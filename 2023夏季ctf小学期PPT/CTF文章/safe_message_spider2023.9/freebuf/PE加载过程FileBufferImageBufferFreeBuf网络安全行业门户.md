## 一、FileBuffer到ImageBuffer常见的误区

### 1.文件执行的总过程

  * 我们知道一个硬盘上的文件读入到内存中（FileBuffer），是原封不动的将硬盘上的文件数据复制一份放到内存中

  * 接着如果文件要运行，需要先将FileBuffer中的文件数据"拉伸"，重载到每一个可执行文件的4GB虚拟内存中！此时称文件印象或者内存印象，即ImageBuffer

  * 但是ImageBuffer就是文件运行时真正在内存中状态吗？或者说文件在ImageBuffer中就是表示文件被执行了吗？不！！！！！！

  *  **在ImageBuffer中的文件数据由于按照一定的规则被"拉伸"，只是已经无线接近于可被windows执行的文件格式了！但是此时还不代表文件已经被执行了，因为此时文件也只是处在4GB的虚拟内存中，如果文件被执行操作系统还需要做一些事情，将文件真正的装入内存中，等待CPU的分配执行**

  * 所以不要理解为ImageBuffer中的状态就是文件正在被执行，后面操作系统还要做很多事情才能让ImageBuffer中的文件真正执行起来的

### 2.SizeOfRawData一定大于Misc.VirtualSize？

  * SizeOfRawData表示此节在硬盘上经过文件对齐后的大小；Misc.VirtualSize表示此节没有经过对齐的在内存中的大小。那么是不是说SizeOfRawData一定大于Misc.VirtualSize呢？不一定！！！！！！！

  * 我们写C语言的时候知道如果你定义一个数组已经初始化，比如 **int arr[1000] = {0}** ;，此时编译成.exe文件存放在硬盘上时，这1000个int类型的0肯定会存放在某一个节中，并且分配1000个0的空间，这个空间大小是多少，最后重载到ImageBuffer时还是多少，即Misc.VirtualSize不管文件在硬盘上还是内存中的值都是一致的。所以，SizeOfRawData一般都是大于Misc.VirtualSize的

  * 但是如果我们定义成 **int arr[1000]** ;，表示 **数据还未初始化** ，并且如果程序中没有使用过或初始化过这块内存空间，那么我们平时看汇编会发现其实编译器还没有做任何事情，这就只是告诉编译器需要留出1000个int宽度大小的内存空间。所以如果某一个节中存在已经被定义过但还未初始化的数据，那么文件在硬盘上不会显式的留出空间，即 **SizeOfRawData中不会算上未初始化数据的空间** ；但是此节的 **Misc.VirtualSize为加载到内存中时节的未对齐的大小** ，那么这个值就需要算上给未初始化留出来空间后的整个节的大小，故在内存中的节本身的总大小可能会大于硬盘中的此节文件对齐后的大小。

## 二、模拟PE加载过程

