![](https://image.3001.net/images/20200810/1596994512.jpg!small)

## Evine

Evine是一款功能强大的我交互式命令行Web爬虫，该工具基于Golang开发，并且实现了一个简单且快速的交互式Web爬虫和数据搜索工具。对于大范围扫描任务来说，Evine允许研究人员通过命令行接口来完成元数据和其他数据的提取、数据挖掘、网络侦察和测试任务。

## 工具安装

注意事项：该项目的正常运行需要Golang 1.13.x环境。

### 预构建源码

如果广大研究人员需要使用预构建的Evine源码，可以直接访问该项目GitHub库的[
_Release页面_](https://github.com/saeeddhqan/evine/releases)来直接获取。

### 源码安装

    
    
    go get github.com/saeeddhqan/evine
    
    "$GOPATH/bin/evine" -h

### 通过GitHub库安装

    
    
    git clone https://github.com/saeeddhqan/evine.git
    
    cd evine
    
    go build .
    
    mv evine /usr/local/bin
    
    evine --help

## 工具命令&使用

****快捷键****

|

****描述****  
  
---|---  
  
Enter

|

运行爬虫（URL视图）  
  
Enter

|

显示响应信息  
  
Tab

|

切换下一个视图  
  
Ctrl+Space

|

运行爬虫  
  
Ctrl+S

|

保存响应信息  
  
Ctrl+Z

|

工具退出  
  
Ctrl+R

|

回复默认值  
  
Ctrl+Q

|

关闭响应存储视图  
  
下列命令可以显示工具的帮助信息：

    
    
    evine -h

“-url”参数用于指定工具待爬取的URL地址：

    
    
    evine -url toscrape.com

“-url-exclude string”参数可以允许用户通过正则表达式来排除待匹配的URL地址：

    
    
    evine -url-exclude ?id=

“-domain-exclude string”参数可以指定需要排除的多个域名，参数值以逗号分隔，默认为root域名：

    
    
    evine -domain-exclude host1.tld,host2.tld

“-code-exclude string”参数可以指定需要排除的HTTP状态码，以“|”分隔，默认为“.*”：

    
    
    evine -code-exclude 200,201

“-delay int”参数可以设置每个请求之间的休眠时间，单位为毫秒：

    
    
    evine -delay 300

“-depth”参数可以指定爬虫的搜索深度，默认为1：

    
    
    evine -depth 2

“-thread int”参数可以指定解析的并发线程数量，默认为5：

    
    
    evine -thread 10

“-header”参数可以设置每个请求的HTTP Header：

    
    
    evine -header KEY: VALUE\nKEY1: VALUE1

“-proxy string”参数用于指定代理地址：

    
    
    evine -proxy http://1.1.1.1:8080

“-scheme string”设置请求发送模式：

    
    
    evine -scheme http

“-timeout int”参数用于指定超时时间，默认为10秒：

    
    
    evine -timeout 15

“-keys string”参数可指定搜索内容，支持邮件、URL、电话、css、cdn、dns、脚本或文件后缀等等：

    
    
    evine -keys urls,pdf,txt

“-regex string”参数允许用户针对页面内容指定搜索正则式：

    
    
    evine -regex 'User.+'

“-max-regex int”参数指定正则搜索的最大结果数量，默认为1000：

    
    
    evine -max-regex -1

“-robots”参数用于指定目标URL的robots.txt，并将其当作种子使用：

    
    
    evine -robots

“-sitemap”参数用于指定目标URL的sitemap.xml，并将其当作种子使用：

    
    
    evine -sitemap

## 工具运行截图

![](https://image.3001.net/images/20200810/1596994620.png!small)

## 工具演示视频

视频地址：【[ _点我观看_](https://asciinema.org/a/351624)】

## 项目地址

Evine：【[ _GitHub传送门_](https://github.com/saeeddhqan/evine)】

