**Hello，大家好！在这篇文章中，我们将教大家如何使用KaliLinux的字典生成工具-Cewl。这是一份工具使用全指南，希望能给大家带来帮助！**

![1.png](https://image.3001.net/images/20181122/1542862403_5bf63643b86a9.png!small)

## Cewl介绍

Cewl是一款采用Ruby开发的应用程序，你可以给它的爬虫指定URL地址和爬取深度，还可以添额外的外部链接，接下来Cewl会给你返回一个字典文件，你可以把字典用到类似John
the Ripper这样的密码破解工具中。除此之外，Cewl还提供了命令行工具。

工具源地址：【[传送门](https://tools.kali.org/password-attacks/cewl)】

在终端输入“cewl -h”之后，工具会输出所有可接受的选项参数，以及对应的选项描述：

    
    
    SYNTAX:cewl <url> [options] 
    
    Genral Options
    
                    -h, –help:                               Show help.
    
                    -k, –keep:                              Keep the downloadedfile.
    
                    -d <x>,–depth<x>:        Depth to spider to,default 2.
    
                    -m, –min_word_length: Minimumword length, default 3.
    
                    -o, –offsite:                       Let the spider    visitother sites.
    
                    -w, –write:                         Write    the output tothe file.
    
                    -u, –ua <agent>:              User agent to send.
    
                    -n, –no-words:                                    Don’t outputthe wordlist.
    
                    –with-numbers:              Accept words with numbers in aswell as just letters
    
                    -a, –meta:                             include meta data.
    
                    –meta_file file:                                   Output file forMeta data.
    
                    -e, –email:                             Include emailaddresses.
    
                    –email_file <file>:           Output file for email addresses.
    
                    –meta-temp-dir <dir>: Thetemporary directory used by exiftool when parsing files, default /tmp.
    
                    -c, –count:                             Show the count foreach word found.
    
                    -v, –verbose:                    Verbose.
    
                    –debug:                                 Extra debuginformation
    
                    Authentication
    
                    –auth_type:                      Digest or basic. 
    
                    –auth_user:                      Authentication username.
    
                    –auth_pass:                      Authentication password.
    
                   Proxy Support
    
                    –proxy_host:                    Proxy host.
    
                    –proxy_port:                    Proxy port, default 8080.
    
                    –proxy_username:        Username for proxy, if required.
    
                    –proxy_password:         Password for proxy, if required.

![2.png](https://image.3001.net/images/20181122/1542862425_5bf6365971cb4.png!small)

### 默认方法

输入下列命令之后，爬虫会根据指定的URL和深度进行爬取，然后打印出可用于密码破解的字典：

    
    
    cewl http://www.ignitetechnologies.in/

![3.png](https://image.3001.net/images/20181122/1542862701_5bf6376d36860.png!small)

### 保存字典文件

为了方便大家记录，或者为将来的研究提供参考，Cewl可以将打印出的字典存储为文件。这里可以使用-w参数来将密码字典存储为text文件：

    
    
    cewl http://www.ignitetechnologies.in/ -w dict.txt

我们可以使用下列命令查看密码字典是否存储成功，我们的存储路径为/root /dict.txt：

    
    
    cat dict.txt

![4.png](https://image.3001.net/images/20181122/1542862737_5bf63791e1056.png!small)

### 生成特定长度的字典

如果你想生成指定长度的密码字典，你可以使用-m选项来设置：

    
    
    cewl http://www.ignitetechnologies.in/ -m 9

上述命令将生成长度至少为9位的密码，你可以从下图中看到，Cewl对目标网站进行了爬取，并打印出了长度至少为9位的密码：

![5.png](https://image.3001.net/images/20181122/1542862762_5bf637aaacd89.png!small)

### 从网站中获取Email

你可以使用-e选项来启用Email参数，并配合-n选项来隐藏工具在爬取网站过程中生成的密码字典：

    
    
    cewl http://www.ignitetechnologies.in/ -n -e

此时，工具成功在网站中发现了一个Email地址：

![6.png](https://image.3001.net/images/20181122/1542863019_5bf638ab3a797.png!small)

### 计算网站字典中重复的单词数量：

如果你想要计算目标网站中某个词的重复出现次数，你可以使用-c选项来开启参数计算功能：

    
    
    cewl http://www.ignitetechnologies.in/ -c

大家可以看到，Cewl可以直接统计出目标网站中重复的单词数量：

![7.png](https://image.3001.net/images/20181122/1542862997_5bf6389566826.png!small)

### 增加爬取深度

如果你想增加爬虫的爬取深度以生成更大的字典文件，你可以使用-d选项来指定爬取深度，默认的爬取深度为2：

    
    
    cewl http://www.ignitetechnologies.in/ -d 3

![8.png](https://image.3001.net/images/20181122/1542862977_5bf63881d01e6.png!small)

### 提取调试信息

你可以使用--debug选项来开启调试模式，这样就可以查看网站爬取过程中出现的错误和元数据了：

    
    
    cewl http://www.ignitetechnologies.in/ --debug

![9.png](https://image.3001.net/images/20181122/1542862959_5bf6386fc2d2c.png!small)

### Verbose模式

为了扩展网站爬取结果，并获取更加完整的数据报告，你可以使用-v选项来进入verbose模式。该模式下，Cewl会导出目标网站的详细数据：

    
    
    cewl http://www.ignitetechnologies.in/ -v

![10.png](https://image.3001.net/images/20181122/1542862932_5bf63854d9649.png!small)

### 生成包含数字和字符的字典

如果你想生成包含数字和字符的字典文件，你可以在命令中使用–with-numbers选项：

    
    
    cewl http://testphp.vulnweb.com/ --with-numbers

![11.png](https://image.3001.net/images/20181122/1542862909_5bf6383dcd89c.png!small)![12.png](https://image.3001.net/images/20181122/1542862910_5bf6383e0350d.png!small)

### Cewl摘要/基础认证

如果目标网站需要进行页面登录认证的话，我们就要使用下列参数来绕过页面认证的限制：

    
    
    –auth_type:                      Digest or basic.
    
    
    –auth_user:                     Authentication username.
    
    
    –auth_pass:                     Authentication password.
    
    
    cewl http://192.168.1.105/dvwa/login.php --auth_type Digest --auth_user admin--auth_pass password -v

或者

    
    
    cewl http://192.168.1.105/dvwa/login.php --auth_type basic --auth_user admin--auth_pass password -v

从下图中可以看到，接收到的http响应码为200，并成功生成了字典：

![13.png](https://image.3001.net/images/20181122/1542862883_5bf63823823b0.png!small)

### 代理URL

如果目标网站设置了代理服务器的话，Cewl将无法使用默认命令来生成字典。此时你需要使用–proxy option选项来启用代理URL功能：

    
    
    cewl --proxy_host 192.168.1.103 --proxy_port 3128 -w dict.txt http://192.168.1.103/wordpress/

![14.png](https://image.3001.net/images/20181122/1542862868_5bf6381483ca9.png!small)

## 总结

这是一份Kali Linux CeWL工具使用全指南，希望能给大家带来帮助！

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/comprehensive-guide-on-cewl-tool/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

