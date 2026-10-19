## 我这里使用的是ANSI版的exe实例，在OllyICE中打开TraceMe.exe。

### 1.在适当的位置设置断点可以帮助我们快速定位到关键代码。

一般情况下，我们事先不知道该程序会具体调用什么函数来处理字符。在Win32程序使用了很多的API函数，通常使用的函数是GetDlgItemText或者GetWindowText，想要最终确定，只能多试几次找出行相关函数。

按“Ctrl+G”打开跟随表达式窗口，输入GetDlgItemTextA，点击“确定”，跳转到如下界面：

> 756E2720 8BFF mov edi, edi  
> 756E2722 55 push ebp  
> 756E2723 8BEC mov ebp, esp  
> 756E2725 FF75 0C push dword ptr [ebp+C]  
> 756E2728 FF75 08 push dword ptr [ebp+8]  
> 756E272B E8 C04BFAFF call GetDlgItem  
> 756E2730 85C0 test eax, eax  
> 756E2732 74 0E je short 756E2742  
> 756E2734 FF75 14 push dword ptr [ebp+14]  
> 756E2737 FF75 10 push dword ptr [ebp+10]  
> 756E273A 50 push eax  
> 756E273B E8 2011F9FF call GetWindowTextA  
> 756E2740 EB 0E jmp short 756E2750  
> 756E2742 837D 14 00 cmp dword ptr [ebp+14], 0  
> 756E2746 74 06 je short 756E274E  
> 756E2748 8B45 10 mov eax, dword ptr [ebp+10]  
> 756E274B C600 00 mov byte ptr [eax], 0  
> 756E274E 33C0 xor eax, eax  
> 756E2750 5D pop ebp  
> 756E2751 C2 1000 retn 10

按”F2“键设置断点，按“F9”运行程序，在窗口中随意输入用户名和序列号，点击“check”开始分析。

