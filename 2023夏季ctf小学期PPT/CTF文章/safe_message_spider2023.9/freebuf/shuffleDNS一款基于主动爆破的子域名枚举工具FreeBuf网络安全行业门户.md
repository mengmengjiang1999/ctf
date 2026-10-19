#
![](https://image.3001.net/images/20200330/1585567877_5e81d8856b7e9.png!small)

##  shuffleDNS

**shuffleDNS是一款基于[MassDNS](https://github.com/blechschmidt)开发的强大工具，该工具采用Go语言开发，shuffleDNS可以通过使用主动爆破以及基于通配符的子域名解析方法来帮助广大研究人员枚举有效子域名，并且给我们提供简单易懂的输出报告。**

##  功能介绍

> 1、基于模块化的代码库开发，方便广大研究人员贡献自己的代码；
>
> 2、快速且简单的主动子域名扫描；
>
> 3、以智能化方式处理通配符子域名匹配；
>
> 4、易于使用，性能优化；
>
> 5、支持将Stdin和Stdout集成到工作流中；

##  工具使用

    
    
    shuffledns -h

该命令将显示工具的帮助信息。

**参数** |  **描述** |  **使用样例**  
---|---|---  
-d  |  需要寻找或解析的子域名  |  shuffledns -d hackerone.com   
-directory  |  用于枚举的临时目录  |  shuffledns -directory /hdd   
-r  |  用于枚举的解析器文件  |  shuffledns -r resolvers.txt   
-nC  |  输出中不使用高亮标记  |  shuffledns -nC   
-o  |  保存扫描结果（可选）  |  shuffledns -o hackerone.txt   
-list  |  需要处理的子域名列表  |  shuffledns -list bugcrowd.txt   
-massdns  |  Massdns代码路径  |  shuffledns -massdns /usr/bin/massdns   
-retries  |  DNS枚举尝试次数（默认为5）  |  shuffledns -retries 1   
-silent  |  输出报告中只显示子域名  |  shuffledns -silent   
-t  |  并发massdns解析数（默认为10000）  |  shuffledns -t 100   
-v  |  显示Verbose输出  |  shuffledns -v   
-version  |  显示shuffledns版本  |  shuffledns -version   
-w  |  爆破字典我呢见  |  shuffledns -w words.txt   
-wt  |  并发通配符检查数（默认为25）  |  shuffledns -wg 100   
-raw-input  |  包含现有massdns输出的文件  |  shuffledns -massdns-file output.txt   
  
##  工具安装

shuffleDNS的正常工作需要我们首先安装好MassDNS，关于MassDNS的安装，请参考【这篇文档】。

如果你将代码存放到了/usr/bin/massdns或/usr/local/bin/massdns路径下，工具将会自动检测到代码并使用它们。在Windows平台下，你还需要专门在工具中设置代码路径。

该工具还需要使用到一系列解析器，我们可以利用[dnsvalidator项目](https://github.com/vortexau/dnsvalidator)来生成解析器列表。当然了，你也可以使用自定义字典或[commonspeak2字典](https://github.com/assetnote/commonspeak2-wordlists/tree/master/subdomains)。

##  直接安装

###  代码安装

该工具的安装非常简单，你可以在该项目的[Release页面](https://github.com/projectdiscovery/shuffledns/releases/)找到对应平台的预构建代码，然后使用tar命令提取代码，并将提取出的代码移动到指定路径，就可以开始使用该工具了。

    
    
    > tar -xzvf shuffledns-linux-amd64.tar
    
        > mv shuffledns-linux-amd64 /usr/bin/shuffledns
    
        > shuffledns -h

##  源安装

shuffleDNS要求本地主机配置到Go v1.13+环境，接下来使用下列命令来获取代码库：

    
    
    > GO111MODULE=on go get -u -v github.com/projectdiscovery/shuffledns/cmd/shuffledns

如需对工具进行更新，可以使用-u和go get命令。

##  工具运行

###  1、解析子域名

为了解析列表中的子域名，你需要通过list选项来将子域名列表传递给工具：

    
    
    > shuffledns -d example.com -list example.com-subdomains.txt -r resolvers.txt

上述命令将对example.com-subdomains.txt中的子域名进行处理，并返回结果。工具将会使用-r选项指定的解析器来完成子域名解析。

你还能够以标准输入的方式来传递子域名列表：

    
    
    > subfinder -d example.com | shuffledns -d example.com -r resolvers.txt

###  2、子域名爆破

shuffleDNS支持使用给定字典文件来对目标进行暴力破解，你可以使用w选项来传递字典文件：

    
    
    > shuffledns -d hackerone.com -w wordlist.txt -r resolvers.txt

上述命令将会使用字典文件wordlist.txt来对hackerone.com进行爆破，域名爆破还可以使用标准输入的方式来实现：

    
    
    > echo hackerone.com | shuffledns -w wordlist.txt -r resolvers.txt

-o命令可以指定输出文件：
    
    
    > shuffledns -d hackerone.com -w wordlist.txt -o output.txt

我们所发现的子域名还可以传递给其他工具。比如说，你可以将shuffleDNS所发现的额主机传递给httprobe工具，它将帮助我们查找到http服务器：

    
    
    > echo hackerone.com | shuffledns -w wordlist.txt -r resolvers.txt -silent | httprobe

> [http://docs.hackerone.com](http://docs.hackerone.com/)
>
> [http://www.hackerone.com](http://www.hackerone.com/)
>
> [http://info.hackerone.com](http://info.hackerone.com/)

或

    
    
    > echo hackerone.com | subfinder | shuffledns -d hackerone.com -r resolvers.txt -silent | httprobe

> [http://docs.hackerone.com](http://docs.hackerone.com/)
>
> [http://www.hackerone.com](http://www.hackerone.com/)
>
> [http://info.hackerone.com](http://info.hackerone.com/)

##  项目地址

> shuffleDNS：【[GitHub传送门](https://github.com/projectdiscovery/shuffledns)】

 ***
参考来源：[projectdiscovery](https://github.com/projectdiscovery/shuffledns)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

