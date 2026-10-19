影响软件：`Drupal`

版本号：`8.5.0`

方式：`通过文件模块或者子系统上传恶意文件触发XSS漏洞`

效果：`JS代码执行（Cookies 资料窃取、会话劫持、钓鱼欺骗、网页挂马等）`

漏洞测试环境：`KALI + vulhub﻿`

#  **原理解析：** **何为Drupal**

`[**Drupal**]`

[Drupal | Wikiwand](https://www.wikiwand.com/zh/Drupal)

 **是用PHP编写以GNU许可形式发布的开源免费的可自由使用的CMS。**

###  **Drupal核心**

当您下载并安装的Drupal，要正安装的文件通常被称为Drupal核心。核心相当于一个基本网站的“引擎”功能，与其他应用的现成功能一起，创建功能相对完善的网站。
Drupal核心的主要组件功能包括创建和管理

> 内容
>
>  **文件上传/下载**
>
> 菜单
>
> 用户帐户
>
> 角色和权限
>
> 分类
>
> 论坛
>
> 次提取并以各种形式如列表和表显示内容
>
> 基于所见即所得内容编辑器
>
> Drupal核心还包括一个功能丰富的搜索引擎，多语言功能，以及记录和错误报告。

##  **Drupal的特殊机制**

    
    
    function file_create_filename($basename, $directory) {
      // Strip control characters (ASCII value < 32). Though these are allowed in
      // some filesystems, not many applications handle them well.
      $basename = preg_replace('/[\x00-\x1F]/u', '_', $basename);
      if (substr(PHP_OS, 0, 3) == 'WIN') {
        // These characters are not allowed in Windows filenames
        $basename = str_replace([':', '*', '?', '"', '<', '>', '|'], '_', $basename);
      }
    
      // A URI or path may already have a trailing slash or look like "public://".
      if (substr($directory, -1) == '/') {
        $separator = '';
      }
      else {
        $separator = '/';
      }
    
      $destination = $directory . $separator . $basename;
    
      if (file_exists($destination)) {
        // Destination file already exists, generate an alternative.
        $pos = strrpos($basename, '.');
        if ($pos !== FALSE) {
          $name = substr($basename, 0, $pos);
          $ext = substr($basename, $pos);
        }
        else {
          $name = $basename;
          $ext = '';
        }
    
        $counter = 0;
        do {
          $destination = $directory . $separator . $name . '_' . $counter++ . $ext;
        } while (file_exists($destination));
      }
    
      return $destination;
    }
    

对于早期版本的Drupal其出现问题的特殊机制在于其对上传文件的命名机制，对上传文件进行重命名并不是一个罕见的机制，但Drupal却没有直接重命名这么彻底，
**而是对于同名文件会在其后接上`"_ + 序号"`**，例如我们连续上传3张命名相同的照片，则在Drupal中存储这三张照片的命名则是：

![https://image.3001.net/images/20220920/1663680354_6329bf62271ed29b2c2ee.png!small](https://image.3001.net/images/20220920/1663680354_6329bf62271ed29b2c2ee.png!small)

该机制本身没有什么问题，然而问题出现在了`preg_replace()`函数的处理机制

我们先看代码第一行：`$basename = preg_replace('/[\x00-\x1F]/u', '_', $basename);`

此处代表会将 小于 0x20 的字符转化为_，原因在于小于 0x20 的字符大多都是（ASCII）控制字符，所以在文件名中并不应该出现他们

但再仔细看着一句，**最后加了`/u`说明其将主题字符串视为UTF-8，以确保对UTF-8的兼容性（ASCII可以看成是UTF-8的子集，在`0x00 ~
0x7F`二者一致）**我们找来官方对于`/u`更进一步的解释

![1image.png](https://image.3001.net/images/20220921/1663717669_632a512514e45f268982d.png!small)

在综合代码中，对于出错后的处理机制

对于`preg_replace()`函数，在出现错误后，会返回NULL，再综合下述的拼接语句

`$destination = $directory . $separator . $name . '_' . $counter++ . $ext;`

 **会产生`"_ + 序号"`的文件名，没有后缀，后续就可以直接被我们调用利用构造XSS了**

##  **构造特殊无效utf-8字符**

这里遵循上述截图中的提示，可以构造多种无效utf-8字符

比如说依据最后一句`Five and six octet UTF-8 sequences are regarded as invalid.`

我们可以构造出这样的非法文件名：`�����.gif``������.gif`

![2image.png](https://image.3001.net/images/20220921/1663717680_632a5130119a8c8a0eef1.png!small)

成功

亦或是一些特殊的字符（包括但不限于）

![3image.png](https://image.3001.net/images/20220921/1663717703_632a5147e53fdf25edfcb.png!small)

  * ￥

![4image.png](https://image.3001.net/images/20220921/1663717717_632a5155bbedb38e0aa96.png!small)

  * ￦

![5image.png](https://image.3001.net/images/20220921/1663717730_632a5162cf4e954bafc31.png!small)

  * ￧

  * æ

  * å

  * ÿ

其他的我们就不测试了，总体来说，不合法的UTF-8有如下特征：

### 不合法UTF-8字符

* * *

1：UTF-8 单字节字符超出范围。开头字节不能是 254、255 或 128 和 191 之间（含）的任何字符

* * *

2：字节序列中的结尾字节的值超出范围。连续字节必须在 128 和 191 之间（含）

* * *

3：UTF-8 字节序列不完整。COPY 在字符串结束之前没有找到多字节字符所需数量的连续字节

* * *

4：UTF-8 字符作为代理保留。代理码位 (U+D800 - U+DFFF) 无效

* * *

5：字节序列超出最大 UTF-8 码位

* * *

7：UTF-8 字节序列没有匹配的码位

* * *

##  **注意**

此处我们不可以将文件名改为UTF-8编码后的格式，比如说`\xe2\x28\xa1.gif`这样的，因为默认会过滤掉最后一个`\`前的所有路径

![https://image.3001.net/images/20220920/1663680788_6329c1146d86552a29f07.png!small](https://image.3001.net/images/20220920/1663680788_6329c1146d86552a29f07.png!small)

#  **寻找上传点**

该漏洞需要利用`drupal`文件模块上传文件的漏洞，
**伪造一个图片文件，上传，文件的内容实际是一段HTML代码，内嵌JS，这样其他用户在访问这个链接时，就可能触发XSS漏洞**

##  **文件存储位置**

通过探索，发现两处存储上传照片的位置：

  * `/var/www/html/sites/default/files/pictures/2022-09`  
此处用于存放用户信息中，用户头像信息的照片，包括新建用户、更改原用户

  * `/var/www/html/sites/default/files/inline-images/2022-09`  
此处用于存放，用户评论文章的照片、管理者回复编辑照片的路径

两处中的照片，均可通过上述机制重新命名为不带文件后缀的版本

##  **上传点**

> 以下附上了一些相关验证的截图

经测试，以下几处均存在上传点，且可成功上传到上述两处文件存储目录之一

`http://127.0.0.1:8080/admin/people/create`

![6image.png](https://image.3001.net/images/20220921/1663717743_632a516f5ecb855ae98ed.png!small)

`http://127.0.0.1:8080/user/1/edit`

![7image.png](https://image.3001.net/images/20220921/1663717754_632a517adeb74d7b398ec.png!small)

`http://127.0.0.1:8080/user/register`

![9image.png](https://image.3001.net/images/20220921/1663717923_632a5223cf7b75691cfdc.png!small)

`http://127.0.0.1:8080/node/1#comment-form`

![8image.png](https://image.3001.net/images/20220921/1663717790_632a519e3a18522e939f0.png!small)

`http://127.0.0.1:8080/node/1/edit`

`http://127.0.0.1:8080/comment/1/edit`

![https://image.3001.net/images/20220920/1663681162_6329c28ab0b055dd89266.png!small](https://image.3001.net/images/20220920/1663681162_6329c28ab0b055dd89266.png!small)

> 其中带有参数的，比如说 1 表示当前是管理员用户登录的场景，注意区分

#  **完成**

至此最重要的步骤已经完成了，接下来我们只需构建XSS代码上传访问即可

    
    
    <html>
    <head>
    </head>
      <body>
      <a id='a' href="http://127.0.0.1/drupal-8.6.2/sites/default/files/2022-09/_0" type="text/html">123</a>
    
      <script type="text/javascript">
        var a  = document.getElementById('a')
        a.click()
      </script>
      </body>
    </html>
    

## 参考文章

[Vulhub](https://vulhub.org/#/environments/drupal/CVE-2019-6341/)

[Drupal 1-click to RCE 分析](https://paper.seebug.org/897/)

[Zero Day Initiative - A Series of Unfortunate Images: Drupal 1-click to RCE
Exploit Chain
Detailed](https://www.zerodayinitiative.com/blog/2019/4/11/a-series-of-unfortunate-images-drupal-1-click-to-rce-exploit-chain-detailed)

[PHP: Possible modifiers in regex patterns -Manual](https://www.php.net/manual/en/reference.pcre.pattern.modifiers.php)

[Drupal | Wikiwand](https://www.wikiwand.com/zh/Drupal)

[多字节字符加载错误](https://docs.aws.amazon.com/zh_cn/redshift/latest/dg/multi-byte-character-load-errors.html)

[例如无效的utf8字符串？ - 问答 - 腾讯云开发者社区-腾讯云](https://cloud.tencent.com/developer/ask/sof/100940)

[preg_replace
PREG_BAD_UTF8_ERROR](https://stackoverflow.com/questions/20103692/preg-replace-preg-bad-utf8-error)

[PHP preg_replace() 函数](https://www.runoob.com/php/php-preg_replace.html)

