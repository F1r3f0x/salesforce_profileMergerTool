# -*- coding: utf-8 -*-
""" SF Profile Merger - Metadata Models.

This module has the definitions for the different Metadata types for Salesforce Profiles.
Checkout the docs:
    https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_profile.htm

Attributes:
    DEFAULT_API_VERSION (int):  The API version to use when creating objects.

Copyright: Patricio Labin Correa - 2019

@F1r3f0x
"""


from typing import List
from utils import str_to_bool

DEFAULT_API_VERSION = 63

class ProfileFieldType:
    """Base Metadata class
    Args:
        api_version (int): (default=DEFAULT_API_VERSION) Salesforce API Version

    Attributes:
        api_version (int): Human readable string describing the exception.
        model_name (str): Salesforce Metadata API name.
        model_fields (dict): Dict with the field name and value.
        model_toggles (dict): Dict with toggable fields and values.
    """

    def __init__(self, api_version=DEFAULT_API_VERSION):
        self.api_version = api_version
        self.model_id = ''
        self.model_name = ''
        self.model_fields = {}
        self.model_toggles = {}
        self.model_disabled = False

    def _set_fields(self, input_fields: dict):
        if input_fields:
            for field, value in input_fields.items():
                setattr(self, field, value)

    @property
    def toggles(self) -> dict:
        return self.model_toggles

    @property
    def fields(self) -> dict:
        return self.model_fields

    @fields.setter
    def fields(self, input_fields: dict):
        self._set_fields(input_fields)

    @property
    def id(self) -> str:
        return f'{self.model_name}-{self.model_id}'

    def __set_id__(self):
        pass

    def __str__(self):
        return f'<{self.model_name}: {self.model_id}>'


