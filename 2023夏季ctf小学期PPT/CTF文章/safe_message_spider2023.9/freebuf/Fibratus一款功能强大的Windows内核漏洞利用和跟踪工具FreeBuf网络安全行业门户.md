**今天给大家介绍的是一款名叫Fibratus的开源工具，广大研究人员可以使用这款功能强大的工具来进行Windows内核漏洞利用、挖掘与跟踪。**

![Fibratus：一款功能强大的Windows内核漏洞利用和跟踪工具](https://image.3001.net/images/20190309/1552066667_5c82a86b77516.jpg!small)

Fibratus这款工具能够[捕捉](https://www.kitploit.com/search/label/Capture)到绝大多数的[Windows](https://www.kitploit.com/search/label/Windows)[内核](https://www.kitploit.com/search/label/Kernel)活动-进程/线程创建和终止，上下文转换，文件系统I/O，寄存器，网络活动以及[DLL](https://www.kitploit.com/search/label/DLL)加载/卸载等等。除此之外，所有的内核事件可以直接以AMQP消息、Elasticsearch簇或标准输出流的形式提供给用户。大家可以使用filaments（一款轻量级Python模块）来根据自己的需要去扩展Fibratus的功能，这也是Python生态系统给大家提供的便利之处。

## 工具安装

点击【[这里](https://github.com/rabbitstack/fibratus/releases/download/v0.7.2/fibratus-0.7.2.exe)】下载Fibratus的最新版本（Windows安装包）。工具的修改日志和旧版本可以点击【[这里](https://github.com/rabbitstack/fibratus/releases)】获取。

### 安装依赖组件

1、 下载并安装Python
3.4【[下载地址](https://www.python.org/ftp/python/3.4.0/python-3.4.0.amd64.msi)】；

2、 安装Visual Studio 2015（你只需要Visual
C编译器来构建kstreamc扩展），确保环境变量VS100COMNTOOLS指向的是“%VS140COMNTOOLS%”。

3、 获取Cython：

    
    
    pip install Cython >=0.23.4

通过pip包管理器安装fibratus：

    
    
    pip install fibratus

## 工具运行

大家可以运行命令“fibratus --help”来获取使用帮助信息：

    
    
    Usage:
        fibratus run ([--filament=<filament>]| [--filters <kevents>...]) [--no-enum-handles] [--cswitch]
        fibratus list-kevents
        fibratus list-filaments
        fibratus -h | --help
        fibratus --version
     
    Options:
        -h --help                 Show this screen.
        --filament=<filament>     Specify the filament to execute.
        --no-enum-handles         Avoids enumerating the system handles.
        --cswitch                 Enables context switch kernelevents.
    --version                 Show version.

运行命令fibratus run（无需任何参数），可直接捕捉到所有支持的内核事件，控制器初始化完成之后，捕捉到的内核事件会持续输出并呈现给用户：

    
    
    555020:28:14.882000 3 cmd.exe (4396) - UnloadImage (base=0x77950000,checksum=1313154, image=ntdll.dll,path=\Device\HarddiskVolume2\Windows\SysWOW64\ntdll.dll, pid=4396, size=1536.0)
    555120:28:14.882000 3 erl.exe (2756) - TerminateProcess(comm=C:\Windows\system32\cmd.exe /cdir /-C /Wc:/Users/Nedo/AppData/Roaming/RabbitMQ/db/rabbit@NEDOPC-mnesia,exe=C:\Windows\system32\cmd.exe, name=cmd.exe, pid=4396, ppid=2756)
    555220:28:14.882000 3 erl.exe (2756) - CloseFile(file=\Device\HarddiskVolume2\Windows, tid=1672)
    563120:28:17.286000 2 taskmgr.exe (3532) - RegQueryKey(hive=REGISTRY\MACHINE\SYSTEM, key=ControlSet001\Control\Nls\Locale, pid=3532,status=0, tid=4324)
    563220:28:17.286000 2 taskmgr.exe (3532) - RegOpenKey(hive=REGISTRY\MACHINE\SYSTEM,key=ControlSet001\Control\Nls\Locale\Software\Microsoft\DirectUI, pid=3532,status=3221225524, tid=4324)
    563320:28:17.288000 2 taskmgr.exe (3532) - CreateFile(file=\Device\HarddiskVolume2\Windows\system32\xmllite.dll,file_type=REPARSE_POINT, operation=OPEN, share_mask=rwd, tid=4324)
    563420:28:17.288000 2 taskmgr.exe (3532) - CloseFile(file=\Device\HarddiskVolume2\Windows\system32\xmllite.dll, tid=4324)
    563520:28:17.288000 2 taskmgr.exe (3532) - CreateFile(file=\Device\HarddiskVolume2\Windows\system32\xmllite.dll, file_type=FILE,operation=OPEN, share_mask=r-d, tid=4324)
    563620:28:17.288000 2 taskmgr.exe (3531) - LoadImage (base=0x7fefab90000,checksum=204498, image=xmllite.dll, path=\Windows\System32\xmllite.dll,pid=3532, size=217088)
    563720:28:17.288000 2 taskmgr.exe (3532) - CloseFile(file=\Device\HarddiskVolume2\Windows\system32\xmllite.dll, tid=4324)
    563820:28:17.300000 2 taskmgr.exe (3532) - RegQueryKey (hive=REGISTRY\MACHINE\SYSTEM,key=ControlSet001\Control\Nls\Locale\, pid=3532, status=0, tid=4324)
    563920:28:17.300000 2 taskmgr.exe (3532) - RegOpenKey(hive=REGISTRY\MACHINE\SYSTEM,key=ControlSet001\Control\Nls\Locale\SOFTWARE\Microsoft\CTF\KnownClasses,pid=3532, status=3221225524, tid=4324)
    564020:28:17.300000 3 taskmgr.exe (3532) - RegQueryKey(hive=REGISTRY\MACHINE\SYSTEM, key=ControlSet001\Control\Nls\Locale\, pid=3532,status=0, tid=4324)
    564120:28:17.300000 3 taskmgr.exe (3532) - RegOpenKey (hive=REGISTRY\MACHINE\SYSTEM,key=ControlSet001\Control\Nls\Locale\SOFTWARE\Microsoft\CTF\KnownClasses,pid=3532, status=3221225524, tid=4324)
    564220:28:17.302000 2 taskmgr.exe (3532) - UnloadImage (base=0x7fefab90000,checksum=204498, image=xmllite.dll, path=\Windows\System32\xmllite.dll,pid=3532, size=212.0)

注意：按下Ctrl+C即可停止Fibratus运行。

## 项目地址

Fibratus：【[GitHub传送门](https://github.com/rabbitstack/fibratus)】

### 参考文档

【[Wiki传送门](https://github.com/rabbitstack/fibratus/wiki/Running)】

 ***
参考来源：[fibratus](https://github.com/rabbitstack/fibratus)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

