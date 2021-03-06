"""
Templates to create a ``<Target_Identification />`` XML node for
product labels.
"""

from typing import Dict, List

from pdart.xml.Templates import NodeBuilder, interpret_template


def _munge(name: str) -> str:
    """Munge the string to act as part of a LID."""
    return name.replace(" ", "_").lower()


def target_identification(
    target_name: str, target_type: str, target_description: str, target_lid: str
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
            <lid_reference><NODE name="target_lid"/></lid_reference>
            <reference_type>data_to_target</reference_type>
        </Internal_Reference>
        </Target_Identification>"""
    )(
        {
            "name": target_name,
            "type": target_type,
            "description": target_description,
            "target_lid": target_lid,
        }
    )
    return func


def target_lid(target_parts: List[str]) -> str:
    target = ".".join(_munge(target_part) for target_part in target_parts)
    return f"urn:nasa:pds:context:target:{target}"


approximate_target_table: Dict[str, List[str]] = {
    "VENUS": ["Venus", "Planet"],
    "MARS": ["Mars", "Planet"],
    "JUP": ["Jupiter", "Planet"],
    "SAT": ["Saturn", "Planet"],
    "URA": ["Uranus", "Planet"],
    "NEP": ["Neptune", "Planet"],
    "CERES": ["Ceres", "Dwarf Planet"],
    "PLU": ["Pluto", "Dwarf Planet"],
    "PLCH": ["Pluto", "Dwarf Planet"],
    "IO": ["Io", "Satellite", "Jupiter"],
    "EUR": ["Europa", "Satellite", "Jupiter"],
    "GAN": ["Ganymede", "Satellite", "Jupiter"],
    "CALL": ["Callisto", "Satellite", "Jupiter"],
    "TITAN": ["Titan", "Satellite", "Saturn"],
    "TRIT": ["Triton", "Satellite", "Neptune"],
    "DIONE": ["Dione", "Satellite", "Saturn"],
    "IAPETUS": ["Iapetus", "Satellite", "Saturn"],
}
