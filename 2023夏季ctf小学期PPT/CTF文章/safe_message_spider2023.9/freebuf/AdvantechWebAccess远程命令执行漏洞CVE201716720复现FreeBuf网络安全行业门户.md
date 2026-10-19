Advantech
WebAccess是中国台湾研华（Advantech）公司的一套基于浏览器架构的HMI/SCADA软件，该软件支持动态图形显示和实时数据控制，并提供远程控制和管理自动化设备的功能。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 未知  
  
Part2漏洞描述Advantech WebAccess
8.3.2版本及之前版本中存在未经身份验证的远程代码执行漏洞，该漏洞具体存在于webvrpcs进程中0x2711
IOCTL的实现中，由于在文件操作中使用用户提供的路径之前，没有对它进行适当的验证，导致攻击者可以利用此漏洞使用RPC协议通过TCP端口4592以Administrator执行远程命令。

![v2-8cb63da2161a05c093f5a629fe20dba3_720w.jpg](https://image.3001.net/images/20220913/1663048388_63201ac48910a952d4a8c.jpg!small)‍漏洞名称|
Advantech WebAccess远程命令执行漏洞  
---|---  
CVE编号| CVE-2017-16720  
漏洞类型| 远程命令执行  
漏洞等级| 9.3 高危  
公开状态| 公开  
时间线| 2017.11.09 CVE分配  
  
## Part3 漏洞复现

 **1\. 实验环境** 渗透主机：Win10 (192.168.33.1)目标主机：Win7
64(192.168.33.140)软件版本：Advantech WebAccess 8.2

 **2\. 涉及工具** Python 2.7

 **3\. 复现步骤**

1) 启动环境，目标主机启动,如下图：

![v2-33fcb50174eeac1cd17ae4c8cb543aab_720w.jpg](https://image.3001.net/images/20220913/1663048389_63201ac529d8a01ea1e15.jpg!small)

查看端口开放情况，确认4592端口已开启，如下图所示：

![v2-1e8b18839aab6b423ce6242a034c2b62_720w.jpg](https://image.3001.net/images/20220913/1663048389_63201ac5d62fefec17277.jpg!small)

2）攻击者使用渗透主机中的Python 2.7 执行CVE-2017-16720 POC脚本（[https://www.exploit-db.com/exploits/44278](https://link.zhihu.com/?target=https%3A//www.exploit-db.com/exploits/44278)），对目标主机进行攻击，可以发现目标主机中的Calc.exe成功运行 ，如下图所示：

![v2-49242fa350237503588b605c650e3775_720w.jpg](https://image.3001.net/images/20220913/1663048390_63201ac695ea719435f68.jpg!small)

## Part4 漏洞分析

打开drawsrv.dll并定位到函数DsDaqWebService，DsDaqWebService函数实现了各个不同IOCTL
code的功能，如下图所示：

![v2-4ad29df5245aa074e20ad71ff9c1a863_720w.jpg](https://image.3001.net/images/20220913/1663048391_63201ac74ec79b207cbec.jpg!small)

而0x2711对应的处理函数为sub_100017B0。分析sub_100017B0，该函数中调用了CreateProcessA()函数创建进程。其中lpCommandLine参数由RPC客户端发送，且此处未对此参数进行任何检查。因此，可以通过控制该参数使得CreateProcessA()执行任意命令，从而导致远程命令执行。

![v2-04b8276d70157bce5d34b7329714101c_720w.jpg](https://image.3001.net/images/20220913/1663048391_63201ac7ecd1074680619.jpg!small)

## Part5 修复建议

升级到研华WebAccess 8.3.3或更高版本。

