from Indent import Indent
import os
import datetime
import time
from QuestionTypes import getTimeStamp, getVersionNumber


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class QuestionCategories(object):
    """description of class"""

    def __init__(self):
        self.categories = []

    def add(self, category):
        self.categories.append(category)


class CategoryInfo(object):

    INFO_FILE = 'info.quiz'
    CanReDo = False

    def __init__(self, categoryDir = '', readOnlyDescription = False):
        super(CategoryInfo, self).__init__()

        self.categoryDir = categoryDir
        self.readOnlyDescription = readOnlyDescription

        self.open = None
        self.close = None
        self.duration = None
        self.closeafter = None
        self.delay = 0
        self.canredo = CategoryInfo.CanReDo
        self.intro = ''
        
        self.parseInfo()
        self.setValues()

    def parseInfo(self):

        try:
            file = open(os.path.join(self.categoryDir, CategoryInfo.INFO_FILE), 'r', encoding='utf-8')
            lines = file.readlines()
            idx = 0

            while idx < len(lines):
                line = lines[idx].strip()
                idx += 1

                if line == '' or line[0] == '#':
                    continue

                parts = line.split()
                code = parts[0].lower()

                
                if code == 'intro':
                    print('intro')
                    for partId in range(1,len(parts)):
                        self.intro += parts[partId].replace('<', '&lt;').replace('>','&gt;')
                        if partId < len(parts) - 1:
                            self.intro += ' '


                if not self.readOnlyDescription:
                    if code == 'open':
                        self.open = datetime.datetime.strptime(parts[1] + ' ' + parts[2], '%d/%m/%Y %H:%M')
                    elif code == 'close':
                        self.close = datetime.datetime.strptime(parts[1] + ' ' + parts[2], '%d/%m/%Y %H:%M')
                    elif code == 'duration':
                        # duration in minutes
                        self.duration = int(parts[1]) * 60
                    elif code == 'closeafter':
                        self.closeafter = str(int(parts[1]))
                    elif code == 'canredo':
                        self.canredo = str2bool(parts[1])        
                    elif code == 'delay':
                        self.delay = str(int(parts[1]))          


        except Exception as e:
            print('Error in parsing quiz info for', self.categoryDir,e)
            return

    def setValues(self):  
        if self.open is None:
            self.open = '0'

        if self.close is None:
            self.close = '0'

        if self.duration is not None and self.open != '0':
            quizEnd = self.open + datetime.timedelta(seconds = self.duration + int(self.delay) * 60)

            if self.close is not None:
                self.close = max(quizEnd, self.close)
            else:
                self.close = quizEnd
                        
            seconds = int((self.open - datetime.datetime.utcfromtimestamp(0)).total_seconds())
            self.open = str(seconds)
            seconds = int((self.close - datetime.datetime.utcfromtimestamp(0)).total_seconds())
            self.close = str(seconds)


        if self.duration is None:
            self.duration = '0'
        else:
            self.duration = str(self.duration)

        if self.closeafter is None:
            self.closeafter = '0'




