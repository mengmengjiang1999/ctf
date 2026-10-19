## 背景概述

**近日，深信服安全团队捕获到利用Confluence新型漏洞传播勒索病毒的事件，已有政企机构受到攻击，黑客团伙通过漏洞利用入侵服务器，上传Downloader脚本文件，连接C
&C端下载运行勒索病毒。通过样本中提取的IP进行关联，该攻击事件与利用Confluence漏洞(CVE-2019-3396)传播GandCrab勒索病毒攻击事件有密切的关联。**

经深信服安全团队分析，该勒索病毒在功能代码结构上与“侠盗”病毒GandCrab非常相似，同时应用了多种反调试和混淆方式，进行调试时会导致主机蓝屏，且似乎还处于不断调试的阶段，与“侠盗”团队有很大关联，确认是GandCrab勒索病毒最新变种。该勒索病毒使用RSA+AES算法进行加密，加密文件后会使用随机字符串作为后缀，且更换屏幕为深蓝背景的Imagetext，具体勒索特征如下：

![](https://image.3001.net/images/20190429/1556502454_5cc657b6540ec.png!small)

释放勒索信息文件“加密后缀-readme.txt”：

![](https://image.3001.net/images/20190429/1556502457_5cc657b9be887.png!small)

## 排查过程

1\. 排查被加密的服务器，通过修改日期，发现文件在4.27日五点五十左右被加密：

![](https://image.3001.net/images/20190429/1556502461_5cc657bd4d4a7.png!small)

2\. 排查病毒文件，发现在temp目录和IE缓存目录下存在勒索病毒文件：

![](https://image.3001.net/images/20190429/1556502464_5cc657c049076.png!small)

3\. 排查到用于下载勒索病毒文件的vbs脚本，文件名为poc.vbs经过检查确定是针对confluence最新漏洞的poc，属于手动投毒：

![](https://image.3001.net/images/20190429/1556502471_5cc657c7a2f93.png!small)

4\. 病毒文件确认，加密现象与遭到攻击的服务器相同：

![](https://image.3001.net/images/20190429/1556502488_5cc657d8d05ca.png!small)

## 威胁情报关联

1\. 通过哈希搜索，Virustotal上该病毒文件的上传时间就在近日，且通过加密现象来看属于一种新的勒索病毒变种：

![](https://image.3001.net/images/20190429/1556502492_5cc657dc558d0.png!small)

2\. 通过病毒下载链接中的IP（188[.]166[.]74[.]218）进行威胁情报关联，该C&C端近日被用于下载恶意文件：

![](https://image.3001.net/images/20190429/1556502495_5cc657df9dcab.png!small)

3\. 该IP还关联到通过Confluence漏洞(CVE-2019-3396)传播CandCrab勒索病毒的相关事件，链接如下：

> <https://blog.alertlogic.com/active-exploitation-of-confluence-> vulnerability-cve-2019-3396-dropping-gandcrab-ransomware/>

由此可见，该攻击者（团伙）近期活跃频繁，且惯用手法是利用新型漏洞传播勒索病毒，入侵用户终端，并且疑似在开发新型的勒索病毒家族变种。

## 病毒详细分析

1\. 样本母体使用各种加密操作，如下所示：

![](https://image.3001.net/images/20190429/1556502514_5cc657f283a38.png!small)

2\. 解密出第一层Payload代码，如下所示：

![](https://image.3001.net/images/20190429/1556502518_5cc657f6b7b44.png!small)

3\. 解密出勒索核心Payload代码，如下所示：

![](https://image.3001.net/images/20190429/1556502521_5cc657f9aee23.png!small)

4\. 创建互斥变量，如下所示：

![](https://image.3001.net/images/20190429/1556502525_5cc657fd075e6.png!small)

5\. 在内存中解密出勒索相关信息，如下所示：

![](https://image.3001.net/images/20190429/1556502528_5cc658004185f.png!small)

6\. 提升进程权限，如下所示：

![](https://image.3001.net/images/20190429/1556502533_5cc65805599bc.png!small)

7\. 内存中解密出勒索信息文本，如下所示：

![](https://image.3001.net/images/20190429/1556502537_5cc6580982105.png!small)

8\. 生成随机勒索信息文本文件名：[随机数字字符串]+[-readme.txt]，如下所示：

![](https://image.3001.net/images/20190429/1556502541_5cc6580dc5e9e.png!small)

9\. 获取键盘布局，如下所示：

![](https://image.3001.net/images/20190429/1556502545_5cc658114234b.png!small)

如果为以下区域，则退出程序，如下所示:

![](https://image.3001.net/images/20190429/1556502548_5cc658142e063.png!small)

对应的相应区域，如下所示：

**序号** | **简称** | **英文名称** | **中文名称**  
---|---|---|---  
18 | ko | Korean | 朝鲜语  
19 | nl | Dutch | 荷兰语  
20 | no | Norwegian | 挪威语  
21 | pl | Polish | 波兰语  
22 | pt | Portuguese | 葡萄牙语  
24 | ro | Romanian | 罗马尼亚语  
25 | ru | Russian | 俄语  
26 | hr | Croatian | 克罗地亚语  
27 | sk | Slovak | 斯洛伐克语  
28 | sq | Albanian | 阿尔巴尼亚语  
29 | sv | Swedish | 瑞典语  
30 | th | Thai | 泰语  
31 | tr | Turkish | 土耳其语  
32 | ur | Urdu | 乌尔都语  
33 | id | Indonesian | 印度尼西亚语  
34 | uk | Ukrainian | 乌克兰语  
35 | be | Belarusian | 白俄罗斯语  
36 | sl | Slovenian | 斯洛文尼亚语  
37 | et | Estonian | 爱沙尼亚语  
38 | lv | Latvian | 拉脱维亚语  
39 | lt | Lithuanian | 立陶宛语  
41 | fa | Persian | 波斯语  
42 | vi | Vietnamese | 越南语  
43 | hy | Armenian | 亚美尼亚语  
44 | az | Azeri | 阿泽里语  
  
10\. 遍历进程，结束mysql.exe进程，如下所示：

![](https://image.3001.net/images/20190429/1556502575_5cc6582f17cc2.png!small)

11\. 通过cmd.exe执行相应的命令，删除磁盘卷影，如下所示：

![](https://image.3001.net/images/20190429/1556502578_5cc65832be54e.png!small)

12\. 遍历磁盘文件目录，如下所示：

![](https://image.3001.net/images/20190429/1556502582_5cc65836331f1.png!small)

13\. 遍历共享文件目录，如下所示：

![](https://image.3001.net/images/20190429/1556502585_5cc65839415dc.png!small)

14\. 遍历磁盘文件，如下所示：

![](https://image.3001.net/images/20190429/1556502588_5cc6583c39d2c.png!small)

15\. 加密文件，使用RSA+AES算法进行加密，如下所示：

![](https://image.3001.net/images/20190429/1556502683_5cc6589b28264.png!small)

16\. 生成勒索信息桌面图片，更改桌面背景图片，如下所示：

![](https://image.3001.net/images/20190429/1556502686_5cc6589e6c3ba.png!small)

17\. 从内存中解密出来的域名列表中，选取一个然后进行URL拼接，如下所示：

![](https://image.3001.net/images/20190429/1556502722_5cc658c2e3ae4.png!small)

相应的域名列表，如下所示：

    
    
    sochi-okna23.ru;[www.blavait.fr](http://www.blavait.fr);kamin-somnium.de;geoweb.software;[www.drbrianhweeks.com](http://www.drbrianhweeks.com);kombi-dress.com;johnkoen.com;prodentalblue.com;transifer.fr;matteoruzzaofficial.com;jax-interim-and-projectmanagement.com;hawaiisteelbuilding.com; [www.kausette.com](http://www.kausette.com);[www.galaniuklaw.com](http://www.galaniuklaw.com);[www.atma.nl](http://www.atma.nl);[www.piestar.com](http://www.piestar.com);[www.kerstliedjeszingen.nl](http://www.kerstliedjeszingen.nl);biodentify.ai;endlessrealms.net;condormobile.fr; [www.cxcompany.com](http://www.cxcompany.com)等（此处省略N多字...）

18\. 拼接出来的URL，然后发送相应的数据，如下所示：

![](https://image.3001.net/images/20190429/1556502726_5cc658c6ed4fd.png!small)

主机相关数据，如下所示：

![](https://image.3001.net/images/20190429/1556502730_5cc658ca2791c.png!small)

发送相应的HTTP请求，如下所示：

![](https://image.3001.net/images/20190429/1556502734_5cc658ce5b964.png!small)

## 解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

## 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修补漏洞。

2、对重要的数据文件定期进行非本地备份。

3、升级Confluence版本：

> 版本6.6.12及更高版本的6.6.x.
>
> 版本6.12.3及更高版本的6.12.x
>
> 版本6.13.3及更高版本的6.13.x
>
> 版本6.14.2及更高版本

4、主动升级widgetconnector-3.1.3.jar到 widgetconnector-3.1.4.jar。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

