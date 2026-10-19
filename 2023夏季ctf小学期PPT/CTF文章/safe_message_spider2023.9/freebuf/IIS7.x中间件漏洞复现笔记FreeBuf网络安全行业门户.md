## **1、解析漏洞**

 **漏洞简介：**

IIS 7.x版本在 Fast-CGI运行模式下，在任意文件后加上/.php，会解析为php文件。

 **复现操作：**

创建一个.png文件，使用xxx.png/.php解析后显现404错误。  
![image-20210511004251466.png](https://image.3001.net/images/20210511/1620703631_6099f98fce059ea7878e4.png!small)![image-20210510235557969.png](https://image.3001.net/images/20210511/1620703660_6099f9ac61831985e67a2.png!small)复现需关闭phpStudy_FastCGI中的请求限制。  
![image-20210511000727719.png](https://image.3001.net/images/20210511/1620703679_6099f9bf8c4225fd4c87e.png!small)![image-20210511003639934.png](https://image.3001.net/images/20210511/1620703689_6099f9c949dd3fdd29e8d.png!small)  
![image-20210511003735894.png](https://image.3001.net/images/20210511/1620703697_6099f9d1291823fedffb3.png!small)解析成功。

 **修复建议：**

配置cgi.fix_pathinfo(php.ini中)为0并重启php-cgi程序。

##  **2、HTTP.SYS远程代码执行（MS15-034）**

 **漏洞简介：**

远程代码执行漏洞存在于HTTP协议堆栈（HTTP.sys）中，当HTTP.sys未正确分析经特殊设计的HTTP请求时会导致此漏洞。成功利用后可在系统账户的上下文中执行任意代码，可导致IIS服务器所在机器蓝屏或读取内存中的数据。

 **影响范围：**

Windows 7、Windows Server 2008 R2、Windows 8 和 Windows 8.1、Windows Server 2012 和
Windows Server 2012 R2

IIS 7.5、IIS 8.0、IIS 8.5

 **复现操作：**

访问IIS 7.5后，打开F12的网络页面，重新访问出现请求，点击200的一行后，重发并编辑请求头。

    
    
    Range: bytes=0-18446744073709551615
    

![image-20210511010259808.png](https://image.3001.net/images/20210511/1620703739_6099f9fbb50f56514577a.png!small)![image-20210511010521290.png](https://image.3001.net/images/20210511/1620703747_6099fa03dd10ead19eaa5.png!small)返回状态码为416，说明存在此漏洞。

 **修复建议：**

安装修复补丁（KB3042553）

##  **3、认证绕过漏洞**

 **漏洞简介：**

该漏洞源于对用户提供的输入未经正确的验证。

 **影响范围：**

IIS 6.0、IIS 7.5

 **1）安装了PHP的 IIS 6.0身份验证绕过**

IIS 6.0加载受保护（如：admin）目录中的PHP文件需要用户认证信息（用户名和密码访问），如果将

    
    
    ::$INDEX_ALLOCATION/index.php
    

作为后缀附加到目录名称后面，存在绕过验证并可能访问管理文件等，导致重要信息泄露。

 **2）IIS 7.5经典ASP身份认证绕过**

配置 ASP和.NET Framework 4.0的 IIS 7.5，通过将

    
    
    :$i30:$INDEX_ALLOCATION/index.asp
    

后缀附加到需要认证的请求目录名称后面，绕过经典的ASP文件访问限制。

 **3）IIS 7.5 .NET源码公开和身份验证绕过**

配置PHP的 IIS 7.5中存在认证绕过漏洞

    
    
    http://<victimIIS75>/admin:$i30:$INDEX_ALLOCATION/admin.php
    

**复现环境：**

IIS 7.5

 **复现操作：**

在 C:\inetpub\wwwroot目录下创建admin文件夹并放入index.php文件，并关闭默认的匿名身份验证。访问
/admin/index.php目录下的文件需要认证信息，认证失败或无认证信息会返回401未授权。  
![image-20210511014901008.png](https://image.3001.net/images/20210511/1620703762_6099fa12e50ee71f0f091.png!small)![image-20210511015136097.png](https://image.3001.net/images/20210511/1620703769_6099fa19438a869e3ba7b.png!small)  
利用” $i30:$INDEX_ALLOCATION “绕过此限制。

复现失败（逃）。

 **防护建议：**

1.IIS 7.5配置.NET Framework 2.0可以不受2）的绕过影响。

2.攻击者需要事先获取IIS服务器受认证保护目录。

