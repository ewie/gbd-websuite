module.exports = v => ({

    '.uiSelect input.uiRawInput': {
        flex: 1,
        padding: [0, v.UNIT2, 0, v.UNIT2],
    },

    '.uiMenuItem': {
        cursor: 'default',
        height: v.CONTROL_SIZE,
        fontSize: v.CONTROL_FONT_SIZE,
        padding: [0, v.UNIT4, 0, v.UNIT4],
        whiteSpace: 'pre',
        display: 'flex',
        alignItems: 'center',

        ...v.TRANSITION('background-color'),

        '&:hover': {
            backgroundColor: v.HOVER_COLOR,
        },
    },

    '.uiMenuItemLevel1': {
        fontWeight: 800
    },

    '.uiMenuItemLevel2': {
        paddingLeft: v.UNIT8,
    },


});