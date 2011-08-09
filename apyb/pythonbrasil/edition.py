# -*- coding:utf-8 -*-
from five import grok
from plone.directives import dexterity, form

from Acquisition import aq_inner, aq_parent

from zope.component import getMultiAdapter

from zope import schema

from zope.component import getUtility

from zope.lifecycleevent.interfaces import IObjectCreatedEvent

from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides

from apyb.pythonbrasil import MessageFactory as _

class IEdition(form.Schema):
    """
    A edition of the conference
    """
    year = schema.Int(
        title=_(u"Year"),
        required=True,
        )

class Edition(dexterity.Container):
    grok.implements(IEdition)
    

@grok.subscribe(Edition, IObjectCreatedEvent)
def edition_created(context, event):
    """ Edition created, let's set it as 
        a navigation root
    """
    alsoProvides(context,INavigationRoot)

