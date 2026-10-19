## 安全配置加固——账号口令

### 账号优化

目的是为了梳理系统中的账号以及口令，避免默认账号及弱口令的存在

#### 查看账号方式

在Windows中查看账号的方式有以下几种，这里就来简述一下  
 **第一种：开始- >运行->compmgmt.msc（进入计算机管理)->本地用户和组**  
![image.png](https://image.3001.net/images/20210321/1616297912_6056bfb8ef3f17c70c623.png!small)  
 **第二种：开始- >运行->cmd->net user**  
![image.png](https://image.3001.net/images/20210321/1616297959_6056bfe7cb0cc39191ea5.png!small)

#### 删除无用账号

如这里我是删除“cqy”这个账号  
第一种方法：  
 **通过命令行来执行**  
![image.png](https://image.3001.net/images/20210321/1616299546_6056c61a916562a1c43a7.png!small)  
第二种方法：  
 **通过控制面板删除账号**  
首先打开控制面板->用户账户与家庭安全  
![image.png](https://image.3001.net/images/20210321/1616300605_6056ca3dee27ba01b8d9f.png!small)  
接着点击"添加或删除用户账户"  
可以看到这里有这些账户  
![image.png](https://image.3001.net/images/20210321/1616301007_6056cbcfe7deff6a60c89.png!small)  
随便点击一个，其中左边有个“删除账户”，点击它  
![image.png](https://image.3001.net/images/20210321/1616301047_6056cbf7ac184aa9fd8c8.png!small)  
然后就会有个这样的弹框  
![image.png](https://image.3001.net/images/20210321/1616301072_6056cc10300ef26de6c5f.png!small)  
最后就删除了  
![image.png](https://image.3001.net/images/20210321/1616301120_6056cc407a3c4e1d6755e.png!small)

#### 锁定无用账号

如这里我是锁定“Guest”账号  
第一种方法：  
 **通过命令行来执行**  
![image.png](https://image.3001.net/images/20210321/1616299875_6056c76381b427050d639.png!small)  
第二种方法：  
 **通过控制面板禁用Guest账号**  
首先打开控制面板->用户账户与家庭安全  
![image.png](https://image.3001.net/images/20210321/1616300605_6056ca3dee27ba01b8d9f.png!small)  
接着点击"添加或删除用户账户"  
可以看到这里有个Guest账户  
![image.png](https://image.3001.net/images/20210321/1616300674_6056ca821a10087e68bc6.png!small)  
点击它可以看到左边有个“关闭来宾账户”  
![image.png](https://image.3001.net/images/20210321/1616300780_6056caec75af15c86ffc3.png!small)  
点击之，然后就可以看到被禁用了  
![image.png](https://image.3001.net/images/20210321/1616300809_6056cb0989873eeed6162.png!small)

### 口令策略

增强密码复杂度，防止用户长期使用同一个账号，以及账号锁定策略等，降低系统账号被暴力破解的可能性

#### 配置方式

开始运行->运行->secpol.msc（本地安全策略）->安全设置  
![image.png](https://image.3001.net/images/20210321/1616300289_6056c9018b4c66b7d1856.png!small)

##### 账户策略->密码策略（建议加固值）

![image.png](https://image.3001.net/images/20210321/1616302202_6056d07a07714d681e74e.png!small)  
其中的策略：  
密码必须符合复杂性要求：即密码必须是同时包含数字、字母大小写和特殊符号的组合。  
密码最常使用期限：防止用户长期不更换密码。  
设置密码最短使用期限和强制密码历史：防止更换密码时再次更换回原密码。  
用可还原的加密来存储密码：密码必须是加密存储且加密算法不可逆。  
所以下图算相对安全的，其中强制要求系统账号必须符合强口令要求，且隔6个月内需更换一次密码，每次更换的密码不允许和历史记录的5个相同，设置密码最短使用期限为2个月  
![image.png](https://image.3001.net/images/20210321/1616302014_6056cfbeb758167915308.png!small)

##### 账户策略->账户锁定策略（建议加固值）

![image.png](https://image.3001.net/images/20210321/1616302346_6056d10a0c405a17e4e71.png!small)  
其中：  
账户锁定阈值为5次：即5次失效登陆后，账户会锁定一段时间。

##### 本地策略->安全选项

配置用户退出后再次登陆不会显示上次退出的用户名。  
![image.png](https://image.3001.net/images/20210321/1616302548_6056d1d412f5cc7130087.png!small)

## 安全配置加固——授权管理

授权账号登陆：目的是设置允许从本地或者远程登陆的账号

### 配置操作

开始->运行->secpol.msc->安全设置->本地策略->用户权限分配  
其中：  
从网络访问此计算机：设置相关账号  
![image.png](https://image.3001.net/images/20210321/1616302742_6056d296d876f06e79129.png!small)  
允许本地登录：设置相关账号  
![image.png](https://image.3001.net/images/20210321/1616302856_6056d308b3bfdf929c2bd.png!small)  
如果我们强制要求系统账号只能本地登陆无法通过远程的方式登陆的话，那就按如下设置：

双击“从网络访问此计算机”，将其中的全部删除  
![image.png](https://image.3001.net/images/20210321/1616302949_6056d365b41dd14501491.png!small)  
双击“允许本地登录”，其中的不要动  
![image.png](https://image.3001.net/images/20210321/1616303046_6056d3c64b3353e6a2e53.png!small)  
这样我们就能强制要求系统账号只能本地登陆无法通过远程的方式登陆了

