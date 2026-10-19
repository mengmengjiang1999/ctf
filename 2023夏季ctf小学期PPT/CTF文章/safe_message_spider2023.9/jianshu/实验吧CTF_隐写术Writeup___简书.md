实验吧CTF-隐写术Writeup

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF-隐写术Writeup

### 实验吧-隐写术-欢迎来到地狱Writeup

压缩包解压后图片损坏，那么修复，丢进 winhex修复（工具自行google）

jpg的文件头：FFD8FFE1

image.png

  

右击编辑---添加0字节---填写4 然后前八位改为FFD8FFE1

  

image.png

  

image.png

  

网盘地址（注意大小写）进去以后下载音频---摩斯密码  
这摩斯密码听得我怀疑人生。。。。。。。。实在太模糊 密码是：letusgo  
打开以后word文件如图所示

  

image.png

附上 摩斯密码表

    
    
    摩尔斯电码又称摩斯电码，它有两种“符号”用来表示字元：点（·）和划（—
    ），或分别叫滴（Dit）和嗒
    （Dah）或长和短。点的长度，请注意("—",="-","·"="*")！
    决定了发报的速度，并且被当作发报时间参考。下面是时间控制的图示： 摩尔斯
    电码表 
    　　Morse code：—— ——— ·—· ··· · / —·—· ——— —·· 
    · 
    　　这里，“—”表示划，“·”表示点。这是上面消息的准确发报时间（“=”
    表示信号有，“.”代表信
    号无，每个为一个点的长度）： 
    　　
    ===.===...===.===.===...=.===.=...=.=.=...=.......===.=.===.=...===.===
    .=== 
    　　划一般是三个点的长度；点划之间的间隔是一个点的长度；字元之间的间隔
    是三个点的长度；单词之间
    的间隔是七个点的长度。初学者往往被教导发送点划间隔短小、短而快的字元，
    并且在符号和单词之间夸大
    间隔时间。比较起来，这种方式更加容易学会。 
    　　熟悉摩尔斯码的人之间经常象这样说话或拼写［其中，“长音（Dah）”发“
    awe”的音］： 
    　　—— ——— ·—· ··· · / —·—· ——— —·· · 
    　　DahDah DahDahDah DiDahDit DiDiDit Dit, DahDiDahDit DahDahDah 
    DahDiDit Dit. 
    　　 
    字母 
    
    　　A：·— 
    　　B：—··· 
    　　C：—·—· 
    　　D：—·· 
    　　E：· 
    　　F：··—· 
    　　G：——· 
    　　H：···· 
    　　I：·· 
    　　J：·——— 
    　　K：—·— 
    　　L：·—·· 
    　　M：—— 
    　　N：—· 
    　　O：——— 
    　　P：·——· 
    　　Q：——·— 
    　　R：·—· 
    　　S：··· 
    　　T：— 
    　　U：··— 
    　　V：···— 
    　　W：·—— 
    　　X：—··— 
    　　Y：—·—— 
    　　Z：——·· 
    　　 
    数字 
    
    　　1：·———— 
    　　2：··——— 
    　　3：···—— 
    　　4：····— 
    　　5：····· 
    　　6：—···· 
    　　7：——··· 
    　　8：———·· 
    　　9：————· 
    　　0：————— 
    　　 
    标点符号 
    
    　　“.”：·—·—·— 
    　　“:”：———··· 
    　　“,”：——··—— 
    　　“;”：—·—·—· 
    　　“?”：··——·· 
    　　“=”：—···— 
    　　“'”：·————· 
    　　“/”：—··—· 
    　　“!”：—·—·—— 
    　　“-”：—····— 
    　　“_”：··——·— 
    　　“"”：·—··—· 
    　　“(”：—·——· 
    　　“)”：—·——·— 
    　　“$”：···—··— 
    　　“�”：· ··· 
    　　“@”：·——·—· 
    　　 
    非英语拉丁文字母 
    
    　　�aelig;：·—·— 
    　　à：·——·— 
    　　�ccedil;：—·—·· 
    　　ch：———— 
    　　�eth;：··——· 
    　　è：·—··— 
    　　é：··—·· 
    　　�ntilde;：——·—— 
    　　�ouml;：———· 
    　　&thorn;：·——·· 
    　　ü：··—— 
    

