![](https://image.3001.net/images/20210821/1629520070_612080c63c88e3ae47db6.png!small)

## 关于FRIDA-DEXDump

FRIDA-DEXDump是一款功能强大的内存数据操作工具，该工具可以帮助广大研究人员轻松搜索或导出dex内存数据。

## 功能介绍

当前版本的FRIDA-DEXDump支持以下几种功能：

> 针对dex Header支持模糊搜索；
>
> 支持修复dex Header的结构数据；
>
> 与所有Android版本兼容（支持Frida）。
>
> 支持加载为Objection插件。
>
> 已封装为pypi包（已发布）。

## 工具要求

1、[ _Frida_](https://www.github.com/frida/frida)：

    
    
    pip install frida

2、[ _Click_](https://pypi.org/project/click/)（可选）：

    
    
    pip install click

## 工具安装

### 从pypi安装

    
    
    pip3 install frida-dexdump
    
    frida-dexdump -h

### 从代码源安装

    
    
    git clone https://github.com/hluwa/FRIDA-DEXDump
    
    cd FRIDA-DEXDump/frida-dexdump
    
    python3 main.py -h

## 工具使用

首秀按我们需要运行frida-dexdump或python3 main.py来与最前端的应用程序进行绑定，并导出dex数据。

或者，广大研究人员也可以使用下列命令行参数来执行其他功能：

    
    
    -n: [Optional] Specify target process name, when spawn mode, it requires an application package name. If not specified, use frontmost application.
    
    -p: [Optional] Specify pid when multiprocess. If not specified, dump all.
    
    -f: [Optional] Use spawn mode, default is disable.
    
    -s: [Optional] When spawn mode, start dump work after sleep few seconds. default is 10s.
    
    -d: [Optional] Enable deep search maybe detected more dex, but speed will be slower.
    
    -h: show help.

## 以插件加载

除此之外，我们还可以将其以Objection插件进行加载。

首先，我们需要克隆该项目代码库，并将frida_dexdump内容移动至你的插件目录中：

    
    
    git clone https://github.com/hluwa/FRIDA-DEXDump ~/Downloads/FRIDA-DEXDump;
    
    mv ~/Downloads/FRIDA-DEXDump/frida_dexdump ~/.objection/plugins/dexdump

接下来，运行下列命令（使用-p或--plugin-folder参数）：

    
    
    objection -g com.app.name explore -P ~/.objection/plugins

然后，执行下列命令：

 **1、搜索并输出所有的dex数据：**

    
    
    plugin dexdump search

 **2、导出所有找到的dex数据：**

    
    
    plugin dexdump dump

## 项目地址

 **FRIDA-DEXDump：** 【[ _GitHub传送门_](https://github.com/hluwa/FRIDA-DEXDump)】

## 参考资料

  * [ _https://mp.weixin.qq.com/s/n2XHGhshTmvt2FhxyFfoMA_](https://mp.weixin.qq.com/s/n2XHGhshTmvt2FhxyFfoMA)

