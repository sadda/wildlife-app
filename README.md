# Installation

We provide two ways of installation. Both are for Windows only. In case you need to use the app under different operating system, [contact us](mailto:wilddatasets@gmail.com). The first one is simpler, but has a significantly higher requirements for internet bandwith.

## Installation 1

- Download the [zip file](https://1drv.ms/u/c/8621a316a2cb40fa/IQBqMmLdqfzsRqTgyCWCzIHVAd969AvuAbk2FRJtETXhqHU?e=b37zRi).
- Extract the downloaded zip file.
- Go to the `config` inside the extracted folder and rename your project config file (such as `turtles_of_smsrc.json`) into `config.json`.

## Installation 2

- Download [Python](https://www.python.org/ftp/python/3.14.2/python-3.14.2-amd64.exe), [Git](https://git-scm.com/install/windows) and [VS Code](https://code.visualstudio.com/download) and install them.
- Run VS Code. All the remaining commands are to be performed in VS Code.
- Open command palette ("View -> Command Palette"), type "Git: Clone" and add URL
  ```
  https://github.com/sadda/wildlife-app
  ```
  This will download the app.
- The directory with the app should open automatically. If not, open it manually ("File -> Open Folder" and select where you downloaded it in the previous step).
- Open terminal ("View -> Terminal" or keyboard shortcut Ctrl+`) - a text window where commands are typed. Run in terminal (type or paste it into terminal and press enter)
  ```
  python -m venv venv
  ```
- Run in terminal
  ```
  venv/scripts/activate
  ```
  The line in the terminal should now start with `(venv)`.
- Run in terminal
  ```
  pip install -r requirements.txt
  ```
  This will start installing the required Python packages. This operation should finish with a text saying that many packages were installed.


# Running the app

Run the app by

```
python run.py turtles_of_smsrc
```

It will start downloading the dataset, which may take half an hour. Using the app is easy (use keyboard shortcuts). The answers are saved into the file `answers.csv`.