**学系统有四分之一都在学习IO。今天专门来讲解一下Linux下系统的IO。**

# 文件的打开与关闭

首先来说一下open函数。首先来看一下man手册里面对open的调用是怎么样的  
![image.png](https://image.3001.net/images/20211114/1636890521_6190f7997417e322492d6.png!small)我们可以看到open函数有两种调用方式。其中前两个参数是一样的。pathname是传入文件名(绝对路径或相对路径)，第二个参数是文件的访问模式，访问模式分为以下几个：  
![image.png](https://image.3001.net/images/20211114/1636890977_6190f9617cbaaaec354c9.png!small)![image.png](https://image.3001.net/images/20211114/1636890991_6190f96f0e9a85526c797.png!small)上图是《linux系统编程手册》中列举的flag

当我们没有使用O_CREAT标志的时候，mode参数可以省略。如果加上了O_CREAT标志的话，mode则代表着打开文件的权限。该权限以八进制表示，并且最后会与umask进行运算。

如果调用成功的话，open函数将会返回文件描述符。之前简单的说过，open会返回当前可用文件描述符中最小的那个作为返回的文件描述符。如果open函数调用出现错误，那么将会返回-1并且将错误号保存至errno。

当我们想关闭一个文件的时候，就要调用close函数  
![image.png](https://image.3001.net/images/20211114/1636892321_6190fea16bef5fcd5545c.png!small)close函数需要放入一个文件描述符，然后会将其关闭并且将文件描述符释放回该进程。虽然当进程终止的时候也会自动关闭已经打开的文件，但是我们还是应该手动将其关闭。

# 读写函数

## read函数

打开关闭函数都有了，然后我们再来讲一下读写函数。  
![image.png](https://image.3001.net/images/20211114/1636892515_6190ff6375190302df328.png!small)read函数需要放入三个参数，第一个是放入一个文件描述符。第二个是要读入的缓冲区地址。系统库函数不会给我们提供缓冲，所以需要我们自己来创建一个缓冲区。第三个参数是读入缓冲区的字符长度。为了防止缓冲区的溢出我们的缓冲区至少需要count字节。

如果调用成功的话将会返回实际读入的字节数。如果遇到文件结束符（EOF）则返回0.如果调用失败将会返回-1。

不同的文件对读入结束的形式不太一样。举个例子来说，如果我们的文件描述符为标准输入，那么当遇到'\n'也就是换行符就会结束。但是如果读到一般的文件，即便读到'\n'也不会结束。我们具体情况具体分析。

我们来看一个代码

    
    
    #include <stdio.h>
    #include <unistd.h>
    #define MAX_SIZE 20
    main(){
    	char buf[MAX_SIZE];
    	int res = read(0,buf,MAX_SIZE);
    	if(res == -1){
    			printf("Error");
    			exit(1);
    	}
    	printf("%s",buf);
    }
    

这串代码我们来执行以下看看会有什么样的结果  
![image.png](https://image.3001.net/images/20211114/1636893994_6191052a6f280b9384e59.png!small)后面出现了一些其它的字符。我们输入回车确实会换行，但是为什么会有其它的字符？其实原因是我们输入字符以后没有输入结束符'\0'，我们定义buf并没有初始化，buf中还有一些垃圾数据，也会跟着输出出来。

所以说这个代码应该这样写

    
    
    #include <stdio.h>
    #include <unistd.h>
    #define MAX_SIZE 20
    main(){
    	char buf[MAX_SIZE];
    	int res = read(0,buf,MAX_SIZE);
    	if(res == -1){
    			printf("Error");
    			exit(1);
    	}
      buf[res] = '\0';
    	printf("%s",buf);
    }
    

![image.png](https://image.3001.net/images/20211114/1636894324_619106746d760cdda9215.png!small)那么这样安全了吗？至少在这个代码里面没有利用的方式。我们考虑一下，如果我们输入了20个字符以后，这个代码直接会造成数组越界。因为数组下标到19，但是我们在20处输入了'\0'字符。如果换一种场景的话，比如在堆中，就可能造成了off-by-null。具体漏洞这里不细讲了，大家可以看一下我写的漏洞利用的博客。

## write函数

write函数和read函数相对应，是写函数，参数和库一样。从一个缓冲区中读入函数并且写到文件描述符对应的文件中去。

如果调用成功，将会返回实际输出的字节数，如果调用失败将会返回-1并且设置errno。

一般情况下，我们后面的count是多少就会返回多少，但是在出现部分写的情况下才会返回实际输出的字节数。我们来看这样一个例子

    
    
    #include <stdio.h>
    #include <unistd.h>
    #define MAX_SIZE 20
    main(){
    	char buf[MAX_SIZE] = "hello world\n";
    	int res = write(1,buf,MAX_SIZE);
    	printf("%d\n",res);
    	if(res == -1){
    			printf("Error");
    			exit(1);
    	}
    }
    

我们最后输出了res并且发现是20.那么我们更改一下MAX_SIZE的值。  
![image.png](https://image.3001.net/images/20211114/1636895381_61910a9590e85efd68aeb.png!small)将其改为50其实那么输出返回值就成了50.那么这是为什么呢？我们来看一下这个  
![image.png](https://image.3001.net/images/20211114/1636895510_61910b166b7120fd4a7ad.png!small)字符串如果没有填满，后面会以'\0'填充。也就是说并不是没有进行输出，只是因为遇到了'\0'这个结束符。其实在这里的'\0'还是会占用空间的。在某些情况下'\0'将不会占用磁盘空间

# 尝试写一个小工具

我们已经学习了open、close、read、write函数，现在我们已经可以写一个小工具了

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <unistd.h>
    #include <stdio.h>
    
    int main(int argc,char **argv){
    	if(argc<3){
    		printf("input error");
    		exit(1);
    	}
    	char buf;
    	int fd = open(argv[1],O_RDONLY);
    	if(fd == -1){
    		perror("open() fail");
    		exit(1);
    	}
    	int fp = open(argv[2],O_WRONLY|O_CREAT,0666);
    	if(fp == -1){
    		perror("open() fail");
    		exit(1);
    	}
    	for(;read(fd,&buf,1);){				
    		write(fp,&buf,1);
    	}
    	close(fp);
    	close(fd);
    }
    

一个简单的cp小工具。  
虽然尽量使代码保持安全，但是依旧是漏洞百出。我们打开了两个文件，然后将一个文件的字符转移到另一个文件。

# lseek函数与文件空洞

每一个文件都有它的文件位置指针。当我们打开一个文件的时候，文件位置指针在一个文件的开头。然后通过读写函数。每读或写都会将文件位置指针向后移动。直到文件的结尾，遇到EOF文件结束符。

而lseek函数就是调整文件位置指针的函数  
![image.png](https://image.3001.net/images/20211114/1636899243_619119ab3b1589e69c516.png!small)其中offset代表文件位置指针对于whence的偏移，而whence则有以下几个值  
![image.png](https://image.3001.net/images/20211114/1636900523_61911eabba716ed9c2652.png!small)从上往下依次对应文件开头、文件当前位置、文件结尾

如果lseek成功调用则会返回移动后的文件位置指针距离文件头的偏移，调用失败返回-1

![image.png](https://image.3001.net/images/20211114/1636899618_61911b22c29b3f39dd519.png!small)文件位置指针其实就像这个光标一样，我们通过lseek函数进行控制。另外还需要提一下，off_t这个类型比较尴尬，一般情况会被编译为long类型。但是我们也知道long类型有时候是4字节有时候是8字节。如果是4字节的话，那么我们可以想象一下，文件位置指针有正有负，向前为负向后为正。那么最多移动2GB。这就是尴尬的地方，现如今我们超出2G的文件有很多，所以lseek也有它的局限性。

然后还需要说一下文件空洞。什么是文件空洞呢？我们知道当我们读一个文件的时候，到了文件最后就会遇到EOF结束符，但是write函数却可以继续往后写，画个图就是这样  
![image.png](https://image.3001.net/images/20211114/1636900009_61911ca96d3ab35683453.png!small)看到了吗？从最开始的最后一个1，到第二组第一个1，中间的部分就是文件空洞。文件空洞中间将会被'\0'填充，并且会使你的文件看上去很大。但是实际不占用磁盘空间。如果我们想往该区域写数据，就会将'\0'覆盖掉。我们常用的迅雷，在进行传输的过程中就会先创建一个空洞文件。因为迅雷传输方式是P2P传输，一大块数据分成了好几个小块。计算机也不知道哪一块什么时候到达，因此先创建一个空洞文件，每当一块数据到了以后就在相应位置写入数据。

我们来看一下这个代码

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    int main(int argc, char *argv[])
    {
        int fd;
        fd = open(argv[1], O_RDWR);
        if (fd<0){
            perror("fd<0");
            return 0;
        }
        lseek(fd, 51200,SEEK_SET);
        write(fd, "abcde",5);
        close(fd);
        return 0;
    }
    

当我们打开一个文件的时候，它的文件位置指针在最开始，并且里面没有任何数据。然后运行这串代码  
![image.png](https://image.3001.net/images/20211115/1636955915_6191f70bbaaca4d36b294.png!small)占用了51205个字节。然后我们来看一下占用了多少个扇区  
![image.png](https://image.3001.net/images/20211115/1636956168_6191f80862f8b76ea99c9.png!small)一共占用了8个扇区。差距很大吧？这就是文件空洞。我们再看一下文件的内容：  
![image.png](https://image.3001.net/images/20211115/1636956279_6191f877163109f73fb43.png!small)都是以'\0'字符进行的填充。当我们用read函数读取文件的时候，最开始也是会读到'\0'字符。

**总结：这次主要讲解了基本的IO，写了一些代码，但是这些代码都是有不少的漏洞。还简单的了解了一下文件空洞和空洞使用的实例。那么如果遇到了多进程或者多线程操作，我们需要考虑更多。**

 **本文章参考自[空洞文件](https://github.com/Kevin-fqh/learning-k8s-source-code/blob/master/Linux/%2808%29%E7%A9%BA%E6%B4%9E%E6%96%87%E4%BB%B6.md)、书籍《Linux系统编程手册》**

