const dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.colorByZone = (params) => {
    if (params.colDef.field !== "Zone Name") return "";

    const taskText = params.data?.["Zone Name"]?.toLowerCase();

    if (taskText?.endsWith('lf')) return 'lower-zone';
    if (taskText?.endsWith('mf')) return 'middle-zone';
    if (taskText?.endsWith('uf')) return 'upper-zone';
    if (taskText?.endsWith('of')) return 'only-zone';

    return "";
};