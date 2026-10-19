## **摘要：**

* * *

Coship Wireless
Router是中国同洲（Coship）电子公司的一款无线路由器。Coship无线路由器中存在安全漏洞：攻击者可以通过远程发送特定数据包绕过认证，直接获取到管理员的账号密码，从而控制路由器；
**该漏洞目前尚可通杀Coship无线路由器的所有版本** 。

产品官网：http://en.coship.com/

##  **影响分布：**

* * *

fofa上显示，受该漏洞影响的Coship无线路由器数量 **超过20万台** ，且集中分布在哥伦比亚。

![](https://image.3001.net/images/20200817/1597659315.png!small)![](https://image.3001.net/images/20200817/1597659330.png!small)

##  **历史漏洞：**

* * *

我们可以在此网站查看历史漏洞：https://www.cvedetails.com/vendor/17866/Coship.html

如图所示，无论是xss，还是发送特定数据包，最后都需要通过修改设备的账号密码来达到控制路由器的目的。

![](https://image.3001.net/images/20200817/1597659369.png!small)

##  **漏洞演示：**

<https://www.bilibili.com/video/BV1bf4y1Q7dL/>

