## 前言

 **htrace.sh是一个用于调试http/https流量跟踪，响应头和mixed-content（混合内容）和检查域名的简单shell脚本。它允许你验证域配置，并能为你发现配置中存在的错误（例如重定向循环）。此外，它还会为你显示有关ssl的基本配置信息（如果可用），并支持使用Nmap脚本执行安全扫描，以及其它一些外部安全工具，例如Ssllabs和Mozilla
Observatory等。**

![htrace.sh示意图](https://image.3001.net/images/20180810/1533853867_5b6cc0ab469a9.png!small)

## 特性

> 检查域配置（Web服务器/反向代理）；
>
> 重定向分析，例如消除重定向循环；
>
> 检查每个请求的响应头；
>
> 检查基本的ssl配置：确认证书（date，cn，san）以及验证ssl连接；
>
> 为混合内容扫描域；
>
> 使用Nmap NSE库扫描域；
>
> 使用外部安全工具扫描域：Mozilla Observatory和SSL Labs API。

## 使用方法

    
    
    # Clone this repository
    git clone https://github.com/trimstray/htrace.sh
    
    # Go into the repository
    cd htrace.sh
    
    # Install
    ./setup.sh install
    
    # Run the app
    htrace.sh --domain https://google.com

## 外部工具

htrace.sh支持用于安全扫描的外部工具：

> **Mozilla Observatory -**
> 网站安全分析工具，旨在鼓励开发者和系统管理员增强自己网站的安全配置。使用参数：`--format=report --rescan --zero
> --quiet`
>
> **Ssllabs** \- HTTPS检测工具。使用参数：`-quiet -grade`
>
> **mixed-content-scan** \- 为Mixed Content检查启用https站点的CLI工具。使用参数：`-user-agent
> \"$_user_agent\" --no-check-certificate`
>
> **Nmap NSE Library** \- 使用Nmap提供自动安全扫描。

使用的脚本有：

> http-auth-finder
>
> http-chrono
>
> http-cookie-flags
>
> http-cors
>
> http-cross-domain-policy
>
> http-csrf
>
> http-dombased-xss
>
> http-git
>
> http-grep
>
> http-internal-ip-disclosure
>
> http-jsonp-detection
>
> http-malware-host
>
> http-methods
>
> http-passwd
>
> http-phpself-xss
>
> http-php-version
>
> http-robots.txt
>
> http-sitemap-generator
>
> http-shellshock
>
> http-stored-xss
>
> http-unsafe-output-escaping
>
> http-useragent-tester
>
> http-vhosts
>
> http-xssed
>
> ssl-enum-ciphers
>
> whois-ip

## 报告

如果你希望生成的报告格式为html，你可以使用[ansi2html.sh](https://raw.githubusercontent.com/pixelb/scripts/master/scripts/ansi2html.sh)脚本来实现。

    
    
    htrace.sh -d https://nmap.org -s -h | ansi2html --bg=dark > report.html

## Docker

配置被包含在build/Dockerfile文件中。

### Build image

    
    
    cd htrace.sh/build
    docker build --rm -t htrace.sh -f Dockerfile 

### Run container

    
    
    docker run --rm -it --name htrace.sh htrace.sh -d http://nmap.org -h

## 安装环境

> GNU/Linux(已在Debian和CentOS上进行测试)
>
> [Bash](https://www.gnu.org/software/bash/)（测试的版本为4.4.19）
>
> [Curl](https://curl.haxx.se/)（≥ 7.52.0）
>
> [OpenSSL](https://www.openssl.org/)
>
> [Mozilla Observatory](https://github.com/mozilla/http-observatory)
>
> [Ssllabs](https://github.com/ssllabs/ssllabs-scan)
>
> [mixed-content-scan](https://github.com/bramus/mixed-content-scan)
>
> [Nmap](https://nmap.org/)

## 参数

    
    
    htrace.sh v1.0.6
    
    Usage:
        htrace.sh <option|long-option>
    
      Examples:
        htrace.sh --domain https://example.com
        htrace.sh --domain https://example.com -s -h --scan ssllabs
    
      Options:
            --help                                显示帮助信息
            -d|--domain <domain_name>             设置域名
            -s|--ssl                              显示ssl 服务器/连接 参数
            -h|--headers                          显示响应头
            --scan <all|observatory|ssllabs>      使用外部安全工具扫描域
            --mixed-content                       为混合内容扫描网站
            --nse                                 使用nmap nse library扫描网站
            --user-agent <val>                    设置'User-Agent'头
            --max-redirects <num>                 设置最大重定向次数 (默认:10)
            --timeout <num>                       设置最大超时时间 (默认:15)

 ***参考来源：[GitHub](https://github.com/trimstray/htrace.sh)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

