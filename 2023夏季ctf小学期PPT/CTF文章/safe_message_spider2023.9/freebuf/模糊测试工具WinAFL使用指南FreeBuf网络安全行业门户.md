## 一、简介  

 **WinAFL 是一款流行的基于 Windows 平台下的半自动二进制文件格式模糊测试工具，属于 AFL 大家族中的一员，早期的 AFL
测试工具多半是基于 Linux，并不支持 Windows，所以 WinAFL 弥补了这一空白，当然现在越来越多的 AFL 以及其他模糊测试工具适用于
Windows 平台。**

WinAFL 的原理和其他的模糊测试工具类似，通过对程序输入的数据进行变异处理，观察程序在处理这些变异数据是否会产生 Crash，以此来验证程序是否有
Bug。但是相对于其它模糊测试工具来说则更为智能，因为它会通过进化算法不停的改变程序输入的数据，并且结合程序的覆盖率以进行下一步操作。并且运行的速度越快，效果越明显（天下武功，无坚不破，唯快不破）。  

![afl-fuzz.gif](https://image.3001.net/images/20191011/1570805224_5da095e80edfb.gif!small)

> WinAFL 项目地址：<https://github.com/ivanfratric/winafl>
>
> DynamoRIO 项目地址：<https://github.com/DynamoRIO/dynamorio/wiki/Downloads>

## 二、WinAFL 原理及使用（挑了几个重要的）

### 使用 DynamoRIO 进行二进制插桩

WinAFL 的使用非常简单，首先需要了解的是二进制插桩工具
DynamoRIO，它的功能非常的多，在这里主要用它来分析代码的覆盖率，也就是程序运行时会执行哪些汇编代码块。命令如下所示，-t drcov
表示使用代码覆盖率模块，xmlvalidate.exe 表示需要测试的软件，nn-valid.xml 表示生成的结果文件。

    
    
    E:\DynameRIO-7.0.0\bin32\drrun.exe -t drcov -- xmlvalidate.exe nn-valid.xml

命令执行结束之后，会在当前目录中产生 nn-valid.xml 文件，之后在 IDA 中打开它即可显示 xmlvalidate.exe
的代码覆盖率，这里需要用到 lighthouse IDA 插件或者是 Qt5 的界面。

![image.png](https://image.3001.net/images/20191012/1570885407_5da1cf1f455d9.png!small)

如下图所示可以看出被测试软件部分函数的代码覆盖率及块命中次数。

![image.png](https://image.3001.net/images/20191012/1570885413_5da1cf25a4361.png!small)

当然也可以显示函数执行的流程，白色区域表示未执行的部分。

![image.png](https://image.3001.net/images/20191012/1570885550_5da1cfae9d4a0.png!small)

### 使用 winafl-cmin.py 进行案例最小化处理

如下图所示，该命令主要是为对输入的样本文件进行最小化处理，以用来提高 WinAFL 的执行效率。命令如下，--working-dir 表示 winafl
命令文件夹的路径，-D 表示插桩工具 DynamoRIO 的命令文件夹路径（如果测试程序是 32 位的就用 bin32，反之则用 bin64），-i
表示需要筛选的测试用例存放目录，-o 表示将筛选过后的测试用例的存放目录，-coverage_module
表示需要覆盖的模块（如果不需要覆盖其他模块的话就填写为当前模块 xmlvalidate.exe），-target_module
表示被测模块，-target_method 表示被测模块函数的地址（也可以用偏移量 -target_offset
表示），最后就是参数的个数和程序的路径，@@ 引用 -i 参数的中的测试用例。

    
    
    E:\winafl\python winafl-cmin.py --working-dir E:\winafl\bin32 
                                    -D E:\DynamoRIO-7.0.0\bin32
                                    -t 100000
                                    -i E:\xml_fuzz\samples
                                    -o E:\minset_xml
                                    -coverage_module msxml6.dll
                                    -target_module xmlvalidate.exe
                                    -target_method fuzzme [-target_offset 0x1000]
                                    -nargs 2 -- E:\xml_fuzz\xmlvalidate.exe @@

### 使用 afl-fuzz.exe 命令执行模糊测试

命令如下，-i 表示输入的测试文件用例，-o 是输出结果的目录，-fuzz_iterations 表示迭代的次数，其他参数和上面的意思是一样的。

    
    
    E:\winafl\bin32\afl-fuzz.exe -i E:\minset_xml
                                 -o E:\xml\results
                                 -D E:\DynamoRIO-7.0.0\bin32
                                 -t 20000
                                 -- -coverage_module MSXML6.dll
                                 -fuzz_iterations 5000
                                 -target_module xmlvalidate.exe
                                 -target_method fuzzme
                                 -nargs 2 -- E:\xml_fuzz\xmlvalidate.exe @@
    

当使用 afl-fuzz.exe 进行模糊测试时，会在 -o 参数指定的目录下生成如下几个文件夹，其中 crashes 文件夹保存着会导致崩溃的测试用例。

![image.png](https://image.3001.net/images/20191012/1570888118_5da1d9b6c69f3.png!small)

## 三、举个栗子

以图像软件为例子，图像软件会以图片作为软件的输入，使用 WinAFL
变异输入数据来查看软件是否会崩溃。那么使用什么图像软件来进行模糊测试呢？经过百度的搜索，觉得 ABC 看图这个软件不错，就以它为例子吧。

![image.png](https://image.3001.net/images/20191012/1570888492_5da1db2cebe91.png!small)

在下载了 ABC 看图之后，发现该软件只有一个根目录，然后通过查看动态函数库的信息，发现 FreeImage.dll 和 FreeImage64.dll
可能为解析图片的动态链接库。经过搜索之后发现这是一个开源项目，该项目是用来专门解析图片格式的，并且已经有五年的历史了。  
![image.png](https://image.3001.net/images/20191012/1570889410_5da1dec2eb57a.png!small)  
![image.png](https://image.3001.net/images/20191012/1570888755_5da1dc338104b.png!small)

从程序的输入中也可以发现对图片的处理和 FreeImage.dll 有关。

![image.png](https://image.3001.net/images/20191012/1570889872_5da1e090d74a0.png!small)  
因为这个是开源项目，所以顺便查一下这个项目历史上是否有漏洞存在，通过显示的信息发现该项目在 15、17、19
年都有漏洞被发现，利用价值最大的还是一个堆溢出，但是确实堆溢出非常难利用，但是漏洞的出现确实表明存在潜在漏洞的可能性非常的大。

![image.png](https://image.3001.net/images/20191012/1570889161_5da1ddc961ff2.png!small)![image.png](https://image.3001.net/images/20191012/1570889163_5da1ddcbc77fd.png!small)使用
windbg 下断点命令，命令如下，目的是查看 ABC 软件调用了 FreeImage 函数库中的哪些函数。

    
    
    bm FreeImage!* ".echo ; kb 1; gc"

![image.png](https://image.3001.net/images/20191012/1570890317_5da1e24d5735e.png!small)由于显示的数目太多，所以将输入保存到了文件中，之后编写了一个
python 脚本将重复的调用函数删除后得到以下结果，可以看出调用了相当多的 Get 函数去获取图片的信息，由于我输入的图片是 jpg
格式，所以还不包含元标签解析。

    
    
    import os
    
    files = []
    filelist = os.listdir(".")
    for file in filelist:
    
    	if file.split(".")[-1] == "txt":
    
    		output = []
    		with open(file, "r") as data_output:
    			with open(file.split(".")[0]+"OUT.txt", "w") as data_input:
    				
    				for line in data_output:
    					if line != "\n" and line.split()[-1][0:4] == "Free" and line.split()[-1] not in output:
    							print line.split()[-1]
    							output.append(line.split()[-1])
    
    				for linedata in output:
    					data_input.write(linedata+"\n")
      
    

![image.png](https://image.3001.net/images/20191012/1570890547_5da1e3336a227.png!small)

根据显示的结果，我对其中的一些函数进行了调试，发现基本上所有获取图片信息的函数都会用到 FreeImage_LoadU 的返回值，并且
FreeImage_LoadU 之中也会调用相当多的获取图片信息的函数，由此判断 FreeImage_LoadU 可能是提取图片信息的重要函数。如下图所示
FreeImage_LoadU 函数的第二个参数为加载图片的路径。

![image.png](https://image.3001.net/images/20191012/1570891209_5da1e5c9343ce.png!small)下面开始针对
FreeImage_LoadU 函数编写测试程序。测试文件源码如下所示，其中 FreeImage_Initialise 函数用于初始化 FreeImage
库，FreeImage_LoadU 的第一个参数由 FreeImage_GetFileTypeU 获取，表明为图片的类型，经过调试 jpg 图片的返回值为
2。为了让 WinAFL 更快的执行，我将 GetProcAddress 函数放到了 FreeImage_test
函数之外的地方执行，并且将它的返回值设置为全局变量，这样的话只需要模糊测试 FreeImage_test 函数即可，不必要测试整个程序，这会让速度提升至
400% 左右，是非常可观的。

    
    
    #define _CRT_SECURE_NO_WARNINGS
    #include <windows.h> 
    #include <tchar.h>
    #include <iostream>
    using namespace std;
    
    extern "C" __declspec(dllexport) int main(int argc, char** argv);
    void FreeImage_test(HINSTANCE hinstLib, wchar_t* pathfile);
    wchar_t* charToWChar(const char* text);
    
    typedef DWORD(__stdcall *FreeImage_GetFileTypeU)(const wchar_t* lpszPathName, int flag);
    typedef DWORD(__stdcall *FreeImage_Initialise)(BOOL load_local_plugins_only);
    typedef DWORD(__stdcall *FreeImage_DeInitialise)();
    typedef DWORD(__stdcall *
    )(DWORD format, const wchar_t* lpszPathName, int flag);
    typedef DWORD(__stdcall *FreeImage_UnLoad)(DWORD dib);
    
    FreeImage_Initialise Initialise;
    FreeImage_GetFileTypeU LoadFileType;
    FreeImage_LoadU LoadU; DWORD load;
    FreeImage_UnLoad UnLoad;
    FreeImage_DeInitialise DeInitialise;
    
    int main(int argc, char** argv)
    {
    	if (argc < 2) {
    		printf("Usage: %s <xml file>\n", argv[0]);
    		return 0;
    	}
    	
    	wchar_t* PathName = charToWChar(argv[1]);
    
    	HINSTANCE hinstLib; BOOL fFreeResult, fRunTimeLinkSuccess = FALSE; DWORD Error = NULL;
    	hinstLib = LoadLibrary(TEXT("E:\\FreeImage.dll"));
    
    	if (hinstLib != NULL)
    	{
    		fRunTimeLinkSuccess = TRUE;
    		
    		Initialise = (FreeImage_Initialise)GetProcAddress(hinstLib, (LPCSTR)163); // 初始化 FreeImage 库
    		LoadFileType = (FreeImage_GetFileTypeU)GetProcAddress(hinstLib, (LPCSTR)126);// 获取位图文件类型
    		LoadU = (FreeImage_LoadU)GetProcAddress(hinstLib, (LPCSTR)181);	// 加载位图
    		UnLoad = (FreeImage_UnLoad)GetProcAddress(hinstLib, (LPCSTR)242);// 卸载位图
    		DeInitialise = (FreeImage_DeInitialise)GetProcAddress(hinstLib, (LPCSTR)83);//卸载 FreeImage 库
    		
    		FreeImage_test(hinstLib, PathName);
    		fFreeResult = FreeLibrary(hinstLib);
    	}
    
    	if (!fRunTimeLinkSuccess)
    		cout << "加载函数失败, Error: " << Error << endl;
    	return 0;
    }
    
    void FreeImage_test(HINSTANCE hinstLib, wchar_t* pathfile)
    {
    	(Initialise)(FALSE);
    	DWORD FileType = (LoadFileType)(pathfile, 0);
    	load = (LoadU)(FileType, pathfile, 0);
    	(UnLoad)(load);
    	(DeInitialise)();
    }
    
    wchar_t* charToWChar(const char* text)
    {
    	size_t size = strlen(text) + 1;
    	wchar_t* wa = new wchar_t[size];
    	mbstowcs(wa, text, size);
    	return wa;
    }  
    

测试程序编译之后，便开始模糊测试的第一步，使用如下命令测试 WinAFL 是否可以正常使用。-debug 表示设置为调试模式。

    
    
    E:\winafl\bin32>E:\DynamoRIO-7.0.0\bin32\drrun.exe -c winafl.dll -debug -coverage_module FreeImage.dll -target_module test.exe -target_method main -fuzz_iterations 10 -nargs 2 -- E:\test.exe E:\1.jpg

如下图所示，日志文件当中模块加载正常并没有错误显示。

![image.png](https://image.3001.net/images/20191012/1570892437_5da1ea95723b6.png!small)下一步用如下命令筛选测试用例文件。测试用例文件是从网络上搜集的，包含
tiff、png、bmp、ico 等格式。

    
    
    E:\winafl>python winafl-cmin.py --working-dir E:\winafl\bin32 -D E:\DynamoRIO-7.0.0\bin32 -t 100000 -i E:\ImageFormat\all -o E:\out -coverage_module FreeImage.dll -target_module test.exe -target_method main -nargs 2 -- E:\test.exe @@

![image.png](https://image.3001.net/images/20191012/1570892720_5da1ebb089eaa.png!small)筛选过后的测试用例文件如下图所示，确实少了很多，这一步也会显著的提高
WinAFL 的执行速度。

![image.png](https://image.3001.net/images/20191012/1570893374_5da1ee3e624fc.png!small)最后一步，使用如下命令开始模糊测试！！！

    
    
    E:\winafl\bin32>afl-fuzz.exe -i E:\out -o E:\result -D E:\DynamoRIO-7.0.0\bin32 -t 20000 -- -coverage_module FreeImage.dll -target_module test.exe -target_offset 0x1572 -fuzz_iterations 5000 -nargs 2 -- E:\test.exe @@

经过大概五个小时的模糊测试之后，发现了 21 个导致程序 Crash 的 Bug，并且挂起计数为 16。速度方面，平均 153.4
次每秒，其实高峰值达到了1500 次左右，效果还是可以的。

![image.png](https://image.3001.net/images/20191013/1570960408_5da2f4188a7fd.png!small)

Crash 文件夹中存放着崩溃的案例，其实这些之中由许多是相同的，需要用到 BugId 工具去做进一步筛选。

![image.png](https://image.3001.net/images/20191013/1570964655_5da304afcb4ee.png!small)

使用 ABC 软件载入其中一个崩溃案例，发现程序未响应，至于堆栈分析限于篇幅这里就不写了。

![image.png](https://image.3001.net/images/20191013/1570964662_5da304b638ac1.png!small)

## 四、WinAFL 的技巧及错误纠察

### 关于 WinAFL 软件使用中的错误

刚接触这款 Fuzz
工具的时候，它的命令行参数确实多的吓人，这使我足足花了一周的时间去搞清楚了这个软件的各种怪异的错误以及使用的方法和技巧，这里我分享出来，以便使你可以愉快的使用
WinAFL 进行模糊测试。首先是 afl-fuzz.exe 命令，这个命令的参数有很多，其中 -o 参数所指向的文件夹必须是不存在的，因为 WinAFL
会自动建立，不然会报错。-D 参数所指向的二进制插桩工具的路径必须和当前版本的 winafl.dll 版本所匹配，这也是我为什么不用 7.1 而选用 7.0
的原因，而且传入的是 bin32 文件夹的路径而不是 bin32\drrun.exe。还有就是要想使用 -target_method
必须能够查到符号，不然白搭；要想使用 -target_offset 必须为函数的地址，比如
0x1547，多一个少一个都不行。-coverage_module 参数必须在测试文件中包含，也就是使用 -debug
调试所生成的文件中载入的模块。最后就是 -t 参数必须要有，每次我都忘了。反正记住一点，WinAFL 使用中的绝大多数错误和你输入的参数有关。

### 关于 WinAFL 软件使用中的技巧

相比以前的手工挖掘漏洞，工具挖掘漏洞的好处就是快，如果你使用 WinAFL 只有 0.1 次每秒的速度，那你还用它干什么。提升 WinAFL
的执行速度有很多种方法，除了更改源码之外（我可不想花时间去更改源码，只想等着作者更新）最常用的方法就是编写更高效的测试文件，比如上面的测试文件，我将
GetProcAddress 函数放到了 FreeImage_test
函数之外执行，这样就不需要每次都执行一边，也就是说将不怎么重要且浪费时间的代码统统写到测试函数之外的地方。不常用的方法就是修改实例文件（-i
参数），这一点真的非常的重要，实例文件的大小会严重影响 WinAFL 的运行速度，比如使用 154 字节的图片作为实例文件输入比使用 4MB
的实例文件输入要快得多。

最后就是衡量 WinAFL 是否正常运行的一个标准。以下图为例，第一个就是 exec speed，少于 20 次每秒算慢的（zzzzz...），60
次左右每秒算中等（slow），正常是 100 次左右每秒，越快模糊测试效率越高。第二个是 fuzzing strategy yields
板块，这个表示样本变异的计数，数字计数越大表示越模糊，如果你执行了 10 多个小时还显示为 0 的话，就要考虑考虑是哪一流程设置错了。

![image.png](https://image.3001.net/images/20191013/1570967046_5da30e06d3ac6.png!small)

 ***本文原创作者：护花使者cxy，本文属FreeBuf原创奖励计划，未经许可禁止转载**

