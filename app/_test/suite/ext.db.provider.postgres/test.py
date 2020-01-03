import gws.gis.extent
import gws.gis.proj
import gws.gis.shape
import gws.tools.json2

import _test.util as u
import _test.common.const as cc

_REPROJECTION_ERROR_TOLERANCE = 10


def test_find_points():
    x, y = cc.POINTS.paris
    bbox = x, y, x + 101, y + 101
    sh = gws.gis.shape.from_extent(bbox, 'EPSG:3857')

    r = u.cmd('searchFindFeatures', {
        'projectUid': 'a',
        'layerUids': ['a.map.paris_3857'],
        'resolution': 1,
        'shapes': [sh.props]
    })

    r = r.json()

    exp = [
        {
            "attributes": "id=<1> p_str=<paris_3857/1> p_int=<100> p_date=<2019-01-01>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.paris_3857___1"
        },
        {
            "attributes": "id=<2> p_str=<paris_3857/2> p_int=<200> p_date=<2019-01-02>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.paris_3857___2"
        },
        {
            "attributes": "id=<6> p_str=<paris_3857/6> p_int=<600> p_date=<2019-01-06>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.paris_3857___6"
        },
        {
            "attributes": "id=<7> p_str=<paris_3857/7> p_int=<700> p_date=<2019-01-07>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.paris_3857___7"
        }
    ]

    assert u.short_features(r['features']) == exp


def test_find_points_with_reprojection():
    x, y = cc.POINTS.dus
    x, y = gws.gis.proj.transform_xy(x, y, cc.CRS_3857, cc.CRS_25832)
    bbox = x, y, x + 101, y + 101
    bbox = gws.gis.extent.transformed(bbox, cc.CRS_25832, cc.CRS_3857)
    bbox = gws.gis.extent.buffer(bbox, _REPROJECTION_ERROR_TOLERANCE)

    sh = gws.gis.shape.from_extent(bbox, cc.CRS_3857)

    r = u.cmd('searchFindFeatures', {
        'projectUid': 'a',
        'layerUids': ['a.map.dus_25832'],
        'resolution': 1,
        'shapes': [sh.props]
    })

    r = r.json()

    exp = [
        {
            "attributes": "id=<1> p_str=<dus_25832/1> p_int=<100> p_date=<2019-01-01>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.dus_25832___1"
        },
        {
            "attributes": "id=<2> p_str=<dus_25832/2> p_int=<200> p_date=<2019-01-02>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.dus_25832___2"
        },
        {
            "attributes": "id=<6> p_str=<dus_25832/6> p_int=<600> p_date=<2019-01-06>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.dus_25832___6"
        },
        {
            "attributes": "id=<7> p_str=<dus_25832/7> p_int=<700> p_date=<2019-01-07>",
            "geometry": "POINT EPSG:3857",
            "uid": "a.map.dus_25832___7"
        }
    ]

    assert u.short_features(r['features']) == exp


def test_render_squares():
    x, y = cc.POINTS.ny
    bbox = x, y, x + 350, y + 350

    url = '_/cmd/mapHttpGetBbox/layerUid/a.map.ny_3857/bbox/' + gws.as_str_list(bbox)

    r = u.req(url, params={'width': 200, 'height': 200})
    d = u.compare_image_response(r, '/data/squares_200x200.png')
    assert not d

    r = u.req(url, params={'width': 400, 'height': 400})
    d = u.compare_image_response(r, '/data/squares_400x400.png')
    assert not d

    r = u.req(url, params={'width': 800, 'height': 400})
    d = u.compare_image_response(r, '/data/squares_800x400.png')
    assert not d


def test_render_squares_styled():
    x, y = cc.POINTS.ny
    bbox = x, y, x + 350, y + 350

    url = '_/cmd/mapHttpGetBbox/layerUid/a.map.ny_3857_styled/bbox/' + gws.as_str_list(bbox)

    r = u.req(url, params={'width': 200, 'height': 200})
    d = u.compare_image_response(r, '/data/squares_styled_200x200.png')
    assert not d


def test_render_squares_reprojected():
    x, y = cc.POINTS.london
    x, y = gws.gis.proj.transform_xy(x, y, cc.CRS_3857, cc.CRS_25833)
    bbox = x, y, x + 350, y + 350
    bbox = gws.gis.extent.transformed(bbox, cc.CRS_25833, cc.CRS_3857)

    url = '_/cmd/mapHttpGetBbox/layerUid/a.map.london_25833/bbox/' + gws.as_str_list(bbox)

    r = u.req(url, params={'width': 200, 'height': 200})
    d = u.compare_image_response(r, '/data/squares_reprojected_200x200.png')
    assert not d
