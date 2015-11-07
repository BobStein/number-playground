from django import template


register = template.Library()


@register.inclusion_tag('word-diagram-call.html')
def word_diagram(word):
    sbj = word.spawn(word.sbj)
    vrb = word.spawn(word.vrb)
    obj = word.spawn(word.obj)
    return dict(
        sbj=sbj.txt,
        vrb=vrb.txt,
        obj=obj.txt,
        txt=word.txt,
        num=float(word.num),
    )


@register.inclusion_tag('results.html')
def show_results():
    return {'choices': 'moo'}
