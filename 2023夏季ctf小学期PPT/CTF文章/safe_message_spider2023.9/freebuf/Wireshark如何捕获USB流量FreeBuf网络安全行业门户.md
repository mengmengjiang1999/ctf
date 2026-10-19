**如果你满足[必要的条件](https://wiki.wireshark.org/CaptureSetup/USB)，那么你则可以使用Wireshark来捕获USB流量。**

当你开始捕获USB流量然后插入一个USB设备时，你会看到类似以下的内容：

![120180317-224903.png](https://image.3001.net/images/20180328/15222095095321.png!small)  

首先，我们看到的是一个设备描述符的请求（和响应）。

![220180317-225026.png](https://image.3001.net/images/20180328/1522209524577.png!small)  

描述符中包含了一些有趣的信息，如供应商ID（VID或idVendor）和产品ID（PID或idProduct）。也许你已经遇到过VID和PID，就像这个实例ID一样：USB\VID_0951&PID_16AE\902B341D991AB031991F4C4D

在这个设备描述符中，你还可以看到Manufacturer，Product和SerialNumber字符串描述符的索引：1，2和3。

稍后在捕获中，你将看到索引为0的字符串描述符（类型3）的请求：这实际上意味着查询用于字符串描述符的语言。

![320180317-225123.png](https://image.3001.net/images/20180328/15222095449473.png!small)  

我插入的USB设备的字符串描述符使用的语言是美国英语（0x0409）：

![420180317-225145.png](https://image.3001.net/images/20180328/15222095647934.png!small)  

有了这些信息，Windows将执行查询以获取美国英语中字符串描述符3的长度：

![520180317-225202.png](https://image.3001.net/images/20180328/15222095849497.png!small)  

长度为50字节：

![620180317-225214.png](https://image.3001.net/images/20180328/15222096498478.png!small)  

因此，Windows可以在美国英语中查询索引为3的50字节长的字符串描述符：

![720180317-225227.png](https://image.3001.net/images/20180328/1522209670954.png!small)  

并在响应中给了我们序列号（serial number）：

![820180317-225241.png](https://image.3001.net/images/20180328/15222096928560.png!small)  

最后我希望大家能使用不同的USB设备进行测试，并在评论中分享你的测试成果与发现。

***参考来源：[sans](https://isc.sans.edu/forums/diary/Wireshark+and+USB/23457/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**  

