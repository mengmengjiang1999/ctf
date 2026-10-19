![](https://image.3001.net/images/20210427/1619529204_60880df46d9643985f411.png!small)

## 关于TScopy

在事件响应（IR）过程中，研究人员通常需要访问或分析文件系统上的文件。有时这些文件会因为正在使用而被操作系统（OS）锁定，这就很尴尬了。TScopy允许以管理员权限运行的用户通过解析文件系统中的原始位置并在不询问操作系统的情况下复制文件来访问锁定的文件。

当然了，社区还有很多能够执行类似任务的其他工具，比如说RawCopy，而我们的TScopy也是基于该工具开发出来的。然而，RawCopy也有一些缺点，这也是我们开发TScopy的原因，并且提升了工具性能和集成扩展性。

TScopy是一个Python脚本，可以用于解析NTFS
$MFT文件以定位和复制特定文件。通过分析主文件表（MFT），脚本绕过了文件上的操作系统锁。此前的RawCopy是用AutoIT编写的，很难修改，因此我们才决定将RawCopy移植到Python上。

TScopy被设计成可以作为一个独立的程序运行或作为一个python模块导入使用。

## TScopy和RawCopy的区别

TScopy是用Python编写的，并且被组织成类，以使它比AutoIT更易于维护和可读。而AutoIT可能会被反病毒产品标记为恶意组件，因为现在有很多恶意软件已经开始利用它来实现攻击了。

TScopy和RawCopy的主要区别在于每次执行时可以复制多个文件，并且可以缓存文件结构。TScopy提供了下载单个文件、多个逗号分隔文件、目录内容、通配符路径（单个文件或目录）和递归目录的选项。TScopy在迭代目标文件的完整路径时缓存每个目录和文件的位置。然后，它使用此缓存优化对任何其他文件的搜索，确保以后的文件拷贝执行得更快。与RawCopy相比，这是一个显著的优势，RawCopy则会迭代每个文件的整个路径。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/trustedsec/tscopy.git

## TScopy运行选项

    
    
    .\TScopy_x64.exe -h
    
     
    
    usage:
    
        TScopy_x64.exe -r -o c:\test -f c:\users\tscopy\ntuser.dat
    
            Description: Copies only the ntuser.dat file to the c:\test directory
    
        TScopy_x64.exe -o c:\test -f c:\Windows\system32\config
    
            Description: Copies all files in the config directory but does not copy the directories under it.  
    
        TScopy_x64.exe -r -o c:\test -f c:\Windows\system32\config
    
            Description: Copies all files and subdirectories in the config directory.  
    
        TScopy_x64.exe -r -o c:\test -f c:\users\*\ntuser*,c:\Windows\system32\config
    
            Description: Uses Wildcards and listings to copy any file beginning with ntuser under users accounts and recursively copies the registry hives.
    
        
    
     
    
    Copy protected files by parsing the MFT. Must be run with Administrator privileges
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -f FILE, --file FILE  Full path of the file or directory to be copied.
    
                            Filenames can be grouped in a comma ',' seperated
    
                            list. Wildcard '*' is accepted.
    
      -o OUTPUTDIR, --outputdir OUTPUTDIR
    
                            Directory to copy files too. Copy will keep paths
    
      -i, --ignore_saved_ref_nums
    
                            Script stores the Reference numbers and path info to
    
                            speed up internal run. This option will ignore and not
    
                            save the stored MFT reference numbers and path
    
      -r, --recursive       Recursively copies directory. Note this only works with
    
                            directories.

其中还有一个隐藏的“--debug”选项，该选项可以启用调试模式输出。

## 工具使用样例

下列命令会将SYSTEM注册表信息拷贝至e:\outputdir，新文件路径为“e:\outputdir\windows\system32\config\SYSTEM”：

    
    
    TScopy_x64.exe -f c:\windows\system32\config\SYSTEM -o e:\outputdir

下列命令会将SYSTEM注册表信息拷贝至e:\outputdir，但是会忽略之前缓存的文件，并且不会将当前缓存保存至磁盘中：

    
    
    TScopy_x64.exe -f c:\windows\system32\config\SYSTEM,c:\windows\system32\config\SOFTWARE -o e:\outputdir

下列命令会将SYSTEM和SOFTWARE注册表信息拷贝至e:\outputdir：

    
    
    TScopy_x64.exe -f c:\windows\system32\config\ -o e:\outputdir

下列命令可以将目录配置内容拷贝至e:\outputdir：

    
    
    TScopy_x64.exe -r -f c:\windows\system32\config\ -o e:\outputdir

下列命令可以将目录配置内容递归拷贝至e:\outputdir：

    
    
    TScopy_x64.exe  -f c:\users\*\ntuser.dat -o e:\outputdir

下列命令可以将每一个用户NTUSER.DAT文件拷贝至e:\outputdir：

    
    
    TScopy_x64.exe  -f c:\users\*\ntuser.dat* -o e:\outputdir

针对每一个用户，拷贝所有以NTUSER.DAT开头的文件至e:\outputdir：

    
    
    TScopy_x64.exe  -f c:\users\*\AppData\Roaming\Microsoft\Windows\Recent,c:\windows\system32\config,c:\users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt -o e:\outputdir

## 项目地址

 **TScopy：** https://github.com/trustedsec/tscopy

