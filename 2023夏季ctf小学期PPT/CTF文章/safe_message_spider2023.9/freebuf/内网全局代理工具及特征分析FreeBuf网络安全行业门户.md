## 简介

**端口转发是点对点的方式，代理是点对面的方式，如果我们只需要访问主机的特定的端口，使用端口转发就够了，但通常在渗透进内网之后，我们还需要对整个内网进行横向渗透，这时代理必然是一个高校的方法。代理分为正向代理和反向代理，正向代理常适用于外网可以直接访问到web服务器的情况下，反向代理适用于服务器可以出网，但是外部无法直接访问服务器的情况，针对大型企业，现在几乎都是CDN，负载均衡等设备，所以个人认为现在反向代理更常见于渗透攻击中。**

## 一、 EW+Proifier

### 环境

攻击端（windows10）：172.16.110.150

靶机1（windows 2008 R2）：外网IP:192.168.254.132内网IP:192.168.1.1

靶机2（windows2008）： 内网IP：192.168.1.2

### 使用方法

反向代理使用方法（正向代理这儿不演示，反向代理应用更多些，因为反向代理主要适用于服务器无法从外部访问，但是服务器可以访问外部）：

1\. 通过shell上传一个对应版本的EW,这儿我上传了一个windows的

2\. 本地执行：ew_for_Win.exe -srcsocks -l “自定义端口1” -e“自定义端口2”

