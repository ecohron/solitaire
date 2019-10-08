# Name: Emma Cohron
# Section: B
# AndrewID: ecohron
from tkinter import *
import random
import copy

# barebones timer, key press, mouse press, and run functions taken from
# course website: pd43.github.io

class Card(object):
    numberNames = ["Ace","2","3","4","5","6","7","8","9","10","Jack","Queen",
                    "King"]
    suitNames = ["Club", "Diamond", "Spade", "Heart"]
    suitColors = ["black", "red"]
    
    @staticmethod
    def getDeck():
        deck = []
        for number in range(13):
            for suit in range(4):
                deck.append(Card(number, suit))
        return deck

    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
        self.fileName = "%s%s.gif" %(Card.numberNames[self.number],
                                     Card.suitNames[self.suit])
        self.x = 0
        self.y = 0
        self.front = False
        Card.width = 70
        Card.height = 95
    
    def __repr__(self):
        return "%s%s" % (Card.numberNames[self.number], 
                            Card.suitNames[self.suit])
    
    def drawFront(self, canvas):
        image = getPlayingCardImage(canvas, self.suit, self.number)
        canvas.create_image(self.x, self.y, anchor=NW, image=image)
    
    def drawBack(self, canvas):
        image = getBackCardImage(canvas)
        canvas.create_image(self.x, self.y, anchor=NW, image=image)

    def isClicked(self, data, x, y):
        if (x >= self.x and x <= self.x + data.width/15) and \
            (y >= self.y and y <= self.y + data.height/12) \
            and (self.x != 0 and self.y != 0):
            return True
        return False


class Button(object):
    def __init__(self, data, color, x, y, width, text):
        self.color = color
        Button.height = data.height/15
        self.width = width
        self.x = x
        self.y = y
        self.text = text
    
    def draw(self, canvas, data):
        canvas.create_rectangle(self.x, self.y, self.x + self.width,
                                self.y + self.height, fill = self.color)
        canvas.create_text(self.x + self.width/2, self.y + self.height/2,
                            font = "Helvetica 32 bold", fill = "white", 
                            text = self.text)
    
    def isClicked(self, x, y):
        if (x >= self.x and x <= self.x+self.width and
            y >= self.y and y <= self.y+self.height):
            return True
        return False


class Stack(object):
    def __init__(self, data, x, y):
        self.x = x
        self.y = y
        Stack.width = 70
        Stack.height = 95

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.x + Stack.width,
                                self.y + Stack.height)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def isClicked(self, x, y):
        if (x >= self.x and x <= self.x+Stack.width and
            y >= self.y and y <= self.y+Stack.height):
            return True
        return False


bestMoves = []
bestTimes = []
# initialize the data which will be used to draw on the screen.
def init(data):
    # initializes variables to track which screen is displayed at any given moment
    screenInit(data)
    data.gameSolved = False
    data.orderedDeck = Card.getDeck()
    data.deck = Card.getDeck()
    data.boardCards = []
    data.timerCounter = 0
    data.moveCount = 0
    data.backgroundColor = rgbString(0, 128, 55)
    # initializes all the possible buttons that could appear on screen
    buttonInit(data)
    data.foundations = [Stack(data, data.width/2 + 40, 30)] + \
                       [Stack(data, data.width/2 + i*Stack.width + 40 + i*20, 30)
                        for i in range(1,4)]
    data.boardStacks = [Stack(data, data.width/6+i*Stack.width + i*20, 200)
                        for i in range(7)]
    data.leftoverStack = Stack(data, data.width/10, 30)
    data.leftoverCards = []
    data.flippedCards = []
    data.foundationCards = [[], [], [], []]
    data.cardToMove = [None, None]
    data.moves = []
    data.solve = False
    data.gameOver = False
    data.noMoves = False
    data.hint = None
    data.cannotUndo = False


def screenInit(data):
    data.menuScreen = True
    data.instructionScreen = False
    data.gameScreen = False


