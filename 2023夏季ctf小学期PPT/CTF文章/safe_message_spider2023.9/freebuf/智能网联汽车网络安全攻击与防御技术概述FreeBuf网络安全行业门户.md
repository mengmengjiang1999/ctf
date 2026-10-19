**作者 |** 王博文 上海控安可信软件创新研究院研究员

 **来源 |** 鉴源实验室

##  **01** **引言**

在汽车电动化、网联化、智能化和共享化等新四化的发展趋势下，智能网联汽车（Intelligent Connected
Vehicles，ICVs）已经是新时代的必然产物。在智能网联汽车的场景下，衍生出了如智能无线传感器技术、车联网技术、无人驾驶汽车技术和智能交通系统等一系列创新技术。然而，消费者在体验智能技术的同时，却承担着极大的安全风险。智能网联汽车消除了黑客攻击车辆的地域和距离限制，给黑客远程批量攻击目标车辆提供了可能，使得车辆面临的信息安全风险显著增加。

 **该系列文章主要对智能网联汽车的网络安全攻击及其防御技术进行全面的概述。**
一方面总结以往研究的发现和结论，并从学术研究和产业发展的角度，指出当前研究所面临的挑战和发展趋势。我们希望我们的工作可以让汽车设计和开发相关的研究人员和工程师了解ICVs的安全问题以及最先进的防御和缓解技术。另一方面，我们也希望可以激励其他研究人员解决ICVs发展面临的网络安全挑战。

  

##  **02** **智能网联汽车面临的威胁**

智能网联汽车上部署了多种智能传感器组件，如激光雷达、毫米波雷达、超声波雷达、摄像头、全球导航卫星系统传感器（Global Navigation
Satellite
System，GNSS）等[1]，组件之间又是通过各种有线或者无线的通信方式进行连接，如车载以太网、CAN总线、蜂窝网络（4G/5G）、蓝牙（Bluetooth）、Wi-Fi和WAVE（Wireless Access in the Vehicular
Environment）等。传感器组件使得ICVs能够感知周围环境的障碍物，利用传感器的数据，SLAM（Simultaneous localization
and
mapping）可以定位周围环境以及车辆的位置，进一步辅助自动驾驶做出决策。虽然传感器组件和连接机制在安全性、成本和燃油效率方面有了显著改善，但它们也为网络攻击创造了更多机会。

 **2.1 攻击案例**

根据Upstream
2022年全球汽车网络安全报告[2]，如图1所示，2010年至2021年间，攻击者对智能网联汽车最常见的攻击载体有11种，且大多为黑帽攻击，仅2021年，黑帽攻击所占比例高达56.9%。白帽黑客操纵汽车系统为了发现漏洞或进行教育研究，改善车辆的网络安全，而黑帽黑客往往与犯罪活动一致。

早在2004年，德国的安全研究员Marko
Wolf就发现了车载网络存在被恶意攻击的隐患[3]，并在随后的几年进行了深入的调研[4-6]。不过相关安全问题都是通过直接以物理形式接触相应的网络结构为前提。

2010年，美国南卡罗来纳大学的研究员发现了汽车的胎压监测系统存在安全和隐私相关的隐患，车上相关的无线通信协议存在被入侵的风险[7]。

2013年Charlie Miller和Chris
Valasek在通过车载诊断接口实现了对丰田和福特汽车的攻击和控制[8]。通过诊断接口可以直接操纵汽车的发动机、制动器、灯光、车门等，并且通过诊断功能的ECU刷写功能，可以篡改ECU内部的程序信息。2015年他们两人又使用Wi-Fi开放端口侵入Jeep
Cherokee的车载网络系统[9]，更新了车内ECU的固件，并且成功地控制了一系列汽车功能（禁用刹车和停止发动机），该攻击案例引发了140万辆汽车的召回，而该事件是首个信息安全所引发的汽车召回事件。

科恩实验室在2018年针对宝马多款车型的电子控制单元进行安全分析，发现了多个通用安全漏洞[10]。这些漏洞影响组件涉及车载信息娱乐系统、车载通讯模块和车载网关。攻击者可以利用这些漏洞，通过物理接触攻击或远程攻击，获得车内CAN总线控制权，从而实现汽车的控制。

2021年6月，卡内基梅隆大学CyLab研究人员发现了一类新的网络安全漏洞[11]，利用汽车MCU时钟外设的门控特性，开发了用于远程关闭的CANnon攻击，并且成功在不到2ms的时间内对一辆福特福克斯和一辆丰田普锐斯实现了关机。

