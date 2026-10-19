**近期，国外安全公司ESET发布了恶意软件Ramsay针对物理隔离网络的攻击报告，** **本文针对该物理隔离网络的一些攻击进行技术层面的分析。**

## 一、背景

近期，国外安全公司ESET发布了恶意软件Ramsay针对物理隔离网络的攻击报告（ **见参考链接1**
）。所谓物理隔离网络，是指采用物理方法将内网与外网隔离，从而避免入侵或信息泄露的风险的技术手段。物理隔离网络主要用来解决网络安全问题，尤其是在那些需要绝对保证安全的保密网、专网和特种网络，机会全部采用物理隔离网络。

基于腾讯安全威胁情报中心的长期研究跟踪，该
Ramsay恶意文件，跟我们之前跟踪的retro系列的感染文档插件重叠。该波攻击至少从18年就已经开始，并且一直持续到现在。其攻击手段也在不断的进行演化，比如感染的对象从感染doc文件到感染可执行文件，窃取资料的方式从写入可移动磁盘的扇区到写入文档文件末尾等等。事实上，跟ESET的发现类似，我们并未发现太多真实的受控机，因此我们相信该框架还在不断的改进和调试中，暂时并未应用到大规模的攻击活动中。

事实上，除了Retro系列和Ramsay系列有针对物理隔离网络的攻击外，该团伙早在2015年就已经开始使用Asruex后门来针对隔离网络进行攻击了。Asruex系列同样具有感染doc、pdf、exe等文件的能力。相比Ramsay系列少有感染的机器，Asruex系列的感染量就非常巨大了，直到目前都还有大量的新增机器被感染。当然，该系列后门被认为是购买的HackTeam的工具库。

本报告仅对针对物理隔离网络的一些攻击进行技术层面的分析，其他的攻击过程和攻击模块不在本文进行讨论和分析。

二、Retro系列

该系列的的感染，我们曾在2018年的文章《“寄生兽”的极地行动》（ **见参考链接2**
）中就已经简单的披露，进行感染的模块为初始攻击后下发的一个攻击插件：

