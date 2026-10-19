![](https://image.3001.net/images/20200518/1589816397_5ec2ac4d0a553.jpg!small)

## Threadtear

**Threadtear是一款针对Java代码的多功能反混淆工具，该工具即将添加针对Android应用程序的支持。在该工具的帮助下，广大研究人员无需过多担心代码混淆方面的问题，因为Threadtear可以为你的代码分析过程添砖加瓦。即使是ZKM和Stringer之类的混淆工具，对于Threadtear来说也不在话下。为了方便进行代码调试，Threadtear还集成了很多其他的功能，并且还提供了代码行标注以及其他的代码栈追踪功能。值得一提的是，Threadtear还支持逆向分析功能。**

### 任务执行

一次“任务执行”指的是对所有已加载的类文件进行执行和修改操作，执行任务有很多种类型，从字节码清理到字符串反混淆，但所有的任务都需要确保文件以正确的顺序加载和执行。一切准备就绪之后，点击“Run”按钮即可按顺序对目标文件进行操作。

### 安全

Threadtear会使用自己的SecurityManager类来尽可能地帮助研究人员免受恶意调用（任意代码执行）的影响，但无法100%保证安全。尤其是在处理类似ZKM或Stringer这样的混淆目标时，反射是经常会出现的。

## 如何编译

首先，运行下列命令，然后在builds/libs中会创建一个可运行的jar文件。

    
    
    gradle build
    
    gradle fatJar

如果你不想下载项目源码的话，你还可以直接使用该项目Release页面提供的最新版本：【[
_点我获取_](https://github.com/GraxCode/threadtear/releases)】。

## 工具使用

我们可以直接通过扩展me.nov.threadtear.execution.Execution方法来创建自己的执行任务：

    
    
    public class MyExecution extends Execution {
    
    	public MyExecution() {
    
    		super(ExecutionCategory.CLEANING /* category */, "My execution" /* name */,
    
    				"Executes something" /* description, can use html */);
    
    	}
    
    	/**
    
    	* This method is invoked when the user clicks on the Run button
    
    	* @return true if success, false if failure
    
    	*/
    
    	@Override
    
    	public boolean execute(Map<String, Clazz> classes, boolean verbose) {
    
    		classes.values().stream().map(c -> c.node).forEach(c -> {
    
    			//transform the classes here using the tree-API of ASM
    
    		});
    
    		return false;
    
    	}
    
    }

在运行时加载`ClassNodes`类，可以直接使用`me.nov.threadtear.asm.vm.VM`类并实现`me.nov.threadtear.asm.vm.IVMReferenceHandler`方法：

    
    
    public class MyExecution extends Execution implements IVMReferenceHandler {
    
    	public MyExecution() {
    
    		super(ExecutionCategory.GENERIC, "My execution", "Loads ClassNodes at runtime");
    
    	}
    
    	@Override
    
    	public boolean execute(Map<String, Clazz> classes, boolean verbose) {
    
    		classes.values().stream().map(c -> c.node).forEach(c -> {
    
    			VM vm = VM.constructVM(this);
    
    			//transform bytecode to java.lang.Class
    
    			Class<?> loadedClass = vm.loadClass(c.name.replace('/', '.'), true);
    
    			//do stuff with your class here
    
    			loadedClass.getMethods[0].invoke(...);
    
    			return true;
    
    		});
    
    	}
    
    	/**
    
    	* Will get invoked by VM, when VM.loadClass is called
    
    	*/
    
    	@Override
    
    	public ClassNode tryClassLoad(String name) {
    
    		//try to find the class to be loaded in open jar archive
    
    		return classes.containsKey(name) ? classes.get(name).node : null;
    
    	}
    
    }

通过使用`me.nov.threadtear.analysis.stack.ConstantTracker`方法，你可以分析目标代码中的方法并追踪非变量栈值：

    
    
    public class MyExecution extends Execution implements IConstantReferenceHandler {
    
    	public MyExecution() {
    
    		super(ExecutionCategory.GENERIC, "My execution", "Performs stack analysis and replaces code.");
    
    	}
    
    	@Override
    
    	public boolean execute(Map<String, Clazz> classes, boolean verbose) {
    
    		classes.values().stream().map(c -> c.node).forEach(this::analyzeAndRewrite);
    
    		return true;
    
    	}
    
    	public void analyzeAndRewrite(ClassNode cn) {
    
    		cn.methods.forEach(m -> {
    
    			// this analyzer keeps known stack values, e.g. can be useful for jump prediction
    
    			Analyzer<ConstantValue> a = new Analyzer<ConstantValue>(new ConstantTracker(this, Access.isStatic(m.access), m.maxLocals, m.desc, new Object[0]));
    
    			try {
    
    				a.analyze(cn.name, m);
    
    			} catch (AnalyzerException e) {
    
    				logger.severe("Failed stack analysis in " + cn.name + "." + m.name + ":" + e.getMessage());
    
    				return;
    
    			}
    
    			Frame<ConstantValue>[] frames = a.getFrames();
    
    			InsnList rewrittenCode = new InsnList();
    
    			Map<LabelNode, LabelNode> labels = Instructions.cloneLabels(m.instructions);
    
     
    
    			// rewrite method instructions
    
    			for (int i = 0; i < m.instructions.size(); i++) {
    
    				AbstractInsnNode ain = m.instructions.get(i);
    
    				Frame<ConstantValue> frame = frames[i];
    
    				// replace / modify instructions, etc...
    
    				if (frame.getStackSize() > 0) {
    
    					ConstantValue top = frame.getStack(frame.getStackSize() - 1);
    
    					if (top.isKnown() && top.isInteger()) {
    
    						int knownTopStackValue = top.getInteger();
    
    						// use the known stack to remove jumps, simplify code, etc...
    
    						// if(...) { rewrittenCode.add(...); }
    
    						continue;
    
    					}
    
    				}
    
    				rewrittenCode.add(ain.clone(labels));
    
    			}
    
    			// update instructions and fix try catch blocks, local variables, etc...
    
    			Instructions.updateInstructions(m, labels, rewrittenCode);
    
    		});
    
    	}
    
    	/**
    
    	 * Use this method to predict stack values if fields are loaded
    
    	 */
    
    	@Override
    
    	public Object getFieldValueOrNull(BasicValue v, String owner, String name, String desc) {
    
    		return null;
    
    	}
    
    	/**
    
    	 * Use this method to predict stack values if methods are invoked on known objects
    
    	 */
    
    	@Override
    
    	public Object getMethodReturnOrNull(BasicValue v, String owner, String name, String desc, List<? extends ConstantValue> values) {
    
    		if (name.equals("toCharArray") && owner.equals("java/lang/String")) {
    
    			if (!values.get(0).isKnown()) {
    
    				// invocation target is not known, we can't compute the return
    
    				return null;
    
    			}
    
    			return ((String) values.get(0).getValue()).toCharArray();
    
    		}
    
    		return null;
    
    	}
    
    }

### 反混淆顺序

最佳的反混淆处理顺序如下：

> 通用执行->访问反混淆代码->字符串反混淆->清理执行痕迹

## 工具运行截图

![](https://image.3001.net/images/20200518/1589816491_5ec2acabe0a28.png!small)

![](https://image.3001.net/images/20200518/1589816491_5ec2acabdc723.png!small)

![](https://image.3001.net/images/20200518/1589816491_5ec2acabf0225.png!small)

![](https://image.3001.net/images/20200518/1589816492_5ec2acace49e8.png!small)

![](https://image.3001.net/images/20200518/1589816492_5ec2acac5f0f2.png!small)

## 许可证协议

Threadtear项目的开发与发布遵循GNU GPL v3.0开源许可证协议。

## 项目地址

> Threadtear：【[ _GitHub传送门_](https://github.com/GraxCode/threadtear)】

 *** 参考来源：[
_GraxCode_](https://github.com/GraxCode/threadtear)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

