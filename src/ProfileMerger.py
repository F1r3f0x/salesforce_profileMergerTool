# -*- coding: utf-8 -*-
""" SF Profile Merger.

Profile Merger Class

Copyright: Patricio Labin Correa - 2019

@F1r3f0x
"""

import re
import logging
from xml.etree import ElementTree
from xml.dom import minidom
from dataclasses import dataclass

import models
from utils import setup_logging


PROFILE_A = 'A'
PROFILE_B = 'B'
PROFILE_MERGED = 'AB'
DEFAULT_OUTPUT_PATH = 'merged_profile.profile'
LOGFILE_NAME = 'profilemerger'

@dataclass
class ValueMerge:
    field_id: str
    field_ref: models.ProfileFieldType
    values_a: list
    values_b: list

    @property
    def is_different(self) -> bool:
        for value_name, value_a in self.values_a.items():
            value_b = self.values_b.get(value_name)
            if value_a != value_b:
                return True
        return False

    def __str__(self) -> str:
        return f'{self.field_id} || {self.values_a}  --> {self.values_b}'


class Profile:
    """This class handles profile scanning, field generation and saving.

    Attributes:
        name (str): Instance Name.
        file_path (str): Path to the Salesforce profile file.
        namespace (str): Profile namespace.
        fields (dict): Profile fields container.
        is_merged (bool): If the profile is merged.
        diffs (list[ValueMerge]): Differences between the two profiles.
    """

    def __init__(self, name: str, file_path: str = None, namespace=None, *args, **kwargs):
        self.name = name
        self.file_path = file_path
        self.namespace = None
        self.__fields = {}
        self.is_merged = False
        self.__diffs = []

        if file_path and not file_path.isspace():
            self.scan_file(file_path)


    def scan_file(self, file_path=None) -> dict:
        """Scans a *.profile* file to get all the fields with their types.

        Args:
            file_path (_type_, optional): Path to the *.profile* file. Defaults to None.

        Returns:
            dict: Fields dictionary.
        """
        self.clear()
        self.file_path = file_path

        # Loop through profile XML
        tree = ElementTree.parse(self.file_path)
        tree_root = tree.getroot()

        # This regex is for removing the namespace prefix of the tag
        namespace_pattern = '^{.*}'
        namespace_regex = re.compile(namespace_pattern)

        # Create Fields for the Profile
        tag = ''
        for profile_field_element in tree_root:
            namespace = namespace_regex.match(profile_field_element.tag).group()
            namespace_value = namespace.replace('{', '').replace('}', '')
            self.namespace = namespace_value

            field_type_name = profile_field_element.tag.replace(namespace, '')

            # TODO: create exception and handle if not found
            model_class = models.classes_by_modelName.get(field_type_name)

            if model_class:
                # Read metadata from xml
                fields = {}
                for element_child in profile_field_element:
                    tag = element_child.tag.replace(namespace, '')
                    fields[tag] = element_child.text

                profile_field = None
                if model_class is models.ProfileSingleValue:
                    if field_type_name == 'custom':
                        profile_field = model_class(
                            field_type_name, profile_field_element.text, is_boolean=True
                        )
                    else:
                        profile_field = model_class(field_type_name, profile_field_element.text)
                else:
                    profile_field = model_class()
                    profile_field.fields = fields

                _id = profile_field.id
                self.fields[_id] = profile_field
        return self.fields


    def save_file(self, override_file_path=DEFAULT_OUTPUT_PATH) -> bool:
        """Picks a path and saves the merged profile to it.
        """

        if override_file_path is not None:
            self.file_path = override_file_path

        if self.file_path is None:
            return

        xml_root = ElementTree.Element(
            'Profile', attrib={'xmlns': 'http://soap.sforce.com/2006/04/metadata'}
        )

        #  Goes through the profile fields and creates a new xml
        sub_element = None
        for model_field in sorted(
            self.fields.values(), key=lambda x: x.id
        ):
            if not model_field.model_disabled:
                if type(model_field) is not models.ProfileSingleValue:
                    sub_element = ElementTree.SubElement(xml_root, model_field.model_name)
                    if model_field.fields:
                        for field, value in model_field.fields.items():
                            if value and value != '':
                                if type(value) is bool:
                                    value = str(value).lower()
                                ElementTree.SubElement(sub_element, field).text = value
                else:
                    field = model_field.model_name
                    value = model_field.value
                    if value is not None and value != '':
                        if type(value) is bool:
                            value = str(value).lower()
                        sub_element = ElementTree.SubElement(xml_root, model_field.model_name)
                        sub_element.text = value

        # Get the xml as a String and then prettyfies it
        xml_str = ElementTree.tostring(xml_root, 'utf-8')
        reparsed = minidom.parseString(xml_str)
        xml_str = reparsed.toprettyxml(indent="    ", encoding='UTF-8').decode('utf-8').rstrip()

        # Write to the selected path
        with open(self.file_path, 'w', encoding='utf-8') as file_pointer:
            file_pointer.write(xml_str)

        return True


    @property
    def fields(self) -> dict:
        return self.__fields


    @fields.setter
    def fields(self, fields_iter):
        if type(fields_iter) is list:
            fields = {}
            for field in fields_iter:
                fields[field.id] = field
            self.__fields = fields

        if type(fields_iter) is dict:
            self.__fields = fields_iter


    def add(self, field: models.ProfileFieldType):
        self.fields[field.id] = field


    def remove(self, field: models.ProfileFieldType):
        self.fields.pop(field.id)


    def get(self, field_id: str) -> models.ProfileFieldType:
        field = self.fields.get(field_id)
        if not field:
            raise KeyError('Field Not Found')
        return field


    def disable(self, field_id: str) -> models.ProfileFieldType:
        field = self.get(field_id)
        field.model_disabled = False
        return field


    def enable(self, field_id) -> models.ProfileFieldType:
        field = self.get(field_id)
        field.model_disabled = True
        return field


    def clear(self):
        self.namespace = None
        self.file_path = None
        self.fields.clear()



    @property
    def diffs(self) -> list[ValueMerge]:
        return self.__diffs


    @diffs.setter
    def diffs(self, diffs: list):
        self.__diffs = diffs


    def __str__(self) -> str:
        return f'Profile {self.name}: File Path="{self.file_path}" Fields Qty={len(self.fields)}'


