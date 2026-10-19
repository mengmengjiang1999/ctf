## 介绍

**在之前的文章中我介绍了Linux防火墙的基本配置，并在最后简单提及了下firewalld。本文我将详细为大家介绍如何使用firewalld配置Linux防火墙。Firewalld为用户提供了一个GUI界面，在这上面用户可以访问到所有的功能。此外，它还为我们提供了一个任务栏/面板小程序，可以让你快速的访问到最常用的功能，包括“阻止所有网络流量”选项。大多数配置都将在CLI（命令行界面）完成。本文我使用的是xfce终端，但只要是支持bash，ksh或其他Linux
shell的任何终端你都可以用。**

## 关于 firewalld

firewalld提供了支持网络/防火墙区域(zone)定义网络链接，以及接口安全等级的动态防火墙管理工具。它支持IPv4，IPv6，以太网桥以及IPSet防火墙设置。拥有运行时配置和永久配置选项。它还为服务或应用程序提供了一个接口，可以直接添加iptables，ip6tables和ebtables规则。高级用户也可以使用此接口。

参考来源：<https://firewalld.org/documentation/>

这部分的内容可能需要更新，现在firewalld已经支持nftables。如果你安装了iptables并且想要使用nftables，那么你应该结束所有iptables进程（理想情况下，如果这是你首选的防火墙选项，那么最好是安装nftables之前卸载iptables）。

