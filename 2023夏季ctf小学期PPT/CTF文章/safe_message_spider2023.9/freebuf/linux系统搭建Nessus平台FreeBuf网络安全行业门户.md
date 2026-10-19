# Linux系统搭建nessus平台

Nessus号称是世界上最流行的漏洞扫描程序，全世界有超过75000个组织在使用它。该工具提供完整的电脑漏洞扫描服务，并随时更新其漏洞数据库。Nessus不同于传统的漏洞扫描软件，Nessus可同时在本机或远端上遥控，进行系统的漏洞分析扫描。对应渗透测试人员来说，Nessus是必不可少的工具之一。所以，本章将介绍Nessus工具的基础知识。

* * *

## 1.下载nessus

Nessus官网下载链接https://www.tenable.com/downloads/nessus?loginAttempted=true，下载与服务器对应的版本

![1666841421280.png](https://image.3001.net/images/20221027/1666841428_6359fb54a313e129e7856.png!small)

* * *

## 2.开始安装

下载后，将其导入服务器路径/usr/local/src/下

![1666841440063.png](https://image.3001.net/images/20221027/1666841446_6359fb6654283022440a9.png!small)

在/usr/local/src/路径下，执行安装程序，默认安装到/opt/nessus/路径下

执行安装命令sudo dpkg -i Nessus-8.12.1-ubuntu1110_amd64.deb

![1666841464613.png](https://image.3001.net/images/20221027/1666841469_6359fb7dd73c3705354e3.png!small)

在安装/opt/nessus/sbin/路径下执行命令启动程序

执行命令 sudo ./nessusd restart或sudo systemctl start nessusd

![1666841480554.png](https://image.3001.net/images/20221027/1666841490_6359fb92a3edb9fb1f1f9.png!small)

在安装/opt/nessus/sbin/路径下执行命令，查看服务是否开启

执行命令 sudo systemctl status nessusd.service

![1666841497819.png](https://image.3001.net/images/20221027/1666841510_6359fba6c9189056bd07c.png!small)

在安装/opt/nessus/sbin/路径下执行命令，使Nessus守护程序绑定到TCP端口8834上。

执行命令 sudo ss -tunelp | grep 8834

![1666841524062.png](https://image.3001.net/images/20221027/1666841532_6359fbbcca3241ddbfa43.png!small)

如果UFW正在运行，请确保在防火墙上允许此端口  
执行命令 sudo ufw allow 8834/tcp

![1666841552448.png](https://image.3001.net/images/20221027/1666841559_6359fbd7556f41dbd2369.png!small)

此时，访问https://ip地址:8834，按照如下步骤操作即可。

![1666841567461.png](https://image.3001.net/images/20221027/1666841572_6359fbe4ddb8511a140ee.png!small)

![1666841579530.png](https://image.3001.net/images/20221027/1666841585_6359fbf1c9aa579e51a18.png!small)

![1666841592801.png](https://image.3001.net/images/20221027/1666841624_6359fc18aa65b359d5723.png!small)

如若上图无法添加用户可在宝塔执行创建用户命令，并重启服务即可。

执行命令 ./nessuscli adduser

![1666841638769.png](https://image.3001.net/images/20221027/1666841649_6359fc31c8e84c605342f.png!small)

* * *

## 3.导入插件包

在安装/opt/nessus/sbin/路径下执行命令，获取challenge code码

执行命令 ./nessuscli fetch --challenge

![1666841657955.png](https://image.3001.net/images/20221027/1666841665_6359fc413b8340384a2c4.png!small)

访问https://zh-cn.tenable.com/products/nessus/nessus-essentials获取邮箱激活码activation
code

![1666841671747.png](https://image.3001.net/images/20221027/1666841678_6359fc4e884f27b0c2085.png!small)

访问https://plugins.nessus.org/v2/offline.php网址

将获取到的challenge code码和邮箱激活码activation code，分别复制到俩个输入框内。

![1666841687561.png](https://image.3001.net/images/20221027/1666841695_6359fc5ff04536b1007f3.png!small)

将插件包和license文件下载

![1666841704458.png](https://image.3001.net/images/20221027/1666841713_6359fc713f3a2665f8feb.png!small)

将下载下来的俩个文件，复制到/opt/nessus/sbin/路径下。

![1666841721181.png](https://image.3001.net/images/20221027/1666841727_6359fc7fa4387010ddc04.png!small)

在/opt/nessus/sbin/路径下执行命令安装license文件

执行命令./nessuscli fetch --register-offline nessus.license

![1666841741735.png](https://image.3001.net/images/20221027/1666841747_6359fc93e81dc4b9ec7b3.png!small)

在/opt/nessus/sbin/路径下执行命令安装插件包

执行命令./nessuscli update all-2.0.tar.gz

![1666841755184.png](https://image.3001.net/images/20221027/1666841760_6359fca09a0a09b5c45db.png!small)

至此nessus已安装完成，但是只允许扫描16个，接下来将其破解为无限制扫描。

* * *

## 4.破解成无限制

记录下上图的202009231305数值，方便接下来进行破解用。

可使用命令执行

export PLUGIN_SET="202009231305"

cat>/opt/nessus/lib/nessus/plugins/plugin_feed_info.inc<<EOF  
PLUGIN_SET = ${PLUGIN_SET};  
PLUGIN_FEED = "ProfessionalFeed (Direct)";

PLUGIN_FEED_TRANSPORT = "Tenable Network Security Lightning";  
EOF

cat>/opt/nessus/var/nessus/plugin_feed_info.inc<<EOF  
PLUGIN_SET = ${PLUGIN_SET};  
PLUGIN_FEED = "ProfessionalFeed (Direct)";

PLUGIN_FEED_TRANSPORT = "Tenable Network Security Lightning";  
EOF

也可以编辑plugin_feed_info.inc文件上传到/opt/nessus/var/nessus/和/opt/nessus/lib/nessus/plugins/文件夹下。

plugin_feed_info.inc文件内容

![1666841774849.png](https://image.3001.net/images/20221027/1666841780_6359fcb4a3a16172752bb.png!small)

在/opt/nessus/sbin/路径下重启nessus服务即可

执行命令./nessusd restart或service nessusd restart或sudo systemctl start nessusd

