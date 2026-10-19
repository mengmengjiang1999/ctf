![](https://image.3001.net/images/20210425/1619326231_6084f517b194db491c640.png!small)

## 关于Swissknife

Swissknife是一个脚本化的VSCode扩展，可以帮助广大研究人员生成或修改数据，并防止在Web页面中泄露敏感数据。

## 当前可用的脚本

> Base64解码
>
> Base64编码
>
> 二进制转文本
>
> Bip39助记符
>
> CSV转Markdown
>
> 字符计数
>
> 单词计数
>
> 加密货币值
>
> 日期转时间戳
>
> 椭圆曲线密钥对
>
> 生成密码
>
> HTML编码（全部）
>
> 十六进制解码
>
> 十六进制编码
>
> 十六进制转RGB
>
> 标识哈希
>
> JWT解码
>
> Markdown转HTML
>
> Md5哈希
>
> 新Swissknife脚本（JS）
>
> 新Swissknife脚本（TS）
>
> 密码长度
>
> RGB转十六进制
>
> RSA密钥对
>
> 随机字符串
>
> 请求获取
>
> SHA1哈希
>
> SHA256哈希
>
> SHA512哈希
>
> 自签名证书
>
> 启动本地HTTP服务器
>
> 启动本地HTTPS服务器
>
> 停止HTTP服务器
>
> 文本转二进制
>
> 文本转字符串
>
> 时间戳转日期
>
> 驼峰命名
>
> 小写命名
>
> 摩斯密码
>
> 大写命名
>
> UUIDv4
>
> Unicode解码
>
> Unicode编码（js格式）
>
> Unix/Linux转人类可读
>
> Url解码
>
> Url编码
>
> Url编码（所有字符）
>
> Url缩短
>
> Url扩展

## 工具使用

在Windows系统或macOS上，你可以使用ctrl+shift+9调用专用命令pallete。默认配置下，仅会对选定的文本进行转换。如果未选择任何文本，则将使用编辑器的全部内容。它支持多重选择，并将为每个选择单独运行脚本。

如果你的电脑配有Macbook Touchbar的话，也可以直接从Macbook的Touchbar调用Swissknife扩展：

![](https://image.3001.net/images/20210425/1619326247_6084f52717525bdf8fa95.png!small)

## 部分脚本细节

### 加密货币值

使用Cryptonator的API，你可以直接转换文本内容，比如说：

    
    
    1btc to eur

### 识别哈希

操作的结果可能返回多个值，因为来自不同算法的哈希具有相同的输出格式。我们仍然按照最相关的顺序从上到下组织哈希。

### HTTPS(S)服务器

服务器会将接收到的所有请求记录到VSCode的“Output”窗口中（你可以通过进入菜单中的view->Output来查看）。然后可以在窗口的右侧（通常有“Tasks”值），按“Swissknife
Server”过滤。

## 脚本开发

Swissknife将自动加载其用户脚本文件夹中的所有脚本，你可以通过执行命令找到所需的脚本。打开命令行窗口，然后输入“Open swissknife
users script folder”，或者按照命令提示建议进行输入。

如需启动新的脚本，还可以使用扩展提供的命令。打开Swissknife Picker，，然后输入“New swissknife script”即可。

## 脚本模板

你可以根据自己的需要来选择TS或JS版本，TS比较复杂，因为我们需要将其转译为JS。这里我们使用JavaScript，下面给出的是脚本的基本结构：

    
    
    Object.defineProperty(exports, "__esModule", { value: true });
    
     
    
    exports.doSomething = async (text, context) => {
    
      return new Promise((resolve, reject) => {
    
     
    
        resolve(text.replace(/a/g, "b"));
    
     
    
      });
    
    }
    
    const scripts = [
    
      {
    
        title: "My Script",
    
        detail: "This script does something",
    
        cb: (context) => context.replaceRoutine(exports.doSomething)
    
      },
    
    ]
    
     
    
    exports.default = scripts;

这是创建脚本的基本模板。在这个文件中，我们创建了一个名为“My
Script”的脚本。每个文件可以有任意数量的脚本，这只是一种组织方式。脚本的结构由3个属性组成：title、detail和cb。其中的cb是脚本运行时将调用的代码。

## 更多样本

    
    
    Object.defineProperty(exports, "__esModule", { value: true });
    
     
    
    //Uses the context.modules to reuse existing code. Starts an http server
    
    exports.startServer = async (context) => {
    
      context.modules.lib.server.start({ port: 1234 })
    
    }
    
     
    
    //uses context.userModules to invoke another user script
    
    //there will be an entry in context.userModules with the name of the file with scripts loaded
    
    //all exported methods are accessible...
    
    //If  invoking a script remember to send the right params, like the context
    
    exports.anotherUserScript = async (context) => {
    
      context.modules.othermodule.hellowWorld(context);
    
    }
    
     
    
    //Ask user for input
    
    exports.askInput = async (context) => {
    
      return new Promise((resolve, reject) => {
    
        context.vscode.window.showInputBox({ prompt: "Say something" }).then(answer => {
    
          resolve(answer);
    
        });
    
      });
    
    }
    
    const scripts = [
    
      {
    
        title: "Ask Input",
    
        detail: "Asks user input and adds it to the editor",
    
        cb: (context) => context.insertRoutine(this.askInput)
    
      },
    
      {
    
        title: "Start server on port 1234",
    
        detail: "Starts a server on port 1234",
    
        cb: (context) => this.startServer(context)
    
      },
    
      {
    
        title: "Call Another User script",
    
        detail: "Calls Another User script",
    
        cb: (context) => context.insertRoutine(this.anotherUserScript)
    
      },
    
    ]
    
     
    
    exports.default = scripts;

## 项目地址

 **Swissknife：** https://github.com/luisfontes19/vscode-swissknife/

