## **一、** **背景**

**污水（MuddyWater）APT组织是一个疑似来自伊朗的攻击组织，该组织主要针对中东地区、前苏联国家、土耳其等中亚国家的政府部门进行攻击。该组织是目前全球最活跃的的APT攻击组织之一，腾讯安全御见威胁情报中心也曾多次披露该组织的攻击活动。**

近期，腾讯安全御见威胁情报中心又持续监测到该组织在中亚、中东地区的一些攻击活动，包括塔吉克斯坦的外交、政府部门、土耳其的政府部门等。并且该组织也更新了其攻击TTPs，如宏代码拼接内置硬编码字符串写入VBE；利用注册表，自启动文件夹启动VBE等，此外在受害者选择上也更为精确，通过第一阶段后门反馈的受害者信息挑选目标进行下一步持久化等。

本文为对近期一些活动的攻击总结，此外腾讯安全御见威胁情报中心还将继续持续对该组织的一些攻击活动进行跟踪。

##  **二、** **攻击活动**

###  **1.攻击活动一：针对塔斯克斯坦联合国部门的攻击活动**

 **1）攻击诱饵信息：**

文件hash  |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
1e8afda2721eff834ed9c87371a432fe  |  UNDP_TJK_Agreement_ORGS.doc  |  MS Word
Document  |  Khursheda Aknazarova  |  win  |  2019-05-29 12:32:00  |
2019-05-30 04:07:35  
  
文件诱饵内容如下：

