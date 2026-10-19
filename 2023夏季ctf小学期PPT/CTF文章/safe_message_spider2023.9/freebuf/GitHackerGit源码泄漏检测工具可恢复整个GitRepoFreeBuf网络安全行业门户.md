**GitHacker是一个多线程工具，用于检测站点是否存在git源码泄漏，并能够将网站源代码下载到本地。值得一提的是，这个工具会将整个git
repo恢复到本地，而不是像[githack]那样，只是简单的恢复到最新版本。如此一来，你就可以查看到开发人员的历史提交记录以及提交注释，以更好的掌握开发者的性格和心理，从而为进一步的代码审计奠定基础。**

##  **Git源码泄漏检测工具对比**

##
![68747470733a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f323335353037372d363462646531626366363137653063662e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f737472
\(1\).png](https://image.3001.net/images/20190515/1557872797_5cdb409d93784.png!small)
演示视频

## 环境要求

    
    
    git >= 2.11.0
    python-requests
    Linux envrionment

## 安装

    
    
    # Install requests
    pip install requests
    # Download source
    # Notice: NO NOT DOWNLOAD ZIP FROM GITHUB
    git clone https://github.com/wangyihang/GitHacker.git

## 使用

    
    
    Usage :
            python GitHacker.py [Website]
    Example :
            python Githack.py http://127.0.0.1/.git/
    Author :
            wangyihang <wangyihanger@gmail.com>

## 示例

    
    
    python GitHacker.py http://127.0.0.1/.git/

## 未来计划

> 启用索引时下载标记和分支
>
> 禁用索引时尝试使用通用标记和分支
>
> 找到 [packed
> refs](https://github.com/WangYihang/GitHacker/issues/1#issuecomment-487135667)

## 视频演示

<https://asciinema.org/a/xgRmZ9dNvzhe3T2XRYDJe15Rj>（可复制代码）

 **
*参考来源：[GitHub](https://github.com/WangYihang/GitHacker)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

