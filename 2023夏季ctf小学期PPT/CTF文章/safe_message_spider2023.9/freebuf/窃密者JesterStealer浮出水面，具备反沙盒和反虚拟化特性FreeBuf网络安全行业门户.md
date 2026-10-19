安全研究人员近期发现一个新出现的窃密恶意软件 Jester Stealer，窃取登录凭据、Cookie 和信用卡等信息，其销售广告如下所示：

![image.png-282.2kB](https://image.3001.net/images/20220307/1646630649_622596f9b18c93e6ae5ee.png!small)广告

2021 年 7 月，Jester Stealer 在网络犯罪论坛上露面，论坛上发布的贴子如下所示：

![image.png-345.6kB](https://image.3001.net/images/20220307/1646630650_622596fa4161c768a485e.png!small)帖子

Jester Stealer 具备以下典型特点：

> 使用 AES-CBC-256 算法加密进行通信
>
> C&C 服务器位于 Tor 网络中
>
> 所有日志都重定向到 Telegram
>
> 在内存中收集数据，不需写入硬盘

![image.png-291.5kB](https://image.3001.net/images/20220307/1646630651_622596fb638ff32e924be.png!small)特性宣传

在分析调查期间，Jester Stealer 更新了七个版本。除了上面提到的特性外，还具备反沙盒和反虚拟化等对抗特性。该恶意软件窃取浏览器、VPN
客户端、密码管理器、聊天软件、电子邮件客户端、加密钱包和游戏软件的相关数据。窃取的数据通过 Tor 网络以日志的形式发送到 Telegram
Bot，如果这种方法未成功则使用 AnonFiles（匿名文件共享平台）。

![image.png-158.5kB](https://image.3001.net/images/20220307/1646630652_622596fc9ca814e949c10.png!small)功能特性

Jester Stealer 的开发者还提供了自定义恶意软件构建工具，可以通过
txt、jar、ps1、bat、png、doc、xls、pdf、mp3、mp4 和 ppt 等扩展名隐藏 .exe 文件。

![image.png-60.4kB](https://image.3001.net/images/20220307/1646630653_622596fd5d9070200f1fe.png!small)Telegram
频道

## 技术分析

通过静态分析，Jester Stealer 使用 .NET 开发。不止配置文件部署在
[GitHub](http://github.com/L1ghtM4n)上，Jester Stealer 也会通过 GitHub 下载 Tor 代理。

![image.png-155.1kB](https://image.3001.net/images/20220307/1646630653_622596fdd1b4e442d29c5.png!small)文件信息

如下所示，Jester Stealer 使用自定义加解密函数，处理 Onion URL、注册表项等。

![image.png-162.3kB](https://image.3001.net/images/20220307/1646630654_622596fe9cc9f73b2618b.png!small)自定义函数

该恶意软件内置多项检查，阻止被自动分析：

![image.png-39.5kB](https://image.3001.net/images/20220307/1646630655_622596ff50984443304e7.png!small)反分析技术

> 恶意软件发现自己在被调试会终止执行
>
> 恶意软件发现自己在虚拟环境中运行（如 Virtulbox、vmbox、VMware 等）会终止执行
>
> 恶意软件发现自己在沙盒（SbieDll.dll）中运行会终止执行
>
> 恶意软件发现注册表项 state 被设置为 1 会终止执行

![image.png-111.4kB](https://image.3001.net/images/20220307/1646630655_622596ffa7ab33b619dd7.png!small)注册表项

恶意软件在窃取信息后生成报告：

![image.png-296kB](https://image.3001.net/images/20220307/1646630656_622597004165eefbaedb6.png!small)窃取数据

将所有窃取的数据存储在内存中，并将其压缩再回传。

![image.png-207.6kB](https://image.3001.net/images/20220307/1646630657_622597013dc6aff4b0e9e.png!small)窃取数据示例

通过 Tor 将数据回传：

![image.png-186.2kB](https://image.3001.net/images/20220307/1646630657_62259701d4098226b2565.png!small)下载
Tor 代理

Jester Stealer 使用的 Tor URL 为
`hxxp://jesterdcuxzbey4xvlwwheoecpltru5be2mzuk4w7a7nrhckdjjhrbyd.onion`。

如果数据未被回传到 Tor 服务器中，恶意软件将文件上传至公共文件托管服务器 AnonFiles，命名以
`AttackerName_username_systemname.zip`为格式。

![image.png-88.5kB](https://image.3001.net/images/20220307/1646630658_622597025c8233ec001b0.png!small)上传文件

成功窃密后，恶意软件会从失陷主机中自行删除。

![image.png-90.4kB](https://image.3001.net/images/20220307/1646630658_62259702c23765bdda5f1.png!small)自删除

## 结论

窃密恶意软件正在演变为令人担忧的安全威胁之一。攻击者窃取用户凭据、系统信息，甚至是屏幕截图或者其他隐私数据。

## IOC

> hxxp[:]//jesterdcuxzbey4xvlwwheoecpltru5be2mzuk4w7a7nrhckdjjhrbyd.onion  
> 8879ae061540ce3de496adec3683b0fe  
> a30d170412986b90ce293b5a8ff7dfd8  
> 9196e0e3234ef664e828eba9628f468d  
> c73c7c93101d4d741c79127a37d13d3a  
> 7989d8fb3ec96482016acd52d56ea7f8  
> 3986844f88921ccaba28a173a843c27a  
> 26e71a30d1e8b43be1f16d3483d1d44c  
> 9378111ed1b30ad23d37d7d7c33345d1  
> 952cd4334dc6b9c1a3e0d0ab64d5afb2  
> 90257b4f1de0e70235b2ff7419803afa  
> 2cd2390f2138b725f4176343784c7705

## 参考来源

> [Cyble](https://blog.cyble.com/2022/02/24/jester-stealer-an-emerging-info-> stealer/)

