![](https://image.3001.net/images/20220401/1648824295_62470fe7b2819fbb76d26.jpeg!small)

## 关于Factual-rules-generator

Factual-rules-generator是一款功能强大的开源工具，该工具旨在帮助广大研究人员在目标操作系统平台中生成关于已安装软件的[ __
_YARA规则_](https://github.com/CIRCL/factual-rules)。

该工具能够针对收集或获取到的数字取证数据使用一系列规则以及时找到目标系统中已安装的软件。

Factual-rules-generator可以用于对Windows系统中的已知软件进行基线检查，并创建一组规则，以便在其他系统上查找类似的安装程序。

## 工具架构和执行流

![](https://image.3001.net/images/20220401/1648824305_62470ff1df309ea8cc758.png!small)

## 依赖组件

> pefile
>
> psutil
>
> ndjson
>
> python-tlsh
>
> [
> _PyInstaller_](https://pyinstaller.readthedocs.io/en/stable/)（用来将client.py转换为client.exe）
>
> ssdeep

## ssdeep安装

广大研究人员可以在 _Ubuntu_系统上使用下列命令来安装和配置ssdeep：

    
    
    sudo apt-get install build-essential libffi-dev python3 python3-dev python3-pip libfuzzy-dev
    
    pip install ssdeep

## 工具要求

Factual-rules-generator的正常运行要求主机操作系统中安装好一些依赖组件，其中一部分是Unix标准工具，还有一部分是其他的附加工具：

> xxd
>
> curl

针对Windows虚拟机，还需要安装下列工具组件：

> [ _SDelete_](https://docs.microsoft.com/en-> us/sysinternals/downloads/sdelete)
>
> [ _AsA
> (AttackSurfaceAnalyzer)_](https://github.com/microsoft/AttackSurfaceAnalyzer)

## 工具下载

Factual-rules-generator基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CIRCL/factual-rules-generator.git

安装完成后，还需要requirements.txt中定义的所有Python依赖。

然后，创建一个共享文件夹来跟虚拟机通信。

现在，我们要安装一台Windows虚拟机，并进行下列操作：

> 1、在Windows虚拟机中安装chocolatey；
>
> 2、运行“bin/OnWindows/Varclient.py”；
>
> 3、使用[
> _PyInstaller_](https://pyinstaller.readthedocs.io/en/stable/)将“bin/OnWindows/client.py”转换为可执行文件，并移动到启动目录中；

在项目的test/目录中，已经提供了一些可以用于安装测试的样例程序，广大研究人员可以直接使用。

## 工具运行和生成YARA规则

打开命令行终端，然后运行“bin/Generator.py”脚本，别忘了使用之前先更新“etc/allVariables.py”（关键步骤）。

## 公共YARA规则库

> [ _factual-rules_](https://github.com/CIRCL/factual-rules)：提供一些常见软件的规则样例。

## 许可证协议

本项目的开发与发布遵循[ _AGPL_ _-3.0_](https://github.com/CIRCL/factual-rules-generator/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Factual-rules-generator：** 【[
_GitHub传送门_](https://github.com/CIRCL/factual-rules-generator)】

## 参考资料

> [ _https://github.com/CIRCL/factual-> rules_](https://github.com/CIRCL/factual-rules)
>
> [
> _https://pyinstaller.readthedocs.io/en/stable/_](https://pyinstaller.readthedocs.io/en/stable/)
>
> [ _https://python-ssdeep.readthedocs.io/en/latest/installation.html#install-> on-ubuntu-16-04_](https://python-> ssdeep.readthedocs.io/en/latest/installation.html#install-on-ubuntu-16-04)
>
> [ _https://docs.microsoft.com/en-> us/sysinternals/downloads/sdelete_](https://docs.microsoft.com/en-> us/sysinternals/downloads/sdelete)
>
> [
> _https://github.com/microsoft/AttackSurfaceAnalyzer_](https://github.com/microsoft/AttackSurfaceAnalyzer)
>
> [ _https://docs.chocolatey.org/en-> us/choco/setup_](https://docs.chocolatey.org/en-us/choco/setup)

