# 恶意代码常用API混淆方法及处理方式

阅读量 **264881**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-19 10:30:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0146cbe6a081bd8c7a.png)

## 1.摘要

我们在分析恶意代码时经常会遇到，静态分析恶意代码时导入表没有任何导入函数的情况，这种情况通常是恶意代码混淆了API，很多恶意代码尝试混淆它们使用的API来对抗静态分析，API被混淆后静态分析几乎无法得到有效的信息，下面我总结了恶意代码经常用到的混淆API的方法，和处理它们的方法

## 2.恶意代码常用api混淆方法

第一种恶意代码自己创建IAT，自己实现类似于LoadLibrary和GetProcAddress功能的函数，传入的参数也通常是dll名和函数名的hash值，将函数地址存入指针数组，然后通过指针数组调用不同的函数，下面介绍的mailto勒索软件就属于这种

第二种恶意代码计算出真正的函数入口点后，使用jmp指令跳转过去，xshell后门的shellcode用的就是这种方法

![](https://p2.ssl.qhimg.com/t01afc8cceeb83f4a54.png)

第三种将真正的函数入口点加密后存储到全局变量中，调用函数时，将全局变量解密即是函数真正的入口点，下文介绍的xdata勒索软件使用的就是此方法

第四中抹去DOS头，一般恶意代码在shellcode中经常使用，用来对抗内存取证工具或躲避杀软对进程注入pe文件
的检测，下文介绍的ccleaner后门使用的就是这种方法

## 3.解决api混淆的方法

### **3.1 idapython**

以mailto勒索软件为例（MD5:3D6203DF53FCAA16D71ADD5F47BDD060)，首先分析下样本混淆API的方式，样本自己创建IAT，通过用自己实现的函数MwLoadDll来获取dll基址和MwImportApi获取导入函数的地址，MwLoadDll是以dll名的hash值作为参数，MwImportApi是以模块基址和函数名hash值作为参数

