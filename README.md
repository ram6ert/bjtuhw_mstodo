# BJTU ♥ MSTODO

Fetch a list of homework from "智慧课程平台" and add them to your microsoft to-do checklist.

## Usage


1. Clone the repository  
    ```sh
    git clone https://github.com/ram6ert/bjtuhw_mstodo
    cd bjtuhw_mstodo
    ```

2. Install the dependencies
    ```sh
    pip3 install -r ./requirements.txt
    ```

3. Run the program  
    UNIX-like:  
    ```sh
    STUDENT_ID=<Your Student ID> python3 ./main.py
    ```

    Windows users can do these by:  
    ```cmd
    SET STUDENT_ID=<Your Student ID>
    python3 ./main.py
    ```

    And then, follow the instructions to log your microsoft account in.  
    You will get a message like:

    ```
    Login at <url> with <code>.
    ```

    Open the url, enter the code, logging your microsoft account in, and read the permissions the application asks for.  
    Once you think it's all okay to grant the permission, click the accept button and the login will be successful.

4. Save the credentials  
    After the program has fetched all the homework, it will create a to-do list named "BJTU Homework" with all your homework in it while the deadlines and the contents of the homework are also noted. You can change the title of the list as you wish. But let's do that later. What we need to do now is to save your credentials, or you will have to log it in again during the next run.  

    You can see an output similar to the below:
    ```env
    LAST_RUN=1732014330
    LATEST_HW=1832011223
    TOKEN=...
    STUDENT_ID=23114514
    TASKLIST_ID=...
    ```

    You should save these to a file. Such output includes your student id and microsoft account credentials, so you should keep it well.  

    Let's assume that you have saved these to a file named "my-hw.txt". The next time you want to update your homework list, you need to set environment variables by each line of item of "my-hw.txt" before you run the program. With UNIX-like system, you can do these by a command `env $(cat my-hw.txt | xargs) python3 ./main.py`. Windows users should do these by `SET <line>` for each line and finally `python3 ./main.py`.

    This program can also save your credentials to a file automatically by setting an environment variable `OUTFILE`. However, such variable will not be printed to neither the console nor the *outfile*. You should set `OUTFILE` every time you run this program.  

    By using systemd service, all of these can be simplified. Here is my service file:  
    ```systemd-service
    [Service]
    User=mstodo
    Type=oneshot
    ExecStart=/usr/bin/python3 -u /home/mstodo/main.py
    EnvironmentFile=/home/mstodo/users/%I
    Environment=OUTFILE=/home/mstodo/users/%I
    ```
    You can create a systemd timer to work with this.
