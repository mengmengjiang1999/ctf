**作者: Yenn_  
原文链接: [Wei's
Blog](https://0xdf1001f.github.io/2020/12/22/%E5%AF%B9Excel-4-0-Macro%E6%81%B6%E6%84%8F%E4%BB%A3%E7%A0%81%E7%9A%84%E4%B8%80%E6%AC%A1%E5%88%86%E6%9E%90/)**

## 0x1 背景

今天在推特上看见一个老哥发了一个针对意大利的样本，还是热乎的，遂下载下来分析看看，没想到是个Excel 4.0 Macro的样本，以前没仔细分析过Excel
4.0 Macro也没有总结记录过，这里写个文章总结一下分析的过程。

目的在于记录Excel 4.0 Macro的分析方法，所以就不跑动态行为和其他行为特征了，只看代码。

样本在http://yenne.ys168.com/

Sample目录下Abusech_ursnif.xls.zip

[![img](https://images.seebug.org/content/images/2021/03/16/1615867119000-1wvqph.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163104.png)

## 0x2 样本信息

File Name | File Size | File Type | MD5  
---|---|---|---  
Abusech_ursnif.xls | 202,240 Byte | Trojan | 0dd976de7791a9839f9bc1ef3b9ad2e9  
  
## 0x3 样本分析

xls文件名为”zv”表中打开一块空白，但仔细一看表有50000+行代码，其中大部分为空，部分代码穿插在表中

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-2itjrr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//006o5z8lgy1ggdr3t4h1wj31hc0pmjtj.jpg)

### 寻找代码

刚开始分析，搞了半天，也没有看见完整的代码，常用的oledump好像并不能Dump出Excel 4.0 Macro的代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-3czktz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163206.png)

后来找到了一个olevba.py的工具，属于分析OLE文件套件oletools下的一个工具，oletools网址http://www.decalage.info/python/oletools

安装方法：pip install -U https://github.com/decalage2/oletools/archive/master.zip

直接在CMD使用就好。

    
    
    Usage: olevba [options] <filename> [filename2 ...]
    
    Options:
      -h, --help            show this help message and exit
      -r                    find files recursively in subdirectories.
      -z ZIP_PASSWORD, --zip=ZIP_PASSWORD
                            if the file is a zip archive, open all files from it,
                            using the provided password.
      -p PASSWORD, --password=PASSWORD
                            if encrypted office files are encountered, try
                            decryption with this password. May be repeated.
      -f ZIP_FNAME, --zipfname=ZIP_FNAME
                            if the file is a zip archive, file(s) to be opened
                            within the zip. Wildcards * and ? are supported.
                            (default:*)
      -a, --analysis        display only analysis results, not the Excel 4.0 Macro source
                            code
      -c, --code            display only VBA source code, do not analyze it
      --decode              display all the obfuscated strings with their decoded
                            content (Hex, Base64, StrReverse, Dridex, VBA).
      --attr                display the attribute lines at the beginning of VBA
                            source code
      --reveal              display the Excel 4.0 Macro source code after replacing all the
                            obfuscated strings by their decoded content.
      -l LOGLEVEL, --loglevel=LOGLEVEL
                            logging level debug/info/warning/error/critical
                            (default=warning)
      --deobf               Attempt to deobfuscate VBA expressions (slow)
      --relaxed             Do not raise errors if opening of substream fails
    
      Output mode (mutually exclusive):
        -t, --triage        triage mode, display results as a summary table
                            (default for multiple files)
        -d, --detailed      detailed mode, display full results (default for
                            single file)
        -j, --json          json mode, detailed in json format (never default)

olevba.py可以得到样本内的代码与分析的结果

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-4dtziw.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163416.png)

将输出结果重定向到文件中

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-5angtz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163434.png)

### 寻找Auto_Open

输出的内容有1000+行，都不知道从哪开始找Auto_Open运行的函数，搜索Formula也没有结果，后来发现搜索auto_open后，在auto_open后面跟着要执行的函数地址

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-6zpjjv.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163453.png)

在最后”zv!CC906”，zv是表的名称，CC906是表中单元格位置，不知道为啥DUMP出的数据表格位置和文件中的位置有一点差距。

在DUMP的数据中找到CC906的位置，调用了一个DT31804

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-7rollw.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163507.png)

再找到DT31804

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-8phqpn.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163532.png)

### 反调试

可以看见调用了一个函数 APP.MAXIMIZE()，因为DUMP出的表格地址和文件中的地址有偏差，所以直接去文件中搜函数名APP.MAXIMIZE

[![img](https://images.seebug.org/content/images/2021/03/16/1615867120000-9gyavy.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163558.png)

这里就是部分反调试代码

    
    
    =IF(GET.WINDOW(7),$HN$8144(),)              //检查窗口是否隐藏      
    =IF(GET.WINDOW(20),,$HN$8144())             //检查窗口是否最大化
    =IF(GET.WINDOW(23)<3,$HN$8144(),)           //检查窗口大小
    =IF(GET.WORKSPACE(31),$HN$8144(),)          //检查代码是否单步运行
    =IF(GET.WORKSPACE(13)<770,$HN$8144(),)      //检查WorkPlace宽度
    =IF(GET.WORKSPACE(14)<380,$HN$8144(),)      //检查WorkPlace高度
    =IF(GET.WORKSPACE(19),,$HN$8144())          //检查是否有鼠标
    =IF(GET.WORKSPACE(42),,$HN$8144())          //检查是否有音频设备
    =IF(ISNUMBER(SEARCH("Windows",GET.WORKSPACE(1))),,$HN$8144())
    =$BJ$9452()         //获取当前运行样本的环境及版本号

反调试代码有一步没有通过，就会跳转到HN8144直接关闭程序的代码

### 代码

反调试代码后，跳转到地址BJ9452处，在文件中跟过去就行

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-10onhlf.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ggdv9xohtuj30ee07pjrm.jpg)

在olevba.py dump出的文件中的代码和样本中的代码有部分不一样

dump数据中的代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-11rtrgi.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163637.png)

样本中的代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-12hibrr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163700.png)

在样本中单步代码，选择求值，就可以得到和DUMP中一样的代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-13pnckp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163720.png)

然后有大量的类似代码用于加解密代码

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-14yufuz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163743.png)

### 下载执行

执行完成后，跳转到，调用导出函数

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-15dxuan.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163756.png)

调用URLDownloadToFileA从C2服务器”http://link.rolandchase.com/setup.exe"下载文件，并保存为"upeypgt.exe"

[![img](https://images.seebug.org/content/images/2021/03/16/1615867121000-16uiyny.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163819.png)

[![img](https://images.seebug.org/content/images/2021/03/16/1615867122000-17qvwsi.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163838.png)

下载完成后，再调用ShellExecuteA执行这个下载回的文件

[![img](https://images.seebug.org/content/images/2021/03/16/1615867122000-18llybb.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163858.png)

[![img](https://images.seebug.org/content/images/2021/03/16/1615867122000-19vdcya.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master//20201222163923.png)

## 0x4总结

分析过程中，可以通过olevba.py将代码DUMP出来，找到样本运行执行的函数，开始调试，在调试过程中，可点击求值选项，将混淆后的值反混淆出来，单步跟随得到样本目的。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1512/>

