## 一、 前言：

光通天下无患实验室近期在复盘过程中，针对以往远控及高混淆样本进行了梳理，该样本名叫r3nrl.vbs的vbs病毒。

本文通过静态混淆分析、动态混淆调试、样本分析、攻击模拟、取证分析五个模块进行事件分析。

样本信息IOC

![图片0.png](https://image.3001.net/images/20200113/1578900483_5e1c1c038361f.png!small)混淆加密梳理流程图如下所示：

![图片1.png](https://image.3001.net/images/20200113/1578900499_5e1c1c13eae5f.png!small)

## 二、 静态混淆分析：

➀查看样r3nrl.vbs仅1kb，捕获到的附加文件Du3864.TMP数据123kb：

![图片2.png](https://image.3001.net/images/20200113/1578900658_5e1c1cb278e7e.png!small)➁r3nrl.vbs内容分析，图中见注释：

![图片3.png](https://image.3001.net/images/20200113/1578900682_5e1c1cca9b513.png!small)➂如上图所示，r3nrl.vbs功能是加载器得作用，加载执行Du3864.TMP的数据内容，Du3864内容如下：

![图片4.png](https://image.3001.net/images/20200113/1578900699_5e1c1cdb725c8.png!small)

➃如上图所示，发现vb定义了变量yM，NDuISBA，NDuISBAaIrOboTOkIL字符换，并且加密字符串赋值。

针对病毒来说，不论多高强度的混淆手法，总是要被解析与执行，定位执行函数如run、execute作为突破点，提取上述中execute关键字段如下图所示：

![图片5.png](https://image.3001.net/images/20200113/1578900734_5e1c1cfe228ce.png!small)

➄定位execute发现正好解混淆加密变量NDuISBA、NDuISBAaIrOboTOkIL，按照脚本执行顺序，先来分解NDuISBA混淆，将execute中代码执行流程分解，从内到外，如下图所示：

⇛嵌套函数梳理：

![图片6.png](https://image.3001.net/images/20200113/1578900750_5e1c1d0e83cb2.png!small)⇛需要注意的是split()(1)与split()(0)，split函数以检索关键字下标，一维数组返回，分割点是”BA.AB”字符串，切割如下图所示：

![图片7.png](https://image.3001.net/images/20200113/1578900764_5e1c1d1c6b907.png!small)⇛接下来调用replace进行字符串替换，将包含”A.B”字符串替换成空格，去混淆后得到函数Function
aB(ByVal NDuISBAa), 函数内容如下：

![图片8.png](https://image.3001.net/images/20200113/1578900781_5e1c1d2dc3b70.png!small)⇛通过NDuISBA字符串解密出的Zn变量对NDuISBAaIrOboTOkIL字符串split进行数组切割，如下图所示：

![图片9.png](https://image.3001.net/images/20200113/1578900804_5e1c1d441da96.png!small)⇛
replace进行字符串替换，套路与上述相同，通过二次替换参数就被解密出来，调用NDuISBA字符解密的aB()函数(下文动态分析)，NDuISBAaIrOboTOkIL去混淆后的字符串作为传参传进，解密数据如下所示：

![图片10.png](https://image.3001.net/images/20200113/1578900893_5e1c1d9d9b168.png!small)

![图片10（2）.png](https://image.3001.net/images/20200113/1578900820_5e1c1d5437d7f.png!small)

解密出来的数据仍是execute执行且混淆后的数据，针对以上参数类型，就可以给对函数分类，aB()函数则是对字符串解密，而BaB()则是对数字混淆解密。

梳理静态去混淆流程如下：

![图片11.png](https://image.3001.net/images/20200113/1578900945_5e1c1dd14ae22.png!small)➥
第一阶段解密的数据：

![图片11（2）.png](https://image.3001.net/images/20200113/1578900968_5e1c1de887e93.png!small)✍Function
aB(ByVal
NDulSBAa)分析，分析与动态调试过程中这不是必须，但是有时候需要知道如何进行的混淆加密，调试过程中报错或解密数据看起来不对的时候要心中有数，如下所示：

![图片12.png](https://image.3001.net/images/20200113/1578901062_5e1c1e464530f.png!small)✉
第一阶段利用split()与replace()函数对字符串进行了简单混淆了，也就最常见的混淆方式之一”体积膨胀”。

## 三、 动态解密调试：

✎ 上文解密函数aB()，为了方便、精准的动态跟踪，但也有一定风险。这里将用vs2017去调试，使用方式如下所示：

![图片13.png](https://image.3001.net/images/20200113/1578901121_5e1c1e81dd133.png!small)![图片14.png](https://image.3001.net/images/20200113/1578901135_5e1c1e8fb4532.png!small)

wscript /X vbsName即可断下调试

➀ 将函数与解密出来的NDuISBA参数，组成一个新的vbs脚本，这样方便局部功能分析，动态调试去查看解密的结果，第一次aB()函数解密如下：

![图片15.png](https://image.3001.net/images/20200113/1578901259_5e1c1f0b6d9ee.png!small)➁提取数据，发现是两个exectue，也就是上文中标识的数据

![图片1.png](https://image.3001.net/images/20200113/1578901324_5e1c1f4ca0aa4.png!small)

➂脚本在解密的过程中，一定要按照执行代码的执行流程解析，并不是发现简单就入手分析，存在一定的关联，提取数据带入aB().

你会发现异常，如果你分析了aB()加密方法，跟踪一次就很轻送定位到问题,字符串最后”\”导致了报错：

![图片16.png](https://image.3001.net/images/20200113/1578901484_5e1c1fec7b0fa.png!small)

![图片17.png](https://image.3001.net/images/20200113/1578901508_5e1c20040b96a.png!small)

➃再次动态解析，如下所示：

![图片18.png](https://image.3001.net/images/20200113/1578901524_5e1c20142b241.png!small)

➄提取解密的有效数据，示例后如下所示：

![图片19.png](https://image.3001.net/images/20200113/1578901565_5e1c203d43e6f.png!small)➅这时候解密函数
Function Ds(txt)，如上图所示针对1.1的步骤二次解密，如下图所示：

![图片19（2）.png](https://image.3001.net/images/20200113/1578901582_5e1c204e0a3b8.png!small)➥
Function BaB(txt)函数梳理：

![图片20.png](https://image.3001.net/images/20200113/1578902503_5e1c23e79d2c5.png!small)➆针对
Function Ds(txt)函数内部的数据进行去混淆，解密第一个exec数据如下所示：

![图片20（2）.png](https://image.3001.net/images/20200113/1578902542_5e1c240e04f31.png!small)![图片20（3）.png](https://image.3001.net/images/20200113/1578902635_5e1c246bd66cf.png!small)

➇上述过程脚本梳理如下图所示：

![图片21.png](https://image.3001.net/images/20200113/1578902656_5e1c2480543fb.png!small)➈还原Function
Ds(txt)函数如下：

![图片22.png](https://image.3001.net/images/20200113/1578902678_5e1c2496163dd.png!small)➉这时候已经还原aB()、BaB()、Ds()函数，继续分析调用BaB()执行的数据，如下所示：

![图片23.png](https://image.3001.net/images/20200113/1578902696_5e1c24a886905.png!small)⑪
Ym字符串进行去混淆操作，通过Ds()对Ym变量解密，最终vbs整个解密脚本复原如下所示：

![图片24.png](https://image.3001.net/images/20200113/1578902714_5e1c24ba119cb.png!small)✉
第二阶段解密，通过aB()函数提取BaB()函数，再通过BaB()解密出Ds()函数中必要的变量rs1，rs2密钥，针对Ym字符串调用Ds()函数进行解密，这种方式被大多数称为”函数链加密法则”。

## 四、 样本分析：

➀ Ds()对变量Ym解密后提取最后病毒样本，经过缩进排版vbs部分示图如下：

![图片25.png](https://image.3001.net/images/20200113/1578902767_5e1c24ef2bfd9.png!small)![图片26.png](https://image.3001.net/images/20200113/1578902793_5e1c2509ef65b.png!small)✃
针对该阶段调用部分函数功能梳理如下所示：

![图片26（2）.png](https://image.3001.net/images/20200113/1578902828_5e1c252cb0880.png!small)➁样本创建了全局对象如下所示：

![图片26（3）.png](https://image.3001.net/images/20200113/1578902846_5e1c253e9893c.png!small)➂初始化原始变量及数据，如下图所示

![图片27.png](https://image.3001.net/images/20200113/1578902868_5e1c2554666fc.png!small)➃拷贝文件到指定文件夹下，installdir
临时目录Temp：

![图片27（2）.png](https://image.3001.net/images/20200113/1578902892_5e1c256c76d51.png!small)

➄调用了xver()函数，判断是否32Bit系统还是64bit系统，对注册表HKEY_LOCAL_MACHINE\software\Microsoft\rknrl\wspr进行读取，获取了电脑磁盘名称。

调用wmi()函数，内部调用了WmiConsumer,创建了定时器脚本，脚本内容是txt保存的数据，如下所示：

![图片28.png](https://image.3001.net/images/20200113/1578902916_5e1c2584049b7.png!small)➅
Function WmiConsumer(objconn,txt,consumer)函数分析如下：

![图片29.png](https://image.3001.net/images/20200113/1578902940_5e1c259c529b0.png!small)

✎以上内容创建了活动的消费者，绑定过滤器，每8秒执行一次脚本。

✃ 通过wmi插件实现恶意代码持久化，通过活动消费者绑定这种方法去执行的vbs脚本，自启动脚本如下：

![图片29（2）.png](https://image.3001.net/images/20200113/1578903171_5e1c268319377.png!small)

![图片30.png](https://image.3001.net/images/20200113/1578902994_5e1c25d20a235.png!small)➆下面执行instance()，通过调用内部调用variation()替换密钥数据变异原样本切割符，替换原样本中”|E8”切割点，C:\Users\\....Local\Temp路径下释放winstart.Vbs、Du3864.TMP文件，如下所示：

![图片31.png](https://image.3001.net/images/20200113/1578903231_5e1c26bfcc2b9.png!small)![图片32.png](https://image.3001.net/images/20200113/1578904555_5e1c2beb52ba6.png!small)

➇执行释放后的winstart.vbs,
退出当前病毒，执行函数writeRF函数，在C:\Users\\.....\Temp文件夹下创建、拷贝文件rknrl.vbs，，如下图所示：

![图片33.png](https://image.3001.net/images/20200113/1578904587_5e1c2c0bc175a.png!small)➈GetD函数会调用chkroot去检测，同样会解密url如下：

![图片34.png](https://image.3001.net/images/20200113/1578904678_5e1c2c665e2c4.png!small)![图片34（2）.png](https://image.3001.net/images/20200113/1578904709_5e1c2c85a4071.png!small)➉去解密ip链接，后面进入GetH()，调用了Gethost()去收集系统信息，同时字符串解密url链接如下：

![图片34（3）.png](https://image.3001.net/images/20200113/1578904732_5e1c2c9c0fe19.png!small)ⓐ
chkhost检测主机其实是发送采集的系统信息，调用了information()获取账户、操作系统的版本、SID等数据，杀毒软件等敏感数据

![图片35.png](https://image.3001.net/images/20200113/1578904760_5e1c2cb877f61.png!small)![图片36.png](https://image.3001.net/images/20200113/1578904775_5e1c2cc7b2bad.png!small)![图片36（2）.png](https://image.3001.net/images/20200113/1578904786_5e1c2cd2720d9.png!small)

ⓑ 最终函数会返回GetHneW变量,执行WmiServer()，临时文件下创建rknrl.TMP1、rknrl.TMP2，

GetHnew = "http://airobotheworld.aigoingtokill.com/ctrl/playback.php"

![图片37.png](https://image.3001.net/images/20200113/1578904807_5e1c2ce785c6f.png!small)![图片38.png](https://image.3001.net/images/20200113/1578904818_5e1c2cf2672d2.png!small)ⓒ调用chekoffice()，检测是否装了office，匹配成功，通过修改注册表，将office安全将为最低级别，启用了所有宏，这是为了执行宏病毒而做预热，如下所示：

![图片39.png](https://image.3001.net/images/20200113/1578904836_5e1c2d043408e.png!small)ⓓ
下面在Temp文件夹下创建临时目录winstart，调用Function createAuto()函数，设置文件属性为系统文件+隐藏文件，如下图所示：

![图片40.png](https://image.3001.net/images/20200113/1578904855_5e1c2d17600e3.png!small)ⓔ
接下来调用GetIP()收集了网络配置，获取了本机的MAC与IP地址，如下图所示：

![图片41.png](https://image.3001.net/images/20200113/1578904874_5e1c2d2a0198b.png!small)ⓕ
接下来进入main函数，第一次执行会进入codestart()如下所示：

![图片42.png](https://image.3001.net/images/20200113/1578904890_5e1c2d3aa8084.png!small)ⓖ
调用offic()，判断是否Temp文件夹下是否存在rknrl.TMP1与rknrl.TMP2，不存在则下载，并拷贝命名为Normal.doc与Book.xls

![图片43.png](https://image.3001.net/images/20200113/1578904908_5e1c2d4c211b4.png!small)![图片44.png](https://image.3001.net/images/20200113/1578904923_5e1c2d5b48152.png!small)rknrl.TMP1与rknrl.TMP2内容：

![图片45.png](https://image.3001.net/images/20200113/1578904940_5e1c2d6c3c609.png!small)打开html页面后发现github
404,虽然已经挂了，但是病毒作者意图很明显，从上文分析中将office调整安全级别最低及启用宏，意味着要从git上拉工具及payload进行投毒与部署。基于Web
C&C进行隐蔽通讯与跳板较为最出名GitHub公开的twitter后门程序twittor。

![图片46.png](https://image.3001.net/images/20200113/1578904957_5e1c2d7de99b6.png!small)

这一特性利用公用平台投毒与奇安信近期发表的《摩诃草团伙利用公用平台分发C&C配置攻击活动揭露 》利用思路点大体一致。

ⓗ调用post函数对httpobj.sned发送数据请求，chkorder()接收返回的远控指令，根据指令执行功能函数，实现后门远控。

http的方式去远链控制意图很明显，更容易进行指令跳板,也是Web C&C 流量来实现接收指令。

![图片46（2）.png](https://image.3001.net/images/20200113/1578904980_5e1c2d940f6df.png!small)![图片47.png](https://image.3001.net/images/20200113/1578904992_5e1c2da0cadf9.png!small)![图片48.png](https://image.3001.net/images/20200113/1578905000_5e1c2da8e3bea.png!small)ⓘ
进入了死循环，接收服务器端发来的远控执行指令，如下图所示：

![图片49.png](https://image.3001.net/images/20200113/1578905028_5e1c2dc49ac81.png!small)![图片49（2）.png](https://image.3001.net/images/20200113/1578905040_5e1c2dd080b01.png!small)

✈遗憾的是站点与服务器已经挂掉，已经接收不到有价值的payload及[download](http://www.baidu.com/link?url=fn7LryAnqsj4JR_3qHV7icv75a20gv52j6-pgRKDuIZJmWlZ9R3W_JeUU65s9CtKizF2xhFOjCtmcdO0GJHY8GAjX8_BmGu1M0bJWjQNGdK)File。

分析人员通过部署B&C服务，根据样本分析与被控端逻辑复现攻击环境，模拟黑客远控，针对现场环境取证分析，请看《vbs远控病毒之攻击模拟与取证分析》。

函数调用流程图：

![图片50.png](https://image.3001.net/images/20200113/1578905059_5e1c2de3952ac.png!small)

