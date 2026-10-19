# Chrome UAF漏洞模式浅析（三）：unique key容器emplace重复key

阅读量 **272113**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-08 14:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f3390ae30c31598a.jpg)

## 前序

本篇提到的可能不是什么特别的漏洞模式，也不专有于chrome，但是因为笔者在做漏洞分析的时候，看过大概四五个一样的漏洞，所以权做分享。

## 指针生命周期管理的一种常用范式

如果所有的B实例，都是在A构造的时候构造出B，B中保存指向A的原始指针，A持有保存B的`unique_ptr`指针。此时当A析构的时候，`unique_ptr
b_`被析构，于是b_保存的指向B的原始指针也被析构，从而B被析构。

    
    
    class B;
    
    class A {
    public:
        A() {
            printf("A构造\n");
            b_ = std::make_unique<B>(this);
        }
        ~A(){
            printf("A析构\n");
        }
        std::unique_ptr<B> b_;
    };
    
    class B {
    public:
        B(A *a) {
            printf("B构造\n");
            a_ = a;
        }
        ~B(){
            printf("B析构\n");
        }
        A *a_;
    };
    
    int main(){
        A* a = new A();
        delete a;
        pause();
    }
    ...
    ...
    A构造
    B构造
    A析构
    B析构
    

## 漏洞分析

###  例子1: CVE-2019-5788

<https://bugs.chromium.org/p/chromium/issues/detail?id=925864>

一般比较常见的生命周期管理就是让类A的对象通过容器C去保存类B的对象的指针，从而统一的进行B类型对象的删除。

如下FileSystemOperationRunner通过`operations_`字段来管理所有被创建出来的FileSystemOperation对象。

`operations_`就是`map<id,
unique_ptr<FileSystemOperation>>`，它会保存FileSystemOperation的一个unique_ptr指针。

    
    
    OperationID FileSystemOperationRunner::BeginOperation(
        std::unique_ptr<FileSystemOperation> operation) {
      OperationID id = next_operation_id_++;
    
      // TODO( https://crbug.com/864351 ): Diagnostic to determine whether OperationID
      // wrap-around is occurring in the wild.
      DCHECK(operations_.find(id) == operations_.end());
    
      // ! If id already in operations_, this will free operation
      operations_.emplace(id, std::move(operation));
      return id;
    }
    

如下:
在FileSystemOperation对象为了进行生命周期的管理，将其`unique_ptr`指针被map保存，然后又使用其原始指针调用Truncate方法。

    
    
    OperationID FileSystemOperationRunner::Truncate(const FileSystemURL& url,
                                                    int64_t length,
                                                    StatusCallback callback) {
      base::File::Error error = base::File::FILE_OK;
      std::unique_ptr<FileSystemOperation> operation = base::WrapUnique(
          file_system_context_->CreateFileSystemOperation(url, &error));
      // ! take a raw pointer to the contents of the unique_ptr
      FileSystemOperation* operation_raw = operation.get();
      // ! call BeginOperation passing the move'd unique_ptr, freeing operation
      OperationID id = BeginOperation(std::move(operation));
      base::AutoReset<bool> beginning(&is_beginning_operation_, true);
      if (!operation_raw) {
        DidFinish(id, std::move(callback), error);
        return id;
      }
      PrepareForWrite(id, url);
      // ! use the raw free'd pointer here.
      operation_raw->Truncate(url, length,
                              base::BindOnce(&FileSystemOperationRunner::DidFinish,
                                             weak_ptr_, id, std::move(callback)));
      return id;
    }
    

这里有一个问题就是，OperationID是一个int类型的值，如果emplace的时候，该值因为装入的operation过多，而溢出，则可能导致用之前已经装入map的id，再次放入一个operation。  
即

    
    
    operations_.emplace(idA, std::move(op1));
    operations_.emplace(idA, std::move(op2));
    

在第二次装入的时候，因为`operations_`是一个unique_key的容器，它不允许key相同，所以第二次装入是失败的，op2这个`unique_ptr`被当场析构，且此时它里面保存的原始指针不为空，从而使得指针指向的FileSystemOperation也被析构，operation_raw变成悬空指针。

之后通过`operation_raw`调用的时候，就UAF了。

漏洞补丁就是加固了OperationID的范围，避免溢出。

    
    
       using CopyOrMoveOption = FileSystemOperation::CopyOrMoveOption;
       using GetMetadataField = FileSystemOperation::GetMetadataField;
    
    -  using OperationID = int;
    +  using OperationID = uint64_t;
    
       virtual ~FileSystemOperationRunner();
    