![1610355232_5ffc1220e088d7e408e4d.png!small?1610355232812](https://image.3001.net/images/20210111/1610355232_5ffc1220e088d7e408e4d.png!small?1610355232812)

点击“check”后，来到该函数的入口处，即在刚刚设置的断点处。

一直按“F8”单步执行到程序领空，如下界面所示：

![](https://image.3001.net/images/20210111/1610357611_5ffc1b6b2e4f2eecf1b96.png!small)

到这一步，可以看到GetDlgItemTextA函数以及它的相关参数，此时基本就可以确定该程序获取文本框内容的函数就是它。

当然，我们可以再看一下另一个函数。按“Ctrl+F2”结束调试的进程并重新加载它，再次打开跟随表达式窗口，输入GetWindowTextA跳转到该函数处，设置断点。运行程序，在程序窗口中输入用户名和序列号，点击“check”。（再对函数GetWindowTextA分析之前，将刚刚在函数GetDlgItemTextA处的断点取消掉。）

此时来到该函数处:

![](https://image.3001.net/images/20210111/1610357332_5ffc1a545184eaf9642ce.png!small)一直"F8"执行到程序领空后，发现和之前的是一样的。其实在之前跳转到GetDlgItemTextA函数入口为其设置断点时，可以看到“756E273B
E8 2011F9FF call GetWindowTextA”，所以可以说是函数GetDlgItemTextA调用了函数GetWindowTextA。

此时可以确定关键函数应该是GetDlgItemTextA。

### 2.调试分析程序。

此时，已经知道了关键函数是GetDlgItemTextA。我们取消之前设置的断点，重新加载程序，在函数GetDlgItemTextA处设置断点运行程序，输入用户名“pioneer”，序列号“1234”，点击“check”。

一直单步执行到程序领空，分析一下该处程序代码：

> 004011AA . 8D4424 4C lea eax, dword ptr [esp+4C] #把sep+4C这个地址以双字放到eax中
>
> 004011AE . 6A 51 push 51 #将函数参数（字符缓冲区的长度）值压入栈中  
> 004011B0 . 50 push eax #将函数参数（文本缓冲区指针）值压入栈中  
> 004011B1 . 6A 6E push 6E #将函数参数（控件标识）值压入栈中  
> 004011B3 . 56 push esi #将函数参数（对话框句柄）值压入栈中  
> 004011B4 . FFD7 call edi #调用函数GetDlgItemTextA，取出用户名  
> 004011B6 . 8D8C24 9C000000 lea ecx, dword ptr [esp+9C] #把esp+9C这个地址以双字放到ecx中  
> 004011BD . 6A 65 push 65 #将函数参数（字符缓冲区的长度）值压入栈中  
> 004011BF . 51 push ecx #将函数参数（文本缓冲区指针）值压入栈中  
> 004011C0 . 68 E8030000 push 3E8 #将函数参数（控件标识）值压入栈中  
> 004011C5 . 56 push esi #将函数参数（对话框句柄）值压入栈中  
> 004011C6 . 8BD8 mov ebx, eax #将eax中存储的用户名长度转移到ebx中  
> 004011C8 . FFD7 call edi #调用函数GetDlgItemTextA，取出序列号
>
> 004011CA . 8A4424 4C mov al, byte ptr [esp+4C] #将地址为esp+4C的第一个字节传给al  
> 004011CE . 84C0 test al, al #检查用户是否输入用户名，如果没有输入，Z标志就是1  
> 004011D0 . 74 76 je short 00401248 #如果上一步检查出没有输入用户名，就会执行这一步
> 跳走，弹窗告知用户“输入的字符应大于4个！”  
> 004011D2 . 83FB 05 cmp ebx, 5 #将ebx里的值（用户名长度）和立即数5作比较；如果大于5，标志Z为0；相反，标志Z为1。  
> 004011D5 . 7C 71 jl short 00401248 #Z为1时，不执行跳转；相反，弹窗和刚刚的一样。  
> 004011D7 . 8D5424 4C lea edx, dword ptr [esp+4C] #把sep+4C这个地址
> （用户名地址）以双字放到edx中  
> 004011DB . 53 push ebx #将用户名长度压入栈中  
> 004011DC . 8D8424 A00000>lea eax, dword ptr [esp+A0]
> #把sep+A0这个地址（序列号地址）以双字放到eax中  
> 004011E3 . 52 push edx #将用户名压入栈中  
> 004011E4 . 50 push eax #将序列号压入栈中  
> 004011E5 . E8 56010000 call 00401340 #调用函数作进一步运算
>
> 004011EA . 8B3D mov edi, dword ptr [<&USER32.GetDlgItem>]
>
> 004011F0 . 83 0C add esp, 0C  
> 004011F3 85C0 test eax, eax #检查eax中的值，如果为0，则标志Z为1
>
> 注：此处检查是调用函数之后进行的，也就是说是把传入的参数运行之后的结果进行检查，这里就是判断序列号是否正确的关键地方。  
> 004011F5 74 37 je short 0040122E #Z为1，就执行跳转

### 3.爆破

此时，已经找到了该程序和关键位置。只要程序执行到004011F5处时不跳转，那么就相当于是验证成功。

因为跳转判断的依据就是标志F是否为1，所以可以在程序执行完004011F3处的代码后，将标志F手动改为0。

然后，将004011F5处的跳转指令改为nop。

![](https://image.3001.net/images/20210112/1610435924_5ffd4d547b40afa09ffca.png!small)选中修改的指令，右键选择“复制到可执行文件”-“选择”。

![](https://image.3001.net/images/20210112/1610436214_5ffd4e76ab4bde14c5142.png!small)保存之后，会跳出以下界面：

![](https://image.3001.net/images/20210112/1610436756_5ffd509480872107bff68.png!small)此时关闭该界面，跳出以下窗口，我们选择“是”，重新保存一个新文件UpdateTraceMe.exe。

![](https://image.3001.net/images/20210112/1610436962_5ffd5162afa0695bacf2b.png!small)

打开保存的新文件，随机输入用户名和序列号，发现都可以验证成功。

![](https://image.3001.net/images/20210112/1610437129_5ffd520920ba9df48bfe9.png!small)

### 4.代码再分析

除了爆破的方法，之前在分析”004011E5 E8 56010000 call
00401340“处时，我们已经知道此处调用的函数就是去验证序列号的，所以我们执行到这一步时也可以“F7”跟进，进入该程序内部做进一步分析。书中对于具体算法已经分析的很详细了，我这里就不再赘述了。在最后我们可以看到用户名“pioneer”的序列号会在栈中给出，就是“5275”。

当程序执行到0040138F处时，会调用lstrcmpA函数去比较我们输入的序列号和计算出来的序列号。

![](https://image.3001.net/images/20210112/1610438204_5ffd563c2f24269311311.png!small)

## 写在最后

如果刚刚开始学习动态调试，可以自己上手多试几次，一定要结合源代码和反汇编指令将算法分析清楚，这样进步应该也会很快，自己也就会有成就感，也就更爱钻研它了。

**感谢大家的阅读，萌新刚刚接触，如果有写错或写的不准确的地方，欢迎各位大佬在评论区指出。如果有和我一样的萌新有什么问题，欢迎在评论区提问，大家一起讨论。**

