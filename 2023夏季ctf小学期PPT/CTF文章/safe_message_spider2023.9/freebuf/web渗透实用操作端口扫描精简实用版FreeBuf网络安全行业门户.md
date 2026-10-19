## 一、端口扫描技术分类

### 完全连接扫描：

完全连接扫描利用 TCP/IP
协议的三次握手连接机制，使源主机和目的主机的某个端口建立一次完整的连接。如果建立成功，则表明该端口开放。否则，表明该端口关闭。

### 半连接扫描：

半连接扫描是指在源主机和目的主机的三次握手连接过程中，只完成前两次握手，不建 立一次完整的连接。

### SYN 扫描：

首先向目标主机发送连接请求，当目标主机返回响应后，立即切断连接过程，并查看响 应情况。如果目标主机返回ACK信息，表示目标主机的该端口开放。如果目标主机返
回RESET 信息，表示该端口没有开放。

### ACK 扫描：

首先由主机A向目标主机B发送FIN数据包，然后查看反馈数据包的TTL值和WIN值。
开放端口所返回的数据包的TTL值一般小于64，而关闭端口的返回值一般大于64。开 放端口所返回的数据包的WIN值一般大于0，而关闭端口的返回值一般等于0。

........  
还有很多，以上是常用的方式，也是众多端口扫描器的原理。

下面，我将分享一些实用的工具。扫描的目标均是同一IP。

47.97.xxx.118

## 二、在线端口扫描

### 1\. [FOFA](https://fofa.so)

