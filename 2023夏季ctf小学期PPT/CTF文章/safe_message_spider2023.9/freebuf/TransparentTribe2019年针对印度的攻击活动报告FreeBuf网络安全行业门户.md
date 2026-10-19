## **一、** **报告背景**

**进行2019年以来，腾讯御见威胁情报中心检测到多起针对印度政府部门、军事目标等的攻击活动，诱饵内容包括"印度空袭分裂主义组织（英译汉）"、"联合国军事观察员（英译汉）"等。经过分析关联确认，攻击组织为TransparentTribe
APT组织。**

TransparentTribe
APT组织，又称ProjectM、C-Major，是一个来自巴基斯坦的APT攻击组织，主要目标是针对印度政府、军事目标等。该组织的活动最早可以追溯到2012年。该组织的相关活动在2016年3月被proofpoint披露，趋势科技随后也跟进进行了相关活动的披露。

腾讯御见威胁情报中心对该组织进行持续和深入的分析和跟踪，掌握了该组织的相关攻击TTPs（“攻击者的战术，技术和过程”的缩写），并且认为该组织跟另一个由Paloalto
Unit42团队披露的Gogron Group也存在一定的关系。

##  **二、** **攻击活动分析**

### 1、攻击诱饵

该组织的攻击采用鱼叉攻击的方式，诱饵主要有两种类型，xls和doc，诱饵内容跟印度相关，具体如下：

文件hash |  7fa6689ec0a8863e5084d30de4b9b252  
---|---  
文件名 |  UNITED_NATIONS_MILITARY_OBSERVERS____COURSE___UNMOC-19_.xls  
文件类型 |  MS Excel Spreadsheet  
文档作者 |  Cloner  
最后修改者 |  Cloner  
最后修改时间 |  2019:01:07 07:58:00  
上传到VT时间 |  2019/1/30 11:31  
  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837198_5c7f280e732a8.png!small)

  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837207_5c7f2817b2ad2.png!small)

其中，CUNPK为联合国维持和平中心，是一个在印度新德里的一个组织，该组织的主要职能是为联合国的相关人员提供服务，如为联合国观察员提供培训服务等。

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837229_5c7f282d7ddbc.png!small)

该诱饵提到的就是在2019年2月的对联合国军事观察员的一个培训的相关内容。

此外，根据该诱饵文件，我们还找到了一个跟该诱饵文件非常相似的文件，包括内容、恶意代码等都一致，仅个别字节有改动：

**文件hash** **** |  **f2260694b2ecb02bf03181e774140f29**  
---|---  
文件名 |  N/A  
文件类型 |  MS Excel Spreadsheet  
文档作者 |  Cloner  
最后修改者 |  Cloner  
最后修改时间 |  2019:01:07 07:58:00  
上传到VT时间 |  2019/2/5 16:26  
  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837241_5c7f283954b0f.png!small)

文件hash |  b16d4956f6609104eb93a521b60c6f42  
---|---  
文件名 |  EoMA_PGA_2019.xls  
文件类型 |  MS Excel Spreadsheet  
文档作者 |  Cloner  
最后修改者 |  Roche  
最后修改时间 |  2019:02:18 07:13:14  
上传到VT时间 |  2019/2/25 11:19  
  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837251_5c7f2843597fb.png!small)![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837271_5c7f285726b0b.png!small)

该诱饵主要提到的内容是在2019年印度共和国日，印度总统给印度空军人员办法杰出服务奖和英勇奖的相关内容。

其中IAF为印度空军，因此该报告疑似跟军事目标相关：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837312_5c7f28803910a.png!small)

文件hash |  1b7b5c85fe5b9daf2264b7d5f6b364e9  
---|---  
文件名 |  contacts.doc  
文件类型 |  MS Word Document  
文档作者 |  swear  
最后修改者 |  swear  
最后修改时间 |  2019:02:03 12:59:00  
上传到VT时间 |  2019/2/7 13:07  
  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837309_5c7f287d77c98.png!small)

该诱饵文档没什么实际的意义，为一堆乱码，攻击背景不详。

