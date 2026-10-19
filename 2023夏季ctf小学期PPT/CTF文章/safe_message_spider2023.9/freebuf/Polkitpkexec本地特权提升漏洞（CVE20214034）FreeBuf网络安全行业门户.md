# 简介

Qualys 研究团队在 polkit （原名PolicyKit）的 pkexec 中发现了一个本地特权提升漏洞，该SUID-root程序默认安装在每个主要的Linux发行版上。该漏洞允许任何非特权用户通过在Linux默认配置中利用此漏洞来获得易受攻击主机的完全root权限。

# 关于 Polkit pkexec for Linux

Polkit（原名PolicyKit）是一个用于在类 Unix
操作系统中控制系统范围权限的组件。它为非特权进程与特权进程通信提供了一种有组织的方式。还可以使用polkit以提升的权限执行命令，先使用命令pkexec，然后是要执行的命令（具有root权限）。

# PwnKit 漏洞的潜在影响

成功利用此漏洞允许任何非特权用户在易受攻击的主机上获得root特权。Qualys安全研究人员已经能够独立验证漏洞，开发漏洞利用，并在默认安装的Ubuntu、Debian、Fedora和CentOS上获得完整的root权限。其他Linux发行版可能容易受到攻击并且可能被利用。这个漏洞已经隐藏了12年多，并影响到目前为止所有版本的pkexec。（≤0.120）

# 漏洞披露时间表

  * 2021-11-18：咨询发送至 secalert@redhat。
  * 2022-01-11：咨询和补丁发送到 distros@openwall。
  * 2022-01-25：协调发布日期（世界标准时间下午 5:00）。

# 漏洞分析

