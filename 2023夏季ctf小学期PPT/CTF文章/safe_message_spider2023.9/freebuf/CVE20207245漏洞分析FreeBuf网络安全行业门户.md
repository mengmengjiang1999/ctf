## 简介

该漏洞是一个CTFd的账户接管漏洞，在注册和修改密码处，存在逻辑漏洞，从而导致可以修改任意账号密码。

影响版本：v2.0.0-2.2.2

## 漏洞分析

首先定位到用户注册处：/CTFd/auto.py

    
    
    @auth.route("/register", methods=["POST", "GET"])  
    @check_registration_visibility  
    @ratelimit(method="POST", limit=10, interval=5)  
    def register():  
    errors = get_errors()  
    if request.method == "POST":  
    name = request.form["name"]  
    email_address = request.form["email"]  
    password = request.form["password"]  
    ​  
    name_len = len(name) == 0  
    names = Users.query.add_columns("name", "id").filter_by(name=name).first()  
    emails = (  
    Users.query.add_columns("email", "id")  
    .filter_by(email=email_address)  
    .first()  
    )  
    pass_short = len(password.strip()) == 0  
    pass_long = len(password) > 128  
    valid_email = validators.validate_email(request.form["email"])  
    team_name_email_check = validators.validate_email(name)  
    ​  
    if not valid_email:  
    errors.append("Please enter a valid email address")  
    if email.check_email_is_whitelisted(email_address) is False:  
    errors.append(  
    "Only email addresses under {domains} may register".format(  
    domains=get_config("domain_whitelist")  
    )  
    )  
    if names:  
    errors.append("That user name is already taken")  
    if team_name_email_check is True:  
    errors.append("Your user name cannot be an email address")  
    if emails:  
    errors.append("That email has already been used")  
    if pass_short:  
    errors.append("Pick a longer password")  
    if pass_long:  
    errors.append("Pick a shorter password")  
    if name_len:  
    errors.append("Pick a longer user name")  
    ​  
    if len(errors) > 0:  
    return render_template(  
    "register.html",  
    errors=errors,  
    name=request.form["name"],  
    email=request.form["email"],  
    password=request.form["password"],  
    )  
    else:  
    with app.app_context():  
    user = Users(  
    name=name.strip(),  
    email=email_address.lower(),  
    password=password.strip(),  
    )  
    db.session.add(user)  
    db.session.commit()  
    db.session.flush()  
    ​  
    login_user(user)  
    ​  
    if config.can_send_mail() and get_config(  
    "verify_emails"  
    ):  # Confirming users is enabled and we can send email.  
    log(  
    "registrations",  
    format="[{date}] {ip} - {name} registered (UNCONFIRMED) with {email}",  
    )  
    email.verify_email_address(user.email)  
    db.session.close()  
    return redirect(url_for("auth.confirm"))  
    else:  # Don't care about confirming users  
    if (  
    config.can_send_mail()  
    ):  # We want to notify the user that they have registered.  
    email.sendmail(  
    request.form["email"],  
    "You've successfully registered for {}".format(  
    get_config("ctf_name")  
    ),  
    )  
    ​  
    log("registrations", "[{date}] {ip} - {name} registered with {email}")  
    db.session.close()  
    ​  
    if is_teams_mode():  
    return redirect(url_for("teams.private"))  
    ​  
    return redirect(url_for("challenges.listing"))  
    else:  
    return render_template("register.html", errors=errors)

上述代码，有一大半是进行输入检测的，提取出来关键部分：

    
    
    def register():  
    errors = get_errors()  
    if request.method == "POST":  
    name = request.form["name"]  
    email_address = request.form["email"]  
    password = request.form["password"]  
    ​  
    name_len = len(name) == 0  
    names = Users.query.add_columns("name", "id").filter_by(name=name).first()  
    emails = (  
    Users.query.add_columns("email", "id")  
    .filter_by(email=email_address)  
    .first()  
    )  
    pass_short = len(password.strip()) == 0  
    pass_long = len(password) > 128  
    valid_email = validators.validate_email(request.form["email"])  
    team_name_email_check = validators.validate_email(name)  
      
    if len(errors) > 0:         #检测出错  
      
    '''注册账户密码插入数据库'''  
    else:                     
    with app.app_context():  
    user = Users(  
    name=name.strip(),  
    email=email_address.lower(),  
    password=password.strip(),  
    )  
    db.session.add(user)  
    db.session.commit()  
    db.session.flush()  
    ​  
    login_user(user)  
    ​  
    if config.can_send_mail() and get_config(  
    "verify_emails"  
    ):  # Confirming users is enabled and we can send email.  
    log(  
    "registrations",  
    format="[{date}] {ip} - {name} registered (UNCONFIRMED) with {email}",  
    )  
    email.verify_email_address(user.email)  
    db.session.close()  
    return redirect(url_for("auth.confirm"))

