**由于COVID-19疫情越来越严重，世界各地的公司都已选择远程办公。早在病毒爆发之前，zoom就已经被许多公司和远程工作的人用来召开会议等。与此同时，网络犯罪分子也在利用这些工具传播恶意软件。近期发现Coinminer与Zoom安装程序捆绑在一起，诱骗目标下载安装恶意软件。这些安装软件并不是来自Zoom官方下载中心，都是来自虚假恶意网站。**

##
![1.png](https://image.3001.net/images/20200406/1586148243_5e8ab3938d806.png!small)
恶意文件分析

恶意文件是AutoIt编译的木马Win32.MOOZ.THCCABO，包括：  

![1.png](https://image.3001.net/images/20200406/1586148432_5e8ab4501e11c.png!small)![2.png](https://image.3001.net/images/20200406/1586148432_5e8ab4503c91a.png!small)![3.png](https://image.3001.net/images/20200406/1586148432_5e8ab450343c4.png!small)asascpiex.dll前5个字节为空，然后会被0x00代替，其原始文件签名0x37
0x7A 0xBC 0xAF 0x27。CL_Debug_log.txt用于解压加密文档。  

![1.png](https://image.3001.net/images/20200406/1586162642_5e8aebd2d7055.png!small)恶意软件通过Windows
Management Instrumentation
（WMI）收集CPU、系统、操作系统版本、视频控制器和处理器的详细信息，通过cpuinfo确定受感染系统体系结构，针对64位系统会植入64.exe，该恶意软件目前仅支持64位环境。

![1.png](https://image.3001.net/images/20200406/1586163002_5e8aed3a8cfd1.png!small)它还检查系统是否启用了Microsoft
SmartScreen和Windows Defender，以及系统中是否运行了以下防病毒软件：  

![1.png](https://image.3001.net/images/20200406/1586163117_5e8aedadb8df9.png!small)![2.png](https://image.3001.net/images/20200406/1586163117_5e8aedadd22c8.png!small)收集到的信息会通过HTTP
GET 发送到hxxps://2no.co/1IRnc。

![1.png](https://image.3001.net/images/20200406/1586163211_5e8aee0b319e5.png!small)

CR_Debug_log.txt是7-Zip压缩文件，其中含有64.exe coinmine，会以helper.exe
coinminer复制到％appdata％\Roaming\Microsoft\Windows\，使用SystemCheck建立计划任务。  

![1.png](https://image.3001.net/images/20200406/1586163582_5e8aef7e3c65a.png!small)计划任务启动helper.exe后使用SystemCheck91137生成自身。  

![1.png](https://image.3001.net/images/20200406/1586163667_5e8aefd32ee30.png!small)为了逃避检测，helper.exe检查以下进：  

> aida64.exe
>
> AnVir.exe
>
> anvir64.exe
>
> GPU-Z.exe
>
> HWiNFO32.exe
>
> HWiNFO64.exe
>
> i7RealTempGT.exe
>
> OpenHardwareMonitor.exe
>
> pchunter64.exe
>
> perfmon.exe
>
> ProcessHacker.exe
>
> ProcessLasso.exe
>
> procexp.exe
>
> procexp64.exe
>
> RealTemp.exe
>
> RealTempGT.exe
>
> speedfan.exe
>
> SystemExplorer.exe
>
> taskmgr.exe
>
> VirusTotalUpload2.exe

生成Tor始进行挖矿  

![1.png](https://image.3001.net/images/20200406/1586163768_5e8af03811058.png!small)

## 建议

攻击者使用视频会议类工具传播恶意软件，建议用户从应用程序官方网站下载安装程序。用户应采用多层防护措施检测和阻止网络攻击。  

## IOCs

###  **URL**

> 2no(.)co/1IRnc
>
> hxxps://2no(.)co/1O5aW

### Hashes

![1.png](https://image.3001.net/images/20200406/1586163978_5e8af10a1dbc7.png!small)

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/zoomed-in-a-look-into-a-coinminer-bundled-with-zoom-installer/)，由Kriston编译，转载请注明来自FreeBuf.COM **  

