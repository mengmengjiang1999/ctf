# 0x01简介

ThinkPHP是一个快速、兼容而且简单的轻量级国产PHP开发框架，诞生于2006年初，原名FCS，2007年元旦正式更名为ThinkPHP，遵循Apache2开源协议发布，从Struts结构移植过来并做了改进和完善，同时也借鉴了国外很多优秀的框架和模式，使用面向对象的开发结构和MVC模式，融合了Struts的思想和TagLib（标签库）、RoR的ORM映射和ActiveRecord模式。

ThinkPHP可以支持windows/Unix/Linux等服务器环境，正式版需要PHP5.0以上版本支持，支持MySql、PgSQL、Sqlite多种数据库以及PDO扩展，ThinkPHP框架本身没有什么特别模块要求，具体的应用系统运行环境要求视开发所涉及的模块。

该漏洞源于ThinkPHP 6.0的某个逻辑漏洞，成功利用此漏洞的攻击者可以实现“任意”文件创建，在特殊场景下可能会导致GetShell。

# 0x02漏洞概述

2020年1月10日，ThinkPHP团队发布一个补丁更新，修复了一处由不安全的SessionId导致的任意文件操作漏洞。该漏洞允许攻击者在目标环境启用session的条件下创建任意文件以及删除任意文件，在特定情况下还可以getshell。

# 0x03影响范围

ThinkPHP6.0.0-6.0.1

# 0x04环境搭建

1.phpstudy中PHP设置成7.2版本，并把对应的文件夹放入环境变量path中

![0089FO1rly1ghvwapzedkj30wv0k3gue.jpg](https://image.3001.net/images/20200819/1597823123.jpg!small)点击此处添加图片说明文字

2.在Phpstudy服务器中打开php.ini文件，找到extension=php_openssl.dll前面的分号去掉，意思是打开ssl扩展，目的是为了能在cmd命令中能进行访问

![0089FO1rly1ghvwaxawk9j30r50gnk2k.jpg](https://image.3001.net/images/20200819/1597823124.jpg!small)点击此处添加图片说明文字

3.安装composer.phar，找到下载内容的地方，去下载当前最新版本的composer.phar

下载地址https://getcomposer.org/download/

![0089FO1rly1ghvwb6r81xj311p0hsqh7.jpg](https://image.3001.net/images/20200819/1597823125.jpg!small)点击此处添加图片说明文字

4\. 双击安装，不用勾选，选择下一步

![0089FO1rly1ghvwbco9j5j30so0gmgrn.jpg](https://image.3001.net/images/20200819/1597823125.jpg!small)点击此处添加图片说明文字

5.配置环境变量后自动选择了

![0089FO1rly1ghvwbjf1adj30m90giq7m.jpg](https://image.3001.net/images/20200819/1597823126.jpg!small)点击此处添加图片说明文字

然后一直下一步，安装完成

![0089FO1rly1ghvwbq8mafj30ma0gk0xe.jpg](https://image.3001.net/images/20200819/1597823127.jpg!small)点击此处添加图片说明文字

输入composer查看是否安装成功

![0089FO1rly1ghvwbx924nj30q30ecjzy.jpg](https://image.3001.net/images/20200819/1597823128.jpg!small)点击此处添加图片说明文字

6.安装tp6 php composer.phar create-project topthink/think tp 6.0.*

![0089FO1rly1ghvwc80gzbj30ul0q27wh.jpg](https://image.3001.net/images/20200819/1597823129.jpg!small)点击此处添加图片说明文字

我这个时间Thinkphp的最新版是6.0.3，用上面的命令下载下来framework是6.0.3版本的，我们需要再执行一条命令，进入下载的目录tp6，使用cmd命令

composer require topthink/framework:6.0.0

![0089FO1rly1ghvwcft6iej30o509fagp.jpg](https://image.3001.net/images/20200819/1597823130.jpg!small)点击此处添加图片说明文字

8\. 浏览器访问一下

![0089FO1rly1ghvwcm14rqj30qu0jg44n.jpg](https://image.3001.net/images/20200819/1597823131.jpg!small)点击此处添加图片说明文字

# 0x05漏洞复现

首先在得到可控session参数名，这是本地构造的，实战需要自己fuzz。

构造位置：tp6\app\controller\index.php

构造的内容

use think\facade\Session;

Session::set('user',$_GET['username']);

![0089FO1rly1ghvwcunpuvj30qi0cu44f.jpg](https://image.3001.net/images/20200819/1597823132.jpg!small)点击此处添加图片说明文字

开启session且写入的session可控，/tp6/app/middleware.php 文件开启session，去掉注释session的//

![0089FO1rly1ghvwd217uej30gs06e77i.jpg](https://image.3001.net/images/20200819/1597823133.jpg!small)点击此处添加图片说明文字

使用Burp抓取首页的包构造payload：username就是我们刚才构造的接受参数，然后将PHPSESSID的值修改为32位的保存路径

![0089FO1rly1ghvwd7pm4tj310u0idwqi.jpg](https://image.3001.net/images/20200819/1597823134.jpg!small)点击此处添加图片说明文字

点击发送，在浏览器访问

![0089FO1rly1ghvwde8o61j312w0mydu2.jpg](https://image.3001.net/images/20200819/1597823135.jpg!small)点击此处添加图片说明文字

# 0x06修复方式

官方给出的修复方式

对session id 加一个过滤 使用 ctype_alnum（）

$this->id = is_string($id) && strlen($id) === 32 ctype_alnum（$id） && ? $id :
md5(microtime(true) . session_create_id());

