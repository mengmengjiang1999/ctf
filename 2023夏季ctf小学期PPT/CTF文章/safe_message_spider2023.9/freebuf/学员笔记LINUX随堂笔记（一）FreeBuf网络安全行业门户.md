好的笔记是成绩提升的开始，试想一下，如果在你开始复习功课时看到的是连自己都看不懂的笔记，会不会更加没有学习的激情？

![v2-78accfa024d74ac3008a9fb31aa657c6_hd.j](https://pic3.zhimg.com/80/v2-78accfa024d74ac3008a9fb31aa657c6_hd.jpg)

今天就给大家分享一下知了堂学员干净整洁的LINUX随堂笔记，大家一起学习一起进步!

## 第1章 基本命令

## 一. 系统开关机、重启命令

### 1.1 shutdown

格式 ： shutdown [选项]

常用命令选项：

-r： 重新启动系统

-h： 关闭系统

-c： 取消运行shutdown

### 1.2 init 0 // 关闭系统

### 1.3 init 6 // 重启系统

### 1.4 reboot // 重启系统

## 二. 查看类命令

### 2.1 type

格式：type [命令] _// 查看命令类型_

实例：

[root@HH 桌面]#type who

who is /usr/bin/who

[root@localhost ~]# type service

service is hashed (/sbin/service)

### 2.2 pwd

格式：pwd [选项（可为空）]

常用选项

-P _//_ _输出当前工作目录的实际物理路径_

-L _//_ _输出当前工作目录的链接路径_

实例：[root@rhel init.d]#pwd

/etc/init.d _//_ _用户当前的工作目录路径是/etc/init.d_

[root@rhel init.d]#pwd -P

/etc/rc.d/init.d

[root@rhel init.d]#pwd –L

/etc/init.d

### 2.3 cd

格式 cd [选项]

常用选项：

cd ~ _//_ _进入root目录_

cd – _// 返回上一次所在目录_

cd . . _// 返回上一级目录_

cd . ./ . . _// 返回上两级目录_

### 2.4 ls

格式 ls [选项] _//查看目录内容_

常用命令选项

\- l ：以长格显示（简写“ll”）目录的详细资料

\- a ：显示所有目录和文件信息，包括隐藏文件

\- A ：类似于“-a”，但不显示“.”和“..”目录的信息

\- d ：显示目录本身的属性

\- h ：以更易读的字节单位（K、M）等显示信息

\- R ：递归显示内容

\- color ：以颜色区分不同文件

实例：

[root@localhost ~]# ls -l

总用量 132

-rw------. 1 root root 2158 3月 9 17:58 anaconda-ks.cfg

drwxr-xr-x 14 root root 4096 3月 10 14:38 cmake-2.8.6

drwxr-xr-x 4 root root 4096 3月 10 15:01 DiscuzPkg

-rw-r--r--. 1 root root 64664 3月 9 17:58 install.log

### 2.5 which

格式：which [命令] _// 查看命令地址_

实例：

[root@localhost ~]# which service

/sbin/service

### 2.6 who

格式： who _//显示已登录当前计算机用户的信息_

实例：

[root@rhel ~]#who

zhngsan tty2 2017-03-20 02:11

root tty1 2017-03-11 18:00

### 2.7 du

格式：du [选项]……[目录名] _//统计目录及文件的空间占用情况_

常用命令选项：

\- a ：统计时包括所有的文件，而不仅仅只统计目录

\- h ：以更易读的字节单位（K、M等）显示信息

\- s ：只统计每个参数所占用空间总的大小

实例：

[root@localhost ~]# du -ah /root/cmake-2.8.6/

4.0K /root/cmake-2.8.6/Source/cmVersionMacros.h

76M /root/cmake-2.8.6/Source

4.0K /root/cmake-2.8.6/CMakeGraphVizOptions.cmake

32K /root/cmake-2.8.6/Makefile

52K /root/cmake-2.8.6/bootstrap

4.0K /root/cmake-2.8.6/cmake_uninstall.cmake

4.0K
/root/cmake-2.8.6/[http://CTestCustom.cmake.in](https://link.zhihu.com/?target=http%3A//CTestCustom.cmake.in)

4.0K /root/cmake-2.8.6/Copyright.txt

52K /root/cmake-2.8.6/CMakeCache.txt

170M /root/cmake-2.8.6/

## 三. 显示文本文件内容

### 3.1 cat

格式：cat [文件名] _//查看文件内容_

实例：

[root@localhost hh]# cat ss

hspowudoabc

skajcwu

jaicboa

### 3.2 less

格式 ：cat [文件名]| less _//可翻页查看文件所有内容_

### 3.3 more

格式：cat [文件名] | more _//查看文件所有内容,不能翻页_

### 3.4 tail

格式： tail [选项] [文件名] _//查看文件内容_

常用选项

tail -# file _//查看文件内容末#行_

tail –f file _//实时查看添加到文件里的内容_

head -# file _//查看文件内容的前#行_

例：

[root@localhost hh]# cat ss

hspowudoabc

skajcwu

jaicboa

[root@localhost hh]# tail -1 ss

jaicboa

## 四. 目录和文件操作

### 4.1 wc

格式 ： wc [命令][文件绝对路径] _//对文件进行统计_

常用命令：

wc [绝对路径] _//统计行数、大小、字符数_

wc –l [绝对路径] _//统计行数_

wc –w [绝对路径] _//统计字符数_

实例：

[root@localhost hh]# cat ss

hspowudoabc

skajcwu

jaicboa

[root@localhost hh]# wc ss

4 3 29 ss

### 4.2 find

格式： find [路径][选项]

常用命令选项

-name：[文件名] _//按照文件名查找文件_

-user：[用户名] _//按照文件的用户所有者来查找文件_

-group：[组名] _//按照文件的组群所有者来查找文件_

-type：[文件类型] _//按照文件类型来查找文件_

-size： n[ckMG] _//查找大小为n的文件，n为数字，c为字节，k代KB，M代表MB，G代表GB_

实例：

[root@localhost ~]# find / -name w

/var/lib/yum/yumdb/w

/usr/share/terminfo/w

/usr/bin/w

### 4.3 mkdir

格式 mkdir [目录名] _//创建目录_

常用命令选项

mkdir dir1 _//创建一个叫做 'dir1' 的目录_  
mkdir dir1 dir2 _//同时创建两个目录_  
mkdir -p /tmp/dir1/dir2 _//创建一个目录树_

### 4.4 touch

格式 touch [文件名] _//创建一个文件_

### 4.5 cp

格式：cp[选项] [源路径] [目的路径] _//复制源路径内容到目的路径内_

常用命令选项

-r： 递归复制

-p： 连同属性一起复制

-a： 目录所有复制

实例：

[root@localhost ~]#cp –r /root/etc /root/ww
_//复制目录root下的etc目录所有内容到root目录下ww目录内_

[root@localhost ~]#cp –r /root/* . _//复制root目录下的所有文件到当前目录_

### 4.6 ln

格式：ln –s [目录或文件][链接名] _//创建一个指向目录或文件的软链接,源文件更改，链接即失效_

ln –l [目录或文件][链接名] _//创建一个指向文件的硬链接，源文件更改不影响链接_

实例：

[root@localhost ~]#ln –s /root/media/Centos /root/cdrom
_//在root目录下创建指向Centos镜像目录的软连接cdrom_

[root@localhost ~]#ln –l /root/media/Centos /root/cdrom
_//在root目录下创建指向Centos镜像目录的软连接cdrom_

### 4.7 rm

格式 ： rm [选项] [文件或目录] _//删除文件或目录_

常用命令选项

-f file1 _//强制删除一个叫做‘file1’的文件_

-rf dir1 _//强制删除一个叫做‘dir1’的目录并同时删除其内容_

-r dir1 _//递归删除目录和目录里的内容（需要依次确认）_

### 4.8 mv

格式： mv [源文件或目录] [目的文件或目录] _//移动当前工作目录下的文件或目录_

实例：

[root@localhost ~]# ls

a b hh

[root@localhost ~]# mv a b

[root@localhost ~]# ls

hh b

[root@localhost ~]# cd b

[root@localhost b]# ls

a

### 4.9 grep

格式：grep [选项][查找模式][文件] _//在文件中查找并显示包含指定字符串的行_

常用命令选项

-i： 查找忽略大小写

-v： 反转查找，输出与条件不相符的行

查找条件设置

1、要查找的字符串以双引号括起来；

2、“^……” _//表示以……开头_

3、“……$” _//表示以……结尾_

4、“^$” _//表示空行_

### 4.10 gzip、bzip2

格式 ： gzip [选项][文件] _//制作、解压gzip方式压缩文档_

bzip [选项][文件] _//制作、解压bzip方式压缩文档_

常用命令选项

-q： 表示高压比，多在创建时

-d： 用于解开已经压缩过的文件

实例：

[root@localhost hh]# gzip kk

[root@localhost hh]#ls

kk.gz

### 4.11 tar归档

格式： tar [选项][压缩包名.tar] 创建压缩包

常用命令选项

-c ：创建tar的包文件

-x ：解开tar格式的包文件

-f ：使用归档文件

-z ：用gzip压缩

-j ：用bzip2压缩

实例：

tar -cvf [压缩包名.tar] file1 _//创建一个非压缩的 tarball_

tar -cvf [压缩包名.tar] file1 file2 dir1 _//创建一个包含了 'file1', 'file2' 以及
'dir1'的档案文件_

tar -tf [压缩包名.tar] _//显示一个包中的内容_

tar -xvf [压缩包名.tar] _//释放一个包_

tar -xvf [压缩包名.tar] -C /tmp _//将压缩包释放到 /tmp目录下_

tar -cvfj [压缩包名.tar].bz2 dir1 _//创建一个bzip2格式的压缩包_

tar -xvfj [压缩包名.tar].bz2 _//解压一个bzip2格式的压缩包_

tar -cvfz [压缩包名.tar].gz dir1 _//创建一个gzip格式的压缩包_

tar -xvfz [压缩包名.tar].gz _//解压一个gzip格式的压缩包_

### 4.12 chmod

格式： chmod [选项][模式][文件] _//更改文件或目录的模式_

chmod [选项][文件]

常用选项

-v： 为每一个文件处理输出诊断

-R： 递归更改文件和目录

操作对象

u： 用户所有者

g： 组群所有者

o： 其他用户

a： 所有用户

操作符号

+： 添加某个权限

-： 取消某个权限

权限

r： 读取权限

w： 写入权限

x： 可执行权限

实例：

chmod u+w hh _//_ _添加用户所有者对hh文件的写入权限_

### 4.13 sed

格式：sed [选项] [命令] 文件名 _// 非交互式编辑器_

常用选项

-n： 取消默认输入

-e： 多项编辑

-i： 直接修改读取的档案内容，不显示

常用命令

a： 当前行后面添加行

i： 当前行前面添加行

c： 用字符串替代行

s： 用一个字符替代另一个字符

p： 将选择的数据印出，通常是和sed –n 一起使用的

例：

sed –n “2 s/root/hh/g” passwd _//将passwd文件的第二行里所有root替换成hh_

## 五. 获取帮助

### 5.1 man

格式： man [选项（或为空）][命令]

常用选项：

-M [路径] _//指定man手册页的搜索路径_

-a _//显示所有的手册页_

实例：

[root@localhost hh]#man pwd

### 5.2 help

格式： help [选项（或为空）][命令]

常用选项：

-d _//显示命令简短的主题描述_

-s _//显示命令简短的语法描述_

实例：

[root@localhost hh]#help pwd

## 六. vi文本编辑器命令

格式： vim [文件] _//进入vi编辑器编辑文档_

Shift ： _//编辑器内部操作语言_

例：

/set nu _//查看行序列号_

/nonu _//不看行序列号_

### 6.1 光标移动

操作类型操作键功能光标方向移动 上下左右翻页Page Down或Ctrl+F向下翻动一整页内容Page
up或Ctrl+B向上翻动一整页内容行内快速跳转Home键或“^”、数字“0”跳转至行首End键或“$”键跳转至行尾行间快速跳转
跳转至文件的首行G跳转至文件的末尾行#G跳转至文件中的第#行行号显示：set nu在编辑器中显示行号：set nonu在编辑器中不显示行号

![v2-56559fef0dbe190e7108fd69fd72288d_hd.j](https://pic2.zhimg.com/80/v2-56559fef0dbe190e7108fd69fd72288d_hd.jpg)

### 6.2 复制、粘贴、删除

操作类型操作键功能删除x或Del删除光标处的单个字符dd删除当前光标所在行#dd删除从光标开始的#行内容d^删除当前光标之前到行首的所有字符d&删除当前光标到末尾的所有字符复制yy复制当前行整行的内容至剪贴板#yy复制从光标处开始的#行内容粘贴p将缓冲区中的内容粘贴到光标所在位置后P粘贴到光标所在位置前

![v2-1ce0c0ccf99f7b8822a2fef6ffb45711_hd.j](https://pic2.zhimg.com/80/v2-1ce0c0ccf99f7b8822a2fef6ffb45711_hd.jpg)

### 6.3 文件内容查找

操作键功能/word从上而下在文件查找字符串”word”？word从下而上在文件中查找字符串“word”n定位下一个匹配的被查找字符串“word”N定位上一个匹配的被查找字符串“word”

![v2-0a5256a8fbb36724571b0286a25bf0ba_hd.j](https://pic3.zhimg.com/80/v2-0a5256a8fbb36724571b0286a25bf0ba_hd.jpg)

### 6.4 撤销编辑及保存退出

操作键功能u按一次取消最近的操作，多次重复按u键，恢复已进行的多步操作U用于取消对当前行所做的所有编辑ZZ保存当前的文件内容并退出vi编辑器

![v2-1bb6d1d0d9f2e8b759bae4ebad450951_hd.j](https://pic2.zhimg.com/80/v2-1bb6d1d0d9f2e8b759bae4ebad450951_hd.jpg)

### 6.5 保存文件及推出vi编辑器

操作类型操作键功能保存文件:w保存修改文件:w /root/newfile另存为其他文件退出vi：q未修改退出：q！放弃修改，并退出保存并退出vi：wq

![v2-8a1b21e9f38b7b525a76b4732dae80d3_hd.j](https://pic4.zhimg.com/80/v2-8a1b21e9f38b7b525a76b4732dae80d3_hd.jpg)

### 6.6 打开新文件或读入其他文件内容

操作键功能：e ~/install.log打开新的文件进行编辑:r /etc/filesystems在当前文件中读入其他文件内容

![v2-ec7a99923b9f6f9b5dfd0dd04613fbeb_hd.p](https://pic4.zhimg.com/80/v2-ec7a99923b9f6f9b5dfd0dd04613fbeb_hd.png)

### 6.7 文件内容替换

操作类型操作键：s /old/new将当前行中查找到的第一个字符“old”串替换为“new”: s
/old/new/g将当前行中查找到的所有字符串“old”替换为“new”:#,# s
/old/new/g在行号“#，#”范围内替换所有的字符串“old”为“new”:% s
/old/new/g在整个文件范围内替换所有的字符串“old”为“new”:s /old/new/c在替换命令末尾加入c

![v2-b5e80e419cb32203a46312a72df9711a_hd.j](https://pic3.zhimg.com/80/v2-b5e80e419cb32203a46312a72df9711a_hd.jpg)

今天的笔记就分享到这里，明天继续哦~

![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

  

