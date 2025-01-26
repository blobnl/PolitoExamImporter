import re
import base64
import codecs
import markdown
import argparse
import os
import glob
import html
import time
import hashlib
from datetime import date
from shutil import copyfile, rmtree, copytree, make_archive
from pathlib import Path

#str(int(time.time()))

from Indent import Indent


EXTENSION_LIST = ['markdown.extensions.tables', 'markdown.extensions.fenced_code', 'markdown.extensions.attr_list']

questionID = 10000

def textFile2base64(fileName):
    try:
        content = open(fullFileName, "r", encoding="utf-8").read()
    except:
        print('exception reading', fullFileName, 'trying to open it as ANSI file')
        content = open(fullFileName, "r").read()

    content = content.encode()
    result = base64.b64encode(content).decode()

    return result

def binaryFile2base64(fileName):
    content = open(fileName, "rb").read()
    result_enc = base64.b64encode(content)
    # then, removing the b'....' characters of teh textual encoding of byte arrays
    return str(result_enc)[2:-1]


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
    MoodleVersion = 3.1

    def __init__(self):
        self.workDir = '.'
        self.id = getQuestionId()
        self.mark = 0
        self.positionInQuiz = 0
        
    def setMark(self, str, default):
        sign = '@m'
        str = str.lower()
        idx = str.rfind(sign)
    
        if idx == -1:
            return (str, default)
    
        mark = str[idx + len(sign):].split(maxsplit = 1)[0].strip()
    
        try:
            return (str[:idx].strip(), float(mark))
        except Exception as e:
            print(e)
            return (str, default)

    def write(self, file, indent, line):
        return
    
    def writeTxt(self, txtFile, args):
        return

    def writeXml(self, file, indent, line):
        pass

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

    '''
        function for writing the XML file for moodle import into question bank
    '''
    def writeQuestion(self, xmlFile, indent, args):
        pass

    '''
        function for writing the XML for the moodle backup
    '''
    def writeImportQuestion(self, xmlFile, indent, args):
        pass

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

        file.write('<div class="content"><div class="formulation"><h4 class="accesshide">' + self.name + '</h4><input type="hidden" name="q1172691:1_:sequencecheck" value="1" /><div class="qtext"><p dir="ltr" style="text-align: left;">' + text + '</p>' + footerText + '</div></div></div>')
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

        indent.write(xmlFile, '<text><![CDATA[<p dir="ltr" style="text-align: left;">' + text + '</p>' + footerText + ']]></text>')
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
            indent.write(xmlFile, '<filenamesregex>stdin.txt|.*\\.dat</filenamesregex>')
            indent.write(xmlFile, '<filenamesexplain>Optionally attach a file stdin.txt to be used as standard input and/or a data file with extension .dat for other use by the program.</filenamesexplain>')
            indent.write(xmlFile, '<displayfeedback>1</displayfeedback>')

            indent.write(xmlFile, '<testcases>')

        

        self.includeFileList(xmlFile, indent, args)

        indent.write(xmlFile, '</testcases>')
        indent.dec()
        indent.write(xmlFile, '</question>')    

    def includeFileList(self, xmlFile, indent, args):
        indent.inc()

        fullFileList = []
        #for fileName in self.fileList:
        #    fullFileList.append(os.path.join(self.workDir, fileName))


        for fileName in fullFileList:
            fullFileName = os.path.join(self.workDir, fileName)
            getFileHash(fullFileName)
            result = textFile2base64()
            #try:
            #    #file = open(fullFileName, "r", encoding="utf-8")
            #    content = open(fullFileName, "r", encoding="utf-8").read()
            #except:
            #    print('exception reading', fullFileName, 'trying to open it as ANSI file')
            #    content = open(fullFileName, "r").read()

            #content = content.encode()
            #result = base64.b64encode(content).decode()
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
        file.write('<p dir="ltr" style="text-align: left;">' + text + '</p>')
        file.write('<h2>Essay answer</h2>')
        file.write('<p dir="ltr" style="text-align: left;">' + answer + '</p>')
    
        #file.write('<div class="content"><div class="formulation"><h4 class="accesshide">Testo della domanda</h4><input type="hidden" name="q1172691:1_:sequencecheck" value="1" /><div class="qtext"><p>' + answer + '</p></div></div></div>')
    

    
    def writeTxt(self, txtFile, args):
        txtFile.write(f'\n{self.text}\n')

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
        indent.write(xmlFile, "<text> " + f"{self.positionInQuiz:02d} {self.name}" + " </text>")
        indent.dec()
        indent.write(xmlFile, "</name>")

        # text
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        indent.write(xmlFile, "<questiontext format = \"html\">")
        indent.write(xmlFile, '<text><![CDATA[<p dir="ltr" style="text-align: left;">' + text + '</p>]]></text>')
        indent.write(xmlFile, "</questiontext>")
        indent.write(xmlFile, "<generalfeedback format = \"html\">")
        indent.write(xmlFile, "<text></text>")
        indent.write(xmlFile, "</generalfeedback>")

        # parameters
        indent.write(xmlFile, "<defaultgrade> " + str(self.mark) + " </defaultgrade>")
        indent.write(xmlFile, "<penalty> 0 </penalty>")
        indent.write(xmlFile, "<hidden> 0 </hidden>")

        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, "<idnumber></idnumber>")

        # write individual parameters
        
        answer = markdown.markdown(self.answer,  extensions = EXTENSION_LIST)
        indent.write(xmlFile, "<responseformat>editor</responseformat>")
        indent.write(xmlFile, "<responserequired>0</responserequired>")
        indent.write(xmlFile, "<responsefieldlines>15</responsefieldlines>")

        
        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, "<minwordlimit></minwordlimit>")
            indent.write(xmlFile, "<maxwordlimit></maxwordlimit>")

        indent.write(xmlFile, "<attachments>0</attachments>")
        indent.write(xmlFile, "<attachmentsrequired>0</attachmentsrequired>")
        # grader info
        
        correct = html.escape(markdown.markdown(self.correct,  extensions = EXTENSION_LIST))

        indent.write(xmlFile, "<graderinfo format=\"html\">")
        indent.write(xmlFile, '<text><![CDATA[<p dir="ltr" style="text-align: left;"> ' + correct + ' </p>]]></text>')
        indent.write(xmlFile, "</graderinfo>")
        indent.write(xmlFile, "<responsetemplate format=\"html\">")

        if Question.MoodleVersion >= 3.0:
            answer = answer.replace('<p>','<br>').replace('</p>', '')


        indent.write(xmlFile, '<text><![CDATA[' + answer + ']]></text>')
        indent.write(xmlFile, "</responsetemplate>")

        # close
        indent.dec()
        indent.write(xmlFile, "</question>")

