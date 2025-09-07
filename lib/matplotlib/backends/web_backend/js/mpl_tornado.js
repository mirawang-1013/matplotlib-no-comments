


function mpl_ondownload(figure, format) {
    window.open(figure.id + '/download.' + format, '_blank');
}
