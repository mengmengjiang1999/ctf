## 0x00 前言

在枯燥的夏天，突然忍受不了已经使用5年笔记本的风扇声，同时脑子一热。这一刻我知道自己上头了，花了半年的积蓄，买下了一台m1pro芯片14寸的macbook
pro。  
拿到手后，发现确实不错，不仅没有了风扇声，苹果对屏幕和键盘真的非常挑剔，使用感觉非常棒。电池也能抗很久。但是对于偶尔需要打打CTF比赛的菜鸡选手来说，这个笔记本的ARM架构就太不适合玩CTF了。

WEB中的抓包改包似乎没有问题，burp也有对应版本。MISC中的奇奇怪怪的工具似乎也可以在windows中完成。CRYPTO中的算法题，这个mac也可以胜任。逆向和pwn的话，感觉题目的主流还是X86结构的题目，ARM架构的题目毕竟是少数。其中PWN环境的搭建花了我不少功夫。下面主要就是讲讲m1pro芯片下pwn环境的搭建。

## 0x01 pwn环境搭建

#### 2\. 思路1：利用docker，最后可以运行程序，但是不能gdb调试

直接在mac下安装docker,用docker来模拟x86平台。

搭建过程：

直接官网下载docker 网址：https://docs.docker.com/desktop/mac/apple-silicon/
安装完成后，找一个适合的pwn的docker，我找的是https://github.com/skysider/pwndocker

    
    
    git clone https://github.com/skysider/pwndocker
    docker-compose up -d
    docker exec -it pwn_test /bin/bash
    docker-compose down 
    docker run -d \
        --rm  \
        -h $1 \
        --name $1 \
        -v $(pwd)/$1:/ctf/work \
        -p 23946:23946 \
        --privileged  \
        --cap-add=SYS_PTRACE \
        --security-opt seccomp=unconfined \
        --platform linux/amd64  \         # 这个需要指定amd64架构来运行docker
        --security-opt apparmor=unconfined \
        skysider/pwndocker
    #运行成功后查看docker 进程
    docker ps
    CONTAINER ID   IMAGE   COMMAND         CREATED         STATUS         PORTS    NAMES
    56bf6ed39229   skysider/pwndocker   "/sbin/my_init"   6 seconds ago   Up 5 seconds   0.0.0.0:23946->23946/tcp   peaceful_curie
    

进入docker后发现可以运行程序，但是不能使用gdb

    
    
    docker exec -it --privileged peaceful_curie  /bin/bash
    root@--name:/ctf/work# 
    root@--name:/ctf/work# gdb level0
    GNU gdb (Ubuntu 9.2-0ubuntu1~20.04) 9.2
    Copyright (C) 2020 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
    Type "show copying" and "show warranty" for details.
    This GDB was configured as "x86_64-linux-gnu".
    Type "show configuration" for configuration details.
    For bug reporting instructions, please see:
    <http://www.gnu.org/software/gdb/bugs/>.
    Find the GDB manual and other documentation resources online at:
        <http://www.gnu.org/software/gdb/documentation/>.
    
    For help, type "help".
    Type "apropos word" to search for commands related to "word"...
    pwndbg: loaded 195 commands. Type pwndbg [filter] for a list.
    pwndbg: created $rebase, $ida gdb functions (can be used with print/break)
    Reading symbols from level0...
    (No debugging symbols found in level0)
    pwndbg> b *main
    Breakpoint 1 at 0x4005c6
    pwndbg> r
    Starting program: /ctf/work/level0 
    warning: Could not trace the inferior process.
    warning: ptrace: Function not implemented
    During startup program exited with code 127.
    

这个问题网上查了很久，并没有一个好的解决方案，可以查看docker中的运行状态。

    
    
    root@--name:/ctf/work# ps -ef
    UID        PID  PPID  C STIME TTY          TIME CMD
    root       143    81  0 08:49 pts/0    00:00:00 /usr/bin/qemu-x86_64 ./level0 ./
    

