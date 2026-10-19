> 在 GitHub Actions 的仓库中自动化、自定义和执行APP开发工作流程。 您可以发现、创建和共享操作以执行您喜欢的任何作业（包括
> CI/CD），并将操作合并到完全自定义的工作流程中。

Action 能干啥？都能干，前段时间还有人挖矿

下面所有的用户名和仓库用 `laowang`和 `zhangshan`代替

## Actions secrets

一些不方便的隐私的东西可以放进去，然后用环境变量代替

https://github.com/laowang/zhangshan/settings/secrets/actions

    
    
    # 推荐变量名
    DOCKERHUB_PASSWORD 123456   ${{ secrets.DOCKERHUB_PASSWORD }}
    DOCKERHUB_TOKEN 123456      ${{ secrets.DOCKERHUB_TOKEN }}
    DOCKERHUB_USERNAME laowang  ${{ secrets.DOCKERHUB_USERNAME }}
    TOKEN_GITHUB 123456					 ${{ secrets.TOKEN_GITHUB }}
    

## Action.yml

这是一个简单的action文件

    
    
    name: laowang de action
    
    on:
      push
    
    jobs:
      laowang_de_action:
        name: laowang de action
        runs-on: ubuntu-latest
        steps:
          - 
            name: Private Actions Checkout
            uses: actions/checkout@v2.3.4
          - 
            name: Docker Setup QEMU
            uses: docker/setup-qemu-action@v1.2.0
          	run: echo "hello word"
    

### on

    
    
    on:
      push:
        branches:
          - main # 当仓库分支 main 有更新的时候 运行action
      repository_dispatch:
        types: [laowang] # 当仓库接收到 laowang 信号的时候 运行action
      schedule:
        - cron:  '0 0 * * MON' # 定时任务 运行action
    # https://docs.github.com/cn/actions/learn-github-actions/workflow-syntax-for-github-actions
    

那么 `laowang`是怎么发出的呢？

    
    
    jobs:
    	laowang_fasong_tools:
        runs-on: ubuntu-latest
        steps:
          - 
            name: laowang fasong tools
            uses: peter-evans/repository-dispatch@v1
            with:
              token: ${{ secrets.TOKEN_GITHUB }} # github tocken
              repository: ${{ secrets.DOCKERHUB_USERNAME }}/Code-Server-Update # 发送到那个仓库呢？
              # 老王觉得自己的用户名是个密码，所以用 ${{ secrets.DOCKERHUB_USERNAME }} 代替
              event-type: laowang # 给上面这个仓库发送 laowang 信号
              client-payload: '{"ref": "${{ github.ref }}", "sha": "${{ github.sha }}"}'
    

### jobs

    
    
    jobs:
    	laowang_fasong_tools: # 任务的名称，建议使用下划线
        runs-on: ubuntu-latest
        steps: # 步骤
    

### steps

    
    
    jobs:
    	laowang_fasong_tools:
        runs-on: ubuntu-latest
        steps:
          - 
            name: Private Actions Checkout
            uses: actions/checkout@v2.3.4 # 这是 下载 当前仓库源码的 action 
          - 
            name: Docker Setup QEMU
            uses: docker/setup-qemu-action@v1.2.0 # 这是 qemu 模拟的 action 
          - 
            name: Docker Setup Buildx
            uses: docker/setup-buildx-action@v1.6.0 # 这是 docker buildx的 action 
          - 
            name: Docker Login
            uses: docker/login-action@v1.10.0 # 这是 docker 登录的 action 
            with:
              username: ${{ secrets.DOCKERHUB_USERNAME }}
              password: ${{ secrets.DOCKERHUB_TOKEN }}
          - 
            name: Build and push Docker images # 这是 docekr 部署的 action 
            uses: docker/build-push-action@v2.7.0
            with:
              context: .
              p[freebuff限制]latforms: linux/arm64,linux/amd64 # 这里选择你要编译的系统架构
              push: true
              tags: |
                ${{ secrets.DOCKERHUB_USERNAME }}/code-server:init # 这里设置镜像的名称，并推送到hub
              file: .github/workflows/Dockerfile.init # 这里手动选择 dockerfile
              cache-from: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/code-server:init.cache # 这里使用来自 hub 的缓存
              cache-to: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/code-server:init.cache,mode=max # 这里将缓存写入 hub
    

看了这么多，有点累了，上点才艺吧

![121911634978915_.pic_hd.jpg](https://image.3001.net/images/20211023/1634980591_6173d2efc501c825bfce9.jpg!small)

