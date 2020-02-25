# google-minesweeper-bot
Beat Google's Minesweeper game using this script.
Necessary libraries: *numpy*, *opencv2*, *pyautogui*.


![alt tag](/readme_images/gif_1.gif)


## Installation guide
Download this project using this command:
```
https://github.com/EnriqueMoran/google-minesweeper-bot.git
```
Next, install necessary libraries using the following command:
```
pip install pyautogui opencv-python numpy
```
Once the installation is complete, right click on minesweeper.py file and edit it with IDLE.
Open google minesweeper game and make sure the game window is completely visible, then click on python IDLE and press F5.

Note: *The first time you run the script will open a new windows that might be placed over game window, just move out and resize it.*

**Important:** If you need to abort the execution of the script, place the mouse on top-left corner of your screen.


## How it works
On each move a screenshot is taken and each cell that is not green is recognized (not-unknown cell). 

![alt tag](/readme_images/image_1.png)

Next, each cell is checked for placing a flag on any of their adjacent cells. The used algorithm is the following:

If the number of flagged adjacent cells is less than the score of the checked cell and the number of unknown adjacent cells plus flagged cells is less than the score, then place a flag on any of the unknown adjacent cells.

If the number of flagged adjacent cells is equal to the score and the number of unknown adjacent cells is higher than 0, then click on any of them.

![alt tag](/readme_images/image_2.png)

If none of the cells are valid for any action, a random unknown cell will be clicked.

Once there is no more flags left, the game is beated and the script stops. If the game is lost when clicking a random cell, if score window is recognized, the script will stop too.


## Performance
On v1.0 performance depends on speed parameter that set the time the script will wait after clicking a cell to take a new screenshot.


| Speed | Nº Games | Easy win/defeat | Normal win/defeat | Hard win/defeat | Easy Avg. Time | Normal Avg. Time | Hard Avg. Time |
|-------|----------|-----------------|-------------------|-----------------|----------------|------------------|----------------|
| 0.05  | 10       | 9/1             | 5/5               | 3/7             | 27.55          | 258.6            | 854            |
| 0.10  | 10       | 8/2             | 8/2               | 0/10            | 28.875         | 235.83           | -              |
| 0.15  | 10       | 9/1             | 10/0              | 2/8             | 27.2           | 214.66           | 812.5          |


On v1.2, opencv2 template matching is no longer used. The scores are obtained from their pixels color. Speed performance has been improved on easy and normal difficulties.
Adding rules to apply when have to randomly click is needed.

| Speed | Nº Games | Easy win/defeat | Normal win/defeat | Hard win/defeat | Easy Avg. Time | Normal Avg. Time | Hard Avg. Time |
|-------|----------|-----------------|-------------------|-----------------|----------------|------------------|----------------|
| 0.015 | 10       | 8/2             | 4/6               | 0/10            | 11.25          | 42               | -              |
| 0.05  | 10       | 7/3             | 5/5               | 1/9             | 11.28          | 44.6             | 113            |



## TODO

* Add rules for random clicks.
