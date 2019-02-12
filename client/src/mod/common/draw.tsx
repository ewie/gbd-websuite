import * as React from 'react';
import * as ol from 'openlayers';

import * as gws from 'gws';

import * as toolbox from '../common/toolbox';

let {Form, Row, Cell} = gws.ui.Layout;

const MASTER = 'Shared.Draw';

interface DrawProps extends gws.types.ViewProps {
    controller: DrawController;
    drawCurrentShape: string;
    drawEnabledShapes?: Array<string>;
    drawStyle?: gws.types.IMapStyle;
    drawMode: boolean;
}

const DrawPropsKeys = [
    'drawCurrentShape',
    'drawEnabledShapes',
    'drawStyle',
    'drawMode',

];

const DEFAULT_SHAPE_TYPE = 'Polygon';

const SHAPE_TYPES = [
    'Point',
    'Line',
    'Box',
    'Polygon',
    'Circle',
];

export class Tool extends gws.Tool {
    style: gws.types.IMapStyle;

    get toolboxView() {
        let master = this.app.controller(MASTER) as DrawController;
        let shapeType = this.getValue('drawCurrentShape') || DEFAULT_SHAPE_TYPE

        let button = (type, cls, tooltip) => {
            return <Cell>
                <gws.ui.IconButton
                    {...gws.tools.cls(cls, type === shapeType && 'isActive')}
                    tooltip={tooltip}
                    whenTouched={() => master.setShapeType(type)}
                />
            </Cell>
        };

        let buttons = [
            master.shapeTypeEnabled('Point') && button('Point', 'modDrawPointButton', master.__('modDrawPointButton')),
            master.shapeTypeEnabled('Line') && button('Line', 'modDrawLineButton', master.__('modDrawLineButton')),
            master.shapeTypeEnabled('Box') && button('Box', 'modDrawBoxButton', master.__('modDrawBoxButton')),
            master.shapeTypeEnabled('Polygon') && button('Polygon', 'modDrawPolygonButton', master.__('modDrawPolygonButton')),
            master.shapeTypeEnabled('Circle') && button('Circle', 'modDrawCircleButton', master.__('modDrawCircleButton')),
        ];

        buttons.push(<gws.ui.IconButton
                className="modToolboxCancelButton"
                tooltip={this.__('modDrawCancelButton')}
                whenTouched={() => master.cancel()}
            />
        );

        return <toolbox.Content
            controller={this}
            iconClass="modIdentifyClickToolboxIcon"
            title={this.__('modIdentifyClickToolboxTitle')}
            hint={this.__('modIdentifyClickToolboxHint')}
            buttons={buttons}
        />
    }

    start() {
        let master = this.app.controller(MASTER) as DrawController;
        master.start(this);
    }

    stop() {
        let master = this.app.controller(MASTER) as DrawController;
        master.stop();
    }

    enabledShapes() {
        return null;
    }

    whenStarted(shapeType, oFeature) {
    }

    whenEnded(shapeType, oFeature) {
    }

    whenCancelled() {
    }

}

class DrawBox extends gws.View<DrawProps> {

    render() {
        let master = this.props.controller.app.controller(MASTER) as DrawController;

        if (!this.props.drawMode)
            return <div className="modDrawControlBox"/>;

        let shapeType = this.props.drawCurrentShape || DEFAULT_SHAPE_TYPE

        let button = (type, cls, tooltip) => {
            return <Cell>
                <gws.ui.IconButton
                    {...gws.tools.cls(cls, type === shapeType && 'isActive')}
                    tooltip={tooltip}
                    whenTouched={() => master.setShapeType(type)}
                />
            </Cell>
        };

        return <div className="modDrawControlBox isActive">
            <Row>
                {master.shapeTypeEnabled('Point') && button('Point', 'modDrawPointButton', master.__('modDrawPointButton'))}
                {master.shapeTypeEnabled('Line') && button('Line', 'modDrawLineButton', master.__('modDrawLineButton'))}
                {master.shapeTypeEnabled('Box') && button('Box', 'modDrawBoxButton', master.__('modDrawBoxButton'))}
                {master.shapeTypeEnabled('Polygon') && button('Polygon', 'modDrawPolygonButton', master.__('modDrawPolygonButton'))}
                {master.shapeTypeEnabled('Circle') && button('Circle', 'modDrawCircleButton', master.__('modDrawCircleButton'))}
                <Cell flex/>
                <Cell>
                    <gws.ui.IconButton
                        className="cmpButtonFormOk"
                        tooltip={this.props.controller.__('modDrawOkButton')}
                        whenTouched={() => master.commit()}
                    />
                </Cell>
                <Cell>
                    <gws.ui.IconButton
                        className="cmpButtonFormCancel"
                        tooltip={this.props.controller.__('modDrawCancelButton')}
                        whenTouched={() => master.cancel()}
                    />
                </Cell>
            </Row>
        </div>;
    }
}

class DrawController extends gws.Controller {
    uid = MASTER;
    oInteraction: ol.interaction.Draw;
    oFeature: ol.Feature;
    state: string;
    currTool: Tool;

    get appOverlayView() {
        return this.createElement(
            this.connect(DrawBox, DrawPropsKeys));
    }

    get shapeType() {
        let st = this.getValue('drawCurrentShape') || DEFAULT_SHAPE_TYPE;
        if (this.shapeTypeEnabled(st))
            return st;
        let sts = SHAPE_TYPES.filter(t => this.shapeTypeEnabled(t));
        if (sts.length)
            return sts[0];
        console.warn('no shape type enabled!');
        return DEFAULT_SHAPE_TYPE;
    }

    shapeTypeEnabled(st) {
        if (!this.currTool)
            return false;
        let enabled = this.currTool.enabledShapes();
        if (!enabled)
            return true;
        return enabled.some(t => t.toLowerCase() === st.toLowerCase());
    }

    start(tool) {
        this.currTool = tool;
        this.startDrawing();
    }

    startDrawing() {

        let shapeType = this.shapeType;

        console.log('START_DRAW', this.shapeType)

        this.oFeature = null;
        this.state = 'started';

        this.oInteraction = this.map.drawInteraction({
            shapeType,
            style: this.currTool.style,
            whenStarted: (oFeatures) => {
                console.log('DRAW whenStarted', this.state);
                this.oFeature = oFeatures[0];
                this.state = 'drawing';
                this.currTool.whenStarted(this.shapeType, this.oFeature);
            },
            whenEnded: () => {
                console.log('DRAW whenEnded', this.state);
                if (this.state === 'drawing') {
                    this.state = 'ended';
                    this.stopDrawing();
                }
            },
        });

        this.map.setExtraInteractions([this.oInteraction]);

        this.update({
            drawMode: true,
            drawCurrentShape: shapeType
        });

    }

    stop() {
        this.stopDrawing();
        this.update({
            drawMode: false
        })

    }

    stopDrawing() {
        console.log('stopDrawing', this.state);

        let state = this.state;

        this.state = '';

        if (state === 'ended') {
            this.currTool.whenEnded(this.shapeType, this.oFeature);
        }
    }

    commit() {
        if (this.state === 'drawing') {
            this.oInteraction.finishDrawing();
        } else {
            this.stopDrawing();
        }
    }

    cancel() {
        this.stopDrawing();
        this.currTool.whenCancelled();

    }

    setShapeType(s) {
        this.update({
            drawCurrentShape: s
        });
        this.startDrawing();
    }

}

export const tags = {
    [MASTER]: DrawController,
};