文件hash |  41b70737fa8dda75d5e95c82699c2e9b  
---|---  
文件名 |
Exclusive_Pictures__destruction_of_Jaish_Camp_and_dead_bodies_of_terrorists.doc  
文件类型 |  MS Word Document  
文档作者 |  sara123  
最后修改者 |  sara123  
最后修改时间 |  2019/2/28 0:56  
上传到VT时间 |  2019/2/28 4:17:25  
  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837324_5c7f288ce916c.png!small)

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837337_5c7f289937ad5.png!small)

该诱饵提到了最新的印度空袭巴基斯坦恐怖组织训练营的事件。

### 2、宏技术细节

这些攻击诱饵的宏代码基本类似，如下：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837623_5c7f29b7e5e6b.jpg!small)

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837643_5c7f29cbc9d7b.png!small)

宏代码启动后，都会将窗体控件内容进行解密后释放到相关的文件夹中，并解压出可执行文件运行。  

但是细节上，doc版本的诱饵文档跟xls版本的诱饵文档，稍微有点差异。

如doc版本的诱饵文档：

Doc文档打开后，首先会调用内置VBA函数ShadrifileLdr,随后将其窗体UserShiForm控件文本内容显示到文档中。

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837659_5c7f29db51646.png!small)

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837669_5c7f29e5e2bd3.png!small)

因此未启动宏的时候，显示空白：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837684_5c7f29f44a718.png!small)

然后VBA函数ShadrifileLdr的功能则是解密窗体kashForm控件文本内容，并写入到创建在”ALLUSERSPROFILE”\\\Hurmz\rgiwsdasxa.zip压缩文件中，随后在调用内置解压缩函数解压到”ALLUSERSPROFILE”\\\Hurmz\rgiwsdasxa.exe并执行。

但xls版本的诱饵文档：

启动宏代码后，VBA函数同样将窗体UsersobiForm控件文本内容释放到%USERPROFILE%\Documents\Hadram.zip文件，并且将Hadram.zip解压到当前目录下Hadram.exe。但是会判断相应的系统版本，来释放不同的内容（以win7和win8&win10做分界线）：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837699_5c7f2a0353505.png!small)

### 3、恶意文件分析

Doc版本和xls 版本在释放的恶意文件上也有一定的差异。

1） Doc版本释放的恶意文件分析，以诱饵4释放的文件rgiwsdasxa.exe来进行分析：

文件执行后，首先会上传本地机器信息和当前rat信息到服务器，并设置注册表自启动：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837715_5c7f2a1366a76.png!small)

随后接受远程指令进行下一步操作，该rat支持超过20多个指令功能，包括截屏，键盘记录，木马跟新，上传文件等功能：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837745_5c7f2a3138929.png!small)

木马会通过内置两个ip和多个端口号进行通讯，如果当前默认无法联通c2服务器则更换另一个ip或者端口号进行通讯：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837757_5c7f2a3ddd5c2.png!small)

最终的通信c2为：216.176.190.98。

该RAT最终被确认的RAT家族为CrimsonRAT。

2） Xls版本释放的恶意文件分析，以诱饵1释放的文件Hadram.exe来进行分析：

Hadram.exe实际名为lioeek.exe，lioeek.exe首先会尝试是否能访问google，如果能访问则释放exe到%ALLUSERSPROFILE%\ekeoil\ekeoil.exe并启动，最后结束时创建lnk文件设置注册表自启：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837772_5c7f2a4c92c31.png!small)

### ![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837787_5c7f2a5b0df58.png!small)Ekeoil.exe分析

首先会去访问

<https://www.quora.com/If-programming-languages-had-honest-slogans-what-would-they-be>，并且查找该html页面中<span>标签是否为”Quora”：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837799_5c7f2a67dd813.png!small)

如果存在则会去ping firebasebox.com，如果firebasebox.com存活，则会继续访问C2服务器：

<http://firebasebox.com/tootie292/reboshw/c0_nCussi0N.php>，并判断返回值是否为”7375636b6d796469636b”：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837812_5c7f2a745d1e7.png!small)

如果正确则会判断是否存在C:\ProgramData\ekeoil\ekeoil.xml文件并读取xml文件中的username和password，用于与C2服务器通讯。否则通过本地信息已经木马版本号创建username和password并创建xml写入：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837826_5c7f2a82c9c35.png!small)

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837841_5c7f2a91aa91b.png!small)

随后继续收集本地信息和进程列表带上username和password分别发送给不同url：

