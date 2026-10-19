## 关于log4j-scan

log4j-scan是一款功能强大的自动化漏洞检测工具，该工具主要针对的是Log4J远程代码执行漏洞-CVE-2021-44228，并且可以提供准确的扫描结果。在该工具的帮助下，广大研究人员可以轻松扫描大规模网络范围内主机，并确定主机是否受到Log4J远程代码执行漏洞的影响。

自Log4J远程代码执行漏洞（CVE-2021-44228）被曝光以来，我们不仅一直在对其进行研究，而且我们也一直在与客户一起致力于防范此漏洞，因此log4j-scan便应运而生，安全团队可以使用log4j-scan来扫描其基础设施中可能存在的Log4J远程代码执行漏洞，并测试可能导致在组织环境中执行代码的WAF旁路。

该工具“开箱即用”，支持DNS OOB回调，并且不需要设置DNS回调服务器。

## 功能介绍

> 1、支持URL列表扫描；
>
> 2、支持对超过60个HTTP请求Header进行模糊处理（而不是像以前看到的工具那样仅对3-4个Header进行模糊处理）；
>
> 3、针对HTTP POST数据参数进行模糊处理；
>
> 4、针对JSON数据参数进行模糊处理；
>
> 5、支持DNS回调以实现漏洞发现和验证；
>
> 6、Payload支持Web应用防火墙绕过；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/fullhunt/log4j-scan.git

依赖组件安装：

    
    
    $ pip3 install -r requirements.txt

## 工具参数选项

    
    
    $ python3 log4j-scan.py -h
    
    [•] CVE-2021-44228 - Apache Log4j RCE Scanner
    
    [•] Scanner provided by FullHunt.io - The Next-Gen Attack Surface Management Platform.
    
    [•] Secure your External Attack Surface with FullHunt.io.
    
    usage: log4j-scan.py [-h] [-u URL] [-p PROXY] [-l USEDLIST] [--request-type REQUEST_TYPE] [--headers-file HEADERS_FILE] [--run-all-tests] [--exclude-user-agent-fuzzing]
    
                         [--wait-time WAIT_TIME] [--waf-bypass] [--custom-waf-bypass-payload CUSTOM_WAF_BYPASS_PAYLOAD] [--test-CVE-2021-45046]
    
                         [--dns-callback-provider DNS_CALLBACK_PROVIDER] [--custom-dns-callback-host CUSTOM_DNS_CALLBACK_HOST] [--disable-http-redirects]
    
     
    
    optional arguments:
    
      -h, --help            显示帮助菜单和退出
    
      -u URL, --url URL     检测单个URL
    
      -p PROXY, --proxy PROXY
    
                            通过代理发送请求
    
      -l USEDLIST, --list USEDLIST
    
                            检测URL列表
    
      --request-type REQUEST_TYPE
    
                            请求类型: (get, post) - [默认: get].
    
      --headers-file HEADERS_FILE
    
                            Header模糊测试列表 - [默认: headers.txt].
    
      --run-all-tests          针对每一个URL运行所有可用的测试
    
      --exclude-user-agent-fuzzing
    
                            从模糊测试列表中排除User-Agent Header - 用于绕过针对User-Agent的弱检测
    
      --wait-time WAIT_TIME
    
                            等待所有URL处理完成的时间长度 - [默认: 5].
    
      --waf-bypass          WAF绕过Payload扩展扫描
    
      --custom-waf-bypass-payload CUSTOM_WAF_BYPASS_PAYLOAD
    
                            使用自定义WAF绕过Payload测试
    
      --test-CVE-2021-45046
    
                            使用CVE-2021-45046漏洞Payload进行测试 (检测Payload).
    
      --dns-callback-provider DNS_CALLBACK_PROVIDER
    
                            DNS回调提供商(选项: dnslog.cn, interact.sh) - [默认: interact.sh].
    
      --custom-dns-callback-host CUSTOM_DNS_CALLBACK_HOST
    
                            自定义DNS回调主机
    
      --disable-http-redirects
    
                            禁用HTTP重定向

## 工具使用

### 扫描单个URL

    
    
    $ python3 log4j-scan.py -u https://log4j.lab.secbot.local

### 使用所有的请求方法（GET、POST）扫描单个URL

    
    
    $ python3 log4j-scan.py -u https://log4j.lab.secbot.local --run-all-tests

### 发现环境中的WAF绕过

    
    
    $ python3 log4j-scan.py -u https://log4j.lab.secbot.local --waf-bypass

### 扫描URL列表

    
    
    $ python3 log4j-scan.py -l urls.txt

## Docker支持

    
    
    git clone https://github.com/fullhunt/log4j-scan.git
    
    cd log4j-scan
    
    sudo docker build -t log4j-scan .
    
    sudo docker run -it --rm log4j-scan
    
     
    
    # With URL list "urls.txt" in current directory
    
    docker run -it --rm -v $PWD:/data log4j-scan -l /data/urls.txt

## 工具运行截图

![](https://image.3001.net/images/20220117/1642427053_61e572ad27fb440c9c5b4.png!small)

![](https://image.3001.net/images/20220117/1642427058_61e572b2eeb89f579fb9c.png!small)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **log4j-scan：** 【[ _GitHub传送门_](https://github.com/fullhunt/log4j-scan)】

