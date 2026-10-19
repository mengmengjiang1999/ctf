

 ****

 **![TIDoS-Framework](https://image.3001.net/images/20180926/1537923765_5baadab5a3315.png!small)**

 **TIDoS-Framework是一个基于python的攻击性Web应用渗透测试框架，其涵盖了从侦察到漏洞分析的所有内容。TIDoS-Framework将渗透测试分为了5个主阶段，以及14个子阶段。目前，框架自带有108个模块，侦察阶段有50个模块，扫描和枚举阶段有16个模块，漏洞分析阶段有37个模块，1个exploit和4个Auxillaries辅助模块。另外，在每个阶段还额外提供了一个Auto-Awesome模块，可帮你实现自动化模块任务，你只需提供一个域名即可。**

 **![TIDoS-Framework：攻击性Web应用渗透测试框架](https://image.3001.net/images/20180926/1537923775_5baadabfe1369.gif!small)**

## 安装

Clone存储库并进入到tidos-framework目录：

    
    
    git clone https://github.com/theinfecteddrake/tidos-framework.git
    cd tidos-framework

安装依赖项：

    
    
    chmod +x install
    ./install

![TIDoS-Framework：攻击性Web应用渗透测试框架](https://image.3001.net/images/20180926/1537923815_5baadae72059e.gif!small)

运行：

    
    
    tidos

## 基本使用

TIDoS是一个高度灵活的框架，你只需选择和使用模块即可。

但在此之前，我们需要为各个OSINT平台设置自己的API密钥。打开files/目录下的API_KEYS.py文件，设置你用于访问SHODAN，CENSYS，FULL
CONTACT，GOOGLE和WHATCMS的密钥和访问令牌。 **注意：** SHODAN和WHATCMS的公共API KEYS和ACCESS
TOKENS，TIDoS已为我们提供。但你任然可以添加自己的密钥和访问令牌。

框架启动后我们只需输入网址，例如：<http://www.example.com> 并根据提示操作即可。

> **建议：**
>
> 按照工具的顺序执行。
>
> 侦察➣扫描和枚举➣漏洞分析

更新工具，请使用tools/文件夹下的tidos_updater.py模块。

## 特性

###  **侦察+OSINT**

 **被动侦察：**

> Nping枚举（通过外部APi）
>
> WhoIS Lookup域名信息收集
>
> GeoIP Lookup精确定位物理位置
>
> DNS配置查找DNSDump
>
> 子域查找
>
> 反向DNS查找主机实例
>
> 反向IP查找位于同一服务器上的主机
>
> 基于类的子网枚举
>
> 域IP历史IP实例
>
> Web链接收集
>
> Google搜索手册搜索
>
> Google Dorking（多个模块）自动化
>
> 电子邮件到域解析器（Email WhoIs）
>
> Wayback Machine Lookups查找备份
>
> 电子邮件检查Pwned电子邮件帐户
>
> 仅通过Google Groups电子邮件进行枚举
>
> 检查别名可用性（社交网络）
>
> 查找基于域的PasteBin帖子
>
> LinkedIn员工和公司信息收集
>
> Google Plus收集域名配置文件
>
> 公开联系信息爬取
>
> 基于域的Censys Intel信息收集
>
> 威胁情报收集（不良IP）

主动侦察：

> Ping枚举（高级）
>
> CMS检测（支持185+CMS）
>
> Traceroute
>
> robots.txt和sitemap.xml检查
>
> 抓取HTTP头（实时捕获）
>
> 查找通过OPTIONS允许的HTTP方法
>
> 检测服务器类型
>
> 检查SSL证书
>
> Apache Status Disclosure检查（基于文件）
>
> WebDAV HTTP枚举（PROFIND和SEARCH）
>
> PHPInfo文件枚举（爆破）
>
> 注释爬取（基于正则表达式）
>
> 查找共享DNS主机名称服务器
>
> 备用站点发现（基于用户代理）
>
> 爆破有趣的文件
>
> 常见后门文件位置shells等
>
> 常见备份文件位置.bak, .db等
>
> 常用密码文件位置.pgp，.skr等
>
> 常见代理路径配置文件 .pac等
>
> 多索引路径index, index1等
>
> 常见Dot文件.htaccess，.apache等
>
> 常见日志文件位置 .log，.changelog等

**信息泄露：**

> 信用卡泄露如果为明文
>
> 电子邮件信息收集
>
> 致命错误枚举包括完整路径泄露
>
> 基于签名的内部IP泄露
>
> 基于签名的电话号码信息收集
>
> 社会安全码信息收集

### **扫描和枚举**

> 远程服务器WAF枚举（54款通用WAF）
>
> 端口扫描（Ingenious模块）
>
> 通过套接字连接的简单端口扫描
>
> TCP SYN Scan（可靠度：高）
>
> TCP Connect Scan（可靠度：极高）
>
> XMAS Flag Scan仅在LAN中可靠
>
> FIN Flag Scan仅在LAN中可靠
>
> 端口服务检测
>
> Web技术枚举
>
> 完整的SSL枚举
>
> 操作系统指纹识别
>
> 通过开放端口抓取服务Banner
>
> 使用NMap 16个预装模块进行交互式扫描
>
> 使用CENSYS数据库扫描整个网络服务器
>
> Web和链接爬取
>
> 深度为1时，索引Uri爬取
>
> 深度为2时，单页面爬取
>
> 深度为3时，Web链接爬取

###  **漏洞分析**

 **Web-Bugs和服务器配置错误**

> 不安全的CORS
>
> 基于子域的Same-Site Scripting
>
> 基于DNS服务器的区域传输
>
> 点击劫持
>
> Frame-Busting检查
>
> X-FRAME-OPTIONS标头检查
>
> Cookie的安全性
>
> HTTPOnly标志
>
> Secure标志
>
> Cloudflare配置错误检查
>
> DNS配置错误检查
>
> 在线数据库查找
>
> HTTP严格传输安全使用
>
> HTTPS已启用但没有HSTS
>
> 基于域的电子邮件欺骗
>
> 缺少SPF记录
>
> 缺少DMARC记录
>
> 主机头注入
>
> 基于端口基于Web Socket
>
> X-Forwarded-For头注入
>
> 安全标头分析实时捕获
>
> 跨站点跟踪HTTP TRACE方法
>
> 会话固定通过Cookie注入
>
> 网络安全错误配置
>
> 通过23端口检查TELNET是否已启用

**严重Web漏洞**

> 文件包含
>
> 本地文件包含（LFI）基于参数
>
> 远程文件包含（RFI）
>
> 基于参数
>
> 预加载路径
>
> OS命令注入Linux和Windows（RCE）
>
> 路径遍历（敏感路径）
>
> CSRF
>
> SQL注入
>
> 基于错误的注入
>
> 基于Cookie
>
> 基于Refere
>
> 基于User-Agent
>
> 盲注（payload）
>
> 基于Cookie
>
> 基于Refere
>
> 基于User-Agent
>
> 基于参数的LDAP注入
>
> 基于参数的HTML注入
>
> Bash命令注入（ShellShock）
>
> Apache Struts Shock Apache RCE
>
> 基于参数的XPATH注入
>
> XSS
>
> 基于Cookie
>
> 基于Refere
>
> 基于User-Agent
>
> 未经验证的URL转发
>
> PHP代码注入Windows+Linux RCE
>
> CRLF注入HTTP响应拆分
>
> 基于User-Agent
>
> 子域接管

 **其它**

明文协议默认凭据爆破：

> FTP协议爆破
>
> SSH协议爆破
>
> POP 2/3协议爆破
>
> SQL协议爆破
>
> XMPP协议爆破
>
> SMTP协议爆破
>
> TELNET协议爆破

 **Auxillary模块**

> 哈希生成器MD5，SHA1，SHA256，SHA512
>
> 字符串＆Payload编码器
>
> 取证Image分析元数据提取
>
> Web蜜罐ShodanLabs HoneyScore

 **利用**

ShellShock

 **其它工具：**

> net_info.py - 显示你当前的网络信息。位于tools/目录下。
>
> tidos_updater.py - 通过签名匹配将框架更新到最新版本。同样位于tools/目录下。

以下为 TIDoS 的实际使用截图：

![TIDoS-Framework：攻击性Web应用渗透测试框架](https://image.3001.net/images/20180926/1537924022_5baadbb65199c.gif!small)![TIDoS-Framework：攻击性Web应用渗透测试框架](https://image.3001.net/images/20180926/1537924053_5baadbd51d294.gif!small)![TIDoS-Framework：攻击性Web应用渗透测试框架](https://image.3001.net/images/20180926/1537924126_5baadc1e05181.gif!small)

 **版本：**

    
    
    v1.6.1 [latest release] [#stable]

 **下一步计划：**

添加更多类型的：

> 爆破模块
>
> 枚举和信息泄露模块
>
> OSINT＆Stuff
>
> 辅助模块

一些漏洞利用的exploit也正在开发之中~

## 最后的话

该项目目前正在积极的开发当中并会频繁的更新。因此，你可以持续关注该项目。不得不说这是我有史以来构建的最好的项目之一，希望它能成为你工具包中的得力助手。另外，如果你有任何对该项目的改进意见或建议，都可以通过[issue](https://github.com/theInfectedDrake/TIDoS-Framework/issues/new)或[twitter](https://twitter.com/infecteddrake)向我提出！非常感谢！

 *******参考来源：[github](https://github.com/theInfectedDrake/TIDoS-Framework)，
FB小编 secist 编译，转载请注明来自FreeBuf.COM**