def buttonInit(data):
    data.wildButton = Button(data, "black", data.width / 2 - 3 * data.width / 20,
                             5 * data.height / 8, 3 * data.width / 10, "Play Game")
    data.instructionButton = Button(data, "black", data.width / 2 - data.width / 10,
                                    data.wildButton.y + Button.height * 2,
                                    data.width / 5, "Help")
    data.menuButtons = [data.wildButton, data.instructionButton]
    data.hintButton = Button(data, "red", data.width / 10,
                             11 * data.height / 12 - Button.height,
                             data.width / 5, "Hint")
    data.solveButton = Button(data, "red", data.width / 5 + 3 * data.hintButton.width / 4,
                              11 * data.height / 12 - Button.height,
                              3 * data.width / 10, "Solve Game")
    data.undoButton = Button(data, "red", 7 * data.width / 10,
                             11 * data.height / 12 - Button.height,
                             data.width / 5, "Undo Move")
    data.gameButtons = [data.hintButton, data.solveButton, data.undoButton]


def cinit(canvas, data):
    loadPlayingCardImages(canvas, data)

# image handling functions adapted from code on old course website:
# http://www.kosbie.net/cmu/fall-15/15-112/

def loadPlayingCardImages(canvas, data):
    canvas.cardImages = []
    for card in data.orderedDeck:
        filename = card.fileName
        canvas.cardImages.append(PhotoImage(file=filename))
    suitsFileName = "suits.gif"
    canvas.cardImages.append(PhotoImage(file=suitsFileName))
    backFileName = "back.gif"
    canvas.cardImages.append(PhotoImage(file=backFileName))


def getPlayingCardImage(canvas, suit, number):
    return canvas.cardImages[4*number+suit]


def getBackCardImage(canvas):
    return canvas.cardImages[-1]


def getSuitsImage(canvas):
    return canvas.cardImages[-2]


def createDeal(data):
    count = 0
    # deals out the cards into a 2d list that contains every stack in the board:
    for stack in range(7):
        x = data.boardStacks[stack].getX()
        y = data.boardStacks[stack].getY()
        cardStack = []
        for cardNum in range(stack+1):
            card = copy.copy(data.deck[count])
            cardStack.append(card)
            card.x = x
            card.y = y
            if stack==cardNum: card.front = True
            y += 20
            count += 1
        data.boardCards.append(cardStack)
    for leftoverCard in range(count, len(data.deck)):
        data.deck[leftoverCard].x = data.leftoverStack.getX()
        data.deck[leftoverCard].y = data.leftoverStack.getY()
        data.leftoverCards.append(data.deck[leftoverCard])


