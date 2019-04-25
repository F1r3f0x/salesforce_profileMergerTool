from typing import List
from enum import Enum

#from main import apiVersion

apiVersion = 44

# Metadata Classes
class ProfileField:
    def __init__(self):
        self.model_name = ''
        self.toggles = {}
        self.model_fields = {}

    def get_toggles(self) -> dict:
        return self.toggles
    
    def set_toggles(self, toggles: dict):
        self.toggles = toggles

    def set_fields(self, fields: dict):
        self.model_fields = fields

    def get_fields(self) -> dict:
        return self.model_fields

class ProfileActionOverride(ProfileField):
    def __init__(self, actionName: str, content: str, formFactor: str, pageOrSobjectType: str, recordType: str, type:str):
        super().__init__()
        self.actionName = actionName
        self.content = content
        self.formFactor = formFactor
        self.pageOrSobjectType = pageOrSobjectType
        self.recordType = recordType
        self.type = type

        self.model_name = 'profileActionOverrides'
        self.model_fields = {
            'actionName': self.actionName
        }

    def __str__(self):
        return f'{self.model_name}: {self.actionName}: {self.content}'
    

class ProfileApplicationVisibility(ProfileField):
    def __init__(self, application: str, default: bool, visible: bool ):
        super().__init__()
        self.application = application
        self.default = bool
        self.visible = bool

        self.model_name = 'applicationVisibilities'
        self.toggles = {
            'default': default,
            'visible': visible
        }

    def __str__(self):
        return f'{self.model_name}: {self.application}'
    

class ProfileCategoryGroupVisibility(ProfileField):
    def __init__(self, dataCategories: List[str], dataCategoryGroup: str, visibility: str ):
        super().__init__()
        self.dataCategories = dataCategories
        self.dataCategoryGroup = dataCategoryGroup
        self.visibility = visibility

        self.model_name = 'categoryGroupVisibilities'
        self.toggles = {
            'visibility': self.visibility
        }

    def __str__(self):
        return f'{self.model_name}: {self.dataCategoryGroup}'


class ProfileApexClassAccess(ProfileField):
    def __init__(self, apexClass='', enabled=False):
        super().__init__()
        self.apexClass = apexClass
        self.enabled = enabled

        self.model_name = 'classAccesses'
        self.toggles = {
            'enabled': self.enabled
        }

    def get_fields(self):
        return {
            'apexClass': apexClass,
            'enabled': enabled
        }

    def set_fields(self, fields: dict):
        for field, value in fields.items():
            if field == 'apexClass':
                self.apexClass = value
            elif field == 'enabled':
                if value == 'true':
                    self.enabled = True
                else:
                    self.enabled = False

    def __str__(self):
        return f'{self.model_name}: {self.apexClass}'

class ProfileCustomPermissions(ProfileField):
    def __init__(self, enabled: bool, name: str):
        super().__init__()
        self.enabled = enabled
        self.name = name

        self.model_name = 'customPermissions'
        self.toggles = {
            'enabled': self.enabled
        }

    def __str__(self):
        return f'{self.model_name}: {self.name}'


class ProfileExternalDataSourceAccess(ProfileField):
    def __init__(self, enabled: bool, externalDataSource: str ):
        super().__init__()
        self.enabled = enabled
        self.externalDataSource = externalDataSource

        self.model_name = 'externalDataSourceAccesses'
        self.toggles = {
            'enabled': self.enabled
        }

    def __str__(self):
        return f'{self.model_name}: {self.externalDataSource}'


class ProfileFieldLevelSecurity(ProfileField):
    def __init__(self, editable: bool, field: str , readable: bool, hidden: bool):
        self.editable = editable
        self.field = field
        #if apiVersion <= 22.0:
        #    self.hidden = hidden
        self.hidden = hidden
        self.readable = readable

        if apiVersion <= 22:
            self.model_name = 'fieldLevelSecurities'
            self.toggles = {
                'editable': editable,
                'hidden': hidden,
                'readable': readable
            }
        else:
            self.model_name = 'fieldPermissions'
            self.toggles = {
                'editable': editable,
                'readable': readable
            }

    def __str__(self):
        return f'{self.model_name}: {self.field}'

class ProfileLayoutAssignments:
    def __init__(self, layout: str, recordType: str):
        self.layout = layout
        self.recordType = recordType

class ProfileLoginHours:
    def __init__(self, weekdayStart: str, weekdayEnd: str):
        self.weekdayStart = weekdayStart
        self.weekdayEnd = weekdayEnd

