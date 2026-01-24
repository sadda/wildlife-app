# Image Comparator

This repo provides an app for validating whether two images depict the same individual. It is part of a large, mostly automated pipeline that takes photos of one animal species as input and outputs photos showing the same individuals.

<img src="https://github.com/sadda/wildlife-app/raw/master/docs/resources/app.png" alt="App photo" width="500">

## Installation

We provide two ways of installation. Both are for Windows only. If you need to use the app on a different operating system, [contact us](mailto:wilddatasets@gmail.com). The first one is simpler but requires significantly more internet bandwidth.

### Installation 1

- Download the [zip file](https://1drv.ms/u/c/8621a316a2cb40fa/IQBqMmLdqfzsRqTgyCWCzIHVAd969AvuAbk2FRJtETXhqHU?e=b37zRi).
- Extract the downloaded zip file.
- Go to the `config` folder inside the extracted folder and rename your project config file (such as `turtles_of_smsrc.json`) into `config.json`.

### Installation 2

- Download [Python](https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe), [Git](https://git-scm.com/install/windows) and [VS Code](https://code.visualstudio.com/download) and install them.
- Run VS Code. All the remaining commands are to be performed in VS Code.
- Open command palette ("View -> Command Palette"), type "Git: Clone" and add URL
  ```
  https://github.com/sadda/wildlife-app
  ```
  This will download the app.
- The directory with the app should open automatically. If not, open it manually ("File -> Open Folder" and select where you downloaded it in the previous step).
- Open terminal ("View -> Terminal" or keyboard shortcut Ctrl+`) - a text window where commands are typed. All commands below must be run in the same terminal window. Run in terminal (type or paste it into the terminal and press enter)
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
  This will start installing the required Python packages. This operation should end with a message indicating that many packages were installed.

## Updating the app

For Installation 1, the whole process must be repeated. For Installation 2, it is sufficient to click the "Synchronise Changes" in VS Code (two arrows forming a circle in the bottom-left part).

## Running the app

For Installation 1, run the exe file. For Installation 2, open the terminal (see above) and run the following two commands:
```
venv/scripts/activate
python run.py turtles_of_smsrc
```
If you run a different project than TurtlesOfSMSRC, you need to change the last keyword.

When the app starts for the first time, it will begin downloading the dataset, which may take half an hour.

## Using the app

Using the app should be straightforward. Press Same (Q), Different (W) or Unknown (E) for validating whether the two shown turtles are the same. Use Next (A) and Previous (S) to move to the following images without giving an answer or to check the previous answer. You can also move to the next body part if the matching was performed across multiple body parts. It is highly recommended to use the keyboard shortcuts Q, W, E, A and S. The answers are saved to the file `answers.csv`.

When a dataset is updated, it should be downloaded by the corresponding button. Similarly, when new predictions are available for verification, they can be automatically downloaded. The last button downloads segmentation masks, which are used to crop turtle heads and flippers.