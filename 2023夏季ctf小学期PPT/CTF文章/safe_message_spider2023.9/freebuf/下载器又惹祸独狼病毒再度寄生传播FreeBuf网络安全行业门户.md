## 一、概述

**近期毒霸安全团队再次监控到一起病毒传播活动，监控数据显示本次的病毒传播源头为“多特下载器”，分析后我们确认该下载器静默推送的”多点检测”暗藏后门，被用来推广病毒和流氓软件。其代码结构逻辑和我们之前报道过的“群魔乱舞：五大国产病毒家族的末日收割”一文中的“速搜”高度相似，可以确认为同一团伙所为。**

本次传播主要行为是通过三次云控机制推送独狼(幽虫)和QQ蠕虫病毒，以及推广流氓软件，劫持用户主页流量牟利。本次传播被迅速捕获，目前还处于铺量阶段，但是通过其内部访问的统计页显示日感染量已接近1万，感染病毒重灾区分布在山东，江苏，河南，还有上升趋势。

![](https://image.3001.net/images/20191028/1572250582_5db6a3d6f11ab.png!small)

其整个传播执行流程如下：

![](https://image.3001.net/images/20191028/1572250953_5db6a549928b0.png!small)

## 二、技术分析

### 2.1 下载器的那些事

本次病毒传播通过监测发现来自多特下载站的下载器，此类下载器属于“三无产品”：无签名、无版本、无厂商信息，但都有云端配置，每次启动后会获取云端配置，根据配置规则展示用户环境可推广的软件。这些配置可随时更新，即使被发现传播病毒只要更改云端配置也就无法追查，隐蔽性极强违法成本也极低。站点在推广软件时并不会去审核被推广软件是否安全，其界面标榜的杀毒检测通过都是虚假的。配置中为每个推广软件定制了一套私有规则，“filter_process”字段决定了需要规避的进程名，“silent”字段为静默安装的命令，如果本身为静默包则为空，以本文中的“多点检测”为例其安装配置过滤360进程和网吧客户端管理进程，本身为静默安装包。

![](https://image.3001.net/images/20191028/1572250970_5db6a55a33d3e.png!small)

### 2.2 后门触发逻辑

“多点检测”安装包在安装过程中会释放一个服务模块YjService.exe，该服务模块启动前会判断用户环境，是否有网吧客户端进程，是否有Tencent注册表项以确认是一个有效用户。YjService.exe启动后同样会再次检测上述用户环境，通过创建定时器设置2小时后触发，定时器触发后获取云端后门模块URL，经过解密后的返回数据：

    
    
    {"url":"<http://dl.ltwpjb.cn/gx/netpipe.exe>", "md5":"08400228fdf4b0c69b6cba47ca1997ee", "time":"1571716765"}

此后门模块netpipe.exe最终通过内存加载执行。

![](https://image.3001.net/images/20191028/1572250984_5db6a568ec34c.png!small)

### 2.3 后门功能

netpipe.exe得到执行后会再次进行环境检查，作者每走一步都非常谨慎，因之前被我们披露过，作者在此多加了一条毒霸检测，以躲避毒霸安全团队的监控。同时通过获取云端规避城市列表规避以下城市：

    
    
    [{"city": "上海"}，{"city": "深圳"}，{"city": "北京"}，{"city": "珠海"}]

此模块主要功能就是根据云端配置推广病毒和流氓软件。下载恶意文件到临时目录，通过创建explorer.exe进程传入文件路径作为参数执行。本次获取到的配置url有两条，url0为带推广ID的流氓软件EmNotepad，url1为“独狼”和QQ蠕虫母体：

    
    
    {  
    
    "url0" : "<http://down.58bingboluo.com/EmNotepadInstall-4740.exe>",  
    
    "url1" : "<http://dl.ltwpjb.cn/gx/hbei.exe>" 
    
    }

![](https://image.3001.net/images/20191028/1572250995_5db6a573d2822.png!small)

### 2.4 庐山真面目

hbei.exe“独狼”母体与我们之前报道过的过”群魔乱舞”一文中的“cscp.exe”行为和代码基本一致，只是更新了相关云控下载链接，其下载的独狼病毒已经被多家安全厂商披露，且没有太大更新，就不再详细展开分析。hbei.exe执行后，会获取云端版本与本地版本对比是否一致作为云控开关控制病毒传播，本次获取到版本为9.1.2，通过后会尝试下载3张jpg图片，实际为PE文件，这些链接被硬编码在了程序内部，其中Good.jpg为QQ蠕虫病毒，会盗取用户token发送留言和小广告，better.jpg为“独狼”病毒，best.jpg链接已经失效。通过创建傀儡系统进程iexpress.exe
注入病毒代码执行。其中“独狼”病毒通过释放RootKit驱动模块内核注入用户浏览器进程实现主页劫持，该驱动功能完善包含文件系统过滤、注册表过滤、网络过滤、进程镜像过滤等多种技术对抗杀软查杀。注入到浏览器后会解密自身区段配置文件，根据配置文件中的url添加命令行参数进行锁主页。

经过我们解密后的配置如下图，其中bkcurl的链接无法访问，可能病毒在铺量阶段还没有生效，根据其前几个版本的配置推测，该配置主要内容为带推广ID的软件和DDOS攻击病毒：

![](https://image.3001.net/images/20191028/1572251008_5db6a58061895.png!small)

锁主页效果：

![](https://image.3001.net/images/20191028/1572251016_5db6a588c1da2.png!small)

## 三、下载器避坑指南

“软件下载器”向来是病毒传播的温床，例子已经数不胜数，随着“双11”的临近，流量劫持类病毒在利益的驱使下还会迎来一波传播高峰，毒霸安全团队建议：

（1） 用户在下载站下载软件时不要被诱导去点击大框的高速下载按钮

![](https://image.3001.net/images/20191028/1572251031_5db6a597d0ee2.png!small)

（2）仔细对比页面展示的文件大小类型和下载的文件大小类型，不一致就要当心了。如果下载下来的文件命名型如： 软件名@数字_数字.exe ，就是下载器了。

（3）
二次打包被捆绑类型，下载下来咋一看图标大小没问题，但是把文件后缀名改成rar或zip,7z等压缩格式即可看出真面目。对于此类软件都可以在官网或毒霸软件管家中下载。

![](https://image.3001.net/images/20191028/1572251438_5db6a72ef3950.png!small)

## 相关IOC

### [签名]

> Lianyungang Over Season Winter Network Technology Co., Ltd.

### [URL/HOST/IP]

> http[:]//dl.2144zm.cn/dt/PHardware_1002_s_packet.exe"
>
> http[:]//yibaidh.com/index.php
>
> http[:]//tji.qrscq.com
>
> http[:]//yshuiv.com/config/mininews.json
>
> http[:]//yshuiv.com/config/updater.json
>
> http[:]//yshuiv.com/config/asdata.json
>
> http[:]//yshuiv.com/config/cscfg.json
>
> http[:]//yshuiv.com/config/dlproxy.json
>
> http[:]//dl.ltwpjb.cn/gx/netpipe.exe
>
> http[:]//dl.ltwpjb.cn/gx/hbei.exe
>
> http[:]//204.12.196.46/Ver/Ver.txt
>
> http[:]//204.12.196.46/Ver/Good.jpg
>
> http[:]//204.12.196.46/Ver/better.jpg
>
> http[:]//204.12.196.46/Ver/best.jpg
>
> http[:]//204.12.196.46/DuoWan/better.jpg
>
> http[:]107.150.51.206/51la/hz.html
>
> http[:]//ccs.ddd222.xyz
>
> http[:]//204.12.196.46:89/
>
> 107.150.51.203
>
> 107.150.51.206

### [MD5]

> 19E2407C9DD53234C8A8BCD38C86B187
>
> 334B0B77F54B0ED16BE33891BA84C7F8
>
> DC2E380614D2185D0FAB9DCB2**28A57
>
> BB14CDD1E8BE9604090D18AD3A64EAEB
>
> 0FFB8D6DE257117B184FB7CE50295CD0
>
> FC50E2A6594EB02D1D59C9DE2F80B481
>
> B3E0464107C30075652F67D36F446DC9
>
> 5562D51F96757E3B30BE9076E3DE5FE3
>
> 2e708e2b8d6e5a55a0e0***b3d0efd22
>
> 4d207dbae5ebe1f61954fbde6ca77538
>
> 49953f7fec3ad71b704e25d2a67f0d47
>
> c02273ec179ac58ba9bc1cc7f6510326
>
> 5BB09D781DBA72CA82F68408A2DB3452
>
> F058732D50D244F381E784DD9338BB13
>
> 5CFC2D1B4A692887F7807F7FB89A53F9
>
> 4D207DBAE5EBE1F61954FBDE6CA77538
>
> 7F5CFDD6DD5A4277179B663A253DBA7E
>
> D48293AFE925AC9465B41D3508DAAF8E
>
> 733D545D2938CD69BD603763CD11A923
>
> 3EF4B**45CEF74373AA3CC6EF3797838

***本文原创作者：安全豹，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