在<https://www.freedesktop.org/software/polkit/releases/>下载0.120版本的源码，查看src/programs/pkexec.c文件。部分代码如下：

    
    
    435 main (int argc, char *argv[])
    436 {
    ...
    534   for (n = 1; n < (guint) argc; n++)
    535     {
    ...
    568     }
    ...
    610   path = g_strdup (argv[n]);
    ...
    629   if (path[0] != '/')
    630     {
    ...
    632       s = g_find_program_in_path (path);
    ...
    639       argv[n] = path = s;
    640     }
    

在第 534-568 行，pkexec的main函数处理命令行参数，在第 610-640 行，pkexec在 PATH
环境变量的目录中搜索要执行的程序，如果其路径不是绝对路径，argv[n] = path = s。不幸的是，如果命令行参数argc的数量为0，那么：

  * 在第 534 行，整数n永久设置为1；
  * 在第 610 行，从argv[1]越界读取指针路径；
  * 在第 639 行，指针s被越界写入argv[1]。

但是从这个越界的argv[1]中读取和写入的到底是什么？要回答这个问题，我们必须简短地离题。我们需要了解execve函数，函数原型如下：

    
    
    int execve(const char *filename, char *const argv[], char *const envp[]); 
    

当我们使用execve函数启动一个新程序时，内核将我们的参数、环境变量字符串和指针（argv和envp）复制到新程序堆栈的末尾；例如execve("/usr/bin/pkexec",{"program","-option",...},{"value","PATH=name",...})的内存布局如下：

    
    
    |---------+---------+-----+------------|---------+---------+-----+------------| 
    | argv[0] | argv[1] | ... | argv[argc] | envp[0] | envp[1] | ... | envp[envc] | 
    |----|----+----|----+-----+-----|------|----|----+----|----+-----+-----|------| 
    V         V                V           V         V                V 
    "program" "-option"           NULL      "value" "PATH=name"          NULL 
    

显然，因为argv和envp指针在内存中是连续的，如果argc为0，那么越界argv[1]实际上是envp[0]，指向我们的第一个环境变量“value”的指针。最后：

  * 在第610行，将要执行的程序的路径从argv[1]（即envp[0]）中越界读取，并指向“value”；
  * 在第 632 行，这个路径“value”被传递给 g_find_program_in_path函数（因为在第 629 行“value”不是以斜杠开头）；
  * 然后g_find_program_in_path函数在我们的 PATH 环境变量的目录中搜索一个名为“value”的可执行文件；
  * 如果找到这样的可执行文件，则将其完整路径返回给pkexec第 632 行的指针s；
  * 最后在第 639 行，这个完整路径被越界写入argv[1]（即envp[0]），从而覆盖了我们的第一个环境变量。

所以，更准确地说：

  * 如果我们的PATH环境变量是“PATH=name”，并且如果目录“name”存在（在当前工作目录中），并且包含一个名为“value”的可执行文件，那么指向字符串“name/value”的指针将被越界写入envp[0]；

或者

  * 如果我们的PATH是“PATH=name=.”，并且如果目录“name=.” 存在并包含一个名为“value”的可执行文件，那么指向字符串“name=./value”的指针将被越界写入envp[0]。

换句话说，这种越界写入允许我们将“不安全”的环境变量（例如，LD_PRELOAD）重新引入 pkexec
的环境。这些“不安全”变量通常在调用main函数之前通过ld.so从 SUID 程序的环境中删除。

最后注意事项：polkit 还支持非 Linux 操作系统，例如 Solaris 和 *BSD，但Qualys 研究团队尚未调查它们的可利用性。他们注意到
OpenBSD 是不可利用的，因为如果argc为0，它的内核拒绝执行程序。

# 漏洞利用

要想成功利用此漏洞，我们应该将哪个“不安全”变量重新引入pkexec的环境中呢？我们的选项是有限的，因为在第639行越界写入后不久，在第702行将完全清除其环境变量：

    
    
    639       argv[n] = path = s;
    ...
    657   for (n = 0; environment_variables_to_save[n] != NULL; n++)
    658     {
    659       const gchar *key = environment_variables_to_save[n];
    ...
    662       value = g_getenv (key);
    ...
    670       if (!validate_environment_variable (key, value))
    ...
    675     }
    ...
    702   if (clearenv () != 0)
    

为了将错误消息打印到stderr，pkexec调用GLib的g_printerr函数（注意：GLib是一个GNOME库，而不是GNU
C库，也称为glibc）；例如，函数validate_environment_variable和log_message调用g_printerr（第126行和第408-409行）：

    
    
    88 log_message (gint     level,
    89              gboolean print_to_stderr,
    90              const    gchar *format,
    91              ...)
    92 {
    ...
    125   if (print_to_stderr)
    126     g_printerr ("%s\n", s);
    ...
    383 validate_environment_variable (const gchar *key,
    384                                const gchar *value)
    385 {
    ...
    406           log_message (LOG_CRIT, TRUE,
    407                        "The value for the SHELL variable was not found the /etc/shells file");
    408           g_printerr ("\n"
    409                       "This incident has been reported.\n");
    

g_printerr函数通常打印UTF-8错误消息，但如果环境变量CHARSET不是UTF-8，它可以在另一个charset中打印消息（注意：CHARSET不是安全敏感的，它不是“不安全”的环境变量）。要将消息从UTF-8转换为另一个字符集，g_printerr函数调用了glibc的函数iconv_open。

要将消息从一个字符集转换为另一个字符集，iconv_open函数执行了小型共享库；通常，这些三胞胎（源字符集、目的字符集和库名称）从默认配置文件/usr/lib/gconv/gconv-modules中读取。环境变量GCONV_PATH可以强制iconv_open函数读取另一个配置文件；当然，GCONV_路径是“不安全”的环境变量之一（因为它会导致执行任意库），但被ld.so从SUID程序的环境变量中移除。

不幸的是，CVE-2021-4034允许我们将GCONV_PATH重新引入pkexec的环境，并以root用户身份执行我们自己的共享库。

重要提示：这种利用技术会在日志中留下痕迹（“在/etc/shells文件中找不到SHELL变量的值”或“环境变量的值[…]）。此漏洞也可以不留痕迹的被利用，感兴趣的可以自行寻找。

关于pkexec、GLib和GCONV_PATH的进一步讨论，请参阅Tavis Ormandy、Jakub Wilk和Yuki Koike的以下帖子：

<https://www.openwall.com/lists/oss-security/2014/07/14/1><https://www.openwall.com/lists/oss-security/2017/06/23/8><https://hugeh0ge.github.io/2019/11/04/Getting-Arbitrary-Code-Execution-from-fopen-s-2nd-Argument/>

## EXP

<https://github.com/berdav/CVE-2021-4034>

GitHub还有很多

在Kali Linux 2020.4中pkexec版本为0.105，如图：  

![](https://image.3001.net/images/20220126/1643191282_61f11bf2bdf917e732950.png!small)

成功利用该漏洞提升权限至root，如图：![](https://image.3001.net/images/20220126/1643191300_61f11c041dfd5e58c5d6b.png!small)

在CentOS
7中pkexec版本0.112同样成功利用该漏洞提升权限，如图：![](https://image.3001.net/images/20220126/1643191320_61f11c186895d88540cec.png!small)

# 修复建议

1、取消pkexec程序特权

    
    
    chmod 0755 /usr/bin/pkexec
    

2、GitHub源码已进行加固，需要自行安装：<https://github.com/freedesktop/polkit/commit/a2bf5c9c83b6ae46cbd5c779d3055bff81ded683>