![](https://image.3001.net/images/20200529/1590716233_5ed06749d06d5.png!small)

该次感染过程主要有两个模块配合完成：

![](https://image.3001.net/images/20200529/1590716243_5ed067539b769.png!small)docto.exe：开源工具，用来进行文档的格式转化

infsvc：感染可移动磁盘的中的文档文件，使得感染后的文件为带有CVE-2017-8570漏洞（一种Office高危漏洞，亦称“沙虫”二代漏洞）的rtf文件

![](https://image.3001.net/images/20200529/1590716251_5ed0675b0f1ee.png!small)

![](https://image.3001.net/images/20200529/1590716257_5ed0676180b3b.png!small)

此时，完成感染的过程。接下来，当该存有感染后文档的文件，通过可移动磁盘进入到其他设备，甚至物理隔离网络后，若运行感染后的文档文件，就会触发CVE-2017-8570漏洞，进而泄露机器上的敏感信息。

运行感染后的文件后，首先会触发脚本inteldriverupd1.sct：

![](https://image.3001.net/images/20200529/1590716263_5ed06767da644.png!small)

脚本的功能就为执行最终的恶意文件taskhost.exe。该恶意文件的主要功能为收集信息，然后写入可移动磁盘的扇区中：

**1) 执行以下命令收集系统信息存到%allusersprofile%\CommCache\S-{计算机名}.rtt**

    
    
     systeminfo
    
    tasklist /v
    
    netstat -ano
    
    ipconfig /all
    
    arp -a
    
    route print
    
    sc query wlansvc
    
    netsh wlan show all
    
    netsh wlan showprofiles
    
    netsh wlan showinterface
    
    netsh wlan shownetworks mode=Bssid

**2） 遍历本地磁盘，将全部文件目录存到%allusersprofile%\CommCache\C-{时间}.rtt**

 **3） 每5分钟截屏一次，保存到%allusersprofile%\AssemblyDataCache\def{时间}.jpg**

 **4） 加密截屏文件到%allusersprofile%\CommCache\ def{时间}.tmp**

收集完所有信息后，会创建%allusersprofile%\CommCache\complete.txt，当检测到complete.txt的时候，会认为收集信息工作已经结束。开始做后续的信息处理：

**1）将CommCache目录重命名为CommCache_{rand}，并压缩成CommCache_{rand}.zip**

![](https://image.3001.net/images/20200529/1590716272_5ed067700dd40.png!small)

**2）不断检测可移动磁盘，将CommCache_{rand}.zip内容直接以读写扇区的方式写入磁盘偏移1000000000处，并以HDdE
&mE作为标记：**

![](https://image.3001.net/images/20200529/1590716278_5ed0677610ba3.png!small)

![](https://image.3001.net/images/20200529/1590716284_5ed0677c5e966.png!small)

此时，该可移动磁盘上就存有了该设备的相关信息。若该可移动磁盘再度插回到之前被Retro木马攻击的机器上时，这部分数据就会被读取，然后通过其他的收集插件，把这些数据回传到攻击者的服务器上。而在受害者看来，简单使用文件管理器根本看不见该设备存储的秘密数据。

大致的流程图如下：

**![](https://image.3001.net/images/20200529/1590716292_5ed06784b05bc.png!small)**

## 三、Ramsay V1系列

在今年的4月初，我们再次发现了一批带有CVE-2017-8570漏洞的文档文件，经过分析研判后，我们发现该批带有漏洞的文档跟Retro系列感染后得文档存在非常多的相似点。因此我们判断为，该批文档文件同样为被感染后的产物，同样为攻击物理隔离网络而生，并且为同一攻击团伙所有。但是遗憾的是，这次我们并未发现原始的感染器文件。

当然跟Retro系列感染后的文档文件相比，该波感染后的文件，在功能上存在相当大的改进点。而存储感染机器的信息的方式也有一定的改变。

执行感染后的文件，同样会触发CVE-2017-8570漏洞，执行脚本OfficeTemporary.sct：

![](https://image.3001.net/images/20200529/1590716300_5ed0678ccafb9.png!small)

脚本会释放locked.ini、config.ini、slmgr.vbs等文件，最终的恶意文件主要为%allusersprofile%\Identities\netwiz.exe和%windir%\System32\dpnom.dll。其中netwiz.exe主要用来收集机器的信息；dpnom.dll主要用来把收集到的信息写到相应的地方保存。

大致的流程如下：

![](https://image.3001.net/images/20200529/1590716307_5ed06793e844b.png!small)

netwiz.exe收集的信息如下：

**1)执行以下命令收集系统信息存到%allusersprofile%\MediaCache\S-{计算机名}.rtt：**

    
    
     systeminfo
    
    tasklist /v
    
    netstat -ano
    
    ipconfig /all
    
    route print
    
    arp -a
    
    reg queryHKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\

**2)使用开源的powershell脚本%appdata%\Microsoft\Word\winword.ps1，把%appdata%\Microsoft\Word\下所有文档文件转换成TXT文件，并把转换后的TXT文件加密复制到%allusersprofile%\MediaCache\\{rand}.dat；**

 **3)打包以下目录所有.lnk文件到\MediaCache\Items_{rand}.db，密码是PleaseTakeOut!@#：**

    
    
     %APPDATA%\Microsoft\Windows\Recent\*.lnk
    
    %APPDATA%\Microsoft\Office\Recent\*.lnk

**4)接收Mailslot消息（为dpnom.dll注入的进程为iexplorer.exe，winword.exe时发送的一个消息），当收到消息后保存屏幕到%allusersprofile%\NetCache\def+{时间}.tmp；**

而dpnom.dll的主要作用为Hook WriteFile函数，监控到操作的文件为doc的时候，Hook
CloseHandle函数，将%allusersprofile%\MediaCache\中的一个文件附加写到即将关闭的doc文件末尾，流程图为：

![](https://image.3001.net/images/20200529/1590716315_5ed0679b64cf6.png!small)

写入附加信息后的文件：

![](https://image.3001.net/images/20200529/1590716321_5ed067a18996a.png!small)

%allusersprofile%\MediaCache\就是保存netwiz.exe收集到的信息的文件目录。不过值得注意的是：每次写入的内容是上述收集到的信息的文件中随机挑选的一个。因此编辑doc的次数越多，收集到的信息也会越多。

因此，当隔离网中的doc文件，随着可移动磁盘再次回到中转的机器上的时候，攻击者同样能够把隔离网络中的机器的信息给回传回去。

值得注意的是，我们在netwiz.exe还发现了另外一个隐藏的功能，该功能为扫描全盘doc、docx文件，搜索控制指令，根据控制指令进行相应的操作。该功能的目的就是为了完成攻击者对隔离网络中的机器进行控制。由于在隔离网络中无法进行正常的网络通信，因此攻击者为了控制隔离网中的机器，会在外部下发一个控制文档到中转机上，然后跟随可移动磁盘摆渡到隔离网中，因此来完成相应的控制操作。支持的控制指令有：

控制码  |  调试信息  |  功能描述  
---|---|---  
Rr*e#R79m3QNU3Sy  |  ExecuteHiddenExe  |  执行随后的exe文件  
CNDkS_&pgaU#7Yg9  |  ExecuteHiddenDll  |  释放插件Identities\\\netmgr_%d.dll并加载  
2DWcdSqcv3?(XYqT  |  ExecuteHiddenBat  |  依次执行随后的cmd命令  
  
做为控制的文档结构如下：

![](https://image.3001.net/images/20200529/1590716334_5ed067ae7ae1c.jpg!small)

##  四、Ramsay V2系列

除了发现被感染的文档文件外，我们同样还发现了被感染的exe文件。由于在文件中存在Ramsay字符，因此ESET把其命名为Ramsay：

![](https://image.3001.net/images/20200529/1590716341_5ed067b54ea21.png!small)

由于跟上面的感染文档文件的版本，无论是代码、路径、功能上都极为类似，因此归属到同一组织。所以把上面的版本称为Ramsay V1系列，该版本称为Ramsay
V2系列。

该系列具有感染全盘exe文件的功能，因此同样具备感染隔离网络的能力。完成感染功能的模块为Identities\bindsvc.exe，该感染器的名字跟Retro系列中感染文档的命名也极其类似，都以svc.exe结尾。被感染后的文件结构如下：

![](https://image.3001.net/images/20200529/1590716346_5ed067bac7c62.png!small)

执行被感染后的文件后，同样为继续感染该主机上的其他exe文件，实现蠕虫的效果。此外跟上面的Ramsay
V1类似，同样会对相关的机器信息进行收集，然后Hook
WriteFile和CloseHandle后，对写doc、docx操作时候，把收集到的信息写到文档的尾部。同样的，也会搜索控制文档，对控制文档中的相关指令，进行对应的命令操作。

这部分的功能跟上面V1系列类似，因此不再继续讨论。

##  五、Retro系列和Ramsay系列的同源分析

除了ESET文章中提到的Retro后门跟Ramsay后门存在非常多的类似点外，我们发现感染后的文件也存在相当多的类似点，包括使用相类似的字符串、获取结果都保存在.rtt文件、解密算法的类同、功能类同等等：

获取的信息均存储为S-{计算机名}.rtt

截取的屏幕均存储为def-{时间}.rtt

![](https://image.3001.net/images/20200529/1590716354_5ed067c2bc02e.png!small)

![](https://image.3001.net/images/20200529/1590716361_5ed067c90c30e.png!small)

功能上的异同如下表所示：

行为比较  |  Retro plugin  |  Ramsay V1  |  Ramsay V2  
---|---|---|---  
编译时间  |  2018  |  2019  |  2020  
传播途径  |  感染文档  |  感染文档  |  感染exe  
信息回传路径  |  U盘扇区  |  文档尾部  |  文档尾部  
信息存储文件扩展名  |  .rtt  |  .rtt  |  .rtt  
cmd命令收集信息  |  ✓  |  ✓  |  ✓  
获取截屏  |  ✓  |  ✓  |  ✓  
遍历磁盘文件  |  ✓  |  ✓  |  ✓  
持久化  |  ✕  |  ✓  |  ✓  
是否接受控制指令（文件）  |  ✕  |  ✓  |  ✓  
支持插件  |  ✕  |  ✓  |  ✓  
全盘感染  |  ✕  |  ✕  |  ✓  
内网探测  |  ✕  |  ✕  |  ✓  
获取IE临时文件  |  ✕  |  ✕  |  ✓  
  
可以发现，该工具一直在进行更新，且功能越来越趋向性强大和完整。

值得注意的是，腾讯安全威胁情报中心在2019年发表的文章（见参考链接3），文章中提到的做为攻击母体的"网易邮箱大师",当时我们认为是通过伪装正常客户端的方式，通过水坑来进行初始攻击。但是从目前掌握的信息来推测，该文件可能同样为感染后的产物：

![](https://image.3001.net/images/20200529/1590716377_5ed067d9489ba.png!small)

当然该结论仅为猜测，暂时并无更多的证据。因此若存在错误，烦请各位同行指正。

##  六、针对隔离网络攻击的总结

根据上面的分析，我们推测攻击者针对物理隔离网络的感染流程大致如下：

1、通过鱼叉钓鱼、水坑、供应链攻击等方式，初始攻击某台暴露在公网的主机；

2、横向渗透到某台做为中转（该机器用来公网和隔离网络间摆渡文件等功能）的机器上，下发感染文件（包括文档文件、可执行文件等）、收集信息等恶意插件模块；

3、在中转机器上监视可移动磁盘并感染可移动磁盘上的文件；

4、可移动磁盘进入隔离网络。隔离网内的机器若执行被感染的文件，则收集该机器上的相关信息，并写入可移动磁盘的磁盘扇区或文件的文档文件的尾部；

5、可移动磁盘再次插入中转机器上时，中转机器上的其他的恶意插件，对可移动磁盘特定扇区存储的机密信息进行收集，再回传到攻击者控制的服务器中。

6、此外，攻击者还会下发做为控制功能的文件，把相关的指令和操作命令写在控制文件中，然后通过可移动设备摆渡到隔离网络中，再来解析执行。

至此，完成对隔离网络的完成感染过程。大致的流程图如下：

**![](https://image.3001.net/images/20200529/1590716390_5ed067e6cfda7.png!small)**

## 七、其他的针对隔离网的攻击活动

事实上，早在2015年，该攻击团伙就已经被发现使用Asruex系列后门，来针对隔离网络进行攻击。Asruex系列同样具有感染全盘文件的能力，感染的文件类型包括doc、pdf、exe等：

![](https://image.3001.net/images/20200529/1590716399_5ed067ef7b1ad.png!small)

相较于Retro和Ramsay系列少有感染的机器，Asruex系列的感染量就非常巨大，直到目前，每日都还有大量的新增机器被感染：

**![](https://image.3001.net/images/20200529/1590716412_5ed067fc7384d.png!small)**

**![](https://image.3001.net/images/20200529/1590716419_5ed0680327bd4.png!small)**

如此大的感染量，未必是攻击者最初的目标，毕竟高级威胁攻击是针对性极强的攻击活动，很少是大规模展开的攻击活动。攻击动作太大，感染范围太广反而容易暴露自己。不利于隐藏和后续的攻击活动。好在该版本的C
&C服务器早已经失效，因此该系列的木马对受害机器的危害并不大。 ****

此外，该攻击工具库，疑似为Hacking Team所拥有：

Asruex的C&C为themoviehometheather.com，该域名的注册者为Chatere32@mail.com

![](https://image.3001.net/images/20200529/1590716428_5ed0680c4c973.png!small)

该邮箱注册的域名中，odzero.net曾被报道是Hacking Team所拥有：

![](https://image.3001.net/images/20200529/1590716435_5ed06813a7332.png!small)

![](https://image.3001.net/images/20200529/1590716441_5ed068199bc36.png!small)

而且，该团伙购买HackingTeam的军火库也并非首次，卡巴斯基曾报导过相关的新闻：

![](https://image.3001.net/images/20200529/1590716449_5ed0682139029.png!small)

这也跟之前曝光的韩国情报官员因为购买HackingTeam间谍软件而自杀的事件相印证：

![](https://image.3001.net/images/20200529/1590716455_5ed068277604a.png!small)

##  八、结论

Ramsay为一个功能强大的攻击模块，而且该模块一直保持着更新且功能越来越完善和成熟。好在目前发现的受控设备并不多，但也不排除存在隔离网络中的感染设备未被发现的情况。

此外，无论是Asruex系列还是Ramsay系列，该攻击团伙至少从2015年开始就已经针对物理隔离网络进行针对性的攻击了，并且依然在不断的开发攻击库。因此针对物理隔离网络的安全建设也是刻不容缓，千万不能因为隔离网络中的机器未与外网通信而掉以轻心。

##  九、安全建议和解决方案

本次Ramsay恶意软件针对隔离网络环境的攻击，其目的是进行各种网络窃密活动，攻击者将收集到的情报，直接写入移动存储介质的特定扇区，并不在该存储介质上创建容易查看的文件，使得收集行为极具隐蔽性。会对政企机构、科研单位会构成严重威胁。腾讯安全专家建议相关单位参考以下安全措施加强防御，防止黑客入侵增加泄密风险：

1、通过官方渠道或者正规的软件分发渠道下载相关软件，隔离网络安装使用的软件及文档须确保其来源可靠；

2、谨慎连接公用的WiFi网络。若必须连接公用WiFi网络，建议不要进行可能泄露机密信息或隐私信息的操作，如收发邮件、IM通信、银行转账等；最好不要在连接公用WiFi时进行常用软件的升级操作；

3、可能连接隔离网络的系统，切勿轻易打开不明来源的邮件附件；

4、需要在隔离网络环境使用的移动存储设备，需要特别注意安全检查，避免恶意程序通过插入移动介质传播；

5、隔离网络也需要部署可靠的漏洞扫描及修复系统，及时安装系统补丁和重要软件的补丁；

6、使用腾讯电脑管家或腾讯御点终端安全管理系统防御病毒木马攻击；

7、推荐相关单位部署腾讯T-Sec高级威胁检测系统（御界）捕捉黑客攻击。御界高级威胁检测系统，是基于腾讯安全反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。（<https://s.tencent.com/product/gjwxjc/index.html>）

##  十、附录

###  1.IOCs

MD5：

    
    
    92480c1a771d99dbef00436e74c9a927 infsvc.exe
    
     dbcfe5f5b568537450e9fc7b686adffd  taskhost.exe
    
     03bd34a9ba4890f37ac8fed78feac199 bindsvc.exe

URL：

> [http://themoviehometheather.com](http://themoviehometheather.com/)

###  2.参考链接

> 1） <https://www.welivesecurity.com/2020/05/13/ramsay-cyberespionage-toolkit-> airgapped-networks/>
>
> 2） <https://s.tencent.com/research/report/465.html>
>
> 3） <https://s.tencent.com/research/report/741.html>
>
>  
>

***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**  

