##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Globals import InitializeClass

from Products.ZenModel.OSComponent import OSComponent
from Products.ZenRelations.RelSchema import ToOne, ToManyCont


class WinService(OSComponent):
    '''
    Model class for Windows Service.
    '''
    meta_type = portal_type = 'WinRMService'

    """
    startmode [string] = The start mode for the servicename
    account [string] = The account name the service runs as
    usermonitor [boolean] = Did user manually set monitor.
    globalset [boolean] = Has the global templates been checked
    """
    servicename = None
    caption = None
    description = None
    startmode = None
    account = None
    monitor = False
    usermonitor = False
    globalset = False

    _properties = OSComponent._properties + (
        {'id': 'servicename', 'label': 'Service Name', 'type': 'string'},
        {'id': 'caption', 'label': 'Caption', 'type': 'string'},
        {'id': 'description', 'label': 'Description', 'type': 'string'},
        {'id': 'startmode', 'label': 'Start Mode', 'type': 'string'},
        {'id': 'account', 'label': 'Account', 'type': 'string'},
        {'id': 'usermonitor', 'label': 'User Selected Monitor State',
            'type': 'boolean'},
        {'id': 'globalset', 'label': 'Global Set', 'type': 'boolean'},
        )

    _relations = OSComponent._relations + (
        ("os", ToOne(ToManyCont,
         "ZenPacks.zenoss.Microsoft.Windows.OperatingSystem",
         "winrmservices")),
    )

    def getRRDTemplateName(self):
        if self.getRRDTemplateByName(self.servicename):
            return self.servicename
        else:
            return 'WinService'

    def getBest(self):
        # Method to find template that matches this service
        # Gets the monitor value
        self.monitor = False
        self.usermonitor = False
        try:
            if self.getRRDTemplateByName(self.servicename):
                template = self.getRRDTemplateByName(self.servicename)
                if template.datasources.DefaultService.defaultgraph == True:
                    if self.globalset == False:
                        self.globalset = True
                        self.monitor = True
                        self.usermonitor = True
                        self.index_object()
                    return True
                else:
                    template.datasources.DefaultService.enabled = False
                    return False
            return False
        except:
            return False

    def monitored(self):

        # 1 - Check to see if the user has manually set monitor status
        if self.usermonitor == True:
            if self.globalset == True:
                self.globalset = False
            return self.monitor

        # 2 - Check to see if a default template exists with default set
        best_template = self.getBest()

        if best_template == True:
            return True
        # 3 - Default to what the current monitor status is
        else:
            return self.monitor

InitializeClass(WinService)
