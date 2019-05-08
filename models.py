from typing import List
from enum import Enum

#from main import apiVersion

default_api_version = 44

# Utils
def bool_to_str(val):
    if str(val).strip().lower() == 'true':
        return True
    else:
        return False

# Model Classes
class ProfileFieldType:
    def __init__(self, api_version=44):
        self.api_version = api_version
        self.model_name = ''
        self.model_fields = {}
        self.model_special_field = ''

    def get_toggles(self) -> dict:
        return None

    def get_fields(self) -> dict:
        return self.model_fields

    def set_fields(self, input_fields: dict):
        if input_fields:
            for field, value in input_fields.items():
                setattr(self, field, value)


# Metadata Classes
class ProfileActionOverride(ProfileFieldType):
    def __init__(self, actionName='', content='', formFactor='', pageOrSobjectType='', recordType='', f_type='', api_version=default_api_version):
        super().__init__(api_version)
        self.actionName = actionName
        self.content = content
        self.formFactor = formFactor
        self.pageOrSobjectType = pageOrSobjectType
        self.recordType = recordType
        self.type = f_type

        self.model_name = 'profileActionOverrides'

    def get_fields(self) -> dict:
        return {
            'actionName': self.actionName,
            'content': self.content,
            'formFactor': self.formFactor,
            'pageOrSobjectType': self.pageOrSobjectType,
            'recordType': self.recordType,
            'type': self.type,
        }
        
    def __str__(self):
        return f'{self.model_name}: {self.actionName}: {self.content}: {self.pageOrSobjectType}: {self.type}'
    

class ProfileApplicationVisibility(ProfileFieldType):
    def __init__(self, application='', default=False, visible=False, api_version=default_api_version):
        super().__init__(api_version)
        self.application = application
        self.__default = default
        self.__visible = visible

        self.model_name = 'applicationVisibilities'

    @property
    def default(self):
        return self.__default
    @default.setter
    def default(self, value):
        self.__default = bool_to_str(value)
    
    @property
    def visible(self):
        return self.__visible
    @visible.setter
    def visible(self, value):
        self.__visible = bool_to_str(value)
        
    def get_toggles(self):
        return {
            'default': self.default,
            'visible': self.visible
        }

    def get_fields(self) -> dict:
        return {
            'application': self.application,
            'default': self.default,
            'visible': self.visible
        }

    def __str__(self):
        return f'{self.model_name}: {self.application}'
    

class ProfileCategoryGroupVisibility(ProfileFieldType):
    def __init__(self, dataCategories=[], dataCategoryGroup='', visibility='', api_version=default_api_version):
        super().__init__(api_version)
        self.dataCategories = dataCategories
        self.dataCategoryGroup = dataCategoryGroup
        self.__visibility = visibility

        self.model_name = 'categoryGroupVisibilities'
        
    @property
    def visibility(self):
        return self.__visibility
    @visibility.setter
    def visibility(self, value):
        self.__visibility = bool_to_str(value)
        
    def get_toggles(self):
        return {
            'visibility': self.visibility
        }
    
    def get_fields(self):
        return {
            'dataCategories': self.dataCategories,
            'dataCategoryGroup': self.dataCategoryGroup,
            'visibility': self.visibility,
        }

    def __str__(self):
        return f'{self.model_name}: {self.dataCategoryGroup}'


class ProfileApexClassAccess(ProfileFieldType):
    def __init__(self, apexClass='', enabled=False, api_version=default_api_version):
        super().__init__(api_version)
        self.apexClass = apexClass
        self.__enabled = enabled

        self.model_name = 'classAccesses'

    @property
    def enabled(self):
        return self.__enabled
    @enabled.setter
    def enabled(self, value):
        self.__enabled = bool_to_str(value)

    def get_toggles(self):
        return {
            'enabled': self.enabled
        }

    def get_fields(self):
        return {
            'apexClass': self.apexClass,
            'enabled': self.enabled
        }

    def __str__(self):
        return f'{self.model_name}: {self.apexClass}'


