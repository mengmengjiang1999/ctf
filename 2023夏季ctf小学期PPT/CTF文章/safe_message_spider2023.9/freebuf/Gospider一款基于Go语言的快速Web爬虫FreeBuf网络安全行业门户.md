![](https://image.3001.net/images/20200401/1585750919_5e84a387e44ed.png!small)

**Gospider是一款运行速度非常快的Web爬虫程序，Gospider采用Go语言开发。**

##  功能介绍

> 1、快速Web资源爬取
>
> 2、爆破与解析sitemap.xml
>
> 3、解析robots.txt
>
> 4、生成和验证来自JavaScript文件的链接
>
> 5、链接搜索工具
>
> 6、根据响应源搜索AWS-S3
>
> 7、根据响应源搜索子域名
>
> 8、从Wayback Machine, Common Crawl, Virus Total, Alien Vault获取URL资源
>
> 9、格式化输出，可配合Grep使用
>
> 10、支持Burp输入
>
> 11、支持并行爬取多个站点
>
> 12、随机移动端/Web User-Agent

##  工具安装

    
    
    go get -u github.com/jaeles-project/gospider

##  工具使用

Fast web spider written in Go - v1.1.0 by @theblackturtle

Usage:

    
    
      gospider [flags]

Flags:

    
    
      -s, --site string            待爬取的站点地址
    
          -S, --sites string           待爬取的站点列表
    
          -p, --proxy string          代理(例如: [http://127.0.0.1:8080](http://127.0.0.1:8080/))
    
          -o, --output string         输出目录 
    
          -u, --user-agent string      需要使用的User-Agent
    
                                        web: 随机Web User-Agent
    
                                        mobi: 随机移动端User-Agent
    
              --cookie string         设置Cookie (testA=a; testB=b)
    
          -H, --header stringArray     设置Header
    
              --burp string          从Burp Http请求加载Header和Cookie
    
              --blacklist string       URL黑名单正则式
    
          -t, --threads int           并行线程数量 (默认为1)
    
          -c, --concurrent int         匹配域名允许的最大并发请求数（默认为5）
    
          -d, --depth int              限制爬取的最大深度(设置为0则表示无限递归，默认为1)
    
          -k, --delay int              Delay是在向匹配域名发送新请求之前需要等待的时间间隔 (秒)
    
          -K, --random-delay int       RandomDelay是在创建新请求之前需要等待的额外随机等待持续时间 (秒)
    
          -m, --timeout int            请求超时(秒) (默认为10)
    
              --sitemap               尝试爬取sitemap.xml
    
              --robots                尝试爬取robots.txt 
    
          -a, --other-source           从第三方查找URL (Archive.org, CommonCrawl.org, VirusTotal.com)
    
          -w, --include-subs           包含从第三方爬取的子域名，默认为主域名
    
          -r, --include-other-source   包含其他资源的URL
    
              --debug                启用调试模式
    
          -v, --verbose                启用verbose模式
    
              --no-redirect            禁用重定向
    
              --version                检查版本
    
          -h, --help                   显示帮助信息
    
    # 

##  样本命令

###  爬取单个网站：

    
    
    gospider -s "https://google.com/" -o output -c 10 -d 1

###  爬取网站列表：

    
    
    gospider -S sites.txt -o output -c 10 -d 1

###  同时爬取20个站点，每个站点分配10个bot：

    
    
    gospider -S sites.txt -o output -c 10 -d 1 -t 20

###  从第三方(Archive.org, CommonCrawl.org, VirusTotal.com, AlienVault.com)获取URL：

    
    
    gospider -s "https://google.com/" -o output -c 10 -d 1 --other-source

###  从第三方(Archive.org, CommonCrawl.org, VirusTotal.com,
AlienVault.com)获取URL并包含子域名：

    
    
    gospider -s "https://google.com/" -o output -c 10 -d 1 --other-source --include-subs

###  使用自定义Header/Cookie：

gospider -s "<https://google.com/>" -o output -c 10 -d 1 --other-source -H
"Accept: */*" -H "Test: test" --cookie "testA=a; testB=b"

gospider -s "<https://google.com/>" -o output -c 10 -d 1 --other-source --burp
burp_req.txt

###  URL/文件后缀黑名单

    
    
    gospider -s "https://google.com/" -o output -c 10 -d 1 --blacklist ".(woff|pdf)"

注意：Gospider默认配置下的黑名单为：.(jpg|jpeg|gif|css|tif|tiff|png|ttf|woff|woff2|ico)。

##  工具使用样例

视频地址：【[点我观看](https://asciinema.org/a/301827)】

##  项目地址

> Gospider：【[GitHub传送门](https://github.com/jaeles-project/gospider)】

 *** 参考来源：[jaeles-project](https://github.com/jaeles-project/gospider)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

