LyScript插件中提供了三种基本的堆栈操作方法，其中`push_stack`用于入栈，`pop_stack`用于出栈，而最有用的是`peek_stack`函数，该函数可用于检查指定堆栈位置处的内存参数，利用这个特性就可以实现，对堆栈地址的检测，或对堆栈的扫描等。

LyScript项目地址：https://github.com/lyshark/LyScript

peek_stack命令传入的是堆栈下标位置默认从0开始，并输出一个`十进制有符号`长整数，首先实现有符号与无符号数之间的转换操作，为后续堆栈扫描做准备。

    
    
    from LyScript32 import MyDebug
    
    # 有符号整数转无符号数
    def long_to_ulong(inter,is_64 = False):
        if is_64 == False:
            return inter & ((1 << 32) - 1)
        else:
            return inter & ((1 << 64) - 1)
    
    # 无符号整数转有符号数
    def ulong_to_long(inter,is_64 = False):
        if is_64 == False:
            return (inter & ((1 << 31) - 1)) - (inter & (1 << 31))
        else:
            return (inter & ((1 << 63) - 1)) - (inter & (1 << 63))
    
    if __name__ == "__main__":
        dbg = MyDebug()
    
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        for index in range(0,10):
    
            # 默认返回有符号数
            stack_address = dbg.peek_stack(index)
    
            # 使用转换
            print("默认有符号数: {:15} --> 转为无符号数: {:15} --> 转为有符号数: {:15}".
                  format(stack_address, long_to_ulong(stack_address),ulong_to_long(long_to_ulong(stack_address))))
    
        dbg.close()
    

通过上述封装函数，即可实现对有符号和无符号数的转换。

![](https://image.3001.net/images/20220823/1661233201_6304683167253bf8b3d1a.png!small)

继续完善该功能，我们使用`get_disasm_one_code()`函数，扫描堆栈地址并得到该地址处的反汇编代码。

    
    
    from LyScript32 import MyDebug
    
    # 有符号整数转无符号数
    def long_to_ulong(inter,is_64 = False):
        if is_64 == False:
            return inter & ((1 << 32) - 1)
        else:
            return inter & ((1 << 64) - 1)
    
    # 无符号整数转有符号数
    def ulong_to_long(inter,is_64 = False):
        if is_64 == False:
            return (inter & ((1 << 31) - 1)) - (inter & (1 << 31))
        else:
            return (inter & ((1 << 63) - 1)) - (inter & (1 << 63))
    
    if __name__ == "__main__":
        dbg = MyDebug()
    
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        for index in range(0,10):
    
            # 默认返回有符号数
            stack_address = dbg.peek_stack(index)
    
            # 反汇编一行
            dasm = dbg.get_disasm_one_code(stack_address)
    
            # 根据地址得到模块基址
            if stack_address <= 0:
                mod_base = 0
            else:
                mod_base = dbg.get_base_from_address(long_to_ulong(stack_address))
    
            print("stack => [{}] addr = {:10} base = {:10} dasm = {}".format(index, hex(long_to_ulong(stack_address)),hex(mod_base), dasm))
    
        dbg.close()
    

得到的堆栈参数如下：

![](https://image.3001.net/images/20220823/1661233202_63046832118ceb9453c9a.png!small)

由此我们可以得到堆栈处的反汇编参数，但如果我们需要检索堆栈特定区域内是否存在返回到模块的地址，该如何实现呢？

![](https://image.3001.net/images/20220823/1661233202_63046832ab7bf6cadea9e.png!small)

其实很简单，首先我们需要得到程序全局状态下的所有加载模块的基地址，然后得到当前堆栈内存地址内的实际地址，并通过实际内存地址得到模块基地址，对比全局表即可拿到当前模块是返回到了哪里。

    
    
    from LyScript32 import MyDebug
    
    # 有符号整数转无符号数
    def long_to_ulong(inter,is_64 = False):
        if is_64 == False:
            return inter & ((1 << 32) - 1)
        else:
            return inter & ((1 << 64) - 1)
    
    # 无符号整数转有符号数
    def ulong_to_long(inter,is_64 = False):
        if is_64 == False:
            return (inter & ((1 << 31) - 1)) - (inter & (1 << 31))
        else:
            return (inter & ((1 << 63) - 1)) - (inter & (1 << 63))
    
    if __name__ == "__main__":
        dbg = MyDebug()
    
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        # 得到程序加载过的所有模块信息
        module_list = dbg.get_all_module()
    
        # 向下扫描堆栈
        for index in range(0,10):
    
            # 默认返回有符号数
            stack_address = dbg.peek_stack(index)
    
            # 反汇编一行
            dasm = dbg.get_disasm_one_code(stack_address)
    
            # 根据地址得到模块基址
            if stack_address <= 0:
                mod_base = 0
            else:
                mod_base = dbg.get_base_from_address(long_to_ulong(stack_address))
    
            # print("stack => [{}] addr = {:10} base = {:10} dasm = {}".format(index, hex(long_to_ulong(stack_address)),hex(mod_base), dasm))
            if mod_base > 0:
                for x in module_list:
                    if mod_base == x.get("base"):
                        print("stack => [{}] addr = {:10} base = {:10} dasm = {:15} return = {:10}"
                              .format(index,hex(long_to_ulong(stack_address)),hex(mod_base), dasm,
                                      x.get("name")))
    
        dbg.close()
    

运行后，即可扫描到堆栈内的所有返回模块的位置。

![](https://image.3001.net/images/20220823/1661233203_630468332c5b3535fd2c2.png!small)

