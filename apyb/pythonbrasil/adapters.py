# encoding: utf-8
from zope.component import adapts

from Products.CMFCore.interfaces import IContentish

from apyb.pythonbrasil import MessageFactory as _
from plone.stringinterp.interfaces import IStringSubstitution
from plone.stringinterp.adapters import BaseSubstitution

class EmailSubstitution(BaseSubstitution):
    adapts(IContentish)
    
    category = _(u'All Content')
    description = _(u'Content E-mail')
    
    def safe_call(self):
        return self.context.email


class UIDSubstitution(BaseSubstitution):
    adapts(IContentish)
    
    category = _(u'All Content')
    description = _(u'Content UID')
    
    def safe_call(self):
        return self.context.UID()