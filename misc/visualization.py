import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from typing import List
import webbrowser
from classes.Trap import Trap
import geneticAlgorithm.utils as utils
from geneticAlgorithm.encoding import Encoding
import libs.simulation as sim
import libs.visualize as vis

TRAP = [47, 6, 86, 25, 1, 29, 26, 2, 62, 72, 0, 9]

def setTrap(trap: List[int]):
    global TRAP
    TRAP = trap

def getCellsFromStr(strEncoding: str, encoder: Encoding) -> Trap:
    ''' Takes in a string encoding and returns a trap '''
    decoded = encoder.decode(utils.convertStringToEncoding(strEncoding))
    cells = utils.createTrap(decoded).saveCells()

    return cells

def getImages(cells: List[str], activeList: List[int]) -> List[Image.Image]:
    ''' Get images from the the cells given, with activity determined by activeList '''

    # Define lists to generate image names
    cellTypes = ["gopher", "door", "wire", "arrow", "dirt", "food", "floor"]
    angleTypes = ["lacute", "racute", "lright", "rright", "lobtuse", "robtuse", "straight"]
    thickTypes = ["skinny", "normal", "wide"]

    imgList = []
    flattened = [col for row in cells for col in row]
    for i, cell in enumerate(flattened):
        cellCh, angleCh, thickCh, rotationCh = cell
        isActive = activeList[i]
        
        # Create subfields of image path
        cell = cellTypes[int(cellCh)] if cellCh != 'x' else ''
        angle = angleTypes[int(angleCh)] if angleCh != 'x' else ''
        thick = thickTypes[int(thickCh)] if thickCh != 'x' else ''
        active = 'active' if isActive else 'inactive'
        rotation = 45 * int(rotationCh) if rotationCh != 'x' else 0

        # Create image path and load it
        imageName = './animation/{cell}{thick}/{cell}{angle}{thick}{active}.png'.format(
                cell=cell, angle=angle, thick=thick, active=active
            )
        image = Image.open(imageName).rotate(-rotation)

        # Rotate the image
        imgList.append(image)

    # Add row of dirt at the bottom
    dirtImage = './animation/dirt/dirtinactive.png'
    for _ in range(3):
        imgList.append(Image.open(dirtImage))

    return imgList

def createImage(images: List[Image.Image], showGopher=True) -> Image.Image:
    ''' Takes in a list of 15 images and creates a trap image from it '''
    # Define constants for image
    width, height = images[0].width, images[0].height
    numRows, numCols = 5, 3

    # Create new background image on which to paste
    fullImage = Image.new('RGB', (numCols * width, numRows * height))
    
    # Add all background images for the trap
    for i in range(numRows):
        for j in range(numCols):
            x = j * width
            y = i * height
            fullImage.paste(images[j + i * numCols], (x, y))

    # Show the gopher and use the gopher as a mask to keep background transparent
    if showGopher:
        gopherImage = Image.open('./animation/gopher/gopheralive.png')
        fullImage.paste(gopherImage, (width, 4 * height), gopherImage)
    
    return fullImage

def convertTrapToImage(strEncoding: List[str], imageName: str, encoder: Encoding, save=False, showGopher=True, show=False, ext='pdf', tag=None, fitness=None):
    ''' Takes in the string encoding of a trap and converts it to an image '''
    cells = getCellsFromStr(strEncoding, encoder)
    images = getImages(cells, 12 * [0])
    finalImage = createImage(images, showGopher)
    width, height = images[0].width, images[0].height

    if showGopher: 
        gopherImage = Image.open('./animation/gopher/gopheralive.png')
        finalImage.paste(gopherImage, (width, 4 * height), gopherImage)

    # Add tag to the visual
    if tag:
        scale = 0.4
        if 10 <= int(tag) < 100:
            scale = 0.3
        elif 100 <= int(tag) < 1000:
            scale = 0.2

        xText, yText = width * 0.05, height * 4.05
        xNum, yNum = width * scale, height * 4.3

        textFont = ImageFont.truetype(font='~/Library/Fonts/Arial Unicode.ttf', size=180)
        numFont = ImageFont.truetype(font='~/Library/Fonts/Arial Unicode.ttf', size=375)

        ImageDraw.Draw(finalImage).text((xText, yText), 'Generation:', (255, 255, 255), font=textFont)
        ImageDraw.Draw(finalImage).text((xNum, yNum), tag, (255, 255, 255), font=numFont)

    # Add fitness to the visual
    if fitness is not None:
        scale = 2.05
        if len(fitness) == 3:
            scale = 2.2
        xText, yText = width * 2.05, height * 4.05
        xNum, yNum = width * scale, height * 4.3

        textFont = ImageFont.truetype(font='~/Library/Fonts/Arial Unicode.ttf', size=180)
        numFont = ImageFont.truetype(font='~/Library/Fonts/Arial Unicode.ttf', size=375)

        ImageDraw.Draw(finalImage).text((xText, yText), 'Fitness:', (255, 255, 255), font=textFont)
        ImageDraw.Draw(finalImage).text((xNum, yNum), fitness, (255, 255, 255), font=numFont)

    if save:
        finalImage.save(f'./images/traps/{imageName}.{ext}')

    if show:
        finalImage.show(title=f'{imageName}.png')
    
    return finalImage

