import CodeRunnerGenerator as CRG
import os
from QuestionTypes import Essay
from QuestionCategories import CategoryInfo
from MoodleImporterGenerator import MoodleImport
from random import randrange

class ComputerGraphics(object):
    """description of class"""

    def __init__(self, home, args):
        super(ComputerGraphics, self).__init__()

        self.home = home
        self.args = args

    def createBackup(self):
        MAX_MARK = 12
        Q1 = 6
        Q2 = 3

        moodle = MoodleImport(self.args)
        mainCategory = 'CG21'
        workDir = self.args.workDir

        # repeat until it is possible to create a new quiz
        complete = False
        limits = [0, Q1, Q2, 0]

        quizNr = 1

        while not complete:
            allTags = self.updateData()

            quiz = []
            quizTags = []

            for mark in range(1,3):

                # adding Qmark questions
                if len(allTags[mark]) < limits[mark]:
                    print('No more Q', mark, ' questions...', sep = '')
                    complete = True
                    break

                for i in range(limits[mark]):
                    question = self.getQuestion(tags = allTags[mark], mark = mark, quizTags = quizTags)
                    if question is None:
                        complete = True
                        break

                    quiz.append(question)
                    quizTags.append(question.name)
                    #print(quizTags)
            
            # quiz can be saved...
            if not complete:
                print('quiz can be saved...')
                category = f'{mainCategory}/Quiz{quizNr:02d}'
                moodle.addQuiz(category, quiz, CategoryInfo(self.home, readOnlyDescription = True))
                quizNr += 1
            
            
        
        self.args.workDir = workDir
        self.args.category = mainCategory
        moodle.flush()


    def updateData(self):

        allTags = [set(), set(), set(), set()]
        for (key,value) in sorted(self.questions.items()):
            for tag in value:
                allTags[key].add(tag)

        #print('ALLTAGS\n', allTags)
        return allTags


    def getQuestion(self, tags, mark, quizTags):
        if len(tags) == 0:
            return None

        tagList = list(tags)

        done = False
        while not done:
            idx = 0
            if len(tagList) > 1:
                idx = randrange(len(tagList))
            tag = tagList[idx]

            if tag not in quizTags:
                # trovata domanda buona
                done = True

                try:
                    questionList = self.questions[mark][tag]

                except Exception as e:
                    print(tag, 'is not in', self.questions[mark].keys())

                idx = randrange(len(questionList))

                found = questionList.pop(idx)
                print(mark, '::', found.name)

                # se la lista è vuota, eliminala
                if len(questionList) == 0:
                    self.questions[mark].pop(tag)
                    tags.remove(tag)

                return found

        return None

    def readFiles(self):
        self.args.workDir = self.home
        self.outDir = os.path.join(self.home, 'out')

        os.makedirs(self.outDir, exist_ok = True)

        files = [f for f in os.listdir(self.home) if os.path.isfile(os.path.join(self.home, f))]

        questions = {}
        tags = [[], set(), set(), set()]
        counts = [0] * 4

        for file in files:

            if not file.lower().endswith('.txt'):
                continue

            self.args.questionFile = file
            self.args.xml = os.path.join('out', file) + '.xml'
            questionList = CRG.readQuestions(self.args)

            for question in questionList:
                tag = question.name
                mark = int(question.mark)

                tags[mark].add(tag)
                counts[mark] += 1

                if not mark in questions:
                    questions[mark] = {tag : []}
                elif not tag in questions[mark]:
                    questions[mark][tag] = []

                questions[mark][tag].append(question)

            #CRG.storeQuestionList(questionList, self.args)

        print('TAGS')
        for (idx, tag) in enumerate(tags):
            if idx == 0:
                continue
            print(idx, '::', counts[idx], '\n\t', tag)

        for (key,value) in sorted(questions.items()):
            #print(key, value)
            for (tag, questionList) in value.items():
                print('\t', tag,':',len(questionList))

        self.counts = counts
        self.tags = tags
        self.questions = questions
        # per mark, list of {list of questions per tag}

################ Main #####################


def CGmain():

    HOME_DIR = 'G:\\Didattica\\Computer Graphics\\Esami\\2021\\AEG'

    args = CRG.parseArguments()

    cg = ComputerGraphics(HOME_DIR, args)
    cg.readFiles()
    cg.createBackup()




if __name__ == "__main__":
    CGmain()


