![](https://image.3001.net/images/20220210/1644483494_6204d3a694f1e4826732a.jpeg!small)  

## 关于Gh-Dork

Gh-Dork是一款功能强大的Github
Dorking工具，我们只需要给该工具提供一个Dork列表以及对应的选项，工具便可以输出所有的Dorking内容。

## 工具参数

> -u：目标用户
>
> -uf：包含目标用户的列表文件
>
> -org：目标组织机构
>
> -of：包含 目标组织机构的列表文件
>
> -r：目标代码库

除此之外，我们还可以传递下列高级参数：

> -o：指定存储Dorking结果的输出目录；
>
> -vif：如果你的目标用户或组织机构文件可能不存在的情况下，可以使用该参数指定存储有效数据的文件名；

注意：所有的输入文件以及数据都需要按行分隔开。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/molly/gh-dork.git

接下来，使用下列命令安装好该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

## 工具使用

该工具的直接运行仅需要一个-d参数即可，即提供Dork文件。

如果制定了输出目录的话，工具将会为dork列表中的每一个dork创建一个专门的文件，并将相关的数据结果存储到这个文件中，然后打印出来。

如果你的用户文件或组织文件中数据还没有进行过滤并移除不存在的用户/组织的话，我们强烈建议广大用户在运行该工具时添加一个“--valid-items-filename”（-vif）参数。该参数可以帮助我们在搜索dork内容时，过滤掉无效的用户或入职，以避免影响后续dork内容的搜索效率。

输出文件还可以用作用户/组织的输入参数，以提升后续脚本的运行。

## 工具使用样例

 **工具基础使用：**

    
    
    python gh-dork.py -d dorks.txt

 **搜索指定用户的代码库：**

    
    
    python gh-dork.py -d dorks.txt -u molly

 **搜索列表中所有用户的代码库：**

    
    
    python gh-dork.py -d dorks.txt -uf users.txt

 **搜索列表中所有用户的代码库，并过滤掉不存在的用户：**

    
    
    python gh-dork.py -d dorks.txt -uf users.txt -vif valid_users.txt

 **搜索指定组织机构的代码库：**

    
    
    python gh-dork.py -d dorks.txt -org github

 **搜索列表中所有组织机构的代码库：**

    
    
    python gh-dork.py -d dorks.txt -of orgs.txt

 **搜索列表中所有组织机构的代码库，并过滤掉不存在的组织机构：**

    
    
    python gh-dork.py -d dorks.txt -of orgs.txt -vif valid_orgs.txt

 **搜索指定代码库：**

    
    
    python gh-dork.py -d dorks.txt -r molly/gh-dork

 **将搜索结果存储到results/目录下：**

    
    
    python gh-dork.py -d dorks.txt -o results

## 身份认证

身份认证是通过环境变量实现的，我们可以使用一个GitHub私人访问令牌（GH_TOKEN）或用户名及密码（GH_USER和GH_PASS）来实现身份认证。如果你还启用了双因素身份验证功能的话，工具将提示你输入一个双因素验证码。

除此之外，你还可以给工具传递一个GitHub企业URL（GH_URL）以搜索GitHub实例。如果不提供的话，工具将默认搜索github.com。

如果你没有提供凭证或凭证无效的话，虽然脚本仍然会继续运行，但会受到网站针对未认证用户所设置的[
_访问频率限制_](https://docs.github.com/en/rest/reference/search)。

## 项目地址

 **Gh-Dork：** 【[ _GitHub传送门_](https://github.com/molly/gh-dork)】

## 参考资料

> [ _https://github.com/techgaun/github-dorks/blob/master/github-> dorks.txt_](https://github.com/techgaun/github-dorks/blob/master/github-> dorks.txt)
>
> [
> _https://docs.github.com/en/rest/reference/search_](https://docs.github.com/en/rest/reference/search)

