![](https://image.3001.net/images/20230516/1684252640_6463a7e0ad22f4a8df1be.png!small)

## 关于Katana

Katana是一款功能强大的下一代网络爬虫框架，在该工具的帮助下，广大研究人员可以轻松完成资源爬取和渗透测试阶段的信息收集任务。

## 功能介绍

> 1、快速且完全可配置的网络资源爬取；
>
> 2、支持标准模式和Headless模式；
>
> 3、JavaScript解析/爬取；
>
> 4、可自定义的自动化表单填充；
>
> 5、范围控制-预配置字段/正则表达式；
>
> 6、可自定义输出-预定义字段；
>
> 7、输入数据支持STDIN、URL和列表文件形式；
>
> 8、输出数据支持STDOUT、文件和JSON格式；

## 工具安装

Katana的使用需要Go v1 .18环境，安装并配置好Go环境之后，广大研究人员就可以运行下列命令来安装Katana：

    
    
    go install github.com/projectdiscovery/katana/cmd/katana@latest

或者直接访问该项目的【[
_Release页面_](https://github.com/projectdiscovery/katana/releases)】下载预编译的工具代码。

### Docker安装

    
    
    docker pull projectdiscovery/katana:latest

使用Docker以标准模式运行Katana：

    
    
    docker run projectdiscovery/katana:latest -u https://tesla.com

使用Docker以Headless模式运行Katana：

    
    
    docker run projectdiscovery/katana:latest -u https://tesla.com -system-chrome -headless

### Ubuntu安装

首先，我们需要使用下列命令安装该工具所需的依赖组件：

    
    
    sudo apt update
    
    sudo snap refresh
    
    sudo apt install zip curl wget git
    
    sudo snap install golang --classic
    
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -    
    sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    
    sudo apt update
    
    sudo apt install google-chrome-stable

然后运行下列命令安装Katana：

    
    
    go install github.com/projectdiscovery/katana/cmd/katana@latest

## 工具使用

### URL输入

    
    
    katana -u https://tesla.com

### 多目标URL输入（逗号分隔目标）

    
    
    katana -u https://tesla.com,https://google.com

### 列表输入

    
    
    $ cat url_list.txt
    
     
    
    https://tesla.com
    
    https://google.com

### STDIN管道输入

    
    
    echo https://tesla.com | katana
    
    
    cat domains | httpx | katana

## Katana运行结果样例

    
    
    katana -u https://youtube.com
    
     
    
       __        __                
    
      / /_____ _/ /____ ____  ___ _
    
     /  '_/ _  / __/ _  / _ \/ _  /
    
    /_/\_\\_,_/\__/\_,_/_//_/\_,_/ v0.0.1                     
    
     
    
          projectdiscovery.io
    
     
    
    [WRN] Use with caution. You are responsible for your actions.
    
    [WRN] Developers assume no liability and are not responsible for any misuse or damage.
    
    https://www.youtube.com/
    
    https://www.youtube.com/about/
    
    https://www.youtube.com/about/press/
    
    https://www.youtube.com/about/copyright/
    
    https://www.youtube.com/t/contact_us/
    
    https://www.youtube.com/creators/
    
    https://www.youtube.com/ads/
    
    https://www.youtube.com/t/terms
    
    https://www.youtube.com/t/privacy
    
    https://www.youtube.com/about/policies/
    
    https://www.youtube.com/howyoutubeworks?utm_campaign=ytgen&utm_source=ythp&utm_medium=LeftNav&utm_content=txt&u=https%3A%2F%2Fwww.youtube.com%2Fhowyoutubeworks%3Futm_source%3Dythp%26utm_medium%3DLeftNav%26utm_campaign%3Dytgen
    
    https://www.youtube.com/new
    
    https://m.youtube.com/
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/desktop_polymer.vflset/desktop_polymer.js
    
    https://www.youtube.com/s/desktop/4965577f/cssbin/www-main-desktop-home-page-skeleton.css
    
    https://www.youtube.com/s/desktop/4965577f/cssbin/www-onepick.css
    
    https://www.youtube.com/s/_/ytmainappweb/_/ss/k=ytmainappweb.kevlar_base.0Zo5FUcPkCg.L.B1.O/am=gAE/d=0/rs=AGKMywG5nh5Qp-BGPbOaI1evhF5BVGRZGA
    
    https://www.youtube.com/opensearch?locale=en_GB
    
    https://www.youtube.com/manifest.webmanifest
    
    https://www.youtube.com/s/desktop/4965577f/cssbin/www-main-desktop-watch-page-skeleton.css
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/web-animations-next-lite.min.vflset/web-animations-next-lite.min.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/custom-elements-es5-adapter.vflset/custom-elements-es5-adapter.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/webcomponents-sd.vflset/webcomponents-sd.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/intersection-observer.min.vflset/intersection-observer.min.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/scheduler.vflset/scheduler.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/www-i18n-constants-en_GB.vflset/www-i18n-constants.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/www-tampering.vflset/www-tampering.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/spf.vflset/spf.js
    
    https://www.youtube.com/s/desktop/4965577f/jsbin/network.vflset/network.js
    
    https://www.youtube.com/howyoutubeworks/
    
    https://www.youtube.com/trends/
    
    https://www.youtube.com/jobs/
    
    https://www.youtube.com/kids/

## JSON格式输出

    
    
    katana -u https://example.com -json | jq .
    
    
    {
    
      "timestamp": "2023-03-20T16:23:58.027559+05:30",
    
      "request": {
    
        "method": "GET",
    
        "endpoint": "https://example.com",
    
        "raw": "GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36\r\nAccept-Encoding: gzip\r\n\r\n"
    
      },
    
      "response": {
    
        "status_code": 200,
    
        "headers": {
    
          "accept_ranges": "bytes",
    
          "expires": "Mon, 27 Mar 2023 10:53:58 GMT",
    
          "last_modified": "Thu, 17 Oct 2019 07:18:26 GMT",
    
          "content_type": "text/html; charset=UTF-8",
    
          "server": "ECS (dcb/7EA3)",
    
          "vary": "Accept-Encoding",
    
          "etag": "\"3147526947\"",
    
          "cache_control": "max-age=604800",
    
          "x_cache": "HIT",
    
          "date": "Mon, 20 Mar 2023 10:53:58 GMT",
    
          "age": "331239"
    
        },
    
        "body": "<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset=\"utf-8\" />\n    <meta http-equiv=\"Content-type\" content=\"text/html; charset=utf-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n    <style type=\"text/css\">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: -apple-system, system-ui, BlinkMacSystemFont, \"Segoe UI\", \"Open Sans\", \"Helvetica Neue\", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 2em;\n        background-color: #fdfdff;\n        border-radius: 0.5em;\n        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n    @media (max-width: 700px) {\n        div {\n            margin: 0 auto;\n            width: auto;\n        }\n    }\n    </style>    \n</head>\n\n<body>\n<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href=\"https://www.iana.org/domains/example\">More information...</a></p>\n</div>\n</body>\n</html>\n",
    
        "technologies": [
    
          "Azure",
    
          "Amazon ECS",
    
          "Amazon Web Services",
    
          "Docker",
    
          "Azure CDN"
    
        ],
    
        "raw": "HTTP/1.1 200 OK\r\nContent-Length: 1256\r\nAccept-Ranges: bytes\r\nAge: 331239\r\nCache-Control: max-age=604800\r\nContent-Type: text/html; charset=UTF-8\r\nDate: Mon, 20 Mar 2023 10:53:58 GMT\r\nEtag: \"3147526947\"\r\nExpires: Mon, 27 Mar 2023 10:53:58 GMT\r\nLast-Modified: Thu, 17 Oct 2019 07:18:26 GMT\r\nServer: ECS (dcb/7EA3)\r\nVary: Accept-Encoding\r\nX-Cache: HIT\r\n\r\n<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset=\"utf-8\" />\n    <meta http-equiv=\"Content-type\" content=\"text/html; charset=utf-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n    <style type=\"text/css\">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: -apple-system, system-ui, BlinkMacSystemFont, \"Segoe UI\", \"Open Sans\", \"Helvetica Neue\", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 2em;\n        background-color: #fdfdff;\n        border-radius: 0.5em;\n        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n    @media (max-width: 700px) {\n        div {\n            margin: 0 auto;\n            width: auto;\n        }\n    }\n    </style>    \n</head>\n\n<body>\n<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href=\"https://www.iana.org/domains/example\">More information...</a></p>\n</div>\n</body>\n</html>\n"
    
      }
    
    }

## 工具运行截图

![](https://image.3001.net/images/20230516/1684252786_6463a872e179730bbc1c5.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/projectdiscovery/katana/blob/main/LICENSE.md)开源许可证协议。

## 项目地址

 **Katana** ：【[ _GitHub传送门_](https://github.com/projectdiscovery/katana)】

