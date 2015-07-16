from pygments.lexer import inherit
from pygments_markdown_lexer.lexer import *


class BlueprintLexer(MarkdownLexer):
    name = 'API Blueprint'
    aliases = ['apiblueprint', 'apib']
    filenames = ['*.apib']

    tokens = {
        'root': [
            (r'^(#+)(.+)(\[)(.+)(\])$', bygroups(Markdown.Markup, Markdown.Heading, Markdown.Markup, Markdown.CodeBlock, Markdown.Markup)),
            inherit
        ]
    }

