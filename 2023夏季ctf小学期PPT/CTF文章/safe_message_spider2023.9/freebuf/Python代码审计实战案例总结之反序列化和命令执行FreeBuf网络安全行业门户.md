## 介绍

**Python代码审计方法多种多样，但是总而言之是根据前人思路的迁移融合扩展而形成。目前Python代码审计思路，呈现分散和多样的趋势。Python微薄研发经验以及结合实际遇到的思路和技巧进行总结，以便于朋友们的学习和参考。**

## 反序列化审计实战

反序列化漏洞在Python代码审计中属于常见高危漏洞之一，它的危害性根据执行环境略有不同，本地和远程分别为7.2和10的评分。通过评分也可得知漏洞危害是显而易见。那么咱们应该如何发现这个漏洞？关于发现此种漏洞要从反序列化的模块说起，Python的反序列化模块主要为pickle、cPickle、yaml等等。有关反序列化漏洞问题在多年前就被人们所发现，目前所看到的大多数反序列化漏洞是由于应用调用了存在问题的反序列化模块。那么咱们抓住寻找反序列化模块则有可能会发现反序列化漏洞。

### dask 命令执行漏洞（CNVD-2019-16789）

关于这个漏洞是笔者在2019年审计anaconda环境模块时候发现，提交CNVD通过验证，虽然是本地触发漏洞，但绝对是关于反序列化漏洞很好的案例，漏洞利用yaml模块问题进行反序列化。

 **漏洞分析**

漏洞影响的版本 1.1.4
，漏洞出现于dask模块中config.py文件，第139行。源于程序通过coolect_yaml方法中使用了yaml所导致的问题，方法用途从yaml文件收集配置。

![图片2.png](https://image.3001.net/images/20200328/1585377202_5e7eefb26a16e.png!small)

其中第148行会判断是否为目录，传入文件就能继续执行。漏洞触发在第168行，使用了yaml.load执行了反序列化。

![图片3.png](https://image.3001.net/images/20200328/1585377212_5e7eefbc5899b.png!small)

到此咱们通过POC触发存在反序列化的方法，即可造成代码执行问题。

 **漏洞POC**

漏洞验证截图：

![图片1.png](https://image.3001.net/images/20200328/1585377227_5e7eefcb05353.png!small)

 **修复方法**

yaml
在对于反序列化问题上，已经提供了安全反序列化的解决方法，程序使用yaml.safe_load可以进行安全的反序列化。咱们对于审计问题的修复建议根据实际情况使用。

### NumPy 命令执行漏洞（CVE-2019-6446）

在NumPy
1.16.0版本之前存在反序列化命令执行漏洞，用户加载恶意的数据源造成代码执行。按照惯例在讲这个反序列化之前要说明Python的pickle的反序列化原理和栈指令。但不是本篇重点，故暂不讨论。

 **漏洞分析**

咱们直接从代码层说起，漏洞的入口，lib/npyio.py
第288行附近。在这里存在使用反序列化模块的方法，并且allow_pickle值为True。allow_pickle 允许使用 Python pickles
保存对象数组，Python 中的 pickle 用于在保存到磁盘文件或从磁盘文件读取之前，对对象进行序列化和反序列化。通俗讲是个开关，并默认开启。

![图片4.png](https://image.3001.net/images/20200328/1585377250_5e7eefe278403.png!small)

漏洞触发位置，位置在lib/npyio.py，第418行。这里有反序列化加载的方法。笔者将一些代码省略，直观看重点。默认格式要求ZIP文件前缀PK\x03\x04后缀PK\x05\x06，如果不满足默认的格式，则会执行pickle.load()反序列化方法。

到此执行流程为 NumPy.lib.npyio.py:load()=>pickle.py:load()。

    
    
    try:
        # Code to distinguish from NumPy binary files and pickles.
        _ZIP_PREFIX = b'PK\x03\x04'
        _ZIP_SUFFIX = b'PK\x05\x06' # empty zip files start with this
        …… 
        if magic.startswith(_ZIP_PREFIX) or magic.startswith(_ZIP_SUFFIX):
        ……
        elif magic == format.MAGIC_PREFIX:
        ……
        else:
            # Try a pickle
            if not allow_pickle:
                raise ValueError("Cannot load file containing pickled data "
                                 "when allow_pickle=False")
            try:
                return pickle.load(fid, **pickle_kwargs)
            except Exception:
                raise IOError(
                    "Failed to interpret file %s as a pickle" % repr(file))
    finally:
         ……
    

**漏洞POC**

综上所述，编写POC如下：

    
    
    from numpy.lib import npyio
    from numpy import __version__
    print(__version__)
    import os
    import pickle
    class Test(object):
        def __init__(self):
            self.a = 1
        def __reduce__(self):
            return (os.system,('whoami',))
    tmpdaa = Test()
    with open("test-file.pickle",'wb') as f:
        pickle.dump(tmpdaa,f)
    npyio.load("test-file.pickle")
    

测试结果如图：

![图片6.png](https://image.3001.net/images/20200328/1585377263_5e7eefef7bf01.png!small)

## 命令执行审计实战

在Python模块中命令执行漏洞同样较为常见、危害较大。在审计命令执行时，大多时候程序可能会在满足特定条件下才能执行命令，也可能需要在不同的系统中才会执行命令，所以需要关注代码逻辑和某些特性。

### numexpr 命令执行漏洞(CNVD-2019-17298)

Numexpr是机器学习模块NumPy的一个加速包，主要用于提高NumPy的性能。

 **漏洞分析**

在该模块/numexpr/cpuinfo.py 第37行，存在执行命令的方法。

![图片7.png](https://image.3001.net/images/20200328/1585377273_5e7eeff9500ae.png!small)

getoutput
就是存在问题的方法，通过逻辑在.popen中进行命令执行，但是由于os.WIFEXITED(status)和os.WEXITSTATUS(status)只在linux下支持所以在windows下面执行会报错。linux
下当status
为全局变量并且赋值为0的时候，os.WIFEXITED(status)结果为True,os.WEXITSTATUS(status)结果为0。根据代码逻辑：if
os.WIFEXITED(status) and os.WEXITSTATUS(status) in
successful_status:所以successful_status =(True,0)，并通过形参传入，最终导致命令执行问题。

 **漏洞POC**

漏洞POC和执行结果：

![图片8.png](https://image.3001.net/images/20200328/1585377284_5e7ef004d39e6.png!small)

### dotenv 命令执行漏洞(CNVD-2019-17299)

dotenv是一个使Node.js从文件中加载环境变量的库。

 **漏洞分析**

漏洞存在于dotenv
0.10.1版本中的main.py文件之中，第317行，可见该方法形参传入命令和环境变量。但是由于未对可用命令进行过滤导致任意命令执行问题。

![图片9.png](https://image.3001.net/images/20200328/1585377294_5e7ef00eae94f.png!small)

 **漏洞POC**

漏洞POC和执行结果：

![图片10.png](https://image.3001.net/images/20200328/1585377304_5e7ef018c4562.png!small)

## 总结

通过以上案例和总结，相信咱们能够进一步提高Python审计的功力。这些漏洞在Python审计中比较典型，如果在文章中哪里存在疏忽，盼斧正。

 ***本文作者：米怀特，转载请注明来自FreeBuf.COM**

