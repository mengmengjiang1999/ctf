MMSLite是美国SISCO公司开发的一种基于变电站网络通信IEC61850标准的通讯组件开发库,主要用于智能电子设备(Intelligent
ElectronicDevices)如远程终端单元RTU,自动继电器,可编程逻辑控制器PLC等。

 **Part1 漏洞状态**

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
 **Part2 漏洞描述**

SISCO MMS协议某字段存在拒绝服务漏洞。向采用SISCO MMS Lite套件开发的设备发送MMS-Write服务中某个字段Length值为0的畸形报文后，可导致设备MMS模块崩溃，MMS协议对应102端口无法连通。

影响版本: SISCO MMS Lite协议套件 v5.0

漏洞名称| SISCO MMS协议某字段存在拒绝服务漏洞  
---|---  
CNVD编号| CNVD-2019-05652  
漏洞类型| 通用型漏洞  
漏洞等级| 低危6.5中危（Medium）  
公开状态| 公开  
  
 **Part3 复现环境**

Windows 10 + Python3

四方CSI-200EA测量控制装置

![v2-4853e4aed10632bd6454479bd3d430d7_720w.jpg](https://image.3001.net/images/20220408/1649396672_624fcbc00677e9037aeed.jpg!small)

IED Explorer IEC 61850 客户端调试工具

![v2-58761af862087b57b67d6a7954d8c58e_720w.jpg](https://image.3001.net/images/20220408/1649396672_624fcbc05c09ec589ed18.jpg!small)

 **Part4 漏洞复现**

1.构建POC

![v2-72258939b919d7eddc7d3bf8cbf0b66a_720w.jpg](https://image.3001.net/images/20220408/1649396672_624fcbc0a86acd8dd2f25.jpg!small)

2.运行POC 观察现象

![v2-df4eaa5c92392a14a56ae890d3825ff8_720w.jpg](https://image.3001.net/images/20220408/1649396673_624fcbc11bac09329227c.jpg!small)

3.无法ping通

![v2-8a6eb71a60aafb38a7f8ab9567a23171_720w.jpg](https://image.3001.net/images/20220408/1649396673_624fcbc1635cbffc8325b.jpg!small)

4\. MMS服务端口102连接不上

![v2-abc4ee035ee5407ec0a6745a9177cfa1_720w.jpg](https://image.3001.net/images/20220408/1649396673_624fcbc1ad5d99af94d20.jpg!small)

5.Wireshark抓包观察到攻击目标未响应

![v2-86c72f6fd3d69fa4b70809685cc85b61_720w.jpg](https://image.3001.net/images/20220408/1649396674_624fcbc2098f1f8ee4306.jpg!small)

 **Part5 修复建议**

更新补丁：[https://sisconet.com/our-products/mms-lite/](https://link.zhihu.com/?target=https%3A//sisconet.com/our-products/mms-lite/)

 **获取更多情报**

联系我们，获取更多漏洞情报详情及处置建议，让企业远离漏洞威胁。  
电话：18511745601

邮箱：shiliangang@andisec.com

