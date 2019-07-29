# -*- coding: utf-8 -*-
""" SF Profile Merger.

Profile Merger Class

Copyright: Patricio Labin Correa - 2019

@F1r3f0x
"""

import re
from xml.etree import ElementTree
from xml.dom import minidom
from pprint import pprint

import models

PROFILE_A = 'A'
PROFILE_B = 'B'
PROFILE_MERGED = 'AB'


class Profile:
    def __init__(self, name, namespace=None, *args, **kwargs):
        self.name = ''
        self.file_path = ''
        self.is_merged = False
        self.namespace = None
        self.fields = {}

    def scan_file(self, file_path):
        if not file_path:
            return False

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

                _id = profile_field.model_id
                self.fields[_id] = profile_field
        return True

    def save_file(self, override_file_path=None):
        """Picks a path and saves the merged profile to it.
        """

        if override_file_path is not None:
            self.file_path = override_file_path

        if self.file_path:
            xml_root = ElementTree.Element(
                'Profile', attrib={'xmlns': 'http://soap.sforce.com/2006/04/metadata'}
            )

            # Goes through the merged profile and fills the xml
            for model_field in sorted(
                self.fields.values(), key=lambda x: x.model_name + x.model_id
            ):
                if not model_field.model_disabled:
                    if type(model_field) is not models.ProfileSingleValue:
                        c = ElementTree.SubElement(xml_root, model_field.model_name)
                        if model_field.fields:
                            for field, value in model_field.fields.items():
                                if value is not None and value != '':
                                    if type(value) is bool:
                                        value = str(value).lower()
                                    ElementTree.SubElement(c, field).text = value
                    else:
                        field = model_field.model_name
                        value = model_field.value
                        if value is not None and value != '':
                            if type(value) is bool:
                                value = str(value).lower()
                            c = ElementTree.SubElement(xml_root, model_field.model_name)
                            c.text = value

            # Get the xml as a String and then prettyfies it
            xml_str = ElementTree.tostring(xml_root, 'utf-8')
            reparsed = minidom.parseString(xml_str)
            xml_str = reparsed.toprettyxml(indent="    ", encoding='UTF-8').decode('utf-8').rstrip()

            # Write to the selected path
            with open(self.file_path, 'w', encoding='utf-8') as file_pointer:
                file_pointer.write(xml_str)

    def clear(self):
        self.is_merged = False
        self.namespace = None
        self.file_path = None
        self.fields.clear()


class ProfileMerger:
    def __init__(self, *args, **kwargs):
        self.profile_a = Profile(PROFILE_A)
        self.profile_b = Profile(PROFILE_B)
        self.profile_merged = Profile(PROFILE_MERGED)
        self.merge_a_to_b = False

    def merge_profiles(self, profile_a_path=None, profile_b_path=None) -> Profile:
        self.profile_a.scan_file(profile_a_path)
        self.profile_b.scan_file(profile_b_path)

        profiles = [self.profile_b, self.profile_a]
        if not self.merge_a_to_b:
            profiles = profiles[::-1]

        for profile in profiles:
            fields = profile.fields
            for _id, field in fields.items():
                self.profile_merged.fields[_id] = field
            profile.is_merged = True

        return self.profile_merged


if __name__ == '__main__':
    merger = ProfileMerger()
    merger.merge()
