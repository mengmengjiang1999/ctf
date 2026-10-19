**近日，深信服安全团队连续收到不少用户中了勒索病毒的求助。**
**经过分析排查发现，其中的勒索病毒文件相同，为Sodinokibi家族变种，且攻击痕迹也有相似之处，疑似同一伙黑客团体连续作案。**

## 两次攻击的相似点

都创建了一个“intel”文件夹用于保存病毒文件及黑客工具：

![](https://image.3001.net/images/20200420/1587370319_5e9d594fe813b.png!small)

![](https://image.3001.net/images/20200420/1587370356_5e9d597471cf6.png!small)

都将病毒命名为“d.exe”并复制到启动目录：

![](https://image.3001.net/images/20200420/1587370380_5e9d598c36292.png!small)

![](https://image.3001.net/images/20200420/1587370388_5e9d5994bd125.png!small)

## 病毒分析

动态获取程序运行所需API地址：

![](https://image.3001.net/images/20200420/1587370410_5e9d59aa07b20.png!small)

创建互斥量“Global\1DE3C565-E22C-8190-7A66-494816E6C5F5”，避免重复运行：

![](https://image.3001.net/images/20200420/1587370428_5e9d59bcf39e8.png!small)

解密出加密配置信息：

![](https://image.3001.net/images/20200420/1587370438_5e9d59c64376b.png!small)

配置信息为json格式文本，其包含如下信息。

豁免文件夹：

> "tencent fies","wechat files","perflogs","program
> files","mozilla","windows.old","program files
> (x86)","intel","google","windows","application data","$windows.~bt","system
> volume information","appdata","msocache","programdata","tor
> browser","$windows.~ws","boot"

豁免文件名：

>
> "ph.exe","bro.exe","ntuser.dat","sais.exe","xm64.exe","boot.ini","bootfont.bin","ntuser.dat.log","autorun.inf","xwdef.exe","ntldr","desktop.ini","ntuser.ini","bootsect.bak","ns.exe","dudok.exe","thumbs.db","iconcache.db"

豁免文件后缀：

>
> "wpx","mpa","ani","drv","mod","idx","themepack","msu","icl","ocx","cpl","scr","adv","shs","prf","sys","diagpkg","msp","386","theme","com","nls","bat","msstyles","icns","lock","ics","nomedia",
>
> "deskthemepack","diagcab","hlp","cmd","rtp","diagcfg","cur","rom","spl"

删除服务名：

> "oracle","veeam","sql","vm","backup"

结束进程名：

> "veeam","sql","vm","oracle","backup"

服务器域名：

> praxis-management-> plus.de;iqbalscientific.com;retroearthstudio.com;lange.host;starsarecircular.org;urclan.net;lorenacarnero.com......

另外还包含：加密公钥、base64编码后的勒索信息文本、勒索信息文件名格式等。

从上面的配置信息可以发现该病毒变种有如下定制化特点：

1、豁免文件夹除了系统文件夹、浏览器文件夹以保证系统以及浏览器能够正常使用外，还包含了腾讯以及微信的文件夹"tencent fies"、"wechat
files"，表明其攻击目标可能比较倾向中国地区，"intel"则是用于保存病毒文件及黑客工具的文件夹。

2、豁免文件名除了一些系统文件外，还包含常见的黑客工具名以及勒索病毒名，根据从以往Sodinokibi攻击现场获取到的文件，“xm64.exe”为密码抓取工具、“xwdef.exe”为防火墙关闭工具、“ns.exe”为内网扫描工具、“dudok.exe”为病毒文件名，而"ph.exe"、"bro.exe"、"sais.exe"也有可能是其他的黑客工具名。

![](https://image.3001.net/images/20200420/1587370721_5e9d5ae18caca.png!small)

解码出的勒索信息文本如下：

![](https://image.3001.net/images/20200420/1587370710_5e9d5ad6b726e.png!small)

根据键盘布局对如下语言地区进行豁免：

![](https://image.3001.net/images/20200420/1587370636_5e9d5a8c955ed.png!small)

创建注册表自启动项，如果加密过程中被关机，重启后将会继续执行加密：

![](https://image.3001.net/images/20200420/1587370643_5e9d5a93c5371.png!small)

执行powershell命令

“powershell -e
RwBlAHQALQBXAG0AaQBPAGIAagBlAGMAdAAgAFcAaQBuADMAMgBfAFMAaABhAGQAbwB3AGMAbwBwAHkAIAB8ACAARgBvAHIARQBhAGMAaAAtAE8AYgBqAGUAYwB0ACAAewAkAF8ALgBEAGUAbABlAHQAZQAoACkAOwB9AA==”，其中base64解码后为——“Get-WmiObject Win32_Shadowcopy | ForEach-Object
{$_.Delete();}”，其功能为删除卷影副本，防止通过卷影副本的方式恢复被加密文件：

![](https://image.3001.net/images/20200420/1587370793_5e9d5b29a09d6.png!small)

枚举并删除相应服务：

![](https://image.3001.net/images/20200420/1587370775_5e9d5b1796baa.png!small)

结束相应服务进程：

![](https://image.3001.net/images/20200420/1587370807_5e9d5b37a4005.png!small)

遍历磁盘对文件进行加密：

![](https://image.3001.net/images/20200420/1587370815_5e9d5b3fc8011.png!small)

修改桌面背景：

![](https://image.3001.net/images/20200420/1587370823_5e9d5b47b4f28.png!small)

上传系统信息到服务器：

![](https://image.3001.net/images/20200420/1587370833_5e9d5b517ec28.png!small)

加密完成后病毒文件自删除：

![](https://image.3001.net/images/20200420/1587370841_5e9d5b5989147.png!small)

加密后现象如下，将桌面背景改为蓝色，文件加密后被添加随机后缀，并生成txt格式的勒索信息文件：

![](https://image.3001.net/images/20200420/1587370859_5e9d5b6b18d4c.png!small)

## 日常加固建议

> 1、日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；
>
> 2、使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；
>
> 3、避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；
>
> 4、定期检测系统漏洞并且及时进行补丁修复。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

