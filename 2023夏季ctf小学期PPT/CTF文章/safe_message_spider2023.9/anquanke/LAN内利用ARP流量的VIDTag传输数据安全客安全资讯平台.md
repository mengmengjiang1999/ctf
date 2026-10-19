# LAN内利用ARP流量的VID Tag传输数据

阅读量 **440438**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-22 15:30:56

 **x**

##### 译文声明

本文是翻译文章，文章原作者 DamonMohammadbagher，文章来源：github.com

原文地址：<https://github.com/DamonMohammadbagher/NativePayload_ARP2/blob/master/Article/Sending%20DATA%20via%20ARP%20broadcast%20Traffic%20to%20all%20systems%20in%20(LAN)%20by%20(vid%20tag).pdf>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01ab17a7c461e1732b.jpg)

## 0x00 前言

这篇文章中我想就ARP流量再一次进行讨论，在此之前，于我的上一篇[文章](https://www.peerlyst.com/posts/transfer-backdoor-payloads-by-arp-traffic-and-bypassing-avs-damon-mohammadbagher)
中我们已经谈论过这个话题——通过ARP流量传输数据，以及使用[NativePayload_ARP.sh](https://github.com/DamonMohammadbagher/NativePayload_ARP/blob/master/For_Linux_Macchanger/Macchange.sh)
来更改MAC地址。这是一种常见且有用的方式用以在2层的局域网主机之间传输数据，对于建立了桥接的物理主机与虚拟主机同样有效。

但使用这种方法，你发送数据的主机MAC地址总是在不断变化。Now，在这篇文章中我将介绍一种不用改变MAC地址就可以利用ARP流量传输数据的新方法。

在此方法中，我们可以通过ARP流量的`VID Tag`发送数据给局域网内的所有主机。

## 0x01 声明

  1. 这篇文章中我不想再讨论如何在Windows系统下实现，以及如何使用`C#`来编写相关工具。这次我想在Linux系统下实现，同时编写一个简单的`Shell`脚本来实现该方法。
  2. 我不是一个专业的`Bash Shell`程序员，但我想，我们可以很轻松地完成这项工作。
  3. 举个例子，我们想通过ARP流量的`VID Tag`传送”Are you going to Scarborough Fair?”给局域网内的所有主机。
  4. 

## 0x02 为什么是VID Tag?

简单来说，因为这是一种正常且合法的行为用以改变ARP数据包中的字节。我认为，这种方法可以很好地躲避局域网内嗅探工具或者杀软的检测。但确保你仅在测试环境中使用此方法。

## 0x03 如何使用VID Tag作为Payload?

为了解释方便，我们需要一段文本，就让我们使用”Are you going to Scarborough
Fair?”这段文本。你需要将这段文本分成字节块，然后你就可以使用每个字符的十六进制字节块来作为`VID Tag`。

让我来通过命令一步步地解释。

使用下面这条命令，你可以轻松地看到每个字符的字节表示。这种情况下，我将该字符串分成每行10个字符显示：

    
    
    echo "Are you going to Scarborough Fair?" | xxd -c 10
    0000000: 4172 6520 796f 7520 676f Are you go
    000000a: 696e 6720 746f 2053 6361 ing to Sca
    0000014: 7262 6f72 6f75 6768 2046 rborough F
    000001e: 6169 723f 0a               air?.
    

正如你看到的，第一行是下面这段：

    
    
    0000000: 4172 6520 796f 7520 676f Are you go
    
    bytes=char
    41='A'
    72='r'
    65='e'
    20=' '
    79='y'
    ...
    

如果我们想把’A’作为Payload通过`VID Tag`传输的话，那么我们应该注入`0x41`到ARP广播包中。但是如何才能做到？

## 0x04 一步步地教你如何发送“定制”ARP广播包

关于`VID/Vlan-ID Tag`有一点要郑重说明：你的`Vlan-ID`必须位于0-4094之间。所以我们只能使用整数。

###  0x04.1 准备工作

首先，我们需要知道在Linux下如何使用命令发送ARP广播包，如何在广播包中使用我们的`Vlan-ID`。

使用下面这些命令我们可以轻松地拥有一个“新”VLAN和Vlan-ID：

    
    
    root@kali:~# ip link add link eth0 name Vlanx type vlan id 13
    root@kali:~# ip addr add 192.168.110.1/24 brd 192.168.110.255 dev Vlanx
    root@kali:~# ip link set dev Vlanx up
    

![](https://s2.ax1x.com/2019/08/19/m1zcXF.png)

正如你看到的，我们拥有了一个新的VLAN网络接口，它的VID是13，IP地址池是192.168.110.1/24，广播地址是192.168.110.255。

到目前为止，我们已经创建了一个VLAN，但接下来我们需要知道如何在LAN中发送这个VLAN的ARP广播包。

###  0x04.2 发送广播包

这是关键的一步，如何自动发送ARP广播包？为什么要这样做？

先来回答第二个问题：为什么要这样做？

因为我们使用下面这条命令后，将Payload作为`VID Tag`注入到了广播包中：

    
    
    root@kali:~# ip link add link eth0 name Vlanx type vlan id 13
    

这就意味着：你的ARP广播包会携带着`VID Tag`，同时LAN内的所有主机都会接收到这个带有`13`的ARP广播包。

下面回答第一个问题：如何自动发送ARP广播包？

你可以使用一个简单的技巧，如何你想发送ARP广播包的话，你只需发送对`192.168.110.1/24`内某一主机的PING请求即可。目标主机IP地址应该位于`192.168.110.2`到`192.168.110.254`之间。

另外，当你PING某一主机时，因为你PING的主机不存在，所以在每次PING请求之前会持续发送ARP请求。也就是说，如果你发送两次PING请求(例如：ping
192.168.110.2)，至少会有两次对192.168.110.2的ARP请求。

让我来给你展示一下：

![](https://s2.ax1x.com/2019/08/19/m1zR0J.png)

## 0x05 抓取数据包

使用下面这条命令你可以很好地抓取ARP广播包：

![](https://s2.ax1x.com/2019/08/19/m1z2m4.png)

下面是`tcpdump`命令的输出内容：

    
    
    root@kali:~# tcpdump -XX -v broadcast | grep 0x0000
    tcpdump: listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
    0x0000: ffff ffff ffff 0800 279c 70b1 8100 000d ........'.p.....
    0x0000: ffff ffff ffff 0800 279c 70b1 8100 000d ........'.p.....
    0x0000: ffff ffff ffff 0800 279c 70b1 8100 000d ........'.p.....
    

在`0x0000`行， “ffff ffff ffff”和“000d”这两个字段非常重要：

    
    
    0x0000: ffff ffff ffff 0800 279c 70b1 8100 000d ........'.p.....
    

“ffff ffff ffff”：代表这是ARP广播包（发送给LAN中所有主机）。  
“000d”：你的`VID Tag`。

    
    
     printf “%x” 13 ===> d
    

如果你不使用`grep`命令对`tcpdump`的结果进行处理，结果可能是下面这个样子：

    
    
    root@kali:~# tcpdump -XX -v broadcast 
    tcpdump: listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
    13:09:44.640827 ARP, Ethernet (len 6), IPv4 (len 4), Request who-has 192.168.110.2 tell kali, length 28
    0x0000: ffff ffff ffff 0800 279c 70b1 8100 000d ........'.p.....
    0x0010: 0806 0001 0800 0604 0001 0800 279c 70b1 ............'.p.
    13:09:45.637062 ARP, Ethernet (len 6), IPv4 (len 4), Request who-has 192.168.110.2 tell kali, length 28
    0x0000: ffff ffff ffff 0800 279c 70b1 8100 000d ........'.p.....
    0x0010: 0806 0001 0800 0604 0001 0800 279c 70b1 ............'.p.
    

下面两张图片将会为你展示，如何在Linux下通过改变VID将`VID Tag`由13变为4094：

![](https://s2.ax1x.com/2019/08/19/m1zW79.png)

![](https://s2.ax1x.com/2019/08/19/m1z66U.png)

    
    
     printf “%x” 4094 ===> ffe
    

正如你看到的，代表VID的字节从`0x000d`变为`0x0ffe`，即从13变为4094。

## 0x06 脚本实现

你是否还记得 “Are you going to Scarborough
Fair?”这段文本，如果我们想将这段文本作为Payload发送，那么现在你应该知道了如何去实现它。

    
    
    echo "Are you going to Scarborough Fair?" | xxd -c 10
    0000000: 4172 6520 796f 7520 676f Are you go
    000000a: 696e 6720 746f 2053 6361 ing to Sca
    0000014: 7262 6f72 6f75 6768 2046 rborough F
    000001e: 6169 723f 0a             air?.
    

我们将第一行作为示例：

    
    
    0000000: 4172 6520 796f 7520 676f Are you go
    
    byte=char
    41 = 'A'
    72 = 'r'
    65 = 'e'
    20 = ' '
    79 = 'y'
    …
    

这表示我们发送第一个字符`A`时，我们的`VID Tag`应该是`0x41`。现在，我们可以通过下面的命令将它注入到我们的ARP广播包中：

    
    
    root@kali:~# echo $(echo "A" | xxd -p -c 1 )
    41 0a
    root@kali:~# ops=`echo $(echo "A" | xxd -p -c 1)`
    root@kali:~# echo "${ops::-2}"
    41 
    root@kali:~# ops2=`echo "${ops::-2}"`
    root@kali:~# echo $ops2
    41
    root@kali:~# echo $((0x$ops2))
    65
    root@kali:~# 
    

![](https://s2.ax1x.com/2019/08/19/m1zhkR.png)

下面来解释一下上面的代码。

使用下面的命令你会得到`A`的十六进制字节表示：

    
    
    root@kali:~# echo $(echo "A" | xxd -p -c 1 )
    41 0a
    root@kali:~# ops=`echo $(echo "A" | xxd -p -c 1)`
    root@kali:~# echo "${ops::-2}"
    41 
    root@kali:~# ops2=`echo "${ops::-2}"`
    root@kali:~# echo $ops2
    

下面这条命令将其转换为十进制：

    
    
    root@kali:~# echo $((0x$ops2))
    65
    root@kali:~# 
    

所以，我们的结果应该是：A=> 0x41(bytes) => 65(Decimal)。你的`VID Tag`就是65。

    
    
    root@kali:~# ip link add link eth0 name Vlanx type vlan id 65
    root@kali:~# ip addr add 192.168.110.1/24 brd 192.168.110.255 dev Vlanx
    root@kali:~# ip link set dev Vlanx up
    root@kali:~# ping 192.168.110.2
    

下一步就是从ARP广播包中接收这些字节：

![](https://s2.ax1x.com/2019/08/19/m1z4t1.png)

现在你可以使用下面这个简单的脚本来实现上面的步骤：

    
    
    #!/bin/sh
    mytext="Are you going to Scarborough Fair?"
    for text in `echo $mytext | xxd -p -c 1`;
        do
            ops=`echo $(echo $text)`
            vlanID=`echo $((0x$ops))`
            echo "bytes: " $ops "VID Decimal: " $vlanID
    
            `ip link add link "eth0" name "Vlanx" type vlan id $vlanID`
            sleep 0.3
            `ip addr add 192.168.110.1/24 brd 192.168.110.255 dev Vlanx`
            sleep 0.3
            `ip link set dev Vlanx up`
            sleep 0.2
            ping 192.168.110.2 -c 2 | grep "ops" &
            sleep 1.8
            `ip link delete Vlanx`
        done
    

从下面这张图片中你可以看到脚本的执行结果：

![](https://s2.ax1x.com/2019/08/19/m1zop6.png)

正如你从这些图片中看到的那样，我们实现了通过带有`VID Tag`的ARP广播包将文本发送给LAN中的所有主机。

## 0x06 如何使用NativePayload_ARP2.sh

现在我想谈论一下NativePayload_ARP2.sh这个脚本，使用该脚本你可以通过ARP广播发送文本文件以及接收文本文件。该脚本有两种使用方法。

###  0x06.1 双方都使用NativePayload_ARP2.sh

在该方法中，你可以这样来做：

    
    
    Step1: (System A ) ./NativePayload_ARP2.sh -listen (Packet Number)
    
    Step2: (System B ) ./NativePayload_ARP2.sh -send TextFile.txt [VlanName] [vlan-Subnet/mask] [vlan-Broadcast] -p [vlan-    PingIPv4] [(wlan0,eth0,vboxnet0,etc.)]
    

这种情况下，你既可以使用该脚本来发送数据，亦可以使用它来接收。下面的图片中我使用了3台主机进行演示：一台物理机(IP地址：192.168.56.1)和两台虚拟机(IP地址分别是192.168.56.101,192.168.56.102)。

重点在于`-listen (Packet Number)`：你的`Packet Number`应该是`文本文件长度*2`。

    
    
     # cat test.txt | xxd -c 10
    
     0000000: 5365 6e64 696e 6720 4441 Sending DA
     000000a: 5441 2076 6961 2041 5250 TA via ARP
     0000014: 2042 726f 6164 6361 7374 Broadcast
     000001e: 2026 2056 4944 0a        & VID.
    

正如你看到的，文本文件长度是36Bytes，所以你的`Packet Number`应该是72。

![](https://s2.ax1x.com/2019/08/19/m1zT1K.png)

下面的图片中你可以看到这种方法的结果：

![](https://s2.ax1x.com/2019/08/19/m1z76O.png)

从图片中你可以看出脚本使用`tcpdump`工具接收到72个ARP广播包，接收到的文本内容是“Esending DATA via ARERP
Broadcast & VI”，这个结果是不是看起来有些不太好？

    
    
     “Esending DATA via ARERP Broadcast & VI”
    

结果中的“E”是LAN内不知从何处而来的两个广播包中的数据，恰好被脚本接收到。不过你可以根据你的想法来改进代码，解决这个问题。

###  0x06.2 一方使用NativePayload_ARP2.sh，另一方使用tcpdump

在该方法中，你可以使用脚本发送数据，同时接收端使用`tcpdump`接收数据。  
你应当使用下面的命令：

    
    
    Step1: (System A ) tcpdump -XX -v broadcast | grep 0x0000
    
    Step2: (System B ) ./NativePayload_ARP2.sh -send TextFile.txt [VlanName] [vlan-Subnet/mask] [vlan-Broadcast] -p [vlan-    PingIPv4] [(wlan0,eth0,vboxnet0,etc.)]
    

![](https://s2.ax1x.com/2019/08/19/m1zqne.png)

![](https://s2.ax1x.com/2019/08/19/m1zL0H.png)

![](https://s2.ax1x.com/2019/08/19/m1zO7d.png)

## 0x07 总结

一个简单的脚本让你可以通过ARP广播包的`VID
Tag`来传输数据给LAN内所有主机，无论是物理机传输给物理机还是物理机传输给虚拟机，同时这种方法是躲避某些AV(Anti-Virus)或是LAN内监测工具的一种很好的方式，但一定要确保你仅在测试环境中使用此方法。

脚本地址：[Github](https://github.com/DamonMohammadbagher/NativePayload_ARP2)

视频：[Youtube](https://www.youtube.com/watch?v=C4fB7NQJHO4)

## 译者的话：

  1. `0x00 前言`部分提到的[NativePayload_ARP.sh](https://github.com/DamonMohammadbagher/NativePayload_ARP/blob/master/For_Linux_Macchanger/Macchange.sh) 并非`NativePayload_ARP.sh`，而是`Macchange.sh`，我的链接已经指向了它；
  2. 文章的结构划分在原文中并没有体现，译者自作主张将文章根据其内容划分成了7个小节；
  3. 作者在Github中给出了视频链接，一并放于文章末尾，以供读者观看；

作者脚本中listen功能实现中的

    
    
     tcpdump -c $2 -XX -v "broadcast" | grep -e 0806 -e "ffff ffff ffff" | grep 0x0000: | awk {'print $9'}
    

这行代码，译者在实践过程修改为：

    
    
         tcpdump -XX broadcast | grep -E '0x0010.*0806|0x0000.*8100' | grep '0x0000:' | awk  {'print $9'}
    

至于为何这样修改，作者在`0x06.1`已经提到了，不再赘述。译者水平有限，如果读者有更好的修改方案请不吝赐教。

本文翻译自github.com
[原文链接](https://github.com/DamonMohammadbagher/NativePayload_ARP2/blob/master/Article/Sending%20DATA%20via%20ARP%20broadcast%20Traffic%20to%20all%20systems%20in%20\(LAN\)%20by%20\(vid%20tag\).pdf)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERFZE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/184519](/post/id/184519)

安全客 - 有思想的安全新媒体

本文转载自:
[github.com](https://github.com/DamonMohammadbagher/NativePayload_ARP2/blob/master/Article/Sending%20DATA%20via%20ARP%20broadcast%20Traffic%20to%20all%20systems%20in%20\(LAN\)%20by%20\(vid%20tag\).pdf)

如若转载,请注明出处：
<https://github.com/DamonMohammadbagher/NativePayload_ARP2/blob/master/Article/Sending%20DATA%20via%20ARP%20broadcast%20Traffic%20to%20all%20systems%20in%20(LAN)%20by%20(vid%20tag).pdf>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全研究](/tag/安全研究)
  * [ARP](/tag/ARP)

 **+1** __7赞

 __收藏

![](https://p4.ssl.qhimg.com/t01a9ce08613e49eaf2.png) ERFZE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

