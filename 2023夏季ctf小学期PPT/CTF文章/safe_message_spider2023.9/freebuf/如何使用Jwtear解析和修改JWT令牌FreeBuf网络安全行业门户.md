## 关于Jwtear

Jwtear是一款模块化的命令行工具，该工具可以帮助广大研究人员从安全研究的角度来解析、创建和修改JSON Web令牌（JWT）。

## 功能介绍

完整的模块化组件：所有的命令都是插件，可以轻松添加新的插件；

> 支持JWS和JWE令牌；
>
> 提供了易于使用的接口和模版；
>
> 高灵活性，轻松可扩展新功能；
>
> 基于生产类库的令牌生成机制，例如json-jwt和jwe等；

## 可用插件

> Parse：解析JWT令牌；
>
> jsw：修改和生成JWS令牌；
>
> jwe：修改和生成JWE令牌；
>
> bruteforce：暴力破解JWS签名密钥；
>
> wiki：包含关于JWT和攻击相关的离线信息；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/KINGSABRI/jwtear.git

除此之外，我们也可以使用gem命令下载和安装Jwtear：

    
    
    $ gem install jwtear

## 工具使用

 **显示工具帮助信息** ：

    
    
    命令解释：
    
    help             - 显示命令帮助信息
    
        bruteforce, bfs   - 用于离线破解令牌签名的插件
    
        jws, s           - 生成基于签名的JWT（JWS）令牌
    
        jwe, e           - 生成基于加密的JWT（JWE）令牌
    
        parse           - 解析JWT令牌（接受JWS和JWE格式）
    
        wiki, w          - 为研究人员提供的JWT WiKi

 **使用“-h COMMAND”命令可以查看相关命令的参数选项** ：

    
    
    $jwtear -h jws
    
     
    
    NAME
    
        jws - 成基于签名的JWT（JWS）令牌
    
     
    
    SYNOPSIS
    
        jwtear [global options] jws [command options]
    
     
    
    DESCRIPTION
    
        生成JWS和JWE令牌 
    
     
    
    COMMAND OPTIONS
    
        -h, --header=JSON               - JWT header (JSON 格式)。例如： {"typ":"JWT","alg":"HS256"}. Run 'jwtear gen -l' for supported algorithms. (必须, 默认: none)
    
        -p, --payload=JSON              - JWT payload (JSON 格式)。例如： {"login":"admin"} (必须, 默认: none)
    
        -k, --key=PASSWORD|PUB_KEY_FILE - 密钥作为密码字符串或文件公共密钥。例如：P@ssw0rd  | eg. public_key.pem (默认: none)

 **使用一个插件** ：

插件是以子命令的形式定义的，每一个子命令都有一个或多个参数进行控制：

    
    
    $ jwtear parse -t eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.J8SS8VKlI2yV47C4BtfYukWPx_2welF34Mz7l-MNmkE
    
    $ jwtear jws -h '{"alg":"HS256","typ":"JWT"}' -p '{"user":"admin"}' -k p@ss0rd123
    
    $ jwtear jwe -header '{"enc":"A192GCM","typ":"JWT"}' --payload '{"user":"admin"}' --key public.pem
    
    $ jwtear bruteforce -v -t eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjpudWxsfQ.Tr0VvdP6rVBGBGuI_luxGCOaz6BbhC6IxRTlKOW8UjM -l ~/tmp/pass.list

## 添加插件

如需添加一个新的插件，则要在“plugins”目录下创建一个新的Ruby文件，其中包含下列结构数据：

    
    
    module JWTear
    
      module CLI
    
        extend GLI::App
    
        extend JWTear::Helpers::Extensions::Print
    
        extend JWTear::Helpers::Utils
    
     
    
        desc "Plugin short description"
    
        long_desc "Plugin long description"
    
        command [:template, :pt] do |c|
    
          c.action do |global, options, arguments|
    
            print_h1 "Plugin template"
    
            print_good "Hi, I'm a template."
    
            template = TemplatePlugin.new
    
          end
    
        end
    
      end
    
     
    
      module Plugin
    
        class TemplatePlugin
    
          include JWTear::Helpers::Extensions::Print
    
          include JWTear::Helpers::Utils
    
     
    
          def initialize
    
            check_dependencies
    
            # ..code...
    
          end
    
         
    
          # ..code...
    
        end
    
      end
    
    end

其中，我们可以将所需的依赖组件以哈希形式添加到“check_dependencies”方法中：

    
    
    deps = {'async-io' => 'async/ip'}
    
    check_dependencies(deps)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://opensource.org/licenses/MIT)开源许可证协议。

## 项目地址

 **Jwtear** ：【[ _GitHub传送门_](https://github.com/KINGSABRI/jwtear)】

