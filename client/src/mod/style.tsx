import * as React from 'react';

import * as gws from 'gws';
import * as sidebar from './common/sidebar';
import * as storage from './common/storage';

let {Form, Row, Cell} = gws.ui.Layout;

const MASTER = 'Shared.Style';

let _master = (cc: gws.types.IController) => cc.app.controller(MASTER) as StyleController;


interface ViewProps extends gws.types.ViewProps {
    controller: StyleController;
    styleEditorLabelEnabled: boolean;
    styleEditorCurrentName: string;
    styleEditorNewName: string;
    styleEditorValues: gws.api.StyleValues;
}


const StoreKeys = [
    'styleEditorLabelEnabled',
    'styleEditorCurrentName',
    'styleEditorNewName',
    'styleEditorValues',
];


const STORAGE_CATEGORY = 'styles';


class StyleForm extends gws.View<ViewProps> {
    render() {

        let cc = _master(this.props.controller);
        let sv = this.props.styleEditorValues;

        /*
                    <gws.ui.Group label={cc.__('modStyleName')} className="modStyleRenameControl">
                <gws.ui.TextInput
                    {...cc.bind('styleEditorNewName')}/>
                <gws.ui.Button
                    tooltip={cc.__('modStyleRename')}
                    whenTouched={() => cc.renameStyle()}
                />
            </gws.ui.Group>

         */

        let labelPlacement = ['start', 'middle', 'end'].map(opt => <gws.ui.Toggle
            key={opt}
            className={'modStyleProp_label_placement_' + opt}
            tooltip={cc.__('modStyleProp_label_placement_' + opt)}
            {...cc.bind(
                'styleEditorValues.label_placement',
                val => val === opt,
                val => opt
            )}/>,
        );

        let labelAlign = ['left', 'center', 'right'].map(opt => <gws.ui.Toggle
            key={opt}
            className={'modStyleProp_label_align_' + opt}
            tooltip={cc.__('modStyleProp_label_align_' + opt)}
            {...cc.bind(
                'styleEditorValues.label_align',
                val => val === opt,
                val => opt
            )}/>,
        );

        let noLabel = this.props.styleEditorValues.with_label !== gws.api.StyleLabelOption.all;
        let noGeom = this.props.styleEditorValues.with_geometry !== gws.api.StyleGeometryOption.all;

        return <Form tabular>
            <gws.ui.Group label={cc.__('modStyleProp_with_geometry')}>
                <gws.ui.Toggle
                    type="checkbox"
                    {...cc.bind(
                        'styleEditorValues.with_geometry',
                        val => val === 'all',
                        val => val ? 'all' : 'none',
                    )}/>
            </gws.ui.Group>

            <gws.ui.ColorPicker
                disabled={noGeom}
                label={cc.__('modStyleProp_fill')}
                {...cc.bind('styleEditorValues.fill')}/>
            <gws.ui.ColorPicker
                disabled={noGeom}
                label={cc.__('modStyleProp_stroke')}
                {...cc.bind('styleEditorValues.stroke')}/>
            <gws.ui.Slider
                disabled={noGeom}
                label={cc.__('modStyleProp_stroke_width')}
                minValue={0} maxValue={20} step={1}
                {...cc.bind('styleEditorValues.stroke_width')}/>
            <gws.ui.Slider
                disabled={noGeom}
                minValue={0} maxValue={20} step={1}
                label={cc.__('modStyleProp_point_size')}
                {...cc.bind('styleEditorValues.point_size')}/>

            <gws.ui.Group label={cc.__('modStyleProp_with_label')}>
                <gws.ui.Toggle
                    type="checkbox"
                    {...cc.bind(
                        'styleEditorValues.with_label',
                        val => val === 'all',
                        val => val ? 'all' : 'none',
                    )}/>
            </gws.ui.Group>

            <gws.ui.ColorPicker
                disabled={noLabel}
                label={cc.__('modStyleProp_fill')}
                {...cc.bind('styleEditorValues.label_fill')}/>
            <gws.ui.ColorPicker
                disabled={noLabel}
                label={cc.__('modStyleProp_stroke')}
                {...cc.bind('styleEditorValues.label_stroke')}/>
            <gws.ui.Slider
                disabled={noLabel}
                label={cc.__('modStyleProp_stroke_width')}
                minValue={0} maxValue={20} step={1}
                {...cc.bind('styleEditorValues.label_stroke_width')}/>
            <gws.ui.Slider
                disabled={noLabel}
                minValue={10} maxValue={40} step={1}
                label={cc.__('modStyleProp_label_font_size')}
                {...cc.bind('styleEditorValues.label_font_size')}/>
            <gws.ui.Group
                disabled={noLabel}
                label={cc.__('modStyleProp_label_placement')}>{labelPlacement}</gws.ui.Group>
            <gws.ui.Group
                disabled={noLabel}
                label={cc.__('modStyleProp_label_align')}>{labelAlign}</gws.ui.Group>
            <gws.ui.Group disabled={noLabel} label={cc.__('modStyleProp_label_offset')}>
                <gws.ui.Slider
                    minValue={-100} maxValue={+100} step={1}
                    {...cc.bind('styleEditorValues.label_offset_x')}/>
                <gws.ui.Slider
                    minValue={-100} maxValue={+100} step={1}
                    {...cc.bind('styleEditorValues.label_offset_y')}/>
            </gws.ui.Group>
        </Form>
    }
}

