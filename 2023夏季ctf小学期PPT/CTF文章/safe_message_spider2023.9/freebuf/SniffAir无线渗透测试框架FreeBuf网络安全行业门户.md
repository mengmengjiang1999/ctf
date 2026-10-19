![SniffAir.png](https://image.3001.net/images/20181109/1541721629_5be4ce1de03f4.png!small)

**[SniffAir](https://github.com/Tylous/SniffAir)是一个开源的无线安全框架，可帮助你轻松解析被动收集的无线数据并发起复杂的无线攻击。此外，它还可以处理大型的或多个pcap文件，执行交叉检查和流量分析，以寻找潜在的安全漏洞。除了预先构建查询外，SniffAir还允许用户创建自定义的查询来分析存储在后端SQL数据库中的无线数据。SniffAir使用查询提取数据并将此用于无线[渗透测试](https://www.kitploit.com/search/label/Penetration%20Test)报告中。这些数据还可被用来作为模块设置复杂的无线攻击包含在SniffAir中。顺带一提，SniffAir框架是由[@Tyl0us](https://twitter.com/Tyl0us)和[@theDarracott](https://twitter.com/theDarracott)共同开发的。**

## 安装

SniffAir是基于Python 2.7开发的

已测试支持的系统包括Kali Linux，Debian和Ubuntu。

安装请运行setup.sh脚本

    
    
    $./setup.sh

## 使用

    
    
                                                                        % *        ., %                         
                                                                        % ( ,#     (..# %                        
        /@@@@@&,    *@@%        &@,    @@#    /@@@@@@@@@   [email protected]@@@@@@@@. ,/ # # (%%%* % (.(.  [email protected]@     &@@@@@@%.    
      [email protected]@&   *&@    %@@@@.      &@,    @@%    %@@,,,,,,,   ,@@,,,,,,,  .( % %  %%#  # % #   ,@@     @@(,,,#@@@.  
      %@%           %@@(@@.     &@,    @@%    %@@          ,@@          /* #   /*,   %.,,   ,@@     @@*     #@@  
      ,@@&          %@@ ,@@*    &@,    @@%    %@@          ,@@           .#   //#(,   (,    ,@@     @@*     &@%  
       [email protected]@@@@.      %@@  [email protected]@(   &@,    @@%    %@@%%%%%%*   ,@@%%%%%%#         (# ##.        ,@@     @@&%%%@@@%   
           *@@@@    %@@   [email protected]@/  &@,    @@%    %@@,,,,,,    ,@@,,,,,,.        %#####%        ,@@     @@(,,%@@%    
              @@%   %@@     @@( &@,    @@%    %@@          ,@@              %  (*/  #       ,@@     @@*    @@@   
              %@%   %@@      @@&&@,    @@%    %@@          ,@@             %  #  .# .#      ,@@     @@*     @@%  
     [email protected]@&/,,#@@@    %@@       &@@@,    @@%    %@@          ,@@            /(*       /(#     ,@@     @@*      @@# 
       *%@@@&*      *%#        ,%#     #%/    *%#           %%            #############.    .%#     #%.      .%% 
                                                                      (@Tyl0us & @theDarracott)
    
     >>  [default]# help
    Commands
    ========
    workspace                管理工作区（创建，列出，加载，删除）
    live_capture             启动有效的无线接口以收集要解析的无线pakcets（需要提供接口名称）
    offline_capture          开始使用pcap文件解析无线数据包。使用pcapdump会更好（需要提供完整路径）
    offline_capture_list     开始使用pcap文件列表解析无线数据包。使用pcapdump会更好（需要提供完整路径）
    query                    对活动工作区的内容执行查询
    help                     显示帮助菜单
    clear                    清屏
    show                     显示表的内容，所有表或可用模块的特定信息
    inscope                  添加ESSID到scope。inscope [ESSID]
    SSID_Info                显示与inscope SSIDS相关的所有信息（即所有BSSID，Channels 和 Encrpytion）
    use                      使用SniffAir模块
    info                     显示所选模块的所有变量信息
    set                      在模块中设置变量

首先，使用命令workspace create <workspace>或workspace load
<workspace>命令创建或加载新/现有的工作空间。查看现有工作空间，可以使用workspace list命令，删除工作空间可以使用workspace
delete <workspace>。

    
    
    >>  [default]# workspace
         Manages workspaces
     Command Option: workspaces [create|list|load|delete]
    >>  [default]# workspace create demo
    [+]  Workspace demo created

使用offline_capture
<pcap文件完整路径>命令，从pcap文件将数据加载到指定的工作空间。如果要加载pcap文件列表，请使用offline_capture_list
<包含pcap名称列表文件的完整路径>命令。使用live_capture <interface name>命令可以捕获实时的无线流量。

    
    
    >>  [demo]# offline_capture /root/sniffair/demo.pcapdump
     [+] Importing /root/sniffair/demo.pcapdump
     \
     [+] Completed
     [+] Cleaning Up Duplicates
     [+] ESSIDs Observed

##  **show 命令**

show命令将会为我们显示表内容，所有表或可用模块的特定信息。使用语法如下：

    
    
    >>  [demo]# show table AP
    +------+-----------+-------------------+-------------------------------+--------+-------+-------+----------+--------+
    |   ID | ESSID     | BSSID             | VENDOR                        |   CHAN |   PWR | ENC   | CIPHER   | AUTH   |
    |------+-----------+-------------------+-------------------------------+--------+-------+-------+----------+--------|
    |    1 | HoneyPot  | c4:6e:1f:##:##:## | TP-LINK TECHNOLOGIES CO. LTD. |      4 |   -17 | WPA2  | TKIP     | MGT    |
    |    2 | Demo      | 80:2a:a8:##:##:## | Ubiquiti Networks Inc.        |     11 |   -19 | WPA2  | CCMP     | PSK    |
    |    3 | Demo5ghz  | 82:2a:a8:##:##:## | Unknown                       |     36 |   -27 | WPA2  | CCMP     | PSK    |
    |    4 | HoneyPot1 | c4:6e:1f:##:##:## | TP-LINK TECHNOLOGIES CO. LTD. |     36 |   -29 | WPA2  | TKIP     | PSK    |
    |    5 | BELL456   | 44:e9:dd:##:##:## | Sagemcom Broadband SAS        |      6 |   -73 | WPA2  | CCMP     | PSK    |
    +------+-----------+-------------------+-------------------------------+--------+-------+-------+----------+--------+
     >>  [demo]# show SSIDS
    ---------    HoneyPot
    Demo
    HoneyPot1
    BELL456
    Hidden
    Demo5ghz
    ---------
query命令可根据指定参数显示唯一的数据集。query命令的使用语法与sql相同。

##  **Inscope**

inscope
<SSID>命令可用于将SSID添加到inscope表中，将所有相关数据加载到inscope_AP，inscope_proberequests和inscope_proberesponses表。要查看所有inscope
SSIDS的摘要，请运行SSID_Info命令。

##  **模块**

模块可用于分析工作空间中包含的数据，或使用<module name>命令执行无线攻击。对于某些模块，可能需要设置其他变量。可以使用set命令set
<variable name> <variable value>进行设置：

    
    
    >>  [demo]# show modules
    Available Modules
    =================
    [+] Auto EAP - Automated Brute-Force Login Attack Against EAP Networks
    [+] Auto PSK - Automated Brute-Force Passphrase Attack Against PSK Networks
    [+] AP Hunter - Discover Access Point Within  a Certain Range Using a Specific Type of Encrpytion
    [+] Captive Portal - Web Based Login Portal to Capture User Entered Credentials (Runs as an OPEN Network)
    [+] Certificate Generator - Generates a Certificate Used by Evil Twin Attacks
    [+] Exporter - Exports Data Stored in a Workspace to a CSV File
    [+] Evil Twin - Creates a Fake Access Point, Clients Connect to Divulging MSCHAP Hashes or Cleartext Passwords
    [+] Handshaker - Parses Database or .pcapdump Files Extracting the Pre-Shared Handshake for Password Guessing (Hashcat or JTR Format)
    [+] Mac Changer - Changes The Mac Address of an Interface
    [+] Probe Packet - Sends Out Deauth Packets Targeting SSID(s)
    [+] Proof Packet - Parses Database or .pcapdump Files Extracting all Packets Related to the Inscope SSDIS
    [+] Hidden SSID - Discovers the Names of HIDDEN SSIDS
    [+] Suspicious AP - Looks for Access Points that: Is On Different Channel, use a Different Vendor or Encrpytion Type Then the Rest of The Network
    [+] Wigle Search SSID - Queries wigle for SSID (i.e. Bob's wifi)
    [+] Wigle Search MAC - Queries wigle for all observations of a single mac address
     >>  [demo]# 
     >>  [demo]# use Captive Portal
     >>  [demo][Captive Portal]# info
    Globally Set Varibles
    =====================
     Module: Captive Portal
     Interface: 
     SSID: 
     Channel: 
     Template: Cisco (More to be added soon)
     >>  [demo][Captive Portal]# set Interface wlan0
     >>  [demo][Captive Portal]# set SSID demo
     >>  [demo][Captive Portal]# set Channel 1
     >>  [demo][Captive Portal]# info
    Globally Set Varibles
    =====================
     Module: Captive Portal
     Interface: wlan0
     SSID: demo
     Channel: 1
     Template: Cisco (More to be added soon)
     >>  [demo][Captive Portal]# 

设置所有变量后，执行exploit或run命令运行攻击。

## 导出

使用Exporter模块导出存储在工作空间表中的所有信息到指定路径。

 ** *参考来源：.[kitploit](https://amp.kitploit.com/2018/11/sniffair-framework-for-wireless.html?amp=1&m=1)，FB小编secist编译，转载请注明来自FreeBuf.COM**

