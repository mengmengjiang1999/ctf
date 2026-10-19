Schneider Electric Interactive Graphical SCADA System（IGSS）是法国施耐德电气（Schneider
Electric）公司的一套用于监控和控制工业过程的SCADA（数据采集与监控系统）系统。

### Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
### Part2 漏洞描述

未经身份验证的远程攻击者可以通过多种途径强制 IGSSdataServer.exe
分配大量内存来存储攻击者控制的数据。攻击者可以提供少量数据来导致缓冲区过度读取情况，从而产生内存读取访问冲突，这是由 IGSSdataServer.exe
中实现的异常处理程序处理的。但是，异常处理程序不会释放攻击者分配的内存，攻击者可以反复向 IGSSdataServer.exe
发送特制消息以耗尽其内存，从而可能导致拒绝服务。

‍漏洞名称| IGSS内存泄露导致的拒绝服务  
---|---  
CVE编号| CVE-2022-24314  
漏洞类型| 缓冲区错误  
漏洞等级| 高危（7.5）  
受影响的产品| SchneiderElectricInteractive Graphical SCADA System (IGSS) Definition
<=15.0.0.22021  
公开状态| 公开  
时间线| 发布时间:2022-02-09  
  
### Part3 漏洞复现

 **1．实验环境** 渗透主机：kail靶机环境：win10软件版本：IGSS v15.0

 **2．涉及工具** X64dbgPython2

 **3．漏洞复现** 1）在靶机中运行IGSS

![v2-fd0f87e792ec7a0edf967546c7c6056c_720w.jpg](https://image.3001.net/images/20220825/1661404315_6307049b1d58ccea8e77a.jpg!small)

点击开始，如下图所示：

![v2-3c3f13e2586eec8bf2508f0743efd237_720w.jpg](https://image.3001.net/images/20220825/1661404315_6307049bba5018ef3dbc5.jpg!small)

2）POC 验证:python igss_dataserver_memleak.py -t 192.168.0.104 -p 12401 -v

![v2-4b2ac1f33a67138ee651f75441371405_720w.jpg](https://image.3001.net/images/20220825/1661404316_6307049c5851ee5ea35c0.jpg!small)

3）查看结果，查看：

IGSS Master -> Runtime and Diagnostics ->
详细状态中的数据服务器内存使用情况，查看IGSSdataServer.exe服务器日志：FetchControl_RMS::appendRequest，内存不足。

![动图封面](https://image.3001.net/images/20220825/1661404317_6307049d02c6d911444ae.jpg!small)

![v2-b3df274b0be448b65d1336f7d57f9589_720w.jpg](https://image.3001.net/images/20220825/1661404317_6307049dc987c9524d5d0.jpg!small)

停止 POC 后，内存也未释放：

![v2-0bc79d5500ff4e6f1496abfc9f4e5418_720w.jpg](https://image.3001.net/images/20220825/1661404318_6307049eac12186179698.jpg!small)![v2-7e8e8901806cc9ab623f2a1c6a45a3d3_720w.jpg](https://image.3001.net/images/20220825/1661404319_6307049f3068b60a23e0d.jpg!small)

### Part4 漏洞分析

使用x64dbg 附加进程调试：

![v2-d03b5891d8a12b2ebc86540aa038c0cd_720w.jpg](https://image.3001.net/images/20220825/1661404319_6307049fc4b99cf10f63d.jpg!small)

分析此段代码大致流程为：

1）接受攻击者发送的数据判断是否分配内存：

![v2-5495b182ba591dd007ed8bcd0d494a91_720w.jpg](https://image.3001.net/images/20220825/1661404320_630704a08097369b3a5cc.jpg!small)

  

接收的数据和发送的数据一致：

![v2-965b734ff9ef23e66be8e7411f28b208_720w.jpg](https://image.3001.net/images/20220825/1661404321_630704a128c0b5e42b990.jpg!small)

2） 内存分配：

分配的大小结合POC 分析为：0x4000000

![v2-0eff6cc1eb04a525c767599978ca7e20_720w.jpg](https://image.3001.net/images/20220825/1661404321_630704a1d897a3a236a71.jpg!small)![v2-1ba65448b1589d32deae69d411abcbef_720w.jpg](https://image.3001.net/images/20220825/1661404322_630704a265f0a50a932fe.jpg!small)

3）判断内存是否分配成功，成功则调用memcpy，触发异常：分配大量内存来存储攻击者控制的数据。攻击者可以提供少量数据来导致缓冲区过度读取情况，从而产生内存读取访问冲突。

![v2-b360c423ab6c4f0b388cd755a5cd3698_720w.jpg](https://image.3001.net/images/20220825/1661404323_630704a313749e4ec11e9.jpg!small)![v2-a0a4ee85bb70b1132a9347b479866b08_720w.jpg](https://image.3001.net/images/20220825/1661404323_630704a38cbd328cd7d4c.jpg!small)

4） 分配失败则调用错误处理输出日志:

FetchControl_RMS::appendRequest，内存不足。

![v2-6028029ce5e7fe1258c052fa648569b6_720w.jpg](https://image.3001.net/images/20220825/1661404324_630704a4175e05a15feb6.jpg!small)

5）结合POC 分析：

攻击者可以反复连接IGSSdataServer.exe 发送特制消息，分配内存，断开socket连接后IGSSdataServer.exe
也未进行内存释放，导致耗尽其内存，从而可能导致拒绝服务。

![v2-44befe84eb54a9d90749bfdb9bf25457_720w.jpg](https://image.3001.net/images/20220825/1661404324_630704a4b008dea74c398.jpg!small)

### Part5 修复建议

更新到 IGSS 数据服务器版本 15.0.0.22021 或更高版本。

