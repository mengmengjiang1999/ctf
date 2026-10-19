## **背景**

我们发现BadUSB在linux和macos上不需要过免杀，但是无法通过windows上的杀软，于是有了以下的研究。

##  **实验准备**

BadUSB硬件和Arduino软件(https://www.arduino.cc/en/software)

##  **实验过程**

###  **代码烧录测试**

打开Arduino的ide工具，选择端口

![1658306409_62d7bf69c8e43c6b4639b.png!small?1658306410449](https://image.3001.net/images/20220720/1658306409_62d7bf69c8e43c6b4639b.png!small?1658306410449)

选中Arduino开发板

![1658306456_62d7bf98da49040e8c6c3.png!small?1658306457601](https://image.3001.net/images/20220720/1658306456_62d7bf98da49040e8c6c3.png!small?1658306457601)

编辑windows测试脚本，启动cmd命令行，实现whoami，编译上传

随即成功执行whoami，基础的模拟键盘的操作，杀软是通过的，但是一旦有恶意行为，杀软会自动查杀并阻止。

![1658306493_62d7bfbd70828ca4d4fa5.png!small?1658306494116](https://image.3001.net/images/20220720/1658306493_62d7bfbd70828ca4d4fa5.png!small?1658306494116)

###  **windows上线CS**

当然我们可以使用powershell中new-item,rm,dir,cd等命令进行操作，做一些文件的删除等等。但是我 们想要更进一步。

服务器启动./teamserver

![1658306523_62d7bfdb1ec056a148f2c.png!small?1658306523963](https://image.3001.net/images/20220720/1658306523_62d7bfdb1ec056a148f2c.png!small?1658306523963)

客户端连接：

![1658306534_62d7bfe6e5c2cf7bee8a4.png!small?1658306535534](https://image.3001.net/images/20220720/1658306534_62d7bfe6e5c2cf7bee8a4.png!small?1658306535534)

登录上来后先生成个powershell后门

![1658306572_62d7c00ca1182b1348f39.png!small?1658306573263](https://image.3001.net/images/20220720/1658306572_62d7c00ca1182b1348f39.png!small?1658306573263)

首先创建监听器

![1658306607_62d7c02f57b8752166e3c.png!small?1658306608008](https://image.3001.net/images/20220720/1658306607_62d7c02f57b8752166e3c.png!small?1658306608008)

选择刚刚创建好的监听器

![1658306733_62d7c0ad3b70b788c2f89.png!small?1658306733910](https://image.3001.net/images/20220720/1658306733_62d7c0ad3b70b788c2f89.png!small?1658306733910)![1658306803_62d7c0f38e19ec3100ba8.png!small?1658306804147](https://image.3001.net/images/20220720/1658306803_62d7c0f38e19ec3100ba8.png!small?1658306804147)

保存为payload.ps1(服务器)，将其进行base64编码，然后上传到服务器上，作为一个简单的钓鱼下载链接。

![1658306759_62d7c0c73eca7fe2568c4.png!small?1658306760209](https://image.3001.net/images/20220720/1658306759_62d7c0c73eca7fe2568c4.png!small?1658306760209)

ok,成功,正常来说浏览器访问此链接会将它下载下来。(测试的时候虚拟机可以，服务器失败，但都不影响powershell命令行下载)

![1658306830_62d7c10e4f2c6ad2e37fb.png!small?1658306831219](https://image.3001.net/images/20220720/1658306830_62d7c10e4f2c6ad2e37fb.png!small?1658306831219)

下载方式一

![1658306842_62d7c11a61488c282279a.png!small?1658306843059](https://image.3001.net/images/20220720/1658306842_62d7c11a61488c282279a.png!small?1658306843059)

下载方式二

![1658306859_62d7c12b44a1afb01c604.png!small?1658306859847](https://image.3001.net/images/20220720/1658306859_62d7c12b44a1afb01c604.png!small?1658306859847)

但方式二会被某绒报警

![1658306868_62d7c134ecea8d8bb085d.png!small?1658306869582](https://image.3001.net/images/20220720/1658306868_62d7c134ecea8d8bb085d.png!small?1658306869582)

然后进到执行下载的payload.ps1，成功上线CS，接下来，为所欲为？

屏幕截图，权限提升，内网渗透...

##  **相关**

    
    
    #查看powershell版本$PSVersionTable#管理员开启PS1文件执行权限  set-executionpolicy remotesigned；

