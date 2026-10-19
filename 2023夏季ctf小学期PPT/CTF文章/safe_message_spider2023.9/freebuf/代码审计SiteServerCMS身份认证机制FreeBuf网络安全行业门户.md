##  一、前言

**SiteServerCMS是一款开源免费的企业级CMS系统，功能比较丰富，代码一多起来，难免会有些漏洞产生，之前应急响应碰到过几次这个系统，有些问题修复了，有些问题依然还在，趁着整理之前零散的资料，结合6.14.0版本写个总结。**

SiteServerCMS有多种身份认证方式，这里以最常见的Cookie认证来展开分析：

> 官网： <https://www.siteserver.cn/>
>
> Github： <https://github.com/siteserver/cms/releases>

##  二、身份认证

###  2.1 登录框

从何说起呢？渗透，经常开局就只有一个登录框，有时还有验证码，那就从登录框开始吧，SiteServerCMS是后台管理+前台内容(含会员)的前后分离模式，各有独立的登录地址，先从后台登录开始，默认后台登录地址是：

    
    
    http://IP:Port/SiteServer/pageLogin.cshtml

![](https://image.3001.net/images/20200226/1582706957_5e56310dc6e86.png!small)

随便输入个用户名和密码登录查看数据包，通过JSON格式提交到了/api/v1/administrators/actions/login，进入脱发模式，打开源码跟进，位置：

> 源文件： ./SiteServer.Web/Controllers/V1/AdministratorsController.cs

![](https://image.3001.net/images/20200226/1582706975_5e56311f2b4f9.png!small)

登录失败次数+1，出局。

###  2.2 Cookie & accessToken

使用正确的用户名密码登录，登录成功后，会生成一个accessToken的字符串，这个accessToken是作为Cookie身份认证用的：

    
    
    var accessToken = request.AdminLogin(adminInfo.UserName, isAutoLogin);

不信且看，走进AdminLogin()，跟进accessToken生成过程：

    
    
    var accessToken = AdminApi.Instance.GetAccessToken(adminInfo.Id, adminInfo.UserName, expiresAt);

源文件： ./SiteServer.CMS/Core/AuthenticatedRequest.cs

![](https://image.3001.net/images/20200226/1582706988_5e56312ce9d38.png!small)

SiteServerCMS有多种身份认证方式，这里的Constants.AuthKeyAdminCookie对应的是Cookie命名份格式：
SS+名称，规则如下：

源文件： ./SiteServer.Utils/Constants.cs

    
    
    public const string AuthKeyUserHeader = "X-SS-USER-TOKEN";
    public const string AuthKeyUserCookie = "SS-USER-TOKEN";
    public const string AuthKeyUserQuery = "userToken";
    public const string AuthKeyAdminHeader = "X-SS-ADMIN-TOKEN";
    public const string AuthKeyAdminCookie = "SS-ADMIN-TOKEN";
    public const string AuthKeyAdminQuery = "adminToken";
    public const string AuthKeyApiHeader = "X-SS-API-KEY";
    public const string AuthKeyApiCookie = "SS-API-KEY";
    public const string AuthKeyApiQuery = "apiKey";
    public const int AccessTokenExpireDays = 7;
    public static string GetSessionIdCacheKey(int userId)
    {
        return $"SESSION-ID-{userId}";
    }

回来继续跟进GetAccessToken()：

源文件： ./SiteServer.CMS/Plugin/Apis/AdminApi.cs

![](https://image.3001.net/images/20200226/1582707080_5e5631884ca43.png!small)

又回来了，继续回到上一个文件，找到那个GetAccessToken()：

![](https://image.3001.net/images/20200226/1582707101_5e56319df1a93.png!small)

还记得第三个参数类型是什么吗？
突然冒出来的WebConfigUtils.SecretKey是什么？JwtHashAlgorithm.HS256又是什么鬼？为了避免篇幅太长：

>  **WebConfigUtils.SecretKey：** 加密密钥，圈起来，要考的；
>
>  **JwtHashAlgorithm.HS256：** Hash算法模式，知道就行了。

继续跟进JsonWebToken.Encode()，直接跳过中间的方法到最后一个Encode()：

源文件： ./SiteServer.Utils/Auth/JWT.cs

![](https://image.3001.net/images/20200226/1582707114_5e5631aaf3fdf.png!small)

这里的参数对应关系：

> payload对应userToken；
>
> key对应WebConfigUtils.SecretKey；
>
> algorithm对应JwtHashAlgorithm.HS256。

然后整个accessToken生成格式为：

    
    
    算法类型 + 认证信息 + 哈希摘要
    Base64UrlEncode(headerBytes) + "." + Base64UrlEncode(payloadBytes) + "." + Base64UrlEncode(signature)

明文格式大致像这样：

    
    
    {"typ":"JWT","alg":"HS256"}.{"UserId":1,"UserName":"admin","ExpiresAt":"\/Date(1583293343684)\/"}.哈希摘要

accessToken生成完了，看完头发掉了不少，有什么用？

###  2.3 加密 & 解密

暂时还派不上用场，现在我要讲另一件事：加密与解密。

且回到AdminLogin()，登录成功后会将accessToken通过Cookie返回客户端:

    
    
    CookieUtils.SetCookie(Constants.AuthKeyAdminCookie, accessToken);

这里暂时不去理会是否isAutoLogin，捡简单的，跟进SetCookie()：

源文件： ./SiteServer.Utils/CookieUtils.cs

![](https://image.3001.net/images/20200226/1582707126_5e5631b6acaad.png!small)

注意这里有一个很关键的参数isEncrypt，缺省值是true，默认都是启用的:

> 加密： TranslateUtils.EncryptStringBySecretKey()
>
> 解密： TranslateUtils.DecryptStringBySecretKey()

且看EncryptStringBySecretKey():

源文件： ./SiteServer.Utils/TranslateUtils.cs

![](https://image.3001.net/images/20200226/1582707139_5e5631c364c23.png!small)

加密后将在字符串中的+、=、&、?、\特殊符号用0***0代替，解密前则反过来操作，然而那个SecretKey又出现了，它保存在根目录的Web.config中的appSettings节点下，是加解密的密钥，它的初始化是这样的：

源文件： ./SiteServer.Utils/WebConfigUtils.cs

![](https://image.3001.net/images/20200226/1582707150_5e5631ce99410.png!small)

SecretKey =
StringUtils.GetShortGuid();，一个16位字符串的UID，类是：6f2bc5f951826267，注意一下150行被注释掉的SecretKey值。

回到正题，跟进encryptor.DesEncrypt()加密过程：

源文件： ./SiteServer.Utils/Auth/DesEncryptor.cs

![](https://image.3001.net/images/20200226/1582707162_5e5631dac3ef0.png!small)

使用DES加密，没有指定加密模式(.Net默认是CBC模式，是不是又想到了什么？)，密钥从16位减到8位(是不是又有人想着爆破了？)，加密解密iv都是固定值：

    
    
    byte[] iv = { 0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF };

现在来梳理一下accessToken的加密过程：

    
    
    accessToken -> EncryptStringBySecretKey() -> ToBase64String() -> Replace()

用正确密码登录成功Cookie则返回像下图这么一串东西，下面为未加密的accessToken：

![](https://image.3001.net/images/20200226/1582707175_5e5631e7e0cc7.png!small)

冒着掉头发的风险又看了一大截，居然说登录还是要正确的密码? 骗子。。。

###  2.4 Cookie 认证

还没讲完，那后端是如何通过Cookie认证呢？一般都会在控制器看到这么写判断是否有权限：

    
    
    var AuthRequest = new AuthenticatedRequest();
    if (!AuthRequest.IsAdminLoggin) return;

以管理员登录为例，首先从Cookie中获取accessToken，获取流程如下：

源文件： ./SiteServer.CMS/Core/AuthenticatedRequest.cs

![](https://image.3001.net/images/20200226/1582707193_5e5631f954095.png!small)

从GetCookie()取出后，同文件AuthenticatedRequest()：

![](https://image.3001.net/images/20200226/1582707204_5e56320428cc8.png!small)

从AdminToken中获取信息做判断，还记得AdminLogin中也有个IsAdminLoggin = true;吗？

至此，通过Cookie身份认证部分讲得差不多了，普通用户的认证方式与管理员的类似，不重复了。

##  三、漏洞回顾

看起来好像没什么问题呀？一般，进入正题之前，都要先讲讲历史，如果网上搜索siteserver+漏洞关键词，你会看到模板远程GetShell、XSS/抓包绕过后台、挂马挖矿...等相关内容，而导致这些漏洞产生大多跟加密密钥泄露有关，这里分5.0版本前后，
**5.0版本之前可能没有源码，可以把.dll丢到dnSky里反编译** 。

###  3.1 文件远程下载

在讲历史之前，我先讲一个和密钥(SecretKey)有关的故事，在以前的版本，有些管理接口可能是为方便，可以匿名访问，身份认证仅依赖于系统的加密字符串，还是以v6.14.0为例，看文件：

源文件： ./SiteServer.BackgroundPages/Ajax/AjaxOtherService.cs

![](https://image.3001.net/images/20200226/1582707219_5e56321383861.png!small)

这个AJAX请求地址就是不需要权限的，而远程文件下载地址要求是 **加密字符串** ，不然没法使用，好了，故事讲完了。

###  3.2 密钥 Key

###  **在 5.0 版本之前**

这里为什么要把5.0版本作为分界线呢?
因为5.0版本之前，密钥(Cipherkey)是存在数据库的，它存在一张bairong_Config表的SettingsXML字段里，生成算法如下：

![](https://image.3001.net/images/20200226/1582707235_5e5632238330c.png!small)

一个8位随机字符串，IV也是写在源码里：

byte[] rgbIV = new byte[] { 18, 52, 86, 120, 144, 171, 205, 239 };

我们知道之前的某些版本是存在SQL注入的，利用SQL注入读取这个字段获取Cipherkey，然后就可以在加密下载链接，配合远程文件下载达到GetShell的目的。

1.x和2.x这种上古版本，年代久远就直接忽略了。

 **在 5.0 版本之后**

5.0版本之后的secretKey是存在文件里的，其中5.x版本是存在：

源文件： ./SiteFiles/Configuration/Configuration.config

secretKey是 **硬编码固定值** ： vEnfkn16t8aeaZKG3a4Gl9UUlzf4vgqU9xwh8ZV5

而6.0之后secretKey保存在Web根目录的Web.config里(随机生成)，IV和5.x一样硬编码在源码里:

byte[] iv = { 0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF };

有了secretKey和IV就可以本地去加密数据，然后 **远程下载文件GetShell** 和 **计算管理员accessToken登录后台**
，加密算法python3实现：

    
    
    def encrypt(msg, key, iv):
        pad = 8 - len(msg) % 8
        for i in range(pad):
            msg = msg + chr(pad)
        obj = DES.new(key, DES.MODE_CBC, iv)
        buf = obj.encrypt(msg)
        txt = base64.b64encode(buf).decode()
        txt = txt.replace('+','0add0').replace('=','0equals0').replace('&','0and0')
        txt = txt.replace('?','0question0').replace("'",'0quote0').replace('/','0slash0')
        txt = txt + '0secret0'  # v6.x

**注意：** 这里讲的版本划分只是大概版本，具体是哪个小版本开始是随机生成和改变存储位置，有兴趣的自个查一下。

###  3.3 Cookie 构造

前面讲到5.x版本密钥是固定的，可以用密钥构造Cookie直接登录后台，比如： **CNVD-2018-00712**
，这里不展开说了，那有没有不用密钥的呢？

开始是从登录框说起，那么就以登录框结束吧，我再讲二分钟。。。一个不用获取密钥登录后台的栗子。

还记得前面的accessToken生成过程和Cookie身份认证中所用到的参数么？是不是都没有口令参数，都只用到了UserId和UserName？

还记得前面提到的前台和后台是分离的么？也就是管理员和会员各用一张数据表。

然而数据是加密的，有啥用？

注意到前面登录成功返回那数据包没有，UserId是 **整型** 递增的。

那么，在前台注册一个用户名与后台管理员用户名一样的用户，只要使其UserId和Username相等，是不是Cookie的关键信息是一样的。

我们来打开前台会员中心试一下：

> <http://192.168.56.5:801/home/pages/login.html>

注册一个名为adzroolsmin用户，然后登录，查看Cookie：

![](https://image.3001.net/images/20200226/1582707255_5e5632373d2cd.png!small)

SS-USER-TOKEN-CLIENT是没加密的，SS-USER-TOKEN是加密的，还记得前面发送Cookie时管理员的名称是什么了吗？SS-ADMIN-TOKEN，那么，我们直接修改一下，然后访问后台管理员页面(为什么不选择直接跳转控制台主页/SiteServer/main.cshtml？那是另一个故事了)：

> <http://192.168.56.5:801/SiteServer/settings/admin.cshtml>

![](https://image.3001.net/images/20200227/1582765736_5e5716a8f4032.png!small)

直接跳进了后台管理页面，管理员ID往往是1，再多几个管理员也还是个位数，前台注册低位ID也是个迷，利用条件是不是很鸡肋，其实5.x版本里的accessToken是没有Userid这个字段的，然俄。。。

##  四、 最后

如今在身份鉴别模块能利用万能密码去登录的已不多见，更何况有着各种WAF，而今出现的身份鉴别模块的漏洞更倾向于逻辑类型，有时还需通过多种漏洞组合去利用。在平时做代码审计的时候往往需要耐心，也需要细心，很多时候两个看起来没什么问题的功能，遇到一起就擦出了火花，就像上面的Cookie构造里的栗子。

故事讲完了，下课，咱有缘再见。。。 -_-#

> 完整版脚本传送门： <https://github.com/zrools/tools/tree/master/python>

***本文原创作者：zrools，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

