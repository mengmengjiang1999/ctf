## 一、背景介绍

黑莓公司在 Black Hat USA 2020 大会上开源了其逆向工程 PE 文件的工具 PE Tree，一个使用
[pefile](https://github.com/erocarrera/pefile)
和[PyQt5](https://pypi.org/project/PyQt5/) 的Python模块，源代码位于：

<https://github.com/blackberry/pe_tree>

## 二、PE tree 特性

### 1\. 使用Pyhton编写，可以作为单独的应用程序运行，也可以作为IDAPython插件运行

### 2\. 支持Windows/Linux/Mac

### 3\. 彩虹PE比例图表：PE结构、大小和文件位置，快速PE样例对比

### 4\. 支持以下PE头信息的树状显示

\- MZ header

\- DOS stub

\- Rich headers

\- NT/File/Optional headers

\- Data directories

\- Sections

\- Imports

\- Exports

\- Debug information

\- Load config

\- TLS

\- Resources

\- Version information

\- Certificates

\- Overlay

### 5\. 从以下位置提取和存储数据

\- DOS stub

\- Sections

\- Resources

\- Certificates

\- Overlay

### 6\. 可以将数据发送到CyberChef

### 7\. 在VirusTotal搜索

\- File hashes

\- PDB path

\- Timestamps

\- Section hash/name

\- Import hash/name

\- Export name

\- Resource hash

\- Certificate serial

## 三、作为IDA的插件安装

### 1\. 基本要求

\- IDA Pro 7.0+ with Python 2.7

\- IDA Pro 7.4+ with Python 2.7 or 3.x

### 2\. 两种安装方式

setuptools：

> $ git clone https://github.com/blackberry/pe_tree.git
>
> $ cd pe_tree
>
> $ python setup.py develop --ida

手动安装：

> $ git clone https://github.com/blackberry/pe_tree.git
>
> $ cd pe_tree
>
> $ pip install -r requirements.txt

### 3\. 将pe_tree_ida.py复制到IDA7.0的插件目录下：

OS | Plugins 文件夹目录  
---|---  
Windows | %ProgramFiles%\IDA Pro 7.X\plugins  
Linux | /opt/ida-7.X/plugins  
MacOS | ~/.idapro/plugins  
  
###  4\. 运行IDA并点击

> Edit -> Plugins -> PE Tree

![](https://image.3001.net/images/20200806/1596704767.png!small)

##  四、PE tree for IDAPython效果测试

### 1\. 运行PE Tree

这里笔者在Windows10下任意找了一个x64可执行文件做测试

![](https://image.3001.net/images/20200806/1596704075.png!small)

### 2\. PE文件彩虹结构效果

PE tree在IDA7.0中效果如下：

![](https://image.3001.net/images/20200806/1596704223.png!small)可以看到PE
tree将PE文件的文件头信息以及各个段数据分层罗列，并使用彩虹颜色进行表示，形象且直观。各类PE信息较为齐全，在进行逆向分析的时候更加方便查询。

### 3\. 段信息

点击.text段，可以查看text段信息，包括虚地址、Characteristics和比例等基本信息：

### ![](https://image.3001.net/images/20200806/1596704514.png!small)4\. 发送数据

将数据发送至VirusTotal和CyberChef：

![](https://image.3001.net/images/20200806/1596704575.png!small)使用效果可以自行查验。另外，PE
tree还可以很方便地转储各段的数据，提高逆向分析的效率。

### 5\. 切换地址表示方式

地址表示方式可以在虚拟内存地址和相对虚拟内存地址之间切换，方便逆向工程师计算：

### ![](https://image.3001.net/images/20200806/1596704735.png!small)6\. 双击跳转

PE tree保持了IDA的特性，双击各数据段可以非常方便地跳转到view窗口：

![](https://image.3001.net/images/20200806/1596704854.png!small)

## 五、总结

PE tree作为软件逆向工程开源的PE工具，其便利的特性和“rainbow
view”的PE文件结构高级概述可以提高对恶意软件分析的效率。这里笔者仅简单介绍PE tree和PE
tree作为IDAPython插件的安装和使用方法。有兴趣的朋友可以去继续深入探索PE
tree的各个功能，并从日常的逆向分析工作中看看是否能够提高自己逆向分析的效率。

