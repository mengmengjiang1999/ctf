2月20日，国家信息安全漏洞共享平台（CNVD）发布了一则关于Apache
Tomcat存在文件包含漏洞的安全公告（CNVD-2020-10487，对应CVE-2020-1938）。

绿盟科技安全研究团队第一时间对此次漏洞进行研究，并紧急上线了在线检测工具。

您可以登陆绿盟云https://cloud.nsfocus.com，进入“漏洞威胁-紧急漏洞”，按要求输入待检测的站点信息，点击“立即检测”即可。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQpuWaXaJ4v0ROvOYjFo9Jem4CC0LNNT3s91tCYreAZg5cG7iafcqWqew/640?wx_fmt=png](https://image.3001.net/images/20200221/1582272812_5e4f912cb104a.jpg!small)

**漏洞综述**

2月20日，国家信息安全漏洞共享平台（CNVD）发布了一则关于Apache
Tomcat存在文件包含漏洞的安全公告。公告中表示，存在于ApacheTomcat中的文件包含漏洞（CNVD-2020-10487，对应CVE-2020-1938）可使攻击者在未授权的情况下远程读取特定目录下的任意文件。漏洞源于Tomcat
AJP协议实现中的缺陷，使得相关参数可控。攻击者通过向AJP协议端口（默认8009）发送精心构造的数据，可读取服务器webapp目录下的任意文件，比如配置文件、源代码等。而且如果服务器端有文件上传功能，那么攻击者还可能进一步实现远程代码的执行。

参考链接：

https://www.cnvd.org.cn/webinfo/show/5415

**影响范围**

 **受影响产品版本：**

Tomcat 6 (已不受维护)

Tomcat 7 Version < 7.0.100

Tomcat 8 Version < 8.5.51

Tomcat 9 Version < 9.0.31

**不受影响产品版本：**

Tomcat 7 Version >=7.0.100

Tomcat 8 Version >=8.5.51

Tomcat 9 Version >=9.0.31

**解决方案**

Apache官方已经发布新版本修复了该漏洞，请受影响的用户尽快升级进行防护，无法立即进行更新的用户可参考 CNVD通告采取临时缓解措施。

新版本下载地址：

https://github.com/apache/tomcat/releases

http://tomcat.apache.org/

CNVD 通告：

https://www.cnvd.org.cn/webinfo/show/5415

  

