"""Generate the completed lab PDF from its Markdown source (needs reportlab)."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def main():
    root = Path(__file__).resolve().parent.parent
    source = root / 'docs' / 'lab04-answers.md'
    output = root / 'lab04-IT24103430.pdf'
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9.5
    styles['BodyText'].leading = 14
    styles['BodyText'].spaceAfter = 8
    story = []
    for block in source.read_text().split('\n\n'):
        block = block.strip()
        if not block:
            continue
        style = 'BodyText'
        for prefix, heading_style in [('### ', 'Heading2'),
                                      ('## ', 'Heading1'), ('# ', 'Title')]:
            if block.startswith(prefix):
                block = block[len(prefix):]
                style = heading_style
                break
        story.append(Paragraph(escape(block).replace('\n', ' '), styles[style]))
        if style == 'Title':
            story.append(Spacer(1, 10))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(42, 24, 'IT3012 Practical 04 | IT24103430')
        canvas.drawRightString(A4[0] - 42, 24, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=42,
                            leftMargin=42, topMargin=40, bottomMargin=40,
                            title='IT3012 Practical 04 - Completed Exercise',
                            author='IT24103430')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == '__main__':
    main()
