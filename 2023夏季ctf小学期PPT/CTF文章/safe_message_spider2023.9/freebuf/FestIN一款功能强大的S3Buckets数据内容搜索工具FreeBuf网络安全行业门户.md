![](https://image.3001.net/images/20200810/1596991499.png!small)

## FestIN

FestIN是一款功能强大的S3 Bucket数据内容搜索工具，该工具可以帮助研究人员发送公开S3
Buckets中的数据，我们只需给FestIN提供一个目标域名，剩下的工作FestIN将会帮助我们完成。

该工具能够对目标S3 Buckets执行大量的测试，并从下列地方收集数据：

> DNS
>
> Web页面（爬虫）
>
> S3 Bucket本身（类似S3重定向）

FestIN中包含了大量针对S3 Buckets的枚举和发现工具，FestIN的主要功能如下：

> 提供了大量技术用于发现Buckets：爬虫、DNS爬取和S3响应分析；
>
> 针对隧道请求提供了代理支持；
>
> 无需AWS凭证；
>
> 兼容任意S3提供商，不仅支持AWS；
>
> 支持配置自定义DNS服务器；
>
> 整合了高性能HTTP爬虫；
>
> 递归查询：DNS爬虫爬取到域名之后，会将其发送给S3和HTTP爬虫分析器；
>
> 支持监控模式，可实时监听新的域名；
>
> 允许将所有发现的域名存在单独的文件中，以供后续分析；
>
> 允许下载Bucket对象，并自动将其放入一个FullText搜索引擎（Redis搜索）；
>
> 支持限制域名扫描；

## 工具安装

### 使用Python安装

首先，该工具的正常运行要求Python 3.8环境。配置好Python环境之后，运行下列命令安装FestIN：

    
    
    $ pip install festin
    
    $ festin -h

### 使用Docker安装

    
    
    $ docker run --rm -it cr0hn/festin -h

## 工具选项

    
    
    $ festin -h
    
    usage: __main__.py [-h] [--version] [-f FILE_DOMAINS] [-w] [-c CONCURRENCY] [--no-links] [-T HTTP_TIMEOUT] [-M HTTP_MAX_RECURSION] [-dr DOMAIN_REGEX] [-rr RESULT_FILE] [-rd DISCOVERED_DOMAINS] [-ra RAW_DISCOVERED_DOMAINS]
    
                       [--tor] [--debug] [--no-print] [-q] [--index] [--index-server INDEX_SERVER] [-dn] [-ds DNS_RESOLVER]
    
                       [domains [domains ...]]
    
     
    
    Festin - the powered S3 bucket finder and content discover
    
     
    
    positional arguments:
    
      domains
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --version             show version
    
      -f FILE_DOMAINS, --file-domains FILE_DOMAINS
    
                            file with domains
    
      -w, --watch           watch for new domains in file domains '-f' option
    
      -c CONCURRENCY, --concurrency CONCURRENCY
    
                            max concurrency
    
     
    
    HTTP Probes:
    
      --no-links            extract web site links
    
      -T HTTP_TIMEOUT, --http-timeout HTTP_TIMEOUT
    
                            set timeout for http connections
    
      -M HTTP_MAX_RECURSION, --http-max-recursion HTTP_MAX_RECURSION
    
                            maximum recursison when follow links
    
      -dr DOMAIN_REGEX, --domain-regex DOMAIN_REGEX
    
                            only follow domains that matches this regex
    
     
    
    Results:
    
      -rr RESULT_FILE, --result-file RESULT_FILE
    
                            results file
    
      -rd DISCOVERED_DOMAINS, --discovered-domains DISCOVERED_DOMAINS
    
                            file name for storing new discovered after apply filters
    
      -ra RAW_DISCOVERED_DOMAINS, --raw-discovered-domains RAW_DISCOVERED_DOMAINS
    
                            file name for storing any domain without filters
    
     
    
    Connectivity:
    
      --tor                 Use Tor as proxy
    
     
    
    Display options:
    
      --debug               enable debug mode
    
      --no-print            doesn't print results in screen
    
      -q, --quiet           Use quiet mode
    
     
    
    Redis Search:
    
      --index               Download and index documents into Redis
    
      --index-server INDEX_SERVER
    
                            Redis Search ServerDefault: redis://localhost:6379
    
     
    
    DNS options:
    
      -dn, --no-dnsdiscover
    
                            not follow dns cnames
    
      -ds DNS_RESOLVER, --dns-resolver DNS_RESOLVER
    
                            comma separated custom domain name servers

## 工具使用

### 配置搜索域名

默认配置下，我们需要通过命令行参数向FestIN提供一个起始域名：

    
    
    > festin mydomain.com

但是，我们还需要配置一个外部域名文件列表：

    
    
    > cat domains.txt
    
    domain1.com
    
    domain2.com
    
    domain3.com
    
    > festin -f domains.txt

### 并发扫描

FestIN能够对域名执行大量测试，每一个测试都是并发执行的。默认配置下，并发数为5，如果你想要增加并发测试数量，可以通过“-c”选项进行配置：

    
    
    > festin -c 10 mydomain.com

### HTTP爬取配置

FestIN嵌入了一个小型爬虫来搜索S3 Buckets链接，爬虫的使用样例如下：

    
    
    > festin -T 20 -M 8 -dr .mydomain. mydomain.com

其中“-T”参数可以配置HTTP连接的超时，“-H”参数可以定义爬虫递归限制，“-dr”参数可以限制爬虫的扫描域名。

### 管理结果

当FestIN发现了大量有效信息之后，我们可以将数据存储至文件中，并导入到其他的工具，例如nmap等等。使用样例如下：

    
    
    > festin -rr festin.results -rd discovered-domains.txt -ra raw-domains.txt mydomain.txt

接下来，我们可以将其导入到Nmap之中进行下一步分析：

    
    
    > festin -rd domains.txt && nmap -Pn -A -iL domains.txt -oN nmap-domains.txt

### 使用代理

FestIN支持使用“--tor”参数来使用本地Tor代理，代理运行地址为127.0.0.1:9050。

    
    
    > tor &
    
    > festin --tor mydomain.com

## 项目地址

FestIN：【[ _GitHub传送门_](https://github.com/cr0hn/festin)】

