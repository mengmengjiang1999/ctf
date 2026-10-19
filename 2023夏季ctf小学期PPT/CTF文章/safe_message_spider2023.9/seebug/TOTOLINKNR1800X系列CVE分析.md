**作者：The_Itach1@知道创宇404实验室  
日期：2022年10月25日**

## 漏洞简介

TOTOLINK NR1800X最近报了一些cve，现主要对其命令注入进行具体分析，以及对其登录绕过进行分析。

固件下载地址：<https://www.totolink.net/home/menu/detail/menu_listtpl/download/id/225/ids/36.html>

## 环境搭建

### 固件提取

binwalk提取固件  
`binwalk -Me
TOTOLINK_C834FR-1C_NR1800X_IP04469_MT7621A_SPI_16M256M_V9.1.0u.6279_B20210910_ALL.web`

![](https://images.seebug.org/content/images/2022/10/0cdc80f7-d3d0-4955-b55b-80e2214421b3.png-w331s)

查看文件相关信息，mips架构，小端序，使用mipsel来进行模拟。  
`readelf -h ./bin/busybox`
![](https://images.seebug.org/content/images/2022/10/4c2fa10b-f2da-41b1-a250-13c6e52f9c73.png-w331s)

### 固件模拟

有两种模拟方式，user模式和system模式，感觉根据后面的模拟结果来看，好像差别不是很大。

#### user模式模拟

尝试用qemu模拟

    
    
    cp $(which qemu-mipsel-static) .
    sudo chroot . ./qemu-mipsel-static ./usr/sbin/lighttpd

会报错，显示`No configuration available. Try using -f option.`，这个报错是需要-f指定已有的配置文件。

运行`sudo chroot . ./qemu-mipsel-static ./usr/sbin/lighttpd -f
./lighttp/lighttpd.conf`即可，接着又会报错，说缺少一个文件，创建在对应目录创建一个即可。

    
    
    cd ./var
    mkdir run
    cd run
    touch touch lighttpd.pid

然后运行，可以看到服务启动成功。

![](https://images.seebug.org/content/images/2022/10/68e3a67d-96ee-4f2f-94be-ae0161eab838.png-w331s)

但是这个路由器登录是需要密码的，并且由于是模拟的关系，大部分功能无法正常使用，登录不进去，但是还好经过搜索，发现看雪上有一篇文章讲述了如何进行绕过登录，登录过后，能观察到里面的一些设置，通过bp抓包能分析出一些有效的请求头内容，其数据传输通过json实现。

![](https://images.seebug.org/content/images/2022/10/ee0b1ec5-61de-455e-92d9-004ed6effb30.png-w331s)

![](https://images.seebug.org/content/images/2022/10/13430ed8-50d6-4259-b446-2954623dbc7d.png-w331s)

#### system模拟

user模拟中创建的文件都要有，后面会一起传到quem模拟的虚拟机中。

下载qemu启动虚拟机所需要的“镜像”，这是小端序，所以去下载mipsel的镜像。

    
    
    wget https://people.debian.org/~aurel32/qemu/mipsel/debian_wheezy_mipsel_standard.qcow2
    wget https://people.debian.org/~aurel32/qemu/mipsel/vmlinux-3.2.0-4-4kc-malta

创建虚拟网桥，实现虚拟机内部和Ubuntu的连接，并且启动虚拟机，创建一个shell文件。

    
    
    #set network
    sudo brctl addbr virbr0
    sudo ifconfig virbr0 192.168.5.1/24 up
    sudo tunctl -t tap0
    sudo ifconfig tap0 192.168.5.11/24 up
    sudo brctl addif virbr0 tap0
    
    qemu-system-mipsel -M malta -kernel vmlinux-3.2.0-4-4kc-malta -hda debian_wheezy_mipsel_standard.qcow2 -append "root=/dev/sda1" -netdev tap,id=tapnet,ifname=tap0,script=no -device rtl8139,netdev=tapnet -nographic

然后`sudo ./test.sh`执行。
![](https://images.seebug.org/content/images/2022/10/f77c0061-6695-490c-98c0-a9e767e90d31.png-w331s)

最后会让登陆和输入密码，都写root就行，然后就能成功进入qemu虚拟机。
![](https://images.seebug.org/content/images/2022/10/1326d4d6-66fe-4389-af4e-49ffd90bdecd.png-w331s)

在启动的虚拟机里面添加一个IP，是在上面图片中的qemu虚拟机中执行命令。

    
    
    ifconfig eth0 192.168.5.12 up

然后则是将提取出的固件的文件系统上传到qemu虚拟机中，在Ubuntu主机中执行命令。

    
    
    scp -r squashfs-root/ root@192.168.5.12:/root/

![](https://images.seebug.org/content/images/2022/10/60e717a0-a4f2-4a02-b70f-a4d446e85be7.png-w331s)

然后到qemu虚拟机中进行挂载和启动。

    
    
    chroot ./squashfs-root/ /bin/sh
    
    ./usr/sbin/lighttpd -f ./lighttp/lighttpd.conf

成功启动
![](https://images.seebug.org/content/images/2022/10/67e91974-c708-41b8-8ea0-5117c0c3870f.png-w331s)

界面这些和user模式都是差不多一样的。

## 漏洞分析

报了很多个漏洞，大部分是堆栈溢出，然后一些是命令注入，这里主要分析命令注入的相关漏洞。

### 登录验证绕过

这两个命令执行都是是需要登录验证的，这里先来分析如何进行登录验证绕过。

无论输入什么密码，都会返回错误，错误码为302。

先随便输入一个密码，看看发的包，可以看到主要的包有两个，先看第一个包。
![](https://images.seebug.org/content/images/2022/10/1431c95a-c470-4b97-80b5-3aeb5dfce04f.png-w331s)

可以看到处理http
post请求的是cstecgi.cgi，传入了username和password，对应action是login，我们到相关位置去查看对应的代码。

![](https://images.seebug.org/content/images/2022/10/4d980c0e-aa68-469a-9d34-ca8c586312f0.png-w331s)

可以看到，这里主要就是用sprinf初始一段语句，我们需要注意的是其中的topicurl，这个后面跟的就是对应接口的字符串，所以我们要去寻找loginAuth对应的处理函数。

这里再说一下，cstecgi.cgi处理不同的函数接口就是通过topicurl的值实现的，也就是后面goto LABEL_16的代码部分。
![](https://images.seebug.org/content/images/2022/10/e464b1ea-b9ee-4203-acf0-c57eb5656b40.png-w331s)

所以这些函数名称和函数地址也是那种常见的结构体的形式，我们要寻找loginAuth对应的处理函数，找到字符串的交叉引用，然后在周围找找，d键一下，就能找到对应的处理函数，函数地址在sub_42AEEC，下面来具体分析这个函数。

前面还是会获取一些参数的值，比如username还有password这些，然后还对password进行了urldecode。
![](https://images.seebug.org/content/images/2022/10/4c5825c5-b37a-4923-b6cd-ce3e54a4d002.png-w331s)

然后中间会有段比较password和http_passwd的代码，其会修改v18的值。

    
    
    v17 = strcmp(v6, v30);                        // username http_username
    if ( !strcmp(v35, v32) )                      // passwd http_passwd
        v18 = v17 != 0;
    else
        v18 = 1;

这里不知道是否是因为模拟环境的原因，无论使用什么密码都无法正常登陆，但是这里的v18，需要注意下，这是第二个包的参数之一，而且这个值在最后会为0。
![](https://images.seebug.org/content/images/2022/10/5bf9e7d0-8bcc-48a4-817f-fc13ea6842ee.png-w331s)

这段代码会snprintf一个重定向一个url，然后进行访问，其流程由flag参数的值决定，我们随便输入密码，就会进入第3个redirectURL，需要注意其authCode参数，授权码，也就是之前v18的值，现在它的值为0。

接下来我们看第二个包，可以看到和我们前面分析的一样，get访问了这个url。
![](https://images.seebug.org/content/images/2022/10/39c20bd8-cd81-4e7a-b951-b39f29a8a515.png-w331s)

这个http
get请求的处理在web服务进程lighttpd中，也就是我们quem启动的那个进程，我们通过authCode字符串，能交叉引用到其对应的函数为Form_Login。

开始分析Form_Login，开始还是先获取参数的值，然后根据goURL参数是否为空，来判断是否进入if里面。
![](https://images.seebug.org/content/images/2022/10/e66ba088-a13c-4e54-b31b-23650d734c10.png-w331s)

接着向下看。
![](https://images.seebug.org/content/images/2022/10/727a2dc7-e98f-4c29-b928-7b47a2633635.png-w331s)

所以这里，我们可以了解到goURL就是接下来要访问的html文件，authCode则是验证是否正确登录的一个值，并且经过后面的测试访问home.html就可以进入到后台界面。
所以我们可以构造下面的url，来绕过登录，进入后台，并且可以获取到cookie的SESSION_ID。

    
    
    http://xxx.xxx.xxx.xxx/formLoginAuth.htm?authCode=1&userName=admin&goURL=home.html&action=login
    http://xxx.xxx.xxx.xxx/formLoginAuth.htm?authCode=1&userName=admin&goURL=&action=login

goURL可有可无，因为goURL无值时，自动会strcpy “home.html”，效果如下。

![](https://images.seebug.org/content/images/2022/10/f469b384-61e8-4211-826f-f00c8093ff6e.png-w331s)

### OpModeCfg 命令注入

第一个是 /cgi-bin/cstecgi.cgi 中的 OpModeCfg
函数的命令注入漏洞，其漏洞原因是传入的hostName参数，可执行到doSystem函数，通过简单的构造即可导致命令执行。
但是想要执行到doSystem函数，需要绕过一些判断语句，proto不能为0，3，4，6，hostName不能为空。
![](https://images.seebug.org/content/images/2022/10/13214965-e306-4a85-bd4f-11265b2ef86e.png-w331s)

### UploadFirmwareFile 命令注入

第二个是 /cgi-bin/cstecgi.cgi 的 UploadFirmwareFile
函数，其参数FileName参数可控，并且将作为doSystem的参数被执行。

这个命令注入不需要绕过什么东西，代码位置比较靠前。
![](https://images.seebug.org/content/images/2022/10/5d3907ce-4f87-41b2-a18d-28eb3cd5c61e.png-w331s)

## 攻击测试

先尝试bp发一下包，可以看到攻击成功，并且带有回显
![](https://images.seebug.org/content/images/2022/10/c245547f-5f30-4b3c-afa6-cfe00144527d.png-w331s)

编写个poc进行攻击，先进行登录绕过获取cookie，然后进行攻击，攻击效果如下
![](https://images.seebug.org/content/images/2022/10/ba66579a-6bf4-482c-8f21-7b03f490e69a.png-w331s)

对于另一个命令注入攻击方式也差不多，只是没有回显，简单修改下poc，在tmp目录创建一个hack文件，攻击效果如下
![](https://images.seebug.org/content/images/2022/10/b6b9be6a-a4a4-40b7-8168-5aa072adf0b6.png-w331s)

## 参考

TOTOLINK NR1800X系列cve：<https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=TOTOLINK%20NR1800X>

环境搭建usr模式和system模式，并绕过登录检测：<https://bbs.pediy.com/thread-271765.htm#msg_header_h2_1>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1995/>

