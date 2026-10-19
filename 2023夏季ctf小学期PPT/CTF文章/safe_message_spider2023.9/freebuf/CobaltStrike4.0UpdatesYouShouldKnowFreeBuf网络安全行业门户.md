# 你应该知道的Cobalt Strike 4.0的更新!

    
    
    本文由Gcow安全团队绝影小组小离师傅原创,属于教程类文章  
    全文字数2348字 图片63张 预计10分钟阅读完毕  
    文中有一个小推荐 请各位看官不要在意

我相信大家都被一条信息给炸了锅“cobaltstrike4.0破解版出来了”，这对于我们这些穷逼来说是一件好事，今天我就带大家看看cs4.0更新了啥

 **在这里先声明，cobaltstrike的本意是用于教育目的，并非提供给非法渗透**

## 一.准备

### 试验环境：

    
    
    Kali ipv4：192.168.1.119  
         ipv6：出于隐私考虑，没写  
    ​  
    靶场win2008 ipv4：192.168.1.162  
                     10.10.10.80  
               ipv6：处于隐私考虑，没写  
    ​  
    靶场DC Win2012 ipv4：10.10.10.10  
    ​

 **本文只是演示cs4.0的新特性，并非真正渗透**

## 二.更新的内容

### 首先，先看看有什么主要更新

#### 1.Stageless：

