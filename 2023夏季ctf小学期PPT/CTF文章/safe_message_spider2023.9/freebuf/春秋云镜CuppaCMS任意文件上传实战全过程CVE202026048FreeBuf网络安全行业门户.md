## 漏洞简介：

CuppaCMS是一套内容管理系统（CMS）。 CuppaCMS
2019-11-12之前版本存在安全漏洞，攻击者可利用该漏洞在图像扩展内上传恶意文件，通过使用文件管理器提供的重命名函数的自定义请求，可以将图像扩展修改为PHP，从而导致远程任意代码执行。

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2020-26048

## 漏洞复现：

访问漏洞环境

看到登陆界面，尝试一下存不存在弱口令，发现存在弱口令admin/admin

![](https://image.3001.net/images/20230625/1687656373_649797b529da60f9c18f1.png!small)

  

登录进管理界面，寻找可利用的点

![](https://image.3001.net/images/20230625/1687656396_649797ccae03f8e26df36.png!small)

  

在settings中的files发现可以更改允许的文件扩展名

![](https://image.3001.net/images/20230625/1687656419_649797e347891b20bcf6d.png!small)

果断加上 *.php

![](https://image.3001.net/images/20230625/1687656447_649797ff858937d58c607.png!small)

  

并找到文件管理器，且可文件上传

![](https://image.3001.net/images/20230625/1687656478_6497981e3561807a00d7c.png!small)

  

这个上传的会检验文件头是不是图片格式的，所以写个图片马绕过检测

![](https://image.3001.net/images/20230625/1687656501_64979835beaa725ce591d.png!small)

  

网站有前端js验证，所以需要把文件扩展名改为图片格式的扩展名，再用burpsuite抓包改成php

![](https://image.3001.net/images/20230625/1687656525_6497984d5b4f0a04ef577.png!small)

  

文件管理器还可以显示文件的路径

![](https://image.3001.net/images/20230625/1687656577_64979881ba5292464fc8e.png!small)

  

访问上传的木马，发现访问不了

![](https://image.3001.net/images/20230625/1687656619_649798ab8848640e70538.png!small)

  

回到文件管理器，猜测可能是.htaccess文件加了限制，发现在文件管理器能删除文件，就把.htaccess文件删了，再去访问

![](https://image.3001.net/images/20230625/1687656640_649798c0403b69064223a.png!small)

  

访问成功

![](https://image.3001.net/images/20230625/1687656657_649798d15fb6a767a3483.png!small)

  

验证木马文件是否可用

![](https://image.3001.net/images/20230625/1687656690_649798f2b6385ccbfbf09.png!small)

  

  

接下来就可执行想要执行的命令了，这里要获取flag

![](https://image.3001.net/images/20230625/1687656700_649798fc283f2ab73c2f6.png!small)

