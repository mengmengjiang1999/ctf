![](https://image.3001.net/images/20210521/1621571329_60a73701d9767251e4748.png!small)

**kali Linux工具帮你评估 Web 服务器的安全性，并帮助你执行黑客渗透测试。**

###  **注意：这里不是所提及的所有工具都是开源的。**

## 1\. Nmap

![1621507756_60a63eac521c0abeb99bc.png!small?1621507755558](https://image.3001.net/images/20210520/1621507756_60a63eac521c0abeb99bc.png!small?1621507755558)

 **Nmap** （ **网络映射器** ）是一款用于 **网络发现** 和 **安全审计** 的 **网络安全** 工具.

[核心功能](https://zh.wikipedia.org/wiki/Nmap#Nmap_%E6%A0%B8%E5%BF%83%E5%8A%9F%E8%83%BD)
**[:
主机发现,端口扫描,版本侦测,操作系统侦测,防火墙/IDS规避和哄骗](https://zh.wikipedia.org/wiki/Nmap#Nmap_%E6%A0%B8%E5%BF%83%E5%8A%9F%E8%83%BD)**

 **Nmap 基本语法**

    
    
    nmap [ <扫描类型> ...] [ <选项> ] { <扫描目标说明> }
    

**全面进攻性** 扫描（包括各种主机发现、端口扫描、版本扫描、OS扫描及默认脚本扫描）:

nmap -A -v target_ip

 **ping** 扫描: nmap -sn -v target_ip

 **快速端口** 扫描:nmap -F -v target_ip

 **版本** 扫描: nmap -sV -v target_ip

 **操作系统** 扫描:nmap -O -v target_ip

## 2\. Wireshark

![1621519865_60a66df98359498712be9.png!small?1621519864772](https://image.3001.net/images/20210520/1621519865_60a66df98359498712be9.png!small?1621519864772)

##

 **Wireshark的** 是一个[自由](https://en.wikipedia.org/wiki/Free_software
"跨平台")和[开源](https://en.wikipedia.org/wiki/Open-source_software
"开源软件")[数据包分析器,是 Kali Linux
上最受欢迎的网络分析仪。](https://en.wikipedia.org/wiki/Packet_analyzer)

 **Wireshark** 使用WinPCAP作为接口，直接与 **网卡** 进行 **数据报文交换。**

## 3\. Metasploit Framework

![1621522244_60a67744d96353fc7a85a.png!small?1621522243943](https://image.3001.net/images/20210520/1621522244_60a67744d96353fc7a85a.png!small?1621522243943)

 **Metasploit Framework**
是一个旨在提供[安全漏洞信息](https://zh.wikipedia.org/wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%AE%89%E5%85%A8%E9%9A%90%E6%82%A3
"计算机安全隐患")计算机安全项目，可以协助安全工程师进行[渗透测试](https://zh.wikipedia.org/wiki/%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95
"渗透测试")（penetration
testing）及[入侵检测系统](https://zh.wikipedia.org/wiki/%E5%85%A5%E4%BE%B5%E6%A3%80%E6%B5%8B%E7%B3%BB%E7%BB%9F)签名开发。

 **Metasploit Framework**
最为知名的子项目是[开源](https://zh.wikipedia.org/wiki/%E5%BC%80%E6%94%BE%E6%BA%90%E4%BB%A3%E7%A0%81)的Metasploit框架，一套针对远程主机进行开发和执行“[exploit](https://zh.wikipedia.org/wiki/Exploit
"Exploit")代码”的工具

使用 **Metasploit框架** 的基本步骤包括：

选择并配置一个攻击代码(exploit, 利用[漏洞](https://zh.wikipedia.org/wiki/%E6%BC%8F%E6%B4%9E
"漏洞")来进入目标系统的代码）；

检查目标系统是否会被此代码影响；

选择并配置一个[有效负载](https://zh.wikipedia.org/wiki/%E6%9C%89%E6%95%88%E8%B4%9F%E8%BD%BD)(payload,
在成功进入后在目标系统上执行的代码）；

选择编码方式，使[入侵预防系统](https://zh.wikipedia.org/wiki/%E5%85%A5%E4%BE%B5%E9%A2%84%E9%98%B2%E7%B3%BB%E7%BB%9F
"入侵预防系统")，忽略已被编码的有效负载；

执行攻击代码。

## 4.Hydra

![1621557142_60a6ff96c05efacb613fa.png!small?1621557141539](https://image.3001.net/images/20210521/1621557142_60a6ff96c05efacb613fa.png!small?1621557141539)

 **Hydra**
是[并行化的](https://en.wikipedia.org/wiki/Parallel_computing)网络[登录破解程序，](https://en.wikipedia.org/wiki/Password_cracking)内置于各种操作系统中。

 **Hydra** 通过使用[暴力攻击](https://en.wikipedia.org/wiki/Brute-force_attacks
"并行运算")，猜测正确的用户名和[密码](https://en.wikipedia.org/wiki/Password "密码")。

 **kali** 下是默认安装的，几乎支持 **所有协议** 的在线破解

## 5.Aircrack-ng

![1621558601_60a705494e04e16c4a9ea.png!small?1621558601612](https://image.3001.net/images/20210521/1621558601_60a705494e04e16c4a9ea.png!small?1621558601612)

 **Aircrack-ng** 是一个与[802.11](https://zh.wikipedia.org/wiki/802.11
"802.11")标准的无线网络分析有关的安全软件，主要功能有：网络侦测，[数据包嗅探](https://zh.wikipedia.org/wiki/%E5%97%85%E6%8E%A2
"嗅探")，[WEP](https://zh.wikipedia.org/wiki/%E6%9C%89%E7%B7%9A%E7%AD%89%E6%95%88%E5%8A%A0%E5%AF%86
"有线等效加密")和[WPA](https://zh.wikipedia.org/wiki/WPA
"WPA")/[WPA2-PSK](https://zh.wikipedia.org/w/index.php?title=WPA2-PSK&action=edit&redlink=1
"WPA2-PSK（页面不存在）")破解。

 **Aircrack-ng可以** 用于 **监视** ， **收集** 有关WiFi的信息SSID（服务集标识符）IP和MAC地址以及WiFi的破解密码

## 6.Nessus

![1621559138_60a70762f130c4c142c9d.png!small?1621559139366](https://image.3001.net/images/20210521/1621559138_60a70762f130c4c142c9d.png!small?1621559139366)

 **Nessus** 为一款[系统](https://zh.wikipedia.org/wiki/%E7%B3%BB%E7%BB%9F
"系统")弱点[扫描](https://zh.wikipedia.org/wiki/%E6%89%AB%E6%8F%8F "扫描")与分析软件。能够协助
**检测和修复** 各种操作系统、应用程序、乃至设备上的漏洞、恶意软件、配置错误、及补丁的缺失。

但是，它不再是免费的工具了，免费的功能受限制。

## 7.WafW00f

![1621566853_60a72585ab7ca2a6138c3.png!small?1621566854391](https://image.3001.net/images/20210521/1621566853_60a72585ab7ca2a6138c3.png!small?1621566854391)

 **Wafw00f --** 防火墙检测工具，

 **Wafw00f** 使用一组HTTP请求和方法查询Web服务器,分析来自它们的响应并检测防火墙

## 8\. Burp Suite

![1621526092_60a6864c6294e11a17405.png!small?1621526091423](https://image.3001.net/images/20210520/1621526092_60a6864c6294e11a17405.png!small?1621526091423)

**Burp Suite** 是一个用于测试网络应用程序安全性的图形化工具，出色的网络安全分析工具。

 **主要模块** 介绍:

 **HTTP代理** — 它作为一个 Web 代理服务器运行，并且位于浏览器和目标 Web 服务器之间。这允许拦截、检查和修改在两个方向上通过的原始流量。

 **Scanner** (扫描器)— 一个 Web 应用程序安全扫描器，用于执行 Web 应用程序的自动漏洞扫描。

 **Intruder** (入侵)— 此工具可以对 Web
应用程序执行自动攻击。该工具提供了一种可配置的[算法](https://zh.wikipedia.org/wiki/%E7%AE%97%E6%B3%95
"算法")，可以生成恶意 HTTP 请求。Intruder 工具可以测试和检测 [SQL
注入](https://zh.wikipedia.org/wiki/SQL%E8%B3%87%E6%96%99%E9%9A%B1%E7%A2%BC%E6%94%BB%E6%93%8A
"SQL资料隐码攻击")、[跨站脚本](https://zh.wikipedia.org/wiki/%E8%B7%A8%E7%B6%B2%E7%AB%99%E6%8C%87%E4%BB%A4%E7%A2%BC
"跨网站指令码")、参数篡改和易受蛮力攻击的漏洞。

 **Spider(蜘蛛)** — 一个自动抓取 Web 应用程序的工具。

 **Repeater(中继器)** — 一个可以用来手动测试应用程序的简单工具。它可以用于修改对服务器的请求，重新发送它们并观察结果。

 **Decoder** (解码器)—
一种将已编码的数据转换为其规范形式，或将原始数据转换为各种编码和散列形式的工具。它能够利用启发式技术智能识别多种编码格式。

 **Comparer** (比较)— 在任意两个数据项之间执行比较（一个可视化的“差异”）的工具。

 **Extender** (扩展)— 允许安全测试人员加载 Burp 扩展，使用安全测试人员自己的或第三方代码扩展 Burp 的功能

 **Sequencer** (会话)— 一种分析数据项样本随机性的工具。它可以用于测试应用程序的会话令牌或其他重要的数据项，如反 CSRF
令牌、密码重置令牌等。

## 9.Maltego

![1621568089_60a72a59da57f1f4697a9.png!small?1621568090170](https://image.3001.net/images/20210521/1621568089_60a72a59da57f1f4697a9.png!small?1621568090170)

 **Maltego** \--是一个 **开源情报** （OSINT）和 **图形链接分析** 工具,用于 **收集和连接** 用于调查任务的信息。

 **Maltego 以简单,智能,功能强大受安全人员喜爱。**

## 10.W3AF

![1621570653_60a7345de36022a563727.png!small?1621570654103](https://image.3001.net/images/20210521/1621570653_60a7345de36022a563727.png!small?1621570654103)

  

 **W3AF** 是一个[开源](https://zh.wikipedia.org/wiki/%E5%BC%80%E6%BA%90
"开源")的Web应用程序安全扫描器。该项目为[Web应用程序](https://zh.wikipedia.org/wiki/Web%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F
"Web应用程序")提供了一个漏洞扫描器和漏洞利用工具。它提供了有关[安全性漏洞](https://zh.wikipedia.org/wiki/%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%AE%89%E5%85%A8%E9%9A%90%E6%82%A3)的信息，以便在[渗透测试](https://zh.wikipedia.org/wiki/%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95
"渗透测试")项目中使用

 **W3AF** 能用Web应用程序攻击和审核框架的Arconym，来查找网站中的缺陷

## 11.Wpscan

![1621571845_60a7390565d22fd5ad546.png!small?1621571846484](https://image.3001.net/images/20210521/1621571845_60a7390565d22fd5ad546.png!small?1621571846484)

 **Wpscan** 是Kali Linux 自带的一款漏洞扫描工具，它采用Ruby 编写，能够扫描WordPress
网站中的多种安全漏洞，它可以为所有Web开发人员扫描 WordPress漏洞并在他们开发前找到并解决问题。

WordPress（WP，WordPress.org）是一个[免费的开源](https://en.wikipedia.org/wiki/Free_and_open-source_software
"的PHP")[内容管理系统](https://en.wikipedia.org/wiki/Content_management_system)（CMS）

## 12.sqlmap

![1621573031_60a73da7e023739dc8878.png!small?1621573033546](https://image.3001.net/images/20210521/1621573031_60a73da7e023739dc8878.png!small?1621573033546)

 **sqlmap** 是一个开源的渗透测试工具，可以用来进行自动化检测，能自动化利用 SQL 注入漏洞的过程，帮助你接管数据库服务器

