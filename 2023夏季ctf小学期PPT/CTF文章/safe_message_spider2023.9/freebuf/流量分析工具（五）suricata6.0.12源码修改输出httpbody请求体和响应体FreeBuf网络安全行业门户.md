# suricata 6.0.12 源码修改输出 http body 请求体和响应体

## 一、简介

### 1\. 需求

最近有个使用suricata进行日志分析的需求，通过分析协议发现 suricata 对于http
的解析输出日志中，仅包含请求头和URL字段，不包含请求体和响应体的数据。

根据网上百度查到的信息，可以通过修改源码的方式增加suricata http 协议对于请求体和响应体输出。

此外，suricata中对于请求头和响应头的输出并不是标准的json格式，而是数组中存放单个字段的形式，这对于在 ES
中的检错来说，存在不便之处，所以也计划进行修改成 json 格式。

使用的源码是最新的 suricata-6.0.12，下载地址
<https://www.openinfosecfoundation.org/download/suricata-6.0.12.tar.gz>

参考链接 [suricata-输出http-json body](https://www.jianshu.com/p/abc8c7f3c833)

### 2\. 安装调试

centos7 安装 suricata-6.0.12 见文章[流量分析工具（二）：centos7 + suricata + redis +
ELK](https://www.freebuf.com/sectool/364203.html)

VS Code 调试 suricata 源码 见文章 [流量分析工具（三）：搭建 CentOS7 + vscode + suricata 6.0.12
源码修改调试环境](https://www.freebuf.com/sectool/368439.html)

## 二、修改源码

### 1\. 分析源码中的数据代码是如何写的

修改 suricata 对 http 协议的支持，主要是修改文件`src/output-json-http.c`

输出 http 的 json 数据的主函数是 `static void EveHttpLogJSON()`

    
    
    /* JSON format logging */
    static void EveHttpLogJSON(JsonHttpLogThread *aft, JsonBuilder *js, htp_tx_t *tx, uint64_t tx_id)
    {
    	LogHttpFileCtx *http_ctx = aft->httplog_ctx;
    	jb_open_object(js, "http");
    
    	EveHttpLogJSONBasic(js, tx);
    	/* log custom fields if configured */
    	if (http_ctx->fields != 0)
    		EveHttpLogJSONCustom(http_ctx, js, tx);
    	if (http_ctx->flags & LOG_HTTP_EXTENDED)
    		EveHttpLogJSONExtended(js, tx);
    	if (http_ctx->flags & LOG_HTTP_REQ_HEADERS)
    		EveHttpLogJSONHeaders(js, LOG_HTTP_REQ_HEADERS, tx);
    	if (http_ctx->flags & LOG_HTTP_RES_HEADERS)
    		EveHttpLogJSONHeaders(js, LOG_HTTP_RES_HEADERS, tx);
    
    	jb_close(js);
    }
    

输出 http 的 请求体明文数据的函数是 `void EveHttpLogJSONBodyPrintable(`

    
    
    void EveHttpLogJSONBodyPrintable(JsonBuilder *js, Flow *f, uint64_t tx_id)
    {
    	HtpState *htp_state = (HtpState *)FlowGetAppState(f);
    	if (htp_state) {
    		htp_tx_t *tx = AppLayerParserGetTx(IPPROTO_TCP, ALPROTO_HTTP, htp_state, tx_id);
    		if (tx) {
    			HtpTxUserData *htud = (HtpTxUserData *)htp_tx_get_user_data(tx);
    			if (htud != NULL) {
    				BodyPrintableBuffer(js, &htud->request_body, "http_request_body_printable");
    				BodyPrintableBuffer(js, &htud->response_body, "http_response_body_printable");
    			}
    		}
    	}
    }
    

输出 http 的 请求体 base64 数据的函数是 `void
EveHttpLogJSONBodyPrintable(`，base编码的目的是保持请求体中的乱码字符的完整性。因为
`http_request_body_printable`的输出结果中汉字等不可见字符全部都变成了
`...`，在特定场景中进行处理的时候会出现失真的情况，比如做响应体中xor异或密文的解密操作时会乱码。

    
    
    void EveHttpLogJSONBodyBase64(JsonBuilder *js, Flow *f, uint64_t tx_id)
    {
    	HtpState *htp_state = (HtpState *)FlowGetAppState(f);
    	if (htp_state) {
    		htp_tx_t *tx = AppLayerParserGetTx(IPPROTO_TCP, ALPROTO_HTTP, htp_state, tx_id);
    		if (tx) {
    			HtpTxUserData *htud = (HtpTxUserData *)htp_tx_get_user_data(tx);
    			if (htud != NULL) {
    				BodyBase64Buffer(js, &htud->request_body, "http_request_body");
    				BodyBase64Buffer(js, &htud->response_body, "http_response_body");
    			}
    		}
    	}
    }
    

### 2\. 修改整合源码中对http body的输出

  1. 修改代码函数 `static void EveHttpLogJSON()`，增加代码

    
    
    /* JSON format logging */
    static void EveHttpLogJSON(JsonHttpLogThread *aft, JsonBuilder *js, htp_tx_t *tx, uint64_t tx_id)
    {
        LogHttpFileCtx *http_ctx = aft->httplog_ctx;
        jb_open_object(js, "http");
    
        EveHttpLogJSONBasic(js, tx);
        /* log custom fields if configured */
        if (http_ctx->fields != 0)
            EveHttpLogJSONCustom(http_ctx, js, tx);
        if (http_ctx->flags & LOG_HTTP_EXTENDED)
            EveHttpLogJSONExtended(js, tx);
        if (http_ctx->flags & LOG_HTTP_REQ_HEADERS)
            EveHttpLogJSONHeaders(js, LOG_HTTP_REQ_HEADERS, tx);
        if (http_ctx->flags & LOG_HTTP_RES_HEADERS)
            EveHttpLogJSONHeaders(js, LOG_HTTP_RES_HEADERS, tx);
    
        if (tx) {
                HtpTxUserData *htud = (HtpTxUserData *)htp_tx_get_user_data(tx);
                if (htud != NULL) {
                    BodyPrintableBuffer(js, &htud->request_body, "http_request_body_printable");
                    BodyPrintableBuffer(js, &htud->response_body, "http_response_body_printable");
                    BodyBase64Buffer(js, &htud->request_body, "http_request_body");
                    BodyBase64Buffer(js, &htud->response_body, "http_response_body");
                }
            }
    
        jb_close(js);
    }
    

  2. 编译运行

    
    
    make
    make install
    suricata -i ens37 -c /etc/suricata/suricata.yaml -v -k none --runmode single
    

  3. 分析http协议数据

    
    
    {
      "timestamp": "2023-06-04T23:56:54.202013+0800",
      "flow_id": 1385525114442202,
      "in_iface": "ens37",
      "event_type": "http",
      "src_ip": "192.168.10.102",
      "src_port": 51045,
      "dest_ip": "1.192.193.244",
      "dest_port": 80,
      "proto": "TCP",
      "tx_id": 0,
      "ether": {
        "src_mac": "24:b6:fd:30:fc:2c",
        "dest_mac": "b0:f9:63:39:42:f7"
      },
      "community_id": "1:FDm7lQHSAlzpeSvPdsmj2Xbb/Vw=",
      "http": {
        "hostname": "c.skconf.f.360.cn",
        "url": "/commonquery",
        "http_content_type": "application/octet-stream",
        "http_method": "POST",
        "protocol": "HTTP/1.1",
        "status": 200,
        "length": 177,
        "request_headers": [
          {
            "name": "Host",
            "value": "c.skconf.f.360.cn"
          },
          {
            "name": "Accept",
            "value": "*/*"
          },
          {
            "name": "Connection",
            "value": "Keep-Alive"
          },
          {
            "name": "Cache-Control",
            "value": "no-cache"
          },
          {
            "name": "Content-Length",
            "value": "454"
          },
          {
            "name": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "response_headers": [
          {
            "name": "Server",
            "value": "nginx"
          },
          {
            "name": "Date",
            "value": "Fri, 03 Nov 2017 02:42:40 GMT"
          },
          {
            "name": "Content-Type",
            "value": "application/octet-stream"
          },
          {
            "name": "Transfer-Encoding",
            "value": "chunked"
          },
          {
            "name": "Connection",
            "value": "close"
          },
          {
            "name": "Cache-Control",
            "value": "no-cache"
          },
          {
            "name": "pragma",
            "value": "no-cache"
          }
        ],
        "http_request_body_printable": "..$!..g.9.......%...lZaR....:..`k..u.?.....g{...#-.z..s.N....JB....E.M.!....$d.`~.EWbA........N......([..+Wx4..fyO.;.q.b...y.8..N......JX..BD.,;n1....<=bS.5..xZ.'...b...s.nX9VM...l.......s....a..kl...5....../......H....>...*....B ..f...(....T..B...M...G..7.~M..6F..0zI..f...&......h.....Z...@8.\rk..AE..([).y..H.E.~?..i..L.:.....O..Wy..q...,.7.O....:O.k.u.U.p5.3qJ..QMr......v.W2.3.s%.....q.]+Q..W..bf.wbI.....!.k\r..=\r.945.gC.hp...*B........[..:..+..]..?f",
        "http_response_body_printable": "............!....I....m ...r.....<t...ee.K.O.A...]....-..\n...q.....4.N...@/#..~.w..+....n.....\n.......1$..@..7ORV.....C...$.ghJ_...|...Yy;!-..Gs}{m.0._..}...F.(..u..T..",
        "http_request_body": "DgYkIQUIZ505+QAACQC3fyWMx9xsWmFSu6MJCzqtf2BrjsN1pz+Hvw+P4Wd7G9PGIy30evLKcxxO+uafkkpC3NKqqUUATesh3/SejyRk+mB+7UVXYkECqogHq8HnrU7Aj88I4pYoW7vjK1d4NAK8ZnlPmjvccfNi0PK1eYI4pdVO9bCP/h62Sljuu0JEriw7bjGbmM+tPD1iU6M1ks54WhEnobguYpTirHO9blg5Vk3ApKVsyACdwsqxjXMLnQ65YZDja2z8iY411dCB3o/EL/QSy6XXgkiaBdXEPhj77CoYiuLfQiAA9maq/Oworwm6zVSI9EL61tVNrhPdR4CIN6V+TX/oNkYUBDB6SQnpZvCOjSYIpt+qqbto/7EarN9arKzRQDi3DWuVrEFFrOIoWykAecaPSAdFsn4/GxFp9wxMhDrt3Ymgnk8Y41d5mxlxD//fLLM3+U+VzQmMOk/wa9F1vlWlcDXlM3FKwB5RTXLyj8aeyYV2jFcy9jObcyUVq+Pp7XH3XStR3ohXp69iZvh3YknzhcbOGiHNaw3tpj0Nijk0NcVnQ4VocA7X1SpCAZYArObl+R9bntY6lfcrvBld1as/Zg==",
        "http_response_body": "EAYAAQaM04EAAAkQIef0gBdJ0s79DG0g2+EDcvmjHB27PHTNlR5lZalLvU+mQRjAiV3irtAALbTzCsijvXHjGaen/TSnThAEokAvI4/MfhJ3w5kr4RvQ5W7xpLTh+wqM89ujz9eVMSTG8ED+BDdPUlYEiRzKjkOSz6EkEWdoSl8uxcJ8mcOlWXk7IS2PsUdzfXtt5zC4X5zNfQKZE0auKPaBdb+bVMin"
      },
      "host": "127.0.0.1"
    }
    

![image](https://image.3001.net/images/20230605/1685953973_647d9db5f40db30b31685.png!small)

### 2\. 修改请求头和响应头的格式

分析输出的结果，发现请求头和请求体中的格式是 name 和 value 中单独存储的，如果数据存入到 elasticsearch
中之后，在通过查询语句统计聚合查询的时候，很多请求头的参数无法统计，所以还是需要进行一下简单的修改，可以做成json的格式进程存储。

  1. 修改源码

分析代码，原本是创建一个数组格式的对象`jb_open_array`，我们要改成json格式的对象`jb_open_object`。

原来的写法 `jb_set_string(js, "value", value);`我们改成 `jb_set_string(js, name,
value);`，意思是直接复制，不经过中间变量。

打印输出变量内容可以用这种 `SCLogNotice`函数。

    
    
    SCLogNotice("%s: %s", name, value);
    

千万记住，for 循环里面的 `jb_close(js);`已经要注释掉，否则在第一次循环解释之后 json 对象将会被关闭，进而无法全部输出完整的
请求头。

    
    
    # 源码文件 src/output-json-http.c
    static void EveHttpLogJSONHeaders(JsonBuilder *js, uint32_t direction, htp_tx_t *tx)
    {
        htp_table_t * headers = direction & LOG_HTTP_REQ_HEADERS ?
            tx->request_headers : tx->response_headers;
        char name[MAX_SIZE_HEADER_NAME] = {0};
        char value[MAX_SIZE_HEADER_VALUE] = {0};
        size_t n = htp_table_size(headers);
        jb_open_object(js, direction & LOG_HTTP_REQ_HEADERS ? "request_headers" : "response_headers");
        for (size_t i = 0; i < n; i++) {
            htp_header_t * h = htp_table_get_index(headers, i, NULL);
            if (h == NULL) {
                continue;
            }
            // jb_start_object(js);
    
            size_t size_name = bstr_len(h->name) < MAX_SIZE_HEADER_NAME - 1 ?
                bstr_len(h->name) : MAX_SIZE_HEADER_NAME - 1;
            memcpy(name, bstr_ptr(h->name), size_name);
            name[size_name] = '\0';
            // jb_set_string(js, "name", name);
    
            size_t size_value = bstr_len(h->value) < MAX_SIZE_HEADER_VALUE - 1 ?
                bstr_len(h->value) : MAX_SIZE_HEADER_VALUE - 1;
            memcpy(value, bstr_ptr(h->value), size_value);
            value[size_value] = '\0';
            // jb_set_string(js, "value", value);
    
            // 打印输出结果，进行调试分析
            // SCLogNotice("%s: %s", name, value);
            jb_set_string(js, name, value);
    		
    		// 这里一定要注释掉
            // jb_close(js);
        }
    
        // Close array.
        jb_close(js);
    
    }
    

  2. 编译运行

    
    
    make
    make install
    suricata -i ens37 -c /etc/suricata/suricata.yaml -v -k none --runmode single
    

  3. 分析http协议数据

    
    
    {
      "timestamp": "2023-06-05T02:03:03.674683+0800",
      "flow_id": 1284061303104653,
      "in_iface": "ens37",
      "event_type": "http",
      "src_ip": "10.10.10.1",
      "src_port": 59188,
      "dest_ip": "10.10.10.128",
      "dest_port": 80,
      "proto": "TCP",
      "tx_id": 4,
      "ether": {
        "src_mac": "00:50:56:c0:00:08",
        "dest_mac": "00:0c:29:97:c2:df"
      },
      "community_id": "1:Kn09jQgdaGwbtqPYDRuasuCu+IQ=",
      "http": {
        "hostname": "10.10.10.128",
        "url": "/noindex/css/fonts/Bold/OpenSans-Bold.ttf",
        "http_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "http_content_type": "text/html",
        "http_refer": "http://10.10.10.128/noindex/css/open-sans.css",
        "http_method": "GET",
        "protocol": "HTTP/1.1",
        "status": 404,
        "length": 238,
        "request_headers": {
          "Host": "10.10.10.128",
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
          "Accept": "application/font-woff2;q=1.0,application/font-woff;q=0.9,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
          "Accept-Encoding": "gzip, deflate",
          "Connection": "keep-alive",
          "Referer": "http://10.10.10.128/noindex/css/open-sans.css"
        },
        "response_headers": {
          "Date": "Sun, 04 Jun 2023 18:03:03 GMT",
          "Server": "Apache/2.4.6 (CentOS)",
          "Content-Length": "238",
          "Keep-Alive": "timeout=5, max=96",
          "Connection": "Keep-Alive",
          "Content-Type": "text/html; charset=iso-8859-1"
        },
        "http_response_body_printable": "<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\">\n<html><head>\n<title>404 Not Found</title>\n</head><body>\n<h1>Not Found</h1>\n<p>The requested URL /noindex/css/fonts/Bold/OpenSans-Bold.ttf was not found on this server.</p>\n</body></html>\n",
        "http_response_body": "PCFET0NUWVBFIEhUTUwgUFVCTElDICItLy9JRVRGLy9EVEQgSFRNTCAyLjAvL0VOIj4KPGh0bWw+PGhlYWQ+Cjx0aXRsZT40MDQgTm90IEZvdW5kPC90aXRsZT4KPC9oZWFkPjxib2R5Pgo8aDE+Tm90IEZvdW5kPC9oMT4KPHA+VGhlIHJlcXVlc3RlZCBVUkwgL25vaW5kZXgvY3NzL2ZvbnRzL0JvbGQvT3BlblNhbnMtQm9sZC50dGYgd2FzIG5vdCBmb3VuZCBvbiB0aGlzIHNlcnZlci48L3A+CjwvYm9keT48L2h0bWw+Cg=="
      },
      "host": "127.0.0.1"
    }
    

  4. 查看

![image](https://image.3001.net/images/20230605/1685953993_647d9dc928caef926803d.png!small)

### 3\. 修改请求体和响应体对中文的支持

  1. 修改源码

在 文件`src/output-json-http.c`中调用函数`static void
BodyPrintableBuffer(`，用是将字符串进行格式化处理。调用语句如下：

    
    
    PrintStringsToBuffer(printable_buf, &offset,
                                 sizeof(printable_buf),
                                 body_data, body_data_len);
    

跳转到对应的方法中。

修改文件 `src/util-print.c`中的函数 `void PrintStringsToBuffer(`。

分析代码，代码中使用三目运算符，判断缓冲区数据，如果是不可打印字符，则用 `.`替换。我们把三目运算符去掉。

    
    
    void PrintStringsToBuffer(uint8_t *dst_buf, uint32_t *dst_buf_offset_ptr, uint32_t dst_buf_size,
                              const uint8_t *src_buf, const uint32_t src_buf_len)
    {
        uint32_t ch = 0;
        for (ch = 0; ch < src_buf_len; ch++) {
            // PrintBufferData((char *)dst_buf, dst_buf_offset_ptr, dst_buf_size,
            //                 "%c",
            //                 (isprint((uint8_t)src_buf[ch]) ||
            //                 src_buf[ch] == '\n' ||
            //                 src_buf[ch] == '\r') ? (uint8_t)src_buf[ch] : '.');
            PrintBufferData((char *)dst_buf, dst_buf_offset_ptr, dst_buf_size,
                            "%c",
                            (uint8_t)src_buf[ch]);
    
    
        }
        dst_buf[dst_buf_size - 1] = 0;
    
        return;
    }
    

  2. 编译运行

    
    
    make
    make install
    suricata -i ens37 -c /etc/suricata/suricata.yaml -v -k none --runmode single
    

  3. 分析http协议数据

    
    
    {
      "timestamp": "2023-06-05T15:34:41.439990+0800",
      "flow_id": 2240940258471811,
      "in_iface": "ens33",
      "event_type": "http",
      "src_ip": "192.168.254.147",
      "src_port": 57110,
      "dest_ip": "192.168.254.82",
      "dest_port": 80,
      "proto": "TCP",
      "tx_id": 0,
      "http": {
        "hostname": "192.168.254.82",
        "url": "/123.html",
        "http_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "http_content_type": "text/html",
        "http_method": "POST",
        "protocol": "HTTP/1.1",
        "status": 200,
        "length": 130,
        "request_headers": {
          "Host": "192.168.254.82",
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
          "Accept-Encoding": "gzip, deflate",
          "Connection": "close",
          "Cookie": "sessionid=mzhv5wcmrskaaz4e8nl4dg80t5zahl5x",
          "Upgrade-Insecure-Requests": "1",
          "Content-Length": "51"
        },
        "response_headers": {
          "Date": "Mon, 05 Jun 2023 07:34:41 GMT",
          "Server": "Apache/2.4.6 (CentOS)",
          "Last-Modified": "Mon, 05 Jun 2023 07:34:14 GMT",
          "ETag": "\"82-5fd5cedf182b0\"",
          "Accept-Ranges": "bytes",
          "Content-Length": "130",
          "Connection": "close",
          "Content-Type": "text/html; charset=UTF-8"
        },
        "http_request_body": "5Y6G5Y+y5paH5YyW5piv5LiA5Liq5rCR5peP55qE57K+56We5YW75YiG5ZKM6aqo6auT",
        "http_response_body": "5Lit5Zu95paH5YyW5rqQ6L+c5rWB6ZW/77yM5Lit5Y2O5paH5piO5Y2a5aSn57K+5rex44CC6K6p5oiR5Lus5b6q552A5oC75Lmm6K6w55qE6K6y6L+w77yM5LiA6LW35L+d5oqk5aW95Lyg5om/5aW95Y6G5Y+y5paH5YyW44CCCg==",
        "http_request_body_printable": "历史文化是一个民族的精神养分和骨髓",
        "http_response_body_printable": "中国文化源远流长，中华文明博大精深。让我们循着总书记的讲述，一起保护好传承好历史文化。\n"
      }
    }
    

  4. 查看

![image](https://image.3001.net/images/20230605/1685954005_647d9dd56fed7ebb9225c.png!small)

### 4\. 调试删除日志中对于 fileinfo 的输出

  1. 修改源码

刚开始没找到 fileinfo
配置的参数开关，然后在源码里进行了注释操作。后来在配置文件中找到了对应的参数，所以此处的代码排查分析过程就仅用于记录和分析了。也没有删除。

下面的参数在配置文件中注释即可，如果不注释的话，eve.log 文件中会默认输出 `fileinfo`字段 。

    
    
    # - files:
    #     force-magic: yes   # force logging magic on all logged files
    #     # force logging of checksums, available hash functions are md5,
    #     # sha1 and sha256
    #     force-hash: [md5]
    

输出日志如下

    
    
    {
      "timestamp": "2023-06-05T15:16:09.392656+0800",
      "flow_id": 2194296840779430,
      "in_iface": "ens33",
      "event_type": "fileinfo",
      "src_ip": "192.168.254.82",
      "src_port": 80,
      "dest_ip": "192.168.254.147",
      "dest_port": 16367,
      "proto": "TCP",
      "http": {
        "hostname": "192.168.254.82",
        "url": "/123.html",
        "http_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "http_content_type": "text/html",
        "http_method": "POST",
        "protocol": "HTTP/1.1",
        "status": 200,
        "length": 73
      },
      "app_proto": "http",
      "fileinfo": {
        "filename": "/123.html",
        "sid": [],
        "gaps": false,
        "state": "CLOSED",
        "stored": false,
        "size": 73,
        "tx_id": 0
      }
    }
    

分析源码，查看文件`src/output-json-file.c`的方法`JsonBuilder
*JsonBuildFileInfoRecord(`，从代码顺序上看，和日志输出是保持一致的，先出现`app_proto`，然后是`fileinfo`，说明位置找对了。

    
    
    jb_set_string(js, "app_proto", AppProtoToString(p->flow->alproto));
    
        jb_open_object(js, "fileinfo");
        EveFileInfo(js, ff, stored);
        jb_close(js);
    
        /* xff header */
        if (have_xff_ip && xff_cfg->flags & XFF_EXTRADATA) {
            jb_set_string(js, "xff", xff_buffer);
        }
    
        return js;
    

跳转进去`EveFileInfo(js, ff, stored);`函数，可以简单看到里里面的字段也是符合日志输出的。

    
    
    void EveFileInfo(JsonBuilder *jb, const File *ff, const bool stored)
    {
        jb_set_string_from_bytes(jb, "filename", ff->name, ff->name_len);
    
        jb_open_array(jb, "sid");
        for (uint32_t i = 0; ff->sid != NULL && i < ff->sid_cnt; i++) {
            jb_append_uint(jb, ff->sid[i]);
        }
        jb_close(jb);
    
    #ifdef HAVE_MAGIC
        if (ff->magic)
            jb_set_string(jb, "magic", (char *)ff->magic);
    #endif
        jb_set_bool(jb, "gaps", ff->flags & FILE_HAS_GAPS);
        switch (ff->state) {
            case FILE_STATE_CLOSED:
                JB_SET_STRING(jb, "state", "CLOSED");
    #ifdef HAVE_NSS
                if (ff->flags & FILE_MD5) {
                    size_t x;
                    int i;
                    char str[256];
                    for (i = 0, x = 0; x < sizeof(ff->md5); x++) {
                        i += snprintf(&str[i], 255-i, "%02x", ff->md5[x]);
                    }
                    jb_set_string(jb, "md5", str);
                }
                if (ff->flags & FILE_SHA1) {
                    size_t x;
                    int i;
                    char str[256];
                    for (i = 0, x = 0; x < sizeof(ff->sha1); x++) {
                        i += snprintf(&str[i], 255-i, "%02x", ff->sha1[x]);
                    }
                    jb_set_string(jb, "sha1", str);
                }
    #endif
                break;
            case FILE_STATE_TRUNCATED:
                JB_SET_STRING(jb, "state", "TRUNCATED");
                break;
            case FILE_STATE_ERROR:
                JB_SET_STRING(jb, "state", "ERROR");
                break;
            default:
                JB_SET_STRING(jb, "state", "UNKNOWN");
                break;
        }
    
    #ifdef HAVE_NSS
        if (ff->flags & FILE_SHA256) {
            size_t x;
            int i;
            char str[256];
            for (i = 0, x = 0; x < sizeof(ff->sha256); x++) {
                i += snprintf(&str[i], 255-i, "%02x", ff->sha256[x]);
            }
            jb_set_string(jb, "sha256", str);
        }
    #endif
    
        if (stored) {
            JB_SET_TRUE(jb, "stored");
            jb_set_uint(jb, "file_id", ff->file_store_id);
        } else {
            JB_SET_FALSE(jb, "stored");
        }
    
        jb_set_uint(jb, "size", FileTrackedSize(ff));
        if (ff->end > 0) {
            jb_set_uint(jb, "start", ff->start);
            jb_set_uint(jb, "end", ff->end);
        }
        jb_set_uint(jb, "tx_id", ff->txid);
    }
    

我们看看这个方法`JsonBuilder *JsonBuildFileInfoRecord(`是在哪里调用的，找到这个方法`static void
FileWriteJsonRecord(`

    
    
    static void FileWriteJsonRecord(JsonFileLogThread *aft, const Packet *p,
                                    const File *ff, uint8_t dir)
    {
        HttpXFFCfg *xff_cfg = aft->filelog_ctx->xff_cfg != NULL ?
            aft->filelog_ctx->xff_cfg : aft->filelog_ctx->parent_xff_cfg;;
        JsonBuilder *js = JsonBuildFileInfoRecord(
                p, ff, ff->flags & FILE_STORED ? true : false, dir, xff_cfg, &aft->filelog_ctx->cfg);
        if (unlikely(js == NULL)) {
            return;
        }
    
        MemBufferReset(aft->buffer);
        OutputJsonBuilderBuffer(js, aft->file_ctx, &aft->buffer);
        jb_free(js);
    }
    

继续看 `static void FileWriteJsonRecord(`是在哪里调用的，然后就找到了 `static int
JsonFileLogger(`函数

    
    
    static int JsonFileLogger(ThreadVars *tv, void *thread_data, const Packet *p,
                              const File *ff, uint8_t dir)
    {
        SCEnter();
        JsonFileLogThread *aft = (JsonFileLogThread *)thread_data;
    
        BUG_ON(ff->flags & FILE_LOGGED);
    
        SCLogDebug("ff %p", ff);
    
        FileWriteJsonRecord(aft, p, ff, dir);
        return 0;
    }
    

然后我们这此把函数注释掉

    
    
    static int JsonFileLogger(ThreadVars *tv, void *thread_data, const Packet *p,
                              const File *ff, uint8_t dir)
    {
        // SCEnter();
        // JsonFileLogThread *aft = (JsonFileLogThread *)thread_data;
    
        // BUG_ON(ff->flags & FILE_LOGGED);
    
        // SCLogDebug("001 ff %p", ff);
    
        // FileWriteJsonRecord(aft, p, ff, dir);
        return 0;
    }
    

  2. 编译运行

    
    
    make
    make install
    suricata -i ens37 -c /etc/suricata/suricata.yaml -v -k none --runmode single
    

  3. 分析http协议数据

已经没有关于 `fileinfo`字段的相关输出到了。

    
    
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]# 
    [root@sensor suricata]# 
    [root@sensor suricata]# cat eve.json | grep fileinfo | jq
    [root@sensor suricata]#
    

