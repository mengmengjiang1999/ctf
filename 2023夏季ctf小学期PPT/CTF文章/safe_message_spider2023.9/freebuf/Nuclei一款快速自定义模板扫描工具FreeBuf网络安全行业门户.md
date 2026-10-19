![](https://image.3001.net/images/20200502/1588409400_5ead34387026e.png!small)

**Nuclei是一款运行速度非常快且易于使用的扫描工具，它可以帮助研究人员基于模板执行可配置的目标扫描任务，并提供了大量可扩展接口以辅助使用。**

Nuclei可以基于模板来跨目标发送请求，能够实现零误报，并且可以帮助研究人员对已知路径执行有效的扫描。Nuclei的主要使用场景为网络侦察的初始阶段，可以帮助研究人员快速检查已知且易于探测的目标中是否存在安全漏洞。该工具使用了[retryablehttp-go库](https://github.com/projectdiscovery/retryablehttp-go)来处理各种错误，并在Web应用防火墙屏蔽的情况下进行自动重传，这也是该工具的核心模块之一。我们还专门开源了一个专门的
[资源库](https://github.com/projectdiscovery/nuclei-templates)来维护各种类型的扫描模板，我们也欢迎社区中的各位大佬[贡献自己的力量](https://github.com/projectdiscovery/nuclei-templates/blob/master/GUIDE.md)。

## 功能介绍

> 简单且模块化的代码，方便使用和开发；
>
> 运行速度快且完全可配置，使用了基于模板的引擎；
>
> 错误事件/特殊情况处理重传；
>
> WAF处理；
>
> 智能匹配，实现零误报扫描；

## 工具使用

    
    
    nuclei -h  
    

上述命令将显示该工具的帮助信息，下面给出的是该工具的常用选项：

**选项标签** | **描述信息** | **使用样例**  
---|---|---  
-c | 并发请求数（默认为10） | nuclei -c 100  
-l | 要运行模板的URL列表 | nuclei -l urls.txt  
-t | 需跨主机检测的模板输入文件 | nuclei -t git-core.yaml  
-t | 需跨主机检测的模板输入文件 | nuclei -t "path/*.yaml"  
-nC | 输出中不使用高亮颜色 | nuclei -nC  
-o | 保存输出结果文件（可选） | nuclei -o output.txt  
-silent | 在输出中仅显示找到的结果 | nuclei -silent  
-retries | 重试失败请求的次数（默认值1） | nuclei -retries 1  
-timeout | 超时前等待的秒数（默认为5） | nuclei -timeout 5  
-v | 显示详细输出 | nuclei -v  
-version | 显示Nuclei版本 | nuclei -version  
-proxy-url | 代理URL | nuclei -proxy-url [http://user:pass@this.is.a.proxy:8080](http://this.is.a.proxy:8080/)  
-proxy-socks-url | 代理Socks URL | nuclei -proxy-socks-url socks5://user:[pass@this.is.a.proxy.socks](mailto:pass@this.is.a.proxy.socks):9050  
  
## 工具安装

 **代码安装**

该工具的安装其实非常简单，大家可以在该项目GitHub库中的Releases页面中根据自己的平台选择预编译好的源代码，然后使用`tar`命令进行代码提取，将提取出的代码移动到自己的$PATH路径下。所使用的命令如下：

    
    
    > tar -xzvf nuclei-linux-amd64.tar
    
    > mv nuclei-linux-amd64 /usr/bin/nuclei
    
    > nuclei -h

 **源安装**

Nuclei要求目标设备成功配置好`Go v1.13+`环境，然后运行下列命令获取项目代码：

    
    
    > GO111MODULE=on go get -u -v github.com/projectdiscovery/nuclei/cmd/nuclei  
    

如需更新Nuclei，可以使用`-u`选项和`go get`命令。

## Nuclei运行

 **使用单一模板运行Nuclei。**

下列命令将会对`urls.txt`文件中列出的主机进行扫描，并返回匹配的结果：

    
    
    > nuclei -l urls.txt -t git-core.yaml -o results.txt  
    

你还能够以标准输入（STDIN）的方式传递目标主机列表，下列命令同样可以对`urls.txt`文件中列出的主机进行扫描，并返回匹配的结果：

    
    
    > cat urls.txt | nuclei -t git-core.yaml -o results.txt  
    

 **使用多个模板运行Nuclei。**

下列命令将能够使用`path-to-templates`目录中所有模板来对`urls.txt`文件中列出的主机进行扫描，并返回匹配的结果：

    
    
    > nuclei -l urls.txt -t "path-to-templates/*.yaml" -o results.txt   
    

**使用子扫描器和其他类似工具自动化运行Nuclei。**

    
    
    > subfinder -d hackerone.com -silent | httprobe | nuclei -t "path-to-templates/*.yaml" -o results.txt  
    

## 自定义模板

Nuclei支持通过.yaml文件来自动传递和执行多个模板任务，如需开发自定义模板，请参考这篇【[文档](https://github.com/projectdiscovery/nuclei-templates/blob/master/GUIDE.md)】。

 **工具截图**

![](https://image.3001.net/images/20200502/1588409491_5ead34936dcf4.png!small)
**项目地址**

Nuclei：【[GitHub传送门](https://github.com/projectdiscovery/nuclei)】

***参考来源：[projectdiscovery](https://github.com/projectdiscovery/nuclei)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

