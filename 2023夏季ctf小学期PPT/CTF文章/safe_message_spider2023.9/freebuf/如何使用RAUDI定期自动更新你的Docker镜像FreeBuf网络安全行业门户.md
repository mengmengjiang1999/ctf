![](https://image.3001.net/images/20220121/1642699884_61e99c6cad76c86f32272.jpeg!small)

## 关于RAUDI

RAUDI是一款功能强大的Docker镜像自动更新工具，RAUDI基于GitHub
Actions实现其功能，在该工具的帮助下，广大研究人员可以轻松地定期自动更新Docker镜像，并保持你所使用的Docker镜像为最新版本。

RAUDI可以帮助我们避免通过手动的方式创建和管理大量Docker镜像。且每次更新软件时，如果要使用最新功能，则需要更新Docker映像，而且依赖组件可能会无法正常工作。这样做既麻烦又耗时，而RAUDI便应运而生。

## 工具要求

> Python 3.x
>
> Docker

## 工具安装

该工具的安装过程也十分简单，我们只需要使用下列命令将该项目源码克隆至本地，并安装相关的依赖组件即可：

    
    
    git clone https://github.com/cybersecsi/RAUDI
    
    cd RAUDI
    
    pip install -r requirements.txt

## 工具测试

如需运行测试，我们还得安装pytest：

    
    
    pip install pytest

然后运行下列命令即可执行测试：

    
    
    pytest -s

或

    
    
    python -m pytest -s

## 本地使用

我们可以通过多种不同的命令参数选项来运行RAUDI。在本地使用RAUDI之前，我们需要创建一个.env文件（可以直接拷贝.env.sample文件），并添加你的GitHub个人访问令牌以避免访问频率限制。对于未经身份验证的用户，GitHub每小时最多允许60个请求，而经过身份验证的用户每小时最多允许15000个请求。

## 工具执行模式

### 常规模式

在这个模式下，RAUDI会尝试构建所有需要的工具，操作命令如下：

    
    
    python3 ./raudi.py --all

### 单独构建

在该模式下，RAUDI会尝试构建指定的工具，操作命令如下：

    
    
    python3 ./raudi.py --single <tool_name>

其中的“tool_name”必须是项目tools目录中的工具名称。

### 显示工具

如果你想要查看所有可用的工具，可以使用下列命令：

    
    
    python3 ./raudi.py --list

## 工具选项

> \--push：是否自动push至Docker Hub（默认为False）
>
> \--remote：在构建之前是否检测Docker Hub（默认为False）
>
> \--force：如果检测到了相同的镜像标签名，是否要强制构建（默认为False）

## 可用工具列表

 ** **工具名称****

|

 ** **Docker镜像****

|

 ** **源地址****  
  
---|---|---  
  
Altdns

|

secsi/altdns

|

<https://github.com/infosec-au/altdns>  
  
Apktool

|

secsi/apktool

|

<https://github.com/iBotPeaches/Apktool>  
  
Arjun

|

secsi/arjun

|

<https://github.com/s0md3v/Arjun>  
  
bfac

|

secsi/bfac

|

<https://github.com/mazen160/bfac>  
  
CloudFail

|

secsi/cloudfail

|

<https://github.com/m0rtem/CloudFail>  
  
CMSeeK

|

secsi/cmseek

|

<https://github.com/Tuhinshubhra/CMSeeK>  
  
Crowbar

|

secsi/crowbar

|

<https://github.com/galkan/crowbar>  
  
datasploit

|

secsi/datasploit

|

<https://github.com/DataSploit/datasploit>  
  
dex2jar

|

secsi/dex2jar

|

<https://github.com/pxb1988/dex2jar>  
  
dirb

|

secsi/dirb

|

<http://dirb.sourceforge.net/>  
  
dirhunt

|

secsi/dirhunt

|

<https://github.com/Nekmo/dirhunt>  
  
dirsearch

|

secsi/dirsearch

|

<https://github.com/maurosoria/dirsearch>  
  
dnscan

|

secsi/dnscan

|

<https://github.com/rbsec/dnscan>  
  
Dorks Eye

|

secsi/dorks-eye

|

<https://github.com/BullsEye0/dorks-eye>  
  
dvcs-ripper

|

secsi/dvcs-ripper

|

<https://github.com/kost/dvcs-ripper>  
  
EyeWitness

|

secsi/eyewitness

|

<https://github.com/FortyNorthSecurity/EyeWitness>  
  
fast-recon

|

secsi/fast-recon

|

<https://github.com/DanMcInerney/fast-recon>  
  
ffuf

|

secsi/ffuf

|

<https://github.com/ffuf/ffuf>  
  
fierce

|

secsi/fierce

|

<https://github.com/mschwager/fierce>  
  
Findsploit

|

secsi/findsploit

|

<https://github.com/1N3/Findsploit>  
  
GetJS

|

secsi/getjs

|

<https://github.com/003random/getJS>  
  
Gitrob

|

secsi/gitrob

|

<https://github.com/michenriksen/gitrob>  
  
GitTools

|

secsi/gittools

|

<https://github.com/internetwache/GitTool>  
  
gobuster

|

secsi/gobuster

|

<https://github.com/OJ/gobuster>  
  
GoogD0rker

|

secsi/googd0rker

|

<https://github.com/ZephrFish/GoogD0rker>  
  
GoSpider

|

secsi/gospider

|

<https://github.com/jaeles-project/gospider>  
  
Ground control

|

secsi/ground-control

|

<https://github.com/jobertabma/ground-control>  
  
Hakrawler

|

secsi/hakrawler

|

<https://github.com/hakluke/hakrawler>  
  
hakrevdns

|

secsi/hakrevdns

|

<https://github.com/hakluke/hakrevdns>  
  
hashID

|

secsi/hashid

|

<https://github.com/psypanda/hashID>  
  
httprobe

|

secsi/httprobe

|

<https://github.com/tomnomnom/httprobe>  
  
hydra

|

secsi/hydra

|

<https://github.com/vanhauser-thc/thc-hydra>  
  
impacket

|

secsi/impacket

|

<https://github.com/SecureAuthCorp/impacket>  
  
JoomScan

|

secsi/joomscan

|

<https://github.com/OWASP/joomscan>  
  
The JSON Web Token Toolkit

|

secsi/jwt_tool

|

<https://github.com/ticarpi/jwt_tool>  
  
knock

|

secsi/knockpy

|

<https://github.com/guelfoweb/knock>  
  
LFI Suite

|

secsi/lfisuite

|

<https://github.com/D35m0nd142/LFISuite>  
  
LinkFinder

|

secsi/linkfinder

|

<https://github.com/GerbenJavado/LinkFinder>  
  
MASSCAN

|

secsi/masscan

|

<https://github.com/robertdavidgraham/masscan>  
  
MassDNS

|

secsi/massdns

|

<https://github.com/blechschmidt/massdns>  
  
Memcrashed DDoS Exploit

|

secsi/memcrashed

|

<https://github.com/649/Memcrashed-DDoS-Exploit>  
  
nikto

|

secsi/nikto

|

<https://github.com/sullo/nikto>  
  
nmap

|

secsi/nmap

|

<https://github.com/nmap/nmap>  
  
oxml_xxe

|

secsi/oxml_xxe

|

<https://github.com/BuffaloWill/oxml_xxe>  
  
Pagodo

|

secsi/pagodo

|

<https://github.com/opsdisk/pagodo>  
  
photon

|

secsi/photon

|

<https://github.com/s0md3v/Photon>  
  
PivotSuite

|

secsi/pivotsuite

|

<https://github.com/RedTeamOperations/PivotSuite>  
  
psalm

|

secsi/psalm

|

<https://github.com/vimeo/psalm>  
  
pureDNS

|

secsi/puredns

|

<https://github.com/d3mondev/puredns>  
  
Race The Web

|

secsi/race-the-web

|

<https://github.com/TheHackerDev/race-the-web>  
  
RestfulHarvest

|

secsi/restfulharvest

|

<https://github.com/laramies/theHarvester>  
  
Retire.js

|

secsi/retire

|

<https://github.com/RetireJS/retire.js>  
  
RouterSploit

|

secsi/routersploit

|

<https://github.com/threat9/routersploit>  
  
Sandcastle

|

secsi/sandcastle

|

<https://github.com/0xSearches/sandcastle>  
  
scanless

|

secsi/scanless

|

<https://github.com/vesche/scanless>  
  
spyse.py

|

secsi/spysepy

|

<https://github.com/zeropwn/spyse.py>  
  
sqlmap

|

secsi/sqlmap

|

<https://github.com/sqlmapproject/sqlmap>  
  
Striker

|

secsi/striker

|

<https://github.com/s0md3v/Striker>  
  
Subfinder

|

secsi/subfinder

|

<https://github.com/projectdiscovery/subfinder>  
  
Subjack

|

secsi/subjack

|

<https://github.com/haccer/subjack>  
  
Sublist3r

|

secsi/sublist3r

|

<https://github.com/aboul3la/Sublist3r>  
  
theHarvester

|

secsi/theharvester

|

<https://github.com/laramies/theHarvester>  
  
WAFW00F

|

secsi/wafw00f

|

<https://github.com/EnableSecurity/wafw00f>  
  
waybackpy

|

secsi/waybackpy

|

<https://github.com/akamhy/waybackpy>  
  
WhatWeb

|

secsi/whatweb

|

<https://github.com/urbanadventurer/WhatWeb>  
  
xray

|

secsi/xray

|

<https://github.com/evilsocket/xray>  
  
XXEinjector

|

secsi/xxeinjector

|

<https://github.com/enjoiz/XXEinjector>  
  
## 工具使用样例

### 常规使用

    
    
    docker run -it --rm secsi/<tool> <command>

### 特殊使用

    
    
    docker run -it --rm -v <wordlist_src_dir>:<wordlist_container_dir> secsi/dirb <url> <wordlist_container_dir>/<wordlist_file>

## 许可证协议

本项目的开发与发布遵循[ _GNU_ __ _GPL_ __ _v_
_3_](https://github.com/cybersecsi/RAUDI/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **RAUDI：** 【[ _GitHub传送门_](https://github.com/cybersecsi/RAUDI)】

