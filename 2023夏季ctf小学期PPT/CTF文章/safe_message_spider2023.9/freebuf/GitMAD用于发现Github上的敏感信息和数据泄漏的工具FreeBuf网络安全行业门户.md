**GitMAD是一个用于发现Github上的敏感信息和数据泄漏的工具。通过给定关键字或域，GitMAD便会搜索Github上托管的代码，以查找是否存在匹配项。一旦找到了匹配项，GitMAD将克隆存储库并在文件中搜索一系列可配置的正则表达式。然后，GitMAD会获取这些结果，并将它们插入到数据库中供后续的查看使用。这些结果也可作为邮件警报发送。另外，GitMAD将持续运行以发现与输入关键字匹配的新存储库。**

## 输入

除此之外，用户还可以配置每次搜索的最大结果量，搜索间隔时间以及要克隆的存储库的大小范围。有两种模式，Monitor和Discovery。Discovery模式将在每次运行时提取并搜索新结果。Monitor模式则会首先下载给定关键字/域的所有匹配项搜索它们，然后继续搜索新结果。

## 处理

GitMAD从上面获取结果并搜索存储库的Git历史记录。
搜索历史记录以查找一组可配置的正则表达式。GitMAD还可以对历史文件的每一行进行分解，并在信息熵（Shannon entropy）中搜索匹配项。

## 配置文件

### regex_matches.py

这是将关键字和正则表达式放在存储库内容中进行搜索的位置，只需在下面的列表中添加字典即可：

    
    
    to_match = [
        {'match_regex': r'password', 'match_type': 'Password Match'},
        {'match_regex': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'match_type': 'IP Match'},
        {'match_regex': r'username', 'match_type': 'Username Match'},
        {'match_regex': r'\b[\w.]*@[\w]*\.[\w.]*\b', 'match_type': 'Email Match'}
        ]

### entropy_whitelist.py

这是移除Entropy功能匹配你不想要的项目位置。只需在下面的列表中添加字典即可：

    
    
    r_whitelist = [{'regex':r'\b[A-Za-z][a-z]+([A-Z][a-z]*)+\b'}] # Camel Case

## 输出

GitMAD获取上面的结果，并将它们插入到一个数据库中，该数据库包含有关找到匹配项的文件以及存储库的信息。它还插入了匹配的字符串和匹配的行。这些结果可通过邮件警报，数据库和Web应用获得。

## 当前状态

该项目正在积极开发中。

## 安装

GitMAD最初是在Windows上用Python3.6编写的。它也在Ubuntu 18.04上进行了测试。

 **环境要求**

> Python 3.6+
>
> Pip for Python3
>
> Git
>
> MySQL 8.0

如果是Windows系统你可以直接从Oracle网站下载MySQL8.0。如果是Ubuntu 18.04，其默认版本仍为5.7，因此你必须升级你的当前版本：

    
    
    wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.12-1_all.deb 
    sudo dpkg -i mysql-apt-config_0.8.12-1_all.deb
    #select version 8.0
    sudo apt update 
    sudo apt install mysql-server
    sudo mysql_secure_installation

 **Ubuntu 18.04 安装步骤**

1）克隆存储库并进入到目录：

    
    
    git clone https://github.com/deepdivesec/GitMAD.git
    cd GitMAD

2）安装依赖项：

    
    
    pip3 install -r requirements.txt

3）向MySQL添加脚本：

    
    
    $sudo mysql -u username -p
    mysql> source /<path-to-gitmad>/GitMAD/github_search_db.sql

4）运行main.py并在首次运行时输入配置信息：

    
    
    python3 /<path-to-gitmad>/GitMAD/main.py -q <keyword-to-search> [see other options below]

![gitmad-help.png](https://image.3001.net/images/20190722/1563752030_5d34f65eac5f0.png!small)

5）运行Web应用：

    
    
    python3 /<path-to-gitmad>/GitMAD/web_home.py

6）（可选）下载并安装[MySQL
Workbench](https://dev.mysql.com/downloads/workbench/)与结果直接进行交互。

Ubuntu安装动图请在[此处](https://github.com/deepdivesec/GitMAD/tree/master/GitMAD-install)查看。

## 已知问题

有时，无论存储库的大小如何，GitHub API都会返回0。该问题尚未处理，而被克隆的存储库大于-mx/--max的大小这个问题，正在处理中。

***参考来源：[GitHub](https://github.com/deepdivesec/gitmad)，FB小编secist编译，转载请注明来自FreeBuf.COM**

