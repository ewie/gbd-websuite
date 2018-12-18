import * as React from 'react';
import * as ol from 'openlayers';

import * as gws from 'gws';
import * as sidebar from './sidebar';

let {Form, Row, Cell} = gws.ui.Layout;

interface ViewProps extends gws.types.ViewProps {
    controller: SidebarOverviewController;
    mapUpdateCount: number;
    mapEditScale: number;
    mapEditAngle: number;
    mapEditCenterX: number;
    mapEditCenterY: number;

}

// @TODO: should be configurable in the project
const COORDINATE_PRECISION = 0;

const POINTER_DEBOUNCE = 800;


class SidebarBody extends gws.View<ViewProps> {
    mapRef: React.RefObject<HTMLDivElement>;

    constructor(props) {
        super(props);
        this.mapRef = React.createRef();
    }

    componentDidMount() {
        if (this.mapRef.current)
            this.props.controller.setMapTarget(this.mapRef.current);
    }

    submit() {
        let map = this.props.controller.map;

        map.setViewState({
            center: [this.props.mapEditCenterX, this.props.mapEditCenterY],
            scale: this.props.mapEditScale,
            angle: this.props.mapEditAngle
        }, true)
    }

    mapInfoBlock() {
        let map = this.props.controller.map,
            vs = map.viewState,
            ve = map.viewExtent;

        let coord = n => map.formatCoordinate(Number(n) || 0);
        let num = n => String(Math.floor(Number(n) || 0));

        let data = [
            {
                name: 'projection',
                title: this.__('modOverviewProjection'),
                value: map.projection.getCode(),
            },
            {
                name: 'extent',
                title: this.__('modOverviewExtent'),
                value: <div>
                    {coord(ve[0])}, {coord(ve[1])}, {coord(ve[2])}, {coord(ve[3])}
                </div>
            },
            {
                name: 'mapEditCenterX',
                title: this.__('modOverviewCenterX'),
                value: coord(this.props.mapEditCenterX),
                editable: true,
            },
            {
                name: 'mapEditCenterY',
                title: this.__('modOverviewCenterY'),
                value: coord(this.props.mapEditCenterY),
                editable: true,
            },
            {
                name: 'mapEditScale',
                title: this.__('modOverviewScale'),
                value: num(this.props.mapEditScale),
                editable: true,
            },
            {
                name: 'mapEditAngle',
                title: this.__('modOverviewRotation'),
                value: num(this.props.mapEditAngle),
                editable: true,
            },

        ];

        return <Form>
            <Row>
                <Cell flex>
                    <gws.components.sheet.Editor
                        data={data}
                        whenChanged={(k, v) => this.props.controller.update({[k]: v})}
                        whenEntered={() => this.submit()}
                    />
                </Cell>
            </Row>
            <Row>
                <Cell flex/>
                <Cell>
                    <gws.ui.TextButton primary whenTouched={() => this.submit()}>
                        {this.__('modOverviewUpdateButton')}
                    </gws.ui.TextButton>
                </Cell>
            </Row>
        </Form>;
    }

    render() {
        let desc = this.props.controller.app.project.description;

        return <sidebar.Tab>

            <sidebar.TabHeader>
                <gws.ui.Title content={this.props.controller.app.project.title}/>
            </sidebar.TabHeader>

            <sidebar.TabBody>
                {this.props.controller.oMap && <div className="modOverviewMap" ref={this.mapRef}/>}
                {this.mapInfoBlock()}
            </sidebar.TabBody>

            {desc && <sidebar.TabFooter className="modOverviewTabFooter">
                <gws.ui.TextBlock className="cmpDescription" withHTML content={desc}/>
            </sidebar.TabFooter>}


        </sidebar.Tab>
    }
}

class SidebarOverviewController extends gws.Controller implements gws.types.ISidebarItem {
    oMap: ol.Map = null;
    oProjection: ol.proj.Projection;
    oOverlay: ol.Overlay;

    async init() {
        await super.init();
        if (this.app.overviewMap) {
            this.initMap();
        }

        this.app.whenChanged('mapUpdateCount', () => this.refresh());
        this.app.whenChanged('windowSize', () => this.refresh());
    }

    setMapTarget(div) {
        if (this.oMap) {
            this.oMap.setTarget(div);
            this.refresh();
        }
    }

    initMap() {
        let m = this.app.overviewMap.oMap;

        m.addInteraction(new ol.interaction.Pointer({
            handleDownEvent: e => this.handleMouseEvent(e),
            handleDragEvent: e => this.handleMouseEvent(e),

        }));

        let d = document.createElement('div');
        d.className = 'modOverviewBox';

        this.oOverlay = new ol.Overlay({
            element: d,
            stopEvent: false,
            positioning: 'center-center',
        });

        m.addOverlay(this.oOverlay);

        this.oMap = m;
        this.oProjection = m.getView().getProjection();
    }

    mouseTimer: any = 0;

    handleMouseEvent(evt: ol.MapBrowserPointerEvent) {
        clearTimeout(this.mouseTimer);
        this.oOverlay.setPosition(evt.coordinate);

        // prevent excessive map updates when dragging

        let cc = ol.proj.transform(
            evt.coordinate,
            this.oProjection,
            this.map.projection,
        );

        this.mouseTimer = setTimeout(
            () => this.map.setViewState({center: cc}),
            POINTER_DEBOUNCE);

        return true;
    }

    refresh() {
        let vs = this.map.viewState;

        this.update({
            'mapEditScale': vs.scale,
            'mapEditAngle': vs.angle,
            'mapEditCenterX': vs.centerX,
            'mapEditCenterY': vs.centerY,
        });

        if (this.oMap) {
            this.updateMap();
        }
    }

    updateMap() {
        clearTimeout(this.mouseTimer);

        let vs = this.map.viewState;

        let cc = ol.proj.transform(
            [vs.centerX, vs.centerY],
            this.map.projection,
            this.oProjection,
        );

        this.oOverlay.setPosition(cc);
        this.oMap.getView().setRotation(vs.rotation);

        let size = this.map.size;

        if (size) {
            let res = vs.resolution / this.oMap.getView().getResolution();

            let el = this.oOverlay.getElement() as HTMLDivElement;

            el.style.width = (size[0] * res) + 'px';
            el.style.height = (size[1] * res) + 'px';

            return;

        }
    }

    get iconClass() {
        return 'modOverviewSidebarIcon'
    }

    get tooltip() {
        return this.__('modOverviewTooltip');
    }

    get tabView() {
        return this.createElement(
            this.connect(SidebarBody, [
                'mapUpdateCount',
                'mapEditScale',
                'mapEditAngle',
                'mapEditCenterX',
                'mapEditCenterY',
            ]),
        );
    }

}

export const tags = {
    'Sidebar.Overview': SidebarOverviewController
};

