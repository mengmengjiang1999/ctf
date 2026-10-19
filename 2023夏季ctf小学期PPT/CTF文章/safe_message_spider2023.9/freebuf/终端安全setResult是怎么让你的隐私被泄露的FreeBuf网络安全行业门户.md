## 1 背景介绍

Android应用间有多种跨进程通信的方式，而setResult便是其中一种相对特殊的方式，用于两个activity之间通信，在通信的过程中，一旦防护出现疏漏，可能导致各种漏洞。setResult相关漏洞最主要是由Intent的错误传递造成，无论是发送方还是接收方，如果出现Intent的错误传递，均可能发生敏感信息泄露、任意文件读写、本地无权限窃取隐私数据、横向移动攻击受保护应用组件等高危危害。

## 2 **原理介绍**

startActivityForResult和setResult这对API各应用使用非常普遍，这里再简单介绍一下。

startActivityForResult(Intent, int) 启动某activity并通过onActivityResult(int, int,
Intent) 方法接收数据。当一个活动退出时，它可以调用 setResult(int)
将数据返回给它的父级activity，它还可以选择返回一个Intent，其中包含通信的任何附加数据。

假设现在有一个Activity A，从Activity A通过startActivityForResult方法启动了Activity B，在Activity
B销毁前，Activity B若将一些数据回传给 Activity A，可以调用setResult方法，这样在Activity B销毁后，Activity
A重新展示时，在Activity A的onActivityResult方法就能够获取 Activity B回传过来的数据。

Activity 回传数据的这个流程，示意如下：

![](https://image.3001.net/images/20230508/1683537275_6458bd7b5e2d8c1d76dd4.png!small)

注意：startActivityForResult已经被废弃，官方推荐使用Activity Result API。

startActivityForResult和setResult这对API通常使用场景，比如权限动态申请、拍照预览、媒体分享、文件访问、联系人选择等等，这也是跨进程通信的一种特殊方式。

但是，setResult你真的用对，用安全了吗？

本文分享setResult可能导致什么样的漏洞。可以看到，一个正常的跳转下一页，一个简单的返回上一页，你的通信录，私人文件，甚至可能是身份证号都已经泄露。

## 案例1 **——窃取身份证**

 **漏洞解析**

某应用需要验证用户身份，有一个身份认证的页面，用户输入个人信息后，认证完成，关闭WebView，再通过setResult回传验证结果；

主要逻辑如下：对象NameValidationWebPresenter，重写了setResultAndFinish方法，完成身份认证后返回结果并关闭页面；

![](https://image.3001.net/images/20230508/1683537431_6458be176e2be8e64fe47.png!small)接下来逻辑进入到isClosed方法，注意nameCheckSuccess方法，这里便是漏洞点所在；

![](https://image.3001.net/images/20230508/1683537447_6458be278d8502a20ff88.png!small)

在nameCheckSuccess方法中，经一系列的判断后，调用对象NameValidationWebPresenter提供的setResultAndFinish方法，而其中的createResultIntent中包含了极其敏感用户信息。

![](https://image.3001.net/images/20230508/1683537477_6458be455dcbf683409cb.png!small)createResultIntent中，可以发现在Intent中存入了诸多用户信息，那么接下来要做的，就是找到入口触发setResultAndFinish，从而获取信息。

![](https://image.3001.net/images/20230508/1683537503_6458be5fd7a74671458ec.png!small)在这个应用，有一个特别的点，无论用户是否进行身份认证，无论成功与否，都会将数据返回，甚至点击任意键返回、切换到桌面或者其他应用、关闭当前页等等，同样会将数据返回，这样恶意应用要实现本地攻击的成功率将大大增加，非常容易实现数据窃取。

 **漏洞利用**

我们简单写个验证应用触发对应组件，接收结果，获取数据；

![](https://image.3001.net/images/20230508/1683537573_6458bea5c996a2792026e.png!small)

这样，触发一个毫不起眼的跳转操作，用户关闭页面或者返回上一页，不知不觉中信息已经被窃取了。

![](https://image.3001.net/images/20230508/1683537597_6458bebdc7b4282e725c4.png!small)

## 案例2—— **读写私有文件**

 **漏洞解析**

这是某应用的Activity在初始化的方法，简单判断Uri后逻辑会进入handleRequestMode和handleResponseResult这两个方法；

![](https://image.3001.net/images/20230508/1683538602_6458c2aa41c2d8c00fe2f.png!small)

注意handleRequestMode和handleResponseResult这两个方法，handleRequestMode中token验证通过，setResult的数据中会携带外部输入的整体Intent。而handleResponseResult中，虽然有非常多的业务逻辑判断，但是无论判断正确与否，都将执行setResult；

![](https://image.3001.net/images/20230508/1683538625_6458c2c1b3d590f3adc65.png!small)

![](https://image.3001.net/images/20230508/1683538644_6458c2d47303590c7a365.png!small)

与第一个案例不同的是，这个案例上，任意三方可以接收到一个完完整整的Intent，中间没有任何修改或重新封装。

 **漏洞利用**

基于AMS的特性，我们构造赋权的Intent，启动受害应用，随后受害应用将恶意Intent返回给了恶意应用，此时恶意应用获取到最原始的恶意Intent，从中取出原始的Uri，因为这样setResult给恶意应用的Intent已经具备了受害应用的特权，恶意应用就可以以受害应用权限执行任意私有文件读写。

攻击流程如下：

![](https://image.3001.net/images/20230508/1683538673_6458c2f1a5a700be940c7.png!small)

## 案例3——窃取电话

 **漏洞解析**

这个案例是某应用通过startActivityForResult与某第三方应用进行数据交换，正常情况下恶意应用是不可能获取到两者之间通信的任何数据的，但是当RequestCode为3的时候，该应用setResult回的数据竟然是恶意应用输入的完整Intent。

![](https://image.3001.net/images/20230508/1683538729_6458c3297da9f4c911e3a.png!small)

这样的操作直接导致了类似第二个案例的问题——任意文件读写，但是这个案例我们分享另外一种利用——利用漏洞应用本身申请的权限。

 **漏洞利用**

由于受害应用本身申请了联系人权限，我们直接利用联系人Uri；这种方式，受害应用申请什么权限，恶意应用就可以获取到什么权限，短信、日历、存储等等。

![](https://image.3001.net/images/20230508/1683538853_6458c3a52cd85c2872b43.png!small)

##  **总结和展望**

看到这儿，setResult你真的用对了吗？应用安全了吗？

普遍使用的API，不代表就是安全的API，越是普遍的API，越需要开发者留心。至于怎么防护，各大规范指导讲得非常详细，这儿简单列下：

  * 将受影响的应用组件设置不导出，不接收来自其他应用的 Intent；

  * 确保提取的 Intent 来自可信的来源：可以使用getCallingActivity等方法来验证源Activity是否可信,只适用startActivityForResult；

  * 确保输入的 Intent 安全：验证输入的 Intent，可以使用 resolveActivity 等方法检查将使用哪个组件来处理该 Intent，或者重写输入Intent。

  * 应用可使用 getFlags 等方法来检查 Intent 是否会授予 URI 权限，或使用Intent#removeFlags移除授权flag。

  * 回传敏感、用户数据假名化或匿名化；

安全防护一定要从基础防护做起，谨防千里之堤毁于蚁穴！！！

