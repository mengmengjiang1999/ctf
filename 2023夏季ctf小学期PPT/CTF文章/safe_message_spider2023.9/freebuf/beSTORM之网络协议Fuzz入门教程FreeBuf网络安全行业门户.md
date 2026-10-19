**本文将以SNMP协议为例介绍如何使用beSTORM进行网络协议Fuzz。**  

## 实验环境

Windows 7 X64 （IP：192.168.0.123）

beSTORM 3.7

被测机器：Centos （IP：192.168.0.120）

Perl 5

## 一、beSTORM架构简介

beSTORM的架构分为两个部分，一部分为Client，另一部分为Monitor。其中Client用于向被测程序发送畸形数据包；Monitor用于监控被测程序的状态，一旦发现被测程序出现异常立即记录下来，并发送给Client端，如下图所示。

![beSTORM架构_v2.png](https://image.3001.net/images/20180601/15278218894510.png!small)  

## 二、配置Monitor

通常在Windows环境下的对被测程序的监控使用GUI版本的Monitor，如下图所示。

![beSTROM_Monitor.png](https://image.3001.net/images/20180601/15278219245346.png!small)

在Linux环境下对被测程序的监控利用gdb调试工具，gdb可以在被测程序发生异常时通知beSTORM的Client端。beSTORM提供一个Perl脚本（gdb_monitor.pl文件），该脚本将gdb作为被测程序的调试器，并且将运行信息通过UDP发送给beSTORM的Client端。

首先在beSTORM的安装目录下找到gdb_monitor.pl文件。该脚本共有4个参数，分别是：（1）host，指定beSTORM
client的host。（2）port，指定beSTORM的client的UDP端口用于接收异常信息。（3）file，指定被测程序。（4）pid，指定需要附加进程的PID。

![gdb_monitor.pl_mosaic.png](https://image.3001.net/images/20180601/15278245043987.png!small)

本文对远程服务器的SNMP协议进行Fuzz，首先查看SNMP协议161端口对应的进程，如下图所示，对应进程的PID为4670。

![查看161端口对应的进程_mosaic.png](https://image.3001.net/images/20180601/15278235278987.png!small)

故pl脚本的执行命令如下：

    
    
    perl gdb_monitor.pl --host 192.168.0.123 --pid 4670

## 0x3 配置beSTORM

（1）向导步骤1。首先新建beSTORM的工程，向导第一步如下图所示。这里选择“Advanced”。

![beSTORM_Wizard_1.png](https://image.3001.net/images/20180601/15278220233033.png!small)  

（2）向导步骤2。注意在predefined modules中选择SNMP协议，Hostname or IP
address编辑框中填写被测服务器的IP地址192.168.0.120。

![beSTORM_Wizard_2.png](https://image.3001.net/images/20180601/15278220583553.png!small)  

（3）向导步骤3。

![Wizard_3.png](https://image.3001.net/images/20180601/15278221039571.png!small)  

选中“Run in batch
mode”（以批处理模式运行）复选框时，beSTORM发现首个错误后会继续运行。注意，在这种情况下，无论采用重新启动还是其他方法，都应从之前的错误中恢复被测程序。

选中“Make sure monitor is up before
starting”（确保开始前开启监控器）复选框时，beSTORM收到测试环境发出的约定信号后才会开始测试。这样，beSTORM就可确定测试环境是否运行正常。

选中“Report connectivity issues as
exceptions”（报告异常连接问题）复选框时，如果beSTORM无法接收测试环境发出的网络流量，即视为存在潜在问题或漏洞。这一功能会将所有网络问题识别为潜在漏洞，因此对于测试监控难度较大的环境（例如专用硬件设备）大有帮助。通过这种方式，beSTORM可以在后续的处理中轻松地发现同样的问题，并找出原因。

选中“Periodically test connection and report vulnerability upon
failure”（定期测试连接并在出现故障时报告漏洞）复选框时，beSTORM会测试被测程序的操作，并对于非正常流量做出回应。如果没有出现预期响应，beSTORM会生成异常报告。

（4）向导步骤4。在步骤4可以查看本工程中的已有配置，可以手动修改相关配置。

![beSTORM_Wizard_4.png](https://image.3001.net/images/20180601/15278221409351.png!small)  

（5）向导步骤5。SPS（Session per Second）即为每秒连接次数，请根据服务器性能设置。Host or IP
address需要填写Monitor的IP地址，一般情况下，Monitor的IP地址与被测目标程序所在IP地址是一致的。

![beSTORM_Wizard_5.png](https://image.3001.net/images/20180601/15278222026185.png!small)  

（6）向导步骤6。

![beSTORM_Wizard_6.png](https://image.3001.net/images/20180601/15278222401786.png!small)  

beSTORM Client运行界面如下图所示。

![beSTORM_Main_run.png](https://image.3001.net/images/20180601/15278222946517.png!small)

## 0x4 Fuzz测试

配置完毕后，可以查看的此次Fuzz测试的架构，如下图所示。

![beSTORM_Architecture_mosaic.png](https://image.3001.net/images/20180601/15278223158081.png!small)

当beSTORM
Client开始发送畸形数据包时，可以配置tcpdump抓取到beSTROM发送到161端口的畸形数据包，tcpdump抓取结果如下图所示，抓取命令为：tcpdump
–nn –i eth0 port 161。

![tcpdump_mosaic.png](https://image.3001.net/images/20180601/15278223316226.png!small)

此时可以坐等被测程序出现异常，Monitor可以检测到异常，并将异常发送给beSTORM Client。

ref: 《beSTORM - User Guide》

***本文作者：dolphin，转载请注明来自FreeBuf.COM**