没有任何有用信息。。。。看看 word里面有没有隐藏文字  
文件--》选项---》隐藏文字的勾 去掉 出来了 steganography  
上工具。。。  

image.png

  
将哈士奇这个图片解密<http://www.atool.org/steganography.php>  

image.png

  
key{you are in finally hell now}  

image.png

  
服了。。。。。。  
图片是个压缩文件，不要问我怎么知道的，虽然文件头是FFD8，但他就是压缩文件（改了其他格式全部乱码），打开有密码。。。。。

将二进制文本8个一组转换一下，对照ASCLL表，解密后为 ruokouling  
BUT：ruokouling 并不是密码。。。拼一下：弱口令  
百度下弱口令字典，执行爆破，密码为：Password

image.png

image.png

  
根据图文信息--base64编码---》rabbit--》凯撒密码  
解密网址：<https://www.sojson.com/encrypt/>  
base64---》

    
    
    VTJGc2RHVmtYMTlwRG9yWjJoVFArNXcwelNBOWJYaFZlekp5MnVtRlRTcDZQZE42elBLQ01BPT0=
    

Rabbit解密---》

    
    
    fxbqrwrvnwmngrjxsrnsrnhx
    

凯撒密码解密：---》有26个结果，如下图所示：

    
    
    第1次解密:fxbqrwrvnwmngrjxsrnsrnhx
    第2次解密:ewapqvqumvlmfqiwrqmrqmgw
    第3次解密:dvzopuptluklephvqplqplfv
    第4次解密:cuynotosktjkdogupokpokeu
    第5次解密:btxmnsnrjsijcnftonjonjdt
    第6次解密:aswlmrmqirhibmesnminmics
    第7次解密:zrvklqlphqghaldrmlhmlhbr
    第8次解密:yqujkpkogpfgzkcqlkglkgaq
    第9次解密:xptijojnfoefyjbpkjfkjfzp
    第10次解密:woshinimendexiaojiejieyo
    第11次解密:vnrghmhldmcdwhznihdihdxn
    第12次解密:umqfglgkclbcvgymhgchgcwm
    第13次解密:tlpefkfjbkabufxlgfbgfbvl
    第14次解密:skodejeiajzatewkfeafeauk
    第15次解密:rjncdidhziyzsdvjedzedztj
    第16次解密:qimbchcgyhxyrcuidcydcysi
    第17次解密:phlabgbfxgwxqbthcbxcbxrh
    第18次解密:ogkzafaewfvwpasgbawbawqg
    第19次解密:nfjyzezdveuvozrfazvazvpf
    第20次解密:meixydycudtunyqezyuzyuoe
    第21次解密:ldhwxcxbtcstmxpdyxtyxtnd
    第22次解密:kcgvwbwasbrslwocxwsxwsmc
    第23次解密:jbfuvavzraqrkvnbwvrwvrlb
    第24次解密:iaetuzuyqzpqjumavuqvuqka
    第25次解密:hzdstytxpyopitlzutputpjz
    第26次解密:gycrsxswoxnohskytsotsoiy
    

## flag：woshinimendexiaojiejieyo

### 九连环

image.png

  

上来只有一张图片，隐写术肯定在这张图片里了  
把图片下载下来，首先想到拉进 binwalk里面分析下有没有隐藏文件。  
果真有东西，利用 -e 命令分离开来（windows下）。

  

image.png

  

image.png

分离后有一个压缩包，一个文件夹（实际内容是一样的）。

  

image.png

  

