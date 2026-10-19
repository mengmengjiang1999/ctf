***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **上一次在《[WordPress插件Form Maker
SQL注入漏洞分析](https://www.freebuf.com/vuls/205290.html)》中主要分析了Wordpress插件的注入漏洞，这个漏洞可以获取用户网站敏感信息，但是在网站服务器突破方面比较鸡肋。最近WordPress的另一个插件（真的是插件多如牛毛）insert
or embed articulate
content爆出远程代码执行漏洞，在登陆网站后可通过zip压缩文件上传php后门，我就突然想到这两个插件的漏洞组合起来就很完美了。**

## Insert or Embed articulate content插件介绍

插件官网：<https://wordpress.org/plugins/insert-or-embed-articulate-content-into-wordpress/>

该插件主要是可以快速的向文章中嵌入自己的学习内容(e-Learing)，同时该插件可以直接对zip压缩文件进行处理，文件可以先压缩到zip中再一起上传到服务器中。

## 测试环境

本地测试环境为 WordPress5.1 + Insert or Embed articulate content4.2995(一下简称IEAC)

## 漏洞复现

step1：通过插件上传在WordPress中安装存在漏洞的插件 Insert or Embed articulate content

step2：准备一个php后门脚本并压缩到poc.zip中，在这里我用的最简单的一句话：

    
    
      <?php eval($_POST[]);?>

step3：以任意用户登陆Wordpress选择 '文章—>写文章—>添加区块—>e-Learining'

![WordPress插件IEAC漏洞分析及组合利用尝试](https://image.3001.net/images/20190612/1560309609_5d006f6995092.png!small)

step4:在上传功能中选择准备好的poc.zip，并上传该文件

![捕获.PNG](https://image.3001.net/images/20190612/1560309851_5d00705b90057.png!small)

step5:连接后门文件:<http://website/>wp-content/uploads/articulate_uploads/poc/test.php

![WordPress插件IEAC漏洞分析及组合利用尝试](https://image.3001.net/images/20190612/1560310689_5d0073a1b414b.png!small)可以直接连接到后台进行文件管理，压缩包里的文件被成功解压到目标文件夹内。

## 漏洞分析

下载插件源码后分析了一下该插件漏洞点以及存在的问题。

在源码程序中搜索处理zip压缩包的函数全部集中在functions.php文件中：

![WordPress插件IEAC漏洞分析及组合利用尝试](https://image.3001.net/images/20190612/1560310984_5d0074c8d512d.png!small)在对源码审计后发现插件接收zip压缩包之后对压缩包文件名进行了过滤，但是对压缩包的内容没有进行过滤，直接解压到了目标文件下

    
    
    /functions.php
        ...    
        $dir = explode(".",$fileName);  
        $dir[0] = str_replace(" ","_",$dir[0]);         
        $target = getUploadsPath().$dir[0];  
        $file = $filePath ;            
        while(file_exists($target))  
        {  
        $r = rand(1,10);  
        $target .= $r;  
        $dir[0] .= $r;  
        }  
        $arr = extractZip($file,$target,$dir[0]);
        ...  
    
    
    
    /functions.php
      function extractZip($fileName,$target,$dir){
          add_filter('admin_memory_limit', 'articulate_run_admin_memory_limit_hook', 100, 1 );
          #admin_memory_limit hook is called in wp_raise_memory_limit function that is called in unzip_file function.   $arr = array();
          $unzipper = new Quiz_Unzip( true );
          $unzip = $unzipper->unzip_file( $fileName, $target );
          ...
      }

解压目标目录为/wp-content/uploads/articulate_uploads，没有设置任何访问限制，任意用户都可以直接访问。

    
    
        define('WP_CONTENT_DIR_NAME','wp-content'); #CHANGE THIS IF YOUR content directory is defferent.  
        define('WP_UPLOADS_DIR_NAME','uploads');  
        define('WP_QUIZ_EMBEDER_UPLOADS_DIR_NAME','articulate_uploads');  
        define('WP_QUIZ_EMBEDER_CAPABILITY','edit_posts');

## 漏洞组合尝试

首先回顾一下[WordPress插件Form
Maker](https://www.freebuf.com/vuls/205290.html?preview=true)的使用及影响:

> CVE-2019-10866：可利用有效登陆用户通过sql注入获取服务器敏感信息

一开始的组合利用思路： _首先通过插件Form
Maker的漏洞利用低权限的用户通过注入获得管理员用户，然后以管理员身份登陆网站安装插件IEAC，在上传后门并控制服务器_ 。（一切想的如此美好）

但是在利用Form Maker漏洞进行注入的时候发现了问题：

>
> 在上一篇对该插件漏洞分析时并没有分析用户登陆部分的影响，经过验证该插件能够成功注入并获取敏感数据的账户必须是Administrtor！！！（无语了很久），其他类型的用户在进行注入尝试时全部会显示403错误（通常由于服务器上文件或目录的权限设置导致的WEB访问错误）。

在这里先学习一下WordPress中的角色分配：

>  **WORDPRESS自身的用户角色**  
>
>
> 仅指Wordpress安装时就有的几种用户角色(所列为角色名称)：
>
> Subscriber：订阅者
>
> Contributor ：投稿者
>
> Author ：作者
>
> Editor ：编辑
>
> Administrator ：管理员
>
> 此外，如果启用了Wordpress多站，将会多出一种用户角色：Super Admin（超级管理员）。

再回到IEAC这个插件漏洞上来，这个插件漏洞也需要用户登陆，在进行验证后除了订阅者之外其他类型的用户均可以利用这个漏洞，但是除了管理员外的用户是无权对网站的插件进行安装移除的。也就是说这个漏洞可以不用管理员账户就可以触发（不知为何要进行漏洞组合尝试的我在风中凌乱）。

## 结语

WordPress插件的漏洞近期出现了很多，从注入到远程代码执行还有网站重定向等等。当初想进行漏洞组合利用也是想根据不同漏洞的特点相互弥补不足，但是可能是因为漏洞研究做的还不够细致（就是太菜），最终结果并不是很理想，但是我认为这种利用
**多个插件组合攻击**
的方式还是值得研究与警惕的。大家如果有什么更好的组合方式可以留言评论，相互学习。以上，如果有不对的地方也希望大家主动私信，我们共同进步。

 ***本文作者：Kriston，本文属FreeBuf原创奖励计划，未经许可禁止转载。**

