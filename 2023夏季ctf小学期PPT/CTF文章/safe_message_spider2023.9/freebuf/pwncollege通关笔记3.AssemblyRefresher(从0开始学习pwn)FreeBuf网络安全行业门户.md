# 0x1.前言

到第三部分了，撒花✿✿ヽ(°▽°)ノ✿。

第三部分是装配复习，直译过来是这样的。

看了看具体的关卡是啥后，感觉可能就是汇编链接过程的复习吧。

这次居然把讲解写到了关卡里，运行程序就能得到讲解，针不戳~

题目地址：https://dojo.pwn.college/challenges/asm

这一部分主要涉及到汇编语言的相关知识，如果有过汇编学习基础的同学当然更容易上手，没有问题也不大，因为关卡的讲解就是从基础开始讲起，然后每个挑战都是让你用汇编代码实现一些功能。

# 0x2.通关记录

这里面的关卡还真不太熟悉，不知道怎么去做，基本上明白是把指定汇编代码的汇编结果二进制输入进去就可以了，但是不太清楚到底怎么做。

直到把官方的教学视频看完之后才知道了一些东西：[CSE 466 : Computer Systems Security - Extended Q&A -08/31/2021](https://youtu.be/qr4mlLDn4so)

之前也学到过x8086的基础，这个汇编指令版本也基本类似，毕竟好像都是x86系列的，还是很不错的。

## level0：linux常用工具使用

 **1.gcc编译链接**

gcc除了可以编译链接c语言后，还可以直接编译链接汇编代码。

如果用汇编代码，一般是用不到std库和os共享库的，可以用**-nostdlib **和** -static**参数来处理，如下：

    
    
    gcc -nostdlib -static exit.s -o exit
    

这样就能避免导入std库，也不用有main函数，同时采用静态链接的当时不会再引用动态库

 **2.strace显示执行过程**

直接用strace来运行程序，会显示进程进行的每一个步骤。

 **3.objdump显示二进制程序的所有模块**

可以显示所有模块：

利用`-M`指定指令集格式

`-d`反汇编全部。

    
    
    objdump -M intel -d exit.elf
    

**4.objcopy提取二进制程序模块**

objcopy可以将二进制程序中的模块汇编代码单独提取出来，以方便我们利用。

如下：

    
    
    objcopy --dump-section .text=exit.bin exit.elf
    

这样就可以把text模块的代码对应的二进制提取出来，放到exit.bin文件中。

## level1：mov

 **命令行通过：**

汇编代码：

1.s内容：

（第一关先放上标准的文件头，之后就不放了，只放代码主体）

    
    
    .global _start
    _start:
    .intel_syntax noprefix
            mov rdi, 0x1337
    

编译链接：

    
    
    gcc -nostdlib -static 1.s
    

然后提取出二进制后输入到挑战程序中，利用管道连接：

    
    
    objcopy --dump-section .text=b.bin a.out && cat b.bin | /challenge/embryoasm_level*
    

**python代码通过：**

用命令行方式还是有些繁琐了，如果能用python最好不过了，pwntools是有这个功能的。

另外用命令行方式的话提取的二进制会多一个0x48，反汇编之后是 **dec eax**
的意思，不过好像并没有被当做命令来显示，应该只是个标志作用，没啥用吧。

1.py：

    
    
    import pwn
    pwn.context.arch = "amd64"
    pwn.context.encoding = "latin"
    pwn.context.log_level = "debug"
    pwn.warnings.simplefilter("ignore")
    
    assembly = """
    	mov rdi, 0x1337
    """
    with pwn.process(f"/challenge/{pwn.os.getenv('HOSTNAME')}") as target:
        pwn.info(target.readrepeat(1))
        target.send(pwn.asm(assembly))
        pwn.info(target.readrepeat(1))
    

mov指令是移动指令，将第二个操作数值移到第一个操作数。

## level2~5：加减乘除

第2关提示：

    
    
    Many instructions exist in x86 that allow you to do all the normal
        math operations on registers_use and memory. For shorthand, when we say
        A += B, it really means, A = A + B. Here are some useful instructions:
        add reg1, reg2       <=>     reg1 += reg2
        sub reg1, reg2       <=>     reg1 -= reg2
        imul reg1, reg2      <=>     reg1 *= reg2
        div  is a littler harder, we will discuss it later.
        Note: all 'regX' can be replaced by a constant or memory location
    

只是让加一次，所以：

    
    
    add rdi,0x331337
    

3：让实现一个f(x) = mx + b的函数：

    
    
    imul rdi,rsi
    add rdi,rdx
    mov rax,rdi
    

4：教了教除法的使用：

    
    
    Recall division in x86 is more special than in normal math. Math in here is
    called integer math. This means everything, as it is now, is in the realm
    of whole looking numbers. As an example:
    10 / 3 = 3 in integer math. Why? Because 3.33 gets rounded down to an integer.
    
    The relevant instructions for this level are:
    mov rax, reg1; div reg2
    Notice: to use this instruction you need to first load rax with the desired register
    you intended to be the divided. Then run div reg2, where reg2 is the divisor. This
    results in:
    rax = rdi / rsi; rdx = remainder
    The quotient is placed in rax, the remainder is placed in rdx.
    

简单来说就是先把被除数放到rax中，然后调用div除以另一个寄存器。

rax存商，而rdx存余数。

    
    
    mov rax,rdi
    div rsi
    

5：考余数，用上一关学到的。

    
    
    mov rax,rdi
    div rsi
    mov rax,rdx
    

## level6：寄存器高低位

6：教了教怎么通过不同的名字利用寄存器的一部分，下面那张图很清楚。

    
    
    Another cool concept in x86 is the independent access to lower register bytes.
    Each register in x86 is 64 bits in size, in the previous levels we have accessed
    the full register using rax, rdi or rsi. We can also access the lower bytes of
    each register using different register names. For example the lower
    32 bits of rax can be accessed using eax, lower 16 bits using ax,
    lower 8 bits using al, etc.
    MSB                                    LSB
    +----------------------------------------+
    |                   rax                  |
    +--------------------+-------------------+
                         |        eax        |
                         +---------+---------+
                                   |   ax    |
                                   +----+----+
                                   | ah | al |
                                   +----+----+
    Lower register bytes access is applicable to all registers_use.
    
    Using only the following instruction(s):
    mov
    Please compute the following:
    rax = rdi modulo 256
    rbx = rsi module 65536
    

简而言之就是一张表，通用寄存器都有这个特性：

    
    
    8位：al，ah
    16位：ax
    32位：eax
    64位：rax
    

他的问题就是让他们分别mod一下，还打错了一个字母，让我以为module是什么新运算找了半天。。

    
    
    mov rcx,rdi		;需要先移到通用寄存器
    mov al,cl		;然后只取低位即可
    mov rdx,rsi
    mov bx,dx
    

## level7~9：逻辑算数运算

7：讲解算数移位

讲解：

    
    
    In this level you will be working with bit logic and operations. This will involve heavy use of directly interacting with bits stored in a register or memory location. You will also likely need to make use of the logic instructions in x86: and, or, not, xor.
    
    Shifting in assembly is another interesting concept! x86 allows you to 'shift'
    bits around in a register. Take for instance, rax. For the sake of this example
    say rax only can store 8 bits (it normally stores 64). The value in rax is:
    rax = 10001010
    We if we shift the value once to the left:
    shl rax, 1
    The new value is:
    rax = 00010100
    As you can see, everything shifted to the left and the highest bit fell off and
    a new 0 was added to the right side. You can use this to do special things to
    the bits you care about. It also has the nice side affect of doing quick multiplication,
    division, and possibly modulo.
    Here are the important instructions:
    shl reg1, reg2       <=>     Shift reg1 left by the amount in reg2
    shr reg1, reg2       <=>     Shift reg1 right by the amount in reg2
    Note: all 'regX' can be replaced by a constant or memory location
    
    Using only the following instructions:
    mov, shr, shl
    Please perform the following:
    Set rax to the 4th least significant byte of rdi
    i.e.
    rdi = | B7 | B6 | B5 | B4 | B3 | B2 | B1 | B0 |
    Set rax to the value of B3
    

x8086中的规则是，移1位时才能用立即数1来指定移的位数，而移多位时则必须用寄存器来指定所移位数，而且被移位的数必须在寄存器中。

但是这里的好像更轻松，所有寄存器都可以用常量代替。

    
    
    mov rax,rdi
    shl rax,32      ;先向高位移位32位
    shr rax,56      ;然后向低位移位24位（需要加上原来32位）
    

8：与或还有异或操作，结果保存在第一个操作数，关卡不让用mov：

    
    
    and rdi,rsi
    xor rax,rax		;需要先异或置零，不然也得不到正确结果
    or rax,rdi
    

9：实现一个简单逻辑，如果x为偶数则y为1，不然y为0

    
    
    and rdi,1
    xor rdi,1
    xor rax,rax
    or rax,rdi
    

## level10~13：内存操作

10：通过中括号包裹可以从指定地址读取数据，即内存操作。

    
    
    Up until now you have worked with registers as the only way for storing things, essentially
    variables like 'x' in math. Recall that memory can be addressed. Each address contains something at that location, like real addresses! As an example: the address '699 S Mill Ave, Tempe, AZ 85281' maps to the 'ASU Campus'. We would also say it points to 'ASU Campus'.  We can represent this like:
    ['699 S Mill Ave, Tempe, AZ 85281'] = 'ASU Campus'
    The address is special because it is unique. But that also does not mean other address cant point to the same thing (as someone can have multiple houses). Memory is exactly the same! For instance,the address in memory that your code is stored (when we take it from you) is 0x400000.
    In x86 we can access the thing at a memory location, called dereferencing, like so:
    mov rax, [some_address]        <=>     Moves the thing at 'some_address' into rax
    This also works with things in registers:
    mov rax, [rdi]         <=>     Moves the thing stored at the address of what rdi holds to rax
    This works the same for writing:
    mov [rax], rdi         <=>     Moves rdi to the address of what rax holds.
    So if rax was 0xdeadbeef, then rdi would get stored at the address 0xdeadbeef:
    [0xdeadbeef] = rdi
    Note: memory is linear, and in x86, it goes from 0 - 0xffffffffffffffff (yes, huge).
    
    Please perform the following:
    1. Place the value stored at 0x404000 into rax
    2. Increment the value stored at the address 0x404000 by 0x1337
    Make sure the value in rax is the original value stored at 0x404000 and make sure
    that [0x404000] now has the incremented value.
    

要求读懂后很简单：

    
    
    mov rax,[0x404000]
    mov rbx,rax
    add rbx,0x1337
    mov [0x404000],rbx
    

11：讲了下不同数据长度的名字：

    
    
    Recall that registers in x86_64 are 64 bits wide, meaning they can store 64 bits in them.
    Similarly, each memory location is 64 bits wide. We refer to something that is 64 bits
    (8 bytes) as a quad word. Here is the breakdown of the names of memory sizes:
    * Quad Word = 8 Bytes = 64 bits
    * Double Word = 4 bytes = 32 bits
    * Word = 2 bytes = 16 bits
    * Byte = 1 byte = 8 bits
    In x86_64, you can access each of these sizes when dereferencing an address, just like using
    bigger or smaller register accesses:
    mov al, [address]        <=>         moves the least significant byte from address to rax
    mov ax, [address]        <=>         moves the least significant word from address to rax
    mov eax, [address]        <=>         moves the least significant double word from address to rax
    mov rax, [address]        <=>         moves the full quad word from address to rax
    Remember that moving only into al for instance does not fully clear the upper bytes.
    
    Please perform the following:
    1) Set rax to the byte at 0x404000
    2) Set rbx to the word at 0x404000
    3) Set rcx to the double word at 0x404000
    4) Set rdx to the quad word at 0x404000
    

