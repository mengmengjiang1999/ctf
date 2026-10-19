## 简介

谷歌搜索引擎可谓是无人不知，无人不晓一般的存在。对于普通用户来说是一款非常强大的检索工具，对于黑客来讲，则是一款非常强大的黑客工具。  
这里就介绍几个常用基础的谷歌黑客语法。对于像我这样的新手来说，已经是非常强大了。  
![image](https://image.3001.net/images/20210604/1622817251_60ba39e3e9babaa70f5de.jpg!small)

intitle：检索含有指定标题内容的网页。例如："intitle:管理员登陆"，搜索的结果就像下面这样。  
![image](https://image.3001.net/images/20210604/1622817270_60ba39f6521b6091cdfc5.png!small)inurl：检索含有指定内容的URL。例如："inurl:admin"，搜索的结果就像下面这样。  
![image](https://image.3001.net/images/20210604/1622817284_60ba3a0474e102b7c889f.png!small)intext：检索在正文部分含有指定内容的网页。例如："intext:管理员登陆"，搜索的结果就像下面这样。  
![image](https://image.3001.net/images/20210604/1622817302_60ba3a1629d5cf1eb4a88.png!small)site：检索与指定网站有联系的所有已收录的网页。例如：  
"site:www.XXX.edu.cn"，搜索的结果就像下面这样。  
![image](https://image.3001.net/images/20210604/1622817313_60ba3a21b8a1ec07746d4.png!small)filetype：检索指定文件格式的网页。例如："filetype:txt"，搜索的结果就像下面这样。检索到的大部分都是“robots.txt”。  
![image](https://image.3001.net/images/20210604/1622817335_60ba3a377e3a000690f40.png!small)

## 运用

1.下面就是利用谷歌黑客语法“intitle:管理员登陆”所找到的一个存储型的XSS漏洞。首先进去就是管理员登陆的界面。  
![image](https://image.3001.net/images/20210604/1622817349_60ba3a45e7e2d37c07804.png!small)2.一般这种情况下都是先尝试一些常见的弱口令，如果行不通，再进行尝试暴力破解。但是呢这个站点的账号密码属实简单，一下就试出来了。进入后台。貌似是订单管理后台，用处不是很大。  
![image](https://image.3001.net/images/20210604/1622817386_60ba3a6a3b0757b832825.png!small)尝试对登录框和后台URL中的参数进行SQL注入，无果。  
3.进入网站的主页，URL中的参数也无法SQL注入。但是，有一处客户留言。一般留言的地方，要想到XSS漏洞。  
![image](https://image.3001.net/images/20210604/1622817398_60ba3a76df2f4470e6099.png!small)4.原来这里就是刚刚后台订单生成的地方。留言加入XSS漏洞验证语句，然后回到刚刚的后台。  
![image](https://image.3001.net/images/20210604/1622817418_60ba3a8a89fa6901aad14.png!small)5.成功弹窗，表明是有存储型XSS漏洞的。我是菜鸡，完结撒花，上报漏洞  
![image](https://image.3001.net/images/20210604/1622817701_60ba3ba504e8f7854941d.png!small)

XSS跨站脚本漏洞修复建议  
1、对所有输入中的script等关键字进行严格的检查。  
2、在客服端与服务端进行数据的验证。  
3、对于输出的内容，也要进行一定的过滤。对于一些特殊的符号进行编码处理。  
4、网站发布前，可以先进行漏洞测试。