压缩包有密码。但是没有密码提示，所以爆破基本上是不可能的，思路只能转向图片了，继续丢进binwalk里面看看有没有东西。

  

image.png

  
ok！！失败，啥也没有，图片隐写上另一个工具Steghide。  
利用--help 命令可以查看使用方法  

image.png

  

有密码。。。。。试了几个弱口令，都不正确，然后啥也没输入，索性一个回车，居然进去了。。。。。TMD。空密码。。。

  

image.png

  
搞出来了个KO.txt  

image.png

    
    
    bV1g6t5wZDJif^J7
    

* * *

## FIVE1

又是一张图片  
继续binwalk

分离出来了一个压缩文件，题目提示了5位数密码，生成密码，进行爆破

  

image.png

  

坑爹竟然是4位的

  

image.png

  
用binwalk 分离不出来，不知道为什么。。。  
然后winhex把图片以外的数据搞出来。。  

image.png

  

image.png

  

表示不知道这是什么密码。。。。。看了下面的提示。。。这尽然是base64.。。。。。。

然后又来个摩斯密码。。。。

  

image.png

  

16个数肯定是MD5了

  

image.png

    
    
    admin
    

* * *

## stegas 300

#### 分析音频波形

既然是音频  
上MP3Stego，结果是这样，没有密码，两个文件全空

  

image.png

binwalk里面啥也没有

  

image.png

题目给出的是分析音频波形。。上Wave Editor试下，看到了东西，有戏，但是并不知道这是什么玩意，百度了下 波频上为1
下为0。。。。好的。。。记住了。。。

  

image.png

  

01100010 0110000101101011011001000110111101110010  
01100010 01100001 01101011 01100100 01101111 01110010  
八个一组转ASCLL  
98 97 107 100 111 114  
b a k d o r  
试了N次这个并不是密码，然后去网上搜了下，，，，题目有问题。。。。。  
MD5加密后是答案  
flag{e1b64df17443b51e3007fd3d5370dca1}

出题者是智障么。。。改了答案。。不改问题。。。

* * *

## Chromatophoria

只给了一张图片，图片名字是steg~~  
上stegsolve

对了~做之前可以看下这篇总结：<https://www.secpulse.com/archives/4855.html>  

image.png

image.png

image.png

image.png

  

低位全勾上不行 ~~ 去掉一个试试 ~~ 出来了~~

  

image.png

  

ps

  

ps：格式很坑！！

* * *

## Black Hole

一个镜像文件，挂载的时候损坏失败，放进binwalk 分离不来也不知到是啥东西。

image.png

## 不会做。。。先pass。。。

## 心中无码

放到stegsolve中 没观察到什么东西

丢进binwalk 发现有东西，分离出来不知道是什么鬼。。丢进 winhex 乱码

  

好像思路错了。。百度了下，要用python跑。。。并不会写python脚本。。。没办法，，先比葫芦画瓢。。。后期慢慢学把。。。

先pass

## 刷新 刷新 快刷新

题目说的很清楚了F5

github工具源码：<https://github.com/matthewgao/F5-steganography>  
命令：java Extract 你的图片的绝对路径\123456.jpg -p 123456

image.png

## flag{F5_f5_F5_Ez!!!}

## 流

一个vmdk，貌似是虚拟机的文件，老规矩丢进binwalk
里面看看有啥。。。然后啥也没有。。丢进winhex看下。。flag被发现12次。。。。结果把hidden提交了N次不是正确答案。。。看了下提交格式是：CTF{}
搜了下CTF关键词。。。出来了答案。。。。

  

image.png

image.png

  

image.png

  

image.png

* * *

# 我就是flag

是个 png 然后 漆黑一片。。。看下 属性，里面没东西。

  

image.png

  

丢进binwalk里面 啥也没有

  

image.png

搜了下 用 outguess~~~

