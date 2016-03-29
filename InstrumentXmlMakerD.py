import abc

import FileArchive
import XmlMaker


class InstrumentInfo(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def observing_system_name(self):
        pass

    @abc.abstractmethod
    def observing_system_component_name(self):
        pass

    @abc.abstractmethod
    def observing_system_component_lid(self):
        pass


class AcsInstrumentInfo(InstrumentInstrumentInfo):
    def __init__(self, document):
        super(AcsInstrumentInfo, self).__init__(document)

    def observing_system_name(self):
        return 'Hubble Space Telescope Advanced Camera for Surveys'

    def observing_system_component_name(self):
        return 'Advanced Camera for Surveys'

    def observing_system_component_lid(self):
        return 'urn:nasa:pds:context:instrument:insthost.acs.hst'


class Wfc3InstrumentInfo(InstrumentInstrumentInfo):
    def __init__(self, document):
        super(Wfc3InstrumentInfo, self).__init__(document)

    def observing_system_name(self):
        return 'Hubble Space Telescope Wide Field Camera 3'

    def observing_system_component_name(self):
        return 'Wide Field Camera 3'

    def observing_system_component_lid(self):
        return 'urn:nasa:pds:context:instrument:insthost.wfc3.hst'


class Wfpc2InstrumentInfo(InstrumentInstrumentInfo):
    def __init__(self, document):
        super(Wfpc2InstrumentInfo, self).__init__(document)

    def observing_system_name(self):
        return 'Hubble Space Telescope Wide-Field Planetary Camera 2'

    def observing_system_component_name(self):
        return 'Wide-Field Planetary Camera 2'

    def observing_system_component_lid(self):
        return 'urn:nasa:pds:context:instrument:insthost.wfpc2.hst'

_factories = {
    'acs': AcsInstrumentInfo,
    'wfc3': Wfc3InstrumentInfo,
    'wfpc2': Wfpc2InstrumentInfo
    }


class InstrumentXmlMakerD(XmlMaker.XmlMaker):
    """Version of InstrumentXmlMaker run on distillation"""
    def __init__(self, document, instrument):
        super(InstrumentXmlMakerD, self).__init__(document)
        assert FileArchive.is_valid_instrument(instrument), \
            'invalid instrument %s' % instrument
        self.instrument_info = _factories[instrument]

    def create_xml(self, parent):
        assert parent

        # At XPath 'Observing_System'
        observing_system = self.create_child(parent, 'Observing_System')
        name, observing_system_component_hst, \
            observing_system_component_inst = \
            self.create_children(observing_system,
                                 ['name',
                                  'Observing_System_Component',
                                  'Observing_System_Component'])
        self.set_text(name, self.instrument_info.observing_system_name())

        # At XPath
        # 'Observing_System/Observing_System_Component[0]'
        name, type, internal_reference = \
            self.create_children(observing_system_component_hst,
                                 ['name', 'type', 'Internal_Reference'])
        self.set_text(name, 'Hubble Space Telescope')
        self.set_text(type, 'Spacecraft')

        # At XPath
        # 'Observing_System/Observing_System_Component[0]/Internal_Reference'
        lid_reference, reference_type = \
            self.create_children(internal_reference,
                                 ['lid_reference', 'reference_type'])
        self.set_text(lid_reference,
                      'urn:nasa:pds:context:instrument_host:spacecraft.hst')
        self.set_text(reference_type, 'is_instrument_host')

        # At XPath
        # 'Observing_System/Observing_System_Component[1]'
        name, type, internal_reference = \
            self.create_children(observing_system_component_inst,
                                 ['name', 'type', 'Internal_Reference'])
        self.set_text(name,
                      self.instrument_info.observing_system_component_name())
        self.set_text(type, 'Instrument')

        # At XPath
        # 'Observing_System/Observing_System_Component[1]/Internal_Reference'
        lid_reference, reference_type = \
            self.create_children(internal_reference,
                                 ['lid_reference', 'reference_type'])
        self.set_text(lid_reference,
                      self.instrument_info.observing_system_component_lid())
        self.set_text(reference_type, 'is_instrument')