![](https://image.3001.net/images/20221118/1668743067_6376ff9b49677d0776dbf.png!small)

图1 2010年-2021年最常见的ICVs攻击类型[2]

 **2.2 攻击的分类**

 **2.2.1 攻击目标**

正如前面所说，ICVs部署了多种智能传感器组件，组件之间又通过各种通信方式进行连接。它们一起工作，促进ICVs的运转。破坏或篡改任何这些组件都可能破坏ICVs的稳定，攻击者可以把智能传感器组件以及通信方式作为攻击目标，进而实现窃取车辆或者个人信息，造成财产损失和人身伤害。下面描述现有的研究中已被网络攻击者锁定的ICVs组件，有些攻击模型已经被证明是真实的威胁，而有些只是在理论上进行了讨论。

 **（1）车载诊断接口（On-board Diagnostic Port，OBD）**
：OBD端口可以用来收集有关汽车排放、里程、速度和汽车零部件数据的信息。OBD标准有OBD-I和OBD-II两种。OBD-I于1987年推出，但存在许多缺陷，因此被1996年推出的OBD-II所取代。OBD端口可以提供车内CAN网络和以太网的实时数据，许多OEM制造商也使用OBD端口来执行OTA固件更新。

 **（2）汽车电子控制单元（Electronic Control Unit，ECU）**
：汽车ECU是嵌入式电子系统，用于控制车辆中的其他子系统。所有现代车辆都使用ECU来控制车辆的功能，一些重要的ECU可以是刹车控制模块，发动机控制模块，轮胎压力监测系统等。制动控制模块从轮速传感器和制动系统收集数据，并处理数据以确定是否实时释放制动压力。发动机控制模块控制燃料、空气和火花，并从其他传感器收集数据，以确保所有组件都在正常的工作范围内。轮胎压力监测系统从轮胎内的传感器收集数据，并确定轮胎压力是否处于理想水平。

 **（3）控制区域网络（Controller Area Network，CAN）**
：ECU通常通过CAN总线进行连接。CAN为总线型网络，具有广播特性，在ICVs中，网络数据包可以被传输到CAN网络中的所有节点，并且数据包不包含认证字段。因此，一个被入侵的节点可以收集所有通过网络传输的数据，并将恶意数据广播给其他节点，使整个CAN系统容易受到网络攻击。

 **（4）激光雷达（Light Detection and Ranging，LiDAR）**
：激光雷达传感器发送光波探测周围环境，并根据反射信号进行测量其到周围物体的距离。在ICVs中，激光雷达通常用于障碍物检测，以安全通过环境，通常由反旋转激光束实现。激光雷达的数据可被EUC的软件用于确定环境中是否有障碍物，也可用于自动紧急制动系统。

 **（5）毫米波雷达（Radio Detection and Ranging，Radar）**
：毫米波雷达属于在无线电毫米波领域发出电磁波的传感器，通过感应反射信号来探测物体并测量其距离和速度。在ICVs中，毫米波雷达在许多应用中都很有用。例如，近程雷达可以实现盲点监测、车道保持辅助系统和停车辅助系统等。

 **（6）全球定位系统（Global Positioning System，GPS）**
：GPS是一种基于卫星的导航系统，当GPS接收器发现来自三个或更多卫星的信号时，就可以计算出接收器的位置。由于找到两个地点之间的路线是自动驾驶的必要条件，GPS信号对自动驾驶汽车至关重要。但是由于GPS信号不包含任何可以直接验证信号来源的数据，GPS接收器很容易受到干扰和欺骗攻击。

 **（7）摄像头（Cameras/Image Sensors）**
：自动驾驶和半自动驾驶汽车依赖于放置在许多位置的摄像头来获得360度的视野。相机为重要的自动驾驶任务提供信息，比如交通标志识别和车道检测等。摄像机也可以用来取代激光雷达，以更低的成本完成物体探测和测量距离的任务，但它们在下雨、雾或雪等特定情况下的性能较差[12]。因此摄像头与激光雷达和毫米波雷达相配合，可以为自动驾驶提供更丰富多样的数据。

 **（8）V2X通信（Vehicle to Everything，V2X）** ：V2X通信可分为车对车网络（Vehicle to
Vehicle，V2V）和车对基础设施网络（Vehicle to
Infrastructure）。V2V通信有助于在附近的车辆之间交换数据，并可以快速地为ICVs已经收集到的关于周围环境的数据提供额外的信息。V2I通信有助于ICVs和道路基础设施之间的数据交换，这些基础设施提供了关于交通系统的数据。

 **2.2.2 攻击模型分类**

 **根据访问需求可以将攻击模型分为远程执行（远程访问攻击）或物理访问ICVs组件执行（物理访问攻击）。**

 **（1）远程访问攻击**
：攻击者不需要对ICVs上的部件进行物理修改，也不需要在ICVs上附加设备。这种类型的攻击比物理访问攻击更常见，而且由于ICVs之间会传输大量信息，这种攻击的数量正在增加。ICVs上任何与周围环境通信和交互的组件都容易被远程利用。远程访问攻击的三种常见模式是发送伪造数据、阻塞信号和收集机密数据。发送伪造数据的目的是欺骗ICVs系统，以获得对系统行为的显著控制，比如LiDAR欺骗、Radar欺骗、GPS欺骗和对抗性图像攻击等。阻塞信号旨在阻止ICVs接收确保其正常工作的信息，比如激光雷达干扰、毫米波雷达干扰、GPS干扰、摄像机致盲和拒绝服务攻击等。收集机密数据则为进一步的攻击服务。

 **（2）物理访问攻击**
：攻击者需要物理修改ICVs上的组件或将仪器附加到ICVs上，比如故障数据注入。物理访问攻击更难实施，因为攻击者在篡改ICVs时可能被检测到。但是CAN和ECU既可以作为远程访问的目标，也可以作为物理访问的目标。

 **从攻击者的动机角度又可以将攻击模型分为三种，中断ICVs的操作，控制ICVs和窃取信息。**

 **（1）中断操作** ：攻击者的目标是破坏对自动驾驶很重要的ICVs组件，从而使自动驾驶功能在ICVs上失效。这些攻击类似于网络上的拒绝服务攻击。

 **（2）获取ICVs控制权限** ：攻击者获得对ICVs的充分控制，以便他们可以改变车辆的移动，如改变车辆的路线，强制紧急刹车，和改变车辆速度。

 **（3）窃取信息** ：攻击者的目标是从ICVs收集重要的或机密的信息，收集的信息可能用于进一步的攻击。

 **如表1所示，将ICVs的攻击模型进行分类，按照攻击目标和攻击行为方式分为15种。**

表1 ICVs攻击模型的分类

![](https://image.3001.net/images/20221118/1668743091_6376ffb3f0cffad13dfda.png!small)![](https://image.3001.net/images/20221118/1668743102_6376ffbedaf3a38a1dd58.png!small)

后面几期将对智能网联汽车的攻击场景以及对应的应对措施做详细的分析与介绍。

  

参考文献

[1] WYGLINSKI A M, HUANG X, PADIR T, et al. Security of autonomous systems
employing embedded computing and sensors [J]. IEEE micro, 2013, 33(1): 80-6.

[2] UPSTREAM. Global Automotive Cybersecurity Report [R], 2022.

[3] WOLF M, WEIMERSKIRCH A, PAAR C. Security in automotive bus systems;
proceedings of the Workshop on Embedded Security in Cars, F, 2004 [C]. Bochum.

[4] WOLF M, WEIMERSKIRCH A, PAAR C. Secure in-vehicle communication [M].
Embedded Security in Cars. Springer. 2006: 95-109.

[5] WOLF M, WEIMERSKIRCH A, WOLLINGER T. State of the art: Embedding security
in vehicles [J]. EURASIP Journal on Embedded Systems, 2007, 2007: 1-16.

[6] WOLF M, DALY P. Security engineering for vehicular IT systems [M].
Springer, 2009.

[7] ROUF I, MILLER R, MUSTAFA H, et al. Security and Privacy Vulnerabilities
of {In-Car} Wireless Networks: A Tire Pressure Monitoring System Case Study;
proceedings of the 19th USENIX Security Symposium (USENIX Security 10), F,
2010 [C].

[8] MILLER C, VALASEK C. Adventures in automotive networks and control units
[J]. Def Con, 2013, 21(260-264): 15-31.

[9] MILLER C, VALASEK C. Remote exploitation of an unaltered passenger vehicle
[J]. Black Hat USA, 2015, 2015(S 91).

[10] LAB K S. Experimental Security Assessment of BMW Cars: A Summary Report
[R], 2018.

[11] KULANDAIVEL S, JAIN S, GUAJARDO J, et al. Cannon: Reliable and stealthy
remote shutdown attacks via unaltered automotive microcontrollers; proceedings
of the 2021 IEEE Symposium on Security and Privacy (SP), F, 2021 [C]. IEEE.

[12] WANG Y, CHAO W-L, GARG D, et al. Pseudo-lidar from visual depth
estimation: Bridging the gap in 3d object detection for autonomous driving;
proceedings of the Proceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, F, 2019 [C].

