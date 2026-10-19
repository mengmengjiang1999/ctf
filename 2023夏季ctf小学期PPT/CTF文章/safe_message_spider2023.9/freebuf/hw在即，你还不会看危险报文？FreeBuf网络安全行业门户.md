> 我收集了八种近期主流的漏洞攻击报文，来自多个威胁感知平台，小白可以看看

# 信息泄露类

这种情况是最常见的，也是最难以捕获的，因为它也许不用攻击数据就能轻易获取，尤其是报错或探针页面，配置不当可能泄露很多东西

![image.png](https://image.3001.net/images/20210331/1617188678_606457464936b44dabbfe.png!small)

别看它危害小，但往往某个不起眼的信息就可以成为突破点  
![在这里插入图片描述](https://image.3001.net/images/20210331/1617188587_606456eb98ab328dbb6ce.png!small)

# 命令执行类

此类攻击多以echo、curl、wget、cd、ping、cat、ls等命令出现，还是很好辨认的

在GET参数中执行命令  
![在这里插入图片描述](https://image.3001.net/images/20210331/1617188588_606456ec33cc0bd000214.png!small)

在POST参数中执行命令

![image.png](https://image.3001.net/images/20210331/1617188713_60645769a9e2ed1c08ff9.png!small)

在请求头中执行命令

![image.png](https://image.3001.net/images/20210331/1617188734_6064577ee8e820cc51695.png!small)

除了普通的系统命令，还有特殊构造的命令执行语句，比如这种利用thinkphp漏洞进行命令执行

![image.png](https://image.3001.net/images/20210331/1617188763_6064579b8ad83c7b84a8a.png!small)

# 代码执行类

URL中有编码后的数据

![image.png](https://image.3001.net/images/20210331/1617188829_606457dd590b4f15367fb.png!small)

解码之后是这样的

![image.png](https://image.3001.net/images/20210331/1617188908_6064582c6c4fc9c03390d.png!small)

百度可知这是漏洞`cve-2012-1823`的攻击代码，网上有exp

![image.png](https://image.3001.net/images/20210331/1617188925_6064583d33220a8158e84.png!small)

# 文件读取类

在GET参数中读取文件

![image.png](https://image.3001.net/images/20210331/1617188963_60645863072ab38cdce5b.png!small)

# sql注入类

在GET参数中注入sql语句

![image.png](https://image.3001.net/images/20210331/1617189006_6064588e3540d7e4eeb46.png!small)

在请求头中注入sql语句

![image.png](https://image.3001.net/images/20210331/1617189043_606458b31fba082668a75.png!small)

# 文件上传类

伪装成压缩文件的测试木马

![image.png](https://image.3001.net/images/20210331/1617189073_606458d125ef88bfabd5f.png!small)

伪装成图片的一句话木马

![image.png](https://image.3001.net/images/20210331/1617189093_606458e5df54e2d455b8f.png!small)

# URL跳转类

用@绕过域名或ip白名单检测

![image.png](https://image.3001.net/images/20210331/1617189133_6064590d96916ccdd45d2.png!small)

# xml外部实体注入类

在POST请求中出现攻击命令，xxe漏洞也可读取任意文件

![image.png](https://image.3001.net/images/20210331/1617189159_606459278639824ff0df9.png!small)

> 欢迎关注公众号，原创不易，转载请注明来源[【爱国小白帽】](https://admin-root.blog.csdn.net/)