class ProfileCustomPermissions(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=default_api_version):
        super().__init__(api_version)
        self.__enabled = enabled
        self.name = name

        self.model_name = 'customPermissions'

    @property
    def enabled(self):
        return self.__enabled
    
    @enabled.setter
    def enabled(self, value):
        self.__enabled = bool_to_str(value)
    
    def get_toggles(self):
        return {
            'enabled': self.enabled
        }

    def get_fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    def __str__(self):
        return f'{self.model_name}: {self.name}'


class ProfileExternalDataSourceAccess(ProfileFieldType):
    def __init__(self, enabled=False, externalDataSource='', api_version=default_api_version):
        super().__init__(api_version)
        self.__enabled = enabled
        self.externalDataSource = externalDataSource

        self.model_name = 'externalDataSourceAccesses'
        
    @property
    def enabled(self):
        return self.__enabled
    
    @enabled.setter
    def enabled(self, value):
        self.__enabled = bool_to_str(value)

    def get_toggles(self):
        return {
            'enabled': self.enabled
        }

    def get_fields(self):
        return {
            'enabled': self.enabled,
            'externalDataSource': self.externalDataSource
        }

    def __str__(self):
        return f'{self.model_name}: {self.externalDataSource}'


class ProfileFieldLevelSecurity(ProfileFieldType):
    def __init__(self, editable=False, field='', readable=False, hidden=False, api_version=default_api_version):
        super().__init__(api_version)
        self.__editable = editable
        self.field = field
        self.__hidden = hidden
        self.__readable = readable

        if self.api_version <= 22:
            self.model_name = 'fieldLevelSecurities'
            
        else:
            self.model_name = 'fieldPermissions'

    @property
    def editable(self):
        return self.__editable
    @editable.setter
    def editable(self, value):
        self.__editable = bool_to_str(value)
    
    @property
    def hidden(self):
        return self.__hidden
    @hidden.setter
    def hidden(self, value):
        self.__hidden = bool_to_str(value)
    
    @property
    def readable(self):
        return self.__readable
    @readable.setter
    def readable(self, value):
        self.__readable = bool_to_str(value)
        
    def get_toggles(self):
        if self.api_version <= 22:
            return  {
                'editable': self.editable,
                'hidden': self.hidden,
                'readable': self.readable
            }
        else:
            return {
                'editable': self.editable,
                'readable': self.readable
            }

    def get_fields(self):
        return  {
                'editable': self.editable,
                'hidden': self.hidden,
                'field': self.field,
                'readable': self.readable
            }


    def __str__(self):
        return f'{self.model_name}: {self.field}'

class ProfileLayoutAssignments(ProfileFieldType):
    def __init__(self, layout='', recordType='', api_version=default_api_version):
        super().__init__(api_version)
        self.layout = layout
        self.recordType = recordType

        self.model_name = 'layoutAssignments'

    def get_fields(self):
        return {
            'layout': self.layout,
            'recordType': self.recordType
        }

    def __str__(self):
        if self.recordType != '':
            return f'{self.model_name}: {self.layout}: {self.recordType}'
        else:
            return f'{self.model_name}: {self.layout}'


class ProfileLoginHours(ProfileFieldType):
    def __init__(self, weekdayStart='', weekdayEnd='', api_version=default_api_version):
        super().__init__(api_version)
        self.weekdayStart = weekdayStart
        self.weekdayEnd = weekdayEnd

        self.model_name = 'loginHours'


    def get_fields(self):
        return {
            'weekdayStart': self.weekdayStart,
            'weekdayEnd': self.weekdayEnd
        }

    def __str__(self):
        return f'{self.model_name}: {self.weekdayStart}: {self.weekdayEnd}'
        

class ProfileLoginIpRanges(ProfileFieldType):
    def __init__(self, description='', endAddress='', startAddress='', api_version=default_api_version):
        super().__init__(api_version)
        self.description = description
        self.endAddress = endAddress
        self.startAddress = startAddress

        self.model_name = 'loginIpRanges'

    def get_fields(self):
        return {
            'description': self.description,
            'endAddress': self.endAddress,
            'startAddress': self.startAddress
        }

    def __str__(self):
        return f'{self.model_name}: {self.description}: {self.startAddress} - {self.endAddress}' 
    

