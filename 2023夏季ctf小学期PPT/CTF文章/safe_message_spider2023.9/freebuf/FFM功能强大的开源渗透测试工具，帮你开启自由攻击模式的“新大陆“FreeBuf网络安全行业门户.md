![bbbbbbbbbb.jpg](https://image.3001.net/images/20190413/1555166727_5cb1f607e839f.jpg!small)

## Freedom Fighting Mode (FFM)

 **FFM是一款采用Python开发的开源渗透测试工具，广大研究人员可以将FFM用于红队任务的后渗透测试阶段。**

研究人员在[SSTIC
2018](https://www.sstic.org/)大会上正式公布了这款工具，感兴趣的用户可以点击【[这里](http://manalyzer.org/static/talks/SSTIC2018.pptx)】查看当时的工具介绍文稿。

## 工具安装

    
    
    git clone git://github.com/JusticeRage/FFM.git

## 工具使用

该工具的主要目的是为了帮助研究人员自动化实现后渗透利用阶段的常规任务，并通过检测目标环境的安全配置来帮助目标用户增强安全保护等级。

运行“./ffm.py“即可激活FFM，接下来我们就可以开始测试任务了。最常用的两个操作命令如下：

> 1、 输入“!list“命令可查看该工具提供的所有操作命令；
>
> 2、 输入“SHIFT+TAB“命令可在远程主机上实现命令补全；

## 命令列表

1、“!os“：这个命令非常简单，它会执行“cat
/etc/*release*”来查看当前设备运行的操作系统版本，以便研究人员了解目标设备的测试环境。通过SSH连接目标设备后，“!os”命令即可使用，插件位于“commands/replacement_commands.py”。

2、“!download [remotefile] [local
path]”：可以从远程主机中获取文件，并将其通过命令行工具拷贝到本地。这个命令有些复杂，因为它有更严格的错误检查，插件位于“commands/download_file.py”。需要注意的是，远程主机需要xxd或od来保证功能的正常运行。

3、“!upload [local file][remote path]”：这个命令的功能跟上面的那个差不多，只不过它负责的是将本地文件发送到远程主机中。

4、“!pty”：该命令会生成一个TTY，不过大多数情况下不建议使用，因为它会在目标主机上留下“痕迹“。当然，某些命令（例如sudo）还是需要TTY的。

5、“!py [local script]“：该命令可以在远程主机上执行本地Python脚本，而且全部在内存中运行。

研究人员可以通过编辑ffm.conf来对插件进行自定义配置。

### 处理器

上述指令可以生成一些bash命令并将其转发至shell，然后根据shell的输出来生成额外指令并进行更加复杂的操作。其中，当用户输入完数据并按下回车键后，输入处理器便会开始执行；当shell返回处理数据后，输出处理器便会运行。

### 许可证协议

该项目遵循[GPL v3](https://www.gnu.org/licenses/gpl.html)开源许可证协议。

## 工具地址

FFM：【[GitHub传送门](https://github.com/JusticeRage/FFM)】

***参考来源：[JusticeRage](https://github.com/JusticeRage/FFM)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

