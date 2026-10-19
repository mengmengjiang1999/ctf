#### 通过对1.dll恶意程序分析，得知DllMain的地址是什么？

使用IDA静态反编译，在函数窗口找到 DllMain 函数，定位到地址
1000D02E（新的7.5及以上版IDA会自动定位入口函数，在主窗口左下角可以看到函数名和地址）

![image](https://image.3001.net/images/20220104/1641262351_61d3ad0f6e79fbb11e4b3.png!small)

新版IDA截图

![image](https://image.3001.net/images/20220104/1641262506_61d3adaacd24f4ca2eaf8.png!small)

#### 通过对1.dll恶意程序分析，gethostbyname函数定位到什么地址？

gethostbyname函数在 `导入（Imports）`子视图中可以找到

![image](https://image.3001.net/images/20220104/1641262516_61d3adb4143a28c493c9e.png!small)  
![image](https://image.3001.net/images/20220104/1641262523_61d3adbb404628b797917.png!small)

可以看到地址为 100163CC

#### 接上题，有多少个函数调用了函数gethostbyname

双击进入 gethostbyname 函数，按键盘的X，打开交叉引用窗口

![image](https://image.3001.net/images/20220104/1641262533_61d3adc58915824fdcb8d.png!small)

> ###### CODE XREF:代码交叉引用  
> > 普通流  
> > 调用流 p（看做是Procedure）  
> > 跳转流 j（看做是Jump）

> ###### DATA XREF:数据交叉引用  
> > 读取交叉引用 r（看做是Read）（address何时被读取）  
> > 写入交叉引用 w（看做是Write）（address何时被写入）  
> > 偏移量交叉引用 o（看做是Offset）（address何时被引用）

由图可见类型为p（调用）的不重名函数有5个，即有5个函数调用了函数gethostbyname

#### 通过对1.dll恶意程序分析，详细分析位于0x10001757处的gethostbyname调用，DNS请求将被触发的域名是？

![image](https://image.3001.net/images/20220104/1641262548_61d3add485089f5f28703.png!small)

查看位于0x10001757处的gethostbyname调用情况

![image](https://image.3001.net/images/20220104/1641262554_61d3adda438563c6cfbc2.png!small)

从call开始往上看（也可以`F5`看伪代码），调用传进的参数为eax，eax为地址10019040处字符串偏移13位（0Dh转十进制），双击off_10019040查看，偏移13位后字符串即DNS请求将被触发的域名
pics.praticalmalwareanalysis.com

![image](https://image.3001.net/images/20220104/1641262561_61d3ade1402656ee8b2fd.png!small)  
![image](https://image.3001.net/images/20220104/1641262566_61d3ade69fb52de558bc5.png!small)

#### 通过对1.dll恶意程序分析，IDA Pro识别了在0x10001656处的子函数中的多少个局部变量、多少个参数？

按 `G`输入10001656定位到该位置

![image](https://image.3001.net/images/20220104/1641262572_61d3adeca22a42704a9e5.png!small)

可见子函数中 ptr 后面负值有23个，正值有1个，即IDA识别了该函数中的23个变量，1个参数。

> 也可以看该处伪代码的39-61行
>
>
> ![image](https://image.3001.net/images/20220104/1641262580_61d3adf46c75409b4f686.png!small)

#### 通过对1.dll恶意程序分析，字符串“\cmd.exe /c”位于哪里？

按 `Shift + F12`打开字符串窗口，`Ctrl + F`搜索 \cmd.exe /c ，可见该字符串在 10095B34 位置

![image](https://image.3001.net/images/20220104/1641262589_61d3adfd38bb016f1c450.png!small)

#### 接上题，在引用“\cmd.exe /c” 的代码所在的区域发生了什么？

![image](https://image.3001.net/images/20220104/1641262609_61d3ae114110a4eeac080.png!small)  
双击右侧DATA XREF内容检査对该字符串的交叉引用  
![image](https://image.3001.net/images/20220104/1641262614_61d3ae16ce075dbf018a5.png!small)

可见该字符串被压入栈  
往上看，发现一组字符串在其之前被压入栈

![image](https://image.3001.net/images/20220104/1641262620_61d3ae1c8d9cacb51b020.png!small)

双击定位过去

![image](https://image.3001.net/images/20220104/1641262626_61d3ae222a1bdf98c47ed.png!small)

看到 Remote Shell Session 初步判断是开启了远程shell会话  
从 \cmd.exe /c
被压入栈后开始看，发现有`recv`调用、`exit`和`cd`字符串、`SetCurrentDirectoryA`和`GetCurrentDirectoryA`调用，所以可以确定这个区域是开启了远程shell会话。

![image](https://image.3001.net/images/20220104/1641262633_61d3ae29400506824caf4.png!small)  
![image](https://image.3001.net/images/20220104/1641262637_61d3ae2de84a9827479cf.png!small)

> 也可以在伪代码里查看
>
>
> ![image](https://image.3001.net/images/20220104/1641262643_61d3ae3390bb80374cfbd.png!small)

#### 通过对1.dll恶意程序分析，0x1000FF58处子函数中若对 ”robotwork” 字符串的memcmp比较是成功的，会发生什么？

定位到1000FF58位置，以图表视图一路向下看，找到 robotwork 的 memcmp

![image](https://image.3001.net/images/20220104/1641262648_61d3ae38bc0cca96871f2.png!small)

比较成功即为0，走红线

![image](https://image.3001.net/images/20220104/1641262654_61d3ae3e56e9f880034a5.png!small)

看到调用了函数 sub_100052A2，跟进去

![image](https://image.3001.net/images/20220104/1641262659_61d3ae438be9d4308f57e.png!small)

> ###### RegOpenKeyEx 用于打开一个指定的注册表键
>  
>  
>     LONG RegOpenKeyEx(
>  

HKEY hKey, // 需要打开的主键的名称  
LPCTSTR lpSubKey, //需要打开的子键的名称  
DWORD ulOptions, // 保留，设为0  
REGSAM samDesired, // 安全访问标记，也就是权限  
PHKEY phkResult // 得到的将要打开键的句柄  
)

>
>     hKey的值：
>  
>  
>  
>
> Public Enum RootKeyEnum  
> HKEY_CLASSES_ROOT = &H80000000  
> HKEY_CURRENT_USER = &H80000001  
> HKEY_LOCAL_MACHINE = &H80000002  
> HKEY_USERS = &H80000003  
> HKEY_PERFORMANCE_DATA_WIN2K_ONLY = &H80000004 '仅Win2k  
> HKEY_CURRENT_CONFIG = &H80000005  
> HKEY_DYN_DATA = &H80000006  
> End Enum
>  
>  
>     \#\#\#\#\#\# RegQueryValueExA 检索一个已打开的注册表句柄中，指定的注册表键的类型和设置值
>  
>  
>  
>
> LONG WINAPI RegQueryValueEx(  
> HKEY hKey, //一个已打开项的句柄，或者指定一个标准项名  
> LPCTSTR lpValueName, //要查询注册表键值的名字字符串，注册表键的名字，以空字符结束。  
> LPDWORD lpReserved, //未用，设为零  
> LPDWORD lpType, //用于装载取回数据类型的一个变量  
> LPBYTE lpData, //用于装载指定值的一个缓冲区  
> LPDWORD lpcbData //用于装载lpData缓冲区长度的一个变量  
> );
>  
>  
>     \#\#\#\#\#\# RegCloseKey 释放指定注册键的句柄
>  
>  
>  
>
> LONG RegCloseKey(  
> HKEY hKey // 释放键的句柄  
> );
>  
>  
>     这3个函数调用成功，则返回0（ERROR\_SUCCESS），否则返回非零错误代码。
>  

![image](https://image.3001.net/images/20220104/1641262679_61d3ae570a38939ac516d.png!small)

发现程序打开注册表键HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion，获取
WorkTime 键值（接着往下看程序判断若没有这个键则读取 WorkTimes 键值），然后将该值传给函数 sub_100038EE ，跟进去

![image](https://image.3001.net/images/20220104/1641262684_61d3ae5cc66010e9c32ba.png!small)  
![image](https://image.3001.net/images/20220104/1641262690_61d3ae6245cadfb472cb7.png!small)

看到“SOCKET”“send”，发现程序将该值通过套接字发送出去，所以对 ”robotwork”
字符串的memcmp比较成功后会通过注册表中取出机器工作时间的值，然后组成一个字符串，最后通过套接字发送出去

#### 通过对1.dll恶意程序分析，PSLIST导出函数最后导出了什么文件

按 `G`输入 PSLIST 定位 PSLIST 函数位置（或在 `导出(Exports)`子视图中找到）

![image](https://image.3001.net/images/20220104/1641262695_61d3ae67ef988e170a3a4.png!small)

对该函数分析，判断该函数是获取进程列表，然后将进程列表通过套接字发送，图中函数 sub_10006518 和 sub_1000664C 都会调用函数
sub_1000620C，检查该函数找到生成的文件名 xinstall.dll

![image](https://image.3001.net/images/20220104/1641262701_61d3ae6d10b7eb179428f.png!small)

> ###### 还有2种方式可以判断：
>
>   * 通过 导入 子视图找到 fopen 函数，查看其与 PSLIST 函数地址相近的交叉引用
>

>
>
> ![image](https://image.3001.net/images/20220104/1641262706_61d3ae72a5437e5f27260.png!small)
>
>   * 通过查看 PSLIST 函数调用的函数图表判断
>

>
>
> ![image](https://image.3001.net/images/20220104/1641262711_61d3ae77676dbabd7dd1e.png!small)

#### 通过对1.dll恶意程序分析，DllMain直接调用了多少个API？

打开 `视图-图表-用户引用图表`，设置如下

![image](https://image.3001.net/images/20220104/1641262718_61d3ae7e57a13832dc3cf.png!small)

OK后可见调用了 4 个API

![image](https://image.3001.net/images/20220104/1641262723_61d3ae8397aa1252e17cb.png!small)

#### 接上题，DllMain函数有几个参数？

查看方法同前，3个

![image](https://image.3001.net/images/20220104/1641262728_61d3ae88f3fb012427d44.png!small)

#### 通过对1.dll恶意程序分析，程序在0x10001358处对sleep的调用会睡眠多少秒？

跳转到 10001358，可见字符串“30”转换为整型数，乘1000(3E8h的十进制)后作为毫秒传入调用的 Sleep API，即睡眠30秒

![image](https://image.3001.net/images/20220104/1641262734_61d3ae8ebde22197ff890.png!small)

#### 通过对1.dll恶意程序分析，在10001701处是一个对Socket的调用。它的第2个参数是什么？

跳转到 10001701 ，可以看到传入的第2个参数是 1 （也可以用伪代码看）

![image](https://image.3001.net/images/20220104/1641262739_61d3ae93e6fbb6c387aed.png!small)  
![image](https://image.3001.net/images/20220104/1641262744_61d3ae987edd861af27f2.png!small)

#### 通过对1.dll恶意程序分析，搜索in指令（0xED）的使用。使用这个指令目的什么？

`Alt + B`弹出搜索字节序列窗口，在 Find all occurrences 前打勾，进行搜索

![image](https://image.3001.net/images/20220104/1641262749_61d3ae9df1eadd90f0ae0.png!small)  
![image](https://image.3001.net/images/20220104/1641262754_61d3aea23250f2162bc74.png!small)  
![image](https://image.3001.net/images/20220104/1641262758_61d3aea6c38bef0070d15.png!small)

in指令下面一行有比较字符串'VMXh'（若显示ASCII码，光标放在上面按 R 转字符串）  
查看使用in指令的函数 sub_10006196 的被引用情况图表，可见有3个参数对其进行调用

![image](https://image.3001.net/images/20220104/1641262763_61d3aeabc15ed5774e629.png!small)

查看这三个参数

![image](https://image.3001.net/images/20220104/1641262769_61d3aeb18036e4dfda5c3.png!small)

可见是用来验证程序是否在虚拟机下运行

#### 通过对1.dll恶意程序分析，将光标跳转到0x1001D988处，对加密的内容进行解密，解密后的内容为？

定位到 1001D988，发现此位置至 1001D9D7 为加密内容，共50个字符

![image](https://image.3001.net/images/20220104/1641262774_61d3aeb6ee38fb74389f7.png!small)

判断可能是常用的异或加密，写个脚本测试一下  
光标放在第一个字符地址位置（1001D988）  
按 `Shift + F2`打开脚本执行窗口

使用我写的Python脚本（第一次在ida写python，网上找的资料大部分是旧版ida的写法，我这个7.6版总是报错，废了点时间才发现是版本问题，找到一篇IDA
Python 7.5的讲解(cnblogs.com/iBinary/p/14642662.html)，下面代码理论上7.5及以上版本ida可正常执行）

    
    
    def xordecode(xorint):
    	i = 0
    	b = get_wide_byte(ea+i)
    	xres = ''
    	while b>0:
    		a = b^xorint
    		if a not in range(32,126): # ASCII码中共95个包括空格的可见字符，从32到126
    			return False
    		xres += chr(a)
    		i = i+1
    		b = get_wide_byte(ea+i)
    	return xres
    for xori in range(1,95):
    	res = xordecode(xori)
    	if res is not False:
    		print(res)
    

![image](https://image.3001.net/images/20220104/1641262782_61d3aebe044d4d745e7fb.png!small)

执行后可在输出视图中找到为数不多的候选结果，其中一条语句通顺，即为解密结果

![image](https://image.3001.net/images/20220104/1641262786_61d3aec2cfa9a84a02a25.png!small)

xdoor is this backdoor, string decoded for Practical Malware Analysis Lab
:)1234

![image](https://image.3001.net/images/20220104/1641263946_61d3b34a154f6d167101b.jpg!small)

