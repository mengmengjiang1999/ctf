![Goscan](https://image.3001.net/images/20190227/1551264500_5c766af4651a5.png!small)  

**GoScan是一款交互式网络扫描客户端，可用来执行主机扫描、端口扫描和服务枚举等任务。它不仅可在时间有限的情况下完成高难度任务，而且还支持进行专业的安全管理。**

GoScan还特别适用于不稳定的环境，例如网络连接不稳定等情况，因为在触发扫描执行之后它会在一个SQLite数据库中维护其扫描状态。扫描任务（与主线程分离）全部在后台执行，所以即便是连接中断，GoScan也可以异步上传扫描结果。这也就意味着，我们可以在任何一个扫描阶段将数据导入至GoScan中，而且在出现问题时无需再从头开始整个流程。

除此之外，服务枚举阶段还集成了很多强大的工具，例如EyeWitness、Hydra和nikto等等，其中的每一款工具都针对特定的服务进行了定制修改。

![Goscan](https://image.3001.net/images/20190227/1551264911_5c766c8f2b6eb.jpg!small)

## 工具安装

### 源码安装（推荐）

大家可以直接从该项目的Release页面获取工具源码：【[Release页面](https://github.com/marco-lancini/goscan/releases)】。

    
    
    #Linux (64bit)
    $wgethttps://github.com/marco-lancini/goscan/releases/download/v2.3/goscan_2.3_linux_amd64.zip
    $unzip goscan_2.3_linux_amd64.zip
     
    #Linux (32bit)
    $wgethttps://github.com/marco-lancini/goscan/releases/download/v2.3/goscan_2.3_linux_386.zip
    $unzip goscan_2.3_linux_386.zip
     
    #After that, place the executable in your PATH
    $chmod +x goscan
    $sudo mv ./goscan /usr/local/bin/goscan

### 源码构建

    
    
    $ git clone https://github.com/marco-lancini/goscan.git
    $ cd goscan/goscan/
    $make setup
    $make build

大家可以使用make命令和cross命令来添加多平台支持：

    
    
    $make cross

## Docker

    
    
    $ git clone https://github.com/marco-lancini/goscan.git
    $ cd goscan/
    $ docker-compose up --build

## 工具使用

GoScan支持网络枚举中的主要操作任务：

![Goscan](https://image.3001.net/images/20190227/1551265015_5c766cf793b7a.png!small)  

**步骤** **** |  **命令** ****  
---|---  
1\. **Load targets** |  通过CLI添加单个目标（必须是有效的CIDR）：load target SINGLE <IP/32>
从text文件或文件夹上传多个目标：load target MULTI <path-to-file>  
2\. **Host Discovery** |  执行Ping Sweep：sweep <TYPE> <TARGET> 或加载之前的扫描结果：
通过CLI添加一台活动主机：load alive SINGLE <IP> 从text文件或文件夹上传多个活动主机：load alive MULTI
<path-to-file>  
3\. **Port Scanning** |  执行端口扫描： portscan <TYPE> <TARGET>
或从XML文件或文件夹上传nmap扫描结果：load portscan <path-to-file>  
4\. **Service Enumeration** |  Dry Run：enumerate <TYPE> DRY <TARGET>
枚举检测到的设备：enumerate <TYPE> <POLITE/AGGRESSIVE> <TARGET>  
5\. **Special Scans** |  _EyeWitness_ 获取网站、RDP服务和VNC服务器信息截图：special eyewitness
EyeWitness.py需要在system路径下 从枚举数据中提取（Windows）域名信息 special domain
<users/hosts/servers> _DNS_ 枚举DNS (nmap, dnsrecon, dnsenum)：special dns
DISCOVERY <domain> 爆破DNS：special dns BRUTEFORCE <domain> 反向爆破DNS：special dns
BRUTEFORCE_REVERSE <domain> <base_IP>  
**Utils** |  显示扫描结果：show <targets/hosts/ports> 通过加载配置文件完成自动配置： set config_file
<PATH> 修改输出目录（默认为~/goscan）：set output_folder <PATH> 修改默认nmap_switches ：set
nmap_switches <SWEEP/TCP_FULL/TCP_STANDARD/TCP_VULN/UDP_STANDARD> <SWITCHES>
修改默认字典：set_wordlists <FINGER_USER/FTP_USER/...> <PATH>  
  
## 外部工具整合

服务枚举阶段当前支持下列整合工具：

**功能** **** |  **整合工具** ****  
---|---  
ARP |  nmap  
DNS |  nmap dnsrecon dnsenum host  
FINGER |  nmap finger-user-enum  
FTP |  nmap ftp-user-enum hydra [AGGRESSIVE]  
HTTP |  nmap nikto dirb EyeWitness sqlmap [AGGRESSIVE] fimap [AGGRESSIVE]  
RDP |  nmap EyeWitness  
SMB |  nmap enum4linux nbtscan samrdump  
SMTP |  nmap smtp-user-enum  
SNMP |  nmap snmpcheck onesixtyone snmpwalk  
SSH |  hydra [AGGRESSIVE]  
SQL |  nmap  
VNC |  EyeWitness  
  
### 项目地址

GoScan：【[GitHub传送门](https://github.com/marco-lancini/goscan)】

### 许可证协议

GoScan支持MIT许可证协议。

 *** 参考来源：[goscan](https://github.com/marco-lancini/goscan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

