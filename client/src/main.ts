import * as ReactDOM from 'react-dom';

import * as gws from 'gws';

let mods = [
    require('./mod/common/draw'),
    require('./mod/common/modify'),
    require('./mod/common/lens'),
    require('./mod/common/misc'),
    require('./mod/common/toolbar'),
    require('./mod/common/sidebar'),
    require('./mod/common/task'),
    require('./mod/common/toolbox'),
    require('./mod/alkis'),
    require('./mod/annotate'),
    require('./mod/decoration'),
    require('./mod/dimension'),
    require('./mod/dprocon'),
    require('./mod/edit'),
    require('./mod/gekos'),
    require('./mod/identify'),
    require('./mod/infobar'),
    require('./mod/layers'),
    require('./mod/marker'),
    require('./mod/print'),
    require('./mod/select'),
    require('./mod/search'),
    require('./mod/overview'),
    require('./mod/user'),
    require('./mod/zoom'),
];

export async function main() {
    let domNode;
    let divs = document.getElementsByClassName('gws');

    if (divs.length > 0) {
        domNode = divs.item(0);
    } else {
        domNode = document.createElement('div');
        domNode.className = 'gws';
        document.body.appendChild(domNode);
    }

    if (navigator.userAgent.indexOf('Trident/7.0') > 0) {
        domNode.className = 'gws msie';
    }

    let options = {
        serverUrl: window['GWS_SERVER_URL'],
        projectUid: window['GWS_PROJECT_UID'],
        cssBreakpoints: require('./css/node_modules/breakpoints'),
        labels: require('./lang'),
        locale: window['GWS_LOCALE'],
        tags: mods.reduce((o, m) => Object.assign(o, m.tags), {}),
        defaultHelpUrl: '',
        defaultHomeUrl: '/',
        domNode
    };

    // NB assuming our script to be called gws-client-whatever.js

    let scripts = document.getElementsByTagName('script');
    if (scripts) {
        for (let i = 0; i < scripts.length; i++) {
            let m = (scripts[i].src || '').match(/^(.+?)gws-client[^\/]+$/);
            if (m)
                options.defaultHelpUrl = m[1] + 'help_' + options.locale + '.html';
        }
    }

    let app = await gws.Application.create(options);
    if (app) {
        window['DEBUG_APP'] = app;
        ReactDOM.render(app.rootController.defaultView, domNode);
    }
}