代码：

    
    
    mov al,[0x404000]
    mov bx,[0x404000]
    mov ecx,[0x404000]
    mov rdx,[0x404000]
    

12：寄存器间接寻址，顺带提了下小端序：

    
    
    It is worth noting, as you may have noticed, that values are stored in reverse order of how we
        represent them. As an example, say:
        [0x1330] = 0x00000000deadc0de
        If you examined how it actually looked in memory, you would see:
        [0x1330] = 0xde 0xc0 0xad 0xde 0x00 0x00 0x00 0x00
        This format of storing things in 'reverse' is intentional in x86, and its called Little Endian.
    

代码：

    
    
    mov rax,0xDEADBEEF00001337
    mov [rdi],rax
    mov rbx,0x000000C0FFEE0000
    mov [rsi],rbx
    

13：相对寻址

    
    
    mov rax,[rdi]
    mov rbx,[rdi+8]		;注意单位是字节bytes，不是位
    add rax,rbx
    mov [rsi],rax
    

## level14~16：栈操作

14：开始介绍栈

    
    
    In this level you will be working with the Stack, the memory region that dynamically expands
    and shrinks. You will be required to read and write to the Stack, which may require you to use
    the pop & push instructions. You may also need to utilize rsp to know where the stack is pointing.
    
    In these levels we are going to introduce the stack.
    The stack is a region of memory, that can store values for later.
    To store a value a on the stack we use the push instruction, and to retrieve a value we use pop.
    The stack is a last in first out (LIFO) memory structure this means
    the last value pushed in the first value popped.
    Imagine unloading plates from the dishwasher let's say there are 1 red, 1 green, and 1 blue.
    First we place the red one in the cabinet, then the green on top of the red, then the blue.
    Out stack of plates would look like:
    Top ----> Blue
              Green
    Bottom -> Red
    Now if wanted a plate to make a sandwhich we would retrive the top plate from the stack
    which would be the blue one that was last into the cabinet, ergo the first one out.
    
    Subtract rdi from the top value on the stack.
    
    We will now set the following in preparation for your code:
    rdi = 0xc908
    (stack) [0x7fffff1ffff8] = 0x25931854
    

