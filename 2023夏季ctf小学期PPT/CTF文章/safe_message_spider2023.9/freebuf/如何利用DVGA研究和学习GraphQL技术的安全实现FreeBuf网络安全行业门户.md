![](https://image.3001.net/images/20210313/1615646288_604cce50edfe7f70bd85b.png!small)

## DVGA

DVGA（Damn Vulnerable GraphQL
Application）是一款针对Facebook的GraphQL技术的安全学习工具，该项目中包含大量Facebook
GraphQL技术的不安全实现，即故意留下了大量的漏洞，以供广大研究人员探索和学习GraphQL技术的安全性。

DVGA是GraphQL的一个不安全的实现，其中包含了大量故意遗留的漏洞，它提供了一个安全的环境来帮助广大研究人员研究和攻击GraphQL应用程序，并允许开发人员和IT专业人员测试GraphQL漏洞。

DVGA中包含了大量安全漏洞，比如说注入漏洞、代码执行漏洞、认证绕过漏洞和拒绝服务漏洞等等。

## 操作模式

DVGA支持新手等级和专家等级这两种以游戏形式驱动的模式，这两种模式对应的漏洞利用难度会有不同。

## 攻击场景

> 拒绝服务：批查询攻击、深度递归查询攻击、资源密集型查询攻击。
>
> 信息披露：GraphiQL接口、GraphQL字段建议、服务器端请求伪造。
>
> 代码执行：操作系统命令注入。
>
> 注入漏洞：存储型跨站脚本攻击、日志嗅探、日志注入、HTML注入。
>
> 认证绕过：GraphQL接口保护绕过、GraphQL查询拒绝列表绕过。
>
> 其他：GraphQL查询弱密码保护、任意文件写入、路径遍历。

## 工具要求

DVGA的正常运行需要下列Python 3代码库的支持：

> Python3
>
> Flask
>
> Flask-SQLAlchemy
>
> Graphene
>
> Graphene-SQLAlchemy

## 工具安装

### Docker

首先，使用下列命令将该项目源码克隆至本地：

    
    
    git clone git@github.com:dolevf/Damn-Vulnerable-GraphQL-Application.git && cd Damn-Vulnerable-GraphQL-Application

使用下列命令构建Docker镜像：

    
    
    docker build -t dvga .

接下来，通过镜像创建一个容器：

    
    
    docker run -t -p 5000:5000 -e WEB_HOST=0.0.0.0 dvga

创建完成后，在浏览器中访问地址http://localhost:5000即可使用DVGA。

注意，如果你需要将应用程序绑定至一个特殊端口，比如说8080，则可以使用下列参数：

    
    
    -e WEB_PORT=8080

### Docker Hub

使用下列命令从Docker Hub拉取Docker镜像：

    
    
    docker pull dolevf/dvga

使用镜像创建容器：

    
    
    docker run -t -p 5000:5000 -e WEB_HOST=0.0.0.0 dolevf/dvga

创建完成后，在浏览器中访问地址http://localhost:5000即可使用DVGA。

### 服务器端

在命令行终端切换到/opt目录：

    
    
    cd /opt/

使用下列命令将该项目源码克隆至本地：

    
    
    git clone git@github.com:dolevf/Damn-Vulnerable-GraphQL-Application.git && cd Damn-Vulnerable-GraphQL-Application

安装依赖组件：

    
    
    pip3 install -r requirements.txt

运行应用程序：

    
    
    python3 app.py

运行后，在浏览器中访问地址http://localhost:5000即可使用DVGA。

## 工具运行截图

![](https://image.3001.net/images/20210313/1615646362_604cce9a6e7e739024f11.png!small)

![](https://image.3001.net/images/20210313/1615646370_604ccea27cbec018b6876.png!small)

![](https://image.3001.net/images/20210313/1615646379_604cceab2625c5141efae.png!small)

![](https://image.3001.net/images/20210313/1615646387_604cceb367d4afb3c395e.png!small)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

DVGA：【[ _GitHub传送门_](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application)】

