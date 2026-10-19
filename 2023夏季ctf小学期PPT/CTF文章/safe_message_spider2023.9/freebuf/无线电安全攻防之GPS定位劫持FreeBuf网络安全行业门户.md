# 一、需要硬件设备

HackRF

HackRF 连接数据线

外部时钟模块（TCXO 时钟模块）

天线（淘宝套餐中的 700MHz-2700MHz 吸盘天线）

![1648695744_624519c0713c1b7aaa1f4.png!small?1648695742824](https://image.3001.net/images/20220331/1648695744_624519c0713c1b7aaa1f4.png!small?1648695742824)图1，天线实物图

# 二、需要软件应用

hackrf-tools

[Google Earth Pro](https://www.google.com/earth/versions/#earth-pro)

[gps-sdr-sim](https://github.com/osqzss/gps-sdr-sim)

[SatGen Trajectory
Generation](https://files.cnblogs.com/files/k1two2/SatGenNMEAFree.zip)

# 三、操作流程概述

用 Google Earth Pro 制作运动轨迹坐标 kml 文件

前往 NASA 官网下载 GPS 导航电文

用 gps-sdr-sim 将 GPS 导航电文和运动轨迹坐标 kml 文件生成采样文件

hackrf_transfer 发射 GPS 欺骗信号

# 四、运动轨迹坐标文件

Google Earth Pro 查看国内地图会存在火星偏移，即卫星图与显示地名、街道信息不对应，以卫星图为准！

启动 Google Earth Pro ，寻找需要模拟地点，点击添加路径：

![1648695758_624519ced0641f5db6b73.png!small?1648695757367](https://image.3001.net/images/20220331/1648695758_624519ced0641f5db6b73.png!small?1648695757367)

图2，Google Earth Pro演示图1

用鼠标点击图上勾画出路径：

![1648695765_624519d5de047e40f1496.png!small?1648695764531](https://image.3001.net/images/20220331/1648695765_624519d5de047e40f1496.png!small?1648695764531)

图3，模拟轨迹图

绘图完成并保存后，在位置可以找到保存的路径，右键将位置另存为导出kml文件：

![1648695773_624519dda54ce1dfd75ed.png!small?1648695772213](https://image.3001.net/images/20220331/1648695773_624519dda54ce1dfd75ed.png!small?1648695772213)

图4，Google Earth Pro演示图2

kml文件内容展示：

![1648695785_624519e9426d8f6acc470.png!small?1648695783988](https://image.3001.net/images/20220331/1648695785_624519e9426d8f6acc470.png!small?1648695783988)

图5，kml文件内容

# 五、NMEA文件

NMEA 是 GPS 导航设备统一的 RTCM 标准协议，包含坐标、海拔、时间轨迹。将运动轨迹坐标 kml 文件导入 SatGen ，就会自动加载 kml
路径。

![1648695796_624519f4260b2d174849f.png!small?1648695794438](https://image.3001.net/images/20220331/1648695796_624519f4260b2d174849f.png!small?1648695794438)

图6，SatGen软件截图

### 5.1 调参拟合

调整参数将速度轨迹向真实情况进行拟合，SatGen 会模拟真实运动情况，如：拐弯减速、起步&结束停留……

output 数据更新率

max longacc 最大纵向加速度

max jerk 最大加速度

max latacc 最大横向加速度

max speed 最大速度

stationary period 起步停留时间

stationary period end 结束停留时间

scenario distance 总路程长度

total time 总耗时  
  
---  
  
点击 `Generate NMEA file` ，即可生成标准的 NMEA 轨迹文件

![1648695853_62451a2d55b94d90a4796.png!small?1648695851841](https://image.3001.net/images/20220331/1648695853_62451a2d55b94d90a4796.png!small?1648695851841)

图7，NMEA文件内容

GPGGA 格式，其内容定义如下：

![1652171938_627a24a249faedbfae0b8.png!small?1652171939152](https://image.3001.net/images/20220510/1652171938_627a24a249faedbfae0b8.png!small?1652171939152)

图8

### 5.2 绕圈轨迹制作

要制作绕圈跑的 NMEA 轨迹只需要画一圈，将 NMEA 文件内容复制粘贴即可：

$GPGGA,090453.93,2306.36704898,N,11328.49988987,E,1,05,2.87,160.00,M,-21.3213,M,,*7C

$GPGGA,090454.00,2306.36704898,N,11328.49988987,E,1,05,2.87,160.00,M,-21.3213,M,,*71

……

$GPGGA,090453.93,2306.36704898,N,11328.49988987,E,1,05,2.87,160.00,M,-21.3213,M,,*7C

$GPGGA,090454.00,2306.36704898,N,11328.49988987,E,1,05,2.87,160.00,M,-21.3213,M,,*71

……  
  
---  
  
# 六、GPS导航电文

GPS
卫星发送的导航电文是每秒50位的连续的数据流，每颗卫星都同时向地面发送以下信息：系统时间、时钟校正值、自身精确的轨道数据、其他卫星的近似轨道信息、电离层模型参数和世界协调时（UTC）数据等系统状态信息。

导航电文用于计算卫星当前的位置和信号传输的时间，从而使 GPS 接收机在接收导航电文后能确定自身的位置。

各个接收机厂商普遍采用统一的 RINEX 格式，RINEX 本质上是文本文件，RINEX
文件遵循标准的[命名规则](https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/RINEX_Version_3.html)，具体如下图所示：

![1652171949_627a24adb143b5c438438.png!small?1652171950482](https://image.3001.net/images/20220510/1652171949_627a24adb143b5c438438.png!small?1652171950482)

图9

### 6.1 获取GPS导航电文

可以在NASA官网上获取 RINEX 格式的GPS导航电文，原
[ftp](ftp://cddis.gsfc.nasa.gov/pub/gps/data/daily) 地址在 2020 年 10 月由于安全原因停止使用。

现在下载地址为：https://cddis.nasa.gov/archive/gnss/data/daily/

武汉大学IGS数据中心也可以下载广播星历，数据延迟一天。http://www.igs.gnsswhu.cn/index.php/home/data_product/igs.html

![1648695900_62451a5c956cedda4ae2c.png!small?1648695898787](https://image.3001.net/images/20220331/1648695900_62451a5c956cedda4ae2c.png!small?1648695898787)

图10，GPS导航电文1

打开选择最新的年份，然后滑到最底部的 brdc ，点开找最新的导航电文（`n.gz` 结尾）：

![1648695911_62451a67992d4862e9c98.png!small?1648695910052](https://image.3001.net/images/20220331/1648695911_62451a67992d4862e9c98.png!small?1648695910052)

图11，GPS导航电文2

### 6.2 GPS导航电文定义

解压后可以用文本编辑器打开，导航电文文件结果如图所示：

![1652171961_627a24b9d64f0da8a0188.png!small?1652171962740](https://image.3001.net/images/20220510/1652171961_627a24b9d64f0da8a0188.png!small?1652171962740)

图12

# 七、生成采样文件

利用 [gps-sdr-sim](https://github.com/osqzss/gps-sdr-sim) 配合 GPS 导航电文和 NMEA 文件生成
HackRF 发射信号需要的采样文件。

git clone https://github.com/osqzss/gps-sdr-sim.git  
  
---  
  
### 7.1 修改动态模式时间上限

gps-sdr-sim 默认动态模式最大只能生成 300s ；静态模式 86400s （10Hz）。结合实际情况修改 `gpssim.h`
的`USER_MOTION_SIZE` 实现自定义时间上限。

将 `USER_MOTION_SIZE` 调得比 NMEA 轨迹总耗时长 30s 以上。HackRF 开始发出信号，到手机 GPS
被欺骗需要一定时间（30s左右），所以时间上限比时间时间多加 30s ，让定位稳定被欺骗，以防在模拟定位与真实定位之间跳变。

最终运行作用时长取决于较短的那个时间。假如轨迹总耗时 400s ，`USER_MOTION_SIZE` 定义动态模拟时间上限 300s ，最终运行 300s
。

#3000 == 300s

make USER_MOTION_SIZE=3000  
  
---  
  
### 7.2 编译gps-sdr-sim

gcc gpssim.c -lm -O3 -o gps-sdr-sim

用法：gps-sdr-sim [选项]

选项：

-e <gps_nav>用于GPS星历表的RINEX导航文件（必填）

-u <user_motion>用户动作文件（动态模式）

-g <nmea_gga> NMEA GGA流（动态模式）

-c <位置> ECEF X，Y，Z，以米为单位（静态模式），例如3967283.15,1022538.18,4872414.48

-l <位置> Lat，Lon，Hgt（静态模式），例如30.286502,120.032669,100

-t <日期，时间>场景开始时间YYYY / MM / DD，hh：mm：ss

-T <日期，时间>将TOC和TOE覆盖到方案开始时间

-d <欺骗时间>持续时间[秒]（动态模式最大值：300静态模式最大值：86400）

-o <输出> I/Q采样数据文件（默认值：gpssim.bin;使用 - 用于stdout）

-s <频率>采样频率[Hz]（默认值：2600000）

-b <iq_bits> I/Q数据格式[1/8/16]（默认值：16）

-i 禁用航天器场景的电离层延迟

-v 显示有关模拟频道的详细信息  
  
---  
  
### 7.3 生成采样文件

./gps-sdr-sim -e <导航电文文件> -g <轨迹文件> -b 8 -o <输出二进制文件路径>

`-b 8`：降低输出文件大小。hackrf 支持的是8-bit的二进制文件，其他 sdr 查询
[readme](https://github.com/osqzss/gps-sdr-sim)  
  
---  
  
# 八、发射GPS欺骗信号

### 8.1 hackrf-tools 安装

Mac brew 直接安装：

brew install hackrf  
  
---  
  
连接上 hackrf 之后，`hackrf_info` 查看连接是否成功：

![1648695945_62451a89ddee279f638c6.png!small?1648695944355](https://image.3001.net/images/20220331/1648695945_62451a89ddee279f638c6.png!small?1648695944355)

图12，hackrf连接测试

### 8.2 安装外部TCXO（时钟晶振）

![1648695956_62451a94d2b05a8546f54.png!small?1648695955518](https://image.3001.net/images/20220331/1648695956_62451a94d2b05a8546f54.png!small?1648695955518)

图13，时钟晶振

安装 TCXO 后，使用` hackrf_debug -–si5351c -n 0 -r`检查 TCXO 是否被识别和使用。输出` [0] ->
0x01`表示使用 TCXO，而` [0] -> 0x51`表示不使用 TCXO。

### 8.3 发射信号

hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000 -a 1 -x 20 -R

* -t：信号采样文件（gps-sdr-sim 生成的 bin 文件）

* -f：频率赫兹；美国官方的GPS L1信号频段1575420000Hz

* -s：HackRF 采样速率 2.6Msps（其他 sdr 查看 [readme](https://github.com/osqzss/gps-sdr-sim) ）

* -a：放大器使能，接收/发射射频放大器：1=使能；0=禁用

* -x：增益分贝，TX VGA(中频)增益，0-47db；1dB步长

* -R：重复发射模式  
  
---  
  
 **山石网科安全研究技术院 ，信创** **实验室**

  

## 参考文章

https://forum.butian.net/share/230

https://www.cnblogs.com/k1two2/p/6387701.html

https://blog.csdn.net/qq_42652838/article/details/100128968

https://wooyun.js.org/drops/%E7%8B%97%E6%B1%AA%E6%B1%AA%E7%8E%A9%E8%BD%AC%E6%97%A0%E7%BA%BF%E7%94%B5%20--%20GPS%20Hacking%20(%E4%B8%8A%EF%BC%89.html

https://gpspatron.com/spoofing-a-multi-band-rtk-gnss-receiver-with-hackrf-one-and-gnss-jammer/

