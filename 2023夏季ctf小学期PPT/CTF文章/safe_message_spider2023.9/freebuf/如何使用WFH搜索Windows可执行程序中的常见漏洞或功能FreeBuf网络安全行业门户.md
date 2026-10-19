![](https://image.3001.net/images/20210722/1626925808_60f8eaf0654dce08b4b4f.jpg!small)

## 关于WFH

WFH，全名为Windows Feature
Hunter，即Windows功能搜索工具，该工具基于Python开发，使用Frida实现其功能，可以帮助广大研究人员搜索和识别Windows可执行程序中的常见安全漏洞以及功能。当前版本的WFH能够自动识别动态链接库DLL中潜在的侧加载问题以及组件对象模型COM中劫持攻击的实现可能。

DLL侧加载利用勒Windows中WinSXS程序集来从SXS列表中加载恶意DLL文件。COM劫持将允许攻击者置入恶意代码，而这些代码将能够通过劫持COM引用和关系代替合法软件的执行。

WFH可以输出潜在的安全漏洞，并将目标Windows可执行文件中的潜在漏洞相关信息写入至CSV文件中。

## 工具安装

首先， 广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ConsciousHacker/WFH

然后运行下列命令安装和配置相关依赖组件：

    
    
    pip install -r requirements.txt

## 工具帮助信息

    
    
    PS C:\Tools\WFH > python .\wfh.py -h
    
    usage: wfh.py [-h] -t T [T ...] -m {dll,com} [-v] [-timeout TIMEOUT]
    
     
    
    Windows Feature Hunter
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -t T [T ...], -targets T [T ...]
    
                            list of target windows executables
    
      -m {dll,com}, -mode {dll,com}
    
                            vulnerabilities to potentially identify
    
      -v, -verbose          verbose output from Frida instrumentation
    
      -timeout TIMEOUT      timeout value for Frida instrumentation
    
     
    
    EXAMPLE USAGE
    
        NOTE: It is recommended to copy target binaries to the same directory as wfh for identifying DLL Sideloading
    
     
    
        DLL Sideloading Identification (Single):        python wfh.py -t .\mspaint.exe -m dll
    
        DLL Sideloading Identification (Verbose):       python wfh.py -t .\mspaint.exe -m dll -v
    
        DLL Sideloading Identification (Timeout 30s):   python wfh.py -t .\mspaint.exe -m dll -timeout 30
    
        DLL Sideloading Identification (Wildcard):      python wfh.py -t * -m dll
    
        DLL Sideloading Identification (List):          python wfh.py -t .\mspaint.exe .\charmap.exe -m dll
    
     
    
        COM Hijacking Identification (Single):          python wfh.py -t "C:\Program Files\Internet Explorer\iexplore.exe" -m com
    
        COM Hijacking Identification (Verbose):         python wfh.py -t "C:\Program Files\Internet Explorer\iexplore.exe" -m com -v
    
        COM Hijacking Identification (Timeout 60s):     python wfh.py -t "C:\Program Files\Internet Explorer\iexplore.exe" -m com -timeout 60
    
        COM Hijacking Identification (Wildcard):        python wfh.py -t * -m com -v
    
    COM Hijacking Identification (List):            python wfh.py -t "C:\Program Files\Internet Explorer\iexplore.exe" "C:\Windows\System32\notepad.exe" -m com -v

## 工具使用

### DLL侧加载识别

首先，我们需要将需要分析的代码拷贝至WFH工具所在的目录下，然后按照下列命令执行扫描分析：

    
    
    PS C:\Tools\WFH > copy C:\Windows\System32\mspaint.exe .
    
    PS C:\Tools\WFH > copy C:\Windows\System32\charmap.exe .
    
    PS C:\Tools\WFH > dir
    
     
    
     
    
        Directory: C:\Tools\WFH
    
     
    
     
    
    Mode                 LastWriteTime         Length Name
    
    ----                 -------------         ------ ----    
    d-----         5/14/2021   2:12 PM                .vscode
    
    -a----          5/6/2021   2:39 PM           1928 .gitignore
    
    -a----         12/7/2019   2:09 AM         198656 charmap.exe
    
    -a----         5/18/2021   7:39 AM           6603 loadlibrary.js
    
    -a----          4/7/2021  12:48 PM         988160 mspaint.exe
    
    -a----         5/18/2021   7:53 AM           8705 README.md
    
    -a----         5/17/2021  11:27 AM           5948 registry.js
    
    -a----          5/6/2021   2:41 PM             11 requirements.txt
    
    -a----         5/18/2021   8:35 AM          10623 wfh.py

接下来，我们就可以使用WFH来对目标代码进行分析，并尝试识别其中的DLL侧加载机会：

    
    
    PS C:\Tools\WFH > python .\wfh.py -t * -m dll
    
    ==================================================
    
    Running Frida against charmap.exe
    
    --------------------------------------------------    
            [+] Potential DllMain Sideloading: LoadLibraryW,LPCWSTR: MSFTEDIT.DLL
    
            [+] Potential DllMain Sideloading: LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE
    
     
    
    [*] Writing raw Frida instrumentation to charmap.exe-raw.log
    
    [*] Writing Potential DLL Sideloading to charmap.exe-sideload.log
    
    --------------------------------------------------    
    ==================================================
    
    Running Frida against mspaint.exe
    
    --------------------------------------------------    
            [+] Potential DllMain Sideloading: LoadLibraryExW,LPCWSTR : gdiplus.dll, dwFlags : NONE
    
            [-] Potential DllExport Sideloading: GetProcAddress,hModule : C:\WINDOWS\WinSxS\amd64_microsoft.windows.gdiplus_6595b64144ccf1df_1.1.19041.789_none_faf0a7e97612e7bb\gdiplus.dll, LPCSTR: GdiplusStartup
    
            [+] Potential DllMain Sideloading: LoadLibraryW,LPCWSTR: MSFTEDIT.DLL
    
            [+] Potential DllMain Sideloading: LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE
    
     
    
    [*] Writing raw Frida instrumentation to mspaint.exe-raw.log
    
    [*] Writing Potential DLL Sideloading to mspaint.exe-sideload.log
    
    --------------------------------------------------    
    ==================================================
    
    [*] Writing dll results to dll_results.csv
    
     
    
    PS C:\Tools\WFH > type .\dll_results.csv
    
    Executable,WinAPI,DLL,EntryPoint / WinAPI Args
    
    charmap.exe,LoadLibraryW,LPCWSTR: MSFTEDIT.DLL
    
    charmap.exe,LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE
    
    mspaint.exe,LoadLibraryExW,LPCWSTR : gdiplus.dll, dwFlags : NONE
    
    mspaint.exe,GetProcAddress,hModule : C:\WINDOWS\WinSxS\amd64_microsoft.windows.gdiplus_6595b64144ccf1df_1.1.19041.789_none_faf0a7e97612e7bb\gdiplus.dll, LPCSTR: GdiplusStartup
    
    mspaint.exe,LoadLibraryW,LPCWSTR: MSFTEDIT.DLL
    
    mspaint.exe,LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE

如果你想让WFH输出更多详细内容，可以使用“-v”参数开启Verbose模式。此时将能够查看Windows API调用的详细情况：

    
    
    PS C:\Tools\WFH > python .\wfh.py -t * -m dll -v
    
    ==================================================
    
    Running Frida against charmap.exe
    
    {'type': 'send', 'payload': 'LoadLibraryW,LPCWSTR: MSFTEDIT.DLL'}
    
    {'type': 'send', 'payload': 'LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE'}
    
    --------------------------------------------------    
            [+] Potential DllMain Sideloading: LoadLibraryW,LPCWSTR: MSFTEDIT.DLL
    
            [+] Potential DllMain Sideloading: LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE
    
     
    
    [*] Writing raw Frida instrumentation to charmap.exe-raw.log
    
    [*] Writing Potential DLL Sideloading to charmap.exe-sideload.log
    
    --------------------------------------------------    
    ==================================================
    
    Running Frida against mspaint.exe
    
    {'type': 'send', 'payload': 'LoadLibraryExW,LPCWSTR : gdiplus.dll, dwFlags : NONE'}
    
    {'type': 'send', 'payload': 'GetProcAddress,hModule : C:\\WINDOWS\\WinSxS\\amd64_microsoft.windows.gdiplus_6595b64144ccf1df_1.1.19041.789_none_faf0a7e97612e7bb\\gdiplus.dll, LPCSTR: GdiplusStartup'}
    
    {'type': 'send', 'payload': 'LoadLibraryW,LPCWSTR: MSFTEDIT.DLL'}
    
    {'type': 'send', 'payload': 'LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE'}
    
    --------------------------------------------------    
            [+] Potential DllMain Sideloading: LoadLibraryExW,LPCWSTR : gdiplus.dll, dwFlags : NONE
    
            [-] Potential DllExport Sideloading: GetProcAddress,hModule : C:\WINDOWS\WinSxS\amd64_microsoft.windows.gdiplus_6595b64144ccf1df_1.1.19041.789_none_faf0a7e97612e7bb\gdiplus.dll, LPCSTR: GdiplusStartup
    
            [+] Potential DllMain Sideloading: LoadLibraryW,LPCWSTR: MSFTEDIT.DLL
    
            [+] Potential DllMain Sideloading: LoadLibraryExW,LPCWSTR : MSFTEDIT.DLL, dwFlags : NONE
    
     
    
    [*] Writing raw Frida instrumentation to mspaint.exe-raw.log
    
    [*] Writing Potential DLL Sideloading to mspaint.exe-sideload.log
    
    --------------------------------------------------    
    ==================================================
    
    [*] Writing dll results to dll_results.csv

### COM劫持识别

    
    
    PS C:\Tools\WFH > python .\wfh.py -t "C:\Program Files\Internet Explorer\iexplore.exe" -m com
    
    ==================================================
    
    Running Frida against C:\Program Files\Internet Explorer\iexplore.exe
    
    --------------------------------------------------    
            [+] Potential COM Hijack: Path : HKEY_LOCAL_MACHINE\Software\Classes\CLSID\{0E5AAE11-A475-4C5B-AB00-C66DE400274E}\InProcServer*32,lpValueName : null,Type : REG_EXPAND_SZ, Value : %SystemRoot%\system32\Windows.Storage.dll
    
            [+] Potential COM Hijack: Path : HKEY_CLASSES_ROOT\CLSID\{1FD49718-1D00-4B19-AF5F-070AF6D5D54C}\InProcServer*32,lpValueName : null,Type : REG_SZ, Value : C:\Program Files (x86)\Microsoft\Edge\Application\90.0.818.62\BHO\ie_to_edge_bho_64.dll
    
     
    
    [*] Writing raw Frida instrumentation to .\iexplore.exe-raw.log
    
    [*] Writing Potential COM Hijack to .\iexplore.exe-comhijack.log
    
    --------------------------------------------------    
    ==================================================
    
    [*] Writing dll results to comhijack_results.csv

## 工具使用样例

### 原生Windows签名代码

将所有的原生Windows签名代码拷贝至WFH脚本所在目录：

    
    
    Get-ChildItem c:\ -File | ForEach-Object { if($_ -match '.+?exe$') {Get-AuthenticodeSignature $_.fullname} } | where {$_.IsOSBinary} | ForEach-Object {Copy-Item $_.path . }

### 搜索DLL侧加载机会

    
    
    python wfh.py -t * -m dll

### 搜索COM劫持机会

    
    
    python wfh.py -t * -m com

## 项目地址

 **WFH：** 【[ _GitHub传送门_](https://github.com/ConsciousHacker/WFH)】

