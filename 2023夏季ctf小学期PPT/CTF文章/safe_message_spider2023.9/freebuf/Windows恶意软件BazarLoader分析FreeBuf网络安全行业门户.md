**BazarLoader是基于Windows的恶意软件，主要通过电子邮件等方式传播。**
犯罪分子通过恶意软件后门访问受感染的主机，并对目标域网络环境进行探测，部署Cobalt
Strike，绘制网络拓扑图。如果为高价值目标，犯罪分子就会开始横向拓展，部署Conti、Ryuk等勒索软件。

## BazarLoader传播方式

2021年夏天，研究人员发现攻击者通过电子邮件传播BazarLoader恶意软件。目前发现三个攻击活动中使用了该恶意软件：

> “BazarCall”中使用含有BazarLoader的电子邮件作为初始攻击手段，诱导受害者点击含有恶意软件的文件；  
> 七月初，以侵权为主题的“Sleet Images Evidence.ZIP”中包含了BazarLoader；  
> 7月底，TA551（Shathak）开始通过英语电子邮件传播BazarLoader。

除了这三个主要攻击活动外，研究人员还发现了含有BazarLoader的Excel电子表格，其传播感染方式如下：

![Chain of events from BazarLoader infection on Aug. 19, 2021. Excel file with
.xlsb file extension, enable macros, web traffic for BazarLoader, BazarLoader,
Bazar C2 traffic, Cobalt Strike, Cobalt Strike traffic, ADfind and batch file,
Cobalt Strike and Bazar C2 traffic
continues](https://image.3001.net/images/20211025/1635127651_617611635e1e0a7542b71.jpeg!small)

## 恶意Excel表格

恶意Excel电子表格在8月18日被首次发现的，其最后一次修改日期为8月17日。文件后缀为‘.xlsb’，此文件中包含BazarLoader。下图为恶意Excel截图：

![A malicious Excel template that attempts to instill confidence by taking
advantage of the DocuSign brand name and
image.](https://image.3001.net/images/20211025/1635127655_61761167e1fc42f5d5bb1.jpeg!small)

攻击者试图通过利用DocuSign来迷惑受害者。受害者Windows主机上启用恶意宏后，表格中会出现新的sheet，如下图所示：

![A fake invoice that appears on a malicious Excel spreadsheet. The red arrow
indicates a new tab that appears after enabling
macros.](https://image.3001.net/images/20211025/1635127658_6176116acfe64ef8a3c50.jpeg!small)

此时恶意代码已经执行，释放出BazarLoader。

## BazarLoader分析

恶意文件会从‘hxxps://pawevi[.]com/lch5.dll’中下载BazarLoader的DLL文件，并保存到‘C:\Users\\[username]\tru.dll’。

![BazarLoader DLL is saved to the infected user's home directory. The black
arrow indicates where it appears in the
screenshot.](https://image.3001.net/images/20211025/1635127661_6176116d92a93c40f678e.jpeg!small)

BazarLoader DLL会复制到另一个位置，并修改Windows注册表。

![BazarLoader DLL persistent on the infected host, as shown in the
screenshot.](https://image.3001.net/images/20211025/1635127665_61761171c82e3a2c5950a.jpeg!small)

## Bazar C2流量

样本BazarLoader通过443端口从104.248.174.225下载BazarBackdoor。BazarBackdoor通过443端口使用HTTPS生成C2活动，传输至104.248.166.170。

![Traffic from the BazarLoader infection filtered in Wireshark. One black
arrow indicates the section that represents Bazar C2 traffic. Another arrow
indicates traffic for BazarLoader
DLL.](https://image.3001.net/images/20211025/1635127668_61761174a5e5a3883fe00.jpeg!small)

## Cobalt Strike恶意活动

BazarLoader感染大约41分钟后，受感染Windows主机通过https与gojihu[.]com和yuxicu[.]com下载运行Cobalt
Strike，如下图：

![Wireshark activity. The black arrows indicate where the Cobalt Strike
activity
begins.](https://image.3001.net/images/20211025/1635127672_61761178a9807164db957.jpeg!small)

通过Bazar C2获得Cobalt Strike DLL文件，保存到AppData\Roaming目录下，下图为正在运行的Cobalt Strike：

![Cobalt Strike started approximately 43 minutes after the BazarLoader
infection, as illustrated in these screenshots from Process
Hacker.](https://image.3001.net/images/20211025/1635127675_6176117b7304107b9779a.jpeg!small)

## Reconnaissance恶意活动

Cobalt Strike运行两分钟后，环境信息采集工具会下载到受感染主机上‘C:\ProgramData\AdFind.exe’。  
AdFind是一个命令行工具，攻击者通过批处理文件来运行该工具。下图显示了AdFind位置、批处理文件以及采集结果文件。

![Network enumeration after Cobalt
Strike.](https://image.3001.net/images/20211025/1635127678_6176117ea416d720bda8e.jpeg!small)

Bat脚本内容如下：

![Commands used for AdFind.exe, displayed in a screenshot of
Notepad.](https://image.3001.net/images/20211025/1635127684_617611840d09a0db283f1.jpeg!small)

> adfind.exe -f "(objectcategory=person)" > ad_users.txt  
> adfind.exe -f "objectcategory=computer" > ad_computers.txt  
> adfind.exe -f "(objectcategory=organizationalUnit)" > ad_ous.txt  
> adfind.exe -sc trustdmp > trustdmp.txt  
> adfind.exe -subnets -f (objectCategory=subnet)> subnets.txt  
> adfind.exe -f "(objectcategory=group)" > ad_group.txt  
> adfind.exe -gcb -sc trustdmp > trustdmp.txt

## IOC

 **BazarLoader Excel SHA256 hash:**  
8662d511c7f1bef3a6e4f6d72965760345b57ddf0de5d3e6eae4e610216a39c1  
 **Malicious DLL for BazarLoader , SHA256 hash:**  
caa03c25583ea24f566c2800986def73ca13458da6f9e888658f393d1d340ba1  
Online location: hxxps://pawevi[.]com/lch5.dll  
Initial saved location: C:\Users\\[username]\tru.dll  
Final location: C:\Users\\[username]\AppData\Local\Temp\Damp\kibuyuink.exe  
Run method: regsvr*.exe /s [filename]  
 **Malicious DLL for Cobalt Strike, SHA256 hash:**  
73b9d1f8e2234ef0902fca1b2427cbef756f2725f288f19edbdedf03c4cadab0  
File location: C:\Users\\[username]\AppData\Roaming\nubqabmlkp.iowd  
Run method: rundll32.exe [filename],Entrypoint

## 原文链接

[unit42](https://unit42.paloaltonetworks.com/bazarloader-network-reconnaissance/)

