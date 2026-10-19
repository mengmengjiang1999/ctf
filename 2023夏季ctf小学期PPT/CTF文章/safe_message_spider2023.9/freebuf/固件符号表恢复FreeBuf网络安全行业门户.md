# 固件符号表恢复

使用IDA打开固件的时候，有的时候无法识别真实的函数名，即便固件中能够找到符号表，这时就需要我们手动修复

通常情况下，我们会使用IDAPython来进行批量恢复

代码如下：

    
    
    #coding=utf-8  
    from idaapi import *  
    from idc import *  
    ​  
    symbol_interval = 16 # 符号表间隔  
    load_address = 0x10000 # 固件内存加载基址  
    symbol_table_start = 0x31eec4 + load_address   # 符号表起始地址  
    symbol_table_end = 0x348114 + load_address # 符号表结束地址  
    ea = symbol_table_start  
    eaEnd = symbol_table_end  
    ​  
    while ea < eaEnd:  
      offset = 0   # 4个字节为一组数据  
      # 将函数名指针位置的数据转换为字符串  
      create_strlit(Dword(ea-offset), BADADDR)  
      # 将函数名赋值给变量sName  
      sName = get_strlit_contents(Dword(ea - offset), -1, ASCSTR_C)  
      print(sName)  
      if sName:  
          # 开始修复函数名  
          eaFunc = Dword(ea - offset +4)  
          # 将eaFunc指向的地址重命名  
          MakeName(eaFunc, sName)  
          # 在eaFunc处创建指令  
          MakeCode(eaFunc)  
          # 将eaFunc定义成一个新函数  
          MakeFunction(eaFunc, BADADDR)  
      ea += symbol_interval

具体的功能在注释中都已备注，详细可以参考：<https://hex-rays.com/products/ida/support/idadoc/>

![1644545764_6205c6e4da4859a8b21da.png!small](https://image.3001.net/images/20220211/1644545764_6205c6e4da4859a8b21da.png!small)

![1644545772_6205c6ec7542235e06cec.png!small](https://image.3001.net/images/20220211/1644545772_6205c6ec7542235e06cec.png!small)

运行完后，的确可以识别符号表并恢复函数名称

但是实际上，该脚本只能在ida7.4（不包括ida7.4）之前的版本使用

在ida7.4版本之后，因为很多IDAPython的API都发生了改变，所以脚本也需要修改

API详细可以参考 <https://hex-rays.com/products/ida/support/ida74_idapython_no_bc695_porting_guide.shtml>

上述脚本中，主要是以下这几个函数发生了改变

before| after  
---|---  
idc.Dword| idc.get_wide_dword  
idc.MakeName(ea, name)| idc.set_name(ea, name, SN_CHECK)  
idc.MakeCode| idc.create_insn  
idc.MakeFunction| ida_funcs.add_func  
  
所以，修改后的脚本

    
    
    #coding=utf-8  
    from idaapi import *  
    from idc import *  
    ​  
    symbol_interval = 16 #符号表间隔  
    load_address = 0x10000 #固件内存加载基址  
    symbol_table_start = 0x31eec4 + load_address   #符号表起始地址  
    symbol_table_end = 0x348114 + load_address #符号表结束地址  
    ea = symbol_table_start  
    eaEnd = symbol_table_end  
    ​  
    while ea < eaEnd:  
      offset = 0   #4个字节为一组数据  
      #将函数名指针位置的数据转换为字符串  
      create_strlit(get_wide_dword(ea-offset), BADADDR)  
      #将函数名赋值给变量sName  
      sName = get_strlit_contents(get_wide_dword(ea))  
      print(sName)  
      if sName:  
          #开始修复函数名  
          eaFunc = get_wide_dword(ea - offset +4)  
          set_name(eaFunc, sName)  
          create_insn(eaFunc)  
          ida_funcs.add_func(eaFunc, BADADDR)  
      ea += symbol_interval

该脚本可以在python7.4以后的版本中使用，测试的是`7.4.191112`-`7.6.210427`均可以使用

另外，在python7.4之后，ida开始支持python3，上述脚本是适用于python2环境下的

python3版本的话，所对应的脚本也需要更改

如何确定自己的ida中python版本

打开ida后，在左下角的交互窗口里输入

    
    
    import sys  
    print(sys.version)

  * python2

![1644545793_6205c7016b63720733735.png!small](https://image.3001.net/images/20220211/1644545793_6205c7016b63720733735.png!small)

  * python3

![1644545799_6205c707cf07cd3f20c4b.png!small](https://image.3001.net/images/20220211/1644545799_6205c707cf07cd3f20c4b.png!small)

可以在回显里查看python版本

python2和python3不一样的是：在python3中，`get_strlit_contents`返回的是`bytes`类型

![1644545806_6205c70eb8b40d47ae1db.png!small](https://image.3001.net/images/20220211/1644545806_6205c70eb8b40d47ae1db.png!small)

而`set_name`需要的是字符串类型

![1644545824_6205c720769eafb8c2133.png!small](https://image.3001.net/images/20220211/1644545824_6205c720769eafb8c2133.png!small)

如果python版本是3.x，则需要把上面的脚本加一行

    
    
    #coding=utf-8  
    from idaapi import *  
    from idc import *  
    ​  
    symbol_interval = 16 #符号表间隔  
    load_address = 0x10000 #固件内存加载基址  
    symbol_table_start = 0x31eec4 + load_address   #符号表起始地址  
    symbol_table_end = 0x348114 + load_address #符号表结束地址  
    ea = symbol_table_start  
    eaEnd = symbol_table_end  
    ​  
    while ea < eaEnd:  
      offset = 0   #4个字节为一组数据  
      #将函数名指针位置的数据转换为字符串  
      create_strlit(get_wide_dword(ea-offset), BADADDR)  
      #将函数名赋值给变量sName  
      sName = get_strlit_contents(get_wide_dword(ea))  
      print(sName)  
      if sName:  
          #将bytes转为str  
          sName = str(sName,encoding="utf-8")  
          #开始修复函数名  
          eaFunc = get_wide_dword(ea - offset +4)  
          set_name(eaFunc, sName)  
          create_insn(eaFunc)  
          ida_funcs.add_func(eaFunc, BADADDR)  
      ea += symbol_interval

`sName = str(sName,encoding="utf-8")`就可以将返回的bytes类型sName转为str类型sName，其他无需修改。

