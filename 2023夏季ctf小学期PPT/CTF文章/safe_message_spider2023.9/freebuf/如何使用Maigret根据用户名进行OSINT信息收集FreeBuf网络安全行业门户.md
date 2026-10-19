**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210406/1617710342_606c4d06ccb271d27f75b.png!small)

## 关于Maigret

Maigret是一款功能强大的OSINT用户名检测工具，该工具可以帮助广大研究人员从大量网站上通过用户名来收集目标用户的个人信息。

Maigret的主要功能就是通过用户名在大量网站上收集关于目标用户的信息，并建立个人档案。目前，Maigret支持超过2000个网站（https://github.com/soxoj/maigret/blob/main/sites.md），默认配置下Maigret会搜索前500个热门网站。

## 功能介绍

> 个人资料页面解析、提取个人信息、链接到其他个人资料等。
>
> 根据找到的新用户名进行递归搜索。
>
> 按标签搜索（站点类别、国家）。
>
> 信息审查和验证码检测。
>
> 假阳性低。

## 工具安装

注意：Maigret的正常运行要求系统安装好Python 3.6或更高版本，以及pip工具。我们建议广大用户使用Python 3.8。

### 包安装

 **通过PYPI安装：**

    
    
    pip3 install maigret

 **手动克隆并安装：**

    
    
    git clone https://github.com/soxoj/maigret && cd maigret
    
    pip3 install

### 克隆代码库

    
    
    git clone https://github.com/soxoj/maigret && cd maigret

### 虚拟机安装

当然了，你也可以使用一个免费的虚拟机，代码库将会自动完成克隆和安装：

Google
Cloud：https://console.cloud.google.com/cloudshell/open？git_repo=https:/github.com/soxoj/maigret&tutorial=README.md

Repl：https://repl.it/github/soxoj/maigret

Colab：https://colab.research.google.com/gist/soxoj/879b51bc3b2f8b695abb054090645000/maigret.ipynb

    
    
    pip3 install -r requirements.txt

## 工具使用

 **包安装使用：**

    
    
    ./maigret.py user

 **克隆代码库使用：**

    
    
    maigret user

### 功能使用

 **制作HTML和PDF报告：**

    
    
    maigret user --html --pdf

 **搜索带有photo和dating标签的网站：**

    
    
    maigret user --tags photo,dating

 **在所有网站上搜索三个用户名：**

    
    
    maigret user1 user2 user3 -a

 **使用下列命令可获取所有参数的介绍：**

    
    
    maigret --help

## Docker使用

 **手动构建：**

    
    
    docker build -t maigret . && docker run maigret user

 **官方镜像：**

    
    
    docker run soxoj/maigret:latest user

## 工具运行演示

![](https://image.3001.net/images/20210406/1617710441_606c4d694bbacd62ff341.png!small)

![](https://image.3001.net/images/20210406/1617710451_606c4d736bce4c7824231.png!small)

## 页面解析和用户名递归搜索示例

演示GIF：https://github.com/soxoj/maigret/blob/main/static/recursive_search.svg

PDF报告：https://github.com/soxoj/maigret/blob/main/static/report_alexaimephotographycars.pdf

HTML报告：https://htmlpreview.github.io/?https:/raw.githubusercontent.com/soxoj/maigret/main/static/report_alexaimephotographycars.html

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

Maigret：https://github.com/soxoj/maigret

