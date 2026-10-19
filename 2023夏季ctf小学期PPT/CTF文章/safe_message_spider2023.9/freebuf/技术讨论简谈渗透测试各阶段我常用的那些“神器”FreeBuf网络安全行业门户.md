***本文作者：flagellantX，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

 **PS：本文仅用于技术分享与讨论，严禁用于非法用途**

![页首配图](https://image.3001.net/images/20180829/1535507416_5b85fbd8df497.jpg!small)

## 前言

**本人所有文章都很用心的写作完成，并时常总结如何分享更有用的东西给朋友们。这篇更是如此，晚上准备到凌晨四点开始写作，为了需要的朋友而写，不喜欢的右上角点叉不要像上次文章一样在下面喷粪逼我骂你，另疏漏之处欢迎有心的道友下方补充帮助更多的朋友们。**

flagellantX's Windows Weapon
是我整理的在windows下针对基础入侵渗透的一个工具包，放置在百度网盘，为了方便需要的朋友使用和更新。

> <https://pan.baidu.com/s/1iKILpYMz0vM_x1zC3Xq3lA>  
>
>
> 提取密码：9efg

工具包分类如下，接下来逐一来讲：

![工具包.jpg](https://image.3001.net/images/20180829/1535487995_5b85affb69ff7.jpg!small)

## 0x01 漏洞盲扫

我记得最先学安全的时候是从入侵渗透入手的，那时候入门的前辈讲的很清楚，告诉我要思维带着工具去扫，当时我不能完全理解，就使用既简单又有效的无外乎扫描器全上，所有域名全扫，也就是这个分类的由来，“盲扫”

 **硬件要求：** 如果要扫描器一起上，建议内存大于8GB，本人计算机是aw15-i7-6700/16GB

### awvs11:

安装包和破解补丁一并打包了，这款扫描器前身是wvs，目录下有awvs10.5，与11在界面上是完全不一样的(同时安装两者可能引起冲突)，两者测试功能并不相差太多，我个人相对使用11较多，使用只要创建扫描(AddTarget)就可以开始，如图：

![awvs1.jpg](https://image.3001.net/images/20180829/1535488648_5b85b288a0e15.jpg!small)

![awvs2](https://image.3001.net/images/20180829/1535488648_5b85b28888a3d.jpg!small)

### Netsparker4.9.1.16896:

安装稍有不同需要将破解文件复制到软件根目录进行覆盖即可，然后填入域名即可开始扫描目标，如下：

![Netsparker4.9.1.16896](https://image.3001.net/images/20180829/1535488985_5b85b3d9e2bf7.jpg!small)

![Netsparker4.9.1.16896](https://image.3001.net/images/20180829/1535488985_5b85b3d9926b8.jpg!small)

### AppScan9.0.3.6:

主流的一款企业级扫描器，容量很大，也很强大，支持扫描webservice。下载需要花费时间，其它没有什么难度，相对扫描时间要比其它扫描器花费更多时间，电脑内存最好大于8GB，若是4GB内存只开appscan可以带起，不过不宜再多开其它漏扫。

![AppScan9.0.3.6:](https://image.3001.net/images/20180829/1535489586_5b85b6329953b.jpg!small)

安装包安装完成之后将动态链接库文件覆盖到根目录即可

![覆盖到根目录](https://image.3001.net/images/20180829/1535490047_5b85b7ff3310d.jpg!small)

选择需要的扫描类别，开始扫描后再问题处查看报出的漏洞情况。

![查看报出的漏洞情况](https://image.3001.net/images/20180829/1535490141_5b85b85d547b8.jpg!small)

### Burpsuite1.7.26：

Burp优秀的挖洞，数据分析、爆破、撞库功能下常常会忽略它的漏扫功能，这里将它放在漏扫是因为它确实能担当的住，这里分享的版本可以永久使用，监听好后访问目标域名选择sipder和scanner模块即可，这里不演示了。

![Burpsuite1.7.26：](https://image.3001.net/images/20180829/1535490473_5b85b9a9d185c.jpg!small)

### uniscan6.2：

kali下的uniscan，使用命令是`uniscan -u <http://www.target.com/>
-qweds`，而在windows的版本需要搭建php环境，由于我自己目前windows下使用很少所以就不搭建了，它对于扫xss漏洞的能力十分强硬，而且十分全面可以挖掘泄露文件，我比较喜欢它的挖掘邮箱功能和找xss的能力，一个可以用于钓鱼，另一个可以拿来构造xss持久化控制。

![uniscan6.2](https://image.3001.net/images/20180829/1535490754_5b85bac24528b.jpg!small)

![uniscan6.2目录](https://image.3001.net/images/20180829/1535490909_5b85bb5d64049.jpg!small)

### DirBuster-0.12：

也是人人都知道的Fuzzing工具，就不多介绍了，我记得它有一些小功能比较突出，暂时忘了。

![Fuzzing工具](https://image.3001.net/images/20180829/1535491097_5b85bc194221a.jpg!small)

### Safe3WVS 10.1：

用过的都知道是一个威力强劲的挖洞神器，又小又轻便，生成报告很快，不过不支持在虚拟机使用，使用给一个小建议，不要都勾上，单个单个扫效率更高。

![Safe3WVS
10.1](https://image.3001.net/images/20180829/1535491314_5b85bcf23a876.jpg!small)

### WebRobot v1.8.2：

洪流前辈的作品，神级爬虫一出，心里自然有数，不用多说。

![WebRobot
v1.8.2](https://image.3001.net/images/20180829/1535492766_5b85c29e46960.jpg!small)

当然不仅仅是爬虫，我就很喜欢用它的域名爆破和链接分析。

### 御剑三件套:

 **御剑1.5+御剑后台扫描珍藏版+御剑无字典大小限制1937版。**

几代人的回忆就不说了，经典中的经典，效果在现在用也不逊色，往往能给你惊喜，作者也说得很清楚，想念初恋而作，初恋就是这样，如果初恋很美，或许美在回忆那得不到回不去的过去。

![御剑三件套](https://image.3001.net/images/20180829/1535491663_5b85be4f0fc41.jpg!small)

字典的可自定义让御剑能一直御剑江湖，1.5内含的字典较全面。

### Wscan6+Pker多线程后台极速扫描工具2.01：

这两款工具有些年代感，推荐它们是因为早期立过功，扫描速度很快很迅速，找后台找备份找db能力都不俗，其中pkav可是当时乌云的第一天团，办的培训也很靠谱，学成出山的高手众多，只是那时候我还在打酱油，钱不够，哈哈。

当然现在也不够，哈哈。

![Wscan6+Pker多线程后台极速扫描工具2.01](https://image.3001.net/images/20180829/1535492260_5b85c0a4b745b.jpg!small)

## 0x02 资源收集

收集的有：低级域名、url采集、端口扫描

### 子域名收集

 **Layer4.2纪念版：**

![Layer4.2纪念版](https://image.3001.net/images/20180829/1535495116_5b85cbcc0c825.jpg!small)

 **subDomainsBrute** ：

![subDomainsBrute](https://image.3001.net/images/20180829/1535495862_5b85ceb631509.jpg!small)

![subDomainsBrute](https://image.3001.net/images/20180829/1535496727_5b85d21785f0f.jpg!small)

这两个子域收集使用肯定是最多的，在windows环境下layer的会比较方便。

### 端口扫描

 **zenmap** ：

![zenmap](https://image.3001.net/images/20180829/1535496076_5b85cf8c3f7af.jpg!small)

zenmap就不多介绍了,windows下的nmap，使用语法可以网上查找手册，进阶看这个：<http://www.freebuf.com/column/149716.html>。

 **Portscan+御剑TCP：**

这两款我都非常喜欢，在win环境下使用非常方便，特别是御剑也的确配的上高速二字，另外一个端口扫描可以更全面的进一步了解,在内外网都可以有建树。

![Portscan+御剑TCP](https://image.3001.net/images/20180829/1535496562_5b85d17267c64.jpg!small)

 **url采集：**

url采集可以用于扩大攻击面、收集低级域名、同站C段、新的exploit进行规模测试。

![url采集](https://image.3001.net/images/20180829/1535497436_5b85d4dcbd7c7.jpg!small)

## 0x03 渗透测试

### 字典撞库

这招一般是用来配合burp进行挖洞测试的，因为这块准备的匆忙，所以就罗列了几个常用的字典。

![字典撞库](https://image.3001.net/images/20180829/1535497845_5b85d675494bf.jpg!small)

### 中间件漏洞

测试工具是对st2和weblogic，jboss，WebSphere等。st2这款工具多被用于批量挖洞，中间件漏洞中常见端口例如8080，9000，7001
和常见路径例如/console/，/manager/html以及不同中间件对应的弱口令也要掌握，最好的中间件攻击手段是通过端口的弱口令设备爆破，其次才是exploit批量。

![中间件漏洞](https://image.3001.net/images/20180829/1535498412_5b85d8ac1ba38.jpg!small)

### 心脏出血

最好的检测工具莫过于CrowdStrike Heartbleed Scanner了,拿到网段就可以进行测试，无在乎外网内网。

![心脏出血](https://image.3001.net/images/20180829/1535498499_5b85d90310b41.jpg!small)

### IIS写权

同样也是拿到网段即可测试，用到的是经典工具IISPutScanner /桂林老兵前辈的iiswrite /08sec的IISPutScanner。

![IIS写权](https://image.3001.net/images/20180829/1535498914_5b85daa264a98.jpg!small)

 **.svn源码泄露：**

![.svn源码泄露](https://image.3001.net/images/20180829/1535499028_5b85db14ac671.jpg!small)

直接祭出法器就行了。

### 文件上传

我没有准备任何工具，但是准备了一份经典的文件上传漏洞详解，相信不熟悉的朋友看了就可以了解到：

![文件上传漏洞详解](https://image.3001.net/images/20180829/1535499182_5b85dbae0663e.jpg!small)

![文件上传漏洞详解](https://image.3001.net/images/20180829/1535499222_5b85dbd634fe0.jpg!small)

### 口令爆破

我打包的是hydra，学习链接在freebuf中就可以找到很多：<http://search.freebuf.com/search/?search=hydra#article>。

### 编辑器漏洞

我打包了一个ietester，只要在网络上搜索对应编辑器漏洞就会有利用过程。

 **XSS+CSRF+SQLI：**

<https://xsspt.com/>，很nice的一个平台，不仅免费而且在学习栏目中收集了乌云的xss漏洞类别的所有漏洞案例，可以站在前人的肩膀上进行学习。

![XSS+CSRF+SQLI](https://image.3001.net/images/20180829/1535499677_5b85dd9da35b3.jpg!small)

作为拓展也打包了慢雾科技老总黑客猥琐流派系创始人钟晨鸣和天融信阿尔法实验室国内html5攻防第一人徐少培的著作《Web前端黑客技术揭秘》来作为延伸提高资料。

![web前端黑客技术揭秘](https://image.3001.net/images/20180829/1535499813_5b85de25dcbd7.jpg!small)

CSRF就打包了两个常规测试的工具OWASP-CSRFTester和CSRF-Request-Builder使用方法只要你愿意在网络上搜索都可以轻松找到完美教程。

注入方面打包了胡萝卜穿山甲sqlmap的常用工具外，我还添加了一个SQLHunter的叫做注入猎人可以用来进行批量找注入点，但是需要你有代理到外面才可以用，另外我修改了一些sqlmap的脚本，例如你嫌它脱裤太慢，你可以把线程最高加到65535只要你机子吃得消，但是Windows线程Max是65535，Kali2.0线程Max是15750，过犹不及。

![sqlmap的脚本](https://image.3001.net/images/20180829/1535500342_5b85e0366d553.jpg!small)

## 0x04 内网用具

### NetFuke+Cain4.9：

作为老牌的内网杀器这两个大家都不陌生，前者用来域名劫持多，后者用来嗅探密码，但是动静太大，一不小心会把内网瘫痪掉，打包里有使用教程，Cain该隐的话看这个吧：<https://www.jianshu.com/p/facff81a4826>。

![NetFuke+Cain4.9](https://image.3001.net/images/20180829/1535501935_5b85e66fe6e24.jpg!small)

![NetFuke+Cain4.9](https://image.3001.net/images/20180829/1535501936_5b85e6702d1db.jpg!small)

### EvilFoca：

这款工具对内网渗透摸索过的朋友肯定也在用了，局域挂个黑页是手到擒来，但其实可以配合浏览器漏洞、钓鱼页面等等进行做到更多的事情，IE0DAY可以让目标劫持到漏洞网址进行exec木马，没有0day也可以构造一个上网助手页面，wifi.exe或者update.exe作为木马欺骗网内用户下载。工具打包了使用教程，文章是freebuf中作者写的，也可以在站内进行搜索。

![EvilFoca](https://image.3001.net/images/20180829/1535502157_5b85e74ddbc79.jpg!small)

### 局域网查看工具+MAC地址扫描+啊D网络工具包：

三款都是老工具，但是会搞的OG肯定都玩过这些，当年也是威力不俗的利器,比如肉鸡木马种植机，别告诉我你没玩过。

![老工具](https://image.3001.net/images/20180829/1535502439_5b85e867ec127.jpg!small)

![MAC](https://image.3001.net/images/20180829/1535502439_5b85e867eb76c.jpg!small)

![局域查看](https://image.3001.net/images/20180829/1535502440_5b85e86800d94.jpg!small)

### Wireshark:

![Wireshark](https://image.3001.net/images/20180829/1535502570_5b85e8ea8f1b2.jpg!small)

### Intercepter-NG：

我要推的就是这款来自俄国的力量，功能十分强悍，集成内涵有x-scan，可以各种劫持，嗅探，注入，中间人，检测心脏出血，爆破等等各种功能可以驰骋内网，使用教程近日我会往微博发布，很吊但又是非常冷门的软件。

![Intercepter-NG](https://image.3001.net/images/20180829/1535502920_5b85ea4848909.jpg!small)

![Intercepter-NG](https://image.3001.net/images/20180829/1535502920_5b85ea4847607.jpg!small)

![Intercepter-NG](https://image.3001.net/images/20180829/1535502920_5b85ea4848569.jpg!small)

![Intercepter-NG](https://image.3001.net/images/20180829/1535502920_5b85ea48ab0e9.jpg!small)

## 0x05 权限维持

废话不多说，先上图：

![提权.jpg](https://image.3001.net/images/20180829/1535503194_5b85eb5a55099.jpg!small)

webshell中内置了很多绕过各种安全软件的shell，也有很多可能被杀了，因为这篇是基础的入侵渗透，如果要相对高级冷门的shell可以看我微博的那篇1kb后门持久控制系统绕过安全软件。lcx和NtGodMode都是用来简单提权的，操作也简单，百度就可以很快找到，Cknife和caidao就都是webshell管理工具了，大家也都知道。权限维持的话我比较喜欢用RAT，所以今天的重点是分享的这三款：

### LeGend Rat + Orcus Rat + njRAT:

![LeGend Rat + Orcus Rat +
njRAT](https://image.3001.net/images/20180829/1535503659_5b85ed2b67898.jpg!small)

如果想演示远程入侵，又没有酷酷的远控，现在这个问题是不是就解决了？

## 0x06 清洁工人

这部分的起因是这样的，有时候需要快速的拿几台中转服务器，我经常会用比较老的nday，导致黑下来的服务器不是中了挖矿就是lpk全盘感染的ddos肉鸡，所以我就打了个包把火绒剑和360卫士放在一块，当然首选还是火绒剑，360卫士经常无法开启完全保护，火绒体积小安装快，万人骑机器的木马都没什么技术含量更别提免杀了所以直接就可以杀掉，很快速就能让机器干净出来。

![火绒](https://image.3001.net/images/20180829/1535504028_5b85ee9cbb70f.jpg!small)

![huorong1.jpg](https://image.3001.net/images/20180829/1535504060_5b85eebc59e9e.jpg!small)

## 0x07 侦探服务

起因:年幼时碰到个打游戏的朋友居然可以知道我的ip地址，还用蜗牛ddos啥的让我网络掉线，逐百度之，找到了古老绝技QQ显ip，前几年国内出现了一批ip定位接口网站，两者结合玩起。

![ip定位接口](https://image.3001.net/images/20180829/1535504233_5b85ef6947e79.jpg!small)

## 0x08 网络渔点

用来快速的搭建一个临时网站环境使用：

![搭建一个临时网站环境](https://image.3001.net/images/20180829/1535504367_5b85efefdbf27.jpg!small)

## 0x09 压力测试

自己瞎折腾的一款工具，如名字叫极光(Aurora)一般威力也非常大，本来不想放出来的，缺点是发动后要从进程处结束，如果没有ip黑名单一枪能秒掉很多网站，不过再者后只要有一个简单的ip过滤我这个小脚本也就没辙了，就当做压力测试吧。

![极光](https://image.3001.net/images/20180829/1535504724_5b85f1543c4d9.jpg!small)

我加过se壳所以可打印字符有http信息，但这个跟我没关系，不知道为啥，原生文件静态分析贴下面。

![原生文件静态分析](https://image.3001.net/images/20180829/1535505218_5b85f342bc204.jpg!small)

![原生文件静态分析](https://image.3001.net/images/20180829/1535506215_5b85f7272957f.jpg!small)

![原生文件静态分析](https://image.3001.net/images/20180829/1535506272_5b85f7603fdf5.jpg!small)

## 0x10 代理软件

我写了8个匿名度高的科学软件，价格都不便宜，真应该问他们要广告费，大家还是别买了，用国外服务器划算，(￢︿̫̿￢☆)，因为这篇是基础教程就不写太多，有空在微博上教大家搞国外的免费RDP。

## 结语

准备时间不算凌晨四点到现在次日9：36，并不是夸耀什么，只是想告诉读者们这个文章我是充满诚意用心在弄的，希望对大家有帮助。

 ***本文作者：flagellantX，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

