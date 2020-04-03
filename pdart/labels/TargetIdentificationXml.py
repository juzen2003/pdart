"""
Templates to create a ``<Target_Identification />`` XML node for
product labels.
"""

from pdart.xml.Templates import interpret_template

from typing import Dict, Tuple
from pdart.xml.Templates import NodeBuilder


def target_identification(
    target_name: str, target_type: str, target_description: str
) -> NodeBuilder:
    """
    Given a target name and target type, return a function that takes
    a document and returns a filled-out ``<Target_Identification />``
    XML node, used in product labels.
    """
    func = interpret_template(
        """<Target_Identification>
        <name><NODE name="name"/></name>
        <type><NODE name="type"/></type>
        <description><NODE name="description"/></description>
        <Internal_Reference>
            <lid_reference>urn:nasa:pds:context:target:\
<NODE name="lower_name"/>.<NODE name="lower_type"/></lid_reference>
            <reference_type>data_to_target</reference_type>
        </Internal_Reference>
        </Target_Identification>"""
    )(
        {
            "name": target_name,
            "type": target_type,
            "description": target_description,
            "lower_name": target_name.lower(),
            "lower_type": target_type.lower(),
        }
    )
    return func


approximate_target_table: Dict[str, Tuple[str, str]] = {
    "JUP": ("Jupiter", "Planet"),
    "SAT": ("Saturn", "Planet"),
    "URA": ("Uranus", "Planet"),
    "NEP": ("Neptune", "Planet"),
    "PLU": ("Pluto", "Dwarf Planet"),
    "PLCH": ("Pluto", "Dwarf Planet"),
    "IO": ("Io", "Satellite"),
    "EUR": ("Europa", "Satellite"),
    "GAN": ("Ganymede", "Satellite"),
    "CALL": ("Callisto", "Satellite"),
    "TITAN": ("Titan", "Satellite"),
    "TRIT": ("Triton", "Satellite"),
    "DIONE": ("Dione", "Satellite"),
    "IAPETUS": ("Iapetus", "Satellite"),
}
