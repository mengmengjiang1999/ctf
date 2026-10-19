## 声明

文章来自作者日常学习笔记，也有少部分文章是经过原作者授权后转载，未经授权，严禁转载，如需转载，联系开白。请勿利用文章内的相关技术从事非法测试，如因此产生的一切不良后果与文章作者无关。

## 近源渗透--wifi渗透

如今信息时代，信息安全变的格外重要，国家也越来越重视其中的利害。遂鼓励并要求相关企业加强网络安全防护，意识。  
于是攻防演习，护网实战，应运而生，并愈演愈烈  
经过多次的红蓝对抗，在失败与上级要求之下，企业对网络安全的防护不断升级，这也迫使攻击队寻找新的突破口------近源渗透。。。。

就目前来说，我将其分为三点：

> 一、wifi渗透
>
> 二、HLD攻击
>
> 三、社会工程学

本篇主要分享wifi渗透的相关知识，HID攻击后续分享

wifi渗透，我将其分为两点：

> wifi密码的破解
>
> 钓鱼wifi

## wifi密码的破解

 **前置知识：**  
a，自备无线网卡（支持Monitor模式，即监听模式）  
我们平时用的网卡都是混杂模式的，是不支持监听模式的，需要自备，淘宝买一个就ok  
监听模式：监听模式下，可以监听到经过它的所有流量，并且不需要与无线接入点建立连接，就可以接收到目标的mac地址等信息

b，握手包  
握手包：当终端与路由器建立连接时，会先进行认证，认证过程中传输的报文就是握手包。 其中包括了路由器的密 码，所以抓取握手包，获取密码并破解即可实现  
通过网卡的监听模式，可以监听来自经过它的所有流量，从而可以抓取目标的握手包

c，wifi密码的破解方式  
破解方式有很多种，利用路由器的相关漏洞，基于弱加密（WPS，WEP）的破解，以及对WPA/WPA2的暴力破解，就加密算法来说wep<wpa<wpa2<wpa3  
然而现如今市场上的主流路由器加密方式都是wpa2的，所以只能通过字典进行暴力破解

d，Aircrack-ng，是一套用于无线审计的工具，kali自带，里面包含了多种工具，此处主要用到了以下工具  
airmon-ng：改变网卡的工作模式  
airodump-ng：捕获802.11的数据报文  
aireplay-ng：发送注入数据包攻击目标，为后续捕获握手包做准备  
aircrack-ng：对捕获的握手包进行暴力破解

e，密码字典生成工具  
推荐使用crunch，kali自带  
https://blog.csdn.net/weixin_44912169/article/details/105719706

### 开始

