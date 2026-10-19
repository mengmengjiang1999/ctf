![](https://image.3001.net/images/20200806/1596654366.jpg!small)

## 写在前面的话

就在不久之前，Wordfence的威胁情报团队在一款名叫wpDiscuz的Wordpress评论插件中发现了一个高危漏洞，而这款插件目前已有超过80000个网站在使用了。这个漏洞将允许未经认证的攻击者在目标站点中上传任意文件，其中也包括PHP文件，该漏洞甚至还允许攻击者在目标站点的服务器中实现远程代码执行。

## 漏洞简述

> 漏洞描述：任意文件上传
>
> 受影响插件：评论插件– wpDiscuz
>
> 受影响版本：7.0.0 – 7.0.4
>
> CVSS评分: 10.0 (严重)
>
> CVSS Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
>
> 修复版本：7.0.5

一直以来，WordPress自带的评论功能都是非常简单基础的，不能够满足对评论互动比较重视的网站。wpDiscuz是一款非常好用的WordPress评论增强插件，并且提供了自定义评论表单和字段的AJAX实时评论系统，旨在增强WordPress内置评论功能。在该插件的7.x.x版本中，wpDiscuz新增了在评论中上传图片附件的功能，但不幸的是，该功能的实现缺乏安全保护，从而导致了该漏洞的出现。

wpDiscuz的评论只允许用户上传图片附件，但由于其使用的文件MIME类型检测函数没有对文件类型进行正确验证，因此未经身份验证的用户将能够上传任何类型的文件，其中也包括PHP文件。

## 检查文件MIME类型

getMimeType函数使用了三种不同的方法来检测一个文件的MIME类型。第一个方法为mime_content_type，它能够根据文件的内容来判断文件类型。如果PHP函数无法使用，它将会使用finfo_file方法，这个方法同样能够根据文件的内容来判断文件类型。最后，如果这个方法仍然无法使用的话，它将会使用wp_check_filetype方法，这个方法是WordPress指定的文件类型检测方法，它能够根据文件名来检测文件的MIME类型，并于内置的文件类型白名单列表进行匹配。

从字节角度来看，大多数文件的起始字节都是一些特定的签名，我们可以通过这些字节来判断文件的MIME类型。但是，PHP在处理文件时，会忽略<?php标签前面的所有内容。因此，前两个检测函数所使用的方法就可以通过添加图片类型的签名字节来绕过了。比如说，用户可以在PHP文件的开头加入png文件的签名字节，比如说“89
50 4E 47 0D 0A 1A 0A”，这样就能绕过前两个检测函数了。

    
    
    foreach ($files as $file) {
    
      $error = false;
    
      $extension = pathinfo($file["name"], PATHINFO_EXTENSION);
    
      $mimeType = $this->getMimeType($file, $extension);
    
     
    
    private function getMimeType($file, $extension) {
    
         $mimeType = "";
    
         if (function_exists("mime_content_type")) {
    
             $mimeType = mime_content_type($file["tmp_name"]);
    
         } elseif (function_exists("finfo_open") && function_exists("finfo_file")) {
    
             $finfo = finfo_open(FILEINFO_MIME_TYPE);
    
             $mimeType = finfo_file($finfo, $file["tmp_name"]);
    
         } elseif ($extension) {
    
             $matches = wp_check_filetype($file["name"], $this->options->content["wmuMimeTypes"]);
    
             $mimeType = empty($matches["type"]) ? "" : $matches["type"];
    
         }
    
         return $mimeType;
    
     }

## 验证允许的文件类型

isAllowedFileType函数导致这个漏洞更加严重了，这个函数能够使用getMimeType函数来检测目标文件是否属于允许上传的文件类型。由于这个函数是根据文件内容来判断文件MIME类型的，所以绕过该函数的检测并非难事。

    
    
    private function isAllowedFileType($mimeType) {
    
         $isAllowed = false;
    
         if (!empty($this->options->content["wmuMimeTypes"]) && is_array($this->options->content["wmuMimeTypes"])) {
    
             $isAllowed = in_array($mimeType, $this->options->content["wmuMimeTypes"]);
    
         }
    
         return $isAllowed;
    
     }

## 漏洞利用

这也就意味着，攻击者将能够创建任意文件类型，并添加图形文件标识字节，这样就能够绕过文件内容验证检测了。如果想要利用一个PHP文件来绕过检测的话，请求的大致内容应该如下：

    
    
    ------WebKitFormBoundaryXPeRFAXCS9qPc2sB
    
    Content-Disposition: form-data; name="wmu_files[0]"; filename="myphpfile.php"
    
    Content-Type: application/php
    
     
    
    ‰PNG

文件路径地址会在请求的响应内容中返回，这样用户将能够获取到文件的地址，并访问上传到服务器中的文件。因此，攻击者将能够上传任意PHP文件，并通过访问这些文件来实现在服务器端的任意代码执行。

一旦成功利用该漏洞，攻击者将能够在目标服务器上执行任意代码，遍历目标用户的托管账号，从而利用恶意代码进一步感染该账户中托管的其他站点。

## 总结

在这篇文章中，我们对wpDiscuz插件中的一个高危漏洞进行了详细分析，并介绍了漏洞的利用方法。目前，该漏洞已在wpDiscuz的7.0.5版本中完全修复，因此我们建议广大用户立刻将wpDiscuz插件更新至最新版本。

