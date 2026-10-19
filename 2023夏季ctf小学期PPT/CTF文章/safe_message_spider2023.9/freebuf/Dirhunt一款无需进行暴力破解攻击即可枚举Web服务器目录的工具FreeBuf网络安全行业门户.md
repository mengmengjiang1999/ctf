**今天给大家介绍的是一款名叫Dirhunt的工具，它无需进行暴力破解即可帮助你枚举出目标Web服务器的目录。**

![1.png](https://image.3001.net/images/20180716/15317235305476.png!small)  

## 工具介绍

Dirhunt是一款经过优化的Web爬虫，主要功能是搜索并分析服务器目录。如果目标服务器开启了“index
of”模式之后，该工具将能够帮助你发现很多有意思的东西。除此之外，如果服务器没有开启目录枚举功能的话，Dirhunt仍然可以正常工作。值得一提的是，如果目标服务器使用了空白的index文件来尝试干扰爬虫的话，Dirhunt仍然可以通过404错误来检测目录。

### 功能介绍

> 1\. 一次性处理一个或多个目标网站；
>
> 2\. 处理“index of”页面，并报告有意思的文件；
>
> 3\. 检测目录；
>
> 4\. 检测目录中的空白index文件；
>
> 5\. 处理某些html文件并搜索出更多的新目录；
>
> 6\. 检测404错误页面，并检测伪造的404错误信息；
>
> 7\. 根据标识过滤结果；
>
> 8\. 分析结果

## 工具安装

如果你安装了pip，你可以用pip来安装最新版本的Dirhunt：

    
    
    $ sudo pip3 install dirhunt

注：本工具支持Python 2.7，但建议使用Python 3.x版本。

## 使用样例

查看帮助信息：

    
    
    $ dirhunt –help
    
    Usage: dirhunt [OPTIONS] [URLS]...
    
     
    
     :param int threads: :type exclude_flags: list
    
     
    
    Options:
    
     -t, --threads INTEGER          Number of threads to use.
    
     -x, --exclude-flags TEXT       Exclude results with these flags. See
    
                                     documentation.
    
     -i, --include-flags TEXT       Only include results with these flags. See
    
                                     documentation.
    
     -e, --interesting-extensions TEXT
    
                                      The filesfound with these extensions are
    
                                      interesting
    
     -f, --interesting-files TEXT   The files with these names are interesting
    
     --stdout-flags TEXT             Return only in stdout the urls of these
    
                                      flags
    
     --progress-enabled / --progress-disabled
    
     --timeout INTEGER
    
     --version
    
     --help                         Show this message and exit.

搜索目录：

    
    
    $dirhunt http://website.com/

搜索有趣的文件扩展名/：

    
    
    $ dirhunt http://domain1/blog/ -ephp,zip,sh

搜索有趣的文件：

    
    
    $ dirhunt <http://domain1/blog/> -faccess_log,error_log
    
    $ dirhunt <http://domain1/blog/> -f/home/user/dict.txt,./files.txt

多线程：

    
    
    $ dirhunt http://domain1/blog/ --threads10

设置timeout：

    
    
    $ dirhunt http://domain1/blog/ --timeout15

Dirhunt并不依靠暴力破解的方式来实现其功能，但它也不仅仅是一个简单的网络爬虫。该工具的速度也比其他爬虫要快，因为它最大程度减少了发送给服务器端的请求数量。一般来说，该工具只需要5-30秒即可完成任务，具体取决于目标网站或服务器的配置。

关于更多的使用方法内容，请参考Dirhunt的【[使用手册](http://docs.nekmo.org/dirhunt/usage.html)】。

> 工具演示：<https://asciinema.org/a/xPJXT0MhrvlZ8lJYJYkjxlice>

 ***参考来源：[kitploit](https://www.kitploit.com/2018/07/dirhunt-find-web-directories-without.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

