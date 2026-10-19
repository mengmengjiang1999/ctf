自己来动手实现 Native Hook

[ 红橙Darren](https://www.jianshu.com/u/35083fcb7747)关注赞赏支持

# 自己来动手实现 Native Hook

Native Hook 是我们性能优化中最常见的手段之一，推荐大家用开源的方案像
[xhook](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fiqiyi%2FxHook)
和
[bhook](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fbytedance%2Fbhook)
等等，会用这肯定是最基础的，其次我们一直都追求知道原理并且要自己能写。今天这里我们自己来实现一套简单的 Native Hook
，我们只写关键代码。为了确保大家都能看懂，我们可能需要以下基础知识：

  * 跨 so 的方法调用流程
  * elf 文件格式
  * 基本的 NDK 开发知识

有了以上基础知识，我们实现起来就会变得简单了，虽然过程中可能会遇到一些问题，但前期我们只需要确保流程和方案没问题就行。其实主要就是两步：首先，读取
/proc/self/maps 文件内容，找到目标 so 文件的基地址；最后，解析 elf 找到要 hook 的函数的地址，替换成我们自己指定的函数地址。

### 1\. 读取 /proc/self/maps 文件内容，找到目标 so 文件的基地址

让我们先写代码来看看 /proc/self/maps 的内容

    
    
        // 1. 读取 /proc/self/maps 内容，找到 so 文件路径和基地址
        FILE* maps_fp = fopen("/proc/self/maps", "r");
        if (maps_fp == NULL) {
            LOGE("open /proc/self/maps error");
        }
        char  line[512];
        while (fgets(line, sizeof(line), maps_fp)) {
            LOGE("%s", line);
        }
    
    
    
    ...... 省了很多行打印
    7b86a57000-7b87a57000 rw-p 00000000 00:00 0                              [anon:dalvik-region space live bitmap]
    7b87a57000-7b87b57000 rw-p 00000000 00:00 0                              [anon:dalvik-allocspace zygote / non moving space mark-bitmap 0]
    7b87b57000-7b87c57000 rw-p 00000000 00:00 0                              [anon:dalvik-allocspace zygote / non moving space live-bitmap 0]
    7b87c57000-7b87cc8000 r--p 00000000 fd:05 30703605                       /system/framework/hwperf.jar
    7b87cc8000-7b87f92000 r--p 00000000 fd:05 30540624                       /system/framework/hwframework.jar
    7b87f92000-7b87ff3000 r--p 00000000 fd:05 30704758                       /system/framework/hwPartDeviceVirtualization.jar
    7b87ff3000-7b88150000 r--p 00000000 fd:05 30717667                       /system/framework/hwPartSecurity.jar
    7b88150000-7b88249000 r--p 00000000 fd:05 30699746                       /system/framework/hwPartTelephonyOpt.jar
    7b88249000-7b88598000 r--p 00000000 fd:05 30676807                       /system/framework/hwEmui.jar
    7b88598000-7b8869b000 r--p 00000000 fd:05 36412139                       /system/framework/featurelayer-widget.jar
    7b8869b000-7b889d3000 r--p 00000000 fd:05 32955722                       /system/framework/telephony-common.jar
    7b889d3000-7b88ac1000 r--p 00000000 fd:05 30419804                       /system/framework/ext.jar
    7b88ac1000-7b88cee000 r--p 01c80000 fd:05 38214656                       /system/framework/framework.jar
    7b88cee000-7b896ff000 r--p 01270000 fd:05 38214656                       /system/framework/framework.jar
    7b896ff000-7b8a024000 r--p 0094c000 fd:05 38214656                       /system/framework/framework.jar
    7b8a024000-7b8a971000 r--p 00000000 fd:05 38214656                       /system/framework/framework.jar
    7b8a971000-7b8aa99000 r--p 00000000 07:07 40                             /apex/com.android.runtime/javalib/apache-xml.jar
    7b8aa99000-7b8abef000 r--p 00000000 07:07 41                             /apex/com.android.runtime/javalib/bouncycastle.jar
    7b8abef000-7b8af17000 r--p 00004000 07:07 42                             /apex/com.android.runtime/javalib/core-libart.jar
    7b8af17000-7b8b3d0000 r--p 00000000 07:07 43                             /apex/com.android.runtime/javalib/core-oj.jar
    7b8b3d0000-7b8b50e000 r--p 00000000 07:07 111                            /apex/com.android.runtime/lib64/libart.so
    7b8b50e000-7b8b9c1000 --xp 0013e000 07:07 111                            /apex/com.android.runtime/lib64/libart.so
    7b8b9c1000-7b8b9c4000 rw-p 005f1000 07:07 111                            /apex/com.android.runtime/lib64/libart.so
    7b8b9c4000-7b8b9d5000 r--p 005f4000 07:07 111                            /apex/com.android.runtime/lib64/libart.so
    7b8b9d5000-7b8b9d9000 rw-p 00000000 00:00 0                              [anon:.bss]
    7b8b9dc000-7b8ba00000 r--s 00000000 fd:05 78402939                       /system/usr/hyphen-data/hyph-nb.hyb
    ...... 省了很多行打印
    

通过上面的打印，so 的路径地址我们一眼肯定能看出来，但是哪个是基地址呢？这就得去研究一下了，或者查查资料啥的：

    
    
    起始地址 - 结束地址      属性  偏移　　  设备号 inode号    映射的文件名（详细的描述见下表）
    7b8abef000-7b8af17000 r--p 00004000 07:07 42         /apex/com.android.runtime/javalib/core-libart.jar
    7b8af17000-7b8b3d0000 r--p 00000000 07:07 43         /apex/com.android.runtime/javalib/core-oj.jar
    7b8b3d0000-7b8b50e000 r--p 00000000 07:07 111        /apex/com.android.runtime/lib64/libart.so
    7b8b50e000-7b8b9c1000 --xp 0013e000 07:07 111        /apex/com.android.runtime/lib64/libart.so
    7b8b9c1000-7b8b9c4000 rw-p 005f1000 07:07 111        /apex/com.android.runtime/lib64/libart.so
    7b8b9c4000-7b8b9d5000 r--p 005f4000 07:07 111        /apex/com.android.runtime/lib64/libart.so
    
    
    
    void core_dhook(const char *pathname, uintptr_t base_addr, const char *symbol, void *new_func){
        LOGE("2. 解析 elf 找到要 hook 的函数的地址，替换成我们自己指定的函数地址");
    }
    
    void dhook(const char *pathname_regex_str, const char *symbol, void *new_func)
    {
        // 1. 读取 /proc/self/maps 内容，找到 so 文件路径和基地址
        FILE* maps_fp = fopen("/proc/self/maps", "r");
        if (maps_fp == NULL) {
            LOGE("open /proc/self/maps error");
        }
        char                     line[512];
        char                     permission[5];
        uintptr_t                base_addr;
        unsigned long            offset;
        int                      pathname_pos;
        char                    *pathname;
        size_t                   pathname_len;
        regex_t                  path_name_regex;
    
        regcomp(&path_name_regex, pathname_regex_str, REG_NOSUB);
    
        while (fgets(line, sizeof(line), maps_fp)) {
            if(sscanf(line, "%"PRIxPTR"-%*lx %4s %lx %*x:%*x %*d%n", &base_addr, permission, &offset, &pathname_pos) != 3) continue;
    
            // 异常情况的判断
            if(permission[0] != 'r') continue;
            if(permission[3] != 'p') continue;
            if(0 != offset) continue;
    
            // 空格去掉
            while(isspace(line[pathname_pos]) && pathname_pos < (int)(sizeof(line) - 1))
                pathname_pos += 1;
            if(pathname_pos >= (int)(sizeof(line) - 1)) continue;
    
            // 获取成这样 /system/framework/arm64/boot-core-libart.art\n
            pathname = line + pathname_pos;
            pathname_len = strlen(pathname);
            if(0 == pathname_len) continue;
            // 获取成这样 /system/framework/arm64/boot-core-libart.art
            if(pathname[pathname_len - 1] == '\n')
            {
                pathname[pathname_len - 1] = '\0';
                pathname_len -= 1;
            }
            // 异常情况判断
            if(0 == pathname_len) continue;
            if('[' == pathname[0]) continue;
    
            // 正则匹配
            if(0 == regexec(&path_name_regex, pathname, 0, NULL, 0))
            {
                core_dhook(pathname, base_addr, symbol, new_func);
            }
        }
    }
    

### 2\. 解析 elf 找到要 hook 的函数的地址，替换成指定的函数地址

    
    
    void core_dhook(uintptr_t base_addr, const char *symbol, void *new_func){
        // 2.1. 获取计算 program_header_table 的地址
        ElfW(Ehdr) *elf_header = base_addr;
        ElfW(Phdr) *elf_program_header_table = base_addr + elf_header->e_phoff;
        // 2.2. 遍历 elf_program_header_table
        int program_header_table_length = elf_header->e_phnum;
        uintptr_t dyn_address = 0;
        unsigned int dyn_memory_size = 0;
        for (int i = 0; i < program_header_table_length; ++i) {
            if(elf_program_header_table[i].p_type == PT_DYNAMIC){
                dyn_address = elf_program_header_table[i].p_vaddr + base_addr;
                dyn_memory_size = elf_program_header_table[i].p_memsz;
                break;
            }
        }
        // 2.3 找出 rel.plt 表的位置
        ElfW(Dyn) *elf_dynamic_table = dyn_address;
        int dynamic_count = dyn_memory_size / sizeof(ElfW(Dyn));
        ElfW(Dyn) *elf_dynamic_table_end = elf_dynamic_table + dynamic_count;
        uintptr_t     elf_rel_address;
        uintptr_t     sys_tab_address;
        uintptr_t     str_tab_address;
        unsigned long  elf_rel_size;
    
        for (; elf_dynamic_table < elf_dynamic_table_end; elf_dynamic_table++) {
            switch (elf_dynamic_table->d_tag) {
                case DT_NULL:
                    elf_dynamic_table == elf_dynamic_table_end;
                    break;
                case DT_JMPREL:
                    elf_rel_address = elf_dynamic_table->d_un.d_ptr;
                    break;
                case DT_PLTRELSZ:
                    elf_rel_size = elf_dynamic_table->d_un.d_val / sizeof(ElfW(Rela));
                    break;
                case DT_SYMTAB:
                    sys_tab_address = elf_dynamic_table->d_un.d_ptr;
                    break;
                case DT_STRTAB:
                    str_tab_address = elf_dynamic_table->d_un.d_ptr;
                    break;
            }
        }
        // 2.4 遍历 rel.plt 表，匹配 symbol 只能通过 sys_table -> str_tab
        ElfW(Rela) *elf_rel_table = (elf_rel_address + base_addr);
    
        for (int i = 0; i < elf_rel_size; ++i) {
            int sys_tab_index = ELF_R_SYM(elf_rel_table[i].r_info);
            ElfW(Sym) *sys_table = (sys_tab_index * sizeof(ElfW(Sym)) + sys_tab_address + base_addr);
            char* fun_name = (char *) (sys_table->st_name + str_tab_address + base_addr);
            if (memcmp(fun_name, symbol, strlen(symbol)) == 0) {
                uintptr_t mem_page_start = elf_rel_table[i].r_offset + base_addr;
                // 调整目标内存区域的权限
                mprotect(PAGE_START(mem_page_start), getpagesize(), PROT_READ | PROT_WRITE);
                // 2.5 替换掉地址
                *(void **) (elf_rel_table[i].r_offset + base_addr) = new_func;
                // 清除指令缓存
                __builtin___clear_cache((void *) PAGE_START(mem_page_start), (void *) PAGE_END(mem_page_start));
            }
        }
    }
    

视频链接：[https://pan.baidu.com/s/1O5M7oumrpTVBnda8X88VlQ](https://links.jianshu.com/go?to=https%3A%2F%2Fpan.baidu.com%2Fs%2F1O5M7oumrpTVBnda8X88VlQ)  
视频密码：kdtd

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Android Native Hook 检测](https://www.jianshu.com/p/43fd3997330c)

通用Android Native Hook 检测 前言 Hook技术运用很广泛，从应用安全角度来看，Hook也是动...

[老江_](https://www.jianshu.com/u/2c9403bd4d52)阅读 1,749评论 0赞 1

  * [Android中so文件的Hook](https://www.jianshu.com/p/dcb8f6b93ef9)

1\. 背景 在我们的日常工作中经常会遇到一些BUG，而且这些BUG发生在native层，也就是在我们的so共...

[2baf611355d8](https://www.jianshu.com/u/2baf611355d8)阅读 15,936评论 3赞 41

  * [论ART上运行时 Method AOP实现](https://www.jianshu.com/p/820eceabf219)

两年前阿里开源了Dexposed 项目，它能够在Dalvik上无侵入地实现运行时方法拦截，正如其介绍「enable...

[weishu](https://www.jianshu.com/u/e347b97e2f0c)阅读 4,297评论 3赞 42

  * [Android远程调试的探索与实现](https://www.jianshu.com/p/bda6366a6a24)

文章来源：美团点评技术团队 作为移动开发者，最头疼的莫过于遇到产品上线以后出现了bug，但是本地开发环境又无法复现...

[程序农猿](https://www.jianshu.com/u/c7ee28477e33)阅读 1,361评论 3赞 2

  * [黑客赚钱的路子有多野？CTF逆向入门指南](https://www.jianshu.com/p/75e76a734c00)

1、背景 在CTF比赛中, CTF逆向题目除了需要分析程序工作原理, 还要根据分析结果进一步求出FLAG。逆向在解...

[代码熬夜敲666](https://www.jianshu.com/u/6b3b034eacac)阅读 604评论 0赞 1

 