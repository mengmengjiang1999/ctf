**ffuf是一款Go语言编写的高速Web
Fuzzer工具，该项目深受大型项目[gobuster](https://github.com/OJ/gobuster)和[wfuzz](https://github.com/xmendez/wfuzz)的启发。**

## 特性

一个字，快！

允许fuzz HTTP header值，POST数据和URL的不同部分，包括GET数名称和值；

支持静默模式（-s）；

模块化架构；

易于添加的过滤器和匹配器。

## 安装

从[releases](https://github.com/ffuf/ffuf/releases/latest)页面下载预构建的二进制文件，解压缩并运行。

如果你已经安装了编译器，则可以通过以下命令进行安装：

    
    
    go get github.com/ffuf/ffuf

ffuf的唯一依赖项是Go 1.11。不需要Go标准库之外的依赖项。

## 使用

要定义ffuf的测试用例，请在URL（-u），headers（-H）或POST数据（-d）中的任意位置使用关键字FUZZ。

    
    
    -D	DirSearch style wordlist compatibility mode. Used in conjunction with -e flag. Replaces %EXT% in wordlist entry with each of the extensions provided by -e.
     -H "Name: Value"
       	Header "Name: Value", separated by colon. Multiple -H flags are accepted.
     -V	Show version information.
     -X string
       	HTTP method to use (default "GET")
     -ac
       	Automatically calibrate filtering options
     -c	Colorize output.
     -d string
       	POST data.
     -e string
       	Comma separated list of extensions to apply. Each extension provided will extend the wordlist entry once.
     -fc string
       	Filter HTTP status codes from response
     -fr string
       	Filter regexp
     -fs string
       	Filter HTTP response size
     -fw string
       	Filter by amount of words in response
     -k	TLS identity verification
     -mc string
       	Match HTTP status codes from respose, use "all" to match every response code. (default "200,204,301,302,307,401,403")
     -mr string
       	Match regexp
     -ms string
       	Match HTTP response size
     -mw string
       	Match amount of words in response
     -o string
       	Write output to file
     -of string
       	Output file format. Available formats: json, csv, ecsv (default "json")
     -p delay
       	Seconds of delay between requests, or a range of random delay. For example "0.1" or "0.1-2.0"
     -r	Follow redirects
     -s	Do not print additional information (silent mode)
     -sa
       	Stop on all error cases. Implies -sf and -se
     -se
       	Stop on spurious errors
     -sf
       	Stop when > 95% of responses return 403 Forbidden
     -t int
       	Number of concurrent threads. (default 40)
     -timeout int
       	HTTP request timeout in seconds. (default 10)
     -u string
       	Target URL
     -w string
       	Wordlist path
     -x string
       	HTTP Proxy URL

例如：

    
    
    ffuf -u https://example.org/FUZZ -w /path/to/wordlist

## 实例

###  **典型目录发现**

**![68747470733a2f2f61736369696e656d612e6f72672f612f3231313335302e706e67.png](https://image.3001.net/images/20190513/1557709765_5cd8c3c58e768.png!small)**

 **视频演示：**<https://asciinema.org/a/211350>

在URL（-u）末尾使用FUZZ关键字：

    
    
    ffuf -w /path/to/wordlist -u https://target/FUZZ

 **虚拟主机发现（没有DNS记录）**

**![68747470733a2f2f61736369696e656d612e6f72672f612f3231313336302e706e67.png](https://image.3001.net/images/20190513/1557709838_5cd8c40e98603.png!small)**

 **视频演示：**<https://asciinema.org/a/211360>

假设默认的虚拟主机响应大小为4242字节，我们可以过滤掉该大小的所有响应（-fs 4242），同时fuzz主机 - header：

    
    
    ffuf -w /path/to/vhost/wordlist -u https://target -H "Host: FUZZ" -fs 4242

### GET参数fuzz

GET参数名称模糊测试与目录发现非常相似，通过将FUZZ关键字定义为URL的一部分来工作。对于无效的GET参数名，这里也假设响应大小为4242字节。

    
    
    ffuf -w /path/to/paramnames.txt -u https://target/script.php?FUZZ=test_value -fs 4242

如果参数名称已知，则可以以相同方式对值进行模糊测试。此示例假定返回HTTP响应代码401的参数值错误。

    
    
    ffuf -w /path/to/values.txt -u https://target/script.php?valid_name=FUZZ -fc 401

### POST数据fuzz

这是一个非常简单的操作，同样使用FUZZ关键字。此示例仅对POST请求的一部分进行模糊测试。我们再次过滤掉401响应。

    
    
    ffuf -w /path/to/postdata.txt -X POST -d "username=admin\&password=FUZZ" https://target/login.php -fc 401

***参考来源：[GitHub](https://github.com/ffuf/ffuf)，FB小编secist编译，转载请注明来自FreeBuf.COM
**  

