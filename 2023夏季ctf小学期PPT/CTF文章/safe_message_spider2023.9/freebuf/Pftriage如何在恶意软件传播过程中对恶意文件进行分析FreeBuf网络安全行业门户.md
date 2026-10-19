**今天给大家介绍的是一款可以在恶意软件传播过程中帮助研究人员分析和追踪恶意文件的强大工具。**

![a.jpg](https://image.3001.net/images/20190219/1550513963_5c6af72b898d9.jpg!small)

## pftriage

pftriage这款Python工具可以帮助研究人员在恶意软件的分发过程中对恶意文件进行追踪和分析，并快速查看文件属性和内容，以帮助我们更好地了解恶意软件的运行分发机制。

除此之外，该工具还可以分析恶意软件的功能，并从中提取出常见的恶意标识符。

### 依赖组件

> 1、 pefile
>
> 2、 filemagic

注：macOS用户可以使用下列命令安装libmagic：

    
    
    $brew install libmagic

## 工具使用

    
    
    usage:pftriage [options]
    
    Showinformation about a file for triage.
    
    positionalarguments:
    
      file                  The file to triage.
    
    optionalarguments:
    
      -h, --help            show this help message and exit
    
      -i, --imports         Display import tree
    
      -s, --sections        Display overview of sections. For moredetailed info
    
                            pass the -v switch
    
      --removeoverlay       Remove overlay data.
    
      --extractoverlay      Extract overlay data.
    
      -r, --resources       Display resource information
    
      -R, --rich            Display Rich Header information
    
      -D DUMP_OFFSET, --dump DUMP_OFFSET
    
                            Dump data using thepassed offset or 'ALL'. Currently
    
                            only works withresources.
    
      -e, --exports         Display exports
    
      -a, --analyze         Analyze the file.
    
      -v, --verbose         Display version.
    
      -V, --version         Print version and exit.

## 详细信息

显示详细信息，可以使用-s或--sections，或者使用-v来查看更加详细的分析数据。

    
    
    ----Section Overview (use -v for detailed section info)  ----    
     
    
     Name       Raw Size    Raw Data Pointer  Virtual Address     Virtual Size        Entropy             Hash
    
     .text      0x00012200  0x00000400        0x00001000          0x000121d8          6.71168555177       ff38fce4f48772f82fc77b4ef223fd74
    
     .rdata     0x00005a00  0x00012600        0x00014000          0x0000591a          4.81719489022       b0c15ee9bf8480a07012c2cf277c3083
    
     .data      0x00001a00  0x00018000        0x0001a000          0x0000ab80          5.28838495072       5d969a878a5106ba526aa29967ef877f
    
     .rsrc      0x00002200  0x00019a00        0x00025000          0x00002144          7.91994689603       d361caffeadb934c9f6b13b2474c6f0f
    
     .overlay   0x00009b30  0x0001bc00        0x00000000          0x00000000          0                   N/A

## 资源

显示资源数据，可以使用-r或--resources参数。

    
    
    ----Resource Overview ----    
     
    
     Type: CODATA
    
      Name       Language        SubLang             Offset      Size        Code Page   Type
    
      0x68       LANG_RUSSIAN    RUSSIAN             0x000250e0  0x00000cee 0x000004e4
    
      0x69       LANG_RUSSIAN    RUSSIAN             0x00025dd0  0x000011e6 0x000004e4
    
     
    
     Type: RT_MANIFEST
    
      Name       Language        SubLang             Offset      Size        Code Page   Type
    
      0x1        LANG_ENGLISH    ENGLISH_US          0x00026fb8  0x0000018b 0x000004e4

注：使用-D参数可以提取出特定偏移量的资源信息。

## 导入

使用-i或--imports参数可以显示导入的数据或模块：

    
    
    [*]Loading File...
    
     ---- Imports ----    
     Number of imported modules: 4
    
     
    
     KERNEL32.dll
    
      |-- GetProcessHeap
    
      |-- HeapFree
    
      |-- HeapAlloc
    
      |-- SetLastError
    
      |-- GetLastError
    
     
    
     WS2_32.dll
    
      |-- getaddrinfo
    
      |-- freeaddrinfo
    
      |-- closesocket Ordinal[3] (Imported byOrdinal)
    
      |-- WSAStartup Ordinal[115] (Imported byOrdinal)
    
      |-- socket Ordinal[23] (Imported by Ordinal)
    
      |-- send Ordinal[19] (Imported by Ordinal)
    
      |-- recv Ordinal[16] (Imported by Ordinal)
    
      |-- connect Ordinal[4] (Imported by Ordinal)
    
     
    
     ole32.dll
    
      |-- CoCreateInstance
    
      |-- ...

## 导出

使用-e或--exports参数可以显示导出数据：

    
    
    [*]Loading File...
    
     
    
     ---- Exports ----    
     Total Exports: 5
    
     Address    Ordinal   Name
    
     0x00001151 1         FindResources
    
     0x00001103 2         LoadBITMAP
    
     0x00001137 3         LoadICON
    
     0x000010e9 4         LoadIMAGE
    
     0x0000111d 5         LoadSTRINGW

## Rich Header详细数据

使用-R或--rich参数可以显示RichHeader详细数据：

    
    
    [*]Loading File...
    
    --Rich Header Details --    
     
    
     Checksum: 0x2b41e6a9
    
     Id Product         Count   Build Id Build
    
     -- -------         -----   -------- -----    
     150 AliasObj900     1      20413     <Unknown>
    
     132 Utc1500_CPP     36     21022     9.0 2008
    
     149 Masm900         17     21022     9.0 2008
    
     123 Implib800       3      50727     11.0 2012
    
     1  Import0         102     0        <Unknown>
    
     131 Utc1500_C       123    21022     9.0 2008
    
     145 Linker900       1      21022     9.0 2008

## 元数据

如果命令行没有传递任何配置选项参数的话，工具可以显示完整的文件和版本元数据：

    
    
    [*]Loading File...
    
    [*]Processing File details...
    
     
    
     
    
    ----File Summary ----    
     
    
     General
    
         Filename         samaple.exe
    
         Magic Type       PE32 executable (GUI) Intel 80386, forMS Windows
    
         Size             135168
    
         First Bytes      4d 5a 90 00 03 00 00 00 04 00 00 00 ff ff00 00
    
     
    
     Hashes
    
         MD5              8e8a8fe8361c7238f60d6bbfdbd304a8
    
         SHA1            557832efe10daff3f528a3c3589eb5a6dfd12447
    
         SHA256          118983ba4e1c12a366d7d6e9461c68bf222e2b03f3c1296091dee92ac0cc9dd8
    
         Import Hash      0239fd611af3d0e9b0c46c5837c80e09
    
         ssdeep           
    
     
    
     Headers
    
         Subsystem        IMAGE_SUBSYSTEM_WINDOWS_GUI
    
         Linker Version   12.0 - (Visual Studio 2013)
    
         Image Base       0x400000
    
         Compile Time     Thu Jun 23 16:04:21 2016 UTC
    
         Checksum         0
    
         Filename         sample.exe
    
         EP Bytes         55 8b ec 51 83 65 fc 00 8d 45 fc 56 5750 e8 64
    
         Signature        0x4550
    
         First Bytes      4d 5a 90 00 03 00 00 00 04 00 00 00 ff ff00 00
    
         Sections         4
    
         Entry Point      0x139de
    
         Packed           False
    
         Size             135168
    
         Characteristics
    
                          IMAGE_FILE_32BIT_MACHINE
    
                         IMAGE_FILE_EXECUTABLE_IMAGE
    
                          IMAGE_FILE_RELOCS_STRIPPED

## 恶意文件分析

PFTriage可以执行简单的文件分析来帮助研究人员识别恶意字符：

    
    
    [*]Loading File...
    
    [*]Analyzing File...
    
    [*]Analysis Complete...
    
     
    
      [!] Checksum        Invalid CheckSum
    
      [!] AntiDebug       AntiDebug Function import [GetTickCount]
    
      [!] AntiDebug       AntiDebug Function import[QueryPerformanceCounter]
    
      [!] Imports         Suspicious API Call [TerminateProcess]
    
      [!] AntiDebug       AntiDebug Function import[SetUnhandledExceptionFilter]
    
      [!] AntiDebug       AntiDebug Function import[IsDebuggerPresent]

### 项目地址

> PFTriage：<https://github.com/idiom/pftriage>

 ***参考来源：[kitploit](https://www.kitploit.com/2019/02/pftriage-python-tool-and-library-to.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