kali里面并没有集成outguess 所以需要自己安装~~那么跟我一步一步的来。  
github上自行下载源码<https://github.com/crorvick/outguess>

安装方法：  
移步至kalilinux~~新建一个outguess文件夹

命令如下： mkdir outguess

1.解压，linux下cd到outguess的文件夹

2.最好在root下sudo ./configure && make && make install

之后直接用outguess命令就可以使用了

加密：  
outguess -k "my secret key" -d hidden.txt demo.jpg out.jpg  
加密之后，demo.jpg会覆盖out.jpg,  
hidden.txt中的内容是要隐藏的东西

解密：  
outguess -k "my secret key" -r out.jpg hidden.txt  
解密之后，解密内容放在hidden.txt中

  

image.png

ok 拿到flage

  

image.png

* * *

# Fonts

下载下来打开就是flag

* * *

# 男神一般都很低调很低调的！！

* * *

# 黑与白

二维码直接上CQR扫描工具，得到<HttP://pcat.cnbloGs.cOM?Hh>  

image.png

  
打开网址以后是作者的个人博客，里面并没有任何信息  
百度了下writeup~~发现网址居然是培根密码  
这里没有用A B ~~网址的大小写即是 A B，要么大写是A 小写是B，要么大写是B 小写是A  
写出来试一下把  
HttPp ABBAB OR BAABA ---> o 或 t  
catcn BBBBB AAAAA ---> *或a ok只能是后一种，前面的没有答案  
bloGs BBBAB AAABA---> c  
cOMHh BAAAB ABBBA--->p

    
    
    附上培根密码表
        a AAAAA   g AABBA    n ABBAA   t BAABA
        b AAAAB   h AABBB    o ABBAB   u-v BAABB
        c AAABA   i-j ABAAA  p ABBBA   w BABAA
        d AAABB   k ABAAB    q ABBBB   x BABAB
        e AABAA   l ABABA    r BAAAA   y BABBA
        f AABAB   m ABABB    s BAAAB   z BABBB
    
    

上 Stegdetect

    
    
    Stegdetect的参数：
    
    Stegdetect通过统计测试来分析图像文件中是否包含隐藏内容。它运行静态测试以判断隐藏的内容是否存在。此外，它还会尝试识别隐藏内容是通过哪个隐写工具嵌入的。
    
    Stegdetect的主要选项如下：
    
    q – 仅显示可能包含隐藏内容的图像
    
    n – 启用检查JPEG文件头功能，以降低误报率。如果启用，所有带有批注区域的文件将被视为没有被嵌入信息。如果JPEG文件的JFIF标识符中的版本号不是1.1，则禁用OutGuess检测。
    
    s – 修改检测算法的敏感度，该值的默认值为1。检测结果的匹配度与检测算法的敏感度成正比，算法敏感度的值越大，检测出的可疑文件包含敏感信息的可能性越大。
    
    d – 打印带行号的调试信息。
    
    t – 设置要检测哪些隐写工具（默认检测jopi），可设置的选项如下：
    
    j – 检测图像中的信息是否是用jsteg嵌入的。
    
    o – 检测图像中的信息是否是用outguess嵌入的。
    
    p – 检测图像中的信息是否是用jphide嵌入的。
    
    i – 检测图像中的信息是否是用invisible secrets嵌入的。
    
    

image.png

打开JPHswin

  

image.png

  

image.png

这个题

  

这个题不看writeup根本想不出来。。。。。

* * *

# so beautiful so white

题目给了一个压缩包，并且提示压缩包的密码就藏在这幅白色图片中，仔细找找看吧  
解压出来 一张图片，一个压缩包。

  

属性里面什么也没有

  

属性里面什么也没有  
上stegsolve看下，发现东西

  

，发现

  
用密码解压出来以后是一个GIF图片（注意密码是：key 里面的字符）  
打开gif提示损坏，用winhex看下文件头---修复-->添加文件头  

image.png

  

