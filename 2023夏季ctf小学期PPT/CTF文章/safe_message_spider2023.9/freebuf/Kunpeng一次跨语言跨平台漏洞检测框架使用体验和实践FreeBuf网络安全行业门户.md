***本文原创作者：wstart，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

 **最近在玩漏洞检测的工具时候发现一个比较有意思的漏洞检测框架，Kunpeng，它的构造理念是写一次POC， 不分语言，不分系统，不分平台的可以运行。**

![image.png](https://image.3001.net/images/20190310/1552195361_5c849f21445bc.png!small)

> Kunpeng项目地址
>
> <https://github.com/opensec-cn/kunpeng>

### 项目简介  

Kunpeng是一个Golang编写的开源POC检测框架，集成了包括数据库、中间件、web组件、cms等等的漏洞POC，可检测弱口令、SQL注入、XSS、RCE等漏洞类型，以动态链接库的形式提供调用，通过此项目可快速对目标进行安全漏洞检测，比攻击者快一步发现风险漏洞。简单来说就是一个漏洞POC库，封装了大量的漏洞检测插件，以动态链接库形式（so、dll、dylib）提供调用，传入目标地址和指定的POC即可返回结果。

### 环境要求

平台：没有要求，按需编译

系统：没有要求，基本上你的系统可以被GO支持，它就可以给你编译出来对应的版本。  

语言：没有要求，只要支持动态连接库的语言全部都支持。

### 准备工作

可以根据文档自行编译或者下载官方提供编译好的链接库，已经编译好的下载地址：<https://github.com/opensec-cn/kunpeng/releases>

列表中根据自己对应的系统进行下载：

MAC：kunpeng_darwin （吐槽一下不知道为啥要写darwin...我就找了好久mac在哪..后来索性自己编译了）

Linux：kunpeng_linux

Windows：kunpeng_windows

自己编译的话，有问题可以及时修改，比如x86,64之类的问题，或者一些特异性的linux。

当然，前提是要装了go，这又是后话了。

> 注1： kunpeng_darwin_v20190225.zip
> 解压后得到kunpeng_c.dylib和kunpeng_go.dylib一般常见的语言选kunpeng_c这个，用go的话才使用kunpeng_go.dylib。  
>
>
> 注2：由于笔者服务器上用的是JAVA，前期还要去下载 JNA的jar包
> <http://repo1.maven.org/maven2/net/java/dev/jna/jna/5.2.0/jna-5.2.0.jar>

其他的语言也要先调研好，动态库如何去调用的问题 。这里有很多语言的调用例子，可以先查看一下。

<https://github.com/opensec-cn/kunpeng/tree/master/example>

### 启动测试

首先搭建一下存在问题的环境，最简单的常见就是弱密码了，

用Docker一秒钟搭建一个弱密码的mysql：docker run -e MYSQL_ROOT_PASSWORD=123456 -p 3307:3306
-d mysql

为了快速体验一把，这里选了人见人爱的python

    
    
    import sys
    import json
    from ctypes import *
    
    if __name__ == '__main__':
    
        #加载Kunpeng
        kunpeng_path = '/Users/wstart/Downloads/kunpeng_darwin_v20190308/kunpeng_c.dylib'
        kp_obj = cdll.LoadLibrary(kunpeng_path)
    
        #设置参数类型
        kp_obj.Check.argtypes = [c_char_p]
        kp_obj.Check.restype = c_char_p
    
        #检测json
        task = {
            'type': "service",
            'target': "mysql",
            'netloc': "127.0.0.1:3308",
            'meta': {
                'passlist': ['123456', 'admin']
            }
        }
    
        task_json = json.dumps(task).encode('utf-8')
    
        #输出结果
        print(  json.loads( kp_obj.Check(task_json)))
        

执行后的结果：

![image.png](https://image.3001.net/images/20190310/1552188812_5c84858ca3255.png!small)

Kunpeng的基本的调用方式就是通过配置json可以对已经集成的漏洞进行检测和使用。

当然，对于特定需求的，也可以自己进行开发和定制：

<https://github.com/opensec-cn/kunpeng/>

有json和插件两种方式

### 一些思考和实践

 **1\. 和常见的开源项目一样，文档不健全是通病。**

对于一个集成了多个检测类型以及跨平台的漏洞检测框架来说，文档没有很好跟上是一个硬伤。

虽然作者在对应的文档位置已经标记出检测的脚本位置，但如果把支持的类型以及对应的参数列表列出来，会更让人理解和使用。

 **2\. 跨平台的检测框架的重要性**

目前Iot以及各种云服务商，使得当前的运维纬度剧增，在安全上的问题也日益复杂。一般企业可能借助于巡风之类的开源的扫描系统来统一从外部来检测系统的隐患，但是对于内部的隐患，比如内网，一些iot的设备固件问题等等，由于系统或者开发语言的不统一，可能就需要人工进行维护多份的检测代码，这个时候就需要一个可以跨平台的检测框架来统一维护，降低运维成本。

 **3\. 一个尝试**

笔者的一个朋友，在某厂进行运维工作，鉴于日渐增长的安全问题，原部署了内外巡风进行扫描，同时通过堡垒机进行对云服务器的运维。属于一个人的安全部典型。
[虽然厂子是挺大的]

![image.png](https://image.3001.net/images/20190310/1552191454_5c848fde0ed94.png!small)

由于有内外两套系统，部署配置检测起来也是比较麻烦，后Kunpeng发布后，由于跨平台和兼容性比较好，笔者协助其改装以Kunpeng为主要检测引擎的架构，通过堡垒机的集成和更新能力，快速把Kunpeng更新同步内外巡风，快速投入到当前的系统的检测。

![image.png](https://image.3001.net/images/20190310/1552192314_5c84933a55cb7.png!small)

当然，理想总是很美好的，现实很骨感，实验了几次以后，左边因为是单独的巡风扫描服务器，快速的集成了，但是右边会直接嵌入到线上的业务系统，还是需要推动开发以及其他部门来一起推进，暂时无进度中。  

【注】：截止到笔者写稿的时候，巡风已经集成Kunpeng

### 总结

由于跨平台跨语言，后续的很多的实现可以基于此来实现，以前梦想了好久的树莓派漏洞扫描仪估计也可以以这个契机来实现了。值得尝试的一个漏洞检测框架。

 ***本文原创作者：wstart，本文属FreeBuf原创奖励计划，未经许可禁止转载**

