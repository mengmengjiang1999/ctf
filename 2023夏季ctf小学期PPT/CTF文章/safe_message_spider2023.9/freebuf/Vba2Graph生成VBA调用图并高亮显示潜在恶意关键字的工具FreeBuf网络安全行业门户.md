****

**Vba2Graph是一款用于生成VBA调用图，并高亮显示潜在恶意关键字的工具。该工具旨在使安全研究人员能够快速的分析恶意宏，并更加直观的理解其执行流程。**

##  **特性**

> 关键字高亮显示
>
> VBA属性支持
>
> 外部函数声明支持
>
> 使用 "_Change" 执行触发器Tricky宏
>
> 鲜艳的配色方案

## 优点

> 方便快速
>
> 适用于大多数在野观察到的恶意宏

##  **缺点**

> 静态（无法识别动态解析调用）

## 示例

### Example 1：

Trickbot downloader - 利用对象Resize事件作为初始触发器，紧接着是TextBox_Change触发器。

![Vba2Graph](https://image.3001.net/images/20180829/1535505844_5b85f5b443843.png!small)

### Example 2：

![Vba2Graph](https://image.3001.net/images/20180829/1535505858_5b85f5c2aa9f3.png!small)

更多示例可在Examples文件夹中查看。

## 安装

###  **安装oletools**

    
    
    https://github.com/decalage2/oletools/wiki/Install

###  **安装Python依赖包**

    
    
    pip install -r requirements.txt

###  **安装Graphviz**

 **Windows**

安装Graphviz msi：

    
    
    https://graphviz.gitlab.io/_pages/Download/Download_windows.html

将“dot.exe”添加到PATH env变量或是：

    
    
    set PATH=%PATH%;C:\Program Files (x86)\Graphviz2.38\bin

 **Mac**

    
    
    brew install graphviz

 **Ubuntu**

    
    
    sudo apt-get install graphviz

 **Arch**

    
    
    sudo pacman -S graphviz

## 使用（所有平台）

    
    
    olevba malicious.doc | python vba2graph.py -c 1
    
    python vba2graph.py -i olevba_output.bas -o output_folder

## 输出

你将在output文件夹中看到3个文件夹：

> png：您要查找的实际图像
>
> dot：用于创建图像的文件
>
> bas：脚本识别的VBA函数代码（用于调试）

## 批处理

### Mac/Linux

batch.sh脚本文件，用于在恶意文档的input文件夹上运行olevba和vba2graph。

删除output目录。执行此操作时，一定要请谨慎！

***参考来源：[github](https://github.com/MalwareCantFly/Vba2Graph)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

