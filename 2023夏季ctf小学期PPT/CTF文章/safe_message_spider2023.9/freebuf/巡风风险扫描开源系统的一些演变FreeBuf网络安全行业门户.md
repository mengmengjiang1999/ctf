***本文原创作者：无花无酒锄作田，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

**同程SRC团队开源巡风资产风险控制系统也有一段时间了，我们临时用它作为一个简单的soc平台来使用，期间也做了一些定制化开发，此次分享，权当做个笔记吧。基于巡风我们主要做了一下几个方面的工作：**

> 1、因为要开发自己的模块，为了不使巡风的代码显得过于混乱，所以采用flask的blueprint(蓝图)对巡风的视图层进行了模块拆分。
>
> 2、后端数据越来越多且重要性比较高，为了提高数据容灾且保证SLA，就做了mongodb副本集
>
> 3、时常要用到xunfeng的资产数据，为了方便做数据分析，就开发了几个简单的api(没有做认证)
>
> 4、临时用的人越来越多，为了提高并发，就采用了nginx做反向代理
>
> 5、用的人多了，就牵涉到权限的问题，就取巧性的暂时做了个权限限制

下面一一介绍吧！

## 一、对xunfeng使用blueprint

### 1、使用blueprint 主要会对views目录下的文件有比较大的影响，views目录截图如下：

**![image.png](https://image.3001.net/images/20180417/15239686842202.png!small)  
![image.png](https://image.3001.net/images/20180417/15239687445306.png!small)  
**

原始目录结构和使用blueprint后的目录结构  

### 2、我们随便进入views目录下的两个视图模块，文件截图如下：  

![image.png](https://image.3001.net/images/20180417/15239720258770.png!small)  

### 3、如何对xunfeng使用blueprint呢，以views/view模块为例

3.1、修改__init__.py文件，截图如下：

![image.png](https://image.3001.net/images/20180417/15239692523064.png!small)  

3.2、修改view.py文件，截图如下：  

![image.png](https://image.3001.net/images/20180417/15239693887329.png!small)  

3.3、为了使views/view模块生效，我们需要修改根目录下的Run.py，截图如下：  

![image.png](https://image.3001.net/images/20180417/15239695845171.png!small)  

## 二、巡风使用mongodb副本集

### 1、mongodb副本集配置注意事项

1.1、参考 <http://www.runoob.com/mongodb/mongodb-replication.html>

1.2、mongodb配置文件，借鉴下面这个：

![image.png](https://image.3001.net/images/20180417/15239700808297.png!small)  

注意bind_ip，我当时用的0.0.0.0，没有配置成功副本集，最好指定副本集节点的IP

### 2、连接副本集配置

2.1、修改Config.py文件：

![image.png](https://image.3001.net/images/20180417/15239702963266.png!small)  

2.2、xunfeng连接mongodb副本集，修改Conn.py文件，参考截图：  

![image.png](https://image.3001.net/images/20180417/1523970498785.png!small)  

2.3、python操作mongodb副本集，采用读写分离的方式，读mongodb采用xunfeng的配置方式就可以，写mongodb参考下面的配置，参考截图：  

![image.png](https://image.3001.net/images/20180417/15239706002362.png!small)  

## 三、开发restful api

1、接口模块位置：

![image.png](https://image.3001.net/images/20180417/15239708253762.png!small)  

2、接口view.py文件参考截图：  

![image.png](https://image.3001.net/images/20180417/15239709713561.png!small)  

## 四、提高xunfeng的并发处理能力

1、安装nginx，不懂的自行百度

2、pip install uwsgi

3、uwsgi的配置参考截图：

![image.png](https://image.3001.net/images/20180417/15239712733511.png!small)  

4、启动，参考截图：

![image.png](https://image.3001.net/images/20180417/15239713404414.png!small)

## 五、简单的权限限制

1、大概效果截图：

![image.png](https://image.3001.net/images/20180417/15239714645785.png!small)  

2、需要做控制的视图（view.py)代码参考截图：

![image.png](https://image.3001.net/images/20180417/15239716161802.png!small)  

3、权限控制@is_admin代码参考截图：

![image.png](https://image.3001.net/images/20180417/15239717256676.png!small)

## **六：总结**

本人开发能力有限，希望有机会能从各位大牛身上学些东西，最后贴下巡风的开源地址：

<https://github.com/ysrc/xunfeng>

 ***本文原创作者：无花无酒锄作田，本文属FreeBuf原创奖励计划，未经许可禁止转载**

