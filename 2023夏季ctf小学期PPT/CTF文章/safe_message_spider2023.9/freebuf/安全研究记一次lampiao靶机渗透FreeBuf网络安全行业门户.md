最近笔者整理各类靶机，发现部分靶机没有做过记录，因此借此对lampiao靶机渗透思路进行一次总结，以此完善笔记。

##  **过程记录**

一、

导入Lampiao靶机后选择NET模式

开启kali也选择NET模式

Kali的ip为 192.168.56.129

扫描C段寻找靶机地址

![OM7YKSAO_Sstt.png](https://image.3001.net/images/20210129/1611888911_6013790f8b1bd084a447e.png!small)

二、

发现靶机ip为 192.168.56.130

开启了22，80端口，访问80端口

![GpqKwJLq_pJXa.png](https://image.3001.net/images/20210129/1611888912_601379102c46f76234de1.png!small)

三、

没有可利用的信息，通过NMAP扫描主机开放的所有端口

![WBVd42D2_rhqC.png](https://image.3001.net/images/20210129/1611888913_60137911098ffc8deae6d.png!small)

四、

访问1898端口

  

![6x9H2Sac_uwuS.png](https://image.3001.net/images/20210129/1611888913_60137911e52651cd236a2.png!small)

五、

先对对目录进行扫描

![uAWYunkj_d6IF.png](https://image.3001.net/images/20210129/1611888914_60137912bc45505373402.png!small)

六、

通过扫描获取到了程序版本为Drupal 7.54

![2rWJZbnb_Gjfw.png](https://image.3001.net/images/20210129/1611888915_60137913c17e4dfabb624.png!small)

七、

以及存在目录遍历，但未找到可利用的信息

![ggaI8DFE_9VKf.png](https://image.3001.net/images/20210129/1611888916_601379142bdc4c2420768.png!small)

八、

安装文件存在，但需要删除已经存在的数据库才可以再次安装

![4ZhvnYv9_XXae.png](https://image.3001.net/images/20210129/1611888916_60137914cc6671965b3fd.png!small)

九、

通过其他思路尝试，所搜相关Drupal 7.54的漏洞，发现Drupal 7.x版本存在远程代码执行漏洞 Drupal core Remote Code
Execution(CVE-2018-7600) (Drupalgeddon2)

使用MSF搜索相关漏洞利用脚本

![47KSmD7z_EnN2.png](https://image.3001.net/images/20210129/1611888917_6013791539c085d207b80.png!small)

十、

选择第四项设置相关参数进行利用

![5RhG46YR_TPyx.png](https://image.3001.net/images/20210129/1611888921_601379190aac32eda539c.png!small)

十一、

获取到shell，权限较低需要提权，查看系统内核版本

![](https://image.3001.net/images/20210129/1611888921_60137919b2fb1973ed34e.png!small)

十二、

Linux为2016年7月更新，可以使用脏牛进行提权 CVE-2016-5195脏牛漏洞范围：Linux kernel>2.6.22
(2007年发行，到2016年10月18日才修复)

漏洞分析：

漏洞具体为，get_user_page内核函数在处理Copy-on-Write(以下使用COW表示)的过程中，可能产出竞态条件造成COW过程被破坏，导致出现写数据到进程地址空间内只读内存区域的机会。修改su或者passwd程序就可以达到root的目的。

Kali中自带了脏牛提权脚本，搜索文件并复制到根目录

脚本存放目录：

/usr/share/exploitdb/exploits/lnux/local/40847.cpp

![N48rm5Q7_PAGW.png](https://image.3001.net/images/20210129/1611888922_6013791a2f3b4d99a9947.png!small)

十三、

将脚本上传到靶机中，使用gcc编译，生成dcow在当前目录

g++ -Wall -pedantic -O2 -std=c++11 -pthread -o dcow 40847.cpp -lutil

参数含义：

1.-Wall 一般使用该选项，允许发出GCC能够提供的所有有用的警告

2.-pedantic 允许发出ANSI/ISO C标准所列出的所有警告

3.-O2编译器的优化选项的4个级别，-O0表示没有优化,-O1为缺省值，-O3优化级别最高

4.-std=c++11就是用按C++2011标准来编译的

5.-pthread 在Linux中要用到多线程时，需要链接pthread库

6.-o dcow gcc生成的目标文件,名字为dcow

![xyXdRrSF_Yx9p.png](https://image.3001.net/images/20210129/1611888923_6013791b0858c24a4b13b.png!small)

![wVCftKbh_2qj4.png](https://image.3001.net/images/20210129/1611888923_6013791b710ccd962988c.png!small)

十四、

使用puython开启交互式shell，并运行dcow提权

python -c ‘import pty; pty.spawn("/bin/bash")’

![wuqUTuvt_dTVj.png](https://image.3001.net/images/20210129/1611888924_6013791c4977b6e36e785.png!small)

最终、

通过脏牛提权已将管理密码重置为dirtyCowFun，获得root权限。

