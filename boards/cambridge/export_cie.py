"""Exports the Cambridge International AS & A Level Sociology (9699) question bank to the site's data format.

Usage: python3 boards/cambridge/export_cie.py --bank "<Sociology/CIE/Question Bank>" [--images]
Writes boards/cambridge/data/{questions,papers,topics,spec,weighting}.json and, with --images,
public/img/cie/<paper>/<name>.webp (lossless WebP from the bank's PNG crops).
"""
import argparse, base64, hashlib, io, json, os, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / 'data'
IMG = REPO / 'public' / 'img' / 'cie'

# site topic per syllabus sub-topic: slug, name
TOPICS = {
    '1.1': ('socialisation-and-culture', 'Socialisation, culture and the social construction of reality'),
    '1.2': ('social-control-and-deviance', 'Social control, conformity and resistance'),
    '1.3': ('social-identity', 'Social identity and change: class, gender, ethnicity and age'),
    '2.1': ('research-methods', 'Types of data, research methods and research design'),
    '2.2': ('positivism-and-interpretivism', 'Approaches to research: positivism, interpretivism and realism'),
    '2.3': ('research-issues', 'Research issues: validity, reliability, ethics and bias'),
    '3.1': ('perspectives-on-the-family', 'Perspectives on the role of the family'),
    '3.2': ('family-diversity-and-change', 'Family diversity and social change'),
    '4.1': ('gender-roles-and-family-life', 'Gender equality and experiences of family life'),
    '4.2': ('childhood-and-age', 'Childhood, youth, old age and family life'),
    '5.1': ('role-of-education', 'Theories about the role of education'),
    '5.2': ('education-and-social-mobility', 'Education and social mobility'),
    '5.3': ('curriculum', 'Influences on the curriculum'),
    '6.1': ('intelligence-and-attainment', 'Intelligence and educational attainment'),
    '6.2': ('social-class-and-attainment', 'Social class and educational attainment'),
    '6.3': ('ethnicity-and-attainment', 'Ethnicity and educational attainment'),
    '6.4': ('gender-and-attainment', 'Gender and educational attainment'),
    '7.1': ('perspectives-on-globalisation', 'Perspectives on globalisation'),
    '7.2': ('globalisation-and-identity', 'Globalisation and identity'),
    '7.3': ('globalisation-power-and-politics', 'Globalisation, power and politics'),
    '8.1': ('global-poverty-and-inequality', 'Globalisation, poverty and inequalities'),
    '8.2': ('globalisation-and-migration', 'Globalisation and migration'),
    '8.3': ('globalisation-and-crime', 'Globalisation and crime'),
    '9.1': ('traditional-and-new-media', 'Traditional media and the new media'),
    '9.2': ('media-ownership-and-control', 'Theories of the media and influences on media content'),
    '9.3': ('impact-of-new-media', 'The impact of the new media'),
    '10.1': ('media-representations', 'Media representations of class, gender, ethnicity and age'),
    '10.2': ('media-effects', 'Models of media effects'),
    '10.3': ('media-and-behaviour', 'The impact of the media on behaviour'),
    '11.1': ('religion-and-society', 'Religion and society: definitions and theories'),
    '11.2': ('religion-and-social-order', 'Religion and social order'),
    '11.3': ('religion-and-social-change', 'Religion as a source of social change'),
    '12.1': ('secularisation', 'The secularisation debate'),
    '12.2': ('gender-feminism-and-religion', 'Gender, feminism and religion'),
    '12.3': ('religion-and-postmodernity', 'Religion and postmodernity'),
}
GROUP = {1: 'Paper 1: Socialisation and identity', 2: 'Paper 1: Methods of research', 3: 'Paper 2: The family', 4: 'Paper 2: The family',
         5: 'Paper 3: Education', 6: 'Paper 3: Education', 7: 'Paper 4: Globalisation', 8: 'Paper 4: Globalisation',
         9: 'Paper 4: Media', 10: 'Paper 4: Media', 11: 'Paper 4: Religion', 12: 'Paper 4: Religion'}
PAPER_NAMES = {1: 'Socialisation, Identity and Methods of Research', 2: 'The Family', 3: 'Education', 4: 'Globalisation, Media and Religion'}
FMT = {'Describe two (4 marks)': 'Describe two', 'Explain two': 'Explain two', 'Explain a view': 'Explain a view',
       'Argument against a view': 'Against a view', 'Arguments against a view': 'Against a view', 'Essay': 'Essay'}
SER = {'March': 'm', 'June': 's', 'November': 'w'}


