char = ['C']
for i in range(9, 10):
    for c in char:
        name = str(i) + c + '.txt'
        with open(name, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            lines.pop()
            lines.pop()
            lines.pop()
            
            lines.pop()
            lines.pop()
            lines.pop()
            
            lines.pop()
            lines.pop()
            lines.pop()
            
            lines.pop()
            lines.append('Created by "AjinGixtas (https://github.com/AjinGixtas)')
            for line in lines:
                print(line)