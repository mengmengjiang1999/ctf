作为这题的出题人，出这题的本意是想让解题者学到一些新知识如调试器，内存对齐，异常处理这种，加密这块没有增加太多难度就用了最简单的异或，写出来的人不少，看过一些writeup大部分是因为运气好+加密方式简单猜出的题解，故写下这篇文章，详细介绍下这些知识  
本人水平有限，有些地方可能会写错，还望大家指正。

# 涉及知识

进程替换  
调试器  
pe文件结构

# 逻辑

![image.png](https://image.3001.net/images/20211124/1637744750_619e006ea19e2267fb0dc.png!small)  
用到了进程替换技术，吧源程序按照内存对齐加密后添加到壳子的最后一个节.psb节。为什么要内存对齐后面会讲。  
https://github.com/psbazx/PE_shell  
外壳代码用的是我两年前写的，有兴趣的同学可以看下，只不过题目是64位github上的是32位的，用的话需要吧context结构体的几个寄存器改下，还有就是加个宏。

    
    
    #define DWORD DWORD64
    

64位下context结构体的rce是entry point  
Rdx + 16是imagebase需要在源码上进行修改修改  
![image.png](https://image.3001.net/images/20211124/1637744934_619e012636226262eb9c3.png!small)  
下面讲下程序脱壳逻辑，首先获取最后一个节.psb节，然后进行xor解密，接着创建子进程，卸载内存镜像并把节的内容拷贝过去，然后调用ResumeThread恢复线程运行，子进程就跑起来了，接着父进程起了个调试器接受子进程的异常和opcode。  
![image.png](https://image.3001.net/images/20211124/1637745099_619e01cb4f610407acec6.png!small)  
处理三次异常，第一次是int3异常，父进程调用ReadProcessMemory读取录入的flag内容然后xor
0x78后写回去，还有俩次异常是接收到了异常指令即opcode，单纯修改rip。  
父进程逻辑就这些，接着看子进程。  
想获取子进程很简单，可以直接dump，但是上面说了再加壳的时候就已经按照内存对齐加进去了，假如说解题人不太了解内存对齐和文件对齐，看到有个pe文件被解密出来后直接dump然后脱进ida看是看不到啥逻辑的。  
看过一些writeup，貌似很多人都没发现这点，部分同学用的特征码定位到了main函数，也是个不错的方法，长见识了。  
当然最优雅的方式还需要进行一个简单的修复，代码如下，然后可以看到逻辑：

    
    
    #define _CRT_SECURE_NO_DEPRECATE
    #include <stdio.h>
    #include <windows.h>
    #define DWORD DWORD64
    LPVOID ImageBufferToFileBuffer(BYTE* decodebuffer, DWORD& size);
    int main()
    {
        FILE* a;
        DWORD size;
        const char shelladdr[] = "C:\\Users\\pisanbao\\Dropbox\\My PC (DESKTOP-TIPJDRO)\\Desktop\\dump.exe";
        a = fopen(shelladdr, "rb");
        fseek(a, 0, SEEK_END);
        unsigned long long filesize = ftell(a);
        fseek(a, 0, SEEK_SET);
        DWORD* filebuffer = (DWORD*)calloc(1, filesize);
        fread(filebuffer, filesize, 1, a);
        fclose(a);
        LPVOID encryptFileBuffer = ImageBufferToFileBuffer((BYTE*)filebuffer, size);
        FILE* b;
        b = fopen("C:\\Users\\pisanbao\\Dropbox\\My PC (DESKTOP-TIPJDRO)\\Desktop\\dump1.exe", "wb");
        fwrite(encryptFileBuffer, size, 1, b);
        fclose(b);
        return 0;
    }
    
    LPVOID ImageBufferToFileBuffer(BYTE* decodebuffer, DWORD& size)
    {
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER pOptionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader_LAST = NULL;
    
    
        pDosHeader = (PIMAGE_DOS_HEADER)decodebuffer;
        pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)decodebuffer + pDosHeader->e_lfanew);
        pPEHeader = (PIMAGE_FILE_HEADER)(((DWORD)pNTHeader) + 4);
        pOptionHeader = (PIMAGE_OPTIONAL_HEADER)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);
        pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);
        pSectionHeader_LAST = (PIMAGE_SECTION_HEADER)((DWORD)pSectionHeader + (pPEHeader->NumberOfSections - 1) * 40);
    
        unsigned int fileLength = pSectionHeader_LAST->PointerToRawData + pSectionHeader_LAST->SizeOfRawData;
        size = pNTHeader->OptionalHeader.SizeOfImage;
        BYTE* pEncryptBuffer = (BYTE*)malloc(size);
        memset(pEncryptBuffer, 0, size);
        memcpy(pEncryptBuffer, decodebuffer, pNTHeader->OptionalHeader.SizeOfHeaders);
        int i;
        for (i = 0; i < pNTHeader->FileHeader.NumberOfSections; i++)
        {
            memcpy(pEncryptBuffer + pSectionHeader->PointerToRawData, decodebuffer + pSectionHeader->VirtualAddress, pSectionHeader->SizeOfRawData);
            pSectionHeader++;
        }
        return pEncryptBuffer;
    }
    

子进程本身不能跑，必须配合父进程，源代码里有许多垃圾代码和非法指令目的是为了防止静态分析，打乱正常逻辑，必须要在父进程的配合下才能走到正确逻辑，但因为加密算法过于简单被人猜出来了子进程只有一个xor操作  
![image.png](https://image.3001.net/images/20211124/1637745389_619e02ed942f03cc0336a.png!small)  
子进程一开始录入flag，然后int3触发异常，父进程接收到异常后对flag进行xor 操作，  
接着遇到0xc4 0x12非法指令。  
![image.png](https://image.3001.net/images/20211124/1637745468_619e033ceb931a3532f59.png!small)  
父进程读取opcode，对rip进行操作  
![image.png](https://image.3001.net/images/20211124/1637745575_619e03a72dfdf434a86d4.png!small)  
然后子进程会跑到这运行，其实就是xor i的操作，  
跑完后遇到结尾的0xc4 0x48非法指令后父进程再次修改rip，进入最终比较。  
逻辑很简单，就是一个xor，但是涉及到的知识比较多，主要是想让人学到东西，没准备增加难度//其实是懒。  
解题脚本如下：

    
    
    a = [30, 21, 27, 28, 7, 77, 31, 27, 18, 23, 75, 68, 71, 88, 18, 71, 88, 88, 71, 95, 84, 84, 88, 66, 89, 87, 80, 1, 73, 81, 83, 87, 61, 107, 62, 111, 61, 109, 108, 62, 105, 44]
    flag = ''
    for i in range(len(a)):
    	flag += chr(a[i]^0x78^i)
    print flag
    

这题写出来的人挺多的，属于是把我吓到了，本来以为就这些操作已经能难倒很多人了。  
基于这种框架(进程替换配合调试器)还能加难度，比如配合vm，新增一些反调试。。。有机会尝试下。