利用pop和push指令即可出栈和入栈，如下：

    
    
    pop rax
    sub rax,rdi
    push rax
    

也可以利用rsp寄存器的值来获取到栈顶的地址然后直接内存操作（其实栈就是内存一部分，只不过多了pop和push这样的操作而已），如下：

    
    
    mov rax,[rsp]
    sub rax,rdi
    mov [rsp],rax
    

15：只让使用push和pop指令交换两个寄存器的值：

    
    
    push rdi
    push rsi
    pop rdi
    pop rsi
    

16：不用pop操作计算4个栈中数的平均数，结果存在栈顶：

    
    
    mov rax,[rsp]
    add rax,[rsp+8]
    add rax,[rsp+16]
    add rax,[rsp+24]
    mov rbx,4
    div rbx
    mov [rsp-8],rax
    sub rsp,8
    

## level17~19：跳转语句

17：开始介绍跳转语句了：

    
    
    In this level you will be working with control flow manipulation. This involves using instructions
    to both indirectly and directly control the special register `rip`, the instruction pointer.
    You will use instructions like: jmp, call, cmp, and the like to implement requests behavior.
    
    Earlier, you learned how to manipulate data in a pseudo-control way, but x86 gives us actual
    instructions to manipulate control flow directly. There are two major ways to manipulate control
    flow: 1. through a jump; 2. through a call. In this level, you will work with jumps. There are
    two types of jumps:
    1. Unconditional jumps
    2. Conditional jumps
    Unconditional jumps always trigger and are not based on the results of earlier instructions.
    As you know, memory locations can store data and instructions. You code will be stored at 0x40006d (this will change each run).
    For all jumps, there are three types:
    1. Relative jumps
    2. Absolute jumps
    3. Indirect jumps
    In this level we will ask you to do both a relative jump and an absolute jump. You will do a relative
    jump first, then an absolute one. You will need to fill space in your code with something to make this
    relative jump possible. We suggest using the `nop` instruction. It's 1 byte and very predictable.
    Useful instructions for this level is:
    jmp (reg1 | addr | offset) ; nop
    Hint: for the relative jump, lookup how to use `labels` in x86.
    
    Using the above knowledge, perform the following:
    Create a two jump trampoline:
    1. Make the first instruction in your code a jmp
    2. Make that jmp a relative jump to 0x51 bytes from its current position
    3. At 0x51 write the following code:
    4. Place the top value on the stack into register rdi
    5. jmp to the absolute address 0x403000
    
    We will now set the following in preparation for your code:
    - Loading your given gode at: 0x40006d
    - (stack) [0x7fffff1ffff8] = 0x8e
    

