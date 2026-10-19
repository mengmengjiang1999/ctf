## fastbin_dup_consolidate.c 源码

![image-20201215015112694.png](https://image.3001.net/images/20210720/1626764742_60f675c6eb4ec5ce9ad04.png!small)

## 调试分析

首先malloc两个0x40大小的fastbin chunk

![image-20201215015312576.png](https://image.3001.net/images/20210720/1626764744_60f675c8cab18609f5fea.png!small)

同样申请0x40，加上0x10大小的chunk头，1字节的假大小（由于inuse位为1），实际大小为0x50

继续调试，对p1进行了free

![image-20201215015535667.png](https://image.3001.net/images/20210720/1626764747_60f675cb011f5c8c27ba3.png!small)

p1被放进fastbin的空闲链表

然后再malloc一个0x400大小的largbin chunk

来看一下_int_malloc()源码

![image-20201216015034005.png](https://image.3001.net/images/20210720/1626764749_60f675cd7f7e6e6a03ee5.png!small)

检查是否是fastbin范围

![image-20201216015217168.png](https://image.3001.net/images/20210720/1626764751_60f675cfa8934537e99bd.png!small)

检查是否是smallbin范围

![image-20201216015245918.png](https://image.3001.net/images/20210720/1626764752_60f675d0e8c3c519c3ecd.png!small)

都不是就判断属于largebin

![image-20201216015307573.png](https://image.3001.net/images/20210720/1626764754_60f675d27f308e69ecd78.png!small)

可以看到这里在获取了largebin的下表后会检查在分配区(av)内是否有fast chunk (本例有)

如果有则触发malloc_consolidate，对分配区内的chunk进行合并分类

查看consolidate源码

![image-20201216020654470.png](https://image.3001.net/images/20210720/1626764757_60f675d512e55ed319718.png!small)

![image-20201216020945739.png](https://image.3001.net/images/20210720/1626764760_60f675d8d3494eadfcbee.png!small)

主要做的就是向前合并、向后合并相邻的chunk，如果相邻的是top chunk则并入top
chunk，重复这三步直到fastbin链表为空，且合并后的chunk会放到unsortedbin中，除了top chunk

而这里在free完p1后malloc了一个0x400大小的chunk

![image-20201216020945739.png](https://image.3001.net/images/20210720/1626764760_60f675d8d3494eadfcbee.png!small)

0x400 = 1024，实际分配大小为0x400 + 0x10 = 0x410

大于1024字节的chunk会从largebins中申请

此时就会触发malloc_consolidate

p1就会从fastbin中被放到unsortedbin

之后会先在unsortedbin里面整理查找是否有符合大小的chunk，在这个过程中p1就会被分类到smallbin中(因为这里已经没有去fastbin的选择了)

这个过程我们没有跟踪所以我们查看heap的时候会看到0x40大小的p1 chunk被分到了smallbin中而不是unsortedbin

![image-20201216022759341.png](https://image.3001.net/images/20210720/1626764767_60f675df7fe2fddf2920b.png!small)

然后unsortedbin为空，仍未返回需要大小的chunk，则在largebin中查找是否有合适大小的chunk(这里就不是'exact
fit'了)，由于largebin此时为空，则在lastremainder中切割一块0x410大小的chunk出来返回给用户，并将剩下的lastremainder保存为top
chunk

![image-20201216022905077.png](https://image.3001.net/images/20210720/1626764771_60f675e34dc9c5aad8a69.png!small)

而由于在consolidate的过程中p1被移动到smallbin中了，fastbin现在没有记录p1

![image-20201216023102256.png](https://image.3001.net/images/20210720/1626764773_60f675e5a32284f2f7665.png!small)

所以我们可以再次free p1

![image-20201216023133009.png](https://image.3001.net/images/20210720/1626764777_60f675e95559384590207.png!small)

现在，我们就同时在fastbin和smallbin里有p1

![image-20201216023220130.png](https://image.3001.net/images/20210720/1626764781_60f675ed8dde38558e420.png!small)

我们就可以malloc p1两次

第一次malloc结束

![image-20201216023306027.png](https://image.3001.net/images/20210720/1626764784_60f675f029350c1bef4b0.png!small)

![image-20201216023416344.png](https://image.3001.net/images/20210720/1626764787_60f675f35abae9e209d15.png!small)

p1从原来的fastbin记录变为了smallbin

第二次malloc结束

![image-20201216023328468.png](https://image.3001.net/images/20210720/1626764789_60f675f5a385881a0889f.png!small)

![image-20201216023502296.png](https://image.3001.net/images/20210720/1626764792_60f675f8d261fa660c107.png!small)

p1被malloc两次才变为allocated状态

![image-20201216023743030.png](https://image.3001.net/images/20210720/1626764794_60f675fa25fdb793c6e34.png!small)

此时就发生了 'double free'，两次申请的chunk指针指向同一块内存，造成了

