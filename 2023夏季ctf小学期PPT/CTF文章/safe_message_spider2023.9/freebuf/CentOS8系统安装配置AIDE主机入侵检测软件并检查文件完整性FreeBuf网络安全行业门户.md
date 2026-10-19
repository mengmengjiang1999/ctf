## **一、** ** **操作目的和应用场景****

###  **（一）** ** **目的****

CentOS 8系统安装配置aide入侵检测软件，并使用aide软件进行文件完整性检查。

###  **（二）** ** **简介****

1.作用

AIDE（Advanced Intrusion Detection Environment，高级入侵检测环境），主要用于检测文件的完整性。

2.原理

AIDE软件为系统文件生成初始的散列值数据库，然后每次执行检查命令时，aide会将之前生成的校验码和当前文件的校验码进行对比，并且输出报告，主要检查三类文件（修改过的，新增加的，删除的）。

AIDE数据库能够保存文件的各种属性，包括：权限(permission)、索引节点序号(inode
number)、所属用户(user)、所属用户组(group)、文档大小、最后修改时间(mtime)、创建时间(ctime)、最后访问时间(atime)等。AIDE还能够使用下列算法：sha1、md5、rmd160、tiger，以密文形式建立每个文件的校验码或散列值。

在系统安装完毕，要连接到网络上之前，系统管理员应该建立新系统的AIDE数据库。这第一个AIDE数据库是系统的一个快照和以后系统升级的准绳。数据库应该包含这些信息：关键的系统二进制可执行程序、动态连接库、头文件以及其它总是保持不变的文件。这个数据库不应该保存那些经常变动的文件信息，例如：日志文件、邮件、/proc文件系统、用户起始目录以及临时目录。

一旦发现系统被侵入，系统管理员可能会使用ls、ps、netstat以及who等系统工具对系统进行检查，但是所有这些工具都可能被特洛伊木马程序代替了。可以想象被修改的ls程序将不会显示任何有关入侵的文件信息，ps也不会显示任何入侵进程的信息。即使系统管理员已经把关键的系统文件的日期、大小等信息都打印到了纸上，恐怕也无法通过比较知道它们是否被修改过了，因为文件日期、大小等信息是非常容易改变的，一些比较好的rootkit可以很轻松地对这些信息进行假冒。

虽然文件的日期、大小等信息可能被假冒，但是假冒某个文件的一个散列值就非常困难了，更不要说假冒所有AIDE支持的散列值了。在系统被侵入后，系统管理员只要重新运行AIDE，就能够很快识别出哪些关键文件被攻击者修改过了。

不过，要注意这也不是绝对的，因为AIDE可执行程序的二进制文件本身可能被修改了或者数据库也被修改了。因此，应该把AIDE的数据库放到安全的地方，而且进行检查时要使用保证没有被修改过的程序。

tripwire也是入侵检测软件，但是操作比较复杂，aide可以替代tripwire。

##  **二、** ** **操作步骤****

###  **（一）** ** **安装**** ** **aide****

 **1、** **CentOS** ** **8系统安装aide****

    
    
    yum makecache  //更新软件列表
    
    yum install aide  //在线安装

 **2、** ** **查看aide版本和编译选项****

    
    
    aide -v