class ProfileObjectPermissions(ProfileFieldType):
    def __init__(self, allowCreate=False, allowDelete=False, allowEdit=False,
        allowRead=False, modifyAllRecords=False, f_object='', viewAllRecords=False,
        api_version=default_api_version):
        super().__init__(api_version)
        self.__allowCreate = allowCreate
        self.__allowDelete = allowDelete
        self.__allowEdit = allowEdit
        self.__modifyAllRecords = modifyAllRecords
        self.object = f_object
        self.__viewAllRecords = viewAllRecords
        
        self.model_name = 'objectPermissions'

    @property
    def allowCreate(self):
        return self.__allowCreate
    @allowCreate.setter
    def allowCreate(self, value):
        self.__allowCreate = bool_to_str(value)

    @property
    def allowDelete(self):
        return self.__allowDelete
    @allowDelete.setter
    def allowDelete(self, value):
        self.__allowDelete = bool_to_str(value)

    @property
    def allowEdit(self):
        return self.__allowEdit
    @allowEdit.setter
    def allowEdit(self, value):
        self.__allowEdit = bool_to_str(value)
        
    @property
    def modifyAllRecords(self):
        return self.__modifyAllRecords
    @modifyAllRecords.setter
    def modifyAllRecords(self, value):
        self.__modifyAllRecords = bool_to_str(value)

    @property
    def viewAllRecords(self):
        return self.__viewAllRecords
    @viewAllRecords.setter
    def viewAllRecords(self, value):
        self.__viewAllRecords = bool_to_str(value)

    def get_toggles(self):
        if self.api_version < 14:
            return {
                'revokeCreate': self.allowCreate,
                'revokeDelete': self.allowDelete,
                'revokeEdit': self.allowEdit
            }
        elif self.api_version == 14:
            return {
                'allowCreate': self.allowCreate,
                'allowDelete': self.allowDelete,
                'allowEdit': self.allowEdit
            }
        else:
            return {
                'allowCreate': self.allowCreate,
                'allowDelete': self.allowDelete,
                'allowEdit': self.allowEdit,
                'modifyAllRecords': self.modifyAllRecords,
                'viewAllRecords': self.viewAllRecords,
            }

    def get_fields(self) -> dict:
        if self.api_version < 14:
            return {
                'revokeCreate': self.allowCreate,
                'revokeDelete': self.allowDelete,
                'revokeEdit': self.allowEdit,
                'object': self.object
            }
        elif self.api_version == 14:
            return {
                'allowCreate': self.allowCreate,
                'allowDelete': self.allowDelete,
                'allowEdit': self.allowEdit,
                'object': self.object
            }
        else:
            return {
                'allowCreate': self.allowCreate,
                'allowDelete': self.allowDelete,
                'allowEdit': self.allowEdit,
                'object': self.object,
                'modifyAllRecords': self.modifyAllRecords,
                'viewAllRecords': self.viewAllRecords,
            }

    def __str__(self):
        return f'{self.model_name}: {self.object}'


class ProfileApexPageAccess(ProfileFieldType):
    def __init__(self, apexPage='', enabled=False, api_version=default_api_version):
        super().__init__(api_version)
        self.apexPage = apexPage
        self.__enabled = enabled

        self.model_name = 'pageAccesses'

    @property
    def enabled(self):
        return self.__enabled
    @enabled.setter
    def enabled(self, value):
        self.__enabled = bool_to_str(value)

    def get_toggles(self):
        return {
            'enabled': self.enabled
        }

    def get_fields(self):
        return {
            'apexClass': self.apexPage,
            'enabled': self.enabled
        }

    def __str__(self):
        return f'{self.model_name}: {self.apexPage}'