动态图---用stegsolve进行逐帧查看

  

image.png

## CTF{AS3X}

# 水果

又是一个png，直接上stegsolve看看，发现二维码

cqr扫描

  

image.png

    
    
    45 46 45 46 32 45 32 46 46 45 46 32 46 45 46 46 32 46 46 46 32 45 46 46 46 32 46 46 45 45 46 45 32 45 46 46 46 32 46 46 46 32 46 45 46 46 32 
    

而且只有45/46/32

肯定是ascll（我猜的）  
对比了一下，我好像猜对了  
45---'-' 46---'.' 32---' '(空格)  
哈哈 摩斯密码  
-.-. - ..-. .-.. ... -... ..--.- -... ... .-..  
进行解码  
CTF{CTFLSB_BSL}

题目有问题，正确的答案居然是这个。。表示无言以对  
CTF{lsb_bsl}

* * *

## 无处不在的广告

一张png。。  
先看看属性，没有任何东西，上winhex，没有发现任何异常，上stegsolve  
点到不知道几下的时候发现异常，哈哈哈哈

  

image.png

  

image.png

* * *

## 想看正面？那就要看仔细了！

一张图片。先看下属性。

  

image.png

  

image.png

。。直接得到KEY了么。。。然后提交。。。显示key不对。。。肯定还有其他加密。。  
但是实在不知道 这8位字母是什么鬼。。。要不就把所有的解密都来一便把。。。。MD5 base16 base32 aes des rabbit 挨个试试把  
到头来。。base64.。。。

  

image.png

* * *

## 认真你就输了

excel文件，打开不知道是一堆啥玩意。。。而且无规律可循。。  
右击看下属性  

image.png

  
ok~~~没有任何信息  
用记事本打开看下 ~~或者winhex~~  
告诉我看到了什么。。。。  
这个题应该是最简单的了。。。  

image.png

  

image.png

* * *

## 复杂的QR_code

文件名字很明显，还是个二维码，二维码里肯定有东西，上CQR

  

image.png

  

提示说了跟没说一样，继续上winhex跟binwalk  
winhex发现东西，继续上binwalk,

  

image.png

  

image.png

  
分离出来的zip有密码。。并没有提示用破解。。但是有没有其他提示。。。索性先用弱口令爆破，不行再穷举所有密码  

image.png

  

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [实验吧隐写部分wp](https://www.jianshu.com/p/bcfd1b5375d1)

①欢迎来到地狱 原题链接：http://www.shiyanbar.com/ctf/2010 下载文件，解压 打开...

[_Blank_](https://www.jianshu.com/u/288ed2b8421e)阅读 596评论 0赞 0

  * [CTF取证类题目指南](https://www.jianshu.com/p/022fb173677d)

文章简介：大致介绍了CTF比赛中Fornesics题目的常见类型和各类使用工具，此类题目在国内CTF中偶尔出现，但...

[看雪学院](https://www.jianshu.com/u/fc7a20500211)阅读 8,258评论 0赞 20

  * [Android - 收藏集 ](https://www.jianshu.com/p/dad51f6c9c4d)

Android 自定义View的各种姿势1 Activity的显示之ViewRootImpl详解 Activity...

[passiontim](https://www.jianshu.com/u/e946d18f163c)阅读 168,379评论 26赞 707

  * [焦虑与选择](https://www.jianshu.com/p/0ee4205de74f)

没有选择时痛苦，有选择时却是深深的焦虑。唯有静下心来，回归初心，才能找到自己真正的选择。

[姜饼人Ivy](https://www.jianshu.com/u/bcd03d8abcf4)阅读 123评论 0赞 2

  * [上课就是讲故事](https://www.jianshu.com/p/2273ab7d97e4)

人是最重要的，有悬念，把握好逻辑、细节和节奏。

[果子冻](https://www.jianshu.com/u/9ea85d380ea2)阅读 211评论 0赞 0

 