可以发现，7071端口
nmap(-sS)并没有扫描出来，但是确实是能访问成功，并且上面有站点。![](https://image.3001.net/images/20210919/1632028964_6146c924936a6f7422e01.png!small)

用nmap专门扫7071，可以发现成功扫出来了，说明SYN半连接扫描-sS快是快，但是准确度不是特别高

![](https://image.3001.net/images/20210919/1632028998_6146c946e4e96d9081b50.png!small)

### 2\.
[Shodan](https://www.shodan.io)![](https://image.3001.net/images/20210919/1632029067_6146c98bb9a30cfc8916f.png!small)

### 3\. [一个在线端口扫描](https://scan.dyboy.cn/web/portscan)

扫描常见398个端口，结果不是很全，不过还行。![](https://image.3001.net/images/20210919/1632029202_6146ca1294a08727643aa.png!small)

### 4\. 白嫖型

本地网不好，只能找找在线端口扫描了，这找也有门道，绝大部分是有扫描数量限制或者是端口号限制，无法一键入魂，不过可以用py脚本突破，but脚本写的不好还不如本地扫呢，能不能不写脚本？找了一哈，发现一套在线扫描工具，

例：<http://www.all-tool.cn/Tools/portblast/>

这里扫描端口是没有IP、端口数量限制，故可生成1~65535、以’.’间隔的字符串，然后填入自定义端口进行扫描。

![](https://image.3001.net/images/20210919/1632029315_6146ca833e8405a6dc9a0.png!small)

只开了一个页面，0.5s页面加载一次，可以多开几个网页进行分段扫描。  
优点：对本地网络要求低，扫描全面且准确。  
扫描中~~~，对于结果，复制文本，写点py脚本处理一下就可以放到nmap去扫端口详情了，这就像在线版masscan，最后和nmap联动。（联动的话，需要写脚本了，这具体的脚本日后来补~~）![](https://image.3001.net/images/20210919/1632029387_6146cacbd0b5dd807ad93.png!small)

随便找点特征，如/portblast，可以发现还是有几十个站使用了这套程序![](https://image.3001.net/images/20210919/1632029908_6146ccd4bc8e553f792d7.png!small)

![](https://image.3001.net/images/20210919/1632029934_6146cceec614f38731318.png!small)

## 三、NMAP

Nmap好用是好用，但是有些参数用了，确实很慢，而且会对网络有很大的影响。以下是非常好用的命令。

### 1\. nmap -sS 47.97.xxx.118

说明：-sS是半连接扫描，TCP半连接扫描是不会留下记录，并且速度很快，十分常用。  
共21个开放端口，用时8.71
S![](https://image.3001.net/images/20210919/1632030097_6146cd915ceedf4e6f27b.png!small)

### 2\. nmap -sP 47.97.xxx.118/24

或者

    
    
    nmap -sP 47.97.xxx.0-255

说明：扫描网段中存活的主机。其中-sP是ping扫描![](https://image.3001.net/images/20210919/1632030161_6146cdd10974f7f96f580.png!small)

### 3\. nmap -O 47.97.xxx.118

说明：OS操作系统类型的探测![](https://image.3001.net/images/20210919/1632030203_6146cdfb7ef507c827122.png!small)

### 4\. nmap快速扫描大量主机端口方法

    
    
    nmap -sS -Pn -n --open --min-hostgroup 4 --min-parallelism 1024 --host-timeout 30 -T4 -v -oG result.txt -iL ip.txt  
    注：此方法会有部分疏漏，但是面对大批量目标速度快、较为精准。  
    其中：  
    -Pn：禁用PING检测，这样速度快，并且可以防止有些主机无法ping通而被漏掉不扫描  
    -open：只输出检测状态为open的端口，即开放的端口  
    -min-hostgroup 4：调整并行扫描组的大小  
    -min-parallelism 1024：调整探测报文的并行度  
    -host-timeout 30：检测超时的跳过  
    -oG：输出为比较人性化的格式，一条记录一行  
    -iL 扫描文件中的所有⽬标地址，如nmap -sS -iL ip.txt

参考文章：

<https://www.cnblogs.com/cyrusxx/p/12562867.html>

### 5\. 其他推荐参数：

    
    
    -v 显示扫描过程
    -p 指定端口，如-p 80,8080,8081
    -sV探测端口以及服务版本信息(注：速度会慢下来)
    --randomize-hosts  随机扫描，对目标主机的顺序随机划分
    --scan-delay    延时扫描，单位秒,调整探针之间的延迟

## 四、Masscan

批量快速端口扫描  
Kali集成，Linux上运行，源码需要编译才能在windows上运行，这就很不爽了，于是乎翻遍Github，终于找到一款贼无脑、环境不出错、好用的masscan了。（呜呜呜，求个赞，也给项目作者点个收藏！）

项目地址：<https://github.com/zmzmon/masscan>

### 1\.
打开工具![](https://image.3001.net/images/20210919/1632030608_6146cf90afa860ec71d6d.png!small)

### 2\. 点击【安装WinPcap】

注意：就算你之前安装了，这一步必须点，点了就不管了，WinPcap不需要重装，主要是它会释放一些配置文件，masscan才能正常运作。

### 3.【清空IP】

会生成一个IP.txt，将目标填入

### 4\. 点击【调节扫描速度】

会生成一个【扫描.cmd】，可以直接在里面进行命令的配置

### 5\. 点击【自动整理】

会有两个py脚本，整理结果的

### 6\. 配置【扫描.cmd】

把端口改为全端口

    
    
    masscan -p 1-65535 -iL IP.txt -oX 111.xml --rate 2000 -sS

### 7\. 点击【开始扫描】

### 8\. 扫描结束

黑屏自动关闭，生成111.xml

### 9\. 点击【自动整理】

释放两个py脚本

### 10\. 运行脚本

    
    
    python masscan-xml-整理.py

### 11\. 生成结果文件

jieguo.txt

开放端口有49个，用时不到20S，结果较为全面，不过误报也是存在的，李姐。![](https://image.3001.net/images/20210919/1632030939_6146d0dbdd6d45394dd96.png!small)

## 五、Gogy

扫描全端口，不扫漏洞，只扫资产。时间上花费有点多，一个IP全端口大概20分钟吧。  
Gogy扫描资产真滴强，发现6684端口nmap(-sS)没有扫出来，但是gogy、masscan扫出来了。![](https://image.3001.net/images/20210919/1632031325_6146d25d7e806665f67c6.png!small)

## 六、nmap和masscan联动

使用masscan做全端口开放检测，检测出来端口信息后，用nmap进行服务信息识别。  
以下两个项目均可完成功能，不过代码都是Linux上的。

<https://github.com/hellogoldsnakeman/masnmapscan-V1.0>

<https://github.com/CitrusIce/masmap_script/>

简单写了win的脚本，第五步整理完后会生成一个jieguo.txt，一行一个ip:port，我将以这个文件作为输入，用nmap处理后作为输出。

import os

with open("jieguo.txt", 'r') as p:  
urls = p.readlines()  
#IP-Port集合,定义为字典，键为IP，键值为对应开放端口组成的字符串(以逗号分割不同的端口)  
ip_port_dict = {}  
#将jieguo.txt中的ip提取出来，字典中键自动去重  
for url in urls:  
ip_port_dict[url.split(':')[0]] = ""  
#遍历IP，将IP(键)对应的端口拼接到字符串(键值)中  
for key, value in ip_port_dict.items():  
for url in urls:  
if key in url:  
#去掉读取文件而产生的换行符  
url = url.replace("\n", "")  
ip_port_dict[key] = ip_port_dict[key] + url.split(':')[1] + ','  
str = ip_port_dict[key]  
#去掉键值字符串 最后面多余出来的','  
ip_port_dict[key] = str[0:len(str)-1]

#调用nmap，这里需要改下你自己的nmap的路径  
for key, value in ip_port_dict.items():  
os.system("E:\\\nmap\\\nmap.exe " + "-p " + value + " -sV -v " + key)

结果：大概一分钟不到，52个IP:port

第一个IP的端口信息![](https://image.3001.net/images/20210919/1632031626_6146d38a661939517fcd0.png!small)

第二个IP，我就放了一个8080端口![](https://image.3001.net/images/20210919/1632031653_6146d3a55d96dc9687466.png!small)

