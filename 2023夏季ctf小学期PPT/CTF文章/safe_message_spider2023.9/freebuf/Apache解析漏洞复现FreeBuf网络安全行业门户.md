**apache** **解析漏洞**

 **漏洞原理**

Apache 解析文件的规则是从右到左开始判断解析,如果后缀名为不可识别文件解析,就再往左判断。比如 test.php.owf.rar
“.owf”和”.rar” 这两种后缀是apache不可识别解析,apache就会把wooyun.php.owf.rar解析成php。

 **漏洞形式**

www.xxxx.xxx.com/test.php.xxx

 **其余配置问题导致漏洞**

（1）如果在 Apache 的 conf 里有这样一行配置 AddHandler php5-script .php 这时只要文件名里包含.php
即使文件名是 test2.php.jpg 也会以 php 来执行。  
（2）如果在 Apache 的 conf 里有这样一行配置 AddType application/x-httpd-php .jpg 即使扩展名是
jpg，一样能以 php 方式执行。

实验环境：Windows Server 2008 R2

Phpstudy2018

![1612080921_60166719ac83948be47e9.png!small](https://image.3001.net/images/20210131/1612080921_60166719ac83948be47e9.png!small)

在httpd.conf添加AddHandler php5-script .php 添加之后重启

![1612080932_60166724c3dea76b5193c.png!small](https://image.3001.net/images/20210131/1612080932_60166724c3dea76b5193c.png!small)

在根目录下创建php一句话，后缀为.php.xxx

![1612080939_6016672b1be74d06d7a6b.png!small](https://image.3001.net/images/20210131/1612080939_6016672b1be74d06d7a6b.png!small)

访问，看是否能解析

![1612080945_601667316fa7b3d1e22ca.png!small](https://image.3001.net/images/20210131/1612080945_601667316fa7b3d1e22ca.png!small)

解析成功，蚁剑连接

![1612080951_60166737eff3c4c674e0f.png!small](https://image.3001.net/images/20210131/1612080951_60166737eff3c4c674e0f.png!small)

