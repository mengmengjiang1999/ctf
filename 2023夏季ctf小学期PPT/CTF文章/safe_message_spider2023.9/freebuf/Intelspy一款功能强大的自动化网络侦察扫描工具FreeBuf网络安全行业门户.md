![](https://image.3001.net/images/20200805/1596638640.png!small)

## Intelspy

Intelspy是一款功能强大的自动化网络侦察扫描工具，它能够执行自动化的网络侦察扫描任务，并收集网络情报信息。

简而言之，Intelspy是一款多线程的网络情报工具，该工具能够执行自动化的网络服务枚举、活动主机检测扫描、端口扫描、服务枚举扫描、Web内容扫描、暴力破解攻击以及离线攻击搜索等任务。除此之外，该工具害能够针对每一个检测到的服务，使用大量不同的工具来进行进一步的枚举扫描。

## 功能介绍

  * 以IP地址、IP范围（CIDR标记）和可解析主机名的形式扫描多个目标。
  * 同时扫描多个目标。
  * 检测IP地址范围（CIDR）网络中的活动主机。
  * 可自定义的端口扫描配置文件和服务枚举命令。
  * 自动创建用于结果收集和报告的目录结构。
  * 能够记录执行的每个命令。
  * 生成包含要手动运行的命令的Shell脚本。
  * 以txt和markdown格式提取重要信息，以便执行进一步检查。
  * 将数据存储到SQLite数据库中。
  * 生成HTML格式的扫描报告。

## 工具要求

Intelspy的正常运行需要依赖于下列工具：

  * Python 3 (sudo apt install python3)
  * Linux (建议Kali Linux)
  * toml (<https://github.com/toml-lang/toml>)
  * seclists (<https://github.com/danielmiessler/SecLists>)
  * curl (必须) (sudo apt install curl)
  * enum4linux (必须) (sudo apt install enum4linux)
  * gobuster (必须) (sudo apt install gobuster)
  * hydra (可选项) (sudo apt install hydra)
  * ldapsearch (可选项) (sudo apt install ldap-utils)
  * medusa (可选项) (sudo apt install medusa)
  * nbtscan (必须) (sudo apt install nbtscan)
  * nikto (必须) (sudo apt install nikto)
  * nmap (必须) (sudo apt install nmap)
  * onesixtyone (必须) (sudo apt install onesixtyone)
  * oscanner (可选项) (sudo apt install oscanner)
  * pandoc (必须) (sudo apt install pandoc)
  * patator (可选项) (sudo apt install patator)
  * showmount (必须) ('system tool ')
  * smbclient (必须) (sudo apt install smbclient)
  * smbmap (必须) (sudo apt install smbmap)
  * smtp-user-enum (必须) (sudo apt install smtp-user-enum)
  * snmpwalk (必须) (sudo apt install snmp)
  * sslscan (必须) (sudo apt install sslscan)
  * svwar (必须) (sudo apt install sipvicious)
  * tnscmd10g (必须) (sudo apt install tnscmd10g)
  * whatweb (必须) (sudo apt install whatweb)
  * wkhtmltoimage (必须) (<https://github.com/wkhtmltopdf/wkhtmltopdf/>)
  * wpscan (可选项) (sudo apt install wpscan)

## 工具安装

如果用户不想手动安装上述工具的话，可以先使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/maldevel/intelspy.git

接下来，运行下列命令来安装工具依赖组件：

    
    
    pip3 install -r requirements.txt

## 工具使用

    
    
    $ python3 intelspy.py -h
    
     
    
     ___               __        
    
      |  ._ _|_  _  | (_  ._     
    
     _|_ | | |_ (/_ | __) |_) \/
    
                          |   /  
    
                                    
    
    IntelSpy v2.0 - Perform automated network reconnaissance scans to gather network intelligence.
    
    IntelSpy is an open source tool licensed under GPLv3.
    
    Written by: @maldevel | Logisek ICT
    
    Web: https://logisek.com | https://pentest-labs.com
    
    Project: https://github.com/maldevel/intelspy
    
     
    
     
    
    usage: intelspy.py [-h] [-ts TARGET_FILE] -p PROJECT_NAME -w WORKING_DIR
    
                       [--exclude <host1[,host2][,host3],...>] [-s SPEED]
    
                       [-ct <number>] [-cs <number>] [--profile PROFILE_NAME]
    
                       [--livehost-profile LIVEHOST_PROFILE_NAME]
    
                       [--heartbeat HEARTBEAT] [-v]
    
                       [targets [targets ...]]
    
     
    
    positional arguments:
    
      targets               IP addresses (e.g. 10.0.0.1), CIDR notation (e.g.
    
                            10.0.0.1/24), or resolvable hostnames (e.g.
    
                            example.com) to scan.
    
     
    
    optional arguments:
    
      -h, --help            显示工具帮助信息并退出
    
      -ts TARGET_FILE, --targets TARGET_FILE
    
                          从文件中读取扫描目标
    
      -p PROJECT_NAME, --project-name PROJECT_NAME
    
                            设置项目名称
    
      -w WORKING_DIR, --working-dir WORKING_DIR
    
                            指定工作目录
    
      --exclude <host1[,host2][,host3],...>
    
                            排除主机/网络
    
      -s SPEED, --speed SPEED
    
                            0-5, 设置扫描速度，数字越高速度越快，默认为4
    
      -ct <number>, --concurrent-targets <number>
    
                            同时扫描的最大主机数量，默认为5
    
      -cs <number>, --concurrent-scans <number>
    
                            每个目标主机最大的扫描数量，默认为10
    
      --profile PROFILE_NAME
    
                            设置端口扫描配置，默认为port-scan-profiles.toml
    
      --livehost-profile LIVEHOST_PROFILE_NAME
    
                            设置活动主机扫描配置，默认为live-host-scan-profiles.toml
    
      --heartbeat HEARTBEAT
    
                            指定任务状态消息的心跳间隔，默认为60秒
    
      -v, --verbose            启用Verbose输出模式

## 工具使用样例

### 扫描单个目标：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ 192.168.10.15
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ 192.168.10.15 -v
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ 192.168.10.15 -vv
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ 192.168.10.15 -vvv

### 扫描一个主机名：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ example.com

### 扫描一个网络范围（CIDR）：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ 192.168.10.0/24

### 扫描多个目标（以逗号分隔）：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ 192.168.10.15 192.168.10.0/24 example.com

### 扫描文件中的目标：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ -ts /home/user/targets.txt

### 排除单个不需要扫描的主机：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ --exclude 192.168.10.9 192.168.10.0/24

### 排除多个不需要扫描的主机：

    
    
    sudo python3 intelspy.py -p MyProjectName -w /home/user/pt/projects/ --exclude 192.168.10.9,192.168.10.24 192.168.10.0/24

## 项目地址

Intelspy：【[ _GitHub传送门_](https://github.com/maldevel/intelspy)】

