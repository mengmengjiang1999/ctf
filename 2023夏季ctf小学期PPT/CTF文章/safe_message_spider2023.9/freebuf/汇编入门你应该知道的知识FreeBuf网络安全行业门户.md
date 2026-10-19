**160个CrackMe-001**

首先运行程序，发现程序是个注册机，输入用户名与注册码。

![crashme152.png](https://image.3001.net/images/20210713/1626142394_60ecf6ba44f870f74920d.png!small)

点击Check it Baby!会检测注册码是否正确，并且多次尝试发现提示语句相同

![crashme1107.png](https://image.3001.net/images/20210713/1626142396_60ecf6bc36a48d572b9fe.png!small)

拉进OD进行分析，当弹出提示时不着急点确定，回到OD点击暂停运行按钮

![crashme1155.png](https://image.3001.net/images/20210713/1626142398_60ecf6be0463f5b25a131.png!small)

点击堆栈(crlt+k)或者小图标K

![crashme1187.png](https://image.3001.net/images/20210713/1626142399_60ecf6bf78c6b13eae4e0.png!small)

找到地址为0042a1ae的MessageBoxA的函数，该函数为win32的弹窗函数，并且距离用户代码的入口点00401000非常接近

![crashme1269.png](https://image.3001.net/images/20210713/1626142401_60ecf6c1f189701acf90e.png!small)

右键->显示函数调用过程，观察那个函数调用了此函数，找到相关函数，可以发现这是MessageBox调用的过程，那么在堆栈区找到返回函数，观察该函数执行完会返回到哪个函数

![crashme1454.png](https://image.3001.net/images/20210713/1626142403_60ecf6c3de106f90e6856.png!small)

打下断点，运行到此处，在右下角的堆栈窗口查看返回地址，在堆栈窗口中右键->地址->相对于EBP，找到EBP+4的地址，对应的地址为返回地址，右键该地址，反汇编窗口跟随

![crashme1454.png](https://image.3001.net/images/20210713/1626142407_60ecf6c750a4ae560b5d7.png!small)

找到关键的跳转，该跳转会执行错误弹框信息。

![crashme1489.png](https://image.3001.net/images/20210713/1626142410_60ecf6cabc18248c446a5.png!small)

 **方法一:暴力破解**

由于该跳转是用JNZ实现的，那么将跳转改为JE或者NOP掉改变程序的执行流程

![crashme1550.png](https://image.3001.net/images/20210713/1626142414_60ecf6ce3594094293672.png!small)

(1)修改为JE，右键关键跳转语句->选择汇编

![crashme1587.png](https://image.3001.net/images/20210713/1626142417_60ecf6d12b8be66408f2f.png!small)

此时成功信息弹出

![crashme1599.png](https://image.3001.net/images/20210713/1626142419_60ecf6d3f1cf9b503d5ee.png!small)

(2)用NOP填充，由于在关键的跳转语句下有个调用弹框函数，因此猜测该函数为成功的执行流。

右键关键跳转，选择NOP填充

![crashme1673.png](https://image.3001.net/images/20210713/1626142422_60ecf6d68d510ae861543.png!small)

同样弹出成功消息

![crashme1695.png](https://image.3001.net/images/20210713/1626142426_60ecf6da08c968a82c632.png!small)

 **方法二：注册机算法**

发现在关键跳转前有个call调用，打下断点观察下寄存器的值

![crashme1748.png](https://image.3001.net/images/20210713/1626142428_60ecf6dc791f2a14ef3d4.png!small)

在执行到该调用语句时，观察右上角的寄存器窗口，发现了疑似注册码的值，以及我们手动输入的注册码，两者进行比较若不相同则直接跳转到错误弹窗。

![crashme1830.png](https://image.3001.net/images/20210713/1626142430_60ecf6de89398b893acae.png!small)

将疑似注册码输入，发现成功弹窗，因此验证了这个就是注册码的值，那么在call语句实现之前则注册码已经生成

![crashme1896.png](https://image.3001.net/images/20210713/1626142432_60ecf6e0d15c9629972f6.png!small)

0042FAF3的调用没有什么特殊的，跟进去0042FAE5的调用

![crashme1943.png](https://image.3001.net/images/20210713/1626142434_60ecf6e250c9032b2b590.png!small)

(0042FAE5调用)汇编代码

此时可以看到，在进入0042FAE5调用之前，激活码已经生成完毕，在该函数调用只是进行了字符串的替换，将我们输入的name值分部分替换为激活码。

004039AC $ 53 PUSH EBX

004039AD . 56 PUSH ESI

004039AE . 52 PUSH EDX

004039AF . 50 PUSH EAX

004039B0 . 89D3 MOV EBX,EDX

004039B2 . 31C0 XOR EAX,EAX

004039B4 > 8B4C94 10 MOV ECX,DWORD PTR SS:[ESP+EDX*4+0x10] ; 读取注册码各部分的字符串

004039B8 . 85C9 TEST ECX,ECX

004039BA . 74 03 JE SHORT Acid_bur.004039BF

004039BC . 0341 FC ADD EAX,DWORD PTR DS:[ECX-0x4]

004039BF > 4A DEC EDX

004039C0 .^75 F2 JNZ SHORT Acid_bur.004039B4

004039C2 . E8 69FDFFFF CALL Acid_bur.00403730 ; 获取name值

004039C7 . 50 PUSH EAX ; 将name压入栈中

004039C8 . 89C6 MOV ESI,EAX

004039CA > 8B449C 14 MOV EAX,DWORD PTR SS:[ESP+EBX*4+0x14] ; Acid_bur.0042FBC8

004039CE . 89F2 MOV EDX,ESI

004039D0 . 85C0 TEST EAX,EAX

004039D2 . 74 0A JE SHORT Acid_bur.004039DE

004039D4 . 8B48 FC MOV ECX,DWORD PTR DS:[EAX-0x4]

004039D7 . 01CE ADD ESI,ECX ; 计算当前部分激活码的长度

004039D9 . E8 66EDFFFF CALL Acid_bur.00402744 ; 将部分name值替换为激活码

004039DE > 4B DEC EBX

004039DF .^75 E9 JNZ SHORT Acid_bur.004039CA

004039E1 . 5A POP EDX

004039E2 . 58 POP EAX

004039E3 . 85D2 TEST EDX,EDX

004039E5 . 74 03 JE SHORT Acid_bur.004039EA

004039E7 . FF4A F8 DEC DWORD PTR DS:[EDX-0x8]

004039EA > E8 D5FCFFFF CALL Acid_bur.004036C4

004039EF . 5A POP EDX

004039F0 . 5E POP ESI

004039F1 . 5B POP EBX

004039F2 . 58 POP EAX

004039F3 . 8D2494 LEA ESP,DWORD PTR SS:[ESP+EDX*4]

004039F6 . FFE0 JMP EAX

004039F8 . C3 RETN

将断点断在函数的起始部分，单步跟踪查看

![crashme12913.png](https://image.3001.net/images/20210713/1626142435_60ecf6e3ea48cab123624.png!small)

 **汇编代码部分**

可以看到，程序会先计算name的长度，若长度小于4则直接弹出错误信息窗口。

程序会取出我们输入的name的第一个字节，这里简称为name[0]

将name[0]的值乘以0x29再乘以0x2即为部分注册码的值，例如我们输入的name为123456789,name[0]=1，这个1为字符串1，它的ASCII码值为0x31，则0x31*0x29*0x2
= 4018,通过刚刚的寄存器窗口可以看到我们的注册码为CW-4018-CRACKED，即中间数字部分的注册码已经求出

0042FA1E |. E8 35B0FEFF CALL Acid_bur.0041AA58 ; 用于计算name的长度

0042FA23 |. 8B45 F0 MOV EAX,DWORD PTR SS:[EBP-0x10]

0042FA26 |. 0FB640 03 MOVZX EAX,BYTE PTR DS:[EAX+0x3]

0042FA2A |. 6BF0 0B IMUL ESI,EAX,0xB

0042FA2D |. 8D55 EC LEA EDX,DWORD PTR SS:[EBP-0x14]

0042FA30 |. 8B83 DC010000 MOV EAX,DWORD PTR DS:[EBX+0x1DC]

0042FA36 |. E8 1DB0FEFF CALL Acid_bur.0041AA58

0042FA3B |. 8B45 EC MOV EAX,DWORD PTR SS:[EBP-0x14]

0042FA3E |. 0FB640 02 MOVZX EAX,BYTE PTR DS:[EAX+0x2]

0042FA42 |. 6BC0 0E IMUL EAX,EAX,0xE

0042FA45 |. 03F0 ADD ESI,EAX

0042FA47 |. 8935 58174300 MOV DWORD PTR DS:[0x431758],ESI

0042FA4D |. A1 6C174300 MOV EAX,DWORD PTR DS:[0x43176C]

0042FA52 |. E8 D96EFDFF CALL Acid_bur.00406930

0042FA57 |. 83F8 04 CMP EAX,0x4 ; 判断name长度是否大于4

0042FA5A |. 7D 1D JGE SHORT Acid_bur.0042FA79

0042FA5C |. 6A 00 PUSH 0x0

0042FA5E |. B9 74FB4200 MOV ECX,Acid_bur.0042FB74 ; ASCII 54,"ry Again!"

0042FA63 |. BA 80FB4200 MOV EDX,Acid_bur.0042FB80 ; ASCII 53,"orry , The
serial is incorect !"

0042FA68 |. A1 480A4300 MOV EAX,DWORD PTR DS:[0x430A48]

0042FA6D |. 8B00 MOV EAX,DWORD PTR DS:[EAX]

0042FA6F |. E8 FCA6FFFF CALL Acid_bur.0042A170

0042FA74 |. E9 BE000000 JMP Acid_bur.0042FB37

0042FA79 |> 8D55 F0 LEA EDX,DWORD PTR SS:[EBP-0x10] ; EBP-0x10存储着name值，并赋值给EDX

0042FA7C |. 8B83 DC010000 MOV EAX,DWORD PTR DS:[EBX+0x1DC]

0042FA82 |. E8 D1AFFEFF CALL Acid_bur.0041AA58

0042FA87 |. 8B45 F0 MOV EAX,DWORD PTR SS:[EBP-0x10]

0042FA8A |. 0FB600 MOVZX EAX,BYTE PTR DS:[EAX] ; 取第一个字节到EAX中

0042FA8D |. F72D 50174300 IMUL DWORD PTR DS:[0x431750] ; 乘以0x29

0042FA93 |. A3 50174300 MOV DWORD PTR DS:[0x431750],EAX

0042FA98 |. A1 50174300 MOV EAX,DWORD PTR DS:[0x431750]

0042FA9D |. 0105 50174300 ADD DWORD PTR DS:[0x431750],EAX ; 乘以2

0042FAA3 |. 8D45 FC LEA EAX,DWORD PTR SS:[EBP-0x4]

0042FAA6 |. BA ACFB4200 MOV EDX,Acid_bur.0042FBAC

0042FAAB |. E8 583CFDFF CALL Acid_bur.00403708

0042FAB0 |. 8D45 F8 LEA EAX,DWORD PTR SS:[EBP-0x8]

0042FAB3 |. BA B8FB4200 MOV EDX,Acid_bur.0042FBB8

0042FAB8 |. E8 4B3CFDFF CALL Acid_bur.00403708

0042FABD |. FF75 FC PUSH DWORD PTR SS:[EBP-0x4]

0042FAC0 |. 68 C8FB4200 PUSH Acid_bur.0042FBC8 ; UNICODE "-",注册码用"-"字符串隔开

0042FAC5 |. 8D55 E8 LEA EDX,DWORD PTR SS:[EBP-0x18]

0042FAC8 |. A1 50174300 MOV EAX,DWORD PTR DS:[0x431750]

0042FACD |. E8 466CFDFF CALL Acid_bur.00406718

0042FAD2 |. FF75 E8 PUSH DWORD PTR SS:[EBP-0x18]

0042FAD5 |. 68 C8FB4200 PUSH Acid_bur.0042FBC8 ; UNICODE "-",注册码用"-"字符串隔开

通过输入不同的注册码，我们可以发现注册码的形式为CW-*****-CRACKED即只有中间部分的注册码是通过name值变换得来，而其他部分的注册码则是固定不变的，因此生成注册码的代码为，代码写的较为稀烂。

    
    
    #include<stdio.h>
    
    #include<stdlib.h>
    
    #include<string.h>
    
    int main()
    
    {
    
    char flag[20];
    
    char text[20];
    
    int i = 0;
    
    scanf("%s",flag);
    
    while(flag[i]!='\0')
    
    {
    
      i++;
    
      if(i>4)
    
        break;
    
    }
    
    if(i<4)
    
    {
    
      printf("长度需要大于4!\n");
    
      exit(-1);
    
    }
    
    i = flag[0]*0x29*2;
    
    printf("CW-%d-CRACKED\n",i);
    
    return 1;
    
    
    
    
    }

 **补充**

当我们看到这些间接寻址时，可能因为代码太多已经忘记此时里面的值，可以点击数据窗口->Crtl+G输入你想看的地址，例如我输入了0x43176c则可以看到该段里面的值

![crashme16475.png](https://image.3001.net/images/20210713/1626142437_60ecf6e5daffb8d1b0bcd.png!small)

可以看到存储的值即我输入的name值012345678,这样可以随时查看段地址里存储的值，方便阅读汇编代码

![crashme16542.png](https://image.3001.net/images/20210713/1626142441_60ecf6e94453755586f26.png!small)

 **总结**

虽然程序不是十分复杂，但是可以帮助我们去熟悉OD的使用以及对汇编的应用，我也是通过该程序学到了很多，希望能够帮助到大家

 **相关实验：** **[ARM漏洞利用技术五--堆溢出](https://www.hetianlab.com/expc.do?ec=ECIDf4f4-3f86-44b4-bd4c-e1c88520adde&pk_campaign=freebuf-wemedia)**