![](https://p2.ssl.qhimg.com/t010da088a05044c871.png)

MwLoadDll函数是通过FS:[0x30]获取PEB，在通过PEB结构体OxC偏移获取PPEB_LDR_DATA指针，在根据_PEB_LDR_DATA结构体的0x14偏移获取InMemoryOrderModuleList链表，此链表是指向LDR_MODULE结构体的双向链表，在遍历此链表，计算每个模块名的hash值是否与传入的相等，相等则返回模块的基址

![](https://p2.ssl.qhimg.com/t0174800ef0f97be2d5.png)

MwImportApi函数是通过dll模块的pe结构遍历其导出表，分别计算各个导出函数的hash值是否与传递的hash值相等，相等就返回此函数的地址并将其存入指针数组中

![](https://p1.ssl.qhimg.com/t0164e19750d28a8925.png)

之后样本调用函数都通过这个指针数组

![](https://p5.ssl.qhimg.com/t017be9829c44bfe412.png)

![](https://p5.ssl.qhimg.com/t015605093cf9290549.png)

接下来我们开始用idapython来解决样本混淆的API

我们首先需要获取所有MwImportApi函数所传入的hash值和其返回值的偏移量将其一一对应（因为样本的偏移量有几个位置不是有序的，来干扰分析者）

    
    
    for addr in XrefsTo(idc.get_name_ea_simple("MwImportApi"),0):
    if(hex(addr.frm)>hex(0x04013C8)):
    argaddr = addr.frm - 9
    offsetaddr = addr.frm+14
    offsetarg = idc.get_operand_value(offsetaddr,0)
    arghash = idc.get_operand_value(argaddr,0)
    index = int(offsetarg/4)
    apilist[index]=arghash

有了对应的值后，我们用python实现样本所使用的hash算法，mailto根据ida很容易可以识别出此样本使用的是CRC32算法，我们也通过遍历dll的导出表，计算hash值，判断与列表中存储的hash值是否相等，相等就将模块的导出函数名写到列表相应的偏移量上

    
    
    def HashExportNames(pe_path, apilist, hashfunc):
    pe = pefile.PE(pe_path, fast_load=False)
    for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if entry.name != None:
    strtmp = str(entry.name)
    apiname = strtmp[2:len(strtmp)-1]
    apihash = hashfunc(apiname)
    inthash = int(apihash,16)
    if( inthash in apilist ):
    listidx = apilist.index(inthash)
    apilist[listidx] = apiname
    return

最后通过遍历函数名和偏移量对应的列表，自动生成此样本函数指针的结构体头文件，用ida将头文件导入，并将获取指针数组的MwGetApiAddr函数的返回值设置为此结构体指针

    
    
    f = open(APIh_path, 'w')
    f.write("typedef struct MwImportApis{ \n")
    for i in apilist:
    f.write("\tDWORD* %s;\n"%(i))
    
    f.write('}*PApis ;')
    f.close()

或者使用idapython直接创建结构体

    
    
    sid = idc.add_struct(-1,"MwImportApis",0)
    for i in apilist:
    idc.add_struct_member(sid,i,-1,FF_DATA|FF_DWORD,0,4)

到这我们就解决了api混淆问题

解混淆后

![](https://p2.ssl.qhimg.com/t01c4711e87da863969.png)

以上方法处理完后，还是有个不完美的地方，就是无法显示函数参数，为了方便ida静态分析，我们可以使用idapython为结构体中的每个函数设置其函数类型

首先我们通过ida中的结构体名获取结构体，

    
    
    sid = idaapi.get_struc_id("MwImportApis")
    struc = idaapi.get_struc(sid)

之后我们枚举结构体中的所有成员变量

    
    
    def enum_members(struc):
    idx = 0
    while idx != -1:
    member = struc.get_member(idx)
    yield member
    idx = idaapi.get_next_member_idx(struc,member.soff)

最后使用ida_typeinf.get_named_type获取函数类型，然后idaapi.parse_decl2解析此类型，在将结构体中的成员类型设置为此类型，之后ida便会识别出函数参数，方便接下来对样本的后续分析

    
    
    def set_member_type_info(struc,member,decl):
    ti = idaapi.tinfo_t()
    idaapi.parse_decl2(None,decl,ti,0)
    idaapi.set_member_tinfo(struc,member,0,ti,0)

### **3.2模拟执行**

使用ida静态分析时，想要调用恶意代码的某个函数，分析其功能例如字符串解密和api反混淆，模拟执行是很好的选择，常用的插件有flare-emu和qiling，这里以qiling为例处理mailto样本

我们不需要模拟执行整个样本，只需要用qiling模拟执行malito构建iat的函数即可

![](https://p1.ssl.qhimg.com/t017d329574730eec71.png)

我们使用qiling hook
MwImportApi函数的返回地址，获取eax的值即函数的返回值，之后我们在qiling的import_symbols中搜索这个地址，返回函数名

    
    
    from qiling import *
    
    def extract_func_name(ql):
    eax = ql.reg.eax
    func = ql.loader.import_symbols[eax]
    func_name = func["name"].decode("ascii")
    print(f"found {func_name} ")
    
    ql = Qiling(["H:/qiling/examples/bin/mailto.bin"], "B:/qiling_rootfs/x86_windows")
    ql.hook_address(extract_func_name,0x040121A)
    
    ql.run(begin=0x0401360, end=0x0402512)

然后我们再将函数名跟上文一样与指针数组的偏移一一对应，这里就不演示了

模拟执行很耗费时间，执行有大量加密解密操作的函数时，耗费的时间更长

### **3.3 remotelookup**

Remotelookup是fireeye开发的一个工具，它可以枚举进程所加载全部的DLL，计算API地址，构建查找表，首先我们在虚拟机中使用此工具选择恶意代码进程，勾选Allow
Remote Queries（port 9000）

![](https://p0.ssl.qhimg.com/t01e1643eca9bfeae7c.png)

之后我们在主机中使用python，将api地址发送到虚拟机的remoteLookup.exe中，通过搜索构建的查找表返回函数名，我们在将ida中地址修改为函数名

以xdata勒索软件为例（MD5:A0A7022CAA8BD8761D6722FE3172C0AF)，首先简单介绍下xdata混淆API的原理，xdata将函数地址与密钥异或存储到全局变量中

![](https://p2.ssl.qhimg.com/t016c33e3843be331d8.png)

样本调用函数时用全局变量与密钥异或即可获取函数真正的入口点

![](https://p3.ssl.qhimg.com/t01f81f6f6ddbc5d12d.png)

下面介绍使用Remotelookup处理xdata混淆API的方法

首先我们使用OD获取全局变量中存储的API入口点加密后的值

![](https://p2.ssl.qhimg.com/t017d9f5bb1b557556f.png)

将这些值存储到文件中，我们修改remotelookup提供的示例，依次读取这些加密后的值对它们进行异或解密获取真正的函数入口点，然后将函数入口点传到虚拟机中的remotelookup.exe，通过查找构建的查找表返回函数名，我们再将ida全局变量的地址重命名为对应的函数名

    
    
    if remote.attach(6436):
    start=0x04121C0
    end=0x41248C
    base=0x43C1FBF5
    
    while start < end:
    temp = get_encoded_address(start)
    real_address = base^temp
    addr=str(hex(real_address))
    addr=addr[2:10]
    if remote.resolve(addr):
    result=remote.response
    if result.find("Error")==-1 or result.find("Win32Error"):
    result=result.replace(' ','')
    Name=result.split(',')[1]+'0'
    idc.MakeName(start,Name)
    else:
    print (result)
    else:
    print( "Failed:" + remote.response)
    start+=4
    
    else:
    print( 'Failed to attach to pid')

处理前

![](https://p2.ssl.qhimg.com/t0130294e252ad4b9db.png)

处理后

![](https://p5.ssl.qhimg.com/t01b6c80f0035bdf00b.png)

### **3.4修复pe头**

ccleaner后门（MD5:ef694b89ad7addb9a16bb6f26f1efaf7)解密后的shellcode是一个抹去dos头的dll文件，直接使用ida分析，ida无法识别其调用的api，我们可以手动或用工具修复pe文件，修复后ida就可以识别出api，也可以使用Volatility内存取证框架，获取shellcode使用的API和地址，然后导出idc脚本自动命名API

![](https://p1.ssl.qhimg.com/t01513fa4a89640dc7e.png)

修复前

![](https://p5.ssl.qhimg.com/t0144f5eb9de157319c.png)

修复后

![](https://p5.ssl.qhimg.com/t016b0968bb6109fb9c.png)

## 4总结

以上方法足够处理绝大部分恶意代码，有的方法可能使用场景有限，要根据不同的情况，使用不同的方法来处理API混淆

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WINORDIE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237124](/post/id/237124)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [API](/tag/API)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t018a3759a156537d80.png) WINORDIE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

