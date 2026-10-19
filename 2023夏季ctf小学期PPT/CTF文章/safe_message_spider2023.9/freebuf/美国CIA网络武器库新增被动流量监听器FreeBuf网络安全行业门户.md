2021年4月27日，卡巴斯基发布了2021年第一季度APT活动总结，里面提到了一个新的Lambert家族木马。（未了解详情可点击查阅
[美国CIA网络武器库再更新：目标不同国家进行定制化投放](http://mp.weixin.qq.com/s?__biz=MzAxOTM1MDQ1NA==&mid=2451178496&idx=1&sn=b2ea8b72045afb86ff0433fd8b409716&chksm=8c26f2d9bb517bcfd4575bd58ad829564bba839d826055fd1de68a7381a954163b36668e2c5d&scene=21#wechat_redirect)）

卡巴斯基表示，在2019年2月， **多家反病毒公司收到了一系列恶意软件样本，其中大多数与各种已知的APT组织相关。而**
一些样本不能与任何已知活动相关联，并且样本使用的技术非常先进。

该样本是在2014年编译，因此有可能在2014年和2015年末部署在目标设备上。卡巴斯基表示没有发现样本与任何其他已知恶意软件的存在相同的代码，但样本的编码模式，风格和使用的技术却能够在各个Lambert木马家族中看到。

[卡巴斯基会将Lambert各个木马家族以颜色来命名](http://mp.weixin.qq.com/s?__biz=MzAxOTM1MDQ1NA==&mid=2451177703&idx=1&sn=aea967be7108adc6f40d78f0deb017fb&chksm=8c26f63ebb517f28adb25c56e612a2082d156533a6335501629951622939f17a32a609f22fcd&scene=21#wechat_redirect)。因此，卡巴斯基将此恶意软件命名为Purple
Lambert。

![](https://image.3001.net/images/20210429/1619663507_608a1a9350d3e1026c7da.jpg!small)

Purple Lambert由几个模块组成，其 **网络模块会被动监听流量，** 当监听到特定流量（Magic
Packet）时会被唤醒，木马才会脱离潜伏状态，从而执行其他恶意行为。

![](https://image.3001.net/images/20210429/1619663534_608a1aae1fffd3e0ece5b.jpg!small)

木马可以为攻击者提供有关受感染系统的基本信息，并执行接收攻击者发送的恶意Payload，从而进行下一步的攻击行动。

卡巴斯基认为，该木马的功能与另一个在用户模式进行被动监听Gray Lambert很相似。

事实证明，Gray Lambert在多次攻击中都替代了在内核模式进行被动监听的White Lambert木马。 **最后，Purple
Lambert实现的功能（监听流量）类似于Gray Lambert和White Lambert，但实现的方式不同。**

关于 **Gray Lambert**
，黑鸟通过查阅发现，该木马会以服务的形式启动，在进行了一系列持久化操作后，会正式开始进行被动监听流量操作，其会先从资源中释放加载一个网络流量监控和过滤模块，并尝试通过驱动获取过滤的流量。

主要会从System\\\CurrentControlSet\\\Services\\\Null注册表项获取Description值，其中存储的是驱动注册的文件名，以此来实现和驱动的通信。若不存在对应驱动，那么其采用Windows的ETW机制来实现网络流量的过滤。

(ETW(Event trace for Windows)是微软提供的追踪和记录由应用程序和内核驱动事件的机制。)

关于 **White Lambert**
，该木马在执行一系列操作后，最终会加载一个恶意驱动程序，该驱动是一个通过NDIS流量过滤的Rookit，木马会通过NDIS注册一个自定义的协议，并通过该协议过滤对应网卡中的流量数据，并实现具体的功能（远程控制命令）。

（NDIS网络驱动程序接口规范 （Network Driver Interface Specification）

参考链接：

> https://securelist.com/apt-trends-report-q1-2021/101967/
>
> [https://mp.weixin.qq.com/s/kksNdUGSch-> RUOrZwCchbQ](https://mp.weixin.qq.com/s?__biz=MzAxOTM1MDQ1NA==&mid=2451178496&idx=1&sn=b2ea8b72045afb86ff0433fd8b409716&scene=21#wechat_redirect)
>
>
> [抽丝剥茧：复盘美国中央情报局CIA的复杂网络武器杀伤链](http://mp.weixin.qq.com/s?__biz=MzAxOTM1MDQ1NA==&mid=2451177703&idx=1&sn=aea967be7108adc6f40d78f0deb017fb&chksm=8c26f63ebb517f28adb25c56e612a2082d156533a6335501629951622939f17a32a609f22fcd&scene=21#wechat_redirect)

