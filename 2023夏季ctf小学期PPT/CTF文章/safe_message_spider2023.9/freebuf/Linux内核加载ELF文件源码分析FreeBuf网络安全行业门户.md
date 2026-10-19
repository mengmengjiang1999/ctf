# 一、源码版本

1）版本：V6.3-rc7,x86  
2）elf文件加载源码：fs/binfmt_elf.c

# 二、Linux可执行文件注册

Linux支持多种不同格式的可执行程序，这些可执行 程序的加载方式由linux\binfmts.h文件中的linux_binfmt结构体进行定义：

    
    
    struct linux_binfmt {
        struct list_head lh;
        struct module *module;
        int (*load_binary)(struct linux_binprm *);
        int (*load_shlib)(struct file *);
    #ifdef CONFIG_COREDUMP
        int (*core_dump)(struct coredump_params *cprm);
        unsigned long min_coredump;   /* minimal dump size */
    #endif
    } __randomize_layout;
    

结构体定义了可执行程序的3中不同的加载模式：

加载模式| 备注  
---|---  
load_binary| 读取可执行文件内容并加载当前进程建立新的执行环境  
load_shlib| 动态加载共享库到已有进程  
core_dump| 存放当前进程的执行上下文到core文件中  
  
每一种系统支持的可执行文件都对应一个linux_binfmt对象，统一注册在一个链表中，通过register_binfmt和unregister_binfmt函数编辑链表。在执行可执行程序时，内核通过list_for_each_enrty遍历链表中注册的linux_binfmt对象，使用正确的加载方式进行加载。  
elf文件的linux_binfmt对象结构如下，该结构体定义了elf文件由load_elf_binary函数加载：

    
    
    static struct linux_binfmt elf_format = {
        .module     = THIS_MODULE,
        .load_binary    = load_elf_binary,
        .load_shlib = load_elf_library,
    #ifdef CONFIG_COREDUMP
        .core_dump  = elf_core_dump,
        .min_coredump   = ELF_EXEC_PAGESIZE,
    #endif
    };
    

# 三、load_elf_binary函数分析

## 1、文件格式校验

    
    
    struct elfhdr *elf_ex = (struct elfhdr *)bprm->buf;
     
    retval = -ENOEXEC;
    /* First of all, some simple consistency checks */
    if (memcmp(elf_ex->e_ident, ELFMAG, SELFMAG) != 0)
        goto out;
     
        if (elf_ex->e_type != ET_EXEC && elf_ex->e_type != ET_DYN)
            goto out;
        if (!elf_check_arch(elf_ex))
            goto out;
        if (elf_check_fdpic(elf_ex))
            goto out;
        if (!bprm->file->f_op->mmap)
            goto out;
    
    

程序首先读取了e_ident中的魔数并进行了校验，elf_ident是ELF文件最头部的一个长度为16字节的数组，不区分架构和系统位数。e_ident起始的4个字节固定为\0x7fELF，通过校验该位可以确定是否为elf文件。  
然后识别文件是否为可执行文件或动态链接文件，ELF文件当前主要有4种格式，分别为可重定位文件(ET_REL)、可执行文件(ET_EXEC)、共享目标文件(ET_DYN)和core文件(ET_CORE)。load_elf_binary函数只负责解析exec和dyn文件。  
最后还解析了文件依赖的系统架构等必要项。

## 2、读取程序头

    
    
    static struct elf_phdr *load_elf_phdrs(const struct elfhdr *elf_ex,
                           struct file *elf_file)
    {
        struct elf_phdr *elf_phdata = NULL;
        int retval = -1;
        unsigned int size;
     
        /*
         * If the size of this structure has changed, then punt, since
         * we will be doing the wrong thing.
         */
        if (elf_ex->e_phentsize != sizeof(struct elf_phdr))
            goto out;
     
        /* Sanity check the number of program headers... */
        /* ...and their total size. */
        size = sizeof(struct elf_phdr) * elf_ex->e_phnum;
        if (size == 0 || size > 65536 || size > ELF_MIN_ALIGN)
            goto out;
     
        elf_phdata = kmalloc(size, GFP_KERNEL);
        if (!elf_phdata)
            goto out;
     
        /* Read in the program headers */
        retval = elf_read(elf_file, elf_phdata, size, elf_ex->e_phoff);
     
    out:
        if (retval) {
            kfree(elf_phdata);
            elf_phdata = NULL;
        }
        return elf_phdata;
    }
    