1，插入无线网卡，并将其连接至虚拟机kali中，通过iwconfig查看是否接入  
iwconfig主要是查看无线网卡配置的相关信息  
![1.png](https://image.3001.net/images/20210803/1627989563_6109263be1d5b32a9b6ff.png!small)

2，启用网卡  
启用网卡前，建议先kill掉可能会影响的进程：  
airmon-ng check kill  
![2.png](https://image.3001.net/images/20210803/1627989582_6109264e8d28fb2c8e653.png!small)airmon-ng start wlan0  
start后加网卡的名称，通过上一步可以看到  
![3.png](https://image.3001.net/images/20210803/1627989589_61092655d002dddef9f06.png!small)启用之后ifconfig中可以看到本地的网卡信息：  
![4.png](https://image.3001.net/images/20210803/1627989640_610926884b9ce066cfacd.png!small)iwconfig也可以看到网卡的工作模式成为Monitor  
![5.png](https://image.3001.net/images/20210803/1627989650_6109269254bea61578964.png!small)

3，查看附近要攻击目标的wifi相关信息  
airodump-ng wlan0mon  
airodump-ng 加无线网卡的名字，启用监听模式之后无线网卡名称会发生变化，再次通过iwconfig查看即可  
![6.png](https://image.3001.net/images/20210803/1627989668_610926a4ec4ca9c6aa6a8.png!small)图中可以看到目标wifi的相关信息  
我介绍几个主要的参数含义：  
bssid：为目标的mac地址  
 **但是有时候会遇到一个wifi有多个bssid？？？**  
 **在说什么是bssid之前先介绍一下什么是ap的漫游？**

ap可以理解为无线路由器，ap的漫游就是为多个ap设置相同的ssid进行组合，这样可以在其它组合起来的ap上不用输入密码就可以提供服务，比如从一楼到五楼只需要输入一次密码就可以实现跨ap的使用，所以附近的ap都是以漫游的形式组网提供无线服务的  
也就是说，此处嗅探到的bssid代表一个独立的ap，也就是它的mac地址，但是为什么他们的bssid不同，却同属于一个wlan呢，就是因为他们通过ssid实现了ap漫游  
**因此延伸出，如果是像这种情况下进行攻击嗅探，是不会获取到握手包的，因为当你攻击的ap与客户端断开连接之后，他会认为当前ap不让他用，就自动连接至其它具有相同ssid的ap，也就是说，必须把相同ssid的所有ap都进行监听才会捕获到握手包**  
pwr：与目标的距离，该值越大，距离越近  
#data：目标的实时数据传输量  
CH：信道  
ENC：加密方式，可以看到，都是wpa2的  
essid：wifi的名称

4，嗅探并抓取目标的握手包  
分为两步：  
a，通过airodump-ng开启抓包模式  
airodump-ng --bssid D2:77:95:60:E7:00 -c 10 -w t1 wlan0mon  
-bssid是ap的bssid  
-c指的是信道  
-w保存的文件名  
wlan0mon为网卡的名词  
以上信息上图均可看到  
![7.png](https://image.3001.net/images/20210803/1627989739_610926eb5d3ae23f214c5.png!small)图中STATION为连接这个ap客户端的mac地址，需要记录，后续抓握手包使用  
此处需要一直开启监听，之后新开一个终端进行泛洪攻击使客户端与ap断开连接，断开后会自动重新连接，这时才能抓到握手包，也就是说一般只有刚开始连接的时候可以抓到握手包，或者目标在进行大流量传输时，比如使用迅雷等，才会抓到。

b，通过aireplay-ng攻击目标  
aireplay-ng -0 2 -a D2:77:95:60:E7:00 -c 90:78:B2:2D:1E:43 wlan0mon  
-0：冲突攻击，使目标与客户端断开连接，重新连接时从而获取握手包，2指的是攻击两次  
#此值不要设置太大，2次足够了，网上的很多教程都是10次，经过测试是不稳定，如果攻击完两次依然没有握手包就再试一次，就可以了。  
-0攻击的原理  
通过wireshark抓取握手包分析发现  
ffffffff为攻击网卡伪造的mac地址  
![clipboard.png](https://image.3001.net/images/20210803/1627989787_6109271bc167b8c2e3fa7.png!small)airelay-ng攻击的原理是向目标ap不断发送Deauthentication数据包  
该数据包的作用是让当前ap断开与指定客户端的链接，并且在该攻击时间内，所选中的ap无法被连接，类似于拒绝服务攻击  
![8.png](https://image.3001.net/images/20210803/1627989850_6109275a7ed0783267e78.png!small)-a：目标ap的bssid即mac地址  
-c：客户端的mac地址  
以上信息上图均可看到

成功获取握手包。图中红框![9 -副本.png](https://image.3001.net/images/20210803/1627989870_6109276eaa18e1957c928.png!small)处

5，使用aircrack-ng破解握手包，获取密码  
获取到的握手包保存在这里，生成的其它文件也是捕获到的数据包，不过一般用不到，只用这一个  
![11.png](https://image.3001.net/images/20210803/1627989884_6109277c94b59d012c77b.png!small)aircrack-ng -w /home/rookie/桌面/pojie.txt t1-01.cap  
-w：指定密码字典的路径  
后边直接跟cap文件名称  
![12.png](https://image.3001.net/images/20210803/1627989892_61092784ed3554cd8b218.png!small)KEY
FOUND! [ qwe123456 ]

## 钓鱼wifi

钓鱼wifi的框架工具也很多：fluxion，wifiphisher等  
此处我选择fluxion，个人感觉fluxion更人性化，支持的语言达到17种，自然少不了汉语，并且钓鱼模板也比较多  
由于操作步骤繁琐，简化流程如下：  
![13.png](https://image.3001.net/images/20210803/1627989957_610927c514b38ade83c24.png!small)

准备：kali，fluxion，具有收发功能的无线网卡

### 开始：

1，安装fluxion  
kali下git安装 git clone https://www.github.com/FluxionNetwork/fluxion.git  
git完进入该目录执行 ./fluxion.sh 安装即可  
安装完成后进入选择语言界面，17即可  
![14.png](https://image.3001.net/images/20210803/1627989963_610927cb68cc38016473f.png!small)2，捕获目标握手包  
选择完语言之后会进入下面的页面  
1：为创建钓鱼wifi  
2：捕获目标握手包  
此处先捕获目标握手包，选择2  
![15.png](https://image.3001.net/images/20210803/1627989972_610927d4a128bc433c9d1.png!small)之后对扫描的信道选择，此处根据网卡支持的信道进行选择，此处我选择3，对所有信道扫描  
![16.png](https://image.3001.net/images/20210803/1627989978_610927da4302461bba419.png!small)下一步开始扫描，当出现你的目标后，按ctrl+c退出扫描，目标结果会显示出来  
![17.png](https://image.3001.net/images/20210803/1627990027_6109280b03471d7606357.png!small)我的目标就是自己手机的热点，此处输入73  
![18.png](https://image.3001.net/images/20210803/1627990039_61092817e31477a657324.png!small)下一步选择2，跳过  
![19.png](https://image.3001.net/images/20210803/1627990046_6109281eba75e2de3bc8b.png!small)此处选择2通过aireplay-ng获取握手包，与之前实验用的工具是一样的  
![20.png](https://image.3001.net/images/20210803/1627990053_610928259a40799fff48e.png!small)下面的两个选项都选择它推荐的吧  
![21.png](https://image.3001.net/images/20210803/1627990066_61092832c70ab3df4af8c.png!small)![22.png](https://image.3001.net/images/20210803/1627990074_6109283abfe4e9fdd2f86.png!small)然后会出现如图的三个窗口开始捕获
握手包  
左上角窗口显示的是对ap监听抓取握手包的一个记录  
左下角的是握手包抓取结果  
右下角的是使用aircrack的攻击记录  
![23.png](https://image.3001.net/images/20210803/1627990125_6109286d7eb0d4a246abc.png!small)大约等待一两分钟，捕获成功如下图  
![24.png](https://image.3001.net/images/20210803/1627990137_61092879542c16764a81a.png!small)左下图的小窗口，最小化也可以，关掉也可以，至此捕获握手包步骤完成

3，第三步开始攻击真实ap，伪造钓鱼ap，获取密码  
选择1  
![25.png](https://image.3001.net/images/20210803/1627990151_610928871a82e547857b4.png!small)选择1  
![26.png](https://image.3001.net/images/20210803/1627990159_6109288fd785f503bec4e.png!small)选Y，对刚扫描出的目标进行攻击  
![27.png](https://image.3001.net/images/20210803/1627990165_6109289562e4610a86d85.png!small)因没有专用接口，此处跳过该选项  
![28.png](https://image.3001.net/images/20210803/1627990174_6109289e8f3c90c68844f.png!small)选择无线网卡
2  
![29.png](https://image.3001.net/images/20210803/1627990179_610928a38b3d0d895e439.png!small)此处依然使用aireplay进行攻击  
![30.png](https://image.3001.net/images/20210803/1627990187_610928ab884d9a726236b.png!small)下面选择推荐  
![31.png](https://image.3001.net/images/20210803/1627990194_610928b279d4d1f666321.png!small)

验证密码的方式选择1  
![32.png](https://image.3001.net/images/20210803/1627990236_610928dc4817d47bf6f85.png!small)选择1，使用刚刚抓取到的hash文件  
![33.png](https://image.3001.net/images/20210803/1627990243_610928e3f3d41e30cdd31.png!small)选择推荐的  
![34.png](https://image.3001.net/images/20210803/1627990251_610928ebaa8896fb0bead.png!small)创建钓鱼ap，此处选择1  
![35.png](https://image.3001.net/images/20210803/1627990257_610928f174cd0b950fed4.png!small)选择仿真网络  
![36.png](https://image.3001.net/images/20210803/1627990264_610928f886fab95ae33f7.png!small)可以看到很多钓鱼模板：  
此处根据情景进行选择，我选择 3 中文的模板  
![37.png](https://image.3001.net/images/20210803/1627990272_610929004d4b0d125c040.png!small)

选择完钓鱼模板后，会自动开启钓鱼服务，出现下图的六个窗口  
分别代表 钓鱼ap的服务信息，dns信息，认证密码保存信息，服务器的访问记录以及攻击真实ap的记录  
![38.png](https://image.3001.net/images/20210803/1627990288_61092910f10f4b3ec97b2.png!small)出现右上角的窗口代表钓鱼成功，密码保存的位置会显示  
![39.png](https://image.3001.net/images/20210803/1627990300_6109291cdd40f220920e8.png!small)查看密码  
![40.png](https://image.3001.net/images/20210803/1627990317_6109292dcecad4699bb2b.png!small)钓鱼端会显示如下  
![41 -副本.gif](https://image.3001.net/images/20210803/1627990344_61092948b1ef804b0fa3a.gif!small)真实的wifi怎么连都连不上，因为这时候我们一直对其进行泛洪攻击，路由器是不会响应你的请求的，这时候下面会有个同名的，很有可能就会点一下，之后让你输入密码。  
![42.jpg](https://image.3001.net/images/20210803/1627990398_6109297e68efc759e0bed.jpg!small)输入的密码记录后，与之前的握手包校验，校验成功则会停止攻击并导出密码，否则继续攻击。

所有的钓鱼模板如下，并且均可修改  
试想一下，如果攻击者在了解你的路由器品牌下，搭建对应的前台html页面，被钓者应该很容易就会上钩  
![44.png](https://image.3001.net/images/20210803/1627990443_610929abea776e52801fc.png!small)

## 总结

钓鱼wfi也好，破解密码也好，都是为获取目标的密码  
可能很多人都会说获取到密码又能怎么样呢  
我只说几个危害吧，肯定不止这些：

> 1，获取密码后，如果再是公司内网，那危害就不言而喻了吧
>
> 2，很多人，wifi密码，与ap的管理密码一致，这样导致ap也被目标拿下，并可进行中间人攻击了
>
> 3，进入局域网，嗅探抓取局域网内的所有流量，那么你的秘密都被我掌握了  
> 。。。。。。

### 简单提几点防护建议

> 对于wifi的密码的加密认证方式只采用wpa2
>
> 对于密码要求，大小写，字母，数字，特殊字符混合使用
>
> 不要连接没有密码的wifi
>
> 隐藏wifi的ssid  
> 。。。。。。

这毕竟是搭建的有限环境，出现的问题也都解决了，我相信实战中可能会遇到更多的问题，有位师傅曾经说过：当你遇到问题的时候，就是你成长的时候。  
期待着问题到来，期待着成长的到来

