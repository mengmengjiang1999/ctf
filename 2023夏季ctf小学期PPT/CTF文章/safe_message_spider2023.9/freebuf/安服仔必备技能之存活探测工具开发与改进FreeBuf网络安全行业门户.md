# 一、背景

前些阵子客户有个需求是搞个图形化的工具，功能是在信息收集阶段之后能够批量导入获取到的url然后进行扫描，获取页面状态以及大小再在工具上显示页面，其实就是觉得有些端口扫描和目录扫描工具只能显示url以及状态码，所以想尝试做个联动，
工具扫描之后的结果可以直接导入到里面，然后可以在工具里面检测是否存活还是误报，然后显示页面，这样遇到大规模的资产扫描的时候不用从表格一个个的复制粘贴访问网站，简单易懂，了解完需求就开搞！

# 二、实现过程

##

### 2.1前期准备

开搞之前先构思下思路，分成几个部分去实现这个工具？

1、语言选择：万物皆可py。

2、数据获取：如何获取到我们想要扫描的url，初步决定直接读取txt就行了，这个就很好解决了，表格获取同理，我懒得写，都是差不多的原理。

3、url状态获取：获取url的状态码及大小，状态码好说，直接用status_code就行了，大小的话去看了下别人的帖子，发现他们实现的思路跟我的不一样，我就直接获取的页面数据，然后len一下，这样后续如果遇到相同资产的无法访问能够比较有效的去判定是否为误报并且筛选出来。

4、页面显示：怎么通过url显示页面，挑了很多种方式，后面还是选择用cefpython3，然后窗口嵌套窗口，嵌套的时候就遇到了挺多坑的。

ok，思路构思差不多了，开始写脚本！

### 2.2代码实现

### 面板

面板这块不用太多介绍，用的是Tkinter和Ttkbootstrap，Tkinter是Python标准GUI库，从本质上来说，它是对TCL/TK工具包的一种Python接口封装。Tkinter是
Python自带的标准库，因此无须另行安装，它支持跨平台运行，不仅可以在Windows 平台上运行，还支持在 Linux 和 Mac 平台上运行。

Ttkbootstrap是一个基于 Tkinter 的界面美化库，使用这个工具可以开发出类似前端 Bootstrap 风格的 Tkinter
桌面程序。一般的图形化工具用Tkinter就够用了，布局的话也不会很复杂，如果铁子们用过Java写过图形化工具的话用这个简直像回老家，

    
    
    # -*- coding: utf-8 -*-    import requests
    import tkinter as tk
    import ttkbootstrap as ttk
    from tkinter import filedialog, END, scrolledtext
    from cefpython3 import cefpython as cef
    import platform
    import ctypes
    import certifi
    import cryptography
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36','Connection': 'close'}
    
    window = tk.Tk()
    window.title("Ax_url_interface")
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    place_x, place_y = 0, 0
    window.geometry(f'{width}x{height}+{place_x}+{place_y}')
    # window.resizable(0, 0)
    
    notebook = ttk.Notebook(window,bootstyle="info")
    frameOne = ttk.Frame(window)
    #子窗口
    u32=ctypes.windll.user32
    WINDOWS = (platform.system() == "Windows")
    LINUX = (platform.system() == "Linux")
    MAC = (platform.system() == "Darwin")
    # Fix for PyCharm hints warnings
    WindowUtils = cef.WindowUtils()
    cef.Initialize() #init
    
    menubar = ttk.Menu(window)
    exitmenu = ttk.Menu(menubar,tearoff=0)
    menubar.add_cascade(label='start',menu=exitmenu)
    # exitmenu.add_command(label='开始扫描',command=window.destroy)
    exitmenu.add_command(label='导入文件',command=import_file)
    exitmenu.add_command(label='开始扫描',command=start_url)
    window.config(menu=menubar)
    group1 = ttk.LabelFrame(frameOne, text="url探测",bootstyle="info")
    group1.grid(row=0,column=0,padx=10, pady=10)
    notebook.add(frameOne, text='url探测')
    fofa_yf = tk.StringVar(value="http://www.baidu.com")
    
    text3 = scrolledtext.ScrolledText(group1,width=60, height=48)
    text3.grid(row=1, columnspan=3, padx=10, pady=10)
    text1 = ttk.Entry(group1, bootstyle="success", width=48, textvariable=fofa_yf)
    text1.grid(row=0, column=0, padx=5, pady=5)
    button1 = ttk.Button(group1, text="查看页面",command=view_pages, width=8, bootstyle="info")
    button1.grid(row=0, column=2, padx=5, pady=5)
    group2 = ttk.LabelFrame(frameOne, text="页面",bootstyle="info")
    group2.grid(row=0,column=1,padx=10, pady=10)
    text5 = scrolledtext.ScrolledText(group2, width=190, height=50)
    text5.insert(END,r"""页面展示区""")
    text5.config(state='disabled')
    text5.grid(row=0, column=0, padx=10, pady=10)
    
    notebook.grid(padx=10, pady=10)
    window.mainloop()

