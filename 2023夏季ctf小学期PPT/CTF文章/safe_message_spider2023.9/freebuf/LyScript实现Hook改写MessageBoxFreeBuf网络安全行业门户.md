LyScript
可实现自定义汇编指令的替换功能，用户可以自行编写一段汇编指令，将程序中特定的通用函数进行功能改写与转向操作，此功能原理是简单的Hook操作。

  * 项目地址：https://github.com/lyshark/lyscript

首先我们先来实现一个Hook模板，在代码中实现中转机制，如下代码以`MessageBoxA`函数为案例实现修改汇编参数传递。

    
    
    from LyScript32 import MyDebug
    
    # 传入汇编列表,写出到内存
    def assemble(dbg, address=0, asm_list=[]):
        asm_len_count = 0
        for index in range(0,len(asm_list)):
            # 写出到内存
            dbg.assemble_at(address, asm_list[index])
            # print("地址: {} --> 长度计数器: {} --> 写出: {}".format(hex(address + asm_len_count), asm_len_count,asm_list[index]))
            # 得到asm长度
            asm_len_count = dbg.assemble_code_size(asm_list[index])
            # 地址每次递增
            address = address + asm_len_count
    
    if __name__ == "__main__":
        dbg = MyDebug()
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        # 找到MessageBoxA
        messagebox_address = dbg.get_module_from_function("u.dll","MessageBoxA")
        print("MessageBoxA内存地址 = {}".format(hex(messagebox_address)))
    
        # 分配空间
        HookMem = dbg.create_alloc(1024)
        print("自定义内存空间: {}".format(hex(HookMem))
        # 写出FindWindowA内存地址,跳转地址
        asm = [
            f"push {hex(HookMem)}",
            "ret"
        ]
    
        # 将列表中的汇编指令写出到内存
        assemble(dbg,messagebox_address,asm)
    
        dbg.close()
    

上方代码中可以看到，首先获取到`MessageBoxA`函数内存地址，然后我们通过`dbg.create_alloc(1024)`分配一段空间，并利用`assemble()`函数写出一个跳转指令。

此段代码执行后，`MessageBoxA`处的指令将被替换，跳转到我们自己分配的内存中去。

接着我们就来实现功能改写，将弹窗中的消息替换成我们自己的版权信息，此处先给出代码。

    
    
    from LyScript32 import MyDebug
    
    # 传入汇编列表,写出到内存
    def assemble(dbg, address=0, asm_list=[]):
        asm_len_count = 0
        for index in range(0,len(asm_list)):
            # 写出到内存
            dbg.assemble_at(address, asm_list[index])
            # print("地址: {} --> 长度计数器: {} --> 写出: {}".format(hex(address + asm_len_count), asm_len_count,asm_list[index]))
            # 得到asm长度
            asm_len_count = dbg.assemble_code_size(asm_list[index])
            # 地址每次递增
            address = address + asm_len_count
    
    if __name__ == "__main__":
        dbg = MyDebug()
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        # 找到MessageBoxA
        messagebox_address = dbg.get_module_from_function("us.dll","MessageBoxA")
        print("MessageBoxA内存地址 = {}".format(hex(messagebox_address)))
    
        # 分配空间
        HookMem = dbg.create_alloc(1024)
        print("自定义内存空间: {}".format(hex(HookMem)))
    
        # 写出FindWindowA内存地址,跳转地址
        asm = [
            f"push {hex(HookMem)}",
            "ret"
        ]
    
        # 将列表中的汇编指令写出到内存
        assemble(dbg,messagebox_address,asm)
    
        # 定义两个变量,存放字符串
        MsgBoxAddr = dbg.create_alloc(512)
        MsgTextAddr = dbg.create_alloc(512)
    
        # 填充字符串内容
        # lyshark 标题
        txt = [0x6c, 0x79, 0x73, 0x68, 0x61, 0x72, 0x6b]
        # 内容 lyshark.com
        box = [0x6C, 0x79, 0x73, 0x68, 0x61, 0x72, 0x6B, 0x2E, 0x63, 0x6F, 0x6D]
    
        for txt_count in range(0,len(txt)):
            dbg.write_memory_byte(MsgBoxAddr + txt_count, txt[txt_count])
    
        for box_count in range(0,len(box)):
            dbg.write_memory_byte(MsgTextAddr + box_count, box[box_count])
    
        print("标题地址: {} 内容: {}".format(hex(MsgBoxAddr),hex(MsgTextAddr)))
    
        # 此处是MessageBox替换后的片段
        PatchCode =\
        [
            "mov edi, edi",
            "push ebp",
            "mov ebp,esp",
            "push -1",
            "push 0",
            "push dword ptr ss:[ebp+0x14]",
            f"push {hex(MsgBoxAddr)}",
            f"push {hex(MsgTextAddr)}",
            "push dword ptr ss:[ebp+0x8]",
            "call 0x76030E20",
            "pop ebp",
            "ret 0x10"
        ]
    
        # 写出到自定义内存
        assemble(dbg, HookMem, PatchCode)
    
        print("地址已被替换,可以运行了.")
        dbg.set_debug("Run")
        dbg.set_debug("Run")
    
        dbg.close()
    

首先程序运行后，会经过`assemble(dbg,messagebox_address,asm)`汇编写出的位置，此处是一个跳转，直接跳转到我们自己申请的内存空间内。

当EIP走到此处后，跳转到我们自己构建的弹窗位置，此处的代码如下。

当弹窗运行后，读入的内存地址有两处`MsgBoxAddr`是消息`MsgTextAddr`是文本，这两处位置都被python中的`push
{hex()}`替换掉了，当运行弹窗后，就是执行我们自己的函数。

