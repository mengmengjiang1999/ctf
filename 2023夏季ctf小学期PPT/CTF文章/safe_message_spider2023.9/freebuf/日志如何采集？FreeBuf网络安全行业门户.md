日志是人类关于日常生活的一个记录，也是机器运作时对于事件发生的报告。关于网络设备、系统及服务程序等，在运作时都会产生一个叫log的事件记录；每一行日志都记载着日期、时间、使用者及动作等相关操作的描述。当遇到安全攻击事件时，日志能协助进行安全事件还原，能尽快找到事件发生的时间、原因等，通过大量不同安全设备的联动，日志可以关联分析监测真正有威胁的攻击行为，还原出真实的攻击情况。日志可以反应出很多的安全攻击行为，比如登录错误，异常访问等。日志还能告诉你很多关于网络中所发生事件的信息，包括性能信息、故障检测和入侵检测。日志会成为在事故发生后查明“发生了什么”的一个很好的“取证”信息来源。所以日志采集非常必要。

##  **一、概述**

一般系统日志分为三大类：用户行为日志、业务变更日志、系统运行日志。日志文件能够详细记录系统每天发生的各种各样的事件，对设备安全、网络安全等起着非常的重要作用。所以，对与常见的日志的采集，如何更加方便的进行查看。当可以统一查看相关日志时，可以节省大量时间。Windows、linux、交换机作为常见的系统资产，其日志包含的价值信息较多，如何高效无误地采集到这些资产的日志。

## 二、 **常见的日志采集方法**

### 1.Windows日志采集方法及工具

 **一、通过Nxlog采集windows日志**
1、环境准备Windows服务器（windows10）Linux服务器（centos7）Elasticsearch2、环境搭建步骤1）在Windows上安装Nxlog，一直Next即可。

