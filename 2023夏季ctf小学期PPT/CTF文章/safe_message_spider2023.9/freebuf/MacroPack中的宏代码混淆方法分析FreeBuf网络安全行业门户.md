## **宏混淆工具**

**Macro_Pack是一个用于自动化混淆及生成Office文档、VB脚本、快捷方式等文件的工具，其主要用于渗透测试、demo以及社会工程学评估。macro_pack的目标是简化利用流程，反恶意软件绕过，并自动化实现从vba生成到最终Office文档生成的过程。**

    
    
    Github：<https://github.com/sevagas/macro_pack>。

Macro_Pack分为专业模式和普通模式，专业模式包含了更多的混淆手段，但源码现在并未公开出来。普通模式的混淆手段包括“名称混淆”、“字符串混淆”以及“格式混淆”。

![](https://image.3001.net/images/20190816/1565921685_5d5611952ddd4.png!small)

如下为混淆执行流程，普通模式只会执行”ObfuscateNames”、”ObfuscateStrings”以及”ObfuscateForm”；而专业模式还会执行”AvBypass”、”UACBypass”等，通过函数名猜测其应该为杀软绕过、UAC绕过等功能，可以看出专业模式确实很强大且过于“武器化”，作者也是出于这方面考虑才没有公开。

![](https://image.3001.net/images/20190816/1565921705_5d5611a94e73a.png!small)

##  名称混淆

通过关键字的正则匹配，查找出保留函数以外的自定义过程（Sub）及函数（Function）名称，并保存到列表vbaFunctions中：

![](https://image.3001.net/images/20190816/1565921720_5d5611b80304e.png!small)

保留函数为VBA的一些开始函数，如”AutoOpen”、”Workbook_Open”：

![](https://image.3001.net/images/20190816/1565921727_5d5611bf85093.png!small)

逐行查找vbaFunctions列表中的函数名，在定义及调用处将其替换为随机字符串：

![](https://image.3001.net/images/20190816/1565921736_5d5611c8b4600.png!small)

同样的，通过“String”、”Integer”等关键字的正则匹配查找出变量声明，然后在其声明及使用处将其替换为随机字符串：

![](https://image.3001.net/images/20190816/1565921747_5d5611d3499a6.png!small)

对常数“0”“1”“2”，在开头使用随机字符串定义为Const常量，然后在后面使用这3个常数的地方将其替换：

![](https://image.3001.net/images/20190816/1565921755_5d5611dba0379.png!small)

最后，用同样的方式将导入函数名替换为随机字符串：

##
![](https://image.3001.net/images/20190816/1565921763_5d5611e3ba5d3.png!small)
**字符串混淆**

识别到宏代码中的字符串后，将其随机进行切分后用“&”连接：

![](https://image.3001.net/images/20190816/1565921772_5d5611ec5482a.png!small)

将字符串编码为16进制，并作为参数传给16进制解码函数“HexToStr”：

![](https://image.3001.net/images/20190816/1565921779_5d5611f3bbc93.png!small)

HexToStr函数如下，用于在VBA运行起来后解码字符串：

![](https://image.3001.net/images/20190816/1565921788_5d5611fc34043.png!small)

HexToStr函数名及其中使用的变量名用随机字符串替换：

![](https://image.3001.net/images/20190816/1565921795_5d56120380cbb.png!small)

##  **格式混淆**

移除宏代码中的注释：

![](https://image.3001.net/images/20190816/1565921802_5d56120a30f6e.png!small)

将制表符替换为空格：

![](https://image.3001.net/images/20190816/1565921809_5d56121158f94.png!small)

移除每行宏代码前的空格，即缩进，降低代码可读性：

##
![](https://image.3001.net/images/20190816/1565921816_5d5612185b4c7.png!small)
**混淆效果**

使用macro_pack可分别生成非混淆和混淆的宏，效果如下：

###  **非混淆：**

结构清晰，可读性强，能够看到包含明显的特征信息。

![](https://image.3001.net/images/20190816/1565921825_5d56122162247.png!small)

###  **混淆：**

上面的宏混淆后如下，可以看到混淆后的宏代码静态已经几乎不可读，并且也抹去了很多特征信息。

##
![](https://image.3001.net/images/20190816/1565921832_5d561228dd39a.png!small)
**写在最后**

防止逆向工程并不是Macro_Pack混淆的主要目的，其主要目的是防止防病毒检测。以上内容主要是针对Macro_Pack工具对宏代码的混淆方法进行分析，供测试人员，安全研究人员或其他有学习目的的人交流学习使用。

***本文作者：深信服千里目安全实验室，转载须注明来自FreeBuf.COM**

