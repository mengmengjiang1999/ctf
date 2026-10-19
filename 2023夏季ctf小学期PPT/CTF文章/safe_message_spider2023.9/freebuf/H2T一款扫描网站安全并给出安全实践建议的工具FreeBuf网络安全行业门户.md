**今天给大家介绍的是一款名叫h2t的开源工具，广大研究人员可以利用这款工具来对目标站点进行安全扫描，并获取专业的安全实践建议。**

![1.png](https://image.3001.net/images/20190330/1553954588_5c9f771ccf07d.png!small)

虽然h2t的使用非常简单，但它能够很大程度地帮助系统管理员提升网站的安全性。目前，h2t可以检测网站的header，并给出安全实践建议。

## 依赖组件

> [Python 3](https://www.python.org/download/releases/3.0/)
>
> [colorama](https://github.com/tartley/colorama)
>
> [requests](http://docs.python-requests.org/en/master/)

## 工具安装

    
    
    $ git clone <https://github.com/gildasio/h2t>
    
    $ cd h2t
    
    $ pip install -r requirements.txt
    
    $ ./h2t.py –h

## 工具使用

h2t提供下列两种操作子命令：list和scan。

    
    
    $./h2t.py -h
    
    usage:h2t.py [-h] {list,l,scan,s} ...
    
     
    
    h2t -HTTP Hardening Tool
    
     
    
    positional arguments:
    
      {list,l,scan,s}  sub-command help
    
        list (l)       show a list of available headers in h2tcatalog (that can
    
                       be used in scan subcommand-H option)
    
        scan (s)       scan url to hardening headers
    
     
    
    optional arguments:
    
      -h, --help       show this help message and exit

### List子命令

List子命令可以列举出h2t中所有支持的header，并提供相关的描述信息以及安全实践操作建议：

    
    
    $./h2t.py list -h
    
    usage:h2t.py list [-h] [-p PRINT [PRINT ...]] [-B]
    
                       [-a | -H HEADERS [HEADERS...]]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -p PRINT [PRINT ...], --print PRINT [PRINT...]
    
                            a list of additionalinformation about the headers to
    
                            print. For now thereare two options: description and
    
                            refs (you can useeither or both)
    
      -B, --no-banner       don't print the h2t banner
    
      -a, --all             list all available headers[default]
    
      -H HEADERS [HEADERS ...], --headers HEADERS[HEADERS ...]
    
                            a list of headers to look for in theh2t catalog

### Scan子命令

Scan子命令可以对目标站点进行安全扫描，并收集网站header：

    
    
    $./h2t.py scan -h
    
    usage:h2t.py scan [-h] [-v] [-a] [-g] [-b] [-H HEADERS [HEADERS ...]]
    
                       [-p PRINT [PRINT ...]]
    
                       [-i IGNORE_HEADERS[IGNORE_HEADERS ...]] [-B] [-E] [-n]
    
                       [-u USER_AGENT] [-r | -s]
    
                       url
    
     
    
    positional arguments:
    
      url                   url to look for
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -v, --verbose         increase output verbosity: -v printresponse headers,
    
                            -vv print response andrequest headers
    
      -a, --all             scan all cataloged headers[default]
    
      -g, --good            scan good headers only
    
      -b, --bad             scan bad headers only
    
      -H HEADERS [HEADERS ...], --headers HEADERS[HEADERS ...]
    
                            scan only these headers (see available inlist sub-    
                            command)
    
      -p PRINT [PRINT ...], --print PRINT [PRINT...]
    
                            a list of additionalinformation about the headers to
    
                            print. For now thereare two options: description and
    
                            refs (you can useeither or both)
    
      -i IGNORE_HEADERS [IGNORE_HEADERS ...],--ignore-headers IGNORE_HEADERS [IGNORE_HEADERS ...]
    
                            a list of headers toignore in the results
    
      -B, --no-banner       don't print the h2t banner
    
      -E, --no-explanation  don't print the h2t output explanation
    
      -o {normal,csv,json}, --output{normal,csv,json}
    
                            choose which outputformat to use (available: normal,
    
                            csv, json)
    
      -n, --no-redirect     don't follow http redirects
    
      -u USER_AGENT, --user-agent USER_AGENT
    
                            set user agent to scanrequest
    
      -k, --insecure        don't verify SSL certificate as valid
    
      -r, --recommendation  output only recommendations [default]
    
      -s, --status          output actual status (eg: existentheaders only)

## 结果输出

目前，该工具只有“普通模式”这一种数据输出模式：

> [+] 红色header为存在安全隐患的header，这些header可能会让你的网站陷入安全风险，或泄露某些敏感数据，我们建议大家修复这些问题。
>
> [+] 黄色header为正常的header，代表网站没有使用到的header，我们建议大家使用这些header。
>
> [-] 绿色header为正常的header，代表你网站已经在使用的header。

## 使用样例

![2.png](https://image.3001.net/images/20190330/1553954715_5c9f779bdf51f.png!small)

> 建议采用Cookie HTTP Only
>
> 建议采用Cookie over SSL/TLS
>
> 建议移除Server header
>
> 建议采用Referrer-Policy
>
> 已使用X-Frame-Options，无需额外操作
>
> 已使用X-XSS-Protection，无需额外操作

## 运行截图

List h2t分类：

![3.png](https://image.3001.net/images/20190330/1553954733_5c9f77ad35cae.png!small)

从文件获取扫描路径：

![4.png](https://image.3001.net/images/20190330/1553954741_5c9f77b51c0a6.png!small)

扫描url：

![5.png](https://image.3001.net/images/20190330/1553954750_5c9f77bec5d07.png!small)

Verbose模式扫描：

![6.png](https://image.3001.net/images/20190330/1553954759_5c9f77c74abb1.png!small)

Header信息：

![7.png](https://image.3001.net/images/20190330/1553954769_5c9f77d191b10.png!small)  

## 项目地址

> H2T：【[GitHub传送门](https://github.com/gildasio/h2t)】

***参考来源：[gildasio](https://github.com/gildasio/h2t)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

