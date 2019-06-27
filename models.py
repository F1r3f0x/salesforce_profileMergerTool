# -*- coding: utf-8 -*-
""" SF Profile Migrator - Metadata Models.

This module has the definitions for the differente Metadata types for Salesforce Profiles.
Checkout the docs: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_profile.htm

Attributes:
    DEFAULT_API_VERSION (int):  The API version to use when creating objects.

Copyright: Patricio Labin Correa - 2019
"""

from typing import List
from utils import str_to_bool

DEFAULT_API_VERSION = 44


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

    def __str__(self):
        return f'{self.model_name}: {self.actionName}: {self.content}: {self.pageOrSobjectType}: {self.type}'


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

    def __str__(self):
        return f'{self.model_name}: {self.application}'


class ProfileCategoryGroupVisibility(ProfileFieldType):
    def __init__(
        self, dataCategories=[], dataCategoryGroup='', visibility='',
        api_version=DEFAULT_API_VERSION
    ):
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
        self.__visibility = str_to_bool(value)

    @property
    def toggles(self):
        return {
            'visibility': self.visibility
        }

    @property
    def fields(self):
        return {
            'dataCategories': self.dataCategories,
            'dataCategoryGroup': self.dataCategoryGroup,
            'visibility': self.visibility,
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)

    def __str__(self):
        return f'{self.model_name}: {self.dataCategoryGroup}'