![](https://image.3001.net/images/20190712/1562921032_5d2848482c56d.png!small)

3\. Shell上执行：ew_for_Win.exe -s rssocks-d “接收端IP” -e “自定义端口2”

![](https://image.3001.net/images/20190712/1562921056_5d284860cc589.png!small)

![](https://image.3001.net/images/20190712/1562921066_5d28486a8b2b5.png!small)

![](https://image.3001.net/images/20190712/1562921070_5d28486e9a218.png!small)

4\. 配置Proifier

![](https://image.3001.net/images/20190712/1562921079_5d2848774bff0.png!small)

![](https://image.3001.net/images/20190712/1562921085_5d28487d489bd.png!small)

### 行为分析

配置好后对内网IP的一次访问：

![](https://image.3001.net/images/20190712/1562921094_5d28488622821.png!small)

可以看出如果使用ew进行内网的全局代理，如果攻击者使用的上传工具又经过加密，比如冰蝎这款shell管理工具，我们是无法通过流量回溯来发现上传代理工具，以及代理转发痕迹。

不过在靶机本地可以看到可疑进程：

![](https://image.3001.net/images/20190712/1562921173_5d2848d535826.png!small)

可疑网络连接：

![](https://image.3001.net/images/20190712/1562921179_5d2848db17439.png!small)

事件日志：

![](https://image.3001.net/images/20190712/1562921190_5d2848e618f82.png!small)

VirusTotal检查结果：

![](https://image.3001.net/images/20190712/1562921196_5d2848ec3102d.png!small)

### 总结

如果利用ew进行全局代理，配合加密得shell，通过流量回溯极难发现，通过服务器本地日志查看，进程查看，网络排查容易发现痕迹，且ew会被部分杀软查杀。

## 二、 Regeorg+Proifier

### 环境

攻击端（Win10）：192.168.223.1

靶机一（Win2008）：外网IP：192.168.223.128 内网IP：192.168.1.1

靶机二（windows ）：内网IP：192.168.1.2

### 使用方法

1\. 通过Shell上传对应的Tunnel脚本，访问：

![](https://image.3001.net/images/20190712/1562921223_5d28490740aee.png!small)

表你是脚本运行正常。

2\. 在本地运行reGeorgSocksProxy.py脚本：

Python reGeorgSocksProxy.py-p “自定义本地监听端口” -u “tunnel.jsp脚本url”

![](https://image.3001.net/images/20190712/1562921237_5d28491519af8.png!small)

运行成功，然后配置proifier，配置方法与第一个环境一样：

![](https://image.3001.net/images/20190712/1562921254_5d284926dea56.png!small)

行为分析

建立代理的流量：

![](https://image.3001.net/images/20190712/1562921266_5d2849320f1b1.png!small)

对内网WEB的一次访问：

![](https://image.3001.net/images/20190712/1562921274_5d28493a1db45.png!small)

![](https://image.3001.net/images/20190712/1562921281_5d2849419fed6.png!small)

通过流量可以看出，如果使用tunnel.jsp作为隧道，流量有明显跟隧道文件有关的特征，使用端口扫描工具对内网进行端口扫描：

![](https://image.3001.net/images/20190712/1562921293_5d28494d9acfa.png!small)

![](https://image.3001.net/images/20190712/1562921300_5d284954d889e.png!small)

可以看到代理特征还是调用tunnel隧道来进行内网渗透，查看http流量：

![](https://image.3001.net/images/20190712/1562921311_5d28495fdeeb4.png!small)

![](https://image.3001.net/images/20190712/1562921318_5d284966d1efe.png!small)

3389连接的特征：

![](https://image.3001.net/images/20190712/1562921325_5d28496da0b02.png!small)

![](https://image.3001.net/images/20190712/1562921330_5d28497216887.png!small)

传统的3389连接流量：

![](https://image.3001.net/images/20190712/1562921336_5d284978d8842.png!small)

用jmeter漏洞工具进行漏洞攻击(这里靶机IP自动更新到129了)：

![](https://image.3001.net/images/20190712/1562921343_5d28497ff1487.png!small)

追踪TCP流可以看到命令执行痕迹：

![](https://image.3001.net/images/20190712/1562921354_5d28498aa0ebc.png!small)

### 总结

利用regeorg+proifier方式来进行内网全局代理之后有明显的流量特征，但是流量中的行为不方便分析，流量行为主要是以流量隧道来进行攻击，我们能直观看见的是目的IP和目的端口，所以可以根据端口全球数量和频率可以大概分析攻击者行为，脚本会被部分杀软检测。

## 三、Abptts&SSH

### 使用方法

Abptts是一款基于python2.7的http加密隧道工具，Abptts能做的很多：

1\. 通过http加密隧道转发至目标内网下指定的单个TCP端口

2\. 通过http加密隧道同时转发至目标内网下的多台机器上的多个tcp端口

3\. 把ssh隧道包裹在http加密隧道中传递，对目标二级内网进行穿透

### 行为分析

单个端口转发：内网的80端口转发到本地的80端口，无流量产生，无痕迹可分析

### 环境

攻击端（windows）：192.168.114.1靶机一（windows）：外网IP：192.168.114.128内网IP：192.168.1.4靶机二（windows）：内网IP192.168.1.2

![](https://image.3001.net/images/20190712/1562921397_5d2849b52f1ee.png!small)

本地访问80端口，特征为大量对代理文件的请求，数据流加密了无法看出内容：

![](https://image.3001.net/images/20190712/1562921409_5d2849c181540.png!small)

![](https://image.3001.net/images/20190712/1562921422_5d2849ce6bf9e.png!small)

SSH动态转发：

攻击端（kali）：192.168.114.131

靶机一（CentOs）：192.168.114.132

SSH -D 本地端口 user@SshServerHost

Ssh协议采用了加密处理，无法对内容进行分析，ssh动态转发需要知道用户密码，所以使用具有一定前提条件，对服务器的last读取可以看到ssh登录痕迹，并且因为ssh动态转发是一个持续化的过程，所以只要转发进程没有结束，就会一直产生tcp&&ssh协议的流量。

![](https://image.3001.net/images/20190712/1562921451_5d2849ebbdf95.png!small)

Abptts+SSH动态转发：

攻击端（kali）：192.168.114.131

靶机（CentOs）:192.168.114.132

双加密的内网代理手法，繁琐了点，但是对蓝方人员更是无法分析行为：特征为频繁请求代理文件。

![](https://image.3001.net/images/20190712/1562921464_5d2849f82af58.png!small)

VirusTotal检查结果：惊奇发现居然免杀

![](https://image.3001.net/images/20190712/1562921477_5d284a05037a0.png!small)

### 总结

Abptts+SSH代理的优点是方便对多级内网进行代理，传输数据都采用了加密，免杀，不利于蓝方人员分析行为；缺点是结合SSH动态转发动静大，需要SSH账户密码。

 ***本文作者：kczwa1，转载请注明来自FreeBuf.COM**

