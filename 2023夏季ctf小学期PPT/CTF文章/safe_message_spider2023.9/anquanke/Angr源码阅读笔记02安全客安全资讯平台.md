# Angr源码阅读笔记02

阅读量 **314343**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-05 14:30:57

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t017513e9b074aa4f12.jpg)

上一回我们从angr的`__init__.py`文件入手，到解析了`project.py`文件的内容，了解了一个基本的angr项目是怎么一步一步初始化到建立完成开始可以执行操作的，现在我们把目光放回到所有angr项目的基石-CLE类与angr的中间语言VEX-IR语言上，更进一步的理解整个angr系统的工作情况

## 一、一切的基石-CLE

​ angr 中的 CLE 模块用于将二进制文件载入虚拟地址空间，而CLE 最主要的接口就是 loader
类。loader类加载所有的对象并导出一个进程内存的抽象。生成该程序已加载和准备运行的地址空间

​
这里需要注意的是CLE模块本身的代码实现并不在Angr的源码里面，在Angr的源码里面它是已经以一个二进制包的形式调用，它真正的源码实现在另外一个仓库里面：

    
    
    https://github.com/angr/cle
    

​ 里面的README文件里面也介绍了CLE包的基础用法

    
    
    >>> import cle
    >>> ld = cle.Loader("/bin/ls")
    >>> hex(ld.main_object.entry)
    '0x4048d0'
    >>> ld.shared_objects
    {'ld-linux-x86-64.so.2': <ELF Object ld-2.21.so, maps [0x5000000:0x522312f]>,
     'libacl.so.1': <ELF Object libacl.so.1.1.0, maps [0x2000000:0x220829f]>,
     'libattr.so.1': <ELF Object libattr.so.1.1.0, maps [0x4000000:0x4204177]>,
     'libc.so.6': <ELF Object libc-2.21.so, maps [0x3000000:0x33a1a0f]>,
     'libcap.so.2': <ELF Object libcap.so.2.24, maps [0x1000000:0x1203c37]>}
    >>> ld.addr_belongs_to_object(0x5000000)
    <ELF Object ld-2.21.so, maps [0x5000000:0x522312f]>
    >>> libc_main_reloc = ld.main_object.imports['__libc_start_main']
    >>> hex(libc_main_reloc.addr)       # Address of GOT entry for libc_start_main
    '0x61c1c0'
    >>> import pyvex
    >>> some_text_data = ld.memory.load(ld.main_object.entry, 0x100)
    >>> irsb = pyvex.lift(some_text_data, ld.main_object.entry, ld.main_object.arch)
    >>> irsb.pp()
    IRSB {
       t0:Ity_I32 t1:Ity_I32 t2:Ity_I32 t3:Ity_I64 t4:Ity_I64 t5:Ity_I64 t6:Ity_I32 t7:Ity_I64 t8:Ity_I32 t9:Ity_I64 t10:Ity_I64 t11:Ity_I64 t12:Ity_I64 t13:Ity_I64 t14:Ity_I64
    
       15 | ------ IMark(0x4048d0, 2, 0) ------       16 | t5 = 32Uto64(0x00000000)
       17 | PUT(rbp) = t5
       18 | t7 = GET:I64(rbp)
       19 | t6 = 64to32(t7)
       20 | t2 = t6
       21 | t9 = GET:I64(rbp)
       22 | t8 = 64to32(t9)
       23 | t1 = t8
       24 | t0 = Xor32(t2,t1)
       25 | PUT(cc_op) = 0x0000000000000013
       26 | t10 = 32Uto64(t0)
       27 | PUT(cc_dep1) = t10
       28 | PUT(cc_dep2) = 0x0000000000000000
       29 | t11 = 32Uto64(t0)
       30 | PUT(rbp) = t11
       31 | PUT(rip) = 0x00000000004048d2
       32 | ------ IMark(0x4048d2, 3, 0) ------       33 | t12 = GET:I64(rdx)
       34 | PUT(r9) = t12
       35 | PUT(rip) = 0x00000000004048d5
       36 | ------ IMark(0x4048d5, 1, 0) ------       37 | t4 = GET:I64(rsp)
       38 | t3 = LDle:I64(t4)
       39 | t13 = Add64(t4,0x0000000000000008)
       40 | PUT(rsp) = t13
       41 | PUT(rsi) = t3
       42 | PUT(rip) = 0x00000000004048d6
       43 | t14 = GET:I64(rip)
       NEXT: PUT(rip) = t14; Ijk_Boring
    }
    

###  1.1 CLE包的用法

​ 按照Angr官方文档的说法，分析一个没有源码的二进制文件需要克服很多的困难，主要包含以下几种：

  * 如何加载一个二进制文件到一个合适的分析器中
  * 如何将二进制转化为中间表示形式(intermediate representation)
  * 执行分析，可以是： 
    * 对二进制文件局部或整体的静态分析（比如依赖分析，程序切片）
    * 对程序状态空间的符号化探索（比如“我们可以执行这个程序直到我们找到一个溢出吗？”）
    * 上述两种分析在某些程度上的结合（比如“我们只执行程序中对内存写的程序片段来找到一个溢出。”）

​ 而Angr均提供了应对上述挑战的组件，我们的CLE包就是为了解决第一个问题，关于第二个问题我们将在之后的VEX
IR的介绍里面提到。这一章节我们将根据官方文档的视角进行学习

​ CLE
loader（`cle.Loader`）表示整个加载的二进制对象集合，加载并映射到单个内存空间。每个二进制对象都由一个可以处理其文件类型（`cle.Backend`）的加载器后端加载。例如，`cle.ELF`用于加载ELF二进制文件

​ 一般情况下，CLE 会自动选择对应的 backend，也可以自己指定。有的 backend 需要 同时指定架构

名称 | 描述  
---|---  
elf | ELF文件的静态加载器 (基于PyELFTools)  
pe | PE文件静态加载器 (基于PEFile)  
mach-o | Mach-O文件的静态加载器  
cgc | CGC (Cyber Grand Challenge)二进制的静态加载器  
backedcgc | CGC 二进制的静态加载器，允许指定内存和寄存器  
elfcore | ELF 核心转储的静态加载器  
blob | 将文件作为平面镜像加载到内存中  
  
####  1.1.1 加载对象及其地址空间

