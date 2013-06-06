import os, sys
from PyQt4.QtCore import Qt, QRegExp
from PyQt4.QtGui import QPalette, QColor, QTextCharFormat, QFont, QFontMetrics, QSyntaxHighlighter, QPlainTextEdit

from edd.utils.efileutils import EFileUtils


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor(color)
    #_color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)

    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('#CB6C2E', 'bold'),
    'operator': format(Qt.darkGray),
    'brace': format(Qt.darkGray),
    'defclass': format('#A9B7C6', 'bold'),
    'string': format('#92C160'),
    'string2': format('#629755'),
    'comment': format('#808080'),
    'self': format('#94558D'),
    'numbers': format(Qt.darkGray),
    'default': format('#B200B2')}


class EHighlighter (QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def', 'as',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False']

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<']

    # Python braces
    braces = ['\{', '\}', '\(', '\)', '\[', '\]']

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in EHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in EHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in EHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),


            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            (r'(__[a-zA-Z_]*(__)?)', 0, STYLES['default']),

            (r'(\'[a-zA-Z_]*(\')?)', 0, STYLES['string']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers'])]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

    def matchMultiline(self, text, delimiter, in_state, style):

        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
                # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class EScriptEditor(QPlainTextEdit):

    def __init__(self):
        QPlainTextEdit.__init__(self)

        font = QFont('Courier New', 9, False)
        self.setFont(font)
        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.lightGray)
        self.setPalette(palette)

        self.setStyleSheet("QPlainTextEdit {background-color: #2B2B2B}, {text-color: yellow}")

        metrics = QFontMetrics(font)
        self.setTabStopWidth(4 * metrics.width(' '))

        EHighlighter(self.document())

        self.__IsControl = False

    def keyPressEvent(self, keyEvent):

        QPlainTextEdit.keyPressEvent(self, keyEvent)

        if keyEvent.key() == Qt.Key_Control:
            self.__IsControl = True

        if keyEvent.key() == Qt.Key_Return and self.__IsControl:

            f = open(os.path.join(ESettings.EDD_PLUGIN_TEMP, "temp.py"), 'w')

            f.write(self.toPlainText())
            f.close()

            sys.path.append(ESettings.EDD_PLUGIN_TEMP)

            nodes = [pluginFileName.replace('.py', '') for pluginFileName in EFileUtils.getFiles(ESettings.EDD_PLUGIN_PATH, '.py', False)]

            pluginModule = __import__('temp', globals(), locals(), [])

            print self.parentWidget()

            print pluginModule

    def keyReleaseEvent(self, keyEvent):

        QPlainTextEdit.keyReleaseEvent(self, keyEvent)

        if keyEvent.key() == Qt.Key_Control:
            self.__IsControl = False




