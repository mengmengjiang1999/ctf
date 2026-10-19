作者：会上树的猪合天智汇

## 0x00 写点废话  

在渗透测试中，获取一个webshell应该是我们不屑的追求，今天要通过这个CMS从代码的角度看一下可利用的getshell的方法。这一次的代码审计需要借助工具来定位可能存在的漏洞点，选择Seay源代码审计系统。步入正题。

## 0x01文件上传getshell：  

![v2-69b7ff1daa1b30bffe0b4da34c9ee0ea_r.jp](https://pic4.zhimg.com/v2-69b7ff1daa1b30bffe0b4da34c9ee0ea_r.jpg)

1、/kindupload.php：通过获取文件最后一个扩展名进行白名单匹配，且添加随机数命名新文件名，应该不存在文件上传漏洞

![v2-0b9c471a4246fb22e1267ecff1c265bc_r.jp](https://pic1.zhimg.com/v2-0b9c471a4246fb22e1267ecff1c265bc_r.jpg)

2、/upload.php：此文件属于测试文件

![v2-0c9e3b35d6905804a5a9c19666c69f93_r.jp](https://pic3.zhimg.com/v2-0c9e3b35d6905804a5a9c19666c69f93_r.jpg)

3、include/function/common.php：关于$image变量的来源有两个，为null时强制转换jpg格式，当对有图片项目进行编辑时，$image变量就是之前上传的文件地址，这样的话想进行任意文件上传应该就没有可能了。。。。。。

![v2-5170a7dbd7b98f34cc6688ca2871e8c3_r.jp](https://pic4.zhimg.com/v2-5170a7dbd7b98f34cc6688ca2871e8c3_r.jpg)

## 0x02 文件写入+文件包含getshll：  

在进行任意文件删除/读取/修改漏洞审计时发现支付日志位置可以向日志文件写入任意内容：漏洞位置：/alifast/alipay.function.php

![v2-5a1a404b7850461088ffee695cef0501_r.jp](https://pic1.zhimg.com/v2-5a1a404b7850461088ffee695cef0501_r.jpg)

根据定位，可以找到logResult函数：

![v2-52f31132c8410570819548fd4f55fb70_r.jp](https://pic2.zhimg.com/v2-52f31132c8410570819548fd4f55fb70_r.jpg)

可以看到其中的$word变量未经过任何check便写入到log.txt文件中（此处写入文件可能比较鸡肋，但如果可以找到任意文件包含，便可以直接getshell）而其中$word变量来源于对函数的引用，我们全局搜索一下看有哪些地方调用了logResult函数：

![v2-56b1cc48646a7cd333c7552058222ef3_r.jp](https://pic4.zhimg.com/v2-56b1cc48646a7cd333c7552058222ef3_r.jpg)

可以找到一处调用，在/alifast/lib/alipay_notify_class.php文件中：

![v2-df1866fdf62b5bc38b7db3582e2b867d_r.jp](https://pic2.zhimg.com/v2-df1866fdf62b5bc38b7db3582e2b867d_r.jpg)

通过verifyNotify函数，当POST数据不为空时就会调用logResult函数进行日志写入，那之后就转到查找何处调用了verifyNotify函数，找到一处调用：/alifast/returnadd_url.php

![v2-19a4b51ef4198083cc3f382b229945c8_r.jp](https://pic3.zhimg.com/v2-19a4b51ef4198083cc3f382b229945c8_r.jpg)

![v2-f0fc8bd5114919e0542f6935373645ed_r.jp](https://pic2.zhimg.com/v2-f0fc8bd5114919e0542f6935373645ed_r.jpg)

而且可以发现此处文件应该不需要登录便可以直接访问：

![v2-3f269321f49ff3d0f73dae5098f624ab_r.jp](https://pic4.zhimg.com/v2-3f269321f49ff3d0f73dae5098f624ab_r.jpg)

之后我们传入一个payload，然后开启DEBUG调试一下，看一下参数传递：

![v2-111aba25378a0e92256c66746f3c6078_r.jp](https://pic1.zhimg.com/v2-111aba25378a0e92256c66746f3c6078_r.jpg)

![v2-dd80b61b8cf5f6989f1bdb6260a7d985_r.jp](https://pic3.zhimg.com/v2-dd80b61b8cf5f6989f1bdb6260a7d985_r.jpg)

最后可以看一下log.txt文件，成功写入payload：

![v2-45edd478adef01e55bfd1ed739915ed6_r.jp](https://pic3.zhimg.com/v2-45edd478adef01e55bfd1ed739915ed6_r.jpg)

这需要结合文件读取漏洞才能利用，否则写入到txt文件属于鸡肋，之后便通过对扫描到的可能存在文件包含漏洞的点进行验证，未发现可利用的文件包含漏洞，上面这个任意写入真的鸡肋了。

![v2-25d94b7bbd2fb2f7799f46fc911fc955_r.jp](https://pic4.zhimg.com/v2-25d94b7bbd2fb2f7799f46fc911fc955_r.jpg)

不过作为一个搞信息安全的弱鸡，我是不会放弃的。

![v2-88bfe2ca45a06c88ed91218b42c01125_r.jp](https://pic4.zhimg.com/v2-88bfe2ca45a06c88ed91218b42c01125_r.jpg)

## 0x03后台通过修改模板getshell：  

感觉模板渲染位置最容易存在代码执行漏洞了，之前审计一些其他的CMS也在类似模板渲染位置发现了漏洞，导致getshell。因为系统存在很多模板，便只举一个模板当作栗子。

此处漏洞位置：/include/function/template.php

![v2-7d157815904bf7803964e579d6c121f2_r.jp](https://pic4.zhimg.com/v2-7d157815904bf7803964e579d6c121f2_r.jpg)

在__parse函数中存在preg_replace函数通过e参数进行代码执行。

我们先看在哪些地方对__parse函数进行了调用：

![v2-1f5e74a0258f59b4044fafd636b70076_r.jp](https://pic2.zhimg.com/v2-1f5e74a0258f59b4044fafd636b70076_r.jpg)

在同文件下58行，通过__tempate函数进行调用。

![v2-343d420f1d7ac87488d9724c63ffd7b4_r.jp](https://pic3.zhimg.com/v2-343d420f1d7ac87488d9724c63ffd7b4_r.jpg)

再搜索有哪些地方对__template函数进行了调用：

![v2-ccc2dc69a72dfc68e926e5c563a6308e_r.jp](https://pic3.zhimg.com/v2-ccc2dc69a72dfc68e926e5c563a6308e_r.jpg)

在/include/function/common.php文件下存在对__template函数的调用：

![v2-ac44305cb3abe6563ff31ff1c7b85385_r.jp](https://pic3.zhimg.com/v2-ac44305cb3abe6563ff31ff1c7b85385_r.jpg)

最后就是看有哪些地方调用了template函数：

![v2-7a443cf562e71c57a36700ad4dfb37a9_r.jp](https://pic2.zhimg.com/v2-7a443cf562e71c57a36700ad4dfb37a9_r.jpg)

这些调用基本都是进行模板加载的位置，我们先随便找一处：（团购信息提交）

![v2-757e16af8c936e086e16d52eb52366e1_r.jp](https://pic3.zhimg.com/v2-757e16af8c936e086e16d52eb52366e1_r.jpg)

接下来还是要开启debug，然后跟踪一下程序执行的逻辑：

  1. 访问链接，触发模板解析函数：注意此处采用的include的方式进行模板加载。  

![v2-0bba94b0af61d7895ef35ca76bb1c1f3_r.jp](https://pic2.zhimg.com/v2-0bba94b0af61d7895ef35ca76bb1c1f3_r.jpg)

2、进入template函数之后，会根据传递的参数加载不同的模板。

![v2-25a454b968c3c3e1e998138f37c84993_r.jp](https://pic2.zhimg.com/v2-25a454b968c3c3e1e998138f37c84993_r.jpg)

3、当进入__template函数之后要先根据传递的参数加载模板的绝对位置，这里注意，存在一个模板和一个编译后的模板，模板是.html文件，而编译后的模板是.php文件，程序在此处将模板文件路径存在变量$tfile，编译后的模板文件路径存在变量$cFile，之后会利用filemtime函数来比较两个文件的修改时间，如果模板的修改时间小于编译后的模板文件，那说明已经对模板进行过编译，直接返回编译后的模板文件路径。反之才会调用__parse函数对模板进行重新编译。

![v2-5fcf51f55ca764447e1ffff26a405bd6_r.jp](https://pic2.zhimg.com/v2-5fcf51f55ca764447e1ffff26a405bd6_r.jpg)

根据上面的分析，我们要找到可以修改模板的功能点，不然此处漏洞便无法利用，因为无法满足文件修改时间的检查，除非站长刚好改了模板文件。不过一般站点都提供了模板修改功能，这个CMS也不例外：

![v2-54f937a05dee25edf9e8db3076f67947_r.jp](https://pic2.zhimg.com/v2-54f937a05dee25edf9e8db3076f67947_r.jpg)

既然后台可以修改模板文件，那就保证模板文件修改时间大于编译后的模板文件，这样就会进入重新编译环节。

![v2-77e79eaf8f***e51ffd14c2387ade859_r.jp](https://pic4.zhimg.com/v2-77e79eaf8f***e51ffd14c2387ade859_r.jpg)

我们通过第20行的preg_replace来进行分析：

preg_replace("/\<\\!\\-\\-\s*\\\\\$\\{(.+?)\\}\s*\\-\\-\>/ies",
"__replace('<?php \\\1; ?>')", $fileContent);

![v2-8cadfa733ed771027abed1d02f946ee5_r.jp](https://pic2.zhimg.com/v2-8cadfa733ed771027abed1d02f946ee5_r.jpg)

这个正则表达式会怎么匹配不太好说，直接举一下编译前和编译后的栗子出来就能明白了：

![v2-c47618a9a939cf6e8078595af0f925b6_r.jp](https://pic4.zhimg.com/v2-c47618a9a939cf6e8078595af0f925b6_r.jpg)

![v2-94b3d74083bfb5688190a455aeb2160e_r.jp](https://pic2.zhimg.com/v2-94b3d74083bfb5688190a455aeb2160e_r.jpg)

上面那个正则是如何处理的应该就清楚了。接下来还是继续debug，跟踪模板渲染的具体逻辑：

![v2-004f353debad46082990e159c15b092e_r.jp](https://pic2.zhimg.com/v2-004f353debad46082990e159c15b092e_r.jpg)

通过正则表达式将模板进行渲染，然后通过file_put_content函数将内容全部写入到渲染后的模板，写入成功则返回true。

![v2-aaa9644d2cbe9abbbf65651798985bfd_r.jp](https://pic3.zhimg.com/v2-aaa9644d2cbe9abbbf65651798985bfd_r.jpg)

值得注意的是最后返回的是渲染后的模板的物理路径，然后通过include方式加载模板，此时可以看到模板已经通过正则全部替换为php代码。

![v2-0bc32b9b801c12c1972b1053f689676c_r.jp](https://pic3.zhimg.com/v2-0bc32b9b801c12c1972b1053f689676c_r.jpg)

在这个地方存在一个之前的想法错误，其实并不是通过preg_replace来进行代码执行，因为通过/e参数调用的函数是__replace方法，只进行了简单的替换，最后还是通过文件包含的方法来包含存在恶意代码的模板。

![v2-5ae714c353edab0fcaa3dde913e30121_r.jp](https://pic2.zhimg.com/v2-5ae714c353edab0fcaa3dde913e30121_r.jpg)

![v2-bde2af761f393620d0de203ef148f032_r.jp](https://pic1.zhimg.com/v2-bde2af761f393620d0de203ef148f032_r.jpg)

既然已经清楚模板渲染的流程，接下来尝试getshell操作，首先将模板修改成如下形式：记得闭合双引号，括号等等。

![v2-e18055b3368fff71a58b2d4bb98a37fa_r.jp](https://pic4.zhimg.com/v2-e18055b3368fff71a58b2d4bb98a37fa_r.jpg)

通过编译函数之后模板应该是下面这个样子的：

![v2-66164c810ad3ccdef66deb4ac373e2cc_r.jp](https://pic1.zhimg.com/v2-66164c810ad3ccdef66deb4ac373e2cc_r.jpg)

最后通过include包含这个含有恶意代码的模板：

![v2-82f519c96749dc2b7027fb706fdf5c9f_r.jp](https://pic4.zhimg.com/v2-82f519c96749dc2b7027fb706fdf5c9f_r.jpg)

## 0x04数据库备份getshell：  

在一般系统中通常会存在数据库备份的功能，在渗透测试中利用数据库备份getshell也是常用操作，在这个CMS系统中同样发现了数据库备份与还原功能。

![v2-641a6d6fd8b16033bff19a09f2e223ef_r.jp](https://pic3.zhimg.com/v2-641a6d6fd8b16033bff19a09f2e223ef_r.jpg)

但是此处数据库备份的文件是默认的用户不可控的，未发现将恶意代码备份到.php文件当中的操作：

![v2-6b97cdd9f250df7941180a64945b64b7_r.jp](https://pic1.zhimg.com/v2-6b97cdd9f250df7941180a64945b64b7_r.jpg)

但是在之后对从本地文件恢复数据库的功能进行审计发现，此处存在任意SQL语句执行，相当于给我们提供了一个执行任意SQL语句的接口，那么便可以尝试通过SQL命令导出文件getshell和MySQL日志getshell。先来看一下程序逻辑：

在数据库恢复功能提供了从本地文件恢复的功能：

![v2-09afd387f02d497801cd4d62faa7c702_r.jp](https://pic1.zhimg.com/v2-09afd387f02d497801cd4d62faa7c702_r.jpg)

当本地文件上传到服务器，会通过一个backup_import的函数执行文件内的SQL语句：

![v2-796c6ec1ebefdf09af4bc4c8d00a65e3_r.jp](https://pic1.zhimg.com/v2-796c6ec1ebefdf09af4bc4c8d00a65e3_r.jpg)

我们跟踪一下这个函数：

![v2-584b6dff248cf7a7b95e99fd86e36d01_r.jp](https://pic2.zhimg.com/v2-584b6dff248cf7a7b95e99fd86e36d01_r.jpg)

可以看到从文件中读取到SQL语句之后只去掉了几个特殊符号，便通过DB::Query方法直接执行，其中可以再看一下Query方法：未经过任何处理，直接执行SQL语句。

![v2-0a5dcf76799eda20307099f1bec4574d_r.jp](https://pic3.zhimg.com/v2-0a5dcf76799eda20307099f1bec4574d_r.jpg)

已经明白程序的运行逻辑，那么我们便只要构造可以getshell的SQL语句，然后通过备份还原的功能执行SQL语句便能够成功getshell。

上面说MySQL有两种常用的方法getshell：文件导出和日志记录。因为新版的MySQL添加了secure_file_priv参数对文件导入导出进行了限制，这个参数需要修改数据库配置文件，利用困难。

![v2-f2d06d45c15cb4ec6fe44ba428dced5c_r.jp](https://pic1.zhimg.com/v2-f2d06d45c15cb4ec6fe44ba428dced5c_r.jpg)

所以为了提高成功率优先选择利用日志功能getshell。这里还是先介绍一下利用log日志getshell。在MySQL日志功能中：

  1. General_log 指的是日志保存状态，一共有两个值（ON/OFF）ON代表开启 OFF代表关闭。  

  2. General_log_file 指的是日志的保存路径。  

  3. 关于开启general_log参数的作用：  

  4. 开启它可以记录用户输入的每条命令，会把其保存再general_log_file指定的目录下，就是日志文件。这个参数是可以直接通过mysqld进行设置。  

  5. 我们的利用的思路是开启general_log之后把general_log_file的值修改为我们网站默认路径下一个自定义的php文件中，然后我们通过log日志进行写入一句话后门到上面去，然后再进一步利用。  

通过上面的介绍我们知道要实现日志getshell，要做的以下三步：开启日志功能，重定义日志输出文件（需要绝对路径），执行恶意SQL语句写入日志，具体SQL语句如下：

![v2-5824c9db2613b2a30276a4717c9f60ff_r.jp](https://pic1.zhimg.com/v2-5824c9db2613b2a30276a4717c9f60ff_r.jpg)

之后上传文件执行SQL语句，然后在之前设置的日志路径下便可以看到带有恶意payload的日志文件了：

![v2-c0b9fb3548ec42635c8539bb163c3461_r.jp](https://pic2.zhimg.com/v2-c0b9fb3548ec42635c8539bb163c3461_r.jpg)

![v2-d5dc7f0a08d69563890422aee57fdbd8_r.jp](https://pic4.zhimg.com/v2-d5dc7f0a08d69563890422aee57fdbd8_r.jpg)

访问一下链接，成功getshell

![v2-4c02efb47025d9477eb3ff16166d234b_r.jp](https://pic1.zhimg.com/v2-4c02efb47025d9477eb3ff16166d234b_r.jpg)

## 0x05 收尾：  

还是来点骚话收尾，上述只是我找到的一些getshell的操作，肯定还会有其他getshll的操作没有被我发现。但是用代码审计的方式从代码角度去看待漏洞形成的原因对漏洞的理解还是有很大帮助的，还是那句话，代码审计一时爽，一直审计一直爽，大家也可以加入代码审计的大军，有兴趣和我这个菜鸡一起成长进步。

![v2-4636d78596d9b23decd2ab67c9ada165_r.jp](https://pic2.zhimg.com/v2-4636d78596d9b23decd2ab67c9ada165_r.jpg)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

