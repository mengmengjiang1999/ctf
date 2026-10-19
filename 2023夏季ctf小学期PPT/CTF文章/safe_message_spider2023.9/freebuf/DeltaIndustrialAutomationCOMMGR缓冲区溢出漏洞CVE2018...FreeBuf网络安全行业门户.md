台达电子（Delta
Electronics）成立于1971年4月，总部位于台北市，是交换式电源供应器与直流风扇产品的全球领导厂商，主要产品包括电源管理的整体解决方案、视讯显像系统、工业自动化、网络通讯产品、太阳能、LED照明与电动车控制系统及整车动力系统等。DeltaIndustrial
Automation
COMMGR是台达电子公司的一套通信管理软件，其主要的功能在于扮演台达软件与硬件之间的通讯桥梁，通过COMMGR的管理，使联机的工作更为便利也更有效率。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
## Part2 漏洞描述

Delta Industrial Automation COMMGR
1.08及之前版本中存在缓冲区溢出漏洞，原因为COMMGR.exe在调用recv时没有判断字符串长度，直接向栈中写入超过原本长度限制的数据，其结果可导致远程攻击者可利用该漏洞执行任意代码或造成应用程序拒绝服务。

漏洞名称| Delta Electronics Delta Industrial Automation COMMGR缓冲区溢出漏洞  
---|---  
CVE编号| CVE-2018-10594  
漏洞类型| 缓冲区溢出漏洞  
漏洞等级| 7.5 高危  
公开状态| 公开  
受影响产品| Delta Electronics Delta IndustrialAutomation COMMGR <=1.08Delta
Electronics Delta IndustrialAutomation COMMGR AHSIM_5x0Delta Electronics Delta
IndustrialAutomation COMMGR AHSIM_5x1Delta Electronics Delta
IndustrialAutomation COMMGR D-V--PSimulator EH2Delta Electronics Delta
IndustrialAutomation COMMGR D-V-P-Simulator EH3Delta Electronics Delta
IndustrialAutomation COMMGR D-V-P-Simulator ES2Delta Electronics Delta
IndustrialAutomation COMMGR D-V-P-Simulator SEDelta ElectronicsDelta
Industrial Automation COMMGR D-V-P-Simulator SS2  
时间线| 2018.05.01– 分配CVEID  
  
## Part3 漏洞复现

 **1\. 实验环境** 渗透主机：win10 (192.168.33.1)靶机环境：win xp
sp3(192.168.33.220)软件版本：COMMGR 1.08

 **2.涉及工具** OllyDbgPython3

 **3.漏洞复现**

1）构造POC，其中shellcode为弹出计算器脚本，如下图所示：

  

![v2-cfbaf84572460e2793b13c8911283f7e_720w.jpg](https://image.3001.net/images/20220512/1652352538_627ce61a76ebc6a211a1b.jpg!small)

2）靶机环境搭建

打开 Delta Industrial Automation COMMGR 1.08，如下图所示：

![v2-eae78ecf56ea8af1785811b44b735660_720w.jpg](https://image.3001.net/images/20220512/1652352538_627ce61ade044991d0976.jpg!small)

双击，托盘图标，点击开启，确认502端口开启，如下图所示：

![v2-25a6b21cd9f3248251df84f72fdd9f71_720w.jpg](https://image.3001.net/images/20220512/1652352539_627ce61b4c36f91ed734a.jpg!small)

3）攻击者通过渗透主机执行命令：python3 .\COMMGR_dos_2.py。

4）查看结果，发现成功执行shellcode弹出计算器，如下图所示：

![v2-28c28296281769129e4ccfcbae55ae8d_720w.jpg](https://image.3001.net/images/20220512/1652352539_627ce61b9640faa8e1af9.jpg!small)

## Part4 漏洞分析

OllyDbg查找调用recv的地方，发现只有一处调用在0x66437B，在该位置下断点，发现可以断下来。

![v2-eff078f7ed137f4eb0c9d76403afda24_720w.jpg](https://image.3001.net/images/20220512/1652352540_627ce61c033c9b9eb72ed.jpg!small)

然后发现接收数据包的地址0x12ECF0 在堆栈上，数据长度就是我们发送的长度。

![v2-819267c9519d3e06b11eb27ec4ed6f2f_720w.jpg](https://image.3001.net/images/20220512/1652352540_627ce61c5147fed874c75.jpg!small)

返回到调用这个流程的函数。

![v2-2fc1df3f5e7ead705a5b4455a4dfbdb4_720w.jpg](https://image.3001.net/images/20220512/1652352540_627ce61c9e1921ebf137e.jpg!small)

我们返回到0x4108A8的位置，也就是上一句 0x4108A3 调用的接收数据，查看堆栈上数据。

![v2-89d7c7e11916612341345190bc5fc93b_720w.jpg](https://image.3001.net/images/20220512/1652352540_627ce61cdd3a21679cce4.jpg!small)

发现就是我们发送的测试数据。

## 总结：

通过分析发现漏洞产生的具体原因为COMMGR.exe在调用recv时没有判断字字符串长度，直接将接收到的字符串复制到4208字符的栈空间中，导致溢出。

## Part5 修复建议

据厂商提供的信息，COMMGR v1.09 (或以上)版本已修复缺陷，建议用户从以下地址下载新版本使用：

http://www.delta-china.com.cn/services/DownloadCenter2.aspx?secID=8&pid=2&tid=0&CID=06&itemID=060301&typeID=1&downloadID=,&title=--%20%E8%AB%8B%E9%81%B8%E6%93%87%20--&dataType=8;✓=1&hl=zh-CN

