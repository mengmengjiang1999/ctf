**Halcyon是一个开源的专门设计用于开发[Nmap](https://nmap.org/)脚本的IDE。通过Halcyon你可以开发从侦察到利用的各类Nmap高级扫描脚本。如果你想为该项目做出贡献或有任何的改进建议，请访问我们的[contribute](https://halcyon-ide.org/contribute/)页面。**

![HalcyonIDE_Screen1.png](https://image.3001.net/images/20180712/15313581993324.png!small)

## 特性

相比普通的文本编辑器，Halcyon IDE无论是在用户界面以及功能体验上都更胜一筹。Halcyon
IDE提供了一个非常漂亮和友好的用户界面，并且可以在语法和语义上高亮显示源码，使其更易于实际的开发。

> 设计的Nmap侧栏，使开发人员能够更简单轻松地与文件结构进行交互，并可根据脚本要求进行自定义。
>
> 可以在IDE中配置扫描选项（例如脚本参数，数据包跟踪以及其他的一些调试设置），以优化重复的测试运行。
>
> Halcyon IDE提供/允许你运行脚本，以确保代码在导出到Nmap data目录之前没有错误。
>
> 后开发操作，例如将脚本导出到Nmap data目录并更新Nmap数据库。

## 安装

Halcyon IDE是基于java开发的，因此大部分的操作系统都支持运行。你可以[在这里下载Halcyon
jar文件](https://github.com/s4n7h0/Halcyon/releases/download/2.0.1/Halcyon_IDE_v2.0.1.jar)。

此外，你也可以从git下载源码进行安装。

    
    
    # install dependencies 
    apt-get install default-jre
    apt-get install ant
    
    # clone from git
    cd /opt
    git clone https://github.com/s4n7h0/Halcyon.git
    
    # compile the source 
    cd Halcyon/
    ant
    java -cp /opt/Halcyon/src/lib/autocomplete.jar:/opt/Halcyon/src/lib/rsyntaxtextarea.jar:/opt/Halcyon/dist/Halcyon_IDE_v2.0.1.jar halcyon.ide.HalcyonIDE
    

## 配置

Halcyon IDE会使用当前计算机上已安装的Nmap程序文件。第一次运行时，IDE会要求你进行配置。Halcyon
IDE配置向导会自动识别nmap文件，设置完成后需要重启Halcyon IDE才能使设置生效。

## 快速启动

Halcyon IDE是一个jar文件。我们可以通过以下命令来启动它：

    
    
    java -jar Halcyon_IDE_v2.0.1jar
    

## 致谢

最后我要特别致谢[Gordon “Fyodor” Lyon](mailto:fyodor@nmap.org)
以及Nmap项目团队。此外，我还要感谢[Wasim
Halani](https://twitter.com/washalsec)。如果没有他一路以来给予我的支持和鼓励，这个项目也就不会达到现在的水平！谢谢！

***参考来源：[halcyon-ide](https://halcyon-ide.org)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

