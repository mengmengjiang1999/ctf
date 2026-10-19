**pe-afl是一款基于了PE二进制和WinAFL上的静态二进制检测的工具，可以用于fuzzWindows应用程序和内核模式驱动程序，而无需源代码或完整符号或硬件支持。**

我用这个工具发现了office,gdiplus,jet,lnk,clfs,cng上的bug。

PE上的仪表部分可以被多种用途重用：

> 1\. 如果你觉得测试速度很慢，你可以在ubuntu上运行这个脚本；
>
> 2\. 该工具基于microsoft二进制文件和visual studio编译的二进制文件，因此在非microsoft编译器上可能会出现故障。

## 操作方法

在calc.exe入口点测量2 NOP的例子：

    
    
    ida.exe demo\calc.exe  
    # 如果pdb可用，则使用pdb加载更可靠  
    ​  
    ​  
    File->script file->ida_dump.py  
    ​  
    python instrument.py -i"{0x1012d6c:'9090'}" demo\calc.exe demo\calc.exe.dump.txt  
    # 0x1012d6c is entry point address, you can instrument from command-line or from __main__ in instrument.py

## 如何fuzz

您必须根据目标实现包装器,并添加你想要的东西，例如page heap等。

### JetDB用于fuzz测试

    
    
    ida.exe demo\msjet40.dll  
    ​  
    File->script file->ida_dump.py  
    ​  
    python pe-afl.py -m demo\msjet40.dll demo\msjet40.dll.dump.txt  
    # msjet40是多线程的，所以使用-m参数

### 在win7上测试JetDB

    
    
    copy /Y msjet40.instrumented.dll C:\Windows\System32\msjet40.dll  
    ​  
    bin\afl-showmap.exe -o NUL -p msjet40.dll -- bin\test_mdb.exe demo\mdb\normal.mdb  
    # 确保能够捕获  
    ​  
    bin\AFL.exe -i demo\mdb -o out -t 5000 -m none -p msjet40.dll -- bin\test_mdb.exe @@

### 模糊测试CLFS

    
    
    ida.exe demo\clfs.sys  
    File->script file->ida_dump.py  
    ​  
    python pe-afl.py demo\clfs.sys demo\clfs.sys.dump.txt

### 在win10上的模糊测试CLFS

    
    
    install_helper.bat  
    disable_dse.bat  
    copy /Y clfs.instrumented.sys C:\Windows\System32\drivers\clfs.sys  
    # reboot if necessary  
          
    bin\afl-showmap.exe -o NUL -p clfs.sys -- bin\test_clfs.exe demo\blf\normal.blf  
    # make sure that capture is OK  
          
    bin\AFL.exe -i demo\blf -o out -t 5000 -m none -p clfs.sys -- bin\test_clfs.exe @@

## 如何追踪

### 示例记录驱动程序执行并导入lighthouse

    
    
    ida.exe demo\clfs.sys  
    File->script file->ida_dump.py  
    ​  
    python pe-afl.py -cb demo\clfs.sys demo\clfs.sys.dump.txt  
    copy /Y clfs.instrumented.sys C:\Windows\System32\drivers\clfs.sys  
    # reboot if necessary  
    ​  
    bin\afl-showmap.exe -o NUL -p clfs.sys -d -- bin\test_clfs.exe demo\blf\normal.blf  
    # output is trace.txt  
    ​  
    python lighthouse_trace.py demo\clfs.sys demo\clfs.sys.mapping.txt trace.txt > trace2.txt  
    ​  
    # install lighthouse  
    xcopy /y /e lighthouse [IDA folder]\plugins\  
    ​  
    ida.exe demo\clfs.sys  
    File->Load File->Code coverage file->trace2.txt

 **参考来源：[github](https://github.com/wmliang/pe-afl)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

