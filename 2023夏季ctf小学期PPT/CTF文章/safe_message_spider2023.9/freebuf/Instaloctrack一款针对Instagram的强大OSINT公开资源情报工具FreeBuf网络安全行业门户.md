![](https://image.3001.net/images/20220223/1645628881_62164dd121c195e6f647f.png!small)  

## 关于Instaloctrack

Instaloctrack是一款针对Instagram的功能强大的OSINT公开资源情报收集工具。在该工具的帮助下，广大研究人员可以轻松收集目标Instagram账户配置文件上可用的所有地理标记位置，以便将其绘制在地图上，然后将其转储到JSON中。

## 工具运行机制

该工具基于Selenium的webdriver实现其功能，因此Instaloctrack才能够爬取整个目标Instagram配置文件来检索帐户的所有数据以及图片链接。

接下来，工具将会异步检索每个图片链接，检查它是否包含图片描述中的位置，如果存在位置数据，则检索该位置的数据以及时间戳。

注意：由于2018年Instagram不推荐使用其位置API，并且无法再获取图片的GPS坐标，我们只能检索位置的名称。

因为Instagram不提供GPS坐标，我们只知道地名，所以我们必须对这些地名进行地理编码（即根据地名处获取GPS坐标）。为了实现该功能，我们使用了Namingm的API，这个API使用了OpenStreetMap，能够帮助我们获取到GPS坐标数据。

拿到了所有的GPS坐标，我们就会生成一个嵌入了Javascript的HTML，这个页面可以绘制一张地图，并将坐标数据标记到地图上。

除此之外，整个过程中所收集到的数据（位置名称、时间戳、GPS坐标、错误信息）都将被存储到JSON文件中，以供后续使用。

## 工具依赖安装

    
    
    sudo apt install chromium-chromedriver && chmod a+x /usr/bin/chromedriver

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并使用pip3命令完成工具的安装：

    
    
    git clone https://github.com/bernsteining/instaloctrack
    
    cd instaloctrack
    
    pip3 install

或者，我们也可以使用Docker安装：

    
    
    sudo docker build -t instaloctrack -f Dockerfile .

## 工具使用

### 查看工具帮助信息

    
    
    instaloctrack -h
    
    usage: instaloctrack [-h] [-t TARGET_ACCOUNT] [-l LOGIN] [-p PASSWORD] [-v]
    
     
    
    Instagram location data gathering tool. Usage: python3 instaloctrack.py -t <target_account>
    
     
    
    optional arguments:
    
      -h, --help             显示帮助信息和退出
    
      -t TARGET_ACCOUNT, --target TARGET_ACCOUNT
    
                            目标Instagram帐号
    
      -l LOGIN, --login LOGIN
    
                            需要连接、登录和访问的目标Instagram帐号
    
      -p PASSWORD, --password PASSWORD
    
                            目标Instagram帐号的密码
    
      -v, --visual            生成Chromium GUI实现可视化

比如说：

    
    
    instaloctrack -t <target_account>

如果目标帐号是隐私帐号，而你手上有一个已经关注了目标账号的Instagram帐号的话，你就可以使用一个连接会话来爬取目标帐号的数据了：

    
    
    instaloctrack -t <target_account> -l <your_account> -p <your_password>

或者，使用Docker也可以实现同样的功能：

    
    
    sudo docker run -v /tmp/output:/tmp/output instaloctrack -t <target_account> -o /tmp/output

## 工具使用样例

下面的工具使用样例总，将输出某用户Instagram帐号（[
_@fhollande_](https://www.instagram.com/fhollande/?hl=fr)）的各种数据：

![](https://image.3001.net/images/20220223/1645628935_62164e077f2fbe7f3ff4d.png!small)

热力图：

![](https://image.3001.net/images/20220223/1645628942_62164e0eb91d4d824deca.png!small)

点击地图标记之后，会弹出相关的详细信息：

![](https://image.3001.net/images/20220223/1645628950_62164e161efe3a026700b.png!small)

有关位置数据的统计信息：

![](https://image.3001.net/images/20220223/1645628957_62164e1d438706bb0cd05.png!small)

导出的部分JSON数据：

    
    
    {
    
        "link": "https://www.instagram.com/p/-Q_9EvR9eu",
    
        "place": {
    
          "id": "290297",
    
          "name": "Musée du quai Branly - Jacques Chirac",
    
          "slug": "musee-du-quai-branly-jacques-chirac",
    
          "street_address": " 37 quai Branly",
    
          " zip_code": " 75007",
    
          " city_name": " Paris",
    
          " region_name": " ",
    
          " country_code": " FR"
    
        },
    
        "timestamp": "2015-11-19",
    
        "gps": {
    
          "lat": "48.8566969",
    
          "lon": "2.3514616"
    
        }
    
      }

## 工具演示视频

 **asciinema：**[
_https://asciinema.org/a/IeWgAH6UuxPokyGxp8uUl1Xw3_](https://asciinema.org/a/IeWgAH6UuxPokyGxp8uUl1Xw3)

 **youtu*be：** _https://www.youtu*be.com/watch?v=XVouSOwRDGE_

## 项目地址

 **Instaloctrack：** 【[
_GitHub传送门_](https://github.com/bernsteining/instaloctrack)】

## 参考资料

> [
> _https://operations.osmfoundation.org/policies/nominatim/_](https://operations.osmfoundation.org/policies/nominatim/)
>
> [ _https://github.com/Leaflet/Leaflet_](https://github.com/Leaflet/Leaflet)
>
> [
> _https://www.instagram.com/fhollande/?hl=fr_](https://www.instagram.com/fhollande/?hl=fr)
>
> [ _https://geo.api.gouv.fr/adresse_](https://geo.api.gouv.fr/adresse)
>
> [ _https://pypi.org/project/geopy/﻿_](https://pypi.org/project/geopy/)

