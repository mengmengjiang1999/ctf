# suricata 6.0.12 alert 风险告警输出 http headers

## 一、简介

### 1\. 需求

最近有个使用suricata进行日志分析的需求，通过分析协议发现 suricata 对于http
的风险告警输出日志中，仅包含请求体和部分请求头，没有完整的请求头。

可以通过修改源码的方式增加http 的风险告警对于请求头和响应头的输出。

此外，suricata中对于请求头和响应头的输出并不是标准的json格式，而是数组中存放单个字段的形式，这对于在 ES
中的检索来说，存在不便之处，所以也计划进行修改成 json 格式。

使用的源码是最新的 suricata-6.0.12，下载地址
<https://www.openinfosecfoundation.org/download/suricata-6.0.12.tar.gz>

### 2\. 安装调试

centos7 安装 suricata-6.0.12 见 [文章流量分析工具（二）：centos7 + suricata + redis +
ELK](https://www.freebuf.com/sectool/364203.html)

VS Code 调试 suricata 源码 见文章 [流量分析工具（三）：搭建 CentOS7 + vscode + suricata 6.0.12
源码修改调试环境](https://www.freebuf.com/sectool/368439.html)

源码修改 http body 见 [流量分析工具（五）：suricata 6.0.12 源码修改输出 http body
请求体和响应体](https://www.freebuf.com/sectool/368546.html)

## 二、修改源码

### 1\. 分析源码中的数据代码是如何写的

修改 suricata 对 http 协议的支持，主要是修改文件`src/output-json-http.c`

输出 http 的 json 数据的主函数是 `static void EveHttpLogJSON()`

    
    
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
    

分析看到输出 http headers 主要是靠`EveHttpLogJSONHeaders(js, LOG_HTTP_REQ_HEADERS,
tx);`，其中传的参数`LOG_HTTP_REQ_HEADERS`的值要留意一下

    
    
    #define LOG_HTTP_REQ_HEADERS 8
    #define LOG_HTTP_RES_HEADERS 16
    

分析上面`EveHttpLogJSONHeaders(js, LOG_HTTP_REQ_HEADERS,
tx);`的代码，传入的参数，`js`是json的对象`JsonBuilder *js`，`tx`是`htp_tx_t *tx`类型的对象。

### 2\. 分析需要加入的位置

在分析告警中，输出 http body 的位置是在`src/output-json-alert.c`文件的 `static void
AlertAddAppLayer(`,我们可以紧接着 body 的位置追加一个 header 的字段。看一下 body 的是怎么写的

    
    
    static void AlertAddAppLayer(const Packet *p, JsonBuilder *jb,
            const uint64_t tx_id, const uint16_t option_flags)
    {
        const AppProto proto = FlowGetAppProtocol(p->flow);
        JsonBuilderMark mark = { 0, 0, 0 };
        switch (proto) {
            case ALPROTO_HTTP:
                // TODO: Could result in an empty http object being logged.
                jb_open_object(jb, "http");
                if (EveHttpAddMetadata(p->flow, tx_id, jb)) {
                    if (option_flags & LOG_JSON_HTTP_BODY) {
                        EveHttpLogJSONBodyPrintable(jb, p->flow, tx_id);
                    }
                    if (option_flags & LOG_JSON_HTTP_BODY_BASE64) {
                        EveHttpLogJSONBodyBase64(jb, p->flow, tx_id);
                    }
                }
                jb_close(jb);
                break;
    

根据上面的代码，分析发现`EveHttpLogJSONBodyBase64(jb, p->flow,
tx_id);`传入的参数，`jb`是`JsonBuilder *jb`类型的对象，`p->flow`是没有标明的，是`p`是`const Packet
*p`类型的，根据网络七层模型，我们猜测`p->flow`是网络流量数据分组中的数据流。`tx_id`是`const uint64_t
tx_id`类型的对象。

我们追踪进入`EveHttpLogJSONBodyBase64(jb, p->flow, tx_id);`函数中看一下，各个参数都干了啥

    
    
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
    

分析上面的代码，发现传入的`uint64_t tx_id`参数，在`EveHttpLogJSONBodyBase64(jb, p->flow,
tx_id);`函数内部有生成了 `htp_tx_t *tx`的数据，然后调用了 `BodyBase64Buffer(js,
&htud->request_body, "http_request_body");`函数，把具体数据放入到了json中。

### 3\. 分析并修改代码

根据上面的分析，发现了共同之处：

  1. 函数 `EveHttpLogJSONHeaders(js, LOG_HTTP_REQ_HEADERS, tx);`的代码，传入的参数，`tx`是`htp_tx_t *tx`类型的对象。

  2. 函数`EveHttpLogJSONBodyBase64(JsonBuilder *js, Flow *f, uint64_t tx_id)`的代码，内部生成了`htp_tx_t *tx`类型的对象。

所以，在`src/output-json-alert.c`文件的 `static void AlertAddAppLayer(`, 我们添加代码

    
    
    static void AlertAddAppLayer(const Packet *p, JsonBuilder *jb,
            const uint64_t tx_id, const uint16_t option_flags)
    {
        const AppProto proto = FlowGetAppProtocol(p->flow);
        JsonBuilderMark mark = { 0, 0, 0 };
        switch (proto) {
            case ALPROTO_HTTP:
                // TODO: Could result in an empty http object being logged.
                jb_open_object(jb, "http");
                if (EveHttpAddMetadata(p->flow, tx_id, jb)) {
                    if (option_flags & LOG_JSON_HTTP_BODY) {
                        EveHttpLogJSONBodyPrintable(jb, p->flow, tx_id);
                    }
                    if (option_flags & LOG_JSON_HTTP_BODY_BASE64) {
                        EveHttpLogJSONBodyBase64(jb, p->flow, tx_id);
                    }
    
    
                    HtpState *htp_state = (HtpState *)FlowGetAppState(p->flow);
                        if (htp_state) {
                            htp_tx_t *tx = AppLayerParserGetTx(IPPROTO_TCP, ALPROTO_HTTP, htp_state, tx_id);
                            if (tx) {
                                #define LOG_HTTP_REQ_HEADERS 8
                                #define LOG_HTTP_RES_HEADERS 16
                                EveHttpLogJSONHeaders(jb, (uint32_t )8, tx);
                                EveHttpLogJSONHeaders(jb, (uint32_t )16, tx);
                            }
                        }
    
    
                }
                jb_close(jb);
                break;
    

尝试进行编译

    
    
    make
    make install
    suricata -i ens37 -c /etc/suricata/suricata.yaml -v -k none --runmode single
    

发现报错了，提示说是跨文件调用没有声明函数，我们去头文件做一个声明。

    
    
    make  all-am
    make[1]: Entering directory `/opt/suricata-6.0.12/src'
      CC       output-json-alert.o
    output-json-alert.c: In function ‘AlertAddAppLayer’:
    output-json-alert.c:467:29: error: implicit declaration of function ‘EveHttpLogJSONHeaders’ [-Werror=implicit-function-declaration]
                                 EveHttpLogJSONHeaders(jb, (uint32_t )LOG_HTTP_REQ_HEADERS, tx);
                                 ^
    cc1: some warnings being treated as errors
    make[1]: *** [output-json-alert.o] Error 1
    make[1]: Leaving directory `/opt/suricata-6.0.12/src'
    make: *** [all] Error 2
    

参考 `EveHttpLogJSONBodyBase64(jb, p->flow, tx_id);`的声明方法，我们去查一下文件位置:

    
    
    [root@master src]# grep -rni "EveHttpLogJSONBodyBase64"
    output-json-http.h:31:void EveHttpLogJSONBodyBase64(JsonBuilder *js, Flow *f, uint64_t tx_id);
    output-json-alert.c:457:                    EveHttpLogJSONBodyBase64(jb, p->flow, tx_id);
    output-json-http.c:445:void EveHttpLogJSONBodyBase64(JsonBuilder *js, Flow *f, uint64_t tx_id)
    

发现头文件的位置是在`src/output-json-http.h`，新增一行

    
    
    bool EveHttpAddMetadata(const Flow *f, uint64_t tx_id, JsonBuilder *js);
    void EveHttpLogJSONBodyPrintable(JsonBuilder *js, Flow *f, uint64_t tx_id);
    void EveHttpLogJSONBodyBase64(JsonBuilder *js, Flow *f, uint64_t tx_id);
    void EveHttpLogJSONHeaders(JsonBuilder *js, uint32_t direction, htp_tx_t *tx);
    

继续编译，看看情况，这次提示声明函数 static 的问题，我们直接去`src/output-json-http.c`文件中把函数`void
EveHttpLogJSONHeaders(`的static删掉

    
    
    void EveHttpLogJSONHeaders(JsonBuilder *js, uint32_t direction, htp_tx_t *tx)
    {
        htp_table_t * headers = direction & LOG_HTTP_REQ_HEADERS ?
            tx->request_headers : tx->response_headers;
    

这次就编译通过了。

现在我们把格式规整一下，参考 `src/output-json-alert.c`中对请求体的调用，我们也增加 `if (option_flags &
`的形式

    
    
    # 第96行
    #define LOG_JSON_HTTP_HEADERS              BIT_U16(10)
    #define LOG_HTTP_REQ_HEADERS 8
    #define LOG_HTTP_RES_HEADERS 16
    
    
    # 第924行
    SetFlag(conf, "http-headers", LOG_JSON_HTTP_HEADERS, &flags);
    
    
    # 446行
    static void AlertAddAppLayer(const Packet *p, JsonBuilder *jb,
            const uint64_t tx_id, const uint16_t option_flags)
    {
        const AppProto proto = FlowGetAppProtocol(p->flow);
        JsonBuilderMark mark = { 0, 0, 0 };
        switch (proto) {
            case ALPROTO_HTTP:
                // TODO: Could result in an empty http object being logged.
                jb_open_object(jb, "http");
                if (EveHttpAddMetadata(p->flow, tx_id, jb)) {
                    if (option_flags & LOG_JSON_HTTP_BODY) {
                        EveHttpLogJSONBodyPrintable(jb, p->flow, tx_id);
                    }
                    if (option_flags & LOG_JSON_HTTP_BODY_BASE64) {
                        EveHttpLogJSONBodyBase64(jb, p->flow, tx_id);
                    }
    
                    // 添加代码并修改参数 js -> jb， 然后给增加判断条件
                    HtpState *htp_state = (HtpState *)FlowGetAppState(p->flow);
                        if (htp_state) {
                            htp_tx_t *tx = AppLayerParserGetTx(IPPROTO_TCP, ALPROTO_HTTP, htp_state, tx_id);
                            if (tx) {
                                if (option_flags & LOG_JSON_HTTP_HEADERS) {
                                    EveHttpLogJSONHeaders(jb, (uint32_t)LOG_HTTP_REQ_HEADERS, tx);
                                    EveHttpLogJSONHeaders(jb, (uint32_t)LOG_HTTP_RES_HEADERS, tx);
                                }
                            }
                        }
                }
                jb_close(jb);
                break;
    

去配置文件中增加一行

    
    
    # 第153行
    
          types:
            - alert:
                payload: no             # enable dumping payload in Base64
                # payload-buffer-size: 4kb # max size of payload buffer to output in eve-log
                payload-printable: yes   # enable dumping payload in printable (lossy) format
                packet: no              # enable dumping of packet (without stream segments)
                # metadata: no             # enable inclusion of app layer metadata with alert. Default yes
                http-body: no           # Requires metadata; enable dumping of HTTP body in Base64
                # http-body-printable: no # Requires metadata; enable dumping of HTTP body in printable format
                http-headers: no           # Requires metadata; enable dumping of HTTP body in Base64
    
                # Enable the logging of tagged packets for rules using the
                # "tag" keyword.
                tagged-packets: yes
    

### 4\. 修改请求头格式

修改请求头的格式并将字段改成小写

定位函数位置，文件`src/output-json-http.c`的函数`void EveHttpLogJSONHeaders(`

    
    
    void EveHttpLogJSONHeaders(JsonBuilder *js, uint32_t direction, htp_tx_t *tx)
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
            // 请求头和响应头改小写字母
            for(int i=0; i<(long)size_name; i++) {
                if(name[i] >= 'A' && name[i] <= 'Z') {
                    if (isupper(name[i])) {
                        name[i] = tolower(name[i]);
                    }
                } else if(name[i] == '-') {
                    name[i] = '_';
                }
            }
            // SCLogNotice("%s: %s", name, value);
            jb_set_string(js, name, value);
    
            // 一定要注释掉
            // jb_close(js);
        }
    
        // Close array.
        jb_close(js);
    
    }
    

### 5\. 分析结果

修改源码前

    
    
    types:
            - alert:
                payload: no             # enable dumping payload in Base64
                # payload-buffer-size: 4kb # max size of payload buffer to output in eve-log
                payload-printable: yes   # enable dumping payload in printable (lossy) format
                packet: no              # enable dumping of packet (without stream segments)
                # metadata: no             # enable inclusion of app layer metadata with alert. Default yes
                http-body: no           # Requires metadata; enable dumping of HTTP body in Base64
                # http-body-printable: no # Requires metadata; enable dumping of HTTP body in printable format
                http-headers: no           # Requires metadata; enable dumping of HTTP body in Base64
    

日志

    
    
    {
              "@timestamp": "2023-06-08T15:52:53.385447925Z",
              "dest_ip": "192.168.254.82",
              "event_type": "alert",
              "proto": "TCP",
              "flow_id": 1302691646395864,
              "app_proto": "http",
              "host": "suricata_sensor",
              "tags": [
                "suricata_alert",
                "_geoip_lookup_failure"
              ],
              "timestamp": "2023-06-08T15:52:53.383411+0800",
              "alert": {
                "signature": "HTTP request",
                "signature_id": 1,
                "action": "allowed",
                "category": "",
                "rev": 0,
                "gid": 1,
                "severity": 3
              },
              "ts": 1686210773385,
              "ether": {
                "src_mac": "00:e0:4c:e3:02:18",
                "dest_mac": "00:0c:29:97:c2:d5"
              },
              "in_iface": "ens33",
              "community_id": "1:6zSq0fKWZsow5761D9kjNJzxq1E=",
              "src_port": 28327,
              "http": {
                "http_content_type": "text/html",
                "status": 404,
                "url": "/123.js122",
                "length": 207,
                "http_request_body_printable": """1...................................................
    
    
    """,
                "protocol": "HTTP/1.1",
                "hostname": "192.168.254.82",
                "http_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "http_method": "POST",
                "http_response_body_printable": """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL /123.js122 was not found on this server.</p>
    </body></html>
    """
              },
              "tx_id": 0,
              "src_ip": "192.168.254.147",
              "dest_port": 80
            }
    

修改后

    
    
    types:
            - alert:
                payload: no             # enable dumping payload in Base64
                # payload-buffer-size: 4kb # max size of payload buffer to output in eve-log
                payload-printable: yes   # enable dumping payload in printable (lossy) format
                packet: no              # enable dumping of packet (without stream segments)
                # metadata: no             # enable inclusion of app layer metadata with alert. Default yes
                http-body: no           # Requires metadata; enable dumping of HTTP body in Base64
                # http-body-printable: no # Requires metadata; enable dumping of HTTP body in printable format
                http-headers: no           # Requires metadata; enable dumping of HTTP body in Base64
    

日志

    
    
    {
              "dest_ip": "192.168.254.82",
              "event_type": "alert",
              "proto": "TCP",
              "flow_id": 5985222840849,
              "app_proto": "http",
              "host": "suricata_sensor",
              "timestamp": "2023-06-08T16:02:28.384487+0800",
              "alert": {
                "signature": "HTTP request",
                "signature_id": 1,
                "action": "allowed",
                "category": "",
                "rev": 0,
                "gid": 1,
                "severity": 3
              },
              "community_id": "1:7YRQnHAPQy+izFYjEhKyJvkOPgg=",
              "src_port": 61221,
              "http": {
                "request_headers": {
                  "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                  "accept_language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                  "cookie": "sessionid=mzhv5wcmrskaaz4e8nl4dg80t5zahl5x",
                  "upgrade_insecure_requests": "1",
                  "accept_encoding": "gzip, deflate",
                  "host": "192.168.254.82",
                  "content_length": "58",
                  "connection": "close",
                  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
                },
                "http_content_type": "text/html",
                "response_headers": {
                  "date": "Thu, 08 Jun 2023 08:02:28 GMT",
                  "content_length": "207",
                  "content_type": "text/html; charset=iso-8859-1",
                  "connection": "close",
                  "server": "Apache/2.4.6 (CentOS)"
                },
                "status": 404,
                "url": "/123.js122",
                "length": 207,
                "protocol": "HTTP/1.1",
                "hostname": "192.168.254.82",
                "http_response_body_printable": """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL /123.js122 was not found on this server.</p>
    </body></html>
    """,
                "http_request_body_printable": """1...................................................
    
    
    """,
                "http_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
                "http_method": "POST"
              },
              "tx_id": 0,
              "src_ip": "192.168.254.147",
              "dest_port": 80
            }
          }
        ]
      }
    

