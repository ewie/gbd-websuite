import gws
import gws.common.ows.provider.parseutil as u
import gws.tools.xml3
import gws.types as t

from . import types


def parse(prov, xml):
    el = gws.tools.xml3.from_string(xml)

    prov.meta = t.MetaData(u.get_meta(
        u.one_of(el, 'Service', 'ServiceIdentification')))

    prov.meta.contact = t.MetaContact(u.get_meta_contact(
        u.one_of(el, 'Service.ContactInformation', 'ServiceProvider.ServiceContact')))

    if not prov.meta.url:
        prov.meta.url = u.get_url(el.first('ServiceMetadataURL'))

    prov.operations = u.get_operations(
        u.one_of(el, 'OperationsMetadata', 'Capability'))

    prov.version = el.attr('version')
    prov.source_layers = u.flatten_source_layers(_feature_type(e) for e in el.all('FeatureTypeList.FeatureType'))
    prov.supported_crs = u.crs_from_layers(prov.source_layers)


def _feature_type(el):
    oo = types.SourceLayer()

    n = el.get_text('Name')
    if ':' in n:
        oo.name = n
        oo.title = n.split(':')[1]
    else:
        oo.title = oo.name = n

    oo.meta = t.MetaData(u.get_meta(el))
    oo.extents = u.get_extents(el)

    oo.is_queryable = True

    cs = []
    e = u.one_of(el, 'DefaultSRS', 'DefaultCRS', 'SRS', 'CRS')
    if e:
        cs.append(e.text)

    cs.extend(e.text for e in el.all('OtherSRS'))
    cs.extend(e.text for e in el.all('OtherCRS'))

    oo.supported_crs = gws.compact(cs)

    return oo