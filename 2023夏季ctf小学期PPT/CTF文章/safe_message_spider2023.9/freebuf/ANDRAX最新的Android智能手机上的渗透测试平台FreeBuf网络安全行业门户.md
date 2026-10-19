**今天给大家介绍一款专为Android智能手机设计的渗透测试平台，该工具名叫ANDRAX，它可以直接在原生Android系统上运行，它不仅能够跟常用Linux发行版相媲美，而且它的功能甚至比常见Linux发行版更加强大。**

![1.png](https://image.3001.net/images/20181019/1539928374_5bc9713626f9b.png!small)

## 为何Android能够如此强大？

很简单，每个人都有智能手机，而且几乎一天到晚都离不开它们。我们可以轻松地在人群中伪装自己，目前大多数Android智能手机采用的处理器架构都是ARM，而这也是一种现代的、健壮的体系结构。有了触摸屏之后，我们可以通过图形交互界面轻松灵活地使用各种工具。

从技术上讲，大家不能拿NetHunter来跟ANDRAX作比较。因为ANDRAX是一款专为Android智能手机设计的渗透测试平台，而NetHunter只是一款Debian模拟运行工具。

Termux就不一样了，它可是我们的“好朋友”。Termux是一款Linux数据包安装程序，它使用的是Debian环境，可以直接在原生Android端运行。

值得一提的是，ANDRAX和Termux的开发架构非常相似，而且它们使用了很多相同的代码库以及GNU/Linux资源。

不过，Termux并不是一个渗透测试平台，它所提供的基础工具均来源于Debian环境，渗透测试可不是什么“基础”操作喔！

## 功能与工具

### 信息收集

    
    
    -Whois
    
    -BindDNS工具
    
    -Dnsrecon
    
    -Raccoon
    
    -DNS-Cracker
    
    -Firewalk

### 网络扫描

    
    
    -Nmap– 网络映射工具
    
    -Masscan
    
    -SSLScan
    
    -Amap

### 数据包制作

    
    
    -Hping3
    
    -Nping
    
    -Scapy
    
    -Hexinject
    
    -Ncat
    
    -Socat

### 网络攻击

    
    
    -ARPSpoof
    
    -Bettercap
    
    -MITMProxy
    
    -EvilGINX2

### 网站入侵

    
    
    -0d1n
    
    -Wapiti3
    
    -Recon-NG
    
    -PHPSploit
    
    -Photon
    
    -XSSer
    
    -Commix
    
    -SQLMap
    
    -Payloadmask
    
    -AbernathY-XSS

### 密码破解

    
    
    -Hydra
    
    -Ncrack
    
    -JohnThe Ripper
    
    -CRUNCH

### 无线攻击

    
    
    -VMPEvil AP
    
    -Aircrack-NGTools
    
    -Cowpatty
    
    -MDK3
    
    -Reaver

### 漏洞利用

    
    
    -MetaSploitFramework
    
    -RouterSploitFramework
    
    -Getsploit
    
    -OWASPZSC
    
    -Rop-TOOL

等等等等…….

### 高级终端

该工具还提供了高级且专业的终端模拟器：

![2.png](https://image.3001.net/images/20181019/1539928448_5bc971804f036.png!small)![3.png](https://image.3001.net/images/20181019/1539928448_5bc9718081410.png!small)![4.png](https://image.3001.net/images/20181019/1539928448_5bc971808b4c6.png!small)

### 动态分类(DCO)

美化的工具分类系统：

![51.png](https://image.3001.net/images/20181019/1539928487_5bc971a7eafb0.png!small)![52.png](https://image.3001.net/images/20181019/1539928488_5bc971a895475.png!small)![53.png](https://image.3001.net/images/20181019/1539928488_5bc971a83a00e.png!small)![54.png](https://image.3001.net/images/20181019/1539928488_5bc971a8bac05.png!small)

### 高级IDE

支持多种编程语言：

![61.png](https://image.3001.net/images/20181019/1539928513_5bc971c1d0f8e.png!small)![62.png](https://image.3001.net/images/20181019/1539928513_5bc971c1f0173.png!small)![63.png](https://image.3001.net/images/20181019/1539928514_5bc971c2262ed.png!small)

### 信息收集

可利用这些工具收集目标信息：

![71.png](https://image.3001.net/images/20181019/1539928552_5bc971e8abec5.png!small)![72.png](https://image.3001.net/images/20181019/1539928552_5bc971e8c4df9.png!small)![73.png](https://image.3001.net/images/20181019/1539928552_5bc971e8e12b0.png!small)![74.png](https://image.3001.net/images/20181019/1539928553_5bc971e96a28c.png!small)![75.png](https://image.3001.net/images/20181019/1539928553_5bc971e97bdd5.png!small)![76.png](https://image.3001.net/images/20181019/1539928553_5bc971e995559.png!small)

### 扫描

提供了渗透第二阶段的扫描工具：

![81.png](https://image.3001.net/images/20181019/1539928643_5bc97243c5a25.png!small)![82.png](https://image.3001.net/images/20181019/1539928643_5bc97243db3c4.png!small)![83.png](https://image.3001.net/images/20181019/1539928643_5bc97243ee27d.png!small)![84.png](https://image.3001.net/images/20181019/1539928644_5bc9724478be6.png!small)

### 数据包制作

可手动制作网络数据包：

![91.png](https://image.3001.net/images/20181019/1539928657_5bc972517cd66.png!small)![92.png](https://image.3001.net/images/20181019/1539928657_5bc972518bc84.png!small)

### 网络攻击

用于网络攻击的工具：

![101.png](https://image.3001.net/images/20181019/1539928668_5bc9725cd5669.png!small)![102.png](https://image.3001.net/images/20181019/1539928668_5bc9725ced04c.png!small)
![103.png](https://image.3001.net/images/20181019/1539928669_5bc9725d0c3b4.png!small)![104.png](https://image.3001.net/images/20181019/1539928669_5bc9725d986ef.png!small)

### 网站入侵

可对网站和Web应用进行攻击：

![111.png](https://image.3001.net/images/20181019/1539928688_5bc97270b6dd6.png!small)![112.png](https://image.3001.net/images/20181019/1539928688_5bc97270cbab8.png!small)
![113.png](https://image.3001.net/images/20181019/1539928688_5bc97270d921e.png!small)![114.png](https://image.3001.net/images/20181019/1539928689_5bc972712663f.png!small)![115.png](https://image.3001.net/images/20181019/1539928689_5bc9727175046.png!small)

### 密码破解

![121.png](https://image.3001.net/images/20181019/1539928706_5bc97282978ef.png!small)![122.png](https://image.3001.net/images/20181019/1539928706_5bc97282abcfe.png!small)

### 无线入侵

![131.png](https://image.3001.net/images/20181019/1539928721_5bc97291474f2.png!small)![132.png](https://image.3001.net/images/20181019/1539928721_5bc972915d99c.png!small)

### 漏洞利用

![141.png](https://image.3001.net/images/20181019/1539928735_5bc9729f9b1b6.png!small)![142.png](https://image.3001.net/images/20181019/1539928735_5bc9729fd754f.png!small)
![143.png](https://image.3001.net/images/20181019/1539928735_5bc9729fd7a66.png!small)![144.png](https://image.3001.net/images/20181019/1539928736_5bc972a03b6a8.png!small)

## 工具下载地址

ANDRAX：【[传送门](https://andrax-pentest.org/download)】

 ***参考来源：[ANDRAX](https://www.kitploit.com/2018/10/andrax-first-and-unique-penetration.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

