**上次已经比较详细的讲解了unlink宏，但是这只是在代码层面，下面我会讲一下unlink宏的一些逻辑或者是一些思想**

    
    
    #define unlink(AV, P, BK, FD) {                                            
        FD = P->fd;                                   
        BK = P->bk;                                   
        if (__builtin_expect (FD->bk != P || BK->fd != P, 0))             
          malloc_printerr (check_action, "corrupted double-linked list", P, AV);  
        else {                                    
            FD->bk = BK;                                  
            BK->fd = FD;                                  
            if (!in_smallbin_range (P->size)                      
                && __builtin_expect (P->fd_nextsize != NULL, 0)) {            
            if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)        
            || __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))    
              malloc_printerr (check_action,                      
                       "corrupted double-linked list (not small)",    
                       P, AV);                        
                if (FD->fd_nextsize == NULL) {                    
                    if (P->fd_nextsize == P)                      
                      FD->fd_nextsize = FD->bk_nextsize = FD;             
                    else {                                
                        FD->fd_nextsize = P->fd_nextsize;                 
                        FD->bk_nextsize = P->bk_nextsize;                 
                        P->fd_nextsize->bk_nextsize = FD;                 
                        P->bk_nextsize->fd_nextsize = FD;                 
                      }                               
                  } else {                                
                    P->fd_nextsize->bk_nextsize = P->bk_nextsize;             
                    P->bk_nextsize->fd_nextsize = P->fd_nextsize;             
                  }                                   
              }                                   
          }                                       
    }
    
    

# 第一个检查

`if (__builtin_expect (FD->bk != P || BK->fd != P, 0))`  
这一个语句是比较重要的，这个语句就是为了判断你前面的后面是不是你自己。在堆溢出中，会对一些数据进行覆盖(这个后面会讲)，而这个函数在某一层面会阻止覆盖，但是也并不是万能的，因为攻击者还可以构造fake
chunk

# fd_nextsize和bk_nextsize指针

这两个指针并不是largebin中所有的chunk都会用到，只有尾指针才会用到。这里在某乎找到了一张图，一目了然![image.png](https://image.3001.net/images/20210915/1631705931_6141db4b794067eeb2315.png!small)  
看这张图就很容易看出来，fd指针指向高地址chunk，bk指针指向低地址chunk，而fd_nextsize指针指向相邻bin的低地址，bk_nextsize指向相邻largebin的高地址，很明显unlink宏里面脱链时也判断了largechunk的位置，并且对尾chunk也专门进行了脱链处理

**本文参考自[glibc:浅谈unlink](https://blog.csdn.net/Plus_RE/article/details/79270350)、[堆的largebin
attack利用](https://zhuanlan.zhihu.com/p/373555570)，感谢前辈大佬**

