![](https://image.3001.net/images/20210914/1631628337_6140ac314fca2a4fe673b.png!small)

## 关于TIGMINT

 **TIGMINT是一款功能强大的开源情报GUI软件框架，该工具针对Twitter、Instagram和地理标记应用设计。**

TIGMINT通过实现抽象机制以隐藏其背后技术细节的复杂性，可以帮助广大研究人员更加方便地进行网络调查活动。

TIGMINT引入了多种不同的针对社交媒体情报的分析技术，并且还提供了一个简单的入侵式Web接口以帮助用户与之进行交互。

## 工具要求

Python 3.6;

beautifulsoup4;

Nodejs;

matplotlib;

pandas;

NPM;

nltk;

## 项目界面

### 概览

![](https://image.3001.net/images/20210914/1631628372_6140ac54619679e93f383.png!small)

### 模块选择

![](https://image.3001.net/images/20210914/1631628380_6140ac5ca75683a84cf1a.png!small)

### 团队

![](https://image.3001.net/images/20210914/1631628387_6140ac63763c518974f5c.png!small)

### 文档

![](https://image.3001.net/images/20210914/1631628395_6140ac6b6c2b404a5a6c9.png!small)

### 账号查找工具

![](https://image.3001.net/images/20210914/1631628402_6140ac722c25dcc18a340.png!small)

### Twitter分析器

![](https://image.3001.net/images/20210914/1631628409_6140ac7955a77f1c8f26c.png!small)

## Windows安装问题

针对Windows用户，如果安装失败或应用程序总是被重定向至404错误页面，你可以参照下列步骤解决问题。

1、验证requirements.txt中要求的所有模块是否成功安装，或重新运行下列命令：

    
    
    pip3 install -r requirements.txt

2、检查所有的Node所需组件是否正常安装，或运行下列命令：

    
    
    npm install

## Linux源数据分析所需组件

    
    
    sudo apt install exiftool

TIGMINT需要使用上述工具来从各种文件格式中获取元数据。

## 工具安装和运行

广大研究人员可以使用下列命令将该项目源码克隆至本地，然后安装完工具所需依赖组件之后，直接运行脚本文件：

    
    
    git clone https://github.com/TIGMINT/TIGMINT
    
    cd TIGMINT
    
    pip3 install -r requirements.txt
    
    pip3 install --user --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint
    
     
    
    npm install
    
    node Api/server.js

### 使用Docker

我们可以运行下列命令来运行Docker：

    
    
    docker run --name tigmint -p 3000:3000 k1m0ch1/tigmint

接下来，在浏览器中访问“http://localhost:3000”。

或者，我们也可以使用下列命令手动完成镜像构建：

    
    
    docker build -t tigmint .

## 工具使用截图

![](https://image.3001.net/images/20210914/1631628452_6140aca4cccd182057ac9.png!small)

![](https://image.3001.net/images/20210914/1631628461_6140acad3ed1e4c8b31a9.png!small)

![](https://image.3001.net/images/20210914/1631628467_6140acb3c05d7a832246f.png!small)

![](https://image.3001.net/images/20210914/1631628473_6140acb9c683500f2ea86.png!small)

![](https://image.3001.net/images/20210914/1631628479_6140acbfed923556c29bb.png!small)

![](https://image.3001.net/images/20210914/1631628485_6140acc5d3e8656c6f886.png!small)

![](https://image.3001.net/images/20210914/1631628493_6140accd4fc4bcdde4ba7.png!small)

![](https://image.3001.net/images/20210914/1631628500_6140acd407000e0db39a1.png!small)

![](https://image.3001.net/images/20210914/1631628505_6140acd9dcb7c2e07da49.png!small)

![](https://image.3001.net/images/20210914/1631628513_6140ace18341dd7bbbb8d.png!small)

## 项目地址

 **TIGMINT：** 【[ _GitHub传送门_](https://github.com/TIGMINT/TIGMINT)】

## 参考资料

> [
> _https://www.lfd.uci.edu/~gohlke/pythonlibs/#wordcloud﻿_](https://www.lfd.uci.edu/~gohlke/pythonlibs/#wordcloud)
>
> [ _https://stackoverflow.com/questions/41409570/cant-install-wordcloud-in-> python-anaconda﻿_](https://stackoverflow.com/questions/41409570/cant-> install-wordcloud-in-python-anaconda)

