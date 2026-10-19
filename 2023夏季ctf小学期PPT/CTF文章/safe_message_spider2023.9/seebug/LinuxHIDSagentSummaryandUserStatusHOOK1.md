**Author: u2400@Knownsec 404 Team  
Chinese version: <https://paper.seebug.org/1102/> **

Foreword: Recently, I have implemented HIDS agent in linux. When searching for
data, I found that although there are a lot of data, each article has its own
focus, and few of them are progressive and comprehensive Chinese articles, I
have stepped on a lot of holes in the step-by-step learning. Here I will take
the process information collection as the entry point to give a detailed
explanation on how to implement a HIDS agent. I hope it will be helpful to all
the Masters.

# 1\. What is HIDS?

Host intrusion detection usually divided into two parts: agent and server.

The agent is responsible for collecting information, sorting out relevant
information and sending it to the server.

Server is usually used as an information center to deploy rules written by
security personnel (currently, HIDS rules do not have a specification written
), collect data obtained from various security components (such as waf and
NIDS), analyze the data, and determine whether host behavior is abnormal based
on rules, and alarms and prompts the abnormal behaviors of the host.

The purpose of the existence of HIDS is that the administrator will not be
disturbed by security events when managing a large number of IDCs, and the
health status of each host can be monitored through the information center.

Relevant open-source projects include OSSEC, OSquery, etc. OSSEC is a well-built HIDS with agent and server, built-in rules, and basic rootkit detection,
sensitive file modification reminders and other functions are included in an
open source project called wazuh. OSquery is an open source project developed
by facebook, which can be used as an agent to collect host-related data,
however, the server and rules need to be implemented by themselves.

Each company's HIDS agent will be customized according to its own needs, more
or less adding some personalized functions, a basic HIDS agent generally needs
to achieve:

  * Collect process information
  * Collect network information
  * Periodic collection open port
  * Monitoring sensitive file modifications

The following section will start with the implementation of an agent, and
discuss how to implement the process information collection module of a HIDS
agent around the agent.

# 2\. Agent Process Monitoring Module Summary

## 2.1 The Purpose of Process Monitoring

In the Linux operating system, almost all operations and intrusion behaviors
are reflected in the executed commands, and the essence of command execution
is to start the process, therefore, the monitoring of processes is the
monitoring of command execution, which is of great help to the operation
upgrade and intrusion behavior analysis.

## 2.2 The Data That The Process Monitoring Module Should Obtain

Now that you want to obtain information, you need to make it clear what you
need first. If you don't know what information you need, then there is no way
to realize it, even if you try hard to implement a HIDS that can obtain basic
information such as pid, the interface will be changed frequently due to lack
of planning in the later stage, which will waste manpower, here, refer to the
《Internet Enterprise Security Advanced Guide》 to provide a basic list of
information acquisition. The method of obtaining this table will be
supplemented later.

Data name | Meaning  
---|---  
path | The path of the executable file  
ppath | Parent process executable file path  
ENV | Environment variables  
cmdline | Process start Command  
pcmdline | Parent process startup command  
pid | Process id  
ppid | Parent process id  
pgid | Process Group id  
sid | Process session id  
uid | Uid of the user who started the process  
euid | The euid of the user who started the process  
gid | User group id of the user who started the process  
egid | The egid of the user who started the process  
mode | Executable file permissions  
owner_uid | The uid of the file owner  
owner_gid | The gid of the file owner  
create_time | File creation time  
modify_time | Last file modification time  
pstart_time | The start time of the process  
prun_time | The time when the parent process has been running  
sys_time | Current system time  
fd | File descriptor  
  
## 2.3 The Method of Process Monitoring

