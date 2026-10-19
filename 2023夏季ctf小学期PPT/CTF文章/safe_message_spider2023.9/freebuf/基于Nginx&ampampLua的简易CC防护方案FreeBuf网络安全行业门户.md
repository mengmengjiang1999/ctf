## 前言

CC攻击(ChallengeCollapsar)是常见网站应用层攻击的一种，目的是消耗服务器资源，降低业务响应效率；极端情况会让站点无法正常提供服务。本文旨在描述如何通过ngx_lua模块开发并集成基于令牌桶算法的简易IP限速功能，实现CC攻击的防护。

## 一、服务部署

###  0.环境

a.系统

CentOSLinux release 7.5.1804 (Core)；

b.资源存放目录

mkdir/root/ngx_lua

c.要求

各种编译安装相关依赖和报错请google解决；

d.NGX_LUA官文

<https://github.com/openresty/lua-nginx-module#installation>

e.准备

cd/root/ngx_lua

###  1.Lua

wget<http://www.lua.org/ftp/lua-5.3.4.tar.gz>

tarzxf lua-5.3.4.tar.gz

cdlua-5.3.4

makelinux test

cd..

###  2.LuaJIT2.1

wget<http://luajit.org/download/LuaJIT-2.1.0-beta3.tar.gz>

tarzxvf LuaJIT-2.1.0-beta3.tar.gz

cdLuaJIT-2.1.0-beta3

#指定安装目录

makePREFIX=/usr/local/luajit2

makeinstall PREFIX=/usr/local/luajit2

cd..

###  3.NDK

wget<https://github.com/simplresty/ngx_devel_kit/archive/v0.3.1rc1.tar.gz>

tarzxvf v0.3.1rc1.tar.gz

###  4.LUA_NGX

wget<https://github.com/openresty/lua-nginx-module/archive/v0.10.13.tar.gz>

tarzxvf v0.10.13.tar.gz

###  5.LUA_RESTY_REDIS

wget-O "lua-resty-redis-master.zip"<https://codeload.github.com/openresty/lua-resty-redis/zip/master>

unziplua-resty-redis-master.zip

cdlua-resty-redis-master

makeinstall PREFIX=/usr/local/lua-redis

cd..

###  6.REDIS

wget<http://download.redis.io/releases/redis-4.0.9.tar.gz>

tarzxvf redis-4.0.9.tar.gz

cdredis-4.0.9

  

#复制配置文件模板

cpredis.conf /etc/

#编译安装

makePREFIX=/usr/local/redis

makeinstall PREFIX=/usr/local/redis

#尝试运行，可以考虑打包为后台服务或托管给supervisor，本文略；

cd/usr/local/redis/bin

./redis-server/etc/redis.conf

###  7.Nginx

#添加NGINX 用户

useradd-s /sbin/nologin www

#下载、解压并进入目录

wget<http://nginx.org/download/nginx-1.13.12.tar.gz>

tarzxvf nginx-1.13.12.tar.gz

cdnginx-1.13.12

#增加环境变量

exportLUAJIT_LIB=/usr/local/luajit2/lib

exportLUAJIT_INC=/usr/local/luajit2/include/luajit-2.1

#编译安装

./configure--user=www --group=www --prefix=/usr/local/nginx --with-http_stub_status_module--with-http_gzip_static_module --with-http_sub_module
--with-ld-opt="-Wl,-rpath,/usr/local/luajit2/lib"--add-dynamic-module=/root/ngx_lua/ngx_devel_kit-0.3.1rc1--add-dynamic-module=/root/ngx_lua/lua-nginx-module-0.10.13

make&& make test

#编辑主配置文件使其支持NGX_LUA

vim/usr/local/nginx/conf/nginx.conf

#指定为其创建的用户

userwww www;

#指定进程数及将进程绑定至CPU核心；

worker_processes auto;

worker_cpu_affinityauto;

pid logs/nginx.pid;

#打开文件数

worker_rlimit_nofile 65535;

#此处加载LUA相关模块

