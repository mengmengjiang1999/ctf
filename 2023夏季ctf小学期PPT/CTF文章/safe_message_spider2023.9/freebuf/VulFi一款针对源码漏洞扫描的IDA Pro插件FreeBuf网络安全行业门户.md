![](https://image.3001.net/images/20220506/1651842219_62751cabdbfeea2af43d6.png!small)  

## 关于VulFi

VulFi，全称为Vulnerability Finder，即“漏洞发现者”，它是一个IDA
Pro插件，可以帮助广大研究人员在二进制文件中查找漏洞。VulFi的主要目标是在一个单一视图中给研究人员提供包含了各种函数交叉引用的相关信息。对于可以使用Hexrays反编译器的情况，该工具还可以尝试排除针对这些函数的调用。

## 注意事项

在运行VulFi之前，请确保已经了解了你说要测试的代码，然后尝试识别所有的标准函数（例如strcpy和memcpy等），然后确保它们正确明明。插件是大小写不敏感的，因此MEMCPY、Memcpy和memcpy都是可以识别的。需要注意的是，搜索函数时需要精确匹配。

除此之外，VulFi将尽最大努力来过滤所有明显的误报。

## 工具安装

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Accenture/VulFi.git

接下来，将项目中的vulfi.py、vulfi_prototypes.json和vulfi_rules.json这三个文件拷贝到IDA插件目录下即可：

    
    
    cp vulfi* <IDA_PLUGIN_FOLDER>

## 工具使用

### 扫描

点击顶部菜单栏中的“Search >
VulFi”即可初始化扫描任务。此时，工具将初始化一次新的扫描，或读取之前存储在“idb/i64”文件中的扫描结果。扫描完成后，数据将会自动存储到数据库中。

 **扫描结果包含下列内容：**

> 1、IssueName：可疑问题的标题标签；
>
> 2、FunctionName：函数名称；
>
> 3、FoundIn：包含潜在安全问题引用的函数；
>
> 4、Address：检测到调用的地址；
>
> 5、Status：审阅状态，包含Not Checked、False、Positive、Suspicious和Vulnerable；
>
> 6、Priority：优先级，包含High、Medium和Low；

### 分析

当我们想要查看潜在的包含安全问题的函数实例时，可以直接双击目标代码行，IDA将会直接导航到内存地址。

### 设置自定义规则

工具还支持我们加载包含了多种自定义规则的自定义文件，下面给出的是自定义规则文件的数据结构：

    
    
    [   // An array of rules
    
        {
    
            "name": "RULE NAME", // The name of the rule
    
            "alt_names":[
    
                "function_name_to_look_for" // List of all function names that should be matched against the conditions defined in this rule
    
            ],
    
            "wrappers":true,    // Look for wrappers of the above functions as well (note that the wrapped function has to also match the rule)
    
            "mark_if":{
    
                "High":"True",  // If evaluates to True, mark with priority High (see Rules below)
    
                "Medium":"False", // If evaluates to True, mark with priority Medium (see Rules below)
    
                "Low": "False" // If evaluates to True, mark with priority Low (see Rules below)
    
            }
    
        }
    
    ]

## 规则设置

### 可用变量

> 1、param[<index>]：用访问函数调用的参数（index起始为0）；
>
> 2、function_call：用于访问函数调用事件；
>
> 3、param_count：获取传递给函数的参数数量；

### 可用函数

> 1、判断参数是否为常量：param[<index>].is_constant()
>
> 2、获取参数的数字值：param[<index>].number_value()
>
> 3、获取参数的字符串值：param[<index>].string_value()
>
> 4、调用后参数是否被设置为NULL：param[<index>].set_to_null_after_call()
>
> 5、函数的返回值是否经过检测：function_call.return_value_checked(<constant_to_check>)

## 工具使用演示

### 基础使用

![](https://image.3001.net/images/20220506/1651842304_62751d00d8f125eda863a.gif)

### 添加自定义规则

![](https://image.3001.net/images/20220506/1651842326_62751d1640d8674eef7cb.gif)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/Accenture/VulFi/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **VulFi：** 【[ _GitHub传送门_](https://github.com/Accenture/VulFi)】

## 参考资料

> [
> _https://github.com/Accenture/VulFi/blob/main/rule_template_file.json﻿_](https://github.com/Accenture/VulFi/blob/main/rule_template_file.json)

  