### 1.重复宏汇编

他要求先相对地址跳转，这里用到了宏汇编技术，宏汇编的代码会在汇编器操作时进行处理而达成比如重复指令等操作，因为要重复0x51次nop，一个nop指令占1字节，重复宏汇编的格式如下：

    
    
    .rept [重复次数]		;开始标志
    	[重复的代码块]
    .endr				;结束标志
    

如果是绝对路径跳转则需要把地址放入寄存器之后再跳转，通关代码：

    
    
    _start:
            jmp next
            .rept 0x51
                    nop
            .endr
    next:
            mov rdi,[rsp]
            mov r12,0x403000
            jmp r12
    

18：要求完成一个简单的if-elif-else逻辑段：

要求：

    
    
    if [x] is 0x7f454c46:
       y = [x+4] + [x+8] + [x+12]
    else if [x] is 0x00005A4D:
       y = [x+4] - [x+8] - [x+12]
    else:
       y = [x+4] * [x+8] * [x+12]
    
    where:
    x = rdi, y = rax. Assume each dereferenced value is a signed dword. This means the values can start asa negative value at each memory position.
    A valid solution will use the following at least once:
    jmp (any variant), cmp
    
    We will now run multiple tests on your code, here is an example run:
    - (data) [0x404000] = {4 random dwords]}
    - rdi = 0x404000
    

