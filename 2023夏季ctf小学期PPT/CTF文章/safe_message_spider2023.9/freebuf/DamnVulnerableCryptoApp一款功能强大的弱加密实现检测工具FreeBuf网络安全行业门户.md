![](https://image.3001.net/images/20201015/1602754590_5f88181e7d8e40cfa3f1b.png!small)

## DamnVulnerableCryptoApp

DamnVulnerableCryptoApp是一款实现了各种弱加密的应用程序，广大研究人员可以使用DamnVulnerableCryptoApp来查看、测试或利用目标应用程序钟的弱加密实现，而密码学初学者们也可以利用该工具在无需深入了解加密背后数学知识的情况下，来学习关于密码学的更多知识。

如果你想了解更多关于加密方面的知识，如果你想知道加密攻击是如何执行的，如果你想保护你代码的安全，但是你又对加密算法背后的数学知识感到厌倦的话，DamnVulnerableCryptoApp就是你最佳的选择。

注意事项：该项目目前正在紧张开发阶段，因此部分功能可能不完整或不稳定！

## 工具特性

  * 提供了最接近真实攻击场景的加密攻击样例；
  * 无需编写额外的、复杂的漏洞利用代码；
  * 每一个加密攻击挑战都提供了相应的解决方案；
  * 提供了易于理解的参考文档，没有复杂的数学内容，没有复杂的公式，只有简单的文字；
  * 支持测试各种不同的加密攻击向量；
  * 可以帮助每一位用户轻松了解加密、攻击以及相关的防御方案；
  * 直奔主题，每一个攻击挑战都是最直接的漏洞利用场景；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/DamnVulnerableCryptoApp/DamnVulnerableCryptoApp.git

## 项目构建

在进行项目构建之前，请确保已经安装并配置好了Node环境。接下来，请在本地项目目录中运行下列代码：

    
    
    npm run build-with-deps

或者，如果你已经安装好了依赖组建的话，你可以直接运行下列命令：

    
    
    npm run build

## 疑难解决

如果你在运行测试的过程中，遇到了关于哈希的错误，那你可能需要修改你的git行结束风格：

    
    
    git config --global core.eol lf
    
    git config --global core.autocrlf input

## 工具运行

    
    
    npm run start

你可以使用下列环境变量来修改工具的运行端口：

    
    
    PORT=4000 npm run start

## Docker使用

### 从DockerHub获取

广大研究人员可以使用下列命令下载最新版本的Docker镜像：

    
    
    docker pull damnvulnerablecryptoapp1/damnvulnerablecryptoapp

### 项目构建

如果你想要自行构建Docker镜像，请运行下列命令：

    
    
    npm build:docker

### Docker运行

Docker默认导出的是8081端口，因此我们可以将其映射至我们自己的端口：

    
    
    docker run -p 8081:8081 <IMAGE_ID>

## 功能开发

如果你想要开发自己的功能，或者直接运行该工具而不想构建代码的话，可以直接运行下列命令：

    
    
    npm run install-deps

但此时你需要单独运行前端和后端App。

### 后端

    
    
    cd backend
    
    yarn start

如果你想要修改默认的后端端口1234，你可以使用下列环境变量进行设置：

    
    
    PORT=5000 yarn start

### 前端

    
    
    cd frontend
    
    yarn start

如果你想要修改默认的前端端口4000，你可以使用下列环境变量进行设置：

    
    
    PORT=3000 yarn start

如果你想修改服务器端口，你需要在开启前端之前通过修改环境变量来指定端口：

    
    
    REACT_APP_SERVER_PORT=5000 yarn start

## 工具运行截图

![](https://image.3001.net/images/20201015/1602754723_5f8818a35cc1d706bdc58.png!small)

![](https://image.3001.net/images/20201015/1602754731_5f8818ab0d0b00f19adec.png!small)

![](https://image.3001.net/images/20201015/1602754738_5f8818b203dc032efa86d.png!small)

![](https://image.3001.net/images/20201015/1602754744_5f8818b86a3dc4db51b9b.png!small)

## 许可证协议

DamnVulnerableCryptoApp项目的开发与发布遵循[
_MIT开源许可证协议_](https://tldrlegal.com/license/mit-license)。

## 参考资料

DamnVulnerableCryptoApp：【[ _GitHub_
_传送门_](https://github.com/DamnVulnerableCryptoApp/DamnVulnerableCryptoApp/)】

项目文档：【[ _点我_
_获取_](https://github.com/DamnVulnerableCryptoApp/DamnVulnerableCryptoApp/wiki)】

  