# Metadata Classes
class ProfileActionOverride(ProfileFieldType):
    def __init__(
        self, actionName='', content='', formFactor='', pageOrSobjectType='', recordType='',
        f_type='', api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.actionName = actionName
        self.content = content
        self.formFactor = formFactor
        self.pageOrSobjectType = pageOrSobjectType
        self.recordType = recordType
        self.type = f_type

        self.model_name = 'profileActionOverrides'
        self.__set_id__()

    @property
    def fields(self) -> dict:
        return {
            'actionName': self.actionName,
            'content': self.content,
            'formFactor': self.formFactor,
            'pageOrSobjectType': self.pageOrSobjectType,
            'recordType': self.recordType,
            'type': self.type,
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.actionName}: {self.content}: {self.pageOrSobjectType}: {self.type}'


class ProfileApplicationVisibility(ProfileFieldType):
    def __init__(
        self, application='', default=False, visible=False,
        api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.application = application
        self.__default = default
        self.__visible = visible

        self.model_name = 'applicationVisibilities'
        self.__set_id__()

    @property
    def default(self):
        return self.__default

    @default.setter
    def default(self, value):
        self.__default = str_to_bool(value)

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'default': self.default,
            'visible': self.visible
        }

    @property
    def fields(self) -> dict:
        return {
            'application': self.application,
            'default': self.default,
            'visible': self.visible
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.application}'


#Removed dataCategories and visibility default is = ALL
class ProfileCategoryGroupVisibility(ProfileFieldType):
    def __init__(
        self, dataCategoryGroup='', visibility='ALL',
        api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.dataCategoryGroup = dataCategoryGroup
        self.__visibility = visibility

        self.model_name = 'categoryGroupVisibilities'
        self.__set_id__()

    @property
    def visibility(self):
        return self.__visibility

    @visibility.setter
    def visibility(self, value):
        if value == "ALL":
            self.__visibility = "ALL"
        else:
            self.__visibility = str_to_bool(value)


    @property
    def toggles(self):
        return {
            'visibility': self.visibility
        }

    @property
    def fields(self):
        return {
            'dataCategoryGroup': self.dataCategoryGroup,
            'visibility': self.visibility,
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.dataCategoryGroup}'


class ProfileApexClassAccess(ProfileFieldType):
    def __init__(self, apexClass='', enabled=False, api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.apexClass = apexClass
        self.__enabled = enabled

        self.model_name = 'classAccesses'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'apexClass': self.apexClass,
            'enabled': self.enabled
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.apexClass}'


class ProfileCustomPermissions(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.__enabled = enabled
        self.name = name

        self.model_name = 'customPermissions'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.name}'


class ProfileCustomMetadataTypeAccess(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'customMetadataTypeAccesses'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        if self.enabled != False:
            self.model_id = f'{self.name}: {self.enabled}'
        else:
            self.model_id = f'{self.name}'



class ProfileCustomSettingAccesses(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'customSettingAccesses'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        if self.enabled != False:
            self.model_id = f'{self.name}: {self.enabled}'
        else:
            self.model_id = f'{self.name}'


class ProfileExternalDataSourceAccess(ProfileFieldType):
    def __init__(self, enabled=False, externalDataSource='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.__enabled = enabled
        self.externalDataSource = externalDataSource

        self.model_name = 'externalDataSourceAccesses'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'externalDataSource': self.externalDataSource
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.externalDataSource}'


#readable por padrão tem que ser editable
class ProfileFieldLevelSecurity(ProfileFieldType):
    def __init__(
        self, editable=False, field='', readable=None, hidden=False,
        api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.__editable = editable
        self.field = field
        self.__hidden = hidden
        self.__readable = True if editable or readable is None else readable
        self.model_name = 'fieldLevelSecurities' if self.api_version <= 22 else 'fieldPermissions'
        self.__set_id__()

    @property
    def editable(self):
        return self.__editable

    @editable.setter
    def editable(self, value):
        self.__editable = str_to_bool(value)

    @property
    def hidden(self):
        return self.__hidden

    @hidden.setter
    def hidden(self, value):
        self.__hidden = str_to_bool(value)

    @property
    def readable(self):
        return self.__readable

    @readable.setter
    def readable(self, value):
        self.__readable = str_to_bool(value)

    @property
    def toggles(self):
        toggles = {
            'editable': self.editable,
            'readable': self.readable
        }
        if self.api_version <= 22:
            toggles['hidden'] = self.hidden
        return toggles

    @property
    def fields(self):
        if self.api_version <= 22:
            return {
                    'editable': self.editable,
                    'hidden': self.hidden,
                    'field': self.field,
                    'readable': self.readable
                }
        else:
            return {
                    'editable': self.editable,
                    'field': self.field,
                    'readable': self.readable
                }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.field}'

class ProfileFlowAccess(ProfileFieldType):
    def __init__(self, enabled=False, flow='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.flow = flow

        self.model_name = 'flowAccesses'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'flow': self.flow
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        if self.enabled != False:
            self.model_id = f'{self.flow}: {self.enabled}'
        else:
            self.model_id = f'{self.flow}'

class ProfileLayoutAssignments(ProfileFieldType):
    def __init__(self, layout='', recordType='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.layout = layout
        self.recordType = recordType

        self.model_name = 'layoutAssignments'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'layout': self.layout,
            'recordType': self.recordType
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        if self.recordType != '':
            self.model_id = f'{self.layout}: {self.recordType}'
        else:
            self.model_id = f'{self.layout}'


class ProfileLoginHours(ProfileFieldType):
    def __init__(self, weekdayStart='', weekdayEnd='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.weekdayStart = weekdayStart
        self.weekdayEnd = weekdayEnd

        self.model_name = 'loginHours'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'weekdayStart': self.weekdayStart,
            'weekdayEnd': self.weekdayEnd
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.weekdayStart}: {self.weekdayEnd}'


class ProfileLoginIpRanges(ProfileFieldType):
    def __init__(
        self, description='', endAddress='', startAddress='', api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.description = description
        self.endAddress = endAddress
        self.startAddress = startAddress

        self.model_name = 'loginIpRanges'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'description': self.description,
            'endAddress': self.endAddress,
            'startAddress': self.startAddress
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.description}: {self.startAddress} - {self.endAddress}'


class ProfileObjectPermissions(ProfileFieldType):
    def __init__(
        self, allowCreate=False, allowDelete=False, allowEdit=False,
        allowRead=False, modifyAllRecords=False, f_object='', viewAllRecords=False,
        api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.__allowCreate = allowCreate
        self.__allowDelete = allowDelete
        self.__allowEdit = allowEdit
        self.__allowRead = allowRead
        self.__modifyAllRecords = modifyAllRecords
        self.object = f_object
        self.__viewAllRecords = viewAllRecords

        self.model_name = 'objectPermissions'
        self.__set_id__()

    @property
    def allowCreate(self):
        return self.__allowCreate

    @allowCreate.setter
    def allowCreate(self, value):
        self.__allowCreate = str_to_bool(value)

    @property
    def allowDelete(self):
        return self.__allowDelete

    @allowDelete.setter
    def allowDelete(self, value):
        self.__allowDelete = str_to_bool(value)

    @property
    def allowEdit(self):
        return self.__allowEdit

    @allowEdit.setter
    def allowEdit(self, value):
        self.__allowEdit = str_to_bool(value)

    @property
    def allowRead(self):
        return self.__allowRead

    @allowRead.setter
    def allowRead(self, value):
        self.__allowRead = str_to_bool(value)

    @property
    def modifyAllRecords(self):
        return self.__modifyAllRecords

    @modifyAllRecords.setter
    def modifyAllRecords(self, value):
        self.__modifyAllRecords = str_to_bool(value)

    @property
    def viewAllRecords(self):
        return self.__viewAllRecords

    @viewAllRecords.setter
    def viewAllRecords(self, value):
        self.__viewAllRecords = str_to_bool(value)

    @property
    def toggles(self):
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
                'allowEdit': self.allowEdit,
                'allowRead': self.allowRead
            }
        else:
            return {
                'allowCreate': self.allowCreate,
                'allowDelete': self.allowDelete,
                'allowEdit': self.allowEdit,
                'allowRead': self.allowRead,
                'modifyAllRecords': self.modifyAllRecords,
                'viewAllRecords': self.viewAllRecords,
            }

    @property
    def fields(self) -> dict:
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
                'allowRead': self.allowRead,
                'object': self.object
            }
        else:
            return {
                'allowCreate': self.allowCreate,
                'allowDelete': self.allowDelete,
                'allowEdit': self.allowEdit,
                'allowRead': self.allowRead,
                'modifyAllRecords': self.modifyAllRecords,
                'object': self.object,
                'viewAllRecords': self.viewAllRecords,
            }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.object}'


class ProfileApexPageAccess(ProfileFieldType):
    def __init__(self, apexPage='', enabled=False, api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.apexPage = apexPage
        self.__enabled = enabled

        self.model_name = 'pageAccesses'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'apexPage': self.apexPage,
            'enabled': self.enabled
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.apexPage}'


#default changed to False
class ProfileRecordTypeVisibility(ProfileFieldType):
    def __init__(
        self, default=False, personAccountDefault=None, recordType='', visible=True,
        api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.default = default
        self.personAccountDefault = personAccountDefault
        self.recordType = recordType
        self.visible = visible

        self.model_name = 'recordTypeVisibilities'
        self.__set_id__()

    @property
    def default(self):
        return self.__default

    @default.setter
    def default(self, value):
        self.__default = str_to_bool(value)

    @property
    def personAccountDefault(self):
        return self.__personAccountDefault

    @personAccountDefault.setter
    def personAccountDefault(self, value):
        self.__personAccountDefault = str_to_bool(value)

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'default': self.default,
            'personAccountDefault': self.personAccountDefault,
            'visible': self.visible
        }

    @property
    def fields(self):
        return {
            'default': self.default,
            'personAccountDefault': self.personAccountDefault,
            'recordType': self.recordType,
            'visible': self.visible
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.recordType}'


class ProfileTabVisibility(ProfileFieldType):
    def __init__(self, tab='', visibility='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.tab = tab
        self.visibility = visibility

        self.model_name = 'tabVisibilities'
        self.__set_id__()

    @property
    def fields(self):
        return {
            'tab': self.tab,
            'visibility': self.visibility
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.tab}: {self.visibility}'


class ProfileUserPermission(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'userPermissions'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)
        self.__set_id__()

    def __set_id__(self):
        self.model_id = f'{self.name}'


class ProfileCustomMetadataTypeAccess(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'customMetadataTypeAccesses'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    def __set_id__(self):
        return f'{self.name}'


class ProfileCustomSettingAccess(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'customSettingAccess'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'name': self.name
        }

    def __set_id__(self):
        return f'{self.name}'


class ProfileFlowAccess(ProfileFieldType):
    def __init__(self, enabled=False, flow='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.flow = flow

        self.model_name = 'flowAccess'
        self.__set_id__()

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'enabled': self.enabled
        }

    @property
    def fields(self):
        return {
            'enabled': self.enabled,
            'flow': self.flow
        }

    def __set_id__(self):
        return f'{self.flow}'


class LoginFlow(ProfileFieldType):
    def __init__(self, flow='', flow_type='UI', friendlyname='', uiLoginFlowType='',
                useLightningRuntime='', vfFlowType='', vfFlowPageTitle='',
                api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.flow = flow
        self.flow_type = flow_type
        self.friendlyname = friendlyname
        self.uiLoginFlowType = uiLoginFlowType
        self.useLightningRuntime = useLightningRuntime
        self.vfFlowType = vfFlowType
        self.vfFlowPageTitle = vfFlowPageTitle

        self.model_name = 'loginFlow'
        self.__set_id__()


    @property
    def fields(self):
        return {
            'flow': self.flow,
            'flowType': self.flow_type,
            'friendlyName': self.friendlyname,
            'uiLoginFlowType': self.uiLoginFlowType,
            'useLightningRuntime': self.useLightningRuntime,
            'vfFlowType': self.vfFlowType,
            'vfFlowPageTitle': self.vfFlowPageTitle
        }

    def __set_id__(self):
        return f'{self.flow}: {self.friendlyname}'


class ProfileSingleValue(ProfileFieldType):
    def __init__(self, model_name, value, is_boolean=False, api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.model_name = model_name

        if is_boolean:
            value = str_to_bool(value)
        self.value = value
        self.model_id = f'{self.model_name}'


# TODO: handle different api versions
classes_by_modelName = {
    ProfileApplicationVisibility().model_name: ProfileApplicationVisibility,
    ProfileCategoryGroupVisibility().model_name: ProfileCategoryGroupVisibility,
    ProfileApexClassAccess().model_name: ProfileApexClassAccess,
    'custom': ProfileSingleValue,
    ProfileCustomMetadataTypeAccess().model_name: ProfileCustomMetadataTypeAccess,
    ProfileCustomPermissions().model_name: ProfileCustomPermissions,
    ProfileCustomSettingAccess().model_name: ProfileCustomSettingAccess,
    'description': ProfileSingleValue,
    ProfileExternalDataSourceAccess().model_name: ProfileExternalDataSourceAccess,
    ProfileFieldLevelSecurity().model_name: ProfileFieldLevelSecurity,
    ProfileFlowAccess().model_name: ProfileFlowAccess,
    'fullName': ProfileSingleValue,
    ProfileLayoutAssignments().model_name: ProfileLayoutAssignments,
    LoginFlow().model_name: LoginFlow,
    ProfileLoginHours().model_name: ProfileLoginHours,
    ProfileLoginIpRanges().model_name: ProfileLoginIpRanges,
    ProfileObjectPermissions().model_name: ProfileObjectPermissions,
    ProfileApexPageAccess().model_name: ProfileApexPageAccess,
    ProfileActionOverride().model_name: ProfileActionOverride,
    ProfileRecordTypeVisibility().model_name: ProfileRecordTypeVisibility,
    ProfileTabVisibility().model_name: ProfileTabVisibility,
    'userLicense': ProfileSingleValue,
    ProfileUserPermission().model_name: ProfileUserPermission
}

# TODO: Update API versions
class Profile:
    def __init__(
        self,
        applicationVisibilities: List[ProfileApplicationVisibility],
        categoryGroupVisibilities: List[ProfileCategoryGroupVisibility],
        classAccesses: List[ProfileApexClassAccess],
        custom: bool,
        customMetadataTypeAcceses: List[ProfileCustomMetadataTypeAccess],
        customPermissions: List[ProfileCustomPermissions],
        customSettingAccesses: List[ProfileCustomSettingAccess],
        description: str,
        externalDataSourceAccesses: List[ProfileExternalDataSourceAccess],
        fieldPermissions: List[ProfileFieldLevelSecurity],
        flowAccesses: List[ProfileFlowAccess],
        fullName: str, 
        layoutAssignments: List[ProfileLayoutAssignments],
        loginFlows: List[LoginFlow],
        loginHours: List[ProfileLoginHours],
        loginIpRanges: List[ProfileLoginIpRanges],
        objectPermissions: List[ProfileObjectPermissions],
        pageAccesses: List[ProfileApexPageAccess],
        profileActionOverrides: List[ProfileActionOverride],
        recordTypeVisibilities: List[ProfileRecordTypeVisibility],
        tabVisibilities: List[ProfileTabVisibility],
        userLicense: str, userPermissions: List[ProfileUserPermission],
        customMetadataTypeAccesses: List[ProfileCustomMetadataTypeAccess],
        apiVersion=DEFAULT_API_VERSION,
    ):
        self.fullName = fullName
        self.layoutAssignments = layoutAssignments
        self.classAccesses = classAccesses
        self.pageAccesses = pageAccesses
        self.tabVisibilities = tabVisibilities
        self.loginFlows = loginFlows
        if apiVersion >= 17:
            self.userLicense = userLicense
            self.loginIpRanges = loginIpRanges
        if apiVersion <= 22: self.fieldLevelSecurities = fieldPermissions
        else: self.fieldPermissions = fieldPermissions
        if apiVersion >= 25: self.loginHours = loginHours
        if apiVersion >= 27: self.externalDataSourceAccesses = externalDataSourceAccesses
        if apiVersion >= 28: self.objectPermissions = objectPermissions
        if apiVersion >= 29:
            self.userPermissions = userPermissions
            self.recordTypeVisibilities = recordTypeVisibilities
        if apiVersion >= 30:
            self.custom = custom
            self.description = description
        if apiVersion >= 31: self.customPermissions = customPermissions
        if apiVersion >= 37 and apiVersion <= 44: self.profileActionOverrides = profileActionOverrides
        if apiVersion >= 41: self.categoryGroupVisibilities = categoryGroupVisibilities
        if apiVersion < 45: self.applicationVisibilities = applicationVisibilities
        if apiVersion >= 47:
            self.customMetadataTypeAcceses = customMetadataTypeAcceses
            self.customSettingAccesses = customSettingAccesses
            self.flowAccesses = flowAccesses