代码：

    
    
    mov ebx,[rdi+4]
    mov ecx,[rdi+8]
    mov edx,[rdi+12]
    mov eax,[rdi]
    cmp eax,0x7f454c46
    je con1
    nop
    mov eax,[rdi]
    cmp eax,0x00005A4D
    je con2
    nop
    imul ebx,ecx
    imul ebx,edx
    jmp done
    nop
    con1:
    add ebx,ecx
    add ebx,edx
    jmp done
    nop
    con2:
    sub ebx,ecx
    sub ebx,edx
    done:
    mov eax,ebx
    

19：让用跳转表来跳转，开始没看清楚要求，卡了一会：

    
    
    mov rax,rdi
    and rax,0xfffffffffffffffc
    je nomal
    nop
    jmp [rsi+32]
    nop
    nomal:
    jmp [rsi+rdi*8]
    nop
    

## level20~23：循环结构

20：让编写一个for循环，给一个动态的数列，让求这个数列的平均值，不过这个题目好像有点错误，它说每个数字是qwords，那就是8字节了，应该是dwords，是4字节才对。

    
    
    xor rax,rax
    xor rcx,rcx
    mov rbx,rsi
    loop:
    sub rbx,1
    mov ecx,[rdi+rbx*4]
    add rax,rcx
    cmp rbx,0
    jne loop
    nop
    div rsi
    

21：计数连续的非零数据

    
    
    mov rax,0
    cmp rdi,0
    je done
    mov rsi,-1
    loop:
    add rsi,1
    mov rbx,[rdi+rsi]
    cmp rbx,0
    jne loop
    mov rax,rsi
    done:
    

22：这道题有点坑，题目没怎么说清楚。

需要调用foo函数，虽然得知了他的地址，但是从题目中并不能看出来他怎么获取参数和返回参数，结果是rdi来传参，用rax得到结果，当前函数还必须得保存rax的值