![img](https://image.3001.net/images/20221018/1666104000_634ebac082c42803db4e8.png!small)

  1. 我们先在硬盘上找一个可执行文件，将文件的数据复制到内存中，即FileBuffer中（前面的练习做过很多次了）

  2. 根据SizeOfImage的大小，再使用malloc开辟一块ImageBuffer（SizeOfImage即为文件加载到4GB内存的大小）

  3. 因为NT头和节表文件对齐后的这段数据经过PE loader加载到ImageBuffer是不会变的，所以直接可以将NT头和节表文件对齐后的这块数据从FileBuffer中复制到ImageBuffer中

  4. 接着就是复制所有节的数据：需要使用循环，先复制第一个节的内容。通过第一个节对应节表中的 **PointerToRawData** 的值确定第一个节的起始地址；再通过 **SizeOfRawData** 的值得到从起始地址开始需要复制多少字节的数据到 **ImageBuffer** 中；再接着将这些数据复制到 **ImageBuffer** 中的哪个位置呢？ 就需要再通过此节对应的节表中的 **VirtualAddress** 决定将数据从 **ImageBuffer** 中的哪个地址开始赋值，由于是相对地址，所以还需要知道 **ImageBase** ，但是！！我们是模拟PE的加载过程， **此时ImageBuffer的首地址是由malloc申请的，不是ImageBase！** 所以我们需要使用malloc申请的 **首地址 + VirtualAddress** 就是最终将第一节数据复制到ImageBuffer中的起始地址。后面的节的数据以此类推从FileBuffer复制到ImageBuffer中

>
> 为什么选择SizeOfRawData，不选择Misc.VirtualSize来确定需要复制的节的大小？因为上面说过，Misc.VirtualSize的值由于节中有未初始化的数据且未使用而计算出预留的空间装入内存后的总大小的值可能会很大，如果这个值大到已经包含了后面一个节的数据，那么按照这个值将FileBuffer中的数据复制到ImageBuffer中很可能会把下一个节的数据也复制过去，所以直接用SizeOfRawData就可以了。但是如果节中包含未初始化数据，这样做起始就不太准确了，但是可以大致模拟这个过程即可

![img](https://image.3001.net/images/20221018/1666104001_634ebac177a14d3087409.png!small)

## 三、内存偏移到文件偏移计算

比如一个文件加载到4GB内存中的某一个数据地址为0x501234，那么怎么算出这个内存地址对应到文件在硬盘上时的地址是多少，即算出相对于文件的偏移地址？

  1. 先算出此内存地址相对于文件在内存中的起始地址的偏移量

  2. 接着通过这个偏移量循环和每一个节的VirtualAddress做比较，当此偏移量大于某一个节的VirtualAddress并且小于此VirtualAddress + Misc.VirtualSize，就说明这个内存地址就在这个节中

  3. 再用此偏移量 - （此节的VirtualAddress + 文件在内存中的起始地址）得到这个内存地址相对于所在节的偏移量

  4. 接着找内存地址所在节的PointerToRawData，通过PointerToRawData + 聂村地址相对于所在节的偏移量来得到此内存地址在硬盘上时相对于文件的偏移量

  * 举例：现在我们要找0x501234对应的文件偏移是多少？

  * 0x501234 - 0x500000 = 0x1234

  * 因为0x1000 < 0x1234 < 0x1000 + Misc.VirtualSize，所以0x501234在可执行文件的第一个节中

  * 0x501234 - （0x50000 + 0x1000） = 0x234

  * 由于第一个节的PointerToRawData为0x400，文件在硬盘上的起始地址为0（相对的），所以0x400 + 0x234 = 0x634

![img](https://image.3001.net/images/20221018/1666104002_634ebac2815e51a59b766.png!small)

## 四、作业：filebuffer->imagebuffer->newbuffer->存盘

### 相关的函数说明

#### `ReadPEFile`：

作用：

    
    
    将文件读取到缓冲区

参数说明：

    
    
    lpszFile 文件路径                                 
    ​  
    pFileBuffer 缓冲区指针

返回值说明：

    
    
    读取失败返回0，否则返回实际读取的大小

示例

    
    
    DWORD ReadPEFile(IN LPSTR lpszFile,OUT LPVOID* pFileBuffer);

使用IN和OUT，这个是C++语法中允许的 允许`#define NAME`这样不带替换表达式的定义，目的就是为了告诉用户参数是传入还是传出

`LPSTR ----> typedef CHAR *LPSTR, *PSTR;`是一个`char*`指针；在WINNT.H头文件里面 `LPVOID
----> typedef void far *LPVOID;`是一个`void*`指针，在WINDEF.H头文件里面

它是别名一个`void far *`类型的指针，其中far是以前针对16位系统的，而现在基本都是32位以上系统
所以这个far已经没有意义了，可以忽略，总结下来 LPVOID就是个`void*`指针类型

`DWORD ---> typedef unsigned long DWORD;`是32位系统里面是无符号4字节整数

#### `CopyFileBufferToImageBuffer`：

作用：

将文件从`FileBuffer`复制到`ImageBuffer`

参数说明：

    
    
    pFileBuffer  FileBuffer指针                                 
    ​  
    pImageBuffer ImageBuffer指针

返回值说明：

    
    
    读取失败返回0，否则返回ImageBuffer的大小

示例

    
    
    DWORD CopyFileBufferToImageBuffer(IN LPVOID pFileBuffer,OUT LPVOID* pImageBuffer);

#### `CopyImageBufferToNewBuffer`：

作用：

将`ImageBuffer`中的数据复制到新的缓冲区

参数说明：

    
    
    pImageBuffer ImageBuffer指针                                
    ​  
    pNewBuffer NewBuffer指针  

返回值说明：

    
    
    读取失败返回0，否则返回NewBuffer的大小      
    DWORD CopyImageBufferToNewBuffer(IN LPVOID pImageBuffer,OUT LPVOID* pNewBuffer);

#### `MemeryTOFile`：

作用：

将内存中的数据复制到文件

参数说明：

    
    
    pMemBuffer 内存中数据的指针                               
    ​  
    size 要复制的大小                               
    ​  
    lpszFile 要存储的文件路径   

返回值说明：

    
    
    读取失败返回0，否则返回复制的大小   

示例：

    
    
    BOOL MemeryTOFile(IN LPVOID pMemBuffer,IN size_t size,OUT LPSTR lpszFile);

#### `RvaToFileOffset`：

将内存偏移转换为文件偏移

参数说明：

    
    
    pFileBuffer FileBuffer指针                                  
    ​  
    dwRva RVA的值 

返回值说明：

    
    
    返回转换后的FOA的值，如果失败返回0

示例：

    
    
    DWORD RvaToFileOffset(IN LPVOID pFileBuffer,IN DWORD dwRva);

### 具体代码实现

##### 完整版

###### 为什么要使用void**传参

eg：

  * GetContext(const wchar_t* pKeyName, void** pValue, int& nLen); 其中pValue是在GetContext中获取的值，并在该函数内部分配内存，调 用GetContext的在调用地方调用 ReleaseData释放该内存。

  * 该函数内部做如下使用：

  * step1）WCHAR *pContent = new WCHAR[MAX_PATH];

  * step2）对pContent值赋值

  * step3）*pValue = pContent;

  * (由此可见，*pValue保存的是新分配内存的地址。)

  * Q:为啥形参不是void pValue而是void **pValue，实际用的时候也还是使 用pValue，只要传参时候传pValue， 而不是&pValue就好了呀。

  * A:因为只传void就是值传递，GetContext改变的是副本，传void**，其相当于void&,保证的是引用传递，改变的 是形参
    
        #include<stdio.h>  
    #include<string.h>  
    #include<malloc.h>  
    #include<stdlib.h>  
    #include<windows.h>  
    ​  
    #define test 1  
    ​  
    DWORD ToLoaderPE(LPSTR file_path, PVOID* pFileBuffer);  
    ​  
    DWORD CopyFileBufferToImageBuffer(PVOID pFileBuffer, PVOID* pImageBuffer);  
    DWORD CopyImageBufferToNewFileBuffer(PVOID pImageBuffer, PVOID* pNewFileBuffer);  
    BOOL MemoryToFile(PVOID pMemBuffer, DWORD size, LPSTR lpszFile);  
    ​  
    char file_path[] = "E:\\Reverse\\吾爱破解工具包2.0\\吾爱破解工具包\\Tools\\Others\\ipmsg.exe";  
    char write_file_path[] = "C:\\Users\\whl\\Desktop\\1.exe";  
    ​  
    //返回PE文件大小  
    DWORD ToLoaderPE(LPSTR file_path, PVOID* pFileBuffer)  
    {  
    FILE* pFile = NULL;  
    DWORD FileSize = 0;  
    PVOID pFileBufferTemp = NULL;  
    ​  
    pFile = fopen(file_path, "rb");  
    ​  
    if (!pFile)  
    {  
    printf("(ToLoaderPE)Can't open file!\n");  
    return 0;  
    }  
    ​  
    fseek(pFile, 0, SEEK_END);  
    FileSize = ftell(pFile);  
    printf("FileBuffer: %#x\n", FileSize);  
    fseek(pFile, 0, SEEK_SET);  
    pFileBufferTemp = malloc(FileSize);  
    ​  
    if (!pFileBufferTemp)  
    {  
    printf("(ToLoaderPE)Allocate dynamic memory failed!\n");  
    fclose(pFile);  
    return 0;  
    }  
    ​  
    DWORD n = fread(pFileBufferTemp, FileSize, 1, pFile);  
    ​  
    if (!n)  
    {  
    printf("(ToLoaderPE)Read file failed!\n");  
    free(pFileBufferTemp);  
    fclose(pFile);  
    return 0;  
    }  
    *pFileBuffer = pFileBufferTemp;  
    pFileBufferTemp = NULL;  
    fclose(pFile);  
    return FileSize;  
    }  
    ​  
    DWORD CopyFileBufferToImageBuffer(PVOID pFileBuffer, PVOID* pImageBuffer)  
    {  
    PIMAGE_DOS_HEADER pDosHeader = NULL;  
    PIMAGE_NT_HEADERS pNTHeader = NULL;  
    PIMAGE_FILE_HEADER pPEHeader = NULL;  
    PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;  
    PIMAGE_SECTION_HEADER pSectionHeader = NULL;  
    ​  
    PVOID pImageTemp = NULL;  
    ​  
    if (!pFileBuffer)  
    {  
    printf("(CopyFileBufferToImageBuffer)Can't open file!\n");  
    return 0;  
    }  
    ​  
    if (*((PWORD)pFileBuffer) != IMAGE_DOS_SIGNATURE)  
    {  
    printf("(CopyFileBufferToImageBuffer)No MZ flag, not exe file!\n");  
    return 0;  
    }  
    ​  
    pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;  
    ​  
    if (*((LPDWORD)((DWORD)pFileBuffer + pDosHeader->e_lfanew)) != IMAGE_NT_SIGNATURE)  
    {  
    printf("(CopyFileBufferToImageBuffer)Not a valid PE flag!\n");  
    return 0;  
    }  
    ​  
    pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer + pDosHeader->e_lfanew);  
    pPEHeader = (PIMAGE_FILE_HEADER)(((DWORD)pNTHeader) + 4);  
    pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);  
    pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);  
    ​  
    pImageTemp = malloc(pOptionHeader->SizeOfImage);  
    ​  
    if (!pImageTemp)  
    {  
    printf("(CopyFileBufferToImageBuffer)Allocate dynamic memory failed!\n");  
    free(pImageTemp);  
    return 0;  
    }  
    ​  
    memset(pImageTemp, 0, pOptionHeader->SizeOfImage);  
    memcpy(pImageTemp, pDosHeader, pOptionHeader->SizeOfHeaders);  
    ​  
    PIMAGE_SECTION_HEADER pSectionHeaderTemp = pSectionHeader;  
    ​  
    for (int n = 0; n < pPEHeader->NumberOfSections; n++, pSectionHeaderTemp++)  
    {  
    memcpy((PVOID)((DWORD)pImageTemp + pSectionHeaderTemp->VirtualAddress), (PVOID)((DWORD)pFileBuffer + pSectionHeaderTemp->PointerToRawData), pSectionHeaderTemp->SizeOfRawData);  
    printf("VirtualAddress%d: %#10x         PointerToRawData%d: %#10x\n", n, (DWORD)pImageTemp + pSectionHeader->VirtualAddress, n, (DWORD)pFileBuffer + pSectionHeader->PointerToRawData);  
    }  
    *pImageBuffer = pImageTemp;  
    pImageTemp = NULL;  
    return pOptionHeader->SizeOfImage;  
    }  
    ​  
    DWORD CopyImageBufferToNewFileBuffer(PVOID pImageBuffer, PVOID* pNewFileBuffer)  
    {  
    PIMAGE_DOS_HEADER pDosHeader = NULL;  
    PIMAGE_NT_HEADERS pNTHeader = NULL;  
    PIMAGE_FILE_HEADER pPEHeader = NULL;  
    PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;  
    PIMAGE_SECTION_HEADER pSectionHeader = NULL;  
    ​  
    LPVOID pTempNewbuffer = NULL;  
    ​  
    if (!pImageBuffer)  
    {  
    printf("(CopyImageBufferToNewBuffer)Can't open file!\n");  
    return 0;  
    }  
    ​  
    if (*((PWORD)pImageBuffer) != IMAGE_DOS_SIGNATURE)  
    {  
    printf("(CopyImageBufferToNewBuffer)No MZ flag, not exe file!\n");  
    return 0;  
    }  
    ​  
    pDosHeader = (PIMAGE_DOS_HEADER)pImageBuffer;  
    if (*((PDWORD)((DWORD)pImageBuffer + pDosHeader->e_lfanew)) != IMAGE_NT_SIGNATURE)  
    {  
    printf("(CopyImageBufferToNewBuffer)Not a valid PE flag!\n");  
    return 0;  
    }  
    ​  
    pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pImageBuffer + pDosHeader->e_lfanew);  
    pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4); // 这里必须强制类型转换  
    pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);  
    pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);  
    ​  
    //获取new_buffer的大小  
    int new_buffer_size = pOptionHeader->SizeOfHeaders;  
    for (DWORD i = 0; i < pPEHeader->NumberOfSections; i++)  
    {  
    new_buffer_size += pSectionHeader[i].SizeOfRawData;  // pSectionHeader[i]另一种加法  
    }  
    // 分配内存（newbuffer）  
    pTempNewbuffer = malloc(new_buffer_size);  
    if (!pTempNewbuffer)  
    {  
    printf("(CopyImageBufferToNewBuffer)Allocate dynamic memory failed!\n");  
    return 0;  
    }  
    memset(pTempNewbuffer, 0, new_buffer_size);  
    memcpy(pTempNewbuffer, pDosHeader, pOptionHeader->SizeOfHeaders);  
    // 循环拷贝节区  
    PIMAGE_SECTION_HEADER pTempSectionHeader = pSectionHeader;  
    for (DWORD j = 0; j < pPEHeader->NumberOfSections; j++, pTempSectionHeader++)  
    {   //PointerToRawData节区在文件中的偏移,VirtualAddress节区在内存中的偏移地址,SizeOfRawData节在文件中对齐后的尺寸  
    memcpy((PDWORD)((DWORD)pTempNewbuffer + pTempSectionHeader->PointerToRawData), (PDWORD)((DWORD)pImageBuffer + pTempSectionHeader->VirtualAddress), pTempSectionHeader->SizeOfRawData);  
    }  
    //返回数据  
    *pNewFileBuffer = pTempNewbuffer; //暂存的数据传给参数后释放  
    pTempNewbuffer = NULL;  
    return new_buffer_size;  // 返回计算得到的分配内存的大小  
    }  
    ​  
    BOOL MemoryToFile(PVOID pMemBuffer, DWORD size, LPSTR lpszFile)  
    {  
    FILE* fp;  
    fp = fopen(lpszFile, "wb");  
    if (fp != NULL)  
    {  
    fwrite(pMemBuffer, size, 1, fp);  
    }  
    fclose(fp);  
    return 1;  
    }  
    ​  
    VOID operate()  
    {  
    LPVOID pFileBuffer = NULL;  
    LPVOID pNewFileBuffer = NULL;  
    LPVOID pImageBuffer = NULL;  
    ​  
    DWORD ret1 = ToLoaderPE(file_path, &pFileBuffer);  // &pFileBuffer(void**类型) 传递地址对其值可以进行修改  
    printf("exe->filebuffer  返回值为计算所得文件大小：%#x\n", ret1);  
    ​  
    DWORD ret2 = CopyFileBufferToImageBuffer(pFileBuffer, &pImageBuffer);  
    printf("filebuffer -> imagebuffer返回值为计算所得文件大小：%#x\n", ret2);  
    DWORD ret3 = CopyImageBufferToNewFileBuffer(pImageBuffer, &pNewFileBuffer);  
    printf("imagebuffer -> newfilebuffer返回值为计算所得文件大小：%#x\n", ret3);  
    MemoryToFile(pNewFileBuffer, ret3, write_file_path);  
    ​  
    free(pFileBuffer);  
    free(pNewFileBuffer);  
    free(pImageBuffer);  
    }  
    ​  
    int main()  
    {  
    operate();  
    getchar();  
    return 0;  
    }

