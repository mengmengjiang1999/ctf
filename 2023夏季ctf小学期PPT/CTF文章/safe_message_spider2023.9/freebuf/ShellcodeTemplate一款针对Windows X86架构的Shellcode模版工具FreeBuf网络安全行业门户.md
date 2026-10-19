![](https://image.3001.net/images/20220331/1648740761_6245c9990df1bd9758761.jpeg!small)

## 关于ShellcodeTemplate

ShellcodeTemplate是一款易于修改的针对Windows x64/x86的Shellcode模版工具，该工具基于[
_TitanLdr_](https://github.com/SecIdiot/TitanLdr)开发，能够帮助广大研究人员将项目代码编译成一个PE可执行程序，并提取.text字段。

## Shellcode百科

Shellcode是一段用于利用软件漏洞而执行的代码，实际上是十六进制形式的机器语言，大家知道机器语言是二进制的，CPU只认识二进制，因为要被直接注入到内存中，没办法编译了，所以希望CPU可以执行，那就只能用机器代码了，一般用汇编语言写出程序，在从目标代码中提取出来。

Shellcode可以按照攻击者执行的位置分为本地Shellcode和远程Shellcode。本地运行的Shellcode经常用于利用软件漏洞提升权限，比如在Linux下由普通权限提升至root权限等。而远程Shellcode指的是利用软件漏洞获得特定的Shellcode，再经由C或Python编写远程攻击程序，进而取得对方电脑的root权限。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Cracked5pider/ShellcodeTemplate.git

接下来，我们需要在makefile中修改项目名称，将“ShellcodeTemplate”修改为你想要的名字，然后使用make来编译项目源码：

    
    
    make        // to compile x64 and x86
    
    make x64    // to compile only x64
    
    make x86    // to compile only x86

## 工具使用样例

Shellocde的入口点如下所示，当然了，我们也可以根据自己的需要来进行修改。

首先，我们需要使用自定义的GetModuleHandle和GetProcAddress来初始化我们要用到的库和函数：

    
    
    SEC( text, B ) VOID Entry( VOID )
    
    {
    
        INSTANCE Instance = { };
    
     
    
        Instance.Modules.Kernel32   = TGetModuleHandle( HASH_KERNEL32 );
    
        Instance.Modules.Ntdll      = TGetModuleHandle( HASH_NTDLL );
    
     
    
        if ( Instance.Modules.Kernel32 != NULL )
    
        {
    
            // Load needed functions
    
            Instance.Win32.LoadLibraryA = TGetProcAddr( Instance.Modules.Kernel32, 0xb7072fdb );
    
     
    
            // Load needed Libraries
    
            Instance.Modules.User*32     = Instance.Win32.LoadLibraryA( GET_SYMBOL( "User*32" ) );
    
     
    
            if ( Instance.Modules.User*32 != NULL )
    
            {
    
                Instance.Win32.MessageBoxA = TGetProcAddr( Instance.Modules.User*32, 0xb303ebb4 );
    
            }
    
        }
    
        
    
        // ------ Code ------    
        Instance.Win32.MessageBoxA( NULL, GET_SYMBOL( "Hello World" ), GET_SYMBOL( "MessageBox Title" ), MB_OK );
    
    }

值得注意的是，正如大家所看到的那样，我们可以直接在我们的Shellcode中使用常规字符串，这是因为我们在链接的时候向我们的Shellcode中引入了.rdata字段，GET_SYMBOL将通过GetRIP()的偏移量获取到函数或字符串的指针。

![](https://image.3001.net/images/20220331/1648740798_6245c9be9d1f4fb3eb1fd.png!small)

## 项目地址

 **ShellcodeTemplate：** 【[
_GitHub传送门_](https://github.com/Cracked5pider/ShellcodeTemplate)】

## 参考资料

> [ _https://twitter.com/ilove2pwn__](https://twitter.com/ilove2pwn_)
>
> [
> _https://github.com/SecIdiot/TitanLdr_](https://github.com/SecIdiot/TitanLdr)

