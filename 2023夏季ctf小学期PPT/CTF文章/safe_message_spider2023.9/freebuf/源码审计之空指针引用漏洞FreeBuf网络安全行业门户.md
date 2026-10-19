***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：freezing，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 前言

 **最近在网上加入了一个安全团队，里面有人问我如何做代码审计。只能说先能看得懂代码，了解各种漏洞的形成原因。然后多进行审计和调试练习。
这是刚学习源码审计时写的一遍审核过程， 希望大家做个参考。(php的文章很多，来一篇C语言的）**

## 一、空指针漏洞原因

Null
Pointer空指针的引用，对于空指针的错误引用往往是由于在引用之前没有对空指针做判断，就直接使用空指针，还有可能把空指针作为一个对象来使用，间接使用对象中的属性或是方法，而引起程序崩溃。

## 二、空指针漏洞难以发现的原因

空指针（NullPointer）引用导致的错误，依靠代码审计工具很难发现其中的错误，因为空指针的引用一般不会发生在出现空指针然后直接使用空指针情况。往往是由于代码逻辑比较复杂空指针引用的位置会比较远，不容易发现；并且在正常情况下不会触发，只有在某一个特定输入条件下才会引发空指针引用。对于排查此类错误也就更加困难。

## 三、白盒分析是空指针引用

### 3.1 三个条件  

![图片.png](https://image.3001.net/images/20180421/15242887663440.png!small)

### 3.2.rats软件介绍

RATS是一个代码安全审计工具，可扫描 C、C++、Perl、PHP 和 Python 源码，检查出一些常见的安全问题，例如缓冲区溢出和 TOCTOU
(Time Of Check, Time Of Use) 。 rats软件版本v2.3。  

### 3.3.sourceinsight查找分析

（1）由于软件本身是代码审计工具，所以缓冲区之类的溢出就不检查了。直接查找空指针NULL是否存在。

![图片.png](https://image.3001.net/images/20180421/152428888037.png!small)

剔除出掉指针初始化赋值。

主要针对数据赋值。

找到了一下几处。

可疑点1：

![图片.png](https://image.3001.net/images/20180421/15242889059578.png!small)

可疑点2：

![图片.png](https://image.3001.net/images/20180421/15242889278171.png!small)

可疑点3：

![图片.png](https://image.3001.net/images/20180421/15242889558501.png!small)  

可疑点4：

![图片.png](https://image.3001.net/images/20180421/15242889732388.png!small)  

可疑点5：

![图片.png](https://image.3001.net/images/20180421/15242889888686.png!small)  

可疑点6：

![图片.png](https://image.3001.net/images/20180421/15242890041989.png!small)  

(2)可疑点是否有调用

可疑点1查看其调用点发现所有的都针对NULL做了判断，所以不存在空指针引用。排除。

![图片.png](https://image.3001.net/images/20180421/15242890227055.png!small)

可疑点2：

所有文件中查找后发现就赋值了一次。再也没使用过此字段。排除.

![图片.png](https://image.3001.net/images/20180421/15242890406250.png!small)

可疑点3:

所有文件中查找就只有一处使用，而且做了判断。故排除。

![图片.png](https://image.3001.net/images/20180421/15242890931843.png!small)

可疑点4：

所有文件中查找就一处使用，其它做赋值，使用部分做了判断，故排除。

![图片.png](https://image.3001.net/images/20180421/15242891189104.png!small)

可疑点5和可疑点6一起分析。

![图片.png](https://image.3001.net/images/20180421/1524289144452.png!small)

下面的引用还有未做是否为空的判断。

![图片.png](https://image.3001.net/images/20180421/1524289168263.png!small)

进一步分析可疑点5：函数名为staticbuffer，有引用，所以可疑点5有可能性。

![图片.png](https://image.3001.net/images/20180421/15242891821046.png!small)

进一步分析可疑点6,函数名phpbacktick，没有对data的引用，所以可以排除可疑点6.

![图片.png](https://image.3001.net/images/20180421/15242892089030.png!small)

(3)对触发条件进行分析梳理。

第一步：赋空值的条件

倒推出StaticGlobalBuffer为条件。可以看到下图中的数据。

![图片.png](https://image.3001.net/images/20180421/15242892912612.png!small)

2.调用的条件：

经过查找发现

    
    
    build_html_vulnerability(vulnerability_t*ptr)
    
    report_vulnerability(vulnerability_t*ptr)

存在引用data。

所以可以得知。

一个C或Cpp文件中有char类型的全局缓冲区变量（char数组），就可以触发这个异常。

## 四、验证漏洞

1.根据白盒可得知如下文件即可引发漏洞,1.c文件里只有

char a[10]; 一句代码。  

![图片.png](https://image.3001.net/images/20180421/1524289472429.png!small)

2.生成文件验证。

    
    
    gdb rats
    
    set args --html  1.c

可以得到如下结果。

![图片.png](https://image.3001.net/images/20180421/15242895157647.png!small)

发现并没有引发异常。

所以build_html_vulnerability函数的调用栈。

![图片.png](https://image.3001.net/images/20180421/15242895376883.png!small)

前面有一个条件，如果告警不等于默认以及小于2类。就忽略掉。

但是全局字符的告警为low，不等于默认但是小于2类，忽略。

![图片.png](https://image.3001.net/images/20180421/15242895609162.png!small)

所以需要条件来使告警不被忽略，所以要改变warning_level的值，查找

warning_level的引用。发现如下图  
![图片.png](https://image.3001.net/images/20180421/15242895904152.png!small)

当输入参数小于1时为1，只要warning_level为1时，(low=1)<1不成立，则忽略可以不被忽略即可。所以只要optarg大于等于3即可达到条件。

重新设置参数 set args –w4 --html 1.c，发现已经出现错误了。

![图片.png](https://image.3001.net/images/20180421/15242896221263.png!small)

![图片.png](https://image.3001.net/images/20180421/15242896472203.png!small)

由于xml格式显示也是这样的。所以重新设置参数 set args –w4 --xml 1.c 输出也一样。

![图片.png](https://image.3001.net/images/20180421/15242897157259.png!small)

![图片.png](https://image.3001.net/images/20180421/15242897315544.png!small)

## 五、总结

本次使用到的工具，rats-2.3(源码自行下载），sourceinsight，gdb，peda。学习的时候写一个一片过程总结，今天发表出来。
希望大家做个参考。  

***本文原创作者：freezing，本文属FreeBuf原创奖励计划，未经许可禁止转**

