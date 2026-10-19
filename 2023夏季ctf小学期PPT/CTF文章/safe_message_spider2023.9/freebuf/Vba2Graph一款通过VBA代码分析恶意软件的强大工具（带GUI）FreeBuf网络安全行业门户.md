## 前言

 **今天给大家介绍的是一款名叫Vba2Graph的恶意软件分析工具，这款工具可以根据VBA代码来生成调用图，以帮助研究人员更方便地分析恶意文档。**

![1.png](https://image.3001.net/images/20181206/1544083623_5c08d8a7a7fc6.png!small)

对于安全研究人员来说，很多时候都需要花费大量的时间来分析恶意Office宏文件。但如果我们能提供一个VBA调用图，并高亮标记潜在的恶意关键词，那么研究人员就可以快速对恶意宏进行分析，并了解其执行流程了。

## 功能介绍

> 1、 关键词高亮标记；
>
> 2、 VBA属性支持；
>
> 3、 支持外部函数声明；
>
> 4、 巧妙触发“_Change”执行；
>
> 5、 美观的配色方案。

### 特性

> 1、 速度非常快；
>
> 2、 支持目前绝大部分的恶意宏。

## 演示样例

### 样例1：

Trickbot下载器-使用了对象Resize事件来作为初始触发器，跟在TextBox_Change触发器的之后：

![2.png](https://image.3001.net/images/20181206/1544083647_5c08d8bfe32ea.png!small)

### 样例2：

![3.png](https://image.3001.net/images/20181206/1544083663_5c08d8cf40cc8.png!small)

注：Examples目录中提供了更多参考样例。

## 工具安装

### 安装oletools：

    
    
    https://github.com/decalage2/oletools/wiki/Install

### 安装Python依赖：

    
    
    pip2 install -r requirements.txt

### 安装Graphviz

 **Windows**

安装Graphviz msi：

    
    
    https://graphviz.gitlab.io/_pages/Download/Download_windows.html

添加“dot.exe”到PATH环境变量中，或者运行：

    
    
    set PATH=%PATH%;C:\Program Files (x86)\Graphviz2.38\bin

 **macOS**

    
    
    brew install graphviz

 **Ubuntu**

    
    
    sudo apt-get install graphviz

 **Arch**

    
    
    sudo pacman -S graphviz

## 工具使用

    
    
    usage:vba2graph.py [-h] [-o OUTPUT] [-c {0,1,2,3}] (-i INPUT | -f FILE)
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -o OUTPUT, --output OUTPUT
    
                            output folder (default:"output")
    
      -c {0,1,2,3}, --colors {0,1,2,3}
    
                            color scheme number [0,1, 2, 3] (default: 0 - B&W)
    
      -i INPUT, --input INPUT
    
                            olevba generated fileor .bas file
    
      -fFILE, --file FILE  Office file withmacros

## 工具使用样例（全平台通用）

仅支持Python 2：

    
    
    #Generate call graph directly from an Office file with macros [tnx @doomedraven]
    
    python2 vba2graph.py -f malicious.doc -c 2    
    
     
    
    #Generate vba code using olevba then pipe it to vba2graph
    
    olevba malicious.doc | python2 vba2graph.py -c 1
    
     
    
    #Generate call graph from VBA code
    
    python2 vba2graph.py -i vba_code.bas -o output_folder

## 输出结果

在你的输出目录下会生成4个文件夹：

> 1、 png：存储实际生成的图形文件；
>
> 2、 svg：相同的图形文件（矢量图）；
>
> 3、 dot：dot文件，用来创建图形文件；
>
> 4、 bas：脚本所识别出的VBA函数代码。

### 项目地址

> Vba2Graph：【[GitHub传送门](https://github.com/MalwareCantFly/Vba2Graph)】

 ***参考来源：[kitploit](https://www.kitploit.com/2018/11/vba2graph-generate-call-graphs-from-vba.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+PentestTools+%28PenTest+Tools%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