学到了打开调试模式的方法，不然一直找不到func获取参数和返回参数的具体位置：

    
    
    cat 22.bin - | /challenge/embryoasm_level22 DEBUG
    

通关代码：

    
    
    mov rax,0
    mov rsi,rdi
    cmp rsi,0
    je done
    nop
    loop:
    mov bl,[rsi]
    cmp bl,0
    je done
    nop
    cmp bl,90
    ja next
    nop
    mov dil,bl		;将地址发给rdi，因为foo函数的参数从rdi引用
    mov rdx,rax		;调用函数前保存rax的值
    mov rcx,0x403000
    call rcx
    mov [rsi],al
    mov rax,rdx		;使用之后再赋回rax的值，当然也可以直接使用其他寄存器，在函数最后返回时赋给rax
    add rax,1
    next:
    add rsi,1
    jmp loop
    nop
    done:
    ret
    

23：学到了利用栈帧来保存函数中使用的临时变量。

还去格外找了下资料学了下：[C函数调用过程原理及函数栈帧分析](https://www.jianshu.com/p/e7a22923867f)

    
    
    We will be testing your code multiple times in this level with dynamic values! This means we will
    be running your code in a variety of random ways to verify that the logic is robust enough to
    survive normal use. You can consider this as normal dynamic value se
    In this level you will be working with functions! This will involve manipulating both ip control
    as well as doing harder tasks than normal. You may be asked to utilize the stack to save things
    and call other functions that we provide you.
    
    In the previous level, you learned how to make your first function and how to call other functions. Now
    we will work with functions that have a function stack frame. A function stack frame is a set of
    pointers and values pushed onto the stack to save things for later use and allocate space on the stack
    for function variables.
    First, let's talk about the special register rbp, the Stack Base Pointer. The rbp register is used to tell
    where our stack frame first started. As an example, say we want to construct some list (a contigous space
    of memory) that is only used in our function. The list is 5 elements long, each element is a dword.
    A list of 5 elements would already take 5 registers, so instead, we can make pace on the stack! The
    assembly would look like:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ; setup the base of the stack as the current top
    mov rbp, rsp
    ; move the stack 0x14 bytes (5 * 4) down
    ; acts as an allocation
    sub rsp, 0x14
    ; assign list[2] = 1337
    mov eax, 1337
    mov [rbp-0x8], eax
    ; do more operations on the list ...
    ; restore the allocated space
    mov rsp, rbp
    ret
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Notice how rbp is always used to restore the stack to where it originally was. If we don't restore
    the stack after use, we will eventually run out TM. In addition, notice how we subtracted from rsp
    since the stack grows down. To make it have more space, we subtract the space we need. The ret
    and call still works the same. It is assumed that you will never pass a stack address across functions,
    since, as you can see from the above use, the stack can be overwritten by anyone at any time.
    Once, again, please make function(s) that implements the following:
    most_common_byte(src_addr, size):
        b = 0
        i = 0
        for i <= size-1:
            curr_byte = [src_addr + i]
            [stack_base - curr_byte] += 1
        b = 0
    
        max_freq = 0
        max_freq_byte = 0
        for b <= 0xff:
            if [stack_base - b] > max_freq:
                max_freq = [stack_base - b]
                max_freq_byte = b
    
        return max_freq_byte
    Assumptions:
    - There will never be more than 0xffff of any byte
    - The size will never be longer than 0xffff
    - The list will have at least one element
    Constraints:
    - You must put the "counting list" on the stack
    - You must restore the stack like in a normal function
    - You cannot modify the data at src_addr
    

要求就是利用桶排序来找出现次数最多的字节，但是题目中说是不大于0xffff，我还以为是word呢，结果还是byte。

另外就是它这里演示的代码让直接从`[stack_base - 0]`到`[stack_base -(size-1)]`分配空间和利用栈空间，但是我尝试时原栈顶是有数据的，就导致我一直得不到正确结果，慢慢调试才发现。

感觉导致这种情况有两种可能性，一种是题目中的利用没错，就应该从`0~size-1`开辟空间，只是程序的前半部分不知道怎么把栈顶放上了数据；另一种可能性就是题目中的利用错了，应该从`1~size`开辟空间而不能利用栈顶数据，因为人家栈顶有数据。

不管怎么样吧，我往栈里直接推了个0，让它们有运算空间，这样就不会导致错误了：

    
    
    .global _start
    _start:
    .intel_syntax noprefix
    ; 栈顶有数据，并不是空的，按理说不应该直接用栈顶空间的吧，只不过它这里是这样用的，所以我往栈顶推一个0进去以给其利用，这里卡了好久
    push 0
    
    ; ;;;;;;;;;;;;;;;;;;;;;;;;;
    ; ;;Section 1:alloc space;;
    ; ;;;;;;;;;;;;;;;;;;;;;;;;;
    
    ; setup the base of the stack as the current top
    mov rbp,rsp
    ; move rsi size bytes (size * 1) down to save space for local variables
    ; rsi is size，但是其实如果像这样直接用栈顶空间的话这样的分配其实多分配了一字节的空间
    sub rsp,rsi
    
    ; ;;;;;;;;;;;;;;;;;;;;;;;;;
    ; ;;Section 2:read bytes;;;
    ; ;;;;;;;;;;;;;;;;;;;;;;;;;
    
    ; make rax as i,i=0 #让其=-1节省循环
    mov rax,-1
    ; size=size-1 #rsi=rsi-1
    sub rsi,1
    ; make rax as i, rsi as size-1
    loop1:
            add rax,1
            cmp rax,rsi
            ; greater to si for next
            jg next
            nop
            ; make cl as curr_byte
            mov rcx,0
            mov cl,[rdi+rax]
            ; [stack_base - curr_byte] += 1
            mov r11,rbp
            sub r11,rcx
            mov dl,[r11]
            add dl,1
            mov [r11],dl
            jmp loop1
            nop
    
    ; ;;;;;;;;;;;;;;;;;;;;;;;;;
    ; ;;Section 3:find maxfreq;
    ; ;;;;;;;;;;;;;;;;;;;;;;;;;
    
    
    next:
    ; make ax as b, ax=0
    mov rax,0
    ; make bl,cl as max_freq,max_freq_bytes, max_freq=0,max_freq_byte=0
    mov rbx,rax
    mov rcx,rax
    mov ax,-1
    loop2:
            add ax,1
            cmp ax,0xff
            ; greater to return
            jg return
            nop
            ; make dl as [stack_base-b]
            mov r11,rbp
            sub r11,rax
            mov dl,[r11]
            cmp dl,bl
            ; if <= loop2
            jle loop2
            nop
            mov bl,dl
            mov cl,al
            jmp loop2
            nop
    
    return:
    ; return rax
    mov rax,rcx
    ; reset rsp
    mov rsp,rbp
    ; 最后要把那个多分配的空间pop出来，以还原rsp
    pop rbx
    ret
    

清注释版，gcc好像不是识别的汇编的注释，而是还是c类型的注释，不然就会报错：

    
    
    push 0
    mov rbp,rsp
    
    mov rax,-1
    sub rsi,1
    sub rsp,rsi
    loop1:
            add rax,1
            cmp rax,rsi
            jg next
            nop
            mov rcx,0
            mov cl,[rdi+rax]
            mov r11,rbp
            sub r11,rcx
            mov dl,[r11]
            add dl,1
            mov [r11],dl
            jmp loop1
            nop
    
    next:
    mov rax,0
    mov rbx,rax
    mov rcx,rax
    mov ax,-1
    loop2:
            add ax,1
            cmp ax,0xff
            jg return
            nop
            mov r11,rbp
            sub r11,rax
            mov dl,[r11]
            cmp dl,bl
            jle loop2
            nop
            mov bl,dl
            mov cl,al
            jmp loop2
            nop
    
    return:
    mov rax,rcx
    mov rsp,rbp
    pop rbx
    ret
    

