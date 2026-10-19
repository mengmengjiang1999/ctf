​ **作者：京东零售 秦浩然**

# 一、什么是异常

Java 语言按照错误严重性，从 throwale 根类衍生出 Error 和 Exception 两大派系。

 **Error（错误）：**

程序在执行过程中所遇到的硬件或操作系统的错误。错误对程序而言是致命的，将导致程序无法运行。常见的错误有内存溢出，jvm 虚拟机自身的非正常运行，calss
文件没有主方法。程序本生是不能处理错误的，只能依靠外界干预。Error 是系统内部的错误，由 jvm 抛出，交给系统来处理。

 **Exception（异常）：**

程序正常运行中，可以预料的意外情况。比如数据库连接中断，空指针，数组下标越界。异常出现可以导致程序非正常终止，也可以预先检测，被捕获处理掉，使程序继续运行。Exception（异常）按照性质，又分为编译异常（受检异常）和运行时异常（非受检异常）。

◦ 编译异常：

又叫可检查异常，通常时由语法错和环境因素（外部资源）造成的异常。比如输入输出异常 IOException，数据库操作
SQLException。其特点是，Java 语言强制要求捕获和处理所有非运行时异常。通过行为规范，强化程序的健壮性和安全性。

◦ 运行时异常：

又叫不检查异常 RuntimeException，这些异常一般是由程序逻辑错误引起的，即语义错。比如算术异常，空指针异常
NullPointerException，下标越界
IndexOutOfBoundsException。运行时异常应该在程序测试期间被暴露出来，由程序员去调试，而避免捕获。

# 二、处理异常方式

代码中，我们最常见到的处理异常的方式就是：try-catch

    
    
    try {
                // 业务逻辑
                
            } catch (Exception e) {
                // 捕获到异常的逻辑
            }
    

或者是再进一步区分下异常类型：

    
    
    try {
                // 业务逻辑
                
            } catch (IOException ie) {
                // 捕获到IO异常的逻辑
                
            } catch (Exception e) {
                // 捕获到其他异常的逻辑
            }
    

# 三、如何抛出异常

我们通常可以用抛出异常的方式来控制代码流程，然后在网关处统一catch异常来返回错误code。这在一定程度上可以简化代码流程控制，如下所示：

    
    
    @Override
        public UserVO queryUser(Long id) {
            UserDO userDO = userMapper.queryUserById(id);
            if (Objects.isNull(userDO)) {
                throw new RuntimeException("用户不存在");    //用户不存在抛出异常
            }
            return userDO.toVo();
        }  
    

上面这种抛出异常的方式，虽然简化了代码流程，但是在存在多种错误场景时，没有办法细分具体的错误类型。如：用户不存在的错误、用户没有权限的错误；

聪明如你，一定想到了自定义异常，如下：

    
    
    @Override
        public UserVO queryUser(Long id) {
            UserDO userDO = userMapper.queryUserById(id);
            if (Objects.isNull(userDO)) {
                throw new UserNotFoundException();    //用户不存在抛出对应异常
            }
            if(!checkLicence(userDO)) {
                throw new BadLicenceException();    //用户无权限抛出对应异常
            }
            return userDO.toVo();
        }
    

确实，自定义异常可以解决错误场景细分的问题。进一步的，我们可以对系统流程不同阶段、不同业务类型分别自定义异常，但这需要自定义大量的异常；

# 四、如何优雅的抛出异常

上面的方式，可以区分出错误场景了，但是还存在一些缺点。如：可读性差、需要定义大量的自定义异常；

那我们下面就去优化上面的问题；

 **用断言增加代码的可读性；**

    
    
    @Override
        public UserVO queryUser(Long id) {
            UserDO userDO = userMapper.queryUserById(id);
            Assert.notNull(userDO, "用户不存在");    //用断言进行参数的非空校验
            return userDO.toVo();
        }
    

断言虽然代码简洁、可读性好，但是缺乏像上述自定义异常一样可以明确区分错误场景，这就引出我们的究极方案：自定义断言；

 **自定义断言；**

我们用自定义断言的方式，综合上面自定义异常和断言的优点，在断言失败后，抛出我们制定好的异常。代码如下：

• 自定义异常基本类

    
    
    @Getter
    @Setter
    public class BaseException extends RuntimeException {
    
        // 响应码
        private IResponseEnum responseEnum;
    
        // 参数信息
        private Object[] objs;
    
        public BaseException(String message, IResponseEnum responseEnum, Object[] objs) {
            super(message);
            this.responseEnum = responseEnum;
            this.objs = objs;
        }
    
        public BaseException(String message, Throwable cause, IResponseEnum responseEnum, Object[] objs) {
            super(message, cause);
            this.responseEnum = responseEnum;
            this.objs = objs;
        }
    }
    

