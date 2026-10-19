## 前言

CTF比赛很多次都遇到过文件上传的题，解题思路总以为简简单单，实在是有些骄傲，这次把upload的总结详细总结一次。

参考某学院的脑图.  
[![kHLnS.md.png](https://image.3001.net/images/20220409/1649475004_6250fdbcaa624f033569e.png!small)](https://imgtg.com/image/kHLnS)

## 初见

### 文件上传漏洞的由来

通过客户端的POST请求上传文件，由于消息主体就是一些上传信息。前端上传页面需要指定 enctype 为 multipart/form-data 或者
Multipart/form-data 才能正常上传文件。

### 产生原因

    
    
    1.对于上传文件的后缀名（扩展名）没有做较为严格的限制
    2.对于上传文件的MIMETYPE(用于描述文件的类型的一种表述方法) 没有做检查
    3.权限上没有对于上传的文件目录设置不可执行权限，（尤其是对于shebang类型的文件）
    4.对于web server对于上传文件或者指定目录的行为没有做限制
    

##漏洞危害  
1.上传的文件是WEB语言，服务器的Web容器解释并执行了用户上传的脚本，导致代码执行。如果上传的文件是
**Flash的策略文件crossdomain.xml** ，黑客用以控制Flash在该域下的行为。  
2.上传的是木马、病毒，就会发生信息泄露，进一步的渗透攻击，提权等等。

### 查找文件漏洞

1.找到文件上传的窗口，然后判断是服务器端还是客户端的验证，客户端较容易判断出来，最后检验是哪种服务器端的过滤方式。判断是客户端和服务端检验，再检验是白名单还是黑名单，根据具体情况来决定采用什么绕过方式。  
2.Google Hacker

    
    
    语法：
    1."El Moujahidin Bypass Shell" ext:php 简单上传
    2."You have selected the following files for upload (0 Files)." 查找文件上传页面
    3.'inurl:upload.asp'或inurl:upload_soft.asp'即可找到很多上传页面
    

## 文件上传之验证绕过

### 前端-JS类验证

当我们上传php文件，前端阻止弹窗，存在前端验证文件。  
[![kHEDN.png](https://image.3001.net/images/20220409/1649475005_6250fdbdbafa39c37e88a.png!small)](https://imgtg.com/image/kHEDN)上传php文件，提示文件不允许上传

    
    
    方法：
    	1.把前端的checkfilesuffix()去掉
    	2.修改后缀php为jpg，抓包改回php，跳过前端验证。
    

## 后端-黑名单绕过

###
特殊解析后缀[![kHfwp.png](https://image.3001.net/images/20220409/1649475006_6250fdbeb4b3ea9d913a9.png!small)](https://imgtg.com/image/kHfwp)

黑名单规则不严谨，在某些特定的环境中，某些特殊的后缀名仍然会被当做php文件解析。  
Php|php2|php3|php4|php5|php6|php7|pht|phtm|phtml

### .htaccess解析

    
    
    原理：
    1..htaccess 文件提供了针对目录改变配置的方法， 即在一个特定的文档目录中放置一个包含一条或多条指令的文件， 以作用于此目录及其所有子目录。作为用户，所能使用的命令受到限制。管理员可以通过 Apache 的 AllowOverride 指令来设置。
    2.htaccess 中有 # 单行注释符, 且支持 \拼接上下两行。
    

步骤：上传一个.htaccess内容如下的文件

    
    
    <FilesMatch "1.jpg"> 
        SetHandler application/x-httpd-php
    </FilesMatch>
    

功能：将1.jpg按php文件执行  
再上传1.jpg，完成木马注入  
[![kH91U.png](https://image.3001.net/images/20220409/1649475007_6250fdbfaa942688ce6a2.png!small)](https://imgtg.com/image/kH91U)

### 大小写绕过

由于window对大小写不敏感，linux对大小写敏感  
可以将文件后缀名改为大写，进行上传。  
[![kH8xq.png](https://image.3001.net/images/20220409/1649475008_6250fdc0cb56fe9448e81.png!small)](https://imgtg.com/image/kH8xq)替换时加入了空格，我们可以利用大小写进行绕过  
[![kHXpc.png](https://image.3001.net/images/20220409/1649475009_6250fdc1a5a63749ad4fc.png!small)](https://imgtg.com/image/kHXpc)

### 点绕过

windows等系统默认删除文件后缀的.和空格，查看网站源码发现，没有过滤点。

### 空格绕过

同上，没有过滤掉空格

### ::$$DATA绕过

没有使用str_ireplace()将::$DATA替换为空，导致可以利用NTFS文件流特性。

并没有过滤掉$data,代码中并未出现，所以可以$data绕过  
[![kLMwI.png](https://image.3001.net/images/20220409/1649475010_6250fdc2c9f9c9e26e0ec.png!small)](https://imgtg.com/image/kLMwI)假设xxx.php的内容为  
[![kLa1D.png](https://image.3001.net/images/20220409/1649475011_6250fdc3829ceae870a91.png!small)](https://imgtg.com/image/kLa1D)上传一个名为xxx.php::$DATA的木马，浏览器中访问xxx.php。

### 配合解析漏洞

 **Apache HTTPD换行解析漏洞（CVE-2017-15715）**  
在2.4.0~2.4.29版本存在一个解析漏洞，在解析php时， **1.php\x0A** 将按照 **php**
后缀进行解析，导致绕过一些服务器的安全策略

 **Nginx 解析漏洞**  
由于nginx.conf的如下配置导致nginx把以’.php’结尾的文件交给fastcgi处理,对于任意文件名，在后面添加/xxx.php（xxx）为任意字符后，即可将文件作为php解析。

    
    
    上传shell.jpg
    访问shell.jpg/.php    会按照shell.php执行
    

## 后端-白名单绕过

### MIME绕过

[![kLoHF.png](https://image.3001.net/images/20220409/1649475012_6250fdc42692b561abd3f.png!small)](https://imgtg.com/image/kLoHF)

### 00截断-1（GET|POST）

%00是被服务器解码为0x00  
[![kLq86.png](https://image.3001.net/images/20220409/1649475012_6250fdc4d472409bd5fff.png!small)](https://imgtg.com/image/kLq86)

## 其他内容

### 文件头检测

当文件上传到服务器，白名单进行的文件头检测。  
JPEG (jpg)，文件头：FFD8FF  
PNG (png)，文件头：89504E47  
GIF (gif)，文件头：47494638

### 二次渲染

上传文件后，网站会对图片进行二次处理（格式、尺寸要求等），处理后在放到网站对应的标签进行显示。

如何绕过呢  
1.将一句话插入网站二次处理的图片，把一句话插入图片在二次渲染后会保留的那部分数据里，确保不会在二次处理时删除掉。

### 条件竞争漏洞

条件竞争为特别漏洞，是文件上传进行验证的短暂时间内。对传入的文件进行了临时保存，可能是一秒，也可能是0.几秒。但在这短暂时间内php是可以解析的，如果解析的速度够快。

绕过：  
上传1.php文件，利用bp抓包，设置多线程，不断发包。浏览器访问连接我们上传的1.php文件。不断刷新，会在某瞬间，执行1.php成功。

