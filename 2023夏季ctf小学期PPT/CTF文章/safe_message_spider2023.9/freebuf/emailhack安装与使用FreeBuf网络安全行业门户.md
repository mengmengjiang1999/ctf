## 0X01.工具介绍

    
    
    利用 Python 伪造电子邮件发件人以及制造电子邮件轰炸。

## 0X02.下载与安装

    
    
    https://github.com/Macr0phag3/email_hack

![](https://image.3001.net/images/20221223/1671782688_63a561209c333334423d2.png!small)

个人推荐在linux上进行测试，展示效果会较好：

    
    
    安装环境：Linux，Unix
    ​
    Python version： 2.x ，3.x 
    ​
    安装依赖：pip3 install Dnspython

## 0X03.参数介绍

    
    
    -h, --help            输出帮助信息  
    -faddr FROM_ADDRESS, --from_address FROM_ADDRESS          
    伪造的来源邮件地址 ​     
    -taddr TO_ADDRESS, --to_address TO_ADDRESS               
    接收方的邮件地址 ​     
    -s SUBJECT, --subject SUBJECT                        
    邮件主题 ​    
    -b BODY, --body BODY                                       
    邮件正文 ​     
    -tnum THREADS_NUM, --threads_num THREADS_NUM       
    多线程的线程数，默认为 1 ​   
    -v VERBOSE, --verbose VERBOSE                       
    输出信息的详细程度，默认由代码自动选择，可选为 0, 1, 2, 3 ​    
    -c CRAZY_MODE, --crazy_mode CRAZY_MODE                           
    长连接模式，谨慎使用，默认为False   
    

## 0X04.功能介绍

### 1\. 正常模拟邮件发送

    
    
    python3 email_hacker.py -faddr [hr@xx.com](mailto:hr@xx.com)-taddr 1771656848@qq.com -s "[打码]世界 2019 校园招聘" -b "同学你好\n感谢你对[打码]世界校园招聘的关注，面试时间暂定为 9月20日 下午两点。如有疑问欢迎邮件交流~\n有的人27岁买宝马，有的人27岁打游戏。有的人30岁存款80万，有的人30岁工作都找不到。太多人挑肥拣瘦，嫌工作辛苦，嫌打工没面子，嫌销售卖货丢人，你没钱，没能力，没事业啥也没有，才最最丢人。你想加油、你想更好，没人会阻挡你前进的道路，其实通往成功的路上最大的阻碍就是自己的无知和懒惰.....！"

![c27ac89f48215490d6c15c69e87c3712.png](https://image.3001.net/images/20221223/1671782690_63a5612231c0d47a7ece0.png!small)

![95e5e992bd1fc3dfddf9ad1a1a25ae2f.png](https://image.3001.net/images/20221223/1671782691_63a561235d3652266d0c4.png!small)

### 2\. 添加参数进行运行

    
    
    python3 email_hacker.py -faddr [hr@xx.com](mailto:hr@xx.com)-taddr 3172315008@qq.com -v1 -tnum 2 -c -s "[打码]世界 2023 校园招聘" -b "同学你好\n感谢你对[打码]世界校园招聘的关注，面试时间暂定为 11月20日 下午两点。如有疑问欢迎邮件交流~\n在茫茫宇宙中，在浩瀚银河里，有一个可以任你挥洒的世界，大家都抱着纯粹初心背负梦想前行，在这里，激情无限，跟志同道合的伙伴热血拼搏。在这里，秉持热爱，把梦想变成现实。在这里，精益求精，定义下一代未知的惊喜！"

![e527c60ce3e91a4d5d1e147e56f92784.png](https://image.3001.net/images/20221223/1671782692_63a5612438613abe2ab73.png!small)

![433a6f73d05d7e48f64760b53afba8be.png](https://image.3001.net/images/20221223/1671782693_63a561255eb3165b55e98.png!small)

可以起到轰炸的一个效果。

## 0X05.温馨提示

    
    
    声明本文章仅供安全研究与学习之用，若将工具做其他用途，由使用者承担全部法律及连带责任，作者不承担任何法律及连带责任。

