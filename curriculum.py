"""Build the public bilingual curriculum library from its Markdown manuscripts."""
from pathlib import Path
import re
from html import escape

TEXT = {
'es': dict(title='La gran historia de Dios',library='Currículos de escuela dominical',church='Iglesia Río de Gracia',home='Volver a la iglesia',guide='Guía de la maestra',sheets='Hojas del alumno',printall='Imprimir todo / Guardar PDF',printone='Imprimir esta clase',weeks='13 clases semanales · Niños de 8 a 12 años',intro='Material para comprender el carácter de Dios, nuestra necesidad de redención y el evangelio de Jesucristo. Disponible para consultar, usar e imprimir en español e inglés.',open='Ver el currículo',week='Semana',of='de',index='Índice de clases',back='Volver al índice',name='Nombre',date='Fecha',note='Elige la guía o las hojas del alumno antes de imprimir. Cada clase comienza en una página nueva. Puedes guardar un PDF desde el diálogo de impresión.',worksheet='Hoja del alumno',answer='Respuesta esperada',homework='En casa',closing='Cierre',use='Para familias, maestras e iglesias. Consulta el material y úsalo en tus clases; también puedes imprimirlo.',introheading='Antes de comenzar',review='Orientación para la maestra',family='Para conversar en casa'),
'en': dict(title="God’s Great Story",library='Sunday school curricula',church='River of Grace Church',home='Back to the church',guide='Teacher guide',sheets='Student worksheets',printall='Print all / Save PDF',printone='Print this lesson',weeks='13 weekly lessons · Children ages 8–12',intro='Material to understand God’s character, our need for redemption, and the gospel of Jesus Christ. Available to read, use, and print in Spanish and English.',open='View the curriculum',week='Week',of='of',index='Lesson index',back='Back to the index',name='Name',date='Date',note='Choose the teacher guide or student worksheets before printing. Each lesson starts on a new page. You can save a PDF from the print dialog.',worksheet='Student worksheet',answer='Expected answer',homework='At home',closing='Closing',use='For families, teachers, and churches. Read the material and use it in your classes; you can also print it.',introheading='Before you begin',review='Teacher guidance',family='Discuss at home')}

def inline(s):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escape(s))

def markdown(s):
    out=[]
    for block in re.split(r'\n\s*\n',s.strip()):
        if not block.strip(): continue
        lines=block.splitlines()
        if all(l.startswith('|') for l in lines):
            rows=[]
            for i,l in enumerate(lines):
                if re.match(r'^\|[\s|:-]+\|$',l): continue
                tag='th' if i==0 else 'td'
                rows.append('<tr>'+''.join(f'<{tag}>{inline(c.strip())}</{tag}>' for c in l.strip('|').split('|'))+'</tr>')
            out.append('<div class="table-wrap"><table>'+''.join(rows)+'</table></div>')
        elif block.startswith('#'):
            m=re.match(r'^(#{1,6}) (.*)',block)
            level=min(len(m[1])+1,4)
            out.append(f'<h{level}>{inline(m[2])}</h{level}>')
        elif block.strip()=='---': continue
        elif all(l.startswith('- ') for l in lines): out.append('<ul>'+''.join('<li>'+inline(l[2:])+'</li>' for l in lines)+'</ul>')
        else: out.append('<p>'+inline(' '.join(lines))+'</p>')
    return '\n'.join(out)

