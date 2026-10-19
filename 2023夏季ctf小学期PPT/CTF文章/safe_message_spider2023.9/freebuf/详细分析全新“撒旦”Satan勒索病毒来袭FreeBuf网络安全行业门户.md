**近日，瑞星威胁情报平台发现多起国内用户感染“撒旦”Satan勒索病毒事件。据瑞星安全研究人员介绍，该病毒运行后会加密受害者计算机文件，加密完成后会用中英韩三国语言索取1个比特币作为赎金，并威胁三天内不支付将不予解密。与以往常见的勒索病毒不同，“撒旦”不仅会对感染病毒的电脑下手，同时病毒还会利用多个漏洞继续攻击其它电脑。**

![image001.png](https://image.3001.net/images/20180720/15320541214800.png!small)

图：感染“撒旦”病毒后弹出的勒索窗口

瑞星安全研究人员对最新版本的“撒旦”Satan勒索病毒进行了分析，发现该病毒与以往勒索病毒有较大的不同，“撒旦”Satan勒索病毒不仅使用永恒之蓝漏洞攻击，还增加了其它的漏洞攻击。包括文件上传漏洞、tomcat弱口令漏洞、WebLogic
WLS组件漏洞、JBOOS 反序列化漏洞等。

虽然永恒之蓝已经过去很久，但是国内很多用户出于各种原因依然没有打补丁，这导致很多企业存在极大的安全隐患。“撒旦”Satan勒索病毒可通过漏洞进行传播，所以不下载可疑程序并不能防止感染病毒，如果不打补丁，即使没有任何操作只要联网就有可能被攻击，因此及时更新补丁，排查web漏洞，提高服务器安全才能最大限度的防御此类病毒。

###  **防范措施**

> Ø 更新永恒之蓝漏洞补丁。
>
> Ø 及时更新web漏洞补丁，升级web组件。
>
> Ø 开启防火墙关闭445端口。
>
> Ø 安装杀毒软件保持监控开启。
>
> Ø 安装瑞星之剑勒索防御软件。

由于“撒旦”Satan勒索病毒使用对称加密算法加密，密钥硬编码在病毒程序和被加密文件中，因此可以解密。目前，瑞星已经开发出了解密工具，如果用户中了此病毒可下载此工具恢复被加密文件，下载地址：

<http://download.rising.com.cn/for_down/satan/Satan3.x_Encrypt.exe>。

###  **解密工具使用方法**

1、查看勒索信息是否和报告中的相同；

2、判断被加密文件名是否为[dbger@protonmail.com]+原始文件名+.dbger，或者[satan_pro@mail.ru]+原始文件名+.satan；

3、运行解密工具；

4、点击“文件”按钮选中要解密的文件夹；

![image005.png](https://image.3001.net/images/20180720/15320542327520.png!small)

5、点击“解密”后，被加密文件将会被解密；

![image007.png](https://image.3001.net/images/20180720/15320542559831.png!small)

可以看到同目录下生成了被解密的文件，但是加密的文件将会被保留，用户查看确定文件被完全解密后，可删除被加密文件。在不确定解密文件是否正确的情况下，不要轻易删除被加密文件，防止其它类型病毒变种加密的文件没有被解密。

![image009.png](https://image.3001.net/images/20180720/15320542865530.png!small)

![image011.png](https://image.3001.net/images/20180720/15320543029693.png!small)

6、目前最新版本可以解密，如遇到此病毒的其它变种无法解密，可联系瑞星公司。

##  **病毒详细分析**

病毒攻击流程如下：

![image013.png](https://image.3001.net/images/20180720/15320543255449.png!small)

图：病毒攻击流程

新版撒旦Satan勒索病毒运行后会创建一个互斥体“SATAN_SCAN_APP”，如果已经存在则退出。

![image015.png](https://image.3001.net/images/20180720/1532054343362.png!small)

图：创建互斥体

如果不存在则开始执行恶意功能，从资源中释放需要用到的恶意模块到C:\\\Users\\\All Users
目录下，包括永恒之蓝攻击工具、加密模块、密码抓取工具Mimikatz。

释放永恒之蓝攻击工具，其中blue.exe 是永恒之蓝漏洞攻击工具，star.exe是脉冲双星后门植入工具，down64.dll
是漏洞攻击成功后植入被攻击机器的后门，功能是下载勒索病毒母体，其它文件都是攻击工具需要用到的依赖库和配置文件。

![image017.png](https://image.3001.net/images/20180720/15320545623834.png!small)![image019.png](https://image.3001.net/images/20180720/15320545623092.png!small)![image021.png](https://image.3001.net/images/20180720/15320545625059.png!small)![image023.png](https://image.3001.net/images/20180720/15320545624728.png!small)![image025.png](https://image.3001.net/images/20180720/15320545626935.png!small)![image027.png](https://image.3001.net/images/20180720/1532054563100.png!small)![image029.png](https://image.3001.net/images/20180720/15320545638295.png!small)![image031.png](https://image.3001.net/images/20180720/15320545639637.png!small)![image033.png](https://image.3001.net/images/20180720/15320545632150.png!small)![image035.png](https://image.3001.net/images/20180720/15320545639030.png!small)![image037.png](https://image.3001.net/images/20180720/153205456387.png!small)![image039.png](https://image.3001.net/images/20180720/15320545643175.png!small)![image041.png](https://image.3001.net/images/20180720/15320545646960.png!small)![image043.png](https://image.3001.net/images/20180720/15320545643899.png!small)![image045.png](https://image.3001.net/images/20180720/15320545649785.png!small)![image047.png](https://image.3001.net/images/20180720/15320545653393.png!small)![image049.png](https://image.3001.net/images/20180720/15320545659578.png!small)![image051.png](https://image.3001.net/images/20180720/15320545658019.png!small)![image053.png](https://image.3001.net/images/20180720/15320545662235.png!small)![image055.png](https://image.3001.net/images/20180720/15320545661509.png!small)![image057.png](https://image.3001.net/images/20180720/15320545665865.png!small)![image059.png](https://image.3001.net/images/20180720/15320545668256.png!small)![image061.png](https://image.3001.net/images/20180720/15320545676398.png!small)

图：释放永恒之蓝攻击工具

释放加密模块，负责加密受害者计算机中的文件，针对加密模块的分析详见下文“加密模块分析”部分。

![image063.png](https://image.3001.net/images/20180720/15320545943876.png!small)

图：释放加密模块

判断系统架构，释放不同版本的密码抓取工具Mimikatz
并运行，64位系统从资源MINI64释放，32位系统从资源MINI32释放，命名为mmkt.exe。

![image065.png](https://image.3001.net/images/20180720/15320546573984.png!small)

图：释放运行密码抓取工具

密码抓取模块运行后会将抓取到的用户名保存到病毒目录下的“uname”文件中，密码保存到“upass”文件中。运行加密勒索模块，加密本机文件。

![image067.png](https://image.3001.net/images/20180720/15320546985184.png!small)

图：运行加密模块

创建三个线程攻击网络中的其它机器。

![image069.png](https://image.3001.net/images/20180720/15320547388850.png!small)

图：创建线程攻击其它机器

线程1，获取本机IP地址。

![image071.png](https://image.3001.net/images/20180720/15320547844536.png!small)

图:获取本机IP

循环攻击本地局域网Local_IP/16，16位子网掩码的网段。例如192.168.1.1——192.168.255.255，覆盖65536台主机，而不是仅仅攻击255台主机，相对而言攻击范围更广。

创建线程传入要攻击的IP。

![image073.png](https://image.3001.net/images/20180720/15320549149254.png!small)![image075.png](https://image.3001.net/images/20180720/15320549147623.png!small)

图：循环攻击局域网主机

只攻击指定IP的445端口。

![image077.png](https://image.3001.net/images/20180720/15320549751303.png!small)

图：线程1只攻击445端口

线程2，攻击局域网中除了445端口之外的其它硬编码的226个端口。创建线程，传入攻击IP和端口，与线程1不同，线程1只传入攻击IP，端口固定445。线程2在创建子线程的时候传入了攻击IP和端口
。

![image079.png](https://image.3001.net/images/20180720/15320550162338.png!small)

图：使用web漏洞攻击局域网中的机器

和线程1相比，线程2增加了一个判断，如果传入的端口是445，则执行永恒之蓝漏洞攻击，否则执行web漏洞攻击，不过针对445端口的永恒之蓝攻击不会生效，因为硬编码的226个端口中不包含445端口，即使包含，上层函数也不会传递445端口。因为线程1就可以完成局域网的445端口攻击了，此处就不用再攻击了。此病毒旧版本的硬编码端口列表中包含445端口。新版本的端口列表修改了，但是这里的代码没有修改，因此这里的判断显得有些多余。

![image081.png](https://image.3001.net/images/20180720/15320550545670.png!small)

图：判断端口执行攻击

此外在执行web攻击之前会设置一个标志位，如果端口是443或8443则将标志位设置为1，目的是拼凑攻击报文时，区分http还是https。https服务默认443端口，tomcat的https服务需要8443端口。

![image083.png](https://image.3001.net/images/20180720/15320551596811.png!small)![image085.png](https://image.3001.net/images/20180720/1532055159960.png!small)

图：拼凑攻击报文

之所以没有固定端口，对同一个IP使用不同的端口循环攻击226次，是因为网络中有些机器没有打补丁，但是会将各种web服务的默认端口号修改为其它端口号，作为漏洞缓解措施。攻击者通过这种方式绕过缓解措施。这也为我们提了个醒，缓解措施很有可能被绕过，把漏洞彻底修复才能更大限度的避免被攻击。

硬编码的内置端口列表：

![image087.png](https://image.3001.net/images/20180720/15320551947362.png!small)

图：硬编码的攻击端口列表

线程3和线程2的区别主要是线程2攻击的是局域网IP，线程3攻击的是内置的互联网IP，病毒内置了大量的IP段，循环随机选取攻击。

![image089.png](https://image.3001.net/images/20180720/15320552221546.png!small)

图：循环攻击内置的IP段

从内置的硬编码的IP中，随机选取将要攻击的IP地址段。

![image091.png](https://image.3001.net/images/20180720/15320552423139.png!small)

图：随机选取

线程3的攻击函数和线程2相同，攻击每个IP时，都会循环攻击硬编码的226个端口，同样由于内置的编码表中不含有445端口，攻击互联网的线程也无法对445端口发起永恒之蓝攻击，只会向指定的IP发起web攻击。

![image093.png](https://image.3001.net/images/20180720/15320552688029.png!small)

图：循环攻击指定的IP端口

![image095.png](https://image.3001.net/images/20180720/15320553229382.png!small)

图：判断端口执行攻击

永恒之蓝攻击，漏洞触发后会将down64.dll植入到被攻击机器。

![image097.png](https://image.3001.net/images/20180720/15320554041095.png!small)

图：永恒之蓝攻击

down64.dll的功能是联网下载运行病毒母体，被攻击机器中毒后，又会循环同样的操作，加密本机文件勒索，攻击其它机器。

web攻击利用了多种漏洞，文件上传漏洞。

![image099.png](https://image.3001.net/images/20180720/15320554472429.png!small)

图：文件上传漏洞

tomcat弱口令攻击。

![image101.png](https://image.3001.net/images/20180720/15320554854498.png!small)

图：tomcat弱口令漏洞

CVE-2017-10271 WebLogic WLS组件漏洞。

![image103.png](https://image.3001.net/images/20180720/15320555318754.png!small)![image105.png](https://image.3001.net/images/20180720/15320555313370.png!small)

图：WebLogic WLS组件漏洞

CVE-2017-12149 JBOOS 反序列化漏洞。

![image107.png](https://image.3001.net/images/20180720/15320555832265.png!small)

图：JBOOS 反序列化漏洞

加密模块分析，Satan勒索病毒主要针对数据文件进行加密，加密后追加文件后缀为“.dbger”。

![image109.png](https://image.3001.net/images/20180720/15320556198174.png!small)

图：被加密文件的现象

勒索模块运行后，尝试对所有驱动器遍历文件，排除以下目录：

![b1.png](https://image.3001.net/images/20180723/15323113563981.png!small)

表：病毒排除的目录

![image111.png](https://image.3001.net/images/20180720/15320556785623.png!small)

图：病毒不加密的目录

当为如下后缀时，不会加密：

![b2.png](https://image.3001.net/images/20180723/15323114198083.png!small)

表格：病毒排除的后缀

![image113.png](https://image.3001.net/images/20180720/15320557314342.png!small)

图：病毒不加密的文件类型

然后创建线程对遍历到的文件进行加密，病毒还会尝试关闭SQL相关服务防止文件被占用无法加密。

![image115.png](https://image.3001.net/images/20180720/15320557641028.png!small)

图：关闭SQL服务

加密后文件名:[dbger@protonmail.com]+原始文件名+.dbger。

![image117.png](https://image.3001.net/images/20180720/15320558129637.png!small)

图：被加密的文件 命名规则

把加密密钥上传到给远程服务器101.99.84.136。

![image119.png](https://image.3001.net/images/20180720/1532055863232.png!small)

图：访问控制服务器

病毒的加密算法，加密方式:使用CryptAPI进行加密，算法为RC4，密钥结构:[HardWareID]+k_str1+k_str2+k_str3+[PUBLIC]。

密钥示例如下：

![image121.png](https://image.3001.net/images/20180720/15320559073288.png!small)![image123.png](https://image.3001.net/images/20180720/15320559075300.png!small)

图：密钥结构

使用Windows自带的CryptAPI进行加密，MD5算法哈希密钥，加密算法为RC4。

![image125.png](https://image.3001.net/images/20180720/15320559432699.png!small)

图：加密算法为RC4

硬编码了三个字符串，

    
    
    k_str1:"dfsa#@FGDS!dsaKJiewiu*#&*))__=22121kD()@#(*#@#@!DSKL909*(!#!@AA"  
    k_str2:"*@#AdJJMLDML#SXAIO98390d&th2nfd%%u2j312&&dsjdAa"  
    k_str3:"@!FS#@DSKkop()(290#0^^^2920-((__!#*$gf4SAddAA"。

![image127.png](https://image.3001.net/images/20180720/15320560017875.png!small)

图：硬编码的字符串，作为密钥的一部分

HardWareID和PUBLIC都是是随机生成的。首先，它会尝试读取保存在C:\Windows\Temp\KSession中的HardWareID值，如果失败则随机生成0x40大小字符串（固定的，加密过程只生成一次），然后写入了KSession文件中。

![image129.png](https://image.3001.net/images/20180720/15320560311524.png!small)

图：生成HardWareID

![image131.png](https://image.3001.net/images/20180720/15320560703686.png!small)

图：HardWareID会被保存在KSession文件中  

同样的方式生成长度为0x20大小的PUBLIC值（每加密一个文件生成一次）。

![image133.png](https://image.3001.net/images/20180720/15320560702833.png!small)

图：生成PUBLIC

从图中可以看到，每个文件的PUBLIC是不同的。

![image135.png](https://image.3001.net/images/20180720/1532056070123.png!small)

图：每个文件的PUBLIC不同

最终HardWareID和PUBLIC都会追加到，被加密文件的末尾。

![image137.png](https://image.3001.net/images/20180720/1532056070220.png!small)

图：可以在被加密的文件末尾看到HardWareID与PUBLIC的值

病毒为了加快加密速度，对不同大小，不同类型的文件采取不同的加密策略，重要的文档例如
word、excel文档全部加密。其它文档根据文件大小，加密文件约前二分之一、前五分之一不等。

特殊后缀如下，主要是比较重要的办公文档、源代码文档的后缀名。

![b3.png](https://image.3001.net/images/20180723/15323114792458.png!small)

表：完全加密的特殊后缀

加密方式为如下几种：

1、小于等于100000000字节

（1）特殊后缀，完全加密。

（2）其它后缀，部分加密，加密大小的算法 CryptSize = (FileSize / 2000) *1000，约为文件的二分之一。

举个例子，文件小于等于100000000字节时，zip格式的压缩包就会被完全加密，而RAR格式的只会被加密大约二分之一，因为zip是病毒指定的特殊后缀，而RAR不在列表中。

2、大于100000000 字节的文件

（1）特殊后缀，完全加密。

（2）其它后缀，部分加密，加密大小的算法 CryptSize = (FileSize / 5000) *1000，约为文件的五分之一。

举个例子，文件大于100000000字节时，zip格式的压缩包就会被完全加密，而RAR格式的
只会被加密大约五分之一，因为zip是病毒指定的特殊后缀，而RAR不在列表中。

当加密完成后，病毒会打开勒索文本提示用户支付赎金。勒索信息提供三种语言英文、中文和韩文，威胁受害者在三天之内向作者支付1个比特币，否则文件无法解密，并且重要文件被公开。然而事实上文件可以解密，并且病毒作者也没有获取到受害者的文件。

 **比特币钱包:3EbN7FP8f8x9FPQQoJKXvyoHJgSkKmAHPY**

 **邮箱:dbger@protonmail.com**

![image001.png](https://image.3001.net/images/20180720/15320564393372.png!small)

图：弹出勒索信息

## IOC

MD5

> ECF5CABC81047B46977A4DF9D8D68797 病毒母体
>
> C0150256A864E5C634380A53290C7649 加密模块

C&C

> <http://101.99.84.136>
>
> <http://101.99.84.136/cab/sts.exe>
>
> <http://101.99.84.136/cab/st.exe>
>
>
> [http://101.99.84.136/data/token.php?status=ST&code=](http://101.99.84.136/data/token.php?status=ST&code=)
>
>
> [http://101.99.84.136/data/token.php?status=BK&code=](http://101.99.84.136/data/token.php?status=BK&code=)
>
>
> [http://101.99.84.136/data/token.php?status=DB&code=](http://101.99.84.136/data/token.php?status=DB&code=)
>
>
> [http://101.99.84.136/data/token.php?status=ALL&code=](http://101.99.84.136/data/token.php?status=ALL&code=)
>
> <http://101.99.84.136/count.php?url=>

 ***本文作者：瑞星，转载请注明来自FreeBuf.COM**

