iMonitor（冰镜 -终端行为分析系统）是一款基于[iMonitorSDK](https://github.com/wecooperate/iMonitorSDK)的开源终端行为监控分析软件。

提供了对进程、文件、注册表、网络等系统行为的监控。支持扩展和脚本，可以轻易定制和添加更多功能。可以用于病毒分析、软件逆向、入侵检测，EDR等。

源码：<https://github.com/wecooperate/iMonitor>

## 一些特点

  * 开源

  * 支持Win7到Win11的32位、64位系统（因为Qt用了比较新的版本不支持XP了，需要支持的可以自行换成支持XP的Qt版本）

  * 支持丰富的行为监控，支持进程打开事件、支持socket的各种操作事件

  * 支持按每个事件字段的过滤条件，支持堆栈模块的过滤条件

  *  **所有iMonitor监控到的行为，都可以通过[iMonitorSDK](https://github.com/wecooperate/iMonitorSDK)、[iDefender](https://github.com/wecooperate/iDefender)来拦截阻止**

  *  **支持脚本化和应用市场，可以无限扩展和定制功能（待支持）**

  *  **多方平台集成（待支持）**

## 源码编译

  * 需要VS2019及以上环境

  * 需要CMake 3.10 之后的版本

  * 需要安装Qt5.12（默认支持多语言，需要同时安装qtlinguistinstaller）

  * 执行目录下的build.bat即可 （此步骤会提示设置QT的安装路径，按提示设置环境变量）

## 软件截图

![image](https://image.3001.net/images/20211126/1637923103_61a0b91f7c2a930e16f7d.png)  
![image](https://image.3001.net/images/20211126/1637923121_61a0b93122adebda56a62.png)  
![image](https://image.3001.net/images/20211126/1637923138_61a0b9422a7dde525bc55.png)  
![image](https://image.3001.net/images/20211126/1637923152_61a0b950d0f9293f86ee6.png)  
![image](https://image.3001.net/images/20211126/1637923172_61a0b964deee1a9831ee0.png)