class StyleSidebarView extends gws.View<ViewProps> {
    render() {
        let styleNames = this.app.style.names.map(name => ({
            text: name,
            value: name,
        }));

        let cc = _master(this.props.controller);

        return <sidebar.Tab className="modStyleSidebar">
            <sidebar.TabHeader>
                <Row>
                    <Cell flex>
                        <gws.ui.Title content={this.__('modStyleSidebarTitle')}/>
                    </Cell>
                    <Cell>
                        <gws.ui.Select items={styleNames} {...cc.bind('styleEditorCurrentName')}/>
                    </Cell>
                </Row>
            </sidebar.TabHeader>
            <sidebar.TabBody>
                <StyleForm {...this.props}/>
            </sidebar.TabBody>

            <sidebar.TabFooter>
                <sidebar.AuxToolbar>
                    <Cell flex/>
                    <storage.ReadAuxButton
                        controller={cc}
                        category={STORAGE_CATEGORY}
                        whenDone={data => cc.readStyles(data)}
                    />
                    {<storage.WriteAuxButton
                        controller={this.props.controller}
                        category={STORAGE_CATEGORY}
                        data={cc.writeStyles()}
                    />}
                </sidebar.AuxToolbar>
            </sidebar.TabFooter>

        </sidebar.Tab>

    }
}

class StyleSidebar extends gws.Controller implements gws.types.ISidebarItem {

    iconClass = 'modStyleSidebarIcon';

    get tooltip() {
        return this.__('modStyleSidebarTitle');
    }

    get tabView() {
        return this.createElement(
            this.connect(StyleSidebarView, StoreKeys)
        );
    }
}

const UPDATE_DELAY = 500;


export class StyleController extends gws.Controller {
    uid = MASTER;

    updateTimer: any;


    async init() {
        this.update({
            styleEditorValues: {}
        });
        this.whenChanged('styleEditorCurrentName', () => this.loadStyle());
        this.whenChanged('styleEditorValues', () => this.updateValues());

        let s = this.app.style.get('.modAnnotateFeature');
        this.update({
            styleEditorNewName: s.name,
            styleEditorValues: s.values,
        });
    }


    styleForm() {
        return this.createElement(
            this.connect(StyleForm, StoreKeys)
        );
    }


    loadStyle() {
        let name = this.getValue('styleEditorCurrentName');
        console.log('LOAD STYLE', name)
        let s = this.app.style.get(name);
        this.update({
            styleEditorNewName: s.name,
            styleEditorValues: s.values,
        });
    }

    updateValues() {
        let name = this.getValue('styleEditorCurrentName');
        let style = this.app.style.at(name);
        if (style) {
            style.update(this.getValue('styleEditorValues'));
            clearTimeout(this.updateTimer);
            this.updateTimer = setTimeout(() => this.map.style.notifyChanged(this.map, name), UPDATE_DELAY);
        }
    }

    readStyles(data) {
        this.map.style.unserialize(data);
        this.map.style.notifyChanged(this.map);
        this.loadStyle();
    }

    writeStyles() {
        return this.map.style.serialize();
    }

    renameStyle() {


    }

}


export const tags = {

    [MASTER]: StyleController,
    'Sidebar.Style': StyleSidebar,
}