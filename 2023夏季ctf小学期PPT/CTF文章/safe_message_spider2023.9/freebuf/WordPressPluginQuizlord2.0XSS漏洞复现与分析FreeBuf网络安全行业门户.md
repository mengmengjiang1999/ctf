***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **WordPress是使用PHP语言开发的博客平台，用户可以在支持PHP和MySQL数据库的服务器上架设属于自己的网站。也可以把
WordPress当作一个内容管理系统（CMS）来使用。**  

WordPress经常爆出漏洞基本都是它的插件存在安全问题。

## 漏洞复现

首先搭建worepress，我的版本是4.4。然后进入后台下载插件Quizlord，版本是2.0。

![1.png](https://image.3001.net/images/20181119/1542627085_5bf29f0d0919a.png!small)![2.png](https://image.3001.net/images/20181119/1542627095_5bf29f1726952.png!small)下载、安装完成后，需要点击启用插件。

![3.png](https://image.3001.net/images/20181119/1542627115_5bf29f2b6fbb6.png!small)根据exploit-db给出的漏洞详情，找到触发漏洞的位置。

![4.png](https://image.3001.net/images/20181119/1542627153_5bf29f5163c23.png!small)

进入后台选择Quizlord插件  
![5.png](https://image.3001.net/images/20181119/1542627153_5bf29f516daf8.png!small)

此时浏览器的地址栏正好对应poc中的referer内容，现在只要使用火狐插件hackbar并根据POC构造POST请求。  
![6.png](https://image.3001.net/images/20181119/1542627153_5bf29f517996c.png!small)点击execute即可发送该POST请求。  

![7.png](https://image.3001.net/images/20181119/1542627153_5bf29f51b2ea0.png!small)请求成功后，返回是一个空白页。  

![8.png](https://image.3001.net/images/20181119/1542627153_5bf29f51b97ec.png!small)返回上一页并刷新即可触发该漏洞。  

![9.png](https://image.3001.net/images/20181119/1542627153_5bf29f51cbb7f.png!small)

通过复现这个漏洞，我们可以知道它属于后台存储型XSS，且它的危害其实并不是很大。

需要进入后台，因此必须得知道后台用户的账号和密码。

下面我们来简单分析一下漏洞的成因。

## 漏洞成因分析

WordPress插件源码位置：  

    
    
    \wp4_4\wp-content\plugins\

进入Quizlord插件目录，找到quizlord.php文件。

![11.png](https://image.3001.net/images/20181119/1542627154_5bf29f520ba09.png!small)下图是quizlord.php文件的内容  

![12.png](https://image.3001.net/images/20181119/1542627154_5bf29f52226d4.png!small)

根据POC快速定位到函数。发现POST传入的数据并没有被程序过滤就写入了数据库中。  
![13.png](https://image.3001.net/images/20181119/1542627154_5bf29f5247687.png!small)

  

## 修复方案

利用htmlentities()函数转义html实体。  

![14.png](https://image.3001.net/images/20181119/1542627154_5bf29f52430b0.png!small)再次提交POC后，无法触发XSS漏洞。  

##
![15.png](https://image.3001.net/images/20181119/1542627154_5bf29f528ab37.png!small)  
参考链接  

> <https://www.exploit-db.com/exploits/45307/>  
>

 ***本文作者：看不尽的尘埃，转载请注明来自FreeBuf.COM**

