**今天给大家推荐的这款工具名叫CANalyzat0r，各位研究人员可以利用该工具对专用汽车协议进行安全分析。**

![](https://image.3001.net/images/20190226/1551181583_5c75270f88b68.png!small)

## CANalyzat0r的优势在哪？

1、 引入了新的安全分析机制；

2、 整合了多款安全工具的强大功能；

3、 模块化与可扩展性：可读取doc文件，可实现自己的分析机制；

4、 提供了有好的GUI界面；

5、 可使用数据库单独管理不同的项目；

6、 文档化：如果需要操作手册或技术支持信息，可查看doc文档；

## 工具安装与运行

1、 运行下列两条命令，将自动在当前路径下创建一个名为“pipenv”的文件夹（已配置好pipenv环境）：

    
    
    sudo ./install_requirements.sh
    
    sudo -E ./CANalyzat0r.sh

2、 或直接使用Docker版本（推荐使用），具体请查看子目录下的README.md文件。

注：如需获取更多详细信息，请直接阅读./doc/build目录下的HTML/PDF工具文档。

## 功能介绍

1、 管理接口配置（自动加载内核模块，管理物理/虚拟SocketCAN设备）；

2、 多接口支持；

3、 在项目中管理任务，你还能够以可读/可编辑的JSON模式导入或导出项目信息；

4、 记录所有的分析操作；

5、 图形化的嗅探过程/结果；

6、 管理分析结果，导出数据包；

![](https://image.3001.net/images/20190226/1551182188_5c75296c0d1d5.png!small)

7、 不同标签之间进行数据复制/粘贴，还可以直接将SocketCAN文件拷贝到表中；

![](https://image.3001.net/images/20190226/1551181779_5c7527d389291.gif!small)

8、 线程发送、模糊测试喝嗅探；

![](https://image.3001.net/images/20190226/1551181884_5c75283ccc992.gif!small)

9、 在GUI中添加多个分析线程；

10、根据ID或数据自动化过滤数据包；

11、导出数据对比；

12、允许在单一窗口中设置复杂配置；

13、随机化代码数据包过滤；

14、使用背景噪音过滤来搜索特定数据包；

![](https://image.3001.net/images/20190226/1551182109_5c75291dc5a47.png!small)

15、SQLite支持；

16、实施修改数据值；

## 分析测试

你可以使用这款ICSim模拟器【[下载地址](https://github.com/zombieCraig/ICSim)】来模拟一台“真实”的汽车，并利用该工具来对其进行测试，这样你就不需要用真实的汽车来测试了。

## 项目地址

CANalyzat0r：【[GitHub传送门](https://github.com/schutzwerk/CANalyzat0r)】

## 许可证协议

本项目遵循[GPLv3](https://www.gnu.org/licenses/gpl.txt)许可证协议。

 ***
参考来源：[CANalyzat0r](https://github.com/schutzwerk/CANalyzat0r)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

