Uptycs 威胁研究人员最近发现一个 ELF 勒索软件，它会根据给定的文件夹路径加密 Linux 系统内的文件。根据给出的 README 说明，其与
DarkAngels 勒索软件的 README 说明完全一致。

![image.png-212kB](https://image.3001.net/images/20220921/1663728065_632a79c13282344aca1eb.png!small)DarkAngels
勒索软件

DarkAngels 勒索软件五月份完成首秀，最初发现是针对 Windows 系统的。本次发现的 ELF
文件可能是最新的，而样本中的暗网链接并不存在，这可能说明针对 Linux 的勒索软件仍在开发中。

## 技术概述

ELF 版本的勒索软件需要一个文件夹作为进行加密的参数。给出了文件夹路径，勒索软件就会开始加密文件夹中存在的文件，加密后的文件扩展名为
`.crypted`。

![image.png-48.8kB](https://image.3001.net/images/20220921/1663728065_632a79c1edc04fcd36676.png!small)DarkAngels
勒索软件

恶意软件使用 pthread_create 创建新线程，新线程通过调用 start_routine() 函数开始执行。

![image.png-293.9kB](https://image.3001.net/images/20220921/1663728066_632a79c2acaee7f0a1693.png!small)创建新线程

start_routine() 函数中会执行以下步骤来加密目标文件：

> 打开目标文件并使用 `fcntl()`对其设置写入锁定

> 关闭目标文件，然后将其重命名为 `*.crypted`

> 打开另一个名为 `*.crypted.README_TO_RESTORE`的文件，将 README 内容写入其中

> 打开 `*.crypted`并使用 lseek 和 write 将加密内容写入其中

> 将所有加密文件的列表都存储在名为 wrkman.log.0 的文件中

![image.png-211.1kB](https://image.3001.net/images/20220921/1663728067_632a79c38f20fba1d2c28.png!small)start_routine
函数

## 结论

针对 Linux 系统或跨平台针对多个操作系统的勒索软件屡见不鲜，攻击者正在不断扩展攻击范围。DarkAngels
勒索软件似乎仍处于开发阶段，其又将矛头指向 Linux 系统。

## IOC

> 3b56cea72e8140a7044336933cf382d98dd95c732e5937a0a61e0e7296762c7b  
>
> http[:]//qspjx67hi3heumrubqotn26cwimb6vjegiwgvrnpa6zefae2nqs6xqad[.]onion/page/6297aa368ec25

## 参考来源

> [Uptycs](https://www.uptycs.com/blog/another-ransomware-for-linux-likely-in-> development)

