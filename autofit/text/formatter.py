import configparser
import logging

from autoconf import conf

logger = logging.getLogger(__name__)


class TextFormatter:
    def __init__(self, line_length=90, indent=4):
        self.dict = dict()
        self.line_length = line_length
        self.indent = indent

    def add_to_dict(self, path_item_tuple: tuple, info_dict: dict):
        path_tuple = path_item_tuple[0]
        key = path_tuple[0]
        if len(path_tuple) == 1:
            info_dict[key] = path_item_tuple[1]
        else:
            if key not in info_dict:
                info_dict[key] = dict()
            self.add_to_dict(
                (path_item_tuple[0][1:], path_item_tuple[1]), info_dict[key]
            )

    def add(self, path_item_tuple: tuple):
        self.add_to_dict(path_item_tuple, self.dict)

    def dict_to_list(self, info_dict, line_length):
        lines = []
        for key, value in info_dict.items():
            indent_string = self.indent * " "
            if isinstance(value, dict):
                sub_lines = self.dict_to_list(
                    value, line_length=line_length - self.indent
                )
                lines.append(key)
                for line in sub_lines:
                    lines.append(f"{indent_string}{line}")
            else:
                value_string = str(value)
                space_string = max((line_length - len(key)), 1) * " "
                lines.append(f"{key}{space_string}{value_string}")
        return lines

    @property
    def list(self):
        return self.dict_to_list(self.dict, line_length=self.line_length)

    @property
    def text(self):
        return "\n".join(self.list)


def format_string_for_parameter_name(parameter_name: str) -> str:
    """
    Get the format for the label. Attempts to extract the key string associated with
    the dimension. Seems dodgy.

    Parameters
    ----------
    parameter_name
        A string label

    Returns
    -------
    format
        The format string (e.g {:.2f})
    """
    label_conf = conf.instance.label_format

    try:
        # noinspection PyProtectedMember
        for key, value in sorted(
            label_conf.parser._sections["format"].items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if key in parameter_name:
                return value
    except KeyError:
        pass
    raise configparser.NoSectionError(
        "Could not find an entry for the parameter {} in the label_format.iniconfig at path {}".format(
            parameter_name, label_conf.path
        )
    )


def convert_name_to_label(parameter_name, name_to_label):

    if not name_to_label:
        return parameter_name

    label_conf = conf.instance["notation"]["label"]

    try:
        return label_conf["label"][parameter_name]
    except KeyError:
        raise configparser.NoSectionError(
            "Could not find an entry for the parameter {} in the label_format.iniconfig at path {}".format(
                parameter_name, label_conf.path
            )
        )


def add_whitespace(str0, str1, whitespace):
    return f"{str0}{str1.rjust(whitespace - len(str0) + len(str1))}"


def value_with_limits_string(
    parameter_name, value, values_at_sigma, unit=None, format_string=None
):

    if unit is not None:
        unit = f" {unit}"
    else:
        unit = ""

    format_str = format_string or format_string_for_parameter_name(parameter_name)
    value = format_str.format(value)

    if values_at_sigma is None:
        return f"{value}{unit}"

    lower_value_at_sigma = format_str.format(values_at_sigma[0])
    upper_value_at_sigma = format_str.format(values_at_sigma[1])
    return f"{value} ({lower_value_at_sigma}, {upper_value_at_sigma}){unit}"


def parameter_result_string_from(
    parameter_name,
    value,
    whitespace,
    values_at_sigma=None,
    subscript=None,
    unit=None,
    format_string=None,
    name_to_label=False,
):
    value = value_with_limits_string(
        parameter_name=parameter_name,
        value=value,
        values_at_sigma=values_at_sigma,
        unit=unit,
        format_string=format_string,
    )

    str0 = convert_name_to_label(
        parameter_name=parameter_name, name_to_label=name_to_label
    )
    if subscript is None:
        return add_whitespace(str0=str0, str1=value, whitespace=whitespace)
    return add_whitespace(str0=f"{str0}_{subscript}", str1=value, whitespace=whitespace)


def output_list_of_strings_to_file(file, list_of_strings):
    file = open(file, "w")
    file.write("".join(list_of_strings))
    file.close()


def within_radius_label_value_and_unit_string(
    prefix, radius, unit_length, value, unit_value, whitespace
):
    label = prefix + "_within_{:.2f}_{}".format(radius, unit_length)
    return parameter_result_string_from(
        parameter_name=label, value=value, unit=unit_value, whitespace=whitespace
    )