可以看到docker中的所有进程都是通过qemu虚拟化出来的。那就有个思路，为何不直接通过qemu中的gdb选项来进行调试呢。

#### 2\. 思路2: 利用qemu模拟x86程序，然后通过gdb进行连接，进行调试。

在mac下进行gdb调试有坑，所以我在ubuntu arm下进行。至于如何在mac下搭建arm版的ubuntu，就请自己解决了，网上的解决方案很多。  
搭建qemu及gdb：

  1. 安装依赖库

    
    
    sudo apt install make
    sudo apt install gcc
    sudo apt install g++
    sudo apt install libglib2.0-dev
    sudo apt install libpixman-1-dev
    sudo apt install libfdt-dev
    git clone https://github.com/ninja-build/ninja.git 
    cd ninja
    ./configure.py --bootstrap
    sudo apt install gcc-x86-64-linux-gnu
    

  2. 安装qemu

    
    
    git clone https://github.com/qemu/qemu.git
    mkdir build
    cd build
    ../configure       #这里默认编译所有平台，可以通过target-list参数指定特定平台，例如--target-list=x86_64-softmmu,x86_64-linux-user
    make
    

  3. 安装gdb

    
    
    sudo apt install gdb
    sudo apt install gdb-multiarch
    

  4. 安装pwndbg

    
    
    git clone https://github.com/pwndbg/pwndbg
    cd pwndbg
    vim requirements.txt  #删除带有unicorn的行
    ./setup.sh
    

  5. 自己编译unicorn（选做，不影响gdb调试）

  6. 安装pwntools

    
    
    sudo pip3 install pwntools
    

## 0x02 调试x86程序

  1. 利用qemu运行程序

    
    
    #build后的路径加入$PATH中，这样方便调用
    vim ~/.bashrc 
    export PATH=$PATH:/home/parallels/qemu/build  #这里用自己编译好的路径
    source ~/.bashrc
    qemu-x86_64 -L /usr/x86_64-linux-gnu/ ~/Desktop/level0   #-L后指定libc文件，后面跟二进制文件，可以发现x86程序正常运行
    

![image](https://image.3001.net/images/20220916/1663297456_6323e7b046c3684ed4e11.png!small)

  2. 利用gdb调试qemu运行的程序

    
    
    qemu-x86_64 -L /usr/x86_64-linux-gnu/ -g 12345 ~/Desktop/level0
    

![image](https://image.3001.net/images/20220916/1663297473_6323e7c19ba210e6ba65e.png!small)  
3\. gdb连接调试的程序

    
    
    gdb-multiarch
    set arch i386:x86-64
    target remote 127.0.0.1:12345
    

![image](https://image.3001.net/images/20220916/1663297485_6323e7cd960d62542b799.png!small)  
4\. 设置断点，由于是远程调试，所以程序中的符号表没有添加。需要设置地址  
![image](https://image.3001.net/images/20220916/1663297508_6323e7e4b15b7e01cc35e.png!small)

## 0x03 pwntools工具使用

  1. checksec工具似乎没有任何问题  
![image](https://image.3001.net/images/20220916/1663297523_6323e7f322613d256b12a.png!small)

  2. 脚本运行

    
    
    from pwn import *
    context.arch='amd64'
    context.log_level='debug'
    io = process(["qemu-x86_64","-L","/usr/x86_64-linux-gnu/","./level0"])   #注意这里的变化
    elf = ELF("./level0")
    payload=b'a'*(0x80+0x8)+p64(0x400596)
    io.sendlineafter('\n',payload)
    io.interactive()
    

![image](https://image.3001.net/images/20220916/1663297535_6323e7ff3ad64da244bee.png!small)

## 0x04 后记

至此，简单的栈溢出的pwn题目，就可以通过macbook
m1芯片进行调试，但总觉得比较费事。但是如果是arm架构的pwn题目，就可以直接通过gdb进行调试了，就免去了qemu的模拟。

