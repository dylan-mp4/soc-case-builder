from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtWidgets import QTextEdit
import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter
from ui.settings_dialog import SettingsDialog

class SpellHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.settings_dialog = SettingsDialog()
        self.settings_dialog.load_settings()
        self.language_region = self.settings_dialog.language_region_combo.currentText()
        self.spell_checker = enchant.Dict(self.language_region)
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor("red"))
        self.misspelled_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

    def highlightBlock(self, text):
        words = QRegularExpression("\\b\\w+\\b")
        match_iterator = words.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            word = match.captured(0)
            if not self.spell_checker.check(word):
                self.setFormat(match.capturedStart(), match.capturedLength(), self.misspelled_format)

class SpellTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highlighter = SpellHighlighter(self.document())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        cursor = self.cursorForPosition(position)
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        menu = self.createStandardContextMenu()
        if word and not self.highlighter.spell_checker.check(word):
            suggestions = self.highlighter.spell_checker.suggest(word)
            if suggestions:
                spell_menu = menu.addMenu("Suggestions")
                for suggestion in suggestions:
                    action = spell_menu.addAction(suggestion)
                    action.triggered.connect(lambda _, s=suggestion, c=cursor: self.replace_word(c, s))
            add_word_action = menu.addAction("Add to Dictionary")
            add_word_action.triggered.connect(lambda: self.add_word_to_dictionary(word))
        menu.exec(self.viewport().mapToGlobal(position))

    def replace_word(self, cursor, word):
        cursor.insertText(word)

    def add_word_to_dictionary(self, word):
        self.highlighter.spell_checker.add(word)
        self.highlighter.settings_dialog.custom_dict_list.addItem(word)
        self.highlighter.settings_dialog.save_custom_dictionary()