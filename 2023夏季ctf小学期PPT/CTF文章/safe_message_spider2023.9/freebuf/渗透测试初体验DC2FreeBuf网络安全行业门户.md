渗透测试初体验：DC-2

经历了DC-1的渗透流程熟悉和工具安装，DC-2应该就比较熟悉了，下面我们直接开始。

## 一、 靶机下载和安装

<https://www.vulnhub.com/entry/dc-2,311/>  

![1660486260_62f9027401846edcd6b2a.png!small?1660486260444](https://image.3001.net/images/20220814/1660486260_62f9027401846edcd6b2a.png!small?1660486260444)

查看一下说明，需要添加host

![1660486266_62f9027a4c93061bbf01d.png!small?1660486266704](https://image.3001.net/images/20220814/1660486266_62f9027a4c93061bbf01d.png!small?1660486266704)

看了一下介绍，需要使用如下命令添加host

sudo nano /etc/hosts

![1660486303_62f9029fa758c366c505e.png!small?1660486304690](https://image.3001.net/images/20220814/1660486303_62f9029fa758c366c505e.png!small?1660486304690)

使用Ctrl+X即可进行保存和离开

通过查看介绍，发现跟DC-1差不多，作者也是预埋了五个Flag，一步一步的指导初学者找到最后的root权限，最终的目标就是找到服务器的root权限。

![1660486290_62f902921030aa1c7f8be.png!small?1660486301017](https://image.3001.net/images/20220814/1660486290_62f902921030aa1c7f8be.png!small?1660486301017)

靶机下载完成，直接导入，设置网络为NAT模式，如果搜索不到的话就跟DC1一样，重置一下虚拟网络编辑器

靶机安装完成如下图

![1660486293_62f902951a9c0b405573d.png!small?1660486301017](https://image.3001.net/images/20220814/1660486293_62f902951a9c0b405573d.png!small?1660486301017)

## 二、 信息收集

### 1、namp扫描

Kali的IP地址如下192.168.235.129/24

![1660486301_62f9029d4076a313da675.png!small?1660486302202](https://image.3001.net/images/20220814/1660486301_62f9029d4076a313da675.png!small?1660486302202)

使用nmap扫描该网段，可以看到128网段开了80端口

![1660486303_62f9029f97352234241b5.png!small?1660486304693](https://image.3001.net/images/20220814/1660486303_62f9029f97352234241b5.png!small?1660486304693)

直接访问提示报错

![1660486308_62f902a4883b7254246b3.png!small?1660486308910](https://image.3001.net/images/20220814/1660486308_62f902a4883b7254246b3.png!small?1660486308910)

添加host之后再访问，发现就已经可以访问了

  

![1660486319_62f902afbdc797ff93682.png!small?1660486320345](https://image.3001.net/images/20220814/1660486319_62f902afbdc797ff93682.png!small?1660486320345)![1660486313_62f902a9e4490d732a79c.png!small?1660486314444](https://image.3001.net/images/20220814/1660486313_62f902a9e4490d732a79c.png!small?1660486314444)

页面随便翻一下，结果发现了两个信息，一个是使用的WordPress，还有一个就是Flag1

![1660486328_62f902b89a3efd13c0b39.png!small?1660486329120](https://image.3001.net/images/20220814/1660486328_62f902b89a3efd13c0b39.png!small?1660486329120)

你通常的词表可能不起作用，因此，也许你只需要成为cewl。密码越多越好，但有时你无法赢得所有密码。以个人身份登录以查看下一个标志。如果找不到，请以另一个身份登录。

意思应该是第二个flag要去环境里面找，要登录一下其他的用户

使用nmap加强扫描一下

nmap -sS -sV -sC -O -p 192.168.235.128

知道了WordPress的版本等一系列信息

![1660486337_62f902c184c1ccf65d8a8.png!small?1660486338122](https://image.3001.net/images/20220814/1660486337_62f902c184c1ccf65d8a8.png!small?1660486338122)

### 2、目录扫描

![1660486342_62f902c64e873f85ac4ad.png!small?1660486343064](https://image.3001.net/images/20220814/1660486342_62f902c64e873f85ac4ad.png!small?1660486343064)

看看有没有什么比较敏感的信息，发现了后台admin 的地址

![1660486349_62f902cd591cf83d2eaf7.png!small?1660486350315](https://image.3001.net/images/20220814/1660486349_62f902cd591cf83d2eaf7.png!small?1660486350315)

Flag1提示的应该就是要登录这个后台管理台的地址，要获取用户名和密码

![1660486355_62f902d3af02e4f593207.png!small?1660486356156](https://image.3001.net/images/20220814/1660486355_62f902d3af02e4f593207.png!small?1660486356156)

### 3、登录页面的试探

![1660486361_62f902d90477301fffbc4.png!small?1660486361965](https://image.3001.net/images/20220814/1660486361_62f902d90477301fffbc4.png!small?1660486361965)

提示admin密码错误，那么应该存在admin用户

用户名错误会提示用户名错误

![1660486367_62f902df681ac9c09ba36.png!small?1660486367891](https://image.3001.net/images/20220814/1660486367_62f902df681ac9c09ba36.png!small?1660486367891)

重置密码需要输入注册的用户名或者邮箱，之后会给邮箱发送新的验证码，并且试了几下好像是没有防暴力破解的机制。

![1660486374_62f902e6aa15ed81e3f58.png!small?1660486375139](https://image.3001.net/images/20220814/1660486374_62f902e6aa15ed81e3f58.png!small?1660486375139)

### 4、总结

到这里，我们知道了以下信息

  * 后台管理台登录页面，以及存在admin用户，没有防暴力破解的机制，那么就可以使用进行一下暴力破解，提示使用cewl
  * 知道了使用的是WordPress框架及版本 ，可以使用msf看看有没有可以攻击的

## 三、 漏洞扫描及利用

### Flag1:

第一个flag已经找到了，就在主页上面，提示了要用不同的用户登录从而获取flag2,并且要使用cewl。

首先我们要利用wpscan工具

https://www.freebuf.com/sectool/174663.html

WPScan是Kali
Linux默认自带的一款漏洞扫描工具，它采用Ruby编写，能够扫描WordPress网站中的多种安全漏洞，其中包括主题漏洞、插件漏洞和WordPress本身的漏洞。最新版本WPScan的数据库中包含超过18000种插件漏洞和2600种主题漏洞，并且支持最新版本的WordPress。值得注意的是，它不仅能够扫描类似robots.txt这样的敏感文件，而且还能够检测当前已启用的插件和其他功能。

我们利用一下枚举用户名

wpscan --url http://dc-2/ -e u

![1660486385_62f902f17044eceb7e3b1.png!small?1660486386426](https://image.3001.net/images/20220814/1660486385_62f902f17044eceb7e3b1.png!small?1660486386426)

可以看到爆出来三个用户，admin、jerry、tom

创建一个username.txt文件，作为爆破的用户名

![1660486394_62f902fa98b36319fd868.png!small?1660486395002](https://image.3001.net/images/20220814/1660486394_62f902fa98b36319fd868.png!small?1660486395002)

使用cewl创建密码本

<https://www.freebuf.com/articles/network/190128.html>  

cewl http://dc-2/ -w dict.txt

![1660486400_62f90300172e16a828be4.png!small?1660486401793](https://image.3001.net/images/20220814/1660486400_62f90300172e16a828be4.png!small?1660486401793)

现在有了用户名和密码，剩下就是用wpscan的爆破命令爆破一下了

wpscan --url http://dc-2/ -U username.txt -P dict.txt

![1660486407_62f90307c451a5d6e6733.png!small?1660486408834](https://image.3001.net/images/20220814/1660486407_62f90307c451a5d6e6733.png!small?1660486408834)

![1660486428_62f9031c6031a1fa99657.png!small?1660486429249](https://image.3001.net/images/20220814/1660486428_62f9031c6031a1fa99657.png!small?1660486429249)

| Username: jerry, Password: adipiscing

| Username: tom, Password: parturient

成功了两个，登录一下

### Flag2:

| Username: jerry, Password: adipiscing

使用jerry这个账户登录进去之后，就可以找到flag2

![1660486436_62f9032455232ffe0bd1a.png!small?1660486436812](https://image.3001.net/images/20220814/1660486436_62f9032455232ffe0bd1a.png!small?1660486436812)

提示如果WordPress无法攻击成功的话，还有另外一种方法

之前我们进行nmap扫描的时候发现开启了一个ssh的7744端口，那么可以尝试看看是不是ssh可以尝试登陆

![1660486453_62f9033523d9bedfea170.png!small?1660486454884](https://image.3001.net/images/20220814/1660486453_62f9033523d9bedfea170.png!small?1660486454884)

### Flag3:

使用tom登陆之后就能看到flag3.txt，发现很多命令都无法使用，最后试了一下VI命令是可以查看的。

提示tom是一个低权限的用户，需要进行su提权

![1660486454_62f9033617f2483f08800.png!small?1660486454886](https://image.3001.net/images/20220814/1660486454_62f9033617f2483f08800.png!small?1660486454886)

![1660486459_62f9033be360c6e350818.png!small?1660486460310](https://image.3001.net/images/20220814/1660486459_62f9033be360c6e350818.png!small?1660486460310)

试了一下，发现可以用的就四个命令，因此只能用vi来查看，也没法cd，su命令也没法使用。

![1660486473_62f9034931f49914b2605.png!small?1660486480991](https://image.3001.net/images/20220814/1660486473_62f9034931f49914b2605.png!small?1660486480991)

百度了一下，可以 用rbash绕过，这个后面需要了解一下

BASH_CMDS[a]=/bin/sh;a # 把 /bin/bash 的值赋给 a

/bin/bash # 执行完上一个命令后立刻输入

export PATH=$PATH:/bin/ # 把 /bin 作为 PATH 环境变量导出

export PATH=$PATH:/usr/bin/ # 将 /usr/bin 作为环境变量导出

这个时候就可以使用cat命令了，其他相关的命令也可以使用了

![1660486480_62f9035006cb166cf513a.png!small?1660486486234](https://image.3001.net/images/20220814/1660486480_62f9035006cb166cf513a.png!small?1660486486234)

### Flag4:

可以使用su命令切换到jerry账户

![1660486485_62f90355a8d847330b46d.png!small?1660486486237](https://image.3001.net/images/20220814/1660486485_62f90355a8d847330b46d.png!small?1660486486237)

我们再找一下flag文件

find / -name flag4.txt

![1660486488_62f903585a02629571f9b.png!small?1660486489162](https://image.3001.net/images/20220814/1660486488_62f903585a02629571f9b.png!small?1660486489162)

可以看到再jerry的home目录下有个flag4.txt

![1660486496_62f90360b89956a91c8d1.png!small?1660486497322](https://image.3001.net/images/20220814/1660486496_62f90360b89956a91c8d1.png!small?1660486497322)

最后一行，有个git的提示，可能使用git命令进行提权的操作

### Flag5:

Jerry用户可以直接使用sudo命令，但是无法直接提升到root权限

![1660486502_62f903667c8825837c008.png!small?1660486503008](https://image.3001.net/images/20220814/1660486502_62f903667c8825837c008.png!small?1660486503008)

可以看到jerry可用的命令如下，没有find命令，也就没法通过DC1的使用find命令进行suid提权的方式了

![1660486511_62f9036fb23530875e89a.png!small?1660486512224](https://image.3001.net/images/20220814/1660486511_62f9036fb23530875e89a.png!small?1660486512224)

那么只能试一下git命令

![1660486514_62f903720ff2ed2032e97.png!small?1660486514607](https://image.3001.net/images/20220814/1660486514_62f903720ff2ed2032e97.png!small?1660486514607)

sudo git help config

!/bin/bash

![1660486519_62f90377f158dc962f75d.png!small?1660486520376](https://image.3001.net/images/20220814/1660486519_62f90377f158dc962f75d.png!small?1660486520376)

此时就已经切换到root权限了，使用find命令查找一下flag

![1660486522_62f9037a2a0c48013dde6.png!small?1660486522573](https://image.3001.net/images/20220814/1660486522_62f9037a2a0c48013dde6.png!small?1660486522573)

## 遗留问题：

  * wpscan命令的使用和cewl命令的使用？

这两个命令之间没有使用过，需要学习一下

  * rbash相关知识，rbash提权的使用？
  * git命令提权的相关知识？

  

