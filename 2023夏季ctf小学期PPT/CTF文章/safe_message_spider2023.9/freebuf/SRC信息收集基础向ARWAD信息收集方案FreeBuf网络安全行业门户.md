# 目录

  * 关于ARWAD方案
  * Bash Shell实现ARWAD自动化
  * 收集期间的清点

# 关于ARWAD方案

![1654765969_62a1b991ad1a9d6ab1d2a.png!small](https://image.3001.net/images/20220609/1654765969_62a1b991ad1a9d6ab1d2a.png!small)

由Ahmad Halabi黑客巨佬在2021年@Hack conference in
Riyadh会议上提出漏洞赏金挖掘终极侦察路线图，也是目前我常用的信息收集方案。

# 收集类型

 **主动(Active)：** 需要跟目标系统、业务直接交互，比如说爆破子域名、扫描IP/域名开放端口

 **被动(Passive)：** 收集信息不需要跟目标进行交互，比如收集开源信息，比如企查查

# ARWAD收集方法

  1.  **Whois：** 收集域所有者的相关信息及域注册信息
  2.  **DNS信息：** 收集解析IP、记录类型、类级别等，用于查询DNS相关的漏洞
  3.  **收购域：** 收集哪些域名被企业公司所收购，提供更多的目标域，发现更多漏洞机会
  4.  **子域名枚举：** 分主被动，搭配多个类型不一的工具扫描、整合，提供更多更精准的信息
  5.  **排序与筛选：** 去重与子域名存活检测
  6.  **子域名接管：** 在第二步骤收集到的DNS信息下，进行子域名接管检测
  7.  **提取IP地址：** 从收集到的子域单中提取所有IP地址，用于"开源情报"和“端口扫描”阶段使用
  8.  **端口扫描与获取标志：** 大规模扫描提取到的IP地址，获取端口与协议信息
  9.  **开源信息：** 获取到的IP与子域名利用Shodan与Censys等情报社区，扫描以获取更多的信息。
  10.  **收集Web目标：** 收集开启80/443端口的目标存活域
  11.  **子域名爆破：** 使用如Altdns、ksubdomain等类型的工具对存活域进行爆破
  12.  **内容发现：** 暴力破解目录、备份扫描、文件扫描.......
  13.  **Github搜索：** 寻找公开的敏感代码/信息或有价值....
  14.  **Nuclei：** 漏洞扫描
  15.  **WayBack Machine：** 提取缓存信息与大量的URL和端口
  16.  **提取JS文件：** 从JS文件中获取敏感接口、端口等信息

# Bash Shell实现ARWAD自动化

Ahmad Halabi在文章末尾，提到了关于ARWAD Bash Shell的自动化方案，即:

![1654766150_62a1ba463ffc7bb0d1d95.png!small](https://image.3001.net/images/20220609/1654766150_62a1ba463ffc7bb0d1d95.png!small)

> 注释：左图为Ahmad Halabi的ARWAD Bash Shell自动化方案，右图为我自己设定修改的解决方案

可以看到，github搜索、WayBack、开源信息、内容发现等部分Ahmad Halabi在自己的 Bash
Shell自动化方案都没有添加，而且我也不打算添加，具体原因留到第三部分讲解

# 涉及到的工具

注意：在Kali上搭建会更轻松

Sublist3：

> https://github.com/aboul3la/Sublist3r.git

assetfinder：

>
> https://github.com/tomnomnom/assetfinder/releases/download/v0.1.1/assetfinder-> linux-amd64-0.1.1.tgz

Amass：

> go install -v github.com/OWASP/Amass/v3/...@master

子域名爆破字典：

>
> https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/subdomains-> top1million-5000.txt

subjack：

> go get github.com/haccer/subjack

httpx：

> go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

ksubdomain：

>
> https://github.com/knownsec/ksubdomain/releases/download/v0.7/ksubdomain_linux.zip

# Amass 免费API统计

Amass有API和没有API是两个不一样的工具，统计了一下可以免费白嫖的API：

AlienVault, BinaryEdge, BufferOver, BuiltWith, Censys, Chaos, FacebookCT,
GitHub, NetworksDB, PassiveTotal, SecurityTrails, Shodan, SiteDossier, Spyse,
Twitter, URLScan, VirusTotal, WhoisXML, ZETAlytics, Cloudflare

# Bash Shell 自动化(测试版)

脚本实现原理很简单，懒得自己写脚本的师傅也可以直接使用我写好的，代码比较丑，但是能用。

> <https://github.com/ShmilyChris/ARWAD_Bash_Shell>

![1654766964_62a1bd746a65c81736795.png!small](https://image.3001.net/images/20220609/1654766964_62a1bd746a65c81736795.png!small)

正常来说，目录下有五个文件，其它用得到的工具，如subjack、httpx、assetfinder都可以在kali系统使用go或输入工具名进行安装

# 运行效果

![1654767273_62a1bea95e1763a279546.png!small](https://image.3001.net/images/20220609/1654767273_62a1bea95e1763a279546.png!small)

生成三个文件，分别是存活列表、总列表、包含标题、HTTP状态码的存活列表，生成一个包含标题和状态码的列表是为了能在挖掘SRC的过程中快速定位，Bash
Shell自动化方案与脚本都不成熟，还是希望且需要各位师傅的意见，能多给我提提建议，完善整个脚本与过程。

# 收集期间的清点

在第二部分中说过，Bash
shell自动化方案没有加入github搜索、WayBack、开源信息、内容发现等方法，但，我们可以在自动化方案扫描的过程中，使用另外一种方案，进行清点。

###### Bug Bounty Helper

> https://dorks.faisalahmed.me/

![1654767354_62a1befa0fc9520d96531.png!small](https://image.3001.net/images/20220609/1654767354_62a1befa0fc9520d96531.png!small)

在自动化方案扫描期间，利用Bug Bounty Helper，调用谷歌黑客、Yandex、archive.org、github等帮助我们快速清点，比如：

######  **寻找URL跳转**

![1654767370_62a1bf0a31c2fce6c7c05.png!small](https://image.3001.net/images/20220609/1654767370_62a1bf0a31c2fce6c7c05.png!small)

######  **寻找后台**

![1654767425_62a1bf41ceccc27481103.png!small](https://image.3001.net/images/20220609/1654767425_62a1bf41ceccc27481103.png!small)

######  **获取WayBack信息**

![1654767432_62a1bf488a685b24e5f89.png!small](https://image.3001.net/images/20220609/1654767432_62a1bf488a685b24e5f89.png!small)

######  **获取Github信息**

![1654767437_62a1bf4d86c1b8d5b8ef7.png!small](https://image.3001.net/images/20220609/1654767437_62a1bf4d86c1b8d5b8ef7.png!small)

| 第一次发文有点丑，感谢师傅们的耐心观看。

