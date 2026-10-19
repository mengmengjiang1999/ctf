![aaaaa.jpg](https://image.3001.net/images/20190722/1563808441_5d35d2b9c457a.jpg!small)

## The PenTesters Framework (PTF)

 **The PenTesters Framework
(PTF)是一个针对Debian/Ubuntu/ArchLinux开发设计的Python脚本，在PTF的帮助下，研究人员可以根据自己的需要创建一个专用于渗透测试的小型发行版系统平台。作为渗透测试人员，我们通常会有自己习惯使用的工具集或者/pentest/目录，与此同时我们也希望这些工具能够随时保持最新版本。**

PTF会尝试安装所有你需要的渗透测试工具（最新版本），PTF会对这些项目进行编译和构建，并使它们成为在任何设备上都可以安装、更新和分发的工具。PTF还会简化这些工具的安装和打包操作，并为您创建一个完整的渗透测试框架。因为PTF本质上是一个框架，所以我们可以根据自己的需要来进行组建添加以及配置。

## 使用指南

首先请确保config/ptf.config文件中包含了工具及其组件的安装地址根路径，默认情况下，工具的所有组件会安装在/pentest目录中。配置完成之后，请输入命令“./ptf”（或“python
ptf”）运行PTF。

运行之后，你将会看到一个MetaSploitesque风格的Shell界面，我们可以使用“<modules>”来查看可用模块以及所有可接受的命令。当然了，我们还可以使用“help”或“？”来查看完整的命令帮助列表。

### PTF使用视频

视频地址：<https://vimeo.com/137133837>

## 更新所有组件

如果你想要安装或更新所有工具，请直接运行下列命令：

    
    
    ./ptf
    
    use modules/install_update_all
    
    yes

运行之后，将会把所有工具安装进PTF框架中，如果有工具已存在，它将会自动更新这些工具。

比如说：

    
    
    ./ptf
    
    use modules/update_installed

这条命令只会更新你刚刚安装的工具。如果你只想安装漏洞利用工具，你可以运行：

    
    
    ./ptf
    
    use modules/exploitation/install_update_all

这条命令只会安装漏洞利用模块，你还可以用这种方法安装任何类型的模块。

## 定制已安装的工具

你可以通过modules/custom_list/list.py文件来安装你所需要的工具，修改list.py文件后，你可以直接添加你需要安装或更新的工具。输入下列命令：

    
    
    ./ptf
    
    use modules/custom_list/list
    
    yes

此时你可以根据需要来配置模块，并只对特定的工具进行安装和更新操作。

### 模块

首先，进入modules/目录，该目录下会有基于渗透测试执行标准（PTES）划分的子目录，这些子目录中都包含对应的功能模块。当你添加一个新的模块后，比如说testing.py，PTF会在你下次启动PTF时自动加载这个模块。

下面给出的是一个模块样本：

    
    
    AUTHOR="DavidKennedy (ReL1K)"
    
    DESCRIPTION="Thismodule will install/update the Browser Exploitation Framework (BeEF)"
    
    INSTALL_TYPE="GIT"
    
    REPOSITORY_LOCATION="<https://github.com/beefproject/beef>"
    
    X64_LOCATION="<https://github.com/something_thats_x64_instead_of_x86>
    
    INSTALL_LOCATION="beef"
    
    DEBIAN="ruby1.9.3,sqlite3,ruby-sqlite3"
    
    ARCHLINUX= "arch-module,etc"
    
    BYPASS_UPDATE="NO"
    
    AFTER_COMMANDS="cd{INSTALL_LOCATION},ruby install-beef"
    
    LAUNCHER="beef"
    
    TOOL_DEPEND="modules/exploitation/metasploit"

## 模块开发

模块中所有的参数都很简单，我们可以使用GIT、SVN或FILE，然后直接填写依赖项和安装位置即可。PTF将获取Python文件的位置，并将其移动到PTF配置中指定的位置。默认情况下，PTF会将所有工具安装到/pentest/PTES_PHASE/TOOL_FOLDER目录中。

当然了，我们还可以通过设置{PTF_LOCATION}来指定PTF安装路径。

### After_Commands

通过设置After_Commands，我们可以设置工具安装完成后需要执行的命令：

    
    
    AFTER_COMMANDS="cpconfig/dict/rockyou.txt {INSTALL_LOCATION}"

### 自动化命令行

我们还可以通过运行下列命令来自动化更新所有工具组件：

    
    
    ./ptf--update-all

### 无人值守运行

如果我们想要完成PTF的自动构建，我们就可以使用一个heredoc，这样我们就可以不用跟PTF进行交互键入了：

    
    
    ./ptf<<EOF
    
    use modules/exploitation/metasploit
    
    run
    
    use modules/password-recovery/johntheripper
    
    run
    
    EOF

## 项目地址

> ThePenTesters Framework
> (PTF)：【[GitHub传送门](https://github.com/trustedsec/ptf)】

 ***
参考来源：[trustedsec](https://github.com/trustedsec/ptf)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