def mousePressed(event, data):
    data.hint = None
    data.cannotUndo = False
    if data.menuScreen:
        # checks menu button clicks:
        if data.wildButton.isClicked(event.x, event.y):
            data.menuScreen, data.gameScreen = False, True
            random.shuffle(data.deck)
            createDeal(data)
        elif data.instructionButton.isClicked(event.x, event.y):
            data.menuScreen, data.instructionScreen = False, True
    if data.gameScreen:
        # checks game play button clicks:
        if data.hintButton.isClicked(event.x, event.y): giveHint(data)
        elif data.solveButton.isClicked(event.x, event.y):
            data.solve = True
            solve(data)
        elif data.undoButton.isClicked(event.x, event.y): undoMove(data)
        # checks clicks on leftover cards:
        elif data.leftoverStack.isClicked(event.x, event.y) and len(data.leftoverCards) == 0:
            resetLeftover(data)
        elif len(data.leftoverCards)> 0 and \
                data.leftoverCards[-1].isClicked(data, event.x, event.y):
            flipCards(data)
        # checks for clicks on cards to move:
        elif data.cardToMove[0] == None:
            for stack in range(len(data.boardCards)):
                for card in range(len(data.boardCards[stack])):
                    if data.boardCards[stack] != [] and card == len(data.boardCards[stack])-1 and \
                            data.boardCards[stack][card].isClicked(data, event.x, event.y):
                        data.cardToMove = [data.boardCards[stack][card], stack]
                    elif data.boardCards[stack] != [] and \
                            data.boardCards[stack][card].isClicked(data, event.x, event.y):
                        data.cardToMove = [data.boardCards[stack][card:], stack]
            if data.flippedCards != [] and \
                    data.flippedCards[-1][-1].isClicked(data, event.x, event.y):
                data.cardToMove[0] = data.flippedCards[-1][-1]
        else:
            # checks for clicks on cards where a pre-selected card will be moved to:
            for stack in range(len(data.boardCards)):
                if len(data.boardCards[stack]) > 0:
                    for card in range(len(data.boardCards[stack])-1, len(data.boardCards[stack])):
                        if data.boardCards[stack][card].isClicked(data, event.x, event.y) \
                                and data.cardToMove[1] != None:
                            moveBoardCardsOnBoard(data, stack, card)
                            return
                        elif data.boardCards[stack][card].isClicked(data, event.x, event.y):
                            moveLeftoverCardOnBoard(data, stack, card)
                            return
                else:
                    if data.boardStacks[stack].isClicked(event.x, event.y) \
                            and data.cardToMove[1] != None:
                        moveBoardCardsOnBoard(data, stack, 0)
                    elif data.boardStacks[stack].isClicked(event.x, event.y):
                        moveLeftoverCardOnBoard(data, stack, 0)
            for stack in range(len(data.foundationCards)):
                if data.foundations[stack].isClicked(event.x, event.y) \
                        and data.cardToMove[1] != None:
                    moveBoardCardToFoundation(data, stack)
                    return
                elif data.foundations[stack].isClicked(event.x, event.y):
                    moveLeftoverCardToFoundation(data, stack)
            data.cardToMove = [None, None]


def moveBoardCardsOnBoard(data, stack, position, click=True):
    toReturn = False
    # checks all possible move conditions and makes board changes accordingly:
    if isLegalBoardMove(data, stack, position):
        toReturn = True
        removeStack = data.cardToMove[1]
        if isinstance(data.cardToMove[0], Card):
            card = data.cardToMove[0]
            card.x = data.boardStacks[stack].x
            if len(data.boardCards[stack]) > 0:
                card.y = data.boardCards[stack][position].y + 20
            else: card.y = data.boardStacks[stack].y
            data.boardCards[stack].append(card)
            data.boardCards[removeStack].remove(card)
            data.moves.append([data.cardToMove[0], data.cardToMove[1], stack])
        else:
            cards = data.cardToMove[0]
            count = 0
            for card in cards:
                card.x = data.boardStacks[stack].x
                if len(data.boardCards[stack]) == 0:
                    card.y = data.boardStacks[stack].y + (20*count)
                    count += 1
                else:
                    card.y = data.boardCards[stack][position].y + 20*(count+1)
                    count+=1
            data.boardCards[stack].extend(cards)
            lenList = len(data.boardCards[removeStack])
            lenSub = len(data.cardToMove[0])
            data.boardCards[removeStack] = data.boardCards[removeStack][:lenList-lenSub]
        if data.boardCards[removeStack] != []:
            data.boardCards[removeStack][-1].front = True
    if click == True:
        data.cardToMove = [None, None]
    return toReturn


def isLegalBoardMove(data, stack, position):
    if data.cardToMove[0] == None and data.cardToMove[1]==None:
        return False
    if isinstance(data.cardToMove[0], Card):
        card = data.cardToMove[0]
    elif data.cardToMove[0] != []:
        card = data.cardToMove[0][0]
    else: return False
    if (card.number == 12 and len(data.boardCards[stack]) ==0):
        data.moveCount += 1
        return True
    elif (data.boardCards[stack] == []):
        return False
    elif (data.boardCards[stack][position].number == card.number+1 and
            not Card.suitColors[data.boardCards[stack][position].suit%2]
            == Card.suitColors[card.suit%2]):
        data.moveCount += 1
        return True
    return False


