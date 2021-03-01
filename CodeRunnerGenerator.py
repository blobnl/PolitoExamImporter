import re
import base64
import markdown
import argparse
import os
import glob

from Indent import Indent
from QuestionTypes import Essay, CodeRunner, CheatSheet, MultiChoice
from QuestionCategories import CategoryInfo,str2bool
from MoodleImporterGenerator import MoodleImport



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



    file = open(inputFileName, "r", encoding="utf-8")
    lines = file.readlines()

    text = ""
    content = ""
    fileList = []
    name = ""
    answer = ""
    newQuestion = False
    questionType = ""
    questionTypes = {"QUESTION": CodeRunner, "ESSAY": Essay, 'CHEATSHEET' : CheatSheet, 'MULTICHOICE' : MultiChoice}

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
        elif lineCL in questionTypes:
            content = lineCL
            if newQuestion:
                #writeQuestion(xmlFile, indent, name, text, answer, fileList, args)
                newQuestion = questionTypes[questionType](name, text, answer, fileList)
                newQuestion.workDir = args.workDir
                questionList.append(newQuestion)
                text = ""
                fileList = []
                name = ""
                answer = ""
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

            
    newQuestion = questionTypes[questionType](name, text, answer, fileList)
    newQuestion.workDir = args.workDir
    questionList.append(newQuestion)
    print('Trovate',len(questionList),'domande')
    return questionList
            
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

    return parser.parse_args()

def storeQuestionList(questionList, args):
    try:
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

    except Exception as e:
        print('Error in craeting questions for', xmlFile,e)

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



def main():

    args = parseArguments()
    
    # setting default class parameters
    Essay.defaultMark = args.defaultEssayGrade
    CodeRunner.defaultMark = args.defaultPythonGrade
    CategoryInfo.CanReDo = args.canRedoQuiz

    workDir = args.workDir
    mainCategory = args.category
    #print(args)

    if args.createMBZ:
        moodle = MoodleImport(args)

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
            print('processing',subDir, 'category', category)
            questionList = readQuestions(args)
            if args.canRedoQuiz:
                categories.append(CategoryInfo(subDir, readOnlyDescription = True))
            else:
                categories.append(CategoryInfo(subDir))
            questions.append((args.category,questionList))
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

    
    if args.createUniqueImport and args.processSubDirs:
        print('\nMerging all files into a unique import')
        args.workDir = workDir
        args.category = mainCategory
        createUniqueImport(args)


main()
