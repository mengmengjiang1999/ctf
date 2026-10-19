***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：LEdge1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

**之前WinRAR出现的漏洞，没几天网上就出现了各种利用这种漏洞的攻击了，想到这，我突然想起来Linux下也有这么一款解压软件也是有漏洞的。今天给大家说一说吧
！**

我们在Linux下使用最多的压缩和解压工具就是tar了。如果说这款工具出现了漏洞，那么危害还是很大的。不过还真的出现了一个解压路径的漏洞：这个漏洞出现在tar解压命令上，如果恶意者提前构造好这种有害的压缩包。当我们在使用tar命令解压的时候导致压缩包解压到不是我们指定的目录下面，导致了文件覆盖，更有甚者进行远程的代码执行！

## 影响范围

GNU tar ：1.14 ~1.29 (包含1.29)

影响系统包括所以使用GNU tar命令的linux系统

## 实验环境

操作机 ： Kali Linux

## 实验工具

![](https://image.3001.net/images/20190309/1552107548_5c83481cf2300.png!small)

    
    
    tar-poc.tar ：这个文件是本次漏洞试验的POC，我们将使用本文件验证漏洞
    
    tar-1.26.tar.gz ：1.26版本的tar源码

## 实验步骤

### 步骤1：漏洞分析

在实现漏洞复现之前我们得了解一下，这个漏洞的是什么原因导致的。那我们就得对源码进行分析，在进行源码的分析过程中发现了paxnames.c这个文件是有问题的，那我们废话不多说进入源码存放文件夹，盘它：

    
    
    cd /root/Desktop/ // 进入桌面
    
    cat tar-1.26/lib/paxnames.c // 预览paxnames.c文件

在tar1.26的源码包中，lib文件夹下存放着函数库和一些配置文件，其中paxnames.c文件里面存放着检测文件名和路径安全性的相关函数和配置。就是检测程序考虑的不够完美导致了漏洞的出现。

打开后，可以看到如下代码：

![](https://image.3001.net/images/20190309/1552107563_5c83482b02ffa.png!small)

    
    
    char *
    
    safer_name_suffix (char const*file_name, bool link_target,
    
        bool absolute_names)
    
    {
    
     char const *p;
    
     if (absolute_names)
    
       p = file_name;
    
     else {
    
         /* Skip file system prefixes, leading file name components that contain
    
     &ampquot..&ampquot, and leading slashes.  */
    
                 size_tprefix_len = FILE_SYSTEM_PREFIX_LEN (file_name);
    
     
    
         for (p = file_name + prefix_len; *p; )
    
     {
    
             if (p[0] == '.' &ampamp&ampamp p[1] == '.' &ampamp&ampamp(ISSLASH (p[2]) || !p[2]))
    
        prefix_len = p + 2 - file_name;
    
     
    
      do
    
        {
    
          char c = *p++;
    
          if (ISSLASH (c))
    
     break;
    
        }
    
      while (*p);
    
     }
    
     
    
         for (p = file_name + prefix_len; ISSLASH (*p); p++)
    
     continue;
    
         prefix_len = p - file_name;
    
     
    
         if (prefix_len)
    
     {
    
      const char *prefix;
    
      if (hash_string_insert_prefix (&ampampprefix_table[link_target],file_name,
    
         prefix_len, &ampampprefix))
    
        {
    
          static char const *const diagnostic[] =
    
          {
    
     N_(&ampquotRemoving leading `%s' from member names&ampquot),
    
     N_(&ampquotRemoving leading `%s' from hard link targets&ampquot)
    
          };
    
          WARN ((0, 0, _(diagnostic[link_target]), prefix));
    
        }
    
     }
    
       }

在研究了一段时间之后发现，这段代码里面有个safer_name_suffix函数，他的任务就是检测文件名是否合法，文件后缀是否合法。

absolute_names 是一个变量，它用来获得文件的名称，如果absolute_names变量为0，那么就将文件名中文件系统的前缀给去掉。

在之前比较老的版本，如果压缩文件中存在 .. 字符串，系统会跳过不去处理这些文件。

而在后来的版本中，safer_name_suffix不再跳过文件名中包含 ../ 字符串的恶意字符，强制删除所有存在可能被恶意访问的字符，如 ../ ，把
../ 之前的所有字符都删除，只会留下其后面的字符。

使其与解压目标路径变成相对路径，而压缩包中的内容就会覆盖恶意访问者指定的路径文件，漏洞就这样产生了。

![](https://image.3001.net/images/20190309/1552107609_5c834859cd2fb.png!small)

例如：test.tar压缩包中有一个文件夹，其文件夹路径依次为 etc/motd../etc/shadow ，然后在执行命令 tar -C / -xvf
test.taretc/motd ，意思是将test.tar里面的内容解压到etc/motd目录下。

但是在safer_name_suffix函数中经过一系列操作，已经将 ../ 之前的内容都去掉了，路径名只剩下 etc/shdow ，这时候，
etc/shdow 就被覆盖了。

### 步骤2：使用POC验证漏洞

本步将使用POC验证漏洞.

现在我们使用POC来验证漏洞，因为此POC是覆盖 etc/shadow ，所以我们首先先查看一下原始的shadow文件有什么内容。

使用命令：

    
    
    cat /etc/shadow // 预览shadow文件的内容

![](https://image.3001.net/images/20190309/1552107626_5c83486a7c863.png!small)

可以看到，里面记录了各个账户的用户名、加密过的密码、上次更改密码的日期等。

接下来我们来解压POC，将他解压到 etc 目录下，使用命令：

    
    
    cd /root/Desktop
    
    tar -C / -xvf tar-poc.tar etc/motd

其中，X的意思是从归档文件中释放文件。v的意思是输出tar处理文件的信息到屏幕。f的意思是使用归档文件，一般情况下f这个选项是必选的。

![](https://image.3001.net/images/20190309/1552107648_5c83488072970.png!small)

这时，再次查看 etc/shadow 文件，发现已经被替换。已经不是之前的内容。

我们明明是解压到etc/motd的目录下，它却解压到etc的根目录下，覆盖了shadow文件，因此到这里，我们就成功的验证了漏洞。

## 实验结果分析与总结

### 漏洞修复

自己琢磨了一段时间之后，发现在safer_name_suffix中添加判断，如果检测到 ../ 字符串，直接报错，然后退出程序，如下：

    
    
    --- lib/paxnames.c.orig    2016-04-06 00:04:47.314860045 +0300
    
    +++ lib/paxnames.c      2016-04-06 02:08:44.962297881 +0300
    
    @@ -18,6 +18,7 @@
    
    #include &ampltsystem.h&ampgt
    
    #include &amplthash.h&ampgt
    
    #include &ampltpaxlib.h&ampgt
    
    +#include &ampltquotearg.h&ampgt
    
    /* Hash tables of strings.  */
    
    @@ -114,7 +115,15 @@
    
         for (p = file_name + prefix_len; *p; )
    
           {
    
             if (p[0] == '.' &ampamp&ampamp p[1] == '.' &ampamp&ampamp(ISSLASH (p[2]) || !p[2]))
    
    -          prefix_len = p + 2 - file_name;
    
    +            {
    
    +            static char const *constdiagnostic[] =
    
    +            {
    
    +              N_(&ampquot%s: Member namecontains '..'&ampquot),
    
    +              N_(&ampquot%s: Hard link targetcontains '..'&ampquot)
    
    +            };
    
    +            FATAL_ERROR ((0, 0,_(diagnostic[link_target]),
    
    +                          quotearg_colon(file_name)));
    
    +          }

这种方法的确可以修复漏洞，但还有一点不足，用户在配置文件或者操作文件时，如果遇到 ../ 这种情况，到一半就强行停止下来，这样的话用户体验度很差。

 ***本文作者：LEdge1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

