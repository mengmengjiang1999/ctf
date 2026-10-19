原创： 哈热热  合天智汇

  
  

# ****

# **前言**

《0day安全软件漏洞分析技术》是一本软件漏洞分析的入门经典，虽然已经出版很多年，以至于现在都绝版了，但是其中使用到的技术和分析思路仍然适用。PWN入门就靠这本书233，当年没有仔细琢磨书中的细节，现在回头再看看，同时出个新手向的漏洞分析教程。

 **栈帧**

在母函数调用子函数的时候，会在栈中构建新的栈帧，将 **返回地址，传入的参数，** **EBP**
（母函数的栈帧栈底地址）压进栈中。不同位的操作系统对栈帧的具体操作不尽相同，而且不同语言，不同编译器可能也会产生不一样的栈帧。

  
![图片.png](https://image.3001.net/images/20181115/1542264288_5bed15e067059.png!small)  

书中默认的调用方法采用C的参数传入顺序。

 **函数调用步骤**

1、参数入栈：将参数从右到左依次压入栈

2、返回地址入栈：将当前代码区执行的命令的下一条指令的地址压入栈

3、代码区跳转：CPU跳转到函数入口，EIP指向调用函数的第一行代码

4、调整栈帧

![图片.png](https://image.3001.net/images/20181115/1542264296_5bed15e839975.png!small)  

 **栈帧的调整**

  
![图片.png](https://image.3001.net/images/20181115/1542264302_5bed15eeac69e.png!small)  

 **  
**

 **通过栈溢出修改变量值**

首先构造带有数组边界溢出的源码

#include<stdio.h>

#include<string.h>

#definePASSWORD "1234567"

intverify_password(char *password)

{

intauthenticated;

charbuffer[8]; //add local buff to be overflowed

authenticated=strcmp(password,PASSWORD);

strcpy(buffer,password);//over flowed here!

returnauthenticated;

}

intmain()

{

intvalid_flag=0;

charpassword[1024];

while(1)

{

printf("pleaseinput password: ");

scanf("%s",password);

valid_flag= verify_password(password);

if(valid_flag)

{

printf("nono no no!\n\n");

}

else

{

printf("yesyes yes!\n");

break;

}

}

return0;

}

注意到传入的字符串没有检验长度，存在溢出风险

  
![图片.png](https://image.3001.net/images/20181115/1542264326_5bed16060209c.png!small)  

 **IDA** **查看函数的执行流程**

  
![图片.png](https://image.3001.net/images/20181115/1542264332_5bed160c4d492.png!small)  

push offset aPleaseInputPas ; "please input password: "

call _printf

add esp, 4

lea ecx, [ebp+var_404]

push ecx

push offset aS ; "%s"

call _scanf

add esp, 8

lea edx, [ebp+var_404]

push edx ; char *

call sub_40100A ;这里调用verify_password函数

add esp, 4

mov [ebp+var_4], eax

cmp [ebp+var_4], 0

jz short loc_40F756

我们知道，调用后，由子函数来生成对应的栈帧

 **OD** **查看栈帧生成流程**

  
![图片.png](https://image.3001.net/images/20181115/1542264340_5bed16142ca84.png!small)  

首先上一个栈帧的栈底入栈，然后将ebp指向新栈帧的栈底，开辟栈帧空间，esp指向新栈帧的栈顶。

 **为什么要看** **verify_password** **的栈帧生成**  
函数局部变量空间的开辟会在生成栈帧的时候进行，小白还是要跟进函数中看看局部变量在栈中是怎么分布的~

;Attributes: bp-based frame

;int __cdecl sub_401010(char *)

sub_401010proc near

var_4C=byte ptr -4Ch

var_C=byte ptr -0Ch

var_4=dword ptr -4

arg_0=dword ptr 8

push ebp

mov ebp, esp

sub esp, 4Ch

push ebx

push esi

push edi

lea edi, [ebp+var_4C]

mov ecx, 13h

mov eax, 0CCCCCCCCh

repstosd

push offset a1234567 ; "1234567"

mov eax, [ebp+arg_0]

push eax ; char *

call _strcmp

add esp, 8

mov [ebp+var_4], eax

mov ecx, [ebp+arg_0]

push ecx ; char *

lea edx, [ebp+var_C]

push edx ; char *

call _strcpy

add esp, 8

mov eax, [ebp+var_4]

pop edi

pop esi

pop ebx

add esp, 4Ch

cmp ebp, esp

call __chkesp

mov esp, ebp

pop ebp

retn

sub_401010endp

verify_password()在IDA编译后的高级语言表示

 **strcpy** **导致的变量覆盖**

 **定位** **strcpy**

  
![图片.png](https://image.3001.net/images/20181115/1542264350_5bed161e39ce0.png!small)  

在IDA中找到函数的VA（虚拟地址）

  
![图片.png](https://image.3001.net/images/20181115/1542264357_5bed1625e850a.png!small)  

在OD中Ctrl+G定位到strcpy函数，在调用完函数的下一行下断点，F9执行到这里。

![图片.png](https://image.3001.net/images/20181115/1542264364_5bed162c37181.png!small)  

  
0019FAE4是局部变量authenticated在栈中的位置，上面的是strcpy后的qqqqqqq字符串，\00结尾，authenticated的值为1的时候是还没覆盖变量的正常值。现在输入八个q，让结束符\00覆盖authenticated的值。（一定要注意这是verify_password函数的栈帧，而不是strcpy的栈帧，我之前就是一直在strcpy的栈帧中找，书上也没说清楚:P）

![图片.png](https://image.3001.net/images/20181115/1542264444_5bed167cdd45b.png!small)  

  

  

成功覆盖了authenticated的值！

![图片.png](https://image.3001.net/images/20181115/1542264449_5bed168186e92.png!small)  

  
  

# strcpy存在变量覆盖漏洞

通过输入的字符串，顺着栈一路覆盖至函数的返回地址，将恶意代码的入口地址覆盖到返回地址上。  
这次的目的是将通过验证的入口地址覆盖返回地址:)

  
![图片.png](https://image.3001.net/images/20181115/1542264456_5bed1688c56b0.png!small)  

栈帧的分布情况，返回地址前有16个字节的数据，返回地址有四个字节，前16字节的数据随意覆盖，返回地址用入口地址覆盖。开搞：P

## 查找成功认证函数的入口地址

  
![图片.png](https://image.3001.net/images/20181115/1542264469_5bed1695dbd22.png!small)  

IDA查看函数逻辑，cmp后，zf位如果为0就会跳转到loc_401120位置的函数，这就是我们想要函数跳转到地方。

  
![图片.png](https://image.3001.net/images/20181115/1542264474_5bed169ade3b0.png!small)  

由于地址十六进制对应的ASCII码键盘是打不出的，所以要先用十六进制编辑器写好payload，以读文件的方式输入程序，修改一下程序：

#include<stdio.h>

#include<string.h>

#definePASSWORD "1234567"

intverify_password(char *password)

{

intauthenticated;

charbuffer[8]; //add local buff to be overflowed

authenticated=strcmp(password,PASSWORD);

strcpy(buffer,password);//over flowed here!

returnauthenticated;

}

intmain()

{

intvalid_flag=0;

FILE*fp;

if(!(fp=fopen("password.txt","rw+")))

{

return(0);

}

charpassword[1024];

printf("pleaseinput password: ");

fscanf(fp,"%s",password);

valid_flag= verify_password(password);

if(valid_flag)

{

printf("nono no no!\n\n");

}

else

{

printf("yesyes yes!\n");

}

fclose(fp);

return0;

}

好了，我们已经知道入口地址为00401113。

  
![图片.png](https://image.3001.net/images/20181115/1542264485_5bed16a52f069.png!small)  

用Winhex编辑，前16字节随便填，最后4个字节逆序输入地址，注意x86汇编采用小端序方式。

![图片.png](https://image.3001.net/images/20181115/1542264491_5bed16abd27b6.png!small)  

将字符串保存在password.txt中

  
![图片.png](https://image.3001.net/images/20181115/1542264497_5bed16b1e9a9b.png!small)  

emmmm，成功跳转到了验证字符串输出的地址，也成功输出了正确的字符串，程序崩溃是因为到程序最后返回时，栈平衡被打破，找不到返回到dos的地址，因此崩溃。

## 用OD查看覆盖的地址

![图片.png](https://image.3001.net/images/20181115/1542264504_5bed16b887e9f.png!small)  

  
![图片.png](https://image.3001.net/images/20181115/1542264511_5bed16bf70d50.png!small)  

在返回的时候，成功读取了错误的返回地址。

#  **思考一下**

  
![图片.png](https://image.3001.net/images/20181115/1542264519_5bed16c7483b9.png!small)  

这个入口地址到底出了问题：）

好吧，其实是因为十六进制的20是空格，fscanf%s 遇到空格就会截断，因此后边的114000是传不进去的:P

