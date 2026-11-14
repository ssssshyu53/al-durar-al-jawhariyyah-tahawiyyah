#!/usr/bin/env python3
import argparse
import json
import os
import re

_PARSER = argparse.ArgumentParser()
_PARSER.add_argument('--mode', choices=('verbatim', 'edited'), default='verbatim')
_ARGS, _ = _PARSER.parse_known_args()
IS_EDITED = (_ARGS.mode == 'edited')

_ENG = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_ENG)
out_dir = os.path.join(_REPO, 'الدُّررُ_الجوهرية_على_متن_العقيدة_الطحاوية_النسخة_المحررة' if IS_EDITED else 'الدُّررُ_الجوهرية_على_متن_العقيدة_الطحاوية')
os.makedirs(out_dir, exist_ok=True)

EDIGITS = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')

def to_e(n):
    return str(n).translate(EDIGITS)

LESSON_SPECS = [
    (1, '01_الدرس_الأول_مقدمة_الكتاب_وترجمة_الإمام_الطحاوي_والتوحيد_والخلق_والتقدير.md', 'اللقاء الأول: مقدمة الكتاب، وترجمة الإمام الطحاوي، وباب التوحيد والخلق والتقدير', 'مقدمة الكتاب والتوحيد والتقدير'),
    (2, '02_الدرس_الثاني_نفوذ_المشيئة_ونبوة_محمد_والقرآن_كلام_الله_ونفي_التشبيه.md', 'اللقاء الثاني: نفوذ المشيئة، ونبوة محمد ﷺ، والقرآن كلام الله، ونفي التشبيه', 'نفوذ المشيئة والنبوة وكلام الله'),
    (3, '03_الدرس_الثالث_رؤية_المؤمنين_لربهم_ولزوم_التسليم_والتنزيه_والمعراج_والحوض_والشفاعة.md', 'اللقاء الثالث: رؤية المؤمنين لربهم، ولزوم التسليم، والتنزيه، والمعراج، والحوض، ومقدمة الشفاعة', 'الرؤية والتسليم والمعراج والحوض'),
    (4, '04_الدرس_الرابع_الشفاعة_والميثاق_والقدر_واللوح_والقلم.md', 'اللقاء الرابع: الشفاعة، والميثاق الأول، وسر القدر، واللوح والقلم', 'الشفاعة والميثاق وسر القدر'),
    (5, '05_الدرس_الخامس_العرش_والكرسي_والملائكة_والأنبياء_والقرآن_وأحكام_أهل_الكبائر_والإيمان.md', 'اللقاء الخامس: العرش والكرسي، والملائكة والأنبياء والكتب، وأحكام أهل الكبائر، وحقيقة الإيمان', 'العرش والرسل وأهل الكبائر والإيمان'),
    (6, '06_الدرس_السادس_أركان_الإيمان_والصلاة_خلف_الأئمة_وعذاب_القبر_والبعث_والاستطاعة.md', 'اللقاء السادس: أركان الإيمان، والصلاة خلف الأئمة ولزوم الجماعة، وعذاب القبر، والبعث، والاستطاعة', 'أركان الإيمان والإمامة والبعث والقدر'),
    (7, '07_الدرس_السابع_الدعاء_للأموات_وفضل_الصحابة_والأولياء_وأشراط_الساعة_ووسطية_الإسلام.md', 'اللقاء السابع: الدعاء للأموات، وفضل الصحابة والأولياء، وأشراط الساعة، ووسطية الإسلام وخاتمة المتن', 'الدعاء للأموات والصحابة وخاتمة المتن'),
]

json_name = 'book_data_edited.json' if IS_EDITED else 'book_data.json'
json_path = os.path.join(_ENG, json_name)
if not os.path.exists(json_path):
    print(f"File not found: {json_path}")
    exit(0)

