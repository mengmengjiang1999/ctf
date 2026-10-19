![](https://image.3001.net/images/20230508/1683551617_6458f58152ee449da4ba1.jpeg!small)  

## 关于TwLocation

TwLocation是一款功能强大的网络侦查工具，该工具本质上是一个Python脚本，可以帮助广大研究人员获取Twitter用户的推文发布地理位置，并以此来检测和保护用户的隐私安全。

## 功能介绍

> 1、支持基于经纬度获取目标Twitter账号的用户名信息；
>
> 2、支持获取账号信息URL地址；
>
> 3、支持获取目标账号指定推文发布时的经纬度数据；
>
> 4、支持基于获取到的经纬度数据提供Google地图的链接；

## 工具下载

当前版本的TwLocation支持在所有的Linux发行版操作系统上运行，该工具基于Python
2.7开发，因此我们首先需要在本地设备上安装并配置好Python 2.7环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/MazenElzanaty/TwLocation.git

然后切换到项目目录中，并使用pip命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd TwLocation
    
    pip install -r requirements.txt

## 工具使用

在使用该工具之前，我们需要编辑config.txt配置文件，并提供你的Twitter应用程序密钥数据：

    
    
    cat config.txt
    
    consumer_key = "XxXxXxxXXXxxxxXXXxXX"
    
    consumer_secret = "xXXXXXXXXxxxxXxXXxxXxxXXxXxXxxxxXxXXxxxXXx"
    
    access_key = "XXXXXXXX-xxXXxXXxxXxxxXxXXxXxXxXxxxXxxxxXxXXxXxxXX"
    
    access_secret = "XxXXXXXXXXxxxXXXxXXxXxXxxXXXXXxXxxXXXXx"

现在，我们就可以运行下列命令来执行TwLocation脚本了：

    
    
    python TwLocation.py

## 工具演示视频

 **视频地址** ：【[ _点我观看_](https://www.youtube.com/watch?v=VuCOE8PwJDs)】

## 项目地址

 **TwLocation** ：【[
_GitHub传送门_](TwLocation%EF%BC%9A%E9%92%88%E5%AF%B9Twitter%E7%94%A8%E6%88%B7%E5%9C%B0%E7%90%86%E4%BD%8D%E7%BD%AE%E5%AE%89%E5%85%A8%E7%9A%84%E7%A0%94%E7%A9%B6%E5%B7%A5%E5%85%B7https%3A/github.com/MazenElzanaty/TwLocation)】

## 参考资料

> [ _https://twitter.com/MazenElzanaty_](https://twitter.com/MazenElzanaty)
>
> [
> _https://www.youtube.com/watch?v=VuCOE8PwJDs_](https://www.youtube.com/watch?v=VuCOE8PwJDs)

