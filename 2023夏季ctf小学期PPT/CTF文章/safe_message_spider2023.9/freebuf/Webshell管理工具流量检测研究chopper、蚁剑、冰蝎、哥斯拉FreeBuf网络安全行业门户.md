## **引言**

俗话说得好，80后用菜刀，90后用蚁剑，95后用冰蝎和哥斯拉。
**本文主要是对这四个主流的并具有跨时代意义的webshell管理工具进行流量分析和检测。**

注：本文均以phpshell连接为例进行研究分析，毕竟“php是世界上最好的语言”。

##  **1、 中国菜刀（chopper）**

中国菜刀是一款专业的网站管理软件，用途广泛，使用方便，小巧实用。只要支持动态脚本的网站，都可以用中国菜刀来进行管理。主流有2011版本，2014版本和2016版本。2011和2014版本：![](https://image.3001.net/images/20220310/1646905495_6229c897ddd83ccb4eb97.png!small)![](https://image.3001.net/images/20220310/1646905508_6229c8a444b658c3b3ee9.png!small)
**特征：**

a（密码）参数：值为执行的函数加上对pyload的base64解

Z0参数：base64加密的payload,

Z1参数：shell存在的位置

 **识别：**

(1)执行函数：@eval,@assert 等；

(2)base64_decode($_POST[Z0]),$_GET,$_REQUEST

(3)截取参数z0,进行base64_decode后 ,

@ini_set("display_errors","0");@set_time_limit(0);@set_magic_quotes_runtime(0)等

2016版本：![](https://image.3001.net/images/20220310/1646905527_6229c8b7b9e596da55331.png!small)较于早版本做了一些混淆识别"ass"."ert"
"ev"."Al "Ba"."SE6"."4_dEc"."OdE

##  **2、蚁剑4.0.3**

中国蚁剑是一款开源的跨平台网站管理工具，它主要面向于合法授权的渗透测试安全人员以及进行常规操作的网站管理员。是一款非常优秀的webshell管理工具。开发版本针对有一定编程基础的开发者，你可以根据阅读文档或者分析源码了解熟悉整个应用的执行流程，然后便可随意对代码进行修改增强个性化自定义，真正打造出属于自己的一把宝剑！PHP
WEBSHELL基本操作连接所发的包如下：![](https://image.3001.net/images/20220310/1646905573_6229c8e557aaa237f86a8.png!small)传输的内容为：![](https://image.3001.net/images/20220310/1646905597_6229c8fd23f4baba2556f.png!small)主要获取了服务端当前目录、根目录、系统和当前用户名等信息，输入到缓冲区再由$output变量接收，通过随机字符作为开始结束符定位变量输出位置。默认使用的情况下data仅进行url编码，特征很明显，data中含有@ini_set("display_errors",
"0");@set_time_limit(0);
header中含有antSword字眼，由于蚁剑的源码是和菜刀的一样，所以在默认情况下特征十分明显。但是蚁剑的个性化十分的明显，可以对其进行改造。PHP
WEBSHELL基本操作连接所发的包如下：

###  **2.1 自带的编码器和解码器**

自带的编码器和解码器，编码器的作用是传输的时候加密，解码器的作用是使返回的包带的值也是加密的![](https://image.3001.net/images/20220310/1646905628_6229c91c132cb412a5dde.png!small)![](https://image.3001.net/images/20220310/1646905639_6229c927896d72d3f42c0.png!small)自带编码器发出的包：格式为：pwd=编码方式['xxx']&xxx=内容![](https://image.3001.net/images/20220310/1646905651_6229c933c9705048e59ac.png!small)![](https://image.3001.net/images/20220310/1646905662_6229c93ea2faf2737c545.png!small)至此我们可以分析常规拦截：（1）检测流量包中的编码方式（2）检测必须传输的内容，比如：@ini_set等字眼，不仅是明文，这些字眼的各种编码形式也可以拦。编码识别：只要原始数据不变，编码都是固定的映射，例如只检查ini_set("display_errors",
"0") ，aW5pX3NldCgiZGlzcGxheV9lcnJvcnMiLCAiMCIp（base64）
，vav_frg("qvfcynl_reebef", "0") (rot13)
…![](https://image.3001.net/images/20220310/1646905683_6229c953723bdceb5f77f.png!small)（3）蚁剑自带的header

针对以上明显特征，蚁剑有自定义编码器，自定义header,自定义分隔符……修改明显特征以绕过检测

###  **2.2 自定义header**

建议直接在文件modules/request.js中修改相应的参数值，将其修改成常用的useragent,项目路径下的.modules/update.js也需要修改。也可以在每次连接时添加自定义header头。![](https://image.3001.net/images/20220310/1646905708_6229c96c09eaa6c36eecc.png!small)

###  **2.3 自定义编码**

https://github.com/AntSwordProject/AwesomeEncoder/tree/master/php在自定义编码器中可以将加密的函数名隐去，分区传递，加入干扰字符等。（1）自定义的base64编码：![](https://image.3001.net/images/20220310/1646905732_6229c9843c45be05799ec.png!small)![](https://image.3001.net/images/20220310/1646905757_6229c99db01c602e6a220.png!small)在编码的同时也可以改变包的格式，使用multipart发包进行混淆，很多waf出于对业务性能影响，一般会把
multipart/form-data
这种多用来上传文件的传输方式检测关闭掉。不然攻击者一直给你发大文件，一直损耗WAF的性能，拖垮业务。也可以使用分块传输。![](https://image.3001.net/images/20220310/1646905794_6229c9c29c317c1f3514a.png!small)可以注意到，很多简单的编码器他的参数都是_0x.....=加密字符串，可以作为一个弱特征检测。（2）自定义hex:![](https://image.3001.net/images/20220310/1646905811_6229c9d3d66dcc2995912.png!small)检测识别xxx=
40696e695f7365742822646973706c61795f6572726f7273222c2022302229或者更短。（3）rsa静态密钥（仅支持php）：![](https://image.3001.net/images/20220310/1646905857_6229ca0131973bf9e82b3.png!small)![](https://image.3001.net/images/20220310/1646905870_6229ca0e046f040cad2a4.png!small)![](https://image.3001.net/images/20220310/1646905881_6229ca196afcdca8855b5.png!small)分区块加密，并且会有分隔符，每个区块的长度一致，RSA是分组加密算法，分组大小可以根据密钥的大小而改变，然而密钥是蚁剑自动生成的，所以每区块长度一定是172字节，也就是之前的80字符base64加密的长度。且生成的密钥是有很大的相似性的，也可以加强对shell的检测。![](https://image.3001.net/images/20220310/1646905933_6229ca4d1d492fbb62e53.png!small)但这也是弱特征，这样的加密数据包已经是没法解密了，那我们来看一下执行命令：![](https://image.3001.net/images/20220310/1646905949_6229ca5d1165aa7e7eaba.png!small)![](https://image.3001.net/images/20220310/1646905965_6229ca6d3aed9d39ec9fd.png!small)执行命令的时候会多几个参数，且这几个参数的值仅仅是通过base加密的，一个是执行方式：cmd，一个是执行的命令：whoami，在\source\core\base.js中有对这串字符的加密，这个是蚁剑把命令独立于php语句传输。![](https://image.3001.net/images/20220310/1646905979_6229ca7bee80244b6f285.png!small)处理方法：①可在编码器中通过遍历将每个参数进行加密，也可在每个参数中加入混淆的字符串，在接收处理的时候删除即可,参考方法：http://www.feidao.site/wordpress/?p=4495#1webshell。②在该处编写自己的加密方法，然后将\source\core\php\template文件夹内的js文件做对应修改

（4）AES动态密钥：

要求站点支持openssl,默认是不开启的。密钥可以访问网站时截取session或者截取其他的进行加密，做到动态key。当然，拦截的waf也可以学习这个方法，最后密钥都是自己添加成硬编码也不是不可。![](https://image.3001.net/images/20220310/1646905999_6229ca8f57887a56a302f.png!small)![](https://image.3001.net/images/20220310/1646906009_6229ca99b5c7ef5bfc5ac.png!small)![](https://image.3001.net/images/20220310/1646906020_6229caa4211ef32e1b926.png!small)AES加密后流量包基本就不能够检测出来了，执行其他命令时也需同上述操作一样，遍历将其他参数进行加密，但多次请求同一个包且参数相同参数值开头相同也能够算是一个弱特征。

（5）请求包成功加密，很多waf会选择连接返回包，返回包是明文的，包含了很多关键字，例如[s][E]或者是其他敏感的词汇,所以解码器也随之出现,解码器和之前的加密方式以及防范方式多很相似，就不一一赘述了。

![](https://image.3001.net/images/20220310/1646906037_6229cab5d9351bcc8bcd6.png!small)

###  **2.4 蚁剑市场自带的插件**

蚁剑的市场中也有很多一键绕过的插件，这里就不再进行研究。

##  **3、 冰蝎3.0 Beta 9**

冰蝎3.0
和v2.1相比，最重要的变化就是“去除动态密钥协商机制，采用预共享密钥，全程无明文交互，密钥格式为md5("admin")[0:16]；冰蝎的默认密钥为“e45e329feb5d925b”，正常连接发包如下（连接为两个流量包，全文加密）：

![](https://image.3001.net/images/20220310/1646906090_6229caea091c7420c4728.png!small)明文：

![](https://image.3001.net/images/20220310/1646906104_6229caf8e92c92d044daa.png!small)![](https://image.3001.net/images/20220310/1646906117_6229cb056b0b0f85696f8.png!small)明文：

![](https://image.3001.net/images/20220310/1646906131_6229cb13666bc7626a769.png!small)

密文的加密方式为先将传递数据base64加密，再将其进行AES加密，由于新版本中取消了动态密钥交互过程，加密的密钥被写死在shell中，如果是不改密码直接使用默认的shell,检测是可以进行解密检测敏感字符的，比如：error_reporting(0)
，phpinfo()等。![](https://image.3001.net/images/20220310/1646906148_6229cb24eab6df754a528.png!small)如果密码交互失败，冰蝎会进行常规密钥交互阶段，而且由于密码错误，shell中获取内容失败，会爆出目录文件错误提示。  
![](https://image.3001.net/images/20220310/1646906163_6229cb3383eb5965bc877.png!small)![](https://image.3001.net/images/20220310/1646906201_6229cb59c65c23594ec2a.png!small)如果攻击者改了密码，密文便无法监测，可以从header头入手，首先是user-agent，内置的25个ua请求头，不自定义的话太老，可以在其源码constants.class中自行更改。  
![](https://image.3001.net/images/20220310/1646906214_6229cb6697c40c34fe215.png!small)![](https://image.3001.net/images/20220310/1646906225_6229cb711f3e825d2ab52.png!small)初始化的Accept,Accept-Language,Content-type这三个的值也是一个固定值，且Content-type为小写t,这也可以作为一个监测点。具体值如下：

> "Accept",
> "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9"
>
> "Accept-Language", "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
>
> "Content-type", "application/x-www-form-urlencoded"
>
> 或者
>
> "Accept",
> "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
>
> "Accept-Language", "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-> US;q=0.3,en;q=0.2"
>
> "Content-type", "application/x-www-form-urlencoded"

![](https://image.3001.net/images/20220310/1646906258_6229cb92b2b2d6c9d01ef.png!small)其次为referer:连接的两个包referer中的文件名都是随机生成的，但文件名是纯大写或者是纯小写，可作为一个弱特征检测。  
![](https://image.3001.net/images/20220310/1646906294_6229cbb62faa21b923d24.png!small)![](https://image.3001.net/images/20220310/1646906271_6229cb9fe98dee939e545.png!small)![](https://image.3001.net/images/20220310/1646906350_6229cbee2f741c898e1f0.png!small)Cookie:冰蝎的机制是需要从set-cookie中去取值，所以在发包中即使是有了cookie，他的接收包中都会有setcookie,除去第一个包没有。  
![](https://image.3001.net/images/20220310/1646906368_6229cc00adffdb8c26c1f.png!small)经测试可以发现在点击虚拟终端时会连续发17个包，发包长度不一样但是这17个包的接收长度一模一样。拦截大量发包。  
![](https://image.3001.net/images/20220310/1646906381_6229cc0dc346ce6b4da3a.png!small)连接成功后不操作，冰蝎会每5-8分钟（大概率是5分钟）发一个测试包是否存活。  
![](https://image.3001.net/images/20220310/1646906396_6229cc1cb2ad98ea4b52d.png!small)在连接时冰蝎发的两个包，尽管现在较于2.0修改了length,但是在接收包中可以看到，第一个连接包是比较小的，控制在5000以下，后一个包大概是在17W或者18W左右，原因是因为后一个包会加载phpinfo()等界面内容作为主页，导致返回的长度很长。  
![](https://image.3001.net/images/20220310/1646906409_6229cc29482035950045c.png!small)

##  **4、 哥斯拉v4.0.1**

哥斯拉号称全部类型的shell均可绕过市面所有静态查杀、流量加密可绕过市面全部WAF，且自带众多插件。支持对载荷进行AES等各种加密，支持自定义Http头，支持内存shell，提供丰富的Webshell功能。
哥斯拉客户端运行在Java平台上，通过调用Java库产生TLS流量。哥斯拉生成phpshell文件,存在默认密码和密钥:![](https://image.3001.net/images/20220310/1646906432_6229cc402bfa89bcb7722.png!small)  
phpshell有三种编码方式：  
![](https://image.3001.net/images/20220310/1646906446_6229cc4e657a03627e51a.png!small)EVAL_XOR_BASE64编码连接特征很明显，经过url解码后，pass=eval(base64_decode...
拦截明显的木马特征即可。  
![](https://image.3001.net/images/20220310/1646906462_6229cc5e1aa81d7c152ec.png!small)XOR_BASE64编码方式第一个包形式为pass=加密数据，无法检测:(XOR_RAW与其类似，不再单独分析)  
![](https://image.3001.net/images/20220310/1646906477_6229cc6d1e308c449d09e.png!small)经分析，哥斯拉连接时会有一个握手机制。其内容是固定的（加密前），响应也是固定的（加密前）。且加密中未填充随机长度字符。故在默认密码和密钥的情况下，内容固定，可以检测该握手机制包中的请求体和响应体：DlMRWA1cL1gOVDc2MjRhRwZFEQ%3D%3D11cd6a8758984163fL1tMGI4YTljO/79NDQm7r9PZzBiOA==6c37ac826a2a04bc注：密钥改变，base加密字符串改变，密码改变，md5加密字符串改变。如果密码和密钥不是默认，可以检测响应体的长度以及构成要素：前后为16位md5值，中间为32位加密字符串。![](https://image.3001.net/images/20220310/1646906494_6229cc7e638edb88ba975.png!small)  
哥斯拉页面配置中header中有三个固定值，user-agent,accept,accept-language。该弱特征也可作为检测。![](https://image.3001.net/images/20220310/1646906506_6229cc8a633bf7e002294.png!small)  
  
[原文链接](https://mp.weixin.qq.com/s?__biz=MzAwNTAxMjUwNw==&mid=2650269176&idx=1&sn=f6655fb7a1045dae66469993a537613f&chksm=8320688cb457e19a061bba2e95f97c0b9a6749258441171da0c4e4971169a52a4ff9ea470d27&token=152334928&lang=zh_CN#rd)

