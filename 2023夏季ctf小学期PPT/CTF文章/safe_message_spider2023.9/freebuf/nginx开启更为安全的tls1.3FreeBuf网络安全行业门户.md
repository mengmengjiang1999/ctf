原创： 梦呓233 合天智汇 3天前

  
【不支持外链图片，请上传图片或单独粘贴图片】  

随着互联网安全越来越受到重视，越来越多的网站选择启用https来保证数据的加密传输，TLS1.2发布于2008年8月，至今正好有10年，所以新协议TLS1.3呼之欲出。Google
chrome在最近的版本更新中也开始逐步对TLS1.3进行支持，TLS1.3对于TLS1.2有重大改写，提高了安全性并且提高了速度，所以升级还是很有必要的，本文尝试在nginx中开启TLS1.3.

**关于TLS1.3的科普可以看下面的页面**

https://wiki.openssl.org/index.php/TLS1.3

https://zhuanlan.zhihu.com/p/28850798

我这里用的系统是Debian 8

  

第一步：安装依赖

$ apt-get install git gcc make build-essential zlib1g-dev libpcre3-dev

第二步：下载源码和补丁

$ mkdir -p /usr/src

$ cd /usr/src

$ git clone git://git.openssl.org/openssl.git openssl

$ git clone https://github.com/hakasenyang/openssl-patch.git openssl-patch

$ git clone https://github.com/kn007/patch.git nginx-patch

$ wget https://nginx.org/download/nginx-1.15.0.tar.gz

$ tar zxvf ./nginx-1.15.0.tar.gz

第三步：打补丁

1，给OpenSSL打补丁，补丁的意义在于使OpenSSL支持最新的TLS1.3.

补丁地址：https://github.com/hakasenyang/openssl-patch

$ cd /usr/src/openssl

$ patch -p1 < ../openssl-patch/openssl-equal-pre8_ciphers.patch

2，给Nginx打补丁，nginx 补丁添加SPDY支持，添加HTTP2 HPACK编码支持，添加动态TLS记录支持

补丁地址：https://github.com/kn007/patch

fix_nginx_hpack_push_error 补丁修复nginx的http2 push和http2 hpack兼容性问题

nginx_auto_using_PRIORITIZE_CHACHA
补丁添加在使用OpenSSL1.1.1时SSL_OP_PRIORITIZE_CHACHA的支持。

$ cd /usr/src/nginx-1.15.0

$ patch -p1 < ../nginx-patch/nginx.patch

$ patch -p1 < ../nginx-patch/fix_nginx_hpack_push_error.patch

$ patch -p1 < ../nginx-patch/nginx_auto_using_PRIORITIZE_CHACHA.patch

第四步：编译安装

$ ./configure \

\--sbin-path=/usr/sbin/nginx \

\--conf-path=/etc/nginx/nginx.conf \

\--prefix=/usr/local/nginx \

\--pid-path=/var/run/nginx.pid \

\--lock-path=/var/lock/nginx.lock \

\--with-openssl=../openssl \

\--with-http_v2_module \

\--with-http_v2_hpack_enc \

\--with-http_spdy_module \

\--with-http_ssl_module \

\--with-http_gzip_static_module \

\--http-log-path=/var/log/nginx/access.log \

\--error-log-path=/var/log/nginx/error.log

$ make

$ make install

Nginx的可执行文件安装在/usr/sbin/，Nginx配置文件在/etc/nginx/里

第五步：配置

1，修改Nginx全局配置：

将以下内容填入：/etc/nginx/nginx.conf

worker_processes auto;

pid /var/run/nginx.pid;

error_log /var/log/nginx/error.log;

events {

use epoll;

multi_accept on;

worker_connections 1024;

}

