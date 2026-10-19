# Writeup 1: Controllable Database Connection

本文由 **PeckShield** 漏洞研究总监 **Edward Lo** 撰写  

  

打开网站提示“Please connect to the database first” 还有一个 Connect的链接 所以应该跟数据库有关  

![图片
1.png](https://image.3001.net/images/20191028/1572257296_5db6be105ebd6.png!small)  

点击链接后发现URI 多了/#mysql.php 看来是个提示  

![图片
2.png](https://image.3001.net/images/20191028/1572257310_5db6be1e42e42.png!small)

  

访问mysql.php 提示 Error 常规套路扫一波源码  

![3.png](https://image.3001.net/images/20191028/1572257354_5db6be4a3354b.png!small)  

得到备份文件 /mysql.php.bak 获取到源码  

![4.png](https://image.3001.net/images/20191028/1572257376_5db6be6002cf4.png!small)  

发现连接地址、用户名、密码参数可控，看来考点是mysql伪造恶意服务端读取客户端文件，按照泄露的源码来看，应该是要读 /Flag.php 文件  

![5.png](https://image.3001.net/images/20191028/1572257397_5db6be7578a3f.png!small)  

通过连接自己公网开启的恶意mysql服务端读取成功读取到Flag.php 的源码  

![6.png](https://image.3001.net/images/20191028/1572257412_5db6be84b243d.png!small)  

Flag.php 是一个简单命令执行绕过，限制使用eval、assert函数和长度不得超过11位，满足以上两个条件进入eval函数执行  

![7.png](https://image.3001.net/images/20191028/1572257425_5db6be9195ded.png!small)  

我们可以使用反单引号执行命令，并通过$_GET传入我们需要执行的命令，长度刚好11个字符内  

![屏幕快照 2019-10-27
19.33.37.png](https://image.3001.net/images/20191028/1572257455_5db6beaf4f94f.png!small)  

成功反弹shell 并获取到Flag  

![8.png](https://image.3001.net/images/20191028/1572257440_5db6bea0b18f9.png!small)

  

  

Writeup 2: Unsafe Access  

  

打开网站只有一张logo和一个提示 6_79？很自然的就想到应该跟6379，redis有关  

![21.png](https://image.3001.net/images/20191028/1572257541_5db6bf05c3f4c.png!small)右键查看源码发现一个被注释的链接  

![22.png](https://image.3001.net/images/20191028/1572257566_5db6bf1eda270.png!small)  

测试发现此接口存在SSRF漏洞  

![23.png](https://image.3001.net/images/20191028/1572257586_5db6bf323ea90.png!small)  

扫描备份文件获取到link.php的源码，只是简单的进行了一些过滤，限制了gopher和127、localhost 等字符  

![24.png](https://image.3001.net/images/20191028/1572257611_5db6bf4bc8e7e.png!small)  

联系首页的6_79提示，看来这题是常规的SSRF配合Redis拿Flag。使用dict协议写入redis、使用0
代表当前IP或域名解析等方式即可绕过访问本地限制。尝试反弹或者写私钥，均没有成功应该是权限过低的原因，于是尝试写webshell，成功写入恶意代码，获取到Flag。  

写入恶意代码：（<? 等特殊符号需要转义，不然问号后面会导致截断无法写入）  

![26.png](https://image.3001.net/images/20191028/1572257664_5db6bf80c5919.png!small)设置保存路径：  

![27.png](https://image.3001.net/images/20191028/1572257707_5db6bfab4edd7.png!small)

设置保存名字：  

![28.png](https://image.3001.net/images/20191028/1572257716_5db6bfb46ec73.png!small)

保存：  

![29.png](https://image.3001.net/images/20191028/1572257724_5db6bfbc7dfc7.png!small)  

成功写入  

![25.png](https://image.3001.net/images/20191028/1572257650_5db6bf7261225.png!small)  

  

  

