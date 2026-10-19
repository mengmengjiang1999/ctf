# 1\. 信息收集

先看看robot.txt和[www.zip/rar](http://www.zip/rar)这些敏感文件

发现robot.txt被删了什么信息都没

但[www.zip](http://www.zip)却能下载,里面是网站源码

![image](https://image.3001.net/images/20230509/1683634926_645a3aee76064a5670155.png!small)

在查看网页信息(右键查看网页源代码)

![image](https://image.3001.net/images/20230509/1683634942_645a3afea5f4e6f3b88ea.png!small)

这里好像有做这个框架的作者名字为Ethredah,在github上

在github上搜

搜到网站源码

![image](https://image.3001.net/images/20230509/1683634962_645a3b126c0fc418d52fd.png!small)  
意外收获还有一个默认的后台账号密码

![image](https://image.3001.net/images/20230509/1683634974_645a3b1e5cc4460507ef9.png!small)

迄今为止收集到的信息

该网站源码,一个后台账号及密码

# 2\. 寻找漏洞

通过网站源代码找后台就很容易啦 [www.php.com/admin](http://www.php.com/admin)登录后台

发现后台的功能十分少,就不浪费时间找了

![image](https://image.3001.net/images/20230509/1683635001_645a3b39b1fc675e792a8.png!small)

# 3.审计代码

用seay代码审计工具扫一下刚刚获取的网站源代码看看有什么漏洞

![image](https://image.3001.net/images/20230509/1683635017_645a3b493d2a28f1f89f3.png!small)

一个前台sql漏洞,其他都是后台的

查看single.php的代码

![image](https://image.3001.net/images/20230509/1683635035_645a3b5b77ebb22c5a916.png!small)

通过get方式传入一个参数id,sql语句没做任何过滤

url到这个界面看看没反应,加个id参数呢?

[www.php.com/single.php?id=1](http://www.php.com/single.php?id=1)跳到一个新的页面

![image](https://image.3001.net/images/20230509/1683635060_645a3b74b6f123d35c1a3.png!small)  
尝试输错id的值,发现有报错信息

![image](https://image.3001.net/images/20230509/1683635079_645a3b87ef069fb8a7881.png!small)  
由此得出id的值可以由我们控制,判断出id为注入点

用sqlmap跑一下,发现能注入出数据库

python sqlmap.py -u "www.php.com/single.php?id=1" --dbs –batch

![image](https://image.3001.net/images/20230509/1683635105_645a3ba1347bb3b511c3a.png!small)  
![image](https://image.3001.net/images/20230509/1683635116_645a3bac29fb12fffca5a.png!small)

# 4.sqlmap写入shell

\--is-dba查看一下权限,用—os-shell写入shell

python sqlmap.py -u "www.php.com/single.php?id=1" --is-dba

![image](https://image.3001.net/images/20230509/1683635134_645a3bbe744565f8a771d.png!small)

python sqlmap.py -u "www.php.com/single.php?id=1" --os-shell

![image](https://image.3001.net/images/20230509/1683635151_645a3bcfbd6a452bfa42f.png!small)

# 5\. 上传shell

成功连接,执行dir命令查看所在目录中的内容

发现sqlmap给我们写了3个文件:一个是用于文件上传,一个是用于url执行windows的cmd命令,一个是空的用于检测能否上传文件

![image](https://image.3001.net/images/20230509/1683635169_645a3be1a9a22ca10c542.png!small)

登录上传文件的url

http://www.php.com/tmpuvrdr.php

![image](https://image.3001.net/images/20230509/1683635202_645a3c02b4514965c3f96.png!small)

上传我们的shell.php,成功上传

![image](https://image.3001.net/images/20230509/1683635222_645a3c16d267c5299763c.png!small)  
蚁剑成功连接

如果这时发现我们上传的shell.php发生乱码,无法连接时, 这时要想到可能有防火墙的存在,那就上传我们写的免杀木马绕过

# 8\. get flag

连接成功后读取到对方目录,拿到flag.

![image](https://image.3001.net/images/20230509/1683635241_645a3c29d20f335c341c2.png!small)

Base64三次解密后

![image](https://image.3001.net/images/20230509/1683635270_645a3c463a3ffb4fcb4a2.png!small)

# 9.总结

信息收集在我们渗透的过程中尤为重要,我们拿到一个网站首先要做的就是信息收集.可以先查看一下有没有敏感信息文件泄露:例如像robot.txt,www.zip这些敏感文件,在通过网页下的备案信息搜索网站相关资料,也可以从网页审查元素进行收集,像这次的靶场的源码可以在GitHub上面查找,了解源码后可以通过代码审计找突破口,有sql注入就可以通过工具写入shell(记得查看自己的权限),同时还要注意对方服务器的防火墙做出对应的免杀木马,写入成功后即可连接拿到flag.

