![](https://image.3001.net/images/20190820/1566241182_5d5af19e1331a.png!small)

##  工具介绍

**Objection是一款移动设备运行时漏洞利用工具，该工具由Frida驱动，可以帮助研究人员访问移动端应用程序，并在无需越狱或root操作的情况下对移动端应用程序的安全进行评估检查。**

 **需要注意的是，该工具不涉及到越狱或root绕过，通过使用objection，我们可以很大程度地降低这些安全限制以及沙箱限制。**

##  功能介绍

该工具支持iOS和Android，并且根据真实安全场景增加了很多新的实用工具，下面列出的是该工具的一些核心功能。

Objection针对所有支持的平台，提供了下列核心功能：

> 1、修复iOS和Android应用程序，嵌入了Frida实用工具。
>
> 2、与文件系统交互，枚举条目以及上传/下载的文件。
>
> 3、执行各种内存相关任务，例如列举加载的模块以及相关的输出。
>
> 4、尝试绕过或模拟越狱/root环境。
>
> 5、发现加载的类，并列举对应的方法。
>
> 6、执行常见SSL绑定绕过。
>
> 7、针对目标应用程序，从方法调用中动态导出参数。
>
> 8、与内联SQLite数据库交互，无需下载其他数据库或使用外部工具。
>
> 9、执行自定义Frida脚本。

###  iOS特殊功能：

> 1、导出iOS钥匙串，并存储至文件中。
>
> 2、从常见存储中导出数据，例如NSUserDefaults以及共享NSHTTPCookieStorage。
>
> 3、将信息以可读形式导出。
>
> 4、绕过TouchID限制。
>
> 5、监控类中的所有方法执行。
>
> 6、监控iOS剪贴板。
>
> 7、在无需外部解析工具的情况下，将已编码的.plist文件导出为可读形式。

###  Android特殊功能：

> 1、枚举应用程序的活动、服务和广播接收器。
>
> 2、开启目标应用程序中的任意活动。
>
> 3、监控类方法、报告执行活动。

##  工具运行截图

下列截图显示的是objection的主要功能，测试设备包括一台运行了iOS v10.2.1的iPad和一台运行了Android 6的三星Galaxy
S5，两台设备都运行了测试应用。

###  iOS应用程序主bundle的文件系统：

![](https://image.3001.net/images/20190820/1566241249_5d5af1e187129.png!small)

###  Android应用程序Bundle文件系统：

![](https://image.3001.net/images/20190820/1566241255_5d5af1e7e2ccf.png!small)

###  当前应用程序导出的iOS钥匙串，并将其写入到keychain.json文件中：

![](https://image.3001.net/images/20190820/1566241260_5d5af1ecc943f.png!small)

###  内联SQLite查询工具：

![](https://image.3001.net/images/20190820/1566241266_5d5af1f22b865.png!small)

###  iOS应用程序SSL绑定绕过：

![](https://image.3001.net/images/20190820/1566241272_5d5af1f8c12ec.png!small)

###  Android应用程序SSL绑定绕过：

![](https://image.3001.net/images/20190820/1566241278_5d5af1fe45a1c.png!small)

###  当前存储的iOS sharedHTTPCookieStorage API：

![](https://image.3001.net/images/20190820/1566241283_5d5af2034fddb.png!small)

##  工具使用演示

演示视频：【[点我观看](https://asciinema.org/a/8O6fjDHOdVKgPYeqITHXPp6HV)】

###  工具需求

运行Objection，我们需要用到Python
3解释器，通过pip命令安装即可完成所有的依赖组件安装。针对目标移动端应用程序，iOS需要用到解密的IPA，Android只需要正常的APK文件即可。如果需要对iOS应用程序的源代码进行分析，我们还需要在Xcode项目中加载FridaGadget.dylib。

##  工具安装

广大用户只需要运行下列命令即可完成objection的安装：

    
    
    pip3 install objection

###  工具驱动

![](https://image.3001.net/images/20190820/1566241306_5d5af21a80f38.png!small)

##  许可证协议

Objection遵循[GNU General Public
v3](https://www.gnu.org/licenses/gpl-3.0.en.html)开源许可证协议。

##  项目地址

Objection：【[GitHub传送门](https://github.com/sensepost/objection)】

 ***
参考来源：[sensepost](https://github.com/sensepost/objection)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

