**近日，来自瑞典和英国大学的学者们提出了一项被称之为SonarSnoop的新技术。据称，通过该技术可以将将智能手机的内置扬声器和麦克风，转化为迷你声纳系统，从而窃取Android设备的手机解锁模式。该技术的主要思路是，使用声波来跟踪用户在手机屏幕上手指的位置。攻击者只需在目标手机上安装一个恶意app，手机扬声器就会发出人耳听不到的频率（18kHz和20kHz之间）。**  

就像潜水艇的声纳一样，恶意app会利用（设备的）麦克风来接收从附近物体反弹的声波，即用户手指的点击/滑动声波。根据设备外壳上扬声器和麦克风的位置，可以构建机器学习算法来读取收集的数据并确定可能的解锁模式。

在上周，来自英国兰开斯特大学（Lancaster University）和瑞典林雪平大学（ Linköping
University）的学者，发表了一篇关于在Android 5.0.1的三星Galaxy S4智能手机上SonarSnoop技术测试的详细研究论文。

 **![sonarsnoop-image.png](https://image.3001.net/images/20180906/1536189899_5b9065cb6eab4.png!small)**

该研究小组表示，SonarSnoop获得的数据将可能的解锁模式数量减少近70％。虽说如此，但SonarSnoop技术并没有像你在好莱坞电影的黑客场景中看到的那样酷炫，迄今我们仍无法做到100％准确的解锁模式输出。当前，SonarSnoop正处于实验的早期阶段。相信随着该项技术的不断推进，准确率也会进一步的提升。

在网络安全研究领域，使用声音进行用户跟踪仍然是一个新概念。
在过去的几年中，学者们已经探索了使用智能手机传感器（如加速度计，陀螺仪和接近传感器）来记录和窃取智能手机的[PIN码](https://www.cs.swarthmore.edu/~aviv/papers/aviv-acsac12-accel.pdf)和[解锁模式](http://media.ntu.edu.sg/NewsReleases/Pages/newsdetail.aspx?news=e57faffc-24ea-4034-9181-f5fea9850690)，但从未利用过声波。

自从它在2008年[蝙蝠侠电影“黑暗骑士”](https://www.youtube.com/watch?v=3h8mm5YZb88&t=323)中出现后，使用类似声纳的系统来跟踪用户及其行为的想法，也逐渐走进了我们的现实。

2017年8月美国华盛顿大学的研究人员，首次尝试并实现了一种称之为CovertBand的技术。该技术可将含有麦克风和扬声器的智能设备转化为一种监控工具（主动声纳系统），隐蔽发射频率为18-20
kHz特定构造的音频信号，并可穿越墙壁、门和窗户监测多个用户的位置和身体活动。

但SonarSnoop研究团队认为，其主要的灵感来源于[FingerIO](https://www.youtube.com/watch?v=PpVUCEZvNjI)。FingerIO是2016年3月发布的一种新概念，当时学者们创建了类似声纳的系统，主要用于改善与智能手表的互动。

使用FingerIO，用户可以用手指在智能手表附近绘制线条和形状，智能手表将使用高频声波来接收手指运动并将其转换为触摸屏交互。可以说，SonarSnoop是FingerIO的邪恶版本，概念相同但目的不同（SonarSnoop主要是窃取触摸屏的交互数据）。

研究人员还指出，尽管他们的实验目前专注于智能手机。但SonarSnoop“也适用于许多其他类型的计算设备和可用麦克风和扬声器的物理环境。”

有关SonarSnoop技术的更多细节，可在“[SonarSnoop: Active Acoustic Side-Channel
Attacks](https://arxiv.org/pdf/1808.10250v1.pdf)”研究论文中找到。

 ***参考来源：[zdnet](https://www.zdnet.com/article/sonarsnoop-attack-can-steal-smartphone-unlock-patterns/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

