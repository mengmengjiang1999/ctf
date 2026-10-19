**Cerbero
Suite是为x86/x64设计的一款交互式反汇编工具。最初的目的是为了让我们的用户能够检查内存转储中的代码以及shellcode。如今，市面上已有非常先进的反汇编工具，如IDA和Ghidra，在我看来尝试模仿其中的一种工具是没有意义的。这也是我设计该反汇编工具的原因，同时我也考虑了客户如何使用Cerbero
Suite的问题。**

Cerbero
Suite被大量作为文件初始分类的工具使用。我依然记得使用W32Dasm的美好时光，并从中获取了很大的灵感。当然，W32Dasm已无法应对越来越复杂的情况。这就是为什么在Carbon的设计中，我试图将W32Dasm等工具的即时性与更高级工具的灵活性结合起来的原因。

## 特性介绍

 **Flat 反汇编视图**

Carbon带有一个显示文件中所有指令的Flat 反汇编视图。我不排除将来可能会有图表视图，但它不是我优先考虑的事情。

![1.png](https://image.3001.net/images/20190702/1562023017_5d1a9469c3332.png!small)

 **递归反汇编**

递归反汇编程序是解决代码被数据中断的情况所必需的。Carbon将尽可能的在较短时间内完成disassemble，并同时进行基本的分析工作。

 **速度**

Carbon是多线程的，可以非常快速地处理大型的文件。这对于文件的初始分类非常有用。

![2.png](https://image.3001.net/images/20190702/1562023034_5d1a947ada327.png!small)

以上是大约十分钟内对60 MB chrome DLL执行的分析。这是在虚拟机中运行的。未来的挑战将是保持速度，同时增加更多的分析段落。

 **x86/x64 支持**

Carbon同时支持x86和x64代码。将来会支持更多架构。

实际上，Carbon的设计允许在相同的反汇编视图中混合架构。

 **不受限的数据库**

一个项目在Carbon中可以包含无限个Carbon数据库。这意味着如果你正在分析包含10个可执行文件的Zip文件，那么这些文件中的每一个都可以拥有自己的数据库。

不仅如此：单个文件也可以有多个数据库，只需单击Carbon工具栏按钮或按“Ctrl+Alt+C”即可添加新的Carbon数据库。

![3.png](https://image.3001.net/images/20190702/1562023055_5d1a948f7ca25.png!small)

如果你对分析不满意，那么你可以通过右键单击相关的摘要条目或选择它并按“Del”轻松删除它。

 **脚本**

你只需几行Python代码就可以加载和disassemble一个文件。

    
    
    s = createContainerFromFile(a)
    obj = PEObject()
    obj.Load(s)
    
    c = Carbon()
    c.setObject(obj, True)
    if c.createDB(dbname) != CARBON_OK:
        print("error: couldn't create DB")
        return False
    if c.load() != CARBON_OK:
        print("error: couldn't load file")
        return False
    c.resumeAnalysis()
    # wait for the analysis to finish...

分析完成后，我们可以修改和浏览其内部数据库的各个部分，或者我们可以创建一个视图并显示反汇编：

    
    
    ctx = proContext()
    v = ctx.createView(ProView.Type_Carbon, "test")
    ctx.addView(v, True)
    v.setCarbon(c)

内部数据库使用SQLite，即使不使用SDK也可以轻松浏览和修改它。

 **Python 加载程序**

在很早之前我就决定使用Python编写所有的文件加载程序。虽然这可能会使文件的加载速度稍慢（尽管不明显），但它允许用户自定义加载程序并添加功能，从而提供了极大的灵活性。添加新的文件加载程序也非常简单。

PE文件的整个加载程序大约有350行代码。这是原始文件的加载程序：

    
    
    from Pro.Carbon import *
    
    class RawLoader(CarbonLoader):
    
        def __init__(self):
            super(RawLoader, self).__init__()
            
        def load(self):
            # get parameters
            p = self.carbon().getParameters()
            try:
                arch = int(p.value("arch", str(CarbonType_I_x86)), 16)
            except:
                print("carbon error: invalid arch")
                arch = CarbonType_I_x86
            try:
                base = int(p.value("base", "0"), 16)
            except:
                print("carbon error: invalid base address")
                base = 0
            # load
            db = self.carbon().getDB()
            obj = self.carbon().getObject()
            # add region
            e = caRegion()
            e.def_type_id = arch
            e.flags = caRegion.READ | caRegion.WRITE | caRegion.EXEC
            e.start = base
            e.end = e.start + obj.GetSize()
            e.offset = 0
            db.addRegion(e)
            # don't disassemble automatically
            db.setState(caMain.FINISHED)
            return CARBON_OK
    
    def newRawLoader():
        return RawLoader()

一旦熟悉了SDK，添加新的加载器将会非常的轻松简单。

 **Raw/PE 加载程序**

初始文件的支持是针对PE和raw文件的。

![4.png](https://image.3001.net/images/20190702/1562023108_5d1a94c4086d3.png!small)

例如，这是一些反汇编的shellcode。

 **在内存 PEs 中**

其中一个主要的功能是分析内存中的PE文件。

这是内存中PE的代码：

![5.png](https://image.3001.net/images/20190702/1562023123_5d1a94d339d3a.png!small)

当然，反汇编仅限于未被分页的内存页面，因此可能存在一些空白。

我们对这个功能不是特别了解，后续该功能也将随着即将发布的版本进行相应扩展。

 **交叉引用**

当然，没有一个像样的反汇编程序可以缺少交叉引用这项功能：

![6.png](https://image.3001.net/images/20190702/1562023138_5d1a94e29cca8.png!small)

我们还可以从设置中选择我们想要查看的交叉引用数：

![7.png](https://image.3001.net/images/20190702/1562023152_5d1a94f0eb3a9.png!small)

 **重命名**

我们可以在代码中命名和重命名任何位置或函数（允许重复）。即使ERROR没有指向同一位置，我们也可能有多个带有“jmp ERROR”实例的方法。

![8.png](https://image.3001.net/images/20190702/1562023168_5d1a9500b2081.png!small)

 **生成代码/取消定义**

我们可以通过按“C”将未定义的数据转换为代码，或者相反，按“U”将代码转换为未定义的数据。

在这里，我们向shellcode添加了一个新的Carbon数据库。正如你所看到的，它最初都是未定义的数据：

![9.png](https://image.3001.net/images/20190702/1562023186_5d1a95122e83d.png!small)

在第一个字节按“C”后，我们得到一些初始指令：

![10.png](https://image.3001.net/images/20190702/1562023203_5d1a95231a186.png!small)

但是，正如我们所看到的，突出显示的跳转无效。通过“jmp”之前的“jne”，我们可以看到我们实际上在“jmp”指令之后跳转了一个字节。所以我们要做的是在“jmp”上按“U”，然后在地址0xA的字节上按“C”。

![11.png](https://image.3001.net/images/20190702/1562023218_5d1a95329b2cc.png!small)

之后，在0xA再次按“C”：

![12.png](https://image.3001.net/images/20190702/1562023235_5d1a9543b5591.png!small)

现在，我们就可以正确分析shellcode了。

 **函数**

我们可以在任何我们想要的位置定义和取消定义函数。

![13.png](https://image.3001.net/images/20190702/1562023252_5d1a95547b586.png!small)

 **例外**

已支持x64异常。

![14.png](https://image.3001.net/images/20190702/1562023265_5d1a95613084b.png!small)

 **注释**

添加注释最重要的功能之一。

![15.png](https://image.3001.net/images/20190702/1562023278_5d1a956eea811.png!small)

 **已标记的位置**

你也可以通过按“Alt+M”标记位置或通过“Ctrl+M”跳转到标记的位置。

![16.png](https://image.3001.net/images/20190702/1562023292_5d1a957c341ec.png!small)

 **清单列表**

从“Ctrl+1”到“Ctrl+4”的快捷方式可以为你展示反汇编中的各种列表。

Ctrl+1将显示入口点列表：

![17.png](https://image.3001.net/images/20190702/1562023306_5d1a958a65d85.png!small)

Ctrl+2显示函数列表：

![18.png](https://image.3001.net/images/20190702/1562023324_5d1a959c62a8d.png!small)

Ctrl+3显示导入列表：

![19.png](https://image.3001.net/images/20190702/1562023333_5d1a95a597153.png!small)

Ctrl+4显示导出列表：

![20.png](https://image.3001.net/images/20190702/1562023342_5d1a95ae3461b.png!small)

 **字符串**

可以通过按“Ctrl+5”创建：

![21.png](https://image.3001.net/images/20190702/1562023357_5d1a95bd2a1fd.png!small)

一旦我们跳转到一个字符串，我们就可以检查代码中使用它的位置：

![22.png](https://image.3001.net/images/20190702/1562023370_5d1a95ca87242.png!small)

反汇编本身将尝试识别字符串，并在适当时将它们显示为自生成的注释：

![23.png](https://image.3001.net/images/20190702/1562023388_5d1a95dc6b320.png!small)

 **集成**

我们已经将Carbon很好地融入到了Cerbero Suite的整个逻辑中。Carbon数据库保存在Cerbero
Suite项目中，就像文件分析的任何其他部分一样。

虽然Carbon已经为标记的位置提供了支持，但没有什么可以阻止你使用书签来标记位置并跳回到它们。区别在于标记的位置特定于单个Carbon数据库，而书签可以跨数据库和不同的文件。

 **主题**

一个好的主题同样非常的重要，至少对我而言是这样的。你可以在设置中切换颜色主题。第一个版本包含以下四个主题。

Light：

![24.png](https://image.3001.net/images/20190702/1562023410_5d1a95f2892b3.png!small)

Classic：

![25.png](https://image.3001.net/images/20190702/1562023421_5d1a95fdb524e.png!small)

Iceberg：

![26.png](https://image.3001.net/images/20190702/1562023432_5d1a960891cd0.png!small)

Dasm：

![27.png](https://image.3001.net/images/20190702/1562023442_5d1a9612efed1.png!small)

后续也将添加更多的颜色主体，敬请期待！

 ** *参考来源：[cerbero-blog](https://cerbero-blog.com/?p=1768)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

