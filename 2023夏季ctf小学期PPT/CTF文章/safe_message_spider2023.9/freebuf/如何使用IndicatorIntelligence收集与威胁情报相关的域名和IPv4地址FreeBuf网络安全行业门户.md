![](https://image.3001.net/images/20230607/1686069697_647f61c185612bb1d3288.png!small)  

## 关于Indicator-Intelligence

Indicator-Intelligence是一款针对威胁情报的强大数据收集工具，该工具可以帮助广大研究人员通过威胁情报活动中生成的静态文件来查找与威胁行为相关的域名和IPv4地址。

需要注意的是，请在目标组织授权后再使用该工具进行安全分析，请不要将其用于恶意目的。

## 工具要求

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

## 工具下载

### 源码下载

我们建议广大用户在安装该工具之前，使用virtualenv来创建虚拟环境，并安装工具相关的依赖组件：

    
    
    git clone https://github.com/OsmanKandemir/indicator-intelligence.git
    
    cd indicator-intelligence
    
    python setup.py build
    
    python setup.py install

### Pypi安装

该工具也可以从[
_Pypi库_](https://pypi.org/project/indicatorintelligence/)中获取，直接使用下列命令即可安装Indicator-Intelligence：

    
    
    pip install indicatorintelligence

### Dockerfile安装

我们还可以在构建好Dockerfile之后，在一个容器中运行Indicator-Intelligence：

    
    
    docker build -t indicator .
    
    docker run indicator --domains target-web.com --json

### DockerHub安装

    
    
    docker pull osmankandemir/indicator
    
    docker run osmankandemir/indicator --domains target-web.com --json

### Poetry安装

    
    
    pip install poetry
    
    poetry install

## 工具使用

### 工具执行参数

    
    
    -d DOMAINS [DOMAINS], --domains DOMAINS [DOMAINS] 输入目标，例如 --domains target-web1.com target-web2.com
    
    -p PROXY, --proxy PROXY 使用HTTP代理，例如 --proxy 0.0.0.0:8080
    
    -a AGENT, --agent AGENT 使用代理，例如 --agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    
    -o JSON, --json JSON  设置JSON格式输出，例如 --json

### 作为函数使用

    
    
    from indicator.indicator import Indicator
    
     
    
    #SCAN
    
    Indicator(["target-web.com"])
    
     
    
    #OUTPUT
    
    Indicator(["target-web.com"],json=True)

## 工具运行截图

![](https://image.3001.net/images/20230607/1686069813_647f62355f38cefefb9b6.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3_ _._ _0_](https://github.com/OsmanKandemir/indicator-intelligence/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Indicator-Intelligence** ：【[
_GitHub传送门_](https://github.com/OsmanKandemir/indicator-intelligence)】

## 参考资料

> [
> _https://pypi.org/project/indicatorintelligence/﻿_](https://pypi.org/project/indicatorintelligence/)

