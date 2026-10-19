进入目标网址得： **it must come from https://www.penson.com**

![1624288745_60d0ade98139b6cff0ddb.png!small](https://image.3001.net/images/20210621/1624288745_60d0ade98139b6cff0ddb.png!small)

 **1\. 用hackbar修改referer**

![1624289411_60d0b0837d13bed2653e8.png!small](https://image.3001.net/images/20210621/1624289411_60d0b0837d13bed2653e8.png!small)

得到 ： **you must use penson browser**

 **2\. 修改User-Agent**

![1624289928_60d0b288cf79e7b1a2ed8.png!small](https://image.3001.net/images/20210621/1624289928_60d0b288cf79e7b1a2ed8.png!small)

得 ： **you must speek chinese!!**

 **3.修改Accept-Language**

![1624290056_60d0b308a645c355d3802.png!small](https://image.3001.net/images/20210621/1624290056_60d0b308a645c355d3802.png!small)

得到： **your ip must localhost ! ! !**

 **4.添加localhost用client-ip （注：这个比较罕见）**

![1624290229_60d0b3b575c1ae643db14.png!small](https://image.3001.net/images/20210621/1624290229_60d0b3b575c1ae643db14.png!small)

得到：

    
    
    you must satisfy this condition $_POST['a'] > 1 && intval($_POST['a']) == 1
    && !is_numeric($_POST['a'])

 **intval()函数分析：**

<https://www.runoob.com/php/php-intval-function.html>

![1624325919_60d13f1fd333ca0d816f4.png!small?1624325919937](https://image.3001.net/images/20210622/1624325919_60d13f1fd333ca0d816f4.png!small?1624325919937)

 **大于1但是经过intval()函数要等于1，** **那就是溢出**

 **is_number()函数分析**

>  **该函数用于检测变量是否为数字或数字字符串。而前面加了！就是a必须是字符串**
>
>  **用结束符的URL编码欺骗is_number()函数**

<http://www.bubuko.com/infodetail-2436631.html>

 **5.改POST值**

![1624326634_60d141ea71abedc0881ad.png!small?1624326635152](https://image.3001.net/images/20210622/1624326634_60d141ea71abedc0881ad.png!small?1624326635152)

 **放一个知识点链接**

> <https://blog.csdn.net/fastergohome/article/details/102514264>