![1615171694_6045906eb362a29b1944f.png!small?1615171763612](https://image.3001.net/images/20210308/1615171694_6045906eb362a29b1944f.png!small?1615171763612)

通过查看AIDE的编译选项可了解当前安装的AIDE所支持的检查功能。

###  **（二）** ** **使用默认配置进行文件完整性检查****

 **1、** ** **创建新的数据库****

    
    
    aide --init  //生成包含文件系统中所有文件的数据库

![1615171879_60459127b30d78358991a.png!small?1615171949060](https://image.3001.net/images/20210308/1615171879_60459127b30d78358991a.png!small?1615171949060)

aideinit程序将按照/etc/aide.conf文件中DBDIR的配置，在下面位置创建新的数据库文件：

    
    
    /var/lib/aide/aide.db.new.gz

 **2、** ** **安装新的数据库****

    
    
    cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

 **3、** ** **手动使用**** ** **aide检查文件完整性****

    
    
    //默认会检查文件系统中的全部文件和目录，包括/proc这样的虚拟目录。
    
    aide -c /etc/aide.conf --check

![1615171908_604591445df52969dce00.png!small?1615171977219](https://image.3001.net/images/20210308/1615171908_604591445df52969dce00.png!small?1615171977219)

 **4、** ** **指定**** ** **aide的**** ** **检查范围****

    
    
    //只检查/bin目录中所发生的变化
    
    aide -c /etc/aide.conf --limit /bin --check

![1615171926_60459156cdbf66ed24a68.png!small?1615171996669](https://image.3001.net/images/20210308/1615171926_60459156cdbf66ed24a68.png!small?1615171996669)

###  **（三）** ** **使用自定义的配置进行文件完整性检查****

 **1、** ** **创建自定义配置文件****

    
    
    vi /home/user1/aide.conf  //编辑配置文件，加入下面的内容
    
    # 指定数据库创建的路径
    
    @@define DBDIR /var/lib/aide
    
    @@define LOGDIR /var/log/aide
    
    database=file:@@{DBDIR}/aide.db.gz
    
    database_out=file:@@{DBDIR}/aide.db.new.gz
    
    # 设置自定义的AIDE规则
    
    MYRULE = p+n+u+g+s+m+c+xattrs+md5+sha512
    
    # 指定被监视和并应用规则的目录/文件
    
    /etc MYRULE
    
    /bin MYRULE
    
    /usr/bin MYRULE
    
    # 指定排除哪些目录
    
    !/home
    
    !/proc
    
    !/run
    
    !/tmp
    
    保存退出
    
    说明：
    
    MYRULE = p+n+u+g+s+m+c+xattrs+md5+sha512的含义为：
    
    permissions, number of links, user, group, modification time, inode/file change time, extended file attributes, MD5checksum, SHA512checksum.

 **2、** ** **检查配置文件的合法性****

    
    
    aide -c /home/user1/aide.conf --config-check

![1615171972_604591843be7d181d48f1.png!small?1615172040805](https://image.3001.net/images/20210308/1615171972_604591843be7d181d48f1.png!small?1615172040805)

未返回错误信息，说明配置文件合法。

 **3、** ** **使用自定义配置文件生成新的数据库****

    
    
    aide --init -c /home/user1/aide.conf

![1615171990_6045919649af51cd15a8a.png!small?1615172059653](https://image.3001.net/images/20210308/1615171990_6045919649af51cd15a8a.png!small?1615172059653)

 **4、** ** **安装数据库****

    
    
    cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

![1615172007_604591a71fbc04e702f21.png!small?1615172075825](https://image.3001.net/images/20210308/1615172007_604591a71fbc04e702f21.png!small?1615172075825)

 **5、** ** **使用自定义配置检查文件完整性****

    
    
    aide -c /home/user1/aide.conf --check

![1615172021_604591b59f8bdcdc8c08e.png!small?1615172091184](https://image.3001.net/images/20210308/1615172021_604591b59f8bdcdc8c08e.png!small?1615172091184)

由于在被监视的目录中没有变化，所以检查结果显示文件系统和数据库之间没有差异。

使用下面的命令对文件系统进行操作：

    
    
    touch /bin/aide_test  //在被监视目录中创建文件
    
    touch /etc  //修改/etc目录的时间
    
    touch /home/aide_test1  //在被排除的目录中创建文件
    
    touch /usr/share/aide_test2  //在被监视和被排除的路径之外的目录中创建文件
    
    aide -c /home/user1/aide.conf --check  //再次进行完整性检查

![1615172033_604591c18e075af65c521.png!small?1615172102864](https://image.3001.net/images/20210308/1615172033_604591c18e075af65c521.png!small?1615172102864)

检测到在被监视路径中出现的新文件，以及目录的modify和change时间的变化。

以上说明aide可以使用自定义配置正常进行检测。

###  **（四）通过crontab** ** **自动检查文件完整性****

    
    
    crontab -e -u root  //编辑crontab，创建计划任务
    
    0 0 * * * aide -c /home/user1/aide.conf --check

保存退出。

这样，每个午夜的12点整都会自动进行完整性检查。

##  **三、** ** **参考**** ** **网址****

> https://kifarunix.com/install-and-configure-aide-on-ubuntu-18-04/

