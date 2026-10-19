***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：q601333824，本文属FreeBuf原创奖励计划，未经许可禁止转载**

## 概述

**由于最近渗透测试客户网站碰到了使用这个CMS的站点，于是就去官方下载了这个CMS审计看看，有一处代码的过滤方式并不严格，用的是htmlspecialchars进行实体编码过滤，而且参数用的是ENT_QUOTES(编码双引号和单引号),还有addslashes处理,但是没有对任何恶意关键字进行过滤，这样过滤对某些输出场景来说，已经是非常的宽松了。**

ps:第一次审计，过程简单明了，而且很好理解

## 相关环境

> 源码信息:EmpireCMS_7.5_SC_UTF8
>
> 漏洞类型:反射型XSS
>
> 下载地址:<http://www.phome.net/download/>
>
> 漏洞文件:e/admin/openpage/AdminPage.php

## 漏洞分析

①.例如这个地址是商城系统管理的打开地址,并且其中mainfile和leftfile参数存在XSS漏洞

    
    
    http://192.168.2.167/ecms75/e/admin/openpage/AdminPage.php?leftfile=..%2FShopSys%2Fpageleft.php%3Fehash_oE1Wa%3D2J9djPgtUYfniKn5Trpp&mainfile=..%2Fother%2FOtherMain.php%3Fehash_oE1Wa%3D2J9djPgtUYfniKn5Trpp&title=%E5%95%86%E5%9F%8E%E7%B3%BB%E7%BB%9F%E7%AE%A1%E7%90%86&ehash_oE1Wa=2J9djPgtUYfniKn5Trpp

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305138898825.png!small)

②.查看代码,开始就是hRepPostStr函数进行过滤,主要对字符进行addslashes和htmlspecialchars处理

![Clipboard
Image.png](https://image.3001.net/images/20180702/1530513962734.png!small)

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305142904503.png!small)③.之后又判断了://,意思是不允许http或者https

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305175831463.png!small)  

④.最后就是网页输出了，但是输出的位置是iframe标签的src里面，可以通过输入javascript:alert(document.cookie)触发XSS代码，意思就是上面那些过滤没什么用

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305173823220.png!small)  

![Clipboard
Image.png](https://image.3001.net/images/20180702/153051445799.png!small)

## 利用方法

①.由于url地址存在hash参数，例如ehash_oE1Wa=2J9djPgtUYfniKn5Trpp,这个参数是随机生成的,如果缺少这个参数，会提示非法来源

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305147494390.png!small)

②.用PHP举例,PHP可以通过$_SERVER['HTTP_REFERER']获取点击来源,这样就获取了hash参数，然后组成XSS地址

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305149285384.png!small)  

![Clipboard
Image.png](https://image.3001.net/images/20180702/15305151502811.png!small)  
  
  
③.最后重定向到XSS地址就可以触发了

![111.png](https://image.3001.net/images/20180702/15305183986989.png!small)

![222222.png](https://image.3001.net/images/20180702/15305184446875.png!small)

  

④.动态图测试效果,管理员以为添加的是友情连接<http://192.168.2.167:81/>是正常地址，但是实际从后台打开是XSS地址

![2222222.gif](https://image.3001.net/images/20180702/15305187991775.gif!small)  
  

  
  

## 总结

1.概括内容就是，商城系统管理是用iframe加载页面，但是过滤不严格导致出现XSS，利用的时候，hash参数可以通过从后台点击,从$_SERVER['HTTP_REFERER']获取

2.利用成功只要两个条件，后台显示外部超链接的地方，并且管理员点击就行，所以局限还是有一点的

 ***本文原创作者：q601333824，本文属FreeBuf原创奖励计划，未经许可禁止转载**

