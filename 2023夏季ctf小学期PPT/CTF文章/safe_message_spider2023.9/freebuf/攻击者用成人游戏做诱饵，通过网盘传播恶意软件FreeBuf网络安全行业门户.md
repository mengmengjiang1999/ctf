近日，安全研究人员发现 DDoS IRC Bot 恶意样本正伪装成成人游戏通过网盘进行传播。在韩国，Webhards
是恶意软件经常利用的投递渠道，过去发现传播过 njRAT 和 UDP RAT。

## 通过 Webhards 分发的 UDP RAT

之前发现通过 Webhards 分发的 UDP RAT
与本次发现的恶意样本，应该是同一伙攻击者运营的。首先，二者都是假借成人游戏的幌子进行传播，此外，在下载了 DDoS Bot 后也使用了 UDP RAT。

有一个不同之处在于，之前的 Downloader 是使用 C# 编写的，现在改用 Golang 开发。与 UDP RAT 一起使用的 DDoS Bot
是从开源的 Simple-IRC-Botnet（使用 Golang 开发的 DDoS IRC Bot）修改而来。

![image.png-233.7kB](https://image.3001.net/images/20220120/1642675812_61e93e64011521f38f771.png!small)Simple-IRC-Botnet 项目

由于 Golang 的开发难度较低且原生支持跨平台，正在被各种攻击者广泛使用。在韩国发现的各种恶意软件，使用 Golang 的比例也正在增加。

如下所示，攻击者将恶意软件伪装成成人游戏上传到网盘。

![image.png-160.2kB](https://image.3001.net/images/20220120/1642675813_61e93e65097d8ea9a990e.png!small)网盘截图

虽然不确定上传文件的用户是否为攻击者，但攻击者发的很多类似的贴子都在分发相同的恶意软件。尽管，每个宣称的成人游戏都不相同，但压缩文件中的恶意软件都相同。

![image.png-153.7kB](https://image.3001.net/images/20220120/1642675813_61e93e658956b271c294a.png!small)攻击者发布的贴子

分发涉及的成人游戏如下所示：

序号| 名称  
---|---  
1| [19 Korean version] Naughty Mage’s EXXXXX Life  
2| [19 Korean version] The Reason She Became a Slave  
3| [19 Korean version] Refraining of Heavenly Walk  
4| [19 Korean version] Exchange Diary of Violation  
5| [19 Korean version] Girl From Tea Ceremony Club  
6| [19 Korean version] Curse of Lilia  
7| [19 Korean version] Academy with Magical Girls  
8| [19 Korean version] Monster Fight  
9| [19 Korean version] Dreamy Lilium  
10| [19 Korean version] Enraged Department Manager  
11| [19 Korean version] Fancy Days of Sayuri  
12| [19 Korean version] Sleif Corporation  
13| [19 Korean version] Country Girl Exposure  
14| [19 Korean version] Sylvia and Master of Medicine  
15| [19 Korean version] Assassin Asca  
16| [19 Korean version] How to Reform Your Girlfriend  
17| [19 Korean version] Creating Utopia with Subjugation Skill  
18| [19 Korean version] Uriel and Belial  
19| [19 Korean version] The Case of Chairperson Kana  
20| [19 Korean version] Princess Round  
21| [19 Korean version] Flora and the Root of the World Tree  
22| [19 Korean version] Midnight Exposure  
23| [19 Korean version] Modern Day Elf  
24| [19 Korean version] Research Data of Homunculus  
  
将压缩文件解压后，如下所示。通常，用户会点击 `Game_Open.exe`运行游戏。

![image.png-480.3kB](https://image.3001.net/images/20220120/1642675814_61e93e669dff728ba056c.png!small)伪装成
Game_Open.exe 的恶意软件

但其实 `Game_Open.exe`并不是游戏的启动器，而是用来运行其他恶意软件的可执行文件。程序执行后，将相同路径下的 `PN`更名为
`scall.dll`并执行。再将原始的游戏可执行文件 `index`更名为 `Game.exe`并运行。以此，让用户以为是自己的点击触发了游戏的正常执行。

![image.png-457.1kB](https://image.3001.net/images/20220120/1642675816_61e93e6896a5cbb4e344d.png!small)游戏截图

执行成功后，`Game_Open.exe`文件将被隐藏。而 `scall.dll`会将同一路径下的 `srt`文件移动到 `C:\Program
Files\EdmGen.exe`。

![image.png-250.1kB](https://image.3001.net/images/20220120/1642675817_61e93e69b0d359ce3935a.png!small)恶意软件位置

紧接着进行持久化驻留：

    
    
    “C:\Windows\System32\cmd.exe” /c SCHTASKS /CREATE /SC ONSTART /NP /TN “Windows Google” /TR “C:\Program Files\EdmGen.exe”

`EdmGen.exe`会运行正常程序 `vbc.exe`并将恶意代码注入其中。注入后，该样本就变成了一个使用 Golang 开发的 Downloader。

如下所示，恶意软件定期与 C&C 服务器通信，获取后续的恶意样本。

![image.png-183.4kB](https://image.3001.net/images/20220120/1642675818_61e93e6aa2d3ae44b6d51.png!small)通信代码

下载地址为 `http://node.kibot.pw:8880/links/01-13`，本地路径为 `C:\Down\discord_[random
characters]\[malware name]`。

## Simple-IRC-Botnet

之前安装的 UDP RAT，目前安装的是使用 Golang 开发的 Simple-IRC-Botnet。

这种 DDoS Bot 使用 IRC 协议与 C&C 服务器通信，与 UDP RAT 只支持 UDP 洪水不同，它支持
Slowris、Goldeneye、Hulk DDoS 等方式的攻击。

![image.png-100.8kB](https://image.3001.net/images/20220120/1642675819_61e93e6b58eb2cf374c76.png!small)样本代码

Golang DDoS IRC Bot 会连接到特定的 IRC 服务器并进入攻击者创建的频道，接收到攻击者指令时，对目标进行 DDoS 攻击。

## IRC 通信

Golang DDoS IRC Bot 恶意软件使用的 IRC 服务器如下所示：

    
    
    210.121.222.32:6667157.230.106.25:666789.108.116.192:6667176.56.239.136:6697

![image.png-184kB](https://image.3001.net/images/20220120/1642675819_61e93e6bd9cafb65e51e7.png!small)进入
IRC 频道

![image.png-302.2kB](https://image.3001.net/images/20220120/1642675821_61e93e6d182a9f41e1f8c.png!small)攻击指令下发

这些恶意软件正在韩国通过 webhards 等文件共享网站广泛传播，建议用户下载时需要小心注意。

## IOC

> affbad0bedccbf1812599fbce847d917  
> b21ad73be72280ae30d8c5556824409e  
> 889289d9d97f7c31925a451700b4b7ac  
> 2a7de90437c66b3f2304630c3324e2de  
> f14c51ca5d7afc1128cceca5d5a5694b  
> 41320f572cdf14abc1401a72a24a621d  
> d38803b3f7c0faac71a3e572e9214891  
> 5d97a32e47dfa54dd1bebde208252b88  
> 12baeacfd0ac2d66c5959d6305a4fe50  
> b621005a147ef842fbc7198c8431724c  
> ba43e4c84da7600881ed5ccac070e001  
> b6ad8550dcd317a49c6e563a1188d9f0  
> db2db486b828182c827e4fdfc292e143  
> 4c1777b5763bc7655d1ca89ae4774470  
> 2357c1c6027f21094fa62a35300a96ae  
> 28566a08334f37d7a8d244c393e9ad33  
> 4b3eff9f394ebd2231c5c0b980c62e63  
> 74834f29dd5d244742879c2d800e8a53  
> 4b3eff9f394ebd2231c5c0b980c62e63  
> 42a344fbad7a56e76c83013c677330ac  
> 6b029fc7a0f480b7dd6158bba680e49b  
> 5a74ea453f0b424770fdddaf470f5eae  
> 12c97b2481efe448b93b72b80eb96563  
> 1f993f08ed40f6b03db7f78ab8e087a5  
> 005247fa9b312eb449150b52b38e0a4c  
> 1f2147b2a0caeb43a9a3bcaf42808581  
> 63ff6d1bb53cdd2d7b7fca856826c8b6  
> bff341b0c95eda801429a4b5c321f464  
> 0fd264b12ea39e39da7807a117718429  
> af486a4e9fdc62ac31f8424a787a460c  
> 2160629e9def4c9482b4fb642c0cd2d8  
> 51cfd6c6390ce99979350a9a21471d30  
> 194fb8590e1218f911870c54b-5830f16  
> 7b73a4e6e504800e256495861d0c9f78  
> 57568755bac3f20fffb970a3c6386a43  
> 55b6e07ff120b6c2e784c8900333aa76  
> bc18d787c4d886f24fa673bd2056e1ed  
> 5be1ab1d5385d5aeadc3b498d5476761  
> 1bc93ee0bd931d60d3cd636aa35176e3  
> a2fc31b9c6a23e0a5acc591e46c61618  
> 977c52d51d44a0a9257017b72cfafab1  
> 98e4f982363c70bd9e52e5a249fce662  
> 7f3bd23af53c52b3e84255d7a3232111  
> 00b9bf730dd99f43289eac1c67578852  
> 90bfa487e9c5e8fe58263e09214e565b  
> 2fe8262d0034349a030200390b23b453  
> 8053b24878c4243d8eda0ccae8905ccb  
> http://organic.kibot.pw:2095/links/12-20  
> http://node.kibot.pw:2095/links/12-20  
> http://node.kibot.pw:2095/links/12-25  
> http://node.kibot.pw:8880/links/12-28  
> http://miix.kibot.pw:8880/links/12-28  
> http://node.kibot.pw:8880/links/12-28  
> http://node.kibot.pw:8880/links/01-13  
> 195.133.18.27:1234  
> 195.133.18.27:8080  
> 195.133.18.27:9997

## 参考来源

> [ASEC](https://asec.ahnlab.com/en/30755/)

