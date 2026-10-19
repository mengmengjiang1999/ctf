**宏观结构**  
EXE调用dll文件，dll文件读dat文件并解密dat文件得到第二个dll文件

 **微观分析**

1，样本为32位exe可执行文件  
![image.png](https://image.3001.net/images/20220817/1660725539_62fca9237d9108c11cd34.png!small)  
2，IDA分析初步分析  
通过Getprocaddress调用dll文件的run@4函数  
![image.png](https://image.3001.net/images/20220817/1660725571_62fca943646429971f499.png!small)  
3，分析dll文件  
export窗口找run函数，反汇编一下，连续调用了sub_10001BC0，sub_10001BF0，1BC0没什么东西，看1BF0  
![image.png](https://image.3001.net/images/20220817/1660725948_62fcaabc5912932335a94.png!small)  
通过getproadress和getmodulefilenamA获取了文件名称和路径，获取后有加解密操作  
![image.png](https://image.3001.net/images/20220817/1660727780_62fcb1e43b05f41f4b184.png!small)  
看1000，应该是自写的readfile函数，  
![image.png](https://image.3001.net/images/20220817/1660726220_62fcabcca66a2ee10c32d.png!small)  
动态看一下获取的文件，10DC处下个断点  
![image.png](https://image.3001.net/images/20220817/1660726839_62fcae379aba90591f649.png!small)  
样本文件夹下的一个dat文件，结合上面的加解密操作，应该是通过dll文件获取dat文件路径和名称，然后解密dat文件  
![image.png](https://image.3001.net/images/20220817/1660727591_62fcb1275974872cabc1c.png!small)  
4，获取dat文件解密之后的内容  
从上面看，解密之后返回给15D0运行，在解密之后，运行之前下断点，  
![image.png](https://image.3001.net/images/20220817/1660728025_62fcb2d9e376550ff077e.png!small)  
找到2408，下断点一步步执行，  
![image.png](https://image.3001.net/images/20220817/1660728118_62fcb336a48d84ef1c3ef.png!small)  
将数据窗口的46D600一直到496000的二进制复制到010重命名1  
5，分析解密之后的文件  
dll文件  
![image.png](https://image.3001.net/images/20220817/1660728248_62fcb3b88d3ec05d9cd65.png!small)  
ida分析  
跳到10001D11，然后触发其函数10001C80,1C81里面还有10001B60，F5发现很多函数，一个个分析。

大概的意思：case1：修改环境变量利用注册表进行了自启动操作，权限维持，并在%userprofile%路径下创建文件

Case2：创建互斥体，判断文件是否存在，存在则退出，不存在则创建，如果输入了-net则运行其网络相关的东西，如果没有输入，则进行提权

Case3：使用shell打开会话，并且会话是通过winodows窗口进行传输，错误代码不等183则继续运行代码  
![image.png](https://image.3001.net/images/20220818/1660806316_62fde4ace5346eed6ba6d.png!small)  
在1000909E可以看到操作的注册表目录为  
![image.png](https://image.3001.net/images/20220818/1660806403_62fde503be6327f7ed5e9.png!small)  
![image.png](https://image.3001.net/images/20220818/1660806455_62fde537707c5c05ed19c.png!small)