上方的上半部分，接受用户的输入信息：

    
    
    def register():  
    errors = get_errors()  
    if request.method == "POST":  
    name = request.form["name"]  
    email_address = request.form["email"]  
    password = request.form["password"]  
    ​  
    name_len = len(name) == 0  
    names = Users.query.add_columns("name", "id").filter_by(name=name).first()  
    emails = (  
    Users.query.add_columns("email", "id")  
    .filter_by(email=email_address)  
    .first()  
    )  
    pass_short = len(password.strip()) == 0  
    pass_long = len(password) > 128  
    valid_email = validators.validate_email(request.form["email"])  
    team_name_email_check = validators.validate_email(name)

其关键在于这里：

    
    
    names = Users.query.add_columns("name", "id").filter_by(name=name).first()

在判断用户是否已经注册时，是直接用的name，也就是用户输入的账户名，并且没有任何的过滤。

在下半部分，注册成功时，将账户、密码、邮箱插入到数据库中：

    
    
    with app.app_context():  
    user = Users(  
    name=name.strip(),  
    email=email_address.lower(),  
    password=password.strip(),  
    )  
    db.session.add(user)  
    db.session.commit()  
    db.session.flush()

但是这里又对用户输入的账户进行了去除空格的操作。（也就是说，如果数据库中存在m1sn0w这个账户，但是，如果我在注册时输入的账户名为：空格m1sn0w，那么，注册时不会提示账户已存在，而是将m1sn0w这个用户名插入到数据库中，也就是数据库中有了同名用户）

接下来是第二个利用点（修改密码）：提取出主要代码

    
    
    @auth.route("/reset_password", methods=["POST", "GET"])  
    @auth.route("/reset_password/<data>", methods=["POST", "GET"])  
    @ratelimit(method="POST", limit=10, interval=60)  
    def reset_password(data=None):  
    if data is not None:  
    try:  
    name = unserialize(data, max_age=1800)  
    except (BadTimeSignature, SignatureExpired):  
    return render_template(  
    "reset_password.html", errors=["Your link has expired"]  
    )  
    except (BadSignature, TypeError, base64.binascii.Error):  
    return render_template(  
    "reset_password.html", errors=["Your reset token is invalid"]  
    )  
    ​  
    if request.method == "GET":  
    return render_template("reset_password.html", mode="set")  
    if request.method == "POST":  
    user = Users.query.filter_by(name=name).first_or_404()  
    user.password = request.form["password"].strip()  
    db.session.commit()  
    log(  
    "logins",  
    format="[{date}] {ip} -  successful password reset for {name}",  
    name=name,  
    )  
    db.session.close()  
    return redirect(url_for("auth.login"))

我们知道，在修改密码时，会向相应的邮箱发送一封邮件，点击之后，才能修改密码。（上面的data值，也就是发送给指定邮箱的URL后面的一串值）

接下来，看看data值是什么：/CTFd/utils/email/__init__.py

    
    
    def forgot_password(email, team_name):  
    token = serialize(team_name)  
    text = """Did you initiate a password reset? Click the following link to reset your password:  
    ​  
    {0}/{1}  
    ​  
    """.format(  
    url_for("auth.reset_password", _external=True), token  
    )  
    ​  
    return sendmail(email, text)

可以看到，它是将用户名序列化之后，拼接到相应URL后面，发送给邮箱。（通过前面的分析，我们知道数据库中的账号有两个是同名，那么进行修改密码操作时，就会修改第一个用户的密码）

（有些文章说需要修改当前用户为其他的用户名，但感觉好像不需要）

    
    
    if request.method == "POST":  
    user = Users.query.filter_by(name=name).first_or_404()  
    user.password = request.form["password"].strip()  
    db.session.commit()

它这里取出来的用户就是第一个用户（也就是先前注册的那个用户）

所以，大致的利用方法如下：

1、注册一个账号，和想要修改的那个用户名同名，但在注册时加上空格

2、点击修改密码，在邮箱确认，即可修改指定用户密码

