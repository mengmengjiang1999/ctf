ROP绕过片段简单科普一下，你可以理解成一个可以关闭系统自身内存保护的一段机器指令，这段代码需要我们自己构造，这就涉及到在对端内存搜寻这样的指令，LyScript插件增强了指令片段的查找功能，但需要我们在LyScript插件基础上封装一些方法，实现起来也不难。

LyScript项目地址：https://github.com/lyshark/LyScript

 **封装机器码获取功能:**
首先封装一个方法，当用户传入指定汇编指令的时候，自动的将其转换成对应的机器码，这是为搜索ROP片段做铺垫的，代码很简单，首先`dbg.create_alloc(1024)`在进程内存中开辟堆空间，用于存放我们的机器码，然后调用`dbg.assemble_write_memory(alloc_address,"sub
esp,10")`将一条汇编指令变成机器码写到对端内存，然后再`op = dbg.read_memory_byte(alloc_address +
index)`依次将其读取出来即可。

    
    
    from LyScript32 import MyDebug
    
    # 传入汇编指令,获取该指令的机器码
    def get_assembly_machine_code(dbg,asm):
        pass
    
    if __name__ == "__main__":
        dbg = MyDebug()
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        machine_code_list = []
    
        # 开辟堆空间
        alloc_address = dbg.create_alloc(1024)
        print("分配堆: {}".format(hex(alloc_address)))
    
        # 得到汇编机器码
        machine_code = dbg.assemble_write_memory(alloc_address,"sub esp,10")
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 得到汇编指令长度
        machine_code_size = dbg.assemble_code_size("sub esp,10")
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 读取机器码
        for index in range(0,machine_code_size):
            op = dbg.read_memory_byte(alloc_address + index)
            machine_code_list.append(op)
    
        # 释放堆空间
        dbg.delete_alloc(alloc_address)
    
        # 输出机器码
        print(machine_code_list)
        dbg.close()
    

我们继续封装如上方法，封装成一个可以直接使用的`get_assembly_machine_code`函数。

    
    
    from LyScript32 import MyDebug
    
    # 传入汇编指令,获取该指令的机器码
    def get_assembly_machine_code(dbg,asm):
        machine_code_list = []
    
        # 开辟堆空间
        alloc_address = dbg.create_alloc(1024)
        print("分配堆: {}".format(hex(alloc_address)))
    
        # 得到汇编机器码
        machine_code = dbg.assemble_write_memory(alloc_address,asm)
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 得到汇编指令长度
        machine_code_size = dbg.assemble_code_size(asm)
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 读取机器码
        for index in range(0,machine_code_size):
            op = dbg.read_memory_byte(alloc_address + index)
            machine_code_list.append(op)
    
        # 释放堆空间
        dbg.delete_alloc(alloc_address)
        return machine_code_list
    
    if __name__ == "__main__":
        dbg = MyDebug()
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        # 转换第一对
        opcode = get_assembly_machine_code(dbg,"mov eax,1")
        for index in opcode:
            print("0x{:02X} ".format(index),end="")
        print()
    
        # 转换第二对
        opcode = get_assembly_machine_code(dbg,"sub esp,10")
        for index in opcode:
            print("0x{:02X} ".format(index),end="")
        print()
    
        dbg.close()
    

执行后即可得到结果：

![](https://image.3001.net/images/20220823/1661233399_630468f7df1a55c150039.png!small)

 **扫描符合条件的内存:**
通过使用上方封装的`get_assembly_machine_code()`并配合`scan_memory_one(scan_string)`函数，在对端内存搜索是否存在符合条件的指令。

    
    
    from LyScript32 import MyDebug
    
    # 传入汇编指令,获取该指令的机器码
    def get_assembly_machine_code(dbg,asm):
        machine_code_list = []
    
        # 开辟堆空间
        alloc_address = dbg.create_alloc(1024)
        print("分配堆: {}".format(hex(alloc_address)))
    
        # 得到汇编机器码
        machine_code = dbg.assemble_write_memory(alloc_address,asm)
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 得到汇编指令长度
        machine_code_size = dbg.assemble_code_size(asm)
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 读取机器码
        for index in range(0,machine_code_size):
            op = dbg.read_memory_byte(alloc_address + index)
            machine_code_list.append(op)
    
        # 释放堆空间
        dbg.delete_alloc(alloc_address)
        return machine_code_list
    
    if __name__ == "__main__":
        dbg = MyDebug()
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        # 转换成列表
        opcode = get_assembly_machine_code(dbg,"push eax")
        print("得到机器码列表: ",opcode)
    
        # 列表转换成字符串
        scan_string = " ".join([str(_) for _ in opcode])
        print("搜索机器码字符串: ", scan_string)
    
        address = dbg.scan_memory_one(scan_string)
        print("第一个符合条件的内存块: {}".format(hex(address)))
    
        dbg.close()
    

扫描结果如下：

![](https://image.3001.net/images/20220823/1661233400_630468f88b192d1ec698f.png!small)

将我们需要搜索的ROP指令集片段放到数组内直接搜索，即可直接返回ROP内存地址。

    
    
    from LyScript32 import MyDebug
    
    # 传入汇编指令,获取该指令的机器码
    def get_assembly_machine_code(dbg,asm):
        machine_code_list = []
    
        # 开辟堆空间
        alloc_address = dbg.create_alloc(1024)
        print("分配堆: {}".format(hex(alloc_address)))
    
        # 得到汇编机器码
        machine_code = dbg.assemble_write_memory(alloc_address,asm)
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 得到汇编指令长度
        machine_code_size = dbg.assemble_code_size(asm)
        if machine_code == False:
            dbg.delete_alloc(alloc_address)
    
        # 读取机器码
        for index in range(0,machine_code_size):
            op = dbg.read_memory_byte(alloc_address + index)
            machine_code_list.append(op)
    
        # 释放堆空间
        dbg.delete_alloc(alloc_address)
        return machine_code_list
    
    if __name__ == "__main__":
        dbg = MyDebug()
        connect_flag = dbg.connect()
        print("连接状态: {}".format(connect_flag))
    
        for item in ["push eax","mov eax,1","jmp eax","pop eax"]:
            # 转换成列表
            opcode = get_assembly_machine_code(dbg,item)
            #print("得到机器码列表: ",opcode)
    
            # 列表转换成字符串
            scan_string = " ".join([str(_) for _ in opcode])
            #print("搜索机器码字符串: ", scan_string)
    
            address = dbg.scan_memory_one(scan_string)
            print("第一个符合条件的内存块: {}".format(hex(address)))
    
        dbg.close()
    

检索效果如下：

![](https://image.3001.net/images/20220823/1661233401_630468f940d820e03ad21.png!small)

