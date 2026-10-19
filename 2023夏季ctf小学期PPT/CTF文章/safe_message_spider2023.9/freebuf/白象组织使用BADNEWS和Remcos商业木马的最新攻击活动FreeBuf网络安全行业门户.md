![1685071477_647026750c1a7fe6149ab.png!small?1685071478402](https://image.3001.net/images/20230526/1685071477_647026750c1a7fe6149ab.png!small?1685071478402)

  

## **01** **概述**

白象/WhiteElephant是具有印度背景的APT组织，其攻击活动最早可追溯到2009年11月，安天将该组织中文命名为白象。2016年安天发布了[《白象的舞步——来自南亚次大陆的网络攻击》[1]](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650169803&idx=1&sn=b329ecfb9f42c67abaa95e6ee60329aa&chksm=beb9c2f989ce4beff57a8520094dfd5b6c83bb959efb6ef0810c91422c2325e253df65dc51c0&scene=21#wechat_redirect)，在国内首次披露了白象组织的攻击活动，2017年发布《潜伏的象群——来自南亚次大陆的系列网络攻击活动》[2]，再次披露两起该组织针对我国的网络攻击活动，并在此之后持续跟踪该组织的攻击动向，对捕获到的攻击进行分析、关联、溯源工作。白象的攻击目标涉及非常广泛的国家和地区分布，但主要目标是中国和巴基斯坦。该组织具备Windows、Android、macOS多平台攻击能力，擅长使用政治热点话题作为诱饵进行鱼叉攻击，并不断升级其攻击技术，以达到更好的免杀效果。

近期，安天CERT捕获到一起白象组织针对我国相关单位的攻击活动。在本次攻击活动中，攻击者向目标投递钓鱼邮件，邮件附件为一个包含恶意LNK文件的压缩包，LNK文件用于下载BADNEWS远控木马，最终实现对目标的信息窃取、远程控制等功能。

进一步关联分析发现，LNK系列攻击与近期针对南亚地区的军事政治等目标的网络攻击相关，关联到的攻击使用技术成熟的商业远控工具如Remcos，也是通过LNK类型诱饵，或文件名以军政题材命名的EXE程序、钓鱼网站等作为攻击前导，为此攻陷、注册了相当数量的网络基础设施来支撑载荷分发和控制通联。分析研判后发现关联到的攻击具有明显的印度方向背景，攻击目标暂不涉及我国，目前仅发现与白象组织存在数字证书上的关联重叠。

  

##  **02** **针对我国相关单位的攻击活动**

###  **2.1 LNK** **文件**

表2-1 恶意LNK文件

![1685078302_6470411e75ba215b78c47.png!small?1685078303720](https://image.3001.net/images/20230526/1685078302_6470411e75ba215b78c47.png!small?1685078303720)

攻击者将包含恶意LNK文件的压缩包作为邮件附件发送给目标，恶意LNK文件伪装成pdf文档诱导攻击者打开执行。

![1685071502_6470268e4dcc63498903b.png!small?1685071503587](https://image.3001.net/images/20230526/1685071502_6470268e4dcc63498903b.png!small?1685071503587)

图2‑1 压缩包内双后缀的诱饵文件

LNK文件执行后会从https://msit5214.b-cdn.net/abc.pdf处下载诱饵文件并打开，而后从https://msit5214.b-cdn.net/c处下载后续载荷到C:\ProgramData\Microsoft\DeviceSync并将其命名为OneDrive.exe，最后将其添加到计划任务中执行。

![1685071513_64702699512656a94106d.png!small?1685071514653](https://image.3001.net/images/20230526/1685071513_64702699512656a94106d.png!small?1685071514653)

图2‑2 LNK文件中提取出的代码

###  **2.2 BADNEWS** **木马**

表2-2 BADNEWS木马

![1685078354_647041524bbcbdcd90a38.png!small?1685078356129](https://image.3001.net/images/20230526/1685078354_647041524bbcbdcd90a38.png!small?1685078356129)

OneDrive.exe文件为白象组织的BADNEWS远程控制木马，用于实现文件下载、命令执行、屏幕截图等功能。OneDrive.exe的数字签名信息如下。

![1685071573_647026d5491b5afbaf801.png!small?1685071574617](https://image.3001.net/images/20230526/1685071573_647026d5491b5afbaf801.png!small?1685071574617)

图2‑3 数字签名信息

  

BADNEWS木马执行后，首先判断机器的时区。若检测结果为中国标准时区，则会进行后续恶意操作。

![1685071696_64702750ed21d86e4d5b2.png!small?1685071698309](https://image.3001.net/images/20230526/1685071696_64702750ed21d86e4d5b2.png!small?1685071698309)

图2‑4 判断是否为中国标准时区

  

接着创建互斥量qzex，确保当前环境下该进程唯一，而后使用SetWindowsHookExW函数注册键盘钩子。

![1685071781_647027a55e78ce153f91e.png!small?1685071782705](https://image.3001.net/images/20230526/1685071781_647027a55e78ce153f91e.png!small?1685071782705)

图2‑5 创建互斥量，注册键盘钩子

  

窃取的键盘记录将会存放到%temp%\kednfbdnfby.dat文件。

![1685071892_64702814ea64494bf8325.png!small?1685071895710](https://image.3001.net/images/20230526/1685071892_64702814ea64494bf8325.png!small?1685071895710)

图2‑6 键盘记录存放到kednfbdnfby.dat

  

使用正常的Web服务myexternalip.com、api.ipify.org、ifconfig.me获取主机IP外网地址。

![1685071986_647028720984a81d50d58.png!small?1685071987535](https://image.3001.net/images/20230526/1685071986_647028720984a81d50d58.png!small?1685071987535)

图2‑7 获取主机外网IP

  

将前面获取到的外网IP在api.iplocation.net、ipapi.co 的Web服务中查询，获取外网IP所属国家的名称。

![1685072003_64702883892383dd09fa0.png!small?1685072004950](https://image.3001.net/images/20230526/1685072003_64702883892383dd09fa0.png!small?1685072004950)

图2‑8 获取外网IP所属国家

  

将获取到的加密信息拼接成一个字符串，用于后续作为心跳包的内容回传到C2服务器。

![1685072062_647028be77fbe2cf36cbc.png!small?1685072063888](https://image.3001.net/images/20230526/1685072062_647028be77fbe2cf36cbc.png!small?1685072063888)

图2‑9 回传的信息内容

  

在目标机中收集的数据类型如下所示：

表2-3 收集的数据类型

![1685078414_6470418e9fd976efb4057.png!small?1685078416191](https://image.3001.net/images/20230526/1685078414_6470418e9fd976efb4057.png!small?1685078416191)

收集到的信息首先进行Base64编码，而后通过AES-CBC-128加密，然后再进行一次Base64编码。加密使用的AES密钥为“qgdrbn8kloiuytr3”，IV为“feitrt74673ngbfj”。

![1685072094_647028decd63697297190.png!small?1685072096219](https://image.3001.net/images/20230526/1685072094_647028decd63697297190.png!small?1685072096219)

图2‑10 数据加密

  
创建3个线程同C2服务器通信，C2地址为charliezard.shop，通信端口为443端口，URI为/tagpdjjarzajgt/cooewlzafloumm.php。每个线程分别承担不同的工作，通信内容采用AES-CBC-128加密数据。

![1685072402_64702a1254dda785a2573.png!small?1685072403836](https://image.3001.net/images/20230526/1685072402_64702a1254dda785a2573.png!small?1685072403836)

图2‑11 创建线程通信

  

sub_409900线程函数用于发送收集的基本信息，验证目标机器是否处于开机状态。

![1685072428_64702a2c75aef13bfa79b.png!small?1685072429783](https://image.3001.net/images/20230526/1685072428_64702a2c75aef13bfa79b.png!small?1685072429783)

图2‑12 发送心跳包

  

sub_4092A0线程函数用于实现远程控制功能。攻击者下发执行的格式为：指令$参数1$参数2，参数2并未使用。

![1685072442_64702a3a2054960ca3f01.png!small?1685072443743](https://image.3001.net/images/20230526/1685072442_64702a3a2054960ca3f01.png!small?1685072443743)

图2‑13 获取指令并执行相应功能

  

对比以往的BADNEWS各个控制命令的实现，发现该组织并未同先前攻击活动[3]中一样将执行结果保存到文件，而是直接将数据加密后回传到C2服务器，BADNEWS中存在的指令代码及对应功能如下所示：

表2-4 指令代码及对应功能

![1685078471_647041c7005cf4adecdec.png!small?1685078472391](https://image.3001.net/images/20230526/1685078471_647041c7005cf4adecdec.png!small?1685078472391)

  

sub_409440线程函数用于执行cmd命令收集信息（包括当前用户名、网络配置、DNS缓存、系统信息、进程列表），然后将信息加密后添加到endfh参数回传至C2服务器。

![1685072469_64702a55b2bf02c960177.png!small?1685072471327](https://image.3001.net/images/20230526/1685072469_64702a55b2bf02c960177.png!small?1685072471327)

图2‑14 收集系统信息

###  **2.3** **归因分析**

此次释放的木马OneDrive.exe在代码结构、加密算法、通信模式等方面和白象组织以往攻击活动中使用的BADNEWS木马相似，并且BADNEWS木马的存放路径C:\ProgramData\Microsoft\DeviceSync也是该组织常用文件路径。

以往攻击活动中利用CVE-2017-11882漏洞释放的BADNEWS木马存放路径。

![1685072484_64702a64c32b2167d55fd.png!small?1685072486123](https://image.3001.net/images/20230526/1685072484_64702a64c32b2167d55fd.png!small?1685072486123)

图2‑15 以往攻击活动中CVE-2017-11882漏洞释放的BADNEWS木马存放路径

本次攻击活动中BADNEWS木马存放路径。

![1685072493_64702a6d22852fb9e94fd.png!small?1685072494750](https://image.3001.net/images/20230526/1685072493_64702a6d22852fb9e94fd.png!small?1685072494750)

图2‑16 本次攻击活动中BADNEWS木马存放路径

以往攻击活动BADNEWS木马中存在的系统时区检测代码。

![1685072514_64702a820fbd341254d9b.png!small?1685072515411](https://image.3001.net/images/20230526/1685072514_64702a820fbd341254d9b.png!small?1685072515411)

图2‑17 以往攻击活动BADNEWS木马中存在的系统时区检测代码

本次攻击活动BADNEWS木马中存在的系统时区检测代码。

![1685072522_64702a8a0cb997771bca7.png!small?1685072523347](https://image.3001.net/images/20230526/1685072522_64702a8a0cb997771bca7.png!small?1685072523347)

图2‑18 本次攻击活动BADNEWS木马中存在的系统时区检测代码

  

##  **03** **针对南亚军政目标的攻击活动**

对上述攻击活动使用到的BADNEWS木马进行关联分析，发现与近期针对南亚地区的军事政治等目标的网络攻击存在相关性。关联到的攻击通过LNK类型诱饵，或文件名以军政题材命名的EXE程序、钓鱼网站等作为攻击前导，大量使用商业木马Remcos实现远程控制，获取目标敏感信息。

###  **3.1 Remcos** **商业远控木马**

表3-1 Remcos远控木马

![1685078516_647041f42140e554ccc89.png!small?1685078517382](https://image.3001.net/images/20230526/1685078516_647041f42140e554ccc89.png!small?1685078517382)

Remcos是一款商业远控木马，包括实现远程桌面控制、屏幕窃取、剪切板窃取、摄像头及音频窥视、命令执行、浏览器窃密、密码窃取、创建代理等丰富功能，能对文件、进程、服务、窗口、注册表、网络等信息进行收集和管理。

![1685072536_64702a980c33983a10ec5.png!small?1685072537484](https://image.3001.net/images/20230526/1685072536_64702a980c33983a10ec5.png!small?1685072537484)

图3‑1 官方Remcos Professional产品界面介绍

##

###  **3.2** **与白象组织的关联分析**

3.2.1 数字证书关联

根据上述针对我国相关单位的攻击活动中BADNEWS木马的数字签名信息，可以关联到具备该签名的恶意文件。

![1685072548_64702aa4d96ed05ad47d0.png!small?1685072550191](https://image.3001.net/images/20230526/1685072548_64702aa4d96ed05ad47d0.png!small?1685072550191)

图3‑2 本次攻击活动BADNEWS木马中存在的数字证书

  

使用该签名的文件数量并不多，其中包含名为Minutes-of-Meeting-Joint-Ops.exe的木马样本，样本在今年2月22日从孟加拉国上传，为Remcos远控家族，C2地址为45.137.116.253:443 (TCP)。

同样访问45.137.116.253:443
(TCP)地址的木马还包括其他文件名为军政题材的Remcos远控，其中fatima.exe的母体为此前未见的下载器：

表3-2 IP 45.137.116.253关联到的恶意文件

![1685078613_64704255d4694a3a7371b.png!small?1685078615280](https://image.3001.net/images/20230526/1685078613_64704255d4694a3a7371b.png!small?1685078615280)

托管这些Remcos远控程序的傀儡网站merafm.com是巴基斯坦最受欢迎的无线电广播公司MERA
FM的网站，进一步分析基本确定该网站是被入侵，用于挂载攻击者大量的恶意文件，文件梳理列表如下：

表3-3 merafm.com网站关联到的恶意文件

![1685079025_647043f1a3e66e5c11fc4.png!small?1685079027298](https://image.3001.net/images/20230526/1685079025_647043f1a3e66e5c11fc4.png!small?1685079027298)

恶意文件的工具能力和IoC梳理如下：

表3-4 恶意文件的工具能力和IoC

![1685079132_6470445c72e48eafbb8bd.png!small?1685079133756](https://image.3001.net/images/20230526/1685079132_6470445c72e48eafbb8bd.png!small?1685079133756)

3.2.2 样本同源关联

基于以上样本，通过在文件元数据、代码、资产等同源层面进行关联拓线，关联到多个样本如下表：

表3-5 上述样本关联到的恶意文件

![1685079237_647044c5de5d9d538d479.png!small?1685079239411](https://image.3001.net/images/20230526/1685079237_647044c5de5d9d538d479.png!small?1685079239411)

恶意文件的工具能力和IoC梳理如下：

表3-6 恶意文件的工具能力和IoC

![1685079289_647044f99003dae338092.png!small?1685079291013](https://image.3001.net/images/20230526/1685079289_647044f99003dae338092.png!small?1685079291013)

其中dllhostSvc.exe的执行母体是名为Password.lnk的恶意快捷方式，LNK被打包在压缩包中，压缩包之中存在加密的word文档以及名为Password.lnk的恶意快捷方式，诱导目标打开快捷方式获取密码，手段与上文中针对中国的LNK诱饵较为类似：

![1685072581_64702ac50f7dc679e94fc.png!small?1685072582388](https://image.3001.net/images/20230526/1685072581_64702ac50f7dc679e94fc.png!small?1685072582388)

图3‑3 压缩包内的文件

![1685072587_64702acbd6eacfe60ee5f.png!small?1685072589211](https://image.3001.net/images/20230526/1685072587_64702acbd6eacfe60ee5f.png!small?1685072589211)

图3‑4 加密的word文档

  

Password.lnk通过调用mshta.exe执行远程端HTA文件中包含的PowerShell代码，下载https://webmail.mod.com.pk/uploads/adrean.exe，并将其重命名为%localappdata%\dllhostSvc.exe执行。

3.2.3 网络资产关联

针对南亚攻击活动的相关网络资产主要以自有域名、自有IP和傀儡网站三种类别组成。

  

其中自有域名包括命名上与官方相似的域名，以及Whois注册地址伪装成受害者所在地的域名。这些域名大多数用于给下载器响应载荷，其中webmail.mod.com.pk既作为载荷分发又作为钓鱼盗号网站：

![1685072598_64702ad6150a7dbb98168.png!small?1685072599322](https://image.3001.net/images/20230526/1685072598_64702ad6150a7dbb98168.png!small?1685072599322)

图3‑5 针对孟加拉警察的Outlook登录钓鱼网站

  

表3-7 域名信息及用途

![1685079386_6470455acbe4b1229146f.png!small?1685079388588](https://image.3001.net/images/20230526/1685079386_6470455acbe4b1229146f.png!small?1685079388588)

  
自有IP为Remcos远控的C2地址，多为443端口且同属德国云服务提供商combahton
GmbH，控制端口存在测绘扫描特征，截至报告撰写时可测得IP共计8个，梳理信息如下：

  

表3-8 IP地址信息

![1685079449_6470459967ff212d892e5.png!small?1685079450887](https://image.3001.net/images/20230526/1685079449_6470459967ff212d892e5.png!small?1685079450887)

傀儡网站目前仅发现merafm.com，从恶意文件挂载路径来看有可能是漏洞攻击后通过恶意上传完成。

  

##  **04** **威胁框架映射**

本次捕获到的白象组织针对我国相关单位攻击活动共涉及ATT&CK框架中8个阶段的19个技术点，具体行为描述如下表：

  

表4-1 本次白象针对我国相关单位攻击活动的技术行为描述表

![1685079490_647045c2972c897d02a29.png!small?1685079492429](https://image.3001.net/images/20230526/1685079490_647045c2972c897d02a29.png!small?1685079492429)

  
  

将涉及到的威胁行为技术点映射到ATT&CK框架如下图所示：

![1685077289_64703d290e9c1290220c0.png!small?1685077290634](https://image.3001.net/images/20230526/1685077289_64703d290e9c1290220c0.png!small?1685077290634)

图4‑1 本次白象针对我国相关单位攻击活动对应ATT&CK映射图

  

##  **05** **总结**

综上所述，安天CERT近期发现的LNK系列攻击，由印度的白象APT组织发起，攻击者疑似通过钓鱼攻击投递专用远控木马，相关的攻击手法和代码与以往的白象组织的攻击特征保持一致。通过样本数字证书关联的Remcos商业木马来自针对南亚地区攻击活动，攻击者大量使用Remcos商业木马针对军事政治等目标。除安天发现白象组织使用Remcos商业木马外，斯洛伐克厂商ESET[4]也发现了印度肚脑虫（Donot）组织使用了Remcos商业木马，两个印度组织都开始使用Remcos商业木马，可以看出印度组织进一步尝试购买商业木马纳入为自己的攻击武器，降低成本的同时依托商业木马提高网络攻击活动效率。

  

# 参考资料

[1]
[白象的舞步——来自南亚次大陆的网络攻击](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650169803&idx=1&sn=b329ecfb9f42c67abaa95e6ee60329aa&chksm=beb9c2f989ce4beff57a8520094dfd5b6c83bb959efb6ef0810c91422c2325e253df65dc51c0&scene=21#wechat_redirect)

https://www.antiy.com/response/WhiteElephant/WhiteElephant.html

  

[2] 潜伏的象群——来自南亚次大陆的系列网络攻击活动

https://www.antiy.com/response/The_Latest_Elephant_Group.html

  

[3]
[白象组织近期网络攻击活动分析](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650193918&idx=1&sn=091cfb4be7e16d955b77c45518451cac&chksm=beb91ccc89ce95dab306b93defa63760c09b723763ca75bbc66619752d70e8240192636b58d1&scene=21#wechat_redirect)

https://www.antiy.com/response/20221027.html  
  

[4] ESET APT Activity Report: Attacks by China-, North Korea-, and Iran-aligned threat actors; Russia eyes Ukraine and the EU

https://www.eset.com/int/about/newsroom/press-releases/research/eset-apt-activity-report-attacks-by-china-north-korea-and-iran-aligned-threat-actors-russia-eyes-ukr/

  

