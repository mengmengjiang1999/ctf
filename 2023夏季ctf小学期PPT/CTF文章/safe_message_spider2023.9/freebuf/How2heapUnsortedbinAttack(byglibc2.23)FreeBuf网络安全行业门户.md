## UnsortedbinAttack.c 源码

![image-20201217204056644](https://image.3001.net/images/20210721/1626869545_60f80f294f7ca1e041e22.png!small)

## 调试分析

1.首先定义了一个变量，存放在栈上

![image-20201217205947124](https://image.3001.net/images/20210721/1626869549_60f80f2d95ff51a522845.png!small)

2.然后malloc一个0x400大小的chunk p

![image-20201217210145616](https://image.3001.net/images/20210721/1626869555_60f80f333c7dd6f66891b.png!small)

3.为了防止在下一次执行free的时候 chunk p 被consolidate合并到 top chunk 中，这里再申请一个0x500大小的chunk。

![image-20201217210418350](https://image.3001.net/images/20210721/1626869561_60f80f3902ed7a7b6ebc5.png!small)

4.然后将chunk p free掉，

![image-20201217210609449](https://image.3001.net/images/20210721/1626869565_60f80f3de7860b6765fdd.png!small)

注意这里，

chunk p被放到了unsortedbin中，且fd和bk指针都指向main_arena+88

然后我们改写chunk p的bk指针。

![image-20201217212346175](https://image.3001.net/images/20210721/1626869570_60f80f42668974a38296c.png!small)

需要将chunk p的bk指针改写为栈上变量的低2个"单位"(8字节)的地址，

这是因为在调用malloc整理unsortedbin的时候遵循“LILO”(Last In Last
Out)的原则，会将av分配区的unsortedbin的bk指向的最后一个chunk作为victim，victim的bk指向的chunk作为bck，会从unsortedbin链表尾部开始处理，对chunk做完处理就将chunk移出链表，也就是源码中红框中的代码

这也是unsortedbin attack的来源，

因为在这里并未对bck做足够的检查就将bck的fd指针指向main_arena数组，将会造成main_arena地址的泄露，而main_arena是在libc上的，就会进而导致libc地址的泄露等一系列问题。

![image-20201217213155760](https://image.3001.net/images/20210721/1626869575_60f80f4791a61eb4c142c.png!small)

查看bins，

unsortedbin的bk指针指向刚刚free掉的 chunk p ，p的bk指针指向栈上的假的chunk头。

![image-20201217214506261](https://image.3001.net/images/20210721/1626869577_60f80f4941db1cb686532.png!small)

5.进行malloc

![image-20201217213839076](https://image.3001.net/images/20210721/1626869580_60f80f4c77684485f9442.png!small)

查看bins

![image-20201217214737118](https://image.3001.net/images/20210721/1626869584_60f80f509cb73e9e7f096.png!small)

可以看到 chunk p
被移出unsortedbin，现在unsortedbin的bk指针指向了栈地址，并且通过源码可知这个栈地址指向的地方被当做bck的时候会将 bck->fd
指向bins上的unsortedbin，也即这里的 main_arena+88，也就是将 main_arena+88 写到stack_var了 。

![image-20201217215401106](https://image.3001.net/images/20210721/1626869587_60f80f53c690375683e22.png!small)

以上就是unsortedbin attack的全部内容。

