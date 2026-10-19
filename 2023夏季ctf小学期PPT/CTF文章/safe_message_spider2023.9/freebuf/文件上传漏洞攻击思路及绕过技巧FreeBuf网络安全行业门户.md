## 文件上传检验流程：

1.客户端JS检验（后缀名）

2.服务器端检测：

  * 文件类型content-type
  * 文件内容头(cookie、HTTP认证、会话等)
  * 目录路径
  * 文件扩展名检测
  * 黑名单or白名单
  * 自定义正则校验

3.WAF

## IIS服务器

*.asp;.jpg 这种文件名在“；”后面的内容会被直接忽略，文件会被解析为*.asp

 **两种漏洞**

  1. *.asp、*.asa会被解析为asp
  2. *.asp;1.jpg会被解析为asp

WebDav通信协议

开启WebDav扩展，如果支持Delete、Put、Move、Copy，则可能存在漏洞

 **如何利用WebDav进行攻击？**

  1. option/ /URL 判断服务器支持的http方法
  2. put /abc.txt URL 给服务器上传文件
  3. COPY /abc.txt URL 用COPY或MOVE改名
  4. DELETE /abc.txt URL delete服务器上的任何文件

## apache服务器

解析扩展名：从后向前，当遇到不认识的扩展名时将从后向前进行解析，直到遇到认识的扩展名为止。

 **如何查看apache能识别的文件扩展名？**

/private/etc/apache2/mime.types

 **绕过上传漏洞**

防止上传漏洞主要有两种方式：

客户端检测：在文件未上传时，通过JS代码判断文件类型是否合法

服务器检测：在文件上传到服务器时，通过服务器脚本检测文件类型是否合法，有时会检测文件内容是否合法

1.绕过客户端检测——JS检测绕过

  * Firebug或开发者工具 shift+command+J

将JS检测文件后缀名代码删去

firebug需要Firefox45版本

  * 中间人攻击

上传文件前将文件后缀改为jpg，在用burpsuite抓包，将文件后缀再改为php，但是要修改注意 content
length（实体正文长度）,否则就会失败

2.绕过服务器端检测

a. 黑名单过滤：

  1. 使用开发者未过滤的扩展名
  2. 如果未对扩展名进行大小写转换在进行过滤，则可以通过大小写过滤
  3. 在windows上，如果文件名以”.”或空格结尾，会自动忽略”.”及空格，则可上传等进行绕过

b. 白名单过滤：

只允许上传特定的文件扩展名

若web的容器是IIS 6.0，可以通过修改扩展名1.asp;1.jsp绕过，此时php识别的扩展名为jsp，但浏览器会将其解释为asp脚本文件

c. MIME类型：

用来设定某种扩展名文件（jpg、mp4、mp3等）的打开方式，若该种文件允许上传，浏览器就会使用特定的程序打开。

### 文件类型绕过攻击

通过抓包修改content-type的值绕过客户端检测

HTTP content-type

PHP类型文件：application/octet-stream

jpeg/image类型文件：image/jpeg

二进制文件：binary (application/octet-stream)

mp4文件:video/mpeg4

PDF文件：application/pdf

### 目录验证

关键代码：如果文件夹不存在，就新建文件夹

    
    
    if(!is_dir($Extention))
    
    {
    
    mkdir($Extention)
    
    }

mkdir：新建文件夹函数

HTML关键代码：默认文件上传路径

<input type=”hidden” name=”Extention” value=”up”/>

则可以使用：

  1. firebug或火狐的开发者工具或burp修改默认上传路径（asp）
  2. 然后上传一句话图片木马文件

如果Web容器为IIS6.0，网页代码会被解析

### 截断上传攻击

举例：输入文件名

    
    
    <%
    
    username=request(“username”)
    
    Response.write username
    
    %>

当访问[http://www.scsjsudh.com:80/text.asp?username=abc%00admin](http://www.scsjsudh.com/text.asp?username=abc%00admin)时，相当于访问username=abc

### 如何使用00截断？

  1. 上传文件名时，asp空格cde.jpg
  2. 用burp抓包，打开HEX选项，将“空格”的十六进制编码20改为00，即NULL
  3. asp后的jpg被截断

### 文件编辑器上传漏洞

利用文件编辑器处理文件扩展名时的缺陷，例如：没有对上传文件重命名、文件扩展名过滤不严、编码漏洞等

FCKeditor
2.4.2及其以下版本中，在处理上传文件时，首先判断文件类型，是不是在设置的file、image、flash、media中的一种，如果文件满足条件，就会进行进一步处理，对文件的扩展名进行判断是否为允许上传的类型，然后重命名，但是没有对media类型的文件进行处理，所以就可以通过上传一个文件，然后抓包或者用火狐的开发者工具修改文件类型，从而进行攻击。

“没有绝对安全的网站”，所以在看似毫无漏洞的网页中，查看页面源代码，说不定会有所收获哦～

### 竞争条件攻击

有一些网站就比较猥琐了，上传文件时并不会做任何限制，但是在上传后检查上传的文件是否包含WebShell脚本，若检查为阳性，删除。

但是聪明的黑客意识到，就算他会删除我的脚本，但是在检查和删除时会有一定的时间差，只要我好好利用这段时间差重新生成一个WebShell，那就嘿嘿嘿

## 漏洞修复建议

> 采用白名单
>
> 上传的文件先放在临时上传路径中
>
> 将上传文件扩展名改为小写并判断是否符合上传条件
>
> 对文件进行随机命名
>
> 上传文件

