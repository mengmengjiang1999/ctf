![](https://image.3001.net/images/20211227/1640615031_61c9cc7778d7e08b9a809.jpg!small)

## 关于Kit Hunter

Kit Hunter是一款功能强大的网络钓鱼安全测试工具，该工具主要针对的是专用主机。Kit
Hunter基于Python开发，也是一款功能强大的安全扫描工具，该工具可以帮助广大研究人员根据已建立的标记搜索目录并定位网络钓鱼工具包。当该工具检测到了威胁时，将会为管理员生成相应的报告。

默认配置下，该脚本将会生成一份检测报告，并显示检测到的可能有问题的文件，然后还会给出存在问题的标记。除此之外，Kit
Hunter还会显示检测发生的确切代码行。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/SteveD3/kit_hunter.git

## 工具使用

### 帮助信息

下列命令可快速查看工具帮助信息：

    
    
    python3 kit_hunter_2.py -h

### 默认扫描

下列命令可通过默认设置启动完整扫描：

    
    
    python3 kit_hunter_2.py

### 快速扫描

如需启动快速扫描，可使用最小化的检测规则：

    
    
    python3 kit_hunter_2.py -q

### 自定义扫描

下列命令可启动自定义扫描：

    
    
    python3 kit_hunter_2.py -c

### 选择目录扫描

我们可以在任何位置使用-d选项运行kit_hunter_2.py来选择一个目录进行扫描：

    
    
    python3 kit_hunter_2.py -d /path/to/directory

最后，工具将会在目标扫描目录中生成一份最终的结果报告。

## Shell检测

Kit Hunter的最新版本带有Shell检测功能。Shell脚本通常与网络钓鱼工具包一起打包，或者用于在Web服务器上部署网络钓鱼工具包。Kit
Hunter将扫描一些常见的shell脚本元素，该过程的工作方式与常规扫描完全相同，可以通过-s选项仅执行Shell检测。

扫描完成后，脚本的输出将会链接至扫描报告的存储位置。

## 工具运行样例

![](https://image.3001.net/images/20211227/1640615078_61c9cca6eb28cb3d697aa.jpg!small)

## 项目地址

 **Kit Hunter：** 【[ _GitHub传送门_](https://github.com/SteveD3/kit_hunter)】

## 参考资料

> [ _https://steved3.io/data/Kit-Hunter-2.0-Getting-> Started/2021/09/07/﻿_](https://steved3.io/data/Kit-Hunter-2.0-Getting-> Started/2021/09/07/)

