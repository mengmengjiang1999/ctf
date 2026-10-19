## **事件背景**

近日，深信服终端安全团队接到用户反馈，共享盘下的文件都神秘消失了，只剩下一个“_”文件夹：

![](https://image.3001.net/images/20210723/1627012831_60fa3edf532ca130e395c.png!small)

经安全人员分析发现，此现象是感染了一种名为DeviceManager的蠕虫病毒，该蠕虫病毒不仅会修改防火墙的策略、感染网络磁盘进行传播、感染本地压缩文件，还会访问恶意网站下载并运行恶意文件，由于病毒母体总以“DeviceManager”命名，因此被称为DeviceManager蠕虫病毒：

![](https://image.3001.net/images/20210723/1627012842_60fa3eea7deb4f526d434.png!small)

该蠕虫内置了大量域名进行遍历解析，直到其中一个仍活跃的域名解析成功，则尝试下载其他恶意文件。根据威胁情报查询其中一个域名，创建时间为2021年5月份，说明该蠕虫病毒很可能仍在继续更新其恶意组件：

![](https://image.3001.net/images/20210723/1627012855_60fa3ef7842a5118b14d3.png!small)

##  **样本分析**

###  **基本功能**

  * 对抗静态检测

使用了混淆和加密的方式，执行后会先对shellcode进行Tea解密，然后在内存中进行PE替换，替换掉原始的PE文件，并修复DOS头、导入表等：

![](https://image.3001.net/images/20210723/1627012872_60fa3f08793be4a6938b3.png!small)

  * 添加自启动

通过写入注册表实现开机自启动：

![](https://image.3001.net/images/20210723/1627012885_60fa3f1504e4ae879ecce.png!small)

  * 修改安全策略

修改防火墙策略：

![](https://image.3001.net/images/20210723/1627012895_60fa3f1f3151c41b2eeb9.png!small)

禁用Windows Defender：

![](https://image.3001.net/images/20210723/1627012905_60fa3f291c07864b12bdf.png!small)

禁用安全通知：

![](https://image.3001.net/images/20210723/1627012917_60fa3f3561cc39d787f59.png!small)

禁用系统还原：

![](https://image.3001.net/images/20210723/1627012926_60fa3f3e3f3d74914c0f0.png!small)

###  **传播及感染**

感染软盘、网络磁盘，将软盘、网络磁盘中的文件隐藏在"_"文件夹下，通过写入恶意快捷方式、inf文件等形式引诱用户运行木马文件；写入DeviceManager.exe文件，该文件是木马文件，存放于"_"目录下：

![](https://image.3001.net/images/20210723/1627012947_60fa3f531f1945cf6194a.png!small)

写入autorun.inf文件，自动运行路径指向DeviceManager.exe文件：

![](https://image.3001.net/images/20210723/1627012959_60fa3f5f385b33ced3243.png!small)

创建恶意快捷方式，命令行参数为"/c start _ & _\DeviceManager.exe &
exit"，即打开该快捷方式跳转到"_"文件夹，同时运行DeviceManager.exe恶意文件：

![](https://image.3001.net/images/20210723/1627013233_60fa4071ae6a30333c926.png!small)

删除根目录下所有.lnk、.vbs、.bat、.js、.scr、.com、.jse、.cmd、.pif、.jar、.dll文件：

![](https://image.3001.net/images/20210723/1627013286_60fa40a6aea154d4c8733.png!small)

将所有文件存放至"_"文件夹：

![](https://image.3001.net/images/20210723/1627013515_60fa418b40b0b0efe0112.png!small)

2、通过感染本地压缩包文件、网络服务目录下的exe文件实现更大面积的传播。遍历磁盘，感染zip、rar、7z、tar格式的文件。

![](https://image.3001.net/images/20210723/1627013160_60fa40282f132a8d3e271.png!small)

3、感染网络服务目录下的所有exe文件，网络服务目录包括public_html、htdocs、httpdocs、wwwroot、ftproot、share、income。

![](https://image.3001.net/images/20210723/1627013152_60fa40201cf602917dac9.png!small)

###  **网络功能**

通过逐一连接程序中硬编码的302个恶意域名，直到成功解析，然后下载执行其他恶意文件和组件，部分恶意域名如下：

![](https://image.3001.net/images/20210723/1627013140_60fa40145525ed66f6004.png!small)

循环访问域名下载恶意文件：

![](https://image.3001.net/images/20210723/1627013120_60fa4000a857ea13afbd0.png!small)

##  **加固和防御**

> 关闭不必要的文件共享；
>
> 使用安全软件定期对主机进行全盘查杀，开启文件实时监控。

