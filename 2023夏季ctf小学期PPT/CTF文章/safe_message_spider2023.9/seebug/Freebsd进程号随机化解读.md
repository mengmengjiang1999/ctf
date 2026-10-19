**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/2qX9PKKZ5KA10WFPuMFUbA>**

Freebsd提供了一个有意思的安全功能，fork的进程号可以随机化。这个小功能很有用，可以防止恶意软件猜测父子进程号，内核提供了一个random_pid变量，可以通过sysctl设置。

    
    
    static int randompid = 0;
    
    static int
    sysctl_kern_randompid(SYSCTL_HANDLER_ARGS)
    {
            int error, pid;
    
            error = sysctl_wire_old_buffer(req, sizeof(int));
            if (error != 0)
                    return(error);
    
            sx_xlock(&allproc_lock);
            pid = randompid;
            error = sysctl_handle_int(oidp, &pid, 0, req);
    
            if (error == 0 && req->newptr != NULL) {
                    if (pid == 0)
                            randompid = 0;
    
                    else if (pid == 1)
                            /* generate a random PID modulus between 100 and 1123 */
                            randompid = 100 + arc4random() % 1024;
                    else if (pid < 0 || pid > pid_max - 100)
                            /* out of range */
                            randompid = pid_max - 100;
                    else if (pid < 100)
                            /* Make it reasonable */
                            randompid = 100;
                    else
                            randompid = pid;
            }
    
            sx_xunlock(&allproc_lock);
            return (error);
    }

Sysctl首先获取sysctl设置的pid值，然后根据pid值计算randompid的范围。pid为0表示关闭randompid功能，为1是randompid的范围限制在100-1023，小于0或者大于最大进程号减100，则设置为最大进程号减去100，这样会使randompid的范围变得很大，如果想采取更高的安全性，可以这样设置。pid小于100，randompid设置为固定的100。

    
    
    static int
    
    fork_findpid(int flags)
    {
            pid_t result;
            int trypid;
    
            trypid = lastpid + 1;
            if (flags & RFHIGHPID) {
                    if (trypid < 10)
                            trypid = 10;
            } else {
                    if (randompid)
                            trypid += arc4random() % randompid;
            }
    
            mtx_lock(&procid_lock);
    }

在fork时调用fork_findpid，如果没有RFHIGHPID标志，再次调用arc4random()，生成一个0-randompid的值，这个值用作要搜取的bit数组索引。

实际测试下，首先关闭进程号随机功能：

    
    
    root@kexp:~/code # sysctl kern.randompid=0
    kern.randompid: 231 -> 0
    root@kexp:~/code # ./test
    father: 93528
    child: 93529

父子进程号可以预测。

开启进程号随机功能：

    
    
    root@kexp:~/code # sysctl kern.randompid=1
    kern.randompid: 0 -> 256
    root@kexp:~/code # ./test
    father: 93989
    child: 94050

可以看到子进程号变得不可预测了。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1450/>