http {

charset utf-8;

include /etc/nginx/mime.types;

default_type application/octet-stream;

access_log /var/log/nginx/access.log;

sendfile on;

tcp_nopush on;

tcp_nodelay on;

keepalive_timeout 60;

gzip on;

gzip_vary on;

gzip_proxied any;

gzip_min_length 1k;

gzip_buffers 4 8k;

gzip_comp_level 2;

gzip_disable "msie6";

gzip_types text/plain text/css application/json application/x-javascript
text/xml application/xml application/xml+rss text/javascript
application/javascript image/svg+xml;

include /etc/nginx/vhost/*.conf;

}

2，修改Nginx站点配置

我们已经在全局配置里设置了包含/etc/nginx/vhost/目录下的conf文件

$ mkdir -p /etc/nginx/vhost

在然后/etc/nginx/vhost/里创建站点配置，这里统一用“域名”文字代替真实域名

server {

listen 80;

server_name 域名;

root /wwwroot/域名;

location / {

index index.html;

}

}

这样HTTP的站点配置就弄好了，不过还站点还没页面，我们可以先把Nginx的欢迎页面给放进去

mkdir -p /wwwroot/域名

$ cp /usr/local/nginx/html/index.html /wwwroot/域名/

$ nginx

启动Nginx后HTTP页面就正常了，打开就能看到欢迎页面。

第六步：签发证书

配置HTTPS首先要有证书，我这里是使用acme.sh自动颁发让我们加密的证书

1，安装工具：

apt-get install cron socat

2，获取acme.sh：

curl https://get.acme.sh | sh

3，生成证书：

使用http方式验证域名，这是我们先搭建HTTP站点的原因，接下来指定域名，指定站点目录，开始签发

acme.sh --issue -d 域名 --webroot /wwwroot/域名/ --keylength ec-256 --nginx

4，复制证书：

证书已经签发，保存在~/.acme.sh/里

$ acme.sh --ecc --installcert -d 域名 \

\--key-file /etc/nginx/ssl/域名.key \

\--fullchain-file /etc/nginx/ssl/域名.cer \

\--reloadcmd "nginx -s reload"

指定域名，指定证书保存目录，我这里设置在/etc/nginx/ssl/，指定Nginx重载命令，如果签发的不是ECC证书，把--ecc参数去掉

这样使用acme.sh就完成了证书的签发，如果证书快要过期了，脚本会自动更新证书

脚本自动更新，可以使用以下命令

$ acme.sh --upgrade --auto-upgrade

第七步：HTTPS站点配置

我给OpenSSL打的是pre8_ciphers补丁，所以配置文件如下：

server {

listen 80;

server_name 域名;

return 301 https://域名$request_uri;

}

server {

listen 443 ssl http2;

server_name 域名;

root /wwwroot/域名;

ssl_certificate /etc/nginx/ssl/域名.cer;

ssl_certificate_key /etc/nginx/ssl/域名.key;

ssl_protocols TLSv1.2 TLSv1.3;

ssl_ciphers
[TLS13+AESGCM+AES128|TLS13+AESGCM+AES256|TLS13+CHACHA20]:[EECDH+ECDSA+AESGCM+AES128|EECDH+ECDSA+CHACHA20]:EECDH+ECDSA+AESGCM+AES256:EECDH+ECDSA+AES128+SHA:EECDH+ECDSA+AES256+SHA:[EECDH+aRSA+AESGCM+AES128|EECDH+aRSA+CHACHA20]:EECDH+aRSA+AESGCM+AES256:EECDH+aRSA+AES128+SHA:EECDH+aRSA+AES256+SHA:RSA+AES128+SHA:RSA+AES256+SHA:RSA+3DES;

ssl_ecdh_curve X25519:P-256:P-384;

ssl_prefer_server_ciphers on;

ssl_session_cache shared:SSL:50m;

ssl_session_timeout 1d;

ssl_session_tickets on;

ssl_stapling on;

ssl_stapling_verify on;

add_header Strict-Transport-Security max-age=15768000;

location / {

index index.html;

http2_push /style.css;

}

location ~ .*\\.(gif|jpg|jpeg|png|bmp|swf|ico)$ {

expires 30d;

}

location ~ .*\\.(js|css)?$ {

expires 15d;

}

location ~ /.git/ {

deny all;

}

}

以上就是完整的站点配置文件，覆盖/etc/nginx/vhost/域名.conf后，使用nginx -s
reload重载Nginx再打开站点就能看到HTTPS的页面了

验证一下：

在Chrome 65或更新的版本中，打开开发者工具的安全菜单，就能在里面看到站点是否以TLS1.3连接。

  
【不支持外链图片，请上传图片或单独粘贴图片】  

后记：随着网络技术的发展，网络安全已经变得和我们的生活息息相关，我们需要新的技术来保护我们的隐私，而网站的站长更应该及时更新以保证用户数据的私密性，所以各位站长赶快升级吧。

郑重说明：利用本文做任何违法事情，与本人和合天智汇无关，资料仅供参考与学习。

  

