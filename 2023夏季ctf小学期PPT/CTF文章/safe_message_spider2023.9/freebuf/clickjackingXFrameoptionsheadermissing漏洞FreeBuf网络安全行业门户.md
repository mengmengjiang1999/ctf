## 1.漏洞简介：

clickjacking:X-Frame-options header missing，这个漏洞是由于缺少X-Frame-options头部信息造成的点击劫持

`X-Frame-Options`HTTP报头字段表示策略，以确定是否在浏览器内允许插入`frame`或`iframe框架`。服务器可以在其HTTP响应的标头中声明此策略，以防止点击劫持攻击，从而确保其内容不会嵌入其他页面或框架中。

## 2.攻击方式：

攻击者使用多层透明或不透明层，诱使用户在打算单击顶层页面时诱使他们单击框架页面上的按钮或链接。因此，攻击者正在“劫持”用于其页面的点击，并将其路由到其他页面，该页面很可能由另一个应用程序，域或两者拥有。

使用类似的技术，击键也可以被劫持。通过精心设计的样式表，iframe和文本框的组合，可以使用户相信他们是在电子邮件或银行帐户中输入密码，而是输入由攻击者控制的不可见框架。

攻击者通过

(1).利用有该漏洞的网站（例如：www.haveXFO.com,假设该网站有这样一个漏洞），编写一个可获取用户敏感信息的网页（如，cookie.html）,

(2)然后将cookie.html内嵌到www.haveXFO.com/index.html中（在内嵌的时候将cookie.html的css模式进行精心调整，一般调整为透明模式便于黑客将cookie.html隐藏到www.haveXFO.com/index.html）

(3)黑客将这样一个精心编写好的网页(并命名为attack.html,attcck.html是由index.html与cookie.html构成的)发布到自己的服务器上（www.hackerxxxx.com/attack.html）

(4)将这样一个钓鱼链接www.hackerxxxx.com/attack.html发送给受害者们，等待鱼儿上钩即可

## 3.防御方法：

在HTTP响应标头中发送适当的X-Frame-Options，以指示浏览器不允许来自其他域的框架。

  * `X-Frame-Options: DENY`它完全拒绝在frame / iframe中加载。

  * `X-Frame-Options: SAMEORIGIN`仅当要加载的站点具有相同来源时才允许。

  * `X-Frame-Options: ALLOW-FROM URL`它授予特定的网址以将自身加载到iframe中。但是请注意，并非所有浏览器都支持此功能

## 4.演示对比：

在这里我们找到了两个网站做对比：  
（1）.www.google.com,该网站使用了，X-Frame-Options: SAMEORIGIN头部信息，我们无法编写内嵌攻击网页：

具体演示代码：

    
    
    <!DOCTYPE  html >
    <html>
    <head>
      <meta  charset ="utf-8" >
      <meta  name ="viewport"  content ="width=device-width" >
      <title > IFrame Example </title >
      <style >
        iframe { width: 480px; height: 300px; }
      </style >
    </head >
    <body >
      <iframe  src ="https://www.google.com"/>
    </body >
    </html >

展示效果：

![1611209390_60091aaeea917ebc20ff2.png!small](https://image.3001.net/images/20210121/1611209390_60091aaeea917ebc20ff2.png!small)

  

![1611209397_60091ab5f0314f1e82b08.png!small](https://image.3001.net/images/20210121/1611209397_60091ab5f0314f1e82b08.png!small)

这里由于www.google.com采用了X-Frame-Options: SAMEORIGIN，使得我们无法进行攻击，

（2）.下面我们到了找一个未采用X-Frame-Options的网站进行演示

代码如下：

    
    
    <html>
    <head>
    <title> Clickjack测试页</title>
    </head>
    <body>
    <p>网站容易受到点击劫持的影响！</p>
    <iframe src ="http://www.xxxxxx.com/" width ="500" height ="500"> </iframe>
    </body>
    <html>

![1611209479_60091b074bf28725b71b3.png!small](https://image.3001.net/images/20210121/1611209479_60091b074bf28725b71b3.png!small)

![1611209489_60091b118d18ab4d04274.png!small](https://image.3001.net/images/20210121/1611209489_60091b118d18ab4d04274.png!small)

在这样一个网站中，我们可以从回应的信息中，可以看到并未采用X-Frame-Options，这就使得黑客有了可趁之机。