def combineThreeImages(imgPaths, outputName, labels=['FUNCTIONAL', 'COHERENCE', 'MULTIOBJECTIVE'], save=False, show=False) -> Image.Image:
    ''' Takes 3 images and combines them into one (side by side). Can optionally add labels to the top. '''
    # Define image constants
    images = [Image.open(imgPath) for imgPath in imgPaths]
    width, height = images[0].width, images[0].height
    offset = 0

    # Define border/text constants
    lineWidth = 20; lineColor = 'black'
    textColor = 'white'

    # Allocate space for labels
    if labels:
        height += 400
        offset = 400

    # Create final image with relative dimensions
    finalImage = Image.new('RGB', (width * 3, height), color=(181,181,181))
    imgDraw = ImageDraw.Draw(finalImage)

    if labels:
        # Paste a dirt background behind the labels
        dirt = Image.open('./animation/dirt/dirtinactive.png')
        for i in range(3):
            for j in range(3):
                finalImage.paste(dirt, (width * i + j * width // 3, 0))

    # Paste each set of 3 images into the new image and draw a line between them
    for i, img in enumerate(images):
        finalImage.paste(img, (width * i, offset))
        imgDraw.line((width * i, 0, width * i, height), fill=lineColor, width=lineWidth)
    
    if labels:
        # Draw a line below the text and create the text font
        imgDraw.line((0, offset, 3 * width, offset), fill=lineColor, width=lineWidth)
        textFont = ImageFont.truetype(font='~/Library/Fonts/HP-Impact', size=300)

        # Write each label and center them inside their relative boxed
        for i, label in enumerate(labels):
            xCoord = width * (i + (1 - len(label) / width) / 4)
            textWidth, textHeight = imgDraw.textsize(label, font=textFont)

            xCoord = width * i + (width - textWidth) / 2
            yCoord = (offset - textHeight) / 2

            imgDraw.text((xCoord, yCoord), label, fill=textColor, font=textFont)

    if save:
        if not os.path.exists('./images/traps/blogCombined/'):
            os.mkdir('./images/traps/blogCombined/')
        
        finalImage.save(f'./images/traps/blogCombined/{outputName}.png')

    if show:
        finalImage.show(title=f'{outputName}.png')
    
    return finalImage

def createAnnotatedTrap(encoder: Encoding, show=True, save=False, output='annotated_trap'):
    ''' Creates a trap with annotations on each cell enumerating the indexes of its encoding '''
    TRAP_ENC = f'{encoder.from_canonical(TRAP)}'
    
    cells = getCellsFromStr(TRAP_ENC, encoder)
    images = getImages(cells, 12 * [0])
    width, height = images[0].width, images[0].height
    numRows, numCols = 4, 3

    finalImage = convertTrapToImage(TRAP_ENC, 'encoding_tagged', encoder)

    numFont = ImageFont.truetype(font='~/Library/Fonts/Arial Unicode.ttf', size=500)
    imgDraw = ImageDraw.Draw(finalImage)

    for row in range(0, numRows):
        imgDraw.line((0, row * height, numCols * width, row * height), 'black', 20)
        for col in range(0, numCols):
            if row == 0:
                imgDraw.line((col * width, 0, col * width, height * numRows), 'black', 20)

            num = row * numCols + col
            textWidth, textHeight = imgDraw.textsize(str(num), font=numFont)
            x = (width - textWidth) // 2 + col * width
            y = (height - textHeight) // 2 + row * height - 100

            imgDraw.text((x, y), str(num), 'white', numFont)

    if save:
        if not os.path.exists('./images/traps/'):
            os.mkdir('./images/traps/')
        
        finalImage.save(f'./images/traps/{output}.pdf')
    if show:
        finalImage.show(title=f'{output}.png')
    
    return finalImage

def createSplitTrap(index, encoder: Encoding, annotate=False, show=True, save=False, output='split_trap'):
    '''Creates a trap image with red lines splitting the two sides of recombination '''
    finalImage = None
    TRAP_ENC = f'{encoder.from_canonical(TRAP)}'
    if annotate:
        finalImage = createAnnotatedTrap(encoder, show=False)
    else:
        finalImage = convertTrapToImage(TRAP_ENC, 'annotated_trap', encoder, show=False)
    
    recombined = encoder.getPermutation()[:index]
    cells = getCellsFromStr(TRAP_ENC, encoder)
    images = getImages(cells, 12 * [0])
    width, height = images[0].width, images[0].height
    numRows, numCols = 4, 3

    imgDraw = ImageDraw.Draw(finalImage)

    for row in range(numRows):
        for col in range(numCols):
            currInd = row * numCols + col
            vertLine = (col * width, row * height, col * width, (row + 1) * height)
            horizLine = (col * width, row * height, (col + 1) * width, row * height)
            
            horizColor = 'red' if currInd not in recombined and currInd - 3 in recombined  else 'black'
            vertColor = 'red' if currInd not in recombined and currInd - 1 in recombined else 'black'

            if vertLine[0] == 0:
                vertColor = 'black'
            
            if horizLine[1] == 0:
                horizColor = 'black'

            imgDraw.line(vertLine, vertColor, 20)
            imgDraw.line(horizLine, horizColor, 20)

    if save:
        if not os.path.exists('./images/traps/'):
            os.mkdir('./images/traps/')
        
        finalImage.save(f'./images/traps/{output}.pdf')
    if show:
        finalImage.show(title=f'{output}.png')
    
    return finalImage

def simulateTrapInBrowser(trapEncoding, encoder: Encoding, hunger=0, intention=False, noAnimation=False, gopherState=[1, 4, 0, 1], frame = 0):
    """Takes in a list encoding and simulates the trap in the browser"""
    decodedList = encoder.decode(trapEncoding)
    simulationInfo = sim.simulateTrap(utils.createTrap(decodedList), intention, hunger=hunger, forceEnter=True)[:3]
    vis.writeTojs([simulationInfo], noAnimation, gopherState, frame)

    # opens the animation in the web browser
    webbrowser.open_new_tab("file://" + os.path.realpath("./animation/animation.html"))