class ProfileRecordTypeVisibility(ProfileFieldType):
    def __init__(self, default=True, personAccountDefault=True, recordType='', visible=True, api_version=default_api_version):
        super().__init__(api_version)
        self.default = default
        self.personAccountDefault = personAccountDefault
        self.recordType = recordType
        self.visible = visible

        self.model_name = 'recordTypeVisibilities'

    @property
    def default(self):
        return self.__default
    @default.setter
    def default(self, value):
        self.__default = bool_to_str(value)

    @property
    def personAccountDefault(self):
        return self.__personAccountDefault
    @personAccountDefault.setter
    def personAccountDefault(self, value):
        self.__personAccountDefault = bool_to_str(value)

    @property
    def visible(self):
        return self.__visible
    @visible.setter
    def visible(self, value):
        self.__visible = bool_to_str(value)

    def get_toggles(self):
        return {
            'default': self.default,
            'personAccountDefault': self.personAccountDefault,
            'visible': self.visible
        }

    def get_fields(self):
        return {
            'default': self.default,
            'personAccountDefault': self.personAccountDefault,
            'recordType': self.recordType,
            'visible': self.visible
        }

    def __str__(self):
        return f'{self.model_name}: {self.recordType}'


class ProfileTabVisibility(ProfileFieldType):
    def __init__(self, tab='', visibility='', api_version=default_api_version):
        super().__init__(api_version)
        self.tab = tab
        self.visibility = visibility

        self.model_name = 'tabVisibilities'
    
    def get_fields(self):
        return {
            'tab': self.tab,
            'visibilty': self.visibility
        }

    def __str__(self):
        return f'{self.model_name}: {self.tab}: {self.visibility}'

class ProfileUserPermission(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=default_api_version):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'userPermissions'

    @property
    def enabled(self):
        return self.__enabled
    @enabled.setter
    def enabled(self, value):
        self.__enabled = bool_to_str(value)

    def get_toggles(self):
        return {
            'enabled': self.enabled
        }

    def get_fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    def __str__(self):
        return f'{self.model_name}: {self.name}'


# TODO: handle different api versions
classes_by_modelName = {
    ProfileActionOverride().model_name: ProfileActionOverride,
    ProfileApexClassAccess().model_name: ProfileApexClassAccess,
    ProfileApexPageAccess().model_name: ProfileApexPageAccess,
    ProfileApplicationVisibility().model_name: ProfileApplicationVisibility,
    ProfileCategoryGroupVisibility().model_name: ProfileCategoryGroupVisibility,
    ProfileCustomPermissions().model_name: ProfileCustomPermissions,
    ProfileExternalDataSourceAccess().model_name: ProfileExternalDataSourceAccess,
    ProfileFieldLevelSecurity().model_name: ProfileFieldLevelSecurity,
    ProfileLayoutAssignments().model_name: ProfileLayoutAssignments,
    ProfileLoginHours().model_name: ProfileLoginHours,
    ProfileLoginIpRanges().model_name: ProfileLoginIpRanges,
    ProfileObjectPermissions().model_name: ProfileObjectPermissions,
    ProfileRecordTypeVisibility().model_name: ProfileRecordTypeVisibility,
    ProfileTabVisibility().model_name: ProfileTabVisibility,
    ProfileUserPermission().model_name: ProfileUserPermission
}

class Profile:
    def __init__(self, applicationVisibilities: List[ProfileApplicationVisibility],
        categoryGroupVisibilities: List[ProfileCategoryGroupVisibility], classAccesses: List[ProfileApexClassAccess],
        custom: bool, customPermissions: List[ProfileCustomPermissions], description: str,
        externalDataSourceAccesses: List[ProfileExternalDataSourceAccess], fieldPermissions: List[ProfileFieldLevelSecurity],
        fullName: str, layoutAssignments: List[ProfileLayoutAssignments], loginHours: List[ProfileLoginHours],
        loginIpRanges: List[ProfileLoginIpRanges], objectPermissions: List[ProfileObjectPermissions],
        pageAccesses: List[ProfileApexPageAccess], profileActionOverrides: List[ProfileActionOverride],
        recordTypeVisibilities: List[ProfileRecordTypeVisibility], tabVisibilities: List[ProfileTabVisibility],
        userLicense: str, userPermissions: List[ProfileUserPermission]):

        if apiVersion < 45:
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
            self.objectPermissions = objectPermissions
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