def shell(lang,title,body,path,aside=''):
    t=TEXT[lang];prefix='/en' if lang=='en' else '';other='' if lang=='en' else '/en'
    canonical='https://riodegraciacr.org'+prefix+path
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · {t['church']}</title><meta name="description" content="{escape(t['intro'])}"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="es" href="https://riodegraciacr.org{path}"><link rel="alternate" hreflang="en" href="https://riodegraciacr.org/en{path}"><link rel="stylesheet" href="/curriculum.css"></head><body><div class="sitebar"><a href="{prefix}/#formacion">← {t['home']}</a><a href="{prefix}/curriculum/">{t['library']}</a><a lang="{'es' if lang=='en' else 'en'}" href="{other}{path}">{'Español' if lang=='en' else 'English'}</a></div><div class="layout">{aside}<main id="inicio">{body}<footer>{t['church']} · {t['use']}</footer></main></div><script src="/curriculum.js" defer></script></body></html>'''

def construir_curriculum(root,output):
    urls=[]
    slug='/curriculum/la-gran-historia-de-dios/'
    for lang,t in TEXT.items():
        prefix='en/' if lang=='en' else ''
        s=(root/'contenido/curriculum'/f'{lang}.md').read_text()
        s=s.split('## Preparación para publicar')[0]
        s=s.replace('Material de trabajo para Iglesia Río de Gracia. Primera versión para revisión de Juan y las maestras.', 'Currículo de escuela dominical de Iglesia Río de Gracia.')
        parts=list(re.finditer(r'^## (\d+) · (.*?)\n(.*?)(?=^## |\Z)',s,re.M|re.S))
        assert len(parts)==13,lang
        nav=''.join(f'<a href="#clase-{m[1]}"><span>{int(m[1]):02}</span> {escape(m[2])}</a>' for m in parts)
        aside=f'<aside aria-label="{t["index"]}"><strong>{t["index"]}</strong><nav>{nav}</nav></aside>'
        lessons=[]
        for m in parts:
            n,title,body=m.groups()
            worksheet=body.split(f'**{t["worksheet"]}.**',1)[1].split(f'**{t["answer"]}:**',1)[0].strip()
            worksheet=re.sub(r'\s+(?=\d+\. )','\n\n',worksheet)
            homework=body.split(f'**{t["homework"]}.**',1)[1].split(f'**{t["closing"]}:**',1)[0].strip()
            student=f'<p>{t["name"]}: __________________________ &nbsp; {t["date"]}: ______________</p>'+markdown(worksheet)+'<div class="writing-space" aria-hidden="true"></div>'+f'<h3>{t["family"]}</h3>'+markdown(homework)
            lessons.append(f'<section class="lesson" id="clase-{n}"><div class="eyebrow">{t["week"]} {n} {t["of"]} 13</div><h2>{escape(title)}</h2><button class="print-one" data-lesson="clase-{n}">{t["printone"]}</button><div class="teacher">{markdown(body)}</div><div class="student">{student}</div><a class="back" href="#inicio">↑ {t["back"]}</a></section>')
        intro=re.sub(r'^# .*?\n','',s[:parts[0].start()])
        tail=s[parts[-1].end():]
        body=f'''<header><div class="eyebrow">{t['church']} · {t['weeks']}</div><h1>{t['title']}</h1><p>{t['intro']}</p><div class="tools"><button id="guide" aria-pressed="true" data-mode="guide">{t['guide']}</button><button id="sheets" aria-pressed="false" data-mode="student">{t['sheets']}</button><button id="print-all">{t['printall']}</button></div><p class="print-note">{t['note']}</p></header><section class="intro">{markdown(intro)}</section>'''+''.join(lessons)+f'<section class="closing">{markdown(tail)}</section>'
        target=output/prefix/slug.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(shell(lang,t['title'],body,slug,aside))
        indexbody=f'''<header><div class="eyebrow">{t['church']}</div><h1>{t['library']}</h1><p>{t['intro']}</p></header><section class="intro"><div class="eyebrow">{t['weeks']}</div><h2>{t['title']}</h2><p>{t['use']}</p><p><a class="button-link" href="{'/en' if lang=='en' else ''}{slug}">{t['open']} →</a></p><p>Español · English</p></section>'''
        index=output/prefix/'curriculum/index.html';index.write_text(shell(lang,t['library'],indexbody,'/curriculum/'))
        urls.extend(['https://riodegraciacr.org/'+prefix+'curriculum/','https://riodegraciacr.org/'+prefix+slug.lstrip('/')])
    return urls
