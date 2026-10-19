**作者：evilpan  
原文链接：<https://evilpan.com/2020/07/11/android-ipc-tips/>**

最近在分析一个运行Android系统的IoT平台，其中包含设备管控和日志服务(Agent)、升级服务(FOTA)、自定义桌面(Launcher)、端上IDS以及前台的图形界面应用等多个前后台进程。在对其中某个功能进行逆向时发现调用链路跨越了多个应用，因此本文就做个简单记录。

# 前言

熟悉安卓开发的同学应该都知道构建IPC的流程，但从逆向工程的角度分析的却比较少见。
说到安卓跨进程通信/调用，就不得不提到AIDL和Binder，在逆向一个东西之前，首先需要了解它，因此本文也会先对其工作流程和工作原理进行介绍。

# AIDL 101

AIDL是Google定义的一个接口定义语言，即Android Interface Definition
Language。两个进程(称为客户端和服务端)共享同一份AIDL文件，并在其基础上实现透明的远程调用。

从开发者的角度如何使用AIDL呢？下面参考[Android的官方文档](https://developer.android.com/guide/components/aidl)以一个实例进行说明。我们的目标是构建一个远程服务FooService，并且提供几个简单的远程调用，首先创建AIDL文件`IFooService.aidl`：

    
    
    package com.evilpan; interface IFooService {    void sayHi();    int add(int lhs, int rhs); } 

AIDL作为一种接口语言，其主要目的一方面是简化创建IPC所需要的IPC代码处理，另一方面也是为了在多语言下进行兼容和适配。使用Android内置的SDK开发工具可将其转换为目标语言，本文以Java为例，命令如下：

    
    
    aidl --lang=java com/evilpan/IFooService.aidl -o . 

生成的文件为`IFooService.java`，文件的内容后面再介绍，其大致结构如下：

    
    
    public interface IFooService extends android.os.IInterface {    /** Default implementation for IFooService. */ public static class Default implements com.evilpan.IFooService  {    // ...  } /** Local-side IPC implementation stub class. */  public static abstract class Stub extends android.os.Binder implements com.evilpan.IFooService  {    // ...  }   public void sayHi() throws android.os.RemoteException;  public int add(int lhs, int rhs) throws android.os.RemoteException; } 

在这个文件的基础上，服务端和客户端分别构造远程通信的代码。

## Server

服务端要做两件事：

  1. 实现AIDL生成的的接口
  2. 创建对应的Service并暴露给调用者

实现接口主要是实现AIDL中的Stub类，如下：

    
    
    package com.evilpan.server; import android.os.RemoteException; import android.util.Log; import com.evilpan.IFooService; public class IFooServiceImpl extends IFooService.Stub {    public static String TAG = "pan_IFooServiceImpl";     @Override    public void sayHi() throws RemoteException {        Log.i(TAG, "Hi from server");    }     @Override    public int add(int lhs, int rhs) throws RemoteException {        Log.i(TAG, "add from server");        return lhs + rhs;    } } 

客户端调用接口需要经过Service，因此我们还要创建对应的服务：

    
    
    package com.evilpan.server; import android.app.Service; import android.content.Intent; import android.os.IBinder; import android.util.Log; public class FooService extends Service {    public static String TAG = "pan_FooService";    private IBinder mBinder;     public FooService() {        Log.i(TAG, "Service init");        mBinder = new IFooServiceImpl();    }     @Override    public IBinder onBind(Intent intent) {        Log.i(TAG, "return IBinder Object");        return mBinder;    } } 

注意这个服务需要在`AndroidManifest.xml`中导出：

    
    
    <service android:name=".FooService"         android:enabled="true"         android:exported="true"/> 

这里的服务与常规服务不同， **不需要** 通过`startService`之类的操作去进行启动，而是让客户端去绑定并启动，因此也称为[Bound
Service](https://developer.android.com/guide/components/bound-services)。客户端绑定成功后拿到的`IBinder`对象(远程对象)就相当于上面`onBind`中返回的对象，客户端中操作本地对象可以实现远程调用的效果。

## Client

客户端在正常调用远程方法之前也需要做两件事：

  1. 实现ServiceConnection接口
  2. bindService

ServiceConnection接口主要是连接远程服务成功的异步回调，示例如下：

    
    
        private ServiceConnection mConnection = new ServiceConnection() {        @Override        public void onServiceConnected(ComponentName name, IBinder service) {            Log.i(TAG, "onServiceConnected");            mService = IFooService.Stub.asInterface(service);             Log.i(TAG, "sayHi");            try {                mService.sayHi();                Log.i(TAG, "add");                mService.add(3 , 4);            } catch (RemoteException e) {                e.printStackTrace();            }        }         @Override        public void onServiceDisconnected(ComponentName name) {            Log.i(TAG, "onServiceDisconnected");        } 

连接成功时会获得一个`IBinder`对象，就是前面说的`IFooService.Stub`实现。我们可以直接通过asInterface将其转换为`IFooService`对象。

`bindService`方法用来将Activity绑定到目标Service上，第一个参数为目标Service的Intent，第二个参数为上面的ServiceConnection实例。

    
    
        @Override    protected void onStart() {        super.onStart();        Log.i(TAG, "onStart");         Intent intent = new Intent();        String pName = "com.evilpan.server";        intent.setClassName(pName, pName + ".FooService");        boolean ret = bindService(intent, mConnection, Context.BIND_AUTO_CREATE);        Log.i(TAG, "bindService: " + ret);    } 

注意这里的包名指定的是服务端的包名，并且类名是服务类而不是AIDL中的接口类。绑定成功后启动客户端进程，可看到ADB日志如下所示：

    
    
    07-11 06:01:25.767  8492  8492 I pan_Client: onCreate 07-11 06:01:25.768  8492  8492 I pan_Client: onStart 07-11 06:01:25.769  8492  8492 I pan_Client: bindService: true 07-11 06:01:25.770  8451  8451 I pan_FooService: Service init 07-11 06:01:25.770  8451  8451 I pan_FooService: return IBinder Object 07-11 06:01:25.785  8492  8492 I pan_Client: onServiceConnected 07-11 06:01:25.785  8492  8492 I pan_Client: sayHi 07-11 06:01:25.785  8451  8463 I pan_IFooServiceImpl: Hi from server 07-11 06:01:25.786  8492  8492 I pan_Client: add 07-11 06:01:25.786  8451  8508 I pan_IFooServiceImpl: add from server 

Server和Client示例文件可见附件。

## 其他

前面我们简单介绍了AIDL的使用，实际上AIDL支持丰富的数据类型，除了int、long、float、String这些常见类型外，还支持在进程间传递`对象`(Parcelable)，以及传递`函数`。在AIDL中定义对象如下：

    
    
    package com.evilpan; parcelable Person { int age; String name; } 

也可以在AIDL中只声明parcelable对象，并在Java文件中自己定义。

而函数也可以看做是一个类型进行传递，例如：

    
    
    package com.evilpan; oneway interface IRemoteServiceCallback { void onAsyncResult(String result); } 

可以把`IRemoteServiceCallback`当做一个类型，在其他的AIDL中使用：

    
    
    package com.evilpan; import com.evilpan.IRemoteServiceCallback; interface IRemoteService { void registerCallback(IRemoteServiceCallback cb); } 

这种模式可以让服务端去调用客户端实现的函数，通常用来返回一些异步的事件或者响应。

# Binder

通过上面的介绍我们知道AIDL实际上只是对boundService接口的一个抽象，而boundService的核心是有一个跨进程的IBinder接口(即上面onBind返回的对象)。实现这个接口有三种方式：

  1. 拓展[Binder](https://developer.android.com/reference/android/os/Binder)类来实现接口
  2. 使用[Messenger](https://developer.android.com/reference/android/os/Messenger)来创建服务的接口，实际上底层也是基于AIDL实现的
  3. 直接使用AIDL

通常实现IPC用得更多的是Messenger，因为其接受的信息是在同一个线程中处理的；直接使用AIDL可能需要多线程的能力从而导致复杂性增加，因此不适合大部分应用。

但不管是AIDL还是Messenger，其本质都是使用了Binder。那么什么是Binder？简单来说Binder是Android系统中的进程间通信(IPC)框架。我们都知道Android是基于Linux内核构建的，而Linux中已经有了许多进程间通信的方法，如：

  * 管道（半双工/全双工）
  * 消息队列
  * 信号量
  * 共享存储
  * socket
  * …

理论上Binder可以基于上面的这些机制实现一套IPC的功能，但实际上Binder自己构建了新的进程间通信方法，这意味着其功能必须要侵入到Linux内核中。为满足商业公司需求而提交patch到Linux
upstream，所受到的阻力可想而知，为什么Google仍然坚持呢？[Brian
Swetland](https://lkml.org/lkml/2009/6/19/254)在Linux邮件组中指出，现有的Linux
IPC机制无法满足以下两个需求：

  1. 通过内核将数据直接到目标地址空间的环形缓冲区，从而减少拷贝开销。
  2. 对可在进程间共享和传递的远程代理对象的生命周期管理。

因此目前Binder在内核中实现为独立的驱动，即`/dev/binder`(后续还进行了细分，如hwbinder、vndbinder)。

除了Binder之外，Android还在Linux的基础上增加了一些其他驱动，比如`Ashmem`、`Low Memory
Killer`等，在内核的`drivers/[staging]/android`目录中。

从驱动的层面看，Binder的使用也很简单：使用`open(2)`系统调用打开`/dev/binder`，然后使用`ioctl(2)`系统调用进行数据传输。以前面的AIDL
IPC为例，其底层的实现如下图所示：

![](https://images.seebug.org/content/images/2020/10/07a8d5cf-400c-4496-b0fb-f94d5d133bea.png-w331s)

# 逆向分析

上面介绍了那么多，但本文不是Binder Internal的文章，不要忘记了我们的目的是逆向。从上面Binder
IPC的流程中可以看到一个很重要的特点，即Binder使用`transact`发送数据，并且在(另一个进程的)`onTransact`回调中接收数据。

大部分逆向工程的工作都是类似的，寻找一种经过编译器处理特定文件后的的模式，并在此基础上构建还原出原始的操作。比如，对于C语言的逆向是通过调用约定以及函数入口/出口对栈的分配/释放来判断函数的调用，对于C++则是通过对vtable的查找/偏移来判断虚函数的调用。

对于我们一开始的目标而言，就是需要分析出系统中存在的进程间调用，更准确地说是需要确定某个进程中函数的交叉引用(xref)。以AIDL为例，`.aidl`文件是不包含在release后的apk文件中的，不过我们还是可以通过生成文件的特征判断这是一个AIDL服务。从生成的代码上来看，主要有这些特点：

  1. 服务端和客户端生成的接口文件是相同的
  2. 生成的主类拓展`android.os.IInterface`，包含AIDL中所定义的函数声明
  3. 主类中包含了自身的 **3个** 实现，分别是默认实现`Default`、本地实现`Stub`以及远程代理实现`Proxy`

一般而言，本地的实现(Stub)需要服务端继承并实现对应方法，Stub同时也拓展Binder类，并在`onTransact`方法中根据code来选择不同的函数进行处理。比如对于前面的例子，有：

    
    
    public static abstract class Stub extends android.os.Binder implements com.evilpan.IFooService {  public boolean onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags) {    // ...    switch (code) {        //...      case TRANSACTION_sayHi:        this.sayHi();     reply.writeNoException();           return true;      case TRANSACTION_add:        int _arg0 = data.readInt();        int _arg1 = data.readInt();        int _result = this.add(_arg0, _arg1);     reply.writeNoException();        reply.writeInt(_result);        return true;      // ...    }  } } 

Proxy即Client端的实现则通过指定transact的code来调用对应远程代码，如下：

    
    
    private static class Proxy implements com.evilpan.IFooService {  private android.os.IBinder mRemote; // ... public void sayHi() throws android.os.RemoteException {    //...    boolean _status = mRemote.transact(Stub.TRANSACTION_sayHi, _data, _reply, 0);    //... } } 

除了生成代码的特征，通常远程调用都会用到 Bound
Service，因此在服务端的`AndroidManifest.xml`文件中必然会有导出的服务声明，这也可以作为分析的一个辅助验证。

# 示例

假设我们正在逆向分析上面编译好的APK，在找到某个关键函数(比如add)后`Find
Usage`发现没有任何交叉引用，但实际上这个函数是被调用了的。那么这就有几种可能，比如这个函数是通过反射调用的，或者这个函数是在native代码中调用的。……当然这里实际上是父类中进行多态调用的，本质是Binder唤起的远程调用。

![](https://images.seebug.org/content/images/2020/10/2fbadbab-5b1b-480b-a174-51428587f384.png-w331s)

跨进程交叉引用的一个前提是需要知道是在哪个进程调用的。如果有权限在Server中进行调试或者代码注入，我们就可以在触发调用或者绑定时使用`Binder.getCallingUid()`函数获取调用者的UID，从而获取Client的包名。

单纯静态分析的话可以把系统中所有相关的进程pull下来，分别反编译后使用grep进行搜索。因为远程调用的接口是共享的，所以即便使用了proguard等混淆也不会影响到接口函数。

# 小结

本文主要是记录下最近遇到的一个Android智能设备的逆向，与以往单个APK不同，这类智能设备中通常以系统为整体，其中包含了多个业务部门内置或者安装的应用，在分析时发现许多应用间跳转和通信的场景。由于NDA的原因没有详细介绍，因此使用了我自己创建的Client/Server作为示例进行说明，但其中的方法都是类似的，即先从正向了解IPC的运行方式，然后通过代码特征去鉴别不同应用间的跳转。对于复杂的系统而言，先理清思路比头铁逆向也更为重要。

# 参考资料

  * [BINDER TRANSACTIONS IN THE BOWELS OF THE LINUX KERNEL](https://www.synacktiv.com/posts/systems/binder-transactions-in-the-bowels-of-the-linux-kernel.html)
  * [BINDER - ANALYSIS AND EXPLOITATION OF CVE-2020-0041](https://www.synacktiv.com/posts/exploit/binder-analysis-and-exploitation-of-cve-2020-0041.html)
  * [Android Binder Framework](https://www.synacktiv.com/posts/exploit/binder-analysis-and-exploitation-of-cve-2020-0041.html)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1364/>