![1628836116_61161114d7f670b360a6d.png!small?1628836117411](https://image.3001.net/images/20210813/1628836116_61161114d7f670b360a6d.png!small?1628836117411)

补充：Nxlog默认是安装在C:\Program Files (x86)\nxlog目录中。2）在Linux上安装Fluentdcurl -L
https://toolbelt.treasuredata.com/sh/install-redhat-td-agent3.sh | sh

![1628836127_6116111f19f9669e21d91.png!small?1628836127637](https://image.3001.net/images/20210813/1628836127_6116111f19f9669e21d91.png!small?1628836127637)

![1628836132_61161124554eee246f56a.png!small?1628836132979](https://image.3001.net/images/20210813/1628836132_61161124554eee246f56a.png!small?1628836132979)

3）修改配置文件Nxlog默认配置文件位置为：C:\Program Files\nxlog\conf\nxlog.conftd-agent配置文件/etc/td-agent/td-agent.conf

![1628836139_6116112bb7f870816f10f.png!small?1628836140244](https://image.3001.net/images/20210813/1628836139_6116112bb7f870816f10f.png!small?1628836140244)

3、启动服务

1）启动Linux上的td-agent2）启动Windows上的nxlog

4、查看log文件

![1628836148_6116113402b0c082e6914.png!small?1628836148492](https://image.3001.net/images/20210813/1628836148_6116113402b0c082e6914.png!small?1628836148492)

已经可以接收到相关日志比如当系统中创建新用户时，可以看到有相关日志产生

    
    
    1 2020-11-10T17:31:18.953475+08:00 WIN-BUBQGGIFSJB.server.com Microsoft-Windows-Security-Auditing 484 - [seci-win-2008 Keywords="-9214364837600034816" EventType="AUDIT_SUCCESS" EventID="4720" ProviderGuid="{54849625-5478-4994-A5BA-3E3B0328C30D}" Version="0" Task="13824" OpcodeValue="0" RecordNumber="4858" ThreadID="3140" Channel="Security" Category="用户帐户管理" Opcode="信息" TargetUserName="admin" TargetDomainName="SERVER" TargetSid="S-1-5-21-3732349250-2750458932-4192379908-1119" SubjectUserSid="S-1-5-21-3732349250-2750458932-4192379908-1116" SubjectUserName="test" SubjectDomainName="SERVER" SubjectLogonId="0x13439b1" PrivilegeList="-" SamAccountName="admin" DisyName="%%1793" UserPrincipalName="-" HomeDirectory="%%1793" HomePath="%%1793" ScriptPath="%%1793" ProfilePath="%%1793" UserWorkstations="%%1793" PasswordLastSet="%%1794" AccountExpires="%%1794" PrimaryGroupId="513" AllowedToDelegateTo="-" OldUacValue="0x0" NewUacValue="0x15" UserAccountControl=" %%2080 %%2082 %%2084" UserParameters="%%1792" SidHistory="-" LogonHours="%%1793" EventReceivedTime="2020-11-10 17:31:21" SourceModuleName="in" SourceModuleType="im_msvistalog"]

可以通过日志看出，在2020年11月9日，下午四点十六分创建了一个账户名为admin的账号。 **二、通过winlogbeat收集日志**
1、环境准备Windows服务器（windows2008r2）Linux服务器（centos7）Elasticsearch2、环境搭建步骤1）windows上安装winlogbeat下载地址：https://www.elastic.co/cn/downloads/beats/winlogbeat解压到C:\Program
Files2）使用powershell安装进入到winlogbeat目录

![1628836212_611611745cda3ea6f4be1.png!small?1628836212879](https://image.3001.net/images/20210813/1628836212_611611745cda3ea6f4be1.png!small?1628836212879)

安装winlogbeat

![1628836219_6116117b8c8d5d533bcb1.png!small?1628836220096](https://image.3001.net/images/20210813/1628836219_6116117b8c8d5d533bcb1.png!small?1628836220096)

如果在系统上禁用了脚本执行，则需要为当前会话设置执行策略以允许脚本运行。PowerShell.exe -ExecutionPolicy
UnRestricted -File .\install-service-winlogbeat.ps1。3）修改配置文件本文测试使用winlogbeat收集日志，发送到elasticsearch修改配置文件
：winlogbeat.yml填写要输出到es的地址output.elasticsearch:hosts:-localhost:92003、启动服务Start-Service
winlogbeat4、查看日志打开kibana，或者es的head插件，可以看到，日志会按照默认的index winlogbeat- +
日期，来收录到es中。

### 2.Linux日志采集方法及工具

 **一、通过Rsyslog采集**
1、环境准备两台Linux主机（centos7）接收方IP：192.168.1.168发送方IP：192.168.1.1912、环境搭建1）安装Rsyslogyum
install -y rsyslog

![1628836330_611611ea8a1d8bee970fd.png!small?1628836331152](https://image.3001.net/images/20210813/1628836330_611611ea8a1d8bee970fd.png!small?1628836331152)

两台主机都安装完成2）配置rsyslog.conf文件注：修改前建议备份一下配置文件cp /etc/rsyslog.conf
/etc/rsyslog.conf.bak接收方主机配置文件：Vim /etc/rsyslog.conf

![1628836344_611611f8c40acdd535f2c.png!small?1628836345386](https://image.3001.net/images/20210813/1628836344_611611f8c40acdd535f2c.png!small?1628836345386)

![1628836348_611611fcc03421d396afc.png!small?1628836349272](https://image.3001.net/images/20210813/1628836348_611611fcc03421d396afc.png!small?1628836349272)

发送方配置文件：Vim /etc/rsyslog.conf

![1628836354_61161202f2a6fd93a5f03.png!small?1628836355498](https://image.3001.net/images/20210813/1628836354_61161202f2a6fd93a5f03.png!small?1628836355498)

3、启动服务修改完配置文件后，重启rsyslogSystemctl restart
rsyslog4、查看日志在/var/log/devicelog/下可以发现产生日志文件分别记录了本机的日志文件和采集方主机的日志文件

![1628836378_6116121a1690ee912e167.png!small?1628836378555](https://image.3001.net/images/20210813/1628836378_6116121a1690ee912e167.png!small?1628836378555)

![1628836381_6116121d0ae68a19f9a01.png!small?1628836381531](https://image.3001.net/images/20210813/1628836381_6116121d0ae68a19f9a01.png!small?1628836381531)

![1628836384_611612200a5d2f797cf69.png!small?1628836384700](https://image.3001.net/images/20210813/1628836384_611612200a5d2f797cf69.png!small?1628836384700)

![1628836387_6116122351e11667ad54f.png!small?1628836387910](https://image.3001.net/images/20210813/1628836387_6116122351e11667ad54f.png!small?1628836387910)

当系统中新建账号时，产生如下日志

    
    
    Nov 17 15:17:10 secisland2 useradd[21830]: new user: name=esuser, UID=1001, GID=1001, home=/home/esuser, shell=/bin/bash

可以根据日志分出：在11月17号下午三点十七分，新建了一个账号名为esuser的账号。

### 3.交换机常用的日志采集方法

1、环境准备Linux主机（centos7系统）系统已配置好Rsyslog2、交换机配置 **思科交换机**

    
    
    # config terminal(config)# logging on(config)# logging <10.x.x.x>           ## 注意syslog日志服务器接收地址，根据实际情况修改。(config)# logging facility local7      ## 将记录事件类型定义为local7。(config)# logging trap notifications   ## 将记录事件严重级别定义为从notifications

开始，一直到最紧急级别的事件全部记录到前边指定的syslog server。 **华为交换机**

    
    
    huawei switch：#指定发送消息基本，表示从0-7都发送info-center source default channel 2 log level debugging#指定从哪个接口发送info-center loghost source Vlanif1#指定远程syslog服务器ipinfo-center loghost x.x.x.x例如tail -f /var/log/switch01.logMay  5 16:17:27 switch01 %%01SHELL/6/DIS_CMDRECORD(s)[1]: Recorded dis command information. (Task=VT0, Ip=x.x.x.x, VpnName=, User=**, AuthenticationMethod="Password", Command="dis info-center statistics")

可以看出在五月五号的下午四点十七分，执行了disinfo-center statistics命令。

## 三、 **小结**

本文介绍了一些简单的日志采集方法，以及使用到的工具。当然还有一些比较更加完善的采集方式，例如：利用filebeat采集日志，然后发送到消息队列kafka，然后logstash去获取，利用filter功能过滤格式，然后存储到elasticsearch中，最后通过kibana展示。还比如通过日志采集框架Flume等等。在这个大数据时代，它们的重要性是不言而喻的。后续我们将从日志过滤归并角度探讨如何提高日志存储效率，减少不必要的冗余信息采集，不是所有的日志都适合采集，对业务、运维、安全等分析场景无价值的日志需要被过滤归并处理。

