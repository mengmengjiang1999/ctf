南京邮电ctf-CG-CTF—WEB—WriteUp(持续更新)

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 南京邮电ctf-CG-CTF—WEB—WriteUp(持续更新)

南京邮电ctf-CG-CTF—WEB—WriteUp(持续更新)

## 南京邮电练习题-CTF练习题

# web篇

# 1.签到题

签到题.png

直接右键查看源代码得到flag

签到题

关键是<a style="display:none">这条html属性，让flag不显示，去掉NONE即可get flag

  

签到题.png

# 2\. 签到2

1.png

2.png

输入口令：zhimakaimen 提交后并无反应~~，老规矩看下源代码~  

3.png

看到了猫腻，最大密码长度设为了10，F12改下试下，改成11，get 到 flag ~~~~

4.png

# 3\. md5 collision

1.png

题目给出一段php源码，仔细阅读下面这段代码后发现，这完全不可能！！

    
    
     $a != 'QNKCDZO' && $md51 == $md52
    

but~~~

    
    
    “QNKCDZO”   用MD5加密后是  md5(QNKCDZO,32) = 0e830400451993494058024219903391
    

看到没有 MD5加密后是 _0e_ 开头的，在php中 _0e_ 开头的哈希值都有个bug，并且 _0e_ 开头的密码就这么几个。  
具体链接请看：[freebuf](http://www.freebuf.com/news/67007.html)

然后继续进行构造一下  
令$a = s155964671a <http://chinalover.sinaapp.com/web19/?a=s155964671a>

    
    
    key：nctf{md5_collision_is_easy}
    

## ps：0e开头MD5小节

s878926199a  
0e545993274517709034328855841020  
s155964671a  
0e342768416822451524974117254469  
s214587387a  
0e848240448830537924465865611904  
s214587387a  
0e848240448830537924465865611904  
s878926199a  
0e545993274517709034328855841020  
s1091221200a  
0e940624217856561557816327384675  
s1885207154a  
0e509367213418206700842008763514  
s1502113478a  
0e861580163291561247404381396064  
s1885207154a  
0e509367213418206700842008763514  
s1836677006a  
0e481036490867661113260034900752  
s155964671a  
0e342768416822451524974117254469  
s1184209335a  
0e072485820392773389523109082030  
s1665632922a  
0e731198061491163073197128363787  
s1502113478a  
0e861580163291561247404381396064  
s1836677006a  
0e481036490867661113260034900752  
s1091221200a  
0e940624217856561557816327384675  
s155964671a  
0e342768416822451524974117254469  
s1502113478a  
0e861580163291561247404381396064  
s155964671a  
0e342768416822451524974117254469  
s1665632922a  
0e731198061491163073197128363787  
s155964671a  
0e342768416822451524974117254469  
s1091221200a  
0e940624217856561557816327384675  
s1836677006a  
0e481036490867661113260034900752  
s1885207154a  
0e509367213418206700842008763514  
s532378020a  
0e220463095855511507588041205815  
s878926199a  
0e545993274517709034328855841020  
s1091221200a  
0e940624217856561557816327384675  
s214587387a  
0e848240448830537924465865611904  
s1502113478a  
0e861580163291561247404381396064  
s1091221200a  
0e940624217856561557816327384675  
s1665632922a  
0e731198061491163073197128363787  
s1885207154a  
0e509367213418206700842008763514  
s1836677006a  
0e481036490867661113260034900752  
s1665632922a  
0e731198061491163073197128363787  
s878926199a  
0e545993274517709034328855841020

# 4.这题不是WEB

##### 源代码中只给了一张gif，后缀改为zip，rar均提示文件损坏，然后丢进hex！！flag在最后

1.png

2.png

    
    
        key：nctf{photo_can_also_hid3_msg} 
    

# 5\. 层层递进

这个题果真层层递进。。。。。

查看源代码发现！嗯！对！慢慢找！隐藏表单一个套一个

1.png

、

### 这个题找的本宝宝怀疑人生。。。。。

# 6\. AAencode

将页面转换为UNICODE编码即可看到正常的加密源码。

AAencode密码，可以看下下面的文章研究下  
<http://blog.csdn.net/qq_38329811/article/details/78186362>

在线解码工具：<https://tool.zcmzcm.org/aadecode>  

1.png

    
    
        key：nctf{javascript_aaencode}
    

# 7 .单身二十年

用burp捕获下，发现了一个search页面

  

image.png

  

再看下这个search页面，看到了flag

  

image.png

    
    
        key：nctf{yougotit_script_now}
    

# 8 .你从哪里来

你是从 google 来的吗？

# 9 .PHPCODE

eval可以执行php代码,所以修改代码后，直接运行下！！

image.png

    
    
        flag:nctf{gzip_base64_hhhhhh}
    

# 10 .文件包含

<http://4.chinalover.sinaapp.com/web7/index.php?file=show.php>  
文件包含漏洞！这一题原谅我这个小白不会做。。。。  
网上看到其他人的。

构建file=<php://filter/read=convert.base64-encode/resource=index.php> 就好

文章可以参考：<http://www.2cto.com/article/201311/258420.html>

image.png

    
    
        nctf{edulcni_elif_lacol_si_siht}
    

# 11 .单身一百年也没用

burp抓一下！！

  

image.png

    
    
        nctf{this_is_302_redirect}
    

# 12 .Download~!

image.png

这道题没有反应过来，url上可以直接下载base64加密的文件名，那么开下脑洞，把download.PHP这个文件下下来波~~

  

image.png

替换

  

    
    
        way.nuptzj.cn/web6/download.php?url=ZG93bmxvYWQucGhw
    

  

有看到了一个关键文件，继续加密下载。

  

key

拿到了KEY

    
    
        nctf{download_any_file_666}
    

# 13 .COOKIE

0==not 题目中给了提示，那1==yes 哈哈，猜一下又不会怀孕~~

用burp抓包看下。 看到了0 改为1 flag就出来了！

  

  

    
    
        flag:nctf{cookie_is_different_from_session}
    

# 14 .MYSQL

Do you know robots.txt？

robots是网站的目录文件~~大佬们应该都知道，我们试下：<http://chinalover.sinaapp.com/web11/robots.txt>
有收获。

提示有几个部分 sql.php 以及 sql代码，仔细观摩下  
id=1024 提示 no! try again  
id=1025 1026 1027 1022 1023 结果一样  
无解，试下1024.5 过了。。。。。精度问题

    
    
        the flag is:nctf{query_in_mysql}
    

# 15 .sql injection 3

sql注入。

# 实在太忙，有空继续更新。。。。。

# 16 .

# 17 .

# 18 .

# 密码学：

## easy!

base64编码。  
密文：bmN0Znt0aGlzX2lzX2Jhc2U2NF9lbmNvZGV9  
可以通过这里来解密：<http://encode.chahuo.com/> （解密网站有很多，可以选择适合自己的）  
flag：nctf{this_is_base64_encode}

# KeyBoard

根据题目给出的提示，按照字母的顺序来看键盘。（表示 第二个字母真的是R么？？？怎么看都是Y 啊）  
flag:nctf{areuhack}

# base64全家桶

# n次base64

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [南邮CTF-WEB-writeup](https://www.jianshu.com/p/19999fa5ca8b)

2018/3/16 17:34:51 WEB题 1.签到题 题目：key在哪里？ writeup:查看源代码即可获...

[Sec小玖](https://www.jianshu.com/u/92820b1051ae)阅读 21,599评论 1赞 11

  * [Bugku------Web（持续更新）](https://www.jianshu.com/p/6750db0943b7)

我使用的是火狐浏览器 使用火狐浏览器的hackbar插件 如果有错误的地方希望大家多多指出，多谢多谢 WEB2 点...

[yangc随想](https://www.jianshu.com/u/5d717255d798)阅读 53,634评论 11赞 16

  * [[南邮OJ]Web](https://www.jianshu.com/p/32e28f023159)

签到2 地址：来源：网络攻防大赛 说了输入zhimakaimen，开始输入没认真看，只能输入10个数字，可是zhi...

[JasonChiu17](https://www.jianshu.com/u/40b8af2a544d)阅读 4,324评论 0赞 9

  * [CGCTF Web-Writeup](https://www.jianshu.com/p/75dc5f2dcf50)

抽空整理了一下CGCTF平台的Web题的writeup。 0x01 签到题(题目地址：http://chinal...

[ch3ckr](https://www.jianshu.com/u/13c720cf85fc)阅读 12,235评论 0赞 6

  * [企业和雇员的关系](https://www.jianshu.com/p/90b45367f7f7)

最近阿里月饼时间闹的沸沸扬扬，抢月饼违反价值观吗，开除是合理的吗，不同的人都持有不同的观点。我想借此机会反思一下企...

[徐清](https://www.jianshu.com/u/8b7550f1ac59)阅读 658评论 0赞 0

 