内容目录：  

  * wfuzz 基本用法
    * 暴破文件和路径
    * 测试URL中的参数
    * 测试POST请求
    * 测试Cookies
    * 测试自定义请求头
    * 测试HTTP请求方法（动词）
    * 使用代理
    * 认证
    * 递归测试
    * 测试速度与效率
    * 输出到文件
    * 不同的输出

## wfuzz 基本用法

* * *

### 暴破文件和路径

wfuzz可以用来查找一个web server中的隐藏的文件和路径，来扩大攻击面。值得注意的是，这种测试的成功与否很大程度上要依赖于使用的字典。  
但是，一个web
server的平台是有限的，还有一些是默认安装，再加上一些已知的资源比如日志文件，管理路径等等，我们还是可以在猜测到发现很多东西。因此，暴破文件的路径还是可行的。

wfuzz自带一些字典文件，更多的字典可以参考下面两个开放的git：

  * [fuzzdb](https://code.google.com/p/fuzzdb/)
  * [seclists](https://github.com/danielmiessler/SecLists)

使用wfuzz暴力猜测目录的命令如下：  
`$ wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt
http://testphp.vulnweb.com/FUZZ`

使用wfuzz暴力猜测文件的命令如下：  
`$ wfuzz -w /usr/share/wfuzz/wordlist/general/common.txt
http://testphp.vulnweb.com/FUZZ.php`

* * *

### 测试URL中的参数

通过在URL中在`？`后面设置FUZZ占位符，我们就可以使用wfuzz来测试URL传入的参数：  
`$ wfuzz -z range,0-10 --hl 97
http://testphp.vulnweb.com/listproducts.php?cat=FUZZ`

* * *

### 测试POST请求

如果想使用wfuzz测试`form-encoded`的数据，比如 HTML表单那样的，只需要传入`-d`参数即可：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/wordlist]`
  2. `└──╼ $wfuzz -z file,/usr/share/wfuzz/wordlist/others/common_pass.txt -d "uname=FUZZ&pass=FUZZ" --hc 302 http://testphp.vulnweb.com/userinfo.php`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://testphp.vulnweb.com/userinfo.php`
  8. `Total requests: 52`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000044: C=200 114 L 356 W 5111 Ch "test"`
  15.   

  16. `Total time: 1.308365`
  17. `Processed Requests: 52`
  18. `Filtered Requests: 51`
  19. `Requests/sec.: 39.74425`

* * *

### 测试Cookies

在测试请求中加入自己设置的cookies，可以使用`-b`参数指定，多个cookies使用多次。  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -b cookie=value1
-b cookie2=value2 http://testphp.vulnweb.com/FUZZ`

以上命令可生成如下的HTTP请求：

  1. `GET /attach HTTP/1.1`
  2. `Host: testphp.vulnweb.com`
  3. `Accept: */*`
  4. `Content-Type: application/x-www-form-urlencoded`
  5. `Cookie: cookie=value1; cookie2=value2`
  6. `User-Agent: Wfuzz/2.2`
  7. `Connection: close`

测试cookie字段的话，可以使用下面的命令：  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -b cookie=FUZZ
http://testphp.vulnweb.com/`

* * *

### 测试自定义请求头

使用`-H`参数来指定HTTP请求的请求头，多次指定多次使用。  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -H "myheader:
headervalue" -H "myheader2: headervalue2" http://testphp.vulnweb.com/FUZZ`

生成的HTTP请求如下：

  1. `GET /agent HTTP/1.1`
  2. `Host: testphp.vulnweb.com`
  3. `Accept: */*`
  4. `Myheader2: headervalue2`
  5. `Myheader: headervalue`
  6. `Content-Type: application/x-www-form-urlencoded`
  7. `User-Agent: Wfuzz/2.2`
  8. `Connection: close`

我们还可以修改存在的请求头，比如修改User-Agent头：  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -H "myheader:
headervalue" -H "User-Agent: Googlebot-News" http://testphp.vulnweb.com/FUZZ`

生成的HTTP请求如下：

  1. `GET /asp HTTP/1.1`
  2. `Host: testphp.vulnweb.com`
  3. `Accept: */*`
  4. `Myheader: headervalue`
  5. `Content-Type: application/x-www-form-urlencoded`
  6. `User-Agent: Googlebot-News`
  7. `Connection: close`

Headers也可以被测试：  
`wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -H "User-Agent:
FUZZ" http://testphp.vulnweb.com/`

* * *

### 测试HTTP请求方法（动词）

HTTP请求方法的测试可通过指定`-X`参数指定：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/wordlist]`
  2. `└──╼ $wfuzz -z list,GET-HEAD-POST-TRACE-OPTIONS -X FUZZ http://testphp.vulnweb.com/`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://testphp.vulnweb.com/`
  8. `Total requests: 5`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Request`
  12. `==================================================================`
  13.   

  14. `00002: C=200 0 L 0 W 0 Ch "HEAD"`
  15. `00004: C=405 7 L 12 W 172 Ch "TRACE"`
  16. `00005: C=405 7 L 12 W 172 Ch "OPTIONS"`
  17. `00001: C=200 104 L 296 W 4096 Ch "GET"`
  18. `00003: C=200 104 L 296 W 4096 Ch "POST"`
  19.   

  20. `Total time: 1.030354`
  21. `Processed Requests: 5`
  22. `Filtered Requests: 0`
  23. `Requests/sec.: 4.852696`

如果在测试时要指定请求使用的HTTP方法（动词），同样可以使用`-X`参数指定。相当于御剑中的GET/HEAD。HEAD方法要快一些。

* * *

### 使用代理

如果在测试时想要使用代理的话，只需要传入`-p`参数即可：  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -p
localhost:8080 http://testphp.vulnweb.com/FUZZ`

  
【不支持外链图片，请上传图片或单独粘贴图片】  

