![](https://image.3001.net/images/20230629/1688032977_649d56d16d2cbae0c0c32.png!small)  

## 关于ShadowSpray

ShadowSpray是一款功能强大的[ _Shadow_ __
_Credential_](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab)域喷射工具，该工具能够对整个目标域执行Shadow
Credential喷射，并尝试通过目标域中的其他对象来寻找和利用被遗忘的GenericWrite/GenericAll DACL。

## 工具运行机制

> 1、该工具首先会使用提供的凭证登录到目标域中（或使用当前会话）；
>
> 2、接下来，工具会检查目标域功能，如果停止的话，Shadow Credential攻击将无法成功；
>
> 3、从LDAP收集域中所有对象（用户和计算机）的列表；
>
> 4、对于列表中的每个对象，工具将执行以下操作：尝试将KeyCredential添加到对象的“msDS-> KeyCredentialLink”属性中。如果以上操作成功，将通过PKINIT并使用添加的KeyCredential来请求TGT；如果以上操作成功，将执行UnPACTheHash攻击以获取用户/计算机NT哈希；如果指定了
> --RestoreShadowCred：删除添加的KeyCredential（自行清理…）；如果指定了--> Recursive，则使用我们成功拥有的每个用户/计算机帐户执行相同的过程；

ShadowSpray支持CTRL+C，因此如果在任何时候您希望停止执行，只需按下CTRL+C即可，ShadowSpray将在退出之前显示到目前为止恢复的NT哈希。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Dec0ne/ShadowSpray.git

## 工具使用

    
    
    __             __   __        __   __   __
    
    /__` |__|  /\  |  \ /  \ |  | /__` |__) |__)  /\  \ /
    
    .__/ |  | /~~\ |__/ \__/ |/\| .__/ |    |  \ /~~\  |
    
     
    
     
    
    Usage: ShadowSpray.exe [-d FQDN] [-dc FQDN] [-u USERNAME] [-p PASSWORD] [-r] [-re] [-cp CERT_PASSWORD] [-ssl]
    
     
    
        -r   (--RestoreShadowCred)    攻击完成之后恢复"msDS-KeyCredentialLink"（可选）
    
        -re  (--Recursive)             递归执行ShadowSpray攻击 （可选）
    
        -cp  (--CertificatePassword)   证书密码，默认为随机密码
    
     
    
     
    
    General Options:
    
        -u  (--Username)         初始LDAP 认证用户名（可选）
    
        -p  (--Password)         初始LDAP 认证密码（可选）
    
        -d  (--Domain)              目标域的FQDN（可选）
    
        -dc (--DomainController)      目标域控制器的FQDN（可选）
    
        -ssl                          通过SSL使用LDAP （可选）
    
        -y  (--AutoY)            开始ShadowSpray 攻击时无需询问确认（可选）

## 工具使用演示

 **演示视频** ：【[ _点我观看_](https://user-images.githubusercontent.com/54464773/194827503-b1eead1a-e09a-41ca-9d9b-0a7a6f0ad6a0.mp4)】

## 项目地址

 **ShadowSpray** ：【[ _GitHub传送门_](https://github.com/Dec0ne/ShadowSpray)】

## 参考资料

> [ _https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-> mapping-for-takeover-8ee1a53566ab_](https://posts.specterops.io/shadow-> credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab)
>
> [
> _https://github.com/BloodHoundAD/BloodHound_](https://github.com/BloodHoundAD/BloodHound)
>
> [
> _https://github.com/Dec0ne/KrbRelayUp_](https://github.com/Dec0ne/KrbRelayUp)
>
> [ _https://medium.com/falconforce/falconfriday-detecting-unpacing-and-> shadowed-> credentials-0xff1e-2246934247ce_](https://medium.com/falconforce/falconfriday-> detecting-unpacing-and-shadowed-credentials-0xff1e-2246934247ce)

