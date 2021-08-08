def text_transform(text, filenames):
    commands = ['br>', 'p>', 'b>', 'h>', 'image ', 'a ', '/p>', '/b>', '/h>', '/a>']
    text = text.split('<')
    start_p = False
    tegs = []
    res = ""
    for elem in text:
        if any([elem.lower().startswith(com) for com in commands]):
            if elem.lower().startswith('br>'):
                res += "<br>"
            elif elem.lower().startswith('p>'):
                tegs.append('p')
                if not start_p:
                    res += "<p>"
                    start_p = True
                res += "<i>"
                res += elem[2:]
            elif elem.lower().startswith('/p>'):
                if tegs[-1] == 'p':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}>'
                res += "<i>"
                res += elem[3:]
            elif elem.lower().startswith('b>'):
                if not start_p:
                    res += "<p>"
                    start_p = True
                tegs.append('b')
                res += "<b>"
                res += elem[2:]
            elif elem.lower().startswith('/b>'):
                if tegs[-1] == 'b':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}>'
                res += "</b>"
                res += elem[3:]
            elif elem.lower().startswith('h>'):
                if start_p:
                    res += "</p>"
                tegs.append('h')
                res += "<p class='title'>"
                res += elem[2:]
            elif elem.lower().startswith('/h>'):
                if tegs[-1] == 'h':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}>'
                res += "</p>"
                start_p = False
                res += elem[3:]
            elif elem.lower().startswith('image') and elem.lower().split()[1].split('>')[0].isdigit():
                if start_p:
                    res += "</p>"
                    start_p = False
                if len(filenames) <= int(elem.lower().split()[1].split('>')[0]) - 1 or int(elem.lower().split()[1].split('>')[0]) - 1 < 0:
                    return f'Error: нет такой картинки {elem.lower().split()[1].split(">")[0]}'
                res += f"<img src='{filenames[int(elem.lower().split()[1].split('>')[0])-1]}'>"
            elif elem.lower().startswith('a') and elem.find('>') > -1:
                if not start_p:
                    res += "<p>"
                    start_p = True
                tegs.append('a')
                res += f"<a href='{elem.split()[1].split('>')[0]}'>"
                res += elem.split('>')[1]
            elif elem.lower().startswith('/a>'):
                if tegs[-1] == 'a':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}> 1'
                res += "</a>"
                res += elem[3:]
        else:
            if not start_p:
                res += "<p>"
                start_p = True
            res += elem
    return res


print(text_transform("text<h>lol<p>lol<a site-href>title</p></h>", []))
print(text_transform("text<h>lol<p>lol<a site-href>title<image 0></a></p></h>", []))
print(text_transform("text<h>lol<p>lol<a site-href>title<image 1></a></p></h>", ['a']))
print(text_transform("text<h>lol<p>lol<a site-href>title<image 2></a></p></h>", ['a']))