在阅读free5Gc源码和进行一些功能验证的过程中，我们可能会发现free5Gc的源码实现是存在bug的。

以AMF网元为例，它的UEContextTransferProcedure缺少红框这句话进行实例化，导致请求时会触发空指针异常：

![](https://image.3001.net/images/20210205/1612486210_601c96429cd11e77fe233.png!small)

为了让功能恢复正常可用，我们需要修改源码并重新编译，步骤如下。

##  **一、** ** **下载free5Gc源码****

git clone --recursive -b v3.0.3 -j `nproc`
[_https://github.com/free5gc/free5gc.git_](https://github.com/free5gc/free5gc.git)  
cd free5gc

git checkout master

git submodule sync

git submodule update --init --jobs `nproc`

git submodule foreach git checkout master

git submodule foreach git pull --jobs `nproc`

每个网元的源码都会在free5gc/src/{网元名称下}，按需要进行修改。

##  **二、** ** **重新编译amf****

export CGO_ENABLED=0

go build -o bin/amf -x src/amf/amf.go

##  **三、** ** **将编译后的amf重新拷贝到amf容器****

sudo docker cp ./amf amf:/free5gc/amf/amf

##  **四、** ** **重启amf容器****

sudo docker stop amf

sudo docker start amf

