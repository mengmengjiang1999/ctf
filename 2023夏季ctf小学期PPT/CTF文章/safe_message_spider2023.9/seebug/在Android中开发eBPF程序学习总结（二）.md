**作者：Hcamael@知道创宇404实验室  
日期：2022年11月16日  
相关阅读：  
[在 Android 中开发 eBPF 程序学习总结（一）](https://paper.seebug.org/2003/ "在 Android 中开发
eBPF 程序学习总结（一）")**

在上一章的基础上深入研究

在上一篇文章中，我自己改了一版BPF程序的代码`bpftest.c`，代码也在上一篇文章中放出来了，但是一个完整的BPF程序，还需要一个用户态的loader，也就是需要有一个读取BPF程序给我们数据的程序。

之前也说了，可以使用MAP来进行数据交互，在`bpftest.c`代码中`bpf_execve_map_update_elem(&key, &event,
BPF_ANY);`，把`event`结构体更新到key=1的map中，也就是说，把每个进行`syscall`调用的程序的pid，gid，还有程序名，更新到MAP中。所以我们需要一个loader，来读取MAP，从而得到这些信息。

最开始，loader我使用的是android
demo代码中的那个，但是在使用中发现，没办法读取结构体的值，也搜不到相关文章，能搜到示例代码的value类型都是整型，并且我对android开发也不是很熟悉，所以考虑用C自己写一个。

通过strace抓取之前这个loader的系统调用：

    
    
    bpf(BPF_OBJ_GET, {pathname="/sys/fs/bpf/prog_bpftest_tracepoint_raw_syscalls_sys_enter", bpf_fd=0, file_flags=0}, 120) = 3
    openat(AT_FDCWD, "/sys/kernel/tracing/events/raw_syscalls/sys_enter/id", O_RDONLY|O_CLOEXEC) = 4
    read(4, "21\n", 4096)                   = 3
    close(4)                                = 0
    perf_event_open({type=PERF_TYPE_TRACEPOINT, size=0, config=21, ...}, -1, 0, -1, PERF_FLAG_FD_CLOEXEC) = 4
    ioctl(4, PERF_EVENT_IOC_SET_BPF, 3)     = 0
    ioctl(4, PERF_EVENT_IOC_ENABLE, 0)      = 0
    nanosleep({tv_sec=1, tv_nsec=0}, 0x7ff104b788) = 0
    bpf(BPF_OBJ_GET, {pathname="/sys/fs/bpf/map_bpftest_execve_map", bpf_fd=0, file_flags=0}, 120) = 5
    nanosleep({tv_sec=0, tv_nsec=40000000}, NULL) = 0
    bpf(BPF_MAP_LOOKUP_ELEM, {map_fd=5, key=0x7ff104b5f4, value=0x7ff104b5e8}, 120) = 0

通过上面的系统调用，我们就能理清楚，loader程序到底做了哪些工作。

接着我找到了Linux内核中的一个bpf_load.c，参考了一下在普通的Linux系统中，loader是怎么处理的，所以我对该程序进行了修改，增加了以下代码：

    
    
    struct androidBPF {
        char *prog_path;
        char *map_path;
        char *tp_category;
        char *tp_name;
    };
    
    
    static int load_prog(char *prog_path)
    {
        int pfd;
        pfd = bpf_obj_get(prog_path);
        if (pfd < 0) {
            printf("bpf_prog_load() err=%d\n%s", errno, prog_path);
            return -1;
        }
    
        return pfd;
    }
    
    int attach_tracepoint(char *tp_category, char *tp_name)
    {
        char buf[256];
        int efd, err, id;
        struct perf_event_attr attr = {};
        attr.type = PERF_TYPE_TRACEPOINT;
        attr.sample_type = PERF_SAMPLE_RAW;
        attr.sample_period = 1;
        attr.wakeup_events = 1;
    
        strcpy(buf, DEBUGFS);
        strcat(buf, "events/");
        strcat(buf, tp_category);
        strcat(buf, "/");
        strcat(buf, tp_name);
        strcat(buf, "/id");
        efd = open(buf, O_RDONLY, 0);
        if (efd < 0) {
            printf("failed to open %s\n", buf);
            return -1;
        }
        err = read(efd, buf, sizeof(buf));
        if (err < 0 || err >= sizeof(buf)) {
            printf("read from failed '%s'\n", strerror(errno));
            return -1;
        }
        close(efd);
        buf[err] = 0;
        id = atoi(buf);
        attr.config = id;
        efd = perf_event_open(&attr, -1/*pid*/, 0/*cpu*/, -1/*group_fd*/, 0);
        if (efd < 0) {
            printf("event %d fd %d err %s\n", id, efd, strerror(errno));
            return -1;
        }
        return efd;
    }
    
    static int load_map(char *map_path)
    {
        int mfd;
        mfd = bpf_obj_get(map_path);
        if (mfd < 0) {
            printf("bpf_map_load() err=%d\n%s", errno, map_path);
            return -1;
        }
    
        return mfd;
    }
    
    int get_map_by_int_key(int *key, void *value)
    {
        int mfd, ret;
    
        mfd = map_fd[prog_cnt-1];
        ret = bpf_lookup_elem(mfd, key, value);
        return ret;
    }
    
    int load_bpf_from_fs(struct androidBPF *abpf)
    {
        int fd, efd, mfd;
        fd = load_prog(abpf->prog_path);
        if (fd <= 0) {
            printf("[debug] load prog error.\n");
            return fd;
        }
        prog_fd[prog_cnt] = fd;
        efd = attach_tracepoint(abpf->tp_category, abpf->tp_name);
        if (efd <= 0) {
            printf("[debug] attach_tracepoint error.\n");
            return efd;
        }
        event_fd[prog_cnt] = efd;
        ioctl(efd, PERF_EVENT_IOC_ENABLE, 0);
        ioctl(efd, PERF_EVENT_IOC_SET_BPF, fd);
        printf("[debug] load bpf prog success.\n");
        mfd = load_map(abpf->map_path);
        if (mfd <= 0) {
            printf("[debug] load_map error.\n");
            return mfd;
        }
        map_fd[prog_cnt++] = mfd;
        return 0;
    }
    
    void read_trace_pipe(int times)
    {
        int trace_fd;
        trace_fd = open(DEBUGFS "trace_pipe", O_RDONLY, 0);
        if (trace_fd < 0)
            return;
        // times = 0, loop 0xffffffff
        do {
            static char buf[4096];
            ssize_t sz;
            sz = read(trace_fd, buf, sizeof(buf) - 1);
            if (sz > 0) {
                buf[sz] = 0;
                puts(buf);
            }
        } while (--times);
    }

接着，我就能使用C代码来写loader了：

    
    
    #include "bpf_load.h"
    #include <stdio.h>
    #include <string.h>
    int main(int argc, char **argv) {
      struct androidBPF abpf = {0, };
        if (argc < 3)
            return 0;
      abpf.prog_path = argv[1];
      abpf.map_path = argv[2];
      abpf.tp_category = "raw_syscalls";
      abpf.tp_name = "sys_enter";
      if (load_bpf_from_fs(&abpf) != 0) { // 用于加载 ELF 格式的 BPF 程序
        printf("The kernel didn't load the BPF program\n");
        return -1;
      }
      int key, ret;
      key = 1;
      struct event_execv value;
      for (int i = 0; i < 10; i ++) {
        memset(&value, 0, sizeof(value));
        ret = get_map_by_int_key(&key, &value);
        printf("[debug] ret = %d, pid = %d, gid = %d, comm = %s\n", ret, value.pid, value.gid, value.cmd);
      }
      // for (int i=0; i < 88; i++)
      // {
      //   printf("debug value[%d] = 0x%x\n", i, *((char *)&value+i));
      // }
      read_trace_pipe(1);
      return 0;
    }

在本地的arm64机器上就能编译了：

    
    
    $ ls -alF
    total 916
    drwxr-xr-x 1 hehe hehe    320 Oct 31 11:54 ./
    drwxr-xr-x 1 hehe hehe    416 Oct 30 22:34 ../
    -rw-rw-r-- 1 hehe hehe   4025 Oct 30 22:37 bpf_helpers.h
    -rw-rw-r-- 1 hehe hehe  10940 Oct 31 11:35 bpf_load.c
    -rw-rw-r-- 1 hehe hehe   1112 Oct 31 11:35 bpf_load.h
    -rw-rw-r-- 1 hehe hehe   3432 Oct 30 22:49 libbpf.c
    -rw-rw-r-- 1 hehe hehe   5294 Oct 30 22:50 libbpf.h
    -rw-r--r-- 1 hehe hehe 117176 Oct 30 22:54 libelf.so
    -rwxrwxr-x 1 hehe hehe 773016 Oct 31 11:54 loader*
    -rw-rw-r-- 1 hehe hehe    868 Oct 31 11:54 loader.c
    $ clang loader.c bpf_load.c libbpf.c -lelf -lz -o loader -static

上面的loader只简单实现了一下读取map的操作，进阶的玩法还可以更新map的数据，比如我只想监控`curl`程序，那么可以把`111=>curl`写入map当中，然后在BPF程序中，从`map[111]`获取value，只有当`comm
== map[111]`的情况下，才把信息写入map当中。

我们重新再来理解一下loader的操作：

  1. BPF_OBJ_GET prog_bpftest_tracepoint_raw_syscalls_sys_enter，获取prog对象
  2. 读取SEC定义的section的id，从`/sys/kernel/tracing/events/raw_syscalls/sys_enter/id`获取
  3. perf_event_open打开相应时间，因为是tracepoint，所以type要设置为PERF_TYPE_TRACEPOINT，config等于上面获取id
  4. 打开事件后，获取了一个文件描述符，对该文件描述符进行ioctl操作，操作的命令有两个，`PERF_EVENT_IOC_SET_BPF`和`PERF_EVENT_IOC_ENABLE`，PERF_EVENT_IOC_SET_BPF设置为prog对象的文件描述符

到这里为止，表示激活了你想调用的BPF程序了，要不然默认情况下BPF都处于未激活状态。

接下来就是对map的操作：

  1. BPF_OBJ_GET /sys/fs/bpf/map_bpftest_execve_map，获取map对象。
  2. BPF_MAP_LOOKUP_ELEM {map_fd=5, key=0x7ff104b5f4, value=0x7ff104b5e8}，从map_fd中搜索key对应的value，储存在value的指针中返回。

目前这块的资料太少了，只能通过一些demo和源码来进行研究，下一篇将会研究uprobe的用法。

# 参考

  1. <https://elixir.bootlin.com/linux/v4.14.2/source/samples/bpf/bpf_load.c>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2009/>

