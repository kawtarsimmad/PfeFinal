from django import template

register = template.Library()

@register.filter(name='first_line_bold_italic')
def first_line_bold_italic(value):
    lines = value.split('\n')
    if lines:
        lines[0] = f'<span class="first-line">{lines[0]}</span>'
    return '\n'.join(lines)


@register.filter(name='first_paragraph_bold_italic')
def first_paragraph_bold_italic(value):
    paragraphs = value.split('\n\n')  # Diviser le contenu en paragraphes
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():  # Ignorer les paragraphes vides
            paragraphs[i] = f'<span class="first-paragraph">{paragraph}</span>'
    return '\n'.join(paragraphs)

@register.filter(name='first_letter_bold_upper')
def first_letter_bold_upper(value):
    paragraphs = value.split('\n')  # Diviser le contenu en paragraphes
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():  # Ignorer les paragraphes vides
            first_letter = paragraph.strip()[0].upper()
            paragraph = f'<span class="first-letter">{first_letter}</span>{paragraph.strip()[1:]}'
            paragraphs[i] = paragraph
    return '\n'.join(paragraphs)


@register.filter(name='add_initial_space')
def add_initial_space(value):
    paragraphs = value.split('\n\n')
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():  # Ignorer les paragraphes vides
            paragraphs[i] = f' {paragraph}'
    return '\n'.join(paragraphs)


@register.filter(name='last_line_bold_italic')
def last_line_bold_italic(value):
    paragraphs = value.split('\n\n')
    for i, paragraph in enumerate(paragraphs):
        lines = paragraph.split('\n')
        if lines:  # Vérifier s'il y a des lignes dans le paragraphe
            lines[-1] = f'<span class="last-line">{lines[-1]}</span>'
            paragraphs[i] = '\n'.join(lines)
    return '\n\n'.join(paragraphs)