# -*- coding:utf-8 -*-
from five import grok
import pickle
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from apyb.registration.registration import IRegistration
from apyb.registration.registrations import IRegistrations
from apyb.registration.attendee import IAttendee

TIPO = {
      '1':'apyb',
      '2':'student',
      '3':'individual',
      '4':'government',
      '5':'group',
}


PAIS = {
    'Brasil':u'br',
    'Argentina':u'ar',
}

CAMISETA ={
    'P','S',    
    'M','M',
    'G','L',
    'X','X',
}

class View(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
    
    
    def convertFromDict(self,data):
        ''' Our objects will be returned as dicts '''
        data['fields'] = dict([(l.keys()[0],l.values()[0]) for l in data['fields']])
        tmpReg = {}
        tmpAttendee = {}
        attendees = []
        tmpAttendees = []
        tmpReg['id'] = data['fields']['id']
        tmpReg['registration_type'] = TIPO[data['fields']['tipo']]
        tmpReg['city'] = data['fields']['city']
        tmpReg['state'] = data['fields']['estado']
        tmpReg['country'] = PAIS[data['fields']['pais']]
        tmpReg['email'] = data['fields']['email']
        tmpReg['post_code'] = data['fields']['cep']
        tmpReg['address'] = data['fields']['endereco']
        if data['fields']['paga']:
            tmpReg['paid'] = True
        if data['portal_type']== 'Inscricao':
           tmpAttendee['address'] = data['fields']['endereco']
           tmpAttendee['city'] = data['fields']['city']
           tmpAttendee['state'] = data['fields']['estado']
           tmpAttendee['post_code'] = data['fields']['cep']
           tmpAttendee['country'] = PAIS[data['fields']['pais']]
           tmpAttendee['email'] = data['fields']['email']
           tmpAttendee['fullname'] = data['fields']['nome']
           tmpAttendee['t_shirt_size'] = CAMISETA.get(data['fields']['camiseta'],'L')
           tmpAttendee['gender'] = (data['fields']['sexo'] == 'Masculino') and 'm' or 'f'
           tmpAttendee['twitter'] = data['fields']['twitter']
           tmpAttendee['site'] = data['fields']['site']
           tmpAttendee['organization'] = data['fields']['instituicao']
           tmpAttendee['conference'] = data['fields']['optin_evento']
           tmpAttendee['partners'] = data['fields']['optin_parceiros']
           tmpAttendees.append(tmpAttendee)
        else: 
            for att in data['fields']['participantes']
                tmpAttendee = {}
                tmpAttendee['city'] = data['fields']['city']
                tmpAttendee['state'] = data['fields']['estado']
                tmpAttendee['post_code'] = data['fields']['cep']
                tmpAttendee['country'] = PAIS[data['fields']['pais']]
                tmpAttendee['email'] = att['email']
                tmpAttendee['fullname'] = att['nome']
                tmpAttendee['t_shirt_size'] = CAMISETA.get(att['camiseta'],'L')
                tmpAttendee['gender'] = (att['sexo'] == 'Masculino') and 'm' or 'f'
                tmpAttendee['organization'] = data['fields']['razao_social']
                tmpAttendee['conference'] = data['fields']['optin_evento']
                tmpAttendee['partners'] = data['fields']['optin_parceiros']
                tmpAttendees.append(tmpAttendee)
        reg = createContent('apyb.registration.registration', checkConstraints=True, **tmpReg)
        for att in tmpAttendees:
            attendees.append(createContent('apyb.registration.attendee', checkConstraints=True, **att))
        return [reg,attendees]
    
    def render(self):
        data = open('inscricoes.pickle')
        data = pickle.load(data)
        for item in data:
            reg,attendees = self.convertFromDict(item)
            regObj = addContentToContainer(context,reg)
            for attendee in attendees:
                attObj = addContentToContainer(context,attendee,checkConstraints=False)
        return 'Foo'