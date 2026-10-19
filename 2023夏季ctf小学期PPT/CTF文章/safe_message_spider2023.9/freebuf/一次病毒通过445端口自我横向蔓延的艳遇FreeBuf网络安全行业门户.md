**有一天，发现内网一台主机不停的向所在网段的445端口发SYN, 于是登录这台主机用命令 >netstat -ano |findstr 445
看到如下截图的状态，此主机的行为主动而特别恶劣。**

![](https://image.3001.net/images/20190118/1547792060_5c416ebc1428d.png!small)

除了一大片的61260进程外，居然有94248的进程经常已经ESTABLISHED了，结合Windows任务管理器发现ESTABLISHED进程对应用程序目录为：C:\Windows\AppDiagnostics\

![](https://image.3001.net/images/20190118/1547792504_5c417078762f9.png!small)

进到对应目录C:\Windows\AppDiagnostics\下看到如下可疑文件：

![](https://image.3001.net/images/20190118/1547792690_5c41713250f8a.png!small)

循着文件夹名称AppDiagnostics网上查找了一下，据专业安全网友或安全厂商介绍该病毒是一个名叫更新版NSRminer加密货币挖矿机
或者WannaMine升级到V3.0版本的东东在利用MS17-010/Eternal
Blue啥啥的漏洞在作怪2018年11月份开始从越南流行，这么快就到中国了，赶紧看看怎么查杀吧，根据网友介绍：

第一步先后停止病毒感染服务snmpstorsrv与spooler与结束对应PID进程（61260、94248）如下截图：

![](https://image.3001.net/images/20190118/1547793512_5c41746828ad8.png!small)

![](https://image.3001.net/images/20190118/1547793552_5c41749062486.png!small)

![](https://image.3001.net/images/20190118/1547793977_5c41763967378.png!small)

第二步删除病毒文件夹AppDiagnostics（C:\Windows\目录下 ） 和文件
MarsTraceDiagnostics.xml（C:\Windows\System32\MarsTraceDiagnostics.xml目录下 ）
如下截图，同时在删除时提示文件夹创建于2018年12月14日 14:01分。

![](https://image.3001.net/images/20190118/1547794061_5c41768dcd461.png!small)

![](https://image.3001.net/images/20190118/1547801777_5c4194b1a7a6c.png!small)

第三步开启感染服务 snmpstorsrv与spooler
测试发现不再有针对445端口的SYN_SENT如下截图所示：（注：不删除C:\Windows\System32\下的MarsTraceDiagnostics.xml文件时开启感染服务
snmpstorsrv与spooler后病毒文件夹AppDiagnostics又被写入到C:\Windows\目录下了，针对于445端口的SYN_SENT又开始了，由此看来感染过的服务已不是原来的服务了，还需要进一步的清洗。
）

![](https://image.3001.net/images/20190118/1547794481_5c41783115757.png!small)

## 总结

问题从表面看好像是得到了控制，但听大佬们说病毒感染过的主机，不是这两下能处理干净的，还要分析怎么感染的，感染的文件注册表是否已处理干净，利用的漏洞有没有真正修复，后面有一大堆工作本菜鸟目前无法写了，希望大佬们多多指点。。。

 ***本文作者：Qianng，转载请注明来自FreeBuf.COM**

