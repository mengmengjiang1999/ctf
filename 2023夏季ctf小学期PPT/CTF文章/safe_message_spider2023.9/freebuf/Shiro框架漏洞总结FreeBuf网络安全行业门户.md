
    此文为关于服务攻防中，Shiro框架漏洞的复现与总结

# Shiro框架漏洞

### shiro简介

Apache
Shiro是企业常见的JAVA安全框架，执行身份验证、授权、密码和会话管理。只要rememberMe的AES加密密钥泄露，无论shiro是什么版本都会导致反序列化漏洞

####  **Shiro框架**

Apache
Shiro™是一个强大且易用的Java安全框架,能够用于身份验证、授权、加密和会话管理。Shiro拥有易于理解的API,您可以快速、轻松地获得任何应用程序——从最小的移动应用程序到最大的网络和企业应用程序。

简而言之，Apache Shiro 是一个强大灵活的开源安全框架，可以完全处理身份验证、授权、加密和会话管理。

> 验证用户身份
>
> 用户访问权限控制，比如：1、判断用户是否分配了一定的安全角色。2、判断用户是否被授予完成某个操作的权限
>
> 在非 Web 或 EJB 容器的环境下可以任意使用Session API
>
> 可以响应认证、访问控制，或者 Session 生命周期中发生的事件
>
> 可将一个或以上用户安全数据源数据组合成一个复合的用户 “view”(视图)
>
> 支持单点登录(SSO)功能
>
> 支持提供“Remember Me”服务，获取用户关联信息而无需登录

只要RemeberMe的AES加密密钥泄露，无论shiro是什么版本都会导致反序列化漏洞。

####  **Shiro漏洞原理**

Apache
Shiro框架提供了记住我的功能（RemeberMe），用户登录成功后会生成经过加密并编码的cookie。cookie的key为RemeberMe，cookie的值是经过对相关信息进行序列化，然后使用aes加密，最后在使用base64编码处理形成的

在服务端接收cookie值时，按以下步骤解析：

> 检索RemeberMe cookie的值
>
> Base 64解码
>
> 使用ACE解密（加密密钥硬编码）
>
> 进行反序列化操作（未作过滤处理）

在调用反序列化的时候未进行任何过滤，导致可以触发远程代码执行漏洞

用户登陆成功后会生成经过加密并编码的cookie，在服务端接收cookie值后，Base64解码-->AES解密-->反序列化。攻击者只要找到AES加密的密钥，就可以构造一个恶意对象，对其进行序列化-->AES加密-->Base64编码，然后将其作为cookie的rememberMe字段发送，Shiro将rememberMe进行解密并且反序列化，最终造成反序列化漏洞。

####  **Shiro序列化利用条件**

####
由于使用了AES加密，要想成功利用漏洞则需要获取AES的加密密钥，而在shiro1.2.4之前版本中使用的是硬编码，AES加密的密钥默认在代码里。其默认密钥的base64编码后的值为
kPH+bIxk5D2deZiIxcaaaA==
，这里就可以通过构造恶意的序列化对象进行编码，加密，然后作为cookie加密发送，服务端接收后会解密并触发反序列化漏洞。

目前已经更新了很多版本，但是官方并没有把反序列化漏洞本身解决，而是通过去掉硬编码的密钥，使其每次生成一个密钥来解决该漏洞。但是，目前一些开源系统、教程范例代码都使用固定的编码，也有很多开源项目内部集成了shiro并二次开发，可能会重现低版本shiro的默认固定密钥的风险。例如Guns开源框架内部集成了shiro并进行二次开发，作者自定义密钥并固定，此时用户如果不对密钥进行修改，即使升级shiro版本，也依旧存在固定密钥的风险。这里可以通过搜索引擎和github来收集密钥，提高漏洞检测和利用的成功率。

如果反序列化对象中存在魔法函数，使用unserialize()函数同时也会触发。这样，一旦我们能够控制unserialize()入口，那么就可能引发对象注入漏洞。

####  **shiro漏洞指纹**

在请求包的Cookie中为？remeberMe字段赋任意值

返回包中存在set-Cookie：remeberMe=deleteMe

URL中有shiro字样

有时候服务器不会主动返回remeberMe=deleteMe，直接发包即可

### 本地搭建

> <https://github.com/apache/shiro/releases/tag/shiro-root-1.2.4>

下载好Java、tomcat、shiro.war，把java和tomcat安装好，然后把shiro.war放入tomcat/webapp/目录下，运行tomcat/bin/Tomcat8

