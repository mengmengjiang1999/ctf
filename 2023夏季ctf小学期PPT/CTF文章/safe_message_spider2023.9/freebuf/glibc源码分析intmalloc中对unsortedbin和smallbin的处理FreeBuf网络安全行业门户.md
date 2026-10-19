**之前已经讲过了对三种chunk的申请，接下来有一段处理chunk的代码，下面我会直接上代码**

    
    
    while ( (victim = unsorted_chunks(av)->bk) != unsorted_chunks(av)) {
          bck = victim->bk;
          size = chunksize(victim);
    
          /*
             If a small request, try to use last remainder if it is the
             only chunk in unsorted bin.  This helps promote locality for
             runs of consecutive small requests. This is the only
             exception to best-fit, and applies only when there is
             no exact fit for a small chunk.
          */
    
          if (in_smallbin_range(nb) &&
              bck == unsorted_chunks(av) &&
              victim == av->last_remainder &&
              (unsigned long)(size) > (unsigned long)(nb + MINSIZE)) {
    
            /* split and reattach remainder */
            remainder_size = size - nb;
            remainder = chunk_at_offset(victim, nb);
            unsorted_chunks(av)->bk = unsorted_chunks(av)->fd = remainder;
            av->last_remainder = remainder;
            remainder->bk = remainder->fd = unsorted_chunks(av);
    
            set_head(victim, nb | PREV_INUSE |
    		 (av != &main_arena ? NON_MAIN_ARENA : 0));
            set_head(remainder, remainder_size | PREV_INUSE);
            set_foot(remainder, remainder_size);
    
            check_malloced_chunk(av, victim, nb);
            return chunk2mem(victim);
          }
    
          /* remove from unsorted list */
          unsorted_chunks(av)->bk = bck;
          bck->fd = unsorted_chunks(av);
    
          /* Take now instead of binning if exact fit */
    
          if (size == nb) {
            set_inuse_bit_at_offset(victim, size);
    	if (av != &main_arena)
    	  victim->size |= NON_MAIN_ARENA;
            check_malloced_chunk(av, victim, nb);
            return chunk2mem(victim);
          }
    
          /* place chunk in bin */
    
          if (in_smallbin_range(size)) {
            victim_index = smallbin_index(size);
            bck = bin_at(av, victim_index);
            fwd = bck->fd;
          }
          else {
            victim_index = largebin_index(size);
            bck = bin_at(av, victim_index);
            fwd = bck->fd;
    
            /* maintain large bins in sorted order */
            if (fwd != bck) {
    	  /* Or with inuse bit to speed comparisons */
              size |= PREV_INUSE;
              /* if smaller than smallest, bypass loop below */
    	  assert((bck->bk->size & NON_MAIN_ARENA) == 0);
              if ((unsigned long)(size) <= (unsigned long)(bck->bk->size)) {
                fwd = bck;
                bck = bck->bk;
              }
              else {
    	    assert((fwd->size & NON_MAIN_ARENA) == 0);
                while ((unsigned long)(size) < (unsigned long)(fwd->size)) {
                  fwd = fwd->fd;
    	      assert((fwd->size & NON_MAIN_ARENA) == 0);
    	    }
                bck = fwd->bk;
              }
            }
          }
    
          mark_bin(av, victim_index);
          victim->bk = bck;
          victim->fd = fwd;
          fwd->bk = victim;
          bck->fd = victim;
        }
    

# 初始化数据

最开始有一个while循环，内容为`(victim = unsorted_chunks(av)->bk) !=
unsorted_chunks(av)`，这是判断unsortedbin的bk指针是否指向自己，本质上就是在判断unsortedbin是否为空(前面有讲过，为空的时候两个指针指向自己)，然后bck等于本堆块的bk指针，size等于本堆块的size(不包含低三位)。

# remainder的处理

    
    
    if (in_smallbin_range(nb) &&
              bck == unsorted_chunks(av) &&
              victim == av->last_remainder &&
              (unsigned long)(size) > (unsigned long)(nb + MINSIZE)) {
    
            /* split and reattach remainder */
            remainder_size = size - nb;
            remainder = chunk_at_offset(victim, nb);
            unsorted_chunks(av)->bk = unsorted_chunks(av)->fd = remainder;
            av->last_remainder = remainder;
            remainder->bk = remainder->fd = unsorted_chunks(av);
    
            set_head(victim, nb | PREV_INUSE |
    		 (av != &main_arena ? NON_MAIN_ARENA : 0));
            set_head(remainder, remainder_size | PREV_INUSE);
            set_foot(remainder, remainder_size);
    
            check_malloced_chunk(av, victim, nb);
            return chunk2mem(victim);
          }
    

