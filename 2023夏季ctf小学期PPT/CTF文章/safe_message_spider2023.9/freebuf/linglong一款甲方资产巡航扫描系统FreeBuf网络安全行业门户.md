# linglong

一款资产巡航扫描系统。系统定位是通过masscan+nmap无限循环去发现新增资产，自动进行端口弱口令爆破/、指纹识别、XrayPoc扫描。主要功能包括:
`资产探测`、`端口爆破`、`Poc扫描`、`指纹识别`、`定时任务`、`管理后台识别`、`报表展示`。
使用场景是Docker搭建好之后，设置好你要扫描的网段跟爆破任务。就不要管他了，没事过来收漏洞就行了

### 功能清单

> masscan+namp巡航扫描资产
>
> 创建定时爆破任务(FTP/SSH/SMB/MSSQL/MYSQL/POSTGRESQL/MONGOD)
>
> 管理后台识别
>
> 结果导出
>
> 报表展示
>
> docker一键部署 [21-02-08]
>
> CMS识别 - 结合威胁情报、如果某个CMS爆出漏洞，可以快速定位企业内部有多少资产 [21-02-20]
>
> poc扫描 - 调用xray的Poc,对新发现的资产自动扫描poc [21-02-20]

## 预览

 **资产列表**  
![image](https://image.3001.net/images/20210225/1614236911_60374cef6e8105fd73bef.png!small)

 **敏感后台**  
![image](https://image.3001.net/images/20210225/1614236912_60374cf01968733bf4692.png!small)

 **任务详情**  
![image](https://image.3001.net/images/20210225/1614236912_60374cf0b6801d59675f8.png!small)

 **xray**  
![image](https://image.3001.net/images/20210225/1614236913_60374cf1897528aad0464.png!small)![image](https://image.3001.net/images/20210225/1614236914_60374cf25735f585bf740.png!small)

 **管理后台识别**

不论甲方乙方。大家在渗透一个网站的时候，很多时候都想尽快找到后台地址。linglong对自己的资产库进行Title识别。然后根据title关键字、url关键字、body关键字（比如url中包含login、body中包含username/password）进行简单区分后台。帮助我们渗透中尽快锁定后台。

 **指纹识别**

系统会对新发现的资产进行一遍指纹识别,
也可以手动新增指纹。比如某个CMS爆出漏洞，新增指纹扫描一遍系统中存在的资产。可以快速定位到漏洞资产，对于渗透打点或者甲方应急都是极好的

 **POC扫描**

对于任何一个扫描系统，poc扫描都是必不可少的。但是poc的更新一直是所有开源项目面临的一个问题。综合考虑用Xray的poc,感谢Xray对安全圈做出的贡献！
linglong会对每次新发现的资产进行一遍Xray的Poc扫描。如果发现漏洞会自动入库，可以可视化查看漏洞结果

 **资产巡航更新**

masscan可以无限扫描，但是对于失效资产我们也不能一直保存。linglong通过动态设置资产扫描周期，对于N个扫描周期都没有扫描到的资产会进行删除。保存资产的时效性

## 安装

### Docker安装

#### 如果部署在本地体验

如果是 **本地体验** 下，直接运行如下命令

    
    
    git clone https://github.com/awake1t/linglong
    cd linglong
    docker-compose up -d

运行结束后,运行`docker container ls -a`看下是否运行正常

### 开源地址

<https://github.com/awake1t/linglong>