###  例子2: CVE-2020-6493

  * issue url 
    * <https://bugs.chromium.org/p/chromium/issues/detail?id=1082105>
  * poc 
    
        var i=0;
    setInterval(function(){
    i++;
    console.log(i)
    virtualAuthenticatorManager.createAuthenticator().then(() => {
      return navigator.credentials.create({publicKey : customPublicKey});
    });
    },0.1)
    

`navigator.credentials.create`最终会调到AuthenticatorAdded，用来添加一个新的authentication设备

    
        void FidoRequestHandlerBase::AuthenticatorAdded(
      FidoDiscoveryBase* discovery,
      FidoAuthenticator* authenticator) {
    DCHECK(authenticator &&
           !base::Contains(active_authenticators(), authenticator->GetId()));
    auto authenticator_state =
        std::make_unique<AuthenticatorState>(authenticator);
    auto* weak_authenticator_state = authenticator_state.get();
    active_authenticators_.emplace(authenticator->GetId(),
                                   std::move(authenticator_state));
    //...
    }
    

注意到`active_authenticators_`是一个AuthenticatorMap.

    
        using AuthenticatorMap =
      std::map<std::string, std::unique_ptr<AuthenticatorState>, std::less<>>;
    

如果在向`active_authenticators_`里插入元素的时候，发生了key冲突，就会导致要插入的`unique_ptr
authenticator_state`立刻析构掉它保存的AuthenticatorState对象的原始指针(其实是先进行一个右值拷贝给栈上的临时对象，然后临时对象因为插入失败，在函数结束的时候就析构掉了)，测试样例如下:

    
    
    class A{
    public:
        A(){
            cout << "A 构造"<<endl;
        }
        ~A(){
            cout << "A 析构"<<endl;
        }
    };
    
    using AMap = std::map<std::string, std::unique_ptr<A>, std::less<>>;
    AMap ua_m;
    void f(){
        auto ua1 = std::make_unique<A>();
        std::string ua1_id = "1";
        auto ua2 = std::make_unique<A>();
        std::string ua2_id = "1";
        ua_m.emplace(ua1_id, std::move(ua1));
        ua_m.emplace(ua2_id, std::move(ua2));
        cout << "done1" << endl;
    }
    int main(){
        f();
        cout << "done2" <<endl;
    }
    ...
    ...
    A 构造
    A 构造
    done1
    A 析构
    

插入失败之后，我们将被析构掉的对象的原始指针`weak_authenticator_state`作为`FidoRequestHandlerBase::InitializeAuthenticatorAndDispatchRequest`的参数绑定成一个callback，并PostTask到当前线程的消息队列里，等待执行，当消息循环取出这个callback并执行的时候，就会在`InitializeAuthenticatorAndDispatchRequest`里触发UAF。

    
    
    void FidoRequestHandlerBase::InitializeAuthenticatorAndDispatchRequest(
        AuthenticatorState* authenticator_state) {
      authenticator_state->timer = std::make_unique<base::ElapsedTimer>();
      authenticator_state->authenticator->InitializeAuthenticator(base::BindOnce(
          &FidoRequestHandlerBase::DispatchRequest, weak_factory_.GetWeakPtr(),
          authenticator_state->authenticator));//<--解引用被析构的authenticator_state
    }
    

## 模式总结

要找到这样的漏洞，要满足几个条件  
1 找到向map或者其他unique key容器里进行insert/emplace的点  
2 在插入的时候，key是否是可重复的，要么可控制，要么可爆破随机数，要么可溢出。  
3
emplace进行析构的地方，和使用被析构对象的原始指针的地方，不能在同一个函数里（因为我们的测试证明要emplace所在函数结束才真正析构），要么是在外层函数，要么是将raw
pointer传入其他函数进行回调。

## 后记

本系列至此暂时告一段落，本来还想写一篇RenderFrameHost生命周期相关的漏洞模式，但是因为之前写过了很详细的分析，感兴趣的师傅可以找一下我以前发的文章。  
本系列涉及到的漏洞多是一年前的漏洞了，Chrome的安全性是快速迭代的，所以现在的Chrome
UAF漏洞挖掘往往需要组合多个点，以及对对象的生命周期关系做一个比较明确的分析图。  
希望本篇能给师傅们一些启发 : )

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sakura** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231414](/post/id/231414)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞挖掘](/tag/漏洞挖掘)
  * [Chrome](/tag/Chrome)
  * [双倍活动](/tag/双倍活动)

 **+1** __4赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/44110799D419F015C1D87EF97B55B122/40)
sakura

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

