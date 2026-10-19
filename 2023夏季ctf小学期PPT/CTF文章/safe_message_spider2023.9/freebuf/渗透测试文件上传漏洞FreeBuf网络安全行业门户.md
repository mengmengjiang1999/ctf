## ****简介****

文件上传漏洞，字如其意，就是 ** **可能出现在一切允许上传文件的功能点**** ；

它是指由于程序员未对上传的文件进行严格的验证和过滤，而导致的用户可以越过其本身权限向服务器上上传可执行的动态脚本文件。这里上传的文件可以是木马，病毒，恶意脚本或者WebShell等。这种攻击方式是最为直接和有效的，“文件上传”本身没有问题，有问题的是文件上传后，服务器怎么处理、解释文件。如果服务器的处理逻辑做的不够安全，则会导致严重的后果。

##  ** **靶场推荐****

  * [upload-labs](https://github.com/c0ny1/upload-labs.git)
  * [upload-labs-writeup](https://github.com/LandGrey/upload-labs-writeup)

##  ** **漏洞危害****

允许上传脚本语言文件且解析 ==> getshell

允许上传html ==> xss、csrf、登陆劫持...

允许上传压缩包 ==> 压缩包DOS、解压文件getshell

允许上传pdf ==> pdf xss

允许上传swf ==> swf xss

允许上传excel、docx ==> xxe

...

<https://twitter.com/Eyhuss1/status/1492507581084053508>

asp, aspx, php : webshell, rce  
svg: stored xss, ssrf, xxe  
gif: stored xss, ssrf  
csv: csv injection  
xml: xxe  
avi: lfi,ssrf  
html, js: html injection, xss, open redirect  
png: pixel flood attack, dos  
zip: rce via lfi, dos  
pdf: ssrf, blind xxe, Stored XSS

##  ** **挖掘判断****

主要过程还是上传正常的图片抓包，再判断一下后端的过滤规则有哪些，再针对这些规则来分析绕过

黑白名单

内容是否有判断

是否二次渲染

是否有解析漏洞

图自：<https://github.com/c0ny1/upload-labs/raw/master/doc/sum_up.png>

![1652424599_627dff97472fd0e3aa95d.png!small?1652424599682](https://image.3001.net/images/20220513/1652424599_627dff97472fd0e3aa95d.png!small?1652424599682)

##  ** **绕过方法****

图自：<https://github.com/c0ny1/upload-labs/blob/master/doc/mind-map.png>

![1652424795_627e005b23a8a96d0aceb.png!small?1652424797969](https://image.3001.net/images/20220513/1652424795_627e005b23a8a96d0aceb.png!small?1652424797969)

###  ** **可解析后缀****

语言

|

可解析后缀  
  
---|---  
  
asp/aspx

|

asp,aspx,asa,asax,ascx,ashx,asmx,cer,aSp,aSpx,aSa,aSax,aScx,aShx,aSmx,cEr  
  
php

|

php,php5,php4,php3,php2,pHp,pHp5,pHp4,pHp3,pHp2,html,htm,phtml,pht,Html,Htm,pHtml  
  
jsp

|

jsp,jspa,jspx,jsw,jsv,jspf,jtml,jSp,jSpx,jSpa,jSw,jSv,jSpf,jHtml  
  
###  ** **Content-Type****

常见类型见下：

文件类型

|

Content-type  
  
---|---  
  
超文本标记语言文本

|

.html,.html text/html  
  
普通文本

|

.txt text/plain  
  
RTF文本

|

.txt text/plain  
  
GIF图形

|

.gif image/gif  
  
JPEG图形

|

.jpeg,.jpg image/jpeg  
  
au声音文件

|

.au audio/basic  
  
MIDI音乐文件

|

.mid,.midi audio/midi,audio/x-midi  
  
RealAudio音乐文件

|

.ra, .ram audio/x-pn-realaudio  
  
MPEG文件

|

.mpg,.mpeg video/mpeg  
  
AVI文件

|

.avi video/x-msvideo  
  
GZIP文件

|

.gz application/x-gzip  
  
TAR文件

|

.tar application/x-tar  
  
  * [fuzz dict 下载](%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E6%BC%8F%E6%B4%9E.assets/content-type.txt)

###  ** **文件头****

文件幻数是用来唯一标识文件类型的一系列数字（十六进制），也就是我们常说的文件头，当白名单限制了文件幻数时，我们就要给我们的文件制造可以通过检测的文件头即可：

.jpg Value = FF D8 FF E0  
.gif Value = 47 49 46 38 ==> GIF89a  
.png Value = 89 50 4E 47  
.html Value = 68 74 6D 6C 3E 10  
.xml Value = 3C 3F 78 6D 6C

![1652424803_627e00636ac7720e35865.png!small?1652424803751](https://image.3001.net/images/20220513/1652424803_627e00636ac7720e35865.png!small?1652424803751)

###  ** **图片马****

如果后缀可以为jsp、php等，但是内容必须为图片，那么可以用图片马来进行getshell

或者会解析图片为相关的代码

  * Windows

copy 1.jpg/b+1.php/a 2.jpg

  * *nix（我失败了）

cat file1.txt >> file2.jpg  
cat file1.txt file2.jpg >> file3.jsp

###  ** **条件竞争****

如果网站的文件上传的过程是：服务器获取文件–>保存上传临时文件–>重命名移动临时文件
这样的步骤时，就可以通过不断地对文件进行上传和访问，从而使服务器还未重命名移动临时文件时，我们就利用时间差打开了文件，成功执行其中的恶意代码。

 ** **具体方法：**** 并发发包，如Burp、fuff等

###  ** **二次渲染****

二次渲染的工具可能存在RCE等漏洞，如ImageMagick

通过十六进制寻找二次渲染后内容未改变的部分，再在其中插入代码

###  ** **双上传****

和标题一个意思，同时构造两个上传，可能服务端只会验证第一个上传，而第二个上传则直接保存

##  ** **修复建议****

后缀白名单，只允许上传jpg、jpeg、png、gif

内容完整性检测

WAF

##  ** **文件上传FUZZ****

  * [upload-fuzz-dic-builder](https://github.com/c0ny1/upload-fuzz-dic-builder.git)
  * [构造优质上传漏洞fuzz字典](https://gv7.me/articles/2018/make-upload-vul-fuzz-dic/)

