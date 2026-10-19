***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 概述

 **DedeCMS 简称织梦CMS，当前最新版为 5.7
sp2,最近又去挖了挖这个CMS,发现过滤XSS的RemoveXSS函数存在缺陷导致可以被绕过。**

## 相关环境

> 源码信息：DedeCMS-V5.7-UTF8-SP2
>
> 漏洞类型：反射型XSS
>
> 下载地址：<http://www.dedecms.com/products/dedecms/downloads/>
>
> 漏洞文件：/include/helpers/filter.helper.php  
>

## 漏洞分析

1.先查看/include/helpers/filter.helper.php文件，其中的RemoveXSS函数，其中代码如下：

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534918651_5b7cfffbefa3e.png!small)

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534918672_5b7d0010d3ee7.png!small)

2.过滤的大概流程是,前面先把例如十进制和十六进制的(&#xxxxxxxxxx;)这种编码,转换回原来的字符,后面就是根据$ra1和$ra2里的黑名单进行过滤替换,例如javascript:alert(1)会被过滤成
ja<x>vasc<x>ript:alert(1)；

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534919193_5b7d0219ac6e6.png!small)

3.如果这个时候,我输入的内容是

    
    
    javascrip%26%2338%3B%26%2335%3B%26%2349%3B%26%2349%3B%26%2354%3B%26%2359%3B:alert(1)；

4.url解码得到

    
    
    javascrip&#38;&#35;&#49;&#49;&#54;&#59;:alert(1)；

5.这个时候进去RemoveXSS,进行第一次处理,也就是把(&#xxxxxxxxxx;)这种编码,转换回原来的字符,得到

    
    
    javascrip&#116;:alert(1)；

6.后面的过滤步骤就是黑名单过滤了,然而javascrip&#116;并不在黑名单之内,所以不会过滤,最后就是输出内容了；

7.这个时候输出&#116;在标签的属性里面会重新还原成字母t,所以最后会在html输出javascript:alert(1)；

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534921347_5b7d0a834f2ff.png!small)

8.下面是测试效果图：

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534922158_5b7d0daeb2d15.gif!small)

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534922427_5b7d0ebbaded5.gif!small)

##  **总结**

1.我画了草图，两次和一次编码的区别如下：

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534923326_5b7d123e4e68e.png!small)

2.另外后面的代码会根据黑名单生成正则表达式，我拿其中一个测试,这段代码会生成正则表达式：

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534923747_5b7d13e3c8016.png!small)

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534923782_5b7d14063971d.png!small)

3.根据生成的其中一条正则表达式,可以看出,他应该是匹配javascript之间有没有恶意字符防止绕过,例如j&#x0a;avascript会被匹配到

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534923978_5b7d14ca08a45.png!small)

4.正则匹配的是恶意字符之间的&#xxxxxx;,以分号结尾,但是有一点要注意的就是&#x0a; 等于
,不需要分号结尾也是可以的,例如,不加分号正则就匹配不到,但是效果也是一样的,也是可以弹窗。

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534928683_5b7d272b046e0.png!small)

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534925607_5b7d1b2718b8c.png!small)

5.还有一个问题,就是织梦的正则匹配&#[xX]0{0,8}([9ab]);
,注意{0,8},大概是八位左右,如果我超过八位,就算加上分号过滤器也匹配不到，正好十六进制格式的时候可以有很多0,足够超过八位了,例如：

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534928789_5b7d2795d52d3.png!small)

![DedeCMS v 5.7 sp2 RemoveXSS
bypass](https://image.3001.net/images/20180822/1534926066_5b7d1cf25b6f5.png!small)

## 最终总结

漏洞挖挖总还是有的,织梦的XSS过滤器有三个问题：

> 1.两次编码的时候,正则和黑名单就没软用了；
>
> 2.黑名单匹配的时候，正则无法匹配到没有分号结尾的编码；
>
> 3.也是黑名单匹配的时候，匹配编码字符大概在0-8个字符之内,但是十六进制可以超过八个字符,这个时候也无法匹配。

 ***本文作者：q601333824，转载请注明来自 FreeBuf.COM。**

