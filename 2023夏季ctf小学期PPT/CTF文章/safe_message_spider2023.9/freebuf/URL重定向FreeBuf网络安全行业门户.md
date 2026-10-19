# ****1\. URL重定向****

 ** **1.1 什么是URL重定向****

url重定向漏洞也称url任意跳转漏洞，网站信任了用户的输入导致恶意攻击，url重定向主要用来钓鱼，比如url跳转中最常见的跳转在登陆口，支付口，也就是一旦登陆将会跳转任意自己构造的网站，如果设置成自己的url则会造成钓鱼。

###  ** **1.2 利用场景****

此处举例说明，不表示以下为全部利用场景

登陆跳转 （最为常见）

用户分享跳转

跨站点认证、授权后，会跳转

用户交互页面如评价完成后跳转界面

业务完成后跳转

常见可疑参数

### redirect  
url  
redirectUrl  
callback  
return_url  
toUrl  
ReturnUrl  
fromUrl  
redUrl  
request  
redirect_to  
redirect_url  
jump  
jump_to  
target  
to  
goto  
link  
linkto  
domain  
oauth_callback

##  ** **1.3 如何攻击与绕过****

一般在测试过程主需要让测试站点跳转到第三方站点即可证明危害

一般POST跳转不算在范围内，主要看GET型跳转

常见跳转格式为

 ** **完整URL型****

http://www.a.com/login.html?url=http://www.b.com

这种类型在没有限制的情况下可以直接替换发生跳转  
但可能遇到存在限制的情况，可以通过以下方式进行绕过:

1、@  
http://www.a.com/login.html?url=http://www.a.com@b.com  
2、\  
http://www.a.com/login.html?url=http://www.b.com\a.com  
3、\  
http://www.a.com/login.html?url=http://www.b.com\\\a.com  
4、？  
http://www.a.com/login.html?url=http://www.b.com?a.com  
5、#  
http://www.a.com/login.html?url=http://www.b.com#a.com

 ** **路径型：****

http://www.a.com/login.html?url=/home

这种类型只能尝试@绕过  
在部分场景中遇到过站点会将域名和路径进行拼接保存到JS中

http://www.a.com/login.html?url=@b.com

拼接后可以查看到为

http://www.a.com@b.com

###  ** **1.4 漏洞危害提升****

在测试过程中也许只是遇到跳转，绕过跳转就结束了这个漏洞的测试。  
但在部分情况下，可能由于URL跳转造成更严重的安全问题。

举例说明：

此处发现存在一处URL跳转

![1647227341_622eb1cdb48bfdd45421b.png!small?1647227342021](https://image.3001.net/images/20220314/1647227341_622eb1cdb48bfdd45421b.png!small?1647227342021)

后续观察后发现会将url和token拼接进行身份确认

![1647227346_622eb1d21f24f2e3988f5.png!small?1647227346345](https://image.3001.net/images/20220314/1647227346_622eb1d21f24f2e3988f5.png!small?1647227346345)

那么后续将URL替换成我们自己监听的地址也能获取到JWT

![1647227351_622eb1d76d654de98aab7.png!small?1647227351974](https://image.3001.net/images/20220314/1647227351_622eb1d76d654de98aab7.png!small?1647227351974)

jwt可以直接使用

![1647227355_622eb1dbbfd418c417b1f.png!small?1647227356291](https://image.3001.net/images/20220314/1647227355_622eb1dbbfd418c417b1f.png!small?1647227356291)

  

正常URL跳转可能直接造成危害不大，但此处结合开发中错误的身份验证方式使这个漏洞危害等级从中危提高到了严重所以在日常渗透过程中需要仔细观察前后的参数、数据包，可能会发现意外收获。

###  ** **1.5 漏洞防御****

1、不应从用户请求或填写的内容中获取跳转的目标URL，应在后端设定跳转URL。

2、 对需要跳转的目标URL进行验证，如果跳转的URL不是所允许的，则禁止跳转。

3、进行URL时提示用户并显示跳转的目标URL地址并询问是否跳转。

4、对如@、#、\、\\\、？等符号进行过滤。

