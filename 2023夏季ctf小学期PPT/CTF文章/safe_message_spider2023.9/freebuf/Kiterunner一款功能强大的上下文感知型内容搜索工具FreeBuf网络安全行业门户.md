![](https://image.3001.net/images/20210513/1620898552_609cf2f84ae85a5dcaaed.png!small)

## 关于Kiterunner

长期以来，跟“内容搜索”相关的技术一直都是基于文件和文件夹查找来实现的。虽然这种方法对于托管静态文件或响应文件路径的Web服务器来说是有效的，但对于现代Web应用程序来说，这种方法的有效性就没那么高了，尤其是那些使用了API来实现功能的Web应用程序。

随着时间的推移，越来越多的研究人员开始投身于加快内容发现工具的开发上，以便使用更大型的字典，但这种方式仍然没有本质上的革新。

Kiterunner这款工具不仅能够以闪电般的速度执行传统的内容扫描技术，而且还能够在现代应用程序中爆破路由或节点。

现代应用程序框架，例如Flask、Rails、Express、Django等，都遵循显式定义路由的范式，路由需要特定的HTTP方法、头、参数和值。当使用传统的内容发现工具时，这样的路由常常会被遗漏，而且很难被发现。

通过整理Swagger规范的数据集并将其压缩到我们自己的模式中，Kiterunner可以使用此数据集，并通过为它发送的每个请求发送正确的HTTP方法、头、路径、参数和值来爆破API节点。

## 工具安装

### 下载Release版本

广大研究人员可以直接点击【[
_这里_](https://github.com/assetnote/kiterunner/releases)】下载该工具的预编译拷贝。

### 源码构建

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/assetnote/kiterunner.git

接下来，构建源码：

    
    
    make build

设置代码符号链接：

    
    
    ln -s $(pwd)/dist/kr /usr/local/bin/kr

编译字典：

    
    
    kr kb compile routes.json routes.kite

执行扫描：

    
    
    kr scan hosts.txt -w routes.kite -x 20 -j 100 --ignore-length=1053

## JSON格式数据集

-[ _rootes-large.json_](https://wordlists-cdn.assetnote.io/rawdata/kiterunner/routes-large.json.tar.gz)（压缩后118MB，解压后2.6GB）

-[ _rootes-small.json_](https://wordlists-cdn.assetnote.io/rawdata/kiterunner/routes-small.json.tar.gz)（压缩后14MB，解压后228MB）

或者，我们也可以直接下载.kite文件：

-[ _routes-large.kite_](https://wordlists-cdn.assetnote.io/data/kiterunner/routes-large.kite.tar.gz)（压缩后40MB，解压后182MB）

-[ _routes-small.kite_](https://wordlists-cdn.assetnote.io/data/kiterunner/routes-small.kite.tar.gz)（压缩后2MB，解压后35MB）

## 工具使用

### 快速扫描

其中的<imput>可以是一个文件、域名或者URI：

    
    
    kr [scan|brute] <input> [flags]

有一个待扫描主机的列表，但是没有字典：

    
    
    kr scan hosts.txt -A=apiroutes-210328:20000 -x 5 -j 100 --fail-status-codes 400,401,404,403,501,502,426,411

有自己的字典：

    
    
    kr scan target.com -w routes.kite -A=apiroutes-210328:20000 -x 20 -j 1 --fail-status-codes 400,401,404,403,501,502,426,411

使用前20000个单词进行常规爆破：

    
    
    kr brute https://target.com/subapp/ -A=aspx-210328:20000 -x 20 -j 1

使用目录搜索风格的字典和%EXT%结合扫描：

    
    
    kr brute https://target.com/subapp/ -w dirsearch.txt -x 20 -j 1 -exml,asp,aspx,ashx -D

### 命令行选项

    
    
    Usage:
    
      kite scan [flags]
    
     
    
    Flags:
    
      -A, --assetnote-wordlist strings    use the wordlists from wordlist.assetnote.io. specify the type/name to use, e.g. apiroutes-210228. You can specify an additional maxlength to use only the first N values in the wordlist, e.g. apiroutes-210228;20000 will only use the first 20000 lines in that wordlist
    
          --blacklist-domain strings      domains that are blacklisted for redirects. We will not follow redirects to these domains
    
          --delay duration                delay to place inbetween requests to a single host
    
          --disable-precheck              whether to skip host discovery
    
          --fail-status-codes ints        which status codes blacklist as fail. if this is set, this will override success-status-codes
    
          --filter-api strings            only scan apis matching this ksuid
    
          --force-method string           whether to ignore the methods specified in the ogl file and force this method
    
      -H, --header strings                headers to add to requests (default [x-forwarded-for: 127.0.0.1])
    
      -h, --help                          help for scan
    
          --ignore-length strings         a range of content length bytes to ignore. you can have multiple. e.g. 100-105 or 1234 or 123,34-53. This is inclusive on both ends
    
          --kitebuilder-full-scan         perform a full scan without first performing a phase scan.
    
      -w, --kitebuilder-list strings      ogl wordlist to use for scanning
    
      -x, --max-connection-per-host int   max connections to a single host (default 3)
    
      -j, --max-parallel-hosts int        max number of concurrent hosts to scan at once (default 50)
    
          --max-redirects int             maximum number of redirects to follow (default 3)
    
      -d, --preflight-depth int           when performing preflight checks, what directory depth do we attempt to check. 0 means that only the docroot is checked (default 1)
    
          --profile-name string           name for profile output file
    
          --progress                      a progress bar while scanning. by default enabled only on Stderr (default true)
    
          --quarantine-threshold int      if the host return N consecutive hits, we quarantine the host as wildcard. Set to 0 to disable (default 10)
    
          --success-status-codes ints     which status codes whitelist as success. this is the default mode
    
      -t, --timeout duration              timeout to use on all requests (default 3s)
    
          --user-agent string             user agent to use for requests (default "Chrome. Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36")
    
          --wildcard-detection            can be set to false to disable wildcard redirect detection (default true)
    
     
    
    Global Flags:
    
          --config string    config file (default is $HOME/.kiterunner.yaml)
    
      -o, --output string    output format. can be json,text,pretty (default "pretty")
    
      -q, --quiet            quiet mode. will mute unecessarry pretty text
    
      -v, --verbose string   level of logging verbosity. can be error,info,debug,trace (default "info")

### 爆破选项

    
    
    bruteforce flags (all the flags above +)
    
     
    
      -D, --dirsearch-compat              this will replace %EXT% with the extensions provided. backwards compat with dirsearch because shubs loves him some dirsearch
    
      -e, --extensions strings            extensions to append while scanning
    
      -w, --wordlist strings              normal wordlist to use for scanning

### API扫描

扫描单个目标：

    
    
    kr scan https://target.com:8443/ -w routes.kite -A=apiroutes-210228:20000 -x 10 --ignore-length=34

扫描单个目标，并尝试http和https：

    
    
    kr scan target.com -w routes.kite -A=apiroutes-210228:20000 -x 10 --ignore-length=34

扫描目标列表：

    
    
    kr scan targets.txt -w routes.kite -A=apiroutes-210228:20000 -x 10 --ignore-length=34

## 项目地址

Kiterunner：【[ _GitHub传送门_](https://github.com/assetnote/kiterunner)】

