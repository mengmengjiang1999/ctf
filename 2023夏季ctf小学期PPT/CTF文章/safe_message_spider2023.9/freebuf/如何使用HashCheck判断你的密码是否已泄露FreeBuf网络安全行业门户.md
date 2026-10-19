![](https://image.3001.net/images/20210716/1626438693_60f17c25c08b2cecfad4f.png!small)

## 关于HashCheck

HashCheck项目旨在帮助广大用户搜索泄露的密码，并判断自己的密码安全态势，同时保持高等级的隐私保护程度。

为了实现我们的目标，HashCheck使用了各种不同服务所提供的API，我们只需要检查密码哈希的一部分即可实现密码泄露判断，比如说密码哈希的前五个字符。

## 工具要求

该项目需要使用某些代码库才能正常工作，我们只需运行下列命令即可安装：

    
    
    pip install -r requirements

别忘了，先要在本地环境中安装好Python 3。

## 工具使用

    
    
    passme.py [FUNC] [ELEMENT] -engine [ENGINE] -api_key [API_KEY]
    
        FUNC:       The kind of element tha you want to check, it can be -h/--hash or -p/--password
    
                    or -f/--file or -l/--list or --help.
    
     
    
        ELEMENT:    The "Hash", "Password" or the name of the file that contains a list of
    
                    hashes or password separeted by a new line.
    
     
    
        ENGINE:     The leaks engine that you want to be used, by default it uses HIBP (Have I been PWN).
    
     
    
        API_KEY:    The API_KEY necessary for some functions of some engines.

## 功能函数

### PASSME_HASH

该项目的主要功能函数，负责接收一个密码哈希，并调用分析引擎和API密钥。API密钥和密码哈希必须根据情况发送至其他函数。

如果你想要添加自己的引擎或实现一个还未实现的引擎，只需要多添加一个选项即可：

    
    
    passme_hash(hashed_password, engine="HIBP", api_key="0")

### PASSME_PASSWORD

这个函数会使用SHA-1对密码进行哈希计算，并将哈希发送至passme_hash()函数：

    
    
    passme_password(password, engine="HIBP", api_key="0")

### PASSME_FILE

这个函数可以按行读取接收到的文件内容，并检查每一个密码，然后给出接收到的密码的相关信息：

    
    
    passme_file(filename, engine="HIBP", api_key="0")

### PASSME_LIST

这个函数可以按行读取接收到的文件内容，并检查每一个密码哈希，然后给出接收到的密码哈希的相关信息：

    
    
    passme_list(filename, engine="HIBP", api_key="0")

### PASSME_HIBP

这个函数可以处理HIBP（Have I Been Pwned） API，并发送密码哈希的前五个字符，然后跟完整的密码哈希进行比对，以判断密码是否已泄露：

    
    
    engine_HIBP(hashed_password, engine, api_key)

## 功能测试

这个项目还提供了大量的测试用例以判断功能函数是否能够正常运行，如果需要测试的话，还需要安装“pytest”库：

    
    
    pip install pytest

安装好之后，只需要运行“pytest”命令即可自动运行完整的测试用例。

## 项目地址

 **HashCheck：** 【[ _GitHub传送门_](https://github.com/Telefonica/HashCheck)】

## 许可证协议

本项目的开发与发布遵循GNU开源许可证协议。

