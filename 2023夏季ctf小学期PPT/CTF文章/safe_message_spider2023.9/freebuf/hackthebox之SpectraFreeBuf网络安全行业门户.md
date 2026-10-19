# Spectra介绍

![1618467554_6077dae257c04e794e2a8.png!small?1618467550396](https://image.3001.net/images/20210415/1618467554_6077dae257c04e794e2a8.png!small?1618467550396)

## 探测

![1618467895_6077dc37463ccdf841be5.png!small?1618467891159](https://image.3001.net/images/20210415/1618467895_6077dc37463ccdf841be5.png!small?1618467891159)

访问10.10.10.229:80端口

![1618467969_6077dc81665b168204d31.png!small?1618467965245](https://image.3001.net/images/20210415/1618467969_6077dc81665b168204d31.png!small?1618467965245)

找到spectra.htb and www.spectra.htb反向代理

http://spectra.htb/main/  
http://www.spectra.htb/testing/index.php

在/etc/hosts中添加spectra.htb

![1618468247_6077dd97b448ed890b382.png!small?1618468243634](https://image.3001.net/images/20210415/1618468247_6077dd97b448ed890b382.png!small?1618468243634)

再用目录猜解工具gobuster扫域名，这是一个扫描目录文件、DNS和VHost爆破工具。

![1618468463_6077de6fea6be4bb793e5.png!small?1618468459805](https://image.3001.net/images/20210415/1618468463_6077de6fea6be4bb793e5.png!small?1618468459805)

进一步的

![1618468484_6077de84af0fbf95face8.png!small?1618468480604](https://image.3001.net/images/20210415/1618468484_6077de84af0fbf95face8.png!small?1618468480604)

![1618468527_6077deaf144f51a099ff0.png!small?1618468522993](https://image.3001.net/images/20210415/1618468527_6077deaf144f51a099ff0.png!small?1618468522993)

testing路径下有一些php文件，我们主要看看有没有一些配置信息。

![1618468613_6077df05261b0179e2812.png!small?1618468609101](https://image.3001.net/images/20210415/1618468613_6077df05261b0179e2812.png!small?1618468609101)

发现wp-config.php.save文件里有配置信息，发现了数据库用户名密码

![1618468713_6077df694eb8ceee56247.png!small?1618468709297](https://image.3001.net/images/20210415/1618468713_6077df694eb8ceee56247.png!small?1618468709297)

![1618468770_6077dfa24608f2820d685.png!small?1618468766173](https://image.3001.net/images/20210415/1618468770_6077dfa24608f2820d685.png!small?1618468766173)

发现不允许这个ip链接数据库。再用administrator / devteam01尝试登录

![1618468911_6077e02f6f5f85b6a7e96.png!small?1618468907321](https://image.3001.net/images/20210415/1618468911_6077e02f6f5f85b6a7e96.png!small?1618468907321)![1618468873_6077e0096b417f7910bb2.png!small?1618468869399](https://image.3001.net/images/20210415/1618468873_6077e0096b417f7910bb2.png!small?1618468869399)

发现是wordpress 5.4.2版本。

## 渗透测试反弹shell

访问访问管理员面板后，可以创建反弹shell。

下载php反弹代码：http://pentestmonkey.net/tools/php-reverse-shell/php-reverse-shell-1.0.tar.gz

在如下页面填写代码

![1618469122_6077e1028f20f50e58075.png!small?1618469119311](https://image.3001.net/images/20210415/1618469122_6077e1028f20f50e58075.png!small?1618469119311)

![1618469138_6077e1121dac76613bfd1.png!small?1618469134675](https://image.3001.net/images/20210415/1618469138_6077e1121dac76613bfd1.png!small?1618469134675)

还可以参考下面链接

https://www.hackingarticles.in/wordpress-reverse-shell/

https://rioasmara.com/2019/02/25/penetration-test-wordpress-reverse-shell/

  

kali监听

![1618469276_6077e19c13e9d3acb7052.png!small?1618469272032](https://image.3001.net/images/20210415/1618469276_6077e19c13e9d3acb7052.png!small?1618469272032)

访问已编辑php页面 http://spectra.htb/main/wp-content/themes/twentyseventeen/404.php

反弹shell

![1618469394_6077e212f213c3fc0e699.png!small?1618469390860](https://image.3001.net/images/20210415/1618469394_6077e212f213c3fc0e699.png!small?1618469390860)

![1618469438_6077e23e17e29fe2d981b.png!small?1618469433966](https://image.3001.net/images/20210415/1618469438_6077e23e17e29fe2d981b.png!small?1618469433966)

  

![1618469574_6077e2c6494f86b7a0e3d.png!small?1618469570282](https://image.3001.net/images/20210415/1618469574_6077e2c6494f86b7a0e3d.png!small?1618469570282)

![1618469879_6077e3f796c35584031ee.png!small?1618469875502](https://image.3001.net/images/20210415/1618469879_6077e3f796c35584031ee.png!small?1618469875502)

输出

![1618469916_6077e41c87375f5abbbc1.png!small?1618469912408](https://image.3001.net/images/20210415/1618469916_6077e41c87375f5abbbc1.png!small?1618469912408)

继续访问数据库

mysql -D dev --user dev -p development01 超时了

mysql -D dev --user devtest -p devteam01 连接被拒绝

更多输出信息

![1618469985_6077e4615f475f1b92a77.png!small?1618469981426](https://image.3001.net/images/20210415/1618469985_6077e4615f475f1b92a77.png!small?1618469981426)

https://pentestlab.blog/2017/09/25/suid-executables/

https://unix.stackexchange.com/questions/116792/privileged-mode-in-bash

  

bash信息

![1618470047_6077e49fe51d85610f673.png!small?1618470043799](https://image.3001.net/images/20210415/1618470047_6077e49fe51d85610f673.png!small?1618470043799)

![1618470061_6077e4ade1693e947d746.png!small?1618470058609](https://image.3001.net/images/20210415/1618470061_6077e4ade1693e947d746.png!small?1618470058609)

## 结束

OVER

