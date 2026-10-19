RXSwift — 使用RxTest 和RxBlocking对Rx代码进行单元测试

[ 沈枫_SerenF](https://www.jianshu.com/u/02d76422b530)关注赞赏支持

# RXSwift — 使用RxTest 和RxBlocking对Rx代码进行单元测试

12

RxTest和RxBlocking属于RxSwift库，需要单独的导入。  
RxTest可测试Rx代码，它包括TestScheduler。  
RxBlocking可以将一个普通的可观察序列转换为一个可观察的阻塞序列，它将阻塞正在运行的线程，直到可观察序列完成或超时为止，让测试异步操作更加容易。

# RxTest

RxTest为测试公开了两种可观察性。

  * HotObservables：不管是否有任何订阅者，HotObservables都会使用测试scheduler在指定的时间重播事件。
  * ColdObservables：ColdObservables的工作方式更像普通的可观察对象，在订阅时将其元素重新播放给新订阅者。

# Schedulers

Schedulers主要用来指定执行队列。  
有如下内置类型：

  * SerialDispatchQueueScheduler：在指定的串行调度队列上调度工作。
  * ConcurrentDispatchQueueScheduler：在并发调度队列上调度工作。
  * OperationQueueScheduler：在指定的NSOperations队列上执行工作。

我们也可以自定义Schedulers，要遵循ImmediateScheduler协议。

常用单例：

  * CurrentThreadScheduler：表示当前线程，是默认的调度器。
  * MainScheduler：表示通常用于所有ui相关工作的主线程。

# Testing with RxBlocking

现在我们进行一个测试。

    
    
    # RxTests 和 RxBlocking 将在单元/集成测试中起到重要作用
    target 'YOUR_TESTING_TARGET' do
        pod 'RxBlocking', '~> 5.0'
        pod 'RxTest', '~> 5.0'
    end
    

第一步，先创建一个10、20和30的可观察序列，如下所示:

    
    
    func testBlocking(){
            let observableToTest = Observable.of(10, 20, 30)
    }
    

第二步，调用toBlocking():

    
    
    let result = observableToTest.toBlocking()
    

toBlocking()将一个常规的可观察序列转变为一个阻塞的可观察序列，如下图所示:

第三步，封装在do catch语句中，添加AssertEquals语句，如下所示:

    
    
    func testBlocking(){
            let observableToTest = Observable.of(10, 20, 30)
            do{
                let result = try observableToTest.toBlocking().first()
                XCTAssertEqual(result, 10)
            } catch {
                XCTFail(error.localizedDescription)
            }
    }
    

第四步，运行测试，可以看到测试通过。

当然，我们也可以通过try!：

    
    
    func testBlocking(){
            let observableToTest = Observable.of(10, 20, 30)
    //        do{
    //            let result = try observableToTest.toBlocking().first()
    //            XCTAssertEqual(result, 10)
    //        } catch {
    //            XCTFail(error.localizedDescription)
    //        }
            XCTAssertEqual(try! observableToTest.toBlocking().first(), 10)
    }
    

为了测试异步操作，我们将再编写一个测试。这一次，我们将在后台线程上使用一个并发调度程序，如下:

    
    
    func testAsynchronousToArry(){
            let scheduler = ConcurrentDispatchQueueScheduler(qos: .background)
    }
    

第一步，创建一个包含简单整数的可观察序列，使用map将每个值加倍，如下所示:

    
    
    let intObservbale = Observable.of(10, 20, 30)
                .map{ $0 * 2 }
    

第二步，订阅scheduler:

    
    
    let intObservbale = Observable.of(10, 20, 30)
                .map{ $0 * 2 }
                .subscribeOn(scheduler)
    

第三步，跟上个测试一样，将其封装到do catch语句中，调用toBlocking，如下:

    
    
    do{
       let result = try intObservbale.observeOn(MainScheduler.instance).toBlocking().toArray()
        } catch {   
        }
    

第四步，添加断言:

    
    
    do{
       let result = try intObservbale.observeOn(MainScheduler.instance).toBlocking().toArray()
                XCTAssertEqual(result, [20, 40, 60])
         } catch {
                XCTFail(error.localizedDescription)
         }
    

第五步，运行，测试通过：

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Retrofit&RxJava](https://www.jianshu.com/p/6caf2b6b02ac)

一、Retrofit详解 ·Retrofit的官网地址为 : http://square.github.io/re...

[余生_d630](https://www.jianshu.com/u/db418f75959f)阅读 1,096评论 0赞 5

  * [RxSwift_v1.0笔记——15 Intro To Schedulers](https://www.jianshu.com/p/cae710c08d83)

RxSwift_v1.0笔记——15 Intro To Schedulers 到目前为止，您已经设法使用了调度程序...

[大灰很](https://www.jianshu.com/u/124d4a5e6432)阅读 257评论 0赞 1

  * [重拾Android之路之探究RX java](https://www.jianshu.com/p/f9db747a92e2)

前言 近这几个月，我也发现国内越来越多的人开始提及 RxJava 。有人说『RxJava 真是太好用了』，有人说『...

[OzanShareing](https://www.jianshu.com/u/225baf5d0de9)阅读 866评论 4赞 18

  * [多线程](https://www.jianshu.com/p/37780d904de3)

一个任务通常就是一个程序，每个运行中的程序就是一个进程。当一个程序运行时，内部可能包含了多个顺序执行流，每个顺...

[OmaiMoon](https://www.jianshu.com/u/11562e9cb771)阅读 1,564评论 0赞 12

  * [0728晨读感悟:告别聚光灯效应，喜欢上自己](https://www.jianshu.com/p/71ffaf7fe1ea)

今天又一次读完剽悍晨读后突然想起自己14岁生日前的周末爸爸带我去江汉路逛街买了一件外套毛衣，一直觉得没有机会穿到学...

[子涵莉](https://www.jianshu.com/u/b160ecf6b7eb)阅读 253评论 0赞 0

 