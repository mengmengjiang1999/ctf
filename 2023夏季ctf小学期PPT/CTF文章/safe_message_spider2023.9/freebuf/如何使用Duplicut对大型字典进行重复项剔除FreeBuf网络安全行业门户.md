![](https://image.3001.net/images/20210505/1620202478_609253ee7b6959ee45ec2.jpg!small)

## 概述

现代密码字典在创建过程中通常会连接多个数据源，在理想情况下，最有可能成功的密码一般都位于字典列表的开头部分，这样才能够确保密码在最短的时间里被破解成功。

使用现有的消除重复数据的工具，还必须通过排序的方法来实现，这样就没办法确保可能性最大的密码排在前列了。

很不幸的是，字典的创建通常要求满足下列条件：

![](https://image.3001.net/images/20210505/1620202487_609253f7c1264a69ff89f.png!small)

Duplicut这款工具可以帮助广大研究人员在不需要对字典密码排序的情况下，轻松剔除重复项，以实现更快速的基于字典的密码暴力破解。

## 功能介绍

> 处理大型字典，即使其大小超过了可用RAM；
>
> 通过定义最大长度过滤字典行（-l选项）；
>
> 能够移除包含了不可打印ASCII字符的字典行（-p选项）；
>
> 按下任意键即可显示程序运行时状态；

## 技术实现

> Duplicut基于纯C语言开发，运行速度非常快；
>
> 在64位平台上压缩Hashmap；
>
> 多线程支持；

## 限制条件

> 长度超过255个字符的字典行将被忽略；
>
> 仅在Linux x64平台上进行了测试；

## 快速使用

    
    
    git clone https://github.com/nil0x42/duplicut
    
    cd duplicut/ && make
    
    ./duplicut wordlist.txt -o clean-wordlist.txt

## 功能选项

![](https://image.3001.net/images/20210505/1620202507_6092540bc1763b410e894.png!small)

## 技术细节

### 内存优化

使用了uni64在Hashmap种实现快速索引：

![](https://image.3001.net/images/20210505/1620202521_60925419944571596d24e.png!small)

### 大型文件处理

如果整个文件超过了内存大小，则会被切割为多个虚拟数据块，并单独进行测试：

![](https://image.3001.net/images/20210505/1620202528_6092542008e6dcba55a9c.png!small)

## 问题处理

如果你发现程序运行过程中存在漏洞，或者报错的话，请在调试模式下编译Duplicut并查看输出：

    
    
    # debug level can be from 1 to 4
    
    make debug level=1
    
    ./duplicut [OPTIONS] 2>&1 | tee /tmp/duplicut-debug.log

## 项目地址

Duplicut：【[ _GitHub传送门_](https://github.com/nil0x42/duplicut)】

## 参考资料

> [
> _https://github.com/nil0x42/duplicut/blob/master/src/line.c#L39_](https://github.com/nil0x42/duplicut/blob/master/src/line.c#L39)
>
> [
> _https://github.com/nil0x42/duplicut/issues﻿_](https://github.com/nil0x42/duplicut/issues)

