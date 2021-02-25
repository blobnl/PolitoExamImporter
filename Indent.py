# class to manage proper file indentation

class Indent:
    def __init__(self):
        self.level = 0

    def inc(self):
        self.level += 1

    def dec(self):
        if self.level > 0:
            self.level -= 1

    def __str__(self):
        return "\t" * self.level

    def write(self, file, line):
        file.write(str(self) + line + '\n')
