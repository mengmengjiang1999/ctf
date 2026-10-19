![](https://image.3001.net/images/20221002/1664690643_633929d3ad270ea208c45.jpeg!small)

## 关于DeadFinder

DeadFinder是一款功能强大的链接分析工具，该工具可以帮助广大研究人员快速地寻找目标页面中的无效链接（死链）。所谓死链，即一个页面中存在的无法被连接的一条链接。这些链接如果一直保留在页面中的话，可能会影响SEO的效果，更严重的可能会影响整个网站的安全。因此，DeadFinder便应运而生，在该工具的帮助下，广大研究人员可以轻松识别和修改这些死链。

## 工具安装

### 源码获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hahwul/deadfinder.git

### 使用Gem安装

我们还可以使用Gem来安装DeadFinder：

    
    
    gem install deadfinder

### Docker镜像安装

除此之外，该工具还提供了预构建的Docker镜像：

    
    
    docker pull ghcr.io/hahwul/deadfinder:latest

## 工具使用

    
    
    Commands:
    
      deadfinder file            # Scan the URLs from File. (e.g deadfinder file urls.txt)
    
      deadfinder help [COMMAND]  # Describe available commands or one specific command
    
      deadfinder pipe            # Scan the URLs from STDIN. (e.g cat urls.txt | deadfinder pipe)
    
      deadfinder sitemap         # Scan the URLs from sitemap.
    
      deadfinder url             # Scan the Single URL.
    
      deadfinder version         # Show version.
    
    Options:
    
      c, [--concurrency=N]  # Set Concurrncy
    
                            # Default: 20
    
      t, [--timeout=N]      # Set HTTP Timeout
    
                            # Default: 10
    
      o, [--output=OUTPUT]  # Save JSON Result

### 参数解释

    
    
    deadfinder file：从文件读取并扫描多个URL地址，例如“deadfinder file urls.txt”            
    
      deadfinder help [COMMAND]：查看工具可用命令和指定命令帮助信息
    
      deadfinder pipe：从STDIN扫描多个URL地址，例如“cat urls.txt | deadfinder pipe”            
    
      deadfinder sitemap：从站点sitemap扫描多个URL地址
    
      deadfinder url：扫描单个URL地址
    
      deadfinder version：显示工具版本信息
    
      c, [--concurrency=N]：设置并发数量，默认为20
    
      t, [--timeout=N]：设置HTTP超时，默认为10秒
    
      o, [--output=OUTPUT]：存储JSON结果

### 运行模式

从STDIN扫描多个URL地址：

    
    
    cat urls.txt | deadfinder pipe

从文件读取并扫描多个URL地址：

    
    
    deadfinder file urls.txt

扫描单个URL地址：

    
    
    deadfinder url https://www.hahwul.com

从站点sitemap扫描多个URL地址：

    
    
    deadfinder sitemap https://www.hahwul.com/sitemap.xml

### JSON处理

    
    
    deadfinder sitemap https://www.hahwul.com/sitemap.xml \
    
      -o output.json
    
    cat output.json | jq

## 工具运行截图

![](https://image.3001.net/images/20221002/1664690904_63392ad8be7f42a25b02e.png!small)

## 项目地址

 **DeadFinder** ：【[ _GitHub传送门_](https://github.com/hahwul/deadfinder)】

