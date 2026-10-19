**linux的基础命令**

## linux入门

    
    
    LAMP(linux+Apache+Mysql+php)  
    LNMP(LiNUX+NIGINX+MYSQL+PHP)

## 走进Linux系统

###  **开机登录**

开机会启动很多程序，他们在windows叫做服务（service),在linux叫做“守护进度”

###  **关机**

关机指令为：shutdown

    
    
    sync#将数据由内存同步到硬盘  
    shutdown# 关机  
    shutdown -h now#马上关机  
    shutdown -r now#马上重启

###  **系统目录结构**

1.一切皆文件

2.根目录/，所有的文件均挂载在这个节点下

    
    
    ls /  
    root@kali:~# ls /  
    bin  boot  dev  etc  home  initrd.img  initrd.img.old  lib  lib32  lib64  libx32  lost+found  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var  vmlinuz  vmlinuz.old  
    ​
    
    
    #以下是对这些目录的解释  
    /bin : bin是Binary的缩写，这个目录存放着最经常使用的命令  
    /boot: 这里存放的是启动linux时使用的一些核心文件，包括一些连接文件以及镜像的文件  
    /etc :这个目录用来存放所有的系统管理所需要的配置文件和子目录  
    /home :用户的主目录，在linux中，每个用户都有一个自己的目录，一般该目录名是以用户的账号命名  
    /lib :这个目录里存放着系统最基本的动态连接库，它的作用是类似于windows里的DLL文件  
    /lost+found:  存在突然关机的一些文件  
    /media :linux会自动识别一些设备，例如u盘，光驱等，  
    /mnt :系统提供该目录为了让用户临时挂载别的文件系统的  
    ##/opt :这是给主机额外安装软件所摆放的目录  
    /root :当你是管理员时可以进这个root目录下  
    /usr :这是一个非常重要的目录，用户很多的应用程序和文件都放在这个目录下，类似于windows下的program files  
    /tmp 这个目录是用来存放一些临时文件，用完即丢  
    ​

## 常用的基本命令

###  **目录管理**

    
    
    绝对路径.相对路径

绝对路径的全称：c:\programData\xxxx

相对路径：/xxx

cd: 切换目录命令

返回上一级： cd ../

    
    
    ls (列出目录)

-a :all 查看全部的文件，包括隐藏文件

-l :列出所有的文件，包含文件的属性和权限，没有隐藏文件

所有的linux命令可以组合使用

    
    
    cd 命令 切换目录
    
    cd 目录名（绝对路径，相对路径）
    
    cd ../ 返回上一级目录
    
    cd ../../ 返回上两级目录
    
    root@kali:/# ls bin boot dev etc home initrd.img initrd.img.old lib lib32 lib64 libx32 lost+found media mnt opt proc root run sbin srv sys tmp usr var vmlinuz vmlinuz.old root@kali:/# cd tmp root@kali:/tmp# cd ../usr
    
    通过cd ../usr 的方式我们可以快速切换路径
    
    root@kali:/home# mkdir ccc root@kali:/home# ls ccc
    
    mkdir可以创建文件
    
    cp 复制文件的作用
    
    cp 需要复制的文件 要拷贝到什么文件夹
    
    例如：cp 1.txt sdsds
    
    如果文件重复，选择覆盖或者放弃
    
    rm(移除文件或者目录)
    
    -f 忽略不存在的文件，不会出现警告，强制删除
    
    -r 递归删除目录
    
    -i 互动，删除询问是否删除
    
    rm -rf /  #系统中所有的文件就被删除
    root@kali:/home# rm -rf 1.txt
    root@kali:/home# ls
    test2
    ​
    mv 移动文件或者目录
    
    -f 强制移动
    
    -u 只替换已经更新过的文件
    
    mv 要被移除的文件 移到的位置

