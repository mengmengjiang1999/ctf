![](https://image.3001.net/images/20220315/1647339904_62306980157964c3681d8.png!small)

## 关于GeoWiFi

GeoWiFi是一款功能强大的WiFi定位工具，该工具可以通过BSSID和SSID并搜索各种不同的公开数据库，来定位WiFi并获取地理位置数据。

## 公开数据库

> [ _Wigle_](https://wigle.net/)
>
> Apple
>
> [ _OpenWifi_](https://openwifi.su/)
>
> [ _Milnikov_](https://www.mylnikov.org/)

## 工具要求

> 1、[ _Python_ _3_](https://www.python.org/download/releases/3.0/)
>
> 2、为了在WIndows平台上显示emoji表情，我们建议广大用户安装[
> _新版本的Windows终端_](https://www.microsoft.com/en-us/p/windows-> terminal/9n0dx20hk701)。
>
> 3、如需使用Wigle服务，这需要获取一个[
> _API_](https://api.wigle.net/)并配置“utils/API.yaml”文件，使用[
> _Wigle_](https://wigle.net/account)提供的“Encoded for
> use”数据替换其中“wigle_auth”参数的值。这一步骤对于搜索SSID至关重要！

## 工具安装

该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python
3环境。配置完成后，就可以使用下列命令将该项目源码克隆至本地了：

    
    
    git clone https://github.com/GONZOsint/geowifi.git

接下来，使用pip包管理器来安装该工具所需的依赖组件：

    
    
    python3 -m pip install -r requirements.txt

## 工具使用

    
    
    usage: geowifi.py [-h] (-s SSID | -b BSSID) [-j] [-m]
    
     
    
     
    
    optional arguments:
    
      -h, --help               显示帮助信息和退出
    
      -s SSID, --ssid SSID     通过SSID搜索WiFi数据
    
      -b BSSID, --bssid BSSID  通过BSSID搜索WiFi数据
    
      -j, --json                将数据以JSON格式输出
    
      -m, --map               地图数据输出

## 工具使用

通过BSSID搜索WiFi地理位置数据：

    
    
    python3 geowifi.py -b BSSID

通过SSID搜索WiFi地理位置数据：

    
    
    python3 geowifi.py -s SSID

我们还可以使用“-j”参数来将工具执行结果导出为JSON格式，并使用“-m”参数在HTML地图中显示WiFi地理位置信息。

## HTML地图输出样例

![](https://image.3001.net/images/20220315/1647340014_623069eea05d23171c838.png!small)

## JSON数据输出样例

    
    
    {
    
       "data":{
    
          "bssid":"A0:XX:XX:XX:6F:90",
    
          "vendor":"TP-LINK TECHNOLOGIES CO.,LTD.",
    
          "mac_type":"MA-L",
    
          "wigle":{
    
             "lat":00.000908922099,
    
             "lon":00.000945220028
    
          },
    
          "apple":{
    
             "lat":"not_found",
    
             "lon":"not_found"
    
          },
    
          "openwifi":{
    
             "lat":00.000808900099,
    
             "lon":00.000845500028
    
          },
    
          "milnikov":{
    
             "lat":"not_found",
    
             "lon":"not_found"
    
          }
    
       }
    
    }

## 项目地址

 **GeoWiFi：** 【[ _GitHub传送门_](https://github.com/GONZOsint/geowifi)】

## 参考资料

> [ _https://wigle.net/_](https://wigle.net/)
>
> [ _https://openwifi.su/_](https://openwifi.su/)
>
> [ _https://www.mylnikov.org/_](https://www.mylnikov.org/)
>
> [ _https://api.wigle.net/_](https://api.wigle.net/)
>
> [ _https://www.microsoft.com/en-us/p/windows-> terminal/9n0dx20hk701_](https://www.microsoft.com/en-us/p/windows-> terminal/9n0dx20hk701)
>
> [
> _https://www.python.org/download/releases/3.0/_](https://www.python.org/download/releases/3.0/)

