### 一、简述

鼎信云WAF社区版，是鼎信安全团队专门为中小企业应用安全打造的一款开源云WAF。
鼎信安全团队通过将开源ModSecurity封装，实现便于界面操作的云化WAF，并实现和HFish蜜罐联动封禁、操作系统级黑名单封禁、多WAF数据联动、租户管理等功能。

可实现界面化被防护网站业务系统添加、界面化防护规则添加、数据统计，详细功能如下：

  * 大屏展示。

  * 站点管理：添加、删除、修改网站。

  * 资产管理：被保护网站单位信息留存。

  * 安全设置：黑白名单、策略放过、网站防护策略、系统策略、防护日志、自定义报告、月报。

  * 系统管理：配置模块、管理员模块、角色模块、菜单模块、登录日志、操作日志。

  * 二级权限管理，即管理员可以看到所有用户的防护情况，用户只能看到自己业务的防护情况。

适用于中小企业资金有限的云化应用防御。易于使用，下载虚拟机启动即可使用。

### [](https://github.com/ziluobu/DRUST-WAF-Community#%E4%BA%8C%E5%8A%9F%E8%83%BD%E6%88%AA%E5%9B%BE)二、功能截图

功能展示：

大屏：

[![](https://image.3001.net/images/20221213/1670916838_63982ae6a436c00221dfa.png!small)](https://github.com/ziluobu/DRUST-WAF-Community/blob/master/img/%E5%A4%A7%E5%B1%8F.png)

首页：

[![](https://image.3001.net/images/20221213/1670916854_63982af6961c659672580.png!small)](https://github.com/ziluobu/DRUST-WAF-Community/blob/master/img/%E9%A6%96%E9%A1%B5.png)

[![](https://image.3001.net/images/20221213/1670916866_63982b021b0af760adbb3.png!small)](https://github.com/ziluobu/DRUST-WAF-Community/blob/master/img/%E9%A6%96%E9%A1%B51.png)

系统：

[![](https://image.3001.net/images/20221213/1670916877_63982b0de30097846583b.png!small)](https://github.com/ziluobu/DRUST-WAF-Community/blob/master/img/%E7%B3%BB%E7%BB%9F.png)

日志：

[![](https://image.3001.net/images/20221213/1670916887_63982b17dc7bffdcdfbad.png!small)](https://github.com/ziluobu/DRUST-WAF-Community/blob/master/img/%E6%97%A5%E5%BF%97.png)

### [](https://github.com/ziluobu/DRUST-WAF-Community#%E4%B8%89%E5%AE%89%E8%A3%85%E4%B8%8E%E4%BD%BF%E7%94%A8)三、安装与使用

#### 传送门：

https://github.com/ziluobu/DRUST-WAF-Community

#### [](https://github.com/ziluobu/DRUST-WAF-Community#%E8%B5%84%E6%BA%90%E9%9C%80%E6%B1%82)资源需求：

CPU6核，内存12G，硬盘100G

#### [](https://github.com/ziluobu/DRUST-WAF-Community#%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%AE%89%E8%A3%85%E6%8E%A8%E8%8D%90)虚拟机安装[推荐]

下载方式：

迅雷网盘链接[Releases](https://github.com/ziluobu/DRUST-WAF-Community/releases)

从迅雷网盘下载DRUST-WAF-Community虚拟机到本地

解压密码 www.dingxinsec.com.cn

首次使用：

1、使用VMWARE启动DRUST-WAF-Community.vmx

2、访问<http://192.168.166.129:10088/>默认用户名：admin密码：Admin@123

3、根据自身环境修改服务器IP地址。服务器用户名：root密码：root

服务启动与关闭：

1、服务默认随系统自动启动。

2、如需重启可执行`/usr/local/apache/bin/apachectl restart`

### [](https://github.com/ziluobu/DRUST-WAF-Community#%E6%BA%90%E7%A0%81%E5%AE%89%E8%A3%85%E4%B8%8D%E6%8E%A8%E8%8D%90)源码安装[不推荐]

 **因环境搭建较为复杂，仅提供管理后台搭建方式。**

#### [](https://github.com/ziluobu/DRUST-WAF-Community#%E7%8E%AF%E5%A2%83%E8%A6%81%E6%B1%82)环境要求

    
    
    - centos  v7.x
    - php版本 >= v8.0
    - MariaDB版本 >= v10.3 or Mysql >= v5.7
    - Redis版本 >= v6.0
    - IDE推荐：PhpStorm
    
    
    
    git clone https://github.com/ziluobu/DRUST-WAF-Community.git
    

  * web项目

    
    
    cd DRUST-WAF-Community/web
    yarn install
    #.env.development 测试环境配置
    yarn run serve
    #打包
    #.env.production 生产环境配置
    yarn run build

  * server项目

    
    
    cd server
    composer update
    cp .env.example .env
    
    sh sh/buildv2.sh
    

### [](https://github.com/ziluobu/DRUST-WAF-Community#%E6%B5%8B%E8%AF%95)测试

本机host中加入`192.168.166.129 www.modsecurity.cn`

### [](https://github.com/ziluobu/DRUST-WAF-Community#%E5%9B%9B%E4%BA%A4%E6%B5%81%E4%BA%92%E5%8A%A8)四、沙龙互动

随时可加入鼎信星海安全实验室安全沙龙微信群互动。

另外鼎信安全团队还基于商用WAF内核，打造了一款用于商业市场的云防WAF，欢迎有更高安全需求的大中小型企业联系试用。

