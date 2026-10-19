## 一、veinmind-privilege-escalation

veinmind-tools 这次上新的插件 veinmind-privilege-escalation
是一款提权风险扫描插件，它能检测容器逃逸场景提权风险，其功能特性如下：

  * 能快速扫描容器/镜像中的 suid、limited-suid、sudo提权风险 
  * 支持 docker/containerd 容器运行时 
  * 支持 json/cli/html 等多种报告格式输出

## 二、使用参数

### 1.指定镜像名称或镜像ID并扫描 (需要本地存在对应的镜像)

    
    
    ./veinmind-privilege-escalation scan image [imageID/imageName]

![1688538509_64a50d8ddeafc43ed9a83.png!small?1688538509992](https://image.3001.net/images/20230705/1688538509_64a50d8ddeafc43ed9a83.png!small?1688538509992)

### 2.扫描所有本地镜像

    
    
    ./veinmind-privilege-escalation scan image

![1688538561_64a50dc1250d77d87ef96.png!small?1688538560792](https://image.3001.net/images/20230705/1688538561_64a50dc1250d77d87ef96.png!small?1688538560792)

### 3.指定容器名称或容器ID并扫描

    
    
    ./veinmind-privilege-escalation scan container [containerID/containerName]

![1688538611_64a50df3c284e7f127ddb.png!small?1688538611379](https://image.3001.net/images/20230705/1688538611_64a50df3c284e7f127ddb.png!small?1688538611379)

### 4.扫描所有本地容器

    
    
    ./veinmind-privilege-escalation scan container

![1688538657_64a50e2128dbd38545605.png!small?1688538656804](https://image.3001.net/images/20230705/1688538657_64a50e2128dbd38545605.png!small?1688538656804)

### 5.指定输出格式 支持的输出格式：

  * html
  * json
  * cli（默认）

    
    
    ./veinmind-privilege-escalation scan container [containerID/containerName] -f html

生成的result.html效果如图：

![1688538742_64a50e76d2a9506b8cece.png!small?1688538742525](https://image.3001.net/images/20230705/1688538742_64a50e76d2a9506b8cece.png!small?1688538742525)

## 三、总结

由上文可见，问脉Tools是很好上手的工具，想要容器安全，点击下方链接，快快来体验吧！！！

项目地址：https://github.com/chaitin/veinmind-tools

