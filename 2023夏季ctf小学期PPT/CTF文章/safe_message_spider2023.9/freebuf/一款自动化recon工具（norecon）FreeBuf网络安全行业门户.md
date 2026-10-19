## 款简介

闲来没事，做一个自动化recon的工具，简化操作流程。可以对域名或ip进行whois查询，dns记录查询，ip端口扫描，http屏幕快照。

最终生成markdown格式的报告，可使用[Obsidian](https://obsidian.md/)或vscode的[markdown
notes插件](https://marketplace.visualstudio.com/items?itemName=kortina.vscode-markdown-notes)打开，借助双向链接功能，方便跳转查看。

## 依赖的程序

### amass

子域名查找 [下载地址](https://github.com/OWASP/Amass/releases)

### masscan

扫描全部端口，发现开放端口。

### nmap

服务扫描，针对masscan发现的端口进行具体的服务扫描。

### aquatone

屏幕快照，由于需要对每个目标(域名或ip)单独进行快照，然后再合并，fork原版做了简单的修改，提供了session保存与合并的功能,下载地址:
[aquatone](https://github.com/ntestoc3/aquatone/releases)

## 安装程序

使用python3环境：

    
    
    pip install norecon

## 使用ansible批量安装

不喜欢手动安装的话，可以使用ansible进行自动化安装,使用这个[playbooks](https://github.com/ntestoc3/playbooks)仓库：

git clone 项目到本地,配置好ansible，设置好主机项，然后执行：

    
    
    ansible-playbook norecon.yml

即可在指定的主机上安装好依赖程序及norecon包。

## 使用方法

命令行参数：

> usage: norecon [-h] [--amass-timeout AMASS_TIMEOUT] [--ip-scan-timeout
> IP_SCAN_TIMEOUT]  
> [--screenshot-timeout SCREENSHOT_TIMEOUT] [--masscan-rate MASSCAN_RATE]  
> [--scan-cdn-ip] [--overwrite] [-ss SCREEN_SESSION] [-e [EXCLUDE]] -p  
> PROJECT_DIR [-t [TARGETS]] [-v [VERBOSE]]  
> [target [target ...]]
>
> 针对目标进行recon
>
> positional arguments:  
> target 要扫描的目标，可以是域名或ip地址
>
> optional arguments:  
> -h, --help show this help message and exit  
> \--amass-timeout AMASS_TIMEOUT  
> amass扫描超时时间(分) (default: 60)  
> \--ip-scan-timeout IP_SCAN_TIMEOUT  
> ip扫描超时时间(秒) (default: 600)  
> \--screenshot-timeout SCREENSHOT_TIMEOUT  
> 屏幕快照超时时间(秒) (default: 1000)  
> \--masscan-rate MASSCAN_RATE  
> masscan扫描速率 (default: 1000)  
> \--scan-cdn-ip 是否对cdn ip进行端口扫描 (default: False)  
> \--overwrite 是否强制重新扫描(如果为False,则扫描过的项目不再重新扫描) (default: False  
> )  
> -ss SCREEN_SESSION, --screen-session SCREEN_SESSION  
> 输出屏幕快照的session文件名 (default: screen)  
> -e [EXCLUDE], --exclude [EXCLUDE]  
> 包含排除列表的文件,可以是域名或ip,支持glob格式匹配(*?)  
> -p PROJECT_DIR, --project-dir PROJECT_DIR  
> 项目根目录  
> -t [TARGETS], --targets [TARGETS]  
> 输入的目标  
> -v [VERBOSE], --verbose [VERBOSE]  
> 日志输出级别(0,1,2) (default: 0)

最简单的用法：

    
    
    norecon -p 项目保存目录　域名或ip

如果域名比较多，可以增大--amass-timeout参数，以收集更多的子域名。

比如测试yahoo,支持一级域名或子域名。

    
    
    norecon -v -p yahoo --amass-timeout 60 yahoo.com engadget.com login.aol.com

如果中途中断，继续执行以上命令，会自动跳过已经扫描的部分．可使用--overwrite强制重新扫描。

也可以在项目执行完毕后再添加ip或域名,或只进行ip扫描(支持cidr子网或ip范围)：

    
    
    norecon -v -p yahoo 202.165.107.00/28 119.161.10.15-119.161.10.40 106.10.236.40

扫描完成后，结果在项目目录下，按whois,domain,ip分类存放为json格式，可以自己进行分析，

也可以生成markdown格式的报告:

    
    
    noreport -v yahoo

项目目录下的screen/screen.html为aquatone的输出报告，包含了所有屏幕快照的域名或ip。

## 报告截图

生成报告后使用Obsidian打开项目目录，查看报告结果 ,主要是方便跳转和查看反向引用。

![使用Obsidian查看noreport输出的报告](https://image.3001.net/images/20200909/1599656005.gif)

## 附带的单独工具

### noresolvers

域名解析服务器查询工具，根据可用性和超时时间获取域名解析服务器列表．按响应时间排序。

使用方法,可用性为0.9,响应时间为3秒内，输出解析服务器列表到resolve：

    
    
    noresolvers -r 0.9 -t 3 -o resolve

### domainvalid

检测一级域名是否有效，即含有ns记录，是正常使用的一级域名。

可以指定resolvers文件，即noresolvers输出的域名解析服务器文件。

### norecords

获取一个域名的所有解析记录。

### wildomains

获取一个通配域名的所有一级域名，比如baidu.*,会查找所有可能的tld后缀，找到还在使用的一级域名．

可以使用tld文件指定要查找的后缀，如果不指定，会查找大量tld,速度比较慢。

### nosubsfinder

从网页查询子域名。

### noamass

调用amass查询子域名。

### nowhois

whois查询域名或ip。

### nonmap

调用masscan和nmap进行服务扫描。

### noffuf

调用ffuf进行路径爆破。

### noscreen

调用aquatone进行屏幕快照。

### nowx

发送微信消息,借助[微信消息推送服务](http://wxpusher.zjiecode.com/docs/)发送消息，可以实现命令执行完毕后发送微信消息通知。

第一次运行输入nowx执行，根据提示进行配置：

    
    
    ➜  sub-domains git:(master) ✗ nowx
    未发现token配置
    访问 http://wxpusher.zjiecode.com/admin/app/list 创建token.
    输入申请的APP_TOKEN:[粘贴页面申请的token]
    
    网页打开下面的网址，微信扫码关注以接收消息：
    https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=xxxxxx

然后可以在执行时带上消息参数发送消息：

    
    
    nowhois bing.com  ; nowx whois执行完毕,返回代码:$?

上面的命令在nowhois执行完毕后，由nowx发送微信消息，通知命令完成及nowhois的返回代码．注意两个命令之间使用;分割。

## 最后

[项目页面](https://github.com/ntestoc3/norecon)，欢迎issue或pr。

