# Flare-On 2018 writeup（上）

阅读量 **201174**

发布时间 : 2018-10-08 14:30:34

 **x**

##### 译文声明

本文是翻译文章

原文地址：<https://mp.weixin.qq.com/s/oINP7YFCivzXUDGe45BF6Q>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01c3755bf6f655d770.png)

## Ultimate Minesweeper

donet写的扫雷程序，找到正确的安全位置点击，雷区map的布置藏在下面的代码中

![](https://p1.ssl.qhimg.com/t0121123fdda2668d0e.png)

![](https://p5.ssl.qhimg.com/t0129b9072943f38826.png)

重构输出得到(28, 7)，(7, 20)，(24, 28)三个坐标点，依次点击显示flag

    
    
    mine = []
    vtypes = [-896,-639,-270]
    for i in range(30):
        mine.append([])
        for j in range(30):
            flag = True
            r = i + 1
            c = j + 1
            if ~((r * 30) + c) in vtypes:
                flag = False
                print 'x',j,'y',i

![](https://p5.ssl.qhimg.com/t017b593f00169f13ab.png)

## FLEGGO

解压得到48个程序，模式一模一样，可以通过脚本批量取出各个程序的key，输入正确的key后，echo几个字符并得到一张乐高图片

![](https://p4.ssl.qhimg.com/t01337a5c306c22c36b.png)

    
    
    import os
    from subprocess import *
    
    output = ''
    pngtxt = ''
    
    for dirpath,dirnames,filenames in os.walk('FLEGGO'):
        for file in filenames:
            pathname = os.path.join(dirpath,file)
            if pathname[-4:] == '.exe':
                txt = open(pathname,'rb').read()
                head = txt.find('\x42\x00\x52\x00', 6500) + 14
                tail = txt.find('\x00\x00', head)
                pw = txt[head:tail:2]
                output = output + pathname + '\t' + pw + '\n'
                p = Popen(pathname,stdin=PIPE,stdout=PIPE)
                p.stdin.write(pw + '\n')
                p.stdin.flush()
                p.stdout.readline()
                p.stdout.readline() 
                pngtxt = pngtxt + p.stdout.readline() + '\n'
    open('res.txt','w+').write(output)

对图片根据内容进行标号，然后将得到的字符按图片标号顺序连接即flag

![](https://p1.ssl.qhimg.com/t0196215109f6a99f17.png)

    
    
    pngdat = []
    for i in range(48):
        pngdat.append(open('png\\%02d.png'%(i+1),'rb').read())
    pngarr = pngtxt.split('\n')
    for p in pngarr:
        pinfo = p.split(' ')
        pngd = open('FLEGGO\\%s'%(pinfo[0]),'rb').read()
        print str(pngdat.index(pngd)) + '\t' + str(pinfo[1])

mor3_awes0m3_th4n_an_awes0me_p0ssum@flare-on.com

## binstall

donet程序，会删除浏览器缓存，修改注册表，然后释放browserassist.dll文件

![](https://p3.ssl.qhimg.com/t01843bf7ca499b7c3c.png)

这个dll文件会下载了一段加密的数据，解密后得到一个js文件

![](https://p4.ssl.qhimg.com/t01823f5036accfe8b1.png)

![](https://p4.ssl.qhimg.com/t01c4a82121f1e78ced.png)

通过cp()函数中的判断式推出密码为k9btBW7k2y，根据密码调用js中的de()函数得到flag

    
    
    function cp(p) { //get password
        if (model.passwordEntered = !1, 10 === p.length && 123 == (16 ^ p.charCodeAt(0)) && p.charCodeAt(1) << 2 == 228 && p.charCodeAt(2) + 44 === 142 && p.charCodeAt(3) >> 3 == 14 && p.charCodeAt(4) === parseInt(function() {
            var h = Array.prototype.slice.call(arguments),
            k = h.shift();
            return h.reverse().map(function(m, W) {
                return String.fromCharCode(m - k - 24 - W)
            }).join("")
        } (50, 124) + 4..toString(36).toLowerCase(), 31) && p.charCodeAt(5) - 109 == -22 && 64 == (p.charCodeAt(3) << 4 & 255) && 5 * p.charCodeAt(6) === parseInt(function() {
            var n = Array.prototype.slice.call(arguments),
            M = n.shift();
            return n.reverse().map(function(r, U) {
                return String.fromCharCode(r - M - 16 - U)
            }).join("")
        } (22, 107) + 9..toString(36).toLowerCase(), 19) && p.charCodeAt(7) + 14 === "xyz".charCodeAt(1) && 3 * (6 * (p.charCodeAt(8) - 50) + 14) == 17 + parseInt(function() {
            var l = Array.prototype.slice.call(arguments),
            f = l.shift();
            return l.reverse().map(function(O, o) {
                return String.fromCharCode(O - f - 30 - o)
            }).join("")
        } (14, 93) + 6..toString(36).toLowerCase(), 8) - 1 + 12 && 3 + (p.charCodeAt(9) + 88 - 1) / 2 === p.charCodeAt(0)) model.root = 1,
        model.password = p, console.log(p) ;
        else {
            ……省略一万字
    }
    
    function de(instr) { //de code flag
        for (var zzzzz, z = model.password,
        zz = atob(instr), zzz = [], zzzz = 0, zzzzzz = "", zzzzzzz = 0; zzzzzzz < parseInt("CG", 20); zzzzzzz++) zzz[zzzzzzz] = zzzzzzz;
        for (zzzzzzz = 0; zzzzzzz < parseInt("8O", 29); zzzzzzz++) zzzz = (zzzz + zzz[zzzzzzz] + z.charCodeAt(zzzzzzz % z.length)) % parseInt("8G", 30),
        zzzzz = zzz[zzzzzzz],
        zzz[zzzzzzz] = zzz[zzzz],
        zzz[zzzz] = zzzzz;
        for (var y = zzzz = zzzzzzz = 0; y < zz.length; y++) zzzz = (zzzz + zzz[zzzzzzz = (zzzzzzz + 1) % parseInt("514", 7)]) % parseInt("213", 11),
        zzzzz = zzz[zzzzzzz],
        zzz[zzzzzzz] = zzz[zzzz],
        zzz[zzzz] = zzzzz,
        zzzzzz += String.fromCharCode(zz.charCodeAt(y) ^ zzz[(zzz[zzzzzzz] + zzz[zzzz]) % parseInt("D9", 19)]);
        return zzzzzz
    }

根据js中的等式推测出password= k9btBW7k2y，然后执行de(..)函数

![](https://p5.ssl.qhimg.com/t0139cd0a6a0e139549.png)

## web 2.0

wasm,可以由chrome调试  
github下载wabt将wasm转换为wat文件，S字节码，非常类似JVM字节码时刻都在入栈、出栈。  
编写watHelper脚本解析函数块，思路是记录指令操作的栈影响，然后还原出代码（遇到function call出入栈数量要根据函数类型决定）  
watHelper部分代码如下

![](https://p1.ssl.qhimg.com/t0151d0e9e4870d8104.png)

分析后的函数关键位置下bp即可偷flag字节

![](https://p5.ssl.qhimg.com/t01c77028ffd70f88fc.png)

## Magic

666轮checkkey通过后可以得到flag

sub_4037BF在每轮通过后改变自身程序，改变decoder和分段check函数

![](https://p5.ssl.qhimg.com/t01a9cc57ce9b8ccaa4.png)

由decoder[33]将一轮的key分33段检查，每段的检查函数需要pFunc ^
pFunXorArr解密，并且每一轮decoder的内容、pFunc、pFunXorArr内存区的内容都将被改变

getkey程序将magic当前轮的decoder和funcArr、funcXorArr加载在本地然后进行爆破（每个片段最大为3个Ascii）

爆破流程

在call ram前对stack进行清空，否则有些函数内未对所有局部变量初始化会造成和源程序执行的结果不同

pwntools进行多轮爆破

mag!iC_mUshr00ms_maY_h4ve_g!ven_uS_Santa_ClaUs@flare-on.com

## WOW

![](https://p4.ssl.qhimg.com/t016be79cfe1cf8881f.png)

程序xor和alloc载入dll资源

然后修改cs: 33h执行载入的x64 dll中的api，由于经过x86和x64的来回切换需要使用windbg调试

![](https://p5.ssl.qhimg.com/t01df7c5b1cc24ca07a.png)

来到s0.dll，由于不是正常的loadlibrary加载的，所以全局偏移实际是文件偏移载入内存的并不是以PE描述偏移载入，导致直接运行会因为访问越界的全局量而奔溃

![](https://p2.ssl.qhimg.com/t01fa1987b444449950.jpg)

意味着使用到全局变量的地方crackme_dll，crack_len需要断点修改实际地址

函数会再次alloc并加载crackme.dll，x86 dll，通过结束前覆盖return stack执行到crackme中的函数

![](https://p1.ssl.qhimg.com/t01b4337ab9bac7fb64.png)

crackme.dll中的主要逻辑利用了socket通讯获取flag，但crackme本身并没藏有flag，回到s0.dll

![](https://p1.ssl.qhimg.com/t0179c581faf5d82d5a.png)

s0中hook了crackme的socket driver

关键函数是被hook的相关函数

重构flag脚本

    
    
    t_6b40 = [0x0F,0x57,0x61,0x77,0x0B,0xFA,0xB5,0xD1,0x81,0x99,0xAC,0xA7,0x90,0x58,0x1A,0x52,0x0C,0xA0,0x08,0x2D,0xED,0xD5,0x6D,0xE7,0xE0,0xF2,0xBC,0xE9,0xF2]
    t_6bb8 = [0x5F,0x68,0x44,0x62,0x23,0xBA,0x21,0x54,0x33,0x73,0x04,0x65,0x50,0x97,0x72,0x26,0x01,0xC4,0xCD,0x11,0xB6,0x0B,0xD6,0xF9,0x58,0x76,0x7E,0x65,0x69]
    counter = 0
    
    def printArr(arr):
        output = ''
        for c in arr:
            output = output + chr(c)
        print output
    
    for magicnum in t_6b40:
        if magicnum == t_6b40[counter]:
            for i in range(counter+1, 29):
                t_6b40[i] = t_6b40[i] ^ magicnum
        t_6bb8[counter] = t_6bb8[counter] ^ t_6b40[counter]
        counter = counter + 1
        print ''
        printArr(t_6b40)
        printArr(t_6bb8)

P0rt_Kn0ck1ng_0n_he4v3ns_d00r@flare-on.com

## Doogie Hacker

得到一段mbr程序，bootloader, 16bit 668p加载到ida

![](https://p2.ssl.qhimg.com/t01426caddf1a92e426.png)

![](https://p5.ssl.qhimg.com/t01ea7020bdd65f5d3c.png)

大体是密文表和取现行时间异或，再和密文异或

时间在bin中提示1990.02.06，题目中还出现了16岁的时间概念因此对该时间可疑

![](https://p3.ssl.qhimg.com/t010f4e08a8594a03cc.png)

使用不同时间异或后，密文只剩一轮异或加密，计算重合指数，确认1990.02.06时间，并且确认密文长度为17

![](https://p5.ssl.qhimg.com/t01d993eb0aed9aa26a.png)

然后假设了key中存在特殊串@flare-on.com，只需要猜测串在key的位置，对密文解密看效果，所有可能性都为乱码，排除key中存在特殊串

再假设明文中存在@flare-on.com，会得到部分的key，部分key在key中的位置也可以求得，只需要补足4位key，先不管4位key，使用部分key解出部分明文依然所有可能性都是乱码

![](https://p5.ssl.qhimg.com/t017e82e57cd383b011.png)

17个密文为一行进行统计发现每列都有2个字符频次极高

假设出现频次极高的字符对应明文为空格可以推的可能的key

qwh}jyteonuatoyj}

ioperal}wvmylware

进行上下组合

key: ioperateonmalware

![](https://p5.ssl.qhimg.com/t01ee396aa1225e938f.png)

R3_PhD@flare-on.com

## leet editr

![](https://p5.ssl.qhimg.com/t019549b86bd08f0dd5.png)

程序开始分配多个堆块并设成不可访问

![](https://p1.ssl.qhimg.com/t015a61d2ca61930233.png)

分配了VEH然后执行堆块代码发生异常，由于程序有多个反调试的地方，使用od调试

大概就是在运行堆块时触发异常，通过VEH解码shellcode，从而分段解密vbs

![](https://p4.ssl.qhimg.com/t0188f4051f2fa08e47.png)

程序解密后可以找到If I were to title this piece, it would be
‘A_FLARE_f0r_th3_Dr4m4t1(C)’将是最后的title

![](https://p3.ssl.qhimg.com/t01d3e5256c9e699b64.png)

该函数对数据分段解密，并且周期轮换使用了xor、rc4组合的三种加密方法，bp拿到所有的解密段

![](https://p4.ssl.qhimg.com/t01fea710db992c4997.png)

包含一张FLARE Ascii图片、网页和vbs脚本

![](https://p3.ssl.qhimg.com/t019f758093a5cc72d1.png)

脚本运行oh(hai(createtextfile(xx,xx)),xx))，

![](https://p5.ssl.qhimg.com/t01b095a93cb52868aa.png)

先通过程序invoke解RC4得到BASE64编码数据，在用vbs自身BASE64，RC4解出反调试代码

vbs invoke部分可以参考github项目wine-stable

![](https://p5.ssl.qhimg.com/t01b53a68edf7adb449.png)

程序最后调用gimme…love(key)，然后对key取md5（去除空白符等），以md5为RC4的key再解密得到最后的明文

key由ascii + title得到，分别是上面提到的FLARE图案和函数解密后的title

![](https://p1.ssl.qhimg.com/dm/1024_131_/t01b566b32b4f8e7f2d.png)

scr1pt1ng_sl4ck1ng_and_h4ck1ng@flare-on.com

## glof

![](https://p2.ssl.qhimg.com/t01f0ad3e58afa998c1.png)

程序是一个驱动加载器，输入flag作为程序参数

一开始会检查一些启动环境，释放出fhv.sys进行加载，然后调用keyCheck分4段检查key

![](https://p3.ssl.qhimg.com/t01b6ef49c1371b1e12.png)

![](https://p4.ssl.qhimg.com/t01e558602cb35e3659.png)

大致是想通过调用vmcall，触发驱动中的某个函数，将check函数加载到申请页面进行校验

将打开CPU VT并进入OS测试模式进行运行，系统奔溃，虚拟机运行一样奔溃

分析fhv.sys参考<https://github.com/Laureline001/lolo>

![](https://p5.ssl.qhimg.com/t01be06aa8fc6fee287.png)

驱动加载后检查了OS、CPU是否支持VT，然后启动VMX

![](https://p4.ssl.qhimg.com/t01d9d90ff31ec7e5eb.png)

客户机寄存器和虚拟机寄存器交换数据，存在非一一对应的，同时用于vmcall传递参数

![](https://p3.ssl.qhimg.com/t014c9f84ab97955c88.png)

![](https://p4.ssl.qhimg.com/t01c86572c61d2027c7.png)

不同的vmcall取得不同数据后再xor 0xe2

![](https://p4.ssl.qhimg.com/t01ef769545d7ea4c9f.png)

跟入找到ring3加载器对应的vmcall，看出对内存释放了一定的数据，dump出来

![](https://p5.ssl.qhimg.com/t01546877be59e4ee37.png)

IDA无法解析，非合法指令

![](https://p4.ssl.qhimg.com/t018db8c98d04fe1792.jpg)

驱动捕捉了异常指令

![](https://p5.ssl.qhimg.com/t01e76a1b0743bcde8e.jpg)

在驱动中重新解析了指令，意味着一套自定义的CPU指令解析

![](https://p0.ssl.qhimg.com/t01eb70a06d867720fd.jpg)

![](https://p2.ssl.qhimg.com/t01552ecad644e1053d.png)

![](https://p5.ssl.qhimg.com/t013928453809622512.png)

![](https://p4.ssl.qhimg.com/t01f34383a04ba3ea7a.png)

脚本分析后得到合法代码

![](https://p3.ssl.qhimg.com/t0101528b32e9c7c2ef.png)

![](https://p1.ssl.qhimg.com/t01b8716c7fd180c5e2.png)

![](https://p3.ssl.qhimg.com/t0195cd03e22300fc08.png)

化简片段后得到4段key

We4r_ur_v1s0r_w1th_Fl4R3@flare-on.com

本文翻译自 [原文链接](https://mp.weixin.qq.com/s/oINP7YFCivzXUDGe45BF6Q)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ChaMd5安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/161163](/post/id/161163)

安全客 - 有思想的安全新媒体

本文转载自: [](https://mp.weixin.qq.com/s/oINP7YFCivzXUDGe45BF6Q)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/oINP7YFCivzXUDGe45BF6Q>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [writeup](/tag/writeup)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t01e150b8fd13828cb0.png) ChaMd5安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

