注：此次环境搭建使用的系统是最新版kali2022，从官网下载直接导入虚拟机，按下图操作即可，不会出什么问题

这里使用的默认的kali官方源，如有需要也可以换，不过我这里测试的是默认源，没有出一点问题

### kali

    
    
    https://www.kali.org/get-kali/#kali-virtual-machines

### GDB

kali2022默认是不带gdb的，需要安装

    
    
    sudo apt update  
    sudo apt install gdb

### pwndbg

    
    
    git clone https://github.com/pwndbg/pwndbg  
    cd pwndbg  
    sudo ./setup.sh  
    ​  
    cp /root/.gdbinit /home/zhou/.gdbinit  
    sudo cp /root/.gdbinit /home/kali/.gdbinit  
    gdb  
    在安装pwndbg会自动安装pwntools

### ROPgadget

    
    
    git clone https://github.com/JonathanSalwan/ROPgadget.git  
    cd ROPgadget  
    sudo python setup.py develop

### LibcSearcher

    
    
    git clone https://github.com/lieanu/LibcSearcher.git  
    cd LibcSearcher  
    sudo python3 setup.py develop

测试：

    
    
    from LibcSearcher import * #执行这句话没有报错即可

### one_gatget

    
    
    sudo apt install ruby  
    sudo apt install gem  
    sudo gem install one_gadget

### vscode

    
    
    下载deb安装包  
    sudo dpkg -i 本地安装包路径

### checksec

    
    
    git clone https://github.com/slimm609/checksec.sh  
    env | grep "^PATH"  
    sudo cp checksec /usr/local/bin/

### 换源

    
    
    deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse

ubuntu18默认源

    
    
    #deb cdrom:[Ubuntu 18.04.6 LTS _Bionic Beaver_ - Release amd64 (20210915)]/ bionic main restricted  
    ​  
    # See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to  
    # newer versions of the distribution.  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic main restricted  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic main restricted  
    ​  
    ## Major bug fix updates produced after the final release of the  
    ## distribution.  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic-updates main restricted  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic-updates main restricted  
    ​  
    ## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu  
    ## team. Also, please note that software in universe WILL NOT receive any  
    ## review or updates from the Ubuntu security team.  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic universe  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic universe  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic-updates universe  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic-updates universe  
    ​  
    ## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu   
    ## team, and may not be under a free licence. Please satisfy yourself as to   
    ## your rights to use the software. Also, please note that software in   
    ## multiverse WILL NOT receive any review or updates from the Ubuntu  
    ## security team.  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic multiverse  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic multiverse  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic-updates multiverse  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic-updates multiverse  
    ​  
    ## N.B. software from this repository may not have been tested as  
    ## extensively as that contained in the main release, although it includes  
    ## newer versions of some applications which may provide useful features.  
    ## Also, please note that software in backports WILL NOT receive any review  
    ## or updates from the Ubuntu security team.  
    deb http://cn.archive.ubuntu.com/ubuntu/ bionic-backports main restricted universe multiverse  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ bionic-backports main restricted universe multiverse  
    ​  
    ## Uncomment the following two lines to add software from Canonical's  
    ## 'partner' repository.  
    ## This software is not part of Ubuntu, but is offered by Canonical and the  
    ## respective vendors as a service to Ubuntu users.  
    # deb http://archive.canonical.com/ubuntu bionic partner  
    # deb-src http://archive.canonical.com/ubuntu bionic partner  
    ​  
    deb http://security.ubuntu.com/ubuntu bionic-security main restricted  
    # deb-src http://security.ubuntu.com/ubuntu bionic-security main restricted  
    deb http://security.ubuntu.com/ubuntu bionic-security universe  
    # deb-src http://security.ubuntu.com/ubuntu bionic-security universe  
    deb http://security.ubuntu.com/ubuntu bionic-security multiverse  
    # deb-src http://security.ubuntu.com/ubuntu bionic-security multiverse

ubuntu16默认源

    
    
    #deb cdrom:[Ubuntu 16.04.7 LTS _Xenial Xerus_ - Release amd64 (20200806)]/ xenial main restricted  
    ​  
    # See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to  
    # newer versions of the distribution.  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial main restricted  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial main restricted  
    ​  
    ## Major bug fix updates produced after the final release of the  
    ## distribution.  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates main restricted  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial-updates main restricted  
    ​  
    ## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu  
    ## team. Also, please note that software in universe WILL NOT receive any  
    ## review or updates from the Ubuntu security team.  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial universe  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial universe  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates universe  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial-updates universe  
    ​  
    ## N.B. software from this repository is ENTIRELY UNSUPPORTaED by the Ubuntu   
    ## team, and may not be under a free licence. Please satisfy yourself as to   
    ## your rights to use the software. Also, please note that software in   
    ## multiverse WILL NOT receive any review or updates from the Ubuntu  
    ## security team.  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial multiverse  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial multiverse  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial-updates multiverse  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial-updates multiverse  
    ​  
    ## N.B. software from this repository may not have been tested as  
    ## extensively as that contained in the main release, although it includes  
    ## newer versions of some applications which may provide useful features.  
    ## Also, please note that software in backports WILL NOT receive any review  
    ## or updates from the Ubuntu security team.  
    deb http://cn.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse  
    # deb-src http://cn.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse  
    ​  
    ## Uncomment the following two lines to add software from Canonical's  
    ## 'partner' repository.  
    ## This software is not part of Ubuntu, but is offered by Canonical and the  
    ## respective vendors as a service to Ubuntu users.  
    # deb http://archive.canonical.com/ubuntu xenial partner  
    # deb-src http://archive.canonical.com/ubuntu xenial partner  
    ​  
    deb http://security.ubuntu.com/ubuntu xenial-security main restricted  
    # deb-src http://security.ubuntu.com/ubuntu xenial-security main restricted  
    deb http://security.ubuntu.com/ubuntu xenial-security universe  
    # deb-src http://security.ubuntu.com/ubuntu xenial-security universe  
    deb http://security.ubuntu.com/ubuntu xenial-security multiverse  
    # deb-src http://security.ubuntu.com/ubuntu xenial-security multiverse

