# HackTheBox Cyber Apocalypse 2021 CTF

阅读量 **219773**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-18 16:30:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t010857db12123596ef.png)

## 数字取证题目Key mission

大家好我是来自Tiger-Team的evi1_f4iry，近期刚刚和小伙伴们组队TigerEyes，完成了为期一周的Cyber Apocalypse
2021 CTF线上赛，队伍最终排名第15。

我将陆续在此分享一些我在队伍中负责解出的题目，本文为取证题Key mission。

### 题目信息

Key mission

实际完成该题目的人数：691

题目线索：

“The secretary of earth defense has been kidnapped. We have sent out elite
team on the enemy’s base to find his location. Our team only managed to
intercept this traffic. You mission is to retrieve secretary’s hidden
location.

地球防务部长被绑架了，我们已经派出我们的精英队伍去找寻他的下落。 我们的队伍只截获了这些流量。你的任务是找到部长被藏匿的地点。

题目数据包解压后是一个名为“key_mission.pcap”的流量数据包。

从文件大小和信息来看，应该只是很普通的USB流量包。

Wireshark打开查看。

通过分析功能，再次确认了确实只是个单纯的usb数据包（对题目难度产生了怀疑）

尝试通过设备信息确认是那种设备，但是并没有显示能进一步确认的线索。

通过观察数据包内的数据，可以推断usb设备应该为键盘。

因为HID Data数据长度为八个字节。主要信息集中在第三个字，应为usb键盘。

查看整个流量包，并没有发现新的线索。显然只能按照传统的usb键盘题解法进行处理。

我只需要有HID Data的包，这可以通过usbhid.data先进行过滤查看一下，没有特殊的。

使用tshark将HID Data部分的数据导出并直接去除空行，为接下来的数据处理提供方便。

tshark -r key_mission.pcap -T fields -e usbhid.data | sed ‘/^$/d’ > key.txt

当我导出这个数据后我使用了几个比较常用的键盘数据转换的CTF脚本。这些脚本提出的flag都无法提交，显然这些脚本都是将一些功能按键通过脚本直接处理得到最终flag，这已经不是我现在需要的了，此时我需要完整的解析每一个按键，而不是将shift，backspace，CapsLock这些功能键直接处理掉，这样我才能看清到底发生了什么，我找到一个可以直接输出的脚本，并进行了一些简单的修改  
如下：

    
    
    #!/usr/bin/python
    # coding: utf-8
    from __future__ import print_function
    import sys,os
    
    #declare -A lcasekey
    lcasekey = {}
    #declare -A ucasekey
    ucasekey = {}
    
    #associate USB HID scan codes with keys
    #ex: key 4  can be both "a" and "A", depending on if SHIFT is held down
    lcasekey[4]="a";           ucasekey[4]="A"
    lcasekey[5]="b";           ucasekey[5]="B"
    lcasekey[6]="c";           ucasekey[6]="C"
    lcasekey[7]="d";           ucasekey[7]="D"
    lcasekey[8]="e";           ucasekey[8]="E"
    lcasekey[9]="f";           ucasekey[9]="F"
    lcasekey[10]="g";          ucasekey[10]="G"
    lcasekey[11]="h";          ucasekey[11]="H"
    lcasekey[12]="i";          ucasekey[12]="I"
    lcasekey[13]="j";          ucasekey[13]="J"
    lcasekey[14]="k";          ucasekey[14]="K"
    lcasekey[15]="l";          ucasekey[15]="L"
    lcasekey[16]="m";          ucasekey[16]="M"
    lcasekey[17]="n";          ucasekey[17]="N"
    lcasekey[18]="o";          ucasekey[18]="O"
    lcasekey[19]="p";          ucasekey[19]="P"
    lcasekey[20]="q";          ucasekey[20]="Q"
    lcasekey[21]="r";          ucasekey[21]="R"
    lcasekey[22]="s";          ucasekey[22]="S"
    lcasekey[23]="t";          ucasekey[23]="T"
    lcasekey[24]="u";          ucasekey[24]="U"
    lcasekey[25]="v";          ucasekey[25]="V"
    lcasekey[26]="w";          ucasekey[26]="W"
    lcasekey[27]="x";          ucasekey[27]="X"
    lcasekey[28]="y";          ucasekey[28]="Y"
    lcasekey[29]="z";          ucasekey[29]="Z"
    lcasekey[30]="1";          ucasekey[30]="!"
    lcasekey[31]="2";          ucasekey[31]="@"
    lcasekey[32]="3";          ucasekey[32]="#"
    lcasekey[33]="4";          ucasekey[33]="$"
    lcasekey[34]="5";          ucasekey[34]="%"
    lcasekey[35]="6";          ucasekey[35]="^"
    lcasekey[36]="7";          ucasekey[36]="&"
    lcasekey[37]="8";          ucasekey[37]="*"
    lcasekey[38]="9";          ucasekey[38]="("
    lcasekey[39]="0";          ucasekey[39]=")"
    lcasekey[40]="<enter>";      ucasekey[40]="<ENTER>"
    lcasekey[41]="<esc>";        ucasekey[41]="<ESC>"
    lcasekey[42]="<del>";        ucasekey[42]="<Del>"
    lcasekey[43]="<tab>";        ucasekey[43]="<TAB>"
    lcasekey[44]="<space>";      ucasekey[44]="<SPACE>"
    lcasekey[45]="-";          ucasekey[45]="_"
    lcasekey[46]="=";          ucasekey[46]="+"
    lcasekey[47]="[";          ucasekey[47]="{"
    lcasekey[48]="]";          ucasekey[48]="}"
    lcasekey[49]="\\";         ucasekey[49]="|"
    lcasekey[50]=" ";          ucasekey[50]=" "
    lcasekey[51]=";";          ucasekey[51]=":"
    lcasekey[52]="'";          ucasekey[52]="\""
    lcasekey[53]="`";          ucasekey[53]="~"
    lcasekey[54]=",";          ucasekey[54]="<"
    lcasekey[55]=".";          ucasekey[55]=">"
    lcasekey[56]="/";          ucasekey[56]="?"
    lcasekey[57]="<capslook>";   ucasekey[57]="<CAPSLOOK>"
    lcasekey[79]="<r_arrow>"; ucasekey[79]="<R_ARROW>"
    lcasekey[80]="<l_arrow>";  ucasekey[80]="<L_ARROW>"
    lcasekey[84]="/";          ucasekey[84]="/"
    lcasekey[85]="*";          ucasekey[85]="*"
    lcasekey[86]="-";          ucasekey[86]="-"
    lcasekey[87]="+";          ucasekey[87]="+"
    lcasekey[88]="<num_enter>";      ucasekey[88]="<NUM_ENTER>"
    lcasekey[89]="1";          ucasekey[89]="1"
    lcasekey[90]="2";          ucasekey[90]="2"
    lcasekey[91]="3";          ucasekey[91]="3"
    lcasekey[92]="4";          ucasekey[92]="4"
    lcasekey[93]="5";          ucasekey[93]="5"
    lcasekey[94]="6";          ucasekey[94]="6"
    lcasekey[95]="7";          ucasekey[95]="7"
    lcasekey[96]="8";          ucasekey[96]="8"
    lcasekey[97]="9";          ucasekey[97]="9"
    lcasekey[98]="0";          ucasekey[98]="0"
    lcasekey[99]=".";          ucasekey[99]="."
    
    #make sure filename to open has been provided
    if len(sys.argv) == 2:
        keycodes = open(sys.argv[1])
        for line in keycodes:
            #dump line to bytearray
            bytesArray = bytearray.fromhex(line.strip())
            #see if we have a key code
            val = int(bytesArray[2])
            if val > 3 and val < 100:
                #see if left shift or right shift was held down
                if bytesArray[0] == 0x02 or bytesArray[0] == 0x20 :
                    print(ucasekey[int(bytesArray[2])], end=''),  #single line output
                    #print(ucasekey[int(bytesArray[2])])            #newline output
                else:
                    print(lcasekey[int(bytesArray[2])], end=''),  #single line output
                    #print(lcasekey[int(bytesArray[2])])            #newline output
    else:
        print("USAGE: python %s [filename]" % os.path.basename(__file__))

