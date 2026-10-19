纸上得来终觉浅，为了更好的将知识掌握，从网上下载了这个病毒的apk样本来分析学习。

 **正文**

这里先将apk样本放到在线的文件分析平台看一下，这里选择的是国内的平台，书上推荐的是Mobile
SANDBOX，这个平台有一个优势，就是会保存运行时的流量包，可以自己再对流量包进行手动分析。在等待平台跑出结果的时候，先自己手动分析一下。

![image.png](https://image.3001.net/images/20220508/1652023865_6277e239ec581097aa8a8.png!small)

这里先用Android Killer看一下java层的代码。

![img](https://image.3001.net/images/20220508/1652023212_6277dfacbc6b5c31c35be.jpg!small)

可以看到这里一共需要五个权限。

android.permission.INTERNET

android.permission.ACCESS_NETWORK_STATE

android.permission.ACCESS_WIFI_STATE

android.permission.READ_PHONE_STATE

android.permission.ACCESS_COARSE_LOCATION

总共申请获取了网络、WIFI、读取、定位这几个权限。

![image-20220508230627812](https://image.3001.net/images/20220508/1652023215_6277dfaf978805ec077a1.png!small)

点击查看java层的源码，可以看到这里先判断手机有无进行root操作。

![image-20220508230648298](https://image.3001.net/images/20220508/1652023216_6277dfb0c0b8299843f71.png!small)

然后启动了一个线程，这里面涉及的网站已经访问不了了，但是根据以前的资料，这个连接网站主要是为了下派广告。

![image-20220508230710809](https://image.3001.net/images/20220508/1652023217_6277dfb129c7120d59af7.png!small)

接着初始化了一个f类

![image-20220508230726084](https://image.3001.net/images/20220508/1652023217_6277dfb1f2b6e418ea16c.png!small)

然后之后通过读取配置文件的did,和外连网站注册userid.(这里注册的userid,因为网站已经无法访问，所以只能根据之前的资料).

![image-20220508230746622](https://image.3001.net/images/20220508/1652023218_6277dfb23a906e1a1fb8f.png!small)

![image-20220508230755822](https://image.3001.net/images/20220508/1652023218_6277dfb2e75d41d9619cd.png!small)

接着再启动一个全局定时器，用于启动ReceiverAlarm。

![image-20220508230825266](https://image.3001.net/images/20220508/1652023219_6277dfb34b238b68c35f1.png!small)

接着会获取系统的通知服务。

![image-20220508230845508](https://image.3001.net/images/20220508/1652023220_6277dfb453080fc613bda.png!small)

接着的操作就是跟获取广告有关了。

![image-20220508230901563](https://image.3001.net/images/20220508/1652023221_6277dfb5120d4fa76772b.png!small)

接着再回到MainActivity,可以看到在之后又启动了一个服务。

![image-20220508230913934](https://image.3001.net/images/20220508/1652023222_6277dfb65bd5ea7bd9ccb.png!small)

这里调用了一个原生的动态连接库。这里我们用apktool对apk进行操作，获得lib目录下的so文件进行native层的分析。

![image-20220508230933925](https://image.3001.net/images/20220508/1652023222_6277dfb69985aa1ad2515.png!small)

将so文件放入ida中，f5一下。(汇编水平还不行，所以这里用查看伪代码的方式进行分析).

![image-20220508230955460](https://image.3001.net/images/20220508/1652023222_6277dfb6d78f687149cfc.png!small)

根据java层可以得知，这里会传入三个参数，设备id，程序包名，meta_data.

![image-20220508231016749](https://image.3001.net/images/20220508/1652023223_6277dfb743572900ae53d.png!small)

然后之后可以看到这里进行了一个写文件的操作，判断这里就是病毒主体生成的地方。文件名是根据时间随机生成的。然后对主体加上了一个权限操作。

![image-20220508231035250](https://image.3001.net/images/20220508/1652023224_6277dfb81d8857ad05670.png!small)

接下来进行了root的一个判断，然后通过管道调用su.

![image-20220508231049380](https://image.3001.net/images/20220508/1652023224_6277dfb89bb468d95722c.png!small)

接下来，就是执行病毒主体的操作，再执行完后，还会对文件进行一个删除。

![image-20220508231107267](https://image.3001.net/images/20220508/1652023224_6277dfb8dd094132a1077.png!small)

这里把病毒主体bin文件放入到ida中查看。

![image-20220508231126125](https://image.3001.net/images/20220508/1652023225_6277dfb9761f6fc0c135e.png!small)

这里对系统感染的部分进行分析。

这里可以看到是通过一个中间临时文件，对系统文件进行修改。

![image-20220508231145149](https://image.3001.net/images/20220508/1652023226_6277dfbaa054bb6fbbb20.png!small)

![image-20220508231200573](https://image.3001.net/images/20220508/1652023227_6277dfbb5304467db52cc.png!small)

最后再回去看一下在线平台的分析结果。

![image-20220508231218357](https://image.3001.net/images/20220508/1652023228_6277dfbc4564d49871439.png!small)

![image-20220508231226224](https://image.3001.net/images/20220508/1652023230_6277dfbe65a401cc81657.png!small)

![image-20220508231235134](https://image.3001.net/images/20220508/1652023230_6277dfbebcb6f5c402e05.png!small)

这里可以看到的运行截图和之前的分析差不多。若有不足之处请大家多多指出希望可以和大家一起学习交流。

