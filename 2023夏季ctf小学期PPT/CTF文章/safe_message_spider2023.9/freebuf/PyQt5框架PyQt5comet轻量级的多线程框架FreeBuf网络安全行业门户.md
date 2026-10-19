## **简介**

PyQt5-comet是一款轻量级的多线程框架。它通过使用pyqtSlot+QMutex+QThread+pyqtSignal+importlib，实现以模块化形式加载提高GUI程序开发速度。优势在于能够帮助研发人员将更多精力放在程序逻辑与回调函数，从而使得GUI在功能上更为强大。

## 框架模块

下面为框架的目录结构以及模块功能描述：

    
    
    -PyLib
        Controller.py               控制器文件
        MainUi.py                 GUI设计界面文件
        Module-Test.py               功能模块文件
        ProgramManagement.py              GUI多线程启动文件
        MainUi.ui                 GUI设计界面.ui文件
    main.py                                          启动文件

### 安装教程

首先需要安装PyQt5和PyQt5-tools，使用命令如下：

    
    
    pip install pyqt5 -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install pyqt5-tools -i https://pypi.tuna.tsinghua.edu.cn/simple

然后将PyQt5-comet模块下载，如下：

    
    
    pip install -i https://test.pypi.org/simple/ PyQt5-comet --prefix="我的项目路径"
    or
    pip install PyQt5-comet --prefix="我的项目路径"

最后将Lib\site-packages\PyLib目录和Lib\site-packages\main.py文件复制到项目根目录即可。

### 开发教程

Module-Test.py 为自定义模块，可以使用其处理GUI子模块的逻辑。

固定class RunModule和def update用于加载器的调用，剩下逻辑需要按照研发需求设计。

    
    
    import _thread
    import os
    
    
    class RunModule:
        def __init__(self, tmp_dict):
            self.log = tmp_dict.get("log")
            pass
    
    
        def _log(self,threadName):
            print(os.getpid())
            print(self.log)
            print(threadName)
    
    
        def run(self):
            _thread.start_new_thread(self._log,("Thread-1",))
    
    
        def update(self):
            self.run()
            return self.log

在控制器中加载，name="Module-Test" 是需要加载的模块名称，log="1111111111111111" 是传递的参数。

connect(self._lookTestsLog)是回调函数。

注：函数调用规范 on_组件名称_组件动作() 定义后就可以通过装饰器调用任意组件和动作。

    
    
    from PyQt5.QtCore import pyqtSlot, QModelIndex, QMutex
    from PyQt5.QtWidgets import QMainWindow
    from PyLib.MainUi import Ui_Dialog
    from PyLib.ProgramManagement import runCmd
    
    
    
    class MainWin(QMainWindow, Ui_Dialog):
        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.q = QMutex()
    
    
        #@pyqtSlot(QModelIndex)
        @pyqtSlot()
        def on_pushButton_clicked(self):
            self.q.lock()
            self.runCmd_ = runCmd(name="Module-Test", log="1111111111111111")
            self.runCmd_.cmdsign.connect(self._lookTestsLog)
            self.runCmd_.start()
            self.runCmd_.wait()
            self.q.unlock()
    
    
        def _lookTestsLog(self, log):
            self.label.setText(log)

运行时，需要启动main.py。

## PyQt5-comet项目地址

    
    
    https://pypi.org/project/PyQt5-comet/
    https://github.com/SkyBlueEternal/PyQt5-comet

