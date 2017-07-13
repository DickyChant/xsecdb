
const searchPageReducer = (state = [], action) => {
    console.log(action);
    switch (action.type) {
        case "GET_RECORDS_SUCCESS":
            const records = action.records.map(r => Object.assign({}, r, { id: r._id.$oid }));

            return Object.assign({}, state, { records: records });
        case "SEARCH_FIELD_CHANGE":
            return Object.assign({}, state, { searchField: action.value });
        case "RECORD_CELL_CHANGE":
            const index = getRecordIndexById(action.recordId);
            return Object.assign({}, state, {
                records: [
                    ...state.records.splice(0, index),
                    Object.assign({}, state.records[index], {
                        [action.propertyName]: action.value
                    })
                ]
            });
        default:
            return state;
    }
}

function getRecordIndexById(id, records) {
    return records.findIndex(r => r.id == id);
}

export default searchPageReducer;