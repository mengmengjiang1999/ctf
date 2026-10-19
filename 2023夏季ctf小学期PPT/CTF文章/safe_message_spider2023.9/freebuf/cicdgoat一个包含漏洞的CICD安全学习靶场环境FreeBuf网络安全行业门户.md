![](https://image.3001.net/images/20221121/1669023684_637b47c44e98c57f4ee6c.png!small)

## 关于cicd-goat

cicd-goat是一个故意包含大量漏洞的CI/CD安全学习靶场环境，广大研究人员可以使用cicd-goat来学习关于CI/CD安全的相关内容，并通过各种挑战并拿到Flag来更好地掌握针对CI/CD管道的安全渗透技术。

cicd-goat项目允许允许工程师和安全从业人员通过一组包含是十个项目的挑战来学习和实践CI/CD安全，这些挑战是在真实、全面的CI/CD环境中实施的。这些场景具有不同的难度级别，每个场景侧重于一个主要攻击向量。这些挑战包括[
_10大CI/CD安全风险_](https://www.cidersecurity.io/top-10-cicd-security-risks/?utm_source=github&utm_medium=github_page&utm_campaign=ci%2Fcd%20goat_060422)，包括流量控制机制不足、PPE（管道执行投毒）、依赖链滥用、PBAC（基于管道的访问控制）等。

该项目的环境基于Docker容器实现，并且可以在本地运行，这些容器包括：

> 1、Gitea
>
> 2、Jenkins
>
> 3、Jenkins agent
>
> 4、LocalStack
>
> 5、Prod
>
> 6、CTFd
>
> 7、GitLab
>
> 8、GitLab runner
>
> 9、Docker in Docker

这些映像能够创建功能齐全的管道，并实现互连。

## 工具下载&运行

### Linux&macOS

    
    
    curl -o cicd-goat/docker-compose.yaml --create-dirs https://raw.githubusercontent.com/cider-security-research/cicd-goat/main/docker-compose.yaml
    
    cd cicd-goat && docker-compose up -d

注意：GitLab当前不支持配备有苹果芯片的macOS设备。

### Windows（PowerShell）

> mkdir cicd-goat; cd cicd-goat
>
> curl -o docker-compose.yaml https://raw.githubusercontent.com/cider-> security-research/cicd-goat/main/docker-compose.yaml
>
> get-content docker-compose.yaml | %{$_ -replace "bridge","nat"}
>
> docker-compose up -d

## 工具使用

首先，在开启容器之后，可能需要等待五分钟左右的时间来让容器完成配置。

接下来，登录http://localhost:8000来查看所有的挑战：

> 用户名：alice
>
> 密码：alice

### 开始渗透

> Jenkins：[ _http_ _://localhost:80_ _80_](http://localhost:8080)
>
> 用户名：alice
>
> 密码：alice

  

> Gitea [_http://localhost:3000_](http://localhost:3000)
>
> 用户名：thealice
>
> 密码：thealice

  

> GitLab [_http://localhost:4000_](http://localhost:4000)
>
> 用户名：alice
>
> 密码：alice1234

最后，将你拿到的Flag提交进去，查看是否成功即可。

## 自定义开发

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cider-security-research/cicd-goat.git

然后重命名.git文件夹：

    
    
    ./rename.py git

然后安装测试需要用到的依赖组件：

    
    
    pip3 install pipenv==2022.8.30
    
    pipenv install --deploy

运行开发环境并测试新增的挑战项目：

    
    
    rm -rf tmp tmp-ctfd/
    
    cp -R ctfd/data/ tmp-ctfd/
    
    docker-compose -f docker-compose-dev.yaml up -d

关闭环境，将挑战重构：

    
    
    docker-compose -f docker-compose-dev.yaml down
    
    ./apply.sh # save CTFd changes
    
    docker-compose -f docker-compose-dev.yaml up -d --build

运行测试：

    
    
    pytest tests/

重命名.git文件夹并允许push：

    
    
    ./rename.py notgit

最后，commit并push即可。

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._ _0_](https://github.com/cider-security-research/cicd-goat/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **cicd-goat** ：【[ _GitHub传送门_](https://github.com/cider-security-research/cicd-goat)】

## 参考资料

> [ _https://www.cidersecurity.io/?utm_source=github
> &utm_medium=github_page&utm_campaign=ci%2fcd%20goat%20_060422_](https://www.cidersecurity.io/?utm_source=github&utm_medium=github_page&utm_campaign=ci%2Fcd%20goat%20_060422)
>
> [ _https://www.cidersecurity.io/top-10-cicd-security-> risks/?utm_source=github
> &utm_medium=github_page&utm_campaign=ci%2fcd%20goat_060422_](https://www.cidersecurity.io/top-10-cicd-> security-> risks/?utm_source=github&utm_medium=github_page&utm_campaign=ci%2Fcd%20goat_060422)

