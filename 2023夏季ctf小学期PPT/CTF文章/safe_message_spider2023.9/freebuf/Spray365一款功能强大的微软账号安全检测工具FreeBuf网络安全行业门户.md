![](https://image.3001.net/images/20220117/1642417091_61e54bc35641ab7a5bc19.png!small)

## 关于Spray365

Spray365是一款功能强大的密码喷射工具，该工具主要针对微软服务而设计，可以帮助广大研究人员通过密码喷射技术识别微软账号（Office 365 /
Azure AD）中的有效凭证。

Spray365允许从一个“执行计划”中进行密码喷射，预先生成的执行计划会在密码喷射行为发生之前就进行了描述，这样做会有很多好处，这也允许广大研究人员在网络错误或其他中断情况发生后继续恢复密码喷射（-R选项）。我们可以直接选择使用Spray365生成的Spray365执行计划，或者利用其他能够生成兼容JSON结构的工具来构建专门的密码喷射工作流。

Spray365提供了一些针对凭证喷射的实用选项，其中的随机用户代理可用于检测和绕过配置为“限制允许设备类型”的不安全条件访问策略。类似的，“--shuffle_auth_order”参数是一种基于“最小预测”模式的密码喷射方式，虽然这种方式不是很完美，但随机尝试凭证的顺序也有其他好处，比如说可以提升检测密码喷射行为的难度等等。除此之外，Spray365还支持HTTP/HTTPS代理，并且能够跟Burp
Suite之类的工具进行集成。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/MarkoH17/Spray365

然后切换至项目根目录中，运行下列命令安装该工具所需的Python包，并运行Spray365：

    
    
    $ cd Spray365
    
    ~/Spray365$ pip3 install -r requirements.txt
    
    ~/Spray365$ python3 spray365.py

## 工具使用

### 生成一个执行计划

Spray365必须通过一个“执行计划”来实现密码/凭证喷射，因此我们首先需要创建一个“执行计划”。我们可以使用-g（生成）模式来让Spray365生成自己的执行计划：

    
    
    $ python3 spray365.py -g <path_for_saved_execution_plan> -d <domain_name> -u <file_containing_usernames> -pf <file_containing_passwords>

 **参考样例如下：**

    
    
    $ python3 spray365.py -g ex-plan.s365 -d example.com -u usernames -pf passwords

### 执行计划喷射

但生成好了一个“执行计划”之后，Spray365就可以开始处理这个执行计划了。以-s（喷射）模式来运行Spray365之后，Spray365将会处理指定的执行计划，并喷射对应的凭证：

    
    
    $ python3 spray365.py -s <path_to_execution_plan>

 **参考样例如下：**

    
    
    $ python3 spray365.py -s ex-plan.s365

## 工具高级选项

### 生成模式选项

    
    
    --delay <int>
    
    -cID / --aad_client <string>
    
    -S / --shuffle_auth_order
    
    -mD / --min_cred_loop_delay
    
    -SO / --shuffle_optimization_attempts <int>
    
    -mD / --min_cred_loop_delay <int>
    
    -cUA / --custom_user_agent <string>
    
    -rUA, --random_user_agent

### 喷射模式选项

    
    
    --lockout <int>
    
    --proxy <string>
    
    -R / --resume_index <int>

## 工具运行截图

### 生成一个“执行计划”（第一步）

![](https://image.3001.net/images/20220117/1642417167_61e54c0f7cb66141c5634.png!small)

### 使用“执行计划”喷射密码凭证（第二步）

![](https://image.3001.net/images/20220117/1642417174_61e54c16e1ba688d4e028.png!small)

## 项目地址

 **Spray365：** 【[ _GitHub传送门_](https://github.com/MarkoH17/Spray365)】