![1.png](https://image.3001.net/images/20190611/1560215992_5cff01b89ab2e.png!small)

![2.png](https://image.3001.net/images/20190611/1560216035_5cff01e35524a.png!small)

![3.png](https://image.3001.net/images/20190611/1560216024_5cff01d8096ed.png!small)

从诱饵内容来看，该波钓鱼攻击的对象为塔吉克斯坦联合国相关部门。

打开文档后，提示开启宏。执行宏代码后，首先会创建文件%public%dj.txt，并写入硬编码在宏中的字符串，随后再在启动文件夹下创建antibiotic.vbe文件，并将控件domainServer中的内容进行拼接写入vbe文件：

![4.png](https://image.3001.net/images/20190611/1560216031_5cff01df9db7f.png!small)

![5.png](https://image.3001.net/images/20190611/1560216056_5cff01f8d75a8.png!small)

 **2）Antibiotic.vbe分析**

vbe解密后展开，这段vbs代码作用是创建%public%USERCa.jpeg文件，并将内置编码字符串写入该文件中，随后利用powershell运行该图片：

![6.png](https://image.3001.net/images/20190611/1560216056_5cff01f8bd910.png!small)

 **3）USERCa.jpeg分析**

该段内容经过编码混淆：

![7.png](https://image.3001.net/images/20190611/1560216092_5cff021cec8f7.png!small)

去混淆后的powershell脚本为：

![8.png](https://image.3001.net/images/20190611/1560216096_5cff0220e4d57.png!small)

脚本首先会解密出来相关的c2配置：

![9.png](https://image.3001.net/images/20190611/1560216105_5cff02290064c.png!small)

随后会收集本地机器信息写入%temp%log.txt中，然后获取guid和c2拼接成地址，最后将log.txt中的内容读取并进行base64编码，传送给拼接的地址，最后再去请求服务器下载最后的powershell木马。

post本地信息url：<http://185.244.149.218/game.php?NewsIID=guid>

![10.png](https://image.3001.net/images/20190611/1560216113_5cff02313c64a.png!small)

接着下载下一步powershell后门：

![11.png](https://image.3001.net/images/20190611/1560216120_5cff02380d77c.png!small)

[http://185.244.149.218/JpeGDownload/{guid}.png](http://185.244.149.218/JpeGDownload/%7Bguid%7D.png)

![12.png](https://image.3001.net/images/20190611/1560216165_5cff0265bc418.png!small)

### 2.攻击活动二：针对塔吉克斯坦政府部门的攻击

 **1）攻击诱饵**

文件hash  |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
6cb076f1f42573c5c43083a89bcfe442  |  Zakupki_Agency on Public Procurement.doc
|  MS Word Document  |  win7  |  win7  |  2019-05-23 04:00:00  |  2019-05-27
00:11:18  
  
文档内容为：

![13.png](https://image.3001.net/images/20190611/1560216196_5cff02843cb41.png!small)

![14.png](https://image.3001.net/images/20190611/1560216178_5cff0272464ba.png!small)

从诱饵内容来看是针对塔吉克斯坦采购部门的一次钓鱼攻击。

该文档打开后，同样提示需要打开宏。而执行宏代码后，会创建%Temp%aulngr.vbe和%Temp%bbbbbb.tmp并将内置硬编码数据写入。随后设置注册表自启：

![15.png](https://image.3001.net/images/20190611/1560216238_5cff02ae9cc01.png!small)

![16.png](https://image.3001.net/images/20190611/1560216246_5cff02b61bad1.png!small)

该生成的vbe的内容跟上面的攻击差别不大，不再赘述：

![17.png](https://image.3001.net/images/20190611/1560216252_5cff02bc536c8.png!small)

 **2）最终的jepg分析**

最终下载回来的jepg实际为一个powershell的ps1脚本：

![18.png](https://image.3001.net/images/20190611/1560216259_5cff02c3cbaff.png!small)

对其解码后为：

![19.png](https://image.3001.net/images/20190611/1560216267_5cff02cbd6562.png!small)

解码后的脚本包含大量的混淆，其中大量无用代码。

脚本首先会去利用内置解密函数解密C2：

![20.png](https://image.3001.net/images/20190611/1560216277_5cff02d5a3cef.png!small)

随后收集本地信息，包括本地用户名、系统名、系统版本、ip等：

![21.png](https://image.3001.net/images/20190611/1560216285_5cff02dd3b145.png!small)

如获取外网ip：

![22.png](https://image.3001.net/images/20190611/1560216291_5cff02e36e0c6.png!small)

如设置注册表，获取guid：

![23.png](https://image.3001.net/images/20190611/1560216299_5cff02ebd1c61.png!small)

接着将收集到的本地信息http post到C2服务器，%guid%表示本机guid。

url：[http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=reg&UU=%guid%](http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=reg&UU=%guid%)

![24.png](https://image.3001.net/images/20190611/1560216307_5cff02f3dbb2e.png!small)

然后，不断http get C2服务器，获取下一步执行指令：

URL：

<http://83.171.238.62/command/%guid%.cmd>

[http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=uDel&filename=%guid%.cmd](http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=uDel&filename=%guid%.cmd)

![25.png](https://image.3001.net/images/20190611/1560216314_5cff02fa5fe34.png!small)

该powershell 木马支持三种指令，并且将结果通过base64编码后http post给C2服务器：

指令一：获取截图

URL：[http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=sc&i=%guid%.png](http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=sc&i=%guid%.png)

指令二：执行cmd指令

URL：[http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=res&R=%guid%](http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=res&R=%guid%)

指令三：执行powershell

URL：[http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=res&R=%guid%](http://83.171.238.62/ls.php?TOKEN=Pomy54tvbRetceX&funx=res&R=%25guid%25)

![26.png](https://image.3001.net/images/20190611/1560216324_5cff030415291.png!small)

![27.png](https://image.3001.net/images/20190611/1560216331_5cff030b0c5b3.png!small)

### 3.攻击活动三：针对塔吉克斯坦外交部门（如使领馆）的攻击

文件hash  |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
3cc5e7df7e9b0b216327ae7b451b8b90  |  TAJIKISTAN_INCORPORATE_E-GOVERMENT.docx
|  Office Open XML Document  |  N/A  |  N/A  |  2019-04-18 09:20:00  |
2019-05-28 16:24:01  
  
![28.png](https://image.3001.net/images/20190611/1560216338_5cff0312261c7.png!small)

![29.png](https://image.3001.net/images/20190611/1560216344_5cff0318c5d4c.png!small)

通过模板注入执行下载命令：

![30.png](https://image.3001.net/images/20190611/1560216356_5cff032433dfc.png!small)

### 4.攻击活动四：针对土耳其的政府的攻击

文件hash  |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
28ca1d5f6ac9a2e5c4d2e3b41276ffe2  |  ggm sigorta dosyasi.docx  |  Office Open
XML Document  |  sevginaz  |  sevginaz  |  2019-04-18 08:34:00  |  2019-04-18
13:40:30  
b41e0c8a2ce8e9de32b9f62b7c3ca047  |  Cumhurbaşkanlığı Programı hakkında
yapılan çalışmalar sonucu oluşan ekteki taslağın.docx  |  Office Open XML
Document  |  sevginaz  |  sevginaz  |  2019-04-16 09:09:00  |  2019-04-16
11:21:50  
  
![31.png](https://image.3001.net/images/20190611/1560216367_5cff032f98721.png!small)

![32.png](https://image.3001.net/images/20190611/1560216373_5cff033591993.png!small)

![33.png](https://image.3001.net/images/20190611/1560216380_5cff033c76775.png!small)

同样使用模板注入的方式：

![34.png](https://image.3001.net/images/20190611/1560216386_5cff0342ac085.png!small)

### 5.其他的一些攻击活动：

文件hash  |  文件名  |  文件类型  |  文档作者  |  最后修改者  |  最后修改时间  |  上传到VT时间  
---|---|---|---|---|---|---  
72f92f81721fe832316f7b27ad328e17  |  Tapal-6.doc  |  MS Word Document  |  N/A
|  Windows User  |  2019-05-26 15:03:00  |  2019-05-26 14:13:46  
97bf0d6e11ee4118993ad9c4b959c916  |  company information list.doc  |  MS Word
Document  |  Babak Amiri  |  jack  |  2019-04-23 21:18:00  |  2019-04-24
09:23:27  
  
![35.png](https://image.3001.net/images/20190611/1560216394_5cff034aa31ce.png!small)

![36.png](https://image.3001.net/images/20190611/1560216401_5cff03513cd0d.png!small)

宏代码为：

![37.png](https://image.3001.net/images/20190611/1560216409_5cff0359b2049.png!small)

从宏名字看，为BlackWater活动。而对比收集本地信息高度一致：

![38.png](https://image.3001.net/images/20190611/1560216424_5cff0368a4b68.png!small)

![39.png](https://image.3001.net/images/20190611/1560216442_5cff037a3acc2.png!small)

该活动思科的talos团队已经披露过，本文就不再追溯。

##  **三、** **总结**

污水（MuddyWater）APT
组织是近几年来全球最活跃的攻击组织之一，虽然该组织的攻击活动多次被多个安全公司所曝光，但是该组织并未停止他们的攻击活动，并且持续的更新其TTPs来对抗安全软件的检测。此外，鱼叉攻击、宏代码等传统的攻击方式依然是最有效、使用最广泛的攻击方式，因此相关部门和单位切不可掉以轻心。因为APT攻击不会因为被曝光而停止，只要攻击目标有价值，APT攻击组织必然会持续的对目标进行攻击，直到达成目的。因此我们建议相关部门和单位：

1.提升安全意识，不要打开来历不明的邮件的附件；除非文档来源可靠，用途明确，否则不要轻易启用Office的宏代码；

2.使用杀毒软件防御可能得病毒木马攻击，对于企业用户，推荐使用腾讯御点终端安全管理系统。腾讯御点内置全网漏洞修复和病毒防御功能，可帮助企业用户降低病毒木马入侵风险；

## **四、** **附录**

### 1.IOCs

 **MD5：**

1e8afda2721eff834ed9c87371a432fe

d129aab947fc6a8fb7ae9df5bc70d460

176e56a418bc4c11783d6411aef94c38

f460780c1cad15c3883868cb5050375c

6cb076f1f42573c5c43083a89bcfe442

9d2da5228e21594ab46b4f5281d38b8f

57c0b9e0fed9a65c63ec0825b6867a40

34a072f42905f9de31523616e8f207b1

3cc5e7df7e9b0b216327ae7b451b8b90

28ca1d5f6ac9a2e5c4d2e3b41276ffe2

b41e0c8a2ce8e9de32b9f62b7c3ca047

72f92f81721fe832316f7b27ad328e17

0cd84d601971a91cc023e16d94cc7e6c

 **C &C：**

185.244.149.218

185.185.25.175

83.171.238.62

38.132.99.167

82.102.8.101

###  **2.参考链接**

1）Recent MuddyWater-associatedBlackWater campaign shows signs of new anti-detection techniques <https://blog.talosintelligence.com/2019/05/recent-muddywater-associated-blackwater.html>

2）“污水”（MuddyWater）APT组织攻击活动汇总（2018年3月13日）<https://mp.weixin.qq.com/s/D1zuXjQPYleoohqpjq57PA>

3）MuddyWater（污水）APT组织针对土耳其安全部门的定向攻击
<https://mp.weixin.qq.com/s/DggTaSJPiM179Qynzx6KFA>

4）污水（MuddyWater）APT组织针对白俄罗斯国防部、外交部等机构的定向攻击活动分析
<https://mp.weixin.qq.com/s/qzTGQMvV-IaAlP_IwCHnLg>

***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

