import re
import base64
import markdown
import argparse
import os
import glob
import html
import time
import hashlib
from datetime import date
from shutil import copyfile

#str(int(time.time()))

from Indent import Indent


EXTENSION_LIST = ['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'markdown.extensions.attr_list']

questionID = 10000

def getTimeStamp():
    return str(int(time.time()))

def getVersionNumber(subVersion = 0):
    today = date.today()

    # dd/mm/YY
    version = today.strftime("%Y%m%d") + f'{subVersion:02d}'
    return version

def getQuestionId():
    global questionID
    questionID += 1
    return questionID - 1

def getQuestionHash():
    # myme type = $@NULL@$, size = 0
    return "da39a3ee5e6b4b0d3255bfef95601890afd80709"

def getFileHash(filename):
    file = filename # Location of the file (can be set a different way)
    BLOCK_SIZE = 65536 # The size of each read from the file

    file_hash = hashlib.sha1() # Create the hash object, can use something other than `.sha256()` if you wish
    filesize = os.stat(filename).st_size

    with open(file, 'rb') as f: # Open the file to read it's bytes
        fb = f.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
        while len(fb) > 0: # While there is still data being read from the file
            file_hash.update(fb) # Update the hash
            fb = f.read(BLOCK_SIZE) # Read the next block from the file

    #print ('Hash for', filename,'is',str(file_hash.hexdigest())) # Get the hexadecimal digest of the hash
    return (str(file_hash.hexdigest()), filesize)

class Question(object):
      
    fileID = 6359000              # unique ID per file    

    def __init__(self):
        self.workDir = '.'
        self.id = getQuestionId()
        self.mark = 0
        
    def setMark(self, str, default):
        sign = '@m'
        str = str.lower()
        idx = str.rfind(sign)
    
        if idx == -1:
            return (str, default)
    
        mark = str[idx + len(sign):].strip()
    
        try:
            return (str[:idx].strip(), float(mark))
        except Exception as e:
            print(e)
            return (str, default)

    def write(self, file, indent, line):
        return

    def getFileId():
        Question.fileID += 1
        return Question.fileID - 1

    def writeFile(self, xmlFile, indent, hash, filename = '.', size = 0, mimeType = '$@NULL@$', component = 'qtype_coderunner', filearea = 'datafile'):
        indent.write(xmlFile, '<file id="' + str(Question.getFileId()) + '">')
        indent.inc()
        indent.write(xmlFile, '<contenthash>' + hash + '</contenthash>')
        indent.write(xmlFile, '<contextid>542952</contextid>')
        indent.write(xmlFile, '<component>' + component + '</component>')
        indent.write(xmlFile, '<filearea>' + filearea + '</filearea>')
        indent.write(xmlFile, '<itemid>' + str(self.id) + '</itemid>')
        indent.write(xmlFile, '<filepath>/</filepath>')
        indent.write(xmlFile, '<filename>' + filename + '</filename>')
        indent.write(xmlFile, '<userid>$@NULL@$</userid>')
        indent.write(xmlFile, '<filesize>' + str(size) + '</filesize>')
        indent.write(xmlFile, '<mimetype>' + mimeType + '</mimetype>')
        indent.write(xmlFile, '<status>0</status>')
        indent.write(xmlFile, '<timecreated>' + getTimeStamp() + '</timecreated>')
        indent.write(xmlFile, '<timemodified>' + getTimeStamp() + '</timemodified>')
        
        source = '$@NULL@$'
        if mimeType == 'application/pdf':
            source = filename

        indent.write(xmlFile, '<source>' + source + '</source>')
        indent.write(xmlFile, '<author>$@NULL@$</author>')
        indent.write(xmlFile, '<license>$@NULL@$</license>')
        indent.write(xmlFile, '<sortorder>0</sortorder>')
        indent.write(xmlFile, '<repositorytype>$@NULL@$</repositorytype>')
        indent.write(xmlFile, '<repositoryid>$@NULL@$</repositoryid>')
        indent.write(xmlFile, '<reference>$@NULL@$</reference>')
        indent.dec()
        indent.write(xmlFile, '</file>')

class CodeRunner(Question):

    ID = 1
    defaultMark = 26.0

    def __init__(self, **kwargs):
        super(CodeRunner, self).__init__()
        self.text = kwargs['text']
        self.name = kwargs['name']
        self.fileList = kwargs['fileList']
        self.answer = kwargs['answer']
        self.workDir = '.'
        (self.name, self.mark) = self.setMark(self.name, CodeRunner.defaultMark)

        self.coderunnerId = CodeRunner.ID
        CodeRunner.ID += 1

 

    def writeExportFiles(self, file, args, root):

        indent = Indent()
        indent.inc()

        # 1. question text as entry
        self.writeFile(file, indent, getQuestionHash())


        # 2. each file as entry and as file
        for fileName in self.fileList:
            fullFileName = os.path.join(self.workDir, fileName)
            (fileHash, fileSize) = getFileHash(fullFileName)

            subDir = os.path.join(root, 'files', fileHash[:2])
            os.makedirs(subDir, exist_ok = True)

            # file name where to copy content
            storeName = os.path.join(subDir, fileHash)
            copyfile(fullFileName, storeName)

            print('\t',fullFileName, ' --> ', storeName)

            self.writeFile(file, indent, fileHash, fileName, fileSize, 'text/plain')



    def writeHtml(self, file, args):
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        footerText = ""
        try:
            footerFileName = args.footer #os.path.join(args.workDir, args.footer)
            footerFile = open(footerFileName, 'r')
            footerText = footerFile.read()
            footerText = markdown.markdown(footerText, extensions = EXTENSION_LIST)
            #print(footerText)
            footerFile.close()
        except:
            print("Footer file not available...")

        file.write('<div class="content"><div class="formulation"><h4 class="accesshide">' + self.name + '</h4><input type="hidden" name="q1172691:1_:sequencecheck" value="1" /><div class="qtext"><p>' + text + '</p>' + footerText + '</div></div></div>')
        #file.write('<p>' + text + '</p>' + footerText + '')

    def includeTemplate(self, xmlFile, indent, export = False):
        template = open("template.py", "r")

        if export:
            indent.write(xmlFile, '<template>')
        else:
            indent.write(xmlFile, '<template><![CDATA[')

        for line in template:
            if export:
                line = line.replace('<', '&lt;').replace('>','&gt;')
                xmlFile.write(line)
            else:
                xmlFile.write(line)

        if export:
            xmlFile.write('\n')
        else:
            xmlFile.write(']]>\n')
        indent.write(xmlFile, '</template>')
        template.close()

    def writeQuestion(self, xmlFile, indent, args):
        print("Saving coderunner question:", self.name,"\n\tUsing files", self.fileList)

        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        #print(text + "\n")

        indent.write(xmlFile, '<question type="coderunner">')
        indent.inc()
        indent.write(xmlFile, '<name>')
        indent.inc()
        indent.write(xmlFile, '<text><![CDATA[' + self.name + ']]></text>')
        indent.dec()
        indent.write(xmlFile, '</name>')
        indent.write(xmlFile, '<questiontext format="html">')
        indent.inc()

        footerText = ""
        try:
            footerFileName = args.footer #os.path.join(args.workDir, args.footer)
            footerFile = open(footerFileName, 'r')
            footerText = footerFile.read()
            footerText = markdown.markdown(footerText, extensions = EXTENSION_LIST)
            #print(footerText)
            footerFile.close()
        except:
            print("Footer file not available...")

        answer = self.getFullAnswer()

        indent.write(xmlFile, '<text><![CDATA[<p>' + text + '</p>' + footerText + ']]></text>')
        indent.dec()
        indent.write(xmlFile, '</questiontext>')
        indent.write(xmlFile, '<generalfeedback format="html">')
        indent.write(xmlFile, '<text></text>')
        indent.write(xmlFile, '</generalfeedback>')
        
        #self.mark = args.defaultPythonGrade

        indent.write(xmlFile, '<defaultgrade>' + str(self.mark) + '</defaultgrade>')
        indent.write(xmlFile, '<penalty>0.0000000</penalty>')
        indent.write(xmlFile, '<hidden>0</hidden>')
        indent.write(xmlFile, '<coderunnertype>python3_sandbox-1</coderunnertype>')
        indent.write(xmlFile, '<prototypetype>2</prototypetype>')
        indent.write(xmlFile, '<allornothing>1</allornothing>')
        indent.write(xmlFile, '<penaltyregime>0</penaltyregime>')
        indent.write(xmlFile, '<precheck>0</precheck>')
        indent.write(xmlFile, '<showsource>0</showsource>')
        indent.write(xmlFile, '<answerboxlines>30</answerboxlines>')
        indent.write(xmlFile, '<answerboxcolumns>100</answerboxcolumns>')
        indent.write(xmlFile, '<answerpreload>' + answer + '</answerpreload>')
        indent.write(xmlFile, '<useace>' + str(int(args.enableACE)) + '</useace>')
        indent.write(xmlFile, '<resultcolumns></resultcolumns>')

        self.includeTemplate(xmlFile, indent)

        indent.write(xmlFile, '<iscombinatortemplate>1</iscombinatortemplate>')
        indent.write(xmlFile, '<allowmultiplestdins>0</allowmultiplestdins>')
        indent.write(xmlFile, '<answer></answer>')
        indent.write(xmlFile, '<validateonsave>1</validateonsave>')
        indent.write(xmlFile, '<testsplitterre><![CDATA[|#<ab@17943918#@>#\\n|ms]]></testsplitterre>')
        indent.write(xmlFile, '<language>python3</language>')
        indent.write(xmlFile, '<acelang></acelang>')
        indent.write(xmlFile, '<sandbox></sandbox>')
        indent.write(xmlFile, '<grader>TemplateGrader</grader>')
        indent.write(xmlFile, '<cputimelimitsecs>30</cputimelimitsecs>')
        indent.write(xmlFile, '<memlimitmb>1000</memlimitmb>')
        indent.write(xmlFile, '<sandboxparams></sandboxparams>')
        indent.write(xmlFile, '<templateparams></templateparams>')
                        
        if len(self.fileList) > 0:  
            indent.write(xmlFile, '<hoisttemplateparams>1</hoisttemplateparams>')
            indent.write(xmlFile, '<twigall>1</twigall>')
            indent.write(xmlFile, '<uiplugin>ace</uiplugin>')
            indent.write(xmlFile, '<attachments>' + str(len(self.fileList) + 2) + '</attachments>')
            indent.write(xmlFile, '<attachmentsrequired>' + str(len(self.fileList)) + '</attachmentsrequired>')
            indent.write(xmlFile, '<maxfilesize>102400</maxfilesize>')
            indent.write(xmlFile, '<filenamesregex>stdin.txt|.*\.dat</filenamesregex>')
            indent.write(xmlFile, '<filenamesexplain>Optionally attach a file stdin.txt to be used as standard input and/or a data file with extension .dat for other use by the program.</filenamesexplain>')
            indent.write(xmlFile, '<displayfeedback>1</displayfeedback>')

            indent.write(xmlFile, '<testcases>')

        

        self.includeFileList(xmlFile, indent, args)

        indent.write(xmlFile, '</testcases>')
        indent.dec()
        indent.write(xmlFile, '</question>')    

    def includeFileList(self, xmlFile, indent, args):
        indent.inc()

        for fileName in self.fileList:
            fullFileName = os.path.join(self.workDir, fileName)
            getFileHash(fullFileName)
            try:
                #file = open(fullFileName, "r", encoding="utf-8")
                content = open(fullFileName, "r", encoding="utf-8").read()
            except:
                print('exception reading', fullFileName, 'trying to open it as ANSI file')
                content = open(fullFileName, "r").read()

            content = content.encode()
            result = base64.b64encode(content).decode()
            indent.write(xmlFile, '<file name="' + fileName + '" path="/" encoding="base64">' + result + '</file>')
            #print("including", fileName) #, "coded as", repr(result))

        indent.dec()

    def writeImportQuestion(self, xmlFile, indent, args):
        
        indent.write(xmlFile, '<question id="' + str(self.id) + '">')
        indent.inc()
        indent.write(xmlFile, '<parent>0</parent>')
        indent.write(xmlFile, '<name>' + self.name + '</name>')

        footerText = ""
        try:
            footerFileName = args.footer #os.path.join(args.workDir, args.footer)
            footerFile = open(footerFileName, 'r')
            footerText = footerFile.read()
            footerText = markdown.markdown(footerText, extensions = EXTENSION_LIST)
            #print(footerText)
            footerFile.close()
        except:
            print("Footer file not available...")

        text = html.escape(markdown.markdown(self.text,  extensions = EXTENSION_LIST))
        footerText = html.escape(markdown.markdown(footerText,  extensions = EXTENSION_LIST))

        indent.write(xmlFile, '<questiontext>' + text + '\n' + footerText + '</questiontext>')
        indent.write(xmlFile, '<questiontextformat>1</questiontextformat>')
        indent.write(xmlFile, '<generalfeedback></generalfeedback>')
        indent.write(xmlFile, '<generalfeedbackformat>1</generalfeedbackformat>')
        indent.write(xmlFile, '<defaultmark>' + str(self.mark) + '</defaultmark>')
        indent.write(xmlFile, '<penalty>0.0000000</penalty>')
        indent.write(xmlFile, '<qtype>coderunner</qtype>')
        indent.write(xmlFile, '<length>1</length>')
        indent.write(xmlFile, '<stamp>exam.polito.it+210211091420+FkseOz</stamp>')
        indent.write(xmlFile, '<version>exam.polito.it+210211091420+LOJKdo</version>')
        indent.write(xmlFile, '<hidden>0</hidden>')
        indent.write(xmlFile, '<timecreated>' + getTimeStamp() + '</timecreated>')
        indent.write(xmlFile, '<timemodified>' + getTimeStamp() + '</timemodified>')
        indent.write(xmlFile, '<createdby>374443</createdby>')
        indent.write(xmlFile, '<modifiedby>374443</modifiedby>')
        indent.write(xmlFile, '<plugin_qtype_coderunner_question>')
        indent.inc()
        indent.write(xmlFile, '<coderunner_options>')
        indent.inc()
        indent.write(xmlFile, '<coderunner_option id="' + str(self.coderunnerId) + '">')
        indent.inc()
        indent.write(xmlFile, '<coderunnertype>python3_sandbox-1-23</coderunnertype>')
        indent.write(xmlFile, '<prototypetype>2</prototypetype>')
        indent.write(xmlFile, '<allornothing>1</allornothing>')
        indent.write(xmlFile, '<penaltyregime>0</penaltyregime>')
        indent.write(xmlFile, '<precheck>0</precheck>')
        indent.write(xmlFile, '<showsource>0</showsource>')
        indent.write(xmlFile, '<answerboxlines>30</answerboxlines>')
        indent.write(xmlFile, '<answerboxcolumns>100</answerboxcolumns>')

        answer = self.getFullAnswer()

        indent.write(xmlFile, '<answerpreload>' + answer + '</answerpreload>')
        indent.write(xmlFile, '<useace>' + str(int(args.enableACE)) + '</useace>')
        indent.write(xmlFile, '<resultcolumns>$@NULL@$</resultcolumns>')

        self.includeTemplate(xmlFile, indent, export = True)


        indent.write(xmlFile, '<iscombinatortemplate>1</iscombinatortemplate>')
        indent.write(xmlFile, '<allowmultiplestdins>0</allowmultiplestdins>')
        indent.write(xmlFile, '<answer></answer>')
        indent.write(xmlFile, '<validateonsave>1</validateonsave>')
        indent.write(xmlFile, '<testsplitterre>|#&lt;ab@17943918#@&gt;#\\n|ms</testsplitterre>')
        indent.write(xmlFile, '<language>python3</language>')
        indent.write(xmlFile, '<acelang>$@NULL@$</acelang>')
        indent.write(xmlFile, '<sandbox>$@NULL@$</sandbox>')
        indent.write(xmlFile, '<grader>TemplateGrader</grader>')
        indent.write(xmlFile, '<cputimelimitsecs>30</cputimelimitsecs>')
        indent.write(xmlFile, '<memlimitmb>1000</memlimitmb>')
        indent.write(xmlFile, '<sandboxparams>$@NULL@$</sandboxparams>')
        indent.write(xmlFile, '<templateparams></templateparams>')
        indent.dec()
        indent.write(xmlFile, '</coderunner_option>')
        indent.dec()
        indent.write(xmlFile, '</coderunner_options>')
        indent.write(xmlFile, '<coderunner_testcases>')
        indent.write(xmlFile, '</coderunner_testcases>')
        indent.dec()
        indent.write(xmlFile, '</plugin_qtype_coderunner_question>')
        indent.write(xmlFile, '<question_hints>')
        indent.write(xmlFile, '</question_hints>')
        indent.write(xmlFile, '<tags>')
        indent.write(xmlFile, '</tags>')
        indent.dec()
        indent.write(xmlFile, '</question>')

    def getFullAnswer(self):
        answer = self.answer

        choices = ['# NO_DEFAULT_ANSWER', '#NO_DEFAULT_ANSWER']

        for marker in choices:
            if marker in answer:
                answer = answer.replace(marker, '')
                return answer

        for file in self.fileList:
            answer += '\n# compile to see contents of file ' + file
            answer += '\n# remember to use utf-8 encoding in the open to correctly read non-ascii caharacters'
            answer += '\nprint("Contents of ' + file + ':")'
            answer += '\nprint(open("' + file + '", "r", encoding="utf-8").read())'
            answer += '\nprint()\n'

        return answer;

class Essay(Question):

    ID = 1500
    defaultMark = 2.0

    def getId():
        Essay.ID += 1
        return Essay.ID - 1

    def __init__(self, **kwargs):
        super(Essay, self).__init__()
        self.text = kwargs['text']
        self.name = kwargs['name']
        self.answer = kwargs['answer']
        self.correct = kwargs['correct']
        self.workDir = '.'
        self.essayId = Essay.getId()
        (self.name, self.mark) = self.setMark(self.name, Essay.defaultMark)
        
    def writeExportFiles(self, file, args, root):
        pass

    def writeHtml(self, file, args):
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        answer = markdown.markdown(self.answer,  extensions = EXTENSION_LIST)
        file.write('<h2>Essay text</h2>')
        file.write('<p>' + text + '</p>')
        file.write('<h2>Essay answer</h2>')
        file.write('<p>' + answer + '</p>')
    
        #file.write('<div class="content"><div class="formulation"><h4 class="accesshide">Testo della domanda</h4><input type="hidden" name="q1172691:1_:sequencecheck" value="1" /><div class="qtext"><p>' + answer + '</p></div></div></div>')
    


    def writeImportQuestion(self, xmlFile, indent, args):
        
        indent.write(xmlFile, '<question id="' + str(self.id) + '">')
        indent.inc()
        indent.write(xmlFile, '<parent>0</parent>')
        indent.write(xmlFile, '<name>' + self.name + '</name>')

        # text from md to html in text version+
        text = html.escape(markdown.markdown(self.text,  extensions = EXTENSION_LIST))
        
        indent.write(xmlFile, '<questiontext>' + text + '</questiontext>')
        indent.write(xmlFile, '<questiontextformat>1</questiontextformat>')
        indent.write(xmlFile, '<generalfeedback></generalfeedback>')
        indent.write(xmlFile, '<generalfeedbackformat>1</generalfeedbackformat>')
        indent.write(xmlFile, '<defaultmark>' + str(self.mark) + '</defaultmark>')
        indent.write(xmlFile, '<penalty>0.0000000</penalty>')
        indent.write(xmlFile, '<qtype>essay</qtype>')
        indent.write(xmlFile, '<length>1</length>')
        indent.write(xmlFile, '<stamp>exam.polito.it+210211091420+03bWrP</stamp>')
        indent.write(xmlFile, '<version>exam.polito.it+210211091420+S5vzv2</version>')
        indent.write(xmlFile, '<hidden>0</hidden>')
        indent.write(xmlFile, '<timecreated>' + getTimeStamp() + '</timecreated>')
        indent.write(xmlFile, '<timemodified>' + getTimeStamp() + '</timemodified>')
        indent.write(xmlFile, '<createdby>374443</createdby>')
        indent.write(xmlFile, '<modifiedby>374443</modifiedby>')
        indent.write(xmlFile, '<plugin_qtype_essay_question>')
        indent.inc()
        indent.write(xmlFile, '<essay id="' + str(self.essayId) + '">')
        
        indent.inc()
        indent.write(xmlFile, '<responseformat>editor</responseformat>')
        indent.write(xmlFile, '<responserequired>0</responserequired>')
        indent.write(xmlFile, '<responsefieldlines>15</responsefieldlines>')
        indent.write(xmlFile, '<attachments>0</attachments>')
        indent.write(xmlFile, '<attachmentsrequired>0</attachmentsrequired>')

        correct = html.escape(markdown.markdown(self.correct,  extensions = EXTENSION_LIST))

        indent.write(xmlFile, '<graderinfo>' + correct + '</graderinfo>')
        indent.write(xmlFile, '<graderinfoformat>1</graderinfoformat>')

        answer = html.escape(markdown.markdown(self.answer,  extensions = EXTENSION_LIST))

        indent.write(xmlFile, '<responsetemplate>' + answer + '</responsetemplate>')
        indent.write(xmlFile, '<responsetemplateformat>1</responsetemplateformat>')
        indent.dec()
        indent.write(xmlFile, '</essay>')
        indent.dec()
        indent.write(xmlFile, '</plugin_qtype_essay_question>')
        indent.write(xmlFile, '<question_hints>')
        indent.write(xmlFile, '</question_hints>')
        indent.write(xmlFile, '<tags>')
        indent.write(xmlFile, '</tags>')
        indent.dec()
        indent.write(xmlFile, '</question>')
        

    def writeQuestion(self, xmlFile, indent, args):
        print("Saving essay:", self.name)

        # header
        indent.write(xmlFile, "<question type=\"essay\">")
        indent.inc()
        indent.write(xmlFile, "<name>")
        indent.inc()
        indent.write(xmlFile, "<text> " + self.name + " </text>")
        indent.dec()
        indent.write(xmlFile, "</name>")

        # text
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        indent.write(xmlFile, "<questiontext format = \"html\">")
        indent.write(xmlFile, "<text><![CDATA[<p>" + text + "</p>]]></text>")
        indent.write(xmlFile, "</questiontext>");
        indent.write(xmlFile, "<generalfeedback format = \"html\">")
        indent.write(xmlFile, "<text></text>");
        indent.write(xmlFile, "</generalfeedback>")

        # parameters
        indent.write(xmlFile, "<defaultgrade> " + str(self.mark) + " </defaultgrade>")
        indent.write(xmlFile, "<penalty> 0 </penalty>")
        indent.write(xmlFile, "<hidden> 0 </hidden>")

        # write individual parameters
        
        answer = markdown.markdown(self.answer,  extensions = EXTENSION_LIST)
        indent.write(xmlFile, "<responseformat>editor</responseformat>")
        indent.write(xmlFile, "<responserequired>0</responserequired>")
        indent.write(xmlFile, "<responsefieldlines>15</responsefieldlines>")
        indent.write(xmlFile, "<attachments>0</attachments>")
        indent.write(xmlFile, "<attachmentsrequired>0</attachmentsrequired>")
        indent.write(xmlFile, "<graderinfo format=\"html\">")
        indent.write(xmlFile, "<text></text>")
        indent.write(xmlFile, "</graderinfo>")
        indent.write(xmlFile, "<responsetemplate format=\"html\">")
        indent.write(xmlFile, "<text><![CDATA[<p> " + answer + " </p>]]></text>")
        indent.write(xmlFile, "</responsetemplate>")

        # close
        indent.dec()
        indent.write(xmlFile, "</question>");


class CheatSheet(Question):


    def __init__(self, *argv):
        super(CheatSheet, self).__init__()

        self.dataDir = './cheatsheet'
        self.NORMAL = 'cheatsheet.pdf'
        self.ACCESSIBLE = 'accessible_cheatsheet.pdf'
        self.cheatsheetId = Essay.getId()
        
        self.text = (
            '<ul><li><a href="@@PLUGINFILE@@/' + self.NORMAL + ''
            '" class="md-opjjpmhoiojifppkkcdabiobhakljdgm_doc" target="_blank">File PDF con le funzioni di Python</a></li>' 
            '<li><a href="@@PLUGINFILE@@/' + self.ACCESSIBLE + ''
            '" class="md-opjjpmhoiojifppkkcdabiobhakljdgm_doc" target="_blank">File PDF con le funzioni di Python (versione accessibile)</a><br></li></ul>'
        )

    # fro the html control file
    def writeHtml(self, file, args):
        file.write('<h1>Cheat sheet PDF</h1>')
        
    # for creating backup file
    def writeImportQuestion(self, xmlFile, indent, args):
        
        indent.write(xmlFile, '<question id="' + str(self.cheatsheetId) + '">')
        indent.inc()
        indent.write(xmlFile, '<parent>0</parent>')
        indent.write(xmlFile, '<name>Cheat sheet PDF</name>')

        text = self.text.replace('<', '&lt;').replace('>','&gt;')

        indent.write(xmlFile, '<questiontext>' + text + '</questiontext>')
        indent.write(xmlFile, '<questiontextformat>1</questiontextformat>')
        indent.write(xmlFile, '<generalfeedback></generalfeedback>')
        indent.write(xmlFile, '<generalfeedbackformat>1</generalfeedbackformat>')
        indent.write(xmlFile, '<defaultmark>0.0000000</defaultmark>')
        indent.write(xmlFile, '<penalty>0.0000000</penalty>')
        indent.write(xmlFile, '<qtype>description</qtype>')
        indent.write(xmlFile, '<length>0</length>')
        indent.write(xmlFile, '<stamp>exam.polito.it+210121094425+9hmxuP</stamp>')
        indent.write(xmlFile, '<version>exam.polito.it+210125130739+v09hOT</version>')
        indent.write(xmlFile, '<hidden>0</hidden>')
        indent.write(xmlFile, '<timecreated>' + getTimeStamp() + '</timecreated>')
        indent.write(xmlFile, '<timemodified>' + getTimeStamp() + '</timemodified>')
        indent.write(xmlFile, '<createdby>374443</createdby>')
        indent.write(xmlFile, '<modifiedby>374443</modifiedby>')
        indent.write(xmlFile, '<question_hints>')
        indent.write(xmlFile, '</question_hints>')
        indent.write(xmlFile, '<tags>')
        indent.write(xmlFile, '</tags>')
        indent.dec()
        indent.write(xmlFile, '</question>')

    # for moodle XML import file
    def writeQuestion(self, xmlFile, indent, args):
        pass
        
    def writeExportFiles(self, file, args, root):

        indent = Indent()
        indent.inc()

        fileList = [self.NORMAL, self.ACCESSIBLE]
            
        self.writeFile(file, indent, getQuestionHash(), mimeType = 'document/unknown', component = 'question', filearea = 'questiontext')

        # 2. each file as entry and as file
        for fileName in fileList:
            fullFileName = os.path.join(self.dataDir, fileName)
            (fileHash, fileSize) = getFileHash(fullFileName)

            subDir = os.path.join(root, 'files', fileHash[:2])
            os.makedirs(subDir, exist_ok = True)

            # file name where to copy content
            storeName = os.path.join(subDir, fileHash)
            copyfile(fullFileName, storeName)

            print('\t',fullFileName, ' --> ', storeName)
            
            self.writeFile(file, indent, fileHash, fileName, fileSize, 'application/pdf', component = 'question', filearea = 'questiontext')

class MultiChoice(Question):

    def __init__(self, name, text, answer, questions):
        super(MultiChoice, self).__init__()

        self.questions = questions
        self.text = text
        self.name = name
        self.answer = answer


    # fro the html control file
    def writeHtml(self, file, args):
        pass

    # for creating backup file
    def writeImportQuestion(self, xmlFile, indent, args):
        pass

    # for moodle XML import file
    def writeQuestion(self, xmlFile, indent, args):
        pass
        
    def writeExportFiles(self, file, args, root):
        pass