class ProfileMerger:
    """This class handles the merges

    Attributes:

    """

    def __init__(self, profile_a_path: str = None , profile_b_path: str = None, profile_a: Profile = None, profile_b: Profile = None, *args, **kwargs):
        self.profile_a = Profile(PROFILE_A, profile_a_path) if profile_a_path is not None else profile_a
        self.profile_b = Profile(PROFILE_B, profile_b_path) if profile_b_path is not None else profile_b
        self.profile_merged = Profile(PROFILE_MERGED)
        self.profiles = [self.profile_a, self.profile_b, self.profile_merged]
        self.merge_a_to_b = False



    def merge(self, profile_a_path: str=None , profile_b_path: str=None) -> Profile:

        self.profile_merged.clear()

        if profile_a_path and not profile_a_path.isspace():
            self.profile_a.scan_file(profile_a_path)

        if profile_b_path and not profile_b_path.isspace():
            self.profile_b.scan_file(profile_b_path)

        profiles = (self.profile_b, self.profile_a)
        if not self.merge_a_to_b:
            profiles = profiles[::-1]

        base = profiles[0]
        other = profiles[1]

        logging.info(f'Base Profile {base}')
        logging.info(f'Other Profile {other}')
        
        diffs = []

        # Add base fields to merged profile
        base_fields = base.fields
        for _id, field in base_fields.items():
            self.profile_merged.fields[_id] = field
            logging.debug(f'Added field to merge profile: {_id}{field}')
            
            # Track non existing fields in the other profile
            if not other.fields.get(_id):
                value_merge = ValueMerge(_id, field, None, field.fields)
                diffs.append(value_merge)
                logging.debug(f'Missing Field: {value_merge}')
            
            
        base.is_merged = True

        # Add other fields to merge profile, log the diffs
        other_fields = other.fields
        for _id, field in other_fields.items():
            merged_field = self.profile_merged.fields.get(_id)
            if merged_field:
                value_merge = ValueMerge(_id, field, merged_field.fields, field.fields)
                logging.debug(f'Different Field: {value_merge}')
                if value_merge.is_different:
                    diffs.append(value_merge)
            else:
                value_merge = ValueMerge(_id, None, field, field.fields)
                logging.debug(f'Added Field: {value_merge}')
                diffs.append(value_merge)
            self.profile_merged.fields[_id] = field
        other.is_merged = True

        if (base.is_merged and other.is_merged):
            self.profile_merged.is_merged = True
            self.profile_merged.diffs = diffs

        for i, diff in enumerate(diffs):
            logging.info(f'Difference {i}: {diff}')

        return self.profile_merged


    def merge_and_save(self, profile_a_path: str=None , profile_b_path: str=None) -> bool:
        self.merge(profile_a_path, profile_b_path)
        return self.profile_merged.save_file()


def parse_args():
    """
    Parses command line arguments to create a Profile Merger.

    Returns:
        argparse.Namespace: The parsed arguments.

    Raises:
        SystemExit: If required arguments are missing.
    """
    parser = argparse.ArgumentParser(description='Profile Merger')
    parser.add_argument('-a', '--profile_a', required=True, help='Path to Profile A')
    parser.add_argument('-b', '--profile_b', required=True, help='Path to Profile B')
    parser.add_argument('-o', '--output', required=True, help='Output file')
    parser.add_argument('-l', '--log', default=LOGFILE_NAME, help='Log file name')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args.log)

    merger = ProfileMerger(args.profile_a, args.profile_b)
    merger.merge_and_save()
