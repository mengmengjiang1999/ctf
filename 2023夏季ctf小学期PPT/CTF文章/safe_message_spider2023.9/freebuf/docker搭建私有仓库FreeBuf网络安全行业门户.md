## 一. 安装docker

#### 1\. docker一键安装命令:

    
    
    curl -sSL https://get.daocloud.io/docker | sh
    

#### 2\. 启动docker

    
    
    systemctl start docker
    

## 二. 搭建镜像仓库

拉取Registry私有镜像仓库，在我们本地搭建一个内网的仓库，避免将一些私密项目暴露在公网，引发不必要的风险。

#### 1\. 下载Registry镜像

    
    
    docker pull registry
    

![在这里插入图片描述](https://image.3001.net/images/20211118/1637225409_619613c15a082aad68614.png!small)

#### 2\. 运行Registry镜像

    
    
    docker run -d --name registry -p 5000:5000 -v /storage/registry:/tmp/registry registry
    

#### 3\. 查看镜像仓库中的所有镜像

    
    
    curl http://127.0.0.1:5000/v2/_catalog
    

下图返回的json数据代表暂无任何仓库，因为我们还没有上传任何镜像。

![在这里插入图片描述](https://image.3001.net/images/20211118/1637225410_619613c213b2406de4f4c.png!small)

## 三. 配置仓库可直接通过http方式访问

docker默认是传输方式使用https协议，我们手头上没有sttps证书，所以此处不配置https证书，直接设置可信源，使我们内网可以通过http方式访问

#### 1\. 修改vim /etc/docker/daemon.json,添加以下内容:

没有daemon.json文件则新建.

    
    
    { 
        "insecure-registries" : [ "your-server-ip:5000" ] 
    
    

![!\[在这里插入图片描述\]\(https://img-blog.csdnimg.cn/d677c3ce5ae04a55b4a5a51bc28e0733.png](https://image.3001.net/images/20211118/1637225410_619613c2c7b77b3174373.png!small)

#### 2\. 重新加载、重启docker、启动镜像

    
    
    systemctl daemon-reload
    systemctl restart docker
    docker start registry
    

## 四. 上传镜像至仓库

#### 1\. 查看镜像

    
    
    docker images
    

#### 2\. 将要上传的镜像打Tag

    
    
    docker tag your-image-name:tagname your-server-ip:5000/your-image-name:tagname
    

![在这里插入图片描述](https://image.3001.net/images/20211118/1637225411_619613c34e56af2c8ebf9.png!small)

#### 3\. 把镜像推送到仓库

    
    
    docker push your-registry-server-ip:5000/your-image-name:tagname
    

![在这里插入图片描述](https://image.3001.net/images/20211118/1637225411_619613c3c9f4598bc5c4f.png!small)

#### 4.再次验证是否推送成功

    
    
    curl http://your-server-ip:5000/v2/_catalog
    

可以看见`{"repositories":["registry"]}`,说明已经推送成功,有一个registry镜像了

![在这里插入图片描述](https://image.3001.net/images/20211118/1637225412_619613c428c69feadc78e.png!small)

## 五. 客户端下载镜像

现在在本机测试能否下载刚刚上次的镜像，如果此处是在另一台客户机下载，注意要配置http方式访问。

#### 1\. 修改vim /etc/docker/daemon.json添加以下内容:

    
    
    { 
        "insecure-registries" : [ "your-server-ip:5000" ] 
    }
    

#### 2\. 重新加载docker

    
    
    systemctl daemon-reload
    systemctl restart docker
    

#### 3\. 下载镜像

    
    
    docker pull 10.168.6.109:5000/registry:latest
    