多个代理可使用多个`-p`参数同时指定：  
`$ wfuzz -z file,/usr/share/wfuzz/wordlist/general/common.txt -p
localhost:8080 -p localhost:9090 http://testphp.vulnweb.com/FUZZ`  
这样每次请求都会选取不同的代理进行。

* * *

### 认证

wfuzz可以通过`--basec/ntml/digest`来设置认证头。

例如，想要测试一个需要HTTP Basic Auth保护的内容可使用如下命令：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/wordlist]`
  2. `└──╼ $wfuzz -z list,nonvalid-httpwatch --basic FUZZ:FUZZ https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx`
  8. `Total requests: 2`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000001: C=401 0 L 11 W 58 Ch "nonvalid"`
  15. `000002: C=200 20 L 91 W 5294 Ch "httpwatch"`
  16.   

  17. `Total time: 1.332051`
  18. `Processed Requests: 2`
  19. `Filtered Requests: 0`
  20. `Requests/sec.: 1.501443`

想测试经过认证之后的资源，我们可以通过指定`--basic user:pass`的方式来测试。

* * *

### 递归测试

使用`-R`参数可以指定一个payload被递归的深度。例如，暴破目录时，我们想使用相同的payload对已发现的目录进行测试，可以使用如下命令：

  1. `┌─[michael@parrot]─[/usr/share/wfuzz/wordlist]`
  2. `└──╼ $wfuzz -z list,"admin-CVS-cgi\-bin" -R 1 http://testphp.vulnweb.com/FUZZ`
  3. `********************************************************`
  4. `* Wfuzz 2.2.9 - The Web Fuzzer *`
  5. `********************************************************`
  6.   

  7. `Target: http://testphp.vulnweb.com/FUZZ`
  8. `Total requests: 3`
  9.   

  10. `==================================================================`
  11. `ID Response Lines Word Chars Payload `
  12. `==================================================================`
  13.   

  14. `000002: C=301 7 L 12 W 184 Ch "CVS"`
  15. ` |_ Enqueued response for recursion (level=1)`
  16. `000001: C=301 7 L 12 W 184 Ch "admin"`
  17. ` |_ Enqueued response for recursion (level=1)`
  18. `000003: C=403 10 L 29 W 263 Ch "cgi-bin"`
  19. `000005: C=404 7 L 12 W 168 Ch "CVS - CVS"`
  20. `000006: C=404 7 L 12 W 168 Ch "CVS - cgi-bin"`
  21. `000004: C=404 7 L 12 W 168 Ch "CVS - admin"`
  22. `000007: C=404 7 L 12 W 168 Ch "admin - admin"`
  23. `000008: C=404 7 L 12 W 168 Ch "admin - CVS"`
  24. `000009: C=404 7 L 12 W 168 Ch "admin - cgi-bin"`
  25.   

  26. `Total time: 1.584295`
  27. `Processed Requests: 9`
  28. `Filtered Requests: 0`
  29. `Requests/sec.: 5.680760`

* * *

### 测试速度与效率

根据对目标的影响和自身的承受能力及带宽，wfuzz提供了一些参数可以用来调节HTTP请求引擎。

使用`-t`参数可以增加或减少同时发送HTTP请求的数量。  
使用`-s`参数可以调节每次发送HTTP的时间间隔。

* * *

### 输出到文件

wfuzz通过`printers`插件来将结果以不同格式保存到文档中，可用的`printers`参考上面的`重要关键词`。  
将结果以`json`格式输出到文件的命令如下：  
`$ wfuzz -f /tmp/outfile,json -w /usr/share/wfuzz/wordlist/general/common.txt
http://testphp.vulnweb.com/FUZZ`

  
  

  

