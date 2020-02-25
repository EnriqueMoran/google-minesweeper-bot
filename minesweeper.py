import cv2
import pyautogui
import time
import numpy as np
import random



class Minesweeper():

    __author__: "EnriqueMoran"


    def __init__(self, difficulty=1, mute=False, speed=0.85):
        self.difficulty = difficulty    # 0 = Easy, 1 = Normal, 2 = Hard
        self.configImage = "./images/config.png"    # images folder must be in the same directory as this script
        self.muteImage = "./images/mute.png"
        self.oneImage = "./images/one.png"
        self.twoImage = "./images/two.png"
        self.threeImage = "./images/three.png"
        self.fourImage = "./images/four.png"
        self.fiveImage = "./images/five.png"
        self.mute = mute    # mute game
        self.speed = speed
        self.gameWindow = None
        self.cells = {}    # {(x, y) : (posX, posY), cont}   cont = ? (unknow), F (flag), 0 (safe), n (number)
        self.nBombs = None
        self.size = None    # cell size
        self.rows = None    # number of rows
        self.cols = None    # number of columns


    def getGameWindow(self):

        def clearWindow(corners):    # remove wrong detections
            res = []
            coords = [coord for coords in corners for coord in coords]
            for coord in coords:
                if coords.count(coord) > 1:
                    res.append(coord)
            return [res[k:k+2] for k in range(0, len(res), 2)]    # group by 2


        screenshot = pyautogui.screenshot()
        image = np.array(screenshot)    # convert to opencv compatible format

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)    # filter by color
        lower_green = np.array([80, 60, 80])
        upper_green = np.array([81, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        result = cv2.bitwise_and(image, image, mask=mask)

        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)    # filter by shape
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        threshold = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        im2, contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        for i in contours:    # filter by min size
            size = cv2.contourArea(i)
            if size > 10000:    # get corners
                gray = np.float32(gray)
                mask = np.zeros(gray.shape, dtype="uint8")
                cv2.fillPoly(mask, [i], (255, 255, 255))
                dst = cv2.cornerHarris(mask, 5, 3, 0.04)
                ret, dst = cv2.threshold(dst, 0.1 * dst.max(), 255, 0)
                dst = np.uint8(dst)
                ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
                corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)
                if len(corners) == 5:    # if its a square
                    return clearWindow(corners)
        print("Game window not found!")


    def initializeCells(self):
        x0 = self.gameWindow[0][1]
        y0 = self.gameWindow[0][0]
        if self.difficulty == 0:
            self.size = 45    # px
            self.rows = 8
            self.cols = 10
            self.nBombs = 10
        elif self.difficulty == 1:
            self.size = 30
            self.rows = 14
            self.cols = 18
            self.nBombs = 40
        elif self.difficulty == 2:
            self.size = 25
            self.rows = 20
            self.cols = 24
            self.nBombs = 99
        for row in range(self.rows):
            for col in range(self.cols):
                x = x0 + (row * self.size) + (self.size / 2)
                y = y0 + (col * self.size) + (self.size / 2)
                self.cells[(col, row)] = [(x, y), '?']


    def muteSound(self):    # find mute button and click on it if its not muted
        try:
            muteButton = pyautogui.locateOnScreen(self.muteImage, confidence=0.9)
            mute_x = pyautogui.center(muteButton).x
            mute_y = pyautogui.center(muteButton).y
            pyautogui.moveTo(mute_x, mute_y, 0.5)
            pyautogui.click()
        except:
            print("Mute sound button not found! (might be already muted)")
        self.mute = False


    def setDifficulty(self):
        if self.difficulty not in [0, 1, 2]:
            raise ValueError("Difficulty must be 0 (easy), 1 (normal) or 2 (hard)!")
        try:
            configButton = pyautogui.locateOnScreen(self.configImage, confidence=0.9)
            config_x = pyautogui.center(configButton).x
            config_y = pyautogui.center(configButton).y
            pyautogui.moveTo(config_x, config_y, 0.5)
            pyautogui.click()
            if self.difficulty == 0:    # easy
                pyautogui.moveTo(config_x, config_y + 25, 0.5)
            elif self.difficulty == 1:   # normal
                pyautogui.moveTo(config_x, config_y + 50, 0.5)
            else:    # hard
                pyautogui.moveTo(config_x, config_y + 75, 0.5)
            pyautogui.click()
        except:
            raise Exception("Flag image not found!")


    def getScore(self, image):
        image = cv2.resize(image, (30, 30))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        res = 0
        resConfidence = 0
        cont = 0
        scores = [self.oneImage, self.twoImage, self.threeImage, self.fourImage, self.fiveImage]
        matchTemplateMethod = eval('cv2.TM_CCOEFF_NORMED')
        for score in scores:
            cont += 1
            score = cv2.imread(score, 0)
            match = cv2.matchTemplate(image, score, matchTemplateMethod)
            _, confidence, _, _ = cv2.minMaxLoc(match)
            if confidence > 0.75 and confidence > resConfidence:
                resConfidence = confidence
                res = cont
        return res


    def updateCells(self):
        screenshot = pyautogui.screenshot()
        x0 = self.gameWindow[0][1]
        y0 = self.gameWindow[0][0]

        thr = [10 if self.difficulty == 0 else 6 if self.difficulty == 1 else 4][0]    # cell border thickness

        for row in range(self.rows):
            for col in range(self.cols):
                x = x0 + (row * self.size)
                y = y0 + (col * self.size)
                color = screenshot.getpixel((int(y) + thr, int(x) + thr))
                if color not in [(162, 209, 73), (170, 215, 81)] and color in [(229, 194, 159), (215, 184, 153), (236, 209, 183), (225, 202, 179)]:    # if its not an unknown cell
                    image = np.array(screenshot)
                    image = image[int(x):int(x + self.size), int(y):int(y + self.size)]
                    score = self.getScore(image)
                    if self.cells[(col, row)][1] == 'F':
                        pass
                    else:
                        self.cells[(col, row)] = [(y + self.size / 2, x + self.size / 2), score]


    def getNeighbors(self, col, row):    # return unknown neighbors
        res = []
        try:
            if self.cells[col - 1, row - 1][1] == '?':
                res.append((col - 1, row - 1))
        except:
            pass
        try:
            if self.cells[col, row - 1][1] == '?':
                res.append((col, row - 1))
        except:
            pass
        try:
            if self.cells[col + 1, row - 1][1] == '?':
                res.append((col + 1, row - 1))
        except:
            pass
        try:
            if self.cells[col - 1, row][1] == '?':
                res.append((col - 1, row))
        except:
            pass
        try:
            if self.cells[col + 1, row][1] == '?':
                res.append((col + 1, row))
        except:
            pass
        try:
            if self.cells[col - 1, row + 1][1] == '?':
                res.append((col - 1, row + 1))
        except:
            pass
        try:
            if self.cells[col, row + 1][1] == '?':
                res.append((col, row + 1))
        except:
            pass
        try:
            if self.cells[col + 1, row + 1][1] == '?':
                res.append((col + 1, row + 1))
        except:
            pass
        return res


    def getFlags(self, col, row):    # return flagged neighbors
        res = []
        try:
            if self.cells[col - 1, row - 1][1] == 'F':
                res.append((col - 1, row - 1))
        except:
            pass
        try:
            if self.cells[col, row - 1][1] == 'F':
                res.append((col, row - 1))
        except:
            pass
        try:
            if self.cells[col + 1, row - 1][1] == 'F':
                res.append((col + 1, row - 1))
        except:
            pass
        try:
            if self.cells[col - 1, row][1] == 'F':
                res.append((col - 1, row))
        except:
            pass
        try:
            if self.cells[col + 1, row][1] == 'F':
                res.append((col + 1, row))
        except:
            pass
        try:
            if self.cells[col - 1, row + 1][1] == 'F':
                res.append((col - 1, row + 1))
        except:
            pass
        try:
            if self.cells[col, row + 1][1] == 'F':
                res.append((col, row + 1))
        except:
            pass
        try:
            if self.cells[col + 1, row + 1][1] == 'F':
                res.append((col + 1, row + 1))
        except:
            pass
        return res


    def selectCell(self, lastCell):
        col, th_x = lastCell[0], lastCell[0]
        row, th_y = lastCell[1], lastCell[1]
        dx = 0
        dy = -1
        cont = 0    # cells checked (in board)
        while cont < self.rows * self.cols:
            if col < self.cols and row < self.rows and col >= 0 and row >= 0:
                score = self.cells[(col, row)][1]
                if score != 0 and score != 'F':
                    try:
                        neighbors = self.getNeighbors(col, row)
                        flaggeds = self.getFlags(col, row)
                        # print((col, row), score, len(neighbors), len(flaggeds))    # debug
                        if len(flaggeds) < int(score) and len(neighbors) + len(flaggeds) <= int(score):
                            return (neighbors, 0)    # select cells to place flag
                        elif len(flaggeds) == int(score) and len(neighbors) > 0:
                            return (neighbors, 1)    # select cells to click
                    except:
                        pass
                cont += 1
            col -= th_x
            row -= th_y
            if col == row or (col < 0 and col == -row) or (col > 0 and col == 1 - row):
                dx, dy = -dy, dx
            col, row = col + dx + th_x, row + dy + th_y
        return (None, 2)    # select random cell to click


    def start(self):
        x0 = self.gameWindow[0][1]
        y0 = self.gameWindow[0][0]
        pyautogui.moveTo(y0 + 5, x0 + 5)
        pyautogui.click()


    def placeFlag(self, cell):
        x, y = self.cells[(cell[0], cell[1])][0]
        pyautogui.moveTo(y, x, 0.1)
        pyautogui.click(button='right')
        self.cells[(cell[0], cell[1])][1] = 'F'

                    
    def showGrid(self):
        print("")
        cont = 0
        cells = list(self.cells.values())
        for i in range(self.rows):
            for j in range(self.cols):
                print(cells[cont][1], end="")
                cont += 1
            print("")


    def randomCell(self):    # click on random unknown cell
        unknownCells = {cell: value[0] for cell, value in self.cells.items() if value[1] == '?'}
        cell = random.choice(list(unknownCells.keys()))
        x, y = self.cells[cell][0][0], self.cells[cell][0][1]
        pyautogui.moveTo(y, x, 0.1)
        pyautogui.click()
        print("random!")
        return cell
        
    
    def checkLose(self, nBombs):
        lose = False
        # time.sleep(0.1 * nBombs)    # ensure score screen is shown
        screenshot = pyautogui.screenshot()
        if self.difficulty == 0:
            x, y = self.cells[(2, 0)][0]
        elif self.difficulty == 1:
            x, y = self.cells[(5, 1)][0]
        elif self.difficulty == 2:
            x, y = self.cells[(7, 4)][0]
        color = screenshot.getpixel((int(y), int(x)))
        if color == (77, 193, 249):
            lose = True
        return lose


    def play(self):    # game loop
        if self.mute:
            self.muteSound()
        self.setDifficulty()

        self.gameWindow = self.getGameWindow()
        self.initializeCells()
        self.start()
        time.sleep(0.85)

        self.updateCells()
        # self.updateCells()    # remove false positive
        # self.showGrid()

        lastCell = (0, 0)    # last clicked cell

        while self.nBombs >= 0:   
            cells, click = self.selectCell(lastCell)
            if click == 0:
                for cell in cells:
                    self.placeFlag(cell)
                    self.nBombs -= 1
                    lastCell = cell
            elif click == 1:
                for cell in cells:
                    x, y = self.cells[(cell[0], cell[1])][0]
                    pyautogui.moveTo(y, x, 0.1)
                    pyautogui.click()
                    lastCell = cell
            elif click == 2:    # click random cell
                lastCell = self.randomCell()
            if self.checkLose(self.nBombs):
                print("I lose")
                break

            time.sleep(self.speed)
            self.updateCells()
            # self.updateCells()
            # self.showGrid()
        print("I won!")
        return



if __name__ == "__main__":
    difficulty = 1    # normal difficulty
    mute = True    # mute sound
    speed = 0.15    # time between each move
    minesweeper = Minesweeper(difficulty, mute, speed)
    minesweeper.play()


