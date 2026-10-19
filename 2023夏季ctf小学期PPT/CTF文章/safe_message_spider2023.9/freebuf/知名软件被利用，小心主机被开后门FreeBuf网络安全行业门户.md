## ****背景概述****

近日，深信服终端安全研究团队中捕获到了一个木马程序，攻击者通过网络钓鱼的手段诱导受害者点击运行邮件中附带的木马程序，结合正常的Adobe CEF
Helper程序进行攻击；在局域网内通过共享目录进行传播，并在用户主机上留下后门程序进行窃密或者其他恶意行为。

##  ** **详细分析****

从受害主机上的情况来看，病毒主要有三个部分构成：![](https://image.3001.net/images/20220117/1642407983_61e5282f2cc97f7886f88.png!small)

木马的启动程序Explorer.exe其实为正常的Adobe CEF Helper程序，是Adobe Creative
Cloud程序的组件之一：![](https://image.3001.net/images/20220117/1642407995_61e5283b85309c9ee7bf8.png!small)

该组织应该是发现了这个Helper程序会在执行过程中去以函数名的方式获取到Hex.dll中CEFProcessForkHandlerEx的函数地址并执行。所以就伪造了一个假的Hex.dll并导出同名函数CEFProcessForkHandlerEx进行一个劫持的过程。![](https://image.3001.net/images/20220117/1642408072_61e528884745c8a299994.png!small)

这个伪造的CEFProcessForkHandlerEx函数首先会搜索当前进程对应可执行文件目录下的AdobeUpdates.dat文件：![](https://image.3001.net/images/20220117/1642408085_61e52895599b764831ad6.png!small)

然后将文件中的数据读出来：![](https://image.3001.net/images/20220117/1642408099_61e528a3d147c3e7a31aa.png!small)

用0当做隔断，取前十个字节作为秘钥，第十二个字节开始作为带解密的内容。进行一个循环异或的解密：![](https://image.3001.net/images/20220117/1642408111_61e528af493b410962a92.png!small)

异或的过程：![](https://image.3001.net/images/20220117/1642408123_61e528bbab6ff5557b0d1.png!small)

文件内容，前十个字节为循环异或的秘钥：

![](https://image.3001.net/images/20220117/1642408140_61e528cc0d04744acb14b.png!small)

异或完成后得到Payload：![](https://image.3001.net/images/20220117/1642408152_61e528d8b1306a648e9b8.png!small)

然后开始执行Payload代码，其会将病毒的三个文件拷贝到拷贝到%UserProfile%以及%Appdata%目录下，并将Explorer.exe重命名为AAM
Updates.exe：![](https://image.3001.net/images/20220117/1642408170_61e528eac345b29c90adb.png!small)

![](https://image.3001.net/images/20220117/1642409082_61e52c7a58bedebe946cd.png!small)

还会添加自启动注册表项：![](https://image.3001.net/images/20220117/1642409120_61e52ca024f2c21efadb2.png!small)

然后会创建新的进程AAM
Updates.exe：![](https://image.3001.net/images/20220117/1642409132_61e52cacab269defcb232.png!small)

然后结束自身进程：![](https://image.3001.net/images/20220117/1642409146_61e52cba8d09ecb442c07.png!small)

新创建的进程会持续运行，并与恶意地址进行持续的通信，并且会不断地想共享目录写下恶意的快捷方式，并将病毒拷贝到共享目录。

尝试与恶意的地址进行通信：![](https://image.3001.net/images/20220117/1642409165_61e52ccd1ee855cf1d033.png!small)

写下的快捷方式，意在通过用快捷方式让内网其他用户不小心将病毒执行起来：![](https://image.3001.net/images/20220117/1642409178_61e52cdadfb5dbfee6d83.png!small)

##  ** **日常加固****

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

