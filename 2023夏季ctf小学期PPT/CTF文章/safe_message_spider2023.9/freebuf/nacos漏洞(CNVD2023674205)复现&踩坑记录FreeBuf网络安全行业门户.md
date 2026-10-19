## nacos漏洞(CNVD-2023674205)复现&踩坑记录

### 漏洞披露

3月2日，CNVD披露了编号为CNVD-2023674205的nacos认证绕过漏洞

![image](https://image.3001.net/images/20230529/1685345954_647456a238c566a0da5df.png!small)

在nacos官方github项目(https://github.com/alibaba/nacos)发布2.2.0.1版本对应修复版本，移除了默认鉴权插件中依赖的`nacos.core.auth.plugin.nacos.token.secret.key`默认值

![image](https://image.3001.net/images/20230529/1685345966_647456ae33498baf27171.png!small)

### 漏洞复现&分析

下载2.2.0版本nacos搭建环境，下载链接：https://github.com/alibaba/nacos/releases/download/2.2.0/nacos-server-2.2.0.tar.gz

启动也很简单，先安装好java环境（如何安装java自行搜索 (～￣▽￣)～），进入bin目录下，执行./startsh -m standalone即可

    
    
    # 解压缩
    unzip nacos-server-1.0.0.zip
    # 进入bin目录
    cd nacos/bin
    # 运行nacos 注意添加 -m standalone 
    sh startup.sh -m standalone
    # 关闭nacos
    sh shutdown.sh
    

![image](https://image.3001.net/images/20230529/1685345987_647456c3146246b91ba32.png!small)

根据官方的修复公告，查看配置文件
conf/application.properties，发现`nacos.core.auth.plugin.nacos.token.secret.key`是有默认值的

![image](https://image.3001.net/images/20230529/1685346002_647456d20c67cd01c3b16.png!small)

而nacos使用jwt构造认证token，使用HS256算法，把配置文件中`nacos.core.auth.plugin.nacos.token.secret.key`的默认值当作私钥生成Signature，将subject（用户名）和exp戳写到jwt
token里

查看源码：nacos-2.2.0\plugin-default-impl\src\main\java\com\alibaba\nacos\plugin\auth\impl\JwtTokenManager.java

![image](https://image.3001.net/images/20230529/1685346035_647456f3aa93760496958.png!small)

其中secretKey即配置文件中`nacos.core.auth.plugin.nacos.token.secret.key`的值，从JwtTokenManager类的processProperties()函数中可以看到

![image](https://image.3001.net/images/20230529/1685346046_647456fe45a89c4aa3b0d.png!small)

在jwt token校验的时候，校验了token签名有效性和是否过期（nacos-2.2.0\plugin-default-impl\src\main\java\com\alibaba\nacos\plugin\auth\impl\NacosAuthManager.java）

![image](https://image.3001.net/images/20230529/1685346056_647457080d4c7ae0286cf.png!small)

现在知道了jwt的生成和校验逻辑，以及jwt的默认私钥，就可以伪造jwt
token绕过认证nacos认证逻辑，构造一个超长有效期的token，就可以使用poc扫描啦

![image](https://image.3001.net/images/20230529/1685346122_6474574a73898aff461c6.png!small)

下面进行验证，以获取配置信息接口为例，首先是没有jwt token访问接口，返回禁止访问

![image](https://image.3001.net/images/20230529/1685346133_64745755c64a364b11547.png!small)

带上Authorization再访问，jwt token使用刚才构造的，成功返回

![image](https://image.3001.net/images/20230529/1685346148_6474576474d1d43516999.png!small)

ps：在老版本中（1.1.4版本及以下），如果nacos没有配置信息，则body中没有数据，仅返回200，所以poc不能以响应包的body为标志进行扫描，若以status_code为标志，则误报会很多

![image](https://image.3001.net/images/20230529/1685346158_6474576e87b55d4f0b368.png!small)

可以删除search参数值，以响应包的body为标志( •̀ ω •́ )✧

![image](https://image.3001.net/images/20230529/1685346167_6474577776174816fd56f.png!small)

**ps：**0.x.x的远古版本没有登录逻辑。。访问就直接进入系统了

## 漏洞修复

1.2.0版本及以上的nacos，修改配置文件中的`nacos.core.auth.plugin.nacos.token.secret.key`即可

1.1.4版本及以下的nacos，由于私钥写死到了代码里，用户无法自行配置，只能升级nacos到最新版

![image](https://image.3001.net/images/20230529/1685346277_647457e5376e10fbc3660.png!small)

## 踩过的坑

一开始用登录接口来检测jwt默认私钥漏洞，在1.2.0及以上版本中，使用构造的jwt
token访问，发现即使不输入账密，也显示登录成功，接口地址为/nacos/v1/auth/users/login（默认配置启动），响应包中校验200状态码和accessToken字段即可

![image](https://image.3001.net/images/20230529/1685346262_647457d60754ade03f64d.png!small)

但在老版本（1.1.4及以下版本）中，接口地址为/nacos/v1/auth/login（默认配置启动），跟新版本的不一样，并且使用了伪造的jwt
token也不成功，造成了漏报(っ °Д °;)っ

![image](https://image.3001.net/images/20230529/1685346235_647457bb4d4454610342f.png!small)

勾起了好奇心，下载nacos源码一探究竟：

首先是老版本（1.1.4及以前）的源码，登录逻辑为直接比对账密，比对成功即登录成功

![image](https://image.3001.net/images/20230529/1685346292_647457f4cc71a0bf9c353.png!small)

而在新版本（1.2.0版本-最新）中，增加了一个header中token的认证逻辑：如果配置文件中的nacos.core.auth.system.type为nacos或者ldap，且请求包含Authorization的header并校验通过，则优先使用请求中的token，可以不用校验账密

配置文件（nacos.core.auth.system.type默认为nacos）：

![image](https://image.3001.net/images/20230529/1685346310_647458060988739c7633a.png!small)

登录部分的源码（nacos-2.2.0\plugin-default-impl\src\main\java\com\alibaba\nacos\plugin\auth\impl\controller\UserController.java）：

校验通过后，响应包会直接使用请求包中的jwt token

![image](https://image.3001.net/images/20230529/1685346322_64745812724505ac68572.png!small)

跟进authManager.login(request)函数，到达nacos-2.2.0\plugin-default-impl\src\main\java\com\alibaba\nacos\plugin\auth\impl\NacosAuthManager.java里面

在resolveToken和validate0函数里校验

![image](https://image.3001.net/images/20230529/1685346330_6474581ae6684a4f5a0b0.png!small)

resolveToken函数用于提取Authorization的值，若以Bearer 为开头，则取第7个字符以后的字符串返回

![image](https://image.3001.net/images/20230529/1685346354_6474583293c487a111ec4.png!small)

validate0用于校验jwt token，使用配置的nacos.core.auth.default.token.secret.key

![image](https://image.3001.net/images/20230529/1685346376_647458486a5b277af7269.png!small)

响应包中返回登录成功，响应包中包含请求header中的token，而老版本仅校验账密导致返回登陆失败

![image](https://image.3001.net/images/20230529/1685348077_64745eede286c0b7d6898.png!small)

所以新版本中使用登录接口验证默认私钥漏洞不适用于老版本，构造一个全版本通杀的poc还是不容易的o(TヘTo)，还是加上获取配置信息接口一块扫吧。。

## 题外话

#### 1、User-Agent导致的未授权漏洞

nacos历史上曾经爆出过使用特殊构造的User-Agent造成未授权接口访问的漏洞，在翻官方文档（https://nacos.io/zh-cn/docs/auth.html）中发现这么一段话：

![image](https://image.3001.net/images/20230529/1685346436_64745884f227687e17191.png!small)

由此可见，使用特殊构造的User-Agent是官方用于服务端之间的可信通信，未考虑到暴露公网的情况，在nacos
1.2-1.4.0版本期间存在这个安全问题，在1.4.1及以上版本中，nacos默认配置关闭了这个特性，用户可以手动开启，开启后需要配置自定义的key
value对

#### 2、某poc扫描器的小特性

在写poc时，我的expression是这样写的，校验响应包头中是否有Content-Type字段，并判断是否为application/json

![image](https://image.3001.net/images/20230529/1685346478_647458ae9089ad4082d04.png!small)

看着莫得问题，结果poc扫描器显示poc加载失败

![image](https://image.3001.net/images/20230529/1685346489_647458b990326c0c97cc2.png!small)

看了看官方文档，也没发现啥问题，文档里也这么用的

![image](https://image.3001.net/images/20230529/1685346498_647458c2309391a4f88c5.png!small)

调试了半天，发现前面一定要有response.status的判断才能加载成功。。

![image](https://image.3001.net/images/20230529/1685346515_647458d31bae0ba8b4366.png!small)

![image](https://image.3001.net/images/20230529/1685346523_647458db01e76c93de0b2.png!small)

但是响应包的状态码本来就不确定，可能为200 400
500，所以就没加状态码的判断，结果就卡在这里了。。（不晓得为啥一定要先判断response.status才能检查headers）

被逼无奈，只能写了个response.status != 1来意思一下了(* ￣︿￣)

