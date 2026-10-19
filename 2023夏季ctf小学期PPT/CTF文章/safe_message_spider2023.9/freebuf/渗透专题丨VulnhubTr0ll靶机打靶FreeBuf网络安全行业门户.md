首先安装好靶机，再打开Kali，使用ifconfig查看Kali IP信息，之后使用nmap进行扫描网段：

![](https://image.3001.net/images/20230707/1688720753_64a7d571973dfc3a87da7.png!small)

image-20230629200225568

经过排除主机IP和Kali IP，选择192.168.38.139，进行端口扫描：

![](https://image.3001.net/images/20230707/1688720754_64a7d5725cbe681be6b0b.png!small)

image-20230629201035695

接下来看一下80端口：

![](https://image.3001.net/images/20230707/1688720755_64a7d57304b3d7bc8ae51.png!small)

在源码中也查看不到任何信息，接下来扫描一下端口服务版本（全面系统检测）：

![](https://image.3001.net/images/20230707/1688720756_64a7d5741e2f6dbedc86a.png!small)

可以看到这里允许匿名登录，接下来登录：

![](https://image.3001.net/images/20230707/1688720757_64a7d575840a8638b4b89.png!small)

登录成功，使用ls查看文件，发现和端口扫描结果一致，有个流量包，下载下来：

![](https://image.3001.net/images/20230707/1688720758_64a7d5760efe85fc90fca.png!small)

下载下来之后，通过wireshark进行分析：

![](https://image.3001.net/images/20230707/1688720758_64a7d576a5b72a8267992.png!small)

追踪一个TCP流，然后根据顺序在过滤器中查找，找到如下：

![](https://image.3001.net/images/20230707/1688720759_64a7d5778b2431a23ba86.png!small)

根据提示，访问网址路径，下载下来这个文件，进行分析：

![](https://image.3001.net/images/20230707/1688720760_64a7d5784a2b80b20c1ef.png!small)

![](https://image.3001.net/images/20230707/1688720760_64a7d578e2c549c87b148.png!small)

可以看到这是一个ELF 32位可执行文件，直接在IDA中进行分析：

![](https://image.3001.net/images/20230707/1688720761_64a7d579876314f66eaa3.png!small)

只打印了一句话，继续找地址0x0856BF：

![](https://image.3001.net/images/20230707/1688720762_64a7d57a55c0e3121ec02.png!small)

接下来就可以在目录中找到如下信息：

![](https://image.3001.net/images/20230707/1688720762_64a7d57af33d22c527c59.png!small)

maleus  
ps-aux  
felux  
Eagle11  
genphlux < \-- Definitely not this one  
usmc8892  
blawrg  
wytshadow  
vis1t0r  
overflow  
  
Good_job_:)

![](https://image.3001.net/images/20230707/1688720763_64a7d57ba9b509fe76ce1.png!small)

完事记录下用户名到一个文件之后，使用hydra进行爆破：

![](https://image.3001.net/images/20230707/1688720764_64a7d57c3ab8a06eaf783.png!small)

密码不正确，是文件名Pass.txt,不是Good_job_:)。之后通过远程ssh连接，因为权限问题，在临时目录temp下查看uname：

![](https://image.3001.net/images/20230707/1688720764_64a7d57cd3f0eac5c373e.png!small)

Linux troll 3.13.0-32-generic #57-Ubuntu SMP Tue Jul 15 03:51:12 UTC 2014 i686
i686 i686 GNU/Linux

随后通过系统版本找到相对应的漏洞，从而进行提权操作。

![](https://image.3001.net/images/20230707/1688720765_64a7d57d79875c597c2ea.png!small)

选第一条，下载下来，拷贝到靶机tmp目录下，通过gcc生成，进而运行，成功获取到root权限。

![](https://image.3001.net/images/20230707/1688720766_64a7d57e2ec3c8c5ae8b1.png!small)​

这样就获得了flag。

