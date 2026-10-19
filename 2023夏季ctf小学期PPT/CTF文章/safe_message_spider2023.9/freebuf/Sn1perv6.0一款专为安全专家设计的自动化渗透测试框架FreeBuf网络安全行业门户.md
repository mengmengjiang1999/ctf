## 前言

**今天给大家介绍的是一款专为安全专家设计的自动化渗透测试框架，这个自动化渗透测试框架名叫Sn1per。实际上，Sn1per社区版是一款自动化扫描工具，可在渗透测试过程中帮助研究人员完成漏洞的枚举和扫描任务。而Sn1per专业版作为Xero
Security的额外报告插件，可给专业渗透测试人员、漏洞猎人和企业安全团队管理大型环境提供帮助。**

![1.png](https://image.3001.net/images/20181212/1544548039_5c0feec7c62d1.png!small)

## Sn1per专业版功能

### 专业的报告接口

![2.png](https://image.3001.net/images/20181212/1544548050_5c0feed2f1d05.png!small)

### 幻灯片形式查看报告截图

![3.png](https://image.3001.net/images/20181212/1544548057_5c0feed94f013.png!small)

### 可搜索可排序的DNS、IP及开放端口数据库

![4.png](https://image.3001.net/images/20181212/1544548072_5c0feee8bdb18.png!small)

### 主机分类报告

![5.png](https://image.3001.net/images/20181212/1544548088_5c0feef897612.png!small)

### 快速链接在线recon工具及Google Hacking查询

![6.png](https://image.3001.net/images/20181212/1544548110_5c0fef0ead254.png!small)

### 自定义单台主机的note文本

![7.png](https://image.3001.net/images/20181212/1544548124_5c0fef1ca1dde.png!small)

## 演示视频

视频地址：<https://asciinema.org/a/IDckE48BNSWQ8TV8yEjJjjMNm>

## Sn1per社区版功能：

> 自动收集基础recon（例如whois、ping和DNS等等）
>
> 针对目标域名自动启动Google Hacking查询
>
> 通过Nmap端口扫描自动化枚举开放端口
>
> 自动化爆破子域名、收集DNS信息和检测区域转移
>
> 自动化检测子域名劫持
>
> 针对开放端口自动化运行Nmap脚本
>
> 自动化运行Metasploit扫描和漏洞利用模块
>
> 自动化扫描所有常见的Web应用漏洞
>
> 自动化爆破所有的开放服务
>
> 自动化测试匿名FTP访问
>
> 自动化运行WPScan、Arachni和Nikto
>
> 自动化枚举NFS共享
>
> 自动化测试匿名LDAP访问
>
> 自动化枚举SSL/TLS密码、协议和漏洞
>
> 自动化枚举SNMP社区字符串、服务和用户
>
> 自动化列举SMB用户及共享，检测空会话，利用MS08-067
>
> 自动化测试开放X11服务器
>
> 执行高级主机/子网枚举
>
> 自动化收集目标站点截图
>
> 创建独立工作站空间存储所有的扫描输出

## 自动化PWN

> DrupalDrupalgedon2远程代码执行漏洞CVE-2018-7600
>
> GPON路由器远程代码执行漏洞CVE-2018-10561
>
> [Apache Struts
> 2](https://www.kitploit.com/search/label/Apache%20Struts)远程代码执行漏洞CVE-2017-5638
>
> ApacheStruts 2 远程代码执行漏洞CVE-2017-9805
>
> ApacheJakarta 远程代码执行漏洞CVE-2017-5638
>
> ShellshockGNU Bash远程代码执行漏洞CVE-2014-6271
>
> HeartBleedOpenSSL检测漏洞CVE-2014-0160
>
> MSWindows SMB远程代码执行漏洞MS08-067
>
> Webmin文件披露漏洞CVE-2006-3392
>
> [匿名FTP](https://www.kitploit.com/search/label/Anonymous%20FTP)访问
>
> PHPMyAdmin后门远程代码执行漏洞
>
> PHPMyAdmin认证绕过漏洞
>
> JBossJava反序列化远程代码执行漏洞

## Kali Linux安装

    
    
    ./install.sh

## Docker安装/构建

Docker安装:

    
    
     https://github.com/menzow/sn1per-docker

Docker构建:

    
    
    https://hub.docker.com/r/menzo/sn1per-docker/builds/bqez3h7hwfun4odgd2axvn4/

### 使用样例

    
    
    $docker pull menzo/sn1per-docker
    
    $docker run --rm -ti menzo/sn1per-docker sniper menzo.io

## 工具使用

    
    
    [*]NORMAL MODE
    
    sniper-t|--target <TARGET
    
     
    
    [*]NORMAL MODE + OSINT + RECON
    
    sniper-t|--target <TARGET -o|--osint -re|--recon
    
     
    
    [*]STEALTH MODE + OSINT + RECON
    
    sniper-t|--target <TARGET -m|--mode stealth -o|--osint -re|--recon
    
     
    
    [*]DISCOVER MODE
    
    sniper-t|--target <CIDR -m|--mode discover -w|--workspace<WORSPACE_ALIAS
    
     
    
    [*]SCAN ONLY SPECIFIC PORT
    
    sniper-t|--target <TARGET -m port -p|--port <portnum
    
     
    
    [*]FULLPORTONLY SCAN MODE
    
    sniper-t|--target <TARGET -fp|--fullportonly
    
     
    
    [*]PORT SCAN MODE
    
    sniper-t|--target <TARGET -m|--mode port -p|--port <PORT_NUM
    
     
    
    [*]WEB MODE - PORT 80 + 443 ONLY!
    
    sniper-t|--target <TARGET -m|--mode web
    
     
    
    [*]HTTP WEB PORT MODE
    
    sniper-t|--target <TARGET -m|--mode webporthttp -p|--port <port
    
     
    
    [*]HTTPS WEB PORT MODE
    
    sniper-t|--target <TARGET -m|--mode webporthttps -p|--port <port
    
     
    
    [*]ENABLE BRUTEFORCE
    
    sniper-t|--target <TARGET -b|--bruteforce
    
     
    
    [*]AIRSTRIKE MODE
    
    sniper-f|--file /full/path/to/targets.txt -m|--mode airstrike
    
     
    
    [*]NUKE MODE WITH TARGET LIST, BRUTEFORCE ENABLED, FULLPORTSCAN ENABLED, OSINTENABLED, RECON ENABLED, WORKSPACE & LOOT ENABLED
    
    sniper-f--file /full/path/to/targets.txt -m|--mode nuke -w|--workspace<WORKSPACE_ALIAS
    
     
    
    [*]ENABLE LOOT IMPORTING INTO METASPLOIT
    
    sniper-t|--target <TARGET
    
     
    
    [*]LOOT REIMPORT FUNCTION
    
    sniper-w <WORKSPACE_ALIAS --reimport
    
     
    
    [*]UPDATE SNIPER
    
    sniper-u|--update

样本报告：【[传送门](https://gist.github.com/1N3/8214ec2da2c91691bcbc)】

## 项目地址

> Sn1perv6.0：【[GitHub传送门](https://github.com/1N3/Sn1per)】

 *** 参考来源：[kitploit](https://www.kitploit.com/2018/11/sn1per-v60-automated-pentest-framework.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

