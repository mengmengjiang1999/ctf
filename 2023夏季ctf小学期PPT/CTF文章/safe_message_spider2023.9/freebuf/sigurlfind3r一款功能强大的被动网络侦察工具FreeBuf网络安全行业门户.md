![](https://image.3001.net/images/20210904/1630764365_61337d4d264bb241155a1.jpg!small)

## 关于sigurlfind3r

sigurlfind3r是一款功能强大的被动网络侦察工具，该工具主要针对的是已知的URL搜索，并且可以使用各种在线源并以被动方式收集URL列表。

## 功能介绍

> 收集已知URL：可从[ _AlienVault's OTX_](https://otx.alienvault.com/)、[ _Common
> Crawl_](https://commoncrawl.org/)、[ _URLScan_](https://urlscan.io/)、[
> _Github_](https://github.com/)和[ _Wayback
> Machine_](https://archive.org/web/)获取数据，可以从txt获取禁用路径；
>
> 降低噪声：通过正则表达式过滤URL，移除URL中的重复页面；
>
> 输出至stdout或存储至文件；

## 工具安装

### 预构建源码下载

我们可以直接访问该项目的【[
_Releases页面_](https://github.com/signedsecurity/sigurlfind3r/releases/)】下载针对自己平台的预构建源码。下载完成之后，提取源码文件，并将其移动指$PATH路径下即可直接使用。

### 源码获取

sigurlfind3r要求本地主机安装并配置好Go v1.14+环境，配置好后就可以直接使用下列命令下载并安装sigurlfind3r了：

    
    
    GO111MODULE=on go get -u -v github.com/signedsecurity/sigurlfind3r/cmd/sigurlfind3r

### 从GitHub安装

    
    
    git clone https://github.com/signedsecurity/sigurlfind3r.git && \
    cd sigurlfind3r/cmd/sigurlfind3r/ && \
    go build; mv sigurlfind3r /usr/local/bin/ && \
    sigurlfind3r -h

## 工具配置

sigurlfind3r在安装完成之后，还需要进行适当的配置。这里你将需要获取API密钥，这个API密钥存储在$HOME/.config/sigurlfind3r/conf.yaml之中。参考样例如下：

    
    
    version: 1.5.0
    sources:
        - commoncrawl
        - github
        - otx
        - urlscan
        - wayback
        - waybackrobots
    keys:
        github:
            - d23a554bbc1aabb208c9acfbd2dd41ce7fc9db39
            - asdsd54bbc1aabb208c9acfbd2dd41ce7fc9db39

## 工具使用

提示：从GitHub爬取URL的话可能速度会比较慢。

    
    
    sigurlfind3r -h

上述命令将会显示如下信息：

    
    
    _                  _  __ _           _ _____
    
     ___(_) __ _ _   _ _ __| |/ _(_)_ __   __| |___ / _ __
    
    / __| |/ _` | | | | '__| | |_| | '_ \ / _` | |_ \| '__|
    
    \__ \ | (_| | |_| | |  | |  _| | | | | (_| |___) | |
    
    |___/_|\__, |\__,_|_|  |_|_| |_|_| |_|\__,_|____/|_| 1.5.0
    
           |___/
    USAGE:
      sigurlfind3r [OPTIONS]
    OPTIONS:
       -d, --domain            domain to fetch urls for
      -eS, --exclude-sources   comma(,) separated list of sources to exclude
       -f, --filter            URL filtering regex
      -iS, --include-subs      include subdomains' urls
      -lS, --list-sources      list all the available sources
      -nC, --no-color          no color mode
       -s  --silent            silent mode: output urls only
      -uS, --use-sources       comma(,) separated list of sources to use
       -o, --output            output file

## 使用样例

### 基础使用

    
    
    sigurlfind3r -d tesla.com

### 正则表达式过滤URL

    
    
    sigurlfind3r -d tesla.com -f ".(jpg|jpeg|gif|png|ico|css|eot|tif|tiff|ttf|woff|woff2)"

### 包含子域名URL

    
    
    sigurlfind3r -d tesla.com -iS

## 项目地址

>  **sigurlfind3r：** 【[
> _GitHub传送门_](https://github.com/signedsecurity/sigurlfind3r)】

