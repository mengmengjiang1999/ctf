Schneider Electric EcoStruxure Control Expert（前称Unity Pro）是法国施耐德电气（Schneider
Electric）公司的一套用于Schneider
Electric逻辑控制器产品的编程软件。CVE-2020-28213漏洞存在于其中的PLC仿真器，该仿真器是EcoStruxure Control
Expert编程软件内置的一个有PLC仿真功能windows应用程序。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
## Part2 漏洞描述

EcoStruxure Control Expert上的 PLC 仿真器中存在没有完整性检查的代码下载漏洞，当通过 Modbus
发送特制请求时，该漏洞可能导致未经授权的命令执行。

‍漏洞名称| 施耐德PLC仿真器中的无约束代码执行漏洞  
---|---  
CVE编号| CVE-2020-28213  
漏洞类型| 远程代码执行  
漏洞等级| 8.8 高危  
影响范围| Schneider Electric EcoStruxure Control Expert version <= v14.1  
公开状态| 公开  
时间线| 2020-11-05 -分配CVE2020-11-08 -公开发布  
  
复现环境：

Windows 10

Schneider Electric EcoStruxure Control Expert v14.1

### Part3 漏洞复现

\- 安装Schneider Electric EcoStruxure Control Expert v14.1

\- 启动Control Expert 14.1

![v2-b27e8a6d08d7eafceee7608ca053ee16_720w.jpg](https://image.3001.net/images/20220825/1661404880_630706d0098b42318d584.jpg!small)

\- 新建项目(这里选择 BMX P32 2000 型号仿真器)：

![v2-03e1f2b8cbdd44fc1302302bda064c73_720w.jpg](https://image.3001.net/images/20220825/1661404880_630706d0e0db451aafd5b.jpg!small)

\- 新建一个变量：

![v2-6d305d2b3e55012d559a42cda9c7f6c0_720w.jpg](https://image.3001.net/images/20220825/1661404881_630706d19ce07f246da10.jpg!small)

新建一个程序段：

![v2-2684776fdeeffca597e0f76edba8c5b9_720w.jpg](https://image.3001.net/images/20220825/1661404882_630706d2600eb40f9e47c.jpg!small)![v2-587aee1d3c07f29158be62ddaf167499_720w.jpg](https://image.3001.net/images/20220825/1661404882_630706d2eb7dccb3e7f8e.jpg!small)

\- 写入一段ST赋值代码：

![v2-30535a64a1ac8948c79f567181b40a15_720w.jpg](https://image.3001.net/images/20220825/1661404883_630706d380707f6de0da4.jpg!small)

\- 使用 xdbg附加 ControlExpert 并在编译函数处下断点:

![v2-3e525fe7eb2b11aaa7f427d2a80612c6_720w.jpg](https://image.3001.net/images/20220825/1661404884_630706d41b735f250acbf.jpg!small)

\- 连接PLC 然后将项目传输到PLC：

![v2-5b56059991f3037c453bf393dd0bede4_720w.jpg](https://image.3001.net/images/20220825/1661404884_630706d4b3f3bf92b96d8.jpg!small)

\- Xdbg 暂停在断点处 单步执行一次：

![v2-c0467374b400a50c77306a39abbbf516_720w.jpg](https://image.3001.net/images/20220825/1661404885_630706d54bf6355f863c5.jpg!small)

\- 搜索特征码：

![v2-9f290a5377ccef4de6c36463e80b71e8_720w.jpg](https://image.3001.net/images/20220825/1661404885_630706d5c0ec73ffa63eb.jpg!small)

\- 双击过去反汇编查看：

![v2-3bc977deacc05034531d2fc0ecd6e59b_720w.jpg](https://image.3001.net/images/20220825/1661404886_630706d64324471e46b79.jpg!small)

可以看到对应研究者写的ST代码的汇编代码。这里替换字节码为研究者的测试代码后，让程序运行。- 提示上传信息完好：

![v2-46440550d781091588a8390690cb08fc_720w.jpg](https://image.3001.net/images/20220825/1661404886_630706d6e0ae013344769.jpg!small)

\- 启动PLC仿真器：

![v2-e5528199d280f0ef3623b483eb3535f4_720w.jpg](https://image.3001.net/images/20220825/1661404887_630706d76aa246a5849f9.jpg!small)

\- 弹出计算器，PLC仿真器异常：

![v2-39e8f9f6c52c4dc48e0d7b6daa3dda28_720w.jpg](https://image.3001.net/images/20220825/1661404887_630706d7f20fb9863549e.jpg!small)

 **复现成功！**

### Part4 漏洞细节

通过逆向手段，定位到编译PLC程序到PLC仿真器可执行的字节码的函数，再执行之后，修改原本编译好的字节码，程序会把测试字节码传输到PLC仿真器中，当操作PLC仿真器执行任务的时候，就会执行到测试代码。

## Part5 修复缓解建议

1\. 软件升级至v15.1版本。

2\. 监控网络流量，查看是否有恶意代码的流量特征。3. 安装主机卫士，设置IP白名单。

