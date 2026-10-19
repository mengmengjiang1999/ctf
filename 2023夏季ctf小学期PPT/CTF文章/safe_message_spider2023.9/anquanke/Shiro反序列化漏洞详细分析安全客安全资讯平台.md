# Shiro反序列化漏洞详细分析

阅读量 **328583**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-25 15:30:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01227c4ffb96025ab7.jpg)

## 0x00 前言

上次讲了最近的shiro权限绕过的漏洞，这次来补充分析一下以前的shiro-550反序列化漏洞。另外学习了shiro-550也可以更好地理解shiro-721漏洞，也就是Shiro
Padding Oracle Attack。所以这次就详细地看下shiro反序列化漏洞。

## 0x01 shiro-550介绍

shiro-550（shiro小于1.2.5）主要是由shiro的rememberMe内容反序列化导致的命令执行漏洞，造成的原因是AES密钥被硬编码在shiro源码中，这就导致了可以通过在cookie的rememberMe字段插入payload实现任意代码执行。在这以后shiro使用随机密钥，而不再硬编码，这又造成padding
oracle attack导致的shiro-721。

## 0x02 动态详细分析

###  一、环境搭建

1.首先下载shiro-root-1.2.4，部署到IDEA

2.然后修改一下依赖文件

    
    
    <dependencies>
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>jstl</artifactId>
            <!--  这里需要将jstl设置为1.2 -->
            <version>1.2</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-collections4</artifactId>
            <version>4.0</version>
        </dependency>
    <dependencies>
    

3.用IDEA内置tomcat部署即可

![](https://p3.ssl.qhimg.com/t017ab6eef1e49e0cdc.png)

###  二、加密分析

我们进入登陆页面，输入后准备登录

![](https://p0.ssl.qhimg.com/t01c09eff2a97347912.png)

在登陆前我们先在AbstractShiroFilter.class#doFilterInternal下断点，登陆时会断到这里。在第158行this.createSubject(request,
response)这里，会创建subject，并使用cookie等信息，在解密时会进行分析

![](https://p1.ssl.qhimg.com/t01201979d779800a75.png)

我们步入executeChain(request, response,
chain)后，再单步步入doFilter、InternaldoFilter等等后，最后可以进入到AuthenticatingFilter#executeLogin，用来处理登录

![](https://p3.ssl.qhimg.com/t01bb868cdd9fdb89d5.png)

再单步步入33行login函数，经过相关判断后，登陆成功，我们来到this.onSuccessfulLogin(token, info, loggedIn)

![](https://p2.ssl.qhimg.com/t01de5a7b00b44dcabb.png)

单步步入onSuccessfulLogin函数，继续步入rememberMeSuccessfulLogin函数

![](https://p4.ssl.qhimg.com/t01e591dc2b5305709b.png)

在获取到RememberMeManager不为空后，步入AbstractRememberMeManager#onSuccessfulLogin

![](https://p2.ssl.qhimg.com/t01a5265fe9da13f021.png)

我们跟进forgetIdentity函数，发现它处理了request和response请求

![](https://p3.ssl.qhimg.com/t01f5cb601db3568552.png)

继续步入this.forgetIdentity(request,
response)后单步步入this.getCookie().removeFrom(request,
response)，获取了配置信息包括rememberMe字段和deleteMe字段，并用addCookieHeader()添加到cookie中

![](https://p1.ssl.qhimg.com/t01cd501481e3073cac.png)

之后返回到AbstractRememberMeManager#onSuccessfulLogin。this.isRememberMe(token)检查是否选中登陆时Remember
Me选项，之后我们一直单步步入rememberIdentity

![](https://p4.ssl.qhimg.com/t01765f12a13f315890.png)

最后到达这里

![](https://p5.ssl.qhimg.com/t01d9266234249f51bd.png)

第一个函数就是转为bytes，我们跟进convertPrincipalsToBytes函数后发现首先将进行序列化，之后由this.getCipherService()获取到加密服务方式不为空后，进入this.encrypt(bytes)阶段

![](https://p5.ssl.qhimg.com/t016b63630962686959.png)

我们单步步入encrypt函数。在其中首先获取密码服务为AES/CBC/PKCS5Padding，之后进入this.getEncryptionCipherKey()

![](https://p1.ssl.qhimg.com/t01e8e0313523ccb9d2.png)

![](https://p5.ssl.qhimg.com/t017fde90580d12ab5d.png)

单步步入后，最后可以发现CipherKey就是AbstractRememberMeManager.class开头的DEFAULT_CIPHER_KEY_BYTES=”kPH+bIxk5D2deZiIxcaaaA==”

![](https://p3.ssl.qhimg.com/t01c76fab3748884107.png)

获取CipherKey返回后进入cipherService.encrypt函数中，生成初始化向量ivBytes后，进入具体的加密函数，最后return

![](https://p0.ssl.qhimg.com/t01268fb51aef5a9d07.png)

一步步return
bytes后，回到rememberIdentity函数，下面的rememberSerializedIdentity实现了记住序列化身份的功能，跟进

![](https://p4.ssl.qhimg.com/t0118a0ab67988634e8.png)

在rememberSerializedIdentity里面，进行base64后，将信息加入到cookie中

![](https://p1.ssl.qhimg.com/t014c8c61ae148566e2.png)

之后就层层返回，直到AuthenticatingFilter#executeLogin处理登录，返回成功登陆

![](https://p0.ssl.qhimg.com/t01f83060851b4a3abb.png)

###  三、解密分析

与加密类似，直接在AbstractShiroFilter.class#doFilterInternal下断点，然后单步到DefaultSecurityManager#createSubject

![](https://p0.ssl.qhimg.com/t012723ace8b0dab41e.png)

单步到resolvePrincipals函数后，继续单步到getRememberedIdentity函数，在其中获取RememberMeManager后进入rmm.getRememberedPrincipals(subjectContext)

![](https://p0.ssl.qhimg.com/t0122e24c925b42ad5d.png)

我们分别步入其中两个函数看看

![](https://p2.ssl.qhimg.com/t01682c402a147aaf83.png)

在第一个函数getRememberedSerializedIdentity中，先获取cookie中的值，然后base64解密，生成二进制数后返回

![](https://p3.ssl.qhimg.com/t0120247bf8a6634eec.png)

第二个函数convertBytesToPrincipals中，先获取解密服务不为空后，将二进制数据传入decrypt函数进行解密，之后return
this.deserialize(bytes)

![](https://p5.ssl.qhimg.com/t017bc60c8de69b28f8.png)

在deserialize(bytes)中有readObject()，触发apache.commons利用链漏洞

![](https://p1.ssl.qhimg.com/t0140fe5e450a3ff91c.png)

## 0x03 小结和修复

加密时：序列化转为二进制、encrypt加密、base64加密、放入cookie

解密时：从cookie中取出、base64解密、decrypt解密、反序列化

在利用时，可以根据硬编码在源码中的key构造payload。

修复：升级到最新的shiro、过滤cookie中较长的rememberMe等。CipherKey不要泄露。

## 0x04 结语

通过这次的分析，可以详细了解到shiro反序列化的过程，加深了对利用方式的思考和记忆。除了shiro-550以外的shiro-721则主要是关于AES-128-CBC模式加密的利用，有兴趣可以继续学习。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zzZ** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/228889](/post/id/228889)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [shiro](/tag/shiro)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t0177bde109b464d6d4.png) zzZ

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