Process Monitoring usually uses hook technology, and these hooks are roughly
divided into two types:

  * Application-level (working in r3, it is common to hijack the libc Library, which is usually simple but may be bypassed.
  * Kernel-level (working in r0 or r1, kernel-level hook is usually related to the system call VFS, which is complex, and may cause compatibility problems between different kernel versions, when a serious error occurs on the hook, kenrel may panic and cannot be bypassed in principle.

Let's start with a simple application-level hook.

# 3\. HIDS Application-level Hook

## 3.1 Hijack libc Library

Libraries are used to package functions. The packaged functions can be used
directly. linux is divided into static libraries and dynamic libraries.
Dynamic libraries are loaded only when applications are loaded, however, the
program has a loading order for the dynamic library, which can be modified
/etc/ld.so.preload To manually load a dynamic link library first, in which the
original function can be replaced before the program calls the original
function, after executing its own logic in its own function, call the original
function to return the result that the original function should return.

For those who want to know more, please refer to this
[article](https://www.ibm.com/developerworks/cn/linux/l-dynamic-libraries/index.html).

To hijack the libc library, you can perform the following steps:

### 3.1.1 Compile a Dynamic Link Library

A simple dynamic link library of hook execve is as follows.

The logic is very simple

  1. Customize a function named execve, and accept the same parameter type as the original execve.
  2. Execute your own logic

    
    
    #define _GNU_SOURCE
    #include <unistd.h>
    #include <dlfcn.h>
    typedef ssize_t (*execve_func_t)(const char* filename, char* const argv[], char* const envp[]);
    static execve_func_t old_execve = NULL;
    int execve(const char* filename, char* const argv[], char* const envp[]) {
            //从这里开始是自己的逻辑, 即进程调用execve函数时你要做什么
        printf("Running hook\n");
        //下面是寻找和调用原本的execve函数, 并返回调用结果
        old_execve = dlsym(RTLD_NEXT, "execve");
        return old_execve(filename, argv, envp);
    }

Compile into so file through gcc.

    
    
    gcc -shared -fPIC -o libmodule.so module.c

### 3.1.2 Modify ld. so. preload

Ld. so. preload is the configuration file of the LD_PRELOAD environment
variable. By modifying the file content to the specified dynamic link library
file path,

Be careful, only root can modify ld. so. preload, unless the default
permission is changed

Customize an execve function as follows:

    
    
    extern char **environ;
    int execve(const char* filename, char* const argv[], char* const envp[]) {
        for (int i = 0; *(environ + i) ; i++)
        {
            printf("%s\n", *(environ + i));
        }
        printf("PID:%d\n", getpid());
        old_execve = dlsym(RTLD_NEXT, "execve");
        return old_execve(filename, argv, envp);
    }

The Pid of the current process and all environment variables can be output.
After compilation, modify ld. so. preload and restart the shell. The result of
running the ls command is as follows:

![image.png](https://images.seebug.org/content/images/2019/12/27/1577418066000-1mwjbg.png-w331s)

### 3.1.3 Advantages and Disadvantages of libc hook

Advantages: it has better performance and is relatively stable. Compared with
LKM, it is simpler and more adaptable. It is usually against web intrusion.

Disadvantages: there is no way out for the static compilation program, and
there is a risk of being bypassed.

### 3.1.4 Hook and Information Acquisition

A hook is set up to establish monitoring points and obtain process-related
information. However, if the hook part is written too much, it will affect the
operation efficiency of normal services, this is unacceptable to the business.
In general HIDS, the information that can not be obtained at the hook is
obtained in the agent, so that the information acquisition and the business
logic are executed concurrently, reduce the impact on the business.

# 4\. Information Completion and Acquisition

If the information accuracy requirement is not very high, and you want to do
everything possible without affecting the normal business deployed on the HIDS
host, you can choose hook to obtain only the necessary data such as PID and
environment variables, then, these things are handed over to the agent, and
the agent continues to obtain other relevant information of the process. That
is to say, when obtaining other information of the process, the process has
already continued to run, instead of waiting for the agent to obtain the
complete information table.

## /proc/[pid]/stat

/Proc is a set of fifo interfaces provided by the kernel to the user state,
calling interfaces in the form of pseudo file directories

The information related to each process is placed in a folder named pid.
Commands such as ps also obtain the information related to the process by
traversing the/proc directory.

The contents of a stat file are as follows. The following self is an interface
provided by the/proc directory to quickly view its own process information.
Each process will see its own information when accessing/self.

    
    
    #cat /proc/self/stat
    3119 (cat) R 29973 3119 19885 34821 3119 4194304 107 0 0 0 0 0 0 0 20 0 1 0 5794695 5562368 176 18446744073709551615 94309027168256 94309027193225 140731267701520 0 0 0 0 0 0 0 0 0 17 0 0 0 0 0 0 94309027212368 94309027213920 94309053399040 140731267704821 140731267704841 140731267704841 140731267706859 0

You will find that the data is messy. Spaces are used as the boundaries of
each data. There is no place to explain what the data means.

Generally, I found a list in an article, which describes the data type of each
data and the meaning of its expression. See the article in [Appendix 1].

Finally, a structure with 52 data items and different types of each data item
was sorted out. It was a little troublesome to get it. No wheel was found on
the Internet, so I wrote one myself.

Specific structure definition:

    
    
    struct proc_stat {
        int pid; //process ID.
        char* comm; //可执行文件名称, 会用()包围
        char state; //进程状态
        int ppid;   //父进程pid
        int pgid;
        int session;    //sid
        int tty_nr;     
        int tpgid;
        unsigned int flags;
        long unsigned int minflt;
        long unsigned int cminflt;
        long unsigned int majflt;
        long unsigned int cmajflt;
        long unsigned int utime;
        long unsigned int stime;
        long int cutime;
        long int cstime;
        long int priority;
        long int nice;
        long int num_threads;
        long int itrealvalue;
        long long unsigned int starttime;
        long unsigned int vsize;
        long int rss;
        long unsigned int rsslim;
        long unsigned int startcode;
        long unsigned int endcode;
        long unsigned int startstack;
        long unsigned int kstkesp;
        long unsigned int kstkeip;
        long unsigned int signal;   //The bitmap of pending signals
        long unsigned int blocked;
        long unsigned int sigignore;
        long unsigned int sigcatch;
        long unsigned int wchan;
        long unsigned int nswap;
        long unsigned int cnswap;
        int exit_signal;
        int processor;
        unsigned int rt_priority;
        unsigned int policy;
        long long unsigned int delayacct_blkio_ticks;
        long unsigned int guest_time;
        long int cguest_time;
        long unsigned int start_data;   
        long unsigned int end_data;
        long unsigned int start_brk;    
        long unsigned int arg_start;    //参数起始地址
        long unsigned int arg_end;      //参数结束地址
        long unsigned int env_start;    //环境变量在内存中的起始地址
        long unsigned int env_end;      //环境变量的结束地址
        int exit_code; //退出状态码
    };

Read from the file and format it as a structure:

    
    
    struct proc_stat get_proc_stat(int Pid) {
        FILE *f = NULL;
        struct proc_stat stat = {0};
        char tmp[100] = "0";
        stat.comm = tmp;
        char stat_path[20];
        char* pstat_path = stat_path;
    
        if (Pid != -1) {
            sprintf(stat_path, "/proc/%d/stat", Pid);
        } else {
            pstat_path = "/proc/self/stat";
        }
    
        if ((f = fopen(pstat_path, "r")) == NULL) {
            printf("open file error");
            return stat;
        }
    
        fscanf(f, "%d ", &stat.pid);
        fscanf(f, "(%100s ", stat.comm);
        tmp[strlen(tmp)-1] = '\0';
        fscanf(f, "%c ", &stat.state);
        fscanf(f, "%d ", &stat.ppid);
        fscanf(f, "%d ", &stat.pgid);
    
        fscanf (
                f,
                "%d %d %d %u %lu %lu %lu %lu %lu %lu %ld %ld %ld %ld %ld %ld %llu %lu %ld %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %d %d %u %u %llu %lu %ld %lu %lu %lu %lu %lu %lu %lu %d",
                &stat.session, &stat.tty_nr, &stat.tpgid, &stat.flags, &stat.minflt,
                &stat.cminflt, &stat.majflt, &stat.cmajflt, &stat.utime, &stat.stime,
                &stat.cutime, &stat.cstime, &stat.priority, &stat.nice, &stat.num_threads,
                &stat.itrealvalue, &stat.starttime, &stat.vsize, &stat.rss, &stat.rsslim,
                &stat.startcode, &stat.endcode, &stat.startstack, &stat.kstkesp, &stat.kstkeip,
                &stat.signal, &stat.blocked, &stat.sigignore, &stat.sigcatch, &stat.wchan,
                &stat.nswap, &stat.cnswap, &stat.exit_signal, &stat.processor, &stat.rt_priority,
                &stat.policy, &stat.delayacct_blkio_ticks, &stat.guest_time, &stat.cguest_time, &stat.start_data,
                &stat.end_data, &stat.start_brk, &stat.arg_start, &stat.arg_end, &stat.env_start,
                &stat.env_end, &stat.exit_code
        );
        fclose(f);
        return stat;
    }

Compared with the data we need to obtain, we can obtain the following data

ppid | Parent process id  
---|---  
pgid | Process Group id  
sid | Process session id  
start_time | The start time of the parent process.  
run_time | The time when the parent process has been running.  
  
## /proc/[pid]/exe

Obtain the path of the executable file through/proc/[pid]/exe, here
/Proc/[pid]/exe is a soft link pointing to an executable file, so the readlink
function is used to obtain the address pointed to by the soft link.

Note that if the file read by readlink has been deleted, one more file name
will be read. `(deleted)` However, the agent cannot delete the corresponding
string at the end of the file blindly. Therefore, you must pay attention to
this situation when writing server rules.

    
    
    char *get_proc_path(int Pid) {
        char stat_path[20];
        char* pstat_path = stat_path;
        char dir[PATH_MAX] = {0};
        char* pdir = dir;
        if (Pid != -1) {
            sprintf(stat_path, "/proc/%d/exe", Pid);
        } else {
            pstat_path = "/proc/self/exe";
        }
    
        readlink(pstat_path, dir, PATH_MAX);
        return pdir;
    }

## /proc/[pid]/cmdline

Obtain the startup command of the process startup, which can be obtained by
obtaining the content of/proc/[pid]/cmdline. There are two pits in this
acquisition.

  1. Because the length of the startup command is uncertain, to avoid overflow, you need to obtain the length first, apply for heap space with MPRI, and then read the data into the variable.
  2. All spaces and press enter in the/proc/self/cmdline file become `'\0'`?I don't know why, so I need to manually change, and several connected spaces will only become one `'\0'`?.

The method of obtaining the length here is stupid, but using fseek to directly
move the file pointer to the end of the file returns 0 each time. I don't know
what to do, so I can only do this first.

    
    
    long get_file_length(FILE* f) {
        fseek(f,0L,SEEK_SET);
        char ch;
        ch = (char)getc(f);
        long i;
        for (i = 0;ch != EOF; i++ ) {
            ch = (char)getc(f);
        }
        i++;
        fseek(f,0L,SEEK_SET);
        return i;
    }

Obtain the content of cmdline

    
    
    char* get_proc_cmdline(int Pid) {
        FILE* f;
        char stat_path[100] = {0};
        char* pstat_path = stat_path;
    
        if (Pid != -1) {
            sprintf(stat_path, "/proc/%d/cmdline", Pid);
        } else {
            pstat_path = "/proc/self/cmdline";
        }
    
        if ((f = fopen(pstat_path, "r")) == NULL) {
            printf("open file error");
            return "";
        }
        char* pcmdline = (char *)malloc((size_t)get_file_length(f));
        char ch;
        ch = (char)getc(f);
        for (int i = 0;ch != EOF; i++ ) {
            *(pcmdline + i) = ch;
            ch = (char)getc(f);
            if ((int)ch == 0) {
                ch = ' ';
            }
        }
        return pcmdline;
    }

# Summary

What is written here is only one of the most common and simple application-level hook methods. The specific implementation and code have been put in
[github](https://github.com/u2400/libc_hook_demo). At the same time, the code
on github is updated. The next article will share how to use LKM to modify
sys_call_table to hook system calls to implement HIDS hook.

# Reference articles

<https://www.freebuf.com/articles/system/54263.html>
<http://abcdefghijklmnopqrst.xyz/2018/07/30/Linux_INT80/>
<https://cloud.tencent.com/developer/news/337625>
<https://github.com/g0dA/linuxStack/blob/master/%E8%BF%9B%E7%A8%8B%E9%9A%90%E8%97%8F%E6%8A%80%E6%9C%AF%E7%9A%84%E6%94%BB%E4%B8%8E%E9%98%B2-%E6%94%BB%E7%AF%87.md>

# Appendix 1

Here is a complete description of the specific meaning of each file in
the/proc directory. <http://man7.org/linux/man-pages/man5/proc.5.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1104/>

