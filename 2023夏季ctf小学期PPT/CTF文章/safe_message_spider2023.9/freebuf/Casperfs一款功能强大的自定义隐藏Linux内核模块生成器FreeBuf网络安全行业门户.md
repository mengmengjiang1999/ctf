![](https://image.3001.net/images/20220404/1649063259_624ab55b376759b201093.jpeg!small)

## 关于Casper-fs

Casper-fs是一款功能强大的自定义隐藏Linux内核模块生成器，其中的每一个模块都可以在文件系统中工作并利用系统资源，然后根据YAML规则文件总的自定义规则列表来保护和隐藏各种敏感文件。

值得一提的是，即使你有root权限，你也无法查看、访问、编辑、修改和删除受到Casper-fs所保护的文件。只有当用户向自定义设备发送了正确的密钥以释放文件系统中的操作时，才能查看、编辑和删除文件。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CoolerVoid/casper-fs.git

## 工具使用

### 准备工作

首先，我们需要运行下列命令来验证内核版本是否为3.x、4.x或5.x：

    
    
    $ uname -r

接下来，进入项目目录中，然后安装Python 3模块：

    
    
    $ cd casper-fs/module_generator
    
    $ sudo python3 -m pip install -r requirements.txt

然后编辑“module_generator/rules/fs-rules.yaml”文件中的YAML规则，Python脚本会使用这个文件来生成一个新的Casper-fs自定义模块：

    
    
    $ cat module_generator/rules/fs-rules.yaml
    
    binary_name: casperfs
    
    module_name: Casperfs
    
    unhide_module_key: AbraKadabra
    
    hide_module_key: Shazam
    
    fake_device_name: usb15
    
    unhide-hide-file-key: Alakazam
    
    unprotect-protect-file-key: Sesame
    
    fs-rules:
    
    - hidden:
    
       1: secret.txt
    
       2: my_vault.db
    
    - protect:
    
       1: backup_httpd.log

我们可以在文件的上下文插入大量需要保护和隐藏的元素，比如说：

    
    
    - protect:
    
       1: backup_httpd.log
    
       2: secret_img.iso
    
       3: secret_file.img
    
       4: secret_file2.img
    
       5: secret_file3.img

如果你想要了解静态代码相关的生成方法，可以查看项目中“templates”目录下的内容。

### 生成模块

如果你向按照YAML文件规则来生成一个内核模块的话，可以直接运行下列命令：

    
    
    $ python3 casper-fs-gen.py --rules rules/fs-rules.yaml

上述代码将使用fs-rules.yaml来生成一个通用模块。

### 安装模块

如果你使用的是Fedora Linux，可以使用下列命令为开发人员安装内核包：

    
    
    # dnf update
    
    # dnf install kernel-headers.x86_64 kernel-modules.x86_64 kernel.x86_64 kernel-devel kmod

Ubuntu Linux安装方式如下：

    
    
    apt install linux-headers-generic gcc make

下列命令可以测试模块功能：

    
    
    # cd output; make clean; make
    
    # insmod casperfs.ko

### 运行自定义模块

> 针对lsmod的casper-fs模块可见操作密码为“Shazam”；
>
> 将casper-fs改为不可见的操作密码为“AbraKadabra”；
>
> 将敏感文件隐藏的操作密码为“Alakazam”，改为显示的操作密码也是“Alakazam”；
>
> 文件的保护和解保护操作密码为“Sesame”；

我们需要向目标设备发送密码（例如“usb15”）来测试文件系统中的隐藏和解隐藏资源：

    
    
    $ touch secret.txt
    
    $ ls
    
    -- no results--    
    $ echo "Alakazam" > /dev/usb15
    
    $ ls
    
    secret.txt
    
    $ echo "Alakazam" > /dev/usb15
    
    $ ls
    
    -- no results--
## 工具使用样例

下列样例中，我们将尝试删除受Casper-fs保护的文件。注意，我们需要使用lsmod命令将Casper-fs调整为可见，因此需要先执行下列操作：

    
    
    # ls
    
    test.txt  log.txt backup_httpd.log
    
    # rm backup_httpd.log
    
    # ls
    
    test.txt  log.txt backup_httpd.log
    
    # echo "Sesame" > /dev/usb15            // to remove protection
    
    # rm backup_httpd.log
    
    # ls
    
    test.txt  log.txt
    
    # echo "Sesame" > /dev/usb15    // to active protection again

然后才可以执行删除操作：

    
    
    # rmmod casperfs
    
    rmmod: ERROR: ../libkmod/libkmod-module.c:799 kmod_module_remove_module() could not remove 'casperfs': No such file or directory
    
    rmmod: ERROR: could not remove module casperfs: No such file or directory
    
    # lsmod | grep casper
    
    # echo "Shazam" > /dev/usb15
    
    # lsmod | grep casper
    
    casperfs
    
    # rmmod casperfs

## 工具运行截图

![](https://image.3001.net/images/20220404/1649063500_624ab64c3d5763260818d.png!small)

## 工具演示视频

 **视频地址：** _https://www.you*tube.com/watch?v=qxLEkYFicTg_

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/CoolerVoid/casper-fs/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Casper-fs：** 【[ _GitHub传送门_](https://github.com/CoolerVoid/casper-fs)】

## 参考资料

> [
> _https://en.wiki*pedia.org/wiki/Netfilter_](https://en.wikipedia.org/wiki/Netfilter)
>
> [ _http://lwn.net/Kernel/LDD3/_](http://lwn.net/Kernel/LDD3/)
>
> [
> _https://github.com/m0nad/Diamorphine/_](https://github.com/m0nad/Diamorphine/)

