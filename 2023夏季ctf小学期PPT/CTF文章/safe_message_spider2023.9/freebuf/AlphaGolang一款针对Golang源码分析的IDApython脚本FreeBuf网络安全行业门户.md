![](https://image.3001.net/images/20220121/1642699431_61e99aa79e183783f1010.png!small)

## 关于AlphaGolang

AlphaGolang是一款针对Golang源码分析的IDApython脚本，该脚本基于Python
3进行了重构和更新，可以帮助广大研究人员或恶意软件逆向工程师深入分析Go二进制文件。该工具的核心思想是将脚本代码分解为具体的步骤，并模仿分析人员在处理和测试Go二进制文件时可能遵循的某些方法或策略。

## 工具要求

> IDA Pro（推荐v7.6+）

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/SentineLabs/AlphaGolang.git

## AlphaGolang分析方法论

### 第一步：Yara规则识别Go源码（PE/ELF/MachO）

> identify_go_binaries.yara：
>
> 1、简单的Header检测和针对Go构建ID字符串的正则表达式；
>
> 2、可以增加构建ID的长度范围。

### 第二步：重新创建pcln表

![](https://image.3001.net/images/20220121/1642699533_61e99b0de71c67f52fcee.gif)

> recreate_pclntab.py（兼容IDA v7.5）：
>
> 1、通过启发式算法重新创建gopclntab字段
>
> 2、兼容IDA v7.5。

### 第三步：通过遍历pcln表发现函数，并添加名称

![](https://image.3001.net/images/20220121/1642699570_61e99b32553b46c40115c.gif)

  

> function_renaming.py（兼容IDA v7.5）：
>
> 1、分离Golang加载器；
>
> 2、基于pcln表和暴力破解方式发现缺失的函数；
>
> 3、修复py3转换中的一些函数名清理问题；

### 第四步：用户生成的函数浮出水面

![](https://image.3001.net/images/20220121/1642699652_61e99b84d7e25758904a0.gif)

> categorize_go_folders.py（要求IDA v7.6+）：
>
> 1、自动将函数归类进目录中；
>
> 2、要求IDA v7.6+，在函数试图内启用“显示目录”功能；

### 第五步：修复字符串应用

![](https://image.3001.net/images/20220121/1642699690_61e99baa8d3a93d2add6b.gif)

> fix_string_cast.py：
>
> 1、分离Golang加载器；
>
> 2、添加逻辑以实现取消对以前存在的字符串blob的定义；
>
> 3、数据净化功能提升工具执行效率；

### 第六步：提取类型信息

![](https://image.3001.net/images/20220121/1642699730_61e99bd2a7746c02616a4.gif!small)

> extract_types.py：
>
> 1、在newobject和makechan等调用的参数上添加注释；
>
> 2、将正确的C类型应用于这些对象并进行重命名；
>
> 3、获取人类可读的名称并将其添加为注释；

## 许可证协议

本项目的开发与发布遵循GPL开源许可证协议。

## 项目地址

 **AlphaGolang：** 【[ _GitHub传送门_](https://github.com/SentineLabs/AlphaGolang)】

## 参考资料

> [
> _https://github.com/strazzere/golang_loader_assist﻿_](https://github.com/strazzere/golang_loader_assist)

