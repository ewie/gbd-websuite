module.exports = v => ({

    '.modLensFeature': {
        stroke: v.COLOR.blueGrey100,
        strokeWidth: 3,
        strokeDasharray: "5,5",
        mark: 'circle',
        markFill: v.COLOR.blueGrey300,
        markSize: 10,
        fill: v.COLOR.opacity(v.COLOR.blueGrey500, 0.3),
    },

    '.modLensFeatureEdit': {
        stroke: v.COLOR.blueGrey100,
        strokeWidth: 3,
        strokeDasharray: "5,5",
        mark: 'circle',
        markFill: v.COLOR.blueGrey300,
        markSize: 15,
        markStroke: v.COLOR.cyan100,
        markStrokeWidth: 5,
        fill: v.COLOR.opacity(v.COLOR.blueGrey50, 0.3),
    },

    '.modLensOverlay': {
        backgroundColor: v.COLOR.blueGrey800,
        borderRadius: v.UNIT8,

        'div': {
            ...v.ICON('small'),
            display: 'inline-block',
        }
    },

    '.modLensOverlayAnchorButton': {
        ...v.LOCAL_SVG('move', v.COLOR.white),
    },

    '.modLensOverlayDrawButton': {
        ...v.GOOGLE_SVG('content/create', v.COLOR.white),
    },

    '.modLensOverlayCancelButton': {
        ...v.GOOGLE_SVG('content/clear', v.COLOR.white),
    },


    '.modLensButton': {
        ...v.LOCAL_SVG('search_lens', v.TOOLBAR_BUTTON_COLOR)
    }

});
