## 一、前言

 **这就是个新的轮子，技术上没有大的创新，只是更好用一些。SSH双因素认证的开源方案有挺多的，但是实践应用中发现有三个问题，让推广的情况不是很好。**

以google otp为例：

1、需要安装APP

2、需要修改客户端ssh的登陆方式

3、无法集中管理

第三点先不谈，因为跟用户没啥关系。前面两点对于运维人员还好说，但是对于其他的人来说就不是那么友好，特别是第二个步骤引起的问题就比较多，比如不同软件不同的配置方式等。

所以优化的思路就是尽量透明化，越方便越好。

JXOTP计划有两个版本，一个是单机版本，一个是企业版本，针对的是不同的需求，目前开源的是单机版本，企业版本还在内测中，后续会放出。

单机版本比较适合服务器少的情况，区分程度可以简单划为管理的服务器是否多于10台，10台以内，特别是只有几台服务器的情况下，用单机版本是个不错的选择。

写这个JXOTP的背景是，云上的服务器被没完没了的怼，每时每刻都被进行SSH暴力破解，虽说密码本身不弱，但是哪天要是被撞库了也没地方说理去，所以保险起见还是上个双因素认证系统好。

## 二、部署

目前在centos6/7上测试通过，其他系统自测。

安装如下：

1、# git clone <https://github.com/jx-sec/jxotp.git>

2、# cd jxotp

3、# sh install_otp.sh

结果如下：

![clipboard.png](https://image.3001.net/images/20180719/15319897144140.png)

拿出你发财的小手，打开微信小程序，搜索 "运维密码" ，打开后 点击 "添加场景" 扫描二维码即可完成OTP的配置。

最后是在服务器上启用OTP功能：

    
    
    # vi /etc/pam.d/sshd 

在最上一行添加：

    
    
    auth optional pam_python.so auth.py

![clipboard.png](https://image.3001.net/images/20180719/15319897379551.png)

保存文件即可生效，无需重启sshd服务。

安装配置过程到此结束，下面校验效果：

    
    
    # tail -F /var/log/messages

新开个窗口登陆服务器，随便输入个密码，如123456：

![clipboard.png](https://image.3001.net/images/20180719/15319897615450.png)

日志为"sshd: otp auth log: login user is root,login fail,code is 123456,must
054040"。

code is 123456，是取当前输入密码的后六位，即123456。

must is 054040,
054040是当前OTP生成的code，需要对比运维密码中的code与服务器的code是否一致，正常服务器时间没问题的话，是一致的。

当确定服务器和运维密码的code一致后，安装就此结束。

假设密码为abcdfgww，code为951753，那么当登陆的时候，输入的密码为abcdfgww951753。

## 三、代码分析

    
    
    # -*- coding: utf-8 -*-    import syslog
    import pyotp
    
    OTP_SECRET = "YOU OTP SECRET KEY"  
    # 可以手动修改SECRET KEY，必须为16位base32格式字符串
    WHITE_IP = ["YOU BYPASS IP"]
    #设置白名单IP，白名单IP将无需进行动态口令认证，适合有堡垒机的场景，或者固定IP的情况
    GLOBAL_USER_CHECK = False
    #开启所有系统用户双因素认证，默认为否，即只针对特定用户开启双因素认证
    CHECK_USER = ['root']
    #当GLOBAL_USER_CHECK = False时生效，配置需要进行双因素认证的用户，可添加多个用户，默认只对root用户开启双因素认证
    def  otp_auth(code):
            totp = pyotp.TOTP(OTP_SECRET)
            if totp.now() == code:
                    return True
            else:
                    return False
    #进行OTP校验
    def otp_log(msg):
        syslog.openlog(facility=syslog.LOG_AUTH)
        syslog.syslog("otp auth log: "+msg)
        syslog.closelog()
    #记录日志
    def otp_code():
    	totp = pyotp.TOTP(OTP_SECRET)
    	return totp.now()
    #获取当前时间的code
    def pam_sm_authenticate(pamh, flags, argv):
    	for white in WHITE_IP:
    		if pamh.rhost == white:
    			otp_log("white ip login,ip is "+pamh.rhost)
    			return pamh.PAM_SUCCESS
    #判断是否有白名单IP，有的话直接返回验证成功，无需进行双因素认证
            if GLOBAL_USER_CHECK:
    #判断是否开启双因素认证
                    resp = pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_OFF,'Password:'))
    #获取输入的密码
                    code = resp.resp[-6:]
    #取密码后六位
                    if otp_auth(code):
                            pamh.authtok = resp.resp[:-6]
    			otp_log("login user is "+pamh.user+",login success,code is "+resp.resp[-6:])
                    else:
                            pamh.authtok = ""
    			otp_log("login user is "+pamh.user+",login fail,code is "+ resp.resp[-6:]+",must  "+otp_code())
                    return pamh.PAM_SUCCESS
    #判断密码后六位与服务器code是否一致，如果是将密码后六位删除，重写密码参数，如果不是将整个密码参数设置为空
            else:
                    for user in CHECK_USER:
    
                            if pamh.user == user:
                                    resp = pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_OFF,'Password:'))
                                    code = resp.resp[-6:]
                                    if otp_auth(code):
                                            pamh.authtok = resp.resp[:-6]
    					otp_log("login user is "+pamh.user+",login success,code is "+resp.resp[-6:])
                                    else:
                                            pamh.authtok = ""
    					otp_log("login user is "+pamh.user+",login fail,code is "+ resp.resp[-6:]+",must  "+otp_code())
                            else:
    				otp_log("user login otp check bypass,user is  "+ pamh.user)
                                    return pamh.PAM_SUCCESS
    #判断用户是否为设置开启校验的用户，不是直接返回成功，是的话进行检测，流程同上
    
    def pam_sm_setcred(pamh, flags, argv):
    
           return pamh.PAM_SUCCESS
    

## 四、总结

新轮子更好用的地方主要体现在，不需要像传统的方法去改sshd的配置文件开启ChallengeResponseAuthentication选项，也即对于使用的用户来说，部署完后是透明的，无需修改windows下登陆客户端的配置，降低使用的成本，其次支持用户和IP设置，提高了灵活性，但是相对企业版来说，单机版存在不好维护的问题，所以适合少量服务器使用。

 ***本文作者chenjc，转载请注明来自FreeBuf.COM。**