带有防火墙配置的Firewalld，它的图形配置工具和防火墙面板小程序你可以从Ubuntu的存储库中进行安装（所有Ubuntu的衍生版都可以从这里安装
）。此外，它也是Centos中的默认防火墙选项，大多数主要Linux发行版都可以在[pkgs.org](https://pkgs.org/download/firewalld)中以下列格式获取：

> .rpm
>
> .deb
>
> .tar.xz

以及适用于以下发行版的firewalld linux软件包：

> ALT Linux Sisypus
>
> Arch
>
> Centos7
>
> [Fedora](https://www.peerlyst.com/tags/fedora)
>
> Mageia
>
> Open Suse
>
> Ubuntu
>
> 包括其它一些非发行版本的软件包

## 安装 firewalld

在大多数主要的Linux发行版中，你只需从包管理器（synaptic，pacman等）中选择firewalld（以及GUI和面板小程序，如果你需要的话），下载并让包管理器安装即可。

或者你也可以[编译安装firewalld](https://firewalld.org/2018/09/firewalld-0-6-2-release)。

你可以在运行时环境中进行更改，不需要重新启动服务或守护程序。

使用firewalld D-Bus接口，服务，应用程序和用户都可以轻松调整防火墙设置。该接口被用于防火墙配置工具firewall-cmd，firewall-config和firewall-applet。

运行时和永久配置的分离使得在运行时进行评估和测试成为可能。运行时配置仅在下次服务重新加载和重新启动或系统重新引导时有效，并将再次加载永久配置。
使用运行时环境，可以使用运行时的设置这些设置只在有限的时间内有效。如果运行时配置已用于评估，并已完成且正常工作，则可以将此配置保存到永久环境中。

## 特性

> 完整的D-Bus API
>
> 支持IPv4，IPv6，网桥和ipset
>
> 支持IPv4和IPv6 NAT
>
> 防火墙区域（zones）
>
> 预定义的区域，服务和icmptypes列表
>
> 区域中的简单服务，端口，协议，源端口，地址伪装（masquerading），端口转发，icmp过滤器，丰富规则，接口和源地址处理
>
> 简单的服务定义，包括端口，协议，源端口，模块（netfilter helpers）和目标地址处理
>
> 丰富的语言，可在区域中实现更灵活，复杂的规则
>
> 区域中的定时防火墙规则
>
> 简单记录被拒绝的数据包
>
> 直接接口
>
> 锁定：可能修改防火墙的应用程序的白名单
>
> 自动加载Linux内核模块
>
> 与Puppet集成
>
> 命令行clints用于联机和脱机配置
>
> 使用gtk3的图形配置工具
>
> 使用Qt4的Applet

参考来源：<https://firewalld.org/>

![1.png](https://image.3001.net/images/20181118/1542511744_5bf0dc80add3c.png!small)

所有firewalld软件和文档（包括网站）都包含在<https://unlicense.org/>中。

安装firewalld后，你可以启用该服务并重启服务器。注意：启用firewalld将导致服务在重启时启动。最佳做法是在配置此行为之前创建防火墙规则，并对其进行测试以避免潜在问题的发生。

    
    
    sudo systemctl enable firewalld
    sudo reboot

当服务器重启时，防火墙会被启动，你的网络接口将被放入你配置的区域（或回退到配置的默认区域），并且与区域关联的任何规则都将应用于关联的接口。

参考来源：[在centos7上使用firewalld](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-using-firewalld-on-centos-7)

如果你安装了firewall-config，它应该在你的菜单中。在Mint中，它位于Menu→system下。你只需单击“firewall”启动firewall-config，并在出现提示时输入密码即可。

![2.png](https://image.3001.net/images/20181118/1542511782_5bf0dca66569a.png!small)

区域中public是默认值，默认情况下信任的服务为dhcpv6，mdns和ssh的最小集合。相同的基本可信服务集适用于内部区域。

工作区仅信任dhcpv6和ssh，外部区域仅信任ssh。

而在所有其他区域中，则没有服务被信任：

> dmz（非军事区）：仅接受ssh服务
>
> block（限制）：拒绝所有的网络服务
>
> drop（丢弃）：任何访问的网络数据包都会被丢弃，没有任何回应
>
> trust（信任）：可接受所有的网络连接

查看区域选项卡中的其他选项我们发现：

> 在端口中，没有定义任何的内容
>
> 在协议中，也没有定义任何内容
>
> 地址伪装未开启
>
> 端口转发没有任何内容
>
> 而且没有定义ICMP过滤器
>
> 没有“丰富的规则”，也没有接口，来源。

因此，看起来firewalld做了一个合理的工作，即设置最小的默认值以允许基本的工作站操作。服务器将需要根据其预期的功能进行不同的配置。

查看服务选项卡，每个预定义服务都分配了其默认端口要求。

telnet在端口23 tcp，ntp在端口123 udp上，snmp在端口161上用于moth tcp和udp等等...

![3.png](https://image.3001.net/images/20181118/1542511813_5bf0dcc5ea66a.png!small)

注意：firewalld对权限的超时非常严格，可能你离开几秒钟，它就会要求你再次进行身份验证。

如果面板小程序正在运行，默认情况下你将在panel0中看到：

![4.png](https://image.3001.net/images/20181118/1542511841_5bf0dce14eb0c.png!small)

带有红色圆图标的那个就是。

点击它，将会出现一个下拉菜单：

![5.png](https://image.3001.net/images/20181118/1542511859_5bf0dcf395cc7.png!small)

在对GUI做了基本的了解后，现在是时候回到命令行了！

 **命令行下 firewalld 配置**

在开始配置防火墙之前，先让我们看一下现有的默认配置。

使用以下命令，查看firewalld当前配置状态的一些基本信息：

    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ sudo firewall-cmd --state
    
    [sudo] password for davdi:
    
    running
    
    davdi@davdi-G1-SNIPER-B7 ~ $
    
    davdi@davdi-G1-SNIPER-B7 ~ $ sudo firewall-cmd --state
    
    running
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --get-default-zone
    
    public
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --get-active-zones
    
    public
    
    interfaces: enp0s31f6
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --list-all
    
    public (default, active)
    
    interfaces: enp0s31f6
    
    sources:
    
    services: dhcpv6-client ssh
    
    ports:
    
    protocols:
    
    masquerade: no
    
    forward-ports:
    
    icmp-blocks:
    
    rich rules:
    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --get-zones
    
    block dmz drop external home internal public trusted work
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --zone=home --list-all
    
    home
    
    interfaces:
    
    sources:
    
    services: dhcpv6-client mdns samba-client ssh
    
    ports:
    
    protocols:
    
    masquerade: no
    
    forward-ports:
    
    icmp-blocks:
    
    rich rules:
    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --get-services
    
    amanda-client amanda-k5-client bacula bacula-client ceph ceph-mon dhcp dhcpv6 dhcpv6-client dns docker-registry dropbox-lansync freeipa-ldap freeipa-ldaps freeipa-replication ftp high-availability http https imap imaps ipp ipp-client ipsec iscsi-target kadmin kerberos kpasswd ldap ldaps libvirt libvirt-tls mdns mosh mountd ms-wbt mysql nfs ntp openvpn pmcd pmproxy pmwebapi pmwebapis pop3 pop3s postgresql privoxy proxy-dhcp ptp pulseaudio puppetmaster radius rpc-bind rsyncd samba samba-client sane smtp smtps snmp snmptrap squid ssh synergy syslog syslog-tls telnet tftp tftp-client tinc tor-socks transmission-client vdsm vnc-server wbem-https xmpp-bosh xmpp-client xmpp-local xmpp-server  
      
    davdi@davdi-G1-SNIPER-B7 ~ $

所有服务定义都以xml格式文件被存储在/usr/lib/firewalld/services中。

你可以在任何的文本编辑器，Web浏览器或xml查看器中查看这些内容。

获取当前配置状态后，接下来就是配置firewalld以符合我们的使用需求。

 **firewalld 配置**

首先，我们将默认区域更改为home：

    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ sudo firewall-cmd --zone=home --change-interface=eth0
    
    [sudo] password for davdi:
    
    success
    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --get-active-zones
    
    home
    
    interfaces: eth0
    
    public
    
    interfaces: enp0s31f6  
      
    davdi@davdi-G1-SNIPER-B7 ~ $

现在，让我们将home区域设为默认区域：

    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ firewall-cmd --set-default-zone=home
    
    success
    
    davdi@davdi-G1-SNIPER-B7 ~ $

注意：如果你忘记使用sudo，则可能会要求你输入密码（这取决于的Linux发行版本）。除非你想要关闭所有不必要的端口，停止响应ping请求等行为，以最小化你的攻击面。

首先，建议你查看下当前开放的端口有哪些：

你可以使用cat /etc/services命令，查看服务及其对应的端口号。

但这很可能会向你展示一长串的端口列表，看起来会让你觉得有点晕。

更好的办法是使用nmap来查看。如果你的系统上没有nmap，只需简单的安装即可。

Nmap 127.0.0.1将为你显示当前有哪些端口正在使用。

Firewall-cmd –list-ports也会为你显示相同的结果。

如果要打开特定端口，可以--add-port选项指定：

    
    
    davdi@davdi-G1-SNIPER-B7 ~ $ sudo firewall-cmd --add-port=8080/tcp
    
    [sudo] password for davdi:
    
    success
    
    davdi@davdi-G1-SNIPER-B7 ~ $

不要忘记重新加载firewalld来激活更改：firewall-command --reload

记住，更改将在重启后失效，除非你设置了永久更改。

    
    
    sudo firewall-cmd  --permanent --add-port=8080/tcp

注意：这里我没有执行该命令，因为我不需要进行永久性的更改。

我省略了区域，因为之前我将默认区域设置为了“home”，省略区域后将对默认（home）区域进行更改。

你还可以添加一个范围的端口，如下所示：

    
    
    sudo firewall-cmd --zone=home --permanent --add-port=3500-3559/udp

以上端口范围是我随意选的，没什么特别的意义。

或者你也可以使用图形界面：

![6.png](https://image.3001.net/images/20181118/1542511906_5bf0dd22192f0.png!small)

从下拉菜单中选择相关协议。

 **定义服务**

为你的区域打开端口很容易，但管理起来就比较麻烦。如果你在服务器上退役某项服务，那么你可能很难记住仍然需要打开哪些端口。为避免这种情况，你可以定义一个服务。

服务只是具有相关名称和描述的端口集合。使用服务比端口更加容易管理，但需要做一些前期的工作。最简单的方法是将现有脚本（位于/usr/lib/firewalld/services）复制到防火墙查找非标准定义的/etc/firewalld/services目录中。

例如，我们可以复制SSH服务定义用于我们的“example”服务定义。

    
    
    sudo cp /usr/lib/firewalld/services/ssh.xml /etc/firewalld/services/example.xml

现在，你可以使用首选编辑器调整在复制的文件中找到的定义。

该文件将包含你复制的SSH定义：

/etc/firewalld/services/example.xml

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <service>
      <short>SSH</short>
       Secure Shell (SSH) is a protocol for 
       logging into and executing commands on remote machines. It provides secure 
       encrypted communications. If you plan on accessing your machine remotely via SSH over a firewalled interface, enable this option. You need the openssh-server package installed for this option to be useful.  
      <port protocol="tcp" port="22"/>
    </service>

参考来源：[在centos7上使用firewalld](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-using-firewalld-on-centos-7)

大多数文件都包含xml元数据，以下是我们重点需要关注的部分：

    
    
    <port protocol="tcp" port="22"/> 

这里将会告诉我们，当前正在使用的端口和协议。

## 总结

相信通过本文的学习，你已基本掌握了firewalld防火墙的配置。在这里也提醒大家，在未做好充分的准备和决定之前不要轻易的执行永久更改操作，并在更改的过程中提前做好重要数据内容的备份，以便在出现问题时进行回滚。

 ***参考来源：[peerlyst](https://www.peerlyst.com/posts/how-to-configure-a-linux-firewall-with-firewalld-david-dunmore?utm_source=twitter&utm_medium=social&utm_content=peerlyst_post&utm_campaign=peerlyst_shared_post)
，FB小编secist编译，转载请注明来自FreeBuf.COM**

