![](https://image.3001.net/images/20200111/1578737578_5e199faadc52f.jpg!small)

## BetterBackdoor

 **BetterBackdoor是一款多功能的后门工具，广大安全研究人员可以利用BetterBackdoor来获取目标设备的远程访问权限。**

一般来说，后门工具会利用类似NetCat这样的实用工具来实现两大主要功能：使用cmd或bash来实现控制命令的远程传递并接收响应信息。这种方式实现起来很容易，但是也会受到各种因素的限制。而BetterBackdoor成功克服了这种限制，并引入了击键注入、获取屏幕截图、传输文件以及其他的渗透任务。

### 功能介绍

BetterBackdoor可以直接帮助渗透测试人员创建并控制一个后门。

BetterBackdoor创建的后门工具可以实现下列功能：

> 1、运行终端命令行控制指令
>
> 2、运行PowerShell脚本
>
> 3、运行DuckyScripts来注入键盘击键操作
>
> 4、根据文件扩展名来提取文件
>
> 5、提取Microsoft Edge密码以及WiFi密码
>
> 6、向目标设备发送文件或接收目标设备发送过来的文件
>
> 7、开启键盘记录器
>
> 8、获取目标设备的屏幕截图
>
> 9、获取目标设备的剪切板数据
>
> 10、获取目标文件的内容（cat）

BetterBackdoor创建的后门由一个客户端和一个服务器端组成，双方通过套接字链接通信。渗透测试的发起方需要开启一个服务器端，目标设备需要以客户端的形式跟这台服务器建立连接。连接建立成功之后，渗透测试人员就可以从服务器端向目标设备发送控制命令来管理和控制后门程序了。

### BetterBackdoor运行机制

首先，BetterBackdoor会创建一个“run.jar”文件，即后门jar文件，然后将其拷贝到“backdoor”目录中。接下来，将包含有服务器IP地址的文本文件添加进“run.jar”文件中，这里的IP地址是以明文形式写入的。

如果你想的话，你还可以将Java运行时环境拷贝至“backdoor”目录中，然后创建一个批处理文件“run.bat”来在封装的Java运行时环境中运行后门程序。

BetterBackdoor支持在一个单一网络，局域网，或互联网（广域网）下工作。如果你想要在广域网上使用BetterBackdoor，则必须进行端口转发。

若要使用广域网，必须在服务器端主机开启TCP，并使用端口1025和1026来进行端口转发。完成此操作之后，即使目标设备和渗透发起设备位于不同的网络上，渗透测试人员也可以控制后门。

要在目标设备上启动后门，请将“backdoor”目录下的所有文件传输到目标设备中。如果后门文件内封装有JRE环境，那么直接运行run.bat即可，否则请运行run.jar文件。运行完成之后，后门便会在目标设备上启动。

## 工具要求

> 1、Java JDK >= 8
>
> 2、生成后门与控制后门的设备必须是同一台，IP地址必须是保持静态不变的。
>
> 3、控制后门的设备必须关闭本机防火墙，如果在类Unix操作系统下运行的话，则需要使用“sudo”权限来运行BetterBackdoor。

### 兼容性

BetterBackdoor支持在Windows、macOS和Linux平台下运行，但生成的后门程序目前仅支持在Windows平台下工作。

### 工具下载与安装

使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/ThatcherDev/BetterBackdoor.git

切换到项目所在的工作目录：

    
    
    cd BetterBackdoor

使用Maven构建BetterBackdoor，Windows平台请运行下列命令：

    
    
    mvnw.cmd clean package

Linux和macOS环境请运行下列命令完成BetterBackdoor的构建：

    
    
    sh mvnw clean package

### 工具使用

> java -jar betterbackdoor.jar

### 演示视频

> 视频地址：【[ _点我观看_](https://asciinema.org/a/6K0SOY7W8u7ligNoP3s912kwY)】

### 许可证协议

> 本项目的开发与发布遵循[ _MIT开源许可证协议_](https://choosealicense.com/licenses/mit/)。

## 项目地址

BetterBackdoor：【[ _GitHub传送门_](https://github.com/ThatcherDev/BetterBackdoor)】

 *** 参考来源：[
_ThatcherDev_](https://github.com/ThatcherDev/BetterBackdoor)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