class ProfileLoginIpRange:
    def __init__(self, description: str, endAddress: str, startAddress: str):
        self.description = description
        self.endAddress = endAddress
        self.startAddress = startAddress
    
class ProfileObjectPermissions:
    def __init__(self, allowCreate: bool, allowDelete: bool, allowEdit: bool,
        allowRead: bool, modifyAllRecords: bool, object: str, viewAllRecords:bool):
        if apiVersion < 14:
            self.revokeCreate = allowCreate
            self.revokeDelete = allowDelete
            self.revokeEdit = allowEdit
        else:
            self.allowCreate = allowCreate
            self.allowDelete = allowDelete
            self.allowEdit = allowEdit
        
        if apiVersion >= 15:
            self.modifyAllRecords = modifyAllRecords
        
        self.object = object
        
        if apiVersion >= 15:
            self.viewAllRecords = viewAllRecords

class ProfileApexPageAccess:
    def __init__(self, apexPage: str, enabled: bool):
        self.apexPage = apexPage
        self.enabled = enabled

class ProfileRecordTypeVisibility:
    def __init__(self, default: bool, personAccountDefault: bool, recordType: str, visible: bool):
        self.default = default
        self.personAccountDefault = personAccountDefault
        self.recordType = recordType
        self.visible = visible

class ProfileTabVisibility:
    def __init__(self, tab: str, visibility: str):
        self.tab = tab
        self.visibilty = visibility

class ProfileUserPermission:
    def __init__(self, enabled: bool, name: str):
        self.enabled = enabled
        self.name = name

classes_by_modelName = {
    #ProfileActionOverride(None, None, None, None, None, None).model_name, ProfileActionOverride,
    ProfileApexClassAccess(None, None).model_name: ProfileApexClassAccess,
    #ProfileApexPageAccess().model_name, ProfileApexPageAccess,
    #ProfileApplicationVisibility().model_name, ProfileApplicationVisibility,
    #ProfileCategoryGroupVisibility().model_name, ProfileCategoryGroupVisibility,
    #ProfileCustomPermissions().model_name, ProfileCustomPermissions,
    #ProfileExternalDataSourceAccess().model_name, ProfileExternalDataSourceAccess,
    #ProfileFieldLevelSecurity().model_name, ProfileFieldLevelSecurity,
}

class Profile:
    def __init__(self, applicationVisibilities: List[ProfileApplicationVisibility],
        categoryGroupVisibilities: List[ProfileCategoryGroupVisibility], classAccesses: List[ProfileApexClassAccess],
        custom: bool, customPermissions: List[ProfileCustomPermissions], description: str,
        externalDataSourceAccesses: List[ProfileExternalDataSourceAccess], fieldPermissions: List[ProfileFieldLevelSecurity],
        fullName: str, layoutAssignments: List[ProfileLayoutAssignments], loginHours: List[ProfileLoginHours],
        loginIpRanges: List[ProfileLoginIpRange], objectPerimissions: List[ProfileObjectPermissions],
        pageAccesses: List[ProfileApexPageAccess], profileActionOverrides: List[ProfileActionOverride],
        recordTypeVisibilities: List[ProfileRecordTypeVisibility], tabVisibilities: List[ProfileTabVisibility],
        userLicense: str, userPermissions: List[ProfileUserPermission]):

        self.applicationVisibilities = applicationVisibilities
        if apiVersion >= 41:
            self.categoryGroupVisibilities = categoryGroupVisibilities
        self.classAccesses = classAccesses
        if apiVersion >= 30:
            self.custom = custom
        if apiVersion >= 31:
            self.customPermissions = customPermissions
        if apiVersion >= 30:
            self.description = description
        if apiVersion >= 27:
            self.externalDataSourceAccesses = externalDataSourceAccesses

        if apiVersion <= 22:
            self.fieldLevelSecurities = fieldPermissions
        else:
            self.fieldPermissions = fieldPermissions

        self.fullName = fullName
        self.layoutAssignments = layoutAssignments
        if apiVersion >= 25:
            self.loginHours = loginHours
        if apiVersion >= 17:
            self.loginIpRanges = loginIpRanges
        if apiVersion >= 28:
            self.objectPerimissions = objectPerimissions
        self.pageAccesses = pageAccesses
        if apiVersion>= 37 and apiVersion <= 44:
            self.profileActionOverrides = profileActionOverrides
        if apiVersion >= 29:
            self.recordTypeVisibilities = recordTypeVisibilities
        self.tabVisibilities = tabVisibilities
        if apiVersion >= 17:
            self.userLicense = userLicense
        if apiVersion >= 29:
            self.userPermissions = userPermissions