def moveBoardCardToFoundation(data, stack, click = True):
    toReturn = False
    # checks all possible move conditions and makes board changes accordingly:
    if isLegalFoundationMove(data, stack):
        card = data.cardToMove[0]
        removeStack = data.cardToMove[1]
        card.x = data.foundations[stack].x
        card.y = data.foundations[stack].y
        data.foundationCards[stack].append(card)
        data.boardCards[removeStack].pop()
        if data.boardCards[removeStack] != []:
            data.boardCards[removeStack][-1].front = True
        data.moves.append([data.cardToMove[0], data.cardToMove[1], stack])
        toReturn = True
        data.moves.append((data.cardToMove[0], stack, data.cardToMove[1]))
    if click == True:
        data.cardToMove = [None, None]
    return toReturn


def isLegalFoundationMove(data, stack):
    card = data.cardToMove[0]
    if card == None and data.cardToMove[1]==None:
        return False
    if (data.foundationCards[stack] == [] and card.number == 0):
        data.moveCount += 1
        return True
    elif (data.foundationCards[stack] == []):
        return False
    elif (data.foundationCards[stack][-1].number == card.number-1 and
        data.foundationCards[stack][-1].suit == card.suit):
        data.moveCount += 1
        return True
    return False


def moveLeftoverCardOnBoard(data, stack, position, click = True):
    toReturn = False
    # checks all possible move conditions and makes board changes accordingly:
    if isLegalBoardMove(data, stack, position):
        card = data.cardToMove[0]
        card.x = data.boardStacks[stack].x
        if len(data.boardCards[stack]) > 0:
            card.y = data.boardCards[stack][position].y + 20
        else:
            card.y = data.boardStacks[stack].y
        data.boardCards[stack].append(card)
        data.flippedCards[-1].pop()
        if data.flippedCards[-1] == []:
            data.flippedCards.pop()
        toReturn = True
    if click == True:
        data.cardToMove = [None, None]
    return toReturn


def moveLeftoverCardToFoundation(data, stack, click = True):
    toReturn = False
    # checks all possible move conditions and makes board changes accordingly:
    if isLegalFoundationMove(data, stack):
        card = data.cardToMove[0]
        card.x = data.foundations[stack].x
        card.y = data.foundations[stack].y
        data.foundationCards[stack].append(card)
        data.flippedCards[-1].remove(card)
        if data.flippedCards[-1]==[]:
            data.flippedCards.pop()
        toReturn = True
    if click == True:
        data.cardToMove = [None, None]
    return toReturn


def resetLeftover(data):
    for set in range(len(data.flippedCards)-1, -1, -1):
        for card in range(len(data.flippedCards[set])-1, -1, -1):
            data.flippedCards[set][card].x = data.leftoverStack.getX()
            data.flippedCards[set][card].front = False
            data.leftoverCards.append(data.flippedCards[set][card])
    data.flippedCards = []


def flipCards(data):
    numLeftover = len(data.leftoverCards)
    if numLeftover < 4: end = -1
    else: end = numLeftover-4
    data.flippedCards.append([])
    for card in range(numLeftover-1, end, -1):
        data.leftoverCards[card].front = True
        data.flippedCards[-1].append(data.leftoverCards[card])
        data.leftoverCards.pop()


