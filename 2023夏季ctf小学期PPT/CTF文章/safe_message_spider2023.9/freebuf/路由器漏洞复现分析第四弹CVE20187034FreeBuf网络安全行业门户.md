## 漏洞信息  

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214390333218.png!small)

本系列中的前三篇文章参考如下：

> [通过CVE-2017-17215学习路由器漏洞分析，从入坑到放弃](http://www.freebuf.com/vuls/160040.html)
>
> [路由器漏洞复现分析第二弹：CNVD-2018-01084](http://www.freebuf.com/vuls/162627.html)
>
> [路由器漏洞复现分析第三弹：DVRF
> INTRO题目分析](http://www.freebuf.com/articles/wireless/163823.html)

TrendNET路由器权限绕过漏洞，攻击者通过设置$AUTHORIZED_GROUP >= 1绕过权限验证

漏洞参考信息:<https://blogs.securiteam.com/index.php/archives/3627>

受影响的路由器版本

> TEW-751DR – v1.03B03
>
> TEW-752DRU – v1.03B01

通过zoomeye搜索,能找到508台设备,主要用户分布于美国和马其顿.

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214390872562.png!small)  

使用curl -d "SERVICES=DEVICE.ACCOUNT%0aAUTHORIZED_GROUP=1"
http://[IP]/getcfg.php 命令可以直接获取到路由器的用户名和密码

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214393459131.png!small)

## 漏洞分析

本次分析使用固件的是TEW751DR_FW103B03.  

Binwalk解包后找到getcfg.php,位置如图

当AUTHORIZED_GROUP>=0的时候,getcfg就正常执行代码功能.

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214400765738.png!small)

POC中传入的参数为SERVICES=DEVICE.ACCOUNT

$file最后可以拼接为/htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml.php

打开这个文件,可以看到它能读取设备的各种信息包括用户名和密码

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214407317674.png!small)  

造成验证漏洞的函数在htdoc/cgibin的
phpcgi_main函数,当cgibin_parse_request函数处理http请求的时候,sub_405AC0函数会获取AUTHORIZED_GROUP并存下来,
之后再调用sess_validate()作验证,因此可以非授权用户可以直接给AUTHORIZED_GROUP赋值来绕过验证  

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214414542222.png!small)  

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214414707391.png!small)

使用如下脚本调试存在漏洞的cgibin:

    
    
    chroot . ./qemu  -0"phpcgi" -E REQUEST_METHOD="POST"  -EREQUEST_URI="getcfg?AUTHORIZED_GROUP=1" -E CONTENT_LENGTH=18 -ECONTENT_TYPE="application/x-www-form-urlencoded" -g $PORT -EREMOTE_ADDR="127.0.0.1"   -strace ./htdocs/cgibin "kkkkkkkkkkkk"

cgibin_parse_request中的parse_uri函数会调用sub_405AC0，此处从request_uri中取”?”后的字符,作为参数传入sub_403864

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214492538354.png!small)

sub_405AC0调用后可以看已经把”AUTHORIZED_GROUP=1”存入全局变量

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214492841569.png!small)

再继续执行到sess_validate()执行完毕

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214492995167.png!small)

后面再将得到的这个值写入/var/run/xmldb_sock

![路由器漏洞复现分析第4弹：CVE-2018-7034](https://image.3001.net/images/20180319/15214493337046.png!small)  

 ***本文作者：kczwa1，转载请注明来自FreeBuf.COM**

