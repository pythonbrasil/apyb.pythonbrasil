# -*- coding:utf-8 -*-
from five import grok
import pickle
from DateTime import DateTime
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent

from apyb.registration import browser

from apyb.registration.registration import IRegistration
from apyb.registration.registrations import IRegistrations
from apyb.registration.attendee import IAttendee
from apyb.registration.registrations import IRegistrations

PATH = browser.__path__[0]

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
    'P':'S',    
    'M':'M',
    'G':'L',
    'X':'X',
}

class View(grok.View):
    grok.context(IRegistrations)
    grok.require('zope2.View')
    grok.name('import')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self._wt = self.tools.workflow()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
    
    
    def convertFromDict(self,data):
        ''' Our objects will be returned as dicts '''
        data['fields'] = dict([(l.keys()[0],l.values()[0]) for l in data['fields']])
        tmpReg = {}
        tmpAttendee = {}
        attendees = []
        tmpAttendees = []
        data['created'] = DateTime(data['fields']['creation_date'])
        data['modified'] = DateTime(data['fields']['modification_date'])
        tmpReg['id'] = data['fields']['id']
        tmpReg['registration_type'] = TIPO[data['fields']['tipo']]
        tmpReg['city'] = data['fields']['cidade']
        tmpReg['state'] = data['fields']['estado']
        tmpReg['country'] = PAIS.get(data['fields']['pais'],'br')
        tmpReg['email'] = data['fields']['email']
        tmpReg['post_code'] = data['fields']['cep']
        tmpReg['address'] = data['fields']['endereco']
        if data['fields']['paga']:
            tmpReg['paid'] = True
            tmpReg['service'] = 'pagseguro'
            tmpReg['amount'] = data['fields']['valor_pago'] or 0
            tmpReg['amount'] = data['fields']['valor_pago'] or 0
        if data['portal_type']== 'Inscricao':
           tmpAttendee['address'] = data['fields']['endereco']
           tmpAttendee['city'] = data['fields']['cidade']
           tmpAttendee['state'] = data['fields']['estado']
           tmpAttendee['post_code'] = data['fields']['cep']
           tmpAttendee['country'] = PAIS.get(data['fields']['pais'],'br')
           tmpAttendee['email'] = data['fields']['email']
           tmpAttendee['fullname'] = data['fields']['nome']
           tmpAttendee['t_shirt_size'] = CAMISETA.get(data['fields']['camiseta'],'L')
           tmpAttendee['gender'] = (data['fields']['sexo'] == 'Feminino') and 'f' or 'm'
           tmpAttendee['twitter'] = data['fields']['twitter']
           tmpAttendee['site'] = data['fields']['site']
           tmpAttendee['organization'] = data['fields']['instituicao']
           tmpAttendee['conference'] = data['fields']['optin_evento']
           tmpAttendee['partners'] = data['fields']['optin_parceiros']
           tmpAttendees.append(tmpAttendee)
        else: 
            for att in data['fields']['participantes']:
                tmpAttendee = {}
                tmpAttendee['city'] = data['fields']['cidade']
                tmpAttendee['state'] = data['fields']['estado']
                tmpAttendee['post_code'] = data['fields']['cep']
                tmpAttendee['country'] = PAIS.get(data['fields']['pais'],'br')
                tmpAttendee['email'] = att['email']
                tmpAttendee['fullname'] = att['nome']
                tmpAttendee['t_shirt_size'] = CAMISETA.get(att['camiseta'],'L')
                tmpAttendee['gender'] = (att['sexo'] == 'Feminino') and 'f' or 'm'
                tmpAttendee['organization'] = data['fields']['razao_social']
                tmpAttendee['conference'] = data['fields']['optin_evento']
                tmpAttendee['partners'] = data['fields']['optin_parceiros']
                tmpAttendees.append(tmpAttendee)
        reg = createContent('apyb.registration.registration', checkConstraints=True, **tmpReg)
        for att in tmpAttendees:
            attendees.append(createContent('apyb.registration.attendee', checkConstraints=True, **att))
        return [reg,attendees]
    
    def fixWorkFlowHistory(self,wh):
        ''' change workflows and actions '''
        actions = wh['inscricao_workflow']
        wh['registration_workflow'] = []
        for action in actions:
            dictAction = {}
            if action['action'] == 'registrar':
                dictAction['action'] = 'submit'
            elif action['action'] == 'pagar':
                dictAction['action'] = 'confirm'
            else:
                dictAction['action'] = action['action']
            
            if action['review_state'] == 'novo':
                dictAction['review_state'] = 'new'
            elif action['review_state'] == 'registrado':
                dictAction['review_state'] = 'pending'
            elif action['review_state'] == 'inscrito':
                dictAction['review_state'] = 'confirmed'
            else:
                dictAction['review_state'] = action['action']
            dictAction['comments'] = action['comments']
            dictAction['time'] = action['time']
            dictAction['actor'] = action['actor']
            
            wh['registration_workflow'].append(dictAction)
        wh['registration_workflow'] = tuple(wh['registration_workflow'])
        del wh['inscricao_workflow']
        return wh
            
    def render(self):
        context = self.context
        wt = self._wt
        data = open('%s/inscricoes.pickle' % PATH)
        data = pickle.load(data)
        i = 0
        for item in data:
            reg,attendees = self.convertFromDict(item)
            regObj = addContentToContainer(context,reg)
            for attendee in attendees:
                attObj = addContentToContainer(regObj,attendee,checkConstraints=False)
            regObj.title = len(attendees) >1 and attObj.organization or attObj.fullname
            regObj.creation_date = item['created']
            regObj.modification_date = item['modified']
            regObj.workflow_history = self.fixWorkFlowHistory(item['workflow_history'])
            wt['registration_workflow'].updateRoleMappingsFor(regObj)
            regObj.reindexObject(['modified'])
            if item['review_state'] == 'inscrito':
                for attId in regObj.objectIds():
                    wt.doActionFor(regObj[attId],'confirm')
            i +=1
            print i
        return 'Foo'