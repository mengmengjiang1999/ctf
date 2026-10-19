本文首发于“合天网安实验室”作者： 淡灬看夏丶恋雨

海南大学校内赛。国庆打的，之前没时间复现。校外人水了个纪念品。感谢Gamous不舍赐教。感动的哭了。比赛的复盘。有些没做出来的阔以看官方wp。题附及官方wp已打包：

蓝奏：

<https://wws.lanzous.com/i7HmLhmw18f>

百度云：链接：

<https://pan.baidu.com/s/1mKWDG-bftD-kPAeZwEUvGw>

提取码：bcxv

# 1、WEB

signin：

![](https://image.3001.net/images/20201116/1605519986_5fb24a729fa51aa8cf6ba.png!small)

打开网页，源代码，base64解码

 **babysql(ACTF题)：**

这题，一开始以为是纯注入，一个一个试'load_file','information_schema'。还过滤了挺多东西的，后来就直接绕过注入，直接select即可。看提示(划线划掉的)也是

查完字段是三个之后，直接查询flag即可。

    
    
    1' union select 1,2,flag from flag#

![](https://image.3001.net/images/20201116/1605519999_5fb24a7f673299e7079e5.png!small)![](https://image.3001.net/images/20201116/1605520012_5fb24a8ca995233d7b3bf.png!small)

 **babyrce(ACTF题)：**

这题也没啥限制，就是最简单的rce，../ 就返回上级目录，flag就是flag文件。

![](https://image.3001.net/images/20201116/1605520023_5fb24a977647532dc931d.png!small)

 **easygit(ACTF题)：**

![](https://image.3001.net/images/20201116/1605520032_5fb24aa0e270a8fab7171.png!small)

git泄露，github上找个工具，下了源码直接cat flag就好了

backup_file(ACTF题)：

index.php.bak，备份文件，根据源码绕过就好了，构造?key=123即可

![](https://image.3001.net/images/20201116/1605520041_5fb24aa972b3568271af5.png!small)

![](https://image.3001.net/images/20201116/1605520049_5fb24ab196212faa9c019.png!small)

考点应该是php弱类型

参考别人总结的：

    
    
    https://www.cnblogs.com/Mrsm1th/p/6745532.html

![](https://image.3001.net/images/20201116/1605520058_5fb24aba29991052cfcd0.png!small)

intval函数直接将值转换成数字，即数字跟字符串比较。

传key=123即可绕过限制。

![](https://image.3001.net/images/20201116/1605520120_5fb24af8d4ad848714061.png!small)

 **easy_file_include(ACTF题)：**

伪协议直接包含

    
    
    http://8.129.15.153:20005/?file=php://filter/read=convert.base64-encode/resource=flag.php

点击页面的tips，文件包含php伪协议直接尝试即可

![](https://image.3001.net/images/20201116/1605520131_5fb24b0372720cdb8b007.png!small)

![](https://image.3001.net/images/20201116/1605520142_5fb24b0ecb61521274fab.png!small)

![](https://image.3001.net/images/20201116/1605520153_5fb24b192deda5bb9173c.png!small)

 **do_u_know_HTTP：**

提交get参数Hainan_University,然后在post提交HnuSec即可。在根据最后一条，burpsuite抓包加上http头，没啥难的，就按要求提交各类参数就好了。就是post的时候我bp一直不行，用hackbar才可以

![](https://image.3001.net/images/20201116/1605520163_5fb24b2337e1d12ff65ad.png!small)

 **erciyuan**

![](https://image.3001.net/images/20201116/1605520175_5fb24b2fdb84eae3a1ed4.png!small)

![](https://image.3001.net/images/20201116/1605520188_5fb24b3c5a369a250f557.png!small)

![](https://image.3001.net/images/20201116/1605520202_5fb24b4ab1ae0eb62248e.png!small)

看源码，直接跟到最后。先第一步绕过正则即可，^符号取反。就把除了26个大小写字母和数字的其他替换成空，第二个过滤则把HnuSec替换成!。观察前面的hint我们要访问到!HDCTF!.php文件。就构造HnuSecHDCTFHnuSec.php的编码即可绕过

![](https://image.3001.net/images/20201116/1605520215_5fb24b57308110f452fa2.png!small)

![](https://image.3001.net/images/20201116/1605520232_5fb24b684f2479b8cffa4.png!small)

 **hash_hmac：**

观察源码，直接绕过即可。post传x[]=QNKCDZO&y[]=aabg7XSs。给了个 fllllllllllllag.php，访问cat flag

md5弱类型，直接绕过吧

![](https://image.3001.net/images/20201116/1605520250_5fb24b7a0fde4d8fe911e.png!small)

![](https://image.3001.net/images/20201116/1605520258_5fb24b82f073513f07640.png!small)

![](https://image.3001.net/images/20201116/1605520271_5fb24b8f8677b9d001237.png!small)

 **welcome:**

猜测弱口令，admin/123456，密码错误左上角弹出密码。输入 cat flag

![](https://image.3001.net/images/20201116/1605520280_5fb24b98cca17106e15c1.png!small)

![](https://image.3001.net/images/20201116/1605520291_5fb24ba378f4e0ecb96f5.png!small)

 **calculator_v1**

flask的一题，下载给的python文件，没做任何过滤。直接cat flag即可

![](https://image.3001.net/images/20201116/1605520300_5fb24bacb4cdd44c28ad0.png!small)

![](https://image.3001.net/images/20201116/1605520310_5fb24bb6867fba535cee9.png!small)

 **ezflask**

给了个参考链接，模板注入。还什么都没过滤。就直接套了wp里的payload。

    
    
    https://www.k0rz3n.com/2018/11/12/%E4%B8%80%E7%AF%87%E6%96%87%E7%AB%A0%E5%B8%A6%E4%BD%A0%E7%90%86%E8%A7%A3%E6%BC%8F%E6%B4%9E%E4%B9%8BSSTI%E6%BC%8F%E6%B4%9E/{{config.__class__.__init__.__globals__['os'].popen('cat ./flag').read()}}

![](https://image.3001.net/images/20201116/1605520336_5fb24bd0e4aa74e11cd8c.png!small)

 **warmup**

![](https://image.3001.net/images/20201116/1605520346_5fb24bda2f5377752bbbe.png!small)

 **getshell**

getshell。看过滤。过滤逗号和等号，而后用.来连接前后。

直接把连接前面的闭合掉，在用//注释符把后面注释掉

![](https://image.3001.net/images/20201116/1605520358_5fb24be67205b1a74b344.png!small)

直接闭合后面也是可以cat flag的，看源码就拿到flag了

![](https://image.3001.net/images/20201116/1605520371_5fb24bf307790fbae4a63.png!small)

 **dudaima**

get给pass传个值，然后反序列化他。就满足if里的条件即可

就可自己测试了。引用赋值和传值赋值参考：

    
    
    https://blog.csdn.net/m15712884682/article/details/77350027

![](https://image.3001.net/images/20201116/1605520381_5fb24bfd26f5d7953f74e.png!small)

![](https://image.3001.net/images/20201116/1605520406_5fb24c16b04af0c429fa1.png!small)

剩下的web题就不咋会了。还有几道flask和反序列化，可以看看官方wp

# 2MISC

 **签到题：**

直接输flag，签到即可。

![](https://image.3001.net/images/20201116/1605520431_5fb24c2f17c1b40d66555.png!small)

 **一步之遥：**

伪加密

![](https://image.3001.net/images/20201116/1605520442_5fb24c3a05ac4ba40d784.png!small)

改成00打开

![](https://image.3001.net/images/20201116/1605520452_5fb24c445f3757adad681.png!small)

 **你知道lsb是什么意思吗**

就lsb低位隐写，存为7z即可

![](https://image.3001.net/images/20201116/1605520462_5fb24c4ee825e0ac18f51.png!small)

后来保存下来，看到文件较小，也猜到可能是crc32，找工具爆了确实也不是

![](https://image.3001.net/images/20201116/1605520476_5fb24c5c81d7187bede58.png!small)

在比赛中是没想到可能会是纯数字，后来就写个纯数字的爆破脚本即可(脚本来自官方wp)

![](https://image.3001.net/images/20201116/1605520489_5fb24c69db9137e1a85db.png!small)

 **girlfriend：**

导出HTTP对象，选最大的是图片文件。打开看到flag

![](https://image.3001.net/images/20201116/1605520518_5fb24c861af7aa33b006d.png!small)

![](https://image.3001.net/images/20201116/1605520535_5fb24c970f340ee0a1d8a.png!small)

 **嘤语：**

    
    
    ----- . ----. -... ..--- -... ...-- -.... . . ...-- ...-- -... .---- ...-- ..-. ..-. ----. .- --... ...-- -.. ..-. ....- ....- ----. -... --... --... . ..--- ..-.http://www.zhongguosou.com/zonghe/moersicodeconverter.aspx

![](https://image.3001.net/images/20201116/1605520559_5fb24caf4d3e6c877a77e.png!small)

 **奇怪的字符：**

leet,l33t。黑客语言。wiki上找一下。有对照表，也有在线的网站

    
    
    http://www.englishcn.com/tools/Leet.htmhttp://output.jsbin.com/IHoFuQE/1
    https://www.dcode.fr/leet-speak-1337
    http://www.toolsxx.com/code/1337.html
    https://1337.me/
    https://www.gamehouse.com/blog/leet-speak-cheat-sheet/

![](https://image.3001.net/images/20201116/1605520580_5fb24cc41fc82df3c1ca1.png!small)

 **无字天书：**

![](https://image.3001.net/images/20201116/1605520599_5fb24cd7554385821c53c.png!small)

打开文件，文件只由空格，tab，换行组成。可能是white-space

![](https://image.3001.net/images/20201116/1605520611_5fb24ce33e98c13648ca5.png!small)

找个在线的网站贴进去可以直接解，或者去gayhub上找个。

    
    
    https://vii5ard.github.io/whitespace/

![](https://image.3001.net/images/20201116/1605520622_5fb24cee2a9db1558e7e6.png!small)

ook直接解密就可

    
    
    https://www.splitbrain.org/services/ook

![](https://image.3001.net/images/20201116/1605520631_5fb24cf74091991ba24e1.png!small)

 **你真的了解dns吗？**

![](https://image.3001.net/images/20201116/1605520647_5fb24d074577ecfa8a479.png!small)

nslookup -type=txt hdctf.0x00.work,直接看到flag

dns的type表示dns的协议类型

![](https://image.3001.net/images/20201116/1605520659_5fb24d133ac3c674a9e67.png!small)

 **nospace**

零度字符隐写

解出来的就是password，密码admin：https://offdev.net/demos/zwsp-steg-js

![](https://image.3001.net/images/20201116/1605520670_5fb24d1ebaf9775ea5036.png!small)

 **雪花飘飘**

零解一题，看了wp还没给我整懂，问了一下出题人。diff原页面和链接页面。发现换行，考虑网页隐写。使用stegsnow。snow=雪

![](https://image.3001.net/images/20201116/1605520680_5fb24d2833e092a8bf025.png!small)

用在线工具diff即可。

![](https://image.3001.net/images/20201116/1605520690_5fb24d324cfc4c5afd840.png!small)

海南上一次下雨时间。

![](https://image.3001.net/images/20201116/1605520703_5fb24d3f37432d32cbf62.png!small)

然后就保存题目链接的html文件。

![](https://image.3001.net/images/20201116/1605520712_5fb24d48d850090a056b3.png!small)

花朵解密

    
    
    https://www.qqxiuzi.cn/bianma/wenbenjiami.php?s=huaduo

![](https://image.3001.net/images/20201116/1605520722_5fb24d5279bb24e51f344.png!small)

 **海底捞帧预告片**

这题感觉不难，就是头大，看了wp还能懂，找到了可以用FFmpeg删除重复帧的命令，和wp一毛一样，问了一下出题人，还给一个用脚本的思路，Hash比较每一帧来筛选。写不来，Ffmpeg天下第一。

![](https://image.3001.net/images/20201116/1605520733_5fb24d5dc458107056cad.png!small)

![](https://image.3001.net/images/20201116/1605520745_5fb24d6915fbabca89960.png!small)

删除重复帧之后，提出图片。

![](https://image.3001.net/images/20201116/1605520761_5fb24d795563013c88617.png!small)

![](https://image.3001.net/images/20201116/1605520775_5fb24d87c86c41cba1892.png!small)

最后筛选到4张，但目前无ps就没继续做下去了，拼起来反色即可得到二维码。

![](https://image.3001.net/images/20201116/1605520786_5fb24d92372244643570e.png!small)

 **专业团队：**

分四阶段，主要就是要降噪处理(不知道能不能把抬棺那段分离出来)。还有能听出来DTMF编码。morse降噪完直接看就好了。DTMF不能的话，就手解。降噪完也是能看的,一个是频谱,然后第二个应该是morse,第三个是dtmf
第四个就是流派的flag。连起来就是最后的flag了。

![](https://image.3001.net/images/20201116/1605520798_5fb24d9e9607255e628d7.png!small)

![](https://image.3001.net/images/20201116/1605520808_5fb24da8e5e681b546988.png!small)

![](https://image.3001.net/images/20201116/1605520820_5fb24db42fbbd5c27b45a.png!small)

调两个频段之后对着DTMF的表就可以看出来了。用工具解的话有几位是乱了的

![](https://image.3001.net/images/20201116/1605520834_5fb24dc2d2275d50fd94d.png!small)

![](https://image.3001.net/images/20201116/1605520844_5fb24dcc91f4035b4ec83.png!small)

 **瓦斯矿工**

很新奇的一道题，虚拟货币相关。

metamask使用可参考：

    
    
    https://zhuanlan.zhihu.com/p/112285438?from_voters_page=true

直接foremost分离图片即可得到一个压缩包，拖进16进制文件里也可以看到有12个50 4B 03 04的PK头

![](https://image.3001.net/images/20201116/1605520869_5fb24de564d20fc9dd748.png!small)

观察到大小较小，直接爆破crc即可，以太坊钱包通过助记词登录。助记词可通过数字查询，这里就只爆破数字。

![](https://image.3001.net/images/20201116/1605520909_5fb24e0d1dd406b46b965.png!small)

直接破即可

    
    
    https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt#L350

以太坊钱包通过BIP-39生成私钥，数字查询助记词。

![](https://image.3001.net/images/20201116/1605520918_5fb24e16bfd42bc9b144a.png!small)

脚本

    
    
    import binascii
    import zipfile
    import time
    def crc32asii(v):
           return (binascii.crc32(bytes(str(v), encoding='ascii')) & 0xffffffff)
    for x in range(1, 10000):
          f = zipfile.ZipFile("00000001.zip", "r")
          for i in range(1, 13): 
                  GetCrc = f.getinfo(str(i)) 
                  crc = GetCrc.CRC
                  a = ("0x%08x" % crc) 
                  j = crc32asii(x) 
                 if ("0x%08x" % j) == a: 
                       print(i, x)
                       time.sleep(0.1)

使用助记词登录之后，复制地址，去查询最近的交易记录

![](https://image.3001.net/images/20201116/1605520930_5fb24e2265313d58bf53c.png!small)

![](https://image.3001.net/images/20201116/1605520944_5fb24e30c433d7c1af175.png!small)

详情里得到的直接转字符串得到flag

![](https://image.3001.net/images/20201116/1605520956_5fb24e3c639242cebda36.png!small)

 **到点了，上号**

出题肯定有故事doge

考点是mp3保留字隐写数据，wp里给了wiki链接

    
    
    https://en.wikipedi.org/wiki/MP3#File_structure

直接拿脚本就出了，未学习原理。

    
    
    https://github.com/impakho/de1ctf-mc_challs/blob/master/writeup/mc_easybgm/mp3.py

![](https://image.3001.net/images/20201116/1605520969_5fb24e4940cf5b0e5ba37.png!small)

#  **3.crypto**

 **起源**

应该是凯撒直接解

![](https://image.3001.net/images/20201116/1605520980_5fb24e54b03dca36bfe4e.png!small)

![](https://image.3001.net/images/20201116/1605520994_5fb24e6244f3efcd428b5.png!small)

 **围住世界：**

![](https://image.3001.net/images/20201116/1605521005_5fb24e6de930b19df09f5.png!small)

这题疑惑了挺久的，以为是自己找的网站和软件不对。反反复复里里外外。试了好几个。后来翻看笔记的时候发现可能是w型栅栏密码

    
    
    http://www.atoolbox.net/Tool.php?Id=777.com

![](https://image.3001.net/images/20201116/1605521017_5fb24e79b2940249efbfb.png!small)

 **有趣起来了：**

![](https://image.3001.net/images/20201116/1605521030_5fb24e86384b8dd6a458c.png!small)

就倒序，ctf特训营上有讲的。quiqui也可以做的，前面改成hdctf就好了。顺便把字母改一下即可。

![](https://image.3001.net/images/20201116/1605521044_5fb24e94d089600fb7aa2.png!small)

官方wp上给的是用脚本

![](https://image.3001.net/images/20201116/1605521058_5fb24ea299365b911d815.png!small)

 **神秘字符：**

一看时候只注意到mc。以为是什么mc的其他版本。就去疯狂google也没找到。后来就翻到mc的wiki。就mc附魔台上的字符，玩过mc的应该都知道,mc
wiki上找张对比图，对比就好

![](https://image.3001.net/images/20201116/1605521072_5fb24eb090bfe16483859.png!small)

    
    
    https://minecraft-zh.gamepedia.com/Minecraft_Dungeons:%E7%AC%A6%E6%96%87

![](https://image.3001.net/images/20201116/1605521086_5fb24ebe5b6090e106da1.png!small)

 **茫茫人海：**

base64隐写，跟[ACTF新生赛2020]base64隐写挺像的。反正也是套脚本就好了

![](https://image.3001.net/images/20201116/1605521096_5fb24ec84c7d6587a31f6.png!small)

![](https://image.3001.net/images/20201116/1605521107_5fb24ed3df40697f184d3.png!small)

 **奇怪的贝斯：**

整不会了这题，抱歉。

具体思路应该就是构造一个码表。\x即是转义字符，方便表示

 **babyrsa：**

![](https://image.3001.net/images/20201116/1605521120_5fb24ee073b169e2dbb0a.png!small)

    
    
    https://www.anquanke.com/post/id/87105

这题还好，纯现代密码菜鸡，不过给了pqe。又给了个链接，先求欧拉，然后就n，d，m

![](https://image.3001.net/images/20201116/1605521133_5fb24eed746ba53f97b11.png!small)

    
    
    #coding:utf-8
    from binascii import a2b_hex, b2a_hex
    import gmpy2
    #flag = "*****************************"
    p = 262248800182277040650192055439906580479
    q = 262854994239322828547925595487519915551
    e = 65533
    n = p*q
    phi = (p-1)*(q-1)
    d = gmpy2.invert(e, phi)
    c = 68405618655091231850901459679785989915772760467494039910176075122809565696913
    m = pow(c, d, n)
    print(m)
    #a=(int(str(m),16))
    a=191853633260784640753082658319123392799532077630882079100618224148262386737246462849
    
    
    https://tool.lu/hexconvert/https://www.bejson.com/convert/ox2str/

![](https://image.3001.net/images/20201116/1605521145_5fb24ef9afd2df19590b8.png!small)

#  **4.Re**

 **sign_up**

 **直接查看字符串就可看到flag**

![](https://image.3001.net/images/20201116/1605521156_5fb24f049a38cc6e4e680.png!small)

 **re1**

这题比赛的时候看,以为是异或运算+base64换表然后解密,找了半天硬是没找全64个字符。然后就不了了之。Re也不咋会。之后的题可以看官方wp。

#  **5.Pwn**

 **calculator**

 **题目描述：**

![](https://image.3001.net/images/20201116/1605521169_5fb24f11d4ee475b370f8.png!small)

 **python2的input执行输入导致rce**

 **先用__import__('os').system('/bin/sh')。**

 **直接rce**

 **然后用python -c 'import pty;pty.spawn("/bin/bash");'。**

 **获得一个bash的shell**

![](https://image.3001.net/images/20201116/1605521179_5fb24f1bebdb90d31b282.png!small)

 **找到之后cat即可**

![](https://image.3001.net/images/20201116/1605521213_5fb24f3d54ce08fe36cd8.png!small)

自己写了一个。。发现py直接input就可了

![](https://image.3001.net/images/20201116/1605521255_5fb24f671873513b05654.png!small)

 **warmup**

abs函数是取绝对值的意思。所以不可能小于0。考虑abs负数溢出。就是2的31次方。直接写脚本传就可

![](https://image.3001.net/images/20201116/1605521270_5fb24f76d1bd35bf6ecce.png!small)

![](https://image.3001.net/images/20201116/1605521284_5fb24f84608ccaa0e235c.png!small)

backdoor

字符串查看到sh,跟入

![](https://image.3001.net/images/20201116/1605521296_5fb24f908d1da387cbca0.png!small)

继续跟

![](https://image.3001.net/images/20201116/1605521309_5fb24f9d6ea01b93b7360.png!small)

bash后门

![](https://image.3001.net/images/20201116/1605521321_5fb24fa97781494e2ef93.png!small)

查看buf到r的位置

![](https://image.3001.net/images/20201116/1605521333_5fb24fb58100c0c7c2530.png!small)

编写脚本溢出即可

![](https://image.3001.net/images/20201116/1605521344_5fb24fc05d167b881ef91.png!small)

![](https://image.3001.net/images/20201116/1605521354_5fb24fca30652d3e51dda.png!small)

其他pwn题本菜不会，pwn题可以参考某大佬，应该是ak了pwn题的：

    
    
    https://www.cnblogs.com/z2yh/p/13771942.html

