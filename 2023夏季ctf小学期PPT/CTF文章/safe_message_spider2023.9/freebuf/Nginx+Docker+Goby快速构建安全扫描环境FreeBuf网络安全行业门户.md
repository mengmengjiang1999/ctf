[Goby](gobies.org)是国内优秀的漏洞扫描器，但是如果构建分布式扫描环境难度比较大，而且，goby本身使用http通信，数据明文传输，不利于隐藏自身。这里主要通过nginx反向代理来对流量进行加密，同时使用docker实现goby环境的快速搭建。

goby分为client端和server端，server端程序使用Golang编写，放在golib文件夹中。client和server通过restful的形式进行数据交互，内容不加密。结合上述特点，我们如果需要构建分布式扫描环境，可以有以下思路：

> 使用https协议加密流量
>
> 将server端封装成docker
>
> 实现goby api的sdk，批量开启扫描

本篇文章介绍前两点内容。

## 配置

### nginx配置

我们这里使用nginx的官方docker镜像，下载地址: <https://github.com/nginxinc/docker-nginx/tree/master/stable/alpine>

下载后的文件夹，新建一个conf.d文件，内容如下：

    
    
    server {
        listen       80;
        listen  [::]:80;
    
        listen 443 ssl default_server;
        listen [::]:443 default_server;
    
        ssl_certificate /etc/nginx/conf.d/domain.crt;
        ssl_certificate_key /etc/nginx/conf.d/domain.key;
        server_name  localhost;
    
        #access_log  /var/log/nginx/host.access.log  main;
    
        location / {
            proxy_pass http://127.0.0.1:8361;
        }
    }
    

这里重点是生成一个自签名证书，流程如下：

RSA密钥生成（设置一个密码）  
`openssl genrsa -des3 -out domain_pass.key 1024`

拷贝一个不需要输入密码的密钥文件  
`openssl rsa -in domain_pass.key -out domain.key`

生成一个证书请求  
`openssl req -new -key domain.key -out domain.csr`

对证书签名  
`openssl x509 -req -days 365 -in domain.csr -signkey domain.key -out
domain.crt`

最后将生成的文件放在nginx的`conf.d`文件夹中，nginx的配置工作就完成了。

### Goby配置

Docker中需要保持Goby的即时更新，因此需要从github上获取最新版本的docker，这里通过调用github的api来实现，代码如下：

    
    
    # 40-goby-deploy.sh
    
    echo 'Downloading goby..'
    mkdir /app
    goby_url=`curl -s https://api.github.com/repos/gobysec/Goby/releases/latest | grep browser_download_url | grep linux | cut -d '"' -f 4`
    wget $goby_url -O /app/goby.zip
    unzip /app/goby.zip -d /app/
    echo 'Goby Download success'
    goby_dir=`ls /app/ | grep goby-linux-`
    mv /app/$goby_dir /app/goby
    echo 'Goby Download success'
    

代码下载最新的`goby`，并移动到`/app`目录下，同时，将文件夹重命名为`goby`

接下来配置Goby的后台启动，脚本如下：

    
    
    # start-goby.sh
    
    echo "Starting Goby Service"
    nohup /app/goby/golib/goby-cmd-linux -mode api -apiauth goby:goby > /app/goby.log 2>&1 &
    echo "Goby Done"
    

## Docker打包

完成了上述的准备工作，我们就可以着手写自己的Dockerfile。这里就在原有Dockerfile的基础上修改：

    
    
    COPY 40-goby-deploy.sh /
    COPY start-goby.sh /
    
    RUN /bin/sh /40-goby-deploy.sh # 在打包阶段下载最新的goby
    ENTRYPOINT ["/docker-entrypoint.sh"] # 
    COPY conf.d /etc/nginx/conf.d/
    
    EXPOSE 80 443
    
    STOPSIGNAL SIGQUIT
    
    CMD ["nginx", "-g", "daemon off;"]
    

最后，在入口脚本`docker-entrypoint.sh`中添加：

`/bin/sh "/start-goby.sh"`

## 运行

构建镜像：`docker build -t gobysec:v1 .`

运行镜像：`docker run -it -d -p 80:80 -p 443:443 gobysec:v1`

## 使用

1\. Goby的官方client需要使用http进行通信，如图：

![CleanShot 2021-07-13 at
17.35.23.png](https://image.3001.net/images/20210713/1626168936_60ed5e689bf2e200e1b81.png!small)

2\. 可以通过GobyAPI来进行分布式调度，目前可以同时调度多个goby后台程序扫描。相关内容下一期讨论。

