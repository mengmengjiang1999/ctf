![](https://image.3001.net/images/20210922/1632318701_614b34ed8d3bf0ecb32df.jpg!small)

## 关于XLMMacroDeobfuscator

XLMMacroDeobfuscator一款针对XLM宏的安全工具，该工具可以帮助广大研究人员提取并解码经过混淆处理的XLM宏（Excel
4.0宏）。该工具可以使用一个内部XLM模拟器来解析宏文件，而且无需完整执行目标宏代码。

当前版本的XLMMacroDeobfuscator支持xls、xlsm和xlsb格式。

该工具使用了[ _xlrd2_](https://github.com/DissectMalware/xlrd2)、[
_pyxlsb2_](https://github.com/DissectMalware/pyxlsb2)和其自带的解析器来相应地从xls、xlsb和xlsm文件中提取单元数据以及其他信息。

你可以在[ _xlm-macro-lark.template_](https://github.com/DissectMalware/XLMMacroDeobfuscator/blob/master/XLMMacroDeobfuscator/xlm-macro.lark.template)查看XLM语法。

## 工具要求

XLMMacroDeobfuscator项目中提供的requirements.txt文件中给出了该项目所需的Python库。

XLMMacroDeobfuscator可以在任意操作系统上运行，并正常来相应地从xls、xlsb和xlsm文件中提取和解析XLM宏文件，而无需安装Microsoft
Excel。

## 模拟器安装

首先，我们需要使用pip下载和安装XLMMacroDeobfuscator：

    
    
    pip install XLMMacroDeobfuscator

接下来，我们可以使用下列命令安装最新的开发版本：

    
    
    pip install -U https://github.com/DissectMalware/xlrd2/archive/master.zip
    
    pip install -U https://github.com/DissectMalware/pyxlsb2/archive/master.zip
    
    pip install -U https://github.com/DissectMalware/XLMMacroDeobfuscator/archive/master.zip

## 模拟器运行

针对Excecl文档中的宏进行反混淆处理：

    
    
    xlmdeobfuscator --file document.xlsm

仅获取反混淆处理后的宏而不进行其他格式化处理：

    
    
    xlmdeobfuscator --file document.xlsm --no-indent --output-formula-format "[[INT-FORMULA]]"

以JSON格式导出输出数据：

    
    
    xlmdeobfuscator --file document.xlsm --export-json result.json

如需查看JSON输出样本，请点击【[ _这里_](https://pastebin.com/bwmS7mi0)】。

使用配置文件：

    
    
    xlmdeobfuscator --file document.xlsm -c default.config

default.config文件必须为有效的JSON文件，参考格式如下：

    
    
    {
    
    "no-indent": true,
    
    "output-formula-format": "[[CELL-ADDR]] [[INT-FORMULA]]",
    
    "non-interactive": true,
    
    "output-level": 1
    
    }

## 命令行使用

    
    
    _        _______
    
    |\     /|( \      (       )
    
    ( \   / )| (      | () () |
    
     \ (_) / | |      | || || |
    
      ) _ (  | |      | |(_)| |
    
     / ( ) \ | |      | |   | |
    
    ( /   \ )| (____/\| )   ( |
    
    |/     \|(_______/|/     \|
    
       ______   _______  _______  ______   _______           _______  _______  _______ _________ _______  _______
    
      (  __  \ (  ____ \(  ___  )(  ___ \ (  ____ \|\     /|(  ____ \(  ____ \(  ___  )\__   __/(  ___  )(  ____ )
    
      | (  \  )| (    \/| (   ) || (   ) )| (    \/| )   ( || (    \/| (    \/| (   ) |   ) (   | (   ) || (    )|
    
      | |   ) || (__    | |   | || (__/ / | (__    | |   | || (_____ | |      | (___) |   | |   | |   | || (____)|
    
      | |   | ||  __)   | |   | ||  __ (  |  __)   | |   | |(_____  )| |      |  ___  |   | |   | |   | ||     __)
    
      | |   ) || (      | |   | || (  \ \ | (      | |   | |      ) || |      | (   ) |   | |   | |   | || (\ (
    
      | (__/  )| (____/\| (___) || )___) )| )      | (___) |/\____) || (____/\| )   ( |   | |   | (___) || ) \ \__
    
      (______/ (_______/(_______)|/ \___/ |/       (_______)\_______)(_______/|/     \|   )_(   (_______)|/   \__/
    
     
    
        
    
    XLMMacroDeobfuscator(v0.1.9) - https://github.com/DissectMalware/XLMMacroDeobfuscator
    
     
    
    usage: deobfuscator.py [-h] [-c FILE_PATH] [-f FILE_PATH] [-n] [-x] [-2]
    
                           [--with-ms-excel] [-s] [-d DAY]
    
                           [--output-formula-format OUTPUT_FORMULA_FORMAT]
    
                           [--no-indent] [--export-json FILE_PATH]
    
                           [--start-point CELL_ADDR] [-p PASSWORD]
    
                           [-o OUTPUT_LEVEL]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -c FILE_PATH, --config_file FILE_PATH
    
                            Specify a config file (must be a valid JSON file)
    
      -f FILE_PATH, --file FILE_PATH
    
                            The path of a XLSM file
    
      -n, --noninteractive  Disable interactive shell
    
      -x, --extract-only    Only extract cells without any emulation
    
      -2, --no-ms-excel     [Deprecated] Do not use MS Excel to process XLS files
    
      --with-ms-excel       Use MS Excel to process XLS files
    
      -s, --start-with-shell
    
                            Open an XLM shell before interpreting the macros in
    
                            the input
    
      -d DAY, --day DAY     Specify the day of month
    
      --output-formula-format OUTPUT_FORMULA_FORMAT
    
                            Specify the format for output formulas ([[CELL-ADDR]],
    
                            [[INT-FORMULA]], and [[STATUS]]
    
      --no-indent           Do not show indent before formulas
    
      --export-json FILE_PATH
    
                            Export the output to JSON
    
      --start-point CELL_ADDR
    
                            Start interpretation from a specific cell address
    
      -p PASSWORD, --password PASSWORD
    
                            Password to decrypt the protected document
    
      -o OUTPUT_LEVEL, --output-level OUTPUT_LEVEL
    
                            Set the level of details to be shown (0:all commands,
    
                            1: commands no jump 2:important commands 3:strings in
    
                            important commands).
    
      --timeout N           stop emulation after N seconds (0: not interruption
    
                            N>0: stop emulation after N seconds)

## 以Python库的形式使用

下面的样例中，我们能够以Python库的形式使用XLMMacroDeobfuscator并对XLM宏进行反混淆处理：

    
    
    from XLMMacroDeobfuscator.deobfuscator import process_file
    
     
    
    result = process_file(file='path/to/an/excel/file',
    
                noninteractive= True,
    
                noindent= True,
    
                output_formula_format='[[CELL-ADDR]], [[INT-FORMULA]]',
    
                return_deobfuscated= True,
    
                timeout= 30)
    
     
    
    for record in result:
    
        print(record)

## 引入的项目

XLMMacroDeobfuscator基于以下项目实现其功能：

> [ _CAPE Sandbox_](https://github.com/ctxis/CAPE)
>
> [ _FAME_](https://certsocietegenerale.github.io/fame/)
>
> [ _REMNUX_](https://remnux.org/)
>
> [ _IntelOwl_](https://github.com/intelowlproject/IntelOwl)
>
> [ _Assemblyline
> 4﻿_](https://cybercentrecanada.github.io/assemblyline4_docs/)

## 项目地址

 **XLMMacroDeobfuscator：** 【[
_GitHub传送门_](https://github.com/DissectMalware/XLMMacroDeobfuscator)】

