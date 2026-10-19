# Codefest2018 writeup

阅读量 **263731**

发布时间 : 2018-09-04 16:30:37

 **x**

##### 译文声明

本文是翻译文章，文章来源：github.io

原文地址：<https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0131ff12f4159c88f1.jpg)

> 本文转载自:
> [github.io](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/)  
>  如若转载,请注明出处： <https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/>

实在是太无聊了，找了找比赛打，`Codefest2018`这个感觉跟以往的ctf比赛不同，感觉更偏向代码能力的考查，以下是这次自己做出来的题目writeup，比赛题目一共`15`道，菜鸡一枚，只做出`10`道。

## Freebies

### problem

This one’s simple. Join the [Slack
channel](https://www.hackerrank.com/external_redirect?to=https://join.slack.com/t/codefest-ctf-18/shared_invite/enQtNDI2MjY1NDcyNDA2LTdiNTczZWUxMjJkZWUwMmQ5MTIxNzMzNDMwMjU5ZTU5MWFlYzU1MjY0MTE2NWI4ZTEyMWFkMTNlYzg3MTAxMTQ)
to get the flag.

这题算是签到题，但也是寻找了好一番，就不放答案了

## Fortune Cookie

### problem

H4k3r has heard that there is a secret hidden behind this
[website](https://www.hackerrank.com/external_redirect?to=http://34.216.132.109:8084/),
but he is confused as to how to get access to it. Can you help him

这题，呃，很简单，该下cookies(说着简单，最后试了半天才发现是admin，不是Admin)

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535766037090.png)

`Who are you?=admin`即可

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535766076578.png)

## Typing Master

### problem

If you think you have it in you, connect now to 34.216.132.109 9093 and prove
your mettle.

You will be presented with a simple typing task which is meant to check your
typing speed.

For example, _Can you type ‘Z’ 10 times followed by ‘u’ 6 times, followed by
the sum of their ASCII values?_

    
    
    ZZZZZZZZZZuuuuuu207
    

### Input Format

**Regarding input to the server** – The question was designed keeping netcat
in mind. Some users who are using other tools/language (eg, Python, PuTTY,
TELNET) to connect to the server please note that they do not terminate the
strings like netcat does. If you choose not to use netcat, the message you
send to our server should terminate with a trailing newline (‘n’) and nothing
else.

nc下,先看看大概是啥样子的

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535879235703.png)

发现每次访问，要求的都不一样，甚至返回的字符串也不一样，想了想，觉得还是一个脚本的事，需要正则一下即可

脚本如下：

    
    
    #-*-coding:utf-8
    
    from pwn import *
    import re 
    
    conn=remote('34.216.132.109',9093)
    text=conn.recv()
    print text
    
    result = re.findall(r"'(w)' (d*)", text)
    #print result
    #print result[0][0]
    #print result[0][1]
    
    str1=(result[0][0] * int(result[0][1]))
    str2=(result[1][0] * int(result[1][1]))
    str3=(str(ord(result[0][0]) +  ord(result[1][0])))
    S = ''.join(str1+str2+str3)
    print S
    
    conn.sendline(S)
    print conn.recv()
    

运行结果

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535879374237.png)

最终答案：`CodefestCTF{1_s33_y0u_4r3_a_m4n_0f_sp33d}`

## Web BooK

### problem

It is expected to complete reading a book/novel to pass the course, but the
students being clever avoid reading the whole book by going through the
summary only. Santosh(their course teacher) comes up with a new idea, he
creates a magic book (you can only go to next page, that is: you can’t go to
next page without reading the previous one and so on, and you can only start
from the beginning). It is know that the flag is hidden somewhere in the book,
so the only way to pass the course is to read the whole book, find the flag.
The book has 1000 pages so better be fast. And if you are lucky, you may even
find the key on the very first page itself. [link to
Web_BooK](https://www.hackerrank.com/external_redirect?to=http://34.216.132.109:8083/fp/)

打开网站，发现如下页面，点击next发现，都是没有规则的url

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535877269304.png)

没办法，只能简单爬虫脚本写下，源码如下

    
    
    #-*-coding:utf-8
    
    import requests
    import re
    
    
    url = 'http://34.216.132.109:8083'
    page = '/fp/'
    s = requests.Session()
    
    counter = 0
    while (True):
        counter += 1
        r = s.get(url + page)
        page_text = r.text
        print page_text
        page = re.findall('action="(.*?)"', page_text)[0]
        print page, counter
    

运行下

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535877528777.png)

## Access Denied?

### problem

A school IT staff manages access to secure files by the method of access code.
You are required to give your name and the access code, and the program will
give out secret information.

It checks whether you already have an access code, generates new random one
along with a new user ID alloted to the user, if that user is not found
locally on the system. The access codes are known to have random expiration
time (don’t know what goes on in their minds!), so don’t be surprised if you
generated an access code just seconds ago and next time the same access code
doesn’t work.

