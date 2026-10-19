原文：<http://hypercrux.com/bug-report/2017/06/19/DIR605L-DoS-BugReport/>  
译者：Serene

#### 介绍

由于去年掀起的物联网/可嵌入设备安全事件的浪潮，我开始有兴趣寻找附近和家中使用设备的漏洞。因为我知道大多数这些设备都存在安全和隐私问题，所以一开始我自己并没有很多这样的设备。我从一箱旧路由器中选择了D-Link DIR-615L，事实证明这是研究的一个很好的开始。

在几周的尝试之后，我发现了一个通过发送GET请求到它的web服务器就能允许我重启路由器的漏洞，我决定重点研究这个漏洞，并试图找到漏洞出现的位置和根本原因。由于我对C语言和MIPS汇编了解的知识有限，这些尝试对我来说是很好的挑战和学习经验。总的来说，这是一个有趣的项目，并且我因此得到了第一个CVE，这是我第一次向厂商报告漏洞，D-Link很快作了回应并修复了这个漏洞，太让人高兴了。

以下是我提交给D-Link的报告，包括我的发现以及漏洞的潜在成因。现在已经发布了补丁，我想将更新的可执行文件与有漏洞的可执行文件进行比较，明确补丁程序和修复程序的确切位置，之后会有一个后续的文章来讲这个分析结果。

#### DIR-605L通过HTTP GET拒绝服务

在尝试通过浏览器URL来访问web根目录下的已知文件时，服务器的响应挂在`http://192.168.1.1/common/`请求上，我注意到路由器正在自己重启/重置：连接完全断开了，系统LED灯在启动时闪烁。这个行为只有在目录尾部“/”被包含时，才会被触发。更进一步的测试表明，只有GET请求时会导致崩溃，HEAD请求会导致服务器的空的200
OK响应，并不会崩溃。这些结果让我有理由相信，导致崩溃的原因在Boa web服务器的某个位置。

##### 细节：

  * 设备：D-Link DIR-605L, B型
  * 有漏洞的固件版本：2.08UIB01及以前的版本。2.08UIBETA01版本得以修复。
  * 攻击向量：未认证的HTTP GET请求
  * 影响：拒绝服务
  * CVE：CVE-2017-9675

##### PoC：

`curl http://192.168.1.1/common/`

##### 静态代码分析：

