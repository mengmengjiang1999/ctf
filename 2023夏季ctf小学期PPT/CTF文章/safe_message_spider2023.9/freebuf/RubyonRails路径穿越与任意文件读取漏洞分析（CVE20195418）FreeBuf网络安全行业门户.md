***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：LEdge1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

 **Ruby on Rails是一个 Web 应用程序框架,是一个相对较新的 Web 应用程序框架，构建在 Ruby
语言之上。它被宣传为现有企业框架的一个替代，而它的目标，就是让 Web 开发方面的生活，变得更轻松。**

【CVE-2019-5418】漏洞公告：[](https://groups.google.com/forum/#!topic/rubyonrails-security/pFRKI96Sm8Q) [公告地址](http://www.example.com)。  

    
    
    Versions Affected:  All. 
    Not affected:       None. 
    Fixed Versions:     6.0.0.beta3, 5.2.2.1, 5.1.6.2, 5.0.7.2, 4.2.11.1 
    Impact 
    There is a possible file content disclosure vulnerability in Action View. 
    Specially crafted accept headers in combination with calls to render file: 
    can cause arbitrary files on the target server to be rendered, disclosing the 
    file contents. 
    The impact is limited to calls to render which render file contents without 
    a specified accept format.  Impacted code in a controller looks something like 
    this: 
    class UserController < ApplicationController 
    def index 
        render file: "#{Rails.root}/some/file" 
    end 
    end
    

这个漏洞主要是由于网站使用了为指定参数的render
file来渲染应用之外的视图，我们可以通过修改访问某控制器的请求包，通过“../../../../”来达到路径穿越的目的，然后再通过“{{”来进行模板查询路径的闭合，使得所要访问的文件被当做外部模板来解析。``

## 实验环境

> Centos7桌面版，装有Ruby On Rails环境。

##  **Ruby On Rails** **环境搭建**

1\. 安装git #yum install git

2\. 安装rbenv到~/.rbenv目录

    
    
    git clonegit://github.com/sstephenson/rbenv.git~/.rbenv

3\. 安装rbenv的插，用来编译安装 ruby

    
    
    git clonegit://github.com/sstephenson/ruby-build.git~/.rbenv/plugins/ruby-build

4\. 用来管理 gemset, 可选, 因为有 bundler 也没什么必要

    
    
    git clone git://github.com/jamis/rbenv-gemset.git ~/.rbenv/plugins/rbenv-gemset

5\. 通过 gem 命令安装完 gem 后无需手动输入 rbenv rehash 命令

    
    
    git clonegit://github.com/sstephenson/rbenv-gem-rehash.git~/.rbenv/plugins/rbenv-gem-rehash

6\. 通过 rbenv update 命令来更新 rbenv 以及所有插件

    
    
    git clone git://github.com/rkh/rbenv-update.git~/.rbenv/plugins/rbenv-update

7\. 使用 Ruby China 的镜像安装 Ruby, 国内用户推荐

    
    
    git clonegit://github.com/AndorChen/rbenv-china-mirror.git~/.rbenv/plugins/rbenv-china-mirror

8\. 然后需要将下面两句代码放在bash的配置文件中：

    
    
    export PATH="$HOME/.rbenv/bin:$PATH"
    
    eval "$(rbenv init -)"

9\. 位置是在.bash_profile（Ubuntu中应该是.bashrc）修改完成后，执行下面的命令使其生效

    
    
    source ~/.bashrc

10\. 安装ruby

    
    
    rbenv install --list  # 列出所有ruby 版本
    
    rbenv install 2.3.3   #安装2.3.3版本Ruby

11\. 设置使用的ruby版本

    
    
    rbenv global 2.3.3      # 默认使用2.3.3，此步骤不能省略
    
    ruby –v                #查看安装的Ruby版本

12\. 安装rails

设置ruby版本后，安装rails（指定rails版本）：

1）在当前的ruby版本中安装rails

    
    
    gem install rails -v 5.2.1   #指定版本

2）查看rails安装版本

    
    
    rails –v

3）修改bundle的源地址（可能需要修改，视情况而定。）

    
    
    bundle config mirror.<https://rubygems.orghttps://gems.ruby-china.org>

[](https://rubygems.orghttps://gems.ruby-china.org)

执行bundleinstall

在项目根目录执行bundleinstall

问题解决（在安装和运行的过程中，可能会出现各种各样的问题， [](http://www.example.com)
[](http://www.example.com) [](http://www.example.com)
[](http://www.example.com) [](http://www.example.com)
[](http://www.example.com)
[](http://www.example.com)[链接文字](http://www.example.com)我就是安装下面的这些依赖的，但是不一定和我这个一样，大家还是根据自己的提示来吧）：

    
    
    yum -y install gcc
    
    yum install flex autoconf zlib curlzlib-devel curl-devel bzip2 bzip2-develncurses-devel libjpeg-devel libpng-devel libtiff-develfreetype-devel pam-develgcc+ gcc-c++ libxml2 libxml2-devel libxslt libxslt-devel 
    
    yum install sqlite*

## 漏洞复现

1\. 先下载原码（;">路径“/root /CVE-2019-5418/”），
[源码地址](https://github.com/mpgn/CVE-2019-5418)。

2\. 进入“/root”路径下，执行“source .bash_profile”

![image.png](https://image.3001.net/images/20190331/1554000424_5ca02a28536ec.png!small)  

3\. 将下载得到的压缩包进行解压，进入demo路径下执行：

    
    
    bundle install

4\. 在demo路径下执行“rails s”,开启服务。

![image.png](https://image.3001.net/images/20190331/1554000454_5ca02a46753fa.png!small)5\.
此时漏洞环境已搭建完成且开始运行，使用浏览器测试能否访问。如下图表示可正常访问  

![image.png](https://image.3001.net/images/20190331/1554000471_5ca02a57b73aa.png!small)6\.
访问“chybeta”路径：  

7\. 我们使用浏览器自带的开发者工具进行漏洞复现，按“f12”打开工具，修改这条请求，修改内容如下：

    
    
     ../../../../../../etc/passwd{{

![image.png](https://image.3001.net/images/20190331/1554000665_5ca02b19ec186.png!small)

![image.png](https://image.3001.net/images/20190331/1554000518_5ca02a8620c64.png!small)![image.png](https://image.3001.net/images/20190331/1554000528_5ca02a90dc5d3.png!small)

8\. 漏洞复现成功，成功读取到passwd文件的内容：  

![image.png](https://image.3001.net/images/20190331/1554000697_5ca02b3926e1c.png!small)

9\. 或者，我们也可以使用burp
suite来抓包，设置好浏览器代理，访问“/chybeta”路径抓包.我们只要修改好流量包的内容重新发送即可。用浏览器自带的工具实现功能，我就不想在使用Burp
suite了。之后就可以很简单的得到目标主机的passwd文件内容。  

## 漏洞分析

漏洞影响所有版本的rails，但是目前已经有几个版本修复了此漏洞：

    
    
    6.0.0.beta3,
    
    5.2.2.1
    
    5.1.6.2
    
    5.0.7.2
    
    4.2.11.1

我们先看一下正常访问时什么样的吧：  

![image.png](https://image.3001.net/images/20190331/1554000857_5ca02bd97a098.png!small)可以看到我们每获取一个请求，Ruby
On Rails就会使用Render
file（没有指定参数）的渲染模式来渲染目标。这样就会在我们攻击的时候，将目标文件当做模板来渲染，然后返回给浏览器：哈哈哈哈。

**![image.png](https://image.3001.net/images/20190331/1554000963_5ca02c4383ca6.png!small)**
** ****** rails在控制器中通过render
file形式来渲染应用之外的视图，因此在“.rbenv/versions/2.3.3/lib/ruby/gems/2.3.0/gems/actionview-5.2.1/lib/action_view/renderer/template_renderer.rb”中会根据“options.key?(:file)”，调用“find_file”函数来寻找视图。代码如下：

    
    
    module ActionView
    
      class TemplateRenderer < AbstractRenderer#:nodoc:
    
        # Determine the template to be renderedusing the given options.
    
          def determine_template(options)
    
            keys = options.has_key?(:locals) ?options[:locals].keys : []
    
            if options.key?(:body)
    
              ...
    
            elsif options.key?(:file)
    
              with_fallbacks {find_file(options[:file], nil, false, keys, @details) }
    
            ...
    
          end
    
    end

“find_file”代码如下（路径为：“.rbenv/versions/2.3.3/lib/ruby/gems/2.3.0/gems/actionview-5.2.1/lib/action_view/lookup_context.rb”）

![image.png](https://image.3001.net/images/20190331/1554001474_5ca02e4258dd1.png!small)

发现“find_file”又调用了“*args_for_lookup”,所以我们继续跟入查看“args_for_lookup”函数，代码如下：

![image.png](https://image.3001.net/images/20190331/1554001565_5ca02e9d874b8.png!small)

此函数会生成用于查找文件的参数，当其最终返回时会把payload保存在details[formats]中(大家自己做实验的时候可以直接访问一个不存在的文件，这样会直接显示访问的详细信息)。

再回到“find_file”函数，跟进之后，会进入到：“.rbenv/versions/2.3.3/lib/ruby/gems/2.3.0/gems/actionview-5.2.1/lib/action_view/path_set.rb”。

    
    
    class PathSet #:nodoc:
    
       def find_file(path, prefixes = [], *args)
    
         _find_all(path, prefixes, args, true).first ||raise(MissingTemplate.new(self, path, prefixes, *args))
    
       end
    
       private
    
        #注，这里的 args 即前面args_for_lookup生成的details
    
           def _find_all(path, prefixes, args, outside_app)
    
               prefixes = [prefixes] if String === prefixes
    
               prefixes.each do |prefix|
    
               paths.each do |resolver|
    
                    if outside_app
    
                    templates =resolver.find_all_anywhere(path, prefix, *args)
    
                    else
    
                    templates =resolver.find_all(path, prefix, *args)
    
                    end
    
                    return templates unlesstemplates.empty?
    
               end
    
               end
    
               []
    
           end

由于要渲染的视图在应用之外（outside_app,因此跟入“find_all_anywhere”（在“.rbenv/versions/2.3.3/lib/ruby/gems/2.3.0/gems/actionview-5.2.1/lib/action_view/template/resolver.rb”）：

    
    
    def find_all_anywhere(name, prefix, partial= false, details = {}, key = nil, locals = [])
    
       cached(key, [name, prefix, partial], details, locals) do
    
       find_templates(name, prefix, partial, details, true)
    
       end
    
    end

进入find_templates，这就是根据条件来查找要渲染的模板：  

![image.png](https://image.3001.net/images/20190331/1554002152_5ca030e8038b1.png!small)

从代码便可以看到，所查找的模板会赋值给details[:formats],如果建立建立查询后，查询内容就会如下：  

![image.png](https://image.3001.net/images/20190331/1554002302_5ca0317e8aa09.png!small)

利用../与前缀组合造成路径穿越，利用最后的{{完成闭合。

最后“/etc/passwd”被当成模板文件进行渲染，最后造成了任意文件读取。

使用IDE环境进行调试，最后组成的路径应该是：

    
    
    /etc/passwd{{},}{+{},}{.{raw,erb,html,builder,ruby,coffee,jbuilder},}

##  **漏洞修复**  

> 1\. 使用已经修复该漏洞的版本
>
> 2\.
> 补丁：[补丁地址](https://github.com/rails/rails/commit/f4c70c2222180b8d9d924f00af0c7fd632e26715)

 ***本文作者：LEdge1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

