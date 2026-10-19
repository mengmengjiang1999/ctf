# webshell免杀之传参方式及特征绕过

### 传参方式：

在这里解释一下为什么，需要讲述传参方式，由于在很多情况下，以请求头作为参数传递并非waf和人工排查的重中之重且非常误导和隐藏，下面就是常用的几种方式。

### Cookie

由于Cookie基本上是每个web应用都需要使用到的，php应用在默认情况下，在Cookies请求头中会存在一个PHPSESSID=xxxx这样的cookie，其实这个就可以成为我们的传参位置。

![1662113893_6311d865467a8a12e5308.png!small?1662113893668](https://image.3001.net/images/20220902/1662113893_6311d865467a8a12e5308.png!small?1662113893668)

用bp抓包：

![1662113910_6311d8762ce44a95f5e52.png!small?1662113910671](https://image.3001.net/images/20220902/1662113910_6311d8762ce44a95f5e52.png!small?1662113910671)

修改内容：将内容改成base64加密后的命令

![1662113930_6311d88a56b5835ae7450.png!small?1662113931301](https://image.3001.net/images/20220902/1662113930_6311d88a56b5835ae7450.png!small?1662113931301)

  

可以看到已经执行成功了，可以看到这个迷惑去非常强，如果不仔细排查是不容易发现的，由于webshell的session和网站本身业务并没有关系，所以这个PHPSESSID可以随意修改。

### Session

session的传参方式其实算是一种间接传产方式，由于session的内容是需要通过源码设置的，并不能想cookie一样直接在请求头中修改，因此需要准备两个文件，一个是将输入的参数传入session，另一个就是将session中的内容取出并执行命令

这里依旧沿用上面的cookie传参

给session传入参数

![1662113958_6311d8a611edf30970a41.png!small?1662113958437](https://image.3001.net/images/20220902/1662113958_6311d8a611edf30970a41.png!small?1662113958437)

取出session内容并执行，其实下面的代码是可以直接插入到正常页面中的，增加迷惑性，因为一般正常页面返回的html代码是比较多的，如果我们将内容回显的正常页面当中是比较难发现的

![1662113969_6311d8b1c80abf1c218c2.png!small?1662113970167](https://image.3001.net/images/20220902/1662113969_6311d8b1c80abf1c218c2.png!small?1662113970167)

在test.php下通过cookie添加session，注意这个PHPSESSID的值其实就是一个session文件，每当有一个新的sessionid都会生成一个新的session文件，因此这个文件名我们是可以随意修改的，在这里的sessionid不但是文件名，而且也是我们的base64加密后的命令，这里只需要了解一下即可

![1662113985_6311d8c16e59b6415d76d.png!small?1662113986324](https://image.3001.net/images/20220902/1662113985_6311d8c16e59b6415d76d.png!small?1662113986324)

访问命令执行的页面，并添加其cookie，即可跨页面传递参数，如果用这种方式传参是比较难发现的

![1662113997_6311d8cdc2165995dcb3c.png!small?1662113998358](https://image.3001.net/images/20220902/1662113997_6311d8cdc2165995dcb3c.png!small?1662113998358)

### 自定义头

自定义请求头其实也是作为一种伪装的请求方式，你可以选择完全自定义一个请求头进行参数传递，但是很多waf也会检测一些没出现过的请求头容易被识别出来，且一旦在日志中被找到一个以这种方式传参，很容易就能查找到使用数据包，还是不稳当，与cookie相比，cookie本身就是一堆随机数不好区分

![1662114016_6311d8e07df73bc358940.png!small?1662114016853](https://image.3001.net/images/20220902/1662114016_6311d8e07df73bc358940.png!small?1662114016853)

![1662114025_6311d8e91c6ea2e0cf847.png!small?1662114026293](https://image.3001.net/images/20220902/1662114025_6311d8e91c6ea2e0cf847.png!small?1662114026293)

### php伪协议

![1662114037_6311d8f5e9132b68a1374.png!small?1662114038348](https://image.3001.net/images/20220902/1662114037_6311d8f5e9132b68a1374.png!small?1662114038348)

![1662114044_6311d8fcbe42c7d75b26a.png!small?1662114045459](https://image.3001.net/images/20220902/1662114044_6311d8fcbe42c7d75b26a.png!small?1662114045459)

免杀效果：

![1662114050_6311d902907a6f0d226c4.png!small?1662114051122](https://image.3001.net/images/20220902/1662114050_6311d902907a6f0d226c4.png!small?1662114051122)

## 特征绕过

在这里为什么我会将特征绕过，而并没有像其他博客上写的那些，整一堆混淆的方法，原因就是因为，waf毕竟还是通过特征判断的，只有知道了，waf匹配的正则表达式大概是什么样的，webshell的免杀有真正的意义。

### 数据特征绕过

### $_xxx[xxx] 绕过:

看这个特征可以发现很明显的是一个获取参数的语句，但为什么我会将起列举出来了，因为在很多情况下，现在的web应用大多都是使用的框架，基本上所有的获取请求参数内容的方法都是经过框架封装过的，最原始的获取参数内容的方式已经非常少见了，很容易通过一些命令如linux下的find命令通过正则表达式即可找到对应的webshell，很容易被发现，因此不使用该特征是很有必要的。

### {}

使用{}来替代[]是在ctf中十分常见的绕过方式

![1662114181_6311d9850305c3ab3c5f5.png!small?1662114181379](https://image.3001.net/images/20220902/1662114181_6311d9850305c3ab3c5f5.png!small?1662114181379)

![1662114187_6311d98b038edbe4c5083.png!small?1662114187635](https://image.3001.net/images/20220902/1662114187_6311d98b038edbe4c5083.png!small?1662114187635)

### foreach语句

利用复合变量加foreach，获取参数中的内容，其特点并没有[],不容易被识别

![1662114212_6311d9a42d01d40cda2ff.png!small?1662114212544](https://image.3001.net/images/20220902/1662114212_6311d9a42d01d40cda2ff.png!small?1662114212544)

![1662114217_6311d9a99d6d32e1f9e3d.png!small?1662114218079](https://image.3001.net/images/20220902/1662114217_6311d9a99d6d32e1f9e3d.png!small?1662114218079)

### 自定义请求头

使用自定义的请求头同样是没有上面的特征

![1662114240_6311d9c0a0bd3afcc8d9d.png!small?1662114241042](https://image.3001.net/images/20220902/1662114240_6311d9c0a0bd3afcc8d9d.png!small?1662114241042)

![1662114245_6311d9c5e106e3b0db443.png!small?1662114246407](https://image.3001.net/images/20220902/1662114245_6311d9c5e106e3b0db443.png!small?1662114246407)

### 分离免杀

顾名思义，就是将一个马拆分成两部分，及使用file_get_contents()将内容读取出来，为什么不使用include等这些文件包含函数了？因为webshell的免杀在于动态函数的调用，最终还是要拼接在一起，绕过的原则其实就是绕过waf的正则表达式，如果直接include其实和写在一个文件里没啥区别

![1662114320_6311da109a0ad6592f8df.png!small?1662114320989](https://image.3001.net/images/20220902/1662114320_6311da109a0ad6592f8df.png!small?1662114320989)

![1662114326_6311da16aee3c2f659075.png!small?1662114327145](https://image.3001.net/images/20220902/1662114326_6311da16aee3c2f659075.png!small?1662114327145)

![1662114333_6311da1d5e8d41c447504.png!small?1662114334030](https://image.3001.net/images/20220902/1662114333_6311da1d5e8d41c447504.png!small?1662114334030)

![1662114341_6311da250d143bf91737c.png!small?1662114341487](https://image.3001.net/images/20220902/1662114341_6311da250d143bf91737c.png!small?1662114341487)

### 注释及空白符混淆

这种方式和sql注入差不多，原理就是php允许在括号中添加注释符和空白符并不会影响代码正常运行

![1662114359_6311da374f36ddf2d6466.png!small?1662114359652](https://image.3001.net/images/20220902/1662114359_6311da374f36ddf2d6466.png!small?1662114359652)

![1662114364_6311da3c7ca18818371ca.png!small?1662114364937](https://image.3001.net/images/20220902/1662114364_6311da3c7ca18818371ca.png!small?1662114364937)

免杀效果：

![1662114377_6311da4973ea5cbab86b5.png!small?1662114378008](https://image.3001.net/images/20220902/1662114377_6311da4973ea5cbab86b5.png!small?1662114378008)

这里方式可以绕某狗，但过不了某盾

### 反射调用

反射类及反射类方法

![1662114765_6311dbcd44e23c93d0138.png!small?1662114765743](https://image.3001.net/images/20220902/1662114765_6311dbcd44e23c93d0138.png!small?1662114765743)

通过属性名免杀

![1662114421_6311da75ce58426116661.png!small?1662114422278](https://image.3001.net/images/20220902/1662114421_6311da75ce58426116661.png!small?1662114422278)

![1662114428_6311da7c8afc1d3cca91c.png!small?1662114429189](https://image.3001.net/images/20220902/1662114428_6311da7c8afc1d3cca91c.png!small?1662114429189)

通过注释免杀

![1662114510_6311dacecb1f7cb4f927a.png!small?1662114511617](https://image.3001.net/images/20220902/1662114510_6311dacecb1f7cb4f927a.png!small?1662114511617)

![1662114518_6311dad656d5ffae7fb35.png!small?1662114518828](https://image.3001.net/images/20220902/1662114518_6311dad656d5ffae7fb35.png!small?1662114518828)

# 字符串变形

### 简单字符串拼接

![1662114573_6311db0d9e15c87f8d06a.png!small?1662114574001](https://image.3001.net/images/20220902/1662114573_6311db0d9e15c87f8d06a.png!small?1662114574001)

![1662114595_6311db236008a9455b495.png!small?1662114595943](https://image.3001.net/images/20220902/1662114595_6311db236008a9455b495.png!small?1662114595943)

### 利用字符串函数

![1662114625_6311db41e87a6daf6bced.png!small?1662114626341](https://image.3001.net/images/20220902/1662114625_6311db41e87a6daf6bced.png!small?1662114626341)

在这里我们使用base64加参数加密

![1662114638_6311db4eca674188e6665.png!small?1662114639187](https://image.3001.net/images/20220902/1662114638_6311db4eca674188e6665.png!small?1662114639187)

![1662114646_6311db568f50f9da9532c.png!small?1662114647033](https://image.3001.net/images/20220902/1662114646_6311db568f50f9da9532c.png!small?1662114647033)

  

  

  

# 内置函数免杀

### 原始webshell：

查杀的点在于Runtime.getRuntime().exec非常明显的特征

![1662111824_6311d050a5e42f7e18e00.png!small?1662111825054](https://image.3001.net/images/20220902/1662111824_6311d050a5e42f7e18e00.png!small?1662111825054)

### 利用ProcessBuilder替换Runtime.getRuntime().exec(cmd)

Runtime.getRuntime().exec(cmd)其实最终调用的是ProcessBuilder这个函数，因此我们可以直接利用ProcessBuilder来替换Runtime.getRuntime().exec(cmd)，从而绕过正则表达式。

![1662112721_6311d3d15e7278d88f3ec.jpg!small?1662112721784](https://image.3001.net/images/20220902/1662112721_6311d3d15e7278d88f3ec.jpg!small?1662112721784)

![1662112754_6311d3f2f324d07f2ef32.png!small?1662112755364](https://image.3001.net/images/20220902/1662112754_6311d3f2f324d07f2ef32.png!small?1662112755364)

执行效果：

![1662112774_6311d4062b6e409b2d8a0.png!small?1662112774546](https://image.3001.net/images/20220902/1662112774_6311d4062b6e409b2d8a0.png!small?1662112774546)

某狗：

![1662112802_6311d4228088b1a2fda24.png!small?1662112802936](https://image.3001.net/images/20220902/1662112802_6311d4228088b1a2fda24.png!small?1662112802936)

某盾：

![1662112816_6311d43085424db6b032f.png!small?1662112816936](https://image.3001.net/images/20220902/1662112816_6311d43085424db6b032f.png!small?1662112816936)

某马：

![1662112828_6311d43c6e32b50bebf02.png!small?1662112828817](https://image.3001.net/images/20220902/1662112828_6311d43c6e32b50bebf02.png!small?1662112828817)

### BeansExpression免杀

这种方式是利用Expression将Runtime.getRuntime().exec这个特征分开，相当于一个对调函数。免杀效果一般，因为很多查杀都是直接匹配Runtime.getRuntime()

![1662112883_6311d4734674ca6a25cb9.png!small?1662112883673](https://image.3001.net/images/20220902/1662112883_6311d4734674ca6a25cb9.png!small?1662112883673)

查杀效果：查杀结果一般。

![1662112904_6311d4888ad2ec259bd25.png!small?1662112904962](https://image.3001.net/images/20220902/1662112904_6311d4888ad2ec259bd25.png!small?1662112904962)

## 基于框架免杀

### thinkphp

array_map_recursive函数

![1662113090_6311d5425b54a20c6176a.png!small?1662113090711](https://image.3001.net/images/20220902/1662113090_6311d5425b54a20c6176a.png!small?1662113090711)

array_map_recursive函数分析

这里存在一个call_user_func命令执行函数

![1662113104_6311d550c94548c4acf0f.png!small?1662113105166](https://image.3001.net/images/20220902/1662113104_6311d550c94548c4acf0f.png!small?1662113105166)

![1662113116_6311d55c6025dd84fb531.png!small?1662113116798](https://image.3001.net/images/20220902/1662113116_6311d55c6025dd84fb531.png!small?1662113116798)

免杀效果：

![1662113132_6311d56c4098cb4d253b1.png!small?1662113132711](https://image.3001.net/images/20220902/1662113132_6311d56c4098cb4d253b1.png!small?1662113132711)

### smarty_php_tag函数

![1662113159_6311d58793826595dcf65.png!small?1662113159922](https://image.3001.net/images/20220902/1662113159_6311d58793826595dcf65.png!small?1662113159922)

![1662113167_6311d58f7316e208ff837.png!small?1662113167829](https://image.3001.net/images/20220902/1662113167_6311d58f7316e208ff837.png!small?1662113167829)

免杀效果：

![1662113180_6311d59c63aba60b33044.png!small?1662113180874](https://image.3001.net/images/20220902/1662113180_6311d59c63aba60b33044.png!small?1662113180874)

smarty_php_tag函数分析

直接存在命令执行，且参数可控

![1662113199_6311d5af7080fd77f93a3.png!small?1662113199820](https://image.3001.net/images/20220902/1662113199_6311d5af7080fd77f93a3.png!small?1662113199820)

## 无扩展免杀

### php加密

这里是利用phpjiami网站进行加密，进而达到加密效果

地址：https://www.phpjiami.com/

![1662113346_6311d6425ac74dd76b8a5.png!small?1662113346856](https://image.3001.net/images/20220902/1662113346_6311d6425ac74dd76b8a5.png!small?1662113346856)

加密前：

![1662113366_6311d656494e5d20238e2.png!small?1662113366617](https://image.3001.net/images/20220902/1662113366_6311d656494e5d20238e2.png!small?1662113366617)

查杀效果：D某和某狗都查杀

![1662113381_6311d6656580b00558784.png!small?1662113381774](https://image.3001.net/images/20220902/1662113381_6311d6656580b00558784.png!small?1662113381774)

![1662113399_6311d677e0ff8d9a730c9.png!small?1662113400318](https://image.3001.net/images/20220902/1662113399_6311d677e0ff8d9a730c9.png!small?1662113400318)

加密后：

![1662113425_6311d6915a1a0d3b8f711.png!small?1662113425743](https://image.3001.net/images/20220902/1662113425_6311d6915a1a0d3b8f711.png!small?1662113425743)

查杀结果：

![1662113441_6311d6a1785c7562971ba.png!small?1662113441855](https://image.3001.net/images/20220902/1662113441_6311d6a1785c7562971ba.png!small?1662113441855)

![1662113448_6311d6a8d422a98a130a9.png!small?1662113449493](https://image.3001.net/images/20220902/1662113448_6311d6a8d422a98a130a9.png!small?1662113449493)

### dezend加密

地址：http://dezend.qiling.org/encrypt.html

![1662113486_6311d6ce0e1e993a06b73.png!small?1662113486487](https://image.3001.net/images/20220902/1662113486_6311d6ce0e1e993a06b73.png!small?1662113486487)

免杀效果：

![1662113510_6311d6e607ba5ddfca21e.png!small?1662113510401](https://image.3001.net/images/20220902/1662113510_6311d6e607ba5ddfca21e.png!small?1662113510401)

dezend加密的特征还是太过明显。

### z5encrypt

地址：https://z5encrypt.com/encrypt/build

![1662113553_6311d71121c31e0718cf0.png!small?1662113553661](https://image.3001.net/images/20220902/1662113553_6311d71121c31e0718cf0.png!small?1662113553661)

  

### php-obfuscator

工具下载地址：https://github.com/naneau/php-obfuscator

在线地址：https://www.phpobfuscator.cn/

![1662113610_6311d74a22d157e77f739.png!small?1662113610691](https://image.3001.net/images/20220902/1662113610_6311d74a22d157e77f739.png!small?1662113610691)

免杀结果：（不太好用）

![1662113624_6311d7588c27a32883c4e.png!small?1662113625090](https://image.3001.net/images/20220902/1662113624_6311d7588c27a32883c4e.png!small?1662113625090)

### phpjm

地址：http://www.phpjm.net/encode.html

查杀效果：

![1662113675_6311d78b320de9100b976.png!small?1662113675680](https://image.3001.net/images/20220902/1662113675_6311d78b320de9100b976.png!small?1662113675680)

### Virbox

工具下载地址：https://shell.virbox.com/apply.html

加密后效果;

![1662113713_6311d7b15433ddffbed29.png!small?1662113713764](https://image.3001.net/images/20220902/1662113713_6311d7b15433ddffbed29.png!small?1662113713764)

Virbox已经属于是商业源码加密,基本上没有任何特征

但是由于这个是需要将生成好的php-cqi.exe原有的php-cqi.exe才能达到解密的效果，因此只能说作为一个权限维持的方式，先拿到权限后，修改php-cqi.exe，在上这种加密马，作为一个权限维持

加密过程：

操作手册：https://baijiahao.baidu.com/s?id=1671004157804653895𝔴=spider&for=pc

免杀效果：

![1662113756_6311d7dc73ba91f962ccc.png!small?1662113756884](https://image.3001.net/images/20220902/1662113756_6311d7dc73ba91f962ccc.png!small?1662113756884)

![1662113762_6311d7e2752724315c3e0.png!small?1662113762983](https://image.3001.net/images/20220902/1662113762_6311d7e2752724315c3e0.png!small?1662113762983)

  

