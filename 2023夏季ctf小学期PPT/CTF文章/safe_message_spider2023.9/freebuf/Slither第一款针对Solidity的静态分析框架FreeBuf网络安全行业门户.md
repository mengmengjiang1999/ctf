**Slither是第一个开源的针对Solidity语言的静态分析框架。Slither速度非常快，准确性也非常高，它能够在不需要用户交互的情况下，在几秒钟之内找到真正的漏洞。该工具高度可配置，并且提供了多种API来帮助研究人员审计和分析Solidity代码。**

![1.png](https://image.3001.net/images/20181111/1541871508_5be7179417859.png!small)

目前，我们开源了Slither的核心分析引擎，这个核心提供了很多高级静态分析功能。除此之外，我们还构建了很多检测工具。

如果你是一名智能合约的开发者，一名安全专家，或者是一名学术研究人员，你肯定能发现Slither的价值。

## 可自主集成其他功能

Slither拥有简单的命令行接口，如果你想对一份Solidity文件运行所有的检测工具，你只需要运行：

    
    
    $slither contract.sol

![1.gif](https://image.3001.net/images/20181111/1541871522_5be717a2467e0.gif!small)

你可以在无需进行任何配置的情况下，将你自己设计的功能整合进Slither，不过你需要确保自己添加的代码不存在漏洞。

## 自动化安全审计

Slither提供了一个API来给研究人员通过自定义脚本审计Solidity代码。我们可以使用Slither做到：

> 1、 识别能够修改变量值的代码；
>
> 2、 隔离受特定变量值影响的条件逻辑语句；
>
> 3、 查找能够调用特定函数的其他函数；

比如说下面这段脚本， myContract的function(s)函数会给状态变量myVar写入值：

    
    
    #function_writing.py
    
    import sys
    
    from slither.slither import Slither
    
     
    
    iflen(sys.argv) != 2:
    
    print('python.pyfunction_writing.py file.sol')
    
    exit(-1)
    
     
    
    #Init slither
    
    slither= Slither(sys.argv[1])
    
     
    
    # Getthe contract
    
    contract= slither.get_contract_from_name('myContract')
    
     
    
    # Getthe variable
    
    myVar= contract.get_state_variable_from_name('myVar')
    
     
    
    # Getthe functions writing the variable
    
    funcs_writing_myVar= contract.get_functions_writing_to_variable(myVar)
    
     
    
    #Print the result
    
    print('Functionsthat write to "myVar": {}'.format([f.name for f infuncs_writing_myVar]))

大家可以阅读一下【[API文档](https://github.com/trailofbits/slither/wiki/API-examples)】和【[样本代码](https://github.com/trailofbits/slither/tree/master/examples/scripts)】来初步了解Slither。

### 帮助理解智能合约

Slither预定义了一套“printer”，它们可以显示关于智能合约的高级信息，其中包括四个关于安全方面的关键数据：合约摘要、函数摘要、继承图和授权概述。

1、 合约摘要printer

这个printer可以快速显示合约的大致信息，并显示函数和对应的可见度：

![2.png](https://image.3001.net/images/20181111/1541871558_5be717c67867b.png!small)

2、 函数摘要printer

显示关于每个函数的信息，例如状态变量、读写操作和函数调用信息：

![3.png](https://image.3001.net/images/20181111/1541871566_5be717cec5f60.png!small)3、
继承图printer

以图表的形式输出所有合约的继承依赖关系：

![4.png](https://image.3001.net/images/20181111/1541871574_5be717d6827be.png!small)4、
授权printer

显示用户对智能合约的操作权限：

![5.png](https://image.3001.net/images/20181111/1541871582_5be717de864a2.png!small)

大家可以查看一下Slither的【[文档](https://github.com/trailofbits/slither/wiki/Printer-documentation)】来了解如何添加自己的printer。

## 工具安装

Slither要求Python
3.6+、[solc](https://github.com/ethereum/solidity/)和Solidity编译器。

使用pip安装：

    
    
    $ pip install slither-analyzer

使用Git安装：

    
    
    $ git clone <https://github.com/trailofbits/slither.git> && cd slither
    
    $ python setup.py install

## 工具使用

审计单一文件：

    
    
    $slither tests/uninitialized.sol # argument can be file, folder or glob, be sureto quote the argument when using a glob
    
    [..]
    
    INFO:Detectors:Uninitializedstate variables in tests/uninitialized.sol, Contract: Uninitialized, Vars:destination, Used in ['transfer']
    
    [..]

如果目标是一个目录的话，它将会审计目录中的每一个.sol文件。

### 项目地址

> GitHub：<https://github.com/trailofbits/slither>

*参考来源：[trailofbits](https://blog.trailofbits.com/2018/10/19/slither-a-solidity-static-analysis-framework/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM

