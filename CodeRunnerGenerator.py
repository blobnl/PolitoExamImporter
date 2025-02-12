import re
import base64
import markdown
import argparse
import os
import glob

from Indent import Indent
from QuestionTypes import Essay, CodeRunner, CheatSheet, MultiChoice, CrownLab, TrueFalse
from QuestionCategories import CategoryInfo,str2bool
import MoodleImporterGenerator

from collections import Counter
import langdetect

from docx import Document
from docx.shared import RGBColor
from docx.shared import Pt



#from MoodleImporterGenerator import MoodleImport



EXTENSION_LIST = ['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'markdown.extensions.attr_list']




def writeHeader(xmlFile, indent, category):
    indent.write(xmlFile, '<?xml version="1.0" encoding="UTF-8"?>')
    indent.write(xmlFile, '<quiz>')
    
    indent.write(xmlFile, '<question type = "category">')
    indent.inc()
    indent.write(xmlFile, '<category>')
    indent.inc()
    indent.write(xmlFile, '<text>' + category + '</text>')
    indent.dec()
    indent.write(xmlFile, '</category>')
    indent.dec()
    indent.write(xmlFile, '</question>')

    
def writeFooter(xmlFile, indent):
    indent.write(xmlFile, '</quiz>')

def readQuestions(args):

    inputFileName = os.path.join(args.workDir, args.questionFile)

    '''
    file = open(inputFileName, "r")
    rawdata = file.read()
    result = chardet.detect(bytearray(rawdata.encode()))
    charenc = result['encoding']
    file.close()

    print(inputFileName, "detected encoding:", charenc)
    '''



    try:
        file = open(inputFileName, "r", encoding="utf-8")
    except Exception as e:
        print("\tError in opening", inputFileName)
        print("\tError:", str(e))
        return None

    lines = file.readlines()
    
    languageDetected = langdetect.detect(''.join(lines))
    print(f'Language detected: {languageDetected}')

    text = ''
    content = ''
    fileList = []
    name = ''
    answer = ''
    correct = ''
    destination = ''
    newQuestion = False
    questionType = ''
    questionTypes = {"QUESTION": CrownLab, "ESSAY": Essay, 'CHEATSHEET' : CheatSheet, 'MULTICHOICE' : MultiChoice, 'TRUEFALSE' : TrueFalse}

    questionList = []

    for line in lines:
        BOM = '\ufeff'
        lineCL = line.strip().strip(BOM)
        if lineCL == "TEXT":
            content = lineCL
        elif lineCL == "FILES":
            content = lineCL
        elif lineCL == "ANSWER":
            content = lineCL
        elif lineCL == "CORRECT":
            content = lineCL
        elif lineCL == "DESTINATION":
            content = lineCL
        elif lineCL in questionTypes:
            content = lineCL
            if newQuestion:
                #print(questionType, name)
                addedQuestion = addQuestion(questionList, args, questionTypes[questionType], 
                                            **{'name':name, 
                                               'text':text, 
                                               'answer':answer, 
                                               'fileList':fileList, 
                                               'correct':correct, 
                                               'destination':destination,
                                               'language':languageDetected})
                addedQuestion.positionInQuiz = len(questionList)

                # cleaning fields for next question
                text = ''
                fileList = []
                name = ''
                answer = ''
                correct = ''

            newQuestion = True
            questionType = lineCL
        elif content == "TEXT":
            text += line
        elif content == "FILES":
            if lineCL != "":
                fileList.append(lineCL)
        elif content in questionTypes:
            if lineCL != "":
                name = lineCL
        elif content == "ANSWER":
            answer += line
        elif content == "CORRECT":
            correct += line
        elif lineCL == "DESTINATION":
            destination = line
        elif content == "CHEATSHEET":
            if lineCL != "":
                text = lineCL

    
    addedQuestion = addQuestion(questionList, args, questionTypes[questionType], 
                                **{'name':name, 'text':text, 'answer':answer, 
                                   'fileList':fileList, 'correct':correct, 'destination':destination,
                                   'language':languageDetected})
    addedQuestion.positionInQuiz = len(questionList)

    print('Trovate',len(questionList),'domande')
    return questionList
            
def addQuestion(questionList, args, questionClass, **kwargs):

    newQuestion = None

    try:
        if (kwargs['name'] == '' or kwargs['text'] == '') and (not questionClass is CheatSheet):
            print('Warning: empty question', type(questionClass), kwargs['name'], kwargs['text'])

        newQuestion = questionClass(**kwargs)
        newQuestion.workDir = args.workDir
        questionList.append(newQuestion)
    except Exception as e:
        print('Error in creating question', type(questionClass), kwargs['name'], kwargs['text'], e)

    return newQuestion


def writeHtmlHeader(file, args):
    file.write('<!DOCTYPE html>')
    file.write('<html>')
    file.write('<head>')
    file.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8">')
    file.write('<title>' + args.category +'</title>')
    file.write('<link rel="stylesheet" type="text/css" href="https://exam.polito.it/theme/yui_combo.php?rollup/3.17.2/yui-moodlesimple-min.css" />')
    file.write('</head>')
    file.write('<body>')

    
def writeHtmlFooter(file):
    file.write('</body>')
    file.write('</html>')


def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml', type=str, default='demo.xml', help='output moodle xml file')
    parser.add_argument('--questionFile', type=str, default='domande.txt', help='input txt question file')
    parser.add_argument('--footer', type=str, default='footer.txt', help='footer txt for questions')
    parser.add_argument('--workDir', type=str, default='', help='working dir')
    parser.add_argument('--category', type=str, default='', help='"Default per 14BHDLZ_16"')
    parser.add_argument('--enableACE', type=str2bool, default=False, help='Enabling ACE ditor (default is False)')
    parser.add_argument('--defaultPythonGrade', type=float, default=26.0, help='Python grade (default is 26)')
    parser.add_argument('--defaultEssayGrade', type=float, default=2.0, help='Essay grade (default is 2)')
    parser.add_argument('--createUniqueImport', type=str2bool, default=False, help='Create unique import file (default is False)')
    parser.add_argument('--processSubDirs', type=str2bool, default=False, help='Processing each subdir (default is False)')
    parser.add_argument('--merge', type=str2bool, default=False, help='Merging all questions from multiple dirs into a unique file (default is False)')
    parser.add_argument('--createMBZ', type=str2bool, default=False, help='Create moodle importer (default is False)')
    parser.add_argument('--canRedoQuiz', type=str2bool, default=False, help='Create moodle importer (default is False)')
    parser.add_argument('--createDoc', type=str2bool, default=False, help='Create doc export')

    return parser.parse_args()

def set_default_font(doc, font_name="Aptos", font_size=11):
    """
    Imposta il font predefinito per il documento modificando lo stile 'Normal'.

    :param doc: Oggetto Document di python-docx
    :param font_name: Nome del font (default: "Aptos")
    :param font_size: Dimensione del font in pt (default: 11)
    """
    style = doc.styles['Normal']
    font = style.font
    font.name = font_name
    font.size = Pt(font_size)

def storeQuestionList(questionList, args):
    try:
        indent = Indent()
        xmlFile = open(os.path.join(args.workDir, args.xml), "w", encoding="utf-8")
        htmlFile = open(os.path.join(args.workDir, args.xml + '.html'), "w", encoding="utf-8")
        if args.createDoc:
            #txtFile = open(os.path.join(args.workDir, args.xml + '.txt'), "w", encoding="utf-8")
            docFile = os.path.join(args.workDir, args.xml + '.docx')
            doc = Document()
            set_default_font(doc, font_name="Aptos", font_size=11)

        writeHeader(xmlFile, indent, args.category)
        writeHtmlHeader(htmlFile, args)
        indent.inc()

        counter = 0
        for question in questionList:
            if type(question).__name__ in ['Essay', 'TrueFalse', 'MultiChoice']:
                counter += 1
                
            question.writeQuestion(xmlFile, indent, args)
            question.writeHtml(htmlFile, args)
            if args.createDoc:
                #print(f'write {question}')
                question.writeTxt(doc, args, counter)

        indent.dec()
        writeFooter(xmlFile, indent)
        writeHtmlFooter(htmlFile)
        xmlFile.close()
        htmlFile.close()
        if args.createDoc:
            #txtFile.close()
            doc.save(docFile)

    except Exception as e:
        print('Error in craeting questions for', xmlFile,e)

def storeHTMLPreview(questionList, args):
    try:
        indent = Indent()
        htmlFile = open(os.path.join(args.workDir, args.xml + '.html'), "w", encoding="utf-8")

        writeHtmlHeader(htmlFile, args)
        indent.inc()

        for question in questionList:
            question.writeHtml(htmlFile, args)

        indent.dec()
        writeHtmlFooter(htmlFile)
        htmlFile.close()

    except Exception as e:
        print('Error in craeting questions for', htmlFile,e)

def processDir(args):
    try:
        questionList = readQuestions(args)
        storeQuestionList(questionList, args)
        '''
        indent = Indent()
        xmlFile = open(os.path.join(args.workDir, args.xml), "w", encoding="utf-8")
        htmlFile = open(os.path.join(args.workDir, args.xml + '.html'), "w", encoding="utf-8")

        writeHeader(xmlFile, indent, args.category)
        writeHtmlHeader(htmlFile, args)
        indent.inc()

        for question in questionList:
            question.writeQuestion(xmlFile, indent, args)
            question.writeHtml(htmlFile, args)

        indent.dec()
        writeFooter(xmlFile, indent)
        writeHtmlFooter(htmlFile)
        xmlFile.close()
        htmlFile.close()
        '''

    except Exception as e:
        print('Error in processing dir', args.workDir)
        print(e)
        print('skipping to next entry')

def createUniqueImport(args):
        root = args.workDir
        dirList = [ f.path for f in os.scandir(root) if f.is_dir() ]
        args.xml = args.category + '.xml'
        
        # collecting file contents

        lines = []
        for subDir in dirList:
            for file in os.listdir(subDir):
                if file.endswith(".xml"):
                    fullPath = os.path.join(subDir, file)
                    print(fullPath)
                    contents = open(fullPath,'r', encoding="utf-8").readlines()

                    lines += contents

        # cleaning files, keeping header of xml quiz file
        cleaned = lines[:2]

        for i in range(len(lines) - 1):

            line = lines[i]

            # removing intermediate quiz definition tags
            if '<?xml' in line or '<quiz>' in line or '</quiz>' in line:
                continue

            cleaned.append(line)

        # close quiz
        cleaned.append(lines[-1])
        fileName = os.path.join(root, args.xml)
        print('Creating merged file', fileName)
        xmlFile = open(fileName, "w", encoding="utf-8")
        xmlFile.writelines(cleaned)
        xmlFile.close()

def isComputerScience(args):
    return 'informatica' in args.xml.lower()

def checkQuiz(questionList):
    stdClassList = ['Essay', 'TrueFalse', 'Essay', 'Essay', 'Essay', 'CheatSheet', 'CrownLab']
    classNames = [obj.__class__.__name__ for obj in questionList]
    if classNames != stdClassList:
        print('Compito identificato come comito di Informatica, In questo case,  errore nel file delle domande')
        # Count occurrences of each class name
        actual_count = Counter(classNames)
        expected_count = Counter(stdClassList)

        # Find missing and extra items
        missing = {key: expected_count[key] - actual_count[key] 
                   for key in expected_count if expected_count[key] > actual_count[key]}
        extra = {key: actual_count[key] - expected_count[key] 
                 for key in actual_count if actual_count[key] > expected_count[key]}
        
        if missing:
            print(f'Missing: {missing}')
        if extra:
            print(f'Extra; {extra}')
            
        abort = input('Abort program (y/n)? ')
        if 'y' in abort.lower():
            exit()

def CRGmain():

    args = parseArguments()
    
    # setting default class parameters
    Essay.defaultMark = args.defaultEssayGrade
    CodeRunner.defaultMark = args.defaultPythonGrade
    CategoryInfo.CanReDo = args.canRedoQuiz

    workDir = args.workDir
    mainCategory = args.category
    #print(args)

    if args.createMBZ:
        moodle = MoodleImporterGenerator.MoodleImport(args)

    if args.processSubDirs and not args.merge or args.createMBZ:
        root = args.workDir
        dirList = [ f.path for f in os.scandir(root) if f.is_dir() ]
        questions = []
        categories = []
        for subDir in dirList:
            currentDir = subDir
            category = os.path.basename(os.path.normpath(subDir))
            
            if category == mainCategory:
                continue

            args.workDir = currentDir
            args.category = mainCategory + '/' + category
            print('processing',category)
            questionList = readQuestions(args)

            if questionList is None:
                continue

            if args.canRedoQuiz:
                categories.append(CategoryInfo(subDir, readOnlyDescription = True))
            else:
                categories.append(CategoryInfo(subDir))
            questions.append((args.category,questionList))
            storeHTMLPreview(questionList, args)
            if isComputerScience(args):
                checkQuiz(questionList)
            #processDir(args)

        for (idx,block) in enumerate(questions):
            (args.category, questionList) = block

            if args.createMBZ:
                moodle.addQuiz(args.category, questionList, categories[idx])
            else:
                storeQuestionList(questionList, args)

        if args.createMBZ:
            args.workDir = workDir
            args.category = mainCategory
            moodle.flush()

    elif args.processSubDirs and args.merge and not args.createMBZ:
        root = args.workDir
        args.xml = "merged.xml"
        questionList = []
        dirList = [ f.path for f in os.scandir(root) if f.is_dir() ]
        for subDir in dirList:
            currentDir = subDir
            category = args.category
            args.workDir = currentDir
            print('processing',subDir, 'category', category)
            questionList = questionList + readQuestions(args)

        args.workDir = root #'.'
        storeQuestionList(questionList, args)
    else:
        processDir(args)

    '''
    if args.createUniqueImport and args.processSubDirs:
        print('\nMerging all files into a unique import')
        args.workDir = workDir
        args.category = mainCategory
        createUniqueImport(args)
    '''


if __name__ == "__main__":
    CRGmain()



