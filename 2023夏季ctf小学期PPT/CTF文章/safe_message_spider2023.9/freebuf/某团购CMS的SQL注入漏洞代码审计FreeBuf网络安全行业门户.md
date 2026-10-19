作者：会上树的猪 合天智汇

0x00 SQL注入漏洞：

简单介绍一下SQL语句：通俗来理解就是开发者盲目相信用户，没有严格检查用户输入，导致用户可以输入恶意参数进入程序逻辑，最终拼接恶意参数改变原本的SQL语句逻辑，造成SQL注入漏洞。

0x01 关于CMS

本次审计的CMS是基于Web应用的B/S架构的团购网站建设解决方案的建站系统，它可以让用户高效、快速、低成本的构建个性化、专业化、强大功能的团购网站，采用PHP和MYSQL数据库开发技术，版本CV1.6。商业案例如下：

![v2-4f041bbfa91b573cced92aef80bf8e77_r.jp](https://pic2.zhimg.com/v2-4f041bbfa91b573cced92aef80bf8e77_r.jpg)

审计结果实战测试：

![v2-4337d139e492b5a83e446f0fa490a131_r.jp](https://pic4.zhimg.com/v2-4337d139e492b5a83e446f0fa490a131_r.jpg)

0x02 漏洞分析：

首先在本地搭建一个网站，方便之后测试，一键安装也没啥说的，跳过。重点讲讲这个团购CMS的SQL操作。这个团购CMS将SQL操作全部写到了include/library/DB.class.php文件：

![v2-a976ee8ad73f83351ae61993002fa422_r.jp](https://pic3.zhimg.com/v2-a976ee8ad73f83351ae61993002fa422_r.jpg)

然后分析这个文件，发现这里面的函数有些使用了：mysql_real_escape_string函数对参数进行过滤，整数参数就强制转换int类型

![v2-5afa47eacfcee9d22a89da4d4386f9af_r.jp](https://pic2.zhimg.com/v2-5afa47eacfcee9d22a89da4d4386f9af_r.jpg)

关于mysql_real_escape_string函数的注入可以尝试宽字节注入，当数据库编码采用GBK的时候可以尝试bypass函数检查，但是此处不适用。之后审计发现其中存在几个未对参数进行过滤直接执行SQL语句的函数：GetDbRowById、GetQueryResult、GetField。

![v2-00d674c1a1d0596adb025b8f46ef5eb9_r.jp](https://pic1.zhimg.com/v2-00d674c1a1d0596adb025b8f46ef5eb9_r.jpg)

![v2-9703ea8e127177a4d***e8a6e8b0cb2c_r.jp](https://pic4.zhimg.com/v2-9703ea8e127177a4d***e8a6e8b0cb2c_r.jpg)

![v2-e5b361a66231d7f23358b0a5b1c0ad43_r.jp](https://pic2.zhimg.com/v2-e5b361a66231d7f23358b0a5b1c0ad43_r.jpg)

此处采用敏感函数回溯的方法进行审计，先全局搜索这些函数，然后想办法对达到触发条件。

  1. 全局搜索GetField函数，发现没有被引用的地方。  

![v2-658110142b8c287ec8096944d5479970_r.jp](https://pic1.zhimg.com/v2-658110142b8c287ec8096944d5479970_r.jpg)

2、全局搜索GetQueryResult函数，搜索结果比较多，如下：

![v2-ac1474496ce601ff07b0ff84d8f9cac2_r.jp](https://pic4.zhimg.com/v2-ac1474496ce601ff07b0ff84d8f9cac2_r.jpg)

先尝试审计第一处：/ajax/manage.php，如下，如果存在，可以通过$id变量进行注入。

![v2-b370822a85a2cc8edb00c331d5931e07_r.jp](https://pic1.zhimg.com/v2-b370822a85a2cc8edb00c331d5931e07_r.jpg)

追踪如何触发函数：第490行，当变量action满足条件即可：

![v2-b1d533daae5be3b5332c063551e7a7b9_r.jp](https://pic4.zhimg.com/v2-b1d533daae5be3b5332c063551e7a7b9_r.jpg)

而继续回溯，$action的来源$_GET:

![v2-bb907d6c25e3ed299a7761ce1c432a5c_r.jp](https://pic2.zhimg.com/v2-bb907d6c25e3ed299a7761ce1c432a5c_r.jpg)

同时也发现id变量被强制类型转换了，哦豁，这下安逸了，这个点基本利用不了了。同时测试过程中此处还有一处调用了未过滤SQL函数：

![v2-bdb2d7e89c0538cf7b197758594ad73e_r.jp](https://pic3.zhimg.com/v2-bdb2d7e89c0538cf7b197758594ad73e_r.jpg)

![v2-b040576886fcdb892da04c644184c84b_r.jp](https://pic2.zhimg.com/v2-b040576886fcdb892da04c644184c84b_r.jpg)

不过都用到了ID参数进行注入，所以不能利用，放弃。

之后选择其他可能存在的地方继续审计：/manage/user/index.php

![v2-cac3f3073531981252ae5e7910c63c7c_r.jp](https://pic3.zhimg.com/v2-cac3f3073531981252ae5e7910c63c7c_r.jpg)

![v2-60bae407babd96c9e3b6605b6bb24055_r.jp](https://pic2.zhimg.com/v2-60bae407babd96c9e3b6605b6bb24055_r.jpg)

但是这两处同样存在intval参数过滤。

![v2-5838cb2bcf592d162e891962b00c2c74_r.jp](https://pic4.zhimg.com/v2-5838cb2bcf592d162e891962b00c2c74_r.jpg)

再继续搜索，发现/manage/vote/feedback.php

![v2-64b21f0676964e39c33a09f8a0264318_r.jp](https://pic1.zhimg.com/v2-64b21f0676964e39c33a09f8a0264318_r.jpg)

此处$question[‘id’]参数来源于前一个查询结果，可以考虑二次注入，不过此处因为id参数为提交问卷时系统自动生成，所以无法利用了。

![v2-d8665eb9204fd16b287f173d51b6bb5a_r.jp](https://pic4.zhimg.com/v2-d8665eb9204fd16b287f173d51b6bb5a_r.jpg)

最后两处调用这个函数的地方在DB.class.php中：其中一个属于LimitQuery函数调用，因为存在过滤，所以利用比较困难：

![v2-8ebb415b33f5b010f2aeee90d5cffd25_r.jp](https://pic1.zhimg.com/v2-8ebb415b33f5b010f2aeee90d5cffd25_r.jpg)

另外一处便是GetDbRowById调用，此处不存在过滤，可能存在注入，这个审计便放到下一部分：

![v2-2db48300e5748ba51d3599dfcf5804cd_r.jp](https://pic3.zhimg.com/v2-2db48300e5748ba51d3599dfcf5804cd_r.jpg)

  1. 全局搜索GetDbRowById函数：根据之前的审计，函数本身没有对参数过滤，其中调用的GetQueryResult函数也没有过滤，可能存在SQL注入。  

![v2-8e195d68a9f1cbf80e8a8152ebcce5d8_r.jp](https://pic2.zhimg.com/v2-8e195d68a9f1cbf80e8a8152ebcce5d8_r.jpg)

可以发现GetDbRowById函数在include/library/Table.class.php文件存在调用：_Fetch函数和FetchForce函数

![v2-779de5bced710eb1f22ad1ff2d676409_r.jp](https://pic3.zhimg.com/v2-779de5bced710eb1f22ad1ff2d676409_r.jpg)

![v2-1f79f45a7864df6a216dfdb82b84596c_r.jp](https://pic4.zhimg.com/v2-1f79f45a7864df6a216dfdb82b84596c_r.jpg)

![v2-379ed534aa49f2835974d3b604af7f57_r.jp](https://pic1.zhimg.com/v2-379ed534aa49f2835974d3b604af7f57_r.jpg)

其中_Fetch函数在同类中的Fetch方法被调用：

![v2-6c9fcd88d21e85b06a59b2d4c1736f3a_r.jp](https://pic4.zhimg.com/v2-6c9fcd88d21e85b06a59b2d4c1736f3a_r.jpg)

因此需要全局搜索Fetch函数和FetchForce函数：

首先来搜索FetchForce函数，结果如下，还挺多的

![v2-74ed1e587437f3c3fa4c01d784a3d38f_r.jp](https://pic1.zhimg.com/v2-74ed1e587437f3c3fa4c01d784a3d38f_r.jpg)

首先要说的就是搜索的结果不一定全部存在注入，需要再次寻找其中疏于过滤的点进行验证，下面举几个栗子：

文件：/ajax/chargecard.php

![v2-66ff67c6844023d7ccfca401eb977365_r.jp](https://pic4.zhimg.com/v2-66ff67c6844023d7ccfca401eb977365_r.jpg)

不需要登录便可以直接访问这个文件，当$action为query时可以调用函数，且$secret不存在过滤，开启debug调试跟踪参数的流程：先输入secret=123’

可以看到对secret参数没有进行任何过滤便传入FetchForce函数：

![v2-71a820c4878fc2b092b1a8aa098c84a5_r.jp](https://pic1.zhimg.com/v2-71a820c4878fc2b092b1a8aa098c84a5_r.jpg)

将存在恶意字符的参数拼接SQL语句，造成SQL注入，因为此处存在对空格等字符的正则匹配，所以可以使用/**/代替空格。

![v2-bcb37cfb7233ec3092ab03bffd55157f_r.jp](https://pic2.zhimg.com/v2-bcb37cfb7233ec3092ab03bffd55157f_r.jpg)

因为此处不存在回显，要使用盲注，使用时间盲注验证，一个用时2秒，一个用时5秒

![v2-affa3c5f66265ec159894f20b615b4ec_r.jp](https://pic3.zhimg.com/v2-affa3c5f66265ec159894f20b615b4ec_r.jpg)

![v2-33b0dd6969ed09a131462b822350a1b2_r.jp](https://pic2.zhimg.com/v2-33b0dd6969ed09a131462b822350a1b2_r.jpg)

而且同文件下存在另外一处注入：

![v2-0e74c9729ca722bb522d31***1bc3f83_r.jp](https://pic4.zhimg.com/v2-0e74c9729ca722bb522d31***1bc3f83_r.jpg)

这个地方用方法也差不多，就改一下action参数便可以。

再举一个不存在注入的情况：/ajax/manage.php

![v2-cbe4b72897acc3f0588eb11984e63465_r.jp](https://pic4.zhimg.com/v2-cbe4b72897acc3f0588eb11984e63465_r.jpg)

![v2-c6491cefd6e697b03abe582a8053e126_r.jp](https://pic4.zhimg.com/v2-c6491cefd6e697b03abe582a8053e126_r.jpg)

虽然调用了FetchForce函数，但是溯源之后发现对id变量进行了强制转换，因此属于不能利用的点。与此同时new.php也属于同理情况：

![v2-1dfa7aea4bb6be777bdb63847b3ef471_r.jp](https://pic3.zhimg.com/v2-1dfa7aea4bb6be777bdb63847b3ef471_r.jpg)

同时如果继续搜索审计就能发现其他存在注入的点：

![v2-0036ecc69aa5cdd5f56ef17303ec1c79_r.jp](https://pic4.zhimg.com/v2-0036ecc69aa5cdd5f56ef17303ec1c79_r.jpg)

其余的文件就不一一看了。

接下来查看Fetch函数：搜索结果如下

![v2-aa5fbfe4cc292a5dafc7965ec08c08d2_r.jp](https://pic2.zhimg.com/v2-aa5fbfe4cc292a5dafc7965ec08c08d2_r.jpg)

先来看文件：/ajax/system.php

![v2-fb6f6c2727d6bd903a067bcd161a9034_r.jp](https://pic3.zhimg.com/v2-fb6f6c2727d6bd903a067bcd161a9034_r.jpg)

![v2-765bebe511cb39ed8feeb667d1b23201_r.jp](https://pic1.zhimg.com/v2-765bebe511cb39ed8feeb667d1b23201_r.jpg)

不过这个地方应该是需要管理员登录的，登录之后传参是这个亚子的：

![v2-a6a83703544c1f5c0621850bb67fc4bd_r.jp](https://pic3.zhimg.com/v2-a6a83703544c1f5c0621850bb67fc4bd_r.jpg)

可以采用和之前相同的时间盲注：

![v2-69f453cd41dc8820d2c0fbd8a48e7452_r.jp](https://pic4.zhimg.com/v2-69f453cd41dc8820d2c0fbd8a48e7452_r.jpg)

![v2-c1787a6d6925179785***fcb9ef54c54_r.jp](https://pic3.zhimg.com/v2-c1787a6d6925179785***fcb9ef54c54_r.jpg)

再看另外一处漏洞：/api/call.php，此处不需要任何登录，可以在前台直接访问到文件，而且其中多个参数存在注入：

![v2-0899b510e34d2e000e5dd5966695b2a9_r.jp](https://pic1.zhimg.com/v2-0899b510e34d2e000e5dd5966695b2a9_r.jpg)

![v2-833e4caf72d89e1d1e4c212dc757c600_r.jp](https://pic3.zhimg.com/v2-833e4caf72d89e1d1e4c212dc757c600_r.jpg)

再之后很多便与上面的审计方法类似，还存在可以利用的点，也会存在许多无法利用的点，就不一一写出来了。

上面这个注入点还找到一个案例：

![v2-43346aaa0fef2e751b56a9b0ef925495_r.jp](https://pic3.zhimg.com/v2-43346aaa0fef2e751b56a9b0ef925495_r.jpg)

不过存在问题的便是这个CMS的密码加了一个固定字符串当作盐，在解MD5时会存在困难。

0x03 总结：

按照惯例，来小结几句。

关于SQL注入的防御，应该有很多方法了，首先就是不信任用户输入，严格过滤参数，之后的话还可以使用预查询方案，之后的话还可以使用软硬件防火墙。不过这些理论上都会存在bypass的情况，不过我太菜，不会bypass。

另外就是关于参数过滤，如同上面，执行参数过滤，但是依然找到了漏网之鱼，所以过滤策略某种情况下也是不可靠的。

最后就是关于代码审计了，代码审计一时爽，一直审计一直爽，奥力给！！！

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

