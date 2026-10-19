![](https://image.3001.net/images/20220923/1663935469_632da3ed19cdbfae0ed5e.png!small)

## 关于OSRipper

OSRipper是一款功能强大的macOS后门研究与加密框架，在该功能的帮助下，广大研究人员可以通过创建无法检测的后门和信息加密来研究macOS（M1芯片）的安全性。除此之外，该工具还支持在Windows系统上运行，但目前该功能仍在开发阶段。

## 功能介绍

> 1、针对macOS（M1芯片）设计；
>
> 2、可以伪装成官方应用程序，例如微软App或ExpressV*P*N等；
>
> 3、支持导出系统信息、浏览器历史记录、系统登录信息、SSH/AWS/Azure/Gcloud凭证、剪切板内容和本地用户信息；
>
> 4、加密通信；
>
> 5、支持类似Rootkit的功能；
>
> 6、支持Ngrok；

## 工具依赖

该工具基于Python 3开发，因此我们首先需要在设备上安装并配置好Python
3环境。如果你不想下载Python的话，也可以直接下载预编译好的发布版本。该工具所需的Python依赖已在项目的requirements.txt文件中定义。

如果你使用的是v1.4+的版本，你还需要安装MetaSploit，以便处理Meterpreter监听器。

## 工具安装

### Linux安装

    
    
    apt install git python -y
    
    git clone https://github.com/SubGlitch1/OSRipper.git
    
    cd OSRipper
    
    sudo python3 setup.py

### Windows安装

    
    
    git clone https://github.com/SubGlitch1/OSRipper.git
    
    cd OSRipper
    
    sudo python3 setup.py

### 预编译版本下载

广大研究人员还可以直接访问该项目的【[
_Releases页面_](https://github.com/SubGlitch1/OSRipper/releases)】下载预编译好的OSRipper。

## 工具运行

直接在控制台输入下列命令即可执行OSRipper：

    
    
    sudo python3 main.py

## 工具运行截图

![](https://image.3001.net/images/20220923/1663935511_632da4176580ddd9df2f8.png!small)

![](https://image.3001.net/images/20220923/1663935518_632da41e42586b3184e3e.png!small)

## 工具使用演示

在下面的例子中，我们将演示如何使用OSRipper生成后门并加密数据：

![](https://image.3001.net/images/20220923/1663935528_632da4282a2d7c4cf57dc.png!small)

![](https://image.3001.net/images/20220923/1663935534_632da42ee94aef755214c.png!small)

![](https://image.3001.net/images/20220923/1663935541_632da4357dda858504af7.png!small)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **OSRipper** ：【[ _GitHub传送门_](https://github.com/SubGlitch1/OSRipper)】

## 参考资料

> [ _https://github.com/htr-tech/PyObfuscate_](https://github.com/htr-> tech/PyObfuscate)
>
> [
> _https://github.com/cedowens/SwiftBelt_](https://github.com/cedowens/SwiftBelt)