程序头是描述与程序执行直接相关的目标文件结构信息，用于在文件中定位各个段的映像，同时包含其他一些用来为程序创建进程映像所必须的信息。

## 3、读取解释器段

    
    
    elf_ppnt = elf_phdata;
        for (i = 0; i < elf_ex->e_phnum; i++, elf_ppnt++) {
            char *elf_interpreter;
     
            if (elf_ppnt->p_type == PT_GNU_PROPERTY) {
                elf_property_phdata = elf_ppnt;
                continue;
            }
     
            if (elf_ppnt->p_type != PT_INTERP)
                continue;
     
            /*
             * This is the program interpreter used for shared libraries -             * for now assume that this is an a.out format binary.
             */
            retval = -ENOEXEC;
            if (elf_ppnt->p_filesz > PATH_MAX || elf_ppnt->p_filesz < 2)
                goto out_free_ph;
     
            retval = -ENOMEM;
            elf_interpreter = kmalloc(elf_ppnt->p_filesz, GFP_KERNEL);
            if (!elf_interpreter)
                goto out_free_ph;
     
            retval = elf_read(bprm->file, elf_interpreter, elf_ppnt->p_filesz,
                      elf_ppnt->p_offset);
            if (retval < 0)
                goto out_free_interp;
            /* make sure path is NULL terminated */
            retval = -ENOEXEC;
            if (elf_interpreter[elf_ppnt->p_filesz - 1] != '\0')
                goto out_free_interp;
     
            interpreter = open_exec(elf_interpreter);
            kfree(elf_interpreter);
            retval = PTR_ERR(interpreter);
            if (IS_ERR(interpreter))
                goto out_free_ph;
     
            /*
             * If the binary is not readable then enforce mm->dumpable = 0
             * regardless of the interpreter's permissions.
             */
            would_dump(bprm, interpreter);
     
            interp_elf_ex = kmalloc(sizeof(*interp_elf_ex), GFP_KERNEL);
            if (!interp_elf_ex) {
                retval = -ENOMEM;
                goto out_free_file;
            }
     
            /* Get the exec headers */
            retval = elf_read(interpreter, interp_elf_ex,
                      sizeof(*interp_elf_ex), 0);
            if (retval < 0)
                goto out_free_dentry;
     
            break;
     
    out_free_interp:
            kfree(elf_interpreter);
            goto out_free_ph;
        }
    
    

如果程序需要动态链接，则需要加载解释器段(PT_INTERP)，程序遍历所有的程序头，识别到解释器段后，读取该段的内容。解释器段实际上是标明解释器程序文件路径的字符串，内核根据字符串指向的文件，使用open_exec函数打开解释器。

## 4、栈可执行属性及其他定制信息获取

    
    
    elf_ppnt = elf_phdata;
        for (i = 0; i < elf_ex->e_phnum; i++, elf_ppnt++)
            switch (elf_ppnt->p_type) {
            case PT_GNU_STACK:
                if (elf_ppnt->p_flags & PF_X)
                    executable_stack = EXSTACK_ENABLE_X;
                else
                    executable_stack = EXSTACK_DISABLE_X;
                break;
     
            case PT_LOPROC ... PT_HIPROC:
                retval = arch_elf_pt_proc(elf_ex, elf_ppnt,
                              bprm->file, false,
                              &arch_state);
                if (retval)
                    goto out_free_dentry;
                break;
            }
    
    

同样通过for循环遍历，如果识别到栈属性段(PT_GNU_STACK)，根据程序头中的p_flags标志位判定栈的可执行属性。如果识别到处理器专用语义段(PT_LOPROC至PT_HIPROC之间)，则调用arch_elf_pt_proc函数完成相应的配置。