![1](https://image.3001.net/images/20210808/1628422389_610fc0f535f8f03e9b4c6.png!small)

![2](https://image.3001.net/images/20210808/1628422390_610fc0f6d262e56b09ca0.png!small)

![3](https://image.3001.net/images/20210808/1628422391_610fc0f7bd49ee76da51d.png!small)

### Shiro渗透总结

#### Linux出网环境渗透Shiro反序列化漏洞

CVE-2016-4437（Apache Shiro 反序列化漏洞）

 **漏洞描述**

Apache
Shiro是一个Java安全框架，执行身份验证、授权、密码学和会话管理。只要rememberMe的AES加密密钥泄露，无论Shiro是什么版本都会导致反序列化漏洞。

 **漏洞原理**

Apache
Shiro框架提供了记住我（RememberMe）的功能，关闭了浏览器下次再打开时还是能记住你是谁，下次访问时无需再登录即可访问。Shiro对rememberMe的cookie做了加密处理，shiro在CookieRemeberMeManger类中将cookie中rememberMe字段内容分别进行序列化、AES加密、Base64编码操作。

 **原因分析：**

Apache
Shiro默认使用了CookieRememberMeManager，其处理cookie的流程是：得到rememberMe的cookie值->Base64解码->AES解密->反序列化。然而AES的密钥是硬编码的，就导致了攻击者可以构造恶意数据造成反序列化的RCE漏洞。

 **漏洞特征：**

Shiro反序列化的特征：在返回包的Set-Cookie中存在rememberMe=deleteMe字段

影响版本

影响Shiro<1.2.5版本，当未设置用于“remember me”特征的AES密钥时，存在反序列化漏洞，可远程命令执行

漏洞复现

访问靶机

192.168.27.153:8080/shiro/

![2](https://image.3001.net/images/20210808/1628422392_610fc0f8b1ee4f440d1a4.png!small)

![3](https://image.3001.net/images/20210808/1628422393_610fc0f997cdf17132974.png!small)

确认网站是apache shiro搭建的

抓包：

![4](https://image.3001.net/images/20210808/1628422394_610fc0faac427c40b43ba.png!small)

将Cookie内容改为remember Me=1，若相应包有rememberMe=deleteMe，则基本可以确定网站是apache shiro搭建的。

![6](https://image.3001.net/images/20210808/1628422396_610fc0fc07632399bd933.png!small)

运行工具找key

![8](https://image.3001.net/images/20210808/1628422397_610fc0fd33a7b12c83996.png!small)

#### Linux不出网环境渗透shiro反序列化漏洞

 **搭建环境**

docker pull medicean/vulapps:s_shiro_1

docker run -d -p 8888:8080 -p 7777:6666 medicean/vulapps:s_shiro_1

![11](https://image.3001.net/images/20210808/1628422398_610fc0fe4647d5207db99.png!small)

![9](https://image.3001.net/images/20210808/1628422399_610fc0ff57b53cdd56f76.png!small)

![10](https://image.3001.net/images/20210808/1628422400_610fc1002ddbfa1d490b8.png!small)

 **抓包验证**

同上

> windows环境渗透shiro反序列化
>
> 需要python3进行执行
>
> 分析shiro-rce脚本

判断逻辑，修改了源码的ysoserial-sleep.jar，主要对应延迟5的应用，然后去循环key和gadget，如果某个key和gadget组合以及延时命令success生效了，就是存在的，还区分两个判断windows和linux，最后在写入shell后还对发送命令进行了base64编码后发送

 **用脚本进行验证攻击**

python3 shiro-1.2.3_rce.py <http://192.168.27.153:8080/login>

![88](https://image.3001.net/images/20210808/1628422400_610fc100e3082366c0381.png!small)

![89](https://image.3001.net/images/20210808/1628422402_610fc1020a3d1afdf930b.png!small)

![90](https://image.3001.net/images/20210808/1628422403_610fc1036764ea979afcf.png!small)

#### CVE-2020-11989：Apache Shiro权限绕过复现

 **漏洞原理**

Apache Shiro
1.5.2之前版本中存在安全漏洞。攻击者可借助特制的请求利用该漏洞绕过身份验证。Shiro框架通过拦截器功能来对用户访问权限进行控制，如anon，authc等拦截器。anon为匿名拦截器，不需要登陆即可访问；authc为登录拦截器，需要登录才可以访问。Shiro的URL路径表达式为Ant格式，路径通配符表示匹配零个或多个字符串，/可以匹配/hello，但是匹配不到/hello/，如果*通配符无法匹配路径。假设/hello接口设置了authc拦截器，访问/hello会进行权限判断，但如果访问的是/hello/，那么将无法正确匹配URL，直接放行，进入到spring拦截器。spring中的/hello和/hello/形式的URL访问的资源是一样的，从而实现了权限绕过

 **影响版本**

Apache Shiro < 1.5.2

 **Shiro拦截器**

> Shiro框架通过拦截器功能来实现对用户访问权限的控制和拦截。Shiro中常见的拦截器有anon，authc等拦截器
>
> anon为匿名拦截器，不需要登录就能访问，一般用于静态资源，或者移动端接口
>
> authc为登录拦截器，需要登录认证才能访问的资源

用户可以在Shiro.ini编写匹配URL配置，将会拦截匹配的URL，并执行响应的拦截器。从而实现对URL的访问控制，URL路径表达式通常为ANT格式。如下配置，访问
/index.html 主页的时候，Shiro将不会对其进行登录判断，anon拦截器不需要登录就能进行访问。而对于 /user/xiaoming 等
/user/xiaogang 等接口，authc拦截器将会对其进行登录判断，有登录认证才能访问资源。

[urls] /index.html = anon /user/** = authc

Shiro的URL路径表达式为Ant格式，路径通配符支持？* **

？：匹配一个字符 *：匹配零个或多个字符串 * ：匹配路径中的零个或多个路径

其中表示匹配零个或多个字符串，/可以匹配/hello，但匹配不到/hello/，因为通配符无法匹配路径

假设/hello接口设置了authc拦截器，访问/hello将会被进行权限判断，如果请求的URL为/hello/，/*URL路径表达式将无法正确匹配，放行。然后进入到spring（Servlet）拦截器，spring中/hello形式和/hello/形式的URL访问的资源是一样的

> 开启漏洞环境
>
> 拉取环境

docker pull vulfocus/shiro-cve_2020_1957

![QQ截图20210804094813](https://image.3001.net/images/20210808/1628422404_610fc104bbacf70a3decf.png!small)

![91](https://image.3001.net/images/20210808/1628422406_610fc1061fa7e46982c3b.png!small)

 **开启docker**

docker run -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock -e
VUL_IP=192.168.27.180 29136b1d3c61

sudo docker ps

![92](https://image.3001.net/images/20210808/1628422407_610fc107500ba32d0c148.png!small)

 **漏洞复现**

 **访问靶机**

![93](https://image.3001.net/images/20210808/1628422408_610fc10896be07f4f880b.png!small)

<http://192.168.27.180:8080/>

需要加login

<http://192.168.27.180:8080/login>

![94](https://image.3001.net/images/20210808/1628422409_610fc109e79957604132b.png!small)

> shiro1.4.2版本权限绕过
>
> 访问 /hello/1 接口，可以看到被authc拦截器拦截了，将会跳转到登录接口进行登录：

![95](https://image.3001.net/images/20210808/1628422411_610fc10b17c05955cf362.png!small)

访问 /hello/1/ ，成功绕过authc拦截器，获取到了资源：

![96](https://image.3001.net/images/20210808/1628422412_610fc10c701069cc887c6.png!small)

> shiro<=1.5.1版本绕过

在1.5.1版本中，/hello/ 会直接跳转到登录

绕过payload： /dwdww;/../hello/1 成功绕过

![97](https://image.3001.net/images/20210808/1628422414_610fc10e04be8b03f698e.png!small)

### 总结漏洞详情

CVE-2020-13933虽然是CVE-2020-11989的绕过，然而两者的绕过内容却不同

CVE-2020-11989针对于/admin/page，这种固定路由，shiro得到的地址为 / ，因此认为可以访问，Spring得到的地址为
/admin/page ，从而定位到未授权的页面

CVE-2020-13933则是匹配非固定地址路由，比如 /admin/{name}，因为shiro得到的是
/admin/，认为可以访问，而Spring得到的是 /admin/;page，如果也采取固定路由，则会因为找不到 ;page ，从而返回404

> Apache Shiro 认证绕过漏洞（CVE-2020-1957）
>
> 漏洞简介
>
> 漏洞原理

Apache Shiro是一款开源安全框架，提供身份验证、授权、密码学和会话管理。Shiro框架直观、易用，同时也能提供健壮的安全性

在Apache Shiro 1.5.2以前的版本中，在使用Spring动态控制器时，攻击者通过构造 ..; 这样的跳转可以绕过Shiro中对目录的权限限制

> 影响版本
>
> Apache Shiro < 1.5.3
>
> 复现过程与上文一致
>
> 对shiro进行总结

总结下来就是shiro的功能用到了AES加密，但是密钥是硬编码在代码里的，所以很容易拿到密钥，因为AES是对称加密，即加密密钥也是解密密钥，所以就可以通过恶意构造Cookie获取权限执行攻击命令，拿到root权限，官方解决的方案是简单的弃用了问题代码

所以建议是升级shiro，升级到1.2.5版本及以上版本，但是可能升级了shiro版本仍然存在反序列化漏洞，其原因是因为我们使用了别人的开源框架，他们在代码里会配置shiro的密钥，如果使用了开源的框架，而没有修改shiro的密钥，其实这就相当于你使用的shiro密钥已经泄露，如果使用大量的密钥集合进行轮流尝试，是非常危险的

上述为shiro-550

shiro-721

漏洞原理：  
由于Apache Shiro cookie中通过 AES-128-CBC 模式加密的rememberMe字段存在问题，用户可通过Padding Oracle
加密生成的攻击代码来构造恶意的rememberMe字段，并重新请求网站，进行反序列化攻击，最终导致任意代码执行。  
影响版本：Apache Shiro < 1.4.2版本。

