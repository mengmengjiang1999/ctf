**今天给大家介绍的是一款名叫Project
iKy的开源工具，广大研究人员可以利用该工具来从电子邮件中收集信息，该工具将会以数据图表的形式将分析结果反馈给用户。**

![1.png](https://image.3001.net/images/20190530/1559231699_5ceffcd3d5571.png!small)

## 项目介绍

首先，我们建议广大研究人员先将前端从之前的AngularJS更新为Angular。为了方便用户使用，我们在iKy-v1分支中仍然使用的是AngularJS，相关参考文档可以点击【[这里](https://draft.blogger.com/kennbroorg/iKy/blob/iKy/README-v1.es.md)】获取。

### 工具演示视频

视频地址：<https://vimeo.com/326114716>

## 工具安装

使用下列命令克隆项目代码库至本地：

    
    
    git clone https://gitlab.com/kennbroorg/iKy.git

## 安装工具后端

首先，我们需要安装Redis：

    
    
    wget <http://download.redis.io/redis-stable.tar.gz>
    
    tar xvzf redis-stable.tar.gz
    
    cd redis-stable
    
    make
    
    sudo make install

接下来，使用下列命令在终端开启后台服务器：

    
    
    redis -server

## Python依赖组件以及Celery

在使用该工具之前，我们需要安装相应的依赖组件：

    
    
    pip install -r requirements.txt

打开另一个终端窗口，然后在backend目录中开启Celery：

    
    
    ./celery.sh

最后，再打开一个新的终端窗口，开启后端App（服务器端）：

    
    
    python app.py

## 安装工具前端

### NodeJS

首先，我们要安装[NodeJS](https://nodejs.org/en/)。

### 依赖组件

切换至frontend目录，并安装相应的依赖组件：

    
    
    npm install

### 开启前端服务器

最后，使用下列命令开启前端服务器：

    
    
    npm start

### 工具访问

打开浏览器，然后在浏览器地址栏中输入下列URL即可访问工具前端：

    
    
    http://127.0.0.1:4200/

![2.png](https://image.3001.net/images/20190530/1559231783_5ceffd27b871d.png!small)

### 配置API密钥

当我们在浏览器中加载完应用程序之后，我们就可以打开API配置选项，并加载所需要的API密钥了：

> 1.Fullcontact：点击【[这里](https://support.fullcontact.com/hc/en-> us/articles/115003415888-Getting-Started-FullContact-v2-APIs)】生成API密钥；
>
>
> 2.Twitter：点击【[这里](https://developer.twitter.com/en/docs/basics/authentication/guides/access-> tokens.html)】生成API密钥；
>
> 3.Linkedin：只需加载账户的用户名及密码。

## 项目地址

ProjectiKy：【[GitLab传送门](https://gitlab.com/kennbroorg/iKy)】

***参考来源：[iKy](https://gitlab.com/kennbroorg/iKy)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

