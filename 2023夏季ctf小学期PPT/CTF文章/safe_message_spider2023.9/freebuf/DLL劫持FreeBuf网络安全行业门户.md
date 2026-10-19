  

# DLL劫持

## 1.DLL介绍

DLL(Dynamic Link
Library)文件为动态链接库文件，又称"应用程序拓展"，是软件文件类型。在Windows中，许多应用程序并不是一个完整的可执行文件，它们被分割成一些相对独立的动态链接库，即DLL文件，放置于系统中。当我们执行某一个程序时，相应的DLL文件就会被调用。一个应用程序可使用多个DLL文件，一个DLL文件也可能被不同的应用程序使用，这样的DLL文件被称为共享DLL文件。

## 2.DLL劫持原理

 **Windows xp sp2之前**

Windows查找DLL的目录以及对应的顺序：

  1. 进程对应的应用程序所在目录；

  2. 当前目录（Current Directory）；

  3. 系统目录（通过 GetSystemDirectory 获取）；

  4. 16位系统目录；

  5. Windows目录（通过 GetWindowsDirectory 获取）；

  6. PATH环境变量中的各个目录；

 **Windows xp sp2之后**

Windows查找DLL的目录以及对应的顺序（SafeDllSearchMode 默认会被开启）：

默认注册表为：HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session
Manager\SafeDllSearchMode，其键值为1

  1. 进程对应的应用程序所在目录（可理解为程序安装目录比如C:\ProgramFiles\uTorrent）

  2. 系统目录（即%windir%system32）；

  3. 16位系统目录（即%windir%system）；

  4. Windows目录（即%windir%）；

  5. 当前目录（运行的某个文件所在目录，比如C:\Documents and Settings\Administrator\Desktop\test）；

  6. PATH环境变量中的各个目录；

 **Windows7 以上版本**

系统没有了SafeDllSearchMode
而采用KnownDLLs，那么凡是此项下的DLL文件就会被禁止从exe自身所在的目录下调用，而只能从系统目录即SYSTEM32目录下调用，其注册表位置：

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs

那么最终Windows2003以上以及win7以上操作系统通过“DLL路径搜索目录顺序”和“KnownDLLs注册表项”的机制来确定应用程序所要调用的DLL的路径，之后，应用程序就将DLL载入了自己的内存空间，执行相应的函数功能。

  * 默认情况下，如果软件安装在c盘根目录，而不是c:\Program Files，那经过身份验证的用户具有该目录的写权限，另外，perl，python，ruby等软件通常都添加到path变量中。那攻击者可以在当前目录中编写恶意DLL，只要重新运行exe程序就会中招。

  * SafeDllSearchMode + KnownDLLs二者结合可用来防范dll劫持，但是如果调用"不常见"的dll，也就是并未出现在KnownDLLs的列表中，那么无论SafeDllSearchMode是否开启，dll搜索的第一顺序均为程序的当前目录，这里就存在一个DLL劫持漏洞（在程序同级目录下预先放置一个同名dll，在进程启动的过程中会优先加载，实现劫持。

## 3.寻找DLL劫持点

### 方法一（API Monitor）：

以D盾为例，使用API Monitor寻找D盾加载的DLL

![1655951869_62b3d1fd19becdccc6b87.png!small?1655951870414](https://image.3001.net/images/20220623/1655951869_62b3d1fd19becdccc6b87.png!small?1655951870414)

寻找使用相对路径的DLL

![1655951836_62b3d1dc31f1638bcf7ca.png!small?1655951837620](https://image.3001.net/images/20220623/1655951836_62b3d1dc31f1638bcf7ca.png!small?1655951837620)

查看注册表，发现该DLL不在KnownDLLs中，可以被劫持

![1655951812_62b3d1c4a4bdaf01e496b.png!small?1655951813293](https://image.3001.net/images/20220623/1655951812_62b3d1c4a4bdaf01e496b.png!small?1655951813293)

使用rattler提供的可以弹计算器的dll进行验证

![1655951151_62b3cf2f07b621f3f3ddc.png!small](https://image.3001.net/images/20220623/1655951151_62b3cf2f07b621f3f3ddc.png!small)

使用CS生成DLL文件

![1655951404_62b3d02c9613036f992f6.png!small](https://image.3001.net/images/20220623/1655951404_62b3d02c9613036f992f6.png!small)

将生成的DLL文件重命名为cscapi.dll，双击D盾点击上线

![1655951660_62b3d12caf5c352ac1b86.png!small?1655951660934](https://image.3001.net/images/20220623/1655951660_62b3d12caf5c352ac1b86.png!small?1655951660934)

### 方法二（Rattler）：

使用全自动检测工具Rattler来发现DLL劫持：<https://github.com/sensepost/rattler>

注：使用该工具，测试软件路径不能有中文。

如果是目标机器运行者需要劫持的应用程序，需要先kill进程，然后上传需要替换的劫持dll以及源dll，才能完成替换。

Rattler_32.exe "C:\Users\lhc\Desktop\Hacker\d_safe_2.1.5.4\D_Safe_Manage.exe"
1

![1655951794_62b3d1b20b17006663a89.png!small?1655951795106](https://image.3001.net/images/20220623/1655951794_62b3d1b20b17006663a89.png!small?1655951795106)

### 方法三（Windbg Preview+ChkDllHijack）:

![1655951777_62b3d1a18c546d13492b0.png!small?1655951778940](https://image.3001.net/images/20220623/1655951777_62b3d1a18c546d13492b0.png!small?1655951778940)

未成功发现可被劫持的DLL

## 4.DLL免杀

暂时没有比较优雅的解决方案

### 方法一：DLL调用免杀exe

    
    
    // 入口函数
    BOOL WINAPI DllMain(HMODULE hModule, DWORD dwReason, PVOID pvReserved)
    {
      if (dwReason == DLL_PROCESS_ATTACH)
      {
        DisableThreadLibraryCalls(hModule);
      }
      else if (dwReason == DLL_PROCESS_DETACH)
      {
        STARTUPINFO si = { sizeof(si) };
        PROCESS_INFORMATION pi;
        CreateProcess(TEXT("C:\Users\lhc\Desktop\test\test.exe"), NULL, NULL, NULL, false, 0, NULL, NULL, &si, π);
      }
      return TRUE;
    }

![1655951713_62b3d161af85cc59154f4.png!small?1655951714878](https://image.3001.net/images/20220623/1655951713_62b3d161af85cc59154f4.png!small?1655951714878)

### 方法二：拿破仑胎DLL劫持工具（只能过火绒）

  
![1655951556_62b3d0c481072a5839f96.png!small](https://image.3001.net/images/20220623/1655951556_62b3d0c481072a5839f96.png!small)

![1655951731_62b3d173c185a8a0fe710.png!small?1655951732183](https://image.3001.net/images/20220623/1655951731_62b3d173c185a8a0fe710.png!small?1655951732183)  
![1655951621_62b3d105947a19e7fd48d.png!small?1655951621905](https://image.3001.net/images/20220623/1655951621_62b3d105947a19e7fd48d.png!small?1655951621905)

## 5.安装包打包

D盾之类的可以直接打成压缩包发给受害者

如果是安装包格式的可以使用[NSIS制作安装包](https://www.cnblogs.com/modou/p/3573772.html)

## 6.Todo

代码实现比较优雅的DLL免杀

## 参考资料

<https://www.cnblogs.com/swyft/articles/5580342.html>

  

本文作者：深信服深蓝实验室_北京天雄战队