def giveHint(data):
    # checks foundation moves then board moves, otherwise suggests flipping cards from the deck:
    data.cardToMove = [None, None]
    for stack in range(len(data.boardCards)):
        if len(data.boardCards[stack]) > 0:
            data.cardToMove[0] = data.boardCards[stack][-1]
            data.cardToMove[1] = stack
        else: continue
        for fstack in range(len(data.foundationCards)):
            if isLegalFoundationMove(data, fstack):
                data.hint = data.cardToMove[0]
                return
    data.cardToMove = [None, None]
    for stack in range(len(data.boardCards)):
        if len(data.boardCards[stack]) > 0:
            last = findLastUp(data, stack)
            data.cardToMove[0] = data.boardCards[stack][last:]
            data.cardToMove[1] = stack
        else: continue
        for bstack in range(len(data.boardCards)):
            if isLegalBoardMove(data, bstack, -1):
                data.hint = data.cardToMove[0]
                return
    data.cardToMove = [None, None]
    if (len(data.flippedCards) > 1):
        data.cardToMove[0] = data.flippedCards[-1][-1]
        data.cardToMove[1] = None
        for fstack in range(len(data.foundationCards)):
            if isLegalFoundationMove(data, fstack):
                data.hint = data.cardToMove[0]
                return
    data.cardToMove = [None, None]
    if len(data.flippedCards) > 1:
        data.cardToMove[0] = data.flippedCards[-1][-1]
        data.cardToMove[1] = None
        for bstack in range(len(data.boardCards)):
            if isLegalBoardMove(data, bstack, -1):
                data.hint = data.cardToMove[0]
                return
    elif len(data.leftoverCards) > 0:
        data.hint = data.leftoverCards[-1]
    else:
        data.noMoves = True


def undoMove(data):
    # undoes last saved move:
    if len(data.moves)>0 and isinstance(data.moves[-1][0], Card):
        card = data.moves[-1][0]
        cardTo = data.moves[-1][1]
        cardFrom = data.moves[-1][2]
        if len(data.boardCards[cardTo]) > 0:
            data.boardCards[cardTo][-1].front = False
        data.boardCards[cardFrom][-1].x = data.boardStacks[cardTo].getX()
        if len(data.boardCards[cardFrom]) == 0:
            data.boardCards[cardFrom][-1].y = data.boardStacks[cardTo].getY()
        else:
            data.boardCards[cardFrom][-1].y = data.boardCards[cardTo][-1].y +20
        data.boardCards[cardTo].append(card)
        data.boardCards[cardFrom].remove(card)
        data.moves.pop()
    else:
        data.cannotUndo = True


def keyPressed(event, data):
    if data.instructionScreen:
        data.instructionScreen = False
        data.menuScreen = True
    # cheat codes :)
    elif event.keysym == "r":
        init(data)
    elif event.keysym == "s":
        bestMoves.append(data.moveCount)
        bestMoves.sort()
        if len(bestMoves) > 3: bestMoves.pop()
        bestTimes.append(data.timerCounter)
        bestTimes.sort()
        if len(bestTimes) > 3: bestTimes.pop()
        data.gameSolved = True
    elif event.keysym == "o":
        data.gameOver = True


def timerFired(data):
    if data.gameScreen:
        data.timerCounter += 1
    for stack in data.foundationCards:
        if len(stack) != 13:
            return
    data.gameSolved = True


def redrawAll(canvas, data):
    if data.gameOver:
        drawGameOverScreen(canvas, data)
    elif data.gameSolved:
        drawGameSolvedScreen(canvas, data)
    elif data.menuScreen:
        drawMenuScreen(canvas, data)
    elif data.instructionScreen:
        drawInstructionScreen(canvas, data)
    else:
        drawGame(canvas, data)


def drawMenuScreen(canvas, data):
    drawBackground(canvas, data)
    canvas.create_text(data.width/2, data.height/4, fill = "white", 
                        font = "Helvetica 64 bold", text = "SOLITAIRE")
    for button in data.menuButtons:
        button.draw(canvas, data)
    image = getSuitsImage(canvas)
    canvas.create_image(data.width/2, data.height/3 + 110, image=image)


