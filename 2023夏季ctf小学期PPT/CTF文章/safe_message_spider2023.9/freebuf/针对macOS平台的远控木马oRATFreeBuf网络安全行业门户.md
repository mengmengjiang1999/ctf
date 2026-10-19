最近，安全研究人员发现了一个新的 APT 组织，该组织针对赌博网站开发了包括 macOS 在内各种平台的恶意软件。而 SentinelOne
最近也发现了一个针对 macOS 用户的、使用 Go 编写的远控木马 oRAT。

使用 Go 编写的远控木马实际上在 Mac 平台上并不常见，这表明攻击者越来越重视 Mac 平台，想要加强对该平台的控制。

## oRAT 分发传播

oRAT 通过伪装成 Bitget 应用程序集合的磁盘镜像进行传播，磁盘镜像中包含一个名为 `Bitget Apps.pkg`的程序安装包，其标识符为
`com.adobe.pkg.Bitget`。

![image.png-111kB](https://image.3001.net/images/20220518/1652870670_6284ce0e3535c8c54799b.png!small)磁盘镜像

之所以该磁盘镜像和程序安装包值得关注，是因为二者都没有有效的开发者签名，并且程序安装包内并没有任何文件只有一个预安装脚本。

![image.png-47.3kB](https://image.3001.net/images/20220518/1652870670_6284ce0ec951041dcc834.png!small)安装包

预安装脚本是一个简短的 shell 脚本，将 Payload 写入 /tmp 目录并赋予可执行权限启动。

![image.png-188.2kB](https://image.3001.net/images/20220518/1652870671_6284ce0f42a5e7d23c839.png!small)预安装脚本

目前尚不清楚攻击者使用何种方式诱使受害者下载并执行恶意文件。从样本需要覆盖来自 Gatekeeper
的默认安全警告来看，用户可能是在获取破解软件、盗版软件等网站下载得到样本，或者通过社会工程学方法诱使受害者绕过 Gatekeeper 的默认安全警告。

但是用户实际上并没有得到他们想要的东西，这对攻击者来说是非常冒险的。用户执行程序后并没有按照预期得到想要的东西，用户是容易产生怀疑的。不过这同时也表明，攻击者的攻击可能并非定向的，而是广泛撒网的攻击。

## Payload

通过 darwinx64 检查释放在 `/tmp`文件夹中的 Payload 时，会发现该二进制文件没有任何符号。与此同时，通过 sections
列表可以发现该文件使用 UPX 进行加壳：

![image.png-139.6kB](https://image.3001.net/images/20220518/1652870671_6284ce0fdab4af652f541.png!small)恶意文件

加壳阻碍了静态分析，幸好攻击者使用的标准 UPX 3.96 容易脱壳。

加壳后的文件为 3MB，脱壳后接近 10MB。跨平台的恶意软件通常都比较大，尤其是使用 Go 编写的恶意软件，需要将语言的运行时很多支持库都打包进去。

radare2 用户可以查看函数 `sym._main`：

![image.png-41.1kB](https://image.3001.net/images/20220518/1652870672_6284ce104cd57e7db2e7b.png!small)逆向分析

在 Go 二进制文件中，程序代码入口点位于 `main.main`，从中可以发现主函数中调用了另一个自定义包 `orat_utils`。

![image.png-502.7kB](https://image.3001.net/images/20220518/1652870672_6284ce10a86e32b99dcf1.png!small)逆向分析

orat_utils 包中包含几个典型的功能：

![image.png-308.5kB](https://image.3001.net/images/20220518/1652870673_6284ce11ca282742dc98e.png!small)逆向分析

LoadConfig 函数主要解析附加在二进制文件末尾的数据块，加载远控木马的配置。解压后的加密数据占用 166 个字节，分为三部分：加密数据、AES
密钥和两字节的块大小。

![image.png-581.9kB](https://image.3001.net/images/20220518/1652870674_6284ce128a2b934c1430f.png!small)加密数据

解密后即为恶意软件的 C&C 配置信息：

![image.png-41.1kB](https://image.3001.net/images/20220518/1652870675_6284ce1393ce6d6d43c57.png!small)配置信息

获取配置信息后，调用 `sym._orat_cmd_agent.app`并建立连接。根据配置指定的类型，调用
`orat_protocol.DialTCP`、`orat_protocol.DialSTCP`或者
`orat_protocol.DialSUDP`建立连接。TCP 使用的是
[smux](https://github.com/xtaci/smux)，SUDP 使用的是
[QUIC](https://github.com/lucas-clemente/quic-go)。恶意软件在等待 C&C
服务器响应时会进入五秒轮询的睡眠循环。

`sym._orat_cmd_agent.app`中包含了远控的主要功能，都在下列函数中：

> orat/cmd/agent/app.(*App).DownloadFile  
> orat/cmd/agent/app.(*App).Info  
> orat/cmd/agent/app.(*App).Join  
> orat/cmd/agent/app.(*App).KillSelf  
> orat/cmd/agent/app.(*App).NewNetConn  
> orat/cmd/agent/app.(*App).NewProxyConn  
> orat/cmd/agent/app.(*App).NewShellConn  
> orat/cmd/agent/app.(*App).Ping  
> orat/cmd/agent/app.(*App).PortScan  
> orat/cmd/agent/app.(*App).registerRouters  
> orat/cmd/agent/app.(*App).run  
> orat/cmd/agent/app.(*App).Screenshot  
> orat/cmd/agent/app.(*App).Serve  
> orat/cmd/agent/app.(*App).Unzip  
> orat/cmd/agent/app.(*App).UploadFile  
> orat/cmd/agent/app.(*App).Zip

## 总结

oRAT 综合利用开源代码与自研代码针对 macOS 用户发起攻击。攻击者显然对利用 Go
开发复杂网络通信功能十分熟稔，但似乎对恶意软件规避检测方面不太擅长，例如使用标准加壳方式、代码未经过开发者签名等。其他攻击者在这方面给 oRAT
已经做出了好榜样，可以预见在之后该攻击者还会从中学习、持续改进。

## IOC

> 3f08dfafbf04a062e6231344f18a60d95e8bd010  
> 9779aac8867c4c5ff5ce7b40180d939572a4ff55  
> 911895ed27ee290bea47bca3e208f1b302e98648  
> 26ccf50a6c120cd7ad6b0d810aca509948c8cd78  
> 9b4717505d8d165b0b12c6e2b9cc4f58ee8095a6

## 参考来源

> [SentinelOne](https://www.sentinelone.com/blog/from-the-front-lines-> unsigned-macos-orat-malware-gambles-for-the-win/)

