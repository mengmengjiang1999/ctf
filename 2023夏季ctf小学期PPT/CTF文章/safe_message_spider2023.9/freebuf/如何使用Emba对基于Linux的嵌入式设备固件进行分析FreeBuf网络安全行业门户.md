![](https://image.3001.net/images/20210210/1612953573_6023b7e596199a5f2f1d7.png!small)

## 写在前面的话

Emba是一款针对基于Linux的嵌入式设备固件的分析工具，本质上来说，Emba是一款固件扫描器，可以帮助广大研究人员分析基于Linux的已提取出来的固件镜像。在该工具的帮助下，我们可以轻松识别并分析大体积固件镜像中有意思的部分。虽然Emba支持离线固件镜像，但它可以同时对实时系统或已提取镜像进行分析。除此之外，Emba还可以分析内核配置，其主要功能其实也是为渗透测试人员所设计的。该工具需要研究人员与之交互，并且能够
尽可能多地给研究人员提供关于目标固件的任何信息。测试人员可以自行决定需要重点关注的镜像区域，并对分析结果进行解释和验证。

![](https://image.3001.net/images/20210210/1612953585_6023b7f16d21f72d1316e.png!small)

## 工具依赖组件

    
    
    readelf
    
    find
    
    grep
    
    modinfo
    
    realpath
    
    sed
    
    cut
    
    sort
    
    basename
    
    strings
    
    bc
    
    netstat
    
    可选: tree
    
    可选: shellcheck
    
    可选: docker
    
    可选: docker-compose
    
    可选: yara
    
    可选: qemu
    
    可选: binwalk
    
    可选: cve-search
    
    可选: cve-searchsploit

如需检测这些依赖组件，可运行下列命令：

    
    
    sudo ./emba.sh -d

如需安装所有的依赖组件，可以运行下列命令：

    
    
    sudo ./installer.sh

## 工具使用

在开始之前，我们需要检测主机是否已经安装并配置好了Emba运行所需的全部依赖组件，并使用installer.sh脚本进行安装。

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/e-m-b-a/emba.git

接下来，运行安装脚本：

    
    
    sudo ./installer.sh

安装好之后，我们就可以使用下列命令来运行Emba了：

    
    
    sudo ./emba.sh

## 可选参数

    
    
    Test firmware / live system
    
    -a [MIPS]         Architecture of the linux firmware [MIPS, ARM, x86, x64, PPC]
    
    -A [MIPS]         Force Architecture of the linux firmware [MIPS, ARM, x86, x64, PPC] (disable architecture check)
    
    -l [./path]       Log path
    
    -f [./path]       Firmware path
    
    -e [./path]       Exclude paths from testing (multiple usage possible)
    
    -m [MODULE_NO.]   Test only with set modules [e.g. -m p05 -m s10 ... ]]
    
                      (multiple usage possible, case insensitive, final modules aren't selectable, if firmware isn't a binary, the p modules won't run)
    
    -c                Enable cwe-checker
    
    -g                Create grep-able log file in [log_path]/fw_grep.log
    
                      Schematic: MESSAGE_TYPE;MODULE_NUMBER;SUB_MODULE_NUMBER;MESSAGE
    
    -E                Enable automated qemu emulation tests (WARNING this module could harm your host!)
    
    -D                Run emba in docker container
    
    -i                Ignore log path check
    
     
    
    Dependency check
    
    -d                Only check dependencies
    
    -F                Check dependencies but ignore errors
    
     
    
    Special tests
    
    -k [./config]     Kernel config path
    
     
    
    Modify output
    
    -s                Print only relative paths
    
    -z                Add ANSI color codes to log
    
     
    
    Firmware details
    
    -X [version]      Firmware version (double quote your input)
    
    -Y [vendor]       Firmware vendor (double quote your input)
    
    -Z [device]       Device (double quote your input)
    
    -N [notes]        Testing notes (double quote your input)
    
     
    
    Help
    
    -h                Print this help message

## Docker容器

工具还提供了一个简单的Docker-Compose安装来帮助我们在一个Docker容器中运行Emba。接下来，我们需要按照下列方式在Docker中手动运行Docker。

 **构建：**

    
    
    docker-compose build emba

 **运行：**

    
    
    sudo ./emba.sh -l ./logs/path_log -f ./firmware/path_firmware/ -D

 **运行交互式Docker容器：**

    
    
    FIRMWARE=/absolute/path/to/firmware LOG=/home/n/firmware_log/ docker-compose run emba

 **我们还可以使用-D选项切换Emba的Docker模式：**

    
    
    sudo ./emba.sh -z -s -l ./logs_docker_test1 -f /home/m1k3/git-repos/testimages/testimages/testimages/MIPS_router -E -D

## 工具使用样例

### 静态固件测试：

> 从上传文件或闪存中使用binwalk提取固件；
>
> 使用下列命令执行Emba：
    
    
    sudo ./emba.sh -l ./logs/arm_test -f ./firmware/arm_firmware/

![](https://image.3001.net/images/20210210/1612953752_6023b8981ef03243f4693.png!small)

### 测试内核配置：

    
    
    sudo ./emba.sh -l ./logs/kernel_conf -k ./kernel.config

## 许可证协议

本项目的开发与发布遵循GPL v3.0开源许可证协议。

## 项目地址

Emba：【[ _GitHub传送门_](https://github.com/e-m-b-a/emba)】

