***本文作者：gncao，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 一、前言

 **作为系列文章的第一篇<https://www.freebuf.com/es/193557.html>
介绍了攻防系统的整个环境和搭建方法，按照这篇文章应该是可以把整个环境搭建完毕的.。在这篇文章中还介绍到了课程大纲包含主机安全、web安全、后门/木马等等，下面就让我们开始我们的实验课程。**

## 二、课程目标

首先第一个课程是主机安全的ssh端口入侵&检测&响应课程。  

课程有几个目标如下所示：

 **1\. 熟练使用nmap类端口扫描工具**

 **2\. 熟练使用hydra、msf等平台对ssh服务开展爆破行为**

 **3\. 监测平台能够在第一时间检测到攻击行为并发出告警**

 **4\. 能够在服务器上找到入侵痕迹包括攻击时间、攻击方式、是否成功、攻击源等有价值信息**

注：对于很多大佬来说这些都是小菜了，但是在一开始的时候我也是这么认为的（我不是大佬）直到在做后面环节的时候还是碰到了一些问题，同时也掌握了一些新的知识，相信大家都会在这个过程当中都能够有所收获。

## 三、实验环境

攻击主机ip：192.168.171.130（注：因为换了新电脑，物理主机没有攻击环境，所以新装了一个kali虚拟机作为攻击主机）

受害者主机ip：192.168.171.121

检测主机ip：192.168.171.120

## 四、攻击思路

1\. 使用nmap等端口扫描工具探测目标服务器是否存在ssh服务  

1）在攻击主机的命令行下输入nmap -sS 192.168.171.121 对目标主机进行端口扫描：  