class CheatSheet(Question):


    def __init__(self, **kwargs):
        super(CheatSheet, self).__init__()

        self.dataDir = './cheatsheet'
        self.cheatsheetId = Essay.getId()
        self.name = 'Cheatsheet'

        self.english = False
        if 'eng' in kwargs['name'].lower():
            self.english = True
        
        if not self.english:
            self.NORMAL = 'CS.pdf'
            self.ACCESSIBLE = 'CSA.pdf'
            self.text = ('<p dir="ltr" style="text-align: left;"><b>Documentazione online di Python</b> (<a href="https://docs.python.org/3/" target="_blank">python.org</a>)</p>'
                '<p dir="ltr" style="text-align: left;"><b>CheatSheet </b><a href="@@PLUGINFILE@@/' + self.NORMAL + '" target="_blank">PDF</a></p>'
                '<p dir="ltr" style="text-align: left;"><b>CheatSheet (versione accessibile)</b> <a href="@@PLUGINFILE@@/' + self.ACCESSIBLE + '" target="_blank">PDF</a><br></p>')
        else:
            self.NORMAL = 'CSeng.pdf'
            self.ACCESSIBLE = 'CSAeng.pdf'
        
            self.text = ('<p dir="ltr" style="text-align: left;"><b>Online Python documentation</b> (<a href="https://docs.python.org/3/" target="_blank">python.org</a>)</p>'
                '<p dir="ltr" style="text-align: left;"><b>CheatSheet </b><a href="@@PLUGINFILE@@/' + self.NORMAL + '" target="_blank">PDF</a></p>'
                '<p dir="ltr" style="text-align: left;"><b>CheatSheet (accessible version)</b> <a href="@@PLUGINFILE@@/' + self.ACCESSIBLE + '" target="_blank">PDF</a><br></p>')
        

    # fro the html control file
    def writeHtml(self, file, args):
        file.write('<h1>Cheat sheet PDF</h1>')
        


    # for creating backup file
    def writeImportQuestion(self, xmlFile, indent, args):
        
        indent.write(xmlFile, '<question id="' + str(self.cheatsheetId) + '">')
        indent.inc()
        indent.write(xmlFile, '<parent>0</parent>')
        indent.write(xmlFile, f'<name>{self.positionInQuiz:02d} Cheat sheet PDF </name>')

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
        print("Saving Cheatsheet question:", self.name)

        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        #print(text + "\n")

      
        indent.write(xmlFile, '<question type="description">')
        indent.inc()
        indent.write(xmlFile, f'<name><text>{self.positionInQuiz:02d} Documentazione Python</text></name>')
        indent.write(xmlFile, '<questiontext format="html">')
        indent.inc()
        
        indent.write(xmlFile, '<text><![CDATA[' + self.text + ']]></text>')
        
        
        #''' saving binary files:
        # something wrong with the first two bytes that should not be included into the PDF file (otherwise it looks corrupted)
        content = open(os.path.join(self.dataDir, self.NORMAL), "rb").read()
        result_enc = base64.b64encode(content)
        indent.write(xmlFile, f'<file name="{self.NORMAL}" path="/" encoding="base64">' + str(result_enc)[2:] + '</file>')
        #result = b64encode(content)
        content = open(os.path.join(self.dataDir, self.ACCESSIBLE), "rb").read()
        result_enc = base64.b64encode(content)
        indent.write(xmlFile, f'<file name="{self.ACCESSIBLE}" path="/" encoding="base64">' + str(result_enc)[2:] + '</file>')
        #content = open(os.path.join(self.dataDir, self.NORMAL), "rb").read()
        #'''

        result = binaryFile2base64(os.path.join(self.dataDir, self.NORMAL))
        indent.write(xmlFile, '<file name="CS.pdf" path="/" encoding="base64">' + result + '</file>')

        result = binaryFile2base64(os.path.join(self.dataDir, self.ACCESSIBLE))
        indent.write(xmlFile, '<file name="CSA.pdf" path="/" encoding="base64">' + result + '</file>')
        

        indent.dec()
        indent.write(xmlFile, '</questiontext>')
        indent.write(xmlFile, '<generalfeedback format="html">')
        indent.write(xmlFile, '<text></text>')
        indent.write(xmlFile, '</generalfeedback>')
        indent.write(xmlFile, '<defaultgrade>0.0000000</defaultgrade>')
        indent.write(xmlFile, '<penalty>0.0000000</penalty>')
        indent.write(xmlFile, '<hidden>0</hidden>')
        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, "<idnumber></idnumber>")
        indent.dec()
        indent.write(xmlFile, '</question>')

        # end of flushing
        
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

