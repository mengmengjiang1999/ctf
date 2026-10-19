***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **2019年3月25日，国外安全研究人员** 在 **大量攻击数据中发现了一个WordPress** **plugins** **Social
Warfare远程代码执行** **漏洞** **。** **该漏洞位于social-warfare\lib\utilities\SWP_Database_Migration.php文件中的eval** **(** **)**
**函数，该函数能够运行攻击者在“swp_url”GET参数中定义的PHP代码。此漏洞允许攻击者接管整个WordPress站点并管理您的主机帐户上的所有文件和数据库，**
**从而实现完全远程接管** **整个服务器的目的。** ****

##  **** **WordPress** **组件** **介绍**

WordPress是使用PHP语言开发的CMS系统，是网络上最受欢迎的CMS之一，也是一款个人博客系统。根据w3tech的资料显示，约有30％的网站在使用它，用户可以在支持PHP和MySQL数据库的服务器上架设属于自己的网站或者使用自己的博客。  

Social Warfare
Plugin是WordPress的一款流行社交分享插件，在WordPress站点上的安装量已达70000以上，该插件在WordPress社交分享类插件中也独占鳌头，用户可以利用该插件获得更多的社交分享，同时也可以利用该插件获得更多的网站流量。该插件是由一群专业的社交媒体营销专家和世界级开发人员开发而出的。

Social Warfare Plugin在WordPress
插件库中一致保持着更新，该插件最近更新时间为2019年3月24日，最新版本为3.5.4，该插件共有Social Warfare Plugin
2.2.x、Social Warfare Plugin 2.3.x、Social Warfare Plugin 3.3.x、Social Warfare
Plugin 3.4.x、Social Warfare Plugin 3.5.x五个系列，该插件每个版本的使用情况如下图：

##
![图片.png](https://image.3001.net/images/20190326/1553604387_5c9a1f2366d85.png!small)
**漏洞描述**

WordPress Social Warfare Plugin 远程代码执行漏洞影响Social Warfare Plugin
3.5.3以前的版本，我们从上节Social Warfare
Plugin各版本使用量可知，该漏洞影响大部分该插件的90%以上的用户，所以该漏洞影响范围甚广。

该漏洞位于social-warfare\lib\utilities\SWP_Database_Migration.php文件中的eval()函数，该函数能够运行攻击者在“swp_url”GET参数中定义的PHP代码。此漏洞允许攻击者接管整个WordPress站点并管理您的主机帐户上的所有文件和数据库，从而实现完全远程接管整个服务器的目的。
**  
**

##  **漏洞分析**

在文件social-warfare\lib\utilities\SWP_Database_Migration.php中：

![图片.png](https://image.3001.net/images/20190326/1553604403_5c9a1f33dc75c.png!small)

在代码中，服务器通过获取到swp_url参数，然后使用file_get_contents读取该文件中的内容，存储到options中，然后经过识别内容中的<pre>标签，将处理过后的内容存入到$array中,最终，该参数被带入到eval参数中直接执行，造成远程代码执行漏洞。

##  **漏洞** **复现**

我们首先在任意版本WordPress上安装Social Warfare插件，然后使用构造好的payload攻击该网站，最终执行命令。

##
![图片.png](https://image.3001.net/images/20190326/1553604425_5c9a1f499c7ac.png!small)
**影响范围**

目前据统计，在全球范围内对互联网开放Wordpress网站的资产数量多达12833569台，其中归属中国地区的受影响WordPress资产数量为18万以上，该插件安装量达7万多站点。

目前受影响的Social Warfare Plugin版本：

    
    
    Social Warfare Plugin < 3.5.3

##  **修复建议**

Wordpress官方插件库已经在更新了该插件版本，该插件的用户可以更新至该插件的最新版本：

<https://wordpress.org/plugins/social-warfare/advanced/> __

__

## **参考链接**

<https://www.webarxsecurity.com/social-warfare-vulnerability/> _  
_

 ***本文作者：深信服千里目安全实验室，转载庆祝来自FreeBuf.COM**