Johnny decided to go into the IT room and copy the program into his pendrive.
You can find it
[here](https://www.hackerrank.com/external_redirect?to=https://drive.google.com/open?id=1KGoBbSNViJS8aZsh1Jjp8XbESv0E-Z4t).

Can you get the secret information out from the program? The service runs on
34.216.132.109 on port 9094.

### Constraints

User ID / UID will be a positive integer

这题给了个school.py

    
    
    #-*-coding:utf-8
    import random
    import user_functions
    
    user = raw_input("Enter your name: ")
    
    if not user_functions.exists(user):
        # generate a code
    
        count_ = user_functions.generateID(user)%1000    #User ID/ UID in the table is always positive
    
        generator = "xorshift"
        random.seed(generator)
        count = 0;
    
        for ch in user:
            ra = random.randint(1, ord(ch))
            rb = (ord(ch) * random.randint(1, len(user))) ^ random.randint(1, ord(ch))
    
            count += (ra + rb)/2
    
    
        code = 1
    
        for i in range(1,count+count_):
            code = (code + random.randint(1, i) ) % 1000000
    
        final = random.randint(1,9) * 1000000 + code
    
        #store it in the database
        user_functions.store(user, final)
    
    else:
        #if user already exists, fetch access code
        final = user_functions.get_code(user)
    
    code = raw_input("Enter your access code: ").strip()
    
    
    while True:
    
        if code.isdigit():
            if (int(code) == final):
                print "The flag is " + user_functions.get_flag(user)
                exit()
            else:
                print "Incorrect access code"
        else:
            print "The code must be an integer"
    
        code = (raw_input("nPlease enter the code: "))
    
        print "n###############################################"
    

乍一看好像挺复杂的，其实不然，只需要爆破即可，简单分析下

起始变量`count`
是由我们输入的`user`确定的。如果我们每次测试时都提供相同的`user`，那么最终`count`变量也都是不变的；而`count_`变量嘛，虽然不知道到底是什么嘛，但是模`1000`得到的结果只可能是`[0,999]`；而`code`呢？由于`code`种子`xorshift`生成的，我们可以根据`count_`遍历`code`。只需要稍微改改给的school.py我们就可以暴力跑出答案。

核心代码其实也就是下面这个：

    
    
    for i in range(0,1000):
        count_ = i
    
        # the seed is always the same
        generator = "xorshift"
        random.seed(generator)
        count = 0;
    
        for ch in user:
            ra = random.randint(1, ord(ch))
            rb = (ord(ch) * random.randint(1, len(user))) ^ random.randint(1, ord(ch))
            count += (ra + rb)/2
        code = 1
        for i in range(1,count+count_):
            code = (code + random.randint(1, i) ) % 1000000
        final = random.randint(1,9) * 1000000 + code
    

完整代码如下：

    
    
    #-*-coding:utf-8
    from pwn import *
    import sys
    
    list_code = []
    user = 'jianghu'
    
    for i in range(0,1000):
        count_ = i
    
        generator = "xorshift"
        random.seed(generator)
        count = 0;
    
        for ch in user:
            ra = random.randint(1, ord(ch))
            rb = (ord(ch) * random.randint(1, len(user))) ^ random.randint(1, ord(ch))
    
            count += (ra + rb)/2
    
        code = 1
    
        for i in range(1,count+count_):
            code = (code + random.randint(1, i) ) % 1000000
    
        final = random.randint(1,9) * 1000000 + code
        list_code.append(final)
    
    print list_code
    
    con = remote('34.216.132.109',9094)
    con.recvuntil('Enter your name: ')
    con.sendline(user)
    
    for i in list_code:
        text = con.recv()
        if 'flag' not in text:
            con.sendline(str(i))
        else:
            print text,i
            sys.exit()
    

运行结果如下

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535892298309.png)

最终答案：`CodefestCTF{1_s33_y0u_4r3_a_m4n_0f_r4nd0mn3ss}`

## It’s Magic

### problem

Repair given corrupted file to get the flag. [download file
here](https://www.hackerrank.com/external_redirect?to=https://drive.google.com/file/d/10O4w6rtsUiCspM94qdXqvHeTj-4O0RfX/view?usp=sharing)

下载完毕后，拖到winhex里，拖到尾部发现`FFD9`，尝试改文件头，发现无效

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535879938784.png)

遂尝试网上搜索在线修复受损图片，找到一个[工具网站](https://online.officerecovery.com/cn/fix-damaged-photo-file-online/)

修复完成后，打开即有flag

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535880232974.png)

最终答案：`CodefestCTF{mAgic_byTes}`

## Hidden Agenda

### problem

Just before getting caught in Russia, MI-6 agent John Stegwal sent a mail to
MI-6 containing two [visually similar
images](https://www.hackerrank.com/external_redirect?to=https://drive.google.com/drive/folders/1GHCN9eIRPtlMA0xGxnr44nY0boo-6DOx?usp=sharing).
It is possible that the images contain information on how to access his
findings. Can you find the message he sent?

给了两个`jpg`文件：`image1.jpg`与`image2.jpg`。

先用`StegSolve`将`image1.jpg`与`image2.jpg`来次`xor`，发现有个二维码的痕迹，保存为`solved.bmp`

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535769690535.png)

