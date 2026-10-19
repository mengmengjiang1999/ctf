前段时间学习代码审计时，审计小众cms：lmxcms 新手，不足之处，勿喷 ^o^  

##  

## 环境  

###  **一、** ** **Lmxcms_v1.4下载:****

[
_http://www.lmxcms.com/file/d/down/xitong/20150113/201501130910222659.rar_](http://www.lmxcms.com/file/d/down/xitong/20150113/201501130910222659.rar)  

###  **二、** ** **Lmxcms_v1.4搭建:****

环境：phpstudy2018 +windows10

  * 第一步：上传程序到服务器网站根目录
  * 第二步：运行install目录进行安装(在地址栏输入[ _http://你的域名/install_](http://xn--6qqv7i2xdt95b/install))
  * 第三步：登陆后台。

## 代码审计  

###  ** **三、漏洞分析****

通读源码，发现BackdbAction.class.php-->delbackdb函数处存在任意文件删除的漏洞。上源码分析，图1

![1605443318_5fb11ef6cf58c42abf02d.png!small?1605443320177](https://image.3001.net/images/20201115/1605443318_5fb11ef6cf58c42abf02d.png!small?1605443320177)

####  ** **图1****

标记1处，是变量**filename**获取文件名，只经过trim函数去除文件名两侧的空格。

标记2处，引用自制函数*del0ne*删除文件

我们跟随进入del0en函数。见图2

![1605443325_5fb11efd99120b0b662e4.png!small?1605443326618](https://image.3001.net/images/20201115/1605443325_5fb11efd99120b0b662e4.png!small?1605443326618)

####  ** **图2****

标记1处，将文件名直接拼接在*file/back/*下，然后删除，未作过滤。

那么，这就会造成利用*..*与*/*组合达到文件删除漏洞。

###  ** **四、漏洞验证：****

提前准备一个测试文件1.txt,在网站所在盘的根目录。

构造url:

[ _http://www.lmx.com/admin.php?m=Backdb
&a=delbackdb&filename=_](http://www.lmx.com/admin.php?m=Backdb&a=delbackdb&filename=)  

../../../../../../../../.././1.txt

结果，删除成功。如图2.2.2.3

![1605443340_5fb11f0cb77118f3feb7b.png!small?1605443342007](https://image.3001.net/images/20201115/1605443340_5fb11f0cb77118f3feb7b.png!small?1605443342007)

图3

