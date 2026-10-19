IIS短文件漏洞影响范围及危害  
IIS 1.0，Windows NT 3.51  
IIS 3.0，Windows NT 4.0 Service Pack 2  
IIS 4.0，Windows NT 4.0选项包  
IIS 5.0，Windows 2000  
IIS 5.1，Windows XP Professional和Windows XP Media Center Edition  
IIS 6.0，Windows Server 2003和Windows XP Professional x64 Edition  
IIS 7.0，Windows Server 2008和Windows Vista  
IIS 7.5，Windows 7（远程启用<customErrors>或没有web.config）

IIS 7.5，Windows 2008（经典管道模式）

注意：IIS使用.Net Framework 4时不受影响

漏洞描述

弱点描述：IIS是由微软公司提供的基于运行Microsoft Windows的互联网基本服务。最初是Windows
NT版本的可选包，随后内建在Windows 2000、Windows XP Professional和Windows Server
2003一起发行，但在普遍使用的Windows XP
Home版本上并没有IIS。7月2日网上公开了iis短文件名泄露漏洞，该漏洞对用户的危害性中等，但影响范围较广，几乎所有版本的IIS均会直接受到影响。下面是该漏洞的详细信息：1、漏洞类型：
信息泄露2、发布时间： 2012-07-023、漏洞危害： 中等4、影响范围（几乎所有IIS版本） IIS 1.0, Windows NT 3.51 IIS
2.0, Windows NT 4.0 IIS 3.0, Windows NT 4.0 Service Pack 2 IIS 4.0, Windows NT
4.0 Option Pack IIS 5.0, Windows 2000 IIS 5.1, Windows XP Professional and
Windows XP Media Center Edition IIS 6.0, Windows Server 2003 and Windows XP
Professional x64 Edition IIS 7.0, Windows Server 2008 and Windows Vista IIS
7.5, Windows 7 (error remotely enabled or no Web.config) IIS 7.5, Windows 2008
(classic pipeline mode)5、漏洞描述 windows下通过~表示短文件名，如：test~1，
在IIs中可通过短文件名的方式判断目标文件是否存在，从而降低文件名暴力猜解的难度。6、漏洞检查方式
可使用http://test/%2Fconnec~1.as*%2Fx.aspx
如果存在connec开头的asp,aspx等类似文件，将返回文件不存在的错误，否则将返回非法请求。参考链接：IIS短文件名泄露漏洞

漏洞建议

一般性的建议：建议升级IIS版本或者使用WAF进行防护。

复现方法：

OPTIONS方法猜解分析

由于上述OPTIONS方法请求猜测出短文件名，猜测成功返回404，猜测失败返回的是200，失败的组合比较多，所以下面主要分析下404猜测成功的请求如何通过OPTIONS方法获取短文件名IIS10T.HTM的。

使用Burp Sutie工具爆破拆解，如果所示：  
![1682501613_6448efed52f6e944490f5.png!small](https://image.3001.net/images/20230426/1682501613_6448efed52f6e944490f5.png!small)

猜测出存在以字母“c”为开头的文件，服务器响应404，不存在显示响应200，存在该IIS短文件名泄露漏洞。

![1682501701_6448f04544d0dab0b4070.png!small](https://image.3001.net/images/20230426/1682501701_6448f04544d0dab0b4070.png!small)

