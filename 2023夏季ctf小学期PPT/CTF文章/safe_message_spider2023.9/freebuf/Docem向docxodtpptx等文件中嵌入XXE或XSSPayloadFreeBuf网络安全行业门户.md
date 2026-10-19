**docem是一个用于向docx，odt，pptx等（任意包含大量xml文件的zip）文件中嵌入XXE/XSS
Payload的工具。许多常见的文档格式（例如doc，docx，odt等）都只是一个zip文件，其中包含了一些xml文件。**  

    
    
     _|_|_|   
    
    
    _|    _|    _|_|      _|_|_|    _|_|    _|_|_|  _|_|      
    _|    _|  _|    _|  _|        _|_|_|_|  _|    _|    _|    
    _|    _|  _|    _|  _|        _|        _|    _|    _|  
    _|_|_|      _|_|      _|_|_|    _|_|_|  _|    _|    _|version 1.3

该工具是[ShikariSenpai](https://twitter.com/ShikariSenpai)和[ansjdnakjdnajkd](https://twitter.com/ansjdnakjdnajkd)对文档内部结构进行协作研究的side
project。  

![](https://image.3001.net/images/20191022/1571709380_5dae61c4871f4.png!small)

那为什么不将XXE payloads嵌入其中呢？

这项伟大的[研究](http://oxmlxxe.github.io/reveal.js/slides.html#/)是由Will Vandevanter
(_will_is)
完成的。要创建带有嵌入payloads的文档，我们可以使用一个名为[oxml_xxe](https://github.com/BuffaloWill/oxml_xxe)的工具。

但是，当你需要在不同的位置创建数百个payloads文档时，使用oxml_xxe并不方便。这也是Docem被创建的主要原因之一。

它的工作方式如下：你指定sample文档 -该文档具有一些magic_symbols（在下图中为፨（在程序中为常量XXCb8bBA9XX）），如果你使用XXE payload，则将其替换为对
payload的引用；或者将被你的XSS payload所替换。

此外，payload_type有三种不同的类型 -每种类型都决定了如何处理对文档中给定文件的各个magic_symbol。在用法部分对各个payload_type进行了描述。下面是一个小的工作方案：

![](https://image.3001.net/images/20191022/1571709410_5dae61e2cd203.png!small)

Payload modes

![](https://image.3001.net/images/20191022/1571709425_5dae61f15821e.png!small)

程序界面

![](https://image.3001.net/images/20191022/1571709438_5dae61fea4fc1.png!small)

##  安装

    
    
    pip3 install -r requirements.txt

##  使用

    
    
    python3 docem.py --help

必要参数

> xss - XSS - 跨站点脚本
>
> xxe - XXE - 外部XML实体
>
> -s - sample文件或sample目录的路径
>
> -pm - payload模式

可选参数

> per_document -默认模式，将payload嵌入所有文件中的所有位置并创建新文档
>
> per_file - 对于各个payload，文档中的各个文件，以及文件中的所有位置嵌入payload并创建新文档
>
> per_place - 对于各个payload，文件中的各个位置嵌入payload并创建新文档
>
> -pt - payload类型
>
> -pf - payload文件
>
> -kt - 不要在tmp中删除临时文件夹
>
> -sx - sample扩展名-当sample是目录时使用
>
> -h - 打印帮助信息

示例：

    
    
    ./docem.py -s samples/xxe/sample_oxml_xxe_mod0/ -pm xss -pf payloads/xss_all.txt -pt per_document -kt -sx docx
    ./docem.py -s samples/xxe/sample_oxml_xxe_mod1.docx -pm xxe -pf payloads/xxe_special_2.txt -kt -pt per_place
    ./docem.py -s samples/xss_sample_0.odt -pm xss -pf payloads/xss_tiny.txt -pm per_place
    ./docem.py -s samples/xxe/sample_oxml_xxe_mod0/ -pm xss -pf payloads/xss_all.txt -pt per_file -kt -sx docx

##  如何创建自定义 sample？

**通过新文件**

> 1.提取你的文档example.docx
>
> 2.在要嵌入payload的地方添加magic symbols（魔术符号）- ፨
>
> 3.将你的新sample压缩到example_modified0.zip中
>
> 4.重命名扩展名 - example_modified0.docx
>
> 5.使用新创建的sample

##  如何添加自定义 payload？

###  XXE payloads

文件中的字符串

    
    
    {"vector":"<!DOCTYPE docem [<!ENTITY xxe_canary_0 \"XXE_STRING\">]>","reference":"&xxe_canary_0;"}

vector - 必要关键字 - 用于脚本搜索

<!DOCTYPE docem [<!ENTITY xxe_canary_0 \"XXE_STRING\">]> \- payload。警告所有双引号 "
必须用一个反斜杠转义 \ => \"

reference - 必要关键字 - 用于脚本搜索

&xxe_canary_0; - 将在所有位置添加带有魔术符号的引用

###  XSS payloads

没有特殊格式。只是一个有字符串的文件。

##  功能和计划

功能

> 读取带有payload的文件
>
> XXE自定义payload文件
>
> XSS payload文件

计划

> 添加可以嵌入解压缩文件的功能
>
> 添加标志用以指定要在XXE中使用的自定义网址
>
> 添加标志用以指定要在XSS中使用的自定义网址

***参考来源：[GitHub](https://github.com/whitel1st/docem)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

  