![图1 Stageless payload
improved](https://i.loli.net/2020/03/20/Q81JndR7BMcmxyK.png)

可以看到，更新日志提到`Web
Delivery`攻击方式，在使用`64`位的`payload`的时候，使用的是`stageless`攻击方式，而`regsvr32`攻击方式同时被去掉了，
**因为不能注入完整的payload** ，同时，作者在视频中提到，在`cs4.0`中将会大大使用`stageless`，很少会使用`stager`.

#### 2.移除媒介自动播放攻击

![图2 Removed Windows-Dropper
attack](https://i.loli.net/2020/03/20/ImiNt6sVhUl95Cn.png)

#### 3.新增jump横向移动命令

其实就是把以前`psexec`，`wmi`等的整合到一个模块里，并且，当使用`psexec_psh`进行横向的时候会使用`stager`，其他方式均为`stageless`

![图3 Added Jump command](https://i.loli.net/2020/03/20/m6Wxt8slqNfb5oa.png)

#### 4.No Powershell 偏好

![图4 More inject was no
powershell](https://i.loli.net/2020/03/20/SQg1CaJYbZDm43V.png)

#### 5.提权新成员：SVC-exe和runasadmin

`svc-exe`其实就是在本地执行`psexec`（作者吐槽）

![图5 Svc-exe added in elevate
kit](https://i.loli.net/2020/03/20/iskXqKntgfvVRGI.png)

![图6 Runasadmin also is elevate
tool](https://i.loli.net/2020/03/20/Wiuq3TAaIl82By6.png)

#### 6.同时移除了ms14-058 exp 和uac-dll提权方式

![图7：Remove ms14-058](https://i.loli.net/2020/03/20/uxOczH72V9NXCKQ.png)

![图8：Remove uac-dll](https://i.loli.net/2020/03/20/iX3SHzw8vG7WjL4.png)

#### 7.重大更新：Listener

`http/https/dns`均支持一个`payload`填写 **多个ip或者域名** ，相当于把 **多个相同payload**
的`listener`整合到一起，并且支持填入`C2`参数以及代理参数

a.https/http listener：

![图9：Https Beacon info](https://i.loli.net/2020/03/20/HsbgIAK7m9Lvy5G.png)

    
    
    细心的同学可能发现，下面新的选项是用来干啥的，因为在cs4.0中，对C2攻击方式进行了优化，你可以在profile选择你在外部导入进去的c2 profile，然后修改HTTPS Port（bind）的端口为你C2 服务器的端口（我也不是很懂，如果有误的话，大佬们请指正，以免误人子弟）

b.Dns listener：

![图10 Dns Beacon info](https://i.loli.net/2020/03/20/TBCWasQItgoFDdu.png)

c.External C2 Listener：

![图11 External C2 listener](https://i.loli.net/2020/03/20/xv39lih5FDUPwo6.png)

## 三.看完了cs4.0的新特性，接下来开始实践一下吧

首先，先新建一个listener，在这里，你可以填写你cs服务器的 **公网IPv4** ， **内网IPv4** ，
**IPv6（IPv6要用中括号，例[240c::6666]）** ， **以及你CS服务器的域名**
，我在这里填入了我`kali`的`ipv4`和`ipv6`

![图12 Create a listener by using Beacon https
payload](https://i.loli.net/2020/03/20/ETy5GOe81KNqrmA.png)

> 这里的HTTPS Port (C2)就是上线端口

### 1.生成木马并执行

我这边直接生成了一个`stageless`的木马（不熟悉的话可以去看啊离上一篇文章）

生成的木马丢上去靶机执行然后等一小会（顺带一提：不知道是不是出于某种原因，`cs`直接生成的马，免杀并没有效果）

### 2.上线

因为我靶机有`ipv6`，所以`beacon`的`ip`也会显示`ipv6`，同时，因为也有`ipv4`，所以也会显示`ipv4`（意思为使用不同的协议的`ip`进行同时交互）

![图13 Beacon in ipv6](https://i.loli.net/2020/03/20/PhBg8DImwuMFxsc.png)

![图14 Beacon in ipv4](https://i.loli.net/2020/03/20/hcOVgY72IZ3UBb4.png)

### 3.界面变化

同时`CS4.0`改了界面，可以显示当前的 **beacon进程,PID,系统位数**

![图15 Cobalt Strike 4.0 table
view](https://i.loli.net/2020/03/20/zRXWS2CTg7VKpFD.png)

### 4.提权变化

正如我上面提到，`CS4.0`版本已经移除了`uac-dll`和`ms14-058`提权方式，同时`bypassuac`命令被移除

![图16 Elevate module](https://i.loli.net/2020/03/20/jkKMxcyWTsovNAG.png)

为了做实验，我生成了一个名为`Priv Esc`的`listener`（ **payload:tcp beacon** ）（建议勾选 **Bind to
localhost only** ）

为什么要勾选呢？作者的话：（反正就是勾选就对了）

![图17 Author's words](https://i.loli.net/2020/03/20/Vi6e5cK9DuOmNRJ.png)

![图18 Create a listener for privilege
escalation](https://i.loli.net/2020/03/20/KidDbJ6ZvVcI2yC.png)

#### a.UAC-token-duplication（UAC口令复制提权）

会在主机弹出一个`UAC`框去欺骗管理员输入密码，可能是因为域的原因，即使输入了也会提权失败，但是没关系，因为已经密码记录在内存中了，我们只需要本地提权并使用`mimikatz`读取密码

【按照实际情况来说，其实输入本地管理员口令的更多，这里我为了演示，在UAC弹窗中输入了域管理员口令】

UAC框框

![图19 UAC](https://i.loli.net/2020/03/20/REbfljNezxPZvDC.png)

failed，but the password was logged in memory

![图20 Failed when users was domain
user](https://i.loli.net/2020/03/20/3ZuSaUk9ni8smAe.png)

#### b.svc-exe

`svc-exe`这个参数，并不是和`exp`提权那样，帮你从普通用户 ”pwn！！“ 一下子拿下系统，而是当管理员权限满足不了你的时候，可以用`svc-exe`进行提升（类似`getsystem`命令，但是`getsystem`不太好使）

使用例如下情况：

![图21 A administrator privilege
Beacon](https://i.loli.net/2020/03/20/rkpMyPeRxcgCTXL.png)

svc-exe priv esc：

![图22 Use Svc-exe to privilege
escalation](https://i.loli.net/2020/03/20/5DusvQKMdTLN8px.png)

![图23 Connected to system privilege
beacon](https://i.loli.net/2020/03/20/t5muBQH3snDrqdv.png)

#### c.EXP 本地提权

因为现在是域用户，又又又又只能用exp本地提权了，因为 **作者已经在cs4.0中删除了exp** ，但是你可以通过`GitHub`去`clone`作者的
**【Elevate Kit】** 项目，然后在`cs`加载模块

cs作者的项目:<https://github.com/rsmudge/ElevateKit>

![图24 Imported elevate kit for privilege
escalation](https://i.loli.net/2020/03/20/iL4ybS2rzAucJE3.png)

#### d.runasadmin 提权模块（后面会用到）

![图25 Runasadmin module](https://i.loli.net/2020/03/20/2eKS7JzsANjZ4Xa.png)

### 5.Recon 部分更新

#### a.Net模块新增俩参数

##### (a).net domain

![图26 net domain command](https://i.loli.net/2020/03/20/am8EG7kyAWFfCes.png)

##### (b).net domain_controllers

![图27 net domain_controllers
command](https://i.loli.net/2020/03/20/pN9IWngfYGoaOvc.png)

可以看到，计算机名为DC的就是域控，接下来可以鞭挞它了

#### b.横向移动改进

exp提权，然后抓密码（此处密码为刚刚UAC钓到的域管理员明文密码）

![图28 Logonpassword after privilege
escalation](https://i.loli.net/2020/03/20/lM1TeBJsyIZLUrw.png)

##### (a).SMB Beacon改进

生成一个用于横向移动的listener，取名为LM，并使用SMB Beacon payload，可以看到，SMB Beacon支持自定义pipe name了

![图29 SMB Beacon now support custom
pipename](https://i.loli.net/2020/03/20/Ff4K9ygX3imBR2s.png)

有点小伙伴要问了，为什么在旧版的cs中没有这个呢？其实，旧版cs中的pipe name是[status_端口号]

![图30 Create a listener for Lateral
Movement](https://i.loli.net/2020/03/20/iWTKI1bgn3lUvzt.png)

> 如图，旧版cs的pipe name则为status_6001

##### (b).jump命令

`jump`命令本质上就是把原来零散的 **psexec，psexec64，psexec_psh，winrm，winrm64**
整合到一个套件里（wmi已经移除）

How to use

![图31 Help of jump command](https://i.loli.net/2020/03/20/bj8Dq3k1pO7ylxG.png)

Lateral Movement kits in jump command

![图32 Lateral Movement tookit in jump
command](https://i.loli.net/2020/03/20/S5rKb9wVCnNkIxD.png)

老样子，调用刚刚抓到的域凭据

make_token de1ay.com\Administrator 1qaz@WSX

![图33 Use make_token command to impersonal
credential](https://i.loli.net/2020/03/20/UZHB93I5rDMLz4T.png)

使用`jump`命令进行横向

jump psexec DC LM

![图34 Use jump command lateral movement to
DC](https://i.loli.net/2020/03/20/7ltKx8UQN9C24SM.png)

DC Beacon Online

![图35 Connected to DC through smb
beacon](https://i.loli.net/2020/03/20/aLRiwrZn6IBtG21.png)

##### (c).remote-exec 命令

可以选择以下三个套件进行远程命令执行

![图36 Remote-exec module](https://i.loli.net/2020/03/20/DfHua29bCiV1NxS.png)

remote-exec wmi DC netsh advfirewall set allprofiles state off
(当然，和上面一样，也要先调用凭据)

![图37 Use remote-exec to disable firewall on
DC](https://i.loli.net/2020/03/20/PiOMD9aeFnQNpus.png)

##### (d).Invoke-Command（个人补充）

补充：在`CS`中，可以使用`powershell-import`导入`ps1`脚本，然后使用`powerpick`去执行脚本的模块

![图38 You can use powershell-import command to import
module](https://i.loli.net/2020/03/20/dNZtoeDSYvl1cf8.png)

其实可以使用系统自带的`Invoke-Command`模块进行远程命令执行（ **当然，也需要调用凭据** ）

powerpick Invoke-Command -ComputerName DC -ScriptBlock { netsh advfirewall set
allprofiles state off }

![图39 Use Invoke-Command module to remote disable firewall on
DC](https://i.loli.net/2020/03/20/WoNPdShTDLajGQk.png)

#### c.One-liner

`oneliner`其实就是生成一段在目标`beacon`本地运行的`payload`，你可以用它在目标beacon中进行花样玩耍，配合的方式有很多种，如：
**runas，runu，runasadmin，psinject**

##### (a).oneliner配合runasadmin进行提权

在`cs`中，只有当前用户名为`administrator`的管理员用户，`cs`才会自动提权，当用户名为别的管理员，`cs`并不会自动提权，例如以下情况:

![图40 Show current user
groups](https://i.loli.net/2020/03/20/b4yY7mq2Qeiakdn.png)

可以看到，`xiaoli`这个用户是本地管理员，可是`cs`没有帮我们提权

抓密码提示权限不足

![图41 Privilege less when
logonpasswords](https://i.loli.net/2020/03/20/qXEHP19z6c8lBpA.png)

so，we can do like this

①.生成oneliner，右击beacon-Access-oneliner

在这里的话，是看beacon的arch生成oneliner，我当前的beacon是64位，所以x86和x64的payload都可以，x86
beacon只能执行x86的payload

（我当前的beacon是x86的）

![图42 Generate powershell
oneliner](https://i.loli.net/2020/03/20/YI8KLFxzbfCk7hQ.png)

![图43 Generated Success!](https://i.loli.net/2020/03/20/ZpbCKYAVLv73jfP.png)

runasadmin uac-wscript + oneliner

![图44 Use runasadmin to privilege
escalation](https://i.loli.net/2020/03/20/bfP43mXzkIZdo9g.png)

执行完它并不会自动连接，需要去手动连接

connect 127.0.0.1

![图45 Connect to beacon](https://i.loli.net/2020/03/20/poNyi4EI1qstJcV.png)

![图46 Connected!](https://i.loli.net/2020/03/20/ScU3QJ7rqszdHp1.png)

重新`logonpassword`

![图47 Re logonpasswords](https://i.loli.net/2020/03/20/Oy1rZunD9oYIweU.png)

##### (b).One-liner 配合runas生成一个指定用户的权限

在这里的话，也是看beacon的arch生成oneliner，同上

runas DE1AY\Administrator 1qaz@WSX + oneliner 注：runas在system权限的beacon运行会失败

![图48 Runas with oneliner](https://i.loli.net/2020/03/20/eZmQnc5sfGBjght.png)

connect 127.0.0.1

![图49 Connect to beacon](https://i.loli.net/2020/03/20/6elPjcCbqGthBMs.png)

![图50 Connected!](https://i.loli.net/2020/03/20/Hj61kWlwtshCNrz.png)

##### (c).One-liner 配合runu在指定进程执行命令

在这里的话，是看目标进程的arch生成oneliner，我的目标进程是64位，所以生成x64和x86的payload都可以，x86进程则只能生成x86
payload

runu 460 + oneliner 这边选择了一个pid为460的进程

![图51 Runu command with
oneliner](https://i.loli.net/2020/03/20/WhPRZrasxl6OzKA.png)

connect 127.0.0.1

![图52 Connect to beacon](https://i.loli.net/2020/03/20/FaxpbUZtMXcVNAk.png)

![图53 Connected!](https://i.loli.net/2020/03/20/GTrE4RZkl7MDahH.png)

同时看到该beacon的父进程就是我们刚刚所指定的

![图54 Created a child session base on PPID
460](https://i.loli.net/2020/03/20/9H6B4MnUDYKS7ZV.png)

##### (d).Psinject使用one-liner payload注入进程

在psinject这里，x64进程可以注入x86/x64的payload，x86进程只能注入x86

![图55 Choose a process for
target](https://i.loli.net/2020/03/20/6G38kyXHAF5daBs.png)

psinject 2784 x64 + oneliner

![图56 Inject powershell payload with
psinject](https://i.loli.net/2020/03/20/EeHtfUnT2mNp7Ry.png)

connect 127.0.0.1

![图57 Connect to beacon](https://i.loli.net/2020/03/20/aymkDPXjIFJbTU6.png)

connected

![图58 Connected!](https://i.loli.net/2020/03/20/Scl2epwBkOEDFKb.png)

当然，还有更多的姿势等你来解锁~

#### d.Link / Connect and unlink

`link`支持指定`pipe name`，`connect`支持 **指定端口**
，`unlink`支持指定`pid`号，其目的是为了可以更好管理多个`smb beacon listener`与`tcp beacon listener`

link ip pipe_name（图中因为没有111这个pipe name，连不上就报错了）

![图60 Link to a beacon through assign
pipename](https://i.loli.net/2020/03/20/W8RMDLjUXsNx5ek.png)

connect ip port

![图61 Connect to tcp beacon through assign
port](https://i.loli.net/2020/03/20/IcX94lJivNd7MoY.png)

unlink ip pid

![图62 Unlink beacon through assign
process](https://i.loli.net/2020/03/20/kptsuHlCdKWEYrN.png)

## 四.总结

###
作为一名有职业道德的伸手党，要时刻记得吃水不忘挖井人的道理，所以在这里要非常感谢WBGlIl大大![image-20200320175426198](https://i.loli.net/2020/03/20/i4yODbL5QG6Zqtm.png)（对，没错，认准这只熊）提供的破解版，以及Yansu大大提供的二次元版

![图63 cs二次元版作者大大](https://i.loli.net/2020/03/20/LCVRvMxmjhQ9Aut.png)

 **问答环节:**

    
    
     Q&A  
    ​  
    问：为什么x64的beacon和session可以同时兼容x86和x64的payload？  
    ​  
    答：CS特性，作者超级偏爱x86，link：https://blog.cobaltstrike.com/2016/03/10/cobalt-strike-3-2-the-inevitable-x64-beacon/  
    ​  
    ​  
    问：为什么作者强推Stageless？  
    ​  
    答：因为stager不安全，更脆弱，容易被检测  
    ​

文末惊喜！  

两天过去了，我知道，大家都在等CS完美破解版  
CS4.0去暗桩，windows teamserver支持，vnc修复，x64 payload修复，汉化支持 终极版本今天发布！！Gcow安全团队核心成员
J0o1ey’参考先知某牛和国外某牛的修复方法，目前已无x64 payload和暗桩问题

* * *

小声BB：后台回复cobaltstrike即可获取下载链接

![qrcode_for_gh_f444cf1f314b_258\(1\).jpg](https://image.3001.net/images/20200321/1584773592_5e75b9d8974a0.jpg!small)  

  

