其实定时任务不止有 Crontab，还有 Anacron、at。就算是大家最为熟悉的
crontab，其实还是有很多细节的知识的。比如各位可以问问自己，若攻击者插入了一条恶意的
crontab，该怎么找出来呢？或者说，如何完整地检查一下服务器的 crontab 呢？大家的第一反应可能是 crontab
-l，但其实这样只能检查很有限的一部分。 **本文以 centos 为例** ，介绍一下 Linux 定时任务的检查方式。

## ## Crontab

大多数人都用过 Crontab：crontab -e / -l，所以这里就不介绍了，也不赘述使用方式了。

要想完整的列出 crontab，最好还是从 crontab 保存的定时任务文件入手。

### ### Crontab 相关的文件

Crontab 相关的文件分别在 /etc、/var/spool/cron/ 下：

  1. /etc/ 
    1. /etc/cron.allow: 相当于白名单，限制类配置，不在这里面的用户不能使用 crontab
    2. /etc/cron.deny: 相当于黑名单，限制类配置，在这里面的用户不能使用 crontab
    3. /etc/crontab: 系统级别的定时任务配置，可以理解为大家一起用的定时任务，所有权是系统而不是特定的某用户
    4. /etc/cron.d/: 这个文件夹下的配置同 /etc/crontab。假如你有个定时任务不想直接写到 /etc/crontab里，那么你可以选择新建一个文件，放在 /etc/cron.d/ 里面（无需其他配置，直接生效）。 
      1. /etc/cron.d/0hourly: 自带的，其实就是用 run-parts 去执行 /etc/cron.hourly 下面的脚本
      2. ...（可能有其他用户把定时任务放在这下面）
    5. /etc/cron.hourly/: 被 /etc/cron.d/0hourly 执行。里面是可执行文件或者 shell 脚本。 
      1. /etc/cron.hourly/0anacron: anacron 下面会讲
    6. /etc/cron.daily、/etc/cron.weekly、/etc/cron.monthly: 看起来和 crontab 有关系？其实是 anacron的！下面会讲
  2. /var/spool/cron/: 存放每个用户的 crontab，所有权是特定的用户（注意与 /etc/crontab 对比）。这个就是我们在用 crontab -e 的时候创建/编辑的文件，所以文件名就是用户名，并且执行的时候是用文件名（即用户名）的权限来执行的，例如你在下面建了一个名叫 Tr0y 的文件，则会以 Tr0y 的身份去执行这个文件里的定时任务。需要注意的是，如果你在这个目录下强行创建了一个以不存在的用户名为命名的文件，例如 test，但是你又没有这个用户的话，test 里面的定时任务是不会执行的。另一个需要注意的是，/var/spool/cron/ 的所有权是 root，所以普通用户是没办法直接在下面创建文件的，只能加 sudo 或者通过 crontab -e。 
    1. ...（各个用户的 crontab）

注意，/etc/cron.allow 的优先级比 /etc/cron.deny
要高，所以配置只需要选择一种来限制即可。一般来说，系统的用户相对可靠，故默认保留的是 /etc/cron.deny，且内容为空，这样所有人都能用
crontab。如果这两个限制文件都不存在，那么只有 root 才能使用 crontab。

最后需要注意的是，cron 是不会递归文件夹的，所以你在 /etc/cron.d/ 和 /var/spool/cron/
下面建文件夹，再在里面放配置文件是没用的。为什么要特别提到这一点？因为我见过有攻击者这么干过...

### ### 防御建议

