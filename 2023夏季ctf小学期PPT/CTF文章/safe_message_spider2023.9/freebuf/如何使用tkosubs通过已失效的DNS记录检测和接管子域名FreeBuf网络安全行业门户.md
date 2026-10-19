## 关于tko-subs

tko-subs是一款功能强大的子域名检测工具，该工具可以利用已失效的DNS记录检测和接管目标子域名。该工具具备以下三个功能。

>
> 检测一个目标子域名是否能够被接管。检测指向CMS提供商的CNAME是否能够被接管，检测指向不存在域名的空CNAME，检测一个或多个指向域名服务器的错误NS记录。
>
> 通过使用“-takeover”参数来接管目标子域名。
>
> 指定我们自己的CMS提供商，并通过 _providers-data.csv_
> 文件检查其安全性。在该文件中，需提供CMS迷哦改昵称、CNAME值以及需要查询的字符串信息。

## 工具要求&安装

首先，我们需要在本地设备上安装并配置好Go环境。接下来，再使用下列命令下载并安装该工具：

    
    
    go get github.com/anshumanbh/tko-subs

工具下载完成之后，在命令行终端中切换至该项目根目录，并运行下列命令查看该工具帮助信息：

    
    
    tko-subs -h

接下来，我们要做的就是获取下列信息：

> GitHub的个人访问令牌（创建地址：[
> _https://github.com/settings/tokens_](https://github.com/settings/tokens%EF%BC%89)）
>
> Heroku的用户名和API密钥
>
> Heroku应用程序名称【[
> _参考资料_](https://gist.github.com/wh1tney/2ad13aa5fbdd83f6a489)】

下面给出的是该工具所需构建的Go包：

    
    
    go get github.com/bgentry/heroku-go
    go get github.com/gocarina/gocsv
    go get github.com/google/go-github/github
    go get github.com/olekukonko/tablewriter
    go get golang.org/x/net/publicsuffix
    go get golang.org/x/oauth2
    go get github.com/miekg/dns

## 工具运行

安装好工具之后，在命令行终端中切换至该项目根目录，并运行下列命令：

    
    
    tko-subs -domains=domains.txt -data=providers-data.csv -output=output.csv

如果你想同时实现子域名接管，则可以运行下列命令：

    
    
    tko-subs -domains=domains.txt -data=providers-data.csv -output=output.csv -takeover -githubtoken=<github-token> -herokuusername=<heroku-username> -herokuapikey=<heroku-api-key> -herokuappname=<heroku-app-name>

如果你想要检测一个单独的域名，则可以运行下列命令：

    
    
    tko-subs -domain <domain-name>

如果你想要检测多个域名，则可以运行下列命令：

    
    
    tko-subs -domain <domain-name-1>,<domain-name-2>

## 默认参数解释

> domains：默认设置为domains.txt
>
> data：默认设置为providers-data.csv
>
> output：默认设置为output.csv
>
> takeover：默认设置为空
>
> domain：默认设置为空，默认检测domains.txt文件中的所有域名
>
> threads：默认设置为5

因此，我们可以直接不带参数运行tko-subs，则tko-subs会按照上述默认配置运行。

## providers-data.csv文件格式

该文件中需包含name、cname、string和http这四个参数。

> name：服务提供商名称，例如Github
>
> cname：用于映射服务提供商网站内容的CNAME
>
> string：返回的错误信息，例如“There isn't a GitHub Pages site here”
>
> http：是否使用HTTP来连接目标站点

## 输出格式

tko-subs的输出数据中包含Domain、CNAME、Provider、IsVulnerable、IsTakenOver和Response。

> Domain：需检测的目标域名
>
> CNAME：目标域名的CNAME
>
> Provider：服务提供商所使用的域名
>
> IsVulnerable：目标域名是否存在漏洞
>
> IsTakenOver：目标域名是否被接管
>
> Response：目标子域名返回的信息

如果该工具检测到了已失效的DNS记录，则Provider参数留空。如果检测到了存在安全问题的域名服务器，则Provider和CNAME留空。

## 项目地址

 **tko-subs：** 【[ _GitHub传送门_](https://github.com/anshumanbh/tko-subs)】

参考资料

> [ _https://github.com/anshumanbh/tko-subs/blob/master/providers-> data.csv_](https://github.com/anshumanbh/tko-subs/blob/master/providers-> data.csv)
>
> [ _https://github.com/settings/tokens_](https://github.com/settings/tokens)
>
> [
> _https://gist.github.com/wh1tney/2ad13aa5fbdd83f6a489_](https://gist.github.com/wh1tney/2ad13aa5fbdd83f6a489)

