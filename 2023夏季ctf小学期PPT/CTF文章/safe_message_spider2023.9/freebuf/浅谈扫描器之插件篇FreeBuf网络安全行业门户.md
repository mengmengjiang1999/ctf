**在我们试图构建漏扫系统的时候，调整好插件的配置和格式，能更有效地帮助我们进行漏洞探测，以及提升对bug的进行fuzz的高效性。**  

在本文中，我们将简单谈谈插件相关的内容。下面的示例代码依旧会沿用python，但求行文精炼不赘言。

### 插件的基本格式

  * 入口函数

    
    
    def run():
        print 'I am the bone of my sword'
    

运行这类插件时，加载插件的入口函数run，就可以直接运行插件。

  * 类 + 入口函数

    
    
    class BaseVerify:
    
        def __init__(self, url):
            self.url = url
        
        def run(self):
            print 'I am the bone of my sword'
    

对于这种插件，在我们获取到漏洞库文件路径后，需要对服务类型进行匹配，最后再进行插件调用。
此后，我们会获得BaseVerify类的实例，再引用里面的入口函数。

调用方式：

    
    
    test = BaseVerify('http://www.baidu.com')
    test.run()
    

  * 入口函数 + 验证函数

    
    
    def assign(service, arg):
        if service != "wordpress":
            return
        else:
            r = urlparse.urlparse(arg)
            return True, r.netloc
            
    def audit(arg):
        print 'I am the bone of my sword'
            
    

这里也可以在类中引入函数，不过此处关键点在于，同时也使用了验证函数。

这样做的好处在于，即使不做插件目录分类，也能进行精准扫描，不至于在验证漏洞时处耗时过多。

不过顺便提一句，即使只运行了验证service类型的代码，在加载大量插件的情况下，也是会消耗一定的资源的。

调用方式(仅做参考)：

    
    
    try:
        audit( assign('www', 'http://www.baidu.com')[1] )
    except:
        pass
    

  * 关于插件注释

在每个文件中，建议通过类属性或者直接头部注释，对每个插件进行细节标识。
不然的话，他人在复现和修改的时候，很难对代码量较大的内容进行阅读调整。当然，对于某些故意加密的插件，那就另当别论了。

### 插件的加载

  * _import_

    
    
    plugin_path = 'plugin_dir.plugin_name'
    try:
        plugin = __import__(plugin_path, fromlist=[plugin_path])
        test = getattr(plugin,'audit')
        test('http://www.baidu.com')
    except Exception,e:
        print e
    
    

这里在获取某个插件的路径后，可转换为__import__可识别的路径格式，然后再对其入口函数audit进行引用。

  * importlib

    
    
    from importlib import import_module
    plugin_path = 'plugin_dir.plugin_name'
    split_dot = plugin_path.rindex('.')
    module, name = plugin_path[:split_dot], plugin_path[split_dot+1:]
    mod = import_module(module)
    try:
        test = getattr(mod, name)
        test.audit('http://www.baidu.com')
    except:
        pass
    
    

注意，这里的plugin_path如果不含'.'的话，可用下面的形式：

    
    
    from importlib import import_module
    plugin_path = 'plugin_name'
    test = import_module(plugin_path)
    test.audit('http://www.baidu.com')
    
    

  * import

    
    
    import sys
    sys.path.append('plugin_dir/')
    #加入系统路径plugin_dir
    import plugin_name
    plugin_name.audit('http://www.baidu.com')
    

  * imp

    
    
    import imp
    #这里需要正常路径名
    test = imp.load_source('audit', 'plugin_dir/plugin_name.py')
    test.audit('http://www.baidu.com')
    
    

  * 关于导入细节

笔者还见过某框架，除了导入必要的核心库文件以外，还把所有分类插件里的验证、运行等函数，也在主文件头部一股脑导入的。

也就是说，在每次运行框架之前，就算只是-v看版本，也会预载入所有内容。

而在某些框架脚本，在每次运行前会自动下载一个巨大的封装库（作者diy的），而不是把它放在requirement文件里。

也不是说这样一定不好，不过个人窃以为，如果想要尽可能优化框架的效率，还是不太推荐大家这么做。

### 插件的存储

  * 临时加载

在一次性加载插件不算多的时候，我们是可以这么做的，也不会太影响效率。 比如metasploit就可以选择是否启用postgresql数据库。
如果插件都放在一个目录下，进行文件遍历即可，大概可以这样写：

    
    
    vuln_dir = 'plugin_dir/*'
    vuln_paths = [f.replace('/','.') for f in glob.glob(vuln_dir)]
    for vuln_path in vuln_paths:
        #vuln_path == 'plugin_dir.plugin_name'
        #下面省略
        ...
        ...
    

  * 离线插件入库

另外还有不少框架，是直接用数据库或者json文件存储了插件相关信息。在我们需要的时候，再查询导入储存的插件路径，进而对相应的插件进行调用。

当然，这样需要我们每次手动或调用update脚本，去现更新这些库。

  * 在线核验下发

如果想要再自动化一点，我们可以参考下bugscan、antoor、tangscan等社区级别的漏洞利用框架，对于插件下发的法子。

譬如在贡献者上传poc，并填写好相关验证信息后，后台会有工作人员或者自动化检测脚本，检测该poc是否合乎官方规定的语法格式。
如果没有发现问题，脚本会生成基础信息然后入库，待做好加密打码等工作后【非必要步骤】，再供离线的完整框架或者client节点爬取更新【如有出入，当我扯淡】。

### 结果的聚合

  * 分级过滤

一般在汇总数据报告时，可能会出现有的脚本可以确认是漏洞，有的却只是疑似bug，或者只是敏感URL。

混在一起存储也不是不行，不过更好的法子是通过分级，使用单独的函数上报master，最后再进行分储和输出。

  * 混合存储

在整合网上搜集来的插件时，由于各结果的返回格式不是很好统一，有的整合型框架为了兼容会直接简单处理下，就糅合在一起存储和输出了。
其实这也没啥，只要入库的时候，将特殊字符等问题处理好，做好插件漏洞的信息粗放分类标注，那就基本OK了。

  * 单体输出

某些作者单独开发的框架，是直接省略了存储这一环节的，或者是提供了选项，默认不开启的。
这时候，插件验证如果成功，会直接把信息反馈输出到命令行里。如果在验证单体漏洞或者单个目标的时候，这样做还是比较有效率的。

### 结语

上面列举的案例分析代码，部分来自Github上搜到的漏洞poc框架以及爬虫框架，部分来自于笔者自己的储备，这里再次感谢各位coder的开源。

另外，上一篇本系列的文章也贴出来，大家可以对比参照下。

[浅谈扫描器之加速篇](http://www.freebuf.com/column/182866.html)

欢迎关注专栏，后面我会发点私货的XD。

