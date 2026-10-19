![](https://image.3001.net/images/20210501/1619841481_608cd1c98ce4dd8bcf1c0.jpg!small)

## Fav-up

Fav-up是一款功能强大的IP查询工具，该工具可以通过Shodan和Favicon（网站图标）来帮助研究人员查询目标服务或设备的真实IP地址。

## 工具安装

首先，该工具需要本地设备安装并部署好Python 3环境。然后广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/pielco11/fav-up.git

接下来， 运行下列命令安装好Fav-up所需的依赖组件：

    
    
    pip3 install -r requirements.txt

除此之外，你还需要一个Shodan API密钥！

## 工具使用

### 命令行接口

首先，你需要确定如何传递你的API密钥：

-k或--key：向stdin传递密钥；

-kf或--key-file：传递获取密钥的目标文件名；

-sc或--shodan-cli：从Shodan命令行接口获取密钥；

配置好密钥之后，我们就能够以下列几种不同方式使用Fav-up了：

-f或--favicon-file：在本地存储的需要查询的Favicon网站图标文件；

-fu或--favicon-url：无需在本地存储Favicon网站图标，但是需要知道目标图标的实际URL地址；

-w或--web：如果你不知道Favicon网站图标的实际URL，可以直接传递目标站点地址；

-fh或--favicon-hash：在全网搜索Favicon网站图标哈希；

你可以指定包含了Favicon网站图标的URL和域名的输入文件，或者直接提供Favicon网站图标的本地存储路径：

-fl或--favicon-list：文件包含所有待查询Favicon网站图标的完整路径；

-ul或--url-list：文件包含所有待查询Favicon网站图标的完整URL地址；

-wl或--web-list：

当然了，你也可以将搜索结果存储至一个CSV/JSON文件中：

-o或--output：指定数据输出文件和格式，比如说csv，它会将存储结果存储至一个CSV文件中；

## 工具使用样例

### Favicon-file

    
    
    python3 favUp.py --favicon-file favicon.ico -sc

### Favicon-url

    
    
    python3 favUp.py --favicon-url https://domain.behind.cloudflare/assets/favicon.ico -sc

### Web

    
    
    python3 favUp.py --web domain.behind.cloudflare -sc

## 作为模块导入使用

    
    
    from favUp import FavUp
    
     
    
    f = FavUp()          
    
    f.shodanCLI = True
    
    f.web = "domain.behind.cloudflare"
    
    f.show = True
    
    f.run()
    
     
    
    for result in f.faviconsList:
    
        print(f"Real-IP: {result['found_ips']}")
    
    print(f"Hash: {result['favhash']}")

## 所有属性

 ** **变量****

|

 ** **类型****  
  
---|---  
  
FavUp.show

|

布尔  
  
FavUp.key

|

字符串  
  
FavUp.keyFile

|

字符串  
  
FavUp.shodanCLI

|

布尔  
  
FavUp.faviconFile

|

字符串  
  
FavUp.faviconURL

|

字符串  
  
FavUp.web

|

字符串  
  
FavUp.shodan

|

Shodan 类  
  
FavUp.faviconsList

|

列表[字典]  
  
## 工具使用截图

![](https://image.3001.net/images/20210501/1619841568_608cd220ce5f41de34613.png!small)

![](https://image.3001.net/images/20210501/1619841575_608cd2276f08585fbc39b.png!small)

## 项目地址

 **Fav-up：** https://github.com/pielco11/fav-up

