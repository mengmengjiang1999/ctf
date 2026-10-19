![](https://image.3001.net/images/20200409/1586365470_5e8e041ea28a3.jpg!small)

**FProbe是一款HTTP/HTTPS服务器快速探测工具，广大研究人员只需要给FProbe提供一个域名或子域名列表，它就可以帮助我们探测目标域名后台运行的是HTTP服务器还是HTTPS服务器了。**

##  工具安装

    
    
    GO111MODULE=on go get -u github.com/theblackturtle/fprobe

##  功能介绍

> 1、该工具可以接受域名/子域名列表，并探测其后端的HTTP/HTTPS服务器；
>
> 2、在运行时优化RAM和CPU；
>
> 3、支持域名特殊端口；
>
> 4、详细的JSON格式，包含Status Code、Content Type和Location；

##  工具使用

    
    
    Usage of fprobe:
    
          -c int
    
                Concurrency (default 50)
    
          -i string
    
                Input file (default is stdin) (default "-")
    
          -l    Use ports in the same line (google.com,2087,2086)
    
          -p value
    
                add additional probe (proto:port)
    
          -s    skip the default probes (http:80 and https:443)
    
          -t int
    
                Timeout (seconds) (default 9)
    
          -v    Turn on verbose

##  基础使用

###  Stdin输入：

    
    
    ❯ cat domains.txt | fprobe

###  文件输入：

    
    
    ❯ fprobe -i domains.txt

###  并发性：

    
    
    ❯ cat domains.txt | fprobe -c 200

##  使用内联端口

如果你想要针对每一个域名来指定特殊端口，你可以使用-l标签。除此之外，你还可以使用这个功能来解析Nmap/Masscan输出，并对数据进行重新格式化。

###  输入（domains.txt）：

    
    
    google.com,2087,2086,8880,2082,443,80,2052,2096,2083,8080,8443,2095,2053
    
        yahoo.com,2087,2086,8880,2082,443,80,2052,2096,2083,8080,8443,2095,2053
    
        sport.yahoo.com,2086,443,2096,2053,8080,2082,80,2083,8443,2052,2087,2095,8880

###  命令：

    
    
    ❯ cat domains.txt | fprobe -l

###  超时：

    
    
    ❯ cat domains.txt | fprobe -t 10

###  指定特殊端口：

    
    
    ❯ cat domains.txt | fprobe -p http:8080 -p https:8443

###  检测可用的URL：

❯ echo '<https://google.com/path1?param=1>' | fprobe

<https://google.com/path1?param=1>

###  使用内置端口收集功能（默认包含80和443）：

> 1、Medium: 8000, 8080, 8443
>
> 2、Large: 81, 591, 2082, 2087, 2095, 2096, 3000, 8000, 8001, 8008, 8080,
> 8083, 8443, 8834, 8888
>
> 3、XLarge: 81, 300, 591, 593, 832, 981, 1010, 1311, 2082, 2087, 2095, 2096,
> 2480, 3000, 3128, 3333, 4243, 4567, 4711, 4712, 4993, 5000, 5104, 5108,
> 5800, 6543, 7000, 7396, 7474, 8000, 8001, 8008, 8014, 8042, 8069, 8080,
> 8081, 8088, 8090, 8091, 8118, 8123, 8172, 8222, 8243, 8280, 8281, 8333,
> 8443, 8500, 8834, 8880, 8888, 8983, 9000, 9043, 9060, 9080, 9090, 9091,
> 9200, 9443, 9800, 9981, 12443, 16080, 18091, 18092, 20720, 28017
    
    
    ❯ cat domains.txt | fprobe -p medium/large/xlarge

###  跳过默认探测：

如果你不想探测HTTP（80端口）或HTTPS（443端口），你可以使用-s标签：

    
    
    ❯ cat domains.txt | fprobe -s

###  Verbose

Verbose输出数据为JSON格式数据，其中还会包含额外的Header，例如Status Code、Content Type、Location。

    
    
    ❯ cat domains.txt | fprobe -v
    
        {"site":"[http://google.com](http://google.com/)","status_code":301,"server":"gws","content_type":"text/html; charset=UTF-8","location":"<http://www.google.com/>"}
    
        {"site":"[https://google.com](https://google.com/)","status_code":301,"server":"gws","content_type":"text/html; charset=UTF-8","location":"<https://www.google.com/>"}

##  项目地址

> FProbe：【[GitHub传送门](https://github.com/theblackturtle/fprobe)】

 ***
参考来源：[theblackturtle](https://github.com/theblackturtle/fprobe)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

