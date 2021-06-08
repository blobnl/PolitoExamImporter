import re
import base64
import markdown
import argparse
import os
import glob

from Indent import Indent
from QuestionCategories import Category
from QuestionTypes import getTimeStamp
import tarfile
import CodeRunnerGenerator as CRG

'''
# get timestamp in seconds
import time

int(time.time()) 
'''

class MoodleImport(object):

    contextId = '542952'

    def __init__(self, args):
        super().__init__()

        self.args = args

        self.questions = {}
        self.categories = {}
        self.quizzes = {}

        self.backupType = 'course' # or 'activity'
        
        self.root = os.path.join(self.args.workDir, self.args.category)
        self.xmlDir = os.path.join(self.args.workDir, 'XMLquiz')
        self.activityDir = os.path.join(self.root, 'activities')
        os.makedirs(self.activityDir, exist_ok = True)

        self.backupName = self.args.category + '.mbz'

        print('creating moodle import file', self.backupName)


    def createSectionFiles(self):
        
        sectionDir = os.path.join(self.root, 'sections', 'section_1474')
        os.makedirs(sectionDir, exist_ok = True)
        # empty files
        # inforef
        file = open(os.path.join(sectionDir, 'inforef.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<inforef>\n</inforef>')
        file.close()

        
        # section
        file = open(os.path.join(sectionDir, 'section.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<section id="1474">\n')
        file.write('<number>0</number>\n')
        file.write('<name>$@NULL@$</name>\n')
        file.write('<summary></summary>\n')
        file.write('<summaryformat>1</summaryformat>\n')
        file.write('<sequence>')

        items = self.categories.items()
        for idx,(key,value) in enumerate(items):         
            file.write(str(value.quizId))
            if(idx < len(items) - 1):    
                file.write(',')

        file.write('</sequence>\n')
        file.write('<visible>1</visible>\n')
        file.write('<availabilityjson>{"op":"&amp;","c":[],"showc":[]}</availabilityjson>\n')
        file.write('</section>')
        file.close()



    def createCourseFiles(self):

        courseDir = os.path.join(self.root, 'course')
        os.makedirs(courseDir, exist_ok = True)
        
        # empty files
        # roles
        file = open(os.path.join(courseDir, 'roles.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n\t<role_overrides>\n\t</role_overrides>\n\t<role_assignments>\n\t</role_assignments>\n</roles>')
        file.close()
        
        
        # inforef
        file = open(os.path.join(courseDir, 'inforef.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<inforef>')
        indent = Indent()
        indent.inc()

        indent.write(file, '<roleref>')
        indent.inc()
        indent.write(file, '<role>')
        indent.inc()
        indent.write(file, '<id>5</id>')
        indent.dec()
        indent.write(file, '</role>')
        indent.dec()
        indent.write(file, '</roleref>')
        
        indent.write(file, '<question_categoryref>')
        indent.inc()

        for (key,value) in self.categories.items():         
            indent.write(file, '<question_category><id>' + str(value.categoryId) + '</id></question_category>')

        indent.dec()
        indent.write(file, '</question_categoryref>')
        indent.dec()
        
        indent.write(file, '</inforef>')

        file.close()
        
        # course
        file = open(os.path.join(courseDir, 'course.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        indent = Indent()

        indent.write(file, '<?xml version="1.0" encoding="UTF-8"?>')
        indent.write(file, '<course id="1053" contextid="' + MoodleImport.contextId + '">')
        indent.inc()
        indent.write(file, '<shortname>XXYY_Importer</shortname>')
        indent.write(file, '<fullname>Automatic Importer</fullname>')
        indent.write(file, '<idnumber></idnumber>')
        indent.write(file, '<summary>$@NULL@$</summary>')
        indent.write(file, '<summaryformat>1</summaryformat>')
        indent.write(file, '<format>topics</format>')
        indent.write(file, '<showgrades>0</showgrades>')
        indent.write(file, '<newsitems>0</newsitems>')
        indent.write(file, '<startdate>0</startdate>')
        indent.write(file, '<marker>0</marker>')
        indent.write(file, '<maxbytes>0</maxbytes>')
        indent.write(file, '<legacyfiles>0</legacyfiles>')
        indent.write(file, '<showreports>0</showreports>')
        indent.write(file, '<visible>1</visible>')
        indent.write(file, '<groupmode>0</groupmode>')
        indent.write(file, '<groupmodeforce>0</groupmodeforce>')
        indent.write(file, '<defaultgroupingid>0</defaultgroupingid>')
        indent.write(file, '<lang></lang>')
        indent.write(file, '<theme></theme>')
        indent.write(file, '<timecreated>' + getTimeStamp() + '</timecreated>')
        indent.write(file, '<timemodified>' + getTimeStamp() + '</timemodified>')
        indent.write(file, '<requested>0</requested>')
        indent.write(file, '<enablecompletion>0</enablecompletion>')
        indent.write(file, '<completionnotify>0</completionnotify>')
        indent.write(file, '<numsections>0</numsections>')
        indent.write(file, '<hiddensections>1</hiddensections>')
        indent.write(file, '<coursedisplay>0</coursedisplay>')
        indent.write(file, '<category id="12">')
        indent.inc()
        indent.write(file, '<name>TEST270</name>')
        indent.write(file, '<description></description>')
        indent.dec()
        indent.write(file, '</category>')
        indent.write(file, '<tags>')
        indent.write(file, '</tags>')
        indent.dec()
        indent.write(file, '</course>')



    def saveBackup(self):
        tarFilename = os.path.join(self.args.workDir, 'backup_' + self.backupName.replace('.mbz', ''))
        outputFilename = os.path.join(self.args.workDir, self.backupName)
        sourceDir = os.path.join(self.root, '')
        with tarfile.open(outputFilename, "w:gz") as tar:
            tar.add(sourceDir, arcname = os.path.basename(sourceDir))

    def addCategory(self, category):
        if not category in self.categories:
            self.categories[category] = Category(category)

        return self.categories[category]

    
    def getQuizId(self):
        self.quizId += 1
        return self.quizId - 1


    def addQuiz(self, category, questionList, categoryInfo = None):
        
        print('Adding category', category)
        parts = category.strip().split('/')

        for category in parts:
            self.addCategory(category)

        newCategory = self.categories[parts[-1]]
        newCategory.info = categoryInfo
        newCategory.addQuestions(questionList)

        # if it has a parent, get its id
        if len(parts) > 1:
            newCategory.parent = self.categories[parts[-2]].categoryId

    def categoryById(self, id):
        for key in self.categories:
            if self.categories[key].categoryId == id:
                return self.categories[key]

        return None

    def writeXml(self):
        # create root for XML dirs 
        os.makedirs(self.xmlDir, exist_ok = True)

        # directory where to save XML
        oldWorkDir = self.args.workDir
        oldCategory = self.args.category
        oldXML = self.args.xml


        for key in self.categories:
            # getting question list
            quiz = self.categories[key]

            if not quiz.isQuiz:
                continue

            category = key
            parent = self.categoryById(quiz.parent)
            while parent is not None:
                category = parent.name + '\\' + category
                parent = self.categoryById(parent.parent)

            self.args.xml = key + '.xml'
            self.args.category = category
            self.args.workDir = os.path.join(self.xmlDir, key)
            os.makedirs(self.args.workDir, exist_ok = True)

            CRG.storeQuestionList(quiz.questions, self.args)

        # creating unique import
        self.args.category = 'CG_quizzes'
        self.args.xml = self.args.category
        self.args.workDir = self.xmlDir
        CRG.createUniqueImport(self.args)

        # update args
        self.args.workDir = oldWorkDir
        self.args.xml = oldXML
        self.args.category = oldCategory


    def flush(self):

        # uncomment this if you want to save xml import file for question bank

        #self.writeXml()
        #return

        # empty files
        # groups
        file = open(os.path.join(self.root, 'groups.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<groups>\n\t<groupings>\n\t</groupings>\n</groups>')
        file.close()

        # outcomes
        file = open(os.path.join(self.root, 'outcomes.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<outcomes_definition>\n</outcomes_definition>')
        file.close()
        
        # roles 
        file = open(os.path.join(self.root, 'roles.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<roles_definition>\n</roles_definition>')
        file.close()

        # scales 
        file = open(os.path.join(self.root, 'scales.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<scales_definition>\n</scales_definition>')
        file.close()

        # completion
        file = open(os.path.join(self.root, 'completion.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<course_completion>\n</course_completion>')
        file.close()

        # grade_history
        file = open(os.path.join(self.root, 'grade_history.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<grade_history>\n<grade_grades>\n</grade_grades>\n</grade_history>')
        file.close()
        
        # gradebook
        file = open(os.path.join(self.root, 'gradebook.xml'), 'w', encoding = 'utf-8')
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n<gradebook>')
        indent = Indent()
        indent.inc()
        file.write('<grade_categories>')
        indent.inc()
        file.write('<grade_category id="852">')
        indent.inc()
        file.write('<parent>$@NULL@$</parent>')
        file.write('<depth>1</depth>')
        file.write('<path>/852/</path>')
        file.write('<fullname>?</fullname>')
        file.write('<aggregation>11</aggregation>')
        file.write('<keephigh>0</keephigh>')
        file.write('<droplow>0</droplow>')
        file.write('<aggregateonlygraded>1</aggregateonlygraded>')
        file.write('<aggregateoutcomes>0</aggregateoutcomes>')
        file.write('<timecreated>' + getTimeStamp() + '</timecreated>')
        file.write('<timemodified>' + getTimeStamp() + '</timemodified>')
        file.write('<hidden>0</hidden>')
        indent.dec()
        file.write('</grade_category>')
        indent.dec()
        file.write('</grade_categories>')
        
        file.write('<grade_items>')
        indent.inc()
        
        for (key,value) in self.categories.items():         
            indent.write(file, '<question_category><id>' + str(value.quizId) + '</id></question_category>')

        indent.dec()
        file.write('</grade_items>')
        
        file.write('<grade_letters>')
        file.write('</grade_letters>')
        file.write('<grade_settings>')
        file.write('</grade_settings>')
        indent.dec()
        indent.write(file, '</gradebook>')
        file.close()


        # create files
        self.createMoodleBackupFile()
        self.createCategoriesFile()
        self.createQuizFiles()

        if self.backupType == 'course':
            self.createCourseFiles()
            self.createSectionFiles()

        # create archive index
        self.createArchiveIndex()

        # create MBZ file
        self.saveBackup()

        
    def createArchiveIndex(self):
        # form root backup directory
        entries = []

        for root, dirs, files in os.walk(os.path.join(self.root, '')):
            dirName = root.replace(self.root, '').lstrip('\\').replace('\\', '/') + '/'

            if dirName != '/':
                entries.append(dirName + ' d 0 ?')
                #entries.append()


            #print('x', dirName)
            for file in files:
                filename = os.path.join(root, file) 
                printname = dirName + file
                filesize = os.stat(filename).st_size
                entries.append(printname + ' f ' + str(filesize) + ' ' + str(getTimeStamp()))

        entries.insert(0, 'Moodle archive file index. Count: ' + str(len(entries)))

        file = open(os.path.join(self.root, '.ARCHIVE_INDEX'), 'w', encoding = 'utf-8')

        for entry in entries:
            file.write(entry + '\n')

        file.close()


    def createMoodleBackupFile(self):
        indent = Indent()
        file = open(os.path.join(self.root, 'moodle_backup.xml'), 'w', encoding = 'utf-8')
        indent.write(file, '<?xml version="1.0" encoding="UTF-8"?>')
        indent.write(file, '<moodle_backup>')
        indent.inc()
        indent.write(file, '<information>')
        indent.inc()

        # general info
        
        indent.write(file, '<name>' + self.backupName + '</name>')
        indent.write(file, '<moodle_version>2015051100.04</moodle_version>')
        indent.write(file, '<moodle_release>2.9+ (Build: 20150604)</moodle_release>')
        indent.write(file, '<backup_version>2015051100</backup_version>')
        indent.write(file, '<backup_release>2.9</backup_release>')
        indent.write(file, '<backup_date>1613144889</backup_date>')
        indent.write(file, '<mnet_remoteusers>0</mnet_remoteusers>')
        indent.write(file, '<include_files>1</include_files>')
        indent.write(file, '<include_file_references_to_external_content>0</include_file_references_to_external_content>')
        indent.write(file, '<original_wwwroot>https://exam.polito.it</original_wwwroot>')
        indent.write(file, '<original_site_identifier_hash>cab50d79c086152fbba76d2abfa65a17</original_site_identifier_hash>')
        indent.write(file, '<original_course_id>' + str(1000) + '</original_course_id>') # 1035
        indent.write(file, '<original_course_format>topics</original_course_format>')
        indent.write(file, '<original_course_fullname>' + str('Automatic Importer') + '</original_course_fullname>') # Informatica
        indent.write(file, '<original_course_shortname>' + str('XXYY_Importer') + '</original_course_shortname>') # 2021_14BHDLZ_16
        indent.write(file, '<original_course_startdate>0</original_course_startdate>')
        indent.write(file, '<original_course_contextid>542952</original_course_contextid>')
        indent.write(file, '<original_system_contextid>1</original_system_contextid>')

        # details
        
        indent.write(file, '<details>')
        indent.inc()
        indent.write(file, '<detail backup_id="433d8cf111a71cd9f1276e022ab6d481">') # which id? SHA 80??
        indent.inc()
        indent.write(file, '<type>' + self.backupType + '</type>')  # activity/course??
        indent.write(file, '<format>moodle2</format>')
        indent.write(file, '<interactive>1</interactive>')
        indent.write(file, '<mode>10</mode>')   # which mode???
        indent.write(file, '<execution>1</execution>')
        indent.write(file, '<executiontime>0</executiontime>')
        indent.dec()
        indent.write(file, '</detail>')
        indent.dec()
        indent.write(file, '</details>')

        # contents
        
        indent.write(file, '<contents>')
        indent.inc()
        indent.write(file, '<activities>')
        indent.inc()

        # writing all quizzes
        for category in self.categories.values():
            category.writeMBEntry(file, indent) 

        indent.dec()
        indent.write(file, '</activities>')

        # sections and course
        if self.backupType == 'course':  
            indent.write(file, '<sections>')
            indent.inc()
            indent.write(file, '<section>')
            indent.inc()
            indent.write(file, '<sectionid>1474</sectionid>')
            indent.write(file, '<title>0</title>')
            indent.write(file, '<directory>sections/section_1474</directory>')         
            indent.dec()
            indent.write(file, '</section>')      
            indent.dec()
            indent.write(file, '</sections>')
            indent.write(file, '<course>')
            indent.inc()
            indent.write(file, '<courseid>1053</courseid>')
            indent.write(file, '<title>XXYY_Importer</title>')
            indent.write(file, '<directory>course</directory>')      
            indent.dec()
            indent.write(file, '</course>')


        indent.dec()
        indent.write(file, '</contents>')

        # if backup is from course, there need to be section directory, with file in it... to be implemented

        # settings....
       
        indent.write(file, '<settings>')
        indent.inc()
        
        rootSettings = {'users' : 0,
            'anonymize' : 0,
            'role_assignments' : 0,
            'activities' : 1,
            'blocks' : 0,
            'filters' : 0,
            'comments' : 0,
            'badges' : 0,
            'calendarevents' : 0,
            'userscompletion' : 0,
            'logs' : 0,
            'grade_histories' : 0,
            'questionbank' : 1,
            'groups' : 0
        }

        for (key,value) in rootSettings.items():
            self.writeSetting(file, indent, 'root', key, value)

        if self.backupType == 'course':
            self.writeSetting(file, indent, 'section', 'section_1474_included', 1, section = 'section_1474')
            self.writeSetting(file, indent, 'section', 'section_1474_userinfo', 0, section = 'section_1474')

        for category in self.categories.values():
            self.writeSetting(file, indent, 'activity', 'quiz_' + str(category.quizId) + '_included', 1, activity = 'quiz_' + str(category.quizId))
            self.writeSetting(file, indent, 'activity', 'quiz_' + str(category.quizId) + '_userinfo', 0, activity = 'quiz_' + str(category.quizId))


        indent.dec()
        indent.write(file, '</settings>')

        
        # tail

        indent.dec()
        indent.write(file, '</information>')
        indent.dec()
        indent.write(file, '</moodle_backup>')


        file.close()

    def writeSetting(self, file, indent, level, name, value, section = None, activity = None):
        
        indent.write(file, '<setting>')
        indent.inc()
        indent.write(file, '<level>' + level + '</level>')

        if activity is not None:
            indent.write(file, '<activity>' + activity + '</activity>')

        if section is not None:
            indent.write(file, '<section>' + section + '</section>')

        indent.write(file, '<name>' + name + '</name>')
        indent.write(file, '<value>' + str(value) + '</value>')
        indent.dec()
        indent.write(file, '</setting>')

    def createQuizFiles(self):

        for category in self.categories.values():
            category.writeQuiz(self.activityDir, self.args)
            pass

        pass

    def createCategoriesFile(self):
        filename = os.path.join(self.root, 'questions.xml')
        questionFile = open(filename, 'w', encoding = 'utf-8')
        filesFile = open(os.path.join(self.root, 'files.xml'), 'w', encoding = 'utf-8')

        # write head
        questionFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        questionFile.write('<question_categories>\n')
        
        filesFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        filesFile.write('<files>\n')

        # write categories
        for category in self.categories.values():
            category.writeXml(questionFile, self.args)
            category.writeExportFiles(filesFile, self.args, self.root)
        
        # write tail
        questionFile.write('</question_categories>')
        filesFile.write('</files>')

        
        questionFile.close()
        filesFile.close()
        
