![photo-1530692228265-084b21566b12.jpg](https://image.3001.net/images/20180705/15307248741522.jpg!small)

*****本文原创作者：flagellantX，属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **通篇是一个模拟的思路架构，以及一些演示，朋友们有了点以后肯定能耍的比我⑥~**

 **环境：**

win10 runing kali

两个环节:beef-xss钓鱼环节(建议使用服务器)、Nday钓鱼环节(很好用)、钓鱼框架环节(便携好用)

 **渔具(演示用)：**

ngrok、beef-xss、CVE-2017-17692、CVE-2015-5119、CVE-2016-0189(ms16-051)、setoolkit、spf、weeman

 **彩蛋环节：**

> 一个钓鱼利器
>
> 一个不跟踪搜索引擎
>
> 一个最新的web扫描器
>
> 几个高匿名的上网小助手

首先我们要让win10的kali跑起来，可以直接前几天专栏的文章，这里简单叙述下。

首先我翻kali官方文档看到这个<https://www.kali.org/news/kali-linux-in-the-windows-app-store/>

![1.png](https://image.3001.net/images/20180703/15306096392541.png!small)

我们接着就可以实操，打开Microsoft store，输入kali linux进行获取应用

![2.jpg](https://image.3001.net/images/20180703/15306096604413.jpg!small)

获取好了以后在powershell这里按照官方文档运行这段命令 。  

![3.jpg](https://image.3001.net/images/20180703/15306096776561.jpg!small)![4.jpg](https://image.3001.net/images/20180703/15306096803707.jpg!small)关闭windowsdefener或者将kali包加入信任，就可以开始使用了。
![5.jpg](https://image.3001.net/images/20180703/15306096991660.jpg!small)

安装metasploit的命令是sudo apt-get install metasploit-framework，beef:sudo apt-get
install beef-xss,nmap:sudo apt-get install
nmap，总而言之kali上的所有工具都可以如此安装而且github上的工具也可以使用git clone。

![6.jpg](https://image.3001.net/images/20180703/15306097162736.jpg!small)![7.jpg](https://image.3001.net/images/20180703/15306097197981.jpg!small)直接在cmd窗口输入kali即可进入，非常便捷。![8.jpg](https://image.3001.net/images/20180703/15306097663743.jpg!small)

 **beef-xss钓鱼布置：**

切换到beef-xss目录，以管理员身份打开beef。![9.jpg](https://image.3001.net/images/20180703/15306097805263.jpg!small)

打开ngrok将http流量转发到3000端口。

先在这个目录下删除ngrok的authtoken(如果之前玩过我前面几招的)，这样让ngrok可以同时转发多个http端口。![10.jpg](https://image.3001.net/images/20180703/1530609796877.jpg!small)![11.jpg](https://image.3001.net/images/20180703/15306097997284.jpg!small)

这时候转发一个80端口，配合hsf写入hook搭建一个临时的钓鱼链接。  

![12.jpg](https://image.3001.net/images/20180703/15306098243237.jpg!small)![13.jpg](https://image.3001.net/images/20180703/15306098271250.jpg!small)![14.jpg](https://image.3001.net/images/20180703/15306098306858.jpg!small)beef的控制页面和hook地址。  

![15.jpg](https://image.3001.net/images/20180703/15306099464620.jpg!small)![16.jpg](https://image.3001.net/images/20180703/15306099492583.jpg!small)然后很显然这样转发一个beef老是掉，甚至可能连hijack都拿不到，所以我强烈建议你用服务器，不要这样用，但是这个方式可以用于自写前端接收一些账号密码，以及ngrok的http协议多端口转发，所以还是有必要写一下,当然如果你在外网服务器上搭建beef这套，直接就可以用了。

**Nady钓鱼环节:**

这边开始的就是今天比较重磅的环节。

打开msf，因为都是钓鱼的，使用http协议，一并将ngrok转发到http 9999作为测试使用。

![17.jpg](https://image.3001.net/images/20180703/15306103712629.jpg!small)当然你也可以布置不同的转发端口，因为上面我们已经删掉了token。![18.jpg](https://image.3001.net/images/20180703/15306103917959.jpg!small)CVE-2017-17692![19.jpg](https://image.3001.net/images/20180703/1530610420508.jpg!small)复制ngrok的链接，进行缩短或者如何都可以，我们这里只是测试，如果实战的话我建议你购买钓鱼域名，当然调戏py是无所谓的。![20.jpg](https://image.3001.net/images/20180703/15306104793982.jpg!small)![21.jpg](https://image.3001.net/images/20180703/15306104827621.jpg!small)![22.jpg](https://image.3001.net/images/20180703/15306104856676.jpg!small)
![23.jpg](https://image.3001.net/images/20180703/15306104898729.jpg!small)CVE-2015-5119，hackingteam这个nday就转发到8080端口吧。![24.jpg](https://image.3001.net/images/20180703/15306106808938.jpg!small)

测试的攻击link在ngrok自取。

CVE-2016-0189(ms16-051针对IE11)

![26.jpg](https://image.3001.net/images/20180703/15306107124457.jpg!small)

![27.jpg](https://image.3001.net/images/20180703/15306108572242.jpg!small)

 **钓鱼框架：**

我说过，win10上的kali具备所有kali功能，所以我们可以git clone使用我们想要的脚本来进行攻击测试。

简单的用setoolkit来测试一下。

**安装**![29.jpg](https://image.3001.net/images/20180703/15306141806977.jpg!small)

要等很久，然后cd set /python setup.py install进行安装。

lol，等了两个小时(我的网渣)，成功安装了，喜悦的心情不以言表，看一下亲切的set。  

![30.jpg](https://image.3001.net/images/20180703/15306152788124.jpg!small)测试一下功能。

![31.jpg](https://image.3001.net/images/20180703/15306155878449.jpg!small)

ok，完全欧98k。

![32.jpg](https://image.3001.net/images/20180703/15306161599057.jpg!small)![33.jpg](https://image.3001.net/images/20180703/15306161715384.jpg!small)

![34.jpg](https://image.3001.net/images/20180703/15306161453242.jpg!small)SPF：(<https://github.com/flagellantX/SPF>)

 **启动演示：**

![spf4.jpg](https://image.3001.net/images/20180705/15307245645154.jpg!small)

![spf.jpg](https://image.3001.net/images/20180705/1530722202827.jpg!small)![spf2.jpg](https://image.3001.net/images/20180705/15307222518789.jpg!small)
你要转发到外网也同理。

![spf3.jpg](https://image.3001.net/images/20180705/1530722495800.jpg!small)

weeman：(<https://github.com/flagellantX/weeman>)

**运行演示：**

![weeman2.jpg](https://image.3001.net/images/20180705/15307246656307.jpg!small)

![weeman1.jpg](https://image.3001.net/images/20180705/15307247146474.jpg!small)

以上通篇差不多就结束了，非常感谢你读到这里，因为我花了一下午到晚八点写了这些，当然手残和网速也是因素。

 **接下来是彩蛋环节：**

这个钓鱼利器真的很酷(<https://github.com/flagellantX/gophish>)，使用文档(<https://getgophish.com/documentation/>)我建议热衷于当渔夫的读者们可以学习一下如何使用，我搜索了一下fb没有人写，如果过段时间还没有写我会写的。  

![gophish_purple.png](https://image.3001.net/images/20180703/1530617477471.png!small)

<https://github.com/flagellantX/SearX>
通过这个脚本可以在kali上打造自己的搜索引擎，比起google它更像duckgogo吧，具体的看怎么用了。  

 **安装**

![cd.jpg](https://image.3001.net/images/20180703/15306293873420.jpg!small)

![cd1.jpg](https://image.3001.net/images/20180703/1530629421599.jpg!small)
我们来看一下搜索效果：

还可以，该有的都有了

![cd2.jpg](https://image.3001.net/images/20180703/15306294846554.jpg!small)![cd3.jpg](https://image.3001.net/images/20180703/15306295253396.jpg!small)总之很不错的，比国内一些搜索引擎靠谱，至少不会跟踪你。

扫描器的故事：

我在irc看到有一只汪上线了，然后我问他有没有好的漏扫，我的英语还是chinese很english好的，你们可以看的到

![scanner.jpg](https://image.3001.net/images/20180705/15307289806808.jpg!small)

![scanner1.jpg](https://image.3001.net/images/20180705/15307300495970.jpg!small)扫描器还是挺酷的，但是没能把nsa黑掉有点遗憾。

官网:<https://www.vegabird.com/vooki/>

我帮你们打包了教程和安装文件：

链接老是掉，补到微博里了。

<https://weibo.com/6008521503/GorsJaj77>

匿名性高的一些上网小助手：

1.IPVANISH <https://www.ipvanish.com>

2.Private <https://privatevpn.com/>

3.Nordvpn <https://nordvpn.com>

4.STRONG VPN <https://strongvpn.com>

5.Overplay VPN <https://www.overplay.net>

今天这部分文章有点长(不夸张地说打结尾的现在我自己都忘了我写了啥)，视频教程的话近期会在微博贴出，你也不需要完全按照我的方法和步骤去弄，我用ngrok来当实验的想法很简单，你只需要一个本机一个ngrok就可以上战场了，非常便携，还有就是ngrok可以保护我们攻击者的发出ip，如果用服务器的话，你必须采取手段来隐藏你的ip，方法有很多，但一定要采取，不然你的服务器要是不够好，起码也要比fb官网的服务器好吧，如果对同类型玩家发起这类攻击，他/她/它
抓到你服务器的ip粗暴的直接就把你D了，连pwn都懒得，那么钓鱼的意义就不大了，还是老规矩，我是一个很热衷与攻防研究的家伙，如果你喜欢我的东西，我非常欢迎你来找我一起交流些干货，weibo@flagellantX,
thanks。

尾部再送个photo。

![photo-1517607908060-9a66da662869.jpg](https://image.3001.net/images/20180703/15306179066316.jpg!small)

黑客就是平淡无奇中的一抹红色

End...............

 ***本文原创作者：flagellantX，属于FreeBuf原创奖励计划，未经许可禁止转载**  