def drawInstructionScreen(canvas, data):
    drawBackground(canvas, data)
    # Objective, Deal, and Play instructions taken from: 
    # http://www.bicyclecards.com/how-to-play/solitaire/
    instructionText = '''Welcome to Solitaire!
    The Objective:
        The first objective is to release and play into position certain cards
        to build up each foundation, in sequence and in suit, from the ace
        through the king.  The ultimate objective is to build the whole pack
        onto the foundations, and if that can be done, the game is won!
    The Deal:
        There are three different types of piles in Solitaire...
        1. The Tableau: Seven piles that make up the main table.
        2. The Foundations: Four piles on which a whole suit or sequence must
                            be built up.  The four aces are the bases of the
                            foundations.
        3. The Stock: The remaining cards if the entire deck is not laid out in
                      the tableau.  Additional cards from here can be brought
                      into the game according to the rules.
    The Play:
        The initial array may be changed by "building" - transferring cards
        among the face-up cards in the tableau.  Certain cards of the tableau
        can be played at once, while others may not be played until certain
        blocking cards are removed.  For example, of the seven cards facing up
        in the tableau, if one is a nine and another is a ten, you may transfer
        the nine to on top of the ten to begin building that pile in sequence.
        Since you have moved the nine from one of the seven piles, you have now
        unblocked a face down card; this card can be turned over and now is in
        play.
        As you transfer cards in the tableau and begin building sequences, if 
        you uncover an ace, the ace should be placed in one of the foundation
        piles.  The foundations get built by suit and in sequence from ace to
        king.
        Continue to transfer cards on top of each other in the tableau in 
        sequence.  If you can't move any more face up cards, you can utilize
        the stock pile by flipping over the first card.  This card can be played
        in the foundations or tableau.  If you cannot play the card in the 
        tableau or the foundations piles, you may take another set of three from
        the stock.  You may only access the second and third cards from the draw 
        when you have played the first and second respectively.
        If a vacancy in the tableau is created by the removal of cards elsewhere
        it is called a "space".  If a space is created, it can only be filled in
        with a king.  Filling a space with a king could potentially unblock one
        of the face down cards in another pile in the tableau.
        Continue to transfer cards in the tableau and bring cards into play from
        the stock pile until all the cards are built in suit sequences in the
        foundation piles to win!
    Extras:
        The game plays in "wild card" mode, which will give you a randomly shuffled 
        deck to play with.  This means the game may or may not be fully solvable.
        If you get stuck, click the "SOLVE GAME" button on the board to have the 
        computer finish the game for you.
        Your final scores are based on the number of moves you make and the amount
        of time it takes you to finish the game.  Therefore, a lower score is
        always better!  Only winning scores will be recorded.
        Press "r" on your keyboard at any time during game play to return to the
        main menu.
    Press any key to go back to the main menu.
    '''
    canvas.create_text(data.width/2, data.height/2, text = instructionText)


def drawGame(canvas, data):
    drawBackground(canvas, data)
    for button in data.gameButtons:
        button.draw(canvas, data)
    drawMovesandTime(canvas, data)
    drawBoard(canvas, data)
    drawBoardCards(canvas, data)
    drawFoundationCards(canvas, data)
    drawLeftoverCards(canvas, data)
    drawFlippedCards(canvas, data)
    # checks for and draws extraneous game conditions
    if data.noMoves:
        canvas.create_text(data.width/2, 2*data.height/3, text = "No Available Moves",
                           font = "Helvetica 32 bold", fill = "black")
    if isinstance(data.hint, Card) and data.timerCounter%2 == 0:
        canvas.create_rectangle(data.hint.x, data.hint.y, data.hint.x+Card.width,
                                data.hint.y+Card.height, fill="yellow")
    elif isinstance(data.hint, list) and len(data.hint) > 1 and data.timerCounter%2 == 0:
        canvas.create_rectangle(data.hint[0].x, data.hint[0].y, data.hint[0].x+Card.width,
                                data.hint[0].y+20, fill="yellow")
    elif isinstance(data.hint, list) and data.timerCounter%2 == 0:
        canvas.create_rectangle(data.hint[0].x, data.hint[0].y, data.hint[0].x+Card.width,
                                data.hint[0].y+Card.height, fill="yellow")
    if data.cannotUndo == True:
        canvas.create_text(data.width/2, 2*data.height/3, text = "No Available Move to Undo",
                           font = "Helvetica 32 bold", fill = "black")


