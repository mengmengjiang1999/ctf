在学习web安全时，通常为主流漏洞和非主流漏洞，但是大部分遇到的都是主流漏洞；非主流也不可忽略。

web中间件漏洞是非常常见的漏洞，主要原因还是其用户配置不当造成的，修改相关的配置就可以恢复！

第一，我们这次采用的Vulhub的靶场，当然也可以自己搭建靶场，个人觉得这样更方便一些。

>
>     安装完成之后，就可以打开靶场了
>         docker-compose up -d
>         目录：root@aa:/vulhub-master/nginx/nginx_parsing_vulnerability#
>  

![image.png](https://image.3001.net/images/20210530/1622361491_60b3459336b26514fe532.png!small)

第二，访问靶场 192.168.80.136；由于本机默认端口是8080，就可以直接打开了。

![image.png](https://image.3001.net/images/20210530/1622361656_60b346380e28c19b79bec.png!small)

由于是解析漏洞（会把jpg类型的文件当成PHP文件解析），直接在图片里隐写上php后门代码就可以了。

> #后门连接代码
>
> <php phpinfo(); ?php> #获取php配置信息

第三，开始上传

![image.png](https://image.3001.net/images/20210530/1622361936_60b347502aa155b998c3d.png!small)

> 上传成功后，就访问
> http://192.168.80.136/uploadfiles/bc808b0f8bfb5a2bdda6bdf1c8a9e5e7.jpg/mm.php

![image.png](https://image.3001.net/images/20210530/1622362048_60b347c0839eecaf12c7e.png!small)

接下来，看看能不能连接上后门；  
用御剑打开

![image.png](https://image.3001.net/images/20210530/1622362100_60b347f460aad52cf80a2.png!small)

![image.png](https://image.3001.net/images/20210530/1622362133_60b34815e3b80dd81faf4.png!small)

最后还是失败了，我不知道感觉每次连接都失败了，有知道的大佬可以解释一下。

当然，这是nginx中间件的解析漏洞，在其他web中间件也存在解析漏洞，比如Apache 6.x 也存在相应的BUG。大家也可以去尝试一下。

大家一起学习，一起交流呀！