class TrueFalse(Question):
    
    ID = 2600 # what for???
    defaultMark = 0.0
    correctFraction = "100"
    wrongFraction = "0"
    
    
    def __init__(self, **kwargs):
        super(TrueFalse, self).__init__()

        self.text = kwargs['text']
        name = kwargs['name']
        (self.name, self.mark) = self.setMark(name, TrueFalse.defaultMark)
        
    # for moodle XML import file
    def writeQuestion(self, xmlFile, indent, args):
        print("Saving truefalse:", self.name)

        # header
        indent.write(xmlFile, "<question type=\"truefalse\">")
        indent.inc()
        indent.write(xmlFile, "<name>")
        indent.inc()
        indent.write(xmlFile, "<text> " + f"{self.positionInQuiz:02d} {self.name}" + " </text>")
        indent.dec()
        indent.write(xmlFile, "</name>")

        # text
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        indent.write(xmlFile, "<questiontext format = \"html\">")
        indent.write(xmlFile, '<text><![CDATA[<p dir="ltr" style="text-align: left;">' + text + '</p>]]></text>')
        indent.write(xmlFile, "</questiontext>")
        indent.write(xmlFile, "<generalfeedback format = \"html\">")
        indent.write(xmlFile, "<text></text>")
        indent.write(xmlFile, "</generalfeedback>")

        # parameters
        indent.write(xmlFile, "<defaultgrade> " + str(self.mark) + " </defaultgrade>")
        indent.write(xmlFile, "<penalty> 1.0000000 </penalty>")
        indent.write(xmlFile, "<hidden> 0 </hidden>")

        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, "<idnumber></idnumber>")

        # write individual parameters
        
        
        indent.write(xmlFile, '<answer fraction="0" format="moodle_auto_format">')
        indent.inc()
        indent.write(xmlFile, '<text>true</text>')
        indent.write(xmlFile, '<feedback format="html">')
        indent.inc()
        indent.write(xmlFile, '<text></text>')
        indent.dec()
        indent.write(xmlFile, '</feedback>')
        indent.dec()
        indent.write(xmlFile, '</answer>')
        
        indent.write(xmlFile, '<answer fraction="100" format="moodle_auto_format">')
        indent.inc()
        indent.write(xmlFile, '<text>false</text>')
        indent.write(xmlFile, '<feedback format="html">')
        indent.inc()
        indent.write(xmlFile, '<text></text>')
        indent.dec()
        indent.write(xmlFile, '</feedback>')
        indent.dec()
        indent.write(xmlFile, '</answer>')

        # close
        indent.dec()
        indent.write(xmlFile, "</question>")

    
    def writeExportFiles(self, file, args, root):
        pass
    
    # fro the html control file
    def writeHtml(self, file, args):
        pass

    # for creating backup file
    def writeImportQuestion(self, xmlFile, indent, args):
        pass        

