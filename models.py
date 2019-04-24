from typing import List
from enum import Enum

#from main import apiVersion

apiVersion = 44

# Metadata Classes
class ProfileActionOverride:
    def __init__(self, actionName: str, content: str, formFactor: str, pageOrSobjectType: str, recordType: str, type:str):
        self.actionName = actionName
        self.content = content
        self.formFactor = formFactor
        self.pageOrSobjectType = pageOrSobjectType
        self.recordType = recordType
        self.type = type

class ProfileApplicationVisibility:
    def __init__(self, application: str, default: bool, visible: bool ):
        self.application = application
        self.default = bool
        self.visible = bool

class ProfileCategoryGroupVisibility:
    def __init__(self, dataCategories: List[str], dataCategoryGroup: str, visibility: str ):
        self.dataCategories = dataCategories
        self.dataCategoryGroup = dataCategoryGroup
        self.visibility = visibility

class ProfileApexClassAccess:
    def __init__(self, apexClass: str, enabled: bool):
        self.apexClass = apexClass
        self.enabled = enabled

class ProfileCustomPermissions:
    def __init__(self, enabled: bool, name: str):
        self.enabled = enabled
        self.name = name

class ProfileExternalDataSourceAccess:
    def __init__(self, enabled: bool, externalDataSource: str ):
        self.enabled = enabled
        self.externalDataSource = externalDataSource
        
class ProfileFieldLevelSecurity:
    def __init__(self, editable: bool, field: str , readable: bool, hidden: bool):
        self.editable = editable
        self.field = field
        if apiVersion <= 22.0:
            self.hidden = hidden
        self.readable = readable

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
        if apiVersion >= 31:
            self.custom = custom
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