class Category(object):
    """description of class"""

    categoryID = 1000               # unique ID per category
    quizID = 7500                   # unique ID per quiz
    quizInstanceID = 6800           # unique ID per quiz
    contextID = 618350              # unique ID per quiz
    questionInstanceID = 115520     # unique ID per quiz
    sectionID = 7620                # unique ID per quiz   
    gradesID = 8270                 # unique ID per quiz     
    feedbackID = 27070              # unique ID per quiz     

    def getCategoryId():
        Category.categoryID += 1
        return  Category.categoryID - 1

    def getQuizId():
        Category.quizID += 1
        return  Category.quizID - 1
    
    def getQuizInstanceId():
        Category.quizInstanceID += 1
        return  Category.quizInstanceID - 1
    
    def getContextId():
        Category.contextID += 1
        return  Category.contextID - 1

    def getQuestionInstanceId():
        Category.questionInstanceID += 1
        return  Category.questionInstanceID - 1

    def getSectionId():
        Category.sectionID += 1
        return  Category.sectionID - 1
    
    def getGradesId():
        Category.gradesID += 1
        return  Category.gradesID - 1

    def getFeedbackId():
        Category.feedbackID += 1
        return  Category.feedbackID - 1

    def __init__(self, name):
        self.categoryId = Category.getCategoryId()    # quiz id (same as instance name in grades)
        self.quizId = Category.getQuizId() # module ID
        self.quizInstanceId = Category.getQuizInstanceId() # module ID
        self.contextId = Category.getContextId()
        #self.questionInstanceId = Category.getQuestionInstanceId()
        self.sectionId = Category.getSectionId()
        self.gradesId = Category.getGradesId()
        self.feedbackId = Category.getFeedbackId()

        self.name = name
        self.parent = 0
        self.info = ""
        self.isQuiz = False
        self.info = None

        self.questions = []

    def addQuestions(self, questions):
        self.questions = questions
        # if it has questions, then it is a quiz that must be saved
        self.isQuiz = True

    def writeQuiz(self, activityDir, args):

        # the parent categoriues are not quizzes and should not be saved
        if not self.isQuiz:
            return

        quizDir = os.path.join(activityDir, 'quiz_' + str(self.quizId))
        os.makedirs(quizDir, exist_ok = True)

        # grade history
        file = open(os.path.join(quizDir, 'grade_history.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<grade_history>\n\t<grade_grades>\n\t</grade_grades>\n</grade_history>')
        file.close()

        # roles
        file = open(os.path.join(quizDir, 'roles.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n\t<role_overrides>\n\t</role_overrides>\n\t<role_assignments>\n\t</role_assignments>\n</roles>')
        file.close()

        #grades 
        file = open(os.path.join(quizDir, 'grades.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.writeGrades(file)
        file.close()
        
        #inforef 
        file = open(os.path.join(quizDir, 'inforef.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.writeInfoRef(file)
        file.close()
        
        #module 
        file = open(os.path.join(quizDir, 'module.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.writeModule(file)
        file.close()
               
        #quiz 
        file = open(os.path.join(quizDir, 'quiz.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.writeQuizFile(file)
        file.close()

    def writeMBEntry(self, file, indent):

        if not self.isQuiz:
            return

        indent.write(file, '<activity>')
        indent.inc()
        indent.write(file, '<moduleid>' + str(self.quizId) + '</moduleid>')
        indent.write(file, '<sectionid>1474</sectionid>')  # quiz --> 1474 (not the sectionId of the category)
        indent.write(file, '<modulename>quiz</modulename>')
        indent.write(file, '<title>' + self.name + '</title>')
        indent.write(file, '<directory>activities/quiz_' + str(self.quizId) + '</directory>')
        indent.dec()
        indent.write(file, '</activity>')

        pass
        
    def writeQuizFile(self, file):
        indent = Indent()
        indent.write(file, '<activity id="' + str(self.quizInstanceId) + '" moduleid="' + str(self.quizId) + '" modulename="quiz" contextid="542952">')
        indent.inc()
        indent.write(file, '<quiz id="' + str(self.quizInstanceId) + '">')
        indent.inc()
        indent.write(file, '<name>' + self.name + '</name>')

        intro = self.info.intro
        if intro == '':
            intro = '&lt;p&gt;&lt;b&gt;&lt;i&gt;Esame di Informatica&amp;nbsp; (Python)&lt;/i&gt;&lt;/b&gt;&amp;nbsp;&lt;/p&gt;'
            intro += '&lt;p&gt;Potete rispondere alle domande in un ordine qualsiasi (e tornare indietro e modificare le risposte). '
            intro += "Ricordo che se anche ci fossero problemi con il server che gestisce la compilazione python, il codice scritto nella casella di testo viene salvato correttamente all'interno della risposta. "
            intro += "In caso di problemi, potete quindi continuare a scrivere il codice (e provare a ricompilare in un momento successivo). "
            intro += "Ricordo che il funzionamento corretto del compito NON è un requisito essenziale per la valutazione dello stesso&lt;/p&gt;"

        indent.write(file, '<intro>' + intro + '</intro>')
        indent.write(file, '<introformat>1</introformat>')
        indent.write(file, '<timeopen>' + str(self.info.open) + '</timeopen>')
        indent.write(file, '<timeclose>' + str(self.info.close) + '</timeclose>')
        indent.write(file, '<timelimit>' + str(self.info.duration) + '</timelimit>')
        indent.write(file, '<overduehandling>autosubmit</overduehandling>')
        indent.write(file, '<graceperiod>0</graceperiod>')
        indent.write(file, '<preferredbehaviour>interactive</preferredbehaviour>')
        indent.write(file, '<canredoquestions>0</canredoquestions>')

        attempts = 1
        if self.info.canredo:
            attempts = 0

        indent.write(file, '<attempts_number>' + str(attempts) + '</attempts_number>')
        indent.write(file, '<attemptonlast>0</attemptonlast>')
        indent.write(file, '<grademethod>1</grademethod>')
        indent.write(file, '<decimalpoints>2</decimalpoints>')
        indent.write(file, '<questiondecimalpoints>-1</questiondecimalpoints>')
        indent.write(file, '<reviewattempt>69904</reviewattempt>')
        indent.write(file, '<reviewcorrectness>69904</reviewcorrectness>')
        indent.write(file, '<reviewmarks>69904</reviewmarks>')
        indent.write(file, '<reviewspecificfeedback>69904</reviewspecificfeedback>')
        indent.write(file, '<reviewgeneralfeedback>69904</reviewgeneralfeedback>')
        indent.write(file, '<reviewrightanswer>69904</reviewrightanswer>')
        indent.write(file, '<reviewoverallfeedback>4368</reviewoverallfeedback>')
        indent.write(file, '<questionsperpage>1</questionsperpage>')
        indent.write(file, '<navmethod>free</navmethod>')
        indent.write(file, '<shuffleanswers>1</shuffleanswers>')
        indent.write(file, '<sumgrades>32.00000</sumgrades>')
        indent.write(file, '<grade>32.00000</grade>')
        indent.write(file, '<timecreated>0</timecreated>')
        indent.write(file, '<timemodified>' + getTimeStamp() + '</timemodified>')
        indent.write(file, '<password></password>')
        indent.write(file, '<subnet></subnet>')
        indent.write(file, '<browsersecurity>-</browsersecurity>')
        indent.write(file, '<delay1>' + str(self.info.delay) + '</delay1>')
        indent.write(file, '<delay2>1</delay2>')
        indent.write(file, '<showuserpicture>0</showuserpicture>')
        indent.write(file, '<showblocks>0</showblocks>')
        indent.write(file, '<completionattemptsexhausted>0</completionattemptsexhausted>')
        indent.write(file, '<completionpass>0</completionpass>')
        indent.write(file, '<pagination>0</pagination>')
        indent.write(file, '<closeafter>' + str(self.info.closeafter) + '</closeafter>')
        indent.write(file, '<autoreport>0</autoreport>')
        indent.write(file, '<watermark>0</watermark>')
    
        indent.write(file, '<question_instances>')
        indent.inc()

        #write instances
        
        for (idx,question) in enumerate(self.questions):
            questionId = str(question.id)
            instanceId = str(Category.getQuestionInstanceId())
            # mark should be assigned to question from args
            questionMark = str(question.mark)

            indent.write(file, '<question_instance id="' + instanceId + '">')
            indent.inc()
            indent.write(file, '<slot>' + str(idx + 1) + '</slot>')
            indent.write(file, '<page>' + str(idx + 1) + '</page>')
            indent.write(file, '<requireprevious>0</requireprevious>')
            indent.write(file, '<questionid>' + questionId + '</questionid>')
            indent.write(file, '<maxmark>' + questionMark + '</maxmark>')
            indent.dec()
            indent.write(file, '</question_instance>')
        


        indent.dec()
        indent.write(file, '</question_instances>')
    
        indent.write(file, '<sections>')
        indent.inc()
        indent.write(file, '<section id="' + str(self.sectionId) + '">')
        indent.inc()
        indent.write(file, '<firstslot>1</firstslot>')
        indent.write(file, '<heading></heading>')
        indent.write(file, '<shufflequestions>0</shufflequestions>')
        indent.dec()
        indent.write(file, '</section>')
        indent.dec()
        indent.write(file, '</sections>')
        indent.write(file, '<feedbacks>')
        indent.inc()
        indent.write(file, '<feedback id="' + str(self.feedbackId) + '">')
        indent.inc()
        indent.write(file, '<feedbacktext></feedbacktext>')
        indent.write(file, '<feedbacktextformat>1</feedbacktextformat>')
        indent.write(file, '<mingrade>0.00000</mingrade>')
        indent.write(file, '<maxgrade>33.00000</maxgrade>')
        indent.dec()
        indent.write(file, '</feedback>')
        indent.dec()
        indent.write(file, '</feedbacks>')
        indent.write(file, '<overrides>')
        indent.write(file, '</overrides>')
        indent.write(file, '<grades>')
        indent.write(file, '</grades>')
        indent.write(file, '<attempts>')
        indent.write(file, '</attempts>')
        indent.dec()
        indent.write(file, '</quiz>')
        indent.dec()
        indent.write(file, '</activity>')

    def writeModule(self, file):
        indent = Indent()
        indent.write(file, '<module id="' + str(self.quizId) + '" version="' + getVersionNumber() + '">')
        indent.inc()
        indent.write(file, '<modulename>quiz</modulename>')
        indent.write(file, '<sectionid>1474</sectionid>')
        indent.write(file, '<sectionnumber>0</sectionnumber>')
        indent.write(file, '<idnumber></idnumber>')
        indent.write(file, '<added>' + getTimeStamp() + '</added>')
        indent.write(file, '<score>0</score>')
        indent.write(file, '<indent>0</indent>')
        indent.write(file, '<visible>0</visible>')
        indent.write(file, '<visibleold>0</visibleold>')
        indent.write(file, '<groupmode>0</groupmode>')
        indent.write(file, '<groupingid>0</groupingid>')
        indent.write(file, '<completion>0</completion>')
        indent.write(file, '<completiongradeitemnumber>$@NULL@$</completiongradeitemnumber>')
        indent.write(file, '<completionview>0</completionview>')
        indent.write(file, '<completionexpected>0</completionexpected>')
        indent.write(file, '<availability>$@NULL@$</availability>')
        indent.write(file, '<showdescription>1</showdescription>')
        indent.dec()
        indent.write(file, '</module>')

    def writeInfoRef(self, file):
        indent = Indent()
        indent.write(file, '<inforef>')
        indent.inc()
        indent.write(file, '<grade_itemref>')
        indent.inc()
        indent.write(file, '<grade_item>')
        indent.inc()
        indent.write(file, '<id>' + str(self.gradesId) + '</id>')
        indent.dec()
        indent.write(file, '</grade_item>')
        indent.dec()
        indent.write(file, '</grade_itemref>')

        # actually, moodle backup lists all categories.... is it really necessary??
        categoryList = [self.categoryId]
    
        indent.write(file, '<question_categoryref>')
        indent.inc()
        for id in categoryList:
            indent.write(file, '<question_category>')
            indent.inc()
            indent.write(file, '<id>' + str(id) + '</id>')
            indent.dec()
            indent.write(file, '</question_category>')
                 
        indent.dec()
        indent.write(file, '</question_categoryref>')
        indent.dec()
        indent.write(file, '</inforef>')

        
    def writeGrades(self, file):
        indent = Indent()

        indent.write(file, '<activity_gradebook>')
        indent.inc()
        indent.write(file, '<grade_items>')
        indent.inc()
        indent.write(file, '<grade_item id="' + str(self.gradesId) + '">')
        indent.inc()
        indent.write(file, '<categoryid>852</categoryid>')
        indent.write(file, '<itemname>' + self.name + '</itemname>')
        indent.write(file, '<itemtype>mod</itemtype>')
        indent.write(file, '<itemmodule>quiz</itemmodule>')
        indent.write(file, '<iteminstance>' + str(self.quizInstanceId) + '</iteminstance>')
        indent.write(file, '<itemnumber>0</itemnumber>')
        indent.write(file, '<iteminfo>$@NULL@$</iteminfo>')
        indent.write(file, '<idnumber>$@NULL@$</idnumber>')
        indent.write(file, '<calculation>$@NULL@$</calculation>')
        indent.write(file, '<gradetype>1</gradetype>')
        indent.write(file, '<grademax>32.00000</grademax>')
        indent.write(file, '<grademin>0.00000</grademin>')
        indent.write(file, '<scaleid>$@NULL@$</scaleid>')
        indent.write(file, '<outcomeid>$@NULL@$</outcomeid>')
        indent.write(file, '<gradepass>0.00000</gradepass>')
        indent.write(file, '<multfactor>1.00000</multfactor>')
        indent.write(file, '<plusfactor>0.00000</plusfactor>')
        indent.write(file, '<aggregationcoef>0.00000</aggregationcoef>')
        indent.write(file, '<aggregationcoef2>0.00000</aggregationcoef2>')
        indent.write(file, '<weightoverride>0</weightoverride>')
        indent.write(file, '<sortorder>63</sortorder>')
        indent.write(file, '<display>0</display>')
        indent.write(file, '<decimals>$@NULL@$</decimals>')
        indent.write(file, '<hidden>1</hidden>')
        indent.write(file, '<locked>0</locked>')
        indent.write(file, '<locktime>0</locktime>')
        indent.write(file, '<needsupdate>0</needsupdate>')
        indent.write(file, '<timecreated>' + getTimeStamp() + '</timecreated>')
        indent.write(file, '<timemodified>' + getTimeStamp() + '</timemodified>')
        indent.write(file, '<grade_grades>')
        indent.write(file, '</grade_grades>')
        indent.dec()
        indent.write(file, '</grade_item>')
        indent.dec()
        indent.write(file, '</grade_items>')
        indent.write(file, '<grade_letters>')
        indent.write(file, '</grade_letters>')
        indent.dec()
        indent.write(file, '</activity_gradebook>')

    def writeExportFiles(self, file, args, root):
        
        # write for each question... if essay, it has no file
        # if coderunner, one entry for text (no file) and the other for files --> 2char for dir, hash for name, myme type as original

        for question in self.questions:
            question.writeExportFiles(file, args, root)

    def writeXml(self, file, args):
        indent = Indent()
        indent.inc()

        indent.write(file, '<question_category id="' + str(self.categoryId) + '">')
        indent.inc()
        indent.write(file, '<name>' + self.name + '</name>')
        indent.write(file, '<contextid>542952</contextid>')
        indent.write(file, '<contextlevel>50</contextlevel>')
        indent.write(file, '<contextinstanceid>1053</contextinstanceid>')
        indent.write(file, '<info></info>')

        hasParent = 0
        if self.parent != 0:
            hasParent = 1

        indent.write(file, '<infoformat>' + str(hasParent) + '</infoformat>')
        indent.write(file, '<stamp>exam.polito.it+210210103259+FoLZQU</stamp>')
        indent.write(file, '<parent>' + str(self.parent) + '</parent>')  # --> this way questions appear in the quiz, but not in the questionbank, and the correct hyerarchy is not created
        #indent.write(file, '<parent>0</parent>')   # --> this way questions appear in questionbank, but not with the correct hyerarchy
        indent.write(file, '<sortorder>0</sortorder>')
        indent.write(file, '<questions>')
        indent.inc()

        # writing questions
        for question in self.questions:
            question.writeImportQuestion(file, indent, args)

        indent.dec()
        indent.write(file, '</questions>')
        indent.dec()
        indent.write(file, '</question_category>')





