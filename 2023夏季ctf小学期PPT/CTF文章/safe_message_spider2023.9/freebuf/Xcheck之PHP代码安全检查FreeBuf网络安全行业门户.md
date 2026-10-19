![1616378737_6057fb7114422e5018868.png!small?1616378737392](https://image.3001.net/images/20210322/1616378737_6057fb7114422e5018868.png!small?1616378737392)

## 1 PHP安全检查引擎

Xcheck的php引擎支持原生php的安全检查，也支持对国内主流框架编写的web应用进行安全检查，覆盖包括
**Thinkphp,Laravel,CodeIgniter,Yii,Yaf**
等web框架，对尚未覆盖的框架如果有需求，Xcheck也可迅速适配。覆盖漏洞类别包括但不限于以下:

  * 命令注入
  * SQL注入
  * XSS
  * XXE
  * URL跳转
  * 路径穿越
  * 反序列化
  * 代码执行
  * 变量覆盖
  * ...  

## 2 简单聊一下RIPS

![1616378782_6057fb9e0540a8cc9424b.png!small?1616378782329](https://image.3001.net/images/20210322/1616378782_6057fb9e0540a8cc9424b.png!small?1616378782329)

说到PHP代码工具化安全审计，就不得不提RIPS。RIPS是国外一家专门做代码安全检查的科技公司，凭借PHP代码安全检查出名。这里说的并不是RIPS的开源版本，因为RIPS的
**开源版本是不支持面向对象的**
，上个开源版本0.55已经是2017年的事情，所以说的是RIPS的商业化版本，了解到前段时间RIPS也已经被SonarSource收购。

![1616378807_6057fbb7ccf409a45bf3e.png!small?1616378808144](https://image.3001.net/images/20210322/1616378807_6057fbb7ccf409a45bf3e.png!small?1616378808144)

我们通过一些渠道接触使用到了RIPS的商用版本，从目前的一些检测结果来看，不得不承认，RIPS相比一些其他我们已经接触使用过的商业化代码安全审计产品，如某marx，RIPS在误报率、速度上都是有一定优势。但尽管RIPS在PHP代码安全审计这一领域研究可能超过10年(10年推出开源0.32版本)，还是会在一些地方有疏漏，
**盲目地迷信权威并不可取** 。

举个简单的例子，这是pikachu靶场里的一段ssrf漏洞代码，RIPS并未检测出这个简单漏洞。

    
    
    <?php  
    $URL = $_GET[1];  
    $CH = curl_init($URL);  
    curl_setopt($CH, CURLOPT_HEADER, FALSE);  
    curl_setopt($CH, CURLOPT_SSL_VERIFYPEER, FALSE);  
    $RES = curl_exec($CH);  
    curl_close($CH) ;  
    echo $RES;

当然，这个例子只是为了说明 **即使是大家公认的权威，也可能存在着不足** 。

至于Xcheck相较于RIPS，我们已知的是 **Xcheck速度和自定义规则具备一定优势**
，RIPS并不支持自定义规则，也就不支持自研框架，例如thinkphp项目对RIPS来说是难以理解的。

## 3 Wpdiscuz任意文件上传漏洞分析与检测

![1616378836_6057fbd4a9d0697a972a2.png!small?1616378837031](https://image.3001.net/images/20210322/1616378836_6057fbd4a9d0697a972a2.png!small?1616378837031)

wpdiscuz是一个wordpress使用较广泛的插件，8月份时爆出一个任意文件上传漏洞。使用RIPS扫描带有漏洞的源码，但并没有发现问题。这里将使用7.0.3带漏洞的版本源码进行分析。

先看下xcheck的检测结果。

![1616378858_6057fbea775b4d541c0f5.png!small?1616378858837](https://image.3001.net/images/20210322/1616378858_6057fbea775b4d541c0f5.png!small?1616378858837)

  1. 污染传入, combineArray函数取出`$_FILES`当中的数据，传递给`$files`![1616378918_6057fc26982285c5c0eee.png!small?1616378919836](https://image.3001.net/images/20210322/1616378918_6057fc26982285c5c0eee.png!small?1616378919836)
  2. 从`$files`中取出数据，并获取了后缀。 **但是这里`$this->getMimeType`并没有对后缀进行判断，而是只是获取了memetype. 下面有对memetype进行安全校验。**`getMimeType`函数的代码如下。![1616378940_6057fc3ca9b55e15af683.png!small?1616378941023](https://image.3001.net/images/20210322/1616378940_6057fc3ca9b55e15af683.png!small?1616378941023)

    
    
    private function getMimeType($file, $extension) {  
    $mimeType = "";  
    if (function_exists("mime_content_type")) {  
    $mimeType = mime_content_type($file["tmp_name"]);  
    } elseif (function_exists("finfo_open") && function_exists("finfo_file")) {  
    $finfo = finfo_open(FILEINFO_MIME_TYPE);  
    $mimeType = finfo_file($finfo, $file["tmp_name"]);  
    } elseif ($extension) {  
    $matches = wp_check_filetype($file["name"], $this->options->content["wmuMimeTypes"]);  
    $mimeType = empty($matches["type"]) ? "" : $matches["type"];  
    }  
    return $mimeType;  
    }

  3. 接着传入`uploadSingleFile`函数,使用`pathinfo`获取到上传文件的后缀就直接拼接上传了。总的来看，只有对`mimetype`进行校验，所以直接上传“图片马”绕过`mimetype`校验即可。

![1616379003_6057fc7b619e24ab4f4c6.png!small?1616379003765](https://image.3001.net/images/20210322/1616379003_6057fc7b619e24ab4f4c6.png!small?1616379003765)

## 4 最后

Xcheck作为国内新生的代码安全审计工具，面对这些早已名声在外的前辈，会时刻保持谦逊，不断进取向前。后续我们Xcheck团队也会持续披露Xcheck发现的一些有价值的漏洞或者分享代码安全审计相关技术。

专注于代码安全 | 公众号：腾讯代码安全检查Xcheck

