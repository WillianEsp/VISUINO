﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Purpose:     Implements a palette for blocks drag and drop.
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
#              This file is part of VISUINO project - Copyright (C) 2013
#
# Licence:     GNU GPL. Its simple: use and modify as you please, and redis-
#              tribute ONLY as 100% free and keeping the credits.
#-------------------------------------------------------------------------------
__all__ = ['GxPalette', 'GxPaletteView']

from PyQt4 import QtGui, QtCore
import sys

from visuino.gx.bases import *
from visuino.gx.blocks import *
from visuino.gui import *
from visuino.resources import *


class GxPalette(QtGui.QGraphicsProxyWidget):
    def __init__(self, scene=None):
        QtGui.QGraphicsProxyWidget.__init__(self)

        self._scene = QtGui.QGraphicsScene()
        self._scene.setSceneRect(0, 0, 200, 1000)
##        self._scene.setBackgroundBrush(QtGui.QBrush(
##            QtGui.QColor(208, 214, 219)))
##        self._scene.setBackgroundBrush(QtGui.QBrush(
##            QtGui.QImage('slab.jpg')))

        grad = QtGui.QLinearGradient(QtCore.QPointF(0, 0),
                                     QtCore.QPointF(200, 0))
        grad.setColorAt(1, QtGui.QColor('#444444'))
        grad.setColorAt(0, QtCore.Qt.gray)
        self._scene.setBackgroundBrush(QtGui.QBrush(grad))


        self._view = GxView(self._scene)
        self._view.wheel_zoom = False
        self._view.setGeometry(0, 0, 200, 600)
        self._view.setFrameShape(QtGui.QFrame.NoFrame)

        self.setWidget(self._view)

        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)

        self.cursor_collide = QtGui.QCursor(QtGui.QPixmap(':trash-icon.png'))

        if isinstance(scene, QtGui.QGraphicsScene):
            scene.addItem(self)

        self.setupBlocks()

    def setupBlocks(self):
        y = 10

        block_pin_mode = GxBlockFunctionCall('pinMode',
            [FieldInfo('pin', 'int', '0|13', 'combobox'),
             FieldInfo('mode', 'const', 'INPUT,OUTPUT', 'combobox')],
            None, StyleBlockFunctionCall(), self._scene)
        block_pin_mode.setPos(20, y)
        y += block_pin_mode.boundingRect().height() + 10

        block_digital_read = GxBlockFunctionCall('digitalRead',
            [FieldInfo('pin', 'int', '0|13', 'combobox')],
            FieldInfo('value', 'int', 'HIGH,LOW', 'combobox'),
            StyleBlockFunctionCall(), self._scene)
        block_digital_read.setPos(10, y)
        y += block_digital_read.boundingRect().height() + 10

        block_digital_write = GxBlockFunctionCall('digitalWrite',
            [FieldInfo('pin', 'int', '0|13', 'combobox'),
             FieldInfo('value', 'const', 'HIGH,LOW', 'combobox')],
            None, StyleBlockFunctionCall(), self._scene)
        block_digital_write.setPos(20, y)
        y += block_digital_write.boundingRect().height() + 10

        block_analog_read = GxBlockFunctionCall('analogRead',
            [FieldInfo('pin', 'int', '0|13', 'combobox')],
            FieldInfo('value', 'int', '0|1023', 'combobox'),
            StyleBlockFunctionCall(), self._scene)
        block_analog_read.setPos(10, y)
        y += block_analog_read.boundingRect().height() + 10

        block_analog_write = GxBlockFunctionCall('analogWrite',
            [FieldInfo('pin', 'int', '0|13', 'combobox'),
             FieldInfo('value', 'const', '0|255', 'combobox')],
            None, StyleBlockFunctionCall(), self._scene)
        block_analog_write.setPos(20, y)
        y += block_analog_write.boundingRect().height() + 10

    def mousePressEvent(self, event):
        ''' QtGui.QGraphicsProxyWidget.mousePressEvent(
            QGraphicsSceneMouseEvent) -> NoneType
        '''
        QtGui.QGraphicsProxyWidget.mousePressEvent(self, event)

        block_icon = self._view.itemAt(event.pos().toPoint())
        if hasattr(block_icon, 'cloneMe'):

            new_block = block_icon.cloneMe()
            new_block.setFlags(QtGui.QGraphicsItem.ItemIsMovable)
            self.scene().addItem(new_block)
            new_block.new_block = True
            new_block.palette = self

            icon_pos = QtCore.QPointF(block_icon.pos().x() + 2,
                                      block_icon.pos().y() + 2)

            new_block.setPos(self._view.mapFromScene(icon_pos))

            new_block.grabMouse()
            new_block.setCursor(QtGui.QCursor(
                QtGui.QPixmap(':add.ico').scaled(48, 48)))


class GxPaletteView(GxView):
    def __init__(self, parent=None, opengl=True):
        GxView.__init__(self, GxScene(), parent, opengl)

        self.scene().setSceneRect(0, 0, 1000, 2000)
        self.scene().setParent(self)
        self.wheel_zoom = False

        self.palette = GxPalette(self.scene())

        my_style = StyleBlockFunctionCall()

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def scrollContentsBy(self, x, y):
        QtGui.QGraphicsView.scrollContentsBy(self, x, y)
        if x == 0:
            self.palette.setPos(self.palette.pos().x(),
                                self.mapToScene(0, 0).y())


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
##    app.setStyle(QtGui.QStyleFactory.create('Plastique'))

    win = QtGui.QMainWindow()
    win.setGeometry(100, 100, 900, 600)

    gx_palette_view = GxPaletteView(parent=win)

    win.setCentralWidget(gx_palette_view)
    win.show()
    sys.exit(app.exec_())
