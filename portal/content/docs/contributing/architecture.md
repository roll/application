---
title: Architecture
sidebar:
  order: 2
---

In a nutshell, the Open Data Editor is a desktop application that:

- Reads tabular data (csv, excels, etc).
- Execute some analysis to find errors in the data.
- Displays a report with errors in the data (if any!).
- If desired, publish the data file and metadata somewhere (Github, Zenodo, CKAN, etc).

And that's it! That's the core idea of the application.

However, besides that, the application also implements some extra functionalities to enhance the previous workflow:

- A metadata editor that:
  - Will inform the analysis and validation workflows.
  - Will create a metadata file that will be published among the data.
- A beta integration with LLMs that allow the user to improve its analysis workflow
- Some basic data editing for simple manipulations of the file.
- Some basic file management (adding, removing, deleting, etc)

# Components

Taking into consideration the goal of the application, we have a traditional PySide6 application with:

- **MainWindow** containinig widgets and orchestrating interactions
  - **Sidebar**: to display a file navigator and some buttons.
  - **Content**: A widget to display the main content of the application that can switch between:
    - **Toolbar + Panels/Views**: We display a toolbar plus all the views like Data, Metadata, Errors Report, Source, etc)
    - **Welcome**: If no file are selected we display a welcome screen with an upload button
- **Custom Widgets**: To extend functionalities (like a CustomTreeView or a ClickableLabel) or implement Dialogs.

In a visual way, our simplified macro structure looks something like this:

![ODE Components](./assets/ode-components.png)

## Main Window

Besides the normal responsibilities of the [QMainWindow](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMainWindow.html#detailed-description), we are using it to **store state variables and orchestrate interactions** between QWidgets. Think of the MainWindow as the state manager or the main controller of the application. If two Widgets needs to talk to each other, probably that interaction will be orchestrated in the MainWindow. In Qt Language: all the [Signals and Slots](https://doc.qt.io/qt-6/signalsandslots.html) connections are coded in the MainWindow.

:::note 
One Key difference is that we are not using Qt's Toolbar, we coded our own Toolbar (which is just a QWidget with a couple of buttons).
:::

## Model View Programing

If there is one piece of documentation that we would definitely suggest as mandatory to feel comfortable developing the Open Data Editor is the [Model/View architecture](https://doc.qt.io/qt-6/model-view-programming.html) of Qt. The main feature of Reading/Viewing/Reporting is done using [QTableView](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTableView.html#pyside6-qtwidgets-qtableview) and an instanced [QAbstractTableModel](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QAbstractTableModel.html) that we call FrictionlessTableModel.

:::note
There is an excellent tutorial to understand the basics of Model/View programming in [Python GUIs website](https://www.pythonguis.com/tutorials/pyside6-qtableview-modelviews-numpy-pandas/).
:::

**FrictionlessTableModel** is one of our key classes since it is in charge of reading, validating and creating data structures to display both the data and our Error Reports. So definitely spend some time understanding it.


# Files and Metadata handling

## 1. Uploading a File

We are not uploading anywhere. When a user clicks on `Upload data` we just make a copy of the file and paste it in the `PROJECT_PATH` which, so far, is hardcoded to a `.opendataeditor/tmp` folder in the Home directory of the user:
 - **Linux/Mac**: `/home/username/.opendataeditor/tmp`
 - **Windows**: `C:\Users\username\.opendataeditor\tmp`

This means that the user **do not work on the original file**, but a copy of it.

## 2. Metadata handling

In order to properly work with Frictionless Data we need to handle a metadata file. There is a 1:1 relation between data files and metadata files: **for every data file, we have a metadata file**.

The metadata file is a JSON file that stores Fricionless Metadata and any other metadata required by ODE. All metadata files are going to be 
stored in a `.metadata` folder mimicing the structure of the `PROJECT_PATH` folder.

Example 1:
  - **Data File**: `/home/username/.opendataeditor/tmp/myfile.csv`
  - **Metadata File**: `/home/username/.opendataeditor/tmp/.metadata/myfile.json`

Example 2 (subfolder):
  - **Data File**: `/home/username/.opendataeditor/tmp/subfolder/invalid-file.csv`
  - **Metadata File**: `/home/username/.opendataeditor/tmp/.metadata/subfolder/invalid-file.json`

This decision was made for the following reasons:
 - Maintaining the same filename for the data file and metadata allow us to easily join them.
 - The uniqueness  of files (you cannot have two files with the same name in the same folder) provide us with a perfect UNIQUE identifier.
 - This way we do not need a third database to keep track of the mapping between Data Files and Metadata Files.

This decision comes with a pain point:
 - We need to ensure that on every file operation (create, rename, delete, etc) we replicate it for the metadata file. If the user renames a `file.csv` to `new-name.csv`, we need to ensure that the metadata file is renamed as well from `./metadata/file.csv` to `./metadata/new-name.csv`.

# Weaknesses Analysis

### Frictionless Dependency

Historically, the project relied on the `frictionless-py` framework for all tabular data operations. Although `frictionless-py` is a battle-tested library it has its own limitations regarding performance, maintenance and, generally speaking, legacy approaches that are used in its data-processing and data-modelling architecture. 

Using `frictionless-py` also brings the whole package dependencies to be installed and used for Open Data Editor to work properly. This is a significant limitation for the project as it makes the project less portable and more complex to set up. 

