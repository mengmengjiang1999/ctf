Apache ShenYu Admin爆出身份验证绕过漏洞，攻击者可通过该漏洞绕过JSON Web Token (JWT)安全认证，直接进入系统后台。
Apache ShenYu 是应用于所有微服务场景的，可扩展、高性能、响应式的 API 网关解决方案。

Apache ShenYu Admin 存在身份验证绕过漏洞。 ShenyuAdminBootstrap 中 JWT
的错误使用允许攻击者绕过身份验证，攻击者可通过该漏洞直接进入系统后台。

CVE 编号 CVE-2021-37580

影响版本： Apache ShenYu 2.3.0 Apache ShenYu 2.4.0

漏洞复现：

该漏洞主要是接口文件dashboardUser未设置访问权限，攻击者可以直接访问该文件获取管理员帐号和口令

通过FOFA查找使用Apache ShenYu系统

fofa:fid="uPGDN6V9UWnc+KJdy5wdkQ=="

通过BurpSuite发送数据包，GET /dashboardUser

还需要生成jwt，将生成的jwt数据带入head，发送数据包

![](https://image.3001.net/images/20211118/1637210577_6195d9d19e1de7542bb71.jpg!small)

通过返回数据包，可获取管理员帐号和口令，登录系统后台。

通过pocsuite3下的POC扫描脚本CVE-2021-37580.py验证漏洞。

![](https://image.3001.net/images/20211118/1637210590_6195d9deb0248781d197f.jpg!small)

脚本研发过程也非常简单，主要是发送GET数据包到/dashboardUser，通过返回数据包进行判断是否存在漏洞。

关键代码贴出来：

generateToken()主要是生成jwt，将生成的jwt数据带入head

![](https://image.3001.net/images/20211118/1637210645_6195da158e9529b6a276c.jpg!small)

check(url)主要是验证漏洞函数

![](https://image.3001.net/images/20211118/1637210655_6195da1f12f842cf23011.jpg!small)

check(url)验证漏洞函数返回2个值，一个是状态，一个是漏洞结果，存在漏洞返回真和漏洞结果。![](https://image.3001.net/images/20211117/1637139998_6194c61ed38f66528ee5e.jpg!small)

利用pocsuite3下的POC扫描脚本CVE-2021-37580.py

![](https://image.3001.net/images/20211118/1637210678_6195da36ec7f9cbad5d75.jpg!small)

通过fofaviewer导出fofa结果，保存url到url.txt中，可批量验证漏洞

python3 cli.py -r CVE-2021-37580.py -f url.txt --threads 10

可以发现大量存在漏洞的系统。

POC代码：https://github.com/rabbitsafe/CVE-2021-37580

