[BTAB (Blue Team Analyisis
Box)](https://github.com/Martin2877/btab)是一个蓝队分析工具箱，专注于攻击特征分析。可以辅助安全运营人员在客户现场较苛刻环境下(无网、无python环境)的流量包分析、木马分析等场景，目前已集成流量包检测、SQL注入检测、Webshell检测、bash命令执行检测，以及解码序列化等工具。

## 下载与使用

[前往releases下载](https://github.com/Martin2877/btab/releases)，双击执行即可。启动后访问本地的
8001 端口： http://localhost:8001

注意：部分功能需要 java 环境依赖。

## 功能

初版本主要实现基本的功能和整体流程，主要包含以下三块功能：

  1. 威胁仓库：  
用于存储流量包、payload文件、webshell文件的列表；

  2. 风险检测：  
包括流量包检测、HTTP深度解析、SQLi检测、XSS检测等检测项；

  3. 辅助工具：  
包括 jq 、反序列化解析、数据加解密等处理工具；

## 议题分享文档

[btab蓝队分析工具箱-ali0th-v1.0.pdf](btab%E8%93%9D%E9%98%9F%E5%88%86%E6%9E%90%E5%B7%A5%E5%85%B7%E7%AE%B1-ali0th-v1.0.pdf)

## 功能界面截图

![image](https://image.3001.net/images/20230427/1682561166_6449d88ec02711448be17.png!small)

![image](https://image.3001.net/images/20230427/1682561188_6449d8a490c50657f3b5a.png!small)

![image](https://image.3001.net/images/20230427/1682561203_6449d8b3e519f90a73247.png!small)