​ 我们可以通过loader来查看二进制文件加载的共享库，以及执行对加载地址空间相关的基本查询，按照官方文档例如：

    
    
    # All loaded objects
    >>> proj.loader.all_objects
    [    <ELF Object fauxware, maps [0x400000:0x60105f]>,
        <ELF Object libc.so.6, maps [0x1000000:0x13c42bf]>,
        <ELF Object ld-linux-x86-64.so.2, maps [0x2000000:0x22241c7]>,
           <ELFTLSObject Object cle##tls, maps [0x3000000:0x300d010]>,
           <KernelObject Object cle##kernel, maps [0x4000000:0x4008000]>,
           <ExternObject Object cle##externs, maps [0x5000000:0x5008000]>
    
    # This is the "main" object, the one that you directly specified when loading the project
    >>> proj.loader.main_object
    <ELF Object true, maps [0x400000:0x60105f]>
    
    # This is a dictionary mapping from shared object name to object
    >>> proj.loader.shared_objects
    {     'libc.so.6': <ELF Object libc.so.6, maps [0x1000000:0x13c42bf]>
        'ld-linux-x86-64.so.2': <ELF Object ld-linux-x86-64.so.2, maps [0x2000000:0x22241c7]>}
    
    # Here's all the objects that were loaded from ELF files
    # If this were a windows program we'd use all_pe_objects!
    >>> proj.loader.all_elf_objects
    [    <ELF Object true, maps [0x400000:0x60105f]>,
        <ELF Object libc.so.6, maps [0x1000000:0x13c42bf]>,
        <ELF Object ld-linux-x86-64.so.2, maps [0x2000000:0x22241c7]>]
    
    # Here's the "externs object", which we use to provide addresses for unresolved imports and angr internals
    >>> proj.loader.extern_object
    <ExternObject Object cle##externs, maps [0x5000000:0x5008000]>
    
    # This object is used to provide addresses for emulated syscalls
    >>> proj.loader.kernel_object
    <KernelObject Object cle##kernel, maps [0x4000000:0x4008000]>
    
    # Finally, you can to get a reference to an object given an address in it
    >>> proj.loader.find_object_containing(0x400000)
    <ELF Object true, maps [0x400000:0x60105f]>
    

  * `proj.loader.all_objects`：可以查看这个程序加载的所有对象对应内存的加载地址
  * `proj.loader.main_object`：这个可以查看我们项目里选择分析的程序的相应信息，也就是我们自己手动选择加载的程序，例如我们之前测试的程序`test`之类的
  * `proj.loader.shared_objects`：查看二进制文件加载的共享库，以及执行对加载地址空间相关的基本查询
  * `proj.loader.all_elf_objects`：这个是查看所有ELF格式的对象及其加载地址空间，在Windows里面我们就要使用`all_pe_objects`而不是`all_elf_objects`
  * `proj.loader.extern_object`：这个也就是加载所有的`extern`对象及其加载地址空间
  * `proj.loader.kernel_object`：这个就是加载系统内核加载地址空间
  * `proj.loader.find_object_containing(0x400000)`：这个我们可以通过提供地址空间内存返回处于这个内存加载地址空间的对象名称，也就是个反查询的功能

​ 我们可以直接与这些对象进行交互以从中提取元数据：

    
    
    >>> obj = proj.loader.main_object
    
    # The entry point of the object
    >>> obj.entry
    0x400580
    
    >>> obj.min_addr, obj.max_addr
    (0x400000, 0x60105f)
    
    # Retrieve this ELF's segments and sections
    >>> obj.segments
    <Regions: [<ELFSegment offset=0x0, flags=0x5, filesize=0xa74, vaddr=0x400000, memsize=0xa74>,
    <ELFSegment offset=0xe28, flags=0x6, filesize=0x228, vaddr=0x600e28, memsize=0x238>]>
    
     >>> obj.sections
     <Regions: [<Unnamed | offset 0x0, vaddr 0x0, size 0x0>,
                <.interp | offset 0x238, vaddr 0x400238, size 0x1c>,
                <.note.ABI-tag | offset 0x254, vaddr 0x400254, size 0x20>,  
                ...etc
    
    # You can get an individual segment or section by an address it contains:
    >>> obj.find_segment_containing(obj.entry)         
    <ELFSegment offset=0x0, flags=0x5, filesize=0xa74, vaddr=0x400000, memsize=0xa74>
    >>> obj.find_section_containing(obj.entry)
    <.text | offset 0x580, vaddr 0x400580, size 0x338>
    
    # Get the address of the PLT stub for a symbol
    >>> addr = obj.plt['abort']
    >>> addr
    0x400540
    
    >>> obj.reverse_plt[addr]
    'abort'
    
    # Show the prelinked base of the object and the location it was actually mapped into memory by CLE
    >>> obj.linked_base
    0x400000
    >>> obj.mapped_base
    0x400000
    

####  1.1.2 符号和重定位

​
还可以在使用CLE时使用符号，这里的符号是编译程序中的符号的概念，我们这里也可以简单认为就是函数的名称也是一种符号，也就是提供了一种将名称映射到地址的方式

​ 从CLE获取符号的最简单方法是使用`loader.find_symbol`，它接受名称或地址并返回Symbol对象，一个最简单例子就是：

    
    
    >>> malloc = proj.loader.find_symbol('malloc')
    >>> malloc
    <Symbol "malloc" in libc.so.6 at 0x1054400>
    

​
这里我们就通过函数名`malloc`查找到了其对应的共享库和加载地址空间。符号上最有用的属性是其名称，所有者和地址，但符号的“地址”可能不明确。Symbol对象有三种报告其地址的方式：

  * `.rebased_addr`：是它在所有地址空间中的地址。这是打印输出中显示的内容
  * `.linked_addr`：是它相对于二进制的预链接基础的地址
  * `.relative_addr`：是它相对于对象库的地址。这在文献（特别是Windows文献）中称为RVA（相对虚拟地址）

​ 一个简单的使用例子就是：

    
    
    >>> malloc.name
    'malloc'
    
    >>> malloc.owner_obj
    <ELF Object libc.so.6, maps [0x1000000:0x13c42bf]>
    
    >>> malloc.rebased_addr
    0x1054400
    >>> malloc.linked_addr
    0x54400
    >>> malloc.relative_addr
    0x54400
    

​ 我们还可以判断一个符号是导入符号还是导出符号，根据官方文档的例子：

    
    
    >>> malloc.is_export
    True
    >>> malloc.is_import
    False
    
    # On Loader, the method is find_symbol because it performs a search operation to find the symbol.
    # On an individual object, the method is get_symbol because there can only be one symbol with a given name.
    >>> main_malloc = proj.loader.main_object.get_symbol("malloc")
    >>> main_malloc
    <Symbol "malloc" in true (import)>
    >>> main_malloc.is_export
    False
    >>> main_malloc.is_import
    True
    >>> main_malloc.resolvedby
    <Symbol "malloc" in libc.so.6 at 0x1054400>
    

​ 我们还可以定向查看具体对应的共享库的导入或者导出符号表

    
    
    # Relocations don't have a good pretty-printing, so those addresses are python-internal, unrelated to our program
    >>> proj.loader.shared_objects['libc.so.6'].imports
    {u'__libc_enable_secure': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x4221fb0>,
     u'__tls_get_addr': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x425d150>,
     u'_dl_argv': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x4254d90>,
     u'_dl_find_dso_for_object': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x425d130>,
     u'_dl_starting_up': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x42548d0>,
     u'_rtld_global': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x4221e70>,
     u'_rtld_global_ro': <cle.backends.relocations.generic.GenericJumpslotReloc at 0x4254210>}
    

###  1.2 CLE源码分析

####  1.2.1 loader类

​
CLE源码文件里的`__init__.py`没有什么值得分析的点，分析CLE包，关键是分析CLE的loader类，这就是源码文件里的`loader.py`

​ 我们当然首先关注loader类的初始化方法

    
    
     def __init__(self, main_binary, auto_load_libs=True, concrete_target = None,
                     force_load_libs=(), skip_libs=(),
                     main_opts=None, lib_opts=None, ld_path=(), use_system_libs=True,
                     ignore_import_version_numbers=True, case_insensitive=False, rebase_granularity=0x100000,
                     except_missing_libs=False, aslr=False, perform_relocations=True, load_debug_info=False,
                     page_size=0x1, preload_libs=(), arch=None):
    

​ 其中的说明文档如下：

    
    
        """
        The loader loads all the objects and exports an abstraction of the memory of the process. What you see here is an address space with loaded and rebased binaries.
        :param main_binary:         The path to the main binary you're loading, or a file-like object with the binary in it.The following parameters are optional.
        :param auto_load_libs:      Whether to automatically load shared libraries that loaded objects depend on.
        :param load_debug_info:     Whether to automatically parse DWARF data and search for debug symbol files.
        :param concrete_target:     Whether to instantiate a concrete target for a concrete execution of the process.if this is the case we will need to instantiate a SimConcreteEngine that wraps the ConcreteTarget provided by the user.
        :param force_load_libs:     A list of libraries to load regardless of if they're required by a loaded object.
        :param skip_libs:           A list of libraries to never load, even if they're required by a loaded object.
        :param main_opts:           A dictionary of options to be used loading the main binary.
        :param lib_opts:            A dictionary mapping library names to the dictionaries of options to be used when loading them.
        :param ld_path:      A list of paths in which we can search for shared libraries.
        :param use_system_libs:     Whether or not to search the system load path for requested libraries. Default True.
        :param ignore_import_version_numbers:
                                    Whether libraries with different version numbers in the filename will be considered equivalent, for example libc.so.6 and libc.so.0
        :param case_insensitive:    If this is set to True, filesystem loads will be done case-insensitively regardless of the case-sensitivity of the underlying filesystem.
        :param rebase_granularity:  The alignment to use for rebasing shared objects
        :param except_missing_libs: Throw an exception when a shared library can't be found.
        :param aslr:                Load libraries in symbolic address space. Do not use this option.
        :param page_size:           The granularity with which data is mapped into memory. Set to 1 if you are working in a non-paged environment.
        :param preload_libs:        Similar to `force_load_libs` but will provide for symbol resolution, with precedence over any dependencies.
        :ivar memory:               The loaded, rebased, and relocated memory of the program.
        :vartype memory:            cle.memory.Clemory
        :ivar main_object:          The object representing the main binary (i.e., the executable).
        :ivar shared_objects:       A dictionary mapping loaded library names to the objects representing them.
        :ivar all_objects:          A list containing representations of all the different objects loaded.
        :ivar requested_names:      A set containing the names of all the different shared libraries that were marked as a dependency by somebody.
        :ivar initial_load_objects: A list of all the objects that were loaded as a result of the initial load request.
    
        When reference is made to a dictionary of options, it requires a dictionary with zero or more of the following keys:
    
        - backend :             "elf", "pe", "mach-o", "blob" : which loader backend to use
        - arch :                The archinfo.Arch object to use for the binary
        - base_addr :           The address to rebase the object at
        - entry_point :         The entry point to use for the object
    
        More keys are defined on a per-backend basis.
        """
    

参数的解析主要如下：

  * main_binary：要加载主要二进制文件的路径，或者一个带有二进制文件的对象
  * auto_load_libs：是否自动加载加载对象所依赖的共享库
  * force_load_libs：要加载的库列表，无论加载的对象是否需要它们
  * skip_libs：永不加载的库列表，即使加载对象需要它们也是如此
  * main_opts：加载主二进制文件的选项字典
  * lib_opts：字典映射库名称到加载它们时要使用的选项的字典
  * custom_ld_path：我们可以在其中搜索共享库的路径列表
  * use_system_libs：是否搜索所请求库的系统加载路径。默认为True
  * ignore_import_version_numbers：文件名中具有不同版本号的库是否会被视为等效，例如libc.so.6和libc.so.0
  * case_insensitive：如果将其设置为True，则无论基础文件系统的区分大小写如何，文件系统加载都将以区分大小写的方式完成
  * rebase_granularity：用于重新定位共享对象的对齐方式
  * except_missing_libs：无法找到共享库时抛出异常
  * aslr：在符号地址空间中加载库（我觉得是指开启ASLR机制）。不要使用此选项
  * page_size：数据映射到内存的粒度。如果在非分页环境中工作，请设置为1

还有一些变量的解释：

  * memory：程序的加载，重新定位和重定位的内存
  * main_object：表示主二进制文件的对象（即可执行文件）
  * shared_objects：将加载的库名称映射到表示它们的对象的字典
  * all_objects：包含加载的所有不同对象的表示的列表
  * requested_names：包含由某人标记为依赖项的所有不同共享库的名称的集合
  * initial_load_objects：由于初始加载请求而加载的所有对象的列表

​ 在加载二进制文件时可以设置特定的参数，使用 `main_opts` 和 `lib_opts` 参数进行设置，例如：

  * `backend`：指定 backend
  * `base_addr` ：指定基址
  * `entry_point` ：指定入口点
  * `arch` ：指定架构

    
    
    >>> angr.Project('examples/fauxware/fauxware', main_opts={'backend': 'blob', 'arch': 'i386'}, lib_opts={'libc.so.6': {'backend': 'elf'}})
    <Project examples/fauxware/fauxware>
    

​ 我们来看看源码

    
    
    if hasattr(main_binary, 'seek') and hasattr(main_binary, 'read'):
                self._main_binary_path = None
                self._main_binary_stream = main_binary
            else:
                self._main_binary_path = os.path.realpath(str(main_binary))
                self._main_binary_stream = None
    
            # whether we are presently in the middle of a load cycle
            self._juggling = False
    
            # auto_load_libs doesn't make any sense if we have a concrete target.
            if concrete_target:
                auto_load_libs = False
    
            self._auto_load_libs = auto_load_libs
            self._load_debug_info = load_debug_info
            self._satisfied_deps = dict((x, False) for x in skip_libs)
            self._main_opts = {} if main_opts is None else main_opts
            self._lib_opts = {} if lib_opts is None else lib_opts
            self._custom_ld_path = [ld_path] if type(ld_path) is str else ld_path
            force_load_libs = [force_load_libs] if type(force_load_libs) is str else force_load_libs
            preload_libs = [preload_libs] if type(preload_libs) is str else preload_libs
            self._use_system_libs = use_system_libs
            self._ignore_import_version_numbers = ignore_import_version_numbers
            self._case_insensitive = case_insensitive
            self._rebase_granularity = rebase_granularity
            self._except_missing_libs = except_missing_libs
            self._relocated_objects = set()
            self._perform_relocations = perform_relocations
    
            # case insensitivity setup
            if sys.platform == 'win32': # TODO: a real check for case insensitive filesystems
                if self._main_binary_path: self._main_binary_path = self._main_binary_path.lower()
                force_load_libs = [x.lower() if type(x) is str else x for x in force_load_libs]
                for x in list(self._satisfied_deps): self._satisfied_deps[x.lower()] = self._satisfied_deps[x]
                for x in list(self._lib_opts): self._lib_opts[x.lower()] = self._lib_opts[x]
                self._custom_ld_path = [x.lower() for x in self._custom_ld_path]
    
            self.aslr = aslr
            self.page_size = page_size
            self.memory = None
            self.main_object = None
            self.tls = None
            self._kernel_object = None # type: Optional[KernelObject]
            self._extern_object = None # type: Optional[ExternObject]
            self.shared_objects = OrderedDict()
            self.all_objects = []  # type: List[Backend]
            self.requested_names = set()
            if arch is not None:
                self._main_opts.update({'arch': arch})
            self.preload_libs = []
    

​ 到这里为止都是在使用传入的参数进行对象的初始化，然后

    
    
    self.initial_load_objects = self._internal_load(main_binary, *preload_libs, *force_load_libs, preloading=(main_binary, *preload_libs))
    

​ 这里是在调用内部函数 `_internal_load(main_binary, *force_load_libs)`
加载对象文件。该函数返回一个所加载对象的列表（需要注意的是如果其中有任意一个不能正确加载，函数将会退出）

​ 接下来我们来分析这个内部函数

    
    
    def _internal_load(self, *args, preloading=()):
            """
            Pass this any number of files or libraries to load. If it can't load any of them for any reason, it will except out. Note that the semantics of ``auto_load_libs`` and ``except_missing_libs`` apply at all times.
            It will return a list of all the objects successfully loaded, which may be smaller than the list you provided if any of them were previously loaded.
            The ``main_binary`` has to come first, followed by any additional libraries to load this round. To create the effect of "preloading", i.e. ensuring symbols are resolved to preloaded libraries ahead of any others, pass ``preloading`` as a list of identifiers which should be considered preloaded. Note that the identifiers will be compared using object identity.
            """
    
            # ideal loading pipeline:
            # - load everything, independently and recursively until dependencies are satisfied
            # - resolve symbol-based dependencies
            # - layout address space, including (as a prerequisite) coming up with the layout for tls and externs
            # - map everything into memory
            # - perform relocations
    

​
开头的语句的意思就是我们可以传递给任意数量的文件或库给这个函数进行加载的处理，需要注意的是如果其中有任意一个不能正确加载，函数将会退出。`auto_load_libs`和`except_missing_libs`参数也将对这个函数对于传入的对象处理产生影响

​
它将返回所有成功加载的对象的列表，该列表可能小于我们提供的希望加载对象的列表。之后的意义大概就是要注意传入列表的顺序，应该首先传入我们希望分析的程序，然后是其它库，在其它库中也应该优先加载符号解析

​ 一个理想完美的加载器应该包含以下内容：

  * 可以独立且递归地加载所有内容，直到满足依赖关系为止
  * 可以解决基于符号的依赖性
  * 拥有完善的布局地址空间，包括能兼容tls和extern的布局空间（作为先决条件）
  * 可以将所有内容映射到内存中
  * 可以完美执行重定位

​
我们的`CLE.loader`也的确是这样设计并这样做的，首先加载所有内容，对于每个二进制文件，独立分别加载，以便我们得到一个Backend实例。如果`auto_load_libs`处于打开状态，则迭代执行此操作，直到满足所有依赖关系为止

    
    
     for main_spec in args:
                is_preloading = any(spec is main_spec for spec in preloading)
                if self.find_object(main_spec, extra_objects=objects) is not None:
                    l.info("Skipping load request %s - already loaded", main_spec)
                    continue
                obj = self._load_object_isolated(main_spec)
    

​ 这里是首先遍历传入的参数，并判断对应的文件是否已经被加载，如果是，则跳过，否则调用函数 `_load_object_isolated()`
加载单个文件。这里我们又要跟进到`_load_object_isolated`函数中，该函数给定一个依赖关系的部分规范，这会将加载的对象作为后端实例返回。它不会触及
Loader 的任何全局数据

​ 我们先来看看这个函数的源码

    
    
    def _load_object_isolated(self, spec):
            """
            Given a partial specification of a dependency, this will return the loaded object as a backend instance.
            It will not touch any loader-global data.
            """
            # STEP 1: identify file
            if isinstance(spec, Backend):
                return spec
            elif hasattr(spec, 'read') and hasattr(spec, 'seek'):
                binary_stream = spec
                binary = None
                close = False
            elif type(spec) in (bytes, str):
                binary = self._search_load_path(spec) # this is allowed to cheat and do partial static loading
                l.debug("... using full path %s", binary)
                binary_stream = open(binary, 'rb')
                close = True
            else:
                raise CLEError("Bad library specification: %s" % spec)
    
            try:
                # STEP 2: collect options
                if self.main_object is None:
                    options = dict(self._main_opts)
                else:
                    for ident in self._possible_idents(binary_stream if binary is None else binary): # also allowed to cheat
                        if ident in self._lib_opts:
                            options = dict(self._lib_opts[ident])
                            break
                    else:
                        options = {}
    
                # STEP 3: identify backend
                backend_spec = options.pop('backend', None)
                backend_cls = self._backend_resolver(backend_spec)
                if backend_cls is None:
                    backend_cls = self._static_backend(binary_stream if binary is None else binary)
                if backend_cls is None:
                    raise CLECompatibilityError("Unable to find a loader backend for %s.  Perhaps try the 'blob' loader?" % spec)
    
                # STEP 4: LOAD!
                l.debug("... loading with %s", backend_cls)
    
                result = backend_cls(binary, binary_stream, is_main_bin=self.main_object is None, loader=self, **options)
                result.close()
                return result
            finally:
                if close:
                    binary_stream.close()
    

简单来说就是：

  * 首先识别文件，确认是一个二进制文件后，调用函数 `_search_load_path()` 获取完整的文件路径
  * 收集选项 options。遍历生成器 `_possible_idents(full_spec)`，获得所有可能用于描述给定 spec 的识别符 ident，然后取出 `_lib_opts[ident]`
  * 识别后端。从 options 中获得 backend_spec，调用函数 `_backend_resolver()` 得到对应的后端类 backend_cls，如果 backend_cls 不存在，则又调用函数 `_static_backend()` 来获取。这个过程还是值得说一下。`ALL_BACKENDS` 是一个全局字典，里面保存了所有通过函数 `register_backend(name, cls)` 注册的后端。每个后端都需要有一个 `is_compatible()` 函数，这个函数就是用于判断对象文件是否属于该后端所操作的对象，判断方法是二进制特征匹配，例如 ELF 文件：`if identstring.startswith('x7fELF')`
  * 最后创建`backend_cls`类的实例

​ 然后现在我们继续回到`_internal_load`函数中，看看接下来的源代码

    
    
                obj = self._load_object_isolated(main_spec)
                objects.append(obj)
                objects.extend(obj.child_objects)
                dependencies.extend(obj.deps)
    
                if self.main_object is None:
                    # this is technically the first place we can start to initialize things based on platform
                    self.main_object = obj
                    self.memory = Clemory(obj.arch, root=True)
    
                    chk_obj = self.main_object if isinstance(self.main_object, ELFCore) or not self.main_object.child_objects else self.main_object.child_objects[0]
                    if isinstance(chk_obj, ELFCore):
                        self.tls = ELFCoreThreadManager(self, obj.arch)
                    elif isinstance(obj, Minidump):
                        self.tls = MinidumpThreadManager(self, obj.arch)
                    elif isinstance(chk_obj, MetaELF):
                        self.tls = ELFThreadManager(self, obj.arch)
                    elif isinstance(chk_obj, PE):
                        self.tls = PEThreadManager(self, obj.arch)
                    else:
                        self.tls = ThreadManager(self, obj.arch)
    

​ 这里就是将加载的所有对象添加到列表 objects，依赖添加到 dependencies。且如果 `self.main_object`
没有指定的话，就将其设置为第一个加载的对象，并创建一个 Clemory 类的实例，用于初始化内存空间，然后将其赋值给
`self.memory`，然后还有根据不同文件格式例如ELF或者PE的不同再初始化tls

​ 我们继续看看

    
    
    ordered_objects = []
    soname_mapping = OrderedDict((obj.provides if not self._ignore_import_version_numbers else obj.provides.rstrip('.0123456789'), obj) for obj in objects if obj.provides)
    seen = set()
    def visit(obj):
        if id(obj) in seen:
            return
        seen.add(id(obj))
    
        stripped_deps = [dep if not self._ignore_import_version_numbers else dep.rstrip('.0123456789') for dep in obj.deps]
        dep_objs = [soname_mapping[dep_name] for dep_name in stripped_deps if dep_name in soname_mapping]
        for dep_obj in dep_objs:
            visit(dep_obj)
    
        ordered_objects.append(obj)
    
        for obj in preload_objects + objects:
            visit(obj)
    

​ 之后就是在加载并移除所有 dependencies 里的对象文件，添加到 objects，依赖添加到 dependencies。如此一直执行下去直到
dependencies 为空。此时 objects 里就是所有加载对象

    
    
     extern_obj = ExternObject(self)
    
    # tls registration
    for obj in objects:
        self.tls.register_object(obj)
    
    # link everything
    if self._perform_relocations:
        for obj in ordered_objects:
            l.info("Linking %s", obj.binary)
            sibling_objs = list(obj.parent_object.child_objects) if obj.parent_object is not None else []
            stripped_deps = [dep if not self._ignore_import_version_numbers else dep.rstrip('.0123456789') for dep in obj.deps]
            dep_objs = [soname_mapping[dep_name] for dep_name in stripped_deps if dep_name in soname_mapping]
            main_objs = [self.main_object] if self.main_object is not obj else []
            for reloc in obj.relocs:
                reloc.resolve_symbol(main_objs + preload_objects + sibling_objs + dep_objs + [obj], extern_object=extern_obj)
    
    # if the extern object was used, add it to the list of objects we're mapping
    # also add it to the linked list of extern objects
    if extern_obj.map_size:
    # resolve the extern relocs this way because they may produce more relocations as we go
        i = 0
        while i < len(extern_obj.relocs):
            extern_obj.relocs[i].resolve_symbol(objects, extern_object=extern_obj)
            i += 1
    
        objects.append(extern_obj)
        ordered_objects.insert(0, extern_obj)
        extern_obj._next_object = self._extern_object
        self._extern_object = extern_obj
    
        extern_obj._finalize_tls()
        self.tls.register_object(extern_obj)
    

​ 然后接下来就是最后遍历 objects，依次调用 `_register_object`、`_map_object` 和
`_relocate_object`，进行对象注册、地址映射和重定位操作。如果启用了 TLS，那么还需要对 TLS
对象进行注册和地址映射。这就完成了所有CLE加载对象的内存地址空间的布局，也就完成了二进制文件的加载

####  1.2.2 Clemory类

​ Clemory 类的实例用于表示内存空间，也就是angr使用加载二进制文件的虚拟内存空间，并提供了操作内存空间的API。它使用 backers 和
updates 来区分内存加载和内存写入的概念，使得查找的效率更高。通过 `[index]` 这样的形式进行内存访问

​ 可以通过 `state.mem[index]` 访问内存，但对于一段连续内存的操作十分不方便。因此我们也可以使用 `state.memory` 的
`.load(addr, size) / .store(addr, val)` 接口读写内存, size 以 bytes 为单位。以下 load 和
store 的函数声明和一些参数解释：

    
    
    def load(self, addr, size=None, condition=None, fallback=None, add_constraints=None, action=None, endness=None,
                 inspect=True, disable_actions=False, ret_on_segv=False):
            """
            Loads size bytes from dst.
            :param addr:             The address to load from. #读取的地址
            :param size:            The size (in bytes) of the load. #大小
            :param condition:       A claripy expression representing a condition for a conditional load.
            :param fallback:        A fallback value if the condition ends up being False. 
            :param add_constraints: Add constraints resulting from the merge (default: True).
            :param action:          A SimActionData to fill out with the constraints.
            :param endness:         The endness to load with. #端序
           ....
    
    
    
    def store(self, addr, data, size=None, condition=None, add_constraints=None, endness=None, action=None,
                  inspect=True, priv=None, disable_actions=False):
            """
            Stores content into memory.
            :param addr:        A claripy expression representing the address to store at. #内存地址
            :param data:        The data to store (claripy expression or something convertable to a claripy expression).#写入的数据
            :param size:        A claripy expression representing the size of the data to store. #大小
            ...
    
    
    
    >>> s = proj.factory.blank_state()
    >>> s.memory.store(0x4000, s.solver.BVV(0x0123456789abcdef0123456789abcdef, 128))
    >>> s.memory.load(0x4004, 6) # load-size is in bytes
    <BV48 0x89abcdef0123>
    

​ 参数 `endness` 用于设置端序。可选的值如下：

    
    
    LE – 小端序(little endian, least significant byte is stored at lowest address)
    BE – 大端序(big endian, most significant byte is stored at lowest address)
    ME – 中间序(Middle-endian. Yep.)
    
    
    
    >>> import archinfo
    >>> s.memory.load(0x4000, 4, endness=archinfo.Endness.LE)
    <BV32 0x67453201>
    

​ 关于memory类的方法主要有以下这些：

  * `memory.load(addr, n) -> bytes`
  * `memory.store(addr, bytes)`
  * `memory[addr] -> int`
  * `memory.unpack_word(addr) -> int`
  * `memory.pack_word(addr, value)`
  * `memory.backers() -> iter[(start, bytearray)]`

​ 官方文档还提供了使用示例：

    
    
    import cffi, cle
    ffi = cffi.FFI()
    ld = cle.Loader('/bin/true')
    
    addr = ld.main_object.entry
    try:
        backer_start, backer = next(ld.memory.backers(addr))
    except StopIteration:
        raise Exception("not mapped")
    
    if backer_start > addr:
        raise Exception("not mapped")
    
    cbacker = ffi.from_buffer(backer)
    addr_pointer = cbacker + (addr - backer_start)
    

####  1.2.3 Backend类

​ Backend 是 CLE 所支持二进制对象文件的基类，我们可以看看它的初始函数

    
    
    class Backend:
        """
        Main base class for CLE binary objects.
    
        An alternate interface to this constructor exists as the static method :meth:`cle.loader.Loader.load_object`
    
        :ivar binary:           The path to the file this object is loaded from
        :ivar binary_basename:  The basename of the filepath, or a short representation of the stream it was loaded from
        :ivar is_main_bin:      Whether this binary is loaded as the main executable
        :ivar segments:         A listing of all the loaded segments in this file
        :ivar sections:         A listing of all the demarked sections in the file
        :ivar sections_map:     A dict mapping from section name to section
        :ivar imports:          A mapping from symbol name to import relocation
        :ivar resolved_imports: A list of all the import symbols that are successfully resolved
        :ivar relocs:           A list of all the relocations in this binary
        :ivar irelatives:       A list of tuples representing all the irelative relocations that need to be performed. The
                                first item in the tuple is the address of the resolver function, and the second item is the
                                address of where to write the result. The destination address is an RVA.
        :ivar jmprel:           A mapping from symbol name to the address of its jump slot relocation, i.e. its GOT entry.
        :ivar arch:             The architecture of this binary
        :vartype arch:          archinfo.arch.Arch
        :ivar str os:           The operating system this binary is meant to run under
        :ivar int mapped_base:  The base address of this object in virtual memory
        :ivar deps:             A list of names of shared libraries this binary depends on
        :ivar linking:          'dynamic' or 'static'
        :ivar linked_base:      The base address this object requests to be loaded at
        :ivar bool pic:         Whether this object is position-independent
        :ivar bool execstack:   Whether this executable has an executable stack
        :ivar str provides:     The name of the shared library dependancy that this object resolves
        :ivar list symbols:     A list of symbols provided by this object, sorted by address
        :ivar has_memory:       Whether this backend is backed by a Clemory or not. As it stands now, a backend should still
                                define `min_addr` and `max_addr` even if `has_memory` is False.
        """
        is_default = False
    
        def __init__(self,
                binary,
                binary_stream,
                loader=None,
                is_main_bin=False,
                entry_point=None,
                arch=None,
                base_addr=None,
                force_rebase=False,
                has_memory=True,
                **kwargs):
            """
            :param binary:          The path to the binary to load
            :param binary_stream:   The open stream to this binary. The reference to this will be held until you call close.
            :param is_main_bin:     Whether this binary should be loaded as the main executable
            """
    

  * binary：即我们指定文件路径
  * binary_stream：我们也可以使用二进制流的形式输入
  * loader：是否已经加载
  * is_main_bin：是不是作为主文件进行加载
  * entry_point：可以指定加载的进入点
  * arch：可以指定加载的架构
  * base_addr：可以指定文件加载的基地址
  * force_rebase：是否需要重新定义基底
  * has_memory：此后端是否由Clemory支持
  * kwargs：其它参数

每个实现的后端都需要通过函数 `register_backend` 进行注册。

    
    
    ALL_BACKENDS = dict()
    
    def register_backend(name, cls):
        if not hasattr(cls, 'is_compatible'):
            raise TypeError("Backend needs an is_compatible() method")
        ALL_BACKENDS.update({name: cls})
    

## 二、一切的中间层-VEX

​ VEX-IR是一套中间语言。使用它的是 Valgrind
插桩框架工具，它的设计思想类似LLVM与QEMU，为了模拟执行已经编译好的某种架构的程序，把目标代码转化为IR中间语言，再把 IR
翻译为本机架构可执行的机器语言，实现跨架构模拟执行，多用于没有源码的二进制程序分析。分析二进制程序，例如做类似插桩的工作时，失去了高级语言的抽象表达，不得不与更底层的部分打交道，即
CPU、寄存器、虚拟内存等

​ LLVM与QEMU其实本身并不是以安全分析为出发点的平台，只是因为他们过于完善和强大，所以有很多基于他们的改进工作来做程序安全分析。而 Valgrind
则是以安全为出发点开发的插桩框架，也相对成熟流行

​ 私以为看过学习过LLVM框架中的IR语言语法，再看VEX的IR语言语法，其实可以触类旁通，这里塞一个私货关于学习LLVM
IR的入门指南建议阅读GitHub用户EvianZhang的《LLVM IR入门指南》清晰易懂，可以先看看这个再看看VEX IR。学习VEX
IR可以查看VEX的官方文档，中文资料也可以参考知乎用户王志的《angr中的中间语言表示VEX》

> ​ 一个经常的问题就是为什么有时候Angr解析出来的IR或者说Block与IDA
> Pro中看到的不一样，就是因为两者使用的中间语言不一样，Angr采用的是VEX IR而IDA Pro采用的是IDA microcode。IDA Pro
> 为代表的一些反编译软件，也是利用中间语言这一思想实现的。使用中间语言来做反编译的好处也很明显，可以摆脱复杂的设计不同处理器的指令，使得反编译可移植、适配性更广
>
> ​ IDA 自身的 IR 为 microcode，在 IDA 7.1 的时候开源。开源之前 IDA 一直在对这套 IR
> 做完善和优化，开源之后提供了相应的 API，更方便使用者利用 microcode 来开发插件做反编译的分析工作，例如应对花指令、混淆之类的情况

###  2.1 VEX简介

​ angr为了支持对多种CPU架构的二进制程序进行分析，angr采用了指令的中间表示（Intermediate
Representation）方法来描述CPU指令的操作过程。angr采用的是Valgrind的VEX中间表示方法。主要是因为VEX能将没有源码的二进制文件处理抽象成VEX的IR中间语言表示

​ 在angr项目中，PyVEX负责将二进制代码翻译成VEX中间表示。IRSB （Intermediate Representation Super-Block）是VEX中的基本块，表示一个入口和一个或多个出口的VEX语句序列（single-entry, multiple-exit code block）

​ 当处理不同的体系结构时，VEX IR会抽象出一些体系结构差异，并通过统一为标准的VEX IR语言消除这些差异，从而允许对所有结构的程序进行统一的分析：

  * 寄存器名称：寄存器的数量和名称在体系结构之间是不同的，但是现代CPU设计遵循一个共同的主题：每个CPU包含几个通用寄存器，用于保存堆栈指针的寄存器，用于存储条件标志的一组寄存器等等。IR为不同平台上的寄存器提供了一致的抽象接口，具体来说，VEX将寄存器建模为具有整数偏移量的单独存储空间。简单来说就是没有单独建立一个“寄存器”数据类型，而是将寄存器也视作一种内存，将CPU指令对寄存器的访问描述成对内存的访问，实现对寄存器操作的中间表示。VEX在内存中为寄存器分配了存储空间，为每个寄存器分配了一个索引地址
  * 内存访问：不同的体系结构以不同的方式访问内存。例如，ARM可以在小端或者大端模式下访问内存。VEX IR也同时支持对于小端序和大端序，消除了这些差异
  * 内存分段：某些体系结构（例如x86）通过使用特殊的段寄存器来支持内存分段以提供更高级的功能，VEX IR也同时支持这些功能
  * 具有副作用的指令：大多数指令都有副作用，也就是一连串的操作。例如，ARM上处于Thumb模式的大多数操作都会更新条件标志，而堆栈推入/弹出指令将更新堆栈指针。在分析中以临时方式跟踪这些副作用会很疯狂

​ VEX IR中间语言将机器代码抽象为一种统一的表示形式，旨在简化程序分析，这种表示形式的描述类型有以下5种：

  * 表达式（Expression）：表示 **数值** ，例如变量或常量的数值
  * 操作（Operation）：表示数值的 **计算** ，实现对数值的修改
  * 临时变量（Temporary Variables）：表示数值的 **存储** 位置
  * 语句（Statements）：表示数值对计算机 **状态的修改** ，例如对内存、寄存器的修改
  * 基本块（Block）：语句的 **集合** ，表示一列没有分支的语句序列

​
这5中描述类型中，首先是最基本的数值，使用表达式（Expression）来描述；其次，是数值间的计算、数值的存储，分别用操作（Operation）和临时变量（Temporary
Variable）来描述；然后，是数值对计算机状态的修改，使用语句（statement）来描述；最后，是语句的集合，表示一个包括多条语句的连续行为，使用基本块（Block）来描述

​ 我们主要介绍一些可能会经常与之交互的VEX的某些部分和它的VEX IR表达式

IR Expression | Evaluated Value | VEX Output Example  
---|---|---  
Constant | A constant value. | 0x4:I32  
Read Temp | The value stored in a VEX temporary variable. | RdTmp(t10)  
Get Register | The value stored in a register. | GET:I32(16)  
Load Memory | The value stored at a memory address, with the address specified
by another IR Expression. | LDle:I32 / LDbe:I64  
Operation | A result of a specified IR Operation, applied to specified IR
Expression arguments. | Add32  
If-Then-Else | If a given IR Expression evaluates to 0, return one IR
Expression. Otherwise, return another. | ITE  
Helper Function | VEX uses C helper functions for certain operations, such as
computing the conditional flags registers of certain architectures. These
functions return IR Expressions. | function_name()  
  
​ 以上是比较常用的最基础的VEX的IR表达式，接下来还有一些比较常用的部分是需要上面基本的部分组合的

IR Statement | Meaning | VEX Output Example  
---|---|---  
Write Temp | Set a VEX temporary variable to the value of the given IR
Expression. | WrTmp(t1) = (IR Expression)  
Put Register | Update a register with the value of the given IR Expression. |
PUT(16) = (IR Expression)  
Store Memory | Update a location in memory, given as an IR Expression, with a
value, also given as an IR Expression. | STle(0x1000) = (IR Expression)  
Exit | A conditional exit from a basic block, with the jump target specified
by an IR Expression. The condition is specified by an IR Expression. | if
(condition) goto (Boring) 0x4000A00:I32  
  
​ 总结来说CPU指令对计算机状态的修改，常见的是内存访问、寄存器访问，VEX都有对应的语句表示，我们可以再分别来看看

####  2.1.1 数值（Expression）

​ 在VEX
IR中最基础的数据类型就是数值，例如`0x4:I32`，就表示的是一个32位整数类型（I32）的0x4数值。这个就很类似LLVM的IR表示，这个在LLMV的写法应该就是`i32
0x4`

####  2.1.2 内存（memory）

​ 在VEX中内存的访问包括两种语句：读（Load）和写（Store）：

  * 读内存（Load Memory），例如`LDle:I32`和`LDbe:I64`，LD是读内存（Load Memory）的缩写，表示读内存操作；le和be表示两种字节序列，le是little endianess的缩写，表示是小端序，be是big endianess的缩写，表示是大端序；I32和I64表示的是读取的数据类型，分别表示32位整数和64位整数
  * 写内存（Store Memory），例如`STle(0x1000) = (IR Expression)`，ST是写内存（Store Memory）的缩写，le是字节序，0x1000是内存的地址，IR Expression是要写入的数值

​ 在LLVM IR中对于大小端序是在`target datalayout`字段中注明了目标汇编代码的数据分布，例如：

    
    
    target datalayout = "e-m:o-i64:64-f80:128-n8:16:32:64-S128"
    

​ 其中的e就代表了这次编译的平台采用小端序，在LLVM IR中对于内存的读写例子：

    
    
    %1 = load i32, i32* @global_variable
    store i32 1, i32* @global_variable
    

####  2.1.3 寄存器（Register）

​
VEX并没有为CPU寄存器创建一个新的存储类型，而是将CPU指令对寄存器的访问描述成对内存的访问，实现对寄存器操作的中间表示。VEX在内存中为寄存器分配了存储空间，为每个寄存器分配了一个索引地址

​ 寄存器的访问包括两种语句：读（Get）和写（Put）：

  * 读寄存器（Get Register），例如`GET:I32(16)`，GET是读寄存器（Get Register）的缩写，I32是数值的类型，16是一个寄存器在内存中的索引
  * 写寄存器（Put Register），例如`PUT(16) = (IR Expression)`，PUT是写寄存器（Put Register）的缩写，16是一个寄存器在内存中的索引，IR Expression是要写入寄存器中的数值

​ 在LLVM中对于寄存器的处理是引入了虚拟寄存器的概念，对于寄存器而言，我们只需要像普通的赋值语句一样操作，但需要注意名字必须以`%`开头：

    
    
    %local_variable = add i32 1, 2
    

​ 因为不同架构的寄存器数量不一样，且数量都是有限的，如果所有通用寄存器都用光了，LLVM
IR会帮我们把剩余的值放在栈上，但是对我们用户而言，实际上都是虚拟寄存器，LLVM对于保留的寄存器的操作也是放入栈中。简单来说就是LLVM
IR不是把寄存器的数据都放在内存中，单独抽象了一种数据类型叫虚拟寄存器，而VEX IR并没有创建一个新的存储类型，而是将寄存器都放在了内存中

####  2.1.4 临时变量（Temporary Variable）

​ 一条CPU指令通常会被多条中间表示的语句进行描述，中间会用到一些临时变量来存储中间值

​ 临时变量包括两种操作：读（Read）和写（Write）：

  * 读临时变量（Read Temp），例如RdTmp(t10)，RdTmp是读临时变量（Read Temp）的缩写，t10是一个临时变量的名称
  * 写临时变量（Write Temp），例如WrTmp(t1) = (IR Expression)，WrTmp是写临时变量（Write Temp）的缩写，t1是临时变量的名称，IR Expression是要写入临时变量t1的数值

###  2.2 VEX实例

​ 上面介绍了很多关于VEX IR的基础语法，没有实际的操作验证也还是有些晦涩难懂的，我们通过实际操作来看看现实中的VEX IR是如何工作的

​ 首先就同上一篇文章讲到的需要获取一个基本块（block），基本块对应一个相对的IRSB中间表示基本块信息，也就是我们想要看一个代码的VEX
IR样子，得先获取一个基本块，然后再通过这个基本块去查看IRSB信息，从而获得转换后的VEX IR代码

> IRSB（Intermediate Representation Super Block）表示一个中间表示的基本块

​ 我们这次使用一个简单的例子：

    
    
    #include<stdio.h>
    int main(){
        int a = 1;
        int b = 1;
        int c = a + b;
        return 0;
    }
    
    
    
    $ gcc 02.c -no-pie -g -o test2
    

​ 然后进行逐步调试，我们可以通过直接打印基本块的vex属性看到VEX
IR信息，bb.capstone是一个CapstoneBlock对象，bb.vex是一个IRSB对象

    
    
    >>> import angr
    >>> import monkeyhex
    >>> proj = angr.Project('./test2', auto_load_libs=False)
    >>> block = proj.factory.block(proj.entry)
    >>> type(block.capstone)
    <class 'angr.block.CapstoneBlock'>
    >>> type(block.vex)
    <class 'pyvex.block.IRSB'>
    >>> block.pp()
    0x401020:       endbr64
    0x401024:       xor     ebp, ebp
    0x401026:       mov     r9, rdx
    0x401029:       pop     rsi
    0x40102a:       mov     rdx, rsp
    0x40102d:       and     rsp, 0xfffffffffffffff0
    0x401031:       push    rax
    0x401032:       push    rsp
    0x401033:       mov     r8, 0x4011a0
    0x40103a:       mov     rcx, 0x401130
    0x401041:       mov     rdi, 0x401106
    0x401048:       call    qword ptr [rip + 0x2fa2]
    >>> print(block.vex)
    IRSB {
       t0:Ity_I32 t1:Ity_I32 t2:Ity_I32 t3:Ity_I64 t4:Ity_I64 t5:Ity_I64 t6:Ity_I64 t7:Ity_I64 t8:Ity_I64 t9:Ity_I64 t10:Ity_I64 t11:Ity_I64 t12:Ity_I32 t13:Ity_I64 t14:Ity_I64 t15:Ity_I64 t16:Ity_I64 t17:Ity_I32 t18:Ity_I64 t19:Ity_I32 t20:Ity_I64 t21:Ity_I64 t22:Ity_I64 t23:Ity_I64 t24:Ity_I64 t25:Ity_I64 t26:Ity_I64 t27:Ity_I64 t28:Ity_I64 t29:Ity_I64 t30:Ity_I64 t31:Ity_I64 t32:Ity_I64 t33:Ity_I64
    
       00 | ------ IMark(0x401020, 4, 0) ------       01 | ------ IMark(0x401024, 2, 0) ------       02 | PUT(rbp) = 0x0000000000000000
       03 | ------ IMark(0x401026, 3, 0) ------       04 | t23 = GET:I64(rdx)
       05 | PUT(r9) = t23
       06 | PUT(rip) = 0x0000000000401029
       07 | ------ IMark(0x401029, 1, 0) ------       08 | t4 = GET:I64(rsp)
       09 | t3 = LDle:I64(t4)
       10 | t24 = Add64(t4,0x0000000000000008)
       11 | PUT(rsi) = t3
       12 | ------ IMark(0x40102a, 3, 0) ------       13 | PUT(rdx) = t24
       14 | ------ IMark(0x40102d, 4, 0) ------       15 | t5 = And64(t24,0xfffffffffffffff0)
       16 | PUT(cc_op) = 0x0000000000000014
       17 | PUT(cc_dep1) = t5
       18 | PUT(cc_dep2) = 0x0000000000000000
       19 | PUT(rip) = 0x0000000000401031
       20 | ------ IMark(0x401031, 1, 0) ------       21 | t8 = GET:I64(rax)
       22 | t26 = Sub64(t5,0x0000000000000008)
       23 | PUT(rsp) = t26
       24 | STle(t26) = t8
       25 | PUT(rip) = 0x0000000000401032
       26 | ------ IMark(0x401032, 1, 0) ------       27 | t28 = Sub64(t26,0x0000000000000008)
       28 | PUT(rsp) = t28
       29 | STle(t28) = t26
       30 | ------ IMark(0x401033, 7, 0) ------       31 | PUT(r8) = 0x00000000004011a0
       32 | ------ IMark(0x40103a, 7, 0) ------       33 | PUT(rcx) = 0x0000000000401130
       34 | ------ IMark(0x401041, 7, 0) ------       35 | PUT(rdi) = 0x0000000000401106
       36 | PUT(rip) = 0x0000000000401048
       37 | ------ IMark(0x401048, 6, 0) ------       38 | t14 = LDle:I64(0x0000000000403ff0)
       39 | t30 = Sub64(t28,0x0000000000000008)
       40 | PUT(rsp) = t30
       41 | STle(t30) = 0x000000000040104e
       42 | t32 = Sub64(t30,0x0000000000000080)
       43 | ====== AbiHint(0xt32, 128, t14) ======
       NEXT: PUT(rip) = t14; Ijk_Call
    }
    

​ 我们首先关注到第一行

    
    
     t0:Ity_I32 t1:Ity_I32 t2:Ity_I32 t3:Ity_I64 t4:Ity_I64 t5:Ity_I64 t6:Ity_I64 t7:Ity_I64 t8:Ity_I64 t9:Ity_I64 t10:Ity_I64 t11:Ity_I64 t12:Ity_I32 t13:Ity_I64 t14:Ity_I64 t15:Ity_I64 t16:Ity_I64 t17:Ity_I32 t18:Ity_I64 t19:Ity_I32 t20:Ity_I64 t21:Ity_I64 t22:Ity_I64 t23:Ity_I64 t24:Ity_I64 t25:Ity_I64 t26:Ity_I64 t27:Ity_I64 t28:Ity_I64 t29:Ity_I64 t30:Ity_I64 t31:Ity_I64 t32:Ity_I64 t33:Ity_I64
    

​ 这一行表示该IRSB中临时变量的信息，可以看到一共有34个临时变量，变量名从t0到t33

​ IRSB中，每个CPU指令中间表示的开始位置都是一个IMark的标记。IMark是Instruction Mark的缩写

​ IMark的格式是`IMark(<addr>, <len>, <delta>)`

  * addr：表示该CPU指令在内存中的地址
  * len：表示该CPU指令在内存中占几个字节
  * delta：表示该指令是否为Thumb Instruction。通常x86、amd64平台上的CPU指令，delta值都是0，只有Thumb指令的delta值是1

​ 例如我们来看看一下这个例子，上面的是x86架构的汇编指令，下面的是它抽象成的VEX IR中间语言

    
    
    0x401024:       xor     ebp, ebp
    
    
    
    01 | ------ IMark(0x401024, 2, 0) ------    02 | PUT(rbp) = 0x0000000000000000
    

​ 指令`xor ebp, ebp`的内存地址是0x401024，指令长度是2字节（0x401026-0x401024），该指令不是Thumb
Instruction，所以对应的IMark是`IMark(0x401024,2,0)`

​ `xor ebp，ebp`把ebp寄存器的值清零，对应的中间表示就是PUT(rbp)=0x0000000000000000，把数值0写入rbp寄存器

​ 我们再往下看一行

    
    
    0x401026:       mov     r9, rdx
    
    03 | ------ IMark(0x401026, 3, 0) ------    04 | t23 = GET:I64(rdx)
    05 | PUT(r9) = t23
    06 | PUT(rip) = 0x0000000000401029
    

​ 指令`mov r9, rdx`把寄存器rdx的值存储到寄存器r9上面，对应了3条VEX中间表示语句：

  * `t23 = GET:I64(rdx)`：将rdx寄存器的值存储到t23临时变量中
  * `PUT(r9) = t23`：将临时变量t23的值存储到r9寄存器中
  * `PUT(rip) = 0x0000000000401029`：更新指令指针寄存器rip的值，指向下一条CPU指令

> 更新rip的值是CPU指令mov r9,
> rdx的副作用，在二进制代码中不能直接看到，而VEX将CPU指令的副作用显示的表示了出来。其它的CPU指令副作用还有对EFlags状态寄存器的修改、栈寄存器RSP的修改等等

​ 然后接下来我们来看看对栈的操作的VEX IR

    
    
    0x401029:       pop     rsi
    
    07 | ------ IMark(0x401029, 1, 0) ------    08 | t4 = GET:I64(rsp)
    09 | t3 = LDle:I64(t4)
    10 | t24 = Add64(t4,0x0000000000000008)
    11 | PUT(rsi) = t3
    

​ 指令`pop rsi`，将栈顶指针rsp所指的内存位置的数据存储到rsi寄存器中，对应了4条VEX中间表示语句：

  * `t4 = GET:I64(rsp)`：将rsp寄存器的值存储到t4临时变量中
  * `t3 = LDle:I64(t4)`：以64位小端序的形式读取变量t4存储的内存地址中的数据保存到t3临时变量中
  * `t24 = Add64(t4,0x0000000000000008)`：将临时变量t4的值增加0x8，因为是64位的栈所以相当于降栈（栈是从高地址往低地址增长）
  * `PUT(rsi) = t3`：将临时变量t3的值存储到rsi寄存器中

​ 最后我们来看看call指令

    
    
    0x401048:       call    qword ptr [rip + 0x2fa2]
    
    37 | ------ IMark(0x401048, 6, 0) ------    38 | t14 = LDle:I64(0x0000000000403ff0)
    39 | t30 = Sub64(t28,0x0000000000000008)
    40 | PUT(rsp) = t30
    41 | STle(t30) = 0x000000000040104e
    42 | t32 = Sub64(t30,0x0000000000000080)
    43 | ====== AbiHint(0xt32, 128, t14) ======
    NEXT: PUT(rip) = t14; Ijk_Call
    

​ `call qword ptr [rip +
0x2fa2]`，调用指定的函数。对应的VEX中间表示可以看到，将call指令的副作用（将返回地址写入栈中）也显示的表示出来：

  * `t14 = LDle:I64(0x0000000000403ff0)`：以64位小端序的形式读取0x0403ff0内存地址中的数据保存到t14临时变量中
  * `t30 = Sub64(t28,0x0000000000000008)`：在栈顶增长8个字节（栈顶是向低地址方向增长）
  * `PUT(rsp) = t30`：更新栈顶指针rsp的值
  * `STle(t30) = 0x000000000040104e`：将call指令的返回地址0x000000000040104e写入栈顶
  * `t32 = Sub64(t30,0x0000000000000080)`：在栈顶增长8个字节

​ ABI（Application Binary
Interface）应用二进制接口，表示两个二进制底层对象的接口信息，类似于源代码层使用的API接口。VEX的AbiHint用来指定一个未定义（undefined）的内存区间（a
given chunk of address space）

​ AbiHint的格式是`AbiHint(<base>, <len>, <nia>)` ：

  * base：表示未定义内存区间的起始地址（Start of undefined chunk ）
  * len：表示该未定义内存区间的长度（Length of undefined chunk），128是一个默认值
  * nia：是下一条指令的内存地址（Address of next (guest) insn）

​ IRSB的最后是修改指令指针寄存器rip的值，将CPU控制权转交给被调用函数，并标记该跳转的类型是Ijk_Call，表示是一个call指令跳转

###  2.3 IRSB的源码

​ IRSB基本块是在Block构造函数中创建的

​ `angr/angr/factory.py`中，`block()`函数：

    
    
    @overload
    def block(self, addr: int, size=None, max_size=None, byte_string=None, vex=None, thumb=False, backup_state=None,
              extra_stop_points=None, opt_level=None, num_inst=None, traceflags=0,
              insn_bytes=None, insn_text=None,  # backward compatibility
              strict_block_end=None, collect_data_refs=False, cross_insn_opt=True,
              ) -> 'Block': ...
    ......
        # 调用了Block类的构造函数
        return Block(addr, project=self.project, size=size, byte_string=byte_string, vex=vex,
                     extra_stop_points=extra_stop_points, thumb=thumb, backup_state=backup_state,
                     opt_level=opt_level, num_inst=num_inst, traceflags=traceflags,
                     strict_block_end=strict_block_end, collect_data_refs=collect_data_refs,
                     cross_insn_opt=cross_insn_opt,
        )
    # Block类的定义在angr/angr/block.py文件中
    from .block import Block, SootBlock
    

​
`angr/angr/block.py`中，Block的`__init__()`调用了`_vex_engine.lift_vex()`获得了IRSB基本块对象，并将IRSB对象保存在Block对象的vex属性中

    
    
     def __init__(self, addr, project=None, arch=None, size=None, byte_string=None, vex=None, thumb=False, backup_state=None,
                     extra_stop_points=None, opt_level=None, num_inst=None, traceflags=0, strict_block_end=None,
                     collect_data_refs=False, cross_insn_opt=True):
            ......# 省略了一些语句
    
            if size is None:
                if byte_string is not None:
                    size = len(byte_string)
                elif vex is not None:
                    size = vex.size
                else:
                    # 调用_vex_engine.lift_vex()获得IRSB基本块对象，并将IRSB对象保存在vex属性中
                    vex = self._vex_engine.lift_vex(
                            clemory=project.loader.memory,
                            state=backup_state,
                            insn_bytes=byte_string,
                            addr=addr, # 0x400580
                            thumb=thumb, # False
                            extra_stop_points=extra_stop_points,
                            opt_level=opt_level,
                            num_inst=num_inst,
                            traceflags=traceflags,
                            strict_block_end=strict_block_end,
                            collect_data_refs=collect_data_refs,
                            cross_insn_opt=cross_insn_opt,
                    )
                    size = vex.size
    

​
vex_engine的`lift_vex()`定义在`angr/angr/engines/vex/lifter.py`中，调用`pyvex.lift()`获得IRSB对象

    
    
    import pyvex
    ......
    
           # phase 5: call into pyvex
            l.debug("Creating IRSB of %s at %#x", arch, addr)
            try:
                for subphase in range(2):
    
                    irsb = pyvex.lift(buff, addr + thumb, arch,
                                      max_bytes=size,
                                      max_inst=num_inst,
                                      bytes_offset=thumb,
                                      traceflags=traceflags,
                                      opt_level=opt_level,
                                      strict_block_end=strict_block_end,
                                      skip_stmts=skip_stmts,
                                      collect_data_refs=collect_data_refs,
                                      cross_insn_opt=cross_insn_opt
                                      )
    

​ 在PyVEX的Github仓库中的README中介绍了更多的用法

    
    
    import pyvex
    import archinfo
    
    # translate an AMD64 basic block (of nops) at 0x400400 into VEX
    # 将一个AMD64格式得二进制数据（nops指令）转换为IRSB的基本块类型
    irsb = pyvex.lift(b"\x90\x90\x90\x90\x90", 0x400400, archinfo.ArchAMD64())
    
    # pretty-print the basic block
    # 打印基本块的汇编代码
    irsb.pp()
    
    # this is the IR Expression of the jump target of the unconditional exit at the end of the basic block
    print(irsb.next)
    
    # this is the type of the unconditional exit (i.e., a call, ret, syscall, etc)
    print(irsb.jumpkind)
    
    # you can also pretty-print it
    irsb.next.pp()
    
    # iterate through each statement and print all the statements
    for stmt in irsb.statements:
        stmt.pp()
    
    # pretty-print the IR expression representing the data, and the *type* of that IR expression written by every store statement
    import pyvex
    for stmt in irsb.statements:
        if isinstance(stmt, pyvex.IRStmt.Store):
            print("Data:", end="")
            stmt.data.pp()
            print("")
    
            print("Type:", end="")
            print(stmt.data.result_type)
            print("")
    
    # pretty-print the condition and jump target of every conditional exit from the basic block
    for stmt in irsb.statements:
        if isinstance(stmt, pyvex.IRStmt.Exit):
            print("Condition:", end="")
            stmt.guard.pp()
            print("")
    
            print("Target:", end="")
            stmt.dst.pp()
            print("")
    
    # these are the types of every temp in the IRSB
    print(irsb.tyenv.types)
    
    # here is one way to get the type of temp 0
    print(irsb.tyenv.types[0])
    

​ 执行完毕的效果：

    
    
    IRSB {
       t0:Ity_I64
    
       00 | ------ IMark(0x400400, 1, 0) ------       01 | ------ IMark(0x400401, 1, 0) ------       02 | ------ IMark(0x400402, 1, 0) ------       03 | ------ IMark(0x400403, 1, 0) ------       04 | ------ IMark(0x400404, 1, 0) ------       NEXT: PUT(rip) = 0x0000000000400405; Ijk_Boring
    }
    0x0000000000400405
    Ijk_Boring
    0x0000000000400405
    ------ IMark(0x400400, 1, 0) ------    ------ IMark(0x400401, 1, 0) ------    ------ IMark(0x400402, 1, 0) ------    ------ IMark(0x400403, 1, 0) ------    ------ IMark(0x400404, 1, 0) ------    ['Ity_I64']
    Ity_I64
    

## 三、参考资料

在此感谢各位作者或者译者的辛苦付出，特此感谢

  * [angr官方文档](https://docs.angr.io/)
  * [angr入门之CLE](https://blog.csdn.net/baizhi2361/article/details/101084429)
  * [angr源码分析——cle.Loader类](https://blog.csdn.net/doudoudouzoule/article/details/79354436?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-3.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-3.control)
  * [angr中的中间语言表示VEX](https://zhuanlan.zhihu.com/p/349182248)
  * [LLVM IR入门指南](https://github.com/Evian-Zhang/llvm-ir-tutorial)
  * [Clang/LLVM 从入门到实践](https://lvchenqiang.github.io/2019/02/01/Clang-LLVM/)
  * [Valgrind官网](https://valgrind.org/)
  * [angr中定义的VEX-IR](https://github.com/angr/vex/blob/master/pub/libvex_ir.h)
  * [angr中的pyvex文档](https://angr.io/api-doc/pyvex.html)
  * [angr的IR官方文档](https://docs.angr.io/advanced-topics/ir)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ZERO-A-ONE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231591](/post/id/231591)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [符号执行](/tag/符号执行)
  * [angr](/tag/angr)
  * [源码解析](/tag/源码解析)

 **+1** __8赞

 __收藏

![](https://p0.ssl.qhimg.com/t01a8f8240d1801aeee.png) ZERO-A-ONE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