def drawBoard(canvas, data):
    for foundation in data.foundations:
        foundation.draw(canvas)
    for stack in data.boardStacks:
        stack.draw(canvas)
    data.leftoverStack.draw(canvas)


def drawBoardCards(canvas, data):
    for i in range(len(data.boardCards)):
        for j in range(len(data.boardCards[i])):
            if not data.boardCards[i][j].front:
                data.boardCards[i][j].drawBack(canvas)
            else: data.boardCards[i][j].drawFront(canvas)


def drawFoundationCards(canvas, data):
    if data.gameOver == True or data.gameSolved == True:
        for i in range(4):
            for j in range(13):
                data.foundationCards[i][j].x = random.randint(0, 1000 - Card.width)
                data.foundationCards[i][j].y = random.randint(0, 1000 - Card.height)
                data.foundationCards[i][j].drawFront(canvas)
    else:
        for i in range(len(data.foundationCards)):
            for j in range(len(data.foundationCards[i])):
                if data.foundationCards[i][j] != None:
                    data.foundationCards[i][j].drawFront(canvas)


def drawLeftoverCards(canvas, data):
    for card in data.leftoverCards:
        card.drawBack(canvas)


def drawFlippedCards(canvas, data):
    x = data.leftoverStack.getX()+Card.width+20
    if data.flippedCards != []:
        for set in range(len(data.flippedCards)-1, len(data.flippedCards)):
            for card in range(len(data.flippedCards[set])):
                data.flippedCards[set][card].x = x
                data.flippedCards[set][card].drawFront(canvas)
                x += 20


def drawBackground(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill=data.backgroundColor)


