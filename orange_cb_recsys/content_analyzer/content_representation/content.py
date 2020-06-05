from typing import List, Dict
import pickle
import re

from orange_cb_recsys.content_analyzer.content_representation.content_field import ContentField


class Content:
    """
    Class that represents a content. A content can be an item, a user or a rating
    A content is identified by a string id and is composed of different fields
    Args:
        content_id (str): identifier
        field_dict (list[ContentField]): list of the fields instances of a content
    """
    def __init__(self, content_id: str,
                 field_dict: Dict[str, ContentField] = None):
        if field_dict is None:
            field_dict = {}       # list o dict
        self.__index_document_id: int = None
        self.__content_id: str = content_id
        self.__field_dict: Dict[str, ContentField] = field_dict

    def set_index_document_id(self, index_document_id: int):
        self.__index_document_id = index_document_id

    def get_field_list(self):
        return self.__field_dict

    def get_field(self, field_name: str):
        return self.__field_dict[field_name]

    def get_index_document_id(self):
        return self.__index_document_id

    def append(self, field_name: str, field: ContentField):
        self.__field_dict[field_name] = field

    def remove(self, field_name: str):
        """
        Remove the field named field_name from the field list
        Args:
            field_name (str): the name of the field to remove
        """

        self.__field_dict.pop(field_name)

    def serialize(self, output_directory: str):
        """
        Serialize a content instance
        """
        file_name = re.sub(r'[^\w\s]','', self.__content_id)
        with open(output_directory + '/' + file_name + '.bin', 'wb') as file:
            pickle.dump(self, file)

    def __str__(self):
        content_string = "Content:" + self.__content_id
        field_string = ""
        for field in self.__field_dict.values():
            field_string += str(field) + "\n"

        return content_string + '\n\n' + field_string + "##############################"

    def get_content_id(self):
        return self.__content_id

    def __eq__(self, other):
        return self.__content_id == other.__content_id and self.__field_dict == other.__field_dict


class RepresentedContentsRecap:
    """
    Class that collects the Contents instance created,
    the whole collection can be serialized.
    Args:

    """
    def __init__(self, representation_list: str = None):
        if representation_list is None:
            representation_list = []

        self.__representation_list = representation_list

    def append(self, representation: str):
        self.__representation_list.append(representation)

    def serialize(self):
        """
        Serialize the entire collection
        Returns:
        """

        raise NotImplementedError

    def __str__(self):
        return '\n\n'.join(self.__representation_list)
