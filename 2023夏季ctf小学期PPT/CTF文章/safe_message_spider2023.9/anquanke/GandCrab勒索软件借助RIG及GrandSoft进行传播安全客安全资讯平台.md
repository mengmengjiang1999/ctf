# GandCrab勒索软件借助RIG及GrandSoft进行传播

阅读量 **254354**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-02-02 15:30:13

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Malwarebytes Labs，文章来源：blog.malwarebytes.com

原文地址：<https://blog.malwarebytes.com/threat-analysis/2018/01/gandcrab-ransomware-distributed-by-rig-and-grandsoft-exploit-kits/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01593e41e198e4daea.jpg)

## 一、前言

上周末时，我们发现GandCrab这款新型勒索软件开始粉墨登场。令人惊讶的是，这款恶意软件借助了两款漏洞利用工具包（exploit
kit）进行传播，这两款套件分别为RIG EK以及GrandSoft EK。

为什么这一点令人惊讶？与Magnitude EK不同的是（众所周知，Magnitude EK一直在传播[Magniber
](https://blog.malwarebytes.com/threat-analysis/2017/10/magniber-ransomware-exclusively-for-south-koreans/)勒索软件），今年来其他工具包释放的都是其他类型的载荷，比如Ramnit或者SmokeLoader，以及一些RAT或挖矿程序。

尽管在2017年最后一个季度中，勒索软件的增长幅度有所放缓，但这种安全威胁依然不容忽视，攻击者可以通过这种手段获得可观的收入。

## 二、传播渠道

GandCrab的首次活动时间可以追溯到1月26日，随后我们也可以在漏洞利用攻击活动中找到它的踪影。

###  2.1 RIG Exloit Kit

之前业界对Seamless
gate已经分析得较为透彻，但随后Seamless衍生出了许多分支，传播不同的载荷，以增加自身的多样性。虽然Seamless正在逐步切换到包含俄文字符的国际域名（[International
Domain Names](https://blog.malwarebytes.com/threat-analysis/2017/12/seamless-campaign-caught-using-punycode/)，IDN），但我们也发现了一条不同的攻击链，该攻击链使用的是标准的域名（备注：这条攻击链中同样也会重定向到Magnitude
exploit kit）。

此次攻击活动中，我们可以观察到恶意软件请求了一些常见的地址，这些地址包含我们已知的IP信息，但也用到了比较特殊的`gav[0-9].php`地址，该地址用来重定向至RIG
EK。

![](https://p1.ssl.qhimg.com/t01857adba6bfa0c2fe.png)

目前，攻击者只使用了[
_gav4.php_](https://twitter.com/nao_sec/status/956924254376812544)这个地址来传播这款勒索软件。

###  2.2 GrandSoft Exploit Kit

这款Exploit Kit年代已经比较久远，并不常见，人们曾经认为它已不再活跃。然而事实证明攻击者也用到了这款工具包来传播GandCrab。

![](https://p4.ssl.qhimg.com/t01c2b8722b51ef5575.png)

GrandSoft EK所用的下载页面并没有经过混淆处理，并且我们发现该工具包也用到了其他Exploit Kit中类似的功能。

## 三、整体情况

有趣的是，GrandCrab并没有要求受害者使用流行的Bitcoin货币来支付，而是用到了知名度较低的一款加密货币：Dash（达世币）。这表明攻击者追求的是在匿名性方面以及交易费方面比BTC更加优秀的加密货币。

![](https://p0.ssl.qhimg.com/t013d8777446b8e4741.png)

## 四、技术分析

从安全分析角度来看，解封装后的二进制程序非常简单，并没有混淆数据或代码，只对第一层封装器做了些处理。恶意软件在数据区中保存了各种明文，如不处理的文件类型、Web请求变量、URL地址、AV清单以及勒索信息等。只要稍作分析，你就有可能通过二进制文件中的字符串信息，推测出这款恶意软件的部分功能。

恶意软件的代码流内部关联度比较高，因此从逆向分析工程角度来看，即使只用反汇编器来静态分析这个样本，我们也能得到比较准确的分析结果。程序代码可以分成3个主要部分：
**初始化部分（initialization）** 、 **网络部分（network）** 以及 **加密部分（encryption）** 。

###  4.1 初始化

解封装之后，GranCrab首先会执行一些函数，这些函数的功能是收集一些信息，以便后续使用。恶意软件会查询与用户有关的信息，如：

  * 用户名
  * 键盘类型
  * 主机名
  * 反病毒软件情况
  * 处理器类型
  * IP地址 操作系统版本
  * 磁盘空间情况
  * 系统语言
  * 活动的驱动器
  * 区域化设置信息
  * 当前Windows版本
  * 处理器架构

恶意软件会特意去检查键盘布局是否采用俄语布局，使用某个整数来表明键盘类型，通过某个字符串来收集这个信息。恶意软件使用某些变量名来记录收集到的信息，如下所示：

![](https://p4.ssl.qhimg.com/t018d0c9354df244973.png)

随后，恶意软件通过字母表来遍历所有盘符，查询哪些驱动器存在，判断这些驱动器的具体类型。如果该驱动器为CDRom、未知驱动器或者不存在的驱动器，则会被恶意软件跳过。如果恶意软件找到一个固定驱动器，则会将驱动器的名字复制到某个缓冲区中，使用某个字符串来表示驱动器的类型。比如，`C:`盘对应的是`FIXED`。

然后恶意软件会收集可用磁盘空间及扇区信息，通过`printf`函数将其转换为一串数字，如`C:FIXED_64317550592`。遍历完所有驱动器后，恶意软件会得到一份磁盘清单。

随后，恶意软件将收集到的所有信息汇总在一起，并在某个时刻使用GET请求将这些信息发往C2服务器。系统信息所对应的请求格式如下所示：

    
    
    ip=99.8.160.100&pc_user=virusLab&pc_name=VI
    

恶意软件也会搜索正在运行的进程，检查其中是否存在某些反病毒程序，这些信息经过处理后也会发给C2服务器。

![](https://p5.ssl.qhimg.com/t01a1de1fdf7e064c12.png)

接下来，恶意软件利用收集到的一些系统信息以及生成的ID来创建互斥量（mutex），如下所示：

    
    
    Globalpc_group=WORKGROUP&ransom_id=c9ed65de824663f
    

![](https://p4.ssl.qhimg.com/t013ee2f7d4184e4648.png)

为了后续加密过程能顺利进行，恶意软件会遍历内置的一份进程列表，结束该列表中存在的进程。对勒索软件而言，这是一种常用的技术，可以终止某些进程，避免某些文件被锁住而无法加密。

![](https://p5.ssl.qhimg.com/t01400a3823b71a50ed.png)

需要终止的进程如下：

    
    
    msftesql.exe
    sqlagent.exe
    sqlbrowser.exe
    sqlservr.exe
    sqlwriter.exe
    oracle.exe
    ocssd.exe
    dbsnmp.exe
    synctime.exe
    mydesktopqos.exe
    agntsvc.exe
    isqlplussvc.exe
    xfssvccon.exe
    mydesktopservice.exe
    ocautoupds.exe
    agntsvc.exe
    agntsvc.exe
    agntsvc.exe
    encsvc.exe
    firefoxconfig.exe
    tbirdconfig.exe
    ocomm.exe
    mysqld.exe
    mysqld-nt.exe
    mysqld-opt.exe
    dbeng50.exe
    sqbcoreservice.exe
    excel.exe
    infopath.exe
    msaccess.exe
    mspub.exe
    onenote.exe
    outlook.exe
    powerpnt.exe
    steam.exe
    thebat.exe
    thebat64.exe
    thunderbird.exe
    visio.exe
    winword.exe
    wordpad.exe
    

接下来，恶意软件会调用内置的加密函数来生成密钥。GandCrab会在客户端生成公钥及私钥，然后通过`Advapi32.dll`中的API调用来使用标准的微软加密程序库。恶意软件使用RSA算法来调用`CryptGenKey`函数。

![](https://p1.ssl.qhimg.com/t01aee4b86d17a412ee.png)

###  4.2 网络行为

现在，勒索软件会进入主循环，处理互联网相关功能。这部分代码中，如果执行成功，则会进入加密部分代码，否则，恶意软件会不断循环，直至成功为止。如果一直不能成功执行，则恶意软件永远不会加密任何文件。

在这部分代码中，恶意软件首先向 _ipv4bot.whatismyipaddress.com_
发起GET请求，查询本机的IP地址，然后将其添加到系统信息中，通过GET请求发给服务器。

![](https://p5.ssl.qhimg.com/t01b40deda6f02cacf9.png)

随后，恶意软件开始处理一段二进制数据，这段数据为初始化过程中生成的RSA公钥。恶意软件通过 _CryptBinaryToStringA_
API，传入CRYPT_STRING_NOCRLF以及CRYPT_STRING_BASE64参数，将公钥转换为base64编码，并将编码结果加入GET请求字符串中。RSA密钥的生成及转化过程如下。

使用加密API生成的RSA公钥如下：

    
    
    A7 EC BD E2 49 43 E1 11 DA 12 10 E0 25 59 AA 83 77 35 FC 3E 49 C8 3B 6C 3D 91 CF FF 96 6E D8 45 FE 8A 58 20 E6 CB 91 AB 99 6A E2 04 EC 58 66 95 05 8C 2F 7E C6 19 6D 24 B5 5F C4 9A 01 3D 3B FB 31 4E AC 25 07 8C 0E 6C 57 4C C0 23 24 3A EB 57 97 17 79 F8 62 73 6B AD B2 09 60 BB B7 9A CF F9 5B 68 B8 C1 44 07 F5 5E 3E 06 FE C2 35 CF 99 82 29 28 37 1B E6 51 29 6C 0B 87 89 F9 90 26 F7 CC DA 75 C4 46 A1 E3 30 09 C0 6A CB 5E CB 87 8E 40 EF 4C 7E 02 AE E8 06 6A D7 24 FC 0E 40 EA 69 CD 6D 8D 24 92 6E 53 2F D2 69 D2 A2 F3 97 54 63 EB D9 C7 BD 9E 41 19 91 F1 6B D6 CA AD 9E 0E D3 0B A0 53 50 84 87 6D 49 4C 49 D2 3B 8E 80 F7 7F 35 F1 D7 A7 81 0F 90 04 40 AC 4B 7C ED 37 71 8A B1 FA 84 33 33 FB 62 EE 04 A3 C7 9A 47 2C 64 64 95 3D 34 A5 CC 12 6E E4 81 40 E6 7F 03 02 C4 57 D6
    

转化为base64编码为：

    
    
    BgIAAACkAABSU0ExAAgAAAEAAQCn7L3iSUPhEdoSEOAlWaqDdzX8PknIO2w9kc//lm7YRf6KWCDmy5GrmWriBOxYZpUFjC9+xhltJLVfxJoBPTv7MU6sJQeMDmxXTMAjJDrrV5cXefhic2utsglgu7eaz/lbaLjBRAf1Xj4G/sI1z5mCKSg3G+ZRKWwLh4n5kCb3zNp1xEah4zAJwGrLXsuHjkDvTH4CrugGatck/A5A6mnNbY0kkm5TL9Jp0qLzl1Rj69nHvZ5BGZHxa9bKrZ4O0wugU1CEh21JTEnSO46A93818dengQ+QBECsS3ztN3GKsfqEMzP7Yu4Eo8eaRyxkZJU9NKXMEm7kgUDmfwMCxFfW
    

加密密钥与之前收集到的系统所有信息合在一起，通过GET请求字符串发往C2服务器，请求字符串如下所示：

    
    
    action=call&ip=99.8.160.100&pc_user=virusLab&pc_name=VIRUSLAB-PC&pc_group=WORKGROUP&pc_lang=en-US&pc_keyb=0&os_major=Windows 7 Enterprise&os_bit=x64&ransom_id=c9ed65de824663fc&hdd=C:FIXED_64317550592/50065174528&pub_key=BgIAAACkAABSU0ExAAgAAAEAAQCn7L3iSUPhEdoSEOAlWaqDdzX8PknIO2w9kc//lm7YRf6KWCDmy5GrmWriBOxYZpUFjC9+xhltJLVfxJoBPTv7MU6sJQeMDmxXTMAjJDrrV5cXefhic2utsglgu7eaz/lbaLjBRAf1Xj4G/sI1z5mCKSg3G+ZRKWwLh4n5kCb3zNp1xEah4zAJwGrLXsuHjkDvTH4CrugGatck/A5A6mnNbY0kkm5TL9Jp0qLzl1Rj69nHvZ5BGZHxa9bKrZ4O0wugU1CEh21JTEnSO46A93818dengQ+QBECsS3ztN3GKsfqEMzP7Yu4Eo8eaRyxkZJU9NKXMEm7kgUDmfwMCxFfW
     &priv_key=BwIAAACkAABSU0EyAAgAAAEAAQCn7L3iSUPhEdoSEOAlWaqDdzX8PknIO2w9kc//lm7YRf6KWCDmy5GrmWriBOxYZpUFjC9+xhltJLVfxJoBPTv7MU6sJQeMDmxXTMAjJDrrV5cXefhic2utsglgu7eaz/lbaLjBRAf1Xj4G/sI1z5mCKSg3G+ZRKWwLh4n5kCb3zNp1xEah4zAJwGrLXsuHjkDvTH4CrugGatck/A5A6mnNbY0kkm5TL9Jp0qLzl1Rj69nHvZ5BGZHxa9bKrZ4O0wugU1CEh21JTEnSO46A93818dengQ+QBECsS3ztN3GKsfqEMzP7Yu4Eo8eaRyxkZJU9NKXMEm7kgUDmfwMCxFfWGRZmQmHH5W5K1RYgSg8VJEFLebRW8+o7X0K30wzzrw5NHpJpVJYX8OKot8KvopS4wsZzuxu5YJih1ZYVgF6QT5FW4WEG3BzMtq5vGVqTmrlckudC0xfGlGb7J41vUkZsp6S07NTIIT7HtYJSA/pxS51Zg+13TfU0nxC92RkKuva/8Dzmgssm6uE7aYJQFEkUmkPImYreHGIPsffEEGtZM9zwz4tXbrXLch0BoRNHeR+GFLJclnLc5JMg/J4BLaS6js+RGxRbZGMPJDVX6lTEEl+aIYO38Wh49+Zcpzs4EOUfb1EsoLEDAZbppIWq8Yr1P6KtWkqIXRzjUk9HXiJm3qHm0u0vchV4iRAKz2MJ/xZdYjHp+C3qMTTsNbQbtcscpy13/rEv8oO6clfciSCPcthy5IkLFLKZQP5be+IcsAjxeSoOqqtEpNpj8nOKfZ5PvEs+/kn718vG0R5CMU4I0fyF0BD68AFat6dl5gHK1sKs0ndAvCKdDMg/HqO/JKUZRSza2VKkgxpXC57BRGNP0r/jYySGnqhE2owHQaXoEmP9tme1A8PHsAoNtUEd0SO4/pn4hDg70o/Nmph/UWqtOq9nSlrxQMD8Q08w4K2H1CC3eCAnHZOM8PTCDYH3nh6f/ftkVtyrpudTpicTjoUSEkwtEPRsWk7ff3F/Na8D2FcXSI5xQ6R+R2uy8GvVoxpBy8Xdh78VqViOBlu5+Jxp09PMQmI2EFususg4VJeH047Wayi2r+VemzAX1rTuMh2mRKfKa+eae+YBKjBUkIh9WPCmFjO+3lll7GqV7P4JFm1g2sjrm/dPWnoGzfg1E7brER6aD2q+w1+4o8wCzNTNvPH2bwPMyV6R+vbWOVZUTprzZ4sRr7KxT0ucZmNA76WX39NegSU56tOngYpAQprOMrJP0NYmrizT8FsCOcqlUGk0jf6moarJSWQxh2MxXtlpFAvJjPTqqKruIVMhIkTJ9aZHKnn02a5PIdLcs4a09D85js9klKZn90Gj6C4AxlT2nI/ba9mEx+7srvxxbh1XNgI987IWLsLYpWxHlRptJqIvI0ZAA3EuvwZuZ8f6sqLM2/rSxdOnFW5hd8am9zgopimktfkjFtsHpev/Svf0VlxQ3Fj22A06aXqfi7hmWPZ8ZCtZ874PUHgbrG3foNESQiTghT2NLV9rNNad7ij/kVA=
     &version=1.0
    

密钥转化为base64编码的函数段如下：

![](https://p4.ssl.qhimg.com/t0188a0a54a03b3f61a.png)

将编码后的密钥添加到请求字符串中（私钥存放于`priv_key`参数中）：

![](https://p4.ssl.qhimg.com/t0102f71a6dff082eeb.png)

此时，我们已经清楚恶意软件会将哪些信息发往C2服务器。这些信息非常有趣，因为我们有可能从内存中提取出加密密钥，然后使用这些密钥来解密文件。我们会继续调查，如果有新发现会及时更新分析文章。

GandCrab的服务器托管在`.bit`域名上，因此恶意软件必须查询支持该TLD的域名服务器，恶意软件采用如下命令来查询相关域名：

    
    
    nslookup [insert domain]  a.dnspod.com.
    

这条命令会查询`a.dnspod.com`域名服务器，该服务器支持以下`.bit`类型的TLD：

    
    
    bleepingcomputer.bit
    nomoreransom.bit
    esetnod32.bit
    emsisoft.bit
    gandcrab.bit
    

恶意软件创建管道，通过该管道打开`NSlookup`子进程。这样一来，子进程就可以直接影响父进程的内存，无需手动传输输出结果。这是一种比较有趣又实用的技术，相关代码如下所示：

![](https://p2.ssl.qhimg.com/t0108b662879806de5e.png)

准备就绪后，恶意软件尝试向服务器发送数据，如果出现错误或者服务器不可达，则会在无限循环中继续执行该过程，直到找到可用的服务器为止，然后重新查询客户端IP，再次运行`nslookup`，解析IP地址。除非恶意软件与服务器建立连接，否则它将继续运行，直至进程被手动结束为止。

![](https://p2.ssl.qhimg.com/t017860743322007922.png)

前面我们提到过，除非恶意软件找到可用的服务器，才会进入加密过程，也就是说恶意软件会进入一个死循环中，查询IP地址：

![](https://p1.ssl.qhimg.com/t018c8b3f53257e491c.png)

找到可用地址后，恶意软件继续打开一个线程，启动主加密流程。然而，在执行加密过程之前，恶意软件会打开另一个线程，创建一个窗口，将其标记为Firefox。窗口加载时，会将自身拷贝至`temp`目录中，并在注册表中建立相应键值。这也是这款恶意软件为数不多的没有直接用明文表示的动作之一。恶意软件调用
_cryptGenRandom_ 函数，将输出结果应用在一组字符串上，从而随机生成复制文件的文件名。

以上功能有点奇怪，虽然恶意软件会通过上述流程实现本地持久化目的，但同时也会第一时间创建一个窗口。从我们的角度来看，创建窗口对其本身任务而言没有任何好处。作者这么做可能只是想实验一下，真实的意图我们仍然不得而知。

![](https://p1.ssl.qhimg.com/t0181a5cad945a6d1f3.png)

###  4.3 加密行为

如前文所述，恶意软件所使用的加密算法为RSA算法。在进入加密流程之前，恶意软件首先确保自己没有加密特定类型的文件，这些文件类型已硬编码到恶意软件中，如下所示：

    
    
    desktop.ini
    autorun.inf
    ntuser.dat
    iconcache.db
    bootsect.bak
    boot.ini
    ntuser.dat
    thumbs.db
    GDCB-DECRYPT.txt
    .sql
    

如果恶意软件发现目标文件名在该列表中出现，则会跳过此文件，继续处理下一个文件。与此同时，如果待处理的目录属于如下几个关键目录，也会被恶意软件跳过：

    
    
    local app data
    windows
    programfiles
    program data
    ransomware
    localsettings
    

通过这些检查过程后，恶意软件会对文件扩展名做最后一次检查，检查该类型的文件是否可以加密处理，可以处理的扩展名如下：

![](https://p3.ssl.qhimg.com/t01905e8fcf4c6a4b86.png)

如果所有检查过程都通过，恶意软件会使用之前生成的密钥，配合盐（salt）以及生成的随机数来加密文件，并将文件重命名为`.GDCB`类型。循环加密过程是一个递归函数，可以处理磁盘上的所有文件。

![](https://p3.ssl.qhimg.com/t01ca72b4ab53fb891a.png)

![](https://p5.ssl.qhimg.com/t01ba39cd804239960f.png)

![](https://p5.ssl.qhimg.com/t019e6b8ced91b77086.png)

## 五、防护手段

借助漏洞利用防护功能，Malwarebytes能够保护客户免于感染这款恶意软件，由于采用了强大的反勒索软件引擎，客户能够防范于未然，在看到恶意软件之前就能主动阻止其攻击活动。

## 六、总结

在当前活跃的攻击活动中看到新型勒索软件的踪影是非常有趣的一件事情，此外，更有趣的是有两款不同的漏洞利用工具包在传播这款软件。我们不知道这两种攻击活动背后的主使者是否为同一波人，正在尝试使用不同的传播渠道来发起攻击。

## 七、IoC

Seamless gate

    
    
    31.31.196.187,xn--80abmi5aecft.xn--p1acf
    

GrandSoft EK（IP）

    
    
    62.109.4.135
    

GandCrab（封装形态）

    
    
    69f55139df165bea1fcada0b0174d01240bc40bc21aac4b42992f2e0a0c2ea1d
    

GandCrab（解封装形态）

    
    
    ab0819ae61ecbaa87d893aa239dc82d971cfcce2d44b5bebb4c45e66bb32ec51

本文翻译自blog.malwarebytes.com [原文链接](https://blog.malwarebytes.com/threat-analysis/2018/01/gandcrab-ransomware-distributed-by-rig-and-grandsoft-exploit-kits/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/97243](/post/id/97243)

安全客 - 有思想的安全新媒体

本文转载自: [blog.malwarebytes.com](https://blog.malwarebytes.com/threat-analysis/2018/01/gandcrab-ransomware-distributed-by-rig-and-grandsoft-exploit-kits/)

如若转载,请注明出处： <https://blog.malwarebytes.com/threat-analysis/2018/01/gandcrab-ransomware-distributed-by-rig-and-grandsoft-exploit-kits/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [勒索软件](/tag/勒索软件)
  * [GandCrab](/tag/GandCrab)
  * [RIG](/tag/RIG)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

