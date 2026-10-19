![](https://image.3001.net/images/20210719/1626693145_60f55e19f276b45748812.jpg!small)

## 关于Heappy

Heappy是一款功能强大的堆内存编辑器，该工具基于gdb/gef实现其功能，可以帮助广大研究人员在漏洞利用开发或渗透测试过程中处理堆内存信息。

该项目可以作为一个有助于帮助研究人员了解堆在进程生命周期中的演化情况，而它的主要功能就是简化对最常见堆开发技术的研究，并支持研究人员在CTF比赛中解决一些关于源码漏洞利用相关的问题。

## 主要功能

获取堆快照并进行相互比较；

立即识别堆代码中的类型和字段；

按十进制、十六进制或字符串搜索和编辑堆数据值；

可以查看到堆内存的完整状态；

在“注释”列中记录有关单元格的注释；

支持明亮模式和暗黑模式；

## 工具快速开始

下列的命令参数可以帮助广大研究人员快速安装并运行Heappy。

### 工具要求

首先，我们需要在GDB中安装好GEF：

    
    
    wget -q -O- https://github.com/hugsy/gef/raw/master/scripts/gef.sh | sh
    
    
    md5(gef.sh): eb053864d050048cb001c80c79fde7b5

### 工具安装

首先，我们需要安装Node.js和npm：

    
    
    apt update
    
    sudo apt install nodejs npm

接下来，使用下列命令下载并安装Heappy：

    
    
    git clone https://github.com/gand3lf/heappy
    
    cd heappy/
    
    npm install

安装好Heappy之后，我们需要在GDB中加载服务器：

    
    
    gef➤ source /my/path/heappy/server/heappy.py

我们建议大家在目标堆初始化完成之后，再运行Heappy GUI，比如说：

    
    
    gef➤ break main
    
    gef➤ run

除此之外，我们还可以在其他终端窗口中运行Heappy GUI：

    
    
    cd /my/path/heappy/
    
    npm start

现在，大家就可以尽情享受Heappy啦！

### 工具依赖组件

[ _Vue.js_](https://vuejs.org/)\- Web框架

[ _Electron_](https://www.electronjs.org/)\- Builder框架

[ _GEF_](https://github.com/hugsy/gef)\- GDB扩展

[ _Python3_](https://www.python.org/)\- 用于GEF集成

## 工具运行截图

![](https://image.3001.net/images/20210719/1626693177_60f55e39ea9f9cfea7422.png!small)

## 项目地址

 **Heappy：** 【[ _GitHub传送门_](https://github.com/gand3lf/heappy)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Gand3lf/heappy/blob/main/LICENSE)开源许可证协议。

