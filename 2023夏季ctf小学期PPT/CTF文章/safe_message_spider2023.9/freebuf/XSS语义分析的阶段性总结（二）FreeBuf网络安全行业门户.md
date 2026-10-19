原创 Kale 合天智汇

### 前言  

上次分享了javascript语义分析，并且简单介绍了新型xss扫描器的一些想法，如何在不进行大量fuzz的情况下又能准确的检测出xss漏洞，这其中我们又可以尽量的避免触发waf的xss防护功能！

首先先接着上文介绍一下html语义分析的方法。

### 扫描思路  

### HTML语义分析  

如果把html语义分析看为对html结构的解析与识别，在python中我们可以使用HTMLParser，对，又是python帮我解决了难题。在XSStrike里面同样使用了自定义的HTMLParser进行漏洞的辅助识别。

我们可以通过继承HTMLParser并重载其方法来实现我们需要的功能

下面是简单的 HTML 解析器的一个基本示例，使用 [HTMLParser](https://docs.python.org/zh-cn/3/library/html.parser.html#html.parser.HTMLParser)
类，当遇到开始标记、结束标记以及数据的时候将内容打印出来

    
    
    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            print("Encountered a start tag:", tag)
    
        def handle_endtag(self, tag):
            print("Encountered an end tag :", tag)
    
        def handle_data(self, data):
            print("Encountered some data  :", data)
    
    parser = MyHTMLParser()
    parser.feed('<html><head><title>Test</title></head>'
                '<body><h1>Parse me!</h1></body></html>')

![v2-c083579ad1d523f46b59e2d4dfe502e7_720w](https://pic2.zhimg.com/80/v2-c083579ad1d523f46b59e2d4dfe502e7_720w.png)

我们需要定义一个我们自己的HTML解析器来处理我们的标签，标识出来script标签，html注释，html标签，属性，css等等

部分代码如下

![v2-207155344567a865d7319d69178c64ce_720w](https://pic1.zhimg.com/80/v2-207155344567a865d7319d69178c64ce_720w.png)

寻找反射点的思路和js的类似，通过遍历标签来来解析html结构，tagname代表标签名，attibutes代表属性，content代表数据内容，#comment代表注释，每个标签被封装为字典形式的列表元素

使用以下的demo

    
    
        <body>
        <a href="?q=1&w=2&e=3&r=4&t=5">test</a>
        <style>
        body{
            background:#aaaflag{111222};
        }
        </style>
        <script>
        var a = 'xx';flag{111222}</script>
        <div>
        <textarea>flag{111222}</TexTarea>kkk
        </div>ffff<aaaaa>bb
        <input style="color:flag{111222}" value2="flag{111222}" aflag{111222}="aaa"/>
            <!--                this is comment
                5flag{111222}
                        -->
        </body>
        </html>

处理后的效果

![v2-14f5eabed18c73c821f4c28fdb568f61_720w](https://pic4.zhimg.com/80/v2-14f5eabed18c73c821f4c28fdb568f61_720w.png)

处理完html标签，接下该寻找sink输出点在html的上下文。思路跟js的寻找思路是相同的

通过遍历列表内容来找到我们的input，部分代码如下：

![v2-22737531e5d59078da5b3bacbf4c00ee_720w](https://pic2.zhimg.com/80/v2-22737531e5d59078da5b3bacbf4c00ee_720w.png)

最后会给出输出点上下文的一些细节信息，如是否是html标签等等

![v2-6f715684fa826cb08307ce99bba781b6_720w](https://pic1.zhimg.com/80/v2-6f715684fa826cb08307ce99bba781b6_720w.png)

然后根据不同的上下文给出我们的payload，使用html语法树有很多好处，比如可以准确判断回显的位置

### 探究发包  

X3Scan的扫描思路参考了一些xray的扫描思路，比如不发送一些产生危害的payload，只根据回显的上下文发送一些flag测试一些关键字符是否被转义和过滤，如<>,".',()等，如果没有过滤最后给出建议payload，如：confirm()

首先对于无法使用html和js解析的回显，如jsonp和json格式的相应包，我们使用如下的发包顺序：

随机flag ---》判断回显 ----》解析找不到回显 ---》发送<随机flag> \---》判断响应包中字符是否转义---》给出payload

最后给出<img src=1>的payload，对与jsonp_xss这里有一个tip，正常情况下判断jsonp_xss，会首先判断content-type是包含text/html，然后继续测试，实际测试中当content-type为空时，也可能存在xss漏洞，因此应该对两种情况都进行一下判断。

    
    
    if 'html' in (resp_headers.get("content-type","").lower()) or resp_headers.get("content-type")==None:

对于html标签内的内容

<h2>xxxxx</h2>

扫描器会依次发送0xb9d8c，</H2><mowvhry>当确认标签可以闭合，会给出</h2><img src=1>

![v2-e28da8eb8444c1cde46f01d04a8e8a3c_720w](https://pic1.zhimg.com/80/v2-e28da8eb8444c1cde46f01d04a8e8a3c_720w.png)

对于标签属性

demo:https://brutelogic.com.br/xss.php?b3=

扫描器会依次发送0xb78123，'psafq='，'><arcbvyf>，"psafq="，"><arcbvyf>，当确认引号和尖括号没有被过滤时，最终给出"><img
src=1>，"OnMoUsEoVeR=confirm()//。

![v2-586988ffedba850fe83b87fbe1c84663_720w](https://pic2.zhimg.com/80/v2-586988ffedba850fe83b87fbe1c84663_720w.png)

对于html注释

<!-- this is comment <?php echo $t;?> \-->

扫描器会依次发送0xfda748，--><aorxlwd>，--!><aorxlwd>，当确定-->或--!>没有过滤时，给出payload，--><aorxlwd>

对于script标签的回显

扫描器会依次发送0x829a5c，-829a5c-，</sCRiPt><sCRiPt>dncjbwv</sCRiPt>，当最后确认</sCrIpT>未被过滤时，最终给出payload，</sCRiPt><sCRiPt>confirm()</sCRiPt>

另外一种情况就是回显到script标签的注释里面

使用以下demo

    
    
    <html> <body> 
    <script> 
    var a = 1; 
    // inline <?php echo $_GET["a"];?> 
    /* 
    <?php echo $_GET["b"];?> */ 
    </script> 
    </body> 
    </html

扫描器会依次发出0x829a5c，-829a5c-，</sCRiPt><sCRiPt>dncjbwv</sCRiPt>，\n;rmhwe;//，最后给出payload，</sCRiPt><sCRiPt>confirm()</sCRiPt>,/n;prompt(1);//。

对于块注释，扫描器会依次发出，0xc13f，*/0xc13f;/*，最后给出payload，*/prompt(1);/*

通过上面的分析，我们可以发现使用html语法树有很多好处，比如通过发送一个随机payload，例如：<wrqweew>,然后通过html语法树检测是否有wrqweew这个标签，便可以确定payload是否执行成功了。

对于回显在js的情况，发送测试payload后，通过js语法树解析确定Identifier和Literal这两个类型中是否包含，如果payload是Identifier类型，就可以直接判断存在xss，最后给出payload，confirm();//。如果payload是Literal类型，再通过单双引号来测试是否可以闭合。

另外，还有一些比较精致的技巧，比如对payload的随机大小写，由于html对大小写是不敏感的，但是一些waf由于设计缺陷能会被绕过。

### 大致流程  

扫描器大致流程：

    
    
    发送随机字符--》确认参数回显---》通过html/js解析确认回显位置--》根据回显的上下文发送不同的payload进行测试--》使用html，js语法树解析是否多出来标签，属性，js语句等来确定是否执行成功

### 成果展示  

由于一直处于开发阶段，并没进行大规模测试，但是偶尔也会有个小惊喜，某次调bug的时候发现京东某站的xss

![v2-8e2386afe933ca3a1bb7b0228f05c314_720w](https://pic4.zhimg.com/80/v2-8e2386afe933ca3a1bb7b0228f05c314_720w.png)

实验推荐：

XSS进阶二

<http://hetianlab.com/expc.do?ce=ae2460c3-845b-4aa3-a38a-976ca41f62f7>

（恶意攻击者往Web页面里插入恶意html代码，当用户浏览该页之时，嵌入其中Web里面的html代码会被执行，从而形成XSS攻击）"

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