![](https://image.3001.net/images/20190121/1548070033_5c45ac91cb2fc.png!small)

2）检测发现目标主机存在ssh服务，尝试登陆几次判断是否存在登陆次数限制或登陆地址限制情况：  

![](https://image.3001.net/images/20190121/1548070057_5c45aca918abc.png!small)

经过多次尝试登陆发现没有存在限制次数登陆和限制登录地址的情况，所以我们可以使用爆破工具加载字典对ssh服务进行爆破了。

2\. 使用msf、hydra等工具加载字典对目标ssh服务开展爆破行为，这里使用hydra来做演示。

hydra和msf的使用方法不做过多介绍，否则篇幅无法控制。大家如果有不懂的，可以百度或者联系我。

1）在命令行下使用hydra加载用户名、密码字典对目标ssh服务开展爆破行为：

    
    
    hydra -L user.txt -P pass.txt ssh://192.168.171.121

2）对爆破出来的用户名密码尝试登陆  

![](https://image.3001.net/images/20190121/1548070140_5c45acfcaab22.png!small)ssh
victim@192.168.171.121 输入密码后正常登陆：  

![](https://image.3001.net/images/20190124/1548337012_5c49bf74c5eb5.png!small)

3）创建SSH免密登陆

3.1）现在攻击主机上生成公钥信息

    
    
    ssh-keygen -t rsa

![](https://image.3001.net/images/20190121/1548070339_5c45adc3edfec.png!small)3.2）将生成的公钥信息传到受害主机上  

![](https://image.3001.net/images/20190121/1548070369_5c45ade11b241.png!small)

一定要注意是公钥文件后缀为.pub。

    
    
    ssh-copy-id -i .ssh/id_rsa.pub victim@192.168.171.121

![](https://image.3001.net/images/20190121/1548070417_5c45ae119ef06.png!small)

输入受害主机的密码后即可。

3.3）尝试可以免密登陆

ssh victim@192.168.171.121 直接登陆不用输入密码。

![](https://image.3001.net/images/20190121/1548070468_5c45ae449ef88.png!small)

正常情况下是需要输入密码的，注意标红位置：  

![](https://image.3001.net/images/20190121/1548070474_5c45ae4aca595.png!small)

至此基本的SSH攻击已经结束了，思路很简单这个应该是基本功无压力。下面的过程就比较有收获了。

## 五、响应方法

1\. 登陆目标主机关闭ssh服务、查看被爆破成功账户、判断是否存在ssh免密登陆。

1）关闭ssh服务

    
    
    systemctl stop sshd 或者/etc/init.d/sshd stop

2）查看被爆破成功的账户

两种方案可以查看到

2.1）第一种是查看ssh日志中的关键字眼 Accepted password for

注意Accepted的第一个字母大写否则匹配不到记录：

    
    
    cat /var/log/secure | grep "Accepted password for"

![](https://image.3001.net/images/20190121/1548070713_5c45af39ab717.png!small)

从日志中能够发现victim和root账户均被爆破出来。

2.2）第二种是last命令查看登陆地址信息

![](https://image.3001.net/images/20190121/1548070736_5c45af5006f50.png!small)last
命令效果等同于 who /var/log/wtmp。  

![](https://image.3001.net/images/20190121/1548070783_5c45af7f426a8.png!small)

3）检查是否存在免密登陆

因为从日志和wtmp记录中我们看到攻击者已经登陆了victim和root账户所以我们需要在这两个账户下面分别查看是否存在ssh公钥信息。

3.1）首先查看普通账户victim的.ssh目录下是否存在authorized_keys文件

    
    
    ls -l /home/victim/.ssh/

![image.png](https://image.3001.net/images/20190121/1548070837_5c45afb56432a.png!small)

从上面可以看出victim账户存在免密登陆而且还记录到了攻击者服务器的主机名和用户名信息。

3.2）然后查看root账户的.ssh目录是否存在authorized_keys文件

    
    
    ls -l /root/.ssh/

![](https://image.3001.net/images/20190121/1548070863_5c45afcf6f119.png!small)

从结果可以看到root账户下不存在免密登陆。

2\. 检查系统用户是否存在异常账号若存在清除异常账户

    
    
    cat /etc/passwd

![](https://image.3001.net/images/20190121/1548070885_5c45afe5d6672.png!small)

无异常账户

3\. 检查ssh日志是否存在短时间内大量的尝试登陆行为，从而判断这个登录成功的账户是正常登陆还是异常登陆

查看secure日志文件判断是否存在大量的Invalid user 字眼

    
    
    cat /var/log/secure | grep "Invalid user"

![](https://image.3001.net/images/20190121/1548070918_5c45b006e66bf.png!small)cat
/var/log/secure | grep "Accepted password for victim from 192.168.171.130"
记录登陆成功的时间点然后判断是否跟暴力破解的时间段一致，如果一致则表示该账户是被爆破成功登陆。或者直接找管理员确认登陆信息是否正常。  

![](https://image.3001.net/images/20190121/1548070963_5c45b033adf1d.png!small)

跟上面的secure日志中的时间点做匹配可以看到该账户是被暴力破解出来的。

4，检查定时任务是否存在异常情况

1）crontab -l查看当前用户的定时任务信息

![](https://image.3001.net/images/20190121/1548070982_5c45b04652599.png!small)2）sudo
crontab -u root -l 查看root账户的定时任务信息  

![](https://image.3001.net/images/20190121/1548070997_5c45b055d662f.png!small)3）查看/etc/cron.d/文件夹中是否存在文件  

![](https://image.3001.net/images/20190121/1548071014_5c45b06657f87.png!small)

能够看到cron.d文件夹中存在定时任务但是内容不含攻击行为。

4）查看/etc/cron.daily/ /etc/cron.weekly/ /etc/cron.hourly/ /etc/cron.monthly/
这些文件夹下面是否存在定时任务

![image.png](https://image.3001.net/images/20190121/1548071055_5c45b08fcc780.png!small)

## 六、修复方案

1\. 修改被爆破账户密码增加密码复杂度

分别执行passwd victim 和passwd root命令修改victim和root账户密码。

2\. 清除免密登陆信息

删除.ssh/目录下的authorized_keys文件。

    
    
    rm -rf .ssh/authorized_keys

3，清除定时任务

如果存在定时任务直接删除定时任务文件或者进入到定时任务文件中删除所在行信息即可。

4，增加ssh登陆失败次数限制

编辑sshd_config配置文件修改MaxAuthTries记录。

![](https://image.3001.net/images/20190121/1548071111_5c45b0c76d10e.png!small)

保存退出后重启sshd服务。

再次尝试登陆且输入密码超过2次后会出现如下信息。

![](https://image.3001.net/images/20190121/1548071132_5c45b0dc7d5df.png!small)再次使用hydra尝试爆破ssh用户名密码。  

查看secure日志：  

![image.png](https://image.3001.net/images/20190121/1548071171_5c45b103497e8.png!small)  

为什么呢？为什么会出现这种情况呢？

我们已经在SSH的配置文件中增加次数限制了为什么还是可以爆破成功呢？

是因为我们在这里对登陆失败次数做限制了，但是没有锁定账户。也就是说这个账户依然可以被暴力破解只是破解的速度会慢一点而已。

那正确的方式应该怎么做呢。

需要通过pam来锁定超过登陆次数的账户编辑/etc/pam.d/sshd文件：

    
    
    vim /etc/pam.d/sshd

![](https://image.3001.net/images/20190121/1548071248_5c45b150c05f6.png!small)增加如上所示一条记录该条记录，表示登陆失败超过三次后就锁定300秒，root账户如果三次尝试后也不行将被锁定1200秒。

字段解释：

    
    
    deny表示的是设置的最大失败次数
    
    unlock_time 表示的是锁定多长时间单位是秒
    
    deny_root 表示root账户也封锁
    
    root_unlock_time 表示的是root账户的锁定时间

注：

> 如果限制ssh登陆则编辑sshd文件
>
> 如果限制终端登陆则编辑login文件
>
> 再次尝试hydra爆破

![](https://image.3001.net/images/20190121/1548071346_5c45b1b2371a1.png!small)发现无法成功爆破查看secure日志：

![](https://image.3001.net/images/20190121/1548071359_5c45b1bfc44cd.png!small)日志中显示victim账户已经被锁定。

查看锁定的账户和登陆失败的次数：

    
    
    sudo pam_tally2 --user victim

![](https://image.3001.net/images/20190121/1548071392_5c45b1e07f640.png!small)这时候尝试输入正确密码尝试登陆：  

![](https://image.3001.net/images/20190121/1548071408_5c45b1f0c5ba6.png!small)

依然无法登陆。那怎么解除封锁呢？

只需要将pam中的记录清除掉即可。

    
    
    sudo pam_tally2 --user victim --reset

![](https://image.3001.net/images/20190121/1548071429_5c45b20573476.png!small)再次尝试登陆victim账户：  

![image.png](https://image.3001.net/images/20190121/1548071444_5c45b21427151.png!small)

可以发现能够正常登陆了

5\. 限制只允许特定ip地址访问ssh

通过编辑/etc/hosts.allow和/etc/hosts.deny这两个文件来控制访问源ip地址范围。当两个文件同时存在策略的时候allow文件的优先级大于deny文件。

这里我们限制victim主机只允许171.1访问其他全阻断。

1）vim /etc/hosts.allow 增加如下记录

    
    
    sshd:192.168.171.1:allow

2）vim /etc/hosts.deny 增加如下记录sshd:ALL

然后测试从171.130 ssh访问171.121主机如下所示可以看到通过171.130无法登陆。

![image.png](https://image.3001.net/images/20190121/1548071505_5c45b2516e381.png!small)查看171.1主机仍然处于登陆状态。  

![image.png](https://image.3001.net/images/20190121/1548071557_5c45b28541178.png!small)

6\. 限制只允许特定用户访问ssh

通过编辑sshd配置文件增加AllowUsers和DenyUsers配置选项来控制允许登陆的用户。

sudo vim /etc/ssh/sshd_config在文件中追加如下配置，如果记录存在直接修改记录即可，如果记录不存在需要在文件末尾追加。

    
    
    AllowUsers      victim
    
    DenyUsers       root

配置完毕后重启sshd服务然后分别尝试以vicitm和root账户登陆victim主机。

![image.png](https://image.3001.net/images/20190121/1548071616_5c45b2c09e377.png!small)

可以看到victim账户可以直接登陆root账户则无法直接登陆。

这样我们可以通过控制ip和账户信息来实现完美控制限制只允许从某台主机使用某个账户登陆。

但是这样有点麻烦需要编辑hosts.allow、hosts.deny和sshd_config文件，其实我们可以直接编辑sshd_config文件增加如下记录：

    
    
    AllowUsers      victim@192.168.171.1

这样我们就可以限制只允许171.1通过victim账户登陆victim主机了。

我们在其他主机尝试用victim账户登陆如下图所示可以看到无法登陆。

![image.png](https://image.3001.net/images/20190121/1548071675_5c45b2fb43b84.png!small)

7\. 修改对外提供ssh服务的端口号

1）编辑sshd_config文件增加如下配置

    
    
    port 22
    
    port 3389

增加另外一个ssh端口号3389避免修改失败连接不上主机了

2）向防火墙添加修改的端口号

    
    
    sudo firewall-cmd --zone=public --add-port=3389/tcp --permanent

重载防火墙

    
    
    sudo firewall-cmd --reload

查看端口号是否添加成功

    
    
    sudo firewall-cmd --zone=public --query-port=3389/tcp

![](https://image.3001.net/images/20190121/1548071704_5c45b318c8d4e.png!small)提示yes表示成功添加

3）向selinux中添加修改的端口号

3.1）首先要安装selinux的管理工具semanage

    
    
    sudo yum provides semanage
    
    sudo yum install policycoreutils-python  #安装依赖包

3.2）安装完成后可以使用semanage命令查看ssh服务端口

    
    
    sudo semanage port -l | grep ssh

![](https://image.3001.net/images/20190121/1548071760_5c45b35079880.png!small)

向selinux添加ssh端口

    
    
    sudo semanage port -a -t ssh_port_t -p tcp 3389

验证ssh端口是否添加成功

    
    
    sudo semanage port -l | grep ssh

![](https://image.3001.net/images/20190121/1548071807_5c45b37fea663.png!small)

添加后重启ssh服务

    
    
    systemctl restart sshd

重启后我们可以尝试用3389登陆

![](https://image.3001.net/images/20190121/1548071825_5c45b39114e4f.png!small)

输入密码后成功登陆。

4）删除22端口号

4.1）编辑sshd_config文件注释掉22端口

4.2）firewall_cmd删除22端口

    
    
    firewall-cmd --zone=public --remove-port=22/tcp --permanent

重载防火墙

    
    
    sudo firewall-cmd --reload

4.3）selinux不用删除22端口或者说你也删除不了，但是不影响我们的需求

![](https://image.3001.net/images/20190121/1548071847_5c45b3a7aeb32.png!small)4.4）重启sshd服务然后尝试用22端口连接victim主机发现是无法连接的使用3389端口是可以的  

![](https://image.3001.net/images/20190121/1548071864_5c45b3b8c47fa.png!small)

策略正常生效

到此加固工作已经完成。

## 七、检测方法

检测需求如下：

> 1\. 能够检测到尝试登陆行为
>
> 2\. 能够检测到登陆成功行为  
>
>
> 3\. 能够检测到登陆成功账户  
>
>
> 4\. 收集用户字典  
>
>
> 5\.
> 记录登录失败的用户名/次数、登录失败用户正确的次数、登录成功的用户名/次数、登陆成功的攻击源IP地址/尝试次数、登录失败的攻击源IP地址/尝试次数（自己可以罗列更详细需求）

检测方法：

我们从secure日志文件分析来开展检测工作，通过对secure日志文件进行分析我们提取如下关键信息。

ssh服务的默认日志记录在/var/log/secure文件中，关于ssh服务的日志存在五种情况。注意标黑和标红的字眼。

1\. 用户名错误用户名错误的日志如下所示：

    
    
    Jan 14 07:37:41 victim sshd[54715]: **Invalid user** **victim1** from 192.168.171.130 port 48550
    
    Jan 14 07:37:41 victim sshd[54715]: input_userauth_request: invalid user victim1 [preauth]

在错误用户的基础上输入密码会出现如下日志

    
    
    Jan 14 07:37:59 victim sshd[54715]: pam_unix(sshd:auth): check pass; user unknown
    
    Jan 14 07:37:59 victim sshd[54715]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.171.130
    
    Jan 14 07:38:01 victim sshd[54715]: **Failed password for invalid user** **victim1** from 192.168.171.130 port 48550 ssh2

2\. 用户名正确但输入错误密码的日志如下所示：

    
    
    Jan 14 07:37:08 victim unix_chkpwd[54691]: password check failed for user (victim)
    
    Jan 14 07:37:08 victim sshd[54689]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.171.130  user=victim
    
    Jan 14 07:37:10 victim sshd[54689]: **Failed password for** **victim** from 192.168.171.130 port 48548 ssh2

3\. 用户名正确且输入正确密码的日志如下所示：

    
    
    Jan 14 07:37:30 victim sshd[54689]: **Accepted password for** **victim** from 192.168.171.130 port 48548 ssh2
    
    Jan 14 07:37:30 victim sshd[54689]: pam_unix(sshd:session): session opened for user victim by (uid=0)

4\. 客户端主动退出ssh连接的日志如下所示

    
    
    Jan 14 07:37:38 victim sshd[54694]: **Received disconnect from 192.168.171.130 port 48548** :11: disconnected by user
    
    Jan 14 07:37:38 victim sshd[54694]: Disconnected from 192.168.171.130 port 48548
    
    Jan 14 07:37:38 victim sshd[54689]: pam_unix(sshd:session): session closed for user victim

5\. 客户端强制关闭ssh连接的日志如下所示

    
    
    Jan 14 07:42:25 victim sshd[54718]: **Connection closed by** 192.168.171.130 port 48552 [preauth]

由上所述，我们需要做的检测策略如下：

1\. 能够检测到尝试登陆行为

1）这里我们设定10秒钟内发现5条存在 invalid user 或者password check
failed语句的记录则表示存在尝试登陆行为（规则可自定义：包括时间和记录数）

2\. 能够检测到登陆成功行为

1）检索所有日志发现存在 accepted password for 语句的记录则判定存在登陆成功情况

3\. 能够检测到登陆成功账户

1）提取日志中匹配到accepted password for关键词语句后面的一个字段

4\. 收集用户字典

1）提取日志中匹配到Invalid user关键词语句后面的一个字段

5\. 记录登录失败的用户名/次数、登录失败用户正确的次数、登录成功的用户名/次数、登陆成功的攻击源IP地址/尝试次数、登录失败的攻击源IP地址/尝试次数  

1）通过各种计算方法来统计如上信息

检查脚本如下：

    
    
    #!/usr/bin/python
    
    #coding:utf-8
    
    from collections import Counter
    
    #定义关键词信息
    
    username_error='Invalid user'
    
    username_correct='password check failed'
    
    username_password_correct='Accepted password for'
    
    user_quit='Received disconnect from'
    
    user_forcequit='Connection closed'
    
    #打开日志文件
    
    f=open('secure','r')
    
    #定义检测方法
    
    def attack_detect():
    
        #用户名错误的请求次数
    
        failed_account=0
    
        #用户名正确且密码错误的请求次数
    
        correct_user_account=0
    
        #用户名正确且密码正确的请求次数  
    
    
        correct_pass_account=0
    
        #记录错误的用户名  
    
    
        failed_user=[]
    
        #记录用户名正确且密码错误的用户名  
    
    
        correct_user=[]
    
        #记录用户名正确且密码正确的用户名  
    
    
        correct_pass=[]
    
        #记录登录失败的ip地址  
    
    
        failed_ipaddr=[]
    
        #记录登录失败&用户名正确的ip地址  
    
    
        correct_ipaddr=[]
    
        #记录登录成功的ip地址  
    
    
        correct_pass_ipaddr=[]
    
        #标志位  
    
    
        alert=True
    
        for i in f:
    
            if username_error in i:
    
                failed_account += 1
    
                failed_user.append(i.split(': ')[1].split()[2])
    
                failed_ipaddr.append(i.split(': ')[1].split()[4])
    
            if username_correct in i:
    
                correct_user_account += 1
    
                correct_user.append(i.split(': ')[1].split('(')[1].strip(')'))
    
            if username_password_correct in i:
    
                correct_pass_account += 1
    
                correct_pass.append(i.split(': ')[1].split()[3])
    
                correct_pass_ipaddr.append(i.split(': ')[1].split()[5])
    
            if failed_account > 30 and alert:
    
                print 'exists ssh enumrate'
    
                alert=False 
    
        #记录登陆失败攻击源IP地址和尝试次数
    
        failed_ipaddr_count=Counter(failed_ipaddr)
    
        failed_ipaddr_dict=dict(failed_ipaddr_count)
    
        #记录登陆成功攻击源IP地址和尝试次数
    
        correct_pass_ipaddr_count=Counter(correct_pass_ipaddr)
    
        correct_pass_ipaddr_dict=dict(correct_pass_ipaddr_count)
    
        #记录登陆失败用户名和次数
    
        failed_user_count=Counter(failed_user)
    
        failed_user_dict=dict(failed_user_count)
    
        #记录登陆失败用户名正确和次数
    
        correct_user_count=Counter(correct_user)
    
        correct_user_dict=dict(correct_user_count)
    
        #记录登陆成功用户名和次数
    
        correct_pass_count=Counter(correct_pass)
    
        correct_pass_dict=dict(correct_pass_count)
    
        #记录所有尝试次数
    
        all_account=failed_account+correct_user_account+correct_pass_account
    
        return all_account,failed_account,correct_user_account,correct_pass_account,failed_user_dict,correct_user_dict,correct_pass_dict,failed_ipaddr_dict,correct_pass_ipaddr_dict

然后执行该脚本可以得出如下结果：

![image.png](https://image.3001.net/images/20190125/1548405967_5c4acccf907ff.png!small)从结果中可以看出该脚本能够满足我们的需求，但是我们需要考虑如何把这段脚本加入到spark
streaming中。

## 八、技术实现

1\. victim主机上的flume配置

![image.png](https://image.3001.net/images/20190130/1548819473_5c511c1143ae5.png!small)
**注意：这里在配置channels选项的时候，增加了下面两个条目：**

    
    
     a1.channels.c1.keep-alive = 60
    
    a1.channels.c1.capacity = 1000000

这里表示增加channels中queue的大小，默认为100，如果使用默认值，当处理大量的日志时就会发生如下报错情况。

![](https://image.3001.net/images/20190130/1548819606_5c511c961562d.png!small)

2\. observer主机上的flume配置

![](https://image.3001.net/images/20190127/1548585155_5c4d88c3a79a8.png!small)3\.
observer上的kafka、zookeeper配置

kafka和zookeeper的配置保持不变即可

4\. spark streaming配置

    
    
    #!/usr/bin/python
    
    #coding:utf-8
    
    from pyspark import SparkContext
    
    from pyspark.streaming import StreamingContext
    
    from pyspark.streaming.kafka import KafkaUtils
    
    from collections import Counter
    
    import datetime
    
    import json
    
    #定义保存的文件名
    
    destname="result.json"
    
    #定义读取文件方法
    
    def readjson(file_name):
    
        with open (file_name,"r") as file_obj:
    
            numbers = json.load(file_obj)
    
            print "读取json文件：",numbers
    
            return numbers
    
    #定义写入文件方法
    
    def writejson(file_name,nums):
    
        with open (file_name,"w") as file_obj:
    
            json.dump(nums,file_obj)
    
            print "写入json文件：",nums
    
    #第一步：创建一个本地的StreamingContext，并设置批处理周期为1s
    
    sc=SparkContext("local[2]","flumeWordCount")
    
    ssc=StreamingContext(sc,1)
    
    #第二步：创建一个kafka连接
    
    topic="streamingtopic"
    
    brokers="hadoop0:9092"
    
    #参数分别表示ssc连接名，列表形式显示的topic名称，brokers列表
    
    directkafkaStream = KafkaUtils.createDirectStream(ssc,[topic],{"metadata.broker.list":brokers})
    
    #第三步：数据处理&转换
    
    #0，提取kafka数据的第一个字段为消息正文字段
    
    lines = directkafkaStream.map(lambda x: x[1])
    
    #1，定义检测方法
    
    def attack_detect(i):
    
        username_error='Invalid user'
    
        username_correct='password check failed'
    
        username_password_correct='Accepted password for'
    
        user_quit='Received disconnect from'
    
        user_forcequit='Connection closed'
    
        failed_account=0
    
        correct_user_account=0
    
        correct_pass_account=0
    
        failed_user=[]
    
        correct_user=[]
    
        correct_pass=[]
    
        failed_ipaddr=[]
    
        correct_ipaddr=[]
    
        correct_pass_ipaddr=[]
    
        alert=True    
    
        if username_error in i:
    
            print username_error
    
            failed_account += 1
    
            failed_user.append(i.split(': ')[1].split()[2])
    
            failed_ipaddr.append(i.split(': ')[1].split()[4])
    
            #print failed_account
    
        if username_correct in i:
    
            #print username_correct
    
            correct_user_account += 1
    
            correct_user.append(i.split(': ')[1].split('(')[1].strip(')').strip(')\n'))
    
        if username_password_correct in i:
    
            #print username_password_correct
    
            correct_pass_account += 1
    
            correct_pass.append(i.split(': ')[1].split()[3])
    
            correct_pass_ipaddr.append(i.split(': ')[1].split()[5])
    
        if failed_account > 5 and alert:
    
            #print 'exists ssh enumrate'
    
            alert=False
    
        total_count=failed_account+correct_user_account+correct_pass_account
    
        #记录登陆失败攻击源IP地址和尝试次数
    
        failed_ipaddr_count=Counter(failed_ipaddr)
    
        failed_ipaddr_dict=dict(failed_ipaddr_count)
    
        #记录登陆成功攻击源IP地址和尝试次数
    
        correct_pass_ipaddr_count=Counter(correct_pass_ipaddr)
    
        correct_pass_ipaddr_dict=dict(correct_pass_ipaddr_count)
    
        #记录登陆失败用户名和次数
    
        failed_user_count=Counter(failed_user)
    
        failed_user_dict=dict(failed_user_count)
    
        #记录登陆失败用户名正确和次数
    
        correct_user_count=Counter(correct_user)
    
        correct_user_dict=dict(correct_user_count)
    
        #记录登陆成功用户名和次数
    
        correct_pass_count=Counter(correct_pass)
    
        correct_pass_dict=dict(correct_pass_count)
    
        #这里将处理的数据以字典的形式保存到json文件中，每次从json文件中读取变量值并跟处理的结果进行累加
    
        nums=[{"total_count":total_count,"failed_account":failed_account,"correct_user_account":correct_user_account,"correct_pass_account":correct_pass_account,"failed_ipaddr_count":failed_ipaddr_count,"failed_ipaddr_dict":failed_ipaddr_dict,"correct_pass_ipadd_count":correct_pass_ipaddr_count,"correct_pass_dict":correct_pass_dict,"correct_pass_ipaddr_dict":correct_pass_ipaddr_dict,"failed_user_count":failed_user_count,"failed_user_dict":failed_user_dict,"correct_user_count":correct_user_count,"correct_user_dict":correct_user_dict}]
    
        rs_old = readjson(destname)
    
        for i in nums:
    
            for j in rs_old:
    
                for k,v in j.items():
    
                    if isinstance(v,dict):
    
                        for m,n in v.items():
    
                            try:
    
                                i[k][m] = i[k][m] + j[k][m]
    
                            except KeyError as e:
    
                                i[k][m] = j[k][m]
    
                    else:
    
                        i[k] = i[k] + j[k]
    
        writejson(destname,nums)
    
    #第四步：数据输出，这里选择打印出去
    
    pairs=lines.map(lambda x:attack_detect(x))
    
    pairs.pprint()
    
    #第五步：开始sparkstreaming
    
    ssc.start()
    
    ssc.awaitTermination()

5\. 启动各个组件

1）先启动zookeeper和kafka

    
    
     ./zkServer.sh start
    
    ./bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties

2）然后启动flume-server端（先监听，后发送）

    
    
    ./bin/flume-ng agent --name a1 --conf $FLUME_HOME/conf --conf-file $FLUME_HOME/conf/collect-ssh-kafka.conf -Dflume.root.logger=INFO,console

3）启动flume-client端（监听文件，发送数据到server端）

    
    
    sudo ./flume-ng agent --name a1 --conf $FLUME_HOME/conf --conf-file $FLUME_HOME/conf/send-ssh.conf -Dflume.root.logger=INFO,console

4）启动spark-streaming

    
    
    ./bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 examples/src/main/python/streaming/sshdirect.py

6\. 模拟攻击者向victim发起ssh爆破行为

    
    
    hydra -L user -P pass ssh://192.168.171.121:3389

![image.png](https://image.3001.net/images/20190130/1548819938_5c511de23be8e.png!small)然后我们查看result.json文件中的内容不断实时更新，攻击完成后的最终结果如下：

![image.png](https://image.3001.net/images/20190130/1548820070_5c511e6660d3d.png!small)

由上所述我们能够看到文件记录了ssh总攻击次数、用户名错误尝试次数、用户名正确登陆次数以及登陆源ip地址等信息。

 **注：**

1\. 这里我使用的是以文件形式进行存储的，没有使用mysql数据库，理论上方法是一样的，这里我就不演示了，有兴趣的小伙伴可以自己搞

2\. 这里的result.json文件内容是固定的，必须要跟spark
streaming脚本中的变量格式一致，否则可能会出现问题，后面附录中我会把格式文件贴上来

## 九、图形页面展示

这里我就以一个例子来展示吧，以条形图的形式展示登陆失败的用户情况。

1，django环境安装

注：已安装django环境的自动忽略

1）使用virtualenv环境

    
    
    virtualenv -p /usr/bin/python3 myechart
    
    source myechart/bin/activate
    
    pip install django==1.11.4
    
    pip install pyecharts

2）新建django项目和app程序

    
    
    django-admin startproject myechart
    
    cd sshechart
    
    python manage.py startapp  sshechart

编辑myechart/settings.py文件，注册应用程序：

![](https://image.3001.net/images/20190131/1548902719_5c52613fcd970.png!small)编辑sshechart的urls文件，该文件默认不存在，需要创建。内容如下：

    
    
    from django.conf.urls import url
    
    from . import views
    
    urlpatterns = [
    
        url(r'^$', views.index, name='index'),
    
    ]

编辑myechart的urls文件，更新内容如下：

![image.png](https://image.3001.net/images/20190131/1548902817_5c5261a131f6d.png!small)2\.
数据处理

1）编辑views.py文件内容如下：

    
    
    from __future__ import unicode_literals
    
    import math
    
    from django.http import HttpResponse
    
    from django.template import loader
    
    from pyecharts import Line
    
    from django.shortcuts import render
    
    import json
    
    # Create your views here.
    
    #加载echart.js文件
    
    REMOTE_HOST = "<https://pyecharts.github.io/assets/js>"
    
    def index(request):
    
        #指定模板文件
    
        template = loader.get_template('sshechart/index.html')
    
        attack_line=line1()
    
        context = dict(
    
            myechart=attack_line.render_embed(),
    
            host=REMOTE_HOST,
    
            script_list=attack_line.get_js_dependencies()
    
        )
    
        return HttpResponse(template.render(context, request))
    
    def line1():
    
        #Line图需要指定x轴和y轴数据
    
        x_raw=[]
    
        y_raw=[]
    
        with open('result.json') as f:
    
            numbers = json.load(f)
    
            for i in numbers:
    
                dic=i["failed_user_dict"]
    
                print (dic)
    
                for k,v in dic.items():
    
                    x_raw.append(k)
    
                    y_raw.append(v)
    
        line_attack=Line("登陆失败用户",title_pos="45%")
    
        line_attack.add("",x_raw,y_raw,mark_point=["max","min"],is_datazoom_show=True,datazoom_type="inside")
    
        return line_attack

2）创建模板index.html文件

在sshechart目录下创建templates/sshechart目录。

![image.png](https://image.3001.net/images/20190131/1548903873_5c5265c17e3b0.png!small)

并编辑index.html文件，内容如下：

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
        <meta charset="utf-8">
    
        <title>Proudly presented by PycCharts</title>
    
        {% for jsfile_name in script_list %}
    
            <script src="{{ host }}/{{ jsfile_name }}.js"></script>
    
        {% endfor %}
    
    </head>
    
    <body>
    
      {{ myechart|safe }}
    
    </body>
    
    </html>

3\. 运行程序

运行程序后，在浏览器中打开目标网站，如下所示：

![image.png](https://image.3001.net/images/20190131/1548903126_5c5262d68b13b.png!small)同样的，还可以多添加几个echart图，增加分析维度。

也可以将这个里面的源代码拷贝下来集成到其他web程序中。

至此，这个课题就此结束，期间也是碰到各种问题，拖延了不少时间，好在最终是搞定了，希望大家能够在这里有所收获，也希望大家能够指出文章的不足之处，共勉之。

## 附录：

1\. result.json文件格式

    
    
    [{"failed_account": 0, "correct_user_dict": {}, "correct_pass_ipaddr_count": {}, "correct_pass_account": 0, "failed_ipaddr_dict": {}, "failed_user_dict": {}, "correct_pass_ipaddr_dict": {}, "correct_pass_dict":{},"total_count": 0, "correct_pass_ipadd_count": {}, "correct_user_count": {}, "correct_user_account": 0, "failed_user_count": {}, "failed_ipaddr_count": {}}]

 ***本文作者：gncao，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

