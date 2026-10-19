## **前言**

pwn中的off by
one，顾名思义就是单字节缓冲区溢出，其中最常见的是边界验证不严，通常包括循环次数错误和字符串操作不合适而造成的。在对单字节溢出利用时，我们利用ptmalloc进行攻击，今天就来谈谈堆中的off
by one。

##  **利用思路**

溢出字节为可控制任意字节，通过修改大小造成块结构之间出现重叠，从而泄露其他块数据，或是覆盖其他块数据。

**demo：**![](https://image.3001.net/images/20220511/1652250894_627b590e8c9e4d23b8910.png!small)  
my_gets函数执行前：

    
    
    0x602000:   0x0000000000000000  0x00000000000000210x602010:   0x0000000000000000  0x00000000000000000x602020:   0x0000000000000000  0x0000000000000021

my_gets函数执行后：

    
    
    0x602000:   0x0000000000000000  0x00000000000000210x602010:   0x4141414141414141  0x41414141414141410x602020:   0x0000000000000041  0x0000000000000021

可以看到因为循环，多溢出了一个字节，已经到了第二个堆块。

##  **寻找off by one漏洞**

关闭ASLR：

    
    
    echo 0 > /proc/sys/kernel/randomize_va_space

首先我们先checksec一下，发现只有一个canary没开：![](https://image.3001.net/images/20220511/1652250936_627b5938c194ec6b3ccd2.png!small)

执行，发现有六个选项：![](https://image.3001.net/images/20220511/1652250947_627b59435236c1f2d147f.png!small)

首先是这个函数，欢迎的意思：

    
    
    int sub_A77(){return puts("Welcome to ASISCTF book library");}

接着分析下面的函数：

    
    
    signed __int64 sub_B6D(){printf("Enter author name: ");if ( !(unsigned int)sub_9F5(off_202018, 32LL) )return 0LL;printf("fail to read author_name", 32LL);return 1LL;}

这里是写了一个判断，里面有一个函数，紧接着我们看下面，就能够知道这个函数的作用是创建作者名。

###  **SUB_9F5函数：**

    
    
    signed __int64 __fastcall sub_9F5(_BYTE *a1, int a2){int i; // [rsp+14h] [rbp-Ch]_BYTE *buf; // [rsp+18h] [rbp-8h]if ( a2 <= 0 )return 0LL;buf = a1;for ( i = 0; ; ++i ){if ( (unsigned int)read(0, buf, 1uLL) != 1 )return 1LL;if ( *buf == 10 )break;++buf;if ( i == a2 )break;}*buf = 0;return 0LL;

这个函数的功能不难看出，就是内存写入，它的写入内容就是作者名，也就是我们运行程序：![](https://image.3001.net/images/20220511/1652251012_627b5984a8acfbb4cb9e5.png!small)

我们注意到这个函数是有两个参数的，其中第一个参数是一个指针，指向我们存入的地址，第二个参数是32，是一个循环的参数，前面我们介绍了off by
one，循环所致，这里是一个漏洞。

###  **SUB_A89函数：**

    
    
    signed __int64 sub_A89(){signed __int64 result; // raxint v1; // [rsp+Ch] [rbp-4h]v1 = -1;puts("\n1. Create a book");puts("2. Delete a book");puts("3. Edit a book");puts("4. Print book detail");puts("5. Change current author name");puts("6. Exit");printf("> ");__isoc99_scanf("%d", &v1);if ( v1 <= 6 && v1 > 0 )result = (unsigned int)v1;elseresult = 0xFFFFFFFFLL;return result;}

这个就是我们看到的六个选项。

这里解释一下，1代表创建2代表删除3代表编辑4代表打印5代表更换作者名字6代表退出。

下面写了一个判断，如果在1-6区间中，那么就执行对应的功能：

    
    
    default:v3 = (struct _IO_FILE *)"Wrong option";puts("Wrong option");break;

如果不在这个区间，那么就会显示 Wrong
option：![](https://image.3001.net/images/20220511/1652252021_627b5d751a3308f322042.png!small)

    
    
    switch ( (unsigned int)&savedregs ){case 1u:sub_F55();break;

  

接下来就需要我们分析这些功能点了。

###  **创建图书分析：**

    
    
    printf("\nEnter book name size: ", *(_QWORD *)&v2);__isoc99_scanf("%d", &v2);if ( v2 >= 0 ){printf("Enter book name (Max 32 chars): ", &v2);ptr = malloc(v2);

书名放到v2变量中，不超过32个字符，并且创建一个v2大小的堆，调用之前的SUB_9f5函数，往这个堆中写入书名，并且判断是否写入成功。

    
    
    else{v2 = sub_B24();if ( v2 == -1 ){printf("Library is full");

紧接着写一个判断，分配id并且判断是否大于20本。

我们对其进行描述，每本书的格式：

    
    
    struct book{int id;char *name;char *description;int size;}

紧接着创建了0x20个大小的堆，用来存放书的一些相关数据。

    
    
    else{v3 = malloc(0x20uLL);if ( v3 ){*((_DWORD *)v3 + 6) = v1;*((_QWORD *)off_202010 + v2) = v3;*((_QWORD *)v3 + 2) = v5;*((_QWORD *)v3 + 1) = ptr;*(_DWORD *)v3 = ++unk_202024;return 0LL;}.data:0000000000202010 off_202010      dq offset unk_202060    ; DATA XREF: sub_B24:loc_B38↑o.data:0000000000202010                                         ; sub_BBD:loc_C1B↑o ....data:0000000000202018 off_202018      dq offset unk_202040    ; DATA XREF: sub_B6D+15↑o

我们不难看出，202010和202018，10代表的是作者名，18代表的是图书名。这两个是挨着的，如果我们将作者名输入32个字节的字符串，那么循环多出来的一次会将\x00写到off_202010的起始第一个字节，也就是说会将创建的第一本图书的低字节覆盖掉，这样就能够实现off
by one的漏洞利用。

##  **小结**

在书写代码的时候，我们要注意>和>=类似这样的区别，不然很容易造成off by one这种类似漏洞的发生。

