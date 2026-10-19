![](https://image.3001.net/images/20220120/1642668555_61e9220b28717b1f45596.png!small)

## 关于Narthex

Narthex是一款功能强大的模块化可定制字典生成器，该工具基于C和Shell开发，至此在Unix或类Unix操作系统上运行。该工具包含了一个自治Unix风格的字典生成程序，可以帮助广大研究人员创建可用于密码恢复和安全评估的个性化词典。

根据Unix系统原理，Narthex可以利用Unix文本流进行相互协作。

## 工具组件

> nchance - 将结果添加到字典底部的大写转换工具。
>
> ninc - 一种递增工具，它将字母行相乘，并在每行末尾追加一个n++字符。
>
> ncom - 一种组合工具，用于在词典的现有行之间创建不同的组合。
>
> nrev - 一个反向工具，在字典末尾追加保留版本的行数据。
>
> nleet - 将字符替换为Leet等效项，例如替换为@而不是a，或3而不是e。
>
> nclean - 用于删除不符合条件（太短、无特殊字符等）的密码（长度太短或无特殊字符等）。
>
> napp - 在字典行之前或之后追加字符或单词。
>
> nwiz - 一个要求用户提供信息并将工具组合在一起以创建最终词典的向导工具。

## 工具安装

广大研究人员可以通过下列命令将该项目源码克隆至本地，并完成工具的安装：

    
    
    $ git clone https://github.com/MichaelDim02/Narthex.git && cd Narthex
    
    $ sudo make install

## 工具使用

该工具的使用非常简单，我们提供了一个向导程序来帮助大家轻松生成定制化、个性化字典文件：

    
    
    $ nwiz

运行上述命令之后，工具将要求用户输入目标的相关信息，并生成对应的字典文件。

## 高级使用

如果你想要最大限度地发挥Narthex的作用，可以详细阅读该工具组件的操作手册，了解这些组件的功能和特点等等。

比如说，我们可以将一组关键词以不同行存储到一个文本文件“words.txt”中，并运行下列命令来生成字典：

    
    
    $ cat words.txt | nhance -f | ncom | nrev | nleet | ninc 1 30 > dictionary.txt

此时，我们将能够看到生成的字典文件了。

## 工具运行截图

![](https://image.3001.net/images/20220120/1642668598_61e922360f67248d9f28a.png!small)

![](https://image.3001.net/images/20220120/1642668606_61e9223e1dd04aae123a6.png!small)

## 工具演示视频

为了方便广大用户的使用，也方便非Unix用户上手Narthex，开发人员专门录制了一个工具演示视频： _https://www.you_ _*_
_tube.com/watch?v=U0UmCeLJSkk &t=938s_

## 许可证协议

本项目的开发与发布遵循GPL v3.0开源许可证协议。

## 项目地址

 **Narthex：** 【[ _GitHub传送门_](https://github.com/MichaelDim02/Narthex)】

## 参考资料

>  _https://www.you_ _*_ _tube.com/watch?v=U0UmCeLJSkk &t=938s_

