import * as React from 'react';

import * as gws from 'gws';

let {Row, Cell} = gws.ui.Layout;

interface ToolboxProps extends gws.types.ViewProps {
    appActiveTool: string;
}

const ToolboxStoreKeys = [
    'appActiveTool',
];

interface ToolboxViewProps extends gws.types.ViewProps {
    iconClass: string;
    title: string;
    hint: string;
    buttons?: Array<React.ReactElement<any>>;
}


export class Content extends gws.View<ToolboxViewProps> {
    render() {
        return <div className="modToolboxContent">
            <Row className="modToolboxContentHeader">
                <Cell>
                    <gws.ui.IconButton
                        className={this.props.iconClass}
                    />
                </Cell>
                <Cell>
                    <div className="modToolboxContentTitle">{this.props.title}</div>
                    <div className="modToolboxContentHint">{this.props.hint}</div>
                </Cell>
            </Row>

            <Row className="modToolboxContentFooter">
                <Cell flex/>
                {this.props.buttons}
                <Cell>
                    <gws.ui.IconButton
                        className="modToolboxCancelButton"
                        tooltip={this.props.controller.__('modDrawCancelButton')}
                        whenTouched={() => this.props.controller.app.stopTool('')}
                    />
                </Cell>
            </Row>
        </div>
    }
}




class ToolboxView extends gws.View<ToolboxProps> {
    render() {
        // let view = this.props.controller.app.tool('Tool.Identify.Click').toolboxView;
        //
        // return <div className="modToolbox isActive">{view}</div>;

        let view = this.props.controller.app.activeTool.toolboxView;

        if(!view)
            return <div className="modToolbox"/>;

        return <div className="modToolbox isActive">{view}</div>;



    }
}


class ToolboxController extends gws.Controller {
    uid: 'Toolbox';

    // get appOverlayView() {
    //     return this.createElement(
    //         this.connect(ToolboxView, ToolboxStoreKeys));
    // }

}

export const tags = {
    'Shared.Toolbox': ToolboxController,
};

