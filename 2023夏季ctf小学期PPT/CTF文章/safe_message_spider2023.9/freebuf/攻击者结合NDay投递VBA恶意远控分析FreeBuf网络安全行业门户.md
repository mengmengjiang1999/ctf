## **情报背景**

Malwarebytes的研究人员发现有攻击者在近期的攻击活动中使用CVE-2021-26411部署了功能齐全的VBA
RAT，本文对其中包含的攻击技术进行了分析研判。

 **战术标签**

|

网络钓鱼  
  
---|---  
  
 **技术标签**

|

Marco  
  
 **情报来源**

|

https://blog.malwarebytes.com/threat-intelligence/2021/07/crimea-manifesto-deploys-vba-rat-using-double-attack-vectors/

https://enki.co.kr/blog/2021/02/04/ie_0day  
  
## 攻击技术分析

恶意文档执行攻击过程：

1\. 投递的恶意文档Manifest.docx被诱骗打开后远程加载 settings.xml.rels、Document.xml.rels模板文件。

2\. settings.xml.rels 中包含功能齐全的VBA RAT。

3\. Document.xml.rels 使用CVE-2021-26411漏洞利用后同样部署相同的VBA RAT，两种方式双保险，提高感染成功率。

 **1 CVE-2021-26411 远程代码执行漏洞在野利用**

CVE-2021-26411是影响大部分Edge和Internet
Explorer版本的远程代码执行漏洞。此漏洞之前被Lazarus用于针对安全研究人员进行社会工程学攻击，在今年1月份，谷歌与微软的安全人员披露相关攻击的技术细节。

![1629251906_611c69425dd119a40a598.png!small?1629251908558](https://image.3001.net/images/20210818/1629251906_611c69425dd119a40a598.png!small?1629251908558)

使用了该漏洞的Document.xml.rels 模板文件。

 **2 使用 AutoHotKey脚本语言实现部署VBA RAT**

漏洞利用成功会使用 AutoHotKey脚本部署VBA RAT。

1\. 将恶意VBA RAT作为受信任文档添加到TrustedRecords注册表项，当下次打开此文档时，将不需要启用宏。

![1629252053_611c69d5c5c41a26625ab.png!small?1629252053973](https://image.3001.net/images/20210818/1629252053_611c69d5c5c41a26625ab.png!small?1629252053973)

2\. 通过Winword 下载VBA RAT。

![1629252074_611c69eaea19328981da7.png!small?1629252075112](https://image.3001.net/images/20210818/1629252074_611c69eaea19328981da7.png!small?1629252075112)

3\. 创建计划任务启动winword加载模板文件，运行其中的VBA RAT获得持久化。

![1629252099_611c6a033c2df6b61ecd8.png!small?1629252099393](https://image.3001.net/images/20210818/1629252099_611c6a033c2df6b61ecd8.png!small?1629252099393)

 **3 沙盒检测 &记录清除**

模板文件首先运行Document_open 函数代码，在运行RAT之前还会进行相关检测清除。

1\. 使用 VBAWarnings 注册表值反向检查是否在沙盒中运行。

![1629252129_611c6a214eceabf505df8.png!small?1629252129462](https://image.3001.net/images/20210818/1629252129_611c6a214eceabf505df8.png!small?1629252129462)

当此注册表值为1时，表示当前计算机默认允许所有不受信任和受限的宏代码在没有通知的情况下运行，换言之所有的文档都会以默认启用宏的方式运行，计算机将不会受到相关保护。而通常沙盒环境为了让恶意文档触发运行默认将其设置开启，攻击者反向依靠沙箱的这个特性进行检测，当检测到VBAWarnings注册表项为1时，反而退出不进行操作，从而绕过沙盒。

2\. 删除RunMRU注册表值以清除其活动记录。

![1629252160_611c6a400173f0666846e.png!small?1629252160149](https://image.3001.net/images/20210818/1629252160_611c6a400173f0666846e.png!small?1629252160149)

 **4 功能完整的VBA RAT**

功能齐全的VBA恶意远控较为少见，可能是作为先锋或炮灰投递。

其功能包括：

完整磁盘文件读取

文件下载

文件上传

文件删除

退出

加载shellcode

改变任务请求频率

![1629252349_611c6afda190c0ec31370.png!small?1629252350624](https://image.3001.net/images/20210818/1629252349_611c6afda190c0ec31370.png!small?1629252350624)

整个功能和控制方式简单清晰，访问服务器获取Json格式的命令，值得注意的是，RAT开发者将同时执行任务总数限制为3个以内，可能是为了减少因为过多的操作而导致噪音过大导致被安全产品检测（开发者和使用者可能并不是同一个人）。

 **5 使用EnumWindows加载shellcode运行**

RAT 中加载执行shellcode的代码如下

![1629252383_611c6b1f1fd38c343725a.png!small?1629252383532](https://image.3001.net/images/20210818/1629252383_611c6b1f1fd38c343725a.png!small?1629252383532)

EnumWindows 函数原型

![1629252401_611c6b31130319cd63dfe.png!small?1629252401258](https://image.3001.net/images/20210818/1629252401_611c6b31130319cd63dfe.png!small?1629252401258)

EnumWindows 作用是枚举程序窗口,
参数包含一个回调函数，api执行后会调用回调返回结果，攻击者将参数填写为分配的shellcode地址从而绕过安全软件对敏感api调用的检测。

可被滥用的API已经有安全人员做了相关整理https://github.com/S4R1N/AlternativeShellcodeExec

## 总结

攻击中综合利用了远程模板加载、漏洞利用、AutoHotKey脚本作为其前置的攻击步骤，经过一些检测规避之后才会加载其真正的控制木马。不断更新攻击模式和组件，使用脚本语言压缩开发成本，结合多种利用方式提高成功率。在shellcode利用方面，从之前的Lazarus使用的EnumSystemLocalesA
到这次的攻击者使用的 EnumWindows, 滥用windows API 已经成为隐蔽加载shellcode的常用方法。

