*****本文原创作者：cat01，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

>  **面向对象：** 喜欢自己制作安全工具的新手
>
> **依赖：** python2.7，requests，jinja2
>
> **参考项目：**[theHarvester](https://github.com/laramies/theHarvester)
>
> **关注点：** 上千star的开源安全工具是如何具体实现信息收集功能的，如何把简单的事情做漂亮
>
> **我的demo版地址：**[戳这里，本文所有代码均在这里，含测试用例](https://github.com/alvinyeats/Zeus)

 **俗话说的好，不会开发的白猫不是好白猫，想在安全界拿到高薪，掌握点开发技术那是必须滴。**

最近在制作一个集成化工具，要用到前期的信息收集。由于之前做批量化信息收集时对theHarvester做过一些功能封装，所以打算参考这个做demo版的实现。如何信息收集相信很多人都懂，手里多多少少也有那么几个常用顺手的工具，但真正愿意花时间去研究工具内部实现的人估计不多，喜欢在代码层面上较真儿的人少之又少。楼主恰恰是这样的人，看到好的代码就如同看到神奇的拿权姿势一样兴奋。所以无心关注工具实现的童鞋完全可以绕过了。

回归正题，theHarvester的功能其实不只是子域名收集，还包括email账号收集，虚拟主机，开放端口/服务器指纹和员工姓名，本文只分析theHarvester是如何用搜索引擎处理子域名收集的。

> theHarvester is a tool for gathering e-mail accounts, subdomain names,
> virtual hosts, open ports/ banners, and employee names from different public
> sources (search engines, pgp key servers).

## 动手前的分析

### 需求分析

先考虑最简单的功能实现，输入一个域名，工具返回其关联的子域名

> 输入：域名，如qq.com
>
> 输出：信息汇总表（文件格式：html）

### 功能模块分析

theHarvester主要分为四个模块：

> 搜索引擎模块：discovery，其实就是爬虫，利用各大搜索引擎或资产搜索引擎对相关输入进行搜索，并利用解析模块从爬到的网页中提取信息，核心模块
>
> 数据输出模块：lib，将数据输出到指定格式的文件中，并绘制简单的统计图（柱状图），只要你喜欢，输出txt，json，cvs随意，完全可以自己加
>
> 数据解析模块：myparser.py ，从网页中提取有用信息，如域名，email等，含数据清洗的工具，排除干扰项，主要提供正则解析
>
> 命令解析模块：theHarvester.py，入口文件，用于解析输入的命令，根据输入调用相关的功能并进行结果输出

![image.png](https://image.3001.net/images/20180303/15200099017841.png!small)

## 开撸

简化版的项目结构

![image.png](https://image.3001.net/images/20180303/15200537493223.png!small)

信息收集的流程基本都差不多：输入命令—>调用相关引擎—>分析—>结果输出

说白了就是个爬虫，我打算先从搜索引擎模块搞起，看看人家是通过什么参数去访问的，以前以为site:domain.com这种套路，看了下还真不是=_=!

### 搜索引擎模块

搜素引擎目录discovery目录下的文件结构基本一致，一个搜索类含有多个定制化的function（如按照限制数执行检索，爬去网页，获取hostname，email等），以百度搜索为例，这些搜索文件中提供基础数据的便是do_search方法，而do_search方法中最为关键的则是红线标注部分，用户提交的搜索关键字，相当于你在百度搜索框输入“@domain.com”。所以人家还真不是通过“site:doman.com来实现的”。

![image.png](https://image.3001.net/images/20180303/15200111263867.png!small)相关参数的解释如下

> s?wd: 指关键词, “wd=”
> 是英文的word的缩写，参数表示的是搜索关键词的内容，如果是汉字那么这个参数是汉字的十六进制形式，如果是英文，那么这个参数就用该英文来表示rn:
> 每页包含的搜索结果数目。默认值为10pn: 搜索结果的页码，从零开始计数。即pn = ${结果页码-1}*rn。

### 撸主改进的地方

 **discovery目录下，如baidusearch.py**

他们用的居然是httplib，好吧，这种上古时期的库我特么是肯定要优化的啊！看到其他地方用到了requests，那我直接上requests好啦，而且目前我暂时只需要收集子域名。网上找了篇httplib与requests的对比，[Sending
HTTP requests with Python: “httplib” vs
“requests”](https://tech4lib.wordpress.com/2015/06/21/sending-http-requests-with-python-httplib-vs-requests/)，大概意思就是"我"用httplib访问某个网址半天没搞定，后来才知道原来忘了httplib必须配置一些参数才能正常访问某些网址（如：
Content-type），好麻烦的说，等“我”改用requests之后，发现，沃德天，原来只需要给个url就搞定，还是requests傻瓜式啊，666。所以撸主的do_search实现优雅了很多

    
    
       def do_search(self):
            payload = {'wd': '@'+self.word, 'pn': self.counter}
            r = requests.get(self.server, params=payload)
            self.total_results += r.text
    

后面我们可以参考baidu，逐步添加google，bing，领英，shadon等，还可以根据国情，多加点国内的站点，比如51job，猎聘，拉钩，boss直聘等。

### 数据输出模块

 **lib目录，htmlexport.py**

theHarvester采用的HTML生成方式：自己插入HTML标签、样式等。我的方式：因为平时经常用python的web框架做应用，习惯了使用模板，所以这块我是直接用的Jinja2，一个export.html模板加一个输出控制文件htmlexport.py足够了，喜欢用什么样式可以在html模板里慢慢加。

输出控制文件：lib/htmlexport.py

    
    
    # filename: htmlexport.py
    from jinja2 import Environment, FileSystemLoader
    
    class HtmlExport(object):
    
        def __init__(self, hostnames, filename):
            self.hostnames = hostnames
            self.filename = filename
    
        def write_html(self):
            env = Environment(loader=FileSystemLoader('templates'))
            output_template = env.get_template('export.html')
            output = output_template.render(hostnames=self.hostnames)
    
            with open(self.filename, "wb") as f:
                f.write(output)
    

模板文件：lib/templates/export.html

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Zeus Harvest</title>
    </head>
    <body>
        <h1>Hosts</h1>
        <ul>
        {% for item in hostnames %}
            <li>{{ item }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    

使用HTML模板搞数据会更easy些，日后改动也方便。

未加任何style的输出效果

![image.png](https://image.3001.net/images/20180303/15200560585680.png!small)

### 数据解析模块

 **myparser.py**

![image.png](https://image.3001.net/images/20180303/15200545889579.png!small)

一个很简单的正则，self.word为用户在命令行输入的要检索的目标，如google.com。不过这样做有个问题就是必须提供规范化的输入，假如我输入一个
**<http://www.bing.com>** 这种信息是不能识别的，而我们在做批量化收集过程中，拿到的域名list很可能存在大量不符合
**google.com**
这种格式的数据，针对这种场景需求可以在命令行解析模块对用户的批量化输入做下简单的数据清洗。后续我会在自己的github项目中加上这部分的功能。

### 命令解析模块

这部分就没啥好讲的了，了解下python里的 **sys.argv[1:]**
，就知道怎么去做了。在开始界面搞个狂掉酷炫拽的标志，对推广自己的开源项目是个不错的选择。

## 结尾

本文主要对开源信息工具 **theHarvester**
做了下内部功能点分析。对于熟悉python基本语法的新手来说，实现这样一款相同功能的工具难度不大，theHarvester的亮点在于良好的代码风格（废话，写的不好谁愿意看啊），这也是很多新手欠缺的地方。

芦竹业余时间会对[Zeus](https://github.com/alvinyeats/Zeus)项目做持续性的跟进和开发，这是一款弱点自动发现工具，含信息收集、指纹扫描、漏洞库收集，自动匹配受影响的web应用并尝试做简单的渗透或给出渗透入侵报告，可以动手前期节省很大一部分人力。

 ***本文原创作者：cat01，本文属FreeBuf原创奖励计划，未经许可禁止转载**

