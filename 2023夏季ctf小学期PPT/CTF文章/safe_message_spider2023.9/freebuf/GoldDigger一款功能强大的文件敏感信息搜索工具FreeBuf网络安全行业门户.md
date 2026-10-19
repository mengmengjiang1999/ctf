![](https://image.3001.net/images/20230718/1689645814_64b5f2f68a9da9019d593.jpg!small)

## 关于GoldDigger

GoldDigger是一款功能强大的文件敏感信息搜索工具，该工具基于递归搜索实现其功能，可以帮助广大研究人员以递归的形式在大量文件中快速搜索和发现感兴趣的敏感信息。GoldDigger专为渗透测试人员设计，原始目的就是为了帮助研究人员在渗透测试中执行快速文件搜索。

本项目所使用的大多数正则表达式都来自于d1vious的【[ _git_ _-wild-hunt_](https://github.com/d1vious/git-wild-hunt)】项目。

## 工具要求

> Python 3

## 工具安装

由于GoldDigger基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境：

    
    
    virtualenv -p python3 .
    
    source bin/activate
    
    python dig.py --help

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ustayready/golddigger.git

## 工具使用

    
    
    usage: dig.py [-h] [-e EXCLUDE] [-g GOLD] -d DIRECTORY [-r RECURSIVE] [-l LOG]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -e EXCLUDE, --exclude EXCLUDE
    
                            JSON file containing extension exclusions
    
      -g GOLD, --gold GOLD  JSON file containing the gold to search for
    
      -d DIRECTORY, --directory DIRECTORY
    
                            Directory to search for gold
    
      -r RECURSIVE, --recursive RECURSIVE
    
                            Search directory recursively?
    
      -l LOG, --log LOG     Log file to save output

### 参数解释

    
    
    -h, --help            显示工具帮助信息和退出
    
      -e EXCLUDE, --exclude EXCLUDE
    
                            包含要排除扩展的JSON文件
    
      -g GOLD, --gold GOLD  包含要搜索结果的JSON文件
    
      -d DIRECTORY, --directory DIRECTORY
    
                            需要搜索敏感信息的目录路径
    
      -r RECURSIVE, --recursive RECURSIVE
    
                            是否开启文件目录递归搜索功能
    
      -l LOG, --log LOG     输出结果日志文件路径

## 工具使用样例

GoldDigger首先会递归搜索所有的目录并根据gold.json文件中的条目来尝试匹配文件中的内容。除此之外，我们还可以利用一个exclusions.json文件来排除不想要搜索的文件或扩展名。该工具支持以
--directory参数选项来指定递归搜索的root根目录。

下面给出的是工具输出的样例结构：

    
    
    ~/Engagements/CustomerName/data/randomfiles/
    
    ~/Engagements/CustomerName/data/randomfiles2/
    
    ~/Engagements/CustomerName/data/code/

还可以提供下列命令来解析所有的三种报告：

    
    
    ~/Engagements/CustomerName/data/randomfiles/
    
    ~/Engagements/CustomerName/data/randomfiles2/
    
    ~/Engagements/CustomerName/data/code/

## 运行结果

该工具将创建一个包含扫描结果的日志文件。由于使用正则表达式的性质，可能存在许多误报。尽管如此，该工具已被证明可以在处理数千个文件时提高生产力。

## 项目地址

 **GoldDigger** ：【[ _GitHub传送门_](https://github.com/ustayready/golddigger)】

## 参考资料

> [ _https://github.com/d1vious/git-wild-> hunt_](https://github.com/d1vious/git-wild-hunt)

