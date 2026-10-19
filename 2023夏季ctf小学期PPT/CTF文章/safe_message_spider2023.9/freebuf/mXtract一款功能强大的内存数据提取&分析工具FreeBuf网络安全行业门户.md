## mXtract

**mXtract是一款开源的Linux安全工具，该工具可从目标系统的内存中提取并分析数据。从本质上来说，mXtract是一款防御端渗透测试工具，它的主要功能是扫描目标系统内存并尝试通过正则表达式来从中提取出私钥、IP和用户密码等敏感数据。请记住，扫描结果跟正则表达式的质量息息相关…**

## 工具截图

![mXtract](https://image.3001.net/images/20190414/1555179573_5cb22835b6472.png!small)

Verbose模式扫描单个IP正则式，扫描单个数据段，显示整个扫描进程信息以及扫描的环境文件。

![mXtract](https://image.3001.net/images/20190414/1555179580_5cb2283cb5685.png!small)

Verbose模式扫描单个IP正则式，扫描范围仅限堆栈空间，显示扫描进程信息，扫描环境文件。

![mXtract](https://image.3001.net/images/20190414/1555179586_5cb2284263726.png!small)

简单扫描，单个IP正则式，显示扫描进程信息，扫描环境文件。

### 为什么直接从内存中导出数据？

在大多数Linux环境中，用户可以直接访问进程的内存信息，这将允许攻击者收集用户凭证、私钥或其他敏感信息。

## 功能介绍

> 1、 可输入正则表达式列表；
>
> 2、 清晰可读的显示数据；
>
> 3、 使用当前权限检测内存范围是否可写；
>
> 4、 以XML和HTML格式输出数据；
>
> 5、 大规模扫描每一个进程或特定的PID；
>
> 6、 选择特定的内存区域进行扫描；
>
> 7、 显示详细的进程信息；
>
> 8、 扫描进程环境文件；
>
> 9、 内存数据自动导出，并移除Unicode字符

### 工具下载

    
    
    git clone https://github.com/rek7/mXtract

### 工具编译

    
    
    cd mXtract && sh compile.sh

命令运行完成之后，将创建/bin/目录，并将代码编译为mxtract。

## 命令

![mXtract](https://image.3001.net/images/20190414/1555179592_5cb22848c0431.png!small)

### 工具使用样例

    
    
    $./mxtract -wm -wr -e -i -d=/tmp/output/ -r=example_regexes.db

## 项目地址

mXtract：【[GitHub传送门](https://github.com/rek7/mXtract)】

 ***
参考来源：[mXtract](https://github.com/rek7/mXtract)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

