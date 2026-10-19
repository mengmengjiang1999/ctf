![](https://image.3001.net/images/20200807/1596794018.jpg!small)

## CWFF

CWFF是一款专用于模糊测试的自定义字典工具，该工具可以帮助广大研究人员以高速并发的形式创建一个特定的高质量模糊测试/内容发现字典。

## 工具说明

简单来说，该工具可以使用各种资源来直接收集目标的终端节点参数以及其子域名。其中包括下列资源内容：

1、工具会遍历目标站点中的所有记录和子域名，以及所有能返回200响应状态码的URL地址（需使用--subdomains参数）。

2、在信息收集阶段，工具会通过解析目标页面的<script>标签来收集JavaScript文件。CWFF还可以分辨出目标站点中那些JS库和JS文件是由网站开发者编写的，并能够从中提取出JavaScript文件（需使用
--js-libraries参数）。

3、爬取常见CDX索引和Alien vault OTX。

4、如果使用了--juicy-files参数，工具还能够从终端节点中提取类似Sitemap.xml和robots.txt之类的文件。

5、你还可以通过--github参数来给CWFF提供一个GitHub代码库，工具将会使用GitHub API来从目标代码库中提取路径。

6、如果使用了--connected-websites参数，CWFF将会使用内置的站点API来提取相关的配置文件以及站点资源。

使用了--recursive参数之后，工具将能够从所有终端节点中以遍历的方式收集信息，下面给出的是一个终端节点（parseq/javadoc/1.1.0/com）扫描结果样例：

    
    
    parseq/javadoc/1.1.0/com
    
    parseq/javadoc/1.1.0/
    
    parseq/javadoc/
    
    parseq/
    
    javadoc/
    
    1.1.0/
    
    com

## 工具要求

  * Python 3.6+；
  * 工具已在Linux Manjaro平台上进行了测试，理论上该工具适用于任何操作系统；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并安装相关依赖组件：

    
    
    git clone https://github.com/D4Vinci/CWFF.git
    
    python3 -m pip install -r requirements.txt
    
    python3 cwff.py --help

## 工具使用

    
    
    CWFF [-h] [--threads] [--github] [--subdomains] [--recursive] [--js-libraries] [--connected-websites] [--juicy-files] [--use-filter-model] [-o] domain
    
     
    
    positional arguments:
    
      domain                目标站点域名
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息和退出
    
      --threads             最大可用的并发线程数量，默认为1000
    
      --github         从给定GitHub库收集终端节点信息，例如https://github.com/google/flax
    
      --subdomains         从子域名收集终端节点信息
    
      --recursive          递归提取终端节点信息 
    
      --js-libraries        从JS库中提取信息
    
      --connected-websites    引入从已连接网站提取的节点信息
    
      --juicy-files         引入从sitemap.xml和robots.txt中提取出的节点信息
    
      --use-filter-model    使用filter_model文件过滤结果
    
      -o                  指定终端节点和参数的输出目录，默认为网站名称

## 结果过滤

CWFF支持对资源收集结果进行过滤，CWFF提供了两种方法来检测和删除无用的终端节点：

  * 使用给定列表删除包含了特定字符串的终端节点；
  * 使用正则表达式删除特定终端节点；

除此之外，你还可以使用filter.py脚本来实现过滤，该脚本将会加载filter_model.py文件来自动化返回字典结果：

    
    
    python filter.py wordlist.txt output.txt

## 工具运行截图

![](https://image.3001.net/images/20200807/1596794128.png!small)

## 项目地址

CWFF：【[ _GitHub传送门_](https://github.com/D4Vinci/CWFF)】

