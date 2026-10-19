![](https://image.3001.net/images/20191120/1574237936_5dd4f6f0a14f5.gif!small)

## 一、概述

近期毒霸安全团队通过“捕风”威胁感知系统监控到一起大规模窃取用户浏览器隐私的流氓病毒活动，源头为“上海**网络科技有限公司”旗下的“**看看”软件，除了收集主流浏览器的历史访问记录外，还会定向收集“m****v.com”的cookies上报，推测属于第三方广告营销平台合作行为，可能被用于广告营销商业效果评估等用途。

![](https://image.3001.net/images/20191120/1574253100_5dd5322c954b7.png!small)

通过深入溯源关联分析，我们还发现用于推送浏览器隐私收集插件的LUA云控模块“LuaRtl.dll”还广泛存在于“快*”、“小*记事本”、“小*便签”、“*风pdf
”、“麦*助手”、“A**看图”、“光*搜索”、“7***浏览器”、“小*壁纸”等数十款软件中。除此之外，我们还发现多类涉及用户隐私收集或劫持的病毒插件模块，包括“htkkinforeport_dll.dll”、“UrlReport_dll.dll”、“BrowserLink.dll”等。从我们的长期监控来看，上述软件的云控机制也在不断迭代升级，加强对抗监控分析能力，在技术上强调灵活性和隐蔽性，攻击过程文件不落地，恶意模块通过LUA脚本引擎、Shellcode注入以及DLL反射装载等“无文件”技术手段下放执行，配合环境规避、代码混淆、反调试等灵活对抗机制，给传统安全软件的监控检测也带来一定的困扰。

上述软件大多有正常软件功能包装，安装活跃用户较多，如此大规模的隐私窃取活动在业内也比较罕见。浏览器访问历史、Cookies对于用户来说不仅是非常重要的个人隐私，更是账号身份安全认证信息，这样重要的个人信息被不法软件大规模收集，被用于“大数据”分析对用户进行
“精准画像”，包括“定制信息推送”、“精准广告投放”、“用户行为预测”、“转化分析”、“反作弊分析”等等商业用途。“技术无罪”的论调下，黑与白的界限似乎变得模糊，一方面是用户和信息之间更快速高效的匹配，商家降低获客成本；但是另一方面是个人隐私无限制的泄露，随之而来的各种广告骚扰和安全隐患。无论如何用户对于自身隐私被收集利用应该具备知情权，所以我们决定披露这一起针对用户浏览器隐私进行收集窃取的流氓病毒活动。

云控模块推送隐私收集插件的主要流程如下：

![](https://image.3001.net/images/20191120/1574253109_5dd53235808d3.png!small)

## 二、技术分析

由于涉及产品众多，本文以好*看看为例进行分析，好*看看主进程Hao**KanKan.exe会启动当前目录下的viewuc.exe，传入加密参数执行，经过解密后的参数如下：

![](https://image.3001.net/images/20191120/1574253119_5dd5323f0bb66.png!small)

首先读取当前目录下的hao**uc.jpg图片，看似正常的图片但末尾被附加了加密的PE文件，解开后为updatechecker_dll.dll，该模块被内存加载后调用导出函数EnteyPoint传入解密后的参数执行。其另外两张同样也是隐藏PE文件分别为Report_dll.dll和Update_dll.dll：

![](https://image.3001.net/images/20191120/1574253143_5dd532573f1db.png!small)

进入updatechecker_dll模块后会对命令行参数进行解析后对指定的模块进行加载，这些模块都被加密被存放在了注册表中，在安装时被就下载存入，此公司旗下产品也都是以此种方式存放功能模块于注册表中。updatechecker对应于注册表项，mininews
和logo为需要加载的模块，logouc为Lua脚本。其中logo是Lua扩展模块，Lua脚本中的相关接口实现需要该模块支持。

在加载模块前会先查询云端MD5值与本地数据MD5进行对比，不相同则下载最新文件存入。以logo模块为例首先访问[http]://i.hao**kankan.com/logo/v1.0.0.2/super.gif.MD5

获取该模块MD5值，不相同再访问[http]://i.hao**ukankan.com/logo/v1.0.0.2/super.gif进行下载。Logo解密后为Lua脚本扩展模块LuaRtl.dll.dll，对应执行的脚本为logouc：

![](https://image.3001.net/images/20191120/1574253157_5dd53265e157e.png!small)

在进行上述模块解密前还会进行调试器攻击，先调用BlockInput函数让鼠标和键盘失灵，再通过PEB中的BeingDebugged调试标志位检测是否在调试，如果正在调试则去桌面寻找fuck.debug文件，不存在直接返回不恢复键盘和鼠标输入，造成调试器和整个桌面卡死的假象：

![](https://image.3001.net/images/20191120/1574253166_5dd5326e98cd5.png!small)

进入解密及模块加载功能的函数时，其函数头部代码已经被混淆处理：

![](https://image.3001.net/images/20191120/1574253180_5dd5327cf1827.png!small)

通过混淆代码后会解密出Lua脚本和Lua扩展模块，对Lua扩展模块进行内存加载，同时载入已编译的lua脚本，后期工作逻辑交给Lua脚本处理。对Lua脚本还原后其执行逻辑是在main函数中执行完弹窗后，会调用execute_urlreport函数进行url和cookie收集，该函数进行参数封装后调用接口函数invoke_exe_inject，此函数在LuaRtl.dll中实现。在LuaRtl.dl中根据传入的参数，解密出注册表中的隐私收集模块logo_UrlReport
(htkkinforeport_dll.dll)，同时挂起创建傀儡进程E320.TMP.exe
注入shellcode和htkkinforeport_dll.dll模块，创建远程线程执行shellcode，由shellcode内存加载起htkkinforeport_dll.dll并调用导出函数e开始工作：

![](https://image.3001.net/images/20191120/1574253190_5dd53286dc734.png!small)

在htkkinforeport_dll.dll模块中，首先获取用户硬件信息计算出唯一的UID标识用户，再判断使用该模块的是旗下哪款产品，通过解密出字符串访问相应的注册表键值获取安装数据上报。

获取浏览器历史记录包括了市面上的绝大部分浏览器：chrome，2345，360chrome，360safe，世界之窗，liebao，opera，qq，uc，IE，Mozilla，sogou。以chrome浏览器为例，历史记录都是以Sqlite数据库存储的，先复制一份数据到临时目录，通过Sqlite3库打开数据库执行SQL语句进行查询，在查询前会获取上一次的时间戳，获取此时间戳以后的新内容。为了直观展示以数据库查询工具做演示执行sql语句：

![](https://image.3001.net/images/20191120/1574253206_5dd5329674d4d.png!small)

这些数据最终会被封装成json格式加密后通libcurl库发送到服务器[http://h](http://h/)*kkinforeport.***ingzao.com/12.gif：

![](https://image.3001.net/images/20191120/1574253220_5dd532a4a7d38.png!small)

浏览器的Cookie与历史记录相似也是Sqlite数据库，同样复制到临时目录，打开Cookie数据库进行查询操作。与查询历史记录不同的是，Cookie定向收集所有包含m****v.com域名的cookie。

![](https://image.3001.net/images/20191120/1574253233_5dd532b177aef.png!small)

Cookie值在数据库是加密存放在encrypted_value字段中的，但是加密是基于本地账户登录凭证的所以解密需要在本地进行，通过调用API
CryptUnprotectData进行解密并发送。

![](https://image.3001.net/images/20191120/1574253246_5dd532becbc69.png!small)

## 三、总结

当下谈及用户隐私安全，普遍更多的侧重于和个人信息结合更紧密的移动端APP案例，但是PC端同样保存了非常多有价值的用户隐私信息，相对于移动端，PC系统的安全权限设置更加宽松开放，隐私窃取的技术难度反而更低，并且现阶段的用户隐私保护政策并不完备，对于部分流氓团伙和软件厂商来说就成为可乘之机。所以我们安全团队建议用户定期清理浏览记录，毒霸用户可以使用隐私清理保护功能防止个人信息泄露。

### IOC

[MD5]

> 36593363D3F09A6D65F6670BDC115241
>
> 8E139186B82AD88B50**A04E2C82BFE1
>
> 8D85BFC97A1DF511BBD477DB32A42E72
>
> E5A5B8A5A9402E9154A392A**F4D9811
>
> 0B9C5CB6201EEE56AB332AEB44802D9B
>
> 7B059DE910C2BDF3D051174F50**C71B
>
> 75A1AE668EB6773C18CB0613A8E4BFA5
>
> 5B60924BE0F70B5D9525021C234B2070
>
> 6CCDA533C**43BAE4372858715183CF3
>
> 9FCD1DE8B96A7DDF0BDFDBAD494E4708

 ***本文作者：安全豹，转载请注明来自FreeBuf.COM**

