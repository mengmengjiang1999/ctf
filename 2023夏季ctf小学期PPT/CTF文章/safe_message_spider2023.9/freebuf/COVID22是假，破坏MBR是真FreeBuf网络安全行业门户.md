在 COVID-19 还未结束之际，伪装成 COVID-22 安装程序的新兴恶意软件已经出现。

FortiGuard Labs 11 月中旬发现，攻击者利用疫情为诱饵，受害者一旦安装 COVID-22
恶意软件，主机将失陷无法启动，属于一种破坏性恶意软件变种。

## COVID-22

恶意软件命名为 Covid22，与 COVID-19
的命名保持一致，但与已经爆发的新冠病毒无关。攻击者将用户对这种破坏性病毒的恐惧投射到计算机上，表明该病毒可能会在 2022 年大肆传播。

尽管并不清楚恶意软件的确切分布情况，但攻击者在尝试利用恐惧来引诱受害者打开恶意软件。其实恶意软件并不复杂，但攻击者为了让受害者感到恐惧着实下了功夫。

该文件第一次手动运行时，会像正常程序一样询问用户是否想要安装 COVID-22。

![image.png-49.9kB](https://image.3001.net/images/20211124/1637750328_619e16383958b970e0162.png!small)

运行提示

一旦用户选择继续安装，恶意软件就会在强制重启计算机前释放几个恶意文件。恶意文件的名称非常简单：

> Covid22Server.exe 执行释放的 script.txt 的命令。  
> lol.vbs 会创建一个无限循环的 MessageBox，弹窗显示“你的电脑已经被 COVID-22 病毒感染！静待死机吧！”

![image.png-22.5kB](https://image.3001.net/images/20211124/1637750328_619e1638e60c346966c7f.png!small)

弹窗提示

> speakwh.vbs 通过电脑的扬声器循环播放“冠状病毒”。  
> CoronaPopup.exe 弹出一个窗口，标题为“COVID-22 已经感染电脑！”，并显示冠状病毒的图像。

![image.png-203.6kB](https://image.3001.net/images/20211124/1637750329_619e1639737ca27d8b720.png!small)

冠状病毒的图像

> ClutterScreen.exe 不断移动像素块把屏幕弄花。  
> x.vbs 会弹出提示“新冠病毒！”的消息 50 次。

![image.png-32.4kB](https://image.3001.net/images/20211124/1637750330_619e163a27f8888a6a42b.png!small)

弹窗提示

> noescapes.vbs 会弹出提示“无处可逃！”的消息 10 次。

![image.png-29kB](https://image.3001.net/images/20211124/1637750330_619e163a9349f2f82f832.png!small)

弹窗提示

> icon.exe 用红色的 X 号图标填充屏幕。

![image.png-442.5kB](https://image.3001.net/images/20211124/1637750331_619e163b645a5d9bc8323.png!small)

屏幕填充满的情况

> final.vbs 会弹出提示“再见”的消息。

![image.png-28.8kB](https://image.3001.net/images/20211124/1637750333_619e163d5579354c54f5d.png!small)

弹窗提示

这些功能通常是用于取笑用户的 Joke 类程序的典型行为，但攻击者不止于此。恶意软件还会执行 WipeMBR.exe
来破坏主引导记录（MBR），执行后将会弹出提示“COVID-22 已经安装完成！和你的电脑永别吧！”的提示并强制重新启动计算机。

![image.png-42.7kB](https://image.3001.net/images/20211124/1637750333_619e163db22bef13c5703.png!small)

重新启动前的弹窗提示

MBR
中保存着硬盘驱动器分区信息和操作系统的加载程序，所以失陷主机也不能在重启的时候正常加载操作系统。对用户来说，值得庆幸的是恶意软件并未破坏或者窃取失陷主机上的任何文件，受害者仍然可以从硬盘上恢复文件。

该恶意软件与 Sonicwall 在 2020 年 4 月中提到的另一个 MBR 擦除器功能类似，但代码上看不出什么相似之处。该恶意软件只是用零覆盖了
MBR：

![image.png-78.2kB](https://image.3001.net/images/20211124/1637750334_619e163e2d40d4daa39cb.png!small)

恶意样本部分代码

## 如何修复 MBR

现代的 Windows 机器上修复 MBR 相对容易一些， **重启后系统会自动进入修复模式** 。Windows
可以启动自动修复，或者也可以选择手动修复，如 bootrec.exe /fixmbr。

提醒管理员在外部存储上备份数据也很重要，这样才能防止任何文件被加密或者破坏。

## IOC

> [Covid22.exe]  
> 79f3b39797f0e85d9e537397a6f8966bc288d1b83ae1c313c825fbd17698879e  
> [ClutterScreen.exe]  
> 726DC8D52C9CF794412941BFBD27AF8F6FA27E72154A63F5C81A42BA40BD972D  
> [CoronaPopup.exe]  
> 80C9F65617386940153CC4D42E1097DEB79B4F9C98C67E6025BDC1CA03AD8FB7  
> [icons.exe]  
> 496CABBD18530780A3CB75340BDDD7F74A71E84C83DF4D185CFC6EC71D14C41E  
> [WipeMBR.exe]  
> 5FC9080177A096DE2B717F2F2196867B6966900E129E5BC4E412D5DCA7ED9E60  
> [final.vbs]  
> EA2EF4196586BF851D4DC422A04D51AD2CB552BF5AAE2DF361D1ED2D4842B4BA  
> [lol.vbs]  
> C88D3022B25EF86CD19CE99815AD26A1F9A201F69974577DA93E08328E047410  
> [noescapez.vbs]  
> 3D519FC10BC2B6CAA5A27069DA55B1614CC97C1DFD4BCDC1DD7F36E686D913F1  
> [x.vbs]  
> E22F004CF9E7C4C7B52BDA59DB2B57816992CB01FDBEF6675760FDD7BCD29728  
> [speakwh.vbs]  
> 4624876389F6DDFB111FBBF3473D7C6B5555ED8A0F31C37E822A6FFEF5E27DE0  
> [Covid22Server.exe]  
> 0C6DFAA12A98FB17058B79D283E96A3E34549D0AD2BE58F505AC8ABDE858D8A6

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/to-joke-or-not-to-> joke-covid-22-brings-disaster-to-mbr)

