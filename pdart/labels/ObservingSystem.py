"""Templates to create an ``<Observing_System />`` XML element."""
from pdart.xml.Templates import NodeBuilder, NodeBuilderTemplate, interpret_template

_observing_system: NodeBuilderTemplate = interpret_template(
    """<Observing_System>
      <name><NODE name="name"/></name>
      <Observing_System_Component>
        <name>Hubble Space Telescope</name>
        <type>Spacecraft</type>
        <Internal_Reference>
          <lid_reference>urn:nasa:pds:context:instrument_host:spacecraft.hst</lid_reference>
          <reference_type>is_instrument_host</reference_type>
        </Internal_Reference>
      </Observing_System_Component>
      <Observing_System_Component>
        <name><NODE name="component_name"/></name>
        <type>Instrument</type>
        <Internal_Reference>
          <lid_reference><NODE name="instrument_lid"/></lid_reference>
          <reference_type>is_instrument</reference_type>
        </Internal_Reference>
      </Observing_System_Component>
    </Observing_System>"""
)
"""
An interpreted fragment template to create an ``<Observing_System />``
XML element.
"""


acs_observing_system: NodeBuilder = _observing_system(
    {
        "name": "Hubble Space Telescope Advanced Camera for Surveys",
        "component_name": "Advanced Camera for Surveys",
        "instrument_lid": "urn:nasa:pds:context:instrument:insthost.acs",
        "instrument_host_lid": "urn:nasa:pds:context:instrument_host:spacecraft.hst",
    }
)
"""
An interpreted fragment template to create an ``<Observing_System />``
XML element.
"""

wfc3_observing_system: NodeBuilder = _observing_system(
    {
        "name": "Hubble Space Telescope Wide Field Camera 3",
        "component_name": "Wide Field Camera 3",
        "instrument_lid": "urn:nasa:pds:context:instrument:insthost.wfc3",
        "instrument_host_lid": "urn:nasa:pds:context:instrument_host:spacecraft.hst",
    }
)
"""
An interpreted fragment template to create an ``<Observing_System />``
XML element.
"""

wfpc2_observing_system: NodeBuilder = _observing_system(
    {
        "name": "Hubble Space Telescope Wide-Field Planetary Camera 2",
        "component_name": "Wide-Field Planetary Camera 2",
        "instrument_lid": "urn:nasa:pds:context:instrument:insthost.wfpc2",
        "instrument_host_lid": "urn:nasa:pds:context:instrument_host:spacecraft.hst",
    }
)
"""
An interpreted fragment template to create an ``<Observing_System />``
XML element.
"""


def observing_system_lid(instrument: str) -> str:
    return f"urn:nasa:pds:context:instrument:insthost.{instrument}"


def instrument_host_lid() -> str:
    return "urn:nasa:pds:context:instrument_host:spacecraft.hst"


def observing_system(instrument: str) -> NodeBuilder:
    """
    Given an instrument, return an interpreted fragment template to
    create an ``<Observing_System />`` XML element.
    """
    return {
        "acs": acs_observing_system,
        "wfc3": wfc3_observing_system,
        "wfpc2": wfpc2_observing_system,
    }[instrument]