主要排版的话用左右排版就行了，左边导入以及输出结果，右边显示页面，这样也比较清晰简洁，主打一个方便开发，节约开发成本（毕竟只是小需求，还不是有得搞的项目），整体就像是现在这样，不过还没办法导入文件，对url进行探测等。

![1686124392_648037682f2a8aa88d9f9.png!small?1686124392502](https://image.3001.net/images/20230607/1686124392_648037682f2a8aa88d9f9.png!small?1686124392502)

### 导入文件

这块就比较简单了，单纯的读取文件，然后循环就行了，这块的一个进阶方式是监听各类工具的扫描日志，这样能够一边扫一边在这边做二次检测并且显示页面，不想太复杂就搞个死循环，然后每次循环都休眠1秒之后再获取文档里面的数据，然后再进行一次探测就行了，不过最好能多做一步去重，因为多次对一个站点发起请求的话，容易被发现。

    
    
    def import_file():  
    global filepath  
    filepath = filedialog.askopenfilename()  
    filetype = [".txt"]  # 规定读取的文件类型  
    if str(filepath)[-4:] in filetype:  
    text3.insert(END, chars='导入文件为：'+filepath+'\n')  
    text3.insert(END, chars='------------------------------------------------------------------------------------\n')  
    text3.see(END)  
    else:  
    text3.insert(END, chars='请导入txt文件！！！！\n')  
    text3.insert(END, chars='------------------------------------------------------------------------------------\n')  
    text3.see(END)

### 探测存活

查看页面状态码这里用的是Requests，这个应该搞过工具或者爬虫的大佬都不会陌生，很常用的一个模块，这里主要是用来探测状态码以及长度。

    
    
    def start_url():  
    Note = open(filepath, mode='r', encoding='utf-8')  
    requests.packages.urllib3.disable_warnings()  
    for line in Note:  
    try:  
    code = requests.get(line, headers=headers,verify=False,timeout=3)  
    data_line = line.strip("\n")  # 去除首尾换行符，并按空格划分  
    text3.insert(END, chars=data_line + '\n'+'Content Length：'+str(len(code.content))+'\n'+'状态码：'+str(code.status_code)+'\n')  
    #上面的代码可以多加一句代码获取页面的js数据，尝试获取js中的code作为状态码或者当相同长度以及状态码的数据超过多少条的时候，就跳过当前扫描，并把之前的相同的删除  
    text3.insert(END,chars='------------------------------------------------------------------------------------\n')  
    text3.see(END)  
    except:  
    continue

有一个很奇怪的点就是明明扫描器扫描的时候显示的是200，但是实际上去访问的时候他还是显示的404或者其他的情况，还有一个就是类似于目录扫描的工具在扫描的时候容易出现大规模的误报，状态码全为200或403且content长度都是一样的，这种基本上就是误报没错了，出现这种情况的原因是，部分工具直接读取的数据包中的Content-Length，但是有时候这个Content-Length是没有数据的或者是访问过去无法访问，所以这里用了个笨办法就是我重新去请求一次这个页面并且直接计算页面返回数据的大小并且当相同长度以及状态码的数据超过多少条的时候，就跳过当前扫描，这样在减少了部分的误报，效果还是满可以的，这里尝试一组扫描出来的目录误报进行二次扫描，这个是原始的扫描数据：

![1686124395_6480376b9cdb70cdec590.png!small?1686124396092](https://image.3001.net/images/20230607/1686124395_6480376b9cdb70cdec590.png!small?1686124396092)

扫描后可以看到这个其实效果还是蛮不错的，基本上都能检测出来不是真的状态码200，然后可以根据页面数据相同这块做个针对性的改进，就是对比页面数据，相同的话删掉就好了，具体的筛选误报的方式各位见仁见智，不局限于这种，也可以多种方式合起来用，效果没准更好。

![1686124829_6480391dd3316be59f222.png!small?1686124830545](https://image.3001.net/images/20230607/1686124829_6480391dd3316be59f222.png!small?1686124830545)

### 子窗口

本来是想通过PyQt5来打开子窗口并且显示页面的，但是不知道为啥搞不了，是我太菜了，后面只能换成cefpython3，效果出奇的好，并且打开多了也不会卡，这才是关键点，不像有一个版本他打开一个页面之后再次打开另外一个页面就开始卡住了，就是在页面展示位置的时候一定要定位好，并且嵌套在函数里面，不要一运行就有个小窗口存在，不然当你移动工具父窗口的时候，子窗口会找不到父窗口位置，这样就会卡住。

    
    
    class Browser(tk.Frame):
        class LoadHandler(object):
            def __init__(self, browser):
                self.browser = browser
            def OnBeforePopup(self,target_url,**a):
                res = self.browser.NewWindow(target_url)
                if res == "break":
                    return True
        class FocusHandler(object):
            "From cefpython3.example.tkinter_"
            def __init__(self, browser_frame):
                self.browser_frame = browser_frame
            def OnSetFocus(self, source, **_):
                return False
            def OnGotFocus(self, **_):
                """Fix CEF focus issues (#255). Call browser frame's focus_set
                   to get rid of type cursor in url entry widget."""
                self.browser_frame.focus_set()
        def __init__(self,*a,url="",**b):
            super().__init__(*a,**b)
            #create browser
            window_info = cef.WindowInfo()
            rect = [0, 0, self.winfo_width(), self.winfo_height()]
            window_info.SetAsChild(self.get_window_handle(), rect)
            if not url:
                url="https://www.baidu.com/"
            self.browser = cef.CreateBrowserSync(window_info,url=url)
            assert self.browser
            self.browser.SetClientHandler(self.LoadHandler(self))
            self.browser.SetClientHandler(self.FocusHandler(self))
            #fit frame
            self.bind("<Configure>", self._configure)
        def _configure(self, event):
            res=self.event_generate("<<Configure>>")
            if res=="break":
                return
            width = event.width
            height = event.height
            if WINDOWS:
                WindowUtils.OnSize(self.winfo_id(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()
        def NewWindow(self,url):
            self.load(url)
            return "break"
        def loadurl(self,url):
            self.browser.StopLoad()
            self.browser.LoadUrl(url)
        def geturl(self):
            return self.browser.GetUrl()
        def reload(self):
            self.browser.Reload()
        def get_window_handle(self):
            "From cef"
            if self.winfo_id() > 0:
                return self.winfo_id()
            elif MAC:
                # On Mac window id is an invalid negative value (Issue #308).
                # This is kind of a dirty hack to get window handle using
                # PyObjC package. If you change structure of windows then you
                # need to do modifications here as well.
                # noinspection PyUnresolvedReferences
                from AppKit import NSApp
                # noinspection PyUnresolvedReferences
                import objc
                # Sometimes there is more than one window, when application
                # didn't close cleanly last time Python displays an NSAlert
                # window asking whether to Reopen that window.
                # noinspection PyUnresolvedReferences
                return objc.pyobjc_id(NSApp.windows()[-1].contentView())
            else:
                raise Exception("Couldn't obtain window handle")
    def maincefloop(n=200):
        cef.MessageLoopWork()
        tk._default_root.after(n, maincefloop,n)
    def bye():
        cef.Shutdown()
    def view_pages():
        from tkinter import ttk
        def makenew(url):
            b = Browser(note, url=url)
            note.add(b, text=url.replace("https://", "").replace("http://", "").replace("blob://", "")[:25])
            note.select(note.index("end") - 1)
            b.NewWindow = lambda url: makenew(url) or "break"
    
        def go():
            b_back = u32.GetParent(text5.winfo_id())
            a_back = u32.GetParent(root.winfo_id())
            u32.SetParent(a_back, text5.winfo_id())
        url = text1.get()
        root = tk.Toplevel()
        root.title("页面展示")
        width, height = 1325, 825
        place_x, place_y = 0, 0
        root.geometry(f'{width}x{height}+{place_x}+{place_y}')
        note = ttk.Notebook(root)
        note.pack(expand=1, fill="both")
        makenew(url)
        maincefloop()
        text5.after(1, go)
        text5.mainloop()
        bye()

### 完整代码

    
    
    # -*- coding: utf-8 -*-    import requests
    import tkinter as tk
    import ttkbootstrap as ttk
    from tkinter import filedialog, END, scrolledtext
    from cefpython3 import cefpython as cef
    import platform
    import ctypes
    import certifi
    import cryptography
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36','Connection': 'close'}
    
    window = tk.Tk()
    window.title("Ax_url_interface")
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    place_x, place_y = 0, 0
    window.geometry(f'{width}x{height}+{place_x}+{place_y}')
    # window.resizable(0, 0)
    
    notebook = ttk.Notebook(window,bootstyle="info")
    frameOne = ttk.Frame(window)
    #子窗口
    u32=ctypes.windll.user32
    WINDOWS = (platform.system() == "Windows")
    LINUX = (platform.system() == "Linux")
    MAC = (platform.system() == "Darwin")
    # Fix for PyCharm hints warnings
    WindowUtils = cef.WindowUtils()
    cef.Initialize() #init
    
    class Browser(tk.Frame):
        class LoadHandler(object):
            def __init__(self, browser):
                self.browser = browser
            def OnBeforePopup(self,target_url,**a):
                res = self.browser.NewWindow(target_url)
                if res == "break":
                    return True
        class FocusHandler(object):
            "From cefpython3.example.tkinter_"
            def __init__(self, browser_frame):
                self.browser_frame = browser_frame
            def OnSetFocus(self, source, **_):
                return False
            def OnGotFocus(self, **_):
                """Fix CEF focus issues (#255). Call browser frame's focus_set
                   to get rid of type cursor in url entry widget."""
                self.browser_frame.focus_set()
        def __init__(self,*a,url="",**b):
            super().__init__(*a,**b)
            #create browser
            window_info = cef.WindowInfo()
            rect = [0, 0, self.winfo_width(), self.winfo_height()]
            window_info.SetAsChild(self.get_window_handle(), rect)
            if not url:
                url="https://www.baidu.com/"
            self.browser = cef.CreateBrowserSync(window_info,url=url)
            assert self.browser
            self.browser.SetClientHandler(self.LoadHandler(self))
            self.browser.SetClientHandler(self.FocusHandler(self))
            #fit frame
            self.bind("<Configure>", self._configure)
        def _configure(self, event):
            res=self.event_generate("<<Configure>>")
            if res=="break":
                return
            width = event.width
            height = event.height
            if WINDOWS:
                WindowUtils.OnSize(self.winfo_id(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()
        def NewWindow(self,url):
            self.load(url)
            return "break"
        def loadurl(self,url):
            self.browser.StopLoad()
            self.browser.LoadUrl(url)
        def geturl(self):
            return self.browser.GetUrl()
        def reload(self):
            self.browser.Reload()
        def get_window_handle(self):
            "From cef"
            if self.winfo_id() > 0:
                return self.winfo_id()
            elif MAC:
                # On Mac window id is an invalid negative value (Issue #308).
                # This is kind of a dirty hack to get window handle using
                # PyObjC package. If you change structure of windows then you
                # need to do modifications here as well.
                # noinspection PyUnresolvedReferences
                from AppKit import NSApp
                # noinspection PyUnresolvedReferences
                import objc
                # Sometimes there is more than one window, when application
                # didn't close cleanly last time Python displays an NSAlert
                # window asking whether to Reopen that window.
                # noinspection PyUnresolvedReferences
                return objc.pyobjc_id(NSApp.windows()[-1].contentView())
            else:
                raise Exception("Couldn't obtain window handle")
    def maincefloop(n=200):
        cef.MessageLoopWork()
        tk._default_root.after(n, maincefloop,n)
    def bye():
        cef.Shutdown()
    
    
    
    def import_file():
        global filepath
        filepath = filedialog.askopenfilename()
        filetype = [".txt"]  # 规定读取的文件类型
        if str(filepath)[-4:] in filetype:
            text3.insert(END, chars='导入文件为：'+filepath+'\n')
            text3.insert(END, chars='------------------------------------------------------------------------------------\n')
            text3.see(END)
        else:
            text3.insert(END, chars='请导入txt文件！！！！\n')
            text3.insert(END, chars='------------------------------------------------------------------------------------\n')
            text3.see(END)
    
    def start_url():
        Note = open(filepath, mode='r', encoding='utf-8')
        requests.packages.urllib3.disable_warnings()
        for line in Note:
            try:
                code = requests.get(line, headers=headers,verify=False,timeout=3)
                data_line = line.strip("\n")  # 去除首尾换行符，并按空格划分
                text3.insert(END, chars=data_line + '\n'+'Content Length：'+str(len(code.content))+'\n'+'状态码：'+str(code.status_code)+'\n')
                #上面的代码可以多加一句代码获取页面的js数据，尝试获取js中的code作为状态码或者当相同长度以及状态码的数据超过多少条的时候，就跳过当前扫描，并把之前的相同的删除
                #
                text3.insert(END,chars='------------------------------------------------------------------------------------\n')
                text3.see(END)
            except:
                continue
    def view_pages():
        from tkinter import ttk
        def makenew(url):
            b = Browser(note, url=url)
            note.add(b, text=url.replace("https://", "").replace("http://", "").replace("blob://", "")[:25])
            note.select(note.index("end") - 1)
            b.NewWindow = lambda url: makenew(url) or "break"
    
        def go():
            b_back = u32.GetParent(text5.winfo_id())
            a_back = u32.GetParent(root.winfo_id())
            u32.SetParent(a_back, text5.winfo_id())
        url = text1.get()
        root = tk.Toplevel()
        root.title("页面展示")
        width, height = 1325, 825
        place_x, place_y = 0, 0
        root.geometry(f'{width}x{height}+{place_x}+{place_y}')
        note = ttk.Notebook(root)
        note.pack(expand=1, fill="both")
        makenew(url)
        maincefloop()
        text5.after(1, go)
        text5.mainloop()
        bye()
    menubar = ttk.Menu(window)
    exitmenu = ttk.Menu(menubar,tearoff=0)
    menubar.add_cascade(label='start',menu=exitmenu)
    # exitmenu.add_command(label='开始扫描',command=window.destroy)
    exitmenu.add_command(label='导入文件',command=import_file)
    exitmenu.add_command(label='开始扫描',command=start_url)
    window.config(menu=menubar)
    group1 = ttk.LabelFrame(frameOne, text="url探测",bootstyle="info")
    group1.grid(row=0,column=0,padx=10, pady=10)
    notebook.add(frameOne, text='url探测')
    fofa_yf = tk.StringVar(value="http://www.baidu.com")
    
    text3 = scrolledtext.ScrolledText(group1,width=60, height=48)
    text3.grid(row=1, columnspan=3, padx=10, pady=10)
    text1 = ttk.Entry(group1, bootstyle="success", width=48, textvariable=fofa_yf)
    text1.grid(row=0, column=0, padx=5, pady=5)
    button1 = ttk.Button(group1, text="查看页面",command=view_pages, width=8, bootstyle="info")
    button1.grid(row=0, column=2, padx=5, pady=5)
    group2 = ttk.LabelFrame(frameOne, text="页面",bootstyle="info")
    group2.grid(row=0,column=1,padx=10, pady=10)
    text5 = scrolledtext.ScrolledText(group2, width=190, height=50)
    text5.insert(END,r"""页面展示区""")
    text5.config(state='disabled')
    text5.grid(row=0, column=0, padx=10, pady=10)
    
    notebook.grid(padx=10, pady=10)
    window.mainloop()
    

最终呈现的就是这样的

![1686124477_648037bd14807422f41f6.png!small?1686124477703](https://image.3001.net/images/20230607/1686124477_648037bd14807422f41f6.png!small?1686124477703)

# 三、总结&改进

整个小工具下来其实并没有什么太难的点，包括面板，窗口嵌套，页面显示啥的并不是很难，基本上看下就知道该怎么搞了，在探测存活这块在整的时候刚好想到之前目录扫描或者获取js文件里面的链接时候经常会有那些误报或者一些无用数据引起的误报，大部分扫描结果出现状态码为200且大小相同的情况是因为自定义报错页面，虽然返回的数据包状态码为200，但是页面数据显示的是404或者是其他状态码。

针对这个问题做了改进，可以设置个计数器，当出现一定数量的相同状态码和大小的扫描结果时，将几个扫描结果的页面body数据进行对比，如果相同保留一个就行了，这样也可以减少大部分的误报，也可以不设置计数器，直接匹配，但是这样消耗的资源有点多，所以还是计数会比较好点。

