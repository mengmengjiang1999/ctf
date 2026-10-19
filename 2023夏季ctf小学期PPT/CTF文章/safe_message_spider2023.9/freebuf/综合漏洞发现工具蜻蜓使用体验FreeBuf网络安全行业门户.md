一直关注QingScan，最近蜻蜓开放内测，第一时间抢先一步抢到了内测名额,使用后发现效果很赞，记录下我使用的过程。

GitHub：<https://github.com/StarCrossPortal/QingTing>

### 1\. 添加节点

点击:接入节点→添加节点,按照上面提示的内容安装docker和执行自动注册脚本。  
![](https://image.3001.net/images/20220525/1653409264_628d05f04f56ba4d83388.png!small)

#### 1.1 安装docker

    
    
    curl -sSL https://get.daocloud.io/docker | sh
    

#### 1.2 注册脚本

    
    
    curl -L http://qingting.starcross.cn/static/autoRegNode > ~/autoRegNode && chmod 755 ~/autoRegNode && ~/autoRegNode -token ed8ceeac4eac28ce9434ba86fb06c51b
    

![](https://image.3001.net/images/20220525/1653409264_628d05f0a1dfd5ff092ce.png!small)

#### 1.3 查看节点连通

刷新浏览器发现节点已连通。节点添加成功后我们去装备武器。

![](https://image.3001.net/images/20220525/1653409269_628d05f54f128652c2c3b.png!small)

### 2\. 装备武器

#### 2.1 挑选装备

访问路径：装备武器→添加装备。可以看到下图中有许多可选项的场景，每个场景中对应不同的工具，我的需求是对网站进行黑盒测试，所以此处选择“黑盒盲扫”添加。

![](https://image.3001.net/images/20220525/1653409269_628d05f5ce7d827b60467.png!small)

### 3\. 添加目标

#### 3.1 添加目标

已经选择好了所需要的武器，现在去添加目标，访问路径：点击目标管理→添加  
![](https://image.3001.net/images/20220525/1653409271_628d05f70e79b7f36835f.png!small)

#### 3.2 查看结果

等待一会后，发现扫到漏洞了，点击详情查看。工具`dirmap`、`dismap`、`masscan`、`nmap`、`rad`、`sqlmap`、`xray`都发现了漏洞。`oneforall`（子域名查询）因为我填的是ip，所以没有发现漏洞，还有些工具没扫描完。  
![](https://image.3001.net/images/20220525/1653409271_628d05f75cc7eeb372826.png!small)

##### 3.2.1 dirmap（扫目录结构工具）、dismap（指纹识别工具）扫描结果如下：

![](https://image.3001.net/images/20220525/1653409271_628d05f79a839dd907d65.png!small)

##### 3.2.2 masscan（端口扫描工具）、nmap（端口扫描工具）扫描结果如下：

![](https://image.3001.net/images/20220525/1653409272_628d05f80103383d33234.png!small)

##### 3.2.3 oneforall（子域名工具）、rad（url爬虫工具）扫描结果如下：

![](https://image.3001.net/images/20220525/1653409272_628d05f853628fefcaebd.png!small)

##### 3.2.4 rad（url爬虫工具）、sqlmap（SQL注入工具）扫描结果如下：

![](https://image.3001.net/images/20220525/1653409272_628d05f899381dd2b8017.png!small)

### 4\. 总结

    
    
    使用流程：先添加节点，再去选装备，然后添加目标开始扫描。快速的把多款工具的扫描结果展现在页面中，快速提升挖洞效率。
    