## 5、读取解释器

    
    
    if (interpreter) {
            retval = -ELIBBAD;
            /* Not an ELF interpreter */
            if (memcmp(interp_elf_ex->e_ident, ELFMAG, SELFMAG) != 0)
                goto out_free_dentry;
            /* Verify the interpreter has a valid arch */
            if (!elf_check_arch(interp_elf_ex) ||
                elf_check_fdpic(interp_elf_ex))
                goto out_free_dentry;
     
            /* Load the interpreter program headers */
            interp_elf_phdata = load_elf_phdrs(interp_elf_ex,
                               interpreter);
            if (!interp_elf_phdata)
                goto out_free_dentry;
    
    

解释器也是一个elf文件，这里读取解释器以便于后续操作

## 6、加载程序段

    
    
    for(i = 0, elf_ppnt = elf_phdata;
        i < elf_ex->e_phnum; i++, elf_ppnt++) {
        int elf_prot, elf_flags;
        unsigned long k, vaddr;
        unsigned long total_size = 0;
        unsigned long alignment;
     
        if (elf_ppnt->p_type != PT_LOAD)
            continue;
    

加载所有类型为PT_LOAD的段，当处理第1个PT_LOAD段时，如果文件为dyn类型，还需要对其进行地址随机化。随机化时还需要区分解释器或者其他普通so文件，对于解释器，为避免程序发生冲突，程序固定从ELF_ET_DYN_BASE开始计算偏移进行加载。

    
    
    if (!first_pt_load) {
        elf_flags |= MAP_FIXED;
    } else if (elf_ex->e_type == ET_EXEC) {
        elf_flags |= MAP_FIXED_NOREPLACE;
    } else if (elf_ex->e_type == ET_DYN) {
        if (interpreter) {
            load_bias = ELF_ET_DYN_BASE;
            if (current->flags & PF_RANDOMIZE)
                load_bias += arch_mmap_rnd();
            alignment = maximum_alignment(elf_phdata, elf_ex->e_phnum);
            if (alignment)
                load_bias &= ~(alignment - 1);
            elf_flags |= MAP_FIXED_NOREPLACE;
        } else
            load_bias = 0;
     
        load_bias = ELF_PAGESTART(load_bias - vaddr);
        total_size = total_mapping_size(elf_phdata,
                        elf_ex->e_phnum);
        if (!total_size) {
            retval = -EINVAL;
            goto out_free_dentry;
        }
    }
    

一切就绪后，通过elf_map函数建立用户空间虚拟地址空间与目标映像文件中段的映射

    
    
    error = elf_map(bprm->file, load_bias + vaddr, elf_ppnt,
                    elf_prot, elf_flags, total_size);
    

## 7、装载程序入口地址

    
    
    if (interpreter) {
            elf_entry = load_elf_interp(interp_elf_ex,
                            interpreter,
                            load_bias, interp_elf_phdata,
                            &arch_state);
            if (!IS_ERR_VALUE(elf_entry)) {
                /*
                 * load_elf_interp() returns relocation
                 * adjustment
                 */
                interp_load_addr = elf_entry;
                elf_entry += interp_elf_ex->e_entry;
            }
            if (BAD_ADDR(elf_entry)) {
                retval = IS_ERR_VALUE(elf_entry) ?
                        (int)elf_entry : -EINVAL;
                goto out_free_dentry;
            }
            reloc_func_desc = interp_load_addr;
     
            allow_write_access(interpreter);
            fput(interpreter);
     
            kfree(interp_elf_ex);
            kfree(interp_elf_phdata);
        } else {
            elf_entry = e_entry;
            if (BAD_ADDR(elf_entry)) {
                retval = -EINVAL;
                goto out_free_dentry;
            }
        }
    
    

对于需要解释器的程序，需要先通过load_elf_interp函数装入解释器的映像，并将程序入口点设置为解释器的入口地址，对于不需要解释器的文件，直接读取elf_header中的入口点虚拟地址即可。

## 8、添加参数和环境变量等配置信息

    
    
    retval = create_elf_tables(bprm, elf_ex, interp_load_addr,
                   e_entry, phdr_addr);
    if (retval < 0)
        goto out;
     
    mm = current->mm;
    mm->end_code = end_code;
    mm->start_code = start_code;
    mm->start_data = start_data;
    

