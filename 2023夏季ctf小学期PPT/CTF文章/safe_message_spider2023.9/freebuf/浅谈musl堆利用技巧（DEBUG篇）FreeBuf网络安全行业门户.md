## 前言

最近比赛出的musl题型的越来越多，不得不学习一波musl的堆利用来应对今后的比赛。这里要讲的是musl1.22版本的利用，因为网上可以找到很多审计源码的文章，所以这篇文章是通过一道题目来debug去学习堆的利用技巧，这里用到的是2021第五空间线上赛的notegame题目。

## 题目分析

1、首先是add函数，使用了calloc，申请的最大size是0x90

![1644544060_6205c03c4f40604635344.png!small?1644544060474](https://image.3001.net/images/20220211/1644544060_6205c03c4f40604635344.png!small?1644544060474)

2、接着是delete函数,free之后将指针清空了

![1644544069_6205c045c747a38dd7588.png!small?1644544069941](https://image.3001.net/images/20220211/1644544069_6205c045c747a38dd7588.png!small?1644544069941)

3、然后是edit函数，漏洞就出现在这里，这里存在溢出空字节的漏洞，可以对index清零指向 fake_meta

![1644544077_6205c04dc816318214054.png!small?1644544078086](https://image.3001.net/images/20220211/1644544077_6205c04dc816318214054.png!small?1644544078086)

4、最后来看这个update函数，这个realloc函数会将原来chunk的内容复制到新的chunk里面，我们可以用这个来进行泄露libc地址

![1644544084_6205c054c607077406c4f.png!small?1644544085049](https://image.3001.net/images/20220211/1644544084_6205c054c607077406c4f.png!small?1644544085049)

## 调试分析

musl的chunk跟glibc的区别就是，chunk头的结构存放了比较少的堆块信息，没有像glibc那样存放了一些指针地址信息，所以我们如果要泄露libc地址的话也是要特定的条件，就是要chunk里面保存着另外一个chunk的指针地址或者其他指针地址的信息，而且也再不能直接改指针去达到任意分配的效果，而是要改chunk头仅有的信息去伪造meta进行任意分配。

### malloc_context

    
    
    add(0x20,'a'*0x20)

![1644544094_6205c05ea66aa6d0cf2a4.png!small?1644544094909](https://image.3001.net/images/20220211/1644544094_6205c05ea66aa6d0cf2a4.png!small?1644544094909)

1、secret是用来校验meta域的一个key

2、free_meta_head存放着释放掉的meta，是个单链表结构，这里还没有释放，所以为空

3、active是根据size大小分出来的不同的meta

4、usage_by_class是对应meta的数量

### meta

    
    
    add(0x20,'a'*0x20)  
    add(0x20,'a'*0x20)  
    add(0x20,'a'*0x20)  
    add(0x20,'a'*0x20)  
    free(0)

![1644544102_6205c06626f7551820c29.png!small?1644544102457](https://image.3001.net/images/20220211/1644544102_6205c06626f7551820c29.png!small?1644544102457)

1、prev和next分别是上一个和下一个meta页，这里都指向本身，表示只有一个meta页

2、 mem表示group的地址，它是由多个chunk组成

3、avail_mask表示可以分配的chunk情况，0x3f0=0b01111110000，因为我们已经分配了4个堆块，所以这里表示前四个不可分配。

4、freed_mask表示已经释放的chunk情况，因为我们释放掉了第一个chunk，所以这里的0x1表示的是free掉的第一个chunk

5、last_idx表示最后一个chunk的下标，这里是0x9，总数是0xa个

6、freeable表示已经释放的堆块个数

7、sizeclass表示管理的group的大小

8、maplen如果不为零表示mmap分配的内存页数

### chunk

    
    
    add(0x20,'a'*0x20)  
    add(0x20,'a'*0x20)  
    add(0x20,'a'*0x20)  
    add(0x20,'a'*0x20)  
    free(3)

![1644544111_6205c06fc1aedd209fb66.png!small?1644544112033](https://image.3001.net/images/20220211/1644544111_6205c06fc1aedd209fb66.png!small?1644544112033)

1、表示距离group首地址的偏移分别为0x0、0x30、0x60，系统是根据这个偏移来找到对应的meta地址，所以我们如果能改这个偏移比如把chunk1的偏移置零的话，就能在chunk1-0x10的地方伪造一个meta的指针，而这个地方又是我们可以控制的chunk0的data域，于是我们就可以在任意地方伪造一个meta，不过这个地址必须是跟0x1000对齐的。

2、表示当前chunk的下标，当chunk被free之后会变成0xff

3、表示剩下用户空间的大小，chunk头后面的4个字节跟glibc的prev_size那样可以被上一个chunk复用，
所以我们就可知道我们分配的大小跟chunk大小的关系

    
    
    0x10：0-0xc  
    0x20：0xd-0x1c  
    0x30：0x1d-0x2c  
    0x40：0x2d-0x3c  
    ...

### chunk的分配释放

    
    
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    free(0)  
    add(0x50,'a'*0x50)

![1644544120_6205c078d83fc70d6ab26.png!small?1644544121070](https://image.3001.net/images/20220211/1644544120_6205c078d83fc70d6ab26.png!small?1644544121070)

avail_mask = 0x10=0b10000

freed_mask = 0x1 =0b00001

musl的chunk释放了之后并不会马上分配，这里group里面有5个chunk，先是申请了3个chunk，然后free掉第一个，再次申请的时候并不会把第一个chunk分配出来，而是把group的第四个chunk申请出来，然后对应的avail_mask置零

    
    
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    free(0)  
    free(1)  
    free(2)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)

![1644544128_6205c0803b833314bebb0.png!small?1644544138410](https://image.3001.net/images/20220211/1644544128_6205c0803b833314bebb0.png!small?1644544138410)

avail_mask = 0x6 =0b0110

freed_mask = 0x0 =0b0000

耗尽group的chunk的时候，musl会把释放掉的申请出来，并把其他chunk对应的avail_mask置1

### meta的释放

    
    
    add(0x50,'a'*0x50)  
    free(0)

![1644544137_6205c0895c25a4464ecaf.png!small?1644544138409](https://image.3001.net/images/20220211/1644544137_6205c0895c25a4464ecaf.png!small?1644544138409)

当只有一个chunk是被分配出去的，而freed_mask=0，我们把这个chunk给free掉之后，系统会回收整块meta空间

    
    
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    add(0x50,'a'*0x50)  
    free(0)  
    free(1)  
    free(2)  
    free(3)  
    free(4)

![1644544145_6205c09116261ead739e1.png!small?1644544145363](https://image.3001.net/images/20220211/1644544145_6205c09116261ead739e1.png!small?1644544145363)

总结起来，就是说`avail_mask |freed_mask`的结果是满状态的时候，就会释放这个meta。

## 总结

本篇先通过debug的方法来简单阐述musl堆块的结构，后续再讲如何对它进行利用。