## RVA和FOA的相互转换

    
        #include<stdafx.h>  
    #include<stdio.h>  
    #include<stdlib.h>  
    #include<windows.h>  
      
    #define test 1  
      
    DWORD ToLoaderPE(LPSTR file_path, PVOID* pFileBuffer);  
    DWORD FoaToImageOffset(PVOID pBuffer, DWORD dwFoa);  
    DWORD RvaToFileOffset(PVOID pBuffer, DWORD dwRva);  
      
    char file_path[] = "C:\\Windows\\System32\\notepad.exe";  
    char write_file_path[] = "E:\\滴水\\1.exe";  
    ​  
    //返回PE文件大小  
    DWORD ToLoaderPE(LPSTR file_path, PVOID* pFileBuffer)  
    {  
    FILE *pFile = NULL;  
    DWORD FileSize = 0;  
    PVOID pFileBufferTemp = NULL;  
      
    pFile = fopen(file_path, "rb");  
      
    if (!pFile)  
    {  
    printf("(ToLoaderPE)Can't open file!\n");  
    return 0;  
    }  
      
    fseek(pFile, 0, SEEK_END);  
    FileSize = ftell(pFile);  
    printf("FileBuffer: %#x\n", FileSize);  
    fseek(pFile, 0, SEEK_SET);  
    pFileBufferTemp = malloc(FileSize);  
      
    if (!pFileBufferTemp)  
    {  
    printf("(ToLoaderPE)Allocate dynamic memory failed!\n");  
    fclose(pFile);  
    return 0;  
    }  
      
    DWORD n = fread(pFileBufferTemp, FileSize, 1, pFile);  
      
    if (!n)  
    {  
    printf("(ToLoaderPE)Read file failed!\n");  
    free(pFileBufferTemp);  
    fclose(pFile);  
    return 0;  
    }  
    *pFileBuffer = pFileBufferTemp;  
    pFileBufferTemp = NULL;  
    fclose(pFile);  
    return FileSize;  
    }  
      
    DWORD RvaToFileOffset(PVOID pBuffer, DWORD dwRva)  
    {  
    PIMAGE_DOS_HEADER pDosHeader = NULL;  
    PIMAGE_NT_HEADERS pNTHeader = NULL;  
    PIMAGE_FILE_HEADER pPEHeader = NULL;  
    PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;  
    PIMAGE_SECTION_HEADER pSectionHeader = NULL;  
      
    if (!pBuffer)  
    {  
    printf("(RvaToFileOffset)Can't open file!\n");  
    return 0;  
    }  
      
    if (*((PWORD)pBuffer) != IMAGE_DOS_SIGNATURE)  
    {  
    printf("(RvaToFileOffset)No MZ flag, not exe file!\n");  
    return 0;  
    }  
      
    pDosHeader = (PIMAGE_DOS_HEADER)pBuffer;  
    if (*((PDWORD)((DWORD)pBuffer + pDosHeader->e_lfanew)) != IMAGE_NT_SIGNATURE)  
    {  
    printf("(RvaToFileOffset)Not a valid PE flag!\n");  
    return 0;  
    }  
      
    printf("ImageOffset: %#x\n", dwRva);  
    pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pBuffer + pDosHeader->e_lfanew);  
    pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4); // 这里必须强制类型转换  
    pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);  
    pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);  
      
    PIMAGE_SECTION_HEADER pSectionTemp = pSectionHeader;  
      
    if (dwRva <= pOptionHeader->SizeOfHeaders)  
    return (DWORD)dwRva;  
    else  
    {  
    for (int n = 0; n < pPEHeader->NumberOfSections; n++, pSectionTemp++)  
    {   //判断 :   文件对齐+文件偏移>file_panyi>文件偏移  (即是在文件的哪个节中)  
    if ((dwRva >= pSectionTemp->VirtualAddress) && (dwRva < pSectionTemp->VirtualAddress + pSectionTemp->Misc.VirtualSize))  
    {  
    return dwRva - pSectionTemp->VirtualAddress + pSectionTemp->PointerToRawData;  
    }  
    }  
    }  
    printf("RvaToFoa failed！\n");  
    return 0;  
    }  
      
    DWORD FoaToImageOffset(PVOID pBuffer, DWORD dwFoa)  
    {  
    PIMAGE_DOS_HEADER pDosHeader = NULL;  
    PIMAGE_NT_HEADERS pNTHeader = NULL;  
    PIMAGE_FILE_HEADER pPEHeader = NULL;  
    PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;  
    PIMAGE_SECTION_HEADER pSectionHeader = NULL;  
      
    if (!pBuffer)  
    {  
    printf("(FoaToImageOffset)Can't open file!\n");  
    return 0;  
    }  
      
    if (*((PWORD)pBuffer) != IMAGE_DOS_SIGNATURE)  
    {  
    printf("(FoaToImageOffset)No MZ flag, not exe file!\n");  
    return 0;  
    }  
      
    pDosHeader = (PIMAGE_DOS_HEADER)pBuffer;  
    if (*((PDWORD)((DWORD)pBuffer + pDosHeader->e_lfanew)) != IMAGE_NT_SIGNATURE)  
    {  
    printf("(FoaToImageOffset)Not a valid PE flag!\n");  
    return 0;  
    }  
    printf("FileOffset: %#x\n", dwFoa);  
      
    pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pBuffer + pDosHeader->e_lfanew);  
    pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4); // 这里必须强制类型转换  
    pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);  
    pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);  
      
    PIMAGE_SECTION_HEADER pSectionTemp = pSectionHeader;  
      
    if (dwFoa <= pOptionHeader->SizeOfHeaders)  
    return (DWORD)dwFoa;  
    else  
    {  
    for (int n = 0; n < pPEHeader->NumberOfSections; n++, pSectionTemp++)  
    {   //判断 :   文件对齐+文件偏移>file_panyi>文件偏移  (即是在文件的哪个节中)  
    if ((dwFoa >= pSectionTemp->PointerToRawData) && (dwFoa < pSectionTemp->PointerToRawData + pSectionTemp->SizeOfRawData))  
    {  
    return dwFoa - pSectionTemp->PointerToRawData + pSectionTemp->VirtualAddress;  
    }  
    }  
    }  
    printf("FoaToRva failed！\n");  
    return 0;  
    }  
      
    VOID operate()  
    {  
    LPVOID pFileBuffer = NULL;  
    LPVOID pNewFileBuffer = NULL;  
    LPVOID pImageBuffer = NULL;  
    size_t pRVA = 0x0003123;  
    size_t pFOA = 0x00020450;  
      
    DWORD ret1 = ToLoaderPE(file_path, &pFileBuffer);  // &pFileBuffer(void**类型) 传递地址对其值可以进行修改  
    printf("exe->filebuffer  返回值为计算所得文件大小：%#x\n", ret1);  
      
    DWORD ret_FOA1 = RvaToFileOffset(pFileBuffer, pRVA);  
    printf("内存偏移%#x 转换为文件中的偏移: %#x\n", pRVA, ret_FOA1);  
    DWORD ret_RVA1 = FoaToImageOffset(pFileBuffer, pFOA);  
    printf("文件偏移%#x 转换为内存中的偏移: %#x\n", pFOA, ret_RVA1);  
      
    free(pFileBuffer);  
    free(pNewFileBuffer);  
    free(pImageBuffer);  
    }  
      
    int main()  
    {  
    operate();  
    getchar();  
    return 0;  
    }