我从[官网](http://www.boa.org/)下载了Boa
web服务器的匹配版本，路由器上服务器响应的“Server”字符串表明它使用的是0.94.14rc21版本。我知道这是一个修改后的版本，以`apmib.so`的自定义库和其它可能的修改构建，但这与我想要得到的源代码非常接近。路由器上存在的boa二进制文件的一些细节：

    
    
    hyper@ubuntu:~/squashfs-root-0$ mips-linux-gnu-objdump -f bin/boa
    
    bin/boa:     file format elf32-tradbigmips
    architecture: mips:3000, flags 0x00000102:
    EXEC_P, D_PAGED
    start address 0x00407400

因为漏洞只会由GET请求触发，我推测漏洞发生在处理GET的函数中的某个地方，并且只在那些处理目录GET的函数中，另外，只有包含尾部"/"的目录请求会触发漏洞，这意味着修改或使用URL字符串的函数可能是罪魁祸首。

在提取下载的文件后，我开始阅读源代码，寻找可能包含处理请求的代码。果然，在src/目录中有一个命名为 request.c
的文件，于是我从这里开始着手。这个文件中包含了很多处理请求的函数，它们大多数在src /
globals.h中定义的`request`结构上运行。这里有存储请求的路径名和打开文件的文件描述符的成员变量，等等。

###### process_requests()

处理请求自然在`process_requests()`函数中开始，如果队列上有待处理的请求，那么另一个名为`get_request（）`的函数会被调用来从队列中提取请求。这个函数在返回一个到初始化req结构的指针之前，调用其它的一些函数来执行一些基本的清理和处理。如果在几次超时和错误检查之后所有都恢复正常，那么switch..case语句将开始迭代处理请求。

    
    
    if (retval == 1) {
                switch (current->status) {
                case READ_HEADER:
                case ONE_CR:
                case ONE_LF:
                case TWO_CR:
                    retval = read_header(current);
                    break;
                case BODY_READ:
                    retval = read_body(current);
                    break;
                case BODY_WRITE:
                    retval = write_body(current);
                    break;
                case WRITE:
                    retval = process_get(current);
                    break;
                case PIPE_READ:
                    retval = read_from_pipe(current);
                    break;
                case PIPE_WRITE:
                    retval = write_from_pipe(current);
                    break;
                case IOSHUFFLE:
                [...]
                }

###### process_requests() -> read_header()

第一次调用是read.c:`read_header(current)`，“current”是指向正在操作的请求结构的指针。在执行一些操作来读取请求的头部，并设置上面switch语句中用到的一些标志之后，指向“current”的指针被传递给位于request.c中的函数request.c：`process_logline()`。

代码注释中的功能描述：

    
    
    /*
     * Name: process_logline
     *
     * Description: This is called with the first req->header_line received
     * by a request, called "logline" because it is logged to a file.
     * It is parsed to determine request type and method, then passed to
     * translate_uri for further parsing.  Also sets up CGI environment if
     * needed.
     */

request.c:`process_logline()`解析请求URI并处理错误，例如格式错误的请求或无效的URI长度等等。这个函数在处理请求URI，这引起了我的注意，因为只有在向函数的请求中包含了尾部“/”，才会触发该漏洞，所以我想这可能与URI/路径名解析函数有关。经过一段时间审视代码后，我得出结论，漏洞不是在这个函数中引起的，继续往前找。

一旦`process_logline()`返回`read_header()`，下一个根据当前请求运行的函数是request.c:
`process_header_end()`，因为req-> status之前已经被设置为BODY_READ。以下代码段来自`read_header()`：

    
    
                } else {
                    if (process_logline(req) == 0)
                        /* errors already logged */
                        return 0;
                    if (req->http_version == HTTP09)
                        return process_header_end(req);
                }
                /* set header_line to point to beginning of new header */
                req->header_line = check;
            } else if (req->status == BODY_READ) {
    #ifdef VERY_FASCIST_LOGGING
                int retval;
                log_error_time();
                fprintf(stderr, "%s:%d -- got to body read.\n",
                        __FILE__, __LINE__);
                retval = process_header_end(req);
    #else
                int retval = process_header_end(req);
    #endif
                /* process_header_end inits non-POST CGIs */

###### process_requests() -> read_header() -> process_header_end()

如代码注释中的描述所示，在调用get.c:`init_get()`之前，request.c:`process_header_end()`函数会对请求执行一些最终检查。这些测试中大多数是检查req->
request_uri的无效字符或格式错误的输入。我看了一下这些函数，看看这个漏洞是否位于其中一个，但似乎并非如此。

    
    
    /*
     * Name: process_header_end
     *
     * Description: takes a request and performs some final checking before
     * init_cgi or init_get
     * Returns 0 for error or NPH, or 1 for success
     */
    
    int process_header_end(request * req)
    {
        if (!req->logline) {
            log_error_doc(req);
            fputs("No logline in process_header_end\n", stderr);
            send_r_error(req);
            return 0;
        }
    
        /* Percent-decode request */
        if (unescape_uri(req->request_uri, &(req->query_string)) == 0) {
            log_error_doc(req);
            fputs("URI contains bogus characters\n", stderr);
            send_r_bad_request(req);
            return 0;
        }
    
        /* clean pathname */
        clean_pathname(req->request_uri);
    
        if (req->request_uri[0] != '/') {
            log_error("URI does not begin with '/'\n");
            send_r_bad_request(req);
            return 0;
        }
    
        [...]
    
        if (translate_uri(req) == 0) { /* unescape, parse uri */
            /* errors already logged */
            SQUASH_KA(req);
            return 0;               /* failure, close down */
        }
        [...]
    
        if (req->cgi_type) {
            return init_cgi(req);
        }
    
        req->status = WRITE;
    
        return init_get(req);       /* get and head */
    }

所有检查完成后，还有一个检查看'req-> cgi_type'是否已被初始化。由于没有设置这个变量，检查失败了，而是'req->
status'被设置为WRITE，`init_get()`被调用，并且它的返回值被用作`process_header_end()`返回值。

###### process_requests() -> read_header() -> process_header_end() ->
init_get()

从下面get.c:`init_get()`的描述中看，我可以说这个请求将遵循这个路径，因为它是一个非脚本GET请求。

    
    
    /*
     * Name: init_get
     * Description: Initializes a non-script GET or HEAD request.
     */
    
    int init_get(request * req)
    {
        int data_fd, saved_errno;
        struct stat statbuf;
        volatile unsigned int bytes_free;
    
        data_fd = open(req->pathname, O_RDONLY);
        saved_errno = errno;        /* might not get used */
    
        [...]
    
        fstat(data_fd, &statbuf);

一个整型变量被声明来保存打开路径的结果文件描述符和一个名为statbuf的stat结构。statbuf保存关于打开文件状态的信息，它被初始化调用`fstat()`。

在测试看路径是否被成功打开后，接着检查看是否是一个目录，在触发漏洞的请求情况下这将为true。打开文件描述符是关闭的，然后执行检查来看请求的最后一个字符是不是“/”，这将为false，所以后面的代码会被跳过。

    
    
        if (S_ISDIR(statbuf.st_mode)) { /* directory */
            close(data_fd);         /* close dir */
    
            if (req->pathname[strlen(req->pathname) - 1] != '/') {
                char buffer[3 * MAX_PATH_LENGTH + 128];
                unsigned int len;
    
                [...]
            }
    
            data_fd = get_dir(req, &statbuf); /* updates statbuf */
    
            if (data_fd < 0)      /* couldn't do it */
                return 0;           /* errors reported by get_dir */
            else if (data_fd == 0 || data_fd == 1)
                return data_fd;
            /* else, data_fd contains the fd of the file... */
        }
    }

下一个将要执行的代码段，将在调用`get_dir()`时开始。

###### process_requests() -> read_header() -> process_header_end() ->
init_get() -> get_dir()

这一点上，我认为get.c:`get_dir()`可能包含了导致崩溃的函数调用，因为直到这一点所有发生的事情都适用于非目录的请求。现有的常规文件没有请求触发崩溃，这意味着它一定在与打开目录有关的函数中。

    
    
    /*
     * Name: get_dir
     * Description: Called from process_get if the request is a directory.
     * statbuf must describe directory on input, since we may need its
     *   device, inode, and mtime.
     * statbuf is updated, since we may need to check mtimes of a cache.
     * returns:
     *  -1 error
     *  0  cgi (either gunzip or auto-generated)
     *  >0  file descriptor of file
     */
    
    int get_dir(request * req, struct stat *statbuf)
    {
    
        char pathname_with_index[MAX_PATH_LENGTH];
        int data_fd;
    
        if (directory_index) {      /* look for index.html first?? */
    
        [...]

这个函数首先检查请求目录中的index.html文件，因为这将是false（在请求目录中没有名为index.html的文件存在），执行将跳过下面的代码段。

注意：'dirmaker'是一个指向char数组的指针，它使用在boa.conf中配置的DirectoryMaker值进行初始化。在通过telnet检查路由器上设置了什么之后，我看到它被配置为使用'/
usr / lib / boa / boa_indexer'，这在路由器上是不存在的文件。这可能是也可能不是导致漏洞的原因，我将在下一部分中解释。

    
    
        /* only here if index.html, index.html.gz don't exist */
        if (dirmaker != NULL) {     /* don't look for index.html... maybe automake? */
            req->response_status = R_REQUEST_OK;
            SQUASH_KA(req);
    
            /* the indexer should take care of all headers */
            if (req->http_version != HTTP09) {
                req_write(req, http_ver_string(req->http_version));
                req_write(req, " 200 OK" CRLF);
                print_http_headers(req);
                print_last_modified(req);
                req_write(req, "Content-Type: text/html" CRLF CRLF);
                req_flush(req);
            }
            if (req->method == M_HEAD)
                return 0;
    
            return init_cgi(req);
            /* in this case, 0 means success */
        } else if (cachedir) {
            return get_cachedir_file(req, statbuf);
        } else {                    /* neither index.html nor autogenerate are allowed */
            send_r_forbidden(req);
            return -1;              /* nothing worked */
        }
    }

在这一块中，有一个写入服务器回复HTTP
200响应的内部块，在这一块最后有一个检查来看是否请求方法是HEAD，如果是的，函数返回为0.当我们发送HEAD请求时，这里就是函数停止的位置，并且不会发生崩溃。如果该请求方法不是HEAD，那么这个块返回为`init_cgi()`。

###### process_requests() -> read_header() -> process_header_end() ->
init_get() -> get_dir() -> init_cgi()

如下面代码段所示，`init_cgi()`首先声明几个变量将为以后所用，这里有一个检查看是否已经设置了req->
cgi_type，因为它还没有设置，所以被跳过了。下一部分的代码包含了一个检查，来看是否req->pathname的最后一个字符等于“/”，以及req->cgi_type还没有设置。这个评估是true，它将use_pipes设置为1，打开一个未命名的管道，它读取和写入fd的存储在管道[]中。

    
    
    int init_cgi(request * req)
    {
        int child_pid;
        int pipes[2];
        int use_pipes = 0;
    
        SQUASH_KA(req);
    
        if (req->cgi_type) {
            if (complete_env(req) == 0) {
                return 0;
            }
        }
        DEBUG(DEBUG_CGI_ENV) {
            int i;
            for (i = 0; i < req->cgi_env_index; ++i)
                log_error_time();
                fprintf(stderr, "%s - environment variable for cgi: \"%s\"\n",
                        __FILE__, req->cgi_env[i]);
        }
    
        /* we want to use pipes whenever it's a CGI or directory */
        /* otherwise (NPH, gunzip) we want no pipes */
        if (req->cgi_type == CGI ||
            (!req->cgi_type &&
             (req->pathname[strlen(req->pathname) - 1] == '/'))) {
            use_pipes = 1;
            if (pipe(pipes) == -1) {
                log_error_doc(req);
                perror("pipe");
                return 0;
            }

如果打开管道时没有错误，fork()会被调用，它的返回值会被储存。然后switch语句检查fork()的返回值，如果fork成功，那么case
0是true，并且接下来执行的代码（在子进程中）会是检查‘use_pipes’的if语句中的代码块，因为这会返回true。

    
    
    child_pid = fork();
    switch (child_pid) {
    case -1:
        /* fork unsuccessful */
        /* FIXME: There is a problem here. send_r_error (called by
            * boa_perror) would work for NPH and CGI, but not for GUNZIP.  
            * Fix that. 
            */
        boa_perror(req, "fork failed");
        if (use_pipes) {
            close(pipes[0]);
            close(pipes[1]);
        }
        return 0;
        break;
    case 0:
        /* child */
        reset_signals();
    
        if (req->cgi_type == CGI || req->cgi_type == NPH) {
            /* SKIPPED */
        }
    
        if (use_pipes) {
            /* close the 'read' end of the pipes[] */
            close(pipes[0]);
            /* tie CGI's STDOUT to our write end of pipe */
            if (dup2(pipes[1], STDOUT_FILENO) == -1) {
                log_error_doc(req);
                perror("dup2 - pipes");
                _exit(EXIT_FAILURE);
            }
            close(pipes[1]);
        }

正如代码注释中描述的，之前打开的管道的‘read’端被关闭了，STDOUT使用dup2（）绑定到管道的‘write’端。最后，如果所有成功完成，下一个相关的代码段将是如下所示。

    
    
            /*
             * tie STDERR to cgi_log_fd
             * cgi_log_fd will automatically close, close-on-exec rocks!
             * if we don't tie STDERR (current log_error) to cgi_log_fd,
             *  then we ought to tie it to /dev/null
             *  FIXME: we currently don't tie it to /dev/null, we leave it
             *  tied to whatever 'error_log' points to.  This means CGIs can
             *  scribble on the error_log, probably a bad thing.
             */
            if (cgi_log_fd) {
                dup2(cgi_log_fd, STDERR_FILENO);
            }
    
            if (req->cgi_type) {
                char *aargv[CGI_ARGC_MAX + 1];
                create_argv(req, aargv);
                execve(req->pathname, aargv, req->cgi_env);
            } else {
                if (req->pathname[strlen(req->pathname) - 1] == '/')
                    execl(dirmaker, dirmaker, req->pathname, req->request_uri,
                          (void *) NULL);

因为req->cgi_type还没有设置，所以检查它的值的if语句之后的代码块被跳过了，而是执行else语句后面的块，这将检查是否req->pathname最后的字符是‘/’。如果是路径名导致了崩溃的情况下，这个评估将是true。`execl()`被这样调用：

    
    
    execl(dirmaker, dirmaker, req->pathname, req->request_uri, (void *) NULL);

#### 潜在的根本原因

##### execl()的错误使用

前面提到过，'dirmaker'是一个指向char数组的指针，它使用在boa.conf中配置的DirectoryMaker值进行初始化（在路由器的情况下，这是‘/usr/lib/boa/boa_indexer’，一个不在系统中存在的文件）。这有可能是导致崩溃的潜在原因。

来自<http://pubs.opengroup.org/onlinepubs/7908799/xsh/execl.html>：

>
> 如果过程映像文件不是有效的可执行对象，execlp()和execvp()使用该文件内容作为符合system()的命令解释器的标准输入。在这种情况下，命令解释器成为新的过程映像。

另一个可能是传递给函数的最后一个参数。

来自手册`exec()`：

> execl(), execlp(), 和 execle()函数中的const char * arg和后续的省略号可以被认为是arg0, arg1, …,
> argn. 参数列表必须被一个空指针终止，并且因为这些是可变参数函数，指针必须强制转换（char *）NULL。

看一下调用`execl()`的方法，表明了最后参数强制转换`(void *) NULL`，而不是`(char *)
NULL`，我一直没找到任何文件表明这是绝对必须的，以及如果使用不同类型的指针，会发生什么情况。

##### 在2.6.x内核中对管道的不安全使用

最后，这个漏洞也可能是管道和文件描述符的不安全使用的结果，如`init_cgi()`所示。Linux内核版本2.6.x已知有关管道的漏洞，可用于获取权限升级。下面的代码段来自[这个漏洞](https://www.exploit-db.com/exploits/33322/)，将漏洞来源与在Boa中的潜在漏洞函数相比较，我们可以看到在调用fork()的上下文中，有非常类似的管道使用。

    
    
        {
            pid = fork();
            if (pid == -1)
            {
                perror("fork");
                return (-1);
            }
            if (pid)
            {
                char path[1024];
                char c;
                /* I assume next opened fd will be 4 */
                sprintf(path, "/proc/%d/fd/4", pid);
                    printf("Parent: %d\nChild: %d\n", parent_pid, pid); 
                while (!is_done(0))
                {
                    fd[0] = open(path, O_RDWR);
                    if (fd[0] != -1)
                    {
                        close(fd[0]);
                    }
                }
                //system("/bin/sh");
                execl("/bin/sh", "/bin/sh", "-i", NULL);
                return (0);
            }

来自[安全编码，CERT](https://wiki.sei.cmu.edu/confluence/display/c/POS38-C.+Beware+of+race+conditions+when+using+fork+and+file+descriptors)：

>
> 当fork子进程时，文件描述符会被复制到子进程中，这可能会导致文件的并发操作。对同一个文件进行并发操作会导致数据以不确定的顺序下被读写，造成竞争条件和不可预知的行为。

#### 结论

到这里我的分析就结束了，除了我对C语言和MIPS的有限知识外，二进制文件模拟环境的难度降低了对我测试理论的能力要求，并得出了一个明确的结论。接下来，我将对Boa的补丁版本进行逆向并确定修复。

#### 参考

  * [Mitre: CVE-2017-9675](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-9675)
  * [DIR-605L Firmware Downloads](http://support.dlink.com/productinfo.aspx?m=DIR-605L)
  * [D-Link DIR-605L Security Advisory](ftp://ftp2.dlink.com/SECURITY_ADVISEMENTS/DIR-605L/REVB/DIR-605L_REVB_RELEASE_NOTES_v2.08UIBETAB01_EN.pdf)
  * [Boa 0.94.14rc21 Source](http://www.boa.org/boa-0.94.14rc21.tar.gz)
  * [Linux Kernel 2.6.x ‘pipe.c’ Privilege Escalation](https://www.exploit-db.com/exploits/33322/)
  * [POS38-C. Beware of race conditions when using fork and file descriptors](https://www.securecoding.cert.org/confluence/display/c/POS38-C.+Beware+of+race+conditions+when+using+fork+and+file+descriptors)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/464/>

