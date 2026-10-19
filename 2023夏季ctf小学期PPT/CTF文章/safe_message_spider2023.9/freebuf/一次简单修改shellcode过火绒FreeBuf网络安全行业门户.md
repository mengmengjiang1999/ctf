### 前言

最近在学习病毒分析，在玉师傅的指导下完成了一次小实验，遂发出来纪念一下。

### 环境

kali ：192.168.0.108  
win10：192.168.0.103

### 开始

1，首先使用msf生成一段shellcode，并将其编译  
![image.png](https://image.3001.net/images/20220803/1659535217_62ea7f7145c181930f825.png!small)  
编译，此时已被火绒直接杀掉，关闭火绒重新编译  
![image.png](https://image.3001.net/images/20220803/1659535688_62ea8148ed7eb6d0c30be.png!small)

2，编译完成后将exe拖入OD得到其汇编代码  
进入call eax内部  
![image.png](https://image.3001.net/images/20220803/1659535944_62ea8248ae0855af4062e.png!small)  
从灰色背景这一句开始都是shellcode的汇编代码  
![image.png](https://image.3001.net/images/20220803/1659536203_62ea834b8b99a4812f9cf.png!small)  
我们只选比较重要的一段  
![image.png](https://image.3001.net/images/20220803/1659536678_62ea8526b621eb5e5c8e7.png!small)

3，分析火绒的抓取特征  
经过分段测试火绒抓取的是这一段  
![image.png](https://image.3001.net/images/20220803/1659537058_62ea86a2a726cf4d3c27c.png!small)  
4，达到效果  
既然已经知道抓取特征，那么我们只要在其特征之中添加混淆指令即可，比如 push,pop,mov等  
测试  
![image.png](https://image.3001.net/images/20220803/1659539140_62ea8ec4ec47ea7ec7c3e.png!small)  
![image.png](https://image.3001.net/images/20220803/1659539450_62ea8ffa14cb2b7d00c31.png!small)

#####
[测试视频在这](https://www.bilibili.com/video/BV1BY4y1w7vA?spm_id_from=333.999.0.0&vd_source=455495f8c85b06a1f3695d3bbece70a3)