def drawGameOverScreen(canvas, data):
    drawBackground(canvas, data)
    # draws cards in random arrangement
    for i in range(4):
        stack = []
        for j in range(13):
            card = data.orderedDeck[4*j+i]
            card.front = True
            card.x = data.foundations[i].getX()
            card.y = data.foundations[i].getY()
            stack.append(card)
        data.foundationCards[i].extend(stack)
    drawFoundationCards(canvas, data)
    canvas.create_text(data.width / 2, data.height / 2 - 100,
                       text="NO MORE POSSIBLE MOVES :(", font="Helvetica 48 bold",
                       fill="black")
    canvas.create_text(data.width / 2, data.height / 2 - 40, text="Best Winning Times:",
                       font="Helvetica 32 bold", fill="black")
    for i in range(len(bestTimes)):
        minutes = str(bestTimes[i] // 60)
        seconds = bestTimes[i] % 60
        if seconds < 10: seconds = "0" + str(seconds)
        canvas.create_text(data.width / 2, data.height / 2 - 10 + 40 * i,
                           text=minutes + ":" + str(seconds), font="Helvetica 32 bold",
                           fill="black")
    canvas.create_text(data.width / 2, data.height / 2 + 120, text="Best Winning Moves:",
                       font="Helvetica 32 bold", fill="black")
    for i in range(len(bestMoves)):
        canvas.create_text(data.width / 2, data.height / 2 + 150 + 40 * i, text=bestMoves[i],
                           font="Helvetica 32 bold", fill="black")


def drawGameSolvedScreen(canvas, data):
    drawBackground(canvas, data)
    # draws cards in random arrangement
    for i in range(4):
        stack = []
        for j in range(13):
            card = data.orderedDeck[4*j+i]
            card.front = True
            card.x = data.foundations[i].getX()
            card.y = data.foundations[i].getY()
            stack.append(card)
        data.foundationCards[i].extend(stack)
    drawFoundationCards(canvas, data)
    canvas.create_text(data.width/2, data.height/2 - 100, text = "CONGRATULATIONS - YOU WIN!!",
                       font = "Helvetica 48 bold", fill = "black")
    canvas.create_text(data.width/2, data.height/2 - 40, text = "Best Winning Times:",
                       font = "Helvetica 32 bold", fill = "black")
    for i in range(len(bestTimes)):
        minutes = str(bestTimes[i]//60)
        seconds = bestTimes[i]%60
        if seconds < 10: seconds = "0"+str(seconds)
        canvas.create_text(data.width/2, data.height/2 - 10 + 40*i, text = minutes+":"+str(seconds),
                           font = "Helvetica 32 bold", fill = "black")
    canvas.create_text(data.width/2, data.height/2 + 120, text = "Best Winning Moves:",
                       font = "Helvetica 32 bold", fill = "black")
    for i in range(len(bestMoves)):
        canvas.create_text(data.width/2, data.height/2 + 150 + 40*i, text = bestMoves[i],
                          font = "Helvetica 32 bold", fill = "black")


def drawMovesandTime(canvas, data):
    minutes = data.timerCounter//60
    seconds = data.timerCounter%60
    if seconds < 10: seconds = "0" + str(seconds)
    time = str(minutes) + ":" + str(seconds)
    canvas.create_text(data.width/2, 3*data.height/4,
                       text = "Time: %s Moves: %s" % (time, str(data.moveCount)),
                       font = "Helvetica 30 bold", fill = "white")


def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)


# SOLVER FUNCTIONS:
def solve(data):
    data.cardToMove = [None, None]
    for stack in range(len(data.boardCards)):
        if len(data.boardCards[stack]) > 0:
            data.cardToMove[0] = data.boardCards[stack][-1]
            data.cardToMove[1] = stack
        else: continue
        for fstack in range(len(data.foundationCards)):
            if isLegalFoundationMove(data, fstack):
                moveBoardCardToFoundation(data, fstack, False)
                return solve(data)
    data.cardToMove = [None, None]
    for stack in range(len(data.boardCards)):
        if len(data.boardCards[stack]) > 0:
            last = findLastUp(data, stack)
            data.cardToMove[0] = data.boardCards[stack][last:]
            data.cardToMove[1] = stack
        else: continue
        for bstack in range(len(data.boardCards)):
            if isLegalBoardMove(data, bstack, -1):
                moveBoardCardsOnBoard(data, bstack, -1, False)
                return solve(data)
    data.cardToMove = [None, None]
    if (len(data.flippedCards) > 1):
        data.cardToMove[0] = data.flippedCards[-1][-1]
        data.cardToMove[1] = None
        for fstack in range(len(data.foundationCards)):
            if isLegalFoundationMove(data, fstack):
                moveLeftoverCardToFoundation(data, fstack, False)
                return solve(data)
    data.cardToMove = [None, None]
    if len(data.flippedCards) > 1:
        data.cardToMove[0] = data.flippedCards[-1][-1]
        data.cardToMove[1] = None
        for bstack in range(len(data.boardCards)):
            if isLegalBoardMove(data, bstack, -1):
                moveLeftoverCardOnBoard(data, bstack, -1, False)
                return solve(data)
    elif len(data.leftoverCards) > 0:
        flipCards(data)
        return solve(data)
    elif len(data.flippedCards) > 0:
        resetLeftover(data)
        return solve(data)
    elif isSolved(data):
        data.gameSolved = True
        return True
    else:
        data.gameOver = True
        return False


def isSolved(data):
    for i in range(len(data.foundationCards)):
        if len(data.foundationCards[i]) < 13:
            return False
    return True


def findLastUp(data, stack):
    for i in range(len(data.boardCards[stack])):
        if data.boardCards[stack][i].front:
            return i
    return 0

####################################
####################################
# use the run function as-is
####################################
####################################

def run(width=1000, height=1000):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    class Struct(object): pass
    root = Tk()
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 1000 # milliseconds
    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    cinit(canvas, data)
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("bye!")

run()