如本地机器信息：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837854_5c7f2a9ecb4b3.png!small)

如进程列表：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837872_5c7f2ab055c5e.png!small)

随后进行循环访问c2服务器，根据返回的内容进行上传下载文件，卸载，设置注册表自启等操作：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837884_5c7f2abc9fe06.png!small)

而最终，会下载执行一个基于python的恶意文件Axess.exe。

###  **Axess.exe分析**

首先检查注册表和自身文件名和路径，如果不正确则设置注册表自启并且在”%appdata%”下创建axess文件夹，并复制自身到该文件夹下并重命名为axess_xxxx.exe，xxxx为1000-9999的随机数。然后重新启动自身：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837903_5c7f2acf47c52.png!small)

重新启动后，首先在配置文件中选择服务器地址，判断服务器是否存活。随后创建本地数据库文件”axess.db”，然后创建username和password，并且将username和password发送到服务器。随后对通过配置文件规则对本地进行文件收集：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837918_5c7f2ade370a0.png!small)

最后循环访问c2服务器，等待服务器下发的功能指令，等待的过程中会上传收集到的本地文件：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837941_5c7f2af524b8d.png!small)

该版本支持下载，更新，上传，获取当前执行任务等功能：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837953_5c7f2b01adc0d.png!small)

该RAT最终确认为PeppyRAT。

##  **三、** **关联分析**

根据该轮的攻击样本，我们又从腾讯御见威胁情报中心的大数据库中关联到了一些相似的攻击样本：

如诱饵文件：

文件hash |  91e5c5afcf42f8912d5ae3b7dafcda22  
---|---  
文件名 |  Officer_Course_for_FY_2018_19-4.xls  
文件类型 |  MS Excel Spreadsheet  
文档作者 |  Qaatil  
最后修改者 |  Qaatil  
最后修改时间 |  2018:10:23 06:53:39  
上传到VT时间 |  2018/10/29 19:04  
  
![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837987_5c7f2b239ab4f.png!small)

文件内容依然跟印度相关。该文件的宏跟上述分析的基本一致，不过也有一些小的区别：

该文件的宏执行后，会解密窗体控件文本内容释放到%USERPROFILE%\AppData\下文件名为6个字符的scr文件，并执行：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551837994_5c7f2b2a606c1.png!small)

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838024_5c7f2b488c14c.png!small)

src文件执行后会释放一个可执行文件到”ALLUSERSPROFILE”\ewbusm\ewbusm.exe 并且在启动文件夹下创建同名lnk文件用于自启：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838044_5c7f2b5c1a728.png!small)

从版本号上来看，该版本为2.1.2.9，该.net文件跟上述分析的.net（xls版本释放的恶意文件）基本一致：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838072_5c7f2b78ccf20.png!small)

而从关联到的样本来看，该版本恶意文件也是经过了持续的迭代，从版本号1.0.0.0一直更新到了8.7.18.11。

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838085_5c7f2b85cb449.png!small)

虽然在持续进行迭代，但是该些.net文件变化不大，功能和代码结构基本一致。  

## **四、** **攻击TTPs总结**

事项  |  说明  
---|---  
攻击目标  |  印度政府、军事目标等  
投递方式  |  鱼叉攻击  
诱饵类型  |  带有VBA宏的doc、xls文档等。并且把相关的内容和恶意文件以整形的数据形式存放在窗体控件中。  
诱饵内容  |  以攻击目标感兴趣的新闻和通知等内容  
特马家族  |  CrimsonRAT、.net loader、.net droper、PeppyRAT  
攻击目的  |  窃取相关资料文件  
  
## **五、** **溯源关系**

 **1、** **同TransparentTribe关系**

从攻击TTPs来看，该次攻击活动可以确定是同TransparentTribe相关的。

如：使用CrimsonRAT、基于python的PeppyRAT。

 **2、** **同GorgonGroup的关系**

通过腾讯御见威胁情报中心的大数据，我们又关联到一个新的攻击样本。

样本hash：10f6cc542bf69acdd749f8e226200cf5

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838104_5c7f2b98e96c7.png!small)

该文件最终会释放文件Intel
Graphics.exe（c9401cdee589b69c5d57b4c747a950af），经过分析，该文件跟上述xls版本释放的.net文件几乎一致。