将`solved.bmp`与`image1.jpg`再来一次MUL，得到一个可扫的清晰二维码

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535769505500.png)

扫出来是个网址`https://drive.google.com/file/d/13chbULOlKaOM_jI8_RaxECZ0xzJUg7Y4/view`，打开后，有张图片，下载下来，打开后可以看到清晰的`flag{`字样，然后，没然后了，这张图片只有`flag{`（那时候看到flag，开心极了，贼坑）

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535882244230.png)

没事，我吃柠檬。谷歌了下，找了找有关`jpg`图片隐写，找到了个`jsteg`，哟，试试

先试试`image1.jpg`，试出东西来了

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535882176697.png)

得到了个`flg.exe`，`winhex`看下，没看懂是啥

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535882473635.png)

`file`下，发现是个`MP3`

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535882547718.png)

改后缀名，听了听，这是鸟叫声？`exm`?拖到`Adobe Audition CC2017`试试，查看了下频谱图

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535882938272.png)

得到最终答案：`CodefestCTF{0b5cur17y > 53cur17y}`

## Thunder

此题给了个流量包`thunder.pcap`，包不大，分析发现好几个`flag.jpg`，但是都是不完整的。

尝试根据`jpg`文件的文件格式来拼图。先导出`http`对象，删除重复的。此题有个坑点，不可以按照分组序号的大小来拼，必须按照`TCP`流所显示的时间依小到大排序，然后拼好即可。

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535773565813.png)

人懒，写了个`bat`脚本`1.bat`

    
    
    type flag*.jpg>>all.jpg
    

以下是`all.jpg`

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535880779671.png)

得到最终答案：`CodefestCTF{AP_is_amazing}`

## Polyglot

### problem

Chetu writes code with weird whitespace, and nobody knows why. He uses his own
[C
interpreter](https://www.hackerrank.com/external_redirect?to=https://drive.google.com/open?id=12pZCXtDxvGqZUEzaZ-I_3Md-bPizUILT), which is probably the only thing that can handle his absurd
code. He insists its more secure this way. Since no one ever believes him, he
demonstrated his technique on [this vulnerable
code](https://www.hackerrank.com/external_redirect?to=https://drive.google.com/open?id=17ORWMNSOodeEarjuYDXHswlC_6t_kH_A).
Can you get the flag?

这题贼有意思，贼好玩。题目给了两个文件，但是做这题，我只用了`c`代码的文件，另外一个`elf`都没看。

首先我们看看`c`代码：

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535893121359.png)

会发现，这些数字排序，怎么都是空那么多格子的呢？奇怪，但是突然想起了写`python`脚本时，会因为空格和`tab`混淆而报错，下意识看看这些空白字符是由什么构成的。`Notepad++`有个功能

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535893522278.png)

果然，这些空白字符是由不同的空格字符和制表符组成。尝试先用脚本读读

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535894260379.png)

果然，猜想是正确的，那么现在需要提取下这些空白的字符。想到了正则表达式，其中`s`表示只要出现空白就匹配。但是匹配完后有什么用了？随即想到有没可能是`0`,`1`替换，到时候来个二进制转换`ASCII`可见字符。尝试一波，先匹配试试，然后`‘t’`替换成`1`，`‘
’`替换成`0`，得到了想要的答案

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535894689021.png)

最终答案：`CodefestCTF{sP4c3S AnDtAb5}`

## Intercept

### problem

Garry encrypted a message with his public key and mailed it to Monika. Sure
Garry is an idiot. The intercepted mail is given below as seen from Monika’s
side. Decrypt the message to get the key.
[interceptedMail.eml](https://www.hackerrank.com/external_redirect?to=https://drive.google.com/file/d/1T9mCsfp-QZFnas6scLSUx7cg9yYmT8hH/view?usp=sharing)

下载文件后，发现`eml`中存在`zip`，`base64`解码下

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535897369171.png)

有两个文件，`flag.enc`是密文，但是私钥哪去了呢？其实在下面那个文件里。

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535895884842.png)

其中`Public_Key_Encryption_.docx`实际上是是个压缩包，`winhex`下看到了`PK`的头

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535895863184.png)

改后缀名，解压。寻找一番没找到私钥。最后才发现，在解压文件中`wordmedia`，存在三张图片

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535896502425.png)

其中的`image1.png`的尾部存在私钥

那么，提取出来，保存为`private.pem`

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535897514713.png)

额，`openssl`解密下，执行命令`openssl rsautl -decrypt -in flag.enc -inkey private.pem
-out flag.txt`

![](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/1535897143197.png)

最终答案：`CodefestCTF{kristeinStewart_is_5EXY}`

本文翻译自github.io
[原文链接](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **汕口** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158680](/post/id/158680)

安全客 - 有思想的安全新媒体

本文转载自: [github.io](https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/)

如若转载,请注明出处： <https://jianghuxia.github.io/2018/09/03/Codefest2018-CTF/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [writeup](/tag/writeup)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t01e2d1fa28a22b6619.png) 汕口

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

