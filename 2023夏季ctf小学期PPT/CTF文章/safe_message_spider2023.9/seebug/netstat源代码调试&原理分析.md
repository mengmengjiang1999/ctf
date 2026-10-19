**作者：Spoock**  
**来源：<https://blog.spoock.com/2019/05/26/netstat-learn/>**

### 说明

估计平时大部分人都是通过`netstat`来查看网络状态，但是事实是`netstat`已经逐渐被其他的命令替代，很多新的Linux发行版本中很多都不支持了`netstat`。以`ubuntu
18.04`为例来进行说明：

    
    
    ~ netstat 
    zsh: command not found: netstat

按照[difference between netstat and ss in
linux?](https://stackoverflow.com/questions/11763376/difference-between-netstat-and-ss-in-linux)这篇文章的说法,

> NOTE This program is obsolete. Replacement for netstat is ss. Replacement
> for netstat -r is ip route. Replacement for netstat -i is ip -s link.
> Replacement for netstat -g is ip maddr.

中文含义就是:`netstat`已经过时了，`netstat`的部分命令已经被`ip`这个命令取代了，当然还有更为强大的`ss`。
`ss`命令用来显示处于活动状态的套接字信息。ss命令可以用来获取socket统计信息，它可以显示和netstat类似的内容。但ss的优势在于它能够显示更多更详细的有关TCP和连接状态的信息，而且比`netstat`更快速更高效。`netstat`的原理显示网络的原理仅仅只是解析`/proc/net/tcp`,所以如果服务器的socket连接数量变得非常大，那么通过`netstat`执行速度是非常慢。而`ss`采用的是通过`tcp_diag`的方式来获取网络信息，`tcp_diag`通过netlink的方式从内核拿到网络信息，这也是`ss`更高效更全面的原因。

下图就展示了`ss`和`nestat`在监控上面的区别。

[![img](https://images.seebug.org/content/images/2019/05/29/1559100037000-1vfvgi.png-w331s)](https://blog.spoock.com/2019/05/26/netstat-learn/ss.png)

`ss`是获取的`socket`的信息，而`netstat`是通过解析`/proc/net/`下面的文件来获取信息包括`Sockets`,`TCP/UDP`，`IP`，`Ethernet`信息。

`netstat`和`ss`的效率的对比，找同一台机器执行:

    
    
    time ss
    ........
    real    0m0.016s
    user    0m0.001s
    sys     0m0.001s
    --------------------------------    time netstat
    real    0m0.198s
    user    0m0.009s
    sys     0m0.011s

`ss`明显比`netstat`更加高效.

### netstat简介

`netstat`是在`net-tools`工具包下面的一个工具集，[net-tools](https://github.com/ecki/net-tools)提供了一份`net-tools`的源码，我们通过`net-tools`来看看`netstat`的实现原理。

#### netstat源代码调试

下载`net-tools`之后，导入到`Clion`中，创建`CMakeLists.txt`文件，内容如下：

    
    
    cmake_minimum_required(VERSION 3.13)
    project(test C)
    
    set(BUILD_DIR .)
    
    #add_executable()
    add_custom_target(netstat command -c ${BUILD_DIR})

修改根目录下的`Makefile`中的59行的编译配置为：

    
    
    CFLAGS ?= -O0 -g3

[![img](https://images.seebug.org/content/images/2019/05/29/1559100039000-2hmpqg.png-w331s)](https://blog.spoock.com/2019/05/26/netstat-learn/netstat.png)

按照如上图设置自己的编译选项

以上就是搭建`netstat`的源代码调试过程。

#### tcp show

在netstat不需要任何参数的情况，程序首先会运行到2317行的`tcp_info()`

    
    
    #if HAVE_AFINET
        if (!flag_arg || flag_tcp) {
            i = tcp_info();
            if (i)
            return (i);
        }
    
        if (!flag_arg || flag_sctp) {
            i = sctp_info();
            if (i)
            return (i);
        }
    .........

跟踪进入到`tcp_info()`:

    
    
    static int tcp_info(void)
    {
        INFO_GUTS6(_PATH_PROCNET_TCP, _PATH_PROCNET_TCP6, "AF INET (tcp)",
               tcp_do_one, "tcp", "tcp6");
    }

参数的情况如下：

  * _PATH_PROCNET_TCP，在`lib/pathnames.h`中定义，是`#define _PATH_PROCNET_TCP "/proc/net/tcp"`

  * _PATH_PROCNET_TCP6, 在`lib/pathnames.h`中定义, 是`#define _PATH_PROCNET_TCP6 "/proc/net/tcp6"`

  * `tcp_do_one`,函数指针，位于1100行，部分代码如下：

    
    
    static void tcp_do_one(int lnr, const char *line, const char *prot)
    {
    unsigned long rxq, txq, time_len, retr, inode;
    int num, local_port, rem_port, d, state, uid, timer_run, timeout;
    char rem_addr[128], local_addr[128], timers[64];
    const struct aftype *ap;
    struct sockaddr_storage localsas, remsas;
    struct sockaddr_in *localaddr = (struct sockaddr_in *)&localsas;
    struct sockaddr_in *remaddr = (struct sockaddr_in *)&remsas;
    ......

`tcp_do_one()`就是用来解析`/proc/net/tcp`和`/proc/net/tcp6`每一行的含义的，关于`/proc/net/tcp`的每一行的含义可以参考之前写过的[osquery源码解读之分析process_open_socket](https://blog.spoock.com/2018/12/06/osquery-source-analysis-process-open-socket/)中的扩展章节。

#### INFO_GUTS6

    
    
    #define INFO_GUTS6(file,file6,name,proc,prot4,prot6)    \
     char buffer[8192];                 \
     int rc = 0;                        \
     int lnr = 0;                       \
     if (!flag_arg || flag_inet) {              \
        INFO_GUTS1(file,name,proc,prot4)            \
     }                          \
     if (!flag_arg || flag_inet6) {             \
        INFO_GUTS2(file6,proc,prot6)            \
     }                          \
     INFO_GUTS3

`INFO_GUTS6`采用了`#define`的方式进行定义，最终根据是`flag_inet`(IPv4)或者`flag_inet6`(IPv6)的选项分别调用不同的函数，我们以`INFO_GUTS1(file,name,proc,prot4)`进一步分析。

#### INFO_GUTS1

    
    
    #define INFO_GUTS1(file,name,proc,prot)         \
      procinfo = proc_fopen((file));            \
      if (procinfo == NULL) {               \
        if (errno != ENOENT && errno != EACCES) {       \
          perror((file));                   \
          return -1;                    \
        }                           \
        if (!flag_noprot && (flag_arg || flag_ver))     \
          ESYSNOT("netstat", (name));           \
        if (!flag_noprot && flag_arg)           \
          rc = 1;                       \
      } else {                      \
        do {                        \
          if (fgets(buffer, sizeof(buffer), procinfo))  \
            (proc)(lnr++, buffer,prot);         \
        } while (!feof(procinfo));              \
        fclose(procinfo);                   \
      }

  1. `rocinfo = proc_fopen((file))` 获取`/proc/net/tcp`的文件句柄
  2. `fgets(buffer, sizeof(buffer), procinfo)` 解析文件内容并将每一行的内容存储在buffer中
  3. `(proc)(lnr++, buffer,prot)`，利用`(proc)`函数解析buffer。`(proc)`就是前面说明的`tcp_do_one()`函数

#### tcp_do_one

以`" 14: 020110AC:B498 CF0DE1B9:4362 06 00000000:00000000 03:000001B2 00000000
0 0 0 3 0000000000000000`这一行为例来说明`tcp_do_one()`函数的执行过程。
[![img](https://images.seebug.org/content/images/2019/05/29/1559100039000-3eqvxx.png-w331s)](https://blog.spoock.com/2019/05/26/netstat-learn/tcp_do_one_1.png)

由于分析是`Ipv4`，所以会跳过`#if HAVE_AFINET6`这段代码。之后执行：

    
    
    num = sscanf(line,
        "%d: %64[0-9A-Fa-f]:%X %64[0-9A-Fa-f]:%X %X %lX:%lX %X:%lX %lX %d %d %lu %*s\n",
             &d, local_addr, &local_port, rem_addr, &rem_port, &state,
             &txq, &rxq, &timer_run, &time_len, &retr, &uid, &timeout, &inode);
    if (num < 11) {
        fprintf(stderr, _("warning, got bogus tcp line.\n"));
        return;
    }

解析数据，并将每一列的数据分别填充到对应的字段上面。分析一下其中的每个字段的定义：

    
    
    char rem_addr[128], local_addr[128], timers[64];
    struct sockaddr_storage localsas, remsas;
    struct sockaddr_in *localaddr = (struct sockaddr_in *)&localsas;
    struct sockaddr_in *remaddr = (struct sockaddr_in *)&remsas;

在`Linux`中`sockaddr_in`和`sockaddr_storage`的定义如下：

    
    
    struct sockaddr {
       unsigned short    sa_family;    // address family, AF_xxx
       char              sa_data[14];  // 14 bytes of protocol address
    };
    
    
    struct  sockaddr_in {
        short  int  sin_family;                      /* Address family */
        unsigned  short  int  sin_port;       /* Port number */
        struct  in_addr  sin_addr;              /* Internet address */
        unsigned  char  sin_zero[8];         /* Same size as struct sockaddr */
    };
    /* Internet address. */
    struct in_addr {
      uint32_t       s_addr;     /* address in network byte order */
    };
    
    struct sockaddr_storage {
        sa_family_t  ss_family;     // address family
    
        // all this is padding, implementation specific, ignore it:
        char      __ss_pad1[_SS_PAD1SIZE];
        int64_t   __ss_align;
        char      __ss_pad2[_SS_PAD2SIZE];
    };

之后代码继续执行：

    
    
    sscanf(local_addr, "%X", &localaddr->sin_addr.s_addr);
    sscanf(rem_addr, "%X", &remaddr->sin_addr.s_addr);
    localsas.ss_family = AF_INET;
    remsas.ss_family = AF_INET;

将`local_addr`使用`sscanf(,"%X")`得到对应的十六进制，保存到`&localaddr->sin_addr.s_addr`(即`in_addr`结构体中的`s_addr`)中,同理`&remaddr->sin_addr.s_addr`。运行结果如下所示:

[![img](https://images.seebug.org/content/images/2019/05/29/1559100040000-4fvnqb.png-w331s)](https://blog.spoock.com/2019/05/26/netstat-learn/saddr.png)

#### addr_do_one

    
    
    addr_do_one(local_addr, sizeof(local_addr), 22, ap, &localsas, local_port, "tcp");
    addr_do_one(rem_addr, sizeof(rem_addr), 22, ap, &remsas, rem_port, "tcp");

程序继续执行，最终会执行到`addr_do_one()`函数，用于解析本地IP地址和端口，以及远程IP地址和端口。

    
    
    static void addr_do_one(char *buf, size_t buf_len, size_t short_len, const struct aftype *ap,
                const struct sockaddr_storage *addr,
                int port, const char *proto
    )
    {
        const char *sport, *saddr;
        size_t port_len, addr_len;
    
        saddr = ap->sprint(addr, flag_not & FLAG_NUM_HOST);
        sport = get_sname(htons(port), proto, flag_not & FLAG_NUM_PORT);
        addr_len = strlen(saddr);
        port_len = strlen(sport);
        if (!flag_wide && (addr_len + port_len > short_len)) {
            /* Assume port name is short */
            port_len = netmin(port_len, short_len - 4);
            addr_len = short_len - port_len;
            strncpy(buf, saddr, addr_len);
            buf[addr_len] = '\0';
            strcat(buf, ":");
            strncat(buf, sport, port_len);
        } else
              snprintf(buf, buf_len, "%s:%s", saddr, sport);
    }

  1. `saddr = ap->sprint(addr, flag_not & FLAG_NUM_HOST);` 这个表示是否需要将`addr`转换为域名的形式。由于`addr`值是`127.0.0.1`，转换之后得到的就是`localhost`，其中`FLAG_NUM_HOST`的就等价于`--numeric-hosts`的选项。
  2. `sport = get_sname(htons(port), proto, flag_not & FLAG_NUM_PORT);`,`port`无法无法转换,其中的`FLAG_NUM_PORT`就等价于`--numeric-ports`这个选项。
  3. `!flag_wide && (addr_len + port_len > short_len` 这个代码的含义是判断是否需要对`IP`和`PORT`进行截断。其中`flag_wide`的等同于`-W, --wide don't truncate IP addresses`。而`short_len`长度是22.
  4. `snprintf(buf, buf_len, "%s:%s", saddr, sport);`,将`IP:PORT`赋值给`buf`.

#### output

最终程序执行

    
    
    printf("%-4s  %6ld %6ld %-*s %-*s %-11s",
               prot, rxq, txq, (int)netmax(23,strlen(local_addr)), local_addr, (int)netmax(23,strlen(rem_addr)), rem_addr, _(tcp_state[state]));

按照制定的格式解析，输出结果

#### finish_this_one

最终程序会执行`finish_this_one(uid,inode,timers);`.

    
    
    static void finish_this_one(int uid, unsigned long inode, const char *timers)
    {
        struct passwd *pw;
    
        if (flag_exp > 1) {
        if (!(flag_not & FLAG_NUM_USER) && ((pw = getpwuid(uid)) != NULL))
            printf(" %-10s ", pw->pw_name);
        else
            printf(" %-10d ", uid);
        printf("%-10lu",inode);
        }
        if (flag_prg)
        printf(" %-" PROGNAME_WIDTHs "s",prg_cache_get(inode));
        if (flag_selinux)
        printf(" %-" SELINUX_WIDTHs "s",prg_cache_get_con(inode));
    
        if (flag_opt)
        printf(" %s", timers);
        putchar('\n');
    }

(1) `flag_exp` 等同于`-e`的参数。`-e, --extend display other/more information`.举例如下：

    
    
       netstat -e 
       Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode
       tcp        0      0 localhost:6379          172.16.1.200:46702    ESTABLISHED redis      437788048
    
       netstat
       Proto Recv-Q Send-Q Local Address           Foreign Address         State      
       tcp        0      0 localhost:6379          172.16.1.200:46702    ESTABLISHED

发现使用`-e`参数会多显示`User`和`Inode`号码。而在本例中还可以如果用户名不存在，则显示 uid
[getpwuid](https://linux.die.net/man/3/getpwuid)

(2) `flag_prg`等同于`-p, --programs display PID/Program name for sockets`。举例如下：

    
    
       netstat -pe
       Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode      PID/Program name
       tcp        0      0 localhost:6379          172.16.1.200:34062      ESTABLISHED redis      437672000  6017/redis-server *
    
       netstat -e
       Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode
       tcp        0      0 localhost:6379          172.16.1.200:46702    ESTABLISHED redis      437788048

可以看到是通过`prg_cache_get(inode)`，inode来找到对应的PID和进程信息;

(3) `flag_selinux`等同于`-Z, --context display SELinux security context for
sockets`

#### prg_cache_get

对于上面的通过`inode`找到对应进程的方法非常的好奇，于是去追踪`prg_cache_get()`函数的实现。

    
    
    #define PRG_HASH_SIZE 211
    
    #define PRG_HASHIT(x) ((x) % PRG_HASH_SIZE)
    
    static struct prg_node {
        struct prg_node *next;
        unsigned long inode;
        char name[PROGNAME_WIDTH];
        char scon[SELINUX_WIDTH];
    } *prg_hash[PRG_HASH_SIZE];
    
    static const char *prg_cache_get(unsigned long inode)
    {
        unsigned hi = PRG_HASHIT(inode);
        struct prg_node *pn;
    
        for (pn = prg_hash[hi]; pn; pn = pn->next)
        if (pn->inode == inode)
            return (pn->name);
        return ("-");
    }

在`prg_hash`中存储了所有的inode编号与`program`的对应关系，所以当给定一个 inode
编号时就能够找到对应的程序名称。那么`prg_hash`又是如何初始化的呢？

#### prg_cache_load

我们使用 debug 模式，加入`-p`的运行参数:

[![img](https://images.seebug.org/content/images/2019/05/29/1559100040000-5xzydv.png-w331s)](https://blog.spoock.com/2019/05/26/netstat-learn/netstat-p.png)

程序会运行到 2289 行的`prg_cache_load()`; 进入到`prg_cache_load()`函数中． 由于整个函数的代码较长，拆分来分析.

##### 获取fd

    
    
    #define PATH_PROC      "/proc"
    #define PATH_FD_SUFF    "fd"
    #define PATH_FD_SUFFl       strlen(PATH_FD_SUFF)
    #define PATH_PROC_X_FD      PATH_PROC "/%s/" PATH_FD_SUFF
    #define PATH_CMDLINE    "cmdline"
    #define PATH_CMDLINEl       strlen(PATH_CMDLINE)
    
    if (!(dirproc=opendir(PATH_PROC))) goto fail;
        while (errno = 0, direproc = readdir(dirproc)) {
        for (cs = direproc->d_name; *cs; cs++)
            if (!isdigit(*cs))
            break;
        if (*cs)
            continue;
        procfdlen = snprintf(line,sizeof(line),PATH_PROC_X_FD,direproc->d_name);
        if (procfdlen <= 0 || procfdlen >= sizeof(line) - 5)
            continue;
        errno = 0;
        dirfd = opendir(line);
        if (! dirfd) {
            if (errno == EACCES)
            eacces = 1;
            continue;
        }
        line[procfdlen] = '/';
        cmdlp = NULL;

(1) `dirproc=opendir(PATH_PROC);errno = 0, direproc = readdir(dirproc)`
遍历`/proc`拿到所有的 pid  
(2) `procfdlen = snprintf(line,sizeof(line),PATH_PROC_X_FD,direproc→d_name);`
遍历所有的`/proc/pid`拿到所有进程的 fd  
(3) `dirfd = opendir(line);` 得到`/proc/pid/fd`的文件句柄

##### 获取inode

    
    
    while ((direfd = readdir(dirfd))) {
            /* Skip . and .. */
            if (!isdigit(direfd->d_name[0]))
                continue;
        if (procfdlen + 1 + strlen(direfd->d_name) + 1 > sizeof(line))
        　　　continue;
        memcpy(line + procfdlen - PATH_FD_SUFFl, PATH_FD_SUFF "/",
            PATH_FD_SUFFl + 1);
        safe_strncpy(line + procfdlen + 1, direfd->d_name,
                        sizeof(line) - procfdlen - 1);
        lnamelen = readlink(line, lname, sizeof(lname) - 1);
        if (lnamelen == -1)
            continue;
            lname[lnamelen] = '\0';  /*make it a null-terminated string*/
    
            if (extract_type_1_socket_inode(lname, &inode) < 0)
                if (extract_type_2_socket_inode(lname, &inode) < 0)
                continue;

(1) `memcpy(line + procfdlen - PATH_FD_SUFFl, PATH_FD_SUFF "/",PATH_FD_SUFFl +
1);safe_strncpy(line + procfdlen + 1, direfd->d_name, sizeof(line) - procfdlen
- 1);` 得到遍历之后的fd信息，比如 /proc/pid/fd

(2) `lnamelen = readlink(line, lname, sizeof(lname) - 1);` 得到 fd 所指向的
link，因为通常情况下 fd 一般都是链接，要么是 socket 链接要么是 pipe 链接．如下所示：

    
    
       $ ls -al /proc/1289/fd
       total 0
       dr-x------ 2 username username  0 May 25 15:45 .
       dr-xr-xr-x 9 username username  0 May 25 09:11 ..
       lr-x------ 1 username username 64 May 25 16:23 0 -> 'pipe:[365366]'
       l-wx------ 1 username username 64 May 25 16:23 1 -> 'pipe:[365367]'
       l-wx------ 1 username username 64 May 25 16:23 2 -> 'pipe:[365368]'
       lr-x------ 1 username username 64 May 25 16:23 3 -> /proc/uptime

(3) 通过`extract_type_1_socket_inode`获取到 link 中对应的 inode 编号．

    
    
       #define PRG_SOCKET_PFX    "socket:["
       #define PRG_SOCKET_PFXl (strlen(PRG_SOCKET_PFX))
       static int extract_type_1_socket_inode(const char lname[], unsigned long * inode_p) {
    
       /* If lname is of the form "socket:[12345]", extract the "12345"
          as *inode_p.  Otherwise, return -1 as *inode_p.
          */
       // 判断长度是否小于　strlen(socket:[)+3
       if (strlen(lname) < PRG_SOCKET_PFXl+3) return(-1);
    
       //函数说明：memcmp()用来比较s1 和s2 所指的内存区间前n 个字符。
       ／／　判断lname是否以　socket:[　开头
       if (memcmp(lname, PRG_SOCKET_PFX, PRG_SOCKET_PFXl)) return(-1);
       if (lname[strlen(lname)-1] != ']') return(-1);  {
           char inode_str[strlen(lname + 1)];  /* e.g. "12345" */
           const int inode_str_len = strlen(lname) - PRG_SOCKET_PFXl - 1;
           char *serr;
    
           // 获取到inode的编号
           strncpy(inode_str, lname+PRG_SOCKET_PFXl, inode_str_len);
           inode_str[inode_str_len] = '\0';
           *inode_p = strtoul(inode_str, &serr, 0);
           if (!serr || *serr || *inode_p == ~0)
               return(-1);
       }

(4) 获取程序对应的 cmdline

    
    
       if (!cmdlp) {
           if (procfdlen - PATH_FD_SUFFl + PATH_CMDLINEl >=sizeof(line) - 5)
               continue;
           safe_strncpy(line + procfdlen - PATH_FD_SUFFl, PATH_CMDLINE,sizeof(line) - procfdlen + PATH_FD_SUFFl);
       fd = open(line, O_RDONLY);
       if (fd < 0)
           continue;
       cmdllen = read(fd, cmdlbuf, sizeof(cmdlbuf) - 1);
       if (close(fd))
           continue;
       if (cmdllen == -1)
           continue;
       if (cmdllen < sizeof(cmdlbuf) - 1)
           cmdlbuf[cmdllen]='\0';
       if (cmdlbuf[0] == '/' && (cmdlp = strrchr(cmdlbuf, '/')))
           cmdlp++;
       else
           cmdlp = cmdlbuf;
       }

由于cmdline是可以直接读取的，所以并不需要像读取fd那样借助与readlink()函数，直接通过`read(fd, cmdlbuf,
sizeof(cmdlbuf) - 1)`即可读取文件内容。

(5) `snprintf(finbuf, sizeof(finbuf), "%s/%s", direproc->d_name, cmdlp);` 拼接
pid 和 cmdlp，最终得到的就是类似与 `6017/redis-server *` 这样的效果

(6) 最终程序调用 `prg_cache_add(inode, finbuf, "-");` 将解析得到的inode和finbuf 加入到缓存中.

#### prg_cache_add

    
    
    #define PRG_HASH_SIZE 211
    #define PRG_HASHIT(x) ((x) % PRG_HASH_SIZE)
    static struct prg_node {
        struct prg_node *next;
        unsigned long inode;
        char name[PROGNAME_WIDTH];
        char scon[SELINUX_WIDTH];
    } *prg_hash[　];
    
    static void prg_cache_add(unsigned long inode, char *name, const char *scon)
    {
        unsigned hi = PRG_HASHIT(inode);
        struct prg_node **pnp,*pn;
    
        prg_cache_loaded = 2;
        for (pnp = prg_hash + hi; (pn = *pnp); pnp = &pn->next) {
        if (pn->inode == inode) {
            /* Some warning should be appropriate here
               as we got multiple processes for one i-node */
            return;
        }
        }
        if (!(*pnp = malloc(sizeof(**pnp))))
        return;
        pn = *pnp;
        pn->next = NULL;
        pn->inode = inode;
        safe_strncpy(pn->name, name, sizeof(pn->name));
    
        {
        int len = (strlen(scon) - sizeof(pn->scon)) + 1;
        if (len > 0)
                safe_strncpy(pn->scon, &scon[len + 1], sizeof(pn->scon));
        else
                safe_strncpy(pn->scon, scon, sizeof(pn->scon));
        }
    
    }

  1. `unsigned hi = PRG_HASHIT(inode);` 使用 inode 整除 211 得到作为 hash 值
  2. `for (pnp = prg_hash + hi; (pn = *pnp); pnp = &pn->next)` 由于`prg_hash`是一个链表结构，所以通过 for 循环找到链表的结尾;
  3. `pn = *pnp;pn->next = NULL;pn->inode = inode;safe_strncpy(pn->name, name, sizeof(pn→name));`为新的 inode 赋值并将其加入到链表的末尾;

所以`prg_node`是一个全局变量，是一个链表结果，保存了 inode 编号与`pid/cmdline`之间的对应关系;

#### prg_cache_get

    
    
    static const char *prg_cache_get(unsigned long inode)
    {
        unsigned hi = PRG_HASHIT(inode);
        struct prg_node *pn;
    
        for (pn = prg_hash[hi]; pn; pn = pn->next)
        if (pn->inode == inode)
            return (pn->name);
        return ("-");
    }

分析完毕 prg_cache_add() 之后，看 prg_cache_get() 就很简单了．

  1. `unsigned hi = PRG_HASHIT(inode);` 通过 inode 号拿到 hash 值
  2. `for (pn = prg_hash[hi]; pn; pn = pn->next)` 遍历 prg_hash 链表中的每一个节点，如果遍历的 inode 与目标的 inode 相符就返回对应的信息。

### 总结

通过对 netstat 的一个简单的分析，可以发现其实 netstat 就是通过遍历 /proc
目录下的目录或者是文件来获取对应的信息。如果在一个网络进程频繁关闭打开关闭，那么使用 netstat 显然是相当耗时的。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/934/>

