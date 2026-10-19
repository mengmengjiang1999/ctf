## 概述

奇安信威胁情报中心红雨滴安全研究团队多年来持续对南亚次大陆方向的攻击活动进行追踪。我们对魔罗桫组织均做过大量的分析和总结。上述组织长期针对东亚和南亚地区进行了长达数年的网络间谍攻击活动，主要攻击领域为政府机构、军工企业、核能行业、商贸会议、通信运营商、智库期刊、广播电台、新闻媒体等。

本文内容是对魔罗桫组织在2020年的攻击活动做一个总结，并对南亚地区有争议的组织进行梳理，正本清源。在此过程中我们发现了魔罗桫组织使用的新型攻击手法和恶意软件。所涉及的恶意域名和IP均已无法访问。

## 钓鱼分析

2020年奇安信大数据平台捕获了大量的魔罗桫组织钓鱼页面，加载钓鱼页面前会有预加载页面，如下：

![1623307552_60c1b520dc3a73fd5a804.png!small?1623307554201](https://image.3001.net/images/20210610/1623307552_60c1b520dc3a73fd5a804.png!small?1623307554201)

之后会跳转到对应的钓鱼页面

![1623307557_60c1b525bceed9333dd9b.png!small?1623307558009](https://image.3001.net/images/20210610/1623307557_60c1b525bceed9333dd9b.png!small?1623307558009)

![1623307560_60c1b528e24e285de1722.png!small?1623307561256](https://image.3001.net/images/20210610/1623307560_60c1b528e24e285de1722.png!small?1623307561256)

![1623307564_60c1b52c29853644c1629.png!small?1623307564764](https://image.3001.net/images/20210610/1623307564_60c1b52c29853644c1629.png!small?1623307564764)

其钓鱼方式与去年我们披露的细节基本一致，受害者需要连续输入两次密码，且两次密码必须相同的情况下才会跳转到对应的页面。钓鱼页面涉及军工、政府、媒体、智库期刊、杂志、高校、国企、研究所等单位。

## 诱饵分析

经过长时间的收集和整理，我们一共发现了五类诱饵投递的手法

 **Rar+Exe**

 **文件名**

|

 **MD5**  
  
---|---  
  
2020-07-28_RepairForConfirmation_PDF.rar

|

5d682ce0b4a04e9cd37bebf1f20db865  
  
CARGO RECEIVING ETA DFS_LAX 09_08_2020.rar

|

1b93f551e49eff0dc0e7f619123df125  
  
XXXXXXX（2020）正文 9月08日修改.rar

|

3c392e37c314877244fe9b4072f3ff3e  
  
据称XX记者向XXXXXX出X了XX信息.rar

|

ac4647816fd5c502ca1a03349c178ea4  
  
解XXX：XXX界X题.rar

|

4c328190b5cd6a72eda28340ad21a65a  
  
XX竞X通向XX的中XX界.rar

|

2b32add625bda417bb828758a0443111  
  
样本目录如下：

![1623307575_60c1b5370d1fbb8f50ebc.png!small?1623307575431](https://image.3001.net/images/20210610/1623307575_60c1b5370d1fbb8f50ebc.png!small?1623307575431)

样本涉及的PDB如下：

 **PDB**  
  
---  
  
C:\Users\Virat\Desktop\hello\WindowsFormsApplication1\obj\Debug\WindowsFormsApplication1.pdb  
  
C:\Users\W7H64\Desktop\VCSamples-master\VC2010Samples\ATL\General\ATLCollections\Client\Client.pdb  
  
有些样本在运行过程中会弹出文本框迷惑受害者，制造文件损坏的假象。

![1623307678_60c1b59e416dd213a96c3.png!small?1623307678572](https://image.3001.net/images/20210610/1623307678_60c1b59e416dd213a96c3.png!small?1623307678572)

有些则会作为下载者从远程服务器下载PDF诱饵和第二阶段载荷，相关诱饵如下：

![1623307685_60c1b5a5aea957d6dbb1d.png!small?1623307686016](https://image.3001.net/images/20210610/1623307685_60c1b5a5aea957d6dbb1d.png!small?1623307686016)

 **Rar+Documnet+Exe**

 **文件名**

|

 **MD5**  
  
---|---  
  
JOINT INSPECTION OF INSULATION MATERIAL 57th BATCH OF KoM - 15HT-2
(SB-278).rar

|

3e84bf8e1f9b469c3fcc24281a1f65dc  
  
LY80 Test doc.rar

|

bef6c430c3068e25018e1edbfb979717  
  
Final research papers.rar

|

381ee6c0f4e4779ed49a88c56ae11957  
  
4f895f2a05f99e355f5022be6a7a9950  
  
057a1dc0aac2637a4c7d5097baecf0c7  
  
reaearch papers.rar

|

cc944a2ad6f8efba1fcc4ff5dd986028  
  
0709_ch.rar

|

11362c81ccc7a6c365e191b8153c6031  
  
2-research papers final.rar

|

5e77eb4f9a10ca153d9cc82b8f3e1de4  
  
XX的Suga着眼于XX，并寻求与XX和XXXX亚X立更XX的联系.zip

|

b6a39615bb3f40b36175b68b5c12d2cd  
  
XX关系与XX影响.zip

|

d65906aab1b8336c674ffb741951cda7  
  
Revised repair quote for LT RT wing Receiver.rar

|

49f5f3f2ebb5a35bc7802b8dfc7f6e05  
  
样本目录如下:

![1623307695_60c1b5af595c3a71690b2.png!small?1623307696082](https://image.3001.net/images/20210610/1623307695_60c1b5af595c3a71690b2.png!small?1623307696082)

压缩包中存在一个损坏的文件和一个恶意程序，这种类型的样本在去年的报告《提菩行动：来自南亚APT组织“魔罗桫”的报复性定向攻击》中已经提过，再次不做赘述，损坏的文档如下：

![1623307701_60c1b5b563d3020a39b2b.png!small?1623307701758](https://image.3001.net/images/20210610/1623307701_60c1b5b563d3020a39b2b.png!small?1623307701758)

除此之外我们发现了该组织首次在同一个诱饵文档上使用DDE和VBA Stomping技术。

![1623307706_60c1b5ba90baf890c70f3.png!small?1623307706859](https://image.3001.net/images/20210610/1623307706_60c1b5ba90baf890c70f3.png!small?1623307706859)

恶意Doc文件内容如下：

![1623307711_60c1b5bf4d495eb537da0.png!small?1623307711622](https://image.3001.net/images/20210610/1623307711_60c1b5bf4d495eb537da0.png!small?1623307711622)

![1623307714_60c1b5c2ad9c750b5618e.png!small?1623307714954](https://image.3001.net/images/20210610/1623307714_60c1b5c2ad9c750b5618e.png!small?1623307714954)

 **Rar+Lnk+Sfx**

 **文件名**

|

 **MD5**  
  
---|---  
  
Trump has directeed for closure of more Chinese consulates.rar

|

5ffd101e3059f315f43506a8a913c7f0  
  
letter to ADP for clearance of CRVs 20200720PDF.rar

|

67cb06092b449a39b8b15f1c7d450c13  
  
research paper- Tensions in the South China Sea escalate, U.S. policy toward
China turns tough.zip

|

886cdb101ca5bb907087b5_012cb23488  
  
执行流程大致如下：

![1623307720_60c1b5c8c0af74b192cb8.png!small?1623307721013](https://image.3001.net/images/20210610/1623307720_60c1b5c8c0af74b192cb8.png!small?1623307721013)

2020年中旬，我们首次发现魔罗桫组织利用Lnk文件发起定向攻击，大体分为两类，一类通过lnk执行cmd命令从远程服务器下载第二阶段payload。

![1623307729_60c1b5d1dfcdf1a550fce.png!small?1623307730316](https://image.3001.net/images/20210610/1623307729_60c1b5d1dfcdf1a550fce.png!small?1623307730316)

另一类则通过lnk启动sfx自解压文件打开诱饵并执行远控，相关诱饵如下

![1623307733_60c1b5d568228d52cfdc4.png!small?1623307733754](https://image.3001.net/images/20210610/1623307733_60c1b5d568228d52cfdc4.png!small?1623307733754)

![1623307736_60c1b5d88c147765111ff.png!small?1623307736848](https://image.3001.net/images/20210610/1623307736_60c1b5d88c147765111ff.png!small?1623307736848)

  

![1623307739_60c1b5db4177f97605cd7.png!small?1623307739703](https://image.3001.net/images/20210610/1623307739_60c1b5db4177f97605cd7.png!small?1623307739703)

 **Rar+Exe+txt**

 **文件名**

|

 **MD5**  
  
---|---  
  
Update.rar

|

72181dd18878f71097fc3d6441e63f9c  
  
该类型的诱饵最近两年较为少见。攻击者通过使用软件更新等主题的邮件对相关人员进行定向攻击。

![1623307747_60c1b5e3652652334283b.png!small?1623307747696](https://image.3001.net/images/20210610/1623307747_60c1b5e3652652334283b.png!small?1623307747696)

txt诱饵内容如下：

![1623307769_60c1b5f943d1aded0eba7.png!small?1623307769482](https://image.3001.net/images/20210610/1623307769_60c1b5f943d1aded0eba7.png!small?1623307769482)

运行更新程序后会弹出提示框迷惑用户

![1623307759_60c1b5ef94990bc93255b.png!small?1623307759816](https://image.3001.net/images/20210610/1623307759_60c1b5ef94990bc93255b.png!small?1623307759816)

 **Rar+document**

 **文件名**

|

 **MD5**  
  
---|---  
  
对照XXXX找差X问题清单.rar

|

75f14630d436ac67ad7de84cd794cb00  
  
ANNEX A Inspection for overhaul of WE systems onboard F22P Ships.rar

|

36bbdac5062804020faacc354ab03b52  
  
Annexure Project requirement and progress update.rar

|

4f2f8d1805ae27d3d02d5b96f6820f8b  
  
Webinar on India-China-Nepal on 12 Aug, 2020.rar

|

d73431cf21b400f1ce3cdda854c4ba1c  
  
American Institute in Taiwan (AIT), Director Brent Christensen statement on
823 ceremony.docx

|

b73f2590edc4569d6ae8999be5017ead  
  
Document.docx

|

5c5b66dad86afa990af5aa7a2d96aa93  
  
Escalation in SCS foreign media.rar

|

4147d49afb7d9527dd8ac1808583b9be  
  
Invitation.zip

|

567c7aed5f5406145a9ace167cbc25a2  
  
XXXX学会（AIT）所长XXX·XXXXX（Brent Christensen）在XXXXX上的讲话.docx

|

b73f2590edc4569d6ae8999be5017ead  
  
AIT.doc

|

1331b068477e2974894a899c855bfc4b  
  
Delivery Plan for RRC-2020-08-26.xls

|

edc6315c0736da67a0cdb6651383b4a5  
  
Encrypted delivery items list.doc

|

6d325c718d8a44e8799f5d0bfb813497  
  
contact list.xlsm

|

65864c98ab91cc987e64ed8fbfe33237  
  
XX警报和XX僵局.rar

|

ae8766ac5306637b631311b8f6d53414  
  
Book1.doc

|

89850b1049288d5f2c1fda42a3935d08  
  
2020-08-03 Provision of Technical Proposal.rar

|

892a57154ed7907bebadce0ffcf66028  
  
Weekly Report by JF-17 Service Team.zip

|

bf8355d02594eb28938d6cef4d119e22  
  
letter to ADP for clearance of CRVs 20200720.rar

|

f5f3bb60677e59d27c640b21a530e603  
  
program list.xls

|

9a85ca4b70146297704b81fb10f3b124  
  
Request of Courtesy Call on CNS.zip

|

fe2ebf337e425e18d3013d0d7002b032  
  
Annexure to documents.docx

|

d1d52f65bed15cb8e42ef921df919c42  
  
list of medical equipments required.xlsm

|

a65135558c2785964c8fe3986cac7f5d  
  
研究论文-XX紧张XX升级 XX对XXX转向XX.zip

|

03cbf5f6fea3ce68faa169dc3154b4e4  
  
样本目录如下：

![1623307780_60c1b604d5205fde1c11d.png!small?1623307781303](https://image.3001.net/images/20210610/1623307780_60c1b604d5205fde1c11d.png!small?1623307781303)

上述样本包含了魔罗桫组织常用的宏、模板注入，rtf，dde auto等文档类样本。

## 样本分析

除了去年报告中提到过的.net混淆器、dephi注入器、warzone
Rat、DarktrackRAT、AsyncRat外，在本次活动中捕获了一些魔罗桫组织之前从未披露过的样本和攻击手法：

 **VB DownLoader**

从远程服务器下载payload并执行

![1623307789_60c1b60d73b5a7bfcafa2.png!small?1623307790037](https://image.3001.net/images/20210610/1623307789_60c1b60d73b5a7bfcafa2.png!small?1623307790037)

下载PDF诱饵文件并执行

![1623307793_60c1b6115cbe9af4d4dbb.png!small?1623307793801](https://image.3001.net/images/20210610/1623307793_60c1b6115cbe9af4d4dbb.png!small?1623307793801)

 **Golang Rat**

会先弹出提示框

![1623307797_60c1b615d75345bfe1bca.png!small?1623307798304](https://image.3001.net/images/20210610/1623307797_60c1b615d75345bfe1bca.png!small?1623307798304)

连接远程服务器，

![1623307801_60c1b619df692545a43d3.png!small?1623307802309](https://image.3001.net/images/20210610/1623307801_60c1b619df692545a43d3.png!small?1623307802309)

根据控制号执行相关动作，如命令执行、文件下载、屏幕快照、注册表管理、文件管理、键盘记录等

![1623307809_60c1b621a23c01d9dd7e1.png!small?1623307810088](https://image.3001.net/images/20210610/1623307809_60c1b621a23c01d9dd7e1.png!small?1623307810088)

![1623307814_60c1b626169dee38d126f.png!small?1623307814450](https://image.3001.net/images/20210610/1623307814_60c1b626169dee38d126f.png!small?1623307814450)

![1623307817_60c1b62987ddc20e24e10.png!small?1623307817885](https://image.3001.net/images/20210610/1623307817_60c1b62987ddc20e24e10.png!small?1623307817885)

![1623307821_60c1b62d7a9fcb9931624.png!small?1623307822038](https://image.3001.net/images/20210610/1623307821_60c1b62d7a9fcb9931624.png!small?1623307822038)

MinGW Loader(Test File)

测试样本如下：

![1623307834_60c1b63a257d547d7c200.png!small?1623307835116](https://image.3001.net/images/20210610/1623307834_60c1b63a257d547d7c200.png!small?1623307835116)

VB Starter（Test File）

![1623307847_60c1b647ba51c25b49b51.png!small?1623307847999](https://image.3001.net/images/20210610/1623307847_60c1b647ba51c25b49b51.png!small?1623307847999)

 **DDE AUTO+VBA Stomping**

恶意文档的DDE auto代码会启动同目录下的paper_final_comment.exe程序

![1623307855_60c1b64fc15e99ffda895.png!small?1623307856905](https://image.3001.net/images/20210610/1623307855_60c1b64fc15e99ffda895.png!small?1623307856905)

paper_final_comment.exe程序主要功能为弹出如下提示框

![1623307860_60c1b654a99923f606076.png!small?1623307861215](https://image.3001.net/images/20210610/1623307860_60c1b654a99923f606076.png!small?1623307861215)

文档内容会诱导受害者启用宏，在此过程中使用了VBA Stomping技术，以源代码形成存储的宏如下：

![1623307866_60c1b65a1ed55ac719a9e.png!small?1623307866697](https://image.3001.net/images/20210610/1623307866_60c1b65a1ed55ac719a9e.png!small?1623307866697)

以Pcode形式存储的宏如下：

![1623307871_60c1b65fd09acbabb16ee.png!small?1623307872127](https://image.3001.net/images/20210610/1623307871_60c1b65fd09acbabb16ee.png!small?1623307872127)

有些样本在Pcode中对字符串进行了十六进制的转换，用于规避杀软

![1623307877_60c1b665acca4ae7080a9.png!small?1623307878188](https://image.3001.net/images/20210610/1623307877_60c1b665acca4ae7080a9.png!small?1623307878188)

在我们对多个类似样本分析后发现DDE auto除了会执行VB的弹窗程序外还会执行Loader程序，最终会内存加载WarZone远控

Loader程序如下：

![1623307883_60c1b66b947e08d7a2402.png!small?1623307883816](https://image.3001.net/images/20210610/1623307883_60c1b66b947e08d7a2402.png!small?1623307883816)

WarZone Rat代码如下：

![1623307908_60c1b68495ffc382f720c.png!small?1623307908870](https://image.3001.net/images/20210610/1623307908_60c1b68495ffc382f720c.png!small?1623307908870)

 **模板注入** **+DDE auto**

攻击者会将一个带有DDE
auto的恶意文档和一个带有模板注入的恶意文档一起打包作为邮件附件发送，虽然我们不清楚这种组合的意思在哪里？但是这两个文档类样本的最终payload相同，均为Warzone
Rat

![1623307915_60c1b68bdd91ce509bba9.png!small?1623307916275](https://image.3001.net/images/20210610/1623307915_60c1b68bdd91ce509bba9.png!small?1623307916275)

## 与Patchwork组织的关联

在对相关线索进行梳理时，我们发现在魔罗桫的邮箱中出现了patchwork组织的相关邮件，钓鱼链接如下：

213.252.245[.]191/126/?em=Y3N0Y3hpZWppb25n&&Rj5y=aHR0cHM6Ly9tYWlsLjEyNi5jb20=

通过在固定参数后接base64编码的URL链接是Patchwork组织钓鱼时常用的手法，基于C2关联我们发现了两个样本

 **文件名**

|

 **MD5**

|

 **Packer**  
  
---|---|---  
  
feedback_to_NWRC.exe

|

eef2e2146a102e10297a91d28408cac3

|

Golang  
  
app-release_v2.apk

|

fb120df3810782b461da58b3ef114c2b

|

APK([com.example.apaar97.translate](https://www.virustotal.com/gui/search/androguard%253Acom.example.apaar97.translate))  
  
其中Golang样本与我们在样本分析部分的Golang rat同属一个家族，Apk样本均被各大厂商归为PatchWork组织。

![1623307926_60c1b696e0b2e3b2f6949.png!small?1623307927277](https://image.3001.net/images/20210610/1623307926_60c1b696e0b2e3b2f6949.png!small?1623307927277)

通过上述样本，我们得到了一些恶意的github账号

  

 **用户名**  
  
---  
  
jannetgellar  
  
miaao7891  
  
这两个Github账号历史投递样本如下：

 **文件名**

|

 **MD5**

|

 **PDB** **（Packer）**  
  
---|---|---  
  
submit_details.exe

|

25fcc1c3b33412c337c2932d667f796b

|

C:\Users\user\Documents\TestandResult\Shells\CnC\cnc_client\unicode_all\cnc_client\cnc_client_unicode_persist\x64\Release\CnC_Client.pdb  
  
APS_Nomination_Submission.exe

|

9d390501e515af4905dc08fdd4462df7

|

Golang  
  
Feedback for Himalayan Hydro Expo 2019.exe

|

da3fc17b6998d118cbc7f3ecba0fb29b

|

Golang  
  
Feedback_Submission.exe

|

c2edc754c7b0ac2a5b32cbe4562db8d0

|

Golang  
  
Invoice_Generation.exe

|

cba58c1e1e2472ae89ab067d3e345c8f

|

Golang  
  
c2edc754c7b0ac2a5b32cbe4562db8d0  
  
OSA_Feedback_Submission.exe

|

99c00d96024977221cc26196e4856ec3

|

Golang  
  
Submit feedback form.exe

|

fca3ce656e9f51c4d1f4d755ba6b5aa2

|

Golang  
  
Waverider.exe

|

56bf5637512bcb13b0c9e0be13b498bd

|

Golang  
  
WindowsUpdateAssistance.exe

|

d22c62db5eee2f18aeb969a2389a0ab6

|

Python  
  
certificate_generation.exe

|

386d4846a79aef927d317326f6f699a2

|

Golang  
  
feedback.exe

|

fca3ce656e9f51c4d1f4d755ba6b5aa2

|

Golang  
  
feedback_to_MICC.exe

|

eef2e2146a102e10297a91d28408cac3

|

Golang  
  
feedback_to_NWRC.exe

|

eef2e2146a102e10297a91d28408cac3

|

Golang  
  
  

在历史样本中发现了PatchWork组织常用的CnC
Client，除此之外还有发现了经过pyinstaller打包的窃密程序，运行时会先检查与目标IP的联通性，之后收集qq浏览器、firefox浏览器、uc浏览器、chrome浏览器相关信息

![1623307940_60c1b6a489389700af397.png!small?1623307940822](https://image.3001.net/images/20210610/1623307940_60c1b6a489389700af397.png!small?1623307940822)

最终将数据上传到DropBox上

![1623307945_60c1b6a956d7a89b0555c.png!small?1623307945683](https://image.3001.net/images/20210610/1623307945_60c1b6a956d7a89b0555c.png!small?1623307945683)

南亚地区的APT组织之间相互存在重叠似乎并不是一件新鲜事，早在去年的报告中我们提到魔罗桫组织与Bitter组织也存在一定程度的重叠，我们认为这些组织的基础设施很有可能是由同一个机构进行统一管理分配，调度资源包含但不限于域名、IP、邮箱等。

  

## 与Bitter组织的不同

时至今日，我们观察到仍有友商将魔罗桫组织相关样本归类为Bitter组织，上述两个组织除了攻击手法，木马家族，发件邮箱不同外，钓鱼网站的形式也完全不一样，Bitter组织钓鱼页面如下

![1623307951_60c1b6afdc811c910de19.png!small?1623307952174](https://image.3001.net/images/20210610/1623307951_60c1b6afdc811c910de19.png!small?1623307952174)

![1623307962_60c1b6ba26292a47aa367.png!small?1623307962681](https://image.3001.net/images/20210610/1623307962_60c1b6ba26292a47aa367.png!small?1623307962681)

会将账号密码Post同域名下的某个PHP页面，之后会提示操作完成或者跳转到相关页面。

![1623307967_60c1b6bf2ea1b4611a23b.png!small?1623307967509](https://image.3001.net/images/20210610/1623307967_60c1b6bf2ea1b4611a23b.png!small?1623307967509)

而魔罗桫组织钓鱼页面的Post逻辑如下，Post的URL带有复杂的参数，且第一次输入密码后并不会进行跳转，当第二次输入的密码和第一次相同时才进行跳转

![1623307971_60c1b6c3da3b86981779f.png!small?1623307972084](https://image.3001.net/images/20210610/1623307971_60c1b6c3da3b86981779f.png!small?1623307972084)

除此之外魔罗桫组织的钓鱼链接构成非常复杂，只有在域名和URL后缀完全正确的情况下才会加载钓鱼页面，与Bitter组织的钓鱼有很大的不同。这也是目前主流的测绘网站无法探测到魔罗桫组织钓鱼的主要原因。

  