该文件的访问域名也被腾讯安图高级威胁溯源系统标记为ProjectM：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838120_5c7f2ba8b03c9.png!small)

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838135_5c7f2bb7794dd.png!small)

此外，该样本的来源为：<http://stemtopx.com/work/i/2.exe>，该域名被标记为Gorgon Group：

![TransparentTribe
APT组织2019年针对印度政府、军事目标的攻击活动报告](https://image.3001.net/images/20190306/1551838154_5c7f2bca92306.png!small)

此外，友商360的报告《利用了多种Office
OLE特性的免杀样本分析及溯源》（参考文章5）中提到的组织为ProjectM，该报告也被Paloalto的Unit42的团队归结为Gorgon
Group的一部分（参考文章3）。

此外，攻击者背景都为来自巴基斯坦的团队，而攻击目标也主要为印度的相关敏感目标。因此我们判断这两个组织存在一定的关联。

##  **六、** **总结**

近期，印巴冲突是国际社会重点关注的大事，随着印巴冲突的不断升级，两国间的网络攻击也不断升级：腾讯御见威胁情报中心在2019年多次检测到双方针对对方重要部门的网络攻击事件。

"没有网络安全，就没有国家安全"，随着政治形势的变化，国家间的网络攻击行为成为一种全新的博弈手段，针对国家敏感部门等的APT攻击会愈演愈烈。因此各大部门和单位切不可掉以轻心，随时保持高度警惕，防止被攻击而影响国家或者重要单位的信息安全。

##  **七、** **安全建议**

> 1、 不要打开不明来源的邮件附件；除非非常清楚文档来源可靠，否则建议不要启用Office执行宏代码；
>
> 2、 及时打系统补丁和重要软件的补丁；
>
> 3、 使用杀毒软件防御可能的病毒木马攻击

##  **八、** **附录**

###  **1、** **IOCs**

 **MD5** **：**

> 41b70737fa8dda75d5e95c82699c2e9b
>
> e0e9c625adab63c255a0e16fe8683189
>
> 2eb4469c76f5230c66626a6918c7664f
>
> 79d690b27e287a0a24c91b6be91254cf
>
> 7fa6689ec0a8863e5084d30de4b9b252
>
> 0f3488c89f4f519ceba2c97e83d12af2
>
> 801f94eedb9481fb65709457c1f4c47a
>
> ab68db5c97f9ee12ca29c1eed881781d
>
> b16d4956f6609104eb93a521b60c6f42
>
> 512dd1f7380b3507f670c061e756f005
>
> 2c94776b6a145854f305a9febf95fd00
>
> 1b7b5c85fe5b9daf2264b7d5f6b364e9
>
> b709529e2db6356c4578000de02725cb
>
> 1300ef72d620d298d5413658e01ee7e8
>
> 973ca595e9abe9f4c6e6cf5a624f21d7
>
> 3b3b39cb3c2306e38f9e06b23c4a645e
>
> ec544e62d65474e4f033fdc4d4aff639
>
> 11bfb965c20327564f4555734e966cdc
>
> 93350312094d1ffcf2656c8d8df694bf
>
> 91e5c5afcf42f8912d5ae3b7dafcda22
>
> 4dfde74cb13ed3890e33082b7f296f57
>
> 208606ace2e34c4b2fefeb4909c66d50

 **Domain**

> hxxp://firebasebox.com
>
> hxxp://cynqms.com
>
> hxxp://bdrive.club
>
> hxxp://Cloudserve.online
>
> hxxp://Bdrive.space
>
> hxxp://[www.scan9t.com](http://www.scan9t.com)
>
> hxxp://tprlink.com

 **ip**

> 216.176.190.98
>
> 210.115.241.121

###  **2、** **参考链接**

1）<https://www.proofpoint.com/sites/default/files/proofpoint-operation-transparent-tribe-threat-insight-en.pdf>

2）<http://documents.trendmicro.com/assets/pdf/Indian-military-personnel-targeted-by-information-theft-campaign-cmajor.pdf>

3）<https://unit42.paloaltonetworks.com/unit42-gorgon-group-slithering-nation-state-cybercrime/>

4）<https://unit42.paloaltonetworks.com/unit42-tracking-subaat-targeted-phishing-attacks-point-leader-threat-actors-repository/>

5）<https://www.anquanke.com/post/id/101722>