class MultiChoice(Question):
    
    ID = 2500 # what for???
    defaultMark = 3.0
    correctFraction = "100"
    wrongFraction = "-33.33333"
    
    
    def __init__(self, **kwargs):
        super(MultiChoice, self).__init__()

        self.text = kwargs['text']
        name = kwargs['name']
        self.answer = self.processAnswers(kwargs['answer'])
        (self.name, self.mark) = self.setMark(name, MultiChoice.defaultMark)
        (self.correctFraction, self.wrongFraction) = self.setFractions(name)



    def setFractions(self, name):
        default = (MultiChoice.correctFraction, MultiChoice.wrongFraction)
        sign = '@f'
        name = name.lower()
        idx = name.rfind(sign)
    
        if idx == -1:
            return default
    
        text = name[idx + len(sign):].split(maxsplit = 1)[0].strip()
        (correct, wrong) = text.split(':')
    
        try:
            return (correct, wrong)
        except Exception as e:
            print(e)
            return default

    def processAnswers(self, data):
        answers = data.split('\n')
        choiches = []
        # correct, text
        lut = [False, True]
        for answer in answers:
            if answer == '':
                continue
            
            (correct, text) = answer.split(' ', 1)
            choiches.append((lut[int(correct)], text.strip()))
          
        return choiches

    
    def writeTxt(self, txtFile, args):
        txtFile.write(f'\n{self.text}\n')
        for answer in self.answer:
            line = f'- [{int(answer[0])}] {answer[1]}\n'
            txtFile.write(line)

    def markdownTuplesToHtml(self, tuples):
        """
        Converts a list of tuples containing a boolean and markdown text into an HTML string.
        Each tuple is transformed into an item of an itemized list with different bullets based on the boolean value.
        """
        html_list = "<ul>\n"

        for boolean, markdown_text in tuples:
            # Convert markdown to HTML
            html_text = markdown.markdown(markdown_text,  extensions = EXTENSION_LIST)

            # Choose bullet style based on boolean value
            bullet = "*" if boolean else "o"

            # Create list item
            html_list += f"  <li><span>{bullet}</span> {html_text}</li>\n"

        html_list += "</ul>"

        return html_list

    # fro the html control file
    def writeHtml(self, file, args):
        
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        answer = self.markdownTuplesToHtml(self.answer)
        file.write('<h2>Multichoice text</h2>')
        file.write('<p dir="ltr" style="text-align: left;">' + text + '</p>')
        file.write('<h2>Multichoice answer</h2>')
        file.write('<p dir="ltr" style="text-align: left;">' + answer + '</p>')
    
        pass

    # for creating backup file
    def writeImportQuestion(self, xmlFile, indent, args):
        pass

    # for moodle XML import file
    def writeQuestion(self, xmlFile, indent, args):
        print("Saving multichoice:", self.name)

        # header
        indent.write(xmlFile, "<question type=\"multichoice\">")
        indent.inc()
        indent.write(xmlFile, "<name>")
        indent.inc()
        indent.write(xmlFile, "<text> " + f"{self.positionInQuiz:02d} {self.name}" + " </text>")
        indent.dec()
        indent.write(xmlFile, "</name>")

        # text
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        indent.write(xmlFile, "<questiontext format = \"html\">")
        indent.write(xmlFile, '<text><![CDATA[<p dir="ltr" style="text-align: left;">' + text + '</p>]]></text>')
        indent.write(xmlFile, "</questiontext>")
        indent.write(xmlFile, "<generalfeedback format = \"html\">")
        indent.write(xmlFile, "<text></text>")
        indent.write(xmlFile, "</generalfeedback>")

        # parameters
        indent.write(xmlFile, "<defaultgrade> " + str(self.mark) + " </defaultgrade>")
        indent.write(xmlFile, "<penalty> 0 </penalty>")
        indent.write(xmlFile, "<hidden> 0 </hidden>")

        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, "<idnumber></idnumber>")

        # write individual parameters
        
        
        indent.write(xmlFile, "<single>true</single>")
        indent.write(xmlFile, "<shuffleanswers>true</shuffleanswers>")
        indent.write(xmlFile, "<answernumbering>abc</answernumbering>")

        
        # trail

        indent.write(xmlFile, "<correctfeedback format=\"html\">")
        indent.write(xmlFile, "<text>Risposta corretta.</text>")
        indent.write(xmlFile, "</correctfeedback>")
        indent.write(xmlFile, "<partiallycorrectfeedback format = \"html\">")
        indent.write(xmlFile, "<text>Risposta parzialmente esatta.</text>")
        indent.write(xmlFile, "</partiallycorrectfeedback>")
        indent.write(xmlFile, "<incorrectfeedback format = \"html\">")
        indent.write(xmlFile, "<text>Risposta errata.</text>")
        indent.write(xmlFile, "</incorrectfeedback>")
        indent.write(xmlFile, "<shownumcorrect/>")
        
        for (value, choice) in self.answer:
            fraction = self.correctFraction if value else self.wrongFraction
            choice = markdown.markdown(choice,  extensions = EXTENSION_LIST)
            indent.write(xmlFile, "<answer fraction=\"" + str(fraction) + "\" format =\"html\">")
            indent.write(xmlFile, "<text><![CDATA[<p> " + choice + " </p>]]></text>")
            indent.write(xmlFile, "<feedback format=\"html\">")
            indent.write(xmlFile, "<text></text>")
            indent.write(xmlFile, "</feedback>")
            indent.write(xmlFile, "</answer>")


        # close
        indent.dec()
        indent.write(xmlFile, "</question>")
        
    def writeExportFiles(self, file, args, root):
        pass