• 自定义断言接口

    
    
    public interface MyAssert {
    
        /**
         * 创建自定义异常
         *
         * @param objs 参数信息
         * @return 自定义异常
         */
        BaseException newException(Object... objs);
    
        /**
         * 创建自定义异常
         *
         * @param msg  描述信息
         * @param objs 参数信息
         * @return 自定义异常
         */
        BaseException newException(String msg, Object... objs);
    
        /**
         * 创建自定义异常
         *
         * @param t    接收验证异常
         * @param msg  描述信息
         * @param objs 参数信息
         * @return 自定义异常
         */
        BaseException newException(Throwable t, String msg, Object... objs);
    
    
        /**
         * 校验非空
         *
         * @param obj 被验证对象
         */
        default void assertNotNull(Object obj, Object... objs) {
            if (obj == null) {
                throw newException(objs);
            }
        }
    
        /**
         * 校验非空
         *
         * @param obj 被验证对象
         */
        default void assertNotNull(Object obj, String msg, Object... objs) {
            if (obj == null) {
                throw newException(msg, objs);
            }
        }
    }
    

上述代码我们可以看出基本设计，就是在我们自定义断言失败后抛出我们自定义异常。

下面是具体的实现案例：

• 自定义业务异常类，继承自异常基本类

    
    
    public class BusinessException extends BaseException {
    
        public BusinessException(IResponseEnum responseEnum, Object[] args, String msg) {
            super(msg, responseEnum, args);
        }
    
        public BusinessException(IResponseEnum responseEnum, Object[] args, String msg, Throwable t) {
            super(msg, t, responseEnum, args);
        }
    
    }
    

• 响应code枚举接口定义

    
    
    public interface IResponseEnum {
    
        /**
         * 返回code码
         *
         * @return code码
         */
        String getCode();
    
        /**
         * 返回描述信息
         *
         * @return 描述信息
         */
        String getMsg();
    }
    

• 自定义业务异常类断言定义，实现自定义断言失败后对应的自定义异常的定义；

    
    
    public interface BusinessExceptionAssert extends IResponseEnum, MyAssert {
    
        @Override
        default BaseException newException(Object... args) {
            return new BusinessException(this, args, this.getMsg());    //断言失败后，抛出自定义异常
        }
    
        @Override
        default BaseException newException(String msg, Object... args) {
            return new BusinessException(this, args, msg);              //断言失败后，抛出自定义异常
        }
    
        @Override
        default BaseException newException(Throwable t, String msg, Object... args) {
            return new BusinessException(this, args, msg, t);           //断言失败后，抛出自定义异常
        }
    }
    

• 用枚举的方式，代替BadLicenceException、UserNotFoundException自定义异常。

    
    
    public enum ResponseEnum implements IResponseEnum, BusinessExceptionAssert {
    
        BAD_LICENCE("0001", "无权访问"),
    
        USER_NOT_FOUND("1001", "用户不存在"),
        ;
    
        private final String code, msg;
    
        ResponseEnum(String code, String msg) {
            this.code = code;
            this.msg = msg;
        }
    
        @Override
        public String getCode() {
            return code;
        }
    
        @Override
        public String getMsg() {
            return msg;
        }
    }
    

**使用实例**

自定义断言失败抛出自定义异常

    
    
    @Override
        public UserVO queryUser(Long id) {
            UserDO userDO = userMapper.queryUserById(id);
            ResponseEnum.USER_NOT_FOUND.assertNotNull(userDO);    //自定义断言失败抛出自定义异常
            return userDO.toVo();
        }
    

网关处统一catch异常，识别异常场景

    
    
    public static void main(String[] args) {
            UserService userService = new UserServiceImpl(new UserMapperImpl());
            UserController userController = new UserController(userService);
            try {
                UserVO vo = userController.queryUser(2L);               //执行业务逻辑
            } catch (BusinessException e) {
                System.out.println(e.getResponseEnum().getCode());      //出现异常，错误code：1001
                System.out.println(e.getMessage());                     //出现异常，错误msg：用户不存在
            }
        }
    

# 五、如何优雅的处理异常

网关处统一处理异常，这属于常规操作，这里不再赘述，简单举例如下：

    
    
    @ControllerAdvice
    public class BusinessExceptionHandler {
        
        @ExceptionHandler(value = BusinessException.class)
        @ResponseBody
        public Response handBusinessException(BaseException e) {
            return new Response(e.getResponseEnum().getCode(), e.getResponseEnum().getMsg());    //统一处理异常
        }
    }
    

综上，我们采用自定义断言的方式，结合了断言的可读性高的优势和自定义异常区分错误场景的优势。并且，有新增的错误场景，我们只需要在错误码枚举中新增对应枚举即可。

​

