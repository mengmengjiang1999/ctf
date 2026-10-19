![](https://image.3001.net/images/20200802/1596341273.png!small)

## reNgine

reNgine是一款针对Web应用渗透测试的自动化网络侦察框架，广大研究人员可以在针对Web应用程序的渗透测试过程中使用reNgine来实现信息收集，reNgine提供了一个自定义的扫描引擎，可以用于对网站和终端节点进行扫描和信息收集。![](https://image.3001.net/images/20200802/1596341282.png!small)

reNgine的优点在于它把所有的东西都集中在了一个工具之中，并且提供了一个高度可定制的的侦察方式。如果你需要对一个目标执行网络侦察，收集终端节点信息、查询目录、查询文件、抓取屏幕截图并获取所有处理结果时，reNgine就非常有用了。

比如说，我们现在的目标域名为hackerone.com，reNgine可以根据扫描引擎的配置来执行扫描任务，并将结果进行汇总显示。比如说，你想要搜索页面标题为“Dashboard”且页面状态为200的所有页面，并且想直接看到屏幕截图，那么reNgine就可以帮助你实现这个目的。或者说，你想要枚举出全部使用了PHP并且HTTP状态为200的子域名，reNgine同样可以实现。

在终端节点部分，reNgine能够使用类似gau、hakrawler的工具来收集关于目标URL节点的信息。除此之外，如果想要搜索包含.php后缀和HTTP状态为200的页面，reNgine同样可以做到。

### 注意事项

  * reNgine并非一款漏洞扫描工具！
  * reNgine使用了很多其他的开源工具，reNgine的扫描结果准确度会受到其他工具的影响。

## 工具运行机制

![](https://image.3001.net/images/20200802/1596341298.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/yogeshojha/rengine.git
    
    cd rengine

### 工具要求

  * Docker：【点我安装】
  * Docker-Compose：【点我安装】
  * make

## 工具安装

目前，该工具提供了两种安装配置方法，我们建议大家使用Makefile方式：![](https://image.3001.net/images/20200802/1596341317.png!small)

如果你是通过HTTPS并在VPS中进行配置的话，Makefile可以让安装过程变得更加简单。

dotenv文件可以在安装reNgine的过程中进行更新，比如说，使用下列命令编辑文件：

    
    
    nano .env

或

    
    
    vim .env

并写入下列内容：

    
    
    AUTHORITY_NAME=reNgine
    
    AUTHORITY_PASSWORD=nSrmNkwT
    
    COMPANY=reNgine
    
    DOMAIN_NAME=recon.example.com
    
    COUNTRY_CODE=US
    
    STATE=Georgia
    
    CITY=Atlanta

接下来，使用下列命令生成证书：

    
    
    make certs

证书生成完成之后，我们就可以使用HTTPS来运行reNgine了。

构建reNgine：

    
    
    make build

## 工具使用

如果构建成功，我们就可以使用下列命令运行reNgine了：

    
    
    make up

此时，可以直接访问https://127.0.0.1或https://your_ip来使用Web应用程序了。

## 工具运行截图

![](https://image.3001.net/images/20200802/1596341368.png!small)![](https://image.3001.net/images/20200802/1596341375.png!small)

![](https://image.3001.net/images/20200802/1596341388.png!small)

## 工具演示视频

视频地址：【[ _油管链接_](https://www.youtube.com/watch?v=u8_Z2-3-o2M)】

## 许可证协议

本项目的开发与发布遵循[ _GNU GPL
v3_](https://github.com/yogeshojha/rengine/blob/master/LICENSE)开源许可证协议。

## 项目地址

reNgine：【[ _GitHub传送门_](https://github.com/yogeshojha/rengine)】

