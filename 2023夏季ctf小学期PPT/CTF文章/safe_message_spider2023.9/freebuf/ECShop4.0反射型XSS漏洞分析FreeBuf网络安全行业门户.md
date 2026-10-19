***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：Cyc1ing，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **前言：
Ecshop是国内的一款开源的电商框架，在国内应用较为广泛，当前最新版本为4.0.0，最近对其代码进行了简单的分析，发现可以绕过其filter触发XSS。**

##  **一、漏洞利用方式**

发送GET请求包如下：

    
    
    GET/CMS/ECShop_V4.0./user.php HTTP/1.1Referer:https://127.0.0.1" /><a href=javascript:alert('Cyc1e_test')><imgsrc="xxxxxUser-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko)Chrome/41.0.2228.0 Safari/537.21Cookie:ECS_ID=17b608d2a679cf2c7e8611581478e6929dbfb34b;ECS[visit_times]=2Connection:keep-aliveAccept: */*Accept-Encoding:gzip,deflateHost: 127.0.0.1
    

其中漏洞触发代码为：

    
    
    Referer:https://127.0.0.1" /><ahref=javascript:alert('Cyc1e_test')><imgsrc="xxxxx
    

实现绕过过滤规则，触发XSS漏洞的效果。

##  **二、相关环境**

版本：ECShop4.0.0

漏洞类型：反射型XSS

本地环境：php5.6.27+ Apache + Mysql

##  **三、漏洞分析**

该XSS漏洞路口点在user.php文件，查看user.php：328行

![user.php](https://image.3001.net/images/20190313/1552477638_5c88edc60620d.jpg!small)

在用户登入界面的处理代码中，首先变量$action赋值为login进入主体代码，若变量$back_act为空并且请求包中存在REFERER字段，则将REFERER字段中的内容赋值给变量$back_act，这是导致该漏洞的直接原因，对$back_act变量赋值过后传入assign函数进行处理，其中$smarty是模版类cls_template的实例化：/includes/init.php：170行

![/includes/init.php](https://image.3001.net/images/20190313/1552477009_5c88eb51d6c7c.jpg!small)

所以查看assign函数时跟进到模版类cls_template中查看：/includes/ cls_template.php：70行![/includes/
cls_template.php](https://image.3001.net/images/20190313/1552477026_5c88eb625619c.jpg!small)对传入变量名和变量值进行变量注册，我们可以传入非数组数据对$back_act进行变量注册，注册完毕回到user.php代码，继续跟进模版类中的display函数：/includes/
cls_template.php：100行![/includes/
cls_template.php](https://image.3001.net/images/20190313/1552477056_5c88eb8005ff8.jpg!small)调用fetch函数进行user_passport.dwt文件的页面显示，也就是显示用户登入页面，其中在user_passport.dwt文件中：![user_passport.dwt](https://image.3001.net/images/20190313/1552477077_5c88eb956422e.jpg!small)$back_act值被赋值给input标签中的value,所以我们控制了$back_act变量值便可以在html页面中插入js代码。

 **四、绕过全局Waf触发XSS**

Ecshop中定义了全局安全过滤规则，查看代码：/includes/safety.php![/includes/safety.php](https://image.3001.net/images/20190313/1552477103_5c88ebaf683f5.jpg!small)这个过滤规则比较简单粗暴，利用’on[a-zA-Z]{3,15}’
过滤了所有的on开头js事件，所以用事件触发是较为困难了，并且<script、alert、eval、data、Javascript等敏感字符，继续查看代码：

![E7.jpg](https://image.3001.net/images/20190313/1552477834_5c88ee8ae76b7.jpg!small)

$back_act的值如果不是数组便传入filter()函数中利用preg_match进行字符校验，这里利用了/i，所以不区分大小写，无法利用大小写的方式进行绕过，不过这里的敏感字符过滤也不全，例如对于弹窗的js函数confirm就可以被利用，所以主要考虑的是如何绕过过滤检测。

我利用了HTML的实体编码来进行绕过，在 HTML
中，某些字符是预留的，比如不能使用小于号（<）和大于号（>），这是因为浏览器会误认为它们是标签。如果希望正确地显示预留字符，我们必须在 HTML
源代码中使用字符实体，如需显示小于号，我们必须这样写：< 或 <，其中'< '便是小于号（<）的HTML实体编码，并且不仅是 "<"">"
这样的能编码，所有字符均能编码，a-zA-Z的HTML实体编码方式是&#[字符ACCII编码]，例如a->a。

所以可以利用这一编码方式进行构造POC：

    
    
    Referer: [https://127.0.0.1](https://127.0.0.1)"/><a href=javascript:alert('Cyc1e_test')><imgsrc="xxxxx
    

其中javascript:alert('Cyc1e_test')可以绕过xss过滤规则的匹配从而绕过服务端的安全过滤植入html页面中，经过html编码解析会恢复成javascript:alert('Cyc1e_test')，从而触发执行，效果如图：

![XSS代码植入](https://image.3001.net/images/20190313/1552477204_5c88ec14084fc.jpg!small)通过点击图片可以直接触发

![XSS代码执行](https://image.3001.net/images/20190313/1552477221_5c88ec25b04c9.jpg!small)

漏洞绕过触发的方式不唯一。

##  **五、总结**

漏洞挖掘主要在于一定的技术基础，充分的经验积累以及一些运气所在，挖掘的漏洞不在大小，每一漏洞都是一次成长，新手挖掘文章，希望大牛们批评指正。

 ***本文原创作者：Cyc1ing，本文属FreeBuf原创奖励计划，未经许可禁止转载**

