![](https://image.3001.net/images/20210607/1623049715_60bdc5f3d38f144522e23.jpg!small)

## 关于MagicRecon

MagicRecon是一个功能强大的Shell脚本，它可以帮助广大研究人员在有针对性的挖洞过程中，最大化地收集网络侦察信息和其他数据。MagicRecon所收集到的所有数据都将以一种规范化的形式存储在目录中，并且支持多种数据格式。

当前的MagicRecon的v2.0新版本，引入了大量的新工具以实现数据收集和漏洞挖掘的自动化。除此之外，MagicRecon
v2.0还提供了一个菜单，以供用户选择所要执行的操作。

新版本还提供了一个“安装依赖”的选项，用户可以直接安装MagicRecon所有的工具和依赖组件。脚本代码以模块化的方式开发，用户也可以轻松进行自定义修改。

## 功能介绍

在MagicRecon的帮助下，广大研究人员可以轻松发现以下内容：

  * 敏感数据披露
  * HTTP Header收集
  * 开放S3 Bucket
  * 子域名接管
  * SSL/TLS漏洞
  * 开放端口和服务
  * 电子邮件欺诈
  * 节点发现
  * 目录发现
  * 文件发现
  * JavaScript文件敏感信息扫描
  * CORS错误配置
  * 跨站脚本漏洞（XSS）
  * 开放重定向
  * SQL注入漏洞
  * 服务器端请求伪造（SSRF）
  * CRLF注入
  * 远程代码执行（RCE）
  * 其他漏洞

## 工具要求

为了保证MagicRecon项目的正常运行，广大研究人员需要安装下列依赖工具和组件：

  * [Subfinder](https://github.com/projectdiscovery/subfinder)
  * [Httpx](https://github.com/projectdiscovery/httpx)
  * [Notify](https://github.com/projectdiscovery/notify)
  * [Nuclei](https://github.com/projectdiscovery/nuclei)
  * [Nuclei-templates](https://github.com/projectdiscovery/nuclei-templates)
  * [SecLists](https://github.com/danielmiessler/SecLists)
  * [Corsy](https://github.com/s0md3v/Corsy)
  * [Securityheaders](https://github.com/koenbuyens/securityheaders)
  * [Ssl-checker](https://github.com/narbehaj/ssl-checker)
  * [Secretfinder](https://github.com/m4ll0k/SecretFinder)
  * [Wfuzz](https://github.com/xmendez/wfuzz)
  * [Aquatone](https://github.com/michenriksen/aquatone)
  * [Html-tool](https://github.com/tomnomnom/hacks/tree/master/html-tool)
  * [Waybackurls](https://github.com/tomnomnom/waybackurls)
  * [Kxss](https://github.com/Emoe/kxss)
  * [Anew](https://github.com/tomnomnom/anew)
  * [Qsreplace](https://github.com/tomnomnom/qsreplace)
  * [Urlprobe](https://github.com/1ndianl33t/urlprobe)
  * [Anew](https://github.com/tomnomnom/anew)
  * [Gf](https://github.com/tomnomnom/gf)
  * [Gobuster](https://github.com/OJ/gobuster)
  * [Findomain](https://github.com/Findomain/Findomain)
  * [spoofcheck](https://github.com/BishopFox/spoofcheck)
  * [linkfiner](https://github.com/GerbenJavado/LinkFinder)
  * [Nmap](https://nmap.org/)

## 工具使用

    
    
    ./magicRecon.sh
    
     
    
    Output:
    
     
    
     __  __             _      ____                      
    
    |  \/  | __ _  __ _(_) ___|  _ \ ___  ___ ___  _ __  
    
    | |\/| |/ _` |/ _` | |/ __| |_) / _ \/ __/ _ \| '_ \
    
    | |  | | (_| | (_| | | (__|  _ <  __/ (_| (_) | | | |
    
    |_|  |_|\__,_|\__, |_|\___|_| \_\___|\___\___/|_| |_|
    
                  |___/                                  
    
     
    
    MENU
    
    1) Install dependencies
    
    2) Massive vulnerability analysis with notifications via Discord, Telegram or Slack
    
    3) Subdomain enumeration
    
    4) Subdomain enumeration and vulnerability scanning with nuclei
    
    5) Subdomain enumeration with common vulnerabilities scanning
    
    6) Scan for javascript files
    
    7) Scan for files and directoires
    
    8) All in one! (original MagicRecon)
    
    q) Exit
    
    Choose a option:

## 工具运行演示

![](https://image.3001.net/images/20210607/1623049749_60bdc61572a8a82a85d9d.gif!small)

## 项目地址

MagicRecon：【[ _GitHub传送门_](https://github.com/robotshell/magicRecon)】

