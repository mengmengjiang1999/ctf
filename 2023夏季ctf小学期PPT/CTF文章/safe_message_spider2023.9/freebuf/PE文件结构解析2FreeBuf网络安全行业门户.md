# 0x0导读

上一篇文章把Dos头,Nt头,可选头里的一些成员说过了(文章链接:[[PE文件结构解析1-SecIN (sec-in.com)](https://www.sec-in.com/article/1614)])，今天主要讲的内容是，Rva(内存偏移)转换Foa(文件偏移)，数据目录表，节表，话不多说来看文章。

# 0x1环境

编译器:VirsualStudio2022

16进制查看工具:winhex

# 0x2Rva与Foa转换

rva到foa的意义：因为pe文件在文件中和在内存中的大小是不一样的，在内存中，pe文件会被拉伸，所以同一个地址在内存中和文件中所指向的值是不一样的，所以要把内存中的偏移转换成文件中的偏移，下面我们来看一下转换的函数。

函数定义

    
    
    DWORD rtf(PBYTE buffer, DWORD rva)
    {
    PIMAGE_DOS_HEADER doshd = (PIMAGE_DOS_HEADER)buffer;
    PIMAGE_NT_HEADERS nthd = (PIMAGE_NT_HEADERS)(buffer + doshd->e_lfanew);
    PIMAGE_FILE_HEADER filehd = (PIMAGE_FILE_HEADER)(buffer + doshd->e_lfanew + 4);
    PIMAGE_OPTIONAL_HEADER32 optionhd = (PIMAGE_OPTIONAL_HEADER32)(buffer + doshd->e_lfanew + 24);
    PIMAGE_SECTION_HEADER sectionhd = IMAGE_FIRST_SECTION(nthd);
    for (int i = 0; i < filehd->NumberOfSections; i++)
    {
    if (rva >= sectionhd[i].VirtualAddress && rva <= sectionhd[i].VirtualAddress + sectionhd[i].SizeOfRawData)
    {
    return rva - sectionhd[i].VirtualAddress + sectionhd[i].PointerToRawData;
    }
    }
    }
    

转换函数代码解析：`首先为这个函数定义了两个参数，一个参数是基址用于定位各种头，和节表，另一个参数是要转换的rva，PIMAGE开头的代码主要是定位头和节表，为下面循环判断做准备，rva是在节中的，所以只需要循环判断，如果rva>=当前节的VirtualAddress又小于VirtualAddress+SizeOfRawData就可以判断出这个rva在当前节，只需要减去VirtualAddress再加上PointerToRawData即可。`

# 0x3数据目录解析

数据目录是可选头的一个成员(对可选头有疑问的可以看上一篇文章)，这个成员是一个结构体类型的，像这个样的成员一共有16个，也就是说数据目录表其实就是16个这样的结构体，结构体定义如下。

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
        DWORD   VirtualAddress;//一个rva，指向真正的数据表
        DWORD   Size;//数据表大小
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    
    

这16个结构体对应的表分别是`导出表，导入表，资源表，异常处理表，安全表，重定位表，调试表，版权表，指针目录，TLS表，载入配置表，绑定输入表，导入地址表，延迟载入表，COM信息，保留`最后一个表是保留起来的用不到。

结构体中的`VirtualAddress`成员是一个rva，`通过这个rva可以找到真正的表所在的地方，我们可以把VirtualAddress中的值看作一个"中间人"，可以通过这个"中间人"来找到真正的数据表。这里要注意时16个这样的结构。`

![wKg0C2I9fU6AY6udAABThbXhqKw341.png](https://image.3001.net/images/20220523/1653292798_628b3efe91fe4c6da262d.png!small)

`Size`表示当前结构体的`VirtualAddress`所指向表的大小。

代码解析

    
    
    #include <stdio.h>
    #include <Windows.h>
    #define path "C:\\Users\\blue\\Desktop\\Dll1.dll"
    
    void main()
    {
    FILE* fp = fopen(path, "rb");
    fseek(fp, 0, SEEK_END);
    int size = ftell(fp);
    rewind(fp);
    PBYTE ptr = (PBYTE)malloc(size);
    memset(ptr, 0, size);
    fread(ptr, size, 1, fp);
    PIMAGE_DOS_HEADER Dos = (PIMAGE_DOS_HEADER)ptr;
    PIMAGE_NT_HEADERS Nt = (PIMAGE_NT_HEADERS)(ptr + Dos->e_lfanew);
    PIMAGE_FILE_HEADER File = (PIMAGE_FILE_HEADER)(ptr + Dos->e_lfanew + 4);
    PIMAGE_OPTIONAL_HEADER32 Option = (PIMAGE_OPTIONAL_HEADER32)(ptr + Dos->e_lfanew + 20 + 4);
    PIMAGE_DATA_DIRECTORY DataDir = Option->DataDirectory;
    for (int i = 0; i < 17; i++)
    {
    printf("VirtualAddress:%x\n", DataDir[i].VirtualAddress);
    printf("Size:%x\n", DataDir[i].Size);
    }
    getchar();
    }
    

前三行代码主要是包含头文件，定义宏作为`fopen`函数的参数。

`FILE* fp = fopen(path,
"rb");`定义一个文件指针来接受`fopen`函数返回值，`fopen`第一个参数是要打开文件的路径，第二个参数是以什么方式打开，这里是rb也就是以二进制方式打开一个文件，只能读不可以写。

`fseek(fp, 0,
SEEK_END);`第一个参数是要设置文件的文件指针，第二个参数是一个相对于第三个参数是一个偏移量，第三个参数`SEEK_END`代表文件的末尾，代码大致意思文件流重定向到文件末尾。

`int size =
ftell(fp);`定义一个变量用来接收ftell函数的返回值，`ftell`函数作用是计算文件的大小，第一个参数是要计算那个文件的文件指针。

`rewind(fp);`将文件流重定向到文件开头，为下面读取数据做准备。

`PBYTE ptr =
(PBYTE)malloc(size);`定义一个`PBYTE`类型的指针指向`malloc`函数申请的内存，`malloc`函数第一个参数是申请多大的内存，`PBYTE`就是`char*`。

`memset(ptr, 0, size);`用0填充刚才申请的内存块，第一个参数内存块的地址，第二个参数用什么填充，第三个参数填充多大。

`fread(ptr, size, 1,
fp);`用于读取数据到内存，第一个参数是要读到哪里，第二个参数是读多少字节，第三个参数读多少次，第四个参数要读取文件的文件指针。

`PIMAGE_DOS_HEADER`结构体定义

    
    
    typedef struct _IMAGE_DOS_HEADER {      // DOS .EXE header
        WORD   e_magic;                     // Magic number
        WORD   e_cblp;                      // Bytes on last page of file
        WORD   e_cp;                        // Pages in file
        WORD   e_crlc;                      // Relocations
        WORD   e_cparhdr;                   // Size of header in paragraphs
        WORD   e_minalloc;                  // Minimum extra paragraphs needed
        WORD   e_maxalloc;                  // Maximum extra paragraphs needed
        WORD   e_ss;                        // Initial (relative) SS value
        WORD   e_sp;                        // Initial SP value
        WORD   e_csum;                      // Checksum
        WORD   e_ip;                        // Initial IP value
        WORD   e_cs;                        // Initial (relative) CS value
        WORD   e_lfarlc;                    // File address of relocation table
        WORD   e_ovno;                      // Overlay number
        WORD   e_res[4];                    // Reserved words
        WORD   e_oemid;                     // OEM identifier (for e_oeminfo)
        WORD   e_oeminfo;                   // OEM information; e_oemid specific
        WORD   e_res2[10];                  // Reserved words
        LONG   e_lfanew;                    // File address of new exe header
      } IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;
    

`PIMAGE_DOS_HEADER Dos =
(PIMAGE_DOS_HEADER)ptr;`定义一个`PIMAGE_DOS_HEADER`类型的结构体指针来指向刚才申请的那块内存，也可以说用这块内存中的数据来填充这个结构体指针所指向的结构体，因为ptr是PBYTE类型和`PIMAGE_DOS_HEADER`类型不同所以要把ptr从`PBYTE`强转成`PIMAGE_DOS_HEADER`类型。

    
    
    typedef struct _IMAGE_NT_HEADERS {
        DWORD Signature;
        IMAGE_FILE_HEADER FileHeader;
        IMAGE_OPTIONAL_HEADER32 OptionalHeader;
    } IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;
    

`PIMAGE_NT_HEADERS Nt = (PIMAGE_NT_HEADERS)(ptr +
Dos->e_lfanew);`定义一个`PIMAGE_NT_HEADERS32`类型的结构体指针在·通过基址+偏移的方式定位到Nt头，也就是ptr与Dos头的e_lfanew成员相加得到一个地址，这个地址就是Nt头开始的地方，也可理解为用这个地址中的数据填充这个结构体指针指向的结构体。

`PIMAGE_FILE_HEADER`结构体定义

    
    
    typedef struct _IMAGE_FILE_HEADER {
        WORD    Machine;
        WORD    NumberOfSections;
        DWORD   TimeDateStamp;
        DWORD   PointerToSymbolTable;
        DWORD   NumberOfSymbols;
        WORD    SizeOfOptionalHeader;
        WORD    Characteristics;
    } IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;
    

`PIMAGE_FILE_HEADER File = (PIMAGE_FILE_HEADER)(ptr + Dos->e_lfanew +
4);`定义一个结构体指针`(PIMAGE_NT_HEADERS32类型)`，在用基址+Dos头的e_lfanew成员定位到nt头，跟据nt头的结构体定义可以知道`Signature`成员后面就是File头而`Signature`成员大小是四字节，所以加4定位到File头，所以是`ptr
+ Dos->e_lfanew + 4`运算结果就是File头开始的地址，再用这个结构体指针指向这个地址即可。

`PIMAGE_OPTIONAL_HEADER32;`结构体定义

    
    
    typedef struct _IMAGE_OPTIONAL_HEADER {
        //
        // Standard fields.
        //
    
        WORD    Magic;
        BYTE    MajorLinkerVersion;
        BYTE    MinorLinkerVersion;
        DWORD   SizeOfCode;
        DWORD   SizeOfInitializedData;
        DWORD   SizeOfUninitializedData;
        DWORD   AddressOfEntryPoint;
        DWORD   BaseOfCode;
        DWORD   BaseOfData;
    
        //
        // NT additional fields.
        //
    
        DWORD   ImageBase;
        DWORD   SectionAlignment;
        DWORD   FileAlignment;
        WORD    MajorOperatingSystemVersion;
        WORD    MinorOperatingSystemVersion;
        WORD    MajorImageVersion;
        WORD    MinorImageVersion;
        WORD    MajorSubsystemVersion;
        WORD    MinorSubsystemVersion;
        DWORD   Win32VersionValue;
        DWORD   SizeOfImage;
        DWORD   SizeOfHeaders;
        DWORD   CheckSum;
        WORD    Subsystem;
        WORD    DllCharacteristics;
        DWORD   SizeOfStackReserve;
        DWORD   SizeOfStackCommit;
        DWORD   SizeOfHeapReserve;
        DWORD   SizeOfHeapCommit;
        DWORD   LoaderFlags;
        DWORD   NumberOfRvaAndSizes;
        IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
    } IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;
    

`PIMAGE_OPTIONAL_HEADER32 Option = (PIMAGE_OPTIONAL_HEADER32)(ptr +
Dos->e_lfanew + 20 +
4);`定义一个`PIMAGE_OPTIONAL_HEADER32`类型的结构体指针，然后通过基址+Dos头e_lfanew成员定位到nt头再加上nt头的Signature成员(4字节)得到File头地址，在加上File头的大小(20字节)，它们相加结果是一个地址这个地址是可选头开始的地方，用结构体指针指向这个地址即可。

`PIMAGE_DATA_DIRECTORY`结构体定义

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
        DWORD   VirtualAddress;
        DWORD   Size;
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    

`PIMAGE_DATA_DIRECTORY DataDir =
Option->DataDirectory;`定义一个`PIMAGE_DATA_DIRECTORY`类型的结构体指针，通过可选头的`DataDirectory`成员定位到数据目录表。

    
    
    for (int i = 0; i < 17; i++)
    {
    printf("VirtualAddress:%x\n", DataDir[i].VirtualAddress);
    printf("Size:%x\n", DataDir[i].Size);
    }
    

这里使用了一个for循环来循环打印数据目录表的数据。每循环一次i就加1知道i小于17就停止循环。

程序执行结果

![wKg0C2I9kluAWy72AAEagIiKrI119.png](https://image.3001.net/images/20220523/1653292798_628b3efedaf953b7a40b0.png!small)

个人对数据目录表的理解：就是16个结构体组成的表，通过结构体的`VirtualAddress`成员可以找到真正的表。

# 0x4节表解析

节表的大小是40个字节(注意是一个节表大小是40)，节表的数量有`File`头的`NumberOfSections`成员决定，节表指向节，节是用来存储数据的，如`.txt`节存放代码，`.data`节存放数据，但是并不是一成不变的，也可以把存放数据的节名字改成.txt并不会影响程序运行。

节表的定义

    
    
    typedef struct _IMAGE_SECTION_HEADER {
        BYTE    Name[IMAGE_SIZEOF_SHORT_NAME];
        union {
                DWORD   PhysicalAddress;
                DWORD   VirtualSize;
        } Misc;
        DWORD   VirtualAddress;
        DWORD   SizeOfRawData;
        DWORD   PointerToRawData;
        DWORD   PointerToRelocations;
        DWORD   PointerToLinenumbers;
        WORD    NumberOfRelocations;
        WORD    NumberOfLinenumbers;
        DWORD   Characteristics;
    } IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;
    

`Name[IMAGE_SIZEOF_SHORT_NAME]`一个BYTE类型的数组，用来存放当前节的名字，大小是8字节。

`Misc`一个联合体，通常会使用`VirtualSizez`成员，`VirtualSize`当前节内存中的大小。

`VirtualAddress`内存中节开始的地方，也就是内存中的偏移。

`SizeOfRawData`节在文件中的大小，按照文件对齐。

`PointerToRawData`文件中节开始的地方，文件中的偏移。

`Characteristics`节的属性

节表示例

![wKg0C2I9moWAT4rGAAAlXbjT2Ug017.png](https://image.3001.net/images/20220523/1653292799_628b3eff561ee70365dc8.png!small)

前8字节是节的名字，可以看出名字是.textbss，根据上面节定义可知名字后面是`VirtualSize`(内存中节大小)，我们从73也就是名字结束的地方往后查4个字节得到VirtualSize的值00010000去掉前面的0得到10000，再从`VirtualSize`结束的地方查4个字节得到`VirtualAddress`的值00001000同样去掉前面的0得到1000，剩下的成员怎么找就不赘述了，也是和上面这几个成员一样都是查出来的，我们直接看代码，用代码解析节表。

代码解析

    
    
    #include <stdio.h>
    #include <Windows.h>
    #define path "C:\\Users\\blue\\Desktop\\Dll1.dll"
    
    void main()
    {
    FILE* fp = fopen(path, "rb");
    fseek(fp, 0, SEEK_END);
    int size = ftell(fp);
    rewind(fp);
    PBYTE ptr = (PBYTE)malloc(size);
    memset(ptr, 0, size);
    fread(ptr, size, 1, fp);
    PIMAGE_DOS_HEADER Dos = (PIMAGE_DOS_HEADER)ptr;
    PIMAGE_NT_HEADERS Nt = (PIMAGE_NT_HEADERS)(ptr + Dos->e_lfanew);
    PIMAGE_FILE_HEADER File = (PIMAGE_FILE_HEADER)(ptr + Dos->e_lfanew + 4);
    PIMAGE_OPTIONAL_HEADER32 Option = (PIMAGE_OPTIONAL_HEADER32)(ptr + Dos->e_lfanew + 20 + 4);
    PIMAGE_DATA_DIRECTORY DataDir = Option->DataDirectory;
    
    for (int i = 0; i < 17; i++)
    {
    printf("VirtualAddress:%x\n", DataDir[i].VirtualAddress);
    printf("Size:%x\n", DataDir[i].Size);
    
    }
    PIMAGE_SECTION_HEADER Section = IMAGE_FIRST_SECTION(Nt);
    printf("节表\n");
    for (int i = 0; i < File->NumberOfSections; i++)
    {
    
    printf("Name:%s\n", Section[i].Name);
    printf("VirtualSize:%x\n", Section[i].Misc.VirtualSize);
    printf("VirtualAddress:%x\n", Section[i].VirtualAddress);
    printf("SizeOfRawData:%x\n",Section[i].SizeOfRawData);
    printf("PointerToRawData:%x\n", Section[i].PointerToRawData);
    printf("Characteristics:%x\n", Section[i].Characteristics);
    }
    getchar();
    }
    

上面说解析过的代码就不赘述了，直接看`PIMAGE_SECTION_HEADER Section =
IMAGE_FIRST_SECTION(Nt);`这行代码还是定义一个`PIMAGE_SECTION_HEADER`类型的结构体指针，这里使用`IMAGE_FIRST_SECTION`宏来定位节表这样方便些，当然也可以通过，可选头的地址+可选头的大小来定位节表。

    
    
    for (int i = 0; i < File->NumberOfSections; i++)
    {
    
    printf("Name:%s\n", Section[i].Name);
    printf("VirtualSize:%x\n", Section[i].Misc.VirtualSize);
    printf("VirtualAddress:%x\n", Section[i].VirtualAddress);
    printf("SizeOfRawData:%x\n",Section[i].SizeOfRawData);
    printf("PointerToRawData:%x\n", Section[i].PointerToRawData);
    printf("Characteristics:%x\n", Section[i].Characteristics);
    }
    

因为`File`头里`NumberOfSections`成员代表节表的数量，所以要用它作为判断条件，循环打印即可，这里打印名字是要用`%s`是打印字符串时用的，`%d`是10进制时用的，`%x`是打印16进制时用的

程序运行结果

![wKg0C2I9nSyARq6JAAF9ACzYN78868.png](https://image.3001.net/images/20220523/1653292799_628b3eff9c09a9107e969.png!small)

# 0x5结语

主要是介绍了Rva与Foa的转换和数据目录表，节表中一些比较重要的成员，和如何使用代码打印出它们，涉及到指针和结构体相关的知识。

由于作者水平有限，文章如有错误欢迎指出。

