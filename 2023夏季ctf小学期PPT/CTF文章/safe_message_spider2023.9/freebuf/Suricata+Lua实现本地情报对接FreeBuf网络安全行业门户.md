## 背景

 **由于近期网站遭受恶意攻击, 通过对于登录接口的审计与分析, 现已确定了一批可疑账号。既然之前写过一个登录接口的审计脚本,
那么完全可以通过扩展这个脚本来实现对于可疑账号的比对。主要思路: 通过将可疑账存进Redis中, 再利用Lua脚本调用Redis接口进行账号的比对。**

先说一下Suricata默认是存在黑名单机制的, 如下:

    
    
    # IP Reputation
    #reputation-categories-file: /etc/suricata/iprep/categories.txt
    #default-reputation-path: /etc/suricata/iprep
    #reputation-files:
    # - reputation.list

在Suricata
5.0版本中更是增加了新的功能[Datasets](https://suricata.readthedocs.io/en/suricata-5.0.0/rules/datasets.html)。大概看了一下,
可以通过在规则中使用dataset和datarep关键字将大量数据与sticky buffer进行匹配。确实是个很赞的功能!  

    
    
    alert http any any -> any any (http.user_agent; dataset:set, ua-seen, type string, save ua-seen.lst; sid:1;)
    alert dns any any -> any any (dns.query; to_sha256; dataset:set, dns-sha256-seen, type sha256, save dns-sha256-seen.lst; sid:2;)
    alert http any any -> any any (http.uri; to_md5; dataset:isset, http-uri-md5-seen, type md5, load http-uri-md5-seen.lst; sid:3;)

但是... 这并不适用我现在的场景。因为在我的场景中, 用户的登录请求存在于POST Body中,
默认的Suricata方法并不能准确定位到我们需要的账号。这个时候我们就只能依赖于Lua脚本来扩展。当然这些需求Zeek也可以满足,
只是...Zeek的脚本真是难写...主要是我技术太low~

## 准备阶段

### 运行环境

> OS:Ubuntu 18.04
>
> Suricata: Suricata 5.0.0 RELEASE (我是AWS的流量镜像, 必须使用4.1.5或者5.0版本, 因为要解析VXLAN)

### LuaRocks

1.由于Ubuntu默认没有安装[LuaRocks](https://luarocks.org/)(LuaRocks is the package
manager for Lua modules), 这里需要我们手动安装。

    
    
    # 通过apt直接安装, 简单省事儿。
    $ apt-get install luarocks  
    

2\. 通过`luarocks`安装我们所需要的`lua`模块, 这里我们需要用到`redis-lua`、`luasocket`这两个模块。

    
    
    # Install Modules
    $ luarocks install luasocket
    $ luarocks install redis-lua
    
    $ ll /usr/local/share/lua/5.1/
    total 72
    drwxr-xr-x 3 root root  4096 Oct 25 03:35 ./
    drwxr-xr-x 3 root root  4096 Sep 17 14:14 ../
    -rw-r--r-- 1 root root  8331 Oct 25 03:34 ltn12.lua
    -rw-r--r-- 1 root root  2487 Oct 25 03:34 mime.lua
    -rw-r--r-- 1 root root 35599 Oct 25 03:35 redis.lua
    drwxr-xr-x 2 root root  4096 Oct 25 03:34 socket/
    -rw-r--r-- 1 root root  4451 Oct 25 03:34 socket.lua  
    

3\. 安装成功后, 可以简单的测试一下。

3.1 利用 **Docker** 启动 **Redis** 容器

    
    
    $ docker run -ti -d -p 6379:6379 redis  
    

3.2 测试脚本 **hello_redis.lua**

    
    
    local redis = require "redis"
    
    local client = redis.connect("127.0.0.1", 6379)
    
    local response = client:ping()
    if response == false then
    	return 0
    end
    
    client:set("hello", "world")
    
    local var = client:get("hello")
    print(var)  
    

3.3 可能会存在环境变量不对导致的报错

    
    
    $ luajit hello_redis.lua
    	luajit: /usr/local/share/lua/5.1/redis.lua:793: module 'socket' not found:
    	no field package.preload['socket']
    	no file './socket.lua'
    	no file '/usr/local/share/luajit-2.0.5/socket.lua'
    	no file '/usr/local/share/lua/5.1/socket.lua'
    	no file '/usr/local/share/lua/5.1/socket/init.lua'
    	no file './socket.so'
    	no file '/usr/local/lib/lua/5.1/socket.so'
    	no file '/usr/local/lib/lua/5.1/loadall.so'
    stack traceback:
    	[C]: in function 'require'
    	/usr/local/share/lua/5.1/redis.lua:793: in function 'create_connection'
    	/usr/local/share/lua/5.1/redis.lua:836: in function 'connect'
    	a.lua:3: in main chunk
    	[C]: at 0x56508049e440  
    

3.4 执行 **luarocks path --bin** 并将结果输入

    
    
    $ luarocks path --bin
    Warning: The directory '/home/canon/.cache/luarocks' or its parent directory is not owned by the current user and the cache has been disabled. Please check the permissions and owner of that directory. If executing /usr/local/bin/luarocks with sudo, you may want sudo's -H flag.
    export LUA_PATH='/home/canon/.luarocks/share/lua/5.1/?.lua;/home/canon/.luarocks/share/lua/5.1/?/init.lua;/usr/local/share/lua/5.1/?.lua;/usr/local/share/lua/5.1/?/init.lua;./?.lua;/usr/local/share/luajit-2.0.5/?.lua'
    export LUA_CPATH='/home/canon/.luarocks/lib/lua/5.1/?.so;/usr/local/lib/lua/5.1/?.so;./?.so;/usr/local/lib/lua/5.1/loadall.so'
    export PATH='/home/canon/.luarocks/bin:/usr/local/bin:/home/canon/anaconda3/bin:/home/canon/anaconda3/condabin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin'  
    

3.5 执行脚本, 将会看到如下输出

    
    
    $ luajit hello_redis.lua
    world  
    

### CJson

这里建议大家使用CJson模块, 我之前为了测试随便从github上找了个json模块来使用。这几天发现在网站的高峰时期
Suricataapp_layer.flow这个字段非常的大, 从而导致了kernel_drops。由于我们的网站是面对海外用户想定位问题又存在时差,
经过几天的熬夜最终定位到是由于json模块太过于消耗性能而导致。可以看下这个截图:

a.Suricata监控图 -启用CJson模块之前

![](https://image.3001.net/images/20191104/1572838682_5dbf9d1aaa6d0.png!small)

b.Suricata监控图 -启用CJson模块之后

![](https://image.3001.net/images/20191104/1572838682_5dbf9d1aae289.png!small)

1.下载 CJson

    
    
    # wget 下载
    $ wget https://www.kyne.com.au/~mark/software/download/lua-cjson-2.1.0.tar.gz
    
    # Git Clone
    $ git clone git@github.com:mpx/lua-cjson.git  
    

2\. 根据Lua环境修改Makefile(个人配置)

    
    
    ##### Build defaults #####
    LUA_VERSION =       5.1
    TARGET =            cjson.so
    PREFIX =            /usr/local
    #CFLAGS =            -g -Wall -pedantic -fno-inline
    CFLAGS =            -O3 -Wall -pedantic -DNDEBUG
    CJSON_CFLAGS =      -fpic
    CJSON_LDFLAGS =     -shared
    LUA_INCLUDE_DIR =   $(PREFIX)/include/luajit-2.0
    LUA_CMODULE_DIR =   $(PREFIX)/lib/lua/$(LUA_VERSION)
    LUA_MODULE_DIR =    $(PREFIX)/share/lua/$(LUA_VERSION)
    LUA_BIN_DIR =       $(PREFIX)/bin  
    

3\. 安装 CJson

    
    
    $ make && make install

## 登录接口代码示例  

    
    
    json = require "cjson.safe"
    md5 = require "md5"
    redis = require "redis"
    
    -- 登录接口
    login_url = "/login" -- 根据实际接口而定
    -- 登录错误提示
    success_code = 0
    -- event_name
    event_name = "login_audit"
    -- event_type
    event_type = "lua"
    -- logs
    name = "login_audit.json"
    -- 协议
    proto = "TCP"
    
    -- redis_config
    host = "127.0.0.1"
    port = 6379
    
    -- common_mapping 通用请求头
    http_common_mapping = '{"accept":"accept","accept-charset":"accept_charset","accept-encoding":"accept_encoding","accept-language":"accept_language","user-agent":"user_agent"}'
    common_mapping_table = json.decode(http_common_mapping)
    
    -- request_mapping 自定义请求头
    http_request_mapping = '{"content-length":"request_content_length","content-type":"request_content_type"}'
    request_mapping_table = json.decode(http_request_mapping)
    
    -- response_mapping 自定义响应头
    http_response_mapping = '{"content-length":"response_content_length","content-type":"response_content_type"}')
    
    
    -- custom defind functioin
    function md5Encode(args)
        m = md5.new()
        m:update(args)
        return md5.tohex(m:finish())
    end
    
    function formatBody(args)
        t = {}
        ios = string.match(args, 'canon')
        if ios ~= nil then
            mail = 'email"%s+(.-)%s'
            t['email'] = string.match(args, mail)
        else
            data = string.split(args, '&')
            for n, v in ipairs(data) do
                d = string.split(v, '=')
                t[d[1]] = d[2]
            end
        end
        return t
    end
    
    function string.split(s, p)
        rt = {}
        string.gsub(s, '[^'..p..']+', function(w) table.insert(rt, w) end )
        return rt
    end
    
    -- default function
    function init (args)
        local needs = {}
        needs["protocol"] = "http"
        return needs
    end
    
    function setup (args)
        filename = SCLogPath() .. "/" .. name
        file = assert(io.open(filename, "a"))
        SCLogInfo("app_login_audit filename: " .. filename)
        http = 0
      
        -- Connect Redis Server 连接Redis服务器
        SCLogInfo("Connect Redis Server...")
        client = redis.connect(host, port)
        response = client:ping()
        if response then
            SCLogInfo("Redis Server connection succeeded.")
        end
    end
    
    function log(args)
        -- init tables
        http_table = {}
    
        -- ti tables
        ti = {
            tags = {}
        }
    
        -- init score 初始分数(为后期规则判断而准备, 符合规则进行加分。)
        score = 50
    
        -- http_hostname & http_url
        http_hostname = HttpGetRequestHost()
        http_url = HttpGetRequestUriNormalized()
        
        -- http_method
        rl = HttpGetRequestLine()
        if rl then
            http_method = string.match(rl, "%w+")
            if http_method then
                http_table["method"] = http_method
            end
        end
    	
        -- 为了保证 Suricata 的性能不受影响, 指定登录接口以及请求才能进入此逻辑。
        if http_url == login_url and http_method == "POST" then
            http_table["hostname"] = http_hostname
            http_table["url"] = http_url
            http_table["url_path"] = http_url
            
            -- http_status & http_protocol
            rsl = HttpGetResponseLine()
            if rsl then
                status_code = string.match(rsl, "%s(%d+)%s")
                http_table["status"] = tonumber(status_code)
    
                http_protocol = string.match(rsl, "(.-)%s")
                http_table["protocol"] = http_protocol
            end
    
            -- login_results
            a, o, e = HttpGetResponseBody()
            if a then
                for n, v in ipairs(a) do
                    body = json.decode(v)
                    results_code = tonumber(body["code"])
                    if results_code == success_code then
                        http_table["results"] = "success"
                    else
                        http_table["results"] = "failed"
                    end
                end
                http_table["results_code"] = results_code
            end
            
            --[[
                1. 获取用户登录email并查询Redis中是否存在该账号
                2. 根据结果进行相应的打分以及tags标注
            --]]
            a, o, e = HttpGetRequestBody()
            if a then
                for n, v in ipairs(a) do
                    res = formatStr(v)
                    if res["email"] then
                        -- 查询Redis对比黑名单
                        black_ioc = client:get(res["email"])
                        if black_ioc then
                            ti["provider"] = "Canon"
                            ti["producer"] = "NTA"
                            table.insert(ti["tags"], "account in blacklist")
                            score = score + 10
                        end
                    end
                end
            end
    
            -- RequestHeaders 根据自定义的请求头进行获取, 对于业务安全来说有些请求头还是有必要获取的。
            rh = HttpGetRequestHeaders()
            if rh then
                for k, v in pairs(rh) do
                    key = string.lower(k)
                    common_var = common_mapping_table[key]
                    if common_var then
                        http_table[common_var] = v
                    end
        
                    request_var = request_mapping_table[key]
                    if request_var then
                        http_table[request_var] = v
                    end
                end
            end
    
            -- ResponseHeaders 自定义获取响应头
            rsh = HttpGetResponseHeaders()
            if rsh then
                for k, v in pairs(rsh) do
                    key = string.lower(k)
                    common_var = common_mapping_table[key]
                    if common_var then
                        http_table[common_var] = v
                    end
            
                    response_var = response_mapping_table[key]
                    if response_var then
                        http_table[response_var] = v
                    end
                end
            end
    
            -- timestring
            sec, usec = SCPacketTimestamp()
            timestring = os.date("!%Y-%m-%dT%T", sec) .. '.' .. usec .. '+0000'
            
            -- flow_info
            ip_version, src_ip, dst_ip, protocol, src_port, dst_port = SCFlowTuple()
    
            -- flow_id
            id = SCFlowId()
            flow_id = string.format("%.0f", id)
            flow_id = tonumber(flow_id)
    
            -- alerts 查询这笔flow是否存在特征匹配后的告警
            has_alerts = SCFlowHasAlerts()
    
            -- true_ip
            true_client_ip = HttpGetRequestHeader("True-Client-IP")
            if true_client_ip ~= nil then
                src_ip = true_client_ip
            end
    
            -- session_id
            tetrad = src_ip .. src_port .. dst_ip .. dst_port
            session_id = md5Encode(tetrad)
    
            -- table
            raw_data = {
                timestamp = timestring,
                flow_id = flow_id,
                session_id = session_id,
                src_ip = src_ip,
                src_port = src_port,
                proto = proto,
                dest_ip = dst_ip,
                dest_port = dst_port,
                event_name = event_name,
                event_type = event_type,
                app_type = app_type,
                http = http_table,
                alerted = has_alerts,
                ti = ti,
                score = score
            }
    
            -- json encode
            data = json.encode(raw_data)
    
            file:write(data .. "\n")
            file:flush()
    
            http = http + 1
        end
    
    end
    
    function deinit (args)
        SCLogInfo ("app_login_audit transactions logged: " .. http);
        file:close(file)
    end

### 1\. 简单说下以上脚本的功能:

a.登录接口的用户名审计(废话…);

b.通过请求Redis比对当前用户是否在黑名单中, 并进行相应的打分、标签处理;

c.根据自定义的需求获取的http headers, 个人觉得这个对于业务安全上还是有点用的;

d. 新增字段"session_id", 主要考虑是针对CDN或者Nginx这种方向代理的场景下, 可以直接对 xff 或者 true_client_ip
进行四元组的hash, 得到session_id, 这样溯源的时候会比较方便。因为在这种场景下传统的四层flow_id就不是那么有用了。

e.后续可以追加一些简单的检测方法, 例如: (这些适用于我们, 其他的请头脑风暴)

> 检查请求头中的字段是否完整;
>
> 检查请求头中的某个字段长度是否符合合规;
>
> 头脑风暴...

### 2\. 配置Suricata启用Lua脚本

    
    
    - lua:
        enabled: yes
        scripts-dir: /etc/suricata/lua-output/
        scripts:
          - login_audit.lua

3\. 启动Suricata  

    
    
    $ suricata -vvv --pfring -k none -c /etc/suricata/suricata.yaml  
    

注: 这里`-vvv` 参数建议加上. 如果你的Lua脚本有一些问题, 如果加上了这个参数, 就可以通过这个日志看出。  

    
    
    $ tailf /data/logs/suricata/suricata.log
    4/11/2019 -- 02:22:25 - <Warning> - [ERRCODE: SC_ERR_PF_RING_VLAN(304)] - no VLAN header in the raw packet. See #2355.
    4/11/2019 -- 02:22:25 - <Warning> - [ERRCODE: SC_ERR_PF_RING_VLAN(304)] - no VLAN header in the raw packet. See #2355.
    4/11/2019 -- 02:22:25 - <Warning> - [ERRCODE: SC_ERR_PF_RING_VLAN(304)] - no VLAN header in the raw packet. See #2355.
    4/11/2019 -- 02:22:25 - <Warning> - [ERRCODE: SC_ERR_PF_RING_VLAN(304)] - no VLAN header in the raw packet. See #2355.
    4/11/2019 -- 02:22:25 - <Warning> - [ERRCODE: SC_ERR_PF_RING_VLAN(304)] - no VLAN header in the raw packet. See #2355.
    4/11/2019 -- 02:28:03 - <Info> - failed to run script: /usr/local/share/luajit-2.0.5/md5.lua:347: attempt to get length of local 's' (a nil value)  
    

## 输出日志样例  

    
    
    {
        "src_port": 62722,
        "score": 60,
        "session_id": "c863aeb2ef8d1b37f3257f8c210bf440",
        "ti": {
            "tags": [
                "account in blacklist"
            ],
            "provider": "Canon",
            "producer": "NTA"
        },
        "alert": {
            "alerted": true,
            "rules": {
                "请求头校验": "dev-id"
            }
        },
        "proto": "TCP",
        "flow_id": "1064295903559076",
        "timestamp": "2019-10-25T08:33:55.585519+0000",
        "event_type": "lua",
        "src_ip": "1.1.1.1",
        "dest_port": 80,
        "http": {
            "response_content_length": "96",
            "response_content_type": "application/json; charset=UTF-8",
            "accept_encoding": "gzip",
            "accept": "application/json",
            "results_code": 400504,
            "server": "nginx",
            "date": "Fri, 25 Oct 2019 08:33:55 GMT",
            "app_version": "6.6.0",
            "request_content_type": "application/x-www-form-urlencoded",
            "user_agent": "okhttp/3.12.0",
            "url": "/login",
            "email": "canon@gmail.com",
            "results": "failed",
            "pragma": "no-cache",-            "cache_control": "no-cache, max-age=0, no-store",
            "connection": "keep-alive",
            "status": 200,
            "protocol": "HTTP/1.1",
            "hostname": "x.x.x.x",
            "url_path": "/login",
            "method": "POST",
            "device": "RMX1920 Android8.0.0",
            "device_type": "Android",
            "request_content_length": "39"
        },
        "event_name": "login_audit",
        "dest_ip": "2.2.2.2"
    }  
    

![](https://image.3001.net/images/20191112/1573524230138.png!small)

 ***本文作者：Shell.，转载请注明来自FreeBuf.COM**

