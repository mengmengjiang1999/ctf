**上次简单的介绍了一下基础的IO函数，但是当时也说过，那些代码都是有漏洞的。我们就来分析一下漏洞以及修复的方式**

# 条件竞争

还拿上次的copy小工具来举例

    
    
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
    

我们的工具是打开两个文件，然后将一个文件的内容放到另外一个文件里面去。重点关注一下fp这个文件。这个文件是存在则覆盖，不存在则创建。我们都知道如果open打开一个文件的时候其文件位置指针就会放到文件的最前面。那么如果里面本来就有内容那么就会被覆盖。

我们试想一下这样的情况，当我们同时启动这样的两个进程，然后同时都往同一个文件里面传输数据，会怎么样？进程调度的过程中一个进程没有执行结束，但是它的时间片已经结束了，于是换成了另外一个进程。该进程又打开了文件，将里面的数据覆盖掉。

我们来看一个简单一些的代码

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <unistd.h>
    #include <stdio.h>
    int main(int argc,char **argv){
    	int fd = open(argv[1],O_WRONLY);
    	if(fd!=-1){
    		printf("The file has exists already!");
    		close(fd);
    	}
    	else{
    		fd = open(argv[1],O_WRONLY|O_CREAT,0666);
    		if(fd == -1){
    				perror("open()");
    				exit(1);
    		}
    		printf("The file creat successfully");
    		}
    }
    

该进程要创建一个文件，而且必须要是该进程本身创建的文件。那么这样可以保证文件一定是自己的原创了吗？并不一定，我们开启两个相同的该进程，在进程A

    
    
    if(fd!=-1){
    		printf("The file has exists already!");
    		close(fd);
    }
    

这条语句结束以后，进程A的时间片用完了，然后进程B开始执行，同样的文件名。然后B成功创建，但是A该执行else语句了，所以A也以为这个文件是它自己创建的。我们对代码进行一个小小的修改

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <unistd.h>
    #include <stdio.h>
    int main(int argc,char **argv){
    	int fd = open(argv[1],O_WRONLY);
    	if(fd!=-1){
    		printf("The file has exists already!");
    		close(fd);
    	}
    	else{
        if(argc > 2)
            sleep(10);
    		fd = open(argv[1],O_WRONLY|O_CREAT,0666);
    		if(fd == -1){
    				perror("open()");
    				exit(1);
    		}
    		printf("The file creat successfully");
    		}
    }
    

我们专门设置一个这样的语句，要求睡眠的进程我们输入三个参数，多加一个sleep。这就是我们所说的进程A。然后正常执行的进程我们输入参数是只输入两个参数  
![image.png](https://image.3001.net/images/20211115/1636967767_619225570af9d465e02ab.png!small)  
专门开了两个shell，我们可以看一下两个进程都认为文件是它们创建的。两个进程同时对同一个资源进行访问，最后造成了错误。我们就将这种情况称为条件竞争。我们看一下进程执行的流程  
![image.png](https://image.3001.net/images/20211115/1636968223_6192271f9b18dddb58d97.png!small)  
考虑一个更糟糕的情况，比如说需要往里面写数据，那么就会产生覆盖的情况

# 原子操作

出现上述情况我们就要想办法将其避免。上面的情况主要是因为进程执行的时候指令被中断掉了，那么我们就要依靠原子操作。原子操作是什么？原子操作就是说一个指令要么不执行，只要执行就执行完。在并发执行中经常用到。

上述代码中我们就要添加原子操作，比如这样`fd =
open(argv[1],O_WRONLY|O_CREAT|O_EXCL,0666);`。当O_CREAT标志和O_EXCL标志同时存在时，就会进行检测。如果文件存在则会发生报错。这样的语句是不能被打断的，一旦执行就要执行到底。也通过这类方式避免了open类型的条件竞争。

# 读取和更改文件的标志位

## F_GETFL参数

除了以上述方式更改，还有一种方法。通过调用fcntl函数来进行设置。所以这里就先简单介绍一下这个函数  
![image.png](https://image.3001.net/images/20211115/1636976059_619245bbc7a703576349d.png!small)  
其中fd表示的是传入的文件描述符，cmd表示指令。一共有很多不同的指令，这里我们先介绍F_GETFL和F_SETFL指令。然后第三个参数在某些情况下需要用到。首先来看一下F_GETFL。我们先来简单的用一下这个函数

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <unistd.h>
    #include <stdio.h>
    #include <stdlib.h>
    int main(){
    	int fd = open("obj_getfl",O_WRONLY|O_CREAT,0666);
    	if(fd == -1){
    		perror("open()");
    		exit(1);
    
    	}
    	int flag = fcntl(fd,F_GETFL);
    	if(flag == 1){
    		perror("fcntl()");
    		exit(1);
    
    	}
    	printf("the flag of the process %d is %d",getpid(),flag);
    	gets();
    	return 0;
     }
    

然后我们看一下输出的内容  
![image.png](https://image.3001.net/images/20211115/1636977037_6192498d7339d8e22e0d5.png!small)  
最后返回的是文件的状态标志![image.png](https://image.3001.net/images/20211115/1636977314_61924aa2e271e1a142d1e.png!small)  
根据这个标志，我们可以判断一个文件是否具有某个状态。我们只需要让flag和一个状态标志位进行按位与运算就可以得出。

我们还可以判断一个文件的访问情况。是以什么权限进行的访问，可读、可写还是读写。但是访问权限并不与打开文件的状态标志位的单个比特位对应，所以还需要掩码O_ACCMODE参与运算，这里还有一个公式  
`accessMode = flag & O_ACCMODE`  
最终得到accessMode以后才可以得出访问状态。

我们再把open的标志位复习一下  
![image.png](https://image.3001.net/images/20211115/1636977773_61924c6d0272deb14d3a3.png!small)  
![image.png](https://image.3001.net/images/20211115/1636977790_61924c7e02f0f14b6ae66.png!small)

其中最上面的三个是文件的访问模式，中间的这部分是文件的创建标志，最后的五个是已经打开文件的状态标志

然后我们返回去看上面的输出32769，然后我们去往这个目录：/proc/11128/fdinfo，然后使用ls查看打开文件  
![image.png](https://image.3001.net/images/20211115/1636978055_61924d87e299847737f1d.png!small)  
其中0、1、2就不再多说，我们使用cat 3  
![image.png](https://image.3001.net/images/20211115/1636978088_61924da86154c997d64d6.png!small)  
其中有个flags字段，该字段记录了打开文件的状态标志。以0开头表示这是8进制，然后变为十进制以后就会发现正是我们的flag的值。那么O_ACCMODE又是什么呢？该值是八进制中的3。也就是二进制中的11，我们的访问模式需要两个标志位来表示。00代表只读，01代表只写，11代表读写。这也就是为什么我们需要依靠O_ACCMODE来得到文件访问标志了。

## F_SETFL参数

说完得到flag值，然后我们就可以讲解一下修改falgs的值了。第二个参数中填写F_SETFL，第三个参数中填写flag。通过这种方式我们可以更改一些flags标志  
`flags |= O_APPEND;fcntl(fd,F_SETFL,flags);`

**这就是有关open的条件竞争和解决条件竞争的方法，也就是通过原子操作来使指令不可被打断。我们还可以通过fcntl函数来修改文件的标志，通过修改标志来防止条件竞争**

