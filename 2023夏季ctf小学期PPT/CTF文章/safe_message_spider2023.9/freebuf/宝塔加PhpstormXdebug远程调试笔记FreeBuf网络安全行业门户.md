服务器网站ip 192.168.161.132

phpstorm客户端ip 192.168.10.175

1.首先宝塔下载xdebug，找到php管理

![1681964461_6440bdadbc04d6bc6a839.png!small](https://image.3001.net/images/20230420/1681964461_6440bdadbc04d6bc6a839.png!small)

2.安装完成后，修改配置文件

![1681964667_6440be7bf11c90121408d.png!small](https://image.3001.net/images/20230420/1681964667_6440be7bf11c90121408d.png!small)

xdebug.mode=debug  
xdebug.discover_client_host=true  
xdebug.remote_cookie_expire_time = 3600  
xdebug.client_port=9000  
xdebug.client_host="填写phpstorm所在客户端ip"  
xdebug.start_with_request=yes  
xdebug.remote_handler = "dbgp"

3.接下来配置phpstorm,将端口配置为php配置文件的端口

![1681964823_6440bf177b43edccb53ca.png!small](https://image.3001.net/images/20230420/1681964823_6440bf177b43edccb53ca.png!small)

配置服务器ip地址

客户端网站源码与服务端源码相映射

![1681964960_6440bfa08faa13466d38b.png!small](https://image.3001.net/images/20230420/1681964960_6440bfa08faa13466d38b.png!small)

最后的配置

![1681965163_6440c06bed9a34adb50f0.png!small](https://image.3001.net/images/20230420/1681965163_6440c06bed9a34adb50f0.png!small)

下断点运行

![1681965230_6440c0aeac573becb87c0.png!small](https://image.3001.net/images/20230420/1681965230_6440c0aeac573becb87c0.png!small)

