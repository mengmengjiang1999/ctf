![](https://image.3001.net/images/20211122/1637566657_619b48c1bb7866f0286e5.jpg!small)

## 关于Terra

Terra是一款功能强大的公开资源情报工具（OSINT），该工具主要针对的是Twitter和Instagram数据，广大研究人员可以利用Terra在这两个社交媒体平台上实现信息收集和数据获取。

## 支持的社交媒体平台

> Twitter
>
> Instagram

## 工具安装

首先，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/xadhrit/terra.git

接下来，在命令行终端中修改当前工作目录：

    
    
    $ cd terra

运行下列命令，安装该工具所需的依赖组件:

    
    
    $ python3 -m pip install -r requirements.txt

## 注意事项

### 针对Twitter[ _凭证_](https://www.kitploit.com/search/label/Credentials)

在使用Terra时，我们需要将Twitter凭证信息存储至项目creds目录下的twitter.yml文件中，具体可以参考[ _Twitter
API_](https://www.kitploit.com/search/label/Twitter%20Api)信息，或前往Twitter的[
_开发者门户网站_](https://developer.twitter.com/en/docs)获取访问令牌。

### 针对Instagram凭证

在使用Terra时，我们需要将Instagram的用户名和密码存储至creds/insta.yml文件中。

## 工具使用

![](https://image.3001.net/images/20211122/1637566687_619b48df4865fffe14ae5.png!small)

### 基础使用

    
    
    ~/terra$ python3 terra.py <username of target>
    help :  -j  将结果存储至JSON文件中
           -f  处理文本文件

### Twitter侦察命令

    
    
    ls:  显示所有可用的Terra命令
    help: 获取帮助信息
    quit: 退出程序运行
    clear: 清理终端信息
    exit: 退出Terra
    reset target : 在命令行中重置新的目标
    tweets : 获取目标Twitter用户最新发布的推文
    favtweets :获取目标Twitter用户最新收藏的推文
    followers : 获取目标的粉丝列表
    following : 获取目标的关注列表
    info: 获取目标用户信息概览
    profile pic: 下载目标账号的头像
    banner: 下载目标账号的信息页背景图
    htags : 获取目标账号使用的Hashtag

### Instagram侦察命令

    
    
    ls:  显示所有可用的Terra命令
    help: 获取帮助信息
    quit: 退出程序运行
    clear: 清理终端信息
    exit: 退出Terra
    locations : 获取聚标绑定的地理位置
    captions : 获取目标的标题信息
    reset target: 在命令行中重置新的目标
    comments : 获取目标所有的评论
    followers : 获取目标的粉丝列表
    followings: 获取目标的关注列表
    followers emails : 获取目标账号粉丝的电子邮箱
    following emails : 获取目标账号关注的账号邮箱
    followers phone : 获取目标账号粉丝的
    followings phone : 获取目标账号关注的手机号码
    tags  : 获取目标账号使用的Hashtag
    timeline : 获取目标账号概览
    likes: 获取目标的点赞数量
    mediatype : 获取目标的照片和视频信息
    photodes : 获取目标的照片描述
    photos  : 下载目标照片
    profile pic : 下载目标账号头像
    stories : 下载目标账号的故事信息
    tagged': 获取目标账号标记的用户列表
    commenter': 获取目标发布信息的评论用户

## 项目地址

 **Terra：** 【[ _GitHub传送门_](https://github.com/xadhrit/terra)】

## 参考资料

> [ _https://github.com/bear/python-twitter_](https://github.com/bear/python-> twitter)
>
> [
> _https://github.com/ping/instagram_private_api_](https://github.com/ping/instagram_private_api)

