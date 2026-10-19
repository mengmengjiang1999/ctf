# 从一道CTF练习题浅谈php原生文件操作类

阅读量 **302031**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-05 11:32:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t016ac8e1137d73f7c7.jpg)

## 前言

记一次CTF练习有感,觉得需要记录一波…还有就是最近CTF比赛中利用php原生类来进行反序列化的题目比较多，所以就紧跟时代潮流…

## 一.SPL

顾名思义，SPL就是Standard PHP Library的缩写。据手册显示，SPL是用于解决`典型问题(standard
problems)`的一组接口与类的集合。打开[手册](http://php.net/manual/zh/book.spl.php)，正如上面的定义一样，有许多封装好的类。因为是要解决典型问题，免不了有一些处理文件的类。

![](https://p0.ssl.qhimg.com/t01bee8bac2ff16c1ec.png)

![](https://p1.ssl.qhimg.com/t010618caf6162af051.png)

###  一.可遍历目录类

`DirectoryIterator`

`FilesystemIterator`

`GlobIterator` 与上面略不同，该类可以通过模式匹配来寻找文件路径。

###  二.可读取文件类

`SplFileObject` 在此函数中，URL 可作为文件名，不过也要受到`allow_url_fopen`影响。

## 二.文件系统相关扩展

`finfo` 该类的构造函数`finfo::__construct` — 别名 `finfo_open()`,也可以读取文件。

![](https://p5.ssl.qhimg.com/t01f36a1cb5d6eb1fed.png)

## 三.例题

题目是websec上面的[第12关](https://websec.fr/level12/index.php)

![](https://p3.ssl.qhimg.com/t01f56b2a94463ddacb.png)

题目可以见源码就一句

    
    
    echo new [class]([first parameter],[second parameter]);
    

类的名字可控，类的参数可控，个数为二，题目说过滤了(实际可以绕过)上述提到的``splfileobject`, `globiterator`,
`filesystemiterator`,and `directoryiterator`等诸多函数，考虑使用`finfo`类,正好开了此拓展。

![](https://p4.ssl.qhimg.com/t0169cf1985c91e2179.png)

可以读到文件，但是`$key`未知

![](https://p5.ssl.qhimg.com/t01aac92211ddefb580.png)

关键代码大致如下：

    
    
    <?php
        ini_set('display_errors', 'on');
        ini_set('error_reporting', E_ALL);
        ....
        $key = ini_get ('user_agent');
        if ($_SERVER['REMOTE_ADDR'] === '127.0.0.1') {
             if ($_SERVER['HTTP_USER_AGENT'] !== $key) {
                 die ("Cheating is bad, m'kay?");
             }
        }
         $i = 0;
        $flag = '';
        foreach (str_split (base64_decode ($text)) as $letter) {
            $flag .= chr (ord ($key[$i++]) ^ ord ($letter));
        }
    

要想得到flag，则需要知道`php.ini`文件中的`user_agent`，尝试读取`php.ini`文件，路径未知，无果。

尝试使用`SplFileObject`访问VPS，得到服务器自身的user_agent。利用``绕过得到`user_agent`

![](https://p1.ssl.qhimg.com/t014aa63b473c555af9.png)

## 四.问题成因分析

调试一下为什么`finfo`会将文件信息（当然这一些都是建立在程序警告、报错消息开启的情况下

`ini_set('display_errors', 'on');ini_set('error_reporting', E_ALL);`）爆出来的原因。

编译过程就略过了，用的是php-7.0的源码。在`ext/fileinfo/fileinfo.c`文件的285行出下断点。也即`finfo_open`函数处

    
    
    /* {{{ proto resource finfo_open([int options [, string arg]])
       Create a new fileinfo resource. */
    PHP_FUNCTION(finfo_open)
    {
        zend_long options = MAGIC_NONE;
        char *file = NULL;
    

![](https://p2.ssl.qhimg.com/t01f61ef912690d4660.jpg)

`1.php`内容为:

    
    
    <?php
    ini_set('display_errors', 'on');
    ini_set('error_reporting', E_ALL);
    echo new finfo(1,'1.php')
    

忽略一些过渡的函数调用如`magic_load`->`file_apprentice`->`apprentice_1`->`apprentice_load`->`load_1`来到
`ext/fileinfo/apprentice.c`文件1025行处，也即`load_1`函数处

    
    
    /*
     * Load and parse one file.
     */
    private void
    load_1(struct magic_set *ms, int action, const char *fn, int *errs,#flag
       struct magic_entry_set *mset)
    {
        char buffer[BUFSIZ + 1];
        char *line = NULL;
        size_t len;
        size_t lineno = 0;
        struct magic_entry me;
    
        php_stream *stream;
    
    
        ms->file = fn;
        stream = php_stream_open_wrapper((char *)fn, "rb", REPORT_ERRORS, NULL);
    
        if (stream == NULL) {
            if (errno != ENOENT)
                file_error(ms, errno, "cannot read magic file `%s'",
                       fn);
            (*errs)++;
            return;
        }
    
        memset(&me, 0, sizeof(me));
        /* read and parse this file */
        for (ms->line = 1; (line = php_stream_get_line(stream, buffer , BUFSIZ, &len)) != NULL; ms->line++) {
            if (len == 0) /* null line, garbage, etc */
                continue;
            if (line[len - 1] == 'n') {
                lineno++;
                line[len - 1] = ''; /* delete newline */
            }
    

`php_stream_get_line`函数将`finfo`要读取的文件一行行读出

![](https://p4.ssl.qhimg.com/t01db317a7fb8cd5fd7.jpg)

随后将一行行内容进入`parse`函数进行解析，

    
    
            switch (parse(ms, &me, line, lineno, action)) {
                case 0:
                    continue;
                case 1:
                    (void)addentry(ms, &me, mset);
    

`parse`函数解析内容是否有效

    
    
    /*
     * parse one line from magic file, put into magic[index++] if valid
     */
    private int
    parse(struct magic_set *ms, struct magic_entry *me, const char *line,
        size_t lineno, int action)
    {
    

对于不符合magic文件内容格式的则会发出相应警告，从而一句句报出文件信息。

    
    
        file_magwarn(ms, "offset `%s' invalid", l);#1802行
        file_magwarn(ms, "type `%s' invalid", l);  #1950行
    

![](https://p2.ssl.qhimg.com/t01f812bdf288f42a7a.jpg)

## 五.后记：

上诉里面有一些东西只是简单提一下，希望能抛砖引玉。在一些情况下，如反序列化和其他某些特定场所，原生文件操作类也许能发挥不小的作用。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **myndtt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/167140](/post/id/167140)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PHP](/tag/PHP)
  * [代码安全](/tag/代码安全)

 **+1** __13赞

 __收藏

![](https://p2.ssl.qhimg.com/t011fe16ddec650cf81.png) myndtt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

