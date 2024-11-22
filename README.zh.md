# BJTU ♥ MSTODO

从智慧课程平台拉取作业，并添加到你的Microsoft ToDo的待办清单中。

## 用法

1. 克隆仓库
    ```sh
    git clone https://github.com/ram6ert/bjtuhw_mstodo.git
    cd bjtuhw_mstodo
    ```

2. 安装依赖
    ```sh
    pip3 install -r ./requirements.txt
    ```

3. 运行程序  
    类UNIX：  
    ```sh
    STUDENT_ID=<Your Student ID> python3 ./main.py
    ```

    Windows用户可以这么做：
    ```cmd
    SET STUDENT_ID=<Your Student ID>
    python3 ./main.py
    ```


    之后，跟随输出的指示，登录你的微软账号。  
    指示信息大概长这样：  

    ```
    Login at <网址> with <代码>.
    ```

    打开网址，输入代码，登录你的微软账号。然后就可以看到我们的应用程序正在向你请求权限。阅读程序请求的权限清单，待你觉得程序没问题后点击接受并继续，登录就成功了。  

4. 保存凭据  
    待程序拉取完所有的作业后，它会在你的To-Do里创建一个代办清单，名为“BJTU Homework”，里面有你全部的作业，而且包含截止日期和内容。你可以自由更改清单的标题。不过，那些可以等会再做，我们现在要保存我们的凭据，不然你下次还要再登录。  

    你会看到一个类似这样的程序输出：  
    ```env
    LAST_RUN=1732014330
    LATEST_HW=1732011223
    TOKEN=...
    STUDENT_ID=23114514
    TASKLIST_ID=...
    ```

    你要把这些储存到一个文件里。这里的内容包括你的学号和微软账号凭据，所以你应当对其进行妥善保管。  

    假设你将上述内容储存到了“my-hw.txt”，下次你希望更新你的作业清单时，你需要按文件内容逐行设置你的环境变量再运行程序。如果你在使用类UNIX操作系统，你可以执行这条命令，一次搞定：`env $(cat my-hw.txt | xargs) python3 ./main.py`。Windows用户可以针对文件里的每一行，运行`SET <行>`，然后再运行`python3 ./main.py`。  

    这个程序也可以自动将这些数据保存到文件，你只需要设置`OUTFILE`环境变量。不过这个环境变量不会被输出到控制台或者保存到文件，你每次都需要手动设置`OUTFILE`。

    如果你在用systemd service，那么这些工作可以得到极大简化，以下是我的service文件：  
    ```systemd-service
    [Service]
    User=mstodo
    Type=oneshot
    ExecStart=/usr/bin/python3 -u /home/mstodo/main.py
    EnvironmentFile=/home/mstodo/users/%I
    Environment=OUTFILE=/home/mstodo/users/%I
    ```
    你还可以创建个systemd timer与它协同工作。
