## 前言

在前面说了好几种域内的攻击手法，可是发现这些方法总是存在各种限制。那么今天在介绍一个漏洞，好消息是该漏洞的危害很大并且利用简单，只要存在相当于就拿到域管理员的权限；坏消息就是这是14年的漏洞，现在已经不多见了，多数产生在windowsserver
2008和windows server 2003的域环境中。

接下来还是一起来看看这个漏洞。

这是内网方面的第六篇文章，关于内网前面的几篇文章如下，大家感兴趣的可以去看看：

[内网渗透：Kerberos认证协议安全性分析](https://www.freebuf.com/articles/network/371028.html)

[内网横移：抓取域管理员密码](https://www.freebuf.com/articles/web/370338.html)

[内网渗透：详解kerberoast攻击](https://www.freebuf.com/articles/network/371446.html)

[内网渗透：详解Responder利用方式](https://www.freebuf.com/articles/network/371863.html)

[内网渗透：NTML认证与PTH攻击](https://www.freebuf.com/articles/network/372482.html)

另外，我在freebug的知识大陆建立了一个帮会，现在免费加入，会不断更新相关的文章，欢迎大家加入帮会，共同探讨。

帮会名称：安全防线

  

## 漏洞原理

这个漏洞还是在kerberos的认证过程中发生的，那么我们还有必要简要的回顾一下kerberos的认证协议。下面就是kerberos的认证流程图。

![1690012013_64bb896dbaf6450069271.png!small?1690012014722](https://image.3001.net/images/20230722/1690012013_64bb896dbaf6450069271.png!small?1690012014722)

 **我们知道在Kerberos最初的设计的流程里只说了如何证明客户端的真实身份, 并没有说明客户端是否有权限访问该服务,因为在域中不同的权限的用户
能够访问的资源是不同的,因此微软为了解决这个权限为题引入了PAC（特权属性证书）。**

 **引入PAC以后** ,在AS REP阶段返回的TGT中会包含PAC，TGS
REQ阶段中client将带有PAC的TGT发送给KDC，KDC除了验证TGT的合法性以外，还会验证PAC的合法性，如果两者都验证通过，再重新构造新的PAC放在ST里返回给客户端，client带着这个pac去请求服务，服务会根据PAC中的user
id和group id来判断client具有的权限。

需要注意:

 **TGS-REP中KDC并不会验证客户端是否有权限访问服务端,因此不管用户有没有访问 服务的权限,只要TGT正确,均会返回ST。**

## PAC组成部分

 **PAC主要有两个部分组成，一个是用户信息，一个是两个数字签名。**

用户信息：Client的User的SID、Group的SID等信息。根据用户信息去判断权限

数字签名：这两个签名的作用是确保PAC不被篡改

 **1.PAC_SERVER_CHECKSUM**

PAC_SERVER_CHECKSUM是使用服务密钥进行签名

 **2.PAC_PRIVSVR_CHECKSUM**

PAC_PRIVSVR_CHECKSUM是使用KDC密钥进行签名

看了上面的流程，我们了解到server是根据PAC的里面的内容来确认权限的。那么如果PAC的内容可以进行伪造，那么我们是不是就可以伪造任意权限的用户了？

在研究PAC的过程中，发现了生成PAC具有下面的特征：

1.在AS_REQ阶段有一个参数include-PAC，将该参数设置为False时，则返回TGT中不会包含PAC

![1690012108_64bb89ccd954ad4f007fc.png!small?1690012109526](https://image.3001.net/images/20230722/1690012108_64bb89ccd954ad4f007fc.png!small?1690012109526)

2. **PAC中的数字签名可以由Client端指定，并且Key的值可以为空** ；（KDC对PAC进行验证时，对于PAC尾部的签名算法，虽然原理上规定必须是带有Key的签名算法才可以，但微软在实现上，却允许任意签名算法，只要客户端指定任意签名算法，KDC服务器就会使用指定的算法进行签名验证。因此伪造的任意内容都可以是合法的，直接加上内容的MD5值作为签名即可）

3.我们没有办法修改返回的TGT，因此我们只能把PAC放到数据包中其它地方，但是 PAC没有被放在TGT中，放在其它地方。
**KDC在仍然能够正确解析出没有放在TGT中的PAC信息。**
PAC必须是密文，经过Key加密的KDC会从Authenticator中取出来subkey，把PAC信息解密并利用客户端设定的签名算法验证签名

4.将我们生成的PAC放到数据包中发送给KDC，KDC在验证PAC通过以后，KDC把PAC中的User SID、Group
SID取出来，重新使用进行签名，签名算法和密钥与设置inclue-pac标志位为TRUE时一模一样。将新产生的PAC加入到解密后的TGT中，
**再重新加密制作全新的TGT发送给Client，不是ST**

 **根据上面的特征，我们发现可以伪造PAC** 。下面为其流程：

1.我们发送AS_REQ时将数据包中的include-PAC修改为False。

2.指定PAC的加密算法和密钥并将pac中的权限改为管理员权限，生成PAC

3.将PAC添加到数据包中发送KDC验证

4.KDC验证通过以后 **生成一个正常的TGT并返回给客户端**

5.到此，我们拿到了高权限的TGT，将其导入内存中，我们就可以使用这个TGT去申请服务票据。

## 漏洞利用

接下来我们实际验证一下

### 利用条件

1.拿下一台加入域的机器并且具有管理员权限

2.域控没有打MS14-068的补丁(KB3011780)

3.有这台域内计算机的域用户密码和sid

### 利用工具

Ms14-068.exe
下载地址:<https://github.com/abatchy17/WindowsExploits/tree/master/MS14-068>

mimikatz

### 漏洞利用

前提我们已经拿到了域控的机器并且有管理员权限，并且已经拿到这个用户的密码。

关于如何抓取用户的密码，可以看另外一篇文章：[内网横移：抓取域管理员密码](https://www.freebuf.com/articles/web/370338.html)

首先通过 whoami /user获取sid

![1690012249_64bb8a590799594ef96ff.png!small?1690012249609](https://image.3001.net/images/20230722/1690012249_64bb8a590799594ef96ff.png!small?1690012249609)

现在我们已经获得了所需的所有条件，接下来用ms14-068工具生成伪造的kerberos协议认证证书

ms-14-068.exe -u 域用户@域控名 -p 域用户密码 -s 域用户sid -d 域ip

参数说明：

-u 域账号+@+域名称，这里是ts1+@+yunying.lab

-p 为当前用户的密码，即ts1的密码

-s为ts1的SID值，可以通过whoami/all来获取用户的SID值

-d为当前域的域控

![1690012263_64bb8a6724d8c33d6154f.png!small?1690012264290](https://image.3001.net/images/20230722/1690012263_64bb8a6724d8c33d6154f.png!small?1690012264290)

获取到TGT文件以后，用mimikatz.exe将证书写入，从而提升为域管理员。

kerberos::ptc 证明名字

![1690012268_64bb8a6c5a94102477ea3.png!small?1690012269069](https://image.3001.net/images/20230722/1690012268_64bb8a6c5a94102477ea3.png!small?1690012269069)

写入成功就可以直接以域管理员的权限去访问服务

![1690012282_64bb8a7a8e72578d62cbc.png!small?1690012283475](https://image.3001.net/images/20230722/1690012282_64bb8a7a8e72578d62cbc.png!small?1690012283475)

上面就是整个的利用过程。

## 总结

MS14-068这个漏洞是非常严重的，只要存在可以说就相当于拿到了域控的权限，只不过现在已经不多见了。万一遇见了呢，所以还是非常有必要去了解一下的。

 **由于本人水平有限，文章中可能会出现一些错误，欢迎各位大佬指正，感激不尽。如果有什么好的想法也欢迎交流~~**

## 参考链接

<https://www.cnblogs.com/feizianquan/p/11760564.html>

[https://blog.csdn.net/lhh134/article/details/104139081﻿](https://blog.csdn.net/lhh134/article/details/104139081)