book_json = json.load(open(json_path, encoding='utf-8'))
lessons_data = {l['lesson_num']: l for l in book_json.get('lessons', [])}
units_by_lesson = {}
for u in book_json.get('units', []):
    lnum = u['lesson_num']
    if lnum not in units_by_lesson:
        units_by_lesson[lnum] = []
    units_by_lesson[lnum].append(u)

full_volume_lines = [
    f"# {book_json.get('title', 'الدُّرَرُ الجَوْهَرِيَّة عَلَى مَتْنِ العَقِيدَةِ الطَّحَاوِيَّة')}",
    f"## {book_json.get('subtitle', 'شَرْحُ مَتْنِ بَيَانِ عَقِيدَةِ أَهْلِ السُّنَّةِ وَالجَمَاعَةِ')}",
    "",
    f"**المتن:** {book_json.get('author_matn', '')}  ",
    f"**الشرح:** {book_json.get('author_sharh', '')}  ",
    f"**النسخة:** {'النسخة المحررة المهذبة (بكلام الشيخ بلفظه دون اختصار مع الاقتصار على مقدمة اللقاء الأول وخاتمة الأخير وتهذيب التكرار المتتابع)' if IS_EDITED else 'النسخة الحرفية الكاملة كما ألقيت'}  ",
    "",
    "---",
    "",
]

for lnum, fname, full_title, short_title in LESSON_SPECS:
    if lnum not in units_by_lesson:
        continue
    u_list = units_by_lesson[lnum]
    pinfo = lessons_data.get(lnum, {})
    disp_title = full_title.replace('اللقاء ', 'المحاضرة رقم ') if IS_EDITED else full_title
    
    lesson_md = []
    lesson_md.append(f"# {disp_title}")
    lesson_md.append("")
    if pinfo.get('url'):
        lesson_md.append(f"> 🔗 **رابط المحاضرة الأصلية:** [{pinfo.get('url')}]({pinfo.get('url')}) — المدة: {pinfo.get('duration_min', 0)} دقيقة ({to_e(pinfo.get('duration_min', 0))} د)")
        lesson_md.append("")
    lesson_md.append("---")
    lesson_md.append("")

    for u in u_list:
        if u.get('heading'):
            lesson_md.append(f"## {u['heading']}")
            lesson_md.append("")
        
        if u.get('matn_raw'):
            lesson_md.append("> ### [ مَتْنُ العَقِيدَةِ الطَّحَاوِيَّةِ ]")
            for ml in u['matn_raw'].splitlines():
                if ml.strip():
                    lesson_md.append(f"> **{ml.strip()}**")
            lesson_md.append("")
            lesson_md.append("---")
            lesson_md.append("")

        for p_html in u.get('sharh_paras_html', []):
            p_text = re.sub(r'<span class="ayah(?:-ref)?">([^<]+)</span>', r'\1', p_html)
            p_text = re.sub(r'<strong>([^<]+)</strong>', r'**\1**', p_text)
            p_text = re.sub(r'<[^>]+>', '', p_text)
            lesson_md.append(p_text.strip())
            lesson_md.append("")

        if u.get('glosses'):
            lesson_md.append("")
            lesson_md.append("##### الحواشي ومعاني المفردات:")
            for g in u['glosses']:
                lesson_md.append(f"- **{g['term']}**: {g['gloss']}")
            lesson_md.append("")

        lesson_md.append("")

    file_path = os.path.join(out_dir, fname)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lesson_md).strip() + '\n')
    print(f"Saved: {file_path}")

    full_volume_lines.extend(lesson_md)
    full_volume_lines.append("")
    full_volume_lines.append("---")
    full_volume_lines.append("")

vol_name = 'الدُّررُ_الجوهرية_على_متن_العقيدة_الطحاوية_النسخة_المحررة.md' if IS_EDITED else 'الدُّررُ_الجوهرية_على_متن_العقيدة_الطحاوية.md'
vol_path = os.path.join(out_dir, vol_name)
with open(vol_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(full_volume_lines).strip() + '\n')
print(f"Saved Full Volume Markdown: {vol_path}")