class ProfileApexClassAccess(ProfileFieldType):
    def __init__(self, apexClass='', enabled=False, api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.apexClass = apexClass
        self.__enabled = enabled

        self.model_name = 'classAccesses'

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

    def __str__(self):
        return f'{self.model_name}: {self.apexClass}'


class ProfileCustomPermissions(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.__enabled = enabled
        self.name = name

        self.model_name = 'customPermissions'

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

    def __str__(self):
        return f'{self.model_name}: {self.name}'


class ProfileExternalDataSourceAccess(ProfileFieldType):
    def __init__(self, enabled=False, externalDataSource='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.__enabled = enabled
        self.externalDataSource = externalDataSource

        self.model_name = 'externalDataSourceAccesses'

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

    def __str__(self):
        return f'{self.model_name}: {self.externalDataSource}'


class ProfileFieldLevelSecurity(ProfileFieldType):
    def __init__(
        self, editable=False, field='', readable=False, hidden=False,
        api_version=DEFAULT_API_VERSION
    ):
        super().__init__(api_version)
        self.__editable = editable
        self.field = field
        self.__hidden = hidden
        self.__readable = readable

        self.model_name = 'fieldLevelSecurities' if self.api_version <= 22 else 'fieldPermissions'

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

    def __str__(self):
        return f'{self.model_name}: {self.field}'


class ProfileLayoutAssignments(ProfileFieldType):
    def __init__(self, layout='', recordType='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.layout = layout
        self.recordType = recordType

        self.model_name = 'layoutAssignments'

    @property
    def fields(self):
        return {
            'layout': self.layout,
            'recordType': self.recordType
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)

    def __str__(self):
        if self.recordType != '':
            return f'{self.model_name}: {self.layout}: {self.recordType}'
        else:
            return f'{self.model_name}: {self.layout}'


class ProfileLoginHours(ProfileFieldType):
    def __init__(self, weekdayStart='', weekdayEnd='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.weekdayStart = weekdayStart
        self.weekdayEnd = weekdayEnd

        self.model_name = 'loginHours'

    @property
    def fields(self):
        return {
            'weekdayStart': self.weekdayStart,
            'weekdayEnd': self.weekdayEnd
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)

    def __str__(self):
        return f'{self.model_name}: {self.weekdayStart}: {self.weekdayEnd}'


class ProfileLoginIpRanges(ProfileFieldType):
    def __init__(self, description='', endAddress='', startAddress='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.description = description
        self.endAddress = endAddress
        self.startAddress = startAddress

        self.model_name = 'loginIpRanges'

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

    def __str__(self):
        return f'{self.model_name}: {self.description}: {self.startAddress} - {self.endAddress}'


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

    def __str__(self):
        return f'{self.model_name}: {self.object}'


class ProfileApexPageAccess(ProfileFieldType):
    def __init__(self, apexPage='', enabled=False, api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.apexPage = apexPage
        self.__enabled = enabled

        self.model_name = 'pageAccesses'

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

    def __str__(self):
        return f'{self.model_name}: {self.apexPage}'


class ProfileRecordTypeVisibility(ProfileFieldType):
    def __init__(
        self, default=True, personAccountDefault=None, recordType='', visible=True,
        api_version=DEFAULT_API_VERSION
    ):
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

    def __str__(self):
        return f'{self.model_name}: {self.recordType}'


class ProfileTabVisibility(ProfileFieldType):
    def __init__(self, tab='', visibility='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.tab = tab
        self.visibility = visibility

        self.model_name = 'tabVisibilities'

    @property
    def fields(self):
        return {
            'tab': self.tab,
            'visibility': self.visibility
        }

    @fields.setter
    def fields(self, input_dict: dict):
        self._set_fields(input_dict)

    def __str__(self):
        return f'{self.model_name}: {self.tab}: {self.visibility}'


class ProfileUserPermission(ProfileFieldType):
    def __init__(self, enabled=False, name='', api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.enabled = enabled
        self.name = name

        self.model_name = 'userPermissions'

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

    def __str__(self):
        return f'{self.model_name}: {self.name}'


class ProfileSingleValue(ProfileFieldType):
    def __init__(self, model_name, value, is_boolean=False, api_version=DEFAULT_API_VERSION):
        super().__init__(api_version)
        self.model_name = model_name
        
        if is_boolean:
            value = str_to_bool(value) 
        self.value = value

    @property
    def toggles(self):
        return None

    @property
    def fields(self) -> dict:
        return None

    def __str__(self):
        return f'{self.model_name}'


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
    ProfileUserPermission().model_name: ProfileUserPermission,
    'custom': ProfileSingleValue,
    'description': ProfileSingleValue,
    'fullName': ProfileSingleValue,
    'userLicense': ProfileSingleValue
}


class Profile:
    def __init__(
        self, applicationVisibilities: List[ProfileApplicationVisibility],
        categoryGroupVisibilities: List[ProfileCategoryGroupVisibility], classAccesses: List[ProfileApexClassAccess],
        custom: bool, customPermissions: List[ProfileCustomPermissions], description: str,
        externalDataSourceAccesses: List[ProfileExternalDataSourceAccess], fieldPermissions: List[ProfileFieldLevelSecurity],
        fullName: str, layoutAssignments: List[ProfileLayoutAssignments], loginHours: List[ProfileLoginHours],
        loginIpRanges: List[ProfileLoginIpRanges], objectPermissions: List[ProfileObjectPermissions],
        pageAccesses: List[ProfileApexPageAccess], profileActionOverrides: List[ProfileActionOverride],
        recordTypeVisibilities: List[ProfileRecordTypeVisibility], tabVisibilities: List[ProfileTabVisibility],
        userLicense: str, userPermissions: List[ProfileUserPermission], apiVersion=DEFAULT_API_VERSION
    ):
        self.fullName = fullName
        self.layoutAssignments = layoutAssignments
        self.classAccesses = classAccesses
        self.pageAccesses = pageAccesses
        self.tabVisibilities = tabVisibilities
        if apiVersion <= 22: self.fieldLevelSecurities = fieldPermissions
        else: self.fieldPermissions = fieldPermissions
        if apiVersion >= 17: self.userLicense = userLicense
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
        if apiVersion < 45: self.applicationVisibilities = applicationVisibilities
        if apiVersion >= 41: self.categoryGroupVisibilities = categoryGroupVisibilities
        if apiVersion >= 17: self.loginIpRanges = loginIpRanges
        if apiVersion >= 37 and apiVersion <= 44: self.profileActionOverrides = profileActionOverrides