load_modulemodules/ndk_http_module.so;

load_modulemodules/ngx_http_lua_module.so;

events{

useepoll;

worker_connections 65535;

accept_mutexoff;

multi_accepton;

}

http{

include mime.types;

default_type application/octet-stream;

server_names_hash_bucket_size 128;

client_header_buffer_size 64k;

large_client_header_buffers4 32k;

client_max_body_size 512m;

#lua redis 依赖包

lua_package_path"/usr/local/lua-redis/lib/lua/?.lua;;";

sendfile on;

keepalive_timeout 60;

server_tokens off;

log_formataccess '$remote_addr - $remote_user [$time_local] "$request" '

'$status $body_bytes_sent"$http_referer" '

'"$http_user_agent""$http_x_forwarded_for"';

includeconf.d/*.conf;

}

:wq

nginx-t && nginx

## 二、开发LUA响应体及建立VHOST

###  1.建立lua脚本存放目录

mkdir/usr/local/nginx/conf/lua

###  2.开发用于响应内容的lua脚本

vim/usr/local/nginx/conf/lua/content.lua

\--获取请求的HEADER

localheaders = ngx.req.get_headers()

\--依次通过x_real_ip，x_forwarded_for，remote_addr获取客户端IP

localclientip = headers["X-Real-IP"]

ifclientip == nil then

clientip =headers["x_forwarded_for"]

end

ifclientip == nil then

clientip = ngx.var.remote_addr

end

\--指定响应内容

ngx.say("YourIp Adress is ",clientip,", WelCome!")

:wq

###  3.搭建用于测试的VHOST

a.新建配置文件

vim/usr/local/nginx/conf/conf.d/luatest.conf

server

{

#指定监听端口及主机名

listen80;

server_name[www.knownsec.com](http://www.knownsec.com);

#建立测试地址

location/lua_test

{

#指定响应的默认MIME类型

default_type"text/html";

#通过lua响应内容

content_by_lua_fileconf/lua/index.lua;

}

error_log /home/log/ngx/error.log;

access_log /home/log/ngx/access access;

}

:wq

b.测试并重载配置

nginx-t

nginx-s reload

###  4.测试访问

curl--resolve [www.knownsec.com:80:192.168.0.196](http://www.knownsec.com)
<http://www.knownsec.com/lua_test>

YourIp Adress is 192.168.0.196, WelCome!

## 三、IP限速实现原理

###  1.请求处理过程

a.NGINX的请求处理过程一共划分为11个阶段，分别是：post-read、server-rewrite、find-config、rewrite、post-rewrite、 preaccess、access、post-access、try-files、content、log.（参考：<https://github.com/nginx/nginx/blob/master/src/http/ngx_http_core_module.h>）

b.在nginx官方文档(参考：<https://www.nginx.com/resources/wiki/modules/lua/>)中，可处理阶段均有相应的lua指令；就本文的目的而言，访问限速控制处于access阶段，所以需要使用的指令为access_by_lua；

c.为了方便调试和管理，可以使用access_by_lua_file指令直接加载指定路径下的lua文件来对access过程进行处理；

###  2.基于令牌桶算法的逻辑

a.令牌桶算法可控制请求的数量，并允许突发大量请求的情况。

b.当用户请求Nginx时，判断该location是否需要限制流量；

c.若需要，则检查当前IP是否已有令牌桶，若无则使用setex往redis中放入令牌桶，并指定的令牌数量及“桶”过期时间；设定单位时间内允许访问次数，比如1分钟允许10次，则令牌数量为9(当前请求算作首次消耗)，过期时间60s

d.若已有令牌桶，并且令牌数量大于0，则使用decr使其值减1(消耗令牌)并放行；

e.若令牌数量为0，则拦截；

###  3.代码实现

vim/usr/local/lua-redis/lib/lua/LimitRate.lua

\--加载REDIS模块

localr_md = require "resty.redis"

\--获取当前请求的HEADER

localheaders = ngx.req.get_headers()

\--指定REDIS的地址和端口

localredis_ip = "127.0.0.1"

localredis_port = "9600"

\--建立redis实例

localredis = r_md:new()

\--指定单位时间

localqtrange = 60

\--允许访问的次数

localqcount = 10

\--尝试根据HTTP头遂级获取IP

localclientip = headers["X-Real-IP"]

ifclientip == nil then

clientip =headers["x_forwarded_for"]

end

ifclientip == nil then

clientip = ngx.var.remote_addr

end

\--释放redis连接的函数

localfunction redis_close(red)

\--释放连接，使用set_keepalive指令将当前连接放入当前进程的连接池中待用，需要指定连接池的大小及其中各个连接的空闲超时时间；

localpool_max_idle_time = 10000 --毫秒

localpool_size = 100 --连接池大小

localok, err = red:set_keepalive(pool_max_idle_time, pool_size)

ifnot ok then  

ngx_log(ngx_ERR,"set redis keepalive error : ", err)

end

end

\--指定所有REDIS操作的超时时间，其中包含了连接超时

redis:set_timeout(1000)

建立连接，若异常则释放连接；

localok, wrong = redis:connect(redis_ip,redis_port)

ifnot ok then

redis_close(redis)

end

\--建立限速类

LimitIpRate= {}

\--限速方法，令牌桶限速逻辑实现

functionLimitIpRate:is_limited()

\--尝试获取当前IP的令牌桶，令牌桶命名为“x.x.x.x|pool”

localres, err = redis:get(clientip.."|pool")

ifnot res then

ngx.log(ngx.ERR,"luaerror: ",err)

end

\--如果res不为空并且类型为string，则代表获取到了对应的令牌桶

iftype(res) == "string" then

\--可用令牌数量为0则拦截

iftonumber(res) == 0 then

ngx.exit(ngx.HTTP_FORBIDDEN)

\--反之放行并让令牌数量减少1

else

add,err= redis:decr(clientip.."|pool")

ifnot add then

ngx.log(ngx.ERR,"luaerror: ",err)

end

end

\--如果res不为空并且类型为userdata，则代表redis中没有对应令牌桶

elseiftype(res) == "userdata" then

\--往redis中放入指定名称、过期时间、值的键值对

ini,err = redis:setex(clientip.."|pool", qtrange, (qcount-1))

ifnot ini then

ngx.log(ngx.ERR,"luaerror: ",err)

end

end

end

\--调用限速方法

LimitIpRate.is_limited()

:wq

###  4.将LimitRate.lua集成进NGINX配置文件

a.编辑配置文件，加入指令

vim/usr/local/nginx/conf/conf.d/luatest.conf

server

{

#指定监听端口及主机名

listen80;

server_name[www.knownsec.com](http://www.knownsec.com);

#建立测试地址

location/lua_test

{

#指定响应的默认MIME类型

default_type"text/html";

#通过lua对access进行过滤

access_by_lua_file"conf/lua/LimitRate.lua";

#通过lua返回响应内容

content_by_lua_fileconf/lua/index.lua;

}

error_log /home/log/ngx/error.log;

access_log /home/log/ngx/access access;

}

:wq

b.测试并重载配置

nginx-t

nginx-s reload

###  5.限速测试

fori in {1..12}; do curl -s --resolve
[www.knownsec.com:80:192.168.0.196http://www.knownsec.com/lua_test](http://www.knownsec.com//www.knownsec.com/lua_test)
-o /dev/null -w %{http_code};echo ;done

200

200

200

200

200

200

200

200

200

200

403

403

## 四、总结

a.在需要的location使用ngx_lua指定加载LimitRate.lua，并指定单位时间和单位时间中允许的请求次数；则可实现对该location请求的IP限速；

b.截止目前，仅是简单地描述了如何实现IP限速控制，还需要结合更多的业务环境来开发不同的需求，才能逐渐构建相对成熟的CC防护体系；

c.攻防之根本即为攻防双方对成本的投入；

d.若需成熟解决方案，可选择抗D保——攻击打不死，专接防不住；