class CrownLab(Question):

    ID = 1
    defaultMark = 26.0
    CODE_KEY = '###CODE###'

    def __init__(self, **kwargs):
        super(CrownLab, self).__init__()
        self.text = kwargs['text']
        self.name = kwargs['name']
        self.hasMain = False
        self.mainCode = ''
        self.fileList = kwargs['fileList']
        self.answer = kwargs['answer']
        self.workDir = '.'
        (self.name, self.mark) = self.setMark(self.name, CrownLab.defaultMark)
        if kwargs['destination'] != '':
            self.destination = kwargs['destination']
        else:
            self.destination = "portal:"
            
        # analizza testo per vedere se c'è del codice esplicito per il main
        
        if CrownLab.CODE_KEY in self.text:
            parts = self.text.split(CrownLab.CODE_KEY, 1)
            self.text = parts[0].strip()
            self.mainCode = parts[1].strip()
            self.hasMain = True

        '''
        DESTINATION TYPES
        null/stringa vuota: non consegnare (scarta contenuti istanza allo spegnimento)  
        portal: carica su consegna elaborati (com'è stato finora; notare i : a fine stringa, sono necessari)
        mdlZip: carica zip su moodle (è presente un pulsante per scaricare lo zip dal report della domanda, anche qui i : 
        fanno parte della stringa)
        mdlTxt:path/to/file.ext carica zip su moodle, poi renderizza il file di testo indicato prendendolo dallo zip 
        (il pulsante di download dello zip completo sul report comunque rimane)
        mdlPic:path/to/file.ext carica zip su moodle, poi visualizza l'immagine indicata prendendola dallo zip 
        (anche qui, il pulsante di download dello zip completo sul report permette il download di tutto il package arrivato dal crownlabs)
        se invece qualcuno preferisse avere la consegna su moodle in modo che il file sia visualizzato nel report, sarebbe da mettere 
        <destination>mdlTxt:main.py</destination>

        '''


        self.coderunnerId = CrownLab.ID
        CrownLab.ID += 1


    # fro the html control file
    def writeHtml(self, file, args):
        pass

    # for creating backup file
    def writeImportQuestion(self, xmlFile, indent, args):
        pass

    def createZipFile(self, directory):

        # 1. create the exam dir that will be zipped
        examDir = os.path.join(directory, "exam")
        #if os.path.exists(examDir) and os.path.isdir(examDir):
        
        try:
            rmtree(examDir, ignore_errors=True)
        except:
            pass

        os.mkdir(examDir)
        '''
        # .idea dir is for pycharm
        ideaDir = os.path.join(examDir, ".idea")
        Path(ideaDir).mkdir(exist_ok=True)
        copytree('./.idea', ideaDir, dirs_exist_ok=True)
        '''
        

        # .vscode dir is for visual studio code
        vsDir = os.path.join(examDir, ".vscode")
        Path(vsDir).mkdir(exist_ok=True)
        copytree('./.vscode', vsDir, dirs_exist_ok=True)

        for fileName in self.fileList:
            original = os.path.join(self.workDir, fileName)
            
            # check import files
            if not (os.path.exists(original) and os.access(original, os.R_OK)):
                print(f'errore in accesso del file {original}')
                if input('Interrompo esecuzione? (y/n) ').lower() == 'y':
                    exit()

            destination = os.path.join(examDir, fileName)
            copyfile(original, destination)

        mainFile = os.path.join(examDir, "main.py")

        with open(mainFile, "w", encoding = "utf-8") as file:

            if self.hasMain:
                file.write(self.mainCode)
                file.write("\n\n")
                
            else:
                header = open("./pythonHeader.txt", "r", encoding = "utf-8").read()
                file.write(header)
                file.write("\n\n")

            
                for fileName in self.fileList:
                    file.write(f"print(open('{fileName}', 'r').read())\nprint()\n")

        zipFile = os.path.join(directory, "exam")
        try:
            os.remove(zipFile)
        except OSError:
            pass

        archiveFormat = 'zip'
        make_archive(zipFile, archiveFormat, examDir)
        return binaryFile2base64(zipFile + '.' + archiveFormat)

    def createCLText(self):
        #text = html.escape(markdown.markdown(self.text,  extensions = EXTENSION_LIST))
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)
        clTextFile = os.path.join(self.workDir, "CrownLabQuestionText.txt")

        with open(clTextFile, "w", encoding = "utf-8") as file:
            file.write(text)


    # for moodle XML import file
    def writeQuestion(self, xmlFile, indent, args):
        print("Saving crownlab question:", self.name,"\n\tUsing files", self.fileList)
        zipFileContent = self.createZipFile(os.path.dirname(os.path.abspath(xmlFile.name)))
        self.createCLText()
        
        
        indent.write(xmlFile, '<question type="crownlabs">')

        indent.inc()
        indent.write(xmlFile, '<name>')
        indent.inc()
        #indent.write(xmlFile, '<text>test export</text>')
        # f'<name><text>{self.positionInQuiz:02d} Documentazione Python</text></name>
        indent.write(xmlFile, '<text><![CDATA[' + f'{self.positionInQuiz:02d} ' + self.name + ']]></text>')
        indent.dec()
        indent.write(xmlFile, '</name>')
        indent.write(xmlFile, '<questiontext format="html">')
        indent.inc()
        
        text = markdown.markdown(self.text,  extensions = EXTENSION_LIST)

        indent.write(xmlFile, '<text><![CDATA[' + text + ']]></text>')
        indent.dec()
        indent.write(xmlFile, '</questiontext>')
        indent.write(xmlFile, '<generalfeedback format="moodle_auto_format">')
        indent.inc()
        indent.write(xmlFile, '<text></text>')
        indent.dec()
        indent.write(xmlFile, '</generalfeedback>')
        indent.write(xmlFile, '<defaultgrade>' + str(self.mark) + '</defaultgrade>')
        indent.write(xmlFile, '<penalty>0.0000000</penalty>')
        indent.write(xmlFile, '<hidden>0</hidden>')
        
        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, '<idnumber>python</idnumber>')

        if Question.MoodleVersion >= 3.0:
            indent.write(xmlFile, '<template>vscode-py-noexts</template>')
        else:
            indent.write(xmlFile, '<template>pycharm2021-persistent</template>')

        if Question.MoodleVersion >= 3.0:
            contentorigin = '\n<![CDATA[{"filename":"exam.zip","content":"' + zipFileContent + '"}]]>'
            indent.write(xmlFile, '<contentorigin>' + contentorigin + '</contentorigin>')
        else:
            indent.write(xmlFile, '<file name="exam.zip" path="/" encoding="base64">' + zipFileContent + '</file>')

        
        if Question.MoodleVersion >= 3.0:
            #indent.write(xmlFile, '<deliver>0</deliver>')
            indent.write(xmlFile, f'<destination>{self.destination}</destination>')
            
        indent.dec()
        indent.write(xmlFile, '</question>')
        
    def writeExportFiles(self, file, args, root):
        pass

