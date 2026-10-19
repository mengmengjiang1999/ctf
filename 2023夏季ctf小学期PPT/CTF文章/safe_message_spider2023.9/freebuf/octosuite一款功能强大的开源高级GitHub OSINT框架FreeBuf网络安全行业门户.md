![](https://image.3001.net/images/20220416/1650113668_625abc842d190eb06514c.png!small)

## 关于octosuite

octosuite是一款功能强大的高级GitHub公开资源情报（OSINT）框架，广大研究人员可以使用该工具收集针对目标GitHub库的相关信息。

## 功能介绍

> 获取组织信息
>
> 获取用户信息
>
> 获取代码库信息
>
> 返回代码库路径内容
>
> 返回组织拥有的代码库列表
>
> 返回用户拥有的代码库列表
>
> 返回用户拥有的gist列表
>
> 返回用户的粉丝Follower列表
>
> 检测用户A是否关注了用户B
>
> 搜索用户信息
>
> 搜索代码库
>
> 搜索topic话题
>
> 搜索issue问题
>
> 搜索commit提交
>
> 支持“update”命令一键更新
>
> 自动记录网络活动（存储在.logs目录中）

## 工具安装

octosuite基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/rly0nheart/octosuite.git

![](https://image.3001.net/images/20220416/1650113709_625abcadb8a50e5283a6f.jpeg!small)

接下来使用下列命令切换至项目目录中：

    
    
    cd octosuite

![](https://image.3001.net/images/20220416/1650113719_625abcb780513f1777a25.jpeg!small)

使用下列命令安装该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

![](https://image.3001.net/images/20220416/1650113728_625abcc068b8ca37c1d21.jpeg!small)

除此之外，我们还可以直接使用PyPI安装octosuite：

    
    
    pip install octosuite

![](https://image.3001.net/images/20220416/1650113737_625abcc98d5afc171f851.jpeg!small)

## GitHub Fork使用

 **Linux**

    
    
    sudo chmod +x octosuite

![](https://image.3001.net/images/20220416/1650113747_625abcd30b777322ef9c0.jpeg!small)

    
    
    sudo ./octosuite

![](https://image.3001.net/images/20220416/1650113753_625abcd93c5e30a8a0ffa.jpeg!small)

 **Windows**

    
    
    python3 octosuite

 **macOS**

    
    
    python3 octosuite

## 工具可用指令

 ** **命令****

|

 ** **描述****  
  
---|---  
  
info:org

|

获取组织信息  
  
info:user

|

获取用户信息  
  
info:repo

|

获取代码库信息  
  
info:dev

|

显示开发者信息  
  
path:contents

|

返回代码库路径内容  
  
repos:org

|

返回组织拥有的代码库列表  
  
repos:user

|

返回用户拥有的代码库列表  
  
user:gists

|

返回用户拥有的gist列表  
  
user:followers

|

返回用户的粉丝Follower列表  
  
user:following

|

检测用户A是否关注了用户B  
  
search:users

|

搜索用户信息  
  
search:repos

|

搜索代码库  
  
search:topics

|

搜索topic话题  
  
search:issues

|

搜索issue问题  
  
search:commits

|

搜索commit提交  
  
update

|

更新octosuite  
  
changelog

|

显示版本修改信息  
  
help

|

显示工具帮助信息  
  
exit

|

退出会话  
  
## 工具运行截图

![](https://image.3001.net/images/20220416/1650113796_625abd047acd8300605f4.png!small)

## 开发版本下载

 **octosuite v1.5.2-alpha版本：** 【[
_点我下载_](https://github.com/rly0nheart/octosuite/releases/tag/1.5.2-alpha)】

## 许可证信息

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/rly0nheart/octosuite/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **octosuite：** 【[ _GitHub传送门_](https://github.com/rly0nheart/octosuite)】

## 参考资料

> [ _https://pypi.org/project/octosuite_](https://pypi.org/project/octosuite)
>
> [ _https://about.me/rly0nheart_](https://about.me/rly0nheart)

