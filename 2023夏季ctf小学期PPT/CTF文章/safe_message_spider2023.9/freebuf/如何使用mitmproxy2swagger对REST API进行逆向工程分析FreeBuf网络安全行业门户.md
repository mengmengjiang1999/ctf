## 关于mitmproxy2swagger

mitmproxy2swagger是一款功能强大的逆向工程分析工具，该工具能够以自动化的形式将捕捉到的[
_mitmproxy_](https://mitmproxy.org/)数据转换为符合[ _OpenAPI
3.0规范_](https://swagger.io/specification/)的数据。这也就意味着，在该工具的帮助下，广大研究人员能够以自动化的形式对REST
API进行逆向分析，并捕捉流量数据。

除此之外，该工具还可以支持从浏览器开发者工具导出并处理HAR文件，具体可以参考这篇【 _文档_】。

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3和pip 3环境。

接下来，我们可以使用下列命令直接将该项目源码克隆至本地：

    
    
    git clone https://github.com/alufers/mitmproxy2swagger.git

除此之外，我们还可以通过pip或pip3来直接安装mitmproxy2swagger：

    
    
    $ pip install mitmproxy2swagger
    
    # ... 或 ...
    
    $ pip3 install mitmproxy2swagger

## 工具使用

### Mitmproxy

首先，通过运行mitmproxy工具来捕捉流量数据，我们建议大家使用mitmweb，也就是内置在mitmproxy中的一个Web接口：

    
    
    $ mitmweb
    
    Web server listening at http://127.0.0.1:8081/
    
    Proxy server listening at http://*:9999
    
    ...

接下来，将捕捉到的流量数据存储到流文件中。在mitmweb中，我们可以点击“File”菜单，并选择“Save”：

![](https://image.3001.net/images/20220612/1655017989_62a59205eb15a83bb3d44.png!small)

第三步，使用下列参数命令来运行mitmproxy2swagger：

    
    
    $ mitmproxy2swagger -i <path_to_mitmptoxy_flow> -o <path_to_output_schema> -p <api_prefix>

需要注意的是，我们可以直接使用已有的schema，并根据需要来进行自定义扩展。

其中的<api_prefix>是需要进行逆向工程分析的目标API的URL基地址前缀，然后可以在mitmproxy中观察请求以及响应数据。

比如说，如果一个App发送了如下所示的请求：

    
    
    https://api.example.com/v1/login
    
    https://api.example.com/v1/users/2
    
    https://api.example.com/v1/users/2/profile

那么URL基地址前缀则为https://api.example.com/v1。

然后，在schema文件中创建如下所示的字段：

    
    
    x-path-templates:
    
    # Remove the ignore: prefix to generate an endpoint with its URL
    
    # Lines that are closer to the top take precedence, the matching is greedy
    
    - ignore:/addresses
    
    - ignore:/basket
    
    - ignore:/basket/add
    
    - ignore:/basket/checkouts
    
    - ignore:/basket/coupons/attach/{id}
    
    - ignore:/basket/coupons/attach/104754

在代码编辑器中打开一个schema文件，并移除目标生成路径的“ignore:”前缀，或者在路径中添加其他的参数。

最后，运行mitmproxy2swagger即可：

    
    
    $ mitmproxy2swagger -i <path_to_mitmptoxy_flow> -o <path_to_output_schema> -p <api_prefix> [--examples]

### HAR

首先，从浏览器的开发者工具捕捉并导出流量。在浏览器的开发者工具中，切换到“Network”标签，并点击“Export HAR”按钮：

![](https://image.3001.net/images/20220612/1655018035_62a5923368645acb5f31f.png!small)

接下来，运行mitmproxy2swagger，工具将会自动检测HAR文件并对其进行数据分析和处理。

## 工具输出样例

 **输出样例：** 【[ _lisek-out.swagger.yml_](https://github.com/alufers/mitmproxy2swagger/blob/master/example_outputs/lisek-out.swagger.yml)】

## 工具使用演示

 **视频地址：** 【[ _mitmproxy2swagger_ _.mp4_](https://user-images.githubusercontent.com/5400940/168086818-c48f60ab-3f95-42eb-b435-c8b1a6326b81.mp4)】

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **mitmproxy2swagger：** 【[
_GitHub传送门_](https://github.com/alufers/mitmproxy2swagger)】

## 参考资料

> [ _https://mitmproxy.org/_](https://mitmproxy.org/)
>
> [ _https://swagger.io/specification/_](https://swagger.io/specification/)
>
> [
> _https://github.com/alufers/mitmproxy2swagger#har_](https://github.com/alufers/mitmproxy2swagger#har)
>
> [ _https://docs.mitmproxy.org/stable/_](https://docs.mitmproxy.org/stable/)
>
> [ _https://www.npmjs.com/package/redoc-> cli_](https://www.npmjs.com/package/redoc-cli)

