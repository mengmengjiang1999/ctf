## 简介

本文介绍比较好用的几个burp插件，并且亲自使用和调试了一段时间，为了避免大家走弯路，我写这篇文章来跟喜欢安全的小伙伴分享：

1.不同burp的版本一定程度上会影响插件使用，老版本burp对有些插件并不适用，如果想要有良好的体验尽量下载新burp。

2.有些插件是python写的，想在java环境的burp中使用这些插件需要安装jython环境，具体步骤在第6个插件上有详细说明。

3.下面这些XXXscan插件更多的作用体现在漏洞扫描（漏洞发现）层面，需要配合其他工具利用效果更佳。例：ShiroScan+ShiroExploit，Struts_Finder+Strus2漏洞检查工具，就可以很好地对这些漏洞进行复现。

#  ** **1.**** ** **F**** ** **astjsonscan****

##  ** **1.1**** ** **FastjsonScan的工具说明****

该工具为一款fastjson检测的插件，为被动扫描，但是需要借助dnslog检测，当dnslog无法访问时，会检测失败。

##  ** **1.2FastjsonScan的安装方法****

  

点击select file

![1647914589_62392e5d7336b35ebe26b.png!small](https://image.3001.net/images/20220322/1647914589_62392e5d7336b35ebe26b.png!small)

选择相应的BurpFastJsonScan.jar点击Next即可。

![1647914596_62392e64d2b47da9176b9.png!small](https://image.3001.net/images/20220322/1647914596_62392e64d2b47da9176b9.png!small)

##  ** **1.3FastjsonScan的使用实例****

1.先打开burp配置好代理，准备抓包。

![1647914608_62392e70735c6a1ebb35b.png!small](https://image.3001.net/images/20220322/1647914608_62392e70735c6a1ebb35b.png!small)

2.打开存在漏洞的网站，并抓包。

![1647914612_62392e74e0a00291dd889.png!small](https://image.3001.net/images/20220322/1647914612_62392e74e0a00291dd889.png!small)

3.点击右键，寻找刚装好的FastJosnScan 点击【Send to FastjosnScan】。

![1647914628_62392e8499ec70ca917e6.png!small](https://image.3001.net/images/20220322/1647914628_62392e8499ec70ca917e6.png!small)

4.当检测到存在Fastjson时，issue会出现vul!!!并附带payload。

![1647914634_62392e8a133877b7769d5.png!small](https://image.3001.net/images/20220322/1647914634_62392e8a133877b7769d5.png!small)

注：由于该插件需要利用DNSLOG，所以必须要能访问DNSLOG，否则会出现如下情况：

![1647914638_62392e8e6dd8b678c7139.png!small](https://image.3001.net/images/20220322/1647914638_62392e8e6dd8b678c7139.png!small)

#  ** **2.**** ** **S**** ** **hiro**** ** **S**** ** **can****

##  ** **2.1ShiroScan的工具说明****

该工具为pmiaowu开发的一款burpsuite被动式shiro扫描插件，该工具仅能扫shiro keys，利用链需要自行查找。

##  ** **2.2ShiroScan的安装方法****

下载地址：https://github.com/Daybr4ak/ShiroScan

跟上述步骤一样，请自行安装。

##  ** **2.3ShiroScan的使用实例****

1.使用该插件前应确保被动扫描开启。

![1647914647_62392e973ce486b1c784a.png!small](https://image.3001.net/images/20220322/1647914647_62392e973ce486b1c784a.png!small)

  

2.该插件为被动扫描，无需人工点击扫描，扫描成功的结果会输出到图形界面中。

  

![1647914649_62392e99dc5fa0426315e.png!small](https://image.3001.net/images/20220322/1647914649_62392e99dc5fa0426315e.png!small)

  

#  ** **3.**** ** **S**** ** **truts_**** ** **Finder****

##  ** **3**** ** **.1Struts_Finder的工具说明****

用于检查struts 2 RCE漏洞，需要人工点击扫描

##  ** **3**** ** **.**** ** **2**** ** **Struts_Finder的安装方法****

下载地址：https://github.com/prakharathreya/Struts2-RCE

跟上述步骤一样，请自行安装。

  

  

##  ** **3**** ** **.3Struts_Finder的使用实例****

1.先输入数据后抓包。

![1647914657_62392ea171acffa2e828e.png!small](https://image.3001.net/images/20220322/1647914657_62392ea171acffa2e828e.png!small)

2.需要人工点击扫描，鼠标右键点击数据包，选择【Check for Struts RCE】。

![1647914672_62392eb04228a1725987d.png!small](https://image.3001.net/images/20220322/1647914672_62392eb04228a1725987d.png!small)

3.漏洞详情和payload都在issue里。

![1647914676_62392eb49480fd222384b.png!small](https://image.3001.net/images/20220322/1647914676_62392eb49480fd222384b.png!small)

#  ** **4.**** ** **Autorize****

##  ** **4.1Autorize的工具说明****

Autorize 是一个测试权限问题的插件，可以在插件中设置一个低权限账号的 cookie ，然后使用高权限的账号去浏览所有功能，Autorize
会自动用低权限账号的 cookie 重放请求，同时也会发一个不带 cookie 的请求来测试是否可以在未登录状态下访问

##  ** **4.2Autorize的安装方法****

该插件可以直接在BApp Store里面安装

![1647914683_62392ebbe8aaf3647d403.png!small](https://image.3001.net/images/20220322/1647914683_62392ebbe8aaf3647d403.png!small)

##  ** **4.3Autorize的使用实例****

1.在方框中填入低权限的Cookie，然后点击Autorize is off，然后使用高权限的账号去浏览所有功能。

![1647914688_62392ec0c79eb5e80ae3c.png!small](https://image.3001.net/images/20220322/1647914688_62392ec0c79eb5e80ae3c.png!small)

![1647914692_62392ec41b1bc41dd4c50.png!small](https://image.3001.net/images/20220322/1647914692_62392ec41b1bc41dd4c50.png!small)

#  ** **5.**** ** **H**** ** **ack**** ** **B**** ** **ar****

##  ** **5.1Hack Bar的工具说明****

HackBar是一个基于java的Burpsuite插件，支持很多高效便携的功能，如SQL注入丶常见LFI漏洞等。

##  ** **5.2Hack Bar的安装方法****

  

下载地址：<https://github.com/d3vilbug/HackBar>

跟上述步骤一样，请自行安装。

  

##  ** **5.3Hack Bar的使用实例****

1.以sql注入漏洞为例，发送请求并抓包。

![1647914701_62392ecdc91c457309649.png!small](https://image.3001.net/images/20220322/1647914701_62392ecdc91c457309649.png!small)

  

2.放到repeater中，使用对想要使用payload的地方右键点击【Hack Bar】

![1647914705_62392ed1761a22c90b238.png!small](https://image.3001.net/images/20220322/1647914705_62392ed1761a22c90b238.png!small)

  

3.选择自己想要的payload进行使用。

![1647914718_62392ede1facb2548ed71.png!small](https://image.3001.net/images/20220322/1647914718_62392ede1facb2548ed71.png!small)

#  ** **6.****[ **
**BurpReflectiveXssMiao****](https://github.com/pmiaowu/BurpReflectiveXssMiao)

  

##  ** **6**** ** **.1BurpReflectiveXssMiao的工具说明****

此插件会检测所有的GET/POST参数并且进行xss fuzz

##  ** **6**** ** **.2BurpReflectiveXssMiao的安装方法****

下载地址：https://github.com/pmiaowu/BurpReflectiveXssMiao

首先要下载http转发插件：https://github.com/pmiaowu/BurpHttpForwardRequests

因为该工具由python编写，所以要装jython环境。

Jython下载地址：<https://www.jython.org/download.html>

![1647914726_62392ee638beeee89f021.png!small](https://image.3001.net/images/20220322/1647914726_62392ee638beeee89f021.png!small)

Jython在burp中安装步骤。

![1647914733_62392eed69ad8e0d60066.png!small](https://image.3001.net/images/20220322/1647914733_62392eed69ad8e0d60066.png!small)

##  ** **6.**** ** **3BurpReflectiveXssMiao的使用实例****

  

  

  

1.浏览在有xss漏洞的页面，该工具会自动扫描，配置好参数

![1647914737_62392ef1c1b0b9b7cf4ed.png!small](https://image.3001.net/images/20220322/1647914737_62392ef1c1b0b9b7cf4ed.png!small)

  

2.最后在扫描器或者插件处查看结果。

![1647914744_62392ef8ea233edec15ba.png!small](https://image.3001.net/images/20220322/1647914744_62392ef8ea233edec15ba.png!small)

#  ** **7**** ** **.**** ** **J2EE Scan****

##  ** **7.**** ** **1**** ** **J2EE Scan**** ** **的工具说明****

J2EEScan 是[Burp Suite Proxy](http://portswigger.net/)的插件。此插件的目标是提高对 J2EE 应用程序的
Web 应用程序渗透测试期间的测试覆盖率。

##  ** **7.**** ** **2**** ** **J2EE Scan**** ** **的安装方法****

下载地址：<https://github.com/portswigger/j2ee-scan>

安装步骤如下：

  1. 从“选项”->“会话”中的“Cookie jar”部分启用扫描器和扩展器字段。

![1647914750_62392efecfbb60610688a.png!small](https://image.3001.net/images/20220322/1647914750_62392efecfbb60610688a.png!small)

  

  2. 在 Burp Extender 选项卡中加载 J2EEscan jar。

![1647914754_62392f0279dd9575cc635.png!small](https://image.3001.net/images/20220322/1647914754_62392f0279dd9575cc635.png!small)

3.出现√代表安装成功。

![1647914758_62392f06847abd3f8e229.png!small](https://image.3001.net/images/20220322/1647914758_62392f06847abd3f8e229.png!small)

##  ** **7.**** ** **3J2EE Scan**** ** **的使用实例****

1.抓取数据包并右键【Do active scan】发送给J2EE扫描。

![1647914766_62392f0eecb8aa412113a.png!small](https://image.3001.net/images/20220322/1647914766_62392f0eecb8aa412113a.png!small)

2.查看漏洞详情。

![1647914771_62392f134362d10bd63ad.png!small](https://image.3001.net/images/20220322/1647914771_62392f134362d10bd63ad.png!small)

#  ** **8.Passive-scan-clien**** ** **t****

##  ** **8.**** ** **1Passive-scan-client的工具说明****

被动扫描流量转发插件，主要功能和目前版本burp的Upstream Proxy Server功能基本重复，但是其也有自己的优势

1.不用每次新打开burp都要去配置Upstream Proxy Server

2.有流量筛选功能，包括去除某些请求，锁定某个域名的流量

##  ** **8.2**** ** **Passive-scan-client的安装方法****

下载地址：https://github.com/c0ny1/passive-scan-client

##  ** **8.**** ** **3**** ** **Passive-scan-client的使用实例****

1.例：与xray联动，ip和端口设置好后点击【run】

![1647914786_62392f22103e9138402a7.png!small](https://image.3001.net/images/20220322/1647914786_62392f22103e9138402a7.png!small)

2.如果有漏洞，就会在插件窗口显示。

![1647914789_62392f251d708827ea831.png!small](https://image.3001.net/images/20220322/1647914789_62392f251d708827ea831.png!small)

如果看完这篇文章还有地方不懂得可以在评论区评论或者私信我哈。

如果有的地方讲错的也请大佬指出。

 **转载请标明出处哦。**

  

