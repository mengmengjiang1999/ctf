***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **0x0 背景**

**以前做等级保护的时候漏扫经常扫描出来一些网站有CSRF的漏洞，由于一般扫描器提示为中风险必须要解决经常和开发人员扯皮要怎么改怎么改，每次都描述的不清楚经常感觉心累。**

最近看到OWASP的一本《安全测试指南第四版》的书就随手翻了二页其中谈到了关于会话管理测试的一栏目比较感兴趣就从网上随便下载了一个开源的CMS做一下黑盒测试，练练手万一失业了还能转化写写代码做做测试，过程中发现CMS对于很多表单请求都采用了Token认证做的挺好的于是写个笔记方便日后来看。

##  **0x1 抓包分析**

 **** 架起代理burpsuit开启准备大干一场，首先找到了一个表单的提交页面，表单主要采用Post方法进行提交，随便填了点数据就提交了。

![图片1.png](https://image.3001.net/images/20190108/1546952517_5c349f4533e82.png!small)

通过burpsuit拦截下来之后看一下各个参数  

![图片2.png](https://image.3001.net/images/20190108/1546952529_5c349f51ce421.png!small)

通过Post提交到一个Task的action，看这么多参数万一有过滤不严格的情况方法说不定能出现一些XSS或者sql注入的漏洞于是就稍微看了一下就发送到了scanner。  

Proxy放过之后页面却出现了异常提示Token验证不通过。

![图片3.png](https://image.3001.net/images/20190108/1546952558_5c349f6e60858.png!small)

然后认真一看发现除了一些表单提交的参数外还有一个token=20e168c64ce1f1f98f89e4c8ff9e3aba的字段。表单提交之后response数据包当中也有一个新的token":"e40fe4b3afedc40f95903fef92eb79ed，这样导致这一个请求包只能请求一次，Burpsuit
Scanner基于原有请求包的参数测试的扫描模式就基本上没有什么用了。

![图片4.png](https://image.3001.net/images/20190108/1546952573_5c349f7dde252.png!small)

Token普遍有二个作用：  

1.防止表单重复提交

2.anti csrf攻击（跨站点请求伪造）

由于token具有较好的随机性，不容易被猜测出来具有良好的安全性，于是看一下源码当中的实现。

##  **0x2 源码分析** ****

通过请求的路径找到对应的php文件，当请求这个表单的时候会自动执行$label->token()这么一个方法

![图片5.png](https://image.3001.net/images/20190108/1546952607_5c349f9fd36c8.png!small)

查看label.php的源码，token这个方法构造hidden表单定义了一个token的变量后赋值Core\Func\CoreFunc::$token

![图片6.png](https://image.3001.net/images/20190108/1546952621_5c349fad9303b.png!small)

继续再查看CoreFunc的源码，包含了对token生成的过程

调用microtime生成毫秒数之后打散成数组增加随机性，通过substr提取数字与随机数相乘之后计算md5保证了token的不可预测性。

Token的随机性取决于当前时间、rand随机、md5散列算法

![图片7.png](https://image.3001.net/images/20190108/1546952634_5c349fba54977.png!small)

将生成的token存如session服务器会话当中

![图片8.png](https://image.3001.net/images/20190108/1546952853_5c34a09561371.png!small)

提交的表单主要由task.php处理task类当中只是读取了session中userid的字段，使用父类Content的
parent::action($jump, $commit)方法进行验证通过之后再处理表单数据。  

![图片9.png](https://image.3001.net/images/20190108/1546952793_5c34a0595d3b7.png!small)

一层又一层，感觉真复杂。Content类继承了Controller中的checkToken()检查

Token无论验证是否通过都会删除当前token的值保证了不会被重用

![图片10.png](https://image.3001.net/images/20190108/1546952727_5c34a017be28a.png!small)

##  **0x3 总结**

session应用相对安全但也繁琐，同时当多页面多请求时必须采用多Token同时生成的方法，这样占用更多资源，执行效率会降低。但是对安全性的提升是明显的，对于表单的重复提交、基于单个数据包的变形扫描、解决CSRF漏洞也不是一种不错的方式。

 ***本文作者：si1ence，转载请注明来自FreeBuf.COM**

