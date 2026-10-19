## GitHub Action介绍

GitHub Actions 是一种持续集成和持续交付 (CI/CD)
平台，可用于自动化构建、测试和部署应用程序，执行代码质量检查，创建和发布软件包，发送通知，执行持续集成和持续部署等等。
**可以根据自己的需求和工作流程来定义和配置这些自动化任务** 。

  * [官方中文文档](https://docs.github.com/zh/actions/quickstart)

  * [GitHub Action市场](https://github.com/marketplace?type=actions)

可以理解为GitHub提供了一台最长可以使用[6小时](https://docs.github.com/zh/actions/learn-github-actions/usage-limits-billing-and-administration)的云服务器，每次push代码时，该云服务器都会按照你提前设定好的流程去执行一遍。

## 简单演示

> 以构建简单的 **subfinder子域名收集 - nuclei漏扫**
> 为例，先使用subfinder进行子域名收集，然后使用nuclei进行漏扫，最后将结果上传到GitHub的当前仓库中。

创建git项目，编写`.github/workflows/blank.yml`内容如下，基本上都能看懂每一步干啥，每个字段解读可参考[官方文档](https://docs.github.com/zh/actions/learn-github-actions/understanding-github-actions#%E4%BA%86%E8%A7%A3%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%A8%8B%E6%96%87%E4%BB%B6)

    
    
    name: CI
    on:
      push:
        branches: [ "main" ]
      pull_request:
        branches: [ "main" ]
      workflow_dispatch:
    
    jobs:
      build:
        runs-on: ubuntu-latest
    
        steps:
          # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
          - uses: actions/checkout@v3
    
          # Setup Go environment
          - name: Setup Go environment
            uses: actions/setup-go@v4.0.1
            with:
              go-version: 1.20.1
    
          # 安装subfinder 和 nuclei
          - name: Run Install
            run: |
              go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
              go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
    
          # 使用
          - name: Run tools
            shell: bash
            run: |
              domain=$(cat input/domain.txt)
              subfinder -d $domain -o output/subdomains.txt
              nuclei -l output/subdomains.txt -o output/vuln.txt -s medium
    
          # push到当前仓库
          - name: Commit files
            run: |
              git config --local user.email "github-actions[bot]@users.noreply.github.com"
              git config --local user.name "github-actions[bot]"
              git add *
              git commit -m "commit change file"
    
          - name: GitHub Push
            # You may pin to the exact commit or the version.
            # uses: ad-m/github-push-action@40bf560936a8022e68a3c00e7d2abefaf01305a6
            uses: ad-m/github-push-action@v0.6.0
            with:
              # Token for the repo. Can be passed in using $\{{ secrets.GITHUB_TOKEN }}
              github_token: ${{ secrets.GITHUB_TOKEN }}
              branch: ${{ github.ref }}
    

  
整体目录结构如下：

    
    
    .
    ├── .github
    │   └── workflows
    │       └── blank.yml
    ├── .gitignore
    ├── input
    │   └── domain.txt // 内容为gm7.org
    └── output
        └── res.txt
    

  
上传到Github中，Github将会通过Action自动构建，按照我们设置的流程运行，结果如下。

![res](https://image.3001.net/images/20230605/1685929264_647d3d309505d3c1adb40.png!small)

结果push到仓库，可随时查看。

![push](https://image.3001.net/images/20230605/1685929268_647d3d34b3b0f63a42452.png!small)

## 注意事项

### 创建workflow

如果要从头写一个workflow的话，建议在Github中新建模板后再改。

![action](https://image.3001.net/images/20230605/1685929272_647d3d38a94cc532e8eb7.png!small)

此外右边有语法参考，还可以直接从市场复制想要的东西，很方便。

![cankao](https://image.3001.net/images/20230605/1685929277_647d3d3df1e55d4d9a55b.png!small)

### remote: Write access to repository not granted.

需要在当前仓库的设置中，赋予workflow写权限。

![image-20230602下午21707374](https://image.3001.net/images/20230605/1685929282_647d3d4218138fb37075c.png!small)

### 速度方面

个人感觉速度比较慢，比较欠缺，有这精力不如直接买台服务器配了，一劳永逸。

