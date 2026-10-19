## 什么是shiro?

shiro是apache的一个开源框架，是一个 **权限管理框架**
，可以帮助开发者完成：认证、授权、加密、会话管理与web集成、缓存等。基本功能点如下图：（图来自w3cschool）

![1654678054_62a0622634db0bc5f79c4.png!small?1654678055051](https://image.3001.net/images/20220608/1654678054_62a0622634db0bc5f79c4.png!small?1654678055051)

> Authentication：身份认证 / 登录，验证用户是不是拥有相应的身份；  
>
> Authorization：授权，即权限验证，验证某个已认证的用户是否拥有某个权限；即判断用户是否能做事情，常见的如：验证某个用户是否拥有某个角色。或者细粒度的验证某个用户对某个资源是否具有某个权限；  
> Session Management：会话管理，即用户登录后就是一次会话，在没有退出之前，它的所有信息都在会话中；会话可以是普通 JavaSE
> 环境的，也可以是如 Web 环境的；  
> Cryptography：加密，保护数据的安全性，如密码加密存储到数据库，而不是明文存储；  
> Web Support：Web 支持，可以非常容易的集成到 Web 环境；  
> Caching：缓存，比如用户登录后，其用户信息、拥有的角色 / 权限不必每次去查，这样可以提高效率；  
> Concurrency：shiro 支持多线程应用的并发验证，即如在一个线程中开启另一个线程，能把权限自动传播过去；  
> Testing：提供测试支持；  
> Run As：允许一个用户假装为另一个用户（如果他们允许）的身份进行访问；  
>  **RememberMe：记住我，这个是非常常见的功能，即一次登录后，下次再来的话不用登录了。**

## Apache Shiro 1.2.4反序列化漏洞（CVE-2016-4437/shiro-550）

Apache Shiro
1.2.4及以前版本中，shiro提供了rememberMe的功能，加密的用户信息序列化后存储在名为rememberme的Cookie中，服务器端对rememberMe中的cookie依次进行
**base64解密、AES解密和反序列化** 得到cookie的值对用户进行认证。

但在这个过程中，由于Shiro的密钥默认硬编码在代码中，所以攻击者可以 **以序列化、AES加密、base64编码**
的顺序伪造用户Cookie，将恶意代码放入cookie，服务器端解析后就会触发Java反序列化漏洞，进而在目标机器上执行任意命令。

###  **怎么判断网站是不是用了shiro?**

使用了shiro的网站中， **url中可能会有shiro** ，或者 **request包的cookie中含有rememberMe字段** ，r
**esponse包中包含set-cookie:rememberMe=deleteMe**
，但有时服务器不会主动返回rememberMe=deleteMe，而是直接通信就行，此时将request包中的cookie内容改成rememberMe=1，如果response包中有rememberMe=seleteMe，那么网站用了shiro。

可以使用的工具：[BurpShiroPassiveScan](https://github.com/pmiaowu/BurpShiroPassiveScan)，是一个burpsuite的扩展插件，对burp传进来的每个不同的域名加端口的流量进行一次shiro框架的指纹识别，同时也有shiro的密钥检测功能。

###  **shiro的密钥获取方式**

最重要的是拿到AES的密钥

在1.2.4版本之前，shiro中使用默认AES密钥(CBC模式)，硬编码的key为经过base64编码后的kPH+bIxk5D2deZiIxcaaaA==，使用时要先base64解码。

在1.2.4版本之后，修复为自定义AES密钥(CBC模式)，这时需要获取到key才可以开始渗透，可以通过google、github进行搜索来收集常用的github中的key值。

可以使用的工具：

shiro_exploit 和 shiro_attack

shiro_exploit是用python写的，[搁这呢](https://github.com/insightglacier/Shiro_exploit)，示例：python
shiro_exploit.py -u <http://192.168.100.30:8081>  

以及超超超好用的[shiro_attack](https://blog.csdn.net/Fighting_hawk/article/details/125562498#1__1)，下载下来直接使用就行

![1663988070_632e71662cf86ed5f632f.png!small?1663988069771](https://image.3001.net/images/20220924/1663988070_632e71662cf86ed5f632f.png!small?1663988069771)

###  **漏洞复现**

靶场选择[vulfocus](https://vulfocus.cn/#/dashboard)，选择其中的CVE-2016-4437靶场

![1663988451_632e72e33f61009f2ab6b.png!small?1663988450623](https://image.3001.net/images/20220924/1663988451_632e72e33f61009f2ab6b.png!small?1663988450623)

![1663988914_632e74b2c9c482d633ad3.png!small?1663988914239](https://image.3001.net/images/20220924/1663988914_632e74b2c9c482d633ad3.png!small?1663988914239)

![1663988960_632e74e098447986eff48.png!small?1663988959935](https://image.3001.net/images/20220924/1663988960_632e74e098447986eff48.png!small?1663988959935)

request包中发现rememberMe:

![1663989007_632e750f028508f364306.png!small?1663989006334](https://image.3001.net/images/20220924/1663989007_632e750f028508f364306.png!small?1663989006334)

使用shiro_attack发现存在默认密钥和攻击链：

![1663989343_632e765f96d611805933c.png!small?1663989343028](https://image.3001.net/images/20220924/1663989343_632e765f96d611805933c.png!small?1663989343028)

成功远程命令执行：

![1663989361_632e7671cf9103d2f62fd.png!small?1663989361232](https://image.3001.net/images/20220924/1663989361_632e7671cf9103d2f62fd.png!small?1663989361232)

## Apache Shiro 1.4.2Padding Oracle Attack(CVE-2019-12422/shiro-721)

### 漏洞简介

上面提到的shiro550漏洞是因为shiro1.2.4及以前的版本中存在默认密钥，当使用默认密钥进行rememberMe字段加密传输后，服务器端会反序列化rememberMe字段的值并进行执行，这使得攻击者可以构造恶意的rememberMe值造成远程代码执行。

shiro-721则是1.4.2之前版本中存在的漏洞，是由于shiro
cookie中通过AES-128-CBC模式加密的rememberMe字段存在问题，用户通过Padding
Oracle攻击生成的攻击代码来构造恶意的rememberMe字段，造成任意代码执行。

【shiro-721攻击的前提是先登录后台获取一个合法cookie】

>  **什么是padding oracle?**
>
>
> padding表示填充，oracle表示提示(不是甲骨文哈)，在解密的时候，如果算法发现解密后数据的填充方式不符合规则，那么就表示输入数据有问题，那么解密的类库就会抛出一个异常，提示输入数据的padding不对。
>
> shiro中出现padding oracle漏洞的是CBC加密模式，CBC加密模式是密码学5种加密模式中的一种(ECB、 **CBC**
> 、CFB、OFB、CTR)，意思是密码块链模式(Cipher Block
> Chaining)，简单来说就是在加密之前会设置一个初始向量IV，IV先与第一个明文分组异或，然后使用密钥加密得到第一个分组的密文，然后依次将每一个明文分组与前一个分组的密文进行异或后再进行密钥加密。由于CBC有一个随机的初始变量，那么相同的明文每次经过CBC加密模式的加密结果是不同的，但是CBC存在设计缺陷，造成padding
> oracle攻击。
>
>
> **【漏洞点：客户端发送加密数据，服务器端会解密数据，然后进行一个回显，反映解密成功与否。服务器的回显总归是有些危险的，我们可以以回显差异来判断我们的输入是否正确，这也是padding
> oracle攻击的利用点。】**
>
>
> 以AES/DES为例，AES的分组长度为128bit(16字节)，DES每块为8个字节，但并不是每一段明文都可以刚好被16或8整除，那么就需要用到一些强制措施将明文补充到16或8的倍数，最直接的就是直接填充(padding)。
>
>
> 那么怎么才能有意义的填充？CBC模式的设计者就考虑到这个问题，以DES为例，假设DES按8个字节分为明文分组，那么CBC的填充方法就是缺了1位(即明文7个字节)就填一个0x01，缺了2位(即明文6个字节)就填2个0x02，缺了3位就填3个0x03......需要注意的是即使明文正好是分组的整数倍，也会再填充8个0x08。服务器端在解密的时候，其实就是加密过程反过来。
>
>  **加密流程**
> ：iv初始向量异或第一组明文->用密钥加密第一组明文->上一组密文和当前明文异或->......->最后一个明文分组缺n位就填充n位0x0n。
>
>  **解密流程**
> ：解密密文的第一分组->解密得到iv和第一段明文异或的结果(中间值)->中间值和iv再异或一次就得到了第一组的明文->......直到解密完最后一组密文。
>
> 这个时候按理说服务器端会将解密后的数据交给业务逻辑进行后续的判断执行，但是 **实际上中间还有一个步骤，程序会判断明文最后的填充位是否正确**
> 。这个判断本身没有问题，反而可以过滤掉一些错误的、被恶意篡改的加密数据，但是判断出明文最后的一个分组的填充位是错误的之后，返回给客户端的信息，会被攻击者利用。
>
> a. 如果密文解密成明文后，填充位判断正确，而且经过业务逻辑代码的校验后，也是正确，那么服务端会返回200的状态码。
>
> b. 如果密文解密成明文后，填充位判断正确，但是业务逻辑判断不通过，也就是说这个明文有问题，那么服务端会返回200或者300等状态码。
>
> c. 如果密文解密成明文后，填充位判断不正确，就会返回500等状态码。
>
> 总结起来就是，明文填充位的正确与否，服务器端返回的状态码不一样，padding oracle正是通过这一点进行漏洞利用。
>
> 例子及详细分析可以看看[这篇文章](http://blog.topsec.com.cn/padding-> oracle%E5%8E%9F%E7%90%86%E6%B7%B1%E5%BA%A6%E8%A7%A3%E6%9E%90/)，来自
> **天融信阿尔法实验室**

### 漏洞复现

利用条件：已经拥有已登录用户的合法cookie，并且目标服务器含有可利用的攻击链。

影响版本：< 1.4.2

利用工具：[ysoserial](https://github.com/frohoff/ysoserial/releases/tag/v0.0.6)、shiro
721的exp [shiro_exp](https://github.com/inspiringz/Shiro-721)  

靶场：vulfocus shiro-721

![1666319559_635204c72a7e5c3624c61.png!small?1666319559673](https://image.3001.net/images/20221021/1666319559_635204c72a7e5c3624c61.png!small?1666319559673)

![1666319544_635204b8484e6e06c81fd.png!small?1666319544835](https://image.3001.net/images/20221021/1666319544_635204b8484e6e06c81fd.png!small?1666319544835)

先用给出的账户密码登录，然后选择rememberMe，抓包得到cookie

![1666319725_6352056d2af055e1605b7.png!small?1666319725822](https://image.3001.net/images/20221021/1666319725_6352056d2af055e1605b7.png!small?1666319725822)

rememberMe字段复制下来输入到工具中进行利用

java -jar ysoserial.jar CommonsBeanutils1 "ls /tmp" > payload.class

![1666321948_63520e1ccdccfe0eb335a.png!small?1666321949208](https://image.3001.net/images/20221021/1666321948_63520e1ccdccfe0eb335a.png!small?1666321949208)

python shiro_exp.py http://192.168.171.137:8080/login.jsp **rememberMe字段**
payload.class

![1666322282_63520f6a1334b09d6def9.png!small?1666322282536](https://image.3001.net/images/20221021/1666322282_63520f6a1334b09d6def9.png!small?1666322282536)

最后会生成恶意的rememberMe cookie，我们使用这个cookie替换原数据包中的cookie，得到flag **（并没有，爆破时间太久了）**

![1666322234_63520f3ae15b923e26d12.png!small](https://image.3001.net/images/20221021/1666322234_63520f3ae15b923e26d12.png!small)

（爆破不太出来阿巴阿巴阿巴，这个图rememberMe字段和上面不一样因为靶场过期了重开了......但是思想是对的，真实环境下版本号在1.4.2下的话可以尝试......）

 **大无语事件: 后来发现这个靶场不太对，可以直接用默认密钥打**

![1666321618_63520cd2b5e9327e209c1.png!small?1666321619197](https://image.3001.net/images/20221021/1666321618_63520cd2b5e9327e209c1.png!small?1666321619197)

![1666321661_63520cfda0e494f930e69.png!small?1666321662044](https://image.3001.net/images/20221021/1666321661_63520cfda0e494f930e69.png!small?1666321662044)

好吧，721的爆破时间还是比较长的，有时间有授权的话可以在真实环境下试试......

## Apache Shiro 认证绕过漏洞 (CVE-2020-1957)

### 漏洞简介

这里涉及到shiro和spring各自的拦截器对于URI模式匹配的差异。

（1）在shiro中，shiro框架通过拦截器功能来对用户访问权限进行控制和拦截，如anon, authc等拦截器。

> anon为匿名拦截器，不需要登录即可访问，一般用来访问静态资源、移动端接口；
>
> authc为登录拦截器，用于需要登录才可以访问的资源。
>
>
> 用户可以在Shiro.ini编写匹配URL配置，将会拦截匹配的URL，并执行响应的拦截器。从而实现对URL的访问控制，URL路径表达式通常为ANT格式。如采用”[urls]
> /index.html = anon /user/** = authc“的配置，访问
> /index.html主页的时候，Shiro将不会对其进行登录判断，anon拦截器不需要登录就能进行访问。而对于/user/root
> 等接口，authc拦截器将会对其进行登录判断，有登录认证才能访问资源。
>
> ShiroConfig文件是shiro的核心配置类，里面配置哪些路径需要登录才能访问，如
>
>  **authMap.put("/user/*","authc")**
>
>  **authMap.put("/admin/*","authc")**
>
>  **......**
>
>  
>
>
> 且Shiro的URL路径表达式为Ant 格式，路径通配符支持 ? * ** 。
>
> ?：匹配一个字符
>
> *：匹配零个或多个字符串
>
> **：匹配路径中的零个或多个路径

以上可知，shiro中路径检查的时候，*表示匹配零个或多个字符串，/*可以匹配/hello，但匹配不到/hello/，因为*通配符无法匹配路径。
**假设/hello接口设置了authc拦截器，访问/hello将会被进行权限判断，但是如果请求的URI为/hello/，/*
表达式将无法正确匹配，会执行放行操作，进入spring。**

（2）在spring(Servlet)拦截器中，spring中/hello 形式和/hello/形式的URL访问的资源是一样的。

简单来说就是，/aa/bb和/aa/bb/在shiro的处理中被看成两个不同的路径；
**但是spring中，/aa/bb/和/aa/bb都会被视为aa/bb进行资源访问**
。那么在spring集成shiro的时候，如果在路径后面添加/，就可以绕过shiro的拦截器检查，访问本不被允许访问的资源，造成越权访问。

### 漏洞复现

利用版本：shiro<1.5.2

漏洞靶场：vulfocus shiro cve-2020-1957

![1666341213_6352595dddead7fee0483.png!small?1666341214133](https://image.3001.net/images/20221021/1666341213_6352595dddead7fee0483.png!small?1666341214133)

![1666341244_6352597c01709eb6f5a39.png!small?1666341244273](https://image.3001.net/images/20221021/1666341244_6352597c01709eb6f5a39.png!small?1666341244273)

漏洞复现：

![1666339998_6352549e400f0eba06622.png!small?1666339998573](https://image.3001.net/images/20221021/1666339998_6352549e400f0eba06622.png!small?1666339998573)

当我们直接在url后面拼接/hello/1的时候，靶场要求我们登录：

![1666340560_635256d07c96f3dcaed90.png!small?1666340560760](https://image.3001.net/images/20221021/1666340560_635256d07c96f3dcaed90.png!small?1666340560760)

当url后面拼接/hello/1/的时候，可以成功访问：

![1666340353_635256018baac17fd90a6.png!small?1666340353765](https://image.3001.net/images/20221021/1666340353_635256018baac17fd90a6.png!small?1666340353765)

【这里好像找不到flag，哪位大佬找到flag麻烦教教我呜呜呜】

### 漏洞迭代

（1） **shiro <
1.4.2**版本中，访问/hello/1接口，会被authc拦截器拦截，导致跳转到登录接口进行登录，但是因为*不匹配路径，所以/hello/1/是不会被权限校验所匹配检查的，故/hello/1/
可绕过。

（2） **shiro <= 1.5.1**版本做了修改，/hello/1/ 会跳转到登陆进行权限验证，但可借助;进行绕过，绕过的
**payload为/xxxx/..;/hello/1**

以上处理过程具体为：

①客户端请求URL: /xxxx/..;/hello/1，shiro先处理url，先判断分号是否存在，存在就截取分号之前的路径，得到/xxxx/..

②然后shiro对路径进行标准化处理，如替换//为/，替换\等，得到/xxxx/..进入路径的权限校验

③因为只有/**可以匹配路径。所以/**与/xxxx/..匹配，/**是anon权限，无需登录操作，这样绕过了shiro权限判断

④spring得到/xxxx/..;/hello/1，通过规范化的一些函数去掉url中/与/之间的;及其后面的内容(如/..;aa/1 ->
/../1)得到/xxxx/../hello/1，然后替换/xxxx/..，最终访问 /hello, 成功绕过了权限限制

（3） **1.5.2** 版本的shiro仍可以绕过，就是后面提到的CVE-2020-11989(shiro<1.5.3) 和
CVE-2020-13933(shiro<1.6.0)

> 简单总结：
>
> 访问请求的时候，Shiro的拦截器比spring(Servlet)先执行，两者拦截器对于URI模式匹配的差异，导致Shiro拦截器的绕过。

## CVE-2020-11989

### 漏洞简介

shiro在1.5.2中存在两种利用方法：

 **第一种** ：利用;来绕过验证，payload为： **/;/test/admin/page**
(/test表示tomcat根目录，实际操作中灵活变化)

对于 **http://aaa.com/;/test/admin/page** 这个url，shiro先进行权限验证，截取 **;**
前面的路径，http://aaa.com/,这是可以访问的资源，从而通过shiro权限验证。

然后在spring中解析url,spring
剔除url中的;，保留其他所有内容，然后经过一些规范化函数，会得到http://aaa.com/admin/page

 **第二种** ：利用shiro框架解码方法和路径处理方法进行绕过， **payload为/test/admin/a%25%32%66a**
。（/test表示tomcat根目录，实际操作中灵活变化）

shiro拿到 **http://aaa.com/test/admin/a%25%32%66a**
后，会进行两次解码得到URL：http://aaa.com/test/admin/a/a **(a%25%32%66a - > a%2fa -> a/a)
**这样的话admin/a/a 与 admin匹配不了，通过shiro验证。

然后就在spring中解析url,
spring解析得到的路径为http://aaa.com/test/admin/a%2fa，这在spring中符合/admin/{name}的访问规则，所以成功越权。

> 参考资料：https://www.anquanke.com/post/id/222489?display=mobile
>
> 这篇分析的大大滴好

### 漏洞复现

利用版本： shiro<=1.5.2

靶场：vulfocus(有坑)

访问/hello/1,提示登录

![1666427239_6353a967d90764360caea.png!small?1666427239263](https://image.3001.net/images/20221022/1666427239_6353a967d90764360caea.png!small?1666427239263)

访问/hello/1，仍提示登录

![1666427325_6353a9bd68da63e1ce6fc.png!small?1666427324793](https://image.3001.net/images/20221022/1666427325_6353a9bd68da63e1ce6fc.png!small?1666427324793)

访问/;/hello/1仍需要登录、 /hello/;/1 仍需登录、/hello/1%25%32%66仍需登录......

![1666429804_6353b36cce133d3a81ad5.png!small?1666429804247](https://image.3001.net/images/20221022/1666429804_6353b36cce133d3a81ad5.png!small?1666429804247)

(我的有效poc呢，我那么大一个有效的poc放那，刚才还在......)

访问/hello、/hello/、/;/hello 倒是可以出来内容，这个靶场有点问题......

![1666429383_6353b1c71f70aeab8907f.png!small?1666429382483](https://image.3001.net/images/20221022/1666429383_6353b1c71f70aeab8907f.png!small?1666429382483)

> 自己搭环境试试（放一个屁股在这回头补）

## CVE-2020-13933

本质上也是因为shiro和spring处理路径上的差异，因为;符号带来的越权漏洞

> 不写了，看参考链接吧
>
> https://www.anquanke.com/post/id/216096
>
> http://h0cksr.xyz/archives/493

