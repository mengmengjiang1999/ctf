![](https://image.3001.net/images/20220206/1644143877_61ffa505afb1ebe7a672a.png!small)

## 关于reFlutter

reFlutter是一款功能强大的逆向工程分析工具，该工具主要针对的是Flutter应用程序。该框架使用了已编译且重新封装的Flutter库来帮助广大研究人员对Flutter应用程序进行逆向工程分析。

除此之外，reFlutter框架的代码还修改了快照反序列化进程，以方便研究人员对目标应用程序执行动态分析。

## 功能介绍

> 1、socket.cc可执行流量拦截和监控；
>
> 2、dart.cc支持输出类、函数和某些字段；
>
> 3、方便进行自定义修改或重编译；
>
> 4、支持使用专门的Dockerfile对项目代码进行手动修改；

## 支持的引擎

> Android：ARM64、ARM32；
>
> iOS：ARM64；
>
> 发布版本：稳定版（Stable）、测试版（Beta）；

## 工具安装

适用于Linux、Windows和macOS：

    
    
    pip3 install reflutter

## 工具使用

    
    
    impact@f:~$ reflutter main.apk
    
     
    
    Please enter your Burp Suite IP: <input_ip>
    
     
    
    SnapshotHash: 8ee4ef7a67df9845fba331734198a953
    
    The resulting apk file: ./release.RE.apk
    
    Please sign the apk file
    
     
    
    Configure Burp Suite proxy server to listen on *:8083
    
    Proxy Tab -> Options -> Proxy Listeners -> Edit -> Binding Tab
    
     
    
    Then enable invisible proxying in Request Handling Tab
    
    Support Invisible Proxying -> true
    
     
    
    impact@f:~$ reflutter main.ipa

## 流量拦截

我们需要制定Burp
Suite代理服务器的IP地址，且需要跟运行了目标Flutter应用程序的设备处于同一网络总。接下来，我们还需要配置代理（BurpSuite ->
Listener Proxy -> Options tab）：

> 1、添加端口：8083；
>
> 2、绑定地址：所有接口；
>
> 3、请求处理：支持隐形代理 = True

![](https://image.3001.net/images/20220206/1644143962_61ffa55a224d4b4c01651.png!small)

我们不需要安装任何的证书，在Android设备上我们也不需要root权限。除此之外，reFlutter还允许我们绕过某些Flutter证书绑定实现。

## Android端使用

生成的apk必须对齐并签名，这里我们可以使用[ _uber-apk-signer_](https://github.com/patrickfav/uber-apk-signer/releases/tag/v1.2.1)和下列命令：

    
    
    java -jar uber-apk-signer.jar --allowResign -a release.RE.apk

如果你想使用DartVM来查看哪些代码被加载了，你还需要在设备上运行应用程序，reFlutter会通过logcat和“reflutter”选项来输出结果：

    
    
    impact@f:~$ adb logcat -e reflutter | sed 's/.*DartVM//' >> reflutter.txt

代码输出结果如下：

    
    
    Library:'package:anyapp/navigation/DeepLinkImpl.dart' Class: Navigation extends Object {  
    
     
    
    String* DeepUrl = anyapp://evil.com/ ;
    
     
    
     Function 'Navigation.': constructor. (dynamic, dynamic, dynamic, dynamic) => NavigationInteractor {
    
      
    
                       }
    
        
    
     Function 'initDeepLinkHandle':. (dynamic) => Future<void>* {
    
      
    
                       }
    
        
    
     Function '_navigateDeepLink@547106886':. (dynamic, dynamic, {dynamic navigator}) => void {
    
     
    
                       }
    
     
    
           }
    
     
    
    Library:'package:anyapp/auth/navigation/AuthAccount.dart' Class: AuthAccount extends Account {
    
     
    
    PlainNotificationToken* _instance = sentinel;
    
     
    
     Function 'getAuthToken':. (dynamic, dynamic, dynamic, dynamic) => Future<AccessToken*>* {
    
     
    
                       }
    
      
    
     Function 'checkEmail':. (dynamic, dynamic) => Future<bool*>* {
    
     
    
                       }
    
     
    
     Function 'validateRestoreCode':. (dynamic, dynamic, dynamic) => Future<bool*>* {
    
     
    
                       }
    
     
    
     Function 'sendSmsRestorePassword':. (dynamic, dynamic) => Future<bool*>* {
    
     
    
                       }
    
           }

## iOS端使用

执行“reflutter
main.ipa”命令之后，我们将拿到IPA文件。如果你想使用DartVM来查看哪些代码被加载了，你还需要在设备上运行应用程序，reFlutter会通过XCode和“reflutter”选项来输出结果：

![](https://image.3001.net/images/20220206/1644144037_61ffa5a52862ea8dbce76.png!small)

## 自定义构建

如果你想要实现你自己的代码，reFlutter也支持我们使用专门的[
_Docker_](https://hub.docker.com/r/ptswarm/reflutter)来进行手动代码修改：

    
    
    sudo docker pull ptswarm/reflutter
    
    
    # Linux, Windows
    
    EXAMPLE BUILD ANDROID ARM64:
    
        sudo docker run -e WAIT=300 -e x64=0 -e arm=0 -e HASH_PATCH=<Snapshot_Hash> -e COMMIT=<Engine_commit> --rm -iv${PWD}:/t ptswarm/reflutter
    
     
    
    FLAGS:
    
        -e x64=0                         <disables building for x64 archiitechture, use to reduce building time>
    
        -e arm=0                         <disables building for arm archiitechture, use to reduce building time>
    
        -e WAIT=300                      <the amount of time in seconds you need to edit source code>
    
        -e HASH_PATCH=[Snapshot_Hash]    <here you need to specify snapshot hash which matches the engine_commit line of enginehash.csv table best. It is used for proper patch search in reFlutter and for successfull compilation>
    
        -e COMMIT=[Engine_commit]        <here you specify commit for your engine version, take it from enginehash.csv table or from flutter/engine repo>

## 项目地址

 **reFlutter：** 【[ _GitHub传送门_](https://github.com/ptswarm/reFlutter)】

## 参考资料

[ _https://github.com/patrickfav/uber-apk-signer/releases/tag/v1.2.1_](https://github.com/patrickfav/uber-apk-signer/releases/tag/v1.2.1)

[
_https://github.com/ptswarm/reFlutter/blob/main/.github/workflows/main.yml_](https://github.com/ptswarm/reFlutter/blob/main/.github/workflows/main.yml)

[
_https://github.com/ptswarm/reFlutter/actions_](https://github.com/ptswarm/reFlutter/actions)

[
_https://github.com/ptswarm/reFlutter/blob/main/enginehash.csv_](https://github.com/ptswarm/reFlutter/blob/main/enginehash.csv)

[
_https://hub.docker.com/r/ptswarm/reflutter_](https://hub.docker.com/r/ptswarm/reflutter)

