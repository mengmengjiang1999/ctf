![](https://image.3001.net/images/20210309/1615278927_6047334fbdbd07f7b7175.png!small)

## **简介**

Snort是一个多平台(Multi-Platform)，实时(Real-Time)流量分析，网络IP数据包(Pocket)记录等特性的强大的网络入侵检测/防御系统(Network Intrusion
Detection/Prevention System)，即NIDS/NIPS。

Snort采用规则匹配机制检测网络分组是否违反了事先配置的安全策略。安装在一台主机上就可以监测整个共享网段，一旦发现入侵和探测行为，即有将报警信息发送到系统日志、报警文件或控制台屏幕等多种实时报警方式。Snort不仅能够检测各种网络攻击，还具有网络分组采集、分析和日志记录功能。相对于昂贵与庞大的商用产品而言，Snort
具有系统规模小、容易安装、容易配置、规则灵活和插件（plug-in）扩展等诸多优点。

##  **组成**

Snort主要由分组协议分析器、入侵检测引擎、日志记录和报警模块组成。协议分析器的任务就是对协议栈上的分组进行协议解析，以便提交给入侵检测引擎进行规则匹配。入侵检测引擎根据规则文件匹配分组特征，当分组特征满足检测规则时，触发指定的响应操作。日志记录将解析后的分组以文本或
Tcpdump 二进制格式记录到日志文件，文本格式便于分组分析，二进制格式提高记录速度。报警信息可以发送到系统日志；也可以采用文本或 Tcpdump
二进制格式发送到报警文件；也容许选择关闭报警操作。记录到报警文件的报警信息有完全和快速两种方式，完全报警记录分组首部所有字段信息和报警信息，而快速报警只记录分组首部部分字段信息。

    
    
    环境介绍：
    虚拟机：Centos7 
    Snort官网：https://www.snort.org/downloads    #下载dap和snort
    dap:https://www.snort.org/downloads/snort/daq-2.0.7.tar.gz
    snort:https://www.snort.org/downloads/snort/snort-2.9.17.tar.gz

![1615278971_6047337b07ef304d0b01b.png!small](https://image.3001.net/images/20210309/1615278971_6047337b07ef304d0b01b.png!small)

    
    
    Centos7最小化安装--开启网络
    1、ip addr    #查看网卡名称
    2、cd /etc/sysconfig/network-scripts/    #进入网卡配置文件的目录
    3、vi ifcfg-enXXX
    4、找到ONBOOT=no ，修改为ONBOOT=yes然后保存退出
    5、service network restart #重启网卡服务，不行的话用systemctl restart network
    6、ip addr #查看是否分配到IP地址
    7、yum install net-tools    #安装net-tools包，该包提供ifconfig命令
    8、ifconfig        #确认IP，方便通过SSH软件进行登陆操作
    
    
    Snort相关依赖下载及安装
    yum install -y gcc flex bison zlib zlib-devel libpcap libpcap-devel pcre pcre-devel libdnet libdnet-devel tcpdump openssl openssl-devel
    wget https://www.snort.org/downloads/snort/daq-2.0.7.tar.gz
    wget https://www.snort.org/downloads/snort/snort-2.9.17.tar.gz
    wget http://luajit.org/download/LuaJIT-2.0.5.tar.gz
    
    #解压缩到/usr/local/下
    tar -zxvf daq-2.0.7.tar.gz -C /usr/local/
    tar -zxvf snort-2.9.17.tar.gz -C /usr/local/
    tar -zxvf LuaJIT-2.0.5.tar.gz -C /usr/local/
    
    cd /usr/local/
    #daq安装
    cd daq-2.0.7/
    ./configure && make && sudo make install
    #LuaJIT安装
    cd LuaJIT-2.0.5/
    make install
    #snort安装
    cd snort-2.9.17/
    ./configure --enable-sourcefire && make && sudo make install
    
    
    #创建Snort目录：
    mkdir rules
    mkdir rules/iplists
    mkdir /usr/local/lib/snort_dynamicrules
    mkdir so_rules
    
    #创建一些存储规则和ip列表的文件
    touch rules/iplists/black_list.rules
    touch rules/iplists/white_list.rules
    touch rules/local.rules
    touch sid-msg.map
    
    #创建日志目录：
    mkdir /var/log/snort
    mkdir /var/log/snort/archived_logs
    
    #修改配置文件，将 HOME_NET 更改为自己主机所在的IP段
    vi /usr/local/snort-2.9.17/etc
    ipvar HOME_NET 192.168.0.0/24    #在45行，输入：set number可显示行号
    
    var RULE_PATH /usr/local/snort-2.9.17/rules
    var SO_RULE_PATH /usr/local/snort-2.9.17/so_rules
    var PREPROC_RULE_PATH /usr/local/snort-2.9.17/preproc_rules
    var WHITE_LIST_PATH /usr/local/snort-2.9.17/rules/iplists
    var BLACK_LIST_PATH /usr/local/snort-2.9.17/rules/iplists
    
    include $RULE_PATH/local.rules    #在550行左右，开启local.rules，默认是开启的

注：实际上在include $RULE_PATH/local.rules下面还开启了很多规则，由于未配置，因此运行时会报错，需要注释掉

![1615279044_604733c4b42b267c7cac2.png!small](https://image.3001.net/images/20210309/1615279044_604733c4b42b267c7cac2.png!small)

    
    
    #测试ping规则
    vi /usr/local/snort-2.9.17/rules/local.rules
    输入：alert icmp any any -> $HOME_NET any (msg:"ICMP test detected"; GID:1; sid:10000001; rev:001; classtype:icmp-event;)
    #启动规则，通过ifconfig确认好你的网卡是ethXX还是ensXXX
    sudo /usr/local/bin/snort -A console -q -c /usr/local/snort-2.9.17/etc/snort.conf -i ens192

![1615279070_604733de91b60f8b10c41.png!small](https://image.3001.net/images/20210309/1615279070_604733de91b60f8b10c41.png!small)

