#####
写这篇文章的初衷就是在做pwn的时候会遇到一些对我这样的菜鸡比较不友好的题目，自己在漏洞复现的时候默认使用glibc2.27版本导致的版本不一样，就非常难受，下面开搞

    
    
    #首先下载glibc-all-in-one和patchelf(先更新为清华镜像源)
    git clone https://github.com/matrix1001/glibc-all-in-one
    
    git clone https://github.com/NixOS/patchelf
    
    #然后进入glibc-all-in-one的文件夹
    cd glibc-all-in-one
    
    #进入文件夹后，执行update_list,然后会在文件夹内出现list和old_list两个文件
    #查看两个文件
    cat list/old_list
    
    #输出的内容为可供下载的glibc版本
    #执行download或者download_old(具体执行哪个看是再list中还是再list_old中)
    #下载完以后会出现一个libs文件夹，里面存放的就是下载的glibc文件夹
    #下载完patchelf后进入该文件夹
    #并且执行以下代码
    
    
    ./bootstrap.sh
    ./configure
    make
    sudo make install
    make check
    
    #然后执行以下的patch代码
    patch --set-interpreter [你下载的glibc目录下ld文件] --set-rpath [libc的目录] [需要更改的文件]
    

下面还有测试图  
![Untitled.png](https://image.3001.net/images/20210908/1631110206_6138c43e752e6c5231b36.png!small)  
输入ldd [文件名]可以得到它的glibc版本  
![Untitled.png](https://image.3001.net/images/20210908/1631110285_6138c48d57b8cb6aa3149.png!small)  
这个是我上面写的那条命令  
![Untitled.png](https://image.3001.net/images/20210908/1631110323_6138c4b32917a4b2d7a9b.png!small)  
再来一波ldd命令查看，发现已经改了

了解elf文件的朋友可以具体了解一下patchelf的原理，还是比较巧妙的。然后就再也不怕漏洞复现的时候glibc版本不一样。

######
glibc版本不一样最开始巨难受，也不知道怎么办，因为版本不一样在内存管理方面的一些细节也不一样，改了以后就好很多了。(比如我学堆的时候用的glibc2.27版本，和ctfwiki上用的版本不一样，造成的结果有很大的困扰)

