臭名昭著的恶意软件僵尸网络 Emotet 在 2020 年 10 月底陷入低迷，又在 2020 年 12 月 21 日再次活跃。Emotet
充当恶意软件的桥头堡，在失陷主机上安装其他恶意软件。目前，观察到 Emotet 在野分发 TrickBot。立陶宛的国家公共卫生中心遭到了 Emotet
的攻击，Emotet 感染了其内部网络，并开始下载其他恶意软件。这导致立陶宛国家公共卫生中心暂时禁用了电子邮件系统，直到恶意软件被从内部网络中删除。

本文将会介绍 Emotet 的新 Loader 并与前期使用的 Loader
进行对比。二者在解压缩的顺序、文件的新属性和新的混淆方法上存在差异，与此同时还会讨论使用的检测逃避技术。

## 差异

### 执行流程

最终的 Payload
执行前要执行多个步骤：![1632805210_6152a15a024153d42fef3.png!small?1632805209686](https://image.3001.net/images/20210928/1632805210_6152a15a024153d42fef3.png!small?1632805209686)

观察最近收集的样本，减少了执行的步骤：![1632805224_6152a168b65c9e14d78b5.png!small?1632805224281](https://image.3001.net/images/20210928/1632805224_6152a168b65c9e14d78b5.png!small?1632805224281)

原因尚不清楚，但是猜测是因为较长的执行过程无法有效降低检测率。Emotet
使用一种被称为反射加载的技术来在所有阶段进行加载，那么如果某个安全产品可以检测到反射加载这个行为，则多次使用也无助于规避检测。

另一个可能的原因是，攻击者试图逃避专门为 Emotet
创建的启发式检测方法。因为先前的执行流程非常长，这变成了一个独特的特征。如果检测到如此长的执行流程也就可以发现
Emotet，所以更改执行流程的常读可能会有所帮助。

### Loader

Loader 也进行了一些更改。第一个变动是从可执行文件切换到 DLL。该 DLL 文件具有导出函数 `RunDLL`和
`Control_RunDLL`，这使检测由 Emotet 引起的感染成为可能。如果使用与导出匹配的参数启动了进程 rundll32.exe，则系统就是被
Emotet 被感染了。

    
    
    import “pe”private rule emotet_exports{condition:pe.exports(“RunDLL”) or pe.exports(“Control_RunDLL”)}private rule is_dll{condition:pe.characteristics & pe.DLL}﻿rule emotet{condition:is_dll and emotet_exports}

### 混淆技术

通过 Loader 提取得到的 Payload
使用了一种新的混淆技术，使用多个按位运算而非单个位运算来在局部变量中设置值。这种混淆在不执行代码的情况下非常难以理解，调试过程也十分繁琐。![1632805274_6152a19ab54134c72b017.png!small?1632805274349](https://image.3001.net/images/20210928/1632805274_6152a19ab54134c72b017.png!small?1632805274349)

## 相似之处

### 解密算法

Payload 加密后存储在 Loader 中，此前开发针对 Emotet 进行静态解密提取 Payload 的工具仍然有效，没有改变加密算法。

### 代码混淆

除上述混淆技术外，代码还包含一个复杂的条件分支和不必要的跳转指令，这让分析代码执行顺序变得异常困难。![1632805299_6152a1b3c355e16d997d7.png!small?1632805299721](https://image.3001.net/images/20210928/1632805299_6152a1b3c355e16d997d7.png!small?1632805299721)

### 隐藏数据

Payload 通过不列出 Windows API 的名称或者任何有意义的字符串来隐藏功能。研究人员必须通过调试才能知道 Payload
的功能，字符串以加密形式存储，API 使用名称的哈希值进行解析。

## 进化

2020 年末，Emotet 的进化在尽可能地降低检出的概率。由于感染的数量甚多，跟踪 Emotet 的不断进化至关重要，它的变动很可能会造成大面积的感染。

## 参考来源

> [DeepInstinct](https://www.deepinstinct.com/2021/01/07/emotet-malware-2020/)

