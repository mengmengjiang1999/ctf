## 概述

自新型冠状病毒爆发以来，奇安信红雨滴团队便第一时间建立了疫情相关网络攻击事件的攻击态势感知系统。并监控到大量以疫情相关信息为诱饵进行的攻击活动，捕获数百起APT、黑产、勒索相关的攻击事件。

![图片.png](https://image.3001.net/images/20200319/1584609994_5e733aca7e434.png!small)

而近期，一批利用疫情相关信息进行定向攻击的特殊样本又进入了我们的视野。在其中一个疑似定向攻击的样本中，攻击者构造了与印度电子信息技术部高度相似的域名（http://email[.]gov[.]in[.]maildrive.email
[/?att=1581914657](https://www.virustotal.com/gui/url/8821796118611f9cf6cc9d9e039730306fd41ef24a05377cdca22607219f5a76)）进行恶意代码下发。该恶意样本植入了宏代码，一旦受害者被诱导启用宏，样本则会释放执行Crimson
RAT远控木马控制受害者机器，并展示疫情相关信息以迷惑受害者。

经关联分析，该样本疑似与南亚来源的APT组织“透明部落”相关。“透明部落”（Transparent
Tribe）是一个南亚来源具有政府背景的APT组织，其长期针对周边国家和地区的军队和政府机构实施定向攻击。红雨滴团队在捕获该样本的第一时间便对其进行了披露，以提醒各安全厂商第一时间关注相关的攻击事件。

![图片.png](https://image.3001.net/images/20200319/1584610008_5e733ad835a0a.png!small)

## 拓展大量的相关样本

基于红雨滴团队疫情网络攻击事件感知系统和红雨滴APT样本关联系统，我们发现近期该组织针对周边国家和地区投递的大量定向攻击样本。这些样本在利用方式上主要分为带恶意宏的文档和伪装成文档的可执行文件两类。

关联捕获的相关特殊样本如下。

### 通过伪造印度电子信息技术部域名传播的样本

文件名  |  Urgent Encl 1.xls  
---|---  
MD5  |  e074c234858d890502c7bb6905f0716e  
利用方式  |  宏  
RAT MD5  |  e262407a5502fa5607ad3b709a73a2e0  
C2  |  107.175.64.209:6728  
文档来源  |  http://email.gov.in.maildrive.email/?att=1581914657  
  
###
![图片.png](https://image.3001.net/images/20200319/1584610026_5e733aea708aa.png!small)  

### 克什米尔信息相关样本

文件名  |  Kashmir Projects.xls  
---|---  
MD5  |  63902ca9d9a24bc52e5deb03846e5546/085b821db833d44ad717f73dd819c29f  
利用方式  |  宏  
RAT MD5  |  E3752C801B5D0246757E9728D217BEB4  
C2  |  5.79.127.138:4586  
诱饵  |  克什米尔地区信息相关  
  
![图片.png](https://image.3001.net/images/20200319/1584610040_5e733af840aec.png!small)

### 印度政府国防部会议资料相关样本

文件名  |  NHQ Notice File.xls  
---|---  
MD5  |  5158c5c17862225a86c8a4f36f054ae2  
利用方式  |  宏  
RAT MD5  |  6D5E033651AE6371B8C8A44B269101B2  
C2  |  142.234.201.80:4488  
诱饵信息  |  印度政府国防部网络安全小组新德里相关会议资料  
  
###
![图片.png](https://image.3001.net/images/20200319/1584610098_5e733b3265eb1.png!small)  

### 印度国防部邮服信息相关样本

文件名  |  All DAs DSPUS.xls  
---|---  
MD5  |  bce8a8ea8d47951abffeec38fbeeeef1  
利用方式  |  宏  
RAT MD5  |  8a1f4a512fe9edbcc62ba4b1c3e08f0a  
C2  |  167.114.138.12:6828  
诱饵信息  |  印度国防部邮件地址更换相关  
  
![图片.png](https://image.3001.net/images/20200319/1584610109_5e733b3d0ed18.png!small)

### 印度某公司任命信息相关样本

文件名  |  2020-21.xls  
---|---  
MD5  |  e061670462a35bb5f46803394f9ca733  
利用方式  |  宏  
RAT MD5  |  9c52beedf24a763c8551715b7736b032  
C2  |  167.114.138.12:6828  
诱饵信息  |  印度某公司人事任命  
  
![图片.png](https://image.3001.net/images/20200319/1584610115_5e733b43c9af8.png!small)

### 印度调查问卷相关样本

文件名  |  engg_review.doc  
---|---  
MD5  |  d4de0d1aa8c1d361d9e1c6444e5121f3  
利用方式  |  宏  
RAT MD5  |  c57defdc4133d27f9bc02a340ac35cd2  
C2  |  185.136.163.197:4442  
诱饵信息  |  印度相关的一些问答题  
  
![图片.png](https://image.3001.net/images/20200319/1584610121_5e733b4996814.png!small)

### 阿富汗安全事件相关样本

部分伪装为文档的可执行文件样本信息如下：

文件名  |  رکز هماهنگی اوپراتیفی زون جنوب.rar （南区业务协调中心）  
---|---  
MD5  |  cafffff2f91b5fa5741bd69f2f89a822  
利用方式  |  伪装成文档的可执行文件  
RAT MD5  |  3bcf1bf59b51a170cbf0b8bad518608d  
C2  |  64.188.25.205  
诱饵信息  |  阿富汗境内安全事件相关信息  
  
###
![图片.png](https://image.3001.net/images/20200319/1584610135_5e733b57a8cd9.png!small)  

### 印度简历相关样本

文件名  |  Preet cv.exe  
---|---  
MD5  |  309c16372edcfe697abf7af66cd6a6da  
利用方式  |  伪装成文档的可执行文件  
C2  |  23.254.119.11:3163  
诱饵  |  印度美女简历  
  
![图片.png](https://image.3001.net/images/20200319/1584610141_5e733b5d64445.png!small)

文件名  |  New Preet cv.exe  
---|---  
MD5  |  284df0208d03af926d1dfc868f0ef474  
利用方式  |  伪装成文档的exe  
RAT MD5  |  888ca13af164c6f514dec5223d319a40  
C2  |  107.150.19.238:3268  
诱饵信息  |  印度相关简历  
  
![图片.png](https://image.3001.net/images/20200319/1584610148_5e733b64dc387.png!small)

## 样本详细分析

### 插入恶意宏一类的攻击样本分析

关联到的利用宏的恶意文档样本中的宏代码基本一致，以疫情相关样本为例进行分析如下。

文件名  |  Urgent Encl 1.xls  
---|---  
MD5  |  e074c234858d890502c7bb6905f0716e  
  
一旦打开该文档，便会弹框提示启用宏：

![图片.png](https://image.3001.net/images/20200319/1584610156_5e733b6c607ee.png!small)

启用宏后便会展示新型冠状病毒相关信息迷惑受害者：

![图片.png](https://image.3001.net/images/20200319/1584610161_5e733b71700e2.png!small)

恶意宏执行后会在%ALLUSERSPROFILE%目录下创建Uahaiws，Edlacar目录：

![图片.png](https://image.3001.net/images/20200319/1584610167_5e733b77cb930.png!small)

之后判断操作系统位数，根据位数选择读取数据的位置，包含不同位数可执行文件的压缩包数据存在UserForm1的两个文本框中：

![图片.png](https://image.3001.net/images/20200319/1584610173_5e733b7d400b7.png!small)![图片.png](https://image.3001.net/images/20200319/1584610178_5e733b82010ab.png!small)

将读取的数据写入到%ALLUSERSPROFILE%Uahaiws\othria.zip，然后将该zip文件加压缩到%
ALLUSERSPROFILE%\Edlacar\dhrwarhsav.exe并执行：

![图片.png](https://image.3001.net/images/20200319/1584610182_5e733b864ca6e.png!small)

释放的可执行文件基本信息如下：

文件名  |  dhrwarhsav.exe  
---|---  
Md5  |  e262407a5502fa5607ad3b709a73a2e0  
C2  |  107.175.64.209:6728  
  
执行后，首先进行一些初始化操作：

![图片.png](https://image.3001.net/images/20200319/1584610190_5e733b8ed0060.png!small)

初始化端口，可用端口如下：

![图片.png](https://image.3001.net/images/20200319/1584610196_5e733b9423c79.png!small)

获取计算机机器名，用户名作为木马版本相关的信息：

![图片.png](https://image.3001.net/images/20200319/1584610203_5e733b9b178dc.png!small)

设置注册表自启动项，实现持久化：

![图片.png](https://image.3001.net/images/20200319/1584610209_5e733ba149129.png!small)

初始化配置结束后，开始与c2通信，获取命令执行：

![图片.png](https://image.3001.net/images/20200319/1584610214_5e733ba69f095.png!small)

获取控制命令：

![图片.png](https://image.3001.net/images/20200319/1584610221_5e733bad33f07.png!small)

之后进入命令分发，根据命令执行对应功能：

![图片.png](https://image.3001.net/images/20200319/1584610225_5e733bb1c9a13.png!small)

支持的命令如下表所示：

Command  |  function  
---|---  
dhrwarhsav-procl |  枚举进程并打印  
dhrwarhsav-getavs |  枚举进程并打印  
dhrwarhsav-thumb |  上传gif图像  
dhrwarhsav-clping |  刷新运行时间  
dhrwarhsav-putsrt |  复制木马,设置自启动  
dhrwarhsav-filsz |  获取文件属性  
dhrwarhsav-rupth |  返回文件路径  
dhrwarhsav-dowf |  文件下载  
dhrwarhsav-endpo |  结束指定进程  
dhrwarhsav-scrsz |  设置截屏参数  
dhrwarhsav-cownar |  写入文件并执行  
dhrwarhsav-cscreen |  屏幕截图  
dhrwarhsav-dirs |  获取磁盘目录信息  
dhrwarhsav-stops |  停止截屏  
dhrwarhsav-scren |  获取屏幕截图  
dhrwarhsav-cnls |  参数初始化  
dhrwarhsav-udlt |  用户删除  
dhrwarhsav-delt |  文件删除  
dhrwarhsav-afile |  读取文件信息  
dhrwarhsav-listf |  文件搜索  
dhrwarhsav-file |  上传文件  
dhrwarhsav-info |  获取用户信息  
dhrwarhsav-runf |  文件执行  
dhrwarhsav-fles |  查找文件  
dhrwarhsav-dowr |  文件下载  
dhrwarhsav-fldr |  根据路径列出文件夹  
  
### 伪装为文档的可执行文件一类样本分析

以关联到的阿富汗地区相关安全事件的伪装为文档的可执行样本为例进行分析如下。

文件名  |  رکز هماهنگی اوپراتیفی زون جنوب.rar （南区业务协调中心）  
---|---  
MD5  |  cafffff2f91b5fa5741bd69f2f89a822  
  
该样本以رکز هماهنگی اوپراتیفی زون جنوب（南区业务协调中心）为诱饵，将文件图标设置为word文档图标，诱导受害者执行：

![图片.png](https://image.3001.net/images/20200319/1584610243_5e733bc33234b.png!small)

该样本运行流程与恶意宏代码基本一致，可看出出自同一组织之手。首先判断操作系统位数，根据位数读取不同资源：

![图片.png](https://image.3001.net/images/20200319/1584610250_5e733bca941c2.png!small)

将获取的资源保存到%ALLUSERSPROFILE% \DIllb\mtdlhsrivan.zip文件中，再解压该zip文件到%
ALLUSERSPROFILE% @DIllb\mtdlhsrivan.exe执行：

![图片.png](https://image.3001.net/images/20200319/1584610257_5e733bd1440c3.png!small)

之后再次从资源中获取一个docx文件保存到”\مرکز هماهنگی اوپراتیفی زون جنوب-1 .docx”中，并打开该文档以迷惑受害者：

![图片.png](https://image.3001.net/images/20200319/1584610263_5e733bd766dda.png!small)

展示诱饵文档如下，内容为阿富汗境内的一些安全事件相关信息：

![图片.png](https://image.3001.net/images/20200319/1584610269_5e733bddd607a.png!small)![图片.png](https://image.3001.net/images/20200319/1584610275_5e733be37f2ae.png!small)

文件名  |  Mtdlhsrivan.exe  
---|---  
Md5  |  3bcf1bf59b51a170cbf0b8bad518608d  
  
释放执行的Mtdlhsrivan.exe与上述dhrwarhsav.exe基本一致，是同一家族木马。执行后进行相关配置信息初始化：

![图片.png](https://image.3001.net/images/20200319/1584610281_5e733be9a8b4f.png!small)

通过mdlthsrvainCMD.mdlthsrvainserverIPD()函数进行c2初始化设置：

![图片.png](https://image.3001.net/images/20200319/1584610295_5e733bf762df4.png!small)  

初始化端口，可用端口如下：

![图片.png](https://image.3001.net/images/20200319/1584610310_5e733c066f536.png!small)  

命令功能与上述dhrwarhsav.exe完全相同，不再赘述。

![图片.png](https://image.3001.net/images/20200319/1584610315_5e733c0b620c7.png!small)  

## 溯源关联

通过对释放的木马，恶意宏等分析，奇安信威胁情报中心判断本次攻击活动的幕后黑手疑似为Transparent Tribe。

1\. 释放的木马为Crimson RAT，与之前公开披露的Crimson RAT基本一致，功能完全一致

![图片.png](https://image.3001.net/images/20200319/1584610325_5e733c1572fa4.png!small)

而Crimson RA是Transparent Tribe独有的远程控制木马：

![图片.png](https://image.3001.net/images/20200319/1584610331_5e733c1b665e7.png!small)

2\. 恶意宏与Transparent Tribe组织之前被披露的样本基本一致，变化很小

![图片.png](https://image.3001.net/images/20200319/1584610336_5e733c20debad.png!small)

3\. 奇安信ALPHA威胁分析平台对相关ioc已标注Transparent Tribe

![图片.png](https://image.3001.net/images/20200319/1584610343_5e733c27e9dc8.png!small)

## 总结

随着新型冠状病毒在全球范围的蔓延，APT组织与黑产团伙借用疫情相关信息的攻击活动将越来越频繁，相关的网络攻击已存在蔓延态势的苗头。奇安信威胁情报中心红雨滴团队将持续关注披露相关攻击活动。同时，奇安信威胁情报中心提醒用户在日常的工作中，切勿随意打开来历不明的邮件附件，不安装未知来源的APP，提高个人网络安全意识。

若需运行，安装来历不明的应用，可先通过奇安信威胁情报文件深度分析平台（<https://sandbox.ti.qianxin.com/sandbox/page>）进行简单判别。目前已支持包括Windows、安卓平台在内的多种格式文件深度分析。

![图片.png](https://image.3001.net/images/20200319/1584610352_5e733c3088f0e.png!small)

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。

## IOCs

 **MD5:**

cafffff2f91b5fa5741bd69f2f89a822

3bcf1bf59b51a170cbf0b8bad518608d

4d33804d5e6fd053837ddd374d7e32b5

c3e60bd2cf811f5049e1ed106c533f36

cbfae579a25df1e2fe0e02934efd65dc

d62156fa2c5bffdc63f0975c5482eab6

e074c234858d890502c7bb6905f0716e

e262407a5502fa5607ad3b709a73a2e0

d4de0d1aa8c1d361d9e1c6444e5121f3

c57defdc4133d27f9bc02a340ac35cd2

48476da4403243b342a166d8a6be7a3f

a3a0750d74705d235b60556f1331ae9b

284df0208d03af926d1dfc868f0ef474

888ca13af164c6f514dec5223d319a40

bce8a8ea8d47951abffeec38fbeeeef1

8a1f4a512fe9edbcc62ba4b1c3e08f0a

309c16372edcfe697abf7af66cd6a6da

15b47ac554679f7ca2fac728123f2694

1F0FE3A696143743B9C77B77332C0902

b3f8eee133ae385d9c7655aae033ca3e

a3a0750d74705d235b60556f1331ae9b

e061670462a35bb5f46803394f9ca733

9c52beedf24a763c8551715b7736b032

5158c5c17862225a86c8a4f36f054ae2

6D5E033651AE6371B8C8A44B269101B2

63902ca9d9a24bc52e5deb03846e5546

085b821db833d44ad717f73dd819c29f

80812d4b01071a137f5bf845beb80e8b

8FC5ADBB6C01030F750C1ED8E913C876

**C2:**

64.188.25.205

198.46.177.73:6421

181.215.47.169:3368

107.175.64.209:6728

185.136.163.197:4442

198.46.177.73:6421

107.150.19.238:3268

167.114.138.12:6828

23.254.119.11:3163

167.114.138.12:6828

tgservermax.duckdns.org

198.46.177.73:6421

167.114.138.12:6828

142.234.201.80:4488

5.79.127.138:4586

5.189.134.216:5156

## 参考

<https://www.proofpoint.com/sites/default/files/proofpoint-operation-transparent-tribe-threat-insight-en.pdf>

<https://www.freebuf.com/column/228135.html>

