**Part1 漏洞状态**

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
 **Part2 实验描述**

Siemens S7 Layer 2 - Denial of Service (DoS)该攻击是由伪造PLC Mac
地址,在网络中发送以太二层广播包，导致该PLC网络阻塞影响正常业务。

 **Part3 受影响版本**

Version: 4.5

 **Part4 实验环境**

PLC: S7-1200

ISF: (Industrial Security Exploitation Framework)

![v2-f4cb9a4d0085d2af6dc8d766818505b6_720w.jpg](https://image.3001.net/images/20220304/1646362163_62217e33c17dac0af4cc1.jpg!small)

 **Part5 实验复现**

使用ISF扫描设备

![v2-2eebdbaf2650a98248c622b53d8ca0aa_720w.jpg](https://image.3001.net/images/20220304/1646362164_62217e34204fc742866a6.jpg!small)

攻击之前先和PLC正常通讯

![v2-0091ddaaadb5b6cdf403d8f8e80dba0a_720w.jpg](https://image.3001.net/images/20220304/1646362164_62217e346cfc092ee3c7e.jpg!small)

运行POC

![v2-864a5704a6d715dbb1eaa393f1711014_720w.jpg](https://image.3001.net/images/20220304/1646362165_62217e350ad83cf467b9b.jpg!small)![v2-e3a4bf7b08b9f46a7df555b1581fd3f9_720w.jpg](https://image.3001.net/images/20220304/1646362165_62217e3549e26cc6df7f7.jpg!small)

此时观察到PLC 网络丢包延迟

![v2-b2b12ec5de21f7775c8fb00d0de300b6_720w.jpg](https://image.3001.net/images/20220304/1646362165_62217e359214bd35d79a5.jpg!small)

另外一台PLC正常

![v2-e859abfb9c0c0e62b53949994beeeaa2_720w.jpg](https://image.3001.net/images/20220304/1646362165_62217e35e1020a4a85e17.jpg!small)

停止攻击后也无法马上恢复

![v2-f7354d9e93d49ac41531a653f31c3f2f_720w.jpg](https://image.3001.net/images/20220304/1646362166_62217e364494e0d00d534.jpg!small)

分析网络流量发现大量的ICMP Request请求,并无Response回复

![v2-a442205cf7678c18b4a34e9931977cca_720w.jpg](https://image.3001.net/images/20220304/1646362166_62217e368554497dbdb99.jpg!small)

 **Part6 细节分析**

关键POC分析：

![v2-802d5d1bebc0be8fc4748ebe64bdd13e_720w.jpg](https://image.3001.net/images/20220304/1646362166_62217e36c7fa8f437a3f7.jpg!small)

该攻击为伪造该PLC Mac 地址发送二层Ether广播包造成的

Part7修复建议

交换机Mac地址绑定

交换机隔绝广播风暴

 **获取更多情报**

联系我们，获取更多漏洞情报详情及处置建议，让企业远离漏洞威胁。  
电话：18511745601

邮箱：shiliangang@andisec.com