1\. 使用 /etc/cron.allow 来指定可使用 crontab 的用户（最好不要使用黑名单的/etc/cron.deny）。需要注意的是，
**此文件一定要是 root 所有** 。  
2\. 检查 crontab 的时候，分别检查：/etc/crontab、/etc/cron.d/*、/var/spool/cron/*。  
3\. 检查是否有除了 /etc/cron.hourly/0anacron 之外的 anacron 定时任务（下面会提）

## ## Anacron

Anacron 可能大家用的少一点，所以会说的多一些。

它与 Crontab 最大的不同在于，它会去执行那些落下的定时任务。举个例子，假如你设定了一个 Crontab 定时任务，在每周六晚上 6
点执行。但是正好周六晚上 5 点到 7 点停电了，那么这个定时任务相当于这一轮就没有执行。但是如果你用的是
Anacron，它会去检查并执行那些没有执行过的定时任务。实际上，Anacron 是每个小时被 crond（Crontab 服务）执行一次，然后
Anacron 再去检测相关的定时任务有没有被执行，如果有超期没被执行的工作，就执行该定时任务。

Anacron 其实仅仅是一个程序，不像 Crontab 那样利用 crond 服务执行。之前在 Crontab
里提到过，有个自带的每一个小时执行一次的定时任务集 合：/etc/cron.d/0hourly，而这个定时任务其实就是用 run-parts 去执行
/etc/cron.hourly 下面的脚本，这里面自带一个 0anacron，其实就是这一节提到的 Anacron。所以 Anacron 其实是依托于
Crontab 去定时执行的。0anacron 如下：

    
    
    #!/bin/sh
    # Check whether 0anacron was run today already
    if test -r /var/spool/anacron/cron.daily; then
        day=cat /var/spool/anacron/cron.daily
    fi
    if [ date +%Y%m%d = "$day" ]; then
        exit 0;
    fi
    
    # --- 上面这部分就是我说的检测定时任务是否执行过的逻辑 ---    
    # Do not run jobs when on battery power
    if test -x /usr/bin/on_ac_power; then
        /usr/bin/on_ac_power >/dev/null 2>&1
        if test $? -eq 1; then
        exit 0
        fi
    fi
    /usr/sbin/anacron -s

# 所以这个脚本其实执行的就是 anacron -s...

各位可能会觉得很奇怪，为啥这个名字最前面要加个 0。根据网上的说法，0 开头的定时任务会排在最前面执行，这样的话，就避免了有些 Crontab
定时任务执行过之后，Anacron 误以为 Crontab 没执行，导致重复执行某些定时任务。包括命令之前加上 nice 让它优先获得 cpu
以便执行，也是出于这个目的。

### ### Anacron 的相关文件

  1. /etc/anacrontab: 与 /etc/crontab 类似，自带，通过 run-parts 执行 /etc/cron.daily、/etc/cron.weekly、/etc/cron.monthly。
  2. /var/spool/anacron/: 记录上面几个的执行时间，内容就是年月日 
    1. /var/spool/anacron/cron.daily
    2. /var/spool/anacron/cron.monthly
    3. /var/spool/anacron/cron.weekly
  3. anacrontab 可以通过 -t 参数指定 /etc/anacrontab 的位置，默认就是 /etc/anacrontab

简单解释一下 /etc/anacrontab 的内容吧：

    
    
    SHELL=/bin/sh
    PATH=/sbin:/bin:/usr/sbin:/usr/bin
    MAILTO=root
    RANDOM_DELAY=45         # 执行之前随机延迟时间（分钟，可分散服务器的压力）
    START_HOURS_RANGE=3-22  # 允许执行命令的时间段（这里是 3 点 - 22 点才能执行）
    
    1                 5        cron.daily         nice run-parts /etc/cron.daily
    
    # 1: 每隔多久执行（天）
    # 5: 固定延迟时间（分钟）
    # cron.daily: 定时任务名称，随便设置，主要是看 log （/var/log/cron 的时候可能有用）
    # nice run-parts /etc/cron.daily: 定时任务的核心 —— 要执行的命令

与 /etc/cron.d/0hourly 挺像的，同时名字最前面加 0 这个逻辑也是一样的。

  1. 以 cron.daily 为例，对照上面这个配置，总结一下 Anacron 的运行流程：  
crond 读取 /etc/crontab、/var/spool/cron/*、/etc/cron.d/*，根据设定的时间执行

  2. 执行到 /etc/cron.d/0hourly 的时候，执行 /etc/cron.hourly/ 下的所有可执行文件，其中就有 0anacron
  3. 0anacron 执行 anacron
  4. anacron 读取 /etc/anacrontab，它指定了 cron.daily 执行间隔为 1 天
  5. 从 /var/spool/anacron/cron.daily 取出最近一次执行 anacron 的时间
  6. 比较当前时间与上一步获得的时间，若相差 1 天以上 （含 1 天），则准备执行指定的定时任务。
  7. 根据 /etc/anacrontab 的设置，执行之前要先延时 5 分钟 + n 分钟（n 为不超过 45 的随机数）
  8. 延时到点之后，开始执行指定的命令，即 nice run-parts /etc/cron.daily
  9. 执行完毕，结束

最后，anacrontab 仅能用 root 权限配置。

### ### 防御建议

anacrontab
的执行比较佛系，最快也就是一天执行一次（除非加上了-f，强制每轮检查都执行），所以恶意软件通常不想用这个去做持久化。不过也不好说，谁让它比 crontab
隐蔽呢？

  1. 检查 /etc/anacrontab 下是否有疑似恶意的定时任务
  2. 检查 /etc/cron.hourly/0anacron 是否利用-t自定义了 anacrontab 定时任务文件位置，如果有也要检查这个自定义的文件。

## ## at

at 依赖于 atd 服务执行，这点与 crontab 有点像，但现在似乎不是默认启用 atd 的，所以可能需要手动启动（systemctl start
atd）。它与前两个最大的区别在于 at 是一次性的， **设定完之后只会运行一次** 。

### ### at 的相关文件

  1. /etc/at.allow: 相当于白名单，限制类配置，不在这里面的用户不能使用 at
  2. /etc/at.deny: 相当于黑名单，限制类配置，在这里面的用户不能使用 at
  3. /var/spool/at/: 保存定时任务的文件夹。下面用特定格式的文件名存放定时任务详情，包括命令、环境变量、设定定时任务时的路径等。 
    1. /var/spool/at/spool: 据说是保存输出的文件夹...至于是什么输出、什么时候会输出到这里就不得而知了...
    2. 示例：a000030196c020。这个文件名的格式暂时没找到资料，不过经过我的测试，格式应该为，a(固定)+00011(任务每加一个这里要+1)+从 1970-01-01 08:00:00 至 任务执行时间 的分钟数(8 位，位数不够在前面补 0) （注意这里面计算都是十六进制的）

上面的两个限制文件个 crontab 类似，也是 allow 的优先级比 deny 要高，如果这两个限制文件都不存在，那么只有 root 才能使用 at。

当然，你也可以不用 at 来新建定时任务，只要往 /var/spool/at/ 下面新建文件，注意权限要有 x，且得是 root
才能这么创建，至于文件名，一定要按照上面的规则才能被识别。示例，若我们想建一个在 2030-01-01 08:00:00 执行的定时任务。先计算一下时间差：

    
    
    In [27]: import datetime
    
    In [28]: delta = datetime.datetime.strptime('2030-01-01 08:00:00', "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime('1970-01-01 0
        ...: 8:00:00', "%Y-%m-%d %H:%M:%S")
    
    In [29]:  hex(delta.days * 24 * 60)  # 转分钟
    Out[29]: '0x1e187e0'
    

补齐至 8 位：01e187e0。

所以这个定时任务的格式应该为 a+00012(上一个任务+1)+01e187e0(时间差) = a0001201e187e0：

    
    
    ➜  at atq
    ➜  at vim a0001201e187e0
    ➜  at atq
    18 Tue Jan  1 08:00:00 2030 a root
    

各位如果比较敏感的话，就会想到 8 位的 hex，会不会出现类似千年虫的 bug 呢？0xffffffff = 4294967295 年，43
亿年，嗯，各位是等不到了。

最后有几点要提一下：

  1. 如果 at 定时任务执行没有成功，似乎会变成=开头的定时任务（原来是a开头的）
  2. 执行时间在过去的定时任务是不会被执行的
  3. 在直接写 at 定时任务的时候，要注意开头要有这三行：

    
    
    #!/bin/sh            # shell
    # atrun uid=0 gid=0  # 应该是表明计划任务的拥有者的权限，未考证
    # mail root 0        # 触发发邮件的逻辑时，收件人是谁
    

4\. 与 at 相关的还有一个 batch 命令，通过它设定的 at 定时任务，只有在 cpu 负载小于 0.8 的时候才会运 行，且文件名则会以 b
开头。其实原理都是一样的，batch 也是用 at 来配置定时任务的：

    
    
    ➜  at echo 'echo <0001f382> > /dev/pts/8' | batch && ls
    job 32 at Mon Aug  3 17:35:00 2020
    b000200195ff5f  spool

at 的可读性还是很好的，例如你可以给自己发一个生日祝福：

    
    
    ➜  ~ echo 'echo <0001f382> > /dev/pts/8' | at 00:00 September 7
    job 1 at Mon Aug  3 14:02:00 2020
    ➜  ~ atq
    1 Mon Sep  7 00:00:00 2020 a root
    ➜  ~ ls /var/spool/at/
    a000010195fe8a  spool
    ➜  ~ cat /var/spool/at/a000010195fe8a
    #!/bin/sh
    # atrun uid=0 gid=0
    # mail root 0
    ...
    cd /root || {
      echo 'Execution directory inaccessible' >&2
      exit 1
    }
    ...
    echo <0001f382> > /dev/pts/8  
    ...

等到 9 月 7 号，你就会收到你自己给自己发的祝福了（前提是你的 tty 没变），~~再也不用担心没人送祝福啦...怎么这么凄凉呢...~~###
防御建议

如果说选择 anacrontab 的恶意软件较少，那么选择 at 的恶意软件就更少了，同样也是比较隐蔽，甚至比 anacrontab 要更加隐蔽。

1\. 使用 /etc/at.allow 来指定可使用 at 的用户（最好不要使用黑名单的/etc/at.deny）。需要注意的是， **此文件一定要是
root 所有** 。

2\. 检查 /var/spool/at/ 下是否有可疑的定时任务

最后，现在已经知道恶意的定时任务可能出现在哪些地方了，剩下的就是如何识别一个定时任务是不是恶意的了。有传统的关键字、正则匹配，启发式的机器学习、深度学习...这就得大家各显神通了

**吐槽：编辑器真的是越 来 越 难 用 了...**

