![](https://image.3001.net/images/20230615/1686823451_648ae21bda177ba1115e5.png!small)

## 关于cbrutekrag

cbrutekrag是一款针对SSH服务器的渗透测试工具，该工具基于C语言开发，可以帮助广大研究人员使用字典攻击来对目标SSH服务器执行渗透测试。

该工具仅出于教育目的设计和开发，请在获得测试授权后再使用该工具。

## 工具要求

> [ _libssh﻿_](http://www.libssh.org/)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone --depth=1 https://github.com/matricali/cbrutekrag.git

### 项目构建

构建要求：

> make
>
> gcc编译器
>
> libssh-dev

构建命令：

    
    
    cd cbrutekrag
    
    make
    
    make install

### 静态构建

构建要求：

> cmake
>
> gcc编译器
>
> make
>
> libssh-dev
>
> libz-dev

构建命令：

    
    
    git clone --depth=1 https://github.com/matricali/cbrutekrag.git
    
    cd cbrutekrag
    
    bash static-build.sh
    
    make install

## 工具运行

![](https://image.3001.net/images/20230615/1686823503_648ae24f970211f475811.png!small)

### 参数解释

> -h 显示工具帮助信息
>
> -v Verbose模式
>
> -V Verbose模式(sshlib)
>
> -s 扫描模式
>
> -D 演示运行
>
> -P 进程条
>
> -T <targets> 目标文件
>
> -C <combinations> 用户名和密码文件
>
> -t <threads> 最大线程数量
>
> -o <output> 输出日志文件
>
> -a 接收非OpenSSH服务器
>
> -A 允许服务器被检测为蜜罐

## 支持的目标语法

> 192.168.0.1
>
> 10.0.0.0/8
>
> 192.168.100.0/24:2222
>
> 127.0.0.1:2222

## 组合文件格式

    
    
    root root
    
    root password
    
    root $BLANKPASS$

## 工具使用样例

    
    
    cbrutekrag -T targets.txt -C combinations.txt -o result.log
    
    cbrutekrag -s -t 8 -C combinations.txt -o result.log 192.168.1.0/24

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/matricali/cbrutekrag/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **cbrutekrag** ：【[ _GitHub传送门_](https://github.com/matricali/cbrutekrag)】

## 参考资料

> [ _http://www.libssh.org/﻿_](http://www.libssh.org/)

