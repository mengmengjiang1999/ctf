之前学习代码审计时，审计的一个小众cms:semcms v3.9 **。** 有啥不足之处，菜鸟勿喷 ^-^

## 环境搭建：

使用给搭建环境：phpstudy2018+phpstrom+Windows10

  * semcms v3.9 的下载：

http://www.sem-cms.com/TradeCmsdown/php/SEMCMS_PHP_3.9.zip

  * Semcms v3.9的安装：
  * 第一步：将解压后的文件上传到phpstudy2018网站根目录
  * 第二步：运行install目录进行默认安装(在地址栏输入[ _http://你的域名/install_](http://xn--6qqv7i2xdt95b/install))
  * 使用phpstorm打开网站文件夹有与浏览器打开网站。

## 代码审计：

通过分析网站首页index.php文件，发现第一步需要加载文件web_inc.php文件，此文件是漏洞触发文件。见图3.1

![1605440101_5fb11265e5bd9eea2a019.png!small?1605440102981](https://image.3001.net/images/20201115/1605440101_5fb11265e5bd9eea2a019.png!small?1605440102981)

####  ** **图3.1****

分析web_inc.php文件，发现初始位置，加载了两个文件，一个是连接数据库的，没啥看的，另一个是contorl.php文件，进行sql语句的过滤，见图3.2.

![1605440113_5fb112710594d5c026d4b.png!small?1605440114114](https://image.3001.net/images/20201115/1605440113_5fb112710594d5c026d4b.png!small?1605440114114)

####  ** **图3.2****

进入contorl.php文件分析。发现仅对GET请求做过滤，并且采用黑名单过滤，可以绕过。见图3.3

![1605440119_5fb11277710ef3f29d392.png!small?1605440120518](https://image.3001.net/images/20201115/1605440119_5fb11277710ef3f29d392.png!small?1605440120518)

####  ** **图3.3****

再分析web_inc.php文件，我们直接分析漏洞点。可以发现先判断是否存在POST请求中是否存在languageID，有就进行sql黑名单过滤，然后$Language=$languageID赋值，黑名单我们可以绕过，然后判断language是否为空，不为空就进入if语句，也就是漏洞点，将$language变量赋值给sql语句。并且未做单引号保护。见图3.4

![1605440129_5fb1128160a5588f2bd3c.png!small?1605440130505](https://image.3001.net/images/20201115/1605440129_5fb1128160a5588f2bd3c.png!small?1605440130505)

  

####  ** **图3.4****

  * 漏洞复现

再浏览器中，访问网站首页，并开启post请求。在post框中加入languageID=1 ，访问，发现显示正常。见图4.1

![1605440136_5fb1128861a5d8cff956c.png!small?1605440137486](https://image.3001.net/images/20201115/1605440136_5fb1128861a5d8cff956c.png!small?1605440137486)

####  ** **图4.1****

将languageID的值改为：

1 and
ascii(substr(database(),1,1))^109,发现网页发生了变化。这样就判断出了数据库名的第一字母就是m,asii码=109.见图4.2

这样攻击者可以通过不断的测试数据库每个字母的asii码值，最终确定数据库名。

![1605440143_5fb1128f31440643de6d5.png!small?1605440144222](https://image.3001.net/images/20201115/1605440143_5fb1128f31440643de6d5.png!small?1605440144222)

  

为了方便测试，自己写了个简单的python脚本（sqlmap当时用的少），爆出数据库名。因为猜测的范围比较大，耗时可能有点长，但是，毕竟比手工快。见图4.3

![1605440161_5fb112a1d2313add47a56.png!small?1605440162966](https://image.3001.net/images/20201115/1605440161_5fb112a1d2313add47a56.png!small?1605440162966)

  

####  ** **图4.3****

  

  

  