def load_bank(bank):
    js = Path(bank, 'data', 'index.js').read_text(encoding='utf-8')
    out = subprocess.run(['node', '-e', 'global.window={};eval(require("fs").readFileSync(0,"utf8"));process.stdout.write(JSON.stringify(window.QB))'],
                         input=js, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def sub(code):  # '1.2(d)' -> '1.2'
    return code.split('(')[0]


def lab(l):  # '3(a)' -> '3a'
    return re.sub(r'[()]', '', l)


def series_slug(p):
    return 'specimen' if p['src'] == 'specimen' else p['series'].lower().replace(' ', '-')


def ao_of(q):
    m = [x for x in q['mc'] if x.startswith('Marks: ')]
    if m:
        d = dict(re.findall(r'(AO\d) (\d+)', m[0]))
        ao = [int(d.get(f'AO{i}', 0)) for i in (1, 2, 3)]
        return ao, ','.join(f'AO{i}={ao[i-1]}' for i in (1, 2, 3) if ao[i - 1])
    return [0, 0, 0], ' + '.join(q['ao'].split(','))


def convert(job):
    bundle, src, dest, want = job
    from PIL import Image
    s = Path(src).read_text()
    items = dict(re.findall(r'"([^"]+\.png)":\s*"data:image/png;base64,([^"]+)"', s))
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for name in want:
        if name not in items: continue
        out = dest / (name[:-4] + '.webp')
        if out.exists(): n += 1; continue
        im = Image.open(io.BytesIO(base64.b64decode(items[name])))
        if im.mode not in ('RGB', 'L'): im = im.convert('RGB')
        im.save(out, 'WEBP', lossless=True, method=4)
        n += 1
    return bundle, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bank', required=True)
    ap.add_argument('--images', action='store_true')
    a = ap.parse_args()
    D = load_bank(a.bank)
    img_dir = Path(a.bank, 'data', 'img')
    have = {}
    for f in img_dir.glob('*.js'):
        have[f.stem] = set(re.findall(r'"([^"]+\.png)":', f.read_text()))

    papers, questions, jobs = [], [], []
    pmeta = {p['id']: p for p in D['papers']}
    for p in D['papers']:
        n = p['paper']
        qual = 'AS' if n <= 2 else 'A level'
        sl = series_slug(p)
        comp = p['comp'] if p['src'] == 'exam' else str(n)
        pid = f"9699-{comp}-{p['id'].split('_')[0].upper()}"
        qs = [q for q in D['q'] if q['p'] == p['id']]
        want = []
        rec_ids = []
        for q in qs:
            ao, aot = ao_of(q)
            A = [s for s, k in q['st'] if k == 'A']
            subs = list(dict.fromkeys(sub(s) for s in A)) or list(dict.fromkeys(sub(s) for s, k in q['st']))
            topics = [TOPICS[s][0] for s in subs if s in TOPICS]
            main = int(subs[0].split('.')[0]) if subs else n
            area = GROUP[main].split(': ')[1] if n == 4 else GROUP[main].split(': ')[1]
            if n == 4:  # Paper 4 area comes from the section the question sits in
                sec = next((x for x in q['mc'] if x.startswith('Section')), '')
                area = sec.split(': ')[1] if ': ' in sec else area
            notes = [x for x in q['mc'] if not re.match(r'(Section|Marks:|Cambridge publishes no AO)', x)]
            cropname = lambda f: f'/img/cie/{p["id"]}/{f[:-4]}.webp' if f and f in have.get(p['id'], ()) else None
            for f in (q['qi'], q['mi'], q['ei'] if q.get('et') else None):
                if f and f in have.get(p['id'], ()): want.append(f)
            et = re.sub(r'\s+', ' ', q.get('et') or '').strip()
            qid = f'{pid}-{lab(q["l"])}'
            rec_ids.append(qid)
            questions.append({
                'id': qid, 'paperId': pid, 'bundle': p['id'], 'spec': '9699', 'comp': comp if p['src'] == 'exam' else None,
                'paper': f'Paper {n}', 'level': qual, 'series': 'Specimen' if p['src'] == 'specimen' else p['series'],
                'year': p['year'], 'question': q['l'], 'marks': q['m'], 'ao': ao, 'aoText': aot,
                'format': FMT.get(q['fmt'], q['fmt']), 'commands': q['cmd'],
                'crop': cropname(q['qi']), 'msCrop': cropname(q['mi']), 'erCrop': cropname(q['ei']) if et else None,
                'text': q['qt'], 'msText': q['mt'], 'erText': '', 'erBrief': et[:400],
                'statements': A or [s for s, k in q['st']], 'topics': topics, 'area': area,
                'skills': q['sk'], 'mistakes': notes, 'choice': (n in (1, 2) and q['l'] in ('4', '5')) or n == 4,
                'difficulty': None, 'facility': None, 'notCurrentSpec': False, 'level_of_response': 'level_of_response' in q['fl'],
                'features': [], 'context': [], 'item': False, 'lds': False, 'mcqAnswers': None, 'msBands': [],
                'paperName': PAPER_NAMES[n], 'specNote': '', 'stemCrop': None, 'stemId': None, 'stemText': '', 'sourceLines': '',
            })
        papers.append({
            'id': pid, 'bundle': p['id'], 'kind': 'specimen' if p['src'] == 'specimen' else 'exam', 'series': 'Specimen' if p['src'] == 'specimen' else p['series'],
            'year': p['year'], 'spec': '9699', 'qual': qual, 'paper': f'Paper {n}', 'paperNo': str(n), 'comp': comp,
            'name': PAPER_NAMES[n], 'total': p['total'], 'questions': rec_ids, 'reprints': p.get('twins') or [],
            'slug': f'{sl}-9699-{comp}' if p['src'] == 'exam' else f'specimen-9699-{n}',
            'source': 'Cambridge', 'files': {'qp': p['qp'], 'ms': p['ms'], 'er': p['er']},
        })
        jobs.append((p['id'], str(img_dir / f"{p['id']}.js"), str(IMG / p['id']), want))

    # a sub-topic no question assesses directly takes the questions that use it as context
    assessed = {t for q in questions for t in q['topics']}
    for q in questions:
        bq = next(x for x in D['q'] if x['p'] == q['bundle'] and f"{q['paperId']}-{lab(x['l'])}" == q['id'])
        for s_, k in bq['st']:
            t = TOPICS.get(sub(s_), (None,))[0]
            if k == 'C' and t and t not in assessed and t not in q['topics']: q['topics'].append(t)
    # topics
    spec_sections = {s['code']: s for s in D['spec']}
    topics = []
    for code, (slug, name) in TOPICS.items():
        s = spec_sections[code]
        tn = int(code.split('.')[0])
        tq = [q for q in questions if slug in q['topics']]
        topics.append({
            'slug': slug, 'name': name, 'code': code, 'group': GROUP[tn], 'strand': GROUP[tn], 'paper': GROUP[tn],
            'papers': sorted({q['paper'] for q in tq}), 'option': None,
            'asOrA': 'AS and A level' if tn <= 4 else 'A level only',
            'statements': [st['id'] for st in s['st']],
            'statementText': {st['id']: st['t'] for st in s['st']}, 'statementShort': {st['id']: '' for st in s['st']},
            'asStatements': [st['id'] for st in s['st']] if tn <= 4 else [], 'levels': {st['id']: None for st in s['st']},
            'parts': len(tq), 'marks': sum(q['marks'] for q in tq), 'essays': sum(1 for q in tq if q['format'] == 'Essay'), 'mcq': 0,
            'syllabusTopic': spec_sections[str(tn)]['title'],
        })
    empty = [t['slug'] for t in topics if not t['parts']]
    if empty: print('topics with no questions:', empty)
    # spec
    spec = []
    for s in D['spec']:
        tn = int(s['code'].split('.')[0])
        spec.append({'code': s['code'], 'title': s['title'], 'paper': (tn + 1) // 2 if tn <= 4 else (3 if tn <= 6 else 4),
                     'aLevelOnly': tn > 4, 'topic': TOPICS.get(s['code'], (None,))[0],
                     'statements': [{'id': st['id'], 'text': st['t'], 'guidance': st.get('g', ''), 'as': tn <= 4,
                                     'topics': [TOPICS[s['code']][0]] if s['code'] in TOPICS else []} for st in s['st']]})
    # weighting: marks by syllabus topic (1..12) per paper
    areas = {s['code']: s['title'] for s in D['spec'] if '.' not in s['code']}
    byPaper = {}
    for q in questions:
        main = q['statements'][0].split('.')[0] if q['statements'] else None
        if main: byPaper.setdefault(q['paperId'], {}).setdefault(main, 0); byPaper[q['paperId']][main] += q['marks']
    OUT.mkdir(parents=True, exist_ok=True)
    order = {'March': 0, 'June': 1, 'November': 2}
    papers.sort(key=lambda p: (p['kind'] != 'exam', -p['year'], -order.get(p['series'].split(' ')[0], 0), p['comp']))
    for name, obj in [('questions', questions), ('papers', papers), ('topics', topics), ('spec', spec), ('weighting', {'areas': areas, 'byPaper': byPaper})]:
        (OUT / f'{name}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=0))
    print(f'{len(papers)} papers, {len(questions)} parts, {len(topics)} topics, untopiced: {sum(1 for q in questions if not q["topics"])}')
    missing = [q['id'] for q in questions if not q['crop']]
    print('no question crop:', len(missing), missing[:5], ' no MS crop:', sum(1 for q in questions if not q['msCrop']))
    if a.images:
        with ProcessPoolExecutor() as ex:
            for b, n in ex.map(convert, jobs):
                pass
        print('images done:', sum(1 for _ in IMG.rglob('*.webp')))


if __name__ == '__main__':
    main()