### 基础属性

    
    
    root@kali:/# ls -al  
    total 152  
    drwxr-xr-x  19 root root 36864 Aug 30  2019 .  
    drwxr-xr-x  19 root root 36864 Aug 30  2019 ..  
    lrwxrwxrwx   1 root root     7 Aug 30  2019 bin -> usr/bin  
    drwxr-xr-x   3 root root  4096 Aug 30  2019 boot  
    drwx------   2 root root  4096 Aug 30  2019 .cache  
    drwxr-xr-x  17 root root  3320 Jan 26 21:12 dev  
    drwxr-xr-x 166 root root 12288 Jan 26 21:12 etc  
    drwxr-xr-x   3 root root  4096 Jan 26 21:28 home  
    lrwxrwxrwx   1 root root    33 Aug 30  2019 initrd.img -> boot/initrd.img-5.2.0-kali2-amd64  
    lrwxrwxrwx   1 root root    33 Aug 30  2019 initrd.img.old -> boot/initrd.img-5.2.0-kali2-amd64  
    lrwxrwxrwx   1 root root     7 Aug 30  2019 lib -> usr/lib  
    lrwxrwxrwx   1 root root     9 Aug 30  2019 lib32 -> usr/lib32  
    lrwxrwxrwx   1 root root     9 Aug 30  2019 lib64 -> usr/lib64  
    lrwxrwxrwx   1 root root    10 Aug 30  2019 libx32 -> usr/libx32  
    drwx------   2 root root 16384 Aug 30  2019 lost+found  
    drwxr-xr-x   3 root root  4096 Aug 27  2019 media  
    drwxr-xr-x   2 root root  4096 Aug 27  2019 mnt  
    drwxr-xr-x   4 root root  4096 Jan 25 03:08 opt  
    dr-xr-xr-x 229 root root     0 Jan 26 21:11 proc  
    drwxr-xr-x  19 root root  4096 Jan 26 21:14 root  
    drwxr-xr-x  38 root root  1040 Jan 26 21:14 run  
    lrwxrwxrwx   1 root root     8 Aug 30  2019 sbin -> usr/sbin  
    drwxr-xr-x   3 root root  4096 Aug 30  2019 srv  
    dr-xr-xr-x  13 root root     0 Jan 26 21:11 sys  
    drwxrwxrwt  15 root root  4096 Jan 26 21:13 tmp  
    drwxr-xr-x  15 root root  4096 Aug 30  2019 usr  
    drwxr-xr-x  12 root root  4096 Aug 30  2019 var  
    lrwxrwxrwx   1 root root    30 Aug 30  2019 vmlinuz -> boot/vmlinuz-5.2.0-kali2-amd64  
    lrwxrwxrwx   1 root root    30 Aug 30  2019 vmlinuz.old -> boot/vmlinuz-5.2.0-kali2-amd64  
    ​
    
    
    #文件第一个字母  
    d 表示的是目录  
    - 文件  
    l 表示的为链接文档  
    b 表示为装置文件的可供存储的接口设备
    
    
    #wxr  
    w表示可写  
    x代表可执行（execute)  
    r代表可读  
    ​
    
    
    #修改文件属性

 **1.chgrp:更改文件的属组**

chgrp[-R] 属组名 文件名

chgrp -R root www

 **2.chown : 更改属主**

chown -R root www

 **3.chmod :更改文件的9个属性**

linux文件属性有两种设置方法，一种是数字，一种是符号。

linux文件的基本权限就是九个，分别是owner/group/others三种身份各自的read/write/execute权限

    
    
    r:4 w:2 x:1  
    可读可写不可执行 rw- 6  
    可读可写可执行 7  
    chomd 777 文件赋予所有用户可读可写可执行的权限  
    root@kali:/home# chmod 777 test2  
    root@kali:/home# ls  
    test2  
    root@kali:/home# ls -al  
    total 48  
    drwxr-xr-x  3 root root  4096 Jan 26 21:28 .  
    drwxr-xr-x 19 root root 36864 Aug 30  2019 ..  
    drwxrwxrwx  3 root root  4096 Jan 26 08:01 test2  
    root@kali:/home# ls -ll  
    total 4  
    drwxrwxrwx 3 root root 4096 Jan 26 08:01 test2  
    ​
    
    
    #文件内容查看

### 文件内容查看

    
    
    linux 系统中使用以下命令来查看文件的内容
    
    cat 由第一行开始显示文件内容
    
    tac从最后一行开始显示
    
    nl显示的时候 随便输出行号（看代码的时候希望显示行号）
    
    more一页一页的显示文件内容
    
    less与More类似，但是比more更好的是，他可以往前翻页
    
    /后面输入我们要查询的字符表示搜索
    
    head只看头几行 -n
    
    tail只看尾巴几行
    
    cat 文件名  读取文件
    
    在使用more less这些命令的时候按下键盘q会立刻退出
    
    拓展：linux 链接的概念
    
    linux的链接分为两种：硬链接，软链接
    
    创建链接 ln命令

touch 命令创建文件

 **touch f1**

root@kali:/home# touch 1.txt root@kali:/home# ls 1.txt test2 root@kali:/home#
cat 1.txt

 **echo输入字符串** **echo "15sdsdsd" >> 1.txt**

root@kali:/home# echo "15sdsdsd" >> 1.txt root@kali:/home# cat 1.txt 15sdsdsd

### vim编辑器

vim通过一些插件可以实现和IDE一样的功能

（查看内容，编辑内容，保存内容）

esc 加上

### 账号管理

    
    
    useradd命令 添加用户
    
    useradd -选项 用户名
    
    -m 自动创建这个用户的主目录 /home/qqqq
    
    useradd -m ccc 创建一个用户
    
    root@kali:/home# useradd -m ccc
    root@kali:/home# ls
    1.php  ccc  lll  test2
    root@kali:/home# 
    ​
    
    在linux中一切都是文件，这里的添加用户说白了就是往某一文件中写入用户的信息 /etc/passwd
    
    删除用户 userdel -r 用户名
    
    userdel -r ccc
    
    修改用户 usermod 
    
    usermod 对应

