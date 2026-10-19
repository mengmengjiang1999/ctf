![](https://image.3001.net/images/20220105/1641313150_61d4737e5fb22a0105618.jpg!small)

## 关于Craw*py

Craw*py是一款功能强大的内容发现工具，该工具基于Python语言开发，具备良好的跨平台特性，可以帮助广大研究人员轻松扫描并识别目标中的文件内容。

 **该工具与同类工具相比，不同之处在于：**

> 1、该工具支持异步工作，允许达到设备最大负载限度，所以运行速度非常快；
>
> 2、提供校准模式，自实现过滤器；
>
> 3、提供了一系列参数选项，可以帮助我们更好地进行测试；
>
> 4、支持给定状态代码和深度的递归扫描模式；
>
> 5、生成报告后，可以随时查看结果；
>
> 6、支持多个URL扫描；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并安装相关的工具依赖组件：

    
    
    git clone https://github.com/morph3/craw*py
    
    pip3 install -r requirements.txt
    
    或者
    
    python3 -m pip install -r requirements.txt

## 工具使用

    
    
    morph3 ➜ craw*py/ [main✗] λ python3 craw*py.py --help
    
    usage: craw*py.py [-h] [-u URL] [-w WORDLIST] [-t THREADS] [-rc RECURSIVE_CODES] [-rp RECURSIVE_PATHS] [-rd RECURSIVE_DEPTH] [-e EXTENSIONS] [-to TIMEOUT] [-follow] [-ac] [-fc FILTER_CODE] [-fs FILTER_SIZE] [-fw FILTER_WORD] [-fl FILTER_LINE] [-k] [-m MAX_RETRY]
    
                     [-H HEADERS] [-o OUTPUT_FILE] [-gr] [-l URL_LIST] [-lt LIST_THREADS] [-s] [-X HTTP_METHOD] [-p PROXY_SERVER]
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息和退出
    
      -u URL, --url URL      目标URL地址
    
      -w WORDLIST, --wordlist WORDLIST
    
                            使用的字典文件
    
      -t THREADS, --threads THREADS
    
                            信号量池的大小
    
      -rc RECURSIVE_CODES, --recursive-codes RECURSIVE_CODES
    
                            递归扫描所使用的递归扫描，例如301、302、307
    
      -rp RECURSIVE_PATHS, --recursive-paths RECURSIVE_PATHS
    
                            递归扫描的递归路径，一开始只扫描给定的递归路径，例如admin、support、js、buckup等
    
      -rd RECURSIVE_DEPTH, --recursive-depth RECURSIVE_DEPTH
    
                            递归扫描深度，例如2
    
      -e EXTENSIONS, --extension EXTENSIONS
    
                            在结尾添加后缀，可使用逗号分隔，例如-x .php,.html,.txt
    
      -to TIMEOUT, --timeout TIMEOUT
    
                            设置超时，不建议使用该选项
    
      -follow, --follow-redirects
    
                            跟随重定向Follow redirects
    
      -ac, --auto-calibrate
    
                            自动校准
    
      -fc FILTER_CODE, --filter-code FILTER_CODE
    
                            过滤器状态码
    
      -fs FILTER_SIZE, --filter-size FILTER_SIZE
    
                            过滤器大小
    
      -fw FILTER_WORD, --filter-word FILTER_WORD
    
                            过滤器关键词
    
      -fl FILTER_LINE, --filter-line FILTER_LINE
    
                            过滤器行
    
      -k, --ignore-ssl          忽略不受信任的SSL证书
    
      -m MAX_RETRY, --max-retry MAX_RETRY
    
                            重试最大值
    
      -H HEADERS, --headers HEADERS
    
                            设置Header
    
      -o OUTPUT_FILE, --output OUTPUT_FILE
    
                            输出文件夹
    
      -gr, --generate-report
    
                            如果你想要Craw*py生成报告，默认路径为craw*py/reports/<url>.txt
    
      -l URL_LIST, --list URL_LIST
    
                            通过multiprocessing -l ./urls.txt将URL列表作为输入
    
      -lt LIST_THREADS, --list-threads LIST_THREADS
    
                            使用URL列表运行时并行运行Crawby的线程数
    
      -s, --silent              不生成报告
    
      -X HTTP_METHOD, --http-method HTTP_METHOD
    
                            HTTP请求方法
    
      -p PROXY_SERVER, --proxy PROXY_SERVER
    
                            代理服务器，例如 'http://127.0.0.1:8080'

## 工具使用样例

    
    
    python3 craw*py.py -u https://facebook.com/FUZZ -w ./common.txt  -k -ac  -e .php,.html
    
    python3 craw*py.py -u https://google.com/FUZZ -w ./common.txt -k -fw 9,83 -rc 301,302 -rd 2 -ac
    
    python3 craw*py.py -u https://morph3sec.com/FUZZ -w ./common.txt -e .php,.html -t 20 -ac -k
    
    python3 craw*py.py -u https://google.com/FUZZ -w ./common.txt  -ac -gr
    
    python3 craw*py.py -u https://google.com/FUZZ -w ./common.txt  -ac -gr -o /tmp/test.txt
    
    sudo python3 craw*py.py -l urls.txt -lt 20 -gr -w ./common.txt -t 20 -o custom_reports -k -ac -s
    
    python3 craw*py.py -u https://google.com/FUZZ -w ./common.txt -ac -gr -rd 1 -rc 302,301 -rp admin,backup,support -k

## 报告样例

该工具生成的报告样例可以从以下地址获取：

> https://morph3sec.com/craw*py/example.html
>
> https://morph3sec.com/craw*py/example.txt

## 工具运行演示

### 演示一：简单运行

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/370172)】

### 演示二：启用自动校准和递归模式时的运行示例

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/370486)】

## 项目地址

 **Craw*py：** 【[ _GitHub传送门_](https://github.com/morph3/crawpy)】

  

