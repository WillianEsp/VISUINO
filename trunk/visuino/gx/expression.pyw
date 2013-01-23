# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 13:05:56 2013

@author: Nelso
"""

from __future__ import division
import sys, imp

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from bases import *

__all__ = ['GxExpression']

class GxExpression(QGraphicsItem):
    
    _H_PADD = 10
    _V_PADD = 10
    _OP_PADD = 5

    def __init__(self, style_scheme, scene=None, parent=None):
        """
        :style_scheme: dict. Format:
            {'field_scheme': dict for GxField style_scheme,
             'backg_color': QColor()}
        """
        QGraphicsItem.__init__(self, parent, scene)
        
        self._style_scheme = style_scheme
        self._width, self._height = 0, 0
        self._elements = []
        
        self.setFlags(QGraphicsItem.ItemIsMovable)
        
        field = GxField(self._style_scheme['field_scheme'], 
                        scene, parent=self)
        field.setPos(self._H_PADD, self._V_PADD)
        self._elements.append(field)    
        
        self.updateMetrics()
        
    def _getMatchIndex(self, match):
        """
        Returns the index of the occurrency of id(match),
        or -1 if not found.
        """
#        print "searching match.."
        for i, x in enumerate(self._elements):
#            print "%d -- id: %d -- %s" % (i, id(x), x.__class__.__name__)
            if id(x) == id(match):
                return i
        return -1        
                            
    def updateMetrics(self):
        """
        Recalculate its dimensions based on the current elements.
        """
        self._width = 2 * self._H_PADD
        for x in self._elements:
            self._width += x.boundingRect().width()        
            if isinstance(x, GxOperatorSymbol):
                self._width += 2*self._OP_PADD
        
        max_height = 0
        for x in self._elements:
            x_height = x.boundingRect().height()
            if x_height > max_height:
                max_height = x_height        
        
        self._height = 2 * self._V_PADD + max_height
        
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option, widget=None):
        painter.fillRect(self.boundingRect(), 
                         self._style_scheme['backg_color'])
                    
    def insertOperator(self, match, place, op_symbol):
        """
        :match: GxField.
        :place: str in ['left', 'right']
        :op_symbol: str. Operator symbol.
        """
        
#        self.printElements()
        
        match_index = self._getMatchIndex(match)
        
        if match_index == -1:
            print "mah oe, nao achou a match..."
            return
            
        text_op = GxOperatorSymbol(op_symbol, 
            self._style_scheme['operator_scheme'],
            self._height - 2*self._V_PADD, 
            parent=self, scene=self.scene())    
       
               
        new_field = GxField(self._style_scheme['field_scheme'], 
                            self.scene(), parent=self)


        if place == 'right':
            
            text_op.setPos(match.pos().x() + match._width + self._OP_PADD, 
                           self._V_PADD)
            new_field.setPos(text_op.pos().x() + text_op._width + 
                             self._OP_PADD, self._V_PADD)                           
            
            self._elements.insert(match_index + 1, text_op)
            self._elements.insert(match_index + 2, new_field)        
            print "to the right"
            
        if place == 'left':
            
            text_op.setPos(match.pos().x() - text_op.boundingRect + self._OP_PADD, 
                           self._V_PADD)
            new_field.setPos(text_op.pos().x() + text_op._width + 
                             self._OP_PADD, self._V_PADD) 

            self._elements.insert(match_index, new_field)            
            self._elements.insert(match_index + 1, text_op)            
            print "to the left"
        
        self.updateMetrics()
        self.update(self.boundingRect())  
        
        self.reposElements(new_field, text_op.boundingRect().width() + \
                            new_field.boundingRect().width() + self._H_PADD)
        
#        self.printElements()
        
    def printElements(self):
        for i, x in enumerate(self._elements):
            print "%d -- %s" % (i, x.__class__.__name__)
        
    def reposElements(self, match, dx):
        """
        Re-positionates all elements after 'match', by displacing 'dx'.
        
        :match: GxField
        :dx: int.
        """
#        print "repositioning because %d ..." % dx
        
        match_index = self._getMatchIndex(match)
        
        if match_index == -1:
            print "No match"
            return
            
        for i in range(match_index + 1, len(self._elements)):
            e = self._elements[i]
            e.setPos(e.pos().x() + dx, e.pos().y())
            
        self.updateMetrics()
        self.update(self.boundingRect())
        
    def isFirst(self, element):
        if self._getMatchIndex(element) == 0:
            return True
        else:
            return False
            
    def isLast(self, element):
        if self._getMatchIndex(element) == len(self._elements) - 1:
            return True
        else:
            return False            
        
        
class GxField(QGraphicsItem):
        
    _DEFAULT_HEIGHT = 30
    _DEFAULT_WIDTH = 40
    _RX = 10     # X roundness of the empty field rectangle
    _RY = 10     # Y roundness of the empty field rectangle        
    
    def __init__(self, style_scheme, scene=None, parent=None):
        """
        :style_scheme: dict. Must be in the form:
            {'backg_color': QColor(), 'input_font': QFont()}
        """
        QGraphicsItem.__init__(self, parent, scene)
        
        self._parent_expr = parent
        
        self._width = self._DEFAULT_WIDTH
        self._height = self._DEFAULT_HEIGHT
        self._style_scheme = style_scheme 

        self._proxy_field = None        
        
        self._menu = QMenu()
        self._menu_input = QMenu()
        self._setupMenus()
        
#        self.setFlags(QGraphicsItem.ItemIsSelectable)
        
        
    def _setupMenus(self):
        self._act_input_here = self._menu.addAction(
            "Input here", self._createInputField)
        self._act_variable_here = self._menu.addAction(
            "Variable here")
        self._act_operation_here = self._menu.addAction(
            "Operation here")
            
        self._menu.addSeparator()

        menu_op_left = self._menu.addMenu("Insert left")        
        menu_op_right = self._menu.addMenu("Insert right")
        
        self._menu.addSeparator()
        
        self._act_remove_left = self._menu.addAction(
            "Remove left")
        self._act_remove_right = self._menu.addAction(
            "Remove right")            
                
        get_slot = lambda op, place: \
            (lambda: self.parentItem().insertOperator(self, place, op))                    
        
        for op in ('+', '-', 'x', '/'):
            menu_op_left.addAction(op, get_slot(op, 'left'))
            menu_op_right.addAction(op, get_slot(op, 'right'))             
            
        self._menu_input.addAction("Remove input field", 
                                   self._removeInputField)
        self._menu_input.addSeparator()
        self._menu_input.addMenu(menu_op_left)
        self._menu_input.addMenu(menu_op_right)
        self._menu_input.addSeparator()
        self._menu_input.addAction(self._act_remove_left)
        self._menu_input.addAction(self._act_remove_right)
        
            
    def _createInputField(self):
        """
        Creates a proper QLineEdit (from EditInputField) to occupy its
        field space. This widget will be keep in self._proxy_field.
        """
        edit = EditInputField(self, self._style_scheme['input_font'])        

        self._proxy_field = GxProxyInputField(self._menu_input,
                                              parent=self)
        self._proxy_field.setWidget(edit)
        edit.setFocus()
#        self.updateMetrics()
    
    def _removeInputField(self):
        """
        Removes the input field by cleaning references and updating 
        self._proxy_field.
        """
        self._proxy_field.setParentItem(None)
        self._proxy_field = None
        self.updateMetrics()            
            
            
    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
        
    def paint(self, painter, option, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)
        if self._proxy_field is None:
            painter.setPen(Qt.transparent)
            painter.setBrush(self._style_scheme['backg_color'])
            painter.drawRoundedRect(self.boundingRect(),
                                    self._RX, self._RY)
    
    def contextMenuEvent(self, event):

        if self._parent_expr.isFirst(self):
            self._act_remove_left.setVisible(False)
        else:
            self._act_remove_left.setVisible(True)
            
        if self._parent_expr.isLast(self):
            self._act_remove_right.setVisible(False)
        else:
            self._act_remove_right.setVisible(True)            
            
        self._menu.popup(event.screenPos())
        
    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        
    def mouseDoubleClickEvent(self, event):
        if self._proxy_field is None:
            self._createInputField()
        
            
    def updateMetrics(self):
        """
        Update its dimensions based on the dimensions of the proxy (if any),
        and also call the apropriate update() for its parent GxExpression.
        """
        old_width = self._width
        if self._proxy_field is not None:
            self._width = self._proxy_field.boundingRect().width()
            self._height = self._proxy_field.boundingRect().height()
        else:
            self._width = self._DEFAULT_WIDTH
            self._height = self._DEFAULT_HEIGHT
            
        parent = self.parentItem()
            
        if isinstance(parent, GxExpression):
            
            old_rect = parent.boundingRect()
            parent.updateMetrics()
            new_rect = parent.boundingRect()            
            
            if old_rect.width() > new_rect.width():
                rect_scene = QRectF(parent.pos(),
                                    old_rect.size())
                parent.scene().update(rect_scene)
            else:
                parent.update(new_rect)
                
            parent.reposElements(self, self._width - old_width)
                
                
class GxOperatorSymbol(QGraphicsItem):
    """
    Holds the operator symbol as a graphical text object.    
    
    Special graphical item where the text appears vertical centralized
    as respect to some given 'max_height'. The width of the bounding
    rect will be the width of the text.
    """
    
    _V_PADD_FIX = -5

    def __init__(self, op_symbol, style_scheme, max_height, 
                 parent=None, scene=None):
        """
        :op_symbol: str.
        :style_scheme: dict  {'font': QFont(), 'color': QColor()}
        """
        QGraphicsItem.__init__(self, parent, scene)
        
        self._op_symbol = op_symbol
        self._style_scheme = style_scheme
        self._width = QFontMetrics(self._style_scheme['font']) \
                        .width(self._op_symbol)
        self._height = max_height

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)
    
    def paint(self, painter, option, widget=None):
        painter.fillRect(self.boundingRect(), Qt.transparent)
        painter.setFont(self._style_scheme['font'])
        painter.setPen(QPen(self._style_scheme['color']))
        rect = self.boundingRect()
        rect.setTop(self._V_PADD_FIX)
        painter.drawText(rect, Qt.AlignCenter, 
                         self._op_symbol)    
    
    
class GxProxyInputField(QGraphicsProxyWidget):
    """
    Features added:
    
        - On mouse click events, brings its "grandpa" GxExpression to the
          front of the GxScene. OBS: Its parent is a GxField.
          
        - On context menu event, raises some QMenu() as specified on the
          self._context_menu attribute.
    """
    def __init__(self, context_menu=None, parent=None):
        QGraphicsProxyWidget.__init__(self, parent)
        
        self._context_menu = context_menu        
        
    def mousePressEvent(self, event):
        QGraphicsProxyWidget.mousePressEvent(self, event)
        self.scene().bringToFront(self.parentItem().parentItem()) 
    
    def contextMenuEvent(self, event):
        if isinstance(self._context_menu, QMenu):
            self._context_menu.popup(event.screenPos())


class EditInputField(QLineEdit):
    """
    Features added:
        
        - Variable width, which will always be big enough (and only that
          big) to contain its text. Call updateMetrics() on the field
          parent (GxField) when the width is updated.
    """
    def __init__(self, field_parent, font=None):
        """
        :field_parent: GxField().
        :font: QFont().
        """
        QLineEdit.__init__(self)
        
        self._field_parent = field_parent
        self._metrics = QFontMetrics(self.font())
        
        self.connect(self, SIGNAL('textChanged(const QString&)'),
                     self._onTextChanged)
                     
        if isinstance(font, QFont):
            self.setFont(font)
        else:
            self.updateWidth()
            
        self.setFrame(False)
        self.setAlignment(Qt.AlignCenter)                         

        
    def setFont(self, font):
        """
        :font: QFont().
        """
        QLineEdit.setFont(self, font)
        self._metrics = QFontMetrics(font) 
        self.updateWidth()
        
    def updateWidth(self):
        """
        Update its x-dimension and also call updateMetrics() on the
        GxField parent, if any.
        """
        min_width = self._metrics.width('MMi')
        new_width = self._metrics.width(self.text())
        if len(self.text()) > 2:
            self.setFixedWidth(new_width + 10)
        else:
            self.setFixedWidth(min_width)
            
        if isinstance(self._field_parent, GxField):
            self._field_parent.updateMetrics()

    def _onTextChanged(self):
        """
        Every time that text change, its dimension will be updated to
        comport the new text.
        """
        self.updateWidth()
    
    
def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(300, 200, 600, 400)
    scene = GxScene()
    
    style_scheme = {'field_scheme': {'backg_color': QColor(255, 213, 213),
                                     'input_font': QFont("Verdana", 12)},
                    'operator_scheme': {'font': QFont("Verdana", 18),
                                        'color': QColor('white')},
                    'backg_color': QColor(255, 128, 128)}
    
    gx_exp = GxExpression(style_scheme, scene)
    gx_exp.setPos(100, 100)
    
    view = GxView(scene, win)
    win.setCentralWidget(view)
    win.show()
    sys.exit(app.exec_())       
    

if __name__ == '__main__':
    main()