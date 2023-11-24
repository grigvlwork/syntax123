class Part:
    def __init__(self, code='', explanation=''):
        self.code = code
        self.explanation = explanation
        self.checked = False


class Task:
    def __init__(self):
        self.tasks = []
        self.comment = ''

    def parse(self, text):
        i = 1
        while f'<code{i}>' in text:
            begin = text.find(f'<code{i}>') + len(f'<code{i}>')
            end = text.find(f'</code{i}>')
            code = text[begin:end].split('```\n')[1]
            if f'<explanation{i}>' in text:
                begin = text.find(f'<explanation{i}>') + len(f'<explanation{i}>')
                end = text.find(f'</explanation{i}>')
                explanation = text[begin:end]
            else:
                explanation = ''
            self.tasks.append(Part(code, explanation))
            i += 1
        if '<comment>' in text:
            begin = text.find('<comment>') + len('<comment>')
            end = text.find('</comment>')
            self.comment = text[begin:end]

    def get_text(self):
        text = ''
        for i in range(len(self.tasks)):
            text += f'<code{i + 1}>\n\n```\n{self.tasks[i].code}\n```\n\n</code{i + 1}>' + \
                    f'\n<explanation{i + 1}>\n{self.tasks[i].explanation}\n</explanation{i + 1}>\n'
        text += f'<comment>\n{self.comment}\n</comment>'
        return text

    def del_part(self, part_id):
        if part_id < len(self.tasks):
            self.tasks.pop(part_id)

    def add_part(self):
        self.tasks.append(Task())

    def is_ready(self):
        for t in self.tasks:
            if not t.checked:
                return False
        return True
