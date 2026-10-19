之前写过一篇《Radius协议认证原理及双因素/双因子认证应用》，TACACS+协议和Radius协议都是AAA协议的一种，核心作用都是认证（Authentication）、授权（Authorization）和计费（Accounting），和Radius协议的区别是：

![1655691674_62afd99a5af064cb4dcfc.png!small?1655691675768](https://image.3001.net/images/20220620/1655691674_62afd99a5af064cb4dcfc.png!small?1655691675768)

#  ** **TACACS**** ** **+**** ** **和Radius一样也是C/S架构****

![1655691682_62afd9a2cdb4c205f6ebe.png!small?1655691682858](https://image.3001.net/images/20220620/1655691682_62afd9a2cdb4c205f6ebe.png!small?1655691682858)

图中NAS（网络接入服务器）作为TACACS+客户端，向远程接入用户提供接入及与TACACS+服务器交互的服务。TACACS+服务器上则存储用户的身份信息、授权信息以及访问记录，对用户进行认证、授权和计费服务。

#  ** **TACACS**** ** **+**** ** **工作原理****

![1655691689_62afd9a9b6d8c9bc9cdb5.png!small?1655691689937](https://image.3001.net/images/20220620/1655691689_62afd9a9b6d8c9bc9cdb5.png!small?1655691689937)

1、Telnet用户请求登录设备。

2、TACACS+客户端收到请求之后，向TACACS+服务器发送认证开始报文。

3、TACACS+服务器发送认证回应报文，请求用户名。

4、TACACS+客户端收到回应报文后，向用户询问用户名。

5、用户输入用户名。

6、TACACS+客户端收到用户名后，向TACACS+服务器发送认证持续报文，其中包括了用户名。

7、TACACS+服务器发送认证回应报文，请求登录密码。

8、TACACS+客户端收到回应报文，向用户询问登录密码。

9、用户输入密码。

10、TACACS+客户端收到登录密码后，向TACACS+服务器发送认证持续报文，其中包括了登录密码。

11、TACACS+服务器发送认证回应报文，指示用户通过认证。

12、TACACS+客户端向TACACS+服务器发送授权请求报文。

13、TACACS+服务器发送授权回应报文，指示用户通过授权。

14、TACACS+客户端收到授权回应成功报文，向用户输出设备的配置界面。

15、TACACS+客户端向TACACS+服务器发送计费开始报文。

16、TACACS+服务器发送计费回应报文，指示计费开始报文已经收到。

17、用户请求断开连接。

18、TACACS+客户端向TACACS+服务器发送计费结束报文。

19、TACACS+服务器发送计费结束报文，指示计费结束报文已经收到。

TACACS+协议本身的优势非常明显，那么在双因素/双因子认证领域中如何应用？

#  ** **TACACS**** ** **+**** ** **在**** ** **双因素/双因子认证**** ** **领域中的应用****

TACACS+主要体现在网络设备中，Cisco设备使用的TACACS+协议，华为和华三设备使用的HWTACACS协议，功能一致，以HWTACACS为例：

##  ** **配置hwtacacs服务器模板****

（在服务器模板下，指定与交换机对接的服务器的IP地址、端口号（默认为49）和共享密钥，交换机上的配置信息需要与服务器上的信息保持一致）

> #
>
> hwtacacs-server template ckey //建立“ckey”hwtacacs服务器模板
>
> hwtacacs-server authentication xxx.xxx.xxx.xxx //认证服务器地址
>
> hwtacacs-server authorization xxx.xxx.xxx.xxx //授权服务器地址
>
> hwtacacs-server accounting xxx.xxx.xxx.xxx //审计服务器地址
>
> hwtacacs-server shared-key cipher ****** //配置共享秘钥******
>
> undo hwtacacs-server user-name domain-included //取消域名后缀，登录时不需要后缀域名
>
> quit
>
> #

##  ** **配置AAA方案****

> #
>
> aaa
>
> authentication-scheme ckey1 //创建认证方案ckey1
>
> authentication-mode hwtacacs local //认证模式为hwtacacs认证，备份认证模式为本地认证
>
> quit
>
> authorization-scheme ckey2 //创建授权方案ckey2
>
> authorization-mode hwtacacs local //授权模式为hwtacacs授权，备份授权模式为本地授权
>
> authorization-cmd 15 hwtacacs local //用户级别授权
>
> quit
>
> accounting-scheme ckey3 //创建计费方案ckey3
>
> accounting-mode hwtacacs //计费模式为hwtacacs计费（交换机没有本地计费）
>
> accounting start-fail online //计费功能启动失败，允许用户上线
>
> accounting interim-fail online //计费功能临时故障，允许用户上线
>
> quit
>
> #

注：需要在设备上配置本地用户，以确保在hwtacacs服务器故障的情况下，用户可以本地认证上线

##  ** **配置本地用户****

> #
>
> aaa
>
> local-user user1 password irreversible-cipher ****** //创建用户user1和密码
>
> local-user user1 privilege level 15 //为user1用户授予15级权限
>
> local-user user1 service-type telnet //授予user1 Telnet权限
>
> quit
>
> #

##  ** **配置域****

（配置用户所属的域并在域下绑定AAA方案和服务器模板，默认情况下普通用户在default域内，管理员用户在default_admin内）

> #
>
> aaa
>
> domain ckeydas //创建ckeydas域
>
> authentication-scheme ckey1 //绑定ckey1认证方案
>
> authorization-scheme ckey2 //绑定ckey2授权方案
>
> accounting-scheme ckey3 //绑定ckey3计费方南
>
> hwtacacs-server ckey //绑定ckey hwtacacs服务器模板
>
> #

##  ** **远程登入授权****

> #
>
> user-interface vty 0 4
>
> authentication-mode aaa
>
> #

* 配置方法仅供参考，各设备各版本会有所不同，具体参考官方文档！

#  ** **配合中科恒伦TACACS**** ** **+**** ** **服务端，有几个非常大的优势：****

1、统一用户管理：直接在服务端增删改查用户；

![1655691758_62afd9ee7b5cb40ad7905.png!small?1655691758699](https://image.3001.net/images/20220620/1655691758_62afd9ee7b5cb40ad7905.png!small?1655691758699)

2、统一认证：统一在服务端认证，服务端可启用双因素/双因子认证，即可安全登录；

![1655691767_62afd9f7d0a33fbe0a3f5.png!small?1655691768502](https://image.3001.net/images/20220620/1655691767_62afd9f7d0a33fbe0a3f5.png!small?1655691768502)

3、统一授权：在服务端为不同用户分配不同的登录权限，并且可设置允许输入的命令，

![1655691773_62afd9fd9a2d219f8310f.png!small?1655691773807](https://image.3001.net/images/20220620/1655691773_62afd9fd9a2d219f8310f.png!small?1655691773807)

4、统一审计：详细记录xx用户在xx时间访问xx设备，并且详细记录该账号的操作命令；

![1655691779_62afda03b68d6cc4d7c48.png!small?1655691780051](https://image.3001.net/images/20220620/1655691779_62afda03b68d6cc4d7c48.png!small?1655691780051)

综合来看，TACACS+协议在双因素认证领域中的应用非常成熟，相对Radius协议控制更精细，所以正常情况下我更偏向使用TACACS+协议对接双因素认证。

