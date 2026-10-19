2019年7月11日，
Discuz！ML被发现存在一处远程代码执行漏洞，攻击者通过修改请求流量的cookie字段中的language参数处插入构造的payload，进行远程代码执行利用，该漏洞利用方式简单，危害性较大。本次漏洞是由于Discuz!
ML对于cookie字段的不恰当处理造成的cookie字段中的language参数未经过滤，直接被拼接写入缓存文件之中，而缓存文件随后又被加载，从而造成代码执行。

  

 **0x00 漏洞复现环境**

平台环境(windows) : phpStudy(2018) php 5.5.38 + apache

源代码<http://discuz.ml/download>

  

 **0x01 漏洞复现**

访问<http://127.0.0.1/discuz/upload/forum.php> 使用burpsuite
对请求包修改，在Cookie字段中DeBP_2132_language参数写入恶意代码 ‘.phpinfo().’ 。

整体请求如下：

> GET /discuz/upload/forum.php HTTP/1.1
>
> Host: 127.0.0.1
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0)
> Gecko/20100101 Firefox/68.0
>
> Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
>
> Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
>
> Accept-Encoding: gzip, deflate
>
> Connection: keep-alive
>
> Cookie: DeBP_2132_saltkey=PpJ0DNbK; DeBP_2132_language=sc'.phpinfo().';
> DeBP_2132_lastvisit=1563773757; DeBP_2132_sid=MjB6U2;
> DeBP_2132_lastact=1563777365%09home.php%09misc; DeBP_2132_onlineusernum=1;
> DeBP_2132_sendmail=1
>
> Upgrade-Insecure-Requests: 1
>
> Cache-Control: max-age=0

  
![0.webp.jpg](https://image.3001.net/images/20190827/1566874063_5d6499cf7a1a5.jpg!small)

在服务器返回的请求中发现我们写入的恶意代码成功得到了执行。

![执行.webp.jpg](https://image.3001.net/images/20190827/1566874092_5d6499ec41fe3.jpg!small)  

 **0x02 漏洞分析**

打开forum.php文件查看24 行包含了 ‘./source/class/class_core.php’文件。

  

那么来查看 class_core.php文件，在文件第33行的时候调用了creatapp() 方法。

  

在查看creatapp方法中如果私有属性$_app不是一个对象的话将调用discuz_application的instance()方法。

![方
1.webp.jpg](https://image.3001.net/images/20190827/1566875453_5d649f3d95789.jpg!small)  

在instance()方法中对自身类进行了实例化。

![实例.webp.jpg](https://image.3001.net/images/20190827/1566875492_5d649f64196dc.jpg!small)

而在discuz_application类的构造方法中_init_input()方法会将cookie中language的值赋给$lan变量。

![变量.webp.jpg](https://image.3001.net/images/20190827/1566875524_5d649f84dcd9a.jpg!small)

  

继续查看后发现最终会将值传递给DISCUZ_LANG。

![lang.webp.jpg](https://image.3001.net/images/20190827/1566875550_5d649f9ed5554.jpg!small)

  

扭头回到forum.php文件中继续看，在第78行的时候包含了forum_index.php文件。

![php.webp.jpg](https://image.3001.net/images/20190827/1566875576_5d649fb8d15fc.jpg!small)

查看forum_index.php文件 在432行的时候它会包含通过template方法生成的恶意文件。

分析template方法在function_core.php文件中第644行中，$cachefile变量 即缓存文件名是通过拼接几个变量的值得来的。

![值得.webp.jpg](https://image.3001.net/images/20190827/1566876389_5d64a2e50d1b1.jpg!small)

接着在653行调用了checktplrefresh方法。

![653.webp.jpg](https://image.3001.net/images/20190827/1566876572_5d64a39c5a451.jpg!small)

在checktplrefresh 方法中调用template类中的parse_template方法来生成缓存文件。

![缓存.webp.jpg](https://image.3001.net/images/20190827/1566889865_5d64d789e626d.jpg!small)  

在parse_template方法中读取模板文件到template变量。

![变量.webp.jpg](https://image.3001.net/images/20190827/1566889891_5d64d7a3bfec5.jpg!small)  

在parse_template方法中第74行的时候将可控变量cachefile拼接后赋给了headeradd变量。

![head.webp.jpg](https://image.3001.net/images/20190827/1566889921_5d64d7c11f9d9.jpg!small)

84行的时候又将headeradd拼接到了template中。

所以就形成了以下代码。

![代码.webp.jpg](https://image.3001.net/images/20190827/1566890009_5d64d819aaef2.jpg!small)

最终写入本地。

并且由forum_index.php文件的第432行代码 对template方法生成的缓存文件包含，使得在cookie中恶意构造的代码得到执行。

  

 **0x03 修复建议**

针对缓存的缓存文件名进行固定。

![qrcode_for_gh_223e082fe8a7_430.jpg](https://image.3001.net/images/20190827/1566890071_5d64d85737750.jpg!small)