## 多个判断

首先进行判断申请的chunk是否属于smallbin，并且判断unsortedbin中的chunk是否是唯一的chunk，再判断被检查的chunk是否是last_remainder,并且再判断被检查的堆块是否大于请求的大小加上MINSIZE。当全部通过以后，也就是说该chunk就是remainderchunk

## 操作remainderchunk

该chunk的size就等于本身的大小减去请求的大小。并且新的remainderchunk就会成为剩下的那一部分chunk。![image.png](https://image.3001.net/images/20211007/1633595323_615eafbb3a784a19e3556.png!small)画图的话大概就是这样  
然后unsortedbin的fd和bk指针全部指向remainderchunk，并且arena的last_remainder字段指向remainderchunk。而remainderchunk的fd和bk指针全部指向unsortedbin头部![image.png](https://image.3001.net/images/20211007/1633595969_615eb241a028d6824004d.png!small)最后是一个这样的状态  
然后设置victim的size为nb(包含低三位)，设置remainder的size和remainder的下一个chunk的prevsize，最后进行返回。

## 总结

通过这个我们也知道了什么是remainderchunk，首先它必须是再unsortedbin中，而且必须是唯一的chunk，而且上一次的remainderchunk也需要是它，将remainderchunk分割以后请求的返回给用户，剩下的才被称为是last_remainder

# unsortedchunk的返回

我们会发现，之前的语句全都是if语句，也就是说申请的chunk如果前面的都不属于(前面有一个else语句，但是只是设置了idx的值，并没有返回堆块，而是检查fastbin并且进行初始化)，就将unsortedbin的头chunk交出去，整体和smallchunk操作差不多![image.png](https://image.3001.net/images/20211007/1633597237_615eb735c26219f61e5df.png!small)很简单的一个操作

后面就是对chunk的一些数据的写入，和对chunk的返回

# 操作largechunk

我们首先把代码附上，这里是整个malloc代码中唯一对largechunk进行操作的地方

    
    
    if (in_smallbin_range(size)) {
            victim_index = smallbin_index(size);
            bck = bin_at(av, victim_index);
            fwd = bck->fd;
          }
          else {
            victim_index = largebin_index(size);
            bck = bin_at(av, victim_index);
            fwd = bck->fd;
    
            /* maintain large bins in sorted order */
            if (fwd != bck) {
    	  /* Or with inuse bit to speed comparisons */
              size |= PREV_INUSE;
              /* if smaller than smallest, bypass loop below */
    	  assert((bck->bk->size & NON_MAIN_ARENA) == 0);
              if ((unsigned long)(size) <= (unsigned long)(bck->bk->size)) {
                fwd = bck;
                bck = bck->bk;
              }
              else {
    	          assert((fwd->size & NON_MAIN_ARENA) == 0);
                while ((unsigned long)(size) < (unsigned long)(fwd->size)) {
                  fwd = fwd->fd;
    	            assert((fwd->size & NON_MAIN_ARENA) == 0);
    	    }
                bck = fwd->bk;
              }
            }
          }
    
          mark_bin(av, victim_index);
          victim->bk = bck;
          victim->fd = fwd;
          fwd->bk = victim;
          bck->fd = victim;
        }
    
    

首先会判断我们请求的size是否属于smallbin，如果属于的话，分别将fwd和bck分别赋值为相应下标bins的fd和bk指针  
![image.png](https://image.3001.net/images/20211013/1634130173_6166d8fd037e71234a451.png!small)

如果不属于，不属于smallbin(不属于smallbin那么也不属于fastbin，因为前面已经有过检测)，那么就属于largebin，那么将相关数据赋值为largebin的相关数据，然后检测largebin是否为空，不为空的话设置size并且进行断言。再判断我们请求的size是否小于等于bins头chunk的size域，如果结果为真，那么进行操作，画图来看的话比较好一些![image.png](https://image.3001.net/images/20211013/1634130737_6166db310ff836ca9c5dd.png!small)大概是这样的一个操作。而如果结果为假，依旧是下一个断言，然后进行一个循环，然后一直向前进行遍历，直到size
< fwd->size。并且把bck置为fwd->bk

 **由此我们可以知道，largebin中的chunk由尾到头依次变大**

最后进行

    
    
    victim->bk = bck;
          victim->fd = fwd;
          fwd->bk = victim;
          bck->fd = victim;
    

属于一种归值操作

 **这就是这一段的代码，最主要的是对largechunk的操作，也是唯一一段针对largechunk的操作**

 **本文参考自glibc2.31**

