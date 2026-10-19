***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **图片验证码是为了防止恶意破解密码、刷票、论坛灌水等才出现的，但是你有没有想过，你的图形验证码竟然可能导致服务器的崩溃？**

那他是如何导致的呢？请听我婉婉道来。  

先看看各大平台对待此漏洞的态度：

![TIM截图20180818092202.png](https://image.3001.net/images/20180818/1534555567_5b7775afb8756.png!small)![TIM截图20180818092213.png](https://image.3001.net/images/20180818/1534555576_5b7775b8d78cd.png!small)![TIM截图20180818092417.png](https://image.3001.net/images/20180818/1534555586_5b7775c2d13dc.png!small)![TIM截图20180818092548.png](https://image.3001.net/images/20180818/1534555602_5b7775d272b46.png!small)

##  **利用过程**

这里以phpcms为例，首先需要找一个图形验证码。

![TIM截图20180818093124.png](https://image.3001.net/images/20180818/1534555939_5b777723a34ac.png!small)将图片拖动到浏览器中将得到该图形验证码的链接：

![TIM截图20180818093459.png](https://image.3001.net/images/20180818/1534556126_5b7777de570d2.png!small)将链接拖出来咱们分析一下：

[http://127.0.0.1/phpcms/api.php?op=checkcode&code_len=4&font_size=20&width=130&height=50&font_color=&background=](http://127.0.0.1/phpcms/api.php?op=checkcode&code_len=4&font_size=20&width=130&height=50&font_color=&background=)  

> code_len=4是验证码的字符的个数  
>
>
> font_size=20是验证码的大小  
>
>
> width=130是验证码的宽  
>
>
> height=50是验证码的高  
>

如果将参数font_size、width、height均设置为1000将会出现什么情况呢？

![TIM截图20180818094003.png](https://image.3001.net/images/20180818/1534556443_5b77791b941b1.png!small)

可以发现验证码的形状已经改变，证明这个参数是会随着我们的更改而更改的，而且在改成1000时，整个页面的加载速度明显变慢，大家请想，如果都改为10000甚至更高会发生什么事情？
服务器会不会一直在处理我们所请求的图片？

此时我们上神器burp来检验一下

当设置为1000时：

![TIM截图20180818094642.png](https://image.3001.net/images/20180818/1534556920_5b777af8ca24e.png!small)

当设置为10000时：

![TIM截图20180818094814.png](https://image.3001.net/images/20180818/1534557146_5b777bda0d8fd.png!small)处理所用的时间明显增长，我们再看看在发起这个请求时CPU有什么反应：

![Clipboard
Image.png](https://image.3001.net/images/20180818/1534557481_5b777d29395c0.png!small)CPU有一个明显的峰值，那当我们使用python去不断进行请求的时候又会发生什么？这个是正常情况下的CPU占用率：

![TIM截图20180818100719.png](https://image.3001.net/images/20180818/1534558080_5b777f800ce50.png!small)

当我们启动python程序的时候CPU的占用率：

![TIM截图20180818102204.png](https://image.3001.net/images/20180818/1534559739_5b7785fbad217.png!small)

可见，我们请求的验证码对服务器产生了重大的影响。

## 代码分析

根据请求包我们跟进到 \api\checkcode.php：

![TIM截图20180818101750.png](https://image.3001.net/images/20180818/1534558679_5b7781d773f6e.png!small)

在第12行和第17行可以看到，仅仅将验证码的长宽通过get方式接受，没有任何其他的过滤，在第13行和第18行也仅仅只对最小值进行了限制，并没有对最大值进行限制，所以就造成了这个验证码的漏洞。

总结一下这个漏洞的利用点：

> 1.图片长宽等可控
>
> 2.后端没有对图片的最大大小进行限制

 **解决方案**

> 1.对接受的参数进行最大值的控制，或者固定值处理
>
> 2.使用固定大小的验证码

 ***本文作者：1wuxin1，转载请注明来自FreeBuf.COM**

