![](https://image.3001.net/images/20220106/1641436376_61d654d850c3b468fbf1b.jpg!small)

## **前言**

告别脚本小子系列是本公众号新开的一个集代码审计、安全研究和漏洞复现的专题，意在帮助大家更深入的理解漏洞原理和掌握漏洞挖掘的思路和技巧。我们将由浅入深的对java安全相关的技术进行讲解。课程中提到的任何漏洞均为已公开漏洞，禁止把文中提到的方法用于攻击目的，由此产生的法律问题与本公众号无关。

本系列课程可能包含多篇文章，初期构想的课程目录如下，具体可能依据实际情况有所变动。如果你对下面的某些内容感兴趣，可以点击关注。

> 目录
>
> 1\. Java本地调试和远程调试技巧
>
>  **2\. Java反编译技巧**
>
> 3\. Java安全基础概念之反射与ClassLoader
>
> 4\. 从冰蝎来看目前webshell的实现原理
>
> 5\. Java反序列化基础
>
> 6\. CommonCollections利用链分析介绍上
>
> 7\. CommonCollections利用链分析介绍下
>
> 8\. JNDI注入原理与fastjson漏洞实践
>
> 9\. Weblogic反序列化漏洞分析
>
> 10\. Java命令回显技术研究
>
> 11\. Java内存马技术研究
>
> 12\. RASP技术研究
>
> 13\. 基于CodeQL的自动化代码审计技术研究上
>
> 14\. 基于CodeQL的自动化代码审计技术研究下
>
> ……

##  **基础概念**

1）.java和.class文件

java是编译型语言，源码文件是.java，编译后的文件是.class（又称为字节码文件），只有编译之后的文件才能被执行。.class是不可读的二进制文件，反编译的一种场景是需要把.class文件反编译为可读的.java文件。

2）JVM

JVM是Java Virtual
Machine（Java虚拟机）的缩写，编译后的.class文件是交由JVM来执行。JAVA是一种跨平台的语言，也是因为JVM帮我们适应了不同操作系统的区别，导致上层的.class文件是通用的。

3）Jar包

Jar包是指把大量的Java类文件、相关的元数据和资源文件聚合到一个文件，按照特定的命名和存放方式，以zip的形式进行压缩的文件。Jar包本质上就是一个zip压缩文件，可以用常规的解压软件打开。Jar包可以是独立运行的java运行程序，也可以是供其他程序调用的库文件。如果在Jar包内部的Manifest.MF文件中配置Main-Class属性，则该Jar包可以直接通过java -jar test.jar的方式运行。

##  **Java反编译方法**

要对class文件进行反编译，首先需要来认识class文件，典型的class文件如下：

![](https://image.3001.net/images/20220106/1641436523_61d6556b169335c041915.png!small)最前面的“cafe
babe”是属于java字节码的规定特征，只有以这个字符开头的文件才是JVM能识别的正确的字节码文件。后面的“0000”代表JDK的次版本号，“0034”代表JDK的主版本号。编译的class文件只允许运行在大于等于自己版本的JDK环境中，否则会报错，这里引用一张公开流传的关于字节码组成的图片：

![](https://image.3001.net/images/20220106/1641436564_61d655943fbe78c860838.png!small)

关于字节码的具体组成我们不需要太过于关注，我们更重要的是关心如何对字节码文件进行反编译。

1）反编译工具javap

java原生提供了对字节码文件进行反编译的工具javap，javap提供的命令如下所示：

![](https://image.3001.net/images/20220106/1641436596_61d655b4a1bc07aa97fb0.png!small)主要用法是javap
-p test.class，可以查看所有class文件的属性和方法：

![](https://image.3001.net/images/20220106/1641436629_61d655d58cf7d79bb65b1.png!small)

如果要查看方法的详细信息，可以通过-c参数来查看，但是看到的信息就像汇编一样难看，所以我们一般不采用原生的反编译工具，如下图所示：

![](https://image.3001.net/images/20220106/1641436660_61d655f4d1c164b3b4e4f.png!small)

2）IDEA反编译工具

由于javap反编译工具反编译的代码可读性较差，所以在javap的基础上出现了更多好用的反编译工具，其中比较有代表性的是jd-gui。jd-gui是一款简单易用的反编译工具，直接把jar包或者class文件打包，就可以看到反编译的结果了。但是由于对批量反编译的支持不友好，所以我个人是不喜欢用JD-GUI的。

我更喜欢用IDEA自带的反编译工具，使用idea对class文件进行反编译，只要直接打开class文件就可以了。新建一个空的项目，在项目中新建文件夹lib，把需要反编译的jar包拷贝到lib目录里面，右键选中“Add
as Library”就可以通过IDEA对目标jar进行反编译了。

![](https://image.3001.net/images/20220106/1641436686_61d6560e656a64d89327e.png!small)反编译之后的jar包是可读性很好的java代码，IDEA会提示此文件属于反编译的class文件，class文件只能查看，不能修改。

![](https://image.3001.net/images/20220106/1641436715_61d6562b86ffdb70311db.png!small)

3）批量反编译工具

使用IDEA进行反编译已经可以解决我们很多日常遇到的问题，是属于我们日常做JAVA安全研究必不可少的功能。但是IDEA有一个缺陷是不支持对反编译文件的文本内容进行搜索（IDEA只支持对已经建立了索引的类进行搜索），这对于一个习惯了各种全局搜索找关键字的人来说，可谓是很不方便的。

这里推荐使用开源的工具fernflower（https://github.com/fesh0r/fernflower）对目标jar包进行批量反编译，相关用法直接参考Github就可以了。反编译之后的jar包就可以像正常的文本一样进行搜索和查看了。

##  **Java反编译实践**

对某个项目进行反编译除了可以帮助我们阅读程序的逻辑代码以及挖掘代码可能存在的安全隐患外，还有一种用处是修改程序可能存在的授权机制，绕过授权认证。下面以绕过某OA授权机制来实践说明反编译的用处。

某OA在安装完成之后需要上传license激活，首先安装之后的界面如下：

![](https://image.3001.net/images/20220106/1641436771_61d656635ad6aed9e7e9b.png!small)登录会弹出license授权功能，需要上传授权文件。

![](https://image.3001.net/images/20220106/1641436799_61d6567f6aaba1f228f2c.png!small)

随便上传一个.license的文件，用burp抓一下关于license上传的处理逻辑，如下图所示：

![](https://image.3001.net/images/20220106/1641436829_61d6569d0336236f04910.png!small)

下一步就是找请求路径对应的后端真实文件信息，这个不是我们本次课程的主要内容。我们直接定位到后端处理文件LicenseOperation.jsp。其他代码我都省略了，只看关于授权相关的关键代码。

这里的逻辑代表要获取一个参数code，用于和WEB-INF/code.key文件比较，如果不一致就报错，这一步我们直接看一下对应文件里面的值是多少就好了：

![](https://image.3001.net/images/20220106/1641436865_61d656c1ac2d708538a0c.png!small)

message这里就是真正在进行授权license文件校验的地方：

![](https://image.3001.net/images/20220106/1641436890_61d656dad5c03a5f94bbb.png!small)

继续跟进InLicense函数，这里会进行一个CkLicense的判断，如果返回1，则代表license有效（激活成功），然后就可以设置数据库中保存的公司信息。

![](https://image.3001.net/images/20220106/1641436919_61d656f7cff85f707ebe5.png!small)然后再跟CkLicense函数，这里就是通过某OA自己的逻辑判断license是否合法，我们直接让这个函数返回1就可以了。

![](https://image.3001.net/images/20220106/1641436991_61d6573fcc30a38fe44aa.png!small)

在项目目录中新建一个和目标CkLicense相同的类（类名和包名都要一样），如下图所示：

![](https://image.3001.net/images/20220106/1641437028_61d65764e9aa96f730089.png!small)

编译的时候发现这个包报错了，看了一下代码，这里确实是有语法错误的。竟然定义了一个int的变量，初始值是false。不知道最开始这个jar包是怎么编译通过的？

![](https://image.3001.net/images/20220106/1641437075_61d657931f159cd6dd2c4.png!small)

如果我们在重打包的时候遇到这种问题，那就直接按照正确的语法来改就好了。不把语法错误改正了，我们也不好把java编译成class文件。

编译之后会生成对应类的class文件，我们在对应的jar包中替换对应文件就可以了。用winrar这样的工具打开jar包，直接把编译好的class文件拖进去就可以替换了：

![](https://image.3001.net/images/20220106/1641437089_61d657a191d5f9aecee85.png!small)然后再到服务器上面用这个新的jar包替换同名jar包，就完成了某OA绕过license的过程。绕过之后我们就可以直接登录系统了，登录会要求进行升级，这里为了保护该oa隐私就不登陆进去截图了：

![](https://image.3001.net/images/20220106/1641437125_61d657c56332e9d3cbab7.png!small)

[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483803&idx=1&sn=1af141cd5623b2682cfbdc2c12a53309&chksm=c2a1d512f5d65c04bc046ee83de4ba98881d086837f05cef581b39323026195b504bb5635c4c&token=800894986&lang=zh_CN#rd)