执行后得到结果如下

    
    
    I<space>aam<space>ssendinf<del><del>g<space>ssecrretary's<space>loccation<space>oveer<space>this<space>tottally<space>encrypted<space>channel<space>to<space>make<space>surre<space>no<space>one<space>elsse<space>will<space>be<space>able<space>to<space><space>rreeat<del><del>d<space>itt<space>exceppt<space>of<space>us.<space>Tthis<space>informmaation<space>iss<space>confiddential<space>and<space>must<space>not<space>be<space>sharred<space>with<space>anyone<space>elsse.<space>Tthe<space><space>ssecrretary's<space>hidden<space>looccation<space>is<space>CHTB{a_place=3<del><del>-3<del><del>_3<del><del><del>3_fAr_fAar_awway_ffr0m_eearth}<enter>

检查了一下并没有按下CapsLock的记录，直接拿出flag部分

CHTB{a_place=3<del><del>-3<del><del>_3<del><del><del>3_fAr_fAar_awway_ffr0m_eearth}<enter>

按照删除键删除对应的字符得到

CHTB{a_plac3_fAr_fAar_awway_ffr0m_eearth}

再次提交，此flag仍然是错误的。但是检查脚本并未发现任何错误。

我需要再次回到流量包仔细检查flag部分的流量发生了什么

首先查一下flag段的流量一共有几个包，每一个按键即为一个包。简单修改一下脚本，将每个按键的原始数据输出出来，并将原本的不换行print改为换行。

运行后在输出中找到CHTB{这个flag开头标准，向下逐个检查。

通过仔细查看，我们可以发现按键和数据的对应。

这些数据只在flag的fAr_fAar的第二个fAar部分出现了奇怪的现象，按照我发现的规律，如果第二个far在flag中为fAr，则数据应与第一个far一样为

    
    
    0000090000000000
    f
    0000000000000000
    
    0200000000000000
    0200040000000000
    A
    0200000000000000
    0000000000000000
    
    0000150000000000
    r
    0000000000000000

如果正确flag为fAar，那数据按照规律应为

    
    
    0000090000000000
    f
    0000000000000000
    
    0200000000000000
    0200040000000000
    A
    0200000000000000
    0000000000000000
    
    0000040000000000
    a
    0000000000000000
    
    0000150000000000
    r
    0000000000000000

而实际数据显然与两种可能性都不相符

对比实际数据和预期数据：

![](https://p4.ssl.qhimg.com/t0138af5bbee75c15fe.png)

所以，这道题不是key mission，而是key missing

两种可能性，一是连续按了两个大写的A，一个是根本没按第二个a键，只是传输错误。

分别尝试提交，最终flag为

CHTB{a_plac3_fAr_fAr_awway_ffr0m_eearth}

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **evi1_f4iry** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/240615](/post/id/240615)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t01af37a39308d02728.png) evi1_f4iry

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

