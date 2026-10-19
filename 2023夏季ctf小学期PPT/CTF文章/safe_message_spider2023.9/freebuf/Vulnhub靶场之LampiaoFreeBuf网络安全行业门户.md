## 一、环境搭建

lampiao靶场下载地址：[https](https://download.vulnhub.com/lampiao/Lampiao.zip):[//download.vulnhub.com/lampiao/Lampiao.zip](https://download.vulnhub.com/lampiao/Lampiao.zip)

使用vm打开，配置kali和靶场处于同一个网络，建议都为nat

## 二、信息收集

### 1、nmap扫描

使用namp扫描整个网段，找到靶场ip地址

![1603639829_5f959a152789423abbe07.png!small?1603639829221](https://image.3001.net/images/20201025/1603639829_5f959a152789423abbe07.png!small?1603639829221)

使用namp进一步扫描，扫出更多的信息

![1603640394_5f959c4ac6cb63cd1851b.png!small?1603640395080](https://image.3001.net/images/20201025/1603640394_5f959c4ac6cb63cd1851b.png!small?1603640395080)

### 2、访问页面

访问靶机的80端口，发现是一个静态网页，什么都没有![1603640416_5f959c60dcd1cd797cae1.png!small?1603640417000](https://image.3001.net/images/20201025/1603640416_5f959c60dcd1cd797cae1.png!small?1603640417000)

使用御剑扫描目录，没扫到

![1603643250_5f95a7722c98b01a5a456.png!small?1603643249867](https://image.3001.net/images/20201026/1603643250_5f95a7722c98b01a5a456.png!small?1603643249867)

访问下1898端口试试看

![1603640521_5f959cc9b045f3b746e79.png!small?1603640521649](https://image.3001.net/images/20201025/1603640521_5f959cc9b045f3b746e79.png!small?1603640521649)

使用谷歌插件检测出来cms是drupal7

使用dirscan扫描目录进一步信息收集

![1603642857_5f95a5e991d74dae8f2f4.png!small?1603642857409](https://image.3001.net/images/20201026/1603642857_5f95a5e991d74dae8f2f4.png!small?1603642857409)

CHANGELOG.txt可能是更新日志，访问一下看看

![1603643050_5f95a6aa9e16a895f75e2.png!small?1603643050841](https://image.3001.net/images/20201026/1603643050_5f95a6aa9e16a895f75e2.png!small?1603643050841)

可以看到cms的版本更新到Drupal 7.54了，百度看看这个版本的Drupal有没有已知漏洞

![1604128914_5f9d1092b21c169d687d4.png!small?1604128915338](https://image.3001.net/images/20201031/1604128914_5f9d1092b21c169d687d4.png!small?1604128915338)

## 三、漏洞利用

### Drupal核心远程代码执行漏洞CVE-2018-7600

使用msf的search发现存在Drupal核心远程代码执行漏洞CVE-2018-7600，使用msf攻击

![1604142563_5f9d45e3ec7409ec59aa4.png!small?1604142564669](https://image.3001.net/images/20201031/1604142563_5f9d45e3ec7409ec59aa4.png!small?1604142564669)

![1604142616_5f9d46188f3dca20f20a2.png!small?1604142617212](https://image.3001.net/images/20201031/1604142616_5f9d46188f3dca20f20a2.png!small?1604142617212)

连接成功，查看以下数据库密码

![1604142741_5f9d4695d1618b53c92f3.png!small?1604142742455](https://image.3001.net/images/20201031/1604142741_5f9d4695d1618b53c92f3.png!small?1604142742455)

![1604142774_5f9d46b6631ce92af789e.png!small?1604142775076](https://image.3001.net/images/20201031/1604142774_5f9d46b6631ce92af789e.png!small?1604142775076)

查看以下用户目标主机用户

![1604142807_5f9d46d72cc6ebf86245a.png!small?1604142807879](https://image.3001.net/images/20201031/1604142807_5f9d46d72cc6ebf86245a.png!small?1604142807879)

使用此用户和数据库密码进行ssh登入，这是靶场的套路。。。。

**![1604142943_5f9d475fd46e68e923aa2.png!small?1604142944519](https://image.3001.net/images/20201031/1604142943_5f9d475fd46e68e923aa2.png!small?1604142944519)**

## 四、权限提升

### 使用脏牛提权

![1604143315_5f9d48d3e3abb072da598.png!small?1604143316631](https://image.3001.net/images/20201031/1604143315_5f9d48d3e3abb072da598.png!small?1604143316631)

将40847.cpp拷贝到用户目录，然后复制到真机上，全选复制

![1604143401_5f9d492929a71305aa434.png!small?1604143401809](https://image.3001.net/images/20201031/1604143401_5f9d492929a71305aa434.png!small?1604143401809)

在ssh连接中使用vim dirtycow.cpp 创建一个.cpp文件，将复制40847.cpp的内容粘贴过来，保存

![1604143549_5f9d49bd9e375ea710b84.png!small?1604143550230](https://image.3001.net/images/20201031/1604143549_5f9d49bd9e375ea710b84.png!small?1604143550230)

编译cpp文件，命令：g++ -Wall -pedantic -O2 -std=c++11 -pthread -o dcow dirtycow.cpp
-lutil

![1604143714_5f9d4a62df8ebac8bf4a3.png!small?1604143715654](https://image.3001.net/images/20201031/1604143714_5f9d4a62df8ebac8bf4a3.png!small?1604143715654)

命令解释：

  * -Wall 一般使用该选项，允许发出GCC能够提供的所有有用的警告
  * -pedantic 允许发出ANSI/ISO C标准所列出的所有警告

  * -O2编译器的优化选项的4个级别，-O0表示没有优化,-O1为缺省值，-O3优化级别最高

  * -std=c++11就是用按C++2011标准来编译的 

  * -pthread 在Linux中要用到多线程时，需要链接pthread库

  * -o 指定gcc生成的目标文件名

![1604143862_5f9d4af6a36d92e4bf5ab.png!small?1604143863363](https://image.3001.net/images/20201031/1604143862_5f9d4af6a36d92e4bf5ab.png!small?1604143863363)

执行dirtycow文件提升权限，得到flag.txt

