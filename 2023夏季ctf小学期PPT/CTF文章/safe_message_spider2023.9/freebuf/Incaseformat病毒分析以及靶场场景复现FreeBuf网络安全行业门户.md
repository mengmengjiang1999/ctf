## 一、事件说明

2021-01-13日一种名为incaseformat的蠕虫在国内爆发，该蠕虫执行后将删除被感染计算机所有非系统软件，蠕虫设定的下一次删除时间为1月23日，欧米伽实验室建议各用户做好U盘防护及查杀工作。

## 二、已知样本

![图片.png](https://image.3001.net/images/20210114/1610626897_600037517d8f1b427bbd7.png!small)  
![图片.png](https://image.3001.net/images/20210114/1610626938_6000377aa5a6c382d791a.png!small)  
经过分析，1506 KB大小样本为未压缩样本，tsay样本已压缩

## 三、病毒分析

### 1、病毒信息

病毒名称：incaseformat  
病毒类型：蠕虫病毒  
病毒危害：删除用户除系统盘外的所有磁盘文件，并在磁盘的根目录下创建名为incaseformat.log文件

### 2、病毒行为

样本在windows目录下运行，会复制自身到同目录下，并且修改注册表  
![图片.png](https://image.3001.net/images/20210114/1610626957_6000378d31f0596b47808.png!small)  
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\HideFileExt的值为1  
![图片.png](https://image.3001.net/images/20210114/1610626971_6000379baaa059f437309.png!small)  
此外还会通过修改注册表，实现不显示隐藏文件及隐藏已知文件类型扩展名，涉及的注册表项包括：  
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Hidden

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\HideFileExt

HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\Hidden\SHOWALL\checkedvalue

HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\HideFileExt\checkedvalue

## 四、Incaseformat病毒靶场场景复现(仅供安全研究参考，切勿进行非法用途，否则后果自负)

### 1.靶场复现拓扑图

![图片.png](https://image.3001.net/images/20210114/1610626985_600037a94c6c2c0fab698.png!small)

### 2.靶场Rangenet附件下载

![图片.png](https://image.3001.net/images/20210114/1610626993_600037b18d7d038d33fbf.png!small)

### 3.传播场景复现

3.1 A机在已运行病毒样本情况下，插入靶场虚拟U盘

![图片.png](https://image.3001.net/images/20210114/1610627005_600037bd14f3787a6ecbc.png!small)

3.2 靶场虚拟U盘内原有文件夹被病毒成功感染。

![图片.png](https://image.3001.net/images/20210114/1610627015_600037c73459a724bf227.png!small)

3.3 B机未感染病毒主机情况

![图片.png](https://image.3001.net/images/20210114/1610627022_600037ce33982876e8c14.png!small)

3.4 插入从A机拔下已被感染的的靶场虚拟U盘

![图片.png](https://image.3001.net/images/20210114/1610627028_600037d4ca68baf9c2b16.png!small)

3.5 打开虚拟U盘查看存在病毒

![图片.png](https://image.3001.net/images/20210114/1610627036_600037dc4b747f267e3f0.png!small)

3.6 虚拟U盘内病毒运行后成功感染B机

![图片.png](https://image.3001.net/images/20210114/1610627044_600037e4eca4bbc4de336.png!small)

3.7主机 A 和主机 B 同时修改为病毒触发时间。病毒执行删除操作。

![图片.png](https://image.3001.net/images/20210114/1610627052_600037ece9e75da7fa0fc.png!small)

3.8 病毒成功执行视频【详见公众号】

[欧米伽实验室](https://mp.weixin.qq.com/s/nYyqXGurrip0PKU9z_FC1A)

## 五、查杀与恢复

### 1、主机排查

排查主机Windows目录下是否存在图标为文件夹的tsay.exe文件，若存在该文件，及时删除即可，删除前切勿对主机执行重启操作。

### 2、数据恢复

切勿对被删除文件的分区执行写操作，以免覆盖原有数据，然后使用常见的数据恢复软件（如：Finaldata、recuva、DiskGenius等）即可恢复被删除数据。

### 3、病毒清理

由于病毒出现年份较早，主流杀毒软件均可对该病毒进行查杀，用户也可通过以下手工方式进行清理修复：

1）通过任务管理器结束病毒相关进程（ttry.exe）  
2）删除Windows目录下驻留文件tsay.exe和ttry.exe及注册表相关启动项（RunOnce）  
3）恢复上述被病毒篡改的用于隐藏文件及扩展名的相关注册表项。

