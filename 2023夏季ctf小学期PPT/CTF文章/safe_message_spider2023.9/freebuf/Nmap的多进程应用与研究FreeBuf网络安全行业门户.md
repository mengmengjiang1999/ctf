使用Nmap进行多目标多端口（强调端口数目较多，比如全端口）扫描时，其在执行时间上的表现并不好。本文旨在分析多目标多端口扫描时的速度瓶颈以及减少时间成本的解决方案。

## 实验

实验环境：

靶机

Debian01 10.0.2.2

Debian02 10.0.2.3

攻击机

Windows10 10.0.2.4

### 场景一

首先由攻击机对两台靶机分别进行扫描，耗时基本相同，为46.8秒

![image](https://image.3001.net/images/20210806/1628219447_610ca8376886540bb086f.png!small)

### 场景二

开启wireshark，并同时对两台靶机进行扫描，耗时96.82秒，大致为先前对某一台靶机进行扫描的两倍。

![image](https://image.3001.net/images/20210806/1628219466_610ca84a5f1f883ad0990.png!small)

其次根据wireshark的抓包情况，对于两个靶机Nmap是在并行扫描的。

![image](https://image.3001.net/images/20210806/1628219482_610ca85a63f9db8b51893.png!small)

### 场景三

开启两个终端，分别对两个靶机进行扫描，耗时与单个靶机扫描基本相同，为47.2秒。

![image](https://image.3001.net/images/20210806/1628219500_610ca86c1d9df6df3de97.png!small)

### 结果分析

结合上述三个场景，Nmap的扫描速度并非受限于网络资源而是受限于计算资源，但Nmap的参数中并没有给出多进程的选项。

## 解决方案

为此我编写了一个基于python-nmap和Nmap的通过多进程进行更快速的多目标多端口（比如全端口）扫描的脚本，github地址如下  
https://github.com/YC0806/MultiprocessNmapAutoScan

